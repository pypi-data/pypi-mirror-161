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
        pzpg__mfx = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({pzpg__mfx})\n')
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    ayue__bpb = 'def impl(df):\n'
    if df.has_runtime_cols:
        ayue__bpb += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        lnqy__ioudz = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        ayue__bpb += f'  return {lnqy__ioudz}'
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo}, yysg__sbuq)
    impl = yysg__sbuq['impl']
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
    zlosb__runli = len(df.columns)
    jaet__ganhe = set(i for i in range(zlosb__runli) if isinstance(df.data[
        i], IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in jaet__ganhe else '') for i in
        range(zlosb__runli))
    ayue__bpb = 'def f(df):\n'.format()
    ayue__bpb += '    return np.stack(({},), 1)\n'.format(data_args)
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo, 'np': np}, yysg__sbuq)
    kvm__wha = yysg__sbuq['f']
    return kvm__wha


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
    krrll__nuxmj = {'dtype': dtype, 'na_value': na_value}
    hoa__tefs = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', krrll__nuxmj, hoa__tefs,
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
            lyd__fpxtz = bodo.hiframes.table.compute_num_runtime_columns(t)
            return lyd__fpxtz * len(t)
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
            lyd__fpxtz = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), lyd__fpxtz
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    ayue__bpb = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    lnpx__yuk = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    ayue__bpb += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{lnpx__yuk}), {index}, None)
"""
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo}, yysg__sbuq)
    impl = yysg__sbuq['impl']
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
    krrll__nuxmj = {'copy': copy, 'errors': errors}
    hoa__tefs = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', krrll__nuxmj, hoa__tefs,
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
        omi__usg = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        nmtmc__yeeh = _bodo_object_typeref.instance_type
        assert isinstance(nmtmc__yeeh, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in nmtmc__yeeh.column_index:
                    idx = nmtmc__yeeh.column_index[name]
                    arr_typ = nmtmc__yeeh.data[idx]
                else:
                    arr_typ = df.data[i]
                omi__usg.append(arr_typ)
        else:
            extra_globals = {}
            hni__alp = {}
            for i, name in enumerate(nmtmc__yeeh.columns):
                arr_typ = nmtmc__yeeh.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    yjo__kugx = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    yjo__kugx = boolean_dtype
                else:
                    yjo__kugx = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = yjo__kugx
                hni__alp[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {hni__alp[mwqw__udkx]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if mwqw__udkx in hni__alp else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, mwqw__udkx in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        osqe__gjm = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            osqe__gjm = {name: dtype_to_array_type(parse_dtype(dtype)) for 
                name, dtype in osqe__gjm.items()}
            for i, name in enumerate(df.columns):
                if name in osqe__gjm:
                    arr_typ = osqe__gjm[name]
                else:
                    arr_typ = df.data[i]
                omi__usg.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(osqe__gjm[mwqw__udkx])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if mwqw__udkx in osqe__gjm else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, mwqw__udkx in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        omi__usg = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        qcw__tlzjm = bodo.TableType(tuple(omi__usg))
        extra_globals['out_table_typ'] = qcw__tlzjm
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
        txi__xamoi = types.none
        extra_globals = {'output_arr_typ': txi__xamoi}
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
        uybbr__fyhlv = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                uybbr__fyhlv.append(arr + '.copy()')
            elif is_overload_false(deep):
                uybbr__fyhlv.append(arr)
            else:
                uybbr__fyhlv.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(uybbr__fyhlv)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    krrll__nuxmj = {'index': index, 'level': level, 'errors': errors}
    hoa__tefs = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', krrll__nuxmj, hoa__tefs,
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
        tys__zcxg = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        tys__zcxg = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    knry__zug = tuple([tys__zcxg.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    mss__pov = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        mss__pov = df.copy(columns=knry__zug)
        txi__xamoi = types.none
        extra_globals = {'output_arr_typ': txi__xamoi}
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
        uybbr__fyhlv = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                uybbr__fyhlv.append(arr + '.copy()')
            elif is_overload_false(copy):
                uybbr__fyhlv.append(arr)
            else:
                uybbr__fyhlv.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(uybbr__fyhlv)
    return _gen_init_df(header, knry__zug, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    tnx__grs = not is_overload_none(items)
    ikvi__wmgrh = not is_overload_none(like)
    guqrh__ula = not is_overload_none(regex)
    qdua__chqk = tnx__grs ^ ikvi__wmgrh ^ guqrh__ula
    taeby__gpm = not (tnx__grs or ikvi__wmgrh or guqrh__ula)
    if taeby__gpm:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not qdua__chqk:
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
        kxzl__rxz = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        kxzl__rxz = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert kxzl__rxz in {0, 1}
    ayue__bpb = 'def impl(df, items=None, like=None, regex=None, axis=None):\n'
    if kxzl__rxz == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if kxzl__rxz == 1:
        fcvg__ugcw = []
        jom__ujwom = []
        ltcm__ehq = []
        if tnx__grs:
            if is_overload_constant_list(items):
                mjud__oawy = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if ikvi__wmgrh:
            if is_overload_constant_str(like):
                xkyz__zyjz = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if guqrh__ula:
            if is_overload_constant_str(regex):
                pxjjz__vjx = get_overload_const_str(regex)
                ovf__noo = re.compile(pxjjz__vjx)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, mwqw__udkx in enumerate(df.columns):
            if not is_overload_none(items
                ) and mwqw__udkx in mjud__oawy or not is_overload_none(like
                ) and xkyz__zyjz in str(mwqw__udkx) or not is_overload_none(
                regex) and ovf__noo.search(str(mwqw__udkx)):
                jom__ujwom.append(mwqw__udkx)
                ltcm__ehq.append(i)
        for i in ltcm__ehq:
            var_name = f'data_{i}'
            fcvg__ugcw.append(var_name)
            ayue__bpb += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(fcvg__ugcw)
        return _gen_init_df(ayue__bpb, jom__ujwom, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    mss__pov = None
    if df.is_table_format:
        txi__xamoi = types.Array(types.bool_, 1, 'C')
        mss__pov = DataFrameType(tuple([txi__xamoi] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': txi__xamoi}
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
    jpcjz__nzpiy = is_overload_none(include)
    wjth__qav = is_overload_none(exclude)
    ygdzb__dryhp = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if jpcjz__nzpiy and wjth__qav:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not jpcjz__nzpiy:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            kbbs__ywgi = [dtype_to_array_type(parse_dtype(elem,
                ygdzb__dryhp)) for elem in include]
        elif is_legal_input(include):
            kbbs__ywgi = [dtype_to_array_type(parse_dtype(include,
                ygdzb__dryhp))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        kbbs__ywgi = get_nullable_and_non_nullable_types(kbbs__ywgi)
        izb__djwv = tuple(mwqw__udkx for i, mwqw__udkx in enumerate(df.
            columns) if df.data[i] in kbbs__ywgi)
    else:
        izb__djwv = df.columns
    if not wjth__qav:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            ewour__xvbg = [dtype_to_array_type(parse_dtype(elem,
                ygdzb__dryhp)) for elem in exclude]
        elif is_legal_input(exclude):
            ewour__xvbg = [dtype_to_array_type(parse_dtype(exclude,
                ygdzb__dryhp))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        ewour__xvbg = get_nullable_and_non_nullable_types(ewour__xvbg)
        izb__djwv = tuple(mwqw__udkx for mwqw__udkx in izb__djwv if df.data
            [df.column_index[mwqw__udkx]] not in ewour__xvbg)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[mwqw__udkx]})'
         for mwqw__udkx in izb__djwv)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, izb__djwv, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    mss__pov = None
    if df.is_table_format:
        txi__xamoi = types.Array(types.bool_, 1, 'C')
        mss__pov = DataFrameType(tuple([txi__xamoi] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': txi__xamoi}
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
    wlb__vkn = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in wlb__vkn:
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
    wlb__vkn = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in wlb__vkn:
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
    ayue__bpb = 'def impl(df, values):\n'
    jyglj__qhmtl = {}
    lxs__blv = False
    if isinstance(values, DataFrameType):
        lxs__blv = True
        for i, mwqw__udkx in enumerate(df.columns):
            if mwqw__udkx in values.column_index:
                bqfsw__pbu = 'val{}'.format(i)
                ayue__bpb += f"""  {bqfsw__pbu} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[mwqw__udkx]})
