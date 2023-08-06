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
    shu__ywuy = context.get_python_api(builder)
    return shu__ywuy.unserialize(shu__ywuy.serialize_object(pyval))


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
        wvlz__qwofo = ', '.join('e{}'.format(zfp__aejwh) for zfp__aejwh in
            range(len(args)))
        if wvlz__qwofo:
            wvlz__qwofo += ', '
        wisfi__nkz = ', '.join("{} = ''".format(rguc__olipj) for
            rguc__olipj in kws.keys())
        bedvi__xnc = f'def format_stub(string, {wvlz__qwofo} {wisfi__nkz}):\n'
        bedvi__xnc += '    pass\n'
        xzv__uarej = {}
        exec(bedvi__xnc, {}, xzv__uarej)
        disp__gexv = xzv__uarej['format_stub']
        oaqzl__bym = numba.core.utils.pysignature(disp__gexv)
        nhk__hqra = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, nhk__hqra).replace(pysig=oaqzl__bym)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for tunzn__lnp in ('logging.Logger', 'logging.RootLogger'):
        for yir__xlnzf in func_names:
            fpqx__vdd = f'@bound_function("{tunzn__lnp}.{yir__xlnzf}")\n'
            fpqx__vdd += (
                f'def resolve_{yir__xlnzf}(self, logger_typ, args, kws):\n')
            fpqx__vdd += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(fpqx__vdd)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for ixzgr__pbv in logging_logger_unsupported_attrs:
        jpl__kktnp = 'logging.Logger.' + ixzgr__pbv
        overload_attribute(LoggingLoggerType, ixzgr__pbv)(
            create_unsupported_overload(jpl__kktnp))
    for voklx__xrnvm in logging_logger_unsupported_methods:
        jpl__kktnp = 'logging.Logger.' + voklx__xrnvm
        overload_method(LoggingLoggerType, voklx__xrnvm)(
            create_unsupported_overload(jpl__kktnp))


_install_logging_logger_unsupported_objects()
