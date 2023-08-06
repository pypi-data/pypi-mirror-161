import enum
import operator
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.utils.typing import NOT_CONSTANT, BodoError, MetaType, check_unsupported_args, dtype_to_array_type, get_literal_value, get_overload_const, get_overload_const_bool, is_common_scalar_dtype, is_iterable_type, is_list_like_index_type, is_literal_type, is_overload_constant_bool, is_overload_none, is_overload_true, is_scalar_type, raise_bodo_error


class PDCategoricalDtype(types.Opaque):

    def __init__(self, categories, elem_type, ordered, data=None, int_type=None
        ):
        self.categories = categories
        self.elem_type = elem_type
        self.ordered = ordered
        self.data = _get_cat_index_type(elem_type) if data is None else data
        self.int_type = int_type
        ihwnh__oqn = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=ihwnh__oqn)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    ltxx__vxd = tuple(val.categories.values)
    elem_type = None if len(ltxx__vxd) == 0 else bodo.typeof(val.categories
        .values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(ltxx__vxd, elem_type, val.ordered, bodo.
        typeof(val.categories), int_type)


def _get_cat_index_type(elem_type):
    elem_type = bodo.string_type if elem_type is None else elem_type
    return bodo.utils.typing.get_index_type_from_dtype(elem_type)


@lower_constant(PDCategoricalDtype)
def lower_constant_categorical_type(context, builder, typ, pyval):
    categories = context.get_constant_generic(builder, bodo.typeof(pyval.
        categories), pyval.categories)
    ordered = context.get_constant(types.bool_, pyval.ordered)
    return lir.Constant.literal_struct([categories, ordered])


@register_model(PDCategoricalDtype)
class PDCategoricalDtypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kwt__zmxyb = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, kwt__zmxyb)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    bzgba__ymmc = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    vgwo__rci = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, lxmu__agg, lxmu__agg = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    dzdy__trv = PDCategoricalDtype(vgwo__rci, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, bzgba__ymmc)
    return dzdy__trv(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    tbuv__mogut = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, tbuv__mogut).value
    c.pyapi.decref(tbuv__mogut)
    dluka__nkqf = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, dluka__nkqf).value
    c.pyapi.decref(dluka__nkqf)
    xygnc__bcke = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=xygnc__bcke)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    tbuv__mogut = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    lngbd__ulua = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    frnc__uhvgr = c.context.insert_const_string(c.builder.module, 'pandas')
    rhl__dobsm = c.pyapi.import_module_noblock(frnc__uhvgr)
    mddlw__jsq = c.pyapi.call_method(rhl__dobsm, 'CategoricalDtype', (
        lngbd__ulua, tbuv__mogut))
    c.pyapi.decref(tbuv__mogut)
    c.pyapi.decref(lngbd__ulua)
    c.pyapi.decref(rhl__dobsm)
    c.context.nrt.decref(c.builder, typ, val)
    return mddlw__jsq


@overload_attribute(PDCategoricalDtype, 'nbytes')
def pd_categorical_nbytes_overload(A):
    return lambda A: A.categories.nbytes + bodo.io.np_io.get_dtype_size(types
        .bool_)


class CategoricalArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(CategoricalArrayType, self).__init__(name=
            f'CategoricalArrayType({dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return CategoricalArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.Categorical)
def _typeof_pd_cat(val, c):
    return CategoricalArrayType(bodo.typeof(val.dtype))


@register_model(CategoricalArrayType)
class CategoricalArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        gdimf__zsjr = get_categories_int_type(fe_type.dtype)
        kwt__zmxyb = [('dtype', fe_type.dtype), ('codes', types.Array(
            gdimf__zsjr, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, kwt__zmxyb)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    psyl__yms = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), psyl__yms
        ).value
    c.pyapi.decref(psyl__yms)
    mddlw__jsq = c.pyapi.object_getattr_string(val, 'dtype')
    zeyky__oqqc = c.pyapi.to_native_value(typ.dtype, mddlw__jsq).value
    c.pyapi.decref(mddlw__jsq)
    npr__ehbc = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    npr__ehbc.codes = codes
    npr__ehbc.dtype = zeyky__oqqc
    return NativeValue(npr__ehbc._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    thvqg__mds = get_categories_int_type(typ.dtype)
    vqktt__wwxga = context.get_constant_generic(builder, types.Array(
        thvqg__mds, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, vqktt__wwxga])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    sjyx__fumyk = len(cat_dtype.categories)
    if sjyx__fumyk < np.iinfo(np.int8).max:
        dtype = types.int8
    elif sjyx__fumyk < np.iinfo(np.int16).max:
        dtype = types.int16
    elif sjyx__fumyk < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    frnc__uhvgr = c.context.insert_const_string(c.builder.module, 'pandas')
    rhl__dobsm = c.pyapi.import_module_noblock(frnc__uhvgr)
    gdimf__zsjr = get_categories_int_type(dtype)
    nnlhd__ppf = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    bil__iwq = types.Array(gdimf__zsjr, 1, 'C')
    c.context.nrt.incref(c.builder, bil__iwq, nnlhd__ppf.codes)
    psyl__yms = c.pyapi.from_native_value(bil__iwq, nnlhd__ppf.codes, c.
        env_manager)
    c.context.nrt.incref(c.builder, dtype, nnlhd__ppf.dtype)
    mddlw__jsq = c.pyapi.from_native_value(dtype, nnlhd__ppf.dtype, c.
        env_manager)
    gyvj__eqbpv = c.pyapi.borrow_none()
    jmotz__zxzz = c.pyapi.object_getattr_string(rhl__dobsm, 'Categorical')
    regs__zybf = c.pyapi.call_method(jmotz__zxzz, 'from_codes', (psyl__yms,
        gyvj__eqbpv, gyvj__eqbpv, mddlw__jsq))
    c.pyapi.decref(jmotz__zxzz)
    c.pyapi.decref(psyl__yms)
    c.pyapi.decref(mddlw__jsq)
    c.pyapi.decref(rhl__dobsm)
    c.context.nrt.decref(c.builder, typ, val)
    return regs__zybf


def _to_readonly(t):
    from bodo.hiframes.pd_index_ext import DatetimeIndexType, NumericIndexType, TimedeltaIndexType
    if isinstance(t, CategoricalArrayType):
        return CategoricalArrayType(_to_readonly(t.dtype))
    if isinstance(t, PDCategoricalDtype):
        return PDCategoricalDtype(t.categories, t.elem_type, t.ordered,
            _to_readonly(t.data), t.int_type)
    if isinstance(t, types.Array):
        return types.Array(t.dtype, t.ndim, 'C', True)
    if isinstance(t, NumericIndexType):
        return NumericIndexType(t.dtype, t.name_typ, _to_readonly(t.data))
    if isinstance(t, (DatetimeIndexType, TimedeltaIndexType)):
        return t.__class__(t.name_typ, _to_readonly(t.data))
    return t


@lower_cast(CategoricalArrayType, CategoricalArrayType)
def cast_cat_arr(context, builder, fromty, toty, val):
    if _to_readonly(toty) == fromty:
        return val
    raise BodoError(f'Cannot cast from {fromty} to {toty}')


def create_cmp_op_overload(op):

    def overload_cat_arr_cmp(A, other):
        if not isinstance(A, CategoricalArrayType):
            return
        if A.dtype.categories and is_literal_type(other) and types.unliteral(
            other) == A.dtype.elem_type:
            val = get_literal_value(other)
            bwbxn__mhk = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                tepss__fspvg = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), bwbxn__mhk)
                return tepss__fspvg
            return impl_lit

        def impl(A, other):
            bwbxn__mhk = get_code_for_value(A.dtype, other)
            tepss__fspvg = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), bwbxn__mhk)
            return tepss__fspvg
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        wmi__wptx = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(wmi__wptx)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    nnlhd__ppf = cat_dtype.categories
    n = len(nnlhd__ppf)
    for aygl__eor in range(n):
        if nnlhd__ppf[aygl__eor] == val:
            return aygl__eor
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    rfhh__ndv = bodo.utils.typing.parse_dtype(dtype, 'CategoricalArray.astype')
    if rfhh__ndv != A.dtype.elem_type and rfhh__ndv != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if rfhh__ndv == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            tepss__fspvg = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for aygl__eor in numba.parfors.parfor.internal_prange(n):
                odfed__xpok = codes[aygl__eor]
                if odfed__xpok == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(
                            tepss__fspvg, aygl__eor)
                    else:
                        bodo.libs.array_kernels.setna(tepss__fspvg, aygl__eor)
                    continue
                tepss__fspvg[aygl__eor] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[odfed__xpok]))
            return tepss__fspvg
        return impl
    bil__iwq = dtype_to_array_type(rfhh__ndv)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        tepss__fspvg = bodo.utils.utils.alloc_type(n, bil__iwq, (-1,))
        for aygl__eor in numba.parfors.parfor.internal_prange(n):
            odfed__xpok = codes[aygl__eor]
            if odfed__xpok == -1:
                bodo.libs.array_kernels.setna(tepss__fspvg, aygl__eor)
                continue
            tepss__fspvg[aygl__eor] = bodo.utils.conversion.unbox_if_timestamp(
                categories[odfed__xpok])
        return tepss__fspvg
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        jigvf__peml, zeyky__oqqc = args
        nnlhd__ppf = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        nnlhd__ppf.codes = jigvf__peml
        nnlhd__ppf.dtype = zeyky__oqqc
        context.nrt.incref(builder, signature.args[0], jigvf__peml)
        context.nrt.incref(builder, signature.args[1], zeyky__oqqc)
        return nnlhd__ppf._getvalue()
    blts__eaxsb = CategoricalArrayType(cat_dtype)
    sig = blts__eaxsb(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    owse__dukd = args[0]
    if equiv_set.has_shape(owse__dukd):
        return ArrayAnalysis.AnalyzeResult(shape=owse__dukd, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    gdimf__zsjr = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, gdimf__zsjr)
        return init_categorical_array(codes, cat_dtype)
    return impl


def alloc_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_alloc_categorical_array
    ) = alloc_categorical_array_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_categorical_arr_codes(A):
    return lambda A: A.codes


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_categorical_array',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_categorical_arr_codes',
    'bodo.hiframes.pd_categorical_ext'] = alias_ext_dummy_func


