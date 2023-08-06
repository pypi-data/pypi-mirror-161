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
        toj__cod = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=toj__cod)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    cqb__jvq = tuple(val.categories.values)
    elem_type = None if len(cqb__jvq) == 0 else bodo.typeof(val.categories.
        values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(cqb__jvq, elem_type, val.ordered, bodo.typeof
        (val.categories), int_type)


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
        llgev__oczgb = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, llgev__oczgb)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    gfdz__vgzac = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    odq__twks = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, lhk__ezkqc, lhk__ezkqc = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    kdj__wpt = PDCategoricalDtype(odq__twks, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, gfdz__vgzac)
    return kdj__wpt(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    djoyv__tfok = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, djoyv__tfok).value
    c.pyapi.decref(djoyv__tfok)
    wpx__vvxug = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, wpx__vvxug).value
    c.pyapi.decref(wpx__vvxug)
    gyw__xtup = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=gyw__xtup)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    djoyv__tfok = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    ejuq__zrvpe = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    qlw__mkh = c.context.insert_const_string(c.builder.module, 'pandas')
    qcw__lwh = c.pyapi.import_module_noblock(qlw__mkh)
    wjnb__aprhg = c.pyapi.call_method(qcw__lwh, 'CategoricalDtype', (
        ejuq__zrvpe, djoyv__tfok))
    c.pyapi.decref(djoyv__tfok)
    c.pyapi.decref(ejuq__zrvpe)
    c.pyapi.decref(qcw__lwh)
    c.context.nrt.decref(c.builder, typ, val)
    return wjnb__aprhg


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
        hbbvf__oaiuo = get_categories_int_type(fe_type.dtype)
        llgev__oczgb = [('dtype', fe_type.dtype), ('codes', types.Array(
            hbbvf__oaiuo, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, llgev__oczgb)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    lyuiu__quunr = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), lyuiu__quunr
        ).value
    c.pyapi.decref(lyuiu__quunr)
    wjnb__aprhg = c.pyapi.object_getattr_string(val, 'dtype')
    uvxqp__edcbm = c.pyapi.to_native_value(typ.dtype, wjnb__aprhg).value
    c.pyapi.decref(wjnb__aprhg)
    wyslx__kqrmn = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    wyslx__kqrmn.codes = codes
    wyslx__kqrmn.dtype = uvxqp__edcbm
    return NativeValue(wyslx__kqrmn._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    jaknv__dsl = get_categories_int_type(typ.dtype)
    fpwdo__upiu = context.get_constant_generic(builder, types.Array(
        jaknv__dsl, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, fpwdo__upiu])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    vxrgq__evrli = len(cat_dtype.categories)
    if vxrgq__evrli < np.iinfo(np.int8).max:
        dtype = types.int8
    elif vxrgq__evrli < np.iinfo(np.int16).max:
        dtype = types.int16
    elif vxrgq__evrli < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    qlw__mkh = c.context.insert_const_string(c.builder.module, 'pandas')
    qcw__lwh = c.pyapi.import_module_noblock(qlw__mkh)
    hbbvf__oaiuo = get_categories_int_type(dtype)
    kop__btdw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    mci__zlqz = types.Array(hbbvf__oaiuo, 1, 'C')
    c.context.nrt.incref(c.builder, mci__zlqz, kop__btdw.codes)
    lyuiu__quunr = c.pyapi.from_native_value(mci__zlqz, kop__btdw.codes, c.
        env_manager)
    c.context.nrt.incref(c.builder, dtype, kop__btdw.dtype)
    wjnb__aprhg = c.pyapi.from_native_value(dtype, kop__btdw.dtype, c.
        env_manager)
    xczbd__vgtt = c.pyapi.borrow_none()
    hae__soa = c.pyapi.object_getattr_string(qcw__lwh, 'Categorical')
    gkd__szf = c.pyapi.call_method(hae__soa, 'from_codes', (lyuiu__quunr,
        xczbd__vgtt, xczbd__vgtt, wjnb__aprhg))
    c.pyapi.decref(hae__soa)
    c.pyapi.decref(lyuiu__quunr)
    c.pyapi.decref(wjnb__aprhg)
    c.pyapi.decref(qcw__lwh)
    c.context.nrt.decref(c.builder, typ, val)
    return gkd__szf


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
            tohj__zvu = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                uzym__sbjwk = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), tohj__zvu)
                return uzym__sbjwk
            return impl_lit

        def impl(A, other):
            tohj__zvu = get_code_for_value(A.dtype, other)
            uzym__sbjwk = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), tohj__zvu)
            return uzym__sbjwk
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        djma__knu = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(djma__knu)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    kop__btdw = cat_dtype.categories
    n = len(kop__btdw)
    for zbus__ofjc in range(n):
        if kop__btdw[zbus__ofjc] == val:
            return zbus__ofjc
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    optnd__mledv = bodo.utils.typing.parse_dtype(dtype,
        'CategoricalArray.astype')
    if (optnd__mledv != A.dtype.elem_type and optnd__mledv != types.
        unicode_type):
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if optnd__mledv == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            uzym__sbjwk = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for zbus__ofjc in numba.parfors.parfor.internal_prange(n):
                ggjv__nurcn = codes[zbus__ofjc]
                if ggjv__nurcn == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(
                            uzym__sbjwk, zbus__ofjc)
                    else:
                        bodo.libs.array_kernels.setna(uzym__sbjwk, zbus__ofjc)
                    continue
                uzym__sbjwk[zbus__ofjc] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[ggjv__nurcn]))
            return uzym__sbjwk
        return impl
    mci__zlqz = dtype_to_array_type(optnd__mledv)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        uzym__sbjwk = bodo.utils.utils.alloc_type(n, mci__zlqz, (-1,))
        for zbus__ofjc in numba.parfors.parfor.internal_prange(n):
            ggjv__nurcn = codes[zbus__ofjc]
            if ggjv__nurcn == -1:
                bodo.libs.array_kernels.setna(uzym__sbjwk, zbus__ofjc)
                continue
            uzym__sbjwk[zbus__ofjc] = bodo.utils.conversion.unbox_if_timestamp(
                categories[ggjv__nurcn])
        return uzym__sbjwk
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        hhlec__bfvb, uvxqp__edcbm = args
        kop__btdw = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        kop__btdw.codes = hhlec__bfvb
        kop__btdw.dtype = uvxqp__edcbm
        context.nrt.incref(builder, signature.args[0], hhlec__bfvb)
        context.nrt.incref(builder, signature.args[1], uvxqp__edcbm)
        return kop__btdw._getvalue()
    atxra__liup = CategoricalArrayType(cat_dtype)
    sig = atxra__liup(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    cfatg__knseb = args[0]
    if equiv_set.has_shape(cfatg__knseb):
        return ArrayAnalysis.AnalyzeResult(shape=cfatg__knseb, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    hbbvf__oaiuo = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, hbbvf__oaiuo)
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
            agtw__xxjw = {}
            fpwdo__upiu = np.empty(n + 1, np.int64)
            hnagx__fywge = {}
            zmv__myij = []
            lfttx__xuhkr = {}
            for zbus__ofjc in range(n):
                lfttx__xuhkr[categories[zbus__ofjc]] = zbus__ofjc
            for jyg__dgftb in to_replace:
                if jyg__dgftb != value:
                    if jyg__dgftb in lfttx__xuhkr:
                        if value in lfttx__xuhkr:
                            agtw__xxjw[jyg__dgftb] = jyg__dgftb
                            nrpx__wpbre = lfttx__xuhkr[jyg__dgftb]
                            hnagx__fywge[nrpx__wpbre] = lfttx__xuhkr[value]
                            zmv__myij.append(nrpx__wpbre)
                        else:
                            agtw__xxjw[jyg__dgftb] = value
                            lfttx__xuhkr[value] = lfttx__xuhkr[jyg__dgftb]
            uwq__ulo = np.sort(np.array(zmv__myij))
            mizc__mnwmm = 0
            lgcl__ibxrs = []
            for meys__muv in range(-1, n):
                while mizc__mnwmm < len(uwq__ulo) and meys__muv > uwq__ulo[
                    mizc__mnwmm]:
                    mizc__mnwmm += 1
                lgcl__ibxrs.append(mizc__mnwmm)
            for twey__ldgy in range(-1, n):
                klvu__jawhu = twey__ldgy
                if twey__ldgy in hnagx__fywge:
                    klvu__jawhu = hnagx__fywge[twey__ldgy]
                fpwdo__upiu[twey__ldgy + 1] = klvu__jawhu - lgcl__ibxrs[
                    klvu__jawhu + 1]
            return agtw__xxjw, fpwdo__upiu, len(uwq__ulo)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for zbus__ofjc in range(len(new_codes_arr)):
        new_codes_arr[zbus__ofjc] = codes_map_arr[old_codes_arr[zbus__ofjc] + 1
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
    cta__qdv = arr.dtype.ordered
    unu__rnfb = arr.dtype.elem_type
    xxhu__gcs = get_overload_const(to_replace)
    zbx__cdfc = get_overload_const(value)
    if (arr.dtype.categories is not None and xxhu__gcs is not NOT_CONSTANT and
        zbx__cdfc is not NOT_CONSTANT):
        xhnb__pnay, codes_map_arr, lhk__ezkqc = python_build_replace_dicts(
            xxhu__gcs, zbx__cdfc, arr.dtype.categories)
        if len(xhnb__pnay) == 0:
            return lambda arr, to_replace, value: arr.copy()
        cgq__dffgn = []
        for rdkx__tok in arr.dtype.categories:
            if rdkx__tok in xhnb__pnay:
                imt__zwo = xhnb__pnay[rdkx__tok]
                if imt__zwo != rdkx__tok:
                    cgq__dffgn.append(imt__zwo)
            else:
                cgq__dffgn.append(rdkx__tok)
        anfnu__uiy = bodo.utils.utils.create_categorical_type(cgq__dffgn,
            arr.dtype.data.data, cta__qdv)
        dpcj__rrjmv = MetaType(tuple(anfnu__uiy))

        def impl_dtype(arr, to_replace, value):
            cvdw__jqg = init_cat_dtype(bodo.utils.conversion.
                index_from_array(anfnu__uiy), cta__qdv, None, dpcj__rrjmv)
            kop__btdw = alloc_categorical_array(len(arr.codes), cvdw__jqg)
            reassign_codes(kop__btdw.codes, arr.codes, codes_map_arr)
            return kop__btdw
        return impl_dtype
    unu__rnfb = arr.dtype.elem_type
    if unu__rnfb == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            agtw__xxjw, codes_map_arr, bev__gksre = build_replace_dicts(
                to_replace, value, categories.values)
            if len(agtw__xxjw) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), cta__qdv,
                    None, None))
            n = len(categories)
            anfnu__uiy = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                bev__gksre, -1)
            qbpa__wdab = 0
            for meys__muv in range(n):
                txjmz__wjjh = categories[meys__muv]
                if txjmz__wjjh in agtw__xxjw:
                    ydkwh__aboo = agtw__xxjw[txjmz__wjjh]
                    if ydkwh__aboo != txjmz__wjjh:
                        anfnu__uiy[qbpa__wdab] = ydkwh__aboo
                        qbpa__wdab += 1
                else:
                    anfnu__uiy[qbpa__wdab] = txjmz__wjjh
                    qbpa__wdab += 1
            kop__btdw = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                anfnu__uiy), cta__qdv, None, None))
            reassign_codes(kop__btdw.codes, arr.codes, codes_map_arr)
            return kop__btdw
        return impl_str
    jun__pym = dtype_to_array_type(unu__rnfb)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        agtw__xxjw, codes_map_arr, bev__gksre = build_replace_dicts(to_replace,
            value, categories.values)
        if len(agtw__xxjw) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), cta__qdv, None, None))
        n = len(categories)
        anfnu__uiy = bodo.utils.utils.alloc_type(n - bev__gksre, jun__pym, None
            )
        qbpa__wdab = 0
        for zbus__ofjc in range(n):
            txjmz__wjjh = categories[zbus__ofjc]
            if txjmz__wjjh in agtw__xxjw:
                ydkwh__aboo = agtw__xxjw[txjmz__wjjh]
                if ydkwh__aboo != txjmz__wjjh:
                    anfnu__uiy[qbpa__wdab] = ydkwh__aboo
                    qbpa__wdab += 1
            else:
                anfnu__uiy[qbpa__wdab] = txjmz__wjjh
                qbpa__wdab += 1
        kop__btdw = alloc_categorical_array(len(arr.codes), init_cat_dtype(
            bodo.utils.conversion.index_from_array(anfnu__uiy), cta__qdv,
            None, None))
        reassign_codes(kop__btdw.codes, arr.codes, codes_map_arr)
        return kop__btdw
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
    qxx__ffjrb = dict()
    upj__vdjgo = 0
    for zbus__ofjc in range(len(vals)):
        val = vals[zbus__ofjc]
        if val in qxx__ffjrb:
            continue
        qxx__ffjrb[val] = upj__vdjgo
        upj__vdjgo += 1
    return qxx__ffjrb


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    qxx__ffjrb = dict()
    for zbus__ofjc in range(len(vals)):
        val = vals[zbus__ofjc]
        qxx__ffjrb[val] = zbus__ofjc
    return qxx__ffjrb


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    kitz__ojt = dict(fastpath=fastpath)
    qpvbd__wjln = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', kitz__ojt, qpvbd__wjln)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        jkcla__kazf = get_overload_const(categories)
        if jkcla__kazf is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                gtu__nqad = False
            else:
                gtu__nqad = get_overload_const_bool(ordered)
            ginb__slg = pd.CategoricalDtype(pd.array(jkcla__kazf), gtu__nqad
                ).categories.array
            gfzwt__tqd = MetaType(tuple(ginb__slg))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                cvdw__jqg = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(ginb__slg), gtu__nqad, None, gfzwt__tqd)
                return bodo.utils.conversion.fix_arr_dtype(data, cvdw__jqg)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            cqb__jvq = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                cqb__jvq, ordered, None, None)
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
            kjzu__dlfd = arr.codes[ind]
            return arr.dtype.categories[max(kjzu__dlfd, 0)]
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
    for zbus__ofjc in range(len(arr1)):
        if arr1[zbus__ofjc] != arr2[zbus__ofjc]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    prfsa__kjzgv = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    mltjz__xexb = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    ypxs__iqrth = categorical_arrs_match(arr, val)
    uustf__cfc = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    phxwk__ffb = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not prfsa__kjzgv:
            raise BodoError(uustf__cfc)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            kjzu__dlfd = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = kjzu__dlfd
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (prfsa__kjzgv or mltjz__xexb or ypxs__iqrth !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(uustf__cfc)
        if ypxs__iqrth == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(phxwk__ffb)
        if prfsa__kjzgv:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                iewui__fuh = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for meys__muv in range(n):
                    arr.codes[ind[meys__muv]] = iewui__fuh
            return impl_scalar
        if ypxs__iqrth == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for zbus__ofjc in range(n):
                    arr.codes[ind[zbus__ofjc]] = val.codes[zbus__ofjc]
            return impl_arr_ind_mask
        if ypxs__iqrth == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(phxwk__ffb)
                n = len(val.codes)
                for zbus__ofjc in range(n):
                    arr.codes[ind[zbus__ofjc]] = val.codes[zbus__ofjc]
            return impl_arr_ind_mask
        if mltjz__xexb:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for meys__muv in range(n):
                    gaw__vfcyv = bodo.utils.conversion.unbox_if_timestamp(val
                        [meys__muv])
                    if gaw__vfcyv not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    kjzu__dlfd = categories.get_loc(gaw__vfcyv)
                    arr.codes[ind[meys__muv]] = kjzu__dlfd
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (prfsa__kjzgv or mltjz__xexb or ypxs__iqrth !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(uustf__cfc)
        if ypxs__iqrth == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(phxwk__ffb)
        if prfsa__kjzgv:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                iewui__fuh = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for meys__muv in range(n):
                    if ind[meys__muv]:
                        arr.codes[meys__muv] = iewui__fuh
            return impl_scalar
        if ypxs__iqrth == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                gnu__rpqc = 0
                for zbus__ofjc in range(n):
                    if ind[zbus__ofjc]:
                        arr.codes[zbus__ofjc] = val.codes[gnu__rpqc]
                        gnu__rpqc += 1
            return impl_bool_ind_mask
        if ypxs__iqrth == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(phxwk__ffb)
                n = len(ind)
                gnu__rpqc = 0
                for zbus__ofjc in range(n):
                    if ind[zbus__ofjc]:
                        arr.codes[zbus__ofjc] = val.codes[gnu__rpqc]
                        gnu__rpqc += 1
            return impl_bool_ind_mask
        if mltjz__xexb:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                gnu__rpqc = 0
                categories = arr.dtype.categories
                for meys__muv in range(n):
                    if ind[meys__muv]:
                        gaw__vfcyv = bodo.utils.conversion.unbox_if_timestamp(
                            val[gnu__rpqc])
                        if gaw__vfcyv not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        kjzu__dlfd = categories.get_loc(gaw__vfcyv)
                        arr.codes[meys__muv] = kjzu__dlfd
                        gnu__rpqc += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (prfsa__kjzgv or mltjz__xexb or ypxs__iqrth !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(uustf__cfc)
        if ypxs__iqrth == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(phxwk__ffb)
        if prfsa__kjzgv:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                iewui__fuh = arr.dtype.categories.get_loc(val)
                uxn__xrhsp = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                for meys__muv in range(uxn__xrhsp.start, uxn__xrhsp.stop,
                    uxn__xrhsp.step):
                    arr.codes[meys__muv] = iewui__fuh
            return impl_scalar
        if ypxs__iqrth == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if ypxs__iqrth == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(phxwk__ffb)
                arr.codes[ind] = val.codes
            return impl_arr
        if mltjz__xexb:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                uxn__xrhsp = numba.cpython.unicode._normalize_slice(ind,
                    len(arr))
                gnu__rpqc = 0
                for meys__muv in range(uxn__xrhsp.start, uxn__xrhsp.stop,
                    uxn__xrhsp.step):
                    gaw__vfcyv = bodo.utils.conversion.unbox_if_timestamp(val
                        [gnu__rpqc])
                    if gaw__vfcyv not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    kjzu__dlfd = categories.get_loc(gaw__vfcyv)
                    arr.codes[meys__muv] = kjzu__dlfd
                    gnu__rpqc += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
