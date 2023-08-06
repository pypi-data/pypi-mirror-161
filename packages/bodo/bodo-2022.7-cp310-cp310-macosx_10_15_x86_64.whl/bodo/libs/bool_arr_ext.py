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
        pch__ogw = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, pch__ogw)


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
    fhbv__soj = c.context.insert_const_string(c.builder.module, 'pandas')
    ndyol__mko = c.pyapi.import_module_noblock(fhbv__soj)
    mvtc__sprmf = c.pyapi.call_method(ndyol__mko, 'BooleanDtype', ())
    c.pyapi.decref(ndyol__mko)
    return mvtc__sprmf


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    omw__wfzoy = n + 7 >> 3
    return np.full(omw__wfzoy, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    lyu__gvupk = c.context.typing_context.resolve_value_type(func)
    fiw__dfpq = lyu__gvupk.get_call_type(c.context.typing_context, arg_typs, {}
        )
    cbwy__zpnqe = c.context.get_function(lyu__gvupk, fiw__dfpq)
    pejyy__xqhkt = c.context.call_conv.get_function_type(fiw__dfpq.
        return_type, fiw__dfpq.args)
    sxyu__qacgg = c.builder.module
    irnqa__wcdz = lir.Function(sxyu__qacgg, pejyy__xqhkt, name=sxyu__qacgg.
        get_unique_name('.func_conv'))
    irnqa__wcdz.linkage = 'internal'
    pows__yyenv = lir.IRBuilder(irnqa__wcdz.append_basic_block())
    ixg__dvjvz = c.context.call_conv.decode_arguments(pows__yyenv,
        fiw__dfpq.args, irnqa__wcdz)
    emkvn__usrap = cbwy__zpnqe(pows__yyenv, ixg__dvjvz)
    c.context.call_conv.return_value(pows__yyenv, emkvn__usrap)
    pyzuq__xuz, dikh__vaq = c.context.call_conv.call_function(c.builder,
        irnqa__wcdz, fiw__dfpq.return_type, fiw__dfpq.args, args)
    return dikh__vaq


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    fhi__eprdz = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(fhi__eprdz)
    c.pyapi.decref(fhi__eprdz)
    pejyy__xqhkt = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    eopa__coc = cgutils.get_or_insert_function(c.builder.module,
        pejyy__xqhkt, name='is_bool_array')
    pejyy__xqhkt = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    irnqa__wcdz = cgutils.get_or_insert_function(c.builder.module,
        pejyy__xqhkt, name='is_pd_boolean_array')
    bpjf__uako = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pkig__ssu = c.builder.call(irnqa__wcdz, [obj])
    xef__yifc = c.builder.icmp_unsigned('!=', pkig__ssu, pkig__ssu.type(0))
    with c.builder.if_else(xef__yifc) as (vedv__zlz, uwfm__fdc):
        with vedv__zlz:
            rsxr__xtjpm = c.pyapi.object_getattr_string(obj, '_data')
            bpjf__uako.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), rsxr__xtjpm).value
            bjpwy__wyr = c.pyapi.object_getattr_string(obj, '_mask')
            poybn__stmmu = c.pyapi.to_native_value(types.Array(types.bool_,
                1, 'C'), bjpwy__wyr).value
            omw__wfzoy = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            pqlz__tgym = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, poybn__stmmu)
            zxo__dcctp = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [omw__wfzoy])
            pejyy__xqhkt = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            irnqa__wcdz = cgutils.get_or_insert_function(c.builder.module,
                pejyy__xqhkt, name='mask_arr_to_bitmap')
            c.builder.call(irnqa__wcdz, [zxo__dcctp.data, pqlz__tgym.data, n])
            bpjf__uako.null_bitmap = zxo__dcctp._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), poybn__stmmu)
            c.pyapi.decref(rsxr__xtjpm)
            c.pyapi.decref(bjpwy__wyr)
        with uwfm__fdc:
            ycpu__uxxbv = c.builder.call(eopa__coc, [obj])
            ocri__byko = c.builder.icmp_unsigned('!=', ycpu__uxxbv,
                ycpu__uxxbv.type(0))
            with c.builder.if_else(ocri__byko) as (ktebi__dmycu, ojhvf__awuav):
                with ktebi__dmycu:
                    bpjf__uako.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    bpjf__uako.null_bitmap = call_func_in_unbox(gen_full_bitmap
                        , (n,), (types.int64,), c)
                with ojhvf__awuav:
                    bpjf__uako.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    omw__wfzoy = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    bpjf__uako.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [omw__wfzoy])._getvalue()
                    aqewf__yhaoe = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, bpjf__uako.data
                        ).data
                    jtckp__zkcby = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, bpjf__uako.
                        null_bitmap).data
                    pejyy__xqhkt = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    irnqa__wcdz = cgutils.get_or_insert_function(c.builder.
                        module, pejyy__xqhkt, name='unbox_bool_array_obj')
                    c.builder.call(irnqa__wcdz, [obj, aqewf__yhaoe,
                        jtckp__zkcby, n])
    return NativeValue(bpjf__uako._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    bpjf__uako = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        bpjf__uako.data, c.env_manager)
    blwqz__ytftn = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, bpjf__uako.null_bitmap).data
    fhi__eprdz = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(fhi__eprdz)
    fhbv__soj = c.context.insert_const_string(c.builder.module, 'numpy')
    pgo__ypjko = c.pyapi.import_module_noblock(fhbv__soj)
    esam__wgqx = c.pyapi.object_getattr_string(pgo__ypjko, 'bool_')
    poybn__stmmu = c.pyapi.call_method(pgo__ypjko, 'empty', (fhi__eprdz,
        esam__wgqx))
    rqzg__mam = c.pyapi.object_getattr_string(poybn__stmmu, 'ctypes')
    poax__sjk = c.pyapi.object_getattr_string(rqzg__mam, 'data')
    ecx__dsv = c.builder.inttoptr(c.pyapi.long_as_longlong(poax__sjk), lir.
        IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as orop__ojk:
        xiwx__pjixl = orop__ojk.index
        snrn__lsdpb = c.builder.lshr(xiwx__pjixl, lir.Constant(lir.IntType(
            64), 3))
        ixx__pagkr = c.builder.load(cgutils.gep(c.builder, blwqz__ytftn,
            snrn__lsdpb))
        viyj__sdzfz = c.builder.trunc(c.builder.and_(xiwx__pjixl, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(ixx__pagkr, viyj__sdzfz), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        ewre__ues = cgutils.gep(c.builder, ecx__dsv, xiwx__pjixl)
        c.builder.store(val, ewre__ues)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        bpjf__uako.null_bitmap)
    fhbv__soj = c.context.insert_const_string(c.builder.module, 'pandas')
    ndyol__mko = c.pyapi.import_module_noblock(fhbv__soj)
    ggus__yyf = c.pyapi.object_getattr_string(ndyol__mko, 'arrays')
    mvtc__sprmf = c.pyapi.call_method(ggus__yyf, 'BooleanArray', (data,
        poybn__stmmu))
    c.pyapi.decref(ndyol__mko)
    c.pyapi.decref(fhi__eprdz)
    c.pyapi.decref(pgo__ypjko)
    c.pyapi.decref(esam__wgqx)
    c.pyapi.decref(rqzg__mam)
    c.pyapi.decref(poax__sjk)
    c.pyapi.decref(ggus__yyf)
    c.pyapi.decref(data)
    c.pyapi.decref(poybn__stmmu)
    return mvtc__sprmf


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    btr__bys = np.empty(n, np.bool_)
    ywc__jexz = np.empty(n + 7 >> 3, np.uint8)
    for xiwx__pjixl, s in enumerate(pyval):
        ykr__qapsu = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(ywc__jexz, xiwx__pjixl, int(
            not ykr__qapsu))
        if not ykr__qapsu:
            btr__bys[xiwx__pjixl] = s
    nffbp__edy = context.get_constant_generic(builder, data_type, btr__bys)
    hrvyj__zopym = context.get_constant_generic(builder, nulls_type, ywc__jexz)
    return lir.Constant.literal_struct([nffbp__edy, hrvyj__zopym])


def lower_init_bool_array(context, builder, signature, args):
    hum__fujxt, yutgc__zvjmj = args
    bpjf__uako = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    bpjf__uako.data = hum__fujxt
    bpjf__uako.null_bitmap = yutgc__zvjmj
    context.nrt.incref(builder, signature.args[0], hum__fujxt)
    context.nrt.incref(builder, signature.args[1], yutgc__zvjmj)
    return bpjf__uako._getvalue()


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
    lxowh__rwm = args[0]
    if equiv_set.has_shape(lxowh__rwm):
        return ArrayAnalysis.AnalyzeResult(shape=lxowh__rwm, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    lxowh__rwm = args[0]
    if equiv_set.has_shape(lxowh__rwm):
        return ArrayAnalysis.AnalyzeResult(shape=lxowh__rwm, pre=[])
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
    btr__bys = np.empty(n, dtype=np.bool_)
    ezo__uxcdh = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(btr__bys, ezo__uxcdh)


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
            ghq__neq, arqaa__bvtc = array_getitem_bool_index(A, ind)
            return init_bool_array(ghq__neq, arqaa__bvtc)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            ghq__neq, arqaa__bvtc = array_getitem_int_index(A, ind)
            return init_bool_array(ghq__neq, arqaa__bvtc)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            ghq__neq, arqaa__bvtc = array_getitem_slice_index(A, ind)
            return init_bool_array(ghq__neq, arqaa__bvtc)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    icg__jcqk = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(icg__jcqk)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(icg__jcqk)
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
        for xiwx__pjixl in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, xiwx__pjixl):
                val = A[xiwx__pjixl]
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
            fdl__kdurp = np.empty(n, nb_dtype)
            for xiwx__pjixl in numba.parfors.parfor.internal_prange(n):
                fdl__kdurp[xiwx__pjixl] = data[xiwx__pjixl]
                if bodo.libs.array_kernels.isna(A, xiwx__pjixl):
                    fdl__kdurp[xiwx__pjixl] = np.nan
            return fdl__kdurp
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload_method(BooleanArrayType, 'fillna', no_unliteral=True)
def overload_bool_fillna(A, value=None, method=None, limit=None):

    def impl(A, value=None, method=None, limit=None):
        data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
        n = len(data)
        fdl__kdurp = np.empty(n, dtype=np.bool_)
        for xiwx__pjixl in numba.parfors.parfor.internal_prange(n):
            fdl__kdurp[xiwx__pjixl] = data[xiwx__pjixl]
            if bodo.libs.array_kernels.isna(A, xiwx__pjixl):
                fdl__kdurp[xiwx__pjixl] = value
        return fdl__kdurp
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
    nmwrc__jsa = op.__name__
    nmwrc__jsa = ufunc_aliases.get(nmwrc__jsa, nmwrc__jsa)
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
    for fkodl__kxiph in numba.np.ufunc_db.get_ufuncs():
        wtvv__azp = create_op_overload(fkodl__kxiph, fkodl__kxiph.nin)
        overload(fkodl__kxiph, no_unliteral=True)(wtvv__azp)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        wtvv__azp = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(wtvv__azp)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        wtvv__azp = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(wtvv__azp)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        wtvv__azp = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(wtvv__azp)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        viyj__sdzfz = []
        vac__yvd = False
        jlu__voxv = False
        umtlp__ktslz = False
        for xiwx__pjixl in range(len(A)):
            if bodo.libs.array_kernels.isna(A, xiwx__pjixl):
                if not vac__yvd:
                    data.append(False)
                    viyj__sdzfz.append(False)
                    vac__yvd = True
                continue
            val = A[xiwx__pjixl]
            if val and not jlu__voxv:
                data.append(True)
                viyj__sdzfz.append(True)
                jlu__voxv = True
            if not val and not umtlp__ktslz:
                data.append(False)
                viyj__sdzfz.append(True)
                umtlp__ktslz = True
            if vac__yvd and jlu__voxv and umtlp__ktslz:
                break
        ghq__neq = np.array(data)
        n = len(ghq__neq)
        omw__wfzoy = 1
        arqaa__bvtc = np.empty(omw__wfzoy, np.uint8)
        for agpe__hak in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(arqaa__bvtc, agpe__hak,
                viyj__sdzfz[agpe__hak])
        return init_bool_array(ghq__neq, arqaa__bvtc)
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
    mvtc__sprmf = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, mvtc__sprmf)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    wrbei__soo = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        expoq__qkbe = bodo.utils.utils.is_array_typ(val1, False)
        npu__eaca = bodo.utils.utils.is_array_typ(val2, False)
        rehxv__ryu = 'val1' if expoq__qkbe else 'val2'
        jrjsf__ppb = 'def impl(val1, val2):\n'
        jrjsf__ppb += f'  n = len({rehxv__ryu})\n'
        jrjsf__ppb += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        jrjsf__ppb += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if expoq__qkbe:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            tamxb__ytg = 'val1[i]'
        else:
            null1 = 'False\n'
            tamxb__ytg = 'val1'
        if npu__eaca:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            seb__wpvf = 'val2[i]'
        else:
            null2 = 'False\n'
            seb__wpvf = 'val2'
        if wrbei__soo:
            jrjsf__ppb += f"""    result, isna_val = compute_or_body({null1}, {null2}, {tamxb__ytg}, {seb__wpvf})
"""
        else:
            jrjsf__ppb += f"""    result, isna_val = compute_and_body({null1}, {null2}, {tamxb__ytg}, {seb__wpvf})
"""
        jrjsf__ppb += '    out_arr[i] = result\n'
        jrjsf__ppb += '    if isna_val:\n'
        jrjsf__ppb += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        jrjsf__ppb += '      continue\n'
        jrjsf__ppb += '  return out_arr\n'
        vvb__nllcp = {}
        exec(jrjsf__ppb, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, vvb__nllcp)
        impl = vvb__nllcp['impl']
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
        xab__tplgs = boolean_array
        return xab__tplgs(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    hri__pqdht = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return hri__pqdht


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        cyxfn__anqo = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(cyxfn__anqo)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(cyxfn__anqo)


_install_nullable_logical_lowering()
