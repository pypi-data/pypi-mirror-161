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
    tjjt__skmq = tuple(call_list)
    if tjjt__skmq in no_side_effect_call_tuples:
        return True
    if tjjt__skmq == (bodo.hiframes.pd_index_ext.init_range_index,):
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
    if len(tjjt__skmq) == 1 and tuple in getattr(tjjt__skmq[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        yro__wujub = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        yro__wujub = func.__globals__
    if extra_globals is not None:
        yro__wujub.update(extra_globals)
    if add_default_globals:
        yro__wujub.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, yro__wujub, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[gji__lnqt.name] for gji__lnqt in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, yro__wujub)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        tyrxb__ray = tuple(typing_info.typemap[gji__lnqt.name] for
            gji__lnqt in args)
        xxb__kdj = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, tyrxb__ray, {}, {}, flags)
        xxb__kdj.run()
    ojvn__btbz = f_ir.blocks.popitem()[1]
    replace_arg_nodes(ojvn__btbz, args)
    tcd__jeocq = ojvn__btbz.body[:-2]
    update_locs(tcd__jeocq[len(args):], loc)
    for stmt in tcd__jeocq[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        vag__pcbzt = ojvn__btbz.body[-2]
        assert is_assign(vag__pcbzt) and is_expr(vag__pcbzt.value, 'cast')
        onvlp__nmpp = vag__pcbzt.value.value
        tcd__jeocq.append(ir.Assign(onvlp__nmpp, ret_var, loc))
    return tcd__jeocq


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for oaus__ewbzl in stmt.list_vars():
            oaus__ewbzl.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        nyzq__fbp = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        dfi__zlrjz, xfhb__mpk = nyzq__fbp(stmt)
        return xfhb__mpk
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        bidhk__tzh = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(bidhk__tzh, ir.UndefinedType):
            nwq__ynj = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{nwq__ynj}' is not defined", loc=loc)
    except GuardException as xjhm__jvbg:
        raise BodoError(err_msg, loc=loc)
    return bidhk__tzh


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    oqd__bfpon = get_definition(func_ir, var)
    omk__yzvop = None
    if typemap is not None:
        omk__yzvop = typemap.get(var.name, None)
    if isinstance(oqd__bfpon, ir.Arg) and arg_types is not None:
        omk__yzvop = arg_types[oqd__bfpon.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(omk__yzvop):
        return get_literal_value(omk__yzvop)
    if isinstance(oqd__bfpon, (ir.Const, ir.Global, ir.FreeVar)):
        bidhk__tzh = oqd__bfpon.value
        return bidhk__tzh
    if literalize_args and isinstance(oqd__bfpon, ir.Arg
        ) and can_literalize_type(omk__yzvop, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({oqd__bfpon.index}, loc=var
            .loc, file_infos={oqd__bfpon.index: file_info} if file_info is not
            None else None)
    if is_expr(oqd__bfpon, 'binop'):
        if file_info and oqd__bfpon.fn == operator.add:
            try:
                jlf__fxk = get_const_value_inner(func_ir, oqd__bfpon.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(jlf__fxk, True)
                oxgvd__pyj = get_const_value_inner(func_ir, oqd__bfpon.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return oqd__bfpon.fn(jlf__fxk, oxgvd__pyj)
            except (GuardException, BodoConstUpdatedError) as xjhm__jvbg:
                pass
            try:
                oxgvd__pyj = get_const_value_inner(func_ir, oqd__bfpon.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(oxgvd__pyj, False)
                jlf__fxk = get_const_value_inner(func_ir, oqd__bfpon.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return oqd__bfpon.fn(jlf__fxk, oxgvd__pyj)
            except (GuardException, BodoConstUpdatedError) as xjhm__jvbg:
                pass
        jlf__fxk = get_const_value_inner(func_ir, oqd__bfpon.lhs, arg_types,
            typemap, updated_containers)
        oxgvd__pyj = get_const_value_inner(func_ir, oqd__bfpon.rhs,
            arg_types, typemap, updated_containers)
        return oqd__bfpon.fn(jlf__fxk, oxgvd__pyj)
    if is_expr(oqd__bfpon, 'unary'):
        bidhk__tzh = get_const_value_inner(func_ir, oqd__bfpon.value,
            arg_types, typemap, updated_containers)
        return oqd__bfpon.fn(bidhk__tzh)
    if is_expr(oqd__bfpon, 'getattr') and typemap:
        gmdja__arnvn = typemap.get(oqd__bfpon.value.name, None)
        if isinstance(gmdja__arnvn, bodo.hiframes.pd_dataframe_ext.
            DataFrameType) and oqd__bfpon.attr == 'columns':
            return pd.Index(gmdja__arnvn.columns)
        if isinstance(gmdja__arnvn, types.SliceType):
            mkwb__bvw = get_definition(func_ir, oqd__bfpon.value)
            require(is_call(mkwb__bvw))
            bal__huado = find_callname(func_ir, mkwb__bvw)
            wzrfu__zwd = False
            if bal__huado == ('_normalize_slice', 'numba.cpython.unicode'):
                require(oqd__bfpon.attr in ('start', 'step'))
                mkwb__bvw = get_definition(func_ir, mkwb__bvw.args[0])
                wzrfu__zwd = True
            require(find_callname(func_ir, mkwb__bvw) == ('slice', 'builtins'))
            if len(mkwb__bvw.args) == 1:
                if oqd__bfpon.attr == 'start':
                    return 0
                if oqd__bfpon.attr == 'step':
                    return 1
                require(oqd__bfpon.attr == 'stop')
                return get_const_value_inner(func_ir, mkwb__bvw.args[0],
                    arg_types, typemap, updated_containers)
            if oqd__bfpon.attr == 'start':
                bidhk__tzh = get_const_value_inner(func_ir, mkwb__bvw.args[
                    0], arg_types, typemap, updated_containers)
                if bidhk__tzh is None:
                    bidhk__tzh = 0
                if wzrfu__zwd:
                    require(bidhk__tzh == 0)
                return bidhk__tzh
            if oqd__bfpon.attr == 'stop':
                assert not wzrfu__zwd
                return get_const_value_inner(func_ir, mkwb__bvw.args[1],
                    arg_types, typemap, updated_containers)
            require(oqd__bfpon.attr == 'step')
            if len(mkwb__bvw.args) == 2:
                return 1
            else:
                bidhk__tzh = get_const_value_inner(func_ir, mkwb__bvw.args[
                    2], arg_types, typemap, updated_containers)
                if bidhk__tzh is None:
                    bidhk__tzh = 1
                if wzrfu__zwd:
                    require(bidhk__tzh == 1)
                return bidhk__tzh
    if is_expr(oqd__bfpon, 'getattr'):
        return getattr(get_const_value_inner(func_ir, oqd__bfpon.value,
            arg_types, typemap, updated_containers), oqd__bfpon.attr)
    if is_expr(oqd__bfpon, 'getitem'):
        value = get_const_value_inner(func_ir, oqd__bfpon.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, oqd__bfpon.index, arg_types,
            typemap, updated_containers)
        return value[index]
    kwncb__xwblk = guard(find_callname, func_ir, oqd__bfpon, typemap)
    if kwncb__xwblk is not None and len(kwncb__xwblk) == 2 and kwncb__xwblk[0
        ] == 'keys' and isinstance(kwncb__xwblk[1], ir.Var):
        vzps__zykxw = oqd__bfpon.func
        oqd__bfpon = get_definition(func_ir, kwncb__xwblk[1])
        rvc__junde = kwncb__xwblk[1].name
        if updated_containers and rvc__junde in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                rvc__junde, updated_containers[rvc__junde]))
        require(is_expr(oqd__bfpon, 'build_map'))
        vals = [oaus__ewbzl[0] for oaus__ewbzl in oqd__bfpon.items]
        vgg__nwmqb = guard(get_definition, func_ir, vzps__zykxw)
        assert isinstance(vgg__nwmqb, ir.Expr) and vgg__nwmqb.attr == 'keys'
        vgg__nwmqb.attr = 'copy'
        return [get_const_value_inner(func_ir, oaus__ewbzl, arg_types,
            typemap, updated_containers) for oaus__ewbzl in vals]
    if is_expr(oqd__bfpon, 'build_map'):
        return {get_const_value_inner(func_ir, oaus__ewbzl[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            oaus__ewbzl[1], arg_types, typemap, updated_containers) for
            oaus__ewbzl in oqd__bfpon.items}
    if is_expr(oqd__bfpon, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, oaus__ewbzl, arg_types,
            typemap, updated_containers) for oaus__ewbzl in oqd__bfpon.items)
    if is_expr(oqd__bfpon, 'build_list'):
        return [get_const_value_inner(func_ir, oaus__ewbzl, arg_types,
            typemap, updated_containers) for oaus__ewbzl in oqd__bfpon.items]
    if is_expr(oqd__bfpon, 'build_set'):
        return {get_const_value_inner(func_ir, oaus__ewbzl, arg_types,
            typemap, updated_containers) for oaus__ewbzl in oqd__bfpon.items}
    if kwncb__xwblk == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, oqd__bfpon.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if kwncb__xwblk == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, oqd__bfpon.args[0],
            arg_types, typemap, updated_containers))
    if kwncb__xwblk == ('range', 'builtins') and len(oqd__bfpon.args) == 1:
        return range(get_const_value_inner(func_ir, oqd__bfpon.args[0],
            arg_types, typemap, updated_containers))
    if kwncb__xwblk == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, oaus__ewbzl,
            arg_types, typemap, updated_containers) for oaus__ewbzl in
            oqd__bfpon.args))
    if kwncb__xwblk == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, oqd__bfpon.args[0],
            arg_types, typemap, updated_containers))
    if kwncb__xwblk == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, oqd__bfpon.args[0],
            arg_types, typemap, updated_containers))
    if kwncb__xwblk == ('format', 'builtins'):
        gji__lnqt = get_const_value_inner(func_ir, oqd__bfpon.args[0],
            arg_types, typemap, updated_containers)
        xapqc__rvyz = get_const_value_inner(func_ir, oqd__bfpon.args[1],
            arg_types, typemap, updated_containers) if len(oqd__bfpon.args
            ) > 1 else ''
        return format(gji__lnqt, xapqc__rvyz)
    if kwncb__xwblk in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, oqd__bfpon.args[0],
            arg_types, typemap, updated_containers))
    if kwncb__xwblk == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, oqd__bfpon.args[0],
            arg_types, typemap, updated_containers))
    if kwncb__xwblk == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, oqd__bfpon.args
            [0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, oqd__bfpon.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            oqd__bfpon.args[2], arg_types, typemap, updated_containers))
    if kwncb__xwblk == ('len', 'builtins') and typemap and isinstance(typemap
        .get(oqd__bfpon.args[0].name, None), types.BaseTuple):
        return len(typemap[oqd__bfpon.args[0].name])
    if kwncb__xwblk == ('len', 'builtins'):
        ewn__mfh = guard(get_definition, func_ir, oqd__bfpon.args[0])
        if isinstance(ewn__mfh, ir.Expr) and ewn__mfh.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(ewn__mfh.items)
        return len(get_const_value_inner(func_ir, oqd__bfpon.args[0],
            arg_types, typemap, updated_containers))
    if kwncb__xwblk == ('CategoricalDtype', 'pandas'):
        kws = dict(oqd__bfpon.kws)
        eao__tvq = get_call_expr_arg('CategoricalDtype', oqd__bfpon.args,
            kws, 0, 'categories', '')
        maal__qurxh = get_call_expr_arg('CategoricalDtype', oqd__bfpon.args,
            kws, 1, 'ordered', False)
        if maal__qurxh is not False:
            maal__qurxh = get_const_value_inner(func_ir, maal__qurxh,
                arg_types, typemap, updated_containers)
        if eao__tvq == '':
            eao__tvq = None
        else:
            eao__tvq = get_const_value_inner(func_ir, eao__tvq, arg_types,
                typemap, updated_containers)
        return pd.CategoricalDtype(eao__tvq, maal__qurxh)
    if kwncb__xwblk == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, oqd__bfpon.args[0],
            arg_types, typemap, updated_containers))
    if kwncb__xwblk is not None and len(kwncb__xwblk) == 2 and kwncb__xwblk[1
        ] == 'pandas' and kwncb__xwblk[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, kwncb__xwblk[0])()
    if kwncb__xwblk is not None and len(kwncb__xwblk) == 2 and isinstance(
        kwncb__xwblk[1], ir.Var):
        bidhk__tzh = get_const_value_inner(func_ir, kwncb__xwblk[1],
            arg_types, typemap, updated_containers)
        args = [get_const_value_inner(func_ir, oaus__ewbzl, arg_types,
            typemap, updated_containers) for oaus__ewbzl in oqd__bfpon.args]
        kws = {qyq__ybirw[0]: get_const_value_inner(func_ir, qyq__ybirw[1],
            arg_types, typemap, updated_containers) for qyq__ybirw in
            oqd__bfpon.kws}
        return getattr(bidhk__tzh, kwncb__xwblk[0])(*args, **kws)
    if kwncb__xwblk is not None and len(kwncb__xwblk) == 2 and kwncb__xwblk[1
        ] == 'bodo' and kwncb__xwblk[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, oaus__ewbzl, arg_types,
            typemap, updated_containers) for oaus__ewbzl in oqd__bfpon.args)
        kwargs = {nwq__ynj: get_const_value_inner(func_ir, oaus__ewbzl,
            arg_types, typemap, updated_containers) for nwq__ynj,
            oaus__ewbzl in dict(oqd__bfpon.kws).items()}
        return getattr(bodo, kwncb__xwblk[0])(*args, **kwargs)
    if is_call(oqd__bfpon) and typemap and isinstance(typemap.get(
        oqd__bfpon.func.name, None), types.Dispatcher):
        py_func = typemap[oqd__bfpon.func.name].dispatcher.py_func
        require(oqd__bfpon.vararg is None)
        args = tuple(get_const_value_inner(func_ir, oaus__ewbzl, arg_types,
            typemap, updated_containers) for oaus__ewbzl in oqd__bfpon.args)
        kwargs = {nwq__ynj: get_const_value_inner(func_ir, oaus__ewbzl,
            arg_types, typemap, updated_containers) for nwq__ynj,
            oaus__ewbzl in dict(oqd__bfpon.kws).items()}
        arg_types = tuple(bodo.typeof(oaus__ewbzl) for oaus__ewbzl in args)
        kw_types = {furtk__nnupe: bodo.typeof(oaus__ewbzl) for furtk__nnupe,
            oaus__ewbzl in kwargs.items()}
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
    f_ir, typemap, ycydz__kdmdq, ycydz__kdmdq = (bodo.compiler.
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
                    wzx__vubg = guard(get_definition, f_ir, rhs.func)
                    if isinstance(wzx__vubg, ir.Const) and isinstance(wzx__vubg
                        .value, numba.core.dispatcher.ObjModeLiftedWith):
                        return False
                    mzt__msnfo = guard(find_callname, f_ir, rhs)
                    if mzt__msnfo is None:
                        return False
                    func_name, wveq__ftzs = mzt__msnfo
                    if wveq__ftzs == 'pandas' and func_name.startswith('read_'
                        ):
                        return False
                    if mzt__msnfo in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if mzt__msnfo == ('File', 'h5py'):
                        return False
                    if isinstance(wveq__ftzs, ir.Var):
                        omk__yzvop = typemap[wveq__ftzs.name]
                        if isinstance(omk__yzvop, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(omk__yzvop, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(omk__yzvop, bodo.LoggingLoggerType):
                            return False
                        if str(omk__yzvop).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            wveq__ftzs), ir.Arg)):
                            return False
                    if wveq__ftzs in ('numpy.random', 'time', 'logging',
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
        tyo__speyx = func.literal_value.code
        mbgid__ayz = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            mbgid__ayz = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(mbgid__ayz, tyo__speyx)
        fix_struct_return(f_ir)
        typemap, obskl__sugxi, kze__huhk, ycydz__kdmdq = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, kze__huhk, obskl__sugxi = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, kze__huhk, obskl__sugxi = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, kze__huhk, obskl__sugxi = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(obskl__sugxi, types.DictType):
        gypt__ipct = guard(get_struct_keynames, f_ir, typemap)
        if gypt__ipct is not None:
            obskl__sugxi = StructType((obskl__sugxi.value_type,) * len(
                gypt__ipct), gypt__ipct)
    if is_udf and isinstance(obskl__sugxi, (SeriesType,
        HeterogeneousSeriesType)):
        owe__dbdc = numba.core.registry.cpu_target.typing_context
        prgd__zkoa = numba.core.registry.cpu_target.target_context
        znrpt__uos = bodo.transforms.series_pass.SeriesPass(f_ir, owe__dbdc,
            prgd__zkoa, typemap, kze__huhk, {})
        znrpt__uos.run()
        znrpt__uos.run()
        znrpt__uos.run()
        yocav__kqelq = compute_cfg_from_blocks(f_ir.blocks)
        zyrrx__oknz = [guard(_get_const_series_info, f_ir.blocks[
            dkoc__przaa], f_ir, typemap) for dkoc__przaa in yocav__kqelq.
            exit_points() if isinstance(f_ir.blocks[dkoc__przaa].body[-1],
            ir.Return)]
        if None in zyrrx__oknz or len(pd.Series(zyrrx__oknz).unique()) != 1:
            obskl__sugxi.const_info = None
        else:
            obskl__sugxi.const_info = zyrrx__oknz[0]
    return obskl__sugxi


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    cprbh__dixoz = block.body[-1].value
    fveej__uam = get_definition(f_ir, cprbh__dixoz)
    require(is_expr(fveej__uam, 'cast'))
    fveej__uam = get_definition(f_ir, fveej__uam.value)
    require(is_call(fveej__uam) and find_callname(f_ir, fveej__uam) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    drkke__grps = fveej__uam.args[1]
    mcj__plna = tuple(get_const_value_inner(f_ir, drkke__grps, typemap=typemap)
        )
    if isinstance(typemap[cprbh__dixoz.name], HeterogeneousSeriesType):
        return len(typemap[cprbh__dixoz.name].data), mcj__plna
    yrhv__yfw = fveej__uam.args[0]
    oln__kxsz = get_definition(f_ir, yrhv__yfw)
    func_name, sub__gkzpe = find_callname(f_ir, oln__kxsz)
    if is_call(oln__kxsz) and bodo.utils.utils.is_alloc_callname(func_name,
        sub__gkzpe):
        rqqg__ynkx = oln__kxsz.args[0]
        fhbl__zwu = get_const_value_inner(f_ir, rqqg__ynkx, typemap=typemap)
        return fhbl__zwu, mcj__plna
    if is_call(oln__kxsz) and find_callname(f_ir, oln__kxsz) in [('asarray',
        'numpy'), ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'), (
        'build_nullable_tuple', 'bodo.libs.nullable_tuple_ext')]:
        yrhv__yfw = oln__kxsz.args[0]
        oln__kxsz = get_definition(f_ir, yrhv__yfw)
    require(is_expr(oln__kxsz, 'build_tuple') or is_expr(oln__kxsz,
        'build_list'))
    return len(oln__kxsz.items), mcj__plna


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    jgtu__ihvbb = []
    rbzn__ookgp = []
    values = []
    for furtk__nnupe, oaus__ewbzl in build_map.items:
        ahdod__tbjr = find_const(f_ir, furtk__nnupe)
        require(isinstance(ahdod__tbjr, str))
        rbzn__ookgp.append(ahdod__tbjr)
        jgtu__ihvbb.append(furtk__nnupe)
        values.append(oaus__ewbzl)
    bgm__xyb = ir.Var(scope, mk_unique_var('val_tup'), loc)
    lviu__ffzj = ir.Assign(ir.Expr.build_tuple(values, loc), bgm__xyb, loc)
    f_ir._definitions[bgm__xyb.name] = [lviu__ffzj.value]
    seu__hrj = ir.Var(scope, mk_unique_var('key_tup'), loc)
    rifl__nfis = ir.Assign(ir.Expr.build_tuple(jgtu__ihvbb, loc), seu__hrj, loc
        )
    f_ir._definitions[seu__hrj.name] = [rifl__nfis.value]
    if typemap is not None:
        typemap[bgm__xyb.name] = types.Tuple([typemap[oaus__ewbzl.name] for
            oaus__ewbzl in values])
        typemap[seu__hrj.name] = types.Tuple([typemap[oaus__ewbzl.name] for
            oaus__ewbzl in jgtu__ihvbb])
    return rbzn__ookgp, bgm__xyb, lviu__ffzj, seu__hrj, rifl__nfis


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    ydr__wptn = block.body[-1].value
    blnx__azbn = guard(get_definition, f_ir, ydr__wptn)
    require(is_expr(blnx__azbn, 'cast'))
    fveej__uam = guard(get_definition, f_ir, blnx__azbn.value)
    require(is_expr(fveej__uam, 'build_map'))
    require(len(fveej__uam.items) > 0)
    loc = block.loc
    scope = block.scope
    rbzn__ookgp, bgm__xyb, lviu__ffzj, seu__hrj, rifl__nfis = (
        extract_keyvals_from_struct_map(f_ir, fveej__uam, loc, scope))
    fby__jesxr = ir.Var(scope, mk_unique_var('conv_call'), loc)
    pes__rnww = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), fby__jesxr, loc)
    f_ir._definitions[fby__jesxr.name] = [pes__rnww.value]
    isl__zwo = ir.Var(scope, mk_unique_var('struct_val'), loc)
    wfyx__zlr = ir.Assign(ir.Expr.call(fby__jesxr, [bgm__xyb, seu__hrj], {},
        loc), isl__zwo, loc)
    f_ir._definitions[isl__zwo.name] = [wfyx__zlr.value]
    blnx__azbn.value = isl__zwo
    fveej__uam.items = [(furtk__nnupe, furtk__nnupe) for furtk__nnupe,
        ycydz__kdmdq in fveej__uam.items]
    block.body = block.body[:-2] + [lviu__ffzj, rifl__nfis, pes__rnww,
        wfyx__zlr] + block.body[-2:]
    return tuple(rbzn__ookgp)


