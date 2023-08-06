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
            xazep__poem = 'Series'
        else:
            xazep__poem = 'DataFrame'
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(obj_type,
            f'{xazep__poem}.rolling()')
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
        lbpb__vnuxm = [('obj', fe_type.obj_type), ('window', fe_type.
            window_type), ('min_periods', types.int64), ('center', types.bool_)
            ]
        super(RollingModel, self).__init__(dmm, fe_type, lbpb__vnuxm)


make_attribute_wrapper(RollingType, 'obj', 'obj')
make_attribute_wrapper(RollingType, 'window', 'window')
make_attribute_wrapper(RollingType, 'center', 'center')
make_attribute_wrapper(RollingType, 'min_periods', 'min_periods')


@overload_method(DataFrameType, 'rolling', inline='always', no_unliteral=True)
def df_rolling_overload(df, window, min_periods=None, center=False,
    win_type=None, on=None, axis=0, closed=None):
    check_runtime_cols_unsupported(df, 'DataFrame.rolling()')
    nrva__fspox = dict(win_type=win_type, axis=axis, closed=closed)
    rtx__wgd = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('DataFrame.rolling', nrva__fspox, rtx__wgd,
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
    nrva__fspox = dict(win_type=win_type, axis=axis, closed=closed)
    rtx__wgd = dict(win_type=None, axis=0, closed=None)
    check_unsupported_args('Series.rolling', nrva__fspox, rtx__wgd,
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
        yuq__viqmg, gwgc__jvjyp, kvtq__orkj, cime__ddpb, jfpqq__pkd = args
        oizfc__kbkrp = signature.return_type
        wfu__icyza = cgutils.create_struct_proxy(oizfc__kbkrp)(context, builder
            )
        wfu__icyza.obj = yuq__viqmg
        wfu__icyza.window = gwgc__jvjyp
        wfu__icyza.min_periods = kvtq__orkj
        wfu__icyza.center = cime__ddpb
        context.nrt.incref(builder, signature.args[0], yuq__viqmg)
        context.nrt.incref(builder, signature.args[1], gwgc__jvjyp)
        context.nrt.incref(builder, signature.args[2], kvtq__orkj)
        context.nrt.incref(builder, signature.args[3], cime__ddpb)
        return wfu__icyza._getvalue()
    on = get_literal_value(on_type)
    if isinstance(obj_type, SeriesType):
        selection = None
    elif isinstance(obj_type, DataFrameType):
        selection = obj_type.columns
    else:
        assert isinstance(obj_type, DataFrameGroupByType
            ), f'invalid obj type for rolling: {obj_type}'
        selection = obj_type.selection
    oizfc__kbkrp = RollingType(obj_type, window_type, on, selection, False)
    return oizfc__kbkrp(obj_type, window_type, min_periods_type,
        center_type, on_type), codegen


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
    gkn__btvt = not isinstance(rolling.window_type, types.Integer)
    lnjn__lwci = 'variable' if gkn__btvt else 'fixed'
    brhr__yjlw = 'None'
    if gkn__btvt:
        brhr__yjlw = ('bodo.utils.conversion.index_to_array(index)' if 
            rolling.on is None else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {rolling.obj_type.columns.index(rolling.on)})'
            )
    pjbkk__qzv = []
    ehxo__ifd = 'on_arr, ' if gkn__btvt else ''
    if isinstance(rolling.obj_type, SeriesType):
        return (
            f'bodo.hiframes.rolling.rolling_{lnjn__lwci}(bodo.hiframes.pd_series_ext.get_series_data(df), {ehxo__ifd}index_arr, window, minp, center, func, raw)'
            , brhr__yjlw, rolling.selection)
    assert isinstance(rolling.obj_type, DataFrameType
        ), 'expected df in rolling obj'
    mui__dpqz = rolling.obj_type.data
    out_cols = []
    for ifqeg__yasg in rolling.selection:
        klxcs__uwa = rolling.obj_type.columns.index(ifqeg__yasg)
        if ifqeg__yasg == rolling.on:
            if len(rolling.selection) == 2 and rolling.series_select:
                continue
            wdk__ackf = (
                f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {klxcs__uwa})'
                )
            out_cols.append(ifqeg__yasg)
        else:
            if not isinstance(mui__dpqz[klxcs__uwa].dtype, (types.Boolean,
                types.Number)):
                continue
            wdk__ackf = (
                f'bodo.hiframes.rolling.rolling_{lnjn__lwci}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {klxcs__uwa}), {ehxo__ifd}index_arr, window, minp, center, func, raw)'
                )
            out_cols.append(ifqeg__yasg)
        pjbkk__qzv.append(wdk__ackf)
    return ', '.join(pjbkk__qzv), brhr__yjlw, tuple(out_cols)


