"""IR node for the groupby"""
import ctypes
import operator
import types as pytypes
from collections import defaultdict, namedtuple
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, compiler, ir, ir_utils, types
from numba.core.analysis import compute_use_defs
from numba.core.ir_utils import build_definitions, compile_to_numba_ir, find_callname, find_const, find_topo_order, get_definition, get_ir_of_code, get_name_var_table, guard, is_getitem, mk_unique_var, next_label, remove_dels, replace_arg_nodes, replace_var_names, replace_vars_inner, visit_vars_inner
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic
from numba.parfors.parfor import Parfor, unwrap_parfor_blocks, wrap_parfor_blocks
import bodo
from bodo.hiframes.datetime_date_ext import DatetimeDateArrayType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, decref_table_array, delete_info_decref_array, delete_table, delete_table_decref_arrays, groupby_and_aggregate, info_from_table, info_to_array, py_data_to_cpp_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, pre_alloc_array_item_array
from bodo.libs.binary_arr_ext import BinaryArrayType, pre_alloc_binary_array
from bodo.libs.bool_arr_ext import BooleanArrayType
from bodo.libs.decimal_arr_ext import DecimalArrayType, alloc_decimal_array
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, _find_used_columns, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.transform import get_call_expr_arg
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, dtype_to_array_type, get_index_data_arr_types, get_literal_value, get_overload_const_func, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, is_overload_constant_dict, is_overload_constant_list, is_overload_constant_str, list_cumulative, to_str_arr_if_dict_array, type_has_unknown_cats, unwrap_typeref
from bodo.utils.utils import gen_getitem, incref, is_assign, is_call_assign, is_expr, is_null_pointer, is_var_assign
gb_agg_cfunc = {}
gb_agg_cfunc_addr = {}


