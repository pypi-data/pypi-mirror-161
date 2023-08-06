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
        mjv__dmre = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, mjv__dmre)


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
        siy__qwrnp = args[0]
        bsvzk__rgrm = signature.return_type
        thcro__bwk = cgutils.create_struct_proxy(bsvzk__rgrm)(context, builder)
        thcro__bwk.obj = siy__qwrnp
        context.nrt.incref(builder, signature.args[0], siy__qwrnp)
        return thcro__bwk._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for uqcd__xra in keys:
        selection.remove(uqcd__xra)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    bsvzk__rgrm = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return bsvzk__rgrm(obj_type, by_type, as_index_type, dropna_type), codegen


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
        grpby, yaqk__peg = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(yaqk__peg, (tuple, list)):
                if len(set(yaqk__peg).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(yaqk__peg).difference(set(grpby.df_type
                        .columns))))
                selection = yaqk__peg
            else:
                if yaqk__peg not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(yaqk__peg))
                selection = yaqk__peg,
                series_select = True
            vnb__sel = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(vnb__sel, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, yaqk__peg = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            yaqk__peg):
            vnb__sel = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(yaqk__peg)), {}).return_type
            return signature(vnb__sel, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    pxt__jvvu = arr_type == ArrayItemArrayType(string_array_type)
    kaf__iczjx = arr_type.dtype
    if isinstance(kaf__iczjx, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {kaf__iczjx} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(kaf__iczjx, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {kaf__iczjx} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(kaf__iczjx,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(kaf__iczjx, (types.Integer, types.Float, types.Boolean)):
        if pxt__jvvu or kaf__iczjx == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(kaf__iczjx, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not kaf__iczjx.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {kaf__iczjx} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(kaf__iczjx, types.Boolean) and func_name in {'cumsum',
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
    kaf__iczjx = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(kaf__iczjx, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(kaf__iczjx, types.Integer):
            return IntDtype(kaf__iczjx)
        return kaf__iczjx
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        tzbpn__ydr = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{tzbpn__ydr}'."
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
    for uqcd__xra in grp.keys:
        if multi_level_names:
            jvm__guvyh = uqcd__xra, ''
        else:
            jvm__guvyh = uqcd__xra
        agib__ihdcu = grp.df_type.column_index[uqcd__xra]
        data = grp.df_type.data[agib__ihdcu]
        out_columns.append(jvm__guvyh)
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
        ndr__hgu = tuple(grp.df_type.column_index[grp.keys[yvty__raum]] for
            yvty__raum in range(len(grp.keys)))
        auy__paar = tuple(grp.df_type.data[agib__ihdcu] for agib__ihdcu in
            ndr__hgu)
        index = MultiIndexType(auy__paar, tuple(types.StringLiteral(
            uqcd__xra) for uqcd__xra in grp.keys))
    else:
        agib__ihdcu = grp.df_type.column_index[grp.keys[0]]
        hjyn__spsh = grp.df_type.data[agib__ihdcu]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(hjyn__spsh,
            types.StringLiteral(grp.keys[0]))
    lvv__pwg = {}
    yqlr__ihql = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        lvv__pwg[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        lvv__pwg[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        var__jau = dict(ascending=ascending)
        uhbg__twed = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', var__jau, uhbg__twed,
            package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for tzix__ybcqs in columns:
            agib__ihdcu = grp.df_type.column_index[tzix__ybcqs]
            data = grp.df_type.data[agib__ihdcu]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            hruh__azre = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                hruh__azre = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    ydtt__cpc = SeriesType(data.dtype, data, None, string_type)
                    phv__tac = get_const_func_output_type(func, (ydtt__cpc,
                        ), {}, typing_context, target_context)
                    if phv__tac != ArrayItemArrayType(string_array_type):
                        phv__tac = dtype_to_array_type(phv__tac)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=tzix__ybcqs, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    vexg__mwzb = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    mijez__iub = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    var__jau = dict(numeric_only=vexg__mwzb, min_count=
                        mijez__iub)
                    uhbg__twed = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}', var__jau,
                        uhbg__twed, package_name='pandas', module_name=
                        'GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    vexg__mwzb = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    mijez__iub = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    var__jau = dict(numeric_only=vexg__mwzb, min_count=
                        mijez__iub)
                    uhbg__twed = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}', var__jau,
                        uhbg__twed, package_name='pandas', module_name=
                        'GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    vexg__mwzb = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    var__jau = dict(numeric_only=vexg__mwzb)
                    uhbg__twed = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}', var__jau,
                        uhbg__twed, package_name='pandas', module_name=
                        'GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    lrggv__nhfxu = args[0] if len(args) > 0 else kws.pop('axis'
                        , 0)
                    iqaym__agz = args[1] if len(args) > 1 else kws.pop('skipna'
                        , True)
                    var__jau = dict(axis=lrggv__nhfxu, skipna=iqaym__agz)
                    uhbg__twed = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}', var__jau,
                        uhbg__twed, package_name='pandas', module_name=
                        'GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    fjnnq__cdd = args[0] if len(args) > 0 else kws.pop('ddof',
                        1)
                    var__jau = dict(ddof=fjnnq__cdd)
                    uhbg__twed = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}', var__jau,
                        uhbg__twed, package_name='pandas', module_name=
                        'GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                phv__tac, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                phv__tac = to_str_arr_if_dict_array(phv__tac) if func_name in (
                    'sum', 'cumsum') else phv__tac
                out_data.append(phv__tac)
                out_columns.append(tzix__ybcqs)
                if func_name == 'agg':
                    fhyk__umlhb = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    lvv__pwg[tzix__ybcqs, fhyk__umlhb] = tzix__ybcqs
                else:
                    lvv__pwg[tzix__ybcqs, func_name] = tzix__ybcqs
                out_column_type.append(hruh__azre)
            else:
                yqlr__ihql.append(err_msg)
    if func_name == 'sum':
        ydzs__nrbfv = any([(olsec__wam == ColumnType.NumericalColumn.value) for
            olsec__wam in out_column_type])
        if ydzs__nrbfv:
            out_data = [olsec__wam for olsec__wam, smhn__cgv in zip(
                out_data, out_column_type) if smhn__cgv != ColumnType.
                NonNumericalColumn.value]
            out_columns = [olsec__wam for olsec__wam, smhn__cgv in zip(
                out_columns, out_column_type) if smhn__cgv != ColumnType.
                NonNumericalColumn.value]
            lvv__pwg = {}
            for tzix__ybcqs in out_columns:
                if grp.as_index is False and tzix__ybcqs in grp.keys:
                    continue
                lvv__pwg[tzix__ybcqs, func_name] = tzix__ybcqs
    ueat__chf = len(yqlr__ihql)
    if len(out_data) == 0:
        if ueat__chf == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(ueat__chf, ' was' if ueat__chf == 1 else 's were',
                ','.join(yqlr__ihql)))
    lqvws__ceukr = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            ekoa__lcz = IntDtype(out_data[0].dtype)
        else:
            ekoa__lcz = out_data[0].dtype
        fri__sgon = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        lqvws__ceukr = SeriesType(ekoa__lcz, data=out_data[0], index=index,
            name_typ=fri__sgon)
    return signature(lqvws__ceukr, *args), lvv__pwg


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    vgbjj__pcd = True
    if isinstance(f_val, str):
        vgbjj__pcd = False
        vqzi__fzcnd = f_val
    elif is_overload_constant_str(f_val):
        vgbjj__pcd = False
        vqzi__fzcnd = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        vgbjj__pcd = False
        vqzi__fzcnd = bodo.utils.typing.get_builtin_function_name(f_val)
    if not vgbjj__pcd:
        if vqzi__fzcnd not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {vqzi__fzcnd}')
        vnb__sel = DataFrameGroupByType(grp.df_type, grp.keys, (col,), grp.
            as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(vnb__sel, (), vqzi__fzcnd, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            nauj__vqabx = types.functions.MakeFunctionLiteral(f_val)
        else:
            nauj__vqabx = f_val
        validate_udf('agg', nauj__vqabx)
        func = get_overload_const_func(nauj__vqabx, None)
        xpu__lcah = func.code if hasattr(func, 'code') else func.__code__
        vqzi__fzcnd = xpu__lcah.co_name
        vnb__sel = DataFrameGroupByType(grp.df_type, grp.keys, (col,), grp.
            as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(vnb__sel, (), 'agg', typing_context,
            target_context, nauj__vqabx)[0].return_type
    return vqzi__fzcnd, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    atbdg__vkkqy = kws and all(isinstance(hldv__esi, types.Tuple) and len(
        hldv__esi) == 2 for hldv__esi in kws.values())
    if is_overload_none(func) and not atbdg__vkkqy:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not atbdg__vkkqy:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    xfex__zeyf = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if atbdg__vkkqy or is_overload_constant_dict(func):
        if atbdg__vkkqy:
            jbt__sme = [get_literal_value(pjt__oulpm) for pjt__oulpm,
                huyx__qtb in kws.values()]
            erf__wfevm = [get_literal_value(wmefy__bmt) for huyx__qtb,
                wmefy__bmt in kws.values()]
        else:
            ejb__mzo = get_overload_constant_dict(func)
            jbt__sme = tuple(ejb__mzo.keys())
            erf__wfevm = tuple(ejb__mzo.values())
        for gmot__czlax in ('head', 'ngroup'):
            if gmot__czlax in erf__wfevm:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {gmot__czlax} cannot be mixed with other groupby operations.'
                    )
        if any(tzix__ybcqs not in grp.selection and tzix__ybcqs not in grp.
            keys for tzix__ybcqs in jbt__sme):
            raise_bodo_error(
                f'Selected column names {jbt__sme} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            erf__wfevm)
        if atbdg__vkkqy and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        lvv__pwg = {}
        out_columns = []
        out_data = []
        out_column_type = []
        ouwb__nhk = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for rqsfz__sbe, f_val in zip(jbt__sme, erf__wfevm):
            if isinstance(f_val, (tuple, list)):
                kubgs__ciz = 0
                for nauj__vqabx in f_val:
                    vqzi__fzcnd, out_tp = get_agg_funcname_and_outtyp(grp,
                        rqsfz__sbe, nauj__vqabx, typing_context, target_context
                        )
                    xfex__zeyf = vqzi__fzcnd in list_cumulative
                    if vqzi__fzcnd == '<lambda>' and len(f_val) > 1:
                        vqzi__fzcnd = '<lambda_' + str(kubgs__ciz) + '>'
                        kubgs__ciz += 1
                    out_columns.append((rqsfz__sbe, vqzi__fzcnd))
                    lvv__pwg[rqsfz__sbe, vqzi__fzcnd] = rqsfz__sbe, vqzi__fzcnd
                    _append_out_type(grp, out_data, out_tp)
            else:
                vqzi__fzcnd, out_tp = get_agg_funcname_and_outtyp(grp,
                    rqsfz__sbe, f_val, typing_context, target_context)
                xfex__zeyf = vqzi__fzcnd in list_cumulative
                if multi_level_names:
                    out_columns.append((rqsfz__sbe, vqzi__fzcnd))
                    lvv__pwg[rqsfz__sbe, vqzi__fzcnd] = rqsfz__sbe, vqzi__fzcnd
                elif not atbdg__vkkqy:
                    out_columns.append(rqsfz__sbe)
                    lvv__pwg[rqsfz__sbe, vqzi__fzcnd] = rqsfz__sbe
                elif atbdg__vkkqy:
                    ouwb__nhk.append(vqzi__fzcnd)
                _append_out_type(grp, out_data, out_tp)
        if atbdg__vkkqy:
            for yvty__raum, jexll__cadp in enumerate(kws.keys()):
                out_columns.append(jexll__cadp)
                lvv__pwg[jbt__sme[yvty__raum], ouwb__nhk[yvty__raum]
                    ] = jexll__cadp
        if xfex__zeyf:
            index = grp.df_type.index
        else:
            index = out_tp.index
        lqvws__ceukr = DataFrameType(tuple(out_data), index, tuple(
            out_columns), is_table_format=True)
        return signature(lqvws__ceukr, *args), lvv__pwg
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            ntvvx__sas = get_overload_const_list(func)
        else:
            ntvvx__sas = func.types
        if len(ntvvx__sas) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        kubgs__ciz = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        lvv__pwg = {}
        lhbod__rgadg = grp.selection[0]
        for f_val in ntvvx__sas:
            vqzi__fzcnd, out_tp = get_agg_funcname_and_outtyp(grp,
                lhbod__rgadg, f_val, typing_context, target_context)
            xfex__zeyf = vqzi__fzcnd in list_cumulative
            if vqzi__fzcnd == '<lambda>' and len(ntvvx__sas) > 1:
                vqzi__fzcnd = '<lambda_' + str(kubgs__ciz) + '>'
                kubgs__ciz += 1
            out_columns.append(vqzi__fzcnd)
            lvv__pwg[lhbod__rgadg, vqzi__fzcnd] = vqzi__fzcnd
            _append_out_type(grp, out_data, out_tp)
        if xfex__zeyf:
            index = grp.df_type.index
        else:
            index = out_tp.index
        lqvws__ceukr = DataFrameType(tuple(out_data), index, tuple(
            out_columns), is_table_format=True)
        return signature(lqvws__ceukr, *args), lvv__pwg
    vqzi__fzcnd = ''
    if types.unliteral(func) == types.unicode_type:
        vqzi__fzcnd = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        vqzi__fzcnd = bodo.utils.typing.get_builtin_function_name(func)
    if vqzi__fzcnd:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, vqzi__fzcnd, typing_context, kws)
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
        lrggv__nhfxu = args[0] if len(args) > 0 else kws.pop('axis', 0)
        vexg__mwzb = args[1] if len(args) > 1 else kws.pop('numeric_only', 
            False)
        iqaym__agz = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        var__jau = dict(axis=lrggv__nhfxu, numeric_only=vexg__mwzb)
        uhbg__twed = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', var__jau,
            uhbg__twed, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        tog__rejpx = args[0] if len(args) > 0 else kws.pop('periods', 1)
        uvls__qrcle = args[1] if len(args) > 1 else kws.pop('freq', None)
        lrggv__nhfxu = args[2] if len(args) > 2 else kws.pop('axis', 0)
        qdj__xbx = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        var__jau = dict(freq=uvls__qrcle, axis=lrggv__nhfxu, fill_value=
            qdj__xbx)
        uhbg__twed = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', var__jau,
            uhbg__twed, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        bgf__ayfo = args[0] if len(args) > 0 else kws.pop('func', None)
        app__dpo = kws.pop('engine', None)
        uafn__pdp = kws.pop('engine_kwargs', None)
        var__jau = dict(engine=app__dpo, engine_kwargs=uafn__pdp)
        uhbg__twed = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', var__jau, uhbg__twed,
            package_name='pandas', module_name='GroupBy')
    lvv__pwg = {}
    for tzix__ybcqs in grp.selection:
        out_columns.append(tzix__ybcqs)
        lvv__pwg[tzix__ybcqs, name_operation] = tzix__ybcqs
        agib__ihdcu = grp.df_type.column_index[tzix__ybcqs]
        data = grp.df_type.data[agib__ihdcu]
        kcm__twg = (name_operation if name_operation != 'transform' else
            get_literal_value(bgf__ayfo))
        if kcm__twg in ('sum', 'cumsum'):
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
            phv__tac, err_msg = get_groupby_output_dtype(data,
                get_literal_value(bgf__ayfo), grp.df_type.index)
            if err_msg == 'ok':
                data = phv__tac
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    lqvws__ceukr = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        lqvws__ceukr = SeriesType(out_data[0].dtype, data=out_data[0],
            index=index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(lqvws__ceukr, *args), lvv__pwg


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
        xoja__adcoe = _get_groupby_apply_udf_out_type(func, grp, f_args,
            kws, self.context, numba.core.registry.cpu_target.target_context)
        ubfe__mnyen = isinstance(xoja__adcoe, (SeriesType,
            HeterogeneousSeriesType)
            ) and xoja__adcoe.const_info is not None or not isinstance(
            xoja__adcoe, (SeriesType, DataFrameType))
        if ubfe__mnyen:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                lwyf__druy = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                ndr__hgu = tuple(grp.df_type.column_index[grp.keys[
                    yvty__raum]] for yvty__raum in range(len(grp.keys)))
                auy__paar = tuple(grp.df_type.data[agib__ihdcu] for
                    agib__ihdcu in ndr__hgu)
                lwyf__druy = MultiIndexType(auy__paar, tuple(types.literal(
                    uqcd__xra) for uqcd__xra in grp.keys))
            else:
                agib__ihdcu = grp.df_type.column_index[grp.keys[0]]
                hjyn__spsh = grp.df_type.data[agib__ihdcu]
                lwyf__druy = bodo.hiframes.pd_index_ext.array_type_to_index(
                    hjyn__spsh, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            lfzs__qwniq = tuple(grp.df_type.data[grp.df_type.column_index[
                tzix__ybcqs]] for tzix__ybcqs in grp.keys)
            alzg__aba = tuple(types.literal(hldv__esi) for hldv__esi in grp
                .keys) + get_index_name_types(xoja__adcoe.index)
            if not grp.as_index:
                lfzs__qwniq = types.Array(types.int64, 1, 'C'),
                alzg__aba = (types.none,) + get_index_name_types(xoja__adcoe
                    .index)
            lwyf__druy = MultiIndexType(lfzs__qwniq +
                get_index_data_arr_types(xoja__adcoe.index), alzg__aba)
        if ubfe__mnyen:
            if isinstance(xoja__adcoe, HeterogeneousSeriesType):
                huyx__qtb, pjmvv__kbs = xoja__adcoe.const_info
                if isinstance(xoja__adcoe.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    lkoxv__tlnl = xoja__adcoe.data.tuple_typ.types
                elif isinstance(xoja__adcoe.data, types.Tuple):
                    lkoxv__tlnl = xoja__adcoe.data.types
                yqtz__kep = tuple(to_nullable_type(dtype_to_array_type(
                    gzl__tkgio)) for gzl__tkgio in lkoxv__tlnl)
                lepvm__flo = DataFrameType(out_data + yqtz__kep, lwyf__druy,
                    out_columns + pjmvv__kbs)
            elif isinstance(xoja__adcoe, SeriesType):
                nzdzl__lsovo, pjmvv__kbs = xoja__adcoe.const_info
                yqtz__kep = tuple(to_nullable_type(dtype_to_array_type(
                    xoja__adcoe.dtype)) for huyx__qtb in range(nzdzl__lsovo))
                lepvm__flo = DataFrameType(out_data + yqtz__kep, lwyf__druy,
                    out_columns + pjmvv__kbs)
            else:
                vqpl__vfsx = get_udf_out_arr_type(xoja__adcoe)
                if not grp.as_index:
                    lepvm__flo = DataFrameType(out_data + (vqpl__vfsx,),
                        lwyf__druy, out_columns + ('',))
                else:
                    lepvm__flo = SeriesType(vqpl__vfsx.dtype, vqpl__vfsx,
                        lwyf__druy, None)
        elif isinstance(xoja__adcoe, SeriesType):
            lepvm__flo = SeriesType(xoja__adcoe.dtype, xoja__adcoe.data,
                lwyf__druy, xoja__adcoe.name_typ)
        else:
            lepvm__flo = DataFrameType(xoja__adcoe.data, lwyf__druy,
                xoja__adcoe.columns)
        udwyw__ybce = gen_apply_pysig(len(f_args), kws.keys())
        tlrl__snpm = (func, *f_args) + tuple(kws.values())
        return signature(lepvm__flo, *tlrl__snpm).replace(pysig=udwyw__ybce)

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
    hxvhm__jfg = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            rqsfz__sbe = grp.selection[0]
            vqpl__vfsx = hxvhm__jfg.data[hxvhm__jfg.column_index[rqsfz__sbe]]
            kvt__iljz = SeriesType(vqpl__vfsx.dtype, vqpl__vfsx, hxvhm__jfg
                .index, types.literal(rqsfz__sbe))
        else:
            gjwy__odx = tuple(hxvhm__jfg.data[hxvhm__jfg.column_index[
                tzix__ybcqs]] for tzix__ybcqs in grp.selection)
            kvt__iljz = DataFrameType(gjwy__odx, hxvhm__jfg.index, tuple(
                grp.selection))
    else:
        kvt__iljz = hxvhm__jfg
    ewgag__dmedy = kvt__iljz,
    ewgag__dmedy += tuple(f_args)
    try:
        xoja__adcoe = get_const_func_output_type(func, ewgag__dmedy, kws,
            typing_context, target_context)
    except Exception as tvk__nimh:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', tvk__nimh),
            getattr(tvk__nimh, 'loc', None))
    return xoja__adcoe


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    ewgag__dmedy = (grp,) + f_args
    try:
        xoja__adcoe = get_const_func_output_type(func, ewgag__dmedy, kws,
            self.context, numba.core.registry.cpu_target.target_context, False)
    except Exception as tvk__nimh:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', tvk__nimh),
            getattr(tvk__nimh, 'loc', None))
    udwyw__ybce = gen_apply_pysig(len(f_args), kws.keys())
    tlrl__snpm = (func, *f_args) + tuple(kws.values())
    return signature(xoja__adcoe, *tlrl__snpm).replace(pysig=udwyw__ybce)


def gen_apply_pysig(n_args, kws):
    cncrf__gus = ', '.join(f'arg{yvty__raum}' for yvty__raum in range(n_args))
    cncrf__gus = cncrf__gus + ', ' if cncrf__gus else ''
    uai__pcd = ', '.join(f"{faae__awg} = ''" for faae__awg in kws)
    nlxr__fujzn = f'def apply_stub(func, {cncrf__gus}{uai__pcd}):\n'
    nlxr__fujzn += '    pass\n'
    urg__etaj = {}
    exec(nlxr__fujzn, {}, urg__etaj)
    pocqj__glvmu = urg__etaj['apply_stub']
    return numba.core.utils.pysignature(pocqj__glvmu)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        xgqzx__qrkz = types.Array(types.int64, 1, 'C')
        xng__cbsvu = _pivot_values.meta
        qxxg__ufqhy = len(xng__cbsvu)
        sgruc__koxc = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        uksll__jzv = DataFrameType((xgqzx__qrkz,) * qxxg__ufqhy,
            sgruc__koxc, tuple(xng__cbsvu))
        return signature(uksll__jzv, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    nlxr__fujzn = 'def impl(keys, dropna, _is_parallel):\n'
    nlxr__fujzn += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    nlxr__fujzn += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{yvty__raum}])' for yvty__raum in range(len(
        keys.types))))
    nlxr__fujzn += '    table = arr_info_list_to_table(info_list)\n'
    nlxr__fujzn += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    nlxr__fujzn += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    nlxr__fujzn += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    nlxr__fujzn += '    delete_table_decref_arrays(table)\n'
    nlxr__fujzn += '    ev.finalize()\n'
    nlxr__fujzn += '    return sort_idx, group_labels, ngroups\n'
    urg__etaj = {}
    exec(nlxr__fujzn, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, urg__etaj)
    vocmz__ujqp = urg__etaj['impl']
    return vocmz__ujqp


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    tnlzd__nhue = len(labels)
    jqxq__ksalh = np.zeros(ngroups, dtype=np.int64)
    msz__vqry = np.zeros(ngroups, dtype=np.int64)
    izyeh__mfdmu = 0
    vsaf__tvh = 0
    for yvty__raum in range(tnlzd__nhue):
        mtemw__jfvhl = labels[yvty__raum]
        if mtemw__jfvhl < 0:
            izyeh__mfdmu += 1
        else:
            vsaf__tvh += 1
            if yvty__raum == tnlzd__nhue - 1 or mtemw__jfvhl != labels[
                yvty__raum + 1]:
                jqxq__ksalh[mtemw__jfvhl] = izyeh__mfdmu
                msz__vqry[mtemw__jfvhl] = izyeh__mfdmu + vsaf__tvh
                izyeh__mfdmu += vsaf__tvh
                vsaf__tvh = 0
    return jqxq__ksalh, msz__vqry


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    vocmz__ujqp, huyx__qtb = gen_shuffle_dataframe(df, keys, _is_parallel)
    return vocmz__ujqp


