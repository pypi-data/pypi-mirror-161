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
        ice__cpzf = func.signature
        if ice__cpzf == types.none(types.voidptr):
            sjzft__axnx = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            aqu__exf = cgutils.get_or_insert_function(builder.module,
                sjzft__axnx, sym._literal_value)
            builder.call(aqu__exf, [context.get_constant_null(ice__cpzf.
                args[0])])
        elif ice__cpzf == types.none(types.int64, types.voidptr, types.voidptr
            ):
            sjzft__axnx = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            aqu__exf = cgutils.get_or_insert_function(builder.module,
                sjzft__axnx, sym._literal_value)
            builder.call(aqu__exf, [context.get_constant(types.int64, 0),
                context.get_constant_null(ice__cpzf.args[1]), context.
                get_constant_null(ice__cpzf.args[2])])
        else:
            sjzft__axnx = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            aqu__exf = cgutils.get_or_insert_function(builder.module,
                sjzft__axnx, sym._literal_value)
            builder.call(aqu__exf, [context.get_constant_null(ice__cpzf.
                args[0]), context.get_constant_null(ice__cpzf.args[1]),
                context.get_constant_null(ice__cpzf.args[2])])
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
        gsutv__aayu = True
        wvlu__izs = 1
        ayb__ywd = -1
        if isinstance(rhs, ir.Expr):
            for bmrhn__shp in rhs.kws:
                if func_name in list_cumulative:
                    if bmrhn__shp[0] == 'skipna':
                        gsutv__aayu = guard(find_const, func_ir, bmrhn__shp[1])
                        if not isinstance(gsutv__aayu, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if bmrhn__shp[0] == 'dropna':
                        gsutv__aayu = guard(find_const, func_ir, bmrhn__shp[1])
                        if not isinstance(gsutv__aayu, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            wvlu__izs = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', wvlu__izs)
            wvlu__izs = guard(find_const, func_ir, wvlu__izs)
        if func_name == 'head':
            ayb__ywd = get_call_expr_arg('head', rhs.args, dict(rhs.kws), 0,
                'n', 5)
            if not isinstance(ayb__ywd, int):
                ayb__ywd = guard(find_const, func_ir, ayb__ywd)
            if ayb__ywd < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = gsutv__aayu
        func.periods = wvlu__izs
        func.head_n = ayb__ywd
        if func_name == 'transform':
            kws = dict(rhs.kws)
            vlngc__yjbbd = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            nisf__ahkae = typemap[vlngc__yjbbd.name]
            ber__znjbv = None
            if isinstance(nisf__ahkae, str):
                ber__znjbv = nisf__ahkae
            elif is_overload_constant_str(nisf__ahkae):
                ber__znjbv = get_overload_const_str(nisf__ahkae)
            elif bodo.utils.typing.is_builtin_function(nisf__ahkae):
                ber__znjbv = bodo.utils.typing.get_builtin_function_name(
                    nisf__ahkae)
            if ber__znjbv not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {ber__znjbv}')
            func.transform_func = supported_agg_funcs.index(ber__znjbv)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    vlngc__yjbbd = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if vlngc__yjbbd == '':
        nisf__ahkae = types.none
    else:
        nisf__ahkae = typemap[vlngc__yjbbd.name]
    if is_overload_constant_dict(nisf__ahkae):
        dyp__qysa = get_overload_constant_dict(nisf__ahkae)
        oux__xkmf = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in dyp__qysa.values()]
        return oux__xkmf
    if nisf__ahkae == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(nisf__ahkae, types.BaseTuple) or is_overload_constant_list(
        nisf__ahkae):
        oux__xkmf = []
        vtso__fasy = 0
        if is_overload_constant_list(nisf__ahkae):
            tnzw__mgga = get_overload_const_list(nisf__ahkae)
        else:
            tnzw__mgga = nisf__ahkae.types
        for t in tnzw__mgga:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                oux__xkmf.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(tnzw__mgga) > 1:
                    func.fname = '<lambda_' + str(vtso__fasy) + '>'
                    vtso__fasy += 1
                oux__xkmf.append(func)
        return [oux__xkmf]
    if is_overload_constant_str(nisf__ahkae):
        func_name = get_overload_const_str(nisf__ahkae)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(nisf__ahkae):
        func_name = bodo.utils.typing.get_builtin_function_name(nisf__ahkae)
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
        vtso__fasy = 0
        ksp__zbt = []
        for floo__oij in f_val:
            func = get_agg_func_udf(func_ir, floo__oij, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{vtso__fasy}>'
                vtso__fasy += 1
            ksp__zbt.append(func)
        return ksp__zbt
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
    ber__znjbv = code.co_name
    return ber__znjbv


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
            cptz__qltsf = types.DType(args[0])
            return signature(cptz__qltsf, *args)


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
        return [caqxo__asdrc for caqxo__asdrc in self.in_vars if 
            caqxo__asdrc is not None]

    def get_live_out_vars(self):
        return [caqxo__asdrc for caqxo__asdrc in self.out_vars if 
            caqxo__asdrc is not None]

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
        faj__qfrwy = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        lhoa__rxpix = list(get_index_data_arr_types(self.out_type.index))
        return faj__qfrwy + lhoa__rxpix

    def update_dead_col_info(self):
        for svgfj__jfsry in self.dead_out_inds:
            self.gb_info_out.pop(svgfj__jfsry, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for snwvn__wso, muhm__dma in self.gb_info_in.copy().items():
            xarn__zjq = []
            for floo__oij, bkyol__pcot in muhm__dma:
                if bkyol__pcot not in self.dead_out_inds:
                    xarn__zjq.append((floo__oij, bkyol__pcot))
            if not xarn__zjq:
                if (snwvn__wso is not None and snwvn__wso not in self.
                    in_key_inds):
                    self.dead_in_inds.add(snwvn__wso)
                self.gb_info_in.pop(snwvn__wso)
            else:
                self.gb_info_in[snwvn__wso] = xarn__zjq
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for bxz__yzo in range(1, len(self.in_vars)):
                svgfj__jfsry = self.n_in_table_arrays + bxz__yzo - 1
                if svgfj__jfsry in self.dead_in_inds:
                    self.in_vars[bxz__yzo] = None
        else:
            for bxz__yzo in range(len(self.in_vars)):
                if bxz__yzo in self.dead_in_inds:
                    self.in_vars[bxz__yzo] = None

    def __repr__(self):
        ydobu__ndddp = ', '.join(caqxo__asdrc.name for caqxo__asdrc in self
            .get_live_in_vars())
        qirst__kjra = f'{self.df_in}{{{ydobu__ndddp}}}'
        jsws__hra = ', '.join(caqxo__asdrc.name for caqxo__asdrc in self.
            get_live_out_vars())
        ogl__bns = f'{self.df_out}{{{jsws__hra}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {qirst__kjra} {ogl__bns}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({caqxo__asdrc.name for caqxo__asdrc in aggregate_node.
        get_live_in_vars()})
    def_set.update({caqxo__asdrc.name for caqxo__asdrc in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    lvmq__lcfa = agg_node.out_vars[0]
    if lvmq__lcfa is not None and lvmq__lcfa.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            bnvk__pwk = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(bnvk__pwk)
        else:
            agg_node.dead_out_inds.add(0)
    for bxz__yzo in range(1, len(agg_node.out_vars)):
        caqxo__asdrc = agg_node.out_vars[bxz__yzo]
        if caqxo__asdrc is not None and caqxo__asdrc.name not in lives:
            agg_node.out_vars[bxz__yzo] = None
            svgfj__jfsry = agg_node.n_out_table_arrays + bxz__yzo - 1
            agg_node.dead_out_inds.add(svgfj__jfsry)
    if all(caqxo__asdrc is None for caqxo__asdrc in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    jgkrf__nysr = {caqxo__asdrc.name for caqxo__asdrc in aggregate_node.
        get_live_out_vars()}
    return set(), jgkrf__nysr


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for bxz__yzo in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[bxz__yzo] is not None:
            aggregate_node.in_vars[bxz__yzo] = replace_vars_inner(
                aggregate_node.in_vars[bxz__yzo], var_dict)
    for bxz__yzo in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[bxz__yzo] is not None:
            aggregate_node.out_vars[bxz__yzo] = replace_vars_inner(
                aggregate_node.out_vars[bxz__yzo], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for bxz__yzo in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[bxz__yzo] is not None:
            aggregate_node.in_vars[bxz__yzo] = visit_vars_inner(aggregate_node
                .in_vars[bxz__yzo], callback, cbdata)
    for bxz__yzo in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[bxz__yzo] is not None:
            aggregate_node.out_vars[bxz__yzo] = visit_vars_inner(aggregate_node
                .out_vars[bxz__yzo], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    fzf__iwkav = []
    for sphx__fwlor in aggregate_node.get_live_in_vars():
        pocg__uejb = equiv_set.get_shape(sphx__fwlor)
        if pocg__uejb is not None:
            fzf__iwkav.append(pocg__uejb[0])
    if len(fzf__iwkav) > 1:
        equiv_set.insert_equiv(*fzf__iwkav)
    kxay__rjyso = []
    fzf__iwkav = []
    for sphx__fwlor in aggregate_node.get_live_out_vars():
        oaly__ufo = typemap[sphx__fwlor.name]
        zuh__nnqa = array_analysis._gen_shape_call(equiv_set, sphx__fwlor,
            oaly__ufo.ndim, None, kxay__rjyso)
        equiv_set.insert_equiv(sphx__fwlor, zuh__nnqa)
        fzf__iwkav.append(zuh__nnqa[0])
        equiv_set.define(sphx__fwlor, set())
    if len(fzf__iwkav) > 1:
        equiv_set.insert_equiv(*fzf__iwkav)
    return [], kxay__rjyso


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    fqt__ilx = aggregate_node.get_live_in_vars()
    abw__bzrl = aggregate_node.get_live_out_vars()
    nprdi__bepsb = Distribution.OneD
    for sphx__fwlor in fqt__ilx:
        nprdi__bepsb = Distribution(min(nprdi__bepsb.value, array_dists[
            sphx__fwlor.name].value))
    utrw__gzpgz = Distribution(min(nprdi__bepsb.value, Distribution.
        OneD_Var.value))
    for sphx__fwlor in abw__bzrl:
        if sphx__fwlor.name in array_dists:
            utrw__gzpgz = Distribution(min(utrw__gzpgz.value, array_dists[
                sphx__fwlor.name].value))
    if utrw__gzpgz != Distribution.OneD_Var:
        nprdi__bepsb = utrw__gzpgz
    for sphx__fwlor in fqt__ilx:
        array_dists[sphx__fwlor.name] = nprdi__bepsb
    for sphx__fwlor in abw__bzrl:
        array_dists[sphx__fwlor.name] = utrw__gzpgz


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for sphx__fwlor in agg_node.get_live_out_vars():
        definitions[sphx__fwlor.name].append(agg_node)
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
    gdwh__bod = agg_node.get_live_in_vars()
    cywm__lxhml = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for caqxo__asdrc in (gdwh__bod + cywm__lxhml):
            if array_dists[caqxo__asdrc.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                caqxo__asdrc.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    oux__xkmf = []
    func_out_types = []
    for bkyol__pcot, (snwvn__wso, func) in agg_node.gb_info_out.items():
        if snwvn__wso is not None:
            t = agg_node.in_col_types[snwvn__wso]
            in_col_typs.append(t)
        oux__xkmf.append(func)
        func_out_types.append(out_col_typs[bkyol__pcot])
    fiej__pspw = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for bxz__yzo, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            fiej__pspw.update({f'in_cat_dtype_{bxz__yzo}': in_col_typ})
    for bxz__yzo, itqks__rsabo in enumerate(out_col_typs):
        if isinstance(itqks__rsabo, bodo.CategoricalArrayType):
            fiej__pspw.update({f'out_cat_dtype_{bxz__yzo}': itqks__rsabo})
    udf_func_struct = get_udf_func_struct(oux__xkmf, in_col_typs, typingctx,
        targetctx)
    out_var_types = [(typemap[caqxo__asdrc.name] if caqxo__asdrc is not
        None else types.none) for caqxo__asdrc in agg_node.out_vars]
    xiy__wyld, mnqpi__kswhu = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    fiej__pspw.update(mnqpi__kswhu)
    fiej__pspw.update({'pd': pd, 'pre_alloc_string_array':
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
            fiej__pspw.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            fiej__pspw.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    oct__pdbc = {}
    exec(xiy__wyld, {}, oct__pdbc)
    wbi__eia = oct__pdbc['agg_top']
    fibxp__hon = compile_to_numba_ir(wbi__eia, fiej__pspw, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[caqxo__asdrc
        .name] for caqxo__asdrc in gdwh__bod), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(fibxp__hon, gdwh__bod)
    jhxd__mji = fibxp__hon.body[-2].value.value
    lsgl__jbxt = fibxp__hon.body[:-2]
    for bxz__yzo, caqxo__asdrc in enumerate(cywm__lxhml):
        gen_getitem(caqxo__asdrc, jhxd__mji, bxz__yzo, calltypes, lsgl__jbxt)
    return lsgl__jbxt


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        nifg__ibgko = IntDtype(t.dtype).name
        assert nifg__ibgko.endswith('Dtype()')
        nifg__ibgko = nifg__ibgko[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{nifg__ibgko}'))"
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
        nli__fcgub = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {nli__fcgub}_cat_dtype_{colnum})')
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
    qti__mwq = udf_func_struct.var_typs
    btw__snpkg = len(qti__mwq)
    xiy__wyld = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    xiy__wyld += '    if is_null_pointer(in_table):\n'
    xiy__wyld += '        return\n'
    xiy__wyld += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in qti__mwq]), ',' if
        len(qti__mwq) == 1 else '')
    muwxh__kwpey = n_keys
    yha__rhbk = []
    redvar_offsets = []
    jkwfl__lsbrt = []
    if do_combine:
        for bxz__yzo, floo__oij in enumerate(allfuncs):
            if floo__oij.ftype != 'udf':
                muwxh__kwpey += floo__oij.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(muwxh__kwpey, muwxh__kwpey +
                    floo__oij.n_redvars))
                muwxh__kwpey += floo__oij.n_redvars
                jkwfl__lsbrt.append(data_in_typs_[func_idx_to_in_col[bxz__yzo]]
                    )
                yha__rhbk.append(func_idx_to_in_col[bxz__yzo] + n_keys)
    else:
        for bxz__yzo, floo__oij in enumerate(allfuncs):
            if floo__oij.ftype != 'udf':
                muwxh__kwpey += floo__oij.ncols_post_shuffle
            else:
                redvar_offsets += list(range(muwxh__kwpey + 1, muwxh__kwpey +
                    1 + floo__oij.n_redvars))
                muwxh__kwpey += floo__oij.n_redvars + 1
                jkwfl__lsbrt.append(data_in_typs_[func_idx_to_in_col[bxz__yzo]]
                    )
                yha__rhbk.append(func_idx_to_in_col[bxz__yzo] + n_keys)
    assert len(redvar_offsets) == btw__snpkg
    vth__stdf = len(jkwfl__lsbrt)
    oulc__vub = []
    for bxz__yzo, t in enumerate(jkwfl__lsbrt):
        oulc__vub.append(_gen_dummy_alloc(t, bxz__yzo, True))
    xiy__wyld += '    data_in_dummy = ({}{})\n'.format(','.join(oulc__vub),
        ',' if len(jkwfl__lsbrt) == 1 else '')
    xiy__wyld += """
    # initialize redvar cols
"""
    xiy__wyld += '    init_vals = __init_func()\n'
    for bxz__yzo in range(btw__snpkg):
        xiy__wyld += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(bxz__yzo, redvar_offsets[bxz__yzo], bxz__yzo))
        xiy__wyld += '    incref(redvar_arr_{})\n'.format(bxz__yzo)
        xiy__wyld += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(bxz__yzo,
            bxz__yzo)
    xiy__wyld += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(bxz__yzo) for bxz__yzo in range(btw__snpkg)]), ',' if 
        btw__snpkg == 1 else '')
    xiy__wyld += '\n'
    for bxz__yzo in range(vth__stdf):
        xiy__wyld += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(bxz__yzo, yha__rhbk[bxz__yzo], bxz__yzo))
        xiy__wyld += '    incref(data_in_{})\n'.format(bxz__yzo)
    xiy__wyld += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(bxz__yzo) for bxz__yzo in range(vth__stdf)]), ',' if 
        vth__stdf == 1 else '')
    xiy__wyld += '\n'
    xiy__wyld += '    for i in range(len(data_in_0)):\n'
    xiy__wyld += '        w_ind = row_to_group[i]\n'
    xiy__wyld += '        if w_ind != -1:\n'
    xiy__wyld += '            __update_redvars(redvars, data_in, w_ind, i)\n'
    oct__pdbc = {}
    exec(xiy__wyld, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, oct__pdbc)
    return oct__pdbc['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    qti__mwq = udf_func_struct.var_typs
    btw__snpkg = len(qti__mwq)
    xiy__wyld = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    xiy__wyld += '    if is_null_pointer(in_table):\n'
    xiy__wyld += '        return\n'
    xiy__wyld += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in qti__mwq]), ',' if
        len(qti__mwq) == 1 else '')
    dqf__ohy = n_keys
    qxew__vfkp = n_keys
    bouvs__dpo = []
    ziksn__iaguh = []
    for floo__oij in allfuncs:
        if floo__oij.ftype != 'udf':
            dqf__ohy += floo__oij.ncols_pre_shuffle
            qxew__vfkp += floo__oij.ncols_post_shuffle
        else:
            bouvs__dpo += list(range(dqf__ohy, dqf__ohy + floo__oij.n_redvars))
            ziksn__iaguh += list(range(qxew__vfkp + 1, qxew__vfkp + 1 +
                floo__oij.n_redvars))
            dqf__ohy += floo__oij.n_redvars
            qxew__vfkp += 1 + floo__oij.n_redvars
    assert len(bouvs__dpo) == btw__snpkg
    xiy__wyld += """
    # initialize redvar cols
"""
    xiy__wyld += '    init_vals = __init_func()\n'
    for bxz__yzo in range(btw__snpkg):
        xiy__wyld += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(bxz__yzo, ziksn__iaguh[bxz__yzo], bxz__yzo))
        xiy__wyld += '    incref(redvar_arr_{})\n'.format(bxz__yzo)
        xiy__wyld += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(bxz__yzo,
            bxz__yzo)
    xiy__wyld += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(bxz__yzo) for bxz__yzo in range(btw__snpkg)]), ',' if 
        btw__snpkg == 1 else '')
    xiy__wyld += '\n'
    for bxz__yzo in range(btw__snpkg):
        xiy__wyld += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(bxz__yzo, bouvs__dpo[bxz__yzo], bxz__yzo))
        xiy__wyld += '    incref(recv_redvar_arr_{})\n'.format(bxz__yzo)
    xiy__wyld += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(bxz__yzo) for bxz__yzo in range(
        btw__snpkg)]), ',' if btw__snpkg == 1 else '')
    xiy__wyld += '\n'
    if btw__snpkg:
        xiy__wyld += '    for i in range(len(recv_redvar_arr_0)):\n'
        xiy__wyld += '        w_ind = row_to_group[i]\n'
        xiy__wyld += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    oct__pdbc = {}
    exec(xiy__wyld, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, oct__pdbc)
    return oct__pdbc['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    qti__mwq = udf_func_struct.var_typs
    btw__snpkg = len(qti__mwq)
    muwxh__kwpey = n_keys
    redvar_offsets = []
    yts__xpnd = []
    cqx__rcz = []
    for bxz__yzo, floo__oij in enumerate(allfuncs):
        if floo__oij.ftype != 'udf':
            muwxh__kwpey += floo__oij.ncols_post_shuffle
        else:
            yts__xpnd.append(muwxh__kwpey)
            redvar_offsets += list(range(muwxh__kwpey + 1, muwxh__kwpey + 1 +
                floo__oij.n_redvars))
            muwxh__kwpey += 1 + floo__oij.n_redvars
            cqx__rcz.append(out_data_typs_[bxz__yzo])
    assert len(redvar_offsets) == btw__snpkg
    vth__stdf = len(cqx__rcz)
    xiy__wyld = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    xiy__wyld += '    if is_null_pointer(table):\n'
    xiy__wyld += '        return\n'
    xiy__wyld += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in qti__mwq]), ',' if
        len(qti__mwq) == 1 else '')
    xiy__wyld += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in cqx__rcz]
        ), ',' if len(cqx__rcz) == 1 else '')
    for bxz__yzo in range(btw__snpkg):
        xiy__wyld += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(bxz__yzo, redvar_offsets[bxz__yzo], bxz__yzo))
        xiy__wyld += '    incref(redvar_arr_{})\n'.format(bxz__yzo)
    xiy__wyld += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(bxz__yzo) for bxz__yzo in range(btw__snpkg)]), ',' if 
        btw__snpkg == 1 else '')
    xiy__wyld += '\n'
    for bxz__yzo in range(vth__stdf):
        xiy__wyld += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(bxz__yzo, yts__xpnd[bxz__yzo], bxz__yzo))
        xiy__wyld += '    incref(data_out_{})\n'.format(bxz__yzo)
    xiy__wyld += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(bxz__yzo) for bxz__yzo in range(vth__stdf)]), ',' if 
        vth__stdf == 1 else '')
    xiy__wyld += '\n'
    xiy__wyld += '    for i in range(len(data_out_0)):\n'
    xiy__wyld += '        __eval_res(redvars, data_out, i)\n'
    oct__pdbc = {}
    exec(xiy__wyld, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, oct__pdbc)
    return oct__pdbc['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    muwxh__kwpey = n_keys
    izzip__mppm = []
    for bxz__yzo, floo__oij in enumerate(allfuncs):
        if floo__oij.ftype == 'gen_udf':
            izzip__mppm.append(muwxh__kwpey)
            muwxh__kwpey += 1
        elif floo__oij.ftype != 'udf':
            muwxh__kwpey += floo__oij.ncols_post_shuffle
        else:
            muwxh__kwpey += floo__oij.n_redvars + 1
    xiy__wyld = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    xiy__wyld += '    if num_groups == 0:\n'
    xiy__wyld += '        return\n'
    for bxz__yzo, func in enumerate(udf_func_struct.general_udf_funcs):
        xiy__wyld += '    # col {}\n'.format(bxz__yzo)
        xiy__wyld += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(izzip__mppm[bxz__yzo], bxz__yzo))
        xiy__wyld += '    incref(out_col)\n'
        xiy__wyld += '    for j in range(num_groups):\n'
        xiy__wyld += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(bxz__yzo, bxz__yzo))
        xiy__wyld += '        incref(in_col)\n'
        xiy__wyld += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(bxz__yzo))
    fiej__pspw = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    cxhkp__aenye = 0
    for bxz__yzo, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[cxhkp__aenye]
        fiej__pspw['func_{}'.format(cxhkp__aenye)] = func
        fiej__pspw['in_col_{}_typ'.format(cxhkp__aenye)] = in_col_typs[
            func_idx_to_in_col[bxz__yzo]]
        fiej__pspw['out_col_{}_typ'.format(cxhkp__aenye)] = out_col_typs[
            bxz__yzo]
        cxhkp__aenye += 1
    oct__pdbc = {}
    exec(xiy__wyld, fiej__pspw, oct__pdbc)
    floo__oij = oct__pdbc['bodo_gb_apply_general_udfs{}'.format(label_suffix)]
    cqz__jlpm = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(cqz__jlpm, nopython=True)(floo__oij)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    oojz__vduxr = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        lfiry__fgpi = []
        if agg_node.in_vars[0] is not None:
            lfiry__fgpi.append('arg0')
        for bxz__yzo in range(agg_node.n_in_table_arrays, agg_node.n_in_cols):
            if bxz__yzo not in agg_node.dead_in_inds:
                lfiry__fgpi.append(f'arg{bxz__yzo}')
    else:
        lfiry__fgpi = [f'arg{bxz__yzo}' for bxz__yzo, caqxo__asdrc in
            enumerate(agg_node.in_vars) if caqxo__asdrc is not None]
    xiy__wyld = f"def agg_top({', '.join(lfiry__fgpi)}):\n"
    gir__isjo = []
    if agg_node.is_in_table_format:
        gir__isjo = agg_node.in_key_inds + [snwvn__wso for snwvn__wso,
            pnon__beg in agg_node.gb_info_out.values() if snwvn__wso is not
            None]
        if agg_node.input_has_index:
            gir__isjo.append(agg_node.n_in_cols - 1)
        vahwn__jtodj = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        ptw__ckkb = []
        for bxz__yzo in range(agg_node.n_in_table_arrays, agg_node.n_in_cols):
            if bxz__yzo in agg_node.dead_in_inds:
                ptw__ckkb.append('None')
            else:
                ptw__ckkb.append(f'arg{bxz__yzo}')
        khqpe__ybza = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        xiy__wyld += f"""    table = py_data_to_cpp_table({khqpe__ybza}, ({', '.join(ptw__ckkb)}{vahwn__jtodj}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        egdan__qqgg = [f'arg{bxz__yzo}' for bxz__yzo in agg_node.in_key_inds]
        dov__ohcv = [f'arg{snwvn__wso}' for snwvn__wso, pnon__beg in
            agg_node.gb_info_out.values() if snwvn__wso is not None]
        bqgf__agp = egdan__qqgg + dov__ohcv
        if agg_node.input_has_index:
            bqgf__agp.append(f'arg{len(agg_node.in_vars) - 1}')
        xiy__wyld += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({shk__sil})' for shk__sil in bqgf__agp))
        xiy__wyld += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    tezk__akhl = []
    func_idx_to_in_col = []
    brsl__qnh = []
    gsutv__aayu = False
    glk__bvkx = 1
    ayb__ywd = -1
    etkl__cho = 0
    ule__mgyhj = 0
    oux__xkmf = [func for pnon__beg, func in agg_node.gb_info_out.values()]
    for zpszn__avea, func in enumerate(oux__xkmf):
        tezk__akhl.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            etkl__cho += 1
        if hasattr(func, 'skipdropna'):
            gsutv__aayu = func.skipdropna
        if func.ftype == 'shift':
            glk__bvkx = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            ule__mgyhj = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            ayb__ywd = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(zpszn__avea)
        if func.ftype == 'udf':
            brsl__qnh.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            brsl__qnh.append(0)
            do_combine = False
    tezk__akhl.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if etkl__cho > 0:
        if etkl__cho != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    bvko__juucr = []
    if udf_func_struct is not None:
        rczsk__rryaa = next_label()
        if udf_func_struct.regular_udfs:
            cqz__jlpm = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            oivv__bdoju = numba.cfunc(cqz__jlpm, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs, do_combine,
                func_idx_to_in_col, rczsk__rryaa))
            ahqc__lmogq = numba.cfunc(cqz__jlpm, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, rczsk__rryaa))
            xsb__dpm = numba.cfunc('void(voidptr)', nopython=True)(gen_eval_cb
                (udf_func_struct, allfuncs, n_keys, func_out_types,
                rczsk__rryaa))
            udf_func_struct.set_regular_cfuncs(oivv__bdoju, ahqc__lmogq,
                xsb__dpm)
            for aqfrr__sfc in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[aqfrr__sfc.native_name] = aqfrr__sfc
                gb_agg_cfunc_addr[aqfrr__sfc.native_name] = aqfrr__sfc.address
        if udf_func_struct.general_udfs:
            hikkh__acnn = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, func_out_types, func_idx_to_in_col,
                rczsk__rryaa)
            udf_func_struct.set_general_cfunc(hikkh__acnn)
        qti__mwq = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        zst__hktlu = 0
        bxz__yzo = 0
        for ddpn__whxk, floo__oij in zip(agg_node.gb_info_out.keys(), allfuncs
            ):
            if floo__oij.ftype in ('udf', 'gen_udf'):
                bvko__juucr.append(out_col_typs[ddpn__whxk])
                for nnl__lhg in range(zst__hktlu, zst__hktlu + brsl__qnh[
                    bxz__yzo]):
                    bvko__juucr.append(dtype_to_array_type(qti__mwq[nnl__lhg]))
                zst__hktlu += brsl__qnh[bxz__yzo]
                bxz__yzo += 1
        xiy__wyld += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{bxz__yzo}' for bxz__yzo in range(len(bvko__juucr)))}{',' if len(bvko__juucr) == 1 else ''}))
"""
        xiy__wyld += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(bvko__juucr)})