@intrinsic
def add_agg_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        vkf__nib = func.signature
        if vkf__nib == types.none(types.voidptr):
            qnbe__pkqj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            qpqtk__cvt = cgutils.get_or_insert_function(builder.module,
                qnbe__pkqj, sym._literal_value)
            builder.call(qpqtk__cvt, [context.get_constant_null(vkf__nib.
                args[0])])
        elif vkf__nib == types.none(types.int64, types.voidptr, types.voidptr):
            qnbe__pkqj = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            qpqtk__cvt = cgutils.get_or_insert_function(builder.module,
                qnbe__pkqj, sym._literal_value)
            builder.call(qpqtk__cvt, [context.get_constant(types.int64, 0),
                context.get_constant_null(vkf__nib.args[1]), context.
                get_constant_null(vkf__nib.args[2])])
        else:
            qnbe__pkqj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            qpqtk__cvt = cgutils.get_or_insert_function(builder.module,
                qnbe__pkqj, sym._literal_value)
            builder.call(qpqtk__cvt, [context.get_constant_null(vkf__nib.
                args[0]), context.get_constant_null(vkf__nib.args[1]),
                context.get_constant_null(vkf__nib.args[2])])
        context.add_linking_libs([gb_agg_cfunc[sym._literal_value]._library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_agg_udf_addr(name):
    with numba.objmode(addr='int64'):
        addr = gb_agg_cfunc_addr[name]
    return addr


class AggUDFStruct(object):

    def __init__(self, regular_udf_funcs=None, general_udf_funcs=None):
        assert regular_udf_funcs is not None or general_udf_funcs is not None
        self.regular_udfs = False
        self.general_udfs = False
        self.regular_udf_cfuncs = None
        self.general_udf_cfunc = None
        if regular_udf_funcs is not None:
            (self.var_typs, self.init_func, self.update_all_func, self.
                combine_all_func, self.eval_all_func) = regular_udf_funcs
            self.regular_udfs = True
        if general_udf_funcs is not None:
            self.general_udf_funcs = general_udf_funcs
            self.general_udfs = True

    def set_regular_cfuncs(self, update_cb, combine_cb, eval_cb):
        assert self.regular_udfs and self.regular_udf_cfuncs is None
        self.regular_udf_cfuncs = [update_cb, combine_cb, eval_cb]

    def set_general_cfunc(self, general_udf_cb):
        assert self.general_udfs and self.general_udf_cfunc is None
        self.general_udf_cfunc = general_udf_cb


AggFuncStruct = namedtuple('AggFuncStruct', ['func', 'ftype'])
supported_agg_funcs = ['no_op', 'ngroup', 'head', 'transform', 'size',
    'shift', 'sum', 'count', 'nunique', 'median', 'cumsum', 'cumprod',
    'cummin', 'cummax', 'mean', 'min', 'max', 'prod', 'first', 'last',
    'idxmin', 'idxmax', 'var', 'std', 'udf', 'gen_udf']
supported_transform_funcs = ['no_op', 'sum', 'count', 'nunique', 'median',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'var', 'std']


def get_agg_func(func_ir, func_name, rhs, series_type=None, typemap=None):
    if func_name == 'no_op':
        raise BodoError('Unknown aggregation function used in groupby.')
    if series_type is None:
        series_type = SeriesType(types.float64)
    if func_name in {'var', 'std'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 3
        func.ncols_post_shuffle = 4
        return func
    if func_name in {'first', 'last'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        return func
    if func_name in {'idxmin', 'idxmax'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 2
        func.ncols_post_shuffle = 2
        return func
    if func_name in supported_agg_funcs[:-8]:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        xxc__lre = True
        znyg__etha = 1
        lugbf__lev = -1
        if isinstance(rhs, ir.Expr):
            for ekree__gid in rhs.kws:
                if func_name in list_cumulative:
                    if ekree__gid[0] == 'skipna':
                        xxc__lre = guard(find_const, func_ir, ekree__gid[1])
                        if not isinstance(xxc__lre, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if ekree__gid[0] == 'dropna':
                        xxc__lre = guard(find_const, func_ir, ekree__gid[1])
                        if not isinstance(xxc__lre, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            znyg__etha = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', znyg__etha)
            znyg__etha = guard(find_const, func_ir, znyg__etha)
        if func_name == 'head':
            lugbf__lev = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(lugbf__lev, int):
                lugbf__lev = guard(find_const, func_ir, lugbf__lev)
            if lugbf__lev < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = xxc__lre
        func.periods = znyg__etha
        func.head_n = lugbf__lev
        if func_name == 'transform':
            kws = dict(rhs.kws)
            spq__sqyd = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            cae__kdrrr = typemap[spq__sqyd.name]
            hklsu__owfk = None
            if isinstance(cae__kdrrr, str):
                hklsu__owfk = cae__kdrrr
            elif is_overload_constant_str(cae__kdrrr):
                hklsu__owfk = get_overload_const_str(cae__kdrrr)
            elif bodo.utils.typing.is_builtin_function(cae__kdrrr):
                hklsu__owfk = bodo.utils.typing.get_builtin_function_name(
                    cae__kdrrr)
            if hklsu__owfk not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {hklsu__owfk}'
                    )
            func.transform_func = supported_agg_funcs.index(hklsu__owfk)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    spq__sqyd = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if spq__sqyd == '':
        cae__kdrrr = types.none
    else:
        cae__kdrrr = typemap[spq__sqyd.name]
    if is_overload_constant_dict(cae__kdrrr):
        bnsi__ten = get_overload_constant_dict(cae__kdrrr)
        pqe__fyl = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in bnsi__ten.values()]
        return pqe__fyl
    if cae__kdrrr == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(cae__kdrrr, types.BaseTuple) or is_overload_constant_list(
        cae__kdrrr):
        pqe__fyl = []
        quks__xvq = 0
        if is_overload_constant_list(cae__kdrrr):
            yjync__bcpk = get_overload_const_list(cae__kdrrr)
        else:
            yjync__bcpk = cae__kdrrr.types
        for t in yjync__bcpk:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                pqe__fyl.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(yjync__bcpk) > 1:
                    func.fname = '<lambda_' + str(quks__xvq) + '>'
                    quks__xvq += 1
                pqe__fyl.append(func)
        return [pqe__fyl]
    if is_overload_constant_str(cae__kdrrr):
        func_name = get_overload_const_str(cae__kdrrr)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(cae__kdrrr):
        func_name = bodo.utils.typing.get_builtin_function_name(cae__kdrrr)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    assert typemap is not None, 'typemap is required for agg UDF handling'
    func = _get_const_agg_func(typemap[rhs.args[0].name], func_ir)
    func.ftype = 'udf'
    func.fname = _get_udf_name(func)
    return func


def get_agg_func_udf(func_ir, f_val, rhs, series_type, typemap):
    if isinstance(f_val, str):
        return get_agg_func(func_ir, f_val, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(f_val):
        func_name = bodo.utils.typing.get_builtin_function_name(f_val)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if isinstance(f_val, (tuple, list)):
        quks__xvq = 0
        xht__xjts = []
        for bgrmf__cvm in f_val:
            func = get_agg_func_udf(func_ir, bgrmf__cvm, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{quks__xvq}>'
                quks__xvq += 1
            xht__xjts.append(func)
        return xht__xjts
    else:
        assert is_expr(f_val, 'make_function') or isinstance(f_val, (numba.
            core.registry.CPUDispatcher, types.Dispatcher))
        assert typemap is not None, 'typemap is required for agg UDF handling'
        func = _get_const_agg_func(f_val, func_ir)
        func.ftype = 'udf'
        func.fname = _get_udf_name(func)
        return func


def _get_udf_name(func):
    code = func.code if hasattr(func, 'code') else func.__code__
    hklsu__owfk = code.co_name
    return hklsu__owfk


def _get_const_agg_func(func_typ, func_ir):
    agg_func = get_overload_const_func(func_typ, func_ir)
    if is_expr(agg_func, 'make_function'):

        def agg_func_wrapper(A):
            return A
        agg_func_wrapper.__code__ = agg_func.code
        agg_func = agg_func_wrapper
        return agg_func
    return agg_func


@infer_global(type)
class TypeDt64(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if len(args) == 1 and isinstance(args[0], (types.NPDatetime, types.
            NPTimedelta)):
            stzuq__vnku = types.DType(args[0])
            return signature(stzuq__vnku, *args)


class Aggregate(ir.Stmt):

    def __init__(self, df_out, df_in, key_names, gb_info_in, gb_info_out,
        out_vars, in_vars, in_key_inds, df_in_type, out_type,
        input_has_index, same_index, return_key, loc, func_name, dropna=True):
        self.df_out = df_out
        self.df_in = df_in
        self.key_names = key_names
        self.gb_info_in = gb_info_in
        self.gb_info_out = gb_info_out
        self.out_vars = out_vars
        self.in_vars = in_vars
        self.in_key_inds = in_key_inds
        self.df_in_type = df_in_type
        self.out_type = out_type
        self.input_has_index = input_has_index
        self.same_index = same_index
        self.return_key = return_key
        self.loc = loc
        self.func_name = func_name
        self.dropna = dropna
        self.dead_in_inds = set()
        self.dead_out_inds = set()

    def get_live_in_vars(self):
        return [jvau__sot for jvau__sot in self.in_vars if jvau__sot is not
            None]

    def get_live_out_vars(self):
        return [jvau__sot for jvau__sot in self.out_vars if jvau__sot is not
            None]

    @property
    def is_in_table_format(self):
        return self.df_in_type.is_table_format

    @property
    def n_in_table_arrays(self):
        return len(self.df_in_type.columns
            ) if self.df_in_type.is_table_format else 1

    @property
    def n_in_cols(self):
        return self.n_in_table_arrays + len(self.in_vars) - 1

    @property
    def in_col_types(self):
        return list(self.df_in_type.data) + list(get_index_data_arr_types(
            self.df_in_type.index))

    @property
    def is_output_table(self):
        return not isinstance(self.out_type, SeriesType)

    @property
    def n_out_table_arrays(self):
        return len(self.out_type.table_type.arr_types) if not isinstance(self
            .out_type, SeriesType) else 1

    @property
    def n_out_cols(self):
        return self.n_out_table_arrays + len(self.out_vars) - 1

    @property
    def out_col_types(self):
        opp__xamdh = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        rzxqn__scfcg = list(get_index_data_arr_types(self.out_type.index))
        return opp__xamdh + rzxqn__scfcg

    def update_dead_col_info(self):
        for iei__csgoe in self.dead_out_inds:
            self.gb_info_out.pop(iei__csgoe, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for haat__iwc, irxz__ahrg in self.gb_info_in.copy().items():
            lry__myh = []
            for bgrmf__cvm, xaz__efum in irxz__ahrg:
                if xaz__efum not in self.dead_out_inds:
                    lry__myh.append((bgrmf__cvm, xaz__efum))
            if not lry__myh:
                if haat__iwc is not None and haat__iwc not in self.in_key_inds:
                    self.dead_in_inds.add(haat__iwc)
                self.gb_info_in.pop(haat__iwc)
            else:
                self.gb_info_in[haat__iwc] = lry__myh
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for atl__wpdt in range(1, len(self.in_vars)):
                iei__csgoe = self.n_in_table_arrays + atl__wpdt - 1
                if iei__csgoe in self.dead_in_inds:
                    self.in_vars[atl__wpdt] = None
        else:
            for atl__wpdt in range(len(self.in_vars)):
                if atl__wpdt in self.dead_in_inds:
                    self.in_vars[atl__wpdt] = None

    def __repr__(self):
        nnfv__cgep = ', '.join(jvau__sot.name for jvau__sot in self.
            get_live_in_vars())
        rul__hzxot = f'{self.df_in}{{{nnfv__cgep}}}'
        fqgw__xpc = ', '.join(jvau__sot.name for jvau__sot in self.
            get_live_out_vars())
        aqx__isz = f'{self.df_out}{{{fqgw__xpc}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {rul__hzxot} {aqx__isz}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({jvau__sot.name for jvau__sot in aggregate_node.
        get_live_in_vars()})
    def_set.update({jvau__sot.name for jvau__sot in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    psvb__iowba = agg_node.out_vars[0]
    if psvb__iowba is not None and psvb__iowba.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            wpvgu__uiwom = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(wpvgu__uiwom)
        else:
            agg_node.dead_out_inds.add(0)
    for atl__wpdt in range(1, len(agg_node.out_vars)):
        jvau__sot = agg_node.out_vars[atl__wpdt]
        if jvau__sot is not None and jvau__sot.name not in lives:
            agg_node.out_vars[atl__wpdt] = None
            iei__csgoe = agg_node.n_out_table_arrays + atl__wpdt - 1
            agg_node.dead_out_inds.add(iei__csgoe)
    if all(jvau__sot is None for jvau__sot in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    mtq__fruse = {jvau__sot.name for jvau__sot in aggregate_node.
        get_live_out_vars()}
    return set(), mtq__fruse


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for atl__wpdt in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[atl__wpdt] is not None:
            aggregate_node.in_vars[atl__wpdt] = replace_vars_inner(
                aggregate_node.in_vars[atl__wpdt], var_dict)
    for atl__wpdt in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[atl__wpdt] is not None:
            aggregate_node.out_vars[atl__wpdt] = replace_vars_inner(
                aggregate_node.out_vars[atl__wpdt], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for atl__wpdt in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[atl__wpdt] is not None:
            aggregate_node.in_vars[atl__wpdt] = visit_vars_inner(aggregate_node
                .in_vars[atl__wpdt], callback, cbdata)
    for atl__wpdt in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[atl__wpdt] is not None:
            aggregate_node.out_vars[atl__wpdt] = visit_vars_inner(
                aggregate_node.out_vars[atl__wpdt], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    gwuv__gord = []
    for hvq__ess in aggregate_node.get_live_in_vars():
        yikqs__jnn = equiv_set.get_shape(hvq__ess)
        if yikqs__jnn is not None:
            gwuv__gord.append(yikqs__jnn[0])
    if len(gwuv__gord) > 1:
        equiv_set.insert_equiv(*gwuv__gord)
    wuwo__rru = []
    gwuv__gord = []
    for hvq__ess in aggregate_node.get_live_out_vars():
        pref__buby = typemap[hvq__ess.name]
        oiz__tyetq = array_analysis._gen_shape_call(equiv_set, hvq__ess,
            pref__buby.ndim, None, wuwo__rru)
        equiv_set.insert_equiv(hvq__ess, oiz__tyetq)
        gwuv__gord.append(oiz__tyetq[0])
        equiv_set.define(hvq__ess, set())
    if len(gwuv__gord) > 1:
        equiv_set.insert_equiv(*gwuv__gord)
    return [], wuwo__rru


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    fppz__bglar = aggregate_node.get_live_in_vars()
    zef__xwy = aggregate_node.get_live_out_vars()
    giv__uqfez = Distribution.OneD
    for hvq__ess in fppz__bglar:
        giv__uqfez = Distribution(min(giv__uqfez.value, array_dists[
            hvq__ess.name].value))
    pely__vsgks = Distribution(min(giv__uqfez.value, Distribution.OneD_Var.
        value))
    for hvq__ess in zef__xwy:
        if hvq__ess.name in array_dists:
            pely__vsgks = Distribution(min(pely__vsgks.value, array_dists[
                hvq__ess.name].value))
    if pely__vsgks != Distribution.OneD_Var:
        giv__uqfez = pely__vsgks
    for hvq__ess in fppz__bglar:
        array_dists[hvq__ess.name] = giv__uqfez
    for hvq__ess in zef__xwy:
        array_dists[hvq__ess.name] = pely__vsgks


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for hvq__ess in agg_node.get_live_out_vars():
        definitions[hvq__ess.name].append(agg_node)
    return definitions


ir_utils.build_defs_extensions[Aggregate] = build_agg_definitions


def __update_redvars():
    pass


@infer_global(__update_redvars)
class UpdateDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __combine_redvars():
    pass


@infer_global(__combine_redvars)
class CombineDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __eval_res():
    pass


@infer_global(__eval_res)
class EvalDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(args[0].dtype, *args)


def agg_distributed_run(agg_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    bzhv__rqu = agg_node.get_live_in_vars()
    yzypf__jyc = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for jvau__sot in (bzhv__rqu + yzypf__jyc):
            if array_dists[jvau__sot.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                jvau__sot.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    pqe__fyl = []
    func_out_types = []
    for xaz__efum, (haat__iwc, func) in agg_node.gb_info_out.items():
        if haat__iwc is not None:
            t = agg_node.in_col_types[haat__iwc]
            in_col_typs.append(t)
        pqe__fyl.append(func)
        func_out_types.append(out_col_typs[xaz__efum])
    pkolq__peifs = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for atl__wpdt, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            pkolq__peifs.update({f'in_cat_dtype_{atl__wpdt}': in_col_typ})
    for atl__wpdt, jszy__mly in enumerate(out_col_typs):
        if isinstance(jszy__mly, bodo.CategoricalArrayType):
            pkolq__peifs.update({f'out_cat_dtype_{atl__wpdt}': jszy__mly})
    udf_func_struct = get_udf_func_struct(pqe__fyl, in_col_typs, typingctx,
        targetctx)
    out_var_types = [(typemap[jvau__sot.name] if jvau__sot is not None else
        types.none) for jvau__sot in agg_node.out_vars]
    pxm__uujj, gwlyt__njumx = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    pkolq__peifs.update(gwlyt__njumx)
    pkolq__peifs.update({'pd': pd, 'pre_alloc_string_array':
        pre_alloc_string_array, 'pre_alloc_binary_array':
        pre_alloc_binary_array, 'pre_alloc_array_item_array':
        pre_alloc_array_item_array, 'string_array_type': string_array_type,
        'alloc_decimal_array': alloc_decimal_array, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'coerce_to_array': bodo.utils.conversion.coerce_to_array,
        'groupby_and_aggregate': groupby_and_aggregate, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array,
        'delete_info_decref_array': delete_info_decref_array,
        'delete_table': delete_table, 'add_agg_cfunc_sym':
        add_agg_cfunc_sym, 'get_agg_udf_addr': get_agg_udf_addr,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'decref_table_array': decref_table_array, 'decode_if_dict_array':
        decode_if_dict_array, 'set_table_data': bodo.hiframes.table.
        set_table_data, 'get_table_data': bodo.hiframes.table.
        get_table_data, 'out_typs': out_col_typs})
    if udf_func_struct is not None:
        if udf_func_struct.regular_udfs:
            pkolq__peifs.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            pkolq__peifs.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    cjpr__qwr = {}
    exec(pxm__uujj, {}, cjpr__qwr)
    mkbm__dmc = cjpr__qwr['agg_top']
    ovorh__pgnu = compile_to_numba_ir(mkbm__dmc, pkolq__peifs, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[jvau__sot.
        name] for jvau__sot in bzhv__rqu), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(ovorh__pgnu, bzhv__rqu)
    hwkn__qgv = ovorh__pgnu.body[-2].value.value
    zqd__sjhhc = ovorh__pgnu.body[:-2]
    for atl__wpdt, jvau__sot in enumerate(yzypf__jyc):
        gen_getitem(jvau__sot, hwkn__qgv, atl__wpdt, calltypes, zqd__sjhhc)
    return zqd__sjhhc


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        bttdk__cht = IntDtype(t.dtype).name
        assert bttdk__cht.endswith('Dtype()')
        bttdk__cht = bttdk__cht[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{bttdk__cht}'))"
            )
    elif isinstance(t, BooleanArrayType):
        return (
            'bodo.libs.bool_arr_ext.init_bool_array(np.empty(0, np.bool_), np.empty(0, np.uint8))'
            )
    elif isinstance(t, StringArrayType):
        return 'pre_alloc_string_array(1, 1)'
    elif t == bodo.dict_str_arr_type:
        return (
            'bodo.libs.dict_arr_ext.init_dict_arr(pre_alloc_string_array(1, 1), bodo.libs.int_arr_ext.alloc_int_array(1, np.int32), False)'
            )
    elif isinstance(t, BinaryArrayType):
        return 'pre_alloc_binary_array(1, 1)'
    elif t == ArrayItemArrayType(string_array_type):
        return 'pre_alloc_array_item_array(1, (1, 1), string_array_type)'
    elif isinstance(t, DecimalArrayType):
        return 'alloc_decimal_array(1, {}, {})'.format(t.precision, t.scale)
    elif isinstance(t, DatetimeDateArrayType):
        return (
            'bodo.hiframes.datetime_date_ext.init_datetime_date_array(np.empty(1, np.int64), np.empty(1, np.uint8))'
            )
    elif isinstance(t, bodo.CategoricalArrayType):
        if t.dtype.categories is None:
            raise BodoError(
                'Groupby agg operations on Categorical types require constant categories'
                )
        jlrug__ozpyy = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {jlrug__ozpyy}_cat_dtype_{colnum})'
            )
    else:
        return 'np.empty(1, {})'.format(_get_np_dtype(t.dtype))


def _get_np_dtype(t):
    if t == types.bool_:
        return 'np.bool_'
    if t == types.NPDatetime('ns'):
        return 'dt64_dtype'
    if t == types.NPTimedelta('ns'):
        return 'td64_dtype'
    return 'np.{}'.format(t)


def gen_update_cb(udf_func_struct, allfuncs, n_keys, data_in_typs_,
    do_combine, func_idx_to_in_col, label_suffix):
    wyg__vis = udf_func_struct.var_typs
    jjx__istr = len(wyg__vis)
    pxm__uujj = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    pxm__uujj += '    if is_null_pointer(in_table):\n'
    pxm__uujj += '        return\n'
    pxm__uujj += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in wyg__vis]), ',' if
        len(wyg__vis) == 1 else '')
    gquf__eeqp = n_keys
    odnz__cxah = []
    redvar_offsets = []
    owv__fiej = []
    if do_combine:
        for atl__wpdt, bgrmf__cvm in enumerate(allfuncs):
            if bgrmf__cvm.ftype != 'udf':
                gquf__eeqp += bgrmf__cvm.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(gquf__eeqp, gquf__eeqp +
                    bgrmf__cvm.n_redvars))
                gquf__eeqp += bgrmf__cvm.n_redvars
                owv__fiej.append(data_in_typs_[func_idx_to_in_col[atl__wpdt]])
                odnz__cxah.append(func_idx_to_in_col[atl__wpdt] + n_keys)
    else:
        for atl__wpdt, bgrmf__cvm in enumerate(allfuncs):
            if bgrmf__cvm.ftype != 'udf':
                gquf__eeqp += bgrmf__cvm.ncols_post_shuffle
            else:
                redvar_offsets += list(range(gquf__eeqp + 1, gquf__eeqp + 1 +
                    bgrmf__cvm.n_redvars))
                gquf__eeqp += bgrmf__cvm.n_redvars + 1
                owv__fiej.append(data_in_typs_[func_idx_to_in_col[atl__wpdt]])
                odnz__cxah.append(func_idx_to_in_col[atl__wpdt] + n_keys)
    assert len(redvar_offsets) == jjx__istr
    yzq__ajrmq = len(owv__fiej)
    wbupt__qbkk = []
    for atl__wpdt, t in enumerate(owv__fiej):
        wbupt__qbkk.append(_gen_dummy_alloc(t, atl__wpdt, True))
    pxm__uujj += '    data_in_dummy = ({}{})\n'.format(','.join(wbupt__qbkk
        ), ',' if len(owv__fiej) == 1 else '')
    pxm__uujj += """
    # initialize redvar cols
"""
    pxm__uujj += '    init_vals = __init_func()\n'
    for atl__wpdt in range(jjx__istr):
        pxm__uujj += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(atl__wpdt, redvar_offsets[atl__wpdt], atl__wpdt))
        pxm__uujj += '    incref(redvar_arr_{})\n'.format(atl__wpdt)
        pxm__uujj += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(atl__wpdt
            , atl__wpdt)
    pxm__uujj += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(atl__wpdt) for atl__wpdt in range(jjx__istr)]), ',' if 
        jjx__istr == 1 else '')
    pxm__uujj += '\n'
    for atl__wpdt in range(yzq__ajrmq):
        pxm__uujj += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(atl__wpdt, odnz__cxah[atl__wpdt], atl__wpdt))
        pxm__uujj += '    incref(data_in_{})\n'.format(atl__wpdt)
    pxm__uujj += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(atl__wpdt) for atl__wpdt in range(yzq__ajrmq)]), ',' if 
        yzq__ajrmq == 1 else '')
    pxm__uujj += '\n'
    pxm__uujj += '    for i in range(len(data_in_0)):\n'
    pxm__uujj += '        w_ind = row_to_group[i]\n'
    pxm__uujj += '        if w_ind != -1:\n'
    pxm__uujj += '            __update_redvars(redvars, data_in, w_ind, i)\n'
    cjpr__qwr = {}
    exec(pxm__uujj, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, cjpr__qwr)
    return cjpr__qwr['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    wyg__vis = udf_func_struct.var_typs
    jjx__istr = len(wyg__vis)
    pxm__uujj = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    pxm__uujj += '    if is_null_pointer(in_table):\n'
    pxm__uujj += '        return\n'
    pxm__uujj += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in wyg__vis]), ',' if
        len(wyg__vis) == 1 else '')
    zjjpa__sfmpe = n_keys
    sskbg__ilqwp = n_keys
    hkjp__qie = []
    kqtdk__ivpc = []
    for bgrmf__cvm in allfuncs:
        if bgrmf__cvm.ftype != 'udf':
            zjjpa__sfmpe += bgrmf__cvm.ncols_pre_shuffle
            sskbg__ilqwp += bgrmf__cvm.ncols_post_shuffle
        else:
            hkjp__qie += list(range(zjjpa__sfmpe, zjjpa__sfmpe + bgrmf__cvm
                .n_redvars))
            kqtdk__ivpc += list(range(sskbg__ilqwp + 1, sskbg__ilqwp + 1 +
                bgrmf__cvm.n_redvars))
            zjjpa__sfmpe += bgrmf__cvm.n_redvars
            sskbg__ilqwp += 1 + bgrmf__cvm.n_redvars
    assert len(hkjp__qie) == jjx__istr
    pxm__uujj += """
    # initialize redvar cols
"""
    pxm__uujj += '    init_vals = __init_func()\n'
    for atl__wpdt in range(jjx__istr):
        pxm__uujj += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(atl__wpdt, kqtdk__ivpc[atl__wpdt], atl__wpdt))
        pxm__uujj += '    incref(redvar_arr_{})\n'.format(atl__wpdt)
        pxm__uujj += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(atl__wpdt
            , atl__wpdt)
    pxm__uujj += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(atl__wpdt) for atl__wpdt in range(jjx__istr)]), ',' if 
        jjx__istr == 1 else '')
    pxm__uujj += '\n'
    for atl__wpdt in range(jjx__istr):
        pxm__uujj += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(atl__wpdt, hkjp__qie[atl__wpdt], atl__wpdt))
        pxm__uujj += '    incref(recv_redvar_arr_{})\n'.format(atl__wpdt)
    pxm__uujj += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(atl__wpdt) for atl__wpdt in range(
        jjx__istr)]), ',' if jjx__istr == 1 else '')
    pxm__uujj += '\n'
    if jjx__istr:
        pxm__uujj += '    for i in range(len(recv_redvar_arr_0)):\n'
        pxm__uujj += '        w_ind = row_to_group[i]\n'
        pxm__uujj += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    cjpr__qwr = {}
    exec(pxm__uujj, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, cjpr__qwr)
    return cjpr__qwr['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    wyg__vis = udf_func_struct.var_typs
    jjx__istr = len(wyg__vis)
    gquf__eeqp = n_keys
    redvar_offsets = []
    jvit__fmg = []
    kwkk__fmrzk = []
    for atl__wpdt, bgrmf__cvm in enumerate(allfuncs):
        if bgrmf__cvm.ftype != 'udf':
            gquf__eeqp += bgrmf__cvm.ncols_post_shuffle
        else:
            jvit__fmg.append(gquf__eeqp)
            redvar_offsets += list(range(gquf__eeqp + 1, gquf__eeqp + 1 +
                bgrmf__cvm.n_redvars))
            gquf__eeqp += 1 + bgrmf__cvm.n_redvars
            kwkk__fmrzk.append(out_data_typs_[atl__wpdt])
    assert len(redvar_offsets) == jjx__istr
    yzq__ajrmq = len(kwkk__fmrzk)
    pxm__uujj = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    pxm__uujj += '    if is_null_pointer(table):\n'
    pxm__uujj += '        return\n'
    pxm__uujj += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in wyg__vis]), ',' if
        len(wyg__vis) == 1 else '')
    pxm__uujj += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        kwkk__fmrzk]), ',' if len(kwkk__fmrzk) == 1 else '')
    for atl__wpdt in range(jjx__istr):
        pxm__uujj += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(atl__wpdt, redvar_offsets[atl__wpdt], atl__wpdt))
        pxm__uujj += '    incref(redvar_arr_{})\n'.format(atl__wpdt)
    pxm__uujj += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(atl__wpdt) for atl__wpdt in range(jjx__istr)]), ',' if 
        jjx__istr == 1 else '')
    pxm__uujj += '\n'
    for atl__wpdt in range(yzq__ajrmq):
        pxm__uujj += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(atl__wpdt, jvit__fmg[atl__wpdt], atl__wpdt))
        pxm__uujj += '    incref(data_out_{})\n'.format(atl__wpdt)
    pxm__uujj += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(atl__wpdt) for atl__wpdt in range(yzq__ajrmq)]), ',' if 
        yzq__ajrmq == 1 else '')
    pxm__uujj += '\n'
    pxm__uujj += '    for i in range(len(data_out_0)):\n'
    pxm__uujj += '        __eval_res(redvars, data_out, i)\n'
    cjpr__qwr = {}
    exec(pxm__uujj, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, cjpr__qwr)
    return cjpr__qwr['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    gquf__eeqp = n_keys
    xabgo__ris = []
    for atl__wpdt, bgrmf__cvm in enumerate(allfuncs):
        if bgrmf__cvm.ftype == 'gen_udf':
            xabgo__ris.append(gquf__eeqp)
            gquf__eeqp += 1
        elif bgrmf__cvm.ftype != 'udf':
            gquf__eeqp += bgrmf__cvm.ncols_post_shuffle
        else:
            gquf__eeqp += bgrmf__cvm.n_redvars + 1
    pxm__uujj = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    pxm__uujj += '    if num_groups == 0:\n'
    pxm__uujj += '        return\n'
    for atl__wpdt, func in enumerate(udf_func_struct.general_udf_funcs):
        pxm__uujj += '    # col {}\n'.format(atl__wpdt)
        pxm__uujj += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(xabgo__ris[atl__wpdt], atl__wpdt))
        pxm__uujj += '    incref(out_col)\n'
        pxm__uujj += '    for j in range(num_groups):\n'
        pxm__uujj += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(atl__wpdt, atl__wpdt))
        pxm__uujj += '        incref(in_col)\n'
        pxm__uujj += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(atl__wpdt))
    pkolq__peifs = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    ewkvj__gho = 0
    for atl__wpdt, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[ewkvj__gho]
        pkolq__peifs['func_{}'.format(ewkvj__gho)] = func
        pkolq__peifs['in_col_{}_typ'.format(ewkvj__gho)] = in_col_typs[
            func_idx_to_in_col[atl__wpdt]]
        pkolq__peifs['out_col_{}_typ'.format(ewkvj__gho)] = out_col_typs[
            atl__wpdt]
        ewkvj__gho += 1
    cjpr__qwr = {}
    exec(pxm__uujj, pkolq__peifs, cjpr__qwr)
    bgrmf__cvm = cjpr__qwr['bodo_gb_apply_general_udfs{}'.format(label_suffix)]
    zid__jfl = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(zid__jfl, nopython=True)(bgrmf__cvm)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    brxo__mzop = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        pyis__gec = []
        if agg_node.in_vars[0] is not None:
            pyis__gec.append('arg0')
        for atl__wpdt in range(agg_node.n_in_table_arrays, agg_node.n_in_cols):
            if atl__wpdt not in agg_node.dead_in_inds:
                pyis__gec.append(f'arg{atl__wpdt}')
    else:
        pyis__gec = [f'arg{atl__wpdt}' for atl__wpdt, jvau__sot in
            enumerate(agg_node.in_vars) if jvau__sot is not None]
    pxm__uujj = f"def agg_top({', '.join(pyis__gec)}):\n"
    hxtjm__bpktz = []
    if agg_node.is_in_table_format:
        hxtjm__bpktz = agg_node.in_key_inds + [haat__iwc for haat__iwc,
            bofzf__gqcsx in agg_node.gb_info_out.values() if haat__iwc is not
            None]
        if agg_node.input_has_index:
            hxtjm__bpktz.append(agg_node.n_in_cols - 1)
        oxd__lzk = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        xclx__cmguw = []
        for atl__wpdt in range(agg_node.n_in_table_arrays, agg_node.n_in_cols):
            if atl__wpdt in agg_node.dead_in_inds:
                xclx__cmguw.append('None')
            else:
                xclx__cmguw.append(f'arg{atl__wpdt}')
        sroyi__kiv = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        pxm__uujj += f"""    table = py_data_to_cpp_table({sroyi__kiv}, ({', '.join(xclx__cmguw)}{oxd__lzk}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        jfju__sctwn = [f'arg{atl__wpdt}' for atl__wpdt in agg_node.in_key_inds]
        kkch__ymjy = [f'arg{haat__iwc}' for haat__iwc, bofzf__gqcsx in
            agg_node.gb_info_out.values() if haat__iwc is not None]
        gzwsk__axyz = jfju__sctwn + kkch__ymjy
        if agg_node.input_has_index:
            gzwsk__axyz.append(f'arg{len(agg_node.in_vars) - 1}')
        pxm__uujj += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({twk__ewfos})' for twk__ewfos in gzwsk__axyz))
        pxm__uujj += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    cpgek__vmcp = []
    func_idx_to_in_col = []
    uir__pxiir = []
    xxc__lre = False
    jwihk__vrkq = 1
    lugbf__lev = -1
    foxmh__ddic = 0
    kfpv__ved = 0
    pqe__fyl = [func for bofzf__gqcsx, func in agg_node.gb_info_out.values()]
    for kcu__eko, func in enumerate(pqe__fyl):
        cpgek__vmcp.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            foxmh__ddic += 1
        if hasattr(func, 'skipdropna'):
            xxc__lre = func.skipdropna
        if func.ftype == 'shift':
            jwihk__vrkq = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            kfpv__ved = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            lugbf__lev = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(kcu__eko)
        if func.ftype == 'udf':
            uir__pxiir.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            uir__pxiir.append(0)
            do_combine = False
    cpgek__vmcp.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if foxmh__ddic > 0:
        if foxmh__ddic != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    pnt__bjbx = []
    if udf_func_struct is not None:
        hzguz__odbp = next_label()
        if udf_func_struct.regular_udfs:
            zid__jfl = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            urc__aqtki = numba.cfunc(zid__jfl, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs, do_combine,
                func_idx_to_in_col, hzguz__odbp))
            gcw__oph = numba.cfunc(zid__jfl, nopython=True)(gen_combine_cb(
                udf_func_struct, allfuncs, n_keys, hzguz__odbp))
            snt__jhec = numba.cfunc('void(voidptr)', nopython=True)(gen_eval_cb
                (udf_func_struct, allfuncs, n_keys, func_out_types,
                hzguz__odbp))
            udf_func_struct.set_regular_cfuncs(urc__aqtki, gcw__oph, snt__jhec)
            for ubwa__lftb in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[ubwa__lftb.native_name] = ubwa__lftb
                gb_agg_cfunc_addr[ubwa__lftb.native_name] = ubwa__lftb.address
        if udf_func_struct.general_udfs:
            rgfw__yqipw = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, func_out_types, func_idx_to_in_col,
                hzguz__odbp)
            udf_func_struct.set_general_cfunc(rgfw__yqipw)
        wyg__vis = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        fzy__dxlg = 0
        atl__wpdt = 0
        for ukh__anz, bgrmf__cvm in zip(agg_node.gb_info_out.keys(), allfuncs):
            if bgrmf__cvm.ftype in ('udf', 'gen_udf'):
                pnt__bjbx.append(out_col_typs[ukh__anz])
                for aam__yjbc in range(fzy__dxlg, fzy__dxlg + uir__pxiir[
                    atl__wpdt]):
                    pnt__bjbx.append(dtype_to_array_type(wyg__vis[aam__yjbc]))
                fzy__dxlg += uir__pxiir[atl__wpdt]
                atl__wpdt += 1
        pxm__uujj += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{atl__wpdt}' for atl__wpdt in range(len(pnt__bjbx)))}{',' if len(pnt__bjbx) == 1 else ''}))
"""
        pxm__uujj += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(pnt__bjbx)})
