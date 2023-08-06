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
            jmqei__djrf = f'{len(self.data)} columns of types {set(self.data)}'
            sdxmd__prh = (
                f"('{self.columns[0]}', '{self.columns[1]}', ..., '{self.columns[-1]}')"
                )
            return (
                f'dataframe({jmqei__djrf}, {self.index}, {sdxmd__prh}, {self.dist}, {self.is_table_format}, {self.has_runtime_cols})'
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
        return {tvwg__mzshd: i for i, tvwg__mzshd in enumerate(self.columns)}

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
            nfjw__fka = (self.index if self.index == other.index else self.
                index.unify(typingctx, other.index))
            data = tuple(lpf__vhsy.unify(typingctx, lwhvn__pwg) if 
                lpf__vhsy != lwhvn__pwg else lpf__vhsy for lpf__vhsy,
                lwhvn__pwg in zip(self.data, other.data))
            dist = Distribution(min(self.dist.value, other.dist.value))
            if nfjw__fka is not None and None not in data:
                return DataFrameType(data, nfjw__fka, self.columns, dist,
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
        return all(lpf__vhsy.is_precise() for lpf__vhsy in self.data
            ) and self.index.is_precise()

    def replace_col_type(self, col_name, new_type):
        if col_name not in self.columns:
            raise ValueError(
                f"DataFrameType.replace_col_type replaced column must be found in the DataFrameType. '{col_name}' not found in DataFrameType with columns {self.columns}"
                )
        tlxs__bnol = self.columns.index(col_name)
        gfxxp__rvgrh = tuple(list(self.data[:tlxs__bnol]) + [new_type] +
            list(self.data[tlxs__bnol + 1:]))
        return DataFrameType(gfxxp__rvgrh, self.index, self.columns, self.
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
        xuwzi__sfv = [('data', data_typ), ('index', fe_type.df_type.index),
            ('parent', types.pyobject)]
        if fe_type.df_type.has_runtime_cols:
            xuwzi__sfv.append(('columns', fe_type.df_type.runtime_colname_typ))
        super(DataFramePayloadModel, self).__init__(dmm, fe_type, xuwzi__sfv)


@register_model(DataFrameType)
class DataFrameModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = DataFramePayloadType(fe_type)
        xuwzi__sfv = [('meminfo', types.MemInfoPointer(payload_type)), (
            'parent', types.pyobject)]
        super(DataFrameModel, self).__init__(dmm, fe_type, xuwzi__sfv)


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
        uin__npc = 'n',
        qvst__jyw = {'n': 5}
        usnbh__jefct, ilhyi__war = bodo.utils.typing.fold_typing_args(func_name
            , args, kws, uin__npc, qvst__jyw)
        nicnf__xgfvk = ilhyi__war[0]
        if not is_overload_int(nicnf__xgfvk):
            raise BodoError(f"{func_name}(): 'n' must be an Integer")
        gipl__teum = df.copy()
        return gipl__teum(*ilhyi__war).replace(pysig=usnbh__jefct)

    @bound_function('df.corr')
    def resolve_corr(self, df, args, kws):
        func_name = 'DataFrame.corr'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        rdhdi__sbz = (df,) + args
        uin__npc = 'df', 'method', 'min_periods'
        qvst__jyw = {'method': 'pearson', 'min_periods': 1}
        dhlr__wobo = 'method',
        usnbh__jefct, ilhyi__war = bodo.utils.typing.fold_typing_args(func_name
            , rdhdi__sbz, kws, uin__npc, qvst__jyw, dhlr__wobo)
        bgmwy__ggttc = ilhyi__war[2]
        if not is_overload_int(bgmwy__ggttc):
            raise BodoError(f"{func_name}(): 'min_periods' must be an Integer")
        qeew__gzqei = []
        xrhac__mger = []
        for tvwg__mzshd, yke__ymo in zip(df.columns, df.data):
            if bodo.utils.typing._is_pandas_numeric_dtype(yke__ymo.dtype):
                qeew__gzqei.append(tvwg__mzshd)
                xrhac__mger.append(types.Array(types.float64, 1, 'A'))
        if len(qeew__gzqei) == 0:
            raise_bodo_error('DataFrame.corr(): requires non-empty dataframe')
        xrhac__mger = tuple(xrhac__mger)
        qeew__gzqei = tuple(qeew__gzqei)
        index_typ = bodo.utils.typing.type_col_to_index(qeew__gzqei)
        gipl__teum = DataFrameType(xrhac__mger, index_typ, qeew__gzqei)
        return gipl__teum(*ilhyi__war).replace(pysig=usnbh__jefct)

    @bound_function('df.pipe', no_unliteral=True)
    def resolve_pipe(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.pipe()')
        return bodo.hiframes.pd_groupby_ext.resolve_obj_pipe(self, df, args,
            kws, 'DataFrame')

    @bound_function('df.apply', no_unliteral=True)
    def resolve_apply(self, df, args, kws):
        check_runtime_cols_unsupported(df, 'DataFrame.apply()')
        kws = dict(kws)
        lgu__awfs = args[0] if len(args) > 0 else kws.pop('func', None)
        axis = args[1] if len(args) > 1 else kws.pop('axis', types.literal(0))
        lev__dtry = args[2] if len(args) > 2 else kws.pop('raw', types.
            literal(False))
        icua__codw = args[3] if len(args) > 3 else kws.pop('result_type',
            types.none)
        qmt__dlb = args[4] if len(args) > 4 else kws.pop('args', types.
            Tuple([]))
        emwmw__fwkhm = dict(raw=lev__dtry, result_type=icua__codw)
        hvb__fhz = dict(raw=False, result_type=None)
        check_unsupported_args('Dataframe.apply', emwmw__fwkhm, hvb__fhz,
            package_name='pandas', module_name='DataFrame')
        adg__bsfm = True
        if types.unliteral(lgu__awfs) == types.unicode_type:
            if not is_overload_constant_str(lgu__awfs):
                raise BodoError(
                    f'DataFrame.apply(): string argument (for builtins) must be a compile time constant'
                    )
            adg__bsfm = False
        if not is_overload_constant_int(axis):
            raise BodoError(
                'Dataframe.apply(): axis argument must be a compile time constant.'
                )
        gsl__duafa = get_overload_const_int(axis)
        if adg__bsfm and gsl__duafa != 1:
            raise BodoError(
                'Dataframe.apply(): only axis=1 supported for user-defined functions'
                )
        elif gsl__duafa not in (0, 1):
            raise BodoError('Dataframe.apply(): axis must be either 0 or 1')
        eqj__pigqp = []
        for arr_typ in df.data:
            aeaph__jtlpu = SeriesType(arr_typ.dtype, arr_typ, df.index,
                string_type)
            nbs__iszw = self.context.resolve_function_type(operator.getitem,
                (SeriesIlocType(aeaph__jtlpu), types.int64), {}).return_type
            eqj__pigqp.append(nbs__iszw)
        azcv__gzldb = types.none
        huz__bye = HeterogeneousIndexType(types.BaseTuple.from_types(tuple(
            types.literal(tvwg__mzshd) for tvwg__mzshd in df.columns)), None)
        abo__zikf = types.BaseTuple.from_types(eqj__pigqp)
        diw__gbkcm = types.Tuple([types.bool_] * len(abo__zikf))
        fnadw__qypn = bodo.NullableTupleType(abo__zikf, diw__gbkcm)
        pinvh__rms = df.index.dtype
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df.index,
            'DataFrame.apply()')
        if pinvh__rms == types.NPDatetime('ns'):
            pinvh__rms = bodo.pd_timestamp_type
        if pinvh__rms == types.NPTimedelta('ns'):
            pinvh__rms = bodo.pd_timedelta_type
        if is_heterogeneous_tuple_type(abo__zikf):
            gst__snbpg = HeterogeneousSeriesType(fnadw__qypn, huz__bye,
                pinvh__rms)
        else:
            gst__snbpg = SeriesType(abo__zikf.dtype, fnadw__qypn, huz__bye,
                pinvh__rms)
        non__pom = gst__snbpg,
        if qmt__dlb is not None:
            non__pom += tuple(qmt__dlb.types)
        try:
            if not adg__bsfm:
                bireh__poubi = bodo.utils.transform.get_udf_str_return_type(df,
                    get_overload_const_str(lgu__awfs), self.context,
                    'DataFrame.apply', axis if gsl__duafa == 1 else None)
            else:
                bireh__poubi = get_const_func_output_type(lgu__awfs,
                    non__pom, kws, self.context, numba.core.registry.
                    cpu_target.target_context)
        except Exception as xgqld__nnid:
            raise_bodo_error(get_udf_error_msg('DataFrame.apply()',
                xgqld__nnid))
        if adg__bsfm:
            if not (is_overload_constant_int(axis) and 
                get_overload_const_int(axis) == 1):
                raise BodoError(
                    'Dataframe.apply(): only user-defined functions with axis=1 supported'
                    )
            if isinstance(bireh__poubi, (SeriesType, HeterogeneousSeriesType)
                ) and bireh__poubi.const_info is None:
                raise BodoError(
                    'Invalid Series output in UDF (Series with constant length and constant Index value expected)'
                    )
            if isinstance(bireh__poubi, HeterogeneousSeriesType):
                wii__yntg, zydgl__uny = bireh__poubi.const_info
                if isinstance(bireh__poubi.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    fzbrk__tyz = bireh__poubi.data.tuple_typ.types
                elif isinstance(bireh__poubi.data, types.Tuple):
                    fzbrk__tyz = bireh__poubi.data.types
                else:
                    raise_bodo_error(
                        'df.apply(): Unexpected Series return type for Heterogeneous data'
                        )
                cvpza__gmvvu = tuple(to_nullable_type(dtype_to_array_type(
                    lkngw__iihea)) for lkngw__iihea in fzbrk__tyz)
                uvqzw__nhlj = DataFrameType(cvpza__gmvvu, df.index, zydgl__uny)
            elif isinstance(bireh__poubi, SeriesType):
                orksi__xybue, zydgl__uny = bireh__poubi.const_info
                cvpza__gmvvu = tuple(to_nullable_type(dtype_to_array_type(
                    bireh__poubi.dtype)) for wii__yntg in range(orksi__xybue))
                uvqzw__nhlj = DataFrameType(cvpza__gmvvu, df.index, zydgl__uny)
            else:
                bxo__emojf = get_udf_out_arr_type(bireh__poubi)
                uvqzw__nhlj = SeriesType(bxo__emojf.dtype, bxo__emojf, df.
                    index, None)
        else:
            uvqzw__nhlj = bireh__poubi
        mtd__slp = ', '.join("{} = ''".format(lpf__vhsy) for lpf__vhsy in
            kws.keys())
        kuxhv__fgg = f"""def apply_stub(func, axis=0, raw=False, result_type=None, args=(), {mtd__slp}):
"""
        kuxhv__fgg += '    pass\n'
        vpxqv__kjm = {}
        exec(kuxhv__fgg, {}, vpxqv__kjm)
        togmo__pmk = vpxqv__kjm['apply_stub']
        usnbh__jefct = numba.core.utils.pysignature(togmo__pmk)
        efsh__yozo = (lgu__awfs, axis, lev__dtry, icua__codw, qmt__dlb
            ) + tuple(kws.values())
        return signature(uvqzw__nhlj, *efsh__yozo).replace(pysig=usnbh__jefct)

    @bound_function('df.plot', no_unliteral=True)
    def resolve_plot(self, df, args, kws):
        func_name = 'DataFrame.plot'
        check_runtime_cols_unsupported(df, f'{func_name}()')
        uin__npc = ('x', 'y', 'kind', 'figsize', 'ax', 'subplots', 'sharex',
            'sharey', 'layout', 'use_index', 'title', 'grid', 'legend',
            'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks', 'xlim',
            'ylim', 'rot', 'fontsize', 'colormap', 'table', 'yerr', 'xerr',
            'secondary_y', 'sort_columns', 'xlabel', 'ylabel', 'position',
            'stacked', 'mark_right', 'include_bool', 'backend')
        qvst__jyw = {'x': None, 'y': None, 'kind': 'line', 'figsize': None,
            'ax': None, 'subplots': False, 'sharex': None, 'sharey': False,
            'layout': None, 'use_index': True, 'title': None, 'grid': None,
            'legend': True, 'style': None, 'logx': False, 'logy': False,
            'loglog': False, 'xticks': None, 'yticks': None, 'xlim': None,
            'ylim': None, 'rot': None, 'fontsize': None, 'colormap': None,
            'table': False, 'yerr': None, 'xerr': None, 'secondary_y': 
            False, 'sort_columns': False, 'xlabel': None, 'ylabel': None,
            'position': 0.5, 'stacked': False, 'mark_right': True,
            'include_bool': False, 'backend': None}
        dhlr__wobo = ('subplots', 'sharex', 'sharey', 'layout', 'use_index',
            'grid', 'style', 'logx', 'logy', 'loglog', 'xlim', 'ylim',
            'rot', 'colormap', 'table', 'yerr', 'xerr', 'sort_columns',
            'secondary_y', 'colorbar', 'position', 'stacked', 'mark_right',
            'include_bool', 'backend')
        usnbh__jefct, ilhyi__war = bodo.utils.typing.fold_typing_args(func_name
            , args, kws, uin__npc, qvst__jyw, dhlr__wobo)
        typ__sroz = ilhyi__war[2]
        if not is_overload_constant_str(typ__sroz):
            raise BodoError(
                f"{func_name}: kind must be a constant string and one of ('line', 'scatter')."
                )
        ufy__mqx = ilhyi__war[0]
        if not is_overload_none(ufy__mqx) and not (is_overload_int(ufy__mqx
            ) or is_overload_constant_str(ufy__mqx)):
            raise BodoError(
                f'{func_name}: x must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(ufy__mqx):
            vjs__biwmx = get_overload_const_str(ufy__mqx)
            if vjs__biwmx not in df.columns:
                raise BodoError(f'{func_name}: {vjs__biwmx} column not found.')
        elif is_overload_int(ufy__mqx):
            hibgf__txj = get_overload_const_int(ufy__mqx)
            if hibgf__txj > len(df.columns):
                raise BodoError(
                    f'{func_name}: x: {hibgf__txj} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            ufy__mqx = df.columns[ufy__mqx]
        vobfu__yku = ilhyi__war[1]
        if not is_overload_none(vobfu__yku) and not (is_overload_int(
            vobfu__yku) or is_overload_constant_str(vobfu__yku)):
            raise BodoError(
                'df.plot(): y must be a constant column name, constant integer, or None.'
                )
        if is_overload_constant_str(vobfu__yku):
            tndp__tpj = get_overload_const_str(vobfu__yku)
            if tndp__tpj not in df.columns:
                raise BodoError(f'{func_name}: {tndp__tpj} column not found.')
        elif is_overload_int(vobfu__yku):
            nsyi__upuzh = get_overload_const_int(vobfu__yku)
            if nsyi__upuzh > len(df.columns):
                raise BodoError(
                    f'{func_name}: y: {nsyi__upuzh} is out of bounds for axis 0 with size {len(df.columns)}'
                    )
            vobfu__yku = df.columns[vobfu__yku]
        peq__vkawf = ilhyi__war[3]
        if not is_overload_none(peq__vkawf) and not is_tuple_like_type(
            peq__vkawf):
            raise BodoError(
                f'{func_name}: figsize must be a constant numeric tuple (width, height) or None.'
                )
        deh__xvfyd = ilhyi__war[10]
        if not is_overload_none(deh__xvfyd) and not is_overload_constant_str(
            deh__xvfyd):
            raise BodoError(
                f'{func_name}: title must be a constant string or None.')
        mifj__xda = ilhyi__war[12]
        if not is_overload_bool(mifj__xda):
            raise BodoError(f'{func_name}: legend must be a boolean type.')
        xmgs__reh = ilhyi__war[17]
        if not is_overload_none(xmgs__reh) and not is_tuple_like_type(xmgs__reh
            ):
            raise BodoError(
                f'{func_name}: xticks must be a constant tuple or None.')
        dfb__zjljh = ilhyi__war[18]
        if not is_overload_none(dfb__zjljh) and not is_tuple_like_type(
            dfb__zjljh):
            raise BodoError(
                f'{func_name}: yticks must be a constant tuple or None.')
        wln__tbd = ilhyi__war[22]
        if not is_overload_none(wln__tbd) and not is_overload_int(wln__tbd):
            raise BodoError(
                f'{func_name}: fontsize must be an integer or None.')
        jel__irxpr = ilhyi__war[29]
        if not is_overload_none(jel__irxpr) and not is_overload_constant_str(
            jel__irxpr):
            raise BodoError(
                f'{func_name}: xlabel must be a constant string or None.')
        zeu__zrkx = ilhyi__war[30]
        if not is_overload_none(zeu__zrkx) and not is_overload_constant_str(
            zeu__zrkx):
            raise BodoError(
                f'{func_name}: ylabel must be a constant string or None.')
        dketb__fmmjm = types.List(types.mpl_line_2d_type)
        typ__sroz = get_overload_const_str(typ__sroz)
        if typ__sroz == 'scatter':
            if is_overload_none(ufy__mqx) and is_overload_none(vobfu__yku):
                raise BodoError(
                    f'{func_name}: {typ__sroz} requires an x and y column.')
            elif is_overload_none(ufy__mqx):
                raise BodoError(
                    f'{func_name}: {typ__sroz} x column is missing.')
            elif is_overload_none(vobfu__yku):
                raise BodoError(
                    f'{func_name}: {typ__sroz} y column is missing.')
            dketb__fmmjm = types.mpl_path_collection_type
        elif typ__sroz != 'line':
            raise BodoError(f'{func_name}: {typ__sroz} plot is not supported.')
        return signature(dketb__fmmjm, *ilhyi__war).replace(pysig=usnbh__jefct)

    def generic_resolve(self, df, attr):
        if self._is_existing_attr(attr):
            return
        check_runtime_cols_unsupported(df,
            'Acessing DataFrame columns by attribute')
        if attr in df.columns:
            aioqb__gvhqa = df.columns.index(attr)
            arr_typ = df.data[aioqb__gvhqa]
            return SeriesType(arr_typ.dtype, arr_typ, df.index, types.
                StringLiteral(attr))
        if len(df.columns) > 0 and isinstance(df.columns[0], tuple):
            bspa__spqyf = []
            gfxxp__rvgrh = []
            nprdg__zsuv = False
            for i, ungoi__eijx in enumerate(df.columns):
                if ungoi__eijx[0] != attr:
                    continue
                nprdg__zsuv = True
                bspa__spqyf.append(ungoi__eijx[1] if len(ungoi__eijx) == 2 else
                    ungoi__eijx[1:])
                gfxxp__rvgrh.append(df.data[i])
            if nprdg__zsuv:
                return DataFrameType(tuple(gfxxp__rvgrh), df.index, tuple(
                    bspa__spqyf))


DataFrameAttribute._no_unliteral = True


@overload(operator.getitem, no_unliteral=True)
def namedtuple_getitem_overload(tup, idx):
    if isinstance(tup, types.BaseNamedTuple) and is_overload_constant_str(idx):
        ymixr__fngrg = get_overload_const_str(idx)
        val_ind = tup.instance_class._fields.index(ymixr__fngrg)
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
        kvbk__jiq = builder.extract_value(payload.data, i)
        context.nrt.decref(builder, df_type.data[i], kvbk__jiq)
    context.nrt.decref(builder, df_type.index, payload.index)


def define_df_dtor(context, builder, df_type, payload_type):
    bfe__tyqbu = builder.module
    tgwqs__kibzk = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    swln__sund = cgutils.get_or_insert_function(bfe__tyqbu, tgwqs__kibzk,
        name='.dtor.df.{}'.format(df_type))
    if not swln__sund.is_declaration:
        return swln__sund
    swln__sund.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(swln__sund.append_basic_block())
    mkml__imcm = swln__sund.args[0]
    hgtfz__kwjb = context.get_value_type(payload_type).as_pointer()
    afe__gvmql = builder.bitcast(mkml__imcm, hgtfz__kwjb)
    payload = context.make_helper(builder, payload_type, ref=afe__gvmql)
    decref_df_data(context, builder, payload, df_type)
    has_parent = cgutils.is_not_null(builder, payload.parent)
    with builder.if_then(has_parent):
        zqt__vtac = context.get_python_api(builder)
        muued__ctl = zqt__vtac.gil_ensure()
        zqt__vtac.decref(payload.parent)
        zqt__vtac.gil_release(muued__ctl)
    builder.ret_void()
    return swln__sund


def construct_dataframe(context, builder, df_type, data_tup, index_val,
    parent=None, colnames=None):
    payload_type = DataFramePayloadType(df_type)
    lcej__mym = cgutils.create_struct_proxy(payload_type)(context, builder)
    lcej__mym.data = data_tup
    lcej__mym.index = index_val
    if colnames is not None:
        assert df_type.has_runtime_cols, 'construct_dataframe can only provide colnames if columns are determined at runtime'
        lcej__mym.columns = colnames
    eyi__qft = context.get_value_type(payload_type)
    agxwh__syp = context.get_abi_sizeof(eyi__qft)
    ktg__nefjy = define_df_dtor(context, builder, df_type, payload_type)
    woohu__fdir = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, agxwh__syp), ktg__nefjy)
    awe__wczwc = context.nrt.meminfo_data(builder, woohu__fdir)
    thrc__ljxlx = builder.bitcast(awe__wczwc, eyi__qft.as_pointer())
    zfxu__pau = cgutils.create_struct_proxy(df_type)(context, builder)
    zfxu__pau.meminfo = woohu__fdir
    if parent is None:
        zfxu__pau.parent = cgutils.get_null_value(zfxu__pau.parent.type)
    else:
        zfxu__pau.parent = parent
        lcej__mym.parent = parent
        has_parent = cgutils.is_not_null(builder, parent)
        with builder.if_then(has_parent):
            zqt__vtac = context.get_python_api(builder)
            muued__ctl = zqt__vtac.gil_ensure()
            zqt__vtac.incref(parent)
            zqt__vtac.gil_release(muued__ctl)
    builder.store(lcej__mym._getvalue(), thrc__ljxlx)
    return zfxu__pau._getvalue()


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
        kodf__dgdx = [data_typ.dtype.arr_types.dtype] * len(data_typ.dtype.
            arr_types)
    else:
        kodf__dgdx = [lkngw__iihea for lkngw__iihea in data_typ.dtype.arr_types
            ]
    yyzcz__jrq = DataFrameType(tuple(kodf__dgdx + [colnames_index_typ]),
        index_typ, None, is_table_format=True)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup, index, col_names = args
        parent = None
        phmee__vbfc = construct_dataframe(context, builder, df_type,
            data_tup, index, parent, col_names)
        context.nrt.incref(builder, data_typ, data_tup)
        context.nrt.incref(builder, index_typ, index)
        context.nrt.incref(builder, colnames_index_typ, col_names)
        return phmee__vbfc
    sig = signature(yyzcz__jrq, data_typ, index_typ, colnames_index_typ)
    return sig, codegen


@intrinsic
def init_dataframe(typingctx, data_tup_typ, index_typ, col_names_typ):
    assert is_pd_index_type(index_typ) or isinstance(index_typ, MultiIndexType
        ), 'init_dataframe(): invalid index type'
    orksi__xybue = len(data_tup_typ.types)
    if orksi__xybue == 0:
        column_names = ()
    rsgt__kuayd = col_names_typ.instance_type if isinstance(col_names_typ,
        types.TypeRef) else col_names_typ
    assert isinstance(rsgt__kuayd, ColNamesMetaType) and isinstance(rsgt__kuayd
        .meta, tuple
        ), 'Third argument to init_dataframe must be of type ColNamesMetaType, and must contain a tuple of column names'
    column_names = rsgt__kuayd.meta
    if orksi__xybue == 1 and isinstance(data_tup_typ.types[0], TableType):
        orksi__xybue = len(data_tup_typ.types[0].arr_types)
    assert len(column_names
        ) == orksi__xybue, 'init_dataframe(): number of column names does not match number of columns'
    is_table_format = False
    uepwo__yrdn = data_tup_typ.types
    if orksi__xybue != 0 and isinstance(data_tup_typ.types[0], TableType):
        uepwo__yrdn = data_tup_typ.types[0].arr_types
        is_table_format = True
    yyzcz__jrq = DataFrameType(uepwo__yrdn, index_typ, column_names,
        is_table_format=is_table_format)

    def codegen(context, builder, signature, args):
        df_type = signature.return_type
        data_tup = args[0]
        index_val = args[1]
        parent = None
        if is_table_format:
            ctrzt__srat = cgutils.create_struct_proxy(yyzcz__jrq.table_type)(
                context, builder, builder.extract_value(data_tup, 0))
            parent = ctrzt__srat.parent
        phmee__vbfc = construct_dataframe(context, builder, df_type,
            data_tup, index_val, parent, None)
        context.nrt.incref(builder, data_tup_typ, data_tup)
        context.nrt.incref(builder, index_typ, index_val)
        return phmee__vbfc
    sig = signature(yyzcz__jrq, data_tup_typ, index_typ, col_names_typ)
    return sig, codegen


@intrinsic
def has_parent(typingctx, df=None):
    check_runtime_cols_unsupported(df, 'has_parent')

    def codegen(context, builder, sig, args):
        zfxu__pau = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        return cgutils.is_not_null(builder, zfxu__pau.parent)
    return signature(types.bool_, df), codegen


@intrinsic
def _column_needs_unboxing(typingctx, df_typ, i_typ=None):
    check_runtime_cols_unsupported(df_typ, '_column_needs_unboxing')
    assert isinstance(df_typ, DataFrameType) and is_overload_constant_int(i_typ
        )

    def codegen(context, builder, sig, args):
        lcej__mym = get_dataframe_payload(context, builder, df_typ, args[0])
        yuzeb__juz = get_overload_const_int(i_typ)
        arr_typ = df_typ.data[yuzeb__juz]
        if df_typ.is_table_format:
            ctrzt__srat = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(lcej__mym.data, 0))
            vfs__ifgw = df_typ.table_type.type_to_blk[arr_typ]
            xzy__fvvg = getattr(ctrzt__srat, f'block_{vfs__ifgw}')
            tna__feqj = ListInstance(context, builder, types.List(arr_typ),
                xzy__fvvg)
            abtx__qahu = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[yuzeb__juz])
            kvbk__jiq = tna__feqj.getitem(abtx__qahu)
        else:
            kvbk__jiq = builder.extract_value(lcej__mym.data, yuzeb__juz)
        qyfl__cxqk = cgutils.alloca_once_value(builder, kvbk__jiq)
        uuakb__ckf = cgutils.alloca_once_value(builder, context.
            get_constant_null(arr_typ))
        return is_ll_eq(builder, qyfl__cxqk, uuakb__ckf)
    return signature(types.bool_, df_typ, i_typ), codegen


def get_dataframe_payload(context, builder, df_type, value):
    woohu__fdir = cgutils.create_struct_proxy(df_type)(context, builder, value
        ).meminfo
    payload_type = DataFramePayloadType(df_type)
    payload = context.nrt.meminfo_data(builder, woohu__fdir)
    hgtfz__kwjb = context.get_value_type(payload_type).as_pointer()
    payload = builder.bitcast(payload, hgtfz__kwjb)
    return context.make_helper(builder, payload_type, ref=payload)


@intrinsic
def _get_dataframe_data(typingctx, df_typ=None):
    check_runtime_cols_unsupported(df_typ, '_get_dataframe_data')
    yyzcz__jrq = types.Tuple(df_typ.data)
    if df_typ.is_table_format:
        yyzcz__jrq = types.Tuple([TableType(df_typ.data)])
    sig = signature(yyzcz__jrq, df_typ)

    def codegen(context, builder, signature, args):
        lcej__mym = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, signature.return_type,
            lcej__mym.data)
    return sig, codegen


@intrinsic
def get_dataframe_index(typingctx, df_typ=None):

    def codegen(context, builder, signature, args):
        lcej__mym = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.index, lcej__mym.
            index)
    yyzcz__jrq = df_typ.index
    sig = signature(yyzcz__jrq, df_typ)
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
        gipl__teum = df.data[i]
        return gipl__teum(*args)


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
        lcej__mym = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.table_type,
            builder.extract_value(lcej__mym.data, 0))
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
    pqke__zfol = ',' if len(df.columns) > 1 else ''
    return eval(f'lambda df: ({data}{pqke__zfol})', {'bodo': bodo})