"""
        if udf_func_struct.regular_udfs:
            xiy__wyld += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{oivv__bdoju.native_name}')\n"
                )
            xiy__wyld += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{ahqc__lmogq.native_name}')\n"
                )
            xiy__wyld += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{xsb__dpm.native_name}')\n"
                )
            xiy__wyld += (
                f"    cpp_cb_update_addr = get_agg_udf_addr('{oivv__bdoju.native_name}')\n"
                )
            xiy__wyld += f"""    cpp_cb_combine_addr = get_agg_udf_addr('{ahqc__lmogq.native_name}')
"""
            xiy__wyld += (
                f"    cpp_cb_eval_addr = get_agg_udf_addr('{xsb__dpm.native_name}')\n"
                )
        else:
            xiy__wyld += '    cpp_cb_update_addr = 0\n'
            xiy__wyld += '    cpp_cb_combine_addr = 0\n'
            xiy__wyld += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            aqfrr__sfc = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[aqfrr__sfc.native_name] = aqfrr__sfc
            gb_agg_cfunc_addr[aqfrr__sfc.native_name] = aqfrr__sfc.address
            xiy__wyld += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{aqfrr__sfc.native_name}')\n"
                )
            xiy__wyld += (
                f"    cpp_cb_general_addr = get_agg_udf_addr('{aqfrr__sfc.native_name}')\n"
                )
        else:
            xiy__wyld += '    cpp_cb_general_addr = 0\n'
    else:
        xiy__wyld += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        xiy__wyld += '    cpp_cb_update_addr = 0\n'
        xiy__wyld += '    cpp_cb_combine_addr = 0\n'
        xiy__wyld += '    cpp_cb_eval_addr = 0\n'
        xiy__wyld += '    cpp_cb_general_addr = 0\n'
    xiy__wyld += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(floo__oij.ftype)) for
        floo__oij in allfuncs] + ['0']))
    xiy__wyld += (
        f'    func_offsets = np.array({str(tezk__akhl)}, dtype=np.int32)\n')
    if len(brsl__qnh) > 0:
        xiy__wyld += (
            f'    udf_ncols = np.array({str(brsl__qnh)}, dtype=np.int32)\n')
    else:
        xiy__wyld += '    udf_ncols = np.array([0], np.int32)\n'
    xiy__wyld += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    xiy__wyld += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {gsutv__aayu}, {glk__bvkx}, {ule__mgyhj}, {ayb__ywd}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes)
"""
    mslm__mtgvk = []
    xsptq__gobak = 0
    if agg_node.return_key:
        nzcg__zvud = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for bxz__yzo in range(n_keys):
            svgfj__jfsry = nzcg__zvud + bxz__yzo
            mslm__mtgvk.append(svgfj__jfsry if svgfj__jfsry not in agg_node
                .dead_out_inds else -1)
            xsptq__gobak += 1
    for ddpn__whxk in agg_node.gb_info_out.keys():
        mslm__mtgvk.append(ddpn__whxk)
        xsptq__gobak += 1
    wuk__sxf = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            mslm__mtgvk.append(agg_node.n_out_cols - 1)
        else:
            wuk__sxf = True
    vahwn__jtodj = ',' if oojz__vduxr == 1 else ''
    lzowf__adkz = (
        f"({', '.join(f'out_type{bxz__yzo}' for bxz__yzo in range(oojz__vduxr))}{vahwn__jtodj})"
        )
    wek__ebnl = []
    tnsp__riy = []
    for bxz__yzo, t in enumerate(out_col_typs):
        if bxz__yzo not in agg_node.dead_out_inds and type_has_unknown_cats(t):
            if bxz__yzo in agg_node.gb_info_out:
                snwvn__wso = agg_node.gb_info_out[bxz__yzo][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                kyvn__uylt = bxz__yzo - nzcg__zvud
                snwvn__wso = agg_node.in_key_inds[kyvn__uylt]
            tnsp__riy.append(bxz__yzo)
            if (agg_node.is_in_table_format and snwvn__wso < agg_node.
                n_in_table_arrays):
                wek__ebnl.append(f'get_table_data(arg0, {snwvn__wso})')
            else:
                wek__ebnl.append(f'arg{snwvn__wso}')
    vahwn__jtodj = ',' if len(wek__ebnl) == 1 else ''
    xiy__wyld += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {lzowf__adkz}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(wek__ebnl)}{vahwn__jtodj}), unknown_cat_out_inds)
