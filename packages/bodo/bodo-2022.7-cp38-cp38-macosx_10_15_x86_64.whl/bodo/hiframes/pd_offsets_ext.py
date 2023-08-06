"""
Implement support for the various classes in pd.tseries.offsets.
"""
import operator
import llvmlite.binding as ll
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.pd_timestamp_ext import get_days_in_month, pd_timestamp_type
from bodo.libs import hdatetime_ext
from bodo.utils.typing import BodoError, create_unsupported_overload, is_overload_none
ll.add_symbol('box_date_offset', hdatetime_ext.box_date_offset)
ll.add_symbol('unbox_date_offset', hdatetime_ext.unbox_date_offset)


class MonthBeginType(types.Type):

    def __init__(self):
        super(MonthBeginType, self).__init__(name='MonthBeginType()')


month_begin_type = MonthBeginType()


@typeof_impl.register(pd.tseries.offsets.MonthBegin)
def typeof_month_begin(val, c):
    return month_begin_type


@register_model(MonthBeginType)
class MonthBeginModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        eqr__enp = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, eqr__enp)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    vsnsu__fduam = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    fuh__qlmgg = c.pyapi.long_from_longlong(vsnsu__fduam.n)
    esg__qtags = c.pyapi.from_native_value(types.boolean, vsnsu__fduam.
        normalize, c.env_manager)
    feoo__yujw = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    bhy__awy = c.pyapi.call_function_objargs(feoo__yujw, (fuh__qlmgg,
        esg__qtags))
    c.pyapi.decref(fuh__qlmgg)
    c.pyapi.decref(esg__qtags)
    c.pyapi.decref(feoo__yujw)
    return bhy__awy


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    fuh__qlmgg = c.pyapi.object_getattr_string(val, 'n')
    esg__qtags = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(fuh__qlmgg)
    normalize = c.pyapi.to_native_value(types.bool_, esg__qtags).value
    vsnsu__fduam = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vsnsu__fduam.n = n
    vsnsu__fduam.normalize = normalize
    c.pyapi.decref(fuh__qlmgg)
    c.pyapi.decref(esg__qtags)
    zjk__jfw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vsnsu__fduam._getvalue(), is_error=zjk__jfw)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        vsnsu__fduam = cgutils.create_struct_proxy(typ)(context, builder)
        vsnsu__fduam.n = args[0]
        vsnsu__fduam.normalize = args[1]
        return vsnsu__fduam._getvalue()
    return MonthBeginType()(n, normalize), codegen


make_attribute_wrapper(MonthBeginType, 'n', 'n')
make_attribute_wrapper(MonthBeginType, 'normalize', 'normalize')


@register_jitable
def calculate_month_begin_date(year, month, day, n):
    if n <= 0:
        if day > 1:
            n += 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = 1
    return year, month, day


def overload_add_operator_month_begin_offset_type(lhs, rhs):
    if lhs == month_begin_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_begin_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_begin_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_begin_date(rhs.year, rhs.
                month, rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_begin_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


class MonthEndType(types.Type):

    def __init__(self):
        super(MonthEndType, self).__init__(name='MonthEndType()')


month_end_type = MonthEndType()


@typeof_impl.register(pd.tseries.offsets.MonthEnd)
def typeof_month_end(val, c):
    return month_end_type


@register_model(MonthEndType)
class MonthEndModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        eqr__enp = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, eqr__enp)


@box(MonthEndType)
def box_month_end(typ, val, c):
    ank__idn = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    fuh__qlmgg = c.pyapi.long_from_longlong(ank__idn.n)
    esg__qtags = c.pyapi.from_native_value(types.boolean, ank__idn.
        normalize, c.env_manager)
    dyp__rwro = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    bhy__awy = c.pyapi.call_function_objargs(dyp__rwro, (fuh__qlmgg,
        esg__qtags))
    c.pyapi.decref(fuh__qlmgg)
    c.pyapi.decref(esg__qtags)
    c.pyapi.decref(dyp__rwro)
    return bhy__awy


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    fuh__qlmgg = c.pyapi.object_getattr_string(val, 'n')
    esg__qtags = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(fuh__qlmgg)
    normalize = c.pyapi.to_native_value(types.bool_, esg__qtags).value
    ank__idn = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ank__idn.n = n
    ank__idn.normalize = normalize
    c.pyapi.decref(fuh__qlmgg)
    c.pyapi.decref(esg__qtags)
    zjk__jfw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ank__idn._getvalue(), is_error=zjk__jfw)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        ank__idn = cgutils.create_struct_proxy(typ)(context, builder)
        ank__idn.n = args[0]
        ank__idn.normalize = args[1]
        return ank__idn._getvalue()
    return MonthEndType()(n, normalize), codegen


