"""Numba extension support for datetime.date objects and their arrays.
"""
import datetime
import operator
import warnings
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_builtin, lower_constant
from numba.core.typing.templates import AttributeTemplate, infer_getattr
from numba.core.utils import PYVERSION
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_getattr, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_datetime_ext import DatetimeDatetimeType
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type
from bodo.libs import hdatetime_ext
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type, is_overload_int, is_overload_none
ll.add_symbol('box_datetime_date_array', hdatetime_ext.box_datetime_date_array)
ll.add_symbol('unbox_datetime_date_array', hdatetime_ext.
    unbox_datetime_date_array)
ll.add_symbol('get_isocalendar', hdatetime_ext.get_isocalendar)


class DatetimeDateType(types.Type):

    def __init__(self):
        super(DatetimeDateType, self).__init__(name='DatetimeDateType()')
        self.bitwidth = 64


datetime_date_type = DatetimeDateType()


@typeof_impl.register(datetime.date)
def typeof_datetime_date(val, c):
    return datetime_date_type


register_model(DatetimeDateType)(models.IntegerModel)


@infer_getattr
class DatetimeAttribute(AttributeTemplate):
    key = DatetimeDateType

    def resolve_year(self, typ):
        return types.int64

    def resolve_month(self, typ):
        return types.int64

    def resolve_day(self, typ):
        return types.int64


@lower_getattr(DatetimeDateType, 'year')
def datetime_get_year(context, builder, typ, val):
    return builder.lshr(val, lir.Constant(lir.IntType(64), 32))


@lower_getattr(DatetimeDateType, 'month')
def datetime_get_month(context, builder, typ, val):
    return builder.and_(builder.lshr(val, lir.Constant(lir.IntType(64), 16)
        ), lir.Constant(lir.IntType(64), 65535))


@lower_getattr(DatetimeDateType, 'day')
def datetime_get_day(context, builder, typ, val):
    return builder.and_(val, lir.Constant(lir.IntType(64), 65535))


@unbox(DatetimeDateType)
def unbox_datetime_date(typ, val, c):
    ioxv__dgsml = c.pyapi.object_getattr_string(val, 'year')
    flg__devfn = c.pyapi.object_getattr_string(val, 'month')
    jco__jsn = c.pyapi.object_getattr_string(val, 'day')
    uvmz__igtu = c.pyapi.long_as_longlong(ioxv__dgsml)
    zine__jcpw = c.pyapi.long_as_longlong(flg__devfn)
    ykhuy__hwkr = c.pyapi.long_as_longlong(jco__jsn)
    qqa__pnq = c.builder.add(ykhuy__hwkr, c.builder.add(c.builder.shl(
        uvmz__igtu, lir.Constant(lir.IntType(64), 32)), c.builder.shl(
        zine__jcpw, lir.Constant(lir.IntType(64), 16))))
    c.pyapi.decref(ioxv__dgsml)
    c.pyapi.decref(flg__devfn)
    c.pyapi.decref(jco__jsn)
    lmeoc__pswg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qqa__pnq, is_error=lmeoc__pswg)


@lower_constant(DatetimeDateType)
def lower_constant_datetime_date(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    qqa__pnq = builder.add(day, builder.add(builder.shl(year, lir.Constant(
        lir.IntType(64), 32)), builder.shl(month, lir.Constant(lir.IntType(
        64), 16))))
    return qqa__pnq


@box(DatetimeDateType)
def box_datetime_date(typ, val, c):
    ioxv__dgsml = c.pyapi.long_from_longlong(c.builder.lshr(val, lir.
        Constant(lir.IntType(64), 32)))
    flg__devfn = c.pyapi.long_from_longlong(c.builder.and_(c.builder.lshr(
        val, lir.Constant(lir.IntType(64), 16)), lir.Constant(lir.IntType(
        64), 65535)))
    jco__jsn = c.pyapi.long_from_longlong(c.builder.and_(val, lir.Constant(
        lir.IntType(64), 65535)))
    vihsm__ucfq = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.date))
    ndfky__zqhkv = c.pyapi.call_function_objargs(vihsm__ucfq, (ioxv__dgsml,
        flg__devfn, jco__jsn))
    c.pyapi.decref(ioxv__dgsml)
    c.pyapi.decref(flg__devfn)
    c.pyapi.decref(jco__jsn)
    c.pyapi.decref(vihsm__ucfq)
    return ndfky__zqhkv


