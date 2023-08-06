import datetime
import numba
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
"""
Implementation is based on
https://github.com/python/cpython/blob/39a5c889d30d03a88102e56f03ee0c95db198fb3/Lib/datetime.py
"""


class DatetimeDatetimeType(types.Type):

    def __init__(self):
        super(DatetimeDatetimeType, self).__init__(name=
            'DatetimeDatetimeType()')


datetime_datetime_type = DatetimeDatetimeType()
types.datetime_datetime_type = datetime_datetime_type


@typeof_impl.register(datetime.datetime)
def typeof_datetime_datetime(val, c):
    return datetime_datetime_type


@register_model(DatetimeDatetimeType)
class DatetimeDateTimeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yba__fqax = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, yba__fqax)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    studa__rmgd = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    bfws__cyj = c.pyapi.long_from_longlong(studa__rmgd.year)
    umzld__fdlgb = c.pyapi.long_from_longlong(studa__rmgd.month)
    hjqlm__szo = c.pyapi.long_from_longlong(studa__rmgd.day)
    tinya__eomt = c.pyapi.long_from_longlong(studa__rmgd.hour)
    swd__bmzf = c.pyapi.long_from_longlong(studa__rmgd.minute)
    rktw__dian = c.pyapi.long_from_longlong(studa__rmgd.second)
    yxzv__wsqx = c.pyapi.long_from_longlong(studa__rmgd.microsecond)
    chp__yvgbt = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    gahdf__lrgsp = c.pyapi.call_function_objargs(chp__yvgbt, (bfws__cyj,
        umzld__fdlgb, hjqlm__szo, tinya__eomt, swd__bmzf, rktw__dian,
        yxzv__wsqx))
    c.pyapi.decref(bfws__cyj)
    c.pyapi.decref(umzld__fdlgb)
    c.pyapi.decref(hjqlm__szo)
    c.pyapi.decref(tinya__eomt)
    c.pyapi.decref(swd__bmzf)
    c.pyapi.decref(rktw__dian)
    c.pyapi.decref(yxzv__wsqx)
    c.pyapi.decref(chp__yvgbt)
    return gahdf__lrgsp


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    bfws__cyj = c.pyapi.object_getattr_string(val, 'year')
    umzld__fdlgb = c.pyapi.object_getattr_string(val, 'month')
    hjqlm__szo = c.pyapi.object_getattr_string(val, 'day')
    tinya__eomt = c.pyapi.object_getattr_string(val, 'hour')
    swd__bmzf = c.pyapi.object_getattr_string(val, 'minute')
    rktw__dian = c.pyapi.object_getattr_string(val, 'second')
    yxzv__wsqx = c.pyapi.object_getattr_string(val, 'microsecond')
    studa__rmgd = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    studa__rmgd.year = c.pyapi.long_as_longlong(bfws__cyj)
    studa__rmgd.month = c.pyapi.long_as_longlong(umzld__fdlgb)
    studa__rmgd.day = c.pyapi.long_as_longlong(hjqlm__szo)
    studa__rmgd.hour = c.pyapi.long_as_longlong(tinya__eomt)
    studa__rmgd.minute = c.pyapi.long_as_longlong(swd__bmzf)
    studa__rmgd.second = c.pyapi.long_as_longlong(rktw__dian)
    studa__rmgd.microsecond = c.pyapi.long_as_longlong(yxzv__wsqx)
    c.pyapi.decref(bfws__cyj)
    c.pyapi.decref(umzld__fdlgb)
    c.pyapi.decref(hjqlm__szo)
    c.pyapi.decref(tinya__eomt)
    c.pyapi.decref(swd__bmzf)
    c.pyapi.decref(rktw__dian)
    c.pyapi.decref(yxzv__wsqx)
    zfcx__abh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(studa__rmgd._getvalue(), is_error=zfcx__abh)


@lower_constant(DatetimeDatetimeType)
def constant_datetime(context, builder, ty, pyval):
    year = context.get_constant(types.int64, pyval.year)
    month = context.get_constant(types.int64, pyval.month)
    day = context.get_constant(types.int64, pyval.day)
    hour = context.get_constant(types.int64, pyval.hour)
    minute = context.get_constant(types.int64, pyval.minute)
    second = context.get_constant(types.int64, pyval.second)
    microsecond = context.get_constant(types.int64, pyval.microsecond)
    return lir.Constant.literal_struct([year, month, day, hour, minute,
        second, microsecond])


@overload(datetime.datetime, no_unliteral=True)
def datetime_datetime(year, month, day, hour=0, minute=0, second=0,
    microsecond=0):

    def impl_datetime(year, month, day, hour=0, minute=0, second=0,
        microsecond=0):
        return init_datetime(year, month, day, hour, minute, second,
            microsecond)
    return impl_datetime


