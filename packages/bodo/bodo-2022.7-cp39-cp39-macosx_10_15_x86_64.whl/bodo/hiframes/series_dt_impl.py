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
        alsdg__bxfk = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(alsdg__bxfk)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ygrz__arpsr = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, ygrz__arpsr)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        fiiy__mxf, = args
        mvzff__ysfsn = signature.return_type
        rpidu__pms = cgutils.create_struct_proxy(mvzff__ysfsn)(context, builder
            )
        rpidu__pms.obj = fiiy__mxf
        context.nrt.incref(builder, signature.args[0], fiiy__mxf)
        return rpidu__pms._getvalue()
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
        zsz__tbxy = 'def impl(S_dt):\n'
        zsz__tbxy += '    S = S_dt._obj\n'
        zsz__tbxy += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        zsz__tbxy += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        zsz__tbxy += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        zsz__tbxy += '    numba.parfors.parfor.init_prange()\n'
        zsz__tbxy += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            zsz__tbxy += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            zsz__tbxy += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        zsz__tbxy += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        zsz__tbxy += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        zsz__tbxy += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        zsz__tbxy += '            continue\n'
        zsz__tbxy += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            zsz__tbxy += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                zsz__tbxy += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            zsz__tbxy += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            busuv__eonx = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            zsz__tbxy += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            zsz__tbxy += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            zsz__tbxy += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(busuv__eonx[field]))
        elif field == 'is_leap_year':
            zsz__tbxy += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            zsz__tbxy += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)\n'
                )
        elif field in ('daysinmonth', 'days_in_month'):
            busuv__eonx = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            zsz__tbxy += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            zsz__tbxy += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            zsz__tbxy += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(busuv__eonx[field]))
        else:
            zsz__tbxy += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            zsz__tbxy += '        out_arr[i] = ts.' + field + '\n'
        zsz__tbxy += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        tez__fbgo = {}
        exec(zsz__tbxy, {'bodo': bodo, 'numba': numba, 'np': np}, tez__fbgo)
        impl = tez__fbgo['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        ainwq__zsbtu = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(ainwq__zsbtu)


_install_date_fields()


def create_date_method_overload(method):
    ucak__zmlcc = method in ['day_name', 'month_name']
    if ucak__zmlcc:
        zsz__tbxy = 'def overload_method(S_dt, locale=None):\n'
        zsz__tbxy += '    unsupported_args = dict(locale=locale)\n'
        zsz__tbxy += '    arg_defaults = dict(locale=None)\n'
        zsz__tbxy += '    bodo.utils.typing.check_unsupported_args(\n'
        zsz__tbxy += f"        'Series.dt.{method}',\n"
        zsz__tbxy += '        unsupported_args,\n'
        zsz__tbxy += '        arg_defaults,\n'
        zsz__tbxy += "        package_name='pandas',\n"
        zsz__tbxy += "        module_name='Series',\n"
        zsz__tbxy += '    )\n'
    else:
        zsz__tbxy = 'def overload_method(S_dt):\n'
        zsz__tbxy += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    zsz__tbxy += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    zsz__tbxy += '        return\n'
    if ucak__zmlcc:
        zsz__tbxy += '    def impl(S_dt, locale=None):\n'
    else:
        zsz__tbxy += '    def impl(S_dt):\n'
    zsz__tbxy += '        S = S_dt._obj\n'
    zsz__tbxy += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    zsz__tbxy += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    zsz__tbxy += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    zsz__tbxy += '        numba.parfors.parfor.init_prange()\n'
    zsz__tbxy += '        n = len(arr)\n'
    if ucak__zmlcc:
        zsz__tbxy += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        zsz__tbxy += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    zsz__tbxy += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    zsz__tbxy += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    zsz__tbxy += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    zsz__tbxy += '                continue\n'
    zsz__tbxy += '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n'
    zsz__tbxy += f'            method_val = ts.{method}()\n'
    if ucak__zmlcc:
        zsz__tbxy += '            out_arr[i] = method_val\n'
    else:
        zsz__tbxy += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    zsz__tbxy += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    zsz__tbxy += '    return impl\n'
    tez__fbgo = {}
    exec(zsz__tbxy, {'bodo': bodo, 'numba': numba, 'np': np}, tez__fbgo)
    overload_method = tez__fbgo['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        ainwq__zsbtu = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            ainwq__zsbtu)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        xzj__cvom = S_dt._obj
        qgcg__xyukc = bodo.hiframes.pd_series_ext.get_series_data(xzj__cvom)
        lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(xzj__cvom)
        alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(xzj__cvom)
        numba.parfors.parfor.init_prange()
        raj__qbtj = len(qgcg__xyukc)
        lmsy__owor = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            raj__qbtj)
        for ivpf__frae in numba.parfors.parfor.internal_prange(raj__qbtj):
            kxs__tbkt = qgcg__xyukc[ivpf__frae]
            xis__zbdf = bodo.utils.conversion.box_if_dt64(kxs__tbkt)
            lmsy__owor[ivpf__frae] = datetime.date(xis__zbdf.year,
                xis__zbdf.month, xis__zbdf.day)
        return bodo.hiframes.pd_series_ext.init_series(lmsy__owor,
            lvmeh__ndw, alsdg__bxfk)
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
            qiaot__nuvb = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            sbxc__fojfv = 'convert_numpy_timedelta64_to_pd_timedelta'
            rqca__crj = 'np.empty(n, np.int64)'
            jhh__hkwcp = attr
        elif attr == 'isocalendar':
            qiaot__nuvb = ['year', 'week', 'day']
            sbxc__fojfv = 'convert_datetime64_to_timestamp'
            rqca__crj = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            jhh__hkwcp = attr + '()'
        zsz__tbxy = 'def impl(S_dt):\n'
        zsz__tbxy += '    S = S_dt._obj\n'
        zsz__tbxy += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        zsz__tbxy += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        zsz__tbxy += '    numba.parfors.parfor.init_prange()\n'
        zsz__tbxy += '    n = len(arr)\n'
        for field in qiaot__nuvb:
            zsz__tbxy += '    {} = {}\n'.format(field, rqca__crj)
        zsz__tbxy += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        zsz__tbxy += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in qiaot__nuvb:
            zsz__tbxy += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        zsz__tbxy += '            continue\n'
        aicjz__qjqj = '(' + '[i], '.join(qiaot__nuvb) + '[i])'
        zsz__tbxy += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(aicjz__qjqj, sbxc__fojfv, jhh__hkwcp))
        hovjp__jen = '(' + ', '.join(qiaot__nuvb) + ')'
        zsz__tbxy += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(hovjp__jen))
        tez__fbgo = {}
        exec(zsz__tbxy, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(qiaot__nuvb))}, tez__fbgo)
        impl = tez__fbgo['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    kaig__hproj = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, iehrm__qfmvn in kaig__hproj:
        ainwq__zsbtu = create_series_dt_df_output_overload(attr)
        iehrm__qfmvn(SeriesDatetimePropertiesType, attr, inline='always')(
            ainwq__zsbtu)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        zsz__tbxy = 'def impl(S_dt):\n'
        zsz__tbxy += '    S = S_dt._obj\n'
        zsz__tbxy += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        zsz__tbxy += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        zsz__tbxy += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        zsz__tbxy += '    numba.parfors.parfor.init_prange()\n'
        zsz__tbxy += '    n = len(A)\n'
        zsz__tbxy += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        zsz__tbxy += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        zsz__tbxy += '        if bodo.libs.array_kernels.isna(A, i):\n'
        zsz__tbxy += '            bodo.libs.array_kernels.setna(B, i)\n'
        zsz__tbxy += '            continue\n'
        zsz__tbxy += (
            '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
            )
        if field == 'nanoseconds':
            zsz__tbxy += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            zsz__tbxy += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            zsz__tbxy += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            zsz__tbxy += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        zsz__tbxy += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        tez__fbgo = {}
        exec(zsz__tbxy, {'numba': numba, 'np': np, 'bodo': bodo}, tez__fbgo)
        impl = tez__fbgo['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        zsz__tbxy = 'def impl(S_dt):\n'
        zsz__tbxy += '    S = S_dt._obj\n'
        zsz__tbxy += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        zsz__tbxy += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        zsz__tbxy += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        zsz__tbxy += '    numba.parfors.parfor.init_prange()\n'
        zsz__tbxy += '    n = len(A)\n'
        if method == 'total_seconds':
            zsz__tbxy += '    B = np.empty(n, np.float64)\n'
        else:
            zsz__tbxy += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        zsz__tbxy += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        zsz__tbxy += '        if bodo.libs.array_kernels.isna(A, i):\n'
        zsz__tbxy += '            bodo.libs.array_kernels.setna(B, i)\n'
        zsz__tbxy += '            continue\n'
        zsz__tbxy += (
            '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
            )
        if method == 'total_seconds':
            zsz__tbxy += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            zsz__tbxy += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            zsz__tbxy += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            zsz__tbxy += '    return B\n'
        tez__fbgo = {}
        exec(zsz__tbxy, {'numba': numba, 'np': np, 'bodo': bodo, 'datetime':
            datetime}, tez__fbgo)
        impl = tez__fbgo['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        ainwq__zsbtu = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(ainwq__zsbtu)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        ainwq__zsbtu = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            ainwq__zsbtu)


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
        xzj__cvom = S_dt._obj
        kyhl__usw = bodo.hiframes.pd_series_ext.get_series_data(xzj__cvom)
        lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(xzj__cvom)
        alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(xzj__cvom)
        numba.parfors.parfor.init_prange()
        raj__qbtj = len(kyhl__usw)
        tdqii__fiugr = bodo.libs.str_arr_ext.pre_alloc_string_array(raj__qbtj,
            -1)
        for pzwgu__hmjru in numba.parfors.parfor.internal_prange(raj__qbtj):
            if bodo.libs.array_kernels.isna(kyhl__usw, pzwgu__hmjru):
                bodo.libs.array_kernels.setna(tdqii__fiugr, pzwgu__hmjru)
                continue
            tdqii__fiugr[pzwgu__hmjru] = bodo.utils.conversion.box_if_dt64(
                kyhl__usw[pzwgu__hmjru]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(tdqii__fiugr,
            lvmeh__ndw, alsdg__bxfk)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        xzj__cvom = S_dt._obj
        pgozv__jizm = get_series_data(xzj__cvom).tz_convert(tz)
        lvmeh__ndw = get_series_index(xzj__cvom)
        alsdg__bxfk = get_series_name(xzj__cvom)
        return init_series(pgozv__jizm, lvmeh__ndw, alsdg__bxfk)
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
        tnnzb__alipl = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        rfmuk__wvoxf = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', tnnzb__alipl,
            rfmuk__wvoxf, package_name='pandas', module_name='Series')
        zsz__tbxy = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        zsz__tbxy += '    S = S_dt._obj\n'
        zsz__tbxy += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        zsz__tbxy += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        zsz__tbxy += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        zsz__tbxy += '    numba.parfors.parfor.init_prange()\n'
        zsz__tbxy += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            zsz__tbxy += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            zsz__tbxy += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        zsz__tbxy += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        zsz__tbxy += '        if bodo.libs.array_kernels.isna(A, i):\n'
        zsz__tbxy += '            bodo.libs.array_kernels.setna(B, i)\n'
        zsz__tbxy += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            bllok__msdqn = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            zvruf__qurn = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            bllok__msdqn = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            zvruf__qurn = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        zsz__tbxy += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            zvruf__qurn, bllok__msdqn, method)
        zsz__tbxy += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        tez__fbgo = {}
        exec(zsz__tbxy, {'numba': numba, 'np': np, 'bodo': bodo}, tez__fbgo)
        impl = tez__fbgo['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    gdk__cbhnm = ['ceil', 'floor', 'round']
    for method in gdk__cbhnm:
        ainwq__zsbtu = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            ainwq__zsbtu)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                svn__eyxj = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                zsw__uykn = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    svn__eyxj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                jwpv__zzjvx = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                koauz__ugeoz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    jwpv__zzjvx)
                raj__qbtj = len(zsw__uykn)
                xzj__cvom = np.empty(raj__qbtj, timedelta64_dtype)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    czl__yao = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        zsw__uykn[ivpf__frae])
                    xmu__btet = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        koauz__ugeoz[ivpf__frae])
                    if czl__yao == ekcli__pkvp or xmu__btet == ekcli__pkvp:
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(czl__yao, xmu__btet)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                koauz__ugeoz = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                raj__qbtj = len(qgcg__xyukc)
                xzj__cvom = np.empty(raj__qbtj, dt64_dtype)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    cwa__hcd = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qgcg__xyukc[ivpf__frae])
                    mfcsw__qfhww = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(koauz__ugeoz[ivpf__frae]))
                    if cwa__hcd == ekcli__pkvp or mfcsw__qfhww == ekcli__pkvp:
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(cwa__hcd, mfcsw__qfhww)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                koauz__ugeoz = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                raj__qbtj = len(qgcg__xyukc)
                xzj__cvom = np.empty(raj__qbtj, dt64_dtype)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    cwa__hcd = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qgcg__xyukc[ivpf__frae])
                    mfcsw__qfhww = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(koauz__ugeoz[ivpf__frae]))
                    if cwa__hcd == ekcli__pkvp or mfcsw__qfhww == ekcli__pkvp:
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(cwa__hcd, mfcsw__qfhww)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                raj__qbtj = len(qgcg__xyukc)
                xzj__cvom = np.empty(raj__qbtj, timedelta64_dtype)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                lynzf__bqnwr = rhs.value
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    cwa__hcd = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qgcg__xyukc[ivpf__frae])
                    if cwa__hcd == ekcli__pkvp or lynzf__bqnwr == ekcli__pkvp:
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(cwa__hcd, lynzf__bqnwr)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                raj__qbtj = len(qgcg__xyukc)
                xzj__cvom = np.empty(raj__qbtj, timedelta64_dtype)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                lynzf__bqnwr = lhs.value
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    cwa__hcd = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qgcg__xyukc[ivpf__frae])
                    if lynzf__bqnwr == ekcli__pkvp or cwa__hcd == ekcli__pkvp:
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(lynzf__bqnwr, cwa__hcd)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                raj__qbtj = len(qgcg__xyukc)
                xzj__cvom = np.empty(raj__qbtj, dt64_dtype)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                ppd__ejvwb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                mfcsw__qfhww = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ppd__ejvwb))
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    cwa__hcd = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qgcg__xyukc[ivpf__frae])
                    if cwa__hcd == ekcli__pkvp or mfcsw__qfhww == ekcli__pkvp:
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(cwa__hcd, mfcsw__qfhww)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                raj__qbtj = len(qgcg__xyukc)
                xzj__cvom = np.empty(raj__qbtj, dt64_dtype)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                ppd__ejvwb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                mfcsw__qfhww = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ppd__ejvwb))
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    cwa__hcd = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qgcg__xyukc[ivpf__frae])
                    if cwa__hcd == ekcli__pkvp or mfcsw__qfhww == ekcli__pkvp:
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(cwa__hcd, mfcsw__qfhww)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                raj__qbtj = len(qgcg__xyukc)
                xzj__cvom = np.empty(raj__qbtj, timedelta64_dtype)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                hsx__xvw = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                cwa__hcd = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    hsx__xvw)
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    hzbew__cxior = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(qgcg__xyukc[ivpf__frae]))
                    if hzbew__cxior == ekcli__pkvp or cwa__hcd == ekcli__pkvp:
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(hzbew__cxior, cwa__hcd)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                raj__qbtj = len(qgcg__xyukc)
                xzj__cvom = np.empty(raj__qbtj, timedelta64_dtype)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                hsx__xvw = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                cwa__hcd = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    hsx__xvw)
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    hzbew__cxior = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(qgcg__xyukc[ivpf__frae]))
                    if cwa__hcd == ekcli__pkvp or hzbew__cxior == ekcli__pkvp:
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(cwa__hcd, hzbew__cxior)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            kpi__wiae = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qgcg__xyukc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                raj__qbtj = len(qgcg__xyukc)
                xzj__cvom = np.empty(raj__qbtj, timedelta64_dtype)
                ekcli__pkvp = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(kpi__wiae))
                ppd__ejvwb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                mfcsw__qfhww = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ppd__ejvwb))
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    zoddj__zxn = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(qgcg__xyukc[ivpf__frae]))
                    if (mfcsw__qfhww == ekcli__pkvp or zoddj__zxn ==
                        ekcli__pkvp):
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(zoddj__zxn, mfcsw__qfhww)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            kpi__wiae = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qgcg__xyukc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                raj__qbtj = len(qgcg__xyukc)
                xzj__cvom = np.empty(raj__qbtj, timedelta64_dtype)
                ekcli__pkvp = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(kpi__wiae))
                ppd__ejvwb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                mfcsw__qfhww = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(ppd__ejvwb))
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    zoddj__zxn = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(qgcg__xyukc[ivpf__frae]))
                    if (mfcsw__qfhww == ekcli__pkvp or zoddj__zxn ==
                        ekcli__pkvp):
                        quk__qrotl = ekcli__pkvp
                    else:
                        quk__qrotl = op(mfcsw__qfhww, zoddj__zxn)
                    xzj__cvom[ivpf__frae
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        quk__qrotl)
                return bodo.hiframes.pd_series_ext.init_series(xzj__cvom,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            sblyt__ify = True
        else:
            sblyt__ify = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            kpi__wiae = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qgcg__xyukc = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                raj__qbtj = len(qgcg__xyukc)
                lmsy__owor = bodo.libs.bool_arr_ext.alloc_bool_array(raj__qbtj)
                ekcli__pkvp = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(kpi__wiae))
                cncx__vtyrz = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                uznyq__gzwv = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(cncx__vtyrz))
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    stjq__gvcu = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(qgcg__xyukc[ivpf__frae]))
                    if stjq__gvcu == ekcli__pkvp or uznyq__gzwv == ekcli__pkvp:
                        quk__qrotl = sblyt__ify
                    else:
                        quk__qrotl = op(stjq__gvcu, uznyq__gzwv)
                    lmsy__owor[ivpf__frae] = quk__qrotl
                return bodo.hiframes.pd_series_ext.init_series(lmsy__owor,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            kpi__wiae = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qgcg__xyukc = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                raj__qbtj = len(qgcg__xyukc)
                lmsy__owor = bodo.libs.bool_arr_ext.alloc_bool_array(raj__qbtj)
                ekcli__pkvp = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(kpi__wiae))
                cjsdi__hnwj = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                stjq__gvcu = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(cjsdi__hnwj))
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    uznyq__gzwv = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(qgcg__xyukc[ivpf__frae]))
                    if stjq__gvcu == ekcli__pkvp or uznyq__gzwv == ekcli__pkvp:
                        quk__qrotl = sblyt__ify
                    else:
                        quk__qrotl = op(stjq__gvcu, uznyq__gzwv)
                    lmsy__owor[ivpf__frae] = quk__qrotl
                return bodo.hiframes.pd_series_ext.init_series(lmsy__owor,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                raj__qbtj = len(qgcg__xyukc)
                lmsy__owor = bodo.libs.bool_arr_ext.alloc_bool_array(raj__qbtj)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    stjq__gvcu = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(qgcg__xyukc[ivpf__frae]))
                    if stjq__gvcu == ekcli__pkvp or rhs.value == ekcli__pkvp:
                        quk__qrotl = sblyt__ify
                    else:
                        quk__qrotl = op(stjq__gvcu, rhs.value)
                    lmsy__owor[ivpf__frae] = quk__qrotl
                return bodo.hiframes.pd_series_ext.init_series(lmsy__owor,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                raj__qbtj = len(qgcg__xyukc)
                lmsy__owor = bodo.libs.bool_arr_ext.alloc_bool_array(raj__qbtj)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    uznyq__gzwv = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(qgcg__xyukc[ivpf__frae]))
                    if uznyq__gzwv == ekcli__pkvp or lhs.value == ekcli__pkvp:
                        quk__qrotl = sblyt__ify
                    else:
                        quk__qrotl = op(lhs.value, uznyq__gzwv)
                    lmsy__owor[ivpf__frae] = quk__qrotl
                return bodo.hiframes.pd_series_ext.init_series(lmsy__owor,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                raj__qbtj = len(qgcg__xyukc)
                lmsy__owor = bodo.libs.bool_arr_ext.alloc_bool_array(raj__qbtj)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                nyr__gzr = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                zsxj__cnpig = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    nyr__gzr)
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    stjq__gvcu = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(qgcg__xyukc[ivpf__frae]))
                    if stjq__gvcu == ekcli__pkvp or zsxj__cnpig == ekcli__pkvp:
                        quk__qrotl = sblyt__ify
                    else:
                        quk__qrotl = op(stjq__gvcu, zsxj__cnpig)
                    lmsy__owor[ivpf__frae] = quk__qrotl
                return bodo.hiframes.pd_series_ext.init_series(lmsy__owor,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            kpi__wiae = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                yok__zfczj = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                qgcg__xyukc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    yok__zfczj)
                lvmeh__ndw = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                alsdg__bxfk = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                raj__qbtj = len(qgcg__xyukc)
                lmsy__owor = bodo.libs.bool_arr_ext.alloc_bool_array(raj__qbtj)
                ekcli__pkvp = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    kpi__wiae)
                nyr__gzr = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                zsxj__cnpig = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    nyr__gzr)
                for ivpf__frae in numba.parfors.parfor.internal_prange(
                    raj__qbtj):
                    hsx__xvw = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        qgcg__xyukc[ivpf__frae])
                    if hsx__xvw == ekcli__pkvp or zsxj__cnpig == ekcli__pkvp:
                        quk__qrotl = sblyt__ify
                    else:
                        quk__qrotl = op(zsxj__cnpig, hsx__xvw)
                    lmsy__owor[ivpf__frae] = quk__qrotl
                return bodo.hiframes.pd_series_ext.init_series(lmsy__owor,
                    lvmeh__ndw, alsdg__bxfk)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for qmwzy__zinn in series_dt_unsupported_attrs:
        hjsvk__pwdx = 'Series.dt.' + qmwzy__zinn
        overload_attribute(SeriesDatetimePropertiesType, qmwzy__zinn)(
            create_unsupported_overload(hjsvk__pwdx))
    for mkzty__dqqni in series_dt_unsupported_methods:
        hjsvk__pwdx = 'Series.dt.' + mkzty__dqqni
        overload_method(SeriesDatetimePropertiesType, mkzty__dqqni,
            no_unliteral=True)(create_unsupported_overload(hjsvk__pwdx))


_install_series_dt_unsupported()
