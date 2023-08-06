from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    owdv__nvbvj = f'class {class_name}(types.Opaque):\n'
    owdv__nvbvj += f'    def __init__(self):\n'
    owdv__nvbvj += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    owdv__nvbvj += f'    def __reduce__(self):\n'
    owdv__nvbvj += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    yjugi__dff = {}
    exec(owdv__nvbvj, {'types': types, 'models': models}, yjugi__dff)
    yzd__ksslu = yjugi__dff[class_name]
    setattr(module, class_name, yzd__ksslu)
    class_instance = yzd__ksslu()
    setattr(types, types_name, class_instance)
    owdv__nvbvj = f'class {model_name}(models.StructModel):\n'
    owdv__nvbvj += f'    def __init__(self, dmm, fe_type):\n'
    owdv__nvbvj += f'        members = [\n'
    owdv__nvbvj += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    owdv__nvbvj += f"            ('pyobj', types.voidptr),\n"
    owdv__nvbvj += f'        ]\n'
    owdv__nvbvj += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(owdv__nvbvj, {'types': types, 'models': models, types_name:
        class_instance}, yjugi__dff)
    rrg__mep = yjugi__dff[model_name]
    setattr(module, model_name, rrg__mep)
    register_model(yzd__ksslu)(rrg__mep)
    make_attribute_wrapper(yzd__ksslu, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(yzd__ksslu)(unbox_py_obj)
    box(yzd__ksslu)(box_py_obj)
    return yzd__ksslu


def box_py_obj(typ, val, c):
    mlql__oyl = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = mlql__oyl.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    mlql__oyl = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mlql__oyl.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    mlql__oyl.pyobj = obj
    return NativeValue(mlql__oyl._getvalue())