"""
                jyglj__qhmtl[mwqw__udkx] = bqfsw__pbu
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        jyglj__qhmtl = {mwqw__udkx: 'values' for mwqw__udkx in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        bqfsw__pbu = 'data{}'.format(i)
        ayue__bpb += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(bqfsw__pbu, i))
        data.append(bqfsw__pbu)
    lki__jqt = ['out{}'.format(i) for i in range(len(df.columns))]
    sdngu__rejr = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    vfxom__pxae = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    kzo__uxejb = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, lfz__wwmx) in enumerate(zip(df.columns, data)):
        if cname in jyglj__qhmtl:
            ozw__uhiaf = jyglj__qhmtl[cname]
            if lxs__blv:
                ayue__bpb += sdngu__rejr.format(lfz__wwmx, ozw__uhiaf,
                    lki__jqt[i])
            else:
                ayue__bpb += vfxom__pxae.format(lfz__wwmx, ozw__uhiaf,
                    lki__jqt[i])
        else:
            ayue__bpb += kzo__uxejb.format(lki__jqt[i])
    return _gen_init_df(ayue__bpb, df.columns, ','.join(lki__jqt))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    zlosb__runli = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(zlosb__runli))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    gebg__bvir = [mwqw__udkx for mwqw__udkx, hrl__omjza in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(hrl__omjza.
        dtype)]
    assert len(gebg__bvir) != 0
    krfvt__jwbm = ''
    if not any(hrl__omjza == types.float64 for hrl__omjza in df.data):
        krfvt__jwbm = '.astype(np.float64)'
    upclm__jnpoj = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[mwqw__udkx], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[mwqw__udkx]], IntegerArrayType) or
        df.data[df.column_index[mwqw__udkx]] == boolean_array else '') for
        mwqw__udkx in gebg__bvir)
    zikv__qcp = 'np.stack(({},), 1){}'.format(upclm__jnpoj, krfvt__jwbm)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(gebg__bvir))
        )
    index = f'{generate_col_to_index_func_text(gebg__bvir)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(zikv__qcp)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, gebg__bvir, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    lqx__kdl = dict(ddof=ddof)
    uce__pzho = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    fncvk__wua = '1' if is_overload_none(min_periods) else 'min_periods'
    gebg__bvir = [mwqw__udkx for mwqw__udkx, hrl__omjza in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(hrl__omjza.
        dtype)]
    if len(gebg__bvir) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    krfvt__jwbm = ''
    if not any(hrl__omjza == types.float64 for hrl__omjza in df.data):
        krfvt__jwbm = '.astype(np.float64)'
    upclm__jnpoj = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[mwqw__udkx], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[mwqw__udkx]], IntegerArrayType) or
        df.data[df.column_index[mwqw__udkx]] == boolean_array else '') for
        mwqw__udkx in gebg__bvir)
    zikv__qcp = 'np.stack(({},), 1){}'.format(upclm__jnpoj, krfvt__jwbm)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(gebg__bvir))
        )
    index = f'pd.Index({gebg__bvir})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(zikv__qcp)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        fncvk__wua)
    return _gen_init_df(header, gebg__bvir, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    lqx__kdl = dict(axis=axis, level=level, numeric_only=numeric_only)
    uce__pzho = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    ayue__bpb = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    ayue__bpb += '  data = np.array([{}])\n'.format(data_args)
    lnqy__ioudz = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    ayue__bpb += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {lnqy__ioudz})\n'
        )
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo, 'np': np}, yysg__sbuq)
    impl = yysg__sbuq['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    lqx__kdl = dict(axis=axis)
    uce__pzho = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    ayue__bpb = 'def impl(df, axis=0, dropna=True):\n'
    ayue__bpb += '  data = np.asarray(({},))\n'.format(data_args)
    lnqy__ioudz = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    ayue__bpb += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {lnqy__ioudz})\n'
        )
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo, 'np': np}, yysg__sbuq)
    impl = yysg__sbuq['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    lqx__kdl = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    uce__pzho = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    lqx__kdl = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    uce__pzho = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    lqx__kdl = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    uce__pzho = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    lqx__kdl = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    uce__pzho = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    lqx__kdl = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    uce__pzho = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    lqx__kdl = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    uce__pzho = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    lqx__kdl = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    uce__pzho = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    lqx__kdl = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    uce__pzho = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    lqx__kdl = dict(numeric_only=numeric_only, interpolation=interpolation)
    uce__pzho = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    lqx__kdl = dict(axis=axis, skipna=skipna)
    uce__pzho = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for fnp__sga in df.data:
        if not (bodo.utils.utils.is_np_array_typ(fnp__sga) and (fnp__sga.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            fnp__sga.dtype, (types.Number, types.Boolean))) or isinstance(
            fnp__sga, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            fnp__sga in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {fnp__sga} not supported.'
                )
        if isinstance(fnp__sga, bodo.CategoricalArrayType
            ) and not fnp__sga.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    lqx__kdl = dict(axis=axis, skipna=skipna)
    uce__pzho = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for fnp__sga in df.data:
        if not (bodo.utils.utils.is_np_array_typ(fnp__sga) and (fnp__sga.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            fnp__sga.dtype, (types.Number, types.Boolean))) or isinstance(
            fnp__sga, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            fnp__sga in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {fnp__sga} not supported.'
                )
        if isinstance(fnp__sga, bodo.CategoricalArrayType
            ) and not fnp__sga.dtype.ordered:
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
        gebg__bvir = tuple(mwqw__udkx for mwqw__udkx, hrl__omjza in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (hrl__omjza.dtype))
        out_colnames = gebg__bvir
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            vujr__axxl = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[mwqw__udkx]].dtype) for mwqw__udkx in out_colnames
                ]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(vujr__axxl, []))
    except NotImplementedError as pka__apqnn:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    ajbo__omxzo = ''
    if func_name in ('sum', 'prod'):
        ajbo__omxzo = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    ayue__bpb = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, ajbo__omxzo))
    if func_name == 'quantile':
        ayue__bpb = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        ayue__bpb = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        ayue__bpb += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        ayue__bpb += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        yysg__sbuq)
    impl = yysg__sbuq['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    bne__tfg = ''
    if func_name in ('min', 'max'):
        bne__tfg = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        bne__tfg = ', dtype=np.float32'
    mny__gjq = f'bodo.libs.array_ops.array_op_{func_name}'
    jmvke__xxm = ''
    if func_name in ['sum', 'prod']:
        jmvke__xxm = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        jmvke__xxm = 'index'
    elif func_name == 'quantile':
        jmvke__xxm = 'q'
    elif func_name in ['std', 'var']:
        jmvke__xxm = 'True, ddof'
    elif func_name == 'median':
        jmvke__xxm = 'True'
    data_args = ', '.join(
        f'{mny__gjq}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[mwqw__udkx]}), {jmvke__xxm})'
         for mwqw__udkx in out_colnames)
    ayue__bpb = ''
    if func_name in ('idxmax', 'idxmin'):
        ayue__bpb += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        ayue__bpb += ('  data = bodo.utils.conversion.coerce_to_array(({},))\n'
            .format(data_args))
    else:
        ayue__bpb += '  data = np.asarray(({},){})\n'.format(data_args,
            bne__tfg)
    ayue__bpb += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return ayue__bpb


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    wff__hwib = [df_type.column_index[mwqw__udkx] for mwqw__udkx in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in wff__hwib)
    eydb__cju = '\n        '.join(f'row[{i}] = arr_{wff__hwib[i]}[i]' for i in
        range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    ion__pot = f'len(arr_{wff__hwib[0]})'
    lzg__scm = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum': 'np.nansum',
        'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in lzg__scm:
        nnju__stm = lzg__scm[func_name]
        qwplj__don = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        ayue__bpb = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {ion__pot}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{qwplj__don})
    for i in numba.parfors.parfor.internal_prange(n):
        {eydb__cju}
        A[i] = {nnju__stm}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return ayue__bpb
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    lqx__kdl = dict(fill_method=fill_method, limit=limit, freq=freq)
    uce__pzho = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', lqx__kdl, uce__pzho,
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
    lqx__kdl = dict(axis=axis, skipna=skipna)
    uce__pzho = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', lqx__kdl, uce__pzho,
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
    lqx__kdl = dict(skipna=skipna)
    uce__pzho = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', lqx__kdl, uce__pzho,
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
    lqx__kdl = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    uce__pzho = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    gebg__bvir = [mwqw__udkx for mwqw__udkx, hrl__omjza in zip(df.columns,
        df.data) if _is_describe_type(hrl__omjza)]
    if len(gebg__bvir) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    czs__szi = sum(df.data[df.column_index[mwqw__udkx]].dtype == bodo.
        datetime64ns for mwqw__udkx in gebg__bvir)

    def _get_describe(col_ind):
        ibc__rjcgb = df.data[col_ind].dtype == bodo.datetime64ns
        if czs__szi and czs__szi != len(gebg__bvir):
            if ibc__rjcgb:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for mwqw__udkx in gebg__bvir:
        col_ind = df.column_index[mwqw__udkx]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[mwqw__udkx]) for
        mwqw__udkx in gebg__bvir)
    imboz__zuggl = (
        "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']")
    if czs__szi == len(gebg__bvir):
        imboz__zuggl = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif czs__szi:
        imboz__zuggl = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({imboz__zuggl})'
    return _gen_init_df(header, gebg__bvir, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    lqx__kdl = dict(axis=axis, convert=convert, is_copy=is_copy)
    uce__pzho = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', lqx__kdl, uce__pzho,
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
    lqx__kdl = dict(freq=freq, axis=axis, fill_value=fill_value)
    uce__pzho = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for vor__aoalp in df.data:
        if not is_supported_shift_array_type(vor__aoalp):
            raise BodoError(
                f'Dataframe.shift() column input type {vor__aoalp.dtype} not supported yet.'
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
    lqx__kdl = dict(axis=axis)
    uce__pzho = dict(axis=0)
    check_unsupported_args('DataFrame.diff', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for vor__aoalp in df.data:
        if not (isinstance(vor__aoalp, types.Array) and (isinstance(
            vor__aoalp.dtype, types.Number) or vor__aoalp.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {vor__aoalp.dtype} not supported.'
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
    exu__tupfz = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(exu__tupfz)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        pmyjk__dxqlc = get_overload_const_list(column)
    else:
        pmyjk__dxqlc = [get_literal_value(column)]
    rbjo__mxxmx = [df.column_index[mwqw__udkx] for mwqw__udkx in pmyjk__dxqlc]
    for i in rbjo__mxxmx:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{rbjo__mxxmx[0]})\n'
        )
    for i in range(n):
        if i in rbjo__mxxmx:
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
    krrll__nuxmj = {'inplace': inplace, 'append': append,
        'verify_integrity': verify_integrity}
    hoa__tefs = {'inplace': False, 'append': False, 'verify_integrity': False}
    check_unsupported_args('DataFrame.set_index', krrll__nuxmj, hoa__tefs,
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
    columns = tuple(mwqw__udkx for mwqw__udkx in df.columns if mwqw__udkx !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    krrll__nuxmj = {'inplace': inplace}
    hoa__tefs = {'inplace': False}
    check_unsupported_args('query', krrll__nuxmj, hoa__tefs, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        ubw__efrvo = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[ubw__efrvo]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    krrll__nuxmj = {'subset': subset, 'keep': keep}
    hoa__tefs = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', krrll__nuxmj, hoa__tefs,
        package_name='pandas', module_name='DataFrame')
    zlosb__runli = len(df.columns)
    ayue__bpb = "def impl(df, subset=None, keep='first'):\n"
    for i in range(zlosb__runli):
        ayue__bpb += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    npjlw__jqfsa = ', '.join(f'data_{i}' for i in range(zlosb__runli))
    npjlw__jqfsa += ',' if zlosb__runli == 1 else ''
    ayue__bpb += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({npjlw__jqfsa}))\n'
        )
    ayue__bpb += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    ayue__bpb += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo}, yysg__sbuq)
    impl = yysg__sbuq['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    krrll__nuxmj = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    hoa__tefs = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    atr__rmpo = []
    if is_overload_constant_list(subset):
        atr__rmpo = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        atr__rmpo = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        atr__rmpo = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    zvmg__fle = []
    for col_name in atr__rmpo:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        zvmg__fle.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', krrll__nuxmj,
        hoa__tefs, package_name='pandas', module_name='DataFrame')
    orwhi__knw = []
    if zvmg__fle:
        for tytc__iqe in zvmg__fle:
            if isinstance(df.data[tytc__iqe], bodo.MapArrayType):
                orwhi__knw.append(df.columns[tytc__iqe])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                orwhi__knw.append(col_name)
    if orwhi__knw:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {orwhi__knw} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    zlosb__runli = len(df.columns)
    xdp__vci = ['data_{}'.format(i) for i in zvmg__fle]
    zgu__njnf = ['data_{}'.format(i) for i in range(zlosb__runli) if i not in
        zvmg__fle]
    if xdp__vci:
        rxm__abney = len(xdp__vci)
    else:
        rxm__abney = zlosb__runli
    mwvk__rrb = ', '.join(xdp__vci + zgu__njnf)
    data_args = ', '.join('data_{}'.format(i) for i in range(zlosb__runli))
    ayue__bpb = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(zlosb__runli):
        ayue__bpb += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    ayue__bpb += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(mwvk__rrb, index, rxm__abney))
    ayue__bpb += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(ayue__bpb, df.columns, data_args, 'index')


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
            kzpzo__azvh = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                kzpzo__azvh = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                kzpzo__azvh = lambda i: f'other[:,{i}]'
        zlosb__runli = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {kzpzo__azvh(i)})'
             for i in range(zlosb__runli))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        miwu__khcjr = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(
            miwu__khcjr)


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    lqx__kdl = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    uce__pzho = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', lqx__kdl, uce__pzho,
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
    zlosb__runli = len(df.columns)
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
        for i in range(zlosb__runli):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(zlosb__runli):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(zlosb__runli):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    uknz__fwvxs = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    ayue__bpb = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    yysg__sbuq = {}
    qzy__vep = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': uknz__fwvxs}
    qzy__vep.update(extra_globals)
    exec(ayue__bpb, qzy__vep, yysg__sbuq)
    impl = yysg__sbuq['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        qkbv__jcd = pd.Index(lhs.columns)
        ugh__sit = pd.Index(rhs.columns)
        vphp__lfgvm, dqap__yvv, hmnas__tib = qkbv__jcd.join(ugh__sit, how=
            'left' if is_inplace else 'outer', level=None, return_indexers=True
            )
        return tuple(vphp__lfgvm), dqap__yvv, hmnas__tib
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        exne__cwpe = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        ygqtk__lzeit = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, exne__cwpe)
        check_runtime_cols_unsupported(rhs, exne__cwpe)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                vphp__lfgvm, dqap__yvv, hmnas__tib = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {ega__jhp}) {exne__cwpe}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {yzq__kcilm})'
                     if ega__jhp != -1 and yzq__kcilm != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for ega__jhp, yzq__kcilm in zip(dqap__yvv, hmnas__tib))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, vphp__lfgvm, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            xaozi__szj = []
            amw__zuc = []
            if op in ygqtk__lzeit:
                for i, kzwrx__pdz in enumerate(lhs.data):
                    if is_common_scalar_dtype([kzwrx__pdz.dtype, rhs]):
                        xaozi__szj.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {exne__cwpe} rhs'
                            )
                    else:
                        iaxry__zhtlr = f'arr{i}'
                        amw__zuc.append(iaxry__zhtlr)
                        xaozi__szj.append(iaxry__zhtlr)
                data_args = ', '.join(xaozi__szj)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {exne__cwpe} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(amw__zuc) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {iaxry__zhtlr} = np.empty(n, dtype=np.bool_)\n' for
                    iaxry__zhtlr in amw__zuc)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(iaxry__zhtlr,
                    op == operator.ne) for iaxry__zhtlr in amw__zuc)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            xaozi__szj = []
            amw__zuc = []
            if op in ygqtk__lzeit:
                for i, kzwrx__pdz in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, kzwrx__pdz.dtype]):
                        xaozi__szj.append(
                            f'lhs {exne__cwpe} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        iaxry__zhtlr = f'arr{i}'
                        amw__zuc.append(iaxry__zhtlr)
                        xaozi__szj.append(iaxry__zhtlr)
                data_args = ', '.join(xaozi__szj)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, exne__cwpe) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(amw__zuc) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(iaxry__zhtlr) for iaxry__zhtlr in amw__zuc)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(iaxry__zhtlr,
                    op == operator.ne) for iaxry__zhtlr in amw__zuc)
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
        miwu__khcjr = create_binary_op_overload(op)
        overload(op)(miwu__khcjr)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        exne__cwpe = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, exne__cwpe)
        check_runtime_cols_unsupported(right, exne__cwpe)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                vphp__lfgvm, _, hmnas__tib = _get_binop_columns(left, right,
                    True)
                ayue__bpb = 'def impl(left, right):\n'
                for i, yzq__kcilm in enumerate(hmnas__tib):
                    if yzq__kcilm == -1:
                        ayue__bpb += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    ayue__bpb += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    ayue__bpb += f"""  df_arr{i} {exne__cwpe} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {yzq__kcilm})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    vphp__lfgvm)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(ayue__bpb, vphp__lfgvm, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            ayue__bpb = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                ayue__bpb += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                ayue__bpb += '  df_arr{0} {1} right\n'.format(i, exne__cwpe)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(ayue__bpb, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        miwu__khcjr = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(miwu__khcjr)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            exne__cwpe = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, exne__cwpe)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, exne__cwpe) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        miwu__khcjr = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(miwu__khcjr)


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
            lxlqi__puh = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                lxlqi__puh[i] = bodo.libs.array_kernels.isna(obj, i)
            return lxlqi__puh
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
            lxlqi__puh = np.empty(n, np.bool_)
            for i in range(n):
                lxlqi__puh[i] = pd.isna(obj[i])
            return lxlqi__puh
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
    krrll__nuxmj = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    hoa__tefs = {'inplace': False, 'limit': None, 'regex': False, 'method':
        'pad'}
    check_unsupported_args('replace', krrll__nuxmj, hoa__tefs, package_name
        ='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    ulifz__hnmm = str(expr_node)
    return ulifz__hnmm.startswith('left.') or ulifz__hnmm.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    ybzy__esl = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (ybzy__esl,))
    goumm__vawao = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        wvy__uap = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        kwe__eproj = {('NOT_NA', goumm__vawao(kzwrx__pdz)): kzwrx__pdz for
            kzwrx__pdz in null_set}
        jzd__pax, _, _ = _parse_query_expr(wvy__uap, env, [], [], None,
            join_cleaned_cols=kwe__eproj)
        qkbq__vmu = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            bel__kyg = pd.core.computation.ops.BinOp('&', jzd__pax, expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = qkbq__vmu
        return bel__kyg

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                ijrco__mfq = set()
                ekfwd__ncb = set()
                whnum__jlpr = _insert_NA_cond_body(expr_node.lhs, ijrco__mfq)
                paa__tiwuq = _insert_NA_cond_body(expr_node.rhs, ekfwd__ncb)
                mjyng__zhkkp = ijrco__mfq.intersection(ekfwd__ncb)
                ijrco__mfq.difference_update(mjyng__zhkkp)
                ekfwd__ncb.difference_update(mjyng__zhkkp)
                null_set.update(mjyng__zhkkp)
                expr_node.lhs = append_null_checks(whnum__jlpr, ijrco__mfq)
                expr_node.rhs = append_null_checks(paa__tiwuq, ekfwd__ncb)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            hmr__tju = expr_node.name
            xxbc__hdb, col_name = hmr__tju.split('.')
            if xxbc__hdb == 'left':
                dmwz__bxp = left_columns
                data = left_data
            else:
                dmwz__bxp = right_columns
                data = right_data
            rewe__ggxp = data[dmwz__bxp.index(col_name)]
            if bodo.utils.typing.is_nullable(rewe__ggxp):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    vez__zmtjp = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        oxc__ipiqq = str(expr_node.lhs)
        fyea__bdwzn = str(expr_node.rhs)
        if oxc__ipiqq.startswith('left.') and fyea__bdwzn.startswith('left.'
            ) or oxc__ipiqq.startswith('right.') and fyea__bdwzn.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [oxc__ipiqq.split('.')[1]]
        right_on = [fyea__bdwzn.split('.')[1]]
        if oxc__ipiqq.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        boer__ijnp, hrb__xpob, col__anpjj = _extract_equal_conds(expr_node.lhs)
        kqjf__ysza, iuag__swuw, dunck__veg = _extract_equal_conds(expr_node.rhs
            )
        left_on = boer__ijnp + kqjf__ysza
        right_on = hrb__xpob + iuag__swuw
        if col__anpjj is None:
            return left_on, right_on, dunck__veg
        if dunck__veg is None:
            return left_on, right_on, col__anpjj
        expr_node.lhs = col__anpjj
        expr_node.rhs = dunck__veg
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    ybzy__esl = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (ybzy__esl,))
    tys__zcxg = dict()
    goumm__vawao = pd.core.computation.parsing.clean_column_name
    for name, vxpfr__pbo in (('left', left_columns), ('right', right_columns)):
        for kzwrx__pdz in vxpfr__pbo:
            vquwv__onxcn = goumm__vawao(kzwrx__pdz)
            awy__pmrg = name, vquwv__onxcn
            if awy__pmrg in tys__zcxg:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{kzwrx__pdz}' and '{tys__zcxg[vquwv__onxcn]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            tys__zcxg[awy__pmrg] = kzwrx__pdz
    nybhx__cywvc, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=tys__zcxg)
    left_on, right_on, sjffp__mkefp = _extract_equal_conds(nybhx__cywvc.terms)
    return left_on, right_on, _insert_NA_cond(sjffp__mkefp, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    lqx__kdl = dict(sort=sort, copy=copy, validate=validate)
    uce__pzho = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    tqy__gqr = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    ompg__xpc = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in tqy__gqr and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, tfzuq__uwlue = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if tfzuq__uwlue is None:
                    ompg__xpc = ''
                else:
                    ompg__xpc = str(tfzuq__uwlue)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = tqy__gqr
        right_keys = tqy__gqr
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
    oalt__yhhf = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        voo__yyvbq = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        voo__yyvbq = list(get_overload_const_list(suffixes))
    suffix_x = voo__yyvbq[0]
    suffix_y = voo__yyvbq[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    ayue__bpb = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    ayue__bpb += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    ayue__bpb += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    ayue__bpb += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, oalt__yhhf, ompg__xpc))
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo}, yysg__sbuq)
    _impl = yysg__sbuq['_impl']
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
    ioidn__lhrr = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    scqxk__kmfv = {get_overload_const_str(ibgko__xollz) for ibgko__xollz in
        (left_on, right_on, on) if is_overload_constant_str(ibgko__xollz)}
    for df in (left, right):
        for i, kzwrx__pdz in enumerate(df.data):
            if not isinstance(kzwrx__pdz, valid_dataframe_column_types
                ) and kzwrx__pdz not in ioidn__lhrr:
                raise BodoError(
                    f'{name_func}(): use of column with {type(kzwrx__pdz)} in merge unsupported'
                    )
            if df.columns[i] in scqxk__kmfv and isinstance(kzwrx__pdz,
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
        voo__yyvbq = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        voo__yyvbq = list(get_overload_const_list(suffixes))
    if len(voo__yyvbq) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    tqy__gqr = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        vueva__blr = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            vueva__blr = on_str not in tqy__gqr and ('left.' in on_str or 
                'right.' in on_str)
        if len(tqy__gqr) == 0 and not vueva__blr:
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
    tamui__yxc = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            elkw__qaeq = left.index
            gbdxr__mss = isinstance(elkw__qaeq, StringIndexType)
            cgkvb__axxie = right.index
            xed__zpe = isinstance(cgkvb__axxie, StringIndexType)
        elif is_overload_true(left_index):
            elkw__qaeq = left.index
            gbdxr__mss = isinstance(elkw__qaeq, StringIndexType)
            cgkvb__axxie = right.data[right.columns.index(right_keys[0])]
            xed__zpe = cgkvb__axxie.dtype == string_type
        elif is_overload_true(right_index):
            elkw__qaeq = left.data[left.columns.index(left_keys[0])]
            gbdxr__mss = elkw__qaeq.dtype == string_type
            cgkvb__axxie = right.index
            xed__zpe = isinstance(cgkvb__axxie, StringIndexType)
        if gbdxr__mss and xed__zpe:
            return
        elkw__qaeq = elkw__qaeq.dtype
        cgkvb__axxie = cgkvb__axxie.dtype
        try:
            jhr__owsly = tamui__yxc.resolve_function_type(operator.eq, (
                elkw__qaeq, cgkvb__axxie), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=elkw__qaeq, rk_dtype=cgkvb__axxie))
    else:
        for rey__dkzj, vmhow__tiwbz in zip(left_keys, right_keys):
            elkw__qaeq = left.data[left.columns.index(rey__dkzj)].dtype
            fvmdb__frh = left.data[left.columns.index(rey__dkzj)]
            cgkvb__axxie = right.data[right.columns.index(vmhow__tiwbz)].dtype
            zwhp__hhs = right.data[right.columns.index(vmhow__tiwbz)]
            if fvmdb__frh == zwhp__hhs:
                continue
            cwxd__kcud = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=rey__dkzj, lk_dtype=elkw__qaeq, rk=vmhow__tiwbz,
                rk_dtype=cgkvb__axxie))
            lnt__zhqbd = elkw__qaeq == string_type
            hycjv__aoy = cgkvb__axxie == string_type
            if lnt__zhqbd ^ hycjv__aoy:
                raise_bodo_error(cwxd__kcud)
            try:
                jhr__owsly = tamui__yxc.resolve_function_type(operator.eq,
                    (elkw__qaeq, cgkvb__axxie), {})
            except:
                raise_bodo_error(cwxd__kcud)


