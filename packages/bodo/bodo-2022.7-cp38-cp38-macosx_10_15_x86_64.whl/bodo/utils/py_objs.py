from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    xfyn__cdob = f'class {class_name}(types.Opaque):\n'
    xfyn__cdob += f'    def __init__(self):\n'
    xfyn__cdob += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    xfyn__cdob += f'    def __reduce__(self):\n'
    xfyn__cdob += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    wtius__fsab = {}
    exec(xfyn__cdob, {'types': types, 'models': models}, wtius__fsab)
    iksw__drur = wtius__fsab[class_name]
    setattr(module, class_name, iksw__drur)
    class_instance = iksw__drur()
    setattr(types, types_name, class_instance)
    xfyn__cdob = f'class {model_name}(models.StructModel):\n'
    xfyn__cdob += f'    def __init__(self, dmm, fe_type):\n'
    xfyn__cdob += f'        members = [\n'
    xfyn__cdob += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    xfyn__cdob += f"            ('pyobj', types.voidptr),\n"
    xfyn__cdob += f'        ]\n'
    xfyn__cdob += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(xfyn__cdob, {'types': types, 'models': models, types_name:
        class_instance}, wtius__fsab)
    wdi__vxp = wtius__fsab[model_name]
    setattr(module, model_name, wdi__vxp)
    register_model(iksw__drur)(wdi__vxp)
    make_attribute_wrapper(iksw__drur, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(iksw__drur)(unbox_py_obj)
    box(iksw__drur)(box_py_obj)
    return iksw__drur


def box_py_obj(typ, val, c):
    lagy__omayw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = lagy__omayw.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    lagy__omayw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    lagy__omayw.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    lagy__omayw.pyobj = obj
    return NativeValue(lagy__omayw._getvalue())