def get_struct_keynames(f_ir, typemap):
    yocav__kqelq = compute_cfg_from_blocks(f_ir.blocks)
    tdh__qeole = list(yocav__kqelq.exit_points())[0]
    block = f_ir.blocks[tdh__qeole]
    require(isinstance(block.body[-1], ir.Return))
    ydr__wptn = block.body[-1].value
    blnx__azbn = guard(get_definition, f_ir, ydr__wptn)
    require(is_expr(blnx__azbn, 'cast'))
    fveej__uam = guard(get_definition, f_ir, blnx__azbn.value)
    require(is_call(fveej__uam) and find_callname(f_ir, fveej__uam) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[fveej__uam.args[1].name])


def fix_struct_return(f_ir):
    sjw__bpkra = None
    yocav__kqelq = compute_cfg_from_blocks(f_ir.blocks)
    for tdh__qeole in yocav__kqelq.exit_points():
        sjw__bpkra = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            tdh__qeole], tdh__qeole)
    return sjw__bpkra


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    tdd__cybss = ir.Block(ir.Scope(None, loc), loc)
    tdd__cybss.body = node_list
    build_definitions({(0): tdd__cybss}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(oaus__ewbzl) for oaus__ewbzl in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    ypl__ngr = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(ypl__ngr, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for cduog__dtyd in range(len(vals) - 1, -1, -1):
        oaus__ewbzl = vals[cduog__dtyd]
        if isinstance(oaus__ewbzl, str) and oaus__ewbzl.startswith(
            NESTED_TUP_SENTINEL):
            zhjp__jtip = int(oaus__ewbzl[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:cduog__dtyd]) + (
                tuple(vals[cduog__dtyd + 1:cduog__dtyd + zhjp__jtip + 1]),) +
                tuple(vals[cduog__dtyd + zhjp__jtip + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    gji__lnqt = None
    if len(args) > arg_no and arg_no >= 0:
        gji__lnqt = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        gji__lnqt = kws[arg_name]
    if gji__lnqt is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return gji__lnqt


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
    yro__wujub = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        yro__wujub.update(extra_globals)
    func.__globals__.update(yro__wujub)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            pphxb__nhphg = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[pphxb__nhphg.name] = types.literal(default)
            except:
                pass_info.typemap[pphxb__nhphg.name] = numba.typeof(default)
            flxd__ajqqk = ir.Assign(ir.Const(default, loc), pphxb__nhphg, loc)
            pre_nodes.append(flxd__ajqqk)
            return pphxb__nhphg
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    tyrxb__ray = tuple(pass_info.typemap[oaus__ewbzl.name] for oaus__ewbzl in
        args)
    if const:
        wxrh__alani = []
        for cduog__dtyd, gji__lnqt in enumerate(args):
            bidhk__tzh = guard(find_const, pass_info.func_ir, gji__lnqt)
            if bidhk__tzh:
                wxrh__alani.append(types.literal(bidhk__tzh))
            else:
                wxrh__alani.append(tyrxb__ray[cduog__dtyd])
        tyrxb__ray = tuple(wxrh__alani)
    return ReplaceFunc(func, tyrxb__ray, args, yro__wujub,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(dqudu__hrqld) for dqudu__hrqld in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        mcj__rdhp = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {mcj__rdhp} = 0\n', (mcj__rdhp,)
    if isinstance(t, ArrayItemArrayType):
        xucjy__bbp, ulp__eojr = gen_init_varsize_alloc_sizes(t.dtype)
        mcj__rdhp = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {mcj__rdhp} = 0\n' + xucjy__bbp, (mcj__rdhp,) + ulp__eojr
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
        return 1 + sum(get_type_alloc_counts(dqudu__hrqld.dtype) for
            dqudu__hrqld in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(dqudu__hrqld) for dqudu__hrqld in
            t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(dqudu__hrqld) for dqudu__hrqld in
            t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    sxgfd__hbdy = typing_context.resolve_getattr(obj_dtype, func_name)
    if sxgfd__hbdy is None:
        yuiv__jtmzc = types.misc.Module(np)
        try:
            sxgfd__hbdy = typing_context.resolve_getattr(yuiv__jtmzc, func_name
                )
        except AttributeError as xjhm__jvbg:
            sxgfd__hbdy = None
        if sxgfd__hbdy is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return sxgfd__hbdy


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    sxgfd__hbdy = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(sxgfd__hbdy, types.BoundFunction):
        if axis is not None:
            sjfa__xmfa = sxgfd__hbdy.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            sjfa__xmfa = sxgfd__hbdy.get_call_type(typing_context, (), {})
        return sjfa__xmfa.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(sxgfd__hbdy):
            sjfa__xmfa = sxgfd__hbdy.get_call_type(typing_context, (
                obj_dtype,), {})
            return sjfa__xmfa.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    sxgfd__hbdy = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(sxgfd__hbdy, types.BoundFunction):
        gsssk__izv = sxgfd__hbdy.template
        if axis is not None:
            return gsssk__izv._overload_func(obj_dtype, axis=axis)
        else:
            return gsssk__izv._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    sxmk__gog = get_definition(func_ir, dict_var)
    require(isinstance(sxmk__gog, ir.Expr))
    require(sxmk__gog.op == 'build_map')
    bak__zqgis = sxmk__gog.items
    jgtu__ihvbb = []
    values = []
    vxbhd__mbf = False
    for cduog__dtyd in range(len(bak__zqgis)):
        uhs__gvg, value = bak__zqgis[cduog__dtyd]
        try:
            awveq__acuy = get_const_value_inner(func_ir, uhs__gvg,
                arg_types, typemap, updated_containers)
            jgtu__ihvbb.append(awveq__acuy)
            values.append(value)
        except GuardException as xjhm__jvbg:
            require_const_map[uhs__gvg] = label
            vxbhd__mbf = True
    if vxbhd__mbf:
        raise GuardException
    return jgtu__ihvbb, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        jgtu__ihvbb = tuple(get_const_value_inner(func_ir, t[0], args) for
            t in build_map.items)
    except GuardException as xjhm__jvbg:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in jgtu__ihvbb):
        raise BodoError(err_msg, loc)
    return jgtu__ihvbb


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    jgtu__ihvbb = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    nll__wkh = []
    otw__rfs = [bodo.transforms.typing_pass._create_const_var(furtk__nnupe,
        'dict_key', scope, loc, nll__wkh) for furtk__nnupe in jgtu__ihvbb]
    pclmj__bzf = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        pcf__heqo = ir.Var(scope, mk_unique_var('sentinel'), loc)
        lzrw__ayps = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        nll__wkh.append(ir.Assign(ir.Const('__bodo_tup', loc), pcf__heqo, loc))
        dmfk__shspf = [pcf__heqo] + otw__rfs + pclmj__bzf
        nll__wkh.append(ir.Assign(ir.Expr.build_tuple(dmfk__shspf, loc),
            lzrw__ayps, loc))
        return (lzrw__ayps,), nll__wkh
    else:
        nnkc__kvolo = ir.Var(scope, mk_unique_var('values_tup'), loc)
        tcw__lqzc = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        nll__wkh.append(ir.Assign(ir.Expr.build_tuple(pclmj__bzf, loc),
            nnkc__kvolo, loc))
        nll__wkh.append(ir.Assign(ir.Expr.build_tuple(otw__rfs, loc),
            tcw__lqzc, loc))
        return (nnkc__kvolo, tcw__lqzc), nll__wkh
