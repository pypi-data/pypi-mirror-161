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
        chrg__esud = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=chrg__esud)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    idv__kmyfg = tuple(val.categories.values)
    elem_type = None if len(idv__kmyfg) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(idv__kmyfg, elem_type, val.ordered, bodo.
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
        wlet__fmtyk = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, wlet__fmtyk)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    oafl__dtfdk = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    ylgr__lqiuz = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, uriw__rjipx, uriw__rjipx = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    fsg__rmd = PDCategoricalDtype(ylgr__lqiuz, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, oafl__dtfdk)
    return fsg__rmd(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    irw__ohrze = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, irw__ohrze).value
    c.pyapi.decref(irw__ohrze)
    yab__vwku = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, yab__vwku).value
    c.pyapi.decref(yab__vwku)
    idog__appy = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=idog__appy)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    irw__ohrze = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    eimfa__uysdc = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    gfn__djy = c.context.insert_const_string(c.builder.module, 'pandas')
    bcvk__hbjx = c.pyapi.import_module_noblock(gfn__djy)
    nloi__buma = c.pyapi.call_method(bcvk__hbjx, 'CategoricalDtype', (
        eimfa__uysdc, irw__ohrze))
    c.pyapi.decref(irw__ohrze)
    c.pyapi.decref(eimfa__uysdc)
    c.pyapi.decref(bcvk__hbjx)
    c.context.nrt.decref(c.builder, typ, val)
    return nloi__buma


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
        lro__biyii = get_categories_int_type(fe_type.dtype)
        wlet__fmtyk = [('dtype', fe_type.dtype), ('codes', types.Array(
            lro__biyii, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, wlet__fmtyk)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    stz__teh = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), stz__teh).value
    c.pyapi.decref(stz__teh)
    nloi__buma = c.pyapi.object_getattr_string(val, 'dtype')
    lmq__tplv = c.pyapi.to_native_value(typ.dtype, nloi__buma).value
    c.pyapi.decref(nloi__buma)
    hlfig__jtvv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hlfig__jtvv.codes = codes
    hlfig__jtvv.dtype = lmq__tplv
    return NativeValue(hlfig__jtvv._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    aai__zyb = get_categories_int_type(typ.dtype)
    vkrlg__musbh = context.get_constant_generic(builder, types.Array(
        aai__zyb, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, vkrlg__musbh])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    nmu__ldxmp = len(cat_dtype.categories)
    if nmu__ldxmp < np.iinfo(np.int8).max:
        dtype = types.int8
    elif nmu__ldxmp < np.iinfo(np.int16).max:
        dtype = types.int16
    elif nmu__ldxmp < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    gfn__djy = c.context.insert_const_string(c.builder.module, 'pandas')
    bcvk__hbjx = c.pyapi.import_module_noblock(gfn__djy)
    lro__biyii = get_categories_int_type(dtype)
    czgzu__tqu = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    tqzdh__qlhvb = types.Array(lro__biyii, 1, 'C')
    c.context.nrt.incref(c.builder, tqzdh__qlhvb, czgzu__tqu.codes)
    stz__teh = c.pyapi.from_native_value(tqzdh__qlhvb, czgzu__tqu.codes, c.
        env_manager)
    c.context.nrt.incref(c.builder, dtype, czgzu__tqu.dtype)
    nloi__buma = c.pyapi.from_native_value(dtype, czgzu__tqu.dtype, c.
        env_manager)
    cjon__ribx = c.pyapi.borrow_none()
    pri__qlv = c.pyapi.object_getattr_string(bcvk__hbjx, 'Categorical')
    rdix__xfm = c.pyapi.call_method(pri__qlv, 'from_codes', (stz__teh,
        cjon__ribx, cjon__ribx, nloi__buma))
    c.pyapi.decref(pri__qlv)
    c.pyapi.decref(stz__teh)
    c.pyapi.decref(nloi__buma)
    c.pyapi.decref(bcvk__hbjx)
    c.context.nrt.decref(c.builder, typ, val)
    return rdix__xfm


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
            kuyxk__ocdit = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                fvr__gmzhr = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), kuyxk__ocdit)
                return fvr__gmzhr
            return impl_lit

        def impl(A, other):
            kuyxk__ocdit = get_code_for_value(A.dtype, other)
            fvr__gmzhr = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), kuyxk__ocdit)
            return fvr__gmzhr
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        nyl__bkoaj = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(nyl__bkoaj)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    czgzu__tqu = cat_dtype.categories
    n = len(czgzu__tqu)
    for etx__zxiqx in range(n):
        if czgzu__tqu[etx__zxiqx] == val:
            return etx__zxiqx
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    dexid__iivgl = bodo.utils.typing.parse_dtype(dtype,
        'CategoricalArray.astype')
    if (dexid__iivgl != A.dtype.elem_type and dexid__iivgl != types.
        unicode_type):
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if dexid__iivgl == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            fvr__gmzhr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for etx__zxiqx in numba.parfors.parfor.internal_prange(n):
                hiti__dqgl = codes[etx__zxiqx]
                if hiti__dqgl == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(fvr__gmzhr
                            , etx__zxiqx)
                    else:
                        bodo.libs.array_kernels.setna(fvr__gmzhr, etx__zxiqx)
                    continue
                fvr__gmzhr[etx__zxiqx] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[hiti__dqgl]))
            return fvr__gmzhr
        return impl
    tqzdh__qlhvb = dtype_to_array_type(dexid__iivgl)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        fvr__gmzhr = bodo.utils.utils.alloc_type(n, tqzdh__qlhvb, (-1,))
        for etx__zxiqx in numba.parfors.parfor.internal_prange(n):
            hiti__dqgl = codes[etx__zxiqx]
            if hiti__dqgl == -1:
                bodo.libs.array_kernels.setna(fvr__gmzhr, etx__zxiqx)
                continue
            fvr__gmzhr[etx__zxiqx] = bodo.utils.conversion.unbox_if_timestamp(
                categories[hiti__dqgl])
        return fvr__gmzhr
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        vwz__czxdq, lmq__tplv = args
        czgzu__tqu = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        czgzu__tqu.codes = vwz__czxdq
        czgzu__tqu.dtype = lmq__tplv
        context.nrt.incref(builder, signature.args[0], vwz__czxdq)
        context.nrt.incref(builder, signature.args[1], lmq__tplv)
        return czgzu__tqu._getvalue()
    shg__scm = CategoricalArrayType(cat_dtype)
    sig = shg__scm(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    agu__kss = args[0]
    if equiv_set.has_shape(agu__kss):
        return ArrayAnalysis.AnalyzeResult(shape=agu__kss, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    lro__biyii = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, lro__biyii)
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
            iktee__fmrq = {}
            vkrlg__musbh = np.empty(n + 1, np.int64)
            fyclq__chf = {}
            rjp__gtvoy = []
            ffz__grzb = {}
            for etx__zxiqx in range(n):
                ffz__grzb[categories[etx__zxiqx]] = etx__zxiqx
            for tmilv__sduyz in to_replace:
                if tmilv__sduyz != value:
                    if tmilv__sduyz in ffz__grzb:
                        if value in ffz__grzb:
                            iktee__fmrq[tmilv__sduyz] = tmilv__sduyz
                            gbuyl__dre = ffz__grzb[tmilv__sduyz]
                            fyclq__chf[gbuyl__dre] = ffz__grzb[value]
                            rjp__gtvoy.append(gbuyl__dre)
                        else:
                            iktee__fmrq[tmilv__sduyz] = value
                            ffz__grzb[value] = ffz__grzb[tmilv__sduyz]
            syji__vpm = np.sort(np.array(rjp__gtvoy))
            iyqfu__eeho = 0
            juo__apixf = []
            for vmv__xxib in range(-1, n):
                while iyqfu__eeho < len(syji__vpm) and vmv__xxib > syji__vpm[
                    iyqfu__eeho]:
                    iyqfu__eeho += 1
                juo__apixf.append(iyqfu__eeho)
            for wro__rdefl in range(-1, n):
                ngw__rux = wro__rdefl
                if wro__rdefl in fyclq__chf:
                    ngw__rux = fyclq__chf[wro__rdefl]
                vkrlg__musbh[wro__rdefl + 1] = ngw__rux - juo__apixf[
                    ngw__rux + 1]
            return iktee__fmrq, vkrlg__musbh, len(syji__vpm)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for etx__zxiqx in range(len(new_codes_arr)):
        new_codes_arr[etx__zxiqx] = codes_map_arr[old_codes_arr[etx__zxiqx] + 1
            ]


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
    evhr__rqaiy = arr.dtype.ordered
    rykx__ncpy = arr.dtype.elem_type
    eog__awt = get_overload_const(to_replace)
    fih__oflkk = get_overload_const(value)
    if (arr.dtype.categories is not None and eog__awt is not NOT_CONSTANT and
        fih__oflkk is not NOT_CONSTANT):
        wdd__seskc, codes_map_arr, uriw__rjipx = python_build_replace_dicts(
            eog__awt, fih__oflkk, arr.dtype.categories)
        if len(wdd__seskc) == 0:
            return lambda arr, to_replace, value: arr.copy()
        xdmg__kwdc = []
        for zmmr__xpvn in arr.dtype.categories:
            if zmmr__xpvn in wdd__seskc:
                twce__jdk = wdd__seskc[zmmr__xpvn]
                if twce__jdk != zmmr__xpvn:
                    xdmg__kwdc.append(twce__jdk)
            else:
                xdmg__kwdc.append(zmmr__xpvn)
        ahw__mijdb = bodo.utils.utils.create_categorical_type(xdmg__kwdc,
            arr.dtype.data.data, evhr__rqaiy)
        ugvkm__duu = MetaType(tuple(ahw__mijdb))

        def impl_dtype(arr, to_replace, value):
            juaka__wmp = init_cat_dtype(bodo.utils.conversion.
                index_from_array(ahw__mijdb), evhr__rqaiy, None, ugvkm__duu)
            czgzu__tqu = alloc_categorical_array(len(arr.codes), juaka__wmp)
            reassign_codes(czgzu__tqu.codes, arr.codes, codes_map_arr)
            return czgzu__tqu
        return impl_dtype
    rykx__ncpy = arr.dtype.elem_type
    if rykx__ncpy == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            iktee__fmrq, codes_map_arr, ovj__pdz = build_replace_dicts(
                to_replace, value, categories.values)
            if len(iktee__fmrq) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), evhr__rqaiy,
                    None, None))
            n = len(categories)
            ahw__mijdb = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                ovj__pdz, -1)
            msdrb__dohjz = 0
            for vmv__xxib in range(n):
                wxwas__drhrh = categories[vmv__xxib]
                if wxwas__drhrh in iktee__fmrq:
                    nqzrq__gfohc = iktee__fmrq[wxwas__drhrh]
                    if nqzrq__gfohc != wxwas__drhrh:
                        ahw__mijdb[msdrb__dohjz] = nqzrq__gfohc
                        msdrb__dohjz += 1
                else:
                    ahw__mijdb[msdrb__dohjz] = wxwas__drhrh
                    msdrb__dohjz += 1
            czgzu__tqu = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                ahw__mijdb), evhr__rqaiy, None, None))
            reassign_codes(czgzu__tqu.codes, arr.codes, codes_map_arr)
            return czgzu__tqu
        return impl_str
    iue__xqjj = dtype_to_array_type(rykx__ncpy)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        iktee__fmrq, codes_map_arr, ovj__pdz = build_replace_dicts(to_replace,
            value, categories.values)
        if len(iktee__fmrq) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), evhr__rqaiy, None, None))
        n = len(categories)
        ahw__mijdb = bodo.utils.utils.alloc_type(n - ovj__pdz, iue__xqjj, None)
        msdrb__dohjz = 0
        for etx__zxiqx in range(n):
            wxwas__drhrh = categories[etx__zxiqx]
            if wxwas__drhrh in iktee__fmrq:
                nqzrq__gfohc = iktee__fmrq[wxwas__drhrh]
                if nqzrq__gfohc != wxwas__drhrh:
                    ahw__mijdb[msdrb__dohjz] = nqzrq__gfohc
                    msdrb__dohjz += 1
            else:
                ahw__mijdb[msdrb__dohjz] = wxwas__drhrh
                msdrb__dohjz += 1
        czgzu__tqu = alloc_categorical_array(len(arr.codes), init_cat_dtype
            (bodo.utils.conversion.index_from_array(ahw__mijdb),
            evhr__rqaiy, None, None))
        reassign_codes(czgzu__tqu.codes, arr.codes, codes_map_arr)
        return czgzu__tqu
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
    tahlx__fvua = dict()
    tetn__lhwl = 0
    for etx__zxiqx in range(len(vals)):
        val = vals[etx__zxiqx]
        if val in tahlx__fvua:
            continue
        tahlx__fvua[val] = tetn__lhwl
        tetn__lhwl += 1
    return tahlx__fvua


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    tahlx__fvua = dict()
    for etx__zxiqx in range(len(vals)):
        val = vals[etx__zxiqx]
        tahlx__fvua[val] = etx__zxiqx
    return tahlx__fvua


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    ydk__jhd = dict(fastpath=fastpath)
    tbohe__jmq = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', ydk__jhd, tbohe__jmq)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        lama__vvob = get_overload_const(categories)
        if lama__vvob is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                gycl__pby = False
            else:
                gycl__pby = get_overload_const_bool(ordered)
            qfpb__axpxq = pd.CategoricalDtype(pd.array(lama__vvob), gycl__pby
                ).categories.array
            asymg__cxeh = MetaType(tuple(qfpb__axpxq))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                juaka__wmp = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(qfpb__axpxq), gycl__pby, None, asymg__cxeh
                    )
                return bodo.utils.conversion.fix_arr_dtype(data, juaka__wmp)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            idv__kmyfg = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                idv__kmyfg, ordered, None, None)
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
            kbbvf__ypbvq = arr.codes[ind]
            return arr.dtype.categories[max(kbbvf__ypbvq, 0)]
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
    for etx__zxiqx in range(len(arr1)):
        if arr1[etx__zxiqx] != arr2[etx__zxiqx]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    rbkiq__wdf = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    ksrxh__bcdy = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    nhel__ywuj = categorical_arrs_match(arr, val)
    ytf__wvmqw = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    bivbq__tefeh = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not rbkiq__wdf:
            raise BodoError(ytf__wvmqw)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            kbbvf__ypbvq = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = kbbvf__ypbvq
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (rbkiq__wdf or ksrxh__bcdy or nhel__ywuj !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(ytf__wvmqw)
        if nhel__ywuj == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(bivbq__tefeh)
        if rbkiq__wdf:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ayuy__bbw = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for vmv__xxib in range(n):
                    arr.codes[ind[vmv__xxib]] = ayuy__bbw
            return impl_scalar
        if nhel__ywuj == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for etx__zxiqx in range(n):
                    arr.codes[ind[etx__zxiqx]] = val.codes[etx__zxiqx]
            return impl_arr_ind_mask
        if nhel__ywuj == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(bivbq__tefeh)
                n = len(val.codes)
                for etx__zxiqx in range(n):
                    arr.codes[ind[etx__zxiqx]] = val.codes[etx__zxiqx]
            return impl_arr_ind_mask
        if ksrxh__bcdy:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for vmv__xxib in range(n):
                    blxld__qocvh = bodo.utils.conversion.unbox_if_timestamp(val
                        [vmv__xxib])
                    if blxld__qocvh not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    kbbvf__ypbvq = categories.get_loc(blxld__qocvh)
                    arr.codes[ind[vmv__xxib]] = kbbvf__ypbvq
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (rbkiq__wdf or ksrxh__bcdy or nhel__ywuj !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(ytf__wvmqw)
        if nhel__ywuj == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(bivbq__tefeh)
        if rbkiq__wdf:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ayuy__bbw = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for vmv__xxib in range(n):
                    if ind[vmv__xxib]:
                        arr.codes[vmv__xxib] = ayuy__bbw
            return impl_scalar
        if nhel__ywuj == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                iomh__whxa = 0
                for etx__zxiqx in range(n):
                    if ind[etx__zxiqx]:
                        arr.codes[etx__zxiqx] = val.codes[iomh__whxa]
                        iomh__whxa += 1
            return impl_bool_ind_mask
        if nhel__ywuj == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(bivbq__tefeh)
                n = len(ind)
                iomh__whxa = 0
                for etx__zxiqx in range(n):
                    if ind[etx__zxiqx]:
                        arr.codes[etx__zxiqx] = val.codes[iomh__whxa]
                        iomh__whxa += 1
            return impl_bool_ind_mask
        if ksrxh__bcdy:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                iomh__whxa = 0
                categories = arr.dtype.categories
                for vmv__xxib in range(n):
                    if ind[vmv__xxib]:
                        blxld__qocvh = (bodo.utils.conversion.
                            unbox_if_timestamp(val[iomh__whxa]))
                        if blxld__qocvh not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        kbbvf__ypbvq = categories.get_loc(blxld__qocvh)
                        arr.codes[vmv__xxib] = kbbvf__ypbvq
                        iomh__whxa += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (rbkiq__wdf or ksrxh__bcdy or nhel__ywuj !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(ytf__wvmqw)
        if nhel__ywuj == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(bivbq__tefeh)
        if rbkiq__wdf:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                ayuy__bbw = arr.dtype.categories.get_loc(val)
                kmyo__zrt = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                for vmv__xxib in range(kmyo__zrt.start, kmyo__zrt.stop,
                    kmyo__zrt.step):
                    arr.codes[vmv__xxib] = ayuy__bbw
            return impl_scalar
        if nhel__ywuj == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if nhel__ywuj == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(bivbq__tefeh)
                arr.codes[ind] = val.codes
            return impl_arr
        if ksrxh__bcdy:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                kmyo__zrt = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                iomh__whxa = 0
                for vmv__xxib in range(kmyo__zrt.start, kmyo__zrt.stop,
                    kmyo__zrt.step):
                    blxld__qocvh = bodo.utils.conversion.unbox_if_timestamp(val
                        [iomh__whxa])
                    if blxld__qocvh not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    kbbvf__ypbvq = categories.get_loc(blxld__qocvh)
                    arr.codes[vmv__xxib] = kbbvf__ypbvq
                    iomh__whxa += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
