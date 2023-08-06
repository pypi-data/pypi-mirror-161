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
        fzm__dsuaz = func.signature
        if fzm__dsuaz == types.none(types.voidptr):
            inqg__wjsh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            elbir__per = cgutils.get_or_insert_function(builder.module,
                inqg__wjsh, sym._literal_value)
            builder.call(elbir__per, [context.get_constant_null(fzm__dsuaz.
                args[0])])
        elif fzm__dsuaz == types.none(types.int64, types.voidptr, types.voidptr
            ):
            inqg__wjsh = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            elbir__per = cgutils.get_or_insert_function(builder.module,
                inqg__wjsh, sym._literal_value)
            builder.call(elbir__per, [context.get_constant(types.int64, 0),
                context.get_constant_null(fzm__dsuaz.args[1]), context.
                get_constant_null(fzm__dsuaz.args[2])])
        else:
            inqg__wjsh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            elbir__per = cgutils.get_or_insert_function(builder.module,
                inqg__wjsh, sym._literal_value)
            builder.call(elbir__per, [context.get_constant_null(fzm__dsuaz.
                args[0]), context.get_constant_null(fzm__dsuaz.args[1]),
                context.get_constant_null(fzm__dsuaz.args[2])])
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
        jgl__cahx = True
        vshxj__avwgq = 1
        prob__lxwe = -1
        if isinstance(rhs, ir.Expr):
            for ocki__vqcc in rhs.kws:
                if func_name in list_cumulative:
                    if ocki__vqcc[0] == 'skipna':
                        jgl__cahx = guard(find_const, func_ir, ocki__vqcc[1])
                        if not isinstance(jgl__cahx, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if ocki__vqcc[0] == 'dropna':
                        jgl__cahx = guard(find_const, func_ir, ocki__vqcc[1])
                        if not isinstance(jgl__cahx, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            vshxj__avwgq = get_call_expr_arg('shift', rhs.args, dict(rhs.
                kws), 0, 'periods', vshxj__avwgq)
            vshxj__avwgq = guard(find_const, func_ir, vshxj__avwgq)
        if func_name == 'head':
            prob__lxwe = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(prob__lxwe, int):
                prob__lxwe = guard(find_const, func_ir, prob__lxwe)
            if prob__lxwe < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = jgl__cahx
        func.periods = vshxj__avwgq
        func.head_n = prob__lxwe
        if func_name == 'transform':
            kws = dict(rhs.kws)
            kftv__zxb = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            ausfu__pys = typemap[kftv__zxb.name]
            goay__uvyy = None
            if isinstance(ausfu__pys, str):
                goay__uvyy = ausfu__pys
            elif is_overload_constant_str(ausfu__pys):
                goay__uvyy = get_overload_const_str(ausfu__pys)
            elif bodo.utils.typing.is_builtin_function(ausfu__pys):
                goay__uvyy = bodo.utils.typing.get_builtin_function_name(
                    ausfu__pys)
            if goay__uvyy not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {goay__uvyy}')
            func.transform_func = supported_agg_funcs.index(goay__uvyy)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    kftv__zxb = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if kftv__zxb == '':
        ausfu__pys = types.none
    else:
        ausfu__pys = typemap[kftv__zxb.name]
    if is_overload_constant_dict(ausfu__pys):
        wpi__bij = get_overload_constant_dict(ausfu__pys)
        cjrsb__dvz = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in wpi__bij.values()]
        return cjrsb__dvz
    if ausfu__pys == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(ausfu__pys, types.BaseTuple) or is_overload_constant_list(
        ausfu__pys):
        cjrsb__dvz = []
        cicsp__nws = 0
        if is_overload_constant_list(ausfu__pys):
            mcekw__eiih = get_overload_const_list(ausfu__pys)
        else:
            mcekw__eiih = ausfu__pys.types
        for t in mcekw__eiih:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                cjrsb__dvz.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>' and len(mcekw__eiih) > 1:
                    func.fname = '<lambda_' + str(cicsp__nws) + '>'
                    cicsp__nws += 1
                cjrsb__dvz.append(func)
        return [cjrsb__dvz]
    if is_overload_constant_str(ausfu__pys):
        func_name = get_overload_const_str(ausfu__pys)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(ausfu__pys):
        func_name = bodo.utils.typing.get_builtin_function_name(ausfu__pys)
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
        cicsp__nws = 0
        ujvm__szb = []
        for fmu__kwdnz in f_val:
            func = get_agg_func_udf(func_ir, fmu__kwdnz, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{cicsp__nws}>'
                cicsp__nws += 1
            ujvm__szb.append(func)
        return ujvm__szb
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
    goay__uvyy = code.co_name
    return goay__uvyy


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
            wre__yhml = types.DType(args[0])
            return signature(wre__yhml, *args)


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
        return [lez__olg for lez__olg in self.in_vars if lez__olg is not None]

    def get_live_out_vars(self):
        return [lez__olg for lez__olg in self.out_vars if lez__olg is not None]

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
        zeqew__yaowm = [self.out_type.data] if isinstance(self.out_type,
            SeriesType) else list(self.out_type.table_type.arr_types)
        vcuj__bqk = list(get_index_data_arr_types(self.out_type.index))
        return zeqew__yaowm + vcuj__bqk

    def update_dead_col_info(self):
        for jbpp__tpzq in self.dead_out_inds:
            self.gb_info_out.pop(jbpp__tpzq, None)
        if not self.input_has_index:
            self.dead_in_inds.add(self.n_in_cols - 1)
            self.dead_out_inds.add(self.n_out_cols - 1)
        for knbb__gyu, npj__ejpr in self.gb_info_in.copy().items():
            rfbt__xww = []
            for fmu__kwdnz, zbls__pjuco in npj__ejpr:
                if zbls__pjuco not in self.dead_out_inds:
                    rfbt__xww.append((fmu__kwdnz, zbls__pjuco))
            if not rfbt__xww:
                if knbb__gyu is not None and knbb__gyu not in self.in_key_inds:
                    self.dead_in_inds.add(knbb__gyu)
                self.gb_info_in.pop(knbb__gyu)
            else:
                self.gb_info_in[knbb__gyu] = rfbt__xww
        if self.is_in_table_format:
            if not set(range(self.n_in_table_arrays)) - self.dead_in_inds:
                self.in_vars[0] = None
            for omugw__dsk in range(1, len(self.in_vars)):
                jbpp__tpzq = self.n_in_table_arrays + omugw__dsk - 1
                if jbpp__tpzq in self.dead_in_inds:
                    self.in_vars[omugw__dsk] = None
        else:
            for omugw__dsk in range(len(self.in_vars)):
                if omugw__dsk in self.dead_in_inds:
                    self.in_vars[omugw__dsk] = None

    def __repr__(self):
        ntmfd__yuf = ', '.join(lez__olg.name for lez__olg in self.
            get_live_in_vars())
        arnfv__zjpyv = f'{self.df_in}{{{ntmfd__yuf}}}'
        rczct__lnsd = ', '.join(lez__olg.name for lez__olg in self.
            get_live_out_vars())
        qcyek__aipc = f'{self.df_out}{{{rczct__lnsd}}}'
        return (
            f'Groupby (keys: {self.key_names} {self.in_key_inds}): {arnfv__zjpyv} {qcyek__aipc}'
            )


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({lez__olg.name for lez__olg in aggregate_node.
        get_live_in_vars()})
    def_set.update({lez__olg.name for lez__olg in aggregate_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(agg_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    uhl__rfkf = agg_node.out_vars[0]
    if uhl__rfkf is not None and uhl__rfkf.name not in lives:
        agg_node.out_vars[0] = None
        if agg_node.is_output_table:
            mazc__etp = set(range(agg_node.n_out_table_arrays))
            agg_node.dead_out_inds.update(mazc__etp)
        else:
            agg_node.dead_out_inds.add(0)
    for omugw__dsk in range(1, len(agg_node.out_vars)):
        lez__olg = agg_node.out_vars[omugw__dsk]
        if lez__olg is not None and lez__olg.name not in lives:
            agg_node.out_vars[omugw__dsk] = None
            jbpp__tpzq = agg_node.n_out_table_arrays + omugw__dsk - 1
            agg_node.dead_out_inds.add(jbpp__tpzq)
    if all(lez__olg is None for lez__olg in agg_node.out_vars):
        return None
    agg_node.update_dead_col_info()
    return agg_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    rpvig__etja = {lez__olg.name for lez__olg in aggregate_node.
        get_live_out_vars()}
    return set(), rpvig__etja


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for omugw__dsk in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[omugw__dsk] is not None:
            aggregate_node.in_vars[omugw__dsk] = replace_vars_inner(
                aggregate_node.in_vars[omugw__dsk], var_dict)
    for omugw__dsk in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[omugw__dsk] is not None:
            aggregate_node.out_vars[omugw__dsk] = replace_vars_inner(
                aggregate_node.out_vars[omugw__dsk], var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    for omugw__dsk in range(len(aggregate_node.in_vars)):
        if aggregate_node.in_vars[omugw__dsk] is not None:
            aggregate_node.in_vars[omugw__dsk] = visit_vars_inner(
                aggregate_node.in_vars[omugw__dsk], callback, cbdata)
    for omugw__dsk in range(len(aggregate_node.out_vars)):
        if aggregate_node.out_vars[omugw__dsk] is not None:
            aggregate_node.out_vars[omugw__dsk] = visit_vars_inner(
                aggregate_node.out_vars[omugw__dsk], callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    tvboa__xkzb = []
    for cor__wsnt in aggregate_node.get_live_in_vars():
        ctr__uyh = equiv_set.get_shape(cor__wsnt)
        if ctr__uyh is not None:
            tvboa__xkzb.append(ctr__uyh[0])
    if len(tvboa__xkzb) > 1:
        equiv_set.insert_equiv(*tvboa__xkzb)
    hbyz__bta = []
    tvboa__xkzb = []
    for cor__wsnt in aggregate_node.get_live_out_vars():
        gguff__zhym = typemap[cor__wsnt.name]
        nwt__zygnl = array_analysis._gen_shape_call(equiv_set, cor__wsnt,
            gguff__zhym.ndim, None, hbyz__bta)
        equiv_set.insert_equiv(cor__wsnt, nwt__zygnl)
        tvboa__xkzb.append(nwt__zygnl[0])
        equiv_set.define(cor__wsnt, set())
    if len(tvboa__xkzb) > 1:
        equiv_set.insert_equiv(*tvboa__xkzb)
    return [], hbyz__bta


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    rtdw__csszo = aggregate_node.get_live_in_vars()
    yedsp__ymw = aggregate_node.get_live_out_vars()
    pjj__uxez = Distribution.OneD
    for cor__wsnt in rtdw__csszo:
        pjj__uxez = Distribution(min(pjj__uxez.value, array_dists[cor__wsnt
            .name].value))
    dtmos__lwjjz = Distribution(min(pjj__uxez.value, Distribution.OneD_Var.
        value))
    for cor__wsnt in yedsp__ymw:
        if cor__wsnt.name in array_dists:
            dtmos__lwjjz = Distribution(min(dtmos__lwjjz.value, array_dists
                [cor__wsnt.name].value))
    if dtmos__lwjjz != Distribution.OneD_Var:
        pjj__uxez = dtmos__lwjjz
    for cor__wsnt in rtdw__csszo:
        array_dists[cor__wsnt.name] = pjj__uxez
    for cor__wsnt in yedsp__ymw:
        array_dists[cor__wsnt.name] = dtmos__lwjjz


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for cor__wsnt in agg_node.get_live_out_vars():
        definitions[cor__wsnt.name].append(agg_node)
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
    dvo__sdv = agg_node.get_live_in_vars()
    mmapb__epvlm = agg_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for lez__olg in (dvo__sdv + mmapb__epvlm):
            if array_dists[lez__olg.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                lez__olg.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    out_col_typs = agg_node.out_col_types
    in_col_typs = []
    cjrsb__dvz = []
    func_out_types = []
    for zbls__pjuco, (knbb__gyu, func) in agg_node.gb_info_out.items():
        if knbb__gyu is not None:
            t = agg_node.in_col_types[knbb__gyu]
            in_col_typs.append(t)
        cjrsb__dvz.append(func)
        func_out_types.append(out_col_typs[zbls__pjuco])
    nesq__mfvw = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for omugw__dsk, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            nesq__mfvw.update({f'in_cat_dtype_{omugw__dsk}': in_col_typ})
    for omugw__dsk, dmfgn__nxppz in enumerate(out_col_typs):
        if isinstance(dmfgn__nxppz, bodo.CategoricalArrayType):
            nesq__mfvw.update({f'out_cat_dtype_{omugw__dsk}': dmfgn__nxppz})
    udf_func_struct = get_udf_func_struct(cjrsb__dvz, in_col_typs,
        typingctx, targetctx)
    out_var_types = [(typemap[lez__olg.name] if lez__olg is not None else
        types.none) for lez__olg in agg_node.out_vars]
    flme__psnc, blfr__vct = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, func_out_types, parallel, udf_func_struct,
        out_var_types, typemap)
    nesq__mfvw.update(blfr__vct)
    nesq__mfvw.update({'pd': pd, 'pre_alloc_string_array':
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
            nesq__mfvw.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            nesq__mfvw.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    agx__wmzwa = {}
    exec(flme__psnc, {}, agx__wmzwa)
    amjc__bdi = agx__wmzwa['agg_top']
    bod__xga = compile_to_numba_ir(amjc__bdi, nesq__mfvw, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[lez__olg.
        name] for lez__olg in dvo__sdv), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(bod__xga, dvo__sdv)
    qmkv__qadw = bod__xga.body[-2].value.value
    djb__ubssy = bod__xga.body[:-2]
    for omugw__dsk, lez__olg in enumerate(mmapb__epvlm):
        gen_getitem(lez__olg, qmkv__qadw, omugw__dsk, calltypes, djb__ubssy)
    return djb__ubssy


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        ygall__bwzf = IntDtype(t.dtype).name
        assert ygall__bwzf.endswith('Dtype()')
        ygall__bwzf = ygall__bwzf[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{ygall__bwzf}'))"
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
        ckv__hyu = 'in' if is_input else 'out'
        return f'bodo.utils.utils.alloc_type(1, {ckv__hyu}_cat_dtype_{colnum})'
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
    csn__chlbl = udf_func_struct.var_typs
    agh__pdblj = len(csn__chlbl)
    flme__psnc = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    flme__psnc += '    if is_null_pointer(in_table):\n'
    flme__psnc += '        return\n'
    flme__psnc += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in csn__chlbl]), 
        ',' if len(csn__chlbl) == 1 else '')
    ycvdn__rglr = n_keys
    dnlt__wytnr = []
    redvar_offsets = []
    jnmy__izh = []
    if do_combine:
        for omugw__dsk, fmu__kwdnz in enumerate(allfuncs):
            if fmu__kwdnz.ftype != 'udf':
                ycvdn__rglr += fmu__kwdnz.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(ycvdn__rglr, ycvdn__rglr +
                    fmu__kwdnz.n_redvars))
                ycvdn__rglr += fmu__kwdnz.n_redvars
                jnmy__izh.append(data_in_typs_[func_idx_to_in_col[omugw__dsk]])
                dnlt__wytnr.append(func_idx_to_in_col[omugw__dsk] + n_keys)
    else:
        for omugw__dsk, fmu__kwdnz in enumerate(allfuncs):
            if fmu__kwdnz.ftype != 'udf':
                ycvdn__rglr += fmu__kwdnz.ncols_post_shuffle
            else:
                redvar_offsets += list(range(ycvdn__rglr + 1, ycvdn__rglr +
                    1 + fmu__kwdnz.n_redvars))
                ycvdn__rglr += fmu__kwdnz.n_redvars + 1
                jnmy__izh.append(data_in_typs_[func_idx_to_in_col[omugw__dsk]])
                dnlt__wytnr.append(func_idx_to_in_col[omugw__dsk] + n_keys)
    assert len(redvar_offsets) == agh__pdblj
    ypurh__kov = len(jnmy__izh)
    mnoy__cxwlq = []
    for omugw__dsk, t in enumerate(jnmy__izh):
        mnoy__cxwlq.append(_gen_dummy_alloc(t, omugw__dsk, True))
    flme__psnc += '    data_in_dummy = ({}{})\n'.format(','.join(
        mnoy__cxwlq), ',' if len(jnmy__izh) == 1 else '')
    flme__psnc += """
    # initialize redvar cols
"""
    flme__psnc += '    init_vals = __init_func()\n'
    for omugw__dsk in range(agh__pdblj):
        flme__psnc += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(omugw__dsk, redvar_offsets[omugw__dsk], omugw__dsk))
        flme__psnc += '    incref(redvar_arr_{})\n'.format(omugw__dsk)
        flme__psnc += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            omugw__dsk, omugw__dsk)
    flme__psnc += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(omugw__dsk) for omugw__dsk in range(agh__pdblj)]), ',' if 
        agh__pdblj == 1 else '')
    flme__psnc += '\n'
    for omugw__dsk in range(ypurh__kov):
        flme__psnc += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(omugw__dsk, dnlt__wytnr[omugw__dsk], omugw__dsk))
        flme__psnc += '    incref(data_in_{})\n'.format(omugw__dsk)
    flme__psnc += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(omugw__dsk) for omugw__dsk in range(ypurh__kov)]), ',' if 
        ypurh__kov == 1 else '')
    flme__psnc += '\n'
    flme__psnc += '    for i in range(len(data_in_0)):\n'
    flme__psnc += '        w_ind = row_to_group[i]\n'
    flme__psnc += '        if w_ind != -1:\n'
    flme__psnc += '            __update_redvars(redvars, data_in, w_ind, i)\n'
    agx__wmzwa = {}
    exec(flme__psnc, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, agx__wmzwa)
    return agx__wmzwa['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, label_suffix):
    csn__chlbl = udf_func_struct.var_typs
    agh__pdblj = len(csn__chlbl)
    flme__psnc = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    flme__psnc += '    if is_null_pointer(in_table):\n'
    flme__psnc += '        return\n'
    flme__psnc += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in csn__chlbl]), 
        ',' if len(csn__chlbl) == 1 else '')
    yvzmq__osh = n_keys
    mbjh__pvtps = n_keys
    owt__xvr = []
    tlfnp__nuk = []
    for fmu__kwdnz in allfuncs:
        if fmu__kwdnz.ftype != 'udf':
            yvzmq__osh += fmu__kwdnz.ncols_pre_shuffle
            mbjh__pvtps += fmu__kwdnz.ncols_post_shuffle
        else:
            owt__xvr += list(range(yvzmq__osh, yvzmq__osh + fmu__kwdnz.
                n_redvars))
            tlfnp__nuk += list(range(mbjh__pvtps + 1, mbjh__pvtps + 1 +
                fmu__kwdnz.n_redvars))
            yvzmq__osh += fmu__kwdnz.n_redvars
            mbjh__pvtps += 1 + fmu__kwdnz.n_redvars
    assert len(owt__xvr) == agh__pdblj
    flme__psnc += """
    # initialize redvar cols
"""
    flme__psnc += '    init_vals = __init_func()\n'
    for omugw__dsk in range(agh__pdblj):
        flme__psnc += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(omugw__dsk, tlfnp__nuk[omugw__dsk], omugw__dsk))
        flme__psnc += '    incref(redvar_arr_{})\n'.format(omugw__dsk)
        flme__psnc += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(
            omugw__dsk, omugw__dsk)
    flme__psnc += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(omugw__dsk) for omugw__dsk in range(agh__pdblj)]), ',' if 
        agh__pdblj == 1 else '')
    flme__psnc += '\n'
    for omugw__dsk in range(agh__pdblj):
        flme__psnc += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(omugw__dsk, owt__xvr[omugw__dsk], omugw__dsk))
        flme__psnc += '    incref(recv_redvar_arr_{})\n'.format(omugw__dsk)
    flme__psnc += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(omugw__dsk) for omugw__dsk in range(
        agh__pdblj)]), ',' if agh__pdblj == 1 else '')
    flme__psnc += '\n'
    if agh__pdblj:
        flme__psnc += '    for i in range(len(recv_redvar_arr_0)):\n'
        flme__psnc += '        w_ind = row_to_group[i]\n'
        flme__psnc += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i)\n')
    agx__wmzwa = {}
    exec(flme__psnc, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, agx__wmzwa)
    return agx__wmzwa['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    csn__chlbl = udf_func_struct.var_typs
    agh__pdblj = len(csn__chlbl)
    ycvdn__rglr = n_keys
    redvar_offsets = []
    bimo__rpx = []
    rrrw__gmzai = []
    for omugw__dsk, fmu__kwdnz in enumerate(allfuncs):
        if fmu__kwdnz.ftype != 'udf':
            ycvdn__rglr += fmu__kwdnz.ncols_post_shuffle
        else:
            bimo__rpx.append(ycvdn__rglr)
            redvar_offsets += list(range(ycvdn__rglr + 1, ycvdn__rglr + 1 +
                fmu__kwdnz.n_redvars))
            ycvdn__rglr += 1 + fmu__kwdnz.n_redvars
            rrrw__gmzai.append(out_data_typs_[omugw__dsk])
    assert len(redvar_offsets) == agh__pdblj
    ypurh__kov = len(rrrw__gmzai)
    flme__psnc = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    flme__psnc += '    if is_null_pointer(table):\n'
    flme__psnc += '        return\n'
    flme__psnc += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in csn__chlbl]), 
        ',' if len(csn__chlbl) == 1 else '')
    flme__psnc += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        rrrw__gmzai]), ',' if len(rrrw__gmzai) == 1 else '')
    for omugw__dsk in range(agh__pdblj):
        flme__psnc += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(omugw__dsk, redvar_offsets[omugw__dsk], omugw__dsk))
        flme__psnc += '    incref(redvar_arr_{})\n'.format(omugw__dsk)
    flme__psnc += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'
        .format(omugw__dsk) for omugw__dsk in range(agh__pdblj)]), ',' if 
        agh__pdblj == 1 else '')
    flme__psnc += '\n'
    for omugw__dsk in range(ypurh__kov):
        flme__psnc += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(omugw__dsk, bimo__rpx[omugw__dsk], omugw__dsk))
        flme__psnc += '    incref(data_out_{})\n'.format(omugw__dsk)
    flme__psnc += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(omugw__dsk) for omugw__dsk in range(ypurh__kov)]), ',' if 
        ypurh__kov == 1 else '')
    flme__psnc += '\n'
    flme__psnc += '    for i in range(len(data_out_0)):\n'
    flme__psnc += '        __eval_res(redvars, data_out, i)\n'
    agx__wmzwa = {}
    exec(flme__psnc, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, agx__wmzwa)
    return agx__wmzwa['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    ycvdn__rglr = n_keys
    vzkpx__glz = []
    for omugw__dsk, fmu__kwdnz in enumerate(allfuncs):
        if fmu__kwdnz.ftype == 'gen_udf':
            vzkpx__glz.append(ycvdn__rglr)
            ycvdn__rglr += 1
        elif fmu__kwdnz.ftype != 'udf':
            ycvdn__rglr += fmu__kwdnz.ncols_post_shuffle
        else:
            ycvdn__rglr += fmu__kwdnz.n_redvars + 1
    flme__psnc = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    flme__psnc += '    if num_groups == 0:\n'
    flme__psnc += '        return\n'
    for omugw__dsk, func in enumerate(udf_func_struct.general_udf_funcs):
        flme__psnc += '    # col {}\n'.format(omugw__dsk)
        flme__psnc += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(vzkpx__glz[omugw__dsk], omugw__dsk))
        flme__psnc += '    incref(out_col)\n'
        flme__psnc += '    for j in range(num_groups):\n'
        flme__psnc += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(omugw__dsk, omugw__dsk))
        flme__psnc += '        incref(in_col)\n'
        flme__psnc += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(omugw__dsk))
    nesq__mfvw = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    jocb__ppzye = 0
    for omugw__dsk, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[jocb__ppzye]
        nesq__mfvw['func_{}'.format(jocb__ppzye)] = func
        nesq__mfvw['in_col_{}_typ'.format(jocb__ppzye)] = in_col_typs[
            func_idx_to_in_col[omugw__dsk]]
        nesq__mfvw['out_col_{}_typ'.format(jocb__ppzye)] = out_col_typs[
            omugw__dsk]
        jocb__ppzye += 1
    agx__wmzwa = {}
    exec(flme__psnc, nesq__mfvw, agx__wmzwa)
    fmu__kwdnz = agx__wmzwa['bodo_gb_apply_general_udfs{}'.format(label_suffix)
        ]
    ljchd__ynrji = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(ljchd__ynrji, nopython=True)(fmu__kwdnz)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
    func_out_types, parallel, udf_func_struct, out_var_types, typemap):
    n_keys = len(agg_node.in_key_inds)
    dxa__mus = len(agg_node.out_vars)
    if agg_node.same_index:
        assert agg_node.input_has_index, 'agg codegen: input_has_index=True required for same_index=True'
    if agg_node.is_in_table_format:
        nmwg__hwdhq = []
        if agg_node.in_vars[0] is not None:
            nmwg__hwdhq.append('arg0')
        for omugw__dsk in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if omugw__dsk not in agg_node.dead_in_inds:
                nmwg__hwdhq.append(f'arg{omugw__dsk}')
    else:
        nmwg__hwdhq = [f'arg{omugw__dsk}' for omugw__dsk, lez__olg in
            enumerate(agg_node.in_vars) if lez__olg is not None]
    flme__psnc = f"def agg_top({', '.join(nmwg__hwdhq)}):\n"
    wuycq__ayaak = []
    if agg_node.is_in_table_format:
        wuycq__ayaak = agg_node.in_key_inds + [knbb__gyu for knbb__gyu,
            idxan__ewdbv in agg_node.gb_info_out.values() if knbb__gyu is not
            None]
        if agg_node.input_has_index:
            wuycq__ayaak.append(agg_node.n_in_cols - 1)
        urrhg__okkl = ',' if len(agg_node.in_vars) - 1 == 1 else ''
        jgic__fuhs = []
        for omugw__dsk in range(agg_node.n_in_table_arrays, agg_node.n_in_cols
            ):
            if omugw__dsk in agg_node.dead_in_inds:
                jgic__fuhs.append('None')
            else:
                jgic__fuhs.append(f'arg{omugw__dsk}')
        mpu__qyrto = 'arg0' if agg_node.in_vars[0] is not None else 'None'
        flme__psnc += f"""    table = py_data_to_cpp_table({mpu__qyrto}, ({', '.join(jgic__fuhs)}{urrhg__okkl}), in_col_inds, {agg_node.n_in_table_arrays})
"""
    else:
        omjy__abxuu = [f'arg{omugw__dsk}' for omugw__dsk in agg_node.
            in_key_inds]
        hytkz__iet = [f'arg{knbb__gyu}' for knbb__gyu, idxan__ewdbv in
            agg_node.gb_info_out.values() if knbb__gyu is not None]
        ull__ozxmb = omjy__abxuu + hytkz__iet
        if agg_node.input_has_index:
            ull__ozxmb.append(f'arg{len(agg_node.in_vars) - 1}')
        flme__psnc += '    info_list = [{}]\n'.format(', '.join(
            f'array_to_info({blzhq__tmgtd})' for blzhq__tmgtd in ull__ozxmb))
        flme__psnc += '    table = arr_info_list_to_table(info_list)\n'
    do_combine = parallel
    allfuncs = []
    nsuej__sffe = []
    func_idx_to_in_col = []
    okmow__jxja = []
    jgl__cahx = False
    uarl__ikb = 1
    prob__lxwe = -1
    crani__xgh = 0
    tubm__nhgr = 0
    cjrsb__dvz = [func for idxan__ewdbv, func in agg_node.gb_info_out.values()]
    for gotlk__xnty, func in enumerate(cjrsb__dvz):
        nsuej__sffe.append(len(allfuncs))
        if func.ftype in {'median', 'nunique', 'ngroup'}:
            do_combine = False
        if func.ftype in list_cumulative:
            crani__xgh += 1
        if hasattr(func, 'skipdropna'):
            jgl__cahx = func.skipdropna
        if func.ftype == 'shift':
            uarl__ikb = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            tubm__nhgr = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            prob__lxwe = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(gotlk__xnty)
        if func.ftype == 'udf':
            okmow__jxja.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            okmow__jxja.append(0)
            do_combine = False
    nsuej__sffe.append(len(allfuncs))
    assert len(agg_node.gb_info_out) == len(allfuncs
        ), 'invalid number of groupby outputs'
    if crani__xgh > 0:
        if crani__xgh != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    jdfin__hyg = []
    if udf_func_struct is not None:
        vnb__xngs = next_label()
        if udf_func_struct.regular_udfs:
            ljchd__ynrji = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            ozdl__tmca = numba.cfunc(ljchd__ynrji, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs, do_combine,
                func_idx_to_in_col, vnb__xngs))
            axrn__pjnek = numba.cfunc(ljchd__ynrji, nopython=True)(
                gen_combine_cb(udf_func_struct, allfuncs, n_keys, vnb__xngs))
            sqy__pns = numba.cfunc('void(voidptr)', nopython=True)(gen_eval_cb
                (udf_func_struct, allfuncs, n_keys, func_out_types, vnb__xngs))
            udf_func_struct.set_regular_cfuncs(ozdl__tmca, axrn__pjnek,
                sqy__pns)
            for nifx__ozo in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[nifx__ozo.native_name] = nifx__ozo
                gb_agg_cfunc_addr[nifx__ozo.native_name] = nifx__ozo.address
        if udf_func_struct.general_udfs:
            hcv__chczx = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, func_out_types, func_idx_to_in_col,
                vnb__xngs)
            udf_func_struct.set_general_cfunc(hcv__chczx)
        csn__chlbl = (udf_func_struct.var_typs if udf_func_struct.
            regular_udfs else None)
        nyzva__get = 0
        omugw__dsk = 0
        for rzhb__crgbo, fmu__kwdnz in zip(agg_node.gb_info_out.keys(),
            allfuncs):
            if fmu__kwdnz.ftype in ('udf', 'gen_udf'):
                jdfin__hyg.append(out_col_typs[rzhb__crgbo])
                for ctkat__kvlg in range(nyzva__get, nyzva__get +
                    okmow__jxja[omugw__dsk]):
                    jdfin__hyg.append(dtype_to_array_type(csn__chlbl[
                        ctkat__kvlg]))
                nyzva__get += okmow__jxja[omugw__dsk]
                omugw__dsk += 1
        flme__psnc += f"""    dummy_table = create_dummy_table(({', '.join(f'udf_type{omugw__dsk}' for omugw__dsk in range(len(jdfin__hyg)))}{',' if len(jdfin__hyg) == 1 else ''}))
"""
        flme__psnc += f"""    udf_table_dummy = py_data_to_cpp_table(dummy_table, (), udf_dummy_col_inds, {len(jdfin__hyg)})
"""
        if udf_func_struct.regular_udfs:
            flme__psnc += (
                f"    add_agg_cfunc_sym(cpp_cb_update, '{ozdl__tmca.native_name}')\n"
                )
            flme__psnc += (
                f"    add_agg_cfunc_sym(cpp_cb_combine, '{axrn__pjnek.native_name}')\n"
                )
            flme__psnc += (
                f"    add_agg_cfunc_sym(cpp_cb_eval, '{sqy__pns.native_name}')\n"
                )
            flme__psnc += (
                f"    cpp_cb_update_addr = get_agg_udf_addr('{ozdl__tmca.native_name}')\n"
                )
            flme__psnc += f"""    cpp_cb_combine_addr = get_agg_udf_addr('{axrn__pjnek.native_name}')
"""
            flme__psnc += (
                f"    cpp_cb_eval_addr = get_agg_udf_addr('{sqy__pns.native_name}')\n"
                )
        else:
            flme__psnc += '    cpp_cb_update_addr = 0\n'
            flme__psnc += '    cpp_cb_combine_addr = 0\n'
            flme__psnc += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            nifx__ozo = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[nifx__ozo.native_name] = nifx__ozo
            gb_agg_cfunc_addr[nifx__ozo.native_name] = nifx__ozo.address
            flme__psnc += (
                f"    add_agg_cfunc_sym(cpp_cb_general, '{nifx__ozo.native_name}')\n"
                )
            flme__psnc += (
                f"    cpp_cb_general_addr = get_agg_udf_addr('{nifx__ozo.native_name}')\n"
                )
        else:
            flme__psnc += '    cpp_cb_general_addr = 0\n'
    else:
        flme__psnc += """    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])
"""
        flme__psnc += '    cpp_cb_update_addr = 0\n'
        flme__psnc += '    cpp_cb_combine_addr = 0\n'
        flme__psnc += '    cpp_cb_eval_addr = 0\n'
        flme__psnc += '    cpp_cb_general_addr = 0\n'
    flme__psnc += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(
        ', '.join([str(supported_agg_funcs.index(fmu__kwdnz.ftype)) for
        fmu__kwdnz in allfuncs] + ['0']))
    flme__psnc += (
        f'    func_offsets = np.array({str(nsuej__sffe)}, dtype=np.int32)\n')
    if len(okmow__jxja) > 0:
        flme__psnc += (
            f'    udf_ncols = np.array({str(okmow__jxja)}, dtype=np.int32)\n')
    else:
        flme__psnc += '    udf_ncols = np.array([0], np.int32)\n'
    flme__psnc += '    total_rows_np = np.array([0], dtype=np.int64)\n'
    flme__psnc += f"""    out_table = groupby_and_aggregate(table, {n_keys}, {agg_node.input_has_index}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {parallel}, {jgl__cahx}, {uarl__ikb}, {tubm__nhgr}, {prob__lxwe}, {agg_node.return_key}, {agg_node.same_index}, {agg_node.dropna}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy, total_rows_np.ctypes)
"""
    nlul__jqzg = []
    ncvzd__kvp = 0
    if agg_node.return_key:
        gvn__nzyq = 0 if isinstance(agg_node.out_type.index, bodo.
            RangeIndexType) else agg_node.n_out_cols - len(agg_node.in_key_inds
            ) - 1
        for omugw__dsk in range(n_keys):
            jbpp__tpzq = gvn__nzyq + omugw__dsk
            nlul__jqzg.append(jbpp__tpzq if jbpp__tpzq not in agg_node.
                dead_out_inds else -1)
            ncvzd__kvp += 1
    for rzhb__crgbo in agg_node.gb_info_out.keys():
        nlul__jqzg.append(rzhb__crgbo)
        ncvzd__kvp += 1
    rdzux__bpgb = False
    if agg_node.same_index:
        if agg_node.out_vars[-1] is not None:
            nlul__jqzg.append(agg_node.n_out_cols - 1)
        else:
            rdzux__bpgb = True
    urrhg__okkl = ',' if dxa__mus == 1 else ''
    iws__ihy = (
        f"({', '.join(f'out_type{omugw__dsk}' for omugw__dsk in range(dxa__mus))}{urrhg__okkl})"
        )
    woc__dkgq = []
    eboyg__bciej = []
    for omugw__dsk, t in enumerate(out_col_typs):
        if omugw__dsk not in agg_node.dead_out_inds and type_has_unknown_cats(t
            ):
            if omugw__dsk in agg_node.gb_info_out:
                knbb__gyu = agg_node.gb_info_out[omugw__dsk][0]
            else:
                assert agg_node.return_key, 'Internal error: groupby key output with unknown categoricals detected, but return_key is False'
                gogdj__gtdv = omugw__dsk - gvn__nzyq
                knbb__gyu = agg_node.in_key_inds[gogdj__gtdv]
            eboyg__bciej.append(omugw__dsk)
            if (agg_node.is_in_table_format and knbb__gyu < agg_node.
                n_in_table_arrays):
                woc__dkgq.append(f'get_table_data(arg0, {knbb__gyu})')
            else:
                woc__dkgq.append(f'arg{knbb__gyu}')
    urrhg__okkl = ',' if len(woc__dkgq) == 1 else ''
    flme__psnc += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {iws__ihy}, total_rows_np[0], {agg_node.n_out_table_arrays}, ({', '.join(woc__dkgq)}{urrhg__okkl}), unknown_cat_out_inds)
