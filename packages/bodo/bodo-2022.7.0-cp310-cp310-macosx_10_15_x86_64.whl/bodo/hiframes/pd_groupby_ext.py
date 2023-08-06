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
        tms__ubz = [('obj', fe_type.df_type)]
        super(GroupbyModel, self).__init__(dmm, fe_type, tms__ubz)


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
        ixk__pvc = args[0]
        otr__qqg = signature.return_type
        vfpxw__xszps = cgutils.create_struct_proxy(otr__qqg)(context, builder)
        vfpxw__xszps.obj = ixk__pvc
        context.nrt.incref(builder, signature.args[0], ixk__pvc)
        return vfpxw__xszps._getvalue()
    if is_overload_constant_list(by_type):
        keys = tuple(get_overload_const_list(by_type))
    elif is_literal_type(by_type):
        keys = get_literal_value(by_type),
    else:
        assert False, 'Reached unreachable code in init_groupby; there is an validate_groupby_spec'
    selection = list(obj_type.columns)
    for zve__flqo in keys:
        selection.remove(zve__flqo)
    if is_overload_constant_bool(as_index_type):
        as_index = is_overload_true(as_index_type)
    else:
        as_index = True
    if is_overload_constant_bool(dropna_type):
        dropna = is_overload_true(dropna_type)
    else:
        dropna = True
    otr__qqg = DataFrameGroupByType(obj_type, keys, tuple(selection),
        as_index, dropna, False)
    return otr__qqg(obj_type, by_type, as_index_type, dropna_type), codegen


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
        grpby, jjctx__xsxq = args
        if isinstance(grpby, DataFrameGroupByType):
            series_select = False
            if isinstance(jjctx__xsxq, (tuple, list)):
                if len(set(jjctx__xsxq).difference(set(grpby.df_type.columns))
                    ) > 0:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(set(jjctx__xsxq).difference(set(grpby.
                        df_type.columns))))
                selection = jjctx__xsxq
            else:
                if jjctx__xsxq not in grpby.df_type.columns:
                    raise_bodo_error(
                        'groupby: selected column {} not found in dataframe'
                        .format(jjctx__xsxq))
                selection = jjctx__xsxq,
                series_select = True
            tuu__xlbmi = DataFrameGroupByType(grpby.df_type, grpby.keys,
                selection, grpby.as_index, grpby.dropna, True, series_select)
            return signature(tuu__xlbmi, *args)


@infer_global(operator.getitem)
class GetItemDataFrameGroupBy(AbstractTemplate):

    def generic(self, args, kws):
        grpby, jjctx__xsxq = args
        if isinstance(grpby, DataFrameGroupByType) and is_literal_type(
            jjctx__xsxq):
            tuu__xlbmi = StaticGetItemDataFrameGroupBy.generic(self, (grpby,
                get_literal_value(jjctx__xsxq)), {}).return_type
            return signature(tuu__xlbmi, *args)


GetItemDataFrameGroupBy.prefer_literal = True