"""
    xiy__wyld += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    xiy__wyld += '    delete_table_decref_arrays(table)\n'
    xiy__wyld += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for bxz__yzo in range(n_keys):
            if mslm__mtgvk[bxz__yzo] == -1:
                xiy__wyld += f'    decref_table_array(out_table, {bxz__yzo})\n'
    if wuk__sxf:
        tdfqy__nhad = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        xiy__wyld += f'    decref_table_array(out_table, {tdfqy__nhad})\n'
    xiy__wyld += '    delete_table(out_table)\n'
    xiy__wyld += '    ev_clean.finalize()\n'
    xiy__wyld += '    return out_data\n'
    hsf__pyin = {f'out_type{bxz__yzo}': out_var_types[bxz__yzo] for
        bxz__yzo in range(oojz__vduxr)}
    hsf__pyin['out_col_inds'] = MetaType(tuple(mslm__mtgvk))
    hsf__pyin['in_col_inds'] = MetaType(tuple(gir__isjo))
    hsf__pyin['cpp_table_to_py_data'] = cpp_table_to_py_data
    hsf__pyin['py_data_to_cpp_table'] = py_data_to_cpp_table
    hsf__pyin.update({f'udf_type{bxz__yzo}': t for bxz__yzo, t in enumerate
        (bvko__juucr)})
    hsf__pyin['udf_dummy_col_inds'] = MetaType(tuple(range(len(bvko__juucr))))
    hsf__pyin['create_dummy_table'] = create_dummy_table
    hsf__pyin['unknown_cat_out_inds'] = MetaType(tuple(tnsp__riy))
    hsf__pyin['get_table_data'] = bodo.hiframes.table.get_table_data
    return xiy__wyld, hsf__pyin


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    cdd__qqyd = tuple(unwrap_typeref(data_types.types[bxz__yzo]) for
        bxz__yzo in range(len(data_types.types)))
    eegdf__wtav = bodo.TableType(cdd__qqyd)
    hsf__pyin = {'table_type': eegdf__wtav}
    xiy__wyld = 'def impl(data_types):\n'
    xiy__wyld += '  py_table = init_table(table_type, False)\n'
    xiy__wyld += '  py_table = set_table_len(py_table, 1)\n'
    for oaly__ufo, hgast__vsqs in eegdf__wtav.type_to_blk.items():
        hsf__pyin[f'typ_list_{hgast__vsqs}'] = types.List(oaly__ufo)
        hsf__pyin[f'typ_{hgast__vsqs}'] = oaly__ufo
        bfo__avw = len(eegdf__wtav.block_to_arr_ind[hgast__vsqs])
        xiy__wyld += f"""  arr_list_{hgast__vsqs} = alloc_list_like(typ_list_{hgast__vsqs}, {bfo__avw}, False)