"""
    flme__psnc += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    flme__psnc += '    delete_table_decref_arrays(table)\n'
    flme__psnc += '    delete_table_decref_arrays(udf_table_dummy)\n'
    if agg_node.return_key:
        for omugw__dsk in range(n_keys):
            if nlul__jqzg[omugw__dsk] == -1:
                flme__psnc += (
                    f'    decref_table_array(out_table, {omugw__dsk})\n')
    if rdzux__bpgb:
        hnmd__xgpyi = len(agg_node.gb_info_out) + (n_keys if agg_node.
            return_key else 0)
        flme__psnc += f'    decref_table_array(out_table, {hnmd__xgpyi})\n'
    flme__psnc += '    delete_table(out_table)\n'
    flme__psnc += '    ev_clean.finalize()\n'
    flme__psnc += '    return out_data\n'
    yks__kmjiz = {f'out_type{omugw__dsk}': out_var_types[omugw__dsk] for
        omugw__dsk in range(dxa__mus)}
    yks__kmjiz['out_col_inds'] = MetaType(tuple(nlul__jqzg))
    yks__kmjiz['in_col_inds'] = MetaType(tuple(wuycq__ayaak))
    yks__kmjiz['cpp_table_to_py_data'] = cpp_table_to_py_data
    yks__kmjiz['py_data_to_cpp_table'] = py_data_to_cpp_table
    yks__kmjiz.update({f'udf_type{omugw__dsk}': t for omugw__dsk, t in
        enumerate(jdfin__hyg)})
    yks__kmjiz['udf_dummy_col_inds'] = MetaType(tuple(range(len(jdfin__hyg))))
    yks__kmjiz['create_dummy_table'] = create_dummy_table
    yks__kmjiz['unknown_cat_out_inds'] = MetaType(tuple(eboyg__bciej))
    yks__kmjiz['get_table_data'] = bodo.hiframes.table.get_table_data
    return flme__psnc, yks__kmjiz


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def create_dummy_table(data_types):
    yven__sav = tuple(unwrap_typeref(data_types.types[omugw__dsk]) for
        omugw__dsk in range(len(data_types.types)))
    jypw__rxypr = bodo.TableType(yven__sav)
    yks__kmjiz = {'table_type': jypw__rxypr}
    flme__psnc = 'def impl(data_types):\n'
    flme__psnc += '  py_table = init_table(table_type, False)\n'
    flme__psnc += '  py_table = set_table_len(py_table, 1)\n'
    for gguff__zhym, cir__niijl in jypw__rxypr.type_to_blk.items():
        yks__kmjiz[f'typ_list_{cir__niijl}'] = types.List(gguff__zhym)
        yks__kmjiz[f'typ_{cir__niijl}'] = gguff__zhym
        bzkmi__rra = len(jypw__rxypr.block_to_arr_ind[cir__niijl])
        flme__psnc += f"""  arr_list_{cir__niijl} = alloc_list_like(typ_list_{cir__niijl}, {bzkmi__rra}, False)
