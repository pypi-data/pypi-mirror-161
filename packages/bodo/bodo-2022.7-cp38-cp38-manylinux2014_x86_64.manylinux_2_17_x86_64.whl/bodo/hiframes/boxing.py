"""
Boxing and unboxing support for DataFrame, Series, etc.
"""
import datetime
import decimal
import warnings
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.ir_utils import GuardException, guard
from numba.core.typing import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, intrinsic, typeof_impl, unbox
from numba.np import numpy_support
from numba.np.arrayobj import _getitem_array_single_int
from numba.typed.typeddict import Dict
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import PDCategoricalDtype
from bodo.hiframes.pd_dataframe_ext import DataFramePayloadType, DataFrameType, check_runtime_cols_unsupported, construct_dataframe
from bodo.hiframes.pd_index_ext import BinaryIndexType, CategoricalIndexType, DatetimeIndexType, NumericIndexType, PeriodIndexType, RangeIndexType, StringIndexType, TimedeltaIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType, typeof_pd_int_dtype
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType, PandasDatetimeTZDtype
from bodo.libs.str_arr_ext import string_array_type, string_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.typing import BodoError, BodoWarning, dtype_to_array_type, get_overload_const_bool, get_overload_const_int, get_overload_const_str, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
ll.add_symbol('is_np_array', hstr_ext.is_np_array)
ll.add_symbol('array_size', hstr_ext.array_size)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
TABLE_FORMAT_THRESHOLD = 20
_use_dict_str_type = True


def _set_bodo_meta_in_pandas():
    if '_bodo_meta' not in pd.Series._metadata:
        pd.Series._metadata.append('_bodo_meta')
    if '_bodo_meta' not in pd.DataFrame._metadata:
        pd.DataFrame._metadata.append('_bodo_meta')


_set_bodo_meta_in_pandas()


@typeof_impl.register(pd.DataFrame)
def typeof_pd_dataframe(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    jdugi__mwf = tuple(val.columns.to_list())
    mgq__ddpq = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        hfnr__jgxmy = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        hfnr__jgxmy = numba.typeof(val.index)
    ziznk__uwhv = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    jck__wdx = len(mgq__ddpq) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(mgq__ddpq, hfnr__jgxmy, jdugi__mwf, ziznk__uwhv,
        is_table_format=jck__wdx)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    ziznk__uwhv = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        cjg__dahou = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        cjg__dahou = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    kyb__pgppp = dtype_to_array_type(dtype)
    if _use_dict_str_type and kyb__pgppp == string_array_type:
        kyb__pgppp = bodo.dict_str_arr_type
    return SeriesType(dtype, data=kyb__pgppp, index=cjg__dahou, name_typ=
        numba.typeof(val.name), dist=ziznk__uwhv)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    wcu__tibyo = c.pyapi.object_getattr_string(val, 'index')
    ryiej__oqcmt = c.pyapi.to_native_value(typ.index, wcu__tibyo).value
    c.pyapi.decref(wcu__tibyo)
    if typ.is_table_format:
        slh__kahw = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        slh__kahw.parent = val
        for gnm__icibi, uqgwm__xvdb in typ.table_type.type_to_blk.items():
            vlqdj__pskih = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[uqgwm__xvdb]))
            irkxa__igptl, fsrh__cqft = ListInstance.allocate_ex(c.context,
                c.builder, types.List(gnm__icibi), vlqdj__pskih)
            fsrh__cqft.size = vlqdj__pskih
            setattr(slh__kahw, f'block_{uqgwm__xvdb}', fsrh__cqft.value)
        pvze__sgoq = c.pyapi.call_method(val, '__len__', ())
        aqqif__vzokc = c.pyapi.long_as_longlong(pvze__sgoq)
        c.pyapi.decref(pvze__sgoq)
        slh__kahw.len = aqqif__vzokc
        milv__mrlp = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [slh__kahw._getvalue()])
    else:
        cuhg__moo = [c.context.get_constant_null(gnm__icibi) for gnm__icibi in
            typ.data]
        milv__mrlp = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            cuhg__moo)
    ail__jryj = construct_dataframe(c.context, c.builder, typ, milv__mrlp,
        ryiej__oqcmt, val, None)
    return NativeValue(ail__jryj)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        llbav__oun = df._bodo_meta['type_metadata'][1]
    else:
        llbav__oun = [None] * len(df.columns)
    yvpg__riftb = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=llbav__oun[i])) for i in range(len(df.columns))]
    yvpg__riftb = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        gnm__icibi == string_array_type else gnm__icibi) for gnm__icibi in
        yvpg__riftb]
    return tuple(yvpg__riftb)


