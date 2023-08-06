"""
Implement pd.DataFrame typing and data model handling.
"""
import json
import operator
from functools import cached_property
from urllib.parse import quote
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.cpython.listobj import ListInstance
from numba.extending import infer_getattr, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_index_ext import HeterogeneousIndexType, NumericIndexType, RangeIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.hiframes.series_indexing import SeriesIlocType
from bodo.hiframes.table import Table, TableType, decode_if_dict_table, get_table_data, set_table_data_codegen
from bodo.io import json_cpp
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_table_to_cpp_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import str_arr_from_sequence
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.conversion import fix_arr_dtype, index_to_array
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_const_func_output_type
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, decode_if_dict_array, dtype_to_array_type, get_index_data_arr_types, get_literal_value, get_overload_const, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_udf_error_msg, get_udf_out_arr_type, is_heterogeneous_tuple_type, is_iterable_type, is_literal_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_str_arr_type, is_tuple_like_type, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array
from bodo.utils.utils import is_null_pointer
_json_write = types.ExternalFunction('json_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.bool_,
    types.voidptr, types.voidptr))
ll.add_symbol('json_write', json_cpp.json_write)


class DataFrameType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, data=None, index=None, columns=None, dist=None,
        is_table_format=False):
        from bodo.transforms.distributed_analysis import Distribution
        self.data = data
        if index is None:
            index = RangeIndexType(types.none)
        self.index = index
        self.columns = columns
        dist = Distribution.OneD_Var if dist is None else dist
        self.dist = dist
        self.is_table_format = is_table_format
        if columns is None:
            assert is_table_format, 'Determining columns at runtime is only supported for DataFrame with table format'
            self.table_type = TableType(tuple(data[:-1]), True)
        else:
            self.table_type = TableType(data) if is_table_format else None
        super(DataFrameType, self).__init__(name=
            f'dataframe({data}, {index}, {columns}, {dist}, {is_table_format}, {self.has_runtime_cols})'
            )

    def __str__(self):
        if not self.has_runtime_cols and len(self.columns) > 20:
            wqux__est = f'{len(self.data)} columns of types {set(self.data)}'
            ftr__rhjzs = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({wqux__est}, {self.index}, {ftr__rhjzs}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
                )
        return super().__str__()

    def copy(self, data=None, index=None, columns=None, dist=None,
        is_table_format=None):
        if data is None:
            data = self.data
        if columns is None:
            columns = self.columns
        if index is None:
            index = self.index
        if dist is None:
            dist = self.dist
        if is_table_format is None:
            is_table_format = self.is_table_format
        return DataFrameType(data, index, columns, dist, is_table_format)

    @property
    def has_runtime_cols(self):
        return self.columns is None

    @cached_property
    def column_index(self):
        return {iqdm__ahiu: i for i, iqdm__ahiu in enumerate(self.columns)}

    @property
    def runtime_colname_typ(self):
        return self.data[-1] if self.has_runtime_cols else None

    @property
    def runtime_data_types(self):
        return self.data[:-1] if self.has_runtime_cols else self.data

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return (self.data, self.index, self.columns, self.dist, self.
            is_table_format)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    def unify(self, typingctx, other):
        from bodo.transforms.distributed_analysis import Distribution
        if (isinstance(other, DataFrameType) and len(other.data) == len(
            self.data) and other.columns == self.columns and other.
            has_runtime_cols == self.has_runtime_cols):
            bigvk__ktk = (self.index if self.index == other.index else self
                .index.unify(typingctx, other.index))
            data = tuple(akxx__mymda.unify(typingctx, zcfjc__mcrr) if 
                akxx__mymda != zcfjc__mcrr else akxx__mymda for akxx__mymda,
                zcfjc__mcrr in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if bigvk__ktk is not None and None not in data:
                return DataFrameType(data, bigvk__ktk, self.columns, dist,
                    self.is_table_format)
        if isinstance(other, DataFrameType) and len(self.data
            ) == 0 and not self.has_runtime_cols:
            return other

    def can_convert_to(self, typingctx, other):
        from numba.core.typeconv import Conversion
        if (isinstance(other, DataFrameType) and self.data == other.data and
            self.index == other.index and self.columns == other.columns and
            self.dist != other.dist and self.has_runtime_cols == other.
            has_runtime_cols):
            return Conversion.safe

    def is_precise(self):
        return all(akxx__mymda.is_precise() for akxx__mymda in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        jzd__tuc = self.columns.index(col_name)
        qao__gnqs = tuple(list(self.data[:jzd__tuc]) + [new_type] + list(
            self.data[jzd__tuc + 1:]))
        return DataFrameType(qao__gnqs, self.index, self.columns, self.dist,
            self.is_table_format)


def check_runtime_cols_unsupported(df, func_name):
    if isinstance(df, DataFrameType) and df.has_runtime_cols:
        raise BodoError(
            f'{func_name} on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information.'
            )


class DataFramePayloadType(types.Type):

    def __init__(self, df_type):
        self.df_type = df_type
        super(DataFramePayloadType, self).__init__(name=
            f'DataFramePayloadType({df_type})')

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFramePayloadType)
class DataFramePayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        data_typ = types.Tuple(fe_type.df_type.data)
        if fe_type.df_type.is_table_format:
            data_typ = types.Tuple([fe_type.df_type.table_type])
        rode__arhio = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            rode__arhio.append(('columns', fe_type.df_type.runtime_colname_typ)
                )
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, rode__arhio)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        rode__arhio = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, rode__arhio)


make_attribute_wrapper(DataFrameType, 'meminfo', '_meminfo')


@infer_getattr
class DataFrameAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])

    @bound_function('df.head')
    def resolve_head(self, df, args, kws):
        func_name = 'DataFrame.head'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        ybpk__hinbs = 'n',
        wzni__vcdvt = {'n': 5}
        bzm__vzpk, tkvgt__lmcn = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, ybpk__hinbs, wzni__vcdvt)
        bbqgj__wrquj = tkvgt__lmcn[0]
        if not is_overload_int(bbqgj__wrquj):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        ako__xffq = df.copy()
        return ako__xffq(*tkvgt__lmcn).replace(pysig=bzm__vzpk)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        bzhp__mrc = (df,) + args
        ybpk__hinbs = 'df', 'method', 'min_periods'
        wzni__vcdvt = {'method': 'pearson', 'min_periods': 1}
        uzt__iazb = 'method',
        bzm__vzpk, tkvgt__lmcn = bodo.utils.typing.fold_typing_args(func_name,
            bzhp__mrc, kws, ybpk__hinbs, wzni__vcdvt, uzt__iazb)
        fcx__wheab = tkvgt__lmcn[2]
        if not is_overload_int(fcx__wheab):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        lwkha__ehkf = []
        jpo__zgi = []
        for iqdm__ahiu, bddd__ybtv in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(bddd__ybtv.dtype):
                lwkha__ehkf.append(iqdm__ahiu)
                jpo__zgi.append(types.Array(types.float64, 1, 'A'))
        if len(lwkha__ehkf) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        jpo__zgi = tuple(jpo__zgi)
        lwkha__ehkf = tuple(lwkha__ehkf)
        index_typ = bodo.utils.typing.type_col_to_index(lwkha__ehkf)
        ako__xffq = DataFrameType(jpo__zgi, index_typ, lwkha__ehkf)
        return ako__xffq(*tkvgt__lmcn).replace(pysig=bzm__vzpk)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        ztbol__mvnds = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        ohiue__cer = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        ykbal__xqqtj = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        aitqw__efw = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        klqfa__zcqgc = dict(raw=ohiue__cer, result_type=ykbal__xqqtj)
        ncy__anr = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', klqfa__zcqgc, ncy__anr,
            package_name='pandas', module_name='DataFrame')
        eiqfo__rujd = True
        if types.unliteral(ztbol__mvnds) == types.unicode_type:
            if not is_overload_constant_str(ztbol__mvnds):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            eiqfo__rujd = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        ssgm__hipvj = get_overload_const_int(axis)
        if eiqfo__rujd and ssgm__hipvj != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif ssgm__hipvj not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        ncq__mmjjr = []
        for arr_typ in df.data:
            hipz__lar = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            clvd__dudt = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(hipz__lar), types.int64), {}
                ).return_type
            ncq__mmjjr.append(clvd__dudt)
        nzgmg__zxex = types.none
        clxt__mhiap = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(iqdm__ahiu) for iqdm__ahiu in df.columns)),
            None)
        esis__flhcd = types.BaseTuple.from_types(ncq__mmjjr)
        avd__ostcl = types.Tuple([types.bool_] * len(esis__flhcd))
        wrgx__phmze = bodo.NullableTupleType(esis__flhcd, avd__ostcl)
        zvg__xjfoy = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if zvg__xjfoy == types.NPDatetime('ns'):
            zvg__xjfoy = bodo.pd_timestamp_type
        if zvg__xjfoy == types.NPTimedelta('ns'):
            zvg__xjfoy = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(esis__flhcd):
            wzn__bsor = HeterogeneousSeriesType(wrgx__phmze, clxt__mhiap,
                zvg__xjfoy)
        else:
            wzn__bsor = SeriesType(esis__flhcd.dtype, wrgx__phmze,
                clxt__mhiap, zvg__xjfoy)
        knqp__qbju = wzn__bsor,
        if aitqw__efw is not None:
            knqp__qbju += tuple(aitqw__efw.types)
        try:
            if not eiqfo__rujd:
                hjz__yckh = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(ztbol__mvnds), self.context,
                    'DataFrame.apply', axis if ssgm__hipvj == 1 else None)
            else:
                hjz__yckh = get_const_func_output_type(ztbol__mvnds,
                    knqp__qbju, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as ccy__jdivc:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', ccy__jdivc)
                )
        if eiqfo__rujd:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(hjz__yckh, (SeriesType, HeterogeneousSeriesType)
                ) and hjz__yckh.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(hjz__yckh, HeterogeneousSeriesType):
                iqv__rwp, spsr__lvyj = hjz__yckh.const_info
                if isinstance(hjz__yckh.data, bodo.libs.nullable_tuple_ext.
                    NullableTupleType):
                    tnjg__dieoz = hjz__yckh.data.tuple_typ.types
                elif isinstance(hjz__yckh.data, types.Tuple):
                    tnjg__dieoz = hjz__yckh.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                ouwr__jcwef = tuple(to_nullable_type(dtype_to_array_type(
                    pkr__lefup)) for pkr__lefup in tnjg__dieoz)
                rcdoo__mwl = DataFrameType(ouwr__jcwef, df.index, spsr__lvyj)
            elif isinstance(hjz__yckh, SeriesType):
                kyjs__icnkd, spsr__lvyj = hjz__yckh.const_info
                ouwr__jcwef = tuple(to_nullable_type(dtype_to_array_type(
                    hjz__yckh.dtype)) for iqv__rwp in range(kyjs__icnkd))
                rcdoo__mwl = DataFrameType(ouwr__jcwef, df.index, spsr__lvyj)
            else:
                bhs__yunai = get_udf_out_arr_type(hjz__yckh)
                rcdoo__mwl = SeriesType(bhs__yunai.dtype, bhs__yunai, df.
                    index, None)
        else:
            rcdoo__mwl = hjz__yckh
        mjxzd__aim = ', '.join("{} = ''".format(akxx__mymda) for
            akxx__mymda in kws.keys())
        pkq__lyakr = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {mjxzd__aim}):
