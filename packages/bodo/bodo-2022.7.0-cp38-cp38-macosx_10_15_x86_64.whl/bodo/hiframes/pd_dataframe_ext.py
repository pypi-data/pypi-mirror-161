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
            ghn__rrfaw = f'{len(self.data)} columns of types {set(self.data)}'
            gwemu__svddu = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({ghn__rrfaw}, {self.index}, {gwemu__svddu}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
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
        return {lvmws__zxen: i for i, lvmws__zxen in enumerate(self.columns)}

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
            fswzt__nzmyp = (self.index if self.index == other.index else
                self.index.unify(typingctx, other.index))
            data = tuple(xvl__dvakf.unify(typingctx, izrc__kdoxb) if 
                xvl__dvakf != izrc__kdoxb else xvl__dvakf for xvl__dvakf,
                izrc__kdoxb in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if fswzt__nzmyp is not None and None not in data:
                return DataFrameType(data, fswzt__nzmyp, self.columns, dist,
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
        return all(xvl__dvakf.is_precise() for xvl__dvakf in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        ucfk__abuub = self.columns.index(col_name)
        sdo__uyr = tuple(list(self.data[:ucfk__abuub]) + [new_type] + list(
            self.data[ucfk__abuub + 1:]))
        return DataFrameType(sdo__uyr, self.index, self.columns, self.dist,
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
        rtxkp__bezr = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            rtxkp__bezr.append(('columns', fe_type.df_type.runtime_colname_typ)
                )
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, rtxkp__bezr)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        rtxkp__bezr = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, rtxkp__bezr)


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
        ttxv__tcsyv = 'n',
        vtr__wlxs = {'n': 5}
        ynel__elpz, ybf__dmhl = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, ttxv__tcsyv, vtr__wlxs)
        mqkyp__ayv = ybf__dmhl[0]
        if not is_overload_int(mqkyp__ayv):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        tda__gdt = df.copy()
        return tda__gdt(*ybf__dmhl).replace(pysig=ynel__elpz)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        daddg__fqsg = (df,) + args
        ttxv__tcsyv = 'df', 'method', 'min_periods'
        vtr__wlxs = {'method': 'pearson', 'min_periods': 1}
        fsd__proar = 'method',
        ynel__elpz, ybf__dmhl = bodo.utils.typing.fold_typing_args(func_name,
            daddg__fqsg, kws, ttxv__tcsyv, vtr__wlxs, fsd__proar)
        rbaeh__elh = ybf__dmhl[2]
        if not is_overload_int(rbaeh__elh):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        hpzf__iawek = []
        qeog__sjfo = []
        for lvmws__zxen, qlhb__etm in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(qlhb__etm.dtype):
                hpzf__iawek.append(lvmws__zxen)
                qeog__sjfo.append(types.Array(types.float64, 1, 'A'))
        if len(hpzf__iawek) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        qeog__sjfo = tuple(qeog__sjfo)
        hpzf__iawek = tuple(hpzf__iawek)
        index_typ = bodo.utils.typing.type_col_to_index(hpzf__iawek)
        tda__gdt = DataFrameType(qeog__sjfo, index_typ, hpzf__iawek)
        return tda__gdt(*ybf__dmhl).replace(pysig=ynel__elpz)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        deovh__rxai = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        zhae__pyrrd = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        qnpj__ahoy = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        gfwi__xyx = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        vxdk__gyob = dict(raw=zhae__pyrrd, result_type=qnpj__ahoy)
        mshe__mde = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', vxdk__gyob, mshe__mde,
            package_name='pandas', module_name='DataFrame')
        dalx__ccng = True
        if types.unliteral(deovh__rxai) == types.unicode_type:
            if not is_overload_constant_str(deovh__rxai):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            dalx__ccng = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        grgr__wyo = get_overload_const_int(axis)
        if dalx__ccng and grgr__wyo != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif grgr__wyo not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        aonzz__jcco = []
        for arr_typ in df.data:
            smnot__vjoc = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            sxaol__cpyyt = self.context.resolve_function_type(operator.
                getitem, (SeriesIlocType(smnot__vjoc), types.int64), {}
                ).return_type
            aonzz__jcco.append(sxaol__cpyyt)
        crope__rwpzn = types.none
        zqz__kkq = HeterogeneousIndexType(types.BaseTuple.from_types(tuple(
            types.literal(lvmws__zxen) for lvmws__zxen in df.columns)), None)
        zpwq__fppj = types.BaseTuple.from_types(aonzz__jcco)
        gou__wha = types.Tuple([types.bool_] * len(zpwq__fppj))
        pnh__lwile = bodo.NullableTupleType(zpwq__fppj, gou__wha)
        qwu__xwwf = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if qwu__xwwf == types.NPDatetime('ns'):
            qwu__xwwf = bodo.pd_timestamp_type
        if qwu__xwwf == types.NPTimedelta('ns'):
            qwu__xwwf = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(zpwq__fppj):
            cuyk__wtzpi = HeterogeneousSeriesType(pnh__lwile, zqz__kkq,
                qwu__xwwf)
        else:
            cuyk__wtzpi = SeriesType(zpwq__fppj.dtype, pnh__lwile, zqz__kkq,
                qwu__xwwf)
        fijh__joecd = cuyk__wtzpi,
        if gfwi__xyx is not None:
            fijh__joecd += tuple(gfwi__xyx.types)
        try:
            if not dalx__ccng:
                iyu__rbca = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(deovh__rxai), self.context,
                    'DataFrame.apply', axis if grgr__wyo == 1 else None)
            else:
                iyu__rbca = get_const_func_output_type(deovh__rxai,
                    fijh__joecd, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as ilfxw__aqk:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()', ilfxw__aqk)
                )
        if dalx__ccng:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(iyu__rbca, (SeriesType, HeterogeneousSeriesType)
                ) and iyu__rbca.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(iyu__rbca, HeterogeneousSeriesType):
                ppnsv__epi, wawuc__dci = iyu__rbca.const_info
                if isinstance(iyu__rbca.data, bodo.libs.nullable_tuple_ext.
                    NullableTupleType):
                    mievm__dzf = iyu__rbca.data.tuple_typ.types
                elif isinstance(iyu__rbca.data, types.Tuple):
                    mievm__dzf = iyu__rbca.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                xkyp__wwi = tuple(to_nullable_type(dtype_to_array_type(
                    lbin__xucmz)) for lbin__xucmz in mievm__dzf)
                pxlh__ubg = DataFrameType(xkyp__wwi, df.index, wawuc__dci)
            elif isinstance(iyu__rbca, SeriesType):
                ouhv__tjdgc, wawuc__dci = iyu__rbca.const_info
                xkyp__wwi = tuple(to_nullable_type(dtype_to_array_type(
                    iyu__rbca.dtype)) for ppnsv__epi in range(ouhv__tjdgc))
                pxlh__ubg = DataFrameType(xkyp__wwi, df.index, wawuc__dci)
            else:
                wymly__cefej = get_udf_out_arr_type(iyu__rbca)
                pxlh__ubg = SeriesType(wymly__cefej.dtype, wymly__cefej, df
                    .index, None)
        else:
            pxlh__ubg = iyu__rbca
        gtkht__zoko = ', '.join("{} = ''".format(xvl__dvakf) for xvl__dvakf in
            kws.keys())
        ekb__dremp = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {gtkht__zoko}):
