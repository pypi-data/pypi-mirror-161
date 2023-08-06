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
        mwf__srdhy = func.signature
        if mwf__srdhy == types.none(types.voidptr):
            sqocv__lrzd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            xvoxs__nxslp = cgutils.get_or_insert_function(builder.module,
                sqocv__lrzd, sym._literal_value)
            builder.call(xvoxs__nxslp, [context.get_constant_null(
                mwf__srdhy.args[0])])
        elif mwf__srdhy == types.none(types.int64, types.voidptr, types.voidptr
            ):
            sqocv__lrzd = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            xvoxs__nxslp = cgutils.get_or_insert_function(builder.module,
                sqocv__lrzd, sym._literal_value)
            builder.call(xvoxs__nxslp, [context.get_constant(types.int64, 0
                ), context.get_constant_null(mwf__srdhy.args[1]), context.
                get_constant_null(mwf__srdhy.args[2])])
        else:
            sqocv__lrzd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            xvoxs__nxslp = cgutils.get_or_insert_function(builder.module,
                sqocv__lrzd, sym._literal_value)
            builder.call(xvoxs__nxslp, [context.get_constant_null(
                mwf__srdhy.args[0]), context.get_constant_null(mwf__srdhy.
                args[1]), context.get_constant_null(mwf__srdhy.args[2])])
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
        ftagx__fxc = True
        whjc__iabaw = 1
        umz__jbqab = -1
        if isinstance(rhs, ir.Expr):
            for vrfi__cti in rhs.kws:
                if func_name in list_cumulative:
                    if vrfi__cti[0] == 'skipna':
                        ftagx__fxc = guard(find_const, func_ir, vrfi__cti[1])
                        if not isinstance(ftagx__fxc, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if vrfi__cti[0] == 'dropna':
                        ftagx__fxc = guard(find_const, func_ir, vrfi__cti[1])
                        if not isinstance(ftagx__fxc, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            whjc__iabaw = get_call_expr_arg('shift', rhs.args, dict(rhs.kws
                ), 0, 'periods', whjc__iabaw)
            whjc__iabaw = guard(find_const, func_ir, whjc__iabaw)
        if func_name == 'head':
            umz__jbqab = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(umz__jbqab, int):
                umz__jbqab = guard(find_const, func_ir, umz__jbqab)
            if umz__jbqab < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = ftagx__fxc
        func.periods = whjc__iabaw
        func.head_n = umz__jbqab
        if func_name == 'transform':
            kws = dict(rhs.kws)
            uxhwm__oprde = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            kipgr__veelw = typemap[uxhwm__oprde.name]
            ufo__xbj = None
            if isinstance(kipgr__veelw, str):
                ufo__xbj = kipgr__veelw
            elif is_overload_constant_str(kipgr__veelw):
                ufo__xbj = get_overload_const_str(kipgr__veelw)
            elif bodo.utils.typing.is_builtin_function(kipgr__veelw):
                ufo__xbj = bodo.utils.typing.get_builtin_function_name(
                    kipgr__veelw)
            if ufo__xbj not in bodo.ir.aggregate.supported_transform_funcs[:]:
                raise BodoError(f'unsupported transform function {ufo__xbj}')
            func.transform_func = supported_agg_funcs.index(ufo__xbj)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    uxhwm__oprde = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if uxhwm__oprde == '':
        kipgr__veelw = types.none
    else:
        kipgr__veelw = typemap[uxhwm__oprde.name]
    if is_overload_constant_dict(kipgr__veelw):
        tjy__xnihi = get_overload_constant_dict(kipgr__veelw)
        hmn__qvv = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in tjy__xnihi.values()]
        return hmn__qvv
    if kipgr__veelw == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(kipgr__veelw, types.BaseTuple) or is_overload_constant_list(
        kipgr__veelw):
        hmn__qvv = []
        qqyns__eix = 0
        if is_overload_constant_list(kipgr__veelw):
            jpp__rlfw = get_overload_const_list(kipgr__veelw)
        else:
            jpp__rlfw = kipgr__veelw.types
        for t in jpp__rlfw:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                hmn__qvv.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(jpp__rlfw) > 1:
                    func.fname = '<lambda_' + str(qqyns__eix) + '>'
                    qqyns__eix += 1
                hmn__qvv.append(func)
        return [hmn__qvv]
    if is_overload_constant_str(kipgr__veelw):
        func_name = get_overload_const_str(kipgr__veelw)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(kipgr__veelw):
        func_name = bodo.utils.typing.get_builtin_function_name(kipgr__veelw)
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
        qqyns__eix = 0
        wjdq__hpx = []
        for fhjyi__gamf in f_val:
            func = get_agg_func_udf(func_ir, fhjyi__gamf, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{qqyns__eix}>'
                qqyns__eix += 1
            wjdq__hpx.append(func)
        return wjdq__hpx
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
    ufo__xbj = code.co_name
    return ufo__xbj


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
            qet__thzr = types.DType(args[0])
            return signature(qet__thzr, *args)


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
        return [iudj__lxrum for iudj__lxrum in self.in_vars if iudj__lxrum
             is not None]

    def get_live_out_vars(self):
        return [iudj__lxrum for iudj__lxrum in self.out_vars if iudj__lxrum
             is not None]

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
        iten__ovdun = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        kukd__ambqj = list(get_index_data_arr_types(self.out_type.index))
        return iten__ovdun + kukd__ambqj

    def update_dead_col_info(self):
        for xrxpw__szgal in self.dead_out_inds:
            self.gb_info_out.pop(xrxpw__szgal, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for coo__lwuet, mqoe__xzzks in self.gb_info_in.copy().items():
            rojs__tddj = []
            for fhjyi__gamf, zttyk__flm in mqoe__xzzks:
                if zttyk__flm not in self.dead_out_inds:
                    rojs__tddj.append((fhjyi__gamf, zttyk__flm))
            if not rojs__tddj:
                if (coo__lwuet is not None and coo__lwuet not in self.
                    in_key_inds):
                    self.dead_in_inds.add(coo__lwuet)
                self.gb_info_in.pop(coo__lwuet)
            else:
                self.gb_info_in[coo__lwuet] = rojs__tddj
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for kzcz__eojt in range(1, len(self.in_vars)):
                xrxpw__szgal = self.n_in_table_arrays + kzcz__eojt - 1
                if xrxpw__szgal in self.dead_in_inds:
                    self.in_vars[kzcz__eojt] = None
        else:
            for kzcz__eojt in range(len(self.in_vars)):
                if kzcz__eojt in self.dead_in_inds:
                    self.in_vars[kzcz__eojt] = None

    def __repr__(self):
        yge__gnlpp = ', '.join(iudj__lxrum.name for iudj__lxrum in self.
            get_live_in_vars())
        jwupa__cublv = f'{self.df_in}{{{yge__gnlpp}}}'
        clz__coi = ', '.join(iudj__lxrum.name for iudj__lxrum in self.
            get_live_out_vars())
        efql__qubu = f'{self.df_out}{{{clz__coi}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {jwupa__cublv} {efql__qubu}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({iudj__lxrum.name for iudj__lxrum in aggregate_node.
        get_live_in_vars()})
    def_set.update({iudj__lxrum.name for iudj__lxrum in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    aaww__dci = agg_node.out_vars[0]
    if aaww__dci is not None and aaww__dci.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            jvttv__jaf = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(jvttv__jaf)
        else:
            agg_node.dead_out_inds.add(0)
    for kzcz__eojt in range(1, len(agg_node.out_vars)):
        iudj__lxrum = agg_node.out_vars[kzcz__eojt]
        if iudj__lxrum is not None and iudj__lxrum.name not in lives:
            agg_node.out_vars[kzcz__eojt] = None
            xrxpw__szgal = agg_node.n_out_table_arrays + kzcz__eojt - 1
            agg_node.dead_out_inds.add(xrxpw__szgal)
    if all(iudj__lxrum is None for iudj__lxrum in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    noc__bmuu = {iudj__lxrum.name for iudj__lxrum in aggregate_node.
        get_live_out_vars()}
    return set(), noc__bmuu


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for kzcz__eojt in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[kzcz__eojt] is not None:
            aggregate_node.in_vars[kzcz__eojt] = replace_vars_inner(
                aggregate_node.in_vars[kzcz__eojt], var_dict)
    for kzcz__eojt in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[kzcz__eojt] is not None:
            aggregate_node.out_vars[kzcz__eojt] = replace_vars_inner(
                aggregate_node.out_vars[kzcz__eojt], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for kzcz__eojt in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[kzcz__eojt] is not None:
            aggregate_node.in_vars[kzcz__eojt] = visit_vars_inner(
                aggregate_node.in_vars[kzcz__eojt], callback, cbdata)
    for kzcz__eojt in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[kzcz__eojt] is not None:
            aggregate_node.out_vars[kzcz__eojt] = visit_vars_inner(
                aggregate_node.out_vars[kzcz__eojt], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    mgyy__vtqp = []
    for yivo__jlqll in aggregate_node.get_live_in_vars():
        yks__nsq = equiv_set.get_shape(yivo__jlqll)
        if yks__nsq is not None:
            mgyy__vtqp.append(yks__nsq[0])
    if len(mgyy__vtqp) > 1:
        equiv_set.insert_equiv(*mgyy__vtqp)
    lulv__cvb = []
    mgyy__vtqp = []
    for yivo__jlqll in aggregate_node.get_live_out_vars():
        hdlhl__qcbos = typemap[yivo__jlqll.name]
        qgn__rjg = array_analysis._gen_shape_call(equiv_set, yivo__jlqll,
            hdlhl__qcbos.ndim, None, lulv__cvb)
        equiv_set.insert_equiv(yivo__jlqll, qgn__rjg)
        mgyy__vtqp.append(qgn__rjg[0])
        equiv_set.define(yivo__jlqll, set())
    if len(mgyy__vtqp) > 1:
        equiv_set.insert_equiv(*mgyy__vtqp)
    return [], lulv__cvb


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    kzfb__kstou = aggregate_node.get_live_in_vars()
    nosgx__hfe = aggregate_node.get_live_out_vars()
    bcmw__afrug = Distribution.OneD
    for yivo__jlqll in kzfb__kstou:
        bcmw__afrug = Distribution(min(bcmw__afrug.value, array_dists[
            yivo__jlqll.name].value))
    xvxyw__mlf = Distribution(min(bcmw__afrug.value, Distribution.OneD_Var.
        value))
    for yivo__jlqll in nosgx__hfe:
        if yivo__jlqll.name in array_dists:
            xvxyw__mlf = Distribution(min(xvxyw__mlf.value, array_dists[
                yivo__jlqll.name].value))
    if xvxyw__mlf != Distribution.OneD_Var:
        bcmw__afrug = xvxyw__mlf
    for yivo__jlqll in kzfb__kstou:
        array_dists[yivo__jlqll.name] = bcmw__afrug
    for yivo__jlqll in nosgx__hfe:
        array_dists[yivo__jlqll.name] = xvxyw__mlf


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for yivo__jlqll in agg_node.get_live_out_vars():
        definitions[yivo__jlqll.name].append(agg_node)
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
    ulrvo__amf = agg_node.get_live_in_vars()
    guqew__bxo = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for iudj__lxrum in (ulrvo__amf + guqew__bxo):
            if array_dists[iudj__lxrum.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                iudj__lxrum.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    hmn__qvv = []
    func_out_types = []
    for zttyk__flm, (coo__lwuet, func) in agg_node.gb_info_out.items():
        if coo__lwuet is not None:
            t = agg_node.in_col_types[coo__lwuet]
            in_col_typs.append(t)
        hmn__qvv.append(func)
        func_out_types.append(out_col_typs[zttyk__flm])
    ocwwl__qyiti = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for kzcz__eojt, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            ocwwl__qyiti.update({f'in_cat_dtype_{kzcz__eojt}': in_col_typ})
    for kzcz__eojt, dgak__sallc in enumerate(out_col_typs):
        if isinstance(dgak__sallc, bodo.CategoricalArrayType):
            ocwwl__qyiti.update({f'out_cat_dtype_{kzcz__eojt}': dgak__sallc})
    udf_func_struct = get_udf_func_struct(hmn__qvv, in_col_typs, typingctx,
        targetctx)
    out_var_types = [(typemap[iudj__lxrum.name] if iudj__lxrum is not None else
        types.none) for iudj__lxrum in agg_node.out_vars]
    qcprb__jgfhe, aivn__tze = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    ocwwl__qyiti.update(aivn__tze)
    ocwwl__qyiti.update({'pd': pd, 'pre_alloc_string_array':
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
            ocwwl__qyiti.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            ocwwl__qyiti.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, {}, ldwoi__dmd)
    gwd__hylpm = ldwoi__dmd['agg_top']
    mby__dwd = compile_to_numba_ir(gwd__hylpm, ocwwl__qyiti, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[iudj__lxrum.
        name] for iudj__lxrum in ulrvo__amf), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(mby__dwd, ulrvo__amf)
    zjn__zwxtg = mby__dwd.body[-2].value.value
    psczd__dpabw = mby__dwd.body[:-2]
    for kzcz__eojt, iudj__lxrum in enumerate(guqew__bxo):
        gen_getitem(iudj__lxrum, zjn__zwxtg, kzcz__eojt, calltypes,
            psczd__dpabw)
    return psczd__dpabw


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        rdn__ujay = IntDtype(t.dtype).name
        assert rdn__ujay.endswith('Dtype()')
        rdn__ujay = rdn__ujay[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{rdn__ujay}'))"
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
        bbjtg__ektg = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {bbjtg__ektg}_cat_dtype_{colnum})'
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
    lghbc__poz = udf_func_struct.var_typs
    femf__ljlju = len(lghbc__poz)
    qcprb__jgfhe = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    qcprb__jgfhe += '    if is_null_pointer(in_table):\n'
    qcprb__jgfhe += '        return\n'
    qcprb__jgfhe += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lghbc__poz]), 
        ',' if len(lghbc__poz) == 1 else '')
    wiijh__tpri = n_keys
    amqy__qyyi = []
    redvar_offsets = []
    jfi__ohfn = []
    if do_combine:
        for kzcz__eojt, fhjyi__gamf in enumerate(allfuncs):
            if fhjyi__gamf.ftype != 'udf':
                wiijh__tpri += fhjyi__gamf.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(wiijh__tpri, wiijh__tpri +
                    fhjyi__gamf.n_redvars))
                wiijh__tpri += fhjyi__gamf.n_redvars
                jfi__ohfn.append(data_in_typs_[func_idx_to_in_col[kzcz__eojt]])
                amqy__qyyi.append(func_idx_to_in_col[kzcz__eojt] + n_keys)
    else:
        for kzcz__eojt, fhjyi__gamf in enumerate(allfuncs):
            if fhjyi__gamf.ftype != 'udf':
                wiijh__tpri += fhjyi__gamf.ncols_post_shuffle
            else:
                redvar_offsets += list(range(wiijh__tpri + 1, wiijh__tpri +
                    1 + fhjyi__gamf.n_redvars))
                wiijh__tpri += fhjyi__gamf.n_redvars + 1
                jfi__ohfn.append(data_in_typs_[func_idx_to_in_col[kzcz__eojt]])
                amqy__qyyi.append(func_idx_to_in_col[kzcz__eojt] + n_keys)
    assert len(redvar_offsets) == femf__ljlju
    fydvf__ykuy = len(jfi__ohfn)
    wbk__spb = []
    for kzcz__eojt, t in enumerate(jfi__ohfn):
        wbk__spb.append(_gen_dummy_alloc(t, kzcz__eojt, True))
    qcprb__jgfhe += '    data_in_dummy = ({}{})\n'.format(','.join(wbk__spb
        ), ',' if len(jfi__ohfn) == 1 else '')
    qcprb__jgfhe += """
    # initialize redvar cols
"""
    qcprb__jgfhe += '    init_vals = __init_func()\n'
    for kzcz__eojt in range(femf__ljlju):
        qcprb__jgfhe += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(kzcz__eojt, redvar_offsets[kzcz__eojt], kzcz__eojt))
        qcprb__jgfhe += '    incref(redvar_arr_{})\n'.format(kzcz__eojt)
        qcprb__jgfhe += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            kzcz__eojt, kzcz__eojt)
    qcprb__jgfhe += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(kzcz__eojt) for kzcz__eojt in range(
        femf__ljlju)]), ',' if femf__ljlju == 1 else '')
    qcprb__jgfhe += '\n'
    for kzcz__eojt in range(fydvf__ykuy):
        qcprb__jgfhe += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(kzcz__eojt, amqy__qyyi[kzcz__eojt], kzcz__eojt))
        qcprb__jgfhe += '    incref(data_in_{})\n'.format(kzcz__eojt)
    qcprb__jgfhe += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(kzcz__eojt) for kzcz__eojt in range(fydvf__ykuy)]), ',' if 
        fydvf__ykuy == 1 else '')
    qcprb__jgfhe += '\n'
    qcprb__jgfhe += '    for i in range(len(data_in_0)):\n'
    qcprb__jgfhe += '        w_ind = row_to_group[i]\n'
    qcprb__jgfhe += '        if w_ind != -1:\n'
    qcprb__jgfhe += (
        '            __update_redvars(redvars, data_in, w_ind, i)\n')
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, ldwoi__dmd)
    return ldwoi__dmd['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    lghbc__poz = udf_func_struct.var_typs
    femf__ljlju = len(lghbc__poz)
    qcprb__jgfhe = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    qcprb__jgfhe += '    if is_null_pointer(in_table):\n'
    qcprb__jgfhe += '        return\n'
    qcprb__jgfhe += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lghbc__poz]), 
        ',' if len(lghbc__poz) == 1 else '')
    cdmg__liht = n_keys
    scxit__tgs = n_keys
    mgze__htzok = []
    phyxx__enrm = []
    for fhjyi__gamf in allfuncs:
        if fhjyi__gamf.ftype != 'udf':
            cdmg__liht += fhjyi__gamf.ncols_pre_shuffle
            scxit__tgs += fhjyi__gamf.ncols_post_shuffle
        else:
            mgze__htzok += list(range(cdmg__liht, cdmg__liht + fhjyi__gamf.
                n_redvars))
            phyxx__enrm += list(range(scxit__tgs + 1, scxit__tgs + 1 +
                fhjyi__gamf.n_redvars))
            cdmg__liht += fhjyi__gamf.n_redvars
            scxit__tgs += 1 + fhjyi__gamf.n_redvars
    assert len(mgze__htzok) == femf__ljlju
    qcprb__jgfhe += """
    # initialize redvar cols
"""
    qcprb__jgfhe += '    init_vals = __init_func()\n'
    for kzcz__eojt in range(femf__ljlju):
        qcprb__jgfhe += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(kzcz__eojt, phyxx__enrm[kzcz__eojt], kzcz__eojt))
        qcprb__jgfhe += '    incref(redvar_arr_{})\n'.format(kzcz__eojt)
        qcprb__jgfhe += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            kzcz__eojt, kzcz__eojt)
    qcprb__jgfhe += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(kzcz__eojt) for kzcz__eojt in range(
        femf__ljlju)]), ',' if femf__ljlju == 1 else '')
    qcprb__jgfhe += '\n'
    for kzcz__eojt in range(femf__ljlju):
        qcprb__jgfhe += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(kzcz__eojt, mgze__htzok[kzcz__eojt], kzcz__eojt))
        qcprb__jgfhe += '    incref(recv_redvar_arr_{})\n'.format(kzcz__eojt)
    qcprb__jgfhe += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(kzcz__eojt) for kzcz__eojt in range(
        femf__ljlju)]), ',' if femf__ljlju == 1 else '')
    qcprb__jgfhe += '\n'
    if femf__ljlju:
        qcprb__jgfhe += '    for i in range(len(recv_redvar_arr_0)):\n'
        qcprb__jgfhe += '        w_ind = row_to_group[i]\n'
        qcprb__jgfhe += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, ldwoi__dmd)
    return ldwoi__dmd['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    lghbc__poz = udf_func_struct.var_typs
    femf__ljlju = len(lghbc__poz)
    wiijh__tpri = n_keys
    redvar_offsets = []
    kxyz__qtct = []
    ptzbz__xzn = []
    for kzcz__eojt, fhjyi__gamf in enumerate(allfuncs):
        if fhjyi__gamf.ftype != 'udf':
            wiijh__tpri += fhjyi__gamf.ncols_post_shuffle
        else:
            kxyz__qtct.append(wiijh__tpri)
            redvar_offsets += list(range(wiijh__tpri + 1, wiijh__tpri + 1 +
                fhjyi__gamf.n_redvars))
            wiijh__tpri += 1 + fhjyi__gamf.n_redvars
            ptzbz__xzn.append(out_data_typs_[kzcz__eojt])
    assert len(redvar_offsets) == femf__ljlju
    fydvf__ykuy = len(ptzbz__xzn)
    qcprb__jgfhe = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    qcprb__jgfhe += '    if is_null_pointer(table):\n'
    qcprb__jgfhe += '        return\n'
    qcprb__jgfhe += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lghbc__poz]), 
        ',' if len(lghbc__poz) == 1 else '')
    qcprb__jgfhe += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        ptzbz__xzn]), ',' if len(ptzbz__xzn) == 1 else '')
    for kzcz__eojt in range(femf__ljlju):
        qcprb__jgfhe += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(kzcz__eojt, redvar_offsets[kzcz__eojt], kzcz__eojt))
        qcprb__jgfhe += '    incref(redvar_arr_{})\n'.format(kzcz__eojt)
    qcprb__jgfhe += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(kzcz__eojt) for kzcz__eojt in range(
        femf__ljlju)]), ',' if femf__ljlju == 1 else '')
    qcprb__jgfhe += '\n'
    for kzcz__eojt in range(fydvf__ykuy):
        qcprb__jgfhe += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(kzcz__eojt, kxyz__qtct[kzcz__eojt], kzcz__eojt))
        qcprb__jgfhe += '    incref(data_out_{})\n'.format(kzcz__eojt)
    qcprb__jgfhe += '    data_out = ({}{})\n'.format(','.join([
        'data_out_{}'.format(kzcz__eojt) for kzcz__eojt in range(
        fydvf__ykuy)]), ',' if fydvf__ykuy == 1 else '')
    qcprb__jgfhe += '\n'
    qcprb__jgfhe += '    for i in range(len(data_out_0)):\n'
    qcprb__jgfhe += '        __eval_res(redvars, data_out, i)\n'
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, ldwoi__dmd)
    return ldwoi__dmd['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    wiijh__tpri = n_keys
    gpet__uecn = []
    for kzcz__eojt, fhjyi__gamf in enumerate(allfuncs):
        if fhjyi__gamf.ftype == 'gen_udf':
            gpet__uecn.append(wiijh__tpri)
            wiijh__tpri += 1
        elif fhjyi__gamf.ftype != 'udf':
            wiijh__tpri += fhjyi__gamf.ncols_post_shuffle
        else:
            wiijh__tpri += fhjyi__gamf.n_redvars + 1
    qcprb__jgfhe = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    qcprb__jgfhe += '    if num_groups == 0:\n'
    qcprb__jgfhe += '        return\n'
    for kzcz__eojt, func in enumerate(udf_func_struct.general_udf_funcs):
        qcprb__jgfhe += '    # col {}\n'.format(kzcz__eojt)
        qcprb__jgfhe += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(gpet__uecn[kzcz__eojt], kzcz__eojt))
        qcprb__jgfhe += '    incref(out_col)\n'
        qcprb__jgfhe += '    for j in range(num_groups):\n'
        qcprb__jgfhe += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(kzcz__eojt, kzcz__eojt))
        qcprb__jgfhe += '        incref(in_col)\n'
        qcprb__jgfhe += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(kzcz__eojt))
    ocwwl__qyiti = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    ynf__brkk = 0
    for kzcz__eojt, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[ynf__brkk]
        ocwwl__qyiti['func_{}'.format(ynf__brkk)] = func
        ocwwl__qyiti['in_col_{}_typ'.format(ynf__brkk)] = in_col_typs[
            func_idx_to_in_col[kzcz__eojt]]
        ocwwl__qyiti['out_col_{}_typ'.format(ynf__brkk)] = out_col_typs[
            kzcz__eojt]
        ynf__brkk += 1
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, ocwwl__qyiti, ldwoi__dmd)
    fhjyi__gamf = ldwoi__dmd['bodo_gb_apply_general_udfs{}'.format(
        label_suffix)]
    bsn__enrrf = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(bsn__enrrf, nopython=True)(fhjyi__gamf)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    rvvps__mfs = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        qtf__yyz = []
        if agg_node.in_vars[0] is not None:
            qtf__yyz.append('arg0')
        for kzcz__eojt in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if kzcz__eojt not in agg_node.dead_in_inds:
                qtf__yyz.append(f'arg{kzcz__eojt}')
    else:
        qtf__yyz = [f'arg{kzcz__eojt}' for kzcz__eojt, iudj__lxrum in
            enumerate(agg_node.in_vars) if iudj__lxrum is not None]
    qcprb__jgfhe = f"def agg_top({', '.join(qtf__yyz)}):\n"
    bmb__czth = []
    if agg_node.is_in_table_format:
        bmb__czth = agg_node.in_key_inds + [coo__lwuet for coo__lwuet,
            mhc__xkp in agg_node.gb_info_out.values() if coo__lwuet is not None
            ]
        if agg_node.input_has_index:
            bmb__czth.append(agg_node.n_in_cols - 1)
        ugww__bwpw = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        bkev__spqt = []
        for kzcz__eojt in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if kzcz__eojt in agg_node.dead_in_inds:
                bkev__spqt.append('None')
            else:
                bkev__spqt.append(f'arg{kzcz__eojt}')
        xvi__qor = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        qcprb__jgfhe += f"""    table = py_data_to_cpp_table({xvi__qor}, ({', '.join(bkev__spqt)}{ugww__bwpw}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        lxmp__uuozg = [f'arg{kzcz__eojt}' for kzcz__eojt in agg_node.
            in_key_inds]
        hhf__zgrcn = [f'arg{coo__lwuet}' for coo__lwuet, mhc__xkp in
            agg_node.gb_info_out.values() if coo__lwuet is not None]
        opumo__frnv = lxmp__uuozg + hhf__zgrcn
        if agg_node.input_has_index:
            opumo__frnv.append(f'arg{len(agg_node.in_vars) - 1}')
        qcprb__jgfhe += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({cxn__nssa})' for cxn__nssa in opumo__frnv))
        qcprb__jgfhe += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    gmn__ddc = []
    func_idx_to_in_col = []
    ovlh__eiwx = []
    ftagx__fxc = False
    zxtlz__ljq = 1
    umz__jbqab = -1
    olflz__ussic = 0
    phz__syu = 0
    hmn__qvv = [func for mhc__xkp, func in agg_node.gb_info_out.values()]
    for mwh__jmj, func in enumerate(hmn__qvv):
        gmn__ddc.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            olflz__ussic += 1
        if hasattr(func, 'skipdropna'):
            ftagx__fxc = func.skipdropna
        if func.ftype == 'shift':
            zxtlz__ljq = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            phz__syu = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            umz__jbqab = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(mwh__jmj)
        if func.ftype == 'udf':
            ovlh__eiwx.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            ovlh__eiwx.append(0)
            do_combine = False
    gmn__ddc.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if olflz__ussic > 0:
        if olflz__ussic != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    gvuy__mryv = []
    if udf_func_struct is not None:
        yjws__jmou = next_label()
        if udf_func_struct.regular_udfs:
            bsn__enrrf = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            jzr__aogq = numba.cfunc(bsn__enrrf, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs, do_combine,
                func_idx_to_in_col, yjws__jmou))
            mjbv__vxouh = numba.cfunc(bsn__enrrf, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, yjws__jmou))
            ydwj__pnea = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys,
                func_out_types, yjws__jmou))
            udf_func_struct.set_regular_cfuncs(jzr__aogq, mjbv__vxouh,
                ydwj__pnea)
            for ewe__dilya in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[ewe__dilya.native_name] = ewe__dilya
                gb_agg_cfunc_addr[ewe__dilya.native_name] = ewe__dilya.address
        if udf_func_struct.general_udfs:
            msg__dfe = gen_general_udf_cb(udf_func_struct, allfuncs, n_keys,
                in_col_typs, func_out_types, func_idx_to_in_col, yjws__jmou)
            udf_func_struct.set_general_cfunc(msg__dfe)
        lghbc__poz = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        jwtm__jnuio = 0
        kzcz__eojt = 0
        for pui__hflc, fhjyi__gamf in zip(agg_node.gb_info_out.keys(), allfuncs
            ):
            if fhjyi__gamf.ftype in ('udf', 'gen_udf'):
                gvuy__mryv.append(out_col_typs[pui__hflc])
                for vqyz__paz in range(jwtm__jnuio, jwtm__jnuio +
                    ovlh__eiwx[kzcz__eojt]):
                    gvuy__mryv.append(dtype_to_array_type(lghbc__poz[
                        vqyz__paz]))
                jwtm__jnuio += ovlh__eiwx[kzcz__eojt]
                kzcz__eojt += 1
        qcprb__jgfhe += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{kzcz__eojt}' for kzcz__eojt in range(len(gvuy__mryv)))}{',' if len(gvuy__mryv) == 1 else ''}))
"""
        qcprb__jgfhe += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(gvuy__mryv)})
