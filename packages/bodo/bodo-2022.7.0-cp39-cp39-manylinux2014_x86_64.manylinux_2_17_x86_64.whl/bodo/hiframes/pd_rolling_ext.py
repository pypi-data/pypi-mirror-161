"""typing for rolling window functions
"""
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, signature
from numba.extending import infer, infer_getattr, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model
import bodo
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_type, pd_timedelta_type
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported
from bodo.hiframes.pd_groupby_ext import DataFrameGroupByType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.rolling import supported_rolling_funcs, unsupported_rolling_methods
from bodo.utils.typing import BodoError, check_unsupported_args, create_unsupported_overload, get_literal_value, is_const_func_type, is_literal_type, is_overload_bool, is_overload_constant_str, is_overload_int, is_overload_none, raise_bodo_error


class RollingType(types.Type):

    def __init__(self, obj_type, window_type, on, selection,
        explicit_select=False, series_select=False):
        if isinstance(obj_type, bodo.SeriesType):
            evci__ovt = 'Series'
        else:
            evci__ovt = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{evci__ovt}.rolling()')
        self.obj_type = obj_type
        self.window_type = window_type
        self.on = on
        self.selection = selection
        self.explicit_select = explicit_select
        self.series_select = series_select
        super(RollingType, self).__init__(name=
            f'RollingType({obj_type}, {window_type}, {on}, {selection}, {explicit_select}, {series_select})'
            )

    def copy(self):
        return RollingType(self.obj_type, self.window_type, self.on, self.
            selection, self.explicit_select, self.series_select)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(RollingType)
class RollingModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kxu__jwh = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, kxu__jwh)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    funr__tzl = dict(win_type=win_type, axis=axis, closed=closed)
    zgbbt__xzdna = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', funr__tzl, zgbbt__xzdna,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(df, window, min_periods, center, on)

    def impl(df, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(df, window,
            min_periods, center, on)
    return impl


@overload_method(SeriesType, 'rolling', inline='always', no_unliteral=True)
def overload_series_rolling(S, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    funr__tzl = dict(win_type=win_type, axis=axis, closed=closed)
    zgbbt__xzdna = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', funr__tzl, zgbbt__xzdna,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(S, window, min_periods, center, on)

    def impl(S, window, min_periods=None, center=False, win_type=None, on=
        None, axis=0, closed=None):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(S, window,
            min_periods, center, on)
    return impl


@intrinsic
def init_rolling(typingctx, obj_type, window_type, min_periods_type,
    center_type, on_type=None):

    def codegen(context, builder, signature, args):
        baow__lkmu, wbae__ppr, rxqk__vjum, jxdqt__rbms, wnptk__rmp = args
        mzy__zqoxa = signature.return_type
        brwue__gua = cgutils.create_struct_proxy(mzy__zqoxa)(context, builder)
        brwue__gua.obj = baow__lkmu
        brwue__gua.window = wbae__ppr
        brwue__gua.min_periods = rxqk__vjum
        brwue__gua.center = jxdqt__rbms
        context.nrt.incref(builder, signature.args[0], baow__lkmu)
        context.nrt.incref(builder, signature.args[1], wbae__ppr)
        context.nrt.incref(builder, signature.args[2], rxqk__vjum)
        context.nrt.incref(builder, signature.args[3], jxdqt__rbms)
        return brwue__gua._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    mzy__zqoxa = RollingType(obj_type, window_type, on, selection, False)
    return mzy__zqoxa(obj_type, window_type, min_periods_type, center_type,
        on_type), codegen


def _handle_default_min_periods(min_periods, window):
    return min_periods


@overload(_handle_default_min_periods)
def overload_handle_default_min_periods(min_periods, window):
    if is_overload_none(min_periods):
        if isinstance(window, types.Integer):
            return lambda min_periods, window: window
        else:
            return lambda min_periods, window: 1
    else:
        return lambda min_periods, window: min_periods


def _gen_df_rolling_out_data(rolling):
    ypgfo__fza = not isinstance(rolling.window_type, types.Integer)
    tedhm__hunah = 'variable' if ypgfo__fza else 'fixed'
    mcy__kjboy = 'None'
    if ypgfo__fza:
        mcy__kjboy = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    nibt__pinf = []
    vrxx__qqlh = 'on_arr, ' if ypgfo__fza else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{tedhm__hunah}(bodo.hiframes.pd_series_ext.get_series_data(df), {vrxx__qqlh}index_arr, window, minp, center, func, raw)'
            , mcy__kjboy, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    ofvb__mrtx = rolling.obj_type.data
    out_cols = []
    for dovg__opb in rolling.selection:
        mto__tjy = rolling.obj_type.columns.index(dovg__opb)
        if dovg__opb == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            pwgi__nqhrc = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {mto__tjy})'
                )
            out_cols.append(dovg__opb)
        else:
            if not isinstance(ofvb__mrtx[mto__tjy].dtype, (types.Boolean,
                types.Number)):
                continue
            pwgi__nqhrc = (
                f'bodo.hiframes.rolling.rolling_{tedhm__hunah}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {mto__tjy}), {vrxx__qqlh}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(dovg__opb)
        nibt__pinf.append(pwgi__nqhrc)
    return ', '.join(nibt__pinf), mcy__kjboy, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    funr__tzl = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    zgbbt__xzdna = dict(engine=None, engine_kwargs=None, args=None, kwargs=None
        )
    check_unsupported_args('Rolling.apply', funr__tzl, zgbbt__xzdna,
        package_name='pandas', module_name='Window')
    if not is_const_func_type(func):
        raise BodoError(
            f"Rolling.apply(): 'func' parameter must be a function, not {func} (builtin functions not supported yet)."
            )
    if not is_overload_bool(raw):
        raise BodoError(
            f"Rolling.apply(): 'raw' parameter must be bool, not {raw}.")
    return _gen_rolling_impl(rolling, 'apply')


@overload_method(DataFrameGroupByType, 'rolling', inline='always',
    no_unliteral=True)
def groupby_rolling_overload(grp, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None, method='single'):
    funr__tzl = dict(win_type=win_type, axis=axis, closed=closed, method=method
        )
    zgbbt__xzdna = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', funr__tzl, zgbbt__xzdna,
        package_name='pandas', module_name='Window')
    _validate_rolling_args(grp, window, min_periods, center, on)

    def _impl(grp, window, min_periods=None, center=False, win_type=None,
        on=None, axis=0, closed=None, method='single'):
        min_periods = _handle_default_min_periods(min_periods, window)
        return bodo.hiframes.pd_rolling_ext.init_rolling(grp, window,
            min_periods, center, on)
    return _impl


