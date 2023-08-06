import datetime
import operator
import warnings
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_constant
from numba.core.typing.templates import AttributeTemplate, signature
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
import bodo.hiframes
import bodo.utils.conversion
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_overload_const_func, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_udf_error_msg, get_udf_out_arr_type, get_val_type_maybe_str_literal, is_const_func_type, is_heterogeneous_tuple_type, is_iterable_type, is_overload_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_nan, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_none, is_overload_true, is_str_arr_type, parse_dtype, raise_bodo_error
from bodo.utils.utils import is_null_value
_dt_index_data_typ = types.Array(types.NPDatetime('ns'), 1, 'C')
_timedelta_index_data_typ = types.Array(types.NPTimedelta('ns'), 1, 'C')
iNaT = pd._libs.tslibs.iNaT
NaT = types.NPDatetime('ns')('NaT')
idx_cpy_arg_defaults = dict(deep=False, dtype=None, names=None)
idx_typ_to_format_str_map = dict()


@typeof_impl.register(pd.Index)
def typeof_pd_index(val, c):
    if val.inferred_type == 'string' or pd._libs.lib.infer_dtype(val, True
        ) == 'string':
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'bytes' or pd._libs.lib.infer_dtype(val, True
        ) == 'bytes':
        return BinaryIndexType(get_val_type_maybe_str_literal(val.name))
    if val.equals(pd.Index([])):
        return StringIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'date':
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))
    if val.inferred_type == 'integer' or pd._libs.lib.infer_dtype(val, True
        ) == 'integer':
        if isinstance(val.dtype, pd.core.arrays.integer._IntegerDtype):
            bsmkj__bcbw = val.dtype.numpy_dtype
            dtype = numba.np.numpy_support.from_dtype(bsmkj__bcbw)
        else:
            dtype = types.int64
        return NumericIndexType(dtype, get_val_type_maybe_str_literal(val.
            name), IntegerArrayType(dtype))
    if val.inferred_type == 'boolean' or pd._libs.lib.infer_dtype(val, True
        ) == 'boolean':
        return NumericIndexType(types.bool_, get_val_type_maybe_str_literal
            (val.name), boolean_array)
    raise NotImplementedError(f'unsupported pd.Index type {val}')


class DatetimeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.datetime64ns, 1, 'C'
            ) if data is None else data
        super(DatetimeIndexType, self).__init__(name=
            f'DatetimeIndex({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def tzval(self):
        return self.data.tz if isinstance(self.data, bodo.DatetimeArrayType
            ) else None

    def copy(self):
        return DatetimeIndexType(self.name_typ, self.data)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, bodo.hiframes.
            pd_timestamp_ext.PandasTimestampType(self.tzval))

    @property
    def pandas_type_name(self):
        return self.data.dtype.type_name

    @property
    def numpy_type_name(self):
        return str(self.data.dtype)


types.datetime_index = DatetimeIndexType()


@typeof_impl.register(pd.DatetimeIndex)
def typeof_datetime_index(val, c):
    if isinstance(val.dtype, pd.DatetimeTZDtype):
        return DatetimeIndexType(get_val_type_maybe_str_literal(val.name),
            DatetimeArrayType(val.tz))
    return DatetimeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(DatetimeIndexType)
class DatetimeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zqxbb__dam = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(_dt_index_data_typ.dtype, types.int64))]
        super(DatetimeIndexModel, self).__init__(dmm, fe_type, zqxbb__dam)


make_attribute_wrapper(DatetimeIndexType, 'data', '_data')
make_attribute_wrapper(DatetimeIndexType, 'name', '_name')
make_attribute_wrapper(DatetimeIndexType, 'dict', '_dict')


@overload_method(DatetimeIndexType, 'copy', no_unliteral=True)
def overload_datetime_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    praj__uikjl = dict(deep=deep, dtype=dtype, names=names)
    pyn__hdgii = idx_typ_to_format_str_map[DatetimeIndexType].format('copy()')
    check_unsupported_args('copy', praj__uikjl, idx_cpy_arg_defaults,
        fn_str=pyn__hdgii, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_datetime_index(A._data.
                copy(), A._name)
    return impl


@box(DatetimeIndexType)
def box_dt_index(typ, val, c):
    dgt__ygbwa = c.context.insert_const_string(c.builder.module, 'pandas')
    qal__zov = c.pyapi.import_module_noblock(dgt__ygbwa)
    dzdxw__xlt = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, dzdxw__xlt.data)
    htv__sej = c.pyapi.from_native_value(typ.data, dzdxw__xlt.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, dzdxw__xlt.name)
    ldf__kwktb = c.pyapi.from_native_value(typ.name_typ, dzdxw__xlt.name, c
        .env_manager)
    args = c.pyapi.tuple_pack([htv__sej])
    npo__ufzy = c.pyapi.object_getattr_string(qal__zov, 'DatetimeIndex')
    kws = c.pyapi.dict_pack([('name', ldf__kwktb)])
    tfqb__cpbi = c.pyapi.call(npo__ufzy, args, kws)
    c.pyapi.decref(htv__sej)
    c.pyapi.decref(ldf__kwktb)
    c.pyapi.decref(qal__zov)
    c.pyapi.decref(npo__ufzy)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return tfqb__cpbi


@unbox(DatetimeIndexType)
def unbox_datetime_index(typ, val, c):
    if isinstance(typ.data, DatetimeArrayType):
        qrox__vnh = c.pyapi.object_getattr_string(val, 'array')
    else:
        qrox__vnh = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, qrox__vnh).value
    ldf__kwktb = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, ldf__kwktb).value
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rxl__bsb.data = data
    rxl__bsb.name = name
    dtype = _dt_index_data_typ.dtype
    zdm__yeznr, svj__fxxg = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    rxl__bsb.dict = svj__fxxg
    c.pyapi.decref(qrox__vnh)
    c.pyapi.decref(ldf__kwktb)
    return NativeValue(rxl__bsb._getvalue())


@intrinsic
def init_datetime_index(typingctx, data, name):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        xdjx__kidrp, cato__uabrz = args
        dzdxw__xlt = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        dzdxw__xlt.data = xdjx__kidrp
        dzdxw__xlt.name = cato__uabrz
        context.nrt.incref(builder, signature.args[0], xdjx__kidrp)
        context.nrt.incref(builder, signature.args[1], cato__uabrz)
        dtype = _dt_index_data_typ.dtype
        dzdxw__xlt.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return dzdxw__xlt._getvalue()
    zqa__dicdh = DatetimeIndexType(name, data)
    sig = signature(zqa__dicdh, data, name)
    return sig, codegen


def init_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) >= 1 and not kws
    muck__rgar = args[0]
    if equiv_set.has_shape(muck__rgar):
        return ArrayAnalysis.AnalyzeResult(shape=muck__rgar, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_datetime_index
    ) = init_index_equiv


def gen_dti_field_impl(field):
    csxb__cig = 'def impl(dti):\n'
    csxb__cig += '    numba.parfors.parfor.init_prange()\n'
    csxb__cig += '    A = bodo.hiframes.pd_index_ext.get_index_data(dti)\n'
    csxb__cig += '    name = bodo.hiframes.pd_index_ext.get_index_name(dti)\n'
    csxb__cig += '    n = len(A)\n'
    csxb__cig += '    S = np.empty(n, np.int64)\n'
    csxb__cig += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    csxb__cig += '        val = A[i]\n'
    csxb__cig += '        ts = bodo.utils.conversion.box_if_dt64(val)\n'
    if field in ['weekday']:
        csxb__cig += '        S[i] = ts.' + field + '()\n'
    else:
        csxb__cig += '        S[i] = ts.' + field + '\n'
    csxb__cig += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    zxve__rey = {}
    exec(csxb__cig, {'numba': numba, 'np': np, 'bodo': bodo}, zxve__rey)
    impl = zxve__rey['impl']
    return impl


def _install_dti_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        if field in ['is_leap_year']:
            continue
        impl = gen_dti_field_impl(field)
        overload_attribute(DatetimeIndexType, field)(lambda dti: impl)


_install_dti_date_fields()