"""
        pkq__lyakr += '    pass\n'
        rqkt__fdngz = {}
        exec(pkq__lyakr, {}, rqkt__fdngz)
        xbb__sqs = rqkt__fdngz['apply_stub']
        bzm__vzpk = numba.core.utils.pysignature(xbb__sqs)
        rrrnj__eofp = (ztbol__mvnds, axis, ohiue__cer, ykbal__xqqtj, aitqw__efw
            ) + tuple(kws.values())
        return signature(rcdoo__mwl, *rrrnj__eofp).replace(pysig=bzm__vzpk)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        ybpk__hinbs = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        wzni__vcdvt = {'x': None, 'y': None, 'kind': 'line', 'figsize':
            None, 'ax': None, 'subplots': False, 'sharex': None, 'sharey': 
            False, 'layout': None, 'use_index': True, 'title': None, 'grid':
            None, 'legend': True, 'style': None, 'logx': False, 'logy': 
            False, 'loglog': False, 'xticks': None, 'yticks': None, 'xlim':
            None, 'ylim': None, 'rot': None, 'fontsize': None, 'colormap':
            None, 'table': False, 'yerr': None, 'xerr': None, 'secondary_y':
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        uzt__iazb = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        bzm__vzpk, tkvgt__lmcn = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, ybpk__hinbs, wzni__vcdvt, uzt__iazb)
        mpbz__hwotr = tkvgt__lmcn[2]
        if not is_overload_constant_str(mpbz__hwotr):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        tlv__kzmje = tkvgt__lmcn[0]
        if not is_overload_none(tlv__kzmje) and not (is_overload_int(
            tlv__kzmje) or is_overload_constant_str(tlv__kzmje)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(tlv__kzmje):
            wkeo__yls = get_overload_const_str(tlv__kzmje)
            if wkeo__yls not in df.columns:
                raise BodoError(f'{func_name}: {wkeo__yls} column not found.')
        elif is_overload_int(tlv__kzmje):
            pixg__mnvg = get_overload_const_int(tlv__kzmje)
            if pixg__mnvg > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {pixg__mnvg} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            tlv__kzmje = df.columns[tlv__kzmje]
        ottvj__irfq = tkvgt__lmcn[1]
        if not is_overload_none(ottvj__irfq) and not (is_overload_int(
            ottvj__irfq) or is_overload_constant_str(ottvj__irfq)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(ottvj__irfq):
            yoap__gkm = get_overload_const_str(ottvj__irfq)
            if yoap__gkm not in df.columns:
                raise BodoError(f'{func_name}: {yoap__gkm} column not found.')
        elif is_overload_int(ottvj__irfq):
            mxx__emt = get_overload_const_int(ottvj__irfq)
            if mxx__emt > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {mxx__emt} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            ottvj__irfq = df.columns[ottvj__irfq]
        hbimx__ighlp = tkvgt__lmcn[3]
        if not is_overload_none(hbimx__ighlp) and not is_tuple_like_type(
            hbimx__ighlp):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        rpi__vhq = tkvgt__lmcn[10]
        if not is_overload_none(rpi__vhq) and not is_overload_constant_str(
            rpi__vhq):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        zagi__pivjs = tkvgt__lmcn[12]
        if not is_overload_bool(zagi__pivjs):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        innnm__yaxu = tkvgt__lmcn[17]
        if not is_overload_none(innnm__yaxu) and not is_tuple_like_type(
            innnm__yaxu):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        vrf__iey = tkvgt__lmcn[18]
        if not is_overload_none(vrf__iey) and not is_tuple_like_type(vrf__iey):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        kqcy__ogkdg = tkvgt__lmcn[22]
        if not is_overload_none(kqcy__ogkdg) and not is_overload_int(
            kqcy__ogkdg):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        scvp__xzxz = tkvgt__lmcn[29]
        if not is_overload_none(scvp__xzxz) and not is_overload_constant_str(
            scvp__xzxz):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        ilgjg__sedv = tkvgt__lmcn[30]
        if not is_overload_none(ilgjg__sedv) and not is_overload_constant_str(
            ilgjg__sedv):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        sazrd__ysbf = types.List(types.mpl_line_2d_type)
        mpbz__hwotr = get_overload_const_str(mpbz__hwotr)
        if mpbz__hwotr == 'scatter':
            if is_overload_none(tlv__kzmje) and is_overload_none(ottvj__irfq):
                raise BodoError(
                    f'{func_name}: {mpbz__hwotr} requires an x and y column.')
            elif is_overload_none(tlv__kzmje):
                raise BodoError(
                    f'{func_name}: {mpbz__hwotr} x column is missing.')
            elif is_overload_none(ottvj__irfq):
                raise BodoError(
                    f'{func_name}: {mpbz__hwotr} y column is missing.')
            sazrd__ysbf = types.mpl_path_collection_type
        elif mpbz__hwotr != 'line':
            raise BodoError(
                f'{func_name}: {mpbz__hwotr} plot is not supported.')
        return signature(sazrd__ysbf, *tkvgt__lmcn).replace(pysig=bzm__vzpk)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            kydhb__scqm = df.columns.index(attr)
            arr_typ = df.data[kydhb__scqm]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            gykm__vnj = []
            qao__gnqs = []
            jocef__zsv = False
            for i, zddy__dsn in enumerate(df.columns):
                if zddy__dsn[0] != attr:
                    continue
                jocef__zsv = True
                gykm__vnj.append(zddy__dsn[1] if len(zddy__dsn) == 2 else
                    zddy__dsn[1:])
                qao__gnqs.append(df.data[i])
            if jocef__zsv:
                return DataFrameType(tuple(qao__gnqs), df.index, tuple(
                    gykm__vnj))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        rehx__xstb = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(rehx__xstb)
        return lambda tup, idx: tup[val_ind]


def decref_df_data(context, builder, payload, df_type):
    if df_type.is_table_format:
        context.nrt.decref(builder, df_type.table_type, builder.
            extract_value(payload.data, 0))
        context.nrt.decref(builder, df_type.index, payload.index)
        if df_type.has_runtime_cols:
            context.nrt.decref(builder, df_type.data[-1], payload.columns)
        return
    for i in range(len(df_type.data)):
        snnn__ysucv = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], snnn__ysucv)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    hwvka__yfl = builder.module
    kqqo__gljgo = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    zmky__pfs = cgutils.get_or_insert_function(hwvka__yfl, kqqo__gljgo,
        name='.dtor.df.{}'.format(df_type))
    if not zmky__pfs.is_declaration:
        return zmky__pfs
    zmky__pfs.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(zmky__pfs.append_basic_block())
    hyhv__gwjm = zmky__pfs.args[0]
    csk__pqd = context.get_value_type(payload_type).as_pointer()
    nsxcy__xwae = builder.bitcast(hyhv__gwjm, csk__pqd)
    payload = context.make_helper(builder, payload_type, ref=nsxcy__xwae)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        lfidj__xfx = context.get_python_api(builder)
        rtqp__yakvy = lfidj__xfx.gil_ensure()
        lfidj__xfx.decref(payload.parent)
        lfidj__xfx.gil_release(rtqp__yakvy)
    builder.ret_void()
    return zmky__pfs


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    cwow__bvjm = cgutils.create_struct_proxy(payload_type)(context, builder)
    cwow__bvjm.data = data_tup
    cwow__bvjm.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        cwow__bvjm.columns = colnames
    oiik__zxpnb = context.get_value_type(payload_type)
    pwm__qpxgr = context.get_abi_sizeof(oiik__zxpnb)
    lzzig__zig = define_df_dtor(context, builder, df_type, payload_type)
    fozim__pds = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, pwm__qpxgr), lzzig__zig)
    ntj__hdfte = context.nrt.meminfo_data(builder, fozim__pds)
    stk__evi = builder.bitcast(ntj__hdfte, oiik__zxpnb.as_pointer())
    usgmt__ermlb = cgutils.create_struct_proxy(df_type)(context, builder)
    usgmt__ermlb.meminfo = fozim__pds
    if parent is None:
        usgmt__ermlb.parent = cgutils.get_null_value(usgmt__ermlb.parent.type)
    else:
        usgmt__ermlb.parent = parent
        cwow__bvjm.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            lfidj__xfx = context.get_python_api(builder)
            rtqp__yakvy = lfidj__xfx.gil_ensure()
            lfidj__xfx.incref(parent)
            lfidj__xfx.gil_release(rtqp__yakvy)
    builder.store(cwow__bvjm._getvalue(), stk__evi)
    return usgmt__ermlb._getvalue()


@intrinsic
def init_runtime_cols_dataframe(typingctx, data_typ, index_typ,
    colnames_index_typ=None):
    assert isinstance(data_typ, types.BaseTuple) and isinstance(data_typ.
        dtype, TableType
        ) and data_typ.dtype.has_runtime_cols, 'init_runtime_cols_dataframe must be called with a table that determines columns at runtime.'
    assert bodo.hiframes.pd_index_ext.is_pd_index_type(colnames_index_typ
        ) or isinstance(colnames_index_typ, bodo.hiframes.
        pd_multi_index_ext.MultiIndexType), 'Column names must be an index'
    if isinstance(data_typ.dtype.arr_types, types.UniTuple):
        atqat__pfshy = [data_typ.dtype.arr_types.dtype] * len(data_typ.
            dtype.arr_types)
    else:
        atqat__pfshy = [pkr__lefup for pkr__lefup in data_typ.dtype.arr_types]
    dcjv__fehf = DataFrameType(tuple(atqat__pfshy + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        blaix__zsoo = construct_dataframe(context, builder, df_type,
            data_tup, index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return blaix__zsoo
    sig = signature(dcjv__fehf, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    kyjs__icnkd = len(data_tup_typ.types)
    if kyjs__icnkd == 0:
        column_names = ()
    pzjo__eqand = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(pzjo__eqand, ColNamesMetaType) and isinstance(pzjo__eqand
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = pzjo__eqand.meta
    if kyjs__icnkd == 1 and isinstance(data_tup_typ.types[0], TableType):
        kyjs__icnkd = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == kyjs__icnkd, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    feq__rewvc = data_tup_typ.types
    if kyjs__icnkd != 0 and isinstance(data_tup_typ.types[0], TableType):
        feq__rewvc = data_tup_typ.types[0].arr_types
        is_table_format = True
    dcjv__fehf = DataFrameType(feq__rewvc, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            bvty__iipw = cgutils.create_struct_proxy(dcjv__fehf.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = bvty__iipw.parent
        blaix__zsoo = construct_dataframe(context, builder, df_type,
            data_tup, index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return blaix__zsoo
    sig = signature(dcjv__fehf, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        usgmt__ermlb = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, usgmt__ermlb.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        cwow__bvjm = get_dataframe_payload(context, builder, df_typ, args[0])
        del__zjqb = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[del__zjqb]
        if df_typ.is_table_format:
            bvty__iipw = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(cwow__bvjm.data, 0))
            ikoyz__nbf = df_typ.table_type.type_to_blk[arr_typ]
            pbl__wghrr = getattr(bvty__iipw, f'block_{ikoyz__nbf}')
            kzw__mgjue = ListInstance(context, builder, types.List(arr_typ),
                pbl__wghrr)
            navxr__vbx = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[del__zjqb])
            snnn__ysucv = kzw__mgjue.getitem(navxr__vbx)
        else:
            snnn__ysucv = builder.extract_value(cwow__bvjm.data, del__zjqb)
        qjna__xlj = cgutils.alloca_once_value(builder, snnn__ysucv)
        iirmj__nvf = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, qjna__xlj, iirmj__nvf)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    fozim__pds = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, fozim__pds)
    csk__pqd = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, csk__pqd)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    dcjv__fehf = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        dcjv__fehf = types.Tuple([TableType(df_typ.data)])
    sig = signature(dcjv__fehf, df_typ)

    def codegen(context, builder, signature, args):
        cwow__bvjm = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            cwow__bvjm.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        cwow__bvjm = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, cwow__bvjm
            .index)
    dcjv__fehf = df_typ.index
    sig = signature(dcjv__fehf, df_typ)
    return sig, codegen


def get_dataframe_data(df, i):
    return df[i]


@infer_global(get_dataframe_data)
class GetDataFrameDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        if not is_overload_constant_int(args[1]):
            raise_bodo_error(
                'Selecting a DataFrame column requires a constant column label'
                )
        df = args[0]
        check_runtime_cols_unsupported(df, 'get_dataframe_data')
        i = get_overload_const_int(args[1])
        ako__xffq = df.data[i]
        return ako__xffq(*args)


GetDataFrameDataInfer.prefer_literal = True


def get_dataframe_data_impl(df, i):
    if df.is_table_format:

        def _impl(df, i):
            if has_parent(df) and _column_needs_unboxing(df, i):
                bodo.hiframes.boxing.unbox_dataframe_column(df, i)
            return get_table_data(_get_dataframe_data(df)[0], i)
        return _impl

    def _impl(df, i):
        if has_parent(df) and _column_needs_unboxing(df, i):
            bodo.hiframes.boxing.unbox_dataframe_column(df, i)
        return _get_dataframe_data(df)[i]
    return _impl


@intrinsic
def get_dataframe_table(typingctx, df_typ=None):
    assert df_typ.is_table_format, 'get_dataframe_table() expects table format'

    def codegen(context, builder, signature, args):
        cwow__bvjm = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(cwow__bvjm.data, 0))
    return df_typ.table_type(df_typ), codegen


def get_dataframe_all_data(df):
    return df.data


def get_dataframe_all_data_impl(df):
    if df.is_table_format:

        def _impl(df):
            return get_dataframe_table(df)
        return _impl
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})' for i in
        range(len(df.columns)))
    yfh__ore = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{yfh__ore})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        ako__xffq = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return ako__xffq(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        cwow__bvjm = get_dataframe_payload(context, builder, signature.args
            [0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, cwow__bvjm.columns)
    return df_typ.runtime_colname_typ(df_typ), codegen


@lower_builtin(get_dataframe_data, DataFrameType, types.IntegerLiteral)
def lower_get_dataframe_data(context, builder, sig, args):
    impl = get_dataframe_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_dataframe_data',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_index',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_table',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_dataframe_all_data',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_dummy_func


def alias_ext_init_dataframe(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 3
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_dataframe',
    'bodo.hiframes.pd_dataframe_ext'] = alias_ext_init_dataframe


def init_dataframe_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 3 and not kws
    data_tup = args[0]
    index = args[1]
    esis__flhcd = self.typemap[data_tup.name]
    if any(is_tuple_like_type(pkr__lefup) for pkr__lefup in esis__flhcd.types):
        return None
    if equiv_set.has_shape(data_tup):
        ifg__dzzc = equiv_set.get_shape(data_tup)
        if len(ifg__dzzc) > 1:
            equiv_set.insert_equiv(*ifg__dzzc)
        if len(ifg__dzzc) > 0:
            clxt__mhiap = self.typemap[index.name]
            if not isinstance(clxt__mhiap, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(ifg__dzzc[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(ifg__dzzc[0], len(
                ifg__dzzc)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    bdbbs__kir = args[0]
    data_types = self.typemap[bdbbs__kir.name].data
    if any(is_tuple_like_type(pkr__lefup) for pkr__lefup in data_types):
        return None
    if equiv_set.has_shape(bdbbs__kir):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            bdbbs__kir)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    bdbbs__kir = args[0]
    clxt__mhiap = self.typemap[bdbbs__kir.name].index
    if isinstance(clxt__mhiap, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(bdbbs__kir):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            bdbbs__kir)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    bdbbs__kir = args[0]
    if equiv_set.has_shape(bdbbs__kir):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            bdbbs__kir), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    bdbbs__kir = args[0]
    if equiv_set.has_shape(bdbbs__kir):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            bdbbs__kir)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    del__zjqb = get_overload_const_int(c_ind_typ)
    if df_typ.data[del__zjqb] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        ctn__exdl, iqv__rwp, huv__wbjk = args
        cwow__bvjm = get_dataframe_payload(context, builder, df_typ, ctn__exdl)
        if df_typ.is_table_format:
            bvty__iipw = cgutils.create_struct_proxy(df_typ.table_type)(context
                , builder, builder.extract_value(cwow__bvjm.data, 0))
            ikoyz__nbf = df_typ.table_type.type_to_blk[arr_typ]
            pbl__wghrr = getattr(bvty__iipw, f'block_{ikoyz__nbf}')
            kzw__mgjue = ListInstance(context, builder, types.List(arr_typ),
                pbl__wghrr)
            navxr__vbx = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[del__zjqb])
            kzw__mgjue.setitem(navxr__vbx, huv__wbjk, True)
        else:
            snnn__ysucv = builder.extract_value(cwow__bvjm.data, del__zjqb)
            context.nrt.decref(builder, df_typ.data[del__zjqb], snnn__ysucv)
            cwow__bvjm.data = builder.insert_value(cwow__bvjm.data,
                huv__wbjk, del__zjqb)
            context.nrt.incref(builder, arr_typ, huv__wbjk)
        usgmt__ermlb = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=ctn__exdl)
        payload_type = DataFramePayloadType(df_typ)
        nsxcy__xwae = context.nrt.meminfo_data(builder, usgmt__ermlb.meminfo)
        csk__pqd = context.get_value_type(payload_type).as_pointer()
        nsxcy__xwae = builder.bitcast(nsxcy__xwae, csk__pqd)
        builder.store(cwow__bvjm._getvalue(), nsxcy__xwae)
        return impl_ret_borrowed(context, builder, df_typ, ctn__exdl)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        qjve__zvn = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        cqyd__anpkv = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=qjve__zvn)
        slpd__eww = get_dataframe_payload(context, builder, df_typ, qjve__zvn)
        usgmt__ermlb = construct_dataframe(context, builder, signature.
            return_type, slpd__eww.data, index_val, cqyd__anpkv.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), slpd__eww.data)
        return usgmt__ermlb
    dcjv__fehf = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(dcjv__fehf, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    kyjs__icnkd = len(df_type.columns)
    sumz__hsxk = kyjs__icnkd
    honw__ler = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    svxkr__wunx = col_name not in df_type.columns
    del__zjqb = kyjs__icnkd
    if svxkr__wunx:
        honw__ler += arr_type,
        column_names += col_name,
        sumz__hsxk += 1
    else:
        del__zjqb = df_type.columns.index(col_name)
        honw__ler = tuple(arr_type if i == del__zjqb else honw__ler[i] for
            i in range(kyjs__icnkd))

    def codegen(context, builder, signature, args):
        ctn__exdl, iqv__rwp, huv__wbjk = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, ctn__exdl)
        jyisv__fng = cgutils.create_struct_proxy(df_type)(context, builder,
            value=ctn__exdl)
        if df_type.is_table_format:
            cvao__sdl = df_type.table_type
            yvcph__uuaiu = builder.extract_value(in_dataframe_payload.data, 0)
            lbuu__zbtb = TableType(honw__ler)
            zjnpu__biqqz = set_table_data_codegen(context, builder,
                cvao__sdl, yvcph__uuaiu, lbuu__zbtb, arr_type, huv__wbjk,
                del__zjqb, svxkr__wunx)
            data_tup = context.make_tuple(builder, types.Tuple([lbuu__zbtb]
                ), [zjnpu__biqqz])
        else:
            feq__rewvc = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != del__zjqb else huv__wbjk) for i in range(
                kyjs__icnkd)]
            if svxkr__wunx:
                feq__rewvc.append(huv__wbjk)
            for bdbbs__kir, badpq__zpe in zip(feq__rewvc, honw__ler):
                context.nrt.incref(builder, badpq__zpe, bdbbs__kir)
            data_tup = context.make_tuple(builder, types.Tuple(honw__ler),
                feq__rewvc)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        nhugr__ehr = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, jyisv__fng.parent, None)
        if not svxkr__wunx and arr_type == df_type.data[del__zjqb]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            nsxcy__xwae = context.nrt.meminfo_data(builder, jyisv__fng.meminfo)
            csk__pqd = context.get_value_type(payload_type).as_pointer()
            nsxcy__xwae = builder.bitcast(nsxcy__xwae, csk__pqd)
            lzpe__llt = get_dataframe_payload(context, builder, df_type,
                nhugr__ehr)
            builder.store(lzpe__llt._getvalue(), nsxcy__xwae)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, lbuu__zbtb, builder.
                    extract_value(data_tup, 0))
            else:
                for bdbbs__kir, badpq__zpe in zip(feq__rewvc, honw__ler):
                    context.nrt.incref(builder, badpq__zpe, bdbbs__kir)
        has_parent = cgutils.is_not_null(builder, jyisv__fng.parent)
        with builder.if_then(has_parent):
            lfidj__xfx = context.get_python_api(builder)
            rtqp__yakvy = lfidj__xfx.gil_ensure()
            qotqn__lch = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, huv__wbjk)
            iqdm__ahiu = numba.core.pythonapi._BoxContext(context, builder,
                lfidj__xfx, qotqn__lch)
            udezd__eri = iqdm__ahiu.pyapi.from_native_value(arr_type,
                huv__wbjk, iqdm__ahiu.env_manager)
            if isinstance(col_name, str):
                fpr__zzq = context.insert_const_string(builder.module, col_name
                    )
                racv__fxgx = lfidj__xfx.string_from_string(fpr__zzq)
            else:
                assert isinstance(col_name, int)
                racv__fxgx = lfidj__xfx.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            lfidj__xfx.object_setitem(jyisv__fng.parent, racv__fxgx, udezd__eri
                )
            lfidj__xfx.decref(udezd__eri)
            lfidj__xfx.decref(racv__fxgx)
            lfidj__xfx.gil_release(rtqp__yakvy)
        return nhugr__ehr
    dcjv__fehf = DataFrameType(honw__ler, index_typ, column_names, df_type.
        dist, df_type.is_table_format)
    sig = signature(dcjv__fehf, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    kyjs__icnkd = len(pyval.columns)
    feq__rewvc = []
    for i in range(kyjs__icnkd):
        ghobr__plpd = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            udezd__eri = ghobr__plpd.array
        else:
            udezd__eri = ghobr__plpd.values
        feq__rewvc.append(udezd__eri)
    feq__rewvc = tuple(feq__rewvc)
    if df_type.is_table_format:
        bvty__iipw = context.get_constant_generic(builder, df_type.
            table_type, Table(feq__rewvc))
        data_tup = lir.Constant.literal_struct([bvty__iipw])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], zddy__dsn) for i,
            zddy__dsn in enumerate(feq__rewvc)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    con__qth = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, con__qth])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    pqkri__fer = context.get_constant(types.int64, -1)
    zpxbi__iaa = context.get_constant_null(types.voidptr)
    fozim__pds = lir.Constant.literal_struct([pqkri__fer, zpxbi__iaa,
        zpxbi__iaa, payload, pqkri__fer])
    fozim__pds = cgutils.global_constant(builder, '.const.meminfo', fozim__pds
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([fozim__pds, con__qth])


@lower_cast(DataFrameType, DataFrameType)
def cast_df_to_df(context, builder, fromty, toty, val):
    if (fromty.data == toty.data and fromty.index == toty.index and fromty.
        columns == toty.columns and fromty.is_table_format == toty.
        is_table_format and fromty.dist != toty.dist and fromty.
        has_runtime_cols == toty.has_runtime_cols):
        return val
    if not fromty.has_runtime_cols and not toty.has_runtime_cols and len(fromty
        .data) == 0 and len(toty.columns):
        return _cast_empty_df(context, builder, toty)
    if len(fromty.data) != len(toty.data) or fromty.data != toty.data and any(
        context.typing_context.unify_pairs(fromty.data[i], toty.data[i]) is
        None for i in range(len(fromty.data))
        ) or fromty.has_runtime_cols != toty.has_runtime_cols:
        raise BodoError(f'Invalid dataframe cast from {fromty} to {toty}')
    in_dataframe_payload = get_dataframe_payload(context, builder, fromty, val)
    if isinstance(fromty.index, RangeIndexType) and isinstance(toty.index,
        NumericIndexType):
        bigvk__ktk = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        bigvk__ktk = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, bigvk__ktk)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        qao__gnqs = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                qao__gnqs)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), qao__gnqs)
    elif not fromty.is_table_format and toty.is_table_format:
        qao__gnqs = _cast_df_data_to_table_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        qao__gnqs = _cast_df_data_to_tuple_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        qao__gnqs = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        qao__gnqs = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, qao__gnqs,
        bigvk__ktk, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    qiwc__yrjcj = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        bmxg__eep = get_index_data_arr_types(toty.index)[0]
        elro__rxeh = bodo.utils.transform.get_type_alloc_counts(bmxg__eep) - 1
        byrsl__sdne = ', '.join('0' for iqv__rwp in range(elro__rxeh))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(byrsl__sdne, ', ' if elro__rxeh == 1 else ''))
        qiwc__yrjcj['index_arr_type'] = bmxg__eep
    sdco__nuyn = []
    for i, arr_typ in enumerate(toty.data):
        elro__rxeh = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        byrsl__sdne = ', '.join('0' for iqv__rwp in range(elro__rxeh))
        qui__bdkn = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, byrsl__sdne, ', ' if elro__rxeh == 1 else ''))
        sdco__nuyn.append(qui__bdkn)
        qiwc__yrjcj[f'arr_type{i}'] = arr_typ
    sdco__nuyn = ', '.join(sdco__nuyn)
    pkq__lyakr = 'def impl():\n'
    ooex__bhltm = bodo.hiframes.dataframe_impl._gen_init_df(pkq__lyakr,
        toty.columns, sdco__nuyn, index, qiwc__yrjcj)
    df = context.compile_internal(builder, ooex__bhltm, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    blp__cwr = toty.table_type
    bvty__iipw = cgutils.create_struct_proxy(blp__cwr)(context, builder)
    bvty__iipw.parent = in_dataframe_payload.parent
    for pkr__lefup, ikoyz__nbf in blp__cwr.type_to_blk.items():
        pqm__zku = context.get_constant(types.int64, len(blp__cwr.
            block_to_arr_ind[ikoyz__nbf]))
        iqv__rwp, wxwuh__mme = ListInstance.allocate_ex(context, builder,
            types.List(pkr__lefup), pqm__zku)
        wxwuh__mme.size = pqm__zku
        setattr(bvty__iipw, f'block_{ikoyz__nbf}', wxwuh__mme.value)
    for i, pkr__lefup in enumerate(fromty.data):
        cnk__azb = toty.data[i]
        if pkr__lefup != cnk__azb:
            ofy__dvqy = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ofy__dvqy)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        snnn__ysucv = builder.extract_value(in_dataframe_payload.data, i)
        if pkr__lefup != cnk__azb:
            wrzhf__cqty = context.cast(builder, snnn__ysucv, pkr__lefup,
                cnk__azb)
            qvay__ery = False
        else:
            wrzhf__cqty = snnn__ysucv
            qvay__ery = True
        ikoyz__nbf = blp__cwr.type_to_blk[pkr__lefup]
        pbl__wghrr = getattr(bvty__iipw, f'block_{ikoyz__nbf}')
        kzw__mgjue = ListInstance(context, builder, types.List(pkr__lefup),
            pbl__wghrr)
        navxr__vbx = context.get_constant(types.int64, blp__cwr.
            block_offsets[i])
        kzw__mgjue.setitem(navxr__vbx, wrzhf__cqty, qvay__ery)
    data_tup = context.make_tuple(builder, types.Tuple([blp__cwr]), [
        bvty__iipw._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    feq__rewvc = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            ofy__dvqy = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ofy__dvqy)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            snnn__ysucv = builder.extract_value(in_dataframe_payload.data, i)
            wrzhf__cqty = context.cast(builder, snnn__ysucv, fromty.data[i],
                toty.data[i])
            qvay__ery = False
        else:
            wrzhf__cqty = builder.extract_value(in_dataframe_payload.data, i)
            qvay__ery = True
        if qvay__ery:
            context.nrt.incref(builder, toty.data[i], wrzhf__cqty)
        feq__rewvc.append(wrzhf__cqty)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), feq__rewvc)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    cvao__sdl = fromty.table_type
    yvcph__uuaiu = cgutils.create_struct_proxy(cvao__sdl)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    lbuu__zbtb = toty.table_type
    zjnpu__biqqz = cgutils.create_struct_proxy(lbuu__zbtb)(context, builder)
    zjnpu__biqqz.parent = in_dataframe_payload.parent
    for pkr__lefup, ikoyz__nbf in lbuu__zbtb.type_to_blk.items():
        pqm__zku = context.get_constant(types.int64, len(lbuu__zbtb.
            block_to_arr_ind[ikoyz__nbf]))
        iqv__rwp, wxwuh__mme = ListInstance.allocate_ex(context, builder,
            types.List(pkr__lefup), pqm__zku)
        wxwuh__mme.size = pqm__zku
        setattr(zjnpu__biqqz, f'block_{ikoyz__nbf}', wxwuh__mme.value)
    for i in range(len(fromty.data)):
        cxxny__onvtv = fromty.data[i]
        cnk__azb = toty.data[i]
        if cxxny__onvtv != cnk__azb:
            ofy__dvqy = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ofy__dvqy)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        tvio__rcwj = cvao__sdl.type_to_blk[cxxny__onvtv]
        monae__clq = getattr(yvcph__uuaiu, f'block_{tvio__rcwj}')
        qwze__bthe = ListInstance(context, builder, types.List(cxxny__onvtv
            ), monae__clq)
        syw__objqt = context.get_constant(types.int64, cvao__sdl.
            block_offsets[i])
        snnn__ysucv = qwze__bthe.getitem(syw__objqt)
        if cxxny__onvtv != cnk__azb:
            wrzhf__cqty = context.cast(builder, snnn__ysucv, cxxny__onvtv,
                cnk__azb)
            qvay__ery = False
        else:
            wrzhf__cqty = snnn__ysucv
            qvay__ery = True
        mut__utxo = lbuu__zbtb.type_to_blk[pkr__lefup]
        wxwuh__mme = getattr(zjnpu__biqqz, f'block_{mut__utxo}')
        pcg__qjz = ListInstance(context, builder, types.List(cnk__azb),
            wxwuh__mme)
        uujw__dka = context.get_constant(types.int64, lbuu__zbtb.
            block_offsets[i])
        pcg__qjz.setitem(uujw__dka, wrzhf__cqty, qvay__ery)
    data_tup = context.make_tuple(builder, types.Tuple([lbuu__zbtb]), [
        zjnpu__biqqz._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    blp__cwr = fromty.table_type
    bvty__iipw = cgutils.create_struct_proxy(blp__cwr)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    feq__rewvc = []
    for i, pkr__lefup in enumerate(toty.data):
        cxxny__onvtv = fromty.data[i]
        if pkr__lefup != cxxny__onvtv:
            ofy__dvqy = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ofy__dvqy)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        ikoyz__nbf = blp__cwr.type_to_blk[pkr__lefup]
        pbl__wghrr = getattr(bvty__iipw, f'block_{ikoyz__nbf}')
        kzw__mgjue = ListInstance(context, builder, types.List(pkr__lefup),
            pbl__wghrr)
        navxr__vbx = context.get_constant(types.int64, blp__cwr.
            block_offsets[i])
        snnn__ysucv = kzw__mgjue.getitem(navxr__vbx)
        if pkr__lefup != cxxny__onvtv:
            wrzhf__cqty = context.cast(builder, snnn__ysucv, cxxny__onvtv,
                pkr__lefup)
            qvay__ery = False
        else:
            wrzhf__cqty = snnn__ysucv
            qvay__ery = True
        if qvay__ery:
            context.nrt.incref(builder, pkr__lefup, wrzhf__cqty)
        feq__rewvc.append(wrzhf__cqty)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), feq__rewvc)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    sdau__kke, sdco__nuyn, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    mbavb__gbo = ColNamesMetaType(tuple(sdau__kke))
    pkq__lyakr = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    pkq__lyakr += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(sdco__nuyn, index_arg))
    rqkt__fdngz = {}
    exec(pkq__lyakr, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': mbavb__gbo}, rqkt__fdngz)
    lkb__nqlhn = rqkt__fdngz['_init_df']
    return lkb__nqlhn


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    dcjv__fehf = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(dcjv__fehf, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    dcjv__fehf = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(dcjv__fehf, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    lhff__lcr = ''
    if not is_overload_none(dtype):
        lhff__lcr = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        kyjs__icnkd = (len(data.types) - 1) // 2
        ijm__etajm = [pkr__lefup.literal_value for pkr__lefup in data.types
            [1:kyjs__icnkd + 1]]
        data_val_types = dict(zip(ijm__etajm, data.types[kyjs__icnkd + 1:]))
        feq__rewvc = ['data[{}]'.format(i) for i in range(kyjs__icnkd + 1, 
            2 * kyjs__icnkd + 1)]
        data_dict = dict(zip(ijm__etajm, feq__rewvc))
        if is_overload_none(index):
            for i, pkr__lefup in enumerate(data.types[kyjs__icnkd + 1:]):
                if isinstance(pkr__lefup, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(kyjs__icnkd + 1 + i))
                    index_is_none = False
                    break
    elif is_overload_none(data):
        data_dict = {}
        data_val_types = {}
    else:
        if not (isinstance(data, types.Array) and data.ndim == 2):
            raise BodoError(
                'pd.DataFrame() only supports constant dictionary and array input'
                )
        if is_overload_none(columns):
            raise BodoError(
                "pd.DataFrame() 'columns' argument is required when an array is passed as data"
                )
        iha__frmt = '.copy()' if copy else ''
        attnk__fevp = get_overload_const_list(columns)
        kyjs__icnkd = len(attnk__fevp)
        data_val_types = {iqdm__ahiu: data.copy(ndim=1) for iqdm__ahiu in
            attnk__fevp}
        feq__rewvc = ['data[:,{}]{}'.format(i, iha__frmt) for i in range(
            kyjs__icnkd)]
        data_dict = dict(zip(attnk__fevp, feq__rewvc))
    if is_overload_none(columns):
        col_names = data_dict.keys()
    else:
        col_names = get_overload_const_list(columns)
    df_len = _get_df_len_from_info(data_dict, data_val_types, col_names,
        index_is_none, index_arg)
    _fill_null_arrays(data_dict, col_names, df_len, dtype)
    if index_is_none:
        if is_overload_none(data):
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_binary_str_index(bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0))'
                )
        else:
            index_arg = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, {}, 1, None)'
                .format(df_len))
    sdco__nuyn = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[iqdm__ahiu], df_len, lhff__lcr) for iqdm__ahiu in
        col_names))
    if len(col_names) == 0:
        sdco__nuyn = '()'
    return col_names, sdco__nuyn, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for iqdm__ahiu in col_names:
        if iqdm__ahiu in data_dict and is_iterable_type(data_val_types[
            iqdm__ahiu]):
            df_len = 'len({})'.format(data_dict[iqdm__ahiu])
            break
    if df_len == '0':
        if not index_is_none:
            df_len = f'len({index_arg})'
        elif data_dict:
            raise BodoError(
                'Internal Error: Unable to determine length of DataFrame Index. If this is unexpected, please try passing an index value.'
                )
    return df_len


def _fill_null_arrays(data_dict, col_names, df_len, dtype):
    if all(iqdm__ahiu in data_dict for iqdm__ahiu in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    obw__lhbdw = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for iqdm__ahiu in col_names:
        if iqdm__ahiu not in data_dict:
            data_dict[iqdm__ahiu] = obw__lhbdw


@infer_global(len)
class LenTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        if isinstance(args[0], (DataFrameType, bodo.TableType)):
            return types.int64(*args)


@lower_builtin(len, DataFrameType)
def table_len_lower(context, builder, sig, args):
    impl = df_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def df_len_overload(df):
    if not isinstance(df, DataFrameType):
        return
    if df.has_runtime_cols:

        def impl(df):
            if is_null_pointer(df._meminfo):
                return 0
            pkr__lefup = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(pkr__lefup)
        return impl
    if len(df.columns) == 0:

        def impl(df):
            if is_null_pointer(df._meminfo):
                return 0
            return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
        return impl

    def impl(df):
        if is_null_pointer(df._meminfo):
            return 0
        return len(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, 0))
    return impl


@infer_global(operator.getitem)
class GetItemTuple(AbstractTemplate):
    key = operator.getitem

    def generic(self, args, kws):
        tup, idx = args
        if not isinstance(tup, types.BaseTuple) or not isinstance(idx,
            types.IntegerLiteral):
            return
        bxwo__ionx = idx.literal_value
        if isinstance(bxwo__ionx, int):
            ako__xffq = tup.types[bxwo__ionx]
        elif isinstance(bxwo__ionx, slice):
            ako__xffq = types.BaseTuple.from_types(tup.types[bxwo__ionx])
        return signature(ako__xffq, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    kmt__flbxe, idx = sig.args
    idx = idx.literal_value
    tup, iqv__rwp = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(kmt__flbxe)
        if not 0 <= idx < len(kmt__flbxe):
            raise IndexError('cannot index at %d in %s' % (idx, kmt__flbxe))
        idqzu__aurfd = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        ghzkb__pbaq = cgutils.unpack_tuple(builder, tup)[idx]
        idqzu__aurfd = context.make_tuple(builder, sig.return_type, ghzkb__pbaq
            )
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, idqzu__aurfd)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, htogc__era, suffix_x,
            suffix_y, is_join, indicator, iqv__rwp, iqv__rwp) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        wlreq__nagfd = {iqdm__ahiu: i for i, iqdm__ahiu in enumerate(left_on)}
        icbx__rwta = {iqdm__ahiu: i for i, iqdm__ahiu in enumerate(right_on)}
        aen__mrla = set(left_on) & set(right_on)
        dsxvo__qsc = set(left_df.columns) & set(right_df.columns)
        vrely__kib = dsxvo__qsc - aen__mrla
        ulo__cwot = '$_bodo_index_' in left_on
        khno__exdxe = '$_bodo_index_' in right_on
        how = get_overload_const_str(htogc__era)
        jnljf__qalw = how in {'left', 'outer'}
        beyhe__tmg = how in {'right', 'outer'}
        columns = []
        data = []
        if ulo__cwot:
            hbznf__caxh = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            hbznf__caxh = left_df.data[left_df.column_index[left_on[0]]]
        if khno__exdxe:
            aizpj__wgmjl = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            aizpj__wgmjl = right_df.data[right_df.column_index[right_on[0]]]
        if ulo__cwot and not khno__exdxe and not is_join.literal_value:
            dfse__eyw = right_on[0]
            if dfse__eyw in left_df.column_index:
                columns.append(dfse__eyw)
                if (aizpj__wgmjl == bodo.dict_str_arr_type and hbznf__caxh ==
                    bodo.string_array_type):
                    vvisu__skhtw = bodo.string_array_type
                else:
                    vvisu__skhtw = aizpj__wgmjl
                data.append(vvisu__skhtw)
        if khno__exdxe and not ulo__cwot and not is_join.literal_value:
            sris__xeb = left_on[0]
            if sris__xeb in right_df.column_index:
                columns.append(sris__xeb)
                if (hbznf__caxh == bodo.dict_str_arr_type and aizpj__wgmjl ==
                    bodo.string_array_type):
                    vvisu__skhtw = bodo.string_array_type
                else:
                    vvisu__skhtw = hbznf__caxh
                data.append(vvisu__skhtw)
        for cxxny__onvtv, ghobr__plpd in zip(left_df.data, left_df.columns):
            columns.append(str(ghobr__plpd) + suffix_x.literal_value if 
                ghobr__plpd in vrely__kib else ghobr__plpd)
            if ghobr__plpd in aen__mrla:
                if cxxny__onvtv == bodo.dict_str_arr_type:
                    cxxny__onvtv = right_df.data[right_df.column_index[
                        ghobr__plpd]]
                data.append(cxxny__onvtv)
            else:
                if (cxxny__onvtv == bodo.dict_str_arr_type and ghobr__plpd in
                    wlreq__nagfd):
                    if khno__exdxe:
                        cxxny__onvtv = aizpj__wgmjl
                    else:
                        utu__tiu = wlreq__nagfd[ghobr__plpd]
                        whc__xllkn = right_on[utu__tiu]
                        cxxny__onvtv = right_df.data[right_df.column_index[
                            whc__xllkn]]
                if beyhe__tmg:
                    cxxny__onvtv = to_nullable_type(cxxny__onvtv)
                data.append(cxxny__onvtv)
        for cxxny__onvtv, ghobr__plpd in zip(right_df.data, right_df.columns):
            if ghobr__plpd not in aen__mrla:
                columns.append(str(ghobr__plpd) + suffix_y.literal_value if
                    ghobr__plpd in vrely__kib else ghobr__plpd)
                if (cxxny__onvtv == bodo.dict_str_arr_type and ghobr__plpd in
                    icbx__rwta):
                    if ulo__cwot:
                        cxxny__onvtv = hbznf__caxh
                    else:
                        utu__tiu = icbx__rwta[ghobr__plpd]
                        wylam__jitek = left_on[utu__tiu]
                        cxxny__onvtv = left_df.data[left_df.column_index[
                            wylam__jitek]]
                if jnljf__qalw:
                    cxxny__onvtv = to_nullable_type(cxxny__onvtv)
                data.append(cxxny__onvtv)
        ytguj__auoxh = get_overload_const_bool(indicator)
        if ytguj__auoxh:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        ccjdj__arlt = False
        if ulo__cwot and khno__exdxe and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            ccjdj__arlt = True
        elif ulo__cwot and not khno__exdxe:
            index_typ = right_df.index
            ccjdj__arlt = True
        elif khno__exdxe and not ulo__cwot:
            index_typ = left_df.index
            ccjdj__arlt = True
        if ccjdj__arlt and isinstance(index_typ, bodo.hiframes.pd_index_ext
            .RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        wuzh__ywk = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(wuzh__ywk, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    usgmt__ermlb = cgutils.create_struct_proxy(sig.return_type)(context,
        builder)
    return usgmt__ermlb._getvalue()


@overload(pd.concat, inline='always', no_unliteral=True)
def concat_overload(objs, axis=0, join='outer', join_axes=None,
    ignore_index=False, keys=None, levels=None, names=None,
    verify_integrity=False, sort=None, copy=True):
    if not is_overload_constant_int(axis):
        raise BodoError("pd.concat(): 'axis' should be a constant integer")
    if not is_overload_constant_bool(ignore_index):
        raise BodoError(
            "pd.concat(): 'ignore_index' should be a constant boolean")
    axis = get_overload_const_int(axis)
    ignore_index = is_overload_true(ignore_index)
    klqfa__zcqgc = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    wzni__vcdvt = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', klqfa__zcqgc, wzni__vcdvt,
        package_name='pandas', module_name='General')
    pkq__lyakr = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        enwwt__sgcog = 0
        sdco__nuyn = []
        names = []
        for i, nhcdq__eobx in enumerate(objs.types):
            assert isinstance(nhcdq__eobx, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(nhcdq__eobx, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                nhcdq__eobx, 'pandas.concat()')
            if isinstance(nhcdq__eobx, SeriesType):
                names.append(str(enwwt__sgcog))
                enwwt__sgcog += 1
                sdco__nuyn.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(nhcdq__eobx.columns)
                for bttl__wqzg in range(len(nhcdq__eobx.data)):
                    sdco__nuyn.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, bttl__wqzg))
        return bodo.hiframes.dataframe_impl._gen_init_df(pkq__lyakr, names,
            ', '.join(sdco__nuyn), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(pkr__lefup, DataFrameType) for pkr__lefup in
            objs.types)
        akp__vgv = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            akp__vgv.extend(df.columns)
        akp__vgv = list(dict.fromkeys(akp__vgv).keys())
        atqat__pfshy = {}
        for enwwt__sgcog, iqdm__ahiu in enumerate(akp__vgv):
            for i, df in enumerate(objs.types):
                if iqdm__ahiu in df.column_index:
                    atqat__pfshy[f'arr_typ{enwwt__sgcog}'] = df.data[df.
                        column_index[iqdm__ahiu]]
                    break
        assert len(atqat__pfshy) == len(akp__vgv)
        vhh__vteeu = []
        for enwwt__sgcog, iqdm__ahiu in enumerate(akp__vgv):
            args = []
            for i, df in enumerate(objs.types):
                if iqdm__ahiu in df.column_index:
                    del__zjqb = df.column_index[iqdm__ahiu]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, del__zjqb))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, enwwt__sgcog))
            pkq__lyakr += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(enwwt__sgcog, ', '.join(args)))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(A0), 1, None)'
                )
        else:
            index = (
                """bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)) if len(objs[i].
                columns) > 0)))
        return bodo.hiframes.dataframe_impl._gen_init_df(pkq__lyakr,
            akp__vgv, ', '.join('A{}'.format(i) for i in range(len(akp__vgv
            ))), index, atqat__pfshy)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(pkr__lefup, SeriesType) for pkr__lefup in
            objs.types)
        pkq__lyakr += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            pkq__lyakr += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            pkq__lyakr += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        pkq__lyakr += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        rqkt__fdngz = {}
        exec(pkq__lyakr, {'bodo': bodo, 'np': np, 'numba': numba}, rqkt__fdngz)
        return rqkt__fdngz['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for enwwt__sgcog, iqdm__ahiu in enumerate(df_type.columns):
            pkq__lyakr += '  arrs{} = []\n'.format(enwwt__sgcog)
            pkq__lyakr += '  for i in range(len(objs)):\n'
            pkq__lyakr += '    df = objs[i]\n'
            pkq__lyakr += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(enwwt__sgcog))
            pkq__lyakr += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(enwwt__sgcog))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            pkq__lyakr += '  arrs_index = []\n'
            pkq__lyakr += '  for i in range(len(objs)):\n'
            pkq__lyakr += '    df = objs[i]\n'
            pkq__lyakr += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(pkq__lyakr,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        pkq__lyakr += '  arrs = []\n'
        pkq__lyakr += '  for i in range(len(objs)):\n'
        pkq__lyakr += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        pkq__lyakr += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            pkq__lyakr += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            pkq__lyakr += '  arrs_index = []\n'
            pkq__lyakr += '  for i in range(len(objs)):\n'
            pkq__lyakr += '    S = objs[i]\n'
            pkq__lyakr += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            pkq__lyakr += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        pkq__lyakr += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        rqkt__fdngz = {}
        exec(pkq__lyakr, {'bodo': bodo, 'np': np, 'numba': numba}, rqkt__fdngz)
        return rqkt__fdngz['impl']
    raise BodoError('pd.concat(): input type {} not supported yet'.format(objs)
        )


def sort_values_dummy(df, by, ascending, inplace, na_position):
    return df.sort_values(by, ascending=ascending, inplace=inplace,
        na_position=na_position)


@infer_global(sort_values_dummy)
class SortDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, by, ascending, inplace, na_position = args
        index = df.index
        if isinstance(index, bodo.hiframes.pd_index_ext.RangeIndexType):
            index = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64)
        dcjv__fehf = df.copy(index=index)
        return signature(dcjv__fehf, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    vcqhu__kybv = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return vcqhu__kybv._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    klqfa__zcqgc = dict(index=index, name=name)
    wzni__vcdvt = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', klqfa__zcqgc,
        wzni__vcdvt, package_name='pandas', module_name='DataFrame')

    def _impl(df, index=True, name='Pandas'):
        return bodo.hiframes.pd_dataframe_ext.itertuples_dummy(df)
    return _impl


