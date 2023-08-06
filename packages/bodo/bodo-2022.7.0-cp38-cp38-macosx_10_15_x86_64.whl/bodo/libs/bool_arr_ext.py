"""Nullable boolean array that stores data in Numpy format (1 byte per value)
but nulls are stored in bit arrays (1 bit per value) similar to Arrow's nulls.
Pandas converts boolean array to object when NAs are introduced.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import NativeValue, box, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.libs.str_arr_ext import string_array_type
from bodo.utils.typing import is_list_like_index_type
ll.add_symbol('is_bool_array', hstr_ext.is_bool_array)
ll.add_symbol('is_pd_boolean_array', hstr_ext.is_pd_boolean_array)
ll.add_symbol('unbox_bool_array_obj', hstr_ext.unbox_bool_array_obj)
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_overload_false, is_overload_true, parse_dtype, raise_bodo_error


class BooleanArrayType(types.ArrayCompatible):

    def __init__(self):
        super(BooleanArrayType, self).__init__(name='BooleanArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.bool_

    def copy(self):
        return BooleanArrayType()


boolean_array = BooleanArrayType()


@typeof_impl.register(pd.arrays.BooleanArray)
def typeof_boolean_array(val, c):
    return boolean_array


data_type = types.Array(types.bool_, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(BooleanArrayType)
class BooleanArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ziai__cfst = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, ziai__cfst)


make_attribute_wrapper(BooleanArrayType, 'data', '_data')
make_attribute_wrapper(BooleanArrayType, 'null_bitmap', '_null_bitmap')


class BooleanDtype(types.Number):

    def __init__(self):
        self.dtype = types.bool_
        super(BooleanDtype, self).__init__('BooleanDtype')


boolean_dtype = BooleanDtype()
register_model(BooleanDtype)(models.OpaqueModel)


@box(BooleanDtype)
def box_boolean_dtype(typ, val, c):
    lkiw__onihr = c.context.insert_const_string(c.builder.module, 'pandas')
    hdpt__atrc = c.pyapi.import_module_noblock(lkiw__onihr)
    vxopq__titiv = c.pyapi.call_method(hdpt__atrc, 'BooleanDtype', ())
    c.pyapi.decref(hdpt__atrc)
    return vxopq__titiv


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    txqob__efye = n + 7 >> 3
    return np.full(txqob__efye, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    sgpmv__gqkj = c.context.typing_context.resolve_value_type(func)
    ojh__ayuz = sgpmv__gqkj.get_call_type(c.context.typing_context,
        arg_typs, {})
    cwgkr__rgro = c.context.get_function(sgpmv__gqkj, ojh__ayuz)
    nhdgc__euiz = c.context.call_conv.get_function_type(ojh__ayuz.
        return_type, ojh__ayuz.args)
    ohct__ddik = c.builder.module
    ofjty__sdgi = lir.Function(ohct__ddik, nhdgc__euiz, name=ohct__ddik.
        get_unique_name('.func_conv'))
    ofjty__sdgi.linkage = 'internal'
    zkwp__zgl = lir.IRBuilder(ofjty__sdgi.append_basic_block())
    kknn__fjdk = c.context.call_conv.decode_arguments(zkwp__zgl, ojh__ayuz.
        args, ofjty__sdgi)
    zewx__udvic = cwgkr__rgro(zkwp__zgl, kknn__fjdk)
    c.context.call_conv.return_value(zkwp__zgl, zewx__udvic)
    fmjcg__ikxwz, zkr__kvxb = c.context.call_conv.call_function(c.builder,
        ofjty__sdgi, ojh__ayuz.return_type, ojh__ayuz.args, args)
    return zkr__kvxb


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    uct__fhgg = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(uct__fhgg)
    c.pyapi.decref(uct__fhgg)
    nhdgc__euiz = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    rcvm__jfc = cgutils.get_or_insert_function(c.builder.module,
        nhdgc__euiz, name='is_bool_array')
    nhdgc__euiz = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    ofjty__sdgi = cgutils.get_or_insert_function(c.builder.module,
        nhdgc__euiz, name='is_pd_boolean_array')
    wjfkq__gku = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    olw__enbz = c.builder.call(ofjty__sdgi, [obj])
    nbh__njwjw = c.builder.icmp_unsigned('!=', olw__enbz, olw__enbz.type(0))
    with c.builder.if_else(nbh__njwjw) as (qthm__lgptk, uoy__aqy):
        with qthm__lgptk:
            dmgv__xrvep = c.pyapi.object_getattr_string(obj, '_data')
            wjfkq__gku.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), dmgv__xrvep).value
            qxtr__yikd = c.pyapi.object_getattr_string(obj, '_mask')
            hsnyk__vbivd = c.pyapi.to_native_value(types.Array(types.bool_,
                1, 'C'), qxtr__yikd).value
            txqob__efye = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            fwf__yspg = c.context.make_array(types.Array(types.bool_, 1, 'C'))(
                c.context, c.builder, hsnyk__vbivd)
            ibxq__vzt = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [txqob__efye])
            nhdgc__euiz = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            ofjty__sdgi = cgutils.get_or_insert_function(c.builder.module,
                nhdgc__euiz, name='mask_arr_to_bitmap')
            c.builder.call(ofjty__sdgi, [ibxq__vzt.data, fwf__yspg.data, n])
            wjfkq__gku.null_bitmap = ibxq__vzt._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), hsnyk__vbivd)
            c.pyapi.decref(dmgv__xrvep)
            c.pyapi.decref(qxtr__yikd)
        with uoy__aqy:
            qnar__qocnv = c.builder.call(rcvm__jfc, [obj])
            bougl__ealck = c.builder.icmp_unsigned('!=', qnar__qocnv,
                qnar__qocnv.type(0))
            with c.builder.if_else(bougl__ealck) as (otyaz__lepy, kmu__ajt):
                with otyaz__lepy:
                    wjfkq__gku.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    wjfkq__gku.null_bitmap = call_func_in_unbox(gen_full_bitmap
                        , (n,), (types.int64,), c)
                with kmu__ajt:
                    wjfkq__gku.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    txqob__efye = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    wjfkq__gku.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [txqob__efye])._getvalue()
                    uqpvn__kuao = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, wjfkq__gku.data
                        ).data
                    qgz__ssdzi = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, wjfkq__gku.
                        null_bitmap).data
                    nhdgc__euiz = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    ofjty__sdgi = cgutils.get_or_insert_function(c.builder.
                        module, nhdgc__euiz, name='unbox_bool_array_obj')
                    c.builder.call(ofjty__sdgi, [obj, uqpvn__kuao,
                        qgz__ssdzi, n])
    return NativeValue(wjfkq__gku._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    wjfkq__gku = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        wjfkq__gku.data, c.env_manager)
    vmq__dtsig = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, wjfkq__gku.null_bitmap).data
    uct__fhgg = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(uct__fhgg)
    lkiw__onihr = c.context.insert_const_string(c.builder.module, 'numpy')
    cgujp__djonw = c.pyapi.import_module_noblock(lkiw__onihr)
    qok__aytw = c.pyapi.object_getattr_string(cgujp__djonw, 'bool_')
    hsnyk__vbivd = c.pyapi.call_method(cgujp__djonw, 'empty', (uct__fhgg,
        qok__aytw))
    evtrb__mmor = c.pyapi.object_getattr_string(hsnyk__vbivd, 'ctypes')
    wfrv__ibkm = c.pyapi.object_getattr_string(evtrb__mmor, 'data')
    vin__ebsz = c.builder.inttoptr(c.pyapi.long_as_longlong(wfrv__ibkm),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as iubo__qyc:
        nygy__gfbrt = iubo__qyc.index
        ezy__kxf = c.builder.lshr(nygy__gfbrt, lir.Constant(lir.IntType(64), 3)
            )
        uclq__moaw = c.builder.load(cgutils.gep(c.builder, vmq__dtsig,
            ezy__kxf))
        fqu__cuu = c.builder.trunc(c.builder.and_(nygy__gfbrt, lir.Constant
            (lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(uclq__moaw, fqu__cuu), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        own__rqj = cgutils.gep(c.builder, vin__ebsz, nygy__gfbrt)
        c.builder.store(val, own__rqj)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        wjfkq__gku.null_bitmap)
    lkiw__onihr = c.context.insert_const_string(c.builder.module, 'pandas')
    hdpt__atrc = c.pyapi.import_module_noblock(lkiw__onihr)
    qxy__str = c.pyapi.object_getattr_string(hdpt__atrc, 'arrays')
    vxopq__titiv = c.pyapi.call_method(qxy__str, 'BooleanArray', (data,
        hsnyk__vbivd))
    c.pyapi.decref(hdpt__atrc)
    c.pyapi.decref(uct__fhgg)
    c.pyapi.decref(cgujp__djonw)
    c.pyapi.decref(qok__aytw)
    c.pyapi.decref(evtrb__mmor)
    c.pyapi.decref(wfrv__ibkm)
    c.pyapi.decref(qxy__str)
    c.pyapi.decref(data)
    c.pyapi.decref(hsnyk__vbivd)
    return vxopq__titiv


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    ztq__humxd = np.empty(n, np.bool_)
    yap__gug = np.empty(n + 7 >> 3, np.uint8)
    for nygy__gfbrt, s in enumerate(pyval):
        dadhr__rubd = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(yap__gug, nygy__gfbrt, int(not
            dadhr__rubd))
        if not dadhr__rubd:
            ztq__humxd[nygy__gfbrt] = s
    rxfdm__cmaj = context.get_constant_generic(builder, data_type, ztq__humxd)
    axtqi__wlt = context.get_constant_generic(builder, nulls_type, yap__gug)
    return lir.Constant.literal_struct([rxfdm__cmaj, axtqi__wlt])


def lower_init_bool_array(context, builder, signature, args):
    bsgo__cen, adg__hwvoc = args
    wjfkq__gku = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    wjfkq__gku.data = bsgo__cen
    wjfkq__gku.null_bitmap = adg__hwvoc
    context.nrt.incref(builder, signature.args[0], bsgo__cen)
    context.nrt.incref(builder, signature.args[1], adg__hwvoc)
    return wjfkq__gku._getvalue()


@intrinsic
def init_bool_array(typingctx, data, null_bitmap=None):
    assert data == types.Array(types.bool_, 1, 'C')
    assert null_bitmap == types.Array(types.uint8, 1, 'C')
    sig = boolean_array(data, null_bitmap)
    return sig, lower_init_bool_array


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_bool_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    yfvgq__tod = args[0]
    if equiv_set.has_shape(yfvgq__tod):
        return ArrayAnalysis.AnalyzeResult(shape=yfvgq__tod, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    yfvgq__tod = args[0]
    if equiv_set.has_shape(yfvgq__tod):
        return ArrayAnalysis.AnalyzeResult(shape=yfvgq__tod, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_init_bool_array = (
    init_bool_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_bool_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_bool_array',
    'bodo.libs.bool_arr_ext'] = alias_ext_init_bool_array
numba.core.ir_utils.alias_func_extensions['get_bool_arr_data',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_bool_arr_bitmap',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_bool_array(n):
    ztq__humxd = np.empty(n, dtype=np.bool_)
    wllm__eis = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(ztq__humxd, wllm__eis)


def alloc_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_alloc_bool_array = (
    alloc_bool_array_equiv)


@overload(operator.getitem, no_unliteral=True)
def bool_arr_getitem(A, ind):
    if A != boolean_array:
        return
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            cgc__irpjt, yuq__llf = array_getitem_bool_index(A, ind)
            return init_bool_array(cgc__irpjt, yuq__llf)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            cgc__irpjt, yuq__llf = array_getitem_int_index(A, ind)
            return init_bool_array(cgc__irpjt, yuq__llf)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            cgc__irpjt, yuq__llf = array_getitem_slice_index(A, ind)
            return init_bool_array(cgc__irpjt, yuq__llf)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    yeou__mbc = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(yeou__mbc)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(yeou__mbc)
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
        f'setitem for BooleanArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_bool_arr_len(A):
    if A == boolean_array:
        return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'size')
def overload_bool_arr_size(A):
    return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'shape')
def overload_bool_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(BooleanArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: pd.BooleanDtype()


@overload_attribute(BooleanArrayType, 'ndim')
def overload_bool_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BooleanArrayType, 'nbytes')
def bool_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(BooleanArrayType, 'copy', no_unliteral=True)
def overload_bool_arr_copy(A):
    return lambda A: bodo.libs.bool_arr_ext.init_bool_array(bodo.libs.
        bool_arr_ext.get_bool_arr_data(A).copy(), bodo.libs.bool_arr_ext.
        get_bool_arr_bitmap(A).copy())


@overload_method(BooleanArrayType, 'sum', no_unliteral=True, inline='always')
def overload_bool_sum(A):

    def impl(A):
        numba.parfors.parfor.init_prange()
        s = 0
        for nygy__gfbrt in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, nygy__gfbrt):
                val = A[nygy__gfbrt]
            s += val
        return s
    return impl


@overload_method(BooleanArrayType, 'astype', no_unliteral=True)
def overload_bool_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "BooleanArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if dtype == types.bool_:
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
    nb_dtype = parse_dtype(dtype, 'BooleanArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
            n = len(data)
            odzk__mdgn = np.empty(n, nb_dtype)
            for nygy__gfbrt in numba.parfors.parfor.internal_prange(n):
                odzk__mdgn[nygy__gfbrt] = data[nygy__gfbrt]
                if bodo.libs.array_kernels.isna(A, nygy__gfbrt):
                    odzk__mdgn[nygy__gfbrt] = np.nan
            return odzk__mdgn
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        odzk__mdgn = np.empty(n, dtype=np.bool_)
        for nygy__gfbrt in numba.parfors.parfor.internal_prange(n):
            odzk__mdgn[nygy__gfbrt] = data[nygy__gfbrt]
            if bodo.libs.array_kernels.isna(A, nygy__gfbrt):
                odzk__mdgn[nygy__gfbrt] = value
        return odzk__mdgn
    return impl


@overload(str, no_unliteral=True)
def overload_str_bool(val):
    if val == types.bool_:

        def impl(val):
            if val:
                return 'True'
            return 'False'
        return impl


ufunc_aliases = {'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    mvmqp__ocm = op.__name__
    mvmqp__ocm = ufunc_aliases.get(mvmqp__ocm, mvmqp__ocm)
    if n_inputs == 1:

        def overload_bool_arr_op_nin_1(A):
            if isinstance(A, BooleanArrayType):
                return bodo.libs.int_arr_ext.get_nullable_array_unary_impl(op,
                    A)
        return overload_bool_arr_op_nin_1
    elif n_inputs == 2:

        def overload_bool_arr_op_nin_2(lhs, rhs):
            if lhs == boolean_array or rhs == boolean_array:
                return bodo.libs.int_arr_ext.get_nullable_array_binary_impl(op,
                    lhs, rhs)
        return overload_bool_arr_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for zjz__cslq in numba.np.ufunc_db.get_ufuncs():
        vqa__igkv = create_op_overload(zjz__cslq, zjz__cslq.nin)
        overload(zjz__cslq, no_unliteral=True)(vqa__igkv)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        vqa__igkv = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vqa__igkv)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        vqa__igkv = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vqa__igkv)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        vqa__igkv = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(vqa__igkv)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        fqu__cuu = []
        yckc__cffnz = False
        quy__diow = False
        osv__qvrkc = False
        for nygy__gfbrt in range(len(A)):
            if bodo.libs.array_kernels.isna(A, nygy__gfbrt):
                if not yckc__cffnz:
                    data.append(False)
                    fqu__cuu.append(False)
                    yckc__cffnz = True
                continue
            val = A[nygy__gfbrt]
            if val and not quy__diow:
                data.append(True)
                fqu__cuu.append(True)
                quy__diow = True
            if not val and not osv__qvrkc:
                data.append(False)
                fqu__cuu.append(True)
                osv__qvrkc = True
            if yckc__cffnz and quy__diow and osv__qvrkc:
                break
        cgc__irpjt = np.array(data)
        n = len(cgc__irpjt)
        txqob__efye = 1
        yuq__llf = np.empty(txqob__efye, np.uint8)
        for wyi__tzpi in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(yuq__llf, wyi__tzpi,
                fqu__cuu[wyi__tzpi])
        return init_bool_array(cgc__irpjt, yuq__llf)
    return impl_bool_arr


@overload(operator.getitem, no_unliteral=True)
def bool_arr_ind_getitem(A, ind):
    if ind == boolean_array and (isinstance(A, (types.Array, bodo.libs.
        int_arr_ext.IntegerArrayType)) or isinstance(A, bodo.libs.
        struct_arr_ext.StructArrayType) or isinstance(A, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType) or isinstance(A, bodo.libs.
        map_arr_ext.MapArrayType) or A in (string_array_type, bodo.hiframes
        .split_impl.string_array_split_view_type, boolean_array)):
        return lambda A, ind: A[ind._data]


@lower_cast(types.Array(types.bool_, 1, 'C'), boolean_array)
def cast_np_bool_arr_to_bool_arr(context, builder, fromty, toty, val):
    func = lambda A: bodo.libs.bool_arr_ext.init_bool_array(A, np.full(len(
        A) + 7 >> 3, 255, np.uint8))
    vxopq__titiv = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, vxopq__titiv)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    ctcxv__rrs = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        qtz__khy = bodo.utils.utils.is_array_typ(val1, False)
        shq__jyl = bodo.utils.utils.is_array_typ(val2, False)
        boyn__jgc = 'val1' if qtz__khy else 'val2'
        ufezn__dstg = 'def impl(val1, val2):\n'
        ufezn__dstg += f'  n = len({boyn__jgc})\n'
        ufezn__dstg += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        ufezn__dstg += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if qtz__khy:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            jgiyw__juqw = 'val1[i]'
        else:
            null1 = 'False\n'
            jgiyw__juqw = 'val1'
        if shq__jyl:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            mldb__rkbri = 'val2[i]'
        else:
            null2 = 'False\n'
            mldb__rkbri = 'val2'
        if ctcxv__rrs:
            ufezn__dstg += f"""    result, isna_val = compute_or_body({null1}, {null2}, {jgiyw__juqw}, {mldb__rkbri})