@overload_attribute(DatetimeIndexType, 'is_leap_year')
def overload_datetime_index_is_leap_year(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        haa__kchia = len(A)
        S = np.empty(haa__kchia, np.bool_)
        for i in numba.parfors.parfor.internal_prange(haa__kchia):
            val = A[i]
            tao__rjrd = bodo.utils.conversion.box_if_dt64(val)
            S[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(tao__rjrd.year)
        return S
    return impl


@overload_attribute(DatetimeIndexType, 'date')
def overload_datetime_index_date(dti):

    def impl(dti):
        numba.parfors.parfor.init_prange()
        A = bodo.hiframes.pd_index_ext.get_index_data(dti)
        haa__kchia = len(A)
        S = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            haa__kchia)
        for i in numba.parfors.parfor.internal_prange(haa__kchia):
            val = A[i]
            tao__rjrd = bodo.utils.conversion.box_if_dt64(val)
            S[i] = datetime.date(tao__rjrd.year, tao__rjrd.month, tao__rjrd.day
                )
        return S
    return impl


@numba.njit(no_cpython_wrapper=True)
def _dti_val_finalize(s, count):
    if not count:
        s = iNaT
    return bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(s)


@numba.njit(no_cpython_wrapper=True)
def _tdi_val_finalize(s, count):
    return pd.Timedelta('nan') if not count else pd.Timedelta(s)


@overload_method(DatetimeIndexType, 'min', no_unliteral=True)
def overload_datetime_index_min(dti, axis=None, skipna=True):
    rdv__ubcq = dict(axis=axis, skipna=skipna)
    hnt__gtcv = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.min', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.min()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        itm__nhbe = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_max_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(itm__nhbe)):
            if not bodo.libs.array_kernels.isna(itm__nhbe, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(itm__nhbe
                    [i])
                s = min(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'max', no_unliteral=True)
def overload_datetime_index_max(dti, axis=None, skipna=True):
    rdv__ubcq = dict(axis=axis, skipna=skipna)
    hnt__gtcv = dict(axis=None, skipna=True)
    check_unsupported_args('DatetimeIndex.max', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dti,
        'Index.max()')

    def impl(dti, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        itm__nhbe = bodo.hiframes.pd_index_ext.get_index_data(dti)
        s = numba.cpython.builtins.get_type_min_value(numba.core.types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(len(itm__nhbe)):
            if not bodo.libs.array_kernels.isna(itm__nhbe, i):
                val = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(itm__nhbe
                    [i])
                s = max(s, val)
                count += 1
        return bodo.hiframes.pd_index_ext._dti_val_finalize(s, count)
    return impl


@overload_method(DatetimeIndexType, 'tz_convert', no_unliteral=True)
def overload_pd_datetime_tz_convert(A, tz):

    def impl(A, tz):
        return init_datetime_index(A._data.tz_convert(tz), A._name)
    return impl


@infer_getattr
class DatetimeIndexAttribute(AttributeTemplate):
    key = DatetimeIndexType

    def resolve_values(self, ary):
        return _dt_index_data_typ


@overload(pd.DatetimeIndex, no_unliteral=True)
def pd_datetimeindex_overload(data=None, freq=None, tz=None, normalize=
    False, closed=None, ambiguous='raise', dayfirst=False, yearfirst=False,
    dtype=None, copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.DatetimeIndex() expected')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'pandas.DatetimeIndex()')
    rdv__ubcq = dict(freq=freq, tz=tz, normalize=normalize, closed=closed,
        ambiguous=ambiguous, dayfirst=dayfirst, yearfirst=yearfirst, dtype=
        dtype, copy=copy)
    hnt__gtcv = dict(freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False)
    check_unsupported_args('pandas.DatetimeIndex', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')

    def f(data=None, freq=None, tz=None, normalize=False, closed=None,
        ambiguous='raise', dayfirst=False, yearfirst=False, dtype=None,
        copy=False, name=None):
        ngmp__lipdl = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_dt64ns(ngmp__lipdl)
        return bodo.hiframes.pd_index_ext.init_datetime_index(S, name)
    return f


def overload_sub_operator_datetime_index(lhs, rhs):
    if isinstance(lhs, DatetimeIndexType
        ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        iaibx__hrrf = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            itm__nhbe = bodo.hiframes.pd_index_ext.get_index_data(lhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(lhs)
            haa__kchia = len(itm__nhbe)
            S = np.empty(haa__kchia, iaibx__hrrf)
            npogg__both = rhs.value
            for i in numba.parfors.parfor.internal_prange(haa__kchia):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    itm__nhbe[i]) - npogg__both)
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl
    if isinstance(rhs, DatetimeIndexType
        ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        iaibx__hrrf = np.dtype('timedelta64[ns]')

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            itm__nhbe = bodo.hiframes.pd_index_ext.get_index_data(rhs)
            name = bodo.hiframes.pd_index_ext.get_index_name(rhs)
            haa__kchia = len(itm__nhbe)
            S = np.empty(haa__kchia, iaibx__hrrf)
            npogg__both = lhs.value
            for i in numba.parfors.parfor.internal_prange(haa__kchia):
                S[i] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                    npogg__both - bodo.hiframes.pd_timestamp_ext.
                    dt64_to_integer(itm__nhbe[i]))
            return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
        return impl


def gen_dti_str_binop_impl(op, is_lhs_dti):
    zlt__dshiy = numba.core.utils.OPERATORS_TO_BUILTINS[op]
    csxb__cig = 'def impl(lhs, rhs):\n'
    if is_lhs_dti:
        csxb__cig += '  dt_index, _str = lhs, rhs\n'
        azp__wgck = 'arr[i] {} other'.format(zlt__dshiy)
    else:
        csxb__cig += '  dt_index, _str = rhs, lhs\n'
        azp__wgck = 'other {} arr[i]'.format(zlt__dshiy)
    csxb__cig += (
        '  arr = bodo.hiframes.pd_index_ext.get_index_data(dt_index)\n')
    csxb__cig += '  l = len(arr)\n'
    csxb__cig += (
        '  other = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(_str)\n')
    csxb__cig += '  S = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    csxb__cig += '  for i in numba.parfors.parfor.internal_prange(l):\n'
    csxb__cig += '    S[i] = {}\n'.format(azp__wgck)
    csxb__cig += '  return S\n'
    zxve__rey = {}
    exec(csxb__cig, {'bodo': bodo, 'numba': numba, 'np': np}, zxve__rey)
    impl = zxve__rey['impl']
    return impl


def overload_binop_dti_str(op):

    def overload_impl(lhs, rhs):
        if isinstance(lhs, DatetimeIndexType) and types.unliteral(rhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, True)
        if isinstance(rhs, DatetimeIndexType) and types.unliteral(lhs
            ) == string_type:
            return gen_dti_str_binop_impl(op, False)
    return overload_impl


@overload(pd.Index, inline='always', no_unliteral=True)
def pd_index_overload(data=None, dtype=None, copy=False, name=None,
    tupleize_cols=True):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'pandas.Index()')
    data = types.unliteral(data) if not isinstance(data, types.LiteralList
        ) else data
    if not is_overload_none(dtype):
        siyl__giyd = parse_dtype(dtype, 'pandas.Index')
        ycmt__veod = False
    else:
        siyl__giyd = getattr(data, 'dtype', None)
        ycmt__veod = True
    if isinstance(siyl__giyd, types.misc.PyObject):
        raise BodoError(
            "pd.Index() object 'dtype' is not specific enough for typing. Please provide a more exact type (e.g. str)."
            )
    if isinstance(data, RangeIndexType):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.RangeIndex(data, name=name)
    elif isinstance(data, DatetimeIndexType) or siyl__giyd == types.NPDatetime(
        'ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.DatetimeIndex(data, name=name)
    elif isinstance(data, TimedeltaIndexType
        ) or siyl__giyd == types.NPTimedelta('ns'):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return pd.TimedeltaIndex(data, name=name)
    elif is_heterogeneous_tuple_type(data):

        def impl(data=None, dtype=None, copy=False, name=None,
            tupleize_cols=True):
            return bodo.hiframes.pd_index_ext.init_heter_index(data, name)
        return impl
    elif bodo.utils.utils.is_array_typ(data, False) or isinstance(data, (
        SeriesType, types.List, types.UniTuple)):
        if isinstance(siyl__giyd, (types.Integer, types.Float, types.Boolean)):
            if ycmt__veod:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    ngmp__lipdl = bodo.utils.conversion.coerce_to_array(data)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        ngmp__lipdl, name)
            else:

                def impl(data=None, dtype=None, copy=False, name=None,
                    tupleize_cols=True):
                    ngmp__lipdl = bodo.utils.conversion.coerce_to_array(data)
                    byyjm__gjal = bodo.utils.conversion.fix_arr_dtype(
                        ngmp__lipdl, siyl__giyd)
                    return bodo.hiframes.pd_index_ext.init_numeric_index(
                        byyjm__gjal, name)
        elif siyl__giyd in [types.string, bytes_type]:

            def impl(data=None, dtype=None, copy=False, name=None,
                tupleize_cols=True):
                return bodo.hiframes.pd_index_ext.init_binary_str_index(bodo
                    .utils.conversion.coerce_to_array(data), name)
        else:
            raise BodoError(
                'pd.Index(): provided array is of unsupported type.')
    elif is_overload_none(data):
        raise BodoError(
            'data argument in pd.Index() is invalid: None or scalar is not acceptable'
            )
    else:
        raise BodoError(
            f'pd.Index(): the provided argument type {data} is not supported')
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_datetime_index_getitem(dti, ind):
    if isinstance(dti, DatetimeIndexType):
        if isinstance(ind, types.Integer):

            def impl(dti, ind):
                hwye__otxq = bodo.hiframes.pd_index_ext.get_index_data(dti)
                val = hwye__otxq[ind]
                return bodo.utils.conversion.box_if_dt64(val)
            return impl
        else:

            def impl(dti, ind):
                hwye__otxq = bodo.hiframes.pd_index_ext.get_index_data(dti)
                name = bodo.hiframes.pd_index_ext.get_index_name(dti)
                pbe__kuy = hwye__otxq[ind]
                return bodo.hiframes.pd_index_ext.init_datetime_index(pbe__kuy,
                    name)
            return impl


@overload(operator.getitem, no_unliteral=True)
def overload_timedelta_index_getitem(I, ind):
    if not isinstance(I, TimedeltaIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            not__pebws = bodo.hiframes.pd_index_ext.get_index_data(I)
            return pd.Timedelta(not__pebws[ind])
        return impl

    def impl(I, ind):
        not__pebws = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        pbe__kuy = not__pebws[ind]
        return bodo.hiframes.pd_index_ext.init_timedelta_index(pbe__kuy, name)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_categorical_index_getitem(I, ind):
    if not isinstance(I, CategoricalIndexType):
        return
    if isinstance(ind, types.Integer):

        def impl(I, ind):
            rfd__mxgvr = bodo.hiframes.pd_index_ext.get_index_data(I)
            val = rfd__mxgvr[ind]
            return val
        return impl
    if isinstance(ind, types.SliceType):

        def impl(I, ind):
            rfd__mxgvr = bodo.hiframes.pd_index_ext.get_index_data(I)
            name = bodo.hiframes.pd_index_ext.get_index_name(I)
            pbe__kuy = rfd__mxgvr[ind]
            return bodo.hiframes.pd_index_ext.init_categorical_index(pbe__kuy,
                name)
        return impl
    raise BodoError(
        f'pd.CategoricalIndex.__getitem__: unsupported index type {ind}')


@numba.njit(no_cpython_wrapper=True)
def validate_endpoints(closed):
    gcaoc__msci = False
    jsj__ceoo = False
    if closed is None:
        gcaoc__msci = True
        jsj__ceoo = True
    elif closed == 'left':
        gcaoc__msci = True
    elif closed == 'right':
        jsj__ceoo = True
    else:
        raise ValueError("Closed has to be either 'left', 'right' or None")
    return gcaoc__msci, jsj__ceoo


@numba.njit(no_cpython_wrapper=True)
def to_offset_value(freq):
    if freq is None:
        return None
    with numba.objmode(r='int64'):
        r = pd.tseries.frequencies.to_offset(freq).nanos
    return r


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _dummy_convert_none_to_int(val):
    if is_overload_none(val):

        def impl(val):
            return 0
        return impl
    if isinstance(val, types.Optional):

        def impl(val):
            if val is None:
                return 0
            return bodo.utils.indexing.unoptional(val)
        return impl
    return lambda val: val


@overload(pd.date_range, inline='always')
def pd_date_range_overload(start=None, end=None, periods=None, freq=None,
    tz=None, normalize=False, name=None, closed=None):
    rdv__ubcq = dict(tz=tz, normalize=normalize, closed=closed)
    hnt__gtcv = dict(tz=None, normalize=False, closed=None)
    check_unsupported_args('pandas.date_range', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='General')
    if not is_overload_none(tz):
        raise_bodo_error('pd.date_range(): tz argument not supported yet')
    faz__iisl = ''
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
        faz__iisl = "  freq = 'D'\n"
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise_bodo_error(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )
    csxb__cig = """def f(start=None, end=None, periods=None, freq=None, tz=None, normalize=False, name=None, closed=None):
"""
    csxb__cig += faz__iisl
    if is_overload_none(start):
        csxb__cig += "  start_t = pd.Timestamp('1800-01-03')\n"
    else:
        csxb__cig += '  start_t = pd.Timestamp(start)\n'
    if is_overload_none(end):
        csxb__cig += "  end_t = pd.Timestamp('1800-01-03')\n"
    else:
        csxb__cig += '  end_t = pd.Timestamp(end)\n'
    if not is_overload_none(freq):
        csxb__cig += (
            '  stride = bodo.hiframes.pd_index_ext.to_offset_value(freq)\n')
        if is_overload_none(periods):
            csxb__cig += '  b = start_t.value\n'
            csxb__cig += (
                '  e = b + (end_t.value - b) // stride * stride + stride // 2 + 1\n'
                )
        elif not is_overload_none(start):
            csxb__cig += '  b = start_t.value\n'
            csxb__cig += '  addend = np.int64(periods) * np.int64(stride)\n'
            csxb__cig += '  e = np.int64(b) + addend\n'
        elif not is_overload_none(end):
            csxb__cig += '  e = end_t.value + stride\n'
            csxb__cig += '  addend = np.int64(periods) * np.int64(-stride)\n'
            csxb__cig += '  b = np.int64(e) + addend\n'
        else:
            raise_bodo_error(
                "at least 'start' or 'end' should be specified if a 'period' is given."
                )
        csxb__cig += '  arr = np.arange(b, e, stride, np.int64)\n'
    else:
        csxb__cig += '  delta = end_t.value - start_t.value\n'
        csxb__cig += '  step = delta / (periods - 1)\n'
        csxb__cig += '  arr1 = np.arange(0, periods, 1, np.float64)\n'
        csxb__cig += '  arr1 *= step\n'
        csxb__cig += '  arr1 += start_t.value\n'
        csxb__cig += '  arr = arr1.astype(np.int64)\n'
        csxb__cig += '  arr[-1] = end_t.value\n'
    csxb__cig += '  A = bodo.utils.conversion.convert_to_dt64ns(arr)\n'
    csxb__cig += (
        '  return bodo.hiframes.pd_index_ext.init_datetime_index(A, name)\n')
    zxve__rey = {}
    exec(csxb__cig, {'bodo': bodo, 'np': np, 'pd': pd}, zxve__rey)
    f = zxve__rey['f']
    return f


@overload(pd.timedelta_range, no_unliteral=True)
def pd_timedelta_range_overload(start=None, end=None, periods=None, freq=
    None, name=None, closed=None):
    if is_overload_none(freq) and any(is_overload_none(t) for t in (start,
        end, periods)):
        freq = 'D'
    if sum(not is_overload_none(t) for t in (start, end, periods, freq)) != 3:
        raise BodoError(
            'Of the four parameters: start, end, periods, and freq, exactly three must be specified'
            )

    def f(start=None, end=None, periods=None, freq=None, name=None, closed=None
        ):
        if freq is None and (start is None or end is None or periods is None):
            freq = 'D'
        freq = bodo.hiframes.pd_index_ext.to_offset_value(freq)
        gou__nega = pd.Timedelta('1 day')
        if start is not None:
            gou__nega = pd.Timedelta(start)
        pgczh__enhd = pd.Timedelta('1 day')
        if end is not None:
            pgczh__enhd = pd.Timedelta(end)
        if start is None and end is None and closed is not None:
            raise ValueError(
                'Closed has to be None if not both of start and end are defined'
                )
        gcaoc__msci, jsj__ceoo = bodo.hiframes.pd_index_ext.validate_endpoints(
            closed)
        if freq is not None:
            zjlcy__qmfdk = _dummy_convert_none_to_int(freq)
            if periods is None:
                b = gou__nega.value
                hldb__kvg = b + (pgczh__enhd.value - b
                    ) // zjlcy__qmfdk * zjlcy__qmfdk + zjlcy__qmfdk // 2 + 1
            elif start is not None:
                periods = _dummy_convert_none_to_int(periods)
                b = gou__nega.value
                ifb__xvjib = np.int64(periods) * np.int64(zjlcy__qmfdk)
                hldb__kvg = np.int64(b) + ifb__xvjib
            elif end is not None:
                periods = _dummy_convert_none_to_int(periods)
                hldb__kvg = pgczh__enhd.value + zjlcy__qmfdk
                ifb__xvjib = np.int64(periods) * np.int64(-zjlcy__qmfdk)
                b = np.int64(hldb__kvg) + ifb__xvjib
            else:
                raise ValueError(
                    "at least 'start' or 'end' should be specified if a 'period' is given."
                    )
            req__chq = np.arange(b, hldb__kvg, zjlcy__qmfdk, np.int64)
        else:
            periods = _dummy_convert_none_to_int(periods)
            dlrit__vcrn = pgczh__enhd.value - gou__nega.value
            step = dlrit__vcrn / (periods - 1)
            mnu__tupu = np.arange(0, periods, 1, np.float64)
            mnu__tupu *= step
            mnu__tupu += gou__nega.value
            req__chq = mnu__tupu.astype(np.int64)
            req__chq[-1] = pgczh__enhd.value
        if not gcaoc__msci and len(req__chq) and req__chq[0
            ] == gou__nega.value:
            req__chq = req__chq[1:]
        if not jsj__ceoo and len(req__chq) and req__chq[-1
            ] == pgczh__enhd.value:
            req__chq = req__chq[:-1]
        S = bodo.utils.conversion.convert_to_dt64ns(req__chq)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return f


@overload_method(DatetimeIndexType, 'isocalendar', inline='always',
    no_unliteral=True)
def overload_pd_timestamp_isocalendar(idx):
    ooae__hzdc = ColNamesMetaType(('year', 'week', 'day'))

    def impl(idx):
        A = bodo.hiframes.pd_index_ext.get_index_data(idx)
        numba.parfors.parfor.init_prange()
        haa__kchia = len(A)
        xtv__jkd = bodo.libs.int_arr_ext.alloc_int_array(haa__kchia, np.uint32)
        nbtb__cagh = bodo.libs.int_arr_ext.alloc_int_array(haa__kchia, np.
            uint32)
        ztgh__jgio = bodo.libs.int_arr_ext.alloc_int_array(haa__kchia, np.
            uint32)
        for i in numba.parfors.parfor.internal_prange(haa__kchia):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(xtv__jkd, i)
                bodo.libs.array_kernels.setna(nbtb__cagh, i)
                bodo.libs.array_kernels.setna(ztgh__jgio, i)
                continue
            xtv__jkd[i], nbtb__cagh[i], ztgh__jgio[i
                ] = bodo.utils.conversion.box_if_dt64(A[i]).isocalendar()
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((xtv__jkd,
            nbtb__cagh, ztgh__jgio), idx, ooae__hzdc)
    return impl


class TimedeltaIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = types.Array(bodo.timedelta64ns, 1, 'C'
            ) if data is None else data
        super(TimedeltaIndexType, self).__init__(name=
            f'TimedeltaIndexType({name_typ}, {self.data})')
    ndim = 1

    def copy(self):
        return TimedeltaIndexType(self.name_typ)

    @property
    def dtype(self):
        return types.NPTimedelta('ns')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.name_typ, self.data

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, bodo.pd_timedelta_type
            )

    @property
    def pandas_type_name(self):
        return 'timedelta'

    @property
    def numpy_type_name(self):
        return 'timedelta64[ns]'


timedelta_index = TimedeltaIndexType()
types.timedelta_index = timedelta_index


@register_model(TimedeltaIndexType)
class TimedeltaIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zqxbb__dam = [('data', _timedelta_index_data_typ), ('name', fe_type
            .name_typ), ('dict', types.DictType(_timedelta_index_data_typ.
            dtype, types.int64))]
        super(TimedeltaIndexTypeModel, self).__init__(dmm, fe_type, zqxbb__dam)


@typeof_impl.register(pd.TimedeltaIndex)
def typeof_timedelta_index(val, c):
    return TimedeltaIndexType(get_val_type_maybe_str_literal(val.name))


@box(TimedeltaIndexType)
def box_timedelta_index(typ, val, c):
    dgt__ygbwa = c.context.insert_const_string(c.builder.module, 'pandas')
    qal__zov = c.pyapi.import_module_noblock(dgt__ygbwa)
    timedelta_index = numba.core.cgutils.create_struct_proxy(typ)(c.context,
        c.builder, val)
    c.context.nrt.incref(c.builder, _timedelta_index_data_typ,
        timedelta_index.data)
    htv__sej = c.pyapi.from_native_value(_timedelta_index_data_typ,
        timedelta_index.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, timedelta_index.name)
    ldf__kwktb = c.pyapi.from_native_value(typ.name_typ, timedelta_index.
        name, c.env_manager)
    args = c.pyapi.tuple_pack([htv__sej])
    kws = c.pyapi.dict_pack([('name', ldf__kwktb)])
    npo__ufzy = c.pyapi.object_getattr_string(qal__zov, 'TimedeltaIndex')
    tfqb__cpbi = c.pyapi.call(npo__ufzy, args, kws)
    c.pyapi.decref(htv__sej)
    c.pyapi.decref(ldf__kwktb)
    c.pyapi.decref(qal__zov)
    c.pyapi.decref(npo__ufzy)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return tfqb__cpbi


@unbox(TimedeltaIndexType)
def unbox_timedelta_index(typ, val, c):
    fxh__wroi = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(_timedelta_index_data_typ, fxh__wroi).value
    ldf__kwktb = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, ldf__kwktb).value
    c.pyapi.decref(fxh__wroi)
    c.pyapi.decref(ldf__kwktb)
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rxl__bsb.data = data
    rxl__bsb.name = name
    dtype = _timedelta_index_data_typ.dtype
    zdm__yeznr, svj__fxxg = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    rxl__bsb.dict = svj__fxxg
    return NativeValue(rxl__bsb._getvalue())


@intrinsic
def init_timedelta_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        xdjx__kidrp, cato__uabrz = args
        timedelta_index = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        timedelta_index.data = xdjx__kidrp
        timedelta_index.name = cato__uabrz
        context.nrt.incref(builder, signature.args[0], xdjx__kidrp)
        context.nrt.incref(builder, signature.args[1], cato__uabrz)
        dtype = _timedelta_index_data_typ.dtype
        timedelta_index.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(dtype, types.int64), types.DictType(
            dtype, types.int64)(), [])
        return timedelta_index._getvalue()
    zqa__dicdh = TimedeltaIndexType(name)
    sig = signature(zqa__dicdh, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_timedelta_index
    ) = init_index_equiv


@infer_getattr
class TimedeltaIndexAttribute(AttributeTemplate):
    key = TimedeltaIndexType

    def resolve_values(self, ary):
        return _timedelta_index_data_typ


make_attribute_wrapper(TimedeltaIndexType, 'data', '_data')
make_attribute_wrapper(TimedeltaIndexType, 'name', '_name')
make_attribute_wrapper(TimedeltaIndexType, 'dict', '_dict')


@overload_method(TimedeltaIndexType, 'copy', no_unliteral=True)
def overload_timedelta_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    praj__uikjl = dict(deep=deep, dtype=dtype, names=names)
    pyn__hdgii = idx_typ_to_format_str_map[TimedeltaIndexType].format('copy()')
    check_unsupported_args('TimedeltaIndex.copy', praj__uikjl,
        idx_cpy_arg_defaults, fn_str=pyn__hdgii, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_timedelta_index(A._data.
                copy(), A._name)
    return impl


@overload_method(TimedeltaIndexType, 'min', inline='always', no_unliteral=True)
def overload_timedelta_index_min(tdi, axis=None, skipna=True):
    rdv__ubcq = dict(axis=axis, skipna=skipna)
    hnt__gtcv = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.min', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        haa__kchia = len(data)
        ishf__epf = numba.cpython.builtins.get_type_max_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(haa__kchia):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            ishf__epf = min(ishf__epf, val)
        nvd__swo = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            ishf__epf)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(nvd__swo, count)
    return impl


@overload_method(TimedeltaIndexType, 'max', inline='always', no_unliteral=True)
def overload_timedelta_index_max(tdi, axis=None, skipna=True):
    rdv__ubcq = dict(axis=axis, skipna=skipna)
    hnt__gtcv = dict(axis=None, skipna=True)
    check_unsupported_args('TimedeltaIndex.max', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    if not is_overload_none(axis) or not is_overload_true(skipna):
        raise BodoError(
            'Index.min(): axis and skipna arguments not supported yet')

    def impl(tdi, axis=None, skipna=True):
        numba.parfors.parfor.init_prange()
        data = bodo.hiframes.pd_index_ext.get_index_data(tdi)
        haa__kchia = len(data)
        khfo__kaj = numba.cpython.builtins.get_type_min_value(numba.core.
            types.int64)
        count = 0
        for i in numba.parfors.parfor.internal_prange(haa__kchia):
            if bodo.libs.array_kernels.isna(data, i):
                continue
            val = (bodo.hiframes.datetime_timedelta_ext.
                cast_numpy_timedelta_to_int(data[i]))
            count += 1
            khfo__kaj = max(khfo__kaj, val)
        nvd__swo = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
            khfo__kaj)
        return bodo.hiframes.pd_index_ext._tdi_val_finalize(nvd__swo, count)
    return impl


def gen_tdi_field_impl(field):
    csxb__cig = 'def impl(tdi):\n'
    csxb__cig += '    numba.parfors.parfor.init_prange()\n'
    csxb__cig += '    A = bodo.hiframes.pd_index_ext.get_index_data(tdi)\n'
    csxb__cig += '    name = bodo.hiframes.pd_index_ext.get_index_name(tdi)\n'
    csxb__cig += '    n = len(A)\n'
    csxb__cig += '    S = np.empty(n, np.int64)\n'
    csxb__cig += '    for i in numba.parfors.parfor.internal_prange(n):\n'
    csxb__cig += (
        '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
        )
    if field == 'nanoseconds':
        csxb__cig += '        S[i] = td64 % 1000\n'
    elif field == 'microseconds':
        csxb__cig += '        S[i] = td64 // 1000 % 100000\n'
    elif field == 'seconds':
        csxb__cig += (
            '        S[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
    elif field == 'days':
        csxb__cig += '        S[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n'
    else:
        assert False, 'invalid timedelta field'
    csxb__cig += (
        '    return bodo.hiframes.pd_index_ext.init_numeric_index(S, name)\n')
    zxve__rey = {}
    exec(csxb__cig, {'numba': numba, 'np': np, 'bodo': bodo}, zxve__rey)
    impl = zxve__rey['impl']
    return impl


def _install_tdi_time_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        impl = gen_tdi_field_impl(field)
        overload_attribute(TimedeltaIndexType, field)(lambda tdi: impl)


_install_tdi_time_fields()


@overload(pd.TimedeltaIndex, no_unliteral=True)
def pd_timedelta_index_overload(data=None, unit=None, freq=None, dtype=None,
    copy=False, name=None):
    if is_overload_none(data):
        raise BodoError('data argument in pd.TimedeltaIndex() expected')
    rdv__ubcq = dict(unit=unit, freq=freq, dtype=dtype, copy=copy)
    hnt__gtcv = dict(unit=None, freq=None, dtype=None, copy=False)
    check_unsupported_args('pandas.TimedeltaIndex', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')

    def impl(data=None, unit=None, freq=None, dtype=None, copy=False, name=None
        ):
        ngmp__lipdl = bodo.utils.conversion.coerce_to_array(data)
        S = bodo.utils.conversion.convert_to_td64ns(ngmp__lipdl)
        return bodo.hiframes.pd_index_ext.init_timedelta_index(S, name)
    return impl


class RangeIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None):
        if name_typ is None:
            name_typ = types.none
        self.name_typ = name_typ
        super(RangeIndexType, self).__init__(name=f'RangeIndexType({name_typ})'
            )
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return RangeIndexType(self.name_typ)

    @property
    def iterator_type(self):
        return types.iterators.RangeIteratorType(types.int64)

    @property
    def dtype(self):
        return types.int64

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)

    def unify(self, typingctx, other):
        if isinstance(other, NumericIndexType):
            name_typ = self.name_typ.unify(typingctx, other.name_typ)
            if name_typ is None:
                name_typ = types.none
            return NumericIndexType(types.int64, name_typ)


@typeof_impl.register(pd.RangeIndex)
def typeof_pd_range_index(val, c):
    return RangeIndexType(get_val_type_maybe_str_literal(val.name))


@register_model(RangeIndexType)
class RangeIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zqxbb__dam = [('start', types.int64), ('stop', types.int64), (
            'step', types.int64), ('name', fe_type.name_typ)]
        super(RangeIndexModel, self).__init__(dmm, fe_type, zqxbb__dam)


make_attribute_wrapper(RangeIndexType, 'start', '_start')
make_attribute_wrapper(RangeIndexType, 'stop', '_stop')
make_attribute_wrapper(RangeIndexType, 'step', '_step')
make_attribute_wrapper(RangeIndexType, 'name', '_name')


@overload_method(RangeIndexType, 'copy', no_unliteral=True)
def overload_range_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    praj__uikjl = dict(deep=deep, dtype=dtype, names=names)
    pyn__hdgii = idx_typ_to_format_str_map[RangeIndexType].format('copy()')
    check_unsupported_args('RangeIndex.copy', praj__uikjl,
        idx_cpy_arg_defaults, fn_str=pyn__hdgii, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_range_index(A._start, A.
                _stop, A._step, A._name)
    return impl


@box(RangeIndexType)
def box_range_index(typ, val, c):
    dgt__ygbwa = c.context.insert_const_string(c.builder.module, 'pandas')
    akli__zdymk = c.pyapi.import_module_noblock(dgt__ygbwa)
    hgxci__tgvwq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    kdzag__psow = c.pyapi.from_native_value(types.int64, hgxci__tgvwq.start,
        c.env_manager)
    rztjn__lrzh = c.pyapi.from_native_value(types.int64, hgxci__tgvwq.stop,
        c.env_manager)
    fky__yfcod = c.pyapi.from_native_value(types.int64, hgxci__tgvwq.step,
        c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, hgxci__tgvwq.name)
    ldf__kwktb = c.pyapi.from_native_value(typ.name_typ, hgxci__tgvwq.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([kdzag__psow, rztjn__lrzh, fky__yfcod])
    kws = c.pyapi.dict_pack([('name', ldf__kwktb)])
    npo__ufzy = c.pyapi.object_getattr_string(akli__zdymk, 'RangeIndex')
    yfb__aacnr = c.pyapi.call(npo__ufzy, args, kws)
    c.pyapi.decref(kdzag__psow)
    c.pyapi.decref(rztjn__lrzh)
    c.pyapi.decref(fky__yfcod)
    c.pyapi.decref(ldf__kwktb)
    c.pyapi.decref(akli__zdymk)
    c.pyapi.decref(npo__ufzy)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return yfb__aacnr


@intrinsic
def init_range_index(typingctx, start, stop, step, name=None):
    name = types.none if name is None else name
    uks__wufv = is_overload_constant_int(step) and get_overload_const_int(step
        ) == 0

    def codegen(context, builder, signature, args):
        assert len(args) == 4
        if uks__wufv:
            raise_bodo_error('Step must not be zero')
        yrj__bozc = cgutils.is_scalar_zero(builder, args[2])
        dkxw__zoniv = context.get_python_api(builder)
        with builder.if_then(yrj__bozc):
            dkxw__zoniv.err_format('PyExc_ValueError', 'Step must not be zero')
            val = context.get_constant(types.int32, -1)
            builder.ret(val)
        hgxci__tgvwq = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        hgxci__tgvwq.start = args[0]
        hgxci__tgvwq.stop = args[1]
        hgxci__tgvwq.step = args[2]
        hgxci__tgvwq.name = args[3]
        context.nrt.incref(builder, signature.return_type.name_typ, args[3])
        return hgxci__tgvwq._getvalue()
    return RangeIndexType(name)(start, stop, step, name), codegen


def init_range_index_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    start, stop, step, fwa__yqkb = args
    if self.typemap[start.name] == types.IntegerLiteral(0) and self.typemap[
        step.name] == types.IntegerLiteral(1) and equiv_set.has_shape(stop):
        return ArrayAnalysis.AnalyzeResult(shape=stop, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_range_index
    ) = init_range_index_equiv


@unbox(RangeIndexType)
def unbox_range_index(typ, val, c):
    kdzag__psow = c.pyapi.object_getattr_string(val, 'start')
    start = c.pyapi.to_native_value(types.int64, kdzag__psow).value
    rztjn__lrzh = c.pyapi.object_getattr_string(val, 'stop')
    stop = c.pyapi.to_native_value(types.int64, rztjn__lrzh).value
    fky__yfcod = c.pyapi.object_getattr_string(val, 'step')
    step = c.pyapi.to_native_value(types.int64, fky__yfcod).value
    ldf__kwktb = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, ldf__kwktb).value
    c.pyapi.decref(kdzag__psow)
    c.pyapi.decref(rztjn__lrzh)
    c.pyapi.decref(fky__yfcod)
    c.pyapi.decref(ldf__kwktb)
    hgxci__tgvwq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hgxci__tgvwq.start = start
    hgxci__tgvwq.stop = stop
    hgxci__tgvwq.step = step
    hgxci__tgvwq.name = name
    return NativeValue(hgxci__tgvwq._getvalue())


@lower_constant(RangeIndexType)
def lower_constant_range_index(context, builder, ty, pyval):
    start = context.get_constant(types.int64, pyval.start)
    stop = context.get_constant(types.int64, pyval.stop)
    step = context.get_constant(types.int64, pyval.step)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    return lir.Constant.literal_struct([start, stop, step, name])


@overload(pd.RangeIndex, no_unliteral=True, inline='always')
def range_index_overload(start=None, stop=None, step=None, dtype=None, copy
    =False, name=None):

    def _ensure_int_or_none(value, field):
        dtkf__ypq = (
            'RangeIndex(...) must be called with integers, {value} was passed for {field}'
            )
        if not is_overload_none(value) and not isinstance(value, types.
            IntegerLiteral) and not isinstance(value, types.Integer):
            raise BodoError(dtkf__ypq.format(value=value, field=field))
    _ensure_int_or_none(start, 'start')
    _ensure_int_or_none(stop, 'stop')
    _ensure_int_or_none(step, 'step')
    if is_overload_none(start) and is_overload_none(stop) and is_overload_none(
        step):
        dtkf__ypq = 'RangeIndex(...) must be called with integers'
        raise BodoError(dtkf__ypq)
    obvfu__nroyn = 'start'
    kdqx__qcnew = 'stop'
    hfcix__bvelg = 'step'
    if is_overload_none(start):
        obvfu__nroyn = '0'
    if is_overload_none(stop):
        kdqx__qcnew = 'start'
        obvfu__nroyn = '0'
    if is_overload_none(step):
        hfcix__bvelg = '1'
    csxb__cig = """def _pd_range_index_imp(start=None, stop=None, step=None, dtype=None, copy=False, name=None):
"""
    csxb__cig += '  return init_range_index({}, {}, {}, name)\n'.format(
        obvfu__nroyn, kdqx__qcnew, hfcix__bvelg)
    zxve__rey = {}
    exec(csxb__cig, {'init_range_index': init_range_index}, zxve__rey)
    tejak__zqmgu = zxve__rey['_pd_range_index_imp']
    return tejak__zqmgu


@overload(pd.CategoricalIndex, no_unliteral=True, inline='always')
def categorical_index_overload(data=None, categories=None, ordered=None,
    dtype=None, copy=False, name=None):
    raise BodoError('pd.CategoricalIndex() initializer not yet supported.')


@overload_attribute(RangeIndexType, 'start')
def rangeIndex_get_start(ri):

    def impl(ri):
        return ri._start
    return impl


@overload_attribute(RangeIndexType, 'stop')
def rangeIndex_get_stop(ri):

    def impl(ri):
        return ri._stop
    return impl


@overload_attribute(RangeIndexType, 'step')
def rangeIndex_get_step(ri):

    def impl(ri):
        return ri._step
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_range_index_getitem(I, idx):
    if isinstance(I, RangeIndexType):
        if isinstance(types.unliteral(idx), types.Integer):
            return lambda I, idx: idx * I._step + I._start
        if isinstance(idx, types.SliceType):

            def impl(I, idx):
                ugfbv__nmz = numba.cpython.unicode._normalize_slice(idx, len(I)
                    )
                name = bodo.hiframes.pd_index_ext.get_index_name(I)
                start = I._start + I._step * ugfbv__nmz.start
                stop = I._start + I._step * ugfbv__nmz.stop
                step = I._step * ugfbv__nmz.step
                return bodo.hiframes.pd_index_ext.init_range_index(start,
                    stop, step, name)
            return impl
        return lambda I, idx: bodo.hiframes.pd_index_ext.init_numeric_index(np
            .arange(I._start, I._stop, I._step, np.int64)[idx], bodo.
            hiframes.pd_index_ext.get_index_name(I))


@overload(len, no_unliteral=True)
def overload_range_len(r):
    if isinstance(r, RangeIndexType):
        return lambda r: max(0, -(-(r._stop - r._start) // r._step))


class PeriodIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, freq, name_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.freq = freq
        self.name_typ = name_typ
        super(PeriodIndexType, self).__init__(name=
            'PeriodIndexType({}, {})'.format(freq, name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return PeriodIndexType(self.freq, self.name_typ)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'period[{self.freq}]'


@typeof_impl.register(pd.PeriodIndex)
def typeof_pd_period_index(val, c):
    return PeriodIndexType(val.freqstr, get_val_type_maybe_str_literal(val.
        name))


@register_model(PeriodIndexType)
class PeriodIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zqxbb__dam = [('data', bodo.IntegerArrayType(types.int64)), ('name',
            fe_type.name_typ), ('dict', types.DictType(types.int64, types.
            int64))]
        super(PeriodIndexModel, self).__init__(dmm, fe_type, zqxbb__dam)


make_attribute_wrapper(PeriodIndexType, 'data', '_data')
make_attribute_wrapper(PeriodIndexType, 'name', '_name')
make_attribute_wrapper(PeriodIndexType, 'dict', '_dict')


@overload_method(PeriodIndexType, 'copy', no_unliteral=True)
def overload_period_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    freq = A.freq
    praj__uikjl = dict(deep=deep, dtype=dtype, names=names)
    pyn__hdgii = idx_typ_to_format_str_map[PeriodIndexType].format('copy()')
    check_unsupported_args('PeriodIndex.copy', praj__uikjl,
        idx_cpy_arg_defaults, fn_str=pyn__hdgii, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), name, freq)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_period_index(A._data.
                copy(), A._name, freq)
    return impl


@intrinsic
def init_period_index(typingctx, data, name, freq):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        xdjx__kidrp, cato__uabrz, fwa__yqkb = args
        adbzk__dpgss = signature.return_type
        vhdtx__ynoup = cgutils.create_struct_proxy(adbzk__dpgss)(context,
            builder)
        vhdtx__ynoup.data = xdjx__kidrp
        vhdtx__ynoup.name = cato__uabrz
        context.nrt.incref(builder, signature.args[0], args[0])
        context.nrt.incref(builder, signature.args[1], args[1])
        vhdtx__ynoup.dict = context.compile_internal(builder, lambda :
            numba.typed.Dict.empty(types.int64, types.int64), types.
            DictType(types.int64, types.int64)(), [])
        return vhdtx__ynoup._getvalue()
    fzhp__csowg = get_overload_const_str(freq)
    zqa__dicdh = PeriodIndexType(fzhp__csowg, name)
    sig = signature(zqa__dicdh, data, name, freq)
    return sig, codegen


@box(PeriodIndexType)
def box_period_index(typ, val, c):
    dgt__ygbwa = c.context.insert_const_string(c.builder.module, 'pandas')
    akli__zdymk = c.pyapi.import_module_noblock(dgt__ygbwa)
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, bodo.IntegerArrayType(types.int64),
        rxl__bsb.data)
    qrox__vnh = c.pyapi.from_native_value(bodo.IntegerArrayType(types.int64
        ), rxl__bsb.data, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, rxl__bsb.name)
    ldf__kwktb = c.pyapi.from_native_value(typ.name_typ, rxl__bsb.name, c.
        env_manager)
    vgrh__tbh = c.pyapi.string_from_constant_string(typ.freq)
    args = c.pyapi.tuple_pack([])
    kws = c.pyapi.dict_pack([('ordinal', qrox__vnh), ('name', ldf__kwktb),
        ('freq', vgrh__tbh)])
    npo__ufzy = c.pyapi.object_getattr_string(akli__zdymk, 'PeriodIndex')
    yfb__aacnr = c.pyapi.call(npo__ufzy, args, kws)
    c.pyapi.decref(qrox__vnh)
    c.pyapi.decref(ldf__kwktb)
    c.pyapi.decref(vgrh__tbh)
    c.pyapi.decref(akli__zdymk)
    c.pyapi.decref(npo__ufzy)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return yfb__aacnr


@unbox(PeriodIndexType)
def unbox_period_index(typ, val, c):
    arr_typ = bodo.IntegerArrayType(types.int64)
    hefr__xwm = c.pyapi.object_getattr_string(val, 'asi8')
    uwm__puuvh = c.pyapi.call_method(val, 'isna', ())
    ldf__kwktb = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, ldf__kwktb).value
    dgt__ygbwa = c.context.insert_const_string(c.builder.module, 'pandas')
    qal__zov = c.pyapi.import_module_noblock(dgt__ygbwa)
    pgsth__koz = c.pyapi.object_getattr_string(qal__zov, 'arrays')
    qrox__vnh = c.pyapi.call_method(pgsth__koz, 'IntegerArray', (hefr__xwm,
        uwm__puuvh))
    data = c.pyapi.to_native_value(arr_typ, qrox__vnh).value
    c.pyapi.decref(hefr__xwm)
    c.pyapi.decref(uwm__puuvh)
    c.pyapi.decref(ldf__kwktb)
    c.pyapi.decref(qal__zov)
    c.pyapi.decref(pgsth__koz)
    c.pyapi.decref(qrox__vnh)
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rxl__bsb.data = data
    rxl__bsb.name = name
    zdm__yeznr, svj__fxxg = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(types.int64, types.int64), types.DictType(types.int64, types
        .int64)(), [])
    rxl__bsb.dict = svj__fxxg
    return NativeValue(rxl__bsb._getvalue())


class CategoricalIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
        assert isinstance(data, CategoricalArrayType
            ), 'CategoricalIndexType expects CategoricalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(CategoricalIndexType, self).__init__(name=
            f'CategoricalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return CategoricalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'categorical'

    @property
    def numpy_type_name(self):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        return str(get_categories_int_type(self.dtype))

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self, self.dtype.elem_type)


@register_model(CategoricalIndexType)
class CategoricalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        sgbsc__cjff = get_categories_int_type(fe_type.data.dtype)
        zqxbb__dam = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(sgbsc__cjff, types.int64))]
        super(CategoricalIndexTypeModel, self).__init__(dmm, fe_type,
            zqxbb__dam)


@typeof_impl.register(pd.CategoricalIndex)
def typeof_categorical_index(val, c):
    return CategoricalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(CategoricalIndexType)
def box_categorical_index(typ, val, c):
    dgt__ygbwa = c.context.insert_const_string(c.builder.module, 'pandas')
    qal__zov = c.pyapi.import_module_noblock(dgt__ygbwa)
    bnl__vqna = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, bnl__vqna.data)
    htv__sej = c.pyapi.from_native_value(typ.data, bnl__vqna.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, bnl__vqna.name)
    ldf__kwktb = c.pyapi.from_native_value(typ.name_typ, bnl__vqna.name, c.
        env_manager)
    args = c.pyapi.tuple_pack([htv__sej])
    kws = c.pyapi.dict_pack([('name', ldf__kwktb)])
    npo__ufzy = c.pyapi.object_getattr_string(qal__zov, 'CategoricalIndex')
    tfqb__cpbi = c.pyapi.call(npo__ufzy, args, kws)
    c.pyapi.decref(htv__sej)
    c.pyapi.decref(ldf__kwktb)
    c.pyapi.decref(qal__zov)
    c.pyapi.decref(npo__ufzy)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return tfqb__cpbi