class SeriesDtypeEnum(Enum):
    Int8 = 0
    UInt8 = 1
    Int32 = 2
    UInt32 = 3
    Int64 = 4
    UInt64 = 7
    Float32 = 5
    Float64 = 6
    Int16 = 8
    UInt16 = 9
    STRING = 10
    Bool = 11
    Decimal = 12
    Datime_Date = 13
    NP_Datetime64ns = 14
    NP_Timedelta64ns = 15
    Int128 = 16
    LIST = 18
    STRUCT = 19
    BINARY = 21
    ARRAY = 22
    PD_nullable_Int8 = 23
    PD_nullable_UInt8 = 24
    PD_nullable_Int16 = 25
    PD_nullable_UInt16 = 26
    PD_nullable_Int32 = 27
    PD_nullable_UInt32 = 28
    PD_nullable_Int64 = 29
    PD_nullable_UInt64 = 30
    PD_nullable_bool = 31
    CategoricalType = 32
    NoneType = 33
    Literal = 34
    IntegerArray = 35
    RangeIndexType = 36
    DatetimeIndexType = 37
    NumericIndexType = 38
    PeriodIndexType = 39
    IntervalIndexType = 40
    CategoricalIndexType = 41
    StringIndexType = 42
    BinaryIndexType = 43
    TimedeltaIndexType = 44
    LiteralType = 45


_one_to_one_type_to_enum_map = {types.int8: SeriesDtypeEnum.Int8.value,
    types.uint8: SeriesDtypeEnum.UInt8.value, types.int32: SeriesDtypeEnum.
    Int32.value, types.uint32: SeriesDtypeEnum.UInt32.value, types.int64:
    SeriesDtypeEnum.Int64.value, types.uint64: SeriesDtypeEnum.UInt64.value,
    types.float32: SeriesDtypeEnum.Float32.value, types.float64:
    SeriesDtypeEnum.Float64.value, types.NPDatetime('ns'): SeriesDtypeEnum.
    NP_Datetime64ns.value, types.NPTimedelta('ns'): SeriesDtypeEnum.
    NP_Timedelta64ns.value, types.bool_: SeriesDtypeEnum.Bool.value, types.
    int16: SeriesDtypeEnum.Int16.value, types.uint16: SeriesDtypeEnum.
    UInt16.value, types.Integer('int128', 128): SeriesDtypeEnum.Int128.
    value, bodo.hiframes.datetime_date_ext.datetime_date_type:
    SeriesDtypeEnum.Datime_Date.value, IntDtype(types.int8):
    SeriesDtypeEnum.PD_nullable_Int8.value, IntDtype(types.uint8):
    SeriesDtypeEnum.PD_nullable_UInt8.value, IntDtype(types.int16):
    SeriesDtypeEnum.PD_nullable_Int16.value, IntDtype(types.uint16):
    SeriesDtypeEnum.PD_nullable_UInt16.value, IntDtype(types.int32):
    SeriesDtypeEnum.PD_nullable_Int32.value, IntDtype(types.uint32):
    SeriesDtypeEnum.PD_nullable_UInt32.value, IntDtype(types.int64):
    SeriesDtypeEnum.PD_nullable_Int64.value, IntDtype(types.uint64):
    SeriesDtypeEnum.PD_nullable_UInt64.value, bytes_type: SeriesDtypeEnum.
    BINARY.value, string_type: SeriesDtypeEnum.STRING.value, bodo.bool_:
    SeriesDtypeEnum.Bool.value, types.none: SeriesDtypeEnum.NoneType.value}
_one_to_one_enum_to_type_map = {SeriesDtypeEnum.Int8.value: types.int8,
    SeriesDtypeEnum.UInt8.value: types.uint8, SeriesDtypeEnum.Int32.value:
    types.int32, SeriesDtypeEnum.UInt32.value: types.uint32,
    SeriesDtypeEnum.Int64.value: types.int64, SeriesDtypeEnum.UInt64.value:
    types.uint64, SeriesDtypeEnum.Float32.value: types.float32,
    SeriesDtypeEnum.Float64.value: types.float64, SeriesDtypeEnum.
    NP_Datetime64ns.value: types.NPDatetime('ns'), SeriesDtypeEnum.
    NP_Timedelta64ns.value: types.NPTimedelta('ns'), SeriesDtypeEnum.Int16.
    value: types.int16, SeriesDtypeEnum.UInt16.value: types.uint16,
    SeriesDtypeEnum.Int128.value: types.Integer('int128', 128),
    SeriesDtypeEnum.Datime_Date.value: bodo.hiframes.datetime_date_ext.
    datetime_date_type, SeriesDtypeEnum.PD_nullable_Int8.value: IntDtype(
    types.int8), SeriesDtypeEnum.PD_nullable_UInt8.value: IntDtype(types.
    uint8), SeriesDtypeEnum.PD_nullable_Int16.value: IntDtype(types.int16),
    SeriesDtypeEnum.PD_nullable_UInt16.value: IntDtype(types.uint16),
    SeriesDtypeEnum.PD_nullable_Int32.value: IntDtype(types.int32),
    SeriesDtypeEnum.PD_nullable_UInt32.value: IntDtype(types.uint32),
    SeriesDtypeEnum.PD_nullable_Int64.value: IntDtype(types.int64),
    SeriesDtypeEnum.PD_nullable_UInt64.value: IntDtype(types.uint64),
    SeriesDtypeEnum.BINARY.value: bytes_type, SeriesDtypeEnum.STRING.value:
    string_type, SeriesDtypeEnum.Bool.value: bodo.bool_, SeriesDtypeEnum.
    NoneType.value: types.none}


