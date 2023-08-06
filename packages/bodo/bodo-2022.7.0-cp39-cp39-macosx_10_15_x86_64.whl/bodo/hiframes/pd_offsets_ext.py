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
        fpzm__znqfh = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthBeginModel, self).__init__(dmm, fe_type, fpzm__znqfh)


@box(MonthBeginType)
def box_month_begin(typ, val, c):
    jxx__qrlvk = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    iwfw__juexo = c.pyapi.long_from_longlong(jxx__qrlvk.n)
    ejihm__dwf = c.pyapi.from_native_value(types.boolean, jxx__qrlvk.
        normalize, c.env_manager)
    vwd__oyy = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthBegin))
    ury__qsxdd = c.pyapi.call_function_objargs(vwd__oyy, (iwfw__juexo,
        ejihm__dwf))
    c.pyapi.decref(iwfw__juexo)
    c.pyapi.decref(ejihm__dwf)
    c.pyapi.decref(vwd__oyy)
    return ury__qsxdd


@unbox(MonthBeginType)
def unbox_month_begin(typ, val, c):
    iwfw__juexo = c.pyapi.object_getattr_string(val, 'n')
    ejihm__dwf = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(iwfw__juexo)
    normalize = c.pyapi.to_native_value(types.bool_, ejihm__dwf).value
    jxx__qrlvk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jxx__qrlvk.n = n
    jxx__qrlvk.normalize = normalize
    c.pyapi.decref(iwfw__juexo)
    c.pyapi.decref(ejihm__dwf)
    ecf__dkq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jxx__qrlvk._getvalue(), is_error=ecf__dkq)


@overload(pd.tseries.offsets.MonthBegin, no_unliteral=True)
def MonthBegin(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_begin(n, normalize)
    return impl


@intrinsic
def init_month_begin(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        jxx__qrlvk = cgutils.create_struct_proxy(typ)(context, builder)
        jxx__qrlvk.n = args[0]
        jxx__qrlvk.normalize = args[1]
        return jxx__qrlvk._getvalue()
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
        fpzm__znqfh = [('n', types.int64), ('normalize', types.boolean)]
        super(MonthEndModel, self).__init__(dmm, fe_type, fpzm__znqfh)


@box(MonthEndType)
def box_month_end(typ, val, c):
    sntig__txy = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    iwfw__juexo = c.pyapi.long_from_longlong(sntig__txy.n)
    ejihm__dwf = c.pyapi.from_native_value(types.boolean, sntig__txy.
        normalize, c.env_manager)
    ytwpa__jous = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.MonthEnd))
    ury__qsxdd = c.pyapi.call_function_objargs(ytwpa__jous, (iwfw__juexo,
        ejihm__dwf))
    c.pyapi.decref(iwfw__juexo)
    c.pyapi.decref(ejihm__dwf)
    c.pyapi.decref(ytwpa__jous)
    return ury__qsxdd


@unbox(MonthEndType)
def unbox_month_end(typ, val, c):
    iwfw__juexo = c.pyapi.object_getattr_string(val, 'n')
    ejihm__dwf = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(iwfw__juexo)
    normalize = c.pyapi.to_native_value(types.bool_, ejihm__dwf).value
    sntig__txy = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    sntig__txy.n = n
    sntig__txy.normalize = normalize
    c.pyapi.decref(iwfw__juexo)
    c.pyapi.decref(ejihm__dwf)
    ecf__dkq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(sntig__txy._getvalue(), is_error=ecf__dkq)


@overload(pd.tseries.offsets.MonthEnd, no_unliteral=True)
def MonthEnd(n=1, normalize=False):

    def impl(n=1, normalize=False):
        return init_month_end(n, normalize)
    return impl