@unbox(CategoricalIndexType)
def unbox_categorical_index(typ, val, c):
    from bodo.hiframes.pd_categorical_ext import get_categories_int_type
    fxh__wroi = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, fxh__wroi).value
    ldf__kwktb = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, ldf__kwktb).value
    c.pyapi.decref(fxh__wroi)
    c.pyapi.decref(ldf__kwktb)
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rxl__bsb.data = data
    rxl__bsb.name = name
    dtype = get_categories_int_type(typ.data.dtype)
    zdm__yeznr, svj__fxxg = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    rxl__bsb.dict = svj__fxxg
    return NativeValue(rxl__bsb._getvalue())


@intrinsic
def init_categorical_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        from bodo.hiframes.pd_categorical_ext import get_categories_int_type
        xdjx__kidrp, cato__uabrz = args
        bnl__vqna = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        bnl__vqna.data = xdjx__kidrp
        bnl__vqna.name = cato__uabrz
        context.nrt.incref(builder, signature.args[0], xdjx__kidrp)
        context.nrt.incref(builder, signature.args[1], cato__uabrz)
        dtype = get_categories_int_type(signature.return_type.data.dtype)
        bnl__vqna.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return bnl__vqna._getvalue()
    zqa__dicdh = CategoricalIndexType(data, name)
    sig = signature(zqa__dicdh, data, name)
    return sig, codegen


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_categorical_index
    ) = init_index_equiv
make_attribute_wrapper(CategoricalIndexType, 'data', '_data')
make_attribute_wrapper(CategoricalIndexType, 'name', '_name')
make_attribute_wrapper(CategoricalIndexType, 'dict', '_dict')


@overload_method(CategoricalIndexType, 'copy', no_unliteral=True)
def overload_categorical_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    pyn__hdgii = idx_typ_to_format_str_map[CategoricalIndexType].format(
        'copy()')
    praj__uikjl = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('CategoricalIndex.copy', praj__uikjl,
        idx_cpy_arg_defaults, fn_str=pyn__hdgii, package_name='pandas',
        module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_categorical_index(A.
                _data.copy(), A._name)
    return impl


class IntervalIndexType(types.ArrayCompatible):

    def __init__(self, data, name_typ=None):
        from bodo.libs.interval_arr_ext import IntervalArrayType
        assert isinstance(data, IntervalArrayType
            ), 'IntervalIndexType expects IntervalArrayType'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = data
        super(IntervalIndexType, self).__init__(name=
            f'IntervalIndexType(data={self.data}, name={name_typ})')
    ndim = 1

    def copy(self):
        return IntervalIndexType(self.data, self.name_typ)

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return f'interval[{self.data.arr_type.dtype}, right]'


@register_model(IntervalIndexType)
class IntervalIndexTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zqxbb__dam = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(types.UniTuple(fe_type.data.arr_type.
            dtype, 2), types.int64))]
        super(IntervalIndexTypeModel, self).__init__(dmm, fe_type, zqxbb__dam)


@typeof_impl.register(pd.IntervalIndex)
def typeof_interval_index(val, c):
    return IntervalIndexType(bodo.typeof(val.values),
        get_val_type_maybe_str_literal(val.name))


@box(IntervalIndexType)
def box_interval_index(typ, val, c):
    dgt__ygbwa = c.context.insert_const_string(c.builder.module, 'pandas')
    qal__zov = c.pyapi.import_module_noblock(dgt__ygbwa)
    yovc__peijr = numba.core.cgutils.create_struct_proxy(typ)(c.context, c.
        builder, val)
    c.context.nrt.incref(c.builder, typ.data, yovc__peijr.data)
    htv__sej = c.pyapi.from_native_value(typ.data, yovc__peijr.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, yovc__peijr.name)
    ldf__kwktb = c.pyapi.from_native_value(typ.name_typ, yovc__peijr.name,
        c.env_manager)
    args = c.pyapi.tuple_pack([htv__sej])
    kws = c.pyapi.dict_pack([('name', ldf__kwktb)])
    npo__ufzy = c.pyapi.object_getattr_string(qal__zov, 'IntervalIndex')
    tfqb__cpbi = c.pyapi.call(npo__ufzy, args, kws)
    c.pyapi.decref(htv__sej)
    c.pyapi.decref(ldf__kwktb)
    c.pyapi.decref(qal__zov)
    c.pyapi.decref(npo__ufzy)
    c.pyapi.decref(args)
    c.pyapi.decref(kws)
    c.context.nrt.decref(c.builder, typ, val)
    return tfqb__cpbi


@unbox(IntervalIndexType)
def unbox_interval_index(typ, val, c):
    fxh__wroi = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, fxh__wroi).value
    ldf__kwktb = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, ldf__kwktb).value
    c.pyapi.decref(fxh__wroi)
    c.pyapi.decref(ldf__kwktb)
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rxl__bsb.data = data
    rxl__bsb.name = name
    dtype = types.UniTuple(typ.data.arr_type.dtype, 2)
    zdm__yeznr, svj__fxxg = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    rxl__bsb.dict = svj__fxxg
    return NativeValue(rxl__bsb._getvalue())


@intrinsic
def init_interval_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        xdjx__kidrp, cato__uabrz = args
        yovc__peijr = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        yovc__peijr.data = xdjx__kidrp
        yovc__peijr.name = cato__uabrz
        context.nrt.incref(builder, signature.args[0], xdjx__kidrp)
        context.nrt.incref(builder, signature.args[1], cato__uabrz)
        dtype = types.UniTuple(data.arr_type.dtype, 2)
        yovc__peijr.dict = context.compile_internal(builder, lambda : numba
            .typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return yovc__peijr._getvalue()
    zqa__dicdh = IntervalIndexType(data, name)
    sig = signature(zqa__dicdh, data, name)
    return sig, codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_interval_index
    ) = init_index_equiv
