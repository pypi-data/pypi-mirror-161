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
    vjhgl__anhv = c.pyapi.object_getattr_string(val, 'year')
    ycbv__zgdgn = c.pyapi.object_getattr_string(val, 'month')
    qlkkd__luq = c.pyapi.object_getattr_string(val, 'day')
    dmv__nure = c.pyapi.long_as_longlong(vjhgl__anhv)
    wjulk__xue = c.pyapi.long_as_longlong(ycbv__zgdgn)
    wns__yxd = c.pyapi.long_as_longlong(qlkkd__luq)
    ksjaz__eita = c.builder.add(wns__yxd, c.builder.add(c.builder.shl(
        dmv__nure, lir.Constant(lir.IntType(64), 32)), c.builder.shl(
        wjulk__xue, lir.Constant(lir.IntType(64), 16))))
    c.pyapi.decref(vjhgl__anhv)
    c.pyapi.decref(ycbv__zgdgn)
    c.pyapi.decref(qlkkd__luq)
    iok__ohmid = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ksjaz__eita, is_error=iok__ohmid)


@lower_constant(DatetimeDateType)
def lower_constant_datetime_date(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    ksjaz__eita = builder.add(day, builder.add(builder.shl(year, lir.
        Constant(lir.IntType(64), 32)), builder.shl(month, lir.Constant(lir
        .IntType(64), 16))))
    return ksjaz__eita


@box(DatetimeDateType)
def box_datetime_date(typ, val, c):
    vjhgl__anhv = c.pyapi.long_from_longlong(c.builder.lshr(val, lir.
        Constant(lir.IntType(64), 32)))
    ycbv__zgdgn = c.pyapi.long_from_longlong(c.builder.and_(c.builder.lshr(
        val, lir.Constant(lir.IntType(64), 16)), lir.Constant(lir.IntType(
        64), 65535)))
    qlkkd__luq = c.pyapi.long_from_longlong(c.builder.and_(val, lir.
        Constant(lir.IntType(64), 65535)))
    knl__dvgj = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.date))
    qzc__odrh = c.pyapi.call_function_objargs(knl__dvgj, (vjhgl__anhv,
        ycbv__zgdgn, qlkkd__luq))
    c.pyapi.decref(vjhgl__anhv)
    c.pyapi.decref(ycbv__zgdgn)
    c.pyapi.decref(qlkkd__luq)
    c.pyapi.decref(knl__dvgj)
    return qzc__odrh


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
    ksjaz__eita = builder.add(day, builder.add(builder.shl(year, lir.
        Constant(lir.IntType(64), 32)), builder.shl(month, lir.Constant(lir
        .IntType(64), 16))))
    return ksjaz__eita


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
    ttz__chlo = _days_in_month(year, month)
    return _days_before_year(year) + _days_before_month(year, month) + day


@register_jitable
def _ord2ymd(n):
    n -= 1
    wwna__ugos, n = divmod(n, _DI400Y)
    year = wwna__ugos * 400 + 1
    uorr__zfgp, n = divmod(n, _DI100Y)
    wkntw__fevrb, n = divmod(n, _DI4Y)
    lwqyo__fzupp, n = divmod(n, 365)
    year += uorr__zfgp * 100 + wkntw__fevrb * 4 + lwqyo__fzupp
    if lwqyo__fzupp == 4 or uorr__zfgp == 4:
        return year - 1, 12, 31
    yafc__jrzje = lwqyo__fzupp == 3 and (wkntw__fevrb != 24 or uorr__zfgp == 3)
    month = n + 50 >> 5
    mqt__bxbyj = _DAYS_BEFORE_MONTH[month] + (month > 2 and yafc__jrzje)
    if mqt__bxbyj > n:
        month -= 1
        mqt__bxbyj -= _DAYS_IN_MONTH[month] + (month == 2 and yafc__jrzje)
    n -= mqt__bxbyj
    return year, month, n + 1


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


@intrinsic
def get_isocalendar(typingctx, dt_year, dt_month, dt_day):

    def codegen(context, builder, sig, args):
        year = cgutils.alloca_once(builder, lir.IntType(64))
        zgg__paqo = cgutils.alloca_once(builder, lir.IntType(64))
        qcqa__nmp = cgutils.alloca_once(builder, lir.IntType(64))
        wilj__amrhx = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
            lir.IntType(64), lir.IntType(64), lir.IntType(64).as_pointer(),
            lir.IntType(64).as_pointer(), lir.IntType(64).as_pointer()])
        xdhg__bbgb = cgutils.get_or_insert_function(builder.module,
            wilj__amrhx, name='get_isocalendar')
        builder.call(xdhg__bbgb, [args[0], args[1], args[2], year,
            zgg__paqo, qcqa__nmp])
        return cgutils.pack_array(builder, [builder.load(year), builder.
            load(zgg__paqo), builder.load(qcqa__nmp)])
    qzc__odrh = types.Tuple([types.int64, types.int64, types.int64])(types.
        int64, types.int64, types.int64), codegen
    return qzc__odrh


