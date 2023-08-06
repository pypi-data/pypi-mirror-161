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
            qqeu__nsfo = 'Series'
        else:
            qqeu__nsfo = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{qqeu__nsfo}.rolling()')
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
        ast__fmyd = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, ast__fmyd)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    jdjb__nvr = dict(win_type=win_type, axis=axis, closed=closed)
    ejx__cmi = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', jdjb__nvr, ejx__cmi,
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
    jdjb__nvr = dict(win_type=win_type, axis=axis, closed=closed)
    ejx__cmi = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', jdjb__nvr, ejx__cmi,
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
        ezy__igmlz, ftjc__mceu, ezmwz__hcw, wfdwe__uwpgw, zxfw__eqi = args
        xdto__atao = signature.return_type
        ocdvp__kox = cgutils.create_struct_proxy(xdto__atao)(context, builder)
        ocdvp__kox.obj = ezy__igmlz
        ocdvp__kox.window = ftjc__mceu
        ocdvp__kox.min_periods = ezmwz__hcw
        ocdvp__kox.center = wfdwe__uwpgw
        context.nrt.incref(builder, signature.args[0], ezy__igmlz)
        context.nrt.incref(builder, signature.args[1], ftjc__mceu)
        context.nrt.incref(builder, signature.args[2], ezmwz__hcw)
        context.nrt.incref(builder, signature.args[3], wfdwe__uwpgw)
        return ocdvp__kox._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    xdto__atao = RollingType(obj_type, window_type, on, selection, False)
    return xdto__atao(obj_type, window_type, min_periods_type, center_type,
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
    wtj__uetw = not isinstance(rolling.window_type, types.Integer)
    ncno__whf = 'variable' if wtj__uetw else 'fixed'
    ersmu__ddis = 'None'
    if wtj__uetw:
        ersmu__ddis = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    ibaj__jze = []
    vmyf__qctyc = 'on_arr, ' if wtj__uetw else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{ncno__whf}(bodo.hiframes.pd_series_ext.get_series_data(df), {vmyf__qctyc}index_arr, window, minp, center, func, raw)'
            , ersmu__ddis, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    ydv__ktc = rolling.obj_type.data
    out_cols = []
    for mltr__shk in rolling.selection:
        ijk__klmy = rolling.obj_type.columns.index(mltr__shk)
        if mltr__shk == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            gbyyi__tnb = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ijk__klmy})'
                )
            out_cols.append(mltr__shk)
        else:
            if not isinstance(ydv__ktc[ijk__klmy].dtype, (types.Boolean,
                types.Number)):
                continue
            gbyyi__tnb = (
                f'bodo.hiframes.rolling.rolling_{ncno__whf}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {ijk__klmy}), {vmyf__qctyc}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(mltr__shk)
        ibaj__jze.append(gbyyi__tnb)
    return ', '.join(ibaj__jze), ersmu__ddis, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    jdjb__nvr = dict(engine=engine, engine_kwargs=engine_kwargs, args=args,
        kwargs=kwargs)
    ejx__cmi = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', jdjb__nvr, ejx__cmi,
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
    jdjb__nvr = dict(win_type=win_type, axis=axis, closed=closed, method=method
        )
    ejx__cmi = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', jdjb__nvr, ejx__cmi,
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
        nmd__ktmg = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        lzqj__yxwmc = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{jzovp__via}'" if
                isinstance(jzovp__via, str) else f'{jzovp__via}' for
                jzovp__via in rolling.selection if jzovp__via != rolling.on))
        wje__zvfan = fllaa__yvmkr = ''
        if fname == 'apply':
            wje__zvfan = 'func, raw, args, kwargs'
            fllaa__yvmkr = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            wje__zvfan = fllaa__yvmkr = 'other, pairwise'
        if fname == 'cov':
            wje__zvfan = fllaa__yvmkr = 'other, pairwise, ddof'
        fpmr__llhww = (
            f'lambda df, window, minp, center, {wje__zvfan}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {lzqj__yxwmc}){selection}.{fname}({fllaa__yvmkr})'
            )
        nmd__ktmg += f"""  return rolling.obj.apply({fpmr__llhww}, rolling.window, rolling.min_periods, rolling.center, {wje__zvfan})
"""
        qcu__hhg = {}
        exec(nmd__ktmg, {'bodo': bodo}, qcu__hhg)
        impl = qcu__hhg['impl']
        return impl
    qkk__fpd = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if qkk__fpd else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if qkk__fpd else rolling.obj_type.columns
        other_cols = None if qkk__fpd else other.columns
        ibaj__jze, ersmu__ddis = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        ibaj__jze, ersmu__ddis, out_cols = _gen_df_rolling_out_data(rolling)
    bpw__ojux = qkk__fpd or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    tpxp__eujde = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    tpxp__eujde += '  df = rolling.obj\n'
    tpxp__eujde += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if qkk__fpd else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    qqeu__nsfo = 'None'
    if qkk__fpd:
        qqeu__nsfo = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif bpw__ojux:
        mltr__shk = (set(out_cols) - set([rolling.on])).pop()
        qqeu__nsfo = f"'{mltr__shk}'" if isinstance(mltr__shk, str) else str(
            mltr__shk)
    tpxp__eujde += f'  name = {qqeu__nsfo}\n'
    tpxp__eujde += '  window = rolling.window\n'
    tpxp__eujde += '  center = rolling.center\n'
    tpxp__eujde += '  minp = rolling.min_periods\n'
    tpxp__eujde += f'  on_arr = {ersmu__ddis}\n'
    if fname == 'apply':
        tpxp__eujde += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        tpxp__eujde += f"  func = '{fname}'\n"
        tpxp__eujde += f'  index_arr = None\n'
        tpxp__eujde += f'  raw = False\n'
    if bpw__ojux:
        tpxp__eujde += (
            f'  return bodo.hiframes.pd_series_ext.init_series({ibaj__jze}, index, name)'
            )
        qcu__hhg = {}
        wik__ofroi = {'bodo': bodo}
        exec(tpxp__eujde, wik__ofroi, qcu__hhg)
        impl = qcu__hhg['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(tpxp__eujde, out_cols,
        ibaj__jze)


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
        mfv__tele = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(mfv__tele)


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
    byg__cyzis = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(byg__cyzis) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    wtj__uetw = not isinstance(window_type, types.Integer)
    ersmu__ddis = 'None'
    if wtj__uetw:
        ersmu__ddis = 'bodo.utils.conversion.index_to_array(index)'
    vmyf__qctyc = 'on_arr, ' if wtj__uetw else ''
    ibaj__jze = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {vmyf__qctyc}window, minp, center)'
            , ersmu__ddis)
    for mltr__shk in out_cols:
        if mltr__shk in df_cols and mltr__shk in other_cols:
            nor__tvew = df_cols.index(mltr__shk)
            awofu__ppvvl = other_cols.index(mltr__shk)
            gbyyi__tnb = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {nor__tvew}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {awofu__ppvvl}), {vmyf__qctyc}window, minp, center)'
                )
        else:
            gbyyi__tnb = 'np.full(len(df), np.nan)'
        ibaj__jze.append(gbyyi__tnb)
    return ', '.join(ibaj__jze), ersmu__ddis


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    nbwea__ofkhq = {'pairwise': pairwise, 'ddof': ddof}
    sgf__ajx = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        nbwea__ofkhq, sgf__ajx, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    nbwea__ofkhq = {'ddof': ddof, 'pairwise': pairwise}
    sgf__ajx = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        nbwea__ofkhq, sgf__ajx, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, lstb__zay = args
        if isinstance(rolling, RollingType):
            byg__cyzis = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(lstb__zay, (tuple, list)):
                if len(set(lstb__zay).difference(set(byg__cyzis))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(lstb__zay).difference(set(byg__cyzis))))
                selection = list(lstb__zay)
            else:
                if lstb__zay not in byg__cyzis:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(lstb__zay))
                selection = [lstb__zay]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            ojfai__jutzq = RollingType(rolling.obj_type, rolling.
                window_type, rolling.on, tuple(selection), True, series_select)
            return signature(ojfai__jutzq, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        byg__cyzis = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            byg__cyzis = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            byg__cyzis = rolling.obj_type.columns
        if attr in byg__cyzis:
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
    auf__vbcj = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    ydv__ktc = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in auf__vbcj):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        qpvh__obwj = ydv__ktc[auf__vbcj.index(get_literal_value(on))]
        if not isinstance(qpvh__obwj, types.Array
            ) or qpvh__obwj.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(wpl__ams.dtype, (types.Boolean, types.Number)) for
        wpl__ams in ydv__ktc):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
