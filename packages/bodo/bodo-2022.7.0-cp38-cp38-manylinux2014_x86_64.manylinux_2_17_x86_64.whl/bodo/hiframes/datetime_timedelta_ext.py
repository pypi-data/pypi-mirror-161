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
        khwro__sqjds = [('value', types.int64)]
        super(PDTimeDeltaModel, self).__init__(dmm, fe_type, khwro__sqjds)


@box(PDTimeDeltaType)
def box_pd_timedelta(typ, val, c):
    bln__hec = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    wysqp__xhiq = c.pyapi.long_from_longlong(bln__hec.value)
    uvcl__zfzkj = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Timedelta))
    res = c.pyapi.call_function_objargs(uvcl__zfzkj, (wysqp__xhiq,))
    c.pyapi.decref(wysqp__xhiq)
    c.pyapi.decref(uvcl__zfzkj)
    return res


@unbox(PDTimeDeltaType)
def unbox_pd_timedelta(typ, val, c):
    wysqp__xhiq = c.pyapi.object_getattr_string(val, 'value')
    pbwe__hxx = c.pyapi.long_as_longlong(wysqp__xhiq)
    bln__hec = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bln__hec.value = pbwe__hxx
    c.pyapi.decref(wysqp__xhiq)
    rgubz__jmbrh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(bln__hec._getvalue(), is_error=rgubz__jmbrh)


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
            uvmj__odz = 1000 * microseconds
            return init_pd_timedelta(uvmj__odz)
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
            uvmj__odz = 1000 * microseconds
            return init_pd_timedelta(uvmj__odz)
        return impl_timedelta_datetime
    if not is_overload_constant_str(unit):
        raise BodoError('pd.to_timedelta(): unit should be a constant string')
    unit = pd._libs.tslibs.timedeltas.parse_timedelta_unit(
        get_overload_const_str(unit))
    jhjee__uvuh, uyggk__nqeih = pd._libs.tslibs.conversion.precision_from_unit(
        unit)

    def impl_timedelta(value=_no_input, unit='ns', days=0, seconds=0,
        microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        return init_pd_timedelta(value * jhjee__uvuh)
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
            zmk__hazp = (rhs.microseconds + (rhs.seconds + rhs.days * 60 * 
                60 * 24) * 1000 * 1000) * 1000
            val = lhs.value + zmk__hazp
            return pd.Timedelta(val)
        return impl
    if lhs == datetime_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            wwtps__ibf = (lhs.microseconds + (lhs.seconds + lhs.days * 60 *
                60 * 24) * 1000 * 1000) * 1000
            val = wwtps__ibf + rhs.value
            return pd.Timedelta(val)
        return impl
    if lhs == pd_timedelta_type and rhs == datetime_datetime_type:
        from bodo.hiframes.pd_timestamp_ext import compute_pd_timestamp

        def impl(lhs, rhs):
            bmgsi__zfyp = rhs.toordinal()
            owfjl__wnnz = rhs.second + rhs.minute * 60 + rhs.hour * 3600
            glg__rwej = rhs.microsecond
            iqs__qceof = lhs.value // 1000
            fxke__pfj = lhs.nanoseconds
            zuhu__twhu = glg__rwej + iqs__qceof
            reva__hapk = 1000000 * (bmgsi__zfyp * 86400 + owfjl__wnnz
                ) + zuhu__twhu
            xsfpf__ltn = fxke__pfj
            return compute_pd_timestamp(reva__hapk, xsfpf__ltn)
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
            ies__vdni = datetime.timedelta(rhs.toordinal(), hours=rhs.hour,
                minutes=rhs.minute, seconds=rhs.second, microseconds=rhs.
                microsecond)
            ies__vdni = ies__vdni + lhs
            umxbc__klu, lrbvg__kbvaj = divmod(ies__vdni.seconds, 3600)
            daw__wzaql, audp__lwqk = divmod(lrbvg__kbvaj, 60)
            if 0 < ies__vdni.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(ies__vdni
                    .days)
                return datetime.datetime(d.year, d.month, d.day, umxbc__klu,
                    daw__wzaql, audp__lwqk, ies__vdni.microseconds)
            raise OverflowError('result out of range')
        return impl
    if lhs == datetime_datetime_type and rhs == datetime_timedelta_type:

        def impl(lhs, rhs):
            ies__vdni = datetime.timedelta(lhs.toordinal(), hours=lhs.hour,
                minutes=lhs.minute, seconds=lhs.second, microseconds=lhs.
                microsecond)
            ies__vdni = ies__vdni + rhs
            umxbc__klu, lrbvg__kbvaj = divmod(ies__vdni.seconds, 3600)
            daw__wzaql, audp__lwqk = divmod(lrbvg__kbvaj, 60)
            if 0 < ies__vdni.days <= _MAXORDINAL:
                d = bodo.hiframes.datetime_date_ext.fromordinal_impl(ies__vdni
                    .days)
                return datetime.datetime(d.year, d.month, d.day, umxbc__klu,
                    daw__wzaql, audp__lwqk, ies__vdni.microseconds)
            raise OverflowError('result out of range')
        return impl


def overload_sub_operator_datetime_timedelta(lhs, rhs):
    if lhs == pd_timedelta_type and rhs == pd_timedelta_type:

        def impl(lhs, rhs):
            wcu__hpmz = lhs.value - rhs.value
            return pd.Timedelta(wcu__hpmz)
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
            qxqg__qvcw = lhs
            numba.parfors.parfor.init_prange()
            n = len(qxqg__qvcw)
            A = alloc_datetime_timedelta_array(n)
            for ggfe__jnjn in numba.parfors.parfor.internal_prange(n):
                A[ggfe__jnjn] = qxqg__qvcw[ggfe__jnjn] - rhs
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
            xtpun__izzmz = _to_microseconds(lhs) % _to_microseconds(rhs)
            return datetime.timedelta(0, 0, xtpun__izzmz)
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
            yajj__ixzku, xtpun__izzmz = divmod(lhs.value, rhs.value)
            return yajj__ixzku, pd.Timedelta(xtpun__izzmz)
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
        khwro__sqjds = [('days', types.int64), ('seconds', types.int64), (
            'microseconds', types.int64)]
        super(DatetimeTimeDeltaModel, self).__init__(dmm, fe_type, khwro__sqjds
            )


@box(DatetimeTimeDeltaType)
def box_datetime_timedelta(typ, val, c):
    bln__hec = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    zjc__xau = c.pyapi.long_from_longlong(bln__hec.days)
    ldupj__bjaua = c.pyapi.long_from_longlong(bln__hec.seconds)
    jbf__gvwo = c.pyapi.long_from_longlong(bln__hec.microseconds)
    uvcl__zfzkj = c.pyapi.unserialize(c.pyapi.serialize_object(datetime.
        timedelta))
    res = c.pyapi.call_function_objargs(uvcl__zfzkj, (zjc__xau,
        ldupj__bjaua, jbf__gvwo))
    c.pyapi.decref(zjc__xau)
    c.pyapi.decref(ldupj__bjaua)
    c.pyapi.decref(jbf__gvwo)
    c.pyapi.decref(uvcl__zfzkj)
    return res


@unbox(DatetimeTimeDeltaType)
def unbox_datetime_timedelta(typ, val, c):
    zjc__xau = c.pyapi.object_getattr_string(val, 'days')
    ldupj__bjaua = c.pyapi.object_getattr_string(val, 'seconds')
    jbf__gvwo = c.pyapi.object_getattr_string(val, 'microseconds')
    hmxqh__irwid = c.pyapi.long_as_longlong(zjc__xau)
    huu__fbnat = c.pyapi.long_as_longlong(ldupj__bjaua)
    pum__xrzr = c.pyapi.long_as_longlong(jbf__gvwo)
    bln__hec = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bln__hec.days = hmxqh__irwid
    bln__hec.seconds = huu__fbnat
    bln__hec.microseconds = pum__xrzr
    c.pyapi.decref(zjc__xau)
    c.pyapi.decref(ldupj__bjaua)
    c.pyapi.decref(jbf__gvwo)
    rgubz__jmbrh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(bln__hec._getvalue(), is_error=rgubz__jmbrh)


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
    yajj__ixzku, xtpun__izzmz = divmod(a, b)
    xtpun__izzmz *= 2
    muss__zdk = xtpun__izzmz > b if b > 0 else xtpun__izzmz < b
    if muss__zdk or xtpun__izzmz == b and yajj__ixzku % 2 == 1:
        yajj__ixzku += 1
    return yajj__ixzku


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
                wjd__hwdq = _cmp(_getstate(lhs), _getstate(rhs))
                return op(wjd__hwdq, 0)
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
            yajj__ixzku, xtpun__izzmz = divmod(_to_microseconds(lhs),
                _to_microseconds(rhs))
            return yajj__ixzku, datetime.timedelta(0, 0, xtpun__izzmz)
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
    xgmb__jtnct = datetime.timedelta(0)

    def impl(timedelta):
        return timedelta != xgmb__jtnct
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
        khwro__sqjds = [('days_data', days_data_type), ('seconds_data',
            seconds_data_type), ('microseconds_data',
            microseconds_data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, khwro__sqjds)


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
    mtq__aeb = types.Array(types.intp, 1, 'C')
    lfebf__ikb = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        mtq__aeb, [n])
    mtbjv__ovkni = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        mtq__aeb, [n])
    gyr__klu = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        mtq__aeb, [n])
    xev__nqw = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64),
        7)), lir.Constant(lir.IntType(64), 8))
    odtkn__gniyy = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [xev__nqw])
    pyvr__tierq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64), lir.IntType(64).as_pointer(), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (8).as_pointer()])
    xdvot__awec = cgutils.get_or_insert_function(c.builder.module,
        pyvr__tierq, name='unbox_datetime_timedelta_array')
    c.builder.call(xdvot__awec, [val, n, lfebf__ikb.data, mtbjv__ovkni.data,
        gyr__klu.data, odtkn__gniyy.data])
    uiywd__kfz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    uiywd__kfz.days_data = lfebf__ikb._getvalue()
    uiywd__kfz.seconds_data = mtbjv__ovkni._getvalue()
    uiywd__kfz.microseconds_data = gyr__klu._getvalue()
    uiywd__kfz.null_bitmap = odtkn__gniyy._getvalue()
    rgubz__jmbrh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(uiywd__kfz._getvalue(), is_error=rgubz__jmbrh)


