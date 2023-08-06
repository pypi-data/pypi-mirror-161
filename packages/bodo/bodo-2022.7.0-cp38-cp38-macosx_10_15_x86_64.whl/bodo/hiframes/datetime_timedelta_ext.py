"""Numba extension support for datetime.timedelta objects and their arrays.
"""
import datetime
import operator
from collections import namedtuple
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.libs import hdatetime_ext
from bodo.utils.indexing import get_new_null_mask_bool_index, get_new_null_mask_int_index, get_new_null_mask_slice_index, setitem_slice_index_null_bits
from bodo.utils.typing import BodoError, get_overload_const_str, is_iterable_type, is_list_like_index_type, is_overload_constant_str
ll.add_symbol('box_datetime_timedelta_array', hdatetime_ext.
    box_datetime_timedelta_array)
ll.add_symbol('unbox_datetime_timedelta_array', hdatetime_ext.
    unbox_datetime_timedelta_array)


class NoInput:
    pass


_no_input = NoInput()


class NoInputType(types.Type):

    def __init__(self):
        super(NoInputType, self).__init__(name='NoInput')


register_model(NoInputType)(models.OpaqueModel)


@typeof_impl.register(NoInput)
def _typ_no_input(val, c):
    return NoInputType()


@lower_constant(NoInputType)
def constant_no_input(context, builder, ty, pyval):
    return context.get_dummy_value()


class PDTimeDeltaType(types.Type):

    def __init__(self):
        super(PDTimeDeltaType, self).__init__(name='PDTimeDeltaType()')


pd_timedelta_type = PDTimeDeltaType()
types.pd_timedelta_type = pd_timedelta_type


@typeof_impl.register(pd.Timedelta)
def typeof_pd_timedelta(val, c):
    return pd_timedelta_type


@register_model(PDTimeDeltaType)
class PDTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mdnym__yhf = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, mdnym__yhf)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    ydli__uefsb = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    nvxha__tnbh = c.pyapi.long_from_longlong(ydli__uefsb.value)
    numcm__tft = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(numcm__tft, (nvxha__tnbh,))
    c.pyapi.decref(nvxha__tnbh)
    c.pyapi.decref(numcm__tft)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    nvxha__tnbh = c.pyapi.object_getattr_string(val, 'value')
    jhwy__fizji = c.pyapi.long_as_longlong(nvxha__tnbh)
    ydli__uefsb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ydli__uefsb.value = jhwy__fizji
    c.pyapi.decref(nvxha__tnbh)
    crtq__iqstk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ydli__uefsb._getvalue(), is_error=crtq__iqstk)


@lower_constant(PDTimeDeltaType)
def lower_constant_pd_timedelta(context, builder, ty, pyval):
    value = context.get_constant(types.int64, pyval.value)
    return lir.Constant.literal_struct([value])


