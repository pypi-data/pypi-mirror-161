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
        gtiyk__awkn = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({gtiyk__awkn})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    jso__cdtez = 'def impl(df):\n'
    if df.has_runtime_cols:
        jso__cdtez += (
            '  return bodo.hiframes.pd_dataframe_ext.get_dataframe_column_names(df)\n'
            )
    else:
        xzfit__piowj = (bodo.hiframes.dataframe_impl.
            generate_col_to_index_func_text(df.columns))
        jso__cdtez += f'  return {xzfit__piowj}'
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo}, opek__gkzkt)
    impl = opek__gkzkt['impl']
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
    lwfgf__gnm = len(df.columns)
    xgrqa__nvurl = set(i for i in range(lwfgf__gnm) if isinstance(df.data[i
        ], IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in xgrqa__nvurl else '') for i in
        range(lwfgf__gnm))
    jso__cdtez = 'def f(df):\n'.format()
    jso__cdtez += '    return np.stack(({},), 1)\n'.format(data_args)
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo, 'np': np}, opek__gkzkt)
    lmyg__onsul = opek__gkzkt['f']
    return lmyg__onsul


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
    xxwx__ezvap = {'dtype': dtype, 'na_value': na_value}
    ymzbh__zmol = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', xxwx__ezvap, ymzbh__zmol,
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
            vlxi__rsvvr = bodo.hiframes.table.compute_num_runtime_columns(t)
            return vlxi__rsvvr * len(t)
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
            vlxi__rsvvr = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), vlxi__rsvvr
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), ncols)


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.dtypes')
    jso__cdtez = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    wpfw__zdgyv = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    jso__cdtez += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{wpfw__zdgyv}), {index}, None)
