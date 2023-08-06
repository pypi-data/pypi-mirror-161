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
        rgfj__tfdm = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, rgfj__tfdm)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    etk__bjn = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    talme__tecrg = c.pyapi.long_from_longlong(etk__bjn.n)
    edt__rqzmy = c.pyapi.from_native_value(types.boolean, etk__bjn.
        normalize, c.env_manager)
    rei__hbj = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    hcpdo__iwz = c.pyapi.call_function_objargs(rei__hbj, (talme__tecrg,
        edt__rqzmy))
    c.pyapi.decref(talme__tecrg)
    c.pyapi.decref(edt__rqzmy)
    c.pyapi.decref(rei__hbj)
    return hcpdo__iwz


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    talme__tecrg = c.pyapi.object_getattr_string(val, 'n')
    edt__rqzmy = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(talme__tecrg)
    normalize = c.pyapi.to_native_value(types.bool_, edt__rqzmy).value
    etk__bjn = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    etk__bjn.n = n
    etk__bjn.normalize = normalize
    c.pyapi.decref(talme__tecrg)
    c.pyapi.decref(edt__rqzmy)
    hefrd__rgj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(etk__bjn._getvalue(), is_error=hefrd__rgj)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        etk__bjn = cgutils.create_struct_proxy(typ)(context, builder)
        etk__bjn.n = args[0]
        etk__bjn.normalize = args[1]
        return etk__bjn._getvalue()
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
        rgfj__tfdm = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, rgfj__tfdm)


