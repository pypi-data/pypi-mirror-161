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
        iri__qrf = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({iri__qrf})\n')
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    seamk__yowxi = 'def impl(df):\n'
    if df.has_runtime_cols:
        seamk__yowxi += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        xsvjz__iswk = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        seamk__yowxi += f'  return {xsvjz__iswk}'
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo}, fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
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
    nau__kbf = len(df.columns)
    qqimf__iklk = set(i for i in range(nau__kbf) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in qqimf__iklk else '') for i in
        range(nau__kbf))
    seamk__yowxi = 'def f(df):\n'.format()
    seamk__yowxi += '    return np.stack(({},), 1)\n'.format(data_args)
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo, 'np': np}, fhzpo__mfnv)
    poznf__tgudw = fhzpo__mfnv['f']
    return poznf__tgudw


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
    vedy__vptzn = {'dtype': dtype, 'na_value': na_value}
    fyc__puhj = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', vedy__vptzn, fyc__puhj,
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
            wbdb__pda = bodo.hiframes.table.compute_num_runtime_columns(t)
            return wbdb__pda * len(t)
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
            wbdb__pda = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), wbdb__pda
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    seamk__yowxi = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    jzuj__rxo = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    seamk__yowxi += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{jzuj__rxo}), {index}, None)
"""
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo}, fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
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
    vedy__vptzn = {'copy': copy, 'errors': errors}
    fyc__puhj = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', vedy__vptzn, fyc__puhj,
        package_name='pandas', module_name='DataFrame')
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
        ajsr__vhk = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        rcju__rcff = _bodo_object_typeref.instance_type
        assert isinstance(rcju__rcff, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in rcju__rcff.column_index:
                    idx = rcju__rcff.column_index[name]
                    arr_typ = rcju__rcff.data[idx]
                else:
                    arr_typ = df.data[i]
                ajsr__vhk.append(arr_typ)
        else:
            extra_globals = {}
            odq__gzz = {}
            for i, name in enumerate(rcju__rcff.columns):
                arr_typ = rcju__rcff.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    xbg__emyz = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    xbg__emyz = boolean_dtype
                else:
                    xbg__emyz = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = xbg__emyz
                odq__gzz[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {odq__gzz[mco__qfdp]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if mco__qfdp in odq__gzz else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, mco__qfdp in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        ncwm__pru = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            ncwm__pru = {name: dtype_to_array_type(parse_dtype(dtype)) for 
                name, dtype in ncwm__pru.items()}
            for i, name in enumerate(df.columns):
                if name in ncwm__pru:
                    arr_typ = ncwm__pru[name]
                else:
                    arr_typ = df.data[i]
                ajsr__vhk.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(ncwm__pru[mco__qfdp])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if mco__qfdp in ncwm__pru else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, mco__qfdp in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        ajsr__vhk = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        vdcn__uhtml = bodo.TableType(tuple(ajsr__vhk))
        extra_globals['out_table_typ'] = vdcn__uhtml
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
        othf__tis = types.none
        extra_globals = {'output_arr_typ': othf__tis}
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
        tfw__yzar = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                tfw__yzar.append(arr + '.copy()')
            elif is_overload_false(deep):
                tfw__yzar.append(arr)
            else:
                tfw__yzar.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(tfw__yzar)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    vedy__vptzn = {'index': index, 'level': level, 'errors': errors}
    fyc__puhj = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', vedy__vptzn, fyc__puhj,
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
        scvxm__beos = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        scvxm__beos = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    zjer__vdzu = tuple([scvxm__beos.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    eyy__fnf = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        eyy__fnf = df.copy(columns=zjer__vdzu)
        othf__tis = types.none
        extra_globals = {'output_arr_typ': othf__tis}
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
        tfw__yzar = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                tfw__yzar.append(arr + '.copy()')
            elif is_overload_false(copy):
                tfw__yzar.append(arr)
            else:
                tfw__yzar.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(tfw__yzar)
    return _gen_init_df(header, zjer__vdzu, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    nbqrh__ubew = not is_overload_none(items)
    islkz__qrka = not is_overload_none(like)
    jvhy__xmu = not is_overload_none(regex)
    fsj__imuyo = nbqrh__ubew ^ islkz__qrka ^ jvhy__xmu
    wcxic__jndp = not (nbqrh__ubew or islkz__qrka or jvhy__xmu)
    if wcxic__jndp:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not fsj__imuyo:
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
        jobrd__tnb = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        jobrd__tnb = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert jobrd__tnb in {0, 1}
    seamk__yowxi = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if jobrd__tnb == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if jobrd__tnb == 1:
        ujb__gzprs = []
        aua__cbt = []
        gca__owvp = []
        if nbqrh__ubew:
            if is_overload_constant_list(items):
                hhmkk__bhioz = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if islkz__qrka:
            if is_overload_constant_str(like):
                bvlbi__fbi = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if jvhy__xmu:
            if is_overload_constant_str(regex):
                lrpmp__btzye = get_overload_const_str(regex)
                fbd__dlrwf = re.compile(lrpmp__btzye)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, mco__qfdp in enumerate(df.columns):
            if not is_overload_none(items
                ) and mco__qfdp in hhmkk__bhioz or not is_overload_none(like
                ) and bvlbi__fbi in str(mco__qfdp) or not is_overload_none(
                regex) and fbd__dlrwf.search(str(mco__qfdp)):
                aua__cbt.append(mco__qfdp)
                gca__owvp.append(i)
        for i in gca__owvp:
            var_name = f'data_{i}'
            ujb__gzprs.append(var_name)
            seamk__yowxi += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(ujb__gzprs)
        return _gen_init_df(seamk__yowxi, aua__cbt, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    eyy__fnf = None
    if df.is_table_format:
        othf__tis = types.Array(types.bool_, 1, 'C')
        eyy__fnf = DataFrameType(tuple([othf__tis] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': othf__tis}
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
    ieqle__faifi = is_overload_none(include)
    iiltm__aruju = is_overload_none(exclude)
    jkxpl__ymii = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if ieqle__faifi and iiltm__aruju:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not ieqle__faifi:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            yzoo__fkkmn = [dtype_to_array_type(parse_dtype(elem,
                jkxpl__ymii)) for elem in include]
        elif is_legal_input(include):
            yzoo__fkkmn = [dtype_to_array_type(parse_dtype(include,
                jkxpl__ymii))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        yzoo__fkkmn = get_nullable_and_non_nullable_types(yzoo__fkkmn)
        lwbi__kpi = tuple(mco__qfdp for i, mco__qfdp in enumerate(df.
            columns) if df.data[i] in yzoo__fkkmn)
    else:
        lwbi__kpi = df.columns
    if not iiltm__aruju:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            yknv__ekj = [dtype_to_array_type(parse_dtype(elem, jkxpl__ymii)
                ) for elem in exclude]
        elif is_legal_input(exclude):
            yknv__ekj = [dtype_to_array_type(parse_dtype(exclude, jkxpl__ymii))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        yknv__ekj = get_nullable_and_non_nullable_types(yknv__ekj)
        lwbi__kpi = tuple(mco__qfdp for mco__qfdp in lwbi__kpi if df.data[
            df.column_index[mco__qfdp]] not in yknv__ekj)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[mco__qfdp]})'
         for mco__qfdp in lwbi__kpi)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, lwbi__kpi, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    eyy__fnf = None
    if df.is_table_format:
        othf__tis = types.Array(types.bool_, 1, 'C')
        eyy__fnf = DataFrameType(tuple([othf__tis] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': othf__tis}
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
    coy__yhbzc = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in coy__yhbzc:
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
    coy__yhbzc = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in coy__yhbzc:
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
    seamk__yowxi = 'def impl(df, values):\n'
    zts__xznra = {}
    caf__praqo = False
    if isinstance(values, DataFrameType):
        caf__praqo = True
        for i, mco__qfdp in enumerate(df.columns):
            if mco__qfdp in values.column_index:
                ebh__ywf = 'val{}'.format(i)
                seamk__yowxi += f"""  {ebh__ywf} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[mco__qfdp]})
