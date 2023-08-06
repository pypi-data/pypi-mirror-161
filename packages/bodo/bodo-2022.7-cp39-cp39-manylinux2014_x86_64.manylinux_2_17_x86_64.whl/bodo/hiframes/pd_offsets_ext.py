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
        jnq__yoa = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, jnq__yoa)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    nmf__gxozd = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    mixp__sooc = c.pyapi.long_from_longlong(nmf__gxozd.n)
    klg__qhs = c.pyapi.from_native_value(types.boolean, nmf__gxozd.
        normalize, c.env_manager)
    cce__psal = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    fzo__ftu = c.pyapi.call_function_objargs(cce__psal, (mixp__sooc, klg__qhs))
    c.pyapi.decref(mixp__sooc)
    c.pyapi.decref(klg__qhs)
    c.pyapi.decref(cce__psal)
    return fzo__ftu


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    mixp__sooc = c.pyapi.object_getattr_string(val, 'n')
    klg__qhs = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(mixp__sooc)
    normalize = c.pyapi.to_native_value(types.bool_, klg__qhs).value
    nmf__gxozd = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nmf__gxozd.n = n
    nmf__gxozd.normalize = normalize
    c.pyapi.decref(mixp__sooc)
    c.pyapi.decref(klg__qhs)
    yicfx__npows = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(nmf__gxozd._getvalue(), is_error=yicfx__npows)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        nmf__gxozd = cgutils.create_struct_proxy(typ)(context, builder)
        nmf__gxozd.n = args[0]
        nmf__gxozd.normalize = args[1]
        return nmf__gxozd._getvalue()
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
        jnq__yoa = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, jnq__yoa)