make_attribute_wrapper(IntervalIndexType, 'data', '_data')
make_attribute_wrapper(IntervalIndexType, 'name', '_name')
make_attribute_wrapper(IntervalIndexType, 'dict', '_dict')


class NumericIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, dtype, name_typ=None, data=None):
        name_typ = types.none if name_typ is None else name_typ
        self.dtype = dtype
        self.name_typ = name_typ
        data = dtype_to_array_type(dtype) if data is None else data
        self.data = data
        super(NumericIndexType, self).__init__(name=
            f'NumericIndexType({dtype}, {name_typ}, {data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return NumericIndexType(self.dtype, self.name_typ, self.data)

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)

    @property
    def pandas_type_name(self):
        return str(self.dtype)

    @property
    def numpy_type_name(self):
        return str(self.dtype)


with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    Int64Index = pd.Int64Index
    UInt64Index = pd.UInt64Index
    Float64Index = pd.Float64Index


@typeof_impl.register(Int64Index)
def typeof_pd_int64_index(val, c):
    return NumericIndexType(types.int64, get_val_type_maybe_str_literal(val
        .name))


@typeof_impl.register(UInt64Index)
def typeof_pd_uint64_index(val, c):
    return NumericIndexType(types.uint64, get_val_type_maybe_str_literal(
        val.name))


@typeof_impl.register(Float64Index)
def typeof_pd_float64_index(val, c):
    return NumericIndexType(types.float64, get_val_type_maybe_str_literal(
        val.name))


@register_model(NumericIndexType)
class NumericIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zqxbb__dam = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(fe_type.dtype, types.int64))]
        super(NumericIndexModel, self).__init__(dmm, fe_type, zqxbb__dam)


make_attribute_wrapper(NumericIndexType, 'data', '_data')
make_attribute_wrapper(NumericIndexType, 'name', '_name')
make_attribute_wrapper(NumericIndexType, 'dict', '_dict')


@overload_method(NumericIndexType, 'copy', no_unliteral=True)
def overload_numeric_index_copy(A, name=None, deep=False, dtype=None, names
    =None):
    pyn__hdgii = idx_typ_to_format_str_map[NumericIndexType].format('copy()')
    praj__uikjl = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', praj__uikjl, idx_cpy_arg_defaults,
        fn_str=pyn__hdgii, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(NumericIndexType)
def box_numeric_index(typ, val, c):
    dgt__ygbwa = c.context.insert_const_string(c.builder.module, 'pandas')
    akli__zdymk = c.pyapi.import_module_noblock(dgt__ygbwa)
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, rxl__bsb.data)
    qrox__vnh = c.pyapi.from_native_value(typ.data, rxl__bsb.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, rxl__bsb.name)
    ldf__kwktb = c.pyapi.from_native_value(typ.name_typ, rxl__bsb.name, c.
        env_manager)
    whjws__xfx = c.pyapi.make_none()
    cig__cnffu = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    yfb__aacnr = c.pyapi.call_method(akli__zdymk, 'Index', (qrox__vnh,
        whjws__xfx, cig__cnffu, ldf__kwktb))
    c.pyapi.decref(qrox__vnh)
    c.pyapi.decref(whjws__xfx)
    c.pyapi.decref(cig__cnffu)
    c.pyapi.decref(ldf__kwktb)
    c.pyapi.decref(akli__zdymk)
    c.context.nrt.decref(c.builder, typ, val)
    return yfb__aacnr


@intrinsic
def init_numeric_index(typingctx, data, name=None):
    name = types.none if is_overload_none(name) else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        adbzk__dpgss = signature.return_type
        rxl__bsb = cgutils.create_struct_proxy(adbzk__dpgss)(context, builder)
        rxl__bsb.data = args[0]
        rxl__bsb.name = args[1]
        context.nrt.incref(builder, adbzk__dpgss.data, args[0])
        context.nrt.incref(builder, adbzk__dpgss.name_typ, args[1])
        dtype = adbzk__dpgss.dtype
        rxl__bsb.dict = context.compile_internal(builder, lambda : numba.
            typed.Dict.empty(dtype, types.int64), types.DictType(dtype,
            types.int64)(), [])
        return rxl__bsb._getvalue()
    return NumericIndexType(data.dtype, name, data)(data, name), codegen


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_init_numeric_index
    ) = init_index_equiv


@unbox(NumericIndexType)
def unbox_numeric_index(typ, val, c):
    fxh__wroi = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(typ.data, fxh__wroi).value
    ldf__kwktb = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, ldf__kwktb).value
    c.pyapi.decref(fxh__wroi)
    c.pyapi.decref(ldf__kwktb)
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rxl__bsb.data = data
    rxl__bsb.name = name
    dtype = typ.dtype
    zdm__yeznr, svj__fxxg = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(dtype, types.int64), types.DictType(dtype, types.int64)(), [])
    rxl__bsb.dict = svj__fxxg
    return NativeValue(rxl__bsb._getvalue())


def create_numeric_constructor(func, func_str, default_dtype):

    def overload_impl(data=None, dtype=None, copy=False, name=None):
        ngmj__mopbf = dict(dtype=dtype)
        lhah__fwcoy = dict(dtype=None)
        check_unsupported_args(func_str, ngmj__mopbf, lhah__fwcoy,
            package_name='pandas', module_name='Index')
        if is_overload_false(copy):

            def impl(data=None, dtype=None, copy=False, name=None):
                ngmp__lipdl = bodo.utils.conversion.coerce_to_ndarray(data)
                hwv__yym = bodo.utils.conversion.fix_arr_dtype(ngmp__lipdl,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(hwv__yym,
                    name)
        else:

            def impl(data=None, dtype=None, copy=False, name=None):
                ngmp__lipdl = bodo.utils.conversion.coerce_to_ndarray(data)
                if copy:
                    ngmp__lipdl = ngmp__lipdl.copy()
                hwv__yym = bodo.utils.conversion.fix_arr_dtype(ngmp__lipdl,
                    np.dtype(default_dtype))
                return bodo.hiframes.pd_index_ext.init_numeric_index(hwv__yym,
                    name)
        return impl
    return overload_impl


def _install_numeric_constructors():
    for func, func_str, default_dtype in ((Int64Index, 'pandas.Int64Index',
        np.int64), (UInt64Index, 'pandas.UInt64Index', np.uint64), (
        Float64Index, 'pandas.Float64Index', np.float64)):
        overload_impl = create_numeric_constructor(func, func_str,
            default_dtype)
        overload(func, no_unliteral=True)(overload_impl)


_install_numeric_constructors()


class StringIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data_typ=None):
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = string_array_type if data_typ is None else data_typ
        super(StringIndexType, self).__init__(name=
            f'StringIndexType({name_typ}, {self.data})')
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return StringIndexType(self.name_typ, self.data)

    @property
    def dtype(self):
        return string_type

    @property
    def pandas_type_name(self):
        return 'unicode'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


@register_model(StringIndexType)
class StringIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zqxbb__dam = [('data', fe_type.data), ('name', fe_type.name_typ), (
            'dict', types.DictType(string_type, types.int64))]
        super(StringIndexModel, self).__init__(dmm, fe_type, zqxbb__dam)


make_attribute_wrapper(StringIndexType, 'data', '_data')
make_attribute_wrapper(StringIndexType, 'name', '_name')
make_attribute_wrapper(StringIndexType, 'dict', '_dict')


class BinaryIndexType(types.IterableType, types.ArrayCompatible):

    def __init__(self, name_typ=None, data_typ=None):
        assert data_typ is None or data_typ == binary_array_type, 'data_typ must be binary_array_type'
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        self.data = binary_array_type
        super(BinaryIndexType, self).__init__(name='BinaryIndexType({})'.
            format(name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return BinaryIndexType(self.name_typ)

    @property
    def dtype(self):
        return bytes_type

    @property
    def pandas_type_name(self):
        return 'bytes'

    @property
    def numpy_type_name(self):
        return 'object'

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


@register_model(BinaryIndexType)
class BinaryIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zqxbb__dam = [('data', binary_array_type), ('name', fe_type.
            name_typ), ('dict', types.DictType(bytes_type, types.int64))]
        super(BinaryIndexModel, self).__init__(dmm, fe_type, zqxbb__dam)


make_attribute_wrapper(BinaryIndexType, 'data', '_data')
make_attribute_wrapper(BinaryIndexType, 'name', '_name')
make_attribute_wrapper(BinaryIndexType, 'dict', '_dict')


@unbox(BinaryIndexType)
@unbox(StringIndexType)
def unbox_binary_str_index(typ, val, c):
    lirm__pwnp = typ.data
    scalar_type = typ.data.dtype
    fxh__wroi = c.pyapi.object_getattr_string(val, 'values')
    data = c.pyapi.to_native_value(lirm__pwnp, fxh__wroi).value
    ldf__kwktb = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, ldf__kwktb).value
    c.pyapi.decref(fxh__wroi)
    c.pyapi.decref(ldf__kwktb)
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    rxl__bsb.data = data
    rxl__bsb.name = name
    zdm__yeznr, svj__fxxg = c.pyapi.call_jit_code(lambda : numba.typed.Dict
        .empty(scalar_type, types.int64), types.DictType(scalar_type, types
        .int64)(), [])
    rxl__bsb.dict = svj__fxxg
    return NativeValue(rxl__bsb._getvalue())


@box(BinaryIndexType)
@box(StringIndexType)
def box_binary_str_index(typ, val, c):
    lirm__pwnp = typ.data
    dgt__ygbwa = c.context.insert_const_string(c.builder.module, 'pandas')
    akli__zdymk = c.pyapi.import_module_noblock(dgt__ygbwa)
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, lirm__pwnp, rxl__bsb.data)
    qrox__vnh = c.pyapi.from_native_value(lirm__pwnp, rxl__bsb.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, rxl__bsb.name)
    ldf__kwktb = c.pyapi.from_native_value(typ.name_typ, rxl__bsb.name, c.
        env_manager)
    whjws__xfx = c.pyapi.make_none()
    cig__cnffu = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    yfb__aacnr = c.pyapi.call_method(akli__zdymk, 'Index', (qrox__vnh,
        whjws__xfx, cig__cnffu, ldf__kwktb))
    c.pyapi.decref(qrox__vnh)
    c.pyapi.decref(whjws__xfx)
    c.pyapi.decref(cig__cnffu)
    c.pyapi.decref(ldf__kwktb)
    c.pyapi.decref(akli__zdymk)
    c.context.nrt.decref(c.builder, typ, val)
    return yfb__aacnr


@intrinsic
def init_binary_str_index(typingctx, data, name=None):
    name = types.none if name is None else name
    sig = type(bodo.utils.typing.get_index_type_from_dtype(data.dtype))(name,
        data)(data, name)
    dbyzm__jfhin = get_binary_str_codegen(is_binary=data.dtype == bytes_type)
    return sig, dbyzm__jfhin


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_index_ext_init_binary_str_index
    ) = init_index_equiv


def get_binary_str_codegen(is_binary=False):
    if is_binary:
        hnwxk__owhg = 'bytes_type'
    else:
        hnwxk__owhg = 'string_type'
    csxb__cig = 'def impl(context, builder, signature, args):\n'
    csxb__cig += '    assert len(args) == 2\n'
    csxb__cig += '    index_typ = signature.return_type\n'
    csxb__cig += (
        '    index_val = cgutils.create_struct_proxy(index_typ)(context, builder)\n'
        )
    csxb__cig += '    index_val.data = args[0]\n'
    csxb__cig += '    index_val.name = args[1]\n'
    csxb__cig += '    # increase refcount of stored values\n'
    csxb__cig += (
        '    context.nrt.incref(builder, signature.args[0], args[0])\n')
    csxb__cig += (
        '    context.nrt.incref(builder, index_typ.name_typ, args[1])\n')
    csxb__cig += '    # create empty dict for get_loc hashmap\n'
    csxb__cig += '    index_val.dict = context.compile_internal(\n'
    csxb__cig += '       builder,\n'
    csxb__cig += (
        f'       lambda: numba.typed.Dict.empty({hnwxk__owhg}, types.int64),\n'
        )
    csxb__cig += (
        f'        types.DictType({hnwxk__owhg}, types.int64)(), [],)\n')
    csxb__cig += '    return index_val._getvalue()\n'
    zxve__rey = {}
    exec(csxb__cig, {'bodo': bodo, 'signature': signature, 'cgutils':
        cgutils, 'numba': numba, 'types': types, 'bytes_type': bytes_type,
        'string_type': string_type}, zxve__rey)
    impl = zxve__rey['impl']
    return impl


@overload_method(BinaryIndexType, 'copy', no_unliteral=True)
@overload_method(StringIndexType, 'copy', no_unliteral=True)
def overload_binary_string_index_copy(A, name=None, deep=False, dtype=None,
    names=None):
    typ = type(A)
    pyn__hdgii = idx_typ_to_format_str_map[typ].format('copy()')
    praj__uikjl = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', praj__uikjl, idx_cpy_arg_defaults,
        fn_str=pyn__hdgii, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_binary_str_index(A._data
                .copy(), A._name)
    return impl


@overload_attribute(BinaryIndexType, 'name')
@overload_attribute(StringIndexType, 'name')
@overload_attribute(DatetimeIndexType, 'name')
@overload_attribute(TimedeltaIndexType, 'name')
@overload_attribute(RangeIndexType, 'name')
@overload_attribute(PeriodIndexType, 'name')
@overload_attribute(NumericIndexType, 'name')
@overload_attribute(IntervalIndexType, 'name')
@overload_attribute(CategoricalIndexType, 'name')
@overload_attribute(MultiIndexType, 'name')
def Index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_index_getitem(I, ind):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType)
        ) and isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, NumericIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_numeric_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))
    if isinstance(I, (StringIndexType, BinaryIndexType)):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_binary_str_index(
            bodo.hiframes.pd_index_ext.get_index_data(I)[ind], bodo.
            hiframes.pd_index_ext.get_index_name(I))


def array_type_to_index(arr_typ, name_typ=None):
    if is_str_arr_type(arr_typ):
        return StringIndexType(name_typ, arr_typ)
    if arr_typ == bodo.binary_array_type:
        return BinaryIndexType(name_typ)
    assert isinstance(arr_typ, (types.Array, IntegerArrayType, bodo.
        CategoricalArrayType)) or arr_typ in (bodo.datetime_date_array_type,
        bodo.boolean_array
        ), f'Converting array type {arr_typ} to index not supported'
    if (arr_typ == bodo.datetime_date_array_type or arr_typ.dtype == types.
        NPDatetime('ns')):
        return DatetimeIndexType(name_typ)
    if isinstance(arr_typ, bodo.DatetimeArrayType):
        return DatetimeIndexType(name_typ, arr_typ)
    if isinstance(arr_typ, bodo.CategoricalArrayType):
        return CategoricalIndexType(arr_typ, name_typ)
    if arr_typ.dtype == types.NPTimedelta('ns'):
        return TimedeltaIndexType(name_typ)
    if isinstance(arr_typ.dtype, (types.Integer, types.Float, types.Boolean)):
        return NumericIndexType(arr_typ.dtype, name_typ, arr_typ)
    raise BodoError(f'invalid index type {arr_typ}')


def is_pd_index_type(t):
    return isinstance(t, (NumericIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType,
        PeriodIndexType, StringIndexType, BinaryIndexType, RangeIndexType,
        HeterogeneousIndexType))


def _verify_setop_compatible(func_name, I, other):
    if not is_pd_index_type(other) and not isinstance(other, (SeriesType,
        types.Array)):
        raise BodoError(
            f'pd.Index.{func_name}(): unsupported type for argument other: {other}'
            )
    qzxx__rhwb = I.dtype if not isinstance(I, RangeIndexType) else types.int64
    bwp__acc = other.dtype if not isinstance(other, RangeIndexType
        ) else types.int64
    if qzxx__rhwb != bwp__acc:
        raise BodoError(
            f'Index.{func_name}(): incompatible types {qzxx__rhwb} and {bwp__acc}'
            )