@type_callable(datetime.date)
def type_datetime_date(context):

    def typer(year, month, day):
        return datetime_date_type
    return typer


@lower_builtin(datetime.date, types.IntegerLiteral, types.IntegerLiteral,
    types.IntegerLiteral)
@lower_builtin(datetime.date, types.int64, types.int64, types.int64)
def impl_ctor_datetime_date(context, builder, sig, args):
    year, month, day = args
    qqa__pnq = builder.add(day, builder.add(builder.shl(year, lir.Constant(
        lir.IntType(64), 32)), builder.shl(month, lir.Constant(lir.IntType(
        64), 16))))
    return qqa__pnq


@intrinsic
def cast_int_to_datetime_date(typingctx, val=None):
    assert val == types.int64

    def codegen(context, builder, signature, args):
        return args[0]
    return datetime_date_type(types.int64), codegen


@intrinsic
def cast_datetime_date_to_int(typingctx, val=None):
    assert val == datetime_date_type

    def codegen(context, builder, signature, args):
        return args[0]
    return types.int64(datetime_date_type), codegen


"""
Following codes are copied from
https://github.com/python/cpython/blob/39a5c889d30d03a88102e56f03ee0c95db198fb3/Lib/datetime.py
"""
_MAXORDINAL = 3652059
_DAYS_IN_MONTH = np.array([-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 
    31], dtype=np.int64)
_DAYS_BEFORE_MONTH = np.array([-1, 0, 31, 59, 90, 120, 151, 181, 212, 243, 
    273, 304, 334], dtype=np.int64)


@register_jitable
def _is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


@register_jitable
def _days_before_year(year):
    y = year - 1
    return y * 365 + y // 4 - y // 100 + y // 400


@register_jitable
def _days_in_month(year, month):
    if month == 2 and _is_leap(year):
        return 29
    return _DAYS_IN_MONTH[month]


@register_jitable
def _days_before_month(year, month):
    return _DAYS_BEFORE_MONTH[month] + (month > 2 and _is_leap(year))


_DI400Y = _days_before_year(401)
_DI100Y = _days_before_year(101)
_DI4Y = _days_before_year(5)


@register_jitable
def _ymd2ord(year, month, day):
    lzumk__aoq = _days_in_month(year, month)
    return _days_before_year(year) + _days_before_month(year, month) + day


@register_jitable
def _ord2ymd(n):
    n -= 1
    alth__vli, n = divmod(n, _DI400Y)
    year = alth__vli * 400 + 1
    ikwx__kyqiu, n = divmod(n, _DI100Y)
    bjy__amm, n = divmod(n, _DI4Y)
    kgtpo__bybuq, n = divmod(n, 365)
    year += ikwx__kyqiu * 100 + bjy__amm * 4 + kgtpo__bybuq
    if kgtpo__bybuq == 4 or ikwx__kyqiu == 4:
        return year - 1, 12, 31
    wefu__aslou = kgtpo__bybuq == 3 and (bjy__amm != 24 or ikwx__kyqiu == 3)
    month = n + 50 >> 5
    jjih__jim = _DAYS_BEFORE_MONTH[month] + (month > 2 and wefu__aslou)
    if jjih__jim > n:
        month -= 1
        jjih__jim -= _DAYS_IN_MONTH[month] + (month == 2 and wefu__aslou)
    n -= jjih__jim
    return year, month, n + 1


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


