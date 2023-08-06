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
            bwg__key = 'Series'
        else:
            bwg__key = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{bwg__key}.rolling()')
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
        lvefd__zgob = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, lvefd__zgob)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    usc__edaa = dict(win_type=win_type, axis=axis, closed=closed)
    energ__bwc = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', usc__edaa, energ__bwc,
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
    usc__edaa = dict(win_type=win_type, axis=axis, closed=closed)
    energ__bwc = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', usc__edaa, energ__bwc,
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
        yjf__jntn, nvpvp__clu, lsvqu__rjbv, ziz__jczqh, fgl__kzth = args
        res__jwlzt = signature.return_type
        elti__mbp = cgutils.create_struct_proxy(res__jwlzt)(context, builder)
        elti__mbp.obj = yjf__jntn
        elti__mbp.window = nvpvp__clu
        elti__mbp.min_periods = lsvqu__rjbv
        elti__mbp.center = ziz__jczqh
        context.nrt.incref(builder, signature.args[0], yjf__jntn)
        context.nrt.incref(builder, signature.args[1], nvpvp__clu)
        context.nrt.incref(builder, signature.args[2], lsvqu__rjbv)
        context.nrt.incref(builder, signature.args[3], ziz__jczqh)
        return elti__mbp._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    res__jwlzt = RollingType(obj_type, window_type, on, selection, False)
    return res__jwlzt(obj_type, window_type, min_periods_type, center_type,
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
    vfu__caohh = not isinstance(rolling.window_type, types.Integer)
    itead__jpi = 'variable' if vfu__caohh else 'fixed'
    twpp__mjmka = 'None'
    if vfu__caohh:
        twpp__mjmka = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    gng__xdp = []
    uuuk__fcp = 'on_arr, ' if vfu__caohh else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{itead__jpi}(bodo.hiframes.pd_series_ext.get_series_data(df), {uuuk__fcp}index_arr, window, minp, center, func, raw)'
            , twpp__mjmka, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    fdku__prn = rolling.obj_type.data
    out_cols = []
    for npi__oire in rolling.selection:
        acssw__lpwxs = rolling.obj_type.columns.index(npi__oire)
        if npi__oire == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            mrf__docgl = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {acssw__lpwxs})'
                )
            out_cols.append(npi__oire)
        else:
            if not isinstance(fdku__prn[acssw__lpwxs].dtype, (types.Boolean,
                types.Number)):
                continue
            mrf__docgl = (
                f'bodo.hiframes.rolling.rolling_{itead__jpi}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {acssw__lpwxs}), {uuuk__fcp}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(npi__oire)
        gng__xdp.append(mrf__docgl)
    return ', '.join(gng__xdp), twpp__mjmka, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    usc__edaa = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    energ__bwc = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', usc__edaa, energ__bwc,
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
    usc__edaa = dict(win_type=win_type, axis=axis, closed=closed, method=method
        )
    energ__bwc = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', usc__edaa, energ__bwc,
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
        hqqpl__cdvx = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        yozf__lnomn = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{ljp__jzt}'" if
                isinstance(ljp__jzt, str) else f'{ljp__jzt}' for ljp__jzt in
                rolling.selection if ljp__jzt != rolling.on))
        bbesi__rhpe = azehj__gulz = ''
        if fname == 'apply':
            bbesi__rhpe = 'func, raw, args, kwargs'
            azehj__gulz = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            bbesi__rhpe = azehj__gulz = 'other, pairwise'
        if fname == 'cov':
            bbesi__rhpe = azehj__gulz = 'other, pairwise, ddof'
        uyd__wqb = (
            f'lambda df, window, minp, center, {bbesi__rhpe}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {yozf__lnomn}){selection}.{fname}({azehj__gulz})'
            )
        hqqpl__cdvx += f"""  return rolling.obj.apply({uyd__wqb}, rolling.window, rolling.min_periods, rolling.center, {bbesi__rhpe})
"""
        wnqc__nlisa = {}
        exec(hqqpl__cdvx, {'bodo': bodo}, wnqc__nlisa)
        impl = wnqc__nlisa['impl']
        return impl
    eyif__oenr = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if eyif__oenr else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if eyif__oenr else rolling.obj_type.columns
        other_cols = None if eyif__oenr else other.columns
        gng__xdp, twpp__mjmka = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        gng__xdp, twpp__mjmka, out_cols = _gen_df_rolling_out_data(rolling)
    sdtm__jiixs = eyif__oenr or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    dhpyw__edfz = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    dhpyw__edfz += '  df = rolling.obj\n'
    dhpyw__edfz += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if eyif__oenr else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    bwg__key = 'None'
    if eyif__oenr:
        bwg__key = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif sdtm__jiixs:
        npi__oire = (set(out_cols) - set([rolling.on])).pop()
        bwg__key = f"'{npi__oire}'" if isinstance(npi__oire, str) else str(
            npi__oire)
    dhpyw__edfz += f'  name = {bwg__key}\n'
    dhpyw__edfz += '  window = rolling.window\n'
    dhpyw__edfz += '  center = rolling.center\n'
    dhpyw__edfz += '  minp = rolling.min_periods\n'
    dhpyw__edfz += f'  on_arr = {twpp__mjmka}\n'
    if fname == 'apply':
        dhpyw__edfz += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        dhpyw__edfz += f"  func = '{fname}'\n"
        dhpyw__edfz += f'  index_arr = None\n'
        dhpyw__edfz += f'  raw = False\n'
    if sdtm__jiixs:
        dhpyw__edfz += (
            f'  return bodo.hiframes.pd_series_ext.init_series({gng__xdp}, index, name)'
            )
        wnqc__nlisa = {}
        ofuft__kwl = {'bodo': bodo}
        exec(dhpyw__edfz, ofuft__kwl, wnqc__nlisa)
        impl = wnqc__nlisa['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(dhpyw__edfz, out_cols,
        gng__xdp)


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
        jei__wfapx = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(jei__wfapx)


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
    aue__uwjrk = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(aue__uwjrk) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    vfu__caohh = not isinstance(window_type, types.Integer)
    twpp__mjmka = 'None'
    if vfu__caohh:
        twpp__mjmka = 'bodo.utils.conversion.index_to_array(index)'
    uuuk__fcp = 'on_arr, ' if vfu__caohh else ''
    gng__xdp = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {uuuk__fcp}window, minp, center)'
            , twpp__mjmka)
    for npi__oire in out_cols:
        if npi__oire in df_cols and npi__oire in other_cols:
            jixc__aos = df_cols.index(npi__oire)
            ixtu__znyk = other_cols.index(npi__oire)
            mrf__docgl = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {jixc__aos}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {ixtu__znyk}), {uuuk__fcp}window, minp, center)'
                )
        else:
            mrf__docgl = 'np.full(len(df), np.nan)'
        gng__xdp.append(mrf__docgl)
    return ', '.join(gng__xdp), twpp__mjmka


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    yjxok__zsedn = {'pairwise': pairwise, 'ddof': ddof}
    cvvvm__ahcs = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        yjxok__zsedn, cvvvm__ahcs, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    yjxok__zsedn = {'ddof': ddof, 'pairwise': pairwise}
    cvvvm__ahcs = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        yjxok__zsedn, cvvvm__ahcs, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, jyw__kttyt = args
        if isinstance(rolling, RollingType):
            aue__uwjrk = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(jyw__kttyt, (tuple, list)):
                if len(set(jyw__kttyt).difference(set(aue__uwjrk))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(jyw__kttyt).difference(set(aue__uwjrk))))
                selection = list(jyw__kttyt)
            else:
                if jyw__kttyt not in aue__uwjrk:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(jyw__kttyt))
                selection = [jyw__kttyt]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            wrwm__mmkp = RollingType(rolling.obj_type, rolling.window_type,
                rolling.on, tuple(selection), True, series_select)
            return signature(wrwm__mmkp, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        aue__uwjrk = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            aue__uwjrk = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            aue__uwjrk = rolling.obj_type.columns
        if attr in aue__uwjrk:
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
    wav__quyw = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    fdku__prn = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in wav__quyw):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        qivq__hzcx = fdku__prn[wav__quyw.index(get_literal_value(on))]
        if not isinstance(qivq__hzcx, types.Array
            ) or qivq__hzcx.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(hnsl__ayaih.dtype, (types.Boolean, types.Number)) for
        hnsl__ayaih in fdku__prn):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
