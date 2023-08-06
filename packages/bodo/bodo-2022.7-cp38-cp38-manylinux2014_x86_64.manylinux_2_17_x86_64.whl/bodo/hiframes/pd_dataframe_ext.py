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
            sbo__gahdw = f'{len(self.data)} columns of types {set(self.data)}'
            ybi__dyg = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({sbo__gahdw}, {self.index}, {ybi__dyg}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
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
        return {xwip__dvn: i for i, xwip__dvn in enumerate(self.columns)}

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
            ycldr__koomb = (self.index if self.index == other.index else
                self.index.unify(typingctx, other.index))
            data = tuple(qrdat__mnkc.unify(typingctx, wgq__zbtw) if 
                qrdat__mnkc != wgq__zbtw else qrdat__mnkc for qrdat__mnkc,
                wgq__zbtw in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if ycldr__koomb is not None and None not in data:
                return DataFrameType(data, ycldr__koomb, self.columns, dist,
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
        return all(qrdat__mnkc.is_precise() for qrdat__mnkc in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        yejuh__wyopa = self.columns.index(col_name)
        wxeaw__zveci = tuple(list(self.data[:yejuh__wyopa]) + [new_type] +
            list(self.data[yejuh__wyopa + 1:]))
        return DataFrameType(wxeaw__zveci, self.index, self.columns, self.
            dist, self.is_table_format)


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
        wpl__yelo = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            wpl__yelo.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, wpl__yelo)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        wpl__yelo = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, wpl__yelo)


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
        rupli__dso = 'n',
        hxr__vixv = {'n': 5}
        ngr__peugo, qkkf__pee = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, rupli__dso, hxr__vixv)
        tarum__gzy = qkkf__pee[0]
        if not is_overload_int(tarum__gzy):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        fyir__oshab = df.copy()
        return fyir__oshab(*qkkf__pee).replace(pysig=ngr__peugo)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        ldumz__ggytz = (df,) + args
        rupli__dso = 'df', 'method', 'min_periods'
        hxr__vixv = {'method': 'pearson', 'min_periods': 1}
        qfin__lwt = 'method',
        ngr__peugo, qkkf__pee = bodo.utils.typing.fold_typing_args(func_name,
            ldumz__ggytz, kws, rupli__dso, hxr__vixv, qfin__lwt)
        qhdq__ytop = qkkf__pee[2]
        if not is_overload_int(qhdq__ytop):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        bvbc__qcq = []
        sktvv__shb = []
        for xwip__dvn, ziymi__jnhxo in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(ziymi__jnhxo.dtype):
                bvbc__qcq.append(xwip__dvn)
                sktvv__shb.append(types.Array(types.float64, 1, 'A'))
        if len(bvbc__qcq) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        sktvv__shb = tuple(sktvv__shb)
        bvbc__qcq = tuple(bvbc__qcq)
        index_typ = bodo.utils.typing.type_col_to_index(bvbc__qcq)
        fyir__oshab = DataFrameType(sktvv__shb, index_typ, bvbc__qcq)
        return fyir__oshab(*qkkf__pee).replace(pysig=ngr__peugo)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        kjwj__ybt = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        quuqr__olnfh = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        agerc__iuhg = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        vpo__ndp = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        muw__pcjka = dict(raw=quuqr__olnfh, result_type=agerc__iuhg)
        mfgjv__dohiu = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', muw__pcjka, mfgjv__dohiu,
            package_name='pandas', module_name='DataFrame')
        arj__cbln = True
        if types.unliteral(kjwj__ybt) == types.unicode_type:
            if not is_overload_constant_str(kjwj__ybt):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            arj__cbln = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        pkel__ugqp = get_overload_const_int(axis)
        if arj__cbln and pkel__ugqp != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif pkel__ugqp not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        xegd__pdyxb = []
        for arr_typ in df.data:
            mmy__ruh = SeriesType(arr_typ.dtype, arr_typ, df.index, string_type
                )
            fjfjk__xhzmc = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(mmy__ruh), types.int64), {}
                ).return_type
            xegd__pdyxb.append(fjfjk__xhzmc)
        rier__twqns = types.none
        xgnj__vffqm = HeterogeneousIndexType(types.BaseTuple.from_types(
            tuple(types.literal(xwip__dvn) for xwip__dvn in df.columns)), None)
        zeqt__hac = types.BaseTuple.from_types(xegd__pdyxb)
        munxp__aknar = types.Tuple([types.bool_] * len(zeqt__hac))
        yhzqy__nglir = bodo.NullableTupleType(zeqt__hac, munxp__aknar)
        kdy__haztj = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if kdy__haztj == types.NPDatetime('ns'):
            kdy__haztj = bodo.pd_timestamp_type
        if kdy__haztj == types.NPTimedelta('ns'):
            kdy__haztj = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(zeqt__hac):
            cwf__jjlk = HeterogeneousSeriesType(yhzqy__nglir, xgnj__vffqm,
                kdy__haztj)
        else:
            cwf__jjlk = SeriesType(zeqt__hac.dtype, yhzqy__nglir,
                xgnj__vffqm, kdy__haztj)
        gwtv__zxqc = cwf__jjlk,
        if vpo__ndp is not None:
            gwtv__zxqc += tuple(vpo__ndp.types)
        try:
            if not arj__cbln:
                dcwk__pqly = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(kjwj__ybt), self.context,
                    'DataFrame.apply', axis if pkel__ugqp == 1 else None)
            else:
                dcwk__pqly = get_const_func_output_type(kjwj__ybt,
                    gwtv__zxqc, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as mitza__nzdc:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()',
                mitza__nzdc))
        if arj__cbln:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(dcwk__pqly, (SeriesType, HeterogeneousSeriesType)
                ) and dcwk__pqly.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(dcwk__pqly, HeterogeneousSeriesType):
                rmt__uizt, qvhq__qusq = dcwk__pqly.const_info
                if isinstance(dcwk__pqly.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    vtuxz__xgn = dcwk__pqly.data.tuple_typ.types
                elif isinstance(dcwk__pqly.data, types.Tuple):
                    vtuxz__xgn = dcwk__pqly.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                nmq__fqkoo = tuple(to_nullable_type(dtype_to_array_type(
                    ley__wuhqs)) for ley__wuhqs in vtuxz__xgn)
                ricgp__engox = DataFrameType(nmq__fqkoo, df.index, qvhq__qusq)
            elif isinstance(dcwk__pqly, SeriesType):
                plyp__ezv, qvhq__qusq = dcwk__pqly.const_info
                nmq__fqkoo = tuple(to_nullable_type(dtype_to_array_type(
                    dcwk__pqly.dtype)) for rmt__uizt in range(plyp__ezv))
                ricgp__engox = DataFrameType(nmq__fqkoo, df.index, qvhq__qusq)
            else:
                ywh__hagh = get_udf_out_arr_type(dcwk__pqly)
                ricgp__engox = SeriesType(ywh__hagh.dtype, ywh__hagh, df.
                    index, None)
        else:
            ricgp__engox = dcwk__pqly
        obk__phqo = ', '.join("{} = ''".format(qrdat__mnkc) for qrdat__mnkc in
            kws.keys())
        vxgvf__oga = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {obk__phqo}):
