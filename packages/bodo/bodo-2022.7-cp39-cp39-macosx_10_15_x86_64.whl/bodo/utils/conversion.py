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
        cih__nbg = data.dtype
        if isinstance(cih__nbg, types.Optional):
            cih__nbg = cih__nbg.type
            if bodo.utils.typing.is_scalar_type(cih__nbg):
                use_nullable_array = True
        if isinstance(cih__nbg, (types.Boolean, types.Integer, Decimal128Type)
            ) or cih__nbg in [bodo.hiframes.pd_timestamp_ext.
            pd_timestamp_type, bodo.hiframes.datetime_date_ext.
            datetime_date_type, bodo.hiframes.datetime_timedelta_ext.
            datetime_timedelta_type]:
            iet__wmqnu = dtype_to_array_type(cih__nbg)
            if not is_overload_none(use_nullable_array):
                iet__wmqnu = to_nullable_type(iet__wmqnu)

            def impl(data, error_on_nonarray=True, use_nullable_array=None,
                scalar_to_arr_len=None):
                lloxu__ghzdd = len(data)
                A = bodo.utils.utils.alloc_type(lloxu__ghzdd, iet__wmqnu, (-1,)
                    )
                bodo.utils.utils.tuple_list_to_array(A, data, cih__nbg)
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
            demye__ovu = data.precision
            tetml__kvpyw = data.scale

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                lloxu__ghzdd = scalar_to_arr_len
                A = bodo.libs.decimal_arr_ext.alloc_decimal_array(lloxu__ghzdd,
                    demye__ovu, tetml__kvpyw)
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    A[gjpc__grod] = data
                return A
            return impl_ts
        if data == bodo.hiframes.datetime_datetime_ext.datetime_datetime_type:
            sefk__blye = np.dtype('datetime64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                lloxu__ghzdd = scalar_to_arr_len
                A = np.empty(lloxu__ghzdd, sefk__blye)
                aaby__ulbhm = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(data))
                pjy__cnq = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    aaby__ulbhm)
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    A[gjpc__grod] = pjy__cnq
                return A
            return impl_ts
        if (data == bodo.hiframes.datetime_timedelta_ext.
            datetime_timedelta_type):
            sizbm__qbva = np.dtype('timedelta64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                lloxu__ghzdd = scalar_to_arr_len
                A = np.empty(lloxu__ghzdd, sizbm__qbva)
                ieh__rglo = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(data))
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    A[gjpc__grod] = ieh__rglo
                return A
            return impl_ts
        if data == bodo.hiframes.datetime_date_ext.datetime_date_type:

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                lloxu__ghzdd = scalar_to_arr_len
                A = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
                    lloxu__ghzdd)
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    A[gjpc__grod] = data
                return A
            return impl_ts
        if data == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            sefk__blye = np.dtype('datetime64[ns]')

            def impl_ts(data, error_on_nonarray=True, use_nullable_array=
                None, scalar_to_arr_len=None):
                lloxu__ghzdd = scalar_to_arr_len
                A = np.empty(scalar_to_arr_len, sefk__blye)
                aaby__ulbhm = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    data.value)
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    A[gjpc__grod] = aaby__ulbhm
                return A
            return impl_ts
        dtype = types.unliteral(data)
        if not is_overload_none(use_nullable_array) and isinstance(dtype,
            types.Integer):

            def impl_null_integer(data, error_on_nonarray=True,
                use_nullable_array=None, scalar_to_arr_len=None):
                numba.parfors.parfor.init_prange()
                lloxu__ghzdd = scalar_to_arr_len
                vqg__edk = bodo.libs.int_arr_ext.alloc_int_array(lloxu__ghzdd,
                    dtype)
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    vqg__edk[gjpc__grod] = data
                return vqg__edk
            return impl_null_integer
        if not is_overload_none(use_nullable_array) and dtype == types.bool_:

            def impl_null_bool(data, error_on_nonarray=True,
                use_nullable_array=None, scalar_to_arr_len=None):
                numba.parfors.parfor.init_prange()
                lloxu__ghzdd = scalar_to_arr_len
                vqg__edk = bodo.libs.bool_arr_ext.alloc_bool_array(lloxu__ghzdd
                    )
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    vqg__edk[gjpc__grod] = data
                return vqg__edk
            return impl_null_bool

        def impl_num(data, error_on_nonarray=True, use_nullable_array=None,
            scalar_to_arr_len=None):
            numba.parfors.parfor.init_prange()
            lloxu__ghzdd = scalar_to_arr_len
            vqg__edk = np.empty(lloxu__ghzdd, dtype)
            for gjpc__grod in numba.parfors.parfor.internal_prange(lloxu__ghzdd
                ):
                vqg__edk[gjpc__grod] = data
            return vqg__edk
        return impl_num
    if isinstance(data, types.BaseTuple) and all(isinstance(grf__eqisg, (
        types.Float, types.Integer)) for grf__eqisg in data.types):
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
    cuth__gvgsv = to_nullable_type(unwrap_typeref(arr_type))
    if scalar == types.none:

        def impl(scalar, length, arr_type):
            return bodo.libs.array_kernels.gen_na_array(length, cuth__gvgsv,
                True)
    elif isinstance(scalar, types.Optional):

        def impl(scalar, length, arr_type):
            if scalar is None:
                return bodo.libs.array_kernels.gen_na_array(length,
                    cuth__gvgsv, True)
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
        ) and all(isinstance(grf__eqisg, types.StringLiteral) for
        grf__eqisg in data.types):
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
        ltssz__ifd = tuple(dtype_to_array_type(grf__eqisg) for grf__eqisg in
            data.dtype.types)

        def impl_tuple_list(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            lloxu__ghzdd = len(data)
            arr = bodo.libs.tuple_arr_ext.pre_alloc_tuple_array(lloxu__ghzdd,
                (-1,), ltssz__ifd)
            for gjpc__grod in range(lloxu__ghzdd):
                arr[gjpc__grod] = data[gjpc__grod]
            return arr
        return impl_tuple_list
    if isinstance(data, types.List) and (bodo.utils.utils.is_array_typ(data
        .dtype, False) or isinstance(data.dtype, types.List)):
        xxbj__anvn = dtype_to_array_type(data.dtype.dtype)

        def impl_array_item_arr(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            lloxu__ghzdd = len(data)
            uwm__yihc = init_nested_counts(xxbj__anvn)
            for gjpc__grod in range(lloxu__ghzdd):
                wyjzd__jbsp = bodo.utils.conversion.coerce_to_array(data[
                    gjpc__grod], use_nullable_array=True)
                uwm__yihc = add_nested_counts(uwm__yihc, wyjzd__jbsp)
            vqg__edk = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
                lloxu__ghzdd, uwm__yihc, xxbj__anvn)
            jpum__zcjj = bodo.libs.array_item_arr_ext.get_null_bitmap(vqg__edk)
            for iymw__jlak in range(lloxu__ghzdd):
                wyjzd__jbsp = bodo.utils.conversion.coerce_to_array(data[
                    iymw__jlak], use_nullable_array=True)
                vqg__edk[iymw__jlak] = wyjzd__jbsp
                bodo.libs.int_arr_ext.set_bit_to_arr(jpum__zcjj, iymw__jlak, 1)
            return vqg__edk
        return impl_array_item_arr
    if not is_overload_none(scalar_to_arr_len) and isinstance(data, (types.
        UnicodeType, types.StringLiteral)):

        def impl_str(data, error_on_nonarray=True, use_nullable_array=None,
            scalar_to_arr_len=None):
            lloxu__ghzdd = scalar_to_arr_len
            sef__sse = bodo.libs.str_arr_ext.str_arr_from_sequence([data])
            cwd__fyjs = bodo.libs.int_arr_ext.alloc_int_array(lloxu__ghzdd,
                np.int32)
            numba.parfors.parfor.init_prange()
            for gjpc__grod in numba.parfors.parfor.internal_prange(lloxu__ghzdd
                ):
                cwd__fyjs[gjpc__grod] = 0
            A = bodo.libs.dict_arr_ext.init_dict_arr(sef__sse, cwd__fyjs, True)
            return A
        return impl_str
    if isinstance(data, types.List) and isinstance(data.dtype, bodo.
        hiframes.pd_timestamp_ext.PandasTimestampType):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
            'coerce_to_array()')

        def impl_list_timestamp(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            lloxu__ghzdd = len(data)
            A = np.empty(lloxu__ghzdd, np.dtype('datetime64[ns]'))
            for gjpc__grod in range(lloxu__ghzdd):
                A[gjpc__grod] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    data[gjpc__grod].value)
            return A
        return impl_list_timestamp
    if isinstance(data, types.List) and data.dtype == bodo.pd_timedelta_type:

        def impl_list_timedelta(data, error_on_nonarray=True,
            use_nullable_array=None, scalar_to_arr_len=None):
            lloxu__ghzdd = len(data)
            A = np.empty(lloxu__ghzdd, np.dtype('timedelta64[ns]'))
            for gjpc__grod in range(lloxu__ghzdd):
                A[gjpc__grod
                    ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    data[gjpc__grod].value)
            return A
        return impl_list_timedelta
    if isinstance(data, bodo.hiframes.pd_timestamp_ext.PandasTimestampType):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
            'coerce_to_array()')
    if not is_overload_none(scalar_to_arr_len) and data in [bodo.
        pd_timestamp_type, bodo.pd_timedelta_type]:
        tie__luq = ('datetime64[ns]' if data == bodo.pd_timestamp_type else
            'timedelta64[ns]')

        def impl_timestamp(data, error_on_nonarray=True, use_nullable_array
            =None, scalar_to_arr_len=None):
            lloxu__ghzdd = scalar_to_arr_len
            A = np.empty(lloxu__ghzdd, tie__luq)
            data = bodo.utils.conversion.unbox_if_timestamp(data)
            for gjpc__grod in numba.parfors.parfor.internal_prange(lloxu__ghzdd
                ):
                A[gjpc__grod] = data
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
    obbl__odvd = is_overload_true(copy)
    anm__frl = is_overload_constant_str(new_dtype) and get_overload_const_str(
        new_dtype) == 'object'
    if is_overload_none(new_dtype) or anm__frl:
        if obbl__odvd:
            return (lambda data, new_dtype, copy=None, nan_to_str=True,
                from_series=False: data.copy())
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data)
    if isinstance(data, NullableTupleType):
        nb_dtype = bodo.utils.typing.parse_dtype(new_dtype)
        if isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype):
            nb_dtype = nb_dtype.dtype
        oaln__uhpei = {types.unicode_type: '', boolean_dtype: False, types.
            bool_: False, types.int8: np.int8(0), types.int16: np.int16(0),
            types.int32: np.int32(0), types.int64: np.int64(0), types.uint8:
            np.uint8(0), types.uint16: np.uint16(0), types.uint32: np.
            uint32(0), types.uint64: np.uint64(0), types.float32: np.
            float32(0), types.float64: np.float64(0), bodo.datetime64ns: pd
            .Timestamp(0), bodo.timedelta64ns: pd.Timedelta(0)}
        aubo__kgbhp = {types.unicode_type: str, types.bool_: bool,
            boolean_dtype: bool, types.int8: np.int8, types.int16: np.int16,
            types.int32: np.int32, types.int64: np.int64, types.uint8: np.
            uint8, types.uint16: np.uint16, types.uint32: np.uint32, types.
            uint64: np.uint64, types.float32: np.float32, types.float64: np
            .float64, bodo.datetime64ns: pd.to_datetime, bodo.timedelta64ns:
            pd.to_timedelta}
        izuhc__ornop = oaln__uhpei.keys()
        vyr__cotbs = list(data._tuple_typ.types)
        if nb_dtype not in izuhc__ornop:
            raise BodoError(f'type conversion to {nb_dtype} types unsupported.'
                )
        for prdxx__qta in vyr__cotbs:
            if prdxx__qta == bodo.datetime64ns:
                if nb_dtype not in (types.unicode_type, types.int64, types.
                    uint64, bodo.datetime64ns):
                    raise BodoError(
                        f'invalid type conversion from {prdxx__qta} to {nb_dtype}.'
                        )
            elif prdxx__qta == bodo.timedelta64ns:
                if nb_dtype not in (types.unicode_type, types.int64, types.
                    uint64, bodo.timedelta64ns):
                    raise BodoError(
                        f'invalid type conversion from {prdxx__qta} to {nb_dtype}.'
                        )
        xopc__bjzzp = (
            'def impl(data, new_dtype, copy=None, nan_to_str=True, from_series=False):\n'
            )
        xopc__bjzzp += '  data_tup = data._data\n'
        xopc__bjzzp += '  null_tup = data._null_values\n'
        for gjpc__grod in range(len(vyr__cotbs)):
            xopc__bjzzp += (
                f'  val_{gjpc__grod} = convert_func(default_value)\n')
            xopc__bjzzp += f'  if not null_tup[{gjpc__grod}]:\n'
            xopc__bjzzp += (
                f'    val_{gjpc__grod} = convert_func(data_tup[{gjpc__grod}])\n'
                )
        hcidl__vjyuc = ', '.join(f'val_{gjpc__grod}' for gjpc__grod in
            range(len(vyr__cotbs)))
        xopc__bjzzp += f'  vals_tup = ({hcidl__vjyuc},)\n'
        xopc__bjzzp += """  res_tup = bodo.libs.nullable_tuple_ext.build_nullable_tuple(vals_tup, null_tup)
"""
        xopc__bjzzp += '  return res_tup\n'
        isk__ruqvt = {}
        kaunb__ccf = aubo__kgbhp[nb_dtype]
        ovopk__ctqh = oaln__uhpei[nb_dtype]
        exec(xopc__bjzzp, {'bodo': bodo, 'np': np, 'pd': pd,
            'default_value': ovopk__ctqh, 'convert_func': kaunb__ccf},
            isk__ruqvt)
        impl = isk__ruqvt['impl']
        return impl
    if _is_str_dtype(new_dtype):
        if isinstance(data.dtype, types.Integer):

            def impl_int_str(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                lloxu__ghzdd = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(lloxu__ghzdd,
                    -1)
                for ybls__txefm in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    if bodo.libs.array_kernels.isna(data, ybls__txefm):
                        if nan_to_str:
                            bodo.libs.str_arr_ext.str_arr_setitem_NA_str(A,
                                ybls__txefm)
                        else:
                            bodo.libs.array_kernels.setna(A, ybls__txefm)
                    else:
                        bodo.libs.str_arr_ext.str_arr_setitem_int_to_str(A,
                            ybls__txefm, data[ybls__txefm])
                return A
            return impl_int_str
        if data.dtype == bytes_type:

            def impl_binary(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                lloxu__ghzdd = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(lloxu__ghzdd,
                    -1)
                for ybls__txefm in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    if bodo.libs.array_kernels.isna(data, ybls__txefm):
                        bodo.libs.array_kernels.setna(A, ybls__txefm)
                    else:
                        A[ybls__txefm] = ''.join([chr(ccw__qtq) for
                            ccw__qtq in data[ybls__txefm]])
                return A
            return impl_binary
        if is_overload_true(from_series) and data.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns):

            def impl_str_dt_series(data, new_dtype, copy=None, nan_to_str=
                True, from_series=False):
                numba.parfors.parfor.init_prange()
                lloxu__ghzdd = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(lloxu__ghzdd,
                    -1)
                for ybls__txefm in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    if bodo.libs.array_kernels.isna(data, ybls__txefm):
                        if nan_to_str:
                            A[ybls__txefm] = 'NaT'
                        else:
                            bodo.libs.array_kernels.setna(A, ybls__txefm)
                        continue
                    A[ybls__txefm] = str(box_if_dt64(data[ybls__txefm]))
                return A
            return impl_str_dt_series
        else:

            def impl_str_array(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                numba.parfors.parfor.init_prange()
                lloxu__ghzdd = len(data)
                A = bodo.libs.str_arr_ext.pre_alloc_string_array(lloxu__ghzdd,
                    -1)
                for ybls__txefm in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    if bodo.libs.array_kernels.isna(data, ybls__txefm):
                        if nan_to_str:
                            A[ybls__txefm] = 'nan'
                        else:
                            bodo.libs.array_kernels.setna(A, ybls__txefm)
                        continue
                    A[ybls__txefm] = str(data[ybls__txefm])
                return A
            return impl_str_array
    if isinstance(new_dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):

        def impl_cat_dtype(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            lloxu__ghzdd = len(data)
            numba.parfors.parfor.init_prange()
            tmfyc__zqp = (bodo.hiframes.pd_categorical_ext.
                get_label_dict_from_categories(new_dtype.categories.values))
            A = bodo.hiframes.pd_categorical_ext.alloc_categorical_array(
                lloxu__ghzdd, new_dtype)
            lblk__lrjc = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A))
            for gjpc__grod in numba.parfors.parfor.internal_prange(lloxu__ghzdd
                ):
                if bodo.libs.array_kernels.isna(data, gjpc__grod):
                    bodo.libs.array_kernels.setna(A, gjpc__grod)
                    continue
                val = data[gjpc__grod]
                if val not in tmfyc__zqp:
                    bodo.libs.array_kernels.setna(A, gjpc__grod)
                    continue
                lblk__lrjc[gjpc__grod] = tmfyc__zqp[val]
            return A
        return impl_cat_dtype
    if is_overload_constant_str(new_dtype) and get_overload_const_str(new_dtype
        ) == 'category':

        def impl_category(data, new_dtype, copy=None, nan_to_str=True,
            from_series=False):
            nhro__jaxz = bodo.libs.array_kernels.unique(data, dropna=True)
            nhro__jaxz = pd.Series(nhro__jaxz).sort_values().values
            nhro__jaxz = bodo.allgatherv(nhro__jaxz, False)
            rcggi__vwccp = bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo
                .utils.conversion.index_from_array(nhro__jaxz, None), False,
                None, None)
            lloxu__ghzdd = len(data)
            numba.parfors.parfor.init_prange()
            tmfyc__zqp = (bodo.hiframes.pd_categorical_ext.
                get_label_dict_from_categories_no_duplicates(nhro__jaxz))
            A = bodo.hiframes.pd_categorical_ext.alloc_categorical_array(
                lloxu__ghzdd, rcggi__vwccp)
            lblk__lrjc = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A))
            for gjpc__grod in numba.parfors.parfor.internal_prange(lloxu__ghzdd
                ):
                if bodo.libs.array_kernels.isna(data, gjpc__grod):
                    bodo.libs.array_kernels.setna(A, gjpc__grod)
                    continue
                val = data[gjpc__grod]
                lblk__lrjc[gjpc__grod] = tmfyc__zqp[val]
            return A
        return impl_category
    nb_dtype = bodo.utils.typing.parse_dtype(new_dtype)
    if isinstance(data, bodo.libs.int_arr_ext.IntegerArrayType):
        vhqqi__knt = isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype
            ) and data.dtype == nb_dtype.dtype
    else:
        vhqqi__knt = data.dtype == nb_dtype
    if obbl__odvd and vhqqi__knt:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data.copy())
    if vhqqi__knt:
        return (lambda data, new_dtype, copy=None, nan_to_str=True,
            from_series=False: data)
    if isinstance(nb_dtype, bodo.libs.int_arr_ext.IntDtype):
        if isinstance(nb_dtype, types.Integer):
            tie__luq = nb_dtype
        else:
            tie__luq = nb_dtype.dtype
        if isinstance(data.dtype, types.Float):

            def impl_float(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                lloxu__ghzdd = len(data)
                numba.parfors.parfor.init_prange()
                zxkcs__zderw = bodo.libs.int_arr_ext.alloc_int_array(
                    lloxu__ghzdd, tie__luq)
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    if bodo.libs.array_kernels.isna(data, gjpc__grod):
                        bodo.libs.array_kernels.setna(zxkcs__zderw, gjpc__grod)
                    else:
                        zxkcs__zderw[gjpc__grod] = int(data[gjpc__grod])
                return zxkcs__zderw
            return impl_float
        else:
            if data == bodo.dict_str_arr_type:

                def impl_dict(data, new_dtype, copy=None, nan_to_str=True,
                    from_series=False):
                    return bodo.libs.dict_arr_ext.convert_dict_arr_to_int(data,
                        tie__luq)
                return impl_dict

            def impl(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                lloxu__ghzdd = len(data)
                numba.parfors.parfor.init_prange()
                zxkcs__zderw = bodo.libs.int_arr_ext.alloc_int_array(
                    lloxu__ghzdd, tie__luq)
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    if bodo.libs.array_kernels.isna(data, gjpc__grod):
                        bodo.libs.array_kernels.setna(zxkcs__zderw, gjpc__grod)
                    else:
                        zxkcs__zderw[gjpc__grod] = np.int64(data[gjpc__grod])
                return zxkcs__zderw
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
            lloxu__ghzdd = len(data)
            numba.parfors.parfor.init_prange()
            zxkcs__zderw = bodo.libs.bool_arr_ext.alloc_bool_array(lloxu__ghzdd
                )
            for gjpc__grod in numba.parfors.parfor.internal_prange(lloxu__ghzdd
                ):
                if bodo.libs.array_kernels.isna(data, gjpc__grod):
                    bodo.libs.array_kernels.setna(zxkcs__zderw, gjpc__grod)
                else:
                    zxkcs__zderw[gjpc__grod] = bool(data[gjpc__grod])
            return zxkcs__zderw
        return impl_bool
    if nb_dtype == bodo.datetime_date_type:
        if data.dtype == bodo.datetime64ns:

            def impl_date(data, new_dtype, copy=None, nan_to_str=True,
                from_series=False):
                lloxu__ghzdd = len(data)
                vqg__edk = (bodo.hiframes.datetime_date_ext.
                    alloc_datetime_date_array(lloxu__ghzdd))
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    if bodo.libs.array_kernels.isna(data, gjpc__grod):
                        bodo.libs.array_kernels.setna(vqg__edk, gjpc__grod)
                    else:
                        vqg__edk[gjpc__grod
                            ] = bodo.utils.conversion.box_if_dt64(data[
                            gjpc__grod]).date()
                return vqg__edk
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
                lloxu__ghzdd = len(data)
                numba.parfors.parfor.init_prange()
                vqg__edk = np.empty(lloxu__ghzdd, dtype=np.dtype(
                    'datetime64[ns]'))
                for gjpc__grod in numba.parfors.parfor.internal_prange(
                    lloxu__ghzdd):
                    if bodo.libs.array_kernels.isna(data, gjpc__grod):
                        bodo.libs.array_kernels.setna(vqg__edk, gjpc__grod)
                    else:
                        vqg__edk[gjpc__grod
                            ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                            np.int64(data[gjpc__grod]))
                return vqg__edk
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
            if obbl__odvd:

                def impl_numeric(data, new_dtype, copy=None, nan_to_str=
                    True, from_series=False):
                    lloxu__ghzdd = len(data)
                    numba.parfors.parfor.init_prange()
                    vqg__edk = np.empty(lloxu__ghzdd, dtype=np.dtype(
                        'timedelta64[ns]'))
                    for gjpc__grod in numba.parfors.parfor.internal_prange(
                        lloxu__ghzdd):
                        if bodo.libs.array_kernels.isna(data, gjpc__grod):
                            bodo.libs.array_kernels.setna(vqg__edk, gjpc__grod)
                        else:
                            vqg__edk[gjpc__grod] = (bodo.hiframes.
                                pd_timestamp_ext.integer_to_timedelta64(np.
                                int64(data[gjpc__grod])))
                    return vqg__edk
                return impl_numeric
            else:
                return (lambda data, new_dtype, copy=None, nan_to_str=True,
                    from_series=False: data.view('int64'))
    if nb_dtype == types.int64 and data.dtype in [bodo.datetime64ns, bodo.
        timedelta64ns]:

        def impl_datelike_to_integer(data, new_dtype, copy=None, nan_to_str
            =True, from_series=False):
            lloxu__ghzdd = len(data)
            numba.parfors.parfor.init_prange()
            A = np.empty(lloxu__ghzdd, types.int64)
            for gjpc__grod in numba.parfors.parfor.internal_prange(lloxu__ghzdd
                ):
                if bodo.libs.array_kernels.isna(data, gjpc__grod):
                    bodo.libs.array_kernels.setna(A, gjpc__grod)
                else:
                    A[gjpc__grod] = np.int64(data[gjpc__grod])
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
    keu__pawjq = []
    lloxu__ghzdd = len(A)
    for gjpc__grod in range(lloxu__ghzdd):
        weyjd__opd = A[gjpc__grod]
        for dhepr__vukwx in weyjd__opd:
            keu__pawjq.append(dhepr__vukwx)
    return bodo.utils.conversion.coerce_to_array(keu__pawjq)


def parse_datetimes_from_strings(data):
    return data


@overload(parse_datetimes_from_strings, no_unliteral=True)
def overload_parse_datetimes_from_strings(data):
    assert is_str_arr_type(data
        ), 'parse_datetimes_from_strings: string array expected'

    def parse_impl(data):
        numba.parfors.parfor.init_prange()
        lloxu__ghzdd = len(data)
        szht__gzy = np.empty(lloxu__ghzdd, bodo.utils.conversion.NS_DTYPE)
        for gjpc__grod in numba.parfors.parfor.internal_prange(lloxu__ghzdd):
            szht__gzy[gjpc__grod
                ] = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(data[
                gjpc__grod])
        return szht__gzy
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
        rntw__qlsw = bodo.utils.conversion.coerce_to_array(data)
        return bodo.utils.conversion.index_from_array(rntw__qlsw, name)
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
                mfxpd__xxrfu = None
            else:
                mfxpd__xxrfu = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                    bodo.utils.indexing.unoptional(val).value)
            return mfxpd__xxrfu
        return impl_optional
    if val == types.Optional(bodo.hiframes.datetime_timedelta_ext.
        pd_timedelta_type):

        def impl_optional_td(val):
            if val is None:
                mfxpd__xxrfu = None
            else:
                mfxpd__xxrfu = (bodo.hiframes.pd_timestamp_ext.
                    integer_to_timedelta64(bodo.utils.indexing.unoptional(
                    val).value))
            return mfxpd__xxrfu
        return impl_optional_td
    return lambda val: val


def to_tuple(val):
    return val


@overload(to_tuple, no_unliteral=True)
def overload_to_tuple(val):
    if not isinstance(val, types.BaseTuple) and is_overload_constant_list(val):
        apz__qkw = len(val.types if isinstance(val, types.LiteralList) else
            get_overload_const_list(val))
        xopc__bjzzp = 'def f(val):\n'
        nvow__ywpu = ','.join(f'val[{gjpc__grod}]' for gjpc__grod in range(
            apz__qkw))
        xopc__bjzzp += f'  return ({nvow__ywpu},)\n'
        isk__ruqvt = {}
        exec(xopc__bjzzp, {}, isk__ruqvt)
        impl = isk__ruqvt['f']
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
                qczr__bphe = bodo.hiframes.pd_index_ext.get_index_data(data)
                return bodo.utils.conversion.coerce_to_array(qczr__bphe)
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
            uih__iqn = bodo.utils.conversion.coerce_to_array(index)
            return uih__iqn
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
    return {tgyh__dpi: aaby__ulbhm for tgyh__dpi, aaby__ulbhm in zip(names,
        values)}


@overload(struct_if_heter_dict, no_unliteral=True)
def overload_struct_if_heter_dict(values, names):
    if not types.is_homogeneous(*values.types):
        return lambda values, names: bodo.libs.struct_arr_ext.init_struct(
            values, names)
    tbt__ynfd = len(values.types)
    xopc__bjzzp = 'def f(values, names):\n'
    nvow__ywpu = ','.join("'{}': values[{}]".format(get_overload_const_str(
        names.types[gjpc__grod]), gjpc__grod) for gjpc__grod in range(
        tbt__ynfd))
    xopc__bjzzp += '  return {{{}}}\n'.format(nvow__ywpu)
    isk__ruqvt = {}
    exec(xopc__bjzzp, {}, isk__ruqvt)
    impl = isk__ruqvt['f']
    return impl