@intrinsic
def init_month_end(typingctx, n, normalize):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        sntig__txy = cgutils.create_struct_proxy(typ)(context, builder)
        sntig__txy.n = args[0]
        sntig__txy.normalize = args[1]
        return sntig__txy._getvalue()
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
        sntig__txy = get_days_in_month(year, month)
        if sntig__txy > day:
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
        fpzm__znqfh = [('n', types.int64), ('normalize', types.boolean), (
            'years', types.int64), ('months', types.int64), ('weeks', types
            .int64), ('days', types.int64), ('hours', types.int64), (
            'minutes', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64), ('nanoseconds', types.int64), (
            'year', types.int64), ('month', types.int64), ('day', types.
            int64), ('weekday', types.int64), ('hour', types.int64), (
            'minute', types.int64), ('second', types.int64), ('microsecond',
            types.int64), ('nanosecond', types.int64), ('has_kws', types.
            boolean)]
        super(DateOffsetModel, self).__init__(dmm, fe_type, fpzm__znqfh)


@box(DateOffsetType)
def box_date_offset(typ, val, c):
    vszr__cli = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    xxtr__xpinc = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    for qpj__qjut, ffg__lmtq in enumerate(date_offset_fields):
        c.builder.store(getattr(vszr__cli, ffg__lmtq), c.builder.inttoptr(c
            .builder.add(c.builder.ptrtoint(xxtr__xpinc, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * qpj__qjut)), lir.IntType(64).
            as_pointer()))
    vdu__ojtm = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(1), lir.IntType(64).as_pointer(), lir.IntType(1)])
    toy__tess = cgutils.get_or_insert_function(c.builder.module, vdu__ojtm,
        name='box_date_offset')
    kthf__jkj = c.builder.call(toy__tess, [vszr__cli.n, vszr__cli.normalize,
        xxtr__xpinc, vszr__cli.has_kws])
    c.context.nrt.decref(c.builder, typ, val)
    return kthf__jkj


@unbox(DateOffsetType)
def unbox_date_offset(typ, val, c):
    iwfw__juexo = c.pyapi.object_getattr_string(val, 'n')
    ejihm__dwf = c.pyapi.object_getattr_string(val, 'normalize')
    n = c.pyapi.long_as_longlong(iwfw__juexo)
    normalize = c.pyapi.to_native_value(types.bool_, ejihm__dwf).value
    xxtr__xpinc = c.builder.alloca(lir.IntType(64), size=lir.Constant(lir.
        IntType(64), 18))
    vdu__ojtm = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer
        (), lir.IntType(64).as_pointer()])
    frjpg__krso = cgutils.get_or_insert_function(c.builder.module,
        vdu__ojtm, name='unbox_date_offset')
    has_kws = c.builder.call(frjpg__krso, [val, xxtr__xpinc])
    vszr__cli = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    vszr__cli.n = n
    vszr__cli.normalize = normalize
    for qpj__qjut, ffg__lmtq in enumerate(date_offset_fields):
        setattr(vszr__cli, ffg__lmtq, c.builder.load(c.builder.inttoptr(c.
            builder.add(c.builder.ptrtoint(xxtr__xpinc, lir.IntType(64)),
            lir.Constant(lir.IntType(64), 8 * qpj__qjut)), lir.IntType(64).
            as_pointer())))
    vszr__cli.has_kws = has_kws
    c.pyapi.decref(iwfw__juexo)
    c.pyapi.decref(ejihm__dwf)
    ecf__dkq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vszr__cli._getvalue(), is_error=ecf__dkq)


@lower_constant(DateOffsetType)
def lower_constant_date_offset(context, builder, ty, pyval):
    n = context.get_constant(types.int64, pyval.n)
    normalize = context.get_constant(types.boolean, pyval.normalize)
    ouc__zmh = [n, normalize]
    has_kws = False
    lyj__jyo = [0] * 9 + [-1] * 9
    for qpj__qjut, ffg__lmtq in enumerate(date_offset_fields):
        if hasattr(pyval, ffg__lmtq):
            rciev__cuhf = context.get_constant(types.int64, getattr(pyval,
                ffg__lmtq))
            has_kws = True
        else:
            rciev__cuhf = context.get_constant(types.int64, lyj__jyo[qpj__qjut]
                )
        ouc__zmh.append(rciev__cuhf)
    has_kws = context.get_constant(types.boolean, has_kws)
    ouc__zmh.append(has_kws)
    return lir.Constant.literal_struct(ouc__zmh)