@overload(pd.Timedelta, no_unliteral=True)
def pd_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
    microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    if value == _no_input:

        def impl_timedelta_kw(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            days += weeks * 7
            hours += days * 24
            minutes += 60 * hours
            seconds += 60 * minutes
            milliseconds += 1000 * seconds
            microseconds += 1000 * milliseconds
            eigs__bwf = 1000 * microseconds
            return init_pd_timedelta(eigs__bwf)
        return impl_timedelta_kw
    if value == bodo.string_type or is_overload_constant_str(value):

        def impl_str(value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
            with numba.objmode(res='pd_timedelta_type'):
                res = pd.Timedelta(value)
            return res
        return impl_str
    if value == pd_timedelta_type:
        return (lambda value=_no_input, unit='ns', days=0, seconds=0,
            microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0: value)
    if value == datetime_timedelta_type:

        def impl_timedelta_datetime(value=_no_input, unit='ns', days=0,
            seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0,
            weeks=0):
            days = value.days
            seconds = 60 * 60 * 24 * days + value.seconds
            microseconds = 1000 * 1000 * seconds + value.microseconds
            eigs__bwf = 1000 * microseconds
            return init_pd_timedelta(eigs__bwf)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    stj__jdwc, vber__cms = pd._libs.tslibs.conversion.precision_from_unit(unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * stj__jdwc)
    return impl_timedelta


@intrinsic
def init_pd_timedelta(typingctx, value):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.value = args[0]
        return timedelta._getvalue()
    return PDTimeDeltaType()(value), codegen


make_attribute_wrapper(PDTimeDeltaType, 'value', '_value')


@overload_attribute(PDTimeDeltaType, 'value')
@overload_attribute(PDTimeDeltaType, 'delta')
def pd_timedelta_get_value(td):

    def impl(td):
        return td._value
    return impl


@overload_attribute(PDTimeDeltaType, 'days')
def pd_timedelta_get_days(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000 * 60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'seconds')
def pd_timedelta_get_seconds(td):

    def impl(td):
        return td._value // (1000 * 1000 * 1000) % (60 * 60 * 24)
    return impl


@overload_attribute(PDTimeDeltaType, 'microseconds')
def pd_timedelta_get_microseconds(td):

    def impl(td):
        return td._value // 1000 % 1000000
    return impl


@overload_attribute(PDTimeDeltaType, 'nanoseconds')
def pd_timedelta_get_nanoseconds(td):

    def impl(td):
        return td._value % 1000
    return impl


@register_jitable
def _to_hours_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60 * 60) % 24


@register_jitable
def _to_minutes_pd_td(td):
    return td._value // (1000 * 1000 * 1000 * 60) % 60


@register_jitable
def _to_seconds_pd_td(td):
    return td._value // (1000 * 1000 * 1000) % 60


@register_jitable
def _to_milliseconds_pd_td(td):
    return td._value // (1000 * 1000) % 1000


@register_jitable
def _to_microseconds_pd_td(td):
    return td._value // 1000 % 1000


Components = namedtuple('Components', ['days', 'hours', 'minutes',
    'seconds', 'milliseconds', 'microseconds', 'nanoseconds'], defaults=[0,
    0, 0, 0, 0, 0, 0])


@overload_attribute(PDTimeDeltaType, 'components', no_unliteral=True)
def pd_timedelta_get_components(td):

    def impl(td):
        a = Components(td.days, _to_hours_pd_td(td), _to_minutes_pd_td(td),
            _to_seconds_pd_td(td), _to_milliseconds_pd_td(td),
            _to_microseconds_pd_td(td), td.nanoseconds)
        return a
    return impl


@overload_method(PDTimeDeltaType, '__hash__', no_unliteral=True)
def pd_td___hash__(td):

    def impl(td):
        return hash(td._value)
    return impl


@overload_method(PDTimeDeltaType, 'to_numpy', no_unliteral=True)
@overload_method(PDTimeDeltaType, 'to_timedelta64', no_unliteral=True)
def pd_td_to_numpy(td):
    from bodo.hiframes.pd_timestamp_ext import integer_to_timedelta64

    def impl(td):
        return integer_to_timedelta64(td.value)
    return impl


@overload_method(PDTimeDeltaType, 'to_pytimedelta', no_unliteral=True)
def pd_td_to_pytimedelta(td):

    def impl(td):
        return datetime.timedelta(microseconds=np.int64(td._value / 1000))
    return impl


@overload_method(PDTimeDeltaType, 'total_seconds', no_unliteral=True)
def pd_td_total_seconds(td):

    def impl(td):
        return td._value // 1000 / 10 ** 6
    return impl


def overload_add_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            val = lhs.value + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            kipkx__iuxsy = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + kipkx__iuxsy
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            efy__ycq = (lhs.microseconds + (lhs.seconds + lhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = efy__ycq + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            oon__bkw = rhs.toordinal()
            udynn__bck = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            vvgsy__wujj = rhs.microsecond
            ufka__chm = lhs.value // 1000
            syd__xjf = lhs.nanoseconds
            nod__jplm = vvgsy__wujj + ufka__chm
            yrfy__wven = 1000000 * (oon__bkw * 86400 + udynn__bck) + nod__jplm
            xyw__pbgh = syd__xjf
            return compute_pd_timestamp(yrfy__wven, xyw__pbgh)
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + rhs.to_pytimedelta()
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days + rhs.days
            s = lhs.seconds + rhs.seconds
            us = lhs.microseconds + rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_datetime_type:

        def impl(lhs, rhs):
            uhbw__awv = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            uhbw__awv = uhbw__awv + lhs
            jfvj__mjnxk, xfw__lbckd = divmod(uhbw__awv.seconds, 3600)
            ewra__vyp, jmjo__tgnsl = divmod(xfw__lbckd, 60)
            if 0 < uhbw__awv.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(uhbw__awv
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    jfvj__mjnxk, ewra__vyp, jmjo__tgnsl, uhbw__awv.microseconds
                    )
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            uhbw__awv = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            uhbw__awv = uhbw__awv + rhs
            jfvj__mjnxk, xfw__lbckd = divmod(uhbw__awv.seconds, 3600)
            ewra__vyp, jmjo__tgnsl = divmod(xfw__lbckd, 60)
            if 0 < uhbw__awv.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(uhbw__awv
                    .days)
                return datetime.datetime(d.year, d.month, d.day,
                    jfvj__mjnxk, ewra__vyp, jmjo__tgnsl, uhbw__awv.microseconds
                    )
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            yflc__skk = lhs.value - rhs.value
            return pd.Timedelta(yflc__skk)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_datetime_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs.days - rhs.days
            s = lhs.seconds - rhs.seconds
            us = lhs.microseconds - rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            return lhs + -rhs
        return impl
    if lhs == datetime_timedelta_array_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            qlkg__jfl = lhs
            numba.parfors.parfor.init_prange()
            n = len(qlkg__jfl)
            A = alloc_datetime_timedelta_array(n)
            for hfvei__pzi in numba.parfors.parfor.internal_prange(n):
                A[hfvei__pzi] = qlkg__jfl[hfvei__pzi] - rhs
            return A
        return impl


def overload_mul_operator_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value * rhs)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(rhs.value * lhs)
        return impl
    if lhs == datetime_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            d = lhs.days * rhs
            s = lhs.seconds * rhs
            us = lhs.microseconds * rhs
            return datetime.timedelta(d, s, us)
        return impl
    elif isinstance(lhs, types.Integer) and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            d = lhs * rhs.days
            s = lhs * rhs.seconds
            us = lhs * rhs.microseconds
            return datetime.timedelta(d, s, us)
        return impl


def overload_floordiv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value // rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value // rhs)
        return impl


def overload_truediv_operator_pd_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return lhs.value / rhs.value
        return impl
    elif lhs == pd_timedelta_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            return pd.Timedelta(int(lhs.value / rhs))
        return impl


def overload_mod_operator_timedeltas(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            return pd.Timedelta(lhs.value % rhs.value)
        return impl
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            bsne__ugud = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, bsne__ugud)
        return impl


def pd_create_cmp_op_overload(op):

    def overload_pd_timedelta_cmp(lhs, rhs):
        if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

            def impl(lhs, rhs):
                return op(lhs.value, rhs.value)
            return impl
        if lhs == pd_timedelta_type and rhs == bodo.timedelta64ns:
            return lambda lhs, rhs: op(bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(lhs.value), rhs)
        if lhs == bodo.timedelta64ns and rhs == pd_timedelta_type:
            return lambda lhs, rhs: op(lhs, bodo.hiframes.pd_timestamp_ext.
                integer_to_timedelta64(rhs.value))
    return overload_pd_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def pd_timedelta_neg(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return pd.Timedelta(-lhs.value)
        return impl


@overload(operator.pos, no_unliteral=True)
def pd_timedelta_pos(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def pd_timedelta_divmod(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            scfdq__xpg, bsne__ugud = divmod(lhs.value, rhs.value)
            return scfdq__xpg, pd.Timedelta(bsne__ugud)
        return impl


@overload(abs, no_unliteral=True)
def pd_timedelta_abs(lhs):
    if lhs == pd_timedelta_type:

        def impl(lhs):
            if lhs.value < 0:
                return -lhs
            else:
                return lhs
        return impl


class DatetimeTimeDeltaType(types.Type):

    def __init__(self):
        super(DatetimeTimeDeltaType, self).__init__(name=
            'DatetimeTimeDeltaType()')


datetime_timedelta_type = DatetimeTimeDeltaType()


@typeof_impl.register(datetime.timedelta)
def typeof_datetime_timedelta(val, c):
    return datetime_timedelta_type


@register_model(DatetimeTimeDeltaType)
class DatetimeTimeDeltaModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mdnym__yhf = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, mdnym__yhf)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    ydli__uefsb = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    nlf__feag = c.pyapi.long_from_longlong(ydli__uefsb.days)
    gylf__fmp = c.pyapi.long_from_longlong(ydli__uefsb.seconds)
    jiuyq__zmjqp = c.pyapi.long_from_longlong(ydli__uefsb.microseconds)
    numcm__tft = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(numcm__tft, (nlf__feag, gylf__fmp,
        jiuyq__zmjqp))
    c.pyapi.decref(nlf__feag)
    c.pyapi.decref(gylf__fmp)
    c.pyapi.decref(jiuyq__zmjqp)
    c.pyapi.decref(numcm__tft)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    nlf__feag = c.pyapi.object_getattr_string(val, 'days')
    gylf__fmp = c.pyapi.object_getattr_string(val, 'seconds')
    jiuyq__zmjqp = c.pyapi.object_getattr_string(val, 'microseconds')
    eogmq__mcd = c.pyapi.long_as_longlong(nlf__feag)
    tumug__aun = c.pyapi.long_as_longlong(gylf__fmp)
    jijd__sqiw = c.pyapi.long_as_longlong(jiuyq__zmjqp)
    ydli__uefsb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ydli__uefsb.days = eogmq__mcd
    ydli__uefsb.seconds = tumug__aun
    ydli__uefsb.microseconds = jijd__sqiw
    c.pyapi.decref(nlf__feag)
    c.pyapi.decref(gylf__fmp)
    c.pyapi.decref(jiuyq__zmjqp)
    crtq__iqstk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ydli__uefsb._getvalue(), is_error=crtq__iqstk)


@lower_constant(DatetimeTimeDeltaType)
def lower_constant_datetime_timedelta(context, builder, ty, pyval):
    days = context.get_constant(types.int64, pyval.days)
    seconds = context.get_constant(types.int64, pyval.seconds)
    microseconds = context.get_constant(types.int64, pyval.microseconds)
    return lir.Constant.literal_struct([days, seconds, microseconds])


@overload(datetime.timedelta, no_unliteral=True)
def datetime_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
    minutes=0, hours=0, weeks=0):

    def impl_timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
        minutes=0, hours=0, weeks=0):
        d = s = us = 0
        days += weeks * 7
        seconds += minutes * 60 + hours * 3600
        microseconds += milliseconds * 1000
        d = days
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += int(seconds)
        seconds, us = divmod(microseconds, 1000000)
        days, seconds = divmod(seconds, 24 * 3600)
        d += days
        s += seconds
        return init_timedelta(d, s, us)
    return impl_timedelta


@intrinsic
def init_timedelta(typingctx, d, s, us):

    def codegen(context, builder, signature, args):
        typ = signature.return_type
        timedelta = cgutils.create_struct_proxy(typ)(context, builder)
        timedelta.days = args[0]
        timedelta.seconds = args[1]
        timedelta.microseconds = args[2]
        return timedelta._getvalue()
    return DatetimeTimeDeltaType()(d, s, us), codegen


make_attribute_wrapper(DatetimeTimeDeltaType, 'days', '_days')
make_attribute_wrapper(DatetimeTimeDeltaType, 'seconds', '_seconds')
make_attribute_wrapper(DatetimeTimeDeltaType, 'microseconds', '_microseconds')


@overload_attribute(DatetimeTimeDeltaType, 'days')
def timedelta_get_days(td):

    def impl(td):
        return td._days
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'seconds')
def timedelta_get_seconds(td):

    def impl(td):
        return td._seconds
    return impl