make_attribute_wrapper(MonthEndType, 'n', 'n')
make_attribute_wrapper(MonthEndType, 'normalize', 'normalize')


@lower_constant(MonthBeginType)
@lower_constant(MonthEndType)
def lower_constant_month_end(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    return lir.Constant.literal_struct([n, normalize])


@register_jitable
def calculate_month_end_date(year, month, day, n):
    if n > 0:
        ank__idn = get_days_in_month(year, month)
        if ank__idn > day:
            n -= 1
    month = month + n
    month -= 1
    year += month // 12
    month = month % 12 + 1
    day = get_days_in_month(year, month)
    return year, month, day


def overload_add_operator_month_end_offset_type(lhs, rhs):
    if lhs == month_end_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond)
        return impl
    if lhs == month_end_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            if lhs.normalize:
                return pd.Timestamp(year=year, month=month, day=day)
            else:
                return pd.Timestamp(year=year, month=month, day=day, hour=
                    rhs.hour, minute=rhs.minute, second=rhs.second,
                    microsecond=rhs.microsecond, nanosecond=rhs.nanosecond)
        return impl
    if lhs == month_end_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            year, month, day = calculate_month_end_date(rhs.year, rhs.month,
                rhs.day, lhs.n)
            return pd.Timestamp(year=year, month=month, day=day)
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == month_end_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_mul_date_offset_types(lhs, rhs):
    if lhs == month_begin_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthBegin(lhs.n * rhs, lhs.normalize)
    if lhs == month_end_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.MonthEnd(lhs.n * rhs, lhs.normalize)
    if lhs == week_type:

        def impl(lhs, rhs):
            return pd.tseries.offsets.Week(lhs.n * rhs, lhs.normalize, lhs.
                weekday)
    if lhs == date_offset_type:

        def impl(lhs, rhs):
            n = lhs.n * rhs
            normalize = lhs.normalize
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                nanoseconds = lhs._nanoseconds
                nanosecond = lhs._nanosecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize)
    if rhs in [week_type, month_end_type, month_begin_type, date_offset_type]:

        def impl(lhs, rhs):
            return rhs * lhs
        return impl
    return impl


class DateOffsetType(types.Type):

    def __init__(self):
        super(DateOffsetType, self).__init__(name='DateOffsetType()')


date_offset_type = DateOffsetType()
date_offset_fields = ['years', 'months', 'weeks', 'days', 'hours',
    'minutes', 'seconds', 'microseconds', 'nanoseconds', 'year', 'month',
    'day', 'weekday', 'hour', 'minute', 'second', 'microsecond', 'nanosecond']


@typeof_impl.register(pd.tseries.offsets.DateOffset)
def type_of_date_offset(val, c):
    return date_offset_type


