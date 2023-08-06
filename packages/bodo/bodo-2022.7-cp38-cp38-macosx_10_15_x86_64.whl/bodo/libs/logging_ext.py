"""
JIT support for Python's logging module
"""
import logging
import numba
from numba.core import types
from numba.core.imputils import lower_constant
from numba.core.typing.templates import bound_function
from numba.core.typing.templates import AttributeTemplate, infer_getattr, signature
from numba.extending import NativeValue, box, models, overload_attribute, overload_method, register_model, typeof_impl, unbox
from bodo.utils.typing import create_unsupported_overload, gen_objmode_attr_overload


class LoggingLoggerType(types.Type):

    def __init__(self, is_root=False):
        self.is_root = is_root
        super(LoggingLoggerType, self).__init__(name=
            f'LoggingLoggerType(is_root={is_root})')


@typeof_impl.register(logging.RootLogger)
@typeof_impl.register(logging.Logger)
def typeof_logging(val, c):
    if isinstance(val, logging.RootLogger):
        return LoggingLoggerType(is_root=True)
    else:
        return LoggingLoggerType(is_root=False)


register_model(LoggingLoggerType)(models.OpaqueModel)


@box(LoggingLoggerType)
def box_logging_logger(typ, val, c):
    c.pyapi.incref(val)
    return val


@unbox(LoggingLoggerType)
def unbox_logging_logger(typ, obj, c):
    c.pyapi.incref(obj)
    return NativeValue(obj)


@lower_constant(LoggingLoggerType)
def lower_constant_logger(context, builder, ty, pyval):
    wmcgy__sxhx = context.get_python_api(builder)
    return wmcgy__sxhx.unserialize(wmcgy__sxhx.serialize_object(pyval))


gen_objmode_attr_overload(LoggingLoggerType, 'level', None, types.int64)
gen_objmode_attr_overload(LoggingLoggerType, 'name', None, 'unicode_type')
gen_objmode_attr_overload(LoggingLoggerType, 'propagate', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'disabled', None, types.boolean)
gen_objmode_attr_overload(LoggingLoggerType, 'parent', None,
    LoggingLoggerType())
gen_objmode_attr_overload(LoggingLoggerType, 'root', None,
    LoggingLoggerType(is_root=True))


@infer_getattr
class LoggingLoggerAttribute(AttributeTemplate):
    key = LoggingLoggerType

    def _resolve_helper(self, logger_typ, args, kws):
        kws = dict(kws)
        vhu__njabq = ', '.join('e{}'.format(iuv__lbdg) for iuv__lbdg in
            range(len(args)))
        if vhu__njabq:
            vhu__njabq += ', '
        xjf__lishj = ', '.join("{} = ''".format(ybwwb__qcfok) for
            ybwwb__qcfok in kws.keys())
        jldtn__jfzx = f'def format_stub(string, {vhu__njabq} {xjf__lishj}):\n'
        jldtn__jfzx += '    pass\n'
        ovcsl__nyn = {}
        exec(jldtn__jfzx, {}, ovcsl__nyn)
        yitn__osy = ovcsl__nyn['format_stub']
        pooip__xksf = numba.core.utils.pysignature(yitn__osy)
        boc__khdy = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, boc__khdy).replace(pysig=pooip__xksf)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for wckd__nfh in ('logging.Logger', 'logging.RootLogger'):
        for enxi__tcuey in func_names:
            lqm__wfqum = f'@bound_function("{wckd__nfh}.{enxi__tcuey}")\n'
            lqm__wfqum += (
                f'def resolve_{enxi__tcuey}(self, logger_typ, args, kws):\n')
            lqm__wfqum += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(lqm__wfqum)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for qctgq__ufw in logging_logger_unsupported_attrs:
        vch__nvx = 'logging.Logger.' + qctgq__ufw
        overload_attribute(LoggingLoggerType, qctgq__ufw)(
            create_unsupported_overload(vch__nvx))
    for qvv__jaj in logging_logger_unsupported_methods:
        vch__nvx = 'logging.Logger.' + qvv__jaj
        overload_method(LoggingLoggerType, qvv__jaj)(
            create_unsupported_overload(vch__nvx))


_install_logging_logger_unsupported_objects()
