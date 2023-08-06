"""
Support for Series.dt attributes and methods
"""
import datetime
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_series_ext import SeriesType, get_series_data, get_series_index, get_series_name, init_series
from bodo.libs.pd_datetime_arr_ext import PandasDatetimeTZDtype
from bodo.utils.typing import BodoError, ColNamesMetaType, check_unsupported_args, create_unsupported_overload, raise_bodo_error
dt64_dtype = np.dtype('datetime64[ns]')
timedelta64_dtype = np.dtype('timedelta64[ns]')


class SeriesDatetimePropertiesType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        hrzli__oen = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(hrzli__oen)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qcko__baenl = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, qcko__baenl)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        yprl__qpqsj, = args
        ssaxj__auw = signature.return_type
        sajux__dzuhj = cgutils.create_struct_proxy(ssaxj__auw)(context, builder
            )
        sajux__dzuhj.obj = yprl__qpqsj
        context.nrt.incref(builder, signature.args[0], yprl__qpqsj)
        return sajux__dzuhj._getvalue()
    return SeriesDatetimePropertiesType(obj)(obj), codegen


@overload_attribute(SeriesType, 'dt')
def overload_series_dt(s):
    if not (bodo.hiframes.pd_series_ext.is_dt64_series_typ(s) or bodo.
        hiframes.pd_series_ext.is_timedelta64_series_typ(s)):
        raise_bodo_error('Can only use .dt accessor with datetimelike values.')
    return lambda s: bodo.hiframes.series_dt_impl.init_series_dt_properties(s)