"""
        if udf_func_struct.regular_udfs:
            pxm__uujj += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{urc__aqtki.native_name}')\n"
                )
            pxm__uujj += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{gcw__oph.native_name}')\n"
                )
            pxm__uujj += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{snt__jhec.native_name}')\n"
                )
            pxm__uujj += (
                f"    cpp_cb_update_addr = get_agg_udf_addr('{urc__aqtki.native_name}')\n"
                )
            pxm__uujj += (
                f"    cpp_cb_combine_addr = get_agg_udf_addr('{gcw__oph.native_name}')\n"
                )
            pxm__uujj += (
                f"    cpp_cb_eval_addr = get_agg_udf_addr('{snt__jhec.native_name}')\n"
                )
        else:
            pxm__uujj += '    cpp_cb_update_addr = 0\n'
            pxm__uujj += '    cpp_cb_combine_addr = 0\n'
            pxm__uujj += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            ubwa__lftb = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[ubwa__lftb.native_name] = ubwa__lftb
            gb_agg_cfunc_addr[ubwa__lftb.native_name] = ubwa__lftb.address
            pxm__uujj += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{ubwa__lftb.native_name}')\n"
                )
            pxm__uujj += (
                f"    cpp_cb_general_addr = get_agg_udf_addr('{ubwa__lftb.native_name}')\n"
                )
        else:
            pxm__uujj += '    cpp_cb_general_addr = 0\n'
    else:
        pxm__uujj += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        pxm__uujj += '    cpp_cb_update_addr = 0\n'
        pxm__uujj += '    cpp_cb_combine_addr = 0\n'
        pxm__uujj += '    cpp_cb_eval_addr = 0\n'
        pxm__uujj += '    cpp_cb_general_addr = 0\n'
    pxm__uujj += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(bgrmf__cvm.ftype)) for
        bgrmf__cvm in allfuncs] + ['0']))
    pxm__uujj += (
        f'    func_offsets = np.array({str(cpgek__vmcp)}, dtype=np.int32)\n')
    if len(uir__pxiir) > 0:
        pxm__uujj += (
            f'    udf_ncols = np.array({str(uir__pxiir)}, dtype=np.int32)\n')
    else:
        pxm__uujj += '    udf_ncols = np.array([0], np.int32)\n'
    pxm__uujj += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    pxm__uujj += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {xxc__lre}, {jwihk__vrkq}, {kfpv__ved}, {lugbf__lev}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes)
"""
    gnmlr__qmue = []
    ugx__gwal = 0
    if agg_node.return_key:
        wvie__ybr = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for atl__wpdt in range(n_keys):
            iei__csgoe = wvie__ybr + atl__wpdt
            gnmlr__qmue.append(iei__csgoe if iei__csgoe not in agg_node.
                dead_out_inds else -1)
            ugx__gwal += 1
    for ukh__anz in agg_node.gb_info_out.keys():
        gnmlr__qmue.append(ukh__anz)
        ugx__gwal += 1
    qavm__qwyzz = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            gnmlr__qmue.append(agg_node.n_out_cols - 1)
        else:
            qavm__qwyzz = True
    oxd__lzk = ',' if brxo__mzop == 1 else ''
    jml__jpcxj = (
        f"({', '.join(f'out_type{atl__wpdt}' for atl__wpdt in range(brxo__mzop))}{oxd__lzk})"
        )
    epqts__kjcn = []
    aflyb__gzgg = []
    for atl__wpdt, t in enumerate(out_col_typs):
        if atl__wpdt not in agg_node.dead_out_inds and type_has_unknown_cats(t
            ):
            if atl__wpdt in agg_node.gb_info_out:
                haat__iwc = agg_node.gb_info_out[atl__wpdt][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                wudnb__piowg = atl__wpdt - wvie__ybr
                haat__iwc = agg_node.in_key_inds[wudnb__piowg]
            aflyb__gzgg.append(atl__wpdt)
            if (agg_node.is_in_table_format and haat__iwc < agg_node.
                n_in_table_arrays):
                epqts__kjcn.append(f'get_table_data(arg0, {haat__iwc})')
            else:
                epqts__kjcn.append(f'arg{haat__iwc}')
    oxd__lzk = ',' if len(epqts__kjcn) == 1 else ''
    pxm__uujj += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {jml__jpcxj}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(epqts__kjcn)}{oxd__lzk}), unknown_cat_out_inds)
