"""
Helper functions for transformations.
"""
import itertools
import math
import operator
import types as pytypes
from collections import namedtuple
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, types
from numba.core.ir_utils import GuardException, build_definitions, compile_to_numba_ir, compute_cfg_from_blocks, find_callname, find_const, get_definition, guard, is_setitem, mk_unique_var, replace_arg_nodes, require
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import fold_arguments
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoConstUpdatedError, BodoError, can_literalize_type, get_literal_value, get_overload_const_bool, get_overload_const_list, is_literal_type, is_overload_constant_bool
from bodo.utils.utils import is_array_typ, is_assign, is_call, is_expr
ReplaceFunc = namedtuple('ReplaceFunc', ['func', 'arg_types', 'args',
    'glbls', 'inline_bodo_calls', 'run_full_pipeline', 'pre_nodes'])
bodo_types_with_params = {'ArrayItemArrayType', 'CSRMatrixType',
    'CategoricalArrayType', 'CategoricalIndexType', 'DataFrameType',
    'DatetimeIndexType', 'Decimal128Type', 'DecimalArrayType',
    'IntegerArrayType', 'IntervalArrayType', 'IntervalIndexType', 'List',
    'MapArrayType', 'NumericIndexType', 'PDCategoricalDtype',
    'PeriodIndexType', 'RangeIndexType', 'SeriesType', 'StringIndexType',
    'BinaryIndexType', 'StructArrayType', 'TimedeltaIndexType',
    'TupleArrayType'}
container_update_method_names = ('clear', 'pop', 'popitem', 'update', 'add',
    'difference_update', 'discard', 'intersection_update', 'remove',
    'symmetric_difference_update', 'append', 'extend', 'insert', 'reverse',
    'sort')