def itertuples_dummy(df):
    return df


@infer_global(itertuples_dummy)
class ItertuplesDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        df, = args
        assert 'Index' not in df.columns
        columns = ('Index',) + df.columns
        atqat__pfshy = (types.Array(types.int64, 1, 'C'),) + df.data
        wauum__xevn = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, atqat__pfshy)
        return signature(wauum__xevn, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    vcqhu__kybv = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return vcqhu__kybv._getvalue()


def query_dummy(df, expr):
    return df.eval(expr)


@infer_global(query_dummy)
class QueryDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=RangeIndexType(types
            .none)), *args)


@lower_builtin(query_dummy, types.VarArg(types.Any))
def lower_query_dummy(context, builder, sig, args):
    vcqhu__kybv = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return vcqhu__kybv._getvalue()


def val_isin_dummy(S, vals):
    return S in vals


def val_notin_dummy(S, vals):
    return S not in vals


@infer_global(val_isin_dummy)
@infer_global(val_notin_dummy)
class ValIsinTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(SeriesType(types.bool_, index=args[0].index), *args)


@lower_builtin(val_isin_dummy, types.VarArg(types.Any))
@lower_builtin(val_notin_dummy, types.VarArg(types.Any))
def lower_val_isin_dummy(context, builder, sig, args):
    vcqhu__kybv = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return vcqhu__kybv._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    hzkou__sid = get_overload_const_bool(check_duplicates)
    bcr__pgyxh = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    his__ohs = len(value_names) > 1
    fmgn__ofql = None
    rqine__elsl = None
    vjsnc__gysc = None
    tel__iqmns = None
    pxiu__xum = isinstance(values_tup, types.UniTuple)
    if pxiu__xum:
        owcm__wtaqz = [to_str_arr_if_dict_array(to_nullable_type(values_tup
            .dtype))]
    else:
        owcm__wtaqz = [to_str_arr_if_dict_array(to_nullable_type(badpq__zpe
            )) for badpq__zpe in values_tup]
    pkq__lyakr = 'def impl(\n'
    pkq__lyakr += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, _constant_pivot_values=None, parallel=False