def _gen_rolling_impl(rolling, fname, other=None):
    if isinstance(rolling.obj_type, DataFrameGroupByType):
        lnftw__axovl = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        aqt__opa = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{igujf__fpbl}'" if
                isinstance(igujf__fpbl, str) else f'{igujf__fpbl}' for
                igujf__fpbl in rolling.selection if igujf__fpbl != rolling.on))
        usnm__qltk = bcu__adu = ''
        if fname == 'apply':
            usnm__qltk = 'func, raw, args, kwargs'
            bcu__adu = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            usnm__qltk = bcu__adu = 'other, pairwise'
        if fname == 'cov':
            usnm__qltk = bcu__adu = 'other, pairwise, ddof'
        uypy__updmp = (
            f'lambda df, window, minp, center, {usnm__qltk}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {aqt__opa}){selection}.{fname}({bcu__adu})'
            )
        lnftw__axovl += f"""  return rolling.obj.apply({uypy__updmp}, rolling.window, rolling.min_periods, rolling.center, {usnm__qltk})
"""
        stbac__tzcm = {}
        exec(lnftw__axovl, {'bodo': bodo}, stbac__tzcm)
        impl = stbac__tzcm['impl']
        return impl
    pxtor__gfohl = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if pxtor__gfohl else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if pxtor__gfohl else rolling.obj_type.columns
        other_cols = None if pxtor__gfohl else other.columns
        nibt__pinf, mcy__kjboy = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        nibt__pinf, mcy__kjboy, out_cols = _gen_df_rolling_out_data(rolling)
    baj__yog = pxtor__gfohl or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    rnw__zylb = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    rnw__zylb += '  df = rolling.obj\n'
    rnw__zylb += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if pxtor__gfohl else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    evci__ovt = 'None'
    if pxtor__gfohl:
        evci__ovt = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif baj__yog:
        dovg__opb = (set(out_cols) - set([rolling.on])).pop()
        evci__ovt = f"'{dovg__opb}'" if isinstance(dovg__opb, str) else str(
            dovg__opb)
    rnw__zylb += f'  name = {evci__ovt}\n'
    rnw__zylb += '  window = rolling.window\n'
    rnw__zylb += '  center = rolling.center\n'
    rnw__zylb += '  minp = rolling.min_periods\n'
    rnw__zylb += f'  on_arr = {mcy__kjboy}\n'
    if fname == 'apply':
        rnw__zylb += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        rnw__zylb += f"  func = '{fname}'\n"
        rnw__zylb += f'  index_arr = None\n'
        rnw__zylb += f'  raw = False\n'
    if baj__yog:
        rnw__zylb += (
            f'  return bodo.hiframes.pd_series_ext.init_series({nibt__pinf}, index, name)'
            )
        stbac__tzcm = {}
        oeaes__hde = {'bodo': bodo}
        exec(rnw__zylb, oeaes__hde, stbac__tzcm)
        impl = stbac__tzcm['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(rnw__zylb, out_cols,
        nibt__pinf)