@intrinsic
def get_isocalendar(typingctx, dt_year, dt_month, dt_day):

    def codegen(context, builder, sig, args):
        year = cgutils.alloca_once(builder, lir.IntType(64))
        ddjrg__rzw = cgutils.alloca_once(builder, lir.IntType(64))
        kua__kut = cgutils.alloca_once(builder, lir.IntType(64))
        edw__nwuhe = lir.FunctionType(lir.VoidType(), [lir.IntType(64), lir
            .IntType(64), lir.IntType(64), lir.IntType(64).as_pointer(),
            lir.IntType(64).as_pointer(), lir.IntType(64).as_pointer()])
        zim__njvf = cgutils.get_or_insert_function(builder.module,
            edw__nwuhe, name='get_isocalendar')
        builder.call(zim__njvf, [args[0], args[1], args[2], year,
            ddjrg__rzw, kua__kut])
        return cgutils.pack_array(builder, [builder.load(year), builder.
            load(ddjrg__rzw), builder.load(kua__kut)])
    ndfky__zqhkv = types.Tuple([types.int64, types.int64, types.int64])(types
        .int64, types.int64, types.int64), codegen
    return ndfky__zqhkv


types.datetime_date_type = datetime_date_type


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_date_type'):
        d = datetime.date.today()
    return d


@register_jitable
def fromordinal_impl(n):
    y, dju__pgfpy, d = _ord2ymd(n)
    return datetime.date(y, dju__pgfpy, d)


@overload_method(DatetimeDateType, 'replace')
def replace_overload(date, year=None, month=None, day=None):
    if not is_overload_none(year) and not is_overload_int(year):
        raise BodoError('date.replace(): year must be an integer')
    elif not is_overload_none(month) and not is_overload_int(month):
        raise BodoError('date.replace(): month must be an integer')
    elif not is_overload_none(day) and not is_overload_int(day):
        raise BodoError('date.replace(): day must be an integer')

    def impl(date, year=None, month=None, day=None):
        hcs__cko = date.year if year is None else year
        pfc__kowz = date.month if month is None else month
        rbnl__rle = date.day if day is None else day
        return datetime.date(hcs__cko, pfc__kowz, rbnl__rle)
    return impl


@overload_method(DatetimeDatetimeType, 'toordinal', no_unliteral=True)
@overload_method(DatetimeDateType, 'toordinal', no_unliteral=True)
def toordinal(date):

    def impl(date):
        return _ymd2ord(date.year, date.month, date.day)
    return impl


@overload_method(DatetimeDatetimeType, 'weekday', no_unliteral=True)
@overload_method(DatetimeDateType, 'weekday', no_unliteral=True)
def weekday(date):

    def impl(date):
        return (date.toordinal() + 6) % 7
    return impl


@overload_method(DatetimeDateType, 'isocalendar', no_unliteral=True)
def overload_pd_timestamp_isocalendar(date):

    def impl(date):
        year, ddjrg__rzw, dnvs__poq = get_isocalendar(date.year, date.month,
            date.day)
        return year, ddjrg__rzw, dnvs__poq
    return impl