@overload_attribute(DatetimeTimeDeltaType, 'microseconds')
def timedelta_get_microseconds(td):

    def impl(td):
        return td._microseconds
    return impl


@overload_method(DatetimeTimeDeltaType, 'total_seconds', no_unliteral=True)
def total_seconds(td):

    def impl(td):
        return ((td._days * 86400 + td._seconds) * 10 ** 6 + td._microseconds
            ) / 10 ** 6
    return impl


@overload_method(DatetimeTimeDeltaType, '__hash__', no_unliteral=True)
def __hash__(td):

    def impl(td):
        return hash((td._days, td._seconds, td._microseconds))
    return impl


@register_jitable
def _to_nanoseconds(td):
    return np.int64(((td._days * 86400 + td._seconds) * 1000000 + td.
        _microseconds) * 1000)


@register_jitable
def _to_microseconds(td):
    return (td._days * (24 * 3600) + td._seconds) * 1000000 + td._microseconds


@register_jitable
def _cmp(x, y):
    return 0 if x == y else 1 if x > y else -1


@register_jitable
def _getstate(td):
    return td._days, td._seconds, td._microseconds


@register_jitable
def _divide_and_round(a, b):
    scfdq__xpg, bsne__ugud = divmod(a, b)
    bsne__ugud *= 2
    ufas__cie = bsne__ugud > b if b > 0 else bsne__ugud < b
    if ufas__cie or bsne__ugud == b and scfdq__xpg % 2 == 1:
        scfdq__xpg += 1
    return scfdq__xpg