"""
    pkq__lyakr += '):\n'
    pkq__lyakr += '    if parallel:\n'
    edtl__hdtk = ', '.join([f'array_to_info(index_tup[{i}])' for i in range
        (len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    pkq__lyakr += f'        info_list = [{edtl__hdtk}]\n'
    pkq__lyakr += '        cpp_table = arr_info_list_to_table(info_list)\n'
    pkq__lyakr += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
    ghjf__fmzun = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    bsnza__dedkw = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    kbxer__gni = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    pkq__lyakr += f'        index_tup = ({ghjf__fmzun},)\n'
    pkq__lyakr += f'        columns_tup = ({bsnza__dedkw},)\n'
    pkq__lyakr += f'        values_tup = ({kbxer__gni},)\n'
    pkq__lyakr += '        delete_table(cpp_table)\n'
    pkq__lyakr += '        delete_table(out_cpp_table)\n'
    pkq__lyakr += '    columns_arr = columns_tup[0]\n'
    if pxiu__xum:
        pkq__lyakr += '    values_arrs = [arr for arr in values_tup]\n'
    hooz__vzr = ', '.join([
        f'bodo.utils.typing.decode_if_dict_array(index_tup[{i}])' for i in
        range(len(index_tup))])
    pkq__lyakr += f'    new_index_tup = ({hooz__vzr},)\n'
    pkq__lyakr += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    pkq__lyakr += '        new_index_tup\n'
    pkq__lyakr += '    )\n'
    pkq__lyakr += '    n_rows = len(unique_index_arr_tup[0])\n'
    pkq__lyakr += '    num_values_arrays = len(values_tup)\n'
    pkq__lyakr += '    n_unique_pivots = len(pivot_values)\n'
    if pxiu__xum:
        pkq__lyakr += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        pkq__lyakr += '    n_cols = n_unique_pivots\n'
    pkq__lyakr += '    col_map = {}\n'
    pkq__lyakr += '    for i in range(n_unique_pivots):\n'
    pkq__lyakr += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    pkq__lyakr += '            raise ValueError(\n'
    pkq__lyakr += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    pkq__lyakr += '            )\n'
    pkq__lyakr += '        col_map[pivot_values[i]] = i\n'
    neyqt__rgw = False
    for i, hmyzo__uzjf in enumerate(owcm__wtaqz):
        if is_str_arr_type(hmyzo__uzjf):
            neyqt__rgw = True
            pkq__lyakr += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            pkq__lyakr += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if neyqt__rgw:
        if hzkou__sid:
            pkq__lyakr += '    nbytes = (n_rows + 7) >> 3\n'
            pkq__lyakr += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        pkq__lyakr += '    for i in range(len(columns_arr)):\n'
        pkq__lyakr += '        col_name = columns_arr[i]\n'
        pkq__lyakr += '        pivot_idx = col_map[col_name]\n'
        pkq__lyakr += '        row_idx = row_vector[i]\n'
        if hzkou__sid:
            pkq__lyakr += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            pkq__lyakr += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            pkq__lyakr += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            pkq__lyakr += '        else:\n'
            pkq__lyakr += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if pxiu__xum:
            pkq__lyakr += '        for j in range(num_values_arrays):\n'
            pkq__lyakr += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            pkq__lyakr += '            len_arr = len_arrs_0[col_idx]\n'
            pkq__lyakr += '            values_arr = values_arrs[j]\n'
            pkq__lyakr += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            pkq__lyakr += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            pkq__lyakr += '                len_arr[row_idx] = str_val_len\n'
            pkq__lyakr += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, hmyzo__uzjf in enumerate(owcm__wtaqz):
                if is_str_arr_type(hmyzo__uzjf):
                    pkq__lyakr += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    pkq__lyakr += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    pkq__lyakr += f"""            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}