"""
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo}, opek__gkzkt)
    impl = opek__gkzkt['impl']
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
    xxwx__ezvap = {'copy': copy, 'errors': errors}
    ymzbh__zmol = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', xxwx__ezvap, ymzbh__zmol,
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
        cdp__ulia = []
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        iql__koss = _bodo_object_typeref.instance_type
        assert isinstance(iql__koss, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        if df.is_table_format:
            for i, name in enumerate(df.columns):
                if name in iql__koss.column_index:
                    idx = iql__koss.column_index[name]
                    arr_typ = iql__koss.data[idx]
                else:
                    arr_typ = df.data[i]
                cdp__ulia.append(arr_typ)
        else:
            extra_globals = {}
            oyw__bvlnt = {}
            for i, name in enumerate(iql__koss.columns):
                arr_typ = iql__koss.data[i]
                if isinstance(arr_typ, IntegerArrayType):
                    vca__nkz = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
                elif arr_typ == boolean_array:
                    vca__nkz = boolean_dtype
                else:
                    vca__nkz = arr_typ.dtype
                extra_globals[f'_bodo_schema{i}'] = vca__nkz
                oyw__bvlnt[name] = f'_bodo_schema{i}'
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {oyw__bvlnt[hmr__zflki]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if hmr__zflki in oyw__bvlnt else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, hmr__zflki in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        zvw__fgsq = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        if df.is_table_format:
            zvw__fgsq = {name: dtype_to_array_type(parse_dtype(dtype)) for 
                name, dtype in zvw__fgsq.items()}
            for i, name in enumerate(df.columns):
                if name in zvw__fgsq:
                    arr_typ = zvw__fgsq[name]
                else:
                    arr_typ = df.data[i]
                cdp__ulia.append(arr_typ)
        else:
            data_args = ', '.join(
                f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(zvw__fgsq[hmr__zflki])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
                 if hmr__zflki in zvw__fgsq else
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
                 for i, hmr__zflki in enumerate(df.columns))
    elif df.is_table_format:
        arr_typ = dtype_to_array_type(parse_dtype(dtype))
        cdp__ulia = [arr_typ] * len(df.columns)
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    if df.is_table_format:
        usvn__wdc = bodo.TableType(tuple(cdp__ulia))
        extra_globals['out_table_typ'] = usvn__wdc
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
        lxil__ujkf = types.none
        extra_globals = {'output_arr_typ': lxil__ujkf}
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
        ezfrt__fkm = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(deep):
                ezfrt__fkm.append(arr + '.copy()')
            elif is_overload_false(deep):
                ezfrt__fkm.append(arr)
            else:
                ezfrt__fkm.append(f'{arr}.copy() if deep else {arr}')
        data_args = ', '.join(ezfrt__fkm)
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    xxwx__ezvap = {'index': index, 'level': level, 'errors': errors}
    ymzbh__zmol = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', xxwx__ezvap, ymzbh__zmol,
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
        vtwkc__ysp = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        vtwkc__ysp = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    hfq__ppfjx = tuple([vtwkc__ysp.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))])
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    extra_globals = None
    mhu__pvhwp = None
    if df.is_table_format:
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        mhu__pvhwp = df.copy(columns=hfq__ppfjx)
        lxil__ujkf = types.none
        extra_globals = {'output_arr_typ': lxil__ujkf}
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
        ezfrt__fkm = []
        for i in range(len(df.columns)):
            arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
            if is_overload_true(copy):
                ezfrt__fkm.append(arr + '.copy()')
            elif is_overload_false(copy):
                ezfrt__fkm.append(arr)
            else:
                ezfrt__fkm.append(f'{arr}.copy() if copy else {arr}')
        data_args = ', '.join(ezfrt__fkm)
    return _gen_init_df(header, hfq__ppfjx, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    mffdc__wlsd = not is_overload_none(items)
    bby__zstv = not is_overload_none(like)
    pelqm__cyr = not is_overload_none(regex)
    jqla__kcl = mffdc__wlsd ^ bby__zstv ^ pelqm__cyr
    eqae__ezn = not (mffdc__wlsd or bby__zstv or pelqm__cyr)
    if eqae__ezn:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not jqla__kcl:
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
        zcxr__fir = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        zcxr__fir = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert zcxr__fir in {0, 1}
    jso__cdtez = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if zcxr__fir == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if zcxr__fir == 1:
        otgae__crpf = []
        iwyzl__hgc = []
        kfaa__qzdz = []
        if mffdc__wlsd:
            if is_overload_constant_list(items):
                epiz__hfj = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if bby__zstv:
            if is_overload_constant_str(like):
                jvyon__jlj = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if pelqm__cyr:
            if is_overload_constant_str(regex):
                xve__bulro = get_overload_const_str(regex)
                jxz__sdz = re.compile(xve__bulro)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, hmr__zflki in enumerate(df.columns):
            if not is_overload_none(items
                ) and hmr__zflki in epiz__hfj or not is_overload_none(like
                ) and jvyon__jlj in str(hmr__zflki) or not is_overload_none(
                regex) and jxz__sdz.search(str(hmr__zflki)):
                iwyzl__hgc.append(hmr__zflki)
                kfaa__qzdz.append(i)
        for i in kfaa__qzdz:
            var_name = f'data_{i}'
            otgae__crpf.append(var_name)
            jso__cdtez += f"""  {var_name} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(otgae__crpf)
        return _gen_init_df(jso__cdtez, iwyzl__hgc, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    header = 'def impl(df):\n'
    extra_globals = None
    mhu__pvhwp = None
    if df.is_table_format:
        lxil__ujkf = types.Array(types.bool_, 1, 'C')
        mhu__pvhwp = DataFrameType(tuple([lxil__ujkf] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': lxil__ujkf}
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
    yyrh__bpfax = is_overload_none(include)
    smsjp__rzql = is_overload_none(exclude)
    cbwwq__kdxy = 'DataFrame.select_dtypes'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.select_dtypes()')
    if yyrh__bpfax and smsjp__rzql:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not yyrh__bpfax:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            pizv__cyhjl = [dtype_to_array_type(parse_dtype(elem,
                cbwwq__kdxy)) for elem in include]
        elif is_legal_input(include):
            pizv__cyhjl = [dtype_to_array_type(parse_dtype(include,
                cbwwq__kdxy))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        pizv__cyhjl = get_nullable_and_non_nullable_types(pizv__cyhjl)
        oxi__orop = tuple(hmr__zflki for i, hmr__zflki in enumerate(df.
            columns) if df.data[i] in pizv__cyhjl)
    else:
        oxi__orop = df.columns
    if not smsjp__rzql:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            pdp__wwup = [dtype_to_array_type(parse_dtype(elem, cbwwq__kdxy)
                ) for elem in exclude]
        elif is_legal_input(exclude):
            pdp__wwup = [dtype_to_array_type(parse_dtype(exclude, cbwwq__kdxy))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        pdp__wwup = get_nullable_and_non_nullable_types(pdp__wwup)
        oxi__orop = tuple(hmr__zflki for hmr__zflki in oxi__orop if df.data
            [df.column_index[hmr__zflki]] not in pdp__wwup)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[hmr__zflki]})'
         for hmr__zflki in oxi__orop)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, oxi__orop, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    header = 'def impl(df):\n'
    extra_globals = None
    mhu__pvhwp = None
    if df.is_table_format:
        lxil__ujkf = types.Array(types.bool_, 1, 'C')
        mhu__pvhwp = DataFrameType(tuple([lxil__ujkf] * len(df.data)), df.
            index, df.columns, df.dist, is_table_format=True)
        extra_globals = {'output_arr_typ': lxil__ujkf}
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
    rdjld__uub = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in rdjld__uub:
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
    rdjld__uub = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in rdjld__uub:
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
    jso__cdtez = 'def impl(df, values):\n'
    gvxi__xznpm = {}
    jflyn__jcu = False
    if isinstance(values, DataFrameType):
        jflyn__jcu = True
        for i, hmr__zflki in enumerate(df.columns):
            if hmr__zflki in values.column_index:
                ikdky__qlnun = 'val{}'.format(i)
                jso__cdtez += f"""  {ikdky__qlnun} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {values.column_index[hmr__zflki]})
"""
                gvxi__xznpm[hmr__zflki] = ikdky__qlnun
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        gvxi__xznpm = {hmr__zflki: 'values' for hmr__zflki in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        ikdky__qlnun = 'data{}'.format(i)
        jso__cdtez += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(ikdky__qlnun, i))
        data.append(ikdky__qlnun)
    djnx__lgvzr = ['out{}'.format(i) for i in range(len(df.columns))]
    mat__muwzo = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    ehde__khnnn = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    dgi__bahe = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, rip__wrhgh) in enumerate(zip(df.columns, data)):
        if cname in gvxi__xznpm:
            fpsix__xlom = gvxi__xznpm[cname]
            if jflyn__jcu:
                jso__cdtez += mat__muwzo.format(rip__wrhgh, fpsix__xlom,
                    djnx__lgvzr[i])
            else:
                jso__cdtez += ehde__khnnn.format(rip__wrhgh, fpsix__xlom,
                    djnx__lgvzr[i])
        else:
            jso__cdtez += dgi__bahe.format(djnx__lgvzr[i])
    return _gen_init_df(jso__cdtez, df.columns, ','.join(djnx__lgvzr))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    lwfgf__gnm = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(lwfgf__gnm))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    qhr__aam = [hmr__zflki for hmr__zflki, nwnp__yqotm in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(nwnp__yqotm.
        dtype)]
    assert len(qhr__aam) != 0
    spr__uqo = ''
    if not any(nwnp__yqotm == types.float64 for nwnp__yqotm in df.data):
        spr__uqo = '.astype(np.float64)'
    hdab__wqs = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[hmr__zflki], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[hmr__zflki]], IntegerArrayType) or
        df.data[df.column_index[hmr__zflki]] == boolean_array else '') for
        hmr__zflki in qhr__aam)
    ewwp__iun = 'np.stack(({},), 1){}'.format(hdab__wqs, spr__uqo)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(qhr__aam)))
    index = f'{generate_col_to_index_func_text(qhr__aam)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(ewwp__iun)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, qhr__aam, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    kloot__wclof = dict(ddof=ddof)
    zna__hxxtt = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bwqg__dql = '1' if is_overload_none(min_periods) else 'min_periods'
    qhr__aam = [hmr__zflki for hmr__zflki, nwnp__yqotm in zip(df.columns,
        df.data) if bodo.utils.typing._is_pandas_numeric_dtype(nwnp__yqotm.
        dtype)]
    if len(qhr__aam) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    spr__uqo = ''
    if not any(nwnp__yqotm == types.float64 for nwnp__yqotm in df.data):
        spr__uqo = '.astype(np.float64)'
    hdab__wqs = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[hmr__zflki], '.astype(np.float64)' if 
        isinstance(df.data[df.column_index[hmr__zflki]], IntegerArrayType) or
        df.data[df.column_index[hmr__zflki]] == boolean_array else '') for
        hmr__zflki in qhr__aam)
    ewwp__iun = 'np.stack(({},), 1){}'.format(hdab__wqs, spr__uqo)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(qhr__aam)))
    index = f'pd.Index({qhr__aam})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(ewwp__iun)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        bwqg__dql)
    return _gen_init_df(header, qhr__aam, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    kloot__wclof = dict(axis=axis, level=level, numeric_only=numeric_only)
    zna__hxxtt = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    jso__cdtez = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    jso__cdtez += '  data = np.array([{}])\n'.format(data_args)
    xzfit__piowj = (bodo.hiframes.dataframe_impl.
        generate_col_to_index_func_text(df.columns))
    jso__cdtez += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {xzfit__piowj})\n'
        )
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo, 'np': np}, opek__gkzkt)
    impl = opek__gkzkt['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    kloot__wclof = dict(axis=axis)
    zna__hxxtt = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    jso__cdtez = 'def impl(df, axis=0, dropna=True):\n'
    jso__cdtez += '  data = np.asarray(({},))\n'.format(data_args)
    xzfit__piowj = (bodo.hiframes.dataframe_impl.
        generate_col_to_index_func_text(df.columns))
    jso__cdtez += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {xzfit__piowj})\n'
        )
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo, 'np': np}, opek__gkzkt)
    impl = opek__gkzkt['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    kloot__wclof = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    zna__hxxtt = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.product()')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    kloot__wclof = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    zna__hxxtt = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.sum()')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    kloot__wclof = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    zna__hxxtt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.max()')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    kloot__wclof = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    zna__hxxtt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.min()')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    kloot__wclof = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    zna__hxxtt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.mean()')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    kloot__wclof = dict(skipna=skipna, level=level, ddof=ddof, numeric_only
        =numeric_only)
    zna__hxxtt = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.var()')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    kloot__wclof = dict(skipna=skipna, level=level, ddof=ddof, numeric_only
        =numeric_only)
    zna__hxxtt = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.std()')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    kloot__wclof = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    zna__hxxtt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.median()')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    kloot__wclof = dict(numeric_only=numeric_only, interpolation=interpolation)
    zna__hxxtt = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.quantile()')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    kloot__wclof = dict(axis=axis, skipna=skipna)
    zna__hxxtt = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmax()')
    for bizbx__dllj in df.data:
        if not (bodo.utils.utils.is_np_array_typ(bizbx__dllj) and (
            bizbx__dllj.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(bizbx__dllj.dtype, (types.Number, types.Boolean))) or
            isinstance(bizbx__dllj, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or bizbx__dllj in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {bizbx__dllj} not supported.'
                )
        if isinstance(bizbx__dllj, bodo.CategoricalArrayType
            ) and not bizbx__dllj.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    kloot__wclof = dict(axis=axis, skipna=skipna)
    zna__hxxtt = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.idxmin()')
    for bizbx__dllj in df.data:
        if not (bodo.utils.utils.is_np_array_typ(bizbx__dllj) and (
            bizbx__dllj.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(bizbx__dllj.dtype, (types.Number, types.Boolean))) or
            isinstance(bizbx__dllj, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or bizbx__dllj in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {bizbx__dllj} not supported.'
                )
        if isinstance(bizbx__dllj, bodo.CategoricalArrayType
            ) and not bizbx__dllj.dtype.ordered:
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
        qhr__aam = tuple(hmr__zflki for hmr__zflki, nwnp__yqotm in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (nwnp__yqotm.dtype))
        out_colnames = qhr__aam
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            tnlue__abq = [numba.np.numpy_support.as_dtype(df.data[df.
                column_index[hmr__zflki]].dtype) for hmr__zflki in out_colnames
                ]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(tnlue__abq, []))
    except NotImplementedError as oiyu__rdix:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    vnap__yls = ''
    if func_name in ('sum', 'prod'):
        vnap__yls = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    jso__cdtez = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, vnap__yls))
    if func_name == 'quantile':
        jso__cdtez = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        jso__cdtez = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        jso__cdtez += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        jso__cdtez += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        opek__gkzkt)
    impl = opek__gkzkt['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    qnrad__hxmy = ''
    if func_name in ('min', 'max'):
        qnrad__hxmy = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        qnrad__hxmy = ', dtype=np.float32'
    ips__gbf = f'bodo.libs.array_ops.array_op_{func_name}'
    sxnc__ipvjp = ''
    if func_name in ['sum', 'prod']:
        sxnc__ipvjp = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        sxnc__ipvjp = 'index'
    elif func_name == 'quantile':
        sxnc__ipvjp = 'q'
    elif func_name in ['std', 'var']:
        sxnc__ipvjp = 'True, ddof'
    elif func_name == 'median':
        sxnc__ipvjp = 'True'
    data_args = ', '.join(
        f'{ips__gbf}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.column_index[hmr__zflki]}), {sxnc__ipvjp})'
         for hmr__zflki in out_colnames)
    jso__cdtez = ''
    if func_name in ('idxmax', 'idxmin'):
        jso__cdtez += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        jso__cdtez += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        jso__cdtez += '  data = np.asarray(({},){})\n'.format(data_args,
            qnrad__hxmy)
    jso__cdtez += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return jso__cdtez


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    ypzss__brylu = [df_type.column_index[hmr__zflki] for hmr__zflki in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in ypzss__brylu)
    hvte__bjn = '\n        '.join(f'row[{i}] = arr_{ypzss__brylu[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    lnsmg__dxt = f'len(arr_{ypzss__brylu[0]})'
    euke__uinx = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in euke__uinx:
        izpt__zovo = euke__uinx[func_name]
        sbwtq__mfbk = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        jso__cdtez = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {lnsmg__dxt}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{sbwtq__mfbk})
    for i in numba.parfors.parfor.internal_prange(n):
        {hvte__bjn}
        A[i] = {izpt__zovo}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return jso__cdtez
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    kloot__wclof = dict(fill_method=fill_method, limit=limit, freq=freq)
    zna__hxxtt = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', kloot__wclof, zna__hxxtt,
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
    kloot__wclof = dict(axis=axis, skipna=skipna)
    zna__hxxtt = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', kloot__wclof, zna__hxxtt,
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
    kloot__wclof = dict(skipna=skipna)
    zna__hxxtt = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', kloot__wclof, zna__hxxtt,
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
    kloot__wclof = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    zna__hxxtt = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.describe()')
    qhr__aam = [hmr__zflki for hmr__zflki, nwnp__yqotm in zip(df.columns,
        df.data) if _is_describe_type(nwnp__yqotm)]
    if len(qhr__aam) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    gms__kca = sum(df.data[df.column_index[hmr__zflki]].dtype == bodo.
        datetime64ns for hmr__zflki in qhr__aam)

    def _get_describe(col_ind):
        ibaq__xmvks = df.data[col_ind].dtype == bodo.datetime64ns
        if gms__kca and gms__kca != len(qhr__aam):
            if ibaq__xmvks:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for hmr__zflki in qhr__aam:
        col_ind = df.column_index[hmr__zflki]
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.column_index[hmr__zflki]) for
        hmr__zflki in qhr__aam)
    dgxum__sqpdg = (
        "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']")
    if gms__kca == len(qhr__aam):
        dgxum__sqpdg = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif gms__kca:
        dgxum__sqpdg = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({dgxum__sqpdg})'
    return _gen_init_df(header, qhr__aam, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    kloot__wclof = dict(axis=axis, convert=convert, is_copy=is_copy)
    zna__hxxtt = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', kloot__wclof, zna__hxxtt,
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
    kloot__wclof = dict(freq=freq, axis=axis, fill_value=fill_value)
    zna__hxxtt = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.shift()')
    for jqvt__rvcw in df.data:
        if not is_supported_shift_array_type(jqvt__rvcw):
            raise BodoError(
                f'Dataframe.shift() column input type {jqvt__rvcw.dtype} not supported yet.'
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
    kloot__wclof = dict(axis=axis)
    zna__hxxtt = dict(axis=0)
    check_unsupported_args('DataFrame.diff', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.diff()')
    for jqvt__rvcw in df.data:
        if not (isinstance(jqvt__rvcw, types.Array) and (isinstance(
            jqvt__rvcw.dtype, types.Number) or jqvt__rvcw.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {jqvt__rvcw.dtype} not supported.'
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
    xzxtx__abo = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(xzxtx__abo)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        kkr__xdii = get_overload_const_list(column)
    else:
        kkr__xdii = [get_literal_value(column)]
    qdwyd__xod = [df.column_index[hmr__zflki] for hmr__zflki in kkr__xdii]
    for i in qdwyd__xod:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{qdwyd__xod[0]})\n'
        )
    for i in range(n):
        if i in qdwyd__xod:
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
    xxwx__ezvap = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    ymzbh__zmol = {'inplace': False, 'append': False, 'verify_integrity': False
        }
    check_unsupported_args('DataFrame.set_index', xxwx__ezvap, ymzbh__zmol,
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
    columns = tuple(hmr__zflki for hmr__zflki in df.columns if hmr__zflki !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    xxwx__ezvap = {'inplace': inplace}
    ymzbh__zmol = {'inplace': False}
    check_unsupported_args('query', xxwx__ezvap, ymzbh__zmol, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        pekce__vlb = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[pekce__vlb]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    xxwx__ezvap = {'subset': subset, 'keep': keep}
    ymzbh__zmol = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', xxwx__ezvap, ymzbh__zmol,
        package_name='pandas', module_name='DataFrame')
    lwfgf__gnm = len(df.columns)
    jso__cdtez = "def impl(df, subset=None, keep='first'):\n"
    for i in range(lwfgf__gnm):
        jso__cdtez += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    zwg__nwx = ', '.join(f'data_{i}' for i in range(lwfgf__gnm))
    zwg__nwx += ',' if lwfgf__gnm == 1 else ''
    jso__cdtez += (
        f'  duplicated = bodo.libs.array_kernels.duplicated(({zwg__nwx}))\n')
    jso__cdtez += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    jso__cdtez += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo}, opek__gkzkt)
    impl = opek__gkzkt['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    xxwx__ezvap = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    ymzbh__zmol = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    qzdo__xbzm = []
    if is_overload_constant_list(subset):
        qzdo__xbzm = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        qzdo__xbzm = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        qzdo__xbzm = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    uskug__ehy = []
    for col_name in qzdo__xbzm:
        if col_name not in df.column_index:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        uskug__ehy.append(df.column_index[col_name])
    check_unsupported_args('DataFrame.drop_duplicates', xxwx__ezvap,
        ymzbh__zmol, package_name='pandas', module_name='DataFrame')
    uqpgw__gma = []
    if uskug__ehy:
        for byrma__fnslg in uskug__ehy:
            if isinstance(df.data[byrma__fnslg], bodo.MapArrayType):
                uqpgw__gma.append(df.columns[byrma__fnslg])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                uqpgw__gma.append(col_name)
    if uqpgw__gma:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {uqpgw__gma} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    lwfgf__gnm = len(df.columns)
    aeo__mvbf = ['data_{}'.format(i) for i in uskug__ehy]
    ofpcp__ynk = ['data_{}'.format(i) for i in range(lwfgf__gnm) if i not in
        uskug__ehy]
    if aeo__mvbf:
        fomsw__cfkr = len(aeo__mvbf)
    else:
        fomsw__cfkr = lwfgf__gnm
    yvm__zdvl = ', '.join(aeo__mvbf + ofpcp__ynk)
    data_args = ', '.join('data_{}'.format(i) for i in range(lwfgf__gnm))
    jso__cdtez = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(lwfgf__gnm):
        jso__cdtez += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    jso__cdtez += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(yvm__zdvl, index, fomsw__cfkr))
    jso__cdtez += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(jso__cdtez, df.columns, data_args, 'index')


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
            uccz__nuwa = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                uccz__nuwa = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other.column_index[df.columns[i]]})'
                     if df.columns[i] in other.column_index else 'None')
            elif isinstance(other, types.Array):
                uccz__nuwa = lambda i: f'other[:,{i}]'
        lwfgf__gnm = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {uccz__nuwa(i)})'
             for i in range(lwfgf__gnm))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        vbp__ucq = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(vbp__ucq)


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    kloot__wclof = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    zna__hxxtt = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', kloot__wclof, zna__hxxtt,
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
    lwfgf__gnm = len(df.columns)
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
        for i in range(lwfgf__gnm):
            if df.columns[i] in other.column_index:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], other.data[other.
                    column_index[df.columns[i]]])
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, 'Series', df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(lwfgf__gnm):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other.data)
    else:
        for i in range(lwfgf__gnm):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , 'Series', df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    eozvy__xsmo = ColNamesMetaType(tuple(columns))
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    jso__cdtez = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, __col_name_meta_value_gen_init_df)
"""
    opek__gkzkt = {}
    qck__jfzi = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba,
        '__col_name_meta_value_gen_init_df': eozvy__xsmo}
    qck__jfzi.update(extra_globals)
    exec(jso__cdtez, qck__jfzi, opek__gkzkt)
    impl = opek__gkzkt['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        yul__fjiei = pd.Index(lhs.columns)
        mdcz__fvkvb = pd.Index(rhs.columns)
        dyzf__ermyp, ckjj__tjg, wsn__uoo = yul__fjiei.join(mdcz__fvkvb, how
            ='left' if is_inplace else 'outer', level=None, return_indexers
            =True)
        return tuple(dyzf__ermyp), ckjj__tjg, wsn__uoo
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        vdzet__nrj = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        zkj__spoal = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, vdzet__nrj)
        check_runtime_cols_unsupported(rhs, vdzet__nrj)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                dyzf__ermyp, ckjj__tjg, wsn__uoo = _get_binop_columns(lhs, rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {sgwy__svs}) {vdzet__nrj}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {orijm__rfwsu})'
                     if sgwy__svs != -1 and orijm__rfwsu != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for sgwy__svs, orijm__rfwsu in zip(ckjj__tjg, wsn__uoo))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, dyzf__ermyp, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            elif isinstance(rhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            pnhr__nkm = []
            sec__ffrn = []
            if op in zkj__spoal:
                for i, ebpr__yuttk in enumerate(lhs.data):
                    if is_common_scalar_dtype([ebpr__yuttk.dtype, rhs]):
                        pnhr__nkm.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {vdzet__nrj} rhs'
                            )
                    else:
                        xzllt__yukm = f'arr{i}'
                        sec__ffrn.append(xzllt__yukm)
                        pnhr__nkm.append(xzllt__yukm)
                data_args = ', '.join(pnhr__nkm)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {vdzet__nrj} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(sec__ffrn) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {xzllt__yukm} = np.empty(n, dtype=np.bool_)\n' for
                    xzllt__yukm in sec__ffrn)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(xzllt__yukm, 
                    op == operator.ne) for xzllt__yukm in sec__ffrn)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            if isinstance(lhs, SeriesType):
                raise_bodo_error(
                    'Comparison operation between Dataframe and Series is not supported yet.'
                    )
            pnhr__nkm = []
            sec__ffrn = []
            if op in zkj__spoal:
                for i, ebpr__yuttk in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, ebpr__yuttk.dtype]):
                        pnhr__nkm.append(
                            f'lhs {vdzet__nrj} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        xzllt__yukm = f'arr{i}'
                        sec__ffrn.append(xzllt__yukm)
                        pnhr__nkm.append(xzllt__yukm)
                data_args = ', '.join(pnhr__nkm)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, vdzet__nrj) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(sec__ffrn) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(xzllt__yukm) for xzllt__yukm in sec__ffrn)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(xzllt__yukm, 
                    op == operator.ne) for xzllt__yukm in sec__ffrn)
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
        vbp__ucq = create_binary_op_overload(op)
        overload(op)(vbp__ucq)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        vdzet__nrj = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, vdzet__nrj)
        check_runtime_cols_unsupported(right, vdzet__nrj)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                dyzf__ermyp, _, wsn__uoo = _get_binop_columns(left, right, True
                    )
                jso__cdtez = 'def impl(left, right):\n'
                for i, orijm__rfwsu in enumerate(wsn__uoo):
                    if orijm__rfwsu == -1:
                        jso__cdtez += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    jso__cdtez += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    jso__cdtez += f"""  df_arr{i} {vdzet__nrj} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {orijm__rfwsu})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    dyzf__ermyp)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(jso__cdtez, dyzf__ermyp, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            jso__cdtez = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                jso__cdtez += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                jso__cdtez += '  df_arr{0} {1} right\n'.format(i, vdzet__nrj)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(jso__cdtez, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        vbp__ucq = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(vbp__ucq)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            vdzet__nrj = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, vdzet__nrj)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, vdzet__nrj) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        vbp__ucq = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(vbp__ucq)


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
            henv__qnay = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                henv__qnay[i] = bodo.libs.array_kernels.isna(obj, i)
            return henv__qnay
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
            henv__qnay = np.empty(n, np.bool_)
            for i in range(n):
                henv__qnay[i] = pd.isna(obj[i])
            return henv__qnay
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
    xxwx__ezvap = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    ymzbh__zmol = {'inplace': False, 'limit': None, 'regex': False,
        'method': 'pad'}
    check_unsupported_args('replace', xxwx__ezvap, ymzbh__zmol,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    gjx__moi = str(expr_node)
    return gjx__moi.startswith('left.') or gjx__moi.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    tbqaq__jgkqs = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (tbqaq__jgkqs,))
    qozqp__ghkpb = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        ibz__nfpcb = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        dwo__pcxim = {('NOT_NA', qozqp__ghkpb(ebpr__yuttk)): ebpr__yuttk for
            ebpr__yuttk in null_set}
        orjb__ppswn, _, _ = _parse_query_expr(ibz__nfpcb, env, [], [], None,
            join_cleaned_cols=dwo__pcxim)
        mcnd__amwf = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            ujpp__qjla = pd.core.computation.ops.BinOp('&', orjb__ppswn,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = mcnd__amwf
        return ujpp__qjla

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                tvj__xir = set()
                auo__swol = set()
                gnldh__mbclz = _insert_NA_cond_body(expr_node.lhs, tvj__xir)
                fpzgw__gfthj = _insert_NA_cond_body(expr_node.rhs, auo__swol)
                yqu__bna = tvj__xir.intersection(auo__swol)
                tvj__xir.difference_update(yqu__bna)
                auo__swol.difference_update(yqu__bna)
                null_set.update(yqu__bna)
                expr_node.lhs = append_null_checks(gnldh__mbclz, tvj__xir)
                expr_node.rhs = append_null_checks(fpzgw__gfthj, auo__swol)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            tmaq__vyckj = expr_node.name
            kphx__vlss, col_name = tmaq__vyckj.split('.')
            if kphx__vlss == 'left':
                dwm__cpbxm = left_columns
                data = left_data
            else:
                dwm__cpbxm = right_columns
                data = right_data
            njhtz__paf = data[dwm__cpbxm.index(col_name)]
            if bodo.utils.typing.is_nullable(njhtz__paf):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    cft__kttqy = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        eyoy__tzwa = str(expr_node.lhs)
        urcvz__qyt = str(expr_node.rhs)
        if eyoy__tzwa.startswith('left.') and urcvz__qyt.startswith('left.'
            ) or eyoy__tzwa.startswith('right.') and urcvz__qyt.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [eyoy__tzwa.split('.')[1]]
        right_on = [urcvz__qyt.split('.')[1]]
        if eyoy__tzwa.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        hjg__wbfzp, lylo__dkmbg, phczc__aau = _extract_equal_conds(expr_node
            .lhs)
        lksm__ijt, oers__ahq, pses__wefm = _extract_equal_conds(expr_node.rhs)
        left_on = hjg__wbfzp + lksm__ijt
        right_on = lylo__dkmbg + oers__ahq
        if phczc__aau is None:
            return left_on, right_on, pses__wefm
        if pses__wefm is None:
            return left_on, right_on, phczc__aau
        expr_node.lhs = phczc__aau
        expr_node.rhs = pses__wefm
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    tbqaq__jgkqs = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (tbqaq__jgkqs,))
    vtwkc__ysp = dict()
    qozqp__ghkpb = pd.core.computation.parsing.clean_column_name
    for name, okeue__raya in (('left', left_columns), ('right', right_columns)
        ):
        for ebpr__yuttk in okeue__raya:
            yeqah__ktltn = qozqp__ghkpb(ebpr__yuttk)
            jckc__rje = name, yeqah__ktltn
            if jckc__rje in vtwkc__ysp:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{ebpr__yuttk}' and '{vtwkc__ysp[yeqah__ktltn]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            vtwkc__ysp[jckc__rje] = ebpr__yuttk
    xrpyr__sfc, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=vtwkc__ysp)
    left_on, right_on, hsz__sjn = _extract_equal_conds(xrpyr__sfc.terms)
    return left_on, right_on, _insert_NA_cond(hsz__sjn, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    kloot__wclof = dict(sort=sort, copy=copy, validate=validate)
    zna__hxxtt = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    dprkm__sioc = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    lmqtn__zwsul = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in dprkm__sioc and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, vbn__zkq = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if vbn__zkq is None:
                    lmqtn__zwsul = ''
                else:
                    lmqtn__zwsul = str(vbn__zkq)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = dprkm__sioc
        right_keys = dprkm__sioc
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
    hck__tor = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        hau__acyv = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        hau__acyv = list(get_overload_const_list(suffixes))
    suffix_x = hau__acyv[0]
    suffix_y = hau__acyv[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    jso__cdtez = "def _impl(left, right, how='inner', on=None, left_on=None,\n"
    jso__cdtez += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    jso__cdtez += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    jso__cdtez += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, hck__tor, lmqtn__zwsul))
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo}, opek__gkzkt)
    _impl = opek__gkzkt['_impl']
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
    phcu__azcf = {string_array_type, dict_str_arr_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    xvi__sfcf = {get_overload_const_str(kuf__zqbeo) for kuf__zqbeo in (
        left_on, right_on, on) if is_overload_constant_str(kuf__zqbeo)}
    for df in (left, right):
        for i, ebpr__yuttk in enumerate(df.data):
            if not isinstance(ebpr__yuttk, valid_dataframe_column_types
                ) and ebpr__yuttk not in phcu__azcf:
                raise BodoError(
                    f'{name_func}(): use of column with {type(ebpr__yuttk)} in merge unsupported'
                    )
            if df.columns[i] in xvi__sfcf and isinstance(ebpr__yuttk,
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
        hau__acyv = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        hau__acyv = list(get_overload_const_list(suffixes))
    if len(hau__acyv) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    dprkm__sioc = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        jtdnf__sjojt = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            jtdnf__sjojt = on_str not in dprkm__sioc and ('left.' in on_str or
                'right.' in on_str)
        if len(dprkm__sioc) == 0 and not jtdnf__sjojt:
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
    pdnho__hyzif = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            kbuh__anou = left.index
            rdh__hlnug = isinstance(kbuh__anou, StringIndexType)
            xmjd__rthi = right.index
            tski__msi = isinstance(xmjd__rthi, StringIndexType)
        elif is_overload_true(left_index):
            kbuh__anou = left.index
            rdh__hlnug = isinstance(kbuh__anou, StringIndexType)
            xmjd__rthi = right.data[right.columns.index(right_keys[0])]
            tski__msi = xmjd__rthi.dtype == string_type
        elif is_overload_true(right_index):
            kbuh__anou = left.data[left.columns.index(left_keys[0])]
            rdh__hlnug = kbuh__anou.dtype == string_type
            xmjd__rthi = right.index
            tski__msi = isinstance(xmjd__rthi, StringIndexType)
        if rdh__hlnug and tski__msi:
            return
        kbuh__anou = kbuh__anou.dtype
        xmjd__rthi = xmjd__rthi.dtype
        try:
            vonjn__vqc = pdnho__hyzif.resolve_function_type(operator.eq, (
                kbuh__anou, xmjd__rthi), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=kbuh__anou, rk_dtype=xmjd__rthi))
    else:
        for hln__pptlw, ssdv__yje in zip(left_keys, right_keys):
            kbuh__anou = left.data[left.columns.index(hln__pptlw)].dtype
            nmf__jwx = left.data[left.columns.index(hln__pptlw)]
            xmjd__rthi = right.data[right.columns.index(ssdv__yje)].dtype
            hqiw__shvoc = right.data[right.columns.index(ssdv__yje)]
            if nmf__jwx == hqiw__shvoc:
                continue
            emgmy__xdd = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=hln__pptlw, lk_dtype=kbuh__anou, rk=ssdv__yje,
                rk_dtype=xmjd__rthi))
            yfthk__xhkg = kbuh__anou == string_type
            hfyv__ziyvy = xmjd__rthi == string_type
            if yfthk__xhkg ^ hfyv__ziyvy:
                raise_bodo_error(emgmy__xdd)
            try:
                vonjn__vqc = pdnho__hyzif.resolve_function_type(operator.eq,
                    (kbuh__anou, xmjd__rthi), {})
            except:
                raise_bodo_error(emgmy__xdd)