"""
    pxm__uujj += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    pxm__uujj += '    delete_table_decref_arrays(table)\n'
    pxm__uujj += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for atl__wpdt in range(n_keys):
            if gnmlr__qmue[atl__wpdt] == -1:
                pxm__uujj += (
                    f'    decref_table_array(out_table, {atl__wpdt})\n')
    if qavm__qwyzz:
        cvlk__lsyj = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        pxm__uujj += f'    decref_table_array(out_table, {cvlk__lsyj})\n'
    pxm__uujj += '    delete_table(out_table)\n'
    pxm__uujj += '    ev_clean.finalize()\n'
    pxm__uujj += '    return out_data\n'
    pxwnd__aprp = {f'out_type{atl__wpdt}': out_var_types[atl__wpdt] for
        atl__wpdt in range(brxo__mzop)}
    pxwnd__aprp['out_col_inds'] = MetaType(tuple(gnmlr__qmue))
    pxwnd__aprp['in_col_inds'] = MetaType(tuple(hxtjm__bpktz))
    pxwnd__aprp['cpp_table_to_py_data'] = cpp_table_to_py_data
    pxwnd__aprp['py_data_to_cpp_table'] = py_data_to_cpp_table
    pxwnd__aprp.update({f'udf_type{atl__wpdt}': t for atl__wpdt, t in
        enumerate(pnt__bjbx)})
    pxwnd__aprp['udf_dummy_col_inds'] = MetaType(tuple(range(len(pnt__bjbx))))
    pxwnd__aprp['create_dummy_table'] = create_dummy_table
    pxwnd__aprp['unknown_cat_out_inds'] = MetaType(tuple(aflyb__gzgg))
    pxwnd__aprp['get_table_data'] = bodo.hiframes.table.get_table_data
    return pxm__uujj, pxwnd__aprp


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    yqdil__ddzv = tuple(unwrap_typeref(data_types.types[atl__wpdt]) for
        atl__wpdt in range(len(data_types.types)))
    arrs__nhcj = bodo.TableType(yqdil__ddzv)
    pxwnd__aprp = {'table_type': arrs__nhcj}
    pxm__uujj = 'def impl(data_types):\n'
    pxm__uujj += '  py_table = init_table(table_type, False)\n'
    pxm__uujj += '  py_table = set_table_len(py_table, 1)\n'
    for pref__buby, qbv__yqapn in arrs__nhcj.type_to_blk.items():
        pxwnd__aprp[f'typ_list_{qbv__yqapn}'] = types.List(pref__buby)
        pxwnd__aprp[f'typ_{qbv__yqapn}'] = pref__buby
        xrz__visps = len(arrs__nhcj.block_to_arr_ind[qbv__yqapn])
        pxm__uujj += f"""  arr_list_{qbv__yqapn} = alloc_list_like(typ_list_{qbv__yqapn}, {xrz__visps}, False)
