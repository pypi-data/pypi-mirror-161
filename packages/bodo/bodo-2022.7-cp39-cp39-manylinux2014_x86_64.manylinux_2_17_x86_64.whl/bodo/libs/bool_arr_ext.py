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
        jvj__mxcpc = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, jvj__mxcpc)


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
    raaev__snko = c.context.insert_const_string(c.builder.module, 'pandas')
    kvc__hegd = c.pyapi.import_module_noblock(raaev__snko)
    jty__asbk = c.pyapi.call_method(kvc__hegd, 'BooleanDtype', ())
    c.pyapi.decref(kvc__hegd)
    return jty__asbk


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    tqfd__rkux = n + 7 >> 3
    return np.full(tqfd__rkux, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    fdvf__yjgef = c.context.typing_context.resolve_value_type(func)
    zqx__xfbvv = fdvf__yjgef.get_call_type(c.context.typing_context,
        arg_typs, {})
    pdpa__yhzep = c.context.get_function(fdvf__yjgef, zqx__xfbvv)
    fzlnl__jslr = c.context.call_conv.get_function_type(zqx__xfbvv.
        return_type, zqx__xfbvv.args)
    wij__zder = c.builder.module
    bjx__rgrt = lir.Function(wij__zder, fzlnl__jslr, name=wij__zder.
        get_unique_name('.func_conv'))
    bjx__rgrt.linkage = 'internal'
    xhg__uja = lir.IRBuilder(bjx__rgrt.append_basic_block())
    vejb__nmaa = c.context.call_conv.decode_arguments(xhg__uja, zqx__xfbvv.
        args, bjx__rgrt)
    rut__aqjru = pdpa__yhzep(xhg__uja, vejb__nmaa)
    c.context.call_conv.return_value(xhg__uja, rut__aqjru)
    hxjrc__vdvh, qkz__odeci = c.context.call_conv.call_function(c.builder,
        bjx__rgrt, zqx__xfbvv.return_type, zqx__xfbvv.args, args)
    return qkz__odeci


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    tsnro__vmokq = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(tsnro__vmokq)
    c.pyapi.decref(tsnro__vmokq)
    fzlnl__jslr = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    ixigb__vuwli = cgutils.get_or_insert_function(c.builder.module,
        fzlnl__jslr, name='is_bool_array')
    fzlnl__jslr = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    bjx__rgrt = cgutils.get_or_insert_function(c.builder.module,
        fzlnl__jslr, name='is_pd_boolean_array')
    kpty__rem = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    cpkes__nic = c.builder.call(bjx__rgrt, [obj])
    pbjby__ipt = c.builder.icmp_unsigned('!=', cpkes__nic, cpkes__nic.type(0))
    with c.builder.if_else(pbjby__ipt) as (lkjmj__gnvnf, ndbw__nbu):
        with lkjmj__gnvnf:
            ghn__vpfqn = c.pyapi.object_getattr_string(obj, '_data')
            kpty__rem.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), ghn__vpfqn).value
            zrnme__fvicl = c.pyapi.object_getattr_string(obj, '_mask')
            lyii__tbm = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), zrnme__fvicl).value
            tqfd__rkux = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            bwa__cnacp = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, lyii__tbm)
            ozill__exetu = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [tqfd__rkux])
            fzlnl__jslr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            bjx__rgrt = cgutils.get_or_insert_function(c.builder.module,
                fzlnl__jslr, name='mask_arr_to_bitmap')
            c.builder.call(bjx__rgrt, [ozill__exetu.data, bwa__cnacp.data, n])
            kpty__rem.null_bitmap = ozill__exetu._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), lyii__tbm)
            c.pyapi.decref(ghn__vpfqn)
            c.pyapi.decref(zrnme__fvicl)
        with ndbw__nbu:
            gan__hodb = c.builder.call(ixigb__vuwli, [obj])
            phxp__auntj = c.builder.icmp_unsigned('!=', gan__hodb,
                gan__hodb.type(0))
            with c.builder.if_else(phxp__auntj) as (teib__hxujb, auzjx__gyw):
                with teib__hxujb:
                    kpty__rem.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    kpty__rem.null_bitmap = call_func_in_unbox(gen_full_bitmap,
                        (n,), (types.int64,), c)
                with auzjx__gyw:
                    kpty__rem.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    tqfd__rkux = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    kpty__rem.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [tqfd__rkux])._getvalue()
                    agqdt__bck = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, kpty__rem.data
                        ).data
                    owki__mie = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, kpty__rem.
                        null_bitmap).data
                    fzlnl__jslr = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    bjx__rgrt = cgutils.get_or_insert_function(c.builder.
                        module, fzlnl__jslr, name='unbox_bool_array_obj')
                    c.builder.call(bjx__rgrt, [obj, agqdt__bck, owki__mie, n])
    return NativeValue(kpty__rem._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    kpty__rem = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        kpty__rem.data, c.env_manager)
    caas__bzi = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, kpty__rem.null_bitmap).data
    tsnro__vmokq = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(tsnro__vmokq)
    raaev__snko = c.context.insert_const_string(c.builder.module, 'numpy')
    icg__whu = c.pyapi.import_module_noblock(raaev__snko)
    qxwvz__scb = c.pyapi.object_getattr_string(icg__whu, 'bool_')
    lyii__tbm = c.pyapi.call_method(icg__whu, 'empty', (tsnro__vmokq,
        qxwvz__scb))
    tzqza__aezym = c.pyapi.object_getattr_string(lyii__tbm, 'ctypes')
    wctwz__udhhq = c.pyapi.object_getattr_string(tzqza__aezym, 'data')
    uma__lcnep = c.builder.inttoptr(c.pyapi.long_as_longlong(wctwz__udhhq),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as haom__gsj:
        nhdan__kel = haom__gsj.index
        ntxz__wlar = c.builder.lshr(nhdan__kel, lir.Constant(lir.IntType(64
            ), 3))
        cfit__riauj = c.builder.load(cgutils.gep(c.builder, caas__bzi,
            ntxz__wlar))
        dsxtm__hxpto = c.builder.trunc(c.builder.and_(nhdan__kel, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(cfit__riauj, dsxtm__hxpto), lir
            .Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        rqdq__fnqc = cgutils.gep(c.builder, uma__lcnep, nhdan__kel)
        c.builder.store(val, rqdq__fnqc)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        kpty__rem.null_bitmap)
    raaev__snko = c.context.insert_const_string(c.builder.module, 'pandas')
    kvc__hegd = c.pyapi.import_module_noblock(raaev__snko)
    jve__vzks = c.pyapi.object_getattr_string(kvc__hegd, 'arrays')
    jty__asbk = c.pyapi.call_method(jve__vzks, 'BooleanArray', (data,
        lyii__tbm))
    c.pyapi.decref(kvc__hegd)
    c.pyapi.decref(tsnro__vmokq)
    c.pyapi.decref(icg__whu)
    c.pyapi.decref(qxwvz__scb)
    c.pyapi.decref(tzqza__aezym)
    c.pyapi.decref(wctwz__udhhq)
    c.pyapi.decref(jve__vzks)
    c.pyapi.decref(data)
    c.pyapi.decref(lyii__tbm)
    return jty__asbk


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    lkxwg__fpw = np.empty(n, np.bool_)
    zcai__rci = np.empty(n + 7 >> 3, np.uint8)
    for nhdan__kel, s in enumerate(pyval):
        upc__igflu = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(zcai__rci, nhdan__kel, int(not
            upc__igflu))
        if not upc__igflu:
            lkxwg__fpw[nhdan__kel] = s
    huhy__afeee = context.get_constant_generic(builder, data_type, lkxwg__fpw)
    jdokn__udvpj = context.get_constant_generic(builder, nulls_type, zcai__rci)
    return lir.Constant.literal_struct([huhy__afeee, jdokn__udvpj])


def lower_init_bool_array(context, builder, signature, args):
    wci__fql, gaeh__wppdn = args
    kpty__rem = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    kpty__rem.data = wci__fql
    kpty__rem.null_bitmap = gaeh__wppdn
    context.nrt.incref(builder, signature.args[0], wci__fql)
    context.nrt.incref(builder, signature.args[1], gaeh__wppdn)
    return kpty__rem._getvalue()


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
    iystc__lka = args[0]
    if equiv_set.has_shape(iystc__lka):
        return ArrayAnalysis.AnalyzeResult(shape=iystc__lka, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    iystc__lka = args[0]
    if equiv_set.has_shape(iystc__lka):
        return ArrayAnalysis.AnalyzeResult(shape=iystc__lka, pre=[])
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
    lkxwg__fpw = np.empty(n, dtype=np.bool_)
    sph__xiczi = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(lkxwg__fpw, sph__xiczi)


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
            roin__hopdn, wrv__ddq = array_getitem_bool_index(A, ind)
            return init_bool_array(roin__hopdn, wrv__ddq)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            roin__hopdn, wrv__ddq = array_getitem_int_index(A, ind)
            return init_bool_array(roin__hopdn, wrv__ddq)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            roin__hopdn, wrv__ddq = array_getitem_slice_index(A, ind)
            return init_bool_array(roin__hopdn, wrv__ddq)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    vwpwj__grtmp = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(vwpwj__grtmp)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(vwpwj__grtmp)
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
        for nhdan__kel in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, nhdan__kel):
                val = A[nhdan__kel]
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
            olris__rco = np.empty(n, nb_dtype)
            for nhdan__kel in numba.parfors.parfor.internal_prange(n):
                olris__rco[nhdan__kel] = data[nhdan__kel]
                if bodo.libs.array_kernels.isna(A, nhdan__kel):
                    olris__rco[nhdan__kel] = np.nan
            return olris__rco
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        olris__rco = np.empty(n, dtype=np.bool_)
        for nhdan__kel in numba.parfors.parfor.internal_prange(n):
            olris__rco[nhdan__kel] = data[nhdan__kel]
            if bodo.libs.array_kernels.isna(A, nhdan__kel):
                olris__rco[nhdan__kel] = value
        return olris__rco
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
    fbra__igaoe = op.__name__
    fbra__igaoe = ufunc_aliases.get(fbra__igaoe, fbra__igaoe)
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
    for xel__vhxc in numba.np.ufunc_db.get_ufuncs():
        clx__bov = create_op_overload(xel__vhxc, xel__vhxc.nin)
        overload(xel__vhxc, no_unliteral=True)(clx__bov)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        clx__bov = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(clx__bov)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        clx__bov = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(clx__bov)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        clx__bov = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(clx__bov)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        dsxtm__hxpto = []
        ofpjy__ypx = False
        vaql__mais = False
        eno__kuiyq = False
        for nhdan__kel in range(len(A)):
            if bodo.libs.array_kernels.isna(A, nhdan__kel):
                if not ofpjy__ypx:
                    data.append(False)
                    dsxtm__hxpto.append(False)
                    ofpjy__ypx = True
                continue
            val = A[nhdan__kel]
            if val and not vaql__mais:
                data.append(True)
                dsxtm__hxpto.append(True)
                vaql__mais = True
            if not val and not eno__kuiyq:
                data.append(False)
                dsxtm__hxpto.append(True)
                eno__kuiyq = True
            if ofpjy__ypx and vaql__mais and eno__kuiyq:
                break
        roin__hopdn = np.array(data)
        n = len(roin__hopdn)
        tqfd__rkux = 1
        wrv__ddq = np.empty(tqfd__rkux, np.uint8)
        for wmfo__ilf in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(wrv__ddq, wmfo__ilf,
                dsxtm__hxpto[wmfo__ilf])
        return init_bool_array(roin__hopdn, wrv__ddq)
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
    jty__asbk = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, jty__asbk)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    heu__nqss = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        lcap__babq = bodo.utils.utils.is_array_typ(val1, False)
        mqhue__pumn = bodo.utils.utils.is_array_typ(val2, False)
        evmp__aaz = 'val1' if lcap__babq else 'val2'
        bxndz__stlfs = 'def impl(val1, val2):\n'
        bxndz__stlfs += f'  n = len({evmp__aaz})\n'
        bxndz__stlfs += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        bxndz__stlfs += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if lcap__babq:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            awgbq__mogn = 'val1[i]'
        else:
            null1 = 'False\n'
            awgbq__mogn = 'val1'
        if mqhue__pumn:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            wsb__lgxho = 'val2[i]'
        else:
            null2 = 'False\n'
            wsb__lgxho = 'val2'
        if heu__nqss:
            bxndz__stlfs += f"""    result, isna_val = compute_or_body({null1}, {null2}, {awgbq__mogn}, {wsb__lgxho})
"""
        else:
            bxndz__stlfs += f"""    result, isna_val = compute_and_body({null1}, {null2}, {awgbq__mogn}, {wsb__lgxho})
"""
        bxndz__stlfs += '    out_arr[i] = result\n'
        bxndz__stlfs += '    if isna_val:\n'
        bxndz__stlfs += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        bxndz__stlfs += '      continue\n'
        bxndz__stlfs += '  return out_arr\n'
        wes__apsi = {}
        exec(bxndz__stlfs, {'bodo': bodo, 'numba': numba,
            'compute_and_body': compute_and_body, 'compute_or_body':
            compute_or_body}, wes__apsi)
        impl = wes__apsi['impl']
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
        eblvn__zdkqe = boolean_array
        return eblvn__zdkqe(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    jtz__gvb = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array) and (
        bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype == types.
        bool_ or typ1 == types.bool_) and (bodo.utils.utils.is_array_typ(
        typ2, False) and typ2.dtype == types.bool_ or typ2 == types.bool_)
    return jtz__gvb


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        gkvy__djss = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(gkvy__djss)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(gkvy__djss)


_install_nullable_logical_lowering()