_MAXORDINAL = 3652059


def overload_floordiv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us // _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, us // rhs)
        return impl


def overload_truediv_operator_dt_timedelta(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return us / _to_microseconds(rhs)
        return impl
    elif lhs == datetime_timedelta_type and rhs == types.int64:

        def impl(lhs, rhs):
            us = _to_microseconds(lhs)
            return datetime.timedelta(0, 0, _divide_and_round(us, rhs))
        return impl


def create_cmp_op_overload(op):

    def overload_timedelta_cmp(lhs, rhs):
        if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

            def impl(lhs, rhs):
                krb__qxxw = _cmp(_getstate(lhs), _getstate(rhs))
                return op(krb__qxxw, 0)
            return impl
    return overload_timedelta_cmp


@overload(operator.neg, no_unliteral=True)
def timedelta_neg(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return datetime.timedelta(-lhs.days, -lhs.seconds, -lhs.
                microseconds)
        return impl


@overload(operator.pos, no_unliteral=True)
def timedelta_pos(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            return lhs
        return impl


@overload(divmod, no_unliteral=True)
def timedelta_divmod(lhs, rhs):
    if lhs == datetime_timedelta_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            scfdq__xpg, bsne__ugud = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return scfdq__xpg, datetime.timedelta(0, 0, bsne__ugud)
        return impl


@overload(abs, no_unliteral=True)
def timedelta_abs(lhs):
    if lhs == datetime_timedelta_type:

        def impl(lhs):
            if lhs.days < 0:
                return -lhs
            else:
                return lhs
        return impl


@intrinsic
def cast_numpy_timedelta_to_int(typingctx, val=None):
    assert val in (types.NPTimedelta('ns'), types.int64)

    def codegen(context, builder, signature, args):
        return args[0]
    return types.int64(val), codegen


@overload(bool, no_unliteral=True)
def timedelta_to_bool(timedelta):
    if timedelta != datetime_timedelta_type:
        return
    srfx__fuqml = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != srfx__fuqml
    return impl


class DatetimeTimeDeltaArrayType(types.ArrayCompatible):

    def __init__(self):
        super(DatetimeTimeDeltaArrayType, self).__init__(name=
            'DatetimeTimeDeltaArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return datetime_timedelta_type

    def copy(self):
        return DatetimeTimeDeltaArrayType()


datetime_timedelta_array_type = DatetimeTimeDeltaArrayType()
types.datetime_timedelta_array_type = datetime_timedelta_array_type
days_data_type = types.Array(types.int64, 1, 'C')
seconds_data_type = types.Array(types.int64, 1, 'C')
microseconds_data_type = types.Array(types.int64, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(DatetimeTimeDeltaArrayType)
class DatetimeTimeDeltaArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mdnym__yhf = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, mdnym__yhf)


make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'days_data', '_days_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'seconds_data',
    '_seconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'microseconds_data',
    '_microseconds_data')
make_attribute_wrapper(DatetimeTimeDeltaArrayType, 'null_bitmap',
    '_null_bitmap')


@overload_method(DatetimeTimeDeltaArrayType, 'copy', no_unliteral=True)
def overload_datetime_timedelta_arr_copy(A):
    return (lambda A: bodo.hiframes.datetime_timedelta_ext.
        init_datetime_timedelta_array(A._days_data.copy(), A._seconds_data.
        copy(), A._microseconds_data.copy(), A._null_bitmap.copy()))


@unbox(DatetimeTimeDeltaArrayType)
def unbox_datetime_timedelta_array(typ, val, c):
    n = bodo.utils.utils.object_length(c, val)
    lda__racfj = types.Array(types.intp, 1, 'C')
    oek__qxqtv = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        lda__racfj, [n])
    ynulm__wmjb = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        lda__racfj, [n])
    vnpqc__gkmk = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        lda__racfj, [n])
    yrtp__uhjx = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    gjs__vnjfk = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [yrtp__uhjx])
    bca__pdzdl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    rhbcy__ghb = cgutils.get_or_insert_function(c.builder.module,
        bca__pdzdl, name='unbox_datetime_timedelta_array')
    c.builder.call(rhbcy__ghb, [val, n, oek__qxqtv.data, ynulm__wmjb.data,
        vnpqc__gkmk.data, gjs__vnjfk.data])
    wry__vrk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wry__vrk.days_data = oek__qxqtv._getvalue()
    wry__vrk.seconds_data = ynulm__wmjb._getvalue()
    wry__vrk.microseconds_data = vnpqc__gkmk._getvalue()
    wry__vrk.null_bitmap = gjs__vnjfk._getvalue()
    crtq__iqstk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(wry__vrk._getvalue(), is_error=crtq__iqstk)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    qlkg__jfl = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    oek__qxqtv = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qlkg__jfl.days_data)
    ynulm__wmjb = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qlkg__jfl.seconds_data).data
    vnpqc__gkmk = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qlkg__jfl.microseconds_data).data
    zodvk__wzjgv = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, qlkg__jfl.null_bitmap).data
    n = c.builder.extract_value(oek__qxqtv.shape, 0)
    bca__pdzdl = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    jijl__xinxs = cgutils.get_or_insert_function(c.builder.module,
        bca__pdzdl, name='box_datetime_timedelta_array')
    dzw__celcg = c.builder.call(jijl__xinxs, [n, oek__qxqtv.data,
        ynulm__wmjb, vnpqc__gkmk, zodvk__wzjgv])
    c.context.nrt.decref(c.builder, typ, val)
    return dzw__celcg


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        oojwm__oekta, cuq__ynqlk, vqrh__geqp, ohjf__nge = args
        tpwz__paa = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        tpwz__paa.days_data = oojwm__oekta
        tpwz__paa.seconds_data = cuq__ynqlk
        tpwz__paa.microseconds_data = vqrh__geqp
        tpwz__paa.null_bitmap = ohjf__nge
        context.nrt.incref(builder, signature.args[0], oojwm__oekta)
        context.nrt.incref(builder, signature.args[1], cuq__ynqlk)
        context.nrt.incref(builder, signature.args[2], vqrh__geqp)
        context.nrt.incref(builder, signature.args[3], ohjf__nge)
        return tpwz__paa._getvalue()
    liv__lqlae = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return liv__lqlae, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    oek__qxqtv = np.empty(n, np.int64)
    ynulm__wmjb = np.empty(n, np.int64)
    vnpqc__gkmk = np.empty(n, np.int64)
    ezkno__lhsad = np.empty(n + 7 >> 3, np.uint8)
    for hfvei__pzi, s in enumerate(pyval):
        llg__homna = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(ezkno__lhsad, hfvei__pzi, int(
            not llg__homna))
        if not llg__homna:
            oek__qxqtv[hfvei__pzi] = s.days
            ynulm__wmjb[hfvei__pzi] = s.seconds
            vnpqc__gkmk[hfvei__pzi] = s.microseconds
    mir__sqaoj = context.get_constant_generic(builder, days_data_type,
        oek__qxqtv)
    wlyb__zeno = context.get_constant_generic(builder, seconds_data_type,
        ynulm__wmjb)
    vda__vohw = context.get_constant_generic(builder,
        microseconds_data_type, vnpqc__gkmk)
    kjhwt__ygpuc = context.get_constant_generic(builder, nulls_type,
        ezkno__lhsad)
    return lir.Constant.literal_struct([mir__sqaoj, wlyb__zeno, vda__vohw,
        kjhwt__ygpuc])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    oek__qxqtv = np.empty(n, dtype=np.int64)
    ynulm__wmjb = np.empty(n, dtype=np.int64)
    vnpqc__gkmk = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(oek__qxqtv, ynulm__wmjb,
        vnpqc__gkmk, nulls)