@infer_global(get_dataframe_all_data)
class GetDataFrameAllDataInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        df_type = args[0]
        check_runtime_cols_unsupported(df_type, 'get_dataframe_data')
        gipl__teum = (df_type.table_type if df_type.is_table_format else
            types.BaseTuple.from_types(df_type.data))
        return gipl__teum(*args)


@lower_builtin(get_dataframe_all_data, DataFrameType)
def lower_get_dataframe_all_data(context, builder, sig, args):
    impl = get_dataframe_all_data_impl(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@intrinsic
def get_dataframe_column_names(typingctx, df_typ=None):
    assert df_typ.has_runtime_cols, 'get_dataframe_column_names() expects columns to be determined at runtime'

    def codegen(context, builder, signature, args):
        lcej__mym = get_dataframe_payload(context, builder, signature.args[
            0], args[0])
        return impl_ret_borrowed(context, builder, df_typ.
            runtime_colname_typ, lcej__mym.columns)
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
    abo__zikf = self.typemap[data_tup.name]
    if any(is_tuple_like_type(lkngw__iihea) for lkngw__iihea in abo__zikf.types
        ):
        return None
    if equiv_set.has_shape(data_tup):
        ghqjg__mpfji = equiv_set.get_shape(data_tup)
        if len(ghqjg__mpfji) > 1:
            equiv_set.insert_equiv(*ghqjg__mpfji)
        if len(ghqjg__mpfji) > 0:
            huz__bye = self.typemap[index.name]
            if not isinstance(huz__bye, HeterogeneousIndexType
                ) and equiv_set.has_shape(index):
                equiv_set.insert_equiv(ghqjg__mpfji[0], index)
            return ArrayAnalysis.AnalyzeResult(shape=(ghqjg__mpfji[0], len(
                ghqjg__mpfji)), pre=[])
    return None


(ArrayAnalysis._analyze_op_call_bodo_hiframes_pd_dataframe_ext_init_dataframe
    ) = init_dataframe_equiv


def get_dataframe_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    zvh__sndym = args[0]
    data_types = self.typemap[zvh__sndym.name].data
    if any(is_tuple_like_type(lkngw__iihea) for lkngw__iihea in data_types):
        return None
    if equiv_set.has_shape(zvh__sndym):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            zvh__sndym)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_data
    ) = get_dataframe_data_equiv