@overload_method(NumericIndexType, 'union', inline='always')
@overload_method(StringIndexType, 'union', inline='always')
@overload_method(BinaryIndexType, 'union', inline='always')
@overload_method(DatetimeIndexType, 'union', inline='always')
@overload_method(TimedeltaIndexType, 'union', inline='always')
@overload_method(RangeIndexType, 'union', inline='always')
def overload_index_union(I, other, sort=None):
    rdv__ubcq = dict(sort=sort)
    mpzx__ene = dict(sort=None)
    check_unsupported_args('Index.union', rdv__ubcq, mpzx__ene,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('union', I, other)
    nusq__twalo = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        cbpr__jehd = bodo.utils.conversion.coerce_to_array(I)
        wfxl__hqpxh = bodo.utils.conversion.coerce_to_array(other)
        sho__wykl = bodo.libs.array_kernels.concat([cbpr__jehd, wfxl__hqpxh])
        potab__wnoz = bodo.libs.array_kernels.unique(sho__wykl)
        return nusq__twalo(potab__wnoz, None)
    return impl


@overload_method(NumericIndexType, 'intersection', inline='always')
@overload_method(StringIndexType, 'intersection', inline='always')
@overload_method(BinaryIndexType, 'intersection', inline='always')
@overload_method(DatetimeIndexType, 'intersection', inline='always')
@overload_method(TimedeltaIndexType, 'intersection', inline='always')
@overload_method(RangeIndexType, 'intersection', inline='always')
def overload_index_intersection(I, other, sort=None):
    rdv__ubcq = dict(sort=sort)
    mpzx__ene = dict(sort=None)
    check_unsupported_args('Index.intersection', rdv__ubcq, mpzx__ene,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('intersection', I, other)
    nusq__twalo = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        cbpr__jehd = bodo.utils.conversion.coerce_to_array(I)
        wfxl__hqpxh = bodo.utils.conversion.coerce_to_array(other)
        aurze__jowi = bodo.libs.array_kernels.unique(cbpr__jehd)
        dahk__pkl = bodo.libs.array_kernels.unique(wfxl__hqpxh)
        sho__wykl = bodo.libs.array_kernels.concat([aurze__jowi, dahk__pkl])
        ripm__hwcye = pd.Series(sho__wykl).sort_values().values
        lry__cwjsb = bodo.libs.array_kernels.intersection_mask(ripm__hwcye)
        return nusq__twalo(ripm__hwcye[lry__cwjsb], None)
    return impl


@overload_method(NumericIndexType, 'difference', inline='always')
@overload_method(StringIndexType, 'difference', inline='always')
@overload_method(BinaryIndexType, 'difference', inline='always')
@overload_method(DatetimeIndexType, 'difference', inline='always')
@overload_method(TimedeltaIndexType, 'difference', inline='always')
@overload_method(RangeIndexType, 'difference', inline='always')
def overload_index_difference(I, other, sort=None):
    rdv__ubcq = dict(sort=sort)
    mpzx__ene = dict(sort=None)
    check_unsupported_args('Index.difference', rdv__ubcq, mpzx__ene,
        package_name='pandas', module_name='Index')
    _verify_setop_compatible('difference', I, other)
    nusq__twalo = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, sort=None):
        cbpr__jehd = bodo.utils.conversion.coerce_to_array(I)
        wfxl__hqpxh = bodo.utils.conversion.coerce_to_array(other)
        aurze__jowi = bodo.libs.array_kernels.unique(cbpr__jehd)
        dahk__pkl = bodo.libs.array_kernels.unique(wfxl__hqpxh)
        lry__cwjsb = np.empty(len(aurze__jowi), np.bool_)
        bodo.libs.array.array_isin(lry__cwjsb, aurze__jowi, dahk__pkl, False)
        return nusq__twalo(aurze__jowi[~lry__cwjsb], None)
    return impl


@overload_method(NumericIndexType, 'symmetric_difference', inline='always')
@overload_method(StringIndexType, 'symmetric_difference', inline='always')
@overload_method(BinaryIndexType, 'symmetric_difference', inline='always')
@overload_method(DatetimeIndexType, 'symmetric_difference', inline='always')
@overload_method(TimedeltaIndexType, 'symmetric_difference', inline='always')
@overload_method(RangeIndexType, 'symmetric_difference', inline='always')
def overload_index_symmetric_difference(I, other, result_name=None, sort=None):
    rdv__ubcq = dict(result_name=result_name, sort=sort)
    mpzx__ene = dict(result_name=None, sort=None)
    check_unsupported_args('Index.symmetric_difference', rdv__ubcq,
        mpzx__ene, package_name='pandas', module_name='Index')
    _verify_setop_compatible('symmetric_difference', I, other)
    nusq__twalo = get_index_constructor(I) if not isinstance(I, RangeIndexType
        ) else init_numeric_index

    def impl(I, other, result_name=None, sort=None):
        cbpr__jehd = bodo.utils.conversion.coerce_to_array(I)
        wfxl__hqpxh = bodo.utils.conversion.coerce_to_array(other)
        aurze__jowi = bodo.libs.array_kernels.unique(cbpr__jehd)
        dahk__pkl = bodo.libs.array_kernels.unique(wfxl__hqpxh)
        dnkeq__xatl = np.empty(len(aurze__jowi), np.bool_)
        ehkj__qznl = np.empty(len(dahk__pkl), np.bool_)
        bodo.libs.array.array_isin(dnkeq__xatl, aurze__jowi, dahk__pkl, False)
        bodo.libs.array.array_isin(ehkj__qznl, dahk__pkl, aurze__jowi, False)
        fqpqr__qnpek = bodo.libs.array_kernels.concat([aurze__jowi[~
            dnkeq__xatl], dahk__pkl[~ehkj__qznl]])
        return nusq__twalo(fqpqr__qnpek, None)
    return impl


@overload_method(RangeIndexType, 'take', no_unliteral=True)
@overload_method(NumericIndexType, 'take', no_unliteral=True)
@overload_method(StringIndexType, 'take', no_unliteral=True)
@overload_method(BinaryIndexType, 'take', no_unliteral=True)
@overload_method(CategoricalIndexType, 'take', no_unliteral=True)
@overload_method(PeriodIndexType, 'take', no_unliteral=True)
@overload_method(DatetimeIndexType, 'take', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'take', no_unliteral=True)
def overload_index_take(I, indices, axis=0, allow_fill=True, fill_value=None):
    rdv__ubcq = dict(axis=axis, allow_fill=allow_fill, fill_value=fill_value)
    mpzx__ene = dict(axis=0, allow_fill=True, fill_value=None)
    check_unsupported_args('Index.take', rdv__ubcq, mpzx__ene, package_name
        ='pandas', module_name='Index')
    return lambda I, indices: I[indices]


def _init_engine(I, ban_unique=True):
    pass


@overload(_init_engine)
def overload_init_engine(I, ban_unique=True):
    if isinstance(I, CategoricalIndexType):

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                req__chq = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(req__chq)):
                    if not bodo.libs.array_kernels.isna(req__chq, i):
                        val = (bodo.hiframes.pd_categorical_ext.
                            get_code_for_value(req__chq.dtype, req__chq[i]))
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl
    else:

        def impl(I, ban_unique=True):
            if len(I) > 0 and not I._dict:
                req__chq = bodo.utils.conversion.coerce_to_array(I)
                for i in range(len(req__chq)):
                    if not bodo.libs.array_kernels.isna(req__chq, i):
                        val = req__chq[i]
                        if ban_unique and val in I._dict:
                            raise ValueError(
                                'Index.get_loc(): non-unique Index not supported yet'
                                )
                        I._dict[val] = i
        return impl


@overload(operator.contains, no_unliteral=True)
def index_contains(I, val):
    if not is_index_type(I):
        return
    if isinstance(I, RangeIndexType):
        return lambda I, val: range_contains(I.start, I.stop, I.step, val)
    if isinstance(I, CategoricalIndexType):

        def impl(I, val):
            key = bodo.utils.conversion.unbox_if_timestamp(val)
            if not is_null_value(I._dict):
                _init_engine(I, False)
                req__chq = bodo.utils.conversion.coerce_to_array(I)
                erfpm__jljb = (bodo.hiframes.pd_categorical_ext.
                    get_code_for_value(req__chq.dtype, key))
                return erfpm__jljb in I._dict
            else:
                dtkf__ypq = (
                    'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                    )
                warnings.warn(dtkf__ypq)
                req__chq = bodo.utils.conversion.coerce_to_array(I)
                ind = -1
                for i in range(len(req__chq)):
                    if not bodo.libs.array_kernels.isna(req__chq, i):
                        if req__chq[i] == key:
                            ind = i
            return ind != -1
        return impl

    def impl(I, val):
        key = bodo.utils.conversion.unbox_if_timestamp(val)
        if not is_null_value(I._dict):
            _init_engine(I, False)
            return key in I._dict
        else:
            dtkf__ypq = (
                'Global Index objects can be slow (pass as argument to JIT function for better performance).'
                )
            warnings.warn(dtkf__ypq)
            req__chq = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(req__chq)):
                if not bodo.libs.array_kernels.isna(req__chq, i):
                    if req__chq[i] == key:
                        ind = i
        return ind != -1
    return impl


@register_jitable
def range_contains(start, stop, step, val):
    if step > 0 and not start <= val < stop:
        return False
    if step < 0 and not stop <= val < start:
        return False
    return (val - start) % step == 0


@overload_method(RangeIndexType, 'get_loc', no_unliteral=True)
@overload_method(NumericIndexType, 'get_loc', no_unliteral=True)
@overload_method(StringIndexType, 'get_loc', no_unliteral=True)
@overload_method(BinaryIndexType, 'get_loc', no_unliteral=True)
@overload_method(PeriodIndexType, 'get_loc', no_unliteral=True)
@overload_method(DatetimeIndexType, 'get_loc', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'get_loc', no_unliteral=True)
def overload_index_get_loc(I, key, method=None, tolerance=None):
    rdv__ubcq = dict(method=method, tolerance=tolerance)
    hnt__gtcv = dict(method=None, tolerance=None)
    check_unsupported_args('Index.get_loc', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    key = types.unliteral(key)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.get_loc')
    if key == pd_timestamp_type:
        key = bodo.datetime64ns
    if key == pd_timedelta_type:
        key = bodo.timedelta64ns
    if key != I.dtype:
        raise_bodo_error(
            'Index.get_loc(): invalid label type in Index.get_loc()')
    if isinstance(I, RangeIndexType):

        def impl_range(I, key, method=None, tolerance=None):
            if not range_contains(I.start, I.stop, I.step, key):
                raise KeyError('Index.get_loc(): key not found')
            return key - I.start if I.step == 1 else (key - I.start) // I.step
        return impl_range

    def impl(I, key, method=None, tolerance=None):
        key = bodo.utils.conversion.unbox_if_timestamp(key)
        if not is_null_value(I._dict):
            _init_engine(I)
            ind = I._dict.get(key, -1)
        else:
            dtkf__ypq = (
                'Index.get_loc() can be slow for global Index objects (pass as argument to JIT function for better performance).'
                )
            warnings.warn(dtkf__ypq)
            req__chq = bodo.utils.conversion.coerce_to_array(I)
            ind = -1
            for i in range(len(req__chq)):
                if req__chq[i] == key:
                    if ind != -1:
                        raise ValueError(
                            'Index.get_loc(): non-unique Index not supported yet'
                            )
                    ind = i
        if ind == -1:
            raise KeyError('Index.get_loc(): key not found')
        return ind
    return impl


def create_isna_specific_method(overload_name):

    def overload_index_isna_specific_method(I):
        yxz__izms = overload_name in {'isna', 'isnull'}
        if isinstance(I, RangeIndexType):

            def impl(I):
                numba.parfors.parfor.init_prange()
                haa__kchia = len(I)
                wirzi__rftew = np.empty(haa__kchia, np.bool_)
                for i in numba.parfors.parfor.internal_prange(haa__kchia):
                    wirzi__rftew[i] = not yxz__izms
                return wirzi__rftew
            return impl
        csxb__cig = f"""def impl(I):
    numba.parfors.parfor.init_prange()
    arr = bodo.hiframes.pd_index_ext.get_index_data(I)
    n = len(arr)
    out_arr = np.empty(n, np.bool_)
    for i in numba.parfors.parfor.internal_prange(n):
       out_arr[i] = {'' if yxz__izms else 'not '}bodo.libs.array_kernels.isna(arr, i)
    return out_arr
"""
        zxve__rey = {}
        exec(csxb__cig, {'bodo': bodo, 'np': np, 'numba': numba}, zxve__rey)
        impl = zxve__rey['impl']
        return impl
    return overload_index_isna_specific_method


isna_overload_types = (RangeIndexType, NumericIndexType, StringIndexType,
    BinaryIndexType, CategoricalIndexType, PeriodIndexType,
    DatetimeIndexType, TimedeltaIndexType)
isna_specific_methods = 'isna', 'notna', 'isnull', 'notnull'


def _install_isna_specific_methods():
    for arhas__guk in isna_overload_types:
        for overload_name in isna_specific_methods:
            overload_impl = create_isna_specific_method(overload_name)
            overload_method(arhas__guk, overload_name, no_unliteral=True,
                inline='always')(overload_impl)


_install_isna_specific_methods()


@overload_attribute(RangeIndexType, 'values')
@overload_attribute(NumericIndexType, 'values')
@overload_attribute(StringIndexType, 'values')
@overload_attribute(BinaryIndexType, 'values')
@overload_attribute(CategoricalIndexType, 'values')
@overload_attribute(PeriodIndexType, 'values')
@overload_attribute(DatetimeIndexType, 'values')
@overload_attribute(TimedeltaIndexType, 'values')
def overload_values(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I, 'Index.values'
        )
    return lambda I: bodo.utils.conversion.coerce_to_array(I)


@overload(len, no_unliteral=True)
def overload_index_len(I):
    if isinstance(I, (NumericIndexType, StringIndexType, BinaryIndexType,
        PeriodIndexType, IntervalIndexType, CategoricalIndexType,
        DatetimeIndexType, TimedeltaIndexType, HeterogeneousIndexType)):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I))


@overload(len, no_unliteral=True)
def overload_multi_index_len(I):
    if isinstance(I, MultiIndexType):
        return lambda I: len(bodo.hiframes.pd_index_ext.get_index_data(I)[0])


@overload_attribute(DatetimeIndexType, 'shape')
@overload_attribute(NumericIndexType, 'shape')
@overload_attribute(StringIndexType, 'shape')
@overload_attribute(BinaryIndexType, 'shape')
@overload_attribute(PeriodIndexType, 'shape')
@overload_attribute(TimedeltaIndexType, 'shape')
@overload_attribute(IntervalIndexType, 'shape')
@overload_attribute(CategoricalIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)),)


@overload_attribute(RangeIndexType, 'shape')
def overload_range_index_shape(s):
    return lambda s: (len(s),)


@overload_attribute(MultiIndexType, 'shape')
def overload_index_shape(s):
    return lambda s: (len(bodo.hiframes.pd_index_ext.get_index_data(s)[0]),)