@box(MonthEndType)
def box_month_end(typ, val, c):
    undn__lgym = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    talme__tecrg = c.pyapi.long_from_longlong(undn__lgym.n)
    edt__rqzmy = c.pyapi.from_native_value(types.boolean, undn__lgym.
        normalize, c.env_manager)
    xmqvu__oadow = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    hcpdo__iwz = c.pyapi.call_function_objargs(xmqvu__oadow, (talme__tecrg,
        edt__rqzmy))
    c.pyapi.decref(talme__tecrg)
    c.pyapi.decref(edt__rqzmy)
    c.pyapi.decref(xmqvu__oadow)
    return hcpdo__iwz


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    talme__tecrg = c.pyapi.object_getattr_string(val, 'n')
    edt__rqzmy = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(talme__tecrg)
    normalize = c.pyapi.to_native_value(types.bool_, edt__rqzmy).value
    undn__lgym = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    undn__lgym.n = n
    undn__lgym.normalize = normalize
    c.pyapi.decref(talme__tecrg)
    c.pyapi.decref(edt__rqzmy)
    hefrd__rgj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(undn__lgym._getvalue(), is_error=hefrd__rgj)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        undn__lgym = cgutils.create_struct_proxy(typ)(context, builder)
        undn__lgym.n = args[0]
        undn__lgym.normalize = args[1]
        return undn__lgym._getvalue()
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
        undn__lgym = get_days_in_month(year, month)
        if undn__lgym > day:
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
        rgfj__tfdm = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, rgfj__tfdm)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    rnt__sqe = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    quhoa__rqot = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for urduo__ecbrk, owd__dxjak in enumerate(date_offset_fields):
        c.builder.store(getattr(rnt__sqe, owd__dxjak), c.builder.inttoptr(c
            .builder.add(c.builder.ptrtoint(quhoa__rqot, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * urduo__ecbrk)), lir.IntType(
            64).as_pointer()))
    kjoqh__uugq = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    tzttj__pcd = cgutils.get_or_insert_function(c.builder.module,
        kjoqh__uugq, name='box_date_offset')
    wwbup__xlv = c.builder.call(tzttj__pcd, [rnt__sqe.n, rnt__sqe.normalize,
        quhoa__rqot, rnt__sqe.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return wwbup__xlv


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    talme__tecrg = c.pyapi.object_getattr_string(val, 'n')
    edt__rqzmy = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(talme__tecrg)
    normalize = c.pyapi.to_native_value(types.bool_, edt__rqzmy).value
    quhoa__rqot = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    kjoqh__uugq = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer()])
    lte__obtjw = cgutils.get_or_insert_function(c.builder.module,
        kjoqh__uugq, name='unbox_date_offset')
    has_kws = c.builder.call(lte__obtjw, [val, quhoa__rqot])
    rnt__sqe = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rnt__sqe.n = n
    rnt__sqe.normalize = normalize
    for urduo__ecbrk, owd__dxjak in enumerate(date_offset_fields):
        setattr(rnt__sqe, owd__dxjak, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(quhoa__rqot, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * urduo__ecbrk)), lir.IntType(
            64).as_pointer())))
    rnt__sqe.has_kws = has_kws
    c.pyapi.decref(talme__tecrg)
    c.pyapi.decref(edt__rqzmy)
    hefrd__rgj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(rnt__sqe._getvalue(), is_error=hefrd__rgj)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    jvx__oqgz = [n, normalize]
    has_kws = False
    xrcb__bnzbv = [0] * 9 + [-1] * 9
    for urduo__ecbrk, owd__dxjak in enumerate(date_offset_fields):
        if hasattr(pyval, owd__dxjak):
            dou__jujx = context.get_constant(types.int64, getattr(pyval,
                owd__dxjak))
            has_kws = True
        else:
            dou__jujx = context.get_constant(types.int64, xrcb__bnzbv[
                urduo__ecbrk])
        jvx__oqgz.append(dou__jujx)
    has_kws = context.get_constant(types.boolean, has_kws)
    jvx__oqgz.append(has_kws)
    return lir.Constant.literal_struct(jvx__oqgz)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    kiru__epnhb = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for vde__wim in kiru__epnhb:
        if not is_overload_none(vde__wim):
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
        rnt__sqe = cgutils.create_struct_proxy(typ)(context, builder)
        rnt__sqe.n = args[0]
        rnt__sqe.normalize = args[1]
        rnt__sqe.years = args[2]
        rnt__sqe.months = args[3]
        rnt__sqe.weeks = args[4]
        rnt__sqe.days = args[5]
        rnt__sqe.hours = args[6]
        rnt__sqe.minutes = args[7]
        rnt__sqe.seconds = args[8]
        rnt__sqe.microseconds = args[9]
        rnt__sqe.nanoseconds = args[10]
        rnt__sqe.year = args[11]
        rnt__sqe.month = args[12]
        rnt__sqe.day = args[13]
        rnt__sqe.weekday = args[14]
        rnt__sqe.hour = args[15]
        rnt__sqe.minute = args[16]
        rnt__sqe.second = args[17]
        rnt__sqe.microsecond = args[18]
        rnt__sqe.nanosecond = args[19]
        rnt__sqe.has_kws = args[20]
        return rnt__sqe._getvalue()
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
        hryqa__tvibn = -1 if dateoffset.n < 0 else 1
        for spiwu__zzxlj in range(np.abs(dateoffset.n)):
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
            year += hryqa__tvibn * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += hryqa__tvibn * dateoffset._months
            year, month, ppbg__lvmgi = calculate_month_end_date(year, month,
                day, 0)
            if day > ppbg__lvmgi:
                day = ppbg__lvmgi
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
            kzja__hjbhe = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            kzja__hjbhe = kzja__hjbhe + pd.Timedelta(dateoffset.
                _nanoseconds, unit='ns')
            if hryqa__tvibn == -1:
                kzja__hjbhe = -kzja__hjbhe
            ts = ts + kzja__hjbhe
            if dateoffset._weekday != -1:
                emor__usbd = ts.weekday()
                afd__mfah = (dateoffset._weekday - emor__usbd) % 7
                ts = ts + pd.Timedelta(days=afd__mfah)
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
        rgfj__tfdm = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, rgfj__tfdm)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        uke__hbm = -1 if weekday is None else weekday
        return init_week(n, normalize, uke__hbm)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        uens__rcp = cgutils.create_struct_proxy(typ)(context, builder)
        uens__rcp.n = args[0]
        uens__rcp.normalize = args[1]
        uens__rcp.weekday = args[2]
        return uens__rcp._getvalue()
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
    uens__rcp = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    talme__tecrg = c.pyapi.long_from_longlong(uens__rcp.n)
    edt__rqzmy = c.pyapi.from_native_value(types.boolean, uens__rcp.
        normalize, c.env_manager)
    jblbk__mtpi = c.pyapi.long_from_longlong(uens__rcp.weekday)
    vevwq__almrw = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    xhi__gjc = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), -1
        ), uens__rcp.weekday)
    with c.builder.if_else(xhi__gjc) as (vvwf__erqzw, uow__rjdr):
        with vvwf__erqzw:
            ubkj__rijgs = c.pyapi.call_function_objargs(vevwq__almrw, (
                talme__tecrg, edt__rqzmy, jblbk__mtpi))
            vwzv__qnjhm = c.builder.block
        with uow__rjdr:
            uuwf__ybezp = c.pyapi.call_function_objargs(vevwq__almrw, (
                talme__tecrg, edt__rqzmy))
            odg__rpqa = c.builder.block
    hcpdo__iwz = c.builder.phi(ubkj__rijgs.type)
    hcpdo__iwz.add_incoming(ubkj__rijgs, vwzv__qnjhm)
    hcpdo__iwz.add_incoming(uuwf__ybezp, odg__rpqa)
    c.pyapi.decref(jblbk__mtpi)
    c.pyapi.decref(talme__tecrg)
    c.pyapi.decref(edt__rqzmy)
    c.pyapi.decref(vevwq__almrw)
    return hcpdo__iwz