def _get_rolling_func_args(fname):
    if fname == 'apply':
        return (
            'func, raw=False, engine=None, engine_kwargs=None, args=None, kwargs=None\n'
            )
    elif fname == 'corr':
        return 'other=None, pairwise=None, ddof=1\n'
    elif fname == 'cov':
        return 'other=None, pairwise=None, ddof=1\n'
    return ''


def create_rolling_overload(fname):

    def overload_rolling_func(rolling):
        return _gen_rolling_impl(rolling, fname)
    return overload_rolling_func


def _install_rolling_methods():
    for fname in supported_rolling_funcs:
        if fname in ('apply', 'corr', 'cov'):
            continue
        nswqc__pnmp = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(nswqc__pnmp)


def _install_rolling_unsupported_methods():
    for fname in unsupported_rolling_methods:
        overload_method(RollingType, fname, no_unliteral=True)(
            create_unsupported_overload(
            f'pandas.core.window.rolling.Rolling.{fname}()'))


_install_rolling_methods()
_install_rolling_unsupported_methods()


def _get_corr_cov_out_cols(rolling, other, func_name):
    if not isinstance(other, DataFrameType):
        raise_bodo_error(
            f"DataFrame.rolling.{func_name}(): requires providing a DataFrame for 'other'"
            )
    djq__cta = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(djq__cta) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    ypgfo__fza = not isinstance(window_type, types.Integer)
    mcy__kjboy = 'None'
    if ypgfo__fza:
        mcy__kjboy = 'bodo.utils.conversion.index_to_array(index)'
    vrxx__qqlh = 'on_arr, ' if ypgfo__fza else ''
    nibt__pinf = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {vrxx__qqlh}window, minp, center)'
            , mcy__kjboy)
    for dovg__opb in out_cols:
        if dovg__opb in df_cols and dovg__opb in other_cols:
            ufe__qblqs = df_cols.index(dovg__opb)
            ezrg__uudeg = other_cols.index(dovg__opb)
            pwgi__nqhrc = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ufe__qblqs}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {ezrg__uudeg}), {vrxx__qqlh}window, minp, center)'
                )
        else:
            pwgi__nqhrc = 'np.full(len(df), np.nan)'
        nibt__pinf.append(pwgi__nqhrc)
    return ', '.join(nibt__pinf), mcy__kjboy


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    qtjip__dfh = {'pairwise': pairwise, 'ddof': ddof}
    wyq__zkd = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        qtjip__dfh, wyq__zkd, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    qtjip__dfh = {'ddof': ddof, 'pairwise': pairwise}
    wyq__zkd = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        qtjip__dfh, wyq__zkd, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, czyj__fnjx = args
        if isinstance(rolling, RollingType):
            djq__cta = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(czyj__fnjx, (tuple, list)):
                if len(set(czyj__fnjx).difference(set(djq__cta))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(czyj__fnjx).difference(set(djq__cta))))
                selection = list(czyj__fnjx)
            else:
                if czyj__fnjx not in djq__cta:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(czyj__fnjx))
                selection = [czyj__fnjx]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            nexro__ejc = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(nexro__ejc, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        djq__cta = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            djq__cta = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            djq__cta = rolling.obj_type.columns
        if attr in djq__cta:
            return RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, (attr,) if rolling.on is None else (attr,
                rolling.on), True, True)


def _validate_rolling_args(obj, window, min_periods, center, on):
    assert isinstance(obj, (SeriesType, DataFrameType, DataFrameGroupByType)
        ), 'invalid rolling obj'
    func_name = 'Series' if isinstance(obj, SeriesType
        ) else 'DataFrame' if isinstance(obj, DataFrameType
        ) else 'DataFrameGroupBy'
    if not (is_overload_int(window) or is_overload_constant_str(window) or 
        window == bodo.string_type or window in (pd_timedelta_type,
        datetime_timedelta_type)):
        raise BodoError(
            f"{func_name}.rolling(): 'window' should be int or time offset (str, pd.Timedelta, datetime.timedelta), not {window}"
            )
    if not is_overload_bool(center):
        raise BodoError(
            f'{func_name}.rolling(): center must be a boolean, not {center}')
    if not (is_overload_none(min_periods) or isinstance(min_periods, types.
        Integer)):
        raise BodoError(
            f'{func_name}.rolling(): min_periods must be an integer, not {min_periods}'
            )
    if isinstance(obj, SeriesType) and not is_overload_none(on):
        raise BodoError(
            f"{func_name}.rolling(): 'on' not supported for Series yet (can use a DataFrame instead)."
            )
    myjdh__ouis = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    ofvb__mrtx = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in myjdh__ouis):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        ibq__zuhw = ofvb__mrtx[myjdh__ouis.index(get_literal_value(on))]
        if not isinstance(ibq__zuhw, types.Array
            ) or ibq__zuhw.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(vwt__myedj.dtype, (types.Boolean, types.Number)) for
        vwt__myedj in ofvb__mrtx):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
