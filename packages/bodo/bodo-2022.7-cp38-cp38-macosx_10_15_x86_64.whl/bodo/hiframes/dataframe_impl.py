"""
Implementation of DataFrame attributes and methods using overload.
"""
import operator
import re
import warnings
from collections import namedtuple
from typing import Tuple
import numba
import numpy as np
import pandas as pd
from numba.core import cgutils, ir, types
from numba.core.imputils import RefType, impl_ret_borrowed, impl_ret_new_ref, iternext_impl, lower_builtin
from numba.core.ir_utils import mk_unique_var, next_label
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_getattr, models, overload, overload_attribute, overload_method, register_model, type_callable
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import _no_input, datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported, handle_inplace_df_type_change
from bodo.hiframes.pd_index_ext import DatetimeIndexType, RangeIndexType, StringIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType, if_series_to_array_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array, boolean_dtype
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.transform import bodo_types_with_params, gen_const_tup, no_side_effect_call_tuples
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, check_unsupported_args, dtype_to_array_type, ensure_constant_arg, ensure_constant_values, get_index_data_arr_types, get_index_names, get_literal_value, get_nullable_and_non_nullable_types, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_overload_constant_dict, get_overload_constant_series, is_common_scalar_dtype, is_literal_type, is_overload_bool, is_overload_bool_list, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_int, is_overload_constant_list, is_overload_constant_series, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, parse_dtype, raise_bodo_error, unliteral_val
from bodo.utils.utils import is_array_typ


@overload_attribute(DataFrameType, 'index', inline='always')
def overload_dataframe_index(df):
    return lambda df: bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)


def generate_col_to_index_func_text(col_names: Tuple):
    if all(isinstance(a, str) for a in col_names) or all(isinstance(a,
        bytes) for a in col_names):
        ifbsq__ctw = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({ifbsq__ctw})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    rnem__hlqb = 'def impl(df):\n'
    if df.has_runtime_cols:
        rnem__hlqb += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        rcdtg__pqlrg = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        rnem__hlqb += f'  return {rcdtg__pqlrg}'
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo}, qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


@overload_attribute(DataFrameType, 'values')
def overload_dataframe_values(df):
    check_runtime_cols_unsupported(df, 'DataFrame.values')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.values')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.values: only supported for dataframes containing numeric values'
            )
    yvuos__faue = len(df.columns)
    nmlgl__lojxg = set(i for i in range(yvuos__faue) if isinstance(df.data[
        i], IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in nmlgl__lojxg else '') for i in
        range(yvuos__faue))
    rnem__hlqb = 'def f(df):\n'.format()
    rnem__hlqb += '    return np.stack(({},), 1)\n'.format(data_args)
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo, 'np': np}, qbsaf__jre)
    ntqn__xgftc = qbsaf__jre['f']
    return ntqn__xgftc


@overload_method(DataFrameType, 'to_numpy', inline='always', no_unliteral=True)
def overload_dataframe_to_numpy(df, dtype=None, copy=False, na_value=_no_input
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.to_numpy()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.to_numpy()')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.to_numpy(): only supported for dataframes containing numeric values'
            )
    wso__vfi = {'dtype': dtype, 'na_value': na_value}
    fqwi__okvxq = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', wso__vfi, fqwi__okvxq,
        package_name='pandas', module_name='DataFrame')

    def impl(df, dtype=None, copy=False, na_value=_no_input):
        return df.values
    return impl


@overload_attribute(DataFrameType, 'ndim', inline='always')
def overload_dataframe_ndim(df):
    return lambda df: 2


@overload_attribute(DataFrameType, 'size')
def overload_dataframe_size(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            qcwcu__bcvd = bodo.hiframes.table.compute_num_runtime_columns(t)
            return qcwcu__bcvd * len(t)
        return impl
    ncols = len(df.columns)
    return lambda df: ncols * len(df)


@lower_getattr(DataFrameType, 'shape')
def lower_dataframe_shape(context, builder, typ, val):
    impl = overload_dataframe_shape(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def overload_dataframe_shape(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            qcwcu__bcvd = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), qcwcu__bcvd
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    rnem__hlqb = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    pujo__axtnu = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    rnem__hlqb += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{pujo__axtnu}), {index}, None)
"""
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo}, qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


@overload_attribute(DataFrameType, 'empty')
def overload_dataframe_empty(df):
    check_runtime_cols_unsupported(df, 'DataFrame.empty')
    if len(df.columns) == 0:
        return lambda df: True
    return lambda df: len(df) == 0


@overload_method(DataFrameType, 'assign', no_unliteral=True)
def overload_dataframe_assign(df, **kwargs):
    check_runtime_cols_unsupported(df, 'DataFrame.assign()')
    raise_bodo_error('Invalid df.assign() call')


@overload_method(DataFrameType, 'insert', no_unliteral=True)
def overload_dataframe_insert(df, loc, column, value, allow_duplicates=False):
    check_runtime_cols_unsupported(df, 'DataFrame.insert()')
    raise_bodo_error('Invalid df.insert() call')


def _get_dtype_str(dtype):
    if isinstance(dtype, types.Function):
        if dtype.key[0] == str:
            return "'str'"
        elif dtype.key[0] == float:
            return 'float'
        elif dtype.key[0] == int:
            return 'int'
        elif dtype.key[0] == bool:
            return 'bool'
        else:
            raise BodoError(f'invalid dtype: {dtype}')
    if type(dtype) in bodo.libs.int_arr_ext.pd_int_dtype_classes:
        return dtype.name
    if isinstance(dtype, types.DTypeSpec):
        dtype = dtype.dtype
    if isinstance(dtype, types.functions.NumberClass):
        return f"'{dtype.key}'"
    if isinstance(dtype, types.PyObject) or dtype in (object, 'object'):
        return "'object'"
    if dtype in (bodo.libs.str_arr_ext.string_dtype, pd.StringDtype()):
        return 'str'
    return f"'{dtype}'"


@overload_method(DataFrameType, 'astype', inline='always', no_unliteral=True)
def overload_dataframe_astype(df, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True, _bodo_object_typeref=None):
    check_runtime_cols_unsupported(df, 'DataFrame.astype()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.astype()')
    wso__vfi = {'copy': copy, 'errors': errors}
    fqwi__okvxq = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', wso__vfi, fqwi__okvxq, package_name
        ='pandas', module_name='DataFrame')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "DataFrame.astype(): 'dtype' when passed as string must be a constant value"
            )
    extra_globals = None
    header = """def impl(df, dtype, copy=True, errors='raise', _bodo_nan_to_str=True, _bodo_object_typeref=None):
"""
    if df.is_table_format:
        extra_globals = {}
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        rgkug__cid = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        kjig__tlcmh = _bodo_object_typeref.instance_type
        assert isinstance(kjig__tlcmh, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in kjig__tlcmh.column_index:
                    idx = kjig__tlcmh.column_index[name]
                    arr_typ = kjig__tlcmh.data[idx]
                else:
                    arr_typ = df.data[i]
                rgkug__cid.append(arr_typ)
        else:
            extra_globals = {}
            qwdj__hlyjc = {}
            for i, name in enumerate(kjig__tlcmh.columns):
                arr_typ = kjig__tlcmh.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    ztfaf__puov = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    ztfaf__puov = boolean_dtype
                else:
                    ztfaf__puov = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = ztfaf__puov
                qwdj__hlyjc[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {qwdj__hlyjc[ttn__dffux]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if ttn__dffux in qwdj__hlyjc else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, ttn__dffux in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        tmjp__scsz = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            tmjp__scsz = {name: dtype_to_array_type(parse_dtype(dtype)) for
                name, dtype in tmjp__scsz.items()}
            for i, name in enumerate(df.columns):
                if name in tmjp__scsz:
                    arr_typ = tmjp__scsz[name]
                else:
                    arr_typ = df.data[i]
                rgkug__cid.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(tmjp__scsz[ttn__dffux])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if ttn__dffux in tmjp__scsz else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, ttn__dffux in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        rgkug__cid = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        zpu__rny = bodo.TableType(tuple(rgkug__cid))
        extra_globals['out_table_typ'] = zpu__rny
        data_args = (
            'bodo.utils.table_utils.table_astype(table, out_table_typ, copy, _bodo_nan_to_str)'
            )
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'copy', inline='always', no_unliteral=True)
def overload_dataframe_copy(df, deep=True):
    check_runtime_cols_unsupported(df, 'DataFrame.copy()')
    header = 'def impl(df, deep=True):\n'
    extra_globals = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        jjetq__nvh = types.none
        extra_globals = {'output_arr_typ': jjetq__nvh}
        if is_overload_false(deep):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
        elif is_overload_true(deep):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' + 'True)')
        else:
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' +
                'True) if deep else bodo.utils.table_utils.generate_mappable_table_func('
                 + 'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
    else:
        evr__zkbcz = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                evr__zkbcz.append(arr + '.copy()')
            elif is_overload_false(deep):
                evr__zkbcz.append(arr)
            else:
                evr__zkbcz.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(evr__zkbcz)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    wso__vfi = {'index': index, 'level': level, 'errors': errors}
    fqwi__okvxq = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', wso__vfi, fqwi__okvxq,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.rename(): 'inplace' keyword only supports boolean constant assignment"
            )
    if not is_overload_none(mapper):
        if not is_overload_none(columns):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'mapper' and 'columns'"
                )
        if not (is_overload_constant_int(axis) and get_overload_const_int(
            axis) == 1):
            raise BodoError(
                "DataFrame.rename(): 'mapper' only supported with axis=1")
        if not is_overload_constant_dict(mapper):
            raise_bodo_error(
                "'mapper' argument to DataFrame.rename() should be a constant dictionary"
                )
        ayjhe__cvlh = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        ayjhe__cvlh = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    kbjky__ijxnp = tuple([ayjhe__cvlh.get(df.columns[i], df.columns[i]) for
        i in range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    jql__djh = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        jql__djh = df.copy(columns=kbjky__ijxnp)
        jjetq__nvh = types.none
        extra_globals = {'output_arr_typ': jjetq__nvh}
        if is_overload_false(copy):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
        elif is_overload_true(copy):
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' + 'True)')
        else:
            data_args = (
                'bodo.utils.table_utils.generate_mappable_table_func(' +
                'table, ' + "'copy', " + 'output_arr_typ, ' +
                'True) if copy else bodo.utils.table_utils.generate_mappable_table_func('
                 + 'table, ' + 'None, ' + 'output_arr_typ, ' + 'True)')
    else:
        evr__zkbcz = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                evr__zkbcz.append(arr + '.copy()')
            elif is_overload_false(copy):
                evr__zkbcz.append(arr)
            else:
                evr__zkbcz.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(evr__zkbcz)
    return _gen_init_df(header, kbjky__ijxnp, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    stt__hsq = not is_overload_none(items)
    wmcq__tps = not is_overload_none(like)
    eta__lfsl = not is_overload_none(regex)
    hekxg__wjup = stt__hsq ^ wmcq__tps ^ eta__lfsl
    xmek__iseh = not (stt__hsq or wmcq__tps or eta__lfsl)
    if xmek__iseh:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not hekxg__wjup:
        raise BodoError(
            'DataFrame.filter(): keyword arguments `items`, `like`, and `regex` are mutually exclusive'
            )
    if is_overload_none(axis):
        axis = 'columns'
    if is_overload_constant_str(axis):
        axis = get_overload_const_str(axis)
        if axis not in {'index', 'columns'}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either "index" or "columns" if string'
                )
        hkf__lln = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        hkf__lln = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert hkf__lln in {0, 1}
    rnem__hlqb = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if hkf__lln == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if hkf__lln == 1:
        ibb__dlorp = []
        fiax__yhls = []
        tgrp__moax = []
        if stt__hsq:
            if is_overload_constant_list(items):
                rhpy__hcboq = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if wmcq__tps:
            if is_overload_constant_str(like):
                iqz__mhocz = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if eta__lfsl:
            if is_overload_constant_str(regex):
                kfr__souxe = get_overload_const_str(regex)
                rvco__ilwr = re.compile(kfr__souxe)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, ttn__dffux in enumerate(df.columns):
            if not is_overload_none(items
                ) and ttn__dffux in rhpy__hcboq or not is_overload_none(like
                ) and iqz__mhocz in str(ttn__dffux) or not is_overload_none(
                regex) and rvco__ilwr.search(str(ttn__dffux)):
                fiax__yhls.append(ttn__dffux)
                tgrp__moax.append(i)
        for i in tgrp__moax:
            var_name = f'data_{i}'
            ibb__dlorp.append(var_name)
            rnem__hlqb += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(ibb__dlorp)
        return _gen_init_df(rnem__hlqb, fiax__yhls, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    jql__djh = None
    if df.is_table_format:
        jjetq__nvh = types.Array(types.bool_, 1, 'C')
        jql__djh = DataFrameType(tuple([jjetq__nvh] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': jjetq__nvh}
        data_args = ('bodo.utils.table_utils.generate_mappable_table_func(' +
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), ' +
            "'bodo.libs.array_ops.array_op_isna', " + 'output_arr_typ, ' +
            'False)')
    else:
        data_args = ', '.join(
            f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'select_dtypes', inline='always',
    no_unliteral=True)
def overload_dataframe_select_dtypes(df, include=None, exclude=None):
    check_runtime_cols_unsupported(df, 'DataFrame.select_dtypes')
    ehucw__fdcm = is_overload_none(include)
    lzxr__viox = is_overload_none(exclude)
    hse__ode = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if ehucw__fdcm and lzxr__viox:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not ehucw__fdcm:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            hhm__zsx = [dtype_to_array_type(parse_dtype(elem, hse__ode)) for
                elem in include]
        elif is_legal_input(include):
            hhm__zsx = [dtype_to_array_type(parse_dtype(include, hse__ode))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        hhm__zsx = get_nullable_and_non_nullable_types(hhm__zsx)
        anuc__ifn = tuple(ttn__dffux for i, ttn__dffux in enumerate(df.
            columns) if df.data[i] in hhm__zsx)
    else:
        anuc__ifn = df.columns
    if not lzxr__viox:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            vvhmf__hkj = [dtype_to_array_type(parse_dtype(elem, hse__ode)) for
                elem in exclude]
        elif is_legal_input(exclude):
            vvhmf__hkj = [dtype_to_array_type(parse_dtype(exclude, hse__ode))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        vvhmf__hkj = get_nullable_and_non_nullable_types(vvhmf__hkj)
        anuc__ifn = tuple(ttn__dffux for ttn__dffux in anuc__ifn if df.data
            [df.column_index[ttn__dffux]] not in vvhmf__hkj)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ttn__dffux]})'
         for ttn__dffux in anuc__ifn)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, anuc__ifn, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    jql__djh = None
    if df.is_table_format:
        jjetq__nvh = types.Array(types.bool_, 1, 'C')
        jql__djh = DataFrameType(tuple([jjetq__nvh] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': jjetq__nvh}
        data_args = ('bodo.utils.table_utils.generate_mappable_table_func(' +
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df), ' +
            "'~bodo.libs.array_ops.array_op_isna', " + 'output_arr_typ, ' +
            'False)')
    else:
        data_args = ', '.join(
            f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})) == False'
             for i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


def overload_dataframe_head(df, n=5):
    if df.is_table_format:
        data_args = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[:n]')
    else:
        data_args = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:n]'
             for i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:n]'
    return _gen_init_df(header, df.columns, data_args, index)


@lower_builtin('df.head', DataFrameType, types.Integer)
@lower_builtin('df.head', DataFrameType, types.Omitted)
def dataframe_head_lower(context, builder, sig, args):
    impl = overload_dataframe_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'tail', inline='always', no_unliteral=True)
def overload_dataframe_tail(df, n=5):
    check_runtime_cols_unsupported(df, 'DataFrame.tail()')
    if not is_overload_int(n):
        raise BodoError("Dataframe.tail(): 'n' must be an Integer")
    if df.is_table_format:
        data_args = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)[m:]')
    else:
        data_args = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[m:]'
             for i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    header += '  m = bodo.hiframes.series_impl.tail_slice(len(df), n)\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[m:]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'first', inline='always', no_unliteral=True)
def overload_dataframe_first(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.first()')
    gxfo__xqei = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in gxfo__xqei:
        raise BodoError(
            "DataFrame.first(): 'offset' must be an string or DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.first()')
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:valid_entries]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:valid_entries]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    start_date = df_index[0]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, start_date, False)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'last', inline='always', no_unliteral=True)
def overload_dataframe_last(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.last()')
    gxfo__xqei = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in gxfo__xqei:
        raise BodoError(
            "DataFrame.last(): 'offset' must be an string or DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.last()')
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[len(df)-valid_entries:]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[len(df)-valid_entries:]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    final_date = df_index[-1]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, final_date, True)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'to_string', no_unliteral=True)
def to_string_overload(df, buf=None, columns=None, col_space=None, header=
    True, index=True, na_rep='NaN', formatters=None, float_format=None,
    sparsify=None, index_names=True, justify=None, max_rows=None, min_rows=
    None, max_cols=None, show_dimensions=False, decimal='.', line_width=
    None, max_colwidth=None, encoding=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_string()')

    def impl(df, buf=None, columns=None, col_space=None, header=True, index
        =True, na_rep='NaN', formatters=None, float_format=None, sparsify=
        None, index_names=True, justify=None, max_rows=None, min_rows=None,
        max_cols=None, show_dimensions=False, decimal='.', line_width=None,
        max_colwidth=None, encoding=None):
        with numba.objmode(res='string'):
            res = df.to_string(buf=buf, columns=columns, col_space=
                col_space, header=header, index=index, na_rep=na_rep,
                formatters=formatters, float_format=float_format, sparsify=
                sparsify, index_names=index_names, justify=justify,
                max_rows=max_rows, min_rows=min_rows, max_cols=max_cols,
                show_dimensions=show_dimensions, decimal=decimal,
                line_width=line_width, max_colwidth=max_colwidth, encoding=
                encoding)
        return res
    return impl


@overload_method(DataFrameType, 'isin', inline='always', no_unliteral=True)
def overload_dataframe_isin(df, values):
    check_runtime_cols_unsupported(df, 'DataFrame.isin()')
    from bodo.utils.typing import is_iterable_type
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.isin()')
    rnem__hlqb = 'def impl(df, values):\n'
    doyt__drgon = {}
    yzi__zmfd = False
    if isinstance(values, DataFrameType):
        yzi__zmfd = True
        for i, ttn__dffux in enumerate(df.columns):
            if ttn__dffux in values.column_index:
                nbdx__ugol = 'val{}'.format(i)
                rnem__hlqb += f"""  {nbdx__ugol} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[ttn__dffux]})
