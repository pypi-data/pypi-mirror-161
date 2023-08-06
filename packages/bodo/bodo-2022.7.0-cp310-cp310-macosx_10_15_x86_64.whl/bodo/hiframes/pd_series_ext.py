"""
Implement pd.Series typing and data model handling.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import bound_function, signature
from numba.extending import infer_getattr, intrinsic, lower_builtin, lower_cast, models, overload, overload_attribute, overload_method, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.io import csv_cpp
from bodo.libs.int_arr_ext import IntDtype
from bodo.libs.pd_datetime_arr_ext import PandasDatetimeTZDtype
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_overload_const_str, get_overload_const_tuple, get_udf_error_msg, get_udf_out_arr_type, is_heterogeneous_tuple_type, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_int, is_overload_none, raise_bodo_error, to_nullable_type
_csv_output_is_dir = types.ExternalFunction('csv_output_is_dir', types.int8
    (types.voidptr))
ll.add_symbol('csv_output_is_dir', csv_cpp.csv_output_is_dir)


class SeriesType(types.IterableType, types.ArrayCompatible):
    ndim = 1

    def __init__(self, dtype, data=None, index=None, name_typ=None, dist=None):
        from bodo.hiframes.pd_index_ext import RangeIndexType
        from bodo.transforms.distributed_analysis import Distribution
        data = dtype_to_array_type(dtype) if data is None else data
        dtype = dtype.dtype if isinstance(dtype, IntDtype) else dtype
        self.dtype = dtype
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        index = RangeIndexType(types.none) if index is None else index
        self.index = index
        self.name_typ = name_typ
        dist = Distribution.OneD_Var if dist is None else dist
        self.dist = dist
        super(SeriesType, self).__init__(name=
            f'series({dtype}, {data}, {index}, {name_typ}, {dist})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self, dtype=None, index=None, dist=None):
        if index is None:
            index = self.index
        if dist is None:
            dist = self.dist
        if dtype is None:
            dtype = self.dtype
            data = self.data
        else:
            data = dtype_to_array_type(dtype)
        return SeriesType(dtype, data, index, self.name_typ, dist)

    @property
    def key(self):
        return self.dtype, self.data, self.index, self.name_typ, self.dist

    def unify(self, typingctx, other):
        from bodo.transforms.distributed_analysis import Distribution
        if isinstance(other, SeriesType):
            jayq__vxtxd = (self.index if self.index == other.index else
                self.index.unify(typingctx, other.index))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if other.dtype == self.dtype or not other.dtype.is_precise():
                return SeriesType(self.dtype, self.data.unify(typingctx,
                    other.data), jayq__vxtxd, dist=dist)
        return super(SeriesType, self).unify(typingctx, other)

    def can_convert_to(self, typingctx, other):
        from numba.core.typeconv import Conversion
        if (isinstance(other, SeriesType) and self.dtype == other.dtype and
            self.data == other.data and self.index == other.index and self.
            name_typ == other.name_typ and self.dist != other.dist):
            return Conversion.safe

    def is_precise(self):
        return self.dtype.is_precise()

    @property
    def iterator_type(self):
        return self.data.iterator_type

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class HeterogeneousSeriesType(types.Type):
    ndim = 1

    def __init__(self, data=None, index=None, name_typ=None):
        from bodo.hiframes.pd_index_ext import RangeIndexType
        from bodo.transforms.distributed_analysis import Distribution
        self.data = data
        name_typ = types.none if name_typ is None else name_typ
        index = RangeIndexType(types.none) if index is None else index
        self.index = index
        self.name_typ = name_typ
        self.dist = Distribution.REP
        super(HeterogeneousSeriesType, self).__init__(name=
            f'heter_series({data}, {index}, {name_typ})')

    def copy(self, index=None, dist=None):
        from bodo.transforms.distributed_analysis import Distribution
        assert dist == Distribution.REP, 'invalid distribution for HeterogeneousSeriesType'
        if index is None:
            index = self.index.copy()
        return HeterogeneousSeriesType(self.data, index, self.name_typ)

    @property
    def key(self):
        return self.data, self.index, self.name_typ

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@lower_builtin('getiter', SeriesType)
def series_getiter(context, builder, sig, args):
    ftfs__yrf = get_series_payload(context, builder, sig.args[0], args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].data))
    return impl(builder, (ftfs__yrf.data,))


@infer_getattr
class HeterSeriesAttribute(OverloadedKeyAttributeTemplate):
    key = HeterogeneousSeriesType

    def generic_resolve(self, S, attr):
        from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
        if self._is_existing_attr(attr):
            return
        if isinstance(S.index, HeterogeneousIndexType
            ) and is_overload_constant_tuple(S.index.data):
            chn__jay = get_overload_const_tuple(S.index.data)
            if attr in chn__jay:
                kfxei__chh = chn__jay.index(attr)
                return S.data[kfxei__chh]


def is_str_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == string_type


def is_dt64_series_typ(t):
    return isinstance(t, SeriesType) and (t.dtype == types.NPDatetime('ns') or
        isinstance(t.dtype, PandasDatetimeTZDtype))


def is_timedelta64_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == types.NPTimedelta('ns')


def is_datetime_date_series_typ(t):
    return isinstance(t, SeriesType) and t.dtype == datetime_date_type


class SeriesPayloadType(types.Type):

    def __init__(self, series_type):
        self.series_type = series_type
        super(SeriesPayloadType, self).__init__(name=
            f'SeriesPayloadType({series_type})')

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesPayloadType)
class SeriesPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        oukg__daau = [('data', fe_type.series_type.data), ('index', fe_type
            .series_type.index), ('name', fe_type.series_type.name_typ)]
        super(SeriesPayloadModel, self).__init__(dmm, fe_type, oukg__daau)


@register_model(HeterogeneousSeriesType)
@register_model(SeriesType)
class SeriesModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = SeriesPayloadType(fe_type)
        oukg__daau = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(SeriesModel, self).__init__(dmm, fe_type, oukg__daau)


def define_series_dtor(context, builder, series_type, payload_type):
    jegy__sob = builder.module
    xuzb__jqda = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    mzos__euta = cgutils.get_or_insert_function(jegy__sob, xuzb__jqda, name
        ='.dtor.series.{}'.format(series_type))
    if not mzos__euta.is_declaration:
        return mzos__euta
    mzos__euta.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(mzos__euta.append_basic_block())
    gaatg__cvxv = mzos__euta.args[0]
    gojln__gvcj = context.get_value_type(payload_type).as_pointer()
    wnmc__kvoz = builder.bitcast(gaatg__cvxv, gojln__gvcj)
    pbb__yxy = context.make_helper(builder, payload_type, ref=wnmc__kvoz)
    context.nrt.decref(builder, series_type.data, pbb__yxy.data)
    context.nrt.decref(builder, series_type.index, pbb__yxy.index)
    context.nrt.decref(builder, series_type.name_typ, pbb__yxy.name)
    builder.ret_void()
    return mzos__euta


def construct_series(context, builder, series_type, data_val, index_val,
    name_val):
    payload_type = SeriesPayloadType(series_type)
    ftfs__yrf = cgutils.create_struct_proxy(payload_type)(context, builder)
    ftfs__yrf.data = data_val
    ftfs__yrf.index = index_val
    ftfs__yrf.name = name_val
    ynj__sxur = context.get_value_type(payload_type)
    suppr__aew = context.get_abi_sizeof(ynj__sxur)
    xuue__qoaz = define_series_dtor(context, builder, series_type, payload_type
        )
    aln__skdl = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, suppr__aew), xuue__qoaz)
    jpqh__gwrte = context.nrt.meminfo_data(builder, aln__skdl)
    padna__moxfz = builder.bitcast(jpqh__gwrte, ynj__sxur.as_pointer())
    builder.store(ftfs__yrf._getvalue(), padna__moxfz)
    series = cgutils.create_struct_proxy(series_type)(context, builder)
    series.meminfo = aln__skdl
    series.parent = cgutils.get_null_value(series.parent.type)
    return series._getvalue()


@intrinsic
def init_series(typingctx, data, index, name=None):
    from bodo.hiframes.pd_index_ext import is_pd_index_type
    from bodo.hiframes.pd_multi_index_ext import MultiIndexType
    assert is_pd_index_type(index) or isinstance(index, MultiIndexType)
    name = types.none if name is None else name

    def codegen(context, builder, signature, args):
        data_val, index_val, name_val = args
        series_type = signature.return_type
        yhubi__rom = construct_series(context, builder, series_type,
            data_val, index_val, name_val)
        context.nrt.incref(builder, signature.args[0], data_val)
        context.nrt.incref(builder, signature.args[1], index_val)
        context.nrt.incref(builder, signature.args[2], name_val)
        return yhubi__rom
    if is_heterogeneous_tuple_type(data):
        ifgi__mofap = HeterogeneousSeriesType(data, index, name)
    else:
        dtype = data.dtype
        data = if_series_to_array_type(data)
        ifgi__mofap = SeriesType(dtype, data, index, name)
    sig = signature(ifgi__mofap, data, index, name)
    return sig, codegen


def init_series_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) >= 2 and not kws
    data = args[0]
    index = args[1]
    dpopo__ciepl = self.typemap[data.name]
    if is_heterogeneous_tuple_type(dpopo__ciepl) or isinstance(dpopo__ciepl,
        types.BaseTuple):
        return None
    nhc__wrnh = self.typemap[index.name]
    if not isinstance(nhc__wrnh, HeterogeneousIndexType
        ) and equiv_set.has_shape(data) and equiv_set.has_shape(index):
        equiv_set.insert_equiv(data, index)
    if equiv_set.has_shape(data):
        return ArrayAnalysis.AnalyzeResult(shape=data, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_init_series = (
    init_series_equiv)


def get_series_payload(context, builder, series_type, value):
    aln__skdl = cgutils.create_struct_proxy(series_type)(context, builder,
        value).meminfo
    payload_type = SeriesPayloadType(series_type)
    pbb__yxy = context.nrt.meminfo_data(builder, aln__skdl)
    gojln__gvcj = context.get_value_type(payload_type).as_pointer()
    pbb__yxy = builder.bitcast(pbb__yxy, gojln__gvcj)
    return context.make_helper(builder, payload_type, ref=pbb__yxy)


@intrinsic
def get_series_data(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        ftfs__yrf = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, series_typ.data,
            ftfs__yrf.data)
    ifgi__mofap = series_typ.data
    sig = signature(ifgi__mofap, series_typ)
    return sig, codegen


@intrinsic
def get_series_index(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        ftfs__yrf = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, series_typ.index,
            ftfs__yrf.index)
    ifgi__mofap = series_typ.index
    sig = signature(ifgi__mofap, series_typ)
    return sig, codegen


@intrinsic
def get_series_name(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        ftfs__yrf = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            ftfs__yrf.name)
    sig = signature(series_typ.name_typ, series_typ)
    return sig, codegen


def get_series_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    usx__pxif = args[0]
    dpopo__ciepl = self.typemap[usx__pxif.name].data
    if is_heterogeneous_tuple_type(dpopo__ciepl) or isinstance(dpopo__ciepl,
        types.BaseTuple):
        return None
    if equiv_set.has_shape(usx__pxif):
        return ArrayAnalysis.AnalyzeResult(shape=usx__pxif, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_get_series_data
    ) = get_series_data_equiv


def get_series_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    usx__pxif = args[0]
    nhc__wrnh = self.typemap[usx__pxif.name].index
    if isinstance(nhc__wrnh, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(usx__pxif):
        return ArrayAnalysis.AnalyzeResult(shape=usx__pxif, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_get_series_index
    ) = get_series_index_equiv


def alias_ext_init_series(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    if len(args) > 1:
        numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
            arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_series',
    'bodo.hiframes.pd_series_ext'] = alias_ext_init_series


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_series_data',
    'bodo.hiframes.pd_series_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_series_index',
    'bodo.hiframes.pd_series_ext'] = alias_ext_dummy_func


def is_series_type(typ):
    return isinstance(typ, SeriesType)


def if_series_to_array_type(typ):
    if isinstance(typ, SeriesType):
        return typ.data
    return typ


@lower_cast(SeriesType, SeriesType)
def cast_series(context, builder, fromty, toty, val):
    if fromty.copy(index=toty.index) == toty and isinstance(fromty.index,
        bodo.hiframes.pd_index_ext.RangeIndexType) and isinstance(toty.
        index, bodo.hiframes.pd_index_ext.NumericIndexType):
        ftfs__yrf = get_series_payload(context, builder, fromty, val)
        jayq__vxtxd = context.cast(builder, ftfs__yrf.index, fromty.index,
            toty.index)
        context.nrt.incref(builder, fromty.data, ftfs__yrf.data)
        context.nrt.incref(builder, fromty.name_typ, ftfs__yrf.name)
        return construct_series(context, builder, toty, ftfs__yrf.data,
            jayq__vxtxd, ftfs__yrf.name)
    if (fromty.dtype == toty.dtype and fromty.data == toty.data and fromty.
        index == toty.index and fromty.name_typ == toty.name_typ and fromty
        .dist != toty.dist):
        return val
    return val


@infer_getattr
class SeriesAttribute(OverloadedKeyAttributeTemplate):
    key = SeriesType

    @bound_function('series.head')
    def resolve_head(self, ary, args, kws):
        vui__izy = 'Series.head'
        kpy__ebtcy = 'n',
        mub__jezd = {'n': 5}
        pysig, qkfl__vrg = bodo.utils.typing.fold_typing_args(vui__izy,
            args, kws, kpy__ebtcy, mub__jezd)
        ijq__njvqp = qkfl__vrg[0]
        if not is_overload_int(ijq__njvqp):
            raise BodoError(f"{vui__izy}(): 'n' must be an Integer")
        mfhsk__gsovv = ary
        return mfhsk__gsovv(*qkfl__vrg).replace(pysig=pysig)

    def _resolve_map_func(self, ary, func, pysig, fname, f_args=None, kws=None
        ):
        dtype = ary.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ary,
            'Series.map()')
        if dtype == types.NPDatetime('ns'):
            dtype = pd_timestamp_type
        if dtype == types.NPTimedelta('ns'):
            dtype = pd_timedelta_type
        wve__cjh = dtype,
        if f_args is not None:
            wve__cjh += tuple(f_args.types)
        if kws is None:
            kws = {}
        leik__eorl = False
        udim__pdxg = True
        if fname == 'map' and isinstance(func, types.DictType):
            tazqr__tgdf = func.value_type
            leik__eorl = True
        else:
            try:
                if types.unliteral(func) == types.unicode_type:
                    if not is_overload_constant_str(func):
                        raise BodoError(
                            f'Series.apply(): string argument (for builtins) must be a compile time constant'
                            )
                    tazqr__tgdf = bodo.utils.transform.get_udf_str_return_type(
                        ary, get_overload_const_str(func), self.context,
                        'Series.apply')
                    udim__pdxg = False
                elif bodo.utils.typing.is_numpy_ufunc(func):
                    tazqr__tgdf = func.get_call_type(self.context, (ary,), {}
                        ).return_type
                    udim__pdxg = False
                else:
                    tazqr__tgdf = get_const_func_output_type(func, wve__cjh,
                        kws, self.context, numba.core.registry.cpu_target.
                        target_context)
            except Exception as ekyif__fcroj:
                raise BodoError(get_udf_error_msg(f'Series.{fname}()',
                    ekyif__fcroj))
        if udim__pdxg:
            if isinstance(tazqr__tgdf, (SeriesType, HeterogeneousSeriesType)
                ) and tazqr__tgdf.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(tazqr__tgdf, HeterogeneousSeriesType):
                smomr__kwi, qbgr__olu = tazqr__tgdf.const_info
                if isinstance(tazqr__tgdf.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    yxcg__znh = tazqr__tgdf.data.tuple_typ.types
                elif isinstance(tazqr__tgdf.data, types.Tuple):
                    yxcg__znh = tazqr__tgdf.data.types
                avgz__ayw = tuple(to_nullable_type(dtype_to_array_type(t)) for
                    t in yxcg__znh)
                bjly__kaq = bodo.DataFrameType(avgz__ayw, ary.index, qbgr__olu)
            elif isinstance(tazqr__tgdf, SeriesType):
                naa__jwvim, qbgr__olu = tazqr__tgdf.const_info
                avgz__ayw = tuple(to_nullable_type(dtype_to_array_type(
                    tazqr__tgdf.dtype)) for smomr__kwi in range(naa__jwvim))
                bjly__kaq = bodo.DataFrameType(avgz__ayw, ary.index, qbgr__olu)
            else:
                vorq__fohm = get_udf_out_arr_type(tazqr__tgdf, leik__eorl)
                bjly__kaq = SeriesType(vorq__fohm.dtype, vorq__fohm, ary.
                    index, ary.name_typ)
        else:
            bjly__kaq = tazqr__tgdf
        return signature(bjly__kaq, (func,)).replace(pysig=pysig)

    @bound_function('series.map', no_unliteral=True)
    def resolve_map(self, ary, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws['arg']
        kws.pop('arg', None)
        na_action = args[1] if len(args) > 1 else kws.pop('na_action',
            types.none)
        jscnl__pkm = dict(na_action=na_action)
        wrcd__yheoh = dict(na_action=None)
        check_unsupported_args('Series.map', jscnl__pkm, wrcd__yheoh,
            package_name='pandas', module_name='Series')

        def map_stub(arg, na_action=None):
            pass
        pysig = numba.core.utils.pysignature(map_stub)
        return self._resolve_map_func(ary, func, pysig, 'map')

    @bound_function('series.apply', no_unliteral=True)
    def resolve_apply(self, ary, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws['func']
        kws.pop('func', None)
        dcd__sqk = args[1] if len(args) > 1 else kws.pop('convert_dtype',
            types.literal(True))
        f_args = args[2] if len(args) > 2 else kws.pop('args', None)
        jscnl__pkm = dict(convert_dtype=dcd__sqk)
        fipn__tovz = dict(convert_dtype=True)
        check_unsupported_args('Series.apply', jscnl__pkm, fipn__tovz,
            package_name='pandas', module_name='Series')
        jve__mqz = ', '.join("{} = ''".format(bhd__lbng) for bhd__lbng in
            kws.keys())
        mncb__hcrpx = (
            f'def apply_stub(func, convert_dtype=True, args=(), {jve__mqz}):\n'
            )
        mncb__hcrpx += '    pass\n'
        hnk__wwdjt = {}
        exec(mncb__hcrpx, {}, hnk__wwdjt)
        vglf__uyh = hnk__wwdjt['apply_stub']
        pysig = numba.core.utils.pysignature(vglf__uyh)
        return self._resolve_map_func(ary, func, pysig, 'apply', f_args, kws)

    def _resolve_combine_func(self, ary, args, kws):
        kwargs = dict(kws)
        other = args[0] if len(args) > 0 else types.unliteral(kwargs['other'])
        func = args[1] if len(args) > 1 else kwargs['func']
        fill_value = args[2] if len(args) > 2 else types.unliteral(kwargs.
            get('fill_value', types.none))

        def combine_stub(other, func, fill_value=None):
            pass
        pysig = numba.core.utils.pysignature(combine_stub)
        odaql__avqzd = ary.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ary,
            'Series.combine()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
            'Series.combine()')
        if odaql__avqzd == types.NPDatetime('ns'):
            odaql__avqzd = pd_timestamp_type
        oyozq__dwjqk = other.dtype
        if oyozq__dwjqk == types.NPDatetime('ns'):
            oyozq__dwjqk = pd_timestamp_type
        tazqr__tgdf = get_const_func_output_type(func, (odaql__avqzd,
            oyozq__dwjqk), {}, self.context, numba.core.registry.cpu_target
            .target_context)
        sig = signature(SeriesType(tazqr__tgdf, index=ary.index, name_typ=
            types.none), (other, func, fill_value))
        return sig.replace(pysig=pysig)

    @bound_function('series.combine', no_unliteral=True)
    def resolve_combine(self, ary, args, kws):
        return self._resolve_combine_func(ary, args, kws)

    @bound_function('series.pipe', no_unliteral=True)
    def resolve_pipe(self, ary, args, kws):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ary,
            'Series.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, ary,
            args, kws, 'Series')

    def generic_resolve(self, S, attr):
        from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
        if self._is_existing_attr(attr):
            return
        if isinstance(S.index, HeterogeneousIndexType
            ) and is_overload_constant_tuple(S.index.data):
            chn__jay = get_overload_const_tuple(S.index.data)
            if attr in chn__jay:
                kfxei__chh = chn__jay.index(attr)
                return S.data[kfxei__chh]


series_binary_ops = tuple(op for op in numba.core.typing.npydecl.
    NumpyRulesArrayOperator._op_map.keys() if op not in (operator.lshift,
    operator.rshift))
series_inplace_binary_ops = tuple(op for op in numba.core.typing.npydecl.
    NumpyRulesInplaceArrayOperator._op_map.keys() if op not in (operator.
    ilshift, operator.irshift, operator.itruediv))
inplace_binop_to_imm = {operator.iadd: operator.add, operator.isub:
    operator.sub, operator.imul: operator.mul, operator.ifloordiv: operator
    .floordiv, operator.imod: operator.mod, operator.ipow: operator.pow,
    operator.iand: operator.and_, operator.ior: operator.or_, operator.ixor:
    operator.xor}
series_unary_ops = operator.neg, operator.invert, operator.pos
str2str_methods = ('capitalize', 'lower', 'lstrip', 'rstrip', 'strip',
    'swapcase', 'title', 'upper')
str2bool_methods = ('isalnum', 'isalpha', 'isdigit', 'isspace', 'islower',
    'isupper', 'istitle', 'isnumeric', 'isdecimal')


@overload(pd.Series, no_unliteral=True)
def pd_series_overload(data=None, index=None, dtype=None, name=None, copy=
    False, fastpath=False):
    if not is_overload_false(fastpath):
        raise BodoError("pd.Series(): 'fastpath' argument not supported.")
    ubc__kdx = is_overload_none(data)
    ihz__vwzje = is_overload_none(index)
    hjiu__llhpe = is_overload_none(dtype)
    if ubc__kdx and ihz__vwzje and hjiu__llhpe:
        raise BodoError(
            'pd.Series() requires at least 1 of data, index, and dtype to not be none'
            )
    if is_series_type(data) and not ihz__vwzje:
        raise BodoError(
            'pd.Series() does not support index value when input data is a Series'
            )
    if isinstance(data, types.DictType):
        raise_bodo_error(
            'pd.Series(): When intializing series with a dictionary, it is required that the dict has constant keys'
            )
    if is_heterogeneous_tuple_type(data) and is_overload_none(dtype):
        lreir__tppp = tuple(len(data) * [False])

        def impl_heter(data=None, index=None, dtype=None, name=None, copy=
            False, fastpath=False):
            ipvaz__ocg = bodo.utils.conversion.extract_index_if_none(data,
                index)
            hduzj__kebts = bodo.utils.conversion.to_tuple(data)
            data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(
                hduzj__kebts, lreir__tppp)
            return bodo.hiframes.pd_series_ext.init_series(data_val, bodo.
                utils.conversion.convert_to_index(ipvaz__ocg), name)
        return impl_heter
    if ubc__kdx:
        if hjiu__llhpe:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                kfznx__hazv = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                ipvaz__ocg = bodo.utils.conversion.extract_index_if_none(data,
                    index)
                numba.parfors.parfor.init_prange()
                saxcv__xgwyu = len(ipvaz__ocg)
                hduzj__kebts = np.empty(saxcv__xgwyu, np.float64)
                for mjzsu__giriu in numba.parfors.parfor.internal_prange(
                    saxcv__xgwyu):
                    bodo.libs.array_kernels.setna(hduzj__kebts, mjzsu__giriu)
                return bodo.hiframes.pd_series_ext.init_series(hduzj__kebts,
                    bodo.utils.conversion.convert_to_index(ipvaz__ocg),
                    kfznx__hazv)
            return impl
        if bodo.utils.conversion._is_str_dtype(dtype):
            xvxhs__vxta = bodo.string_array_type
        else:
            oag__znvt = bodo.utils.typing.parse_dtype(dtype, 'pandas.Series')
            if isinstance(oag__znvt, bodo.libs.int_arr_ext.IntDtype):
                xvxhs__vxta = bodo.IntegerArrayType(oag__znvt.dtype)
            elif oag__znvt == bodo.libs.bool_arr_ext.boolean_dtype:
                xvxhs__vxta = bodo.boolean_array
            elif isinstance(oag__znvt, types.Number) or oag__znvt in [bodo.
                datetime64ns, bodo.timedelta64ns]:
                xvxhs__vxta = types.Array(oag__znvt, 1, 'C')
            else:
                raise BodoError(
                    'pd.Series with dtype: {dtype} not currently supported')
        if ihz__vwzje:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                kfznx__hazv = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                ipvaz__ocg = bodo.hiframes.pd_index_ext.init_range_index(0,
                    0, 1, None)
                numba.parfors.parfor.init_prange()
                saxcv__xgwyu = len(ipvaz__ocg)
                hduzj__kebts = bodo.utils.utils.alloc_type(saxcv__xgwyu,
                    xvxhs__vxta, (-1,))
                return bodo.hiframes.pd_series_ext.init_series(hduzj__kebts,
                    ipvaz__ocg, kfznx__hazv)
            return impl
        else:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                kfznx__hazv = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                ipvaz__ocg = bodo.utils.conversion.extract_index_if_none(data,
                    index)
                numba.parfors.parfor.init_prange()
                saxcv__xgwyu = len(ipvaz__ocg)
                hduzj__kebts = bodo.utils.utils.alloc_type(saxcv__xgwyu,
                    xvxhs__vxta, (-1,))
                for mjzsu__giriu in numba.parfors.parfor.internal_prange(
                    saxcv__xgwyu):
                    bodo.libs.array_kernels.setna(hduzj__kebts, mjzsu__giriu)
                return bodo.hiframes.pd_series_ext.init_series(hduzj__kebts,
                    bodo.utils.conversion.convert_to_index(ipvaz__ocg),
                    kfznx__hazv)
            return impl

    def impl(data=None, index=None, dtype=None, name=None, copy=False,
        fastpath=False):
        kfznx__hazv = bodo.utils.conversion.extract_name_if_none(data, name)
        ipvaz__ocg = bodo.utils.conversion.extract_index_if_none(data, index)
        ojj__waw = bodo.utils.conversion.coerce_to_array(data, True,
            scalar_to_arr_len=len(ipvaz__ocg))
        vixui__tlbd = bodo.utils.conversion.fix_arr_dtype(ojj__waw, dtype,
            None, False)
        return bodo.hiframes.pd_series_ext.init_series(vixui__tlbd, bodo.
            utils.conversion.convert_to_index(ipvaz__ocg), kfznx__hazv)
    return impl


@overload_method(SeriesType, 'to_csv', no_unliteral=True)
def to_csv_overload(series, path_or_buf=None, sep=',', na_rep='',
    float_format=None, columns=None, header=True, index=True, index_label=
    None, mode='w', encoding=None, compression='infer', quoting=None,
    quotechar='"', line_terminator=None, chunksize=None, date_format=None,
    doublequote=True, escapechar=None, decimal='.', errors='strict',
    _bodo_file_prefix='part-', _is_parallel=False):
    if not (is_overload_none(path_or_buf) or is_overload_constant_str(
        path_or_buf) or path_or_buf == string_type):
        raise BodoError(
            "Series.to_csv(): 'path_or_buf' argument should be None or string")
    if is_overload_none(path_or_buf):

        def _impl(series, path_or_buf=None, sep=',', na_rep='',
            float_format=None, columns=None, header=True, index=True,
            index_label=None, mode='w', encoding=None, compression='infer',
            quoting=None, quotechar='"', line_terminator=None, chunksize=
            None, date_format=None, doublequote=True, escapechar=None,
            decimal='.', errors='strict', _bodo_file_prefix='part-',
            _is_parallel=False):
            with numba.objmode(D='unicode_type'):
                D = series.to_csv(None, sep, na_rep, float_format, columns,
                    header, index, index_label, mode, encoding, compression,
                    quoting, quotechar, line_terminator, chunksize,
                    date_format, doublequote, escapechar, decimal, errors)
            return D
        return _impl

    def _impl(series, path_or_buf=None, sep=',', na_rep='', float_format=
        None, columns=None, header=True, index=True, index_label=None, mode
        ='w', encoding=None, compression='infer', quoting=None, quotechar=
        '"', line_terminator=None, chunksize=None, date_format=None,
        doublequote=True, escapechar=None, decimal='.', errors='strict',
        _bodo_file_prefix='part-', _is_parallel=False):
        if _is_parallel:
            header &= (bodo.libs.distributed_api.get_rank() == 0
                ) | _csv_output_is_dir(unicode_to_utf8(path_or_buf))
        with numba.objmode(D='unicode_type'):
            D = series.to_csv(None, sep, na_rep, float_format, columns,
                header, index, index_label, mode, encoding, compression,
                quoting, quotechar, line_terminator, chunksize, date_format,
                doublequote, escapechar, decimal, errors)
        bodo.io.fs_io.csv_write(path_or_buf, D, _bodo_file_prefix, _is_parallel
            )
    return _impl


@lower_constant(SeriesType)
def lower_constant_series(context, builder, series_type, pyval):
    if isinstance(series_type.data, bodo.DatetimeArrayType):
        xvga__fwjc = pyval.array
    else:
        xvga__fwjc = pyval.values
    data_val = context.get_constant_generic(builder, series_type.data,
        xvga__fwjc)
    index_val = context.get_constant_generic(builder, series_type.index,
        pyval.index)
    name_val = context.get_constant_generic(builder, series_type.name_typ,
        pyval.name)
    pbb__yxy = lir.Constant.literal_struct([data_val, index_val, name_val])
    pbb__yxy = cgutils.global_constant(builder, '.const.payload', pbb__yxy
        ).bitcast(cgutils.voidptr_t)
    qxn__hnb = context.get_constant(types.int64, -1)
    ahfn__iwakq = context.get_constant_null(types.voidptr)
    aln__skdl = lir.Constant.literal_struct([qxn__hnb, ahfn__iwakq,
        ahfn__iwakq, pbb__yxy, qxn__hnb])
    aln__skdl = cgutils.global_constant(builder, '.const.meminfo', aln__skdl
        ).bitcast(cgutils.voidptr_t)
    yhubi__rom = lir.Constant.literal_struct([aln__skdl, ahfn__iwakq])
    return yhubi__rom


series_unsupported_attrs = {'axes', 'array', 'flags', 'at', 'is_unique',
    'sparse', 'attrs'}
series_unsupported_methods = ('set_flags', 'convert_dtypes', 'bool',
    'to_period', 'to_timestamp', '__array__', 'get', 'at', '__iter__',
    'items', 'iteritems', 'pop', 'item', 'xs', 'combine_first', 'agg',
    'aggregate', 'transform', 'expanding', 'ewm', 'clip', 'factorize',
    'mode', 'align', 'drop', 'droplevel', 'reindex', 'reindex_like',
    'sample', 'set_axis', 'truncate', 'add_prefix', 'add_suffix', 'filter',
    'interpolate', 'argmin', 'argmax', 'reorder_levels', 'swaplevel',
    'unstack', 'searchsorted', 'ravel', 'squeeze', 'view', 'compare',
    'update', 'asfreq', 'asof', 'resample', 'tz_convert', 'tz_localize',
    'at_time', 'between_time', 'tshift', 'slice_shift', 'plot', 'hist',
    'to_pickle', 'to_excel', 'to_xarray', 'to_hdf', 'to_sql', 'to_json',
    'to_string', 'to_clipboard', 'to_latex', 'to_markdown')


def _install_series_unsupported():
    for lozn__tdv in series_unsupported_attrs:
        uic__sknuo = 'Series.' + lozn__tdv
        overload_attribute(SeriesType, lozn__tdv)(create_unsupported_overload
            (uic__sknuo))
    for fname in series_unsupported_methods:
        uic__sknuo = 'Series.' + fname
        overload_method(SeriesType, fname, no_unliteral=True)(
            create_unsupported_overload(uic__sknuo))


_install_series_unsupported()
heter_series_unsupported_attrs = {'axes', 'array', 'dtype', 'nbytes',
    'memory_usage', 'hasnans', 'dtypes', 'flags', 'at', 'is_unique',
    'is_monotonic', 'is_monotonic_increasing', 'is_monotonic_decreasing',
    'dt', 'str', 'cat', 'sparse', 'attrs'}
heter_series_unsupported_methods = {'set_flags', 'convert_dtypes',
    'infer_objects', 'copy', 'bool', 'to_numpy', 'to_period',
    'to_timestamp', 'to_list', 'tolist', '__array__', 'get', 'at', 'iat',
    'iloc', 'loc', '__iter__', 'items', 'iteritems', 'keys', 'pop', 'item',
    'xs', 'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'pow',
    'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow',
    'combine', 'combine_first', 'round', 'lt', 'gt', 'le', 'ge', 'ne', 'eq',
    'product', 'dot', 'apply', 'agg', 'aggregate', 'transform', 'map',
    'groupby', 'rolling', 'expanding', 'ewm', 'pipe', 'abs', 'all', 'any',
    'autocorr', 'between', 'clip', 'corr', 'count', 'cov', 'cummax',
    'cummin', 'cumprod', 'cumsum', 'describe', 'diff', 'factorize', 'kurt',
    'mad', 'max', 'mean', 'median', 'min', 'mode', 'nlargest', 'nsmallest',
    'pct_change', 'prod', 'quantile', 'rank', 'sem', 'skew', 'std', 'sum',
    'var', 'kurtosis', 'unique', 'nunique', 'value_counts', 'align', 'drop',
    'droplevel', 'drop_duplicates', 'duplicated', 'equals', 'first', 'head',
    'idxmax', 'idxmin', 'isin', 'last', 'reindex', 'reindex_like', 'rename',
    'rename_axis', 'reset_index', 'sample', 'set_axis', 'take', 'tail',
    'truncate', 'where', 'mask', 'add_prefix', 'add_suffix', 'filter',
    'backfill', 'bfill', 'dropna', 'ffill', 'fillna', 'interpolate', 'isna',
    'isnull', 'notna', 'notnull', 'pad', 'replace', 'argsort', 'argmin',
    'argmax', 'reorder_levels', 'sort_values', 'sort_index', 'swaplevel',
    'unstack', 'explode', 'searchsorted', 'ravel', 'repeat', 'squeeze',
    'view', 'append', 'compare', 'update', 'asfreq', 'asof', 'shift',
    'first_valid_index', 'last_valid_index', 'resample', 'tz_convert',
    'tz_localize', 'at_time', 'between_time', 'tshift', 'slice_shift',
    'plot', 'hist', 'to_pickle', 'to_csv', 'to_dict', 'to_excel',
    'to_frame', 'to_xarray', 'to_hdf', 'to_sql', 'to_json', 'to_string',
    'to_clipboard', 'to_latex', 'to_markdown'}


def _install_heter_series_unsupported():
    for lozn__tdv in heter_series_unsupported_attrs:
        uic__sknuo = 'HeterogeneousSeries.' + lozn__tdv
        overload_attribute(HeterogeneousSeriesType, lozn__tdv)(
            create_unsupported_overload(uic__sknuo))
    for fname in heter_series_unsupported_methods:
        uic__sknuo = 'HeterogeneousSeries.' + fname
        overload_method(HeterogeneousSeriesType, fname, no_unliteral=True)(
            create_unsupported_overload(uic__sknuo))


_install_heter_series_unsupported()