@register_model(DateOffsetType)
class DateOffsetModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        eqr__enp = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, eqr__enp)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    bndek__rmbql = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    vjs__awe = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for wtolb__gdkj, nqsp__jdut in enumerate(date_offset_fields):
        c.builder.store(getattr(bndek__rmbql, nqsp__jdut), c.builder.
            inttoptr(c.builder.add(c.builder.ptrtoint(vjs__awe, lir.IntType
            (64)), lir.Constant(lir.IntType(64), 8 * wtolb__gdkj)), lir.
            IntType(64).as_pointer()))
    gsl__ebe = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    dsl__fqmxe = cgutils.get_or_insert_function(c.builder.module, gsl__ebe,
        name='box_date_offset')
    vcph__ndper = c.builder.call(dsl__fqmxe, [bndek__rmbql.n, bndek__rmbql.
        normalize, vjs__awe, bndek__rmbql.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return vcph__ndper


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    fuh__qlmgg = c.pyapi.object_getattr_string(val, 'n')
    esg__qtags = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(fuh__qlmgg)
    normalize = c.pyapi.to_native_value(types.bool_, esg__qtags).value
    vjs__awe = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    gsl__ebe = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer(
        ), lir.IntType(64).as_pointer()])
    lltx__oyf = cgutils.get_or_insert_function(c.builder.module, gsl__ebe,
        name='unbox_date_offset')
    has_kws = c.builder.call(lltx__oyf, [val, vjs__awe])
    bndek__rmbql = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bndek__rmbql.n = n
    bndek__rmbql.normalize = normalize
    for wtolb__gdkj, nqsp__jdut in enumerate(date_offset_fields):
        setattr(bndek__rmbql, nqsp__jdut, c.builder.load(c.builder.inttoptr
            (c.builder.add(c.builder.ptrtoint(vjs__awe, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * wtolb__gdkj)), lir.IntType(64
            ).as_pointer())))
    bndek__rmbql.has_kws = has_kws
    c.pyapi.decref(fuh__qlmgg)
    c.pyapi.decref(esg__qtags)
    zjk__jfw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(bndek__rmbql._getvalue(), is_error=zjk__jfw)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    coe__cnifw = [n, normalize]
    has_kws = False
    vvbq__xmnv = [0] * 9 + [-1] * 9
    for wtolb__gdkj, nqsp__jdut in enumerate(date_offset_fields):
        if hasattr(pyval, nqsp__jdut):
            qxrp__tnc = context.get_constant(types.int64, getattr(pyval,
                nqsp__jdut))
            has_kws = True
        else:
            qxrp__tnc = context.get_constant(types.int64, vvbq__xmnv[
                wtolb__gdkj])
        coe__cnifw.append(qxrp__tnc)
    has_kws = context.get_constant(types.boolean, has_kws)
    coe__cnifw.append(has_kws)
    return lir.Constant.literal_struct(coe__cnifw)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    sqh__lmfj = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for rdd__fmu in sqh__lmfj:
        if not is_overload_none(rdd__fmu):
            has_kws = True
            break

    def impl(n=1, normalize=False, years=None, months=None, weeks=None,
        days=None, hours=None, minutes=None, seconds=None, microseconds=
        None, nanoseconds=None, year=None, month=None, day=None, weekday=
        None, hour=None, minute=None, second=None, microsecond=None,
        nanosecond=None):
        years = 0 if years is None else years
        months = 0 if months is None else months
        weeks = 0 if weeks is None else weeks
        days = 0 if days is None else days
        hours = 0 if hours is None else hours
        minutes = 0 if minutes is None else minutes
        seconds = 0 if seconds is None else seconds
        microseconds = 0 if microseconds is None else microseconds
        nanoseconds = 0 if nanoseconds is None else nanoseconds
        year = -1 if year is None else year
        month = -1 if month is None else month
        weekday = -1 if weekday is None else weekday
        day = -1 if day is None else day
        hour = -1 if hour is None else hour
        minute = -1 if minute is None else minute
        second = -1 if second is None else second
        microsecond = -1 if microsecond is None else microsecond
        nanosecond = -1 if nanosecond is None else nanosecond
        return init_date_offset(n, normalize, years, months, weeks, days,
            hours, minutes, seconds, microseconds, nanoseconds, year, month,
            day, weekday, hour, minute, second, microsecond, nanosecond,
            has_kws)
    return impl


@intrinsic
def init_date_offset(typingctx, n, normalize, years, months, weeks, days,
    hours, minutes, seconds, microseconds, nanoseconds, year, month, day,
    weekday, hour, minute, second, microsecond, nanosecond, has_kws):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        bndek__rmbql = cgutils.create_struct_proxy(typ)(context, builder)
        bndek__rmbql.n = args[0]
        bndek__rmbql.normalize = args[1]
        bndek__rmbql.years = args[2]
        bndek__rmbql.months = args[3]
        bndek__rmbql.weeks = args[4]
        bndek__rmbql.days = args[5]
        bndek__rmbql.hours = args[6]
        bndek__rmbql.minutes = args[7]
        bndek__rmbql.seconds = args[8]
        bndek__rmbql.microseconds = args[9]
        bndek__rmbql.nanoseconds = args[10]
        bndek__rmbql.year = args[11]
        bndek__rmbql.month = args[12]
        bndek__rmbql.day = args[13]
        bndek__rmbql.weekday = args[14]
        bndek__rmbql.hour = args[15]
        bndek__rmbql.minute = args[16]
        bndek__rmbql.second = args[17]
        bndek__rmbql.microsecond = args[18]
        bndek__rmbql.nanosecond = args[19]
        bndek__rmbql.has_kws = args[20]
        return bndek__rmbql._getvalue()
    return DateOffsetType()(n, normalize, years, months, weeks, days, hours,
        minutes, seconds, microseconds, nanoseconds, year, month, day,
        weekday, hour, minute, second, microsecond, nanosecond, has_kws
        ), codegen