@overload_method(CategoricalArrayType, 'copy', no_unliteral=True)
def cat_arr_copy_overload(arr):
    return lambda arr: init_categorical_array(arr.codes.copy(), arr.dtype)


def build_replace_dicts(to_replace, value, categories):
    return dict(), np.empty(len(categories) + 1), 0


@overload(build_replace_dicts, no_unliteral=True)
def _build_replace_dicts(to_replace, value, categories):
    if isinstance(to_replace, types.Number) or to_replace == bodo.string_type:

        def impl(to_replace, value, categories):
            return build_replace_dicts([to_replace], value, categories)
        return impl
    else:

        def impl(to_replace, value, categories):
            n = len(categories)
            jbi__tcsuj = {}
            vqktt__wwxga = np.empty(n + 1, np.int64)
            azir__dgi = {}
            njy__zseba = []
            imbiw__mdbr = {}
            for aygl__eor in range(n):
                imbiw__mdbr[categories[aygl__eor]] = aygl__eor
            for baa__pua in to_replace:
                if baa__pua != value:
                    if baa__pua in imbiw__mdbr:
                        if value in imbiw__mdbr:
                            jbi__tcsuj[baa__pua] = baa__pua
                            bli__ycmc = imbiw__mdbr[baa__pua]
                            azir__dgi[bli__ycmc] = imbiw__mdbr[value]
                            njy__zseba.append(bli__ycmc)
                        else:
                            jbi__tcsuj[baa__pua] = value
                            imbiw__mdbr[value] = imbiw__mdbr[baa__pua]
            ndbs__zno = np.sort(np.array(njy__zseba))
            pem__twemx = 0
            qlff__jkbo = []
            for xmf__yrlz in range(-1, n):
                while pem__twemx < len(ndbs__zno) and xmf__yrlz > ndbs__zno[
                    pem__twemx]:
                    pem__twemx += 1
                qlff__jkbo.append(pem__twemx)
            for xah__lzjm in range(-1, n):
                trgzt__fznf = xah__lzjm
                if xah__lzjm in azir__dgi:
                    trgzt__fznf = azir__dgi[xah__lzjm]
                vqktt__wwxga[xah__lzjm + 1] = trgzt__fznf - qlff__jkbo[
                    trgzt__fznf + 1]
            return jbi__tcsuj, vqktt__wwxga, len(ndbs__zno)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for aygl__eor in range(len(new_codes_arr)):
        new_codes_arr[aygl__eor] = codes_map_arr[old_codes_arr[aygl__eor] + 1]


@overload_method(CategoricalArrayType, 'replace', inline='always',
    no_unliteral=True)
def overload_replace(arr, to_replace, value):

    def impl(arr, to_replace, value):
        return bodo.hiframes.pd_categorical_ext.cat_replace(arr, to_replace,
            value)
    return impl


