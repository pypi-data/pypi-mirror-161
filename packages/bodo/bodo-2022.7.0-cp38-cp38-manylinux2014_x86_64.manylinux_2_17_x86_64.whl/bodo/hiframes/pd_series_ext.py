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
            rmeg__kqm = (self.index if self.index == other.index else self.
                index.unify(typingctx, other.index))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if other.dtype == self.dtype or not other.dtype.is_precise():
                return SeriesType(self.dtype, self.data.unify(typingctx,
                    other.data), rmeg__kqm, dist=dist)
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
    ysiwb__nrl = get_series_payload(context, builder, sig.args[0], args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].data))
    return impl(builder, (ysiwb__nrl.data,))


@infer_getattr
class HeterSeriesAttribute(OverloadedKeyAttributeTemplate):
    key = HeterogeneousSeriesType

    def generic_resolve(self, S, attr):
        from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
        if self._is_existing_attr(attr):
            return
        if isinstance(S.index, HeterogeneousIndexType
            ) and is_overload_constant_tuple(S.index.data):
            bvhj__sgxwv = get_overload_const_tuple(S.index.data)
            if attr in bvhj__sgxwv:
                epdgz__dakr = bvhj__sgxwv.index(attr)
                return S.data[epdgz__dakr]


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
        zvvl__dcdxb = [('data', fe_type.series_type.data), ('index',
            fe_type.series_type.index), ('name', fe_type.series_type.name_typ)]
        super(SeriesPayloadModel, self).__init__(dmm, fe_type, zvvl__dcdxb)


@register_model(HeterogeneousSeriesType)
@register_model(SeriesType)
class SeriesModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = SeriesPayloadType(fe_type)
        zvvl__dcdxb = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(SeriesModel, self).__init__(dmm, fe_type, zvvl__dcdxb)


def define_series_dtor(context, builder, series_type, payload_type):
    ysygv__kjply = builder.module
    lay__yyn = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    kpd__ccqu = cgutils.get_or_insert_function(ysygv__kjply, lay__yyn, name
        ='.dtor.series.{}'.format(series_type))
    if not kpd__ccqu.is_declaration:
        return kpd__ccqu
    kpd__ccqu.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(kpd__ccqu.append_basic_block())
    yqc__son = kpd__ccqu.args[0]
    layz__qbkh = context.get_value_type(payload_type).as_pointer()
    sund__zso = builder.bitcast(yqc__son, layz__qbkh)
    lcqob__vumhb = context.make_helper(builder, payload_type, ref=sund__zso)
    context.nrt.decref(builder, series_type.data, lcqob__vumhb.data)
    context.nrt.decref(builder, series_type.index, lcqob__vumhb.index)
    context.nrt.decref(builder, series_type.name_typ, lcqob__vumhb.name)
    builder.ret_void()
    return kpd__ccqu


def construct_series(context, builder, series_type, data_val, index_val,
    name_val):
    payload_type = SeriesPayloadType(series_type)
    ysiwb__nrl = cgutils.create_struct_proxy(payload_type)(context, builder)
    ysiwb__nrl.data = data_val
    ysiwb__nrl.index = index_val
    ysiwb__nrl.name = name_val
    fxz__vshi = context.get_value_type(payload_type)
    hfztz__zjxvp = context.get_abi_sizeof(fxz__vshi)
    krz__ucjru = define_series_dtor(context, builder, series_type, payload_type
        )
    tfag__dwt = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, hfztz__zjxvp), krz__ucjru)
    pbtlp__fkf = context.nrt.meminfo_data(builder, tfag__dwt)
    dihax__cdaas = builder.bitcast(pbtlp__fkf, fxz__vshi.as_pointer())
    builder.store(ysiwb__nrl._getvalue(), dihax__cdaas)
    series = cgutils.create_struct_proxy(series_type)(context, builder)
    series.meminfo = tfag__dwt
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
        mfym__ckp = construct_series(context, builder, series_type,
            data_val, index_val, name_val)
        context.nrt.incref(builder, signature.args[0], data_val)
        context.nrt.incref(builder, signature.args[1], index_val)
        context.nrt.incref(builder, signature.args[2], name_val)
        return mfym__ckp
    if is_heterogeneous_tuple_type(data):
        pol__fkyv = HeterogeneousSeriesType(data, index, name)
    else:
        dtype = data.dtype
        data = if_series_to_array_type(data)
        pol__fkyv = SeriesType(dtype, data, index, name)
    sig = signature(pol__fkyv, data, index, name)
    return sig, codegen