"""
        ekb__dremp += '    pass\n'
        hpyaa__sal = {}
        exec(ekb__dremp, {}, hpyaa__sal)
        irw__agfji = hpyaa__sal['apply_stub']
        ynel__elpz = numba.core.utils.pysignature(irw__agfji)
        yil__ebee = (deovh__rxai, axis, zhae__pyrrd, qnpj__ahoy, gfwi__xyx
            ) + tuple(kws.values())
        return signature(pxlh__ubg, *yil__ebee).replace(pysig=ynel__elpz)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        ttxv__tcsyv = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots',
            'sharex', 'sharey', 'layout', 'use_index', 'title', 'grid',
            'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks',
            'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr',
            'xerr', 'secondary_y', 'sort_columns', 'xlabel', 'ylabel',
            'position', 'stacked', 'mark_right', 'include_bool', 'backend')
        vtr__wlxs = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        fsd__proar = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        ynel__elpz, ybf__dmhl = bodo.utils.typing.fold_typing_args(func_name,
            args, kws, ttxv__tcsyv, vtr__wlxs, fsd__proar)
        lohz__gkvzv = ybf__dmhl[2]
        if not is_overload_constant_str(lohz__gkvzv):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        pxdwu__cwp = ybf__dmhl[0]
        if not is_overload_none(pxdwu__cwp) and not (is_overload_int(
            pxdwu__cwp) or is_overload_constant_str(pxdwu__cwp)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(pxdwu__cwp):
            nzr__nwgj = get_overload_const_str(pxdwu__cwp)
            if nzr__nwgj not in df.columns:
                raise BodoError(f'{func_name}: {nzr__nwgj} column not found.')
        elif is_overload_int(pxdwu__cwp):
            wpuwd__ryuj = get_overload_const_int(pxdwu__cwp)
            if wpuwd__ryuj > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {wpuwd__ryuj} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            pxdwu__cwp = df.columns[pxdwu__cwp]
        ltkzk__wvtf = ybf__dmhl[1]
        if not is_overload_none(ltkzk__wvtf) and not (is_overload_int(
            ltkzk__wvtf) or is_overload_constant_str(ltkzk__wvtf)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(ltkzk__wvtf):
            cxrw__huh = get_overload_const_str(ltkzk__wvtf)
            if cxrw__huh not in df.columns:
                raise BodoError(f'{func_name}: {cxrw__huh} column not found.')
        elif is_overload_int(ltkzk__wvtf):
            gtm__pgj = get_overload_const_int(ltkzk__wvtf)
            if gtm__pgj > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {gtm__pgj} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            ltkzk__wvtf = df.columns[ltkzk__wvtf]
        pfxb__qsj = ybf__dmhl[3]
        if not is_overload_none(pfxb__qsj) and not is_tuple_like_type(pfxb__qsj
            ):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        jpc__drkzi = ybf__dmhl[10]
        if not is_overload_none(jpc__drkzi) and not is_overload_constant_str(
            jpc__drkzi):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        qmczj__ldfjd = ybf__dmhl[12]
        if not is_overload_bool(qmczj__ldfjd):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        opw__kqrye = ybf__dmhl[17]
        if not is_overload_none(opw__kqrye) and not is_tuple_like_type(
            opw__kqrye):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        amxjh__gfiv = ybf__dmhl[18]
        if not is_overload_none(amxjh__gfiv) and not is_tuple_like_type(
            amxjh__gfiv):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        zebr__qle = ybf__dmhl[22]
        if not is_overload_none(zebr__qle) and not is_overload_int(zebr__qle):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        cvtko__lnk = ybf__dmhl[29]
        if not is_overload_none(cvtko__lnk) and not is_overload_constant_str(
            cvtko__lnk):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        xymir__zyf = ybf__dmhl[30]
        if not is_overload_none(xymir__zyf) and not is_overload_constant_str(
            xymir__zyf):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        ihukf__plq = types.List(types.mpl_line_2d_type)
        lohz__gkvzv = get_overload_const_str(lohz__gkvzv)
        if lohz__gkvzv == 'scatter':
            if is_overload_none(pxdwu__cwp) and is_overload_none(ltkzk__wvtf):
                raise BodoError(
                    f'{func_name}: {lohz__gkvzv} requires an x and y column.')
            elif is_overload_none(pxdwu__cwp):
                raise BodoError(
                    f'{func_name}: {lohz__gkvzv} x column is missing.')
            elif is_overload_none(ltkzk__wvtf):
                raise BodoError(
                    f'{func_name}: {lohz__gkvzv} y column is missing.')
            ihukf__plq = types.mpl_path_collection_type
        elif lohz__gkvzv != 'line':
            raise BodoError(
                f'{func_name}: {lohz__gkvzv} plot is not supported.')
        return signature(ihukf__plq, *ybf__dmhl).replace(pysig=ynel__elpz)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            aopy__aeq = df.columns.index(attr)
            arr_typ = df.data[aopy__aeq]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            qpjjn__jlz = []
            sdo__uyr = []
            rag__sjkwl = False
            for i, tjnna__nrpk in enumerate(df.columns):
                if tjnna__nrpk[0] != attr:
                    continue
                rag__sjkwl = True
                qpjjn__jlz.append(tjnna__nrpk[1] if len(tjnna__nrpk) == 2 else
                    tjnna__nrpk[1:])
                sdo__uyr.append(df.data[i])
            if rag__sjkwl:
                return DataFrameType(tuple(sdo__uyr), df.index, tuple(
                    qpjjn__jlz))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        whtrf__odaq = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(whtrf__odaq)
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
        rxqt__myrhx = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], rxqt__myrhx)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    ltsul__snun = builder.module
    cnqte__vrj = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    bmowa__xywmd = cgutils.get_or_insert_function(ltsul__snun, cnqte__vrj,
        name='.dtor.df.{}'.format(df_type))
    if not bmowa__xywmd.is_declaration:
        return bmowa__xywmd
    bmowa__xywmd.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(bmowa__xywmd.append_basic_block())
    mxpem__xzpna = bmowa__xywmd.args[0]
    jwkz__ekp = context.get_value_type(payload_type).as_pointer()
    qaid__fkz = builder.bitcast(mxpem__xzpna, jwkz__ekp)
    payload = context.make_helper(builder, payload_type, ref=qaid__fkz)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        amvq__ecavf = context.get_python_api(builder)
        puz__fpfu = amvq__ecavf.gil_ensure()
        amvq__ecavf.decref(payload.parent)
        amvq__ecavf.gil_release(puz__fpfu)
    builder.ret_void()
    return bmowa__xywmd


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    lzxhp__kzfol = cgutils.create_struct_proxy(payload_type)(context, builder)
    lzxhp__kzfol.data = data_tup
    lzxhp__kzfol.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        lzxhp__kzfol.columns = colnames
    qbjmk__lpq = context.get_value_type(payload_type)
    tvprq__ulooc = context.get_abi_sizeof(qbjmk__lpq)
    tqw__smd = define_df_dtor(context, builder, df_type, payload_type)
    tqlf__wtx = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tvprq__ulooc), tqw__smd)
    xoofu__ibsb = context.nrt.meminfo_data(builder, tqlf__wtx)
    eyn__aflr = builder.bitcast(xoofu__ibsb, qbjmk__lpq.as_pointer())
    dndl__izxi = cgutils.create_struct_proxy(df_type)(context, builder)
    dndl__izxi.meminfo = tqlf__wtx
    if parent is None:
        dndl__izxi.parent = cgutils.get_null_value(dndl__izxi.parent.type)
    else:
        dndl__izxi.parent = parent
        lzxhp__kzfol.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            amvq__ecavf = context.get_python_api(builder)
            puz__fpfu = amvq__ecavf.gil_ensure()
            amvq__ecavf.incref(parent)
            amvq__ecavf.gil_release(puz__fpfu)
    builder.store(lzxhp__kzfol._getvalue(), eyn__aflr)
    return dndl__izxi._getvalue()


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
        zahg__lqsop = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype
            .arr_types)
    else:
        zahg__lqsop = [lbin__xucmz for lbin__xucmz in data_typ.dtype.arr_types]
    hbsy__mwge = DataFrameType(tuple(zahg__lqsop + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        okv__byz = construct_dataframe(context, builder, df_type, data_tup,
            index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return okv__byz
    sig = signature(hbsy__mwge, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    ouhv__tjdgc = len(data_tup_typ.types)
    if ouhv__tjdgc == 0:
        column_names = ()
    qlu__ygauw = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(qlu__ygauw, ColNamesMetaType) and isinstance(qlu__ygauw
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = qlu__ygauw.meta
    if ouhv__tjdgc == 1 and isinstance(data_tup_typ.types[0], TableType):
        ouhv__tjdgc = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == ouhv__tjdgc, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    rheek__jvwq = data_tup_typ.types
    if ouhv__tjdgc != 0 and isinstance(data_tup_typ.types[0], TableType):
        rheek__jvwq = data_tup_typ.types[0].arr_types
        is_table_format = True
    hbsy__mwge = DataFrameType(rheek__jvwq, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            qpt__jek = cgutils.create_struct_proxy(hbsy__mwge.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = qpt__jek.parent
        okv__byz = construct_dataframe(context, builder, df_type, data_tup,
            index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return okv__byz
    sig = signature(hbsy__mwge, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        dndl__izxi = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, dndl__izxi.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        lzxhp__kzfol = get_dataframe_payload(context, builder, df_typ, args[0])
        idf__amsfp = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[idf__amsfp]
        if df_typ.is_table_format:
            qpt__jek = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(lzxhp__kzfol.data, 0))
            ega__ytppu = df_typ.table_type.type_to_blk[arr_typ]
            rtn__faye = getattr(qpt__jek, f'block_{ega__ytppu}')
            ljry__qrf = ListInstance(context, builder, types.List(arr_typ),
                rtn__faye)
            pfpx__otog = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[idf__amsfp])
            rxqt__myrhx = ljry__qrf.getitem(pfpx__otog)
        else:
            rxqt__myrhx = builder.extract_value(lzxhp__kzfol.data, idf__amsfp)
        rvsws__krb = cgutils.alloca_once_value(builder, rxqt__myrhx)
        fdr__xqso = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, rvsws__krb, fdr__xqso)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    tqlf__wtx = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, tqlf__wtx)
    jwkz__ekp = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, jwkz__ekp)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    hbsy__mwge = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        hbsy__mwge = types.Tuple([TableType(df_typ.data)])
    sig = signature(hbsy__mwge, df_typ)

    def codegen(context, builder, signature, args):
        lzxhp__kzfol = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            lzxhp__kzfol.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        lzxhp__kzfol = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index,
            lzxhp__kzfol.index)
    hbsy__mwge = df_typ.index
    sig = signature(hbsy__mwge, df_typ)
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
        tda__gdt = df.data[i]
        return tda__gdt(*args)


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
        lzxhp__kzfol = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(lzxhp__kzfol.data, 0))
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
    vvbk__yrlva = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{vvbk__yrlva})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        tda__gdt = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return tda__gdt(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        lzxhp__kzfol = get_dataframe_payload(context, builder, signature.
            args[0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, lzxhp__kzfol.columns)
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
    zpwq__fppj = self.typemap[data_tup.name]
    if any(is_tuple_like_type(lbin__xucmz) for lbin__xucmz in zpwq__fppj.types
        ):
        return None
    if equiv_set.has_shape(data_tup):
        tumz__waol = equiv_set.get_shape(data_tup)
        if len(tumz__waol) > 1:
            equiv_set.insert_equiv(*tumz__waol)
        if len(tumz__waol) > 0:
            zqz__kkq = self.typemap[index.name]
            if not isinstance(zqz__kkq, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(tumz__waol[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(tumz__waol[0], len(
                tumz__waol)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    chlnm__qaf = args[0]
    data_types = self.typemap[chlnm__qaf.name].data
    if any(is_tuple_like_type(lbin__xucmz) for lbin__xucmz in data_types):
        return None
    if equiv_set.has_shape(chlnm__qaf):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            chlnm__qaf)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    chlnm__qaf = args[0]
    zqz__kkq = self.typemap[chlnm__qaf.name].index
    if isinstance(zqz__kkq, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(chlnm__qaf):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            chlnm__qaf)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    chlnm__qaf = args[0]
    if equiv_set.has_shape(chlnm__qaf):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            chlnm__qaf), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    chlnm__qaf = args[0]
    if equiv_set.has_shape(chlnm__qaf):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            chlnm__qaf)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    idf__amsfp = get_overload_const_int(c_ind_typ)
    if df_typ.data[idf__amsfp] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        fokj__ixt, ppnsv__epi, iwz__tvqc = args
        lzxhp__kzfol = get_dataframe_payload(context, builder, df_typ,
            fokj__ixt)
        if df_typ.is_table_format:
            qpt__jek = cgutils.create_struct_proxy(df_typ.table_type)(context,
                builder, builder.extract_value(lzxhp__kzfol.data, 0))
            ega__ytppu = df_typ.table_type.type_to_blk[arr_typ]
            rtn__faye = getattr(qpt__jek, f'block_{ega__ytppu}')
            ljry__qrf = ListInstance(context, builder, types.List(arr_typ),
                rtn__faye)
            pfpx__otog = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[idf__amsfp])
            ljry__qrf.setitem(pfpx__otog, iwz__tvqc, True)
        else:
            rxqt__myrhx = builder.extract_value(lzxhp__kzfol.data, idf__amsfp)
            context.nrt.decref(builder, df_typ.data[idf__amsfp], rxqt__myrhx)
            lzxhp__kzfol.data = builder.insert_value(lzxhp__kzfol.data,
                iwz__tvqc, idf__amsfp)
            context.nrt.incref(builder, arr_typ, iwz__tvqc)
        dndl__izxi = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=fokj__ixt)
        payload_type = DataFramePayloadType(df_typ)
        qaid__fkz = context.nrt.meminfo_data(builder, dndl__izxi.meminfo)
        jwkz__ekp = context.get_value_type(payload_type).as_pointer()
        qaid__fkz = builder.bitcast(qaid__fkz, jwkz__ekp)
        builder.store(lzxhp__kzfol._getvalue(), qaid__fkz)
        return impl_ret_borrowed(context, builder, df_typ, fokj__ixt)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        gegat__bwdxf = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        dlza__nry = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=gegat__bwdxf)
        vskvq__iaei = get_dataframe_payload(context, builder, df_typ,
            gegat__bwdxf)
        dndl__izxi = construct_dataframe(context, builder, signature.
            return_type, vskvq__iaei.data, index_val, dlza__nry.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), vskvq__iaei.data)
        return dndl__izxi
    hbsy__mwge = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(hbsy__mwge, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    ouhv__tjdgc = len(df_type.columns)
    tfw__xqbk = ouhv__tjdgc
    yrso__rxxj = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    jym__hckt = col_name not in df_type.columns
    idf__amsfp = ouhv__tjdgc
    if jym__hckt:
        yrso__rxxj += arr_type,
        column_names += col_name,
        tfw__xqbk += 1
    else:
        idf__amsfp = df_type.columns.index(col_name)
        yrso__rxxj = tuple(arr_type if i == idf__amsfp else yrso__rxxj[i] for
            i in range(ouhv__tjdgc))

    def codegen(context, builder, signature, args):
        fokj__ixt, ppnsv__epi, iwz__tvqc = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, fokj__ixt)
        heuhy__pca = cgutils.create_struct_proxy(df_type)(context, builder,
            value=fokj__ixt)
        if df_type.is_table_format:
            muxik__ormao = df_type.table_type
            zni__afov = builder.extract_value(in_dataframe_payload.data, 0)
            pcpn__xwu = TableType(yrso__rxxj)
            grbk__awi = set_table_data_codegen(context, builder,
                muxik__ormao, zni__afov, pcpn__xwu, arr_type, iwz__tvqc,
                idf__amsfp, jym__hckt)
            data_tup = context.make_tuple(builder, types.Tuple([pcpn__xwu]),
                [grbk__awi])
        else:
            rheek__jvwq = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != idf__amsfp else iwz__tvqc) for i in range(
                ouhv__tjdgc)]
            if jym__hckt:
                rheek__jvwq.append(iwz__tvqc)
            for chlnm__qaf, tuan__ihy in zip(rheek__jvwq, yrso__rxxj):
                context.nrt.incref(builder, tuan__ihy, chlnm__qaf)
            data_tup = context.make_tuple(builder, types.Tuple(yrso__rxxj),
                rheek__jvwq)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        knuu__xoes = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, heuhy__pca.parent, None)
        if not jym__hckt and arr_type == df_type.data[idf__amsfp]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            qaid__fkz = context.nrt.meminfo_data(builder, heuhy__pca.meminfo)
            jwkz__ekp = context.get_value_type(payload_type).as_pointer()
            qaid__fkz = builder.bitcast(qaid__fkz, jwkz__ekp)
            jzy__czc = get_dataframe_payload(context, builder, df_type,
                knuu__xoes)
            builder.store(jzy__czc._getvalue(), qaid__fkz)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, pcpn__xwu, builder.
                    extract_value(data_tup, 0))
            else:
                for chlnm__qaf, tuan__ihy in zip(rheek__jvwq, yrso__rxxj):
                    context.nrt.incref(builder, tuan__ihy, chlnm__qaf)
        has_parent = cgutils.is_not_null(builder, heuhy__pca.parent)
        with builder.if_then(has_parent):
            amvq__ecavf = context.get_python_api(builder)
            puz__fpfu = amvq__ecavf.gil_ensure()
            cuoo__zqm = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, iwz__tvqc)
            lvmws__zxen = numba.core.pythonapi._BoxContext(context, builder,
                amvq__ecavf, cuoo__zqm)
            eerch__ayuo = lvmws__zxen.pyapi.from_native_value(arr_type,
                iwz__tvqc, lvmws__zxen.env_manager)
            if isinstance(col_name, str):
                wna__eos = context.insert_const_string(builder.module, col_name
                    )
                zrxn__breom = amvq__ecavf.string_from_string(wna__eos)
            else:
                assert isinstance(col_name, int)
                zrxn__breom = amvq__ecavf.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            amvq__ecavf.object_setitem(heuhy__pca.parent, zrxn__breom,
                eerch__ayuo)
            amvq__ecavf.decref(eerch__ayuo)
            amvq__ecavf.decref(zrxn__breom)
            amvq__ecavf.gil_release(puz__fpfu)
        return knuu__xoes
    hbsy__mwge = DataFrameType(yrso__rxxj, index_typ, column_names, df_type
        .dist, df_type.is_table_format)
    sig = signature(hbsy__mwge, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    ouhv__tjdgc = len(pyval.columns)
    rheek__jvwq = []
    for i in range(ouhv__tjdgc):
        qucmq__jws = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            eerch__ayuo = qucmq__jws.array
        else:
            eerch__ayuo = qucmq__jws.values
        rheek__jvwq.append(eerch__ayuo)
    rheek__jvwq = tuple(rheek__jvwq)
    if df_type.is_table_format:
        qpt__jek = context.get_constant_generic(builder, df_type.table_type,
            Table(rheek__jvwq))
        data_tup = lir.Constant.literal_struct([qpt__jek])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], tjnna__nrpk) for
            i, tjnna__nrpk in enumerate(rheek__jvwq)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    xiv__aoo = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, xiv__aoo])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    wuw__mmnrx = context.get_constant(types.int64, -1)
    svy__djwha = context.get_constant_null(types.voidptr)
    tqlf__wtx = lir.Constant.literal_struct([wuw__mmnrx, svy__djwha,
        svy__djwha, payload, wuw__mmnrx])
    tqlf__wtx = cgutils.global_constant(builder, '.const.meminfo', tqlf__wtx
        ).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([tqlf__wtx, xiv__aoo])


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
        fswzt__nzmyp = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        fswzt__nzmyp = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, fswzt__nzmyp)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        sdo__uyr = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                sdo__uyr)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), sdo__uyr)
    elif not fromty.is_table_format and toty.is_table_format:
        sdo__uyr = _cast_df_data_to_table_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        sdo__uyr = _cast_df_data_to_tuple_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        sdo__uyr = _cast_df_data_keep_table_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    else:
        sdo__uyr = _cast_df_data_keep_tuple_format(context, builder, fromty,
            toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, sdo__uyr,
        fswzt__nzmyp, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    lzvx__aqepu = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        hnlln__btm = get_index_data_arr_types(toty.index)[0]
        qvs__juxwn = bodo.utils.transform.get_type_alloc_counts(hnlln__btm) - 1
        rmyuz__urbus = ', '.join('0' for ppnsv__epi in range(qvs__juxwn))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(rmyuz__urbus, ', ' if qvs__juxwn == 1 else ''))
        lzvx__aqepu['index_arr_type'] = hnlln__btm
    hdpco__ijt = []
    for i, arr_typ in enumerate(toty.data):
        qvs__juxwn = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        rmyuz__urbus = ', '.join('0' for ppnsv__epi in range(qvs__juxwn))
        twmdg__zkoat = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'
            .format(i, rmyuz__urbus, ', ' if qvs__juxwn == 1 else ''))
        hdpco__ijt.append(twmdg__zkoat)
        lzvx__aqepu[f'arr_type{i}'] = arr_typ
    hdpco__ijt = ', '.join(hdpco__ijt)
    ekb__dremp = 'def impl():\n'
    ainv__mbg = bodo.hiframes.dataframe_impl._gen_init_df(ekb__dremp, toty.
        columns, hdpco__ijt, index, lzvx__aqepu)
    df = context.compile_internal(builder, ainv__mbg, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    kmyl__mrg = toty.table_type
    qpt__jek = cgutils.create_struct_proxy(kmyl__mrg)(context, builder)
    qpt__jek.parent = in_dataframe_payload.parent
    for lbin__xucmz, ega__ytppu in kmyl__mrg.type_to_blk.items():
        nbsae__vgb = context.get_constant(types.int64, len(kmyl__mrg.
            block_to_arr_ind[ega__ytppu]))
        ppnsv__epi, npwdz__rgwe = ListInstance.allocate_ex(context, builder,
            types.List(lbin__xucmz), nbsae__vgb)
        npwdz__rgwe.size = nbsae__vgb
        setattr(qpt__jek, f'block_{ega__ytppu}', npwdz__rgwe.value)
    for i, lbin__xucmz in enumerate(fromty.data):
        dlnrw__dlpm = toty.data[i]
        if lbin__xucmz != dlnrw__dlpm:
            sxw__wiiv = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*sxw__wiiv)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        rxqt__myrhx = builder.extract_value(in_dataframe_payload.data, i)
        if lbin__xucmz != dlnrw__dlpm:
            llr__tiqph = context.cast(builder, rxqt__myrhx, lbin__xucmz,
                dlnrw__dlpm)
            axyys__uhjl = False
        else:
            llr__tiqph = rxqt__myrhx
            axyys__uhjl = True
        ega__ytppu = kmyl__mrg.type_to_blk[lbin__xucmz]
        rtn__faye = getattr(qpt__jek, f'block_{ega__ytppu}')
        ljry__qrf = ListInstance(context, builder, types.List(lbin__xucmz),
            rtn__faye)
        pfpx__otog = context.get_constant(types.int64, kmyl__mrg.
            block_offsets[i])
        ljry__qrf.setitem(pfpx__otog, llr__tiqph, axyys__uhjl)
    data_tup = context.make_tuple(builder, types.Tuple([kmyl__mrg]), [
        qpt__jek._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    rheek__jvwq = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            sxw__wiiv = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*sxw__wiiv)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            rxqt__myrhx = builder.extract_value(in_dataframe_payload.data, i)
            llr__tiqph = context.cast(builder, rxqt__myrhx, fromty.data[i],
                toty.data[i])
            axyys__uhjl = False
        else:
            llr__tiqph = builder.extract_value(in_dataframe_payload.data, i)
            axyys__uhjl = True
        if axyys__uhjl:
            context.nrt.incref(builder, toty.data[i], llr__tiqph)
        rheek__jvwq.append(llr__tiqph)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), rheek__jvwq)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    muxik__ormao = fromty.table_type
    zni__afov = cgutils.create_struct_proxy(muxik__ormao)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    pcpn__xwu = toty.table_type
    grbk__awi = cgutils.create_struct_proxy(pcpn__xwu)(context, builder)
    grbk__awi.parent = in_dataframe_payload.parent
    for lbin__xucmz, ega__ytppu in pcpn__xwu.type_to_blk.items():
        nbsae__vgb = context.get_constant(types.int64, len(pcpn__xwu.
            block_to_arr_ind[ega__ytppu]))
        ppnsv__epi, npwdz__rgwe = ListInstance.allocate_ex(context, builder,
            types.List(lbin__xucmz), nbsae__vgb)
        npwdz__rgwe.size = nbsae__vgb
        setattr(grbk__awi, f'block_{ega__ytppu}', npwdz__rgwe.value)
    for i in range(len(fromty.data)):
        eetq__zewkp = fromty.data[i]
        dlnrw__dlpm = toty.data[i]
        if eetq__zewkp != dlnrw__dlpm:
            sxw__wiiv = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*sxw__wiiv)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        xzl__fawrq = muxik__ormao.type_to_blk[eetq__zewkp]
        nbzjd__dvu = getattr(zni__afov, f'block_{xzl__fawrq}')
        tpn__uztqy = ListInstance(context, builder, types.List(eetq__zewkp),
            nbzjd__dvu)
        oaqz__ele = context.get_constant(types.int64, muxik__ormao.
            block_offsets[i])
        rxqt__myrhx = tpn__uztqy.getitem(oaqz__ele)
        if eetq__zewkp != dlnrw__dlpm:
            llr__tiqph = context.cast(builder, rxqt__myrhx, eetq__zewkp,
                dlnrw__dlpm)
            axyys__uhjl = False
        else:
            llr__tiqph = rxqt__myrhx
            axyys__uhjl = True
        omxes__kwtf = pcpn__xwu.type_to_blk[lbin__xucmz]
        npwdz__rgwe = getattr(grbk__awi, f'block_{omxes__kwtf}')
        udh__hestq = ListInstance(context, builder, types.List(dlnrw__dlpm),
            npwdz__rgwe)
        cchpm__fhuuz = context.get_constant(types.int64, pcpn__xwu.
            block_offsets[i])
        udh__hestq.setitem(cchpm__fhuuz, llr__tiqph, axyys__uhjl)
    data_tup = context.make_tuple(builder, types.Tuple([pcpn__xwu]), [
        grbk__awi._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    kmyl__mrg = fromty.table_type
    qpt__jek = cgutils.create_struct_proxy(kmyl__mrg)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    rheek__jvwq = []
    for i, lbin__xucmz in enumerate(toty.data):
        eetq__zewkp = fromty.data[i]
        if lbin__xucmz != eetq__zewkp:
            sxw__wiiv = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*sxw__wiiv)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        ega__ytppu = kmyl__mrg.type_to_blk[lbin__xucmz]
        rtn__faye = getattr(qpt__jek, f'block_{ega__ytppu}')
        ljry__qrf = ListInstance(context, builder, types.List(lbin__xucmz),
            rtn__faye)
        pfpx__otog = context.get_constant(types.int64, kmyl__mrg.
            block_offsets[i])
        rxqt__myrhx = ljry__qrf.getitem(pfpx__otog)
        if lbin__xucmz != eetq__zewkp:
            llr__tiqph = context.cast(builder, rxqt__myrhx, eetq__zewkp,
                lbin__xucmz)
            axyys__uhjl = False
        else:
            llr__tiqph = rxqt__myrhx
            axyys__uhjl = True
        if axyys__uhjl:
            context.nrt.incref(builder, lbin__xucmz, llr__tiqph)
        rheek__jvwq.append(llr__tiqph)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), rheek__jvwq)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    hqn__jkl, hdpco__ijt, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    anuh__hio = ColNamesMetaType(tuple(hqn__jkl))
    ekb__dremp = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    ekb__dremp += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(hdpco__ijt, index_arg))
    hpyaa__sal = {}
    exec(ekb__dremp, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': anuh__hio}, hpyaa__sal)
    hxul__cpwrh = hpyaa__sal['_init_df']
    return hxul__cpwrh


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    hbsy__mwge = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(hbsy__mwge, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    hbsy__mwge = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(hbsy__mwge, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    pxja__fedip = ''
    if not is_overload_none(dtype):
        pxja__fedip = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        ouhv__tjdgc = (len(data.types) - 1) // 2
        ixe__vkeg = [lbin__xucmz.literal_value for lbin__xucmz in data.
            types[1:ouhv__tjdgc + 1]]
        data_val_types = dict(zip(ixe__vkeg, data.types[ouhv__tjdgc + 1:]))
        rheek__jvwq = ['data[{}]'.format(i) for i in range(ouhv__tjdgc + 1,
            2 * ouhv__tjdgc + 1)]
        data_dict = dict(zip(ixe__vkeg, rheek__jvwq))
        if is_overload_none(index):
            for i, lbin__xucmz in enumerate(data.types[ouhv__tjdgc + 1:]):
                if isinstance(lbin__xucmz, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(ouhv__tjdgc + 1 + i))
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
        ylluc__erm = '.copy()' if copy else ''
        orlx__cjxic = get_overload_const_list(columns)
        ouhv__tjdgc = len(orlx__cjxic)
        data_val_types = {lvmws__zxen: data.copy(ndim=1) for lvmws__zxen in
            orlx__cjxic}
        rheek__jvwq = ['data[:,{}]{}'.format(i, ylluc__erm) for i in range(
            ouhv__tjdgc)]
        data_dict = dict(zip(orlx__cjxic, rheek__jvwq))
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
    hdpco__ijt = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[lvmws__zxen], df_len, pxja__fedip) for
        lvmws__zxen in col_names))
    if len(col_names) == 0:
        hdpco__ijt = '()'
    return col_names, hdpco__ijt, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for lvmws__zxen in col_names:
        if lvmws__zxen in data_dict and is_iterable_type(data_val_types[
            lvmws__zxen]):
            df_len = 'len({})'.format(data_dict[lvmws__zxen])
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
    if all(lvmws__zxen in data_dict for lvmws__zxen in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    wae__nor = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len,
        dtype)
    for lvmws__zxen in col_names:
        if lvmws__zxen not in data_dict:
            data_dict[lvmws__zxen] = wae__nor


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
            lbin__xucmz = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df
                )
            return len(lbin__xucmz)
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
        ptrv__fwzxa = idx.literal_value
        if isinstance(ptrv__fwzxa, int):
            tda__gdt = tup.types[ptrv__fwzxa]
        elif isinstance(ptrv__fwzxa, slice):
            tda__gdt = types.BaseTuple.from_types(tup.types[ptrv__fwzxa])
        return signature(tda__gdt, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    mvxjc__ema, idx = sig.args
    idx = idx.literal_value
    tup, ppnsv__epi = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(mvxjc__ema)
        if not 0 <= idx < len(mvxjc__ema):
            raise IndexError('cannot index at %d in %s' % (idx, mvxjc__ema))
        zow__ntn = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        pard__guv = cgutils.unpack_tuple(builder, tup)[idx]
        zow__ntn = context.make_tuple(builder, sig.return_type, pard__guv)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, zow__ntn)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, dejbg__ynyt, suffix_x,
            suffix_y, is_join, indicator, ppnsv__epi, ppnsv__epi) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        zmkiz__xnx = {lvmws__zxen: i for i, lvmws__zxen in enumerate(left_on)}
        tzraj__iomr = {lvmws__zxen: i for i, lvmws__zxen in enumerate(right_on)
            }
        glpq__apcc = set(left_on) & set(right_on)
        hhn__bmv = set(left_df.columns) & set(right_df.columns)
        ucw__wfn = hhn__bmv - glpq__apcc
        koddp__tlzrk = '$_bodo_index_' in left_on
        mpuf__ghihk = '$_bodo_index_' in right_on
        how = get_overload_const_str(dejbg__ynyt)
        mxq__lfdx = how in {'left', 'outer'}
        xuhga__gue = how in {'right', 'outer'}
        columns = []
        data = []
        if koddp__tlzrk:
            ywv__pbrug = bodo.utils.typing.get_index_data_arr_types(left_df
                .index)[0]
        else:
            ywv__pbrug = left_df.data[left_df.column_index[left_on[0]]]
        if mpuf__ghihk:
            jocyc__zeud = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            jocyc__zeud = right_df.data[right_df.column_index[right_on[0]]]
        if koddp__tlzrk and not mpuf__ghihk and not is_join.literal_value:
            zrdvc__gprn = right_on[0]
            if zrdvc__gprn in left_df.column_index:
                columns.append(zrdvc__gprn)
                if (jocyc__zeud == bodo.dict_str_arr_type and ywv__pbrug ==
                    bodo.string_array_type):
                    izd__bhsac = bodo.string_array_type
                else:
                    izd__bhsac = jocyc__zeud
                data.append(izd__bhsac)
        if mpuf__ghihk and not koddp__tlzrk and not is_join.literal_value:
            luudw__wavgl = left_on[0]
            if luudw__wavgl in right_df.column_index:
                columns.append(luudw__wavgl)
                if (ywv__pbrug == bodo.dict_str_arr_type and jocyc__zeud ==
                    bodo.string_array_type):
                    izd__bhsac = bodo.string_array_type
                else:
                    izd__bhsac = ywv__pbrug
                data.append(izd__bhsac)
        for eetq__zewkp, qucmq__jws in zip(left_df.data, left_df.columns):
            columns.append(str(qucmq__jws) + suffix_x.literal_value if 
                qucmq__jws in ucw__wfn else qucmq__jws)
            if qucmq__jws in glpq__apcc:
                if eetq__zewkp == bodo.dict_str_arr_type:
                    eetq__zewkp = right_df.data[right_df.column_index[
                        qucmq__jws]]
                data.append(eetq__zewkp)
            else:
                if (eetq__zewkp == bodo.dict_str_arr_type and qucmq__jws in
                    zmkiz__xnx):
                    if mpuf__ghihk:
                        eetq__zewkp = jocyc__zeud
                    else:
                        rhs__pwyes = zmkiz__xnx[qucmq__jws]
                        nbpgr__ykwkx = right_on[rhs__pwyes]
                        eetq__zewkp = right_df.data[right_df.column_index[
                            nbpgr__ykwkx]]
                if xuhga__gue:
                    eetq__zewkp = to_nullable_type(eetq__zewkp)
                data.append(eetq__zewkp)
        for eetq__zewkp, qucmq__jws in zip(right_df.data, right_df.columns):
            if qucmq__jws not in glpq__apcc:
                columns.append(str(qucmq__jws) + suffix_y.literal_value if 
                    qucmq__jws in ucw__wfn else qucmq__jws)
                if (eetq__zewkp == bodo.dict_str_arr_type and qucmq__jws in
                    tzraj__iomr):
                    if koddp__tlzrk:
                        eetq__zewkp = ywv__pbrug
                    else:
                        rhs__pwyes = tzraj__iomr[qucmq__jws]
                        fzkrd__pkzsx = left_on[rhs__pwyes]
                        eetq__zewkp = left_df.data[left_df.column_index[
                            fzkrd__pkzsx]]
                if mxq__lfdx:
                    eetq__zewkp = to_nullable_type(eetq__zewkp)
                data.append(eetq__zewkp)
        kvha__ipa = get_overload_const_bool(indicator)
        if kvha__ipa:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        qct__cfowj = False
        if koddp__tlzrk and mpuf__ghihk and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            qct__cfowj = True
        elif koddp__tlzrk and not mpuf__ghihk:
            index_typ = right_df.index
            qct__cfowj = True
        elif mpuf__ghihk and not koddp__tlzrk:
            index_typ = left_df.index
            qct__cfowj = True
        if qct__cfowj and isinstance(index_typ, bodo.hiframes.pd_index_ext.
            RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        eds__tfe = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(eds__tfe, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    dndl__izxi = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return dndl__izxi._getvalue()


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
    vxdk__gyob = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    vtr__wlxs = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', vxdk__gyob, vtr__wlxs,
        package_name='pandas', module_name='General')
    ekb__dremp = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        bta__bnw = 0
        hdpco__ijt = []
        names = []
        for i, aedb__gujw in enumerate(objs.types):
            assert isinstance(aedb__gujw, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(aedb__gujw, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                aedb__gujw, 'pandas.concat()')
            if isinstance(aedb__gujw, SeriesType):
                names.append(str(bta__bnw))
                bta__bnw += 1
                hdpco__ijt.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(aedb__gujw.columns)
                for qqs__xqqn in range(len(aedb__gujw.data)):
                    hdpco__ijt.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, qqs__xqqn))
        return bodo.hiframes.dataframe_impl._gen_init_df(ekb__dremp, names,
            ', '.join(hdpco__ijt), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(lbin__xucmz, DataFrameType) for lbin__xucmz in
            objs.types)
        rmtv__dfnml = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            rmtv__dfnml.extend(df.columns)
        rmtv__dfnml = list(dict.fromkeys(rmtv__dfnml).keys())
        zahg__lqsop = {}
        for bta__bnw, lvmws__zxen in enumerate(rmtv__dfnml):
            for i, df in enumerate(objs.types):
                if lvmws__zxen in df.column_index:
                    zahg__lqsop[f'arr_typ{bta__bnw}'] = df.data[df.
                        column_index[lvmws__zxen]]
                    break
        assert len(zahg__lqsop) == len(rmtv__dfnml)
        wergu__jpvgl = []
        for bta__bnw, lvmws__zxen in enumerate(rmtv__dfnml):
            args = []
            for i, df in enumerate(objs.types):
                if lvmws__zxen in df.column_index:
                    idf__amsfp = df.column_index[lvmws__zxen]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, idf__amsfp))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, bta__bnw))
            ekb__dremp += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(bta__bnw, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(ekb__dremp,
            rmtv__dfnml, ', '.join('A{}'.format(i) for i in range(len(
            rmtv__dfnml))), index, zahg__lqsop)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(lbin__xucmz, SeriesType) for lbin__xucmz in
            objs.types)
        ekb__dremp += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            ekb__dremp += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            ekb__dremp += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        ekb__dremp += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        hpyaa__sal = {}
        exec(ekb__dremp, {'bodo': bodo, 'np': np, 'numba': numba}, hpyaa__sal)
        return hpyaa__sal['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for bta__bnw, lvmws__zxen in enumerate(df_type.columns):
            ekb__dremp += '  arrs{} = []\n'.format(bta__bnw)
            ekb__dremp += '  for i in range(len(objs)):\n'
            ekb__dremp += '    df = objs[i]\n'
            ekb__dremp += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(bta__bnw))
            ekb__dremp += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(bta__bnw))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            ekb__dremp += '  arrs_index = []\n'
            ekb__dremp += '  for i in range(len(objs)):\n'
            ekb__dremp += '    df = objs[i]\n'
            ekb__dremp += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(ekb__dremp,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        ekb__dremp += '  arrs = []\n'
        ekb__dremp += '  for i in range(len(objs)):\n'
        ekb__dremp += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        ekb__dremp += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            ekb__dremp += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            ekb__dremp += '  arrs_index = []\n'
            ekb__dremp += '  for i in range(len(objs)):\n'
            ekb__dremp += '    S = objs[i]\n'
            ekb__dremp += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            ekb__dremp += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        ekb__dremp += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        hpyaa__sal = {}
        exec(ekb__dremp, {'bodo': bodo, 'np': np, 'numba': numba}, hpyaa__sal)
        return hpyaa__sal['impl']
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
        hbsy__mwge = df.copy(index=index)
        return signature(hbsy__mwge, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    urqau__xorh = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return urqau__xorh._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    vxdk__gyob = dict(index=index, name=name)
    vtr__wlxs = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', vxdk__gyob, vtr__wlxs,
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
        zahg__lqsop = (types.Array(types.int64, 1, 'C'),) + df.data
        kdek__xkki = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(
            columns, zahg__lqsop)
        return signature(kdek__xkki, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    urqau__xorh = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return urqau__xorh._getvalue()


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
    urqau__xorh = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return urqau__xorh._getvalue()


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
    urqau__xorh = cgutils.create_struct_proxy(sig.return_type)(context, builder
        )
    return urqau__xorh._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    mdg__efy = get_overload_const_bool(check_duplicates)
    skaa__soc = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    vzxpb__tdwq = len(value_names) > 1
    idg__ghiuy = None
    wjis__yoy = None
    ghhh__lnml = None
    ylop__mipi = None
    kovr__ybhx = isinstance(values_tup, types.UniTuple)
    if kovr__ybhx:
        psfkg__yru = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        psfkg__yru = [to_str_arr_if_dict_array(to_nullable_type(tuan__ihy)) for
            tuan__ihy in values_tup]
    ekb__dremp = 'def impl(\n'
    ekb__dremp += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, _constant_pivot_values=None, parallel=False
"""
    ekb__dremp += '):\n'
    ekb__dremp += '    if parallel:\n'
    btxs__uyk = ', '.join([f'array_to_info(index_tup[{i}])' for i in range(
        len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    ekb__dremp += f'        info_list = [{btxs__uyk}]\n'
    ekb__dremp += '        cpp_table = arr_info_list_to_table(info_list)\n'
    ekb__dremp += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
    xlode__hpzu = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    byhn__syqfu = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    ulw__zppur = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    ekb__dremp += f'        index_tup = ({xlode__hpzu},)\n'
    ekb__dremp += f'        columns_tup = ({byhn__syqfu},)\n'
    ekb__dremp += f'        values_tup = ({ulw__zppur},)\n'
    ekb__dremp += '        delete_table(cpp_table)\n'
    ekb__dremp += '        delete_table(out_cpp_table)\n'
    ekb__dremp += '    columns_arr = columns_tup[0]\n'
    if kovr__ybhx:
        ekb__dremp += '    values_arrs = [arr for arr in values_tup]\n'
    qmwj__basxo = ', '.join([
        f'bodo.utils.typing.decode_if_dict_array(index_tup[{i}])' for i in
        range(len(index_tup))])
    ekb__dremp += f'    new_index_tup = ({qmwj__basxo},)\n'
    ekb__dremp += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    ekb__dremp += '        new_index_tup\n'
    ekb__dremp += '    )\n'
    ekb__dremp += '    n_rows = len(unique_index_arr_tup[0])\n'
    ekb__dremp += '    num_values_arrays = len(values_tup)\n'
    ekb__dremp += '    n_unique_pivots = len(pivot_values)\n'
    if kovr__ybhx:
        ekb__dremp += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        ekb__dremp += '    n_cols = n_unique_pivots\n'
    ekb__dremp += '    col_map = {}\n'
    ekb__dremp += '    for i in range(n_unique_pivots):\n'
    ekb__dremp += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    ekb__dremp += '            raise ValueError(\n'
    ekb__dremp += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    ekb__dremp += '            )\n'
    ekb__dremp += '        col_map[pivot_values[i]] = i\n'
    qsmro__ezp = False
    for i, bzdz__izfk in enumerate(psfkg__yru):
        if is_str_arr_type(bzdz__izfk):
            qsmro__ezp = True
            ekb__dremp += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            ekb__dremp += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if qsmro__ezp:
        if mdg__efy:
            ekb__dremp += '    nbytes = (n_rows + 7) >> 3\n'
            ekb__dremp += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        ekb__dremp += '    for i in range(len(columns_arr)):\n'
        ekb__dremp += '        col_name = columns_arr[i]\n'
        ekb__dremp += '        pivot_idx = col_map[col_name]\n'
        ekb__dremp += '        row_idx = row_vector[i]\n'
        if mdg__efy:
            ekb__dremp += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            ekb__dremp += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            ekb__dremp += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            ekb__dremp += '        else:\n'
            ekb__dremp += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if kovr__ybhx:
            ekb__dremp += '        for j in range(num_values_arrays):\n'
            ekb__dremp += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            ekb__dremp += '            len_arr = len_arrs_0[col_idx]\n'
            ekb__dremp += '            values_arr = values_arrs[j]\n'
            ekb__dremp += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            ekb__dremp += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            ekb__dremp += '                len_arr[row_idx] = str_val_len\n'
            ekb__dremp += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, bzdz__izfk in enumerate(psfkg__yru):
                if is_str_arr_type(bzdz__izfk):
                    ekb__dremp += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    ekb__dremp += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    ekb__dremp += f"""            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}
"""
                    ekb__dremp += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    for i, bzdz__izfk in enumerate(psfkg__yru):
        if is_str_arr_type(bzdz__izfk):
            ekb__dremp += f'    data_arrs_{i} = [\n'
            ekb__dremp += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            ekb__dremp += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            ekb__dremp += '        )\n'
            ekb__dremp += '        for i in range(n_cols)\n'
            ekb__dremp += '    ]\n'
        else:
            ekb__dremp += f'    data_arrs_{i} = [\n'
            ekb__dremp += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            ekb__dremp += '        for _ in range(n_cols)\n'
            ekb__dremp += '    ]\n'
    if not qsmro__ezp and mdg__efy:
        ekb__dremp += '    nbytes = (n_rows + 7) >> 3\n'
        ekb__dremp += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    ekb__dremp += '    for i in range(len(columns_arr)):\n'
    ekb__dremp += '        col_name = columns_arr[i]\n'
    ekb__dremp += '        pivot_idx = col_map[col_name]\n'
    ekb__dremp += '        row_idx = row_vector[i]\n'
    if not qsmro__ezp and mdg__efy:
        ekb__dremp += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        ekb__dremp += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        ekb__dremp += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        ekb__dremp += '        else:\n'
        ekb__dremp += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if kovr__ybhx:
        ekb__dremp += '        for j in range(num_values_arrays):\n'
        ekb__dremp += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        ekb__dremp += '            col_arr = data_arrs_0[col_idx]\n'
        ekb__dremp += '            values_arr = values_arrs[j]\n'
        ekb__dremp += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        ekb__dremp += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        ekb__dremp += '            else:\n'
        ekb__dremp += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, bzdz__izfk in enumerate(psfkg__yru):
            ekb__dremp += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            ekb__dremp += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            ekb__dremp += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            ekb__dremp += f'        else:\n'
            ekb__dremp += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        ekb__dremp += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        idg__ghiuy = index_names.meta[0]
    else:
        ekb__dremp += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        idg__ghiuy = tuple(index_names.meta)
    if not skaa__soc:
        ghhh__lnml = columns_name.meta[0]
        if vzxpb__tdwq:
            ekb__dremp += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            wjis__yoy = value_names.meta
            if all(isinstance(lvmws__zxen, str) for lvmws__zxen in wjis__yoy):
                wjis__yoy = pd.array(wjis__yoy, 'string')
            elif all(isinstance(lvmws__zxen, int) for lvmws__zxen in wjis__yoy
                ):
                wjis__yoy = np.array(wjis__yoy, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(wjis__yoy.dtype, pd.StringDtype):
                ekb__dremp += '    total_chars = 0\n'
                ekb__dremp += f'    for i in range({len(value_names)}):\n'
                ekb__dremp += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                ekb__dremp += '        total_chars += value_name_str_len\n'
                ekb__dremp += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                ekb__dremp += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                ekb__dremp += '    total_chars = 0\n'
                ekb__dremp += '    for i in range(len(pivot_values)):\n'
                ekb__dremp += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                ekb__dremp += '        total_chars += pivot_val_str_len\n'
                ekb__dremp += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                ekb__dremp += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            ekb__dremp += f'    for i in range({len(value_names)}):\n'
            ekb__dremp += '        for j in range(len(pivot_values)):\n'
            ekb__dremp += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            ekb__dremp += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            ekb__dremp += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            ekb__dremp += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    kmyl__mrg = None
    if skaa__soc:
        if vzxpb__tdwq:
            noqp__lxgve = []
            for mgss__mjsj in _constant_pivot_values.meta:
                for mjht__dit in value_names.meta:
                    noqp__lxgve.append((mgss__mjsj, mjht__dit))
            column_names = tuple(noqp__lxgve)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        ylop__mipi = ColNamesMetaType(column_names)
        wfopu__mbzd = []
        for tuan__ihy in psfkg__yru:
            wfopu__mbzd.extend([tuan__ihy] * len(_constant_pivot_values))
        hbjm__uyown = tuple(wfopu__mbzd)
        kmyl__mrg = TableType(hbjm__uyown)
        ekb__dremp += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        ekb__dremp += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, tuan__ihy in enumerate(psfkg__yru):
            ekb__dremp += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {kmyl__mrg.type_to_blk[tuan__ihy]})
"""
        ekb__dremp += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        ekb__dremp += '        (table,), index, columns_typ\n'
        ekb__dremp += '    )\n'
    else:
        ofu__xoe = ', '.join(f'data_arrs_{i}' for i in range(len(psfkg__yru)))
        ekb__dremp += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({ofu__xoe},), n_rows)
"""
        ekb__dremp += (
            '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        ekb__dremp += '        (table,), index, column_index\n'
        ekb__dremp += '    )\n'
    hpyaa__sal = {}
    quk__mneg = {f'data_arr_typ_{i}': bzdz__izfk for i, bzdz__izfk in
        enumerate(psfkg__yru)}
    ntrn__fop = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        kmyl__mrg, 'columns_typ': ylop__mipi, 'index_names_lit': idg__ghiuy,
        'value_names_lit': wjis__yoy, 'columns_name_lit': ghhh__lnml, **
        quk__mneg}
    exec(ekb__dremp, ntrn__fop, hpyaa__sal)
    impl = hpyaa__sal['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    ztj__jforu = {}
    ztj__jforu['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, fejzv__wrigs in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        jxcm__byumx = None
        if isinstance(fejzv__wrigs, bodo.DatetimeArrayType):
            tpy__yhn = 'datetimetz'
            kvt__mutw = 'datetime64[ns]'
            if isinstance(fejzv__wrigs.tz, int):
                fkmuh__lddq = (bodo.libs.pd_datetime_arr_ext.
                    nanoseconds_to_offset(fejzv__wrigs.tz))
            else:
                fkmuh__lddq = pd.DatetimeTZDtype(tz=fejzv__wrigs.tz).tz
            jxcm__byumx = {'timezone': pa.lib.tzinfo_to_string(fkmuh__lddq)}
        elif isinstance(fejzv__wrigs, types.Array
            ) or fejzv__wrigs == boolean_array:
            tpy__yhn = kvt__mutw = fejzv__wrigs.dtype.name
            if kvt__mutw.startswith('datetime'):
                tpy__yhn = 'datetime'
        elif is_str_arr_type(fejzv__wrigs):
            tpy__yhn = 'unicode'
            kvt__mutw = 'object'
        elif fejzv__wrigs == binary_array_type:
            tpy__yhn = 'bytes'
            kvt__mutw = 'object'
        elif isinstance(fejzv__wrigs, DecimalArrayType):
            tpy__yhn = kvt__mutw = 'object'
        elif isinstance(fejzv__wrigs, IntegerArrayType):
            rddn__pfnx = fejzv__wrigs.dtype.name
            if rddn__pfnx.startswith('int'):
                tpy__yhn = 'Int' + rddn__pfnx[3:]
            elif rddn__pfnx.startswith('uint'):
                tpy__yhn = 'UInt' + rddn__pfnx[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, fejzv__wrigs))
            kvt__mutw = fejzv__wrigs.dtype.name
        elif fejzv__wrigs == datetime_date_array_type:
            tpy__yhn = 'datetime'
            kvt__mutw = 'object'
        elif isinstance(fejzv__wrigs, (StructArrayType, ArrayItemArrayType)):
            tpy__yhn = 'object'
            kvt__mutw = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, fejzv__wrigs))
        hjps__lzxs = {'name': col_name, 'field_name': col_name,
            'pandas_type': tpy__yhn, 'numpy_type': kvt__mutw, 'metadata':
            jxcm__byumx}
        ztj__jforu['columns'].append(hjps__lzxs)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            cwf__xusnl = '__index_level_0__'
            jir__fnh = None
        else:
            cwf__xusnl = '%s'
            jir__fnh = '%s'
        ztj__jforu['index_columns'] = [cwf__xusnl]
        ztj__jforu['columns'].append({'name': jir__fnh, 'field_name':
            cwf__xusnl, 'pandas_type': index.pandas_type_name, 'numpy_type':
            index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        ztj__jforu['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        ztj__jforu['index_columns'] = []
    ztj__jforu['pandas_version'] = pd.__version__
    return ztj__jforu


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
        cgwjd__iutd = []
        for axs__txrhz in partition_cols:
            try:
                idx = df.columns.index(axs__txrhz)
            except ValueError as cer__fda:
                raise BodoError(
                    f'Partition column {axs__txrhz} is not in dataframe')
            cgwjd__iutd.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    iaty__erh = isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType)
    xvkg__sfs = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not iaty__erh)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not iaty__erh or is_overload_true
        (_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and iaty__erh and not is_overload_true(_is_parallel)
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
        hayy__dbgmo = df.runtime_data_types
        fcg__onqdc = len(hayy__dbgmo)
        jxcm__byumx = gen_pandas_parquet_metadata([''] * fcg__onqdc,
            hayy__dbgmo, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        gjdm__fep = jxcm__byumx['columns'][:fcg__onqdc]
        jxcm__byumx['columns'] = jxcm__byumx['columns'][fcg__onqdc:]
        gjdm__fep = [json.dumps(pxdwu__cwp).replace('""', '{0}') for
            pxdwu__cwp in gjdm__fep]
        zxud__bhm = json.dumps(jxcm__byumx)
        bqby__phx = '"columns": ['
        cvmo__ihmbv = zxud__bhm.find(bqby__phx)
        if cvmo__ihmbv == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        zbt__zoi = cvmo__ihmbv + len(bqby__phx)
        thu__kxe = zxud__bhm[:zbt__zoi]
        zxud__bhm = zxud__bhm[zbt__zoi:]
        xbk__nxyyl = len(jxcm__byumx['columns'])
    else:
        zxud__bhm = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and iaty__erh:
        zxud__bhm = zxud__bhm.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            zxud__bhm = zxud__bhm.replace('"%s"', '%s')
    if not df.is_table_format:
        hdpco__ijt = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    ekb__dremp = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        ekb__dremp += '    py_table = get_dataframe_table(df)\n'
        ekb__dremp += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        ekb__dremp += '    info_list = [{}]\n'.format(hdpco__ijt)
        ekb__dremp += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        ekb__dremp += '    columns_index = get_dataframe_column_names(df)\n'
        ekb__dremp += '    names_arr = index_to_array(columns_index)\n'
        ekb__dremp += '    col_names = array_to_info(names_arr)\n'
    else:
        ekb__dremp += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and xvkg__sfs:
        ekb__dremp += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        adavl__tvzsl = True
    else:
        ekb__dremp += '    index_col = array_to_info(np.empty(0))\n'
        adavl__tvzsl = False
    if df.has_runtime_cols:
        ekb__dremp += '    columns_lst = []\n'
        ekb__dremp += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            ekb__dremp += f'    for _ in range(len(py_table.block_{i})):\n'
            ekb__dremp += f"""        columns_lst.append({gjdm__fep[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            ekb__dremp += '        num_cols += 1\n'
        if xbk__nxyyl:
            ekb__dremp += "    columns_lst.append('')\n"
        ekb__dremp += '    columns_str = ", ".join(columns_lst)\n'
        ekb__dremp += ('    metadata = """' + thu__kxe +
            '""" + columns_str + """' + zxud__bhm + '"""\n')
    else:
        ekb__dremp += '    metadata = """' + zxud__bhm + '"""\n'
    ekb__dremp += '    if compression is None:\n'
    ekb__dremp += "        compression = 'none'\n"
    ekb__dremp += '    if df.index.name is not None:\n'
    ekb__dremp += '        name_ptr = df.index.name\n'
    ekb__dremp += '    else:\n'
    ekb__dremp += "        name_ptr = 'null'\n"
    ekb__dremp += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    ggosq__ojqqe = None
    if partition_cols:
        ggosq__ojqqe = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        nxl__zjkel = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in cgwjd__iutd)
        if nxl__zjkel:
            ekb__dremp += '    cat_info_list = [{}]\n'.format(nxl__zjkel)
            ekb__dremp += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            ekb__dremp += '    cat_table = table\n'
        ekb__dremp += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        ekb__dremp += (
            f'    part_cols_idxs = np.array({cgwjd__iutd}, dtype=np.int32)\n')
        ekb__dremp += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        ekb__dremp += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        ekb__dremp += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        ekb__dremp += (
            '                            unicode_to_utf8(compression),\n')
        ekb__dremp += '                            _is_parallel,\n'
        ekb__dremp += (
            '                            unicode_to_utf8(bucket_region),\n')
        ekb__dremp += '                            row_group_size,\n'
        ekb__dremp += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        ekb__dremp += '    delete_table_decref_arrays(table)\n'
        ekb__dremp += '    delete_info_decref_array(index_col)\n'
        ekb__dremp += '    delete_info_decref_array(col_names_no_partitions)\n'
        ekb__dremp += '    delete_info_decref_array(col_names)\n'
        if nxl__zjkel:
            ekb__dremp += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        ekb__dremp += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        ekb__dremp += (
            '                            table, col_names, index_col,\n')
        ekb__dremp += '                            ' + str(adavl__tvzsl
            ) + ',\n'
        ekb__dremp += (
            '                            unicode_to_utf8(metadata),\n')
        ekb__dremp += (
            '                            unicode_to_utf8(compression),\n')
        ekb__dremp += (
            '                            _is_parallel, 1, df.index.start,\n')
        ekb__dremp += (
            '                            df.index.stop, df.index.step,\n')
        ekb__dremp += (
            '                            unicode_to_utf8(name_ptr),\n')
        ekb__dremp += (
            '                            unicode_to_utf8(bucket_region),\n')
        ekb__dremp += '                            row_group_size,\n'
        ekb__dremp += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        ekb__dremp += '    delete_table_decref_arrays(table)\n'
        ekb__dremp += '    delete_info_decref_array(index_col)\n'
        ekb__dremp += '    delete_info_decref_array(col_names)\n'
    else:
        ekb__dremp += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        ekb__dremp += (
            '                            table, col_names, index_col,\n')
        ekb__dremp += '                            ' + str(adavl__tvzsl
            ) + ',\n'
        ekb__dremp += (
            '                            unicode_to_utf8(metadata),\n')
        ekb__dremp += (
            '                            unicode_to_utf8(compression),\n')
        ekb__dremp += '                            _is_parallel, 0, 0, 0, 0,\n'
        ekb__dremp += (
            '                            unicode_to_utf8(name_ptr),\n')
        ekb__dremp += (
            '                            unicode_to_utf8(bucket_region),\n')
        ekb__dremp += '                            row_group_size,\n'
        ekb__dremp += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        ekb__dremp += '    delete_table_decref_arrays(table)\n'
        ekb__dremp += '    delete_info_decref_array(index_col)\n'
        ekb__dremp += '    delete_info_decref_array(col_names)\n'
    hpyaa__sal = {}
    if df.has_runtime_cols:
        sesg__slzsx = None
    else:
        for qucmq__jws in df.columns:
            if not isinstance(qucmq__jws, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        sesg__slzsx = pd.array(df.columns)
    exec(ekb__dremp, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': sesg__slzsx,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': ggosq__ojqqe,
        'get_dataframe_column_names': get_dataframe_column_names,
        'fix_arr_dtype': fix_arr_dtype, 'decode_if_dict_array':
        decode_if_dict_array, 'decode_if_dict_table': decode_if_dict_table},
        hpyaa__sal)
    mobv__nnaq = hpyaa__sal['df_to_parquet']
    return mobv__nnaq


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    tiqdj__gnt = 'all_ok'
    gjtct__dbma, xduep__zwtvv = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        trxs__yiet = 100
        if chunksize is None:
            zxf__gawq = trxs__yiet
        else:
            zxf__gawq = min(chunksize, trxs__yiet)
        if _is_table_create:
            df = df.iloc[:zxf__gawq, :]
        else:
            df = df.iloc[zxf__gawq:, :]
            if len(df) == 0:
                return tiqdj__gnt
    fqpt__brmf = df.columns
    try:
        if gjtct__dbma == 'snowflake':
            if xduep__zwtvv and con.count(xduep__zwtvv) == 1:
                con = con.replace(xduep__zwtvv, quote(xduep__zwtvv))
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
                df.columns = [(lvmws__zxen.upper() if lvmws__zxen.islower()
                     else lvmws__zxen) for lvmws__zxen in df.columns]
            except ImportError as cer__fda:
                tiqdj__gnt = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return tiqdj__gnt
        if gjtct__dbma == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            wrk__zvh = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            zoio__twuu = bodo.typeof(df)
            qkwtr__utfkn = {}
            for lvmws__zxen, njbuv__wbcx in zip(zoio__twuu.columns,
                zoio__twuu.data):
                if df[lvmws__zxen].dtype == 'object':
                    if njbuv__wbcx == datetime_date_array_type:
                        qkwtr__utfkn[lvmws__zxen] = sa.types.Date
                    elif njbuv__wbcx in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not wrk__zvh or wrk__zvh == '0'
                        ):
                        qkwtr__utfkn[lvmws__zxen] = VARCHAR2(4000)
            dtype = qkwtr__utfkn
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as ilfxw__aqk:
            tiqdj__gnt = ilfxw__aqk.args[0]
            if gjtct__dbma == 'oracle' and 'ORA-12899' in tiqdj__gnt:
                tiqdj__gnt += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return tiqdj__gnt
    finally:
        df.columns = fqpt__brmf


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
    ekb__dremp = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    ekb__dremp += f"    if con.startswith('iceberg'):\n"
    ekb__dremp += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    ekb__dremp += f'        if schema is None:\n'
    ekb__dremp += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    ekb__dremp += f'        if chunksize is not None:\n'
    ekb__dremp += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    ekb__dremp += f'        if index and bodo.get_rank() == 0:\n'
    ekb__dremp += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    ekb__dremp += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    ekb__dremp += (
        f"            warnings.warn('index_label is not supported for Iceberg tables.')\n"
        )
    if df.is_table_format:
        ekb__dremp += f'        py_table = get_dataframe_table(df)\n'
        ekb__dremp += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        hdpco__ijt = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        ekb__dremp += f'        info_list = [{hdpco__ijt}]\n'
        ekb__dremp += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        ekb__dremp += (
            f'        columns_index = get_dataframe_column_names(df)\n')
        ekb__dremp += f'        names_arr = index_to_array(columns_index)\n'
        ekb__dremp += f'        col_names = array_to_info(names_arr)\n'
    else:
        ekb__dremp += f'        col_names = array_to_info(col_names_arr)\n'
    ekb__dremp += """        bodo.io.iceberg.iceberg_write(
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
    ekb__dremp += f'        delete_table_decref_arrays(table)\n'
    ekb__dremp += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        sesg__slzsx = None
    else:
        for qucmq__jws in df.columns:
            if not isinstance(qucmq__jws, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        sesg__slzsx = pd.array(df.columns)
    ekb__dremp += f'    else:\n'
    ekb__dremp += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    ekb__dremp += f"        err_msg = 'unset'\n"
    ekb__dremp += f'        if rank != 0:\n'
    ekb__dremp += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    ekb__dremp += f'        elif rank == 0:\n'
    ekb__dremp += f'            err_msg = to_sql_exception_guard_encaps(\n'
    ekb__dremp += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    ekb__dremp += f'                          chunksize, dtype, method,\n'
    ekb__dremp += f'                          True, _is_parallel,\n'
    ekb__dremp += f'                      )\n'
    ekb__dremp += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    ekb__dremp += f"        if_exists = 'append'\n"
    ekb__dremp += f"        if _is_parallel and err_msg == 'all_ok':\n"
    ekb__dremp += f'            err_msg = to_sql_exception_guard_encaps(\n'
    ekb__dremp += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    ekb__dremp += f'                          chunksize, dtype, method,\n'
    ekb__dremp += f'                          False, _is_parallel,\n'
    ekb__dremp += f'                      )\n'
    ekb__dremp += f"        if err_msg != 'all_ok':\n"
    ekb__dremp += f"            print('err_msg=', err_msg)\n"
    ekb__dremp += (
        f"            raise ValueError('error in to_sql() operation')\n")
    hpyaa__sal = {}
    exec(ekb__dremp, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_typ': df.
        table_type, 'col_names_arr': sesg__slzsx,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'delete_info_decref_array': delete_info_decref_array,
        'arr_info_list_to_table': arr_info_list_to_table, 'index_to_array':
        index_to_array, 'pyarrow_table_schema': bodo.io.iceberg.
        pyarrow_schema(df), 'to_sql_exception_guard_encaps':
        to_sql_exception_guard_encaps, 'warnings': warnings}, hpyaa__sal)
    _impl = hpyaa__sal['df_to_sql']
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
        xvvqv__utve = get_overload_const_str(path_or_buf)
        if xvvqv__utve.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        cqc__ncq = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(cqc__ncq), unicode_to_utf8(_bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(cqc__ncq), unicode_to_utf8(_bodo_file_prefix))
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    ukysy__gjgt = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    fbgf__cbrhf = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', ukysy__gjgt, fbgf__cbrhf,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    ekb__dremp = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        pipfo__kbp = data.data.dtype.categories
        ekb__dremp += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        pipfo__kbp = data.dtype.categories
        ekb__dremp += '  data_values = data\n'
    ouhv__tjdgc = len(pipfo__kbp)
    ekb__dremp += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    ekb__dremp += '  numba.parfors.parfor.init_prange()\n'
    ekb__dremp += '  n = len(data_values)\n'
    for i in range(ouhv__tjdgc):
        ekb__dremp += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    ekb__dremp += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ekb__dremp += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for qqs__xqqn in range(ouhv__tjdgc):
        ekb__dremp += '          data_arr_{}[i] = 0\n'.format(qqs__xqqn)
    ekb__dremp += '      else:\n'
    for qjiyc__vgay in range(ouhv__tjdgc):
        ekb__dremp += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            qjiyc__vgay)
    hdpco__ijt = ', '.join(f'data_arr_{i}' for i in range(ouhv__tjdgc))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(pipfo__kbp[0], np.datetime64):
        pipfo__kbp = tuple(pd.Timestamp(lvmws__zxen) for lvmws__zxen in
            pipfo__kbp)
    elif isinstance(pipfo__kbp[0], np.timedelta64):
        pipfo__kbp = tuple(pd.Timedelta(lvmws__zxen) for lvmws__zxen in
            pipfo__kbp)
    return bodo.hiframes.dataframe_impl._gen_init_df(ekb__dremp, pipfo__kbp,
        hdpco__ijt, index)


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
    for ggw__hbwfl in pd_unsupported:
        wayj__rmrs = mod_name + '.' + ggw__hbwfl.__name__
        overload(ggw__hbwfl, no_unliteral=True)(create_unsupported_overload
            (wayj__rmrs))


def _install_dataframe_unsupported():
    for otyi__buo in dataframe_unsupported_attrs:
        yynor__sdtf = 'DataFrame.' + otyi__buo
        overload_attribute(DataFrameType, otyi__buo)(
            create_unsupported_overload(yynor__sdtf))
    for wayj__rmrs in dataframe_unsupported:
        yynor__sdtf = 'DataFrame.' + wayj__rmrs + '()'
        overload_method(DataFrameType, wayj__rmrs)(create_unsupported_overload
            (yynor__sdtf))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
