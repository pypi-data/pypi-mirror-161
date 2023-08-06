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
_use_dict_str_type = False


def _set_bodo_meta_in_pandas():
    if '_bodo_meta' not in pd.Series._metadata:
        pd.Series._metadata.append('_bodo_meta')
    if '_bodo_meta' not in pd.DataFrame._metadata:
        pd.DataFrame._metadata.append('_bodo_meta')


_set_bodo_meta_in_pandas()


@typeof_impl.register(pd.DataFrame)
def typeof_pd_dataframe(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    svom__gysay = tuple(val.columns.to_list())
    ckqd__kett = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        oie__knzxh = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        oie__knzxh = numba.typeof(val.index)
    jux__dzd = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    gotif__idmd = len(ckqd__kett) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(ckqd__kett, oie__knzxh, svom__gysay, jux__dzd,
        is_table_format=gotif__idmd)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    jux__dzd = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        hbm__zut = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        hbm__zut = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    borl__zmjdy = dtype_to_array_type(dtype)
    if _use_dict_str_type and borl__zmjdy == string_array_type:
        borl__zmjdy = bodo.dict_str_arr_type
    return SeriesType(dtype, data=borl__zmjdy, index=hbm__zut, name_typ=
        numba.typeof(val.name), dist=jux__dzd)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    yfi__geig = c.pyapi.object_getattr_string(val, 'index')
    yjmj__cfh = c.pyapi.to_native_value(typ.index, yfi__geig).value
    c.pyapi.decref(yfi__geig)
    if typ.is_table_format:
        lny__tbwks = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        lny__tbwks.parent = val
        for psroa__vnk, wevfh__yim in typ.table_type.type_to_blk.items():
            rhqbf__xvoj = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[wevfh__yim]))
            avqni__mjtjo, lot__mnut = ListInstance.allocate_ex(c.context, c
                .builder, types.List(psroa__vnk), rhqbf__xvoj)
            lot__mnut.size = rhqbf__xvoj
            setattr(lny__tbwks, f'block_{wevfh__yim}', lot__mnut.value)
        narc__utd = c.pyapi.call_method(val, '__len__', ())
        pzb__mfek = c.pyapi.long_as_longlong(narc__utd)
        c.pyapi.decref(narc__utd)
        lny__tbwks.len = pzb__mfek
        pjv__ptj = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [lny__tbwks._getvalue()])
    else:
        qmukm__dgc = [c.context.get_constant_null(psroa__vnk) for
            psroa__vnk in typ.data]
        pjv__ptj = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            qmukm__dgc)
    ados__gpest = construct_dataframe(c.context, c.builder, typ, pjv__ptj,
        yjmj__cfh, val, None)
    return NativeValue(ados__gpest)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        hzhy__nwhhv = df._bodo_meta['type_metadata'][1]
    else:
        hzhy__nwhhv = [None] * len(df.columns)
    wmped__twfx = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=hzhy__nwhhv[i])) for i in range(len(df.columns))]
    wmped__twfx = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        psroa__vnk == string_array_type else psroa__vnk) for psroa__vnk in
        wmped__twfx]
    return tuple(wmped__twfx)


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
    krs__jvtzo, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(krs__jvtzo) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {krs__jvtzo}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        gdmxd__qbdke, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return gdmxd__qbdke, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        gdmxd__qbdke, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return gdmxd__qbdke, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        hinjb__ajo = typ_enum_list[1]
        pnhxr__mmhfk = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(hinjb__ajo, pnhxr__mmhfk)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        grh__duu = typ_enum_list[1]
        xms__vbg = tuple(typ_enum_list[2:2 + grh__duu])
        rui__prbs = typ_enum_list[2 + grh__duu:]
        amca__bcdo = []
        for i in range(grh__duu):
            rui__prbs, bcnl__cut = _dtype_from_type_enum_list_recursor(
                rui__prbs)
            amca__bcdo.append(bcnl__cut)
        return rui__prbs, StructType(tuple(amca__bcdo), xms__vbg)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        hpp__oexg = typ_enum_list[1]
        rui__prbs = typ_enum_list[2:]
        return rui__prbs, hpp__oexg
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        hpp__oexg = typ_enum_list[1]
        rui__prbs = typ_enum_list[2:]
        return rui__prbs, numba.types.literal(hpp__oexg)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        rui__prbs, vhtcl__bnfph = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        rui__prbs, ynpa__ctla = _dtype_from_type_enum_list_recursor(rui__prbs)
        rui__prbs, txx__pnb = _dtype_from_type_enum_list_recursor(rui__prbs)
        rui__prbs, akj__oare = _dtype_from_type_enum_list_recursor(rui__prbs)
        rui__prbs, whcm__dcwbn = _dtype_from_type_enum_list_recursor(rui__prbs)
        return rui__prbs, PDCategoricalDtype(vhtcl__bnfph, ynpa__ctla,
            txx__pnb, akj__oare, whcm__dcwbn)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        rui__prbs, azrjn__acgg = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return rui__prbs, DatetimeIndexType(azrjn__acgg)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        rui__prbs, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        rui__prbs, azrjn__acgg = _dtype_from_type_enum_list_recursor(rui__prbs)
        rui__prbs, akj__oare = _dtype_from_type_enum_list_recursor(rui__prbs)
        return rui__prbs, NumericIndexType(dtype, azrjn__acgg, akj__oare)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        rui__prbs, exmwx__myqlo = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        rui__prbs, azrjn__acgg = _dtype_from_type_enum_list_recursor(rui__prbs)
        return rui__prbs, PeriodIndexType(exmwx__myqlo, azrjn__acgg)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        rui__prbs, akj__oare = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        rui__prbs, azrjn__acgg = _dtype_from_type_enum_list_recursor(rui__prbs)
        return rui__prbs, CategoricalIndexType(akj__oare, azrjn__acgg)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        rui__prbs, azrjn__acgg = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return rui__prbs, RangeIndexType(azrjn__acgg)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        rui__prbs, azrjn__acgg = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return rui__prbs, StringIndexType(azrjn__acgg)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        rui__prbs, azrjn__acgg = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return rui__prbs, BinaryIndexType(azrjn__acgg)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        rui__prbs, azrjn__acgg = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return rui__prbs, TimedeltaIndexType(azrjn__acgg)
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
        sem__mad = get_overload_const_int(typ)
        if numba.types.maybe_literal(sem__mad) == typ:
            return [SeriesDtypeEnum.LiteralType.value, sem__mad]
    elif is_overload_constant_str(typ):
        sem__mad = get_overload_const_str(typ)
        if numba.types.maybe_literal(sem__mad) == typ:
            return [SeriesDtypeEnum.LiteralType.value, sem__mad]
    elif is_overload_constant_bool(typ):
        sem__mad = get_overload_const_bool(typ)
        if numba.types.maybe_literal(sem__mad) == typ:
            return [SeriesDtypeEnum.LiteralType.value, sem__mad]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        vqs__vbxwz = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for tvd__sifj in typ.names:
            vqs__vbxwz.append(tvd__sifj)
        for czn__grsvf in typ.data:
            vqs__vbxwz += _dtype_to_type_enum_list_recursor(czn__grsvf)
        return vqs__vbxwz
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        zyyfv__xmazd = _dtype_to_type_enum_list_recursor(typ.categories)
        cjn__bmvy = _dtype_to_type_enum_list_recursor(typ.elem_type)
        ftec__ijw = _dtype_to_type_enum_list_recursor(typ.ordered)
        wtb__xnam = _dtype_to_type_enum_list_recursor(typ.data)
        ijdtl__kwu = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + zyyfv__xmazd + cjn__bmvy + ftec__ijw + wtb__xnam + ijdtl__kwu
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                scqs__dlpsj = types.float64
                dqad__vooh = types.Array(scqs__dlpsj, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                scqs__dlpsj = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    dqad__vooh = IntegerArrayType(scqs__dlpsj)
                else:
                    dqad__vooh = types.Array(scqs__dlpsj, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                scqs__dlpsj = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    dqad__vooh = IntegerArrayType(scqs__dlpsj)
                else:
                    dqad__vooh = types.Array(scqs__dlpsj, 1, 'C')
            elif typ.dtype == types.bool_:
                scqs__dlpsj = typ.dtype
                dqad__vooh = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(scqs__dlpsj
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(dqad__vooh)
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
                cevr__jfkd = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(cevr__jfkd)
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
        odwxb__zojm = S.dtype.unit
        if odwxb__zojm != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        buhcm__jcblu = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(buhcm__jcblu)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    lvao__hzwl = cgutils.is_not_null(builder, parent_obj)
    yisqb__uwpj = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(lvao__hzwl):
        qbsd__xtd = pyapi.object_getattr_string(parent_obj, 'columns')
        narc__utd = pyapi.call_method(qbsd__xtd, '__len__', ())
        builder.store(pyapi.long_as_longlong(narc__utd), yisqb__uwpj)
        pyapi.decref(narc__utd)
        pyapi.decref(qbsd__xtd)
    use_parent_obj = builder.and_(lvao__hzwl, builder.icmp_unsigned('==',
        builder.load(yisqb__uwpj), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        pzi__kdghz = df_typ.runtime_colname_typ
        context.nrt.incref(builder, pzi__kdghz, dataframe_payload.columns)
        return pyapi.from_native_value(pzi__kdghz, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        coh__odef = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        coh__odef = np.array(df_typ.columns, 'int64')
    else:
        coh__odef = df_typ.columns
    rodk__oljba = numba.typeof(coh__odef)
    vuj__aiwc = context.get_constant_generic(builder, rodk__oljba, coh__odef)
    aezv__sdoua = pyapi.from_native_value(rodk__oljba, vuj__aiwc, c.env_manager
        )
    return aezv__sdoua


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (uoqbz__uqg, lpmqw__wwat):
        with uoqbz__uqg:
            pyapi.incref(obj)
            gwmb__knpgt = context.insert_const_string(c.builder.module, 'numpy'
                )
            dwubq__bxg = pyapi.import_module_noblock(gwmb__knpgt)
            if df_typ.has_runtime_cols:
                lkyv__hzn = 0
            else:
                lkyv__hzn = len(df_typ.columns)
            clzdt__upxli = pyapi.long_from_longlong(lir.Constant(lir.
                IntType(64), lkyv__hzn))
            lpzr__yocze = pyapi.call_method(dwubq__bxg, 'arange', (
                clzdt__upxli,))
            pyapi.object_setattr_string(obj, 'columns', lpzr__yocze)
            pyapi.decref(dwubq__bxg)
            pyapi.decref(lpzr__yocze)
            pyapi.decref(clzdt__upxli)
        with lpmqw__wwat:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            aoy__lugn = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            gwmb__knpgt = context.insert_const_string(c.builder.module,
                'pandas')
            dwubq__bxg = pyapi.import_module_noblock(gwmb__knpgt)
            df_obj = pyapi.call_method(dwubq__bxg, 'DataFrame', (pyapi.
                borrow_none(), aoy__lugn))
            pyapi.decref(dwubq__bxg)
            pyapi.decref(aoy__lugn)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    uovqt__rrhok = cgutils.create_struct_proxy(typ)(context, builder, value=val
        )
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = uovqt__rrhok.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        nms__iaob = typ.table_type
        lny__tbwks = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, nms__iaob, lny__tbwks)
        maj__cmdh = box_table(nms__iaob, lny__tbwks, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (kjsj__rizv, irlse__zjxfd):
            with kjsj__rizv:
                ted__exk = pyapi.object_getattr_string(maj__cmdh, 'arrays')
                tset__xlw = c.pyapi.make_none()
                if n_cols is None:
                    narc__utd = pyapi.call_method(ted__exk, '__len__', ())
                    rhqbf__xvoj = pyapi.long_as_longlong(narc__utd)
                    pyapi.decref(narc__utd)
                else:
                    rhqbf__xvoj = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, rhqbf__xvoj) as gkt__ptyd:
                    i = gkt__ptyd.index
                    hlmez__bpy = pyapi.list_getitem(ted__exk, i)
                    jugm__qwhf = c.builder.icmp_unsigned('!=', hlmez__bpy,
                        tset__xlw)
                    with builder.if_then(jugm__qwhf):
                        upqph__ftbcs = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, upqph__ftbcs, hlmez__bpy)
                        pyapi.decref(upqph__ftbcs)
                pyapi.decref(ted__exk)
                pyapi.decref(tset__xlw)
            with irlse__zjxfd:
                df_obj = builder.load(res)
                aoy__lugn = pyapi.object_getattr_string(df_obj, 'index')
                opusu__rhie = c.pyapi.call_method(maj__cmdh, 'to_pandas', (
                    aoy__lugn,))
                builder.store(opusu__rhie, res)
                pyapi.decref(df_obj)
                pyapi.decref(aoy__lugn)
        pyapi.decref(maj__cmdh)
    else:
        mvjoe__kkf = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        ggk__pwze = typ.data
        for i, bmnmu__prha, borl__zmjdy in zip(range(n_cols), mvjoe__kkf,
            ggk__pwze):
            uxgl__nias = cgutils.alloca_once_value(builder, bmnmu__prha)
            xchm__ums = cgutils.alloca_once_value(builder, context.
                get_constant_null(borl__zmjdy))
            jugm__qwhf = builder.not_(is_ll_eq(builder, uxgl__nias, xchm__ums))
            theo__dbx = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, jugm__qwhf))
            with builder.if_then(theo__dbx):
                upqph__ftbcs = pyapi.long_from_longlong(context.
                    get_constant(types.int64, i))
                context.nrt.incref(builder, borl__zmjdy, bmnmu__prha)
                arr_obj = pyapi.from_native_value(borl__zmjdy, bmnmu__prha,
                    c.env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, upqph__ftbcs, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(upqph__ftbcs)
    df_obj = builder.load(res)
    aezv__sdoua = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', aezv__sdoua)
    pyapi.decref(aezv__sdoua)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    tset__xlw = pyapi.borrow_none()
    opl__kpx = pyapi.unserialize(pyapi.serialize_object(slice))
    zgqg__tfzc = pyapi.call_function_objargs(opl__kpx, [tset__xlw])
    yne__egtg = pyapi.long_from_longlong(col_ind)
    ibrj__dqpyf = pyapi.tuple_pack([zgqg__tfzc, yne__egtg])
    pchu__vmp = pyapi.object_getattr_string(df_obj, 'iloc')
    cwj__hqydd = pyapi.object_getitem(pchu__vmp, ibrj__dqpyf)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        oqdvm__fgyrb = pyapi.object_getattr_string(cwj__hqydd, 'array')
    else:
        oqdvm__fgyrb = pyapi.object_getattr_string(cwj__hqydd, 'values')
    if isinstance(data_typ, types.Array):
        zqy__dnq = context.insert_const_string(builder.module, 'numpy')
        unour__jxoe = pyapi.import_module_noblock(zqy__dnq)
        arr_obj = pyapi.call_method(unour__jxoe, 'ascontiguousarray', (
            oqdvm__fgyrb,))
        pyapi.decref(oqdvm__fgyrb)
        pyapi.decref(unour__jxoe)
    else:
        arr_obj = oqdvm__fgyrb
    pyapi.decref(opl__kpx)
    pyapi.decref(zgqg__tfzc)
    pyapi.decref(yne__egtg)
    pyapi.decref(ibrj__dqpyf)
    pyapi.decref(pchu__vmp)
    pyapi.decref(cwj__hqydd)
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
        uovqt__rrhok = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            uovqt__rrhok.parent, args[1], data_typ)
        wxmt__ano = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            lny__tbwks = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            wevfh__yim = df_typ.table_type.type_to_blk[data_typ]
            qstnk__lhxor = getattr(lny__tbwks, f'block_{wevfh__yim}')
            wilkh__evh = ListInstance(c.context, c.builder, types.List(
                data_typ), qstnk__lhxor)
            zrbws__mcr = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[col_ind])
            wilkh__evh.inititem(zrbws__mcr, wxmt__ano.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, wxmt__ano.value, col_ind)
        man__zbjh = DataFramePayloadType(df_typ)
        thayl__xpgjy = context.nrt.meminfo_data(builder, uovqt__rrhok.meminfo)
        nvqpl__krkl = context.get_value_type(man__zbjh).as_pointer()
        thayl__xpgjy = builder.bitcast(thayl__xpgjy, nvqpl__krkl)
        builder.store(dataframe_payload._getvalue(), thayl__xpgjy)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        oqdvm__fgyrb = c.pyapi.object_getattr_string(val, 'array')
    else:
        oqdvm__fgyrb = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        zqy__dnq = c.context.insert_const_string(c.builder.module, 'numpy')
        unour__jxoe = c.pyapi.import_module_noblock(zqy__dnq)
        arr_obj = c.pyapi.call_method(unour__jxoe, 'ascontiguousarray', (
            oqdvm__fgyrb,))
        c.pyapi.decref(oqdvm__fgyrb)
        c.pyapi.decref(unour__jxoe)
    else:
        arr_obj = oqdvm__fgyrb
    frp__lcqpq = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    aoy__lugn = c.pyapi.object_getattr_string(val, 'index')
    yjmj__cfh = c.pyapi.to_native_value(typ.index, aoy__lugn).value
    ygba__cnp = c.pyapi.object_getattr_string(val, 'name')
    yeuvn__kap = c.pyapi.to_native_value(typ.name_typ, ygba__cnp).value
    ykvy__bpoti = bodo.hiframes.pd_series_ext.construct_series(c.context, c
        .builder, typ, frp__lcqpq, yjmj__cfh, yeuvn__kap)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(aoy__lugn)
    c.pyapi.decref(ygba__cnp)
    return NativeValue(ykvy__bpoti)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        oexfk__bjb = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(oexfk__bjb._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    gwmb__knpgt = c.context.insert_const_string(c.builder.module, 'pandas')
    msv__nnj = c.pyapi.import_module_noblock(gwmb__knpgt)
    rco__twh = bodo.hiframes.pd_series_ext.get_series_payload(c.context, c.
        builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, rco__twh.data)
    c.context.nrt.incref(c.builder, typ.index, rco__twh.index)
    c.context.nrt.incref(c.builder, typ.name_typ, rco__twh.name)
    arr_obj = c.pyapi.from_native_value(typ.data, rco__twh.data, c.env_manager)
    aoy__lugn = c.pyapi.from_native_value(typ.index, rco__twh.index, c.
        env_manager)
    ygba__cnp = c.pyapi.from_native_value(typ.name_typ, rco__twh.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(msv__nnj, 'Series', (arr_obj, aoy__lugn,
        dtype, ygba__cnp))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(aoy__lugn)
    c.pyapi.decref(ygba__cnp)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(msv__nnj)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    fqp__vvd = []
    for zsfe__bktc in typ_list:
        if isinstance(zsfe__bktc, int) and not isinstance(zsfe__bktc, bool):
            kwp__bxdt = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), zsfe__bktc))
        else:
            nebk__hklub = numba.typeof(zsfe__bktc)
            qko__pkk = context.get_constant_generic(builder, nebk__hklub,
                zsfe__bktc)
            kwp__bxdt = pyapi.from_native_value(nebk__hklub, qko__pkk,
                env_manager)
        fqp__vvd.append(kwp__bxdt)
    cniuf__wllo = pyapi.list_pack(fqp__vvd)
    for val in fqp__vvd:
        pyapi.decref(val)
    return cniuf__wllo


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    gwjen__wcvqe = not typ.has_runtime_cols
    gsunu__rlk = 2 if gwjen__wcvqe else 1
    vcxzh__yjpq = pyapi.dict_new(gsunu__rlk)
    ggt__zuff = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.
        dist.value))
    pyapi.dict_setitem_string(vcxzh__yjpq, 'dist', ggt__zuff)
    pyapi.decref(ggt__zuff)
    if gwjen__wcvqe:
        tsxta__fyflk = _dtype_to_type_enum_list(typ.index)
        if tsxta__fyflk != None:
            qlok__aqni = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, tsxta__fyflk)
        else:
            qlok__aqni = pyapi.make_none()
        if typ.is_table_format:
            psroa__vnk = typ.table_type
            sntu__quk = pyapi.list_new(lir.Constant(lir.IntType(64), len(
                typ.data)))
            for wevfh__yim, dtype in psroa__vnk.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                rhqbf__xvoj = c.context.get_constant(types.int64, len(
                    psroa__vnk.block_to_arr_ind[wevfh__yim]))
                zvzqf__ncy = c.context.make_constant_array(c.builder, types
                    .Array(types.int64, 1, 'C'), np.array(psroa__vnk.
                    block_to_arr_ind[wevfh__yim], dtype=np.int64))
                vehnv__pmr = c.context.make_array(types.Array(types.int64, 
                    1, 'C'))(c.context, c.builder, zvzqf__ncy)
                with cgutils.for_range(c.builder, rhqbf__xvoj) as gkt__ptyd:
                    i = gkt__ptyd.index
                    npq__rzn = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), vehnv__pmr, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(sntu__quk, npq__rzn, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            waux__ucydg = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    cniuf__wllo = type_enum_list_to_py_list_obj(pyapi,
                        context, builder, c.env_manager, typ_list)
                else:
                    cniuf__wllo = pyapi.make_none()
                waux__ucydg.append(cniuf__wllo)
            sntu__quk = pyapi.list_pack(waux__ucydg)
            for val in waux__ucydg:
                pyapi.decref(val)
        pkqix__zdb = pyapi.list_pack([qlok__aqni, sntu__quk])
        pyapi.dict_setitem_string(vcxzh__yjpq, 'type_metadata', pkqix__zdb)
    pyapi.object_setattr_string(obj, '_bodo_meta', vcxzh__yjpq)
    pyapi.decref(vcxzh__yjpq)


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
    vcxzh__yjpq = pyapi.dict_new(2)
    ggt__zuff = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ.
        dist.value))
    tsxta__fyflk = _dtype_to_type_enum_list(typ.index)
    if tsxta__fyflk != None:
        qlok__aqni = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, tsxta__fyflk)
    else:
        qlok__aqni = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            eadc__knjmn = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            eadc__knjmn = pyapi.make_none()
    else:
        eadc__knjmn = pyapi.make_none()
    koa__pnjy = pyapi.list_pack([qlok__aqni, eadc__knjmn])
    pyapi.dict_setitem_string(vcxzh__yjpq, 'type_metadata', koa__pnjy)
    pyapi.decref(koa__pnjy)
    pyapi.dict_setitem_string(vcxzh__yjpq, 'dist', ggt__zuff)
    pyapi.object_setattr_string(obj, '_bodo_meta', vcxzh__yjpq)
    pyapi.decref(vcxzh__yjpq)
    pyapi.decref(ggt__zuff)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as zqky__jczuq:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    yzzuf__lvy = numba.np.numpy_support.map_layout(val)
    othd__fuy = not val.flags.writeable
    return types.Array(dtype, val.ndim, yzzuf__lvy, readonly=othd__fuy)


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
    izbf__wfs = val[i]
    if isinstance(izbf__wfs, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(izbf__wfs, bytes):
        return binary_array_type
    elif isinstance(izbf__wfs, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(izbf__wfs, (int, np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(izbf__wfs))
    elif isinstance(izbf__wfs, (dict, Dict)) and all(isinstance(cvbe__pvzm,
        str) for cvbe__pvzm in izbf__wfs.keys()):
        xms__vbg = tuple(izbf__wfs.keys())
        xebrk__qddwz = tuple(_get_struct_value_arr_type(v) for v in
            izbf__wfs.values())
        return StructArrayType(xebrk__qddwz, xms__vbg)
    elif isinstance(izbf__wfs, (dict, Dict)):
        weaxf__oyvuc = numba.typeof(_value_to_array(list(izbf__wfs.keys())))
        ned__yrfps = numba.typeof(_value_to_array(list(izbf__wfs.values())))
        weaxf__oyvuc = to_str_arr_if_dict_array(weaxf__oyvuc)
        ned__yrfps = to_str_arr_if_dict_array(ned__yrfps)
        return MapArrayType(weaxf__oyvuc, ned__yrfps)
    elif isinstance(izbf__wfs, tuple):
        xebrk__qddwz = tuple(_get_struct_value_arr_type(v) for v in izbf__wfs)
        return TupleArrayType(xebrk__qddwz)
    if isinstance(izbf__wfs, (list, np.ndarray, pd.arrays.BooleanArray, pd.
        arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(izbf__wfs, list):
            izbf__wfs = _value_to_array(izbf__wfs)
        zvsdu__ibxw = numba.typeof(izbf__wfs)
        zvsdu__ibxw = to_str_arr_if_dict_array(zvsdu__ibxw)
        return ArrayItemArrayType(zvsdu__ibxw)
    if isinstance(izbf__wfs, datetime.date):
        return datetime_date_array_type
    if isinstance(izbf__wfs, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(izbf__wfs, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(izbf__wfs, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {izbf__wfs}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    hmv__zbav = val.copy()
    hmv__zbav.append(None)
    bmnmu__prha = np.array(hmv__zbav, np.object_)
    if len(val) and isinstance(val[0], float):
        bmnmu__prha = np.array(val, np.float64)
    return bmnmu__prha


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
    borl__zmjdy = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        borl__zmjdy = to_nullable_type(borl__zmjdy)
    return borl__zmjdy