no_side_effect_call_tuples = {(int,), (list,), (set,), (dict,), (min,), (
    max,), (abs,), (len,), (bool,), (str,), ('ceil', math), ('init_series',
    'pd_series_ext', 'hiframes', bodo), ('get_series_data', 'pd_series_ext',
    'hiframes', bodo), ('get_series_index', 'pd_series_ext', 'hiframes',
    bodo), ('get_series_name', 'pd_series_ext', 'hiframes', bodo), (
    'get_index_data', 'pd_index_ext', 'hiframes', bodo), ('get_index_name',
    'pd_index_ext', 'hiframes', bodo), ('init_binary_str_index',
    'pd_index_ext', 'hiframes', bodo), ('init_numeric_index',
    'pd_index_ext', 'hiframes', bodo), ('init_categorical_index',
    'pd_index_ext', 'hiframes', bodo), ('_dti_val_finalize', 'pd_index_ext',
    'hiframes', bodo), ('init_datetime_index', 'pd_index_ext', 'hiframes',
    bodo), ('init_timedelta_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_range_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_heter_index', 'pd_index_ext', 'hiframes', bodo), (
    'get_int_arr_data', 'int_arr_ext', 'libs', bodo), ('get_int_arr_bitmap',
    'int_arr_ext', 'libs', bodo), ('init_integer_array', 'int_arr_ext',
    'libs', bodo), ('alloc_int_array', 'int_arr_ext', 'libs', bodo), (
    'inplace_eq', 'str_arr_ext', 'libs', bodo), ('get_bool_arr_data',
    'bool_arr_ext', 'libs', bodo), ('get_bool_arr_bitmap', 'bool_arr_ext',
    'libs', bodo), ('init_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'alloc_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'datetime_date_arr_to_dt64_arr', 'pd_timestamp_ext', 'hiframes', bodo),
    (bodo.libs.bool_arr_ext.compute_or_body,), (bodo.libs.bool_arr_ext.
    compute_and_body,), ('alloc_datetime_date_array', 'datetime_date_ext',
    'hiframes', bodo), ('alloc_datetime_timedelta_array',
    'datetime_timedelta_ext', 'hiframes', bodo), ('cat_replace',
    'pd_categorical_ext', 'hiframes', bodo), ('init_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('alloc_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('get_categorical_arr_codes',
    'pd_categorical_ext', 'hiframes', bodo), ('_sum_handle_nan',
    'series_kernels', 'hiframes', bodo), ('_box_cat_val', 'series_kernels',
    'hiframes', bodo), ('_mean_handle_nan', 'series_kernels', 'hiframes',
    bodo), ('_var_handle_mincount', 'series_kernels', 'hiframes', bodo), (
    '_compute_var_nan_count_ddof', 'series_kernels', 'hiframes', bodo), (
    '_sem_handle_nan', 'series_kernels', 'hiframes', bodo), ('dist_return',
    'distributed_api', 'libs', bodo), ('rep_return', 'distributed_api',
    'libs', bodo), ('init_dataframe', 'pd_dataframe_ext', 'hiframes', bodo),
    ('get_dataframe_data', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_all_data', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_table', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_dataframe_column_names', 'pd_dataframe_ext', 'hiframes', bodo), (
    'get_table_data', 'table', 'hiframes', bodo), ('get_dataframe_index',
    'pd_dataframe_ext', 'hiframes', bodo), ('init_rolling',
    'pd_rolling_ext', 'hiframes', bodo), ('init_groupby', 'pd_groupby_ext',
    'hiframes', bodo), ('calc_nitems', 'array_kernels', 'libs', bodo), (
    'concat', 'array_kernels', 'libs', bodo), ('unique', 'array_kernels',
    'libs', bodo), ('nunique', 'array_kernels', 'libs', bodo), ('quantile',
    'array_kernels', 'libs', bodo), ('explode', 'array_kernels', 'libs',
    bodo), ('explode_no_index', 'array_kernels', 'libs', bodo), (
    'get_arr_lens', 'array_kernels', 'libs', bodo), (
    'str_arr_from_sequence', 'str_arr_ext', 'libs', bodo), (
    'get_str_arr_str_length', 'str_arr_ext', 'libs', bodo), (
    'parse_datetime_str', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_dt64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'dt64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'timedelta64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_timedelta64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'npy_datetimestruct_to_datetime', 'pd_timestamp_ext', 'hiframes', bodo),
    ('isna', 'array_kernels', 'libs', bodo), ('copy',), (
    'from_iterable_impl', 'typing', 'utils', bodo), ('chain', itertools), (
    'groupby',), ('rolling',), (pd.CategoricalDtype,), (bodo.hiframes.
    pd_categorical_ext.get_code_for_value,), ('asarray', np), ('int32', np),
    ('int64', np), ('float64', np), ('float32', np), ('bool_', np), ('full',
    np), ('round', np), ('isnan', np), ('isnat', np), ('arange', np), (
    'internal_prange', 'parfor', numba), ('internal_prange', 'parfor',
    'parfors', numba), ('empty_inferred', 'ndarray', 'unsafe', numba), (
    '_slice_span', 'unicode', numba), ('_normalize_slice', 'unicode', numba
    ), ('init_session_builder', 'pyspark_ext', 'libs', bodo), (
    'init_session', 'pyspark_ext', 'libs', bodo), ('init_spark_df',
    'pyspark_ext', 'libs', bodo), ('h5size', 'h5_api', 'io', bodo), (
    'pre_alloc_struct_array', 'struct_arr_ext', 'libs', bodo), (bodo.libs.
    struct_arr_ext.pre_alloc_struct_array,), ('pre_alloc_tuple_array',
    'tuple_arr_ext', 'libs', bodo), (bodo.libs.tuple_arr_ext.
    pre_alloc_tuple_array,), ('pre_alloc_array_item_array',
    'array_item_arr_ext', 'libs', bodo), (bodo.libs.array_item_arr_ext.
    pre_alloc_array_item_array,), ('dist_reduce', 'distributed_api', 'libs',
    bodo), (bodo.libs.distributed_api.dist_reduce,), (
    'pre_alloc_string_array', 'str_arr_ext', 'libs', bodo), (bodo.libs.
    str_arr_ext.pre_alloc_string_array,), ('pre_alloc_binary_array',
    'binary_arr_ext', 'libs', bodo), (bodo.libs.binary_arr_ext.
    pre_alloc_binary_array,), ('pre_alloc_map_array', 'map_arr_ext', 'libs',
    bodo), (bodo.libs.map_arr_ext.pre_alloc_map_array,), (
    'convert_dict_arr_to_int', 'dict_arr_ext', 'libs', bodo), (
    'cat_dict_str', 'dict_arr_ext', 'libs', bodo), ('str_replace',
    'dict_arr_ext', 'libs', bodo), ('dict_arr_eq', 'dict_arr_ext', 'libs',
    bodo), ('dict_arr_ne', 'dict_arr_ext', 'libs', bodo), ('str_startswith',
    'dict_arr_ext', 'libs', bodo), ('str_endswith', 'dict_arr_ext', 'libs',
    bodo), ('str_contains_non_regex', 'dict_arr_ext', 'libs', bodo), (
    'str_series_contains_regex', 'dict_arr_ext', 'libs', bodo), (
    'str_capitalize', 'dict_arr_ext', 'libs', bodo), ('str_lower',
    'dict_arr_ext', 'libs', bodo), ('str_swapcase', 'dict_arr_ext', 'libs',
    bodo), ('str_title', 'dict_arr_ext', 'libs', bodo), ('str_upper',
    'dict_arr_ext', 'libs', bodo), ('str_center', 'dict_arr_ext', 'libs',
    bodo), ('str_get', 'dict_arr_ext', 'libs', bodo), ('str_repeat_int',
    'dict_arr_ext', 'libs', bodo), ('str_lstrip', 'dict_arr_ext', 'libs',
    bodo), ('str_rstrip', 'dict_arr_ext', 'libs', bodo), ('str_strip',
    'dict_arr_ext', 'libs', bodo), ('str_zfill', 'dict_arr_ext', 'libs',
    bodo), ('str_ljust', 'dict_arr_ext', 'libs', bodo), ('str_rjust',
    'dict_arr_ext', 'libs', bodo), ('str_find', 'dict_arr_ext', 'libs',
    bodo), ('str_rfind', 'dict_arr_ext', 'libs', bodo), ('str_slice',
    'dict_arr_ext', 'libs', bodo), ('str_extract', 'dict_arr_ext', 'libs',
    bodo), ('str_extractall', 'dict_arr_ext', 'libs', bodo), (
    'str_extractall_multi', 'dict_arr_ext', 'libs', bodo), ('str_len',
    'dict_arr_ext', 'libs', bodo), ('str_count', 'dict_arr_ext', 'libs',
    bodo), ('str_isalnum', 'dict_arr_ext', 'libs', bodo), ('str_isalpha',
    'dict_arr_ext', 'libs', bodo), ('str_isdigit', 'dict_arr_ext', 'libs',
    bodo), ('str_isspace', 'dict_arr_ext', 'libs', bodo), ('str_islower',
    'dict_arr_ext', 'libs', bodo), ('str_isupper', 'dict_arr_ext', 'libs',
    bodo), ('str_istitle', 'dict_arr_ext', 'libs', bodo), ('str_isnumeric',
    'dict_arr_ext', 'libs', bodo), ('str_isdecimal', 'dict_arr_ext', 'libs',
    bodo), ('str_match', 'dict_arr_ext', 'libs', bodo), ('prange', bodo), (
    bodo.prange,), ('objmode', bodo), (bodo.objmode,), (
    'get_label_dict_from_categories', 'pd_categorial_ext', 'hiframes', bodo
    ), ('get_label_dict_from_categories_no_duplicates', 'pd_categorial_ext',
    'hiframes', bodo), ('build_nullable_tuple', 'nullable_tuple_ext',
    'libs', bodo), ('generate_mappable_table_func', 'table_utils', 'utils',
    bodo), ('table_astype', 'table_utils', 'utils', bodo), ('table_concat',
    'table_utils', 'utils', bodo), ('table_filter', 'table', 'hiframes',
    bodo), ('table_subset', 'table', 'hiframes', bodo), (
    'logical_table_to_table', 'table', 'hiframes', bodo), ('startswith',),
    ('endswith',)}


def remove_hiframes(rhs, lives, call_list):
    pcsa__fte = tuple(call_list)
    if pcsa__fte in no_side_effect_call_tuples:
        return True
    if pcsa__fte == (bodo.hiframes.pd_index_ext.init_range_index,):
        return True
    if len(call_list) == 4 and call_list[1:] == ['conversion', 'utils', bodo]:
        return True
    if isinstance(call_list[-1], pytypes.ModuleType) and call_list[-1
        ].__name__ == 'bodosql':
        return True
    if len(call_list) == 2 and call_list[0] == 'copy':
        return True
    if call_list == ['h5read', 'h5_api', 'io', bodo] and rhs.args[5
        ].name not in lives:
        return True
    if call_list == ['move_str_binary_arr_payload', 'str_arr_ext', 'libs', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['setna', 'array_kernels', 'libs', bodo] and rhs.args[0
        ].name not in lives:
        return True
    if call_list == ['set_table_data', 'table', 'hiframes', bodo] and rhs.args[
        0].name not in lives:
        return True
    if call_list == ['set_table_data_null', 'table', 'hiframes', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['ensure_column_unboxed', 'table', 'hiframes', bodo
        ] and rhs.args[0].name not in lives and rhs.args[1].name not in lives:
        return True
    if call_list == ['generate_table_nbytes', 'table_utils', 'utils', bodo
        ] and rhs.args[1].name not in lives:
        return True
    if len(pcsa__fte) == 1 and tuple in getattr(pcsa__fte[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        rwhr__uwpt = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        rwhr__uwpt = func.__globals__
    if extra_globals is not None:
        rwhr__uwpt.update(extra_globals)
    if add_default_globals:
        rwhr__uwpt.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, rwhr__uwpt, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[ypqc__iklua.name] for ypqc__iklua in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, rwhr__uwpt)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        pvhda__agj = tuple(typing_info.typemap[ypqc__iklua.name] for
            ypqc__iklua in args)
        bdf__btboz = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, pvhda__agj, {}, {}, flags)
        bdf__btboz.run()
    dxpn__pich = f_ir.blocks.popitem()[1]
    replace_arg_nodes(dxpn__pich, args)
    zibja__rzba = dxpn__pich.body[:-2]
    update_locs(zibja__rzba[len(args):], loc)
    for stmt in zibja__rzba[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        klka__wlbib = dxpn__pich.body[-2]
        assert is_assign(klka__wlbib) and is_expr(klka__wlbib.value, 'cast')
        ojsg__dsc = klka__wlbib.value.value
        zibja__rzba.append(ir.Assign(ojsg__dsc, ret_var, loc))
    return zibja__rzba


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for mtcfb__tzl in stmt.list_vars():
            mtcfb__tzl.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        ayjmt__kqrxv = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        bql__yetek, ekt__oiou = ayjmt__kqrxv(stmt)
        return ekt__oiou
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        emy__etky = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(emy__etky, ir.UndefinedType):
            qcai__aoi = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{qcai__aoi}' is not defined", loc=loc)
    except GuardException as nkur__xwgn:
        raise BodoError(err_msg, loc=loc)
    return emy__etky


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    ntdb__vev = get_definition(func_ir, var)
    mzkvw__urovi = None
    if typemap is not None:
        mzkvw__urovi = typemap.get(var.name, None)
    if isinstance(ntdb__vev, ir.Arg) and arg_types is not None:
        mzkvw__urovi = arg_types[ntdb__vev.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(mzkvw__urovi):
        return get_literal_value(mzkvw__urovi)
    if isinstance(ntdb__vev, (ir.Const, ir.Global, ir.FreeVar)):
        emy__etky = ntdb__vev.value
        return emy__etky
    if literalize_args and isinstance(ntdb__vev, ir.Arg
        ) and can_literalize_type(mzkvw__urovi, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({ntdb__vev.index}, loc=var.
            loc, file_infos={ntdb__vev.index: file_info} if file_info is not
            None else None)
    if is_expr(ntdb__vev, 'binop'):
        if file_info and ntdb__vev.fn == operator.add:
            try:
                wce__mrf = get_const_value_inner(func_ir, ntdb__vev.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(wce__mrf, True)
                hbn__aez = get_const_value_inner(func_ir, ntdb__vev.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return ntdb__vev.fn(wce__mrf, hbn__aez)
            except (GuardException, BodoConstUpdatedError) as nkur__xwgn:
                pass
            try:
                hbn__aez = get_const_value_inner(func_ir, ntdb__vev.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(hbn__aez, False)
                wce__mrf = get_const_value_inner(func_ir, ntdb__vev.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return ntdb__vev.fn(wce__mrf, hbn__aez)
            except (GuardException, BodoConstUpdatedError) as nkur__xwgn:
                pass
        wce__mrf = get_const_value_inner(func_ir, ntdb__vev.lhs, arg_types,
            typemap, updated_containers)
        hbn__aez = get_const_value_inner(func_ir, ntdb__vev.rhs, arg_types,
            typemap, updated_containers)
        return ntdb__vev.fn(wce__mrf, hbn__aez)
    if is_expr(ntdb__vev, 'unary'):
        emy__etky = get_const_value_inner(func_ir, ntdb__vev.value,
            arg_types, typemap, updated_containers)
        return ntdb__vev.fn(emy__etky)
    if is_expr(ntdb__vev, 'getattr') and typemap:
        lsm__pqwqh = typemap.get(ntdb__vev.value.name, None)
        if isinstance(lsm__pqwqh, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and ntdb__vev.attr == 'columns':
            return pd.Index(lsm__pqwqh.columns)
        if isinstance(lsm__pqwqh, types.SliceType):
            sue__yifq = get_definition(func_ir, ntdb__vev.value)
            require(is_call(sue__yifq))
            hvup__qsa = find_callname(func_ir, sue__yifq)
            rgl__rqi = False
            if hvup__qsa == ('_normalize_slice', 'numba.cpython.unicode'):
                require(ntdb__vev.attr in ('start', 'step'))
                sue__yifq = get_definition(func_ir, sue__yifq.args[0])
                rgl__rqi = True
            require(find_callname(func_ir, sue__yifq) == ('slice', 'builtins'))
            if len(sue__yifq.args) == 1:
                if ntdb__vev.attr == 'start':
                    return 0
                if ntdb__vev.attr == 'step':
                    return 1
                require(ntdb__vev.attr == 'stop')
                return get_const_value_inner(func_ir, sue__yifq.args[0],
                    arg_types, typemap, updated_containers)
            if ntdb__vev.attr == 'start':
                emy__etky = get_const_value_inner(func_ir, sue__yifq.args[0
                    ], arg_types, typemap, updated_containers)
                if emy__etky is None:
                    emy__etky = 0
                if rgl__rqi:
                    require(emy__etky == 0)
                return emy__etky
            if ntdb__vev.attr == 'stop':
                assert not rgl__rqi
                return get_const_value_inner(func_ir, sue__yifq.args[1],
                    arg_types, typemap, updated_containers)
            require(ntdb__vev.attr == 'step')
            if len(sue__yifq.args) == 2:
                return 1
            else:
                emy__etky = get_const_value_inner(func_ir, sue__yifq.args[2
                    ], arg_types, typemap, updated_containers)
                if emy__etky is None:
                    emy__etky = 1
                if rgl__rqi:
                    require(emy__etky == 1)
                return emy__etky
    if is_expr(ntdb__vev, 'getattr'):
        return getattr(get_const_value_inner(func_ir, ntdb__vev.value,
            arg_types, typemap, updated_containers), ntdb__vev.attr)
    if is_expr(ntdb__vev, 'getitem'):
        value = get_const_value_inner(func_ir, ntdb__vev.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, ntdb__vev.index, arg_types,
            typemap, updated_containers)
        return value[index]
    ljl__tsdu = guard(find_callname, func_ir, ntdb__vev, typemap)
    if ljl__tsdu is not None and len(ljl__tsdu) == 2 and ljl__tsdu[0
        ] == 'keys' and isinstance(ljl__tsdu[1], ir.Var):
        juq__toblg = ntdb__vev.func
        ntdb__vev = get_definition(func_ir, ljl__tsdu[1])
        pzf__txqex = ljl__tsdu[1].name
        if updated_containers and pzf__txqex in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                pzf__txqex, updated_containers[pzf__txqex]))
        require(is_expr(ntdb__vev, 'build_map'))
        vals = [mtcfb__tzl[0] for mtcfb__tzl in ntdb__vev.items]
        ukurk__jkle = guard(get_definition, func_ir, juq__toblg)
        assert isinstance(ukurk__jkle, ir.Expr) and ukurk__jkle.attr == 'keys'
        ukurk__jkle.attr = 'copy'
        return [get_const_value_inner(func_ir, mtcfb__tzl, arg_types,
            typemap, updated_containers) for mtcfb__tzl in vals]
    if is_expr(ntdb__vev, 'build_map'):
        return {get_const_value_inner(func_ir, mtcfb__tzl[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            mtcfb__tzl[1], arg_types, typemap, updated_containers) for
            mtcfb__tzl in ntdb__vev.items}
    if is_expr(ntdb__vev, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, mtcfb__tzl, arg_types,
            typemap, updated_containers) for mtcfb__tzl in ntdb__vev.items)
    if is_expr(ntdb__vev, 'build_list'):
        return [get_const_value_inner(func_ir, mtcfb__tzl, arg_types,
            typemap, updated_containers) for mtcfb__tzl in ntdb__vev.items]
    if is_expr(ntdb__vev, 'build_set'):
        return {get_const_value_inner(func_ir, mtcfb__tzl, arg_types,
            typemap, updated_containers) for mtcfb__tzl in ntdb__vev.items}
    if ljl__tsdu == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, ntdb__vev.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if ljl__tsdu == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, ntdb__vev.args[0],
            arg_types, typemap, updated_containers))
    if ljl__tsdu == ('range', 'builtins') and len(ntdb__vev.args) == 1:
        return range(get_const_value_inner(func_ir, ntdb__vev.args[0],
            arg_types, typemap, updated_containers))
    if ljl__tsdu == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, mtcfb__tzl,
            arg_types, typemap, updated_containers) for mtcfb__tzl in
            ntdb__vev.args))
    if ljl__tsdu == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, ntdb__vev.args[0],
            arg_types, typemap, updated_containers))
    if ljl__tsdu == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, ntdb__vev.args[0],
            arg_types, typemap, updated_containers))
    if ljl__tsdu == ('format', 'builtins'):
        ypqc__iklua = get_const_value_inner(func_ir, ntdb__vev.args[0],
            arg_types, typemap, updated_containers)
        yry__lyqw = get_const_value_inner(func_ir, ntdb__vev.args[1],
            arg_types, typemap, updated_containers) if len(ntdb__vev.args
            ) > 1 else ''
        return format(ypqc__iklua, yry__lyqw)
    if ljl__tsdu in (('init_binary_str_index', 'bodo.hiframes.pd_index_ext'
        ), ('init_numeric_index', 'bodo.hiframes.pd_index_ext'), (
        'init_categorical_index', 'bodo.hiframes.pd_index_ext'), (
        'init_datetime_index', 'bodo.hiframes.pd_index_ext'), (
        'init_timedelta_index', 'bodo.hiframes.pd_index_ext'), (
        'init_heter_index', 'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, ntdb__vev.args[0],
            arg_types, typemap, updated_containers))
    if ljl__tsdu == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, ntdb__vev.args[0],
            arg_types, typemap, updated_containers))
    if ljl__tsdu == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, ntdb__vev.args[
            0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, ntdb__vev.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            ntdb__vev.args[2], arg_types, typemap, updated_containers))
    if ljl__tsdu == ('len', 'builtins') and typemap and isinstance(typemap.
        get(ntdb__vev.args[0].name, None), types.BaseTuple):
        return len(typemap[ntdb__vev.args[0].name])
    if ljl__tsdu == ('len', 'builtins'):
        edj__qld = guard(get_definition, func_ir, ntdb__vev.args[0])
        if isinstance(edj__qld, ir.Expr) and edj__qld.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(edj__qld.items)
        return len(get_const_value_inner(func_ir, ntdb__vev.args[0],
            arg_types, typemap, updated_containers))
    if ljl__tsdu == ('CategoricalDtype', 'pandas'):
        kws = dict(ntdb__vev.kws)
        hycwm__frln = get_call_expr_arg('CategoricalDtype', ntdb__vev.args,
            kws, 0, 'categories', '')
        frfd__ywl = get_call_expr_arg('CategoricalDtype', ntdb__vev.args,
            kws, 1, 'ordered', False)
        if frfd__ywl is not False:
            frfd__ywl = get_const_value_inner(func_ir, frfd__ywl, arg_types,
                typemap, updated_containers)
        if hycwm__frln == '':
            hycwm__frln = None
        else:
            hycwm__frln = get_const_value_inner(func_ir, hycwm__frln,
                arg_types, typemap, updated_containers)
        return pd.CategoricalDtype(hycwm__frln, frfd__ywl)
    if ljl__tsdu == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, ntdb__vev.args[0],
            arg_types, typemap, updated_containers))
    if ljl__tsdu is not None and len(ljl__tsdu) == 2 and ljl__tsdu[1
        ] == 'pandas' and ljl__tsdu[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, ljl__tsdu[0])()
    if ljl__tsdu is not None and len(ljl__tsdu) == 2 and isinstance(ljl__tsdu
        [1], ir.Var):
        emy__etky = get_const_value_inner(func_ir, ljl__tsdu[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, mtcfb__tzl, arg_types,
            typemap, updated_containers) for mtcfb__tzl in ntdb__vev.args]
        kws = {szl__bwd[0]: get_const_value_inner(func_ir, szl__bwd[1],
            arg_types, typemap, updated_containers) for szl__bwd in
            ntdb__vev.kws}
        return getattr(emy__etky, ljl__tsdu[0])(*args, **kws)
    if ljl__tsdu is not None and len(ljl__tsdu) == 2 and ljl__tsdu[1
        ] == 'bodo' and ljl__tsdu[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, mtcfb__tzl, arg_types,
            typemap, updated_containers) for mtcfb__tzl in ntdb__vev.args)
        kwargs = {qcai__aoi: get_const_value_inner(func_ir, mtcfb__tzl,
            arg_types, typemap, updated_containers) for qcai__aoi,
            mtcfb__tzl in dict(ntdb__vev.kws).items()}
        return getattr(bodo, ljl__tsdu[0])(*args, **kwargs)
    if is_call(ntdb__vev) and typemap and isinstance(typemap.get(ntdb__vev.
        func.name, None), types.Dispatcher):
        py_func = typemap[ntdb__vev.func.name].dispatcher.py_func
        require(ntdb__vev.vararg is None)
        args = tuple(get_const_value_inner(func_ir, mtcfb__tzl, arg_types,
            typemap, updated_containers) for mtcfb__tzl in ntdb__vev.args)
        kwargs = {qcai__aoi: get_const_value_inner(func_ir, mtcfb__tzl,
            arg_types, typemap, updated_containers) for qcai__aoi,
            mtcfb__tzl in dict(ntdb__vev.kws).items()}
        arg_types = tuple(bodo.typeof(mtcfb__tzl) for mtcfb__tzl in args)
        kw_types = {kcidn__smsj: bodo.typeof(mtcfb__tzl) for kcidn__smsj,
            mtcfb__tzl in kwargs.items()}
        require(_func_is_pure(py_func, arg_types, kw_types))
        return py_func(*args, **kwargs)
    raise GuardException('Constant value not found')