@box(DatetimeTimeDeltaArrayType)
def box_datetime_timedelta_array(typ, val, c):
    qxqg__qvcw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    lfebf__ikb = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qxqg__qvcw.days_data)
    mtbjv__ovkni = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
        .context, c.builder, qxqg__qvcw.seconds_data).data
    gyr__klu = c.context.make_array(types.Array(types.int64, 1, 'C'))(c.
        context, c.builder, qxqg__qvcw.microseconds_data).data
    taafk__ifutn = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, qxqg__qvcw.null_bitmap).data
    n = c.builder.extract_value(lfebf__ikb.shape, 0)
    pyvr__tierq = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), lir.
        IntType(64).as_pointer(), lir.IntType(64).as_pointer(), lir.IntType
        (64).as_pointer(), lir.IntType(8).as_pointer()])
    zzedw__mxls = cgutils.get_or_insert_function(c.builder.module,
        pyvr__tierq, name='box_datetime_timedelta_array')
    lxa__uecwm = c.builder.call(zzedw__mxls, [n, lfebf__ikb.data,
        mtbjv__ovkni, gyr__klu, taafk__ifutn])
    c.context.nrt.decref(c.builder, typ, val)
    return lxa__uecwm


@intrinsic
def init_datetime_timedelta_array(typingctx, days_data, seconds_data,
    microseconds_data, nulls=None):
    assert days_data == types.Array(types.int64, 1, 'C')
    assert seconds_data == types.Array(types.int64, 1, 'C')
    assert microseconds_data == types.Array(types.int64, 1, 'C')
    assert nulls == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        nfh__wucs, wgyek__tokw, ixd__rwksq, wfg__luvfs = args
        irfj__saq = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        irfj__saq.days_data = nfh__wucs
        irfj__saq.seconds_data = wgyek__tokw
        irfj__saq.microseconds_data = ixd__rwksq
        irfj__saq.null_bitmap = wfg__luvfs
        context.nrt.incref(builder, signature.args[0], nfh__wucs)
        context.nrt.incref(builder, signature.args[1], wgyek__tokw)
        context.nrt.incref(builder, signature.args[2], ixd__rwksq)
        context.nrt.incref(builder, signature.args[3], wfg__luvfs)
        return irfj__saq._getvalue()
    iasb__fww = datetime_timedelta_array_type(days_data, seconds_data,
        microseconds_data, nulls)
    return iasb__fww, codegen


