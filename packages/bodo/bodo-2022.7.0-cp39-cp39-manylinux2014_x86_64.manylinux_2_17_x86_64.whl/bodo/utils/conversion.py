"""
Utility functions for conversion of data such as list to array.
Need to be inlined for better optimization.
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.binary_arr_ext import bytes_type
from bodo.libs.bool_arr_ext import boolean_dtype
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.nullable_tuple_ext import NullableTupleType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_list, get_overload_const_str, is_heterogeneous_tuple_type, is_np_arr_typ, is_overload_constant_list, is_overload_constant_str, is_overload_none, is_overload_true, is_str_arr_type, to_nullable_type, unwrap_typeref
NS_DTYPE = np.dtype('M8[ns]')
TD_DTYPE = np.dtype('m8[ns]')


def coerce_to_ndarray(data, error_on_nonarray=True, use_nullable_array=None,
    scalar_to_arr_len=None):
    return data


@overload(coerce_to_ndarray)
def overload_coerce_to_ndarray(data, error_on_nonarray=True,
    use_nullable_array=None, scalar_to_arr_len=None):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, RangeIndexType, TimedeltaIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    data = types.unliteral(data)
    if isinstance(data, types.Optional) and bodo.utils.typing.is_scalar_type(
        data.type):
        data = data.type
        use_nullable_array = True
    if isinstance(data, bodo.libs.int_arr_ext.IntegerArrayType
        ) and not is_overload_none(use_nullable_array):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.int_arr_ext.
            get_int_arr_data(data))
    if data == bodo.libs.bool_arr_ext.boolean_array and not is_overload_none(
        use_nullable_array):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.bool_arr_ext.
            get_bool_arr_data(data))
    if isinstance(data, types.Array):
        if not is_overload_none(use_nullable_array) and isinstance(data.
            dtype, (types.Boolean, types.Integer)):
            if data.dtype == types.bool_:
                if data.layout != 'C':
                    return (lambda data, error_on_nonarray=True,
                        use_nullable_array=None, scalar_to_arr_len=None:
                        bodo.libs.bool_arr_ext.init_bool_array(np.
                        ascontiguousarray(data), np.full(len(data) + 7 >> 3,
                        255, np.uint8)))
                else:
                    return (lambda data, error_on_nonarray=True,
                        use_nullable_array=None, scalar_to_arr_len=None:
                        bodo.libs.bool_arr_ext.init_bool_array(data, np.
                        full(len(data) + 7 >> 3, 255, np.uint8)))
            elif data.layout != 'C':
                return (lambda data, error_on_nonarray=True,
                    use_nullable_array=None, scalar_to_arr_len=None: bodo.
                    libs.int_arr_ext.init_integer_array(np.
                    ascontiguousarray(data), np.full(len(data) + 7 >> 3, 
                    255, np.uint8)))
            else:
                return (lambda data, error_on_nonarray=True,
                    use_nullable_array=None, scalar_to_arr_len=None: bodo.
                    libs.int_arr_ext.init_integer_array(data, np.full(len(
                    data) + 7 >> 3, 255, np.uint8)))
        if data.layout != 'C':
            return (lambda data, error_on_nonarray=True, use_nullable_array
                =None, scalar_to_arr_len=None: np.ascontiguousarray(data))
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if isinstance(data, (types.List, types.UniTuple)):
        erzem__ugv = data.dtype
        if isinstance(erzem__ugv, types.Optional):
            erzem__ugv = erzem__ugv.type
            if bodo.utils.typing.is_scalar_type(erzem__ugv):
                use_nullable_array = True
        if isinstance(erzem__ugv, (types.Boolean, types.Integer,
            Decimal128Type)) or erzem__ugv in [bodo.hiframes.
            pd_timestamp_ext.pd_timestamp_type, bodo.hiframes.
            datetime_date_ext.datetime_date_type, bodo.hiframes.
            datetime_timedelta_ext.datetime_timedelta_type]:
            upl__xog = dtype_to_array_type(erzem__ugv)
            if not is_overload_none(use_nullable_array):
                upl__xog = to_nullable_type(upl__xog)

            def impl(data, error_on_nonarray=True, use_nullable_array=None,
                scalar_to_arr_len=None):
                jcu__hnrn = len(data)
                A = bodo.utils.utils.alloc_type(jcu__hnrn, upl__xog, (-1,))
                bodo.utils.utils.tuple_list_to_array(A, data, erzem__ugv)
                return A
            return impl
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.asarray(data))
    if isinstance(data, SeriesType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_series_ext.
            get_series_data(data))
    if isinstance(data, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_index_ext.
            get_index_data(data))
    if isinstance(data, RangeIndexType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.arange(data._start, data._stop,
            data._step))
    if isinstance(data, types.RangeType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.arange(data.start, data.stop,
            data.step))
    if not is_overload_none(scalar_to_arr_len):
        if isinstance(data, Decimal128Type):
            rij__naulj = data.precision
            ljxm__nolk = data.scale

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                jcu__hnrn = scalar_to_arr_len
                A = bodo.libs.decimal_arr_ext.alloc_decimal_array(jcu__hnrn,
                    rij__naulj, ljxm__nolk)
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    A[jklg__yghss] = data
                return A
            return impl_ts
        if data == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:
            bbzgp__dus = np.dtype('datetime64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                jcu__hnrn = scalar_to_arr_len
                A = np.empty(jcu__hnrn, bbzgp__dus)
                bdn__lrf = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(data))
                fqxg__phn = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    bdn__lrf)
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    A[jklg__yghss] = fqxg__phn
                return A
            return impl_ts
        if (data == bodo.hiframes.datetime_timedelta_ext.
            datetime_timedelta_type):
            cwrf__dpmep = np.dtype('timedelta64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                jcu__hnrn = scalar_to_arr_len
                A = np.empty(jcu__hnrn, cwrf__dpmep)
                vcsbr__lqjcq = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(data))
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    A[jklg__yghss] = vcsbr__lqjcq
                return A
            return impl_ts
        if data == bodo.hiframes.datetime_date_ext.datetime_date_type:

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                jcu__hnrn = scalar_to_arr_len
                A = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
                    jcu__hnrn)
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    A[jklg__yghss] = data
                return A
            return impl_ts
        if data == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            bbzgp__dus = np.dtype('datetime64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                jcu__hnrn = scalar_to_arr_len
                A = np.empty(scalar_to_arr_len, bbzgp__dus)
                bdn__lrf = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(data
                    .value)
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    A[jklg__yghss] = bdn__lrf
                return A
            return impl_ts
        dtype = types.unliteral(data)
        if not is_overload_none(use_nullable_array) and isinstance(dtype,
            types.Integer):

            def impl_null_integer(data, error_on_nonarray=True,
                use_nullable_array=None, scalar_to_arr_len=None):
                numba.parfors.parfor.init_prange()
                jcu__hnrn = scalar_to_arr_len
                qysf__oovzk = bodo.libs.int_arr_ext.alloc_int_array(jcu__hnrn,
                    dtype)
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    qysf__oovzk[jklg__yghss] = data
                return qysf__oovzk
            return impl_null_integer
        if not is_overload_none(use_nullable_array) and dtype == types.bool_:

            def impl_null_bool(data, error_on_nonarray=True,
                use_nullable_array=None, scalar_to_arr_len=None):
                numba.parfors.parfor.init_prange()
                jcu__hnrn = scalar_to_arr_len
                qysf__oovzk = bodo.libs.bool_arr_ext.alloc_bool_array(jcu__hnrn
                    )
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    qysf__oovzk[jklg__yghss] = data
                return qysf__oovzk
            return impl_null_bool

        def impl_num(data, error_on_nonarray=True, use_nullable_array=None,
            scalar_to_arr_len=None):
            numba.parfors.parfor.init_prange()
            jcu__hnrn = scalar_to_arr_len
            qysf__oovzk = np.empty(jcu__hnrn, dtype)
            for jklg__yghss in numba.parfors.parfor.internal_prange(jcu__hnrn):
                qysf__oovzk[jklg__yghss] = data
            return qysf__oovzk
        return impl_num
    if isinstance(data, types.BaseTuple) and all(isinstance(hht__dan, (
        types.Float, types.Integer)) for hht__dan in data.types):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: np.array(data))
    if bodo.utils.utils.is_array_typ(data, False):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if is_overload_true(error_on_nonarray):
        raise BodoError(f'cannot coerce {data} to array')
    return (lambda data, error_on_nonarray=True, use_nullable_array=None,
        scalar_to_arr_len=None: data)


def coerce_scalar_to_array(scalar, length, arr_type):
    pass


@overload(coerce_scalar_to_array)
def overload_coerce_scalar_to_array(scalar, length, arr_type):
    tkx__jhtcb = to_nullable_type(unwrap_typeref(arr_type))
    if scalar == types.none:

        def impl(scalar, length, arr_type):
            return bodo.libs.array_kernels.gen_na_array(length, tkx__jhtcb,
                True)
    elif isinstance(scalar, types.Optional):

        def impl(scalar, length, arr_type):
            if scalar is None:
                return bodo.libs.array_kernels.gen_na_array(length,
                    tkx__jhtcb, True)
            else:
                return bodo.utils.conversion.coerce_to_array(bodo.utils.
                    indexing.unoptional(scalar), True, True, length)
    else:

        def impl(scalar, length, arr_type):
            return bodo.utils.conversion.coerce_to_array(scalar, True, None,
                length)
    return impl


def coerce_to_array(data, error_on_nonarray=True, use_nullable_array=None,
    scalar_to_arr_len=None):
    return data


@overload(coerce_to_array, no_unliteral=True)
def overload_coerce_to_array(data, error_on_nonarray=True,
    use_nullable_array=None, scalar_to_arr_len=None):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, StringIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    data = types.unliteral(data)
    if isinstance(data, types.Optional) and bodo.utils.typing.is_scalar_type(
        data.type):
        data = data.type
        use_nullable_array = True
    if isinstance(data, SeriesType):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_series_ext.
            get_series_data(data))
    if isinstance(data, (StringIndexType, BinaryIndexType,
        CategoricalIndexType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.hiframes.pd_index_ext.
            get_index_data(data))
    if isinstance(data, types.List) and data.dtype in (bodo.string_type,
        bodo.bytes_type):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            str_arr_from_sequence(data))
    if isinstance(data, types.BaseTuple) and data.count == 0:
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            empty_str_arr(data))
    if isinstance(data, types.UniTuple) and isinstance(data.dtype, (types.
        UnicodeType, types.StringLiteral)) or isinstance(data, types.BaseTuple
        ) and all(isinstance(hht__dan, types.StringLiteral) for hht__dan in
        data.types):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: bodo.libs.str_arr_ext.
            str_arr_from_sequence(data))
    if data in (bodo.string_array_type, bodo.dict_str_arr_type, bodo.
        binary_array_type, bodo.libs.bool_arr_ext.boolean_array, bodo.
        hiframes.datetime_date_ext.datetime_date_array_type, bodo.hiframes.
        datetime_timedelta_ext.datetime_timedelta_array_type, bodo.hiframes
        .split_impl.string_array_split_view_type) or isinstance(data, (bodo
        .libs.int_arr_ext.IntegerArrayType, DecimalArrayType, bodo.libs.
        interval_arr_ext.IntervalArrayType, bodo.libs.tuple_arr_ext.
        TupleArrayType, bodo.libs.struct_arr_ext.StructArrayType, bodo.
        hiframes.pd_categorical_ext.CategoricalArrayType, bodo.libs.
        csr_matrix_ext.CSRMatrixType, bodo.DatetimeArrayType)):
        return (lambda data, error_on_nonarray=True, use_nullable_array=
            None, scalar_to_arr_len=None: data)
    if isinstance(data, (types.List, types.UniTuple)) and isinstance(data.
        dtype, types.BaseTuple):
        pfx__rzrs = tuple(dtype_to_array_type(hht__dan) for hht__dan in
            data.dtype.types)

        def impl_tuple_list(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            jcu__hnrn = len(data)
            arr = bodo.libs.tuple_arr_ext.pre_alloc_tuple_array(jcu__hnrn,
                (-1,), pfx__rzrs)
            for jklg__yghss in range(jcu__hnrn):
                arr[jklg__yghss] = data[jklg__yghss]
            return arr
        return impl_tuple_list
    if isinstance(data, types.List) and (bodo.utils.utils.is_array_typ(data
        .dtype, False) or isinstance(data.dtype, types.List)):
        oeuf__tpa = dtype_to_array_type(data.dtype.dtype)

        def impl_array_item_arr(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            jcu__hnrn = len(data)
            einwf__cupwq = init_nested_counts(oeuf__tpa)
            for jklg__yghss in range(jcu__hnrn):
                epat__msgik = bodo.utils.conversion.coerce_to_array(data[
                    jklg__yghss], use_nullable_array=True)
                einwf__cupwq = add_nested_counts(einwf__cupwq, epat__msgik)
            qysf__oovzk = (bodo.libs.array_item_arr_ext.
                pre_alloc_array_item_array(jcu__hnrn, einwf__cupwq, oeuf__tpa))
            dcy__ktooo = bodo.libs.array_item_arr_ext.get_null_bitmap(
                qysf__oovzk)
            for apwze__cki in range(jcu__hnrn):
                epat__msgik = bodo.utils.conversion.coerce_to_array(data[
                    apwze__cki], use_nullable_array=True)
                qysf__oovzk[apwze__cki] = epat__msgik
                bodo.libs.int_arr_ext.set_bit_to_arr(dcy__ktooo, apwze__cki, 1)
            return qysf__oovzk
        return impl_array_item_arr
    if not is_overload_none(scalar_to_arr_len) and isinstance(data, (types.
        UnicodeType, types.StringLiteral)):

        def impl_str(data, error_on_nonarray=True, use_nullable_array=None,
            scalar_to_arr_len=None):
            jcu__hnrn = scalar_to_arr_len
            yefoa__keydx = bodo.libs.str_arr_ext.str_arr_from_sequence([data])
            djrs__mmly = bodo.libs.int_arr_ext.alloc_int_array(jcu__hnrn,
                np.int32)
            numba.parfors.parfor.init_prange()
            for jklg__yghss in numba.parfors.parfor.internal_prange(jcu__hnrn):
                djrs__mmly[jklg__yghss] = 0
            A = bodo.libs.dict_arr_ext.init_dict_arr(yefoa__keydx,
                djrs__mmly, True)
            return A
        return impl_str
    if isinstance(data, types.List) and isinstance(data.dtype, bodo.
        hiframes.pd_timestamp_ext.PandasTimestampType):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
            'coerce_to_array()')

        def impl_list_timestamp(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            jcu__hnrn = len(data)
            A = np.empty(jcu__hnrn, np.dtype('datetime64[ns]'))
            for jklg__yghss in range(jcu__hnrn):
                A[jklg__yghss
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(data
                    [jklg__yghss].value)
            return A
        return impl_list_timestamp
    if isinstance(data, types.List) and data.dtype == bodo.pd_timedelta_type:

        def impl_list_timedelta(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            jcu__hnrn = len(data)
            A = np.empty(jcu__hnrn, np.dtype('timedelta64[ns]'))
            for jklg__yghss in range(jcu__hnrn):
                A[jklg__yghss
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    data[jklg__yghss].value)
            return A
        return impl_list_timedelta
    if isinstance(data, bodo.hiframes.pd_timestamp_ext.PandasTimestampType):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
            'coerce_to_array()')
    if not is_overload_none(scalar_to_arr_len) and data in [bodo.
        pd_timestamp_type, bodo.pd_timedelta_type]:
        jca__dcj = ('datetime64[ns]' if data == bodo.pd_timestamp_type else
            'timedelta64[ns]')

        def impl_timestamp(data, error_on_nonarray=True, use_nullable_array
            =None, scalar_to_arr_len=None):
            jcu__hnrn = scalar_to_arr_len
            A = np.empty(jcu__hnrn, jca__dcj)
            data = bodo.utils.conversion.unbox_if_timestamp(data)
            for jklg__yghss in numba.parfors.parfor.internal_prange(jcu__hnrn):
                A[jklg__yghss] = data
            return A
        return impl_timestamp
    return (lambda data, error_on_nonarray=True, use_nullable_array=None,
        scalar_to_arr_len=None: bodo.utils.conversion.coerce_to_ndarray(
        data, error_on_nonarray, use_nullable_array, scalar_to_arr_len))


def _is_str_dtype(dtype):
    return isinstance(dtype, bodo.libs.str_arr_ext.StringDtype) or isinstance(
        dtype, types.Function) and dtype.key[0
        ] == str or is_overload_constant_str(dtype) and get_overload_const_str(
        dtype) == 'str' or isinstance(dtype, types.TypeRef
        ) and dtype.instance_type == types.unicode_type


def fix_arr_dtype(data, new_dtype, copy=None, nan_to_str=True, from_series=
    False):
    return data


@overload(fix_arr_dtype, no_unliteral=True)
def overload_fix_arr_dtype(data, new_dtype, copy=None, nan_to_str=True,
    from_series=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'fix_arr_dtype()')
    vpayz__yampl = is_overload_true(copy)
    nfanv__gvdu = is_overload_constant_str(new_dtype
        ) and get_overload_const_str(new_dtype) == 'object'
    if is_overload_none(new_dtype) or nfanv__gvdu:
        if vpayz__yampl:
            return (lambda data, new_dtype, copy=None, nan_to_str=True,
                from_series=False: data.copy())
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data)
    if isinstance(data, NullableTupleType):
        nb_dtype = bodo.utils.typing.parse_dtype(new_dtype)
        if isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype):
            nb_dtype = nb_dtype.dtype
        mrzm__twobz = {types.unicode_type: '', boolean_dtype: False, types.
            bool_: False, types.int8: np.int8(0), types.int16: np.int16(0),
            types.int32: np.int32(0), types.int64: np.int64(0), types.uint8:
            np.uint8(0), types.uint16: np.uint16(0), types.uint32: np.
            uint32(0), types.uint64: np.uint64(0), types.float32: np.
            float32(0), types.float64: np.float64(0), bodo.datetime64ns: pd
            .Timestamp(0), bodo.timedelta64ns: pd.Timedelta(0)}
        wdg__ylqx = {types.unicode_type: str, types.bool_: bool,
            boolean_dtype: bool, types.int8: np.int8, types.int16: np.int16,
            types.int32: np.int32, types.int64: np.int64, types.uint8: np.
            uint8, types.uint16: np.uint16, types.uint32: np.uint32, types.
            uint64: np.uint64, types.float32: np.float32, types.float64: np
            .float64, bodo.datetime64ns: pd.to_datetime, bodo.timedelta64ns:
            pd.to_timedelta}
        dpck__prui = mrzm__twobz.keys()
        eif__udt = list(data._tuple_typ.types)
        if nb_dtype not in dpck__prui:
            raise BodoError(f'type conversion to {nb_dtype} types unsupported.'
                )
        for ogb__qnxf in eif__udt:
            if ogb__qnxf == bodo.datetime64ns:
                if nb_dtype not in (types.unicode_type, types.int64, types.
                    uint64, bodo.datetime64ns):
                    raise BodoError(
                        f'invalid type conversion from {ogb__qnxf} to {nb_dtype}.'
                        )
            elif ogb__qnxf == bodo.timedelta64ns:
                if nb_dtype not in (types.unicode_type, types.int64, types.
                    uint64, bodo.timedelta64ns):
                    raise BodoError(
                        f'invalid type conversion from {ogb__qnxf} to {nb_dtype}.'
                        )
        sahmq__vulm = (
            'def impl(data, new_dtype, copy=None, nan_to_str=True, from_series=False):\n'
            )
        sahmq__vulm += '  data_tup = data._data\n'
        sahmq__vulm += '  null_tup = data._null_values\n'
        for jklg__yghss in range(len(eif__udt)):
            sahmq__vulm += (
                f'  val_{jklg__yghss} = convert_func(default_value)\n')
            sahmq__vulm += f'  if not null_tup[{jklg__yghss}]:\n'
            sahmq__vulm += (
                f'    val_{jklg__yghss} = convert_func(data_tup[{jklg__yghss}])\n'
                )
        tola__dhaga = ', '.join(f'val_{jklg__yghss}' for jklg__yghss in
            range(len(eif__udt)))
        sahmq__vulm += f'  vals_tup = ({tola__dhaga},)\n'
        sahmq__vulm += """  res_tup = bodo.libs.nullable_tuple_ext.build_nullable_tuple(vals_tup, null_tup)