def validate_keys(keys, df):
    xjv__ortip = set(keys).difference(set(df.columns))
    if len(xjv__ortip) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in xjv__ortip:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {xjv__ortip} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    kloot__wclof = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    zna__hxxtt = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', kloot__wclof, zna__hxxtt,
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
    jso__cdtez = "def _impl(left, other, on=None, how='left',\n"
    jso__cdtez += "    lsuffix='', rsuffix='', sort=False):\n"
    jso__cdtez += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo}, opek__gkzkt)
    _impl = opek__gkzkt['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        fdl__lwqvz = get_overload_const_list(on)
        validate_keys(fdl__lwqvz, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    dprkm__sioc = tuple(set(left.columns) & set(other.columns))
    if len(dprkm__sioc) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=dprkm__sioc))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    yjsk__ouos = set(left_keys) & set(right_keys)
    outr__suiaf = set(left_columns) & set(right_columns)
    csk__wmybr = outr__suiaf - yjsk__ouos
    dcoiy__ylzva = set(left_columns) - outr__suiaf
    dtldk__nzl = set(right_columns) - outr__suiaf
    tize__pyap = {}

    def insertOutColumn(col_name):
        if col_name in tize__pyap:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        tize__pyap[col_name] = 0
    for uxjdi__gcr in yjsk__ouos:
        insertOutColumn(uxjdi__gcr)
    for uxjdi__gcr in csk__wmybr:
        tqff__zmcca = str(uxjdi__gcr) + suffix_x
        dojiu__rml = str(uxjdi__gcr) + suffix_y
        insertOutColumn(tqff__zmcca)
        insertOutColumn(dojiu__rml)
    for uxjdi__gcr in dcoiy__ylzva:
        insertOutColumn(uxjdi__gcr)
    for uxjdi__gcr in dtldk__nzl:
        insertOutColumn(uxjdi__gcr)
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
    dprkm__sioc = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = dprkm__sioc
        right_keys = dprkm__sioc
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
        hau__acyv = suffixes
    if is_overload_constant_list(suffixes):
        hau__acyv = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        hau__acyv = suffixes.value
    suffix_x = hau__acyv[0]
    suffix_y = hau__acyv[1]
    jso__cdtez = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    jso__cdtez += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    jso__cdtez += "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n"
    jso__cdtez += "    allow_exact_matches=True, direction='backward'):\n"
    jso__cdtez += '  suffix_x = suffixes[0]\n'
    jso__cdtez += '  suffix_y = suffixes[1]\n'
    jso__cdtez += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo}, opek__gkzkt)
    _impl = opek__gkzkt['_impl']
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
    kloot__wclof = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    akzeb__zoq = dict(sort=False, group_keys=True, squeeze=False, observed=True
        )
    check_unsupported_args('Dataframe.groupby', kloot__wclof, akzeb__zoq,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    nojw__xrviu = func_name == 'DataFrame.pivot_table'
    if nojw__xrviu:
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
    fqfw__vmvm = get_literal_value(columns)
    if isinstance(fqfw__vmvm, (list, tuple)):
        if len(fqfw__vmvm) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {fqfw__vmvm}"
                )
        fqfw__vmvm = fqfw__vmvm[0]
    if fqfw__vmvm not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {fqfw__vmvm} not found in DataFrame {df}."
            )
    qem__rvji = df.column_index[fqfw__vmvm]
    if is_overload_none(index):
        xvu__mvub = []
        nzvz__acq = []
    else:
        nzvz__acq = get_literal_value(index)
        if not isinstance(nzvz__acq, (list, tuple)):
            nzvz__acq = [nzvz__acq]
        xvu__mvub = []
        for index in nzvz__acq:
            if index not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            xvu__mvub.append(df.column_index[index])
    if not (all(isinstance(hmr__zflki, int) for hmr__zflki in nzvz__acq) or
        all(isinstance(hmr__zflki, str) for hmr__zflki in nzvz__acq)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        dzs__hdpxj = []
        rzhl__fgljf = []
        lki__atk = xvu__mvub + [qem__rvji]
        for i, hmr__zflki in enumerate(df.columns):
            if i not in lki__atk:
                dzs__hdpxj.append(i)
                rzhl__fgljf.append(hmr__zflki)
    else:
        rzhl__fgljf = get_literal_value(values)
        if not isinstance(rzhl__fgljf, (list, tuple)):
            rzhl__fgljf = [rzhl__fgljf]
        dzs__hdpxj = []
        for val in rzhl__fgljf:
            if val not in df.column_index:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            dzs__hdpxj.append(df.column_index[val])
    cndrh__uaid = set(dzs__hdpxj) | set(xvu__mvub) | {qem__rvji}
    if len(cndrh__uaid) != len(dzs__hdpxj) + len(xvu__mvub) + 1:
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
    if len(xvu__mvub) == 0:
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
        for vrgp__ojdo in xvu__mvub:
            index_column = df.data[vrgp__ojdo]
            check_valid_index_typ(index_column)
    oedz__ngegn = df.data[qem__rvji]
    if isinstance(oedz__ngegn, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(oedz__ngegn, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for wjgu__penae in dzs__hdpxj:
        obmx__ijy = df.data[wjgu__penae]
        if isinstance(obmx__ijy, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or obmx__ijy == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return nzvz__acq, fqfw__vmvm, rzhl__fgljf, xvu__mvub, qem__rvji, dzs__hdpxj


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (nzvz__acq, fqfw__vmvm, rzhl__fgljf, vrgp__ojdo, qem__rvji, gtkht__fiocx
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot'))
    if len(nzvz__acq) == 0:
        if is_overload_none(data.index.name_typ):
            otz__sdrtj = None,
        else:
            otz__sdrtj = get_literal_value(data.index.name_typ),
    else:
        otz__sdrtj = tuple(nzvz__acq)
    nzvz__acq = ColNamesMetaType(otz__sdrtj)
    rzhl__fgljf = ColNamesMetaType(tuple(rzhl__fgljf))
    fqfw__vmvm = ColNamesMetaType((fqfw__vmvm,))
    jso__cdtez = 'def impl(data, index=None, columns=None, values=None):\n'
    jso__cdtez += f'    pivot_values = data.iloc[:, {qem__rvji}].unique()\n'
    jso__cdtez += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(vrgp__ojdo) == 0:
        jso__cdtez += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        jso__cdtez += '        (\n'
        for jydeh__ogwl in vrgp__ojdo:
            jso__cdtez += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {jydeh__ogwl}),
"""
        jso__cdtez += '        ),\n'
    jso__cdtez += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {qem__rvji}),),
"""
    jso__cdtez += '        (\n'
    for wjgu__penae in gtkht__fiocx:
        jso__cdtez += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {wjgu__penae}),
"""
    jso__cdtez += '        ),\n'
    jso__cdtez += '        pivot_values,\n'
    jso__cdtez += '        index_lit,\n'
    jso__cdtez += '        columns_lit,\n'
    jso__cdtez += '        values_lit,\n'
    jso__cdtez += '    )\n'
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo, 'index_lit': nzvz__acq, 'columns_lit':
        fqfw__vmvm, 'values_lit': rzhl__fgljf}, opek__gkzkt)
    impl = opek__gkzkt['impl']
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
    kloot__wclof = dict(fill_value=fill_value, margins=margins, dropna=
        dropna, margins_name=margins_name, observed=observed, sort=sort)
    zna__hxxtt = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', kloot__wclof,
        zna__hxxtt, package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    (nzvz__acq, fqfw__vmvm, rzhl__fgljf, vrgp__ojdo, qem__rvji, gtkht__fiocx
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot_table'))
    pmaa__jbspi = nzvz__acq
    nzvz__acq = ColNamesMetaType(tuple(nzvz__acq))
    rzhl__fgljf = ColNamesMetaType(tuple(rzhl__fgljf))
    bmzr__siwlr = fqfw__vmvm
    fqfw__vmvm = ColNamesMetaType((fqfw__vmvm,))
    jso__cdtez = 'def impl(\n'
    jso__cdtez += '    data,\n'
    jso__cdtez += '    values=None,\n'
    jso__cdtez += '    index=None,\n'
    jso__cdtez += '    columns=None,\n'
    jso__cdtez += '    aggfunc="mean",\n'
    jso__cdtez += '    fill_value=None,\n'
    jso__cdtez += '    margins=False,\n'
    jso__cdtez += '    dropna=True,\n'
    jso__cdtez += '    margins_name="All",\n'
    jso__cdtez += '    observed=False,\n'
    jso__cdtez += '    sort=True,\n'
    jso__cdtez += '    _pivot_values=None,\n'
    jso__cdtez += '):\n'
    rjeqt__cemkj = vrgp__ojdo + [qem__rvji] + gtkht__fiocx
    jso__cdtez += f'    data = data.iloc[:, {rjeqt__cemkj}]\n'
    bcffn__ufr = pmaa__jbspi + [bmzr__siwlr]
    if not is_overload_none(_pivot_values):
        ktzen__ezj = tuple(sorted(_pivot_values.meta))
        _pivot_values = ColNamesMetaType(ktzen__ezj)
        jso__cdtez += '    pivot_values = _pivot_values_arr\n'
        jso__cdtez += (
            f'    data = data[data.iloc[:, {len(vrgp__ojdo)}].isin(pivot_values)]\n'
            )
        if all(isinstance(hmr__zflki, str) for hmr__zflki in ktzen__ezj):
            sdr__vsx = pd.array(ktzen__ezj, 'string')
        elif all(isinstance(hmr__zflki, int) for hmr__zflki in ktzen__ezj):
            sdr__vsx = np.array(ktzen__ezj, 'int64')
        else:
            raise BodoError(
                f'pivot(): pivot values selcected via pivot JIT argument must all share a common int or string type.'
                )
    else:
        sdr__vsx = None
    jso__cdtez += (
        f'    data = data.groupby({bcffn__ufr!r}, as_index=False).agg(aggfunc)\n'
        )
    if is_overload_none(_pivot_values):
        jso__cdtez += (
            f'    pivot_values = data.iloc[:, {len(vrgp__ojdo)}].unique()\n')
    jso__cdtez += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    jso__cdtez += '        (\n'
    for i in range(0, len(vrgp__ojdo)):
        jso__cdtez += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    jso__cdtez += '        ),\n'
    jso__cdtez += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(vrgp__ojdo)}),),
"""
    jso__cdtez += '        (\n'
    for i in range(len(vrgp__ojdo) + 1, len(gtkht__fiocx) + len(vrgp__ojdo) + 1
        ):
        jso__cdtez += (
            f'            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),\n'
            )
    jso__cdtez += '        ),\n'
    jso__cdtez += '        pivot_values,\n'
    jso__cdtez += '        index_lit,\n'
    jso__cdtez += '        columns_lit,\n'
    jso__cdtez += '        values_lit,\n'
    jso__cdtez += '        check_duplicates=False,\n'
    jso__cdtez += '        _constant_pivot_values=_constant_pivot_values,\n'
    jso__cdtez += '    )\n'
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo, 'numba': numba, 'index_lit': nzvz__acq,
        'columns_lit': fqfw__vmvm, 'values_lit': rzhl__fgljf,
        '_pivot_values_arr': sdr__vsx, '_constant_pivot_values':
        _pivot_values}, opek__gkzkt)
    impl = opek__gkzkt['impl']
    return impl


@overload(pd.melt, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'melt', inline='always', no_unliteral=True)
def overload_dataframe_melt(frame, id_vars=None, value_vars=None, var_name=
    None, value_name='value', col_level=None, ignore_index=True):
    kloot__wclof = dict(col_level=col_level, ignore_index=ignore_index)
    zna__hxxtt = dict(col_level=None, ignore_index=True)
    check_unsupported_args('DataFrame.melt', kloot__wclof, zna__hxxtt,
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
    mas__neakw = get_literal_value(id_vars) if not is_overload_none(id_vars
        ) else []
    if not isinstance(mas__neakw, (list, tuple)):
        mas__neakw = [mas__neakw]
    for hmr__zflki in mas__neakw:
        if hmr__zflki not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'id_vars' column {hmr__zflki} not found in {frame}."
                )
    kmohq__smmov = [frame.column_index[i] for i in mas__neakw]
    if is_overload_none(value_vars):
        klw__ljna = []
        gvy__gxwj = []
        for i, hmr__zflki in enumerate(frame.columns):
            if i not in kmohq__smmov:
                klw__ljna.append(i)
                gvy__gxwj.append(hmr__zflki)
    else:
        gvy__gxwj = get_literal_value(value_vars)
        if not isinstance(gvy__gxwj, (list, tuple)):
            gvy__gxwj = [gvy__gxwj]
        gvy__gxwj = [v for v in gvy__gxwj if v not in mas__neakw]
        if not gvy__gxwj:
            raise BodoError(
                "DataFrame.melt(): currently empty 'value_vars' is unsupported."
                )
        klw__ljna = []
        for val in gvy__gxwj:
            if val not in frame.column_index:
                raise BodoError(
                    f"DataFrame.melt(): 'value_vars' column {val} not found in DataFrame {frame}."
                    )
            klw__ljna.append(frame.column_index[val])
    for hmr__zflki in gvy__gxwj:
        if hmr__zflki not in frame.columns:
            raise BodoError(
                f"DataFrame.melt(): 'value_vars' column {hmr__zflki} not found in {frame}."
                )
    if not (all(isinstance(hmr__zflki, int) for hmr__zflki in gvy__gxwj) or
        all(isinstance(hmr__zflki, str) for hmr__zflki in gvy__gxwj)):
        raise BodoError(
            f"DataFrame.melt(): column names selected for 'value_vars' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    exuq__knepx = frame.data[klw__ljna[0]]
    otrk__eot = [frame.data[i].dtype for i in klw__ljna]
    klw__ljna = np.array(klw__ljna, dtype=np.int64)
    kmohq__smmov = np.array(kmohq__smmov, dtype=np.int64)
    _, abkel__fcq = bodo.utils.typing.get_common_scalar_dtype(otrk__eot)
    if not abkel__fcq:
        raise BodoError(
            "DataFrame.melt(): columns selected in 'value_vars' must have a unifiable type."
            )
    extra_globals = {'np': np, 'value_lit': gvy__gxwj, 'val_type': exuq__knepx}
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
    if frame.is_table_format and all(v == exuq__knepx.dtype for v in otrk__eot
        ):
        extra_globals['value_idxs'] = bodo.utils.typing.MetaType(tuple(
            klw__ljna))
        header += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(frame)\n'
            )
        header += (
            '  val_col = bodo.utils.table_utils.table_concat(table, value_idxs, val_type)\n'
            )
    elif len(gvy__gxwj) == 1:
        header += f"""  val_col = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {klw__ljna[0]})
"""
    else:
        muykt__jrhdz = ', '.join(
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})'
             for i in klw__ljna)
        header += (
            f'  val_col = bodo.libs.array_kernels.concat(({muykt__jrhdz},))\n')
    header += """  var_col = bodo.libs.array_kernels.repeat_like(bodo.utils.conversion.coerce_to_array(value_lit), dummy_id)
"""
    for i in kmohq__smmov:
        header += (
            f'  id{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(frame, {i})\n'
            )
        header += (
            f'  out_id{i} = bodo.libs.array_kernels.concat([id{i}] * {len(gvy__gxwj)})\n'
            )
    xtqs__mxgo = ', '.join(f'out_id{i}' for i in kmohq__smmov) + (', ' if 
        len(kmohq__smmov) > 0 else '')
    data_args = xtqs__mxgo + 'var_col, val_col'
    columns = tuple(mas__neakw + [var_name, value_name])
    index = (
        f'bodo.hiframes.pd_index_ext.init_range_index(0, len(frame) * {len(gvy__gxwj)}, 1, None)'
        )
    return _gen_init_df(header, columns, data_args, index, extra_globals)


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    raise BodoError(f'pandas.crosstab() not supported yet')
    kloot__wclof = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    zna__hxxtt = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', kloot__wclof, zna__hxxtt,
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
    kloot__wclof = dict(ignore_index=ignore_index, key=key)
    zna__hxxtt = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', kloot__wclof,
        zna__hxxtt, package_name='pandas', module_name='DataFrame')
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
    ntj__dll = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        ntj__dll.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        mnom__cossx = [get_overload_const_tuple(by)]
    else:
        mnom__cossx = get_overload_const_list(by)
    mnom__cossx = set((k, '') if (k, '') in ntj__dll else k for k in
        mnom__cossx)
    if len(mnom__cossx.difference(ntj__dll)) > 0:
        hvlaw__svrfv = list(set(get_overload_const_list(by)).difference(
            ntj__dll))
        raise_bodo_error(f'sort_values(): invalid keys {hvlaw__svrfv} for by.')
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
        rgqwj__nczpi = get_overload_const_list(na_position)
        for na_position in rgqwj__nczpi:
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
    kloot__wclof = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    zna__hxxtt = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', kloot__wclof, zna__hxxtt,
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
    jso__cdtez = """def impl(df, axis=0, method='average', numeric_only=None, na_option='keep', ascending=True, pct=False):
"""
    lwfgf__gnm = len(df.columns)
    data_args = ', '.join(
        'bodo.libs.array_kernels.rank(data_{}, method=method, na_option=na_option, ascending=ascending, pct=pct)'
        .format(i) for i in range(lwfgf__gnm))
    for i in range(lwfgf__gnm):
        jso__cdtez += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(jso__cdtez, df.columns, data_args, index)


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    kloot__wclof = dict(limit=limit, downcast=downcast)
    zna__hxxtt = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', kloot__wclof, zna__hxxtt,
        package_name='pandas', module_name='DataFrame')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
        'DataFrame.fillna()')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    ltbta__vesvi = not is_overload_none(value)
    lpt__ahck = not is_overload_none(method)
    if ltbta__vesvi and lpt__ahck:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not ltbta__vesvi and not lpt__ahck:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if ltbta__vesvi:
        jbb__ugiwd = 'value=value'
    else:
        jbb__ugiwd = 'method=method'
    data_args = [(
        f"df['{hmr__zflki}'].fillna({jbb__ugiwd}, inplace=inplace)" if
        isinstance(hmr__zflki, str) else
        f'df[{hmr__zflki}].fillna({jbb__ugiwd}, inplace=inplace)') for
        hmr__zflki in df.columns]
    jso__cdtez = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        jso__cdtez += '  ' + '  \n'.join(data_args) + '\n'
        opek__gkzkt = {}
        exec(jso__cdtez, {}, opek__gkzkt)
        impl = opek__gkzkt['impl']
        return impl
    else:
        return _gen_init_df(jso__cdtez, df.columns, ', '.join(nwnp__yqotm +
            '.values' for nwnp__yqotm in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    kloot__wclof = dict(col_level=col_level, col_fill=col_fill)
    zna__hxxtt = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', kloot__wclof,
        zna__hxxtt, package_name='pandas', module_name='DataFrame')
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
    jso__cdtez = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    jso__cdtez += (
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
        xdnx__gwnyd = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            xdnx__gwnyd)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            jso__cdtez += """  m_index = bodo.hiframes.pd_index_ext.get_index_data(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
            kmqzb__rrf = ['m_index[{}]'.format(i) for i in range(df.index.
                nlevels)]
            data_args = kmqzb__rrf + data_args
        else:
            fzcs__ezhsu = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [fzcs__ezhsu] + data_args
    return _gen_init_df(jso__cdtez, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    zuyt__dma = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and zuyt__dma == 1 or is_overload_constant_list(level) and list(
        get_overload_const_list(level)) == list(range(zuyt__dma))


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
        hhu__qwxi = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        bpg__irqbk = get_overload_const_list(subset)
        hhu__qwxi = []
        for zbk__ckw in bpg__irqbk:
            if zbk__ckw not in df.column_index:
                raise_bodo_error(
                    f"df.dropna(): column '{zbk__ckw}' not in data frame columns {df}"
                    )
            hhu__qwxi.append(df.column_index[zbk__ckw])
    lwfgf__gnm = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(lwfgf__gnm))
    jso__cdtez = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(lwfgf__gnm):
        jso__cdtez += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    jso__cdtez += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in hhu__qwxi)))
    jso__cdtez += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(jso__cdtez, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    kloot__wclof = dict(index=index, level=level, errors=errors)
    zna__hxxtt = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', kloot__wclof, zna__hxxtt,
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
            wmet__dwm = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            wmet__dwm = get_overload_const_list(labels)
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
            wmet__dwm = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            wmet__dwm = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for hmr__zflki in wmet__dwm:
        if hmr__zflki not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(hmr__zflki, df.columns))
    if len(set(wmet__dwm)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    hfq__ppfjx = tuple(hmr__zflki for hmr__zflki in df.columns if 
        hmr__zflki not in wmet__dwm)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.column_index[hmr__zflki], '.copy()' if not inplace else
        '') for hmr__zflki in hfq__ppfjx)
    jso__cdtez = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    jso__cdtez += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(jso__cdtez, hfq__ppfjx, data_args, index)


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
    kloot__wclof = dict(random_state=random_state, weights=weights, axis=
        axis, ignore_index=ignore_index)
    bza__lkldp = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', kloot__wclof, bza__lkldp,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    lwfgf__gnm = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(lwfgf__gnm))
    zyjj__hupl = ', '.join('rhs_data_{}'.format(i) for i in range(lwfgf__gnm))
    jso__cdtez = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    jso__cdtez += '  if (frac == 1 or n == len(df)) and not replace:\n'
    jso__cdtez += (
        '    return bodo.allgatherv(bodo.random_shuffle(df), False)\n')
    for i in range(lwfgf__gnm):
        jso__cdtez += (
            """  rhs_data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})