make_attribute_wrapper(DateOffsetType, 'n', 'n')
make_attribute_wrapper(DateOffsetType, 'normalize', 'normalize')
make_attribute_wrapper(DateOffsetType, 'years', '_years')
make_attribute_wrapper(DateOffsetType, 'months', '_months')
make_attribute_wrapper(DateOffsetType, 'weeks', '_weeks')
make_attribute_wrapper(DateOffsetType, 'days', '_days')
make_attribute_wrapper(DateOffsetType, 'hours', '_hours')
make_attribute_wrapper(DateOffsetType, 'minutes', '_minutes')
make_attribute_wrapper(DateOffsetType, 'seconds', '_seconds')
make_attribute_wrapper(DateOffsetType, 'microseconds', '_microseconds')
make_attribute_wrapper(DateOffsetType, 'nanoseconds', '_nanoseconds')
make_attribute_wrapper(DateOffsetType, 'year', '_year')
make_attribute_wrapper(DateOffsetType, 'month', '_month')
make_attribute_wrapper(DateOffsetType, 'weekday', '_weekday')
make_attribute_wrapper(DateOffsetType, 'day', '_day')
make_attribute_wrapper(DateOffsetType, 'hour', '_hour')
make_attribute_wrapper(DateOffsetType, 'minute', '_minute')
make_attribute_wrapper(DateOffsetType, 'second', '_second')
make_attribute_wrapper(DateOffsetType, 'microsecond', '_microsecond')
make_attribute_wrapper(DateOffsetType, 'nanosecond', '_nanosecond')
make_attribute_wrapper(DateOffsetType, 'has_kws', '_has_kws')


@register_jitable
def relative_delta_addition(dateoffset, ts):
    if dateoffset._has_kws:
        ktftj__ywaet = -1 if dateoffset.n < 0 else 1
        for dea__anxqp in range(np.abs(dateoffset.n)):
            year = ts.year
            month = ts.month
            day = ts.day
            hour = ts.hour
            minute = ts.minute
            second = ts.second
            microsecond = ts.microsecond
            nanosecond = ts.nanosecond
            if dateoffset._year != -1:
                year = dateoffset._year
            year += ktftj__ywaet * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += ktftj__ywaet * dateoffset._months
            year, month, rqu__hmjye = calculate_month_end_date(year, month,
                day, 0)
            if day > rqu__hmjye:
                day = rqu__hmjye
            if dateoffset._day != -1:
                day = dateoffset._day
            if dateoffset._hour != -1:
                hour = dateoffset._hour
            if dateoffset._minute != -1:
                minute = dateoffset._minute
            if dateoffset._second != -1:
                second = dateoffset._second
            if dateoffset._microsecond != -1:
                microsecond = dateoffset._microsecond
            if dateoffset._nanosecond != -1:
                nanosecond = dateoffset._nanosecond
            ts = pd.Timestamp(year=year, month=month, day=day, hour=hour,
                minute=minute, second=second, microsecond=microsecond,
                nanosecond=nanosecond)
            llpi__epi = pd.Timedelta(days=dateoffset._days + 7 * dateoffset
                ._weeks, hours=dateoffset._hours, minutes=dateoffset.
                _minutes, seconds=dateoffset._seconds, microseconds=
                dateoffset._microseconds)
            llpi__epi = llpi__epi + pd.Timedelta(dateoffset._nanoseconds,
                unit='ns')
            if ktftj__ywaet == -1:
                llpi__epi = -llpi__epi
            ts = ts + llpi__epi
            if dateoffset._weekday != -1:
                nxo__hkjo = ts.weekday()
                tkqmx__eog = (dateoffset._weekday - nxo__hkjo) % 7
                ts = ts + pd.Timedelta(days=tkqmx__eog)
        return ts
    else:
        return pd.Timedelta(days=dateoffset.n) + ts