@lower_constant(DatetimeTimeDeltaArrayType)
def lower_constant_datetime_timedelta_arr(context, builder, typ, pyval):
    n = len(pyval)
    lfebf__ikb = np.empty(n, np.int64)
    mtbjv__ovkni = np.empty(n, np.int64)
    gyr__klu = np.empty(n, np.int64)
    yio__lacs = np.empty(n + 7 >> 3, np.uint8)
    for ggfe__jnjn, s in enumerate(pyval):
        ovcl__pfc = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(yio__lacs, ggfe__jnjn, int(not
            ovcl__pfc))
        if not ovcl__pfc:
            lfebf__ikb[ggfe__jnjn] = s.days
            mtbjv__ovkni[ggfe__jnjn] = s.seconds
            gyr__klu[ggfe__jnjn] = s.microseconds
    wlhoj__ziyh = context.get_constant_generic(builder, days_data_type,
        lfebf__ikb)
    vtym__nahh = context.get_constant_generic(builder, seconds_data_type,
        mtbjv__ovkni)
    pcyo__lvhdk = context.get_constant_generic(builder,
        microseconds_data_type, gyr__klu)
    mpgem__dabwt = context.get_constant_generic(builder, nulls_type, yio__lacs)
    return lir.Constant.literal_struct([wlhoj__ziyh, vtym__nahh,
        pcyo__lvhdk, mpgem__dabwt])


