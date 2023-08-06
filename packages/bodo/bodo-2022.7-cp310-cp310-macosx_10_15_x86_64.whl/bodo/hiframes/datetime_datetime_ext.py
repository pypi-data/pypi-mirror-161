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
        emnm__vlo = [('year', types.int64), ('month', types.int64), ('day',
            types.int64), ('hour', types.int64), ('minute', types.int64), (
            'second', types.int64), ('microsecond', types.int64)]
        super(DatetimeDateTimeModel, self).__init__(dmm, fe_type, emnm__vlo)


@box(DatetimeDatetimeType)
def box_datetime_datetime(typ, val, c):
    ugc__szvhz = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    qmf__wyfh = c.pyapi.long_from_longlong(ugc__szvhz.year)
    qugqo__lri = c.pyapi.long_from_longlong(ugc__szvhz.month)
    mwxi__aapmp = c.pyapi.long_from_longlong(ugc__szvhz.day)
    olo__amov = c.pyapi.long_from_longlong(ugc__szvhz.hour)
    gtz__kgaz = c.pyapi.long_from_longlong(ugc__szvhz.minute)
    koi__smokf = c.pyapi.long_from_longlong(ugc__szvhz.second)
    fpuqc__ylooh = c.pyapi.long_from_longlong(ugc__szvhz.microsecond)
    ysitq__nia = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        datetime))
    ejgvm__ugjvb = c.pyapi.call_function_objargs(ysitq__nia, (qmf__wyfh,
        qugqo__lri, mwxi__aapmp, olo__amov, gtz__kgaz, koi__smokf,
        fpuqc__ylooh))
    c.pyapi.decref(qmf__wyfh)
    c.pyapi.decref(qugqo__lri)
    c.pyapi.decref(mwxi__aapmp)
    c.pyapi.decref(olo__amov)
    c.pyapi.decref(gtz__kgaz)
    c.pyapi.decref(koi__smokf)
    c.pyapi.decref(fpuqc__ylooh)
    c.pyapi.decref(ysitq__nia)
    return ejgvm__ugjvb


@unbox(DatetimeDatetimeType)
def unbox_datetime_datetime(typ, val, c):
    qmf__wyfh = c.pyapi.object_getattr_string(val, 'year')
    qugqo__lri = c.pyapi.object_getattr_string(val, 'month')
    mwxi__aapmp = c.pyapi.object_getattr_string(val, 'day')
    olo__amov = c.pyapi.object_getattr_string(val, 'hour')
    gtz__kgaz = c.pyapi.object_getattr_string(val, 'minute')
    koi__smokf = c.pyapi.object_getattr_string(val, 'second')
    fpuqc__ylooh = c.pyapi.object_getattr_string(val, 'microsecond')
    ugc__szvhz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ugc__szvhz.year = c.pyapi.long_as_longlong(qmf__wyfh)
    ugc__szvhz.month = c.pyapi.long_as_longlong(qugqo__lri)
    ugc__szvhz.day = c.pyapi.long_as_longlong(mwxi__aapmp)
    ugc__szvhz.hour = c.pyapi.long_as_longlong(olo__amov)
    ugc__szvhz.minute = c.pyapi.long_as_longlong(gtz__kgaz)
    ugc__szvhz.second = c.pyapi.long_as_longlong(koi__smokf)
    ugc__szvhz.microsecond = c.pyapi.long_as_longlong(fpuqc__ylooh)
    c.pyapi.decref(qmf__wyfh)
    c.pyapi.decref(qugqo__lri)
    c.pyapi.decref(mwxi__aapmp)
    c.pyapi.decref(olo__amov)
    c.pyapi.decref(gtz__kgaz)
    c.pyapi.decref(koi__smokf)
    c.pyapi.decref(fpuqc__ylooh)
    gbmng__iymwy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ugc__szvhz._getvalue(), is_error=gbmng__iymwy)


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
        ugc__szvhz = cgutils.create_struct_proxy(typ)(context, builder)
        ugc__szvhz.year = args[0]
        ugc__szvhz.month = args[1]
        ugc__szvhz.day = args[2]
        ugc__szvhz.hour = args[3]
        ugc__szvhz.minute = args[4]
        ugc__szvhz.second = args[5]
        ugc__szvhz.microsecond = args[6]
        return ugc__szvhz._getvalue()
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
                y, ipwo__fejg = lhs.year, rhs.year
                ptwkv__rru, vvdy__bdip = lhs.month, rhs.month
                d, kpkk__zgk = lhs.day, rhs.day
                oimto__jnzfw, nrd__ohwqp = lhs.hour, rhs.hour
                salkr__yym, shbpb__qxgh = lhs.minute, rhs.minute
                ltzt__lqh, cir__blwzs = lhs.second, rhs.second
                fmjuh__lsiqu, qgni__moc = lhs.microsecond, rhs.microsecond
                return op(_cmp((y, ptwkv__rru, d, oimto__jnzfw, salkr__yym,
                    ltzt__lqh, fmjuh__lsiqu), (ipwo__fejg, vvdy__bdip,
                    kpkk__zgk, nrd__ohwqp, shbpb__qxgh, cir__blwzs,
                    qgni__moc)), 0)
            return impl
    return overload_datetime_cmp


def overload_sub_operator_datetime_datetime(lhs, rhs):
    if lhs == datetime_datetime_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            yhqx__dxr = lhs.toordinal()
            apw__psxmb = rhs.toordinal()
            gwhr__ckgbp = lhs.second + lhs.minute * 60 + lhs.hour * 3600
            giyl__hrwks = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            doc__kyun = datetime.timedelta(yhqx__dxr - apw__psxmb, 
                gwhr__ckgbp - giyl__hrwks, lhs.microsecond - rhs.microsecond)
            return doc__kyun
        return impl


@lower_cast(types.Optional(numba.core.types.NPTimedelta('ns')), numba.core.
    types.NPTimedelta('ns'))
@lower_cast(types.Optional(numba.core.types.NPDatetime('ns')), numba.core.
    types.NPDatetime('ns'))
def optional_dt64_to_dt64(context, builder, fromty, toty, val):
    ncv__iob = context.make_helper(builder, fromty, value=val)
    wkstk__esi = cgutils.as_bool_bit(builder, ncv__iob.valid)
    with builder.if_else(wkstk__esi) as (bgg__yroau, rfrf__yutl):
        with bgg__yroau:
            sdbi__wtyh = context.cast(builder, ncv__iob.data, fromty.type, toty
                )
            ujl__tndk = builder.block
        with rfrf__yutl:
            uas__pmgh = numba.np.npdatetime.NAT
            xycr__vzjb = builder.block
    ejgvm__ugjvb = builder.phi(sdbi__wtyh.type)
    ejgvm__ugjvb.add_incoming(sdbi__wtyh, ujl__tndk)
    ejgvm__ugjvb.add_incoming(uas__pmgh, xycr__vzjb)
    return ejgvm__ugjvb