@intrinsic
def init_datetime(typingctx, year, month, day, hour, minute, second,
    microsecond):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        studa__rmgd = cgutils.create_struct_proxy(typ)(context, builder)
        studa__rmgd.year = args[0]
        studa__rmgd.month = args[1]
        studa__rmgd.day = args[2]
        studa__rmgd.hour = args[3]
        studa__rmgd.minute = args[4]
        studa__rmgd.second = args[5]
        studa__rmgd.microsecond = args[6]
        return studa__rmgd._getvalue()
    return DatetimeDatetimeType()(year, month, day, hour, minute, second,
        microsecond), codegen


make_attribute_wrapper(DatetimeDatetimeType, 'year', '_year')
make_attribute_wrapper(DatetimeDatetimeType, 'month', '_month')
make_attribute_wrapper(DatetimeDatetimeType, 'day', '_day')
make_attribute_wrapper(DatetimeDatetimeType, 'hour', '_hour')
make_attribute_wrapper(DatetimeDatetimeType, 'minute', '_minute')
make_attribute_wrapper(DatetimeDatetimeType, 'second', '_second')
make_attribute_wrapper(DatetimeDatetimeType, 'microsecond', '_microsecond')


@overload_attribute(DatetimeDatetimeType, 'year')
def datetime_get_year(dt):

    def impl(dt):
        return dt._year
    return impl


@overload_attribute(DatetimeDatetimeType, 'month')
def datetime_get_month(dt):

    def impl(dt):
        return dt._month
    return impl


@overload_attribute(DatetimeDatetimeType, 'day')
def datetime_get_day(dt):

    def impl(dt):
        return dt._day
    return impl


@overload_attribute(DatetimeDatetimeType, 'hour')
def datetime_get_hour(dt):

    def impl(dt):
        return dt._hour
    return impl


@overload_attribute(DatetimeDatetimeType, 'minute')
def datetime_get_minute(dt):

    def impl(dt):
        return dt._minute
    return impl


@overload_attribute(DatetimeDatetimeType, 'second')
def datetime_get_second(dt):

    def impl(dt):
        return dt._second
    return impl


@overload_attribute(DatetimeDatetimeType, 'microsecond')
def datetime_get_microsecond(dt):

    def impl(dt):
        return dt._microsecond
    return impl


@overload_method(DatetimeDatetimeType, 'date', no_unliteral=True)
def date(dt):

    def impl(dt):
        return datetime.date(dt.year, dt.month, dt.day)
    return impl


@register_jitable
def now_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.now()
    return d


@register_jitable
def today_impl():
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.today()
    return d


@register_jitable
def strptime_impl(date_string, dtformat):
    with numba.objmode(d='datetime_datetime_type'):
        d = datetime.datetime.strptime(date_string, dtformat)
    return d


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


def create_cmp_op_overload(op):

    def overload_datetime_cmp(lhs, rhs):
        if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

            def impl(lhs, rhs):
                y, ewbnb__pbax = lhs.year, rhs.year
                sfgj__iqmm, qtge__bwcjr = lhs.month, rhs.month
                d, nsa__obzxs = lhs.day, rhs.day
                yyhsx__xbxkx, fxsi__rehq = lhs.hour, rhs.hour
                ikoug__imoii, qcaj__iqnhi = lhs.minute, rhs.minute
                rtp__nmigf, xghsr__bupo = lhs.second, rhs.second
                mec__avb, zrmi__abdzo = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, sfgj__iqmm, d, yyhsx__xbxkx,
                    ikoug__imoii, rtp__nmigf, mec__avb), (ewbnb__pbax,
                    qtge__bwcjr, nsa__obzxs, fxsi__rehq, qcaj__iqnhi,
                    xghsr__bupo, zrmi__abdzo)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            qdu__rzll = lhs.toordinal()
            ttlt__uvhm = rhs.toordinal()
            jucvt__cibj = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            pefio__jzgqw = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            iofcp__kayeh = datetime.timedelta(qdu__rzll - ttlt__uvhm, 
                jucvt__cibj - pefio__jzgqw, lhs.microsecond - rhs.microsecond)
            return iofcp__kayeh
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    oxdai__ijun = context.make_helper(builder, fromty, value=val)
    lyi__zrff = cgutils.as_bool_bit(builder, oxdai__ijun.valid)
    with builder.if_else(lyi__zrff) as (afeb__htdve, hxlo__kvh):
        with afeb__htdve:
            esqf__mzb = context.cast(builder, oxdai__ijun.data, fromty.type,
                toty)
            glvjv__csh = builder.block
        with hxlo__kvh:
            mmnhg__xgp = numba.np.npdatetime.NAT
            edxfh__rgw = builder.block
    gahdf__lrgsp = builder.phi(esqf__mzb.type)
    gahdf__lrgsp.add_incoming(esqf__mzb, glvjv__csh)
    gahdf__lrgsp.add_incoming(mmnhg__xgp, edxfh__rgw)
    return gahdf__lrgsp
