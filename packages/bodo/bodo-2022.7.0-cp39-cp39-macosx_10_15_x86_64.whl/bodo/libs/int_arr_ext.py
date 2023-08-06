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
        lkz__gaqow = int(np.log2(self.dtype.bitwidth // 8))
        lqtkm__cowfo = 0 if self.dtype.signed else 4
        idx = lkz__gaqow + lqtkm__cowfo
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wof__jull = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, wof__jull)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    gjdm__ykiga = 8 * val.dtype.itemsize
    mdi__tbq = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(mdi__tbq, gjdm__ykiga))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        vsy__nmuf = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(vsy__nmuf)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    czyv__ljtb = c.context.insert_const_string(c.builder.module, 'pandas')
    uers__nglwc = c.pyapi.import_module_noblock(czyv__ljtb)
    yvbpb__qevl = c.pyapi.call_method(uers__nglwc, str(typ)[:-2], ())
    c.pyapi.decref(uers__nglwc)
    return yvbpb__qevl


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    gjdm__ykiga = 8 * val.itemsize
    mdi__tbq = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(mdi__tbq, gjdm__ykiga))
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
    mfx__sbuef = n + 7 >> 3
    cxvde__cfpqs = np.empty(mfx__sbuef, np.uint8)
    for i in range(n):
        owu__mffnp = i // 8
        cxvde__cfpqs[owu__mffnp] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            cxvde__cfpqs[owu__mffnp]) & kBitmask[i % 8]
    return cxvde__cfpqs


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    mvxla__ohmy = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(mvxla__ohmy)
    c.pyapi.decref(mvxla__ohmy)
    cxy__pzgv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mfx__sbuef = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    zxhag__wrus = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [mfx__sbuef])
    ipxjs__ttf = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    fqiq__jsd = cgutils.get_or_insert_function(c.builder.module, ipxjs__ttf,
        name='is_pd_int_array')
    xmpmw__zspat = c.builder.call(fqiq__jsd, [obj])
    whqfw__ielwm = c.builder.icmp_unsigned('!=', xmpmw__zspat, xmpmw__zspat
        .type(0))
    with c.builder.if_else(whqfw__ielwm) as (xlpgx__fxvpi, kbcit__jiz):
        with xlpgx__fxvpi:
            ytoov__tve = c.pyapi.object_getattr_string(obj, '_data')
            cxy__pzgv.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), ytoov__tve).value
            ufa__gme = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), ufa__gme).value
            c.pyapi.decref(ytoov__tve)
            c.pyapi.decref(ufa__gme)
            syui__vti = c.context.make_array(types.Array(types.bool_, 1, 'C'))(
                c.context, c.builder, mask_arr)
            ipxjs__ttf = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            fqiq__jsd = cgutils.get_or_insert_function(c.builder.module,
                ipxjs__ttf, name='mask_arr_to_bitmap')
            c.builder.call(fqiq__jsd, [zxhag__wrus.data, syui__vti.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with kbcit__jiz:
            pve__pmeut = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            ipxjs__ttf = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            gwg__vqfgd = cgutils.get_or_insert_function(c.builder.module,
                ipxjs__ttf, name='int_array_from_sequence')
            c.builder.call(gwg__vqfgd, [obj, c.builder.bitcast(pve__pmeut.
                data, lir.IntType(8).as_pointer()), zxhag__wrus.data])
            cxy__pzgv.data = pve__pmeut._getvalue()
    cxy__pzgv.null_bitmap = zxhag__wrus._getvalue()
    fywwa__irdjw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cxy__pzgv._getvalue(), is_error=fywwa__irdjw)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    cxy__pzgv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        cxy__pzgv.data, c.env_manager)
    jgkk__yeyu = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, cxy__pzgv.null_bitmap).data
    mvxla__ohmy = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(mvxla__ohmy)
    czyv__ljtb = c.context.insert_const_string(c.builder.module, 'numpy')
    mkky__rgnfm = c.pyapi.import_module_noblock(czyv__ljtb)
    vszy__qsqz = c.pyapi.object_getattr_string(mkky__rgnfm, 'bool_')
    mask_arr = c.pyapi.call_method(mkky__rgnfm, 'empty', (mvxla__ohmy,
        vszy__qsqz))
    iswd__zvf = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    kdbkj__vwzb = c.pyapi.object_getattr_string(iswd__zvf, 'data')
    mjzzw__jdfbg = c.builder.inttoptr(c.pyapi.long_as_longlong(kdbkj__vwzb),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as xxbsn__odjz:
        i = xxbsn__odjz.index
        qdnx__odg = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        yhsrc__eywt = c.builder.load(cgutils.gep(c.builder, jgkk__yeyu,
            qdnx__odg))
        lln__wfwy = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(yhsrc__eywt, lln__wfwy), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        hdvt__rwcx = cgutils.gep(c.builder, mjzzw__jdfbg, i)
        c.builder.store(val, hdvt__rwcx)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        cxy__pzgv.null_bitmap)
    czyv__ljtb = c.context.insert_const_string(c.builder.module, 'pandas')
    uers__nglwc = c.pyapi.import_module_noblock(czyv__ljtb)
    ippf__cwe = c.pyapi.object_getattr_string(uers__nglwc, 'arrays')
    yvbpb__qevl = c.pyapi.call_method(ippf__cwe, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(uers__nglwc)
    c.pyapi.decref(mvxla__ohmy)
    c.pyapi.decref(mkky__rgnfm)
    c.pyapi.decref(vszy__qsqz)
    c.pyapi.decref(iswd__zvf)
    c.pyapi.decref(kdbkj__vwzb)
    c.pyapi.decref(ippf__cwe)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return yvbpb__qevl


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        lmujo__sfm, plt__pxuc = args
        cxy__pzgv = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        cxy__pzgv.data = lmujo__sfm
        cxy__pzgv.null_bitmap = plt__pxuc
        context.nrt.incref(builder, signature.args[0], lmujo__sfm)
        context.nrt.incref(builder, signature.args[1], plt__pxuc)
        return cxy__pzgv._getvalue()
    urush__iosh = IntegerArrayType(data.dtype)
    yzep__nkzrc = urush__iosh(data, null_bitmap)
    return yzep__nkzrc, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    uqs__yprcz = np.empty(n, pyval.dtype.type)
    kyiz__byk = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        adjiy__ods = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(kyiz__byk, i, int(not adjiy__ods))
        if not adjiy__ods:
            uqs__yprcz[i] = s
    snk__fnbvx = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), uqs__yprcz)
    vhz__nva = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), kyiz__byk)
    return lir.Constant.literal_struct([snk__fnbvx, vhz__nva])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    nhytf__fvz = args[0]
    if equiv_set.has_shape(nhytf__fvz):
        return ArrayAnalysis.AnalyzeResult(shape=nhytf__fvz, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    nhytf__fvz = args[0]
    if equiv_set.has_shape(nhytf__fvz):
        return ArrayAnalysis.AnalyzeResult(shape=nhytf__fvz, pre=[])
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
    uqs__yprcz = np.empty(n, dtype)
    lazcl__hacir = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(uqs__yprcz, lazcl__hacir)


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
            pip__wydo, mdb__azxqj = array_getitem_bool_index(A, ind)
            return init_integer_array(pip__wydo, mdb__azxqj)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            pip__wydo, mdb__azxqj = array_getitem_int_index(A, ind)
            return init_integer_array(pip__wydo, mdb__azxqj)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            pip__wydo, mdb__azxqj = array_getitem_slice_index(A, ind)
            return init_integer_array(pip__wydo, mdb__azxqj)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    vfbv__ibff = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    yeoin__rzi = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if yeoin__rzi:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(vfbv__ibff)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or yeoin__rzi):
        raise BodoError(vfbv__ibff)
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
            xaq__aoa = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                xaq__aoa[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    xaq__aoa[i] = np.nan
            return xaq__aoa
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
                jwd__ipnab = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                rnuv__ixjk = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                rmx__mfrs = jwd__ipnab & rnuv__ixjk
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, rmx__mfrs)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        mfx__sbuef = n + 7 >> 3
        xaq__aoa = np.empty(mfx__sbuef, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            jwd__ipnab = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            rnuv__ixjk = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            rmx__mfrs = jwd__ipnab & rnuv__ixjk
            bodo.libs.int_arr_ext.set_bit_to_arr(xaq__aoa, i, rmx__mfrs)
        return xaq__aoa
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
    for bzsls__udkf in numba.np.ufunc_db.get_ufuncs():
        ymp__fsfy = create_op_overload(bzsls__udkf, bzsls__udkf.nin)
        overload(bzsls__udkf, no_unliteral=True)(ymp__fsfy)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        ymp__fsfy = create_op_overload(op, 2)
        overload(op)(ymp__fsfy)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        ymp__fsfy = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(ymp__fsfy)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        ymp__fsfy = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(ymp__fsfy)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    xyz__ais = len(arrs.types)
    lpe__jout = 'def f(arrs):\n'
    yvbpb__qevl = ', '.join('arrs[{}]._data'.format(i) for i in range(xyz__ais)
        )
    lpe__jout += '  return ({}{})\n'.format(yvbpb__qevl, ',' if xyz__ais ==
        1 else '')
    oumvg__iex = {}
    exec(lpe__jout, {}, oumvg__iex)
    impl = oumvg__iex['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    xyz__ais = len(arrs.types)
    dbgu__mbhq = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        xyz__ais))
    lpe__jout = 'def f(arrs):\n'
    lpe__jout += '  n = {}\n'.format(dbgu__mbhq)
    lpe__jout += '  n_bytes = (n + 7) >> 3\n'
    lpe__jout += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    lpe__jout += '  curr_bit = 0\n'
    for i in range(xyz__ais):
        lpe__jout += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        lpe__jout += '  for j in range(len(arrs[{}])):\n'.format(i)
        lpe__jout += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        lpe__jout += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        lpe__jout += '    curr_bit += 1\n'
    lpe__jout += '  return new_mask\n'
    oumvg__iex = {}
    exec(lpe__jout, {'np': np, 'bodo': bodo}, oumvg__iex)
    impl = oumvg__iex['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    ppk__xho = dict(skipna=skipna, min_count=min_count)
    vywa__vlgug = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', ppk__xho, vywa__vlgug)

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
        lln__wfwy = []
        tywo__vbe = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not tywo__vbe:
                    data.append(dtype(1))
                    lln__wfwy.append(False)
                    tywo__vbe = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                lln__wfwy.append(True)
        pip__wydo = np.array(data)
        n = len(pip__wydo)
        mfx__sbuef = n + 7 >> 3
        mdb__azxqj = np.empty(mfx__sbuef, np.uint8)
        for cmvi__jymfq in range(n):
            set_bit_to_arr(mdb__azxqj, cmvi__jymfq, lln__wfwy[cmvi__jymfq])
        return init_integer_array(pip__wydo, mdb__azxqj)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    jnen__uxdcw = numba.core.registry.cpu_target.typing_context
    jvhu__pcdu = jnen__uxdcw.resolve_function_type(op, (types.Array(A.dtype,
        1, 'C'),), {}).return_type
    jvhu__pcdu = to_nullable_type(jvhu__pcdu)

    def impl(A):
        n = len(A)
        gtea__fjwg = bodo.utils.utils.alloc_type(n, jvhu__pcdu, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(gtea__fjwg, i)
                continue
            gtea__fjwg[i] = op(A[i])
        return gtea__fjwg
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    vexzs__idlds = isinstance(lhs, (types.Number, types.Boolean))
    rnvmr__hzysy = isinstance(rhs, (types.Number, types.Boolean))
    zupch__lysf = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    epzq__dbtee = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    jnen__uxdcw = numba.core.registry.cpu_target.typing_context
    jvhu__pcdu = jnen__uxdcw.resolve_function_type(op, (zupch__lysf,
        epzq__dbtee), {}).return_type
    jvhu__pcdu = to_nullable_type(jvhu__pcdu)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    iioms__cberh = 'lhs' if vexzs__idlds else 'lhs[i]'
    unfr__bscju = 'rhs' if rnvmr__hzysy else 'rhs[i]'
    bgi__dzq = ('False' if vexzs__idlds else
        'bodo.libs.array_kernels.isna(lhs, i)')
    qifqm__oqlxd = ('False' if rnvmr__hzysy else
        'bodo.libs.array_kernels.isna(rhs, i)')
    lpe__jout = 'def impl(lhs, rhs):\n'
    lpe__jout += '  n = len({})\n'.format('lhs' if not vexzs__idlds else 'rhs')
    if inplace:
        lpe__jout += '  out_arr = {}\n'.format('lhs' if not vexzs__idlds else
            'rhs')
    else:
        lpe__jout += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    lpe__jout += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    lpe__jout += '    if ({}\n'.format(bgi__dzq)
    lpe__jout += '        or {}):\n'.format(qifqm__oqlxd)
    lpe__jout += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    lpe__jout += '      continue\n'
    lpe__jout += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(iioms__cberh, unfr__bscju))
    lpe__jout += '  return out_arr\n'
    oumvg__iex = {}
    exec(lpe__jout, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        jvhu__pcdu, 'op': op}, oumvg__iex)
    impl = oumvg__iex['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        vexzs__idlds = lhs in [pd_timedelta_type]
        rnvmr__hzysy = rhs in [pd_timedelta_type]
        if vexzs__idlds:

            def impl(lhs, rhs):
                n = len(rhs)
                gtea__fjwg = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(gtea__fjwg, i)
                        continue
                    gtea__fjwg[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return gtea__fjwg
            return impl
        elif rnvmr__hzysy:

            def impl(lhs, rhs):
                n = len(lhs)
                gtea__fjwg = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(gtea__fjwg, i)
                        continue
                    gtea__fjwg[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return gtea__fjwg
            return impl
    return impl
