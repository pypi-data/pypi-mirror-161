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
    njv__dqbmy = tuple(call_list)
    if njv__dqbmy in no_side_effect_call_tuples:
        return True
    if njv__dqbmy == (bodo.hiframes.pd_index_ext.init_range_index,):
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
    if len(njv__dqbmy) == 1 and tuple in getattr(njv__dqbmy[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        puwnj__heep = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        puwnj__heep = func.__globals__
    if extra_globals is not None:
        puwnj__heep.update(extra_globals)
    if add_default_globals:
        puwnj__heep.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd':
            pd, 'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, puwnj__heep, typingctx=typing_info
            .typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[kbgvq__qwh.name] for kbgvq__qwh in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, puwnj__heep)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        fhvs__voetm = tuple(typing_info.typemap[kbgvq__qwh.name] for
            kbgvq__qwh in args)
        uarix__shq = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, fhvs__voetm, {}, {}, flags)
        uarix__shq.run()
    ggot__ytpzi = f_ir.blocks.popitem()[1]
    replace_arg_nodes(ggot__ytpzi, args)
    ipsw__pwk = ggot__ytpzi.body[:-2]
    update_locs(ipsw__pwk[len(args):], loc)
    for stmt in ipsw__pwk[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        iwuv__kotmx = ggot__ytpzi.body[-2]
        assert is_assign(iwuv__kotmx) and is_expr(iwuv__kotmx.value, 'cast')
        mckfl__qke = iwuv__kotmx.value.value
        ipsw__pwk.append(ir.Assign(mckfl__qke, ret_var, loc))
    return ipsw__pwk


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for the__qsve in stmt.list_vars():
            the__qsve.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        vqb__lmgq = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        owlt__laul, wck__kcmbo = vqb__lmgq(stmt)
        return wck__kcmbo
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        zsjhz__dojol = get_const_value_inner(func_ir, var, arg_types,
            typemap, file_info=file_info)
        if isinstance(zsjhz__dojol, ir.UndefinedType):
            kanw__zcy = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{kanw__zcy}' is not defined", loc=loc)
    except GuardException as soqw__mbcf:
        raise BodoError(err_msg, loc=loc)
    return zsjhz__dojol


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    tboup__zcglj = get_definition(func_ir, var)
    diiw__wzm = None
    if typemap is not None:
        diiw__wzm = typemap.get(var.name, None)
    if isinstance(tboup__zcglj, ir.Arg) and arg_types is not None:
        diiw__wzm = arg_types[tboup__zcglj.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(diiw__wzm):
        return get_literal_value(diiw__wzm)
    if isinstance(tboup__zcglj, (ir.Const, ir.Global, ir.FreeVar)):
        zsjhz__dojol = tboup__zcglj.value
        return zsjhz__dojol
    if literalize_args and isinstance(tboup__zcglj, ir.Arg
        ) and can_literalize_type(diiw__wzm, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({tboup__zcglj.index}, loc=
            var.loc, file_infos={tboup__zcglj.index: file_info} if 
            file_info is not None else None)
    if is_expr(tboup__zcglj, 'binop'):
        if file_info and tboup__zcglj.fn == operator.add:
            try:
                swvp__iox = get_const_value_inner(func_ir, tboup__zcglj.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(swvp__iox, True)
                ceqpa__dcokl = get_const_value_inner(func_ir, tboup__zcglj.
                    rhs, arg_types, typemap, updated_containers, file_info)
                return tboup__zcglj.fn(swvp__iox, ceqpa__dcokl)
            except (GuardException, BodoConstUpdatedError) as soqw__mbcf:
                pass
            try:
                ceqpa__dcokl = get_const_value_inner(func_ir, tboup__zcglj.
                    rhs, arg_types, typemap, updated_containers,
                    literalize_args=False)
                file_info.set_concat(ceqpa__dcokl, False)
                swvp__iox = get_const_value_inner(func_ir, tboup__zcglj.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return tboup__zcglj.fn(swvp__iox, ceqpa__dcokl)
            except (GuardException, BodoConstUpdatedError) as soqw__mbcf:
                pass
        swvp__iox = get_const_value_inner(func_ir, tboup__zcglj.lhs,
            arg_types, typemap, updated_containers)
        ceqpa__dcokl = get_const_value_inner(func_ir, tboup__zcglj.rhs,
            arg_types, typemap, updated_containers)
        return tboup__zcglj.fn(swvp__iox, ceqpa__dcokl)
    if is_expr(tboup__zcglj, 'unary'):
        zsjhz__dojol = get_const_value_inner(func_ir, tboup__zcglj.value,
            arg_types, typemap, updated_containers)
        return tboup__zcglj.fn(zsjhz__dojol)
    if is_expr(tboup__zcglj, 'getattr') and typemap:
        qtjn__ygqsd = typemap.get(tboup__zcglj.value.name, None)
        if isinstance(qtjn__ygqsd, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and tboup__zcglj.attr == 'columns':
            return pd.Index(qtjn__ygqsd.columns)
        if isinstance(qtjn__ygqsd, types.SliceType):
            spnr__dyu = get_definition(func_ir, tboup__zcglj.value)
            require(is_call(spnr__dyu))
            zzj__dddn = find_callname(func_ir, spnr__dyu)
            irpuj__yow = False
            if zzj__dddn == ('_normalize_slice', 'numba.cpython.unicode'):
                require(tboup__zcglj.attr in ('start', 'step'))
                spnr__dyu = get_definition(func_ir, spnr__dyu.args[0])
                irpuj__yow = True
            require(find_callname(func_ir, spnr__dyu) == ('slice', 'builtins'))
            if len(spnr__dyu.args) == 1:
                if tboup__zcglj.attr == 'start':
                    return 0
                if tboup__zcglj.attr == 'step':
                    return 1
                require(tboup__zcglj.attr == 'stop')
                return get_const_value_inner(func_ir, spnr__dyu.args[0],
                    arg_types, typemap, updated_containers)
            if tboup__zcglj.attr == 'start':
                zsjhz__dojol = get_const_value_inner(func_ir, spnr__dyu.
                    args[0], arg_types, typemap, updated_containers)
                if zsjhz__dojol is None:
                    zsjhz__dojol = 0
                if irpuj__yow:
                    require(zsjhz__dojol == 0)
                return zsjhz__dojol
            if tboup__zcglj.attr == 'stop':
                assert not irpuj__yow
                return get_const_value_inner(func_ir, spnr__dyu.args[1],
                    arg_types, typemap, updated_containers)
            require(tboup__zcglj.attr == 'step')
            if len(spnr__dyu.args) == 2:
                return 1
            else:
                zsjhz__dojol = get_const_value_inner(func_ir, spnr__dyu.
                    args[2], arg_types, typemap, updated_containers)
                if zsjhz__dojol is None:
                    zsjhz__dojol = 1
                if irpuj__yow:
                    require(zsjhz__dojol == 1)
                return zsjhz__dojol
    if is_expr(tboup__zcglj, 'getattr'):
        return getattr(get_const_value_inner(func_ir, tboup__zcglj.value,
            arg_types, typemap, updated_containers), tboup__zcglj.attr)
    if is_expr(tboup__zcglj, 'getitem'):
        value = get_const_value_inner(func_ir, tboup__zcglj.value,
            arg_types, typemap, updated_containers)
        index = get_const_value_inner(func_ir, tboup__zcglj.index,
            arg_types, typemap, updated_containers)
        return value[index]
    hzgyv__boe = guard(find_callname, func_ir, tboup__zcglj, typemap)
    if hzgyv__boe is not None and len(hzgyv__boe) == 2 and hzgyv__boe[0
        ] == 'keys' and isinstance(hzgyv__boe[1], ir.Var):
        wxw__tbi = tboup__zcglj.func
        tboup__zcglj = get_definition(func_ir, hzgyv__boe[1])
        hiheh__srjsg = hzgyv__boe[1].name
        if updated_containers and hiheh__srjsg in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                hiheh__srjsg, updated_containers[hiheh__srjsg]))
        require(is_expr(tboup__zcglj, 'build_map'))
        vals = [the__qsve[0] for the__qsve in tboup__zcglj.items]
        ubt__izah = guard(get_definition, func_ir, wxw__tbi)
        assert isinstance(ubt__izah, ir.Expr) and ubt__izah.attr == 'keys'
        ubt__izah.attr = 'copy'
        return [get_const_value_inner(func_ir, the__qsve, arg_types,
            typemap, updated_containers) for the__qsve in vals]
    if is_expr(tboup__zcglj, 'build_map'):
        return {get_const_value_inner(func_ir, the__qsve[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            the__qsve[1], arg_types, typemap, updated_containers) for
            the__qsve in tboup__zcglj.items}
    if is_expr(tboup__zcglj, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, the__qsve, arg_types,
            typemap, updated_containers) for the__qsve in tboup__zcglj.items)
    if is_expr(tboup__zcglj, 'build_list'):
        return [get_const_value_inner(func_ir, the__qsve, arg_types,
            typemap, updated_containers) for the__qsve in tboup__zcglj.items]
    if is_expr(tboup__zcglj, 'build_set'):
        return {get_const_value_inner(func_ir, the__qsve, arg_types,
            typemap, updated_containers) for the__qsve in tboup__zcglj.items}
    if hzgyv__boe == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, tboup__zcglj.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if hzgyv__boe == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, tboup__zcglj.args[0],
            arg_types, typemap, updated_containers))
    if hzgyv__boe == ('range', 'builtins') and len(tboup__zcglj.args) == 1:
        return range(get_const_value_inner(func_ir, tboup__zcglj.args[0],
            arg_types, typemap, updated_containers))
    if hzgyv__boe == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, the__qsve,
            arg_types, typemap, updated_containers) for the__qsve in
            tboup__zcglj.args))
    if hzgyv__boe == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, tboup__zcglj.args[0],
            arg_types, typemap, updated_containers))
    if hzgyv__boe == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, tboup__zcglj.args[0],
            arg_types, typemap, updated_containers))
    if hzgyv__boe == ('format', 'builtins'):
        kbgvq__qwh = get_const_value_inner(func_ir, tboup__zcglj.args[0],
            arg_types, typemap, updated_containers)
        twdl__firtn = get_const_value_inner(func_ir, tboup__zcglj.args[1],
            arg_types, typemap, updated_containers) if len(tboup__zcglj.args
            ) > 1 else ''
        return format(kbgvq__qwh, twdl__firtn)
    if hzgyv__boe in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, tboup__zcglj.args[0],
            arg_types, typemap, updated_containers))
    if hzgyv__boe == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, tboup__zcglj.args[0],
            arg_types, typemap, updated_containers))
    if hzgyv__boe == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, tboup__zcglj.
            args[0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, tboup__zcglj.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            tboup__zcglj.args[2], arg_types, typemap, updated_containers))
    if hzgyv__boe == ('len', 'builtins') and typemap and isinstance(typemap
        .get(tboup__zcglj.args[0].name, None), types.BaseTuple):
        return len(typemap[tboup__zcglj.args[0].name])
    if hzgyv__boe == ('len', 'builtins'):
        ttmq__kii = guard(get_definition, func_ir, tboup__zcglj.args[0])
        if isinstance(ttmq__kii, ir.Expr) and ttmq__kii.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(ttmq__kii.items)
        return len(get_const_value_inner(func_ir, tboup__zcglj.args[0],
            arg_types, typemap, updated_containers))
    if hzgyv__boe == ('CategoricalDtype', 'pandas'):
        kws = dict(tboup__zcglj.kws)
        frdar__qdjwd = get_call_expr_arg('CategoricalDtype', tboup__zcglj.
            args, kws, 0, 'categories', '')
        vymbx__pwfp = get_call_expr_arg('CategoricalDtype', tboup__zcglj.
            args, kws, 1, 'ordered', False)
        if vymbx__pwfp is not False:
            vymbx__pwfp = get_const_value_inner(func_ir, vymbx__pwfp,
                arg_types, typemap, updated_containers)
        if frdar__qdjwd == '':
            frdar__qdjwd = None
        else:
            frdar__qdjwd = get_const_value_inner(func_ir, frdar__qdjwd,
                arg_types, typemap, updated_containers)
        return pd.CategoricalDtype(frdar__qdjwd, vymbx__pwfp)
    if hzgyv__boe == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, tboup__zcglj.args[0],
            arg_types, typemap, updated_containers))
    if hzgyv__boe is not None and len(hzgyv__boe) == 2 and hzgyv__boe[1
        ] == 'pandas' and hzgyv__boe[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, hzgyv__boe[0])()
    if hzgyv__boe is not None and len(hzgyv__boe) == 2 and isinstance(
        hzgyv__boe[1], ir.Var):
        zsjhz__dojol = get_const_value_inner(func_ir, hzgyv__boe[1],
            arg_types, typemap, updated_containers)
        args = [get_const_value_inner(func_ir, the__qsve, arg_types,
            typemap, updated_containers) for the__qsve in tboup__zcglj.args]
        kws = {mnhjp__stanw[0]: get_const_value_inner(func_ir, mnhjp__stanw
            [1], arg_types, typemap, updated_containers) for mnhjp__stanw in
            tboup__zcglj.kws}
        return getattr(zsjhz__dojol, hzgyv__boe[0])(*args, **kws)
    if hzgyv__boe is not None and len(hzgyv__boe) == 2 and hzgyv__boe[1
        ] == 'bodo' and hzgyv__boe[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, the__qsve, arg_types,
            typemap, updated_containers) for the__qsve in tboup__zcglj.args)
        kwargs = {kanw__zcy: get_const_value_inner(func_ir, the__qsve,
            arg_types, typemap, updated_containers) for kanw__zcy,
            the__qsve in dict(tboup__zcglj.kws).items()}
        return getattr(bodo, hzgyv__boe[0])(*args, **kwargs)
    if is_call(tboup__zcglj) and typemap and isinstance(typemap.get(
        tboup__zcglj.func.name, None), types.Dispatcher):
        py_func = typemap[tboup__zcglj.func.name].dispatcher.py_func
        require(tboup__zcglj.vararg is None)
        args = tuple(get_const_value_inner(func_ir, the__qsve, arg_types,
            typemap, updated_containers) for the__qsve in tboup__zcglj.args)
        kwargs = {kanw__zcy: get_const_value_inner(func_ir, the__qsve,
            arg_types, typemap, updated_containers) for kanw__zcy,
            the__qsve in dict(tboup__zcglj.kws).items()}
        arg_types = tuple(bodo.typeof(the__qsve) for the__qsve in args)
        kw_types = {ibxs__zwr: bodo.typeof(the__qsve) for ibxs__zwr,
            the__qsve in kwargs.items()}
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
    f_ir, typemap, grbyn__qqbwl, grbyn__qqbwl = (bodo.compiler.
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
                    kdkp__ele = guard(get_definition, f_ir, rhs.func)
                    if isinstance(kdkp__ele, ir.Const) and isinstance(kdkp__ele
                        .value, numba.core.dispatcher.ObjModeLiftedWith):
                        return False
                    jtmf__mmxq = guard(find_callname, f_ir, rhs)
                    if jtmf__mmxq is None:
                        return False
                    func_name, ydjf__kjxsw = jtmf__mmxq
                    if ydjf__kjxsw == 'pandas' and func_name.startswith('read_'
                        ):
                        return False
                    if jtmf__mmxq in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if jtmf__mmxq == ('File', 'h5py'):
                        return False
                    if isinstance(ydjf__kjxsw, ir.Var):
                        diiw__wzm = typemap[ydjf__kjxsw.name]
                        if isinstance(diiw__wzm, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(diiw__wzm, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(diiw__wzm, bodo.LoggingLoggerType):
                            return False
                        if str(diiw__wzm).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            ydjf__kjxsw), ir.Arg)):
                            return False
                    if ydjf__kjxsw in ('numpy.random', 'time', 'logging',
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
        nizwe__cpb = func.literal_value.code
        brgfy__xjehy = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            brgfy__xjehy = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(brgfy__xjehy, nizwe__cpb)
        fix_struct_return(f_ir)
        typemap, rhv__mhd, meg__bzvgp, grbyn__qqbwl = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, meg__bzvgp, rhv__mhd = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, meg__bzvgp, rhv__mhd = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, meg__bzvgp, rhv__mhd = bodo.compiler.get_func_type_info(
            py_func, arg_types, kw_types)
    if is_udf and isinstance(rhv__mhd, types.DictType):
        fplmp__lbqt = guard(get_struct_keynames, f_ir, typemap)
        if fplmp__lbqt is not None:
            rhv__mhd = StructType((rhv__mhd.value_type,) * len(fplmp__lbqt),
                fplmp__lbqt)
    if is_udf and isinstance(rhv__mhd, (SeriesType, HeterogeneousSeriesType)):
        sorj__sniot = numba.core.registry.cpu_target.typing_context
        hye__zjpmh = numba.core.registry.cpu_target.target_context
        cugbb__sdvg = bodo.transforms.series_pass.SeriesPass(f_ir,
            sorj__sniot, hye__zjpmh, typemap, meg__bzvgp, {})
        cugbb__sdvg.run()
        cugbb__sdvg.run()
        cugbb__sdvg.run()
        wxpc__iifwa = compute_cfg_from_blocks(f_ir.blocks)
        coeh__dshn = [guard(_get_const_series_info, f_ir.blocks[vel__wceox],
            f_ir, typemap) for vel__wceox in wxpc__iifwa.exit_points() if
            isinstance(f_ir.blocks[vel__wceox].body[-1], ir.Return)]
        if None in coeh__dshn or len(pd.Series(coeh__dshn).unique()) != 1:
            rhv__mhd.const_info = None
        else:
            rhv__mhd.const_info = coeh__dshn[0]
    return rhv__mhd


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    jwhd__ppqzo = block.body[-1].value
    pmv__qenih = get_definition(f_ir, jwhd__ppqzo)
    require(is_expr(pmv__qenih, 'cast'))
    pmv__qenih = get_definition(f_ir, pmv__qenih.value)
    require(is_call(pmv__qenih) and find_callname(f_ir, pmv__qenih) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    fcony__zen = pmv__qenih.args[1]
    rxxxb__ypa = tuple(get_const_value_inner(f_ir, fcony__zen, typemap=typemap)
        )
    if isinstance(typemap[jwhd__ppqzo.name], HeterogeneousSeriesType):
        return len(typemap[jwhd__ppqzo.name].data), rxxxb__ypa
    ofkh__nuwq = pmv__qenih.args[0]
    siszx__dua = get_definition(f_ir, ofkh__nuwq)
    func_name, okshh__bfo = find_callname(f_ir, siszx__dua)
    if is_call(siszx__dua) and bodo.utils.utils.is_alloc_callname(func_name,
        okshh__bfo):
        nny__uyte = siszx__dua.args[0]
        rakb__txna = get_const_value_inner(f_ir, nny__uyte, typemap=typemap)
        return rakb__txna, rxxxb__ypa
    if is_call(siszx__dua) and find_callname(f_ir, siszx__dua) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        ofkh__nuwq = siszx__dua.args[0]
        siszx__dua = get_definition(f_ir, ofkh__nuwq)
    require(is_expr(siszx__dua, 'build_tuple') or is_expr(siszx__dua,
        'build_list'))
    return len(siszx__dua.items), rxxxb__ypa


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    ifr__lileu = []
    ocnt__uha = []
    values = []
    for ibxs__zwr, the__qsve in build_map.items:
        ybc__txj = find_const(f_ir, ibxs__zwr)
        require(isinstance(ybc__txj, str))
        ocnt__uha.append(ybc__txj)
        ifr__lileu.append(ibxs__zwr)
        values.append(the__qsve)
    pfuz__mcw = ir.Var(scope, mk_unique_var('val_tup'), loc)
    ecvo__sia = ir.Assign(ir.Expr.build_tuple(values, loc), pfuz__mcw, loc)
    f_ir._definitions[pfuz__mcw.name] = [ecvo__sia.value]
    effv__dtjsx = ir.Var(scope, mk_unique_var('key_tup'), loc)
    lqqet__zom = ir.Assign(ir.Expr.build_tuple(ifr__lileu, loc),
        effv__dtjsx, loc)
    f_ir._definitions[effv__dtjsx.name] = [lqqet__zom.value]
    if typemap is not None:
        typemap[pfuz__mcw.name] = types.Tuple([typemap[the__qsve.name] for
            the__qsve in values])
        typemap[effv__dtjsx.name] = types.Tuple([typemap[the__qsve.name] for
            the__qsve in ifr__lileu])
    return ocnt__uha, pfuz__mcw, ecvo__sia, effv__dtjsx, lqqet__zom


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    iyc__vljbl = block.body[-1].value
    gjy__ics = guard(get_definition, f_ir, iyc__vljbl)
    require(is_expr(gjy__ics, 'cast'))
    pmv__qenih = guard(get_definition, f_ir, gjy__ics.value)
    require(is_expr(pmv__qenih, 'build_map'))
    require(len(pmv__qenih.items) > 0)
    loc = block.loc
    scope = block.scope
    ocnt__uha, pfuz__mcw, ecvo__sia, effv__dtjsx, lqqet__zom = (
        extract_keyvals_from_struct_map(f_ir, pmv__qenih, loc, scope))
    inu__wgh = ir.Var(scope, mk_unique_var('conv_call'), loc)
    seq__avnwo = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), inu__wgh, loc)
    f_ir._definitions[inu__wgh.name] = [seq__avnwo.value]
    ogepi__nym = ir.Var(scope, mk_unique_var('struct_val'), loc)
    htc__rkstg = ir.Assign(ir.Expr.call(inu__wgh, [pfuz__mcw, effv__dtjsx],
        {}, loc), ogepi__nym, loc)
    f_ir._definitions[ogepi__nym.name] = [htc__rkstg.value]
    gjy__ics.value = ogepi__nym
    pmv__qenih.items = [(ibxs__zwr, ibxs__zwr) for ibxs__zwr, grbyn__qqbwl in
        pmv__qenih.items]
    block.body = block.body[:-2] + [ecvo__sia, lqqet__zom, seq__avnwo,
        htc__rkstg] + block.body[-2:]
    return tuple(ocnt__uha)


