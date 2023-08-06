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
    xkzo__wtjbb = context.get_python_api(builder)
    return xkzo__wtjbb.unserialize(xkzo__wtjbb.serialize_object(pyval))


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
        mxq__yucyw = ', '.join('e{}'.format(xmb__vun) for xmb__vun in range
            (len(args)))
        if mxq__yucyw:
            mxq__yucyw += ', '
        uleip__liefq = ', '.join("{} = ''".format(kfioo__vzs) for
            kfioo__vzs in kws.keys())
        guf__umee = f'def format_stub(string, {mxq__yucyw} {uleip__liefq}):\n'
        guf__umee += '    pass\n'
        yifnz__hyygs = {}
        exec(guf__umee, {}, yifnz__hyygs)
        bbvwu__deea = yifnz__hyygs['format_stub']
        lhim__pstzi = numba.core.utils.pysignature(bbvwu__deea)
        kiwap__vleed = (logger_typ,) + args + tuple(kws.values())
        return signature(logger_typ, kiwap__vleed).replace(pysig=lhim__pstzi)
    func_names = ('debug', 'warning', 'warn', 'info', 'error', 'exception',
        'critical', 'log', 'setLevel')
    for bjigi__wcit in ('logging.Logger', 'logging.RootLogger'):
        for tftb__xqg in func_names:
            bwzpc__vdoxj = f'@bound_function("{bjigi__wcit}.{tftb__xqg}")\n'
            bwzpc__vdoxj += (
                f'def resolve_{tftb__xqg}(self, logger_typ, args, kws):\n')
            bwzpc__vdoxj += (
                '    return self._resolve_helper(logger_typ, args, kws)')
            exec(bwzpc__vdoxj)


logging_logger_unsupported_attrs = {'filters', 'handlers', 'manager'}
logging_logger_unsupported_methods = {'addHandler', 'callHandlers', 'fatal',
    'findCaller', 'getChild', 'getEffectiveLevel', 'handle', 'hasHandlers',
    'isEnabledFor', 'makeRecord', 'removeHandler'}


def _install_logging_logger_unsupported_objects():
    for asgo__thx in logging_logger_unsupported_attrs:
        pksr__vhajw = 'logging.Logger.' + asgo__thx
        overload_attribute(LoggingLoggerType, asgo__thx)(
            create_unsupported_overload(pksr__vhajw))
    for hmlr__exg in logging_logger_unsupported_methods:
        pksr__vhajw = 'logging.Logger.' + hmlr__exg
        overload_method(LoggingLoggerType, hmlr__exg)(
            create_unsupported_overload(pksr__vhajw))


_install_logging_logger_unsupported_objects()