def _dtype_from_type_enum_list(typ_enum_list):
    zph__hcf, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(zph__hcf) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {zph__hcf}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        plb__egs, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return plb__egs, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        plb__egs, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:])
        return plb__egs, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        liylz__ebwan = typ_enum_list[1]
        khrt__ylpcu = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(liylz__ebwan, khrt__ylpcu)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        eish__afq = typ_enum_list[1]
        ewx__ozkhx = tuple(typ_enum_list[2:2 + eish__afq])
        elh__ljwc = typ_enum_list[2 + eish__afq:]
        ekd__hfe = []
        for i in range(eish__afq):
            elh__ljwc, mln__aqvt = _dtype_from_type_enum_list_recursor(
                elh__ljwc)
            ekd__hfe.append(mln__aqvt)
        return elh__ljwc, StructType(tuple(ekd__hfe), ewx__ozkhx)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        lqkn__hez = typ_enum_list[1]
        elh__ljwc = typ_enum_list[2:]
        return elh__ljwc, lqkn__hez
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        lqkn__hez = typ_enum_list[1]
        elh__ljwc = typ_enum_list[2:]
        return elh__ljwc, numba.types.literal(lqkn__hez)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        elh__ljwc, cvyy__ltpav = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        elh__ljwc, lzhq__ohb = _dtype_from_type_enum_list_recursor(elh__ljwc)
        elh__ljwc, pgnin__zpi = _dtype_from_type_enum_list_recursor(elh__ljwc)
        elh__ljwc, joeyu__wcbvl = _dtype_from_type_enum_list_recursor(elh__ljwc
            )
        elh__ljwc, ral__yydj = _dtype_from_type_enum_list_recursor(elh__ljwc)
        return elh__ljwc, PDCategoricalDtype(cvyy__ltpav, lzhq__ohb,
            pgnin__zpi, joeyu__wcbvl, ral__yydj)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        elh__ljwc, kxtk__fxu = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return elh__ljwc, DatetimeIndexType(kxtk__fxu)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        elh__ljwc, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        elh__ljwc, kxtk__fxu = _dtype_from_type_enum_list_recursor(elh__ljwc)
        elh__ljwc, joeyu__wcbvl = _dtype_from_type_enum_list_recursor(elh__ljwc
            )
        return elh__ljwc, NumericIndexType(dtype, kxtk__fxu, joeyu__wcbvl)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        elh__ljwc, nkt__titlt = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        elh__ljwc, kxtk__fxu = _dtype_from_type_enum_list_recursor(elh__ljwc)
        return elh__ljwc, PeriodIndexType(nkt__titlt, kxtk__fxu)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        elh__ljwc, joeyu__wcbvl = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        elh__ljwc, kxtk__fxu = _dtype_from_type_enum_list_recursor(elh__ljwc)
        return elh__ljwc, CategoricalIndexType(joeyu__wcbvl, kxtk__fxu)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        elh__ljwc, kxtk__fxu = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return elh__ljwc, RangeIndexType(kxtk__fxu)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        elh__ljwc, kxtk__fxu = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return elh__ljwc, StringIndexType(kxtk__fxu)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        elh__ljwc, kxtk__fxu = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return elh__ljwc, BinaryIndexType(kxtk__fxu)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        elh__ljwc, kxtk__fxu = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return elh__ljwc, TimedeltaIndexType(kxtk__fxu)
    else:
        raise_bodo_error(
            f'Unexpected Internal Error while converting typing metadata: unable to infer dtype for type enum {typ_enum_list[0]}. Please file the error here: https://github.com/Bodo-inc/Feedback'
            )


def _dtype_to_type_enum_list(typ):
    return guard(_dtype_to_type_enum_list_recursor, typ)


