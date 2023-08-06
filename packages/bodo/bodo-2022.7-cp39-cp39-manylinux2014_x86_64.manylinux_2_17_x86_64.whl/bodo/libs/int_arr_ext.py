"""Nullable integer array corresponding to Pandas IntegerArray.
However, nulls are stored in bit arrays similar to Arrow's arrays.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs.str_arr_ext import kBitmask
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('mask_arr_to_bitmap', hstr_ext.mask_arr_to_bitmap)
ll.add_symbol('is_pd_int_array', array_ext.is_pd_int_array)
ll.add_symbol('int_array_from_sequence', array_ext.int_array_from_sequence)
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, check_unsupported_args, is_iterable_type, is_list_like_index_type, is_overload_false, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error, to_nullable_type


class IntegerArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(IntegerArrayType, self).__init__(name=
            f'IntegerArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntegerArrayType(self.dtype)

    @property
    def get_pandas_scalar_type_instance(self):
        usc__kwgbm = int(np.log2(self.dtype.bitwidth // 8))
        slhq__jdimn = 0 if self.dtype.signed else 4
        idx = usc__kwgbm + slhq__jdimn
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        egdf__acyc = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, egdf__acyc)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    eivtx__skgpr = 8 * val.dtype.itemsize
    dymi__bufvp = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(dymi__bufvp, eivtx__skgpr))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        jceu__cepd = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(jceu__cepd)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    huc__rvyj = c.context.insert_const_string(c.builder.module, 'pandas')
    bnx__tni = c.pyapi.import_module_noblock(huc__rvyj)
    qucps__matud = c.pyapi.call_method(bnx__tni, str(typ)[:-2], ())
    c.pyapi.decref(bnx__tni)
    return qucps__matud


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    eivtx__skgpr = 8 * val.itemsize
    dymi__bufvp = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(dymi__bufvp, eivtx__skgpr))
    return IntDtype(dtype)


def _register_int_dtype(t):
    typeof_impl.register(t)(typeof_pd_int_dtype)
    int_dtype = typeof_pd_int_dtype(t(), None)
    type_callable(t)(lambda c: lambda : int_dtype)
    lower_builtin(t)(lambda c, b, s, a: c.get_dummy_value())


pd_int_dtype_classes = (pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.
    Int64Dtype, pd.UInt8Dtype, pd.UInt16Dtype, pd.UInt32Dtype, pd.UInt64Dtype)
for t in pd_int_dtype_classes:
    _register_int_dtype(t)


@numba.extending.register_jitable
def mask_arr_to_bitmap(mask_arr):
    n = len(mask_arr)
    musnt__nsrgm = n + 7 >> 3
    cfrhe__gyk = np.empty(musnt__nsrgm, np.uint8)
    for i in range(n):
        dbyxn__vou = i // 8
        cfrhe__gyk[dbyxn__vou] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            cfrhe__gyk[dbyxn__vou]) & kBitmask[i % 8]
    return cfrhe__gyk


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    bey__zgci = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(bey__zgci)
    c.pyapi.decref(bey__zgci)
    gwkyb__mujo = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    musnt__nsrgm = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType
        (64), 7)), lir.Constant(lir.IntType(64), 8))
    klc__mjr = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types.
        Array(types.uint8, 1, 'C'), [musnt__nsrgm])
    gnj__wby = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()])
    gwgtd__yis = cgutils.get_or_insert_function(c.builder.module, gnj__wby,
        name='is_pd_int_array')
    qpbj__hqi = c.builder.call(gwgtd__yis, [obj])
    dvnhu__awj = c.builder.icmp_unsigned('!=', qpbj__hqi, qpbj__hqi.type(0))
    with c.builder.if_else(dvnhu__awj) as (zabj__dogau, ifnz__cogjd):
        with zabj__dogau:
            hkc__jyc = c.pyapi.object_getattr_string(obj, '_data')
            gwkyb__mujo.data = c.pyapi.to_native_value(types.Array(typ.
                dtype, 1, 'C'), hkc__jyc).value
            uacg__fvnzn = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), uacg__fvnzn).value
            c.pyapi.decref(hkc__jyc)
            c.pyapi.decref(uacg__fvnzn)
            cvxv__lrk = c.context.make_array(types.Array(types.bool_, 1, 'C'))(
                c.context, c.builder, mask_arr)
            gnj__wby = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            gwgtd__yis = cgutils.get_or_insert_function(c.builder.module,
                gnj__wby, name='mask_arr_to_bitmap')
            c.builder.call(gwgtd__yis, [klc__mjr.data, cvxv__lrk.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with ifnz__cogjd:
            tszdt__mwcpm = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            gnj__wby = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            uiooc__snyx = cgutils.get_or_insert_function(c.builder.module,
                gnj__wby, name='int_array_from_sequence')
            c.builder.call(uiooc__snyx, [obj, c.builder.bitcast(
                tszdt__mwcpm.data, lir.IntType(8).as_pointer()), klc__mjr.data]
                )
            gwkyb__mujo.data = tszdt__mwcpm._getvalue()
    gwkyb__mujo.null_bitmap = klc__mjr._getvalue()
    metd__wwdhy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(gwkyb__mujo._getvalue(), is_error=metd__wwdhy)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    gwkyb__mujo = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        gwkyb__mujo.data, c.env_manager)
    lbn__fvkt = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, gwkyb__mujo.null_bitmap).data
    bey__zgci = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(bey__zgci)
    huc__rvyj = c.context.insert_const_string(c.builder.module, 'numpy')
    ebagq__flu = c.pyapi.import_module_noblock(huc__rvyj)
    sinvb__mssbd = c.pyapi.object_getattr_string(ebagq__flu, 'bool_')
    mask_arr = c.pyapi.call_method(ebagq__flu, 'empty', (bey__zgci,
        sinvb__mssbd))
    ljxr__evpef = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    okrkk__bqm = c.pyapi.object_getattr_string(ljxr__evpef, 'data')
    ogqj__grayf = c.builder.inttoptr(c.pyapi.long_as_longlong(okrkk__bqm),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as ygptr__ddjrh:
        i = ygptr__ddjrh.index
        cctjm__fxpq = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        thmtb__bauf = c.builder.load(cgutils.gep(c.builder, lbn__fvkt,
            cctjm__fxpq))
        moo__egbs = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(thmtb__bauf, moo__egbs), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        cjwe__pbcvn = cgutils.gep(c.builder, ogqj__grayf, i)
        c.builder.store(val, cjwe__pbcvn)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        gwkyb__mujo.null_bitmap)
    huc__rvyj = c.context.insert_const_string(c.builder.module, 'pandas')
    bnx__tni = c.pyapi.import_module_noblock(huc__rvyj)
    ngq__ngf = c.pyapi.object_getattr_string(bnx__tni, 'arrays')
    qucps__matud = c.pyapi.call_method(ngq__ngf, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(bnx__tni)
    c.pyapi.decref(bey__zgci)
    c.pyapi.decref(ebagq__flu)
    c.pyapi.decref(sinvb__mssbd)
    c.pyapi.decref(ljxr__evpef)
    c.pyapi.decref(okrkk__bqm)
    c.pyapi.decref(ngq__ngf)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return qucps__matud


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        qwk__ofk, pkqh__lvicm = args
        gwkyb__mujo = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        gwkyb__mujo.data = qwk__ofk
        gwkyb__mujo.null_bitmap = pkqh__lvicm
        context.nrt.incref(builder, signature.args[0], qwk__ofk)
        context.nrt.incref(builder, signature.args[1], pkqh__lvicm)
        return gwkyb__mujo._getvalue()
    rjak__ztp = IntegerArrayType(data.dtype)
    yys__fhk = rjak__ztp(data, null_bitmap)
    return yys__fhk, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    tzt__ivekt = np.empty(n, pyval.dtype.type)
    ppnkm__zjmg = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        hkhe__qmf = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(ppnkm__zjmg, i, int(not hkhe__qmf)
            )
        if not hkhe__qmf:
            tzt__ivekt[i] = s
    hwje__hgo = context.get_constant_generic(builder, types.Array(typ.dtype,
        1, 'C'), tzt__ivekt)
    nqu__djj = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), ppnkm__zjmg)
    return lir.Constant.literal_struct([hwje__hgo, nqu__djj])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    fkzt__wbg = args[0]
    if equiv_set.has_shape(fkzt__wbg):
        return ArrayAnalysis.AnalyzeResult(shape=fkzt__wbg, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    fkzt__wbg = args[0]
    if equiv_set.has_shape(fkzt__wbg):
        return ArrayAnalysis.AnalyzeResult(shape=fkzt__wbg, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_init_integer_array = (
    init_integer_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_integer_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_integer_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_integer_array
numba.core.ir_utils.alias_func_extensions['get_int_arr_data',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_int_arr_bitmap',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_int_array(n, dtype):
    tzt__ivekt = np.empty(n, dtype)
    sye__ninz = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(tzt__ivekt, sye__ninz)


def alloc_int_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_alloc_int_array = (
    alloc_int_array_equiv)


@numba.extending.register_jitable
def set_bit_to_arr(bits, i, bit_is_set):
    bits[i // 8] ^= np.uint8(-np.uint8(bit_is_set) ^ bits[i // 8]) & kBitmask[
        i % 8]


@numba.extending.register_jitable
def get_bit_bitmap_arr(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@overload(operator.getitem, no_unliteral=True)
def int_arr_getitem(A, ind):
    if not isinstance(A, IntegerArrayType):
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            mlqt__wpkhk, gowf__tir = array_getitem_bool_index(A, ind)
            return init_integer_array(mlqt__wpkhk, gowf__tir)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            mlqt__wpkhk, gowf__tir = array_getitem_int_index(A, ind)
            return init_integer_array(mlqt__wpkhk, gowf__tir)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            mlqt__wpkhk, gowf__tir = array_getitem_slice_index(A, ind)
            return init_integer_array(mlqt__wpkhk, gowf__tir)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    xfr__xai = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    pxp__waj = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if pxp__waj:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(xfr__xai)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or pxp__waj):
        raise BodoError(xfr__xai)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for IntegerArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_int_arr_len(A):
    if isinstance(A, IntegerArrayType):
        return lambda A: len(A._data)


@overload_attribute(IntegerArrayType, 'shape')
def overload_int_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(IntegerArrayType, 'dtype')
def overload_int_arr_dtype(A):
    dtype_class = getattr(pd, '{}Int{}Dtype'.format('' if A.dtype.signed else
        'U', A.dtype.bitwidth))
    return lambda A: dtype_class()


@overload_attribute(IntegerArrayType, 'ndim')
def overload_int_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntegerArrayType, 'nbytes')
def int_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(IntegerArrayType, 'copy', no_unliteral=True)
def overload_int_arr_copy(A, dtype=None):
    if not is_overload_none(dtype):
        return lambda A, dtype=None: A.astype(dtype, copy=True)
    else:
        return lambda A, dtype=None: bodo.libs.int_arr_ext.init_integer_array(
            bodo.libs.int_arr_ext.get_int_arr_data(A).copy(), bodo.libs.
            int_arr_ext.get_int_arr_bitmap(A).copy())


@overload_method(IntegerArrayType, 'astype', no_unliteral=True)
def overload_int_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "IntegerArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.NumberClass):
        dtype = dtype.dtype
    if isinstance(dtype, IntDtype) and A.dtype == dtype.dtype:
        if is_overload_false(copy):
            return lambda A, dtype, copy=True: A
        elif is_overload_true(copy):
            return lambda A, dtype, copy=True: A.copy()
        else:

            def impl(A, dtype, copy=True):
                if copy:
                    return A.copy()
                else:
                    return A
            return impl
    if isinstance(dtype, IntDtype):
        np_dtype = dtype.dtype
        return (lambda A, dtype, copy=True: bodo.libs.int_arr_ext.
            init_integer_array(bodo.libs.int_arr_ext.get_int_arr_data(A).
            astype(np_dtype), bodo.libs.int_arr_ext.get_int_arr_bitmap(A).
            copy()))
    nb_dtype = parse_dtype(dtype, 'IntegerArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.int_arr_ext.get_int_arr_data(A)
            n = len(data)
            mxsdf__fjsu = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                mxsdf__fjsu[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    mxsdf__fjsu[i] = np.nan
            return mxsdf__fjsu
        return impl_float
    return lambda A, dtype, copy=True: bodo.libs.int_arr_ext.get_int_arr_data(A
        ).astype(nb_dtype)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def apply_null_mask(arr, bitmap, mask_fill, inplace):
    assert isinstance(arr, types.Array)
    if isinstance(arr.dtype, types.Integer):
        if is_overload_none(inplace):
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap.copy()))
        else:
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap))
    if isinstance(arr.dtype, types.Float):

        def impl(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = np.nan
            return arr
        return impl
    if arr.dtype == types.bool_:

        def impl_bool(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = mask_fill
            return arr
        return impl_bool
    return lambda arr, bitmap, mask_fill, inplace: arr


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def merge_bitmaps(B1, B2, n, inplace):
    assert B1 == types.Array(types.uint8, 1, 'C')
    assert B2 == types.Array(types.uint8, 1, 'C')
    if not is_overload_none(inplace):

        def impl_inplace(B1, B2, n, inplace):
            for i in numba.parfors.parfor.internal_prange(n):
                swa__orei = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                tns__rmgde = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                agnun__pwqkc = swa__orei & tns__rmgde
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, agnun__pwqkc)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        musnt__nsrgm = n + 7 >> 3
        mxsdf__fjsu = np.empty(musnt__nsrgm, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            swa__orei = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            tns__rmgde = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            agnun__pwqkc = swa__orei & tns__rmgde
            bodo.libs.int_arr_ext.set_bit_to_arr(mxsdf__fjsu, i, agnun__pwqkc)
        return mxsdf__fjsu
    return impl


ufunc_aliases = {'subtract': 'sub', 'multiply': 'mul', 'floor_divide':
    'floordiv', 'true_divide': 'truediv', 'power': 'pow', 'remainder':
    'mod', 'divide': 'div', 'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    if n_inputs == 1:

        def overload_int_arr_op_nin_1(A):
            if isinstance(A, IntegerArrayType):
                return get_nullable_array_unary_impl(op, A)
        return overload_int_arr_op_nin_1
    elif n_inputs == 2:

        def overload_series_op_nin_2(lhs, rhs):
            if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
                IntegerArrayType):
                return get_nullable_array_binary_impl(op, lhs, rhs)
        return overload_series_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for wdc__qcq in numba.np.ufunc_db.get_ufuncs():
        unr__zeata = create_op_overload(wdc__qcq, wdc__qcq.nin)
        overload(wdc__qcq, no_unliteral=True)(unr__zeata)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        unr__zeata = create_op_overload(op, 2)
        overload(op)(unr__zeata)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        unr__zeata = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(unr__zeata)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        unr__zeata = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(unr__zeata)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    dzaor__jfjop = len(arrs.types)
    uujp__ynmbi = 'def f(arrs):\n'
    qucps__matud = ', '.join('arrs[{}]._data'.format(i) for i in range(
        dzaor__jfjop))
    uujp__ynmbi += '  return ({}{})\n'.format(qucps__matud, ',' if 
        dzaor__jfjop == 1 else '')
    ljok__qeiua = {}
    exec(uujp__ynmbi, {}, ljok__qeiua)
    impl = ljok__qeiua['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    dzaor__jfjop = len(arrs.types)
    bxu__vohn = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        dzaor__jfjop))
    uujp__ynmbi = 'def f(arrs):\n'
    uujp__ynmbi += '  n = {}\n'.format(bxu__vohn)
    uujp__ynmbi += '  n_bytes = (n + 7) >> 3\n'
    uujp__ynmbi += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    uujp__ynmbi += '  curr_bit = 0\n'
    for i in range(dzaor__jfjop):
        uujp__ynmbi += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        uujp__ynmbi += '  for j in range(len(arrs[{}])):\n'.format(i)
        uujp__ynmbi += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        uujp__ynmbi += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        uujp__ynmbi += '    curr_bit += 1\n'
    uujp__ynmbi += '  return new_mask\n'
    ljok__qeiua = {}
    exec(uujp__ynmbi, {'np': np, 'bodo': bodo}, ljok__qeiua)
    impl = ljok__qeiua['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    nvq__anyfl = dict(skipna=skipna, min_count=min_count)
    lrm__qyejn = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', nvq__anyfl, lrm__qyejn)

    def impl(A, skipna=True, min_count=0):
        numba.parfors.parfor.init_prange()
        s = 0
        for i in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, i):
                val = A[i]
            s += val
        return s
    return impl


@overload_method(IntegerArrayType, 'unique', no_unliteral=True)
def overload_unique(A):
    dtype = A.dtype

    def impl_int_arr(A):
        data = []
        moo__egbs = []
        zskvr__mfkpu = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not zskvr__mfkpu:
                    data.append(dtype(1))
                    moo__egbs.append(False)
                    zskvr__mfkpu = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                moo__egbs.append(True)
        mlqt__wpkhk = np.array(data)
        n = len(mlqt__wpkhk)
        musnt__nsrgm = n + 7 >> 3
        gowf__tir = np.empty(musnt__nsrgm, np.uint8)
        for muyka__bynk in range(n):
            set_bit_to_arr(gowf__tir, muyka__bynk, moo__egbs[muyka__bynk])
        return init_integer_array(mlqt__wpkhk, gowf__tir)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    snzr__hyidu = numba.core.registry.cpu_target.typing_context
    iqjoz__bnv = snzr__hyidu.resolve_function_type(op, (types.Array(A.dtype,
        1, 'C'),), {}).return_type
    iqjoz__bnv = to_nullable_type(iqjoz__bnv)

    def impl(A):
        n = len(A)
        eqnc__zdvnj = bodo.utils.utils.alloc_type(n, iqjoz__bnv, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(eqnc__zdvnj, i)
                continue
            eqnc__zdvnj[i] = op(A[i])
        return eqnc__zdvnj
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    bmib__gvsa = isinstance(lhs, (types.Number, types.Boolean))
    qugkr__pjx = isinstance(rhs, (types.Number, types.Boolean))
    auyfi__xmt = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    fecw__ixsl = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    snzr__hyidu = numba.core.registry.cpu_target.typing_context
    iqjoz__bnv = snzr__hyidu.resolve_function_type(op, (auyfi__xmt,
        fecw__ixsl), {}).return_type
    iqjoz__bnv = to_nullable_type(iqjoz__bnv)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    ywt__mpih = 'lhs' if bmib__gvsa else 'lhs[i]'
    dpu__jfok = 'rhs' if qugkr__pjx else 'rhs[i]'
    uft__gcm = ('False' if bmib__gvsa else
        'bodo.libs.array_kernels.isna(lhs, i)')
    pfo__wmr = ('False' if qugkr__pjx else
        'bodo.libs.array_kernels.isna(rhs, i)')
    uujp__ynmbi = 'def impl(lhs, rhs):\n'
    uujp__ynmbi += '  n = len({})\n'.format('lhs' if not bmib__gvsa else 'rhs')
    if inplace:
        uujp__ynmbi += '  out_arr = {}\n'.format('lhs' if not bmib__gvsa else
            'rhs')
    else:
        uujp__ynmbi += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    uujp__ynmbi += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    uujp__ynmbi += '    if ({}\n'.format(uft__gcm)
    uujp__ynmbi += '        or {}):\n'.format(pfo__wmr)
    uujp__ynmbi += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    uujp__ynmbi += '      continue\n'
    uujp__ynmbi += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(ywt__mpih, dpu__jfok))
    uujp__ynmbi += '  return out_arr\n'
    ljok__qeiua = {}
    exec(uujp__ynmbi, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        iqjoz__bnv, 'op': op}, ljok__qeiua)
    impl = ljok__qeiua['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        bmib__gvsa = lhs in [pd_timedelta_type]
        qugkr__pjx = rhs in [pd_timedelta_type]
        if bmib__gvsa:

            def impl(lhs, rhs):
                n = len(rhs)
                eqnc__zdvnj = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(eqnc__zdvnj, i)
                        continue
                    eqnc__zdvnj[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs, rhs[i]))
                return eqnc__zdvnj
            return impl
        elif qugkr__pjx:

            def impl(lhs, rhs):
                n = len(lhs)
                eqnc__zdvnj = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(eqnc__zdvnj, i)
                        continue
                    eqnc__zdvnj[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs[i], rhs))
                return eqnc__zdvnj
            return impl
    return impl