def get_dataframe_index_equiv(self, scope, equiv_set, loc, args, kws):
    from bodo.hiframes.pd_index_ext import HeterogeneousIndexType
    assert len(args) == 1 and not kws
    zvh__sndym = args[0]
    huz__bye = self.typemap[zvh__sndym.name].index
    if isinstance(huz__bye, HeterogeneousIndexType):
        return None
    if equiv_set.has_shape(zvh__sndym):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            zvh__sndym)[0], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_index
    ) = get_dataframe_index_equiv


def get_dataframe_table_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    zvh__sndym = args[0]
    if equiv_set.has_shape(zvh__sndym):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            zvh__sndym), pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_table
    ) = get_dataframe_table_equiv


def get_dataframe_column_names_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    zvh__sndym = args[0]
    if equiv_set.has_shape(zvh__sndym):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            zvh__sndym)[1], pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_hiframes_pd_dataframe_ext_get_dataframe_column_names
    ) = get_dataframe_column_names_equiv


@intrinsic
def set_dataframe_data(typingctx, df_typ, c_ind_typ, arr_typ=None):
    check_runtime_cols_unsupported(df_typ, 'set_dataframe_data')
    assert is_overload_constant_int(c_ind_typ)
    yuzeb__juz = get_overload_const_int(c_ind_typ)
    if df_typ.data[yuzeb__juz] != arr_typ:
        raise BodoError(
            'Changing dataframe column data type inplace is not supported in conditionals/loops or for dataframe arguments'
            )

    def codegen(context, builder, signature, args):
        iex__rgcb, wii__yntg, ixdoz__vagx = args
        lcej__mym = get_dataframe_payload(context, builder, df_typ, iex__rgcb)
        if df_typ.is_table_format:
            ctrzt__srat = cgutils.create_struct_proxy(df_typ.table_type)(
                context, builder, builder.extract_value(lcej__mym.data, 0))
            vfs__ifgw = df_typ.table_type.type_to_blk[arr_typ]
            xzy__fvvg = getattr(ctrzt__srat, f'block_{vfs__ifgw}')
            tna__feqj = ListInstance(context, builder, types.List(arr_typ),
                xzy__fvvg)
            abtx__qahu = context.get_constant(types.int64, df_typ.
                table_type.block_offsets[yuzeb__juz])
            tna__feqj.setitem(abtx__qahu, ixdoz__vagx, True)
        else:
            kvbk__jiq = builder.extract_value(lcej__mym.data, yuzeb__juz)
            context.nrt.decref(builder, df_typ.data[yuzeb__juz], kvbk__jiq)
            lcej__mym.data = builder.insert_value(lcej__mym.data,
                ixdoz__vagx, yuzeb__juz)
            context.nrt.incref(builder, arr_typ, ixdoz__vagx)
        zfxu__pau = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=iex__rgcb)
        payload_type = DataFramePayloadType(df_typ)
        afe__gvmql = context.nrt.meminfo_data(builder, zfxu__pau.meminfo)
        hgtfz__kwjb = context.get_value_type(payload_type).as_pointer()
        afe__gvmql = builder.bitcast(afe__gvmql, hgtfz__kwjb)
        builder.store(lcej__mym._getvalue(), afe__gvmql)
        return impl_ret_borrowed(context, builder, df_typ, iex__rgcb)
    sig = signature(df_typ, df_typ, c_ind_typ, arr_typ)
    return sig, codegen


@intrinsic
def set_df_index(typingctx, df_t, index_t=None):
    check_runtime_cols_unsupported(df_t, 'set_df_index')

    def codegen(context, builder, signature, args):
        bia__bgf = args[0]
        index_val = args[1]
        df_typ = signature.args[0]
        ssp__fpe = cgutils.create_struct_proxy(df_typ)(context, builder,
            value=bia__bgf)
        pgw__eebjj = get_dataframe_payload(context, builder, df_typ, bia__bgf)
        zfxu__pau = construct_dataframe(context, builder, signature.
            return_type, pgw__eebjj.data, index_val, ssp__fpe.parent, None)
        context.nrt.incref(builder, index_t, index_val)
        context.nrt.incref(builder, types.Tuple(df_t.data), pgw__eebjj.data)
        return zfxu__pau
    yyzcz__jrq = DataFrameType(df_t.data, index_t, df_t.columns, df_t.dist,
        df_t.is_table_format)
    sig = signature(yyzcz__jrq, df_t, index_t)
    return sig, codegen


@intrinsic
def set_df_column_with_reflect(typingctx, df_type, cname_type, arr_type=None):
    check_runtime_cols_unsupported(df_type, 'set_df_column_with_reflect')
    assert is_literal_type(cname_type), 'constant column name expected'
    col_name = get_literal_value(cname_type)
    orksi__xybue = len(df_type.columns)
    imvt__lzhox = orksi__xybue
    mgme__rggmt = df_type.data
    column_names = df_type.columns
    index_typ = df_type.index
    fauou__vgmud = col_name not in df_type.columns
    yuzeb__juz = orksi__xybue
    if fauou__vgmud:
        mgme__rggmt += arr_type,
        column_names += col_name,
        imvt__lzhox += 1
    else:
        yuzeb__juz = df_type.columns.index(col_name)
        mgme__rggmt = tuple(arr_type if i == yuzeb__juz else mgme__rggmt[i] for
            i in range(orksi__xybue))

    def codegen(context, builder, signature, args):
        iex__rgcb, wii__yntg, ixdoz__vagx = args
        in_dataframe_payload = get_dataframe_payload(context, builder,
            df_type, iex__rgcb)
        opq__rwxjp = cgutils.create_struct_proxy(df_type)(context, builder,
            value=iex__rgcb)
        if df_type.is_table_format:
            roniq__jce = df_type.table_type
            nylyj__jmoj = builder.extract_value(in_dataframe_payload.data, 0)
            qthjs__tbeg = TableType(mgme__rggmt)
            ozuzg__fxum = set_table_data_codegen(context, builder,
                roniq__jce, nylyj__jmoj, qthjs__tbeg, arr_type, ixdoz__vagx,
                yuzeb__juz, fauou__vgmud)
            data_tup = context.make_tuple(builder, types.Tuple([qthjs__tbeg
                ]), [ozuzg__fxum])
        else:
            uepwo__yrdn = [(builder.extract_value(in_dataframe_payload.data,
                i) if i != yuzeb__juz else ixdoz__vagx) for i in range(
                orksi__xybue)]
            if fauou__vgmud:
                uepwo__yrdn.append(ixdoz__vagx)
            for zvh__sndym, zuah__hlqmj in zip(uepwo__yrdn, mgme__rggmt):
                context.nrt.incref(builder, zuah__hlqmj, zvh__sndym)
            data_tup = context.make_tuple(builder, types.Tuple(mgme__rggmt),
                uepwo__yrdn)
        index_val = in_dataframe_payload.index
        context.nrt.incref(builder, index_typ, index_val)
        qwan__wdcoo = construct_dataframe(context, builder, signature.
            return_type, data_tup, index_val, opq__rwxjp.parent, None)
        if not fauou__vgmud and arr_type == df_type.data[yuzeb__juz]:
            decref_df_data(context, builder, in_dataframe_payload, df_type)
            payload_type = DataFramePayloadType(df_type)
            afe__gvmql = context.nrt.meminfo_data(builder, opq__rwxjp.meminfo)
            hgtfz__kwjb = context.get_value_type(payload_type).as_pointer()
            afe__gvmql = builder.bitcast(afe__gvmql, hgtfz__kwjb)
            aocka__imqal = get_dataframe_payload(context, builder, df_type,
                qwan__wdcoo)
            builder.store(aocka__imqal._getvalue(), afe__gvmql)
            context.nrt.incref(builder, index_typ, index_val)
            if df_type.is_table_format:
                context.nrt.incref(builder, qthjs__tbeg, builder.
                    extract_value(data_tup, 0))
            else:
                for zvh__sndym, zuah__hlqmj in zip(uepwo__yrdn, mgme__rggmt):
                    context.nrt.incref(builder, zuah__hlqmj, zvh__sndym)
        has_parent = cgutils.is_not_null(builder, opq__rwxjp.parent)
        with builder.if_then(has_parent):
            zqt__vtac = context.get_python_api(builder)
            muued__ctl = zqt__vtac.gil_ensure()
            imgh__xyt = context.get_env_manager(builder)
            context.nrt.incref(builder, arr_type, ixdoz__vagx)
            tvwg__mzshd = numba.core.pythonapi._BoxContext(context, builder,
                zqt__vtac, imgh__xyt)
            uehgg__yyo = tvwg__mzshd.pyapi.from_native_value(arr_type,
                ixdoz__vagx, tvwg__mzshd.env_manager)
            if isinstance(col_name, str):
                vkgzp__ymee = context.insert_const_string(builder.module,
                    col_name)
                txd__radnw = zqt__vtac.string_from_string(vkgzp__ymee)
            else:
                assert isinstance(col_name, int)
                txd__radnw = zqt__vtac.long_from_longlong(context.
                    get_constant(types.intp, col_name))
            zqt__vtac.object_setitem(opq__rwxjp.parent, txd__radnw, uehgg__yyo)
            zqt__vtac.decref(uehgg__yyo)
            zqt__vtac.decref(txd__radnw)
            zqt__vtac.gil_release(muued__ctl)
        return qwan__wdcoo
    yyzcz__jrq = DataFrameType(mgme__rggmt, index_typ, column_names,
        df_type.dist, df_type.is_table_format)
    sig = signature(yyzcz__jrq, df_type, cname_type, arr_type)
    return sig, codegen


@lower_constant(DataFrameType)
def lower_constant_dataframe(context, builder, df_type, pyval):
    check_runtime_cols_unsupported(df_type, 'lowering a constant DataFrame')
    orksi__xybue = len(pyval.columns)
    uepwo__yrdn = []
    for i in range(orksi__xybue):
        bbho__xiu = pyval.iloc[:, i]
        if isinstance(df_type.data[i], bodo.DatetimeArrayType):
            uehgg__yyo = bbho__xiu.array
        else:
            uehgg__yyo = bbho__xiu.values
        uepwo__yrdn.append(uehgg__yyo)
    uepwo__yrdn = tuple(uepwo__yrdn)
    if df_type.is_table_format:
        ctrzt__srat = context.get_constant_generic(builder, df_type.
            table_type, Table(uepwo__yrdn))
        data_tup = lir.Constant.literal_struct([ctrzt__srat])
    else:
        data_tup = lir.Constant.literal_struct([context.
            get_constant_generic(builder, df_type.data[i], ungoi__eijx) for
            i, ungoi__eijx in enumerate(uepwo__yrdn)])
    index_val = context.get_constant_generic(builder, df_type.index, pyval.
        index)
    uid__qcldw = context.get_constant_null(types.pyobject)
    payload = lir.Constant.literal_struct([data_tup, index_val, uid__qcldw])
    payload = cgutils.global_constant(builder, '.const.payload', payload
        ).bitcast(cgutils.voidptr_t)
    ihtbn__lcdet = context.get_constant(types.int64, -1)
    hfs__sxgeo = context.get_constant_null(types.voidptr)
    woohu__fdir = lir.Constant.literal_struct([ihtbn__lcdet, hfs__sxgeo,
        hfs__sxgeo, payload, ihtbn__lcdet])
    woohu__fdir = cgutils.global_constant(builder, '.const.meminfo',
        woohu__fdir).bitcast(cgutils.voidptr_t)
    return lir.Constant.literal_struct([woohu__fdir, uid__qcldw])


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
        nfjw__fka = context.cast(builder, in_dataframe_payload.index,
            fromty.index, toty.index)
    else:
        nfjw__fka = in_dataframe_payload.index
        context.nrt.incref(builder, fromty.index, nfjw__fka)
    if (fromty.is_table_format == toty.is_table_format and fromty.data ==
        toty.data):
        gfxxp__rvgrh = in_dataframe_payload.data
        if fromty.is_table_format:
            context.nrt.incref(builder, types.Tuple([fromty.table_type]),
                gfxxp__rvgrh)
        else:
            context.nrt.incref(builder, types.BaseTuple.from_types(fromty.
                data), gfxxp__rvgrh)
    elif not fromty.is_table_format and toty.is_table_format:
        gfxxp__rvgrh = _cast_df_data_to_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and not toty.is_table_format:
        gfxxp__rvgrh = _cast_df_data_to_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    elif fromty.is_table_format and toty.is_table_format:
        gfxxp__rvgrh = _cast_df_data_keep_table_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    else:
        gfxxp__rvgrh = _cast_df_data_keep_tuple_format(context, builder,
            fromty, toty, val, in_dataframe_payload)
    return construct_dataframe(context, builder, toty, gfxxp__rvgrh,
        nfjw__fka, in_dataframe_payload.parent, None)