@overload(pd.tseries.offsets.DateOffset, no_unliteral=True)
def DateOffset(n=1, normalize=False, years=None, months=None, weeks=None,
    days=None, hours=None, minutes=None, seconds=None, microseconds=None,
    nanoseconds=None, year=None, month=None, day=None, weekday=None, hour=
    None, minute=None, second=None, microsecond=None, nanosecond=None):
    has_kws = False
    chhdj__nvx = [years, months, weeks, days, hours, minutes, seconds,
        microseconds, year, month, day, weekday, hour, minute, second,
        microsecond]
    for pueg__vow in chhdj__nvx:
        if not is_overload_none(pueg__vow):
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
        vszr__cli = cgutils.create_struct_proxy(typ)(context, builder)
        vszr__cli.n = args[0]
        vszr__cli.normalize = args[1]
        vszr__cli.years = args[2]
        vszr__cli.months = args[3]
        vszr__cli.weeks = args[4]
        vszr__cli.days = args[5]
        vszr__cli.hours = args[6]
        vszr__cli.minutes = args[7]
        vszr__cli.seconds = args[8]
        vszr__cli.microseconds = args[9]
        vszr__cli.nanoseconds = args[10]
        vszr__cli.year = args[11]
        vszr__cli.month = args[12]
        vszr__cli.day = args[13]
        vszr__cli.weekday = args[14]
        vszr__cli.hour = args[15]
        vszr__cli.minute = args[16]
        vszr__cli.second = args[17]
        vszr__cli.microsecond = args[18]
        vszr__cli.nanosecond = args[19]
        vszr__cli.has_kws = args[20]
        return vszr__cli._getvalue()
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
        vytq__dfq = -1 if dateoffset.n < 0 else 1
        for tvf__ejl in range(np.abs(dateoffset.n)):
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
            year += vytq__dfq * dateoffset._years
            if dateoffset._month != -1:
                month = dateoffset._month
            month += vytq__dfq * dateoffset._months
            year, month, lltyg__rfjvc = calculate_month_end_date(year,
                month, day, 0)
            if day > lltyg__rfjvc:
                day = lltyg__rfjvc
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
            pngl__vncn = pd.Timedelta(days=dateoffset._days + 7 *
                dateoffset._weeks, hours=dateoffset._hours, minutes=
                dateoffset._minutes, seconds=dateoffset._seconds,
                microseconds=dateoffset._microseconds)
            pngl__vncn = pngl__vncn + pd.Timedelta(dateoffset._nanoseconds,
                unit='ns')
            if vytq__dfq == -1:
                pngl__vncn = -pngl__vncn
            ts = ts + pngl__vncn
            if dateoffset._weekday != -1:
                iawe__iyarj = ts.weekday()
                grmw__lgtl = (dateoffset._weekday - iawe__iyarj) % 7
                ts = ts + pd.Timedelta(days=grmw__lgtl)
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
        fpzm__znqfh = [('n', types.int64), ('normalize', types.boolean), (
            'weekday', types.int64)]
        super(WeekModel, self).__init__(dmm, fe_type, fpzm__znqfh)


make_attribute_wrapper(WeekType, 'n', 'n')
make_attribute_wrapper(WeekType, 'normalize', 'normalize')
make_attribute_wrapper(WeekType, 'weekday', 'weekday')


@overload(pd.tseries.offsets.Week, no_unliteral=True)
def Week(n=1, normalize=False, weekday=None):

    def impl(n=1, normalize=False, weekday=None):
        zibd__fcw = -1 if weekday is None else weekday
        return init_week(n, normalize, zibd__fcw)
    return impl