"""
        sahmq__vulm += '  return res_tup\n'
        rhsjz__ohc = {}
        xvf__lzfar = wdg__ylqx[nb_dtype]
        smyr__pxn = mrzm__twobz[nb_dtype]
        exec(sahmq__vulm, {'bodo': bodo, 'np': np, 'pd': pd,
            'default_value': smyr__pxn, 'convert_func': xvf__lzfar}, rhsjz__ohc
            )
        impl = rhsjz__ohc['impl']
        return impl
    if _is_str_dtype(new_dtype):
        if isinstance(data.dtype, types.Integer):

            def impl_int_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                jcu__hnrn = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(jcu__hnrn, -1)
                for qsa__ahat in numba.parfors.parfor.internal_prange(jcu__hnrn
                    ):
                    if bodo.libs.array_kernels.isna(data, qsa__ahat):
                        if nan_to_str:
                            bodo.libs.str_arr_ext.str_arr_setitem_NA_str(A,
                                qsa__ahat)
                        else:
                            bodo.libs.array_kernels.setna(A, qsa__ahat)
                    else:
                        bodo.libs.str_arr_ext.str_arr_setitem_int_to_str(A,
                            qsa__ahat, data[qsa__ahat])
                return A
            return impl_int_str
        if data.dtype == bytes_type:

            def impl_binary(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                jcu__hnrn = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(jcu__hnrn, -1)
                for qsa__ahat in numba.parfors.parfor.internal_prange(jcu__hnrn
                    ):
                    if bodo.libs.array_kernels.isna(data, qsa__ahat):
                        bodo.libs.array_kernels.setna(A, qsa__ahat)
                    else:
                        A[qsa__ahat] = ''.join([chr(zzi__gatkf) for
                            zzi__gatkf in data[qsa__ahat]])
                return A
            return impl_binary
        if is_overload_true(from_series) and data.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns):

            def impl_str_dt_series(data, new_dtype, copy=None, nan_to_str=
                True, from_series=False):
                numba.parfors.parfor.init_prange()
                jcu__hnrn = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(jcu__hnrn, -1)
                for qsa__ahat in numba.parfors.parfor.internal_prange(jcu__hnrn
                    ):
                    if bodo.libs.array_kernels.isna(data, qsa__ahat):
                        if nan_to_str:
                            A[qsa__ahat] = 'NaT'
                        else:
                            bodo.libs.array_kernels.setna(A, qsa__ahat)
                        continue
                    A[qsa__ahat] = str(box_if_dt64(data[qsa__ahat]))
                return A
            return impl_str_dt_series
        else:

            def impl_str_array(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                jcu__hnrn = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(jcu__hnrn, -1)
                for qsa__ahat in numba.parfors.parfor.internal_prange(jcu__hnrn
                    ):
                    if bodo.libs.array_kernels.isna(data, qsa__ahat):
                        if nan_to_str:
                            A[qsa__ahat] = 'nan'
                        else:
                            bodo.libs.array_kernels.setna(A, qsa__ahat)
                        continue
                    A[qsa__ahat] = str(data[qsa__ahat])
                return A
            return impl_str_array
    if isinstance(new_dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):

        def impl_cat_dtype(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            jcu__hnrn = len(data)
            numba.parfors.parfor.init_prange()
            bjz__mcqpg = (bodo.hiframes.pd_categorical_ext.
                get_label_dict_from_categories(new_dtype.categories.values))
            A = bodo.hiframes.pd_categorical_ext.alloc_categorical_array(
                jcu__hnrn, new_dtype)
            vdi__igsks = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A))
            for jklg__yghss in numba.parfors.parfor.internal_prange(jcu__hnrn):
                if bodo.libs.array_kernels.isna(data, jklg__yghss):
                    bodo.libs.array_kernels.setna(A, jklg__yghss)
                    continue
                val = data[jklg__yghss]
                if val not in bjz__mcqpg:
                    bodo.libs.array_kernels.setna(A, jklg__yghss)
                    continue
                vdi__igsks[jklg__yghss] = bjz__mcqpg[val]
            return A
        return impl_cat_dtype
    if is_overload_constant_str(new_dtype) and get_overload_const_str(new_dtype
        ) == 'category':

        def impl_category(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            wmx__zuhgd = bodo.libs.array_kernels.unique(data, dropna=True)
            wmx__zuhgd = pd.Series(wmx__zuhgd).sort_values().values
            wmx__zuhgd = bodo.allgatherv(wmx__zuhgd, False)
            egf__qthyw = bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo
                .utils.conversion.index_from_array(wmx__zuhgd, None), False,
                None, None)
            jcu__hnrn = len(data)
            numba.parfors.parfor.init_prange()
            bjz__mcqpg = (bodo.hiframes.pd_categorical_ext.
                get_label_dict_from_categories_no_duplicates(wmx__zuhgd))
            A = bodo.hiframes.pd_categorical_ext.alloc_categorical_array(
                jcu__hnrn, egf__qthyw)
            vdi__igsks = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A))
            for jklg__yghss in numba.parfors.parfor.internal_prange(jcu__hnrn):
                if bodo.libs.array_kernels.isna(data, jklg__yghss):
                    bodo.libs.array_kernels.setna(A, jklg__yghss)
                    continue
                val = data[jklg__yghss]
                vdi__igsks[jklg__yghss] = bjz__mcqpg[val]
            return A
        return impl_category
    nb_dtype = bodo.utils.typing.parse_dtype(new_dtype)
    if isinstance(data, bodo.libs.int_arr_ext.IntegerArrayType):
        wxgoc__oise = isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype
            ) and data.dtype == nb_dtype.dtype
    else:
        wxgoc__oise = data.dtype == nb_dtype
    if vpayz__yampl and wxgoc__oise:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data.copy())
    if wxgoc__oise:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data)
    if isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype):
        if isinstance(nb_dtype, types.Integer):
            jca__dcj = nb_dtype
        else:
            jca__dcj = nb_dtype.dtype
        if isinstance(data.dtype, types.Float):

            def impl_float(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                jcu__hnrn = len(data)
                numba.parfors.parfor.init_prange()
                axg__tuegy = bodo.libs.int_arr_ext.alloc_int_array(jcu__hnrn,
                    jca__dcj)
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    if bodo.libs.array_kernels.isna(data, jklg__yghss):
                        bodo.libs.array_kernels.setna(axg__tuegy, jklg__yghss)
                    else:
                        axg__tuegy[jklg__yghss] = int(data[jklg__yghss])
                return axg__tuegy
            return impl_float
        else:
            if data == bodo.dict_str_arr_type:

                def impl_dict(data, new_dtype, copy=None, nan_to_str=True,
                    from_series=False):
                    return bodo.libs.dict_arr_ext.convert_dict_arr_to_int(data,
                        jca__dcj)
                return impl_dict

            def impl(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                jcu__hnrn = len(data)
                numba.parfors.parfor.init_prange()
                axg__tuegy = bodo.libs.int_arr_ext.alloc_int_array(jcu__hnrn,
                    jca__dcj)
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    if bodo.libs.array_kernels.isna(data, jklg__yghss):
                        bodo.libs.array_kernels.setna(axg__tuegy, jklg__yghss)
                    else:
                        axg__tuegy[jklg__yghss] = np.int64(data[jklg__yghss])
                return axg__tuegy
            return impl
    if isinstance(nb_dtype, types.Integer) and isinstance(data.dtype, types
        .Integer):

        def impl(data, new_dtype, copy=None, nan_to_str=True, from_series=False
            ):
            return data.astype(nb_dtype)
        return impl
    if nb_dtype == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            jcu__hnrn = len(data)
            numba.parfors.parfor.init_prange()
            axg__tuegy = bodo.libs.bool_arr_ext.alloc_bool_array(jcu__hnrn)
            for jklg__yghss in numba.parfors.parfor.internal_prange(jcu__hnrn):
                if bodo.libs.array_kernels.isna(data, jklg__yghss):
                    bodo.libs.array_kernels.setna(axg__tuegy, jklg__yghss)
                else:
                    axg__tuegy[jklg__yghss] = bool(data[jklg__yghss])
            return axg__tuegy
        return impl_bool
    if nb_dtype == bodo.datetime_date_type:
        if data.dtype == bodo.datetime64ns:

            def impl_date(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                jcu__hnrn = len(data)
                qysf__oovzk = (bodo.hiframes.datetime_date_ext.
                    alloc_datetime_date_array(jcu__hnrn))
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    if bodo.libs.array_kernels.isna(data, jklg__yghss):
                        bodo.libs.array_kernels.setna(qysf__oovzk, jklg__yghss)
                    else:
                        qysf__oovzk[jklg__yghss
                            ] = bodo.utils.conversion.box_if_dt64(data[
                            jklg__yghss]).date()
                return qysf__oovzk
            return impl_date
    if nb_dtype == bodo.datetime64ns:
        if data.dtype == bodo.string_type:

            def impl_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return bodo.hiframes.pd_timestamp_ext.series_str_dt64_astype(
                    data)
            return impl_str
        if data == bodo.datetime_date_array_type:

            def impl_date(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return (bodo.hiframes.pd_timestamp_ext.
                    datetime_date_arr_to_dt64_arr(data))
            return impl_date
        if isinstance(data.dtype, types.Number) or data.dtype in [bodo.
            timedelta64ns, types.bool_]:

            def impl_numeric(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                jcu__hnrn = len(data)
                numba.parfors.parfor.init_prange()
                qysf__oovzk = np.empty(jcu__hnrn, dtype=np.dtype(
                    'datetime64[ns]'))
                for jklg__yghss in numba.parfors.parfor.internal_prange(
                    jcu__hnrn):
                    if bodo.libs.array_kernels.isna(data, jklg__yghss):
                        bodo.libs.array_kernels.setna(qysf__oovzk, jklg__yghss)
                    else:
                        qysf__oovzk[jklg__yghss
                            ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                            np.int64(data[jklg__yghss]))
                return qysf__oovzk
            return impl_numeric
    if nb_dtype == bodo.timedelta64ns:
        if data.dtype == bodo.string_type:

            def impl_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                return bodo.hiframes.pd_timestamp_ext.series_str_td64_astype(
                    data)
            return impl_str
        if isinstance(data.dtype, types.Number) or data.dtype in [bodo.
            datetime64ns, types.bool_]:
            if vpayz__yampl:

                def impl_numeric(data, new_dtype, copy=None, nan_to_str=
                    True, from_series=False):
                    jcu__hnrn = len(data)
                    numba.parfors.parfor.init_prange()
                    qysf__oovzk = np.empty(jcu__hnrn, dtype=np.dtype(
                        'timedelta64[ns]'))
                    for jklg__yghss in numba.parfors.parfor.internal_prange(
                        jcu__hnrn):
                        if bodo.libs.array_kernels.isna(data, jklg__yghss):
                            bodo.libs.array_kernels.setna(qysf__oovzk,
                                jklg__yghss)
                        else:
                            qysf__oovzk[jklg__yghss] = (bodo.hiframes.
                                pd_timestamp_ext.integer_to_timedelta64(np.
                                int64(data[jklg__yghss])))
                    return qysf__oovzk
                return impl_numeric
            else:
                return (lambda data, new_dtype, copy=None, nan_to_str=True,
                    from_series=False: data.view('int64'))
    if nb_dtype == types.int64 and data.dtype in [bodo.datetime64ns, bodo.
        timedelta64ns]:

        def impl_datelike_to_integer(data, new_dtype, copy=None, nan_to_str
            =True, from_series=False):
            jcu__hnrn = len(data)
            numba.parfors.parfor.init_prange()
            A = np.empty(jcu__hnrn, types.int64)
            for jklg__yghss in numba.parfors.parfor.internal_prange(jcu__hnrn):
                if bodo.libs.array_kernels.isna(data, jklg__yghss):
                    bodo.libs.array_kernels.setna(A, jklg__yghss)
                else:
                    A[jklg__yghss] = np.int64(data[jklg__yghss])
            return A
        return impl_datelike_to_integer
    if data.dtype != nb_dtype:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data.astype(nb_dtype))
    raise BodoError(f'Conversion from {data} to {new_dtype} not supported yet')


def array_type_from_dtype(dtype):
    return dtype_to_array_type(bodo.utils.typing.parse_dtype(dtype))


@overload(array_type_from_dtype)
def overload_array_type_from_dtype(dtype):
    arr_type = dtype_to_array_type(bodo.utils.typing.parse_dtype(dtype))
    return lambda dtype: arr_type


@numba.jit
def flatten_array(A):
    mqk__qmjg = []
    jcu__hnrn = len(A)
    for jklg__yghss in range(jcu__hnrn):
        zynll__vfm = A[jklg__yghss]
        for uorc__ynsi in zynll__vfm:
            mqk__qmjg.append(uorc__ynsi)
    return bodo.utils.conversion.coerce_to_array(mqk__qmjg)


def parse_datetimes_from_strings(data):
    return data


@overload(parse_datetimes_from_strings, no_unliteral=True)
def overload_parse_datetimes_from_strings(data):
    assert is_str_arr_type(data
        ), 'parse_datetimes_from_strings: string array expected'

    def parse_impl(data):
        numba.parfors.parfor.init_prange()
        jcu__hnrn = len(data)
        ftykx__eel = np.empty(jcu__hnrn, bodo.utils.conversion.NS_DTYPE)
        for jklg__yghss in numba.parfors.parfor.internal_prange(jcu__hnrn):
            ftykx__eel[jklg__yghss
                ] = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(data[
                jklg__yghss])
        return ftykx__eel
    return parse_impl


def convert_to_dt64ns(data):
    return data


@overload(convert_to_dt64ns, no_unliteral=True)
def overload_convert_to_dt64ns(data):
    if data == bodo.hiframes.datetime_date_ext.datetime_date_array_type:
        return (lambda data: bodo.hiframes.pd_timestamp_ext.
            datetime_date_arr_to_dt64_arr(data))
    if is_np_arr_typ(data, types.int64):
        return lambda data: data.view(bodo.utils.conversion.NS_DTYPE)
    if is_np_arr_typ(data, types.NPDatetime('ns')):
        return lambda data: data
    if is_str_arr_type(data):
        return lambda data: bodo.utils.conversion.parse_datetimes_from_strings(
            data)
    raise BodoError(f'invalid data type {data} for dt64 conversion')


def convert_to_td64ns(data):
    return data


@overload(convert_to_td64ns, no_unliteral=True)
def overload_convert_to_td64ns(data):
    if is_np_arr_typ(data, types.int64):
        return lambda data: data.view(bodo.utils.conversion.TD_DTYPE)
    if is_np_arr_typ(data, types.NPTimedelta('ns')):
        return lambda data: data
    if is_str_arr_type(data):
        raise BodoError('conversion to timedelta from string not supported yet'
            )
    raise BodoError(f'invalid data type {data} for timedelta64 conversion')


def convert_to_index(data, name=None):
    return data


@overload(convert_to_index, no_unliteral=True)
def overload_convert_to_index(data, name=None):
    from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
    if isinstance(data, (RangeIndexType, NumericIndexType,
        DatetimeIndexType, TimedeltaIndexType, StringIndexType,
        BinaryIndexType, CategoricalIndexType, PeriodIndexType, types.NoneType)
        ):
        return lambda data, name=None: data

    def impl(data, name=None):
        omwvt__kso = bodo.utils.conversion.coerce_to_array(data)
        return bodo.utils.conversion.index_from_array(omwvt__kso, name)
    return impl


def force_convert_index(I1, I2):
    return I2


@overload(force_convert_index, no_unliteral=True)
def overload_force_convert_index(I1, I2):
    from bodo.hiframes.pd_index_ext import RangeIndexType
    if isinstance(I2, RangeIndexType):
        return lambda I1, I2: pd.RangeIndex(len(I1._data))
    return lambda I1, I2: I1


def index_from_array(data, name=None):
    return data


@overload(index_from_array, no_unliteral=True)
def overload_index_from_array(data, name=None):
    if data in [bodo.string_array_type, bodo.binary_array_type, bodo.
        dict_str_arr_type]:
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_binary_str_index(data, name))
    if (data == bodo.hiframes.datetime_date_ext.datetime_date_array_type or
        data.dtype == types.NPDatetime('ns')):
        return lambda data, name=None: pd.DatetimeIndex(data, name=name)
    if data.dtype == types.NPTimedelta('ns'):
        return lambda data, name=None: pd.TimedeltaIndex(data, name=name)
    if isinstance(data.dtype, (types.Integer, types.Float, types.Boolean)):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_numeric_index(data, name))
    if isinstance(data, bodo.libs.interval_arr_ext.IntervalArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_interval_index(data, name))
    if isinstance(data, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_categorical_index(data, name))
    if isinstance(data, bodo.libs.pd_datetime_arr_ext.DatetimeArrayType):
        return (lambda data, name=None: bodo.hiframes.pd_index_ext.
            init_datetime_index(data, name))
    raise BodoError(f'cannot convert {data} to Index')


def index_to_array(data):
    return data


@overload(index_to_array, no_unliteral=True)
def overload_index_to_array(I):
    from bodo.hiframes.pd_index_ext import RangeIndexType
    if isinstance(I, RangeIndexType):
        return lambda I: np.arange(I._start, I._stop, I._step)
    return lambda I: bodo.hiframes.pd_index_ext.get_index_data(I)


def false_if_none(val):
    return False if val is None else val


@overload(false_if_none, no_unliteral=True)
def overload_false_if_none(val):
    if is_overload_none(val):
        return lambda val: False
    return lambda val: val


def extract_name_if_none(data, name):
    return name


@overload(extract_name_if_none, no_unliteral=True)
def overload_extract_name_if_none(data, name):
    from bodo.hiframes.pd_index_ext import CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, TimedeltaIndexType
    from bodo.hiframes.pd_series_ext import SeriesType
    if not is_overload_none(name):
        return lambda data, name: name
    if isinstance(data, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, PeriodIndexType, CategoricalIndexType)):
        return lambda data, name: bodo.hiframes.pd_index_ext.get_index_name(
            data)
    if isinstance(data, SeriesType):
        return lambda data, name: bodo.hiframes.pd_series_ext.get_series_name(
            data)
    return lambda data, name: name


def extract_index_if_none(data, index):
    return index


@overload(extract_index_if_none, no_unliteral=True)
def overload_extract_index_if_none(data, index):
    from bodo.hiframes.pd_series_ext import SeriesType
    if not is_overload_none(index):
        return lambda data, index: index
    if isinstance(data, SeriesType):
        return (lambda data, index: bodo.hiframes.pd_series_ext.
            get_series_index(data))
    return lambda data, index: bodo.hiframes.pd_index_ext.init_range_index(
        0, len(data), 1, None)


def box_if_dt64(val):
    return val


@overload(box_if_dt64, no_unliteral=True)
def overload_box_if_dt64(val):
    if val == types.NPDatetime('ns'):
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            convert_datetime64_to_timestamp(val))
    if val == types.NPTimedelta('ns'):
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            convert_numpy_timedelta64_to_pd_timedelta(val))
    return lambda val: val


def unbox_if_timestamp(val):
    return val


@overload(unbox_if_timestamp, no_unliteral=True)
def overload_unbox_if_timestamp(val):
    if val == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        return lambda val: bodo.hiframes.pd_timestamp_ext.integer_to_dt64(val
            .value)
    if val == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:
        return lambda val: bodo.hiframes.pd_timestamp_ext.integer_to_dt64(pd
            .Timestamp(val).value)
    if val == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return (lambda val: bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(val.value))
    if val == types.Optional(bodo.hiframes.pd_timestamp_ext.pd_timestamp_type):

        def impl_optional(val):
            if val is None:
                cbw__geb = None
            else:
                cbw__geb = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(bodo
                    .utils.indexing.unoptional(val).value)
            return cbw__geb
        return impl_optional
    if val == types.Optional(bodo.hiframes.datetime_timedelta_ext.
        pd_timedelta_type):

        def impl_optional_td(val):
            if val is None:
                cbw__geb = None
            else:
                cbw__geb = (bodo.hiframes.pd_timestamp_ext.
                    integer_to_timedelta64(bodo.utils.indexing.unoptional(
                    val).value))
            return cbw__geb
        return impl_optional_td
    return lambda val: val


def to_tuple(val):
    return val


@overload(to_tuple, no_unliteral=True)
def overload_to_tuple(val):
    if not isinstance(val, types.BaseTuple) and is_overload_constant_list(val):
        grhz__ewi = len(val.types if isinstance(val, types.LiteralList) else
            get_overload_const_list(val))
        sahmq__vulm = 'def f(val):\n'
        awwkv__lpb = ','.join(f'val[{jklg__yghss}]' for jklg__yghss in
            range(grhz__ewi))
        sahmq__vulm += f'  return ({awwkv__lpb},)\n'
        rhsjz__ohc = {}
        exec(sahmq__vulm, {}, rhsjz__ohc)
        impl = rhsjz__ohc['f']
        return impl
    assert isinstance(val, types.BaseTuple), 'tuple type expected'
    return lambda val: val


def get_array_if_series_or_index(data):
    return data


@overload(get_array_if_series_or_index)
def overload_get_array_if_series_or_index(data):
    from bodo.hiframes.pd_series_ext import SeriesType
    if isinstance(data, SeriesType):
        return lambda data: bodo.hiframes.pd_series_ext.get_series_data(data)
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        return lambda data: bodo.utils.conversion.coerce_to_array(data)
    if isinstance(data, bodo.hiframes.pd_index_ext.HeterogeneousIndexType):
        if not is_heterogeneous_tuple_type(data.data):

            def impl(data):
                drc__aonh = bodo.hiframes.pd_index_ext.get_index_data(data)
                return bodo.utils.conversion.coerce_to_array(drc__aonh)
            return impl

        def impl(data):
            return bodo.hiframes.pd_index_ext.get_index_data(data)
        return impl
    return lambda data: data


def extract_index_array(A):
    return np.arange(len(A))


@overload(extract_index_array, no_unliteral=True)
def overload_extract_index_array(A):
    from bodo.hiframes.pd_series_ext import SeriesType
    if isinstance(A, SeriesType):

        def impl(A):
            index = bodo.hiframes.pd_series_ext.get_series_index(A)
            tzgu__khyr = bodo.utils.conversion.coerce_to_array(index)
            return tzgu__khyr
        return impl
    return lambda A: np.arange(len(A))


def ensure_contig_if_np(arr):
    return np.ascontiguousarray(arr)


@overload(ensure_contig_if_np, no_unliteral=True)
def overload_ensure_contig_if_np(arr):
    if isinstance(arr, types.Array):
        return lambda arr: np.ascontiguousarray(arr)
    return lambda arr: arr


def struct_if_heter_dict(values, names):
    return {ebr__wbzr: bdn__lrf for ebr__wbzr, bdn__lrf in zip(names, values)}


@overload(struct_if_heter_dict, no_unliteral=True)
def overload_struct_if_heter_dict(values, names):
    if not types.is_homogeneous(*values.types):
        return lambda values, names: bodo.libs.struct_arr_ext.init_struct(
            values, names)
    iskc__zidt = len(values.types)
    sahmq__vulm = 'def f(values, names):\n'
    awwkv__lpb = ','.join("'{}': values[{}]".format(get_overload_const_str(
        names.types[jklg__yghss]), jklg__yghss) for jklg__yghss in range(
        iskc__zidt))
    sahmq__vulm += '  return {{{}}}\n'.format(awwkv__lpb)
    rhsjz__ohc = {}
    exec(sahmq__vulm, {}, rhsjz__ohc)
    impl = rhsjz__ohc['f']
    return impl
