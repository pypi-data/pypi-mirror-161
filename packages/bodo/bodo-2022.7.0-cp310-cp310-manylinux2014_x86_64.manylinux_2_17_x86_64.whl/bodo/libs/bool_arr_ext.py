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
        ylv__byoaw = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, ylv__byoaw)


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
    fbev__iovv = c.context.insert_const_string(c.builder.module, 'pandas')
    xaph__drnmn = c.pyapi.import_module_noblock(fbev__iovv)
    ybx__kqwss = c.pyapi.call_method(xaph__drnmn, 'BooleanDtype', ())
    c.pyapi.decref(xaph__drnmn)
    return ybx__kqwss


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    glet__fmev = n + 7 >> 3
    return np.full(glet__fmev, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    hna__oxn = c.context.typing_context.resolve_value_type(func)
    oog__ynbsq = hna__oxn.get_call_type(c.context.typing_context, arg_typs, {})
    hmety__yyo = c.context.get_function(hna__oxn, oog__ynbsq)
    dxqb__qiq = c.context.call_conv.get_function_type(oog__ynbsq.
        return_type, oog__ynbsq.args)
    fcgc__qtva = c.builder.module
    stb__afpaf = lir.Function(fcgc__qtva, dxqb__qiq, name=fcgc__qtva.
        get_unique_name('.func_conv'))
    stb__afpaf.linkage = 'internal'
    ill__tvhk = lir.IRBuilder(stb__afpaf.append_basic_block())
    bwl__bwnt = c.context.call_conv.decode_arguments(ill__tvhk, oog__ynbsq.
        args, stb__afpaf)
    fnle__art = hmety__yyo(ill__tvhk, bwl__bwnt)
    c.context.call_conv.return_value(ill__tvhk, fnle__art)
    xsvqj__wqyl, vcafv__efs = c.context.call_conv.call_function(c.builder,
        stb__afpaf, oog__ynbsq.return_type, oog__ynbsq.args, args)
    return vcafv__efs


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    ueb__qbi = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(ueb__qbi)
    c.pyapi.decref(ueb__qbi)
    dxqb__qiq = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    sut__frefd = cgutils.get_or_insert_function(c.builder.module, dxqb__qiq,
        name='is_bool_array')
    dxqb__qiq = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    stb__afpaf = cgutils.get_or_insert_function(c.builder.module, dxqb__qiq,
        name='is_pd_boolean_array')
    vis__dttp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    aje__occtn = c.builder.call(stb__afpaf, [obj])
    pksso__sivy = c.builder.icmp_unsigned('!=', aje__occtn, aje__occtn.type(0))
    with c.builder.if_else(pksso__sivy) as (zwawf__kts, vnb__sgn):
        with zwawf__kts:
            bdfnh__wija = c.pyapi.object_getattr_string(obj, '_data')
            vis__dttp.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), bdfnh__wija).value
            zpgkp__toszo = c.pyapi.object_getattr_string(obj, '_mask')
            ewc__zzd = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), zpgkp__toszo).value
            glet__fmev = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            kcj__kxy = c.context.make_array(types.Array(types.bool_, 1, 'C'))(c
                .context, c.builder, ewc__zzd)
            rix__jynp = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [glet__fmev])
            dxqb__qiq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            stb__afpaf = cgutils.get_or_insert_function(c.builder.module,
                dxqb__qiq, name='mask_arr_to_bitmap')
            c.builder.call(stb__afpaf, [rix__jynp.data, kcj__kxy.data, n])
            vis__dttp.null_bitmap = rix__jynp._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), ewc__zzd)
            c.pyapi.decref(bdfnh__wija)
            c.pyapi.decref(zpgkp__toszo)
        with vnb__sgn:
            bmql__asvc = c.builder.call(sut__frefd, [obj])
            frt__dwix = c.builder.icmp_unsigned('!=', bmql__asvc,
                bmql__asvc.type(0))
            with c.builder.if_else(frt__dwix) as (omiic__srx, uzx__edgfs):
                with omiic__srx:
                    vis__dttp.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    vis__dttp.null_bitmap = call_func_in_unbox(gen_full_bitmap,
                        (n,), (types.int64,), c)
                with uzx__edgfs:
                    vis__dttp.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    glet__fmev = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    vis__dttp.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [glet__fmev])._getvalue()
                    pgdqj__yzbsn = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, vis__dttp.data
                        ).data
                    wzoym__jndn = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, vis__dttp.
                        null_bitmap).data
                    dxqb__qiq = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    stb__afpaf = cgutils.get_or_insert_function(c.builder.
                        module, dxqb__qiq, name='unbox_bool_array_obj')
                    c.builder.call(stb__afpaf, [obj, pgdqj__yzbsn,
                        wzoym__jndn, n])
    return NativeValue(vis__dttp._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    vis__dttp = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        vis__dttp.data, c.env_manager)
    xig__zptzl = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, vis__dttp.null_bitmap).data
    ueb__qbi = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(ueb__qbi)
    fbev__iovv = c.context.insert_const_string(c.builder.module, 'numpy')
    fmm__ige = c.pyapi.import_module_noblock(fbev__iovv)
    rgsk__gosu = c.pyapi.object_getattr_string(fmm__ige, 'bool_')
    ewc__zzd = c.pyapi.call_method(fmm__ige, 'empty', (ueb__qbi, rgsk__gosu))
    jwck__jhd = c.pyapi.object_getattr_string(ewc__zzd, 'ctypes')
    eyak__hjjn = c.pyapi.object_getattr_string(jwck__jhd, 'data')
    vbvcd__tyheg = c.builder.inttoptr(c.pyapi.long_as_longlong(eyak__hjjn),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as cqnn__gkpr:
        ahl__jgcgy = cqnn__gkpr.index
        pwd__tlhfi = c.builder.lshr(ahl__jgcgy, lir.Constant(lir.IntType(64
            ), 3))
        xfani__dlqfu = c.builder.load(cgutils.gep(c.builder, xig__zptzl,
            pwd__tlhfi))
        wqqj__ijkk = c.builder.trunc(c.builder.and_(ahl__jgcgy, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(xfani__dlqfu, wqqj__ijkk), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        mwzro__zqzr = cgutils.gep(c.builder, vbvcd__tyheg, ahl__jgcgy)
        c.builder.store(val, mwzro__zqzr)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        vis__dttp.null_bitmap)
    fbev__iovv = c.context.insert_const_string(c.builder.module, 'pandas')
    xaph__drnmn = c.pyapi.import_module_noblock(fbev__iovv)
    nmngo__npypb = c.pyapi.object_getattr_string(xaph__drnmn, 'arrays')
    ybx__kqwss = c.pyapi.call_method(nmngo__npypb, 'BooleanArray', (data,
        ewc__zzd))
    c.pyapi.decref(xaph__drnmn)
    c.pyapi.decref(ueb__qbi)
    c.pyapi.decref(fmm__ige)
    c.pyapi.decref(rgsk__gosu)
    c.pyapi.decref(jwck__jhd)
    c.pyapi.decref(eyak__hjjn)
    c.pyapi.decref(nmngo__npypb)
    c.pyapi.decref(data)
    c.pyapi.decref(ewc__zzd)
    return ybx__kqwss


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    xtwk__xboig = np.empty(n, np.bool_)
    aby__lsx = np.empty(n + 7 >> 3, np.uint8)
    for ahl__jgcgy, s in enumerate(pyval):
        ogbt__hya = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(aby__lsx, ahl__jgcgy, int(not
            ogbt__hya))
        if not ogbt__hya:
            xtwk__xboig[ahl__jgcgy] = s
    gbdpb__ubr = context.get_constant_generic(builder, data_type, xtwk__xboig)
    isxb__woi = context.get_constant_generic(builder, nulls_type, aby__lsx)
    return lir.Constant.literal_struct([gbdpb__ubr, isxb__woi])


def lower_init_bool_array(context, builder, signature, args):
    hact__yosm, zlw__khrl = args
    vis__dttp = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    vis__dttp.data = hact__yosm
    vis__dttp.null_bitmap = zlw__khrl
    context.nrt.incref(builder, signature.args[0], hact__yosm)
    context.nrt.incref(builder, signature.args[1], zlw__khrl)
    return vis__dttp._getvalue()


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
    wkv__jccp = args[0]
    if equiv_set.has_shape(wkv__jccp):
        return ArrayAnalysis.AnalyzeResult(shape=wkv__jccp, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    wkv__jccp = args[0]
    if equiv_set.has_shape(wkv__jccp):
        return ArrayAnalysis.AnalyzeResult(shape=wkv__jccp, pre=[])
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
    xtwk__xboig = np.empty(n, dtype=np.bool_)
    iunyk__tic = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(xtwk__xboig, iunyk__tic)


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
            hpu__mtjh, kuj__usned = array_getitem_bool_index(A, ind)
            return init_bool_array(hpu__mtjh, kuj__usned)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            hpu__mtjh, kuj__usned = array_getitem_int_index(A, ind)
            return init_bool_array(hpu__mtjh, kuj__usned)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            hpu__mtjh, kuj__usned = array_getitem_slice_index(A, ind)
            return init_bool_array(hpu__mtjh, kuj__usned)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    jqr__bxl = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(jqr__bxl)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(jqr__bxl)
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
        for ahl__jgcgy in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, ahl__jgcgy):
                val = A[ahl__jgcgy]
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
            rjovy__anlm = np.empty(n, nb_dtype)
            for ahl__jgcgy in numba.parfors.parfor.internal_prange(n):
                rjovy__anlm[ahl__jgcgy] = data[ahl__jgcgy]
                if bodo.libs.array_kernels.isna(A, ahl__jgcgy):
                    rjovy__anlm[ahl__jgcgy] = np.nan
            return rjovy__anlm
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        rjovy__anlm = np.empty(n, dtype=np.bool_)
        for ahl__jgcgy in numba.parfors.parfor.internal_prange(n):
            rjovy__anlm[ahl__jgcgy] = data[ahl__jgcgy]
            if bodo.libs.array_kernels.isna(A, ahl__jgcgy):
                rjovy__anlm[ahl__jgcgy] = value
        return rjovy__anlm
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
    pde__uudg = op.__name__
    pde__uudg = ufunc_aliases.get(pde__uudg, pde__uudg)
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
    for diu__wzqpz in numba.np.ufunc_db.get_ufuncs():
        uibt__qlmjn = create_op_overload(diu__wzqpz, diu__wzqpz.nin)
        overload(diu__wzqpz, no_unliteral=True)(uibt__qlmjn)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        uibt__qlmjn = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(uibt__qlmjn)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        uibt__qlmjn = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(uibt__qlmjn)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        uibt__qlmjn = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(uibt__qlmjn)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        wqqj__ijkk = []
        tatq__aqx = False
        ias__vdsqj = False
        okzib__jemgq = False
        for ahl__jgcgy in range(len(A)):
            if bodo.libs.array_kernels.isna(A, ahl__jgcgy):
                if not tatq__aqx:
                    data.append(False)
                    wqqj__ijkk.append(False)
                    tatq__aqx = True
                continue
            val = A[ahl__jgcgy]
            if val and not ias__vdsqj:
                data.append(True)
                wqqj__ijkk.append(True)
                ias__vdsqj = True
            if not val and not okzib__jemgq:
                data.append(False)
                wqqj__ijkk.append(True)
                okzib__jemgq = True
            if tatq__aqx and ias__vdsqj and okzib__jemgq:
                break
        hpu__mtjh = np.array(data)
        n = len(hpu__mtjh)
        glet__fmev = 1
        kuj__usned = np.empty(glet__fmev, np.uint8)
        for albd__paaci in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(kuj__usned, albd__paaci,
                wqqj__ijkk[albd__paaci])
        return init_bool_array(hpu__mtjh, kuj__usned)
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
    ybx__kqwss = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, ybx__kqwss)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    hfeqm__unp = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        fmjrw__giymz = bodo.utils.utils.is_array_typ(val1, False)
        ehma__ipig = bodo.utils.utils.is_array_typ(val2, False)
        qpxw__hzac = 'val1' if fmjrw__giymz else 'val2'
        nsgg__jmj = 'def impl(val1, val2):\n'
        nsgg__jmj += f'  n = len({qpxw__hzac})\n'
        nsgg__jmj += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        nsgg__jmj += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if fmjrw__giymz:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            yjph__pycyx = 'val1[i]'
        else:
            null1 = 'False\n'
            yjph__pycyx = 'val1'
        if ehma__ipig:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            vvf__jpnt = 'val2[i]'
        else:
            null2 = 'False\n'
            vvf__jpnt = 'val2'
        if hfeqm__unp:
            nsgg__jmj += f"""    result, isna_val = compute_or_body({null1}, {null2}, {yjph__pycyx}, {vvf__jpnt})
"""
        else:
            nsgg__jmj += f"""    result, isna_val = compute_and_body({null1}, {null2}, {yjph__pycyx}, {vvf__jpnt})
"""
        nsgg__jmj += '    out_arr[i] = result\n'
        nsgg__jmj += '    if isna_val:\n'
        nsgg__jmj += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        nsgg__jmj += '      continue\n'
        nsgg__jmj += '  return out_arr\n'
        gxamp__ywbcn = {}
        exec(nsgg__jmj, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, gxamp__ywbcn
            )
        impl = gxamp__ywbcn['impl']
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
        ykdrh__xuwjd = boolean_array
        return ykdrh__xuwjd(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    roa__fcs = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array) and (
        bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype == types.
        bool_ or typ1 == types.bool_) and (bodo.utils.utils.is_array_typ(
        typ2, False) and typ2.dtype == types.bool_ or typ2 == types.bool_)
    return roa__fcs


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        trdbm__bfc = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(trdbm__bfc)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(trdbm__bfc)


_install_nullable_logical_lowering()