@overload_attribute(NumericIndexType, 'is_monotonic', inline='always')
@overload_attribute(RangeIndexType, 'is_monotonic', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic', inline='always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic', inline='always')
@overload_attribute(NumericIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_increasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_increasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_increasing', inline=
    'always')
def overload_index_is_montonic(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.is_monotonic_increasing')
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(req__chq, 1)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step > 0 or len(I) <= 1
        return impl


@overload_attribute(NumericIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(RangeIndexType, 'is_monotonic_decreasing', inline='always')
@overload_attribute(DatetimeIndexType, 'is_monotonic_decreasing', inline=
    'always')
@overload_attribute(TimedeltaIndexType, 'is_monotonic_decreasing', inline=
    'always')
def overload_index_is_montonic_decreasing(I):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.is_monotonic_decreasing')
    if isinstance(I, (NumericIndexType, DatetimeIndexType, TimedeltaIndexType)
        ):

        def impl(I):
            req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
            return bodo.libs.array_kernels.series_monotonicity(req__chq, 2)
        return impl
    elif isinstance(I, RangeIndexType):

        def impl(I):
            return I._step < 0 or len(I) <= 1
        return impl


@overload_method(NumericIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(StringIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(PeriodIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(CategoricalIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(BinaryIndexType, 'duplicated', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'duplicated', inline='always',
    no_unliteral=True)
def overload_index_duplicated(I, keep='first'):
    if isinstance(I, RangeIndexType):

        def impl(I, keep='first'):
            return np.zeros(len(I), np.bool_)
        return impl

    def impl(I, keep='first'):
        req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
        wirzi__rftew = bodo.libs.array_kernels.duplicated((req__chq,))
        return wirzi__rftew
    return impl


@overload_method(NumericIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'any', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'any', no_unliteral=True, inline='always')
def overload_index_any(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            return len(I) > 0 and (I._start != 0 or len(I) > 1)
        return impl

    def impl(I):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_any(A)
    return impl


@overload_method(NumericIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'all', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'all', no_unliteral=True, inline='always')
def overload_index_all(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            return len(I) == 0 or I._step > 0 and (I._start > 0 or I._stop <= 0
                ) or I._step < 0 and (I._start < 0 or I._stop >= 0
                ) or I._start % I._step != 0
        return impl

    def impl(I):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(RangeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(NumericIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(StringIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(BinaryIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(CategoricalIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(PeriodIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'drop_duplicates', no_unliteral=True,
    inline='always')
def overload_index_drop_duplicates(I, keep='first'):
    rdv__ubcq = dict(keep=keep)
    hnt__gtcv = dict(keep='first')
    check_unsupported_args('Index.drop_duplicates', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):
        return lambda I, keep='first': I.copy()
    csxb__cig = """def impl(I, keep='first'):
    data = bodo.hiframes.pd_index_ext.get_index_data(I)
    arr = bodo.libs.array_kernels.drop_duplicates_array(data)
    name = bodo.hiframes.pd_index_ext.get_index_name(I)
"""
    if isinstance(I, PeriodIndexType):
        csxb__cig += f"""    return bodo.hiframes.pd_index_ext.init_period_index(arr, name, '{I.freq}')
"""
    else:
        csxb__cig += (
            '    return bodo.utils.conversion.index_from_array(arr, name)')
    zxve__rey = {}
    exec(csxb__cig, {'bodo': bodo}, zxve__rey)
    impl = zxve__rey['impl']
    return impl


@numba.generated_jit(nopython=True)
def get_index_data(S):
    return lambda S: S._data


@numba.generated_jit(nopython=True)
def get_index_name(S):
    return lambda S: S._name


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_index_data',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_datetime_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_timedelta_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_numeric_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_binary_str_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['init_categorical_index',
    'bodo.hiframes.pd_index_ext'] = alias_ext_dummy_func


def get_index_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    muck__rgar = args[0]
    if isinstance(self.typemap[muck__rgar.name], (HeterogeneousIndexType,
        MultiIndexType)):
        return None
    if equiv_set.has_shape(muck__rgar):
        return ArrayAnalysis.AnalyzeResult(shape=muck__rgar, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_index_ext_get_index_data
    ) = get_index_data_equiv


@overload_method(RangeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(NumericIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(StringIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(BinaryIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(CategoricalIndexType, 'map', inline='always', no_unliteral
    =True)
@overload_method(PeriodIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(DatetimeIndexType, 'map', inline='always', no_unliteral=True)
@overload_method(TimedeltaIndexType, 'map', inline='always', no_unliteral=True)
def overload_index_map(I, mapper, na_action=None):
    if not is_const_func_type(mapper):
        raise BodoError("Index.map(): 'mapper' should be a function")
    rdv__ubcq = dict(na_action=na_action)
    xjg__yosnj = dict(na_action=None)
    check_unsupported_args('Index.map', rdv__ubcq, xjg__yosnj, package_name
        ='pandas', module_name='Index')
    dtype = I.dtype
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'DatetimeIndex.map')
    if dtype == types.NPDatetime('ns'):
        dtype = pd_timestamp_type
    if dtype == types.NPTimedelta('ns'):
        dtype = pd_timedelta_type
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = dtype.elem_type
    hew__kgd = numba.core.registry.cpu_target.typing_context
    nomh__ocsk = numba.core.registry.cpu_target.target_context
    try:
        jtlk__ibeau = get_const_func_output_type(mapper, (dtype,), {},
            hew__kgd, nomh__ocsk)
    except Exception as hldb__kvg:
        raise_bodo_error(get_udf_error_msg('Index.map()', hldb__kvg))
    jmpq__sqwb = get_udf_out_arr_type(jtlk__ibeau)
    func = get_overload_const_func(mapper, None)
    csxb__cig = 'def f(I, mapper, na_action=None):\n'
    csxb__cig += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    csxb__cig += '  A = bodo.utils.conversion.coerce_to_array(I)\n'
    csxb__cig += '  numba.parfors.parfor.init_prange()\n'
    csxb__cig += '  n = len(A)\n'
    csxb__cig += '  S = bodo.utils.utils.alloc_type(n, _arr_typ, (-1,))\n'
    csxb__cig += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    csxb__cig += '    t2 = bodo.utils.conversion.box_if_dt64(A[i])\n'
    csxb__cig += '    v = map_func(t2)\n'
    csxb__cig += '    S[i] = bodo.utils.conversion.unbox_if_timestamp(v)\n'
    csxb__cig += '  return bodo.utils.conversion.index_from_array(S, name)\n'
    gug__hvfw = bodo.compiler.udf_jit(func)
    zxve__rey = {}
    exec(csxb__cig, {'numba': numba, 'np': np, 'pd': pd, 'bodo': bodo,
        'map_func': gug__hvfw, '_arr_typ': jmpq__sqwb, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'data_arr_type': jmpq__sqwb.dtype
        }, zxve__rey)
    f = zxve__rey['f']
    return f


@lower_builtin(operator.is_, NumericIndexType, NumericIndexType)
@lower_builtin(operator.is_, StringIndexType, StringIndexType)
@lower_builtin(operator.is_, BinaryIndexType, BinaryIndexType)
@lower_builtin(operator.is_, PeriodIndexType, PeriodIndexType)
@lower_builtin(operator.is_, DatetimeIndexType, DatetimeIndexType)
@lower_builtin(operator.is_, TimedeltaIndexType, TimedeltaIndexType)
@lower_builtin(operator.is_, IntervalIndexType, IntervalIndexType)
@lower_builtin(operator.is_, CategoricalIndexType, CategoricalIndexType)
def index_is(context, builder, sig, args):
    ceq__nufho, fwouo__och = sig.args
    if ceq__nufho != fwouo__och:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return a._data is b._data and a._name is b._name
    return context.compile_internal(builder, index_is_impl, sig, args)


@lower_builtin(operator.is_, RangeIndexType, RangeIndexType)
def range_index_is(context, builder, sig, args):
    ceq__nufho, fwouo__och = sig.args
    if ceq__nufho != fwouo__och:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._start == b._start and a._stop == b._stop and a._step ==
            b._step and a._name is b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)


def create_binary_op_overload(op):

    def overload_index_binary_op(lhs, rhs):
        if is_index_type(lhs):
            csxb__cig = (
                'def impl(lhs, rhs):\n  arr = bodo.utils.conversion.coerce_to_array(lhs)\n'
                )
            if rhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                csxb__cig += """  dt = bodo.utils.conversion.unbox_if_timestamp(rhs)
  return op(arr, dt)
"""
            else:
                csxb__cig += """  rhs_arr = bodo.utils.conversion.get_array_if_series_or_index(rhs)
  return op(arr, rhs_arr)
"""
            zxve__rey = {}
            exec(csxb__cig, {'bodo': bodo, 'op': op}, zxve__rey)
            impl = zxve__rey['impl']
            return impl
        if is_index_type(rhs):
            csxb__cig = (
                'def impl(lhs, rhs):\n  arr = bodo.utils.conversion.coerce_to_array(rhs)\n'
                )
            if lhs in [bodo.hiframes.pd_timestamp_ext.pd_timestamp_type,
                bodo.hiframes.pd_timestamp_ext.pd_timedelta_type]:
                csxb__cig += """  dt = bodo.utils.conversion.unbox_if_timestamp(lhs)
  return op(dt, arr)
"""
            else:
                csxb__cig += """  lhs_arr = bodo.utils.conversion.get_array_if_series_or_index(lhs)
  return op(lhs_arr, arr)
"""
            zxve__rey = {}
            exec(csxb__cig, {'bodo': bodo, 'op': op}, zxve__rey)
            impl = zxve__rey['impl']
            return impl
        if isinstance(lhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(lhs.data):

                def impl3(lhs, rhs):
                    data = bodo.utils.conversion.coerce_to_array(lhs)
                    req__chq = bodo.utils.conversion.coerce_to_array(data)
                    bxjnc__hkvvx = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    wirzi__rftew = op(req__chq, bxjnc__hkvvx)
                    return wirzi__rftew
                return impl3
            count = len(lhs.data.types)
            csxb__cig = 'def f(lhs, rhs):\n'
            csxb__cig += '  return [{}]\n'.format(','.join(
                'op(lhs[{}], rhs{})'.format(i, f'[{i}]' if is_iterable_type
                (rhs) else '') for i in range(count)))
            zxve__rey = {}
            exec(csxb__cig, {'op': op, 'np': np}, zxve__rey)
            impl = zxve__rey['f']
            return impl
        if isinstance(rhs, HeterogeneousIndexType):
            if not is_heterogeneous_tuple_type(rhs.data):

                def impl4(lhs, rhs):
                    data = bodo.hiframes.pd_index_ext.get_index_data(rhs)
                    req__chq = bodo.utils.conversion.coerce_to_array(data)
                    bxjnc__hkvvx = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    wirzi__rftew = op(bxjnc__hkvvx, req__chq)
                    return wirzi__rftew
                return impl4
            count = len(rhs.data.types)
            csxb__cig = 'def f(lhs, rhs):\n'
            csxb__cig += '  return [{}]\n'.format(','.join(
                'op(lhs{}, rhs[{}])'.format(f'[{i}]' if is_iterable_type(
                lhs) else '', i) for i in range(count)))
            zxve__rey = {}
            exec(csxb__cig, {'op': op, 'np': np}, zxve__rey)
            impl = zxve__rey['f']
            return impl
    return overload_index_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        overload_impl = create_binary_op_overload(op)
        overload(op, inline='always')(overload_impl)


_install_binary_ops()


def is_index_type(t):
    return isinstance(t, (RangeIndexType, NumericIndexType, StringIndexType,
        BinaryIndexType, PeriodIndexType, DatetimeIndexType,
        TimedeltaIndexType, IntervalIndexType, CategoricalIndexType))


@lower_cast(RangeIndexType, NumericIndexType)
def cast_range_index_to_int_index(context, builder, fromty, toty, val):
    f = lambda I: init_numeric_index(np.arange(I._start, I._stop, I._step),
        bodo.hiframes.pd_index_ext.get_index_name(I))
    return context.compile_internal(builder, f, toty(fromty), [val])


@numba.njit(no_cpython_wrapper=True)
def range_index_to_numeric(I):
    return init_numeric_index(np.arange(I._start, I._stop, I._step), bodo.
        hiframes.pd_index_ext.get_index_name(I))


class HeterogeneousIndexType(types.Type):
    ndim = 1

    def __init__(self, data=None, name_typ=None):
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        self.name_typ = name_typ
        super(HeterogeneousIndexType, self).__init__(name=
            f'heter_index({data}, {name_typ})')

    def copy(self):
        return HeterogeneousIndexType(self.data, self.name_typ)

    @property
    def key(self):
        return self.data, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def pandas_type_name(self):
        return 'object'

    @property
    def numpy_type_name(self):
        return 'object'


@register_model(HeterogeneousIndexType)
class HeterogeneousIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zqxbb__dam = [('data', fe_type.data), ('name', fe_type.name_typ)]
        super(HeterogeneousIndexModel, self).__init__(dmm, fe_type, zqxbb__dam)


make_attribute_wrapper(HeterogeneousIndexType, 'data', '_data')
make_attribute_wrapper(HeterogeneousIndexType, 'name', '_name')


@overload_method(HeterogeneousIndexType, 'copy', no_unliteral=True)
def overload_heter_index_copy(A, name=None, deep=False, dtype=None, names=None
    ):
    pyn__hdgii = idx_typ_to_format_str_map[HeterogeneousIndexType].format(
        'copy()')
    praj__uikjl = dict(deep=deep, dtype=dtype, names=names)
    check_unsupported_args('Index.copy', praj__uikjl, idx_cpy_arg_defaults,
        fn_str=pyn__hdgii, package_name='pandas', module_name='Index')
    if not is_overload_none(name):

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), name)
    else:

        def impl(A, name=None, deep=False, dtype=None, names=None):
            return bodo.hiframes.pd_index_ext.init_numeric_index(A._data.
                copy(), A._name)
    return impl


@box(HeterogeneousIndexType)
def box_heter_index(typ, val, c):
    dgt__ygbwa = c.context.insert_const_string(c.builder.module, 'pandas')
    akli__zdymk = c.pyapi.import_module_noblock(dgt__ygbwa)
    rxl__bsb = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, typ.data, rxl__bsb.data)
    qrox__vnh = c.pyapi.from_native_value(typ.data, rxl__bsb.data, c.
        env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, rxl__bsb.name)
    ldf__kwktb = c.pyapi.from_native_value(typ.name_typ, rxl__bsb.name, c.
        env_manager)
    whjws__xfx = c.pyapi.make_none()
    cig__cnffu = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    yfb__aacnr = c.pyapi.call_method(akli__zdymk, 'Index', (qrox__vnh,
        whjws__xfx, cig__cnffu, ldf__kwktb))
    c.pyapi.decref(qrox__vnh)
    c.pyapi.decref(whjws__xfx)
    c.pyapi.decref(cig__cnffu)
    c.pyapi.decref(ldf__kwktb)
    c.pyapi.decref(akli__zdymk)
    c.context.nrt.decref(c.builder, typ, val)
    return yfb__aacnr


@intrinsic
def init_heter_index(typingctx, data, name=None):
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        assert len(args) == 2
        adbzk__dpgss = signature.return_type
        rxl__bsb = cgutils.create_struct_proxy(adbzk__dpgss)(context, builder)
        rxl__bsb.data = args[0]
        rxl__bsb.name = args[1]
        context.nrt.incref(builder, adbzk__dpgss.data, args[0])
        context.nrt.incref(builder, adbzk__dpgss.name_typ, args[1])
        return rxl__bsb._getvalue()
    return HeterogeneousIndexType(data, name)(data, name), codegen


@overload_attribute(HeterogeneousIndexType, 'name')
def heter_index_get_name(i):

    def impl(i):
        return i._name
    return impl


@overload_attribute(NumericIndexType, 'nbytes')
@overload_attribute(DatetimeIndexType, 'nbytes')
@overload_attribute(TimedeltaIndexType, 'nbytes')
@overload_attribute(RangeIndexType, 'nbytes')
@overload_attribute(StringIndexType, 'nbytes')
@overload_attribute(BinaryIndexType, 'nbytes')
@overload_attribute(CategoricalIndexType, 'nbytes')
@overload_attribute(PeriodIndexType, 'nbytes')
def overload_nbytes(I):
    if isinstance(I, RangeIndexType):

        def _impl_nbytes(I):
            return bodo.io.np_io.get_dtype_size(type(I._start)
                ) + bodo.io.np_io.get_dtype_size(type(I._step)
                ) + bodo.io.np_io.get_dtype_size(type(I._stop))
        return _impl_nbytes
    else:

        def _impl_nbytes(I):
            return I._data.nbytes
        return _impl_nbytes


@overload_method(NumericIndexType, 'to_series', inline='always')
@overload_method(DatetimeIndexType, 'to_series', inline='always')
@overload_method(TimedeltaIndexType, 'to_series', inline='always')
@overload_method(RangeIndexType, 'to_series', inline='always')
@overload_method(StringIndexType, 'to_series', inline='always')
@overload_method(BinaryIndexType, 'to_series', inline='always')
@overload_method(CategoricalIndexType, 'to_series', inline='always')
def overload_index_to_series(I, index=None, name=None):
    if not (is_overload_constant_str(name) or is_overload_constant_int(name
        ) or is_overload_none(name)):
        raise_bodo_error(
            f'Index.to_series(): only constant string/int are supported for argument name'
            )
    if is_overload_none(name):
        snjuv__wye = 'bodo.hiframes.pd_index_ext.get_index_name(I)'
    else:
        snjuv__wye = 'name'
    csxb__cig = 'def impl(I, index=None, name=None):\n'
    csxb__cig += '    data = bodo.utils.conversion.index_to_array(I)\n'
    if is_overload_none(index):
        csxb__cig += '    new_index = I\n'
    elif is_pd_index_type(index):
        csxb__cig += '    new_index = index\n'
    elif isinstance(index, SeriesType):
        csxb__cig += '    arr = bodo.utils.conversion.coerce_to_array(index)\n'
        csxb__cig += (
            '    index_name = bodo.hiframes.pd_series_ext.get_series_name(index)\n'
            )
        csxb__cig += (
            '    new_index = bodo.utils.conversion.index_from_array(arr, index_name)\n'
            )
    elif bodo.utils.utils.is_array_typ(index, False):
        csxb__cig += (
            '    new_index = bodo.utils.conversion.index_from_array(index)\n')
    elif isinstance(index, (types.List, types.BaseTuple)):
        csxb__cig += '    arr = bodo.utils.conversion.coerce_to_array(index)\n'
        csxb__cig += (
            '    new_index = bodo.utils.conversion.index_from_array(arr)\n')
    else:
        raise_bodo_error(
            f'Index.to_series(): unsupported type for argument index: {type(index).__name__}'
            )
    csxb__cig += f'    new_name = {snjuv__wye}\n'
    csxb__cig += (
        '    return bodo.hiframes.pd_series_ext.init_series(data, new_index, new_name)'
        )
    zxve__rey = {}
    exec(csxb__cig, {'bodo': bodo, 'np': np}, zxve__rey)
    impl = zxve__rey['impl']
    return impl


@overload_method(NumericIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(DatetimeIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(TimedeltaIndexType, 'to_frame', inline='always',
    no_unliteral=True)
@overload_method(RangeIndexType, 'to_frame', inline='always', no_unliteral=True
    )
@overload_method(StringIndexType, 'to_frame', inline='always', no_unliteral
    =True)
@overload_method(BinaryIndexType, 'to_frame', inline='always', no_unliteral
    =True)
@overload_method(CategoricalIndexType, 'to_frame', inline='always',
    no_unliteral=True)
def overload_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        dar__lqaya = 'I'
    elif is_overload_false(index):
        dar__lqaya = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'Index.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'Index.to_frame(): index argument must be a compile time constant')
    csxb__cig = 'def impl(I, index=True, name=None):\n'
    csxb__cig += '    data = bodo.utils.conversion.index_to_array(I)\n'
    csxb__cig += f'    new_index = {dar__lqaya}\n'
    if is_overload_none(name) and I.name_typ == types.none:
        rytb__yecyw = ColNamesMetaType((0,))
    elif is_overload_none(name):
        rytb__yecyw = ColNamesMetaType((I.name_typ,))
    elif is_overload_constant_str(name):
        rytb__yecyw = ColNamesMetaType((get_overload_const_str(name),))
    elif is_overload_constant_int(name):
        rytb__yecyw = ColNamesMetaType((get_overload_const_int(name),))
    else:
        raise_bodo_error(
            f'Index.to_frame(): only constant string/int are supported for argument name'
            )
    csxb__cig += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((data,), new_index, __col_name_meta_value)
"""
    zxve__rey = {}
    exec(csxb__cig, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        rytb__yecyw}, zxve__rey)
    impl = zxve__rey['impl']
    return impl


@overload_method(MultiIndexType, 'to_frame', inline='always', no_unliteral=True
    )
def overload_multi_index_to_frame(I, index=True, name=None):
    if is_overload_true(index):
        dar__lqaya = 'I'
    elif is_overload_false(index):
        dar__lqaya = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(I), 1, None)')
    elif not isinstance(index, types.Boolean):
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a constant boolean')
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): index argument must be a compile time constant'
            )
    csxb__cig = 'def impl(I, index=True, name=None):\n'
    csxb__cig += '    data = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    csxb__cig += f'    new_index = {dar__lqaya}\n'
    wkn__rupe = len(I.array_types)
    if is_overload_none(name) and I.names_typ == (types.none,) * wkn__rupe:
        rytb__yecyw = ColNamesMetaType(tuple(range(wkn__rupe)))
    elif is_overload_none(name):
        rytb__yecyw = ColNamesMetaType(I.names_typ)
    elif is_overload_constant_tuple(name) or is_overload_constant_list(name):
        if is_overload_constant_list(name):
            names = tuple(get_overload_const_list(name))
        else:
            names = get_overload_const_tuple(name)
        if wkn__rupe != len(names):
            raise_bodo_error(
                f'MultiIndex.to_frame(): expected {wkn__rupe} names, not {len(names)}'
                )
        if all(is_overload_constant_str(sjyz__tzp) or
            is_overload_constant_int(sjyz__tzp) for sjyz__tzp in names):
            rytb__yecyw = ColNamesMetaType(names)
        else:
            raise_bodo_error(
                'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
                )
    else:
        raise_bodo_error(
            'MultiIndex.to_frame(): only constant string/int list/tuple are supported for argument name'
            )
    csxb__cig += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(data, new_index, __col_name_meta_value,)
"""
    zxve__rey = {}
    exec(csxb__cig, {'bodo': bodo, 'np': np, '__col_name_meta_value':
        rytb__yecyw}, zxve__rey)
    impl = zxve__rey['impl']
    return impl


@overload_method(NumericIndexType, 'to_numpy', inline='always')
@overload_method(DatetimeIndexType, 'to_numpy', inline='always')
@overload_method(TimedeltaIndexType, 'to_numpy', inline='always')
@overload_method(RangeIndexType, 'to_numpy', inline='always')
@overload_method(StringIndexType, 'to_numpy', inline='always')
@overload_method(BinaryIndexType, 'to_numpy', inline='always')
@overload_method(CategoricalIndexType, 'to_numpy', inline='always')
@overload_method(IntervalIndexType, 'to_numpy', inline='always')
def overload_index_to_numpy(I, dtype=None, copy=False, na_value=None):
    rdv__ubcq = dict(dtype=dtype, na_value=na_value)
    hnt__gtcv = dict(dtype=None, na_value=None)
    check_unsupported_args('Index.to_numpy', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    if not is_overload_bool(copy):
        raise_bodo_error('Index.to_numpy(): copy argument must be a boolean')
    if isinstance(I, RangeIndexType):

        def impl(I, dtype=None, copy=False, na_value=None):
            return np.arange(I._start, I._stop, I._step)
        return impl
    if is_overload_true(copy):

        def impl(I, dtype=None, copy=False, na_value=None):
            return bodo.hiframes.pd_index_ext.get_index_data(I).copy()
        return impl
    if is_overload_false(copy):

        def impl(I, dtype=None, copy=False, na_value=None):
            return bodo.hiframes.pd_index_ext.get_index_data(I)
        return impl

    def impl(I, dtype=None, copy=False, na_value=None):
        data = bodo.hiframes.pd_index_ext.get_index_data(I)
        return data.copy() if copy else data
    return impl


@overload_method(NumericIndexType, 'to_list', inline='always')
@overload_method(RangeIndexType, 'to_list', inline='always')
@overload_method(StringIndexType, 'to_list', inline='always')
@overload_method(BinaryIndexType, 'to_list', inline='always')
@overload_method(CategoricalIndexType, 'to_list', inline='always')
@overload_method(DatetimeIndexType, 'to_list', inline='always')
@overload_method(TimedeltaIndexType, 'to_list', inline='always')
@overload_method(NumericIndexType, 'tolist', inline='always')
@overload_method(RangeIndexType, 'tolist', inline='always')
@overload_method(StringIndexType, 'tolist', inline='always')
@overload_method(BinaryIndexType, 'tolist', inline='always')
@overload_method(CategoricalIndexType, 'tolist', inline='always')
@overload_method(DatetimeIndexType, 'tolist', inline='always')
@overload_method(TimedeltaIndexType, 'tolist', inline='always')
def overload_index_to_list(I):
    if isinstance(I, RangeIndexType):

        def impl(I):
            abd__raz = list()
            for i in range(I._start, I._stop, I.step):
                abd__raz.append(i)
            return abd__raz
        return impl

    def impl(I):
        abd__raz = list()
        for i in range(len(I)):
            abd__raz.append(I[i])
        return abd__raz
    return impl


@overload_attribute(NumericIndexType, 'T')
@overload_attribute(DatetimeIndexType, 'T')
@overload_attribute(TimedeltaIndexType, 'T')
@overload_attribute(RangeIndexType, 'T')
@overload_attribute(StringIndexType, 'T')
@overload_attribute(BinaryIndexType, 'T')
@overload_attribute(CategoricalIndexType, 'T')
@overload_attribute(PeriodIndexType, 'T')
@overload_attribute(MultiIndexType, 'T')
@overload_attribute(IntervalIndexType, 'T')
def overload_T(I):
    return lambda I: I


@overload_attribute(NumericIndexType, 'size')
@overload_attribute(DatetimeIndexType, 'size')
@overload_attribute(TimedeltaIndexType, 'size')
@overload_attribute(RangeIndexType, 'size')
@overload_attribute(StringIndexType, 'size')
@overload_attribute(BinaryIndexType, 'size')
@overload_attribute(CategoricalIndexType, 'size')
@overload_attribute(PeriodIndexType, 'size')
@overload_attribute(MultiIndexType, 'size')
@overload_attribute(IntervalIndexType, 'size')
def overload_size(I):
    return lambda I: len(I)


@overload_attribute(NumericIndexType, 'ndim')
@overload_attribute(DatetimeIndexType, 'ndim')
@overload_attribute(TimedeltaIndexType, 'ndim')
@overload_attribute(RangeIndexType, 'ndim')
@overload_attribute(StringIndexType, 'ndim')
@overload_attribute(BinaryIndexType, 'ndim')
@overload_attribute(CategoricalIndexType, 'ndim')
@overload_attribute(PeriodIndexType, 'ndim')
@overload_attribute(MultiIndexType, 'ndim')
@overload_attribute(IntervalIndexType, 'ndim')
def overload_ndim(I):
    return lambda I: 1


@overload_attribute(NumericIndexType, 'nlevels')
@overload_attribute(DatetimeIndexType, 'nlevels')
@overload_attribute(TimedeltaIndexType, 'nlevels')
@overload_attribute(RangeIndexType, 'nlevels')
@overload_attribute(StringIndexType, 'nlevels')
@overload_attribute(BinaryIndexType, 'nlevels')
@overload_attribute(CategoricalIndexType, 'nlevels')
@overload_attribute(PeriodIndexType, 'nlevels')
@overload_attribute(MultiIndexType, 'nlevels')
@overload_attribute(IntervalIndexType, 'nlevels')
def overload_nlevels(I):
    if isinstance(I, MultiIndexType):
        return lambda I: len(I._data)
    return lambda I: 1


@overload_attribute(NumericIndexType, 'empty')
@overload_attribute(DatetimeIndexType, 'empty')
@overload_attribute(TimedeltaIndexType, 'empty')
@overload_attribute(RangeIndexType, 'empty')
@overload_attribute(StringIndexType, 'empty')
@overload_attribute(BinaryIndexType, 'empty')
@overload_attribute(CategoricalIndexType, 'empty')
@overload_attribute(PeriodIndexType, 'empty')
@overload_attribute(MultiIndexType, 'empty')
@overload_attribute(IntervalIndexType, 'empty')
def overload_empty(I):
    return lambda I: len(I) == 0


@overload_attribute(NumericIndexType, 'is_all_dates')
@overload_attribute(DatetimeIndexType, 'is_all_dates')
@overload_attribute(TimedeltaIndexType, 'is_all_dates')
@overload_attribute(RangeIndexType, 'is_all_dates')
@overload_attribute(StringIndexType, 'is_all_dates')
@overload_attribute(BinaryIndexType, 'is_all_dates')
@overload_attribute(CategoricalIndexType, 'is_all_dates')
@overload_attribute(PeriodIndexType, 'is_all_dates')
@overload_attribute(MultiIndexType, 'is_all_dates')
@overload_attribute(IntervalIndexType, 'is_all_dates')
def overload_is_all_dates(I):
    if isinstance(I, (DatetimeIndexType, TimedeltaIndexType, PeriodIndexType)):
        return lambda I: True
    else:
        return lambda I: False


@overload_attribute(NumericIndexType, 'inferred_type')
@overload_attribute(DatetimeIndexType, 'inferred_type')
@overload_attribute(TimedeltaIndexType, 'inferred_type')
@overload_attribute(RangeIndexType, 'inferred_type')
@overload_attribute(StringIndexType, 'inferred_type')
@overload_attribute(BinaryIndexType, 'inferred_type')
@overload_attribute(CategoricalIndexType, 'inferred_type')
@overload_attribute(PeriodIndexType, 'inferred_type')
@overload_attribute(MultiIndexType, 'inferred_type')
@overload_attribute(IntervalIndexType, 'inferred_type')
def overload_inferred_type(I):
    if isinstance(I, NumericIndexType):
        if isinstance(I.dtype, types.Integer):
            return lambda I: 'integer'
        elif isinstance(I.dtype, types.Float):
            return lambda I: 'floating'
        elif isinstance(I.dtype, types.Boolean):
            return lambda I: 'boolean'
        return
    if isinstance(I, StringIndexType):

        def impl(I):
            if len(I._data) == 0:
                return 'empty'
            return 'string'
        return impl
    ofu__lfx = {DatetimeIndexType: 'datetime64', TimedeltaIndexType:
        'timedelta64', RangeIndexType: 'integer', BinaryIndexType: 'bytes',
        CategoricalIndexType: 'categorical', PeriodIndexType: 'period',
        IntervalIndexType: 'interval', MultiIndexType: 'mixed'}
    inferred_type = ofu__lfx[type(I)]
    return lambda I: inferred_type


@overload_attribute(NumericIndexType, 'dtype')
@overload_attribute(DatetimeIndexType, 'dtype')
@overload_attribute(TimedeltaIndexType, 'dtype')
@overload_attribute(RangeIndexType, 'dtype')
@overload_attribute(StringIndexType, 'dtype')
@overload_attribute(BinaryIndexType, 'dtype')
@overload_attribute(CategoricalIndexType, 'dtype')
@overload_attribute(MultiIndexType, 'dtype')
def overload_inferred_type(I):
    if isinstance(I, NumericIndexType):
        if isinstance(I.dtype, types.Boolean):
            return lambda I: np.dtype('O')
        dtype = I.dtype
        return lambda I: dtype
    if isinstance(I, CategoricalIndexType):
        dtype = bodo.utils.utils.create_categorical_type(I.dtype.categories,
            I.data, I.dtype.ordered)
        return lambda I: dtype
    uwxz__zcvcm = {DatetimeIndexType: np.dtype('datetime64[ns]'),
        TimedeltaIndexType: np.dtype('timedelta64[ns]'), RangeIndexType: np
        .dtype('int64'), StringIndexType: np.dtype('O'), BinaryIndexType:
        np.dtype('O'), MultiIndexType: np.dtype('O')}
    dtype = uwxz__zcvcm[type(I)]
    return lambda I: dtype


@overload_attribute(NumericIndexType, 'names')
@overload_attribute(DatetimeIndexType, 'names')
@overload_attribute(TimedeltaIndexType, 'names')
@overload_attribute(RangeIndexType, 'names')
@overload_attribute(StringIndexType, 'names')
@overload_attribute(BinaryIndexType, 'names')
@overload_attribute(CategoricalIndexType, 'names')
@overload_attribute(IntervalIndexType, 'names')
@overload_attribute(PeriodIndexType, 'names')
@overload_attribute(MultiIndexType, 'names')
def overload_names(I):
    if isinstance(I, MultiIndexType):
        return lambda I: I._names
    return lambda I: (I._name,)


@overload_method(NumericIndexType, 'rename', inline='always')
@overload_method(DatetimeIndexType, 'rename', inline='always')
@overload_method(TimedeltaIndexType, 'rename', inline='always')
@overload_method(RangeIndexType, 'rename', inline='always')
@overload_method(StringIndexType, 'rename', inline='always')
@overload_method(BinaryIndexType, 'rename', inline='always')
@overload_method(CategoricalIndexType, 'rename', inline='always')
@overload_method(PeriodIndexType, 'rename', inline='always')
@overload_method(IntervalIndexType, 'rename', inline='always')
@overload_method(HeterogeneousIndexType, 'rename', inline='always')
def overload_rename(I, name, inplace=False):
    if is_overload_true(inplace):
        raise BodoError('Index.rename(): inplace index renaming unsupported')
    return init_index_from_index(I, name)


def init_index_from_index(I, name):
    tis__cwv = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index}
    if type(I) in tis__cwv:
        init_func = tis__cwv[type(I)]
        return lambda I, name, inplace=False: init_func(bodo.hiframes.
            pd_index_ext.get_index_data(I).copy(), name)
    if isinstance(I, RangeIndexType):
        return lambda I, name, inplace=False: I.copy(name=name)
    if isinstance(I, PeriodIndexType):
        freq = I.freq
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_period_index(bodo.hiframes.pd_index_ext.get_index_data(I).
            copy(), name, freq))
    if isinstance(I, HeterogeneousIndexType):
        return (lambda I, name, inplace=False: bodo.hiframes.pd_index_ext.
            init_heter_index(bodo.hiframes.pd_index_ext.get_index_data(I),
            name))
    raise_bodo_error(f'init_index(): Unknown type {type(I)}')


def get_index_constructor(I):
    vnd__ousjr = {NumericIndexType: bodo.hiframes.pd_index_ext.
        init_numeric_index, DatetimeIndexType: bodo.hiframes.pd_index_ext.
        init_datetime_index, TimedeltaIndexType: bodo.hiframes.pd_index_ext
        .init_timedelta_index, StringIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, BinaryIndexType: bodo.hiframes.pd_index_ext.
        init_binary_str_index, CategoricalIndexType: bodo.hiframes.
        pd_index_ext.init_categorical_index, IntervalIndexType: bodo.
        hiframes.pd_index_ext.init_interval_index, RangeIndexType: bodo.
        hiframes.pd_index_ext.init_range_index}
    if type(I) in vnd__ousjr:
        return vnd__ousjr[type(I)]
    raise BodoError(
        f'Unsupported type for standard Index constructor: {type(I)}')


@overload_method(NumericIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'min', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'min', no_unliteral=True, inline=
    'always')
def overload_index_min(I, axis=None, skipna=True):
    rdv__ubcq = dict(axis=axis, skipna=skipna)
    hnt__gtcv = dict(axis=None, skipna=True)
    check_unsupported_args('Index.min', rdv__ubcq, hnt__gtcv, package_name=
        'pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            iwd__llsv = len(I)
            if iwd__llsv == 0:
                return np.nan
            if I._step < 0:
                return I._start + I._step * (iwd__llsv - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.min(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_min(req__chq)
    return impl


@overload_method(NumericIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(RangeIndexType, 'max', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'max', no_unliteral=True, inline=
    'always')
def overload_index_max(I, axis=None, skipna=True):
    rdv__ubcq = dict(axis=axis, skipna=skipna)
    hnt__gtcv = dict(axis=None, skipna=True)
    check_unsupported_args('Index.max', rdv__ubcq, hnt__gtcv, package_name=
        'pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=None, skipna=True):
            iwd__llsv = len(I)
            if iwd__llsv == 0:
                return np.nan
            if I._step > 0:
                return I._start + I._step * (iwd__llsv - 1)
            else:
                return I._start
        return impl
    if isinstance(I, CategoricalIndexType):
        if not I.dtype.ordered:
            raise BodoError(
                'Index.max(): only ordered categoricals are possible')

    def impl(I, axis=None, skipna=True):
        req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
        return bodo.libs.array_ops.array_op_max(req__chq)
    return impl


@overload_method(NumericIndexType, 'argmin', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'argmin', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'argmin', no_unliteral=True, inline='always')
@overload_method(PeriodIndexType, 'argmin', no_unliteral=True, inline='always')
def overload_index_argmin(I, axis=0, skipna=True):
    rdv__ubcq = dict(axis=axis, skipna=skipna)
    hnt__gtcv = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmin', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.argmin()')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, skipna=True):
            return (I._step < 0) * (len(I) - 1)
        return impl
    if isinstance(I, CategoricalIndexType) and not I.dtype.ordered:
        raise BodoError(
            'Index.argmin(): only ordered categoricals are possible')

    def impl(I, axis=0, skipna=True):
        req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = init_numeric_index(np.arange(len(req__chq)))
        return bodo.libs.array_ops.array_op_idxmin(req__chq, index)
    return impl


@overload_method(NumericIndexType, 'argmax', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'argmax', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'argmax', no_unliteral=True, inline=
    'always')
@overload_method(PeriodIndexType, 'argmax', no_unliteral=True, inline='always')
def overload_index_argmax(I, axis=0, skipna=True):
    rdv__ubcq = dict(axis=axis, skipna=skipna)
    hnt__gtcv = dict(axis=0, skipna=True)
    check_unsupported_args('Index.argmax', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.argmax()')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, skipna=True):
            return (I._step > 0) * (len(I) - 1)
        return impl
    if isinstance(I, CategoricalIndexType) and not I.dtype.ordered:
        raise BodoError(
            'Index.argmax(): only ordered categoricals are possible')

    def impl(I, axis=0, skipna=True):
        req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
        index = np.arange(len(req__chq))
        return bodo.libs.array_ops.array_op_idxmax(req__chq, index)
    return impl


@overload_method(NumericIndexType, 'unique', no_unliteral=True, inline='always'
    )
@overload_method(BinaryIndexType, 'unique', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'unique', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(IntervalIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(DatetimeIndexType, 'unique', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'unique', no_unliteral=True, inline=
    'always')
def overload_index_unique(I):
    nusq__twalo = get_index_constructor(I)

    def impl(I):
        req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = bodo.hiframes.pd_index_ext.get_index_name(I)
        jezp__jnbr = bodo.libs.array_kernels.unique(req__chq)
        return nusq__twalo(jezp__jnbr, name)
    return impl


@overload_method(RangeIndexType, 'unique', no_unliteral=True, inline='always')
def overload_range_index_unique(I):

    def impl(I):
        return I.copy()
    return impl


@overload_method(NumericIndexType, 'nunique', inline='always')
@overload_method(BinaryIndexType, 'nunique', inline='always')
@overload_method(StringIndexType, 'nunique', inline='always')
@overload_method(CategoricalIndexType, 'nunique', inline='always')
@overload_method(DatetimeIndexType, 'nunique', inline='always')
@overload_method(TimedeltaIndexType, 'nunique', inline='always')
@overload_method(PeriodIndexType, 'nunique', inline='always')
def overload_index_nunique(I, dropna=True):

    def impl(I, dropna=True):
        req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
        haa__kchia = bodo.libs.array_kernels.nunique(req__chq, dropna)
        return haa__kchia
    return impl


@overload_method(RangeIndexType, 'nunique', inline='always')
def overload_range_index_nunique(I, dropna=True):

    def impl(I, dropna=True):
        start = I._start
        stop = I._stop
        step = I._step
        return max(0, -(-(stop - start) // step))
    return impl


@overload_method(NumericIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'isin', no_unliteral=True, inline='always')
@overload_method(TimedeltaIndexType, 'isin', no_unliteral=True, inline='always'
    )
def overload_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            noza__tsiu = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_index_ext.get_index_data(I)
            haa__kchia = len(A)
            wirzi__rftew = np.empty(haa__kchia, np.bool_)
            bodo.libs.array.array_isin(wirzi__rftew, A, noza__tsiu, False)
            return wirzi__rftew
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = bodo.hiframes.pd_index_ext.get_index_data(I)
        wirzi__rftew = bodo.libs.array_ops.array_op_isin(A, values)
        return wirzi__rftew
    return impl


@overload_method(RangeIndexType, 'isin', no_unliteral=True, inline='always')
def overload_range_index_isin(I, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(I, values):
            noza__tsiu = bodo.utils.conversion.coerce_to_array(values)
            A = np.arange(I.start, I.stop, I.step)
            haa__kchia = len(A)
            wirzi__rftew = np.empty(haa__kchia, np.bool_)
            bodo.libs.array.array_isin(wirzi__rftew, A, noza__tsiu, False)
            return wirzi__rftew
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Index.isin(): 'values' parameter should be a set or a list")

    def impl(I, values):
        A = np.arange(I.start, I.stop, I.step)
        wirzi__rftew = bodo.libs.array_ops.array_op_isin(A, values)
        return wirzi__rftew
    return impl


@register_jitable
def order_range(I, ascending):
    step = I._step
    if ascending == (step > 0):
        return I.copy()
    else:
        start = I._start
        stop = I._stop
        name = get_index_name(I)
        iwd__llsv = len(I)
        yemy__abzbk = start + step * (iwd__llsv - 1)
        kvaih__cbnb = yemy__abzbk - step * iwd__llsv
        return init_range_index(yemy__abzbk, kvaih__cbnb, -step, name)


@overload_method(NumericIndexType, 'sort_values', no_unliteral=True, inline
    ='always')
@overload_method(BinaryIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
@overload_method(StringIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(DatetimeIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(TimedeltaIndexType, 'sort_values', no_unliteral=True,
    inline='always')
@overload_method(RangeIndexType, 'sort_values', no_unliteral=True, inline=
    'always')
def overload_index_sort_values(I, return_indexer=False, ascending=True,
    na_position='last', key=None):
    rdv__ubcq = dict(return_indexer=return_indexer, key=key)
    hnt__gtcv = dict(return_indexer=False, key=None)
    check_unsupported_args('Index.sort_values', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Index.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Index.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    if isinstance(I, RangeIndexType):

        def impl(I, return_indexer=False, ascending=True, na_position=
            'last', key=None):
            return order_range(I, ascending)
        return impl
    nusq__twalo = get_index_constructor(I)
    hwyx__vay = ColNamesMetaType(('$_bodo_col_',))

    def impl(I, return_indexer=False, ascending=True, na_position='last',
        key=None):
        req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
        name = get_index_name(I)
        index = init_range_index(0, len(req__chq), 1, None)
        jdgb__niy = bodo.hiframes.pd_dataframe_ext.init_dataframe((req__chq
            ,), index, hwyx__vay)
        kgkl__hjd = jdgb__niy.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=False, na_position=na_position)
        wirzi__rftew = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            kgkl__hjd, 0)
        return nusq__twalo(wirzi__rftew, name)
    return impl


@overload_method(NumericIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(BinaryIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(CategoricalIndexType, 'argsort', no_unliteral=True, inline
    ='always')
@overload_method(DatetimeIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'argsort', no_unliteral=True, inline=
    'always')
@overload_method(PeriodIndexType, 'argsort', no_unliteral=True, inline='always'
    )
@overload_method(RangeIndexType, 'argsort', no_unliteral=True, inline='always')
def overload_index_argsort(I, axis=0, kind='quicksort', order=None):
    rdv__ubcq = dict(axis=axis, kind=kind, order=order)
    hnt__gtcv = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Index.argsort', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    if isinstance(I, RangeIndexType):

        def impl(I, axis=0, kind='quicksort', order=None):
            if I._step > 0:
                return np.arange(0, len(I), 1)
            else:
                return np.arange(len(I) - 1, -1, -1)
        return impl

    def impl(I, axis=0, kind='quicksort', order=None):
        req__chq = bodo.hiframes.pd_index_ext.get_index_data(I)
        wirzi__rftew = bodo.hiframes.series_impl.argsort(req__chq)
        return wirzi__rftew
    return impl


@overload_method(NumericIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(StringIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(BinaryIndexType, 'where', no_unliteral=True, inline='always')
@overload_method(DatetimeIndexType, 'where', no_unliteral=True, inline='always'
    )
@overload_method(TimedeltaIndexType, 'where', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'where', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'where', no_unliteral=True, inline='always')
def overload_index_where(I, cond, other=np.nan):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.where()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Index.where()')
    bodo.hiframes.series_impl._validate_arguments_mask_where('where',
        'Index', I, cond, other, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False)
    if is_overload_constant_nan(other):
        exjkq__orpuh = 'None'
    else:
        exjkq__orpuh = 'other'
    csxb__cig = 'def impl(I, cond, other=np.nan):\n'
    if isinstance(I, RangeIndexType):
        csxb__cig += '  arr = np.arange(I._start, I._stop, I._step)\n'
        nusq__twalo = 'init_numeric_index'
    else:
        csxb__cig += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    csxb__cig += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    csxb__cig += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {exjkq__orpuh})\n'
        )
    csxb__cig += f'  return constructor(out_arr, name)\n'
    zxve__rey = {}
    nusq__twalo = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(csxb__cig, {'bodo': bodo, 'np': np, 'constructor': nusq__twalo},
        zxve__rey)
    impl = zxve__rey['impl']
    return impl


@overload_method(NumericIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(StringIndexType, 'putmask', no_unliteral=True, inline='always'
    )
@overload_method(BinaryIndexType, 'putmask', no_unliteral=True, inline='always'
    )
@overload_method(DatetimeIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'putmask', no_unliteral=True, inline=
    'always')
@overload_method(CategoricalIndexType, 'putmask', no_unliteral=True, inline
    ='always')
@overload_method(RangeIndexType, 'putmask', no_unliteral=True, inline='always')
def overload_index_putmask(I, cond, other):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.putmask()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Index.putmask()')
    bodo.hiframes.series_impl._validate_arguments_mask_where('putmask',
        'Index', I, cond, other, inplace=False, axis=None, level=None,
        errors='raise', try_cast=False)
    if is_overload_constant_nan(other):
        exjkq__orpuh = 'None'
    else:
        exjkq__orpuh = 'other'
    csxb__cig = 'def impl(I, cond, other):\n'
    csxb__cig += '  cond = ~cond\n'
    if isinstance(I, RangeIndexType):
        csxb__cig += '  arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        csxb__cig += '  arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    csxb__cig += '  name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    csxb__cig += (
        f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {exjkq__orpuh})\n'
        )
    csxb__cig += f'  return constructor(out_arr, name)\n'
    zxve__rey = {}
    nusq__twalo = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(csxb__cig, {'bodo': bodo, 'np': np, 'constructor': nusq__twalo},
        zxve__rey)
    impl = zxve__rey['impl']
    return impl


@overload_method(NumericIndexType, 'repeat', no_unliteral=True, inline='always'
    )
@overload_method(StringIndexType, 'repeat', no_unliteral=True, inline='always')
@overload_method(CategoricalIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(DatetimeIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(TimedeltaIndexType, 'repeat', no_unliteral=True, inline=
    'always')
@overload_method(RangeIndexType, 'repeat', no_unliteral=True, inline='always')
def overload_index_repeat(I, repeats, axis=None):
    rdv__ubcq = dict(axis=axis)
    hnt__gtcv = dict(axis=None)
    check_unsupported_args('Index.repeat', rdv__ubcq, hnt__gtcv,
        package_name='pandas', module_name='Index')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(I,
        'Index.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Index.repeat(): 'repeats' should be an integer or array of integers"
            )
    csxb__cig = 'def impl(I, repeats, axis=None):\n'
    if not isinstance(repeats, types.Integer):
        csxb__cig += (
            '    repeats = bodo.utils.conversion.coerce_to_array(repeats)\n')
    if isinstance(I, RangeIndexType):
        csxb__cig += '    arr = np.arange(I._start, I._stop, I._step)\n'
    else:
        csxb__cig += '    arr = bodo.hiframes.pd_index_ext.get_index_data(I)\n'
    csxb__cig += '    name = bodo.hiframes.pd_index_ext.get_index_name(I)\n'
    csxb__cig += (
        '    out_arr = bodo.libs.array_kernels.repeat_kernel(arr, repeats)\n')
    csxb__cig += '    return constructor(out_arr, name)'
    zxve__rey = {}
    nusq__twalo = init_numeric_index if isinstance(I, RangeIndexType
        ) else get_index_constructor(I)
    exec(csxb__cig, {'bodo': bodo, 'np': np, 'constructor': nusq__twalo},
        zxve__rey)
    impl = zxve__rey['impl']
    return impl


@overload_method(NumericIndexType, 'is_integer', inline='always')
def overload_is_integer_numeric(I):
    truth = isinstance(I.dtype, types.Integer)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_floating', inline='always')
def overload_is_floating_numeric(I):
    truth = isinstance(I.dtype, types.Float)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_boolean', inline='always')
def overload_is_boolean_numeric(I):
    truth = isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_numeric', inline='always')
def overload_is_numeric_numeric(I):
    truth = not isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(NumericIndexType, 'is_object', inline='always')
def overload_is_object_numeric(I):
    truth = isinstance(I.dtype, types.Boolean)
    return lambda I: truth


@overload_method(StringIndexType, 'is_object', inline='always')
@overload_method(BinaryIndexType, 'is_object', inline='always')
@overload_method(RangeIndexType, 'is_numeric', inline='always')
@overload_method(RangeIndexType, 'is_integer', inline='always')
@overload_method(CategoricalIndexType, 'is_categorical', inline='always')
@overload_method(IntervalIndexType, 'is_interval', inline='always')
@overload_method(MultiIndexType, 'is_object', inline='always')
def overload_is_methods_true(I):
    return lambda I: True


@overload_method(NumericIndexType, 'is_categorical', inline='always')
@overload_method(NumericIndexType, 'is_interval', inline='always')
@overload_method(StringIndexType, 'is_boolean', inline='always')
@overload_method(StringIndexType, 'is_floating', inline='always')
@overload_method(StringIndexType, 'is_categorical', inline='always')
@overload_method(StringIndexType, 'is_integer', inline='always')
@overload_method(StringIndexType, 'is_interval', inline='always')
@overload_method(StringIndexType, 'is_numeric', inline='always')
@overload_method(BinaryIndexType, 'is_boolean', inline='always')
@overload_method(BinaryIndexType, 'is_floating', inline='always')
@overload_method(BinaryIndexType, 'is_categorical', inline='always')
@overload_method(BinaryIndexType, 'is_integer', inline='always')
@overload_method(BinaryIndexType, 'is_interval', inline='always')
@overload_method(BinaryIndexType, 'is_numeric', inline='always')
@overload_method(DatetimeIndexType, 'is_boolean', inline='always')
@overload_method(DatetimeIndexType, 'is_floating', inline='always')
@overload_method(DatetimeIndexType, 'is_categorical', inline='always')
@overload_method(DatetimeIndexType, 'is_integer', inline='always')
@overload_method(DatetimeIndexType, 'is_interval', inline='always')
@overload_method(DatetimeIndexType, 'is_numeric', inline='always')
@overload_method(DatetimeIndexType, 'is_object', inline='always')
@overload_method(TimedeltaIndexType, 'is_boolean', inline='always')
@overload_method(TimedeltaIndexType, 'is_floating', inline='always')
@overload_method(TimedeltaIndexType, 'is_categorical', inline='always')
@overload_method(TimedeltaIndexType, 'is_integer', inline='always')
@overload_method(TimedeltaIndexType, 'is_interval', inline='always')
@overload_method(TimedeltaIndexType, 'is_numeric', inline='always')
@overload_method(TimedeltaIndexType, 'is_object', inline='always')
@overload_method(RangeIndexType, 'is_boolean', inline='always')
@overload_method(RangeIndexType, 'is_floating', inline='always')
@overload_method(RangeIndexType, 'is_categorical', inline='always')
@overload_method(RangeIndexType, 'is_interval', inline='always')
@overload_method(RangeIndexType, 'is_object', inline='always')
@overload_method(IntervalIndexType, 'is_boolean', inline='always')
@overload_method(IntervalIndexType, 'is_floating', inline='always')
@overload_method(IntervalIndexType, 'is_categorical', inline='always')
@overload_method(IntervalIndexType, 'is_integer', inline='always')
@overload_method(IntervalIndexType, 'is_numeric', inline='always')
@overload_method(IntervalIndexType, 'is_object', inline='always')
@overload_method(CategoricalIndexType, 'is_boolean', inline='always')
@overload_method(CategoricalIndexType, 'is_floating', inline='always')
@overload_method(CategoricalIndexType, 'is_integer', inline='always')
@overload_method(CategoricalIndexType, 'is_interval', inline='always')
@overload_method(CategoricalIndexType, 'is_numeric', inline='always')
@overload_method(CategoricalIndexType, 'is_object', inline='always')
@overload_method(PeriodIndexType, 'is_boolean', inline='always')
@overload_method(PeriodIndexType, 'is_floating', inline='always')
@overload_method(PeriodIndexType, 'is_categorical', inline='always')
@overload_method(PeriodIndexType, 'is_integer', inline='always')
@overload_method(PeriodIndexType, 'is_interval', inline='always')
@overload_method(PeriodIndexType, 'is_numeric', inline='always')
@overload_method(PeriodIndexType, 'is_object', inline='always')
@overload_method(MultiIndexType, 'is_boolean', inline='always')
@overload_method(MultiIndexType, 'is_floating', inline='always')
@overload_method(MultiIndexType, 'is_categorical', inline='always')
@overload_method(MultiIndexType, 'is_integer', inline='always')
@overload_method(MultiIndexType, 'is_interval', inline='always')
@overload_method(MultiIndexType, 'is_numeric', inline='always')
def overload_is_methods_false(I):
    return lambda I: False


@overload(operator.getitem, no_unliteral=True)
def overload_heter_index_getitem(I, ind):
    if not isinstance(I, HeterogeneousIndexType):
        return
    if isinstance(ind, types.Integer):
        return lambda I, ind: bodo.hiframes.pd_index_ext.get_index_data(I)[ind]
    if isinstance(I, HeterogeneousIndexType):
        return lambda I, ind: bodo.hiframes.pd_index_ext.init_heter_index(bodo
            .hiframes.pd_index_ext.get_index_data(I)[ind], bodo.hiframes.
            pd_index_ext.get_index_name(I))


@lower_constant(DatetimeIndexType)
@lower_constant(TimedeltaIndexType)
def lower_constant_time_index(context, builder, ty, pyval):
    if isinstance(ty.data, bodo.DatetimeArrayType):
        data = context.get_constant_generic(builder, ty.data, pyval.array)
    else:
        data = context.get_constant_generic(builder, types.Array(types.
            int64, 1, 'C'), pyval.values.view(np.int64))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    vls__aon = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, vls__aon])


@lower_constant(PeriodIndexType)
def lower_constant_period_index(context, builder, ty, pyval):
    data = context.get_constant_generic(builder, bodo.IntegerArrayType(
        types.int64), pd.arrays.IntegerArray(pyval.asi8, pyval.isna()))
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    vls__aon = context.get_constant_null(types.DictType(types.int64, types.
        int64))
    return lir.Constant.literal_struct([data, name, vls__aon])


@lower_constant(NumericIndexType)
def lower_constant_numeric_index(context, builder, ty, pyval):
    assert isinstance(ty.dtype, (types.Integer, types.Float, types.Boolean))
    data = context.get_constant_generic(builder, types.Array(ty.dtype, 1,
        'C'), pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    dtype = ty.dtype
    vls__aon = context.get_constant_null(types.DictType(dtype, types.int64))
    return lir.Constant.literal_struct([data, name, vls__aon])


@lower_constant(StringIndexType)
@lower_constant(BinaryIndexType)
def lower_constant_binary_string_index(context, builder, ty, pyval):
    lirm__pwnp = ty.data
    scalar_type = ty.data.dtype
    data = context.get_constant_generic(builder, lirm__pwnp, pyval.values)
    name = context.get_constant_generic(builder, ty.name_typ, pyval.name)
    vls__aon = context.get_constant_null(types.DictType(scalar_type, types.
        int64))
    return lir.Constant.literal_struct([data, name, vls__aon])


@lower_builtin('getiter', RangeIndexType)
def getiter_range_index(context, builder, sig, args):
    [zbq__umooa] = sig.args
    [index] = args
    tgxv__cke = context.make_helper(builder, zbq__umooa, value=index)
    kvj__sljz = context.make_helper(builder, sig.return_type)
    pluxc__wtfyw = cgutils.alloca_once_value(builder, tgxv__cke.start)
    zur__zitae = context.get_constant(types.intp, 0)
    fiu__ovzo = cgutils.alloca_once_value(builder, zur__zitae)
    kvj__sljz.iter = pluxc__wtfyw
    kvj__sljz.stop = tgxv__cke.stop
    kvj__sljz.step = tgxv__cke.step
    kvj__sljz.count = fiu__ovzo
    bemoz__okx = builder.sub(tgxv__cke.stop, tgxv__cke.start)
    ctjqr__yiei = context.get_constant(types.intp, 1)
    fcj__dxku = builder.icmp_signed('>', bemoz__okx, zur__zitae)
    kznrw__llqq = builder.icmp_signed('>', tgxv__cke.step, zur__zitae)
    yigx__vsjv = builder.not_(builder.xor(fcj__dxku, kznrw__llqq))
    with builder.if_then(yigx__vsjv):
        kqxi__xavg = builder.srem(bemoz__okx, tgxv__cke.step)
        kqxi__xavg = builder.select(fcj__dxku, kqxi__xavg, builder.neg(
            kqxi__xavg))
        wyn__eato = builder.icmp_signed('>', kqxi__xavg, zur__zitae)
        fpqhe__euqk = builder.add(builder.sdiv(bemoz__okx, tgxv__cke.step),
            builder.select(wyn__eato, ctjqr__yiei, zur__zitae))
        builder.store(fpqhe__euqk, fiu__ovzo)
    tfqb__cpbi = kvj__sljz._getvalue()
    xrxzd__ynpca = impl_ret_new_ref(context, builder, sig.return_type,
        tfqb__cpbi)
    return xrxzd__ynpca


def _install_index_getiter():
    index_types = [NumericIndexType, StringIndexType, BinaryIndexType,
        CategoricalIndexType, TimedeltaIndexType, DatetimeIndexType]
    for typ in index_types:
        lower_builtin('getiter', typ)(numba.np.arrayobj.getiter_array)


_install_index_getiter()
index_unsupported_methods = ['append', 'asof', 'asof_locs', 'astype',
    'delete', 'drop', 'droplevel', 'dropna', 'equals', 'factorize',
    'fillna', 'format', 'get_indexer', 'get_indexer_for',
    'get_indexer_non_unique', 'get_level_values', 'get_slice_bound',
    'get_value', 'groupby', 'holds_integer', 'identical', 'insert', 'is_',
    'is_mixed', 'is_type_compatible', 'item', 'join', 'memory_usage',
    'ravel', 'reindex', 'searchsorted', 'set_names', 'set_value', 'shift',
    'slice_indexer', 'slice_locs', 'sort', 'sortlevel', 'str',
    'to_flat_index', 'to_native_types', 'transpose', 'value_counts', 'view']
index_unsupported_atrs = ['array', 'asi8', 'has_duplicates', 'hasnans',
    'is_unique']
cat_idx_unsupported_atrs = ['codes', 'categories', 'ordered',
    'is_monotonic', 'is_monotonic_increasing', 'is_monotonic_decreasing']
cat_idx_unsupported_methods = ['rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered', 'get_loc', 'isin',
    'all', 'any', 'union', 'intersection', 'difference', 'symmetric_difference'
    ]
interval_idx_unsupported_atrs = ['closed', 'is_empty',
    'is_non_overlapping_monotonic', 'is_overlapping', 'left', 'right',
    'mid', 'length', 'values', 'nbytes', 'is_monotonic',
    'is_monotonic_increasing', 'is_monotonic_decreasing', 'dtype']
interval_idx_unsupported_methods = ['contains', 'copy', 'overlaps',
    'set_closed', 'to_tuples', 'take', 'get_loc', 'isna', 'isnull', 'map',
    'isin', 'all', 'any', 'argsort', 'sort_values', 'argmax', 'argmin',
    'where', 'putmask', 'nunique', 'union', 'intersection', 'difference',
    'symmetric_difference', 'to_series', 'to_frame', 'to_list', 'tolist',
    'repeat', 'min', 'max']
multi_index_unsupported_atrs = ['levshape', 'levels', 'codes', 'dtypes',
    'values', 'nbytes', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
multi_index_unsupported_methods = ['copy', 'set_levels', 'set_codes',
    'swaplevel', 'reorder_levels', 'remove_unused_levels', 'get_loc',
    'get_locs', 'get_loc_level', 'take', 'isna', 'isnull', 'map', 'isin',
    'unique', 'all', 'any', 'argsort', 'sort_values', 'argmax', 'argmin',
    'where', 'putmask', 'nunique', 'union', 'intersection', 'difference',
    'symmetric_difference', 'to_series', 'to_list', 'tolist', 'to_numpy',
    'repeat', 'min', 'max']
dt_index_unsupported_atrs = ['time', 'timez', 'tz', 'freq', 'freqstr',
    'inferred_freq']
dt_index_unsupported_methods = ['normalize', 'strftime', 'snap',
    'tz_localize', 'round', 'floor', 'ceil', 'to_period', 'to_perioddelta',
    'to_pydatetime', 'month_name', 'day_name', 'mean', 'indexer_at_time',
    'indexer_between', 'indexer_between_time', 'all', 'any']
td_index_unsupported_atrs = ['components', 'inferred_freq']
td_index_unsupported_methods = ['to_pydatetime', 'round', 'floor', 'ceil',
    'mean', 'all', 'any']
period_index_unsupported_atrs = ['day', 'dayofweek', 'day_of_week',
    'dayofyear', 'day_of_year', 'days_in_month', 'daysinmonth', 'freq',
    'freqstr', 'hour', 'is_leap_year', 'minute', 'month', 'quarter',
    'second', 'week', 'weekday', 'weekofyear', 'year', 'end_time', 'qyear',
    'start_time', 'is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing', 'dtype']
period_index_unsupported_methods = ['asfreq', 'strftime', 'to_timestamp',
    'isin', 'unique', 'all', 'any', 'where', 'putmask', 'sort_values',
    'union', 'intersection', 'difference', 'symmetric_difference',
    'to_series', 'to_frame', 'to_numpy', 'to_list', 'tolist', 'repeat',
    'min', 'max']
string_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
string_index_unsupported_methods = ['min', 'max']
binary_index_unsupported_atrs = ['is_monotonic', 'is_monotonic_increasing',
    'is_monotonic_decreasing']
binary_index_unsupported_methods = ['repeat', 'min', 'max']
index_types = [('pandas.RangeIndex.{}', RangeIndexType), (
    'pandas.Index.{} with numeric data', NumericIndexType), (
    'pandas.Index.{} with string data', StringIndexType), (
    'pandas.Index.{} with binary data', BinaryIndexType), (
    'pandas.TimedeltaIndex.{}', TimedeltaIndexType), (
    'pandas.IntervalIndex.{}', IntervalIndexType), (
    'pandas.CategoricalIndex.{}', CategoricalIndexType), (
    'pandas.PeriodIndex.{}', PeriodIndexType), ('pandas.DatetimeIndex.{}',
    DatetimeIndexType), ('pandas.MultiIndex.{}', MultiIndexType)]
for name, typ in index_types:
    idx_typ_to_format_str_map[typ] = name


def _install_index_unsupported():
    for tpkhv__flvl in index_unsupported_methods:
        for ztkov__gyuku, typ in index_types:
            overload_method(typ, tpkhv__flvl, no_unliteral=True)(
                create_unsupported_overload(ztkov__gyuku.format(tpkhv__flvl +
                '()')))
    for nvwwv__ohr in index_unsupported_atrs:
        for ztkov__gyuku, typ in index_types:
            overload_attribute(typ, nvwwv__ohr, no_unliteral=True)(
                create_unsupported_overload(ztkov__gyuku.format(nvwwv__ohr)))
    urc__duh = [(StringIndexType, string_index_unsupported_atrs), (
        BinaryIndexType, binary_index_unsupported_atrs), (
        CategoricalIndexType, cat_idx_unsupported_atrs), (IntervalIndexType,
        interval_idx_unsupported_atrs), (MultiIndexType,
        multi_index_unsupported_atrs), (DatetimeIndexType,
        dt_index_unsupported_atrs), (TimedeltaIndexType,
        td_index_unsupported_atrs), (PeriodIndexType,
        period_index_unsupported_atrs)]
    opa__lkk = [(CategoricalIndexType, cat_idx_unsupported_methods), (
        IntervalIndexType, interval_idx_unsupported_methods), (
        MultiIndexType, multi_index_unsupported_methods), (
        DatetimeIndexType, dt_index_unsupported_methods), (
        TimedeltaIndexType, td_index_unsupported_methods), (PeriodIndexType,
        period_index_unsupported_methods), (BinaryIndexType,
        binary_index_unsupported_methods), (StringIndexType,
        string_index_unsupported_methods)]
    for typ, oeyhs__eno in opa__lkk:
        ztkov__gyuku = idx_typ_to_format_str_map[typ]
        for wrdx__obzis in oeyhs__eno:
            overload_method(typ, wrdx__obzis, no_unliteral=True)(
                create_unsupported_overload(ztkov__gyuku.format(wrdx__obzis +
                '()')))
    for typ, sswbo__anlms in urc__duh:
        ztkov__gyuku = idx_typ_to_format_str_map[typ]
        for nvwwv__ohr in sswbo__anlms:
            overload_attribute(typ, nvwwv__ohr, no_unliteral=True)(
                create_unsupported_overload(ztkov__gyuku.format(nvwwv__ohr)))


_install_index_unsupported()