"""
        pxm__uujj += f'  for i in range(len(arr_list_{qbv__yqapn})):\n'
        pxm__uujj += (
            f'    arr_list_{qbv__yqapn}[i] = alloc_type(1, typ_{qbv__yqapn}, (-1,))\n'
            )
        pxm__uujj += f"""  py_table = set_table_block(py_table, arr_list_{qbv__yqapn}, {qbv__yqapn})
"""
    pxm__uujj += '  return py_table\n'
    pxwnd__aprp.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    cjpr__qwr = {}
    exec(pxm__uujj, pxwnd__aprp, cjpr__qwr)
    return cjpr__qwr['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    wcf__vmia = agg_node.in_vars[0].name
    oxct__pkpc, sfwb__idg, jfjo__ome = block_use_map[wcf__vmia]
    if sfwb__idg or jfjo__ome:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        qoit__rjaot, mzo__prct, pwxa__ucwc = _compute_table_column_uses(
            agg_node.out_vars[0].name, table_col_use_map, equiv_vars)
        if mzo__prct or pwxa__ucwc:
            qoit__rjaot = set(range(agg_node.n_out_table_arrays))
    else:
        qoit__rjaot = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            qoit__rjaot = {0}
    cnws__gbs = set(atl__wpdt for atl__wpdt in agg_node.in_key_inds if 
        atl__wpdt < agg_node.n_in_table_arrays)
    ozvmp__irh = set(agg_node.gb_info_out[atl__wpdt][0] for atl__wpdt in
        qoit__rjaot if atl__wpdt in agg_node.gb_info_out and agg_node.
        gb_info_out[atl__wpdt][0] is not None)
    ozvmp__irh |= cnws__gbs | oxct__pkpc
    vvdsf__zem = len(set(range(agg_node.n_in_table_arrays)) - ozvmp__irh) == 0
    block_use_map[wcf__vmia] = ozvmp__irh, vvdsf__zem, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    sjfxh__dfxd = agg_node.n_out_table_arrays
    naf__jnxl = agg_node.out_vars[0].name
    ztmn__glhay = _find_used_columns(naf__jnxl, sjfxh__dfxd,
        column_live_map, equiv_vars)
    if ztmn__glhay is None:
        return False
    suv__iaijr = set(range(sjfxh__dfxd)) - ztmn__glhay
    cjhph__lwib = len(suv__iaijr - agg_node.dead_out_inds) != 0
    if cjhph__lwib:
        agg_node.dead_out_inds.update(suv__iaijr)
        agg_node.update_dead_col_info()
    return cjhph__lwib


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for wme__almb in block.body:
            if is_call_assign(wme__almb) and find_callname(f_ir, wme__almb.
                value) == ('len', 'builtins') and wme__almb.value.args[0
                ].name == f_ir.arg_names[0]:
                mdlq__iiwd = get_definition(f_ir, wme__almb.value.func)
                mdlq__iiwd.name = 'dummy_agg_count'
                mdlq__iiwd.value = dummy_agg_count
    iod__biuyx = get_name_var_table(f_ir.blocks)
    ihjo__pjjba = {}
    for name, bofzf__gqcsx in iod__biuyx.items():
        ihjo__pjjba[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, ihjo__pjjba)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    kby__xrew = numba.core.compiler.Flags()
    kby__xrew.nrt = True
    mdgrx__mewh = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, kby__xrew)
    mdgrx__mewh.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, kbz__aewj, calltypes, bofzf__gqcsx = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    fxlh__abm = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    rpiyw__vlb = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    dhsr__yldfw = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    kuvj__vov = dhsr__yldfw(typemap, calltypes)
    pm = rpiyw__vlb(typingctx, targetctx, None, f_ir, typemap, kbz__aewj,
        calltypes, kuvj__vov, {}, kby__xrew, None)
    ceto__pzq = numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline(
        pm)
    pm = rpiyw__vlb(typingctx, targetctx, None, f_ir, typemap, kbz__aewj,
        calltypes, kuvj__vov, {}, kby__xrew, ceto__pzq)
    gkw__dvrk = numba.core.typed_passes.InlineOverloads()
    gkw__dvrk.run_pass(pm)
    nxnxj__eco = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    nxnxj__eco.run()
    for block in f_ir.blocks.values():
        for wme__almb in block.body:
            if is_assign(wme__almb) and isinstance(wme__almb.value, (ir.Arg,
                ir.Var)) and isinstance(typemap[wme__almb.target.name],
                SeriesType):
                pref__buby = typemap.pop(wme__almb.target.name)
                typemap[wme__almb.target.name] = pref__buby.data
            if is_call_assign(wme__almb) and find_callname(f_ir, wme__almb.
                value) == ('get_series_data', 'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[wme__almb.target.name].remove(wme__almb.value
                    )
                wme__almb.value = wme__almb.value.args[0]
                f_ir._definitions[wme__almb.target.name].append(wme__almb.value
                    )
            if is_call_assign(wme__almb) and find_callname(f_ir, wme__almb.
                value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[wme__almb.target.name].remove(wme__almb.value
                    )
                wme__almb.value = ir.Const(False, wme__almb.loc)
                f_ir._definitions[wme__almb.target.name].append(wme__almb.value
                    )
            if is_call_assign(wme__almb) and find_callname(f_ir, wme__almb.
                value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[wme__almb.target.name].remove(wme__almb.value
                    )
                wme__almb.value = ir.Const(False, wme__almb.loc)
                f_ir._definitions[wme__almb.target.name].append(wme__almb.value
                    )
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    mnc__rsegr = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, fxlh__abm)
    mnc__rsegr.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    rdzz__dyr = numba.core.compiler.StateDict()
    rdzz__dyr.func_ir = f_ir
    rdzz__dyr.typemap = typemap
    rdzz__dyr.calltypes = calltypes
    rdzz__dyr.typingctx = typingctx
    rdzz__dyr.targetctx = targetctx
    rdzz__dyr.return_type = kbz__aewj
    numba.core.rewrites.rewrite_registry.apply('after-inference', rdzz__dyr)
    xil__mcivg = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        kbz__aewj, typingctx, targetctx, fxlh__abm, kby__xrew, {})
    xil__mcivg.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            zpszp__ziofb = ctypes.pythonapi.PyCell_Get
            zpszp__ziofb.restype = ctypes.py_object
            zpszp__ziofb.argtypes = ctypes.py_object,
            bnsi__ten = tuple(zpszp__ziofb(hkprg__tym) for hkprg__tym in
                closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            bnsi__ten = closure.items
        assert len(code.co_freevars) == len(bnsi__ten)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, bnsi__ten)


class RegularUDFGenerator:

    def __init__(self, in_col_types, typingctx, targetctx):
        self.in_col_types = in_col_types
        self.typingctx = typingctx
        self.targetctx = targetctx
        self.all_reduce_vars = []
        self.all_vartypes = []
        self.all_init_nodes = []
        self.all_eval_funcs = []
        self.all_update_funcs = []
        self.all_combine_funcs = []
        self.curr_offset = 0
        self.redvar_offsets = [0]

    def add_udf(self, in_col_typ, func):
        bcfx__qasq = SeriesType(in_col_typ.dtype, to_str_arr_if_dict_array(
            in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (bcfx__qasq,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        ktsjv__fetm, arr_var = _rm_arg_agg_block(block, pm.typemap)
        ycnj__asdtb = -1
        for atl__wpdt, wme__almb in enumerate(ktsjv__fetm):
            if isinstance(wme__almb, numba.parfors.parfor.Parfor):
                assert ycnj__asdtb == -1, 'only one parfor for aggregation function'
                ycnj__asdtb = atl__wpdt
        parfor = None
        if ycnj__asdtb != -1:
            parfor = ktsjv__fetm[ycnj__asdtb]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = ktsjv__fetm[:ycnj__asdtb] + parfor.init_block.body
        eval_nodes = ktsjv__fetm[ycnj__asdtb + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for wme__almb in init_nodes:
            if is_assign(wme__almb) and wme__almb.target.name in redvars:
                ind = redvars.index(wme__almb.target.name)
                reduce_vars[ind] = wme__almb.target
        var_types = [pm.typemap[jvau__sot] for jvau__sot in redvars]
        uszsh__otbu = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        csw__pwvd = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        mqzrw__ufv = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(mqzrw__ufv)
        self.all_update_funcs.append(csw__pwvd)
        self.all_combine_funcs.append(uszsh__otbu)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        jjbl__rwuct = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        zieeh__qgtay = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        emney__mhjeo = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        aewf__bln = gen_all_eval_func(self.all_eval_funcs, self.redvar_offsets)
        return (self.all_vartypes, jjbl__rwuct, zieeh__qgtay, emney__mhjeo,
            aewf__bln)


class GeneralUDFGenerator(object):

    def __init__(self):
        self.funcs = []

    def add_udf(self, func):
        self.funcs.append(bodo.jit(distributed=False)(func))
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        func.n_redvars = 0

    def gen_all_func(self):
        if len(self.funcs) > 0:
            return self.funcs
        else:
            return None


def get_udf_func_struct(agg_func, in_col_types, typingctx, targetctx):
    yljm__ocj = []
    for t, bgrmf__cvm in zip(in_col_types, agg_func):
        yljm__ocj.append((t, bgrmf__cvm))
    kmd__mhmy = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    xea__mfmb = GeneralUDFGenerator()
    for in_col_typ, func in yljm__ocj:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            kmd__mhmy.add_udf(in_col_typ, func)
        except:
            xea__mfmb.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = kmd__mhmy.gen_all_func()
    general_udf_funcs = xea__mfmb.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    ihnyf__hxd = compute_use_defs(parfor.loop_body)
    bxps__kvyra = set()
    for myfk__qjbac in ihnyf__hxd.usemap.values():
        bxps__kvyra |= myfk__qjbac
    txvq__owa = set()
    for myfk__qjbac in ihnyf__hxd.defmap.values():
        txvq__owa |= myfk__qjbac
    npei__ixy = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    npei__ixy.body = eval_nodes
    lny__uaf = compute_use_defs({(0): npei__ixy})
    bid__jqj = lny__uaf.usemap[0]
    rlf__njdq = set()
    cgiwx__hgn = []
    fkpwb__xrxx = []
    for wme__almb in reversed(init_nodes):
        gckzn__gpphg = {jvau__sot.name for jvau__sot in wme__almb.list_vars()}
        if is_assign(wme__almb):
            jvau__sot = wme__almb.target.name
            gckzn__gpphg.remove(jvau__sot)
            if (jvau__sot in bxps__kvyra and jvau__sot not in rlf__njdq and
                jvau__sot not in bid__jqj and jvau__sot not in txvq__owa):
                fkpwb__xrxx.append(wme__almb)
                bxps__kvyra |= gckzn__gpphg
                txvq__owa.add(jvau__sot)
                continue
        rlf__njdq |= gckzn__gpphg
        cgiwx__hgn.append(wme__almb)
    fkpwb__xrxx.reverse()
    cgiwx__hgn.reverse()
    fbo__kdckb = min(parfor.loop_body.keys())
    akl__syb = parfor.loop_body[fbo__kdckb]
    akl__syb.body = fkpwb__xrxx + akl__syb.body
    return cgiwx__hgn


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    ucv__tage = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    bdc__qrqv = set()
    mexo__euoy = []
    for wme__almb in init_nodes:
        if is_assign(wme__almb) and isinstance(wme__almb.value, ir.Global
            ) and isinstance(wme__almb.value.value, pytypes.FunctionType
            ) and wme__almb.value.value in ucv__tage:
            bdc__qrqv.add(wme__almb.target.name)
        elif is_call_assign(wme__almb
            ) and wme__almb.value.func.name in bdc__qrqv:
            pass
        else:
            mexo__euoy.append(wme__almb)
    init_nodes = mexo__euoy
    mxo__mfql = types.Tuple(var_types)
    rlzup__pzfah = lambda : None
    f_ir = compile_to_numba_ir(rlzup__pzfah, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    rdu__xjedl = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    yzby__hvrx = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        rdu__xjedl, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [yzby__hvrx] + block.body
    block.body[-2].value.value = rdu__xjedl
    piep__ikoix = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        mxo__mfql, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    usn__cpvt = numba.core.target_extension.dispatcher_registry[cpu_target](
        rlzup__pzfah)
    usn__cpvt.add_overload(piep__ikoix)
    return usn__cpvt


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    rvvbq__eztch = len(update_funcs)
    rtbre__czh = len(in_col_types)
    pxm__uujj = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for aam__yjbc in range(rvvbq__eztch):
        drthd__vhpgu = ', '.join(['redvar_arrs[{}][w_ind]'.format(atl__wpdt
            ) for atl__wpdt in range(redvar_offsets[aam__yjbc],
            redvar_offsets[aam__yjbc + 1])])
        if drthd__vhpgu:
            pxm__uujj += '  {} = update_vars_{}({},  data_in[{}][i])\n'.format(
                drthd__vhpgu, aam__yjbc, drthd__vhpgu, 0 if rtbre__czh == 1
                 else aam__yjbc)
    pxm__uujj += '  return\n'
    pkolq__peifs = {}
    for atl__wpdt, bgrmf__cvm in enumerate(update_funcs):
        pkolq__peifs['update_vars_{}'.format(atl__wpdt)] = bgrmf__cvm
    cjpr__qwr = {}
    exec(pxm__uujj, pkolq__peifs, cjpr__qwr)
    bsjmb__qruk = cjpr__qwr['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(bsjmb__qruk)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    kldfu__gwnif = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    arg_typs = kldfu__gwnif, kldfu__gwnif, types.intp, types.intp
    xxsju__bjpps = len(redvar_offsets) - 1
    pxm__uujj = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for aam__yjbc in range(xxsju__bjpps):
        drthd__vhpgu = ', '.join(['redvar_arrs[{}][w_ind]'.format(atl__wpdt
            ) for atl__wpdt in range(redvar_offsets[aam__yjbc],
            redvar_offsets[aam__yjbc + 1])])
        kfe__amjy = ', '.join(['recv_arrs[{}][i]'.format(atl__wpdt) for
            atl__wpdt in range(redvar_offsets[aam__yjbc], redvar_offsets[
            aam__yjbc + 1])])
        if kfe__amjy:
            pxm__uujj += '  {} = combine_vars_{}({}, {})\n'.format(drthd__vhpgu
                , aam__yjbc, drthd__vhpgu, kfe__amjy)
    pxm__uujj += '  return\n'
    pkolq__peifs = {}
    for atl__wpdt, bgrmf__cvm in enumerate(combine_funcs):
        pkolq__peifs['combine_vars_{}'.format(atl__wpdt)] = bgrmf__cvm
    cjpr__qwr = {}
    exec(pxm__uujj, pkolq__peifs, cjpr__qwr)
    qwawe__snz = cjpr__qwr['combine_all_f']
    f_ir = compile_to_numba_ir(qwawe__snz, pkolq__peifs)
    emney__mhjeo = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    usn__cpvt = numba.core.target_extension.dispatcher_registry[cpu_target](
        qwawe__snz)
    usn__cpvt.add_overload(emney__mhjeo)
    return usn__cpvt


def gen_all_eval_func(eval_funcs, redvar_offsets):
    xxsju__bjpps = len(redvar_offsets) - 1
    pxm__uujj = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for aam__yjbc in range(xxsju__bjpps):
        drthd__vhpgu = ', '.join(['redvar_arrs[{}][j]'.format(atl__wpdt) for
            atl__wpdt in range(redvar_offsets[aam__yjbc], redvar_offsets[
            aam__yjbc + 1])])
        pxm__uujj += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(aam__yjbc,
            aam__yjbc, drthd__vhpgu)
    pxm__uujj += '  return\n'
    pkolq__peifs = {}
    for atl__wpdt, bgrmf__cvm in enumerate(eval_funcs):
        pkolq__peifs['eval_vars_{}'.format(atl__wpdt)] = bgrmf__cvm
    cjpr__qwr = {}
    exec(pxm__uujj, pkolq__peifs, cjpr__qwr)
    zypy__zvkfr = cjpr__qwr['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(zypy__zvkfr)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    vsujl__bphk = len(var_types)
    zxmc__neave = [f'in{atl__wpdt}' for atl__wpdt in range(vsujl__bphk)]
    mxo__mfql = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    tsc__zjrvw = mxo__mfql(0)
    pxm__uujj = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        zxmc__neave))
    cjpr__qwr = {}
    exec(pxm__uujj, {'_zero': tsc__zjrvw}, cjpr__qwr)
    icnb__wqxht = cjpr__qwr['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(icnb__wqxht, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': tsc__zjrvw}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    iyut__omfa = []
    for atl__wpdt, jvau__sot in enumerate(reduce_vars):
        iyut__omfa.append(ir.Assign(block.body[atl__wpdt].target, jvau__sot,
            jvau__sot.loc))
        for zaai__hns in jvau__sot.versioned_names:
            iyut__omfa.append(ir.Assign(jvau__sot, ir.Var(jvau__sot.scope,
                zaai__hns, jvau__sot.loc), jvau__sot.loc))
    block.body = block.body[:vsujl__bphk] + iyut__omfa + eval_nodes
    mqzrw__ufv = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        mxo__mfql, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    usn__cpvt = numba.core.target_extension.dispatcher_registry[cpu_target](
        icnb__wqxht)
    usn__cpvt.add_overload(mqzrw__ufv)
    return usn__cpvt


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    vsujl__bphk = len(redvars)
    croy__oaba = [f'v{atl__wpdt}' for atl__wpdt in range(vsujl__bphk)]
    zxmc__neave = [f'in{atl__wpdt}' for atl__wpdt in range(vsujl__bphk)]
    pxm__uujj = 'def agg_combine({}):\n'.format(', '.join(croy__oaba +
        zxmc__neave))
    ruhkb__ngygt = wrap_parfor_blocks(parfor)
    sqif__nokw = find_topo_order(ruhkb__ngygt)
    sqif__nokw = sqif__nokw[1:]
    unwrap_parfor_blocks(parfor)
    qlevr__brvkv = {}
    usr__pnpjb = []
    for cty__pmz in sqif__nokw:
        polda__vqorr = parfor.loop_body[cty__pmz]
        for wme__almb in polda__vqorr.body:
            if is_assign(wme__almb) and wme__almb.target.name in redvars:
                kaq__jis = wme__almb.target.name
                ind = redvars.index(kaq__jis)
                if ind in usr__pnpjb:
                    continue
                if len(f_ir._definitions[kaq__jis]) == 2:
                    var_def = f_ir._definitions[kaq__jis][0]
                    pxm__uujj += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[kaq__jis][1]
                    pxm__uujj += _match_reduce_def(var_def, f_ir, ind)
    pxm__uujj += '    return {}'.format(', '.join(['v{}'.format(atl__wpdt) for
        atl__wpdt in range(vsujl__bphk)]))
    cjpr__qwr = {}
    exec(pxm__uujj, {}, cjpr__qwr)
    maq__bzn = cjpr__qwr['agg_combine']
    arg_typs = tuple(2 * var_types)
    pkolq__peifs = {'numba': numba, 'bodo': bodo, 'np': np}
    pkolq__peifs.update(qlevr__brvkv)
    f_ir = compile_to_numba_ir(maq__bzn, pkolq__peifs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    mxo__mfql = pm.typemap[block.body[-1].value.name]
    uszsh__otbu = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        mxo__mfql, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    usn__cpvt = numba.core.target_extension.dispatcher_registry[cpu_target](
        maq__bzn)
    usn__cpvt.add_overload(uszsh__otbu)
    return usn__cpvt


def _match_reduce_def(var_def, f_ir, ind):
    pxm__uujj = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        pxm__uujj = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        uaxg__iybxc = guard(find_callname, f_ir, var_def)
        if uaxg__iybxc == ('min', 'builtins'):
            pxm__uujj = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if uaxg__iybxc == ('max', 'builtins'):
            pxm__uujj = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return pxm__uujj


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    vsujl__bphk = len(redvars)
    vajbt__xsox = 1
    in_vars = []
    for atl__wpdt in range(vajbt__xsox):
        quyj__yux = ir.Var(arr_var.scope, f'$input{atl__wpdt}', arr_var.loc)
        in_vars.append(quyj__yux)
    uwis__buz = parfor.loop_nests[0].index_variable
    ieais__iwuih = [0] * vsujl__bphk
    for polda__vqorr in parfor.loop_body.values():
        gbo__tjq = []
        for wme__almb in polda__vqorr.body:
            if is_var_assign(wme__almb
                ) and wme__almb.value.name == uwis__buz.name:
                continue
            if is_getitem(wme__almb
                ) and wme__almb.value.value.name == arr_var.name:
                wme__almb.value = in_vars[0]
            if is_call_assign(wme__almb) and guard(find_callname, pm.
                func_ir, wme__almb.value) == ('isna', 'bodo.libs.array_kernels'
                ) and wme__almb.value.args[0].name == arr_var.name:
                wme__almb.value = ir.Const(False, wme__almb.target.loc)
            if is_assign(wme__almb) and wme__almb.target.name in redvars:
                ind = redvars.index(wme__almb.target.name)
                ieais__iwuih[ind] = wme__almb.target
            gbo__tjq.append(wme__almb)
        polda__vqorr.body = gbo__tjq
    croy__oaba = ['v{}'.format(atl__wpdt) for atl__wpdt in range(vsujl__bphk)]
    zxmc__neave = ['in{}'.format(atl__wpdt) for atl__wpdt in range(vajbt__xsox)
        ]
    pxm__uujj = 'def agg_update({}):\n'.format(', '.join(croy__oaba +
        zxmc__neave))
    pxm__uujj += '    __update_redvars()\n'
    pxm__uujj += '    return {}'.format(', '.join(['v{}'.format(atl__wpdt) for
        atl__wpdt in range(vsujl__bphk)]))
    cjpr__qwr = {}
    exec(pxm__uujj, {}, cjpr__qwr)
    crhih__ybr = cjpr__qwr['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * vajbt__xsox)
    f_ir = compile_to_numba_ir(crhih__ybr, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    dvet__pxuyo = f_ir.blocks.popitem()[1].body
    mxo__mfql = pm.typemap[dvet__pxuyo[-1].value.name]
    ruhkb__ngygt = wrap_parfor_blocks(parfor)
    sqif__nokw = find_topo_order(ruhkb__ngygt)
    sqif__nokw = sqif__nokw[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    akl__syb = f_ir.blocks[sqif__nokw[0]]
    rmre__zjyja = f_ir.blocks[sqif__nokw[-1]]
    ldz__zexv = dvet__pxuyo[:vsujl__bphk + vajbt__xsox]
    if vsujl__bphk > 1:
        zvujx__kbc = dvet__pxuyo[-3:]
        assert is_assign(zvujx__kbc[0]) and isinstance(zvujx__kbc[0].value,
            ir.Expr) and zvujx__kbc[0].value.op == 'build_tuple'
    else:
        zvujx__kbc = dvet__pxuyo[-2:]
    for atl__wpdt in range(vsujl__bphk):
        lamm__mbd = dvet__pxuyo[atl__wpdt].target
        mhn__bfm = ir.Assign(lamm__mbd, ieais__iwuih[atl__wpdt], lamm__mbd.loc)
        ldz__zexv.append(mhn__bfm)
    for atl__wpdt in range(vsujl__bphk, vsujl__bphk + vajbt__xsox):
        lamm__mbd = dvet__pxuyo[atl__wpdt].target
        mhn__bfm = ir.Assign(lamm__mbd, in_vars[atl__wpdt - vsujl__bphk],
            lamm__mbd.loc)
        ldz__zexv.append(mhn__bfm)
    akl__syb.body = ldz__zexv + akl__syb.body
    dno__mxpeu = []
    for atl__wpdt in range(vsujl__bphk):
        lamm__mbd = dvet__pxuyo[atl__wpdt].target
        mhn__bfm = ir.Assign(ieais__iwuih[atl__wpdt], lamm__mbd, lamm__mbd.loc)
        dno__mxpeu.append(mhn__bfm)
    rmre__zjyja.body += dno__mxpeu + zvujx__kbc
    ailj__xeo = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        mxo__mfql, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    usn__cpvt = numba.core.target_extension.dispatcher_registry[cpu_target](
        crhih__ybr)
    usn__cpvt.add_overload(ailj__xeo)
    return usn__cpvt


def _rm_arg_agg_block(block, typemap):
    ktsjv__fetm = []
    arr_var = None
    for atl__wpdt, wme__almb in enumerate(block.body):
        if is_assign(wme__almb) and isinstance(wme__almb.value, ir.Arg):
            arr_var = wme__almb.target
            zqyzu__pqibn = typemap[arr_var.name]
            if not isinstance(zqyzu__pqibn, types.ArrayCompatible):
                ktsjv__fetm += block.body[atl__wpdt + 1:]
                break
            upy__cdks = block.body[atl__wpdt + 1]
            assert is_assign(upy__cdks) and isinstance(upy__cdks.value, ir.Expr
                ) and upy__cdks.value.op == 'getattr' and upy__cdks.value.attr == 'shape' and upy__cdks.value.value.name == arr_var.name
            mxdbk__nmm = upy__cdks.target
            gfwv__huf = block.body[atl__wpdt + 2]
            assert is_assign(gfwv__huf) and isinstance(gfwv__huf.value, ir.Expr
                ) and gfwv__huf.value.op == 'static_getitem' and gfwv__huf.value.value.name == mxdbk__nmm.name
            ktsjv__fetm += block.body[atl__wpdt + 3:]
            break
        ktsjv__fetm.append(wme__almb)
    return ktsjv__fetm, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    ruhkb__ngygt = wrap_parfor_blocks(parfor)
    sqif__nokw = find_topo_order(ruhkb__ngygt)
    sqif__nokw = sqif__nokw[1:]
    unwrap_parfor_blocks(parfor)
    for cty__pmz in reversed(sqif__nokw):
        for wme__almb in reversed(parfor.loop_body[cty__pmz].body):
            if isinstance(wme__almb, ir.Assign) and (wme__almb.target.name in
                parfor_params or wme__almb.target.name in var_to_param):
                jhzuu__yid = wme__almb.target.name
                rhs = wme__almb.value
                sals__asojo = (jhzuu__yid if jhzuu__yid in parfor_params else
                    var_to_param[jhzuu__yid])
                nkqnk__wdclo = []
                if isinstance(rhs, ir.Var):
                    nkqnk__wdclo = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    nkqnk__wdclo = [jvau__sot.name for jvau__sot in
                        wme__almb.value.list_vars()]
                param_uses[sals__asojo].extend(nkqnk__wdclo)
                for jvau__sot in nkqnk__wdclo:
                    var_to_param[jvau__sot] = sals__asojo
            if isinstance(wme__almb, Parfor):
                get_parfor_reductions(wme__almb, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for jdji__zjt, nkqnk__wdclo in param_uses.items():
        if jdji__zjt in nkqnk__wdclo and jdji__zjt not in reduce_varnames:
            reduce_varnames.append(jdji__zjt)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