def overload_add_operator_datetime_date(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            wnbx__pbfp = lhs.toordinal() + rhs.days
            if 0 < wnbx__pbfp <= _MAXORDINAL:
                return fromordinal_impl(wnbx__pbfp)
            raise OverflowError('result out of range')
        return impl
    elif lhs == datetime_timedelta_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            wnbx__pbfp = lhs.days + rhs.toordinal()
            if 0 < wnbx__pbfp <= _MAXORDINAL:
                return fromordinal_impl(wnbx__pbfp)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_date(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + datetime.timedelta(-rhs.days)
        return impl
    elif lhs == datetime_date_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            nawvc__tcs = lhs.toordinal()
            yxqbp__scjiy = rhs.toordinal()
            return datetime.timedelta(nawvc__tcs - yxqbp__scjiy)
        return impl
    if lhs == datetime_date_array_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            jkdtz__sfb = lhs
            numba.parfors.parfor.init_prange()
            n = len(jkdtz__sfb)
            A = alloc_datetime_date_array(n)
            for roxlu__rrb in numba.parfors.parfor.internal_prange(n):
                A[roxlu__rrb] = jkdtz__sfb[roxlu__rrb] - rhs
            return A
        return impl


@overload(min, no_unliteral=True)
def date_min(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@overload(max, no_unliteral=True)
def date_max(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload_method(DatetimeDateType, '__hash__', no_unliteral=True)
def __hash__(td):

    def impl(td):
        ugwcs__hrk = np.uint8(td.year // 256)
        ftxmq__xovdz = np.uint8(td.year % 256)
        month = np.uint8(td.month)
        day = np.uint8(td.day)
        lmea__kdkc = ugwcs__hrk, ftxmq__xovdz, month, day
        return hash(lmea__kdkc)
    return impl


@overload(bool, inline='always', no_unliteral=True)
def date_to_bool(date):
    if date != datetime_date_type:
        return

    def impl(date):
        return True
    return impl


if PYVERSION >= (3, 9):
    IsoCalendarDate = datetime.date(2011, 1, 1).isocalendar().__class__


    class IsoCalendarDateType(types.Type):

        def __init__(self):
            super(IsoCalendarDateType, self).__init__(name=
                'IsoCalendarDateType()')
    iso_calendar_date_type = DatetimeDateType()

    @typeof_impl.register(IsoCalendarDate)
    def typeof_datetime_date(val, c):
        return iso_calendar_date_type


class DatetimeDateArrayType(types.ArrayCompatible):

    def __init__(self):
        super(DatetimeDateArrayType, self).__init__(name=
            'DatetimeDateArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return datetime_date_type

    def copy(self):
        return DatetimeDateArrayType()


datetime_date_array_type = DatetimeDateArrayType()
types.datetime_date_array_type = datetime_date_array_type
data_type = types.Array(types.int64, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DatetimeDateArrayType)
class DatetimeDateArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ynjug__wccro = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, ynjug__wccro)


make_attribute_wrapper(DatetimeDateArrayType, 'data', '_data')
make_attribute_wrapper(DatetimeDateArrayType, 'null_bitmap', '_null_bitmap')


@overload_method(DatetimeDateArrayType, 'copy', no_unliteral=True)
def overload_datetime_date_arr_copy(A):
    return lambda A: bodo.hiframes.datetime_date_ext.init_datetime_date_array(A
        ._data.copy(), A._null_bitmap.copy())


@overload_attribute(DatetimeDateArrayType, 'dtype')
def overload_datetime_date_arr_dtype(A):
    return lambda A: np.object_


@unbox(DatetimeDateArrayType)
def unbox_datetime_date_array(typ, val, c):
    n = bodo.utils.utils.object_length(c, val)
    trsqy__ehzo = types.Array(types.intp, 1, 'C')
    clkfg__amjy = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        trsqy__ehzo, [n])
    tvx__pyb = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64),
        7)), lir.Constant(lir.IntType(64), 8))
    zzt__mhnl = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [tvx__pyb])
    edw__nwuhe = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(8).as_pointer()])
    xnf__mhj = cgutils.get_or_insert_function(c.builder.module, edw__nwuhe,
        name='unbox_datetime_date_array')
    c.builder.call(xnf__mhj, [val, n, clkfg__amjy.data, zzt__mhnl.data])
    mybe__zcp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mybe__zcp.data = clkfg__amjy._getvalue()
    mybe__zcp.null_bitmap = zzt__mhnl._getvalue()
    lmeoc__pswg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mybe__zcp._getvalue(), is_error=lmeoc__pswg)


def int_to_datetime_date_python(ia):
    return datetime.date(ia >> 32, ia >> 16 & 65535, ia & 65535)


def int_array_to_datetime_date(ia):
    return np.vectorize(int_to_datetime_date_python, otypes=[object])(ia)


