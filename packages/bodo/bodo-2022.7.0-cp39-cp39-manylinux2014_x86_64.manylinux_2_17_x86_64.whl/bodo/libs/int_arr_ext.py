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
        rrq__jop = int(np.log2(self.dtype.bitwidth // 8))
        afdba__cjwd = 0 if self.dtype.signed else 4
        idx = rrq__jop + afdba__cjwd
        return pd_int_dtype_classes[idx]()


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cuuo__jki = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, cuuo__jki)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    gkb__byptx = 8 * val.dtype.itemsize
    gdn__vcqfp = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(gdn__vcqfp, gkb__byptx))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        mtnb__jqt = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(mtnb__jqt)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    gfnr__nqvg = c.context.insert_const_string(c.builder.module, 'pandas')
    mgbrg__akf = c.pyapi.import_module_noblock(gfnr__nqvg)
    fqph__uotw = c.pyapi.call_method(mgbrg__akf, str(typ)[:-2], ())
    c.pyapi.decref(mgbrg__akf)
    return fqph__uotw


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    gkb__byptx = 8 * val.itemsize
    gdn__vcqfp = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(gdn__vcqfp, gkb__byptx))
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
    nlrh__zgvp = n + 7 >> 3
    qryk__tlirv = np.empty(nlrh__zgvp, np.uint8)
    for i in range(n):
        vyda__sdn = i // 8
        qryk__tlirv[vyda__sdn] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            qryk__tlirv[vyda__sdn]) & kBitmask[i % 8]
    return qryk__tlirv


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    njs__jkgs = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(njs__jkgs)
    c.pyapi.decref(njs__jkgs)
    rcwx__saxh = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nlrh__zgvp = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    bxrdm__ldzqg = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [nlrh__zgvp])
    ebf__lsd = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()])
    xjgx__bwjxg = cgutils.get_or_insert_function(c.builder.module, ebf__lsd,
        name='is_pd_int_array')
    zkbcl__rykt = c.builder.call(xjgx__bwjxg, [obj])
    ycp__zri = c.builder.icmp_unsigned('!=', zkbcl__rykt, zkbcl__rykt.type(0))
    with c.builder.if_else(ycp__zri) as (ewpf__jkd, vnqy__keup):
        with ewpf__jkd:
            apo__zxf = c.pyapi.object_getattr_string(obj, '_data')
            rcwx__saxh.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), apo__zxf).value
            ukdd__fpa = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), ukdd__fpa).value
            c.pyapi.decref(apo__zxf)
            c.pyapi.decref(ukdd__fpa)
            qesvo__hxi = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            ebf__lsd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            xjgx__bwjxg = cgutils.get_or_insert_function(c.builder.module,
                ebf__lsd, name='mask_arr_to_bitmap')
            c.builder.call(xjgx__bwjxg, [bxrdm__ldzqg.data, qesvo__hxi.data, n]
                )
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with vnqy__keup:
            uge__ieyc = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            ebf__lsd = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            xre__uavyq = cgutils.get_or_insert_function(c.builder.module,
                ebf__lsd, name='int_array_from_sequence')
            c.builder.call(xre__uavyq, [obj, c.builder.bitcast(uge__ieyc.
                data, lir.IntType(8).as_pointer()), bxrdm__ldzqg.data])
            rcwx__saxh.data = uge__ieyc._getvalue()
    rcwx__saxh.null_bitmap = bxrdm__ldzqg._getvalue()
    bwe__dbb = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(rcwx__saxh._getvalue(), is_error=bwe__dbb)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    rcwx__saxh = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        rcwx__saxh.data, c.env_manager)
    dqbc__kcmv = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, rcwx__saxh.null_bitmap).data
    njs__jkgs = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(njs__jkgs)
    gfnr__nqvg = c.context.insert_const_string(c.builder.module, 'numpy')
    jej__auzfs = c.pyapi.import_module_noblock(gfnr__nqvg)
    ehmk__jgvk = c.pyapi.object_getattr_string(jej__auzfs, 'bool_')
    mask_arr = c.pyapi.call_method(jej__auzfs, 'empty', (njs__jkgs, ehmk__jgvk)
        )
    hyj__mwz = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    hgt__dysr = c.pyapi.object_getattr_string(hyj__mwz, 'data')
    sabhh__enf = c.builder.inttoptr(c.pyapi.long_as_longlong(hgt__dysr),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as mbc__fftgc:
        i = mbc__fftgc.index
        ptpa__vzd = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        bey__hja = c.builder.load(cgutils.gep(c.builder, dqbc__kcmv, ptpa__vzd)
            )
        bnubk__xuba = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(bey__hja, bnubk__xuba), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        rxw__kqlxa = cgutils.gep(c.builder, sabhh__enf, i)
        c.builder.store(val, rxw__kqlxa)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        rcwx__saxh.null_bitmap)
    gfnr__nqvg = c.context.insert_const_string(c.builder.module, 'pandas')
    mgbrg__akf = c.pyapi.import_module_noblock(gfnr__nqvg)
    ferdd__sprli = c.pyapi.object_getattr_string(mgbrg__akf, 'arrays')
    fqph__uotw = c.pyapi.call_method(ferdd__sprli, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(mgbrg__akf)
    c.pyapi.decref(njs__jkgs)
    c.pyapi.decref(jej__auzfs)
    c.pyapi.decref(ehmk__jgvk)
    c.pyapi.decref(hyj__mwz)
    c.pyapi.decref(hgt__dysr)
    c.pyapi.decref(ferdd__sprli)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return fqph__uotw


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        qze__sic, iuwy__kng = args
        rcwx__saxh = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        rcwx__saxh.data = qze__sic
        rcwx__saxh.null_bitmap = iuwy__kng
        context.nrt.incref(builder, signature.args[0], qze__sic)
        context.nrt.incref(builder, signature.args[1], iuwy__kng)
        return rcwx__saxh._getvalue()
    gpkel__rfv = IntegerArrayType(data.dtype)
    dbyy__dyk = gpkel__rfv(data, null_bitmap)
    return dbyy__dyk, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    dhm__mkzok = np.empty(n, pyval.dtype.type)
    ztwi__pqntr = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        gigs__xlf = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(ztwi__pqntr, i, int(not gigs__xlf)
            )
        if not gigs__xlf:
            dhm__mkzok[i] = s
    whx__oob = context.get_constant_generic(builder, types.Array(typ.dtype,
        1, 'C'), dhm__mkzok)
    qiey__vpa = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), ztwi__pqntr)
    return lir.Constant.literal_struct([whx__oob, qiey__vpa])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    obnys__flf = args[0]
    if equiv_set.has_shape(obnys__flf):
        return ArrayAnalysis.AnalyzeResult(shape=obnys__flf, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    obnys__flf = args[0]
    if equiv_set.has_shape(obnys__flf):
        return ArrayAnalysis.AnalyzeResult(shape=obnys__flf, pre=[])
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
    dhm__mkzok = np.empty(n, dtype)
    nhjd__ouvi = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(dhm__mkzok, nhjd__ouvi)


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
            pbbeh__tta, lrl__urdt = array_getitem_bool_index(A, ind)
            return init_integer_array(pbbeh__tta, lrl__urdt)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            pbbeh__tta, lrl__urdt = array_getitem_int_index(A, ind)
            return init_integer_array(pbbeh__tta, lrl__urdt)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            pbbeh__tta, lrl__urdt = array_getitem_slice_index(A, ind)
            return init_integer_array(pbbeh__tta, lrl__urdt)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    dbkzu__zko = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    voqxi__vgu = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if voqxi__vgu:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(dbkzu__zko)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or voqxi__vgu):
        raise BodoError(dbkzu__zko)
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
            drrfp__rswn = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                drrfp__rswn[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    drrfp__rswn[i] = np.nan
            return drrfp__rswn
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
                qtopz__kbcwp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                axst__nzv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                pvls__tfkhj = qtopz__kbcwp & axst__nzv
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, pvls__tfkhj)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        nlrh__zgvp = n + 7 >> 3
        drrfp__rswn = np.empty(nlrh__zgvp, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            qtopz__kbcwp = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            axst__nzv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            pvls__tfkhj = qtopz__kbcwp & axst__nzv
            bodo.libs.int_arr_ext.set_bit_to_arr(drrfp__rswn, i, pvls__tfkhj)
        return drrfp__rswn
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
    for gnz__gtxh in numba.np.ufunc_db.get_ufuncs():
        quoo__ikw = create_op_overload(gnz__gtxh, gnz__gtxh.nin)
        overload(gnz__gtxh, no_unliteral=True)(quoo__ikw)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        quoo__ikw = create_op_overload(op, 2)
        overload(op)(quoo__ikw)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        quoo__ikw = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(quoo__ikw)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        quoo__ikw = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(quoo__ikw)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    nygp__yqfmq = len(arrs.types)
    ssvb__lqmp = 'def f(arrs):\n'
    fqph__uotw = ', '.join('arrs[{}]._data'.format(i) for i in range(
        nygp__yqfmq))
    ssvb__lqmp += '  return ({}{})\n'.format(fqph__uotw, ',' if nygp__yqfmq ==
        1 else '')
    wpx__jyqxk = {}
    exec(ssvb__lqmp, {}, wpx__jyqxk)
    impl = wpx__jyqxk['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    nygp__yqfmq = len(arrs.types)
    omqlr__wksx = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        nygp__yqfmq))
    ssvb__lqmp = 'def f(arrs):\n'
    ssvb__lqmp += '  n = {}\n'.format(omqlr__wksx)
    ssvb__lqmp += '  n_bytes = (n + 7) >> 3\n'
    ssvb__lqmp += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    ssvb__lqmp += '  curr_bit = 0\n'
    for i in range(nygp__yqfmq):
        ssvb__lqmp += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        ssvb__lqmp += '  for j in range(len(arrs[{}])):\n'.format(i)
        ssvb__lqmp += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        ssvb__lqmp += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        ssvb__lqmp += '    curr_bit += 1\n'
    ssvb__lqmp += '  return new_mask\n'
    wpx__jyqxk = {}
    exec(ssvb__lqmp, {'np': np, 'bodo': bodo}, wpx__jyqxk)
    impl = wpx__jyqxk['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    wmpfj__cyk = dict(skipna=skipna, min_count=min_count)
    ewdg__mztr = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', wmpfj__cyk, ewdg__mztr)

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
        bnubk__xuba = []
        trkbx__bckhw = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not trkbx__bckhw:
                    data.append(dtype(1))
                    bnubk__xuba.append(False)
                    trkbx__bckhw = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                bnubk__xuba.append(True)
        pbbeh__tta = np.array(data)
        n = len(pbbeh__tta)
        nlrh__zgvp = n + 7 >> 3
        lrl__urdt = np.empty(nlrh__zgvp, np.uint8)
        for yeuj__not in range(n):
            set_bit_to_arr(lrl__urdt, yeuj__not, bnubk__xuba[yeuj__not])
        return init_integer_array(pbbeh__tta, lrl__urdt)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    vljqb__ryo = numba.core.registry.cpu_target.typing_context
    zdjsp__hmv = vljqb__ryo.resolve_function_type(op, (types.Array(A.dtype,
        1, 'C'),), {}).return_type
    zdjsp__hmv = to_nullable_type(zdjsp__hmv)

    def impl(A):
        n = len(A)
        ziqb__egdp = bodo.utils.utils.alloc_type(n, zdjsp__hmv, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(ziqb__egdp, i)
                continue
            ziqb__egdp[i] = op(A[i])
        return ziqb__egdp
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    zjv__erxp = isinstance(lhs, (types.Number, types.Boolean))
    kalj__jsg = isinstance(rhs, (types.Number, types.Boolean))
    ploow__pxpj = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    rqw__atrj = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    vljqb__ryo = numba.core.registry.cpu_target.typing_context
    zdjsp__hmv = vljqb__ryo.resolve_function_type(op, (ploow__pxpj,
        rqw__atrj), {}).return_type
    zdjsp__hmv = to_nullable_type(zdjsp__hmv)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    vmylc__oqoq = 'lhs' if zjv__erxp else 'lhs[i]'
    lbkae__xwo = 'rhs' if kalj__jsg else 'rhs[i]'
    qhst__ngpa = ('False' if zjv__erxp else
        'bodo.libs.array_kernels.isna(lhs, i)')
    lmhd__btrbl = ('False' if kalj__jsg else
        'bodo.libs.array_kernels.isna(rhs, i)')
    ssvb__lqmp = 'def impl(lhs, rhs):\n'
    ssvb__lqmp += '  n = len({})\n'.format('lhs' if not zjv__erxp else 'rhs')
    if inplace:
        ssvb__lqmp += '  out_arr = {}\n'.format('lhs' if not zjv__erxp else
            'rhs')
    else:
        ssvb__lqmp += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    ssvb__lqmp += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ssvb__lqmp += '    if ({}\n'.format(qhst__ngpa)
    ssvb__lqmp += '        or {}):\n'.format(lmhd__btrbl)
    ssvb__lqmp += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    ssvb__lqmp += '      continue\n'
    ssvb__lqmp += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(vmylc__oqoq, lbkae__xwo))
    ssvb__lqmp += '  return out_arr\n'
    wpx__jyqxk = {}
    exec(ssvb__lqmp, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        zdjsp__hmv, 'op': op}, wpx__jyqxk)
    impl = wpx__jyqxk['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        zjv__erxp = lhs in [pd_timedelta_type]
        kalj__jsg = rhs in [pd_timedelta_type]
        if zjv__erxp:

            def impl(lhs, rhs):
                n = len(rhs)
                ziqb__egdp = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(ziqb__egdp, i)
                        continue
                    ziqb__egdp[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return ziqb__egdp
            return impl
        elif kalj__jsg:

            def impl(lhs, rhs):
                n = len(lhs)
                ziqb__egdp = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(ziqb__egdp, i)
                        continue
                    ziqb__egdp[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return ziqb__egdp
            return impl
    return impl
