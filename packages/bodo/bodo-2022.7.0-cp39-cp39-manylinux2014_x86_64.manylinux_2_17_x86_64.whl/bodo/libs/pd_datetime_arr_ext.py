"""DatetimeArray extension for Pandas DatetimeArray with timezone support."""
import operator
import numba
import pandas as pd
import pytz
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.utils.conversion import ensure_contig_if_np
from bodo.utils.typing import BodoArrayIterator, BodoError, get_literal_value, is_list_like_index_type, is_overload_constant_int, is_overload_constant_str, raise_bodo_error


class PandasDatetimeTZDtype(types.Type):

    def __init__(self, tz):
        if isinstance(tz, (pytz._FixedOffset, pytz.tzinfo.BaseTzInfo)):
            tz = get_pytz_type_info(tz)
        if not isinstance(tz, (int, str)):
            raise BodoError(
                'Timezone must be either a valid pytz type with a zone or a fixed offset'
                )
        self.tz = tz
        super(PandasDatetimeTZDtype, self).__init__(name=
            f'PandasDatetimeTZDtype[{tz}]')


def get_pytz_type_info(pytz_type):
    if isinstance(pytz_type, pytz._FixedOffset):
        xrsb__mvuri = pd.Timedelta(pytz_type._offset).value
    else:
        xrsb__mvuri = pytz_type.zone
        if xrsb__mvuri not in pytz.all_timezones_set:
            raise BodoError(
                'Unsupported timezone type. Timezones must be a fixedOffset or contain a zone found in pytz.all_timezones'
                )
    return xrsb__mvuri


def nanoseconds_to_offset(nanoseconds):
    nfbsi__emeyv = nanoseconds // (60 * 1000 * 1000 * 1000)
    return pytz.FixedOffset(nfbsi__emeyv)


class DatetimeArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self, tz):
        if isinstance(tz, (pytz._FixedOffset, pytz.tzinfo.BaseTzInfo)):
            tz = get_pytz_type_info(tz)
        if not isinstance(tz, (int, str)):
            raise BodoError(
                'Timezone must be either a valid pytz type with a zone or a fixed offset'
                )
        self.tz = tz
        self._data_array_type = types.Array(types.NPDatetime('ns'), 1, 'C')
        self._dtype = PandasDatetimeTZDtype(tz)
        super(DatetimeArrayType, self).__init__(name=
            f'PandasDatetimeArray[{tz}]')

    @property
    def data_array_type(self):
        return self._data_array_type

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    @property
    def dtype(self):
        return self._dtype

    def copy(self):
        return DatetimeArrayType(self.tz)


@register_model(DatetimeArrayType)
class PandasDatetimeArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rsrwp__elh = [('data', fe_type.data_array_type)]
        models.StructModel.__init__(self, dmm, fe_type, rsrwp__elh)


make_attribute_wrapper(DatetimeArrayType, 'data', '_data')


@typeof_impl.register(pd.arrays.DatetimeArray)
def typeof_pd_datetime_array(val, c):
    if val.tz is None:
        raise BodoError(
            "Cannot support timezone naive pd.arrays.DatetimeArray. Please convert to a numpy array with .astype('datetime64[ns]')."
            )
    else:
        return DatetimeArrayType(val.dtype.tz)


@unbox(DatetimeArrayType)
def unbox_pd_datetime_array(typ, val, c):
    fwr__nwr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nqjd__cxyn = c.pyapi.string_from_constant_string('datetime64[ns]')
    wyypx__ood = c.pyapi.call_method(val, 'to_numpy', (nqjd__cxyn,))
    fwr__nwr.data = c.unbox(typ.data_array_type, wyypx__ood).value
    c.pyapi.decref(wyypx__ood)
    zlvs__gim = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(fwr__nwr._getvalue(), is_error=zlvs__gim)