def validate_keys(keys, df):
    kyf__uim = set(keys).difference(set(df.columns))
    if len(kyf__uim) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in kyf__uim:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {kyf__uim} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    lqx__kdl = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    uce__pzho = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', lqx__kdl, uce__pzho,
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
    ayue__bpb = "def _impl(left, other, on=None, how='left',\n"
    ayue__bpb += "    lsuffix='', rsuffix='', sort=False):\n"
    ayue__bpb += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo}, yysg__sbuq)
    _impl = yysg__sbuq['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        oaw__ibveb = get_overload_const_list(on)
        validate_keys(oaw__ibveb, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    tqy__gqr = tuple(set(left.columns) & set(other.columns))
    if len(tqy__gqr) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=tqy__gqr))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    ykhir__ztn = set(left_keys) & set(right_keys)
    vvfsk__qzciy = set(left_columns) & set(right_columns)
    wxrsu__pzx = vvfsk__qzciy - ykhir__ztn
    xkq__wbmiy = set(left_columns) - vvfsk__qzciy
    adzr__fgo = set(right_columns) - vvfsk__qzciy
    vsn__kyf = {}

    def insertOutColumn(col_name):
        if col_name in vsn__kyf:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        vsn__kyf[col_name] = 0
    for bjuo__ums in ykhir__ztn:
        insertOutColumn(bjuo__ums)
    for bjuo__ums in wxrsu__pzx:
        zyk__lwtrb = str(bjuo__ums) + suffix_x
        mlby__eyz = str(bjuo__ums) + suffix_y
        insertOutColumn(zyk__lwtrb)
        insertOutColumn(mlby__eyz)
    for bjuo__ums in xkq__wbmiy:
        insertOutColumn(bjuo__ums)
    for bjuo__ums in adzr__fgo:
        insertOutColumn(bjuo__ums)
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
    tqy__gqr = tuple(sorted(set(left.columns) & set(right.columns), key=lambda
        k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = tqy__gqr
        right_keys = tqy__gqr
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
        voo__yyvbq = suffixes
    if is_overload_constant_list(suffixes):
        voo__yyvbq = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        voo__yyvbq = suffixes.value
    suffix_x = voo__yyvbq[0]
    suffix_y = voo__yyvbq[1]
    ayue__bpb = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    ayue__bpb += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    ayue__bpb += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    ayue__bpb += "    allow_exact_matches=True, direction='backward'):\n"
    ayue__bpb += '  suffix_x = suffixes[0]\n'
    ayue__bpb += '  suffix_y = suffixes[1]\n'
    ayue__bpb += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo}, yysg__sbuq)
    _impl = yysg__sbuq['_impl']
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
    lqx__kdl = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    iryh__hcm = dict(sort=False, group_keys=True, squeeze=False, observed=True)
    check_unsupported_args('Dataframe.groupby', lqx__kdl, iryh__hcm,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    okn__ijtq = func_name == 'DataFrame.pivot_table'
    if okn__ijtq:
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
    xhfo__newwk = get_literal_value(columns)
    if isinstance(xhfo__newwk, (list, tuple)):
        if len(xhfo__newwk) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {xhfo__newwk}"
                )
        xhfo__newwk = xhfo__newwk[0]
    if xhfo__newwk not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {xhfo__newwk} not found in DataFrame {df}."
            )
    ptjqs__tjxf = df.column_index[xhfo__newwk]
    if is_overload_none(index):
        rplq__dnaw = []
        xao__trd = []
    else:
        xao__trd = get_literal_value(index)
        if not isinstance(xao__trd, (list, tuple)):
            xao__trd = [xao__trd]
        rplq__dnaw = []
        for index in xao__trd:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            rplq__dnaw.append(df.column_index[index])
    if not (all(isinstance(mwqw__udkx, int) for mwqw__udkx in xao__trd) or
        all(isinstance(mwqw__udkx, str) for mwqw__udkx in xao__trd)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        bip__fazjv = []
        uwp__und = []
        cqkf__gdezz = rplq__dnaw + [ptjqs__tjxf]
        for i, mwqw__udkx in enumerate(df.columns):
            if i not in cqkf__gdezz:
                bip__fazjv.append(i)
                uwp__und.append(mwqw__udkx)
    else:
        uwp__und = get_literal_value(values)
        if not isinstance(uwp__und, (list, tuple)):
            uwp__und = [uwp__und]
        bip__fazjv = []
        for val in uwp__und:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            bip__fazjv.append(df.column_index[val])
    uzwz__dbhr = set(bip__fazjv) | set(rplq__dnaw) | {ptjqs__tjxf}
    if len(uzwz__dbhr) != len(bip__fazjv) + len(rplq__dnaw) + 1:
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
    if len(rplq__dnaw) == 0:
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
        for viqc__wcx in rplq__dnaw:
            index_column = df.data[viqc__wcx]
            check_valid_index_typ(index_column)
    fif__rem = df.data[ptjqs__tjxf]
    if isinstance(fif__rem, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(fif__rem, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for pbxnt__jks in bip__fazjv:
        joag__icebz = df.data[pbxnt__jks]
        if isinstance(joag__icebz, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or joag__icebz == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return xao__trd, xhfo__newwk, uwp__und, rplq__dnaw, ptjqs__tjxf, bip__fazjv


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (xao__trd, xhfo__newwk, uwp__und, viqc__wcx, ptjqs__tjxf, yukcq__etpgc) = (
        pivot_error_checking(data, index, columns, values, 'DataFrame.pivot'))
    if len(xao__trd) == 0:
        if is_overload_none(data.index.name_typ):
            wlsp__hoae = None,
        else:
            wlsp__hoae = get_literal_value(data.index.name_typ),
    else:
        wlsp__hoae = tuple(xao__trd)
    xao__trd = ColNamesMetaType(wlsp__hoae)
    uwp__und = ColNamesMetaType(tuple(uwp__und))
    xhfo__newwk = ColNamesMetaType((xhfo__newwk,))
    ayue__bpb = 'def impl(data, index=None, columns=None, values=None):\n'
    ayue__bpb += f'    pivot_values = data.iloc[:, {ptjqs__tjxf}].unique()\n'
    ayue__bpb += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(viqc__wcx) == 0:
        ayue__bpb += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        ayue__bpb += '        (\n'
        for lfx__ycvmb in viqc__wcx:
            ayue__bpb += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {lfx__ycvmb}),
"""
        ayue__bpb += '        ),\n'
    ayue__bpb += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {ptjqs__tjxf}),),
"""
    ayue__bpb += '        (\n'
    for pbxnt__jks in yukcq__etpgc:
        ayue__bpb += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {pbxnt__jks}),
"""
    ayue__bpb += '        ),\n'
    ayue__bpb += '        pivot_values,\n'
    ayue__bpb += '        index_lit,\n'
    ayue__bpb += '        columns_lit,\n'
    ayue__bpb += '        values_lit,\n'
    ayue__bpb += '    )\n'
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo, 'index_lit': xao__trd, 'columns_lit':
        xhfo__newwk, 'values_lit': uwp__und}, yysg__sbuq)
    impl = yysg__sbuq['impl']
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
    lqx__kdl = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    uce__pzho = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (xao__trd, xhfo__newwk, uwp__und, viqc__wcx, ptjqs__tjxf, yukcq__etpgc) = (
        pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    pnwqn__cra = xao__trd
    xao__trd = ColNamesMetaType(tuple(xao__trd))
    uwp__und = ColNamesMetaType(tuple(uwp__und))
    iwoem__aov = xhfo__newwk
    xhfo__newwk = ColNamesMetaType((xhfo__newwk,))
    ayue__bpb = 'def impl(\n'
    ayue__bpb += '    data,\n'
    ayue__bpb += '    values=None,\n'
    ayue__bpb += '    index=None,\n'
    ayue__bpb += '    columns=None,\n'
    ayue__bpb += '    aggfunc="mean",\n'
    ayue__bpb += '    fill_value=None,\n'
    ayue__bpb += '    margins=False,\n'
    ayue__bpb += '    dropna=True,\n'
    ayue__bpb += '    margins_name="All",\n'
    ayue__bpb += '    observed=False,\n'
    ayue__bpb += '    sort=True,\n'
    ayue__bpb += '    _pivot_values=None,\n'
    ayue__bpb += '):\n'
    auu__yorfu = viqc__wcx + [ptjqs__tjxf] + yukcq__etpgc
    ayue__bpb += f'    data = data.iloc[:, {auu__yorfu}]\n'
    odeq__ktceb = pnwqn__cra + [iwoem__aov]
    if not is_overload_none(_pivot_values):
        qfeaf__bog = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(qfeaf__bog)
        ayue__bpb += '    pivot_values = _pivot_values_arr\n'
        ayue__bpb += (
            f'    data = data[data.iloc[:, {len(viqc__wcx)}].isin(pivot_values)]\n'
            )
        if all(isinstance(mwqw__udkx, str) for mwqw__udkx in qfeaf__bog):
            ubewd__vpz = pd.array(qfeaf__bog, 'string')
        elif all(isinstance(mwqw__udkx, int) for mwqw__udkx in qfeaf__bog):
            ubewd__vpz = np.array(qfeaf__bog, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        ubewd__vpz = None
    ayue__bpb += (
        f'    data = data.groupby({odeq__ktceb!r}, as_index=False).agg(aggfunc)\n'
        )
    if is_overload_none(_pivot_values):
        ayue__bpb += (
            f'    pivot_values = data.iloc[:, {len(viqc__wcx)}].unique()\n')
    ayue__bpb += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    ayue__bpb += '        (\n'
    for i in range(0, len(viqc__wcx)):
        ayue__bpb += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    ayue__bpb += '        ),\n'
    ayue__bpb += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(viqc__wcx)}),),
"""
    ayue__bpb += '        (\n'
    for i in range(len(viqc__wcx) + 1, len(yukcq__etpgc) + len(viqc__wcx) + 1):
        ayue__bpb += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    ayue__bpb += '        ),\n'
    ayue__bpb += '        pivot_values,\n'
    ayue__bpb += '        index_lit,\n'
    ayue__bpb += '        columns_lit,\n'
    ayue__bpb += '        values_lit,\n'
    ayue__bpb += '        check_duplicates=False,\n'
    ayue__bpb += '        _constant_pivot_values=_constant_pivot_values,\n'
    ayue__bpb += '    )\n'
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo, 'numba': numba, 'index_lit': xao__trd,
        'columns_lit': xhfo__newwk, 'values_lit': uwp__und,
        '_pivot_values_arr': ubewd__vpz, '_constant_pivot_values':
        _pivot_values}, yysg__sbuq)
    impl = yysg__sbuq['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    lqx__kdl = dict(col_level=col_level, ignore_index=ignore_index)
    uce__pzho = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', lqx__kdl, uce__pzho,
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
    che__efy = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(che__efy, (list, tuple)):
        che__efy = [che__efy]
    for mwqw__udkx in che__efy:
        if mwqw__udkx not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {mwqw__udkx} not found in {frame}."
                )
    yvrh__upjtt = [frame.column_index[i] for i in che__efy]
    if is_overload_none(value_vars):
        qczpc__rpovq = []
        kfau__gqgu = []
        for i, mwqw__udkx in enumerate(frame.columns):
            if i not in yvrh__upjtt:
                qczpc__rpovq.append(i)
                kfau__gqgu.append(mwqw__udkx)
    else:
        kfau__gqgu = get_literal_value(value_vars)
        if not isinstance(kfau__gqgu, (list, tuple)):
            kfau__gqgu = [kfau__gqgu]
        kfau__gqgu = [v for v in kfau__gqgu if v not in che__efy]
        if not kfau__gqgu:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        qczpc__rpovq = []
        for val in kfau__gqgu:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            qczpc__rpovq.append(frame.column_index[val])
    for mwqw__udkx in kfau__gqgu:
        if mwqw__udkx not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {mwqw__udkx} not found in {frame}."
                )
    if not (all(isinstance(mwqw__udkx, int) for mwqw__udkx in kfau__gqgu) or
        all(isinstance(mwqw__udkx, str) for mwqw__udkx in kfau__gqgu)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    ijy__gkok = frame.data[qczpc__rpovq[0]]
    ltl__oaetq = [frame.data[i].dtype for i in qczpc__rpovq]
    qczpc__rpovq = np.array(qczpc__rpovq, dtype=np.int64)
    yvrh__upjtt = np.array(yvrh__upjtt, dtype=np.int64)
    _, mfzby__fvov = bodo.utils.typing.get_common_scalar_dtype(ltl__oaetq)
    if not mfzby__fvov:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': kfau__gqgu, 'val_type': ijy__gkok}
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
    if frame.is_table_format and all(v == ijy__gkok.dtype for v in ltl__oaetq):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            qczpc__rpovq))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(kfau__gqgu) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {qczpc__rpovq[0]})