@intrinsic
def init_week(typingctx, n, normalize, weekday):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        xhh__xrxxw = cgutils.create_struct_proxy(typ)(context, builder)
        xhh__xrxxw.n = args[0]
        xhh__xrxxw.normalize = args[1]
        xhh__xrxxw.weekday = args[2]
        return xhh__xrxxw._getvalue()
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
    xhh__xrxxw = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    iwfw__juexo = c.pyapi.long_from_longlong(xhh__xrxxw.n)
    ejihm__dwf = c.pyapi.from_native_value(types.boolean, xhh__xrxxw.
        normalize, c.env_manager)
    ervjk__pzh = c.pyapi.long_from_longlong(xhh__xrxxw.weekday)
    tcpa__jlop = c.pyapi.unserialize(c.pyapi.serialize_object(pd.tseries.
        offsets.Week))
    wzi__ccaz = c.builder.icmp_signed('!=', lir.Constant(lir.IntType(64), -
        1), xhh__xrxxw.weekday)
    with c.builder.if_else(wzi__ccaz) as (idb__osum, jjrp__rqs):
        with idb__osum:
            dhxgl__hcx = c.pyapi.call_function_objargs(tcpa__jlop, (
                iwfw__juexo, ejihm__dwf, ervjk__pzh))
            srlh__tnezj = c.builder.block
        with jjrp__rqs:
            oep__pru = c.pyapi.call_function_objargs(tcpa__jlop, (
                iwfw__juexo, ejihm__dwf))
            panjt__irvw = c.builder.block
    ury__qsxdd = c.builder.phi(dhxgl__hcx.type)
    ury__qsxdd.add_incoming(dhxgl__hcx, srlh__tnezj)
    ury__qsxdd.add_incoming(oep__pru, panjt__irvw)
    c.pyapi.decref(ervjk__pzh)
    c.pyapi.decref(iwfw__juexo)
    c.pyapi.decref(ejihm__dwf)
    c.pyapi.decref(tcpa__jlop)
    return ury__qsxdd


@unbox(WeekType)
def unbox_week(typ, val, c):
    iwfw__juexo = c.pyapi.object_getattr_string(val, 'n')
    ejihm__dwf = c.pyapi.object_getattr_string(val, 'normalize')
    ervjk__pzh = c.pyapi.object_getattr_string(val, 'weekday')
    n = c.pyapi.long_as_longlong(iwfw__juexo)
    normalize = c.pyapi.to_native_value(types.bool_, ejihm__dwf).value
    votrs__nem = c.pyapi.make_none()
    zlkfk__cvvw = c.builder.icmp_unsigned('==', ervjk__pzh, votrs__nem)
    with c.builder.if_else(zlkfk__cvvw) as (jjrp__rqs, idb__osum):
        with idb__osum:
            dhxgl__hcx = c.pyapi.long_as_longlong(ervjk__pzh)
            srlh__tnezj = c.builder.block
        with jjrp__rqs:
            oep__pru = lir.Constant(lir.IntType(64), -1)
            panjt__irvw = c.builder.block
    ury__qsxdd = c.builder.phi(dhxgl__hcx.type)
    ury__qsxdd.add_incoming(dhxgl__hcx, srlh__tnezj)
    ury__qsxdd.add_incoming(oep__pru, panjt__irvw)
    xhh__xrxxw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    xhh__xrxxw.n = n
    xhh__xrxxw.normalize = normalize
    xhh__xrxxw.weekday = ury__qsxdd
    c.pyapi.decref(iwfw__juexo)
    c.pyapi.decref(ejihm__dwf)
    c.pyapi.decref(ervjk__pzh)
    ecf__dkq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xhh__xrxxw._getvalue(), is_error=ecf__dkq)