"""
                    pkq__lyakr += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    for i, hmyzo__uzjf in enumerate(owcm__wtaqz):
        if is_str_arr_type(hmyzo__uzjf):
            pkq__lyakr += f'    data_arrs_{i} = [\n'
            pkq__lyakr += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            pkq__lyakr += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            pkq__lyakr += '        )\n'
            pkq__lyakr += '        for i in range(n_cols)\n'
            pkq__lyakr += '    ]\n'
        else:
            pkq__lyakr += f'    data_arrs_{i} = [\n'
            pkq__lyakr += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            pkq__lyakr += '        for _ in range(n_cols)\n'
            pkq__lyakr += '    ]\n'
    if not neyqt__rgw and hzkou__sid:
        pkq__lyakr += '    nbytes = (n_rows + 7) >> 3\n'
        pkq__lyakr += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    pkq__lyakr += '    for i in range(len(columns_arr)):\n'
    pkq__lyakr += '        col_name = columns_arr[i]\n'
    pkq__lyakr += '        pivot_idx = col_map[col_name]\n'
    pkq__lyakr += '        row_idx = row_vector[i]\n'
    if not neyqt__rgw and hzkou__sid:
        pkq__lyakr += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        pkq__lyakr += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        pkq__lyakr += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        pkq__lyakr += '        else:\n'
        pkq__lyakr += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if pxiu__xum:
        pkq__lyakr += '        for j in range(num_values_arrays):\n'
        pkq__lyakr += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        pkq__lyakr += '            col_arr = data_arrs_0[col_idx]\n'
        pkq__lyakr += '            values_arr = values_arrs[j]\n'
        pkq__lyakr += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        pkq__lyakr += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        pkq__lyakr += '            else:\n'
        pkq__lyakr += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, hmyzo__uzjf in enumerate(owcm__wtaqz):
            pkq__lyakr += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            pkq__lyakr += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            pkq__lyakr += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            pkq__lyakr += f'        else:\n'
            pkq__lyakr += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        pkq__lyakr += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        fmgn__ofql = index_names.meta[0]
    else:
        pkq__lyakr += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        fmgn__ofql = tuple(index_names.meta)
    if not bcr__pgyxh:
        vjsnc__gysc = columns_name.meta[0]
        if his__ohs:
            pkq__lyakr += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            rqine__elsl = value_names.meta
            if all(isinstance(iqdm__ahiu, str) for iqdm__ahiu in rqine__elsl):
                rqine__elsl = pd.array(rqine__elsl, 'string')
            elif all(isinstance(iqdm__ahiu, int) for iqdm__ahiu in rqine__elsl
                ):
                rqine__elsl = np.array(rqine__elsl, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(rqine__elsl.dtype, pd.StringDtype):
                pkq__lyakr += '    total_chars = 0\n'
                pkq__lyakr += f'    for i in range({len(value_names)}):\n'
                pkq__lyakr += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                pkq__lyakr += '        total_chars += value_name_str_len\n'
                pkq__lyakr += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                pkq__lyakr += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                pkq__lyakr += '    total_chars = 0\n'
                pkq__lyakr += '    for i in range(len(pivot_values)):\n'
                pkq__lyakr += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                pkq__lyakr += '        total_chars += pivot_val_str_len\n'
                pkq__lyakr += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                pkq__lyakr += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            pkq__lyakr += f'    for i in range({len(value_names)}):\n'
            pkq__lyakr += '        for j in range(len(pivot_values)):\n'
            pkq__lyakr += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            pkq__lyakr += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            pkq__lyakr += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            pkq__lyakr += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    blp__cwr = None
    if bcr__pgyxh:
        if his__ohs:
            lfyag__jqdc = []
            for pus__kyk in _constant_pivot_values.meta:
                for qykq__whzeb in value_names.meta:
                    lfyag__jqdc.append((pus__kyk, qykq__whzeb))
            column_names = tuple(lfyag__jqdc)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        tel__iqmns = ColNamesMetaType(column_names)
        xpbaf__ivwfx = []
        for badpq__zpe in owcm__wtaqz:
            xpbaf__ivwfx.extend([badpq__zpe] * len(_constant_pivot_values))
        mjdd__zzgf = tuple(xpbaf__ivwfx)
        blp__cwr = TableType(mjdd__zzgf)
        pkq__lyakr += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        pkq__lyakr += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, badpq__zpe in enumerate(owcm__wtaqz):
            pkq__lyakr += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {blp__cwr.type_to_blk[badpq__zpe]})
"""
        pkq__lyakr += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        pkq__lyakr += '        (table,), index, columns_typ\n'
        pkq__lyakr += '    )\n'
    else:
        yhl__djjn = ', '.join(f'data_arrs_{i}' for i in range(len(owcm__wtaqz))
            )
        pkq__lyakr += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({yhl__djjn},), n_rows)