@numba.njit(no_cpython_wrapper=True)
def alloc_datetime_timedelta_array(n):
    lfebf__ikb = np.empty(n, dtype=np.int64)
    mtbjv__ovkni = np.empty(n, dtype=np.int64)
    gyr__klu = np.empty(n, dtype=np.int64)
    nulls = np.full(n + 7 >> 3, 255, np.uint8)
    return init_datetime_timedelta_array(lfebf__ikb, mtbjv__ovkni, gyr__klu,
        nulls)


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
            rax__lxome = bodo.utils.conversion.coerce_to_ndarray(ind)
            xqp__yezte = A._null_bitmap
            svea__qcf = A._days_data[rax__lxome]
            zwcz__szc = A._seconds_data[rax__lxome]
            ify__mhwb = A._microseconds_data[rax__lxome]
            n = len(svea__qcf)
            xxduj__fsu = get_new_null_mask_bool_index(xqp__yezte, ind, n)
            return init_datetime_timedelta_array(svea__qcf, zwcz__szc,
                ify__mhwb, xxduj__fsu)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            rax__lxome = bodo.utils.conversion.coerce_to_ndarray(ind)
            xqp__yezte = A._null_bitmap
            svea__qcf = A._days_data[rax__lxome]
            zwcz__szc = A._seconds_data[rax__lxome]
            ify__mhwb = A._microseconds_data[rax__lxome]
            n = len(svea__qcf)
            xxduj__fsu = get_new_null_mask_int_index(xqp__yezte, rax__lxome, n)
            return init_datetime_timedelta_array(svea__qcf, zwcz__szc,
                ify__mhwb, xxduj__fsu)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            n = len(A._days_data)
            xqp__yezte = A._null_bitmap
            svea__qcf = np.ascontiguousarray(A._days_data[ind])
            zwcz__szc = np.ascontiguousarray(A._seconds_data[ind])
            ify__mhwb = np.ascontiguousarray(A._microseconds_data[ind])
            xxduj__fsu = get_new_null_mask_slice_index(xqp__yezte, ind, n)
            return init_datetime_timedelta_array(svea__qcf, zwcz__szc,
                ify__mhwb, xxduj__fsu)
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
    suj__mdmjd = (
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
            raise BodoError(suj__mdmjd)
    if not (is_iterable_type(val) and val.dtype == bodo.
        datetime_timedelta_type or types.unliteral(val) ==
        datetime_timedelta_type):
        raise BodoError(suj__mdmjd)
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_arr_ind_scalar(A, ind, val):
                n = len(A)
                for ggfe__jnjn in range(n):
                    A._days_data[ind[ggfe__jnjn]] = val._days
                    A._seconds_data[ind[ggfe__jnjn]] = val._seconds
                    A._microseconds_data[ind[ggfe__jnjn]] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[ggfe__jnjn], 1)
            return impl_arr_ind_scalar
        else:

            def impl_arr_ind(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(val._days_data)
                for ggfe__jnjn in range(n):
                    A._days_data[ind[ggfe__jnjn]] = val._days_data[ggfe__jnjn]
                    A._seconds_data[ind[ggfe__jnjn]] = val._seconds_data[
                        ggfe__jnjn]
                    A._microseconds_data[ind[ggfe__jnjn]
                        ] = val._microseconds_data[ggfe__jnjn]
                    cxdvb__ncpb = bodo.libs.int_arr_ext.get_bit_bitmap_arr(val
                        ._null_bitmap, ggfe__jnjn)
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ind[ggfe__jnjn], cxdvb__ncpb)
            return impl_arr_ind
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_bool_ind_mask_scalar(A, ind, val):
                n = len(ind)
                for ggfe__jnjn in range(n):
                    if not bodo.libs.array_kernels.isna(ind, ggfe__jnjn
                        ) and ind[ggfe__jnjn]:
                        A._days_data[ggfe__jnjn] = val._days
                        A._seconds_data[ggfe__jnjn] = val._seconds
                        A._microseconds_data[ggfe__jnjn] = val._microseconds
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            ggfe__jnjn, 1)
            return impl_bool_ind_mask_scalar
        else:

            def impl_bool_ind_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(ind)
                kzti__bqva = 0
                for ggfe__jnjn in range(n):
                    if not bodo.libs.array_kernels.isna(ind, ggfe__jnjn
                        ) and ind[ggfe__jnjn]:
                        A._days_data[ggfe__jnjn] = val._days_data[kzti__bqva]
                        A._seconds_data[ggfe__jnjn] = val._seconds_data[
                            kzti__bqva]
                        A._microseconds_data[ggfe__jnjn
                            ] = val._microseconds_data[kzti__bqva]
                        cxdvb__ncpb = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                            val._null_bitmap, kzti__bqva)
                        bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                            ggfe__jnjn, cxdvb__ncpb)
                        kzti__bqva += 1
            return impl_bool_ind_mask
    if isinstance(ind, types.SliceType):
        if types.unliteral(val) == datetime_timedelta_type:

            def impl_slice_scalar(A, ind, val):
                dyh__mktdj = numba.cpython.unicode._normalize_slice(ind, len(A)
                    )
                for ggfe__jnjn in range(dyh__mktdj.start, dyh__mktdj.stop,
                    dyh__mktdj.step):
                    A._days_data[ggfe__jnjn] = val._days
                    A._seconds_data[ggfe__jnjn] = val._seconds
                    A._microseconds_data[ggfe__jnjn] = val._microseconds
                    bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap,
                        ggfe__jnjn, 1)
            return impl_slice_scalar
        else:

            def impl_slice_mask(A, ind, val):
                val = bodo.utils.conversion.coerce_to_array(val,
                    use_nullable_array=True)
                n = len(A._days_data)
                A._days_data[ind] = val._days_data
                A._seconds_data[ind] = val._seconds_data
                A._microseconds_data[ind] = val._microseconds_data
                lyr__qtd = val._null_bitmap.copy()
                setitem_slice_index_null_bits(A._null_bitmap, lyr__qtd, ind, n)
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
            qxqg__qvcw = arg1
            numba.parfors.parfor.init_prange()
            n = len(qxqg__qvcw)
            A = alloc_datetime_timedelta_array(n)
            for ggfe__jnjn in numba.parfors.parfor.internal_prange(n):
                A[ggfe__jnjn] = qxqg__qvcw[ggfe__jnjn] - arg2
            return A
        return impl


