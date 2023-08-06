"""
Array of intervals corresponding to IntervalArray of Pandas.
Used for IntervalIndex, which is necessary for Series.value_counts() with 'bins'
argument.
"""
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo


class IntervalType(types.Type):

    def __init__(self):
        super(IntervalType, self).__init__('IntervalType()')


class IntervalArrayType(types.ArrayCompatible):

    def __init__(self, arr_type):
        self.arr_type = arr_type
        self.dtype = IntervalType()
        super(IntervalArrayType, self).__init__(name=
            f'IntervalArrayType({arr_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntervalArrayType(self.arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(IntervalArrayType)
class IntervalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yljav__nvyz = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, yljav__nvyz)


make_attribute_wrapper(IntervalArrayType, 'left', '_left')
make_attribute_wrapper(IntervalArrayType, 'right', '_right')


@typeof_impl.register(pd.arrays.IntervalArray)
def typeof_interval_array(val, c):
    arr_type = bodo.typeof(val._left)
    return IntervalArrayType(arr_type)


@intrinsic
def init_interval_array(typingctx, left, right=None):
    assert left == right, 'Interval left/right array types should be the same'

    def codegen(context, builder, signature, args):
        xcaxl__wigoc, jhzci__ohe = args
        jzx__ptnx = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        jzx__ptnx.left = xcaxl__wigoc
        jzx__ptnx.right = jhzci__ohe
        context.nrt.incref(builder, signature.args[0], xcaxl__wigoc)
        context.nrt.incref(builder, signature.args[1], jhzci__ohe)
        return jzx__ptnx._getvalue()
    qtvrw__por = IntervalArrayType(left)
    nypq__igxn = qtvrw__por(left, right)
    return nypq__igxn, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    glio__jyls = []
    for eug__ptxw in args:
        taohq__wrc = equiv_set.get_shape(eug__ptxw)
        if taohq__wrc is not None:
            glio__jyls.append(taohq__wrc[0])
    if len(glio__jyls) > 1:
        equiv_set.insert_equiv(*glio__jyls)
    left = args[0]
    if equiv_set.has_shape(left):
        return ArrayAnalysis.AnalyzeResult(shape=left, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_libs_interval_arr_ext_init_interval_array
    ) = init_interval_array_equiv


def alias_ext_init_interval_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_interval_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_interval_array


@box(IntervalArrayType)
def box_interval_arr(typ, val, c):
    jzx__ptnx = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, jzx__ptnx.left)
    lpmfq__ark = c.pyapi.from_native_value(typ.arr_type, jzx__ptnx.left, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, jzx__ptnx.right)
    wfx__snth = c.pyapi.from_native_value(typ.arr_type, jzx__ptnx.right, c.
        env_manager)
    uuqv__mckv = c.context.insert_const_string(c.builder.module, 'pandas')
    ayq__qoms = c.pyapi.import_module_noblock(uuqv__mckv)
    mdibw__xfhbg = c.pyapi.object_getattr_string(ayq__qoms, 'arrays')
    usndf__ddgia = c.pyapi.object_getattr_string(mdibw__xfhbg, 'IntervalArray')
    qmx__yejw = c.pyapi.call_method(usndf__ddgia, 'from_arrays', (
        lpmfq__ark, wfx__snth))
    c.pyapi.decref(lpmfq__ark)
    c.pyapi.decref(wfx__snth)
    c.pyapi.decref(ayq__qoms)
    c.pyapi.decref(mdibw__xfhbg)
    c.pyapi.decref(usndf__ddgia)
    c.context.nrt.decref(c.builder, typ, val)
    return qmx__yejw


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    lpmfq__ark = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, lpmfq__ark).value
    c.pyapi.decref(lpmfq__ark)
    wfx__snth = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, wfx__snth).value
    c.pyapi.decref(wfx__snth)
    jzx__ptnx = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jzx__ptnx.left = left
    jzx__ptnx.right = right
    pncqn__dfow = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jzx__ptnx._getvalue(), is_error=pncqn__dfow)


@overload(len, no_unliteral=True)
def overload_interval_arr_len(A):
    if isinstance(A, IntervalArrayType):
        return lambda A: len(A._left)


@overload_attribute(IntervalArrayType, 'shape')
def overload_interval_arr_shape(A):
    return lambda A: (len(A._left),)


@overload_attribute(IntervalArrayType, 'ndim')
def overload_interval_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntervalArrayType, 'nbytes')
def overload_interval_arr_nbytes(A):
    return lambda A: A._left.nbytes + A._right.nbytes


@overload_method(IntervalArrayType, 'copy', no_unliteral=True)
def overload_interval_arr_copy(A):
    return lambda A: bodo.libs.interval_arr_ext.init_interval_array(A._left
        .copy(), A._right.copy())