"""
        pkq__lyakr += (
            '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        pkq__lyakr += '        (table,), index, column_index\n'
        pkq__lyakr += '    )\n'
    rqkt__fdngz = {}
    tjl__lrsp = {f'data_arr_typ_{i}': hmyzo__uzjf for i, hmyzo__uzjf in
        enumerate(owcm__wtaqz)}
    gsczm__vlbz = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        blp__cwr, 'columns_typ': tel__iqmns, 'index_names_lit': fmgn__ofql,
        'value_names_lit': rqine__elsl, 'columns_name_lit': vjsnc__gysc, **
        tjl__lrsp}
    exec(pkq__lyakr, gsczm__vlbz, rqkt__fdngz)
    impl = rqkt__fdngz['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    ewnfm__anh = {}
    ewnfm__anh['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, whoc__lrrc in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        cqalt__aawv = None
        if isinstance(whoc__lrrc, bodo.DatetimeArrayType):
            oxmr__xana = 'datetimetz'
            igeyp__uhn = 'datetime64[ns]'
            if isinstance(whoc__lrrc.tz, int):
                qek__cnh = bodo.libs.pd_datetime_arr_ext.nanoseconds_to_offset(
                    whoc__lrrc.tz)
            else:
                qek__cnh = pd.DatetimeTZDtype(tz=whoc__lrrc.tz).tz
            cqalt__aawv = {'timezone': pa.lib.tzinfo_to_string(qek__cnh)}
        elif isinstance(whoc__lrrc, types.Array
            ) or whoc__lrrc == boolean_array:
            oxmr__xana = igeyp__uhn = whoc__lrrc.dtype.name
            if igeyp__uhn.startswith('datetime'):
                oxmr__xana = 'datetime'
        elif is_str_arr_type(whoc__lrrc):
            oxmr__xana = 'unicode'
            igeyp__uhn = 'object'
        elif whoc__lrrc == binary_array_type:
            oxmr__xana = 'bytes'
            igeyp__uhn = 'object'
        elif isinstance(whoc__lrrc, DecimalArrayType):
            oxmr__xana = igeyp__uhn = 'object'
        elif isinstance(whoc__lrrc, IntegerArrayType):
            fwgd__eavfl = whoc__lrrc.dtype.name
            if fwgd__eavfl.startswith('int'):
                oxmr__xana = 'Int' + fwgd__eavfl[3:]
            elif fwgd__eavfl.startswith('uint'):
                oxmr__xana = 'UInt' + fwgd__eavfl[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, whoc__lrrc))
            igeyp__uhn = whoc__lrrc.dtype.name
        elif whoc__lrrc == datetime_date_array_type:
            oxmr__xana = 'datetime'
            igeyp__uhn = 'object'
        elif isinstance(whoc__lrrc, (StructArrayType, ArrayItemArrayType)):
            oxmr__xana = 'object'
            igeyp__uhn = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, whoc__lrrc))
        lzkk__wuxjc = {'name': col_name, 'field_name': col_name,
            'pandas_type': oxmr__xana, 'numpy_type': igeyp__uhn, 'metadata':
            cqalt__aawv}
        ewnfm__anh['columns'].append(lzkk__wuxjc)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            cqe__ntmk = '__index_level_0__'
            fijud__mrjj = None
        else:
            cqe__ntmk = '%s'
            fijud__mrjj = '%s'
        ewnfm__anh['index_columns'] = [cqe__ntmk]
        ewnfm__anh['columns'].append({'name': fijud__mrjj, 'field_name':
            cqe__ntmk, 'pandas_type': index.pandas_type_name, 'numpy_type':
            index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        ewnfm__anh['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        ewnfm__anh['index_columns'] = []
    ewnfm__anh['pandas_version'] = pd.__version__
    return ewnfm__anh


@overload_method(DataFrameType, 'to_parquet', no_unliteral=True)
def to_parquet_overload(df, path, engine='auto', compression='snappy',
    index=None, partition_cols=None, storage_options=None, row_group_size=-
    1, _bodo_file_prefix='part-', _is_parallel=False):
    check_unsupported_args('DataFrame.to_parquet', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if df.has_runtime_cols and not is_overload_none(partition_cols):
        raise BodoError(
            f"DataFrame.to_parquet(): Providing 'partition_cols' on DataFrames with columns determined at runtime is not yet supported. Please return the DataFrame to regular Python to update typing information."
            )
    if not is_overload_none(engine) and get_overload_const_str(engine) not in (
        'auto', 'pyarrow'):
        raise BodoError('DataFrame.to_parquet(): only pyarrow engine supported'
            )
    if not is_overload_none(compression) and get_overload_const_str(compression
        ) not in {'snappy', 'gzip', 'brotli'}:
        raise BodoError('to_parquet(): Unsupported compression: ' + str(
            get_overload_const_str(compression)))
    if not is_overload_none(partition_cols):
        partition_cols = get_overload_const_list(partition_cols)
        smysc__rma = []
        for mcxb__gskne in partition_cols:
            try:
                idx = df.columns.index(mcxb__gskne)
            except ValueError as epvg__yfno:
                raise BodoError(
                    f'Partition column {mcxb__gskne} is not in dataframe')
            smysc__rma.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    didj__egen = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType
        )
    todt__iudyj = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not didj__egen)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not didj__egen or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and didj__egen and not is_overload_true(_is_parallel)
    if df.has_runtime_cols:
        if isinstance(df.runtime_colname_typ, MultiIndexType):
            raise BodoError(
                'DataFrame.to_parquet(): Not supported with MultiIndex runtime column names. Please return the DataFrame to regular Python to update typing information.'
                )
        if not isinstance(df.runtime_colname_typ, bodo.hiframes.
            pd_index_ext.StringIndexType):
            raise BodoError(
                'DataFrame.to_parquet(): parquet must have string column names. Please return the DataFrame with runtime column names to regular Python to modify column names.'
                )
        jgkor__ecfhf = df.runtime_data_types
        gijg__kgevm = len(jgkor__ecfhf)
        cqalt__aawv = gen_pandas_parquet_metadata([''] * gijg__kgevm,
            jgkor__ecfhf, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        xfvs__ufnj = cqalt__aawv['columns'][:gijg__kgevm]
        cqalt__aawv['columns'] = cqalt__aawv['columns'][gijg__kgevm:]
        xfvs__ufnj = [json.dumps(tlv__kzmje).replace('""', '{0}') for
            tlv__kzmje in xfvs__ufnj]
        tlib__xoso = json.dumps(cqalt__aawv)
        wvo__jlk = '"columns": ['
        lxgcc__olass = tlib__xoso.find(wvo__jlk)
        if lxgcc__olass == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        zorg__cbqre = lxgcc__olass + len(wvo__jlk)
        zmpnr__nec = tlib__xoso[:zorg__cbqre]
        tlib__xoso = tlib__xoso[zorg__cbqre:]
        toie__yzsq = len(cqalt__aawv['columns'])
    else:
        tlib__xoso = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and didj__egen:
        tlib__xoso = tlib__xoso.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            tlib__xoso = tlib__xoso.replace('"%s"', '%s')
    if not df.is_table_format:
        sdco__nuyn = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    pkq__lyakr = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        pkq__lyakr += '    py_table = get_dataframe_table(df)\n'
        pkq__lyakr += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        pkq__lyakr += '    info_list = [{}]\n'.format(sdco__nuyn)
        pkq__lyakr += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        pkq__lyakr += '    columns_index = get_dataframe_column_names(df)\n'
        pkq__lyakr += '    names_arr = index_to_array(columns_index)\n'
        pkq__lyakr += '    col_names = array_to_info(names_arr)\n'
    else:
        pkq__lyakr += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and todt__iudyj:
        pkq__lyakr += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        lql__eowzb = True
    else:
        pkq__lyakr += '    index_col = array_to_info(np.empty(0))\n'
        lql__eowzb = False
    if df.has_runtime_cols:
        pkq__lyakr += '    columns_lst = []\n'
        pkq__lyakr += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            pkq__lyakr += f'    for _ in range(len(py_table.block_{i})):\n'
            pkq__lyakr += f"""        columns_lst.append({xfvs__ufnj[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            pkq__lyakr += '        num_cols += 1\n'
        if toie__yzsq:
            pkq__lyakr += "    columns_lst.append('')\n"
        pkq__lyakr += '    columns_str = ", ".join(columns_lst)\n'
        pkq__lyakr += ('    metadata = """' + zmpnr__nec +
            '""" + columns_str + """' + tlib__xoso + '"""\n')
    else:
        pkq__lyakr += '    metadata = """' + tlib__xoso + '"""\n'
    pkq__lyakr += '    if compression is None:\n'
    pkq__lyakr += "        compression = 'none'\n"
    pkq__lyakr += '    if df.index.name is not None:\n'
    pkq__lyakr += '        name_ptr = df.index.name\n'
    pkq__lyakr += '    else:\n'
    pkq__lyakr += "        name_ptr = 'null'\n"
    pkq__lyakr += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    hntn__ovxc = None
    if partition_cols:
        hntn__ovxc = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        wfoot__laqdl = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in smysc__rma)
        if wfoot__laqdl:
            pkq__lyakr += '    cat_info_list = [{}]\n'.format(wfoot__laqdl)
            pkq__lyakr += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            pkq__lyakr += '    cat_table = table\n'
        pkq__lyakr += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        pkq__lyakr += (
            f'    part_cols_idxs = np.array({smysc__rma}, dtype=np.int32)\n')
        pkq__lyakr += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        pkq__lyakr += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        pkq__lyakr += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        pkq__lyakr += (
            '                            unicode_to_utf8(compression),\n')
        pkq__lyakr += '                            _is_parallel,\n'
        pkq__lyakr += (
            '                            unicode_to_utf8(bucket_region),\n')
        pkq__lyakr += '                            row_group_size,\n'
        pkq__lyakr += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        pkq__lyakr += '    delete_table_decref_arrays(table)\n'
        pkq__lyakr += '    delete_info_decref_array(index_col)\n'
        pkq__lyakr += '    delete_info_decref_array(col_names_no_partitions)\n'
        pkq__lyakr += '    delete_info_decref_array(col_names)\n'
        if wfoot__laqdl:
            pkq__lyakr += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        pkq__lyakr += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        pkq__lyakr += (
            '                            table, col_names, index_col,\n')
        pkq__lyakr += '                            ' + str(lql__eowzb) + ',\n'
        pkq__lyakr += (
            '                            unicode_to_utf8(metadata),\n')
        pkq__lyakr += (
            '                            unicode_to_utf8(compression),\n')
        pkq__lyakr += (
            '                            _is_parallel, 1, df.index.start,\n')
        pkq__lyakr += (
            '                            df.index.stop, df.index.step,\n')
        pkq__lyakr += (
            '                            unicode_to_utf8(name_ptr),\n')
        pkq__lyakr += (
            '                            unicode_to_utf8(bucket_region),\n')
        pkq__lyakr += '                            row_group_size,\n'
        pkq__lyakr += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        pkq__lyakr += '    delete_table_decref_arrays(table)\n'
        pkq__lyakr += '    delete_info_decref_array(index_col)\n'
        pkq__lyakr += '    delete_info_decref_array(col_names)\n'
    else:
        pkq__lyakr += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        pkq__lyakr += (
            '                            table, col_names, index_col,\n')
        pkq__lyakr += '                            ' + str(lql__eowzb) + ',\n'
        pkq__lyakr += (
            '                            unicode_to_utf8(metadata),\n')
        pkq__lyakr += (
            '                            unicode_to_utf8(compression),\n')
        pkq__lyakr += '                            _is_parallel, 0, 0, 0, 0,\n'
        pkq__lyakr += (
            '                            unicode_to_utf8(name_ptr),\n')
        pkq__lyakr += (
            '                            unicode_to_utf8(bucket_region),\n')
        pkq__lyakr += '                            row_group_size,\n'
        pkq__lyakr += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        pkq__lyakr += '    delete_table_decref_arrays(table)\n'
        pkq__lyakr += '    delete_info_decref_array(index_col)\n'
        pkq__lyakr += '    delete_info_decref_array(col_names)\n'
    rqkt__fdngz = {}
    if df.has_runtime_cols:
        ychk__ppdv = None
    else:
        for ghobr__plpd in df.columns:
            if not isinstance(ghobr__plpd, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        ychk__ppdv = pd.array(df.columns)
    exec(pkq__lyakr, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': ychk__ppdv,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': hntn__ovxc, 'get_dataframe_column_names':
        get_dataframe_column_names, 'fix_arr_dtype': fix_arr_dtype,
        'decode_if_dict_array': decode_if_dict_array,
        'decode_if_dict_table': decode_if_dict_table}, rqkt__fdngz)
    ilni__eeq = rqkt__fdngz['df_to_parquet']
    return ilni__eeq


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    vrapf__rigte = 'all_ok'
    zcyfp__uqka, awpi__sat = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        jjfed__yyzac = 100
        if chunksize is None:
            lfi__ugipn = jjfed__yyzac
        else:
            lfi__ugipn = min(chunksize, jjfed__yyzac)
        if _is_table_create:
            df = df.iloc[:lfi__ugipn, :]
        else:
            df = df.iloc[lfi__ugipn:, :]
            if len(df) == 0:
                return vrapf__rigte
    dak__cil = df.columns
    try:
        if zcyfp__uqka == 'snowflake':
            if awpi__sat and con.count(awpi__sat) == 1:
                con = con.replace(awpi__sat, quote(awpi__sat))
            try:
                from snowflake.connector.pandas_tools import pd_writer
                from bodo import snowflake_sqlalchemy_compat
                if method is not None and _is_table_create and bodo.get_rank(
                    ) == 0:
                    import warnings
                    from bodo.utils.typing import BodoWarning
                    warnings.warn(BodoWarning(
                        'DataFrame.to_sql(): method argument is not supported with Snowflake. Bodo always uses snowflake.connector.pandas_tools.pd_writer to write data.'
                        ))
                method = pd_writer
                df.columns = [(iqdm__ahiu.upper() if iqdm__ahiu.islower() else
                    iqdm__ahiu) for iqdm__ahiu in df.columns]
            except ImportError as epvg__yfno:
                vrapf__rigte = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return vrapf__rigte
        if zcyfp__uqka == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            uoxo__tzmq = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            nogf__jeu = bodo.typeof(df)
            wzvx__cclof = {}
            for iqdm__ahiu, yxpjk__dslnl in zip(nogf__jeu.columns,
                nogf__jeu.data):
                if df[iqdm__ahiu].dtype == 'object':
                    if yxpjk__dslnl == datetime_date_array_type:
                        wzvx__cclof[iqdm__ahiu] = sa.types.Date
                    elif yxpjk__dslnl in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not uoxo__tzmq or 
                        uoxo__tzmq == '0'):
                        wzvx__cclof[iqdm__ahiu] = VARCHAR2(4000)
            dtype = wzvx__cclof
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as ccy__jdivc:
            vrapf__rigte = ccy__jdivc.args[0]
            if zcyfp__uqka == 'oracle' and 'ORA-12899' in vrapf__rigte:
                vrapf__rigte += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return vrapf__rigte
    finally:
        df.columns = dak__cil


@numba.njit
def to_sql_exception_guard_encaps(df, name, con, schema=None, if_exists=
    'fail', index=True, index_label=None, chunksize=None, dtype=None,
    method=None, _is_table_create=False, _is_parallel=False):
    with numba.objmode(out='unicode_type'):
        out = to_sql_exception_guard(df, name, con, schema, if_exists,
            index, index_label, chunksize, dtype, method, _is_table_create,
            _is_parallel)
    return out


@overload_method(DataFrameType, 'to_sql')
def to_sql_overload(df, name, con, schema=None, if_exists='fail', index=
    True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_parallel=False):
    import warnings
    check_runtime_cols_unsupported(df, 'DataFrame.to_sql()')
    df: DataFrameType = df
    if is_overload_none(schema):
        if bodo.get_rank() == 0:
            import warnings
            warnings.warn(BodoWarning(
                f'DataFrame.to_sql(): schema argument is recommended to avoid permission issues when writing the table.'
                ))
    if not (is_overload_none(chunksize) or isinstance(chunksize, types.Integer)
        ):
        raise BodoError(
            "DataFrame.to_sql(): 'chunksize' argument must be an integer if provided."
            )
    pkq__lyakr = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    pkq__lyakr += f"    if con.startswith('iceberg'):\n"
    pkq__lyakr += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    pkq__lyakr += f'        if schema is None:\n'
    pkq__lyakr += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    pkq__lyakr += f'        if chunksize is not None:\n'
    pkq__lyakr += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    pkq__lyakr += f'        if index and bodo.get_rank() == 0:\n'
    pkq__lyakr += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    pkq__lyakr += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    pkq__lyakr += (
        f"            warnings.warn('index_label is not supported for Iceberg tables.')\n"
        )
    if df.is_table_format:
        pkq__lyakr += f'        py_table = get_dataframe_table(df)\n'
        pkq__lyakr += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        sdco__nuyn = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        pkq__lyakr += f'        info_list = [{sdco__nuyn}]\n'
        pkq__lyakr += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        pkq__lyakr += (
            f'        columns_index = get_dataframe_column_names(df)\n')
        pkq__lyakr += f'        names_arr = index_to_array(columns_index)\n'
        pkq__lyakr += f'        col_names = array_to_info(names_arr)\n'
    else:
        pkq__lyakr += f'        col_names = array_to_info(col_names_arr)\n'
    pkq__lyakr += """        bodo.io.iceberg.iceberg_write(
            name,
            con_str,
            schema,
            table,
            col_names,
            if_exists,
            _is_parallel,
            pyarrow_table_schema,
        )
"""
    pkq__lyakr += f'        delete_table_decref_arrays(table)\n'
    pkq__lyakr += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        ychk__ppdv = None
    else:
        for ghobr__plpd in df.columns:
            if not isinstance(ghobr__plpd, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        ychk__ppdv = pd.array(df.columns)
    pkq__lyakr += f'    else:\n'
    pkq__lyakr += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    pkq__lyakr += f"        err_msg = 'unset'\n"
    pkq__lyakr += f'        if rank != 0:\n'
    pkq__lyakr += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    pkq__lyakr += f'        elif rank == 0:\n'
    pkq__lyakr += f'            err_msg = to_sql_exception_guard_encaps(\n'
    pkq__lyakr += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    pkq__lyakr += f'                          chunksize, dtype, method,\n'
    pkq__lyakr += f'                          True, _is_parallel,\n'
    pkq__lyakr += f'                      )\n'
    pkq__lyakr += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    pkq__lyakr += f"        if_exists = 'append'\n"
    pkq__lyakr += f"        if _is_parallel and err_msg == 'all_ok':\n"
    pkq__lyakr += f'            err_msg = to_sql_exception_guard_encaps(\n'
    pkq__lyakr += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    pkq__lyakr += f'                          chunksize, dtype, method,\n'
    pkq__lyakr += f'                          False, _is_parallel,\n'
    pkq__lyakr += f'                      )\n'
    pkq__lyakr += f"        if err_msg != 'all_ok':\n"
    pkq__lyakr += f"            print('err_msg=', err_msg)\n"
    pkq__lyakr += (
        f"            raise ValueError('error in to_sql() operation')\n")
    rqkt__fdngz = {}
    exec(pkq__lyakr, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_typ': df.
        table_type, 'col_names_arr': ychk__ppdv,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'delete_info_decref_array': delete_info_decref_array,
        'arr_info_list_to_table': arr_info_list_to_table, 'index_to_array':
        index_to_array, 'pyarrow_table_schema': bodo.io.iceberg.
        pyarrow_schema(df), 'to_sql_exception_guard_encaps':
        to_sql_exception_guard_encaps, 'warnings': warnings}, rqkt__fdngz)
    _impl = rqkt__fdngz['df_to_sql']
    return _impl


@overload_method(DataFrameType, 'to_csv', no_unliteral=True)
def to_csv_overload(df, path_or_buf=None, sep=',', na_rep='', float_format=
    None, columns=None, header=True, index=True, index_label=None, mode='w',
    encoding=None, compression=None, quoting=None, quotechar='"',
    line_terminator=None, chunksize=None, date_format=None, doublequote=
    True, escapechar=None, decimal='.', errors='strict', storage_options=
    None, _bodo_file_prefix='part-'):
    check_runtime_cols_unsupported(df, 'DataFrame.to_csv()')
    check_unsupported_args('DataFrame.to_csv', {'encoding': encoding,
        'mode': mode, 'errors': errors, 'storage_options': storage_options},
        {'encoding': None, 'mode': 'w', 'errors': 'strict',
        'storage_options': None}, package_name='pandas', module_name='IO')
    if not (is_overload_none(path_or_buf) or is_overload_constant_str(
        path_or_buf) or path_or_buf == string_type):
        raise BodoError(
            "DataFrame.to_csv(): 'path_or_buf' argument should be None or string"
            )
    if not is_overload_none(compression):
        raise BodoError(
            "DataFrame.to_csv(): 'compression' argument supports only None, which is the default in JIT code."
            )
    if is_overload_constant_str(path_or_buf):
        zhwkm__bdma = get_overload_const_str(path_or_buf)
        if zhwkm__bdma.endswith(('.gz', '.bz2', '.zip', '.xz')):
            import warnings
            from bodo.utils.typing import BodoWarning
            warnings.warn(BodoWarning(
                "DataFrame.to_csv(): 'compression' argument defaults to None in JIT code, which is the only supported value."
                ))
    if not (is_overload_none(columns) or isinstance(columns, (types.List,
        types.Tuple))):
        raise BodoError(
            "DataFrame.to_csv(): 'columns' argument must be list a or tuple type."
            )
    if is_overload_none(path_or_buf):

        def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=
            None, columns=None, header=True, index=True, index_label=None,
            mode='w', encoding=None, compression=None, quoting=None,
            quotechar='"', line_terminator=None, chunksize=None,
            date_format=None, doublequote=True, escapechar=None, decimal=
            '.', errors='strict', storage_options=None, _bodo_file_prefix=
            'part-'):
            with numba.objmode(D='unicode_type'):
                D = df.to_csv(path_or_buf, sep, na_rep, float_format,
                    columns, header, index, index_label, mode, encoding,
                    compression, quoting, quotechar, line_terminator,
                    chunksize, date_format, doublequote, escapechar,
                    decimal, errors, storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, sep=',', na_rep='', float_format=None,
        columns=None, header=True, index=True, index_label=None, mode='w',
        encoding=None, compression=None, quoting=None, quotechar='"',
        line_terminator=None, chunksize=None, date_format=None, doublequote
        =True, escapechar=None, decimal='.', errors='strict',
        storage_options=None, _bodo_file_prefix='part-'):
        with numba.objmode(D='unicode_type'):
            D = df.to_csv(None, sep, na_rep, float_format, columns, header,
                index, index_label, mode, encoding, compression, quoting,
                quotechar, line_terminator, chunksize, date_format,
                doublequote, escapechar, decimal, errors, storage_options)
        bodo.io.fs_io.csv_write(path_or_buf, D, _bodo_file_prefix)
    return _impl