@overload_method(RollingType, 'apply', inline='always', no_unliteral=True)
def overload_rolling_apply(rolling, func, raw=False, engine=None,
    engine_kwargs=None, args=None, kwargs=None):
    nrva__fspox = dict(engine=engine, engine_kwargs=engine_kwargs, args=
        args, kwargs=kwargs)
    rtx__wgd = dict(engine=None, engine_kwargs=None, args=None, kwargs=None)
    check_unsupported_args('Rolling.apply', nrva__fspox, rtx__wgd,
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
    nrva__fspox = dict(win_type=win_type, axis=axis, closed=closed, method=
        method)
    rtx__wgd = dict(win_type=None, axis=0, closed=None, method='single')
    check_unsupported_args('GroupBy.rolling', nrva__fspox, rtx__wgd,
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
        sewhy__oxi = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
        mdl__qnxuv = f"'{rolling.on}'" if isinstance(rolling.on, str
            ) else f'{rolling.on}'
        selection = ''
        if rolling.explicit_select:
            selection = '[{}]'.format(', '.join(f"'{oohkc__tzywl}'" if
                isinstance(oohkc__tzywl, str) else f'{oohkc__tzywl}' for
                oohkc__tzywl in rolling.selection if oohkc__tzywl !=
                rolling.on))
        ofq__txd = pglw__ngeuc = ''
        if fname == 'apply':
            ofq__txd = 'func, raw, args, kwargs'
            pglw__ngeuc = 'func, raw, None, None, args, kwargs'
        if fname == 'corr':
            ofq__txd = pglw__ngeuc = 'other, pairwise'
        if fname == 'cov':
            ofq__txd = pglw__ngeuc = 'other, pairwise, ddof'
        nqth__nozq = (
            f'lambda df, window, minp, center, {ofq__txd}: bodo.hiframes.pd_rolling_ext.init_rolling(df, window, minp, center, {mdl__qnxuv}){selection}.{fname}({pglw__ngeuc})'
            )
        sewhy__oxi += f"""  return rolling.obj.apply({nqth__nozq}, rolling.window, rolling.min_periods, rolling.center, {ofq__txd})
"""
        koke__ioct = {}
        exec(sewhy__oxi, {'bodo': bodo}, koke__ioct)
        impl = koke__ioct['impl']
        return impl
    fvkx__smyxg = isinstance(rolling.obj_type, SeriesType)
    if fname in ('corr', 'cov'):
        out_cols = None if fvkx__smyxg else _get_corr_cov_out_cols(rolling,
            other, fname)
        df_cols = None if fvkx__smyxg else rolling.obj_type.columns
        other_cols = None if fvkx__smyxg else other.columns
        pjbkk__qzv, brhr__yjlw = _gen_corr_cov_out_data(out_cols, df_cols,
            other_cols, rolling.window_type, fname)
    else:
        pjbkk__qzv, brhr__yjlw, out_cols = _gen_df_rolling_out_data(rolling)
    wbk__jmnmc = fvkx__smyxg or len(rolling.selection) == (1 if rolling.on is
        None else 2) and rolling.series_select
    mbtl__fasml = f'def impl(rolling, {_get_rolling_func_args(fname)}):\n'
    mbtl__fasml += '  df = rolling.obj\n'
    mbtl__fasml += '  index = {}\n'.format(
        'bodo.hiframes.pd_series_ext.get_series_index(df)' if fvkx__smyxg else
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)')
    xazep__poem = 'None'
    if fvkx__smyxg:
        xazep__poem = 'bodo.hiframes.pd_series_ext.get_series_name(df)'
    elif wbk__jmnmc:
        ifqeg__yasg = (set(out_cols) - set([rolling.on])).pop()
        xazep__poem = f"'{ifqeg__yasg}'" if isinstance(ifqeg__yasg, str
            ) else str(ifqeg__yasg)
    mbtl__fasml += f'  name = {xazep__poem}\n'
    mbtl__fasml += '  window = rolling.window\n'
    mbtl__fasml += '  center = rolling.center\n'
    mbtl__fasml += '  minp = rolling.min_periods\n'
    mbtl__fasml += f'  on_arr = {brhr__yjlw}\n'
    if fname == 'apply':
        mbtl__fasml += (
            f'  index_arr = bodo.utils.conversion.index_to_array(index)\n')
    else:
        mbtl__fasml += f"  func = '{fname}'\n"
        mbtl__fasml += f'  index_arr = None\n'
        mbtl__fasml += f'  raw = False\n'
    if wbk__jmnmc:
        mbtl__fasml += (
            f'  return bodo.hiframes.pd_series_ext.init_series({pjbkk__qzv}, index, name)'
            )
        koke__ioct = {}
        egldu__oav = {'bodo': bodo}
        exec(mbtl__fasml, egldu__oav, koke__ioct)
        impl = koke__ioct['impl']
        return impl
    return bodo.hiframes.dataframe_impl._gen_init_df(mbtl__fasml, out_cols,
        pjbkk__qzv)


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
        fps__wwkhb = create_rolling_overload(fname)
        overload_method(RollingType, fname, inline='always', no_unliteral=True
            )(fps__wwkhb)


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
    yypmq__yezn = rolling.selection
    if rolling.on is not None:
        raise BodoError(
            f'variable window rolling {func_name} not supported yet.')
    out_cols = tuple(sorted(set(yypmq__yezn) | set(other.columns), key=lambda
        k: str(k)))
    return out_cols


def _gen_corr_cov_out_data(out_cols, df_cols, other_cols, window_type,
    func_name):
    gkn__btvt = not isinstance(window_type, types.Integer)
    brhr__yjlw = 'None'
    if gkn__btvt:
        brhr__yjlw = 'bodo.utils.conversion.index_to_array(index)'
    ehxo__ifd = 'on_arr, ' if gkn__btvt else ''
    pjbkk__qzv = []
    if out_cols is None:
        return (
            f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_series_ext.get_series_data(df), bodo.hiframes.pd_series_ext.get_series_data(other), {ehxo__ifd}window, minp, center)'
            , brhr__yjlw)
    for ifqeg__yasg in out_cols:
        if ifqeg__yasg in df_cols and ifqeg__yasg in other_cols:
            zcjz__qzv = df_cols.index(ifqeg__yasg)
            lqkc__tmhi = other_cols.index(ifqeg__yasg)
            wdk__ackf = (
                f'bodo.hiframes.rolling.rolling_{func_name}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {zcjz__qzv}), bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {lqkc__tmhi}), {ehxo__ifd}window, minp, center)'
                )
        else:
            wdk__ackf = 'np.full(len(df), np.nan)'
        pjbkk__qzv.append(wdk__ackf)
    return ', '.join(pjbkk__qzv), brhr__yjlw


@overload_method(RollingType, 'corr', inline='always', no_unliteral=True)
def overload_rolling_corr(rolling, other=None, pairwise=None, ddof=1):
    sqs__nvfra = {'pairwise': pairwise, 'ddof': ddof}
    xkyc__daa = {'pairwise': None, 'ddof': 1}
    check_unsupported_args('pandas.core.window.rolling.Rolling.corr',
        sqs__nvfra, xkyc__daa, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'corr', other)


@overload_method(RollingType, 'cov', inline='always', no_unliteral=True)
def overload_rolling_cov(rolling, other=None, pairwise=None, ddof=1):
    sqs__nvfra = {'ddof': ddof, 'pairwise': pairwise}
    xkyc__daa = {'ddof': 1, 'pairwise': None}
    check_unsupported_args('pandas.core.window.rolling.Rolling.cov',
        sqs__nvfra, xkyc__daa, package_name='pandas', module_name='Window')
    return _gen_rolling_impl(rolling, 'cov', other)


@infer
class GetItemDataFrameRolling2(AbstractTemplate):
    key = 'static_getitem'

    def generic(self, args, kws):
        rolling, aap__tkc = args
        if isinstance(rolling, RollingType):
            yypmq__yezn = rolling.obj_type.selection if isinstance(rolling.
                obj_type, DataFrameGroupByType) else rolling.obj_type.columns
            series_select = False
            if isinstance(aap__tkc, (tuple, list)):
                if len(set(aap__tkc).difference(set(yypmq__yezn))) > 0:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(set(aap__tkc).difference(set(yypmq__yezn))))
                selection = list(aap__tkc)
            else:
                if aap__tkc not in yypmq__yezn:
                    raise_bodo_error(
                        'rolling: selected column {} not found in dataframe'
                        .format(aap__tkc))
                selection = [aap__tkc]
                series_select = True
            if rolling.on is not None:
                selection.append(rolling.on)
            uszah__ludpd = RollingType(rolling.obj_type, rolling.
                window_type, rolling.on, tuple(selection), True, series_select)
            return signature(uszah__ludpd, *args)