def init_series_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) >= 2 and not kws
    data = args[0]
    index = args[1]
    rmxy__fgyb = self.typemap[data.name]
    if is_heterogeneous_tuple_type(rmxy__fgyb) or isinstance(rmxy__fgyb,
        types.BaseTuple):
        return None
    zlrd__pgevw = self.typemap[index.name]
    if not isinstance(zlrd__pgevw, HeterogeneousIndexType
        ) and equiv_set.has_shape(data) and equiv_set.has_shape(index):
        equiv_set.insert_equiv(data, index)
    if equiv_set.has_shape(data):
        return ArrayAnalysis.AnalyzeResult(shape=data, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_init_series = (
    init_series_equiv)


def get_series_payload(context, builder, series_type, value):
    tfag__dwt = cgutils.create_struct_proxy(series_type)(context, builder,
        value).meminfo
    payload_type = SeriesPayloadType(series_type)
    lcqob__vumhb = context.nrt.meminfo_data(builder, tfag__dwt)
    layz__qbkh = context.get_value_type(payload_type).as_pointer()
    lcqob__vumhb = builder.bitcast(lcqob__vumhb, layz__qbkh)
    return context.make_helper(builder, payload_type, ref=lcqob__vumhb)


@intrinsic
def get_series_data(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        ysiwb__nrl = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, series_typ.data,
            ysiwb__nrl.data)
    pol__fkyv = series_typ.data
    sig = signature(pol__fkyv, series_typ)
    return sig, codegen


@intrinsic
def get_series_index(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        ysiwb__nrl = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, series_typ.index,
            ysiwb__nrl.index)
    pol__fkyv = series_typ.index
    sig = signature(pol__fkyv, series_typ)
    return sig, codegen


@intrinsic
def get_series_name(typingctx, series_typ=None):

    def codegen(context, builder, signature, args):
        ysiwb__nrl = get_series_payload(context, builder, signature.args[0],
            args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            ysiwb__nrl.name)
    sig = signature(series_typ.name_typ, series_typ)
    return sig, codegen


def get_series_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    dcz__nxus = args[0]
    rmxy__fgyb = self.typemap[dcz__nxus.name].data
    if is_heterogeneous_tuple_type(rmxy__fgyb) or isinstance(rmxy__fgyb,
        types.BaseTuple):
        return None
    if equiv_set.has_shape(dcz__nxus):
        return ArrayAnalysis.AnalyzeResult(shape=dcz__nxus, pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_series_ext_get_series_data
    ) = get_series_data_equiv


def get_series_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    dcz__nxus = args[0]
    zlrd__pgevw = self.typemap[dcz__nxus.name].index
    if isinstance(zlrd__pgevw, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(dcz__nxus):
        return ArrayAnalysis.AnalyzeResult(shape=dcz__nxus, pre=[])
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
        ysiwb__nrl = get_series_payload(context, builder, fromty, val)
        rmeg__kqm = context.cast(builder, ysiwb__nrl.index, fromty.index,
            toty.index)
        context.nrt.incref(builder, fromty.data, ysiwb__nrl.data)
        context.nrt.incref(builder, fromty.name_typ, ysiwb__nrl.name)
        return construct_series(context, builder, toty, ysiwb__nrl.data,
            rmeg__kqm, ysiwb__nrl.name)
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
        aitf__vdvg = 'Series.head'
        ewfwf__wlmt = 'n',
        fouc__yeij = {'n': 5}
        pysig, zmnxu__qbun = bodo.utils.typing.fold_typing_args(aitf__vdvg,
            args, kws, ewfwf__wlmt, fouc__yeij)
        pxmlp__hngnz = zmnxu__qbun[0]
        if not is_overload_int(pxmlp__hngnz):
            raise BodoError(f"{aitf__vdvg}(): 'n' must be an Integer")
        xuiww__pxjyu = ary
        return xuiww__pxjyu(*zmnxu__qbun).replace(pysig=pysig)

    def _resolve_map_func(self, ary, func, pysig, fname, f_args=None, kws=None
        ):
        dtype = ary.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ary,
            'Series.map()')
        if dtype == types.NPDatetime('ns'):
            dtype = pd_timestamp_type
        if dtype == types.NPTimedelta('ns'):
            dtype = pd_timedelta_type
        yyjt__iinve = dtype,
        if f_args is not None:
            yyjt__iinve += tuple(f_args.types)
        if kws is None:
            kws = {}
        dutd__wzpt = False
        ebv__vlomj = True
        if fname == 'map' and isinstance(func, types.DictType):
            edulw__anaui = func.value_type
            dutd__wzpt = True
        else:
            try:
                if types.unliteral(func) == types.unicode_type:
                    if not is_overload_constant_str(func):
                        raise BodoError(
                            f'Series.apply(): string argument (for builtins) must be a compile time constant'
                            )
                    edulw__anaui = (bodo.utils.transform.
                        get_udf_str_return_type(ary, get_overload_const_str
                        (func), self.context, 'Series.apply'))
                    ebv__vlomj = False
                elif bodo.utils.typing.is_numpy_ufunc(func):
                    edulw__anaui = func.get_call_type(self.context, (ary,), {}
                        ).return_type
                    ebv__vlomj = False
                else:
                    edulw__anaui = get_const_func_output_type(func,
                        yyjt__iinve, kws, self.context, numba.core.registry
                        .cpu_target.target_context)
            except Exception as fcqlb__jbav:
                raise BodoError(get_udf_error_msg(f'Series.{fname}()',
                    fcqlb__jbav))
        if ebv__vlomj:
            if isinstance(edulw__anaui, (SeriesType, HeterogeneousSeriesType)
                ) and edulw__anaui.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(edulw__anaui, HeterogeneousSeriesType):
                hfqr__gefea, dvptm__kxocv = edulw__anaui.const_info
                if isinstance(edulw__anaui.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    kynp__jsl = edulw__anaui.data.tuple_typ.types
                elif isinstance(edulw__anaui.data, types.Tuple):
                    kynp__jsl = edulw__anaui.data.types
                uvaqa__gisw = tuple(to_nullable_type(dtype_to_array_type(t)
                    ) for t in kynp__jsl)
                zus__sdbmo = bodo.DataFrameType(uvaqa__gisw, ary.index,
                    dvptm__kxocv)
            elif isinstance(edulw__anaui, SeriesType):
                ksru__osom, dvptm__kxocv = edulw__anaui.const_info
                uvaqa__gisw = tuple(to_nullable_type(dtype_to_array_type(
                    edulw__anaui.dtype)) for hfqr__gefea in range(ksru__osom))
                zus__sdbmo = bodo.DataFrameType(uvaqa__gisw, ary.index,
                    dvptm__kxocv)
            else:
                vgsx__iarv = get_udf_out_arr_type(edulw__anaui, dutd__wzpt)
                zus__sdbmo = SeriesType(vgsx__iarv.dtype, vgsx__iarv, ary.
                    index, ary.name_typ)
        else:
            zus__sdbmo = edulw__anaui
        return signature(zus__sdbmo, (func,)).replace(pysig=pysig)

    @bound_function('series.map', no_unliteral=True)
    def resolve_map(self, ary, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws['arg']
        kws.pop('arg', None)
        na_action = args[1] if len(args) > 1 else kws.pop('na_action',
            types.none)
        pbv__xezsk = dict(na_action=na_action)
        lyyvn__rzk = dict(na_action=None)
        check_unsupported_args('Series.map', pbv__xezsk, lyyvn__rzk,
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
        xfakq__vzwbt = args[1] if len(args) > 1 else kws.pop('convert_dtype',
            types.literal(True))
        f_args = args[2] if len(args) > 2 else kws.pop('args', None)
        pbv__xezsk = dict(convert_dtype=xfakq__vzwbt)
        wobrr__qwag = dict(convert_dtype=True)
        check_unsupported_args('Series.apply', pbv__xezsk, wobrr__qwag,
            package_name='pandas', module_name='Series')
        dqzu__fby = ', '.join("{} = ''".format(iffxf__hwx) for iffxf__hwx in
            kws.keys())
        rqh__qben = (
            f'def apply_stub(func, convert_dtype=True, args=(), {dqzu__fby}):\n'
            )
        rqh__qben += '    pass\n'
        wqlli__jqrh = {}
        exec(rqh__qben, {}, wqlli__jqrh)
        pqu__cpjnn = wqlli__jqrh['apply_stub']
        pysig = numba.core.utils.pysignature(pqu__cpjnn)
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
        gfku__miepy = ary.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ary,
            'Series.combine()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
            'Series.combine()')
        if gfku__miepy == types.NPDatetime('ns'):
            gfku__miepy = pd_timestamp_type
        ihdb__bazx = other.dtype
        if ihdb__bazx == types.NPDatetime('ns'):
            ihdb__bazx = pd_timestamp_type
        edulw__anaui = get_const_func_output_type(func, (gfku__miepy,
            ihdb__bazx), {}, self.context, numba.core.registry.cpu_target.
            target_context)
        sig = signature(SeriesType(edulw__anaui, index=ary.index, name_typ=
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
            bvhj__sgxwv = get_overload_const_tuple(S.index.data)
            if attr in bvhj__sgxwv:
                epdgz__dakr = bvhj__sgxwv.index(attr)
                return S.data[epdgz__dakr]


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
    cskn__gyv = is_overload_none(data)
    wdqz__nto = is_overload_none(index)
    igx__dxy = is_overload_none(dtype)
    if cskn__gyv and wdqz__nto and igx__dxy:
        raise BodoError(
            'pd.Series() requires at least 1 of data, index, and dtype to not be none'
            )
    if is_series_type(data) and not wdqz__nto:
        raise BodoError(
            'pd.Series() does not support index value when input data is a Series'
            )
    if isinstance(data, types.DictType):
        raise_bodo_error(
            'pd.Series(): When intializing series with a dictionary, it is required that the dict has constant keys'
            )
    if is_heterogeneous_tuple_type(data) and is_overload_none(dtype):
        kpzsd__hrrl = tuple(len(data) * [False])

        def impl_heter(data=None, index=None, dtype=None, name=None, copy=
            False, fastpath=False):
            ideaw__udqlj = bodo.utils.conversion.extract_index_if_none(data,
                index)
            bfy__lkjq = bodo.utils.conversion.to_tuple(data)
            data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(
                bfy__lkjq, kpzsd__hrrl)
            return bodo.hiframes.pd_series_ext.init_series(data_val, bodo.
                utils.conversion.convert_to_index(ideaw__udqlj), name)
        return impl_heter
    if cskn__gyv:
        if igx__dxy:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                wdq__hobyd = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                ideaw__udqlj = bodo.utils.conversion.extract_index_if_none(data
                    , index)
                numba.parfors.parfor.init_prange()
                ilseg__rqcp = len(ideaw__udqlj)
                bfy__lkjq = np.empty(ilseg__rqcp, np.float64)
                for oxi__eknab in numba.parfors.parfor.internal_prange(
                    ilseg__rqcp):
                    bodo.libs.array_kernels.setna(bfy__lkjq, oxi__eknab)
                return bodo.hiframes.pd_series_ext.init_series(bfy__lkjq,
                    bodo.utils.conversion.convert_to_index(ideaw__udqlj),
                    wdq__hobyd)
            return impl
        if bodo.utils.conversion._is_str_dtype(dtype):
            mfdgb__uedxr = bodo.string_array_type
        else:
            ejo__udk = bodo.utils.typing.parse_dtype(dtype, 'pandas.Series')
            if isinstance(ejo__udk, bodo.libs.int_arr_ext.IntDtype):
                mfdgb__uedxr = bodo.IntegerArrayType(ejo__udk.dtype)
            elif ejo__udk == bodo.libs.bool_arr_ext.boolean_dtype:
                mfdgb__uedxr = bodo.boolean_array
            elif isinstance(ejo__udk, types.Number) or ejo__udk in [bodo.
                datetime64ns, bodo.timedelta64ns]:
                mfdgb__uedxr = types.Array(ejo__udk, 1, 'C')
            else:
                raise BodoError(
                    'pd.Series with dtype: {dtype} not currently supported')
        if wdqz__nto:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                wdq__hobyd = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                ideaw__udqlj = bodo.hiframes.pd_index_ext.init_range_index(
                    0, 0, 1, None)
                numba.parfors.parfor.init_prange()
                ilseg__rqcp = len(ideaw__udqlj)
                bfy__lkjq = bodo.utils.utils.alloc_type(ilseg__rqcp,
                    mfdgb__uedxr, (-1,))
                return bodo.hiframes.pd_series_ext.init_series(bfy__lkjq,
                    ideaw__udqlj, wdq__hobyd)
            return impl
        else:

            def impl(data=None, index=None, dtype=None, name=None, copy=
                False, fastpath=False):
                wdq__hobyd = bodo.utils.conversion.extract_name_if_none(data,
                    name)
                ideaw__udqlj = bodo.utils.conversion.extract_index_if_none(data
                    , index)
                numba.parfors.parfor.init_prange()
                ilseg__rqcp = len(ideaw__udqlj)
                bfy__lkjq = bodo.utils.utils.alloc_type(ilseg__rqcp,
                    mfdgb__uedxr, (-1,))
                for oxi__eknab in numba.parfors.parfor.internal_prange(
                    ilseg__rqcp):
                    bodo.libs.array_kernels.setna(bfy__lkjq, oxi__eknab)
                return bodo.hiframes.pd_series_ext.init_series(bfy__lkjq,
                    bodo.utils.conversion.convert_to_index(ideaw__udqlj),
                    wdq__hobyd)
            return impl

    def impl(data=None, index=None, dtype=None, name=None, copy=False,
        fastpath=False):
        wdq__hobyd = bodo.utils.conversion.extract_name_if_none(data, name)
        ideaw__udqlj = bodo.utils.conversion.extract_index_if_none(data, index)
        dhiqu__zyds = bodo.utils.conversion.coerce_to_array(data, True,
            scalar_to_arr_len=len(ideaw__udqlj))
        udfa__apahx = bodo.utils.conversion.fix_arr_dtype(dhiqu__zyds,
            dtype, None, False)
        return bodo.hiframes.pd_series_ext.init_series(udfa__apahx, bodo.
            utils.conversion.convert_to_index(ideaw__udqlj), wdq__hobyd)
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
        tvaig__vmc = pyval.array
    else:
        tvaig__vmc = pyval.values
    data_val = context.get_constant_generic(builder, series_type.data,
        tvaig__vmc)
    index_val = context.get_constant_generic(builder, series_type.index,
        pyval.index)
    name_val = context.get_constant_generic(builder, series_type.name_typ,
        pyval.name)
    lcqob__vumhb = lir.Constant.literal_struct([data_val, index_val, name_val])
    lcqob__vumhb = cgutils.global_constant(builder, '.const.payload',
        lcqob__vumhb).bitcast(cgutils.voidptr_t)
    kew__gke = context.get_constant(types.int64, -1)
    lnywd__gbljn = context.get_constant_null(types.voidptr)
    tfag__dwt = lir.Constant.literal_struct([kew__gke, lnywd__gbljn,
        lnywd__gbljn, lcqob__vumhb, kew__gke])
    tfag__dwt = cgutils.global_constant(builder, '.const.meminfo', tfag__dwt
        ).bitcast(cgutils.voidptr_t)
    mfym__ckp = lir.Constant.literal_struct([tfag__dwt, lnywd__gbljn])
    return mfym__ckp


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
    for pfgl__mbprw in series_unsupported_attrs:
        zgxo__ybx = 'Series.' + pfgl__mbprw
        overload_attribute(SeriesType, pfgl__mbprw)(create_unsupported_overload
            (zgxo__ybx))
    for fname in series_unsupported_methods:
        zgxo__ybx = 'Series.' + fname
        overload_method(SeriesType, fname, no_unliteral=True)(
            create_unsupported_overload(zgxo__ybx))


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
    for pfgl__mbprw in heter_series_unsupported_attrs:
        zgxo__ybx = 'HeterogeneousSeries.' + pfgl__mbprw
        overload_attribute(HeterogeneousSeriesType, pfgl__mbprw)(
            create_unsupported_overload(zgxo__ybx))
    for fname in heter_series_unsupported_methods:
        zgxo__ybx = 'HeterogeneousSeries.' + fname
        overload_method(HeterogeneousSeriesType, fname, no_unliteral=True)(
            create_unsupported_overload(zgxo__ybx))


_install_heter_series_unsupported()
