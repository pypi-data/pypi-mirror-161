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
    mnpzl__lnuga = tuple(call_list)
    if mnpzl__lnuga in no_side_effect_call_tuples:
        return True
    if mnpzl__lnuga == (bodo.hiframes.pd_index_ext.init_range_index,):
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
    if len(mnpzl__lnuga) == 1 and tuple in getattr(mnpzl__lnuga[0],
        '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=False, add_default_globals=True):
    if replace_globals:
        wtbk__lcbzv = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
            'math': math}
    else:
        wtbk__lcbzv = func.__globals__
    if extra_globals is not None:
        wtbk__lcbzv.update(extra_globals)
    if add_default_globals:
        wtbk__lcbzv.update({'numba': numba, 'np': np, 'bodo': bodo, 'pd':
            pd, 'math': math})
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, wtbk__lcbzv, typingctx=typing_info
            .typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[mip__sdx.name] for mip__sdx in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, wtbk__lcbzv)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        sivub__item = tuple(typing_info.typemap[mip__sdx.name] for mip__sdx in
            args)
        trn__gayn = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, sivub__item, {}, {}, flags)
        trn__gayn.run()
    eqpc__czbg = f_ir.blocks.popitem()[1]
    replace_arg_nodes(eqpc__czbg, args)
    dodc__oozn = eqpc__czbg.body[:-2]
    update_locs(dodc__oozn[len(args):], loc)
    for stmt in dodc__oozn[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        awwo__pqh = eqpc__czbg.body[-2]
        assert is_assign(awwo__pqh) and is_expr(awwo__pqh.value, 'cast')
        ourkr__eusht = awwo__pqh.value.value
        dodc__oozn.append(ir.Assign(ourkr__eusht, ret_var, loc))
    return dodc__oozn


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for uufbt__kcgts in stmt.list_vars():
            uufbt__kcgts.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        omla__rijh = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        cicpx__dfcz, kcrm__fjq = omla__rijh(stmt)
        return kcrm__fjq
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        flu__ugce = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(flu__ugce, ir.UndefinedType):
            tbzq__tpl = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{tbzq__tpl}' is not defined", loc=loc)
    except GuardException as fjg__tlh:
        raise BodoError(err_msg, loc=loc)
    return flu__ugce


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    nuz__dtnof = get_definition(func_ir, var)
    ppjh__dcrw = None
    if typemap is not None:
        ppjh__dcrw = typemap.get(var.name, None)
    if isinstance(nuz__dtnof, ir.Arg) and arg_types is not None:
        ppjh__dcrw = arg_types[nuz__dtnof.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(ppjh__dcrw):
        return get_literal_value(ppjh__dcrw)
    if isinstance(nuz__dtnof, (ir.Const, ir.Global, ir.FreeVar)):
        flu__ugce = nuz__dtnof.value
        return flu__ugce
    if literalize_args and isinstance(nuz__dtnof, ir.Arg
        ) and can_literalize_type(ppjh__dcrw, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({nuz__dtnof.index}, loc=var
            .loc, file_infos={nuz__dtnof.index: file_info} if file_info is not
            None else None)
    if is_expr(nuz__dtnof, 'binop'):
        if file_info and nuz__dtnof.fn == operator.add:
            try:
                icmuc__jkhds = get_const_value_inner(func_ir, nuz__dtnof.
                    lhs, arg_types, typemap, updated_containers,
                    literalize_args=False)
                file_info.set_concat(icmuc__jkhds, True)
                mbjx__nyh = get_const_value_inner(func_ir, nuz__dtnof.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return nuz__dtnof.fn(icmuc__jkhds, mbjx__nyh)
            except (GuardException, BodoConstUpdatedError) as fjg__tlh:
                pass
            try:
                mbjx__nyh = get_const_value_inner(func_ir, nuz__dtnof.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(mbjx__nyh, False)
                icmuc__jkhds = get_const_value_inner(func_ir, nuz__dtnof.
                    lhs, arg_types, typemap, updated_containers, file_info)
                return nuz__dtnof.fn(icmuc__jkhds, mbjx__nyh)
            except (GuardException, BodoConstUpdatedError) as fjg__tlh:
                pass
        icmuc__jkhds = get_const_value_inner(func_ir, nuz__dtnof.lhs,
            arg_types, typemap, updated_containers)
        mbjx__nyh = get_const_value_inner(func_ir, nuz__dtnof.rhs,
            arg_types, typemap, updated_containers)
        return nuz__dtnof.fn(icmuc__jkhds, mbjx__nyh)
    if is_expr(nuz__dtnof, 'unary'):
        flu__ugce = get_const_value_inner(func_ir, nuz__dtnof.value,
            arg_types, typemap, updated_containers)
        return nuz__dtnof.fn(flu__ugce)
    if is_expr(nuz__dtnof, 'getattr') and typemap:
        dou__zqfe = typemap.get(nuz__dtnof.value.name, None)
        if isinstance(dou__zqfe, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and nuz__dtnof.attr == 'columns':
            return pd.Index(dou__zqfe.columns)
        if isinstance(dou__zqfe, types.SliceType):
            vvrdy__bmyii = get_definition(func_ir, nuz__dtnof.value)
            require(is_call(vvrdy__bmyii))
            qpbap__jpq = find_callname(func_ir, vvrdy__bmyii)
            ymek__csshf = False
            if qpbap__jpq == ('_normalize_slice', 'numba.cpython.unicode'):
                require(nuz__dtnof.attr in ('start', 'step'))
                vvrdy__bmyii = get_definition(func_ir, vvrdy__bmyii.args[0])
                ymek__csshf = True
            require(find_callname(func_ir, vvrdy__bmyii) == ('slice',
                'builtins'))
            if len(vvrdy__bmyii.args) == 1:
                if nuz__dtnof.attr == 'start':
                    return 0
                if nuz__dtnof.attr == 'step':
                    return 1
                require(nuz__dtnof.attr == 'stop')
                return get_const_value_inner(func_ir, vvrdy__bmyii.args[0],
                    arg_types, typemap, updated_containers)
            if nuz__dtnof.attr == 'start':
                flu__ugce = get_const_value_inner(func_ir, vvrdy__bmyii.
                    args[0], arg_types, typemap, updated_containers)
                if flu__ugce is None:
                    flu__ugce = 0
                if ymek__csshf:
                    require(flu__ugce == 0)
                return flu__ugce
            if nuz__dtnof.attr == 'stop':
                assert not ymek__csshf
                return get_const_value_inner(func_ir, vvrdy__bmyii.args[1],
                    arg_types, typemap, updated_containers)
            require(nuz__dtnof.attr == 'step')
            if len(vvrdy__bmyii.args) == 2:
                return 1
            else:
                flu__ugce = get_const_value_inner(func_ir, vvrdy__bmyii.
                    args[2], arg_types, typemap, updated_containers)
                if flu__ugce is None:
                    flu__ugce = 1
                if ymek__csshf:
                    require(flu__ugce == 1)
                return flu__ugce
    if is_expr(nuz__dtnof, 'getattr'):
        return getattr(get_const_value_inner(func_ir, nuz__dtnof.value,
            arg_types, typemap, updated_containers), nuz__dtnof.attr)
    if is_expr(nuz__dtnof, 'getitem'):
        value = get_const_value_inner(func_ir, nuz__dtnof.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, nuz__dtnof.index, arg_types,
            typemap, updated_containers)
        return value[index]
    yzn__yqdfn = guard(find_callname, func_ir, nuz__dtnof, typemap)
    if yzn__yqdfn is not None and len(yzn__yqdfn) == 2 and yzn__yqdfn[0
        ] == 'keys' and isinstance(yzn__yqdfn[1], ir.Var):
        uznyq__xejae = nuz__dtnof.func
        nuz__dtnof = get_definition(func_ir, yzn__yqdfn[1])
        prk__ecy = yzn__yqdfn[1].name
        if updated_containers and prk__ecy in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                prk__ecy, updated_containers[prk__ecy]))
        require(is_expr(nuz__dtnof, 'build_map'))
        vals = [uufbt__kcgts[0] for uufbt__kcgts in nuz__dtnof.items]
        auryx__updd = guard(get_definition, func_ir, uznyq__xejae)
        assert isinstance(auryx__updd, ir.Expr) and auryx__updd.attr == 'keys'
        auryx__updd.attr = 'copy'
        return [get_const_value_inner(func_ir, uufbt__kcgts, arg_types,
            typemap, updated_containers) for uufbt__kcgts in vals]
    if is_expr(nuz__dtnof, 'build_map'):
        return {get_const_value_inner(func_ir, uufbt__kcgts[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            uufbt__kcgts[1], arg_types, typemap, updated_containers) for
            uufbt__kcgts in nuz__dtnof.items}
    if is_expr(nuz__dtnof, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, uufbt__kcgts, arg_types,
            typemap, updated_containers) for uufbt__kcgts in nuz__dtnof.items)
    if is_expr(nuz__dtnof, 'build_list'):
        return [get_const_value_inner(func_ir, uufbt__kcgts, arg_types,
            typemap, updated_containers) for uufbt__kcgts in nuz__dtnof.items]
    if is_expr(nuz__dtnof, 'build_set'):
        return {get_const_value_inner(func_ir, uufbt__kcgts, arg_types,
            typemap, updated_containers) for uufbt__kcgts in nuz__dtnof.items}
    if yzn__yqdfn == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, nuz__dtnof.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if yzn__yqdfn == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, nuz__dtnof.args[0],
            arg_types, typemap, updated_containers))
    if yzn__yqdfn == ('range', 'builtins') and len(nuz__dtnof.args) == 1:
        return range(get_const_value_inner(func_ir, nuz__dtnof.args[0],
            arg_types, typemap, updated_containers))
    if yzn__yqdfn == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, uufbt__kcgts,
            arg_types, typemap, updated_containers) for uufbt__kcgts in
            nuz__dtnof.args))
    if yzn__yqdfn == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, nuz__dtnof.args[0],
            arg_types, typemap, updated_containers))
    if yzn__yqdfn == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, nuz__dtnof.args[0],
            arg_types, typemap, updated_containers))
    if yzn__yqdfn == ('format', 'builtins'):
        mip__sdx = get_const_value_inner(func_ir, nuz__dtnof.args[0],
            arg_types, typemap, updated_containers)
        gqe__hfq = get_const_value_inner(func_ir, nuz__dtnof.args[1],
            arg_types, typemap, updated_containers) if len(nuz__dtnof.args
            ) > 1 else ''
        return format(mip__sdx, gqe__hfq)
    if yzn__yqdfn in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, nuz__dtnof.args[0],
            arg_types, typemap, updated_containers))
    if yzn__yqdfn == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, nuz__dtnof.args[0],
            arg_types, typemap, updated_containers))
    if yzn__yqdfn == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, nuz__dtnof.args
            [0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, nuz__dtnof.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            nuz__dtnof.args[2], arg_types, typemap, updated_containers))
    if yzn__yqdfn == ('len', 'builtins') and typemap and isinstance(typemap
        .get(nuz__dtnof.args[0].name, None), types.BaseTuple):
        return len(typemap[nuz__dtnof.args[0].name])
    if yzn__yqdfn == ('len', 'builtins'):
        zypk__geqp = guard(get_definition, func_ir, nuz__dtnof.args[0])
        if isinstance(zypk__geqp, ir.Expr) and zypk__geqp.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(zypk__geqp.items)
        return len(get_const_value_inner(func_ir, nuz__dtnof.args[0],
            arg_types, typemap, updated_containers))
    if yzn__yqdfn == ('CategoricalDtype', 'pandas'):
        kws = dict(nuz__dtnof.kws)
        gwe__obi = get_call_expr_arg('CategoricalDtype', nuz__dtnof.args,
            kws, 0, 'categories', '')
        vbkot__xuyob = get_call_expr_arg('CategoricalDtype', nuz__dtnof.
            args, kws, 1, 'ordered', False)
        if vbkot__xuyob is not False:
            vbkot__xuyob = get_const_value_inner(func_ir, vbkot__xuyob,
                arg_types, typemap, updated_containers)
        if gwe__obi == '':
            gwe__obi = None
        else:
            gwe__obi = get_const_value_inner(func_ir, gwe__obi, arg_types,
                typemap, updated_containers)
        return pd.CategoricalDtype(gwe__obi, vbkot__xuyob)
    if yzn__yqdfn == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, nuz__dtnof.args[0],
            arg_types, typemap, updated_containers))
    if yzn__yqdfn is not None and len(yzn__yqdfn) == 2 and yzn__yqdfn[1
        ] == 'pandas' and yzn__yqdfn[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, yzn__yqdfn[0])()
    if yzn__yqdfn is not None and len(yzn__yqdfn) == 2 and isinstance(
        yzn__yqdfn[1], ir.Var):
        flu__ugce = get_const_value_inner(func_ir, yzn__yqdfn[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, uufbt__kcgts, arg_types,
            typemap, updated_containers) for uufbt__kcgts in nuz__dtnof.args]
        kws = {fubt__piye[0]: get_const_value_inner(func_ir, fubt__piye[1],
            arg_types, typemap, updated_containers) for fubt__piye in
            nuz__dtnof.kws}
        return getattr(flu__ugce, yzn__yqdfn[0])(*args, **kws)
    if yzn__yqdfn is not None and len(yzn__yqdfn) == 2 and yzn__yqdfn[1
        ] == 'bodo' and yzn__yqdfn[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, uufbt__kcgts, arg_types,
            typemap, updated_containers) for uufbt__kcgts in nuz__dtnof.args)
        kwargs = {tbzq__tpl: get_const_value_inner(func_ir, uufbt__kcgts,
            arg_types, typemap, updated_containers) for tbzq__tpl,
            uufbt__kcgts in dict(nuz__dtnof.kws).items()}
        return getattr(bodo, yzn__yqdfn[0])(*args, **kwargs)
    if is_call(nuz__dtnof) and typemap and isinstance(typemap.get(
        nuz__dtnof.func.name, None), types.Dispatcher):
        py_func = typemap[nuz__dtnof.func.name].dispatcher.py_func
        require(nuz__dtnof.vararg is None)
        args = tuple(get_const_value_inner(func_ir, uufbt__kcgts, arg_types,
            typemap, updated_containers) for uufbt__kcgts in nuz__dtnof.args)
        kwargs = {tbzq__tpl: get_const_value_inner(func_ir, uufbt__kcgts,
            arg_types, typemap, updated_containers) for tbzq__tpl,
            uufbt__kcgts in dict(nuz__dtnof.kws).items()}
        arg_types = tuple(bodo.typeof(uufbt__kcgts) for uufbt__kcgts in args)
        kw_types = {vbt__ecasi: bodo.typeof(uufbt__kcgts) for vbt__ecasi,
            uufbt__kcgts in kwargs.items()}
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
    f_ir, typemap, usk__lhgu, usk__lhgu = bodo.compiler.get_func_type_info(
        py_func, arg_types, kw_types)
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
                    anl__ymlub = guard(get_definition, f_ir, rhs.func)
                    if isinstance(anl__ymlub, ir.Const) and isinstance(
                        anl__ymlub.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    cakz__jxvyw = guard(find_callname, f_ir, rhs)
                    if cakz__jxvyw is None:
                        return False
                    func_name, jghy__hcww = cakz__jxvyw
                    if jghy__hcww == 'pandas' and func_name.startswith('read_'
                        ):
                        return False
                    if cakz__jxvyw in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if cakz__jxvyw == ('File', 'h5py'):
                        return False
                    if isinstance(jghy__hcww, ir.Var):
                        ppjh__dcrw = typemap[jghy__hcww.name]
                        if isinstance(ppjh__dcrw, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(ppjh__dcrw, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(ppjh__dcrw, bodo.LoggingLoggerType):
                            return False
                        if str(ppjh__dcrw).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            jghy__hcww), ir.Arg)):
                            return False
                    if jghy__hcww in ('numpy.random', 'time', 'logging',
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
        ytava__mfd = func.literal_value.code
        fllgl__vcf = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            fllgl__vcf = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(fllgl__vcf, ytava__mfd)
        fix_struct_return(f_ir)
        typemap, dyug__qqdj, btpk__lmwh, usk__lhgu = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, btpk__lmwh, dyug__qqdj = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, btpk__lmwh, dyug__qqdj = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, btpk__lmwh, dyug__qqdj = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(dyug__qqdj, types.DictType):
        qaiqc__suiia = guard(get_struct_keynames, f_ir, typemap)
        if qaiqc__suiia is not None:
            dyug__qqdj = StructType((dyug__qqdj.value_type,) * len(
                qaiqc__suiia), qaiqc__suiia)
    if is_udf and isinstance(dyug__qqdj, (SeriesType, HeterogeneousSeriesType)
        ):
        guuok__tqemy = numba.core.registry.cpu_target.typing_context
        jhsip__riuku = numba.core.registry.cpu_target.target_context
        wuo__awpl = bodo.transforms.series_pass.SeriesPass(f_ir,
            guuok__tqemy, jhsip__riuku, typemap, btpk__lmwh, {})
        wuo__awpl.run()
        wuo__awpl.run()
        wuo__awpl.run()
        qqg__fbdk = compute_cfg_from_blocks(f_ir.blocks)
        uezrw__adx = [guard(_get_const_series_info, f_ir.blocks[hrpvj__xyzi
            ], f_ir, typemap) for hrpvj__xyzi in qqg__fbdk.exit_points() if
            isinstance(f_ir.blocks[hrpvj__xyzi].body[-1], ir.Return)]
        if None in uezrw__adx or len(pd.Series(uezrw__adx).unique()) != 1:
            dyug__qqdj.const_info = None
        else:
            dyug__qqdj.const_info = uezrw__adx[0]
    return dyug__qqdj


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    tsz__fudw = block.body[-1].value
    mjld__nmm = get_definition(f_ir, tsz__fudw)
    require(is_expr(mjld__nmm, 'cast'))
    mjld__nmm = get_definition(f_ir, mjld__nmm.value)
    require(is_call(mjld__nmm) and find_callname(f_ir, mjld__nmm) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    axur__ogd = mjld__nmm.args[1]
    naos__djoy = tuple(get_const_value_inner(f_ir, axur__ogd, typemap=typemap))
    if isinstance(typemap[tsz__fudw.name], HeterogeneousSeriesType):
        return len(typemap[tsz__fudw.name].data), naos__djoy
    vhx__ydgpf = mjld__nmm.args[0]
    eke__sygjg = get_definition(f_ir, vhx__ydgpf)
    func_name, ugx__oxdet = find_callname(f_ir, eke__sygjg)
    if is_call(eke__sygjg) and bodo.utils.utils.is_alloc_callname(func_name,
        ugx__oxdet):
        hxaji__cvmas = eke__sygjg.args[0]
        etcgf__gubeh = get_const_value_inner(f_ir, hxaji__cvmas, typemap=
            typemap)
        return etcgf__gubeh, naos__djoy
    if is_call(eke__sygjg) and find_callname(f_ir, eke__sygjg) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence',
        'bodo.libs.str_arr_ext'), ('build_nullable_tuple',
        'bodo.libs.nullable_tuple_ext')]:
        vhx__ydgpf = eke__sygjg.args[0]
        eke__sygjg = get_definition(f_ir, vhx__ydgpf)
    require(is_expr(eke__sygjg, 'build_tuple') or is_expr(eke__sygjg,
        'build_list'))
    return len(eke__sygjg.items), naos__djoy


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    thw__rnvn = []
    kqbg__lgdij = []
    values = []
    for vbt__ecasi, uufbt__kcgts in build_map.items:
        ycyxx__nkha = find_const(f_ir, vbt__ecasi)
        require(isinstance(ycyxx__nkha, str))
        kqbg__lgdij.append(ycyxx__nkha)
        thw__rnvn.append(vbt__ecasi)
        values.append(uufbt__kcgts)
    vzzx__bqrpz = ir.Var(scope, mk_unique_var('val_tup'), loc)
    ajr__qnmut = ir.Assign(ir.Expr.build_tuple(values, loc), vzzx__bqrpz, loc)
    f_ir._definitions[vzzx__bqrpz.name] = [ajr__qnmut.value]
    rve__gqzv = ir.Var(scope, mk_unique_var('key_tup'), loc)
    hjq__jsz = ir.Assign(ir.Expr.build_tuple(thw__rnvn, loc), rve__gqzv, loc)
    f_ir._definitions[rve__gqzv.name] = [hjq__jsz.value]
    if typemap is not None:
        typemap[vzzx__bqrpz.name] = types.Tuple([typemap[uufbt__kcgts.name] for
            uufbt__kcgts in values])
        typemap[rve__gqzv.name] = types.Tuple([typemap[uufbt__kcgts.name] for
            uufbt__kcgts in thw__rnvn])
    return kqbg__lgdij, vzzx__bqrpz, ajr__qnmut, rve__gqzv, hjq__jsz


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    lxqff__jjbfs = block.body[-1].value
    weosl__thz = guard(get_definition, f_ir, lxqff__jjbfs)
    require(is_expr(weosl__thz, 'cast'))
    mjld__nmm = guard(get_definition, f_ir, weosl__thz.value)
    require(is_expr(mjld__nmm, 'build_map'))
    require(len(mjld__nmm.items) > 0)
    loc = block.loc
    scope = block.scope
    kqbg__lgdij, vzzx__bqrpz, ajr__qnmut, rve__gqzv, hjq__jsz = (
        extract_keyvals_from_struct_map(f_ir, mjld__nmm, loc, scope))
    owxk__xznb = ir.Var(scope, mk_unique_var('conv_call'), loc)
    ujst__evmsn = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), owxk__xznb, loc)
    f_ir._definitions[owxk__xznb.name] = [ujst__evmsn.value]
    ufx__ckvhl = ir.Var(scope, mk_unique_var('struct_val'), loc)
    taz__ndc = ir.Assign(ir.Expr.call(owxk__xznb, [vzzx__bqrpz, rve__gqzv],
        {}, loc), ufx__ckvhl, loc)
    f_ir._definitions[ufx__ckvhl.name] = [taz__ndc.value]
    weosl__thz.value = ufx__ckvhl
    mjld__nmm.items = [(vbt__ecasi, vbt__ecasi) for vbt__ecasi, usk__lhgu in
        mjld__nmm.items]
    block.body = block.body[:-2] + [ajr__qnmut, hjq__jsz, ujst__evmsn, taz__ndc
        ] + block.body[-2:]
    return tuple(kqbg__lgdij)


