from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    cbyd__jsm = f'class {class_name}(types.Opaque):\n'
    cbyd__jsm += f'    def __init__(self):\n'
    cbyd__jsm += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    cbyd__jsm += f'    def __reduce__(self):\n'
    cbyd__jsm += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    yxjva__riqa = {}
    exec(cbyd__jsm, {'types': types, 'models': models}, yxjva__riqa)
    gxt__lnyy = yxjva__riqa[class_name]
    setattr(module, class_name, gxt__lnyy)
    class_instance = gxt__lnyy()
    setattr(types, types_name, class_instance)
    cbyd__jsm = f'class {model_name}(models.StructModel):\n'
    cbyd__jsm += f'    def __init__(self, dmm, fe_type):\n'
    cbyd__jsm += f'        members = [\n'
    cbyd__jsm += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    cbyd__jsm += f"            ('pyobj', types.voidptr),\n"
    cbyd__jsm += f'        ]\n'
    cbyd__jsm += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(cbyd__jsm, {'types': types, 'models': models, types_name:
        class_instance}, yxjva__riqa)
    kgav__mjy = yxjva__riqa[model_name]
    setattr(module, model_name, kgav__mjy)
    register_model(gxt__lnyy)(kgav__mjy)
    make_attribute_wrapper(gxt__lnyy, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(gxt__lnyy)(unbox_py_obj)
    box(gxt__lnyy)(box_py_obj)
    return gxt__lnyy


def box_py_obj(typ, val, c):
    gwc__rfsps = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = gwc__rfsps.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    gwc__rfsps = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    gwc__rfsps.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    gwc__rfsps.pyobj = obj
    return NativeValue(gwc__rfsps._getvalue())
