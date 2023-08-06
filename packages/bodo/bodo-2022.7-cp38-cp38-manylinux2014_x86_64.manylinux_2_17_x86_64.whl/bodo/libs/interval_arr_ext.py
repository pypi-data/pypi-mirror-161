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
        qscak__giyf = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, qscak__giyf)


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
        ktjh__pwol, vvbc__errb = args
        ozl__pxi = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        ozl__pxi.left = ktjh__pwol
        ozl__pxi.right = vvbc__errb
        context.nrt.incref(builder, signature.args[0], ktjh__pwol)
        context.nrt.incref(builder, signature.args[1], vvbc__errb)
        return ozl__pxi._getvalue()
    onqc__tkmg = IntervalArrayType(left)
    pmel__lbcb = onqc__tkmg(left, right)
    return pmel__lbcb, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    bcszt__bmi = []
    for ufcu__haae in args:
        ejf__pil = equiv_set.get_shape(ufcu__haae)
        if ejf__pil is not None:
            bcszt__bmi.append(ejf__pil[0])
    if len(bcszt__bmi) > 1:
        equiv_set.insert_equiv(*bcszt__bmi)
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
    ozl__pxi = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, ozl__pxi.left)
    plgv__uopk = c.pyapi.from_native_value(typ.arr_type, ozl__pxi.left, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, ozl__pxi.right)
    pbscj__pjuf = c.pyapi.from_native_value(typ.arr_type, ozl__pxi.right, c
        .env_manager)
    maerp__moo = c.context.insert_const_string(c.builder.module, 'pandas')
    pkken__fqtyi = c.pyapi.import_module_noblock(maerp__moo)
    eviu__qll = c.pyapi.object_getattr_string(pkken__fqtyi, 'arrays')
    plo__pjvna = c.pyapi.object_getattr_string(eviu__qll, 'IntervalArray')
    nowwz__vjg = c.pyapi.call_method(plo__pjvna, 'from_arrays', (plgv__uopk,
        pbscj__pjuf))
    c.pyapi.decref(plgv__uopk)
    c.pyapi.decref(pbscj__pjuf)
    c.pyapi.decref(pkken__fqtyi)
    c.pyapi.decref(eviu__qll)
    c.pyapi.decref(plo__pjvna)
    c.context.nrt.decref(c.builder, typ, val)
    return nowwz__vjg


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    plgv__uopk = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, plgv__uopk).value
    c.pyapi.decref(plgv__uopk)
    pbscj__pjuf = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, pbscj__pjuf).value
    c.pyapi.decref(pbscj__pjuf)
    ozl__pxi = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ozl__pxi.left = left
    ozl__pxi.right = right
    ild__giun = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ozl__pxi._getvalue(), is_error=ild__giun)


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