"""
        vxgvf__oga += '    pass\n'
        rmy__pcp = {}
        exec(vxgvf__oga, {}, rmy__pcp)
        aoz__zhdr = rmy__pcp['apply_stub']
        ngr__peugo = numba.core.utils.pysignature(aoz__zhdr)
        ubs__myvm = (kjwj__ybt, axis, quuqr__olnfh, agerc__iuhg, vpo__ndp
            ) + tuple(kws.values())
        return signature(ricgp__engox, *ubs__myvm).replace(pysig=ngr__peugo)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        rupli__dso = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        hxr__vixv = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        qfin__lwt = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        ngr__peugo, qkkf__pee = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, rupli__dso, hxr__vixv, qfin__lwt)
        iyaob__alpnn = qkkf__pee[2]
        if not is_overload_constant_str(iyaob__alpnn):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        url__ogcfp = qkkf__pee[0]
        if not is_overload_none(url__ogcfp) and not (is_overload_int(
            url__ogcfp) or is_overload_constant_str(url__ogcfp)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(url__ogcfp):
            sdmb__mcog = get_overload_const_str(url__ogcfp)
            if sdmb__mcog not in df.columns:
                raise BodoError(f'{func_name}: {sdmb__mcog} column not found.')
        elif is_overload_int(url__ogcfp):
            fts__zvwm = get_overload_const_int(url__ogcfp)
            if fts__zvwm > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {fts__zvwm} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            url__ogcfp = df.columns[url__ogcfp]
        iva__phv = qkkf__pee[1]
        if not is_overload_none(iva__phv) and not (is_overload_int(iva__phv
            ) or is_overload_constant_str(iva__phv)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(iva__phv):
            buc__gkl = get_overload_const_str(iva__phv)
            if buc__gkl not in df.columns:
                raise BodoError(f'{func_name}: {buc__gkl} column not found.')
        elif is_overload_int(iva__phv):
            ryiah__gkxkr = get_overload_const_int(iva__phv)
            if ryiah__gkxkr > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {ryiah__gkxkr} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            iva__phv = df.columns[iva__phv]
        dmtm__hkw = qkkf__pee[3]
        if not is_overload_none(dmtm__hkw) and not is_tuple_like_type(dmtm__hkw
            ):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        hfxdi__fno = qkkf__pee[10]
        if not is_overload_none(hfxdi__fno) and not is_overload_constant_str(
            hfxdi__fno):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        chwo__fhj = qkkf__pee[12]
        if not is_overload_bool(chwo__fhj):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        nox__fpuj = qkkf__pee[17]
        if not is_overload_none(nox__fpuj) and not is_tuple_like_type(nox__fpuj
            ):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        dts__hkwi = qkkf__pee[18]
        if not is_overload_none(dts__hkwi) and not is_tuple_like_type(dts__hkwi
            ):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        spx__huy = qkkf__pee[22]
        if not is_overload_none(spx__huy) and not is_overload_int(spx__huy):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        pzs__rtso = qkkf__pee[29]
        if not is_overload_none(pzs__rtso) and not is_overload_constant_str(
            pzs__rtso):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        mol__ugs = qkkf__pee[30]
        if not is_overload_none(mol__ugs) and not is_overload_constant_str(
            mol__ugs):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        uwkyh__cmj = types.List(types.mpl_line_2d_type)
        iyaob__alpnn = get_overload_const_str(iyaob__alpnn)
        if iyaob__alpnn == 'scatter':
            if is_overload_none(url__ogcfp) and is_overload_none(iva__phv):
                raise BodoError(
                    f'{func_name}: {iyaob__alpnn} requires an x and y column.')
            elif is_overload_none(url__ogcfp):
                raise BodoError(
                    f'{func_name}: {iyaob__alpnn} x column is missing.')
            elif is_overload_none(iva__phv):
                raise BodoError(
                    f'{func_name}: {iyaob__alpnn} y column is missing.')
            uwkyh__cmj = types.mpl_path_collection_type
        elif iyaob__alpnn != 'line':
            raise BodoError(
                f'{func_name}: {iyaob__alpnn} plot is not supported.')
        return signature(uwkyh__cmj, *qkkf__pee).replace(pysig=ngr__peugo)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            oqi__earam = df.columns.index(attr)
            arr_typ = df.data[oqi__earam]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            rti__ibgvt = []
            wxeaw__zveci = []
            xxtk__dbmn = False
            for i, gct__vcizr in enumerate(df.columns):
                if gct__vcizr[0] != attr:
                    continue
                xxtk__dbmn = True
                rti__ibgvt.append(gct__vcizr[1] if len(gct__vcizr) == 2 else
                    gct__vcizr[1:])
                wxeaw__zveci.append(df.data[i])
            if xxtk__dbmn:
                return DataFrameType(tuple(wxeaw__zveci), df.index, tuple(
                    rti__ibgvt))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        ojwce__ramn = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(ojwce__ramn)
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
        opu__pbcab = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], opu__pbcab)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    yigvl__bli = builder.module
    seynq__zdmuz = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    nph__kgt = cgutils.get_or_insert_function(yigvl__bli, seynq__zdmuz,
        name='.dtor.df.{}'.format(df_type))
    if not nph__kgt.is_declaration:
        return nph__kgt
    nph__kgt.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(nph__kgt.append_basic_block())
    wxlg__usc = nph__kgt.args[0]
    bzji__hbzey = context.get_value_type(payload_type).as_pointer()
    ixpc__cjx = builder.bitcast(wxlg__usc, bzji__hbzey)
    payload = context.make_helper(builder, payload_type, ref=ixpc__cjx)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        bjqhv__wcm = context.get_python_api(builder)
        nudtu__jpqcn = bjqhv__wcm.gil_ensure()
        bjqhv__wcm.decref(payload.parent)
        bjqhv__wcm.gil_release(nudtu__jpqcn)
    builder.ret_void()
    return nph__kgt


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    pqhb__nhs = cgutils.create_struct_proxy(payload_type)(context, builder)
    pqhb__nhs.data = data_tup
    pqhb__nhs.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        pqhb__nhs.columns = colnames
    mhruw__pxhi = context.get_value_type(payload_type)
    bkhr__ozo = context.get_abi_sizeof(mhruw__pxhi)
    kevd__hen = define_df_dtor(context, builder, df_type, payload_type)
    bqgam__jgvg = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, bkhr__ozo), kevd__hen)
    hiry__nifpb = context.nrt.meminfo_data(builder, bqgam__jgvg)
    kasl__yqr = builder.bitcast(hiry__nifpb, mhruw__pxhi.as_pointer())
    qlgc__kdq = cgutils.create_struct_proxy(df_type)(context, builder)
    qlgc__kdq.meminfo = bqgam__jgvg
    if parent is None:
        qlgc__kdq.parent = cgutils.get_null_value(qlgc__kdq.parent.type)
    else:
        qlgc__kdq.parent = parent
        pqhb__nhs.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            bjqhv__wcm = context.get_python_api(builder)
            nudtu__jpqcn = bjqhv__wcm.gil_ensure()
            bjqhv__wcm.incref(parent)
            bjqhv__wcm.gil_release(nudtu__jpqcn)
    builder.store(pqhb__nhs._getvalue(), kasl__yqr)
    return qlgc__kdq._getvalue()


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
        lhal__brky = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        lhal__brky = [ley__wuhqs for ley__wuhqs in data_typ.dtype.arr_types]
    fvkj__xgrzx = DataFrameType(tuple(lhal__brky + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        prk__xwh = construct_dataframe(context, builder, df_type, data_tup,
            index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return prk__xwh
    sig = signature(fvkj__xgrzx, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    plyp__ezv = len(data_tup_typ.types)
    if plyp__ezv == 0:
        column_names = ()
    bem__maeso = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(bem__maeso, ColNamesMetaType) and isinstance(bem__maeso
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = bem__maeso.meta
    if plyp__ezv == 1 and isinstance(data_tup_typ.types[0], TableType):
        plyp__ezv = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == plyp__ezv, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    tuhqu__qft = data_tup_typ.types
    if plyp__ezv != 0 and isinstance(data_tup_typ.types[0], TableType):
        tuhqu__qft = data_tup_typ.types[0].arr_types
        is_table_format = True
    fvkj__xgrzx = DataFrameType(tuhqu__qft, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            qfcpm__vjxci = cgutils.create_struct_proxy(fvkj__xgrzx.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = qfcpm__vjxci.parent
        prk__xwh = construct_dataframe(context, builder, df_type, data_tup,
            index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return prk__xwh
    sig = signature(fvkj__xgrzx, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        qlgc__kdq = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, qlgc__kdq.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        pqhb__nhs = get_dataframe_payload(context, builder, df_typ, args[0])
        oqr__qrac = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[oqr__qrac]
        if df_typ.is_table_format:
            qfcpm__vjxci = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(pqhb__nhs.data, 0))
            mgugq__nkjb = df_typ.table_type.type_to_blk[arr_typ]
            tut__vaei = getattr(qfcpm__vjxci, f'block_{mgugq__nkjb}')
            dryp__ljf = ListInstance(context, builder, types.List(arr_typ),
                tut__vaei)
            yejdy__ayrxd = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[oqr__qrac])
            opu__pbcab = dryp__ljf.getitem(yejdy__ayrxd)
        else:
            opu__pbcab = builder.extract_value(pqhb__nhs.data, oqr__qrac)
        lkl__xye = cgutils.alloca_once_value(builder, opu__pbcab)
        cajbz__iomsi = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, lkl__xye, cajbz__iomsi)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    bqgam__jgvg = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, bqgam__jgvg)
    bzji__hbzey = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, bzji__hbzey)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    fvkj__xgrzx = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        fvkj__xgrzx = types.Tuple([TableType(df_typ.data)])
    sig = signature(fvkj__xgrzx, df_typ)

    def codegen(context, builder, signature, args):
        pqhb__nhs = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            pqhb__nhs.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        pqhb__nhs = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, pqhb__nhs.
            index)
    fvkj__xgrzx = df_typ.index
    sig = signature(fvkj__xgrzx, df_typ)
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
        fyir__oshab = df.data[i]
        return fyir__oshab(*args)


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
        pqhb__nhs = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(pqhb__nhs.data, 0))
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
    iwo__kfqi = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{iwo__kfqi})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        fyir__oshab = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return fyir__oshab(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        pqhb__nhs = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, pqhb__nhs.columns)
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
    zeqt__hac = self.typemap[data_tup.name]
    if any(is_tuple_like_type(ley__wuhqs) for ley__wuhqs in zeqt__hac.types):
        return None
    if equiv_set.has_shape(data_tup):
        vhxh__zxyyh = equiv_set.get_shape(data_tup)
        if len(vhxh__zxyyh) > 1:
            equiv_set.insert_equiv(*vhxh__zxyyh)
        if len(vhxh__zxyyh) > 0:
            xgnj__vffqm = self.typemap[index.name]
            if not isinstance(xgnj__vffqm, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(vhxh__zxyyh[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(vhxh__zxyyh[0], len(
                vhxh__zxyyh)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    zibt__mrg = args[0]
    data_types = self.typemap[zibt__mrg.name].data
    if any(is_tuple_like_type(ley__wuhqs) for ley__wuhqs in data_types):
        return None
    if equiv_set.has_shape(zibt__mrg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            zibt__mrg)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    zibt__mrg = args[0]
    xgnj__vffqm = self.typemap[zibt__mrg.name].index
    if isinstance(xgnj__vffqm, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(zibt__mrg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            zibt__mrg)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    zibt__mrg = args[0]
    if equiv_set.has_shape(zibt__mrg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            zibt__mrg), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    zibt__mrg = args[0]
    if equiv_set.has_shape(zibt__mrg):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            zibt__mrg)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    oqr__qrac = get_overload_const_int(c_ind_typ)
    if df_typ.data[oqr__qrac] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        omky__owu, rmt__uizt, chntq__towqa = args
        pqhb__nhs = get_dataframe_payload(context, builder, df_typ, omky__owu)
        if df_typ.is_table_format:
            qfcpm__vjxci = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(pqhb__nhs.data, 0))
            mgugq__nkjb = df_typ.table_type.type_to_blk[arr_typ]
            tut__vaei = getattr(qfcpm__vjxci, f'block_{mgugq__nkjb}')
            dryp__ljf = ListInstance(context, builder, types.List(arr_typ),
                tut__vaei)
            yejdy__ayrxd = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[oqr__qrac])
            dryp__ljf.setitem(yejdy__ayrxd, chntq__towqa, True)
        else:
            opu__pbcab = builder.extract_value(pqhb__nhs.data, oqr__qrac)
            context.nrt.decref(builder, df_typ.data[oqr__qrac], opu__pbcab)
            pqhb__nhs.data = builder.insert_value(pqhb__nhs.data,
                chntq__towqa, oqr__qrac)
            context.nrt.incref(builder, arr_typ, chntq__towqa)
        qlgc__kdq = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=omky__owu)
        payload_type = DataFramePayloadType(df_typ)
        ixpc__cjx = context.nrt.meminfo_data(builder, qlgc__kdq.meminfo)
        bzji__hbzey = context.get_value_type(payload_type).as_pointer()
        ixpc__cjx = builder.bitcast(ixpc__cjx, bzji__hbzey)
        builder.store(pqhb__nhs._getvalue(), ixpc__cjx)
        return impl_ret_borrowed(context, builder, df_typ, omky__owu)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        bnqte__qoc = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        fmwsq__tbz = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=bnqte__qoc)
        btde__lvfi = get_dataframe_payload(context, builder, df_typ, bnqte__qoc
            )
        qlgc__kdq = construct_dataframe(context, builder, signature.
            return_type, btde__lvfi.data, index_val, fmwsq__tbz.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), btde__lvfi.data)
        return qlgc__kdq
    fvkj__xgrzx = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(fvkj__xgrzx, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    plyp__ezv = len(df_type.columns)
    and__azup = plyp__ezv
    jbey__ndjo = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    nul__xtr = col_name not in df_type.columns
    oqr__qrac = plyp__ezv
    if nul__xtr:
        jbey__ndjo += arr_type,
        column_names += col_name,
        and__azup += 1
    else:
        oqr__qrac = df_type.columns.index(col_name)
        jbey__ndjo = tuple(arr_type if i == oqr__qrac else jbey__ndjo[i] for
            i in range(plyp__ezv))

    def codegen(context, builder, signature, args):
        omky__owu, rmt__uizt, chntq__towqa = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, omky__owu)
        ejy__qsk = cgutils.create_struct_proxy(df_type)(context, builder,
            value=omky__owu)
        if df_type.is_table_format:
            vzs__tzf = df_type.table_type
            rjgfa__sqwq = builder.extract_value(in_dataframe_payload.data, 0)
            aytop__kiov = TableType(jbey__ndjo)
            kzby__cufvi = set_table_data_codegen(context, builder, vzs__tzf,
                rjgfa__sqwq, aytop__kiov, arr_type, chntq__towqa, oqr__qrac,
                nul__xtr)
            data_tup = context.make_tuple(builder, types.Tuple([aytop__kiov
                ]), [kzby__cufvi])
        else:
            tuhqu__qft = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != oqr__qrac else chntq__towqa) for i in range(
                plyp__ezv)]
            if nul__xtr:
                tuhqu__qft.append(chntq__towqa)
            for zibt__mrg, ekrfi__jdrc in zip(tuhqu__qft, jbey__ndjo):
                context.nrt.incref(builder, ekrfi__jdrc, zibt__mrg)
            data_tup = context.make_tuple(builder, types.Tuple(jbey__ndjo),
                tuhqu__qft)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        kdyr__ctm = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, ejy__qsk.parent, None)
        if not nul__xtr and arr_type == df_type.data[oqr__qrac]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            ixpc__cjx = context.nrt.meminfo_data(builder, ejy__qsk.meminfo)
            bzji__hbzey = context.get_value_type(payload_type).as_pointer()
            ixpc__cjx = builder.bitcast(ixpc__cjx, bzji__hbzey)
            uvq__cqtc = get_dataframe_payload(context, builder, df_type,
                kdyr__ctm)
            builder.store(uvq__cqtc._getvalue(), ixpc__cjx)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, aytop__kiov, builder.
                    extract_value(data_tup, 0))
            else:
                for zibt__mrg, ekrfi__jdrc in zip(tuhqu__qft, jbey__ndjo):
                    context.nrt.incref(builder, ekrfi__jdrc, zibt__mrg)
        has_parent = cgutils.is_not_null(builder, ejy__qsk.parent)
        with builder.if_then(has_parent):
            bjqhv__wcm = context.get_python_api(builder)
            nudtu__jpqcn = bjqhv__wcm.gil_ensure()
            ptd__pqpr = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, chntq__towqa)
            xwip__dvn = numba.core.pythonapi._BoxContext(context, builder,
                bjqhv__wcm, ptd__pqpr)
            spvmb__ebd = xwip__dvn.pyapi.from_native_value(arr_type,
                chntq__towqa, xwip__dvn.env_manager)
            if isinstance(col_name, str):
                tjrm__njxjt = context.insert_const_string(builder.module,
                    col_name)
                zjxs__gees = bjqhv__wcm.string_from_string(tjrm__njxjt)
            else:
                assert isinstance(col_name, int)
                zjxs__gees = bjqhv__wcm.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            bjqhv__wcm.object_setitem(ejy__qsk.parent, zjxs__gees, spvmb__ebd)
            bjqhv__wcm.decref(spvmb__ebd)
            bjqhv__wcm.decref(zjxs__gees)
            bjqhv__wcm.gil_release(nudtu__jpqcn)
        return kdyr__ctm
    fvkj__xgrzx = DataFrameType(jbey__ndjo, index_typ, column_names,
        df_type.dist, df_type.is_table_format)
    sig = signature(fvkj__xgrzx, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    plyp__ezv = len(pyval.columns)
    tuhqu__qft = []
    for i in range(plyp__ezv):
        qstpt__inwl = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            spvmb__ebd = qstpt__inwl.array
        else:
            spvmb__ebd = qstpt__inwl.values
        tuhqu__qft.append(spvmb__ebd)
    tuhqu__qft = tuple(tuhqu__qft)
    if df_type.is_table_format:
        qfcpm__vjxci = context.get_constant_generic(builder, df_type.
            table_type, Table(tuhqu__qft))
        data_tup = lir.Constant.literal_struct([qfcpm__vjxci])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], gct__vcizr) for 
            i, gct__vcizr in enumerate(tuhqu__qft)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    daga__zkdr = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, daga__zkdr])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    yzzrh__jle = context.get_constant(types.int64, -1)
    fkjqb__lik = context.get_constant_null(types.voidptr)
    bqgam__jgvg = lir.Constant.literal_struct([yzzrh__jle, fkjqb__lik,
        fkjqb__lik, payload, yzzrh__jle])
    bqgam__jgvg = cgutils.global_constant(builder, '.const.meminfo',
        bqgam__jgvg).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([bqgam__jgvg, daga__zkdr])


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
        ycldr__koomb = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        ycldr__koomb = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, ycldr__koomb)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        wxeaw__zveci = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                wxeaw__zveci)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), wxeaw__zveci)
    elif not fromty.is_table_format and toty.is_table_format:
        wxeaw__zveci = _cast_df_data_to_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        wxeaw__zveci = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        wxeaw__zveci = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        wxeaw__zveci = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, wxeaw__zveci,
        ycldr__koomb, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    gfeon__cjll = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        dyhgi__twm = get_index_data_arr_types(toty.index)[0]
        vypoa__shf = bodo.utils.transform.get_type_alloc_counts(dyhgi__twm) - 1
        zocx__ywem = ', '.join('0' for rmt__uizt in range(vypoa__shf))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(zocx__ywem, ', ' if vypoa__shf == 1 else ''))
        gfeon__cjll['index_arr_type'] = dyhgi__twm
    vqzuu__vgzaf = []
    for i, arr_typ in enumerate(toty.data):
        vypoa__shf = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        zocx__ywem = ', '.join('0' for rmt__uizt in range(vypoa__shf))
        ngons__vseud = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'
            .format(i, zocx__ywem, ', ' if vypoa__shf == 1 else ''))
        vqzuu__vgzaf.append(ngons__vseud)
        gfeon__cjll[f'arr_type{i}'] = arr_typ
    vqzuu__vgzaf = ', '.join(vqzuu__vgzaf)
    vxgvf__oga = 'def impl():\n'
    mgh__rzzqr = bodo.hiframes.dataframe_impl._gen_init_df(vxgvf__oga, toty
        .columns, vqzuu__vgzaf, index, gfeon__cjll)
    df = context.compile_internal(builder, mgh__rzzqr, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    xca__aiht = toty.table_type
    qfcpm__vjxci = cgutils.create_struct_proxy(xca__aiht)(context, builder)
    qfcpm__vjxci.parent = in_dataframe_payload.parent
    for ley__wuhqs, mgugq__nkjb in xca__aiht.type_to_blk.items():
        lehiz__ttzx = context.get_constant(types.int64, len(xca__aiht.
            block_to_arr_ind[mgugq__nkjb]))
        rmt__uizt, mxyh__nlcfn = ListInstance.allocate_ex(context, builder,
            types.List(ley__wuhqs), lehiz__ttzx)
        mxyh__nlcfn.size = lehiz__ttzx
        setattr(qfcpm__vjxci, f'block_{mgugq__nkjb}', mxyh__nlcfn.value)
    for i, ley__wuhqs in enumerate(fromty.data):
        pgxws__uut = toty.data[i]
        if ley__wuhqs != pgxws__uut:
            qjo__gxmyi = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qjo__gxmyi)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        opu__pbcab = builder.extract_value(in_dataframe_payload.data, i)
        if ley__wuhqs != pgxws__uut:
            rtqxd__xfv = context.cast(builder, opu__pbcab, ley__wuhqs,
                pgxws__uut)
            xdnl__ebo = False
        else:
            rtqxd__xfv = opu__pbcab
            xdnl__ebo = True
        mgugq__nkjb = xca__aiht.type_to_blk[ley__wuhqs]
        tut__vaei = getattr(qfcpm__vjxci, f'block_{mgugq__nkjb}')
        dryp__ljf = ListInstance(context, builder, types.List(ley__wuhqs),
            tut__vaei)
        yejdy__ayrxd = context.get_constant(types.int64, xca__aiht.
            block_offsets[i])
        dryp__ljf.setitem(yejdy__ayrxd, rtqxd__xfv, xdnl__ebo)
    data_tup = context.make_tuple(builder, types.Tuple([xca__aiht]), [
        qfcpm__vjxci._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    tuhqu__qft = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            qjo__gxmyi = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qjo__gxmyi)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            opu__pbcab = builder.extract_value(in_dataframe_payload.data, i)
            rtqxd__xfv = context.cast(builder, opu__pbcab, fromty.data[i],
                toty.data[i])
            xdnl__ebo = False
        else:
            rtqxd__xfv = builder.extract_value(in_dataframe_payload.data, i)
            xdnl__ebo = True
        if xdnl__ebo:
            context.nrt.incref(builder, toty.data[i], rtqxd__xfv)
        tuhqu__qft.append(rtqxd__xfv)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), tuhqu__qft)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    vzs__tzf = fromty.table_type
    rjgfa__sqwq = cgutils.create_struct_proxy(vzs__tzf)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    aytop__kiov = toty.table_type
    kzby__cufvi = cgutils.create_struct_proxy(aytop__kiov)(context, builder)
    kzby__cufvi.parent = in_dataframe_payload.parent
    for ley__wuhqs, mgugq__nkjb in aytop__kiov.type_to_blk.items():
        lehiz__ttzx = context.get_constant(types.int64, len(aytop__kiov.
            block_to_arr_ind[mgugq__nkjb]))
        rmt__uizt, mxyh__nlcfn = ListInstance.allocate_ex(context, builder,
            types.List(ley__wuhqs), lehiz__ttzx)
        mxyh__nlcfn.size = lehiz__ttzx
        setattr(kzby__cufvi, f'block_{mgugq__nkjb}', mxyh__nlcfn.value)
    for i in range(len(fromty.data)):
        iics__lcsk = fromty.data[i]
        pgxws__uut = toty.data[i]
        if iics__lcsk != pgxws__uut:
            qjo__gxmyi = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qjo__gxmyi)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        tohll__kuim = vzs__tzf.type_to_blk[iics__lcsk]
        qbvwq__hzk = getattr(rjgfa__sqwq, f'block_{tohll__kuim}')
        zjwc__dwggc = ListInstance(context, builder, types.List(iics__lcsk),
            qbvwq__hzk)
        osm__bxaf = context.get_constant(types.int64, vzs__tzf.block_offsets[i]
            )
        opu__pbcab = zjwc__dwggc.getitem(osm__bxaf)
        if iics__lcsk != pgxws__uut:
            rtqxd__xfv = context.cast(builder, opu__pbcab, iics__lcsk,
                pgxws__uut)
            xdnl__ebo = False
        else:
            rtqxd__xfv = opu__pbcab
            xdnl__ebo = True
        pcm__bici = aytop__kiov.type_to_blk[ley__wuhqs]
        mxyh__nlcfn = getattr(kzby__cufvi, f'block_{pcm__bici}')
        thgq__fxwu = ListInstance(context, builder, types.List(pgxws__uut),
            mxyh__nlcfn)
        dbx__scqy = context.get_constant(types.int64, aytop__kiov.
            block_offsets[i])
        thgq__fxwu.setitem(dbx__scqy, rtqxd__xfv, xdnl__ebo)
    data_tup = context.make_tuple(builder, types.Tuple([aytop__kiov]), [
        kzby__cufvi._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    xca__aiht = fromty.table_type
    qfcpm__vjxci = cgutils.create_struct_proxy(xca__aiht)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    tuhqu__qft = []
    for i, ley__wuhqs in enumerate(toty.data):
        iics__lcsk = fromty.data[i]
        if ley__wuhqs != iics__lcsk:
            qjo__gxmyi = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*qjo__gxmyi)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        mgugq__nkjb = xca__aiht.type_to_blk[ley__wuhqs]
        tut__vaei = getattr(qfcpm__vjxci, f'block_{mgugq__nkjb}')
        dryp__ljf = ListInstance(context, builder, types.List(ley__wuhqs),
            tut__vaei)
        yejdy__ayrxd = context.get_constant(types.int64, xca__aiht.
            block_offsets[i])
        opu__pbcab = dryp__ljf.getitem(yejdy__ayrxd)
        if ley__wuhqs != iics__lcsk:
            rtqxd__xfv = context.cast(builder, opu__pbcab, iics__lcsk,
                ley__wuhqs)
            xdnl__ebo = False
        else:
            rtqxd__xfv = opu__pbcab
            xdnl__ebo = True
        if xdnl__ebo:
            context.nrt.incref(builder, ley__wuhqs, rtqxd__xfv)
        tuhqu__qft.append(rtqxd__xfv)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), tuhqu__qft)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    sgk__eaz, vqzuu__vgzaf, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    cvu__wvog = ColNamesMetaType(tuple(sgk__eaz))
    vxgvf__oga = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    vxgvf__oga += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(vqzuu__vgzaf, index_arg))
    rmy__pcp = {}
    exec(vxgvf__oga, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': cvu__wvog}, rmy__pcp)
    errcl__rwi = rmy__pcp['_init_df']
    return errcl__rwi


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    fvkj__xgrzx = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(fvkj__xgrzx, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    fvkj__xgrzx = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(fvkj__xgrzx, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    two__iykk = ''
    if not is_overload_none(dtype):
        two__iykk = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        plyp__ezv = (len(data.types) - 1) // 2
        hkmqa__ctm = [ley__wuhqs.literal_value for ley__wuhqs in data.types
            [1:plyp__ezv + 1]]
        data_val_types = dict(zip(hkmqa__ctm, data.types[plyp__ezv + 1:]))
        tuhqu__qft = ['data[{}]'.format(i) for i in range(plyp__ezv + 1, 2 *
            plyp__ezv + 1)]
        data_dict = dict(zip(hkmqa__ctm, tuhqu__qft))
        if is_overload_none(index):
            for i, ley__wuhqs in enumerate(data.types[plyp__ezv + 1:]):
                if isinstance(ley__wuhqs, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(plyp__ezv + 1 + i))
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
        eeool__dhncu = '.copy()' if copy else ''
        tner__eipyi = get_overload_const_list(columns)
        plyp__ezv = len(tner__eipyi)
        data_val_types = {xwip__dvn: data.copy(ndim=1) for xwip__dvn in
            tner__eipyi}
        tuhqu__qft = ['data[:,{}]{}'.format(i, eeool__dhncu) for i in range
            (plyp__ezv)]
        data_dict = dict(zip(tner__eipyi, tuhqu__qft))
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
    vqzuu__vgzaf = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[xwip__dvn], df_len, two__iykk) for xwip__dvn in
        col_names))
    if len(col_names) == 0:
        vqzuu__vgzaf = '()'
    return col_names, vqzuu__vgzaf, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for xwip__dvn in col_names:
        if xwip__dvn in data_dict and is_iterable_type(data_val_types[
            xwip__dvn]):
            df_len = 'len({})'.format(data_dict[xwip__dvn])
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
    if all(xwip__dvn in data_dict for xwip__dvn in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    qvs__bkczr = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for xwip__dvn in col_names:
        if xwip__dvn not in data_dict:
            data_dict[xwip__dvn] = qvs__bkczr


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
            ley__wuhqs = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            return len(ley__wuhqs)
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
        mxui__dda = idx.literal_value
        if isinstance(mxui__dda, int):
            fyir__oshab = tup.types[mxui__dda]
        elif isinstance(mxui__dda, slice):
            fyir__oshab = types.BaseTuple.from_types(tup.types[mxui__dda])
        return signature(fyir__oshab, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    lagxx__aaq, idx = sig.args
    idx = idx.literal_value
    tup, rmt__uizt = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(lagxx__aaq)
        if not 0 <= idx < len(lagxx__aaq):
            raise IndexError('cannot index at %d in %s' % (idx, lagxx__aaq))
        tjmhu__fxuo = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        btd__wasf = cgutils.unpack_tuple(builder, tup)[idx]
        tjmhu__fxuo = context.make_tuple(builder, sig.return_type, btd__wasf)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, tjmhu__fxuo)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, vsrwl__vhrm, suffix_x,
            suffix_y, is_join, indicator, rmt__uizt, rmt__uizt) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        ezrpy__odlsk = {xwip__dvn: i for i, xwip__dvn in enumerate(left_on)}
        nsyop__vawvv = {xwip__dvn: i for i, xwip__dvn in enumerate(right_on)}
        run__vznh = set(left_on) & set(right_on)
        hhdra__tcxw = set(left_df.columns) & set(right_df.columns)
        mlatj__cqg = hhdra__tcxw - run__vznh
        sxkpz__irc = '$_bodo_index_' in left_on
        apxi__dbm = '$_bodo_index_' in right_on
        how = get_overload_const_str(vsrwl__vhrm)
        fuh__fol = how in {'left', 'outer'}
        lepi__det = how in {'right', 'outer'}
        columns = []
        data = []
        if sxkpz__irc:
            npjh__futeo = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            npjh__futeo = left_df.data[left_df.column_index[left_on[0]]]
        if apxi__dbm:
            oyik__jsn = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            oyik__jsn = right_df.data[right_df.column_index[right_on[0]]]
        if sxkpz__irc and not apxi__dbm and not is_join.literal_value:
            jzedo__fimc = right_on[0]
            if jzedo__fimc in left_df.column_index:
                columns.append(jzedo__fimc)
                if (oyik__jsn == bodo.dict_str_arr_type and npjh__futeo ==
                    bodo.string_array_type):
                    lpq__hcw = bodo.string_array_type
                else:
                    lpq__hcw = oyik__jsn
                data.append(lpq__hcw)
        if apxi__dbm and not sxkpz__irc and not is_join.literal_value:
            khfmm__mjc = left_on[0]
            if khfmm__mjc in right_df.column_index:
                columns.append(khfmm__mjc)
                if (npjh__futeo == bodo.dict_str_arr_type and oyik__jsn ==
                    bodo.string_array_type):
                    lpq__hcw = bodo.string_array_type
                else:
                    lpq__hcw = npjh__futeo
                data.append(lpq__hcw)
        for iics__lcsk, qstpt__inwl in zip(left_df.data, left_df.columns):
            columns.append(str(qstpt__inwl) + suffix_x.literal_value if 
                qstpt__inwl in mlatj__cqg else qstpt__inwl)
            if qstpt__inwl in run__vznh:
                if iics__lcsk == bodo.dict_str_arr_type:
                    iics__lcsk = right_df.data[right_df.column_index[
                        qstpt__inwl]]
                data.append(iics__lcsk)
            else:
                if (iics__lcsk == bodo.dict_str_arr_type and qstpt__inwl in
                    ezrpy__odlsk):
                    if apxi__dbm:
                        iics__lcsk = oyik__jsn
                    else:
                        adcpf__feywe = ezrpy__odlsk[qstpt__inwl]
                        zutf__slatf = right_on[adcpf__feywe]
                        iics__lcsk = right_df.data[right_df.column_index[
                            zutf__slatf]]
                if lepi__det:
                    iics__lcsk = to_nullable_type(iics__lcsk)
                data.append(iics__lcsk)
        for iics__lcsk, qstpt__inwl in zip(right_df.data, right_df.columns):
            if qstpt__inwl not in run__vznh:
                columns.append(str(qstpt__inwl) + suffix_y.literal_value if
                    qstpt__inwl in mlatj__cqg else qstpt__inwl)
                if (iics__lcsk == bodo.dict_str_arr_type and qstpt__inwl in
                    nsyop__vawvv):
                    if sxkpz__irc:
                        iics__lcsk = npjh__futeo
                    else:
                        adcpf__feywe = nsyop__vawvv[qstpt__inwl]
                        psd__mtge = left_on[adcpf__feywe]
                        iics__lcsk = left_df.data[left_df.column_index[
                            psd__mtge]]
                if fuh__fol:
                    iics__lcsk = to_nullable_type(iics__lcsk)
                data.append(iics__lcsk)
        fius__rnauv = get_overload_const_bool(indicator)
        if fius__rnauv:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        pdxrx__rqulr = False
        if sxkpz__irc and apxi__dbm and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            pdxrx__rqulr = True
        elif sxkpz__irc and not apxi__dbm:
            index_typ = right_df.index
            pdxrx__rqulr = True
        elif apxi__dbm and not sxkpz__irc:
            index_typ = left_df.index
            pdxrx__rqulr = True
        if pdxrx__rqulr and isinstance(index_typ, bodo.hiframes.
            pd_index_ext.RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        eict__iwts = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(eict__iwts, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    qlgc__kdq = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return qlgc__kdq._getvalue()


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
    muw__pcjka = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    hxr__vixv = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', muw__pcjka, hxr__vixv,
        package_name='pandas', module_name='General')
    vxgvf__oga = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        qlh__nso = 0
        vqzuu__vgzaf = []
        names = []
        for i, crcfb__vgyl in enumerate(objs.types):
            assert isinstance(crcfb__vgyl, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(crcfb__vgyl, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                crcfb__vgyl, 'pandas.concat()')
            if isinstance(crcfb__vgyl, SeriesType):
                names.append(str(qlh__nso))
                qlh__nso += 1
                vqzuu__vgzaf.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(crcfb__vgyl.columns)
                for gbw__nfanl in range(len(crcfb__vgyl.data)):
                    vqzuu__vgzaf.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, gbw__nfanl))
        return bodo.hiframes.dataframe_impl._gen_init_df(vxgvf__oga, names,
            ', '.join(vqzuu__vgzaf), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(ley__wuhqs, DataFrameType) for ley__wuhqs in
            objs.types)
        bvhtt__rawax = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            bvhtt__rawax.extend(df.columns)
        bvhtt__rawax = list(dict.fromkeys(bvhtt__rawax).keys())
        lhal__brky = {}
        for qlh__nso, xwip__dvn in enumerate(bvhtt__rawax):
            for i, df in enumerate(objs.types):
                if xwip__dvn in df.column_index:
                    lhal__brky[f'arr_typ{qlh__nso}'] = df.data[df.
                        column_index[xwip__dvn]]
                    break
        assert len(lhal__brky) == len(bvhtt__rawax)
        lphxg__mpfq = []
        for qlh__nso, xwip__dvn in enumerate(bvhtt__rawax):
            args = []
            for i, df in enumerate(objs.types):
                if xwip__dvn in df.column_index:
                    oqr__qrac = df.column_index[xwip__dvn]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, oqr__qrac))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, qlh__nso))
            vxgvf__oga += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(qlh__nso, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(vxgvf__oga,
            bvhtt__rawax, ', '.join('A{}'.format(i) for i in range(len(
            bvhtt__rawax))), index, lhal__brky)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(ley__wuhqs, SeriesType) for ley__wuhqs in
            objs.types)
        vxgvf__oga += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            vxgvf__oga += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            vxgvf__oga += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        vxgvf__oga += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        rmy__pcp = {}
        exec(vxgvf__oga, {'bodo': bodo, 'np': np, 'numba': numba}, rmy__pcp)
        return rmy__pcp['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for qlh__nso, xwip__dvn in enumerate(df_type.columns):
            vxgvf__oga += '  arrs{} = []\n'.format(qlh__nso)
            vxgvf__oga += '  for i in range(len(objs)):\n'
            vxgvf__oga += '    df = objs[i]\n'
            vxgvf__oga += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(qlh__nso))
            vxgvf__oga += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(qlh__nso))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            vxgvf__oga += '  arrs_index = []\n'
            vxgvf__oga += '  for i in range(len(objs)):\n'
            vxgvf__oga += '    df = objs[i]\n'
            vxgvf__oga += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(vxgvf__oga,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        vxgvf__oga += '  arrs = []\n'
        vxgvf__oga += '  for i in range(len(objs)):\n'
        vxgvf__oga += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        vxgvf__oga += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            vxgvf__oga += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            vxgvf__oga += '  arrs_index = []\n'
            vxgvf__oga += '  for i in range(len(objs)):\n'
            vxgvf__oga += '    S = objs[i]\n'
            vxgvf__oga += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            vxgvf__oga += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        vxgvf__oga += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        rmy__pcp = {}
        exec(vxgvf__oga, {'bodo': bodo, 'np': np, 'numba': numba}, rmy__pcp)
        return rmy__pcp['impl']
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
        fvkj__xgrzx = df.copy(index=index)
        return signature(fvkj__xgrzx, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    dio__ustee = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return dio__ustee._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    muw__pcjka = dict(index=index, name=name)
    hxr__vixv = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', muw__pcjka, hxr__vixv,
        package_name='pandas', module_name='DataFrame')

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
        lhal__brky = (types.Array(types.int64, 1, 'C'),) + df.data
        gdi__bpg = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(columns,
            lhal__brky)
        return signature(gdi__bpg, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    dio__ustee = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return dio__ustee._getvalue()


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
    dio__ustee = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return dio__ustee._getvalue()


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
    dio__ustee = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return dio__ustee._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    xpfs__yzfmy = get_overload_const_bool(check_duplicates)
    sgxhi__jqyx = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    ahvx__bwxa = len(value_names) > 1
    rsww__cceyt = None
    mor__psqnx = None
    eziqx__woz = None
    aovy__fjfxz = None
    ospdz__mco = isinstance(values_tup, types.UniTuple)
    if ospdz__mco:
        smny__yrae = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        smny__yrae = [to_str_arr_if_dict_array(to_nullable_type(ekrfi__jdrc
            )) for ekrfi__jdrc in values_tup]
    vxgvf__oga = 'def impl(\n'
    vxgvf__oga += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, _constant_pivot_values=None, parallel=False
"""
    vxgvf__oga += '):\n'
    vxgvf__oga += '    if parallel:\n'
    isac__auf = ', '.join([f'array_to_info(index_tup[{i}])' for i in range(
        len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    vxgvf__oga += f'        info_list = [{isac__auf}]\n'
    vxgvf__oga += '        cpp_table = arr_info_list_to_table(info_list)\n'
    vxgvf__oga += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
    wmb__xozun = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    tog__gims = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    xqr__rme = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    vxgvf__oga += f'        index_tup = ({wmb__xozun},)\n'
    vxgvf__oga += f'        columns_tup = ({tog__gims},)\n'
    vxgvf__oga += f'        values_tup = ({xqr__rme},)\n'
    vxgvf__oga += '        delete_table(cpp_table)\n'
    vxgvf__oga += '        delete_table(out_cpp_table)\n'
    vxgvf__oga += '    columns_arr = columns_tup[0]\n'
    if ospdz__mco:
        vxgvf__oga += '    values_arrs = [arr for arr in values_tup]\n'
    zgbq__dby = ', '.join([
        f'bodo.utils.typing.decode_if_dict_array(index_tup[{i}])' for i in
        range(len(index_tup))])
    vxgvf__oga += f'    new_index_tup = ({zgbq__dby},)\n'
    vxgvf__oga += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    vxgvf__oga += '        new_index_tup\n'
    vxgvf__oga += '    )\n'
    vxgvf__oga += '    n_rows = len(unique_index_arr_tup[0])\n'
    vxgvf__oga += '    num_values_arrays = len(values_tup)\n'
    vxgvf__oga += '    n_unique_pivots = len(pivot_values)\n'
    if ospdz__mco:
        vxgvf__oga += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        vxgvf__oga += '    n_cols = n_unique_pivots\n'
    vxgvf__oga += '    col_map = {}\n'
    vxgvf__oga += '    for i in range(n_unique_pivots):\n'
    vxgvf__oga += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    vxgvf__oga += '            raise ValueError(\n'
    vxgvf__oga += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    vxgvf__oga += '            )\n'
    vxgvf__oga += '        col_map[pivot_values[i]] = i\n'
    lrty__rxkv = False
    for i, juzy__vszva in enumerate(smny__yrae):
        if is_str_arr_type(juzy__vszva):
            lrty__rxkv = True
            vxgvf__oga += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            vxgvf__oga += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if lrty__rxkv:
        if xpfs__yzfmy:
            vxgvf__oga += '    nbytes = (n_rows + 7) >> 3\n'
            vxgvf__oga += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        vxgvf__oga += '    for i in range(len(columns_arr)):\n'
        vxgvf__oga += '        col_name = columns_arr[i]\n'
        vxgvf__oga += '        pivot_idx = col_map[col_name]\n'
        vxgvf__oga += '        row_idx = row_vector[i]\n'
        if xpfs__yzfmy:
            vxgvf__oga += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            vxgvf__oga += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            vxgvf__oga += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            vxgvf__oga += '        else:\n'
            vxgvf__oga += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if ospdz__mco:
            vxgvf__oga += '        for j in range(num_values_arrays):\n'
            vxgvf__oga += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            vxgvf__oga += '            len_arr = len_arrs_0[col_idx]\n'
            vxgvf__oga += '            values_arr = values_arrs[j]\n'
            vxgvf__oga += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            vxgvf__oga += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            vxgvf__oga += '                len_arr[row_idx] = str_val_len\n'
            vxgvf__oga += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, juzy__vszva in enumerate(smny__yrae):
                if is_str_arr_type(juzy__vszva):
                    vxgvf__oga += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    vxgvf__oga += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    vxgvf__oga += f"""            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}
"""
                    vxgvf__oga += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    for i, juzy__vszva in enumerate(smny__yrae):
        if is_str_arr_type(juzy__vszva):
            vxgvf__oga += f'    data_arrs_{i} = [\n'
            vxgvf__oga += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            vxgvf__oga += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            vxgvf__oga += '        )\n'
            vxgvf__oga += '        for i in range(n_cols)\n'
            vxgvf__oga += '    ]\n'
        else:
            vxgvf__oga += f'    data_arrs_{i} = [\n'
            vxgvf__oga += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            vxgvf__oga += '        for _ in range(n_cols)\n'
            vxgvf__oga += '    ]\n'
    if not lrty__rxkv and xpfs__yzfmy:
        vxgvf__oga += '    nbytes = (n_rows + 7) >> 3\n'
        vxgvf__oga += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    vxgvf__oga += '    for i in range(len(columns_arr)):\n'
    vxgvf__oga += '        col_name = columns_arr[i]\n'
    vxgvf__oga += '        pivot_idx = col_map[col_name]\n'
    vxgvf__oga += '        row_idx = row_vector[i]\n'
    if not lrty__rxkv and xpfs__yzfmy:
        vxgvf__oga += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        vxgvf__oga += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        vxgvf__oga += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        vxgvf__oga += '        else:\n'
        vxgvf__oga += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if ospdz__mco:
        vxgvf__oga += '        for j in range(num_values_arrays):\n'
        vxgvf__oga += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        vxgvf__oga += '            col_arr = data_arrs_0[col_idx]\n'
        vxgvf__oga += '            values_arr = values_arrs[j]\n'
        vxgvf__oga += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        vxgvf__oga += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        vxgvf__oga += '            else:\n'
        vxgvf__oga += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, juzy__vszva in enumerate(smny__yrae):
            vxgvf__oga += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            vxgvf__oga += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            vxgvf__oga += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            vxgvf__oga += f'        else:\n'
            vxgvf__oga += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        vxgvf__oga += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        rsww__cceyt = index_names.meta[0]
    else:
        vxgvf__oga += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        rsww__cceyt = tuple(index_names.meta)
    if not sgxhi__jqyx:
        eziqx__woz = columns_name.meta[0]
        if ahvx__bwxa:
            vxgvf__oga += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            mor__psqnx = value_names.meta
            if all(isinstance(xwip__dvn, str) for xwip__dvn in mor__psqnx):
                mor__psqnx = pd.array(mor__psqnx, 'string')
            elif all(isinstance(xwip__dvn, int) for xwip__dvn in mor__psqnx):
                mor__psqnx = np.array(mor__psqnx, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(mor__psqnx.dtype, pd.StringDtype):
                vxgvf__oga += '    total_chars = 0\n'
                vxgvf__oga += f'    for i in range({len(value_names)}):\n'
                vxgvf__oga += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                vxgvf__oga += '        total_chars += value_name_str_len\n'
                vxgvf__oga += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                vxgvf__oga += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                vxgvf__oga += '    total_chars = 0\n'
                vxgvf__oga += '    for i in range(len(pivot_values)):\n'
                vxgvf__oga += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                vxgvf__oga += '        total_chars += pivot_val_str_len\n'
                vxgvf__oga += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                vxgvf__oga += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            vxgvf__oga += f'    for i in range({len(value_names)}):\n'
            vxgvf__oga += '        for j in range(len(pivot_values)):\n'
            vxgvf__oga += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            vxgvf__oga += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            vxgvf__oga += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            vxgvf__oga += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    xca__aiht = None
    if sgxhi__jqyx:
        if ahvx__bwxa:
            cuk__gwy = []
            for bxdi__iecok in _constant_pivot_values.meta:
                for eklq__zarz in value_names.meta:
                    cuk__gwy.append((bxdi__iecok, eklq__zarz))
            column_names = tuple(cuk__gwy)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        aovy__fjfxz = ColNamesMetaType(column_names)
        vipj__dnspv = []
        for ekrfi__jdrc in smny__yrae:
            vipj__dnspv.extend([ekrfi__jdrc] * len(_constant_pivot_values))
        gutna__ezoqa = tuple(vipj__dnspv)
        xca__aiht = TableType(gutna__ezoqa)
        vxgvf__oga += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        vxgvf__oga += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, ekrfi__jdrc in enumerate(smny__yrae):
            vxgvf__oga += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {xca__aiht.type_to_blk[ekrfi__jdrc]})
"""
        vxgvf__oga += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        vxgvf__oga += '        (table,), index, columns_typ\n'
        vxgvf__oga += '    )\n'
    else:
        cprml__dob = ', '.join(f'data_arrs_{i}' for i in range(len(smny__yrae))
            )
        vxgvf__oga += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({cprml__dob},), n_rows)
"""
        vxgvf__oga += (
            '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        vxgvf__oga += '        (table,), index, column_index\n'
        vxgvf__oga += '    )\n'
    rmy__pcp = {}
    enzlb__mlg = {f'data_arr_typ_{i}': juzy__vszva for i, juzy__vszva in
        enumerate(smny__yrae)}
    ysjh__bycun = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        xca__aiht, 'columns_typ': aovy__fjfxz, 'index_names_lit':
        rsww__cceyt, 'value_names_lit': mor__psqnx, 'columns_name_lit':
        eziqx__woz, **enzlb__mlg}
    exec(vxgvf__oga, ysjh__bycun, rmy__pcp)
    impl = rmy__pcp['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    tnjjl__iflbl = {}
    tnjjl__iflbl['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, ahk__dgng in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        lap__udets = None
        if isinstance(ahk__dgng, bodo.DatetimeArrayType):
            veg__aechb = 'datetimetz'
            csoag__rvvf = 'datetime64[ns]'
            if isinstance(ahk__dgng.tz, int):
                tqt__ciou = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(ahk__dgng.tz))
            else:
                tqt__ciou = pd.DatetimeTZDtype(tz=ahk__dgng.tz).tz
            lap__udets = {'timezone': pa.lib.tzinfo_to_string(tqt__ciou)}
        elif isinstance(ahk__dgng, types.Array) or ahk__dgng == boolean_array:
            veg__aechb = csoag__rvvf = ahk__dgng.dtype.name
            if csoag__rvvf.startswith('datetime'):
                veg__aechb = 'datetime'
        elif is_str_arr_type(ahk__dgng):
            veg__aechb = 'unicode'
            csoag__rvvf = 'object'
        elif ahk__dgng == binary_array_type:
            veg__aechb = 'bytes'
            csoag__rvvf = 'object'
        elif isinstance(ahk__dgng, DecimalArrayType):
            veg__aechb = csoag__rvvf = 'object'
        elif isinstance(ahk__dgng, IntegerArrayType):
            njjha__bfbf = ahk__dgng.dtype.name
            if njjha__bfbf.startswith('int'):
                veg__aechb = 'Int' + njjha__bfbf[3:]
            elif njjha__bfbf.startswith('uint'):
                veg__aechb = 'UInt' + njjha__bfbf[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, ahk__dgng))
            csoag__rvvf = ahk__dgng.dtype.name
        elif ahk__dgng == datetime_date_array_type:
            veg__aechb = 'datetime'
            csoag__rvvf = 'object'
        elif isinstance(ahk__dgng, (StructArrayType, ArrayItemArrayType)):
            veg__aechb = 'object'
            csoag__rvvf = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, ahk__dgng))
        jkth__jnvau = {'name': col_name, 'field_name': col_name,
            'pandas_type': veg__aechb, 'numpy_type': csoag__rvvf,
            'metadata': lap__udets}
        tnjjl__iflbl['columns'].append(jkth__jnvau)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            nzkm__ccb = '__index_level_0__'
            yoee__caa = None
        else:
            nzkm__ccb = '%s'
            yoee__caa = '%s'
        tnjjl__iflbl['index_columns'] = [nzkm__ccb]
        tnjjl__iflbl['columns'].append({'name': yoee__caa, 'field_name':
            nzkm__ccb, 'pandas_type': index.pandas_type_name, 'numpy_type':
            index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        tnjjl__iflbl['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        tnjjl__iflbl['index_columns'] = []
    tnjjl__iflbl['pandas_version'] = pd.__version__
    return tnjjl__iflbl


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
        rzsz__opa = []
        for hzrdq__pzt in partition_cols:
            try:
                idx = df.columns.index(hzrdq__pzt)
            except ValueError as ixtp__uxp:
                raise BodoError(
                    f'Partition column {hzrdq__pzt} is not in dataframe')
            rzsz__opa.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    gragr__kje = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType
        )
    lnxq__prjjz = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not gragr__kje)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not gragr__kje or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and gragr__kje and not is_overload_true(_is_parallel)
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
        wsnn__yoz = df.runtime_data_types
        iwpi__difb = len(wsnn__yoz)
        lap__udets = gen_pandas_parquet_metadata([''] * iwpi__difb,
            wsnn__yoz, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        weuj__hzvb = lap__udets['columns'][:iwpi__difb]
        lap__udets['columns'] = lap__udets['columns'][iwpi__difb:]
        weuj__hzvb = [json.dumps(url__ogcfp).replace('""', '{0}') for
            url__ogcfp in weuj__hzvb]
        pdt__ant = json.dumps(lap__udets)
        ssrc__zetzk = '"columns": ['
        trrpu__ebd = pdt__ant.find(ssrc__zetzk)
        if trrpu__ebd == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        xjl__bjw = trrpu__ebd + len(ssrc__zetzk)
        vms__pjl = pdt__ant[:xjl__bjw]
        pdt__ant = pdt__ant[xjl__bjw:]
        dmxw__qyf = len(lap__udets['columns'])
    else:
        pdt__ant = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and gragr__kje:
        pdt__ant = pdt__ant.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            pdt__ant = pdt__ant.replace('"%s"', '%s')
    if not df.is_table_format:
        vqzuu__vgzaf = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    vxgvf__oga = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        vxgvf__oga += '    py_table = get_dataframe_table(df)\n'
        vxgvf__oga += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        vxgvf__oga += '    info_list = [{}]\n'.format(vqzuu__vgzaf)
        vxgvf__oga += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        vxgvf__oga += '    columns_index = get_dataframe_column_names(df)\n'
        vxgvf__oga += '    names_arr = index_to_array(columns_index)\n'
        vxgvf__oga += '    col_names = array_to_info(names_arr)\n'
    else:
        vxgvf__oga += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and lnxq__prjjz:
        vxgvf__oga += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        euni__wei = True
    else:
        vxgvf__oga += '    index_col = array_to_info(np.empty(0))\n'
        euni__wei = False
    if df.has_runtime_cols:
        vxgvf__oga += '    columns_lst = []\n'
        vxgvf__oga += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            vxgvf__oga += f'    for _ in range(len(py_table.block_{i})):\n'
            vxgvf__oga += f"""        columns_lst.append({weuj__hzvb[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            vxgvf__oga += '        num_cols += 1\n'
        if dmxw__qyf:
            vxgvf__oga += "    columns_lst.append('')\n"
        vxgvf__oga += '    columns_str = ", ".join(columns_lst)\n'
        vxgvf__oga += ('    metadata = """' + vms__pjl +
            '""" + columns_str + """' + pdt__ant + '"""\n')
    else:
        vxgvf__oga += '    metadata = """' + pdt__ant + '"""\n'
    vxgvf__oga += '    if compression is None:\n'
    vxgvf__oga += "        compression = 'none'\n"
    vxgvf__oga += '    if df.index.name is not None:\n'
    vxgvf__oga += '        name_ptr = df.index.name\n'
    vxgvf__oga += '    else:\n'
    vxgvf__oga += "        name_ptr = 'null'\n"
    vxgvf__oga += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    hyeo__dnjxu = None
    if partition_cols:
        hyeo__dnjxu = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        ylzbk__zgf = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in rzsz__opa)
        if ylzbk__zgf:
            vxgvf__oga += '    cat_info_list = [{}]\n'.format(ylzbk__zgf)
            vxgvf__oga += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            vxgvf__oga += '    cat_table = table\n'
        vxgvf__oga += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        vxgvf__oga += (
            f'    part_cols_idxs = np.array({rzsz__opa}, dtype=np.int32)\n')
        vxgvf__oga += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        vxgvf__oga += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        vxgvf__oga += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        vxgvf__oga += (
            '                            unicode_to_utf8(compression),\n')
        vxgvf__oga += '                            _is_parallel,\n'
        vxgvf__oga += (
            '                            unicode_to_utf8(bucket_region),\n')
        vxgvf__oga += '                            row_group_size,\n'
        vxgvf__oga += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        vxgvf__oga += '    delete_table_decref_arrays(table)\n'
        vxgvf__oga += '    delete_info_decref_array(index_col)\n'
        vxgvf__oga += '    delete_info_decref_array(col_names_no_partitions)\n'
        vxgvf__oga += '    delete_info_decref_array(col_names)\n'
        if ylzbk__zgf:
            vxgvf__oga += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        vxgvf__oga += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        vxgvf__oga += (
            '                            table, col_names, index_col,\n')
        vxgvf__oga += '                            ' + str(euni__wei) + ',\n'
        vxgvf__oga += (
            '                            unicode_to_utf8(metadata),\n')
        vxgvf__oga += (
            '                            unicode_to_utf8(compression),\n')
        vxgvf__oga += (
            '                            _is_parallel, 1, df.index.start,\n')
        vxgvf__oga += (
            '                            df.index.stop, df.index.step,\n')
        vxgvf__oga += (
            '                            unicode_to_utf8(name_ptr),\n')
        vxgvf__oga += (
            '                            unicode_to_utf8(bucket_region),\n')
        vxgvf__oga += '                            row_group_size,\n'
        vxgvf__oga += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        vxgvf__oga += '    delete_table_decref_arrays(table)\n'
        vxgvf__oga += '    delete_info_decref_array(index_col)\n'
        vxgvf__oga += '    delete_info_decref_array(col_names)\n'
    else:
        vxgvf__oga += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        vxgvf__oga += (
            '                            table, col_names, index_col,\n')
        vxgvf__oga += '                            ' + str(euni__wei) + ',\n'
        vxgvf__oga += (
            '                            unicode_to_utf8(metadata),\n')
        vxgvf__oga += (
            '                            unicode_to_utf8(compression),\n')
        vxgvf__oga += '                            _is_parallel, 0, 0, 0, 0,\n'
        vxgvf__oga += (
            '                            unicode_to_utf8(name_ptr),\n')
        vxgvf__oga += (
            '                            unicode_to_utf8(bucket_region),\n')
        vxgvf__oga += '                            row_group_size,\n'
        vxgvf__oga += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        vxgvf__oga += '    delete_table_decref_arrays(table)\n'
        vxgvf__oga += '    delete_info_decref_array(index_col)\n'
        vxgvf__oga += '    delete_info_decref_array(col_names)\n'
    rmy__pcp = {}
    if df.has_runtime_cols:
        dxneg__bwxzv = None
    else:
        for qstpt__inwl in df.columns:
            if not isinstance(qstpt__inwl, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        dxneg__bwxzv = pd.array(df.columns)
    exec(vxgvf__oga, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': dxneg__bwxzv,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': hyeo__dnjxu, 'get_dataframe_column_names':
        get_dataframe_column_names, 'fix_arr_dtype': fix_arr_dtype,
        'decode_if_dict_array': decode_if_dict_array,
        'decode_if_dict_table': decode_if_dict_table}, rmy__pcp)
    ltmp__simsr = rmy__pcp['df_to_parquet']
    return ltmp__simsr


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    kccn__aqjyd = 'all_ok'
    mvy__cadz, zvtc__pjf = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        kxda__rdg = 100
        if chunksize is None:
            nyq__aok = kxda__rdg
        else:
            nyq__aok = min(chunksize, kxda__rdg)
        if _is_table_create:
            df = df.iloc[:nyq__aok, :]
        else:
            df = df.iloc[nyq__aok:, :]
            if len(df) == 0:
                return kccn__aqjyd
    knyem__nbkg = df.columns
    try:
        if mvy__cadz == 'snowflake':
            if zvtc__pjf and con.count(zvtc__pjf) == 1:
                con = con.replace(zvtc__pjf, quote(zvtc__pjf))
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
                df.columns = [(xwip__dvn.upper() if xwip__dvn.islower() else
                    xwip__dvn) for xwip__dvn in df.columns]
            except ImportError as ixtp__uxp:
                kccn__aqjyd = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return kccn__aqjyd
        if mvy__cadz == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            pudr__webo = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            xhmf__xlxe = bodo.typeof(df)
            aqfu__ltx = {}
            for xwip__dvn, keqp__swldi in zip(xhmf__xlxe.columns,
                xhmf__xlxe.data):
                if df[xwip__dvn].dtype == 'object':
                    if keqp__swldi == datetime_date_array_type:
                        aqfu__ltx[xwip__dvn] = sa.types.Date
                    elif keqp__swldi in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not pudr__webo or 
                        pudr__webo == '0'):
                        aqfu__ltx[xwip__dvn] = VARCHAR2(4000)
            dtype = aqfu__ltx
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as mitza__nzdc:
            kccn__aqjyd = mitza__nzdc.args[0]
            if mvy__cadz == 'oracle' and 'ORA-12899' in kccn__aqjyd:
                kccn__aqjyd += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return kccn__aqjyd
    finally:
        df.columns = knyem__nbkg


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
    vxgvf__oga = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    vxgvf__oga += f"    if con.startswith('iceberg'):\n"
    vxgvf__oga += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    vxgvf__oga += f'        if schema is None:\n'
    vxgvf__oga += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    vxgvf__oga += f'        if chunksize is not None:\n'
    vxgvf__oga += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    vxgvf__oga += f'        if index and bodo.get_rank() == 0:\n'
    vxgvf__oga += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    vxgvf__oga += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    vxgvf__oga += (
        f"            warnings.warn('index_label is not supported for Iceberg tables.')\n"
        )
    if df.is_table_format:
        vxgvf__oga += f'        py_table = get_dataframe_table(df)\n'
        vxgvf__oga += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        vqzuu__vgzaf = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        vxgvf__oga += f'        info_list = [{vqzuu__vgzaf}]\n'
        vxgvf__oga += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        vxgvf__oga += (
            f'        columns_index = get_dataframe_column_names(df)\n')
        vxgvf__oga += f'        names_arr = index_to_array(columns_index)\n'
        vxgvf__oga += f'        col_names = array_to_info(names_arr)\n'
    else:
        vxgvf__oga += f'        col_names = array_to_info(col_names_arr)\n'
    vxgvf__oga += """        bodo.io.iceberg.iceberg_write(
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
    vxgvf__oga += f'        delete_table_decref_arrays(table)\n'
    vxgvf__oga += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        dxneg__bwxzv = None
    else:
        for qstpt__inwl in df.columns:
            if not isinstance(qstpt__inwl, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        dxneg__bwxzv = pd.array(df.columns)
    vxgvf__oga += f'    else:\n'
    vxgvf__oga += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    vxgvf__oga += f"        err_msg = 'unset'\n"
    vxgvf__oga += f'        if rank != 0:\n'
    vxgvf__oga += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    vxgvf__oga += f'        elif rank == 0:\n'
    vxgvf__oga += f'            err_msg = to_sql_exception_guard_encaps(\n'
    vxgvf__oga += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    vxgvf__oga += f'                          chunksize, dtype, method,\n'
    vxgvf__oga += f'                          True, _is_parallel,\n'
    vxgvf__oga += f'                      )\n'
    vxgvf__oga += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    vxgvf__oga += f"        if_exists = 'append'\n"
    vxgvf__oga += f"        if _is_parallel and err_msg == 'all_ok':\n"
    vxgvf__oga += f'            err_msg = to_sql_exception_guard_encaps(\n'
    vxgvf__oga += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    vxgvf__oga += f'                          chunksize, dtype, method,\n'
    vxgvf__oga += f'                          False, _is_parallel,\n'
    vxgvf__oga += f'                      )\n'
    vxgvf__oga += f"        if err_msg != 'all_ok':\n"
    vxgvf__oga += f"            print('err_msg=', err_msg)\n"
    vxgvf__oga += (
        f"            raise ValueError('error in to_sql() operation')\n")
    rmy__pcp = {}
    exec(vxgvf__oga, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_typ': df.
        table_type, 'col_names_arr': dxneg__bwxzv,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'delete_info_decref_array': delete_info_decref_array,
        'arr_info_list_to_table': arr_info_list_to_table, 'index_to_array':
        index_to_array, 'pyarrow_table_schema': bodo.io.iceberg.
        pyarrow_schema(df), 'to_sql_exception_guard_encaps':
        to_sql_exception_guard_encaps, 'warnings': warnings}, rmy__pcp)
    _impl = rmy__pcp['df_to_sql']
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
        ezoy__lknjp = get_overload_const_str(path_or_buf)
        if ezoy__lknjp.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        mxg__amyu = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(mxg__amyu), unicode_to_utf8(_bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(mxg__amyu), unicode_to_utf8(_bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    shk__tfj = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    rzs__bpxyp = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', shk__tfj, rzs__bpxyp,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    vxgvf__oga = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        nnd__klzdx = data.data.dtype.categories
        vxgvf__oga += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        nnd__klzdx = data.dtype.categories
        vxgvf__oga += '  data_values = data\n'
    plyp__ezv = len(nnd__klzdx)
    vxgvf__oga += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    vxgvf__oga += '  numba.parfors.parfor.init_prange()\n'
    vxgvf__oga += '  n = len(data_values)\n'
    for i in range(plyp__ezv):
        vxgvf__oga += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    vxgvf__oga += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    vxgvf__oga += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for gbw__nfanl in range(plyp__ezv):
        vxgvf__oga += '          data_arr_{}[i] = 0\n'.format(gbw__nfanl)
    vxgvf__oga += '      else:\n'
    for svr__osf in range(plyp__ezv):
        vxgvf__oga += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            svr__osf)
    vqzuu__vgzaf = ', '.join(f'data_arr_{i}' for i in range(plyp__ezv))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(nnd__klzdx[0], np.datetime64):
        nnd__klzdx = tuple(pd.Timestamp(xwip__dvn) for xwip__dvn in nnd__klzdx)
    elif isinstance(nnd__klzdx[0], np.timedelta64):
        nnd__klzdx = tuple(pd.Timedelta(xwip__dvn) for xwip__dvn in nnd__klzdx)
    return bodo.hiframes.dataframe_impl._gen_init_df(vxgvf__oga, nnd__klzdx,
        vqzuu__vgzaf, index)


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
    for efc__nwxic in pd_unsupported:
        ezcaw__vcnx = mod_name + '.' + efc__nwxic.__name__
        overload(efc__nwxic, no_unliteral=True)(create_unsupported_overload
            (ezcaw__vcnx))


def _install_dataframe_unsupported():
    for vbmx__itk in dataframe_unsupported_attrs:
        ivrde__bxjq = 'DataFrame.' + vbmx__itk
        overload_attribute(DataFrameType, vbmx__itk)(
            create_unsupported_overload(ivrde__bxjq))
    for ezcaw__vcnx in dataframe_unsupported:
        ivrde__bxjq = 'DataFrame.' + ezcaw__vcnx + '()'
        overload_method(DataFrameType, ezcaw__vcnx)(create_unsupported_overload
            (ivrde__bxjq))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
