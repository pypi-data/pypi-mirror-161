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
        fxav__zce = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, fxav__zce)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    qzfn__xzitu = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    vtwje__ipz = c.pyapi.long_from_longlong(qzfn__xzitu.value)
    hna__snugz = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(hna__snugz, (vtwje__ipz,))
    c.pyapi.decref(vtwje__ipz)
    c.pyapi.decref(hna__snugz)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    vtwje__ipz = c.pyapi.object_getattr_string(val, 'value')
    cwgfy__xygxm = c.pyapi.long_as_longlong(vtwje__ipz)
    qzfn__xzitu = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qzfn__xzitu.value = cwgfy__xygxm
    c.pyapi.decref(vtwje__ipz)
    sazwi__jrf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qzfn__xzitu._getvalue(), is_error=sazwi__jrf)


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
            ywa__rpk = 1000 * microseconds
            return init_pd_timedelta(ywa__rpk)
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
            ywa__rpk = 1000 * microseconds
            return init_pd_timedelta(ywa__rpk)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    rkq__jkm, twqx__xfpi = pd._libs.tslibs.conversion.precision_from_unit(unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * rkq__jkm)
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
            qcbfv__oql = (rhs.microseconds + (rhs.seconds + rhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + qcbfv__oql
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            pycl__prsmw = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = pycl__prsmw + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            tdqll__amy = rhs.toordinal()
            hthyh__jdd = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            otqko__hkee = rhs.microsecond
            ulznq__ijv = lhs.value // 1000
            qyt__lele = lhs.nanoseconds
            pbt__apjqu = otqko__hkee + ulznq__ijv
            cls__cbczb = 1000000 * (tdqll__amy * 86400 + hthyh__jdd
                ) + pbt__apjqu
            ciewh__axevx = qyt__lele
            return compute_pd_timestamp(cls__cbczb, ciewh__axevx)
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
            qocsy__nqtwg = datetime.timedelta(rhs.toordinal(), hours=rhs.
                hour, minutes=rhs.minute, seconds=rhs.second, microseconds=
                rhs.microsecond)
            qocsy__nqtwg = qocsy__nqtwg + lhs
            qmkwo__itg, hlle__iabx = divmod(qocsy__nqtwg.seconds, 3600)
            cjlbk__chj, fpyap__oidq = divmod(hlle__iabx, 60)
            if 0 < qocsy__nqtwg.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(
                    qocsy__nqtwg.days)
                return datetime.datetime(d.year, d.month, d.day, qmkwo__itg,
                    cjlbk__chj, fpyap__oidq, qocsy__nqtwg.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            qocsy__nqtwg = datetime.timedelta(lhs.toordinal(), hours=lhs.
                hour, minutes=lhs.minute, seconds=lhs.second, microseconds=
                lhs.microsecond)
            qocsy__nqtwg = qocsy__nqtwg + rhs
            qmkwo__itg, hlle__iabx = divmod(qocsy__nqtwg.seconds, 3600)
            cjlbk__chj, fpyap__oidq = divmod(hlle__iabx, 60)
            if 0 < qocsy__nqtwg.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(
                    qocsy__nqtwg.days)
                return datetime.datetime(d.year, d.month, d.day, qmkwo__itg,
                    cjlbk__chj, fpyap__oidq, qocsy__nqtwg.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            ghkii__itw = lhs.value - rhs.value
            return pd.Timedelta(ghkii__itw)
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
            qxexr__vjgr = lhs
            numba.parfors.parfor.init_prange()
            n = len(qxexr__vjgr)
            A = alloc_datetime_timedelta_array(n)
            for kpjvr__kyvys in numba.parfors.parfor.internal_prange(n):
                A[kpjvr__kyvys] = qxexr__vjgr[kpjvr__kyvys] - rhs
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
            qnim__ebyv = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, qnim__ebyv)
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
            oamk__nckg, qnim__ebyv = divmod(lhs.value, rhs.value)
            return oamk__nckg, pd.Timedelta(qnim__ebyv)
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
        fxav__zce = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, fxav__zce)


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    qzfn__xzitu = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    jrti__ospg = c.pyapi.long_from_longlong(qzfn__xzitu.days)
    sper__nxftp = c.pyapi.long_from_longlong(qzfn__xzitu.seconds)
    qtcj__tdids = c.pyapi.long_from_longlong(qzfn__xzitu.microseconds)
    hna__snugz = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(hna__snugz, (jrti__ospg,
        sper__nxftp, qtcj__tdids))
    c.pyapi.decref(jrti__ospg)
    c.pyapi.decref(sper__nxftp)
    c.pyapi.decref(qtcj__tdids)
    c.pyapi.decref(hna__snugz)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    jrti__ospg = c.pyapi.object_getattr_string(val, 'days')
    sper__nxftp = c.pyapi.object_getattr_string(val, 'seconds')
    qtcj__tdids = c.pyapi.object_getattr_string(val, 'microseconds')
    xxx__lzeh = c.pyapi.long_as_longlong(jrti__ospg)
    njzxv__mjl = c.pyapi.long_as_longlong(sper__nxftp)
    zar__zsrfv = c.pyapi.long_as_longlong(qtcj__tdids)
    qzfn__xzitu = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qzfn__xzitu.days = xxx__lzeh
    qzfn__xzitu.seconds = njzxv__mjl
    qzfn__xzitu.microseconds = zar__zsrfv
    c.pyapi.decref(jrti__ospg)
    c.pyapi.decref(sper__nxftp)
    c.pyapi.decref(qtcj__tdids)
    sazwi__jrf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qzfn__xzitu._getvalue(), is_error=sazwi__jrf)


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
    oamk__nckg, qnim__ebyv = divmod(a, b)
    qnim__ebyv *= 2
    hmgo__rnii = qnim__ebyv > b if b > 0 else qnim__ebyv < b
    if hmgo__rnii or qnim__ebyv == b and oamk__nckg % 2 == 1:
        oamk__nckg += 1
    return oamk__nckg


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
                ezln__idfjp = _cmp(_getstate(lhs), _getstate(rhs))
                return op(ezln__idfjp, 0)
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
            oamk__nckg, qnim__ebyv = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return oamk__nckg, datetime.timedelta(0, 0, qnim__ebyv)
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
    hfp__rvwa = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != hfp__rvwa
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
        fxav__zce = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, fxav__zce)


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
    bwl__uqtq = types.Array(types.intp, 1, 'C')
    ihpa__vduqy = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        bwl__uqtq, [n])
    ijkx__pdzfs = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        bwl__uqtq, [n])
    cndh__bcczy = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        bwl__uqtq, [n])
    czpj__mhufk = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    ijyuj__pqy = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [czpj__mhufk])
    fmat__nrdi = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    rbb__sut = cgutils.get_or_insert_function(c.builder.module, fmat__nrdi,
        name='unbox_datetime_timedelta_array')
    c.builder.call(rbb__sut, [val, n, ihpa__vduqy.data, ijkx__pdzfs.data,
        cndh__bcczy.data, ijyuj__pqy.data])
    wez__wkmb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wez__wkmb.days_data = ihpa__vduqy._getvalue()
    wez__wkmb.seconds_data = ijkx__pdzfs._getvalue()
    wez__wkmb.microseconds_data = cndh__bcczy._getvalue()
    wez__wkmb.null_bitmap = ijyuj__pqy._getvalue()
    sazwi__jrf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(wez__wkmb._getvalue(), is_error=sazwi__jrf)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    qxexr__vjgr = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    ihpa__vduqy = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qxexr__vjgr.days_data)
    ijkx__pdzfs = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qxexr__vjgr.seconds_data).data
    cndh__bcczy = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qxexr__vjgr.microseconds_data).data
    cmcbj__lkjb = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, qxexr__vjgr.null_bitmap).data
    n = c.builder.extract_value(ihpa__vduqy.shape, 0)
    fmat__nrdi = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    buio__lomm = cgutils.get_or_insert_function(c.builder.module,
        fmat__nrdi, name='box_datetime_timedelta_array')
    fjur__iaab = c.builder.call(buio__lomm, [n, ihpa__vduqy.data,
        ijkx__pdzfs, cndh__bcczy, cmcbj__lkjb])
    c.context.nrt.decref(c.builder, typ, val)
    return fjur__iaab


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        swfh__kxxv, zpqjc__gteg, yfdg__bfz, cwgk__firir = args
        obra__inzwg = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        obra__inzwg.days_data = swfh__kxxv
        obra__inzwg.seconds_data = zpqjc__gteg
        obra__inzwg.microseconds_data = yfdg__bfz
        obra__inzwg.null_bitmap = cwgk__firir
        context.nrt.incref(builder, signature.args[0], swfh__kxxv)
        context.nrt.incref(builder, signature.args[1], zpqjc__gteg)
        context.nrt.incref(builder, signature.args[2], yfdg__bfz)
        context.nrt.incref(builder, signature.args[3], cwgk__firir)
        return obra__inzwg._getvalue()
    hyg__mxr = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return hyg__mxr, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    ihpa__vduqy = np.empty(n, np.int64)
    ijkx__pdzfs = np.empty(n, np.int64)
    cndh__bcczy = np.empty(n, np.int64)
    sklzr__odfr = np.empty(n + 7 >> 3, np.uint8)
    for kpjvr__kyvys, s in enumerate(pyval):
        soass__fft = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(sklzr__odfr, kpjvr__kyvys, int
            (not soass__fft))
        if not soass__fft:
            ihpa__vduqy[kpjvr__kyvys] = s.days
            ijkx__pdzfs[kpjvr__kyvys] = s.seconds
            cndh__bcczy[kpjvr__kyvys] = s.microseconds
    exgz__crqcs = context.get_constant_generic(builder, days_data_type,
        ihpa__vduqy)
    mtk__kdh = context.get_constant_generic(builder, seconds_data_type,
        ijkx__pdzfs)
    eacl__gxslo = context.get_constant_generic(builder,
        microseconds_data_type, cndh__bcczy)
    sxitz__njz = context.get_constant_generic(builder, nulls_type, sklzr__odfr)
    return lir.Constant.literal_struct([exgz__crqcs, mtk__kdh, eacl__gxslo,
        sxitz__njz])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    ihpa__vduqy = np.empty(n, dtype=np.int64)
    ijkx__pdzfs = np.empty(n, dtype=np.int64)
    cndh__bcczy = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(ihpa__vduqy, ijkx__pdzfs,
        cndh__bcczy, nulls)


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
            jujro__ifl = bodo.utils.conversion.coerce_to_ndarray(ind)
            iqxbg__pfqv = A._null_bitmap
            iqly__wkdz = A._days_data[jujro__ifl]
            vyx__qrz = A._seconds_data[jujro__ifl]
            vxwtr__uqwiw = A._microseconds_data[jujro__ifl]
            n = len(iqly__wkdz)
            frk__tnsok = get_new_null_mask_bool_index(iqxbg__pfqv, ind, n)
            return init_datetime_timedelta_array(iqly__wkdz, vyx__qrz,
                vxwtr__uqwiw, frk__tnsok)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            jujro__ifl = bodo.utils.conversion.coerce_to_ndarray(ind)
            iqxbg__pfqv = A._null_bitmap
            iqly__wkdz = A._days_data[jujro__ifl]
            vyx__qrz = A._seconds_data[jujro__ifl]
            vxwtr__uqwiw = A._microseconds_data[jujro__ifl]
            n = len(iqly__wkdz)
            frk__tnsok = get_new_null_mask_int_index(iqxbg__pfqv, jujro__ifl, n
                )
            return init_datetime_timedelta_array(iqly__wkdz, vyx__qrz,
                vxwtr__uqwiw, frk__tnsok)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            iqxbg__pfqv = A._null_bitmap
            iqly__wkdz = np.ascontiguousarray(A._days_data[ind])
            vyx__qrz = np.ascontiguousarray(A._seconds_data[ind])
            vxwtr__uqwiw = np.ascontiguousarray(A._microseconds_data[ind])
            frk__tnsok = get_new_null_mask_slice_index(iqxbg__pfqv, ind, n)
            return init_datetime_timedelta_array(iqly__wkdz, vyx__qrz,
                vxwtr__uqwiw, frk__tnsok)
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
    zcaj__bnu = (
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
            raise BodoError(zcaj__bnu)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(zcaj__bnu)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for kpjvr__kyvys in range(n):
                    A._days_data[ind[kpjvr__kyvys]] = val._days
                    A._seconds_data[ind[kpjvr__kyvys]] = val._seconds
                    A._microseconds_data[ind[kpjvr__kyvys]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[kpjvr__kyvys], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for kpjvr__kyvys in range(n):
                    A._days_data[ind[kpjvr__kyvys]] = val._days_data[
                        kpjvr__kyvys]
                    A._seconds_data[ind[kpjvr__kyvys]] = val._seconds_data[
                        kpjvr__kyvys]
                    A._microseconds_data[ind[kpjvr__kyvys]
                        ] = val._microseconds_data[kpjvr__kyvys]
                    vce__ywqt = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, kpjvr__kyvys)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[kpjvr__kyvys], vce__ywqt)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for kpjvr__kyvys in range(n):
                    if not bodo.libs.array_kernels.isna(ind, kpjvr__kyvys
                        ) and ind[kpjvr__kyvys]:
                        A._days_data[kpjvr__kyvys] = val._days
                        A._seconds_data[kpjvr__kyvys] = val._seconds
                        A._microseconds_data[kpjvr__kyvys] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            kpjvr__kyvys, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                gzpw__ahi = 0
                for kpjvr__kyvys in range(n):
                    if not bodo.libs.array_kernels.isna(ind, kpjvr__kyvys
                        ) and ind[kpjvr__kyvys]:
                        A._days_data[kpjvr__kyvys] = val._days_data[gzpw__ahi]
                        A._seconds_data[kpjvr__kyvys] = val._seconds_data[
                            gzpw__ahi]
                        A._microseconds_data[kpjvr__kyvys
                            ] = val._microseconds_data[gzpw__ahi]
                        vce__ywqt = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, gzpw__ahi)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            kpjvr__kyvys, vce__ywqt)
                        gzpw__ahi += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                akkbm__eogb = numba.cpython.unicode._normalize_slice(ind,
                    len(A))
                for kpjvr__kyvys in range(akkbm__eogb.start, akkbm__eogb.
                    stop, akkbm__eogb.step):
                    A._days_data[kpjvr__kyvys] = val._days
                    A._seconds_data[kpjvr__kyvys] = val._seconds
                    A._microseconds_data[kpjvr__kyvys] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        kpjvr__kyvys, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                kikk__ebnu = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, kikk__ebnu,
                    ind, n)
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
            qxexr__vjgr = arg1
            numba.parfors.parfor.init_prange()
            n = len(qxexr__vjgr)
            A = alloc_datetime_timedelta_array(n)
            for kpjvr__kyvys in numba.parfors.parfor.internal_prange(n):
                A[kpjvr__kyvys] = qxexr__vjgr[kpjvr__kyvys] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            kkq__qoj = True
        else:
            kkq__qoj = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                ogx__pzg = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for kpjvr__kyvys in numba.parfors.parfor.internal_prange(n):
                    dbdhv__xje = bodo.libs.array_kernels.isna(lhs, kpjvr__kyvys
                        )
                    qqk__tvdy = bodo.libs.array_kernels.isna(rhs, kpjvr__kyvys)
                    if dbdhv__xje or qqk__tvdy:
                        qxhwq__qhd = kkq__qoj
                    else:
                        qxhwq__qhd = op(lhs[kpjvr__kyvys], rhs[kpjvr__kyvys])
                    ogx__pzg[kpjvr__kyvys] = qxhwq__qhd
                return ogx__pzg
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                ogx__pzg = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for kpjvr__kyvys in numba.parfors.parfor.internal_prange(n):
                    vce__ywqt = bodo.libs.array_kernels.isna(lhs, kpjvr__kyvys)
                    if vce__ywqt:
                        qxhwq__qhd = kkq__qoj
                    else:
                        qxhwq__qhd = op(lhs[kpjvr__kyvys], rhs)
                    ogx__pzg[kpjvr__kyvys] = qxhwq__qhd
                return ogx__pzg
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                ogx__pzg = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for kpjvr__kyvys in numba.parfors.parfor.internal_prange(n):
                    vce__ywqt = bodo.libs.array_kernels.isna(rhs, kpjvr__kyvys)
                    if vce__ywqt:
                        qxhwq__qhd = kkq__qoj
                    else:
                        qxhwq__qhd = op(lhs, rhs[kpjvr__kyvys])
                    ogx__pzg[kpjvr__kyvys] = qxhwq__qhd
                return ogx__pzg
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for tqd__xmnch in timedelta_unsupported_attrs:
        polgm__tag = 'pandas.Timedelta.' + tqd__xmnch
        overload_attribute(PDTimeDeltaType, tqd__xmnch)(
            create_unsupported_overload(polgm__tag))
    for aelny__rxs in timedelta_unsupported_methods:
        polgm__tag = 'pandas.Timedelta.' + aelny__rxs
        overload_method(PDTimeDeltaType, aelny__rxs)(
            create_unsupported_overload(polgm__tag + '()'))


_intstall_pd_timedelta_unsupported()
