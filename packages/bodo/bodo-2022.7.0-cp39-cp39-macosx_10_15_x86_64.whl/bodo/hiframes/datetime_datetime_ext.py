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
        sysc__zff = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, sysc__zff)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    pgo__nlh = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    commu__cdsw = c.pyapi.long_from_longlong(pgo__nlh.year)
    sygj__okd = c.pyapi.long_from_longlong(pgo__nlh.month)
    wbd__cdlat = c.pyapi.long_from_longlong(pgo__nlh.day)
    pfyt__hcffc = c.pyapi.long_from_longlong(pgo__nlh.hour)
    ilj__nxgf = c.pyapi.long_from_longlong(pgo__nlh.minute)
    zzklg__rofdx = c.pyapi.long_from_longlong(pgo__nlh.second)
    kaaa__lwxr = c.pyapi.long_from_longlong(pgo__nlh.microsecond)
    swmtb__sbcm = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    lmbg__lgp = c.pyapi.call_function_objargs(swmtb__sbcm, (commu__cdsw,
        sygj__okd, wbd__cdlat, pfyt__hcffc, ilj__nxgf, zzklg__rofdx,
        kaaa__lwxr))
    c.pyapi.decref(commu__cdsw)
    c.pyapi.decref(sygj__okd)
    c.pyapi.decref(wbd__cdlat)
    c.pyapi.decref(pfyt__hcffc)
    c.pyapi.decref(ilj__nxgf)
    c.pyapi.decref(zzklg__rofdx)
    c.pyapi.decref(kaaa__lwxr)
    c.pyapi.decref(swmtb__sbcm)
    return lmbg__lgp


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    commu__cdsw = c.pyapi.object_getattr_string(val, 'year')
    sygj__okd = c.pyapi.object_getattr_string(val, 'month')
    wbd__cdlat = c.pyapi.object_getattr_string(val, 'day')
    pfyt__hcffc = c.pyapi.object_getattr_string(val, 'hour')
    ilj__nxgf = c.pyapi.object_getattr_string(val, 'minute')
    zzklg__rofdx = c.pyapi.object_getattr_string(val, 'second')
    kaaa__lwxr = c.pyapi.object_getattr_string(val, 'microsecond')
    pgo__nlh = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pgo__nlh.year = c.pyapi.long_as_longlong(commu__cdsw)
    pgo__nlh.month = c.pyapi.long_as_longlong(sygj__okd)
    pgo__nlh.day = c.pyapi.long_as_longlong(wbd__cdlat)
    pgo__nlh.hour = c.pyapi.long_as_longlong(pfyt__hcffc)
    pgo__nlh.minute = c.pyapi.long_as_longlong(ilj__nxgf)
    pgo__nlh.second = c.pyapi.long_as_longlong(zzklg__rofdx)
    pgo__nlh.microsecond = c.pyapi.long_as_longlong(kaaa__lwxr)
    c.pyapi.decref(commu__cdsw)
    c.pyapi.decref(sygj__okd)
    c.pyapi.decref(wbd__cdlat)
    c.pyapi.decref(pfyt__hcffc)
    c.pyapi.decref(ilj__nxgf)
    c.pyapi.decref(zzklg__rofdx)
    c.pyapi.decref(kaaa__lwxr)
    esu__hen = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(pgo__nlh._getvalue(), is_error=esu__hen)


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
        pgo__nlh = cgutils.create_struct_proxy(typ)(context, builder)
        pgo__nlh.year = args[0]
        pgo__nlh.month = args[1]
        pgo__nlh.day = args[2]
        pgo__nlh.hour = args[3]
        pgo__nlh.minute = args[4]
        pgo__nlh.second = args[5]
        pgo__nlh.microsecond = args[6]
        return pgo__nlh._getvalue()
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
                y, eln__mhc = lhs.year, rhs.year
                aiya__ybsn, vhvpd__jcpn = lhs.month, rhs.month
                d, too__rvcpq = lhs.day, rhs.day
                hexr__hbgij, svz__yid = lhs.hour, rhs.hour
                gkg__crjx, vpq__jggdj = lhs.minute, rhs.minute
                tayva__bsn, mmbnr__zhs = lhs.second, rhs.second
                vgnc__ezga, ubi__pdb = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, aiya__ybsn, d, hexr__hbgij, gkg__crjx,
                    tayva__bsn, vgnc__ezga), (eln__mhc, vhvpd__jcpn,
                    too__rvcpq, svz__yid, vpq__jggdj, mmbnr__zhs, ubi__pdb)), 0
                    )
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            mqtew__dswl = lhs.toordinal()
            ssn__wxwpe = rhs.toordinal()
            nlo__gss = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            wqh__xxzj = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            erxo__zfdt = datetime.timedelta(mqtew__dswl - ssn__wxwpe, 
                nlo__gss - wqh__xxzj, lhs.microsecond - rhs.microsecond)
            return erxo__zfdt
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    krtv__uqvgs = context.make_helper(builder, fromty, value=val)
    gcnqk__hnp = cgutils.as_bool_bit(builder, krtv__uqvgs.valid)
    with builder.if_else(gcnqk__hnp) as (ztwh__vba, djqdb__zrbgk):
        with ztwh__vba:
            dvj__uoxm = context.cast(builder, krtv__uqvgs.data, fromty.type,
                toty)
            cykdz__rrme = builder.block
        with djqdb__zrbgk:
            lrv__ilnnn = numba.np.npdatetime.NAT
            wtra__yijy = builder.block
    lmbg__lgp = builder.phi(dvj__uoxm.type)
    lmbg__lgp.add_incoming(dvj__uoxm, cykdz__rrme)
    lmbg__lgp.add_incoming(lrv__ilnnn, wtra__yijy)
    return lmbg__lgp