types.datetime_date_type = datetime_date_type


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_date_type'):
        d = datetime.date.today()
    return d


@register_jitable
def fromordinal_impl(n):
    y, pzaaa__dpvq, d = _ord2ymd(n)
    return datetime.date(y, pzaaa__dpvq, d)


@overload_method(DatetimeDateType, 'replace')
def replace_overload(date, year=None, month=None, day=None):
    if not is_overload_none(year) and not is_overload_int(year):
        raise BodoError('date.replace(): year must be an integer')
    elif not is_overload_none(month) and not is_overload_int(month):
        raise BodoError('date.replace(): month must be an integer')
    elif not is_overload_none(day) and not is_overload_int(day):
        raise BodoError('date.replace(): day must be an integer')

    def impl(date, year=None, month=None, day=None):
        vem__qvy = date.year if year is None else year
        oqbb__emxuk = date.month if month is None else month
        nrlav__ejze = date.day if day is None else day
        return datetime.date(vem__qvy, oqbb__emxuk, nrlav__ejze)
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
        year, zgg__paqo, hnh__vdt = get_isocalendar(date.year, date.month,
            date.day)
        return year, zgg__paqo, hnh__vdt
    return impl


def overload_add_operator_datetime_date(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            czj__kqu = lhs.toordinal() + rhs.days
            if 0 < czj__kqu <= _MAXORDINAL:
                return fromordinal_impl(czj__kqu)
            raise OverflowError('result out of range')
        return impl
    elif lhs == datetime_timedelta_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            czj__kqu = lhs.days + rhs.toordinal()
            if 0 < czj__kqu <= _MAXORDINAL:
                return fromordinal_impl(czj__kqu)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_date(lhs, rhs):
    if lhs == datetime_date_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + datetime.timedelta(-rhs.days)
        return impl
    elif lhs == datetime_date_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            ppxbj__lzv = lhs.toordinal()
            nyj__tdefv = rhs.toordinal()
            return datetime.timedelta(ppxbj__lzv - nyj__tdefv)
        return impl
    if lhs == datetime_date_array_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            ylqz__xwqaz = lhs
            numba.parfors.parfor.init_prange()
            n = len(ylqz__xwqaz)
            A = alloc_datetime_date_array(n)
            for bkjh__iui in numba.parfors.parfor.internal_prange(n):
                A[bkjh__iui] = ylqz__xwqaz[bkjh__iui] - rhs
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
        ibx__oont = np.uint8(td.year // 256)
        dfz__iyf = np.uint8(td.year % 256)
        month = np.uint8(td.month)
        day = np.uint8(td.day)
        iwdlo__owsw = ibx__oont, dfz__iyf, month, day
        return hash(iwdlo__owsw)
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
        nncoh__ozda = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, nncoh__ozda)


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
    qhq__lnp = types.Array(types.intp, 1, 'C')
    ovsnu__mhk = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        qhq__lnp, [n])
    npuo__vfu = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    pfmx__xlrrx = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [npuo__vfu])
    wilj__amrhx = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(8).as_pointer()])
    ahe__vayrs = cgutils.get_or_insert_function(c.builder.module,
        wilj__amrhx, name='unbox_datetime_date_array')
    c.builder.call(ahe__vayrs, [val, n, ovsnu__mhk.data, pfmx__xlrrx.data])
    ozdta__imija = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ozdta__imija.data = ovsnu__mhk._getvalue()
    ozdta__imija.null_bitmap = pfmx__xlrrx._getvalue()
    iok__ohmid = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ozdta__imija._getvalue(), is_error=iok__ohmid)


def int_to_datetime_date_python(ia):
    return datetime.date(ia >> 32, ia >> 16 & 65535, ia & 65535)


def int_array_to_datetime_date(ia):
    return np.vectorize(int_to_datetime_date_python, otypes=[object])(ia)


@box(DatetimeDateArrayType)
def box_datetime_date_array(typ, val, c):
    ylqz__xwqaz = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    ovsnu__mhk = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, ylqz__xwqaz.data)
    ucpj__atxbp = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, ylqz__xwqaz.null_bitmap).data
    n = c.builder.extract_value(ovsnu__mhk.shape, 0)
    wilj__amrhx = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(8).as_pointer()])
    yaspy__riz = cgutils.get_or_insert_function(c.builder.module,
        wilj__amrhx, name='box_datetime_date_array')
    qaj__pzyt = c.builder.call(yaspy__riz, [n, ovsnu__mhk.data, ucpj__atxbp])
    c.context.nrt.decref(c.builder, typ, val)
    return qaj__pzyt


