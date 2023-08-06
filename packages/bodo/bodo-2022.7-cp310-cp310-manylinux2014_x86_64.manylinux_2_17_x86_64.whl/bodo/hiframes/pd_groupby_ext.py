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
        oiy__ulp = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, oiy__ulp)


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
        lezlw__merg = args[0]
        rylnf__bfwa = signature.return_type
        cdlhd__upwoy = cgutils.create_struct_proxy(rylnf__bfwa)(context,
            builder)
        cdlhd__upwoy.obj = lezlw__merg
        context.nrt.incref(builder, signature.args[0], lezlw__merg)
        return cdlhd__upwoy._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for lax__zfsmh in keys:
        selection.remove(lax__zfsmh)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    rylnf__bfwa = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return rylnf__bfwa(obj_type, by_type, as_index_type, dropna_type), codegen


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
        grpby, ehbdk__qgbz = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(ehbdk__qgbz, (tuple, list)):
                if len(set(ehbdk__qgbz).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(ehbdk__qgbz).difference(set(grpby.
                        df_type.columns))))
                selection = ehbdk__qgbz
            else:
                if ehbdk__qgbz not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(ehbdk__qgbz))
                selection = ehbdk__qgbz,
                series_select = True
            lios__phyy = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(lios__phyy, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, ehbdk__qgbz = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            ehbdk__qgbz):
            lios__phyy = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(ehbdk__qgbz)), {}).return_type
            return signature(lios__phyy, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    ixdi__zdsid = arr_type == ArrayItemArrayType(string_array_type)
    butn__itnym = arr_type.dtype
    if isinstance(butn__itnym, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {butn__itnym} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(butn__itnym, (
        Decimal128Type, types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {butn__itnym} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(butn__itnym
        , (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(butn__itnym, (types.Integer, types.Float, types.Boolean)
        ):
        if ixdi__zdsid or butn__itnym == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(butn__itnym, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not butn__itnym.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {butn__itnym} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(butn__itnym, types.Boolean) and func_name in {'cumsum',
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
    butn__itnym = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(butn__itnym, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(butn__itnym, types.Integer):
            return IntDtype(butn__itnym)
        return butn__itnym
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        oaapn__cxjox = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{oaapn__cxjox}'."
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
    for lax__zfsmh in grp.keys:
        if multi_level_names:
            frf__ddtg = lax__zfsmh, ''
        else:
            frf__ddtg = lax__zfsmh
        ocfj__bzzd = grp.df_type.column_index[lax__zfsmh]
        data = grp.df_type.data[ocfj__bzzd]
        out_columns.append(frf__ddtg)
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
        kask__agzub = tuple(grp.df_type.column_index[grp.keys[ico__sij]] for
            ico__sij in range(len(grp.keys)))
        zoe__jtjjq = tuple(grp.df_type.data[ocfj__bzzd] for ocfj__bzzd in
            kask__agzub)
        index = MultiIndexType(zoe__jtjjq, tuple(types.StringLiteral(
            lax__zfsmh) for lax__zfsmh in grp.keys))
    else:
        ocfj__bzzd = grp.df_type.column_index[grp.keys[0]]
        xybi__nvh = grp.df_type.data[ocfj__bzzd]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(xybi__nvh,
            types.StringLiteral(grp.keys[0]))
    pic__oxjcp = {}
    ynubv__bfzxt = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        pic__oxjcp[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        pic__oxjcp[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        snc__wxco = dict(ascending=ascending)
        qvn__ypken = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', snc__wxco,
            qvn__ypken, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for htn__loj in columns:
            ocfj__bzzd = grp.df_type.column_index[htn__loj]
            data = grp.df_type.data[ocfj__bzzd]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            woz__jdqwh = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                woz__jdqwh = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    nqsc__wnh = SeriesType(data.dtype, data, None, string_type)
                    oqg__ejpz = get_const_func_output_type(func, (nqsc__wnh
                        ,), {}, typing_context, target_context)
                    if oqg__ejpz != ArrayItemArrayType(string_array_type):
                        oqg__ejpz = dtype_to_array_type(oqg__ejpz)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=htn__loj, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    htp__jaa = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    dxs__ohsgm = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    snc__wxco = dict(numeric_only=htp__jaa, min_count=
                        dxs__ohsgm)
                    qvn__ypken = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        snc__wxco, qvn__ypken, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    htp__jaa = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    dxs__ohsgm = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    snc__wxco = dict(numeric_only=htp__jaa, min_count=
                        dxs__ohsgm)
                    qvn__ypken = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        snc__wxco, qvn__ypken, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    htp__jaa = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    snc__wxco = dict(numeric_only=htp__jaa)
                    qvn__ypken = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        snc__wxco, qvn__ypken, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    old__naqez = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    qprrr__fhkw = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    snc__wxco = dict(axis=old__naqez, skipna=qprrr__fhkw)
                    qvn__ypken = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        snc__wxco, qvn__ypken, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    cwdt__eyvvs = args[0] if len(args) > 0 else kws.pop('ddof',
                        1)
                    snc__wxco = dict(ddof=cwdt__eyvvs)
                    qvn__ypken = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        snc__wxco, qvn__ypken, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                oqg__ejpz, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                oqg__ejpz = to_str_arr_if_dict_array(oqg__ejpz
                    ) if func_name in ('sum', 'cumsum') else oqg__ejpz
                out_data.append(oqg__ejpz)
                out_columns.append(htn__loj)
                if func_name == 'agg':
                    xbou__hilaj = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    pic__oxjcp[htn__loj, xbou__hilaj] = htn__loj
                else:
                    pic__oxjcp[htn__loj, func_name] = htn__loj
                out_column_type.append(woz__jdqwh)
            else:
                ynubv__bfzxt.append(err_msg)
    if func_name == 'sum':
        war__qiv = any([(euk__ktu == ColumnType.NumericalColumn.value) for
            euk__ktu in out_column_type])
        if war__qiv:
            out_data = [euk__ktu for euk__ktu, buga__efpwj in zip(out_data,
                out_column_type) if buga__efpwj != ColumnType.
                NonNumericalColumn.value]
            out_columns = [euk__ktu for euk__ktu, buga__efpwj in zip(
                out_columns, out_column_type) if buga__efpwj != ColumnType.
                NonNumericalColumn.value]
            pic__oxjcp = {}
            for htn__loj in out_columns:
                if grp.as_index is False and htn__loj in grp.keys:
                    continue
                pic__oxjcp[htn__loj, func_name] = htn__loj
    nfu__tedr = len(ynubv__bfzxt)
    if len(out_data) == 0:
        if nfu__tedr == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(nfu__tedr, ' was' if nfu__tedr == 1 else 's were',
                ','.join(ynubv__bfzxt)))
    ypz__qtnyz = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            crt__xsip = IntDtype(out_data[0].dtype)
        else:
            crt__xsip = out_data[0].dtype
        tnys__bxc = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        ypz__qtnyz = SeriesType(crt__xsip, data=out_data[0], index=index,
            name_typ=tnys__bxc)
    return signature(ypz__qtnyz, *args), pic__oxjcp


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    xoem__hqquo = True
    if isinstance(f_val, str):
        xoem__hqquo = False
        xigii__lqm = f_val
    elif is_overload_constant_str(f_val):
        xoem__hqquo = False
        xigii__lqm = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        xoem__hqquo = False
        xigii__lqm = bodo.utils.typing.get_builtin_function_name(f_val)
    if not xoem__hqquo:
        if xigii__lqm not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {xigii__lqm}')
        lios__phyy = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(lios__phyy, (), xigii__lqm, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            bgmfy__qlkg = types.functions.MakeFunctionLiteral(f_val)
        else:
            bgmfy__qlkg = f_val
        validate_udf('agg', bgmfy__qlkg)
        func = get_overload_const_func(bgmfy__qlkg, None)
        glrqq__noqf = func.code if hasattr(func, 'code') else func.__code__
        xigii__lqm = glrqq__noqf.co_name
        lios__phyy = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(lios__phyy, (), 'agg', typing_context,
            target_context, bgmfy__qlkg)[0].return_type
    return xigii__lqm, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    cvuzi__vroli = kws and all(isinstance(ycqa__dmeap, types.Tuple) and len
        (ycqa__dmeap) == 2 for ycqa__dmeap in kws.values())
    if is_overload_none(func) and not cvuzi__vroli:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not cvuzi__vroli:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    ahkg__npkv = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if cvuzi__vroli or is_overload_constant_dict(func):
        if cvuzi__vroli:
            fgrnz__fon = [get_literal_value(vzsp__ehha) for vzsp__ehha,
                dpny__lxsem in kws.values()]
            lnisz__treii = [get_literal_value(iyqq__uawp) for dpny__lxsem,
                iyqq__uawp in kws.values()]
        else:
            ofc__nypu = get_overload_constant_dict(func)
            fgrnz__fon = tuple(ofc__nypu.keys())
            lnisz__treii = tuple(ofc__nypu.values())
        for ggizv__exge in ('head', 'ngroup'):
            if ggizv__exge in lnisz__treii:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {ggizv__exge} cannot be mixed with other groupby operations.'
                    )
        if any(htn__loj not in grp.selection and htn__loj not in grp.keys for
            htn__loj in fgrnz__fon):
            raise_bodo_error(
                f'Selected column names {fgrnz__fon} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            lnisz__treii)
        if cvuzi__vroli and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        pic__oxjcp = {}
        out_columns = []
        out_data = []
        out_column_type = []
        azz__ppdn = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for rfa__wgts, f_val in zip(fgrnz__fon, lnisz__treii):
            if isinstance(f_val, (tuple, list)):
                espzr__gnv = 0
                for bgmfy__qlkg in f_val:
                    xigii__lqm, out_tp = get_agg_funcname_and_outtyp(grp,
                        rfa__wgts, bgmfy__qlkg, typing_context, target_context)
                    ahkg__npkv = xigii__lqm in list_cumulative
                    if xigii__lqm == '<lambda>' and len(f_val) > 1:
                        xigii__lqm = '<lambda_' + str(espzr__gnv) + '>'
                        espzr__gnv += 1
                    out_columns.append((rfa__wgts, xigii__lqm))
                    pic__oxjcp[rfa__wgts, xigii__lqm] = rfa__wgts, xigii__lqm
                    _append_out_type(grp, out_data, out_tp)
            else:
                xigii__lqm, out_tp = get_agg_funcname_and_outtyp(grp,
                    rfa__wgts, f_val, typing_context, target_context)
                ahkg__npkv = xigii__lqm in list_cumulative
                if multi_level_names:
                    out_columns.append((rfa__wgts, xigii__lqm))
                    pic__oxjcp[rfa__wgts, xigii__lqm] = rfa__wgts, xigii__lqm
                elif not cvuzi__vroli:
                    out_columns.append(rfa__wgts)
                    pic__oxjcp[rfa__wgts, xigii__lqm] = rfa__wgts
                elif cvuzi__vroli:
                    azz__ppdn.append(xigii__lqm)
                _append_out_type(grp, out_data, out_tp)
        if cvuzi__vroli:
            for ico__sij, lgoh__ehb in enumerate(kws.keys()):
                out_columns.append(lgoh__ehb)
                pic__oxjcp[fgrnz__fon[ico__sij], azz__ppdn[ico__sij]
                    ] = lgoh__ehb
        if ahkg__npkv:
            index = grp.df_type.index
        else:
            index = out_tp.index
        ypz__qtnyz = DataFrameType(tuple(out_data), index, tuple(
            out_columns), is_table_format=True)
        return signature(ypz__qtnyz, *args), pic__oxjcp
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            wriag__mtvjk = get_overload_const_list(func)
        else:
            wriag__mtvjk = func.types
        if len(wriag__mtvjk) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        espzr__gnv = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        pic__oxjcp = {}
        cwi__nosam = grp.selection[0]
        for f_val in wriag__mtvjk:
            xigii__lqm, out_tp = get_agg_funcname_and_outtyp(grp,
                cwi__nosam, f_val, typing_context, target_context)
            ahkg__npkv = xigii__lqm in list_cumulative
            if xigii__lqm == '<lambda>' and len(wriag__mtvjk) > 1:
                xigii__lqm = '<lambda_' + str(espzr__gnv) + '>'
                espzr__gnv += 1
            out_columns.append(xigii__lqm)
            pic__oxjcp[cwi__nosam, xigii__lqm] = xigii__lqm
            _append_out_type(grp, out_data, out_tp)
        if ahkg__npkv:
            index = grp.df_type.index
        else:
            index = out_tp.index
        ypz__qtnyz = DataFrameType(tuple(out_data), index, tuple(
            out_columns), is_table_format=True)
        return signature(ypz__qtnyz, *args), pic__oxjcp
    xigii__lqm = ''
    if types.unliteral(func) == types.unicode_type:
        xigii__lqm = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        xigii__lqm = bodo.utils.typing.get_builtin_function_name(func)
    if xigii__lqm:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, xigii__lqm, typing_context, kws)
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
        old__naqez = args[0] if len(args) > 0 else kws.pop('axis', 0)
        htp__jaa = args[1] if len(args) > 1 else kws.pop('numeric_only', False)
        qprrr__fhkw = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        snc__wxco = dict(axis=old__naqez, numeric_only=htp__jaa)
        qvn__ypken = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', snc__wxco,
            qvn__ypken, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        pnoyq__dsmk = args[0] if len(args) > 0 else kws.pop('periods', 1)
        oznkl__rbg = args[1] if len(args) > 1 else kws.pop('freq', None)
        old__naqez = args[2] if len(args) > 2 else kws.pop('axis', 0)
        itiw__xqu = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        snc__wxco = dict(freq=oznkl__rbg, axis=old__naqez, fill_value=itiw__xqu
            )
        qvn__ypken = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', snc__wxco,
            qvn__ypken, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        uib__uigk = args[0] if len(args) > 0 else kws.pop('func', None)
        gfvgf__herpa = kws.pop('engine', None)
        eoxg__jvu = kws.pop('engine_kwargs', None)
        snc__wxco = dict(engine=gfvgf__herpa, engine_kwargs=eoxg__jvu)
        qvn__ypken = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', snc__wxco, qvn__ypken,
            package_name='pandas', module_name='GroupBy')
    pic__oxjcp = {}
    for htn__loj in grp.selection:
        out_columns.append(htn__loj)
        pic__oxjcp[htn__loj, name_operation] = htn__loj
        ocfj__bzzd = grp.df_type.column_index[htn__loj]
        data = grp.df_type.data[ocfj__bzzd]
        vbdg__yjfbf = (name_operation if name_operation != 'transform' else
            get_literal_value(uib__uigk))
        if vbdg__yjfbf in ('sum', 'cumsum'):
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
            oqg__ejpz, err_msg = get_groupby_output_dtype(data,
                get_literal_value(uib__uigk), grp.df_type.index)
            if err_msg == 'ok':
                data = oqg__ejpz
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    ypz__qtnyz = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        ypz__qtnyz = SeriesType(out_data[0].dtype, data=out_data[0], index=
            index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(ypz__qtnyz, *args), pic__oxjcp


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
        bon__hxpql = _get_groupby_apply_udf_out_type(func, grp, f_args, kws,
            self.context, numba.core.registry.cpu_target.target_context)
        aomv__fthaq = isinstance(bon__hxpql, (SeriesType,
            HeterogeneousSeriesType)
            ) and bon__hxpql.const_info is not None or not isinstance(
            bon__hxpql, (SeriesType, DataFrameType))
        if aomv__fthaq:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                cmc__abkax = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                kask__agzub = tuple(grp.df_type.column_index[grp.keys[
                    ico__sij]] for ico__sij in range(len(grp.keys)))
                zoe__jtjjq = tuple(grp.df_type.data[ocfj__bzzd] for
                    ocfj__bzzd in kask__agzub)
                cmc__abkax = MultiIndexType(zoe__jtjjq, tuple(types.literal
                    (lax__zfsmh) for lax__zfsmh in grp.keys))
            else:
                ocfj__bzzd = grp.df_type.column_index[grp.keys[0]]
                xybi__nvh = grp.df_type.data[ocfj__bzzd]
                cmc__abkax = bodo.hiframes.pd_index_ext.array_type_to_index(
                    xybi__nvh, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            mwn__pfi = tuple(grp.df_type.data[grp.df_type.column_index[
                htn__loj]] for htn__loj in grp.keys)
            rspm__iltcs = tuple(types.literal(ycqa__dmeap) for ycqa__dmeap in
                grp.keys) + get_index_name_types(bon__hxpql.index)
            if not grp.as_index:
                mwn__pfi = types.Array(types.int64, 1, 'C'),
                rspm__iltcs = (types.none,) + get_index_name_types(bon__hxpql
                    .index)
            cmc__abkax = MultiIndexType(mwn__pfi + get_index_data_arr_types
                (bon__hxpql.index), rspm__iltcs)
        if aomv__fthaq:
            if isinstance(bon__hxpql, HeterogeneousSeriesType):
                dpny__lxsem, smelb__csq = bon__hxpql.const_info
                if isinstance(bon__hxpql.data, bodo.libs.nullable_tuple_ext
                    .NullableTupleType):
                    dqd__uju = bon__hxpql.data.tuple_typ.types
                elif isinstance(bon__hxpql.data, types.Tuple):
                    dqd__uju = bon__hxpql.data.types
                wrjv__ahjye = tuple(to_nullable_type(dtype_to_array_type(
                    xts__phcm)) for xts__phcm in dqd__uju)
                ykw__wsptn = DataFrameType(out_data + wrjv__ahjye,
                    cmc__abkax, out_columns + smelb__csq)
            elif isinstance(bon__hxpql, SeriesType):
                fwbt__fnj, smelb__csq = bon__hxpql.const_info
                wrjv__ahjye = tuple(to_nullable_type(dtype_to_array_type(
                    bon__hxpql.dtype)) for dpny__lxsem in range(fwbt__fnj))
                ykw__wsptn = DataFrameType(out_data + wrjv__ahjye,
                    cmc__abkax, out_columns + smelb__csq)
            else:
                mwesg__xyry = get_udf_out_arr_type(bon__hxpql)
                if not grp.as_index:
                    ykw__wsptn = DataFrameType(out_data + (mwesg__xyry,),
                        cmc__abkax, out_columns + ('',))
                else:
                    ykw__wsptn = SeriesType(mwesg__xyry.dtype, mwesg__xyry,
                        cmc__abkax, None)
        elif isinstance(bon__hxpql, SeriesType):
            ykw__wsptn = SeriesType(bon__hxpql.dtype, bon__hxpql.data,
                cmc__abkax, bon__hxpql.name_typ)
        else:
            ykw__wsptn = DataFrameType(bon__hxpql.data, cmc__abkax,
                bon__hxpql.columns)
        iidxf__rmfv = gen_apply_pysig(len(f_args), kws.keys())
        ugy__xqzx = (func, *f_args) + tuple(kws.values())
        return signature(ykw__wsptn, *ugy__xqzx).replace(pysig=iidxf__rmfv)

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
    zfitp__vwhm = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            rfa__wgts = grp.selection[0]
            mwesg__xyry = zfitp__vwhm.data[zfitp__vwhm.column_index[rfa__wgts]]
            oxt__vhkf = SeriesType(mwesg__xyry.dtype, mwesg__xyry,
                zfitp__vwhm.index, types.literal(rfa__wgts))
        else:
            itv__yhde = tuple(zfitp__vwhm.data[zfitp__vwhm.column_index[
                htn__loj]] for htn__loj in grp.selection)
            oxt__vhkf = DataFrameType(itv__yhde, zfitp__vwhm.index, tuple(
                grp.selection))
    else:
        oxt__vhkf = zfitp__vwhm
    xzzp__gep = oxt__vhkf,
    xzzp__gep += tuple(f_args)
    try:
        bon__hxpql = get_const_func_output_type(func, xzzp__gep, kws,
            typing_context, target_context)
    except Exception as pejt__lkz:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', pejt__lkz),
            getattr(pejt__lkz, 'loc', None))
    return bon__hxpql


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    xzzp__gep = (grp,) + f_args
    try:
        bon__hxpql = get_const_func_output_type(func, xzzp__gep, kws, self.
            context, numba.core.registry.cpu_target.target_context, False)
    except Exception as pejt__lkz:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', pejt__lkz),
            getattr(pejt__lkz, 'loc', None))
    iidxf__rmfv = gen_apply_pysig(len(f_args), kws.keys())
    ugy__xqzx = (func, *f_args) + tuple(kws.values())
    return signature(bon__hxpql, *ugy__xqzx).replace(pysig=iidxf__rmfv)


def gen_apply_pysig(n_args, kws):
    ktk__tes = ', '.join(f'arg{ico__sij}' for ico__sij in range(n_args))
    ktk__tes = ktk__tes + ', ' if ktk__tes else ''
    iqe__qdp = ', '.join(f"{pyh__mrh} = ''" for pyh__mrh in kws)
    rharo__pkm = f'def apply_stub(func, {ktk__tes}{iqe__qdp}):\n'
    rharo__pkm += '    pass\n'
    uwjhs__unfrr = {}
    exec(rharo__pkm, {}, uwjhs__unfrr)
    qwqqs__ppj = uwjhs__unfrr['apply_stub']
    return numba.core.utils.pysignature(qwqqs__ppj)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        ehrqn__ajt = types.Array(types.int64, 1, 'C')
        dkzx__vflk = _pivot_values.meta
        fcqo__pnqrw = len(dkzx__vflk)
        opxvi__yssj = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        vbn__wce = DataFrameType((ehrqn__ajt,) * fcqo__pnqrw, opxvi__yssj,
            tuple(dkzx__vflk))
        return signature(vbn__wce, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    rharo__pkm = 'def impl(keys, dropna, _is_parallel):\n'
    rharo__pkm += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    rharo__pkm += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{ico__sij}])' for ico__sij in range(len(keys.
        types))))
    rharo__pkm += '    table = arr_info_list_to_table(info_list)\n'
    rharo__pkm += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    rharo__pkm += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    rharo__pkm += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    rharo__pkm += '    delete_table_decref_arrays(table)\n'
    rharo__pkm += '    ev.finalize()\n'
    rharo__pkm += '    return sort_idx, group_labels, ngroups\n'
    uwjhs__unfrr = {}
    exec(rharo__pkm, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, uwjhs__unfrr
        )
    hymt__abi = uwjhs__unfrr['impl']
    return hymt__abi


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    qphya__aio = len(labels)
    dvxa__qie = np.zeros(ngroups, dtype=np.int64)
    owi__jrudr = np.zeros(ngroups, dtype=np.int64)
    rracx__lnw = 0
    vmy__jfgfn = 0
    for ico__sij in range(qphya__aio):
        trww__mdnck = labels[ico__sij]
        if trww__mdnck < 0:
            rracx__lnw += 1
        else:
            vmy__jfgfn += 1
            if ico__sij == qphya__aio - 1 or trww__mdnck != labels[ico__sij + 1
                ]:
                dvxa__qie[trww__mdnck] = rracx__lnw
                owi__jrudr[trww__mdnck] = rracx__lnw + vmy__jfgfn
                rracx__lnw += vmy__jfgfn
                vmy__jfgfn = 0
    return dvxa__qie, owi__jrudr


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    hymt__abi, dpny__lxsem = gen_shuffle_dataframe(df, keys, _is_parallel)
    return hymt__abi


def gen_shuffle_dataframe(df, keys, _is_parallel):
    fwbt__fnj = len(df.columns)
    ospne__tfqe = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    rharo__pkm = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        rharo__pkm += '  return df, keys, get_null_shuffle_info()\n'
        uwjhs__unfrr = {}
        exec(rharo__pkm, {'get_null_shuffle_info': get_null_shuffle_info},
            uwjhs__unfrr)
        hymt__abi = uwjhs__unfrr['impl']
        return hymt__abi
    for ico__sij in range(fwbt__fnj):
        rharo__pkm += f"""  in_arr{ico__sij} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ico__sij})
"""
    rharo__pkm += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    rharo__pkm += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{ico__sij}])' for ico__sij in range(
        ospne__tfqe)), ', '.join(f'array_to_info(in_arr{ico__sij})' for
        ico__sij in range(fwbt__fnj)), 'array_to_info(in_index_arr)')
    rharo__pkm += '  table = arr_info_list_to_table(info_list)\n'
    rharo__pkm += (
        f'  out_table = shuffle_table(table, {ospne__tfqe}, _is_parallel, 1)\n'
        )
    for ico__sij in range(ospne__tfqe):
        rharo__pkm += f"""  out_key{ico__sij} = info_to_array(info_from_table(out_table, {ico__sij}), keys{ico__sij}_typ)
"""
    for ico__sij in range(fwbt__fnj):
        rharo__pkm += f"""  out_arr{ico__sij} = info_to_array(info_from_table(out_table, {ico__sij + ospne__tfqe}), in_arr{ico__sij}_typ)
"""
    rharo__pkm += f"""  out_arr_index = info_to_array(info_from_table(out_table, {ospne__tfqe + fwbt__fnj}), ind_arr_typ)
"""
    rharo__pkm += '  shuffle_info = get_shuffle_info(out_table)\n'
    rharo__pkm += '  delete_table(out_table)\n'
    rharo__pkm += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{ico__sij}' for ico__sij in range(fwbt__fnj))
    rharo__pkm += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    rharo__pkm += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    rharo__pkm += '  return out_df, ({},), shuffle_info\n'.format(', '.join
        (f'out_key{ico__sij}' for ico__sij in range(ospne__tfqe)))
    cvhyr__ojhio = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    cvhyr__ojhio.update({f'keys{ico__sij}_typ': keys.types[ico__sij] for
        ico__sij in range(ospne__tfqe)})
    cvhyr__ojhio.update({f'in_arr{ico__sij}_typ': df.data[ico__sij] for
        ico__sij in range(fwbt__fnj)})
    uwjhs__unfrr = {}
    exec(rharo__pkm, cvhyr__ojhio, uwjhs__unfrr)
    hymt__abi = uwjhs__unfrr['impl']
    return hymt__abi, cvhyr__ojhio


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        tnonb__mrm = len(data.array_types)
        rharo__pkm = 'def impl(data, shuffle_info):\n'
        rharo__pkm += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{ico__sij}])' for ico__sij in range(
            tnonb__mrm)))
        rharo__pkm += '  table = arr_info_list_to_table(info_list)\n'
        rharo__pkm += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for ico__sij in range(tnonb__mrm):
            rharo__pkm += f"""  out_arr{ico__sij} = info_to_array(info_from_table(out_table, {ico__sij}), data._data[{ico__sij}])
"""
        rharo__pkm += '  delete_table(out_table)\n'
        rharo__pkm += '  delete_table(table)\n'
        rharo__pkm += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{ico__sij}' for ico__sij in range(
            tnonb__mrm))))
        uwjhs__unfrr = {}
        exec(rharo__pkm, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, uwjhs__unfrr)
        hymt__abi = uwjhs__unfrr['impl']
        return hymt__abi
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            ncio__wqbz = bodo.utils.conversion.index_to_array(data)
            owpel__hwq = reverse_shuffle(ncio__wqbz, shuffle_info)
            return bodo.utils.conversion.index_from_array(owpel__hwq)
        return impl_index

    def impl_arr(data, shuffle_info):
        lzryd__uvrii = [array_to_info(data)]
        lviqd__xxfl = arr_info_list_to_table(lzryd__uvrii)
        sef__euwme = reverse_shuffle_table(lviqd__xxfl, shuffle_info)
        owpel__hwq = info_to_array(info_from_table(sef__euwme, 0), data)
        delete_table(sef__euwme)
        delete_table(lviqd__xxfl)
        return owpel__hwq
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    snc__wxco = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    qvn__ypken = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', snc__wxco, qvn__ypken,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    tcur__gfeeq = get_overload_const_bool(ascending)
    crzgx__cwel = grp.selection[0]
    rharo__pkm = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    cib__cuxj = (
        f"lambda S: S.value_counts(ascending={tcur__gfeeq}, _index_name='{crzgx__cwel}')"
        )
    rharo__pkm += f'    return grp.apply({cib__cuxj})\n'
    uwjhs__unfrr = {}
    exec(rharo__pkm, {'bodo': bodo}, uwjhs__unfrr)
    hymt__abi = uwjhs__unfrr['impl']
    return hymt__abi


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
    for gooh__zate in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, gooh__zate, no_unliteral=True
            )(create_unsupported_overload(f'DataFrameGroupBy.{gooh__zate}'))
    for gooh__zate in groupby_unsupported:
        overload_method(DataFrameGroupByType, gooh__zate, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{gooh__zate}'))
    for gooh__zate in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, gooh__zate, no_unliteral=True
            )(create_unsupported_overload(f'SeriesGroupBy.{gooh__zate}'))
    for gooh__zate in series_only_unsupported:
        overload_method(DataFrameGroupByType, gooh__zate, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{gooh__zate}'))
    for gooh__zate in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, gooh__zate, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{gooh__zate}'))


_install_groupby_unsupported()