"""
                doyt__drgon[ttn__dffux] = nbdx__ugol
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        doyt__drgon = {ttn__dffux: 'values' for ttn__dffux in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        nbdx__ugol = 'data{}'.format(i)
        rnem__hlqb += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(nbdx__ugol, i))
        data.append(nbdx__ugol)
    lup__mhv = ['out{}'.format(i) for i in range(len(df.columns))]
    aafsz__hwng = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    utcp__oxqdl = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    nokpq__usra = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, ymc__bpneo) in enumerate(zip(df.columns, data)):
        if cname in doyt__drgon:
            prp__tkjii = doyt__drgon[cname]
            if yzi__zmfd:
                rnem__hlqb += aafsz__hwng.format(ymc__bpneo, prp__tkjii,
                    lup__mhv[i])
            else:
                rnem__hlqb += utcp__oxqdl.format(ymc__bpneo, prp__tkjii,
                    lup__mhv[i])
        else:
            rnem__hlqb += nokpq__usra.format(lup__mhv[i])
    return _gen_init_df(rnem__hlqb, df.columns, ','.join(lup__mhv))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    yvuos__faue = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(yvuos__faue))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    wlly__esofn = [ttn__dffux for ttn__dffux, sev__wyx in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(sev__wyx.dtype)]
    assert len(wlly__esofn) != 0
    kydg__getpp = ''
    if not any(sev__wyx == types.float64 for sev__wyx in df.data):
        kydg__getpp = '.astype(np.float64)'
    ysrz__klg = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[ttn__dffux], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[ttn__dffux]], IntegerArrayType) or
        df.data[df.column_index[ttn__dffux]] == boolean_array else '') for
        ttn__dffux in wlly__esofn)
    vzdi__lqwx = 'np.stack(({},), 1){}'.format(ysrz__klg, kydg__getpp)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(
        wlly__esofn)))
    index = f'{generate_col_to_index_func_text(wlly__esofn)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(vzdi__lqwx)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, wlly__esofn, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    wqp__dsfuk = dict(ddof=ddof)
    pncms__hkyvs = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    niwby__uwu = '1' if is_overload_none(min_periods) else 'min_periods'
    wlly__esofn = [ttn__dffux for ttn__dffux, sev__wyx in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(sev__wyx.dtype)]
    if len(wlly__esofn) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    kydg__getpp = ''
    if not any(sev__wyx == types.float64 for sev__wyx in df.data):
        kydg__getpp = '.astype(np.float64)'
    ysrz__klg = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[ttn__dffux], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[ttn__dffux]], IntegerArrayType) or
        df.data[df.column_index[ttn__dffux]] == boolean_array else '') for
        ttn__dffux in wlly__esofn)
    vzdi__lqwx = 'np.stack(({},), 1){}'.format(ysrz__klg, kydg__getpp)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(
        wlly__esofn)))
    index = f'pd.Index({wlly__esofn})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(vzdi__lqwx)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        niwby__uwu)
    return _gen_init_df(header, wlly__esofn, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    wqp__dsfuk = dict(axis=axis, level=level, numeric_only=numeric_only)
    pncms__hkyvs = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    rnem__hlqb = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    rnem__hlqb += '  data = np.array([{}])\n'.format(data_args)
    rcdtg__pqlrg = (bodo.hiframes.dataframe_impl.
        generate_col_to_index_func_text(df.columns))
    rnem__hlqb += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {rcdtg__pqlrg})\n'
        )
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo, 'np': np}, qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    wqp__dsfuk = dict(axis=axis)
    pncms__hkyvs = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    rnem__hlqb = 'def impl(df, axis=0, dropna=True):\n'
    rnem__hlqb += '  data = np.asarray(({},))\n'.format(data_args)
    rcdtg__pqlrg = (bodo.hiframes.dataframe_impl.
        generate_col_to_index_func_text(df.columns))
    rnem__hlqb += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {rcdtg__pqlrg})\n'
        )
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo, 'np': np}, qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    wqp__dsfuk = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    pncms__hkyvs = dict(skipna=None, level=None, numeric_only=None, min_count=0
        )
    check_unsupported_args('DataFrame.prod', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    wqp__dsfuk = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    pncms__hkyvs = dict(skipna=None, level=None, numeric_only=None, min_count=0
        )
    check_unsupported_args('DataFrame.sum', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    wqp__dsfuk = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    pncms__hkyvs = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    wqp__dsfuk = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    pncms__hkyvs = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    wqp__dsfuk = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    pncms__hkyvs = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    wqp__dsfuk = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    pncms__hkyvs = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    wqp__dsfuk = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    pncms__hkyvs = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    wqp__dsfuk = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    pncms__hkyvs = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    wqp__dsfuk = dict(numeric_only=numeric_only, interpolation=interpolation)
    pncms__hkyvs = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    wqp__dsfuk = dict(axis=axis, skipna=skipna)
    pncms__hkyvs = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for mjxn__lrv in df.data:
        if not (bodo.utils.utils.is_np_array_typ(mjxn__lrv) and (mjxn__lrv.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            mjxn__lrv.dtype, (types.Number, types.Boolean))) or isinstance(
            mjxn__lrv, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            mjxn__lrv in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {mjxn__lrv} not supported.'
                )
        if isinstance(mjxn__lrv, bodo.CategoricalArrayType
            ) and not mjxn__lrv.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    wqp__dsfuk = dict(axis=axis, skipna=skipna)
    pncms__hkyvs = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for mjxn__lrv in df.data:
        if not (bodo.utils.utils.is_np_array_typ(mjxn__lrv) and (mjxn__lrv.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            mjxn__lrv.dtype, (types.Number, types.Boolean))) or isinstance(
            mjxn__lrv, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            mjxn__lrv in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {mjxn__lrv} not supported.'
                )
        if isinstance(mjxn__lrv, bodo.CategoricalArrayType
            ) and not mjxn__lrv.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmin(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmin', axis=axis)


@overload_method(DataFrameType, 'infer_objects', inline='always')
def overload_dataframe_infer_objects(df):
    check_runtime_cols_unsupported(df, 'DataFrame.infer_objects()')
    return lambda df: df.copy()


def _gen_reduce_impl(df, func_name, args=None, axis=None):
    args = '' if is_overload_none(args) else args
    if is_overload_none(axis):
        axis = 0
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
    else:
        raise_bodo_error(
            f'DataFrame.{func_name}: axis must be a constant Integer')
    assert axis in (0, 1), f'invalid axis argument for DataFrame.{func_name}'
    if func_name in ('idxmax', 'idxmin'):
        out_colnames = df.columns
    else:
        wlly__esofn = tuple(ttn__dffux for ttn__dffux, sev__wyx in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (sev__wyx.dtype))
        out_colnames = wlly__esofn
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            mqjak__gpxsf = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[ttn__dffux]].dtype) for ttn__dffux in out_colnames
                ]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(mqjak__gpxsf, []))
    except NotImplementedError as tou__ymcu:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    ueptm__yxct = ''
    if func_name in ('sum', 'prod'):
        ueptm__yxct = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    rnem__hlqb = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, ueptm__yxct))
    if func_name == 'quantile':
        rnem__hlqb = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        rnem__hlqb = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        rnem__hlqb += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        rnem__hlqb += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    swjy__cqeqx = ''
    if func_name in ('min', 'max'):
        swjy__cqeqx = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        swjy__cqeqx = ', dtype=np.float32'
    iqsh__nkrg = f'bodo.libs.array_ops.array_op_{func_name}'
    jkok__dgsu = ''
    if func_name in ['sum', 'prod']:
        jkok__dgsu = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        jkok__dgsu = 'index'
    elif func_name == 'quantile':
        jkok__dgsu = 'q'
    elif func_name in ['std', 'var']:
        jkok__dgsu = 'True, ddof'
    elif func_name == 'median':
        jkok__dgsu = 'True'
    data_args = ', '.join(
        f'{iqsh__nkrg}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[ttn__dffux]}), {jkok__dgsu})'
         for ttn__dffux in out_colnames)
    rnem__hlqb = ''
    if func_name in ('idxmax', 'idxmin'):
        rnem__hlqb += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        rnem__hlqb += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        rnem__hlqb += '  data = np.asarray(({},){})\n'.format(data_args,
            swjy__cqeqx)
    rnem__hlqb += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return rnem__hlqb


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    oil__snr = [df_type.column_index[ttn__dffux] for ttn__dffux in out_colnames
        ]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in oil__snr)
    zjno__ygfe = '\n        '.join(f'row[{i}] = arr_{oil__snr[i]}[i]' for i in
        range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    ykto__alkki = f'len(arr_{oil__snr[0]})'
    amt__zaoxm = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in amt__zaoxm:
        flxq__tnlhw = amt__zaoxm[func_name]
        ayv__mdx = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        rnem__hlqb = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {ykto__alkki}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{ayv__mdx})
    for i in numba.parfors.parfor.internal_prange(n):
        {zjno__ygfe}
        A[i] = {flxq__tnlhw}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return rnem__hlqb
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    wqp__dsfuk = dict(fill_method=fill_method, limit=limit, freq=freq)
    pncms__hkyvs = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.pct_change()')
    data_args = ', '.join(
        f'bodo.hiframes.rolling.pct_change(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = (
        "def impl(df, periods=1, fill_method='pad', limit=None, freq=None):\n")
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumprod', inline='always', no_unliteral=True)
def overload_dataframe_cumprod(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumprod()')
    wqp__dsfuk = dict(axis=axis, skipna=skipna)
    pncms__hkyvs = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.cumprod()')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumprod()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumsum', inline='always', no_unliteral=True)
def overload_dataframe_cumsum(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumsum()')
    wqp__dsfuk = dict(skipna=skipna)
    pncms__hkyvs = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.cumsum()')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumsum()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


def _is_describe_type(data):
    return isinstance(data, IntegerArrayType) or isinstance(data, types.Array
        ) and isinstance(data.dtype, types.Number
        ) or data.dtype == bodo.datetime64ns


@overload_method(DataFrameType, 'describe', inline='always', no_unliteral=True)
def overload_dataframe_describe(df, percentiles=None, include=None, exclude
    =None, datetime_is_numeric=True):
    check_runtime_cols_unsupported(df, 'DataFrame.describe()')
    wqp__dsfuk = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    pncms__hkyvs = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    wlly__esofn = [ttn__dffux for ttn__dffux, sev__wyx in zip(df.columns,
        df.data) if _is_describe_type(sev__wyx)]
    if len(wlly__esofn) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    ortw__dxsf = sum(df.data[df.column_index[ttn__dffux]].dtype == bodo.
        datetime64ns for ttn__dffux in wlly__esofn)

    def _get_describe(col_ind):
        jpfzw__okekl = df.data[col_ind].dtype == bodo.datetime64ns
        if ortw__dxsf and ortw__dxsf != len(wlly__esofn):
            if jpfzw__okekl:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for ttn__dffux in wlly__esofn:
        col_ind = df.column_index[ttn__dffux]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[ttn__dffux]) for
        ttn__dffux in wlly__esofn)
    kejgw__bgs = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if ortw__dxsf == len(wlly__esofn):
        kejgw__bgs = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif ortw__dxsf:
        kejgw__bgs = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({kejgw__bgs})'
    return _gen_init_df(header, wlly__esofn, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    wqp__dsfuk = dict(axis=axis, convert=convert, is_copy=is_copy)
    pncms__hkyvs = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[indices_t]'
        .format(i) for i in range(len(df.columns)))
    header = 'def impl(df, indices, axis=0, convert=None, is_copy=True):\n'
    header += (
        '  indices_t = bodo.utils.conversion.coerce_to_ndarray(indices)\n')
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[indices_t]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'shift', inline='always', no_unliteral=True)
def overload_dataframe_shift(df, periods=1, freq=None, axis=0, fill_value=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.shift()')
    wqp__dsfuk = dict(freq=freq, axis=axis, fill_value=fill_value)
    pncms__hkyvs = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for vadyi__xek in df.data:
        if not is_supported_shift_array_type(vadyi__xek):
            raise BodoError(
                f'Dataframe.shift() column input type {vadyi__xek.dtype} not supported yet.'
                )
    if not is_overload_int(periods):
        raise BodoError(
            "DataFrame.shift(): 'periods' input must be an integer.")
    data_args = ', '.join(
        f'bodo.hiframes.rolling.shift(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = 'def impl(df, periods=1, freq=None, axis=0, fill_value=None):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'diff', inline='always', no_unliteral=True)
def overload_dataframe_diff(df, periods=1, axis=0):
    check_runtime_cols_unsupported(df, 'DataFrame.diff()')
    wqp__dsfuk = dict(axis=axis)
    pncms__hkyvs = dict(axis=0)
    check_unsupported_args('DataFrame.diff', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for vadyi__xek in df.data:
        if not (isinstance(vadyi__xek, types.Array) and (isinstance(
            vadyi__xek.dtype, types.Number) or vadyi__xek.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {vadyi__xek.dtype} not supported.'
                )
    if not is_overload_int(periods):
        raise BodoError("DataFrame.diff(): 'periods' input must be an integer."
            )
    header = 'def impl(df, periods=1, axis= 0):\n'
    for i in range(len(df.columns)):
        header += (
            f'  data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    data_args = ', '.join(
        f'bodo.hiframes.series_impl.dt64_arr_sub(data_{i}, bodo.hiframes.rolling.shift(data_{i}, periods, False))'
         if df.data[i] == types.Array(bodo.datetime64ns, 1, 'C') else
        f'data_{i} - bodo.hiframes.rolling.shift(data_{i}, periods, False)' for
        i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'explode', inline='always', no_unliteral=True)
def overload_dataframe_explode(df, column, ignore_index=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.explode()')
    qgc__xrhq = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(qgc__xrhq)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        hrie__pkaz = get_overload_const_list(column)
    else:
        hrie__pkaz = [get_literal_value(column)]
    cqt__mmd = [df.column_index[ttn__dffux] for ttn__dffux in hrie__pkaz]
    for i in cqt__mmd:
        if not isinstance(df.data[i], ArrayItemArrayType) and df.data[i
            ].dtype != string_array_split_view_type:
            raise BodoError(
                f'DataFrame.explode(): columns must have array-like entries')
    n = len(df.columns)
    header = 'def impl(df, column, ignore_index=False):\n'
    header += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    header += '  index_arr = bodo.utils.conversion.index_to_array(index)\n'
    for i in range(n):
        header += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    header += (
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{cqt__mmd[0]})\n'
        )
    for i in range(n):
        if i in cqt__mmd:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.explode_no_index(data{i}, counts)\n'
                )
        else:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.repeat_kernel(data{i}, counts)\n'
                )
    header += (
        '  new_index = bodo.libs.array_kernels.repeat_kernel(index_arr, counts)\n'
        )
    data_args = ', '.join(f'out_data{i}' for i in range(n))
    index = 'bodo.utils.conversion.convert_to_index(new_index)'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'set_index', inline='always', no_unliteral=True
    )
def overload_dataframe_set_index(df, keys, drop=True, append=False, inplace
    =False, verify_integrity=False):
    check_runtime_cols_unsupported(df, 'DataFrame.set_index()')
    wso__vfi = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    fqwi__okvxq = {'inplace': False, 'append': False, 'verify_integrity': False
        }
    check_unsupported_args('DataFrame.set_index', wso__vfi, fqwi__okvxq,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_str(keys):
        raise_bodo_error(
            "DataFrame.set_index(): 'keys' must be a constant string")
    col_name = get_overload_const_str(keys)
    col_ind = df.columns.index(col_name)
    header = """def impl(df, keys, drop=True, append=False, inplace=False, verify_integrity=False):