@box(MonthEndType)
def box_month_end(typ, val, c):
    fshm__rjb = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    mixp__sooc = c.pyapi.long_from_longlong(fshm__rjb.n)
    klg__qhs = c.pyapi.from_native_value(types.boolean, fshm__rjb.normalize,
        c.env_manager)
    reyp__edf = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    fzo__ftu = c.pyapi.call_function_objargs(reyp__edf, (mixp__sooc, klg__qhs))
    c.pyapi.decref(mixp__sooc)
    c.pyapi.decref(klg__qhs)
    c.pyapi.decref(reyp__edf)
    return fzo__ftu


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    mixp__sooc = c.pyapi.object_getattr_string(val, 'n')
    klg__qhs = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(mixp__sooc)
    normalize = c.pyapi.to_native_value(types.bool_, klg__qhs).value
    fshm__rjb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    fshm__rjb.n = n
    fshm__rjb.normalize = normalize
    c.pyapi.decref(mixp__sooc)
    c.pyapi.decref(klg__qhs)
    yicfx__npows = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(fshm__rjb._getvalue(), is_error=yicfx__npows)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        fshm__rjb = cgutils.create_struct_proxy(typ)(context, builder)
        fshm__rjb.n = args[0]
        fshm__rjb.normalize = args[1]
        return fshm__rjb._getvalue()
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
        fshm__rjb = get_days_in_month(year, month)
        if fshm__rjb > day:
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
        jnq__yoa = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, jnq__yoa)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    hoqza__rejy = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    tduoi__jkjp = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for rbm__ggd, ipyx__smi in enumerate(date_offset_fields):
        c.builder.store(getattr(hoqza__rejy, ipyx__smi), c.builder.inttoptr
            (c.builder.add(c.builder.ptrtoint(tduoi__jkjp, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * rbm__ggd)), lir.IntType(64).
            as_pointer()))
    pfdcd__phwsk = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    nsji__vcycj = cgutils.get_or_insert_function(c.builder.module,
        pfdcd__phwsk, name='box_date_offset')
    ourp__flxj = c.builder.call(nsji__vcycj, [hoqza__rejy.n, hoqza__rejy.
        normalize, tduoi__jkjp, hoqza__rejy.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return ourp__flxj


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    mixp__sooc = c.pyapi.object_getattr_string(val, 'n')
    klg__qhs = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(mixp__sooc)
    normalize = c.pyapi.to_native_value(types.bool_, klg__qhs).value
    tduoi__jkjp = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    pfdcd__phwsk = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer()])
    nbcn__jnp = cgutils.get_or_insert_function(c.builder.module,
        pfdcd__phwsk, name='unbox_date_offset')
    has_kws = c.builder.call(nbcn__jnp, [val, tduoi__jkjp])
    hoqza__rejy = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hoqza__rejy.n = n
    hoqza__rejy.normalize = normalize
    for rbm__ggd, ipyx__smi in enumerate(date_offset_fields):
        setattr(hoqza__rejy, ipyx__smi, c.builder.load(c.builder.inttoptr(c
            .builder.add(c.builder.ptrtoint(tduoi__jkjp, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * rbm__ggd)), lir.IntType(64).
            as_pointer())))
    hoqza__rejy.has_kws = has_kws
    c.pyapi.decref(mixp__sooc)
    c.pyapi.decref(klg__qhs)
    yicfx__npows = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(hoqza__rejy._getvalue(), is_error=yicfx__npows)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    tpfm__kvsmh = [n, normalize]
    has_kws = False
    eve__smj = [0] * 9 + [-1] * 9
    for rbm__ggd, ipyx__smi in enumerate(date_offset_fields):
        if hasattr(pyval, ipyx__smi):
            wyc__ipol = context.get_constant(types.int64, getattr(pyval,
                ipyx__smi))
            has_kws = True
        else:
            wyc__ipol = context.get_constant(types.int64, eve__smj[rbm__ggd])
        tpfm__kvsmh.append(wyc__ipol)
    has_kws = context.get_constant(types.boolean, has_kws)
    tpfm__kvsmh.append(has_kws)
    return lir.Constant.literal_struct(tpfm__kvsmh)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    jsau__sizn = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for ount__ots in jsau__sizn:
        if not is_overload_none(ount__ots):
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
        hoqza__rejy = cgutils.create_struct_proxy(typ)(context, builder)
        hoqza__rejy.n = args[0]
        hoqza__rejy.normalize = args[1]
        hoqza__rejy.years = args[2]
        hoqza__rejy.months = args[3]
        hoqza__rejy.weeks = args[4]
        hoqza__rejy.days = args[5]
        hoqza__rejy.hours = args[6]
        hoqza__rejy.minutes = args[7]
        hoqza__rejy.seconds = args[8]
        hoqza__rejy.microseconds = args[9]
        hoqza__rejy.nanoseconds = args[10]
        hoqza__rejy.year = args[11]
        hoqza__rejy.month = args[12]
        hoqza__rejy.day = args[13]
        hoqza__rejy.weekday = args[14]
        hoqza__rejy.hour = args[15]
        hoqza__rejy.minute = args[16]
        hoqza__rejy.second = args[17]
        hoqza__rejy.microsecond = args[18]
        hoqza__rejy.nanosecond = args[19]
        hoqza__rejy.has_kws = args[20]
        return hoqza__rejy._getvalue()
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
        ffdb__hvxh = -1 if dateoffset.n < 0 else 1
        for ugo__annrp in range(np.abs(dateoffset.n)):
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
            year += ffdb__hvxh * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += ffdb__hvxh * dateoffset._months
            year, month, vgbym__uztmw = calculate_month_end_date(year,
                month, day, 0)
            if day > vgbym__uztmw:
                day = vgbym__uztmw
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
            oyz__xuqu = pd.Timedelta(days=dateoffset._days + 7 * dateoffset
                ._weeks, hours=dateoffset._hours, minutes=dateoffset.
                _minutes, seconds=dateoffset._seconds, microseconds=
                dateoffset._microseconds)
            oyz__xuqu = oyz__xuqu + pd.Timedelta(dateoffset._nanoseconds,
                unit='ns')
            if ffdb__hvxh == -1:
                oyz__xuqu = -oyz__xuqu
            ts = ts + oyz__xuqu
            if dateoffset._weekday != -1:
                zemae__nhh = ts.weekday()
                jzs__hnqe = (dateoffset._weekday - zemae__nhh) % 7
                ts = ts + pd.Timedelta(days=jzs__hnqe)
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
        jnq__yoa = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, jnq__yoa)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        jvlmf__wzt = -1 if weekday is None else weekday
        return init_week(n, normalize, jvlmf__wzt)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        lxp__jcpbv = cgutils.create_struct_proxy(typ)(context, builder)
        lxp__jcpbv.n = args[0]
        lxp__jcpbv.normalize = args[1]
        lxp__jcpbv.weekday = args[2]
        return lxp__jcpbv._getvalue()
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
    lxp__jcpbv = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    mixp__sooc = c.pyapi.long_from_longlong(lxp__jcpbv.n)
    klg__qhs = c.pyapi.from_native_value(types.boolean, lxp__jcpbv.
        normalize, c.env_manager)
    vggay__jwb = c.pyapi.long_from_longlong(lxp__jcpbv.weekday)
    vcs__tun = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    ojaw__susil = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64),
        -1), lxp__jcpbv.weekday)
    with c.builder.if_else(ojaw__susil) as (xbfo__vnt, jow__qoevq):
        with xbfo__vnt:
            qpvse__lmjyp = c.pyapi.call_function_objargs(vcs__tun, (
                mixp__sooc, klg__qhs, vggay__jwb))
            ats__ejk = c.builder.block
        with jow__qoevq:
            osdl__euawf = c.pyapi.call_function_objargs(vcs__tun, (
                mixp__sooc, klg__qhs))
            ihymz__moqm = c.builder.block
    fzo__ftu = c.builder.phi(qpvse__lmjyp.type)
    fzo__ftu.add_incoming(qpvse__lmjyp, ats__ejk)
    fzo__ftu.add_incoming(osdl__euawf, ihymz__moqm)
    c.pyapi.decref(vggay__jwb)
    c.pyapi.decref(mixp__sooc)
    c.pyapi.decref(klg__qhs)
    c.pyapi.decref(vcs__tun)
    return fzo__ftu


