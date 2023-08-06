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
    enel__jeca = tuple(val.columns.to_list())
    drkj__muw = get_hiframes_dtypes(val)
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and len(val._bodo_meta['type_metadata'
        ][1]) == len(val.columns) and val._bodo_meta['type_metadata'][0] is not
        None):
        bzb__tazw = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        bzb__tazw = numba.typeof(val.index)
    irznp__enr = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    bpiej__xgihn = len(drkj__muw) >= TABLE_FORMAT_THRESHOLD
    return DataFrameType(drkj__muw, bzb__tazw, enel__jeca, irznp__enr,
        is_table_format=bpiej__xgihn)


@typeof_impl.register(pd.Series)
def typeof_pd_series(val, c):
    from bodo.transforms.distributed_analysis import Distribution
    irznp__enr = Distribution(val._bodo_meta['dist']) if hasattr(val,
        '_bodo_meta') and val._bodo_meta is not None else Distribution.REP
    if (len(val.index) == 0 and val.index.dtype == np.dtype('O') and
        hasattr(val, '_bodo_meta') and val._bodo_meta is not None and 
        'type_metadata' in val._bodo_meta and val._bodo_meta[
        'type_metadata'] is not None and val._bodo_meta['type_metadata'][0]
         is not None):
        ascr__xfh = _dtype_from_type_enum_list(val._bodo_meta[
            'type_metadata'][0])
    else:
        ascr__xfh = numba.typeof(val.index)
    dtype = _infer_series_dtype(val)
    hcriy__bow = dtype_to_array_type(dtype)
    if _use_dict_str_type and hcriy__bow == string_array_type:
        hcriy__bow = bodo.dict_str_arr_type
    return SeriesType(dtype, data=hcriy__bow, index=ascr__xfh, name_typ=
        numba.typeof(val.name), dist=irznp__enr)


@unbox(DataFrameType)
def unbox_dataframe(typ, val, c):
    check_runtime_cols_unsupported(typ, 'Unboxing')
    kcr__wlnwi = c.pyapi.object_getattr_string(val, 'index')
    zeafw__kya = c.pyapi.to_native_value(typ.index, kcr__wlnwi).value
    c.pyapi.decref(kcr__wlnwi)
    if typ.is_table_format:
        albts__krym = cgutils.create_struct_proxy(typ.table_type)(c.context,
            c.builder)
        albts__krym.parent = val
        for vjvhf__qkl, wmbum__osw in typ.table_type.type_to_blk.items():
            exzsz__hhz = c.context.get_constant(types.int64, len(typ.
                table_type.block_to_arr_ind[wmbum__osw]))
            vkt__gylqh, fzk__evm = ListInstance.allocate_ex(c.context, c.
                builder, types.List(vjvhf__qkl), exzsz__hhz)
            fzk__evm.size = exzsz__hhz
            setattr(albts__krym, f'block_{wmbum__osw}', fzk__evm.value)
        gleu__avrzb = c.pyapi.call_method(val, '__len__', ())
        jyhm__jgrd = c.pyapi.long_as_longlong(gleu__avrzb)
        c.pyapi.decref(gleu__avrzb)
        albts__krym.len = jyhm__jgrd
        kydp__fssbv = c.context.make_tuple(c.builder, types.Tuple([typ.
            table_type]), [albts__krym._getvalue()])
    else:
        gqo__qparu = [c.context.get_constant_null(vjvhf__qkl) for
            vjvhf__qkl in typ.data]
        kydp__fssbv = c.context.make_tuple(c.builder, types.Tuple(typ.data),
            gqo__qparu)
    ocg__bbufw = construct_dataframe(c.context, c.builder, typ, kydp__fssbv,
        zeafw__kya, val, None)
    return NativeValue(ocg__bbufw)


def get_hiframes_dtypes(df):
    if (hasattr(df, '_bodo_meta') and df._bodo_meta is not None and 
        'type_metadata' in df._bodo_meta and df._bodo_meta['type_metadata']
         is not None and len(df._bodo_meta['type_metadata'][1]) == len(df.
        columns)):
        crkp__hzuu = df._bodo_meta['type_metadata'][1]
    else:
        crkp__hzuu = [None] * len(df.columns)
    zrlle__nrbp = [dtype_to_array_type(_infer_series_dtype(df.iloc[:, i],
        array_metadata=crkp__hzuu[i])) for i in range(len(df.columns))]
    zrlle__nrbp = [(bodo.dict_str_arr_type if _use_dict_str_type and 
        vjvhf__qkl == string_array_type else vjvhf__qkl) for vjvhf__qkl in
        zrlle__nrbp]
    return tuple(zrlle__nrbp)


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
    qszqw__hjvy, typ = _dtype_from_type_enum_list_recursor(typ_enum_list)
    if len(qszqw__hjvy) != 0:
        raise_bodo_error(
            f"""Unexpected Internal Error while converting typing metadata: Dtype list was not fully consumed.
 Input typ_enum_list: {typ_enum_list}.
Remainder: {qszqw__hjvy}. Please file the error here: https://github.com/Bodo-inc/Feedback"""
            )
    return typ