"""
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'.format(
        i) for i in range(len(df.columns)) if i != col_ind)
    columns = tuple(ttn__dffux for ttn__dffux in df.columns if ttn__dffux !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    wso__vfi = {'inplace': inplace}
    fqwi__okvxq = {'inplace': False}
    check_unsupported_args('query', wso__vfi, fqwi__okvxq, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        wef__eqt = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[wef__eqt]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    wso__vfi = {'subset': subset, 'keep': keep}
    fqwi__okvxq = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', wso__vfi, fqwi__okvxq,
        package_name='pandas', module_name='DataFrame')
    yvuos__faue = len(df.columns)
    rnem__hlqb = "def impl(df, subset=None, keep='first'):\n"
    for i in range(yvuos__faue):
        rnem__hlqb += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    etyag__udzj = ', '.join(f'data_{i}' for i in range(yvuos__faue))
    etyag__udzj += ',' if yvuos__faue == 1 else ''
    rnem__hlqb += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({etyag__udzj}))\n'
        )
    rnem__hlqb += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    rnem__hlqb += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo}, qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    wso__vfi = {'keep': keep, 'inplace': inplace, 'ignore_index': ignore_index}
    fqwi__okvxq = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    tqpm__hryt = []
    if is_overload_constant_list(subset):
        tqpm__hryt = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        tqpm__hryt = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        tqpm__hryt = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    pbvqs__fnnoo = []
    for col_name in tqpm__hryt:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        pbvqs__fnnoo.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', wso__vfi,
        fqwi__okvxq, package_name='pandas', module_name='DataFrame')
    uzedi__znp = []
    if pbvqs__fnnoo:
        for zsiid__ikfkq in pbvqs__fnnoo:
            if isinstance(df.data[zsiid__ikfkq], bodo.MapArrayType):
                uzedi__znp.append(df.columns[zsiid__ikfkq])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                uzedi__znp.append(col_name)
    if uzedi__znp:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {uzedi__znp} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    yvuos__faue = len(df.columns)
    qww__prdvg = ['data_{}'.format(i) for i in pbvqs__fnnoo]
    cpxfm__avzfz = ['data_{}'.format(i) for i in range(yvuos__faue) if i not in
        pbvqs__fnnoo]
    if qww__prdvg:
        cbzip__vlt = len(qww__prdvg)
    else:
        cbzip__vlt = yvuos__faue
    rmmoj__vabxz = ', '.join(qww__prdvg + cpxfm__avzfz)
    data_args = ', '.join('data_{}'.format(i) for i in range(yvuos__faue))
    rnem__hlqb = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(yvuos__faue):
        rnem__hlqb += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    rnem__hlqb += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(rmmoj__vabxz, index, cbzip__vlt))
    rnem__hlqb += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(rnem__hlqb, df.columns, data_args, 'index')


def create_dataframe_mask_where_overload(func_name):

    def overload_dataframe_mask_where(df, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
            f'DataFrame.{func_name}()')
        _validate_arguments_mask_where(f'DataFrame.{func_name}', df, cond,
            other, inplace, axis, level, errors, try_cast)
        header = """def impl(df, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise', try_cast=False):
"""
        if func_name == 'mask':
            header += '  cond = ~cond\n'
        gen_all_false = [False]
        if cond.ndim == 1:
            cond_str = lambda i, _: 'cond'
        elif cond.ndim == 2:
            if isinstance(cond, DataFrameType):

                def cond_str(i, gen_all_false):
                    if df.columns[i] in cond.column_index:
                        return (
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(cond, {cond.column_index[df.columns[i]]})'
                            )
                    else:
                        gen_all_false[0] = True
                        return 'all_false'
            elif isinstance(cond, types.Array):
                cond_str = lambda i, _: f'cond[:,{i}]'
        if not hasattr(other, 'ndim') or other.ndim == 1:
            mxe__rud = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                mxe__rud = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                mxe__rud = lambda i: f'other[:,{i}]'
        yvuos__faue = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {mxe__rud(i)})'
             for i in range(yvuos__faue))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        lxt__liwpg = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(lxt__liwpg
            )


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    wqp__dsfuk = dict(inplace=inplace, level=level, errors=errors, try_cast
        =try_cast)
    pncms__hkyvs = dict(inplace=False, level=None, errors='raise', try_cast
        =False)
    check_unsupported_args(f'{func_name}', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        (cond.ndim == 1 or cond.ndim == 2) and cond.dtype == types.bool_
        ) and not (isinstance(cond, DataFrameType) and cond.ndim == 2 and
        all(cond.data[i].dtype == types.bool_ for i in range(len(df.columns)))
        ):
        raise BodoError(
            f"{func_name}(): 'cond' argument must be a DataFrame, Series, 1- or 2-dimensional array of booleans"
            )
    yvuos__faue = len(df.columns)
    if hasattr(other, 'ndim') and (other.ndim != 1 or other.ndim != 2):
        if other.ndim == 2:
            if not isinstance(other, (DataFrameType, types.Array)):
                raise BodoError(
                    f"{func_name}(): 'other', if 2-dimensional, must be a DataFrame or array."
                    )
        elif other.ndim != 1:
            raise BodoError(
                f"{func_name}(): 'other' must be either 1 or 2-dimensional")
    if isinstance(other, DataFrameType):
        for i in range(yvuos__faue):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(yvuos__faue):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(yvuos__faue):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    hkh__lgsd = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    rnem__hlqb = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    qbsaf__jre = {}
    lzy__lcz = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': hkh__lgsd}
    lzy__lcz.update(extra_globals)
    exec(rnem__hlqb, lzy__lcz, qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        pqk__qedl = pd.Index(lhs.columns)
        fpf__fwql = pd.Index(rhs.columns)
        kfke__vrx, boj__nson, jqmse__jkpvp = pqk__qedl.join(fpf__fwql, how=
            'left' if is_inplace else 'outer', level=None, return_indexers=True
            )
        return tuple(kfke__vrx), boj__nson, jqmse__jkpvp
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        tenqg__qppi = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        yryfy__pqlk = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, tenqg__qppi)
        check_runtime_cols_unsupported(rhs, tenqg__qppi)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                kfke__vrx, boj__nson, jqmse__jkpvp = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {zdt__sagz}) {tenqg__qppi}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {vgdoc__plg})'
                     if zdt__sagz != -1 and vgdoc__plg != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for zdt__sagz, vgdoc__plg in zip(boj__nson, jqmse__jkpvp))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, kfke__vrx, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            zsaw__wlqqf = []
            gvd__qzifc = []
            if op in yryfy__pqlk:
                for i, hnk__rtt in enumerate(lhs.data):
                    if is_common_scalar_dtype([hnk__rtt.dtype, rhs]):
                        zsaw__wlqqf.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {tenqg__qppi} rhs'
                            )
                    else:
                        wblx__wrfan = f'arr{i}'
                        gvd__qzifc.append(wblx__wrfan)
                        zsaw__wlqqf.append(wblx__wrfan)
                data_args = ', '.join(zsaw__wlqqf)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {tenqg__qppi} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(gvd__qzifc) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {wblx__wrfan} = np.empty(n, dtype=np.bool_)\n' for
                    wblx__wrfan in gvd__qzifc)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(wblx__wrfan, 
                    op == operator.ne) for wblx__wrfan in gvd__qzifc)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            zsaw__wlqqf = []
            gvd__qzifc = []
            if op in yryfy__pqlk:
                for i, hnk__rtt in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, hnk__rtt.dtype]):
                        zsaw__wlqqf.append(
                            f'lhs {tenqg__qppi} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        wblx__wrfan = f'arr{i}'
                        gvd__qzifc.append(wblx__wrfan)
                        zsaw__wlqqf.append(wblx__wrfan)
                data_args = ', '.join(zsaw__wlqqf)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, tenqg__qppi) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(gvd__qzifc) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(wblx__wrfan) for wblx__wrfan in gvd__qzifc)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(wblx__wrfan, 
                    op == operator.ne) for wblx__wrfan in gvd__qzifc)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(rhs)'
            return _gen_init_df(header, rhs.columns, data_args, index)
    return overload_dataframe_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        lxt__liwpg = create_binary_op_overload(op)
        overload(op)(lxt__liwpg)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        tenqg__qppi = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, tenqg__qppi)
        check_runtime_cols_unsupported(right, tenqg__qppi)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                kfke__vrx, _, jqmse__jkpvp = _get_binop_columns(left, right,
                    True)
                rnem__hlqb = 'def impl(left, right):\n'
                for i, vgdoc__plg in enumerate(jqmse__jkpvp):
                    if vgdoc__plg == -1:
                        rnem__hlqb += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    rnem__hlqb += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    rnem__hlqb += f"""  df_arr{i} {tenqg__qppi} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {vgdoc__plg})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    kfke__vrx)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(rnem__hlqb, kfke__vrx, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            rnem__hlqb = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                rnem__hlqb += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                rnem__hlqb += '  df_arr{0} {1} right\n'.format(i, tenqg__qppi)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(rnem__hlqb, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        lxt__liwpg = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(lxt__liwpg)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            tenqg__qppi = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, tenqg__qppi)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, tenqg__qppi) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        lxt__liwpg = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(lxt__liwpg)