@unbox(WeekType)
def unbox_week(typ, val, c):
    mixp__sooc = c.pyapi.object_getattr_string(val, 'n')
    klg__qhs = c.pyapi.object_getattr_string(val, 'normalize')
    vggay__jwb = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(mixp__sooc)
    normalize = c.pyapi.to_native_value(types.bool_, klg__qhs).value
    cct__eilyk = c.pyapi.make_none()
    qxenk__hzti = c.builder.icmp_unsigned('==', vggay__jwb, cct__eilyk)
    with c.builder.if_else(qxenk__hzti) as (jow__qoevq, xbfo__vnt):
        with xbfo__vnt:
            qpvse__lmjyp = c.pyapi.long_as_longlong(vggay__jwb)
            ats__ejk = c.builder.block
        with jow__qoevq:
            osdl__euawf = lir.Constant(lir.IntType(64), -1)
            ihymz__moqm = c.builder.block
    fzo__ftu = c.builder.phi(qpvse__lmjyp.type)
    fzo__ftu.add_incoming(qpvse__lmjyp, ats__ejk)
    fzo__ftu.add_incoming(osdl__euawf, ihymz__moqm)
    lxp__jcpbv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    lxp__jcpbv.n = n
    lxp__jcpbv.normalize = normalize
    lxp__jcpbv.weekday = fzo__ftu
    c.pyapi.decref(mixp__sooc)
    c.pyapi.decref(klg__qhs)
    c.pyapi.decref(vggay__jwb)
    yicfx__npows = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(lxp__jcpbv._getvalue(), is_error=yicfx__npows)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            uda__cxsr = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                ahf__dkaa = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                ahf__dkaa = rhs
            return ahf__dkaa + uda__cxsr
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            uda__cxsr = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            if lhs.normalize:
                ahf__dkaa = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                ahf__dkaa = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return ahf__dkaa + uda__cxsr
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            uda__cxsr = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday())
            return rhs + uda__cxsr
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
        bsbi__xkjw = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=bsbi__xkjw)


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
    for lect__tchv in date_offset_unsupported_attrs:
        bbg__qvmoh = 'pandas.tseries.offsets.DateOffset.' + lect__tchv
        overload_attribute(DateOffsetType, lect__tchv)(
            create_unsupported_overload(bbg__qvmoh))
    for lect__tchv in date_offset_unsupported:
        bbg__qvmoh = 'pandas.tseries.offsets.DateOffset.' + lect__tchv
        overload_method(DateOffsetType, lect__tchv)(create_unsupported_overload
            (bbg__qvmoh))


def _install_month_begin_unsupported():
    for lect__tchv in month_begin_unsupported_attrs:
        bbg__qvmoh = 'pandas.tseries.offsets.MonthBegin.' + lect__tchv
        overload_attribute(MonthBeginType, lect__tchv)(
            create_unsupported_overload(bbg__qvmoh))
    for lect__tchv in month_begin_unsupported:
        bbg__qvmoh = 'pandas.tseries.offsets.MonthBegin.' + lect__tchv
        overload_method(MonthBeginType, lect__tchv)(create_unsupported_overload
            (bbg__qvmoh))


def _install_month_end_unsupported():
    for lect__tchv in date_offset_unsupported_attrs:
        bbg__qvmoh = 'pandas.tseries.offsets.MonthEnd.' + lect__tchv
        overload_attribute(MonthEndType, lect__tchv)(
            create_unsupported_overload(bbg__qvmoh))
    for lect__tchv in date_offset_unsupported:
        bbg__qvmoh = 'pandas.tseries.offsets.MonthEnd.' + lect__tchv
        overload_method(MonthEndType, lect__tchv)(create_unsupported_overload
            (bbg__qvmoh))


def _install_week_unsupported():
    for lect__tchv in week_unsupported_attrs:
        bbg__qvmoh = 'pandas.tseries.offsets.Week.' + lect__tchv
        overload_attribute(WeekType, lect__tchv)(create_unsupported_overload
            (bbg__qvmoh))
    for lect__tchv in week_unsupported:
        bbg__qvmoh = 'pandas.tseries.offsets.Week.' + lect__tchv
        overload_method(WeekType, lect__tchv)(create_unsupported_overload(
            bbg__qvmoh))


def _install_offsets_unsupported():
    for wyc__ipol in offsets_unsupported:
        bbg__qvmoh = 'pandas.tseries.offsets.' + wyc__ipol.__name__
        overload(wyc__ipol)(create_unsupported_overload(bbg__qvmoh))


def _install_frequencies_unsupported():
    for wyc__ipol in frequencies_unsupported:
        bbg__qvmoh = 'pandas.tseries.frequencies.' + wyc__ipol.__name__
        overload(wyc__ipol)(create_unsupported_overload(bbg__qvmoh))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