@overload_method(DataFrameType, 'to_json', no_unliteral=True)
def to_json_overload(df, path_or_buf=None, orient='records', date_format=
    None, double_precision=10, force_ascii=True, date_unit='ms',
    default_handler=None, lines=True, compression='infer', index=True,
    indent=None, storage_options=None, _bodo_file_prefix='part-'):
    check_runtime_cols_unsupported(df, 'DataFrame.to_json()')
    check_unsupported_args('DataFrame.to_json', {'storage_options':
        storage_options}, {'storage_options': None}, package_name='pandas',
        module_name='IO')
    if path_or_buf is None or path_or_buf == types.none:

        def _impl(df, path_or_buf=None, orient='records', date_format=None,
            double_precision=10, force_ascii=True, date_unit='ms',
            default_handler=None, lines=True, compression='infer', index=
            True, indent=None, storage_options=None, _bodo_file_prefix='part-'
            ):
            with numba.objmode(D='unicode_type'):
                D = df.to_json(path_or_buf, orient, date_format,
                    double_precision, force_ascii, date_unit,
                    default_handler, lines, compression, index, indent,
                    storage_options)
            return D
        return _impl

    def _impl(df, path_or_buf=None, orient='records', date_format=None,
        double_precision=10, force_ascii=True, date_unit='ms',
        default_handler=None, lines=True, compression='infer', index=True,
        indent=None, storage_options=None, _bodo_file_prefix='part-'):
        with numba.objmode(D='unicode_type'):
            D = df.to_json(None, orient, date_format, double_precision,
                force_ascii, date_unit, default_handler, lines, compression,
                index, indent, storage_options)
        rprd__qscs = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(rprd__qscs), unicode_to_utf8(_bodo_file_prefix)
                )
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(rprd__qscs), unicode_to_utf8(_bodo_file_prefix)
                )
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    thj__gpxa = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    cgw__fwv = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', thj__gpxa, cgw__fwv,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    pkq__lyakr = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        lyk__jdb = data.data.dtype.categories
        pkq__lyakr += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        lyk__jdb = data.dtype.categories
        pkq__lyakr += '  data_values = data\n'
    kyjs__icnkd = len(lyk__jdb)
    pkq__lyakr += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    pkq__lyakr += '  numba.parfors.parfor.init_prange()\n'
    pkq__lyakr += '  n = len(data_values)\n'
    for i in range(kyjs__icnkd):
        pkq__lyakr += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    pkq__lyakr += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    pkq__lyakr += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for bttl__wqzg in range(kyjs__icnkd):
        pkq__lyakr += '          data_arr_{}[i] = 0\n'.format(bttl__wqzg)
    pkq__lyakr += '      else:\n'
    for qpk__wwid in range(kyjs__icnkd):
        pkq__lyakr += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            qpk__wwid)
    sdco__nuyn = ', '.join(f'data_arr_{i}' for i in range(kyjs__icnkd))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(lyk__jdb[0], np.datetime64):
        lyk__jdb = tuple(pd.Timestamp(iqdm__ahiu) for iqdm__ahiu in lyk__jdb)
    elif isinstance(lyk__jdb[0], np.timedelta64):
        lyk__jdb = tuple(pd.Timedelta(iqdm__ahiu) for iqdm__ahiu in lyk__jdb)
    return bodo.hiframes.dataframe_impl._gen_init_df(pkq__lyakr, lyk__jdb,
        sdco__nuyn, index)