"""
        if udf_func_struct.regular_udfs:
            qcprb__jgfhe += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{jzr__aogq.native_name}')\n"
                )
            qcprb__jgfhe += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{mjbv__vxouh.native_name}')\n"
                )
            qcprb__jgfhe += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{ydwj__pnea.native_name}')\n"
                )
            qcprb__jgfhe += f"""    cpp_cb_update_addr = get_agg_udf_addr('{jzr__aogq.native_name}')
"""
            qcprb__jgfhe += f"""    cpp_cb_combine_addr = get_agg_udf_addr('{mjbv__vxouh.native_name}')
"""
            qcprb__jgfhe += (
                f"    cpp_cb_eval_addr = get_agg_udf_addr('{ydwj__pnea.native_name}')\n"
                )
        else:
            qcprb__jgfhe += '    cpp_cb_update_addr = 0\n'
            qcprb__jgfhe += '    cpp_cb_combine_addr = 0\n'
            qcprb__jgfhe += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            ewe__dilya = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[ewe__dilya.native_name] = ewe__dilya
            gb_agg_cfunc_addr[ewe__dilya.native_name] = ewe__dilya.address
            qcprb__jgfhe += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{ewe__dilya.native_name}')\n"
                )
            qcprb__jgfhe += f"""    cpp_cb_general_addr = get_agg_udf_addr('{ewe__dilya.native_name}')