def _func_is_pure(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.ir.csv_ext import CsvReader
    from bodo.ir.json_ext import JsonReader
    from bodo.ir.parquet_ext import ParquetReader
    from bodo.ir.sql_ext import SqlReader
    f_ir, typemap, cxsow__gzogo, cxsow__gzogo = (bodo.compiler.
        get_func_type_info(py_func, arg_types, kw_types))
    for block in f_ir.blocks.values():
        for stmt in block.body:
            if isinstance(stmt, ir.Print):
                return False
            if isinstance(stmt, (CsvReader, JsonReader, ParquetReader,
                SqlReader)):
                return False
            if is_setitem(stmt) and isinstance(guard(get_definition, f_ir,
                stmt.target), ir.Arg):
                return False
            if is_assign(stmt):
                rhs = stmt.value
                if isinstance(rhs, ir.Yield):
                    return False
                if is_call(rhs):
                    wnxs__aoif = guard(get_definition, f_ir, rhs.func)
                    if isinstance(wnxs__aoif, ir.Const) and isinstance(
                        wnxs__aoif.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    esrg__xbrdc = guard(find_callname, f_ir, rhs)
                    if esrg__xbrdc is None:
                        return False
                    func_name, ziu__orvh = esrg__xbrdc
                    if ziu__orvh == 'pandas' and func_name.startswith('read_'):
                        return False
                    if esrg__xbrdc in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if esrg__xbrdc == ('File', 'h5py'):
                        return False
                    if isinstance(ziu__orvh, ir.Var):
                        mzkvw__urovi = typemap[ziu__orvh.name]
                        if isinstance(mzkvw__urovi, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(mzkvw__urovi, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(mzkvw__urovi, bodo.LoggingLoggerType):
                            return False
                        if str(mzkvw__urovi).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            ziu__orvh), ir.Arg)):
                            return False
                    if ziu__orvh in ('numpy.random', 'time', 'logging',
                        'matplotlib.pyplot'):
                        return False
    return True


def fold_argument_types(pysig, args, kws):

    def normal_handler(index, param, value):
        return value

    def default_handler(index, param, default):
        return types.Omitted(default)

    def stararg_handler(index, param, values):
        return types.StarArgTuple(values)
    args = fold_arguments(pysig, args, kws, normal_handler, default_handler,
        stararg_handler)
    return args


def get_const_func_output_type(func, arg_types, kw_types, typing_context,
    target_context, is_udf=True):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
    py_func = None
    if isinstance(func, types.MakeFunctionLiteral):
        unyh__qddp = func.literal_value.code
        znj__jbndb = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            znj__jbndb = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(znj__jbndb, unyh__qddp)
        fix_struct_return(f_ir)
        typemap, nmhai__zozx, aoiva__ksxcn, cxsow__gzogo = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, aoiva__ksxcn, nmhai__zozx = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, aoiva__ksxcn, nmhai__zozx = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, aoiva__ksxcn, nmhai__zozx = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(nmhai__zozx, types.DictType):
        fzdtt__tsmw = guard(get_struct_keynames, f_ir, typemap)
        if fzdtt__tsmw is not None:
            nmhai__zozx = StructType((nmhai__zozx.value_type,) * len(
                fzdtt__tsmw), fzdtt__tsmw)
    if is_udf and isinstance(nmhai__zozx, (SeriesType, HeterogeneousSeriesType)
        ):
        ojsyo__ipwv = numba.core.registry.cpu_target.typing_context
        hahj__shtxe = numba.core.registry.cpu_target.target_context
        feqfp__pwx = bodo.transforms.series_pass.SeriesPass(f_ir,
            ojsyo__ipwv, hahj__shtxe, typemap, aoiva__ksxcn, {})
        feqfp__pwx.run()
        feqfp__pwx.run()
        feqfp__pwx.run()
        gtbho__ndd = compute_cfg_from_blocks(f_ir.blocks)
        xqukg__fxfj = [guard(_get_const_series_info, f_ir.blocks[ugz__olmq],
            f_ir, typemap) for ugz__olmq in gtbho__ndd.exit_points() if
            isinstance(f_ir.blocks[ugz__olmq].body[-1], ir.Return)]
        if None in xqukg__fxfj or len(pd.Series(xqukg__fxfj).unique()) != 1:
            nmhai__zozx.const_info = None
        else:
            nmhai__zozx.const_info = xqukg__fxfj[0]
    return nmhai__zozx


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    iqyl__tmu = block.body[-1].value
    nic__xzj = get_definition(f_ir, iqyl__tmu)
    require(is_expr(nic__xzj, 'cast'))
    nic__xzj = get_definition(f_ir, nic__xzj.value)
    require(is_call(nic__xzj) and find_callname(f_ir, nic__xzj) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    zaicq__uoew = nic__xzj.args[1]
    thxpv__gbdb = tuple(get_const_value_inner(f_ir, zaicq__uoew, typemap=
        typemap))
    if isinstance(typemap[iqyl__tmu.name], HeterogeneousSeriesType):
        return len(typemap[iqyl__tmu.name].data), thxpv__gbdb
    ctdi__wel = nic__xzj.args[0]
    nyddf__cvyi = get_definition(f_ir, ctdi__wel)
    func_name, ecbu__sinr = find_callname(f_ir, nyddf__cvyi)
    if is_call(nyddf__cvyi) and bodo.utils.utils.is_alloc_callname(func_name,
        ecbu__sinr):
        ofgy__sdpzd = nyddf__cvyi.args[0]
        dtgoa__phk = get_const_value_inner(f_ir, ofgy__sdpzd, typemap=typemap)
        return dtgoa__phk, thxpv__gbdb
    if is_call(nyddf__cvyi) and find_callname(f_ir, nyddf__cvyi) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        ctdi__wel = nyddf__cvyi.args[0]
        nyddf__cvyi = get_definition(f_ir, ctdi__wel)
    require(is_expr(nyddf__cvyi, 'build_tuple') or is_expr(nyddf__cvyi,
        'build_list'))
    return len(nyddf__cvyi.items), thxpv__gbdb


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    oxfn__izkru = []
    jdi__bbd = []
    values = []
    for kcidn__smsj, mtcfb__tzl in build_map.items:
        ooc__rqe = find_const(f_ir, kcidn__smsj)
        require(isinstance(ooc__rqe, str))
        jdi__bbd.append(ooc__rqe)
        oxfn__izkru.append(kcidn__smsj)
        values.append(mtcfb__tzl)
    cxyvv__zrwj = ir.Var(scope, mk_unique_var('val_tup'), loc)
    buq__pup = ir.Assign(ir.Expr.build_tuple(values, loc), cxyvv__zrwj, loc)
    f_ir._definitions[cxyvv__zrwj.name] = [buq__pup.value]
    bvxkb__bta = ir.Var(scope, mk_unique_var('key_tup'), loc)
    zsrz__qer = ir.Assign(ir.Expr.build_tuple(oxfn__izkru, loc), bvxkb__bta,
        loc)
    f_ir._definitions[bvxkb__bta.name] = [zsrz__qer.value]
    if typemap is not None:
        typemap[cxyvv__zrwj.name] = types.Tuple([typemap[mtcfb__tzl.name] for
            mtcfb__tzl in values])
        typemap[bvxkb__bta.name] = types.Tuple([typemap[mtcfb__tzl.name] for
            mtcfb__tzl in oxfn__izkru])
    return jdi__bbd, cxyvv__zrwj, buq__pup, bvxkb__bta, zsrz__qer


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    pnss__pldga = block.body[-1].value
    schp__hwx = guard(get_definition, f_ir, pnss__pldga)
    require(is_expr(schp__hwx, 'cast'))
    nic__xzj = guard(get_definition, f_ir, schp__hwx.value)
    require(is_expr(nic__xzj, 'build_map'))
    require(len(nic__xzj.items) > 0)
    loc = block.loc
    scope = block.scope
    jdi__bbd, cxyvv__zrwj, buq__pup, bvxkb__bta, zsrz__qer = (
        extract_keyvals_from_struct_map(f_ir, nic__xzj, loc, scope))
    odfu__maxh = ir.Var(scope, mk_unique_var('conv_call'), loc)
    ohql__ynwpe = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), odfu__maxh, loc)
    f_ir._definitions[odfu__maxh.name] = [ohql__ynwpe.value]
    twnt__bloyw = ir.Var(scope, mk_unique_var('struct_val'), loc)
    trwi__smh = ir.Assign(ir.Expr.call(odfu__maxh, [cxyvv__zrwj, bvxkb__bta
        ], {}, loc), twnt__bloyw, loc)
    f_ir._definitions[twnt__bloyw.name] = [trwi__smh.value]
    schp__hwx.value = twnt__bloyw
    nic__xzj.items = [(kcidn__smsj, kcidn__smsj) for kcidn__smsj,
        cxsow__gzogo in nic__xzj.items]
    block.body = block.body[:-2] + [buq__pup, zsrz__qer, ohql__ynwpe, trwi__smh
        ] + block.body[-2:]
    return tuple(jdi__bbd)