_install_unary_ops()


def overload_isna(obj):
    check_runtime_cols_unsupported(obj, 'pd.isna()')
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj):
        return lambda obj: obj.isna()
    if is_array_typ(obj):

        def impl(obj):
            numba.parfors.parfor.init_prange()
            n = len(obj)
            wwvlj__ozo = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                wwvlj__ozo[i] = bodo.libs.array_kernels.isna(obj, i)
            return wwvlj__ozo
        return impl


overload(pd.isna, inline='always')(overload_isna)
overload(pd.isnull, inline='always')(overload_isna)


@overload(pd.isna)
@overload(pd.isnull)
def overload_isna_scalar(obj):
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj) or is_array_typ(
        obj):
        return
    if isinstance(obj, (types.List, types.UniTuple)):

        def impl(obj):
            n = len(obj)
            wwvlj__ozo = np.empty(n, np.bool_)
            for i in range(n):
                wwvlj__ozo[i] = pd.isna(obj[i])
            return wwvlj__ozo
        return impl
    obj = types.unliteral(obj)
    if obj == bodo.string_type:
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Integer):
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Float):
        return lambda obj: np.isnan(obj)
    if isinstance(obj, (types.NPDatetime, types.NPTimedelta)):
        return lambda obj: np.isnat(obj)
    if obj == types.none:
        return lambda obj: unliteral_val(True)
    if isinstance(obj, bodo.hiframes.pd_timestamp_ext.PandasTimestampType):
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_dt64(obj.value))
    if obj == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(obj.value))
    if isinstance(obj, types.Optional):
        return lambda obj: obj is None
    return lambda obj: unliteral_val(False)


@overload(operator.setitem, no_unliteral=True)
def overload_setitem_arr_none(A, idx, val):
    if is_array_typ(A, False) and isinstance(idx, types.Integer
        ) and val == types.none:
        return lambda A, idx, val: bodo.libs.array_kernels.setna(A, idx)


def overload_notna(obj):
    check_runtime_cols_unsupported(obj, 'pd.notna()')
    if isinstance(obj, (DataFrameType, SeriesType)):
        return lambda obj: obj.notna()
    if isinstance(obj, (types.List, types.UniTuple)) or is_array_typ(obj,
        include_index_series=True):
        return lambda obj: ~pd.isna(obj)
    return lambda obj: not pd.isna(obj)


overload(pd.notna, inline='always', no_unliteral=True)(overload_notna)
overload(pd.notnull, inline='always', no_unliteral=True)(overload_notna)


def _get_pd_dtype_str(t):
    if t.dtype == types.NPDatetime('ns'):
        return "'datetime64[ns]'"
    return bodo.ir.csv_ext._get_pd_dtype_str(t)


@overload_method(DataFrameType, 'replace', inline='always', no_unliteral=True)
def overload_dataframe_replace(df, to_replace=None, value=None, inplace=
    False, limit=None, regex=False, method='pad'):
    check_runtime_cols_unsupported(df, 'DataFrame.replace()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.replace()')
    if is_overload_none(to_replace):
        raise BodoError('replace(): to_replace value of None is not supported')
    wso__vfi = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    fqwi__okvxq = {'inplace': False, 'limit': None, 'regex': False,
        'method': 'pad'}
    check_unsupported_args('replace', wso__vfi, fqwi__okvxq, package_name=
        'pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    hhjq__uzht = str(expr_node)
    return hhjq__uzht.startswith('left.') or hhjq__uzht.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    qysy__vhq = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (qysy__vhq,))
    ozli__rxca = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        dxzqa__wmvx = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        koh__gkgbw = {('NOT_NA', ozli__rxca(hnk__rtt)): hnk__rtt for
            hnk__rtt in null_set}
        wvk__xlhpz, _, _ = _parse_query_expr(dxzqa__wmvx, env, [], [], None,
            join_cleaned_cols=koh__gkgbw)
        gsm__igq = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            wjvtk__blhjg = pd.core.computation.ops.BinOp('&', wvk__xlhpz,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = gsm__igq
        return wjvtk__blhjg

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                izbyk__byx = set()
                mjtwp__rkb = set()
                ltte__exwsl = _insert_NA_cond_body(expr_node.lhs, izbyk__byx)
                hoe__nicf = _insert_NA_cond_body(expr_node.rhs, mjtwp__rkb)
                zoh__bzvmr = izbyk__byx.intersection(mjtwp__rkb)
                izbyk__byx.difference_update(zoh__bzvmr)
                mjtwp__rkb.difference_update(zoh__bzvmr)
                null_set.update(zoh__bzvmr)
                expr_node.lhs = append_null_checks(ltte__exwsl, izbyk__byx)
                expr_node.rhs = append_null_checks(hoe__nicf, mjtwp__rkb)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            mxr__avg = expr_node.name
            ymz__fbdqp, col_name = mxr__avg.split('.')
            if ymz__fbdqp == 'left':
                vdrw__ebq = left_columns
                data = left_data
            else:
                vdrw__ebq = right_columns
                data = right_data
            nho__bdrn = data[vdrw__ebq.index(col_name)]
            if bodo.utils.typing.is_nullable(nho__bdrn):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    kbjnv__pry = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        sxeac__nji = str(expr_node.lhs)
        lomw__bva = str(expr_node.rhs)
        if sxeac__nji.startswith('left.') and lomw__bva.startswith('left.'
            ) or sxeac__nji.startswith('right.') and lomw__bva.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [sxeac__nji.split('.')[1]]
        right_on = [lomw__bva.split('.')[1]]
        if sxeac__nji.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        cmmr__orkf, duge__tivrz, ruy__jcj = _extract_equal_conds(expr_node.lhs)
        jlgp__lnp, tte__tmhp, herw__bdw = _extract_equal_conds(expr_node.rhs)
        left_on = cmmr__orkf + jlgp__lnp
        right_on = duge__tivrz + tte__tmhp
        if ruy__jcj is None:
            return left_on, right_on, herw__bdw
        if herw__bdw is None:
            return left_on, right_on, ruy__jcj
        expr_node.lhs = ruy__jcj
        expr_node.rhs = herw__bdw
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    qysy__vhq = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (qysy__vhq,))
    ayjhe__cvlh = dict()
    ozli__rxca = pd.core.computation.parsing.clean_column_name
    for name, ypdmd__guq in (('left', left_columns), ('right', right_columns)):
        for hnk__rtt in ypdmd__guq:
            jgki__uqv = ozli__rxca(hnk__rtt)
            bxoj__pfvx = name, jgki__uqv
            if bxoj__pfvx in ayjhe__cvlh:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{hnk__rtt}' and '{ayjhe__cvlh[jgki__uqv]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            ayjhe__cvlh[bxoj__pfvx] = hnk__rtt
    ecsht__axed, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=ayjhe__cvlh)
    left_on, right_on, loprp__qpuw = _extract_equal_conds(ecsht__axed.terms)
    return left_on, right_on, _insert_NA_cond(loprp__qpuw, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    wqp__dsfuk = dict(sort=sort, copy=copy, validate=validate)
    pncms__hkyvs = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    aqkay__vbj = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    oztv__geos = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in aqkay__vbj and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, yxlc__ljho = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if yxlc__ljho is None:
                    oztv__geos = ''
                else:
                    oztv__geos = str(yxlc__ljho)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = aqkay__vbj
        right_keys = aqkay__vbj
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    if (not left_on or not right_on) and not is_overload_none(on):
        raise BodoError(
            f"DataFrame.merge(): Merge condition '{get_overload_const_str(on)}' requires a cross join to implement, but cross join is not supported."
            )
    if not is_overload_bool(indicator):
        raise_bodo_error(
            'DataFrame.merge(): indicator must be a constant boolean')
    indicator_val = get_overload_const_bool(indicator)
    if not is_overload_bool(_bodo_na_equal):
        raise_bodo_error(
            'DataFrame.merge(): bodo extension _bodo_na_equal must be a constant boolean'
            )
    jbs__tboi = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        fnpjb__ranl = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        fnpjb__ranl = list(get_overload_const_list(suffixes))
    suffix_x = fnpjb__ranl[0]
    suffix_y = fnpjb__ranl[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    rnem__hlqb = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    rnem__hlqb += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    rnem__hlqb += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    rnem__hlqb += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, jbs__tboi, oztv__geos))
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo}, qbsaf__jre)
    _impl = qbsaf__jre['_impl']
    return _impl


def common_validate_merge_merge_asof_spec(name_func, left, right, on,
    left_on, right_on, left_index, right_index, suffixes):
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError(name_func + '() requires dataframe inputs')
    valid_dataframe_column_types = (ArrayItemArrayType, MapArrayType,
        StructArrayType, CategoricalArrayType, types.Array,
        IntegerArrayType, DecimalArrayType, IntervalArrayType, bodo.
        DatetimeArrayType)
    owwg__lisfq = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    hrzhh__wiwpo = {get_overload_const_str(pfzyp__khlo) for pfzyp__khlo in
        (left_on, right_on, on) if is_overload_constant_str(pfzyp__khlo)}
    for df in (left, right):
        for i, hnk__rtt in enumerate(df.data):
            if not isinstance(hnk__rtt, valid_dataframe_column_types
                ) and hnk__rtt not in owwg__lisfq:
                raise BodoError(
                    f'{name_func}(): use of column with {type(hnk__rtt)} in merge unsupported'
                    )
            if df.columns[i] in hrzhh__wiwpo and isinstance(hnk__rtt,
                MapArrayType):
                raise BodoError(
                    f'{name_func}(): merge on MapArrayType unsupported')
    ensure_constant_arg(name_func, 'left_index', left_index, bool)
    ensure_constant_arg(name_func, 'right_index', right_index, bool)
    if not is_overload_constant_tuple(suffixes
        ) and not is_overload_constant_list(suffixes):
        raise_bodo_error(name_func +
            "(): suffixes parameters should be ['_left', '_right']")
    if is_overload_constant_tuple(suffixes):
        fnpjb__ranl = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        fnpjb__ranl = list(get_overload_const_list(suffixes))
    if len(fnpjb__ranl) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    aqkay__vbj = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        rklf__ishwp = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            rklf__ishwp = on_str not in aqkay__vbj and ('left.' in on_str or
                'right.' in on_str)
        if len(aqkay__vbj) == 0 and not rklf__ishwp:
            raise_bodo_error(name_func +
                '(): No common columns to perform merge on. Merge options: left_on={lon}, right_on={ron}, left_index={lidx}, right_index={ridx}'
                .format(lon=is_overload_true(left_on), ron=is_overload_true
                (right_on), lidx=is_overload_true(left_index), ridx=
                is_overload_true(right_index)))
        if not is_overload_none(left_on) or not is_overload_none(right_on):
            raise BodoError(name_func +
                '(): Can only pass argument "on" OR "left_on" and "right_on", not a combination of both.'
                )
    if (is_overload_true(left_index) or not is_overload_none(left_on)
        ) and is_overload_none(right_on) and not is_overload_true(right_index):
        raise BodoError(name_func +
            '(): Must pass right_on or right_index=True')
    if (is_overload_true(right_index) or not is_overload_none(right_on)
        ) and is_overload_none(left_on) and not is_overload_true(left_index):
        raise BodoError(name_func + '(): Must pass left_on or left_index=True')


def validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
    right_index, sort, suffixes, copy, indicator, validate):
    common_validate_merge_merge_asof_spec('merge', left, right, on, left_on,
        right_on, left_index, right_index, suffixes)
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))


def validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
    right_index, by, left_by, right_by, suffixes, tolerance,
    allow_exact_matches, direction):
    common_validate_merge_merge_asof_spec('merge_asof', left, right, on,
        left_on, right_on, left_index, right_index, suffixes)
    if not is_overload_true(allow_exact_matches):
        raise BodoError(
            'merge_asof(): allow_exact_matches parameter only supports default value True'
            )
    if not is_overload_none(tolerance):
        raise BodoError(
            'merge_asof(): tolerance parameter only supports default value None'
            )
    if not is_overload_none(by):
        raise BodoError(
            'merge_asof(): by parameter only supports default value None')
    if not is_overload_none(left_by):
        raise BodoError(
            'merge_asof(): left_by parameter only supports default value None')
    if not is_overload_none(right_by):
        raise BodoError(
            'merge_asof(): right_by parameter only supports default value None'
            )
    if not is_overload_constant_str(direction):
        raise BodoError(
            'merge_asof(): direction parameter should be of type str')
    else:
        direction = get_overload_const_str(direction)
        if direction != 'backward':
            raise BodoError(
                "merge_asof(): direction parameter only supports default value 'backward'"
                )


def validate_merge_asof_keys_length(left_on, right_on, left_index,
    right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if not is_overload_none(left_on) and is_overload_true(right_index):
        raise BodoError(
            'merge(): right_index = True and specifying left_on is not suppported yet.'
            )
    if not is_overload_none(right_on) and is_overload_true(left_index):
        raise BodoError(
            'merge(): left_index = True and specifying right_on is not suppported yet.'
            )


def validate_keys_length(left_index, right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if is_overload_true(right_index):
        if len(left_keys) != 1:
            raise BodoError(
                'merge(): len(left_on) must equal the number of levels in the index of "right", which is 1'
                )
    if is_overload_true(left_index):
        if len(right_keys) != 1:
            raise BodoError(
                'merge(): len(right_on) must equal the number of levels in the index of "left", which is 1'
                )


def validate_keys_dtypes(left, right, left_index, right_index, left_keys,
    right_keys):
    bnxqx__ecz = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            oamv__gzwk = left.index
            wtv__mrrv = isinstance(oamv__gzwk, StringIndexType)
            bious__sgoy = right.index
            qtzj__zjog = isinstance(bious__sgoy, StringIndexType)
        elif is_overload_true(left_index):
            oamv__gzwk = left.index
            wtv__mrrv = isinstance(oamv__gzwk, StringIndexType)
            bious__sgoy = right.data[right.columns.index(right_keys[0])]
            qtzj__zjog = bious__sgoy.dtype == string_type
        elif is_overload_true(right_index):
            oamv__gzwk = left.data[left.columns.index(left_keys[0])]
            wtv__mrrv = oamv__gzwk.dtype == string_type
            bious__sgoy = right.index
            qtzj__zjog = isinstance(bious__sgoy, StringIndexType)
        if wtv__mrrv and qtzj__zjog:
            return
        oamv__gzwk = oamv__gzwk.dtype
        bious__sgoy = bious__sgoy.dtype
        try:
            zqcej__nnjap = bnxqx__ecz.resolve_function_type(operator.eq, (
                oamv__gzwk, bious__sgoy), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=oamv__gzwk, rk_dtype=bious__sgoy))
    else:
        for jaaaa__wlgnh, tcb__bnw in zip(left_keys, right_keys):
            oamv__gzwk = left.data[left.columns.index(jaaaa__wlgnh)].dtype
            iwrrh__mqbkz = left.data[left.columns.index(jaaaa__wlgnh)]
            bious__sgoy = right.data[right.columns.index(tcb__bnw)].dtype
            ubcu__yrus = right.data[right.columns.index(tcb__bnw)]
            if iwrrh__mqbkz == ubcu__yrus:
                continue
            nit__ptid = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=jaaaa__wlgnh, lk_dtype=oamv__gzwk, rk=tcb__bnw,
                rk_dtype=bious__sgoy))
            hfji__vtu = oamv__gzwk == string_type
            yjkb__rlvdc = bious__sgoy == string_type
            if hfji__vtu ^ yjkb__rlvdc:
                raise_bodo_error(nit__ptid)
            try:
                zqcej__nnjap = bnxqx__ecz.resolve_function_type(operator.eq,
                    (oamv__gzwk, bious__sgoy), {})
            except:
                raise_bodo_error(nit__ptid)


def validate_keys(keys, df):
    bjqqf__arfpc = set(keys).difference(set(df.columns))
    if len(bjqqf__arfpc) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in bjqqf__arfpc:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {bjqqf__arfpc} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    wqp__dsfuk = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    pncms__hkyvs = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort)
    how = get_overload_const_str(how)
    if not is_overload_none(on):
        left_keys = get_overload_const_list(on)
    else:
        left_keys = ['$_bodo_index_']
    right_keys = ['$_bodo_index_']
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    rnem__hlqb = "def _impl(left, other, on=None, how='left',\n"
    rnem__hlqb += "    lsuffix='', rsuffix='', sort=False):\n"
    rnem__hlqb += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo}, qbsaf__jre)
    _impl = qbsaf__jre['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        haern__gqwqd = get_overload_const_list(on)
        validate_keys(haern__gqwqd, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    aqkay__vbj = tuple(set(left.columns) & set(other.columns))
    if len(aqkay__vbj) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=aqkay__vbj))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    dtg__mnzou = set(left_keys) & set(right_keys)
    lbn__ubl = set(left_columns) & set(right_columns)
    endhh__krqd = lbn__ubl - dtg__mnzou
    wngw__tzcuc = set(left_columns) - lbn__ubl
    vlow__dtyaz = set(right_columns) - lbn__ubl
    nxd__vejy = {}

    def insertOutColumn(col_name):
        if col_name in nxd__vejy:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        nxd__vejy[col_name] = 0
    for fnqo__oti in dtg__mnzou:
        insertOutColumn(fnqo__oti)
    for fnqo__oti in endhh__krqd:
        cpju__teb = str(fnqo__oti) + suffix_x
        syce__cbt = str(fnqo__oti) + suffix_y
        insertOutColumn(cpju__teb)
        insertOutColumn(syce__cbt)
    for fnqo__oti in wngw__tzcuc:
        insertOutColumn(fnqo__oti)
    for fnqo__oti in vlow__dtyaz:
        insertOutColumn(fnqo__oti)
    if indicator_val:
        insertOutColumn('_merge')


@overload(pd.merge_asof, inline='always', no_unliteral=True)
def overload_dataframe_merge_asof(left, right, on=None, left_on=None,
    right_on=None, left_index=False, right_index=False, by=None, left_by=
    None, right_by=None, suffixes=('_x', '_y'), tolerance=None,
    allow_exact_matches=True, direction='backward'):
    raise BodoError('pandas.merge_asof() not support yet')
    validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
        right_index, by, left_by, right_by, suffixes, tolerance,
        allow_exact_matches, direction)
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError('merge_asof() requires dataframe inputs')
    aqkay__vbj = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = aqkay__vbj
        right_keys = aqkay__vbj
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    validate_merge_asof_keys_length(left_on, right_on, left_index,
        right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    if isinstance(suffixes, tuple):
        fnpjb__ranl = suffixes
    if is_overload_constant_list(suffixes):
        fnpjb__ranl = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        fnpjb__ranl = suffixes.value
    suffix_x = fnpjb__ranl[0]
    suffix_y = fnpjb__ranl[1]
    rnem__hlqb = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    rnem__hlqb += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    rnem__hlqb += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    rnem__hlqb += "    allow_exact_matches=True, direction='backward'):\n"
    rnem__hlqb += '  suffix_x = suffixes[0]\n'
    rnem__hlqb += '  suffix_y = suffixes[1]\n'
    rnem__hlqb += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo}, qbsaf__jre)
    _impl = qbsaf__jre['_impl']
    return _impl


