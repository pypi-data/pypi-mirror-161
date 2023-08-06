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
        meuyl__bhvhu = [('left', fe_type.arr_type), ('right', fe_type.arr_type)
            ]
        models.StructModel.__init__(self, dmm, fe_type, meuyl__bhvhu)


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
        pcadw__vkq, oyu__vddzq = args
        cslmo__ffczv = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        cslmo__ffczv.left = pcadw__vkq
        cslmo__ffczv.right = oyu__vddzq
        context.nrt.incref(builder, signature.args[0], pcadw__vkq)
        context.nrt.incref(builder, signature.args[1], oyu__vddzq)
        return cslmo__ffczv._getvalue()
    kqjv__nlk = IntervalArrayType(left)
    ignyu__vefv = kqjv__nlk(left, right)
    return ignyu__vefv, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    lfy__omfr = []
    for sxe__cgwg in args:
        llx__afjh = equiv_set.get_shape(sxe__cgwg)
        if llx__afjh is not None:
            lfy__omfr.append(llx__afjh[0])
    if len(lfy__omfr) > 1:
        equiv_set.insert_equiv(*lfy__omfr)
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
    cslmo__ffczv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, cslmo__ffczv.left)
    vkwa__cooe = c.pyapi.from_native_value(typ.arr_type, cslmo__ffczv.left,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, cslmo__ffczv.right)
    awwqy__rcrg = c.pyapi.from_native_value(typ.arr_type, cslmo__ffczv.
        right, c.env_manager)
    sbl__ieop = c.context.insert_const_string(c.builder.module, 'pandas')
    ezz__wxyfp = c.pyapi.import_module_noblock(sbl__ieop)
    are__esrj = c.pyapi.object_getattr_string(ezz__wxyfp, 'arrays')
    egt__mdleo = c.pyapi.object_getattr_string(are__esrj, 'IntervalArray')
    siaoj__ryk = c.pyapi.call_method(egt__mdleo, 'from_arrays', (vkwa__cooe,
        awwqy__rcrg))
    c.pyapi.decref(vkwa__cooe)
    c.pyapi.decref(awwqy__rcrg)
    c.pyapi.decref(ezz__wxyfp)
    c.pyapi.decref(are__esrj)
    c.pyapi.decref(egt__mdleo)
    c.context.nrt.decref(c.builder, typ, val)
    return siaoj__ryk


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    vkwa__cooe = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, vkwa__cooe).value
    c.pyapi.decref(vkwa__cooe)
    awwqy__rcrg = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, awwqy__rcrg).value
    c.pyapi.decref(awwqy__rcrg)
    cslmo__ffczv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    cslmo__ffczv.left = left
    cslmo__ffczv.right = right
    mxfv__ugnzb = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cslmo__ffczv._getvalue(), is_error=mxfv__ugnzb)


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