"""
            .format(i))
    jso__cdtez += '  if frac is None:\n'
    jso__cdtez += '    frac_d = -1.0\n'
    jso__cdtez += '  else:\n'
    jso__cdtez += '    frac_d = frac\n'
    jso__cdtez += '  if n is None:\n'
    jso__cdtez += '    n_i = 0\n'
    jso__cdtez += '  else:\n'
    jso__cdtez += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    jso__cdtez += f"""  ({data_args},), index_arr = bodo.libs.array_kernels.sample_table_operation(({zyjj__hupl},), {index}, n_i, frac_d, replace)
"""
    jso__cdtez += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(jso__cdtez, df.columns,
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
    xxwx__ezvap = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    ymzbh__zmol = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', xxwx__ezvap, ymzbh__zmol,
        package_name='pandas', module_name='DataFrame')
    mpe__dovh = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            bqlz__nyhp = mpe__dovh + '\n'
            bqlz__nyhp += 'Index: 0 entries\n'
            bqlz__nyhp += 'Empty DataFrame'
            print(bqlz__nyhp)
        return _info_impl
    else:
        jso__cdtez = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        jso__cdtez += '    ncols = df.shape[1]\n'
        jso__cdtez += f'    lines = "{mpe__dovh}\\n"\n'
        jso__cdtez += f'    lines += "{df.index}: "\n'
        jso__cdtez += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            jso__cdtez += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            jso__cdtez += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            jso__cdtez += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        jso__cdtez += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        jso__cdtez += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        jso__cdtez += '    column_width = max(space, 7)\n'
        jso__cdtez += '    column= "Column"\n'
        jso__cdtez += '    underl= "------"\n'
        jso__cdtez += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        jso__cdtez += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        jso__cdtez += '    mem_size = 0\n'
        jso__cdtez += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        jso__cdtez += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        jso__cdtez += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        gjggd__qnyxm = dict()
        for i in range(len(df.columns)):
            jso__cdtez += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            mfx__sadgt = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                mfx__sadgt = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                nkw__yel = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                mfx__sadgt = f'{nkw__yel[:-7]}'
            jso__cdtez += f'    col_dtype[{i}] = "{mfx__sadgt}"\n'
            if mfx__sadgt in gjggd__qnyxm:
                gjggd__qnyxm[mfx__sadgt] += 1
            else:
                gjggd__qnyxm[mfx__sadgt] = 1
            jso__cdtez += f'    col_name[{i}] = "{df.columns[i]}"\n'
            jso__cdtez += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        jso__cdtez += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        jso__cdtez += '    for i in column_info:\n'
        jso__cdtez += "        lines += f'{i}\\n'\n"
        tlrk__izw = ', '.join(f'{k}({gjggd__qnyxm[k]})' for k in sorted(
            gjggd__qnyxm))
        jso__cdtez += f"    lines += 'dtypes: {tlrk__izw}\\n'\n"
        jso__cdtez += '    mem_size += df.index.nbytes\n'
        jso__cdtez += '    total_size = _sizeof_fmt(mem_size)\n'
        jso__cdtez += "    lines += f'memory usage: {total_size}'\n"
        jso__cdtez += '    print(lines)\n'
        opek__gkzkt = {}
        exec(jso__cdtez, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, opek__gkzkt)
        _info_impl = opek__gkzkt['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    jso__cdtez = 'def impl(df, index=True, deep=False):\n'
    ywxzl__wph = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes')
    epfox__lrh = is_overload_true(index)
    columns = df.columns
    if epfox__lrh:
        columns = ('Index',) + columns
    if len(columns) == 0:
        pzcmw__msm = ()
    elif all(isinstance(hmr__zflki, int) for hmr__zflki in columns):
        pzcmw__msm = np.array(columns, 'int64')
    elif all(isinstance(hmr__zflki, str) for hmr__zflki in columns):
        pzcmw__msm = pd.array(columns, 'string')
    else:
        pzcmw__msm = columns
    if df.is_table_format and len(df.columns) > 0:
        xae__ekqq = int(epfox__lrh)
        vlxi__rsvvr = len(columns)
        jso__cdtez += f'  nbytes_arr = np.empty({vlxi__rsvvr}, np.int64)\n'
        jso__cdtez += (
            '  table = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)\n'
            )
        jso__cdtez += f"""  bodo.utils.table_utils.generate_table_nbytes(table, nbytes_arr, {xae__ekqq})