"""
                zts__xznra[mco__qfdp] = ebh__ywf
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        zts__xznra = {mco__qfdp: 'values' for mco__qfdp in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        ebh__ywf = 'data{}'.format(i)
        seamk__yowxi += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(ebh__ywf, i))
        data.append(ebh__ywf)
    agtu__ytzvn = ['out{}'.format(i) for i in range(len(df.columns))]
    hlc__nycte = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    siy__kxex = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    slwg__mvqm = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, cks__aco) in enumerate(zip(df.columns, data)):
        if cname in zts__xznra:
            yqs__brvq = zts__xznra[cname]
            if caf__praqo:
                seamk__yowxi += hlc__nycte.format(cks__aco, yqs__brvq,
                    agtu__ytzvn[i])
            else:
                seamk__yowxi += siy__kxex.format(cks__aco, yqs__brvq,
                    agtu__ytzvn[i])
        else:
            seamk__yowxi += slwg__mvqm.format(agtu__ytzvn[i])
    return _gen_init_df(seamk__yowxi, df.columns, ','.join(agtu__ytzvn))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    nau__kbf = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(nau__kbf))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    mub__tuz = [mco__qfdp for mco__qfdp, nzz__dyoc in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(nzz__dyoc.dtype)]
    assert len(mub__tuz) != 0
    mokik__wuz = ''
    if not any(nzz__dyoc == types.float64 for nzz__dyoc in df.data):
        mokik__wuz = '.astype(np.float64)'
    mtjme__njv = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[mco__qfdp], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[mco__qfdp]], IntegerArrayType) or
        df.data[df.column_index[mco__qfdp]] == boolean_array else '') for
        mco__qfdp in mub__tuz)
    wxwk__egomq = 'np.stack(({},), 1){}'.format(mtjme__njv, mokik__wuz)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(mub__tuz)))
    index = f'{generate_col_to_index_func_text(mub__tuz)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(wxwk__egomq)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, mub__tuz, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    alz__bgvkd = dict(ddof=ddof)
    psl__scy = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    ixxjf__mdy = '1' if is_overload_none(min_periods) else 'min_periods'
    mub__tuz = [mco__qfdp for mco__qfdp, nzz__dyoc in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(nzz__dyoc.dtype)]
    if len(mub__tuz) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    mokik__wuz = ''
    if not any(nzz__dyoc == types.float64 for nzz__dyoc in df.data):
        mokik__wuz = '.astype(np.float64)'
    mtjme__njv = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[mco__qfdp], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[mco__qfdp]], IntegerArrayType) or
        df.data[df.column_index[mco__qfdp]] == boolean_array else '') for
        mco__qfdp in mub__tuz)
    wxwk__egomq = 'np.stack(({},), 1){}'.format(mtjme__njv, mokik__wuz)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(mub__tuz)))
    index = f'pd.Index({mub__tuz})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(wxwk__egomq)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        ixxjf__mdy)
    return _gen_init_df(header, mub__tuz, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    alz__bgvkd = dict(axis=axis, level=level, numeric_only=numeric_only)
    psl__scy = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    seamk__yowxi = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    seamk__yowxi += '  data = np.array([{}])\n'.format(data_args)
    xsvjz__iswk = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    seamk__yowxi += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {xsvjz__iswk})\n'
        )
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo, 'np': np}, fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    alz__bgvkd = dict(axis=axis)
    psl__scy = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    seamk__yowxi = 'def impl(df, axis=0, dropna=True):\n'
    seamk__yowxi += '  data = np.asarray(({},))\n'.format(data_args)
    xsvjz__iswk = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    seamk__yowxi += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {xsvjz__iswk})\n'
        )
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo, 'np': np}, fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    alz__bgvkd = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    psl__scy = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    alz__bgvkd = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    psl__scy = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    alz__bgvkd = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    psl__scy = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    alz__bgvkd = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    psl__scy = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    alz__bgvkd = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    psl__scy = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    alz__bgvkd = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    psl__scy = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    alz__bgvkd = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    psl__scy = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    alz__bgvkd = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    psl__scy = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    alz__bgvkd = dict(numeric_only=numeric_only, interpolation=interpolation)
    psl__scy = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    alz__bgvkd = dict(axis=axis, skipna=skipna)
    psl__scy = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for wgg__nuhbj in df.data:
        if not (bodo.utils.utils.is_np_array_typ(wgg__nuhbj) and (
            wgg__nuhbj.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(wgg__nuhbj.dtype, (types.Number, types.Boolean))) or
            isinstance(wgg__nuhbj, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or wgg__nuhbj in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {wgg__nuhbj} not supported.'
                )
        if isinstance(wgg__nuhbj, bodo.CategoricalArrayType
            ) and not wgg__nuhbj.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    alz__bgvkd = dict(axis=axis, skipna=skipna)
    psl__scy = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for wgg__nuhbj in df.data:
        if not (bodo.utils.utils.is_np_array_typ(wgg__nuhbj) and (
            wgg__nuhbj.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(wgg__nuhbj.dtype, (types.Number, types.Boolean))) or
            isinstance(wgg__nuhbj, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or wgg__nuhbj in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {wgg__nuhbj} not supported.'
                )
        if isinstance(wgg__nuhbj, bodo.CategoricalArrayType
            ) and not wgg__nuhbj.dtype.ordered:
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
        mub__tuz = tuple(mco__qfdp for mco__qfdp, nzz__dyoc in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (nzz__dyoc.dtype))
        out_colnames = mub__tuz
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            smrs__bkzg = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[mco__qfdp]].dtype) for mco__qfdp in out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(smrs__bkzg, []))
    except NotImplementedError as wnw__pohln:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    rzmjh__ssek = ''
    if func_name in ('sum', 'prod'):
        rzmjh__ssek = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    seamk__yowxi = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, rzmjh__ssek))
    if func_name == 'quantile':
        seamk__yowxi = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        seamk__yowxi = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        seamk__yowxi += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        seamk__yowxi += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    ovwei__onjr = ''
    if func_name in ('min', 'max'):
        ovwei__onjr = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        ovwei__onjr = ', dtype=np.float32'
    wpf__phmk = f'bodo.libs.array_ops.array_op_{func_name}'
    ayjt__obe = ''
    if func_name in ['sum', 'prod']:
        ayjt__obe = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        ayjt__obe = 'index'
    elif func_name == 'quantile':
        ayjt__obe = 'q'
    elif func_name in ['std', 'var']:
        ayjt__obe = 'True, ddof'
    elif func_name == 'median':
        ayjt__obe = 'True'
    data_args = ', '.join(
        f'{wpf__phmk}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[mco__qfdp]}), {ayjt__obe})'
         for mco__qfdp in out_colnames)
    seamk__yowxi = ''
    if func_name in ('idxmax', 'idxmin'):
        seamk__yowxi += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        seamk__yowxi += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        seamk__yowxi += '  data = np.asarray(({},){})\n'.format(data_args,
            ovwei__onjr)
    seamk__yowxi += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return seamk__yowxi


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    mvdkj__vntc = [df_type.column_index[mco__qfdp] for mco__qfdp in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in mvdkj__vntc)
    ussde__acbv = '\n        '.join(f'row[{i}] = arr_{mvdkj__vntc[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    gkm__odk = f'len(arr_{mvdkj__vntc[0]})'
    dkjot__efj = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in dkjot__efj:
        vqfnx__gso = dkjot__efj[func_name]
        fch__cgs = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        seamk__yowxi = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {gkm__odk}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{fch__cgs})
    for i in numba.parfors.parfor.internal_prange(n):
        {ussde__acbv}
        A[i] = {vqfnx__gso}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return seamk__yowxi
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    alz__bgvkd = dict(fill_method=fill_method, limit=limit, freq=freq)
    psl__scy = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', alz__bgvkd, psl__scy,
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
    alz__bgvkd = dict(axis=axis, skipna=skipna)
    psl__scy = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', alz__bgvkd, psl__scy,
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
    alz__bgvkd = dict(skipna=skipna)
    psl__scy = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', alz__bgvkd, psl__scy,
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
    alz__bgvkd = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    psl__scy = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    mub__tuz = [mco__qfdp for mco__qfdp, nzz__dyoc in zip(df.columns, df.
        data) if _is_describe_type(nzz__dyoc)]
    if len(mub__tuz) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    hxev__sat = sum(df.data[df.column_index[mco__qfdp]].dtype == bodo.
        datetime64ns for mco__qfdp in mub__tuz)

    def _get_describe(col_ind):
        byr__miug = df.data[col_ind].dtype == bodo.datetime64ns
        if hxev__sat and hxev__sat != len(mub__tuz):
            if byr__miug:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for mco__qfdp in mub__tuz:
        col_ind = df.column_index[mco__qfdp]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[mco__qfdp]) for
        mco__qfdp in mub__tuz)
    kjweq__daqhr = (
        "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']")
    if hxev__sat == len(mub__tuz):
        kjweq__daqhr = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif hxev__sat:
        kjweq__daqhr = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({kjweq__daqhr})'
    return _gen_init_df(header, mub__tuz, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    alz__bgvkd = dict(axis=axis, convert=convert, is_copy=is_copy)
    psl__scy = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', alz__bgvkd, psl__scy,
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
    alz__bgvkd = dict(freq=freq, axis=axis, fill_value=fill_value)
    psl__scy = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for hkl__wpjnv in df.data:
        if not is_supported_shift_array_type(hkl__wpjnv):
            raise BodoError(
                f'Dataframe.shift() column input type {hkl__wpjnv.dtype} not supported yet.'
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
    alz__bgvkd = dict(axis=axis)
    psl__scy = dict(axis=0)
    check_unsupported_args('DataFrame.diff', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for hkl__wpjnv in df.data:
        if not (isinstance(hkl__wpjnv, types.Array) and (isinstance(
            hkl__wpjnv.dtype, types.Number) or hkl__wpjnv.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {hkl__wpjnv.dtype} not supported.'
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
    rtmpq__tqwks = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(rtmpq__tqwks)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        ycea__bauen = get_overload_const_list(column)
    else:
        ycea__bauen = [get_literal_value(column)]
    vbt__mab = [df.column_index[mco__qfdp] for mco__qfdp in ycea__bauen]
    for i in vbt__mab:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{vbt__mab[0]})\n'
        )
    for i in range(n):
        if i in vbt__mab:
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
    vedy__vptzn = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    fyc__puhj = {'inplace': False, 'append': False, 'verify_integrity': False}
    check_unsupported_args('DataFrame.set_index', vedy__vptzn, fyc__puhj,
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
    columns = tuple(mco__qfdp for mco__qfdp in df.columns if mco__qfdp !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    vedy__vptzn = {'inplace': inplace}
    fyc__puhj = {'inplace': False}
    check_unsupported_args('query', vedy__vptzn, fyc__puhj, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        bllgi__gqp = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[bllgi__gqp]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    vedy__vptzn = {'subset': subset, 'keep': keep}
    fyc__puhj = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', vedy__vptzn, fyc__puhj,
        package_name='pandas', module_name='DataFrame')
    nau__kbf = len(df.columns)
    seamk__yowxi = "def impl(df, subset=None, keep='first'):\n"
    for i in range(nau__kbf):
        seamk__yowxi += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    dyqf__gaq = ', '.join(f'data_{i}' for i in range(nau__kbf))
    dyqf__gaq += ',' if nau__kbf == 1 else ''
    seamk__yowxi += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({dyqf__gaq}))\n')
    seamk__yowxi += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    seamk__yowxi += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo}, fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    vedy__vptzn = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    fyc__puhj = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    zqxm__doe = []
    if is_overload_constant_list(subset):
        zqxm__doe = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        zqxm__doe = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        zqxm__doe = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    xalcf__pezc = []
    for col_name in zqxm__doe:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        xalcf__pezc.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', vedy__vptzn,
        fyc__puhj, package_name='pandas', module_name='DataFrame')
    myx__oty = []
    if xalcf__pezc:
        for etmfn__ibyhh in xalcf__pezc:
            if isinstance(df.data[etmfn__ibyhh], bodo.MapArrayType):
                myx__oty.append(df.columns[etmfn__ibyhh])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                myx__oty.append(col_name)
    if myx__oty:
        raise BodoError(f'DataFrame.drop_duplicates(): Columns {myx__oty} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    nau__kbf = len(df.columns)
    sogch__bcxaz = ['data_{}'.format(i) for i in xalcf__pezc]
    mgzeo__bxuo = ['data_{}'.format(i) for i in range(nau__kbf) if i not in
        xalcf__pezc]
    if sogch__bcxaz:
        jpim__dhxk = len(sogch__bcxaz)
    else:
        jpim__dhxk = nau__kbf
    vlw__etggt = ', '.join(sogch__bcxaz + mgzeo__bxuo)
    data_args = ', '.join('data_{}'.format(i) for i in range(nau__kbf))
    seamk__yowxi = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(nau__kbf):
        seamk__yowxi += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    seamk__yowxi += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(vlw__etggt, index, jpim__dhxk))
    seamk__yowxi += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(seamk__yowxi, df.columns, data_args, 'index')


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
            mbt__cqtrh = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                mbt__cqtrh = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                mbt__cqtrh = lambda i: f'other[:,{i}]'
        nau__kbf = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {mbt__cqtrh(i)})'
             for i in range(nau__kbf))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        tljb__mesx = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(tljb__mesx
            )


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    alz__bgvkd = dict(inplace=inplace, level=level, errors=errors, try_cast
        =try_cast)
    psl__scy = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', alz__bgvkd, psl__scy,
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
    nau__kbf = len(df.columns)
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
        for i in range(nau__kbf):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(nau__kbf):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(nau__kbf):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    piilm__toz = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    seamk__yowxi = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    fhzpo__mfnv = {}
    qhahn__qle = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': piilm__toz}
    qhahn__qle.update(extra_globals)
    exec(seamk__yowxi, qhahn__qle, fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        uvgt__jcz = pd.Index(lhs.columns)
        ygqf__cilz = pd.Index(rhs.columns)
        nwnu__jxd, anet__ghu, jcxt__cvc = uvgt__jcz.join(ygqf__cilz, how=
            'left' if is_inplace else 'outer', level=None, return_indexers=True
            )
        return tuple(nwnu__jxd), anet__ghu, jcxt__cvc
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        cszo__hdk = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        jtr__jwhyc = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, cszo__hdk)
        check_runtime_cols_unsupported(rhs, cszo__hdk)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                nwnu__jxd, anet__ghu, jcxt__cvc = _get_binop_columns(lhs, rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {nwn__pjj}) {cszo__hdk}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {vrsfz__irjli})'
                     if nwn__pjj != -1 and vrsfz__irjli != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for nwn__pjj, vrsfz__irjli in zip(anet__ghu, jcxt__cvc))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, nwnu__jxd, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            jxcz__zje = []
            bawvn__jsel = []
            if op in jtr__jwhyc:
                for i, kheo__iqxm in enumerate(lhs.data):
                    if is_common_scalar_dtype([kheo__iqxm.dtype, rhs]):
                        jxcz__zje.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {cszo__hdk} rhs'
                            )
                    else:
                        xxymh__fgy = f'arr{i}'
                        bawvn__jsel.append(xxymh__fgy)
                        jxcz__zje.append(xxymh__fgy)
                data_args = ', '.join(jxcz__zje)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {cszo__hdk} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(bawvn__jsel) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {xxymh__fgy} = np.empty(n, dtype=np.bool_)\n' for
                    xxymh__fgy in bawvn__jsel)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(xxymh__fgy, 
                    op == operator.ne) for xxymh__fgy in bawvn__jsel)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            jxcz__zje = []
            bawvn__jsel = []
            if op in jtr__jwhyc:
                for i, kheo__iqxm in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, kheo__iqxm.dtype]):
                        jxcz__zje.append(
                            f'lhs {cszo__hdk} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        xxymh__fgy = f'arr{i}'
                        bawvn__jsel.append(xxymh__fgy)
                        jxcz__zje.append(xxymh__fgy)
                data_args = ', '.join(jxcz__zje)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, cszo__hdk) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(bawvn__jsel) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(xxymh__fgy) for xxymh__fgy in bawvn__jsel)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(xxymh__fgy, 
                    op == operator.ne) for xxymh__fgy in bawvn__jsel)
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
        tljb__mesx = create_binary_op_overload(op)
        overload(op)(tljb__mesx)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        cszo__hdk = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, cszo__hdk)
        check_runtime_cols_unsupported(right, cszo__hdk)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                nwnu__jxd, _, jcxt__cvc = _get_binop_columns(left, right, True)
                seamk__yowxi = 'def impl(left, right):\n'
                for i, vrsfz__irjli in enumerate(jcxt__cvc):
                    if vrsfz__irjli == -1:
                        seamk__yowxi += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    seamk__yowxi += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    seamk__yowxi += f"""  df_arr{i} {cszo__hdk} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {vrsfz__irjli})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    nwnu__jxd)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(seamk__yowxi, nwnu__jxd, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            seamk__yowxi = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                seamk__yowxi += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                seamk__yowxi += '  df_arr{0} {1} right\n'.format(i, cszo__hdk)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(seamk__yowxi, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        tljb__mesx = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(tljb__mesx)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            cszo__hdk = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, cszo__hdk)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, cszo__hdk) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        tljb__mesx = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(tljb__mesx)


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
            jlb__bdax = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                jlb__bdax[i] = bodo.libs.array_kernels.isna(obj, i)
            return jlb__bdax
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
            jlb__bdax = np.empty(n, np.bool_)
            for i in range(n):
                jlb__bdax[i] = pd.isna(obj[i])
            return jlb__bdax
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
    vedy__vptzn = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    fyc__puhj = {'inplace': False, 'limit': None, 'regex': False, 'method':
        'pad'}
    check_unsupported_args('replace', vedy__vptzn, fyc__puhj, package_name=
        'pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    enqhm__vzzjn = str(expr_node)
    return enqhm__vzzjn.startswith('left.') or enqhm__vzzjn.startswith('right.'
        )


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    zfrx__qebq = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (zfrx__qebq,))
    gfqde__oqetd = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        nkjj__uqltt = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        lvll__dyta = {('NOT_NA', gfqde__oqetd(kheo__iqxm)): kheo__iqxm for
            kheo__iqxm in null_set}
        san__qhk, _, _ = _parse_query_expr(nkjj__uqltt, env, [], [], None,
            join_cleaned_cols=lvll__dyta)
        nqpvo__wuei = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            aheu__awlq = pd.core.computation.ops.BinOp('&', san__qhk, expr_node
                )
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = nqpvo__wuei
        return aheu__awlq

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                dpl__bnmsr = set()
                nfz__esdmr = set()
                yncgg__uxqos = _insert_NA_cond_body(expr_node.lhs, dpl__bnmsr)
                phcev__hqc = _insert_NA_cond_body(expr_node.rhs, nfz__esdmr)
                qjl__ksrch = dpl__bnmsr.intersection(nfz__esdmr)
                dpl__bnmsr.difference_update(qjl__ksrch)
                nfz__esdmr.difference_update(qjl__ksrch)
                null_set.update(qjl__ksrch)
                expr_node.lhs = append_null_checks(yncgg__uxqos, dpl__bnmsr)
                expr_node.rhs = append_null_checks(phcev__hqc, nfz__esdmr)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            qga__lhu = expr_node.name
            cmr__zqimn, col_name = qga__lhu.split('.')
            if cmr__zqimn == 'left':
                rda__rbd = left_columns
                data = left_data
            else:
                rda__rbd = right_columns
                data = right_data
            jwx__xgn = data[rda__rbd.index(col_name)]
            if bodo.utils.typing.is_nullable(jwx__xgn):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    vuojo__qmy = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        aodl__msmd = str(expr_node.lhs)
        pgn__you = str(expr_node.rhs)
        if aodl__msmd.startswith('left.') and pgn__you.startswith('left.'
            ) or aodl__msmd.startswith('right.') and pgn__you.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [aodl__msmd.split('.')[1]]
        right_on = [pgn__you.split('.')[1]]
        if aodl__msmd.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        cvylt__woid, moc__dvx, sgim__irl = _extract_equal_conds(expr_node.lhs)
        yqfs__waop, elbks__jtmx, ihvkm__axe = _extract_equal_conds(expr_node
            .rhs)
        left_on = cvylt__woid + yqfs__waop
        right_on = moc__dvx + elbks__jtmx
        if sgim__irl is None:
            return left_on, right_on, ihvkm__axe
        if ihvkm__axe is None:
            return left_on, right_on, sgim__irl
        expr_node.lhs = sgim__irl
        expr_node.rhs = ihvkm__axe
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    zfrx__qebq = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (zfrx__qebq,))
    scvxm__beos = dict()
    gfqde__oqetd = pd.core.computation.parsing.clean_column_name
    for name, rnq__nduze in (('left', left_columns), ('right', right_columns)):
        for kheo__iqxm in rnq__nduze:
            ldd__llkfj = gfqde__oqetd(kheo__iqxm)
            lom__wyn = name, ldd__llkfj
            if lom__wyn in scvxm__beos:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{kheo__iqxm}' and '{scvxm__beos[ldd__llkfj]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            scvxm__beos[lom__wyn] = kheo__iqxm
    elex__yge, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=scvxm__beos)
    left_on, right_on, jfjps__fxou = _extract_equal_conds(elex__yge.terms)
    return left_on, right_on, _insert_NA_cond(jfjps__fxou, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    alz__bgvkd = dict(sort=sort, copy=copy, validate=validate)
    psl__scy = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    poe__dij = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    sdsv__woje = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in poe__dij and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, ngjh__rdkuo = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if ngjh__rdkuo is None:
                    sdsv__woje = ''
                else:
                    sdsv__woje = str(ngjh__rdkuo)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = poe__dij
        right_keys = poe__dij
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
    qea__nlwi = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        mldq__kuhq = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        mldq__kuhq = list(get_overload_const_list(suffixes))
    suffix_x = mldq__kuhq[0]
    suffix_y = mldq__kuhq[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    seamk__yowxi = (
        "def _impl(left, right, how='inner', on=None, left_on=None,\n")
    seamk__yowxi += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    seamk__yowxi += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    seamk__yowxi += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, qea__nlwi, sdsv__woje))
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo}, fhzpo__mfnv)
    _impl = fhzpo__mfnv['_impl']
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
    suyf__okarj = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    uer__iba = {get_overload_const_str(akwpe__belu) for akwpe__belu in (
        left_on, right_on, on) if is_overload_constant_str(akwpe__belu)}
    for df in (left, right):
        for i, kheo__iqxm in enumerate(df.data):
            if not isinstance(kheo__iqxm, valid_dataframe_column_types
                ) and kheo__iqxm not in suyf__okarj:
                raise BodoError(
                    f'{name_func}(): use of column with {type(kheo__iqxm)} in merge unsupported'
                    )
            if df.columns[i] in uer__iba and isinstance(kheo__iqxm,
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
        mldq__kuhq = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        mldq__kuhq = list(get_overload_const_list(suffixes))
    if len(mldq__kuhq) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    poe__dij = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        skcgp__uvz = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            skcgp__uvz = on_str not in poe__dij and ('left.' in on_str or 
                'right.' in on_str)
        if len(poe__dij) == 0 and not skcgp__uvz:
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
    fjq__bsxw = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            vmx__ynvj = left.index
            wlgio__pvh = isinstance(vmx__ynvj, StringIndexType)
            qyc__gvg = right.index
            tytlk__pbt = isinstance(qyc__gvg, StringIndexType)
        elif is_overload_true(left_index):
            vmx__ynvj = left.index
            wlgio__pvh = isinstance(vmx__ynvj, StringIndexType)
            qyc__gvg = right.data[right.columns.index(right_keys[0])]
            tytlk__pbt = qyc__gvg.dtype == string_type
        elif is_overload_true(right_index):
            vmx__ynvj = left.data[left.columns.index(left_keys[0])]
            wlgio__pvh = vmx__ynvj.dtype == string_type
            qyc__gvg = right.index
            tytlk__pbt = isinstance(qyc__gvg, StringIndexType)
        if wlgio__pvh and tytlk__pbt:
            return
        vmx__ynvj = vmx__ynvj.dtype
        qyc__gvg = qyc__gvg.dtype
        try:
            kiv__aarxa = fjq__bsxw.resolve_function_type(operator.eq, (
                vmx__ynvj, qyc__gvg), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=vmx__ynvj, rk_dtype=qyc__gvg))
    else:
        for icdmf__fudn, ltfn__ofap in zip(left_keys, right_keys):
            vmx__ynvj = left.data[left.columns.index(icdmf__fudn)].dtype
            jkec__zxw = left.data[left.columns.index(icdmf__fudn)]
            qyc__gvg = right.data[right.columns.index(ltfn__ofap)].dtype
            hzk__mpdig = right.data[right.columns.index(ltfn__ofap)]
            if jkec__zxw == hzk__mpdig:
                continue
            nci__bzlvh = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=icdmf__fudn, lk_dtype=vmx__ynvj, rk=ltfn__ofap,
                rk_dtype=qyc__gvg))
            guva__tgow = vmx__ynvj == string_type
            wkd__mdwk = qyc__gvg == string_type
            if guva__tgow ^ wkd__mdwk:
                raise_bodo_error(nci__bzlvh)
            try:
                kiv__aarxa = fjq__bsxw.resolve_function_type(operator.eq, (
                    vmx__ynvj, qyc__gvg), {})
            except:
                raise_bodo_error(nci__bzlvh)