def gen_shuffle_dataframe(df, keys, _is_parallel):
    nzdzl__lsovo = len(df.columns)
    tfnl__fjzqi = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    nlxr__fujzn = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        nlxr__fujzn += '  return df, keys, get_null_shuffle_info()\n'
        urg__etaj = {}
        exec(nlxr__fujzn, {'get_null_shuffle_info': get_null_shuffle_info},
            urg__etaj)
        vocmz__ujqp = urg__etaj['impl']
        return vocmz__ujqp
    for yvty__raum in range(nzdzl__lsovo):
        nlxr__fujzn += f"""  in_arr{yvty__raum} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {yvty__raum})
"""
    nlxr__fujzn += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    nlxr__fujzn += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{yvty__raum}])' for yvty__raum in range(
        tfnl__fjzqi)), ', '.join(f'array_to_info(in_arr{yvty__raum})' for
        yvty__raum in range(nzdzl__lsovo)), 'array_to_info(in_index_arr)')
    nlxr__fujzn += '  table = arr_info_list_to_table(info_list)\n'
    nlxr__fujzn += (
        f'  out_table = shuffle_table(table, {tfnl__fjzqi}, _is_parallel, 1)\n'
        )
    for yvty__raum in range(tfnl__fjzqi):
        nlxr__fujzn += f"""  out_key{yvty__raum} = info_to_array(info_from_table(out_table, {yvty__raum}), keys{yvty__raum}_typ)
"""
    for yvty__raum in range(nzdzl__lsovo):
        nlxr__fujzn += f"""  out_arr{yvty__raum} = info_to_array(info_from_table(out_table, {yvty__raum + tfnl__fjzqi}), in_arr{yvty__raum}_typ)
"""
    nlxr__fujzn += f"""  out_arr_index = info_to_array(info_from_table(out_table, {tfnl__fjzqi + nzdzl__lsovo}), ind_arr_typ)
"""
    nlxr__fujzn += '  shuffle_info = get_shuffle_info(out_table)\n'
    nlxr__fujzn += '  delete_table(out_table)\n'
    nlxr__fujzn += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{yvty__raum}' for yvty__raum in range(
        nzdzl__lsovo))
    nlxr__fujzn += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    nlxr__fujzn += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    nlxr__fujzn += '  return out_df, ({},), shuffle_info\n'.format(', '.
        join(f'out_key{yvty__raum}' for yvty__raum in range(tfnl__fjzqi)))
    rnm__mawm = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    rnm__mawm.update({f'keys{yvty__raum}_typ': keys.types[yvty__raum] for
        yvty__raum in range(tfnl__fjzqi)})
    rnm__mawm.update({f'in_arr{yvty__raum}_typ': df.data[yvty__raum] for
        yvty__raum in range(nzdzl__lsovo)})
    urg__etaj = {}
    exec(nlxr__fujzn, rnm__mawm, urg__etaj)
    vocmz__ujqp = urg__etaj['impl']
    return vocmz__ujqp, rnm__mawm


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        ykgg__zbyfe = len(data.array_types)
        nlxr__fujzn = 'def impl(data, shuffle_info):\n'
        nlxr__fujzn += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{yvty__raum}])' for yvty__raum in
            range(ykgg__zbyfe)))
        nlxr__fujzn += '  table = arr_info_list_to_table(info_list)\n'
        nlxr__fujzn += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for yvty__raum in range(ykgg__zbyfe):
            nlxr__fujzn += f"""  out_arr{yvty__raum} = info_to_array(info_from_table(out_table, {yvty__raum}), data._data[{yvty__raum}])
"""
        nlxr__fujzn += '  delete_table(out_table)\n'
        nlxr__fujzn += '  delete_table(table)\n'
        nlxr__fujzn += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{yvty__raum}' for yvty__raum in range
            (ykgg__zbyfe))))
        urg__etaj = {}
        exec(nlxr__fujzn, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, urg__etaj)
        vocmz__ujqp = urg__etaj['impl']
        return vocmz__ujqp
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            azty__ghhi = bodo.utils.conversion.index_to_array(data)
            vea__duj = reverse_shuffle(azty__ghhi, shuffle_info)
            return bodo.utils.conversion.index_from_array(vea__duj)
        return impl_index

    def impl_arr(data, shuffle_info):
        kxph__kqo = [array_to_info(data)]
        pvjy__zxcr = arr_info_list_to_table(kxph__kqo)
        xomky__nxgf = reverse_shuffle_table(pvjy__zxcr, shuffle_info)
        vea__duj = info_to_array(info_from_table(xomky__nxgf, 0), data)
        delete_table(xomky__nxgf)
        delete_table(pvjy__zxcr)
        return vea__duj
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    var__jau = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    uhbg__twed = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', var__jau, uhbg__twed,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    yngxs__ehr = get_overload_const_bool(ascending)
    aflae__yupyi = grp.selection[0]
    nlxr__fujzn = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    fple__ufgdr = (
        f"lambda S: S.value_counts(ascending={yngxs__ehr}, _index_name='{aflae__yupyi}')"
        )
    nlxr__fujzn += f'    return grp.apply({fple__ufgdr})\n'
    urg__etaj = {}
    exec(nlxr__fujzn, {'bodo': bodo}, urg__etaj)
    vocmz__ujqp = urg__etaj['impl']
    return vocmz__ujqp


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
    for srqf__jlkg in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, srqf__jlkg, no_unliteral=True
            )(create_unsupported_overload(f'DataFrameGroupBy.{srqf__jlkg}'))
    for srqf__jlkg in groupby_unsupported:
        overload_method(DataFrameGroupByType, srqf__jlkg, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{srqf__jlkg}'))
    for srqf__jlkg in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, srqf__jlkg, no_unliteral=True
            )(create_unsupported_overload(f'SeriesGroupBy.{srqf__jlkg}'))
    for srqf__jlkg in series_only_unsupported:
        overload_method(DataFrameGroupByType, srqf__jlkg, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{srqf__jlkg}'))
    for srqf__jlkg in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, srqf__jlkg, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{srqf__jlkg}'))


_install_groupby_unsupported()