def _cast_empty_df(context, builder, toty):
    kydo__qti = {}
    if isinstance(toty.index, RangeIndexType):
        index = 'bodo.hiframes.pd_index_ext.init_range_index(0, 0, 1, None)'
    else:
        xzr__vnka = get_index_data_arr_types(toty.index)[0]
        ajs__hvxi = bodo.utils.transform.get_type_alloc_counts(xzr__vnka) - 1
        wswps__wrt = ', '.join('0' for wii__yntg in range(ajs__hvxi))
        index = (
            'bodo.utils.conversion.index_from_array(bodo.utils.utils.alloc_type(0, index_arr_type, ({}{})))'
            .format(wswps__wrt, ', ' if ajs__hvxi == 1 else ''))
        kydo__qti['index_arr_type'] = xzr__vnka
    fcj__wss = []
    for i, arr_typ in enumerate(toty.data):
        ajs__hvxi = bodo.utils.transform.get_type_alloc_counts(arr_typ) - 1
        wswps__wrt = ', '.join('0' for wii__yntg in range(ajs__hvxi))
        qlrd__tkvg = ('bodo.utils.utils.alloc_type(0, arr_type{}, ({}{}))'.
            format(i, wswps__wrt, ', ' if ajs__hvxi == 1 else ''))
        fcj__wss.append(qlrd__tkvg)
        kydo__qti[f'arr_type{i}'] = arr_typ
    fcj__wss = ', '.join(fcj__wss)
    kuxhv__fgg = 'def impl():\n'
    bih__bgd = bodo.hiframes.dataframe_impl._gen_init_df(kuxhv__fgg, toty.
        columns, fcj__wss, index, kydo__qti)
    df = context.compile_internal(builder, bih__bgd, toty(), [])
    return df


def _cast_df_data_to_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame to table format')
    ukdp__ncz = toty.table_type
    ctrzt__srat = cgutils.create_struct_proxy(ukdp__ncz)(context, builder)
    ctrzt__srat.parent = in_dataframe_payload.parent
    for lkngw__iihea, vfs__ifgw in ukdp__ncz.type_to_blk.items():
        gwu__xxax = context.get_constant(types.int64, len(ukdp__ncz.
            block_to_arr_ind[vfs__ifgw]))
        wii__yntg, rxjl__lrvfe = ListInstance.allocate_ex(context, builder,
            types.List(lkngw__iihea), gwu__xxax)
        rxjl__lrvfe.size = gwu__xxax
        setattr(ctrzt__srat, f'block_{vfs__ifgw}', rxjl__lrvfe.value)
    for i, lkngw__iihea in enumerate(fromty.data):
        tcj__qvgp = toty.data[i]
        if lkngw__iihea != tcj__qvgp:
            ouuvc__qha = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ouuvc__qha)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        kvbk__jiq = builder.extract_value(in_dataframe_payload.data, i)
        if lkngw__iihea != tcj__qvgp:
            wpska__maz = context.cast(builder, kvbk__jiq, lkngw__iihea,
                tcj__qvgp)
            jibb__mvvi = False
        else:
            wpska__maz = kvbk__jiq
            jibb__mvvi = True
        vfs__ifgw = ukdp__ncz.type_to_blk[lkngw__iihea]
        xzy__fvvg = getattr(ctrzt__srat, f'block_{vfs__ifgw}')
        tna__feqj = ListInstance(context, builder, types.List(lkngw__iihea),
            xzy__fvvg)
        abtx__qahu = context.get_constant(types.int64, ukdp__ncz.
            block_offsets[i])
        tna__feqj.setitem(abtx__qahu, wpska__maz, jibb__mvvi)
    data_tup = context.make_tuple(builder, types.Tuple([ukdp__ncz]), [
        ctrzt__srat._getvalue()])
    return data_tup


def _cast_df_data_keep_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting traditional DataFrame columns')
    uepwo__yrdn = []
    for i in range(len(fromty.data)):
        if fromty.data[i] != toty.data[i]:
            ouuvc__qha = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ouuvc__qha)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
            kvbk__jiq = builder.extract_value(in_dataframe_payload.data, i)
            wpska__maz = context.cast(builder, kvbk__jiq, fromty.data[i],
                toty.data[i])
            jibb__mvvi = False
        else:
            wpska__maz = builder.extract_value(in_dataframe_payload.data, i)
            jibb__mvvi = True
        if jibb__mvvi:
            context.nrt.incref(builder, toty.data[i], wpska__maz)
        uepwo__yrdn.append(wpska__maz)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), uepwo__yrdn)
    return data_tup


def _cast_df_data_keep_table_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(toty,
        'casting table format DataFrame columns')
    roniq__jce = fromty.table_type
    nylyj__jmoj = cgutils.create_struct_proxy(roniq__jce)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    qthjs__tbeg = toty.table_type
    ozuzg__fxum = cgutils.create_struct_proxy(qthjs__tbeg)(context, builder)
    ozuzg__fxum.parent = in_dataframe_payload.parent
    for lkngw__iihea, vfs__ifgw in qthjs__tbeg.type_to_blk.items():
        gwu__xxax = context.get_constant(types.int64, len(qthjs__tbeg.
            block_to_arr_ind[vfs__ifgw]))
        wii__yntg, rxjl__lrvfe = ListInstance.allocate_ex(context, builder,
            types.List(lkngw__iihea), gwu__xxax)
        rxjl__lrvfe.size = gwu__xxax
        setattr(ozuzg__fxum, f'block_{vfs__ifgw}', rxjl__lrvfe.value)
    for i in range(len(fromty.data)):
        luf__wlt = fromty.data[i]
        tcj__qvgp = toty.data[i]
        if luf__wlt != tcj__qvgp:
            ouuvc__qha = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ouuvc__qha)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        ietr__wgto = roniq__jce.type_to_blk[luf__wlt]
        mytt__hdqd = getattr(nylyj__jmoj, f'block_{ietr__wgto}')
        pjdx__buvor = ListInstance(context, builder, types.List(luf__wlt),
            mytt__hdqd)
        gks__tab = context.get_constant(types.int64, roniq__jce.
            block_offsets[i])
        kvbk__jiq = pjdx__buvor.getitem(gks__tab)
        if luf__wlt != tcj__qvgp:
            wpska__maz = context.cast(builder, kvbk__jiq, luf__wlt, tcj__qvgp)
            jibb__mvvi = False
        else:
            wpska__maz = kvbk__jiq
            jibb__mvvi = True
        gmk__xmm = qthjs__tbeg.type_to_blk[lkngw__iihea]
        rxjl__lrvfe = getattr(ozuzg__fxum, f'block_{gmk__xmm}')
        cyd__tpyz = ListInstance(context, builder, types.List(tcj__qvgp),
            rxjl__lrvfe)
        eyxzb__zkq = context.get_constant(types.int64, qthjs__tbeg.
            block_offsets[i])
        cyd__tpyz.setitem(eyxzb__zkq, wpska__maz, jibb__mvvi)
    data_tup = context.make_tuple(builder, types.Tuple([qthjs__tbeg]), [
        ozuzg__fxum._getvalue()])
    return data_tup


def _cast_df_data_to_tuple_format(context, builder, fromty, toty, df,
    in_dataframe_payload):
    check_runtime_cols_unsupported(fromty,
        'casting table format to traditional DataFrame')
    ukdp__ncz = fromty.table_type
    ctrzt__srat = cgutils.create_struct_proxy(ukdp__ncz)(context, builder,
        builder.extract_value(in_dataframe_payload.data, 0))
    uepwo__yrdn = []
    for i, lkngw__iihea in enumerate(toty.data):
        luf__wlt = fromty.data[i]
        if lkngw__iihea != luf__wlt:
            ouuvc__qha = fromty, types.literal(i)
            impl = lambda df, i: bodo.hiframes.boxing.unbox_col_if_needed(df, i
                )
            sig = types.none(*ouuvc__qha)
            args = df, context.get_constant(types.int64, i)
            context.compile_internal(builder, impl, sig, args)
        vfs__ifgw = ukdp__ncz.type_to_blk[lkngw__iihea]
        xzy__fvvg = getattr(ctrzt__srat, f'block_{vfs__ifgw}')
        tna__feqj = ListInstance(context, builder, types.List(lkngw__iihea),
            xzy__fvvg)
        abtx__qahu = context.get_constant(types.int64, ukdp__ncz.
            block_offsets[i])
        kvbk__jiq = tna__feqj.getitem(abtx__qahu)
        if lkngw__iihea != luf__wlt:
            wpska__maz = context.cast(builder, kvbk__jiq, luf__wlt,
                lkngw__iihea)
            jibb__mvvi = False
        else:
            wpska__maz = kvbk__jiq
            jibb__mvvi = True
        if jibb__mvvi:
            context.nrt.incref(builder, lkngw__iihea, wpska__maz)
        uepwo__yrdn.append(wpska__maz)
    data_tup = context.make_tuple(builder, types.Tuple(toty.data), uepwo__yrdn)
    return data_tup


@overload(pd.DataFrame, inline='always', no_unliteral=True)
def pd_dataframe_overload(data=None, index=None, columns=None, dtype=None,
    copy=False):
    if not is_overload_constant_bool(copy):
        raise BodoError(
            "pd.DataFrame(): 'copy' argument should be a constant boolean")
    copy = get_overload_const(copy)
    cjci__cyin, fcj__wss, index_arg = _get_df_args(data, index, columns,
        dtype, copy)
    espkz__wkhx = ColNamesMetaType(tuple(cjci__cyin))
    kuxhv__fgg = (
        'def _init_df(data=None, index=None, columns=None, dtype=None, copy=False):\n'
        )
    kuxhv__fgg += (
        """  return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, {}, __col_name_meta_value_pd_overload)
"""
        .format(fcj__wss, index_arg))
    vpxqv__kjm = {}
    exec(kuxhv__fgg, {'bodo': bodo, 'np': np,
        '__col_name_meta_value_pd_overload': espkz__wkhx}, vpxqv__kjm)
    tsj__msyoj = vpxqv__kjm['_init_df']
    return tsj__msyoj


@intrinsic
def _tuple_to_table_format_decoded(typingctx, df_typ):
    assert not df_typ.is_table_format, '_tuple_to_table_format requires a tuple format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    yyzcz__jrq = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=True)
    sig = signature(yyzcz__jrq, df_typ)
    return sig, codegen


@intrinsic
def _table_to_tuple_format_decoded(typingctx, df_typ):
    assert df_typ.is_table_format, '_tuple_to_table_format requires a table format input'

    def codegen(context, builder, signature, args):
        return context.cast(builder, args[0], signature.args[0], signature.
            return_type)
    yyzcz__jrq = DataFrameType(to_str_arr_if_dict_array(df_typ.data),
        df_typ.index, df_typ.columns, dist=df_typ.dist, is_table_format=False)
    sig = signature(yyzcz__jrq, df_typ)
    return sig, codegen


def _get_df_args(data, index, columns, dtype, copy):
    dxu__qpin = ''
    if not is_overload_none(dtype):
        dxu__qpin = '.astype(dtype)'
    index_is_none = is_overload_none(index)
    index_arg = 'bodo.utils.conversion.convert_to_index(index)'
    if isinstance(data, types.BaseTuple):
        if not data.types[0] == types.StringLiteral('__bodo_tup'):
            raise BodoError('pd.DataFrame tuple input data not supported yet')
        assert len(data.types) % 2 == 1, 'invalid const dict tuple structure'
        orksi__xybue = (len(data.types) - 1) // 2
        ixuuz__vno = [lkngw__iihea.literal_value for lkngw__iihea in data.
            types[1:orksi__xybue + 1]]
        data_val_types = dict(zip(ixuuz__vno, data.types[orksi__xybue + 1:]))
        uepwo__yrdn = ['data[{}]'.format(i) for i in range(orksi__xybue + 1,
            2 * orksi__xybue + 1)]
        data_dict = dict(zip(ixuuz__vno, uepwo__yrdn))
        if is_overload_none(index):
            for i, lkngw__iihea in enumerate(data.types[orksi__xybue + 1:]):
                if isinstance(lkngw__iihea, SeriesType):
                    index_arg = (
                        'bodo.hiframes.pd_series_ext.get_series_index(data[{}])'
                        .format(orksi__xybue + 1 + i))
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
        zldy__pygb = '.copy()' if copy else ''
        rmgih__chvm = get_overload_const_list(columns)
        orksi__xybue = len(rmgih__chvm)
        data_val_types = {tvwg__mzshd: data.copy(ndim=1) for tvwg__mzshd in
            rmgih__chvm}
        uepwo__yrdn = ['data[:,{}]{}'.format(i, zldy__pygb) for i in range(
            orksi__xybue)]
        data_dict = dict(zip(rmgih__chvm, uepwo__yrdn))
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
    fcj__wss = '({},)'.format(', '.join(
        'bodo.utils.conversion.coerce_to_array({}, True, scalar_to_arr_len={}){}'
        .format(data_dict[tvwg__mzshd], df_len, dxu__qpin) for tvwg__mzshd in
        col_names))
    if len(col_names) == 0:
        fcj__wss = '()'
    return col_names, fcj__wss, index_arg


def _get_df_len_from_info(data_dict, data_val_types, col_names,
    index_is_none, index_arg):
    df_len = '0'
    for tvwg__mzshd in col_names:
        if tvwg__mzshd in data_dict and is_iterable_type(data_val_types[
            tvwg__mzshd]):
            df_len = 'len({})'.format(data_dict[tvwg__mzshd])
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
    if all(tvwg__mzshd in data_dict for tvwg__mzshd in col_names):
        return
    if is_overload_none(dtype):
        dtype = 'bodo.string_array_type'
    else:
        dtype = 'bodo.utils.conversion.array_type_from_dtype(dtype)'
    dvjtn__jhxzb = 'bodo.libs.array_kernels.gen_na_array({}, {})'.format(df_len
        , dtype)
    for tvwg__mzshd in col_names:
        if tvwg__mzshd not in data_dict:
            data_dict[tvwg__mzshd] = dvjtn__jhxzb


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
            lkngw__iihea = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(
                df)
            return len(lkngw__iihea)
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
        amv__toksi = idx.literal_value
        if isinstance(amv__toksi, int):
            gipl__teum = tup.types[amv__toksi]
        elif isinstance(amv__toksi, slice):
            gipl__teum = types.BaseTuple.from_types(tup.types[amv__toksi])
        return signature(gipl__teum, *args)


GetItemTuple.prefer_literal = True


@lower_builtin(operator.getitem, types.BaseTuple, types.IntegerLiteral)
@lower_builtin(operator.getitem, types.BaseTuple, types.SliceLiteral)
def getitem_tuple_lower(context, builder, sig, args):
    sgub__lbal, idx = sig.args
    idx = idx.literal_value
    tup, wii__yntg = args
    if isinstance(idx, int):
        if idx < 0:
            idx += len(sgub__lbal)
        if not 0 <= idx < len(sgub__lbal):
            raise IndexError('cannot index at %d in %s' % (idx, sgub__lbal))
        hlxzm__qmxfb = builder.extract_value(tup, idx)
    elif isinstance(idx, slice):
        seml__ole = cgutils.unpack_tuple(builder, tup)[idx]
        hlxzm__qmxfb = context.make_tuple(builder, sig.return_type, seml__ole)
    else:
        raise NotImplementedError('unexpected index %r for %s' % (idx, sig.
            args[0]))
    return impl_ret_borrowed(context, builder, sig.return_type, hlxzm__qmxfb)