"""
        if epfox__lrh:
            jso__cdtez += f'  nbytes_arr[0] = {ywxzl__wph}\n'
        jso__cdtez += f"""  return bodo.hiframes.pd_series_ext.init_series(nbytes_arr, pd.Index(column_vals), None)
"""
    else:
        data = ', '.join(
            f'bodo.libs.array_ops.array_op_nbytes(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        if epfox__lrh:
            data = f'{ywxzl__wph},{data}'
        else:
            wpfw__zdgyv = ',' if len(columns) == 1 else ''
            data = f'{data}{wpfw__zdgyv}'
        jso__cdtez += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}), pd.Index(column_vals), None)
"""
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo, 'np': np, 'pd': pd, 'column_vals':
        pzcmw__msm}, opek__gkzkt)
    impl = opek__gkzkt['impl']
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
    mpjl__llpvb = 'read_excel_df{}'.format(next_label())
    setattr(types, mpjl__llpvb, df_type)
    hvpwy__born = False
    if is_overload_constant_list(parse_dates):
        hvpwy__born = get_overload_const_list(parse_dates)
    bnpul__tbax = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    jso__cdtez = f"""
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
    with numba.objmode(df="{mpjl__llpvb}"):
        df = pd.read_excel(
            io=io,
            sheet_name=sheet_name,
            header=header,
            names={list(df_type.columns)},
            index_col=index_col,
            usecols=usecols,
            squeeze=squeeze,
            dtype={{{bnpul__tbax}}},
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
            parse_dates={hvpwy__born},
            date_parser=date_parser,
            thousands=thousands,
            comment=comment,
            skipfooter=skipfooter,
            convert_float=convert_float,
            mangle_dupe_cols=mangle_dupe_cols,
        )
    return df
"""
    opek__gkzkt = {}
    exec(jso__cdtez, globals(), opek__gkzkt)
    impl = opek__gkzkt['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as oiyu__rdix:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    jso__cdtez = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    jso__cdtez += '    ylabel=None, title=None, legend=True, fontsize=None, \n'
    jso__cdtez += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        jso__cdtez += '   fig, ax = plt.subplots()\n'
    else:
        jso__cdtez += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        jso__cdtez += '   fig.set_figwidth(figsize[0])\n'
        jso__cdtez += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        jso__cdtez += '   xlabel = x\n'
    jso__cdtez += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        jso__cdtez += '   ylabel = y\n'
    else:
        jso__cdtez += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        jso__cdtez += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        jso__cdtez += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    jso__cdtez += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            jso__cdtez += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            idvxu__btg = get_overload_const_str(x)
            nqk__fja = df.columns.index(idvxu__btg)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if nqk__fja != i:
                        jso__cdtez += (
                            f'   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])\n'
                            )
        else:
            jso__cdtez += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        jso__cdtez += '   ax.scatter(df[x], df[y], s=20)\n'
        jso__cdtez += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        jso__cdtez += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        jso__cdtez += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        jso__cdtez += '   ax.legend()\n'
    jso__cdtez += '   return ax\n'
    opek__gkzkt = {}
    exec(jso__cdtez, {'bodo': bodo, 'plt': plt}, opek__gkzkt)
    impl = opek__gkzkt['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for aer__jgte in df_typ.data:
        if not (isinstance(aer__jgte, IntegerArrayType) or isinstance(
            aer__jgte.dtype, types.Number) or aer__jgte.dtype in (bodo.
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
        cnvyb__lladd = args[0]
        kvy__vne = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        jwvkp__hybzg = cnvyb__lladd
        check_runtime_cols_unsupported(cnvyb__lladd, 'set_df_col()')
        if isinstance(cnvyb__lladd, DataFrameType):
            index = cnvyb__lladd.index
            if len(cnvyb__lladd.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(cnvyb__lladd.columns) == 0:
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
            if kvy__vne in cnvyb__lladd.columns:
                hfq__ppfjx = cnvyb__lladd.columns
                flwpg__fksi = cnvyb__lladd.columns.index(kvy__vne)
                pfo__rbrf = list(cnvyb__lladd.data)
                pfo__rbrf[flwpg__fksi] = val
                pfo__rbrf = tuple(pfo__rbrf)
            else:
                hfq__ppfjx = cnvyb__lladd.columns + (kvy__vne,)
                pfo__rbrf = cnvyb__lladd.data + (val,)
            jwvkp__hybzg = DataFrameType(pfo__rbrf, index, hfq__ppfjx,
                cnvyb__lladd.dist, cnvyb__lladd.is_table_format)
        return jwvkp__hybzg(*args)


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
        geg__ahua = args[0]
        assert isinstance(geg__ahua, DataFrameType) and len(geg__ahua.columns
            ) > 0, 'Error while typechecking __bodosql_replace_columns_dummy: we should only generate a call __bodosql_replace_columns_dummy if the input dataframe'
        col_names_to_replace = get_overload_const_tuple(args[1])
        lxcz__ylhp = args[2]
        assert len(col_names_to_replace) == len(lxcz__ylhp
            ), 'Error while typechecking __bodosql_replace_columns_dummy: the tuple of column indicies to replace should be equal to the number of columns to replace them with'
        assert len(col_names_to_replace) <= len(geg__ahua.columns
            ), 'Error while typechecking __bodosql_replace_columns_dummy: The number of indicies provided should be less than or equal to the number of columns in the input dataframe'
        for col_name in col_names_to_replace:
            assert col_name in geg__ahua.columns, 'Error while typechecking __bodosql_replace_columns_dummy: All columns specified to be replaced should already be present in input dataframe'
        check_runtime_cols_unsupported(geg__ahua,
            '__bodosql_replace_columns_dummy()')
        index = geg__ahua.index
        hfq__ppfjx = geg__ahua.columns
        pfo__rbrf = list(geg__ahua.data)
        for i in range(len(col_names_to_replace)):
            col_name = col_names_to_replace[i]
            okwrf__ymgi = lxcz__ylhp[i]
            assert isinstance(okwrf__ymgi, SeriesType
                ), 'Error while typechecking __bodosql_replace_columns_dummy: the values to replace the columns with are expected to be series'
            if isinstance(okwrf__ymgi, SeriesType):
                okwrf__ymgi = okwrf__ymgi.data
            byrma__fnslg = geg__ahua.column_index[col_name]
            pfo__rbrf[byrma__fnslg] = okwrf__ymgi
        pfo__rbrf = tuple(pfo__rbrf)
        jwvkp__hybzg = DataFrameType(pfo__rbrf, index, hfq__ppfjx,
            geg__ahua.dist, geg__ahua.is_table_format)
        return jwvkp__hybzg(*args)


BodoSQLReplaceColsInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    zbe__pecw = {}

    def _rewrite_membership_op(self, node, left, right):
        czh__pxzlc = node.op
        op = self.visit(czh__pxzlc)
        return op, czh__pxzlc, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    vmmo__bzbwu = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in vmmo__bzbwu:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in vmmo__bzbwu:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        vsw__mdv = node.attr
        value = node.value
        gmgur__fzuv = pd.core.computation.ops.LOCAL_TAG
        if vsw__mdv in ('str', 'dt'):
            try:
                ztj__kof = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as lgqx__rinj:
                col_name = lgqx__rinj.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            ztj__kof = str(self.visit(value))
        jckc__rje = ztj__kof, vsw__mdv
        if jckc__rje in join_cleaned_cols:
            vsw__mdv = join_cleaned_cols[jckc__rje]
        name = ztj__kof + '.' + vsw__mdv
        if name.startswith(gmgur__fzuv):
            name = name[len(gmgur__fzuv):]
        if vsw__mdv in ('str', 'dt'):
            tnq__xopb = columns[cleaned_columns.index(ztj__kof)]
            zbe__pecw[tnq__xopb] = ztj__kof
            self.env.scope[name] = 0
            return self.term_type(gmgur__fzuv + name, self.env)
        vmmo__bzbwu.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in vmmo__bzbwu:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        xam__iac = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        kvy__vne = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(xam__iac), kvy__vne))

    def op__str__(self):
        yvqqj__agfoq = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            ewb__lossm)) for ewb__lossm in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(yvqqj__agfoq)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(yvqqj__agfoq)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(yvqqj__agfoq))
    wwp__dly = pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op
    kfm__ewob = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    yhc__ywog = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    fcza__aqhev = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    ltmu__maqs = pd.core.computation.ops.Term.__str__
    ukd__cms = pd.core.computation.ops.MathCall.__str__
    fyuy__equeu = pd.core.computation.ops.Op.__str__
    mcnd__amwf = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        xrpyr__sfc = pd.core.computation.expr.Expr(expr, env=env)
        ixzys__lplwq = str(xrpyr__sfc)
    except pd.core.computation.ops.UndefinedVariableError as lgqx__rinj:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == lgqx__rinj.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {lgqx__rinj}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            wwp__dly)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            kfm__ewob)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = yhc__ywog
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = fcza__aqhev
        pd.core.computation.ops.Term.__str__ = ltmu__maqs
        pd.core.computation.ops.MathCall.__str__ = ukd__cms
        pd.core.computation.ops.Op.__str__ = fyuy__equeu
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            mcnd__amwf)
    gupd__kcsjl = pd.core.computation.parsing.clean_column_name
    zbe__pecw.update({hmr__zflki: gupd__kcsjl(hmr__zflki) for hmr__zflki in
        columns if gupd__kcsjl(hmr__zflki) in xrpyr__sfc.names})
    return xrpyr__sfc, ixzys__lplwq, zbe__pecw


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        olfh__fvqh = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(olfh__fvqh))
        skwjk__dmr = namedtuple('Pandas', col_names)
        hku__biu = types.NamedTuple([_get_series_dtype(a) for a in arr_typs
            ], skwjk__dmr)
        super(DataFrameTupleIterator, self).__init__(name, hku__biu)

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
        fvvpb__ogdfa = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        fvvpb__ogdfa = [types.Array(types.int64, 1, 'C')] + fvvpb__ogdfa
        vdup__jovxy = DataFrameTupleIterator(col_names, fvvpb__ogdfa)
        return vdup__jovxy(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rlcn__evqob = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            rlcn__evqob)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    acfx__uvfrm = args[len(args) // 2:]
    txql__icj = sig.args[len(sig.args) // 2:]
    fvfgp__eme = context.make_helper(builder, sig.return_type)
    mpmhh__ees = context.get_constant(types.intp, 0)
    cnmv__yut = cgutils.alloca_once_value(builder, mpmhh__ees)
    fvfgp__eme.index = cnmv__yut
    for i, arr in enumerate(acfx__uvfrm):
        setattr(fvfgp__eme, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(acfx__uvfrm, txql__icj):
        context.nrt.incref(builder, arr_typ, arr)
    res = fvfgp__eme._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    bmj__uba, = sig.args
    qdx__njb, = args
    fvfgp__eme = context.make_helper(builder, bmj__uba, value=qdx__njb)
    vvqa__czgw = signature(types.intp, bmj__uba.array_types[1])
    saqbr__brav = context.compile_internal(builder, lambda a: len(a),
        vvqa__czgw, [fvfgp__eme.array0])
    index = builder.load(fvfgp__eme.index)
    vzv__jasnk = builder.icmp_signed('<', index, saqbr__brav)
    result.set_valid(vzv__jasnk)
    with builder.if_then(vzv__jasnk):
        values = [index]
        for i, arr_typ in enumerate(bmj__uba.array_types[1:]):
            yxd__ero = getattr(fvfgp__eme, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                mwk__sju = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    mwk__sju, [yxd__ero, index])
            else:
                mwk__sju = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    mwk__sju, [yxd__ero, index])
            values.append(val)
        value = context.make_tuple(builder, bmj__uba.yield_type, values)
        result.yield_(value)
        cmzw__olvav = cgutils.increment_index(builder, index)
        builder.store(cmzw__olvav, fvfgp__eme.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    cee__ajo = ir.Assign(rhs, lhs, expr.loc)
    jodi__rmr = lhs
    wurf__ris = []
    woop__zqal = []
    byt__isas = typ.count
    for i in range(byt__isas):
        ziomm__fqwy = ir.Var(jodi__rmr.scope, mk_unique_var('{}_size{}'.
            format(jodi__rmr.name, i)), jodi__rmr.loc)
        hbo__xyn = ir.Expr.static_getitem(lhs, i, None, jodi__rmr.loc)
        self.calltypes[hbo__xyn] = None
        wurf__ris.append(ir.Assign(hbo__xyn, ziomm__fqwy, jodi__rmr.loc))
        self._define(equiv_set, ziomm__fqwy, types.intp, hbo__xyn)
        woop__zqal.append(ziomm__fqwy)
    fflt__oyivo = tuple(woop__zqal)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        fflt__oyivo, pre=[cee__ajo] + wurf__ris)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