def validate_keys(keys, df):
    yxqp__myjy = set(keys).difference(set(df.columns))
    if len(yxqp__myjy) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in yxqp__myjy:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {yxqp__myjy} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    alz__bgvkd = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    psl__scy = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', alz__bgvkd, psl__scy,
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
    seamk__yowxi = "def _impl(left, other, on=None, how='left',\n"
    seamk__yowxi += "    lsuffix='', rsuffix='', sort=False):\n"
    seamk__yowxi += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo}, fhzpo__mfnv)
    _impl = fhzpo__mfnv['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        kii__wugin = get_overload_const_list(on)
        validate_keys(kii__wugin, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    poe__dij = tuple(set(left.columns) & set(other.columns))
    if len(poe__dij) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=poe__dij))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    jvj__grd = set(left_keys) & set(right_keys)
    aimb__oyq = set(left_columns) & set(right_columns)
    qbr__bge = aimb__oyq - jvj__grd
    jbzt__pfgl = set(left_columns) - aimb__oyq
    uiac__rblk = set(right_columns) - aimb__oyq
    mai__dsy = {}

    def insertOutColumn(col_name):
        if col_name in mai__dsy:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        mai__dsy[col_name] = 0
    for mih__boxn in jvj__grd:
        insertOutColumn(mih__boxn)
    for mih__boxn in qbr__bge:
        piryk__ncy = str(mih__boxn) + suffix_x
        rlp__eqii = str(mih__boxn) + suffix_y
        insertOutColumn(piryk__ncy)
        insertOutColumn(rlp__eqii)
    for mih__boxn in jbzt__pfgl:
        insertOutColumn(mih__boxn)
    for mih__boxn in uiac__rblk:
        insertOutColumn(mih__boxn)
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
    poe__dij = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = poe__dij
        right_keys = poe__dij
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
        mldq__kuhq = suffixes
    if is_overload_constant_list(suffixes):
        mldq__kuhq = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        mldq__kuhq = suffixes.value
    suffix_x = mldq__kuhq[0]
    suffix_y = mldq__kuhq[1]
    seamk__yowxi = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    seamk__yowxi += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    seamk__yowxi += (
        "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n")
    seamk__yowxi += "    allow_exact_matches=True, direction='backward'):\n"
    seamk__yowxi += '  suffix_x = suffixes[0]\n'
    seamk__yowxi += '  suffix_y = suffixes[1]\n'
    seamk__yowxi += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo}, fhzpo__mfnv)
    _impl = fhzpo__mfnv['_impl']
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
    alz__bgvkd = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    cunqp__oehao = dict(sort=False, group_keys=True, squeeze=False,
        observed=True)
    check_unsupported_args('Dataframe.groupby', alz__bgvkd, cunqp__oehao,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    hbr__zqlg = func_name == 'DataFrame.pivot_table'
    if hbr__zqlg:
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
    doijt__vkwdr = get_literal_value(columns)
    if isinstance(doijt__vkwdr, (list, tuple)):
        if len(doijt__vkwdr) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {doijt__vkwdr}"
                )
        doijt__vkwdr = doijt__vkwdr[0]
    if doijt__vkwdr not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {doijt__vkwdr} not found in DataFrame {df}."
            )
    tiie__irp = df.column_index[doijt__vkwdr]
    if is_overload_none(index):
        kbjf__rahfi = []
        whpkt__ugw = []
    else:
        whpkt__ugw = get_literal_value(index)
        if not isinstance(whpkt__ugw, (list, tuple)):
            whpkt__ugw = [whpkt__ugw]
        kbjf__rahfi = []
        for index in whpkt__ugw:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            kbjf__rahfi.append(df.column_index[index])
    if not (all(isinstance(mco__qfdp, int) for mco__qfdp in whpkt__ugw) or
        all(isinstance(mco__qfdp, str) for mco__qfdp in whpkt__ugw)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        jdryx__zixvf = []
        pqypi__zgjq = []
        qwbs__eklb = kbjf__rahfi + [tiie__irp]
        for i, mco__qfdp in enumerate(df.columns):
            if i not in qwbs__eklb:
                jdryx__zixvf.append(i)
                pqypi__zgjq.append(mco__qfdp)
    else:
        pqypi__zgjq = get_literal_value(values)
        if not isinstance(pqypi__zgjq, (list, tuple)):
            pqypi__zgjq = [pqypi__zgjq]
        jdryx__zixvf = []
        for val in pqypi__zgjq:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            jdryx__zixvf.append(df.column_index[val])
    fmash__uxq = set(jdryx__zixvf) | set(kbjf__rahfi) | {tiie__irp}
    if len(fmash__uxq) != len(jdryx__zixvf) + len(kbjf__rahfi) + 1:
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
    if len(kbjf__rahfi) == 0:
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
        for odycu__xsnw in kbjf__rahfi:
            index_column = df.data[odycu__xsnw]
            check_valid_index_typ(index_column)
    eqcmh__fcinp = df.data[tiie__irp]
    if isinstance(eqcmh__fcinp, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(eqcmh__fcinp, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for jef__easq in jdryx__zixvf:
        tzghf__mvrpm = df.data[jef__easq]
        if isinstance(tzghf__mvrpm, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or tzghf__mvrpm == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (whpkt__ugw, doijt__vkwdr, pqypi__zgjq, kbjf__rahfi, tiie__irp,
        jdryx__zixvf)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (whpkt__ugw, doijt__vkwdr, pqypi__zgjq, odycu__xsnw, tiie__irp, zvn__lto
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot'))
    if len(whpkt__ugw) == 0:
        if is_overload_none(data.index.name_typ):
            spt__mrzq = None,
        else:
            spt__mrzq = get_literal_value(data.index.name_typ),
    else:
        spt__mrzq = tuple(whpkt__ugw)
    whpkt__ugw = ColNamesMetaType(spt__mrzq)
    pqypi__zgjq = ColNamesMetaType(tuple(pqypi__zgjq))
    doijt__vkwdr = ColNamesMetaType((doijt__vkwdr,))
    seamk__yowxi = 'def impl(data, index=None, columns=None, values=None):\n'
    seamk__yowxi += f'    pivot_values = data.iloc[:, {tiie__irp}].unique()\n'
    seamk__yowxi += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(odycu__xsnw) == 0:
        seamk__yowxi += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        seamk__yowxi += '        (\n'
        for eazh__epy in odycu__xsnw:
            seamk__yowxi += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {eazh__epy}),
"""
        seamk__yowxi += '        ),\n'
    seamk__yowxi += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {tiie__irp}),),
"""
    seamk__yowxi += '        (\n'
    for jef__easq in zvn__lto:
        seamk__yowxi += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {jef__easq}),
"""
    seamk__yowxi += '        ),\n'
    seamk__yowxi += '        pivot_values,\n'
    seamk__yowxi += '        index_lit,\n'
    seamk__yowxi += '        columns_lit,\n'
    seamk__yowxi += '        values_lit,\n'
    seamk__yowxi += '    )\n'
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo, 'index_lit': whpkt__ugw,
        'columns_lit': doijt__vkwdr, 'values_lit': pqypi__zgjq}, fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
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
    alz__bgvkd = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    psl__scy = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (whpkt__ugw, doijt__vkwdr, pqypi__zgjq, odycu__xsnw, tiie__irp, zvn__lto
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    eqda__dgfxp = whpkt__ugw
    whpkt__ugw = ColNamesMetaType(tuple(whpkt__ugw))
    pqypi__zgjq = ColNamesMetaType(tuple(pqypi__zgjq))
    zkdl__hegw = doijt__vkwdr
    doijt__vkwdr = ColNamesMetaType((doijt__vkwdr,))
    seamk__yowxi = 'def impl(\n'
    seamk__yowxi += '    data,\n'
    seamk__yowxi += '    values=None,\n'
    seamk__yowxi += '    index=None,\n'
    seamk__yowxi += '    columns=None,\n'
    seamk__yowxi += '    aggfunc="mean",\n'
    seamk__yowxi += '    fill_value=None,\n'
    seamk__yowxi += '    margins=False,\n'
    seamk__yowxi += '    dropna=True,\n'
    seamk__yowxi += '    margins_name="All",\n'
    seamk__yowxi += '    observed=False,\n'
    seamk__yowxi += '    sort=True,\n'
    seamk__yowxi += '    _pivot_values=None,\n'
    seamk__yowxi += '):\n'
    cuxmi__fjgup = odycu__xsnw + [tiie__irp] + zvn__lto
    seamk__yowxi += f'    data = data.iloc[:, {cuxmi__fjgup}]\n'
    dhzfx__dix = eqda__dgfxp + [zkdl__hegw]
    if not is_overload_none(_pivot_values):
        jrif__unkx = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(jrif__unkx)
        seamk__yowxi += '    pivot_values = _pivot_values_arr\n'
        seamk__yowxi += (
            f'    data = data[data.iloc[:, {len(odycu__xsnw)}].isin(pivot_values)]\n'
            )
        if all(isinstance(mco__qfdp, str) for mco__qfdp in jrif__unkx):
            idl__hfs = pd.array(jrif__unkx, 'string')
        elif all(isinstance(mco__qfdp, int) for mco__qfdp in jrif__unkx):
            idl__hfs = np.array(jrif__unkx, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        idl__hfs = None
    seamk__yowxi += (
        f'    data = data.groupby({dhzfx__dix!r}, as_index=False).agg(aggfunc)\n'
        )
    if is_overload_none(_pivot_values):
        seamk__yowxi += (
            f'    pivot_values = data.iloc[:, {len(odycu__xsnw)}].unique()\n')
    seamk__yowxi += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    seamk__yowxi += '        (\n'
    for i in range(0, len(odycu__xsnw)):
        seamk__yowxi += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
    seamk__yowxi += '        ),\n'
    seamk__yowxi += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(odycu__xsnw)}),),
"""
    seamk__yowxi += '        (\n'
    for i in range(len(odycu__xsnw) + 1, len(zvn__lto) + len(odycu__xsnw) + 1):
        seamk__yowxi += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
    seamk__yowxi += '        ),\n'
    seamk__yowxi += '        pivot_values,\n'
    seamk__yowxi += '        index_lit,\n'
    seamk__yowxi += '        columns_lit,\n'
    seamk__yowxi += '        values_lit,\n'
    seamk__yowxi += '        check_duplicates=False,\n'
    seamk__yowxi += '        _constant_pivot_values=_constant_pivot_values,\n'
    seamk__yowxi += '    )\n'
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo, 'numba': numba, 'index_lit':
        whpkt__ugw, 'columns_lit': doijt__vkwdr, 'values_lit': pqypi__zgjq,
        '_pivot_values_arr': idl__hfs, '_constant_pivot_values':
        _pivot_values}, fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    alz__bgvkd = dict(col_level=col_level, ignore_index=ignore_index)
    psl__scy = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', alz__bgvkd, psl__scy,
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
    rcy__bxzq = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(rcy__bxzq, (list, tuple)):
        rcy__bxzq = [rcy__bxzq]
    for mco__qfdp in rcy__bxzq:
        if mco__qfdp not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {mco__qfdp} not found in {frame}."
                )
    xryqm__bgzq = [frame.column_index[i] for i in rcy__bxzq]
    if is_overload_none(value_vars):
        kad__biva = []
        smwt__rqf = []
        for i, mco__qfdp in enumerate(frame.columns):
            if i not in xryqm__bgzq:
                kad__biva.append(i)
                smwt__rqf.append(mco__qfdp)
    else:
        smwt__rqf = get_literal_value(value_vars)
        if not isinstance(smwt__rqf, (list, tuple)):
            smwt__rqf = [smwt__rqf]
        smwt__rqf = [v for v in smwt__rqf if v not in rcy__bxzq]
        if not smwt__rqf:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        kad__biva = []
        for val in smwt__rqf:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            kad__biva.append(frame.column_index[val])
    for mco__qfdp in smwt__rqf:
        if mco__qfdp not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {mco__qfdp} not found in {frame}."
                )
    if not (all(isinstance(mco__qfdp, int) for mco__qfdp in smwt__rqf) or
        all(isinstance(mco__qfdp, str) for mco__qfdp in smwt__rqf)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    tsq__thi = frame.data[kad__biva[0]]
    ani__pujcj = [frame.data[i].dtype for i in kad__biva]
    kad__biva = np.array(kad__biva, dtype=np.int64)
    xryqm__bgzq = np.array(xryqm__bgzq, dtype=np.int64)
    _, dagl__ywqu = bodo.utils.typing.get_common_scalar_dtype(ani__pujcj)
    if not dagl__ywqu:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': smwt__rqf, 'val_type': tsq__thi}
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
    if frame.is_table_format and all(v == tsq__thi.dtype for v in ani__pujcj):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            kad__biva))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(smwt__rqf) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {kad__biva[0]})
