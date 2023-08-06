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
        czjvg__uen = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, czjvg__uen)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    vsm__mld = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    vdu__uqlgb = c.pyapi.long_from_longlong(vsm__mld.year)
    vwnd__lenh = c.pyapi.long_from_longlong(vsm__mld.month)
    ivrez__gubyh = c.pyapi.long_from_longlong(vsm__mld.day)
    hoyiv__zvogn = c.pyapi.long_from_longlong(vsm__mld.hour)
    zchs__onda = c.pyapi.long_from_longlong(vsm__mld.minute)
    wsojg__sxuk = c.pyapi.long_from_longlong(vsm__mld.second)
    bpsb__uzhdw = c.pyapi.long_from_longlong(vsm__mld.microsecond)
    qdtr__gppxk = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    axr__dhtwn = c.pyapi.call_function_objargs(qdtr__gppxk, (vdu__uqlgb,
        vwnd__lenh, ivrez__gubyh, hoyiv__zvogn, zchs__onda, wsojg__sxuk,
        bpsb__uzhdw))
    c.pyapi.decref(vdu__uqlgb)
    c.pyapi.decref(vwnd__lenh)
    c.pyapi.decref(ivrez__gubyh)
    c.pyapi.decref(hoyiv__zvogn)
    c.pyapi.decref(zchs__onda)
    c.pyapi.decref(wsojg__sxuk)
    c.pyapi.decref(bpsb__uzhdw)
    c.pyapi.decref(qdtr__gppxk)
    return axr__dhtwn


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    vdu__uqlgb = c.pyapi.object_getattr_string(val, 'year')
    vwnd__lenh = c.pyapi.object_getattr_string(val, 'month')
    ivrez__gubyh = c.pyapi.object_getattr_string(val, 'day')
    hoyiv__zvogn = c.pyapi.object_getattr_string(val, 'hour')
    zchs__onda = c.pyapi.object_getattr_string(val, 'minute')
    wsojg__sxuk = c.pyapi.object_getattr_string(val, 'second')
    bpsb__uzhdw = c.pyapi.object_getattr_string(val, 'microsecond')
    vsm__mld = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vsm__mld.year = c.pyapi.long_as_longlong(vdu__uqlgb)
    vsm__mld.month = c.pyapi.long_as_longlong(vwnd__lenh)
    vsm__mld.day = c.pyapi.long_as_longlong(ivrez__gubyh)
    vsm__mld.hour = c.pyapi.long_as_longlong(hoyiv__zvogn)
    vsm__mld.minute = c.pyapi.long_as_longlong(zchs__onda)
    vsm__mld.second = c.pyapi.long_as_longlong(wsojg__sxuk)
    vsm__mld.microsecond = c.pyapi.long_as_longlong(bpsb__uzhdw)
    c.pyapi.decref(vdu__uqlgb)
    c.pyapi.decref(vwnd__lenh)
    c.pyapi.decref(ivrez__gubyh)
    c.pyapi.decref(hoyiv__zvogn)
    c.pyapi.decref(zchs__onda)
    c.pyapi.decref(wsojg__sxuk)
    c.pyapi.decref(bpsb__uzhdw)
    gcohb__syf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vsm__mld._getvalue(), is_error=gcohb__syf)


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
        vsm__mld = cgutils.create_struct_proxy(typ)(context, builder)
        vsm__mld.year = args[0]
        vsm__mld.month = args[1]
        vsm__mld.day = args[2]
        vsm__mld.hour = args[3]
        vsm__mld.minute = args[4]
        vsm__mld.second = args[5]
        vsm__mld.microsecond = args[6]
        return vsm__mld._getvalue()
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
                y, jjha__rssh = lhs.year, rhs.year
                fabj__itdld, rspf__qizsp = lhs.month, rhs.month
                d, eil__vhu = lhs.day, rhs.day
                stzfa__sjswv, hixg__qkhn = lhs.hour, rhs.hour
                vve__kmbd, baqpv__bjoi = lhs.minute, rhs.minute
                mxuz__mjewr, ewz__puk = lhs.second, rhs.second
                uay__josr, gyqd__agkeo = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, fabj__itdld, d, stzfa__sjswv, vve__kmbd,
                    mxuz__mjewr, uay__josr), (jjha__rssh, rspf__qizsp,
                    eil__vhu, hixg__qkhn, baqpv__bjoi, ewz__puk,
                    gyqd__agkeo)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            zqnr__fpo = lhs.toordinal()
            ptws__iszzp = rhs.toordinal()
            eeq__broid = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            xhaab__uzdly = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            ukk__zhc = datetime.timedelta(zqnr__fpo - ptws__iszzp, 
                eeq__broid - xhaab__uzdly, lhs.microsecond - rhs.microsecond)
            return ukk__zhc
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    sbh__cuts = context.make_helper(builder, fromty, value=val)
    irj__fizuz = cgutils.as_bool_bit(builder, sbh__cuts.valid)
    with builder.if_else(irj__fizuz) as (yxdf__rfbu, sahu__zref):
        with yxdf__rfbu:
            mgchh__kyyv = context.cast(builder, sbh__cuts.data, fromty.type,
                toty)
            ejvpr__cvdov = builder.block
        with sahu__zref:
            yaxdk__lhrd = numba.np.npdatetime.NAT
            aiugd__gtp = builder.block
    axr__dhtwn = builder.phi(mgchh__kyyv.type)
    axr__dhtwn.add_incoming(mgchh__kyyv, ejvpr__cvdov)
    axr__dhtwn.add_incoming(yaxdk__lhrd, aiugd__gtp)
    return axr__dhtwn