def overload_add_operator_week_offset_type(lhs, rhs):
    if lhs == week_type and rhs == pd_timestamp_type:

        def impl(lhs, rhs):
            hagib__bams = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            if lhs.normalize:
                wnr__wddd = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                wnr__wddd = rhs
            return wnr__wddd + hagib__bams
        return impl
    if lhs == week_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            hagib__bams = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            if lhs.normalize:
                wnr__wddd = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day)
            else:
                wnr__wddd = pd.Timestamp(year=rhs.year, month=rhs.month,
                    day=rhs.day, hour=rhs.hour, minute=rhs.minute, second=
                    rhs.second, microsecond=rhs.microsecond)
            return wnr__wddd + hagib__bams
        return impl
    if lhs == week_type and rhs == datetime_date_type:

        def impl(lhs, rhs):
            hagib__bams = calculate_week_date(lhs.n, lhs.weekday, rhs.weekday()
                )
            return rhs + hagib__bams
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
        rupj__ymy = (weekday - other_weekday) % 7
        if n > 0:
            n = n - 1
    return pd.Timedelta(weeks=n, days=rupj__ymy)


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
    for rxkq__pnkm in date_offset_unsupported_attrs:
        qdtmv__fkn = 'pandas.tseries.offsets.DateOffset.' + rxkq__pnkm
        overload_attribute(DateOffsetType, rxkq__pnkm)(
            create_unsupported_overload(qdtmv__fkn))
    for rxkq__pnkm in date_offset_unsupported:
        qdtmv__fkn = 'pandas.tseries.offsets.DateOffset.' + rxkq__pnkm
        overload_method(DateOffsetType, rxkq__pnkm)(create_unsupported_overload
            (qdtmv__fkn))


def _install_month_begin_unsupported():
    for rxkq__pnkm in month_begin_unsupported_attrs:
        qdtmv__fkn = 'pandas.tseries.offsets.MonthBegin.' + rxkq__pnkm
        overload_attribute(MonthBeginType, rxkq__pnkm)(
            create_unsupported_overload(qdtmv__fkn))
    for rxkq__pnkm in month_begin_unsupported:
        qdtmv__fkn = 'pandas.tseries.offsets.MonthBegin.' + rxkq__pnkm
        overload_method(MonthBeginType, rxkq__pnkm)(create_unsupported_overload
            (qdtmv__fkn))


def _install_month_end_unsupported():
    for rxkq__pnkm in date_offset_unsupported_attrs:
        qdtmv__fkn = 'pandas.tseries.offsets.MonthEnd.' + rxkq__pnkm
        overload_attribute(MonthEndType, rxkq__pnkm)(
            create_unsupported_overload(qdtmv__fkn))
    for rxkq__pnkm in date_offset_unsupported:
        qdtmv__fkn = 'pandas.tseries.offsets.MonthEnd.' + rxkq__pnkm
        overload_method(MonthEndType, rxkq__pnkm)(create_unsupported_overload
            (qdtmv__fkn))


def _install_week_unsupported():
    for rxkq__pnkm in week_unsupported_attrs:
        qdtmv__fkn = 'pandas.tseries.offsets.Week.' + rxkq__pnkm
        overload_attribute(WeekType, rxkq__pnkm)(create_unsupported_overload
            (qdtmv__fkn))
    for rxkq__pnkm in week_unsupported:
        qdtmv__fkn = 'pandas.tseries.offsets.Week.' + rxkq__pnkm
        overload_method(WeekType, rxkq__pnkm)(create_unsupported_overload(
            qdtmv__fkn))


def _install_offsets_unsupported():
    for rciev__cuhf in offsets_unsupported:
        qdtmv__fkn = 'pandas.tseries.offsets.' + rciev__cuhf.__name__
        overload(rciev__cuhf)(create_unsupported_overload(qdtmv__fkn))


def _install_frequencies_unsupported():
    for rciev__cuhf in frequencies_unsupported:
        qdtmv__fkn = 'pandas.tseries.frequencies.' + rciev__cuhf.__name__
        overload(rciev__cuhf)(create_unsupported_overload(qdtmv__fkn))


_install_date_offsets_unsupported()
_install_month_begin_unsupported()
_install_month_end_unsupported()
_install_week_unsupported()
_install_offsets_unsupported()
_install_frequencies_unsupported()