"""
        else:
            qcprb__jgfhe += '    cpp_cb_general_addr = 0\n'
    else:
        qcprb__jgfhe += """    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])
"""
        qcprb__jgfhe += '    cpp_cb_update_addr = 0\n'
        qcprb__jgfhe += '    cpp_cb_combine_addr = 0\n'
        qcprb__jgfhe += '    cpp_cb_eval_addr = 0\n'
        qcprb__jgfhe += '    cpp_cb_general_addr = 0\n'
    qcprb__jgfhe += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(
        ', '.join([str(supported_agg_funcs.index(fhjyi__gamf.ftype)) for
        fhjyi__gamf in allfuncs] + ['0']))
    qcprb__jgfhe += (
        f'    func_offsets = np.array({str(gmn__ddc)}, dtype=np.int32)\n')
    if len(ovlh__eiwx) > 0:
        qcprb__jgfhe += (
            f'    udf_ncols = np.array({str(ovlh__eiwx)}, dtype=np.int32)\n')
    else:
        qcprb__jgfhe += '    udf_ncols = np.array([0], np.int32)\n'
    qcprb__jgfhe += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    qcprb__jgfhe += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {ftagx__fxc}, {zxtlz__ljq}, {phz__syu}, {umz__jbqab}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes)
"""
    setax__xthxb = []
    rozt__vkm = 0
    if agg_node.return_key:
        cyffd__bmfyk = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for kzcz__eojt in range(n_keys):
            xrxpw__szgal = cyffd__bmfyk + kzcz__eojt
            setax__xthxb.append(xrxpw__szgal if xrxpw__szgal not in
                agg_node.dead_out_inds else -1)
            rozt__vkm += 1
    for pui__hflc in agg_node.gb_info_out.keys():
        setax__xthxb.append(pui__hflc)
        rozt__vkm += 1
    oojm__bhdi = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            setax__xthxb.append(agg_node.n_out_cols - 1)
        else:
            oojm__bhdi = True
    ugww__bwpw = ',' if rvvps__mfs == 1 else ''
    qldsj__mqebd = (
        f"({', '.join(f'out_type{kzcz__eojt}' for kzcz__eojt in range(rvvps__mfs))}{ugww__bwpw})"
        )
    xipju__qieky = []
    hzgz__qdpp = []
    for kzcz__eojt, t in enumerate(out_col_typs):
        if kzcz__eojt not in agg_node.dead_out_inds and type_has_unknown_cats(t
            ):
            if kzcz__eojt in agg_node.gb_info_out:
                coo__lwuet = agg_node.gb_info_out[kzcz__eojt][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                mhcye__uuy = kzcz__eojt - cyffd__bmfyk
                coo__lwuet = agg_node.in_key_inds[mhcye__uuy]
            hzgz__qdpp.append(kzcz__eojt)
            if (agg_node.is_in_table_format and coo__lwuet < agg_node.
                n_in_table_arrays):
                xipju__qieky.append(f'get_table_data(arg0, {coo__lwuet})')
            else:
                xipju__qieky.append(f'arg{coo__lwuet}')
    ugww__bwpw = ',' if len(xipju__qieky) == 1 else ''
    qcprb__jgfhe += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {qldsj__mqebd}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(xipju__qieky)}{ugww__bwpw}), unknown_cat_out_inds)