def alloc_datetime_timedelta_array_equiv(self, scope, equiv_set, loc, args, kws
    ):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_datetime_timedelta_ext_alloc_datetime_timedelta_array
    ) = alloc_datetime_timedelta_array_equiv


@overload(operator.getitem, no_unliteral=True)
def dt_timedelta_arr_getitem(A, ind):
    if A != datetime_timedelta_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl_int(A, ind):
            return datetime.timedelta(days=A._days_data[ind], seconds=A.
                _seconds_data[ind], microseconds=A._microseconds_data[ind])
        return impl_int
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            atgo__gomf = bodo.utils.conversion.coerce_to_ndarray(ind)
            dragz__cwxi = A._null_bitmap
            aklid__aqbfi = A._days_data[atgo__gomf]
            qxrhd__eyw = A._seconds_data[atgo__gomf]
            zlyz__cqkbm = A._microseconds_data[atgo__gomf]
            n = len(aklid__aqbfi)
            xhkrt__yrs = get_new_null_mask_bool_index(dragz__cwxi, ind, n)
            return init_datetime_timedelta_array(aklid__aqbfi, qxrhd__eyw,
                zlyz__cqkbm, xhkrt__yrs)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            atgo__gomf = bodo.utils.conversion.coerce_to_ndarray(ind)
            dragz__cwxi = A._null_bitmap
            aklid__aqbfi = A._days_data[atgo__gomf]
            qxrhd__eyw = A._seconds_data[atgo__gomf]
            zlyz__cqkbm = A._microseconds_data[atgo__gomf]
            n = len(aklid__aqbfi)
            xhkrt__yrs = get_new_null_mask_int_index(dragz__cwxi, atgo__gomf, n
                )
            return init_datetime_timedelta_array(aklid__aqbfi, qxrhd__eyw,
                zlyz__cqkbm, xhkrt__yrs)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            dragz__cwxi = A._null_bitmap
            aklid__aqbfi = np.ascontiguousarray(A._days_data[ind])
            qxrhd__eyw = np.ascontiguousarray(A._seconds_data[ind])
            zlyz__cqkbm = np.ascontiguousarray(A._microseconds_data[ind])
            xhkrt__yrs = get_new_null_mask_slice_index(dragz__cwxi, ind, n)
            return init_datetime_timedelta_array(aklid__aqbfi, qxrhd__eyw,
                zlyz__cqkbm, xhkrt__yrs)
        return impl_slice
    raise BodoError(
        f'getitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(operator.setitem, no_unliteral=True)
def dt_timedelta_arr_setitem(A, ind, val):
    if A != datetime_timedelta_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    notrj__ubig = (
        f"setitem for DatetimeTimedeltaArray with indexing type {ind} received an incorrect 'value' type {val}."
        )
    if isinstance(ind, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl(A, ind, val):
                A._days_data[ind] = val._days
                A._seconds_data[ind] = val._seconds
                A._microseconds_data[ind] = val._microseconds
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, ind, 1)
            return impl
        else:
            raise BodoError(notrj__ubig)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(notrj__ubig)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for hfvei__pzi in range(n):
                    A._days_data[ind[hfvei__pzi]] = val._days
                    A._seconds_data[ind[hfvei__pzi]] = val._seconds
                    A._microseconds_data[ind[hfvei__pzi]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[hfvei__pzi], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for hfvei__pzi in range(n):
                    A._days_data[ind[hfvei__pzi]] = val._days_data[hfvei__pzi]
                    A._seconds_data[ind[hfvei__pzi]] = val._seconds_data[
                        hfvei__pzi]
                    A._microseconds_data[ind[hfvei__pzi]
                        ] = val._microseconds_data[hfvei__pzi]
                    btr__tdt = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, hfvei__pzi)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[hfvei__pzi], btr__tdt)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for hfvei__pzi in range(n):
                    if not bodo.libs.array_kernels.isna(ind, hfvei__pzi
                        ) and ind[hfvei__pzi]:
                        A._days_data[hfvei__pzi] = val._days
                        A._seconds_data[hfvei__pzi] = val._seconds
                        A._microseconds_data[hfvei__pzi] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            hfvei__pzi, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                hyrnc__xkm = 0
                for hfvei__pzi in range(n):
                    if not bodo.libs.array_kernels.isna(ind, hfvei__pzi
                        ) and ind[hfvei__pzi]:
                        A._days_data[hfvei__pzi] = val._days_data[hyrnc__xkm]
                        A._seconds_data[hfvei__pzi] = val._seconds_data[
                            hyrnc__xkm]
                        A._microseconds_data[hfvei__pzi
                            ] = val._microseconds_data[hyrnc__xkm]
                        btr__tdt = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                            ._null_bitmap, hyrnc__xkm)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            hfvei__pzi, btr__tdt)
                        hyrnc__xkm += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                bdxo__wyl = numba.cpython.unicode._normalize_slice(ind, len(A))
                for hfvei__pzi in range(bdxo__wyl.start, bdxo__wyl.stop,
                    bdxo__wyl.step):
                    A._days_data[hfvei__pzi] = val._days
                    A._seconds_data[hfvei__pzi] = val._seconds
                    A._microseconds_data[hfvei__pzi] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        hfvei__pzi, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                fpdm__pei = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, fpdm__pei, ind, n
                    )
            return impl_slice_mask
    raise BodoError(
        f'setitem for DatetimeTimedeltaArray with indexing type {ind} not supported.'
        )


