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
        gfy__znzxm = int(np.log2(self.dtype.bitwidth // 8))
        qui__cbkc = 0 if self.dtype.signed else 4
        idx = gfy__znzxm + qui__cbkc
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        yjp__twvik = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, yjp__twvik)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    mufq__tcu = 8 * val.dtype.itemsize
    nrqce__dattr = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(nrqce__dattr, mufq__tcu))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        waafk__alyfg = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(waafk__alyfg)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    cphvu__ovwlq = c.context.insert_const_string(c.builder.module, 'pandas')
    ime__brliy = c.pyapi.import_module_noblock(cphvu__ovwlq)
    mkqw__vazs = c.pyapi.call_method(ime__brliy, str(typ)[:-2], ())
    c.pyapi.decref(ime__brliy)
    return mkqw__vazs


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    mufq__tcu = 8 * val.itemsize
    nrqce__dattr = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(nrqce__dattr, mufq__tcu))
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
    sam__poc = n + 7 >> 3
    wck__cbf = np.empty(sam__poc, np.uint8)
    for i in range(n):
        ivs__pzqi = i // 8
        wck__cbf[ivs__pzqi] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            wck__cbf[ivs__pzqi]) & kBitmask[i % 8]
    return wck__cbf


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    klfb__aodc = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(klfb__aodc)
    c.pyapi.decref(klfb__aodc)
    kkqx__sxsy = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    sam__poc = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64),
        7)), lir.Constant(lir.IntType(64), 8))
    qhu__sofi = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [sam__poc])
    rfkgp__rgm = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    ucqk__jfg = cgutils.get_or_insert_function(c.builder.module, rfkgp__rgm,
        name='is_pd_int_array')
    gedmr__fpx = c.builder.call(ucqk__jfg, [obj])
    xuf__slgj = c.builder.icmp_unsigned('!=', gedmr__fpx, gedmr__fpx.type(0))
    with c.builder.if_else(xuf__slgj) as (ojgo__hmpwt, dpst__ybgr):
        with ojgo__hmpwt:
            knujm__krhd = c.pyapi.object_getattr_string(obj, '_data')
            kkqx__sxsy.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), knujm__krhd).value
            wth__jfffr = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), wth__jfffr).value
            c.pyapi.decref(knujm__krhd)
            c.pyapi.decref(wth__jfffr)
            qrk__ntb = c.context.make_array(types.Array(types.bool_, 1, 'C'))(c
                .context, c.builder, mask_arr)
            rfkgp__rgm = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            ucqk__jfg = cgutils.get_or_insert_function(c.builder.module,
                rfkgp__rgm, name='mask_arr_to_bitmap')
            c.builder.call(ucqk__jfg, [qhu__sofi.data, qrk__ntb.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with dpst__ybgr:
            axizg__efb = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            rfkgp__rgm = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            lvzfa__vepj = cgutils.get_or_insert_function(c.builder.module,
                rfkgp__rgm, name='int_array_from_sequence')
            c.builder.call(lvzfa__vepj, [obj, c.builder.bitcast(axizg__efb.
                data, lir.IntType(8).as_pointer()), qhu__sofi.data])
            kkqx__sxsy.data = axizg__efb._getvalue()
    kkqx__sxsy.null_bitmap = qhu__sofi._getvalue()
    oyx__oreuu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(kkqx__sxsy._getvalue(), is_error=oyx__oreuu)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    kkqx__sxsy = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        kkqx__sxsy.data, c.env_manager)
    vlx__vfhx = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, kkqx__sxsy.null_bitmap).data
    klfb__aodc = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(klfb__aodc)
    cphvu__ovwlq = c.context.insert_const_string(c.builder.module, 'numpy')
    six__gzch = c.pyapi.import_module_noblock(cphvu__ovwlq)
    dljzo__ydvm = c.pyapi.object_getattr_string(six__gzch, 'bool_')
    mask_arr = c.pyapi.call_method(six__gzch, 'empty', (klfb__aodc,
        dljzo__ydvm))
    xno__owfro = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    xvdkb__nkhsd = c.pyapi.object_getattr_string(xno__owfro, 'data')
    dnhla__lpi = c.builder.inttoptr(c.pyapi.long_as_longlong(xvdkb__nkhsd),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as gmcfp__mneu:
        i = gmcfp__mneu.index
        skf__ymq = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        llph__ioeh = c.builder.load(cgutils.gep(c.builder, vlx__vfhx, skf__ymq)
            )
        rmx__bswqz = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(llph__ioeh, rmx__bswqz), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        irbs__qht = cgutils.gep(c.builder, dnhla__lpi, i)
        c.builder.store(val, irbs__qht)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        kkqx__sxsy.null_bitmap)
    cphvu__ovwlq = c.context.insert_const_string(c.builder.module, 'pandas')
    ime__brliy = c.pyapi.import_module_noblock(cphvu__ovwlq)
    wmp__nzjvl = c.pyapi.object_getattr_string(ime__brliy, 'arrays')
    mkqw__vazs = c.pyapi.call_method(wmp__nzjvl, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(ime__brliy)
    c.pyapi.decref(klfb__aodc)
    c.pyapi.decref(six__gzch)
    c.pyapi.decref(dljzo__ydvm)
    c.pyapi.decref(xno__owfro)
    c.pyapi.decref(xvdkb__nkhsd)
    c.pyapi.decref(wmp__nzjvl)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return mkqw__vazs


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        tsmvp__mcd, vsyjq__kkell = args
        kkqx__sxsy = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        kkqx__sxsy.data = tsmvp__mcd
        kkqx__sxsy.null_bitmap = vsyjq__kkell
        context.nrt.incref(builder, signature.args[0], tsmvp__mcd)
        context.nrt.incref(builder, signature.args[1], vsyjq__kkell)
        return kkqx__sxsy._getvalue()
    pdf__mcccg = IntegerArrayType(data.dtype)
    enbt__lxqz = pdf__mcccg(data, null_bitmap)
    return enbt__lxqz, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    wfbc__cpau = np.empty(n, pyval.dtype.type)
    gmjs__gxvov = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        tepc__bmzyk = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(gmjs__gxvov, i, int(not
            tepc__bmzyk))
        if not tepc__bmzyk:
            wfbc__cpau[i] = s
    iod__tspoj = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), wfbc__cpau)
    vjm__sed = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), gmjs__gxvov)
    return lir.Constant.literal_struct([iod__tspoj, vjm__sed])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    zod__cdtbj = args[0]
    if equiv_set.has_shape(zod__cdtbj):
        return ArrayAnalysis.AnalyzeResult(shape=zod__cdtbj, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    zod__cdtbj = args[0]
    if equiv_set.has_shape(zod__cdtbj):
        return ArrayAnalysis.AnalyzeResult(shape=zod__cdtbj, pre=[])
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
    wfbc__cpau = np.empty(n, dtype)
    lpt__aad = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(wfbc__cpau, lpt__aad)


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
            rpda__gat, aqqh__qhk = array_getitem_bool_index(A, ind)
            return init_integer_array(rpda__gat, aqqh__qhk)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            rpda__gat, aqqh__qhk = array_getitem_int_index(A, ind)
            return init_integer_array(rpda__gat, aqqh__qhk)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            rpda__gat, aqqh__qhk = array_getitem_slice_index(A, ind)
            return init_integer_array(rpda__gat, aqqh__qhk)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    xkvtw__dmhuo = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    pfex__rldl = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if pfex__rldl:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(xkvtw__dmhuo)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or pfex__rldl):
        raise BodoError(xkvtw__dmhuo)
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
            hxvg__coozu = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                hxvg__coozu[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    hxvg__coozu[i] = np.nan
            return hxvg__coozu
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
                vvuwd__cilao = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                moci__ppj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                pstyo__jole = vvuwd__cilao & moci__ppj
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, pstyo__jole)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        sam__poc = n + 7 >> 3
        hxvg__coozu = np.empty(sam__poc, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            vvuwd__cilao = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            moci__ppj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            pstyo__jole = vvuwd__cilao & moci__ppj
            bodo.libs.int_arr_ext.set_bit_to_arr(hxvg__coozu, i, pstyo__jole)
        return hxvg__coozu
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
    for opt__lfovg in numba.np.ufunc_db.get_ufuncs():
        dvk__ssh = create_op_overload(opt__lfovg, opt__lfovg.nin)
        overload(opt__lfovg, no_unliteral=True)(dvk__ssh)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        dvk__ssh = create_op_overload(op, 2)
        overload(op)(dvk__ssh)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        dvk__ssh = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(dvk__ssh)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        dvk__ssh = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(dvk__ssh)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    uwyyi__widlw = len(arrs.types)
    uqmv__ymaf = 'def f(arrs):\n'
    mkqw__vazs = ', '.join('arrs[{}]._data'.format(i) for i in range(
        uwyyi__widlw))
    uqmv__ymaf += '  return ({}{})\n'.format(mkqw__vazs, ',' if 
        uwyyi__widlw == 1 else '')
    ceqti__lht = {}
    exec(uqmv__ymaf, {}, ceqti__lht)
    impl = ceqti__lht['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    uwyyi__widlw = len(arrs.types)
    vffc__otc = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        uwyyi__widlw))
    uqmv__ymaf = 'def f(arrs):\n'
    uqmv__ymaf += '  n = {}\n'.format(vffc__otc)
    uqmv__ymaf += '  n_bytes = (n + 7) >> 3\n'
    uqmv__ymaf += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    uqmv__ymaf += '  curr_bit = 0\n'
    for i in range(uwyyi__widlw):
        uqmv__ymaf += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        uqmv__ymaf += '  for j in range(len(arrs[{}])):\n'.format(i)
        uqmv__ymaf += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        uqmv__ymaf += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        uqmv__ymaf += '    curr_bit += 1\n'
    uqmv__ymaf += '  return new_mask\n'
    ceqti__lht = {}
    exec(uqmv__ymaf, {'np': np, 'bodo': bodo}, ceqti__lht)
    impl = ceqti__lht['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    myf__nogaa = dict(skipna=skipna, min_count=min_count)
    ltssp__bhw = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', myf__nogaa, ltssp__bhw)

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
        rmx__bswqz = []
        kkyb__ycfuu = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not kkyb__ycfuu:
                    data.append(dtype(1))
                    rmx__bswqz.append(False)
                    kkyb__ycfuu = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                rmx__bswqz.append(True)
        rpda__gat = np.array(data)
        n = len(rpda__gat)
        sam__poc = n + 7 >> 3
        aqqh__qhk = np.empty(sam__poc, np.uint8)
        for yto__etn in range(n):
            set_bit_to_arr(aqqh__qhk, yto__etn, rmx__bswqz[yto__etn])
        return init_integer_array(rpda__gat, aqqh__qhk)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    uquw__rfdjo = numba.core.registry.cpu_target.typing_context
    mxo__lxa = uquw__rfdjo.resolve_function_type(op, (types.Array(A.dtype, 
        1, 'C'),), {}).return_type
    mxo__lxa = to_nullable_type(mxo__lxa)

    def impl(A):
        n = len(A)
        rcc__fempe = bodo.utils.utils.alloc_type(n, mxo__lxa, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(rcc__fempe, i)
                continue
            rcc__fempe[i] = op(A[i])
        return rcc__fempe
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    plj__bik = isinstance(lhs, (types.Number, types.Boolean))
    lnnm__hhs = isinstance(rhs, (types.Number, types.Boolean))
    lgyg__gzit = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    vdu__bhh = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    uquw__rfdjo = numba.core.registry.cpu_target.typing_context
    mxo__lxa = uquw__rfdjo.resolve_function_type(op, (lgyg__gzit, vdu__bhh), {}
        ).return_type
    mxo__lxa = to_nullable_type(mxo__lxa)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    kindc__lrdt = 'lhs' if plj__bik else 'lhs[i]'
    scz__txwkn = 'rhs' if lnnm__hhs else 'rhs[i]'
    fesg__ozy = 'False' if plj__bik else 'bodo.libs.array_kernels.isna(lhs, i)'
    hlid__dqwpr = ('False' if lnnm__hhs else
        'bodo.libs.array_kernels.isna(rhs, i)')
    uqmv__ymaf = 'def impl(lhs, rhs):\n'
    uqmv__ymaf += '  n = len({})\n'.format('lhs' if not plj__bik else 'rhs')
    if inplace:
        uqmv__ymaf += '  out_arr = {}\n'.format('lhs' if not plj__bik else
            'rhs')
    else:
        uqmv__ymaf += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    uqmv__ymaf += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    uqmv__ymaf += '    if ({}\n'.format(fesg__ozy)
    uqmv__ymaf += '        or {}):\n'.format(hlid__dqwpr)
    uqmv__ymaf += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    uqmv__ymaf += '      continue\n'
    uqmv__ymaf += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(kindc__lrdt, scz__txwkn))
    uqmv__ymaf += '  return out_arr\n'
    ceqti__lht = {}
    exec(uqmv__ymaf, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        mxo__lxa, 'op': op}, ceqti__lht)
    impl = ceqti__lht['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        plj__bik = lhs in [pd_timedelta_type]
        lnnm__hhs = rhs in [pd_timedelta_type]
        if plj__bik:

            def impl(lhs, rhs):
                n = len(rhs)
                rcc__fempe = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(rcc__fempe, i)
                        continue
                    rcc__fempe[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return rcc__fempe
            return impl
        elif lnnm__hhs:

            def impl(lhs, rhs):
                n = len(lhs)
                rcc__fempe = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(rcc__fempe, i)
                        continue
                    rcc__fempe[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return rcc__fempe
            return impl
    return impl