def join_dummy(left_df, right_df, left_on, right_on, how, suffix_x,
    suffix_y, is_join, indicator, _bodo_na_equal, gen_cond):
    return left_df


@infer_global(join_dummy)
class JoinTyper(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        from bodo.utils.typing import is_overload_str
        assert not kws
        (left_df, right_df, left_on, right_on, txykn__pqy, suffix_x,
            suffix_y, is_join, indicator, wii__yntg, wii__yntg) = args
        left_on = get_overload_const_list(left_on)
        right_on = get_overload_const_list(right_on)
        uil__oujuh = {tvwg__mzshd: i for i, tvwg__mzshd in enumerate(left_on)}
        zgz__fwk = {tvwg__mzshd: i for i, tvwg__mzshd in enumerate(right_on)}
        akhiv__eeh = set(left_on) & set(right_on)
        vevv__vdp = set(left_df.columns) & set(right_df.columns)
        dzx__esvlv = vevv__vdp - akhiv__eeh
        gurg__ljt = '$_bodo_index_' in left_on
        eyb__xqeha = '$_bodo_index_' in right_on
        how = get_overload_const_str(txykn__pqy)
        wqfnr__nrho = how in {'left', 'outer'}
        jxi__azddb = how in {'right', 'outer'}
        columns = []
        data = []
        if gurg__ljt:
            ljz__gxaa = bodo.utils.typing.get_index_data_arr_types(left_df.
                index)[0]
        else:
            ljz__gxaa = left_df.data[left_df.column_index[left_on[0]]]
        if eyb__xqeha:
            yblh__jxyhx = bodo.utils.typing.get_index_data_arr_types(right_df
                .index)[0]
        else:
            yblh__jxyhx = right_df.data[right_df.column_index[right_on[0]]]
        if gurg__ljt and not eyb__xqeha and not is_join.literal_value:
            ruyqp__jbyo = right_on[0]
            if ruyqp__jbyo in left_df.column_index:
                columns.append(ruyqp__jbyo)
                if (yblh__jxyhx == bodo.dict_str_arr_type and ljz__gxaa ==
                    bodo.string_array_type):
                    ykx__sqc = bodo.string_array_type
                else:
                    ykx__sqc = yblh__jxyhx
                data.append(ykx__sqc)
        if eyb__xqeha and not gurg__ljt and not is_join.literal_value:
            jaz__emg = left_on[0]
            if jaz__emg in right_df.column_index:
                columns.append(jaz__emg)
                if (ljz__gxaa == bodo.dict_str_arr_type and yblh__jxyhx ==
                    bodo.string_array_type):
                    ykx__sqc = bodo.string_array_type
                else:
                    ykx__sqc = ljz__gxaa
                data.append(ykx__sqc)
        for luf__wlt, bbho__xiu in zip(left_df.data, left_df.columns):
            columns.append(str(bbho__xiu) + suffix_x.literal_value if 
                bbho__xiu in dzx__esvlv else bbho__xiu)
            if bbho__xiu in akhiv__eeh:
                if luf__wlt == bodo.dict_str_arr_type:
                    luf__wlt = right_df.data[right_df.column_index[bbho__xiu]]
                data.append(luf__wlt)
            else:
                if (luf__wlt == bodo.dict_str_arr_type and bbho__xiu in
                    uil__oujuh):
                    if eyb__xqeha:
                        luf__wlt = yblh__jxyhx
                    else:
                        oha__bfb = uil__oujuh[bbho__xiu]
                        jou__tbp = right_on[oha__bfb]
                        luf__wlt = right_df.data[right_df.column_index[
                            jou__tbp]]
                if jxi__azddb:
                    luf__wlt = to_nullable_type(luf__wlt)
                data.append(luf__wlt)
        for luf__wlt, bbho__xiu in zip(right_df.data, right_df.columns):
            if bbho__xiu not in akhiv__eeh:
                columns.append(str(bbho__xiu) + suffix_y.literal_value if 
                    bbho__xiu in dzx__esvlv else bbho__xiu)
                if (luf__wlt == bodo.dict_str_arr_type and bbho__xiu in
                    zgz__fwk):
                    if gurg__ljt:
                        luf__wlt = ljz__gxaa
                    else:
                        oha__bfb = zgz__fwk[bbho__xiu]
                        biobq__jzmr = left_on[oha__bfb]
                        luf__wlt = left_df.data[left_df.column_index[
                            biobq__jzmr]]
                if wqfnr__nrho:
                    luf__wlt = to_nullable_type(luf__wlt)
                data.append(luf__wlt)
        tss__rscsf = get_overload_const_bool(indicator)
        if tss__rscsf:
            columns.append('_merge')
            data.append(bodo.CategoricalArrayType(bodo.PDCategoricalDtype((
                'left_only', 'right_only', 'both'), bodo.string_type, False)))
        index_typ = RangeIndexType(types.none)
        myhl__gmdko = False
        if gurg__ljt and eyb__xqeha and not is_overload_str(how, 'asof'):
            index_typ = left_df.index
            myhl__gmdko = True
        elif gurg__ljt and not eyb__xqeha:
            index_typ = right_df.index
            myhl__gmdko = True
        elif eyb__xqeha and not gurg__ljt:
            index_typ = left_df.index
            myhl__gmdko = True
        if myhl__gmdko and isinstance(index_typ, bodo.hiframes.pd_index_ext
            .RangeIndexType):
            index_typ = bodo.hiframes.pd_index_ext.NumericIndexType(types.int64
                )
        wrtj__rka = DataFrameType(tuple(data), index_typ, tuple(columns),
            is_table_format=True)
        return signature(wrtj__rka, *args)


JoinTyper._no_unliteral = True


@lower_builtin(join_dummy, types.VarArg(types.Any))
def lower_join_dummy(context, builder, sig, args):
    zfxu__pau = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return zfxu__pau._getvalue()


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
    emwmw__fwkhm = dict(join=join, join_axes=join_axes, keys=keys, levels=
        levels, names=names, verify_integrity=verify_integrity, sort=sort,
        copy=copy)
    qvst__jyw = dict(join='outer', join_axes=None, keys=None, levels=None,
        names=None, verify_integrity=False, sort=None, copy=True)
    check_unsupported_args('pandas.concat', emwmw__fwkhm, qvst__jyw,
        package_name='pandas', module_name='General')
    kuxhv__fgg = """def impl(objs, axis=0, join='outer', join_axes=None, ignore_index=False, keys=None, levels=None, names=None, verify_integrity=False, sort=None, copy=True):
"""
    if axis == 1:
        if not isinstance(objs, types.BaseTuple):
            raise_bodo_error(
                'Only tuple argument for pd.concat(axis=1) expected')
        index = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len(objs[0]), 1, None)'
            )
        myn__knqg = 0
        fcj__wss = []
        names = []
        for i, ltb__ldjqj in enumerate(objs.types):
            assert isinstance(ltb__ldjqj, (SeriesType, DataFrameType))
            check_runtime_cols_unsupported(ltb__ldjqj, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                ltb__ldjqj, 'pandas.concat()')
            if isinstance(ltb__ldjqj, SeriesType):
                names.append(str(myn__knqg))
                myn__knqg += 1
                fcj__wss.append(
                    'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'
                    .format(i))
            else:
                names.extend(ltb__ldjqj.columns)
                for zaq__nhr in range(len(ltb__ldjqj.data)):
                    fcj__wss.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, zaq__nhr))
        return bodo.hiframes.dataframe_impl._gen_init_df(kuxhv__fgg, names,
            ', '.join(fcj__wss), index)
    if axis != 0:
        raise_bodo_error('pd.concat(): axis must be 0 or 1')
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        DataFrameType):
        assert all(isinstance(lkngw__iihea, DataFrameType) for lkngw__iihea in
            objs.types)
        tvdy__cqntw = []
        for df in objs.types:
            check_runtime_cols_unsupported(df, 'pandas.concat()')
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df,
                'pandas.concat()')
            tvdy__cqntw.extend(df.columns)
        tvdy__cqntw = list(dict.fromkeys(tvdy__cqntw).keys())
        kodf__dgdx = {}
        for myn__knqg, tvwg__mzshd in enumerate(tvdy__cqntw):
            for i, df in enumerate(objs.types):
                if tvwg__mzshd in df.column_index:
                    kodf__dgdx[f'arr_typ{myn__knqg}'] = df.data[df.
                        column_index[tvwg__mzshd]]
                    break
        assert len(kodf__dgdx) == len(tvdy__cqntw)
        aggc__zhyk = []
        for myn__knqg, tvwg__mzshd in enumerate(tvdy__cqntw):
            args = []
            for i, df in enumerate(objs.types):
                if tvwg__mzshd in df.column_index:
                    yuzeb__juz = df.column_index[tvwg__mzshd]
                    args.append(
                        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(objs[{}], {})'
                        .format(i, yuzeb__juz))
                else:
                    args.append(
                        'bodo.libs.array_kernels.gen_na_array(len(objs[{}]), arr_typ{})'
                        .format(i, myn__knqg))
            kuxhv__fgg += ('  A{} = bodo.libs.array_kernels.concat(({},))\n'
                .format(myn__knqg, ', '.join(args)))
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
        return bodo.hiframes.dataframe_impl._gen_init_df(kuxhv__fgg,
            tvdy__cqntw, ', '.join('A{}'.format(i) for i in range(len(
            tvdy__cqntw))), index, kodf__dgdx)
    if isinstance(objs, types.BaseTuple) and isinstance(objs.types[0],
        SeriesType):
        assert all(isinstance(lkngw__iihea, SeriesType) for lkngw__iihea in
            objs.types)
        kuxhv__fgg += ('  out_arr = bodo.libs.array_kernels.concat(({},))\n'
            .format(', '.join(
            'bodo.hiframes.pd_series_ext.get_series_data(objs[{}])'.format(
            i) for i in range(len(objs.types)))))
        if ignore_index:
            kuxhv__fgg += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            kuxhv__fgg += (
                """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(({},)))
"""
                .format(', '.join(
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(objs[{}]))'
                .format(i) for i in range(len(objs.types)))))
        kuxhv__fgg += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        vpxqv__kjm = {}
        exec(kuxhv__fgg, {'bodo': bodo, 'np': np, 'numba': numba}, vpxqv__kjm)
        return vpxqv__kjm['impl']
    if isinstance(objs, types.List) and isinstance(objs.dtype, DataFrameType):
        check_runtime_cols_unsupported(objs.dtype, 'pandas.concat()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(objs.
            dtype, 'pandas.concat()')
        df_type = objs.dtype
        for myn__knqg, tvwg__mzshd in enumerate(df_type.columns):
            kuxhv__fgg += '  arrs{} = []\n'.format(myn__knqg)
            kuxhv__fgg += '  for i in range(len(objs)):\n'
            kuxhv__fgg += '    df = objs[i]\n'
            kuxhv__fgg += (
                """    arrs{0}.append(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0}))
"""
                .format(myn__knqg))
            kuxhv__fgg += (
                '  out_arr{0} = bodo.libs.array_kernels.concat(arrs{0})\n'.
                format(myn__knqg))
        if ignore_index:
            index = (
                'bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr0), 1, None)'
                )
        else:
            kuxhv__fgg += '  arrs_index = []\n'
            kuxhv__fgg += '  for i in range(len(objs)):\n'
            kuxhv__fgg += '    df = objs[i]\n'
            kuxhv__fgg += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
            if objs.dtype.index.name_typ == types.none:
                name = None
            else:
                name = objs.dtype.index.name_typ.literal_value
            index = f"""bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index), {name!r})
"""
        return bodo.hiframes.dataframe_impl._gen_init_df(kuxhv__fgg,
            df_type.columns, ', '.join('out_arr{}'.format(i) for i in range
            (len(df_type.columns))), index)
    if isinstance(objs, types.List) and isinstance(objs.dtype, SeriesType):
        kuxhv__fgg += '  arrs = []\n'
        kuxhv__fgg += '  for i in range(len(objs)):\n'
        kuxhv__fgg += (
            '    arrs.append(bodo.hiframes.pd_series_ext.get_series_data(objs[i]))\n'
            )
        kuxhv__fgg += '  out_arr = bodo.libs.array_kernels.concat(arrs)\n'
        if ignore_index:
            kuxhv__fgg += """  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(out_arr), 1, None)
"""
        else:
            kuxhv__fgg += '  arrs_index = []\n'
            kuxhv__fgg += '  for i in range(len(objs)):\n'
            kuxhv__fgg += '    S = objs[i]\n'
            kuxhv__fgg += """    arrs_index.append(bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S)))
"""
            kuxhv__fgg += """  index = bodo.utils.conversion.index_from_array(bodo.libs.array_kernels.concat(arrs_index))
"""
        kuxhv__fgg += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index)\n'
            )
        vpxqv__kjm = {}
        exec(kuxhv__fgg, {'bodo': bodo, 'np': np, 'numba': numba}, vpxqv__kjm)
        return vpxqv__kjm['impl']
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
        yyzcz__jrq = df.copy(index=index)
        return signature(yyzcz__jrq, *args)


SortDummyTyper._no_unliteral = True


@lower_builtin(sort_values_dummy, types.VarArg(types.Any))
def lower_sort_values_dummy(context, builder, sig, args):
    if sig.return_type == types.none:
        return
    lzsp__scn = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return lzsp__scn._getvalue()


@overload_method(DataFrameType, 'itertuples', inline='always', no_unliteral
    =True)