@box(DatetimeArrayType)
def box_pd_datetime_array(typ, val, c):
    fwr__nwr = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    c.context.nrt.incref(c.builder, typ.data_array_type, fwr__nwr.data)
    qzw__hewbu = c.pyapi.from_native_value(typ.data_array_type, fwr__nwr.
        data, c.env_manager)
    cmlb__vbp = c.context.get_constant_generic(c.builder, types.
        unicode_type, 'ns')
    bgybf__obo = c.pyapi.from_native_value(types.unicode_type, cmlb__vbp, c
        .env_manager)
    if isinstance(typ.tz, str):
        jki__pyj = c.context.get_constant_generic(c.builder, types.
            unicode_type, typ.tz)
        grfim__mypki = c.pyapi.from_native_value(types.unicode_type,
            jki__pyj, c.env_manager)
    else:
        jmocw__cancr = nanoseconds_to_offset(typ.tz)
        grfim__mypki = c.pyapi.unserialize(c.pyapi.serialize_object(
            jmocw__cancr))
    rvwoh__lxjw = c.context.insert_const_string(c.builder.module, 'pandas')
    hkzjk__rja = c.pyapi.import_module_noblock(rvwoh__lxjw)
    jpuoz__bcri = c.pyapi.call_method(hkzjk__rja, 'DatetimeTZDtype', (
        bgybf__obo, grfim__mypki))
    tzer__fdab = c.pyapi.object_getattr_string(hkzjk__rja, 'arrays')
    ssd__ygwo = c.pyapi.call_method(tzer__fdab, 'DatetimeArray', (
        qzw__hewbu, jpuoz__bcri))
    c.pyapi.decref(qzw__hewbu)
    c.pyapi.decref(bgybf__obo)
    c.pyapi.decref(grfim__mypki)
    c.pyapi.decref(hkzjk__rja)
    c.pyapi.decref(jpuoz__bcri)
    c.pyapi.decref(tzer__fdab)
    c.context.nrt.decref(c.builder, typ, val)
    return ssd__ygwo


@intrinsic
def init_pandas_datetime_array(typingctx, data, tz):

    def codegen(context, builder, sig, args):
        data, tz = args
        dma__kokk = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        dma__kokk.data = data
        context.nrt.incref(builder, sig.args[0], data)
        return dma__kokk._getvalue()
    if is_overload_constant_str(tz) or is_overload_constant_int(tz):
        jki__pyj = get_literal_value(tz)
    else:
        raise BodoError('tz must be a constant string or Fixed Offset')
    hap__shmnm = DatetimeArrayType(jki__pyj)
    sig = hap__shmnm(hap__shmnm.data_array_type, tz)
    return sig, codegen


@overload(len, no_unliteral=True)
def overload_pd_datetime_arr_len(A):
    if isinstance(A, DatetimeArrayType):
        return lambda A: len(A._data)


@lower_constant(DatetimeArrayType)
def lower_constant_pd_datetime_arr(context, builder, typ, pyval):
    snu__qdx = context.get_constant_generic(builder, typ.data_array_type,
        pyval.to_numpy('datetime64[ns]'))
    sbvxs__ldcjm = lir.Constant.literal_struct([snu__qdx])
    return sbvxs__ldcjm


@overload_attribute(DatetimeArrayType, 'shape')
def overload_pd_datetime_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(DatetimeArrayType, 'nbytes')
def overload_pd_datetime_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(DatetimeArrayType, 'tz_convert', no_unliteral=True)
def overload_pd_datetime_tz_convert(A, tz):
    if tz == types.none:
        raise_bodo_error('tz_convert(): tz must be a string or Fixed Offset')
    else:

        def impl(A, tz):
            return init_pandas_datetime_array(A._data.copy(), tz)
    return impl


@overload_method(DatetimeArrayType, 'copy', no_unliteral=True)
def overload_pd_datetime_tz_convert(A):
    tz = A.tz

    def impl(A):
        return init_pandas_datetime_array(A._data.copy(), tz)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_getitem(A, ind):
    if not isinstance(A, DatetimeArrayType):
        return
    tz = A.tz
    if isinstance(ind, types.Integer):

        def impl(A, ind):
            return bodo.hiframes.pd_timestamp_ext.convert_val_to_timestamp(bodo
                .hiframes.pd_timestamp_ext.dt64_to_integer(A._data[ind]), tz)
        return impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            jplo__qjoix = ensure_contig_if_np(A._data[ind])
            return init_pandas_datetime_array(jplo__qjoix, tz)
        return impl_bool
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            jplo__qjoix = ensure_contig_if_np(A._data[ind])
            return init_pandas_datetime_array(jplo__qjoix, tz)
        return impl_slice
    raise BodoError(
        'operator.getitem with DatetimeArrayType is only supported with an integer index, boolean array, or slice.'
        )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def unwrap_tz_array(A):
    if isinstance(A, DatetimeArrayType):
        return lambda A: A._data
    return lambda A: A


def unwrap_tz_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    lewvu__ioppi = args[0]
    if equiv_set.has_shape(lewvu__ioppi):
        return ArrayAnalysis.AnalyzeResult(shape=lewvu__ioppi, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_libs_pd_datetime_arr_ext_unwrap_tz_array
    ) = unwrap_tz_array_equiv