"""
    else:
        tza__hnca = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in kad__biva)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({tza__hnca},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in xryqm__bgzq:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(smwt__rqf)})\n'
            )
    ubz__hbc = ', '.join(f'out_id{i}' for i in xryqm__bgzq) + (', ' if len(
        xryqm__bgzq) > 0 else '')
    data_args = ubz__hbc + 'var_col, val_col'
    columns = tuple(rcy__bxzq + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(smwt__rqf)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    alz__bgvkd = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    psl__scy = dict(values=None, rownames=None, colnames=None, aggfunc=None,
        margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', alz__bgvkd, psl__scy,
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
    alz__bgvkd = dict(ignore_index=ignore_index, key=key)
    psl__scy = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
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
    rtvs__ybjnh = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        rtvs__ybjnh.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        hikff__nulnc = [get_overload_const_tuple(by)]
    else:
        hikff__nulnc = get_overload_const_list(by)
    hikff__nulnc = set((k, '') if (k, '') in rtvs__ybjnh else k for k in
        hikff__nulnc)
    if len(hikff__nulnc.difference(rtvs__ybjnh)) > 0:
        wdasf__urbev = list(set(get_overload_const_list(by)).difference(
            rtvs__ybjnh))
        raise_bodo_error(f'sort_values(): invalid keys {wdasf__urbev} for by.')
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
        rsajq__puqlq = get_overload_const_list(na_position)
        for na_position in rsajq__puqlq:
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
    alz__bgvkd = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    psl__scy = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', alz__bgvkd, psl__scy,
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
    seamk__yowxi = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    nau__kbf = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(nau__kbf))
    for i in range(nau__kbf):
        seamk__yowxi += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(seamk__yowxi, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    alz__bgvkd = dict(limit=limit, downcast=downcast)
    psl__scy = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    tpr__vxr = not is_overload_none(value)
    ranlh__yfgj = not is_overload_none(method)
    if tpr__vxr and ranlh__yfgj:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not tpr__vxr and not ranlh__yfgj:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if tpr__vxr:
        sqnte__owmy = 'value=value'
    else:
        sqnte__owmy = 'method=method'
    data_args = [(
        f"df['{mco__qfdp}'].fillna({sqnte__owmy}, inplace=inplace)" if
        isinstance(mco__qfdp, str) else
        f'df[{mco__qfdp}].fillna({sqnte__owmy}, inplace=inplace)') for
        mco__qfdp in df.columns]
    seamk__yowxi = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        seamk__yowxi += '  ' + '  \n'.join(data_args) + '\n'
        fhzpo__mfnv = {}
        exec(seamk__yowxi, {}, fhzpo__mfnv)
        impl = fhzpo__mfnv['impl']
        return impl
    else:
        return _gen_init_df(seamk__yowxi, df.columns, ', '.join(nzz__dyoc +
            '.values' for nzz__dyoc in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    alz__bgvkd = dict(col_level=col_level, col_fill=col_fill)
    psl__scy = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', alz__bgvkd, psl__scy,
        package_name='pandas', module_name='DataFrame')
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
    seamk__yowxi = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    seamk__yowxi += (
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
        sohqq__hsq = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            sohqq__hsq)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            seamk__yowxi += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            egy__ybvau = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = egy__ybvau + data_args
        else:
            ehv__hxznp = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [ehv__hxznp] + data_args
    return _gen_init_df(seamk__yowxi, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    ecb__anmj = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and ecb__anmj == 1 or is_overload_constant_list(level) and list(
        get_overload_const_list(level)) == list(range(ecb__anmj))


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
        vuqt__zzvp = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        cvn__izpjg = get_overload_const_list(subset)
        vuqt__zzvp = []
        for eczm__ggmj in cvn__izpjg:
            if eczm__ggmj not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{eczm__ggmj}' not in data frame columns {df}"
                    )
            vuqt__zzvp.append(df.column_index[eczm__ggmj])
    nau__kbf = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(nau__kbf))
    seamk__yowxi = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(nau__kbf):
        seamk__yowxi += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    seamk__yowxi += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in vuqt__zzvp)))
    seamk__yowxi += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(seamk__yowxi, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    alz__bgvkd = dict(index=index, level=level, errors=errors)
    psl__scy = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', alz__bgvkd, psl__scy,
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
            rgosc__gnpb = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            rgosc__gnpb = get_overload_const_list(labels)
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
            rgosc__gnpb = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            rgosc__gnpb = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for mco__qfdp in rgosc__gnpb:
        if mco__qfdp not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(mco__qfdp, df.columns))
    if len(set(rgosc__gnpb)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    zjer__vdzu = tuple(mco__qfdp for mco__qfdp in df.columns if mco__qfdp
         not in rgosc__gnpb)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[mco__qfdp], '.copy()' if not inplace else ''
        ) for mco__qfdp in zjer__vdzu)
    seamk__yowxi = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    seamk__yowxi += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(seamk__yowxi, zjer__vdzu, data_args, index)


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
    alz__bgvkd = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    fienn__kuf = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', alz__bgvkd, fienn__kuf,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    nau__kbf = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(nau__kbf))
    znkib__kuwe = ', '.join('rhs_data_{}'.format(i) for i in range(nau__kbf))
    seamk__yowxi = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    seamk__yowxi += '  if (frac == 1 or n == len(df)) and not replace:\n'
    seamk__yowxi += (
        '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n')
    for i in range(nau__kbf):
        seamk__yowxi += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    seamk__yowxi += '  if frac is None:\n'
    seamk__yowxi += '    frac_d = -1.0\n'
    seamk__yowxi += '  else:\n'
    seamk__yowxi += '    frac_d = frac\n'
    seamk__yowxi += '  if n is None:\n'
    seamk__yowxi += '    n_i = 0\n'
    seamk__yowxi += '  else:\n'
    seamk__yowxi += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    seamk__yowxi += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({znkib__kuwe},), {index}, n_i, frac_d, replace)
"""
    seamk__yowxi += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(seamk__yowxi, df.
        columns, data_args, 'index')


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
    vedy__vptzn = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    fyc__puhj = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', vedy__vptzn, fyc__puhj,
        package_name='pandas', module_name='DataFrame')
    bvzy__nhb = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            lslpg__npwm = bvzy__nhb + '\n'
            lslpg__npwm += 'Index: 0 entries\n'
            lslpg__npwm += 'Empty DataFrame'
            print(lslpg__npwm)
        return _info_impl
    else:
        seamk__yowxi = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        seamk__yowxi += '    ncols = df.shape[1]\n'
        seamk__yowxi += f'    lines = "{bvzy__nhb}\\n"\n'
        seamk__yowxi += f'    lines += "{df.index}: "\n'
        seamk__yowxi += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            seamk__yowxi += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            seamk__yowxi += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            seamk__yowxi += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        seamk__yowxi += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        seamk__yowxi += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        seamk__yowxi += '    column_width = max(space, 7)\n'
        seamk__yowxi += '    column= "Column"\n'
        seamk__yowxi += '    underl= "------"\n'
        seamk__yowxi += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        seamk__yowxi += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        seamk__yowxi += '    mem_size = 0\n'
        seamk__yowxi += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        seamk__yowxi += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        seamk__yowxi += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        hia__iwxv = dict()
        for i in range(len(df.columns)):
            seamk__yowxi += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            fvac__xwg = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                fvac__xwg = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                extof__adtx = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                fvac__xwg = f'{extof__adtx[:-7]}'
            seamk__yowxi += f'    col_dtype[{i}] = "{fvac__xwg}"\n'
            if fvac__xwg in hia__iwxv:
                hia__iwxv[fvac__xwg] += 1
            else:
                hia__iwxv[fvac__xwg] = 1
            seamk__yowxi += f'    col_name[{i}] = "{df.columns[i]}"\n'
            seamk__yowxi += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        seamk__yowxi += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        seamk__yowxi += '    for i in column_info:\n'
        seamk__yowxi += "        lines += f'{i}\\n'\n"
        aeq__tho = ', '.join(f'{k}({hia__iwxv[k]})' for k in sorted(hia__iwxv))
        seamk__yowxi += f"    lines += 'dtypes: {aeq__tho}\\n'\n"
        seamk__yowxi += '    mem_size += df.index.nbytes\n'
        seamk__yowxi += '    total_size = _sizeof_fmt(mem_size)\n'
        seamk__yowxi += "    lines += f'memory usage: {total_size}'\n"
        seamk__yowxi += '    print(lines)\n'
        fhzpo__mfnv = {}
        exec(seamk__yowxi, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, fhzpo__mfnv)
        _info_impl = fhzpo__mfnv['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    seamk__yowxi = 'def impl(df, index=True, deep=False):\n'
    ajlw__hadhf = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes')
    wcl__nelqt = is_overload_true(index)
    columns = df.columns
    if wcl__nelqt:
        columns = ('Index',) + columns
    if len(columns) == 0:
        awa__pko = ()
    elif all(isinstance(mco__qfdp, int) for mco__qfdp in columns):
        awa__pko = np.array(columns, 'int64')
    elif all(isinstance(mco__qfdp, str) for mco__qfdp in columns):
        awa__pko = pd.array(columns, 'string')
    else:
        awa__pko = columns
    if df.is_table_format and len(df.columns) > 0:
        nrmwd__yvvq = int(wcl__nelqt)
        wbdb__pda = len(columns)
        seamk__yowxi += f'  nbytes_arr = np.empty({wbdb__pda}, np.int64)\n'
        seamk__yowxi += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        seamk__yowxi += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {nrmwd__yvvq})