@overload(len, no_unliteral=True)
def overload_len_datetime_timedelta_arr(A):
    if A == datetime_timedelta_array_type:
        return lambda A: len(A._days_data)


@overload_attribute(DatetimeTimeDeltaArrayType, 'shape')
def overload_datetime_timedelta_arr_shape(A):
    return lambda A: (len(A._days_data),)


@overload_attribute(DatetimeTimeDeltaArrayType, 'nbytes')
def timedelta_arr_nbytes_overload(A):
    return (lambda A: A._days_data.nbytes + A._seconds_data.nbytes + A.
        _microseconds_data.nbytes + A._null_bitmap.nbytes)


def overload_datetime_timedelta_arr_sub(arg1, arg2):
    if (arg1 == datetime_timedelta_array_type and arg2 ==
        datetime_timedelta_type):

        def impl(arg1, arg2):
            qlkg__jfl = arg1
            numba.parfors.parfor.init_prange()
            n = len(qlkg__jfl)
            A = alloc_datetime_timedelta_array(n)
            for hfvei__pzi in numba.parfors.parfor.internal_prange(n):
                A[hfvei__pzi] = qlkg__jfl[hfvei__pzi] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            odpf__folkv = True
        else:
            odpf__folkv = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                skud__pwq = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for hfvei__pzi in numba.parfors.parfor.internal_prange(n):
                    zhnoz__qormy = bodo.libs.array_kernels.isna(lhs, hfvei__pzi
                        )
                    ofr__rnkta = bodo.libs.array_kernels.isna(rhs, hfvei__pzi)
                    if zhnoz__qormy or ofr__rnkta:
                        ecj__tnly = odpf__folkv
                    else:
                        ecj__tnly = op(lhs[hfvei__pzi], rhs[hfvei__pzi])
                    skud__pwq[hfvei__pzi] = ecj__tnly
                return skud__pwq
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                skud__pwq = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for hfvei__pzi in numba.parfors.parfor.internal_prange(n):
                    btr__tdt = bodo.libs.array_kernels.isna(lhs, hfvei__pzi)
                    if btr__tdt:
                        ecj__tnly = odpf__folkv
                    else:
                        ecj__tnly = op(lhs[hfvei__pzi], rhs)
                    skud__pwq[hfvei__pzi] = ecj__tnly
                return skud__pwq
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                skud__pwq = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for hfvei__pzi in numba.parfors.parfor.internal_prange(n):
                    btr__tdt = bodo.libs.array_kernels.isna(rhs, hfvei__pzi)
                    if btr__tdt:
                        ecj__tnly = odpf__folkv
                    else:
                        ecj__tnly = op(lhs, rhs[hfvei__pzi])
                    skud__pwq[hfvei__pzi] = ecj__tnly
                return skud__pwq
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for jpb__hyis in timedelta_unsupported_attrs:
        fxg__wfjme = 'pandas.Timedelta.' + jpb__hyis
        overload_attribute(PDTimeDeltaType, jpb__hyis)(
            create_unsupported_overload(fxg__wfjme))
    for xsqys__vxbh in timedelta_unsupported_methods:
        fxg__wfjme = 'pandas.Timedelta.' + xsqys__vxbh
        overload_method(PDTimeDeltaType, xsqys__vxbh)(
            create_unsupported_overload(fxg__wfjme + '()'))


_intstall_pd_timedelta_unsupported()