def create_date_field_overload(field):

    def overload_field(S_dt):
        if S_dt.stype.dtype != types.NPDatetime('ns') and not isinstance(S_dt
            .stype.dtype, PandasDatetimeTZDtype):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{field}')
        iexs__gzk = 'def impl(S_dt):\n'
        iexs__gzk += '    S = S_dt._obj\n'
        iexs__gzk += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        iexs__gzk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        iexs__gzk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        iexs__gzk += '    numba.parfors.parfor.init_prange()\n'
        iexs__gzk += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            iexs__gzk += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            iexs__gzk += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        iexs__gzk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        iexs__gzk += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        iexs__gzk += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        iexs__gzk += '            continue\n'
        iexs__gzk += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            iexs__gzk += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                iexs__gzk += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            iexs__gzk += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            nuei__chef = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            iexs__gzk += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            iexs__gzk += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            iexs__gzk += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(nuei__chef[field]))
        elif field == 'is_leap_year':
            iexs__gzk += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            iexs__gzk += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)\n'
                )
        elif field in ('daysinmonth', 'days_in_month'):
            nuei__chef = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            iexs__gzk += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            iexs__gzk += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            iexs__gzk += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(nuei__chef[field]))
        else:
            iexs__gzk += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            iexs__gzk += '        out_arr[i] = ts.' + field + '\n'
        iexs__gzk += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        qrqr__qqoyw = {}
        exec(iexs__gzk, {'bodo': bodo, 'numba': numba, 'np': np}, qrqr__qqoyw)
        impl = qrqr__qqoyw['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        dxxt__mnrs = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(dxxt__mnrs)


_install_date_fields()


def create_date_method_overload(method):
    gzk__txsi = method in ['day_name', 'month_name']
    if gzk__txsi:
        iexs__gzk = 'def overload_method(S_dt, locale=None):\n'
        iexs__gzk += '    unsupported_args = dict(locale=locale)\n'
        iexs__gzk += '    arg_defaults = dict(locale=None)\n'
        iexs__gzk += '    bodo.utils.typing.check_unsupported_args(\n'
        iexs__gzk += f"        'Series.dt.{method}',\n"
        iexs__gzk += '        unsupported_args,\n'
        iexs__gzk += '        arg_defaults,\n'
        iexs__gzk += "        package_name='pandas',\n"
        iexs__gzk += "        module_name='Series',\n"
        iexs__gzk += '    )\n'
    else:
        iexs__gzk = 'def overload_method(S_dt):\n'
        iexs__gzk += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    iexs__gzk += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    iexs__gzk += '        return\n'
    if gzk__txsi:
        iexs__gzk += '    def impl(S_dt, locale=None):\n'
    else:
        iexs__gzk += '    def impl(S_dt):\n'
    iexs__gzk += '        S = S_dt._obj\n'
    iexs__gzk += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    iexs__gzk += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    iexs__gzk += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    iexs__gzk += '        numba.parfors.parfor.init_prange()\n'
    iexs__gzk += '        n = len(arr)\n'
    if gzk__txsi:
        iexs__gzk += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        iexs__gzk += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    iexs__gzk += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    iexs__gzk += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    iexs__gzk += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    iexs__gzk += '                continue\n'
    iexs__gzk += '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n'
    iexs__gzk += f'            method_val = ts.{method}()\n'
    if gzk__txsi:
        iexs__gzk += '            out_arr[i] = method_val\n'
    else:
        iexs__gzk += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    iexs__gzk += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    iexs__gzk += '    return impl\n'
    qrqr__qqoyw = {}
    exec(iexs__gzk, {'bodo': bodo, 'numba': numba, 'np': np}, qrqr__qqoyw)
    overload_method = qrqr__qqoyw['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        dxxt__mnrs = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            dxxt__mnrs)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        jqwr__ujpmg = S_dt._obj
        yilj__fyav = bodo.hiframes.pd_series_ext.get_series_data(jqwr__ujpmg)
        ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(jqwr__ujpmg)
        hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(jqwr__ujpmg)
        numba.parfors.parfor.init_prange()
        yxxma__mcgwn = len(yilj__fyav)
        pkyr__actvl = (bodo.hiframes.datetime_date_ext.
            alloc_datetime_date_array(yxxma__mcgwn))
        for kryx__nytv in numba.parfors.parfor.internal_prange(yxxma__mcgwn):
            ewucp__yrml = yilj__fyav[kryx__nytv]
            ocyg__gvt = bodo.utils.conversion.box_if_dt64(ewucp__yrml)
            pkyr__actvl[kryx__nytv] = datetime.date(ocyg__gvt.year,
                ocyg__gvt.month, ocyg__gvt.day)
        return bodo.hiframes.pd_series_ext.init_series(pkyr__actvl,
            ytrd__fzkgk, hrzli__oen)
    return impl


def create_series_dt_df_output_overload(attr):

    def series_dt_df_output_overload(S_dt):
        if not (attr == 'components' and S_dt.stype.dtype == types.
            NPTimedelta('ns') or attr == 'isocalendar' and (S_dt.stype.
            dtype == types.NPDatetime('ns') or isinstance(S_dt.stype.dtype,
            PandasDatetimeTZDtype))):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{attr}')
        if attr == 'components':
            zsc__kclsb = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            ewsag__lest = 'convert_numpy_timedelta64_to_pd_timedelta'
            orm__yxdpd = 'np.empty(n, np.int64)'
            tbb__gxjf = attr
        elif attr == 'isocalendar':
            zsc__kclsb = ['year', 'week', 'day']
            ewsag__lest = 'convert_datetime64_to_timestamp'
            orm__yxdpd = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            tbb__gxjf = attr + '()'
        iexs__gzk = 'def impl(S_dt):\n'
        iexs__gzk += '    S = S_dt._obj\n'
        iexs__gzk += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        iexs__gzk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        iexs__gzk += '    numba.parfors.parfor.init_prange()\n'
        iexs__gzk += '    n = len(arr)\n'
        for field in zsc__kclsb:
            iexs__gzk += '    {} = {}\n'.format(field, orm__yxdpd)
        iexs__gzk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        iexs__gzk += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in zsc__kclsb:
            iexs__gzk += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        iexs__gzk += '            continue\n'
        jml__uusz = '(' + '[i], '.join(zsc__kclsb) + '[i])'
        iexs__gzk += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(jml__uusz, ewsag__lest, tbb__gxjf))
        cbdr__rkaiq = '(' + ', '.join(zsc__kclsb) + ')'
        iexs__gzk += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(cbdr__rkaiq))
        qrqr__qqoyw = {}
        exec(iexs__gzk, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(zsc__kclsb))}, qrqr__qqoyw)
        impl = qrqr__qqoyw['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    cut__xxd = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, uuz__ssp in cut__xxd:
        dxxt__mnrs = create_series_dt_df_output_overload(attr)
        uuz__ssp(SeriesDatetimePropertiesType, attr, inline='always')(
            dxxt__mnrs)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        iexs__gzk = 'def impl(S_dt):\n'
        iexs__gzk += '    S = S_dt._obj\n'
        iexs__gzk += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        iexs__gzk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        iexs__gzk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        iexs__gzk += '    numba.parfors.parfor.init_prange()\n'
        iexs__gzk += '    n = len(A)\n'
        iexs__gzk += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        iexs__gzk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        iexs__gzk += '        if bodo.libs.array_kernels.isna(A, i):\n'
        iexs__gzk += '            bodo.libs.array_kernels.setna(B, i)\n'
        iexs__gzk += '            continue\n'
        iexs__gzk += (
            '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
            )
        if field == 'nanoseconds':
            iexs__gzk += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            iexs__gzk += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            iexs__gzk += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            iexs__gzk += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        iexs__gzk += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        qrqr__qqoyw = {}
        exec(iexs__gzk, {'numba': numba, 'np': np, 'bodo': bodo}, qrqr__qqoyw)
        impl = qrqr__qqoyw['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        iexs__gzk = 'def impl(S_dt):\n'
        iexs__gzk += '    S = S_dt._obj\n'
        iexs__gzk += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        iexs__gzk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        iexs__gzk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        iexs__gzk += '    numba.parfors.parfor.init_prange()\n'
        iexs__gzk += '    n = len(A)\n'
        if method == 'total_seconds':
            iexs__gzk += '    B = np.empty(n, np.float64)\n'
        else:
            iexs__gzk += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        iexs__gzk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        iexs__gzk += '        if bodo.libs.array_kernels.isna(A, i):\n'
        iexs__gzk += '            bodo.libs.array_kernels.setna(B, i)\n'
        iexs__gzk += '            continue\n'
        iexs__gzk += (
            '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
            )
        if method == 'total_seconds':
            iexs__gzk += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            iexs__gzk += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            iexs__gzk += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            iexs__gzk += '    return B\n'
        qrqr__qqoyw = {}
        exec(iexs__gzk, {'numba': numba, 'np': np, 'bodo': bodo, 'datetime':
            datetime}, qrqr__qqoyw)
        impl = qrqr__qqoyw['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        dxxt__mnrs = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(dxxt__mnrs)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        dxxt__mnrs = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            dxxt__mnrs)


_install_S_dt_timedelta_methods()


@overload_method(SeriesDatetimePropertiesType, 'strftime', inline='always',
    no_unliteral=True)
def dt_strftime(S_dt, date_format):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return
    if types.unliteral(date_format) != types.unicode_type:
        raise BodoError(
            "Series.str.strftime(): 'date_format' argument must be a string")

    def impl(S_dt, date_format):
        jqwr__ujpmg = S_dt._obj
        axjz__kzrv = bodo.hiframes.pd_series_ext.get_series_data(jqwr__ujpmg)
        ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(jqwr__ujpmg)
        hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(jqwr__ujpmg)
        numba.parfors.parfor.init_prange()
        yxxma__mcgwn = len(axjz__kzrv)
        sue__zrrq = bodo.libs.str_arr_ext.pre_alloc_string_array(yxxma__mcgwn,
            -1)
        for jqj__qrirw in numba.parfors.parfor.internal_prange(yxxma__mcgwn):
            if bodo.libs.array_kernels.isna(axjz__kzrv, jqj__qrirw):
                bodo.libs.array_kernels.setna(sue__zrrq, jqj__qrirw)
                continue
            sue__zrrq[jqj__qrirw] = bodo.utils.conversion.box_if_dt64(
                axjz__kzrv[jqj__qrirw]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(sue__zrrq,
            ytrd__fzkgk, hrzli__oen)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        jqwr__ujpmg = S_dt._obj
        mcuo__ehq = get_series_data(jqwr__ujpmg).tz_convert(tz)
        ytrd__fzkgk = get_series_index(jqwr__ujpmg)
        hrzli__oen = get_series_name(jqwr__ujpmg)
        return init_series(mcuo__ehq, ytrd__fzkgk, hrzli__oen)
    return impl


def create_timedelta_freq_overload(method):

    def freq_overload(S_dt, freq, ambiguous='raise', nonexistent='raise'):
        if S_dt.stype.dtype != types.NPTimedelta('ns'
            ) and S_dt.stype.dtype != types.NPDatetime('ns'
            ) and not isinstance(S_dt.stype.dtype, bodo.libs.
            pd_datetime_arr_ext.PandasDatetimeTZDtype):
            return
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt,
            f'Series.dt.{method}()')
        wksa__rqm = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        zce__xdhru = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', wksa__rqm, zce__xdhru,
            package_name='pandas', module_name='Series')
        iexs__gzk = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        iexs__gzk += '    S = S_dt._obj\n'
        iexs__gzk += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        iexs__gzk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        iexs__gzk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        iexs__gzk += '    numba.parfors.parfor.init_prange()\n'
        iexs__gzk += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            iexs__gzk += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            iexs__gzk += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        iexs__gzk += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        iexs__gzk += '        if bodo.libs.array_kernels.isna(A, i):\n'
        iexs__gzk += '            bodo.libs.array_kernels.setna(B, i)\n'
        iexs__gzk += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            akr__zpn = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            utda__gysc = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            akr__zpn = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            utda__gysc = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        iexs__gzk += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            utda__gysc, akr__zpn, method)
        iexs__gzk += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        qrqr__qqoyw = {}
        exec(iexs__gzk, {'numba': numba, 'np': np, 'bodo': bodo}, qrqr__qqoyw)
        impl = qrqr__qqoyw['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    xejt__ybrjj = ['ceil', 'floor', 'round']
    for method in xejt__ybrjj:
        dxxt__mnrs = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            dxxt__mnrs)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yfg__twsex = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                zirs__mxbk = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yfg__twsex)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                litz__dxs = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ujah__mnl = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    litz__dxs)
                yxxma__mcgwn = len(zirs__mxbk)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, timedelta64_dtype)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    ksgt__sblp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(zirs__mxbk[kryx__nytv]))
                    hgd__lmia = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        ujah__mnl[kryx__nytv])
                    if ksgt__sblp == oppm__dzfn or hgd__lmia == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(ksgt__sblp, hgd__lmia)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ujah__mnl = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yxxma__mcgwn = len(yilj__fyav)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, dt64_dtype)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    gjet__bfte = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    cnv__vft = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ujah__mnl[kryx__nytv]))
                    if gjet__bfte == oppm__dzfn or cnv__vft == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(gjet__bfte, cnv__vft)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ujah__mnl = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yxxma__mcgwn = len(yilj__fyav)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, dt64_dtype)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    gjet__bfte = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    cnv__vft = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ujah__mnl[kryx__nytv]))
                    if gjet__bfte == oppm__dzfn or cnv__vft == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(gjet__bfte, cnv__vft)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                yxxma__mcgwn = len(yilj__fyav)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, timedelta64_dtype)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                zndu__bzrx = rhs.value
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    gjet__bfte = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    if gjet__bfte == oppm__dzfn or zndu__bzrx == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(gjet__bfte, zndu__bzrx)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                yxxma__mcgwn = len(yilj__fyav)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, timedelta64_dtype)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                zndu__bzrx = lhs.value
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    gjet__bfte = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    if zndu__bzrx == oppm__dzfn or gjet__bfte == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(zndu__bzrx, gjet__bfte)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                yxxma__mcgwn = len(yilj__fyav)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, dt64_dtype)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                dsqgw__ihvz = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                cnv__vft = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(dsqgw__ihvz))
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    gjet__bfte = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    if gjet__bfte == oppm__dzfn or cnv__vft == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(gjet__bfte, cnv__vft)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                yxxma__mcgwn = len(yilj__fyav)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, dt64_dtype)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                dsqgw__ihvz = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                cnv__vft = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(dsqgw__ihvz))
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    gjet__bfte = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    if gjet__bfte == oppm__dzfn or cnv__vft == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(gjet__bfte, cnv__vft)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                yxxma__mcgwn = len(yilj__fyav)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, timedelta64_dtype)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                zgqqd__bec = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                gjet__bfte = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    zgqqd__bec)
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    tgzze__ymt = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    if tgzze__ymt == oppm__dzfn or gjet__bfte == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(tgzze__ymt, gjet__bfte)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                yxxma__mcgwn = len(yilj__fyav)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, timedelta64_dtype)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                zgqqd__bec = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                gjet__bfte = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    zgqqd__bec)
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    tgzze__ymt = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    if gjet__bfte == oppm__dzfn or tgzze__ymt == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(gjet__bfte, tgzze__ymt)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            bva__kpr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yilj__fyav = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                yxxma__mcgwn = len(yilj__fyav)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, timedelta64_dtype)
                oppm__dzfn = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(bva__kpr))
                dsqgw__ihvz = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                cnv__vft = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(dsqgw__ihvz))
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    yvpo__mqjn = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yilj__fyav[kryx__nytv]))
                    if cnv__vft == oppm__dzfn or yvpo__mqjn == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(yvpo__mqjn, cnv__vft)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            bva__kpr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yilj__fyav = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                yxxma__mcgwn = len(yilj__fyav)
                jqwr__ujpmg = np.empty(yxxma__mcgwn, timedelta64_dtype)
                oppm__dzfn = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(bva__kpr))
                dsqgw__ihvz = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                cnv__vft = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(dsqgw__ihvz))
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    yvpo__mqjn = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yilj__fyav[kryx__nytv]))
                    if cnv__vft == oppm__dzfn or yvpo__mqjn == oppm__dzfn:
                        wzq__ixcw = oppm__dzfn
                    else:
                        wzq__ixcw = op(cnv__vft, yvpo__mqjn)
                    jqwr__ujpmg[kryx__nytv
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wzq__ixcw)
                return bodo.hiframes.pd_series_ext.init_series(jqwr__ujpmg,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            tdses__dme = True
        else:
            tdses__dme = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            bva__kpr = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yilj__fyav = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                yxxma__mcgwn = len(yilj__fyav)
                pkyr__actvl = bodo.libs.bool_arr_ext.alloc_bool_array(
                    yxxma__mcgwn)
                oppm__dzfn = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(bva__kpr))
                pcu__cywhq = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                dydhu__ngmg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(pcu__cywhq))
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    mvzur__bjsz = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yilj__fyav[kryx__nytv]))
                    if mvzur__bjsz == oppm__dzfn or dydhu__ngmg == oppm__dzfn:
                        wzq__ixcw = tdses__dme
                    else:
                        wzq__ixcw = op(mvzur__bjsz, dydhu__ngmg)
                    pkyr__actvl[kryx__nytv] = wzq__ixcw
                return bodo.hiframes.pd_series_ext.init_series(pkyr__actvl,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            bva__kpr = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yilj__fyav = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                yxxma__mcgwn = len(yilj__fyav)
                pkyr__actvl = bodo.libs.bool_arr_ext.alloc_bool_array(
                    yxxma__mcgwn)
                oppm__dzfn = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(bva__kpr))
                xcsr__njipf = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                mvzur__bjsz = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(xcsr__njipf))
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    dydhu__ngmg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(yilj__fyav[kryx__nytv]))
                    if mvzur__bjsz == oppm__dzfn or dydhu__ngmg == oppm__dzfn:
                        wzq__ixcw = tdses__dme
                    else:
                        wzq__ixcw = op(mvzur__bjsz, dydhu__ngmg)
                    pkyr__actvl[kryx__nytv] = wzq__ixcw
                return bodo.hiframes.pd_series_ext.init_series(pkyr__actvl,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                yxxma__mcgwn = len(yilj__fyav)
                pkyr__actvl = bodo.libs.bool_arr_ext.alloc_bool_array(
                    yxxma__mcgwn)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    mvzur__bjsz = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    if mvzur__bjsz == oppm__dzfn or rhs.value == oppm__dzfn:
                        wzq__ixcw = tdses__dme
                    else:
                        wzq__ixcw = op(mvzur__bjsz, rhs.value)
                    pkyr__actvl[kryx__nytv] = wzq__ixcw
                return bodo.hiframes.pd_series_ext.init_series(pkyr__actvl,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                yxxma__mcgwn = len(yilj__fyav)
                pkyr__actvl = bodo.libs.bool_arr_ext.alloc_bool_array(
                    yxxma__mcgwn)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    dydhu__ngmg = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    if dydhu__ngmg == oppm__dzfn or lhs.value == oppm__dzfn:
                        wzq__ixcw = tdses__dme
                    else:
                        wzq__ixcw = op(lhs.value, dydhu__ngmg)
                    pkyr__actvl[kryx__nytv] = wzq__ixcw
                return bodo.hiframes.pd_series_ext.init_series(pkyr__actvl,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                yxxma__mcgwn = len(yilj__fyav)
                pkyr__actvl = bodo.libs.bool_arr_ext.alloc_bool_array(
                    yxxma__mcgwn)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                irsn__wvdil = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(rhs))
                yrsk__rjq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    irsn__wvdil)
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    mvzur__bjsz = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    if mvzur__bjsz == oppm__dzfn or yrsk__rjq == oppm__dzfn:
                        wzq__ixcw = tdses__dme
                    else:
                        wzq__ixcw = op(mvzur__bjsz, yrsk__rjq)
                    pkyr__actvl[kryx__nytv] = wzq__ixcw
                return bodo.hiframes.pd_series_ext.init_series(pkyr__actvl,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            bva__kpr = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                elm__kgnl = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                yilj__fyav = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    elm__kgnl)
                ytrd__fzkgk = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                hrzli__oen = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                yxxma__mcgwn = len(yilj__fyav)
                pkyr__actvl = bodo.libs.bool_arr_ext.alloc_bool_array(
                    yxxma__mcgwn)
                oppm__dzfn = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    bva__kpr)
                irsn__wvdil = (bodo.hiframes.pd_timestamp_ext.
                    parse_datetime_str(lhs))
                yrsk__rjq = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    irsn__wvdil)
                for kryx__nytv in numba.parfors.parfor.internal_prange(
                    yxxma__mcgwn):
                    zgqqd__bec = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(yilj__fyav[kryx__nytv]))
                    if zgqqd__bec == oppm__dzfn or yrsk__rjq == oppm__dzfn:
                        wzq__ixcw = tdses__dme
                    else:
                        wzq__ixcw = op(yrsk__rjq, zgqqd__bec)
                    pkyr__actvl[kryx__nytv] = wzq__ixcw
                return bodo.hiframes.pd_series_ext.init_series(pkyr__actvl,
                    ytrd__fzkgk, hrzli__oen)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for nosk__mtu in series_dt_unsupported_attrs:
        zyjy__argbj = 'Series.dt.' + nosk__mtu
        overload_attribute(SeriesDatetimePropertiesType, nosk__mtu)(
            create_unsupported_overload(zyjy__argbj))
    for zkf__obqf in series_dt_unsupported_methods:
        zyjy__argbj = 'Series.dt.' + zkf__obqf
        overload_method(SeriesDatetimePropertiesType, zkf__obqf,
            no_unliteral=True)(create_unsupported_overload(zyjy__argbj))


_install_series_dt_unsupported()
