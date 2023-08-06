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
        wgk__qpl = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(wgk__qpl)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        oyz__lpq = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, oyz__lpq)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        qye__fjcs, = args
        skpb__tzhq = signature.return_type
        fbw__olgpx = cgutils.create_struct_proxy(skpb__tzhq)(context, builder)
        fbw__olgpx.obj = qye__fjcs
        context.nrt.incref(builder, signature.args[0], qye__fjcs)
        return fbw__olgpx._getvalue()
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
        ysmp__lhpw = 'def impl(S_dt):\n'
        ysmp__lhpw += '    S = S_dt._obj\n'
        ysmp__lhpw += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ysmp__lhpw += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ysmp__lhpw += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ysmp__lhpw += '    numba.parfors.parfor.init_prange()\n'
        ysmp__lhpw += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            ysmp__lhpw += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            ysmp__lhpw += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        ysmp__lhpw += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        ysmp__lhpw += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        ysmp__lhpw += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        ysmp__lhpw += '            continue\n'
        ysmp__lhpw += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            ysmp__lhpw += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                ysmp__lhpw += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            ysmp__lhpw += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            npw__loej = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            ysmp__lhpw += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            ysmp__lhpw += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            ysmp__lhpw += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(npw__loej[field]))
        elif field == 'is_leap_year':
            ysmp__lhpw += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            ysmp__lhpw += """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)
"""
        elif field in ('daysinmonth', 'days_in_month'):
            npw__loej = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            ysmp__lhpw += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            ysmp__lhpw += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            ysmp__lhpw += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(npw__loej[field]))
        else:
            ysmp__lhpw += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            ysmp__lhpw += '        out_arr[i] = ts.' + field + '\n'
        ysmp__lhpw += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        eck__mhno = {}
        exec(ysmp__lhpw, {'bodo': bodo, 'numba': numba, 'np': np}, eck__mhno)
        impl = eck__mhno['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        htfzy__yzkhf = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(htfzy__yzkhf)


_install_date_fields()


def create_date_method_overload(method):
    bgxu__ibg = method in ['day_name', 'month_name']
    if bgxu__ibg:
        ysmp__lhpw = 'def overload_method(S_dt, locale=None):\n'
        ysmp__lhpw += '    unsupported_args = dict(locale=locale)\n'
        ysmp__lhpw += '    arg_defaults = dict(locale=None)\n'
        ysmp__lhpw += '    bodo.utils.typing.check_unsupported_args(\n'
        ysmp__lhpw += f"        'Series.dt.{method}',\n"
        ysmp__lhpw += '        unsupported_args,\n'
        ysmp__lhpw += '        arg_defaults,\n'
        ysmp__lhpw += "        package_name='pandas',\n"
        ysmp__lhpw += "        module_name='Series',\n"
        ysmp__lhpw += '    )\n'
    else:
        ysmp__lhpw = 'def overload_method(S_dt):\n'
        ysmp__lhpw += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    ysmp__lhpw += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    ysmp__lhpw += '        return\n'
    if bgxu__ibg:
        ysmp__lhpw += '    def impl(S_dt, locale=None):\n'
    else:
        ysmp__lhpw += '    def impl(S_dt):\n'
    ysmp__lhpw += '        S = S_dt._obj\n'
    ysmp__lhpw += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ysmp__lhpw += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ysmp__lhpw += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    ysmp__lhpw += '        numba.parfors.parfor.init_prange()\n'
    ysmp__lhpw += '        n = len(arr)\n'
    if bgxu__ibg:
        ysmp__lhpw += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        ysmp__lhpw += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    ysmp__lhpw += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    ysmp__lhpw += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    ysmp__lhpw += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    ysmp__lhpw += '                continue\n'
    ysmp__lhpw += (
        '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n')
    ysmp__lhpw += f'            method_val = ts.{method}()\n'
    if bgxu__ibg:
        ysmp__lhpw += '            out_arr[i] = method_val\n'
    else:
        ysmp__lhpw += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    ysmp__lhpw += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    ysmp__lhpw += '    return impl\n'
    eck__mhno = {}
    exec(ysmp__lhpw, {'bodo': bodo, 'numba': numba, 'np': np}, eck__mhno)
    overload_method = eck__mhno['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        htfzy__yzkhf = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            htfzy__yzkhf)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        fqok__afw = S_dt._obj
        jga__qpkmr = bodo.hiframes.pd_series_ext.get_series_data(fqok__afw)
        hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(fqok__afw)
        wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(fqok__afw)
        numba.parfors.parfor.init_prange()
        oht__cfdzf = len(jga__qpkmr)
        goy__hfo = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            oht__cfdzf)
        for zvq__jktpi in numba.parfors.parfor.internal_prange(oht__cfdzf):
            hwlcy__pft = jga__qpkmr[zvq__jktpi]
            qcs__lvt = bodo.utils.conversion.box_if_dt64(hwlcy__pft)
            goy__hfo[zvq__jktpi] = datetime.date(qcs__lvt.year, qcs__lvt.
                month, qcs__lvt.day)
        return bodo.hiframes.pd_series_ext.init_series(goy__hfo, hhu__nesyi,
            wgk__qpl)
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
            htxed__hyo = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            xgyj__pjrq = 'convert_numpy_timedelta64_to_pd_timedelta'
            oghip__xqwm = 'np.empty(n, np.int64)'
            llk__indds = attr
        elif attr == 'isocalendar':
            htxed__hyo = ['year', 'week', 'day']
            xgyj__pjrq = 'convert_datetime64_to_timestamp'
            oghip__xqwm = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            llk__indds = attr + '()'
        ysmp__lhpw = 'def impl(S_dt):\n'
        ysmp__lhpw += '    S = S_dt._obj\n'
        ysmp__lhpw += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ysmp__lhpw += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ysmp__lhpw += '    numba.parfors.parfor.init_prange()\n'
        ysmp__lhpw += '    n = len(arr)\n'
        for field in htxed__hyo:
            ysmp__lhpw += '    {} = {}\n'.format(field, oghip__xqwm)
        ysmp__lhpw += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        ysmp__lhpw += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in htxed__hyo:
            ysmp__lhpw += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        ysmp__lhpw += '            continue\n'
        dya__ztta = '(' + '[i], '.join(htxed__hyo) + '[i])'
        ysmp__lhpw += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(dya__ztta, xgyj__pjrq, llk__indds))
        ntsqd__okpa = '(' + ', '.join(htxed__hyo) + ')'
        ysmp__lhpw += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(ntsqd__okpa))
        eck__mhno = {}
        exec(ysmp__lhpw, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(htxed__hyo))}, eck__mhno)
        impl = eck__mhno['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    dfqr__piwj = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, ieok__nimj in dfqr__piwj:
        htfzy__yzkhf = create_series_dt_df_output_overload(attr)
        ieok__nimj(SeriesDatetimePropertiesType, attr, inline='always')(
            htfzy__yzkhf)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        ysmp__lhpw = 'def impl(S_dt):\n'
        ysmp__lhpw += '    S = S_dt._obj\n'
        ysmp__lhpw += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ysmp__lhpw += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ysmp__lhpw += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ysmp__lhpw += '    numba.parfors.parfor.init_prange()\n'
        ysmp__lhpw += '    n = len(A)\n'
        ysmp__lhpw += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        ysmp__lhpw += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        ysmp__lhpw += '        if bodo.libs.array_kernels.isna(A, i):\n'
        ysmp__lhpw += '            bodo.libs.array_kernels.setna(B, i)\n'
        ysmp__lhpw += '            continue\n'
        ysmp__lhpw += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if field == 'nanoseconds':
            ysmp__lhpw += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            ysmp__lhpw += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            ysmp__lhpw += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            ysmp__lhpw += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        ysmp__lhpw += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        eck__mhno = {}
        exec(ysmp__lhpw, {'numba': numba, 'np': np, 'bodo': bodo}, eck__mhno)
        impl = eck__mhno['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        ysmp__lhpw = 'def impl(S_dt):\n'
        ysmp__lhpw += '    S = S_dt._obj\n'
        ysmp__lhpw += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ysmp__lhpw += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ysmp__lhpw += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ysmp__lhpw += '    numba.parfors.parfor.init_prange()\n'
        ysmp__lhpw += '    n = len(A)\n'
        if method == 'total_seconds':
            ysmp__lhpw += '    B = np.empty(n, np.float64)\n'
        else:
            ysmp__lhpw += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        ysmp__lhpw += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        ysmp__lhpw += '        if bodo.libs.array_kernels.isna(A, i):\n'
        ysmp__lhpw += '            bodo.libs.array_kernels.setna(B, i)\n'
        ysmp__lhpw += '            continue\n'
        ysmp__lhpw += """        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])
"""
        if method == 'total_seconds':
            ysmp__lhpw += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            ysmp__lhpw += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            ysmp__lhpw += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            ysmp__lhpw += '    return B\n'
        eck__mhno = {}
        exec(ysmp__lhpw, {'numba': numba, 'np': np, 'bodo': bodo,
            'datetime': datetime}, eck__mhno)
        impl = eck__mhno['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        htfzy__yzkhf = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(htfzy__yzkhf)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        htfzy__yzkhf = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            htfzy__yzkhf)


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
        fqok__afw = S_dt._obj
        sdxm__fpx = bodo.hiframes.pd_series_ext.get_series_data(fqok__afw)
        hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(fqok__afw)
        wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(fqok__afw)
        numba.parfors.parfor.init_prange()
        oht__cfdzf = len(sdxm__fpx)
        odld__xpyah = bodo.libs.str_arr_ext.pre_alloc_string_array(oht__cfdzf,
            -1)
        for zvs__qbg in numba.parfors.parfor.internal_prange(oht__cfdzf):
            if bodo.libs.array_kernels.isna(sdxm__fpx, zvs__qbg):
                bodo.libs.array_kernels.setna(odld__xpyah, zvs__qbg)
                continue
            odld__xpyah[zvs__qbg] = bodo.utils.conversion.box_if_dt64(sdxm__fpx
                [zvs__qbg]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(odld__xpyah,
            hhu__nesyi, wgk__qpl)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        fqok__afw = S_dt._obj
        ftv__lrfna = get_series_data(fqok__afw).tz_convert(tz)
        hhu__nesyi = get_series_index(fqok__afw)
        wgk__qpl = get_series_name(fqok__afw)
        return init_series(ftv__lrfna, hhu__nesyi, wgk__qpl)
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
        shps__traw = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        wud__gewv = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', shps__traw, wud__gewv,
            package_name='pandas', module_name='Series')
        ysmp__lhpw = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        ysmp__lhpw += '    S = S_dt._obj\n'
        ysmp__lhpw += (
            '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ysmp__lhpw += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ysmp__lhpw += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ysmp__lhpw += '    numba.parfors.parfor.init_prange()\n'
        ysmp__lhpw += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            ysmp__lhpw += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            ysmp__lhpw += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        ysmp__lhpw += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        ysmp__lhpw += '        if bodo.libs.array_kernels.isna(A, i):\n'
        ysmp__lhpw += '            bodo.libs.array_kernels.setna(B, i)\n'
        ysmp__lhpw += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            vimaz__wvdoj = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            ikx__boip = 'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64'
        else:
            vimaz__wvdoj = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            ikx__boip = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        ysmp__lhpw += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            ikx__boip, vimaz__wvdoj, method)
        ysmp__lhpw += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        eck__mhno = {}
        exec(ysmp__lhpw, {'numba': numba, 'np': np, 'bodo': bodo}, eck__mhno)
        impl = eck__mhno['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    jvk__njqvb = ['ceil', 'floor', 'round']
    for method in jvk__njqvb:
        htfzy__yzkhf = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            htfzy__yzkhf)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                inr__utbmw = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                clc__fcnv = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    inr__utbmw)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                kjuzk__vprt = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ympzl__kmo = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    kjuzk__vprt)
                oht__cfdzf = len(clc__fcnv)
                fqok__afw = np.empty(oht__cfdzf, timedelta64_dtype)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    edv__rcsa = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        clc__fcnv[zvq__jktpi])
                    juu__cds = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        ympzl__kmo[zvq__jktpi])
                    if edv__rcsa == bkqdh__sylk or juu__cds == bkqdh__sylk:
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(edv__rcsa, juu__cds)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ympzl__kmo = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                oht__cfdzf = len(jga__qpkmr)
                fqok__afw = np.empty(oht__cfdzf, dt64_dtype)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    sgkkt__vnvh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    wdap__khlg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ympzl__kmo[zvq__jktpi]))
                    if sgkkt__vnvh == bkqdh__sylk or wdap__khlg == bkqdh__sylk:
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(sgkkt__vnvh, wdap__khlg)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ympzl__kmo = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                oht__cfdzf = len(jga__qpkmr)
                fqok__afw = np.empty(oht__cfdzf, dt64_dtype)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    sgkkt__vnvh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    wdap__khlg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(ympzl__kmo[zvq__jktpi]))
                    if sgkkt__vnvh == bkqdh__sylk or wdap__khlg == bkqdh__sylk:
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(sgkkt__vnvh, wdap__khlg)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                oht__cfdzf = len(jga__qpkmr)
                fqok__afw = np.empty(oht__cfdzf, timedelta64_dtype)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                xwfpj__sbph = rhs.value
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    sgkkt__vnvh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if (sgkkt__vnvh == bkqdh__sylk or xwfpj__sbph ==
                        bkqdh__sylk):
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(sgkkt__vnvh, xwfpj__sbph)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                oht__cfdzf = len(jga__qpkmr)
                fqok__afw = np.empty(oht__cfdzf, timedelta64_dtype)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                xwfpj__sbph = lhs.value
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    sgkkt__vnvh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if (xwfpj__sbph == bkqdh__sylk or sgkkt__vnvh ==
                        bkqdh__sylk):
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(xwfpj__sbph, sgkkt__vnvh)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                oht__cfdzf = len(jga__qpkmr)
                fqok__afw = np.empty(oht__cfdzf, dt64_dtype)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                rmmpp__zzmnt = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                wdap__khlg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(rmmpp__zzmnt))
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    sgkkt__vnvh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if sgkkt__vnvh == bkqdh__sylk or wdap__khlg == bkqdh__sylk:
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(sgkkt__vnvh, wdap__khlg)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                oht__cfdzf = len(jga__qpkmr)
                fqok__afw = np.empty(oht__cfdzf, dt64_dtype)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                rmmpp__zzmnt = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                wdap__khlg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(rmmpp__zzmnt))
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    sgkkt__vnvh = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if sgkkt__vnvh == bkqdh__sylk or wdap__khlg == bkqdh__sylk:
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(sgkkt__vnvh, wdap__khlg)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                oht__cfdzf = len(jga__qpkmr)
                fqok__afw = np.empty(oht__cfdzf, timedelta64_dtype)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                nvuim__cotxe = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                sgkkt__vnvh = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    nvuim__cotxe)
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    mavbd__rcp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if mavbd__rcp == bkqdh__sylk or sgkkt__vnvh == bkqdh__sylk:
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(mavbd__rcp, sgkkt__vnvh)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                oht__cfdzf = len(jga__qpkmr)
                fqok__afw = np.empty(oht__cfdzf, timedelta64_dtype)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                nvuim__cotxe = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                sgkkt__vnvh = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    nvuim__cotxe)
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    mavbd__rcp = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if sgkkt__vnvh == bkqdh__sylk or mavbd__rcp == bkqdh__sylk:
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(sgkkt__vnvh, mavbd__rcp)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            iqv__vsq = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                jga__qpkmr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                oht__cfdzf = len(jga__qpkmr)
                fqok__afw = np.empty(oht__cfdzf, timedelta64_dtype)
                bkqdh__sylk = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(iqv__vsq))
                rmmpp__zzmnt = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                wdap__khlg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(rmmpp__zzmnt))
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    ade__osgsw = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if wdap__khlg == bkqdh__sylk or ade__osgsw == bkqdh__sylk:
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(ade__osgsw, wdap__khlg)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            iqv__vsq = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                jga__qpkmr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                oht__cfdzf = len(jga__qpkmr)
                fqok__afw = np.empty(oht__cfdzf, timedelta64_dtype)
                bkqdh__sylk = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(iqv__vsq))
                rmmpp__zzmnt = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                wdap__khlg = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(rmmpp__zzmnt))
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    ade__osgsw = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if wdap__khlg == bkqdh__sylk or ade__osgsw == bkqdh__sylk:
                        hprop__gqls = bkqdh__sylk
                    else:
                        hprop__gqls = op(wdap__khlg, ade__osgsw)
                    fqok__afw[zvq__jktpi
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        hprop__gqls)
                return bodo.hiframes.pd_series_ext.init_series(fqok__afw,
                    hhu__nesyi, wgk__qpl)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            tam__hahr = True
        else:
            tam__hahr = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            iqv__vsq = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                jga__qpkmr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                oht__cfdzf = len(jga__qpkmr)
                goy__hfo = bodo.libs.bool_arr_ext.alloc_bool_array(oht__cfdzf)
                bkqdh__sylk = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(iqv__vsq))
                emm__jgg = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                ovjh__hab = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(emm__jgg))
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    dqxxu__tbnm = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if dqxxu__tbnm == bkqdh__sylk or ovjh__hab == bkqdh__sylk:
                        hprop__gqls = tam__hahr
                    else:
                        hprop__gqls = op(dqxxu__tbnm, ovjh__hab)
                    goy__hfo[zvq__jktpi] = hprop__gqls
                return bodo.hiframes.pd_series_ext.init_series(goy__hfo,
                    hhu__nesyi, wgk__qpl)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            iqv__vsq = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                jga__qpkmr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                oht__cfdzf = len(jga__qpkmr)
                goy__hfo = bodo.libs.bool_arr_ext.alloc_bool_array(oht__cfdzf)
                bkqdh__sylk = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(iqv__vsq))
                lsy__kaaao = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                dqxxu__tbnm = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(lsy__kaaao))
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    ovjh__hab = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if dqxxu__tbnm == bkqdh__sylk or ovjh__hab == bkqdh__sylk:
                        hprop__gqls = tam__hahr
                    else:
                        hprop__gqls = op(dqxxu__tbnm, ovjh__hab)
                    goy__hfo[zvq__jktpi] = hprop__gqls
                return bodo.hiframes.pd_series_ext.init_series(goy__hfo,
                    hhu__nesyi, wgk__qpl)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                oht__cfdzf = len(jga__qpkmr)
                goy__hfo = bodo.libs.bool_arr_ext.alloc_bool_array(oht__cfdzf)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    dqxxu__tbnm = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if dqxxu__tbnm == bkqdh__sylk or rhs.value == bkqdh__sylk:
                        hprop__gqls = tam__hahr
                    else:
                        hprop__gqls = op(dqxxu__tbnm, rhs.value)
                    goy__hfo[zvq__jktpi] = hprop__gqls
                return bodo.hiframes.pd_series_ext.init_series(goy__hfo,
                    hhu__nesyi, wgk__qpl)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                oht__cfdzf = len(jga__qpkmr)
                goy__hfo = bodo.libs.bool_arr_ext.alloc_bool_array(oht__cfdzf)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    ovjh__hab = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        jga__qpkmr[zvq__jktpi])
                    if ovjh__hab == bkqdh__sylk or lhs.value == bkqdh__sylk:
                        hprop__gqls = tam__hahr
                    else:
                        hprop__gqls = op(lhs.value, ovjh__hab)
                    goy__hfo[zvq__jktpi] = hprop__gqls
                return bodo.hiframes.pd_series_ext.init_series(goy__hfo,
                    hhu__nesyi, wgk__qpl)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                oht__cfdzf = len(jga__qpkmr)
                goy__hfo = bodo.libs.bool_arr_ext.alloc_bool_array(oht__cfdzf)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                wyw__bwh = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                qyddj__zuc = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wyw__bwh)
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    dqxxu__tbnm = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if dqxxu__tbnm == bkqdh__sylk or qyddj__zuc == bkqdh__sylk:
                        hprop__gqls = tam__hahr
                    else:
                        hprop__gqls = op(dqxxu__tbnm, qyddj__zuc)
                    goy__hfo[zvq__jktpi] = hprop__gqls
                return bodo.hiframes.pd_series_ext.init_series(goy__hfo,
                    hhu__nesyi, wgk__qpl)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            iqv__vsq = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                nvdf__adaf = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                jga__qpkmr = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    nvdf__adaf)
                hhu__nesyi = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                wgk__qpl = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                oht__cfdzf = len(jga__qpkmr)
                goy__hfo = bodo.libs.bool_arr_ext.alloc_bool_array(oht__cfdzf)
                bkqdh__sylk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    iqv__vsq)
                wyw__bwh = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                qyddj__zuc = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    wyw__bwh)
                for zvq__jktpi in numba.parfors.parfor.internal_prange(
                    oht__cfdzf):
                    nvuim__cotxe = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(jga__qpkmr[zvq__jktpi]))
                    if (nvuim__cotxe == bkqdh__sylk or qyddj__zuc ==
                        bkqdh__sylk):
                        hprop__gqls = tam__hahr
                    else:
                        hprop__gqls = op(qyddj__zuc, nvuim__cotxe)
                    goy__hfo[zvq__jktpi] = hprop__gqls
                return bodo.hiframes.pd_series_ext.init_series(goy__hfo,
                    hhu__nesyi, wgk__qpl)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for tpk__vle in series_dt_unsupported_attrs:
        mtdnv__cocjm = 'Series.dt.' + tpk__vle
        overload_attribute(SeriesDatetimePropertiesType, tpk__vle)(
            create_unsupported_overload(mtdnv__cocjm))
    for hvg__hgzva in series_dt_unsupported_methods:
        mtdnv__cocjm = 'Series.dt.' + hvg__hgzva
        overload_method(SeriesDatetimePropertiesType, hvg__hgzva,
            no_unliteral=True)(create_unsupported_overload(mtdnv__cocjm))


_install_series_dt_unsupported()