def get_struct_keynames(f_ir, typemap):
    qqg__fbdk = compute_cfg_from_blocks(f_ir.blocks)
    lexl__vjbld = list(qqg__fbdk.exit_points())[0]
    block = f_ir.blocks[lexl__vjbld]
    require(isinstance(block.body[-1], ir.Return))
    lxqff__jjbfs = block.body[-1].value
    weosl__thz = guard(get_definition, f_ir, lxqff__jjbfs)
    require(is_expr(weosl__thz, 'cast'))
    mjld__nmm = guard(get_definition, f_ir, weosl__thz.value)
    require(is_call(mjld__nmm) and find_callname(f_ir, mjld__nmm) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[mjld__nmm.args[1].name])


def fix_struct_return(f_ir):
    khr__uqu = None
    qqg__fbdk = compute_cfg_from_blocks(f_ir.blocks)
    for lexl__vjbld in qqg__fbdk.exit_points():
        khr__uqu = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            lexl__vjbld], lexl__vjbld)
    return khr__uqu


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    huq__idhli = ir.Block(ir.Scope(None, loc), loc)
    huq__idhli.body = node_list
    build_definitions({(0): huq__idhli}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(uufbt__kcgts) for uufbt__kcgts in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    zsfxu__uab = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(zsfxu__uab, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for caoh__notpm in range(len(vals) - 1, -1, -1):
        uufbt__kcgts = vals[caoh__notpm]
        if isinstance(uufbt__kcgts, str) and uufbt__kcgts.startswith(
            NESTED_TUP_SENTINEL):
            qlgj__ykqlv = int(uufbt__kcgts[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:caoh__notpm]) + (
                tuple(vals[caoh__notpm + 1:caoh__notpm + qlgj__ykqlv + 1]),
                ) + tuple(vals[caoh__notpm + qlgj__ykqlv + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    mip__sdx = None
    if len(args) > arg_no and arg_no >= 0:
        mip__sdx = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        mip__sdx = kws[arg_name]
    if mip__sdx is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return mip__sdx


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
    wtbk__lcbzv = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        wtbk__lcbzv.update(extra_globals)
    func.__globals__.update(wtbk__lcbzv)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            kqwl__eibp = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[kqwl__eibp.name] = types.literal(default)
            except:
                pass_info.typemap[kqwl__eibp.name] = numba.typeof(default)
            ogl__goe = ir.Assign(ir.Const(default, loc), kqwl__eibp, loc)
            pre_nodes.append(ogl__goe)
            return kqwl__eibp
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    sivub__item = tuple(pass_info.typemap[uufbt__kcgts.name] for
        uufbt__kcgts in args)
    if const:
        xoe__wlhxo = []
        for caoh__notpm, mip__sdx in enumerate(args):
            flu__ugce = guard(find_const, pass_info.func_ir, mip__sdx)
            if flu__ugce:
                xoe__wlhxo.append(types.literal(flu__ugce))
            else:
                xoe__wlhxo.append(sivub__item[caoh__notpm])
        sivub__item = tuple(xoe__wlhxo)
    return ReplaceFunc(func, sivub__item, args, wtbk__lcbzv,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(ngl__mgf) for ngl__mgf in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        ghrj__dnqg = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {ghrj__dnqg} = 0\n', (ghrj__dnqg,)
    if isinstance(t, ArrayItemArrayType):
        svur__poutx, tley__yab = gen_init_varsize_alloc_sizes(t.dtype)
        ghrj__dnqg = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {ghrj__dnqg} = 0\n' + svur__poutx, (ghrj__dnqg,) + tley__yab
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
        return 1 + sum(get_type_alloc_counts(ngl__mgf.dtype) for ngl__mgf in
            t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(ngl__mgf) for ngl__mgf in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(ngl__mgf) for ngl__mgf in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    oxlph__hcqiy = typing_context.resolve_getattr(obj_dtype, func_name)
    if oxlph__hcqiy is None:
        szw__phfo = types.misc.Module(np)
        try:
            oxlph__hcqiy = typing_context.resolve_getattr(szw__phfo, func_name)
        except AttributeError as fjg__tlh:
            oxlph__hcqiy = None
        if oxlph__hcqiy is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return oxlph__hcqiy


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    oxlph__hcqiy = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(oxlph__hcqiy, types.BoundFunction):
        if axis is not None:
            cooh__aeow = oxlph__hcqiy.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            cooh__aeow = oxlph__hcqiy.get_call_type(typing_context, (), {})
        return cooh__aeow.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(oxlph__hcqiy):
            cooh__aeow = oxlph__hcqiy.get_call_type(typing_context, (
                obj_dtype,), {})
            return cooh__aeow.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    oxlph__hcqiy = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(oxlph__hcqiy, types.BoundFunction):
        nqfmp__qpc = oxlph__hcqiy.template
        if axis is not None:
            return nqfmp__qpc._overload_func(obj_dtype, axis=axis)
        else:
            return nqfmp__qpc._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    vffy__vucz = get_definition(func_ir, dict_var)
    require(isinstance(vffy__vucz, ir.Expr))
    require(vffy__vucz.op == 'build_map')
    fvcbq__xcjyn = vffy__vucz.items
    thw__rnvn = []
    values = []
    snb__xummr = False
    for caoh__notpm in range(len(fvcbq__xcjyn)):
        ykvp__vnx, value = fvcbq__xcjyn[caoh__notpm]
        try:
            kqbz__hghnz = get_const_value_inner(func_ir, ykvp__vnx,
                arg_types, typemap, updated_containers)
            thw__rnvn.append(kqbz__hghnz)
            values.append(value)
        except GuardException as fjg__tlh:
            require_const_map[ykvp__vnx] = label
            snb__xummr = True
    if snb__xummr:
        raise GuardException
    return thw__rnvn, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        thw__rnvn = tuple(get_const_value_inner(func_ir, t[0], args) for t in
            build_map.items)
    except GuardException as fjg__tlh:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in thw__rnvn):
        raise BodoError(err_msg, loc)
    return thw__rnvn


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    thw__rnvn = _get_const_keys_from_dict(args, func_ir, build_map, err_msg,
        loc)
    uawk__jeqa = []
    nlvyi__jimvl = [bodo.transforms.typing_pass._create_const_var(
        vbt__ecasi, 'dict_key', scope, loc, uawk__jeqa) for vbt__ecasi in
        thw__rnvn]
    yyo__irw = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        qnz__cck = ir.Var(scope, mk_unique_var('sentinel'), loc)
        tfkmf__ngvx = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        uawk__jeqa.append(ir.Assign(ir.Const('__bodo_tup', loc), qnz__cck, loc)
            )
        pvbd__dvg = [qnz__cck] + nlvyi__jimvl + yyo__irw
        uawk__jeqa.append(ir.Assign(ir.Expr.build_tuple(pvbd__dvg, loc),
            tfkmf__ngvx, loc))
        return (tfkmf__ngvx,), uawk__jeqa
    else:
        pygia__ssobw = ir.Var(scope, mk_unique_var('values_tup'), loc)
        mrk__zza = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        uawk__jeqa.append(ir.Assign(ir.Expr.build_tuple(yyo__irw, loc),
            pygia__ssobw, loc))
        uawk__jeqa.append(ir.Assign(ir.Expr.build_tuple(nlvyi__jimvl, loc),
            mrk__zza, loc))
        return (pygia__ssobw, mrk__zza), uawk__jeqa