"""
    else:
        fujo__gikfq = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in qczpc__rpovq)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({fujo__gikfq},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in yvrh__upjtt:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(kfau__gqgu)})\n'
            )
    igj__fko = ', '.join(f'out_id{i}' for i in yvrh__upjtt) + (', ' if len(
        yvrh__upjtt) > 0 else '')
    data_args = igj__fko + 'var_col, val_col'
    columns = tuple(che__efy + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(kfau__gqgu)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    lqx__kdl = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    uce__pzho = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', lqx__kdl, uce__pzho,
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
    lqx__kdl = dict(ignore_index=ignore_index, key=key)
    uce__pzho = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', lqx__kdl, uce__pzho,
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
    qnu__tojc = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        qnu__tojc.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        blbt__vqdu = [get_overload_const_tuple(by)]
    else:
        blbt__vqdu = get_overload_const_list(by)
    blbt__vqdu = set((k, '') if (k, '') in qnu__tojc else k for k in blbt__vqdu
        )
    if len(blbt__vqdu.difference(qnu__tojc)) > 0:
        pymb__ytfbq = list(set(get_overload_const_list(by)).difference(
            qnu__tojc))
        raise_bodo_error(f'sort_values(): invalid keys {pymb__ytfbq} for by.')
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
        owgrn__jyanb = get_overload_const_list(na_position)
        for na_position in owgrn__jyanb:
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
    lqx__kdl = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    uce__pzho = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', lqx__kdl, uce__pzho,
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
    ayue__bpb = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    zlosb__runli = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(zlosb__runli))
    for i in range(zlosb__runli):
        ayue__bpb += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(ayue__bpb, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    lqx__kdl = dict(limit=limit, downcast=downcast)
    uce__pzho = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', lqx__kdl, uce__pzho,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    qrjfo__wmkj = not is_overload_none(value)
    yoemq__alld = not is_overload_none(method)
    if qrjfo__wmkj and yoemq__alld:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not qrjfo__wmkj and not yoemq__alld:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if qrjfo__wmkj:
        uzeb__xea = 'value=value'
    else:
        uzeb__xea = 'method=method'
    data_args = [(
        f"df['{mwqw__udkx}'].fillna({uzeb__xea}, inplace=inplace)" if
        isinstance(mwqw__udkx, str) else
        f'df[{mwqw__udkx}].fillna({uzeb__xea}, inplace=inplace)') for
        mwqw__udkx in df.columns]
    ayue__bpb = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        ayue__bpb += '  ' + '  \n'.join(data_args) + '\n'
        yysg__sbuq = {}
        exec(ayue__bpb, {}, yysg__sbuq)
        impl = yysg__sbuq['impl']
        return impl
    else:
        return _gen_init_df(ayue__bpb, df.columns, ', '.join(hrl__omjza +
            '.values' for hrl__omjza in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    lqx__kdl = dict(col_level=col_level, col_fill=col_fill)
    uce__pzho = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', lqx__kdl, uce__pzho,
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
    ayue__bpb = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    ayue__bpb += (
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
        zbjvc__fsszq = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            zbjvc__fsszq)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            ayue__bpb += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            ewa__pnkbz = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = ewa__pnkbz + data_args
        else:
            qbbgi__uvugd = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [qbbgi__uvugd] + data_args
    return _gen_init_df(ayue__bpb, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    pkt__tgz = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and pkt__tgz == 1 or is_overload_constant_list(level) and list(
        get_overload_const_list(level)) == list(range(pkt__tgz))


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
        ogx__gkv = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        qiysm__xqujp = get_overload_const_list(subset)
        ogx__gkv = []
        for jfexi__jtvwg in qiysm__xqujp:
            if jfexi__jtvwg not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{jfexi__jtvwg}' not in data frame columns {df}"
                    )
            ogx__gkv.append(df.column_index[jfexi__jtvwg])
    zlosb__runli = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(zlosb__runli))
    ayue__bpb = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(zlosb__runli):
        ayue__bpb += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    ayue__bpb += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in ogx__gkv)))
    ayue__bpb += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(ayue__bpb, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    lqx__kdl = dict(index=index, level=level, errors=errors)
    uce__pzho = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', lqx__kdl, uce__pzho,
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
            rhx__nkp = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            rhx__nkp = get_overload_const_list(labels)
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
            rhx__nkp = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            rhx__nkp = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for mwqw__udkx in rhx__nkp:
        if mwqw__udkx not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(mwqw__udkx, df.columns))
    if len(set(rhx__nkp)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    knry__zug = tuple(mwqw__udkx for mwqw__udkx in df.columns if mwqw__udkx
         not in rhx__nkp)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[mwqw__udkx], '.copy()' if not inplace else
        '') for mwqw__udkx in knry__zug)
    ayue__bpb = 'def impl(df, labels=None, axis=0, index=None, columns=None,\n'
    ayue__bpb += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(ayue__bpb, knry__zug, data_args, index)


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
    lqx__kdl = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    cvki__sesmk = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', lqx__kdl, cvki__sesmk,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    zlosb__runli = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(zlosb__runli))
    djii__zopv = ', '.join('rhs_data_{}'.format(i) for i in range(zlosb__runli)
        )
    ayue__bpb = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    ayue__bpb += '  if (frac == 1 or n == len(df)) and not replace:\n'
    ayue__bpb += '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n'
    for i in range(zlosb__runli):
        ayue__bpb += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    ayue__bpb += '  if frac is None:\n'
    ayue__bpb += '    frac_d = -1.0\n'
    ayue__bpb += '  else:\n'
    ayue__bpb += '    frac_d = frac\n'
    ayue__bpb += '  if n is None:\n'
    ayue__bpb += '    n_i = 0\n'
    ayue__bpb += '  else:\n'
    ayue__bpb += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    ayue__bpb += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({djii__zopv},), {index}, n_i, frac_d, replace)
"""
    ayue__bpb += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(ayue__bpb, df.columns,
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
    krrll__nuxmj = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    hoa__tefs = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', krrll__nuxmj, hoa__tefs,
        package_name='pandas', module_name='DataFrame')
    fvtqq__wkp = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            zzjb__lua = fvtqq__wkp + '\n'
            zzjb__lua += 'Index: 0 entries\n'
            zzjb__lua += 'Empty DataFrame'
            print(zzjb__lua)
        return _info_impl
    else:
        ayue__bpb = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        ayue__bpb += '    ncols = df.shape[1]\n'
        ayue__bpb += f'    lines = "{fvtqq__wkp}\\n"\n'
        ayue__bpb += f'    lines += "{df.index}: "\n'
        ayue__bpb += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            ayue__bpb += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            ayue__bpb += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            ayue__bpb += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        ayue__bpb += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        ayue__bpb += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        ayue__bpb += '    column_width = max(space, 7)\n'
        ayue__bpb += '    column= "Column"\n'
        ayue__bpb += '    underl= "------"\n'
        ayue__bpb += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        ayue__bpb += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        ayue__bpb += '    mem_size = 0\n'
        ayue__bpb += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        ayue__bpb += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        ayue__bpb += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        fyjvv__vvf = dict()
        for i in range(len(df.columns)):
            ayue__bpb += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            tjfa__odmba = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                tjfa__odmba = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                mpqj__phvl = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                tjfa__odmba = f'{mpqj__phvl[:-7]}'
            ayue__bpb += f'    col_dtype[{i}] = "{tjfa__odmba}"\n'
            if tjfa__odmba in fyjvv__vvf:
                fyjvv__vvf[tjfa__odmba] += 1
            else:
                fyjvv__vvf[tjfa__odmba] = 1
            ayue__bpb += f'    col_name[{i}] = "{df.columns[i]}"\n'
            ayue__bpb += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        ayue__bpb += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        ayue__bpb += '    for i in column_info:\n'
        ayue__bpb += "        lines += f'{i}\\n'\n"
        lqb__lnlcn = ', '.join(f'{k}({fyjvv__vvf[k]})' for k in sorted(
            fyjvv__vvf))
        ayue__bpb += f"    lines += 'dtypes: {lqb__lnlcn}\\n'\n"
        ayue__bpb += '    mem_size += df.index.nbytes\n'
        ayue__bpb += '    total_size = _sizeof_fmt(mem_size)\n'
        ayue__bpb += "    lines += f'memory usage: {total_size}'\n"
        ayue__bpb += '    print(lines)\n'
        yysg__sbuq = {}
        exec(ayue__bpb, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo': bodo,
            'np': np}, yysg__sbuq)
        _info_impl = yysg__sbuq['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    ayue__bpb = 'def impl(df, index=True, deep=False):\n'
    kwv__eomjg = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes')
    ppiip__fnx = is_overload_true(index)
    columns = df.columns
    if ppiip__fnx:
        columns = ('Index',) + columns
    if len(columns) == 0:
        bjz__rch = ()
    elif all(isinstance(mwqw__udkx, int) for mwqw__udkx in columns):
        bjz__rch = np.array(columns, 'int64')
    elif all(isinstance(mwqw__udkx, str) for mwqw__udkx in columns):
        bjz__rch = pd.array(columns, 'string')
    else:
        bjz__rch = columns
    if df.is_table_format and len(df.columns) > 0:
        cokd__evbk = int(ppiip__fnx)
        lyd__fpxtz = len(columns)
        ayue__bpb += f'  nbytes_arr = np.empty({lyd__fpxtz}, np.int64)\n'
        ayue__bpb += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        ayue__bpb += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {cokd__evbk})