def _dtype_to_type_enum_list_recursor(typ, upcast_numeric_index=True):
    if typ.__hash__ and typ in _one_to_one_type_to_enum_map:
        return [_one_to_one_type_to_enum_map[typ]]
    if isinstance(typ, (dict, int, list, tuple, str, bool, bytes, float)):
        return [SeriesDtypeEnum.Literal.value, typ]
    elif typ is None:
        return [SeriesDtypeEnum.Literal.value, typ]
    elif is_overload_constant_int(typ):
        yos__ldlrc = get_overload_const_int(typ)
        if numba.types.maybe_literal(yos__ldlrc) == typ:
            return [SeriesDtypeEnum.LiteralType.value, yos__ldlrc]
    elif is_overload_constant_str(typ):
        yos__ldlrc = get_overload_const_str(typ)
        if numba.types.maybe_literal(yos__ldlrc) == typ:
            return [SeriesDtypeEnum.LiteralType.value, yos__ldlrc]
    elif is_overload_constant_bool(typ):
        yos__ldlrc = get_overload_const_bool(typ)
        if numba.types.maybe_literal(yos__ldlrc) == typ:
            return [SeriesDtypeEnum.LiteralType.value, yos__ldlrc]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        odzm__leqiy = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for ohcng__wglm in typ.names:
            odzm__leqiy.append(ohcng__wglm)
        for cdx__mxu in typ.data:
            odzm__leqiy += _dtype_to_type_enum_list_recursor(cdx__mxu)
        return odzm__leqiy
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        uylbc__rgcdj = _dtype_to_type_enum_list_recursor(typ.categories)
        gflea__sspx = _dtype_to_type_enum_list_recursor(typ.elem_type)
        hrrno__ayyj = _dtype_to_type_enum_list_recursor(typ.ordered)
        qfzd__srg = _dtype_to_type_enum_list_recursor(typ.data)
        freji__cywmi = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + uylbc__rgcdj + gflea__sspx + hrrno__ayyj + qfzd__srg + freji__cywmi
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                moxrm__ilgl = types.float64
                rxdnt__mklt = types.Array(moxrm__ilgl, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                moxrm__ilgl = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    rxdnt__mklt = IntegerArrayType(moxrm__ilgl)
                else:
                    rxdnt__mklt = types.Array(moxrm__ilgl, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                moxrm__ilgl = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    rxdnt__mklt = IntegerArrayType(moxrm__ilgl)
                else:
                    rxdnt__mklt = types.Array(moxrm__ilgl, 1, 'C')
            elif typ.dtype == types.bool_:
                moxrm__ilgl = typ.dtype
                rxdnt__mklt = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(moxrm__ilgl
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(rxdnt__mklt)
        else:
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(typ.dtype
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(typ.data)
    elif isinstance(typ, PeriodIndexType):
        return [SeriesDtypeEnum.PeriodIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.freq
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, CategoricalIndexType):
        return [SeriesDtypeEnum.CategoricalIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.data
            ) + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, RangeIndexType):
        return [SeriesDtypeEnum.RangeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, StringIndexType):
        return [SeriesDtypeEnum.StringIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, BinaryIndexType):
        return [SeriesDtypeEnum.BinaryIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, TimedeltaIndexType):
        return [SeriesDtypeEnum.TimedeltaIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    else:
        raise GuardException('Unable to convert type')


def _infer_series_dtype(S, array_metadata=None):
    if S.dtype == np.dtype('O'):
        if len(S.values) == 0 or S.isna().sum() == len(S):
            if array_metadata != None:
                return _dtype_from_type_enum_list(array_metadata).dtype
            elif hasattr(S, '_bodo_meta'
                ) and S._bodo_meta is not None and 'type_metadata' in S._bodo_meta and S._bodo_meta[
                'type_metadata'][1] is not None:
                rggan__ntcnt = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(rggan__ntcnt)
        return numba.typeof(S.values).dtype
    if isinstance(S.dtype, pd.core.arrays.floating.FloatingDtype):
        raise BodoError(
            """Bodo does not currently support Series constructed with Pandas FloatingArray.
Please use Series.astype() to convert any input Series input to Bodo JIT functions."""
            )
    if isinstance(S.dtype, pd.core.arrays.integer._IntegerDtype):
        return typeof_pd_int_dtype(S.dtype, None)
    elif isinstance(S.dtype, pd.CategoricalDtype):
        return bodo.typeof(S.dtype)
    elif isinstance(S.dtype, pd.StringDtype):
        return string_type
    elif isinstance(S.dtype, pd.BooleanDtype):
        return types.bool_
    if isinstance(S.dtype, pd.DatetimeTZDtype):
        nyiw__zpj = S.dtype.unit
        if nyiw__zpj != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        oup__fkcpg = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(oup__fkcpg)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    cyd__lfl = cgutils.is_not_null(builder, parent_obj)
    jzrdq__mzp = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(cyd__lfl):
        mjq__srw = pyapi.object_getattr_string(parent_obj, 'columns')
        pvze__sgoq = pyapi.call_method(mjq__srw, '__len__', ())
        builder.store(pyapi.long_as_longlong(pvze__sgoq), jzrdq__mzp)
        pyapi.decref(pvze__sgoq)
        pyapi.decref(mjq__srw)
    use_parent_obj = builder.and_(cyd__lfl, builder.icmp_unsigned('==',
        builder.load(jzrdq__mzp), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        dez__udo = df_typ.runtime_colname_typ
        context.nrt.incref(builder, dez__udo, dataframe_payload.columns)
        return pyapi.from_native_value(dez__udo, dataframe_payload.columns,
            c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        zpidh__nfc = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        zpidh__nfc = np.array(df_typ.columns, 'int64')
    else:
        zpidh__nfc = df_typ.columns
    offx__xlbx = numba.typeof(zpidh__nfc)
    ncx__nlwr = context.get_constant_generic(builder, offx__xlbx, zpidh__nfc)
    fcm__dvq = pyapi.from_native_value(offx__xlbx, ncx__nlwr, c.env_manager)
    return fcm__dvq


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (kfrt__voqx, mhkzm__viai):
        with kfrt__voqx:
            pyapi.incref(obj)
            lmun__madcl = context.insert_const_string(c.builder.module, 'numpy'
                )
            nmx__ctze = pyapi.import_module_noblock(lmun__madcl)
            if df_typ.has_runtime_cols:
                opz__blv = 0
            else:
                opz__blv = len(df_typ.columns)
            jbebf__ppm = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), opz__blv))
            fxmu__yabz = pyapi.call_method(nmx__ctze, 'arange', (jbebf__ppm,))
            pyapi.object_setattr_string(obj, 'columns', fxmu__yabz)
            pyapi.decref(nmx__ctze)
            pyapi.decref(fxmu__yabz)
            pyapi.decref(jbebf__ppm)
        with mhkzm__viai:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            yhhkh__xydct = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            lmun__madcl = context.insert_const_string(c.builder.module,
                'pandas')
            nmx__ctze = pyapi.import_module_noblock(lmun__madcl)
            df_obj = pyapi.call_method(nmx__ctze, 'DataFrame', (pyapi.
                borrow_none(), yhhkh__xydct))
            pyapi.decref(nmx__ctze)
            pyapi.decref(yhhkh__xydct)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    yesy__suk = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = yesy__suk.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        ialfp__mxkro = typ.table_type
        slh__kahw = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, ialfp__mxkro, slh__kahw)
        dkcdd__rbh = box_table(ialfp__mxkro, slh__kahw, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (ludw__exwod, qnkeq__lnvu):
            with ludw__exwod:
                yhph__xfd = pyapi.object_getattr_string(dkcdd__rbh, 'arrays')
                qprb__auyt = c.pyapi.make_none()
                if n_cols is None:
                    pvze__sgoq = pyapi.call_method(yhph__xfd, '__len__', ())
                    vlqdj__pskih = pyapi.long_as_longlong(pvze__sgoq)
                    pyapi.decref(pvze__sgoq)
                else:
                    vlqdj__pskih = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, vlqdj__pskih) as jdbw__jocpf:
                    i = jdbw__jocpf.index
                    afjba__kwgo = pyapi.list_getitem(yhph__xfd, i)
                    pep__jnums = c.builder.icmp_unsigned('!=', afjba__kwgo,
                        qprb__auyt)
                    with builder.if_then(pep__jnums):
                        ablv__zdhm = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, ablv__zdhm, afjba__kwgo)
                        pyapi.decref(ablv__zdhm)
                pyapi.decref(yhph__xfd)
                pyapi.decref(qprb__auyt)
            with qnkeq__lnvu:
                df_obj = builder.load(res)
                yhhkh__xydct = pyapi.object_getattr_string(df_obj, 'index')
                zzd__tamse = c.pyapi.call_method(dkcdd__rbh, 'to_pandas', (
                    yhhkh__xydct,))
                builder.store(zzd__tamse, res)
                pyapi.decref(df_obj)
                pyapi.decref(yhhkh__xydct)
        pyapi.decref(dkcdd__rbh)
    else:
        sok__vhgn = [builder.extract_value(dataframe_payload.data, i) for i in
            range(n_cols)]
        amhld__gto = typ.data
        for i, vnav__cdsgy, kyb__pgppp in zip(range(n_cols), sok__vhgn,
            amhld__gto):
            ldu__wjy = cgutils.alloca_once_value(builder, vnav__cdsgy)
            yxlo__ezqqh = cgutils.alloca_once_value(builder, context.
                get_constant_null(kyb__pgppp))
            pep__jnums = builder.not_(is_ll_eq(builder, ldu__wjy, yxlo__ezqqh))
            tnm__eza = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, pep__jnums))
            with builder.if_then(tnm__eza):
                ablv__zdhm = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, kyb__pgppp, vnav__cdsgy)
                arr_obj = pyapi.from_native_value(kyb__pgppp, vnav__cdsgy,
                    c.env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, ablv__zdhm, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(ablv__zdhm)
    df_obj = builder.load(res)
    fcm__dvq = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', fcm__dvq)
    pyapi.decref(fcm__dvq)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    qprb__auyt = pyapi.borrow_none()
    dfh__hyt = pyapi.unserialize(pyapi.serialize_object(slice))
    hglnx__iyjrz = pyapi.call_function_objargs(dfh__hyt, [qprb__auyt])
    xdii__yzys = pyapi.long_from_longlong(col_ind)
    spknx__huro = pyapi.tuple_pack([hglnx__iyjrz, xdii__yzys])
    khzy__iuc = pyapi.object_getattr_string(df_obj, 'iloc')
    ceae__yqq = pyapi.object_getitem(khzy__iuc, spknx__huro)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        rhwur__ujiph = pyapi.object_getattr_string(ceae__yqq, 'array')
    else:
        rhwur__ujiph = pyapi.object_getattr_string(ceae__yqq, 'values')
    if isinstance(data_typ, types.Array):
        pbp__rxj = context.insert_const_string(builder.module, 'numpy')
        gkori__hyf = pyapi.import_module_noblock(pbp__rxj)
        arr_obj = pyapi.call_method(gkori__hyf, 'ascontiguousarray', (
            rhwur__ujiph,))
        pyapi.decref(rhwur__ujiph)
        pyapi.decref(gkori__hyf)
    else:
        arr_obj = rhwur__ujiph
    pyapi.decref(dfh__hyt)
    pyapi.decref(hglnx__iyjrz)
    pyapi.decref(xdii__yzys)
    pyapi.decref(spknx__huro)
    pyapi.decref(khzy__iuc)
    pyapi.decref(ceae__yqq)
    return arr_obj


@intrinsic
def unbox_dataframe_column(typingctx, df, i=None):
    assert isinstance(df, DataFrameType) and is_overload_constant_int(i)

    def codegen(context, builder, sig, args):
        pyapi = context.get_python_api(builder)
        c = numba.core.pythonapi._UnboxContext(context, builder, pyapi)
        df_typ = sig.args[0]
        col_ind = get_overload_const_int(sig.args[1])
        data_typ = df_typ.data[col_ind]
        yesy__suk = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            yesy__suk.parent, args[1], data_typ)
        cayrw__bczm = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            slh__kahw = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            uqgwm__xvdb = df_typ.table_type.type_to_blk[data_typ]
            sbz__pmg = getattr(slh__kahw, f'block_{uqgwm__xvdb}')
            rjies__uvxqr = ListInstance(c.context, c.builder, types.List(
                data_typ), sbz__pmg)
            kgow__iin = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[col_ind])
            rjies__uvxqr.inititem(kgow__iin, cayrw__bczm.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, cayrw__bczm.value, col_ind)
        xtgt__hry = DataFramePayloadType(df_typ)
        edmyr__eml = context.nrt.meminfo_data(builder, yesy__suk.meminfo)
        rci__onzx = context.get_value_type(xtgt__hry).as_pointer()
        edmyr__eml = builder.bitcast(edmyr__eml, rci__onzx)
        builder.store(dataframe_payload._getvalue(), edmyr__eml)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        rhwur__ujiph = c.pyapi.object_getattr_string(val, 'array')
    else:
        rhwur__ujiph = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        pbp__rxj = c.context.insert_const_string(c.builder.module, 'numpy')
        gkori__hyf = c.pyapi.import_module_noblock(pbp__rxj)
        arr_obj = c.pyapi.call_method(gkori__hyf, 'ascontiguousarray', (
            rhwur__ujiph,))
        c.pyapi.decref(rhwur__ujiph)
        c.pyapi.decref(gkori__hyf)
    else:
        arr_obj = rhwur__ujiph
    fcdw__hjgj = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    yhhkh__xydct = c.pyapi.object_getattr_string(val, 'index')
    ryiej__oqcmt = c.pyapi.to_native_value(typ.index, yhhkh__xydct).value
    kqbat__hzl = c.pyapi.object_getattr_string(val, 'name')
    wwb__jgb = c.pyapi.to_native_value(typ.name_typ, kqbat__hzl).value
    jxz__sople = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, fcdw__hjgj, ryiej__oqcmt, wwb__jgb)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(yhhkh__xydct)
    c.pyapi.decref(kqbat__hzl)
    return NativeValue(jxz__sople)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        lpzq__lco = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(lpzq__lco._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    lmun__madcl = c.context.insert_const_string(c.builder.module, 'pandas')
    iny__lailp = c.pyapi.import_module_noblock(lmun__madcl)
    enip__acsk = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, enip__acsk.data)
    c.context.nrt.incref(c.builder, typ.index, enip__acsk.index)
    c.context.nrt.incref(c.builder, typ.name_typ, enip__acsk.name)
    arr_obj = c.pyapi.from_native_value(typ.data, enip__acsk.data, c.
        env_manager)
    yhhkh__xydct = c.pyapi.from_native_value(typ.index, enip__acsk.index, c
        .env_manager)
    kqbat__hzl = c.pyapi.from_native_value(typ.name_typ, enip__acsk.name, c
        .env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(iny__lailp, 'Series', (arr_obj, yhhkh__xydct,
        dtype, kqbat__hzl))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(yhhkh__xydct)
    c.pyapi.decref(kqbat__hzl)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(iny__lailp)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    gqla__jfyq = []
    for npnuk__vex in typ_list:
        if isinstance(npnuk__vex, int) and not isinstance(npnuk__vex, bool):
            dvsi__mjpk = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), npnuk__vex))
        else:
            lhbwq__hlyad = numba.typeof(npnuk__vex)
            ycpac__gtu = context.get_constant_generic(builder, lhbwq__hlyad,
                npnuk__vex)
            dvsi__mjpk = pyapi.from_native_value(lhbwq__hlyad, ycpac__gtu,
                env_manager)
        gqla__jfyq.append(dvsi__mjpk)
    jqqxi__yimo = pyapi.list_pack(gqla__jfyq)
    for val in gqla__jfyq:
        pyapi.decref(val)
    return jqqxi__yimo


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    pye__diyv = not typ.has_runtime_cols
    hii__sumq = 2 if pye__diyv else 1
    wqapw__mfsak = pyapi.dict_new(hii__sumq)
    rhnk__ztuk = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    pyapi.dict_setitem_string(wqapw__mfsak, 'dist', rhnk__ztuk)
    pyapi.decref(rhnk__ztuk)
    if pye__diyv:
        huv__zmgg = _dtype_to_type_enum_list(typ.index)
        if huv__zmgg != None:
            kvomb__cmit = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, huv__zmgg)
        else:
            kvomb__cmit = pyapi.make_none()
        if typ.is_table_format:
            gnm__icibi = typ.table_type
            cwson__zogo = pyapi.list_new(lir.Constant(lir.IntType(64), len(
                typ.data)))
            for uqgwm__xvdb, dtype in gnm__icibi.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                vlqdj__pskih = c.context.get_constant(types.int64, len(
                    gnm__icibi.block_to_arr_ind[uqgwm__xvdb]))
                aylbk__jzxub = c.context.make_constant_array(c.builder,
                    types.Array(types.int64, 1, 'C'), np.array(gnm__icibi.
                    block_to_arr_ind[uqgwm__xvdb], dtype=np.int64))
                avoy__elpp = c.context.make_array(types.Array(types.int64, 
                    1, 'C'))(c.context, c.builder, aylbk__jzxub)
                with cgutils.for_range(c.builder, vlqdj__pskih) as jdbw__jocpf:
                    i = jdbw__jocpf.index
                    pjspw__ccaqc = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), avoy__elpp, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(cwson__zogo, pjspw__ccaqc, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            empc__bwyzx = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    jqqxi__yimo = type_enum_list_to_py_list_obj(pyapi,
                        context, builder, c.env_manager, typ_list)
                else:
                    jqqxi__yimo = pyapi.make_none()
                empc__bwyzx.append(jqqxi__yimo)
            cwson__zogo = pyapi.list_pack(empc__bwyzx)
            for val in empc__bwyzx:
                pyapi.decref(val)
        vnwbf__pmly = pyapi.list_pack([kvomb__cmit, cwson__zogo])
        pyapi.dict_setitem_string(wqapw__mfsak, 'type_metadata', vnwbf__pmly)
    pyapi.object_setattr_string(obj, '_bodo_meta', wqapw__mfsak)
    pyapi.decref(wqapw__mfsak)


def get_series_dtype_handle_null_int_and_hetrogenous(series_typ):
    if isinstance(series_typ, HeterogeneousSeriesType):
        return None
    if isinstance(series_typ.dtype, types.Number) and isinstance(series_typ
        .data, IntegerArrayType):
        return IntDtype(series_typ.dtype)
    return series_typ.dtype


def _set_bodo_meta_series(obj, c, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    wqapw__mfsak = pyapi.dict_new(2)
    rhnk__ztuk = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    huv__zmgg = _dtype_to_type_enum_list(typ.index)
    if huv__zmgg != None:
        kvomb__cmit = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, huv__zmgg)
    else:
        kvomb__cmit = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            eebt__iua = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            eebt__iua = pyapi.make_none()
    else:
        eebt__iua = pyapi.make_none()
    sbjx__ukjk = pyapi.list_pack([kvomb__cmit, eebt__iua])
    pyapi.dict_setitem_string(wqapw__mfsak, 'type_metadata', sbjx__ukjk)
    pyapi.decref(sbjx__ukjk)
    pyapi.dict_setitem_string(wqapw__mfsak, 'dist', rhnk__ztuk)
    pyapi.object_setattr_string(obj, '_bodo_meta', wqapw__mfsak)
    pyapi.decref(wqapw__mfsak)
    pyapi.decref(rhnk__ztuk)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as lxwa__azvx:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    dsm__slnc = numba.np.numpy_support.map_layout(val)
    xvdi__zba = not val.flags.writeable
    return types.Array(dtype, val.ndim, dsm__slnc, readonly=xvdi__zba)


def _infer_ndarray_obj_dtype(val):
    if not val.dtype == np.dtype('O'):
        raise BodoError('Unsupported array dtype: {}'.format(val.dtype))
    i = 0
    while i < len(val) and (pd.api.types.is_scalar(val[i]) and pd.isna(val[
        i]) or not pd.api.types.is_scalar(val[i]) and len(val[i]) == 0):
        i += 1
    if i == len(val):
        warnings.warn(BodoWarning(
            'Empty object array passed to Bodo, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    qxcdr__zbq = val[i]
    if isinstance(qxcdr__zbq, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(qxcdr__zbq, bytes):
        return binary_array_type
    elif isinstance(qxcdr__zbq, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(qxcdr__zbq, (int, np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(qxcdr__zbq))
    elif isinstance(qxcdr__zbq, (dict, Dict)) and all(isinstance(bfdu__odfv,
        str) for bfdu__odfv in qxcdr__zbq.keys()):
        ewx__ozkhx = tuple(qxcdr__zbq.keys())
        haru__oaeb = tuple(_get_struct_value_arr_type(v) for v in
            qxcdr__zbq.values())
        return StructArrayType(haru__oaeb, ewx__ozkhx)
    elif isinstance(qxcdr__zbq, (dict, Dict)):
        xdj__abkhl = numba.typeof(_value_to_array(list(qxcdr__zbq.keys())))
        wjim__rnjws = numba.typeof(_value_to_array(list(qxcdr__zbq.values())))
        xdj__abkhl = to_str_arr_if_dict_array(xdj__abkhl)
        wjim__rnjws = to_str_arr_if_dict_array(wjim__rnjws)
        return MapArrayType(xdj__abkhl, wjim__rnjws)
    elif isinstance(qxcdr__zbq, tuple):
        haru__oaeb = tuple(_get_struct_value_arr_type(v) for v in qxcdr__zbq)
        return TupleArrayType(haru__oaeb)
    if isinstance(qxcdr__zbq, (list, np.ndarray, pd.arrays.BooleanArray, pd
        .arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(qxcdr__zbq, list):
            qxcdr__zbq = _value_to_array(qxcdr__zbq)
        buuyr__adjcd = numba.typeof(qxcdr__zbq)
        buuyr__adjcd = to_str_arr_if_dict_array(buuyr__adjcd)
        return ArrayItemArrayType(buuyr__adjcd)
    if isinstance(qxcdr__zbq, datetime.date):
        return datetime_date_array_type
    if isinstance(qxcdr__zbq, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(qxcdr__zbq, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(qxcdr__zbq, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {qxcdr__zbq}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    yub__bbw = val.copy()
    yub__bbw.append(None)
    vnav__cdsgy = np.array(yub__bbw, np.object_)
    if len(val) and isinstance(val[0], float):
        vnav__cdsgy = np.array(val, np.float64)
    return vnav__cdsgy


def _get_struct_value_arr_type(v):
    if isinstance(v, (dict, Dict)):
        return numba.typeof(_value_to_array(v))
    if isinstance(v, list):
        return dtype_to_array_type(numba.typeof(_value_to_array(v)))
    if pd.api.types.is_scalar(v) and pd.isna(v):
        warnings.warn(BodoWarning(
            'Field value in struct array is NA, which causes ambiguity in typing. This can cause errors in parallel execution.'
            ))
        return string_array_type
    kyb__pgppp = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        kyb__pgppp = to_nullable_type(kyb__pgppp)
    return kyb__pgppp