def categorical_can_construct_dataframe(val):
    if isinstance(val, CategoricalArrayType):
        return val.dtype.categories is not None
    elif isinstance(val, SeriesType) and isinstance(val.data,
        CategoricalArrayType):
        return val.data.dtype.categories is not None
    return False


def handle_inplace_df_type_change(inplace, _bodo_transformed, func_name):
    if is_overload_false(_bodo_transformed
        ) and bodo.transforms.typing_pass.in_partial_typing and (
        is_overload_true(inplace) or not is_overload_constant_bool(inplace)):
        bodo.transforms.typing_pass.typing_transform_required = True
        raise Exception('DataFrame.{}(): transform necessary for inplace'.
            format(func_name))


pd_unsupported = (pd.read_pickle, pd.read_table, pd.read_fwf, pd.
    read_clipboard, pd.ExcelFile, pd.read_html, pd.read_xml, pd.read_hdf,
    pd.read_feather, pd.read_orc, pd.read_sas, pd.read_spss, pd.
    read_sql_query, pd.read_gbq, pd.read_stata, pd.ExcelWriter, pd.
    json_normalize, pd.merge_ordered, pd.factorize, pd.wide_to_long, pd.
    bdate_range, pd.period_range, pd.infer_freq, pd.interval_range, pd.eval,
    pd.test, pd.Grouper)
pd_util_unsupported = pd.util.hash_array, pd.util.hash_pandas_object
dataframe_unsupported = ['set_flags', 'convert_dtypes', 'bool', '__iter__',
    'items', 'iteritems', 'keys', 'iterrows', 'lookup', 'pop', 'xs', 'get',
    'add', 'sub', 'mul', 'div', 'truediv', 'floordiv', 'mod', 'pow', 'dot',
    'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow',
    'lt', 'gt', 'le', 'ge', 'ne', 'eq', 'combine', 'combine_first',
    'subtract', 'divide', 'multiply', 'applymap', 'agg', 'aggregate',
    'transform', 'expanding', 'ewm', 'all', 'any', 'clip', 'corrwith',
    'cummax', 'cummin', 'eval', 'kurt', 'kurtosis', 'mad', 'mode', 'round',
    'sem', 'skew', 'value_counts', 'add_prefix', 'add_suffix', 'align',
    'at_time', 'between_time', 'equals', 'reindex', 'reindex_like',
    'rename_axis', 'set_axis', 'truncate', 'backfill', 'bfill', 'ffill',
    'interpolate', 'pad', 'droplevel', 'reorder_levels', 'nlargest',
    'nsmallest', 'swaplevel', 'stack', 'unstack', 'swapaxes', 'squeeze',
    'to_xarray', 'T', 'transpose', 'compare', 'update', 'asfreq', 'asof',
    'slice_shift', 'tshift', 'first_valid_index', 'last_valid_index',
    'resample', 'to_period', 'to_timestamp', 'tz_convert', 'tz_localize',
    'boxplot', 'hist', 'from_dict', 'from_records', 'to_pickle', 'to_hdf',
    'to_dict', 'to_excel', 'to_html', 'to_feather', 'to_latex', 'to_stata',
    'to_gbq', 'to_records', 'to_clipboard', 'to_markdown', 'to_xml']
dataframe_unsupported_attrs = ['at', 'attrs', 'axes', 'flags', 'style',
    'sparse']


def _install_pd_unsupported(mod_name, pd_unsupported):
    for uhls__blxf in pd_unsupported:
        afbo__nii = mod_name + '.' + uhls__blxf.__name__
        overload(uhls__blxf, no_unliteral=True)(create_unsupported_overload
            (afbo__nii))


def _install_dataframe_unsupported():
    for fens__brkqe in dataframe_unsupported_attrs:
        zzzn__lqx = 'DataFrame.' + fens__brkqe
        overload_attribute(DataFrameType, fens__brkqe)(
            create_unsupported_overload(zzzn__lqx))
    for afbo__nii in dataframe_unsupported:
        zzzn__lqx = 'DataFrame.' + afbo__nii + '()'
        overload_method(DataFrameType, afbo__nii)(create_unsupported_overload
            (zzzn__lqx))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