def cat_replace(arr, to_replace, value):
    return


@overload(cat_replace, no_unliteral=True)
def cat_replace_overload(arr, to_replace, value):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(to_replace,
        'CategoricalArray.replace()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'CategoricalArray.replace()')
    jmfri__jihoq = arr.dtype.ordered
    lgby__xeel = arr.dtype.elem_type
    bdh__vzo = get_overload_const(to_replace)
    kpffx__fzcmz = get_overload_const(value)
    if (arr.dtype.categories is not None and bdh__vzo is not NOT_CONSTANT and
        kpffx__fzcmz is not NOT_CONSTANT):
        jlyk__wnmfz, codes_map_arr, lxmu__agg = python_build_replace_dicts(
            bdh__vzo, kpffx__fzcmz, arr.dtype.categories)
        if len(jlyk__wnmfz) == 0:
            return lambda arr, to_replace, value: arr.copy()
        ydjua__ofhr = []
        for wdnx__hdcoj in arr.dtype.categories:
            if wdnx__hdcoj in jlyk__wnmfz:
                nbx__vtl = jlyk__wnmfz[wdnx__hdcoj]
                if nbx__vtl != wdnx__hdcoj:
                    ydjua__ofhr.append(nbx__vtl)
            else:
                ydjua__ofhr.append(wdnx__hdcoj)
        nlpvp__fwr = bodo.utils.utils.create_categorical_type(ydjua__ofhr,
            arr.dtype.data.data, jmfri__jihoq)
        mpjam__rjtu = MetaType(tuple(nlpvp__fwr))

        def impl_dtype(arr, to_replace, value):
            gjxq__bdcx = init_cat_dtype(bodo.utils.conversion.
                index_from_array(nlpvp__fwr), jmfri__jihoq, None, mpjam__rjtu)
            nnlhd__ppf = alloc_categorical_array(len(arr.codes), gjxq__bdcx)
            reassign_codes(nnlhd__ppf.codes, arr.codes, codes_map_arr)
            return nnlhd__ppf
        return impl_dtype
    lgby__xeel = arr.dtype.elem_type
    if lgby__xeel == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            jbi__tcsuj, codes_map_arr, zsrs__adwi = build_replace_dicts(
                to_replace, value, categories.values)
            if len(jbi__tcsuj) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), jmfri__jihoq,
                    None, None))
            n = len(categories)
            nlpvp__fwr = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                zsrs__adwi, -1)
            fpmcq__atfu = 0
            for xmf__yrlz in range(n):
                jcfoj__sxzvo = categories[xmf__yrlz]
                if jcfoj__sxzvo in jbi__tcsuj:
                    sapm__uli = jbi__tcsuj[jcfoj__sxzvo]
                    if sapm__uli != jcfoj__sxzvo:
                        nlpvp__fwr[fpmcq__atfu] = sapm__uli
                        fpmcq__atfu += 1
                else:
                    nlpvp__fwr[fpmcq__atfu] = jcfoj__sxzvo
                    fpmcq__atfu += 1
            nnlhd__ppf = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                nlpvp__fwr), jmfri__jihoq, None, None))
            reassign_codes(nnlhd__ppf.codes, arr.codes, codes_map_arr)
            return nnlhd__ppf
        return impl_str
    dzzqo__fpal = dtype_to_array_type(lgby__xeel)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        jbi__tcsuj, codes_map_arr, zsrs__adwi = build_replace_dicts(to_replace,
            value, categories.values)
        if len(jbi__tcsuj) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), jmfri__jihoq, None, None))
        n = len(categories)
        nlpvp__fwr = bodo.utils.utils.alloc_type(n - zsrs__adwi,
            dzzqo__fpal, None)
        fpmcq__atfu = 0
        for aygl__eor in range(n):
            jcfoj__sxzvo = categories[aygl__eor]
            if jcfoj__sxzvo in jbi__tcsuj:
                sapm__uli = jbi__tcsuj[jcfoj__sxzvo]
                if sapm__uli != jcfoj__sxzvo:
                    nlpvp__fwr[fpmcq__atfu] = sapm__uli
                    fpmcq__atfu += 1
            else:
                nlpvp__fwr[fpmcq__atfu] = jcfoj__sxzvo
                fpmcq__atfu += 1
        nnlhd__ppf = alloc_categorical_array(len(arr.codes), init_cat_dtype
            (bodo.utils.conversion.index_from_array(nlpvp__fwr),
            jmfri__jihoq, None, None))
        reassign_codes(nnlhd__ppf.codes, arr.codes, codes_map_arr)
        return nnlhd__ppf
    return impl