def itertuples_overload(df, index=True, name='Pandas'):
    check_runtime_cols_unsupported(df, 'DataFrame.itertuples()')
    emwmw__fwkhm = dict(index=index, name=name)
    qvst__jyw = dict(index=True, name='Pandas')
    check_unsupported_args('DataFrame.itertuples', emwmw__fwkhm, qvst__jyw,
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
        kodf__dgdx = (types.Array(types.int64, 1, 'C'),) + df.data
        txob__viw = bodo.hiframes.dataframe_impl.DataFrameTupleIterator(columns
            , kodf__dgdx)
        return signature(txob__viw, *args)


@lower_builtin(itertuples_dummy, types.VarArg(types.Any))
def lower_itertuples_dummy(context, builder, sig, args):
    lzsp__scn = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return lzsp__scn._getvalue()


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
    lzsp__scn = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return lzsp__scn._getvalue()


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
    lzsp__scn = cgutils.create_struct_proxy(sig.return_type)(context, builder)
    return lzsp__scn._getvalue()


@numba.generated_jit(nopython=True)
def pivot_impl(index_tup, columns_tup, values_tup, pivot_values,
    index_names, columns_name, value_names, check_duplicates=True,
    _constant_pivot_values=None, parallel=False):
    if not is_overload_constant_bool(check_duplicates):
        raise BodoError(
            'pivot_impl(): check_duplicates must be a constant boolean')
    uglw__zsx = get_overload_const_bool(check_duplicates)
    oxram__jfj = not is_overload_none(_constant_pivot_values)
    index_names = index_names.instance_type if isinstance(index_names,
        types.TypeRef) else index_names
    columns_name = columns_name.instance_type if isinstance(columns_name,
        types.TypeRef) else columns_name
    value_names = value_names.instance_type if isinstance(value_names,
        types.TypeRef) else value_names
    _constant_pivot_values = (_constant_pivot_values.instance_type if
        isinstance(_constant_pivot_values, types.TypeRef) else
        _constant_pivot_values)
    lrfec__qlq = len(value_names) > 1
    cvjrf__hpmb = None
    kkx__fqkgc = None
    ulkaw__ykq = None
    lhc__cmwzm = None
    gzs__iet = isinstance(values_tup, types.UniTuple)
    if gzs__iet:
        zldhd__xrh = [to_str_arr_if_dict_array(to_nullable_type(values_tup.
            dtype))]
    else:
        zldhd__xrh = [to_str_arr_if_dict_array(to_nullable_type(zuah__hlqmj
            )) for zuah__hlqmj in values_tup]
    kuxhv__fgg = 'def impl(\n'
    kuxhv__fgg += """    index_tup, columns_tup, values_tup, pivot_values, index_names, columns_name, value_names, check_duplicates=True, _constant_pivot_values=None, parallel=False
"""
    kuxhv__fgg += '):\n'
    kuxhv__fgg += '    if parallel:\n'
    tjvb__mtxpl = ', '.join([f'array_to_info(index_tup[{i}])' for i in
        range(len(index_tup))] + [f'array_to_info(columns_tup[{i}])' for i in
        range(len(columns_tup))] + [f'array_to_info(values_tup[{i}])' for i in
        range(len(values_tup))])
    kuxhv__fgg += f'        info_list = [{tjvb__mtxpl}]\n'
    kuxhv__fgg += '        cpp_table = arr_info_list_to_table(info_list)\n'
    kuxhv__fgg += f"""        out_cpp_table = shuffle_table(cpp_table, {len(index_tup)}, parallel, 0)
"""
    pwiu__iyot = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i}), index_tup[{i}])'
         for i in range(len(index_tup))])
    wgo__vaea = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup)}), columns_tup[{i}])'
         for i in range(len(columns_tup))])
    zlggy__cffdn = ', '.join([
        f'info_to_array(info_from_table(out_cpp_table, {i + len(index_tup) + len(columns_tup)}), values_tup[{i}])'
         for i in range(len(values_tup))])
    kuxhv__fgg += f'        index_tup = ({pwiu__iyot},)\n'
    kuxhv__fgg += f'        columns_tup = ({wgo__vaea},)\n'
    kuxhv__fgg += f'        values_tup = ({zlggy__cffdn},)\n'
    kuxhv__fgg += '        delete_table(cpp_table)\n'
    kuxhv__fgg += '        delete_table(out_cpp_table)\n'
    kuxhv__fgg += '    columns_arr = columns_tup[0]\n'
    if gzs__iet:
        kuxhv__fgg += '    values_arrs = [arr for arr in values_tup]\n'
    ytg__hicgh = ', '.join([
        f'bodo.utils.typing.decode_if_dict_array(index_tup[{i}])' for i in
        range(len(index_tup))])
    kuxhv__fgg += f'    new_index_tup = ({ytg__hicgh},)\n'
    kuxhv__fgg += """    unique_index_arr_tup, row_vector = bodo.libs.array_ops.array_unique_vector_map(
"""
    kuxhv__fgg += '        new_index_tup\n'
    kuxhv__fgg += '    )\n'
    kuxhv__fgg += '    n_rows = len(unique_index_arr_tup[0])\n'
    kuxhv__fgg += '    num_values_arrays = len(values_tup)\n'
    kuxhv__fgg += '    n_unique_pivots = len(pivot_values)\n'
    if gzs__iet:
        kuxhv__fgg += '    n_cols = num_values_arrays * n_unique_pivots\n'
    else:
        kuxhv__fgg += '    n_cols = n_unique_pivots\n'
    kuxhv__fgg += '    col_map = {}\n'
    kuxhv__fgg += '    for i in range(n_unique_pivots):\n'
    kuxhv__fgg += '        if bodo.libs.array_kernels.isna(pivot_values, i):\n'
    kuxhv__fgg += '            raise ValueError(\n'
    kuxhv__fgg += """                "DataFrame.pivot(): NA values in 'columns' array not supported\"
"""
    kuxhv__fgg += '            )\n'
    kuxhv__fgg += '        col_map[pivot_values[i]] = i\n'
    uwt__fiu = False
    for i, noo__xrihz in enumerate(zldhd__xrh):
        if is_str_arr_type(noo__xrihz):
            uwt__fiu = True
            kuxhv__fgg += f"""    len_arrs_{i} = [np.zeros(n_rows, np.int64) for _ in range(n_cols)]
"""
            kuxhv__fgg += f'    total_lens_{i} = np.zeros(n_cols, np.int64)\n'
    if uwt__fiu:
        if uglw__zsx:
            kuxhv__fgg += '    nbytes = (n_rows + 7) >> 3\n'
            kuxhv__fgg += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
        kuxhv__fgg += '    for i in range(len(columns_arr)):\n'
        kuxhv__fgg += '        col_name = columns_arr[i]\n'
        kuxhv__fgg += '        pivot_idx = col_map[col_name]\n'
        kuxhv__fgg += '        row_idx = row_vector[i]\n'
        if uglw__zsx:
            kuxhv__fgg += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
            kuxhv__fgg += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
            kuxhv__fgg += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
            kuxhv__fgg += '        else:\n'
            kuxhv__fgg += """            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)
"""
        if gzs__iet:
            kuxhv__fgg += '        for j in range(num_values_arrays):\n'
            kuxhv__fgg += (
                '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
            kuxhv__fgg += '            len_arr = len_arrs_0[col_idx]\n'
            kuxhv__fgg += '            values_arr = values_arrs[j]\n'
            kuxhv__fgg += (
                '            if not bodo.libs.array_kernels.isna(values_arr, i):\n'
                )
            kuxhv__fgg += """                str_val_len = bodo.libs.str_arr_ext.get_str_arr_item_length(values_arr, i)
"""
            kuxhv__fgg += '                len_arr[row_idx] = str_val_len\n'
            kuxhv__fgg += (
                '                total_lens_0[col_idx] += str_val_len\n')
        else:
            for i, noo__xrihz in enumerate(zldhd__xrh):
                if is_str_arr_type(noo__xrihz):
                    kuxhv__fgg += f"""        if not bodo.libs.array_kernels.isna(values_tup[{i}], i):
"""
                    kuxhv__fgg += f"""            str_val_len_{i} = bodo.libs.str_arr_ext.get_str_arr_item_length(values_tup[{i}], i)
"""
                    kuxhv__fgg += f"""            len_arrs_{i}[pivot_idx][row_idx] = str_val_len_{i}
"""
                    kuxhv__fgg += (
                        f'            total_lens_{i}[pivot_idx] += str_val_len_{i}\n'
                        )
    for i, noo__xrihz in enumerate(zldhd__xrh):
        if is_str_arr_type(noo__xrihz):
            kuxhv__fgg += f'    data_arrs_{i} = [\n'
            kuxhv__fgg += (
                '        bodo.libs.str_arr_ext.gen_na_str_array_lens(\n')
            kuxhv__fgg += (
                f'            n_rows, total_lens_{i}[i], len_arrs_{i}[i]\n')
            kuxhv__fgg += '        )\n'
            kuxhv__fgg += '        for i in range(n_cols)\n'
            kuxhv__fgg += '    ]\n'
        else:
            kuxhv__fgg += f'    data_arrs_{i} = [\n'
            kuxhv__fgg += f"""        bodo.libs.array_kernels.gen_na_array(n_rows, data_arr_typ_{i})
"""
            kuxhv__fgg += '        for _ in range(n_cols)\n'
            kuxhv__fgg += '    ]\n'
    if not uwt__fiu and uglw__zsx:
        kuxhv__fgg += '    nbytes = (n_rows + 7) >> 3\n'
        kuxhv__fgg += """    seen_bitmaps = [np.zeros(nbytes, np.int8) for _ in range(n_unique_pivots)]
"""
    kuxhv__fgg += '    for i in range(len(columns_arr)):\n'
    kuxhv__fgg += '        col_name = columns_arr[i]\n'
    kuxhv__fgg += '        pivot_idx = col_map[col_name]\n'
    kuxhv__fgg += '        row_idx = row_vector[i]\n'
    if not uwt__fiu and uglw__zsx:
        kuxhv__fgg += '        seen_bitmap = seen_bitmaps[pivot_idx]\n'
        kuxhv__fgg += """        if bodo.libs.int_arr_ext.get_bit_bitmap_arr(seen_bitmap, row_idx):
"""
        kuxhv__fgg += """            raise ValueError("DataFrame.pivot(): 'index' contains duplicate entries for the same output column")
"""
        kuxhv__fgg += '        else:\n'
        kuxhv__fgg += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(seen_bitmap, row_idx, 1)\n'
            )
    if gzs__iet:
        kuxhv__fgg += '        for j in range(num_values_arrays):\n'
        kuxhv__fgg += (
            '            col_idx = (j * len(pivot_values)) + pivot_idx\n')
        kuxhv__fgg += '            col_arr = data_arrs_0[col_idx]\n'
        kuxhv__fgg += '            values_arr = values_arrs[j]\n'
        kuxhv__fgg += (
            '            if bodo.libs.array_kernels.isna(values_arr, i):\n')
        kuxhv__fgg += (
            '                bodo.libs.array_kernels.setna(col_arr, row_idx)\n'
            )
        kuxhv__fgg += '            else:\n'
        kuxhv__fgg += '                col_arr[row_idx] = values_arr[i]\n'
    else:
        for i, noo__xrihz in enumerate(zldhd__xrh):
            kuxhv__fgg += f'        col_arr_{i} = data_arrs_{i}[pivot_idx]\n'
            kuxhv__fgg += (
                f'        if bodo.libs.array_kernels.isna(values_tup[{i}], i):\n'
                )
            kuxhv__fgg += (
                f'            bodo.libs.array_kernels.setna(col_arr_{i}, row_idx)\n'
                )
            kuxhv__fgg += f'        else:\n'
            kuxhv__fgg += (
                f'            col_arr_{i}[row_idx] = values_tup[{i}][i]\n')
    if len(index_names) == 1:
        kuxhv__fgg += """    index = bodo.utils.conversion.index_from_array(unique_index_arr_tup[0], index_names_lit)
"""
        cvjrf__hpmb = index_names.meta[0]
    else:
        kuxhv__fgg += """    index = bodo.hiframes.pd_multi_index_ext.init_multi_index(unique_index_arr_tup, index_names_lit, None)
"""
        cvjrf__hpmb = tuple(index_names.meta)
    if not oxram__jfj:
        ulkaw__ykq = columns_name.meta[0]
        if lrfec__qlq:
            kuxhv__fgg += (
                f'    num_rows = {len(value_names)} * len(pivot_values)\n')
            kkx__fqkgc = value_names.meta
            if all(isinstance(tvwg__mzshd, str) for tvwg__mzshd in kkx__fqkgc):
                kkx__fqkgc = pd.array(kkx__fqkgc, 'string')
            elif all(isinstance(tvwg__mzshd, int) for tvwg__mzshd in kkx__fqkgc
                ):
                kkx__fqkgc = np.array(kkx__fqkgc, 'int64')
            else:
                raise BodoError(
                    f"pivot(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
                    )
            if isinstance(kkx__fqkgc.dtype, pd.StringDtype):
                kuxhv__fgg += '    total_chars = 0\n'
                kuxhv__fgg += f'    for i in range({len(value_names)}):\n'
                kuxhv__fgg += """        value_name_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(value_names_lit, i)
"""
                kuxhv__fgg += '        total_chars += value_name_str_len\n'
                kuxhv__fgg += """    new_value_names = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * len(pivot_values))
"""
            else:
                kuxhv__fgg += """    new_value_names = bodo.utils.utils.alloc_type(num_rows, value_names_lit, (-1,))
"""
            if is_str_arr_type(pivot_values):
                kuxhv__fgg += '    total_chars = 0\n'
                kuxhv__fgg += '    for i in range(len(pivot_values)):\n'
                kuxhv__fgg += """        pivot_val_str_len = bodo.libs.str_arr_ext.get_str_arr_item_length(pivot_values, i)
"""
                kuxhv__fgg += '        total_chars += pivot_val_str_len\n'
                kuxhv__fgg += f"""    new_pivot_values = bodo.libs.str_arr_ext.pre_alloc_string_array(num_rows, total_chars * {len(value_names)})
"""
            else:
                kuxhv__fgg += """    new_pivot_values = bodo.utils.utils.alloc_type(num_rows, pivot_values, (-1,))
"""
            kuxhv__fgg += f'    for i in range({len(value_names)}):\n'
            kuxhv__fgg += '        for j in range(len(pivot_values)):\n'
            kuxhv__fgg += """            new_value_names[(i * len(pivot_values)) + j] = value_names_lit[i]
"""
            kuxhv__fgg += """            new_pivot_values[(i * len(pivot_values)) + j] = pivot_values[j]
"""
            kuxhv__fgg += """    column_index = bodo.hiframes.pd_multi_index_ext.init_multi_index((new_value_names, new_pivot_values), (None, columns_name_lit), None)
"""
        else:
            kuxhv__fgg += """    column_index =  bodo.utils.conversion.index_from_array(pivot_values, columns_name_lit)
"""
    ukdp__ncz = None
    if oxram__jfj:
        if lrfec__qlq:
            vjmcy__hrlb = []
            for luq__sbzx in _constant_pivot_values.meta:
                for kjynm__zcy in value_names.meta:
                    vjmcy__hrlb.append((luq__sbzx, kjynm__zcy))
            column_names = tuple(vjmcy__hrlb)
        else:
            column_names = tuple(_constant_pivot_values.meta)
        lhc__cmwzm = ColNamesMetaType(column_names)
        khylu__hhgoo = []
        for zuah__hlqmj in zldhd__xrh:
            khylu__hhgoo.extend([zuah__hlqmj] * len(_constant_pivot_values))
        cug__odoj = tuple(khylu__hhgoo)
        ukdp__ncz = TableType(cug__odoj)
        kuxhv__fgg += (
            f'    table = bodo.hiframes.table.init_table(table_type, False)\n')
        kuxhv__fgg += (
            f'    table = bodo.hiframes.table.set_table_len(table, n_rows)\n')
        for i, zuah__hlqmj in enumerate(zldhd__xrh):
            kuxhv__fgg += f"""    table = bodo.hiframes.table.set_table_block(table, data_arrs_{i}, {ukdp__ncz.type_to_blk[zuah__hlqmj]})
"""
        kuxhv__fgg += (
            '    return bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
        kuxhv__fgg += '        (table,), index, columns_typ\n'
        kuxhv__fgg += '    )\n'
    else:
        kxdun__izgp = ', '.join(f'data_arrs_{i}' for i in range(len(
            zldhd__xrh)))
        kuxhv__fgg += f"""    table = bodo.hiframes.table.init_runtime_table_from_lists(({kxdun__izgp},), n_rows)
"""
        kuxhv__fgg += (
            '    return bodo.hiframes.pd_dataframe_ext.init_runtime_cols_dataframe(\n'
            )
        kuxhv__fgg += '        (table,), index, column_index\n'
        kuxhv__fgg += '    )\n'
    vpxqv__kjm = {}
    ujqbl__pki = {f'data_arr_typ_{i}': noo__xrihz for i, noo__xrihz in
        enumerate(zldhd__xrh)}
    bpto__gcoya = {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'info_from_table': info_from_table, 'table_type':
        ukdp__ncz, 'columns_typ': lhc__cmwzm, 'index_names_lit':
        cvjrf__hpmb, 'value_names_lit': kkx__fqkgc, 'columns_name_lit':
        ulkaw__ykq, **ujqbl__pki}
    exec(kuxhv__fgg, bpto__gcoya, vpxqv__kjm)
    impl = vpxqv__kjm['impl']
    return impl


def gen_pandas_parquet_metadata(column_names, data_types, index,
    write_non_range_index_to_metadata, write_rangeindex_to_metadata,
    partition_cols=None, is_runtime_columns=False):
    sjad__jmnts = {}
    sjad__jmnts['columns'] = []
    if partition_cols is None:
        partition_cols = []
    for col_name, rfreg__efws in zip(column_names, data_types):
        if col_name in partition_cols:
            continue
        qflnp__vfkxl = None
        if isinstance(rfreg__efws, bodo.DatetimeArrayType):
            yjsgk__homww = 'datetimetz'
            awcg__bhbg = 'datetime64[ns]'
            if isinstance(rfreg__efws.tz, int):
                fwy__zfs = bodo.libs.pd_datetime_arr_ext.nanoseconds_to_offset(
                    rfreg__efws.tz)
            else:
                fwy__zfs = pd.DatetimeTZDtype(tz=rfreg__efws.tz).tz
            qflnp__vfkxl = {'timezone': pa.lib.tzinfo_to_string(fwy__zfs)}
        elif isinstance(rfreg__efws, types.Array
            ) or rfreg__efws == boolean_array:
            yjsgk__homww = awcg__bhbg = rfreg__efws.dtype.name
            if awcg__bhbg.startswith('datetime'):
                yjsgk__homww = 'datetime'
        elif is_str_arr_type(rfreg__efws):
            yjsgk__homww = 'unicode'
            awcg__bhbg = 'object'
        elif rfreg__efws == binary_array_type:
            yjsgk__homww = 'bytes'
            awcg__bhbg = 'object'
        elif isinstance(rfreg__efws, DecimalArrayType):
            yjsgk__homww = awcg__bhbg = 'object'
        elif isinstance(rfreg__efws, IntegerArrayType):
            ivrcg__xsdd = rfreg__efws.dtype.name
            if ivrcg__xsdd.startswith('int'):
                yjsgk__homww = 'Int' + ivrcg__xsdd[3:]
            elif ivrcg__xsdd.startswith('uint'):
                yjsgk__homww = 'UInt' + ivrcg__xsdd[4:]
            else:
                if is_runtime_columns:
                    col_name = 'Runtime determined column of type'
                raise BodoError(
                    'to_parquet(): unknown dtype in nullable Integer column {} {}'
                    .format(col_name, rfreg__efws))
            awcg__bhbg = rfreg__efws.dtype.name
        elif rfreg__efws == datetime_date_array_type:
            yjsgk__homww = 'datetime'
            awcg__bhbg = 'object'
        elif isinstance(rfreg__efws, (StructArrayType, ArrayItemArrayType)):
            yjsgk__homww = 'object'
            awcg__bhbg = 'object'
        else:
            if is_runtime_columns:
                col_name = 'Runtime determined column of type'
            raise BodoError(
                'to_parquet(): unsupported column type for metadata generation : {} {}'
                .format(col_name, rfreg__efws))
        lwb__ubto = {'name': col_name, 'field_name': col_name,
            'pandas_type': yjsgk__homww, 'numpy_type': awcg__bhbg,
            'metadata': qflnp__vfkxl}
        sjad__jmnts['columns'].append(lwb__ubto)
    if write_non_range_index_to_metadata:
        if isinstance(index, MultiIndexType):
            raise BodoError('to_parquet: MultiIndex not supported yet')
        if 'none' in index.name:
            uir__mtskk = '__index_level_0__'
            eloy__bkgh = None
        else:
            uir__mtskk = '%s'
            eloy__bkgh = '%s'
        sjad__jmnts['index_columns'] = [uir__mtskk]
        sjad__jmnts['columns'].append({'name': eloy__bkgh, 'field_name':
            uir__mtskk, 'pandas_type': index.pandas_type_name, 'numpy_type':
            index.numpy_type_name, 'metadata': None})
    elif write_rangeindex_to_metadata:
        sjad__jmnts['index_columns'] = [{'kind': 'range', 'name': '%s',
            'start': '%d', 'stop': '%d', 'step': '%d'}]
    else:
        sjad__jmnts['index_columns'] = []
    sjad__jmnts['pandas_version'] = pd.__version__
    return sjad__jmnts


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
        tpbcz__sat = []
        for tgfhb__sif in partition_cols:
            try:
                idx = df.columns.index(tgfhb__sif)
            except ValueError as cwbe__qzgg:
                raise BodoError(
                    f'Partition column {tgfhb__sif} is not in dataframe')
            tpbcz__sat.append(idx)
    else:
        partition_cols = None
    if not is_overload_none(index) and not is_overload_constant_bool(index):
        raise BodoError('to_parquet(): index must be a constant bool or None')
    if not is_overload_int(row_group_size):
        raise BodoError('to_parquet(): row_group_size must be integer')
    from bodo.io.parquet_pio import parquet_write_table_cpp, parquet_write_table_partitioned_cpp
    vileg__hhqlw = isinstance(df.index, bodo.hiframes.pd_index_ext.
        RangeIndexType)
    fhcky__aynka = df.index is not None and (is_overload_true(_is_parallel) or
        not is_overload_true(_is_parallel) and not vileg__hhqlw)
    write_non_range_index_to_metadata = is_overload_true(index
        ) or is_overload_none(index) and (not vileg__hhqlw or
        is_overload_true(_is_parallel))
    write_rangeindex_to_metadata = is_overload_none(index
        ) and vileg__hhqlw and not is_overload_true(_is_parallel)
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
        pxppl__wegu = df.runtime_data_types
        sziy__cofk = len(pxppl__wegu)
        qflnp__vfkxl = gen_pandas_parquet_metadata([''] * sziy__cofk,
            pxppl__wegu, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=True)
        ncjb__nmtqu = qflnp__vfkxl['columns'][:sziy__cofk]
        qflnp__vfkxl['columns'] = qflnp__vfkxl['columns'][sziy__cofk:]
        ncjb__nmtqu = [json.dumps(ufy__mqx).replace('""', '{0}') for
            ufy__mqx in ncjb__nmtqu]
        nzvp__ipst = json.dumps(qflnp__vfkxl)
        gfv__cth = '"columns": ['
        lbaa__qjs = nzvp__ipst.find(gfv__cth)
        if lbaa__qjs == -1:
            raise BodoError(
                'DataFrame.to_parquet(): Unexpected metadata string for runtime columns.  Please return the DataFrame to regular Python to update typing information.'
                )
        ghve__prn = lbaa__qjs + len(gfv__cth)
        apfi__vff = nzvp__ipst[:ghve__prn]
        nzvp__ipst = nzvp__ipst[ghve__prn:]
        tco__nsvx = len(qflnp__vfkxl['columns'])
    else:
        nzvp__ipst = json.dumps(gen_pandas_parquet_metadata(df.columns, df.
            data, df.index, write_non_range_index_to_metadata,
            write_rangeindex_to_metadata, partition_cols=partition_cols,
            is_runtime_columns=False))
    if not is_overload_true(_is_parallel) and vileg__hhqlw:
        nzvp__ipst = nzvp__ipst.replace('"%d"', '%d')
        if df.index.name == 'RangeIndexType(none)':
            nzvp__ipst = nzvp__ipst.replace('"%s"', '%s')
    if not df.is_table_format:
        fcj__wss = ', '.join(
            'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
            .format(i) for i in range(len(df.columns)))
    kuxhv__fgg = """def df_to_parquet(df, path, engine='auto', compression='snappy', index=None, partition_cols=None, storage_options=None, row_group_size=-1, _bodo_file_prefix='part-', _is_parallel=False):
"""
    if df.is_table_format:
        kuxhv__fgg += '    py_table = get_dataframe_table(df)\n'
        kuxhv__fgg += (
            '    table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        kuxhv__fgg += '    info_list = [{}]\n'.format(fcj__wss)
        kuxhv__fgg += '    table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        kuxhv__fgg += '    columns_index = get_dataframe_column_names(df)\n'
        kuxhv__fgg += '    names_arr = index_to_array(columns_index)\n'
        kuxhv__fgg += '    col_names = array_to_info(names_arr)\n'
    else:
        kuxhv__fgg += '    col_names = array_to_info(col_names_arr)\n'
    if is_overload_true(index) or is_overload_none(index) and fhcky__aynka:
        kuxhv__fgg += """    index_col = array_to_info(index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)))
"""
        uzs__kwomj = True
    else:
        kuxhv__fgg += '    index_col = array_to_info(np.empty(0))\n'
        uzs__kwomj = False
    if df.has_runtime_cols:
        kuxhv__fgg += '    columns_lst = []\n'
        kuxhv__fgg += '    num_cols = 0\n'
        for i in range(len(df.runtime_data_types)):
            kuxhv__fgg += f'    for _ in range(len(py_table.block_{i})):\n'
            kuxhv__fgg += f"""        columns_lst.append({ncjb__nmtqu[i]!r}.replace('{{0}}', '"' + names_arr[num_cols] + '"'))
"""
            kuxhv__fgg += '        num_cols += 1\n'
        if tco__nsvx:
            kuxhv__fgg += "    columns_lst.append('')\n"
        kuxhv__fgg += '    columns_str = ", ".join(columns_lst)\n'
        kuxhv__fgg += ('    metadata = """' + apfi__vff +
            '""" + columns_str + """' + nzvp__ipst + '"""\n')
    else:
        kuxhv__fgg += '    metadata = """' + nzvp__ipst + '"""\n'
    kuxhv__fgg += '    if compression is None:\n'
    kuxhv__fgg += "        compression = 'none'\n"
    kuxhv__fgg += '    if df.index.name is not None:\n'
    kuxhv__fgg += '        name_ptr = df.index.name\n'
    kuxhv__fgg += '    else:\n'
    kuxhv__fgg += "        name_ptr = 'null'\n"
    kuxhv__fgg += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(path, parallel=_is_parallel)
"""
    vtlfr__pizcm = None
    if partition_cols:
        vtlfr__pizcm = pd.array([col_name for col_name in df.columns if 
            col_name not in partition_cols])
        anzpk__kdylk = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype.categories.values)'
             for i in range(len(df.columns)) if isinstance(df.data[i],
            CategoricalArrayType) and i in tpbcz__sat)
        if anzpk__kdylk:
            kuxhv__fgg += '    cat_info_list = [{}]\n'.format(anzpk__kdylk)
            kuxhv__fgg += (
                '    cat_table = arr_info_list_to_table(cat_info_list)\n')
        else:
            kuxhv__fgg += '    cat_table = table\n'
        kuxhv__fgg += (
            '    col_names_no_partitions = array_to_info(col_names_no_parts_arr)\n'
            )
        kuxhv__fgg += (
            f'    part_cols_idxs = np.array({tpbcz__sat}, dtype=np.int32)\n')
        kuxhv__fgg += (
            '    parquet_write_table_partitioned_cpp(unicode_to_utf8(path),\n')
        kuxhv__fgg += """                            table, col_names, col_names_no_partitions, cat_table,
"""
        kuxhv__fgg += (
            '                            part_cols_idxs.ctypes, len(part_cols_idxs),\n'
            )
        kuxhv__fgg += (
            '                            unicode_to_utf8(compression),\n')
        kuxhv__fgg += '                            _is_parallel,\n'
        kuxhv__fgg += (
            '                            unicode_to_utf8(bucket_region),\n')
        kuxhv__fgg += '                            row_group_size,\n'
        kuxhv__fgg += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        kuxhv__fgg += '    delete_table_decref_arrays(table)\n'
        kuxhv__fgg += '    delete_info_decref_array(index_col)\n'
        kuxhv__fgg += '    delete_info_decref_array(col_names_no_partitions)\n'
        kuxhv__fgg += '    delete_info_decref_array(col_names)\n'
        if anzpk__kdylk:
            kuxhv__fgg += '    delete_table_decref_arrays(cat_table)\n'
    elif write_rangeindex_to_metadata:
        kuxhv__fgg += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        kuxhv__fgg += (
            '                            table, col_names, index_col,\n')
        kuxhv__fgg += '                            ' + str(uzs__kwomj) + ',\n'
        kuxhv__fgg += (
            '                            unicode_to_utf8(metadata),\n')
        kuxhv__fgg += (
            '                            unicode_to_utf8(compression),\n')
        kuxhv__fgg += (
            '                            _is_parallel, 1, df.index.start,\n')
        kuxhv__fgg += (
            '                            df.index.stop, df.index.step,\n')
        kuxhv__fgg += (
            '                            unicode_to_utf8(name_ptr),\n')
        kuxhv__fgg += (
            '                            unicode_to_utf8(bucket_region),\n')
        kuxhv__fgg += '                            row_group_size,\n'
        kuxhv__fgg += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        kuxhv__fgg += '    delete_table_decref_arrays(table)\n'
        kuxhv__fgg += '    delete_info_decref_array(index_col)\n'
        kuxhv__fgg += '    delete_info_decref_array(col_names)\n'
    else:
        kuxhv__fgg += '    parquet_write_table_cpp(unicode_to_utf8(path),\n'
        kuxhv__fgg += (
            '                            table, col_names, index_col,\n')
        kuxhv__fgg += '                            ' + str(uzs__kwomj) + ',\n'
        kuxhv__fgg += (
            '                            unicode_to_utf8(metadata),\n')
        kuxhv__fgg += (
            '                            unicode_to_utf8(compression),\n')
        kuxhv__fgg += '                            _is_parallel, 0, 0, 0, 0,\n'
        kuxhv__fgg += (
            '                            unicode_to_utf8(name_ptr),\n')
        kuxhv__fgg += (
            '                            unicode_to_utf8(bucket_region),\n')
        kuxhv__fgg += '                            row_group_size,\n'
        kuxhv__fgg += (
            '                            unicode_to_utf8(_bodo_file_prefix))\n'
            )
        kuxhv__fgg += '    delete_table_decref_arrays(table)\n'
        kuxhv__fgg += '    delete_info_decref_array(index_col)\n'
        kuxhv__fgg += '    delete_info_decref_array(col_names)\n'
    vpxqv__kjm = {}
    if df.has_runtime_cols:
        iefqo__lfv = None
    else:
        for bbho__xiu in df.columns:
            if not isinstance(bbho__xiu, str):
                raise BodoError(
                    'DataFrame.to_parquet(): parquet must have string column names'
                    )
        iefqo__lfv = pd.array(df.columns)
    exec(kuxhv__fgg, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'str_arr_from_sequence': str_arr_from_sequence,
        'parquet_write_table_cpp': parquet_write_table_cpp,
        'parquet_write_table_partitioned_cpp':
        parquet_write_table_partitioned_cpp, 'index_to_array':
        index_to_array, 'delete_info_decref_array':
        delete_info_decref_array, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'col_names_arr': iefqo__lfv,
        'py_table_to_cpp_table': py_table_to_cpp_table, 'py_table_typ': df.
        table_type, 'get_dataframe_table': get_dataframe_table,
        'col_names_no_parts_arr': vtlfr__pizcm,
        'get_dataframe_column_names': get_dataframe_column_names,
        'fix_arr_dtype': fix_arr_dtype, 'decode_if_dict_array':
        decode_if_dict_array, 'decode_if_dict_table': decode_if_dict_table},
        vpxqv__kjm)
    rflx__haa = vpxqv__kjm['df_to_parquet']
    return rflx__haa


def to_sql_exception_guard(df, name, con, schema=None, if_exists='fail',
    index=True, index_label=None, chunksize=None, dtype=None, method=None,
    _is_table_create=False, _is_parallel=False):
    aduf__idyo = 'all_ok'
    cfnwu__cicz, sbl__nrcx = bodo.ir.sql_ext.parse_dbtype(con)
    if _is_parallel and bodo.get_rank() == 0:
        ktyp__igy = 100
        if chunksize is None:
            mby__out = ktyp__igy
        else:
            mby__out = min(chunksize, ktyp__igy)
        if _is_table_create:
            df = df.iloc[:mby__out, :]
        else:
            df = df.iloc[mby__out:, :]
            if len(df) == 0:
                return aduf__idyo
    dzoyz__bwgj = df.columns
    try:
        if cfnwu__cicz == 'snowflake':
            if sbl__nrcx and con.count(sbl__nrcx) == 1:
                con = con.replace(sbl__nrcx, quote(sbl__nrcx))
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
                df.columns = [(tvwg__mzshd.upper() if tvwg__mzshd.islower()
                     else tvwg__mzshd) for tvwg__mzshd in df.columns]
            except ImportError as cwbe__qzgg:
                aduf__idyo = (
                    "Snowflake Python connector packages not found. Using 'to_sql' with Snowflake requires both snowflake-sqlalchemy and snowflake-connector-python. These can be installed by calling 'conda install -c conda-forge snowflake-sqlalchemy snowflake-connector-python' or 'pip install snowflake-sqlalchemy snowflake-connector-python'."
                    )
                return aduf__idyo
        if cfnwu__cicz == 'oracle':
            import os
            import sqlalchemy as sa
            from sqlalchemy.dialects.oracle import VARCHAR2
            dhote__jatf = os.environ.get('BODO_DISABLE_ORACLE_VARCHAR2', None)
            mxlq__ohj = bodo.typeof(df)
            ski__zjfzl = {}
            for tvwg__mzshd, wtatt__jmiq in zip(mxlq__ohj.columns,
                mxlq__ohj.data):
                if df[tvwg__mzshd].dtype == 'object':
                    if wtatt__jmiq == datetime_date_array_type:
                        ski__zjfzl[tvwg__mzshd] = sa.types.Date
                    elif wtatt__jmiq in (bodo.string_array_type, bodo.
                        dict_str_arr_type) and (not dhote__jatf or 
                        dhote__jatf == '0'):
                        ski__zjfzl[tvwg__mzshd] = VARCHAR2(4000)
            dtype = ski__zjfzl
        try:
            df.to_sql(name, con, schema, if_exists, index, index_label,
                chunksize, dtype, method)
        except Exception as xgqld__nnid:
            aduf__idyo = xgqld__nnid.args[0]
            if cfnwu__cicz == 'oracle' and 'ORA-12899' in aduf__idyo:
                aduf__idyo += """
                String is larger than VARCHAR2 maximum length.
                Please set environment variable `BODO_DISABLE_ORACLE_VARCHAR2` to
                disable Bodo's optimziation use of VARCHA2.
                NOTE: Oracle `to_sql` with CLOB datatypes is known to be really slow.
                """
        return aduf__idyo
    finally:
        df.columns = dzoyz__bwgj


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
    kuxhv__fgg = f"""def df_to_sql(df, name, con, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None, method=None, _is_parallel=False):
"""
    kuxhv__fgg += f"    if con.startswith('iceberg'):\n"
    kuxhv__fgg += (
        f'        con_str = bodo.io.iceberg.format_iceberg_conn_njit(con)\n')
    kuxhv__fgg += f'        if schema is None:\n'
    kuxhv__fgg += f"""            raise ValueError('DataFrame.to_sql(): schema must be provided when writing to an Iceberg table.')
"""
    kuxhv__fgg += f'        if chunksize is not None:\n'
    kuxhv__fgg += f"""            raise ValueError('DataFrame.to_sql(): chunksize not supported for Iceberg tables.')
"""
    kuxhv__fgg += f'        if index and bodo.get_rank() == 0:\n'
    kuxhv__fgg += (
        f"            warnings.warn('index is not supported for Iceberg tables.')\n"
        )
    kuxhv__fgg += (
        f'        if index_label is not None and bodo.get_rank() == 0:\n')
    kuxhv__fgg += (
        f"            warnings.warn('index_label is not supported for Iceberg tables.')\n"
        )
    if df.is_table_format:
        kuxhv__fgg += f'        py_table = get_dataframe_table(df)\n'
        kuxhv__fgg += (
            f'        table = py_table_to_cpp_table(py_table, py_table_typ)\n')
    else:
        fcj__wss = ', '.join(
            f'array_to_info(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
             for i in range(len(df.columns)))
        kuxhv__fgg += f'        info_list = [{fcj__wss}]\n'
        kuxhv__fgg += f'        table = arr_info_list_to_table(info_list)\n'
    if df.has_runtime_cols:
        kuxhv__fgg += (
            f'        columns_index = get_dataframe_column_names(df)\n')
        kuxhv__fgg += f'        names_arr = index_to_array(columns_index)\n'
        kuxhv__fgg += f'        col_names = array_to_info(names_arr)\n'
    else:
        kuxhv__fgg += f'        col_names = array_to_info(col_names_arr)\n'
    kuxhv__fgg += """        bodo.io.iceberg.iceberg_write(
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
    kuxhv__fgg += f'        delete_table_decref_arrays(table)\n'
    kuxhv__fgg += f'        delete_info_decref_array(col_names)\n'
    if df.has_runtime_cols:
        iefqo__lfv = None
    else:
        for bbho__xiu in df.columns:
            if not isinstance(bbho__xiu, str):
                raise BodoError(
                    'DataFrame.to_sql(): must have string column names for Iceberg tables'
                    )
        iefqo__lfv = pd.array(df.columns)
    kuxhv__fgg += f'    else:\n'
    kuxhv__fgg += f'        rank = bodo.libs.distributed_api.get_rank()\n'
    kuxhv__fgg += f"        err_msg = 'unset'\n"
    kuxhv__fgg += f'        if rank != 0:\n'
    kuxhv__fgg += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    kuxhv__fgg += f'        elif rank == 0:\n'
    kuxhv__fgg += f'            err_msg = to_sql_exception_guard_encaps(\n'
    kuxhv__fgg += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    kuxhv__fgg += f'                          chunksize, dtype, method,\n'
    kuxhv__fgg += f'                          True, _is_parallel,\n'
    kuxhv__fgg += f'                      )\n'
    kuxhv__fgg += (
        f'            err_msg = bodo.libs.distributed_api.bcast_scalar(err_msg)\n'
        )
    kuxhv__fgg += f"        if_exists = 'append'\n"
    kuxhv__fgg += f"        if _is_parallel and err_msg == 'all_ok':\n"
    kuxhv__fgg += f'            err_msg = to_sql_exception_guard_encaps(\n'
    kuxhv__fgg += f"""                          df, name, con, schema, if_exists, index, index_label,
"""
    kuxhv__fgg += f'                          chunksize, dtype, method,\n'
    kuxhv__fgg += f'                          False, _is_parallel,\n'
    kuxhv__fgg += f'                      )\n'
    kuxhv__fgg += f"        if err_msg != 'all_ok':\n"
    kuxhv__fgg += f"            print('err_msg=', err_msg)\n"
    kuxhv__fgg += (
        f"            raise ValueError('error in to_sql() operation')\n")
    vpxqv__kjm = {}
    exec(kuxhv__fgg, {'np': np, 'bodo': bodo, 'unicode_to_utf8':
        unicode_to_utf8, 'array_to_info': array_to_info,
        'get_dataframe_table': get_dataframe_table, 'py_table_typ': df.
        table_type, 'col_names_arr': iefqo__lfv,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'delete_info_decref_array': delete_info_decref_array,
        'arr_info_list_to_table': arr_info_list_to_table, 'index_to_array':
        index_to_array, 'pyarrow_table_schema': bodo.io.iceberg.
        pyarrow_schema(df), 'to_sql_exception_guard_encaps':
        to_sql_exception_guard_encaps, 'warnings': warnings}, vpxqv__kjm)
    _impl = vpxqv__kjm['df_to_sql']
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
        yhi__fqfcm = get_overload_const_str(path_or_buf)
        if yhi__fqfcm.endswith(('.gz', '.bz2', '.zip', '.xz')):
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
        tby__vthyn = bodo.io.fs_io.get_s3_bucket_region_njit(path_or_buf,
            parallel=False)
        if lines and orient == 'records':
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, True,
                unicode_to_utf8(tby__vthyn), unicode_to_utf8(_bodo_file_prefix)
                )
            bodo.utils.utils.check_and_propagate_cpp_exception()
        else:
            bodo.hiframes.pd_dataframe_ext._json_write(unicode_to_utf8(
                path_or_buf), unicode_to_utf8(D), 0, len(D), False, False,
                unicode_to_utf8(tby__vthyn), unicode_to_utf8(_bodo_file_prefix)
                )
            bodo.utils.utils.check_and_propagate_cpp_exception()
    return _impl


@overload(pd.get_dummies, inline='always', no_unliteral=True)
def get_dummies(data, prefix=None, prefix_sep='_', dummy_na=False, columns=
    None, sparse=False, drop_first=False, dtype=None):
    vorh__ltzbe = {'prefix': prefix, 'prefix_sep': prefix_sep, 'dummy_na':
        dummy_na, 'columns': columns, 'sparse': sparse, 'drop_first':
        drop_first, 'dtype': dtype}
    hrs__yegg = {'prefix': None, 'prefix_sep': '_', 'dummy_na': False,
        'columns': None, 'sparse': False, 'drop_first': False, 'dtype': None}
    check_unsupported_args('pandas.get_dummies', vorh__ltzbe, hrs__yegg,
        package_name='pandas', module_name='General')
    if not categorical_can_construct_dataframe(data):
        raise BodoError(
            'pandas.get_dummies() only support categorical data types with explicitly known categories'
            )
    kuxhv__fgg = """def impl(data, prefix=None, prefix_sep='_', dummy_na=False, columns=None, sparse=False, drop_first=False, dtype=None,):
"""
    if isinstance(data, SeriesType):
        lukty__yptaz = data.data.dtype.categories
        kuxhv__fgg += (
            '  data_values = bodo.hiframes.pd_series_ext.get_series_data(data)\n'
            )
    else:
        lukty__yptaz = data.dtype.categories
        kuxhv__fgg += '  data_values = data\n'
    orksi__xybue = len(lukty__yptaz)
    kuxhv__fgg += """  codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(data_values)
"""
    kuxhv__fgg += '  numba.parfors.parfor.init_prange()\n'
    kuxhv__fgg += '  n = len(data_values)\n'
    for i in range(orksi__xybue):
        kuxhv__fgg += '  data_arr_{} = np.empty(n, np.uint8)\n'.format(i)
    kuxhv__fgg += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    kuxhv__fgg += '      if bodo.libs.array_kernels.isna(data_values, i):\n'
    for zaq__nhr in range(orksi__xybue):
        kuxhv__fgg += '          data_arr_{}[i] = 0\n'.format(zaq__nhr)
    kuxhv__fgg += '      else:\n'
    for mpfq__fvt in range(orksi__xybue):
        kuxhv__fgg += '          data_arr_{0}[i] = codes[i] == {0}\n'.format(
            mpfq__fvt)
    fcj__wss = ', '.join(f'data_arr_{i}' for i in range(orksi__xybue))
    index = 'bodo.hiframes.pd_index_ext.init_range_index(0, n, 1, None)'
    if isinstance(lukty__yptaz[0], np.datetime64):
        lukty__yptaz = tuple(pd.Timestamp(tvwg__mzshd) for tvwg__mzshd in
            lukty__yptaz)
    elif isinstance(lukty__yptaz[0], np.timedelta64):
        lukty__yptaz = tuple(pd.Timedelta(tvwg__mzshd) for tvwg__mzshd in
            lukty__yptaz)
    return bodo.hiframes.dataframe_impl._gen_init_df(kuxhv__fgg,
        lukty__yptaz, fcj__wss, index)


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
    for psi__sfr in pd_unsupported:
        pgswy__oufpq = mod_name + '.' + psi__sfr.__name__
        overload(psi__sfr, no_unliteral=True)(create_unsupported_overload(
            pgswy__oufpq))


def _install_dataframe_unsupported():
    for cdwer__rmdow in dataframe_unsupported_attrs:
        fel__otjxy = 'DataFrame.' + cdwer__rmdow
        overload_attribute(DataFrameType, cdwer__rmdow)(
            create_unsupported_overload(fel__otjxy))
    for pgswy__oufpq in dataframe_unsupported:
        fel__otjxy = 'DataFrame.' + pgswy__oufpq + '()'
        overload_method(DataFrameType, pgswy__oufpq)(
            create_unsupported_overload(fel__otjxy))


_install_pd_unsupported('pandas', pd_unsupported)
_install_pd_unsupported('pandas.util', pd_util_unsupported)
_install_dataframe_unsupported()