def overload_add_operator_date_offset_type(lhs, rhs):
    if lhs == date_offset_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, rhs)
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs == date_offset_type and rhs in [datetime_date_type,
        datetime_datetime_type]:

        def impl(lhs, rhs):
            ts = relative_delta_addition(lhs, pd.Timestamp(rhs))
            if lhs.normalize:
                return ts.normalize()
            return ts
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == date_offset_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


def overload_sub_operator_offsets(lhs, rhs):
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs in [date_offset_type, month_begin_type, month_end_type,
        week_type]:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl


@overload(operator.neg, no_unliteral=True)
def overload_neg(lhs):
    if lhs == month_begin_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthBegin(-lhs.n, lhs.normalize)
    elif lhs == month_end_type:

        def impl(lhs):
            return pd.tseries.offsets.MonthEnd(-lhs.n, lhs.normalize)
    elif lhs == week_type:

        def impl(lhs):
            return pd.tseries.offsets.Week(-lhs.n, lhs.normalize, lhs.weekday)
    elif lhs == date_offset_type:

        def impl(lhs):
            n = -lhs.n
            normalize = lhs.normalize
            if lhs._has_kws:
                years = lhs._years
                months = lhs._months
                weeks = lhs._weeks
                days = lhs._days
                hours = lhs._hours
                minutes = lhs._minutes
                seconds = lhs._seconds
                microseconds = lhs._microseconds
                year = lhs._year
                month = lhs._month
                day = lhs._day
                weekday = lhs._weekday
                hour = lhs._hour
                minute = lhs._minute
                second = lhs._second
                microsecond = lhs._microsecond
                nanoseconds = lhs._nanoseconds
                nanosecond = lhs._nanosecond
                return pd.tseries.offsets.DateOffset(n, normalize, years,
                    months, weeks, days, hours, minutes, seconds,
                    microseconds, nanoseconds, year, month, day, weekday,
                    hour, minute, second, microsecond, nanosecond)
            else:
                return pd.tseries.offsets.DateOffset(n, normalize)
    else:
        return
    return impl


def is_offsets_type(val):
    return val in [date_offset_type, month_begin_type, month_end_type,
        week_type]


class WeekType(types.Type):

    def __init__(self):
        super(WeekType, self).__init__(name='WeekType()')


week_type = WeekType()


@typeof_impl.register(pd.tseries.offsets.Week)
def typeof_week(val, c):
    return week_type


@register_model(WeekType)
class WeekModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        eqr__enp = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, eqr__enp)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        fnaul__mij = -1 if weekday is None else weekday
        return init_week(n, normalize, fnaul__mij)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        aarc__svwa = cgutils.create_struct_proxy(typ)(context, builder)
        aarc__svwa.n = args[0]
        aarc__svwa.normalize = args[1]
        aarc__svwa.weekday = args[2]
        return aarc__svwa._getvalue()
    return WeekType()(n, normalize, weekday), codegen


@lower_constant(WeekType)
def lower_constant_week(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    if pyval.weekday is not None:
        weekday = context.get_constant(types.int64, pyval.weekday)
    else:
        weekday = context.get_constant(types.int64, -1)
    return lir.Constant.literal_struct([n, normalize, weekday])


@box(WeekType)
def box_week(typ, val, c):
    aarc__svwa = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    fuh__qlmgg = c.pyapi.long_from_longlong(aarc__svwa.n)
    esg__qtags = c.pyapi.from_native_value(types.boolean, aarc__svwa.
        normalize, c.env_manager)
    gndpi__xweak = c.pyapi.long_from_longlong(aarc__svwa.weekday)
    alzc__wwqh = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    zmns__nkew = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), 
        -1), aarc__svwa.weekday)
    with c.builder.if_else(zmns__nkew) as (ztsk__gntam, wxyvy__dsx):
        with ztsk__gntam:
            qndh__nqvva = c.pyapi.call_function_objargs(alzc__wwqh, (
                fuh__qlmgg, esg__qtags, gndpi__xweak))
            irmr__ikcjt = c.builder.block
        with wxyvy__dsx:
            uyy__cvn = c.pyapi.call_function_objargs(alzc__wwqh, (
                fuh__qlmgg, esg__qtags))
            fqml__wss = c.builder.block
    bhy__awy = c.builder.phi(qndh__nqvva.type)
    bhy__awy.add_incoming(qndh__nqvva, irmr__ikcjt)
    bhy__awy.add_incoming(uyy__cvn, fqml__wss)
    c.pyapi.decref(gndpi__xweak)
    c.pyapi.decref(fuh__qlmgg)
    c.pyapi.decref(esg__qtags)
    c.pyapi.decref(alzc__wwqh)
    return bhy__awy