@lower_builtin('static_getitem', DataFrameGroupByType, types.Any)
@lower_builtin(operator.getitem, DataFrameGroupByType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


def get_groupby_output_dtype(arr_type, func_name, index_type=None):
    jjp__jmsoo = arr_type == ArrayItemArrayType(string_array_type)
    wonhp__jne = arr_type.dtype
    if isinstance(wonhp__jne, bodo.hiframes.datetime_timedelta_ext.
        DatetimeTimeDeltaType):
        raise BodoError(
            f"""column type of {wonhp__jne} is not supported in groupby built-in function {func_name}.
{dt_err}"""
            )
    if func_name == 'median' and not isinstance(wonhp__jne, (Decimal128Type,
        types.Float, types.Integer)):
        return (None,
            'For median, only column of integer, float or Decimal type are allowed'
            )
    if func_name in ('first', 'last', 'sum', 'prod', 'min', 'max', 'count',
        'nunique', 'head') and isinstance(arr_type, (TupleArrayType,
        ArrayItemArrayType)):
        return (None,
            f'column type of list/tuple of {wonhp__jne} is not supported in groupby built-in function {func_name}'
            )
    if func_name in {'median', 'mean', 'var', 'std'} and isinstance(wonhp__jne,
        (Decimal128Type, types.Integer, types.Float)):
        return dtype_to_array_type(types.float64), 'ok'
    if not isinstance(wonhp__jne, (types.Integer, types.Float, types.Boolean)):
        if jjp__jmsoo or wonhp__jne == types.unicode_type:
            if func_name not in {'count', 'nunique', 'min', 'max', 'sum',
                'first', 'last', 'head'}:
                return (None,
                    f'column type of strings or list of strings is not supported in groupby built-in function {func_name}'
                    )
        else:
            if isinstance(wonhp__jne, bodo.PDCategoricalDtype):
                if func_name in ('min', 'max') and not wonhp__jne.ordered:
                    return (None,
                        f'categorical column must be ordered in groupby built-in function {func_name}'
                        )
            if func_name not in {'count', 'nunique', 'min', 'max', 'first',
                'last', 'head'}:
                return (None,
                    f'column type of {wonhp__jne} is not supported in groupby built-in function {func_name}'
                    )
    if isinstance(wonhp__jne, types.Boolean) and func_name in {'cumsum',
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
    wonhp__jne = arr_type.dtype
    if func_name in {'count'}:
        return IntDtype(types.int64)
    if func_name in {'sum', 'prod', 'min', 'max'}:
        if func_name in {'sum', 'prod'} and not isinstance(wonhp__jne, (
            types.Integer, types.Float)):
            raise BodoError(
                'pivot_table(): sum and prod operations require integer or float input'
                )
        if isinstance(wonhp__jne, types.Integer):
            return IntDtype(wonhp__jne)
        return wonhp__jne
    if func_name in {'mean', 'var', 'std'}:
        return types.float64
    raise BodoError('invalid pivot operation')


def check_args_kwargs(func_name, len_args, args, kws):
    if len(kws) > 0:
        pfjgm__xfevs = list(kws.keys())[0]
        raise BodoError(
            f"Groupby.{func_name}() got an unexpected keyword argument '{pfjgm__xfevs}'."
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
    for zve__flqo in grp.keys:
        if multi_level_names:
            jit__pdlg = zve__flqo, ''
        else:
            jit__pdlg = zve__flqo
        ytiwd__noy = grp.df_type.column_index[zve__flqo]
        data = grp.df_type.data[ytiwd__noy]
        out_columns.append(jit__pdlg)
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
        eqxtd__urv = tuple(grp.df_type.column_index[grp.keys[hiyht__dtbsc]] for
            hiyht__dtbsc in range(len(grp.keys)))
        dlfsu__tbsf = tuple(grp.df_type.data[ytiwd__noy] for ytiwd__noy in
            eqxtd__urv)
        index = MultiIndexType(dlfsu__tbsf, tuple(types.StringLiteral(
            zve__flqo) for zve__flqo in grp.keys))
    else:
        ytiwd__noy = grp.df_type.column_index[grp.keys[0]]
        xdfn__rjroi = grp.df_type.data[ytiwd__noy]
        index = bodo.hiframes.pd_index_ext.array_type_to_index(xdfn__rjroi,
            types.StringLiteral(grp.keys[0]))
    ppun__xmk = {}
    lsyc__laqzk = []
    if func_name in ('size', 'count'):
        kws = dict(kws) if kws else {}
        check_args_kwargs(func_name, 0, args, kws)
    if func_name == 'size':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('size')
        ppun__xmk[None, 'size'] = 'size'
    elif func_name == 'ngroup':
        out_data.append(types.Array(types.int64, 1, 'C'))
        out_columns.append('ngroup')
        ppun__xmk[None, 'ngroup'] = 'ngroup'
        kws = dict(kws) if kws else {}
        ascending = args[0] if len(args) > 0 else kws.pop('ascending', True)
        obcr__tit = dict(ascending=ascending)
        vcbf__eajhb = dict(ascending=True)
        check_unsupported_args(f'Groupby.{func_name}', obcr__tit,
            vcbf__eajhb, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(func_name, 1, args, kws)
    else:
        columns = (grp.selection if func_name != 'head' or grp.
            explicit_select else grp.df_type.columns)
        for zhfj__fwjid in columns:
            ytiwd__noy = grp.df_type.column_index[zhfj__fwjid]
            data = grp.df_type.data[ytiwd__noy]
            if func_name in ('sum', 'cumsum'):
                data = to_str_arr_if_dict_array(data)
            zhy__szyv = ColumnType.NonNumericalColumn.value
            if isinstance(data, (types.Array, IntegerArrayType)
                ) and isinstance(data.dtype, (types.Integer, types.Float)):
                zhy__szyv = ColumnType.NumericalColumn.value
            if func_name == 'agg':
                try:
                    tfi__favaf = SeriesType(data.dtype, data, None, string_type
                        )
                    mvhu__gtx = get_const_func_output_type(func, (
                        tfi__favaf,), {}, typing_context, target_context)
                    if mvhu__gtx != ArrayItemArrayType(string_array_type):
                        mvhu__gtx = dtype_to_array_type(mvhu__gtx)
                    err_msg = 'ok'
                except:
                    raise_bodo_error(
                        'Groupy.agg()/Groupy.aggregate(): column {col} of type {type} is unsupported/not a valid input type for user defined function'
                        .format(col=zhfj__fwjid, type=data.dtype))
            else:
                if func_name in ('first', 'last', 'min', 'max'):
                    kws = dict(kws) if kws else {}
                    vvj__ukh = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', False)
                    gsf__hwqn = args[1] if len(args) > 1 else kws.pop(
                        'min_count', -1)
                    obcr__tit = dict(numeric_only=vvj__ukh, min_count=gsf__hwqn
                        )
                    vcbf__eajhb = dict(numeric_only=False, min_count=-1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        obcr__tit, vcbf__eajhb, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('sum', 'prod'):
                    kws = dict(kws) if kws else {}
                    vvj__ukh = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    gsf__hwqn = args[1] if len(args) > 1 else kws.pop(
                        'min_count', 0)
                    obcr__tit = dict(numeric_only=vvj__ukh, min_count=gsf__hwqn
                        )
                    vcbf__eajhb = dict(numeric_only=True, min_count=0)
                    check_unsupported_args(f'Groupby.{func_name}',
                        obcr__tit, vcbf__eajhb, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('mean', 'median'):
                    kws = dict(kws) if kws else {}
                    vvj__ukh = args[0] if len(args) > 0 else kws.pop(
                        'numeric_only', True)
                    obcr__tit = dict(numeric_only=vvj__ukh)
                    vcbf__eajhb = dict(numeric_only=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        obcr__tit, vcbf__eajhb, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('idxmin', 'idxmax'):
                    kws = dict(kws) if kws else {}
                    xotl__qzwyd = args[0] if len(args) > 0 else kws.pop('axis',
                        0)
                    ksawh__lzuis = args[1] if len(args) > 1 else kws.pop(
                        'skipna', True)
                    obcr__tit = dict(axis=xotl__qzwyd, skipna=ksawh__lzuis)
                    vcbf__eajhb = dict(axis=0, skipna=True)
                    check_unsupported_args(f'Groupby.{func_name}',
                        obcr__tit, vcbf__eajhb, package_name='pandas',
                        module_name='GroupBy')
                elif func_name in ('var', 'std'):
                    kws = dict(kws) if kws else {}
                    rucdb__zejhe = args[0] if len(args) > 0 else kws.pop('ddof'
                        , 1)
                    obcr__tit = dict(ddof=rucdb__zejhe)
                    vcbf__eajhb = dict(ddof=1)
                    check_unsupported_args(f'Groupby.{func_name}',
                        obcr__tit, vcbf__eajhb, package_name='pandas',
                        module_name='GroupBy')
                elif func_name == 'nunique':
                    kws = dict(kws) if kws else {}
                    dropna = args[0] if len(args) > 0 else kws.pop('dropna', 1)
                    check_args_kwargs(func_name, 1, args, kws)
                elif func_name == 'head':
                    if len(args) == 0:
                        kws.pop('n', None)
                mvhu__gtx, err_msg = get_groupby_output_dtype(data,
                    func_name, grp.df_type.index)
            if err_msg == 'ok':
                mvhu__gtx = to_str_arr_if_dict_array(mvhu__gtx
                    ) if func_name in ('sum', 'cumsum') else mvhu__gtx
                out_data.append(mvhu__gtx)
                out_columns.append(zhfj__fwjid)
                if func_name == 'agg':
                    ercf__sqhof = bodo.ir.aggregate._get_udf_name(bodo.ir.
                        aggregate._get_const_agg_func(func, None))
                    ppun__xmk[zhfj__fwjid, ercf__sqhof] = zhfj__fwjid
                else:
                    ppun__xmk[zhfj__fwjid, func_name] = zhfj__fwjid
                out_column_type.append(zhy__szyv)
            else:
                lsyc__laqzk.append(err_msg)
    if func_name == 'sum':
        jeg__epj = any([(ccxbl__oapjn == ColumnType.NumericalColumn.value) for
            ccxbl__oapjn in out_column_type])
        if jeg__epj:
            out_data = [ccxbl__oapjn for ccxbl__oapjn, pighi__csd in zip(
                out_data, out_column_type) if pighi__csd != ColumnType.
                NonNumericalColumn.value]
            out_columns = [ccxbl__oapjn for ccxbl__oapjn, pighi__csd in zip
                (out_columns, out_column_type) if pighi__csd != ColumnType.
                NonNumericalColumn.value]
            ppun__xmk = {}
            for zhfj__fwjid in out_columns:
                if grp.as_index is False and zhfj__fwjid in grp.keys:
                    continue
                ppun__xmk[zhfj__fwjid, func_name] = zhfj__fwjid
    lkw__ofp = len(lsyc__laqzk)
    if len(out_data) == 0:
        if lkw__ofp == 0:
            raise BodoError('No columns in output.')
        else:
            raise BodoError(
                'No columns in output. {} column{} dropped for following reasons: {}'
                .format(lkw__ofp, ' was' if lkw__ofp == 1 else 's were',
                ','.join(lsyc__laqzk)))
    hwvyp__rjcjz = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if (len(grp.selection) == 1 and grp.series_select and grp.as_index or 
        func_name == 'size' and grp.as_index or func_name == 'ngroup'):
        if isinstance(out_data[0], IntegerArrayType):
            vdiyg__phip = IntDtype(out_data[0].dtype)
        else:
            vdiyg__phip = out_data[0].dtype
        coe__uvsxk = types.none if func_name in ('size', 'ngroup'
            ) else types.StringLiteral(grp.selection[0])
        hwvyp__rjcjz = SeriesType(vdiyg__phip, data=out_data[0], index=
            index, name_typ=coe__uvsxk)
    return signature(hwvyp__rjcjz, *args), ppun__xmk


def get_agg_funcname_and_outtyp(grp, col, f_val, typing_context, target_context
    ):
    pjv__tomeo = True
    if isinstance(f_val, str):
        pjv__tomeo = False
        bzug__zii = f_val
    elif is_overload_constant_str(f_val):
        pjv__tomeo = False
        bzug__zii = get_overload_const_str(f_val)
    elif bodo.utils.typing.is_builtin_function(f_val):
        pjv__tomeo = False
        bzug__zii = bodo.utils.typing.get_builtin_function_name(f_val)
    if not pjv__tomeo:
        if bzug__zii not in bodo.ir.aggregate.supported_agg_funcs[:-1]:
            raise BodoError(f'unsupported aggregate function {bzug__zii}')
        tuu__xlbmi = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(tuu__xlbmi, (), bzug__zii, typing_context,
            target_context)[0].return_type
    else:
        if is_expr(f_val, 'make_function'):
            vvfke__fsk = types.functions.MakeFunctionLiteral(f_val)
        else:
            vvfke__fsk = f_val
        validate_udf('agg', vvfke__fsk)
        func = get_overload_const_func(vvfke__fsk, None)
        tusam__kqcaz = func.code if hasattr(func, 'code') else func.__code__
        bzug__zii = tusam__kqcaz.co_name
        tuu__xlbmi = DataFrameGroupByType(grp.df_type, grp.keys, (col,),
            grp.as_index, grp.dropna, True, True)
        out_tp = get_agg_typ(tuu__xlbmi, (), 'agg', typing_context,
            target_context, vvfke__fsk)[0].return_type
    return bzug__zii, out_tp


def resolve_agg(grp, args, kws, typing_context, target_context):
    func = get_call_expr_arg('agg', args, dict(kws), 0, 'func', default=
        types.none)
    cqaax__kjgu = kws and all(isinstance(kytxh__hlr, types.Tuple) and len(
        kytxh__hlr) == 2 for kytxh__hlr in kws.values())
    if is_overload_none(func) and not cqaax__kjgu:
        raise_bodo_error("Groupby.agg()/aggregate(): Must provide 'func'")
    if len(args) > 1 or kws and not cqaax__kjgu:
        raise_bodo_error(
            'Groupby.agg()/aggregate(): passing extra arguments to functions not supported yet.'
            )
    bwzld__xvebj = False

    def _append_out_type(grp, out_data, out_tp):
        if grp.as_index is False:
            out_data.append(out_tp.data[len(grp.keys)])
        else:
            out_data.append(out_tp.data)
    if cqaax__kjgu or is_overload_constant_dict(func):
        if cqaax__kjgu:
            yiqy__doj = [get_literal_value(wva__adttx) for wva__adttx,
                pfkte__cprm in kws.values()]
            qylo__xsv = [get_literal_value(rrtn__umhbf) for pfkte__cprm,
                rrtn__umhbf in kws.values()]
        else:
            lev__hdzc = get_overload_constant_dict(func)
            yiqy__doj = tuple(lev__hdzc.keys())
            qylo__xsv = tuple(lev__hdzc.values())
        for lfttd__kucs in ('head', 'ngroup'):
            if lfttd__kucs in qylo__xsv:
                raise BodoError(
                    f'Groupby.agg()/aggregate(): {lfttd__kucs} cannot be mixed with other groupby operations.'
                    )
        if any(zhfj__fwjid not in grp.selection and zhfj__fwjid not in grp.
            keys for zhfj__fwjid in yiqy__doj):
            raise_bodo_error(
                f'Selected column names {yiqy__doj} not all available in dataframe column names {grp.selection}'
                )
        multi_level_names = any(isinstance(f_val, (tuple, list)) for f_val in
            qylo__xsv)
        if cqaax__kjgu and multi_level_names:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): cannot pass multiple functions in a single pd.NamedAgg()'
                )
        ppun__xmk = {}
        out_columns = []
        out_data = []
        out_column_type = []
        elj__osxbl = []
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data,
                out_column_type, multi_level_names=multi_level_names)
        for feqcc__aqv, f_val in zip(yiqy__doj, qylo__xsv):
            if isinstance(f_val, (tuple, list)):
                ljph__zzy = 0
                for vvfke__fsk in f_val:
                    bzug__zii, out_tp = get_agg_funcname_and_outtyp(grp,
                        feqcc__aqv, vvfke__fsk, typing_context, target_context)
                    bwzld__xvebj = bzug__zii in list_cumulative
                    if bzug__zii == '<lambda>' and len(f_val) > 1:
                        bzug__zii = '<lambda_' + str(ljph__zzy) + '>'
                        ljph__zzy += 1
                    out_columns.append((feqcc__aqv, bzug__zii))
                    ppun__xmk[feqcc__aqv, bzug__zii] = feqcc__aqv, bzug__zii
                    _append_out_type(grp, out_data, out_tp)
            else:
                bzug__zii, out_tp = get_agg_funcname_and_outtyp(grp,
                    feqcc__aqv, f_val, typing_context, target_context)
                bwzld__xvebj = bzug__zii in list_cumulative
                if multi_level_names:
                    out_columns.append((feqcc__aqv, bzug__zii))
                    ppun__xmk[feqcc__aqv, bzug__zii] = feqcc__aqv, bzug__zii
                elif not cqaax__kjgu:
                    out_columns.append(feqcc__aqv)
                    ppun__xmk[feqcc__aqv, bzug__zii] = feqcc__aqv
                elif cqaax__kjgu:
                    elj__osxbl.append(bzug__zii)
                _append_out_type(grp, out_data, out_tp)
        if cqaax__kjgu:
            for hiyht__dtbsc, ckcdz__cwco in enumerate(kws.keys()):
                out_columns.append(ckcdz__cwco)
                ppun__xmk[yiqy__doj[hiyht__dtbsc], elj__osxbl[hiyht__dtbsc]
                    ] = ckcdz__cwco
        if bwzld__xvebj:
            index = grp.df_type.index
        else:
            index = out_tp.index
        hwvyp__rjcjz = DataFrameType(tuple(out_data), index, tuple(
            out_columns), is_table_format=True)
        return signature(hwvyp__rjcjz, *args), ppun__xmk
    if isinstance(func, types.BaseTuple) and not isinstance(func, types.
        LiteralStrKeyDict) or is_overload_constant_list(func):
        if not (len(grp.selection) == 1 and grp.explicit_select):
            raise_bodo_error(
                'Groupby.agg()/aggregate(): must select exactly one column when more than one function is supplied'
                )
        if is_overload_constant_list(func):
            ktmor__pkdpa = get_overload_const_list(func)
        else:
            ktmor__pkdpa = func.types
        if len(ktmor__pkdpa) == 0:
            raise_bodo_error(
                'Groupby.agg()/aggregate(): List of functions must contain at least 1 function'
                )
        out_data = []
        out_columns = []
        out_column_type = []
        ljph__zzy = 0
        if not grp.as_index:
            get_keys_not_as_index(grp, out_columns, out_data, out_column_type)
        ppun__xmk = {}
        ovp__rmgsu = grp.selection[0]
        for f_val in ktmor__pkdpa:
            bzug__zii, out_tp = get_agg_funcname_and_outtyp(grp, ovp__rmgsu,
                f_val, typing_context, target_context)
            bwzld__xvebj = bzug__zii in list_cumulative
            if bzug__zii == '<lambda>' and len(ktmor__pkdpa) > 1:
                bzug__zii = '<lambda_' + str(ljph__zzy) + '>'
                ljph__zzy += 1
            out_columns.append(bzug__zii)
            ppun__xmk[ovp__rmgsu, bzug__zii] = bzug__zii
            _append_out_type(grp, out_data, out_tp)
        if bwzld__xvebj:
            index = grp.df_type.index
        else:
            index = out_tp.index
        hwvyp__rjcjz = DataFrameType(tuple(out_data), index, tuple(
            out_columns), is_table_format=True)
        return signature(hwvyp__rjcjz, *args), ppun__xmk
    bzug__zii = ''
    if types.unliteral(func) == types.unicode_type:
        bzug__zii = get_overload_const_str(func)
    if bodo.utils.typing.is_builtin_function(func):
        bzug__zii = bodo.utils.typing.get_builtin_function_name(func)
    if bzug__zii:
        args = args[1:]
        kws.pop('func', None)
        return get_agg_typ(grp, args, bzug__zii, typing_context, kws)
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
        xotl__qzwyd = args[0] if len(args) > 0 else kws.pop('axis', 0)
        vvj__ukh = args[1] if len(args) > 1 else kws.pop('numeric_only', False)
        ksawh__lzuis = args[2] if len(args) > 2 else kws.pop('skipna', 1)
        obcr__tit = dict(axis=xotl__qzwyd, numeric_only=vvj__ukh)
        vcbf__eajhb = dict(axis=0, numeric_only=False)
        check_unsupported_args(f'Groupby.{name_operation}', obcr__tit,
            vcbf__eajhb, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 3, args, kws)
    elif name_operation == 'shift':
        hkzs__mpe = args[0] if len(args) > 0 else kws.pop('periods', 1)
        huiej__jeht = args[1] if len(args) > 1 else kws.pop('freq', None)
        xotl__qzwyd = args[2] if len(args) > 2 else kws.pop('axis', 0)
        jmu__fqbp = args[3] if len(args) > 3 else kws.pop('fill_value', None)
        obcr__tit = dict(freq=huiej__jeht, axis=xotl__qzwyd, fill_value=
            jmu__fqbp)
        vcbf__eajhb = dict(freq=None, axis=0, fill_value=None)
        check_unsupported_args(f'Groupby.{name_operation}', obcr__tit,
            vcbf__eajhb, package_name='pandas', module_name='GroupBy')
        check_args_kwargs(name_operation, 4, args, kws)
    elif name_operation == 'transform':
        kws = dict(kws)
        fahz__esvfc = args[0] if len(args) > 0 else kws.pop('func', None)
        swssa__akwao = kws.pop('engine', None)
        ovp__wbn = kws.pop('engine_kwargs', None)
        obcr__tit = dict(engine=swssa__akwao, engine_kwargs=ovp__wbn)
        vcbf__eajhb = dict(engine=None, engine_kwargs=None)
        check_unsupported_args(f'Groupby.transform', obcr__tit, vcbf__eajhb,
            package_name='pandas', module_name='GroupBy')
    ppun__xmk = {}
    for zhfj__fwjid in grp.selection:
        out_columns.append(zhfj__fwjid)
        ppun__xmk[zhfj__fwjid, name_operation] = zhfj__fwjid
        ytiwd__noy = grp.df_type.column_index[zhfj__fwjid]
        data = grp.df_type.data[ytiwd__noy]
        adcsm__zaz = (name_operation if name_operation != 'transform' else
            get_literal_value(fahz__esvfc))
        if adcsm__zaz in ('sum', 'cumsum'):
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
            mvhu__gtx, err_msg = get_groupby_output_dtype(data,
                get_literal_value(fahz__esvfc), grp.df_type.index)
            if err_msg == 'ok':
                data = mvhu__gtx
            else:
                raise BodoError(
                    f'column type of {data.dtype} is not supported by {args[0]} yet.\n'
                    )
        out_data.append(data)
    if len(out_data) == 0:
        raise BodoError('No columns in output.')
    hwvyp__rjcjz = DataFrameType(tuple(out_data), index, tuple(out_columns),
        is_table_format=True)
    if len(grp.selection) == 1 and grp.series_select and grp.as_index:
        hwvyp__rjcjz = SeriesType(out_data[0].dtype, data=out_data[0],
            index=index, name_typ=types.StringLiteral(grp.selection[0]))
    return signature(hwvyp__rjcjz, *args), ppun__xmk


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
        wwksj__kkjg = _get_groupby_apply_udf_out_type(func, grp, f_args,
            kws, self.context, numba.core.registry.cpu_target.target_context)
        gwvk__kbtmo = isinstance(wwksj__kkjg, (SeriesType,
            HeterogeneousSeriesType)
            ) and wwksj__kkjg.const_info is not None or not isinstance(
            wwksj__kkjg, (SeriesType, DataFrameType))
        if gwvk__kbtmo:
            out_data = []
            out_columns = []
            out_column_type = []
            if not grp.as_index:
                get_keys_not_as_index(grp, out_columns, out_data,
                    out_column_type)
                puze__okfua = NumericIndexType(types.int64, types.none)
            elif len(grp.keys) > 1:
                eqxtd__urv = tuple(grp.df_type.column_index[grp.keys[
                    hiyht__dtbsc]] for hiyht__dtbsc in range(len(grp.keys)))
                dlfsu__tbsf = tuple(grp.df_type.data[ytiwd__noy] for
                    ytiwd__noy in eqxtd__urv)
                puze__okfua = MultiIndexType(dlfsu__tbsf, tuple(types.
                    literal(zve__flqo) for zve__flqo in grp.keys))
            else:
                ytiwd__noy = grp.df_type.column_index[grp.keys[0]]
                xdfn__rjroi = grp.df_type.data[ytiwd__noy]
                puze__okfua = bodo.hiframes.pd_index_ext.array_type_to_index(
                    xdfn__rjroi, types.literal(grp.keys[0]))
            out_data = tuple(out_data)
            out_columns = tuple(out_columns)
        else:
            mmst__ykb = tuple(grp.df_type.data[grp.df_type.column_index[
                zhfj__fwjid]] for zhfj__fwjid in grp.keys)
            oxn__cxih = tuple(types.literal(kytxh__hlr) for kytxh__hlr in
                grp.keys) + get_index_name_types(wwksj__kkjg.index)
            if not grp.as_index:
                mmst__ykb = types.Array(types.int64, 1, 'C'),
                oxn__cxih = (types.none,) + get_index_name_types(wwksj__kkjg
                    .index)
            puze__okfua = MultiIndexType(mmst__ykb +
                get_index_data_arr_types(wwksj__kkjg.index), oxn__cxih)
        if gwvk__kbtmo:
            if isinstance(wwksj__kkjg, HeterogeneousSeriesType):
                pfkte__cprm, plgm__ptalw = wwksj__kkjg.const_info
                if isinstance(wwksj__kkjg.data, bodo.libs.
                    nullable_tuple_ext.NullableTupleType):
                    bkba__gwkcl = wwksj__kkjg.data.tuple_typ.types
                elif isinstance(wwksj__kkjg.data, types.Tuple):
                    bkba__gwkcl = wwksj__kkjg.data.types
                ihtv__ajvg = tuple(to_nullable_type(dtype_to_array_type(
                    vez__trmu)) for vez__trmu in bkba__gwkcl)
                usm__bck = DataFrameType(out_data + ihtv__ajvg, puze__okfua,
                    out_columns + plgm__ptalw)
            elif isinstance(wwksj__kkjg, SeriesType):
                jen__knved, plgm__ptalw = wwksj__kkjg.const_info
                ihtv__ajvg = tuple(to_nullable_type(dtype_to_array_type(
                    wwksj__kkjg.dtype)) for pfkte__cprm in range(jen__knved))
                usm__bck = DataFrameType(out_data + ihtv__ajvg, puze__okfua,
                    out_columns + plgm__ptalw)
            else:
                bckxu__uhu = get_udf_out_arr_type(wwksj__kkjg)
                if not grp.as_index:
                    usm__bck = DataFrameType(out_data + (bckxu__uhu,),
                        puze__okfua, out_columns + ('',))
                else:
                    usm__bck = SeriesType(bckxu__uhu.dtype, bckxu__uhu,
                        puze__okfua, None)
        elif isinstance(wwksj__kkjg, SeriesType):
            usm__bck = SeriesType(wwksj__kkjg.dtype, wwksj__kkjg.data,
                puze__okfua, wwksj__kkjg.name_typ)
        else:
            usm__bck = DataFrameType(wwksj__kkjg.data, puze__okfua,
                wwksj__kkjg.columns)
        yoi__xhwl = gen_apply_pysig(len(f_args), kws.keys())
        ramyy__vpisg = (func, *f_args) + tuple(kws.values())
        return signature(usm__bck, *ramyy__vpisg).replace(pysig=yoi__xhwl)

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
    vmth__lckiu = grp.df_type
    if grp.explicit_select:
        if len(grp.selection) == 1:
            feqcc__aqv = grp.selection[0]
            bckxu__uhu = vmth__lckiu.data[vmth__lckiu.column_index[feqcc__aqv]]
            jts__ukmnz = SeriesType(bckxu__uhu.dtype, bckxu__uhu,
                vmth__lckiu.index, types.literal(feqcc__aqv))
        else:
            bdwhi__mvj = tuple(vmth__lckiu.data[vmth__lckiu.column_index[
                zhfj__fwjid]] for zhfj__fwjid in grp.selection)
            jts__ukmnz = DataFrameType(bdwhi__mvj, vmth__lckiu.index, tuple
                (grp.selection))
    else:
        jts__ukmnz = vmth__lckiu
    nsifd__not = jts__ukmnz,
    nsifd__not += tuple(f_args)
    try:
        wwksj__kkjg = get_const_func_output_type(func, nsifd__not, kws,
            typing_context, target_context)
    except Exception as voa__cndk:
        raise_bodo_error(get_udf_error_msg('GroupBy.apply()', voa__cndk),
            getattr(voa__cndk, 'loc', None))
    return wwksj__kkjg


def resolve_obj_pipe(self, grp, args, kws, obj_name):
    kws = dict(kws)
    func = args[0] if len(args) > 0 else kws.pop('func', None)
    f_args = tuple(args[1:]) if len(args) > 0 else ()
    nsifd__not = (grp,) + f_args
    try:
        wwksj__kkjg = get_const_func_output_type(func, nsifd__not, kws,
            self.context, numba.core.registry.cpu_target.target_context, False)
    except Exception as voa__cndk:
        raise_bodo_error(get_udf_error_msg(f'{obj_name}.pipe()', voa__cndk),
            getattr(voa__cndk, 'loc', None))
    yoi__xhwl = gen_apply_pysig(len(f_args), kws.keys())
    ramyy__vpisg = (func, *f_args) + tuple(kws.values())
    return signature(wwksj__kkjg, *ramyy__vpisg).replace(pysig=yoi__xhwl)


def gen_apply_pysig(n_args, kws):
    sxmxr__tui = ', '.join(f'arg{hiyht__dtbsc}' for hiyht__dtbsc in range(
        n_args))
    sxmxr__tui = sxmxr__tui + ', ' if sxmxr__tui else ''
    ixdii__zvn = ', '.join(f"{xwzia__jti} = ''" for xwzia__jti in kws)
    rint__yuwu = f'def apply_stub(func, {sxmxr__tui}{ixdii__zvn}):\n'
    rint__yuwu += '    pass\n'
    ckgwo__mqz = {}
    exec(rint__yuwu, {}, ckgwo__mqz)
    smk__yhpsd = ckgwo__mqz['apply_stub']
    return numba.core.utils.pysignature(smk__yhpsd)


def crosstab_dummy(index, columns, _pivot_values):
    return 0


@infer_global(crosstab_dummy)
class CrossTabTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        index, columns, _pivot_values = args
        ocfe__awlk = types.Array(types.int64, 1, 'C')
        gss__ouqzc = _pivot_values.meta
        enurw__mpfx = len(gss__ouqzc)
        ick__gyou = bodo.hiframes.pd_index_ext.array_type_to_index(index.
            data, types.StringLiteral('index'))
        cdz__ixf = DataFrameType((ocfe__awlk,) * enurw__mpfx, ick__gyou,
            tuple(gss__ouqzc))
        return signature(cdz__ixf, *args)


CrossTabTyper._no_unliteral = True


@lower_builtin(crosstab_dummy, types.VarArg(types.Any))
def lower_crosstab_dummy(context, builder, sig, args):
    return context.get_constant_null(sig.return_type)


def get_group_indices(keys, dropna, _is_parallel):
    return np.arange(len(keys))


@overload(get_group_indices)
def get_group_indices_overload(keys, dropna, _is_parallel):
    rint__yuwu = 'def impl(keys, dropna, _is_parallel):\n'
    rint__yuwu += (
        "    ev = bodo.utils.tracing.Event('get_group_indices', _is_parallel)\n"
        )
    rint__yuwu += '    info_list = [{}]\n'.format(', '.join(
        f'array_to_info(keys[{hiyht__dtbsc}])' for hiyht__dtbsc in range(
        len(keys.types))))
    rint__yuwu += '    table = arr_info_list_to_table(info_list)\n'
    rint__yuwu += '    group_labels = np.empty(len(keys[0]), np.int64)\n'
    rint__yuwu += '    sort_idx = np.empty(len(keys[0]), np.int64)\n'
    rint__yuwu += """    ngroups = get_groupby_labels(table, group_labels.ctypes, sort_idx.ctypes, dropna, _is_parallel)
"""
    rint__yuwu += '    delete_table_decref_arrays(table)\n'
    rint__yuwu += '    ev.finalize()\n'
    rint__yuwu += '    return sort_idx, group_labels, ngroups\n'
    ckgwo__mqz = {}
    exec(rint__yuwu, {'bodo': bodo, 'np': np, 'get_groupby_labels':
        get_groupby_labels, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, ckgwo__mqz)
    gkpi__rrp = ckgwo__mqz['impl']
    return gkpi__rrp


@numba.njit(no_cpython_wrapper=True)
def generate_slices(labels, ngroups):
    shvq__uqdim = len(labels)
    oddow__ssu = np.zeros(ngroups, dtype=np.int64)
    ogu__spvkx = np.zeros(ngroups, dtype=np.int64)
    dvbv__dpl = 0
    jcvh__xsxq = 0
    for hiyht__dtbsc in range(shvq__uqdim):
        jqvb__gsxuf = labels[hiyht__dtbsc]
        if jqvb__gsxuf < 0:
            dvbv__dpl += 1
        else:
            jcvh__xsxq += 1
            if hiyht__dtbsc == shvq__uqdim - 1 or jqvb__gsxuf != labels[
                hiyht__dtbsc + 1]:
                oddow__ssu[jqvb__gsxuf] = dvbv__dpl
                ogu__spvkx[jqvb__gsxuf] = dvbv__dpl + jcvh__xsxq
                dvbv__dpl += jcvh__xsxq
                jcvh__xsxq = 0
    return oddow__ssu, ogu__spvkx


def shuffle_dataframe(df, keys, _is_parallel):
    return df, keys, _is_parallel


@overload(shuffle_dataframe, prefer_literal=True)
def overload_shuffle_dataframe(df, keys, _is_parallel):
    gkpi__rrp, pfkte__cprm = gen_shuffle_dataframe(df, keys, _is_parallel)
    return gkpi__rrp


def gen_shuffle_dataframe(df, keys, _is_parallel):
    jen__knved = len(df.columns)
    pztcj__mia = len(keys.types)
    assert is_overload_constant_bool(_is_parallel
        ), 'shuffle_dataframe: _is_parallel is not a constant'
    rint__yuwu = 'def impl(df, keys, _is_parallel):\n'
    if is_overload_false(_is_parallel):
        rint__yuwu += '  return df, keys, get_null_shuffle_info()\n'
        ckgwo__mqz = {}
        exec(rint__yuwu, {'get_null_shuffle_info': get_null_shuffle_info},
            ckgwo__mqz)
        gkpi__rrp = ckgwo__mqz['impl']
        return gkpi__rrp
    for hiyht__dtbsc in range(jen__knved):
        rint__yuwu += f"""  in_arr{hiyht__dtbsc} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {hiyht__dtbsc})
"""
    rint__yuwu += f"""  in_index_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))
"""
    rint__yuwu += '  info_list = [{}, {}, {}]\n'.format(', '.join(
        f'array_to_info(keys[{hiyht__dtbsc}])' for hiyht__dtbsc in range(
        pztcj__mia)), ', '.join(f'array_to_info(in_arr{hiyht__dtbsc})' for
        hiyht__dtbsc in range(jen__knved)), 'array_to_info(in_index_arr)')
    rint__yuwu += '  table = arr_info_list_to_table(info_list)\n'
    rint__yuwu += (
        f'  out_table = shuffle_table(table, {pztcj__mia}, _is_parallel, 1)\n')
    for hiyht__dtbsc in range(pztcj__mia):
        rint__yuwu += f"""  out_key{hiyht__dtbsc} = info_to_array(info_from_table(out_table, {hiyht__dtbsc}), keys{hiyht__dtbsc}_typ)
"""
    for hiyht__dtbsc in range(jen__knved):
        rint__yuwu += f"""  out_arr{hiyht__dtbsc} = info_to_array(info_from_table(out_table, {hiyht__dtbsc + pztcj__mia}), in_arr{hiyht__dtbsc}_typ)
"""
    rint__yuwu += f"""  out_arr_index = info_to_array(info_from_table(out_table, {pztcj__mia + jen__knved}), ind_arr_typ)
"""
    rint__yuwu += '  shuffle_info = get_shuffle_info(out_table)\n'
    rint__yuwu += '  delete_table(out_table)\n'
    rint__yuwu += '  delete_table(table)\n'
    out_data = ', '.join(f'out_arr{hiyht__dtbsc}' for hiyht__dtbsc in range
        (jen__knved))
    rint__yuwu += (
        '  out_index = bodo.utils.conversion.index_from_array(out_arr_index)\n'
        )
    rint__yuwu += f"""  out_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(({out_data},), out_index, __col_name_meta_value_df_shuffle)
"""
    rint__yuwu += '  return out_df, ({},), shuffle_info\n'.format(', '.join
        (f'out_key{hiyht__dtbsc}' for hiyht__dtbsc in range(pztcj__mia)))
    dmdd__hjhx = {'bodo': bodo, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'shuffle_table':
        shuffle_table, 'info_from_table': info_from_table, 'info_to_array':
        info_to_array, 'delete_table': delete_table, 'get_shuffle_info':
        get_shuffle_info, '__col_name_meta_value_df_shuffle':
        ColNamesMetaType(df.columns), 'ind_arr_typ': types.Array(types.
        int64, 1, 'C') if isinstance(df.index, RangeIndexType) else df.
        index.data}
    dmdd__hjhx.update({f'keys{hiyht__dtbsc}_typ': keys.types[hiyht__dtbsc] for
        hiyht__dtbsc in range(pztcj__mia)})
    dmdd__hjhx.update({f'in_arr{hiyht__dtbsc}_typ': df.data[hiyht__dtbsc] for
        hiyht__dtbsc in range(jen__knved)})
    ckgwo__mqz = {}
    exec(rint__yuwu, dmdd__hjhx, ckgwo__mqz)
    gkpi__rrp = ckgwo__mqz['impl']
    return gkpi__rrp, dmdd__hjhx


def reverse_shuffle(data, shuffle_info):
    return data


@overload(reverse_shuffle)
def overload_reverse_shuffle(data, shuffle_info):
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        jdx__uiii = len(data.array_types)
        rint__yuwu = 'def impl(data, shuffle_info):\n'
        rint__yuwu += '  info_list = [{}]\n'.format(', '.join(
            f'array_to_info(data._data[{hiyht__dtbsc}])' for hiyht__dtbsc in
            range(jdx__uiii)))
        rint__yuwu += '  table = arr_info_list_to_table(info_list)\n'
        rint__yuwu += (
            '  out_table = reverse_shuffle_table(table, shuffle_info)\n')
        for hiyht__dtbsc in range(jdx__uiii):
            rint__yuwu += f"""  out_arr{hiyht__dtbsc} = info_to_array(info_from_table(out_table, {hiyht__dtbsc}), data._data[{hiyht__dtbsc}])
"""
        rint__yuwu += '  delete_table(out_table)\n'
        rint__yuwu += '  delete_table(table)\n'
        rint__yuwu += (
            '  return init_multi_index(({},), data._names, data._name)\n'.
            format(', '.join(f'out_arr{hiyht__dtbsc}' for hiyht__dtbsc in
            range(jdx__uiii))))
        ckgwo__mqz = {}
        exec(rint__yuwu, {'bodo': bodo, 'array_to_info': array_to_info,
            'arr_info_list_to_table': arr_info_list_to_table,
            'reverse_shuffle_table': reverse_shuffle_table,
            'info_from_table': info_from_table, 'info_to_array':
            info_to_array, 'delete_table': delete_table, 'init_multi_index':
            bodo.hiframes.pd_multi_index_ext.init_multi_index}, ckgwo__mqz)
        gkpi__rrp = ckgwo__mqz['impl']
        return gkpi__rrp
    if bodo.hiframes.pd_index_ext.is_index_type(data):

        def impl_index(data, shuffle_info):
            rrbo__sxvy = bodo.utils.conversion.index_to_array(data)
            afy__daco = reverse_shuffle(rrbo__sxvy, shuffle_info)
            return bodo.utils.conversion.index_from_array(afy__daco)
        return impl_index

    def impl_arr(data, shuffle_info):
        famwc__rduqq = [array_to_info(data)]
        xzz__aavet = arr_info_list_to_table(famwc__rduqq)
        jhvk__rpzm = reverse_shuffle_table(xzz__aavet, shuffle_info)
        afy__daco = info_to_array(info_from_table(jhvk__rpzm, 0), data)
        delete_table(jhvk__rpzm)
        delete_table(xzz__aavet)
        return afy__daco
    return impl_arr


@overload_method(DataFrameGroupByType, 'value_counts', inline='always',
    no_unliteral=True)
def groupby_value_counts(grp, normalize=False, sort=True, ascending=False,
    bins=None, dropna=True):
    obcr__tit = dict(normalize=normalize, sort=sort, bins=bins, dropna=dropna)
    vcbf__eajhb = dict(normalize=False, sort=True, bins=None, dropna=True)
    check_unsupported_args('Groupby.value_counts', obcr__tit, vcbf__eajhb,
        package_name='pandas', module_name='GroupBy')
    if len(grp.selection) > 1 or not grp.as_index:
        raise BodoError(
            "'DataFrameGroupBy' object has no attribute 'value_counts'")
    if not is_overload_constant_bool(ascending):
        raise BodoError(
            'Groupby.value_counts() ascending must be a constant boolean')
    nuxy__wwhrf = get_overload_const_bool(ascending)
    yenx__ccaek = grp.selection[0]
    rint__yuwu = f"""def impl(grp, normalize=False, sort=True, ascending=False, bins=None, dropna=True):
"""
    adwa__kjcoq = (
        f"lambda S: S.value_counts(ascending={nuxy__wwhrf}, _index_name='{yenx__ccaek}')"
        )
    rint__yuwu += f'    return grp.apply({adwa__kjcoq})\n'
    ckgwo__mqz = {}
    exec(rint__yuwu, {'bodo': bodo}, ckgwo__mqz)
    gkpi__rrp = ckgwo__mqz['impl']
    return gkpi__rrp


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
    for mpv__lkuk in groupby_unsupported_attr:
        overload_attribute(DataFrameGroupByType, mpv__lkuk, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{mpv__lkuk}'))
    for mpv__lkuk in groupby_unsupported:
        overload_method(DataFrameGroupByType, mpv__lkuk, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{mpv__lkuk}'))
    for mpv__lkuk in series_only_unsupported_attrs:
        overload_attribute(DataFrameGroupByType, mpv__lkuk, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{mpv__lkuk}'))
    for mpv__lkuk in series_only_unsupported:
        overload_method(DataFrameGroupByType, mpv__lkuk, no_unliteral=True)(
            create_unsupported_overload(f'SeriesGroupBy.{mpv__lkuk}'))
    for mpv__lkuk in dataframe_only_unsupported:
        overload_method(DataFrameGroupByType, mpv__lkuk, no_unliteral=True)(
            create_unsupported_overload(f'DataFrameGroupBy.{mpv__lkuk}'))


_install_groupby_unsupported()