"""
        flme__psnc += f'  for i in range(len(arr_list_{cir__niijl})):\n'
        flme__psnc += (
            f'    arr_list_{cir__niijl}[i] = alloc_type(1, typ_{cir__niijl}, (-1,))\n'
            )
        flme__psnc += f"""  py_table = set_table_block(py_table, arr_list_{cir__niijl}, {cir__niijl})
"""
    flme__psnc += '  return py_table\n'
    yks__kmjiz.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len, 'alloc_type':
        bodo.utils.utils.alloc_type})
    agx__wmzwa = {}
    exec(flme__psnc, yks__kmjiz, agx__wmzwa)
    return agx__wmzwa['impl']


def agg_table_column_use(agg_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not agg_node.is_in_table_format or agg_node.in_vars[0] is None:
        return
    ypgrn__gecxf = agg_node.in_vars[0].name
    rjucw__jxbr, hsylj__vuxi, asw__flx = block_use_map[ypgrn__gecxf]
    if hsylj__vuxi or asw__flx:
        return
    if agg_node.is_output_table and agg_node.out_vars[0] is not None:
        xumap__ccv, wyask__zhkmv, djjdi__wms = _compute_table_column_uses(
            agg_node.out_vars[0].name, table_col_use_map, equiv_vars)
        if wyask__zhkmv or djjdi__wms:
            xumap__ccv = set(range(agg_node.n_out_table_arrays))
    else:
        xumap__ccv = {}
        if agg_node.out_vars[0
            ] is not None and 0 not in agg_node.dead_out_inds:
            xumap__ccv = {0}
    xiyq__rgd = set(omugw__dsk for omugw__dsk in agg_node.in_key_inds if 
        omugw__dsk < agg_node.n_in_table_arrays)
    hab__inan = set(agg_node.gb_info_out[omugw__dsk][0] for omugw__dsk in
        xumap__ccv if omugw__dsk in agg_node.gb_info_out and agg_node.
        gb_info_out[omugw__dsk][0] is not None)
    hab__inan |= xiyq__rgd | rjucw__jxbr
    umk__rmz = len(set(range(agg_node.n_in_table_arrays)) - hab__inan) == 0
    block_use_map[ypgrn__gecxf] = hab__inan, umk__rmz, False


ir_extension_table_column_use[Aggregate] = agg_table_column_use


def agg_remove_dead_column(agg_node, column_live_map, equiv_vars, typemap):
    if not agg_node.is_output_table or agg_node.out_vars[0] is None:
        return False
    tfrg__ndhpa = agg_node.n_out_table_arrays
    frwpz__pivv = agg_node.out_vars[0].name
    fdpu__zfmd = _find_used_columns(frwpz__pivv, tfrg__ndhpa,
        column_live_map, equiv_vars)
    if fdpu__zfmd is None:
        return False
    wzmw__khci = set(range(tfrg__ndhpa)) - fdpu__zfmd
    sunx__oxx = len(wzmw__khci - agg_node.dead_out_inds) != 0
    if sunx__oxx:
        agg_node.dead_out_inds.update(wzmw__khci)
        agg_node.update_dead_col_info()
    return sunx__oxx


remove_dead_column_extensions[Aggregate] = agg_remove_dead_column


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for weg__buyqr in block.body:
            if is_call_assign(weg__buyqr) and find_callname(f_ir,
                weg__buyqr.value) == ('len', 'builtins'
                ) and weg__buyqr.value.args[0].name == f_ir.arg_names[0]:
                zkl__qyl = get_definition(f_ir, weg__buyqr.value.func)
                zkl__qyl.name = 'dummy_agg_count'
                zkl__qyl.value = dummy_agg_count
    fwf__khm = get_name_var_table(f_ir.blocks)
    gbzf__edqqb = {}
    for name, idxan__ewdbv in fwf__khm.items():
        gbzf__edqqb[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, gbzf__edqqb)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    qlfha__czw = numba.core.compiler.Flags()
    qlfha__czw.nrt = True
    mnm__ldsgy = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, qlfha__czw)
    mnm__ldsgy.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, vhq__atw, calltypes, idxan__ewdbv = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    qtf__xvfbx = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    rurrh__qvrw = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    zly__yxs = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    ejyi__omv = zly__yxs(typemap, calltypes)
    pm = rurrh__qvrw(typingctx, targetctx, None, f_ir, typemap, vhq__atw,
        calltypes, ejyi__omv, {}, qlfha__czw, None)
    dwcos__lvu = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = rurrh__qvrw(typingctx, targetctx, None, f_ir, typemap, vhq__atw,
        calltypes, ejyi__omv, {}, qlfha__czw, dwcos__lvu)
    macck__ottvn = numba.core.typed_passes.InlineOverloads()
    macck__ottvn.run_pass(pm)
    jxd__vyg = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    jxd__vyg.run()
    for block in f_ir.blocks.values():
        for weg__buyqr in block.body:
            if is_assign(weg__buyqr) and isinstance(weg__buyqr.value, (ir.
                Arg, ir.Var)) and isinstance(typemap[weg__buyqr.target.name
                ], SeriesType):
                gguff__zhym = typemap.pop(weg__buyqr.target.name)
                typemap[weg__buyqr.target.name] = gguff__zhym.data
            if is_call_assign(weg__buyqr) and find_callname(f_ir,
                weg__buyqr.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[weg__buyqr.target.name].remove(weg__buyqr
                    .value)
                weg__buyqr.value = weg__buyqr.value.args[0]
                f_ir._definitions[weg__buyqr.target.name].append(weg__buyqr
                    .value)
            if is_call_assign(weg__buyqr) and find_callname(f_ir,
                weg__buyqr.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[weg__buyqr.target.name].remove(weg__buyqr
                    .value)
                weg__buyqr.value = ir.Const(False, weg__buyqr.loc)
                f_ir._definitions[weg__buyqr.target.name].append(weg__buyqr
                    .value)
            if is_call_assign(weg__buyqr) and find_callname(f_ir,
                weg__buyqr.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[weg__buyqr.target.name].remove(weg__buyqr
                    .value)
                weg__buyqr.value = ir.Const(False, weg__buyqr.loc)
                f_ir._definitions[weg__buyqr.target.name].append(weg__buyqr
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    lxl__wxoyc = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, qtf__xvfbx)
    lxl__wxoyc.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    yndm__gga = numba.core.compiler.StateDict()
    yndm__gga.func_ir = f_ir
    yndm__gga.typemap = typemap
    yndm__gga.calltypes = calltypes
    yndm__gga.typingctx = typingctx
    yndm__gga.targetctx = targetctx
    yndm__gga.return_type = vhq__atw
    numba.core.rewrites.rewrite_registry.apply('after-inference', yndm__gga)
    lbpi__glxl = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        vhq__atw, typingctx, targetctx, qtf__xvfbx, qlfha__czw, {})
    lbpi__glxl.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            jtyeh__lmubp = ctypes.pythonapi.PyCell_Get
            jtyeh__lmubp.restype = ctypes.py_object
            jtyeh__lmubp.argtypes = ctypes.py_object,
            wpi__bij = tuple(jtyeh__lmubp(lqpc__fggys) for lqpc__fggys in
                closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            wpi__bij = closure.items
        assert len(code.co_freevars) == len(wpi__bij)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, wpi__bij)


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
        gutl__sthwo = SeriesType(in_col_typ.dtype, to_str_arr_if_dict_array
            (in_col_typ), None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (gutl__sthwo,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        wus__dyz, arr_var = _rm_arg_agg_block(block, pm.typemap)
        zfn__ahvsa = -1
        for omugw__dsk, weg__buyqr in enumerate(wus__dyz):
            if isinstance(weg__buyqr, numba.parfors.parfor.Parfor):
                assert zfn__ahvsa == -1, 'only one parfor for aggregation function'
                zfn__ahvsa = omugw__dsk
        parfor = None
        if zfn__ahvsa != -1:
            parfor = wus__dyz[zfn__ahvsa]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = wus__dyz[:zfn__ahvsa] + parfor.init_block.body
        eval_nodes = wus__dyz[zfn__ahvsa + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for weg__buyqr in init_nodes:
            if is_assign(weg__buyqr) and weg__buyqr.target.name in redvars:
                ind = redvars.index(weg__buyqr.target.name)
                reduce_vars[ind] = weg__buyqr.target
        var_types = [pm.typemap[lez__olg] for lez__olg in redvars]
        szlwr__mpi = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        yabk__yymk = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        ewnbb__dcdfu = gen_eval_func(f_ir, eval_nodes, reduce_vars,
            var_types, pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(ewnbb__dcdfu)
        self.all_update_funcs.append(yabk__yymk)
        self.all_combine_funcs.append(szlwr__mpi)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        saby__dukrm = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        twmk__amu = gen_all_update_func(self.all_update_funcs, self.
            in_col_types, self.redvar_offsets)
        tyex__xjcpw = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.targetctx)
        dai__rfkqo = gen_all_eval_func(self.all_eval_funcs, self.redvar_offsets
            )
        return (self.all_vartypes, saby__dukrm, twmk__amu, tyex__xjcpw,
            dai__rfkqo)


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
    vers__zqlie = []
    for t, fmu__kwdnz in zip(in_col_types, agg_func):
        vers__zqlie.append((t, fmu__kwdnz))
    yfh__grtl = RegularUDFGenerator(in_col_types, typingctx, targetctx)
    deuc__zmom = GeneralUDFGenerator()
    for in_col_typ, func in vers__zqlie:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            yfh__grtl.add_udf(in_col_typ, func)
        except:
            deuc__zmom.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = yfh__grtl.gen_all_func()
    general_udf_funcs = deuc__zmom.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    adl__divs = compute_use_defs(parfor.loop_body)
    vkn__wokr = set()
    for vxk__hinic in adl__divs.usemap.values():
        vkn__wokr |= vxk__hinic
    yed__jpch = set()
    for vxk__hinic in adl__divs.defmap.values():
        yed__jpch |= vxk__hinic
    ffwg__ijc = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    ffwg__ijc.body = eval_nodes
    xcpm__puea = compute_use_defs({(0): ffwg__ijc})
    sqtvf__hbobg = xcpm__puea.usemap[0]
    bngn__quiog = set()
    laoo__oqt = []
    bfabu__gsmia = []
    for weg__buyqr in reversed(init_nodes):
        ajt__ozl = {lez__olg.name for lez__olg in weg__buyqr.list_vars()}
        if is_assign(weg__buyqr):
            lez__olg = weg__buyqr.target.name
            ajt__ozl.remove(lez__olg)
            if (lez__olg in vkn__wokr and lez__olg not in bngn__quiog and 
                lez__olg not in sqtvf__hbobg and lez__olg not in yed__jpch):
                bfabu__gsmia.append(weg__buyqr)
                vkn__wokr |= ajt__ozl
                yed__jpch.add(lez__olg)
                continue
        bngn__quiog |= ajt__ozl
        laoo__oqt.append(weg__buyqr)
    bfabu__gsmia.reverse()
    laoo__oqt.reverse()
    azhs__imw = min(parfor.loop_body.keys())
    zagrb__mrim = parfor.loop_body[azhs__imw]
    zagrb__mrim.body = bfabu__gsmia + zagrb__mrim.body
    return laoo__oqt


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    ounq__coop = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    bjp__uuf = set()
    fxs__gav = []
    for weg__buyqr in init_nodes:
        if is_assign(weg__buyqr) and isinstance(weg__buyqr.value, ir.Global
            ) and isinstance(weg__buyqr.value.value, pytypes.FunctionType
            ) and weg__buyqr.value.value in ounq__coop:
            bjp__uuf.add(weg__buyqr.target.name)
        elif is_call_assign(weg__buyqr
            ) and weg__buyqr.value.func.name in bjp__uuf:
            pass
        else:
            fxs__gav.append(weg__buyqr)
    init_nodes = fxs__gav
    iiy__ryrg = types.Tuple(var_types)
    rnq__pbkx = lambda : None
    f_ir = compile_to_numba_ir(rnq__pbkx, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    ggrs__gisq = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    lbb__ymzha = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc),
        ggrs__gisq, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [lbb__ymzha] + block.body
    block.body[-2].value.value = ggrs__gisq
    yalcp__mazx = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        iiy__ryrg, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    izff__fke = numba.core.target_extension.dispatcher_registry[cpu_target](
        rnq__pbkx)
    izff__fke.add_overload(yalcp__mazx)
    return izff__fke


def gen_all_update_func(update_funcs, in_col_types, redvar_offsets):
    oknxn__pmcmt = len(update_funcs)
    wmskg__bty = len(in_col_types)
    flme__psnc = 'def update_all_f(redvar_arrs, data_in, w_ind, i):\n'
    for ctkat__kvlg in range(oknxn__pmcmt):
        jztny__drg = ', '.join(['redvar_arrs[{}][w_ind]'.format(omugw__dsk) for
            omugw__dsk in range(redvar_offsets[ctkat__kvlg], redvar_offsets
            [ctkat__kvlg + 1])])
        if jztny__drg:
            flme__psnc += ('  {} = update_vars_{}({},  data_in[{}][i])\n'.
                format(jztny__drg, ctkat__kvlg, jztny__drg, 0 if wmskg__bty ==
                1 else ctkat__kvlg))
    flme__psnc += '  return\n'
    nesq__mfvw = {}
    for omugw__dsk, fmu__kwdnz in enumerate(update_funcs):
        nesq__mfvw['update_vars_{}'.format(omugw__dsk)] = fmu__kwdnz
    agx__wmzwa = {}
    exec(flme__psnc, nesq__mfvw, agx__wmzwa)
    ysgp__tjzc = agx__wmzwa['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(ysgp__tjzc)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx):
    jubdh__idga = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    arg_typs = jubdh__idga, jubdh__idga, types.intp, types.intp
    xmff__snhk = len(redvar_offsets) - 1
    flme__psnc = 'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i):\n'
    for ctkat__kvlg in range(xmff__snhk):
        jztny__drg = ', '.join(['redvar_arrs[{}][w_ind]'.format(omugw__dsk) for
            omugw__dsk in range(redvar_offsets[ctkat__kvlg], redvar_offsets
            [ctkat__kvlg + 1])])
        zhpw__cexkt = ', '.join(['recv_arrs[{}][i]'.format(omugw__dsk) for
            omugw__dsk in range(redvar_offsets[ctkat__kvlg], redvar_offsets
            [ctkat__kvlg + 1])])
        if zhpw__cexkt:
            flme__psnc += '  {} = combine_vars_{}({}, {})\n'.format(jztny__drg,
                ctkat__kvlg, jztny__drg, zhpw__cexkt)
    flme__psnc += '  return\n'
    nesq__mfvw = {}
    for omugw__dsk, fmu__kwdnz in enumerate(combine_funcs):
        nesq__mfvw['combine_vars_{}'.format(omugw__dsk)] = fmu__kwdnz
    agx__wmzwa = {}
    exec(flme__psnc, nesq__mfvw, agx__wmzwa)
    jnbt__ozie = agx__wmzwa['combine_all_f']
    f_ir = compile_to_numba_ir(jnbt__ozie, nesq__mfvw)
    tyex__xjcpw = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    izff__fke = numba.core.target_extension.dispatcher_registry[cpu_target](
        jnbt__ozie)
    izff__fke.add_overload(tyex__xjcpw)
    return izff__fke


def gen_all_eval_func(eval_funcs, redvar_offsets):
    xmff__snhk = len(redvar_offsets) - 1
    flme__psnc = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    for ctkat__kvlg in range(xmff__snhk):
        jztny__drg = ', '.join(['redvar_arrs[{}][j]'.format(omugw__dsk) for
            omugw__dsk in range(redvar_offsets[ctkat__kvlg], redvar_offsets
            [ctkat__kvlg + 1])])
        flme__psnc += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
            ctkat__kvlg, ctkat__kvlg, jztny__drg)
    flme__psnc += '  return\n'
    nesq__mfvw = {}
    for omugw__dsk, fmu__kwdnz in enumerate(eval_funcs):
        nesq__mfvw['eval_vars_{}'.format(omugw__dsk)] = fmu__kwdnz
    agx__wmzwa = {}
    exec(flme__psnc, nesq__mfvw, agx__wmzwa)
    vlmck__kkaiq = agx__wmzwa['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(vlmck__kkaiq)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    djlbb__urtw = len(var_types)
    sbriz__pqqh = [f'in{omugw__dsk}' for omugw__dsk in range(djlbb__urtw)]
    iiy__ryrg = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    ftjnu__mcgzi = iiy__ryrg(0)
    flme__psnc = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        sbriz__pqqh))
    agx__wmzwa = {}
    exec(flme__psnc, {'_zero': ftjnu__mcgzi}, agx__wmzwa)
    lvvme__ywws = agx__wmzwa['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(lvvme__ywws, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': ftjnu__mcgzi}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    tyska__kqdy = []
    for omugw__dsk, lez__olg in enumerate(reduce_vars):
        tyska__kqdy.append(ir.Assign(block.body[omugw__dsk].target,
            lez__olg, lez__olg.loc))
        for jksqm__znji in lez__olg.versioned_names:
            tyska__kqdy.append(ir.Assign(lez__olg, ir.Var(lez__olg.scope,
                jksqm__znji, lez__olg.loc), lez__olg.loc))
    block.body = block.body[:djlbb__urtw] + tyska__kqdy + eval_nodes
    ewnbb__dcdfu = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        iiy__ryrg, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    izff__fke = numba.core.target_extension.dispatcher_registry[cpu_target](
        lvvme__ywws)
    izff__fke.add_overload(ewnbb__dcdfu)
    return izff__fke


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    djlbb__urtw = len(redvars)
    vnya__fshk = [f'v{omugw__dsk}' for omugw__dsk in range(djlbb__urtw)]
    sbriz__pqqh = [f'in{omugw__dsk}' for omugw__dsk in range(djlbb__urtw)]
    flme__psnc = 'def agg_combine({}):\n'.format(', '.join(vnya__fshk +
        sbriz__pqqh))
    nhox__aejy = wrap_parfor_blocks(parfor)
    szy__ahxq = find_topo_order(nhox__aejy)
    szy__ahxq = szy__ahxq[1:]
    unwrap_parfor_blocks(parfor)
    enc__gnvo = {}
    qocwy__cirsx = []
    for xqrfa__smznk in szy__ahxq:
        tie__ndcfd = parfor.loop_body[xqrfa__smznk]
        for weg__buyqr in tie__ndcfd.body:
            if is_assign(weg__buyqr) and weg__buyqr.target.name in redvars:
                vofca__irio = weg__buyqr.target.name
                ind = redvars.index(vofca__irio)
                if ind in qocwy__cirsx:
                    continue
                if len(f_ir._definitions[vofca__irio]) == 2:
                    var_def = f_ir._definitions[vofca__irio][0]
                    flme__psnc += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[vofca__irio][1]
                    flme__psnc += _match_reduce_def(var_def, f_ir, ind)
    flme__psnc += '    return {}'.format(', '.join(['v{}'.format(omugw__dsk
        ) for omugw__dsk in range(djlbb__urtw)]))
    agx__wmzwa = {}
    exec(flme__psnc, {}, agx__wmzwa)
    xxjjq__hfl = agx__wmzwa['agg_combine']
    arg_typs = tuple(2 * var_types)
    nesq__mfvw = {'numba': numba, 'bodo': bodo, 'np': np}
    nesq__mfvw.update(enc__gnvo)
    f_ir = compile_to_numba_ir(xxjjq__hfl, nesq__mfvw, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    iiy__ryrg = pm.typemap[block.body[-1].value.name]
    szlwr__mpi = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        iiy__ryrg, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    izff__fke = numba.core.target_extension.dispatcher_registry[cpu_target](
        xxjjq__hfl)
    izff__fke.add_overload(szlwr__mpi)
    return izff__fke


def _match_reduce_def(var_def, f_ir, ind):
    flme__psnc = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        flme__psnc = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        exjxn__igkc = guard(find_callname, f_ir, var_def)
        if exjxn__igkc == ('min', 'builtins'):
            flme__psnc = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if exjxn__igkc == ('max', 'builtins'):
            flme__psnc = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return flme__psnc


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    djlbb__urtw = len(redvars)
    ucg__husm = 1
    in_vars = []
    for omugw__dsk in range(ucg__husm):
        rvze__xseg = ir.Var(arr_var.scope, f'$input{omugw__dsk}', arr_var.loc)
        in_vars.append(rvze__xseg)
    rjzmr__ifp = parfor.loop_nests[0].index_variable
    yjong__wwv = [0] * djlbb__urtw
    for tie__ndcfd in parfor.loop_body.values():
        zjwko__chm = []
        for weg__buyqr in tie__ndcfd.body:
            if is_var_assign(weg__buyqr
                ) and weg__buyqr.value.name == rjzmr__ifp.name:
                continue
            if is_getitem(weg__buyqr
                ) and weg__buyqr.value.value.name == arr_var.name:
                weg__buyqr.value = in_vars[0]
            if is_call_assign(weg__buyqr) and guard(find_callname, pm.
                func_ir, weg__buyqr.value) == ('isna',
                'bodo.libs.array_kernels') and weg__buyqr.value.args[0
                ].name == arr_var.name:
                weg__buyqr.value = ir.Const(False, weg__buyqr.target.loc)
            if is_assign(weg__buyqr) and weg__buyqr.target.name in redvars:
                ind = redvars.index(weg__buyqr.target.name)
                yjong__wwv[ind] = weg__buyqr.target
            zjwko__chm.append(weg__buyqr)
        tie__ndcfd.body = zjwko__chm
    vnya__fshk = ['v{}'.format(omugw__dsk) for omugw__dsk in range(djlbb__urtw)
        ]
    sbriz__pqqh = ['in{}'.format(omugw__dsk) for omugw__dsk in range(ucg__husm)
        ]
    flme__psnc = 'def agg_update({}):\n'.format(', '.join(vnya__fshk +
        sbriz__pqqh))
    flme__psnc += '    __update_redvars()\n'
    flme__psnc += '    return {}'.format(', '.join(['v{}'.format(omugw__dsk
        ) for omugw__dsk in range(djlbb__urtw)]))
    agx__wmzwa = {}
    exec(flme__psnc, {}, agx__wmzwa)
    xhjd__lzdc = agx__wmzwa['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * ucg__husm)
    f_ir = compile_to_numba_ir(xhjd__lzdc, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    qjedd__snye = f_ir.blocks.popitem()[1].body
    iiy__ryrg = pm.typemap[qjedd__snye[-1].value.name]
    nhox__aejy = wrap_parfor_blocks(parfor)
    szy__ahxq = find_topo_order(nhox__aejy)
    szy__ahxq = szy__ahxq[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    zagrb__mrim = f_ir.blocks[szy__ahxq[0]]
    xwjzb__rhsru = f_ir.blocks[szy__ahxq[-1]]
    kqwt__talm = qjedd__snye[:djlbb__urtw + ucg__husm]
    if djlbb__urtw > 1:
        hgse__ylpvx = qjedd__snye[-3:]
        assert is_assign(hgse__ylpvx[0]) and isinstance(hgse__ylpvx[0].
            value, ir.Expr) and hgse__ylpvx[0].value.op == 'build_tuple'
    else:
        hgse__ylpvx = qjedd__snye[-2:]
    for omugw__dsk in range(djlbb__urtw):
        ztj__pukty = qjedd__snye[omugw__dsk].target
        gonjh__zqk = ir.Assign(ztj__pukty, yjong__wwv[omugw__dsk],
            ztj__pukty.loc)
        kqwt__talm.append(gonjh__zqk)
    for omugw__dsk in range(djlbb__urtw, djlbb__urtw + ucg__husm):
        ztj__pukty = qjedd__snye[omugw__dsk].target
        gonjh__zqk = ir.Assign(ztj__pukty, in_vars[omugw__dsk - djlbb__urtw
            ], ztj__pukty.loc)
        kqwt__talm.append(gonjh__zqk)
    zagrb__mrim.body = kqwt__talm + zagrb__mrim.body
    yes__boih = []
    for omugw__dsk in range(djlbb__urtw):
        ztj__pukty = qjedd__snye[omugw__dsk].target
        gonjh__zqk = ir.Assign(yjong__wwv[omugw__dsk], ztj__pukty,
            ztj__pukty.loc)
        yes__boih.append(gonjh__zqk)
    xwjzb__rhsru.body += yes__boih + hgse__ylpvx
    olwgj__rxf = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        iiy__ryrg, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    izff__fke = numba.core.target_extension.dispatcher_registry[cpu_target](
        xhjd__lzdc)
    izff__fke.add_overload(olwgj__rxf)
    return izff__fke


def _rm_arg_agg_block(block, typemap):
    wus__dyz = []
    arr_var = None
    for omugw__dsk, weg__buyqr in enumerate(block.body):
        if is_assign(weg__buyqr) and isinstance(weg__buyqr.value, ir.Arg):
            arr_var = weg__buyqr.target
            fljqy__vfq = typemap[arr_var.name]
            if not isinstance(fljqy__vfq, types.ArrayCompatible):
                wus__dyz += block.body[omugw__dsk + 1:]
                break
            yluxk__mua = block.body[omugw__dsk + 1]
            assert is_assign(yluxk__mua) and isinstance(yluxk__mua.value,
                ir.Expr
                ) and yluxk__mua.value.op == 'getattr' and yluxk__mua.value.attr == 'shape' and yluxk__mua.value.value.name == arr_var.name
            fio__vzfhd = yluxk__mua.target
            ndqa__ncx = block.body[omugw__dsk + 2]
            assert is_assign(ndqa__ncx) and isinstance(ndqa__ncx.value, ir.Expr
                ) and ndqa__ncx.value.op == 'static_getitem' and ndqa__ncx.value.value.name == fio__vzfhd.name
            wus__dyz += block.body[omugw__dsk + 3:]
            break
        wus__dyz.append(weg__buyqr)
    return wus__dyz, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    nhox__aejy = wrap_parfor_blocks(parfor)
    szy__ahxq = find_topo_order(nhox__aejy)
    szy__ahxq = szy__ahxq[1:]
    unwrap_parfor_blocks(parfor)
    for xqrfa__smznk in reversed(szy__ahxq):
        for weg__buyqr in reversed(parfor.loop_body[xqrfa__smznk].body):
            if isinstance(weg__buyqr, ir.Assign) and (weg__buyqr.target.
                name in parfor_params or weg__buyqr.target.name in var_to_param
                ):
                bvlm__luosn = weg__buyqr.target.name
                rhs = weg__buyqr.value
                wbz__rkojq = (bvlm__luosn if bvlm__luosn in parfor_params else
                    var_to_param[bvlm__luosn])
                pbx__ukiyy = []
                if isinstance(rhs, ir.Var):
                    pbx__ukiyy = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    pbx__ukiyy = [lez__olg.name for lez__olg in weg__buyqr.
                        value.list_vars()]
                param_uses[wbz__rkojq].extend(pbx__ukiyy)
                for lez__olg in pbx__ukiyy:
                    var_to_param[lez__olg] = wbz__rkojq
            if isinstance(weg__buyqr, Parfor):
                get_parfor_reductions(weg__buyqr, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for zbget__opsq, pbx__ukiyy in param_uses.items():
        if zbget__opsq in pbx__ukiyy and zbget__opsq not in reduce_varnames:
            reduce_varnames.append(zbget__opsq)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