"""
    qcprb__jgfhe += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    qcprb__jgfhe += '    delete_table_decref_arrays(table)\n'
    qcprb__jgfhe += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for kzcz__eojt in range(n_keys):
            if setax__xthxb[kzcz__eojt] == -1:
                qcprb__jgfhe += (
                    f'    decref_table_array(out_table, {kzcz__eojt})\n')
    if oojm__bhdi:
        sxy__yqhd = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        qcprb__jgfhe += f'    decref_table_array(out_table, {sxy__yqhd})\n'
    qcprb__jgfhe += '    delete_table(out_table)\n'
    qcprb__jgfhe += '    ev_clean.finalize()\n'
    qcprb__jgfhe += '    return out_data\n'
    rxd__bheid = {f'out_type{kzcz__eojt}': out_var_types[kzcz__eojt] for
        kzcz__eojt in range(rvvps__mfs)}
    rxd__bheid['out_col_inds'] = MetaType(tuple(setax__xthxb))
    rxd__bheid['in_col_inds'] = MetaType(tuple(bmb__czth))
    rxd__bheid['cpp_table_to_py_data'] = cpp_table_to_py_data
    rxd__bheid['py_data_to_cpp_table'] = py_data_to_cpp_table
    rxd__bheid.update({f'udf_type{kzcz__eojt}': t for kzcz__eojt, t in
        enumerate(gvuy__mryv)})
    rxd__bheid['udf_dummy_col_inds'] = MetaType(tuple(range(len(gvuy__mryv))))
    rxd__bheid['create_dummy_table'] = create_dummy_table
    rxd__bheid['unknown_cat_out_inds'] = MetaType(tuple(hzgz__qdpp))
    rxd__bheid['get_table_data'] = bodo.hiframes.table.get_table_data
    return qcprb__jgfhe, rxd__bheid


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    rie__lzipi = tuple(unwrap_typeref(data_types.types[kzcz__eojt]) for
        kzcz__eojt in range(len(data_types.types)))
    qrm__mbwuw = bodo.TableType(rie__lzipi)
    rxd__bheid = {'table_type': qrm__mbwuw}
    qcprb__jgfhe = 'def impl(data_types):\n'
    qcprb__jgfhe += '  py_table = init_table(table_type, False)\n'
    qcprb__jgfhe += '  py_table = set_table_len(py_table, 1)\n'
    for hdlhl__qcbos, jnmb__qqap in qrm__mbwuw.type_to_blk.items():
        rxd__bheid[f'typ_list_{jnmb__qqap}'] = types.List(hdlhl__qcbos)
        rxd__bheid[f'typ_{jnmb__qqap}'] = hdlhl__qcbos
        tmkib__xbuyq = len(qrm__mbwuw.block_to_arr_ind[jnmb__qqap])
        qcprb__jgfhe += f"""  arr_list_{jnmb__qqap} = alloc_list_like(typ_list_{jnmb__qqap}, {tmkib__xbuyq}, False)