"""
        if wcl__nelqt:
            seamk__yowxi += f'  nbytes_arr[0] = {ajlw__hadhf}\n'
        seamk__yowxi += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if wcl__nelqt:
            data = f'{ajlw__hadhf},{data}'
        else:
            jzuj__rxo = ',' if len(columns) == 1 else ''
            data = f'{data}{jzuj__rxo}'
        seamk__yowxi += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        awa__pko}, fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
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
    cpox__zmgp = 'read_excel_df{}'.format(next_label())
    setattr(types, cpox__zmgp, df_type)
    nwlpc__brsmg = False
    if is_overload_constant_list(parse_dates):
        nwlpc__brsmg = get_overload_const_list(parse_dates)
    rgymc__gjug = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    seamk__yowxi = f"""
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
    with numba.objmode(df="{cpox__zmgp}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{rgymc__gjug}}},
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
            parse_dates={nwlpc__brsmg},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    fhzpo__mfnv = {}
    exec(seamk__yowxi, globals(), fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as wnw__pohln:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    seamk__yowxi = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    seamk__yowxi += (
        '    ylabel=None, title=None, legend=True, fontsize=None, \n')
    seamk__yowxi += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        seamk__yowxi += '   fig, ax = plt.subplots()\n'
    else:
        seamk__yowxi += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        seamk__yowxi += '   fig.set_figwidth(figsize[0])\n'
        seamk__yowxi += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        seamk__yowxi += '   xlabel = x\n'
    seamk__yowxi += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        seamk__yowxi += '   ylabel = y\n'
    else:
        seamk__yowxi += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        seamk__yowxi += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        seamk__yowxi += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    seamk__yowxi += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            seamk__yowxi += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            ojlqo__quefm = get_overload_const_str(x)
            okhvx__udt = df.columns.index(ojlqo__quefm)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if okhvx__udt != i:
                        seamk__yowxi += f"""   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])
"""
        else:
            seamk__yowxi += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        seamk__yowxi += '   ax.scatter(df[x], df[y], s=20)\n'
        seamk__yowxi += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        seamk__yowxi += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        seamk__yowxi += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        seamk__yowxi += '   ax.legend()\n'
    seamk__yowxi += '   return ax\n'
    fhzpo__mfnv = {}
    exec(seamk__yowxi, {'bodo': bodo, 'plt': plt}, fhzpo__mfnv)
    impl = fhzpo__mfnv['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for qbagg__foy in df_typ.data:
        if not (isinstance(qbagg__foy, IntegerArrayType) or isinstance(
            qbagg__foy.dtype, types.Number) or qbagg__foy.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns)):
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
        cjr__hsxfe = args[0]
        ilh__ydge = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        mbwp__kupcj = cjr__hsxfe
        check_runtime_cols_unsupported(cjr__hsxfe, 'set_df_col()')
        if isinstance(cjr__hsxfe, DataFrameType):
            index = cjr__hsxfe.index
            if len(cjr__hsxfe.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(cjr__hsxfe.columns) == 0:
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
            if ilh__ydge in cjr__hsxfe.columns:
                zjer__vdzu = cjr__hsxfe.columns
                zubtr__gdtcm = cjr__hsxfe.columns.index(ilh__ydge)
                hzp__fuk = list(cjr__hsxfe.data)
                hzp__fuk[zubtr__gdtcm] = val
                hzp__fuk = tuple(hzp__fuk)
            else:
                zjer__vdzu = cjr__hsxfe.columns + (ilh__ydge,)
                hzp__fuk = cjr__hsxfe.data + (val,)
            mbwp__kupcj = DataFrameType(hzp__fuk, index, zjer__vdzu,
                cjr__hsxfe.dist, cjr__hsxfe.is_table_format)
        return mbwp__kupcj(*args)


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
        kgrpb__dzf = args[0]
        assert isinstance(kgrpb__dzf, DataFrameType) and len(kgrpb__dzf.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        xfm__ctwpw = args[2]
        assert len(col_names_to_replace) == len(xfm__ctwpw
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(kgrpb__dzf.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in kgrpb__dzf.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(kgrpb__dzf,
            '__bodosql_replace_columns_dummy()')
        index = kgrpb__dzf.index
        zjer__vdzu = kgrpb__dzf.columns
        hzp__fuk = list(kgrpb__dzf.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            ghao__zguiu = xfm__ctwpw[i]
            assert isinstance(ghao__zguiu, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(ghao__zguiu, SeriesType):
                ghao__zguiu = ghao__zguiu.data
            etmfn__ibyhh = kgrpb__dzf.column_index[col_name]
            hzp__fuk[etmfn__ibyhh] = ghao__zguiu
        hzp__fuk = tuple(hzp__fuk)
        mbwp__kupcj = DataFrameType(hzp__fuk, index, zjer__vdzu, kgrpb__dzf
            .dist, kgrpb__dzf.is_table_format)
        return mbwp__kupcj(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    luy__ixm = {}

    def _rewrite_membership_op(self, node, left, right):
        bxv__jaowr = node.op
        op = self.visit(bxv__jaowr)
        return op, bxv__jaowr, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    eesd__ycnk = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in eesd__ycnk:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in eesd__ycnk:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        xniz__twp = node.attr
        value = node.value
        ddoz__jpxp = pd.core.computation.ops.LOCAL_TAG
        if xniz__twp in ('str', 'dt'):
            try:
                glbe__ttzbv = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as fem__mbh:
                col_name = fem__mbh.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            glbe__ttzbv = str(self.visit(value))
        lom__wyn = glbe__ttzbv, xniz__twp
        if lom__wyn in join_cleaned_cols:
            xniz__twp = join_cleaned_cols[lom__wyn]
        name = glbe__ttzbv + '.' + xniz__twp
        if name.startswith(ddoz__jpxp):
            name = name[len(ddoz__jpxp):]
        if xniz__twp in ('str', 'dt'):
            yjmiz__oyt = columns[cleaned_columns.index(glbe__ttzbv)]
            luy__ixm[yjmiz__oyt] = glbe__ttzbv
            self.env.scope[name] = 0
            return self.term_type(ddoz__jpxp + name, self.env)
        eesd__ycnk.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in eesd__ycnk:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        pxdhv__etwqf = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        ilh__ydge = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(pxdhv__etwqf), ilh__ydge))

    def op__str__(self):
        dzyk__tyva = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            zzhi__dvz)) for zzhi__dvz in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(dzyk__tyva)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(dzyk__tyva)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(dzyk__tyva))
    eqdr__gncd = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    qzox__cuvd = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    qzmd__wecu = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    qxqb__wvfr = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    pegzx__ilixe = pd.core.computation.ops.Term.__str__
    phb__oirw = pd.core.computation.ops.MathCall.__str__
    emwth__minm = pd.core.computation.ops.Op.__str__
    nqpvo__wuei = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        elex__yge = pd.core.computation.expr.Expr(expr, env=env)
        fkuwb__pdnre = str(elex__yge)
    except pd.core.computation.ops.UndefinedVariableError as fem__mbh:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == fem__mbh.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {fem__mbh}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            eqdr__gncd)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            qzox__cuvd)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = qzmd__wecu
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = qxqb__wvfr
        pd.core.computation.ops.Term.__str__ = pegzx__ilixe
        pd.core.computation.ops.MathCall.__str__ = phb__oirw
        pd.core.computation.ops.Op.__str__ = emwth__minm
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            nqpvo__wuei)
    jzavq__hbq = pd.core.computation.parsing.clean_column_name
    luy__ixm.update({mco__qfdp: jzavq__hbq(mco__qfdp) for mco__qfdp in
        columns if jzavq__hbq(mco__qfdp) in elex__yge.names})
    return elex__yge, fkuwb__pdnre, luy__ixm


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        dzwku__hghws = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(dzwku__hghws))
        sqw__rcm = namedtuple('Pandas', col_names)
        chay__wnasv = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], sqw__rcm)
        super(DataFrameTupleIterator, self).__init__(name, chay__wnasv)

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
        poqs__tugf = [if_series_to_array_type(a) for a in args[len(args) // 2:]
            ]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        poqs__tugf = [types.Array(types.int64, 1, 'C')] + poqs__tugf
        rpk__jgzv = DataFrameTupleIterator(col_names, poqs__tugf)
        return rpk__jgzv(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        syrr__gubo = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            syrr__gubo)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    ovgp__stew = args[len(args) // 2:]
    xxxt__ekff = sig.args[len(sig.args) // 2:]
    ydqtn__qfm = context.make_helper(builder, sig.return_type)
    ahrv__hqvt = context.get_constant(types.intp, 0)
    hmoq__lyy = cgutils.alloca_once_value(builder, ahrv__hqvt)
    ydqtn__qfm.index = hmoq__lyy
    for i, arr in enumerate(ovgp__stew):
        setattr(ydqtn__qfm, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(ovgp__stew, xxxt__ekff):
        context.nrt.incref(builder, arr_typ, arr)
    res = ydqtn__qfm._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    ghzv__hopw, = sig.args
    kumcb__hlqnc, = args
    ydqtn__qfm = context.make_helper(builder, ghzv__hopw, value=kumcb__hlqnc)
    orby__pbq = signature(types.intp, ghzv__hopw.array_types[1])
    efm__wqkxq = context.compile_internal(builder, lambda a: len(a),
        orby__pbq, [ydqtn__qfm.array0])
    index = builder.load(ydqtn__qfm.index)
    nglrs__bnolm = builder.icmp_signed('<', index, efm__wqkxq)
    result.set_valid(nglrs__bnolm)
    with builder.if_then(nglrs__bnolm):
        values = [index]
        for i, arr_typ in enumerate(ghzv__hopw.array_types[1:]):
            lixdh__dgtl = getattr(ydqtn__qfm, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                ctexp__yegwp = signature(pd_timestamp_type, arr_typ, types.intp
                    )
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    ctexp__yegwp, [lixdh__dgtl, index])
            else:
                ctexp__yegwp = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    ctexp__yegwp, [lixdh__dgtl, index])
            values.append(val)
        value = context.make_tuple(builder, ghzv__hopw.yield_type, values)
        result.yield_(value)
        pswf__ddjy = cgutils.increment_index(builder, index)
        builder.store(pswf__ddjy, ydqtn__qfm.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    wje__ggkdg = ir.Assign(rhs, lhs, expr.loc)
    kprd__illku = lhs
    nrzh__psp = []
    xpcag__kozgi = []
    uphlt__zbrjp = typ.count
    for i in range(uphlt__zbrjp):
        zaegw__lnfbm = ir.Var(kprd__illku.scope, mk_unique_var('{}_size{}'.
            format(kprd__illku.name, i)), kprd__illku.loc)
        nklf__gql = ir.Expr.static_getitem(lhs, i, None, kprd__illku.loc)
        self.calltypes[nklf__gql] = None
        nrzh__psp.append(ir.Assign(nklf__gql, zaegw__lnfbm, kprd__illku.loc))
        self._define(equiv_set, zaegw__lnfbm, types.intp, nklf__gql)
        xpcag__kozgi.append(zaegw__lnfbm)
    sts__nni = tuple(xpcag__kozgi)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        sts__nni, pre=[wje__ggkdg] + nrzh__psp)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