@overload_method(DataFrameType, 'groupby', inline='always', no_unliteral=True)
def overload_dataframe_groupby(df, by=None, axis=0, level=None, as_index=
    True, sort=False, group_keys=True, squeeze=False, observed=True, dropna
    =True):
    check_runtime_cols_unsupported(df, 'DataFrame.groupby()')
    validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
        squeeze, observed, dropna)

    def _impl(df, by=None, axis=0, level=None, as_index=True, sort=False,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        return bodo.hiframes.pd_groupby_ext.init_groupby(df, by, as_index,
            dropna)
    return _impl


def validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
    squeeze, observed, dropna):
    if is_overload_none(by):
        raise BodoError("groupby(): 'by' must be supplied.")
    if not is_overload_zero(axis):
        raise BodoError(
            "groupby(): 'axis' parameter only supports integer value 0.")
    if not is_overload_none(level):
        raise BodoError(
            "groupby(): 'level' is not supported since MultiIndex is not supported."
            )
    if not is_literal_type(by) and not is_overload_constant_list(by):
        raise_bodo_error(
            f"groupby(): 'by' parameter only supports a constant column label or column labels, not {by}."
            )
    if len(set(get_overload_const_list(by)).difference(set(df.columns))) > 0:
        raise_bodo_error(
            "groupby(): invalid key {} for 'by' (not available in columns {})."
            .format(get_overload_const_list(by), df.columns))
    if not is_overload_constant_bool(as_index):
        raise_bodo_error(
            "groupby(): 'as_index' parameter must be a constant bool, not {}."
            .format(as_index))
    if not is_overload_constant_bool(dropna):
        raise_bodo_error(
            "groupby(): 'dropna' parameter must be a constant bool, not {}."
            .format(dropna))
    wqp__dsfuk = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    wohl__mfunu = dict(sort=False, group_keys=True, squeeze=False, observed
        =True)
    check_unsupported_args('Dataframe.groupby', wqp__dsfuk, wohl__mfunu,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    egc__vuog = func_name == 'DataFrame.pivot_table'
    if egc__vuog:
        if is_overload_none(index) or not is_literal_type(index):
            raise_bodo_error(
                f"DataFrame.pivot_table(): 'index' argument is required and must be constant column labels"
                )
    elif not is_overload_none(index) and not is_literal_type(index):
        raise_bodo_error(
            f"{func_name}(): if 'index' argument is provided it must be constant column labels"
            )
    if is_overload_none(columns) or not is_literal_type(columns):
        raise_bodo_error(
            f"{func_name}(): 'columns' argument is required and must be a constant column label"
            )
    if not is_overload_none(values) and not is_literal_type(values):
        raise_bodo_error(
            f"{func_name}(): if 'values' argument is provided it must be constant column labels"
            )
    mivd__zkvt = get_literal_value(columns)
    if isinstance(mivd__zkvt, (list, tuple)):
        if len(mivd__zkvt) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {mivd__zkvt}"
                )
        mivd__zkvt = mivd__zkvt[0]
    if mivd__zkvt not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {mivd__zkvt} not found in DataFrame {df}."
            )
    pvx__jtgbt = df.column_index[mivd__zkvt]
    if is_overload_none(index):
        tdqvj__xzw = []
        qzc__bcv = []
    else:
        qzc__bcv = get_literal_value(index)
        if not isinstance(qzc__bcv, (list, tuple)):
            qzc__bcv = [qzc__bcv]
        tdqvj__xzw = []
        for index in qzc__bcv:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            tdqvj__xzw.append(df.column_index[index])
    if not (all(isinstance(ttn__dffux, int) for ttn__dffux in qzc__bcv) or
        all(isinstance(ttn__dffux, str) for ttn__dffux in qzc__bcv)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        gseh__ccxdh = []
        zcvc__ykczk = []
        cxm__hxhlm = tdqvj__xzw + [pvx__jtgbt]
        for i, ttn__dffux in enumerate(df.columns):
            if i not in cxm__hxhlm:
                gseh__ccxdh.append(i)
                zcvc__ykczk.append(ttn__dffux)
    else:
        zcvc__ykczk = get_literal_value(values)
        if not isinstance(zcvc__ykczk, (list, tuple)):
            zcvc__ykczk = [zcvc__ykczk]
        gseh__ccxdh = []
        for val in zcvc__ykczk:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            gseh__ccxdh.append(df.column_index[val])
    aakr__yul = set(gseh__ccxdh) | set(tdqvj__xzw) | {pvx__jtgbt}
    if len(aakr__yul) != len(gseh__ccxdh) + len(tdqvj__xzw) + 1:
        raise BodoError(
            f"{func_name}(): 'index', 'columns', and 'values' must all refer to different columns"
            )

    def check_valid_index_typ(index_column):
        if isinstance(index_column, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType, bodo.
            IntervalArrayType)):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column must have scalar rows"
                )
        if isinstance(index_column, bodo.CategoricalArrayType):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column does not support categorical data"
                )
    if len(tdqvj__xzw) == 0:
        index = df.index
        if isinstance(index, MultiIndexType):
            raise BodoError(
                f"{func_name}(): 'index' cannot be None with a DataFrame with a multi-index"
                )
        if not isinstance(index, RangeIndexType):
            check_valid_index_typ(index.data)
        if not is_literal_type(df.index.name_typ):
            raise BodoError(
                f"{func_name}(): If 'index' is None, the name of the DataFrame's Index must be constant at compile-time"
                )
    else:
        for ivhg__lcnp in tdqvj__xzw:
            index_column = df.data[ivhg__lcnp]
            check_valid_index_typ(index_column)
    nsjsx__wzb = df.data[pvx__jtgbt]
    if isinstance(nsjsx__wzb, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(nsjsx__wzb, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for yiplb__vfw in gseh__ccxdh:
        hmjk__aphm = df.data[yiplb__vfw]
        if isinstance(hmjk__aphm, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or hmjk__aphm == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (qzc__bcv, mivd__zkvt, zcvc__ykczk, tdqvj__xzw, pvx__jtgbt,
        gseh__ccxdh)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (qzc__bcv, mivd__zkvt, zcvc__ykczk, ivhg__lcnp, pvx__jtgbt, gehqy__yvjd
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot'))
    if len(qzc__bcv) == 0:
        if is_overload_none(data.index.name_typ):
            flt__lzi = None,
        else:
            flt__lzi = get_literal_value(data.index.name_typ),
    else:
        flt__lzi = tuple(qzc__bcv)
    qzc__bcv = ColNamesMetaType(flt__lzi)
    zcvc__ykczk = ColNamesMetaType(tuple(zcvc__ykczk))
    mivd__zkvt = ColNamesMetaType((mivd__zkvt,))
    rnem__hlqb = 'def impl(data, index=None, columns=None, values=None):\n'
    rnem__hlqb += f'    pivot_values = data.iloc[:, {pvx__jtgbt}].unique()\n'
    rnem__hlqb += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(ivhg__lcnp) == 0:
        rnem__hlqb += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        rnem__hlqb += '        (\n'
        for lpz__btsd in ivhg__lcnp:
            rnem__hlqb += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {lpz__btsd}),
"""
        rnem__hlqb += '        ),\n'
    rnem__hlqb += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {pvx__jtgbt}),),
"""
    rnem__hlqb += '        (\n'
    for yiplb__vfw in gehqy__yvjd:
        rnem__hlqb += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {yiplb__vfw}),
"""
    rnem__hlqb += '        ),\n'
    rnem__hlqb += '        pivot_values,\n'
    rnem__hlqb += '        index_lit,\n'
    rnem__hlqb += '        columns_lit,\n'
    rnem__hlqb += '        values_lit,\n'
    rnem__hlqb += '    )\n'
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo, 'index_lit': qzc__bcv, 'columns_lit':
        mivd__zkvt, 'values_lit': zcvc__ykczk}, qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


@overload(pd.pivot_table, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot_table', inline='always',
    no_unliteral=True)
def overload_dataframe_pivot_table(data, values=None, index=None, columns=
    None, aggfunc='mean', fill_value=None, margins=False, dropna=True,
    margins_name='All', observed=False, sort=True, _pivot_values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot_table()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot_table()')
    wqp__dsfuk = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    pncms__hkyvs = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', wqp__dsfuk,
        pncms__hkyvs, package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (qzc__bcv, mivd__zkvt, zcvc__ykczk, ivhg__lcnp, pvx__jtgbt, gehqy__yvjd
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    xsvq__itcz = qzc__bcv
    qzc__bcv = ColNamesMetaType(tuple(qzc__bcv))
    zcvc__ykczk = ColNamesMetaType(tuple(zcvc__ykczk))
    bmm__siwap = mivd__zkvt
    mivd__zkvt = ColNamesMetaType((mivd__zkvt,))
    rnem__hlqb = 'def impl(\n'
    rnem__hlqb += '    data,\n'
    rnem__hlqb += '    values=None,\n'
    rnem__hlqb += '    index=None,\n'
    rnem__hlqb += '    columns=None,\n'
    rnem__hlqb += '    aggfunc="mean",\n'
    rnem__hlqb += '    fill_value=None,\n'
    rnem__hlqb += '    margins=False,\n'
    rnem__hlqb += '    dropna=True,\n'
    rnem__hlqb += '    margins_name="All",\n'
    rnem__hlqb += '    observed=False,\n'
    rnem__hlqb += '    sort=True,\n'
    rnem__hlqb += '    _pivot_values=None,\n'
    rnem__hlqb += '):\n'
    qhpbw__smp = ivhg__lcnp + [pvx__jtgbt] + gehqy__yvjd
    rnem__hlqb += f'    data = data.iloc[:, {qhpbw__smp}]\n'
    zin__xfj = xsvq__itcz + [bmm__siwap]
    if not is_overload_none(_pivot_values):
        wmiv__urdc = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(wmiv__urdc)
        rnem__hlqb += '    pivot_values = _pivot_values_arr\n'
        rnem__hlqb += (
            f'    data = data[data.iloc[:, {len(ivhg__lcnp)}].isin(pivot_values)]\n'
            )
        if all(isinstance(ttn__dffux, str) for ttn__dffux in wmiv__urdc):
            jlx__chfp = pd.array(wmiv__urdc, 'string')
        elif all(isinstance(ttn__dffux, int) for ttn__dffux in wmiv__urdc):
            jlx__chfp = np.array(wmiv__urdc, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        jlx__chfp = None
    rnem__hlqb += (
        f'    data = data.groupby({zin__xfj!r}, as_index=False).agg(aggfunc)\n'
        )
    if is_overload_none(_pivot_values):
        rnem__hlqb += (
            f'    pivot_values = data.iloc[:, {len(ivhg__lcnp)}].unique()\n')
    rnem__hlqb += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    rnem__hlqb += '        (\n'
    for i in range(0, len(ivhg__lcnp)):
        rnem__hlqb += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    rnem__hlqb += '        ),\n'
    rnem__hlqb += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(ivhg__lcnp)}),),
"""
    rnem__hlqb += '        (\n'
    for i in range(len(ivhg__lcnp) + 1, len(gehqy__yvjd) + len(ivhg__lcnp) + 1
        ):
        rnem__hlqb += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    rnem__hlqb += '        ),\n'
    rnem__hlqb += '        pivot_values,\n'
    rnem__hlqb += '        index_lit,\n'
    rnem__hlqb += '        columns_lit,\n'
    rnem__hlqb += '        values_lit,\n'
    rnem__hlqb += '        check_duplicates=False,\n'
    rnem__hlqb += '        _constant_pivot_values=_constant_pivot_values,\n'
    rnem__hlqb += '    )\n'
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo, 'numba': numba, 'index_lit': qzc__bcv,
        'columns_lit': mivd__zkvt, 'values_lit': zcvc__ykczk,
        '_pivot_values_arr': jlx__chfp, '_constant_pivot_values':
        _pivot_values}, qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    wqp__dsfuk = dict(col_level=col_level, ignore_index=ignore_index)
    pncms__hkyvs = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(frame, DataFrameType):
        raise BodoError("pandas.melt(): 'frame' argument must be a DataFrame.")
    if not is_overload_none(id_vars) and not is_literal_type(id_vars):
        raise_bodo_error(
            "DataFrame.melt(): 'id_vars', if specified, must be a literal.")
    if not is_overload_none(value_vars) and not is_literal_type(value_vars):
        raise_bodo_error(
            "DataFrame.melt(): 'value_vars', if specified, must be a literal.")
    if not is_overload_none(var_name) and not (is_literal_type(var_name) and
        (is_scalar_type(var_name) or isinstance(value_name, types.Omitted))):
        raise_bodo_error(
            "DataFrame.melt(): 'var_name', if specified, must be a literal.")
    if value_name != 'value' and not (is_literal_type(value_name) and (
        is_scalar_type(value_name) or isinstance(value_name, types.Omitted))):
        raise_bodo_error(
            "DataFrame.melt(): 'value_name', if specified, must be a literal.")
    var_name = get_literal_value(var_name) if not is_overload_none(var_name
        ) else 'variable'
    value_name = get_literal_value(value_name
        ) if value_name != 'value' else 'value'
    rumnv__tpze = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(rumnv__tpze, (list, tuple)):
        rumnv__tpze = [rumnv__tpze]
    for ttn__dffux in rumnv__tpze:
        if ttn__dffux not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {ttn__dffux} not found in {frame}."
                )
    ica__besuv = [frame.column_index[i] for i in rumnv__tpze]
    if is_overload_none(value_vars):
        derx__eis = []
        irglb__dbw = []
        for i, ttn__dffux in enumerate(frame.columns):
            if i not in ica__besuv:
                derx__eis.append(i)
                irglb__dbw.append(ttn__dffux)
    else:
        irglb__dbw = get_literal_value(value_vars)
        if not isinstance(irglb__dbw, (list, tuple)):
            irglb__dbw = [irglb__dbw]
        irglb__dbw = [v for v in irglb__dbw if v not in rumnv__tpze]
        if not irglb__dbw:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        derx__eis = []
        for val in irglb__dbw:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            derx__eis.append(frame.column_index[val])
    for ttn__dffux in irglb__dbw:
        if ttn__dffux not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {ttn__dffux} not found in {frame}."
                )
    if not (all(isinstance(ttn__dffux, int) for ttn__dffux in irglb__dbw) or
        all(isinstance(ttn__dffux, str) for ttn__dffux in irglb__dbw)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    izjg__exh = frame.data[derx__eis[0]]
    udlch__yolzl = [frame.data[i].dtype for i in derx__eis]
    derx__eis = np.array(derx__eis, dtype=np.int64)
    ica__besuv = np.array(ica__besuv, dtype=np.int64)
    _, oznwe__ocpqn = bodo.utils.typing.get_common_scalar_dtype(udlch__yolzl)
    if not oznwe__ocpqn:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': irglb__dbw, 'val_type': izjg__exh}
    header = 'def impl(\n'
    header += '  frame,\n'
    header += '  id_vars=None,\n'
    header += '  value_vars=None,\n'
    header += '  var_name=None,\n'
    header += "  value_name='value',\n"
    header += '  col_level=None,\n'
    header += '  ignore_index=True,\n'
    header += '):\n'
    header += (
        '  dummy_id = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, 0)\n'
        )
    if frame.is_table_format and all(v == izjg__exh.dtype for v in udlch__yolzl
        ):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            derx__eis))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(irglb__dbw) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {derx__eis[0]})
