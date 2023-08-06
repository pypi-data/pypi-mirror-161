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
    qivr__afukl = context.get_python_api(builder)
    return qivr__afukl.unserialize(qivr__afukl.serialize_object(pyval))


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
        fxgqa__kurou = ', '.join('e{}'.format(imk__lkwwo) for imk__lkwwo in
            range(len(args)))
        if fxgqa__kurou:
            fxgqa__kurou += ', '
        ykage__qlh = ', '.join("{} = ''".format(bxb__rua) for bxb__rua in
            kws.keys())
        rcqkt__mpie = (
            f'def format_stub(string, {fxgqa__kurou} {ykage__qlh}):\n')
        rcqkt__mpie += '    pass\n'
        yij__dqrkb = {}
        exec(rcqkt__mpie, {}, yij__dqrkb)
        uqimn__gfwm = yij__dqrkb['format_stub']
        nqupu__ymn = numba.core.utils.pysignature(uqimn__gfwm)
        zws__enyyu = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, zws__enyyu).replace(pysig=nqupu__ymn)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for yibbw__mbopw in ('logging.Logger', 'logging.RootLogger'):
        for ely__rem in func_names:
            ujhzs__fsd = f'@bound_function("{yibbw__mbopw}.{ely__rem}")\n'
            ujhzs__fsd += (
                f'def resolve_{ely__rem}(self, logger_typ, args, kws):\n')
            ujhzs__fsd += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(ujhzs__fsd)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for gcvn__szxf in logging_logger_unsupported_attrs:
        jwnmx__kkn = 'logging.Logger.' + gcvn__szxf
        overload_attribute(LoggingLoggerType, gcvn__szxf)(
            create_unsupported_overload(jwnmx__kkn))
    for ambu__ppbhv in logging_logger_unsupported_methods:
        jwnmx__kkn = 'logging.Logger.' + ambu__ppbhv
        overload_method(LoggingLoggerType, ambu__ppbhv)(
            create_unsupported_overload(jwnmx__kkn))


_install_logging_logger_unsupported_objects()