def get_struct_keynames(f_ir, typemap):
    gtbho__ndd = compute_cfg_from_blocks(f_ir.blocks)
    gxf__vgh = list(gtbho__ndd.exit_points())[0]
    block = f_ir.blocks[gxf__vgh]
    require(isinstance(block.body[-1], ir.Return))
    pnss__pldga = block.body[-1].value
    schp__hwx = guard(get_definition, f_ir, pnss__pldga)
    require(is_expr(schp__hwx, 'cast'))
    nic__xzj = guard(get_definition, f_ir, schp__hwx.value)
    require(is_call(nic__xzj) and find_callname(f_ir, nic__xzj) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[nic__xzj.args[1].name])


def fix_struct_return(f_ir):
    tvi__bhtiu = None
    gtbho__ndd = compute_cfg_from_blocks(f_ir.blocks)
    for gxf__vgh in gtbho__ndd.exit_points():
        tvi__bhtiu = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            gxf__vgh], gxf__vgh)
    return tvi__bhtiu


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    rddn__aoi = ir.Block(ir.Scope(None, loc), loc)
    rddn__aoi.body = node_list
    build_definitions({(0): rddn__aoi}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(mtcfb__tzl) for mtcfb__tzl in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    jrt__qux = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(jrt__qux, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for sert__ydh in range(len(vals) - 1, -1, -1):
        mtcfb__tzl = vals[sert__ydh]
        if isinstance(mtcfb__tzl, str) and mtcfb__tzl.startswith(
            NESTED_TUP_SENTINEL):
            oau__vvl = int(mtcfb__tzl[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:sert__ydh]) + (
                tuple(vals[sert__ydh + 1:sert__ydh + oau__vvl + 1]),) +
                tuple(vals[sert__ydh + oau__vvl + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    ypqc__iklua = None
    if len(args) > arg_no and arg_no >= 0:
        ypqc__iklua = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        ypqc__iklua = kws[arg_name]
    if ypqc__iklua is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return ypqc__iklua


def set_call_expr_arg(var, args, kws, arg_no, arg_name, add_if_missing=False):
    if len(args) > arg_no:
        args[arg_no] = var
    elif add_if_missing or arg_name in kws:
        kws[arg_name] = var
    else:
        raise BodoError('cannot set call argument since does not exist')


def avoid_udf_inline(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    f_ir = numba.core.compiler.run_frontend(py_func, inline_closures=True)
    if '_bodo_inline' in kw_types and is_overload_constant_bool(kw_types[
        '_bodo_inline']):
        return not get_overload_const_bool(kw_types['_bodo_inline'])
    if any(isinstance(t, DataFrameType) for t in arg_types + tuple(kw_types
        .values())):
        return True
    for block in f_ir.blocks.values():
        if isinstance(block.body[-1], (ir.Raise, ir.StaticRaise)):
            return True
        for stmt in block.body:
            if isinstance(stmt, ir.EnterWith):
                return True
    return False


def replace_func(pass_info, func, args, const=False, pre_nodes=None,
    extra_globals=None, pysig=None, kws=None, inline_bodo_calls=False,
    run_full_pipeline=False):
    rwhr__uwpt = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        rwhr__uwpt.update(extra_globals)
    func.__globals__.update(rwhr__uwpt)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            ppi__wzd = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[ppi__wzd.name] = types.literal(default)
            except:
                pass_info.typemap[ppi__wzd.name] = numba.typeof(default)
            rjo__irfdq = ir.Assign(ir.Const(default, loc), ppi__wzd, loc)
            pre_nodes.append(rjo__irfdq)
            return ppi__wzd
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    pvhda__agj = tuple(pass_info.typemap[mtcfb__tzl.name] for mtcfb__tzl in
        args)
    if const:
        cobor__vxzql = []
        for sert__ydh, ypqc__iklua in enumerate(args):
            emy__etky = guard(find_const, pass_info.func_ir, ypqc__iklua)
            if emy__etky:
                cobor__vxzql.append(types.literal(emy__etky))
            else:
                cobor__vxzql.append(pvhda__agj[sert__ydh])
        pvhda__agj = tuple(cobor__vxzql)
    return ReplaceFunc(func, pvhda__agj, args, rwhr__uwpt,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(ddm__wkvou) for ddm__wkvou in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        zuss__ovz = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {zuss__ovz} = 0\n', (zuss__ovz,)
    if isinstance(t, ArrayItemArrayType):
        qhd__nswj, pcihv__cvig = gen_init_varsize_alloc_sizes(t.dtype)
        zuss__ovz = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {zuss__ovz} = 0\n' + qhd__nswj, (zuss__ovz,) + pcihv__cvig
    return '', ()


def gen_varsize_item_sizes(t, item, var_names):
    if t == string_array_type:
        return '    {} += bodo.libs.str_arr_ext.get_utf8_size({})\n'.format(
            var_names[0], item)
    if isinstance(t, ArrayItemArrayType):
        return '    {} += len({})\n'.format(var_names[0], item
            ) + gen_varsize_array_counts(t.dtype, item, var_names[1:])
    return ''


def gen_varsize_array_counts(t, item, var_names):
    if t == string_array_type:
        return ('    {} += bodo.libs.str_arr_ext.get_num_total_chars({})\n'
            .format(var_names[0], item))
    return ''


def get_type_alloc_counts(t):
    if isinstance(t, (StructArrayType, TupleArrayType)):
        return 1 + sum(get_type_alloc_counts(ddm__wkvou.dtype) for
            ddm__wkvou in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(ddm__wkvou) for ddm__wkvou in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(ddm__wkvou) for ddm__wkvou in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    qerfd__nbi = typing_context.resolve_getattr(obj_dtype, func_name)
    if qerfd__nbi is None:
        spwp__tlse = types.misc.Module(np)
        try:
            qerfd__nbi = typing_context.resolve_getattr(spwp__tlse, func_name)
        except AttributeError as nkur__xwgn:
            qerfd__nbi = None
        if qerfd__nbi is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return qerfd__nbi


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    qerfd__nbi = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(qerfd__nbi, types.BoundFunction):
        if axis is not None:
            qnpt__xny = qerfd__nbi.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            qnpt__xny = qerfd__nbi.get_call_type(typing_context, (), {})
        return qnpt__xny.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(qerfd__nbi):
            qnpt__xny = qerfd__nbi.get_call_type(typing_context, (obj_dtype
                ,), {})
            return qnpt__xny.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    qerfd__nbi = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(qerfd__nbi, types.BoundFunction):
        gfxg__bfxah = qerfd__nbi.template
        if axis is not None:
            return gfxg__bfxah._overload_func(obj_dtype, axis=axis)
        else:
            return gfxg__bfxah._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    xfrg__tigan = get_definition(func_ir, dict_var)
    require(isinstance(xfrg__tigan, ir.Expr))
    require(xfrg__tigan.op == 'build_map')
    ohft__mwwp = xfrg__tigan.items
    oxfn__izkru = []
    values = []
    hno__avfrt = False
    for sert__ydh in range(len(ohft__mwwp)):
        uxs__die, value = ohft__mwwp[sert__ydh]
        try:
            ahh__ynlgt = get_const_value_inner(func_ir, uxs__die, arg_types,
                typemap, updated_containers)
            oxfn__izkru.append(ahh__ynlgt)
            values.append(value)
        except GuardException as nkur__xwgn:
            require_const_map[uxs__die] = label
            hno__avfrt = True
    if hno__avfrt:
        raise GuardException
    return oxfn__izkru, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        oxfn__izkru = tuple(get_const_value_inner(func_ir, t[0], args) for
            t in build_map.items)
    except GuardException as nkur__xwgn:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in oxfn__izkru):
        raise BodoError(err_msg, loc)
    return oxfn__izkru


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    oxfn__izkru = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    qxro__ldzgw = []
    zto__cdrl = [bodo.transforms.typing_pass._create_const_var(kcidn__smsj,
        'dict_key', scope, loc, qxro__ldzgw) for kcidn__smsj in oxfn__izkru]
    jej__vmnxc = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        cjkj__tzh = ir.Var(scope, mk_unique_var('sentinel'), loc)
        diq__qep = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        qxro__ldzgw.append(ir.Assign(ir.Const('__bodo_tup', loc), cjkj__tzh,
            loc))
        ibfwd__mgk = [cjkj__tzh] + zto__cdrl + jej__vmnxc
        qxro__ldzgw.append(ir.Assign(ir.Expr.build_tuple(ibfwd__mgk, loc),
            diq__qep, loc))
        return (diq__qep,), qxro__ldzgw
    else:
        tmt__tmlzy = ir.Var(scope, mk_unique_var('values_tup'), loc)
        enfh__muzn = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        qxro__ldzgw.append(ir.Assign(ir.Expr.build_tuple(jej__vmnxc, loc),
            tmt__tmlzy, loc))
        qxro__ldzgw.append(ir.Assign(ir.Expr.build_tuple(zto__cdrl, loc),
            enfh__muzn, loc))
        return (tmt__tmlzy, enfh__muzn), qxro__ldzgw