"""
        else:
            ufezn__dstg += f"""    result, isna_val = compute_and_body({null1}, {null2}, {jgiyw__juqw}, {mldb__rkbri})
"""
        ufezn__dstg += '    out_arr[i] = result\n'
        ufezn__dstg += '    if isna_val:\n'
        ufezn__dstg += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        ufezn__dstg += '      continue\n'
        ufezn__dstg += '  return out_arr\n'
        mfdky__gcux = {}
        exec(ufezn__dstg, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, mfdky__gcux)
        impl = mfdky__gcux['impl']
        return impl
    return bool_array_impl


def compute_or_body(null1, null2, val1, val2):
    pass


@overload(compute_or_body)
def overload_compute_or_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == False
        elif null2:
            return val1, val1 == False
        else:
            return val1 | val2, False
    return impl


def compute_and_body(null1, null2, val1, val2):
    pass


@overload(compute_and_body)
def overload_compute_and_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == True
        elif null2:
            return val1, val1 == True
        else:
            return val1 & val2, False
    return impl


def create_boolean_array_logical_lower_impl(op):

    def logical_lower_impl(context, builder, sig, args):
        impl = create_nullable_logical_op_overload(op)(*sig.args)
        return context.compile_internal(builder, impl, sig, args)
    return logical_lower_impl


class BooleanArrayLogicalOperatorTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        if not is_valid_boolean_array_logical_op(args[0], args[1]):
            return
        make__fzwml = boolean_array
        return make__fzwml(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    cvmk__xgf = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return cvmk__xgf


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        froy__wupr = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(froy__wupr)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(froy__wupr)


_install_nullable_logical_lowering()