@intrinsic
def init_datetime_date_array(typingctx, data, nulls=None):
    assert data == types.Array(types.int64, 1, 'C') or data == types.Array(
        types.NPDatetime('ns'), 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        qay__fqadf, ozheb__kvmp = args
        fsxzq__ybeo = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        fsxzq__ybeo.data = qay__fqadf
        fsxzq__ybeo.null_bitmap = ozheb__kvmp
        context.nrt.incref(builder, signature.args[0], qay__fqadf)
        context.nrt.incref(builder, signature.args[1], ozheb__kvmp)
        return fsxzq__ybeo._getvalue()
    sig = datetime_date_array_type(data, nulls)
    return sig, codegen


@lower_constant(DatetimeDateArrayType)
def lower_constant_datetime_date_arr(context, builder, typ, pyval):
    n = len(pyval)
    xgwl__gimmv = (1970 << 32) + (1 << 16) + 1
    ovsnu__mhk = np.full(n, xgwl__gimmv, np.int64)
    splij__tzo = np.empty(n + 7 >> 3, np.uint8)
    for bkjh__iui, astg__cqg in enumerate(pyval):
        bfrh__uflkn = pd.isna(astg__cqg)
        bodo.libs.int_arr_ext.set_bit_to_arr(splij__tzo, bkjh__iui, int(not
            bfrh__uflkn))
        if not bfrh__uflkn:
            ovsnu__mhk[bkjh__iui] = (astg__cqg.year << 32) + (astg__cqg.
                month << 16) + astg__cqg.day
    tbsec__hoc = context.get_constant_generic(builder, data_type, ovsnu__mhk)
    oky__hvt = context.get_constant_generic(builder, nulls_type, splij__tzo)
    return lir.Constant.literal_struct([tbsec__hoc, oky__hvt])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_date_array(n):
    ovsnu__mhk = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_date_array(ovsnu__mhk, nulls)


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
            xzu__chusz, ljzjj__gthft = array_getitem_bool_index(A, ind)
            return init_datetime_date_array(xzu__chusz, ljzjj__gthft)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            xzu__chusz, ljzjj__gthft = array_getitem_int_index(A, ind)
            return init_datetime_date_array(xzu__chusz, ljzjj__gthft)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            xzu__chusz, ljzjj__gthft = array_getitem_slice_index(A, ind)
            return init_datetime_date_array(xzu__chusz, ljzjj__gthft)
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
    zlth__faw = (
        f"setitem for DatetimeDateArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == datetime_date_type:

            def impl(A, idx, val):
                A._data[idx] = cast_datetime_date_to_int(val)
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl
        else:
            raise BodoError(zlth__faw)
    if not (is_iterable_type(val) and val.dtype == bodo.datetime_date_type or
        types.unliteral(val) == datetime_date_type):
        raise BodoError(zlth__faw)
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
                y, jww__lfyk = lhs.year, rhs.year
                pzaaa__dpvq, makwl__vrbbf = lhs.month, rhs.month
                d, vokm__ueggl = lhs.day, rhs.day
                return op(_cmp((y, pzaaa__dpvq, d), (jww__lfyk,
                    makwl__vrbbf, vokm__ueggl)), 0)
            return impl
    return overload_date_cmp


def create_datetime_date_cmp_op_overload(op):

    def overload_cmp(lhs, rhs):
        dgsin__bfp = (
            f'{lhs} {numba.core.utils.OPERATORS_TO_BUILTINS[op]} {rhs} is always {op == operator.ne} in Python. If this is unexpected there may be a bug in your code.'
            )
        warnings.warn(dgsin__bfp, bodo.utils.typing.BodoWarning)
        if op == operator.eq:
            return lambda lhs, rhs: False
        elif op == operator.ne:
            return lambda lhs, rhs: True
    return overload_cmp


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            ftace__qeyn = True
        else:
            ftace__qeyn = False
        if lhs == datetime_date_array_type and rhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                ielkr__jmn = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for bkjh__iui in numba.parfors.parfor.internal_prange(n):
                    pecrg__kkqy = bodo.libs.array_kernels.isna(lhs, bkjh__iui)
                    mojce__bje = bodo.libs.array_kernels.isna(rhs, bkjh__iui)
                    if pecrg__kkqy or mojce__bje:
                        ovvil__ucc = ftace__qeyn
                    else:
                        ovvil__ucc = op(lhs[bkjh__iui], rhs[bkjh__iui])
                    ielkr__jmn[bkjh__iui] = ovvil__ucc
                return ielkr__jmn
            return impl
        elif lhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                ielkr__jmn = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for bkjh__iui in numba.parfors.parfor.internal_prange(n):
                    rwll__bfpmu = bodo.libs.array_kernels.isna(lhs, bkjh__iui)
                    if rwll__bfpmu:
                        ovvil__ucc = ftace__qeyn
                    else:
                        ovvil__ucc = op(lhs[bkjh__iui], rhs)
                    ielkr__jmn[bkjh__iui] = ovvil__ucc
                return ielkr__jmn
            return impl
        elif rhs == datetime_date_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                ielkr__jmn = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for bkjh__iui in numba.parfors.parfor.internal_prange(n):
                    rwll__bfpmu = bodo.libs.array_kernels.isna(rhs, bkjh__iui)
                    if rwll__bfpmu:
                        ovvil__ucc = ftace__qeyn
                    else:
                        ovvil__ucc = op(lhs, rhs[bkjh__iui])
                    ielkr__jmn[bkjh__iui] = ovvil__ucc
                return ielkr__jmn
            return impl
    return overload_date_arr_cmp
