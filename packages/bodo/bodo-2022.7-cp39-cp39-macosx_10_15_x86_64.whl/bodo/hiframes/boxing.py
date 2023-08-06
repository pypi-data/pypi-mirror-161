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
    golz__hbfpb = tuple(val.columns.to_list())
    jpr__basl = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        ydfr__vzbqt = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        ydfr__vzbqt = numba.typeof(val.index)
    ahmat__pknic = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    vkdoc__zbncj = len(jpr__basl) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(jpr__basl, ydfr__vzbqt, golz__hbfpb, ahmat__pknic,
        is_table_format=vkdoc__zbncj)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    ahmat__pknic = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        zoq__cmoll = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        zoq__cmoll = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    mapwb__rjxw = dtype_to_array_type(dtype)
    if _use_dict_str_type and mapwb__rjxw == string_array_type:
        mapwb__rjxw = bodo.dict_str_arr_type
    return SeriesType(dtype, data=mapwb__rjxw, index=zoq__cmoll, name_typ=
        numba.typeof(val.name), dist=ahmat__pknic)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    dmlwr__bwh = c.pyapi.object_getattr_string(val, 'index')
    flss__bsmet = c.pyapi.to_native_value(typ.index, dmlwr__bwh).value
    c.pyapi.decref(dmlwr__bwh)
    if typ.is_table_format:
        pxa__vtfzp = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        pxa__vtfzp.parent = val
        for enjqk__uom, puvcl__dud in typ.table_type.type_to_blk.items():
            nmxp__vjn = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[puvcl__dud]))
            coxx__tdnga, sjlpi__vpk = ListInstance.allocate_ex(c.context, c
                .builder, types.List(enjqk__uom), nmxp__vjn)
            sjlpi__vpk.size = nmxp__vjn
            setattr(pxa__vtfzp, f'block_{puvcl__dud}', sjlpi__vpk.value)
        huk__svr = c.pyapi.call_method(val, '__len__', ())
        psqo__xmuq = c.pyapi.long_as_longlong(huk__svr)
        c.pyapi.decref(huk__svr)
        pxa__vtfzp.len = psqo__xmuq
        wijrk__rzf = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [pxa__vtfzp._getvalue()])
    else:
        mlua__frzsk = [c.context.get_constant_null(enjqk__uom) for
            enjqk__uom in typ.data]
        wijrk__rzf = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            mlua__frzsk)
    qkhs__bwpw = construct_dataframe(c.context, c.builder, typ, wijrk__rzf,
        flss__bsmet, val, None)
    return NativeValue(qkhs__bwpw)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        ktrbr__hvpm = df._bodo_meta['type_metadata'][1]
    else:
        ktrbr__hvpm = [None] * len(df.columns)
    gjj__tbw = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=ktrbr__hvpm[i])) for i in range(len(df.columns))]
    gjj__tbw = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        enjqk__uom == string_array_type else enjqk__uom) for enjqk__uom in
        gjj__tbw]
    return tuple(gjj__tbw)


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
    vffwt__pnxyy, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(vffwt__pnxyy) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {vffwt__pnxyy}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        trjxk__fhel, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return trjxk__fhel, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        trjxk__fhel, typ = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        return trjxk__fhel, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        gmvma__dcrv = typ_enum_list[1]
        jlq__kjzr = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(gmvma__dcrv, jlq__kjzr)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        pgbt__frp = typ_enum_list[1]
        myn__bxoud = tuple(typ_enum_list[2:2 + pgbt__frp])
        enm__toc = typ_enum_list[2 + pgbt__frp:]
        yrn__znn = []
        for i in range(pgbt__frp):
            enm__toc, xnnnr__sktoc = _dtype_from_type_enum_list_recursor(
                enm__toc)
            yrn__znn.append(xnnnr__sktoc)
        return enm__toc, StructType(tuple(yrn__znn), myn__bxoud)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        dpgjv__ozp = typ_enum_list[1]
        enm__toc = typ_enum_list[2:]
        return enm__toc, dpgjv__ozp
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        dpgjv__ozp = typ_enum_list[1]
        enm__toc = typ_enum_list[2:]
        return enm__toc, numba.types.literal(dpgjv__ozp)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        enm__toc, okw__msvc = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        enm__toc, vxhx__czrf = _dtype_from_type_enum_list_recursor(enm__toc)
        enm__toc, vdo__eia = _dtype_from_type_enum_list_recursor(enm__toc)
        enm__toc, nsxp__wlg = _dtype_from_type_enum_list_recursor(enm__toc)
        enm__toc, ckd__yyd = _dtype_from_type_enum_list_recursor(enm__toc)
        return enm__toc, PDCategoricalDtype(okw__msvc, vxhx__czrf, vdo__eia,
            nsxp__wlg, ckd__yyd)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        enm__toc, glefd__qtcif = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return enm__toc, DatetimeIndexType(glefd__qtcif)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        enm__toc, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        enm__toc, glefd__qtcif = _dtype_from_type_enum_list_recursor(enm__toc)
        enm__toc, nsxp__wlg = _dtype_from_type_enum_list_recursor(enm__toc)
        return enm__toc, NumericIndexType(dtype, glefd__qtcif, nsxp__wlg)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        enm__toc, zbm__ebrbz = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        enm__toc, glefd__qtcif = _dtype_from_type_enum_list_recursor(enm__toc)
        return enm__toc, PeriodIndexType(zbm__ebrbz, glefd__qtcif)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        enm__toc, nsxp__wlg = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        enm__toc, glefd__qtcif = _dtype_from_type_enum_list_recursor(enm__toc)
        return enm__toc, CategoricalIndexType(nsxp__wlg, glefd__qtcif)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        enm__toc, glefd__qtcif = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return enm__toc, RangeIndexType(glefd__qtcif)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        enm__toc, glefd__qtcif = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return enm__toc, StringIndexType(glefd__qtcif)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        enm__toc, glefd__qtcif = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return enm__toc, BinaryIndexType(glefd__qtcif)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        enm__toc, glefd__qtcif = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return enm__toc, TimedeltaIndexType(glefd__qtcif)
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
        egxon__aey = get_overload_const_int(typ)
        if numba.types.maybe_literal(egxon__aey) == typ:
            return [SeriesDtypeEnum.LiteralType.value, egxon__aey]
    elif is_overload_constant_str(typ):
        egxon__aey = get_overload_const_str(typ)
        if numba.types.maybe_literal(egxon__aey) == typ:
            return [SeriesDtypeEnum.LiteralType.value, egxon__aey]
    elif is_overload_constant_bool(typ):
        egxon__aey = get_overload_const_bool(typ)
        if numba.types.maybe_literal(egxon__aey) == typ:
            return [SeriesDtypeEnum.LiteralType.value, egxon__aey]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        vyc__thg = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for zlbjw__czjdt in typ.names:
            vyc__thg.append(zlbjw__czjdt)
        for awvqe__xecc in typ.data:
            vyc__thg += _dtype_to_type_enum_list_recursor(awvqe__xecc)
        return vyc__thg
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        mrpn__aczx = _dtype_to_type_enum_list_recursor(typ.categories)
        vmkv__erzmx = _dtype_to_type_enum_list_recursor(typ.elem_type)
        mxyl__pjk = _dtype_to_type_enum_list_recursor(typ.ordered)
        ggl__csjla = _dtype_to_type_enum_list_recursor(typ.data)
        ccn__ebj = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + mrpn__aczx + vmkv__erzmx + mxyl__pjk + ggl__csjla + ccn__ebj
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                psj__bnwli = types.float64
                mbhkx__pdlri = types.Array(psj__bnwli, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                psj__bnwli = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    mbhkx__pdlri = IntegerArrayType(psj__bnwli)
                else:
                    mbhkx__pdlri = types.Array(psj__bnwli, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                psj__bnwli = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    mbhkx__pdlri = IntegerArrayType(psj__bnwli)
                else:
                    mbhkx__pdlri = types.Array(psj__bnwli, 1, 'C')
            elif typ.dtype == types.bool_:
                psj__bnwli = typ.dtype
                mbhkx__pdlri = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(psj__bnwli
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(mbhkx__pdlri)
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
                cts__olyhq = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(cts__olyhq)
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
        wzuu__zghsl = S.dtype.unit
        if wzuu__zghsl != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        gfoz__zykow = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(gfoz__zykow)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    ylznc__iqgq = cgutils.is_not_null(builder, parent_obj)
    vcczq__cqwg = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(ylznc__iqgq):
        rlpb__miytk = pyapi.object_getattr_string(parent_obj, 'columns')
        huk__svr = pyapi.call_method(rlpb__miytk, '__len__', ())
        builder.store(pyapi.long_as_longlong(huk__svr), vcczq__cqwg)
        pyapi.decref(huk__svr)
        pyapi.decref(rlpb__miytk)
    use_parent_obj = builder.and_(ylznc__iqgq, builder.icmp_unsigned('==',
        builder.load(vcczq__cqwg), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        yhagn__kynsh = df_typ.runtime_colname_typ
        context.nrt.incref(builder, yhagn__kynsh, dataframe_payload.columns)
        return pyapi.from_native_value(yhagn__kynsh, dataframe_payload.
            columns, c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        cpcw__orq = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        cpcw__orq = np.array(df_typ.columns, 'int64')
    else:
        cpcw__orq = df_typ.columns
    kib__ojwie = numba.typeof(cpcw__orq)
    joucc__xzhy = context.get_constant_generic(builder, kib__ojwie, cpcw__orq)
    ilez__pzmxp = pyapi.from_native_value(kib__ojwie, joucc__xzhy, c.
        env_manager)
    return ilez__pzmxp


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (rbehi__xwv, ori__uvsi):
        with rbehi__xwv:
            pyapi.incref(obj)
            oybk__ffxd = context.insert_const_string(c.builder.module, 'numpy')
            qoh__pgm = pyapi.import_module_noblock(oybk__ffxd)
            if df_typ.has_runtime_cols:
                ptt__mvh = 0
            else:
                ptt__mvh = len(df_typ.columns)
            qcbr__mjdc = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), ptt__mvh))
            pfl__deynk = pyapi.call_method(qoh__pgm, 'arange', (qcbr__mjdc,))
            pyapi.object_setattr_string(obj, 'columns', pfl__deynk)
            pyapi.decref(qoh__pgm)
            pyapi.decref(pfl__deynk)
            pyapi.decref(qcbr__mjdc)
        with ori__uvsi:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            jefvb__frpr = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            oybk__ffxd = context.insert_const_string(c.builder.module, 'pandas'
                )
            qoh__pgm = pyapi.import_module_noblock(oybk__ffxd)
            df_obj = pyapi.call_method(qoh__pgm, 'DataFrame', (pyapi.
                borrow_none(), jefvb__frpr))
            pyapi.decref(qoh__pgm)
            pyapi.decref(jefvb__frpr)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    zsurn__hyugc = cgutils.create_struct_proxy(typ)(context, builder, value=val
        )
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = zsurn__hyugc.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        jcd__aunzt = typ.table_type
        pxa__vtfzp = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, jcd__aunzt, pxa__vtfzp)
        lpf__arhax = box_table(jcd__aunzt, pxa__vtfzp, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (ojf__lct, bjlgz__blm):
            with ojf__lct:
                fiou__ajpsj = pyapi.object_getattr_string(lpf__arhax, 'arrays')
                bzyda__phhtw = c.pyapi.make_none()
                if n_cols is None:
                    huk__svr = pyapi.call_method(fiou__ajpsj, '__len__', ())
                    nmxp__vjn = pyapi.long_as_longlong(huk__svr)
                    pyapi.decref(huk__svr)
                else:
                    nmxp__vjn = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, nmxp__vjn) as wznr__avtmc:
                    i = wznr__avtmc.index
                    hoe__lel = pyapi.list_getitem(fiou__ajpsj, i)
                    olri__wasy = c.builder.icmp_unsigned('!=', hoe__lel,
                        bzyda__phhtw)
                    with builder.if_then(olri__wasy):
                        hsu__urkv = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, hsu__urkv, hoe__lel)
                        pyapi.decref(hsu__urkv)
                pyapi.decref(fiou__ajpsj)
                pyapi.decref(bzyda__phhtw)
            with bjlgz__blm:
                df_obj = builder.load(res)
                jefvb__frpr = pyapi.object_getattr_string(df_obj, 'index')
                pgoiv__vzm = c.pyapi.call_method(lpf__arhax, 'to_pandas', (
                    jefvb__frpr,))
                builder.store(pgoiv__vzm, res)
                pyapi.decref(df_obj)
                pyapi.decref(jefvb__frpr)
        pyapi.decref(lpf__arhax)
    else:
        juzg__hsdc = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        hdm__ijzdv = typ.data
        for i, sspvo__omy, mapwb__rjxw in zip(range(n_cols), juzg__hsdc,
            hdm__ijzdv):
            prx__uxuz = cgutils.alloca_once_value(builder, sspvo__omy)
            bzopy__ceemy = cgutils.alloca_once_value(builder, context.
                get_constant_null(mapwb__rjxw))
            olri__wasy = builder.not_(is_ll_eq(builder, prx__uxuz,
                bzopy__ceemy))
            zuag__gjcs = builder.or_(builder.not_(use_parent_obj), builder.
                and_(use_parent_obj, olri__wasy))
            with builder.if_then(zuag__gjcs):
                hsu__urkv = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, mapwb__rjxw, sspvo__omy)
                arr_obj = pyapi.from_native_value(mapwb__rjxw, sspvo__omy,
                    c.env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, hsu__urkv, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(hsu__urkv)
    df_obj = builder.load(res)
    ilez__pzmxp = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', ilez__pzmxp)
    pyapi.decref(ilez__pzmxp)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    bzyda__phhtw = pyapi.borrow_none()
    oezg__zfkj = pyapi.unserialize(pyapi.serialize_object(slice))
    slg__jku = pyapi.call_function_objargs(oezg__zfkj, [bzyda__phhtw])
    vhzc__zwl = pyapi.long_from_longlong(col_ind)
    fab__yxg = pyapi.tuple_pack([slg__jku, vhzc__zwl])
    npz__bkl = pyapi.object_getattr_string(df_obj, 'iloc')
    tqv__cbq = pyapi.object_getitem(npz__bkl, fab__yxg)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        sym__ngh = pyapi.object_getattr_string(tqv__cbq, 'array')
    else:
        sym__ngh = pyapi.object_getattr_string(tqv__cbq, 'values')
    if isinstance(data_typ, types.Array):
        esg__gmiqk = context.insert_const_string(builder.module, 'numpy')
        afylb__zgm = pyapi.import_module_noblock(esg__gmiqk)
        arr_obj = pyapi.call_method(afylb__zgm, 'ascontiguousarray', (
            sym__ngh,))
        pyapi.decref(sym__ngh)
        pyapi.decref(afylb__zgm)
    else:
        arr_obj = sym__ngh
    pyapi.decref(oezg__zfkj)
    pyapi.decref(slg__jku)
    pyapi.decref(vhzc__zwl)
    pyapi.decref(fab__yxg)
    pyapi.decref(npz__bkl)
    pyapi.decref(tqv__cbq)
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
        zsurn__hyugc = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            zsurn__hyugc.parent, args[1], data_typ)
        nadgg__dqt = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            pxa__vtfzp = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            puvcl__dud = df_typ.table_type.type_to_blk[data_typ]
            yhhl__wkmht = getattr(pxa__vtfzp, f'block_{puvcl__dud}')
            hldsg__poo = ListInstance(c.context, c.builder, types.List(
                data_typ), yhhl__wkmht)
            epfa__okt = context.get_constant(types.int64, df_typ.table_type
                .block_offsets[col_ind])
            hldsg__poo.inititem(epfa__okt, nadgg__dqt.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, nadgg__dqt.value, col_ind)
        yculz__tpgmh = DataFramePayloadType(df_typ)
        lobuv__yhz = context.nrt.meminfo_data(builder, zsurn__hyugc.meminfo)
        nrcxn__enx = context.get_value_type(yculz__tpgmh).as_pointer()
        lobuv__yhz = builder.bitcast(lobuv__yhz, nrcxn__enx)
        builder.store(dataframe_payload._getvalue(), lobuv__yhz)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        sym__ngh = c.pyapi.object_getattr_string(val, 'array')
    else:
        sym__ngh = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        esg__gmiqk = c.context.insert_const_string(c.builder.module, 'numpy')
        afylb__zgm = c.pyapi.import_module_noblock(esg__gmiqk)
        arr_obj = c.pyapi.call_method(afylb__zgm, 'ascontiguousarray', (
            sym__ngh,))
        c.pyapi.decref(sym__ngh)
        c.pyapi.decref(afylb__zgm)
    else:
        arr_obj = sym__ngh
    ktnxq__gzij = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    jefvb__frpr = c.pyapi.object_getattr_string(val, 'index')
    flss__bsmet = c.pyapi.to_native_value(typ.index, jefvb__frpr).value
    zdii__whh = c.pyapi.object_getattr_string(val, 'name')
    eyip__uck = c.pyapi.to_native_value(typ.name_typ, zdii__whh).value
    ytv__szws = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, ktnxq__gzij, flss__bsmet, eyip__uck)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(jefvb__frpr)
    c.pyapi.decref(zdii__whh)
    return NativeValue(ytv__szws)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        dwf__ueda = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(dwf__ueda._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    oybk__ffxd = c.context.insert_const_string(c.builder.module, 'pandas')
    ywh__oyu = c.pyapi.import_module_noblock(oybk__ffxd)
    vjxdg__yew = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, vjxdg__yew.data)
    c.context.nrt.incref(c.builder, typ.index, vjxdg__yew.index)
    c.context.nrt.incref(c.builder, typ.name_typ, vjxdg__yew.name)
    arr_obj = c.pyapi.from_native_value(typ.data, vjxdg__yew.data, c.
        env_manager)
    jefvb__frpr = c.pyapi.from_native_value(typ.index, vjxdg__yew.index, c.
        env_manager)
    zdii__whh = c.pyapi.from_native_value(typ.name_typ, vjxdg__yew.name, c.
        env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(ywh__oyu, 'Series', (arr_obj, jefvb__frpr,
        dtype, zdii__whh))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(jefvb__frpr)
    c.pyapi.decref(zdii__whh)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(ywh__oyu)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    oyuva__abd = []
    for jcn__kpcf in typ_list:
        if isinstance(jcn__kpcf, int) and not isinstance(jcn__kpcf, bool):
            jumtn__ejka = pyapi.long_from_longlong(lir.Constant(lir.IntType
                (64), jcn__kpcf))
        else:
            euzp__fgwa = numba.typeof(jcn__kpcf)
            nuek__jmr = context.get_constant_generic(builder, euzp__fgwa,
                jcn__kpcf)
            jumtn__ejka = pyapi.from_native_value(euzp__fgwa, nuek__jmr,
                env_manager)
        oyuva__abd.append(jumtn__ejka)
    rbj__bqq = pyapi.list_pack(oyuva__abd)
    for val in oyuva__abd:
        pyapi.decref(val)
    return rbj__bqq


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    pnsmn__btd = not typ.has_runtime_cols
    pnge__gxvk = 2 if pnsmn__btd else 1
    zxxra__tnhhb = pyapi.dict_new(pnge__gxvk)
    qhiew__lvdxh = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    pyapi.dict_setitem_string(zxxra__tnhhb, 'dist', qhiew__lvdxh)
    pyapi.decref(qhiew__lvdxh)
    if pnsmn__btd:
        upid__upomr = _dtype_to_type_enum_list(typ.index)
        if upid__upomr != None:
            sqi__pin = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, upid__upomr)
        else:
            sqi__pin = pyapi.make_none()
        if typ.is_table_format:
            enjqk__uom = typ.table_type
            bxif__hvpeg = pyapi.list_new(lir.Constant(lir.IntType(64), len(
                typ.data)))
            for puvcl__dud, dtype in enjqk__uom.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                nmxp__vjn = c.context.get_constant(types.int64, len(
                    enjqk__uom.block_to_arr_ind[puvcl__dud]))
                mar__yzj = c.context.make_constant_array(c.builder, types.
                    Array(types.int64, 1, 'C'), np.array(enjqk__uom.
                    block_to_arr_ind[puvcl__dud], dtype=np.int64))
                wysu__scc = c.context.make_array(types.Array(types.int64, 1,
                    'C'))(c.context, c.builder, mar__yzj)
                with cgutils.for_range(c.builder, nmxp__vjn) as wznr__avtmc:
                    i = wznr__avtmc.index
                    hiwst__icj = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), wysu__scc, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(bxif__hvpeg, hiwst__icj, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            qbkfm__cish = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    rbj__bqq = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    rbj__bqq = pyapi.make_none()
                qbkfm__cish.append(rbj__bqq)
            bxif__hvpeg = pyapi.list_pack(qbkfm__cish)
            for val in qbkfm__cish:
                pyapi.decref(val)
        pii__gitcs = pyapi.list_pack([sqi__pin, bxif__hvpeg])
        pyapi.dict_setitem_string(zxxra__tnhhb, 'type_metadata', pii__gitcs)
    pyapi.object_setattr_string(obj, '_bodo_meta', zxxra__tnhhb)
    pyapi.decref(zxxra__tnhhb)


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
    zxxra__tnhhb = pyapi.dict_new(2)
    qhiew__lvdxh = pyapi.long_from_longlong(lir.Constant(lir.IntType(64),
        typ.dist.value))
    upid__upomr = _dtype_to_type_enum_list(typ.index)
    if upid__upomr != None:
        sqi__pin = type_enum_list_to_py_list_obj(pyapi, context, builder, c
            .env_manager, upid__upomr)
    else:
        sqi__pin = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            punx__htmk = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            punx__htmk = pyapi.make_none()
    else:
        punx__htmk = pyapi.make_none()
    gus__rjukr = pyapi.list_pack([sqi__pin, punx__htmk])
    pyapi.dict_setitem_string(zxxra__tnhhb, 'type_metadata', gus__rjukr)
    pyapi.decref(gus__rjukr)
    pyapi.dict_setitem_string(zxxra__tnhhb, 'dist', qhiew__lvdxh)
    pyapi.object_setattr_string(obj, '_bodo_meta', zxxra__tnhhb)
    pyapi.decref(zxxra__tnhhb)
    pyapi.decref(qhiew__lvdxh)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as zpy__lpulu:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    qcdl__eyi = numba.np.numpy_support.map_layout(val)
    sjqgg__dbvu = not val.flags.writeable
    return types.Array(dtype, val.ndim, qcdl__eyi, readonly=sjqgg__dbvu)


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
    zwccc__zxxam = val[i]
    if isinstance(zwccc__zxxam, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(zwccc__zxxam, bytes):
        return binary_array_type
    elif isinstance(zwccc__zxxam, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(zwccc__zxxam, (int, np.int8, np.int16, np.int32, np.
        int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(
            zwccc__zxxam))
    elif isinstance(zwccc__zxxam, (dict, Dict)) and all(isinstance(
        yxfcp__qfjtg, str) for yxfcp__qfjtg in zwccc__zxxam.keys()):
        myn__bxoud = tuple(zwccc__zxxam.keys())
        leys__gxgog = tuple(_get_struct_value_arr_type(v) for v in
            zwccc__zxxam.values())
        return StructArrayType(leys__gxgog, myn__bxoud)
    elif isinstance(zwccc__zxxam, (dict, Dict)):
        ovrjl__yeg = numba.typeof(_value_to_array(list(zwccc__zxxam.keys())))
        ixync__kny = numba.typeof(_value_to_array(list(zwccc__zxxam.values())))
        ovrjl__yeg = to_str_arr_if_dict_array(ovrjl__yeg)
        ixync__kny = to_str_arr_if_dict_array(ixync__kny)
        return MapArrayType(ovrjl__yeg, ixync__kny)
    elif isinstance(zwccc__zxxam, tuple):
        leys__gxgog = tuple(_get_struct_value_arr_type(v) for v in zwccc__zxxam
            )
        return TupleArrayType(leys__gxgog)
    if isinstance(zwccc__zxxam, (list, np.ndarray, pd.arrays.BooleanArray,
        pd.arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(zwccc__zxxam, list):
            zwccc__zxxam = _value_to_array(zwccc__zxxam)
        fytl__emu = numba.typeof(zwccc__zxxam)
        fytl__emu = to_str_arr_if_dict_array(fytl__emu)
        return ArrayItemArrayType(fytl__emu)
    if isinstance(zwccc__zxxam, datetime.date):
        return datetime_date_array_type
    if isinstance(zwccc__zxxam, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(zwccc__zxxam, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(zwccc__zxxam, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(
        f'Unsupported object array with first value: {zwccc__zxxam}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    yds__plp = val.copy()
    yds__plp.append(None)
    sspvo__omy = np.array(yds__plp, np.object_)
    if len(val) and isinstance(val[0], float):
        sspvo__omy = np.array(val, np.float64)
    return sspvo__omy


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
    mapwb__rjxw = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        mapwb__rjxw = to_nullable_type(mapwb__rjxw)
    return mapwb__rjxw