"""
        qcprb__jgfhe += f'  for i in range(len(arr_list_{jnmb__qqap})):\n'
        qcprb__jgfhe += (
            f'    arr_list_{jnmb__qqap}[i] = alloc_type(1, typ_{jnmb__qqap}, (-1,))\n'
            )
        qcprb__jgfhe += f"""  py_table = set_table_block(py_table, arr_list_{jnmb__qqap}, {jnmb__qqap})
"""
    qcprb__jgfhe += '  return py_table\n'
    rxd__bheid.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, rxd__bheid, ldwoi__dmd)
    return ldwoi__dmd['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    xjy__dcbi = agg_node.in_vars[0].name
    sbl__ypk, sfizc__wjrpx, lqr__zzeyo = block_use_map[xjy__dcbi]
    if sfizc__wjrpx or lqr__zzeyo:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        wsrh__ffoc, ajelj__lrgg, gzk__gbq = _compute_table_column_uses(agg_node
            .out_vars[0].name, table_col_use_map, equiv_vars)
        if ajelj__lrgg or gzk__gbq:
            wsrh__ffoc = set(range(agg_node.n_out_table_arrays))
    else:
        wsrh__ffoc = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            wsrh__ffoc = {0}
    tstt__jarh = set(kzcz__eojt for kzcz__eojt in agg_node.in_key_inds if 
        kzcz__eojt < agg_node.n_in_table_arrays)
    pbdjt__fcy = set(agg_node.gb_info_out[kzcz__eojt][0] for kzcz__eojt in
        wsrh__ffoc if kzcz__eojt in agg_node.gb_info_out and agg_node.
        gb_info_out[kzcz__eojt][0] is not None)
    pbdjt__fcy |= tstt__jarh | sbl__ypk
    grz__ape = len(set(range(agg_node.n_in_table_arrays)) - pbdjt__fcy) == 0
    block_use_map[xjy__dcbi] = pbdjt__fcy, grz__ape, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    vun__vxks = agg_node.n_out_table_arrays
    mkb__aqtdj = agg_node.out_vars[0].name
    aljku__vyko = _find_used_columns(mkb__aqtdj, vun__vxks, column_live_map,
        equiv_vars)
    if aljku__vyko is None:
        return False
    uemr__jmqb = set(range(vun__vxks)) - aljku__vyko
    ubugm__wgyru = len(uemr__jmqb - agg_node.dead_out_inds) != 0
    if ubugm__wgyru:
        agg_node.dead_out_inds.update(uemr__jmqb)
        agg_node.update_dead_col_info()
    return ubugm__wgyru


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for ywe__ypuj in block.body:
            if is_call_assign(ywe__ypuj) and find_callname(f_ir, ywe__ypuj.
                value) == ('len', 'builtins') and ywe__ypuj.value.args[0
                ].name == f_ir.arg_names[0]:
                vwbjc__thgxl = get_definition(f_ir, ywe__ypuj.value.func)
                vwbjc__thgxl.name = 'dummy_agg_count'
                vwbjc__thgxl.value = dummy_agg_count
    mzd__tzxhm = get_name_var_table(f_ir.blocks)
    rfue__kkm = {}
    for name, mhc__xkp in mzd__tzxhm.items():
        rfue__kkm[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, rfue__kkm)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    ihx__bwd = numba.core.compiler.Flags()
    ihx__bwd.nrt = True
    oyvrd__kgwyg = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, ihx__bwd)
    oyvrd__kgwyg.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, aak__bhv, calltypes, mhc__xkp = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    stzoj__dyd = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    mpez__wbson = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    kjqfp__zmeed = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    qnotf__mcush = kjqfp__zmeed(typemap, calltypes)
    pm = mpez__wbson(typingctx, targetctx, None, f_ir, typemap, aak__bhv,
        calltypes, qnotf__mcush, {}, ihx__bwd, None)
    oyc__edpqx = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = mpez__wbson(typingctx, targetctx, None, f_ir, typemap, aak__bhv,
        calltypes, qnotf__mcush, {}, ihx__bwd, oyc__edpqx)
    rlc__vgv = numba.core.typed_passes.InlineOverloads()
    rlc__vgv.run_pass(pm)
    zeld__lqt = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    zeld__lqt.run()
    for block in f_ir.blocks.values():
        for ywe__ypuj in block.body:
            if is_assign(ywe__ypuj) and isinstance(ywe__ypuj.value, (ir.Arg,
                ir.Var)) and isinstance(typemap[ywe__ypuj.target.name],
                SeriesType):
                hdlhl__qcbos = typemap.pop(ywe__ypuj.target.name)
                typemap[ywe__ypuj.target.name] = hdlhl__qcbos.data
            if is_call_assign(ywe__ypuj) and find_callname(f_ir, ywe__ypuj.
                value) == ('get_series_data', 'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[ywe__ypuj.target.name].remove(ywe__ypuj.value
                    )
                ywe__ypuj.value = ywe__ypuj.value.args[0]
                f_ir._definitions[ywe__ypuj.target.name].append(ywe__ypuj.value
                    )
            if is_call_assign(ywe__ypuj) and find_callname(f_ir, ywe__ypuj.
                value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[ywe__ypuj.target.name].remove(ywe__ypuj.value
                    )
                ywe__ypuj.value = ir.Const(False, ywe__ypuj.loc)
                f_ir._definitions[ywe__ypuj.target.name].append(ywe__ypuj.value
                    )
            if is_call_assign(ywe__ypuj) and find_callname(f_ir, ywe__ypuj.
                value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[ywe__ypuj.target.name].remove(ywe__ypuj.value
                    )
                ywe__ypuj.value = ir.Const(False, ywe__ypuj.loc)
                f_ir._definitions[ywe__ypuj.target.name].append(ywe__ypuj.value
                    )
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    zxx__mpjpp = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, stzoj__dyd)
    zxx__mpjpp.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    yzeiu__bnp = numba.core.compiler.StateDict()
    yzeiu__bnp.func_ir = f_ir
    yzeiu__bnp.typemap = typemap
    yzeiu__bnp.calltypes = calltypes
    yzeiu__bnp.typingctx = typingctx
    yzeiu__bnp.targetctx = targetctx
    yzeiu__bnp.return_type = aak__bhv
    numba.core.rewrites.rewrite_registry.apply('after-inference', yzeiu__bnp)
    irgn__nvvd = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        aak__bhv, typingctx, targetctx, stzoj__dyd, ihx__bwd, {})
    irgn__nvvd.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            njfgd__rygoi = ctypes.pythonapi.PyCell_Get
            njfgd__rygoi.restype = ctypes.py_object
            njfgd__rygoi.argtypes = ctypes.py_object,
            tjy__xnihi = tuple(njfgd__rygoi(jrp__hwhrv) for jrp__hwhrv in
                closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            tjy__xnihi = closure.items
        assert len(code.co_freevars) == len(tjy__xnihi)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, tjy__xnihi
            )


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
        nmsuv__bax = SeriesType(in_col_typ.dtype, to_str_arr_if_dict_array(
            in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (nmsuv__bax,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        hjk__vqs, arr_var = _rm_arg_agg_block(block, pm.typemap)
        grsad__eoa = -1
        for kzcz__eojt, ywe__ypuj in enumerate(hjk__vqs):
            if isinstance(ywe__ypuj, numba.parfors.parfor.Parfor):
                assert grsad__eoa == -1, 'only one parfor for aggregation function'
                grsad__eoa = kzcz__eojt
        parfor = None
        if grsad__eoa != -1:
            parfor = hjk__vqs[grsad__eoa]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = hjk__vqs[:grsad__eoa] + parfor.init_block.body
        eval_nodes = hjk__vqs[grsad__eoa + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for ywe__ypuj in init_nodes:
            if is_assign(ywe__ypuj) and ywe__ypuj.target.name in redvars:
                ind = redvars.index(ywe__ypuj.target.name)
                reduce_vars[ind] = ywe__ypuj.target
        var_types = [pm.typemap[iudj__lxrum] for iudj__lxrum in redvars]
        rqcqj__riuv = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        dgdow__wiqn = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        uapnb__nxc = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(uapnb__nxc)
        self.all_update_funcs.append(dgdow__wiqn)
        self.all_combine_funcs.append(rqcqj__riuv)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        zpl__ajvep = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        fhpm__jcl = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        pssmi__qrbp = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        xbcn__xggz = gen_all_eval_func(self.all_eval_funcs, self.redvar_offsets
            )
        return (self.all_vartypes, zpl__ajvep, fhpm__jcl, pssmi__qrbp,
            xbcn__xggz)


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
    dxwqj__djqbs = []
    for t, fhjyi__gamf in zip(in_col_types, agg_func):
        dxwqj__djqbs.append((t, fhjyi__gamf))
    umgx__twm = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    mqs__ocxo = GeneralUDFGenerator()
    for in_col_typ, func in dxwqj__djqbs:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            umgx__twm.add_udf(in_col_typ, func)
        except:
            mqs__ocxo.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = umgx__twm.gen_all_func()
    general_udf_funcs = mqs__ocxo.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    sck__vwek = compute_use_defs(parfor.loop_body)
    boos__kyjbf = set()
    for kzpw__tgcwg in sck__vwek.usemap.values():
        boos__kyjbf |= kzpw__tgcwg
    kuyo__fblp = set()
    for kzpw__tgcwg in sck__vwek.defmap.values():
        kuyo__fblp |= kzpw__tgcwg
    xcdxk__pvg = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    xcdxk__pvg.body = eval_nodes
    ipdi__hexu = compute_use_defs({(0): xcdxk__pvg})
    hhw__lqyt = ipdi__hexu.usemap[0]
    dpg__sucpx = set()
    hcrme__sbh = []
    zer__wbx = []
    for ywe__ypuj in reversed(init_nodes):
        rcvm__run = {iudj__lxrum.name for iudj__lxrum in ywe__ypuj.list_vars()}
        if is_assign(ywe__ypuj):
            iudj__lxrum = ywe__ypuj.target.name
            rcvm__run.remove(iudj__lxrum)
            if (iudj__lxrum in boos__kyjbf and iudj__lxrum not in
                dpg__sucpx and iudj__lxrum not in hhw__lqyt and iudj__lxrum
                 not in kuyo__fblp):
                zer__wbx.append(ywe__ypuj)
                boos__kyjbf |= rcvm__run
                kuyo__fblp.add(iudj__lxrum)
                continue
        dpg__sucpx |= rcvm__run
        hcrme__sbh.append(ywe__ypuj)
    zer__wbx.reverse()
    hcrme__sbh.reverse()
    sgmto__walpb = min(parfor.loop_body.keys())
    kkg__ugaz = parfor.loop_body[sgmto__walpb]
    kkg__ugaz.body = zer__wbx + kkg__ugaz.body
    return hcrme__sbh


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    wzku__kbwnz = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    ivxw__cqudd = set()
    whfr__muz = []
    for ywe__ypuj in init_nodes:
        if is_assign(ywe__ypuj) and isinstance(ywe__ypuj.value, ir.Global
            ) and isinstance(ywe__ypuj.value.value, pytypes.FunctionType
            ) and ywe__ypuj.value.value in wzku__kbwnz:
            ivxw__cqudd.add(ywe__ypuj.target.name)
        elif is_call_assign(ywe__ypuj
            ) and ywe__ypuj.value.func.name in ivxw__cqudd:
            pass
        else:
            whfr__muz.append(ywe__ypuj)
    init_nodes = whfr__muz
    ceoyr__rdmy = types.Tuple(var_types)
    imey__ktgr = lambda : None
    f_ir = compile_to_numba_ir(imey__ktgr, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    zewlf__vqx = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    cma__vglc = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc), zewlf__vqx,
        loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [cma__vglc] + block.body
    block.body[-2].value.value = zewlf__vqx
    bss__ckvg = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        ceoyr__rdmy, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    gcl__wjqnr = numba.core.target_extension.dispatcher_registry[cpu_target](
        imey__ktgr)
    gcl__wjqnr.add_overload(bss__ckvg)
    return gcl__wjqnr


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    mvyvd__bxje = len(update_funcs)
    mxdx__okz = len(in_col_types)
    qcprb__jgfhe = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for vqyz__paz in range(mvyvd__bxje):
        dvi__bzlt = ', '.join(['redvar_arrs[{}][w_ind]'.format(kzcz__eojt) for
            kzcz__eojt in range(redvar_offsets[vqyz__paz], redvar_offsets[
            vqyz__paz + 1])])
        if dvi__bzlt:
            qcprb__jgfhe += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                .format(dvi__bzlt, vqyz__paz, dvi__bzlt, 0 if mxdx__okz == 
                1 else vqyz__paz))
    qcprb__jgfhe += '  return\n'
    ocwwl__qyiti = {}
    for kzcz__eojt, fhjyi__gamf in enumerate(update_funcs):
        ocwwl__qyiti['update_vars_{}'.format(kzcz__eojt)] = fhjyi__gamf
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, ocwwl__qyiti, ldwoi__dmd)
    vfr__mvt = ldwoi__dmd['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(vfr__mvt)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    vpwl__udd = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types])
    arg_typs = vpwl__udd, vpwl__udd, types.intp, types.intp
    aho__iko = len(redvar_offsets) - 1
    qcprb__jgfhe = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for vqyz__paz in range(aho__iko):
        dvi__bzlt = ', '.join(['redvar_arrs[{}][w_ind]'.format(kzcz__eojt) for
            kzcz__eojt in range(redvar_offsets[vqyz__paz], redvar_offsets[
            vqyz__paz + 1])])
        guhje__vrgs = ', '.join(['recv_arrs[{}][i]'.format(kzcz__eojt) for
            kzcz__eojt in range(redvar_offsets[vqyz__paz], redvar_offsets[
            vqyz__paz + 1])])
        if guhje__vrgs:
            qcprb__jgfhe += '  {} = combine_vars_{}({}, {})\n'.format(dvi__bzlt
                , vqyz__paz, dvi__bzlt, guhje__vrgs)
    qcprb__jgfhe += '  return\n'
    ocwwl__qyiti = {}
    for kzcz__eojt, fhjyi__gamf in enumerate(combine_funcs):
        ocwwl__qyiti['combine_vars_{}'.format(kzcz__eojt)] = fhjyi__gamf
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, ocwwl__qyiti, ldwoi__dmd)
    fnsm__sab = ldwoi__dmd['combine_all_f']
    f_ir = compile_to_numba_ir(fnsm__sab, ocwwl__qyiti)
    pssmi__qrbp = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    gcl__wjqnr = numba.core.target_extension.dispatcher_registry[cpu_target](
        fnsm__sab)
    gcl__wjqnr.add_overload(pssmi__qrbp)
    return gcl__wjqnr


def gen_all_eval_func(eval_funcs, redvar_offsets):
    aho__iko = len(redvar_offsets) - 1
    qcprb__jgfhe = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for vqyz__paz in range(aho__iko):
        dvi__bzlt = ', '.join(['redvar_arrs[{}][j]'.format(kzcz__eojt) for
            kzcz__eojt in range(redvar_offsets[vqyz__paz], redvar_offsets[
            vqyz__paz + 1])])
        qcprb__jgfhe += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
            vqyz__paz, vqyz__paz, dvi__bzlt)
    qcprb__jgfhe += '  return\n'
    ocwwl__qyiti = {}
    for kzcz__eojt, fhjyi__gamf in enumerate(eval_funcs):
        ocwwl__qyiti['eval_vars_{}'.format(kzcz__eojt)] = fhjyi__gamf
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, ocwwl__qyiti, ldwoi__dmd)
    daag__lksob = ldwoi__dmd['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(daag__lksob)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    wsewy__ybpea = len(var_types)
    xou__gjqn = [f'in{kzcz__eojt}' for kzcz__eojt in range(wsewy__ybpea)]
    ceoyr__rdmy = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    tqar__rlty = ceoyr__rdmy(0)
    qcprb__jgfhe = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        xou__gjqn))
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, {'_zero': tqar__rlty}, ldwoi__dmd)
    rga__ajpl = ldwoi__dmd['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(rga__ajpl, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': tqar__rlty}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    qtz__wyaj = []
    for kzcz__eojt, iudj__lxrum in enumerate(reduce_vars):
        qtz__wyaj.append(ir.Assign(block.body[kzcz__eojt].target,
            iudj__lxrum, iudj__lxrum.loc))
        for abrkd__nnkkh in iudj__lxrum.versioned_names:
            qtz__wyaj.append(ir.Assign(iudj__lxrum, ir.Var(iudj__lxrum.
                scope, abrkd__nnkkh, iudj__lxrum.loc), iudj__lxrum.loc))
    block.body = block.body[:wsewy__ybpea] + qtz__wyaj + eval_nodes
    uapnb__nxc = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        ceoyr__rdmy, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    gcl__wjqnr = numba.core.target_extension.dispatcher_registry[cpu_target](
        rga__ajpl)
    gcl__wjqnr.add_overload(uapnb__nxc)
    return gcl__wjqnr


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    wsewy__ybpea = len(redvars)
    qkdb__tyvkk = [f'v{kzcz__eojt}' for kzcz__eojt in range(wsewy__ybpea)]
    xou__gjqn = [f'in{kzcz__eojt}' for kzcz__eojt in range(wsewy__ybpea)]
    qcprb__jgfhe = 'def agg_combine({}):\n'.format(', '.join(qkdb__tyvkk +
        xou__gjqn))
    rvah__idv = wrap_parfor_blocks(parfor)
    sysm__oduvo = find_topo_order(rvah__idv)
    sysm__oduvo = sysm__oduvo[1:]
    unwrap_parfor_blocks(parfor)
    qtr__vsw = {}
    sgyb__ioon = []
    for kcidg__xpucj in sysm__oduvo:
        xro__wwoq = parfor.loop_body[kcidg__xpucj]
        for ywe__ypuj in xro__wwoq.body:
            if is_assign(ywe__ypuj) and ywe__ypuj.target.name in redvars:
                dgock__obvy = ywe__ypuj.target.name
                ind = redvars.index(dgock__obvy)
                if ind in sgyb__ioon:
                    continue
                if len(f_ir._definitions[dgock__obvy]) == 2:
                    var_def = f_ir._definitions[dgock__obvy][0]
                    qcprb__jgfhe += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[dgock__obvy][1]
                    qcprb__jgfhe += _match_reduce_def(var_def, f_ir, ind)
    qcprb__jgfhe += '    return {}'.format(', '.join(['v{}'.format(
        kzcz__eojt) for kzcz__eojt in range(wsewy__ybpea)]))
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, {}, ldwoi__dmd)
    vpdxi__kzux = ldwoi__dmd['agg_combine']
    arg_typs = tuple(2 * var_types)
    ocwwl__qyiti = {'numba': numba, 'bodo': bodo, 'np': np}
    ocwwl__qyiti.update(qtr__vsw)
    f_ir = compile_to_numba_ir(vpdxi__kzux, ocwwl__qyiti, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=pm.
        typemap, calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    ceoyr__rdmy = pm.typemap[block.body[-1].value.name]
    rqcqj__riuv = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        ceoyr__rdmy, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    gcl__wjqnr = numba.core.target_extension.dispatcher_registry[cpu_target](
        vpdxi__kzux)
    gcl__wjqnr.add_overload(rqcqj__riuv)
    return gcl__wjqnr


def _match_reduce_def(var_def, f_ir, ind):
    qcprb__jgfhe = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        qcprb__jgfhe = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        uqxig__lntf = guard(find_callname, f_ir, var_def)
        if uqxig__lntf == ('min', 'builtins'):
            qcprb__jgfhe = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if uqxig__lntf == ('max', 'builtins'):
            qcprb__jgfhe = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return qcprb__jgfhe


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    wsewy__ybpea = len(redvars)
    xumng__vgfbs = 1
    in_vars = []
    for kzcz__eojt in range(xumng__vgfbs):
        rfo__waom = ir.Var(arr_var.scope, f'$input{kzcz__eojt}', arr_var.loc)
        in_vars.append(rfo__waom)
    kev__tkft = parfor.loop_nests[0].index_variable
    jcmsm__blmm = [0] * wsewy__ybpea
    for xro__wwoq in parfor.loop_body.values():
        ueqjo__wxhw = []
        for ywe__ypuj in xro__wwoq.body:
            if is_var_assign(ywe__ypuj
                ) and ywe__ypuj.value.name == kev__tkft.name:
                continue
            if is_getitem(ywe__ypuj
                ) and ywe__ypuj.value.value.name == arr_var.name:
                ywe__ypuj.value = in_vars[0]
            if is_call_assign(ywe__ypuj) and guard(find_callname, pm.
                func_ir, ywe__ypuj.value) == ('isna', 'bodo.libs.array_kernels'
                ) and ywe__ypuj.value.args[0].name == arr_var.name:
                ywe__ypuj.value = ir.Const(False, ywe__ypuj.target.loc)
            if is_assign(ywe__ypuj) and ywe__ypuj.target.name in redvars:
                ind = redvars.index(ywe__ypuj.target.name)
                jcmsm__blmm[ind] = ywe__ypuj.target
            ueqjo__wxhw.append(ywe__ypuj)
        xro__wwoq.body = ueqjo__wxhw
    qkdb__tyvkk = ['v{}'.format(kzcz__eojt) for kzcz__eojt in range(
        wsewy__ybpea)]
    xou__gjqn = ['in{}'.format(kzcz__eojt) for kzcz__eojt in range(
        xumng__vgfbs)]
    qcprb__jgfhe = 'def agg_update({}):\n'.format(', '.join(qkdb__tyvkk +
        xou__gjqn))
    qcprb__jgfhe += '    __update_redvars()\n'
    qcprb__jgfhe += '    return {}'.format(', '.join(['v{}'.format(
        kzcz__eojt) for kzcz__eojt in range(wsewy__ybpea)]))
    ldwoi__dmd = {}
    exec(qcprb__jgfhe, {}, ldwoi__dmd)
    ffzq__gskou = ldwoi__dmd['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * xumng__vgfbs)
    f_ir = compile_to_numba_ir(ffzq__gskou, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    xabgk__sie = f_ir.blocks.popitem()[1].body
    ceoyr__rdmy = pm.typemap[xabgk__sie[-1].value.name]
    rvah__idv = wrap_parfor_blocks(parfor)
    sysm__oduvo = find_topo_order(rvah__idv)
    sysm__oduvo = sysm__oduvo[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    kkg__ugaz = f_ir.blocks[sysm__oduvo[0]]
    fpy__xymy = f_ir.blocks[sysm__oduvo[-1]]
    jvjl__xeuud = xabgk__sie[:wsewy__ybpea + xumng__vgfbs]
    if wsewy__ybpea > 1:
        ymco__jml = xabgk__sie[-3:]
        assert is_assign(ymco__jml[0]) and isinstance(ymco__jml[0].value,
            ir.Expr) and ymco__jml[0].value.op == 'build_tuple'
    else:
        ymco__jml = xabgk__sie[-2:]
    for kzcz__eojt in range(wsewy__ybpea):
        xxygv__vpahx = xabgk__sie[kzcz__eojt].target
        xtlg__nkblt = ir.Assign(xxygv__vpahx, jcmsm__blmm[kzcz__eojt],
            xxygv__vpahx.loc)
        jvjl__xeuud.append(xtlg__nkblt)
    for kzcz__eojt in range(wsewy__ybpea, wsewy__ybpea + xumng__vgfbs):
        xxygv__vpahx = xabgk__sie[kzcz__eojt].target
        xtlg__nkblt = ir.Assign(xxygv__vpahx, in_vars[kzcz__eojt -
            wsewy__ybpea], xxygv__vpahx.loc)
        jvjl__xeuud.append(xtlg__nkblt)
    kkg__ugaz.body = jvjl__xeuud + kkg__ugaz.body
    gzz__uurrs = []
    for kzcz__eojt in range(wsewy__ybpea):
        xxygv__vpahx = xabgk__sie[kzcz__eojt].target
        xtlg__nkblt = ir.Assign(jcmsm__blmm[kzcz__eojt], xxygv__vpahx,
            xxygv__vpahx.loc)
        gzz__uurrs.append(xtlg__nkblt)
    fpy__xymy.body += gzz__uurrs + ymco__jml
    noo__fhm = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        ceoyr__rdmy, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    gcl__wjqnr = numba.core.target_extension.dispatcher_registry[cpu_target](
        ffzq__gskou)
    gcl__wjqnr.add_overload(noo__fhm)
    return gcl__wjqnr


def _rm_arg_agg_block(block, typemap):
    hjk__vqs = []
    arr_var = None
    for kzcz__eojt, ywe__ypuj in enumerate(block.body):
        if is_assign(ywe__ypuj) and isinstance(ywe__ypuj.value, ir.Arg):
            arr_var = ywe__ypuj.target
            zab__aynp = typemap[arr_var.name]
            if not isinstance(zab__aynp, types.ArrayCompatible):
                hjk__vqs += block.body[kzcz__eojt + 1:]
                break
            bsp__aza = block.body[kzcz__eojt + 1]
            assert is_assign(bsp__aza) and isinstance(bsp__aza.value, ir.Expr
                ) and bsp__aza.value.op == 'getattr' and bsp__aza.value.attr == 'shape' and bsp__aza.value.value.name == arr_var.name
            deszo__xtgt = bsp__aza.target
            tfhj__gmxjr = block.body[kzcz__eojt + 2]
            assert is_assign(tfhj__gmxjr) and isinstance(tfhj__gmxjr.value,
                ir.Expr
                ) and tfhj__gmxjr.value.op == 'static_getitem' and tfhj__gmxjr.value.value.name == deszo__xtgt.name
            hjk__vqs += block.body[kzcz__eojt + 3:]
            break
        hjk__vqs.append(ywe__ypuj)
    return hjk__vqs, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    rvah__idv = wrap_parfor_blocks(parfor)
    sysm__oduvo = find_topo_order(rvah__idv)
    sysm__oduvo = sysm__oduvo[1:]
    unwrap_parfor_blocks(parfor)
    for kcidg__xpucj in reversed(sysm__oduvo):
        for ywe__ypuj in reversed(parfor.loop_body[kcidg__xpucj].body):
            if isinstance(ywe__ypuj, ir.Assign) and (ywe__ypuj.target.name in
                parfor_params or ywe__ypuj.target.name in var_to_param):
                skypf__vpig = ywe__ypuj.target.name
                rhs = ywe__ypuj.value
                zomqd__jvq = (skypf__vpig if skypf__vpig in parfor_params else
                    var_to_param[skypf__vpig])
                npnnz__pqm = []
                if isinstance(rhs, ir.Var):
                    npnnz__pqm = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    npnnz__pqm = [iudj__lxrum.name for iudj__lxrum in
                        ywe__ypuj.value.list_vars()]
                param_uses[zomqd__jvq].extend(npnnz__pqm)
                for iudj__lxrum in npnnz__pqm:
                    var_to_param[iudj__lxrum] = zomqd__jvq
            if isinstance(ywe__ypuj, Parfor):
                get_parfor_reductions(ywe__ypuj, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for noh__rpgv, npnnz__pqm in param_uses.items():
        if noh__rpgv in npnnz__pqm and noh__rpgv not in reduce_varnames:
            reduce_varnames.append(noh__rpgv)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
