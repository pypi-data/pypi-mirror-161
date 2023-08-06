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
        jkbr__kyg = [('left', fe_type.arr_type), ('right', fe_type.arr_type)]
        models.StructModel.__init__(self, dmm, fe_type, jkbr__kyg)


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
        gfp__lovpv, ahre__dphjj = args
        ipj__aqd = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        ipj__aqd.left = gfp__lovpv
        ipj__aqd.right = ahre__dphjj
        context.nrt.incref(builder, signature.args[0], gfp__lovpv)
        context.nrt.incref(builder, signature.args[1], ahre__dphjj)
        return ipj__aqd._getvalue()
    xsl__bgey = IntervalArrayType(left)
    myr__yvudx = xsl__bgey(left, right)
    return myr__yvudx, codegen


def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    mua__rhkla = []
    for olhwd__onl in args:
        sdpdg__sgu = equiv_set.get_shape(olhwd__onl)
        if sdpdg__sgu is not None:
            mua__rhkla.append(sdpdg__sgu[0])
    if len(mua__rhkla) > 1:
        equiv_set.insert_equiv(*mua__rhkla)
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
    ipj__aqd = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.arr_type, ipj__aqd.left)
    xext__tixe = c.pyapi.from_native_value(typ.arr_type, ipj__aqd.left, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.arr_type, ipj__aqd.right)
    bqd__otud = c.pyapi.from_native_value(typ.arr_type, ipj__aqd.right, c.
        env_manager)
    izix__yrimj = c.context.insert_const_string(c.builder.module, 'pandas')
    dxicj__alp = c.pyapi.import_module_noblock(izix__yrimj)
    ejm__tgu = c.pyapi.object_getattr_string(dxicj__alp, 'arrays')
    gmujq__xme = c.pyapi.object_getattr_string(ejm__tgu, 'IntervalArray')
    cwi__ylpu = c.pyapi.call_method(gmujq__xme, 'from_arrays', (xext__tixe,
        bqd__otud))
    c.pyapi.decref(xext__tixe)
    c.pyapi.decref(bqd__otud)
    c.pyapi.decref(dxicj__alp)
    c.pyapi.decref(ejm__tgu)
    c.pyapi.decref(gmujq__xme)
    c.context.nrt.decref(c.builder, typ, val)
    return cwi__ylpu


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    xext__tixe = c.pyapi.object_getattr_string(val, '_left')
    left = c.pyapi.to_native_value(typ.arr_type, xext__tixe).value
    c.pyapi.decref(xext__tixe)
    bqd__otud = c.pyapi.object_getattr_string(val, '_right')
    right = c.pyapi.to_native_value(typ.arr_type, bqd__otud).value
    c.pyapi.decref(bqd__otud)
    ipj__aqd = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ipj__aqd.left = left
    ipj__aqd.right = right
    kys__sgqe = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ipj__aqd._getvalue(), is_error=kys__sgqe)


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