"""
    else:
        ljvkt__eivw = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in derx__eis)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({ljvkt__eivw},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in ica__besuv:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(irglb__dbw)})\n'
            )
    wyer__gmi = ', '.join(f'out_id{i}' for i in ica__besuv) + (', ' if len(
        ica__besuv) > 0 else '')
    data_args = wyer__gmi + 'var_col, val_col'
    columns = tuple(rumnv__tpze + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(irglb__dbw)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    wqp__dsfuk = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    pncms__hkyvs = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(index,
        'pandas.crosstab()')
    if not isinstance(index, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'index' argument only supported for Series types, found {index}"
            )
    if not isinstance(columns, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'columns' argument only supported for Series types, found {columns}"
            )

    def _impl(index, columns, values=None, rownames=None, colnames=None,
        aggfunc=None, margins=False, margins_name='All', dropna=True,
        normalize=False, _pivot_values=None):
        return bodo.hiframes.pd_groupby_ext.crosstab_dummy(index, columns,
            _pivot_values)
    return _impl


@overload_method(DataFrameType, 'sort_values', inline='always',
    no_unliteral=True)
def overload_dataframe_sort_values(df, by, axis=0, ascending=True, inplace=
    False, kind='quicksort', na_position='last', ignore_index=False, key=
    None, _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_values()')
    wqp__dsfuk = dict(ignore_index=ignore_index, key=key)
    pncms__hkyvs = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', wqp__dsfuk,
        pncms__hkyvs, package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'sort_values')
    validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
        na_position)

    def _impl(df, by, axis=0, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', ignore_index=False, key=None,
        _bodo_transformed=False):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df, by,
            ascending, inplace, na_position)
    return _impl


def validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
    na_position):
    if is_overload_none(by) or not is_literal_type(by
        ) and not is_overload_constant_list(by):
        raise_bodo_error(
            "sort_values(): 'by' parameter only supports a constant column label or column labels. by={}"
            .format(by))
    smfsx__zsjsl = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        smfsx__zsjsl.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        ovbcz__zodd = [get_overload_const_tuple(by)]
    else:
        ovbcz__zodd = get_overload_const_list(by)
    ovbcz__zodd = set((k, '') if (k, '') in smfsx__zsjsl else k for k in
        ovbcz__zodd)
    if len(ovbcz__zodd.difference(smfsx__zsjsl)) > 0:
        ksmp__ktl = list(set(get_overload_const_list(by)).difference(
            smfsx__zsjsl))
        raise_bodo_error(f'sort_values(): invalid keys {ksmp__ktl} for by.')
    if not is_overload_zero(axis):
        raise_bodo_error(
            "sort_values(): 'axis' parameter only supports integer value 0.")
    if not is_overload_bool(ascending) and not is_overload_bool_list(ascending
        ):
        raise_bodo_error(
            "sort_values(): 'ascending' parameter must be of type bool or list of bool, not {}."
            .format(ascending))
    if not is_overload_bool(inplace):
        raise_bodo_error(
            "sort_values(): 'inplace' parameter must be of type bool, not {}."
            .format(inplace))
    if kind != 'quicksort' and not isinstance(kind, types.Omitted):
        warnings.warn(BodoWarning(
            'sort_values(): specifying sorting algorithm is not supported in Bodo. Bodo uses stable sort.'
            ))
    if is_overload_constant_str(na_position):
        na_position = get_overload_const_str(na_position)
        if na_position not in ('first', 'last'):
            raise BodoError(
                "sort_values(): na_position should either be 'first' or 'last'"
                )
    elif is_overload_constant_list(na_position):
        anjq__dho = get_overload_const_list(na_position)
        for na_position in anjq__dho:
            if na_position not in ('first', 'last'):
                raise BodoError(
                    "sort_values(): Every value in na_position should either be 'first' or 'last'"
                    )
    else:
        raise_bodo_error(
            f'sort_values(): na_position parameter must be a literal constant of type str or a constant list of str with 1 entry per key column, not {na_position}'
            )
    na_position = get_overload_const_str(na_position)
    if na_position not in ['first', 'last']:
        raise BodoError(
            "sort_values(): na_position should either be 'first' or 'last'")


@overload_method(DataFrameType, 'sort_index', inline='always', no_unliteral
    =True)
def overload_dataframe_sort_index(df, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_index()')
    wqp__dsfuk = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    pncms__hkyvs = dict(axis=0, level=None, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_bool(ascending):
        raise BodoError(
            "DataFrame.sort_index(): 'ascending' parameter must be of type bool"
            )
    if not is_overload_bool(inplace):
        raise BodoError(
            "DataFrame.sort_index(): 'inplace' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "DataFrame.sort_index(): 'na_position' should either be 'first' or 'last'"
            )

    def _impl(df, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df,
            '$_bodo_index_', ascending, inplace, na_position)
    return _impl


@overload_method(DataFrameType, 'rank', inline='always', no_unliteral=True)
def overload_dataframe_rank(df, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    rnem__hlqb = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    yvuos__faue = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(yvuos__faue))
    for i in range(yvuos__faue):
        rnem__hlqb += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(rnem__hlqb, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    wqp__dsfuk = dict(limit=limit, downcast=downcast)
    pncms__hkyvs = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    guufd__carwv = not is_overload_none(value)
    ejmb__jxyy = not is_overload_none(method)
    if guufd__carwv and ejmb__jxyy:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not guufd__carwv and not ejmb__jxyy:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if guufd__carwv:
        yyjb__xdq = 'value=value'
    else:
        yyjb__xdq = 'method=method'
    data_args = [(
        f"df['{ttn__dffux}'].fillna({yyjb__xdq}, inplace=inplace)" if
        isinstance(ttn__dffux, str) else
        f'df[{ttn__dffux}].fillna({yyjb__xdq}, inplace=inplace)') for
        ttn__dffux in df.columns]
    rnem__hlqb = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        rnem__hlqb += '  ' + '  \n'.join(data_args) + '\n'
        qbsaf__jre = {}
        exec(rnem__hlqb, {}, qbsaf__jre)
        impl = qbsaf__jre['impl']
        return impl
    else:
        return _gen_init_df(rnem__hlqb, df.columns, ', '.join(sev__wyx +
            '.values' for sev__wyx in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    wqp__dsfuk = dict(col_level=col_level, col_fill=col_fill)
    pncms__hkyvs = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', wqp__dsfuk,
        pncms__hkyvs, package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'reset_index')
    if not _is_all_levels(df, level):
        raise_bodo_error(
            'DataFrame.reset_index(): only dropping all index levels supported'
            )
    if not is_overload_constant_bool(drop):
        raise BodoError(
            "DataFrame.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.reset_index(): 'inplace' parameter should be a constant boolean value"
            )
    rnem__hlqb = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    rnem__hlqb += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(df), 1, None)\n'
        )
    drop = is_overload_true(drop)
    inplace = is_overload_true(inplace)
    columns = df.columns
    data_args = [
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}\n'.
        format(i, '' if inplace else '.copy()') for i in range(len(df.columns))
        ]
    if not drop:
        dfp__ccarb = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            dfp__ccarb)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            rnem__hlqb += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            mdzld__skrr = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = mdzld__skrr + data_args
        else:
            jik__nho = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [jik__nho] + data_args
    return _gen_init_df(rnem__hlqb, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    stu__hkil = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and stu__hkil == 1 or is_overload_constant_list(level) and list(
        get_overload_const_list(level)) == list(range(stu__hkil))


@overload_method(DataFrameType, 'dropna', inline='always', no_unliteral=True)
def overload_dataframe_dropna(df, axis=0, how='any', thresh=None, subset=
    None, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.dropna()')
    if not is_overload_constant_bool(inplace) or is_overload_true(inplace):
        raise BodoError('DataFrame.dropna(): inplace=True is not supported')
    if not is_overload_zero(axis):
        raise_bodo_error(f'df.dropna(): only axis=0 supported')
    ensure_constant_values('dropna', 'how', how, ('any', 'all'))
    if is_overload_none(subset):
        jkyyt__bmphn = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        pyj__hbxpd = get_overload_const_list(subset)
        jkyyt__bmphn = []
        for hswfx__zqa in pyj__hbxpd:
            if hswfx__zqa not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{hswfx__zqa}' not in data frame columns {df}"
                    )
            jkyyt__bmphn.append(df.column_index[hswfx__zqa])
    yvuos__faue = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(yvuos__faue))
    rnem__hlqb = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(yvuos__faue):
        rnem__hlqb += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    rnem__hlqb += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in jkyyt__bmphn)))
    rnem__hlqb += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(rnem__hlqb, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    wqp__dsfuk = dict(index=index, level=level, errors=errors)
    pncms__hkyvs = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', wqp__dsfuk, pncms__hkyvs,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'drop')
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "DataFrame.drop(): 'inplace' parameter should be a constant bool")
    if not is_overload_none(labels):
        if not is_overload_none(columns):
            raise BodoError(
                "Dataframe.drop(): Cannot specify both 'labels' and 'columns'")
        if not is_overload_constant_int(axis) or get_overload_const_int(axis
            ) != 1:
            raise_bodo_error('DataFrame.drop(): only axis=1 supported')
        if is_overload_constant_str(labels):
            vjc__gexqv = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            vjc__gexqv = get_overload_const_list(labels)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    else:
        if is_overload_none(columns):
            raise BodoError(
                "DataFrame.drop(): Need to specify at least one of 'labels' or 'columns'"
                )
        if is_overload_constant_str(columns):
            vjc__gexqv = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            vjc__gexqv = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for ttn__dffux in vjc__gexqv:
        if ttn__dffux not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(ttn__dffux, df.columns))
    if len(set(vjc__gexqv)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    kbjky__ijxnp = tuple(ttn__dffux for ttn__dffux in df.columns if 
        ttn__dffux not in vjc__gexqv)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[ttn__dffux], '.copy()' if not inplace else
        '') for ttn__dffux in kbjky__ijxnp)
    rnem__hlqb = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    rnem__hlqb += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(rnem__hlqb, kbjky__ijxnp, data_args, index)


@overload_method(DataFrameType, 'append', inline='always', no_unliteral=True)
def overload_dataframe_append(df, other, ignore_index=False,
    verify_integrity=False, sort=None):
    check_runtime_cols_unsupported(df, 'DataFrame.append()')
    check_runtime_cols_unsupported(other, 'DataFrame.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'DataFrame.append()')
    if isinstance(other, DataFrameType):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df, other), ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.BaseTuple):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df,) + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.List) and isinstance(other.dtype, DataFrameType
        ):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat([df] + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    raise BodoError(
        'invalid df.append() input. Only dataframe and list/tuple of dataframes supported'
        )


@overload_method(DataFrameType, 'sample', inline='always', no_unliteral=True)
def overload_dataframe_sample(df, n=None, frac=None, replace=False, weights
    =None, random_state=None, axis=None, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sample()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sample()')
    wqp__dsfuk = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    feow__vpbsk = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', wqp__dsfuk, feow__vpbsk,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    yvuos__faue = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(yvuos__faue))
    mxoir__qjgv = ', '.join('rhs_data_{}'.format(i) for i in range(yvuos__faue)
        )
    rnem__hlqb = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    rnem__hlqb += '  if (frac == 1 or n == len(df)) and not replace:\n'
    rnem__hlqb += (
        '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n')
    for i in range(yvuos__faue):
        rnem__hlqb += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    rnem__hlqb += '  if frac is None:\n'
    rnem__hlqb += '    frac_d = -1.0\n'
    rnem__hlqb += '  else:\n'
    rnem__hlqb += '    frac_d = frac\n'
    rnem__hlqb += '  if n is None:\n'
    rnem__hlqb += '    n_i = 0\n'
    rnem__hlqb += '  else:\n'
    rnem__hlqb += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    rnem__hlqb += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({mxoir__qjgv},), {index}, n_i, frac_d, replace)
"""
    rnem__hlqb += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(rnem__hlqb, df.columns,
        data_args, 'index')


@numba.njit
def _sizeof_fmt(num, size_qualifier=''):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f'{num:3.1f}{size_qualifier} {x}'
        num /= 1024.0
    return f'{num:3.1f}{size_qualifier} PB'


@overload_method(DataFrameType, 'info', no_unliteral=True)
def overload_dataframe_info(df, verbose=None, buf=None, max_cols=None,
    memory_usage=None, show_counts=None, null_counts=None):
    check_runtime_cols_unsupported(df, 'DataFrame.info()')
    wso__vfi = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    fqwi__okvxq = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', wso__vfi, fqwi__okvxq,
        package_name='pandas', module_name='DataFrame')
    jwhc__onkg = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            ggp__adygd = jwhc__onkg + '\n'
            ggp__adygd += 'Index: 0 entries\n'
            ggp__adygd += 'Empty DataFrame'
            print(ggp__adygd)
        return _info_impl
    else:
        rnem__hlqb = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        rnem__hlqb += '    ncols = df.shape[1]\n'
        rnem__hlqb += f'    lines = "{jwhc__onkg}\\n"\n'
        rnem__hlqb += f'    lines += "{df.index}: "\n'
        rnem__hlqb += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            rnem__hlqb += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            rnem__hlqb += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            rnem__hlqb += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        rnem__hlqb += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        rnem__hlqb += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        rnem__hlqb += '    column_width = max(space, 7)\n'
        rnem__hlqb += '    column= "Column"\n'
        rnem__hlqb += '    underl= "------"\n'
        rnem__hlqb += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        rnem__hlqb += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        rnem__hlqb += '    mem_size = 0\n'
        rnem__hlqb += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        rnem__hlqb += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        rnem__hlqb += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        ixuqa__ido = dict()
        for i in range(len(df.columns)):
            rnem__hlqb += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            pypp__ujfuv = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                pypp__ujfuv = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                jwtlz__evj = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                pypp__ujfuv = f'{jwtlz__evj[:-7]}'
            rnem__hlqb += f'    col_dtype[{i}] = "{pypp__ujfuv}"\n'
            if pypp__ujfuv in ixuqa__ido:
                ixuqa__ido[pypp__ujfuv] += 1
            else:
                ixuqa__ido[pypp__ujfuv] = 1
            rnem__hlqb += f'    col_name[{i}] = "{df.columns[i]}"\n'
            rnem__hlqb += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        rnem__hlqb += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        rnem__hlqb += '    for i in column_info:\n'
        rnem__hlqb += "        lines += f'{i}\\n'\n"
        uqux__tijh = ', '.join(f'{k}({ixuqa__ido[k]})' for k in sorted(
            ixuqa__ido))
        rnem__hlqb += f"    lines += 'dtypes: {uqux__tijh}\\n'\n"
        rnem__hlqb += '    mem_size += df.index.nbytes\n'
        rnem__hlqb += '    total_size = _sizeof_fmt(mem_size)\n'
        rnem__hlqb += "    lines += f'memory usage: {total_size}'\n"
        rnem__hlqb += '    print(lines)\n'
        qbsaf__jre = {}
        exec(rnem__hlqb, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, qbsaf__jre)
        _info_impl = qbsaf__jre['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    rnem__hlqb = 'def impl(df, index=True, deep=False):\n'
    mdtk__ovp = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes'
    zhyt__egj = is_overload_true(index)
    columns = df.columns
    if zhyt__egj:
        columns = ('Index',) + columns
    if len(columns) == 0:
        yrhe__bcqrx = ()
    elif all(isinstance(ttn__dffux, int) for ttn__dffux in columns):
        yrhe__bcqrx = np.array(columns, 'int64')
    elif all(isinstance(ttn__dffux, str) for ttn__dffux in columns):
        yrhe__bcqrx = pd.array(columns, 'string')
    else:
        yrhe__bcqrx = columns
    if df.is_table_format and len(df.columns) > 0:
        erhyi__czfs = int(zhyt__egj)
        qcwcu__bcvd = len(columns)
        rnem__hlqb += f'  nbytes_arr = np.empty({qcwcu__bcvd}, np.int64)\n'
        rnem__hlqb += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        rnem__hlqb += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {erhyi__czfs})
"""
        if zhyt__egj:
            rnem__hlqb += f'  nbytes_arr[0] = {mdtk__ovp}\n'
        rnem__hlqb += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if zhyt__egj:
            data = f'{mdtk__ovp},{data}'
        else:
            pujo__axtnu = ',' if len(columns) == 1 else ''
            data = f'{data}{pujo__axtnu}'
        rnem__hlqb += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        yrhe__bcqrx}, qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


@overload(pd.read_excel, no_unliteral=True)
def overload_read_excel(io, sheet_name=0, header=0, names=None, index_col=
    None, usecols=None, squeeze=False, dtype=None, engine=None, converters=
    None, true_values=None, false_values=None, skiprows=None, nrows=None,
    na_values=None, keep_default_na=True, na_filter=True, verbose=False,
    parse_dates=False, date_parser=None, thousands=None, comment=None,
    skipfooter=0, convert_float=True, mangle_dupe_cols=True, _bodo_df_type=None
    ):
    df_type = _bodo_df_type.instance_type
    dzg__taqcq = 'read_excel_df{}'.format(next_label())
    setattr(types, dzg__taqcq, df_type)
    czx__yjrkm = False
    if is_overload_constant_list(parse_dates):
        czx__yjrkm = get_overload_const_list(parse_dates)
    mis__ogd = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    rnem__hlqb = f"""