@unbox(WeekType)
def unbox_week(typ, val, c):
    fuh__qlmgg = c.pyapi.object_getattr_string(val, 'n')
    esg__qtags = c.pyapi.object_getattr_string(val, 'normalize')
    gndpi__xweak = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(fuh__qlmgg)
    normalize = c.pyapi.to_native_value(types.bool_, esg__qtags).value
    kuoad__vugv = c.pyapi.make_none()
    frv__wioni = c.builder.icmp_unsigned('==', gndpi__xweak, kuoad__vugv)
    with c.builder.if_else(frv__wioni) as (wxyvy__dsx, ztsk__gntam):
        with ztsk__gntam:
            qndh__nqvva = c.pyapi.long_as_longlong(gndpi__xweak)
            irmr__ikcjt = c.builder.block
        with wxyvy__dsx:
            uyy__cvn = lir.Constant(lir.IntType(64), -1)
            fqml__wss = c.builder.block
    bhy__awy = c.builder.phi(qndh__nqvva.type)
    bhy__awy.add_incoming(qndh__nqvva, irmr__ikcjt)
    bhy__awy.add_incoming(uyy__cvn, fqml__wss)
    aarc__svwa = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    aarc__svwa.n = n
    aarc__svwa.normalize = normalize
    aarc__svwa.weekday = bhy__awy
    c.pyapi.decref(fuh__qlmgg)
    c.pyapi.decref(esg__qtags)
    c.pyapi.decref(gndpi__xweak)
    zjk__jfw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(aarc__svwa._getvalue(), is_error=zjk__jfw)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            fabyp__gzbf = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            if lhs.normalize:
                jevto__dfii = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                jevto__dfii = rhs
            return jevto__dfii + fabyp__gzbf
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            fabyp__gzbf = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            if lhs.normalize:
                jevto__dfii = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                jevto__dfii = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return jevto__dfii + fabyp__gzbf
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            fabyp__gzbf = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            return rhs + fabyp__gzbf
        return impl
    if lhs in [datetime_datetime_type, pd_timestamp_type, datetime_date_type
        ] and rhs == week_type:

        def impl(lhs, rhs):
            return rhs + lhs
        return impl
    raise BodoError(
        f'add operator not supported for data types {lhs} and {rhs}.')


@register_jitable
def calculate_week_date(n, weekday, other_weekday):
    if weekday == -1:
        return pd.Timedelta(weeks=n)
    if weekday != other_weekday:
        fid__cybs = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=fid__cybs)


date_offset_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
date_offset_unsupported = {'__call__', 'rollback', 'rollforward',
    'is_month_start', 'is_month_end', 'apply', 'apply_index', 'copy',
    'isAnchored', 'onOffset', 'is_anchored', 'is_on_offset',
    'is_quarter_start', 'is_quarter_end', 'is_year_start', 'is_year_end'}
month_end_unsupported_attrs = {'base', 'freqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_end_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
month_begin_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos',
    'rule_code'}
month_begin_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
week_unsupported_attrs = {'basefreqstr', 'kwds', 'name', 'nanos', 'rule_code'}
week_unsupported = {'__call__', 'rollback', 'rollforward', 'apply',
    'apply_index', 'copy', 'isAnchored', 'onOffset', 'is_anchored',
    'is_on_offset', 'is_month_start', 'is_month_end', 'is_quarter_start',
    'is_quarter_end', 'is_year_start', 'is_year_end'}