"""
        if ppiip__fnx:
            ayue__bpb += f'  nbytes_arr[0] = {kwv__eomjg}\n'
        ayue__bpb += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if ppiip__fnx:
            data = f'{kwv__eomjg},{data}'
        else:
            lnpx__yuk = ',' if len(columns) == 1 else ''
            data = f'{data}{lnpx__yuk}'
        ayue__bpb += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        bjz__rch}, yysg__sbuq)
    impl = yysg__sbuq['impl']
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
    bkmy__ckg = 'read_excel_df{}'.format(next_label())
    setattr(types, bkmy__ckg, df_type)
    jmlt__yct = False
    if is_overload_constant_list(parse_dates):
        jmlt__yct = get_overload_const_list(parse_dates)
    lvifv__gjv = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    ayue__bpb = f"""
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
    with numba.objmode(df="{bkmy__ckg}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{lvifv__gjv}}},
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
            parse_dates={jmlt__yct},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    yysg__sbuq = {}
    exec(ayue__bpb, globals(), yysg__sbuq)
    impl = yysg__sbuq['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as pka__apqnn:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    ayue__bpb = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    ayue__bpb += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    ayue__bpb += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        ayue__bpb += '   fig, ax = plt.subplots()\n'
    else:
        ayue__bpb += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        ayue__bpb += '   fig.set_figwidth(figsize[0])\n'
        ayue__bpb += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        ayue__bpb += '   xlabel = x\n'
    ayue__bpb += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        ayue__bpb += '   ylabel = y\n'
    else:
        ayue__bpb += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        ayue__bpb += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        ayue__bpb += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    ayue__bpb += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            ayue__bpb += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            pkzt__xzhbp = get_overload_const_str(x)
            oxzpo__kuqt = df.columns.index(pkzt__xzhbp)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if oxzpo__kuqt != i:
                        ayue__bpb += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            ayue__bpb += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        ayue__bpb += '   ax.scatter(df[x], df[y], s=20)\n'
        ayue__bpb += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        ayue__bpb += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        ayue__bpb += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        ayue__bpb += '   ax.legend()\n'
    ayue__bpb += '   return ax\n'
    yysg__sbuq = {}
    exec(ayue__bpb, {'bodo': bodo, 'plt': plt}, yysg__sbuq)
    impl = yysg__sbuq['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for dafa__hej in df_typ.data:
        if not (isinstance(dafa__hej, IntegerArrayType) or isinstance(
            dafa__hej.dtype, types.Number) or dafa__hej.dtype in (bodo.
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
        kfszy__pgxm = args[0]
        thkbd__mmbvb = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        wdbqs__kgd = kfszy__pgxm
        check_runtime_cols_unsupported(kfszy__pgxm, 'set_df_col()')
        if isinstance(kfszy__pgxm, DataFrameType):
            index = kfszy__pgxm.index
            if len(kfszy__pgxm.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(kfszy__pgxm.columns) == 0:
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
            if thkbd__mmbvb in kfszy__pgxm.columns:
                knry__zug = kfszy__pgxm.columns
                cnmbd__snnx = kfszy__pgxm.columns.index(thkbd__mmbvb)
                jaxa__iiabx = list(kfszy__pgxm.data)
                jaxa__iiabx[cnmbd__snnx] = val
                jaxa__iiabx = tuple(jaxa__iiabx)
            else:
                knry__zug = kfszy__pgxm.columns + (thkbd__mmbvb,)
                jaxa__iiabx = kfszy__pgxm.data + (val,)
            wdbqs__kgd = DataFrameType(jaxa__iiabx, index, knry__zug,
                kfszy__pgxm.dist, kfszy__pgxm.is_table_format)
        return wdbqs__kgd(*args)


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
        gkpy__hxb = args[0]
        assert isinstance(gkpy__hxb, DataFrameType) and len(gkpy__hxb.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        eiljs__xuk = args[2]
        assert len(col_names_to_replace) == len(eiljs__xuk
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(gkpy__hxb.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in gkpy__hxb.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(gkpy__hxb,
            '__bodosql_replace_columns_dummy()')
        index = gkpy__hxb.index
        knry__zug = gkpy__hxb.columns
        jaxa__iiabx = list(gkpy__hxb.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            ugel__yezsi = eiljs__xuk[i]
            assert isinstance(ugel__yezsi, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(ugel__yezsi, SeriesType):
                ugel__yezsi = ugel__yezsi.data
            tytc__iqe = gkpy__hxb.column_index[col_name]
            jaxa__iiabx[tytc__iqe] = ugel__yezsi
        jaxa__iiabx = tuple(jaxa__iiabx)
        wdbqs__kgd = DataFrameType(jaxa__iiabx, index, knry__zug, gkpy__hxb
            .dist, gkpy__hxb.is_table_format)
        return wdbqs__kgd(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    lwzb__lqnzz = {}

    def _rewrite_membership_op(self, node, left, right):
        tcoft__tku = node.op
        op = self.visit(tcoft__tku)
        return op, tcoft__tku, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    eocmc__emjlj = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in eocmc__emjlj:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in eocmc__emjlj:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        emibi__dzln = node.attr
        value = node.value
        qsx__uxcwa = pd.core.computation.ops.LOCAL_TAG
        if emibi__dzln in ('str', 'dt'):
            try:
                ire__ruw = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as hrcq__gyxot:
                col_name = hrcq__gyxot.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            ire__ruw = str(self.visit(value))
        awy__pmrg = ire__ruw, emibi__dzln
        if awy__pmrg in join_cleaned_cols:
            emibi__dzln = join_cleaned_cols[awy__pmrg]
        name = ire__ruw + '.' + emibi__dzln
        if name.startswith(qsx__uxcwa):
            name = name[len(qsx__uxcwa):]
        if emibi__dzln in ('str', 'dt'):
            nfch__phdpa = columns[cleaned_columns.index(ire__ruw)]
            lwzb__lqnzz[nfch__phdpa] = ire__ruw
            self.env.scope[name] = 0
            return self.term_type(qsx__uxcwa + name, self.env)
        eocmc__emjlj.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in eocmc__emjlj:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        umcx__jbdzo = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        thkbd__mmbvb = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(umcx__jbdzo), thkbd__mmbvb))

    def op__str__(self):
        ihje__luj = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            rfuar__ntt)) for rfuar__ntt in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(ihje__luj)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(ihje__luj)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(ihje__luj))
    crem__qgrph = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    roak__pevvc = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_evaluate_binop)
    cuex__cblid = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    wtl__aekah = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    kwmu__vpry = pd.core.computation.ops.Term.__str__
    akwgx__mbc = pd.core.computation.ops.MathCall.__str__
    udi__nyt = pd.core.computation.ops.Op.__str__
    qkbq__vmu = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        nybhx__cywvc = pd.core.computation.expr.Expr(expr, env=env)
        zakwh__upg = str(nybhx__cywvc)
    except pd.core.computation.ops.UndefinedVariableError as hrcq__gyxot:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == hrcq__gyxot.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {hrcq__gyxot}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            crem__qgrph)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            roak__pevvc)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = cuex__cblid
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = wtl__aekah
        pd.core.computation.ops.Term.__str__ = kwmu__vpry
        pd.core.computation.ops.MathCall.__str__ = akwgx__mbc
        pd.core.computation.ops.Op.__str__ = udi__nyt
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            qkbq__vmu)
    qduty__imnm = pd.core.computation.parsing.clean_column_name
    lwzb__lqnzz.update({mwqw__udkx: qduty__imnm(mwqw__udkx) for mwqw__udkx in
        columns if qduty__imnm(mwqw__udkx) in nybhx__cywvc.names})
    return nybhx__cywvc, zakwh__upg, lwzb__lqnzz


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        nvoab__nhdbr = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(nvoab__nhdbr))
        wril__mmj = namedtuple('Pandas', col_names)
        chlch__iebqs = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], wril__mmj)
        super(DataFrameTupleIterator, self).__init__(name, chlch__iebqs)

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
        djqer__nlag = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        djqer__nlag = [types.Array(types.int64, 1, 'C')] + djqer__nlag
        japkz__smlcd = DataFrameTupleIterator(col_names, djqer__nlag)
        return japkz__smlcd(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ypkoz__dttd = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            ypkoz__dttd)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    lna__jgz = args[len(args) // 2:]
    zvsbl__lzp = sig.args[len(sig.args) // 2:]
    mjk__jfbea = context.make_helper(builder, sig.return_type)
    yrt__qjlr = context.get_constant(types.intp, 0)
    pyz__epmzg = cgutils.alloca_once_value(builder, yrt__qjlr)
    mjk__jfbea.index = pyz__epmzg
    for i, arr in enumerate(lna__jgz):
        setattr(mjk__jfbea, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(lna__jgz, zvsbl__lzp):
        context.nrt.incref(builder, arr_typ, arr)
    res = mjk__jfbea._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    lcrr__wym, = sig.args
    uchhh__dqho, = args
    mjk__jfbea = context.make_helper(builder, lcrr__wym, value=uchhh__dqho)
    vdgr__ikkpx = signature(types.intp, lcrr__wym.array_types[1])
    ebyj__nxh = context.compile_internal(builder, lambda a: len(a),
        vdgr__ikkpx, [mjk__jfbea.array0])
    index = builder.load(mjk__jfbea.index)
    vuez__kvb = builder.icmp_signed('<', index, ebyj__nxh)
    result.set_valid(vuez__kvb)
    with builder.if_then(vuez__kvb):
        values = [index]
        for i, arr_typ in enumerate(lcrr__wym.array_types[1:]):
            oxijg__vzg = getattr(mjk__jfbea, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                uua__yym = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    uua__yym, [oxijg__vzg, index])
            else:
                uua__yym = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    uua__yym, [oxijg__vzg, index])
            values.append(val)
        value = context.make_tuple(builder, lcrr__wym.yield_type, values)
        result.yield_(value)
        mguba__zxpc = cgutils.increment_index(builder, index)
        builder.store(mguba__zxpc, mjk__jfbea.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    rhbh__rjd = ir.Assign(rhs, lhs, expr.loc)
    fuh__fbn = lhs
    jmtl__uvi = []
    qgh__mws = []
    kmgss__qgyix = typ.count
    for i in range(kmgss__qgyix):
        jct__loi = ir.Var(fuh__fbn.scope, mk_unique_var('{}_size{}'.format(
            fuh__fbn.name, i)), fuh__fbn.loc)
        krkpw__scos = ir.Expr.static_getitem(lhs, i, None, fuh__fbn.loc)
        self.calltypes[krkpw__scos] = None
        jmtl__uvi.append(ir.Assign(krkpw__scos, jct__loi, fuh__fbn.loc))
        self._define(equiv_set, jct__loi, types.intp, krkpw__scos)
        qgh__mws.append(jct__loi)
    raegc__fnu = tuple(qgh__mws)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        raegc__fnu, pre=[rhbh__rjd] + jmtl__uvi)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