@overload(len, no_unliteral=True)
def overload_cat_arr_len(A):
    if isinstance(A, CategoricalArrayType):
        return lambda A: len(A.codes)


@overload_attribute(CategoricalArrayType, 'shape')
def overload_cat_arr_shape(A):
    return lambda A: (len(A.codes),)


@overload_attribute(CategoricalArrayType, 'ndim')
def overload_cat_arr_ndim(A):
    return lambda A: 1


@overload_attribute(CategoricalArrayType, 'nbytes')
def cat_arr_nbytes_overload(A):
    return lambda A: A.codes.nbytes + A.dtype.nbytes


@register_jitable
def get_label_dict_from_categories(vals):
    orvgo__zxzxj = dict()
    tlf__jdfnt = 0
    for aygl__eor in range(len(vals)):
        val = vals[aygl__eor]
        if val in orvgo__zxzxj:
            continue
        orvgo__zxzxj[val] = tlf__jdfnt
        tlf__jdfnt += 1
    return orvgo__zxzxj


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    orvgo__zxzxj = dict()
    for aygl__eor in range(len(vals)):
        val = vals[aygl__eor]
        orvgo__zxzxj[val] = aygl__eor
    return orvgo__zxzxj


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    tthhd__wugi = dict(fastpath=fastpath)
    jijp__iqydp = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', tthhd__wugi, jijp__iqydp)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        pnf__hsz = get_overload_const(categories)
        if pnf__hsz is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                enzvt__swvw = False
            else:
                enzvt__swvw = get_overload_const_bool(ordered)
            jcls__cdqk = pd.CategoricalDtype(pd.array(pnf__hsz), enzvt__swvw
                ).categories.array
            jikd__fqixk = MetaType(tuple(jcls__cdqk))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                gjxq__bdcx = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(jcls__cdqk), enzvt__swvw, None,
                    jikd__fqixk)
                return bodo.utils.conversion.fix_arr_dtype(data, gjxq__bdcx)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            ltxx__vxd = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                ltxx__vxd, ordered, None, None)
            return bodo.utils.conversion.fix_arr_dtype(data, cat_dtype)
        return impl_cats
    elif is_overload_none(ordered):

        def impl_auto(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, 'category')
        return impl_auto
    raise BodoError(
        f'pd.Categorical(): argument combination not supported yet: {values}, {categories}, {ordered}, {dtype}'
        )


@overload(operator.getitem, no_unliteral=True)
def categorical_array_getitem(arr, ind):
    if not isinstance(arr, CategoricalArrayType):
        return
    if isinstance(ind, types.Integer):

        def categorical_getitem_impl(arr, ind):
            hnnnv__kmij = arr.codes[ind]
            return arr.dtype.categories[max(hnnnv__kmij, 0)]
        return categorical_getitem_impl
    if is_list_like_index_type(ind) or isinstance(ind, types.SliceType):

        def impl_bool(arr, ind):
            return init_categorical_array(arr.codes[ind], arr.dtype)
        return impl_bool
    raise BodoError(
        f'getitem for CategoricalArrayType with indexing type {ind} not supported.'
        )


class CategoricalMatchingValues(enum.Enum):
    DIFFERENT_TYPES = -1
    DONT_MATCH = 0
    MAY_MATCH = 1
    DO_MATCH = 2


def categorical_arrs_match(arr1, arr2):
    if not (isinstance(arr1, CategoricalArrayType) and isinstance(arr2,
        CategoricalArrayType)):
        return CategoricalMatchingValues.DIFFERENT_TYPES
    if arr1.dtype.categories is None or arr2.dtype.categories is None:
        return CategoricalMatchingValues.MAY_MATCH
    return (CategoricalMatchingValues.DO_MATCH if arr1.dtype.categories ==
        arr2.dtype.categories and arr1.dtype.ordered == arr2.dtype.ordered else
        CategoricalMatchingValues.DONT_MATCH)


