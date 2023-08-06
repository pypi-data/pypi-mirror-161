"""Support for Pandas Groupby operations
"""
import operator
from enum import Enum
import numba
import numpy as np
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import AbstractTemplate, bound_function, infer_global, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import NumericIndexType, RangeIndexType
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, get_groupby_labels, get_null_shuffle_info, get_shuffle_info, info_from_table, info_to_array, reverse_shuffle_table, shuffle_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.decimal_arr_ext import Decimal128Type
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.transform import get_call_expr_arg, get_const_func_output_type
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, dtype_to_array_type, get_index_data_arr_types, get_index_name_types, get_literal_value, get_overload_const_bool, get_overload_const_func, get_overload_const_list, get_overload_const_str, get_overload_constant_dict, get_udf_error_msg, get_udf_out_arr_type, is_dtype_nullable, is_literal_type, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, list_cumulative, raise_bodo_error, to_nullable_type, to_numeric_index_if_range_index, to_str_arr_if_dict_array
from bodo.utils.utils import dt_err, is_expr


class DataFrameGroupByType(types.Type):

    def __init__(self, df_type, keys, selection, as_index, dropna=True,
        explicit_select=False, series_select=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(df_type,
            'pandas.groupby()')
        self.df_type = df_type
        self.keys = keys
        self.selection = selection
        self.as_index = as_index
        self.dropna = dropna
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(DataFrameGroupByType, self).__init__(name=
            f'DataFrameGroupBy({df_type}, {keys}, {selection}, {as_index}, {dropna}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return DataFrameGroupByType(self.df_type, self.keys, self.selection,
            self.as_index, self.dropna, self.explicit_select, self.
            series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(DataFrameGroupByType)
class GroupbyModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        dtke__dbvxa = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, dtke__dbvxa)


make_attribute_wrapper(DataFrameGroupByType, 'obj', 'obj')


def validate_udf(func_name, func):
    if not isinstance(func, (types.functions.MakeFunctionLiteral, bodo.
        utils.typing.FunctionLiteral, types.Dispatcher, CPUDispatcher)):
        raise_bodo_error(
            f"Groupby.{func_name}: 'func' must be user defined function")


@intrinsic
def init_groupby(typingctx, obj_type, by_type, as_index_type=None,
    dropna_type=None):

    def codegen(context, builder, signature, args):
        zdkh__ypelt = args[0]
        sujwx__ghuy = signature.return_type
        kfm__svwcr = cgutils.create_struct_proxy(sujwx__ghuy)(context, builder)
        kfm__svwcr.obj = zdkh__ypelt
        context.nrt.incref(builder, signature.args[0], zdkh__ypelt)
        return kfm__svwcr._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for ztb__vmtt in keys:
        selection.remove(ztb__vmtt)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    sujwx__ghuy = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return sujwx__ghuy(obj_type, by_type, as_index_type, dropna_type), codegen


@lower_builtin('groupby.count', types.VarArg(types.Any))
@lower_builtin('groupby.size', types.VarArg(types.Any))
@lower_builtin('groupby.apply', types.VarArg(types.Any))
@lower_builtin('groupby.agg', types.VarArg(types.Any))
def lower_groupby_count_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


@infer
class StaticGetItemDataFrameGroupBy(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        grpby, xzg__djgua = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(xzg__djgua, (tuple, list)):
                if len(set(xzg__djgua).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(xzg__djgua).difference(set(grpby.
                        df_type.columns))))
                selection = xzg__djgua
            else:
                if xzg__djgua not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(xzg__djgua))
                selection = xzg__djgua,
                series_select = True
            uuyd__mmn = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(uuyd__mmn, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, xzg__djgua = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            xzg__djgua):
            uuyd__mmn = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(xzg__djgua)), {}).return_type
            return signature(uuyd__mmn, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    okfo__mrca = arr_type == ArrayItemArrayType(string_array_type)
    wrejm__rxh = arr_type.dtype
    if isinstance(wrejm__rxh, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {wrejm__rxh} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(wrejm__rxh, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {wrejm__rxh} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(wrejm__rxh,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(wrejm__rxh, (types.Integer, types.Float, types.Boolean)):
        if okfo__mrca or wrejm__rxh == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(wrejm__rxh, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not wrejm__rxh.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {wrejm__rxh} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(wrejm__rxh, types.Boolean) and func_name in {'cumsum',
        'sum', 'mean', 'std', 'var'}:
        return (None,
            f'groupby built-in functions {func_name} does not support boolean column'
            )
    if func_name in {'idxmin', 'idxmax'}:
        return dtype_to_array_type(get_index_data_arr_types(index_type)[0].
            dtype), 'ok'
    if func_name in {'count', 'nunique'}:
        return dtype_to_array_type(types.int64), 'ok'
    else:
        return arr_type, 'ok'


def get_pivot_output_dtype(arr_type, func_name, index_type=None):
    wrejm__rxh = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(wrejm__rxh, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(wrejm__rxh, types.Integer):
            return IntDtype(wrejm__rxh)
        return wrejm__rxh
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        rut__ftk = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{rut__ftk}'."
            )
    elif len(args) > len_args:
        raise BodoError(
            f'Groupby.{func_name}() takes {len_args + 1} positional argument but {len(args)} were given.'
            )


class ColumnType(Enum):
    KeyColumn = 0
    NumericalColumn = 1
    NonNumericalColumn = 2


def get_keys_not_as_index(grp, out_columns, out_data, out_column_type,
    multi_level_names=False):
    for ztb__vmtt in grp.keys:
        if multi_level_names:
            oiths__agkdj = ztb__vmtt, ''
        else:
            oiths__agkdj = ztb__vmtt
        dal__jujc = grp.df_type.column_index[ztb__vmtt]
        data = grp.df_type.data[dal__jujc]
        out_columns.append(oiths__agkdj)
        out_data.append(data)
        out_column_type.append(ColumnType.KeyColumn.value)


def get_agg_typ(grp, args, func_name, typing_context, target_context, func=
    None, kws=None):
    index = RangeIndexType(types.none)
    out_data = []
    out_columns = []
    out_column_type = []
    if func_name in ('head', 'ngroup'):
        grp.as_index = True
    if not grp.as_index:
        get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
    elif func_name in ('head', 'ngroup'):
        if grp.df_type.index == index:
            index = NumericIndexType(types.int64, types.none)
        else:
            index = grp.df_type.index
    elif len(grp.keys) > 1:
        awl__kgp = tuple(grp.df_type.column_index[grp.keys[dyp__gqkv]] for
            dyp__gqkv in range(len(grp.keys)))
        fhjl__llox = tuple(grp.df_type.data[dal__jujc] for dal__jujc in
            awl__kgp)
        index = MultiIndexType(fhjl__llox, tuple(types.StringLiteral(
            ztb__vmtt) for ztb__vmtt in grp.keys))
    else:
        dal__jujc = grp.df_type.column_index[grp.keys[0]]
        nwzc__xjfhn = grp.df_type.data[dal__jujc]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(nwzc__xjfhn,
            types.StringLiteral(grp.keys[0]))
    rsqek__mzcu = {}
    wxhf__mlps = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        rsqek__mzcu[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        rsqek__mzcu[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        hcnkq__dsj = dict(ascending=ascending)
        bvucq__jzm = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', hcnkq__dsj,
            bvucq__jzm, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for uodzn__xbmiu in columns:
            dal__jujc = grp.df_type.column_index[uodzn__xbmiu]
            data = grp.df_type.data[dal__jujc]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            jkn__ivset = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                jkn__ivset = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    awg__ttuch = SeriesType(data.dtype, data, None, string_type
                        )
                    fngld__xofu = get_const_func_output_type(func, (
                        awg__ttuch,), {}, typing_context, target_context)
                    if fngld__xofu != ArrayItemArrayType(string_array_type):
                        fngld__xofu = dtype_to_array_type(fngld__xofu)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=uodzn__xbmiu, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    uhja__zqbuw = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    cvvw__gomeo = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    hcnkq__dsj = dict(numeric_only=uhja__zqbuw, min_count=
                        cvvw__gomeo)
                    bvucq__jzm = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        hcnkq__dsj, bvucq__jzm, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    uhja__zqbuw = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    cvvw__gomeo = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    hcnkq__dsj = dict(numeric_only=uhja__zqbuw, min_count=
                        cvvw__gomeo)
                    bvucq__jzm = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        hcnkq__dsj, bvucq__jzm, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    uhja__zqbuw = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    hcnkq__dsj = dict(numeric_only=uhja__zqbuw)
                    bvucq__jzm = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        hcnkq__dsj, bvucq__jzm, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    qhko__hic = args[0] if len(args) > 0 else kws.pop('axis', 0
                        )
                    zqd__hnmn = args[1] if len(args) > 1 else kws.pop('skipna',
                        True)
                    hcnkq__dsj = dict(axis=qhko__hic, skipna=zqd__hnmn)
                    bvucq__jzm = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        hcnkq__dsj, bvucq__jzm, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    jlqgm__hhg = args[0] if len(args) > 0 else kws.pop('ddof',
                        1)
                    hcnkq__dsj = dict(ddof=jlqgm__hhg)
                    bvucq__jzm = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        hcnkq__dsj, bvucq__jzm, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                fngld__xofu, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                fngld__xofu = to_str_arr_if_dict_array(fngld__xofu
                    ) if func_name in ('sum', 'cumsum') else fngld__xofu
                out_data.append(fngld__xofu)
                out_columns.append(uodzn__xbmiu)
                if func_name == 'agg':
                    qqwtb__vphdi = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    rsqek__mzcu[uodzn__xbmiu, qqwtb__vphdi] = uodzn__xbmiu
                else:
                    rsqek__mzcu[uodzn__xbmiu, func_name] = uodzn__xbmiu
                out_column_type.append(jkn__ivset)
            else:
                wxhf__mlps.append(err_msg)
    if func_name == 'sum':
        uvsfz__nkb = any([(pdkbo__zzk == ColumnType.NumericalColumn.value) for
            pdkbo__zzk in out_column_type])
        if uvsfz__nkb:
            out_data = [pdkbo__zzk for pdkbo__zzk, deopd__vtjg in zip(
                out_data, out_column_type) if deopd__vtjg != ColumnType.
                NonNumericalColumn.value]
            out_columns = [pdkbo__zzk for pdkbo__zzk, deopd__vtjg in zip(
                out_columns, out_column_type) if deopd__vtjg != ColumnType.
                NonNumericalColumn.value]
            rsqek__mzcu = {}
            for uodzn__xbmiu in out_columns:
                if grp.as_index is False and uodzn__xbmiu in grp.keys:
                    continue
                rsqek__mzcu[uodzn__xbmiu, func_name] = uodzn__xbmiu
    bgwy__nykqj = len(wxhf__mlps)
    if len(out_data) == 0:
        if bgwy__nykqj == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(bgwy__nykqj, ' was' if bgwy__nykqj == 1 else
                's were', ','.join(wxhf__mlps)))
    zytf__tsffk = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            smf__lwqgp = IntDtype(out_data[0].dtype)
        else:
            smf__lwqgp = out_data[0].dtype
        nxb__abktu = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        zytf__tsffk = SeriesType(smf__lwqgp, data=out_data[0], index=index,
            name_typ=nxb__abktu)
    return signature(zytf__tsffk, *args), rsqek__mzcu


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    lcob__stwpb = True
    if isinstance(f_val, str):
        lcob__stwpb = False
        vypj__nxz = f_val
    elif is_overload_constant_str(f_val):
        lcob__stwpb = False
        vypj__nxz = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        lcob__stwpb = False
        vypj__nxz = bodo.utils.typing.get_builtin_function_name(f_val)
    if not lcob__stwpb:
        if vypj__nxz not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {vypj__nxz}')
        uuyd__mmn = DataFrameGroupByType(grp.df_type, grp.keys, (col,), grp
            .as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(uuyd__mmn, (), vypj__nxz, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            mhpkp__pxy = types.functions.MakeFunctionLiteral(f_val)
        else:
            mhpkp__pxy = f_val
        validate_udf('agg', mhpkp__pxy)
        func = get_overload_const_func(mhpkp__pxy, None)
        qlnag__ukjkr = func.code if hasattr(func, 'code') else func.__code__
        vypj__nxz = qlnag__ukjkr.co_name
        uuyd__mmn = DataFrameGroupByType(grp.df_type, grp.keys, (col,), grp
            .as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(uuyd__mmn, (), 'agg', typing_context,
            target_context, mhpkp__pxy)[0].return_type
    return vypj__nxz, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    tfwmu__iou = kws and all(isinstance(xvjbd__zfnu, types.Tuple) and len(
        xvjbd__zfnu) == 2 for xvjbd__zfnu in kws.values())
    if is_overload_none(func) and not tfwmu__iou:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not tfwmu__iou:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    opj__rqy = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if tfwmu__iou or is_overload_constant_dict(func):
        if tfwmu__iou:
            cjm__qwstr = [get_literal_value(zvkb__ruv) for zvkb__ruv,
                dmyp__qzan in kws.values()]
            vqyx__tiydt = [get_literal_value(ljqb__frk) for dmyp__qzan,
                ljqb__frk in kws.values()]
        else:
            tye__bmh = get_overload_constant_dict(func)
            cjm__qwstr = tuple(tye__bmh.keys())
            vqyx__tiydt = tuple(tye__bmh.values())
        for uie__guthc in ('head', 'ngroup'):
            if uie__guthc in vqyx__tiydt:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {uie__guthc} cannot be mixed with other groupby operations.'
                    )
        if any(uodzn__xbmiu not in grp.selection and uodzn__xbmiu not in
            grp.keys for uodzn__xbmiu in cjm__qwstr):
            raise_bodo_error(
                f'Selected column names {cjm__qwstr} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            vqyx__tiydt)
        if tfwmu__iou and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        rsqek__mzcu = {}
        out_columns = []
        out_data = []
        out_column_type = []
        nlbme__vpvxd = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for zxls__qtyo, f_val in zip(cjm__qwstr, vqyx__tiydt):
            if isinstance(f_val, (tuple, list)):
                hcdri__prpx = 0
                for mhpkp__pxy in f_val:
                    vypj__nxz, out_tp = get_agg_funcname_and_outtyp(grp,
                        zxls__qtyo, mhpkp__pxy, typing_context, target_context)
                    opj__rqy = vypj__nxz in list_cumulative
                    if vypj__nxz == '<lambda>' and len(f_val) > 1:
                        vypj__nxz = '<lambda_' + str(hcdri__prpx) + '>'
                        hcdri__prpx += 1
                    out_columns.append((zxls__qtyo, vypj__nxz))
                    rsqek__mzcu[zxls__qtyo, vypj__nxz] = zxls__qtyo, vypj__nxz
                    _append_out_type(grp, out_data, out_tp)
            else:
                vypj__nxz, out_tp = get_agg_funcname_and_outtyp(grp,
                    zxls__qtyo, f_val, typing_context, target_context)
                opj__rqy = vypj__nxz in list_cumulative
                if multi_level_names:
                    out_columns.append((zxls__qtyo, vypj__nxz))
                    rsqek__mzcu[zxls__qtyo, vypj__nxz] = zxls__qtyo, vypj__nxz
                elif not tfwmu__iou:
                    out_columns.append(zxls__qtyo)
                    rsqek__mzcu[zxls__qtyo, vypj__nxz] = zxls__qtyo
                elif tfwmu__iou:
                    nlbme__vpvxd.append(vypj__nxz)
                _append_out_type(grp, out_data, out_tp)
        if tfwmu__iou:
            for dyp__gqkv, xxofr__regnu in enumerate(kws.keys()):
                out_columns.append(xxofr__regnu)
                rsqek__mzcu[cjm__qwstr[dyp__gqkv], nlbme__vpvxd[dyp__gqkv]
                    ] = xxofr__regnu
        if opj__rqy:
            index = grp.df_type.index
        else:
            index = out_tp.index
        zytf__tsffk = DataFrameType(tuple(out_data), index, tuple(
            out_columns), is_table_format=True)
        return signature(zytf__tsffk, *args), rsqek__mzcu
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            wmyno__mfk = get_overload_const_list(func)
        else:
            wmyno__mfk = func.types
        if len(wmyno__mfk) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        hcdri__prpx = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        rsqek__mzcu = {}
        jsoja__cgcnn = grp.selection[0]
        for f_val in wmyno__mfk:
            vypj__nxz, out_tp = get_agg_funcname_and_outtyp(grp,
                jsoja__cgcnn, f_val, typing_context, target_context)
            opj__rqy = vypj__nxz in list_cumulative
            if vypj__nxz == '<lambda>' and len(wmyno__mfk) > 1:
                vypj__nxz = '<lambda_' + str(hcdri__prpx) + '>'
                hcdri__prpx += 1
            out_columns.append(vypj__nxz)
            rsqek__mzcu[jsoja__cgcnn, vypj__nxz] = vypj__nxz
            _append_out_type(grp, out_data, out_tp)
        if opj__rqy:
            index = grp.df_type.index
        else:
            index = out_tp.index
        zytf__tsffk = DataFrameType(tuple(out_data), index, tuple(
            out_columns), is_table_format=True)
        return signature(zytf__tsffk, *args), rsqek__mzcu
    vypj__nxz = ''
    if types.unliteral(func) == types.unicode_type:
        vypj__nxz = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        vypj__nxz = bodo.utils.typing.get_builtin_function_name(func)
    if vypj__nxz:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, vypj__nxz, typing_context, kws)
    validate_udf('agg', func)
    return get_agg_typ(grp, args, 'agg', typing_context, target_context, func)


def resolve_transformative(grp, args, kws, msg, name_operation):
    index = to_numeric_index_if_range_index(grp.df_type.index)
    if isinstance(index, MultiIndexType):
        raise_bodo_error(
            f'Groupby.{name_operation}: MultiIndex input not supported for groupby operations that use input Index'
            )
    out_columns = []
    out_data = []
    if name_operation in list_cumulative:
        kws = dict(kws) if kws else {}
        qhko__hic = args[0] if len(args) > 0 else kws.pop('axis', 0)
        uhja__zqbuw = args[1] if len(args) > 1 else kws.pop('numeric_only',
            False)
        zqd__hnmn = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        hcnkq__dsj = dict(axis=qhko__hic, numeric_only=uhja__zqbuw)
        bvucq__jzm = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', hcnkq__dsj,
            bvucq__jzm, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        ghftc__wfvnc = args[0] if len(args) > 0 else kws.pop('periods', 1)
        pip__gqr = args[1] if len(args) > 1 else kws.pop('freq', None)
        qhko__hic = args[2] if len(args) > 2 else kws.pop('axis', 0)
        iiwr__tkyw = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        hcnkq__dsj = dict(freq=pip__gqr, axis=qhko__hic, fill_value=iiwr__tkyw)
        bvucq__jzm = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', hcnkq__dsj,
            bvucq__jzm, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        lfjy__ulelp = args[0] if len(args) > 0 else kws.pop('func', None)
        jzpe__iqheg = kws.pop('engine', None)
        tcme__bthi = kws.pop('engine_kwargs', None)
        hcnkq__dsj = dict(engine=jzpe__iqheg, engine_kwargs=tcme__bthi)
        bvucq__jzm = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', hcnkq__dsj, bvucq__jzm,
            package_name='pandas', module_name='GroupBy')
    rsqek__mzcu = {}
    for uodzn__xbmiu in grp.selection:
        out_columns.append(uodzn__xbmiu)
        rsqek__mzcu[uodzn__xbmiu, name_operation] = uodzn__xbmiu
        dal__jujc = grp.df_type.column_index[uodzn__xbmiu]
        data = grp.df_type.data[dal__jujc]
        rlqam__vivh = (name_operation if name_operation != 'transform' else
            get_literal_value(lfjy__ulelp))
        if rlqam__vivh in ('sum', 'cumsum'):
            data = to_str_arr_if_dict_array(data)
        if name_operation == 'cumprod':
            if not isinstance(data.dtype, (types.Integer, types.Float)):
                raise BodoError(msg)
        if name_operation == 'cumsum':
            if data.dtype != types.unicode_type and data != ArrayItemArrayType(
                string_array_type) and not isinstance(data.dtype, (types.
                Integer, types.Float)):
                raise BodoError(msg)
        if name_operation in ('cummin', 'cummax'):
            if not isinstance(data.dtype, types.Integer
                ) and not is_dtype_nullable(data.dtype):
                raise BodoError(msg)
        if name_operation == 'shift':
            if isinstance(data, (TupleArrayType, ArrayItemArrayType)):
                raise BodoError(msg)
            if isinstance(data.dtype, bodo.hiframes.datetime_timedelta_ext.
                DatetimeTimeDeltaType):
                raise BodoError(
                    f"""column type of {data.dtype} is not supported in groupby built-in function shift.
{dt_err}"""
                    )
        if name_operation == 'transform':
            fngld__xofu, err_msg = get_groupby_output_dtype(data,
                get_literal_value(lfjy__ulelp), grp.df_type.index)
            if err_msg == 'ok':
                data = fngld__xofu
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    zytf__tsffk = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        zytf__tsffk = SeriesType(out_data[0].dtype, data=out_data[0], index
            =index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(zytf__tsffk, *args), rsqek__mzcu


def resolve_gb(grp, args, kws, func_name, typing_context, target_context,
    err_msg=''):
    if func_name in set(list_cumulative) | {'shift', 'transform'}:
        return resolve_transformative(grp, args, kws, err_msg, func_name)
    elif func_name in {'agg', 'aggregate'}:
        return resolve_agg(grp, args, kws, typing_context, target_context)
    else:
        return get_agg_typ(grp, args, func_name, typing_context,
            target_context, kws=kws)


@infer_getattr
class DataframeGroupByAttribute(OverloadedKeyAttributeTemplate):
    key = DataFrameGroupByType
    _attr_set = None

    @bound_function('groupby.agg', no_unliteral=True)
    def resolve_agg(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.aggregate', no_unliteral=True)
    def resolve_aggregate(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'agg', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.sum', no_unliteral=True)
    def resolve_sum(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'sum', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.count', no_unliteral=True)
    def resolve_count(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'count', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.nunique', no_unliteral=True)
    def resolve_nunique(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'nunique', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.median', no_unliteral=True)
    def resolve_median(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'median', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.mean', no_unliteral=True)
    def resolve_mean(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'mean', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.min', no_unliteral=True)
    def resolve_min(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'min', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.max', no_unliteral=True)
    def resolve_max(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'max', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.prod', no_unliteral=True)
    def resolve_prod(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'prod', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.var', no_unliteral=True)
    def resolve_var(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'var', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.std', no_unliteral=True)
    def resolve_std(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'std', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.first', no_unliteral=True)
    def resolve_first(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'first', self.context, numba.core
            .registry.cpu_target.target_context)[0]

    @bound_function('groupby.last', no_unliteral=True)
    def resolve_last(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'last', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmin', no_unliteral=True)
    def resolve_idxmin(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmin', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.idxmax', no_unliteral=True)
    def resolve_idxmax(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'idxmax', self.context, numba.
            core.registry.cpu_target.target_context)[0]

    @bound_function('groupby.size', no_unliteral=True)
    def resolve_size(self, grp, args, kws):
        return resolve_gb(grp, args, kws, 'size', self.context, numba.core.
            registry.cpu_target.target_context)[0]

    @bound_function('groupby.cumsum', no_unliteral=True)
    def resolve_cumsum(self, grp, args, kws):
        msg = (
            'Groupby.cumsum() only supports columns of types integer, float, string or liststring'
            )
        return resolve_gb(grp, args, kws, 'cumsum', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cumprod', no_unliteral=True)
    def resolve_cumprod(self, grp, args, kws):
        msg = (
            'Groupby.cumprod() only supports columns of types integer and float'
            )
        return resolve_gb(grp, args, kws, 'cumprod', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummin', no_unliteral=True)
    def resolve_cummin(self, grp, args, kws):
        msg = (
            'Groupby.cummin() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummin', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.cummax', no_unliteral=True)
    def resolve_cummax(self, grp, args, kws):
        msg = (
            'Groupby.cummax() only supports columns of types integer, float, string, liststring, date, datetime or timedelta'
            )
        return resolve_gb(grp, args, kws, 'cummax', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.shift', no_unliteral=True)
    def resolve_shift(self, grp, args, kws):
        msg = (
            'Column type of list/tuple is not supported in groupby built-in function shift'
            )
        return resolve_gb(grp, args, kws, 'shift', self.context, numba.core
            .registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.pipe', no_unliteral=True)
    def resolve_pipe(self, grp, args, kws):
        return resolve_obj_pipe(self, grp, args, kws, 'GroupBy')

    @bound_function('groupby.transform', no_unliteral=True)
    def resolve_transform(self, grp, args, kws):
        msg = (
            'Groupby.transform() only supports sum, count, min, max, mean, and std operations'
            )
        return resolve_gb(grp, args, kws, 'transform', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.head', no_unliteral=True)
    def resolve_head(self, grp, args, kws):
        msg = 'Unsupported Gropupby head operation.\n'
        return resolve_gb(grp, args, kws, 'head', self.context, numba.core.
            registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.ngroup', no_unliteral=True)
    def resolve_ngroup(self, grp, args, kws):
        msg = 'Unsupported Gropupby head operation.\n'
        return resolve_gb(grp, args, kws, 'ngroup', self.context, numba.
            core.registry.cpu_target.target_context, err_msg=msg)[0]

    @bound_function('groupby.apply', no_unliteral=True)
    def resolve_apply(self, grp, args, kws):
        kws = dict(kws)
        func = args[0] if len(args) > 0 else kws.pop('func', None)
        f_args = tuple(args[1:]) if len(args) > 0 else ()
        ugw__jzhq = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        hqnw__dpnx = isinstance(ugw__jzhq, (SeriesType,
            HeterogeneousSeriesType)
            ) and ugw__jzhq.const_info is not None or not isinstance(ugw__jzhq,
            (SeriesType, DataFrameType))
        if hqnw__dpnx:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                dkw__cwhhj = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                awl__kgp = tuple(grp.df_type.column_index[grp.keys[
                    dyp__gqkv]] for dyp__gqkv in range(len(grp.keys)))
                fhjl__llox = tuple(grp.df_type.data[dal__jujc] for
                    dal__jujc in awl__kgp)
                dkw__cwhhj = MultiIndexType(fhjl__llox, tuple(types.literal
                    (ztb__vmtt) for ztb__vmtt in grp.keys))
            else:
                dal__jujc = grp.df_type.column_index[grp.keys[0]]
                nwzc__xjfhn = grp.df_type.data[dal__jujc]
                dkw__cwhhj = bodo.hiframes.pd_index_ext.array_type_to_index(
                    nwzc__xjfhn, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            qza__bqok = tuple(grp.df_type.data[grp.df_type.column_index[
                uodzn__xbmiu]] for uodzn__xbmiu in grp.keys)
            egqm__koppb = tuple(types.literal(xvjbd__zfnu) for xvjbd__zfnu in
                grp.keys) + get_index_name_types(ugw__jzhq.index)
            if not grp.as_index:
                qza__bqok = types.Array(types.int64, 1, 'C'),
                egqm__koppb = (types.none,) + get_index_name_types(ugw__jzhq
                    .index)
            dkw__cwhhj = MultiIndexType(qza__bqok +
                get_index_data_arr_types(ugw__jzhq.index), egqm__koppb)
        if hqnw__dpnx:
            if isinstance(ugw__jzhq, HeterogeneousSeriesType):
                dmyp__qzan, erjd__cpinb = ugw__jzhq.const_info
                if isinstance(ugw__jzhq.data, bodo.libs.nullable_tuple_ext.
                    NullableTupleType):
                    tbyte__fsvj = ugw__jzhq.data.tuple_typ.types
                elif isinstance(ugw__jzhq.data, types.Tuple):
                    tbyte__fsvj = ugw__jzhq.data.types
                els__zpa = tuple(to_nullable_type(dtype_to_array_type(
                    zxdj__trhbo)) for zxdj__trhbo in tbyte__fsvj)
                dlghh__tdhd = DataFrameType(out_data + els__zpa, dkw__cwhhj,
                    out_columns + erjd__cpinb)
            elif isinstance(ugw__jzhq, SeriesType):
                inu__bagk, erjd__cpinb = ugw__jzhq.const_info
                els__zpa = tuple(to_nullable_type(dtype_to_array_type(
                    ugw__jzhq.dtype)) for dmyp__qzan in range(inu__bagk))
                dlghh__tdhd = DataFrameType(out_data + els__zpa, dkw__cwhhj,
                    out_columns + erjd__cpinb)
            else:
                bnkkz__pqqk = get_udf_out_arr_type(ugw__jzhq)
                if not grp.as_index:
                    dlghh__tdhd = DataFrameType(out_data + (bnkkz__pqqk,),
                        dkw__cwhhj, out_columns + ('',))
                else:
                    dlghh__tdhd = SeriesType(bnkkz__pqqk.dtype, bnkkz__pqqk,
                        dkw__cwhhj, None)
        elif isinstance(ugw__jzhq, SeriesType):
            dlghh__tdhd = SeriesType(ugw__jzhq.dtype, ugw__jzhq.data,
                dkw__cwhhj, ugw__jzhq.name_typ)
        else:
            dlghh__tdhd = DataFrameType(ugw__jzhq.data, dkw__cwhhj,
                ugw__jzhq.columns)
        eqn__agl = gen_apply_pysig(len(f_args), kws.keys())
        gmqi__vhb = (func, *f_args) + tuple(kws.values())
        return signature(dlghh__tdhd, *gmqi__vhb).replace(pysig=eqn__agl)

    def generic_resolve(self, grpby, attr):
        if self._is_existing_attr(attr):
            return
        if attr not in grpby.df_type.columns:
            raise_bodo_error(
                f'groupby: invalid attribute {attr} (column not found in dataframe or unsupported function)'
                )
        return DataFrameGroupByType(grpby.df_type, grpby.keys, (attr,),
            grpby.as_index, grpby.dropna, True, True)


def _get_groupby_apply_udf_out_type(func, grp, f_args, kws, typing_context,
    target_context):
    cvc__xwt = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            zxls__qtyo = grp.selection[0]
            bnkkz__pqqk = cvc__xwt.data[cvc__xwt.column_index[zxls__qtyo]]
            ffud__gyez = SeriesType(bnkkz__pqqk.dtype, bnkkz__pqqk,
                cvc__xwt.index, types.literal(zxls__qtyo))
        else:
            nos__pqg = tuple(cvc__xwt.data[cvc__xwt.column_index[
                uodzn__xbmiu]] for uodzn__xbmiu in grp.selection)
            ffud__gyez = DataFrameType(nos__pqg, cvc__xwt.index, tuple(grp.
                selection))
    else:
        ffud__gyez = cvc__xwt
    vhwuq__ana = ffud__gyez,
    vhwuq__ana += tuple(f_args)
    try:
        ugw__jzhq = get_const_func_output_type(func, vhwuq__ana, kws,
            typing_context, target_context)
    except Exception as wph__fim:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', wph__fim),
            getattr(wph__fim, 'loc', None))
    return ugw__jzhq


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    vhwuq__ana = (grp,) + f_args
    try:
        ugw__jzhq = get_const_func_output_type(func, vhwuq__ana, kws, self.
            context, numba.core.registry.cpu_target.target_context, False)
    except Exception as wph__fim:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', wph__fim),
            getattr(wph__fim, 'loc', None))
    eqn__agl = gen_apply_pysig(len(f_args), kws.keys())
    gmqi__vhb = (func, *f_args) + tuple(kws.values())
    return signature(ugw__jzhq, *gmqi__vhb).replace(pysig=eqn__agl)


def gen_apply_pysig(n_args, kws):
    xspfd__iwtlk = ', '.join(f'arg{dyp__gqkv}' for dyp__gqkv in range(n_args))
    xspfd__iwtlk = xspfd__iwtlk + ', ' if xspfd__iwtlk else ''
    opudf__lmlgt = ', '.join(f"{fya__hcxjh} = ''" for fya__hcxjh in kws)
    mwz__yepaj = f'def apply_stub(func, {xspfd__iwtlk}{opudf__lmlgt}):\n'
    mwz__yepaj += '    pass\n'
    dugv__wzql = {}
    exec(mwz__yepaj, {}, dugv__wzql)
    dul__hwaow = dugv__wzql['apply_stub']
    return numba.core.utils.pysignature(dul__hwaow)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        opvnn__twcur = types.Array(types.int64, 1, 'C')
        zqadz__nyx = _pivot_values.meta
        qpp__nlrsj = len(zqadz__nyx)
        qic__dnul = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        etp__jbe = DataFrameType((opvnn__twcur,) * qpp__nlrsj, qic__dnul,
            tuple(zqadz__nyx))
        return signature(etp__jbe, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    mwz__yepaj = 'def impl(keys, dropna, _is_parallel):\n'
    mwz__yepaj += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    mwz__yepaj += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{dyp__gqkv}])' for dyp__gqkv in range(len(keys
        .types))))
    mwz__yepaj += '    table = arr_info_list_to_table(info_list)\n'
    mwz__yepaj += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    mwz__yepaj += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    mwz__yepaj += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    mwz__yepaj += '    delete_table_decref_arrays(table)\n'
    mwz__yepaj += '    ev.finalize()\n'
    mwz__yepaj += '    return sort_idx, group_labels, ngroups\n'
    dugv__wzql = {}
    exec(mwz__yepaj, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, dugv__wzql)
    ylk__wwz = dugv__wzql['impl']
    return ylk__wwz


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    hruek__hbwe = len(labels)
    gtss__cfd = np.zeros(ngroups, dtype=np.int64)
    uiofl__hqmp = np.zeros(ngroups, dtype=np.int64)
    lkxn__vzns = 0
    rzt__iap = 0
    for dyp__gqkv in range(hruek__hbwe):
        juj__tsebe = labels[dyp__gqkv]
        if juj__tsebe < 0:
            lkxn__vzns += 1
        else:
            rzt__iap += 1
            if dyp__gqkv == hruek__hbwe - 1 or juj__tsebe != labels[
                dyp__gqkv + 1]:
                gtss__cfd[juj__tsebe] = lkxn__vzns
                uiofl__hqmp[juj__tsebe] = lkxn__vzns + rzt__iap
                lkxn__vzns += rzt__iap
                rzt__iap = 0
    return gtss__cfd, uiofl__hqmp


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    ylk__wwz, dmyp__qzan = gen_shuffle_dataframe(df, keys, _is_parallel)
    return ylk__wwz


def gen_shuffle_dataframe(df, keys, _is_parallel):
    inu__bagk = len(df.columns)
    fesh__mjmgy = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    mwz__yepaj = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        mwz__yepaj += '  return df, keys, get_null_shuffle_info()\n'
        dugv__wzql = {}
        exec(mwz__yepaj, {'get_null_shuffle_info': get_null_shuffle_info},
            dugv__wzql)
        ylk__wwz = dugv__wzql['impl']
        return ylk__wwz
    for dyp__gqkv in range(inu__bagk):
        mwz__yepaj += f"""  in_arr{dyp__gqkv} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {dyp__gqkv})
"""
    mwz__yepaj += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    mwz__yepaj += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{dyp__gqkv}])' for dyp__gqkv in range(
        fesh__mjmgy)), ', '.join(f'array_to_info(in_arr{dyp__gqkv})' for
        dyp__gqkv in range(inu__bagk)), 'array_to_info(in_index_arr)')
    mwz__yepaj += '  table = arr_info_list_to_table(info_list)\n'
    mwz__yepaj += (
        f'  out_table = shuffle_table(table, {fesh__mjmgy}, _is_parallel, 1)\n'
        )
    for dyp__gqkv in range(fesh__mjmgy):
        mwz__yepaj += f"""  out_key{dyp__gqkv} = info_to_array(info_from_table(out_table, {dyp__gqkv}), keys{dyp__gqkv}_typ)
"""
    for dyp__gqkv in range(inu__bagk):
        mwz__yepaj += f"""  out_arr{dyp__gqkv} = info_to_array(info_from_table(out_table, {dyp__gqkv + fesh__mjmgy}), in_arr{dyp__gqkv}_typ)
"""
    mwz__yepaj += f"""  out_arr_index = info_to_array(info_from_table(out_table, {fesh__mjmgy + inu__bagk}), ind_arr_typ)
"""
    mwz__yepaj += '  shuffle_info = get_shuffle_info(out_table)\n'
    mwz__yepaj += '  delete_table(out_table)\n'
    mwz__yepaj += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{dyp__gqkv}' for dyp__gqkv in range(
        inu__bagk))
    mwz__yepaj += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    mwz__yepaj += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    mwz__yepaj += '  return out_df, ({},), shuffle_info\n'.format(', '.join
        (f'out_key{dyp__gqkv}' for dyp__gqkv in range(fesh__mjmgy)))
    uud__uik = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    uud__uik.update({f'keys{dyp__gqkv}_typ': keys.types[dyp__gqkv] for
        dyp__gqkv in range(fesh__mjmgy)})
    uud__uik.update({f'in_arr{dyp__gqkv}_typ': df.data[dyp__gqkv] for
        dyp__gqkv in range(inu__bagk)})
    dugv__wzql = {}
    exec(mwz__yepaj, uud__uik, dugv__wzql)
    ylk__wwz = dugv__wzql['impl']
    return ylk__wwz, uud__uik


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        vnaey__rcv = len(data.array_types)
        mwz__yepaj = 'def impl(data, shuffle_info):\n'
        mwz__yepaj += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{dyp__gqkv}])' for dyp__gqkv in
            range(vnaey__rcv)))
        mwz__yepaj += '  table = arr_info_list_to_table(info_list)\n'
        mwz__yepaj += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for dyp__gqkv in range(vnaey__rcv):
            mwz__yepaj += f"""  out_arr{dyp__gqkv} = info_to_array(info_from_table(out_table, {dyp__gqkv}), data._data[{dyp__gqkv}])
"""
        mwz__yepaj += '  delete_table(out_table)\n'
        mwz__yepaj += '  delete_table(table)\n'
        mwz__yepaj += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{dyp__gqkv}' for dyp__gqkv in range(
            vnaey__rcv))))
        dugv__wzql = {}
        exec(mwz__yepaj, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, dugv__wzql)
        ylk__wwz = dugv__wzql['impl']
        return ylk__wwz
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            hjxfb__hwxq = bodo.utils.conversion.index_to_array(data)
            yxt__edh = reverse_shuffle(hjxfb__hwxq, shuffle_info)
            return bodo.utils.conversion.index_from_array(yxt__edh)
        return impl_index

    def impl_arr(data, shuffle_info):
        jejpl__mcu = [array_to_info(data)]
        yepbv__hqpdj = arr_info_list_to_table(jejpl__mcu)
        dtns__dtyr = reverse_shuffle_table(yepbv__hqpdj, shuffle_info)
        yxt__edh = info_to_array(info_from_table(dtns__dtyr, 0), data)
        delete_table(dtns__dtyr)
        delete_table(yepbv__hqpdj)
        return yxt__edh
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    hcnkq__dsj = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    bvucq__jzm = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', hcnkq__dsj, bvucq__jzm,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    osah__houxp = get_overload_const_bool(ascending)
    xwi__ffplr = grp.selection[0]
    mwz__yepaj = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    vrpf__ntfm = (
        f"lambda S: S.value_counts(ascending={osah__houxp}, _index_name='{xwi__ffplr}')"
        )
    mwz__yepaj += f'    return grp.apply({vrpf__ntfm})\n'
    dugv__wzql = {}
    exec(mwz__yepaj, {'bodo': bodo}, dugv__wzql)
    ylk__wwz = dugv__wzql['impl']
    return ylk__wwz


groupby_unsupported_attr = {'groups', 'indices'}
groupby_unsupported = {'__iter__', 'get_group', 'all', 'any', 'bfill',
    'backfill', 'cumcount', 'cummax', 'cummin', 'cumprod', 'ffill', 'nth',
    'ohlc', 'pad', 'rank', 'pct_change', 'sem', 'tail', 'corr', 'cov',
    'describe', 'diff', 'fillna', 'filter', 'hist', 'mad', 'plot',
    'quantile', 'resample', 'sample', 'skew', 'take', 'tshift'}
series_only_unsupported_attrs = {'is_monotonic_increasing',
    'is_monotonic_decreasing'}
series_only_unsupported = {'nlargest', 'nsmallest', 'unique'}
dataframe_only_unsupported = {'corrwith', 'boxplot'}


def _install_groupby_unsupported():
    for psey__plf in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, psey__plf, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{psey__plf}'))
    for psey__plf in groupby_unsupported:
        overload_method(DataFrameGroupByType, psey__plf, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{psey__plf}'))
    for psey__plf in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, psey__plf, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{psey__plf}'))
    for psey__plf in series_only_unsupported:
        overload_method(DataFrameGroupByType, psey__plf, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{psey__plf}'))
    for psey__plf in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, psey__plf, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{psey__plf}'))


_install_groupby_unsupported()