offsets_unsupported = {pd.tseries.offsets.BusinessDay, pd.tseries.offsets.
    BDay, pd.tseries.offsets.BusinessHour, pd.tseries.offsets.
    CustomBusinessDay, pd.tseries.offsets.CDay, pd.tseries.offsets.
    CustomBusinessHour, pd.tseries.offsets.BusinessMonthEnd, pd.tseries.
    offsets.BMonthEnd, pd.tseries.offsets.BusinessMonthBegin, pd.tseries.
    offsets.BMonthBegin, pd.tseries.offsets.CustomBusinessMonthEnd, pd.
    tseries.offsets.CBMonthEnd, pd.tseries.offsets.CustomBusinessMonthBegin,
    pd.tseries.offsets.CBMonthBegin, pd.tseries.offsets.SemiMonthEnd, pd.
    tseries.offsets.SemiMonthBegin, pd.tseries.offsets.WeekOfMonth, pd.
    tseries.offsets.LastWeekOfMonth, pd.tseries.offsets.BQuarterEnd, pd.
    tseries.offsets.BQuarterBegin, pd.tseries.offsets.QuarterEnd, pd.
    tseries.offsets.QuarterBegin, pd.tseries.offsets.BYearEnd, pd.tseries.
    offsets.BYearBegin, pd.tseries.offsets.YearEnd, pd.tseries.offsets.
    YearBegin, pd.tseries.offsets.FY5253, pd.tseries.offsets.FY5253Quarter,
    pd.tseries.offsets.Easter, pd.tseries.offsets.Tick, pd.tseries.offsets.
    Day, pd.tseries.offsets.Hour, pd.tseries.offsets.Minute, pd.tseries.
    offsets.Second, pd.tseries.offsets.Milli, pd.tseries.offsets.Micro, pd.
    tseries.offsets.Nano}
frequencies_unsupported = {pd.tseries.frequencies.to_offset}


def _install_date_offsets_unsupported():
    for iifuo__oqcv in date_offset_unsupported_attrs:
        pvx__gtc = 'pandas.tseries.offsets.DateOffset.' + iifuo__oqcv
        overload_attribute(DateOffsetType, iifuo__oqcv)(
            create_unsupported_overload(pvx__gtc))
    for iifuo__oqcv in date_offset_unsupported:
        pvx__gtc = 'pandas.tseries.offsets.DateOffset.' + iifuo__oqcv
        overload_method(DateOffsetType, iifuo__oqcv)(
            create_unsupported_overload(pvx__gtc))


def _install_month_begin_unsupported():
    for iifuo__oqcv in month_begin_unsupported_attrs:
        pvx__gtc = 'pandas.tseries.offsets.MonthBegin.' + iifuo__oqcv
        overload_attribute(MonthBeginType, iifuo__oqcv)(
            create_unsupported_overload(pvx__gtc))
    for iifuo__oqcv in month_begin_unsupported:
        pvx__gtc = 'pandas.tseries.offsets.MonthBegin.' + iifuo__oqcv
        overload_method(MonthBeginType, iifuo__oqcv)(
            create_unsupported_overload(pvx__gtc))


def _install_month_end_unsupported():
    for iifuo__oqcv in date_offset_unsupported_attrs:
        pvx__gtc = 'pandas.tseries.offsets.MonthEnd.' + iifuo__oqcv
        overload_attribute(MonthEndType, iifuo__oqcv)(
            create_unsupported_overload(pvx__gtc))
    for iifuo__oqcv in date_offset_unsupported:
        pvx__gtc = 'pandas.tseries.offsets.MonthEnd.' + iifuo__oqcv
        overload_method(MonthEndType, iifuo__oqcv)(create_unsupported_overload
            (pvx__gtc))


def _install_week_unsupported():
    for iifuo__oqcv in week_unsupported_attrs:
        pvx__gtc = 'pandas.tseries.offsets.Week.' + iifuo__oqcv
        overload_attribute(WeekType, iifuo__oqcv)(create_unsupported_overload
            (pvx__gtc))
    for iifuo__oqcv in week_unsupported:
        pvx__gtc = 'pandas.tseries.offsets.Week.' + iifuo__oqcv
        overload_method(WeekType, iifuo__oqcv)(create_unsupported_overload(
            pvx__gtc))


def _install_offsets_unsupported():
    for qxrp__tnc in offsets_unsupported:
        pvx__gtc = 'pandas.tseries.offsets.' + qxrp__tnc.__name__
        overload(qxrp__tnc)(create_unsupported_overload(pvx__gtc))


def _install_frequencies_unsupported():
    for qxrp__tnc in frequencies_unsupported:
        pvx__gtc = 'pandas.tseries.frequencies.' + qxrp__tnc.__name__
        overload(qxrp__tnc)(create_unsupported_overload(pvx__gtc))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