def impl(
    io,
    sheet_name=0,
    header=0,
    names=None,
    index_col=None,
    usecols=None,
    squeeze=False,
    dtype=None,
    engine=None,
    converters=None,
    true_values=None,
    false_values=None,
    skiprows=None,
    nrows=None,
    na_values=None,
    keep_default_na=True,
    na_filter=True,
    verbose=False,
    parse_dates=False,
    date_parser=None,
    thousands=None,
    comment=None,
    skipfooter=0,
    convert_float=True,
    mangle_dupe_cols=True,
    _bodo_df_type=None,
):
    with numba.objmode(df="{dzg__taqcq}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{mis__ogd}}},
            engine=engine,
            converters=converters,
            true_values=true_values,
            false_values=false_values,
            skiprows=skiprows,
            nrows=nrows,
            na_values=na_values,
            keep_default_na=keep_default_na,
            na_filter=na_filter,
            verbose=verbose,
            parse_dates={czx__yjrkm},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    qbsaf__jre = {}
    exec(rnem__hlqb, globals(), qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as tou__ymcu:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    rnem__hlqb = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    rnem__hlqb += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    rnem__hlqb += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        rnem__hlqb += '   fig, ax = plt.subplots()\n'
    else:
        rnem__hlqb += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        rnem__hlqb += '   fig.set_figwidth(figsize[0])\n'
        rnem__hlqb += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        rnem__hlqb += '   xlabel = x\n'
    rnem__hlqb += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        rnem__hlqb += '   ylabel = y\n'
    else:
        rnem__hlqb += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        rnem__hlqb += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        rnem__hlqb += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    rnem__hlqb += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            rnem__hlqb += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            oxz__tzui = get_overload_const_str(x)
            ajuk__ttp = df.columns.index(oxz__tzui)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if ajuk__ttp != i:
                        rnem__hlqb += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            rnem__hlqb += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        rnem__hlqb += '   ax.scatter(df[x], df[y], s=20)\n'
        rnem__hlqb += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        rnem__hlqb += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        rnem__hlqb += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        rnem__hlqb += '   ax.legend()\n'
    rnem__hlqb += '   return ax\n'
    qbsaf__jre = {}
    exec(rnem__hlqb, {'bodo': bodo, 'plt': plt}, qbsaf__jre)
    impl = qbsaf__jre['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for xgeoc__kipop in df_typ.data:
        if not (isinstance(xgeoc__kipop, IntegerArrayType) or isinstance(
            xgeoc__kipop.dtype, types.Number) or xgeoc__kipop.dtype in (
            bodo.datetime64ns, bodo.timedelta64ns)):
            return False
    return True


def typeref_to_type(v):
    if isinstance(v, types.BaseTuple):
        return types.BaseTuple.from_types(tuple(typeref_to_type(a) for a in v))
    return v.instance_type if isinstance(v, (types.TypeRef, types.NumberClass)
        ) else v


def _install_typer_for_type(type_name, typ):

    @type_callable(typ)
    def type_call_type(context):

        def typer(*args, **kws):
            args = tuple(typeref_to_type(v) for v in args)
            kws = {name: typeref_to_type(v) for name, v in kws.items()}
            return types.TypeRef(typ(*args, **kws))
        return typer
    no_side_effect_call_tuples.add((type_name, bodo))
    no_side_effect_call_tuples.add((typ,))


def _install_type_call_typers():
    for type_name in bodo_types_with_params:
        typ = getattr(bodo, type_name)
        _install_typer_for_type(type_name, typ)


_install_type_call_typers()


def set_df_col(df, cname, arr, inplace):
    df[cname] = arr


@infer_global(set_df_col)
class SetDfColInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 4
        assert isinstance(args[1], types.Literal)
        spb__bgboy = args[0]
        hkubc__dpa = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        qbhi__niev = spb__bgboy
        check_runtime_cols_unsupported(spb__bgboy, 'set_df_col()')
        if isinstance(spb__bgboy, DataFrameType):
            index = spb__bgboy.index
            if len(spb__bgboy.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(spb__bgboy.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if is_overload_constant_str(val) or val == types.unicode_type:
                val = bodo.dict_str_arr_type
            elif not is_array_typ(val):
                val = dtype_to_array_type(val)
            if hkubc__dpa in spb__bgboy.columns:
                kbjky__ijxnp = spb__bgboy.columns
                uwxw__uvmfh = spb__bgboy.columns.index(hkubc__dpa)
                aerm__mywci = list(spb__bgboy.data)
                aerm__mywci[uwxw__uvmfh] = val
                aerm__mywci = tuple(aerm__mywci)
            else:
                kbjky__ijxnp = spb__bgboy.columns + (hkubc__dpa,)
                aerm__mywci = spb__bgboy.data + (val,)
            qbhi__niev = DataFrameType(aerm__mywci, index, kbjky__ijxnp,
                spb__bgboy.dist, spb__bgboy.is_table_format)
        return qbhi__niev(*args)


SetDfColInfer.prefer_literal = True


def __bodosql_replace_columns_dummy(df, col_names_to_replace,
    cols_to_replace_with):
    for i in range(len(col_names_to_replace)):
        df[col_names_to_replace[i]] = cols_to_replace_with[i]


@infer_global(__bodosql_replace_columns_dummy)
class BodoSQLReplaceColsInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 3
        assert is_overload_constant_tuple(args[1])
        assert isinstance(args[2], types.BaseTuple)
        hesen__puxza = args[0]
        assert isinstance(hesen__puxza, DataFrameType) and len(hesen__puxza
            .columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        aqknl__zpiul = args[2]
        assert len(col_names_to_replace) == len(aqknl__zpiul
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(hesen__puxza.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in hesen__puxza.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(hesen__puxza,
            '__bodosql_replace_columns_dummy()')
        index = hesen__puxza.index
        kbjky__ijxnp = hesen__puxza.columns
        aerm__mywci = list(hesen__puxza.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            yclve__kzypy = aqknl__zpiul[i]
            assert isinstance(yclve__kzypy, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(yclve__kzypy, SeriesType):
                yclve__kzypy = yclve__kzypy.data
            zsiid__ikfkq = hesen__puxza.column_index[col_name]
            aerm__mywci[zsiid__ikfkq] = yclve__kzypy
        aerm__mywci = tuple(aerm__mywci)
        qbhi__niev = DataFrameType(aerm__mywci, index, kbjky__ijxnp,
            hesen__puxza.dist, hesen__puxza.is_table_format)
        return qbhi__niev(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    mzib__cxyi = {}

    def _rewrite_membership_op(self, node, left, right):
        nksyf__jtes = node.op
        op = self.visit(nksyf__jtes)
        return op, nksyf__jtes, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    lyaup__kqwfs = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in lyaup__kqwfs:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in lyaup__kqwfs:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        hug__ozz = node.attr
        value = node.value
        fmfaj__hkg = pd.core.computation.ops.LOCAL_TAG
        if hug__ozz in ('str', 'dt'):
            try:
                enacn__psn = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as kbm__bneo:
                col_name = kbm__bneo.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            enacn__psn = str(self.visit(value))
        bxoj__pfvx = enacn__psn, hug__ozz
        if bxoj__pfvx in join_cleaned_cols:
            hug__ozz = join_cleaned_cols[bxoj__pfvx]
        name = enacn__psn + '.' + hug__ozz
        if name.startswith(fmfaj__hkg):
            name = name[len(fmfaj__hkg):]
        if hug__ozz in ('str', 'dt'):
            gnlrt__zht = columns[cleaned_columns.index(enacn__psn)]
            mzib__cxyi[gnlrt__zht] = enacn__psn
            self.env.scope[name] = 0
            return self.term_type(fmfaj__hkg + name, self.env)
        lyaup__kqwfs.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in lyaup__kqwfs:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        qxny__meic = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        hkubc__dpa = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(qxny__meic), hkubc__dpa))

    def op__str__(self):
        xnlcq__gic = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            jug__klb)) for jug__klb in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(xnlcq__gic)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(xnlcq__gic)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(xnlcq__gic))
    nmkcg__qgw = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    yush__njqfc = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_evaluate_binop)
    rcuv__wxc = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    blbkf__iofk = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    uhsy__rxc = pd.core.computation.ops.Term.__str__
    mtkc__tjp = pd.core.computation.ops.MathCall.__str__
    scm__rbqp = pd.core.computation.ops.Op.__str__
    gsm__igq = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
    try:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            _rewrite_membership_op)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            _maybe_evaluate_binop)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = (
            visit_Attribute)
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = lambda self, left, right: (left, right)
        pd.core.computation.ops.Term.__str__ = __str__
        pd.core.computation.ops.MathCall.__str__ = math__str__
        pd.core.computation.ops.Op.__str__ = op__str__
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        ecsht__axed = pd.core.computation.expr.Expr(expr, env=env)
        pvbe__fonhe = str(ecsht__axed)
    except pd.core.computation.ops.UndefinedVariableError as kbm__bneo:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == kbm__bneo.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {kbm__bneo}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            nmkcg__qgw)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            yush__njqfc)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = rcuv__wxc
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = blbkf__iofk
        pd.core.computation.ops.Term.__str__ = uhsy__rxc
        pd.core.computation.ops.MathCall.__str__ = mtkc__tjp
        pd.core.computation.ops.Op.__str__ = scm__rbqp
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = gsm__igq
    php__nzimm = pd.core.computation.parsing.clean_column_name
    mzib__cxyi.update({ttn__dffux: php__nzimm(ttn__dffux) for ttn__dffux in
        columns if php__nzimm(ttn__dffux) in ecsht__axed.names})
    return ecsht__axed, pvbe__fonhe, mzib__cxyi


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        fmvgh__xjxd = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(fmvgh__xjxd))
        quyf__aqf = namedtuple('Pandas', col_names)
        iqysv__kaifl = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], quyf__aqf)
        super(DataFrameTupleIterator, self).__init__(name, iqysv__kaifl)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_series_dtype(arr_typ):
    if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return pd_timestamp_type
    return arr_typ.dtype


def get_itertuples():
    pass


@infer_global(get_itertuples)
class TypeIterTuples(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) % 2 == 0, 'name and column pairs expected'
        col_names = [a.literal_value for a in args[:len(args) // 2]]
        imhk__epiq = [if_series_to_array_type(a) for a in args[len(args) // 2:]
            ]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        imhk__epiq = [types.Array(types.int64, 1, 'C')] + imhk__epiq
        kwnh__sppi = DataFrameTupleIterator(col_names, imhk__epiq)
        return kwnh__sppi(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        vacfg__arl = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            vacfg__arl)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    livjy__nhdjz = args[len(args) // 2:]
    xsl__lwxzt = sig.args[len(sig.args) // 2:]
    mweep__vgmjs = context.make_helper(builder, sig.return_type)
    xtrb__qtn = context.get_constant(types.intp, 0)
    dda__onsf = cgutils.alloca_once_value(builder, xtrb__qtn)
    mweep__vgmjs.index = dda__onsf
    for i, arr in enumerate(livjy__nhdjz):
        setattr(mweep__vgmjs, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(livjy__nhdjz, xsl__lwxzt):
        context.nrt.incref(builder, arr_typ, arr)
    res = mweep__vgmjs._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    bzmyl__dqblc, = sig.args
    dvtyj__rnrm, = args
    mweep__vgmjs = context.make_helper(builder, bzmyl__dqblc, value=dvtyj__rnrm
        )
    dhn__omav = signature(types.intp, bzmyl__dqblc.array_types[1])
    nbswb__lnvbn = context.compile_internal(builder, lambda a: len(a),
        dhn__omav, [mweep__vgmjs.array0])
    index = builder.load(mweep__vgmjs.index)
    dyndu__aea = builder.icmp_signed('<', index, nbswb__lnvbn)
    result.set_valid(dyndu__aea)
    with builder.if_then(dyndu__aea):
        values = [index]
        for i, arr_typ in enumerate(bzmyl__dqblc.array_types[1:]):
            qfnu__mxe = getattr(mweep__vgmjs, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                fvgyz__grj = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    fvgyz__grj, [qfnu__mxe, index])
            else:
                fvgyz__grj = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    fvgyz__grj, [qfnu__mxe, index])
            values.append(val)
        value = context.make_tuple(builder, bzmyl__dqblc.yield_type, values)
        result.yield_(value)
        grz__nkwjs = cgutils.increment_index(builder, index)
        builder.store(grz__nkwjs, mweep__vgmjs.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    ysfy__mjaw = ir.Assign(rhs, lhs, expr.loc)
    weny__xmy = lhs
    ngz__xbrr = []
    nyn__sms = []
    czwt__vmg = typ.count
    for i in range(czwt__vmg):
        ffveu__pvmi = ir.Var(weny__xmy.scope, mk_unique_var('{}_size{}'.
            format(weny__xmy.name, i)), weny__xmy.loc)
        swayo__lqev = ir.Expr.static_getitem(lhs, i, None, weny__xmy.loc)
        self.calltypes[swayo__lqev] = None
        ngz__xbrr.append(ir.Assign(swayo__lqev, ffveu__pvmi, weny__xmy.loc))
        self._define(equiv_set, ffveu__pvmi, types.intp, swayo__lqev)
        nyn__sms.append(ffveu__pvmi)
    zkeul__zsp = tuple(nyn__sms)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        zkeul__zsp, pre=[ysfy__mjaw] + ngz__xbrr)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