def get_struct_keynames(f_ir, typemap):
    wxpc__iifwa = compute_cfg_from_blocks(f_ir.blocks)
    kzuc__rhts = list(wxpc__iifwa.exit_points())[0]
    block = f_ir.blocks[kzuc__rhts]
    require(isinstance(block.body[-1], ir.Return))
    iyc__vljbl = block.body[-1].value
    gjy__ics = guard(get_definition, f_ir, iyc__vljbl)
    require(is_expr(gjy__ics, 'cast'))
    pmv__qenih = guard(get_definition, f_ir, gjy__ics.value)
    require(is_call(pmv__qenih) and find_callname(f_ir, pmv__qenih) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[pmv__qenih.args[1].name])


def fix_struct_return(f_ir):
    agpth__caj = None
    wxpc__iifwa = compute_cfg_from_blocks(f_ir.blocks)
    for kzuc__rhts in wxpc__iifwa.exit_points():
        agpth__caj = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            kzuc__rhts], kzuc__rhts)
    return agpth__caj


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    yno__jwhek = ir.Block(ir.Scope(None, loc), loc)
    yno__jwhek.body = node_list
    build_definitions({(0): yno__jwhek}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(the__qsve) for the__qsve in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    oshws__nxpt = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(oshws__nxpt, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for hasu__jtxj in range(len(vals) - 1, -1, -1):
        the__qsve = vals[hasu__jtxj]
        if isinstance(the__qsve, str) and the__qsve.startswith(
            NESTED_TUP_SENTINEL):
            mckw__dgvl = int(the__qsve[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:hasu__jtxj]) + (
                tuple(vals[hasu__jtxj + 1:hasu__jtxj + mckw__dgvl + 1]),) +
                tuple(vals[hasu__jtxj + mckw__dgvl + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    kbgvq__qwh = None
    if len(args) > arg_no and arg_no >= 0:
        kbgvq__qwh = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        kbgvq__qwh = kws[arg_name]
    if kbgvq__qwh is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return kbgvq__qwh


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
    puwnj__heep = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        puwnj__heep.update(extra_globals)
    func.__globals__.update(puwnj__heep)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            auvuh__uvqo = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[auvuh__uvqo.name] = types.literal(default)
            except:
                pass_info.typemap[auvuh__uvqo.name] = numba.typeof(default)
            mbun__buht = ir.Assign(ir.Const(default, loc), auvuh__uvqo, loc)
            pre_nodes.append(mbun__buht)
            return auvuh__uvqo
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    fhvs__voetm = tuple(pass_info.typemap[the__qsve.name] for the__qsve in args
        )
    if const:
        kwbpl__hcypc = []
        for hasu__jtxj, kbgvq__qwh in enumerate(args):
            zsjhz__dojol = guard(find_const, pass_info.func_ir, kbgvq__qwh)
            if zsjhz__dojol:
                kwbpl__hcypc.append(types.literal(zsjhz__dojol))
            else:
                kwbpl__hcypc.append(fhvs__voetm[hasu__jtxj])
        fhvs__voetm = tuple(kwbpl__hcypc)
    return ReplaceFunc(func, fhvs__voetm, args, puwnj__heep,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(xmj__twuqq) for xmj__twuqq in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        vhe__ybx = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {vhe__ybx} = 0\n', (vhe__ybx,)
    if isinstance(t, ArrayItemArrayType):
        fuz__lib, eyowl__ysb = gen_init_varsize_alloc_sizes(t.dtype)
        vhe__ybx = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {vhe__ybx} = 0\n' + fuz__lib, (vhe__ybx,) + eyowl__ysb
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
        return 1 + sum(get_type_alloc_counts(xmj__twuqq.dtype) for
            xmj__twuqq in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(xmj__twuqq) for xmj__twuqq in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(xmj__twuqq) for xmj__twuqq in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    nffm__nttr = typing_context.resolve_getattr(obj_dtype, func_name)
    if nffm__nttr is None:
        tmx__lroej = types.misc.Module(np)
        try:
            nffm__nttr = typing_context.resolve_getattr(tmx__lroej, func_name)
        except AttributeError as soqw__mbcf:
            nffm__nttr = None
        if nffm__nttr is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return nffm__nttr


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    nffm__nttr = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(nffm__nttr, types.BoundFunction):
        if axis is not None:
            fkijl__xrd = nffm__nttr.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            fkijl__xrd = nffm__nttr.get_call_type(typing_context, (), {})
        return fkijl__xrd.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(nffm__nttr):
            fkijl__xrd = nffm__nttr.get_call_type(typing_context, (
                obj_dtype,), {})
            return fkijl__xrd.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    nffm__nttr = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(nffm__nttr, types.BoundFunction):
        kxp__daf = nffm__nttr.template
        if axis is not None:
            return kxp__daf._overload_func(obj_dtype, axis=axis)
        else:
            return kxp__daf._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    ncmf__jhe = get_definition(func_ir, dict_var)
    require(isinstance(ncmf__jhe, ir.Expr))
    require(ncmf__jhe.op == 'build_map')
    ksou__gvqdc = ncmf__jhe.items
    ifr__lileu = []
    values = []
    nwas__kpmh = False
    for hasu__jtxj in range(len(ksou__gvqdc)):
        sbiqp__nogp, value = ksou__gvqdc[hasu__jtxj]
        try:
            hfv__rctz = get_const_value_inner(func_ir, sbiqp__nogp,
                arg_types, typemap, updated_containers)
            ifr__lileu.append(hfv__rctz)
            values.append(value)
        except GuardException as soqw__mbcf:
            require_const_map[sbiqp__nogp] = label
            nwas__kpmh = True
    if nwas__kpmh:
        raise GuardException
    return ifr__lileu, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        ifr__lileu = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as soqw__mbcf:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in ifr__lileu):
        raise BodoError(err_msg, loc)
    return ifr__lileu


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    ifr__lileu = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    tkilu__spel = []
    xqm__ozkp = [bodo.transforms.typing_pass._create_const_var(ibxs__zwr,
        'dict_key', scope, loc, tkilu__spel) for ibxs__zwr in ifr__lileu]
    ztme__vxr = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        ohos__gigjr = ir.Var(scope, mk_unique_var('sentinel'), loc)
        htpl__kophi = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        tkilu__spel.append(ir.Assign(ir.Const('__bodo_tup', loc),
            ohos__gigjr, loc))
        qxcnc__yvwx = [ohos__gigjr] + xqm__ozkp + ztme__vxr
        tkilu__spel.append(ir.Assign(ir.Expr.build_tuple(qxcnc__yvwx, loc),
            htpl__kophi, loc))
        return (htpl__kophi,), tkilu__spel
    else:
        ldrf__mcnc = ir.Var(scope, mk_unique_var('values_tup'), loc)
        ylu__tigdp = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        tkilu__spel.append(ir.Assign(ir.Expr.build_tuple(ztme__vxr, loc),
            ldrf__mcnc, loc))
        tkilu__spel.append(ir.Assign(ir.Expr.build_tuple(xqm__ozkp, loc),
            ylu__tigdp, loc))
        return (ldrf__mcnc, ylu__tigdp), tkilu__spel