def create_cmp_op_overload_arr(op):

    def overload_date_arr_cmp(lhs, rhs):
        if op == operator.ne:
            urpf__bgp = True
        else:
            urpf__bgp = False
        if (lhs == datetime_timedelta_array_type and rhs ==
            datetime_timedelta_array_type):

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                zte__suksk = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ggfe__jnjn in numba.parfors.parfor.internal_prange(n):
                    nrb__mdnie = bodo.libs.array_kernels.isna(lhs, ggfe__jnjn)
                    rbm__ilmqa = bodo.libs.array_kernels.isna(rhs, ggfe__jnjn)
                    if nrb__mdnie or rbm__ilmqa:
                        ryuo__uwr = urpf__bgp
                    else:
                        ryuo__uwr = op(lhs[ggfe__jnjn], rhs[ggfe__jnjn])
                    zte__suksk[ggfe__jnjn] = ryuo__uwr
                return zte__suksk
            return impl
        elif lhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                zte__suksk = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ggfe__jnjn in numba.parfors.parfor.internal_prange(n):
                    cxdvb__ncpb = bodo.libs.array_kernels.isna(lhs, ggfe__jnjn)
                    if cxdvb__ncpb:
                        ryuo__uwr = urpf__bgp
                    else:
                        ryuo__uwr = op(lhs[ggfe__jnjn], rhs)
                    zte__suksk[ggfe__jnjn] = ryuo__uwr
                return zte__suksk
            return impl
        elif rhs == datetime_timedelta_array_type:

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                n = len(rhs)
                zte__suksk = bodo.libs.bool_arr_ext.alloc_bool_array(n)
                for ggfe__jnjn in numba.parfors.parfor.internal_prange(n):
                    cxdvb__ncpb = bodo.libs.array_kernels.isna(rhs, ggfe__jnjn)
                    if cxdvb__ncpb:
                        ryuo__uwr = urpf__bgp
                    else:
                        ryuo__uwr = op(lhs, rhs[ggfe__jnjn])
                    zte__suksk[ggfe__jnjn] = ryuo__uwr
                return zte__suksk
            return impl
    return overload_date_arr_cmp


timedelta_unsupported_attrs = ['asm8', 'resolution_string', 'freq',
    'is_populated']
timedelta_unsupported_methods = ['isoformat']


def _intstall_pd_timedelta_unsupported():
    from bodo.utils.typing import create_unsupported_overload
    for yusg__fyh in timedelta_unsupported_attrs:
        rru__suimo = 'pandas.Timedelta.' + yusg__fyh
        overload_attribute(PDTimeDeltaType, yusg__fyh)(
            create_unsupported_overload(rru__suimo))
    for vcrf__rytb in timedelta_unsupported_methods:
        rru__suimo = 'pandas.Timedelta.' + vcrf__rytb
        overload_method(PDTimeDeltaType, vcrf__rytb)(
            create_unsupported_overload(rru__suimo + '()'))


_intstall_pd_timedelta_unsupported()