@register_jitable
def cat_dtype_equal(dtype1, dtype2):
    if dtype1.ordered != dtype2.ordered or len(dtype1.categories) != len(dtype2
        .categories):
        return False
    arr1 = dtype1.categories.values
    arr2 = dtype2.categories.values
    for aygl__eor in range(len(arr1)):
        if arr1[aygl__eor] != arr2[aygl__eor]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    pzpqu__bok = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    nifk__ulee = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    acrps__cwowg = categorical_arrs_match(arr, val)
    waio__xgxe = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    drih__nxu = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not pzpqu__bok:
            raise BodoError(waio__xgxe)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            hnnnv__kmij = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = hnnnv__kmij
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (pzpqu__bok or nifk__ulee or acrps__cwowg !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(waio__xgxe)
        if acrps__cwowg == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(drih__nxu)
        if pzpqu__bok:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ikhqf__iwp = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for xmf__yrlz in range(n):
                    arr.codes[ind[xmf__yrlz]] = ikhqf__iwp
            return impl_scalar
        if acrps__cwowg == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for aygl__eor in range(n):
                    arr.codes[ind[aygl__eor]] = val.codes[aygl__eor]
            return impl_arr_ind_mask
        if acrps__cwowg == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(drih__nxu)
                n = len(val.codes)
                for aygl__eor in range(n):
                    arr.codes[ind[aygl__eor]] = val.codes[aygl__eor]
            return impl_arr_ind_mask
        if nifk__ulee:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for xmf__yrlz in range(n):
                    lkyht__xkts = bodo.utils.conversion.unbox_if_timestamp(val
                        [xmf__yrlz])
                    if lkyht__xkts not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    hnnnv__kmij = categories.get_loc(lkyht__xkts)
                    arr.codes[ind[xmf__yrlz]] = hnnnv__kmij
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (pzpqu__bok or nifk__ulee or acrps__cwowg !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(waio__xgxe)
        if acrps__cwowg == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(drih__nxu)
        if pzpqu__bok:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ikhqf__iwp = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for xmf__yrlz in range(n):
                    if ind[xmf__yrlz]:
                        arr.codes[xmf__yrlz] = ikhqf__iwp
            return impl_scalar
        if acrps__cwowg == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                wgpz__etz = 0
                for aygl__eor in range(n):
                    if ind[aygl__eor]:
                        arr.codes[aygl__eor] = val.codes[wgpz__etz]
                        wgpz__etz += 1
            return impl_bool_ind_mask
        if acrps__cwowg == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(drih__nxu)
                n = len(ind)
                wgpz__etz = 0
                for aygl__eor in range(n):
                    if ind[aygl__eor]:
                        arr.codes[aygl__eor] = val.codes[wgpz__etz]
                        wgpz__etz += 1
            return impl_bool_ind_mask
        if nifk__ulee:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                wgpz__etz = 0
                categories = arr.dtype.categories
                for xmf__yrlz in range(n):
                    if ind[xmf__yrlz]:
                        lkyht__xkts = bodo.utils.conversion.unbox_if_timestamp(
                            val[wgpz__etz])
                        if lkyht__xkts not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        hnnnv__kmij = categories.get_loc(lkyht__xkts)
                        arr.codes[xmf__yrlz] = hnnnv__kmij
                        wgpz__etz += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (pzpqu__bok or nifk__ulee or acrps__cwowg !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(waio__xgxe)
        if acrps__cwowg == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(drih__nxu)
        if pzpqu__bok:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ikhqf__iwp = arr.dtype.categories.get_loc(val)
                fmp__dic = numba.cpython.unicode._normalize_slice(ind, len(arr)
                    )
                for xmf__yrlz in range(fmp__dic.start, fmp__dic.stop,
                    fmp__dic.step):
                    arr.codes[xmf__yrlz] = ikhqf__iwp
            return impl_scalar
        if acrps__cwowg == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if acrps__cwowg == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(drih__nxu)
                arr.codes[ind] = val.codes
            return impl_arr
        if nifk__ulee:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                fmp__dic = numba.cpython.unicode._normalize_slice(ind, len(arr)
                    )
                wgpz__etz = 0
                for xmf__yrlz in range(fmp__dic.start, fmp__dic.stop,
                    fmp__dic.step):
                    lkyht__xkts = bodo.utils.conversion.unbox_if_timestamp(val
                        [wgpz__etz])
                    if lkyht__xkts not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    hnnnv__kmij = categories.get_loc(lkyht__xkts)
                    arr.codes[xmf__yrlz] = hnnnv__kmij
                    wgpz__etz += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