@box(DatetimeDateArrayType)
def box_datetime_date_array(typ, val, c):
    jkdtz__sfb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    clkfg__amjy = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, jkdtz__sfb.data)
    dttno__nepbu = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, jkdtz__sfb.null_bitmap).data
    n = c.builder.extract_value(clkfg__amjy.shape, 0)
    edw__nwuhe = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(8).as_pointer()])
    hfrfy__fqyhx = cgutils.get_or_insert_function(c.builder.module,
        edw__nwuhe, name='box_datetime_date_array')
    dgee__jbgp = c.builder.call(hfrfy__fqyhx, [n, clkfg__amjy.data,
        dttno__nepbu])
    c.context.nrt.decref(c.builder, typ, val)
    return dgee__jbgp


@intrinsic
def init_datetime_date_array(typingctx, data, nulls=None):
    assert data == types.Array(types.int64, 1, 'C') or data == types.Array(
        types.NPDatetime('ns'), 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        toqg__ettbw, tgzxt__ith = args
        yqmb__qmm = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        yqmb__qmm.data = toqg__ettbw
        yqmb__qmm.null_bitmap = tgzxt__ith
        context.nrt.incref(builder, signature.args[0], toqg__ettbw)
        context.nrt.incref(builder, signature.args[1], tgzxt__ith)
        return yqmb__qmm._getvalue()
    sig = datetime_date_array_type(data, nulls)
    return sig, codegen


@lower_constant(DatetimeDateArrayType)
def lower_constant_datetime_date_arr(context, builder, typ, pyval):
    n = len(pyval)
    iybj__rrkex = (1970 << 32) + (1 << 16) + 1
    clkfg__amjy = np.full(n, iybj__rrkex, np.int64)
    kpcos__wlb = np.empty(n + 7 >> 3, np.uint8)
    for roxlu__rrb, dlr__mbm in enumerate(pyval):
        mlgqy__yglqb = pd.isna(dlr__mbm)
        bodo.libs.int_arr_ext.set_bit_to_arr(kpcos__wlb, roxlu__rrb, int(
            not mlgqy__yglqb))
        if not mlgqy__yglqb:
            clkfg__amjy[roxlu__rrb] = (dlr__mbm.year << 32) + (dlr__mbm.
                month << 16) + dlr__mbm.day
    cvs__rpi = context.get_constant_generic(builder, data_type, clkfg__amjy)
    husl__faa = context.get_constant_generic(builder, nulls_type, kpcos__wlb)
    return lir.Constant.literal_struct([cvs__rpi, husl__faa])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_date_array(n):
    clkfg__amjy = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_date_array(clkfg__amjy, nulls)


def alloc_datetime_date_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_datetime_date_ext_alloc_datetime_date_array
    ) = alloc_datetime_date_array_equiv


@overload(operator.getitem, no_unliteral=True)
def dt_date_arr_getitem(A, ind):
    if A != datetime_date_array_type:
        return
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: cast_int_to_datetime_date(A._data[ind])
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            bcbe__mau, gnzh__txjm = array_getitem_bool_index(A, ind)
            return init_datetime_date_array(bcbe__mau, gnzh__txjm)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            bcbe__mau, gnzh__txjm = array_getitem_int_index(A, ind)
            return init_datetime_date_array(bcbe__mau, gnzh__txjm)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            bcbe__mau, gnzh__txjm = array_getitem_slice_index(A, ind)
            return init_datetime_date_array(bcbe__mau, gnzh__txjm)
        return impl_slice
    raise BodoError(
        f'getitem for DatetimeDateArray with indexing type {ind} not supported.'
        )


