from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    oid__iyk = f'class {class_name}(types.Opaque):\n'
    oid__iyk += f'    def __init__(self):\n'
    oid__iyk += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    oid__iyk += f'    def __reduce__(self):\n'
    oid__iyk += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    fcz__ktj = {}
    exec(oid__iyk, {'types': types, 'models': models}, fcz__ktj)
    jziu__vgbo = fcz__ktj[class_name]
    setattr(module, class_name, jziu__vgbo)
    class_instance = jziu__vgbo()
    setattr(types, types_name, class_instance)
    oid__iyk = f'class {model_name}(models.StructModel):\n'
    oid__iyk += f'    def __init__(self, dmm, fe_type):\n'
    oid__iyk += f'        members = [\n'
    oid__iyk += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    oid__iyk += f"            ('pyobj', types.voidptr),\n"
    oid__iyk += f'        ]\n'
    oid__iyk += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(oid__iyk, {'types': types, 'models': models, types_name:
        class_instance}, fcz__ktj)
    ojg__xxwqd = fcz__ktj[model_name]
    setattr(module, model_name, ojg__xxwqd)
    register_model(jziu__vgbo)(ojg__xxwqd)
    make_attribute_wrapper(jziu__vgbo, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(jziu__vgbo)(unbox_py_obj)
    box(jziu__vgbo)(box_py_obj)
    return jziu__vgbo


def box_py_obj(typ, val, c):
    ccda__pkbcl = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = ccda__pkbcl.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    ccda__pkbcl = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ccda__pkbcl.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    ccda__pkbcl.pyobj = obj
    return NativeValue(ccda__pkbcl._getvalue())