@lower_builtin('static_getitem', RollingType, types.Any)
def static_getitem_df_groupby(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@infer_getattr
class RollingAttribute(AttributeTemplate):
    key = RollingType

    def generic_resolve(self, rolling, attr):
        yypmq__yezn = ()
        if isinstance(rolling.obj_type, DataFrameGroupByType):
            yypmq__yezn = rolling.obj_type.selection
        if isinstance(rolling.obj_type, DataFrameType):
            yypmq__yezn = rolling.obj_type.columns
        if attr in yypmq__yezn:
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
    syme__lmeq = obj.columns if isinstance(obj, DataFrameType
        ) else obj.df_type.columns if isinstance(obj, DataFrameGroupByType
        ) else []
    mui__dpqz = [obj.data] if isinstance(obj, SeriesType
        ) else obj.data if isinstance(obj, DataFrameType) else obj.df_type.data
    if not is_overload_none(on) and (not is_literal_type(on) or 
        get_literal_value(on) not in syme__lmeq):
        raise BodoError(
            f"{func_name}.rolling(): 'on' should be a constant column name.")
    if not is_overload_none(on):
        wxfq__cjox = mui__dpqz[syme__lmeq.index(get_literal_value(on))]
        if not isinstance(wxfq__cjox, types.Array
            ) or wxfq__cjox.dtype != bodo.datetime64ns:
            raise BodoError(
                f"{func_name}.rolling(): 'on' column should have datetime64 data."
                )
    if not any(isinstance(bdfgj__ynt.dtype, (types.Boolean, types.Number)) for
        bdfgj__ynt in mui__dpqz):
        raise BodoError(f'{func_name}.rolling(): No numeric types to aggregate'
            )