"""
        xiy__wyld += f'  for i in range(len(arr_list_{hgast__vsqs})):\n'
        xiy__wyld += (
            f'    arr_list_{hgast__vsqs}[i] = alloc_type(1, typ_{hgast__vsqs}, (-1,))\n'
            )
        xiy__wyld += f"""  py_table = set_table_block(py_table, arr_list_{hgast__vsqs}, {hgast__vsqs})
"""
    xiy__wyld += '  return py_table\n'
    hsf__pyin.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    oct__pdbc = {}
    exec(xiy__wyld, hsf__pyin, oct__pdbc)
    return oct__pdbc['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    uft__pbwx = agg_node.in_vars[0].name
    fuft__ioy, ysqe__nhx, qfrzn__fdsi = block_use_map[uft__pbwx]
    if ysqe__nhx or qfrzn__fdsi:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        bay__eef, snd__muthb, txz__erc = _compute_table_column_uses(agg_node
            .out_vars[0].name, table_col_use_map, equiv_vars)
        if snd__muthb or txz__erc:
            bay__eef = set(range(agg_node.n_out_table_arrays))
    else:
        bay__eef = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            bay__eef = {0}
    fyc__fvt = set(bxz__yzo for bxz__yzo in agg_node.in_key_inds if 
        bxz__yzo < agg_node.n_in_table_arrays)
    zcee__roi = set(agg_node.gb_info_out[bxz__yzo][0] for bxz__yzo in
        bay__eef if bxz__yzo in agg_node.gb_info_out and agg_node.
        gb_info_out[bxz__yzo][0] is not None)
    zcee__roi |= fyc__fvt | fuft__ioy
    fswsf__nho = len(set(range(agg_node.n_in_table_arrays)) - zcee__roi) == 0
    block_use_map[uft__pbwx] = zcee__roi, fswsf__nho, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    trv__vzgm = agg_node.n_out_table_arrays
    riwd__xgy = agg_node.out_vars[0].name
    scaw__hjdg = _find_used_columns(riwd__xgy, trv__vzgm, column_live_map,
        equiv_vars)
    if scaw__hjdg is None:
        return False
    xzm__pudj = set(range(trv__vzgm)) - scaw__hjdg
    yld__xma = len(xzm__pudj - agg_node.dead_out_inds) != 0
    if yld__xma:
        agg_node.dead_out_inds.update(xzm__pudj)
        agg_node.update_dead_col_info()
    return yld__xma


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for fbx__xwhu in block.body:
            if is_call_assign(fbx__xwhu) and find_callname(f_ir, fbx__xwhu.
                value) == ('len', 'builtins') and fbx__xwhu.value.args[0
                ].name == f_ir.arg_names[0]:
                vor__uwfq = get_definition(f_ir, fbx__xwhu.value.func)
                vor__uwfq.name = 'dummy_agg_count'
                vor__uwfq.value = dummy_agg_count
    lcem__cfn = get_name_var_table(f_ir.blocks)
    oboqp__ass = {}
    for name, pnon__beg in lcem__cfn.items():
        oboqp__ass[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, oboqp__ass)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    bqmw__yewo = numba.core.compiler.Flags()
    bqmw__yewo.nrt = True
    scke__mki = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, bqmw__yewo)
    scke__mki.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, zqzs__eqf, calltypes, pnon__beg = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    ute__ssij = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    kpipt__vlaq = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    zndc__jelz = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    nvv__nbfhi = zndc__jelz(typemap, calltypes)
    pm = kpipt__vlaq(typingctx, targetctx, None, f_ir, typemap, zqzs__eqf,
        calltypes, nvv__nbfhi, {}, bqmw__yewo, None)
    gyw__ewrwl = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = kpipt__vlaq(typingctx, targetctx, None, f_ir, typemap, zqzs__eqf,
        calltypes, nvv__nbfhi, {}, bqmw__yewo, gyw__ewrwl)
    kgkw__ckiul = numba.core.typed_passes.InlineOverloads()
    kgkw__ckiul.run_pass(pm)
    soedq__lihmw = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    soedq__lihmw.run()
    for block in f_ir.blocks.values():
        for fbx__xwhu in block.body:
            if is_assign(fbx__xwhu) and isinstance(fbx__xwhu.value, (ir.Arg,
                ir.Var)) and isinstance(typemap[fbx__xwhu.target.name],
                SeriesType):
                oaly__ufo = typemap.pop(fbx__xwhu.target.name)
                typemap[fbx__xwhu.target.name] = oaly__ufo.data
            if is_call_assign(fbx__xwhu) and find_callname(f_ir, fbx__xwhu.
                value) == ('get_series_data', 'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[fbx__xwhu.target.name].remove(fbx__xwhu.value
                    )
                fbx__xwhu.value = fbx__xwhu.value.args[0]
                f_ir._definitions[fbx__xwhu.target.name].append(fbx__xwhu.value
                    )
            if is_call_assign(fbx__xwhu) and find_callname(f_ir, fbx__xwhu.
                value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[fbx__xwhu.target.name].remove(fbx__xwhu.value
                    )
                fbx__xwhu.value = ir.Const(False, fbx__xwhu.loc)
                f_ir._definitions[fbx__xwhu.target.name].append(fbx__xwhu.value
                    )
            if is_call_assign(fbx__xwhu) and find_callname(f_ir, fbx__xwhu.
                value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[fbx__xwhu.target.name].remove(fbx__xwhu.value
                    )
                fbx__xwhu.value = ir.Const(False, fbx__xwhu.loc)
                f_ir._definitions[fbx__xwhu.target.name].append(fbx__xwhu.value
                    )
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    oggmv__mwkm = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, ute__ssij)
    oggmv__mwkm.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    tzlx__eeyf = numba.core.compiler.StateDict()
    tzlx__eeyf.func_ir = f_ir
    tzlx__eeyf.typemap = typemap
    tzlx__eeyf.calltypes = calltypes
    tzlx__eeyf.typingctx = typingctx
    tzlx__eeyf.targetctx = targetctx
    tzlx__eeyf.return_type = zqzs__eqf
    numba.core.rewrites.rewrite_registry.apply('after-inference', tzlx__eeyf)
    qvjdz__sdqkm = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        zqzs__eqf, typingctx, targetctx, ute__ssij, bqmw__yewo, {})
    qvjdz__sdqkm.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            hmo__evkj = ctypes.pythonapi.PyCell_Get
            hmo__evkj.restype = ctypes.py_object
            hmo__evkj.argtypes = ctypes.py_object,
            dyp__qysa = tuple(hmo__evkj(sqaf__rthuk) for sqaf__rthuk in closure
                )
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            dyp__qysa = closure.items
        assert len(code.co_freevars) == len(dyp__qysa)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, dyp__qysa)


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
        nwu__igfrw = SeriesType(in_col_typ.dtype, to_str_arr_if_dict_array(
            in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (nwu__igfrw,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        mmh__mjfx, arr_var = _rm_arg_agg_block(block, pm.typemap)
        voyrd__zll = -1
        for bxz__yzo, fbx__xwhu in enumerate(mmh__mjfx):
            if isinstance(fbx__xwhu, numba.parfors.parfor.Parfor):
                assert voyrd__zll == -1, 'only one parfor for aggregation function'
                voyrd__zll = bxz__yzo
        parfor = None
        if voyrd__zll != -1:
            parfor = mmh__mjfx[voyrd__zll]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = mmh__mjfx[:voyrd__zll] + parfor.init_block.body
        eval_nodes = mmh__mjfx[voyrd__zll + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for fbx__xwhu in init_nodes:
            if is_assign(fbx__xwhu) and fbx__xwhu.target.name in redvars:
                ind = redvars.index(fbx__xwhu.target.name)
                reduce_vars[ind] = fbx__xwhu.target
        var_types = [pm.typemap[caqxo__asdrc] for caqxo__asdrc in redvars]
        cpybx__span = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        cqp__jyq = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        ami__uvx = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(ami__uvx)
        self.all_update_funcs.append(cqp__jyq)
        self.all_combine_funcs.append(cpybx__span)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        lldom__ubdb = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        egz__hdmgq = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        mca__ugtyy = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        ebn__svfc = gen_all_eval_func(self.all_eval_funcs, self.redvar_offsets)
        return (self.all_vartypes, lldom__ubdb, egz__hdmgq, mca__ugtyy,
            ebn__svfc)


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
    llgr__llb = []
    for t, floo__oij in zip(in_col_types, agg_func):
        llgr__llb.append((t, floo__oij))
    kwwip__hnrco = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    mmuu__xks = GeneralUDFGenerator()
    for in_col_typ, func in llgr__llb:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            kwwip__hnrco.add_udf(in_col_typ, func)
        except:
            mmuu__xks.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = kwwip__hnrco.gen_all_func()
    general_udf_funcs = mmuu__xks.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    evdzg__vbs = compute_use_defs(parfor.loop_body)
    hggg__ignvi = set()
    for bdg__vrfuq in evdzg__vbs.usemap.values():
        hggg__ignvi |= bdg__vrfuq
    xmt__jrvf = set()
    for bdg__vrfuq in evdzg__vbs.defmap.values():
        xmt__jrvf |= bdg__vrfuq
    edmx__krox = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    edmx__krox.body = eval_nodes
    ghadq__vvn = compute_use_defs({(0): edmx__krox})
    aws__duf = ghadq__vvn.usemap[0]
    omln__dnh = set()
    ervu__zhm = []
    slnye__jkzt = []
    for fbx__xwhu in reversed(init_nodes):
        rmrc__zrk = {caqxo__asdrc.name for caqxo__asdrc in fbx__xwhu.
            list_vars()}
        if is_assign(fbx__xwhu):
            caqxo__asdrc = fbx__xwhu.target.name
            rmrc__zrk.remove(caqxo__asdrc)
            if (caqxo__asdrc in hggg__ignvi and caqxo__asdrc not in
                omln__dnh and caqxo__asdrc not in aws__duf and caqxo__asdrc
                 not in xmt__jrvf):
                slnye__jkzt.append(fbx__xwhu)
                hggg__ignvi |= rmrc__zrk
                xmt__jrvf.add(caqxo__asdrc)
                continue
        omln__dnh |= rmrc__zrk
        ervu__zhm.append(fbx__xwhu)
    slnye__jkzt.reverse()
    ervu__zhm.reverse()
    rhdlq__mhxcp = min(parfor.loop_body.keys())
    jme__zis = parfor.loop_body[rhdlq__mhxcp]
    jme__zis.body = slnye__jkzt + jme__zis.body
    return ervu__zhm


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    ret__boam = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    mjvv__aas = set()
    gts__rvfi = []
    for fbx__xwhu in init_nodes:
        if is_assign(fbx__xwhu) and isinstance(fbx__xwhu.value, ir.Global
            ) and isinstance(fbx__xwhu.value.value, pytypes.FunctionType
            ) and fbx__xwhu.value.value in ret__boam:
            mjvv__aas.add(fbx__xwhu.target.name)
        elif is_call_assign(fbx__xwhu
            ) and fbx__xwhu.value.func.name in mjvv__aas:
            pass
        else:
            gts__rvfi.append(fbx__xwhu)
    init_nodes = gts__rvfi
    ceu__yilz = types.Tuple(var_types)
    jooi__tlog = lambda : None
    f_ir = compile_to_numba_ir(jooi__tlog, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    qrqs__fag = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    nzdfc__fdyxl = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        qrqs__fag, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [nzdfc__fdyxl] + block.body
    block.body[-2].value.value = qrqs__fag
    bsws__rtgqn = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        ceu__yilz, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    iqok__kek = numba.core.target_extension.dispatcher_registry[cpu_target](
        jooi__tlog)
    iqok__kek.add_overload(bsws__rtgqn)
    return iqok__kek


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    fqdqw__pbg = len(update_funcs)
    xymul__vqufq = len(in_col_types)
    xiy__wyld = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for nnl__lhg in range(fqdqw__pbg):
        ksqcw__pxazk = ', '.join(['redvar_arrs[{}][w_ind]'.format(bxz__yzo) for
            bxz__yzo in range(redvar_offsets[nnl__lhg], redvar_offsets[
            nnl__lhg + 1])])
        if ksqcw__pxazk:
            xiy__wyld += '  {} = update_vars_{}({},  data_in[{}][i])\n'.format(
                ksqcw__pxazk, nnl__lhg, ksqcw__pxazk, 0 if xymul__vqufq == 
                1 else nnl__lhg)
    xiy__wyld += '  return\n'
    fiej__pspw = {}
    for bxz__yzo, floo__oij in enumerate(update_funcs):
        fiej__pspw['update_vars_{}'.format(bxz__yzo)] = floo__oij
    oct__pdbc = {}
    exec(xiy__wyld, fiej__pspw, oct__pdbc)
    ruqc__tvg = oct__pdbc['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(ruqc__tvg)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    bzu__mgr = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types])
    arg_typs = bzu__mgr, bzu__mgr, types.intp, types.intp
    wavk__rhzt = len(redvar_offsets) - 1
    xiy__wyld = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for nnl__lhg in range(wavk__rhzt):
        ksqcw__pxazk = ', '.join(['redvar_arrs[{}][w_ind]'.format(bxz__yzo) for
            bxz__yzo in range(redvar_offsets[nnl__lhg], redvar_offsets[
            nnl__lhg + 1])])
        mlinu__xpqbm = ', '.join(['recv_arrs[{}][i]'.format(bxz__yzo) for
            bxz__yzo in range(redvar_offsets[nnl__lhg], redvar_offsets[
            nnl__lhg + 1])])
        if mlinu__xpqbm:
            xiy__wyld += '  {} = combine_vars_{}({}, {})\n'.format(ksqcw__pxazk
                , nnl__lhg, ksqcw__pxazk, mlinu__xpqbm)
    xiy__wyld += '  return\n'
    fiej__pspw = {}
    for bxz__yzo, floo__oij in enumerate(combine_funcs):
        fiej__pspw['combine_vars_{}'.format(bxz__yzo)] = floo__oij
    oct__pdbc = {}
    exec(xiy__wyld, fiej__pspw, oct__pdbc)
    qnqmp__ckb = oct__pdbc['combine_all_f']
    f_ir = compile_to_numba_ir(qnqmp__ckb, fiej__pspw)
    mca__ugtyy = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    iqok__kek = numba.core.target_extension.dispatcher_registry[cpu_target](
        qnqmp__ckb)
    iqok__kek.add_overload(mca__ugtyy)
    return iqok__kek


def gen_all_eval_func(eval_funcs, redvar_offsets):
    wavk__rhzt = len(redvar_offsets) - 1
    xiy__wyld = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for nnl__lhg in range(wavk__rhzt):
        ksqcw__pxazk = ', '.join(['redvar_arrs[{}][j]'.format(bxz__yzo) for
            bxz__yzo in range(redvar_offsets[nnl__lhg], redvar_offsets[
            nnl__lhg + 1])])
        xiy__wyld += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(nnl__lhg,
            nnl__lhg, ksqcw__pxazk)
    xiy__wyld += '  return\n'
    fiej__pspw = {}
    for bxz__yzo, floo__oij in enumerate(eval_funcs):
        fiej__pspw['eval_vars_{}'.format(bxz__yzo)] = floo__oij
    oct__pdbc = {}
    exec(xiy__wyld, fiej__pspw, oct__pdbc)
    xtmxb__anh = oct__pdbc['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(xtmxb__anh)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    jtn__yaux = len(var_types)
    way__xfcyw = [f'in{bxz__yzo}' for bxz__yzo in range(jtn__yaux)]
    ceu__yilz = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    tzl__qya = ceu__yilz(0)
    xiy__wyld = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        way__xfcyw))
    oct__pdbc = {}
    exec(xiy__wyld, {'_zero': tzl__qya}, oct__pdbc)
    dqwe__ihp = oct__pdbc['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(dqwe__ihp, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': tzl__qya}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    czxfq__gvr = []
    for bxz__yzo, caqxo__asdrc in enumerate(reduce_vars):
        czxfq__gvr.append(ir.Assign(block.body[bxz__yzo].target,
            caqxo__asdrc, caqxo__asdrc.loc))
        for agjst__htwfb in caqxo__asdrc.versioned_names:
            czxfq__gvr.append(ir.Assign(caqxo__asdrc, ir.Var(caqxo__asdrc.
                scope, agjst__htwfb, caqxo__asdrc.loc), caqxo__asdrc.loc))
    block.body = block.body[:jtn__yaux] + czxfq__gvr + eval_nodes
    ami__uvx = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        ceu__yilz, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    iqok__kek = numba.core.target_extension.dispatcher_registry[cpu_target](
        dqwe__ihp)
    iqok__kek.add_overload(ami__uvx)
    return iqok__kek


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    jtn__yaux = len(redvars)
    pdbts__kzskl = [f'v{bxz__yzo}' for bxz__yzo in range(jtn__yaux)]
    way__xfcyw = [f'in{bxz__yzo}' for bxz__yzo in range(jtn__yaux)]
    xiy__wyld = 'def agg_combine({}):\n'.format(', '.join(pdbts__kzskl +
        way__xfcyw))
    xdm__ygbl = wrap_parfor_blocks(parfor)
    pytux__qlblq = find_topo_order(xdm__ygbl)
    pytux__qlblq = pytux__qlblq[1:]
    unwrap_parfor_blocks(parfor)
    thti__mwmn = {}
    cgmzr__upew = []
    for mjek__bkmav in pytux__qlblq:
        duiah__elzog = parfor.loop_body[mjek__bkmav]
        for fbx__xwhu in duiah__elzog.body:
            if is_assign(fbx__xwhu) and fbx__xwhu.target.name in redvars:
                fxwr__pvnfe = fbx__xwhu.target.name
                ind = redvars.index(fxwr__pvnfe)
                if ind in cgmzr__upew:
                    continue
                if len(f_ir._definitions[fxwr__pvnfe]) == 2:
                    var_def = f_ir._definitions[fxwr__pvnfe][0]
                    xiy__wyld += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[fxwr__pvnfe][1]
                    xiy__wyld += _match_reduce_def(var_def, f_ir, ind)
    xiy__wyld += '    return {}'.format(', '.join(['v{}'.format(bxz__yzo) for
        bxz__yzo in range(jtn__yaux)]))
    oct__pdbc = {}
    exec(xiy__wyld, {}, oct__pdbc)
    cio__ojwo = oct__pdbc['agg_combine']
    arg_typs = tuple(2 * var_types)
    fiej__pspw = {'numba': numba, 'bodo': bodo, 'np': np}
    fiej__pspw.update(thti__mwmn)
    f_ir = compile_to_numba_ir(cio__ojwo, fiej__pspw, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    ceu__yilz = pm.typemap[block.body[-1].value.name]
    cpybx__span = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        ceu__yilz, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    iqok__kek = numba.core.target_extension.dispatcher_registry[cpu_target](
        cio__ojwo)
    iqok__kek.add_overload(cpybx__span)
    return iqok__kek


def _match_reduce_def(var_def, f_ir, ind):
    xiy__wyld = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        xiy__wyld = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        mvv__wigdr = guard(find_callname, f_ir, var_def)
        if mvv__wigdr == ('min', 'builtins'):
            xiy__wyld = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if mvv__wigdr == ('max', 'builtins'):
            xiy__wyld = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return xiy__wyld


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    jtn__yaux = len(redvars)
    ggq__wru = 1
    in_vars = []
    for bxz__yzo in range(ggq__wru):
        znrqy__zslo = ir.Var(arr_var.scope, f'$input{bxz__yzo}', arr_var.loc)
        in_vars.append(znrqy__zslo)
    gym__xrla = parfor.loop_nests[0].index_variable
    auk__wim = [0] * jtn__yaux
    for duiah__elzog in parfor.loop_body.values():
        okv__ude = []
        for fbx__xwhu in duiah__elzog.body:
            if is_var_assign(fbx__xwhu
                ) and fbx__xwhu.value.name == gym__xrla.name:
                continue
            if is_getitem(fbx__xwhu
                ) and fbx__xwhu.value.value.name == arr_var.name:
                fbx__xwhu.value = in_vars[0]
            if is_call_assign(fbx__xwhu) and guard(find_callname, pm.
                func_ir, fbx__xwhu.value) == ('isna', 'bodo.libs.array_kernels'
                ) and fbx__xwhu.value.args[0].name == arr_var.name:
                fbx__xwhu.value = ir.Const(False, fbx__xwhu.target.loc)
            if is_assign(fbx__xwhu) and fbx__xwhu.target.name in redvars:
                ind = redvars.index(fbx__xwhu.target.name)
                auk__wim[ind] = fbx__xwhu.target
            okv__ude.append(fbx__xwhu)
        duiah__elzog.body = okv__ude
    pdbts__kzskl = ['v{}'.format(bxz__yzo) for bxz__yzo in range(jtn__yaux)]
    way__xfcyw = ['in{}'.format(bxz__yzo) for bxz__yzo in range(ggq__wru)]
    xiy__wyld = 'def agg_update({}):\n'.format(', '.join(pdbts__kzskl +
        way__xfcyw))
    xiy__wyld += '    __update_redvars()\n'
    xiy__wyld += '    return {}'.format(', '.join(['v{}'.format(bxz__yzo) for
        bxz__yzo in range(jtn__yaux)]))
    oct__pdbc = {}
    exec(xiy__wyld, {}, oct__pdbc)
    vwikw__huc = oct__pdbc['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * ggq__wru)
    f_ir = compile_to_numba_ir(vwikw__huc, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    jrgau__mogyj = f_ir.blocks.popitem()[1].body
    ceu__yilz = pm.typemap[jrgau__mogyj[-1].value.name]
    xdm__ygbl = wrap_parfor_blocks(parfor)
    pytux__qlblq = find_topo_order(xdm__ygbl)
    pytux__qlblq = pytux__qlblq[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    jme__zis = f_ir.blocks[pytux__qlblq[0]]
    koy__xmdlx = f_ir.blocks[pytux__qlblq[-1]]
    ydns__hier = jrgau__mogyj[:jtn__yaux + ggq__wru]
    if jtn__yaux > 1:
        guoy__xgxe = jrgau__mogyj[-3:]
        assert is_assign(guoy__xgxe[0]) and isinstance(guoy__xgxe[0].value,
            ir.Expr) and guoy__xgxe[0].value.op == 'build_tuple'
    else:
        guoy__xgxe = jrgau__mogyj[-2:]
    for bxz__yzo in range(jtn__yaux):
        oprl__oea = jrgau__mogyj[bxz__yzo].target
        nbc__vtho = ir.Assign(oprl__oea, auk__wim[bxz__yzo], oprl__oea.loc)
        ydns__hier.append(nbc__vtho)
    for bxz__yzo in range(jtn__yaux, jtn__yaux + ggq__wru):
        oprl__oea = jrgau__mogyj[bxz__yzo].target
        nbc__vtho = ir.Assign(oprl__oea, in_vars[bxz__yzo - jtn__yaux],
            oprl__oea.loc)
        ydns__hier.append(nbc__vtho)
    jme__zis.body = ydns__hier + jme__zis.body
    fvp__pntfy = []
    for bxz__yzo in range(jtn__yaux):
        oprl__oea = jrgau__mogyj[bxz__yzo].target
        nbc__vtho = ir.Assign(auk__wim[bxz__yzo], oprl__oea, oprl__oea.loc)
        fvp__pntfy.append(nbc__vtho)
    koy__xmdlx.body += fvp__pntfy + guoy__xgxe
    rxkoe__fzs = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        ceu__yilz, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    iqok__kek = numba.core.target_extension.dispatcher_registry[cpu_target](
        vwikw__huc)
    iqok__kek.add_overload(rxkoe__fzs)
    return iqok__kek


def _rm_arg_agg_block(block, typemap):
    mmh__mjfx = []
    arr_var = None
    for bxz__yzo, fbx__xwhu in enumerate(block.body):
        if is_assign(fbx__xwhu) and isinstance(fbx__xwhu.value, ir.Arg):
            arr_var = fbx__xwhu.target
            qao__uhap = typemap[arr_var.name]
            if not isinstance(qao__uhap, types.ArrayCompatible):
                mmh__mjfx += block.body[bxz__yzo + 1:]
                break
            fzcsd__vnwi = block.body[bxz__yzo + 1]
            assert is_assign(fzcsd__vnwi) and isinstance(fzcsd__vnwi.value,
                ir.Expr
                ) and fzcsd__vnwi.value.op == 'getattr' and fzcsd__vnwi.value.attr == 'shape' and fzcsd__vnwi.value.value.name == arr_var.name
            zelz__zyuc = fzcsd__vnwi.target
            nkp__tvhaf = block.body[bxz__yzo + 2]
            assert is_assign(nkp__tvhaf) and isinstance(nkp__tvhaf.value,
                ir.Expr
                ) and nkp__tvhaf.value.op == 'static_getitem' and nkp__tvhaf.value.value.name == zelz__zyuc.name
            mmh__mjfx += block.body[bxz__yzo + 3:]
            break
        mmh__mjfx.append(fbx__xwhu)
    return mmh__mjfx, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    xdm__ygbl = wrap_parfor_blocks(parfor)
    pytux__qlblq = find_topo_order(xdm__ygbl)
    pytux__qlblq = pytux__qlblq[1:]
    unwrap_parfor_blocks(parfor)
    for mjek__bkmav in reversed(pytux__qlblq):
        for fbx__xwhu in reversed(parfor.loop_body[mjek__bkmav].body):
            if isinstance(fbx__xwhu, ir.Assign) and (fbx__xwhu.target.name in
                parfor_params or fbx__xwhu.target.name in var_to_param):
                nalcl__yxryd = fbx__xwhu.target.name
                rhs = fbx__xwhu.value
                ssl__exrjv = (nalcl__yxryd if nalcl__yxryd in parfor_params
                     else var_to_param[nalcl__yxryd])
                eihop__mlhk = []
                if isinstance(rhs, ir.Var):
                    eihop__mlhk = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    eihop__mlhk = [caqxo__asdrc.name for caqxo__asdrc in
                        fbx__xwhu.value.list_vars()]
                param_uses[ssl__exrjv].extend(eihop__mlhk)
                for caqxo__asdrc in eihop__mlhk:
                    var_to_param[caqxo__asdrc] = ssl__exrjv
            if isinstance(fbx__xwhu, Parfor):
                get_parfor_reductions(fbx__xwhu, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for oioms__wbwg, eihop__mlhk in param_uses.items():
        if oioms__wbwg in eihop__mlhk and oioms__wbwg not in reduce_varnames:
            reduce_varnames.append(oioms__wbwg)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