@overload(operator.setitem, no_unliteral=True)
def dt_date_arr_setitem(A, idx, val):
    if A != datetime_date_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    olttn__takb = (
        f"setitem for DatetimeDateArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == datetime_date_type:

            def impl(A, idx, val):
                A._data[idx] = cast_datetime_date_to_int(val)
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl
        else:
            raise BodoError(olttn__takb)
    if not (is_iterable_type(val) and val.dtype == bodo.datetime_date_type or
        types.unliteral(val) == datetime_date_type):
        raise BodoError(olttn__takb)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):
        if types.unliteral(val) == datetime_date_type:
            return lambda A, idx, val: array_setitem_int_index(A, idx,
                cast_datetime_date_to_int(val))

        def impl_arr_ind(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if types.unliteral(val) == datetime_date_type:
            return lambda A, idx, val: array_setitem_bool_index(A, idx,
                cast_datetime_date_to_int(val))

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):
        if types.unliteral(val) == datetime_date_type:
            return lambda A, idx, val: array_setitem_slice_index(A, idx,
                cast_datetime_date_to_int(val))

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for DatetimeDateArray with indexing type {idx} not supported.'
        )


@overload(len, no_unliteral=True)
def overload_len_datetime_date_arr(A):
    if A == datetime_date_array_type:
        return lambda A: len(A._data)


@overload_attribute(DatetimeDateArrayType, 'shape')
def overload_datetime_date_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(DatetimeDateArrayType, 'nbytes')
def datetime_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


def create_cmp_op_overload(op):

    def overload_date_cmp(lhs, rhs):
        if lhs == datetime_date_type and rhs == datetime_date_type:

            def impl(lhs, rhs):
                y, eiycf__suqom = lhs.year, rhs.year
                dju__pgfpy, itqzk__occom = lhs.month, rhs.month
                d, xoh__rezsy = lhs.day, rhs.day
                return op(_cmp((y, dju__pgfpy, d), (eiycf__suqom,
                    itqzk__occom, xoh__rezsy)), 0)
            return impl
    return overload_date_cmp


def create_datetime_date_cmp_op_overload(op):

    def overload_cmp(lhs, rhs):
        cmsx__ihjj = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[op]} {rhs} is always {op == operator.ne} in Python. If this is unexpected there may be a bug in your code.'
            )
        warnings.warn(cmsx__ihjj, bodo.utils.typing.BodoWarning)
        if op == operator.eq:
            return lambda lhs, rhs: False
        elif op == operator.ne:
            return lambda lhs, rhs: True
    return overload_cmp


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            ogx__ila = True
        else:
            ogx__ila = False
        if lhs == datetime_date_array_type and rhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                bbrgs__qmpqo = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for roxlu__rrb in numba.parfors.parfor.internal_prange(n):
                    seqp__jsyve = bodo.libs.array_kernels.isna(lhs, roxlu__rrb)
                    gluh__oswxo = bodo.libs.array_kernels.isna(rhs, roxlu__rrb)
                    if seqp__jsyve or gluh__oswxo:
                        keyk__jygdz = ogx__ila
                    else:
                        keyk__jygdz = op(lhs[roxlu__rrb], rhs[roxlu__rrb])
                    bbrgs__qmpqo[roxlu__rrb] = keyk__jygdz
                return bbrgs__qmpqo
            return impl
        elif lhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                bbrgs__qmpqo = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for roxlu__rrb in numba.parfors.parfor.internal_prange(n):
                    cwdb__uukl = bodo.libs.array_kernels.isna(lhs, roxlu__rrb)
                    if cwdb__uukl:
                        keyk__jygdz = ogx__ila
                    else:
                        keyk__jygdz = op(lhs[roxlu__rrb], rhs)
                    bbrgs__qmpqo[roxlu__rrb] = keyk__jygdz
                return bbrgs__qmpqo
            return impl
        elif rhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                bbrgs__qmpqo = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for roxlu__rrb in numba.parfors.parfor.internal_prange(n):
                    cwdb__uukl = bodo.libs.array_kernels.isna(rhs, roxlu__rrb)
                    if cwdb__uukl:
                        keyk__jygdz = ogx__ila
                    else:
                        keyk__jygdz = op(lhs, rhs[roxlu__rrb])
                    bbrgs__qmpqo[roxlu__rrb] = keyk__jygdz
                return bbrgs__qmpqo
            return impl
    return overload_date_arr_cmp