@unbox(WeekType)
def unbox_week(typ, val, c):
    talme__tecrg = c.pyapi.object_getattr_string(val, 'n')
    edt__rqzmy = c.pyapi.object_getattr_string(val, 'normalize')
    jblbk__mtpi = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(talme__tecrg)
    normalize = c.pyapi.to_native_value(types.bool_, edt__rqzmy).value
    ieeb__cuu = c.pyapi.make_none()
    lwj__lxd = c.builder.icmp_unsigned('==', jblbk__mtpi, ieeb__cuu)
    with c.builder.if_else(lwj__lxd) as (uow__rjdr, vvwf__erqzw):
        with vvwf__erqzw:
            ubkj__rijgs = c.pyapi.long_as_longlong(jblbk__mtpi)
            vwzv__qnjhm = c.builder.block
        with uow__rjdr:
            uuwf__ybezp = lir.Constant(lir.IntType(64), -1)
            odg__rpqa = c.builder.block
    hcpdo__iwz = c.builder.phi(ubkj__rijgs.type)
    hcpdo__iwz.add_incoming(ubkj__rijgs, vwzv__qnjhm)
    hcpdo__iwz.add_incoming(uuwf__ybezp, odg__rpqa)
    uens__rcp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    uens__rcp.n = n
    uens__rcp.normalize = normalize
    uens__rcp.weekday = hcpdo__iwz
    c.pyapi.decref(talme__tecrg)
    c.pyapi.decref(edt__rqzmy)
    c.pyapi.decref(jblbk__mtpi)
    hefrd__rgj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(uens__rcp._getvalue(), is_error=hefrd__rgj)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            ikx__ujck = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                fjtw__wnevj = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                fjtw__wnevj = rhs
            return fjtw__wnevj + ikx__ujck
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            ikx__ujck = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                fjtw__wnevj = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                fjtw__wnevj = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return fjtw__wnevj + ikx__ujck
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            ikx__ujck = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + ikx__ujck
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
        wdxj__kpd = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=wdxj__kpd)


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
    for hnu__xuuxl in date_offset_unsupported_attrs:
        pbpl__zqmj = 'pandas.tseries.offsets.DateOffset.' + hnu__xuuxl
        overload_attribute(DateOffsetType, hnu__xuuxl)(
            create_unsupported_overload(pbpl__zqmj))
    for hnu__xuuxl in date_offset_unsupported:
        pbpl__zqmj = 'pandas.tseries.offsets.DateOffset.' + hnu__xuuxl
        overload_method(DateOffsetType, hnu__xuuxl)(create_unsupported_overload
            (pbpl__zqmj))


def _install_month_begin_unsupported():
    for hnu__xuuxl in month_begin_unsupported_attrs:
        pbpl__zqmj = 'pandas.tseries.offsets.MonthBegin.' + hnu__xuuxl
        overload_attribute(MonthBeginType, hnu__xuuxl)(
            create_unsupported_overload(pbpl__zqmj))
    for hnu__xuuxl in month_begin_unsupported:
        pbpl__zqmj = 'pandas.tseries.offsets.MonthBegin.' + hnu__xuuxl
        overload_method(MonthBeginType, hnu__xuuxl)(create_unsupported_overload
            (pbpl__zqmj))


def _install_month_end_unsupported():
    for hnu__xuuxl in date_offset_unsupported_attrs:
        pbpl__zqmj = 'pandas.tseries.offsets.MonthEnd.' + hnu__xuuxl
        overload_attribute(MonthEndType, hnu__xuuxl)(
            create_unsupported_overload(pbpl__zqmj))
    for hnu__xuuxl in date_offset_unsupported:
        pbpl__zqmj = 'pandas.tseries.offsets.MonthEnd.' + hnu__xuuxl
        overload_method(MonthEndType, hnu__xuuxl)(create_unsupported_overload
            (pbpl__zqmj))


def _install_week_unsupported():
    for hnu__xuuxl in week_unsupported_attrs:
        pbpl__zqmj = 'pandas.tseries.offsets.Week.' + hnu__xuuxl
        overload_attribute(WeekType, hnu__xuuxl)(create_unsupported_overload
            (pbpl__zqmj))
    for hnu__xuuxl in week_unsupported:
        pbpl__zqmj = 'pandas.tseries.offsets.Week.' + hnu__xuuxl
        overload_method(WeekType, hnu__xuuxl)(create_unsupported_overload(
            pbpl__zqmj))


def _install_offsets_unsupported():
    for dou__jujx in offsets_unsupported:
        pbpl__zqmj = 'pandas.tseries.offsets.' + dou__jujx.__name__
        overload(dou__jujx)(create_unsupported_overload(pbpl__zqmj))


def _install_frequencies_unsupported():
    for dou__jujx in frequencies_unsupported:
        pbpl__zqmj = 'pandas.tseries.frequencies.' + dou__jujx.__name__
        overload(dou__jujx)(create_unsupported_overload(pbpl__zqmj))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
