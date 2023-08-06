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
        jlx__qxutv = (
            f'PDCategoricalDtype({self.categories}, {self.elem_type}, {self.ordered}, {self.data}, {self.int_type})'
            )
        super(PDCategoricalDtype, self).__init__(name=jlx__qxutv)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(pd.CategoricalDtype)
def _typeof_pd_cat_dtype(val, c):
    kiznh__bspb = tuple(val.categories.values)
    elem_type = None if len(kiznh__bspb) == 0 else bodo.typeof(val.
        categories.values).dtype
    int_type = getattr(val, '_int_type', None)
    return PDCategoricalDtype(kiznh__bspb, elem_type, val.ordered, bodo.
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
        sdovk__vnfwu = [('categories', fe_type.data), ('ordered', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, sdovk__vnfwu)


make_attribute_wrapper(PDCategoricalDtype, 'categories', 'categories')
make_attribute_wrapper(PDCategoricalDtype, 'ordered', 'ordered')


@intrinsic
def init_cat_dtype(typingctx, categories_typ, ordered_typ, int_type,
    cat_vals_typ=None):
    assert bodo.hiframes.pd_index_ext.is_index_type(categories_typ
        ), 'init_cat_dtype requires index type for categories'
    assert is_overload_constant_bool(ordered_typ
        ), 'init_cat_dtype requires constant ordered flag'
    rno__jrog = None if is_overload_none(int_type) else int_type.dtype
    assert is_overload_none(cat_vals_typ) or isinstance(cat_vals_typ, types
        .TypeRef), 'init_cat_dtype requires constant category values'
    gxq__smjql = None if is_overload_none(cat_vals_typ
        ) else cat_vals_typ.instance_type.meta

    def codegen(context, builder, sig, args):
        categories, ordered, jtnv__uabcy, jtnv__uabcy = args
        cat_dtype = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        cat_dtype.categories = categories
        context.nrt.incref(builder, sig.args[0], categories)
        context.nrt.incref(builder, sig.args[1], ordered)
        cat_dtype.ordered = ordered
        return cat_dtype._getvalue()
    zsj__lxmtv = PDCategoricalDtype(gxq__smjql, categories_typ.dtype,
        is_overload_true(ordered_typ), categories_typ, rno__jrog)
    return zsj__lxmtv(categories_typ, ordered_typ, int_type, cat_vals_typ
        ), codegen


@unbox(PDCategoricalDtype)
def unbox_cat_dtype(typ, obj, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    zvum__zvvsh = c.pyapi.object_getattr_string(obj, 'ordered')
    cat_dtype.ordered = c.pyapi.to_native_value(types.bool_, zvum__zvvsh).value
    c.pyapi.decref(zvum__zvvsh)
    uky__alepi = c.pyapi.object_getattr_string(obj, 'categories')
    cat_dtype.categories = c.pyapi.to_native_value(typ.data, uky__alepi).value
    c.pyapi.decref(uky__alepi)
    mvdd__srr = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(cat_dtype._getvalue(), is_error=mvdd__srr)


@box(PDCategoricalDtype)
def box_cat_dtype(typ, val, c):
    cat_dtype = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    zvum__zvvsh = c.pyapi.from_native_value(types.bool_, cat_dtype.ordered,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.data, cat_dtype.categories)
    zduzf__srw = c.pyapi.from_native_value(typ.data, cat_dtype.categories,
        c.env_manager)
    yexmh__civq = c.context.insert_const_string(c.builder.module, 'pandas')
    zhr__ids = c.pyapi.import_module_noblock(yexmh__civq)
    vio__grlnf = c.pyapi.call_method(zhr__ids, 'CategoricalDtype', (
        zduzf__srw, zvum__zvvsh))
    c.pyapi.decref(zvum__zvvsh)
    c.pyapi.decref(zduzf__srw)
    c.pyapi.decref(zhr__ids)
    c.context.nrt.decref(c.builder, typ, val)
    return vio__grlnf


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
        tjqr__rbm = get_categories_int_type(fe_type.dtype)
        sdovk__vnfwu = [('dtype', fe_type.dtype), ('codes', types.Array(
            tjqr__rbm, 1, 'C'))]
        super(CategoricalArrayModel, self).__init__(dmm, fe_type, sdovk__vnfwu)


make_attribute_wrapper(CategoricalArrayType, 'codes', 'codes')
make_attribute_wrapper(CategoricalArrayType, 'dtype', 'dtype')


@unbox(CategoricalArrayType)
def unbox_categorical_array(typ, val, c):
    olp__uvc = c.pyapi.object_getattr_string(val, 'codes')
    dtype = get_categories_int_type(typ.dtype)
    codes = c.pyapi.to_native_value(types.Array(dtype, 1, 'C'), olp__uvc).value
    c.pyapi.decref(olp__uvc)
    vio__grlnf = c.pyapi.object_getattr_string(val, 'dtype')
    amdcb__mhbq = c.pyapi.to_native_value(typ.dtype, vio__grlnf).value
    c.pyapi.decref(vio__grlnf)
    ezxwn__qgqqw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ezxwn__qgqqw.codes = codes
    ezxwn__qgqqw.dtype = amdcb__mhbq
    return NativeValue(ezxwn__qgqqw._getvalue())


@lower_constant(CategoricalArrayType)
def lower_constant_categorical_array(context, builder, typ, pyval):
    rrot__ofgha = get_categories_int_type(typ.dtype)
    wpw__eyo = context.get_constant_generic(builder, types.Array(
        rrot__ofgha, 1, 'C'), pyval.codes)
    cat_dtype = context.get_constant_generic(builder, typ.dtype, pyval.dtype)
    return lir.Constant.literal_struct([cat_dtype, wpw__eyo])


def get_categories_int_type(cat_dtype):
    dtype = types.int64
    if cat_dtype.int_type is not None:
        return cat_dtype.int_type
    if cat_dtype.categories is None:
        return types.int64
    rhe__dkyhj = len(cat_dtype.categories)
    if rhe__dkyhj < np.iinfo(np.int8).max:
        dtype = types.int8
    elif rhe__dkyhj < np.iinfo(np.int16).max:
        dtype = types.int16
    elif rhe__dkyhj < np.iinfo(np.int32).max:
        dtype = types.int32
    return dtype


@box(CategoricalArrayType)
def box_categorical_array(typ, val, c):
    dtype = typ.dtype
    yexmh__civq = c.context.insert_const_string(c.builder.module, 'pandas')
    zhr__ids = c.pyapi.import_module_noblock(yexmh__civq)
    tjqr__rbm = get_categories_int_type(dtype)
    vkaip__fkwd = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    ehg__wyzhm = types.Array(tjqr__rbm, 1, 'C')
    c.context.nrt.incref(c.builder, ehg__wyzhm, vkaip__fkwd.codes)
    olp__uvc = c.pyapi.from_native_value(ehg__wyzhm, vkaip__fkwd.codes, c.
        env_manager)
    c.context.nrt.incref(c.builder, dtype, vkaip__fkwd.dtype)
    vio__grlnf = c.pyapi.from_native_value(dtype, vkaip__fkwd.dtype, c.
        env_manager)
    hkuro__zdg = c.pyapi.borrow_none()
    rja__fkd = c.pyapi.object_getattr_string(zhr__ids, 'Categorical')
    yekea__kdyq = c.pyapi.call_method(rja__fkd, 'from_codes', (olp__uvc,
        hkuro__zdg, hkuro__zdg, vio__grlnf))
    c.pyapi.decref(rja__fkd)
    c.pyapi.decref(olp__uvc)
    c.pyapi.decref(vio__grlnf)
    c.pyapi.decref(zhr__ids)
    c.context.nrt.decref(c.builder, typ, val)
    return yekea__kdyq


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
            tcm__ekuvr = list(A.dtype.categories).index(val
                ) if val in A.dtype.categories else -2

            def impl_lit(A, other):
                mcr__esg = op(bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(A), tcm__ekuvr)
                return mcr__esg
            return impl_lit

        def impl(A, other):
            tcm__ekuvr = get_code_for_value(A.dtype, other)
            mcr__esg = op(bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(A), tcm__ekuvr)
            return mcr__esg
        return impl
    return overload_cat_arr_cmp


def _install_cmp_ops():
    for op in [operator.eq, operator.ne]:
        fuqwn__iye = create_cmp_op_overload(op)
        overload(op, inline='always', no_unliteral=True)(fuqwn__iye)


_install_cmp_ops()


@register_jitable
def get_code_for_value(cat_dtype, val):
    vkaip__fkwd = cat_dtype.categories
    n = len(vkaip__fkwd)
    for wsoxq__mcoa in range(n):
        if vkaip__fkwd[wsoxq__mcoa] == val:
            return wsoxq__mcoa
    return -2


@overload_method(CategoricalArrayType, 'astype', inline='always',
    no_unliteral=True)
def overload_cat_arr_astype(A, dtype, copy=True, _bodo_nan_to_str=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "CategoricalArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    urgk__otxgv = bodo.utils.typing.parse_dtype(dtype,
        'CategoricalArray.astype')
    if urgk__otxgv != A.dtype.elem_type and urgk__otxgv != types.unicode_type:
        raise BodoError(
            f'Converting categorical array {A} to dtype {dtype} not supported yet'
            )
    if urgk__otxgv == types.unicode_type:

        def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
            codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(
                A)
            categories = A.dtype.categories
            n = len(codes)
            mcr__esg = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
            for wsoxq__mcoa in numba.parfors.parfor.internal_prange(n):
                pvp__zzjmx = codes[wsoxq__mcoa]
                if pvp__zzjmx == -1:
                    if _bodo_nan_to_str:
                        bodo.libs.str_arr_ext.str_arr_setitem_NA_str(mcr__esg,
                            wsoxq__mcoa)
                    else:
                        bodo.libs.array_kernels.setna(mcr__esg, wsoxq__mcoa)
                    continue
                mcr__esg[wsoxq__mcoa] = str(bodo.utils.conversion.
                    unbox_if_timestamp(categories[pvp__zzjmx]))
            return mcr__esg
        return impl
    ehg__wyzhm = dtype_to_array_type(urgk__otxgv)

    def impl(A, dtype, copy=True, _bodo_nan_to_str=True):
        codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(A)
        categories = A.dtype.categories
        n = len(codes)
        mcr__esg = bodo.utils.utils.alloc_type(n, ehg__wyzhm, (-1,))
        for wsoxq__mcoa in numba.parfors.parfor.internal_prange(n):
            pvp__zzjmx = codes[wsoxq__mcoa]
            if pvp__zzjmx == -1:
                bodo.libs.array_kernels.setna(mcr__esg, wsoxq__mcoa)
                continue
            mcr__esg[wsoxq__mcoa] = bodo.utils.conversion.unbox_if_timestamp(
                categories[pvp__zzjmx])
        return mcr__esg
    return impl


@overload(pd.api.types.CategoricalDtype, no_unliteral=True)
def cat_overload_dummy(val_list):
    return lambda val_list: 1


@intrinsic
def init_categorical_array(typingctx, codes, cat_dtype=None):
    assert isinstance(codes, types.Array) and isinstance(codes.dtype, types
        .Integer)

    def codegen(context, builder, signature, args):
        guwkp__ndh, amdcb__mhbq = args
        vkaip__fkwd = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        vkaip__fkwd.codes = guwkp__ndh
        vkaip__fkwd.dtype = amdcb__mhbq
        context.nrt.incref(builder, signature.args[0], guwkp__ndh)
        context.nrt.incref(builder, signature.args[1], amdcb__mhbq)
        return vkaip__fkwd._getvalue()
    dan__idti = CategoricalArrayType(cat_dtype)
    sig = dan__idti(codes, cat_dtype)
    return sig, codegen


def init_categorical_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    vpi__rny = args[0]
    if equiv_set.has_shape(vpi__rny):
        return ArrayAnalysis.AnalyzeResult(shape=vpi__rny, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_categorical_ext_init_categorical_array
    ) = init_categorical_array_equiv


def alloc_categorical_array(n, cat_dtype):
    pass


@overload(alloc_categorical_array, no_unliteral=True)
def _alloc_categorical_array(n, cat_dtype):
    tjqr__rbm = get_categories_int_type(cat_dtype)

    def impl(n, cat_dtype):
        codes = np.empty(n, tjqr__rbm)
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
            tnxhk__dqiys = {}
            wpw__eyo = np.empty(n + 1, np.int64)
            bfqgd__sgrbl = {}
            njkg__tuyzp = []
            pzlci__dyks = {}
            for wsoxq__mcoa in range(n):
                pzlci__dyks[categories[wsoxq__mcoa]] = wsoxq__mcoa
            for emhzk__pog in to_replace:
                if emhzk__pog != value:
                    if emhzk__pog in pzlci__dyks:
                        if value in pzlci__dyks:
                            tnxhk__dqiys[emhzk__pog] = emhzk__pog
                            unkwd__kric = pzlci__dyks[emhzk__pog]
                            bfqgd__sgrbl[unkwd__kric] = pzlci__dyks[value]
                            njkg__tuyzp.append(unkwd__kric)
                        else:
                            tnxhk__dqiys[emhzk__pog] = value
                            pzlci__dyks[value] = pzlci__dyks[emhzk__pog]
            mkxql__xcz = np.sort(np.array(njkg__tuyzp))
            ejk__cls = 0
            hhcc__gepaj = []
            for pwp__ebxr in range(-1, n):
                while ejk__cls < len(mkxql__xcz) and pwp__ebxr > mkxql__xcz[
                    ejk__cls]:
                    ejk__cls += 1
                hhcc__gepaj.append(ejk__cls)
            for tpank__asjg in range(-1, n):
                kqw__cxaq = tpank__asjg
                if tpank__asjg in bfqgd__sgrbl:
                    kqw__cxaq = bfqgd__sgrbl[tpank__asjg]
                wpw__eyo[tpank__asjg + 1] = kqw__cxaq - hhcc__gepaj[
                    kqw__cxaq + 1]
            return tnxhk__dqiys, wpw__eyo, len(mkxql__xcz)
        return impl


@numba.njit
def python_build_replace_dicts(to_replace, value, categories):
    return build_replace_dicts(to_replace, value, categories)


@register_jitable
def reassign_codes(new_codes_arr, old_codes_arr, codes_map_arr):
    for wsoxq__mcoa in range(len(new_codes_arr)):
        new_codes_arr[wsoxq__mcoa] = codes_map_arr[old_codes_arr[
            wsoxq__mcoa] + 1]


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
    aurj__azc = arr.dtype.ordered
    nwa__wxrdb = arr.dtype.elem_type
    qlkuf__hjl = get_overload_const(to_replace)
    ylht__ifly = get_overload_const(value)
    if (arr.dtype.categories is not None and qlkuf__hjl is not NOT_CONSTANT and
        ylht__ifly is not NOT_CONSTANT):
        ioeqx__nmd, codes_map_arr, jtnv__uabcy = python_build_replace_dicts(
            qlkuf__hjl, ylht__ifly, arr.dtype.categories)
        if len(ioeqx__nmd) == 0:
            return lambda arr, to_replace, value: arr.copy()
        btmcb__mam = []
        for xjbo__tgjq in arr.dtype.categories:
            if xjbo__tgjq in ioeqx__nmd:
                aah__bqyh = ioeqx__nmd[xjbo__tgjq]
                if aah__bqyh != xjbo__tgjq:
                    btmcb__mam.append(aah__bqyh)
            else:
                btmcb__mam.append(xjbo__tgjq)
        lvuy__abrxs = bodo.utils.utils.create_categorical_type(btmcb__mam,
            arr.dtype.data.data, aurj__azc)
        vpo__koza = MetaType(tuple(lvuy__abrxs))

        def impl_dtype(arr, to_replace, value):
            eigq__okf = init_cat_dtype(bodo.utils.conversion.
                index_from_array(lvuy__abrxs), aurj__azc, None, vpo__koza)
            vkaip__fkwd = alloc_categorical_array(len(arr.codes), eigq__okf)
            reassign_codes(vkaip__fkwd.codes, arr.codes, codes_map_arr)
            return vkaip__fkwd
        return impl_dtype
    nwa__wxrdb = arr.dtype.elem_type
    if nwa__wxrdb == types.unicode_type:

        def impl_str(arr, to_replace, value):
            categories = arr.dtype.categories
            tnxhk__dqiys, codes_map_arr, mypcc__uvizj = build_replace_dicts(
                to_replace, value, categories.values)
            if len(tnxhk__dqiys) == 0:
                return init_categorical_array(arr.codes.copy().astype(np.
                    int64), init_cat_dtype(categories.copy(), aurj__azc,
                    None, None))
            n = len(categories)
            lvuy__abrxs = bodo.libs.str_arr_ext.pre_alloc_string_array(n -
                mypcc__uvizj, -1)
            diru__ehr = 0
            for pwp__ebxr in range(n):
                zla__qmx = categories[pwp__ebxr]
                if zla__qmx in tnxhk__dqiys:
                    slrzl__rjoa = tnxhk__dqiys[zla__qmx]
                    if slrzl__rjoa != zla__qmx:
                        lvuy__abrxs[diru__ehr] = slrzl__rjoa
                        diru__ehr += 1
                else:
                    lvuy__abrxs[diru__ehr] = zla__qmx
                    diru__ehr += 1
            vkaip__fkwd = alloc_categorical_array(len(arr.codes),
                init_cat_dtype(bodo.utils.conversion.index_from_array(
                lvuy__abrxs), aurj__azc, None, None))
            reassign_codes(vkaip__fkwd.codes, arr.codes, codes_map_arr)
            return vkaip__fkwd
        return impl_str
    ohxea__itjf = dtype_to_array_type(nwa__wxrdb)

    def impl(arr, to_replace, value):
        categories = arr.dtype.categories
        tnxhk__dqiys, codes_map_arr, mypcc__uvizj = build_replace_dicts(
            to_replace, value, categories.values)
        if len(tnxhk__dqiys) == 0:
            return init_categorical_array(arr.codes.copy().astype(np.int64),
                init_cat_dtype(categories.copy(), aurj__azc, None, None))
        n = len(categories)
        lvuy__abrxs = bodo.utils.utils.alloc_type(n - mypcc__uvizj,
            ohxea__itjf, None)
        diru__ehr = 0
        for wsoxq__mcoa in range(n):
            zla__qmx = categories[wsoxq__mcoa]
            if zla__qmx in tnxhk__dqiys:
                slrzl__rjoa = tnxhk__dqiys[zla__qmx]
                if slrzl__rjoa != zla__qmx:
                    lvuy__abrxs[diru__ehr] = slrzl__rjoa
                    diru__ehr += 1
            else:
                lvuy__abrxs[diru__ehr] = zla__qmx
                diru__ehr += 1
        vkaip__fkwd = alloc_categorical_array(len(arr.codes),
            init_cat_dtype(bodo.utils.conversion.index_from_array(
            lvuy__abrxs), aurj__azc, None, None))
        reassign_codes(vkaip__fkwd.codes, arr.codes, codes_map_arr)
        return vkaip__fkwd
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
    iagy__oohf = dict()
    kmyy__eash = 0
    for wsoxq__mcoa in range(len(vals)):
        val = vals[wsoxq__mcoa]
        if val in iagy__oohf:
            continue
        iagy__oohf[val] = kmyy__eash
        kmyy__eash += 1
    return iagy__oohf


@register_jitable
def get_label_dict_from_categories_no_duplicates(vals):
    iagy__oohf = dict()
    for wsoxq__mcoa in range(len(vals)):
        val = vals[wsoxq__mcoa]
        iagy__oohf[val] = wsoxq__mcoa
    return iagy__oohf


@overload(pd.Categorical, no_unliteral=True)
def pd_categorical_overload(values, categories=None, ordered=None, dtype=
    None, fastpath=False):
    xhef__kpq = dict(fastpath=fastpath)
    zsnex__qcvud = dict(fastpath=False)
    check_unsupported_args('pd.Categorical', xhef__kpq, zsnex__qcvud)
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):

        def impl_dtype(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            data = bodo.utils.conversion.coerce_to_array(values)
            return bodo.utils.conversion.fix_arr_dtype(data, dtype)
        return impl_dtype
    if not is_overload_none(categories):
        npb__hnwev = get_overload_const(categories)
        if npb__hnwev is not NOT_CONSTANT and get_overload_const(ordered
            ) is not NOT_CONSTANT:
            if is_overload_none(ordered):
                cmiz__xcjgr = False
            else:
                cmiz__xcjgr = get_overload_const_bool(ordered)
            lst__hrm = pd.CategoricalDtype(pd.array(npb__hnwev), cmiz__xcjgr
                ).categories.array
            magew__ymhqg = MetaType(tuple(lst__hrm))

            def impl_cats_const(values, categories=None, ordered=None,
                dtype=None, fastpath=False):
                data = bodo.utils.conversion.coerce_to_array(values)
                eigq__okf = init_cat_dtype(bodo.utils.conversion.
                    index_from_array(lst__hrm), cmiz__xcjgr, None, magew__ymhqg
                    )
                return bodo.utils.conversion.fix_arr_dtype(data, eigq__okf)
            return impl_cats_const

        def impl_cats(values, categories=None, ordered=None, dtype=None,
            fastpath=False):
            ordered = bodo.utils.conversion.false_if_none(ordered)
            data = bodo.utils.conversion.coerce_to_array(values)
            kiznh__bspb = bodo.utils.conversion.convert_to_index(categories)
            cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                kiznh__bspb, ordered, None, None)
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
            ckl__phozc = arr.codes[ind]
            return arr.dtype.categories[max(ckl__phozc, 0)]
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
    for wsoxq__mcoa in range(len(arr1)):
        if arr1[wsoxq__mcoa] != arr2[wsoxq__mcoa]:
            return False
    return True


@overload(operator.setitem, no_unliteral=True)
def categorical_array_setitem(arr, ind, val):
    if not isinstance(arr, CategoricalArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    ziv__mlm = is_scalar_type(val) and is_common_scalar_dtype([types.
        unliteral(val), arr.dtype.elem_type]) and not (isinstance(arr.dtype
        .elem_type, types.Integer) and isinstance(val, types.Float))
    wjdqk__dee = not isinstance(val, CategoricalArrayType
        ) and is_iterable_type(val) and is_common_scalar_dtype([val.dtype,
        arr.dtype.elem_type]) and not (isinstance(arr.dtype.elem_type,
        types.Integer) and isinstance(val.dtype, types.Float))
    wwpo__ztyrw = categorical_arrs_match(arr, val)
    kuq__kou = (
        f"setitem for CategoricalArrayType of dtype {arr.dtype} with indexing type {ind} received an incorrect 'value' type {val}."
        )
    mou__swtwa = (
        'Cannot set a Categorical with another, without identical categories')
    if isinstance(ind, types.Integer):
        if not ziv__mlm:
            raise BodoError(kuq__kou)

        def impl_scalar(arr, ind, val):
            if val not in arr.dtype.categories:
                raise ValueError(
                    'Cannot setitem on a Categorical with a new category, set the categories first'
                    )
            ckl__phozc = arr.dtype.categories.get_loc(val)
            arr.codes[ind] = ckl__phozc
        return impl_scalar
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        if not (ziv__mlm or wjdqk__dee or wwpo__ztyrw !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(kuq__kou)
        if wwpo__ztyrw == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(mou__swtwa)
        if ziv__mlm:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                tkkqi__hflpl = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for pwp__ebxr in range(n):
                    arr.codes[ind[pwp__ebxr]] = tkkqi__hflpl
            return impl_scalar
        if wwpo__ztyrw == CategoricalMatchingValues.DO_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                n = len(val.codes)
                for wsoxq__mcoa in range(n):
                    arr.codes[ind[wsoxq__mcoa]] = val.codes[wsoxq__mcoa]
            return impl_arr_ind_mask
        if wwpo__ztyrw == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(mou__swtwa)
                n = len(val.codes)
                for wsoxq__mcoa in range(n):
                    arr.codes[ind[wsoxq__mcoa]] = val.codes[wsoxq__mcoa]
            return impl_arr_ind_mask
        if wjdqk__dee:

            def impl_arr_ind_mask_cat_values(arr, ind, val):
                n = len(val)
                categories = arr.dtype.categories
                for pwp__ebxr in range(n):
                    afvu__mrwp = bodo.utils.conversion.unbox_if_timestamp(val
                        [pwp__ebxr])
                    if afvu__mrwp not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    ckl__phozc = categories.get_loc(afvu__mrwp)
                    arr.codes[ind[pwp__ebxr]] = ckl__phozc
            return impl_arr_ind_mask_cat_values
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        if not (ziv__mlm or wjdqk__dee or wwpo__ztyrw !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(kuq__kou)
        if wwpo__ztyrw == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(mou__swtwa)
        if ziv__mlm:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                tkkqi__hflpl = arr.dtype.categories.get_loc(val)
                n = len(ind)
                for pwp__ebxr in range(n):
                    if ind[pwp__ebxr]:
                        arr.codes[pwp__ebxr] = tkkqi__hflpl
            return impl_scalar
        if wwpo__ztyrw == CategoricalMatchingValues.DO_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                n = len(ind)
                bgc__wbhiv = 0
                for wsoxq__mcoa in range(n):
                    if ind[wsoxq__mcoa]:
                        arr.codes[wsoxq__mcoa] = val.codes[bgc__wbhiv]
                        bgc__wbhiv += 1
            return impl_bool_ind_mask
        if wwpo__ztyrw == CategoricalMatchingValues.MAY_MATCH:

            def impl_bool_ind_mask(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(mou__swtwa)
                n = len(ind)
                bgc__wbhiv = 0
                for wsoxq__mcoa in range(n):
                    if ind[wsoxq__mcoa]:
                        arr.codes[wsoxq__mcoa] = val.codes[bgc__wbhiv]
                        bgc__wbhiv += 1
            return impl_bool_ind_mask
        if wjdqk__dee:

            def impl_bool_ind_mask_cat_values(arr, ind, val):
                n = len(ind)
                bgc__wbhiv = 0
                categories = arr.dtype.categories
                for pwp__ebxr in range(n):
                    if ind[pwp__ebxr]:
                        afvu__mrwp = bodo.utils.conversion.unbox_if_timestamp(
                            val[bgc__wbhiv])
                        if afvu__mrwp not in categories:
                            raise ValueError(
                                'Cannot setitem on a Categorical with a new category, set the categories first'
                                )
                        ckl__phozc = categories.get_loc(afvu__mrwp)
                        arr.codes[pwp__ebxr] = ckl__phozc
                        bgc__wbhiv += 1
            return impl_bool_ind_mask_cat_values
    if isinstance(ind, types.SliceType):
        if not (ziv__mlm or wjdqk__dee or wwpo__ztyrw !=
            CategoricalMatchingValues.DIFFERENT_TYPES):
            raise BodoError(kuq__kou)
        if wwpo__ztyrw == CategoricalMatchingValues.DONT_MATCH:
            raise BodoError(mou__swtwa)
        if ziv__mlm:

            def impl_scalar(arr, ind, val):
                if val not in arr.dtype.categories:
                    raise ValueError(
                        'Cannot setitem on a Categorical with a new category, set the categories first'
                        )
                tkkqi__hflpl = arr.dtype.categories.get_loc(val)
                zgr__hodb = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                for pwp__ebxr in range(zgr__hodb.start, zgr__hodb.stop,
                    zgr__hodb.step):
                    arr.codes[pwp__ebxr] = tkkqi__hflpl
            return impl_scalar
        if wwpo__ztyrw == CategoricalMatchingValues.DO_MATCH:

            def impl_arr(arr, ind, val):
                arr.codes[ind] = val.codes
            return impl_arr
        if wwpo__ztyrw == CategoricalMatchingValues.MAY_MATCH:

            def impl_arr(arr, ind, val):
                if not cat_dtype_equal(arr.dtype, val.dtype):
                    raise ValueError(mou__swtwa)
                arr.codes[ind] = val.codes
            return impl_arr
        if wjdqk__dee:

            def impl_slice_cat_values(arr, ind, val):
                categories = arr.dtype.categories
                zgr__hodb = numba.cpython.unicode._normalize_slice(ind, len
                    (arr))
                bgc__wbhiv = 0
                for pwp__ebxr in range(zgr__hodb.start, zgr__hodb.stop,
                    zgr__hodb.step):
                    afvu__mrwp = bodo.utils.conversion.unbox_if_timestamp(val
                        [bgc__wbhiv])
                    if afvu__mrwp not in categories:
                        raise ValueError(
                            'Cannot setitem on a Categorical with a new category, set the categories first'
                            )
                    ckl__phozc = categories.get_loc(afvu__mrwp)
                    arr.codes[pwp__ebxr] = ckl__phozc
                    bgc__wbhiv += 1
            return impl_slice_cat_values
    raise BodoError(
        f'setitem for CategoricalArrayType with indexing type {ind} not supported.'
        )