def _dtype_from_type_enum_list_recursor(typ_enum_list):
    if len(typ_enum_list) == 0:
        raise_bodo_error('Unable to infer dtype from empty typ_enum_list')
    elif typ_enum_list[0] in _one_to_one_enum_to_type_map:
        return typ_enum_list[1:], _one_to_one_enum_to_type_map[typ_enum_list[0]
            ]
    elif typ_enum_list[0] == SeriesDtypeEnum.IntegerArray.value:
        wtrjq__zti, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return wtrjq__zti, IntegerArrayType(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.ARRAY.value:
        wtrjq__zti, typ = _dtype_from_type_enum_list_recursor(typ_enum_list[1:]
            )
        return wtrjq__zti, dtype_to_array_type(typ)
    elif typ_enum_list[0] == SeriesDtypeEnum.Decimal.value:
        vbgcf__wbqf = typ_enum_list[1]
        ntf__ldk = typ_enum_list[2]
        return typ_enum_list[3:], Decimal128Type(vbgcf__wbqf, ntf__ldk)
    elif typ_enum_list[0] == SeriesDtypeEnum.STRUCT.value:
        ixiht__mlkc = typ_enum_list[1]
        kljt__mktnx = tuple(typ_enum_list[2:2 + ixiht__mlkc])
        coljf__ibj = typ_enum_list[2 + ixiht__mlkc:]
        gea__crb = []
        for i in range(ixiht__mlkc):
            coljf__ibj, lde__emzfl = _dtype_from_type_enum_list_recursor(
                coljf__ibj)
            gea__crb.append(lde__emzfl)
        return coljf__ibj, StructType(tuple(gea__crb), kljt__mktnx)
    elif typ_enum_list[0] == SeriesDtypeEnum.Literal.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'Literal' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        suv__jnc = typ_enum_list[1]
        coljf__ibj = typ_enum_list[2:]
        return coljf__ibj, suv__jnc
    elif typ_enum_list[0] == SeriesDtypeEnum.LiteralType.value:
        if len(typ_enum_list) == 1:
            raise_bodo_error(
                f"Unexpected Internal Error while converting typing metadata: Encountered 'LiteralType' internal enum value with no value following it. Please file the error here: https://github.com/Bodo-inc/Feedback"
                )
        suv__jnc = typ_enum_list[1]
        coljf__ibj = typ_enum_list[2:]
        return coljf__ibj, numba.types.literal(suv__jnc)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalType.value:
        coljf__ibj, mhvis__svhkz = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        coljf__ibj, tar__mnk = _dtype_from_type_enum_list_recursor(coljf__ibj)
        coljf__ibj, egjbf__shyb = _dtype_from_type_enum_list_recursor(
            coljf__ibj)
        coljf__ibj, btib__rzr = _dtype_from_type_enum_list_recursor(coljf__ibj)
        coljf__ibj, deiup__sft = _dtype_from_type_enum_list_recursor(coljf__ibj
            )
        return coljf__ibj, PDCategoricalDtype(mhvis__svhkz, tar__mnk,
            egjbf__shyb, btib__rzr, deiup__sft)
    elif typ_enum_list[0] == SeriesDtypeEnum.DatetimeIndexType.value:
        coljf__ibj, fkq__kifjk = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return coljf__ibj, DatetimeIndexType(fkq__kifjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.NumericIndexType.value:
        coljf__ibj, dtype = _dtype_from_type_enum_list_recursor(typ_enum_list
            [1:])
        coljf__ibj, fkq__kifjk = _dtype_from_type_enum_list_recursor(coljf__ibj
            )
        coljf__ibj, btib__rzr = _dtype_from_type_enum_list_recursor(coljf__ibj)
        return coljf__ibj, NumericIndexType(dtype, fkq__kifjk, btib__rzr)
    elif typ_enum_list[0] == SeriesDtypeEnum.PeriodIndexType.value:
        coljf__ibj, mafb__xgoe = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        coljf__ibj, fkq__kifjk = _dtype_from_type_enum_list_recursor(coljf__ibj
            )
        return coljf__ibj, PeriodIndexType(mafb__xgoe, fkq__kifjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.CategoricalIndexType.value:
        coljf__ibj, btib__rzr = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        coljf__ibj, fkq__kifjk = _dtype_from_type_enum_list_recursor(coljf__ibj
            )
        return coljf__ibj, CategoricalIndexType(btib__rzr, fkq__kifjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.RangeIndexType.value:
        coljf__ibj, fkq__kifjk = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return coljf__ibj, RangeIndexType(fkq__kifjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.StringIndexType.value:
        coljf__ibj, fkq__kifjk = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return coljf__ibj, StringIndexType(fkq__kifjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.BinaryIndexType.value:
        coljf__ibj, fkq__kifjk = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return coljf__ibj, BinaryIndexType(fkq__kifjk)
    elif typ_enum_list[0] == SeriesDtypeEnum.TimedeltaIndexType.value:
        coljf__ibj, fkq__kifjk = _dtype_from_type_enum_list_recursor(
            typ_enum_list[1:])
        return coljf__ibj, TimedeltaIndexType(fkq__kifjk)
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
        due__mrbj = get_overload_const_int(typ)
        if numba.types.maybe_literal(due__mrbj) == typ:
            return [SeriesDtypeEnum.LiteralType.value, due__mrbj]
    elif is_overload_constant_str(typ):
        due__mrbj = get_overload_const_str(typ)
        if numba.types.maybe_literal(due__mrbj) == typ:
            return [SeriesDtypeEnum.LiteralType.value, due__mrbj]
    elif is_overload_constant_bool(typ):
        due__mrbj = get_overload_const_bool(typ)
        if numba.types.maybe_literal(due__mrbj) == typ:
            return [SeriesDtypeEnum.LiteralType.value, due__mrbj]
    elif isinstance(typ, IntegerArrayType):
        return [SeriesDtypeEnum.IntegerArray.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif bodo.utils.utils.is_array_typ(typ, False):
        return [SeriesDtypeEnum.ARRAY.value
            ] + _dtype_to_type_enum_list_recursor(typ.dtype)
    elif isinstance(typ, StructType):
        husqs__ipf = [SeriesDtypeEnum.STRUCT.value, len(typ.names)]
        for mhw__ypffr in typ.names:
            husqs__ipf.append(mhw__ypffr)
        for yknpd__pknez in typ.data:
            husqs__ipf += _dtype_to_type_enum_list_recursor(yknpd__pknez)
        return husqs__ipf
    elif isinstance(typ, bodo.libs.decimal_arr_ext.Decimal128Type):
        return [SeriesDtypeEnum.Decimal.value, typ.precision, typ.scale]
    elif isinstance(typ, PDCategoricalDtype):
        yqqj__dsdw = _dtype_to_type_enum_list_recursor(typ.categories)
        uih__ofu = _dtype_to_type_enum_list_recursor(typ.elem_type)
        wqsg__fbu = _dtype_to_type_enum_list_recursor(typ.ordered)
        qtqf__jmmz = _dtype_to_type_enum_list_recursor(typ.data)
        csm__kpioo = _dtype_to_type_enum_list_recursor(typ.int_type)
        return [SeriesDtypeEnum.CategoricalType.value
            ] + yqqj__dsdw + uih__ofu + wqsg__fbu + qtqf__jmmz + csm__kpioo
    elif isinstance(typ, DatetimeIndexType):
        return [SeriesDtypeEnum.DatetimeIndexType.value
            ] + _dtype_to_type_enum_list_recursor(typ.name_typ)
    elif isinstance(typ, NumericIndexType):
        if upcast_numeric_index:
            if isinstance(typ.dtype, types.Float):
                bihrq__ulqd = types.float64
                imv__iqgl = types.Array(bihrq__ulqd, 1, 'C')
            elif typ.dtype in {types.int8, types.int16, types.int32, types.
                int64}:
                bihrq__ulqd = types.int64
                if isinstance(typ.data, IntegerArrayType):
                    imv__iqgl = IntegerArrayType(bihrq__ulqd)
                else:
                    imv__iqgl = types.Array(bihrq__ulqd, 1, 'C')
            elif typ.dtype in {types.uint8, types.uint16, types.uint32,
                types.uint64}:
                bihrq__ulqd = types.uint64
                if isinstance(typ.data, IntegerArrayType):
                    imv__iqgl = IntegerArrayType(bihrq__ulqd)
                else:
                    imv__iqgl = types.Array(bihrq__ulqd, 1, 'C')
            elif typ.dtype == types.bool_:
                bihrq__ulqd = typ.dtype
                imv__iqgl = typ.data
            else:
                raise GuardException('Unable to convert type')
            return [SeriesDtypeEnum.NumericIndexType.value
                ] + _dtype_to_type_enum_list_recursor(bihrq__ulqd
                ) + _dtype_to_type_enum_list_recursor(typ.name_typ
                ) + _dtype_to_type_enum_list_recursor(imv__iqgl)
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
                usg__hzkng = S._bodo_meta['type_metadata'][1]
                return _dtype_from_type_enum_list(usg__hzkng)
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
        tck__vwfsu = S.dtype.unit
        if tck__vwfsu != 'ns':
            raise BodoError("Timezone-aware datetime data requires 'ns' units")
        plgrg__lvqh = bodo.libs.pd_datetime_arr_ext.get_pytz_type_info(S.
            dtype.tz)
        return PandasDatetimeTZDtype(plgrg__lvqh)
    try:
        return numpy_support.from_dtype(S.dtype)
    except:
        raise BodoError(
            f'data type {S.dtype} for column {S.name} not supported yet')


def _get_use_df_parent_obj_flag(builder, context, pyapi, parent_obj, n_cols):
    if n_cols is None:
        return context.get_constant(types.bool_, False)
    dyy__afdpp = cgutils.is_not_null(builder, parent_obj)
    lcs__uhu = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with builder.if_then(dyy__afdpp):
        xeikc__fgkxu = pyapi.object_getattr_string(parent_obj, 'columns')
        gleu__avrzb = pyapi.call_method(xeikc__fgkxu, '__len__', ())
        builder.store(pyapi.long_as_longlong(gleu__avrzb), lcs__uhu)
        pyapi.decref(gleu__avrzb)
        pyapi.decref(xeikc__fgkxu)
    use_parent_obj = builder.and_(dyy__afdpp, builder.icmp_unsigned('==',
        builder.load(lcs__uhu), context.get_constant(types.int64, n_cols)))
    return use_parent_obj


def _get_df_columns_obj(c, builder, context, pyapi, df_typ, dataframe_payload):
    if df_typ.has_runtime_cols:
        rij__vgem = df_typ.runtime_colname_typ
        context.nrt.incref(builder, rij__vgem, dataframe_payload.columns)
        return pyapi.from_native_value(rij__vgem, dataframe_payload.columns,
            c.env_manager)
    if all(isinstance(c, str) for c in df_typ.columns):
        ddo__hoec = pd.array(df_typ.columns, 'string')
    elif all(isinstance(c, int) for c in df_typ.columns):
        ddo__hoec = np.array(df_typ.columns, 'int64')
    else:
        ddo__hoec = df_typ.columns
    krmuf__pjk = numba.typeof(ddo__hoec)
    ncc__pqcl = context.get_constant_generic(builder, krmuf__pjk, ddo__hoec)
    aptb__wjs = pyapi.from_native_value(krmuf__pjk, ncc__pqcl, c.env_manager)
    return aptb__wjs


def _create_initial_df_object(builder, context, pyapi, c, df_typ, obj,
    dataframe_payload, res, use_parent_obj):
    with c.builder.if_else(use_parent_obj) as (emacp__vqqp, yqo__qyeku):
        with emacp__vqqp:
            pyapi.incref(obj)
            wdpo__xrtv = context.insert_const_string(c.builder.module, 'numpy')
            enwhb__twm = pyapi.import_module_noblock(wdpo__xrtv)
            if df_typ.has_runtime_cols:
                qpqxb__aqxk = 0
            else:
                qpqxb__aqxk = len(df_typ.columns)
            uan__hrt = pyapi.long_from_longlong(lir.Constant(lir.IntType(64
                ), qpqxb__aqxk))
            ozygy__sjnp = pyapi.call_method(enwhb__twm, 'arange', (uan__hrt,))
            pyapi.object_setattr_string(obj, 'columns', ozygy__sjnp)
            pyapi.decref(enwhb__twm)
            pyapi.decref(ozygy__sjnp)
            pyapi.decref(uan__hrt)
        with yqo__qyeku:
            context.nrt.incref(builder, df_typ.index, dataframe_payload.index)
            txr__kdnej = c.pyapi.from_native_value(df_typ.index,
                dataframe_payload.index, c.env_manager)
            wdpo__xrtv = context.insert_const_string(c.builder.module, 'pandas'
                )
            enwhb__twm = pyapi.import_module_noblock(wdpo__xrtv)
            df_obj = pyapi.call_method(enwhb__twm, 'DataFrame', (pyapi.
                borrow_none(), txr__kdnej))
            pyapi.decref(enwhb__twm)
            pyapi.decref(txr__kdnej)
            builder.store(df_obj, res)


@box(DataFrameType)
def box_dataframe(typ, val, c):
    from bodo.hiframes.table import box_table
    context = c.context
    builder = c.builder
    pyapi = c.pyapi
    dataframe_payload = bodo.hiframes.pd_dataframe_ext.get_dataframe_payload(c
        .context, c.builder, typ, val)
    stei__dfg = cgutils.create_struct_proxy(typ)(context, builder, value=val)
    n_cols = len(typ.columns) if not typ.has_runtime_cols else None
    obj = stei__dfg.parent
    res = cgutils.alloca_once_value(builder, obj)
    use_parent_obj = _get_use_df_parent_obj_flag(builder, context, pyapi,
        obj, n_cols)
    _create_initial_df_object(builder, context, pyapi, c, typ, obj,
        dataframe_payload, res, use_parent_obj)
    if typ.is_table_format:
        kukn__igcwe = typ.table_type
        albts__krym = builder.extract_value(dataframe_payload.data, 0)
        context.nrt.incref(builder, kukn__igcwe, albts__krym)
        mqo__riirx = box_table(kukn__igcwe, albts__krym, c, builder.not_(
            use_parent_obj))
        with builder.if_else(use_parent_obj) as (divw__pqisx, aoo__jomk):
            with divw__pqisx:
                hchi__upzye = pyapi.object_getattr_string(mqo__riirx, 'arrays')
                yuukr__dzb = c.pyapi.make_none()
                if n_cols is None:
                    gleu__avrzb = pyapi.call_method(hchi__upzye, '__len__', ())
                    exzsz__hhz = pyapi.long_as_longlong(gleu__avrzb)
                    pyapi.decref(gleu__avrzb)
                else:
                    exzsz__hhz = context.get_constant(types.int64, n_cols)
                with cgutils.for_range(builder, exzsz__hhz) as bhg__nkc:
                    i = bhg__nkc.index
                    qdi__gott = pyapi.list_getitem(hchi__upzye, i)
                    yive__uvlxs = c.builder.icmp_unsigned('!=', qdi__gott,
                        yuukr__dzb)
                    with builder.if_then(yive__uvlxs):
                        ijtv__dfeb = pyapi.long_from_longlong(i)
                        df_obj = builder.load(res)
                        pyapi.object_setitem(df_obj, ijtv__dfeb, qdi__gott)
                        pyapi.decref(ijtv__dfeb)
                pyapi.decref(hchi__upzye)
                pyapi.decref(yuukr__dzb)
            with aoo__jomk:
                df_obj = builder.load(res)
                txr__kdnej = pyapi.object_getattr_string(df_obj, 'index')
                yfm__soa = c.pyapi.call_method(mqo__riirx, 'to_pandas', (
                    txr__kdnej,))
                builder.store(yfm__soa, res)
                pyapi.decref(df_obj)
                pyapi.decref(txr__kdnej)
        pyapi.decref(mqo__riirx)
    else:
        ghfov__rery = [builder.extract_value(dataframe_payload.data, i) for
            i in range(n_cols)]
        zqo__sbzp = typ.data
        for i, rqjn__dtn, hcriy__bow in zip(range(n_cols), ghfov__rery,
            zqo__sbzp):
            toli__qjw = cgutils.alloca_once_value(builder, rqjn__dtn)
            nkp__liseg = cgutils.alloca_once_value(builder, context.
                get_constant_null(hcriy__bow))
            yive__uvlxs = builder.not_(is_ll_eq(builder, toli__qjw, nkp__liseg)
                )
            kdyu__gwmnk = builder.or_(builder.not_(use_parent_obj), builder
                .and_(use_parent_obj, yive__uvlxs))
            with builder.if_then(kdyu__gwmnk):
                ijtv__dfeb = pyapi.long_from_longlong(context.get_constant(
                    types.int64, i))
                context.nrt.incref(builder, hcriy__bow, rqjn__dtn)
                arr_obj = pyapi.from_native_value(hcriy__bow, rqjn__dtn, c.
                    env_manager)
                df_obj = builder.load(res)
                pyapi.object_setitem(df_obj, ijtv__dfeb, arr_obj)
                pyapi.decref(arr_obj)
                pyapi.decref(ijtv__dfeb)
    df_obj = builder.load(res)
    aptb__wjs = _get_df_columns_obj(c, builder, context, pyapi, typ,
        dataframe_payload)
    pyapi.object_setattr_string(df_obj, 'columns', aptb__wjs)
    pyapi.decref(aptb__wjs)
    _set_bodo_meta_dataframe(c, df_obj, typ)
    c.context.nrt.decref(c.builder, typ, val)
    return df_obj


def get_df_obj_column_codegen(context, builder, pyapi, df_obj, col_ind,
    data_typ):
    yuukr__dzb = pyapi.borrow_none()
    vrat__odek = pyapi.unserialize(pyapi.serialize_object(slice))
    epzrl__khhtl = pyapi.call_function_objargs(vrat__odek, [yuukr__dzb])
    nrldr__vxigy = pyapi.long_from_longlong(col_ind)
    ztbj__ukkyf = pyapi.tuple_pack([epzrl__khhtl, nrldr__vxigy])
    dugi__hrubg = pyapi.object_getattr_string(df_obj, 'iloc')
    vkz__kzoek = pyapi.object_getitem(dugi__hrubg, ztbj__ukkyf)
    if isinstance(data_typ, bodo.DatetimeArrayType):
        lgma__fadi = pyapi.object_getattr_string(vkz__kzoek, 'array')
    else:
        lgma__fadi = pyapi.object_getattr_string(vkz__kzoek, 'values')
    if isinstance(data_typ, types.Array):
        qinci__fbcn = context.insert_const_string(builder.module, 'numpy')
        qrf__tmiu = pyapi.import_module_noblock(qinci__fbcn)
        arr_obj = pyapi.call_method(qrf__tmiu, 'ascontiguousarray', (
            lgma__fadi,))
        pyapi.decref(lgma__fadi)
        pyapi.decref(qrf__tmiu)
    else:
        arr_obj = lgma__fadi
    pyapi.decref(vrat__odek)
    pyapi.decref(epzrl__khhtl)
    pyapi.decref(nrldr__vxigy)
    pyapi.decref(ztbj__ukkyf)
    pyapi.decref(dugi__hrubg)
    pyapi.decref(vkz__kzoek)
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
        stei__dfg = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        arr_obj = get_df_obj_column_codegen(context, builder, pyapi,
            stei__dfg.parent, args[1], data_typ)
        sjtx__erft = _unbox_series_data(data_typ.dtype, data_typ, arr_obj, c)
        c.pyapi.decref(arr_obj)
        dataframe_payload = (bodo.hiframes.pd_dataframe_ext.
            get_dataframe_payload(c.context, c.builder, df_typ, args[0]))
        if df_typ.is_table_format:
            albts__krym = cgutils.create_struct_proxy(df_typ.table_type)(c.
                context, c.builder, builder.extract_value(dataframe_payload
                .data, 0))
            wmbum__osw = df_typ.table_type.type_to_blk[data_typ]
            gmn__cas = getattr(albts__krym, f'block_{wmbum__osw}')
            gwih__jexg = ListInstance(c.context, c.builder, types.List(
                data_typ), gmn__cas)
            joj__gsl = context.get_constant(types.int64, df_typ.table_type.
                block_offsets[col_ind])
            gwih__jexg.inititem(joj__gsl, sjtx__erft.value, incref=False)
        else:
            dataframe_payload.data = builder.insert_value(dataframe_payload
                .data, sjtx__erft.value, col_ind)
        wci__vtfr = DataFramePayloadType(df_typ)
        rsm__ilsd = context.nrt.meminfo_data(builder, stei__dfg.meminfo)
        kxv__myta = context.get_value_type(wci__vtfr).as_pointer()
        rsm__ilsd = builder.bitcast(rsm__ilsd, kxv__myta)
        builder.store(dataframe_payload._getvalue(), rsm__ilsd)
    return signature(types.none, df, i), codegen


@numba.njit
def unbox_col_if_needed(df, i):
    if bodo.hiframes.pd_dataframe_ext.has_parent(df
        ) and bodo.hiframes.pd_dataframe_ext._column_needs_unboxing(df, i):
        bodo.hiframes.boxing.unbox_dataframe_column(df, i)


@unbox(SeriesType)
def unbox_series(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        lgma__fadi = c.pyapi.object_getattr_string(val, 'array')
    else:
        lgma__fadi = c.pyapi.object_getattr_string(val, 'values')
    if isinstance(typ.data, types.Array):
        qinci__fbcn = c.context.insert_const_string(c.builder.module, 'numpy')
        qrf__tmiu = c.pyapi.import_module_noblock(qinci__fbcn)
        arr_obj = c.pyapi.call_method(qrf__tmiu, 'ascontiguousarray', (
            lgma__fadi,))
        c.pyapi.decref(lgma__fadi)
        c.pyapi.decref(qrf__tmiu)
    else:
        arr_obj = lgma__fadi
    cwc__upsep = _unbox_series_data(typ.dtype, typ.data, arr_obj, c).value
    txr__kdnej = c.pyapi.object_getattr_string(val, 'index')
    zeafw__kya = c.pyapi.to_native_value(typ.index, txr__kdnej).value
    lsj__abvrb = c.pyapi.object_getattr_string(val, 'name')
    dml__kig = c.pyapi.to_native_value(typ.name_typ, lsj__abvrb).value
    xxjh__ggg = bodo.hiframes.pd_series_ext.construct_series(c.context, c.
        builder, typ, cwc__upsep, zeafw__kya, dml__kig)
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(txr__kdnej)
    c.pyapi.decref(lsj__abvrb)
    return NativeValue(xxjh__ggg)


def _unbox_series_data(dtype, data_typ, arr_obj, c):
    if data_typ == string_array_split_view_type:
        gka__vzgbb = c.context.make_helper(c.builder,
            string_array_split_view_type)
        return NativeValue(gka__vzgbb._getvalue())
    return c.pyapi.to_native_value(data_typ, arr_obj)


@box(HeterogeneousSeriesType)
@box(SeriesType)
def box_series(typ, val, c):
    wdpo__xrtv = c.context.insert_const_string(c.builder.module, 'pandas')
    oebe__sqpv = c.pyapi.import_module_noblock(wdpo__xrtv)
    ezgpc__tifd = bodo.hiframes.pd_series_ext.get_series_payload(c.context,
        c.builder, typ, val)
    c.context.nrt.incref(c.builder, typ.data, ezgpc__tifd.data)
    c.context.nrt.incref(c.builder, typ.index, ezgpc__tifd.index)
    c.context.nrt.incref(c.builder, typ.name_typ, ezgpc__tifd.name)
    arr_obj = c.pyapi.from_native_value(typ.data, ezgpc__tifd.data, c.
        env_manager)
    txr__kdnej = c.pyapi.from_native_value(typ.index, ezgpc__tifd.index, c.
        env_manager)
    lsj__abvrb = c.pyapi.from_native_value(typ.name_typ, ezgpc__tifd.name,
        c.env_manager)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        dtype = c.pyapi.unserialize(c.pyapi.serialize_object(object))
    else:
        dtype = c.pyapi.make_none()
    res = c.pyapi.call_method(oebe__sqpv, 'Series', (arr_obj, txr__kdnej,
        dtype, lsj__abvrb))
    c.pyapi.decref(arr_obj)
    c.pyapi.decref(txr__kdnej)
    c.pyapi.decref(lsj__abvrb)
    if isinstance(typ, HeterogeneousSeriesType) and isinstance(typ.data,
        bodo.NullableTupleType):
        c.pyapi.decref(dtype)
    _set_bodo_meta_series(res, c, typ)
    c.pyapi.decref(oebe__sqpv)
    c.context.nrt.decref(c.builder, typ, val)
    return res


def type_enum_list_to_py_list_obj(pyapi, context, builder, env_manager,
    typ_list):
    vwkmx__pzrtd = []
    for zqh__nvrt in typ_list:
        if isinstance(zqh__nvrt, int) and not isinstance(zqh__nvrt, bool):
            fgrc__qdua = pyapi.long_from_longlong(lir.Constant(lir.IntType(
                64), zqh__nvrt))
        else:
            pymfc__qri = numba.typeof(zqh__nvrt)
            tzokp__qrevd = context.get_constant_generic(builder, pymfc__qri,
                zqh__nvrt)
            fgrc__qdua = pyapi.from_native_value(pymfc__qri, tzokp__qrevd,
                env_manager)
        vwkmx__pzrtd.append(fgrc__qdua)
    jis__vzd = pyapi.list_pack(vwkmx__pzrtd)
    for val in vwkmx__pzrtd:
        pyapi.decref(val)
    return jis__vzd


def _set_bodo_meta_dataframe(c, obj, typ):
    pyapi = c.pyapi
    context = c.context
    builder = c.builder
    yzbre__jsnkj = not typ.has_runtime_cols
    ygbt__qpsej = 2 if yzbre__jsnkj else 1
    tdef__ullyb = pyapi.dict_new(ygbt__qpsej)
    litjh__upf = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    pyapi.dict_setitem_string(tdef__ullyb, 'dist', litjh__upf)
    pyapi.decref(litjh__upf)
    if yzbre__jsnkj:
        haj__fnqd = _dtype_to_type_enum_list(typ.index)
        if haj__fnqd != None:
            jtvwm__kiv = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, haj__fnqd)
        else:
            jtvwm__kiv = pyapi.make_none()
        if typ.is_table_format:
            vjvhf__qkl = typ.table_type
            gdwma__gduae = pyapi.list_new(lir.Constant(lir.IntType(64), len
                (typ.data)))
            for wmbum__osw, dtype in vjvhf__qkl.blk_to_type.items():
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    typ_list = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    typ_list = pyapi.make_none()
                exzsz__hhz = c.context.get_constant(types.int64, len(
                    vjvhf__qkl.block_to_arr_ind[wmbum__osw]))
                iudh__xmvf = c.context.make_constant_array(c.builder, types
                    .Array(types.int64, 1, 'C'), np.array(vjvhf__qkl.
                    block_to_arr_ind[wmbum__osw], dtype=np.int64))
                hllpv__mlul = c.context.make_array(types.Array(types.int64,
                    1, 'C'))(c.context, c.builder, iudh__xmvf)
                with cgutils.for_range(c.builder, exzsz__hhz) as bhg__nkc:
                    i = bhg__nkc.index
                    rcheb__rlgm = _getitem_array_single_int(c.context, c.
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), hllpv__mlul, i)
                    c.context.nrt.incref(builder, types.pyobject, typ_list)
                    pyapi.list_setitem(gdwma__gduae, rcheb__rlgm, typ_list)
                c.context.nrt.decref(builder, types.pyobject, typ_list)
        else:
            bso__eqixz = []
            for dtype in typ.data:
                typ_list = _dtype_to_type_enum_list(dtype)
                if typ_list != None:
                    jis__vzd = type_enum_list_to_py_list_obj(pyapi, context,
                        builder, c.env_manager, typ_list)
                else:
                    jis__vzd = pyapi.make_none()
                bso__eqixz.append(jis__vzd)
            gdwma__gduae = pyapi.list_pack(bso__eqixz)
            for val in bso__eqixz:
                pyapi.decref(val)
        wwl__gmr = pyapi.list_pack([jtvwm__kiv, gdwma__gduae])
        pyapi.dict_setitem_string(tdef__ullyb, 'type_metadata', wwl__gmr)
    pyapi.object_setattr_string(obj, '_bodo_meta', tdef__ullyb)
    pyapi.decref(tdef__ullyb)


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
    tdef__ullyb = pyapi.dict_new(2)
    litjh__upf = pyapi.long_from_longlong(lir.Constant(lir.IntType(64), typ
        .dist.value))
    haj__fnqd = _dtype_to_type_enum_list(typ.index)
    if haj__fnqd != None:
        jtvwm__kiv = type_enum_list_to_py_list_obj(pyapi, context, builder,
            c.env_manager, haj__fnqd)
    else:
        jtvwm__kiv = pyapi.make_none()
    dtype = get_series_dtype_handle_null_int_and_hetrogenous(typ)
    if dtype != None:
        typ_list = _dtype_to_type_enum_list(dtype)
        if typ_list != None:
            odo__vipkf = type_enum_list_to_py_list_obj(pyapi, context,
                builder, c.env_manager, typ_list)
        else:
            odo__vipkf = pyapi.make_none()
    else:
        odo__vipkf = pyapi.make_none()
    bvns__wbf = pyapi.list_pack([jtvwm__kiv, odo__vipkf])
    pyapi.dict_setitem_string(tdef__ullyb, 'type_metadata', bvns__wbf)
    pyapi.decref(bvns__wbf)
    pyapi.dict_setitem_string(tdef__ullyb, 'dist', litjh__upf)
    pyapi.object_setattr_string(obj, '_bodo_meta', tdef__ullyb)
    pyapi.decref(tdef__ullyb)
    pyapi.decref(litjh__upf)


@typeof_impl.register(np.ndarray)
def _typeof_ndarray(val, c):
    try:
        dtype = numba.np.numpy_support.from_dtype(val.dtype)
    except NotImplementedError as prrt__oul:
        dtype = types.pyobject
    if dtype == types.pyobject:
        return _infer_ndarray_obj_dtype(val)
    xxv__ozosg = numba.np.numpy_support.map_layout(val)
    glrxu__wwxob = not val.flags.writeable
    return types.Array(dtype, val.ndim, xxv__ozosg, readonly=glrxu__wwxob)


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
    cakd__nfln = val[i]
    if isinstance(cakd__nfln, str):
        return (bodo.dict_str_arr_type if _use_dict_str_type else
            string_array_type)
    elif isinstance(cakd__nfln, bytes):
        return binary_array_type
    elif isinstance(cakd__nfln, bool):
        return bodo.libs.bool_arr_ext.boolean_array
    elif isinstance(cakd__nfln, (int, np.int8, np.int16, np.int32, np.int64,
        np.uint8, np.uint16, np.uint32, np.uint64)):
        return bodo.libs.int_arr_ext.IntegerArrayType(numba.typeof(cakd__nfln))
    elif isinstance(cakd__nfln, (dict, Dict)) and all(isinstance(mkmk__vqai,
        str) for mkmk__vqai in cakd__nfln.keys()):
        kljt__mktnx = tuple(cakd__nfln.keys())
        vknr__mcz = tuple(_get_struct_value_arr_type(v) for v in cakd__nfln
            .values())
        return StructArrayType(vknr__mcz, kljt__mktnx)
    elif isinstance(cakd__nfln, (dict, Dict)):
        tdw__zmjmg = numba.typeof(_value_to_array(list(cakd__nfln.keys())))
        rha__jeea = numba.typeof(_value_to_array(list(cakd__nfln.values())))
        tdw__zmjmg = to_str_arr_if_dict_array(tdw__zmjmg)
        rha__jeea = to_str_arr_if_dict_array(rha__jeea)
        return MapArrayType(tdw__zmjmg, rha__jeea)
    elif isinstance(cakd__nfln, tuple):
        vknr__mcz = tuple(_get_struct_value_arr_type(v) for v in cakd__nfln)
        return TupleArrayType(vknr__mcz)
    if isinstance(cakd__nfln, (list, np.ndarray, pd.arrays.BooleanArray, pd
        .arrays.IntegerArray, pd.arrays.StringArray)):
        if isinstance(cakd__nfln, list):
            cakd__nfln = _value_to_array(cakd__nfln)
        qlcya__wnm = numba.typeof(cakd__nfln)
        qlcya__wnm = to_str_arr_if_dict_array(qlcya__wnm)
        return ArrayItemArrayType(qlcya__wnm)
    if isinstance(cakd__nfln, datetime.date):
        return datetime_date_array_type
    if isinstance(cakd__nfln, datetime.timedelta):
        return datetime_timedelta_array_type
    if isinstance(cakd__nfln, decimal.Decimal):
        return DecimalArrayType(38, 18)
    if isinstance(cakd__nfln, pd._libs.interval.Interval):
        return bodo.libs.interval_arr_ext.IntervalArrayType
    raise BodoError(f'Unsupported object array with first value: {cakd__nfln}')


def _value_to_array(val):
    assert isinstance(val, (list, dict, Dict))
    if isinstance(val, (dict, Dict)):
        val = dict(val)
        return np.array([val], np.object_)
    ltub__uho = val.copy()
    ltub__uho.append(None)
    rqjn__dtn = np.array(ltub__uho, np.object_)
    if len(val) and isinstance(val[0], float):
        rqjn__dtn = np.array(val, np.float64)
    return rqjn__dtn


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
    hcriy__bow = dtype_to_array_type(numba.typeof(v))
    if isinstance(v, (int, bool)):
        hcriy__bow = to_nullable_type(hcriy__bow)
    return hcriy__bow
