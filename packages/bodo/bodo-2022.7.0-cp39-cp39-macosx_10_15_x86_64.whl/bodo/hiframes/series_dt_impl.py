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
        ayd__xqf = 'SeriesDatetimePropertiesType({})'.format(stype)
        super(SeriesDatetimePropertiesType, self).__init__(ayd__xqf)


@register_model(SeriesDatetimePropertiesType)
class SeriesDtModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ein__goh = [('obj', fe_type.stype)]
        super(SeriesDtModel, self).__init__(dmm, fe_type, ein__goh)


make_attribute_wrapper(SeriesDatetimePropertiesType, 'obj', '_obj')


@intrinsic
def init_series_dt_properties(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        ildx__fshnh, = args
        wkhi__eginf = signature.return_type
        edkwn__ale = cgutils.create_struct_proxy(wkhi__eginf)(context, builder)
        edkwn__ale.obj = ildx__fshnh
        context.nrt.incref(builder, signature.args[0], ildx__fshnh)
        return edkwn__ale._getvalue()
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
        rbz__sqv = 'def impl(S_dt):\n'
        rbz__sqv += '    S = S_dt._obj\n'
        rbz__sqv += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        rbz__sqv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        rbz__sqv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        rbz__sqv += '    numba.parfors.parfor.init_prange()\n'
        rbz__sqv += '    n = len(arr)\n'
        if field in ('is_leap_year', 'is_month_start', 'is_month_end',
            'is_quarter_start', 'is_quarter_end', 'is_year_start',
            'is_year_end'):
            rbz__sqv += '    out_arr = np.empty(n, np.bool_)\n'
        else:
            rbz__sqv += (
                '    out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n'
                )
        rbz__sqv += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        rbz__sqv += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        rbz__sqv += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
        rbz__sqv += '            continue\n'
        rbz__sqv += (
            '        dt64 = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arr[i])\n'
            )
        if field in ('year', 'month', 'day'):
            rbz__sqv += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            if field in ('month', 'day'):
                rbz__sqv += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            rbz__sqv += '        out_arr[i] = {}\n'.format(field)
        elif field in ('dayofyear', 'day_of_year', 'dayofweek',
            'day_of_week', 'weekday'):
            ziiw__oxs = {'dayofyear': 'get_day_of_year', 'day_of_year':
                'get_day_of_year', 'dayofweek': 'get_day_of_week',
                'day_of_week': 'get_day_of_week', 'weekday': 'get_day_of_week'}
            rbz__sqv += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            rbz__sqv += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            rbz__sqv += (
                """        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month, day)
"""
                .format(ziiw__oxs[field]))
        elif field == 'is_leap_year':
            rbz__sqv += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            rbz__sqv += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.is_leap_year(year)\n'
                )
        elif field in ('daysinmonth', 'days_in_month'):
            ziiw__oxs = {'days_in_month': 'get_days_in_month',
                'daysinmonth': 'get_days_in_month'}
            rbz__sqv += """        dt, year, days = bodo.hiframes.pd_timestamp_ext.extract_year_days(dt64)
"""
            rbz__sqv += """        month, day = bodo.hiframes.pd_timestamp_ext.get_month_day(year, days)
"""
            rbz__sqv += (
                '        out_arr[i] = bodo.hiframes.pd_timestamp_ext.{}(year, month)\n'
                .format(ziiw__oxs[field]))
        else:
            rbz__sqv += """        ts = bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp(dt64)
"""
            rbz__sqv += '        out_arr[i] = ts.' + field + '\n'
        rbz__sqv += (
            '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        hqlju__ppb = {}
        exec(rbz__sqv, {'bodo': bodo, 'numba': numba, 'np': np}, hqlju__ppb)
        impl = hqlju__ppb['impl']
        return impl
    return overload_field


def _install_date_fields():
    for field in bodo.hiframes.pd_timestamp_ext.date_fields:
        qtw__kjxfg = create_date_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(qtw__kjxfg)


_install_date_fields()


def create_date_method_overload(method):
    ahl__nmav = method in ['day_name', 'month_name']
    if ahl__nmav:
        rbz__sqv = 'def overload_method(S_dt, locale=None):\n'
        rbz__sqv += '    unsupported_args = dict(locale=locale)\n'
        rbz__sqv += '    arg_defaults = dict(locale=None)\n'
        rbz__sqv += '    bodo.utils.typing.check_unsupported_args(\n'
        rbz__sqv += f"        'Series.dt.{method}',\n"
        rbz__sqv += '        unsupported_args,\n'
        rbz__sqv += '        arg_defaults,\n'
        rbz__sqv += "        package_name='pandas',\n"
        rbz__sqv += "        module_name='Series',\n"
        rbz__sqv += '    )\n'
    else:
        rbz__sqv = 'def overload_method(S_dt):\n'
        rbz__sqv += f"""    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S_dt, 'Series.dt.{method}()')
"""
    rbz__sqv += """    if not (S_dt.stype.dtype == bodo.datetime64ns or isinstance(S_dt.stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
"""
    rbz__sqv += '        return\n'
    if ahl__nmav:
        rbz__sqv += '    def impl(S_dt, locale=None):\n'
    else:
        rbz__sqv += '    def impl(S_dt):\n'
    rbz__sqv += '        S = S_dt._obj\n'
    rbz__sqv += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    rbz__sqv += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    rbz__sqv += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    rbz__sqv += '        numba.parfors.parfor.init_prange()\n'
    rbz__sqv += '        n = len(arr)\n'
    if ahl__nmav:
        rbz__sqv += """        out_arr = bodo.utils.utils.alloc_type(n, bodo.string_array_type, (-1,))
"""
    else:
        rbz__sqv += (
            "        out_arr = np.empty(n, np.dtype('datetime64[ns]'))\n")
    rbz__sqv += '        for i in numba.parfors.parfor.internal_prange(n):\n'
    rbz__sqv += '            if bodo.libs.array_kernels.isna(arr, i):\n'
    rbz__sqv += '                bodo.libs.array_kernels.setna(out_arr, i)\n'
    rbz__sqv += '                continue\n'
    rbz__sqv += '            ts = bodo.utils.conversion.box_if_dt64(arr[i])\n'
    rbz__sqv += f'            method_val = ts.{method}()\n'
    if ahl__nmav:
        rbz__sqv += '            out_arr[i] = method_val\n'
    else:
        rbz__sqv += """            out_arr[i] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(method_val.value)
"""
    rbz__sqv += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    rbz__sqv += '    return impl\n'
    hqlju__ppb = {}
    exec(rbz__sqv, {'bodo': bodo, 'numba': numba, 'np': np}, hqlju__ppb)
    overload_method = hqlju__ppb['overload_method']
    return overload_method


def _install_date_methods():
    for method in bodo.hiframes.pd_timestamp_ext.date_methods:
        qtw__kjxfg = create_date_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            qtw__kjxfg)


_install_date_methods()


@overload_attribute(SeriesDatetimePropertiesType, 'date')
def series_dt_date_overload(S_dt):
    if not (S_dt.stype.dtype == types.NPDatetime('ns') or isinstance(S_dt.
        stype.dtype, bodo.libs.pd_datetime_arr_ext.PandasDatetimeTZDtype)):
        return

    def impl(S_dt):
        qnt__uezh = S_dt._obj
        tavu__hwumq = bodo.hiframes.pd_series_ext.get_series_data(qnt__uezh)
        pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(qnt__uezh)
        ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(qnt__uezh)
        numba.parfors.parfor.init_prange()
        ocl__eafix = len(tavu__hwumq)
        cah__yye = bodo.hiframes.datetime_date_ext.alloc_datetime_date_array(
            ocl__eafix)
        for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(ocl__eafix):
            zzxd__wyh = tavu__hwumq[nfcvj__wbwdn]
            zvm__qkqv = bodo.utils.conversion.box_if_dt64(zzxd__wyh)
            cah__yye[nfcvj__wbwdn] = datetime.date(zvm__qkqv.year,
                zvm__qkqv.month, zvm__qkqv.day)
        return bodo.hiframes.pd_series_ext.init_series(cah__yye, pnlrb__xer,
            ayd__xqf)
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
            nwf__rwwt = ['days', 'hours', 'minutes', 'seconds',
                'milliseconds', 'microseconds', 'nanoseconds']
            rzda__xpsl = 'convert_numpy_timedelta64_to_pd_timedelta'
            jqkq__yqu = 'np.empty(n, np.int64)'
            fbmf__muts = attr
        elif attr == 'isocalendar':
            nwf__rwwt = ['year', 'week', 'day']
            rzda__xpsl = 'convert_datetime64_to_timestamp'
            jqkq__yqu = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.uint32)'
            fbmf__muts = attr + '()'
        rbz__sqv = 'def impl(S_dt):\n'
        rbz__sqv += '    S = S_dt._obj\n'
        rbz__sqv += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        rbz__sqv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        rbz__sqv += '    numba.parfors.parfor.init_prange()\n'
        rbz__sqv += '    n = len(arr)\n'
        for field in nwf__rwwt:
            rbz__sqv += '    {} = {}\n'.format(field, jqkq__yqu)
        rbz__sqv += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        rbz__sqv += '        if bodo.libs.array_kernels.isna(arr, i):\n'
        for field in nwf__rwwt:
            rbz__sqv += ('            bodo.libs.array_kernels.setna({}, i)\n'
                .format(field))
        rbz__sqv += '            continue\n'
        ftqlm__gwul = '(' + '[i], '.join(nwf__rwwt) + '[i])'
        rbz__sqv += (
            '        {} = bodo.hiframes.pd_timestamp_ext.{}(arr[i]).{}\n'.
            format(ftqlm__gwul, rzda__xpsl, fbmf__muts))
        xjc__cjda = '(' + ', '.join(nwf__rwwt) + ')'
        rbz__sqv += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe({}, index, __col_name_meta_value_series_dt_df_output)
"""
            .format(xjc__cjda))
        hqlju__ppb = {}
        exec(rbz__sqv, {'bodo': bodo, 'numba': numba, 'np': np,
            '__col_name_meta_value_series_dt_df_output': ColNamesMetaType(
            tuple(nwf__rwwt))}, hqlju__ppb)
        impl = hqlju__ppb['impl']
        return impl
    return series_dt_df_output_overload


def _install_df_output_overload():
    aovz__idh = [('components', overload_attribute), ('isocalendar',
        overload_method)]
    for attr, kbl__zther in aovz__idh:
        qtw__kjxfg = create_series_dt_df_output_overload(attr)
        kbl__zther(SeriesDatetimePropertiesType, attr, inline='always')(
            qtw__kjxfg)


_install_df_output_overload()


def create_timedelta_field_overload(field):

    def overload_field(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        rbz__sqv = 'def impl(S_dt):\n'
        rbz__sqv += '    S = S_dt._obj\n'
        rbz__sqv += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        rbz__sqv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        rbz__sqv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        rbz__sqv += '    numba.parfors.parfor.init_prange()\n'
        rbz__sqv += '    n = len(A)\n'
        rbz__sqv += (
            '    B = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
        rbz__sqv += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        rbz__sqv += '        if bodo.libs.array_kernels.isna(A, i):\n'
        rbz__sqv += '            bodo.libs.array_kernels.setna(B, i)\n'
        rbz__sqv += '            continue\n'
        rbz__sqv += (
            '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
            )
        if field == 'nanoseconds':
            rbz__sqv += '        B[i] = td64 % 1000\n'
        elif field == 'microseconds':
            rbz__sqv += '        B[i] = td64 // 1000 % 1000000\n'
        elif field == 'seconds':
            rbz__sqv += (
                '        B[i] = td64 // (1000 * 1000000) % (60 * 60 * 24)\n')
        elif field == 'days':
            rbz__sqv += (
                '        B[i] = td64 // (1000 * 1000000 * 60 * 60 * 24)\n')
        else:
            assert False, 'invalid timedelta field'
        rbz__sqv += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        hqlju__ppb = {}
        exec(rbz__sqv, {'numba': numba, 'np': np, 'bodo': bodo}, hqlju__ppb)
        impl = hqlju__ppb['impl']
        return impl
    return overload_field


def create_timedelta_method_overload(method):

    def overload_method(S_dt):
        if not S_dt.stype.dtype == types.NPTimedelta('ns'):
            return
        rbz__sqv = 'def impl(S_dt):\n'
        rbz__sqv += '    S = S_dt._obj\n'
        rbz__sqv += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        rbz__sqv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        rbz__sqv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        rbz__sqv += '    numba.parfors.parfor.init_prange()\n'
        rbz__sqv += '    n = len(A)\n'
        if method == 'total_seconds':
            rbz__sqv += '    B = np.empty(n, np.float64)\n'
        else:
            rbz__sqv += """    B = bodo.hiframes.datetime_timedelta_ext.alloc_datetime_timedelta_array(n)
"""
        rbz__sqv += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        rbz__sqv += '        if bodo.libs.array_kernels.isna(A, i):\n'
        rbz__sqv += '            bodo.libs.array_kernels.setna(B, i)\n'
        rbz__sqv += '            continue\n'
        rbz__sqv += (
            '        td64 = bodo.hiframes.pd_timestamp_ext.timedelta64_to_integer(A[i])\n'
            )
        if method == 'total_seconds':
            rbz__sqv += '        B[i] = td64 / (1000.0 * 1000000.0)\n'
        elif method == 'to_pytimedelta':
            rbz__sqv += (
                '        B[i] = datetime.timedelta(microseconds=td64 // 1000)\n'
                )
        else:
            assert False, 'invalid timedelta method'
        if method == 'total_seconds':
            rbz__sqv += (
                '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
                )
        else:
            rbz__sqv += '    return B\n'
        hqlju__ppb = {}
        exec(rbz__sqv, {'numba': numba, 'np': np, 'bodo': bodo, 'datetime':
            datetime}, hqlju__ppb)
        impl = hqlju__ppb['impl']
        return impl
    return overload_method


def _install_S_dt_timedelta_fields():
    for field in bodo.hiframes.pd_timestamp_ext.timedelta_fields:
        qtw__kjxfg = create_timedelta_field_overload(field)
        overload_attribute(SeriesDatetimePropertiesType, field)(qtw__kjxfg)


_install_S_dt_timedelta_fields()


def _install_S_dt_timedelta_methods():
    for method in bodo.hiframes.pd_timestamp_ext.timedelta_methods:
        qtw__kjxfg = create_timedelta_method_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            qtw__kjxfg)


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
        qnt__uezh = S_dt._obj
        fet__qgq = bodo.hiframes.pd_series_ext.get_series_data(qnt__uezh)
        pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(qnt__uezh)
        ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(qnt__uezh)
        numba.parfors.parfor.init_prange()
        ocl__eafix = len(fet__qgq)
        mozw__fxy = bodo.libs.str_arr_ext.pre_alloc_string_array(ocl__eafix, -1
            )
        for dwymv__algas in numba.parfors.parfor.internal_prange(ocl__eafix):
            if bodo.libs.array_kernels.isna(fet__qgq, dwymv__algas):
                bodo.libs.array_kernels.setna(mozw__fxy, dwymv__algas)
                continue
            mozw__fxy[dwymv__algas] = bodo.utils.conversion.box_if_dt64(
                fet__qgq[dwymv__algas]).strftime(date_format)
        return bodo.hiframes.pd_series_ext.init_series(mozw__fxy,
            pnlrb__xer, ayd__xqf)
    return impl


@overload_method(SeriesDatetimePropertiesType, 'tz_convert', inline=
    'always', no_unliteral=True)
def overload_dt_tz_convert(S_dt, tz):

    def impl(S_dt, tz):
        qnt__uezh = S_dt._obj
        gpklz__fnq = get_series_data(qnt__uezh).tz_convert(tz)
        pnlrb__xer = get_series_index(qnt__uezh)
        ayd__xqf = get_series_name(qnt__uezh)
        return init_series(gpklz__fnq, pnlrb__xer, ayd__xqf)
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
        ymve__azszi = dict(ambiguous=ambiguous, nonexistent=nonexistent)
        utsg__igwce = dict(ambiguous='raise', nonexistent='raise')
        check_unsupported_args(f'Series.dt.{method}', ymve__azszi,
            utsg__igwce, package_name='pandas', module_name='Series')
        rbz__sqv = (
            "def impl(S_dt, freq, ambiguous='raise', nonexistent='raise'):\n")
        rbz__sqv += '    S = S_dt._obj\n'
        rbz__sqv += '    A = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        rbz__sqv += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        rbz__sqv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        rbz__sqv += '    numba.parfors.parfor.init_prange()\n'
        rbz__sqv += '    n = len(A)\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            rbz__sqv += "    B = np.empty(n, np.dtype('timedelta64[ns]'))\n"
        else:
            rbz__sqv += "    B = np.empty(n, np.dtype('datetime64[ns]'))\n"
        rbz__sqv += '    for i in numba.parfors.parfor.internal_prange(n):\n'
        rbz__sqv += '        if bodo.libs.array_kernels.isna(A, i):\n'
        rbz__sqv += '            bodo.libs.array_kernels.setna(B, i)\n'
        rbz__sqv += '            continue\n'
        if S_dt.stype.dtype == types.NPTimedelta('ns'):
            kdjpx__hhjn = (
                'bodo.hiframes.pd_timestamp_ext.convert_numpy_timedelta64_to_pd_timedelta'
                )
            rugsf__enz = (
                'bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64')
        else:
            kdjpx__hhjn = (
                'bodo.hiframes.pd_timestamp_ext.convert_datetime64_to_timestamp'
                )
            rugsf__enz = 'bodo.hiframes.pd_timestamp_ext.integer_to_dt64'
        rbz__sqv += '        B[i] = {}({}(A[i]).{}(freq).value)\n'.format(
            rugsf__enz, kdjpx__hhjn, method)
        rbz__sqv += (
            '    return bodo.hiframes.pd_series_ext.init_series(B, index, name)\n'
            )
        hqlju__ppb = {}
        exec(rbz__sqv, {'numba': numba, 'np': np, 'bodo': bodo}, hqlju__ppb)
        impl = hqlju__ppb['impl']
        return impl
    return freq_overload


def _install_S_dt_timedelta_freq_methods():
    fsqc__pjo = ['ceil', 'floor', 'round']
    for method in fsqc__pjo:
        qtw__kjxfg = create_timedelta_freq_overload(method)
        overload_method(SeriesDatetimePropertiesType, method, inline='always')(
            qtw__kjxfg)


_install_S_dt_timedelta_freq_methods()


def create_bin_op_overload(op):

    def overload_series_dt_binop(lhs, rhs):
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs):
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                hiua__luic = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                whuet__opc = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    hiua__luic)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                zno__kplrx = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                pjwk__hqdzi = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    zno__kplrx)
                ocl__eafix = len(whuet__opc)
                qnt__uezh = np.empty(ocl__eafix, timedelta64_dtype)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    wqpw__qstv = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(whuet__opc[nfcvj__wbwdn]))
                    hitbh__skjq = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(pjwk__hqdzi[nfcvj__wbwdn]))
                    if wqpw__qstv == elw__mom or hitbh__skjq == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(wqpw__qstv, hitbh__skjq)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs):
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                pjwk__hqdzi = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                ocl__eafix = len(tavu__hwumq)
                qnt__uezh = np.empty(ocl__eafix, dt64_dtype)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    agwh__kww = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        tavu__hwumq[nfcvj__wbwdn])
                    qkoyn__pnt = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(pjwk__hqdzi[nfcvj__wbwdn]))
                    if agwh__kww == elw__mom or qkoyn__pnt == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(agwh__kww, qkoyn__pnt)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs):
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                pjwk__hqdzi = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                ocl__eafix = len(tavu__hwumq)
                qnt__uezh = np.empty(ocl__eafix, dt64_dtype)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    agwh__kww = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        tavu__hwumq[nfcvj__wbwdn])
                    qkoyn__pnt = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(pjwk__hqdzi[nfcvj__wbwdn]))
                    if agwh__kww == elw__mom or qkoyn__pnt == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(agwh__kww, qkoyn__pnt)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ocl__eafix = len(tavu__hwumq)
                qnt__uezh = np.empty(ocl__eafix, timedelta64_dtype)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                vln__tnbea = rhs.value
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    agwh__kww = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        tavu__hwumq[nfcvj__wbwdn])
                    if agwh__kww == elw__mom or vln__tnbea == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(agwh__kww, vln__tnbea)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs
            ) and lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ocl__eafix = len(tavu__hwumq)
                qnt__uezh = np.empty(ocl__eafix, timedelta64_dtype)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                vln__tnbea = lhs.value
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    agwh__kww = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        tavu__hwumq[nfcvj__wbwdn])
                    if vln__tnbea == elw__mom or agwh__kww == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(vln__tnbea, agwh__kww)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ocl__eafix = len(tavu__hwumq)
                qnt__uezh = np.empty(ocl__eafix, dt64_dtype)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                kktx__bcw = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                qkoyn__pnt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(kktx__bcw))
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    agwh__kww = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        tavu__hwumq[nfcvj__wbwdn])
                    if agwh__kww == elw__mom or qkoyn__pnt == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(agwh__kww, qkoyn__pnt)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type):
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ocl__eafix = len(tavu__hwumq)
                qnt__uezh = np.empty(ocl__eafix, dt64_dtype)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                kktx__bcw = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                qkoyn__pnt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(kktx__bcw))
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    agwh__kww = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        tavu__hwumq[nfcvj__wbwdn])
                    if agwh__kww == elw__mom or qkoyn__pnt == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(agwh__kww, qkoyn__pnt)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and rhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ocl__eafix = len(tavu__hwumq)
                qnt__uezh = np.empty(ocl__eafix, timedelta64_dtype)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                aeg__oxk = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(rhs))
                agwh__kww = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    aeg__oxk)
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    qfu__bguul = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(tavu__hwumq[nfcvj__wbwdn]))
                    if qfu__bguul == elw__mom or agwh__kww == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(qfu__bguul, agwh__kww)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and lhs ==
            bodo.hiframes.datetime_datetime_ext.datetime_datetime_type):
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ocl__eafix = len(tavu__hwumq)
                qnt__uezh = np.empty(ocl__eafix, timedelta64_dtype)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                aeg__oxk = (bodo.hiframes.pd_timestamp_ext.
                    datetime_datetime_to_dt64(lhs))
                agwh__kww = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    aeg__oxk)
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    qfu__bguul = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(tavu__hwumq[nfcvj__wbwdn]))
                    if agwh__kww == elw__mom or qfu__bguul == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(agwh__kww, qfu__bguul)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tkcu__orbv = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                tavu__hwumq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ocl__eafix = len(tavu__hwumq)
                qnt__uezh = np.empty(ocl__eafix, timedelta64_dtype)
                elw__mom = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tkcu__orbv))
                kktx__bcw = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                qkoyn__pnt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(kktx__bcw))
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    ndoy__bygo = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(tavu__hwumq[nfcvj__wbwdn]))
                    if qkoyn__pnt == elw__mom or ndoy__bygo == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(ndoy__bygo, qkoyn__pnt)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tkcu__orbv = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                tavu__hwumq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ocl__eafix = len(tavu__hwumq)
                qnt__uezh = np.empty(ocl__eafix, timedelta64_dtype)
                elw__mom = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tkcu__orbv))
                kktx__bcw = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                qkoyn__pnt = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(kktx__bcw))
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    ndoy__bygo = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(tavu__hwumq[nfcvj__wbwdn]))
                    if qkoyn__pnt == elw__mom or ndoy__bygo == elw__mom:
                        wklnp__tgb = elw__mom
                    else:
                        wklnp__tgb = op(qkoyn__pnt, ndoy__bygo)
                    qnt__uezh[nfcvj__wbwdn
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                        wklnp__tgb)
                return bodo.hiframes.pd_series_ext.init_series(qnt__uezh,
                    pnlrb__xer, ayd__xqf)
            return impl
        raise BodoError(f'{op} not supported for data types {lhs} and {rhs}.')
    return overload_series_dt_binop


def create_cmp_op_overload(op):

    def overload_series_dt64_cmp(lhs, rhs):
        if op == operator.ne:
            ngjb__nvge = True
        else:
            ngjb__nvge = False
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(lhs) and 
            rhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tkcu__orbv = lhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                tavu__hwumq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ocl__eafix = len(tavu__hwumq)
                cah__yye = bodo.libs.bool_arr_ext.alloc_bool_array(ocl__eafix)
                elw__mom = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tkcu__orbv))
                jer__hqdb = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(rhs))
                gyzbr__suve = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(jer__hqdb))
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    ebn__uqe = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(tavu__hwumq[nfcvj__wbwdn]))
                    if ebn__uqe == elw__mom or gyzbr__suve == elw__mom:
                        wklnp__tgb = ngjb__nvge
                    else:
                        wklnp__tgb = op(ebn__uqe, gyzbr__suve)
                    cah__yye[nfcvj__wbwdn] = wklnp__tgb
                return bodo.hiframes.pd_series_ext.init_series(cah__yye,
                    pnlrb__xer, ayd__xqf)
            return impl
        if (bodo.hiframes.pd_series_ext.is_timedelta64_series_typ(rhs) and 
            lhs == bodo.hiframes.datetime_timedelta_ext.datetime_timedelta_type
            ):
            tkcu__orbv = rhs.dtype('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                tavu__hwumq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ocl__eafix = len(tavu__hwumq)
                cah__yye = bodo.libs.bool_arr_ext.alloc_bool_array(ocl__eafix)
                elw__mom = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(tkcu__orbv))
                gzk__yqqjg = (bodo.hiframes.pd_timestamp_ext.
                    datetime_timedelta_to_timedelta64(lhs))
                ebn__uqe = (bodo.hiframes.pd_timestamp_ext.
                    timedelta64_to_integer(gzk__yqqjg))
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    gyzbr__suve = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(tavu__hwumq[nfcvj__wbwdn]))
                    if ebn__uqe == elw__mom or gyzbr__suve == elw__mom:
                        wklnp__tgb = ngjb__nvge
                    else:
                        wklnp__tgb = op(ebn__uqe, gyzbr__suve)
                    cah__yye[nfcvj__wbwdn] = wklnp__tgb
                return bodo.hiframes.pd_series_ext.init_series(cah__yye,
                    pnlrb__xer, ayd__xqf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs
            ) and rhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ocl__eafix = len(tavu__hwumq)
                cah__yye = bodo.libs.bool_arr_ext.alloc_bool_array(ocl__eafix)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    ebn__uqe = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        tavu__hwumq[nfcvj__wbwdn])
                    if ebn__uqe == elw__mom or rhs.value == elw__mom:
                        wklnp__tgb = ngjb__nvge
                    else:
                        wklnp__tgb = op(ebn__uqe, rhs.value)
                    cah__yye[nfcvj__wbwdn] = wklnp__tgb
                return bodo.hiframes.pd_series_ext.init_series(cah__yye,
                    pnlrb__xer, ayd__xqf)
            return impl
        if (lhs == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type and
            bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs)):
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                numba.parfors.parfor.init_prange()
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ocl__eafix = len(tavu__hwumq)
                cah__yye = bodo.libs.bool_arr_ext.alloc_bool_array(ocl__eafix)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    gyzbr__suve = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(tavu__hwumq[nfcvj__wbwdn]))
                    if gyzbr__suve == elw__mom or lhs.value == elw__mom:
                        wklnp__tgb = ngjb__nvge
                    else:
                        wklnp__tgb = op(lhs.value, gyzbr__suve)
                    cah__yye[nfcvj__wbwdn] = wklnp__tgb
                return bodo.hiframes.pd_series_ext.init_series(cah__yye,
                    pnlrb__xer, ayd__xqf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(lhs) and (rhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(rhs)):
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                ocl__eafix = len(tavu__hwumq)
                cah__yye = bodo.libs.bool_arr_ext.alloc_bool_array(ocl__eafix)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                nkvt__eup = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    rhs)
                yysn__ywy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    nkvt__eup)
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    ebn__uqe = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        tavu__hwumq[nfcvj__wbwdn])
                    if ebn__uqe == elw__mom or yysn__ywy == elw__mom:
                        wklnp__tgb = ngjb__nvge
                    else:
                        wklnp__tgb = op(ebn__uqe, yysn__ywy)
                    cah__yye[nfcvj__wbwdn] = wklnp__tgb
                return bodo.hiframes.pd_series_ext.init_series(cah__yye,
                    pnlrb__xer, ayd__xqf)
            return impl
        if bodo.hiframes.pd_series_ext.is_dt64_series_typ(rhs) and (lhs ==
            bodo.libs.str_ext.string_type or bodo.utils.typing.
            is_overload_constant_str(lhs)):
            tkcu__orbv = bodo.datetime64ns('NaT')

            def impl(lhs, rhs):
                aeoki__pgq = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                tavu__hwumq = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                    aeoki__pgq)
                pnlrb__xer = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                ayd__xqf = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                numba.parfors.parfor.init_prange()
                ocl__eafix = len(tavu__hwumq)
                cah__yye = bodo.libs.bool_arr_ext.alloc_bool_array(ocl__eafix)
                elw__mom = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    tkcu__orbv)
                nkvt__eup = bodo.hiframes.pd_timestamp_ext.parse_datetime_str(
                    lhs)
                yysn__ywy = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                    nkvt__eup)
                for nfcvj__wbwdn in numba.parfors.parfor.internal_prange(
                    ocl__eafix):
                    aeg__oxk = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        tavu__hwumq[nfcvj__wbwdn])
                    if aeg__oxk == elw__mom or yysn__ywy == elw__mom:
                        wklnp__tgb = ngjb__nvge
                    else:
                        wklnp__tgb = op(yysn__ywy, aeg__oxk)
                    cah__yye[nfcvj__wbwdn] = wklnp__tgb
                return bodo.hiframes.pd_series_ext.init_series(cah__yye,
                    pnlrb__xer, ayd__xqf)
            return impl
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_series_dt64_cmp


series_dt_unsupported_methods = {'to_period', 'to_pydatetime',
    'tz_localize', 'asfreq', 'to_timestamp'}
series_dt_unsupported_attrs = {'time', 'timetz', 'tz', 'freq', 'qyear',
    'start_time', 'end_time'}


def _install_series_dt_unsupported():
    for rmpm__kcq in series_dt_unsupported_attrs:
        nnxav__tqjv = 'Series.dt.' + rmpm__kcq
        overload_attribute(SeriesDatetimePropertiesType, rmpm__kcq)(
            create_unsupported_overload(nnxav__tqjv))
    for tdzlu__iwm in series_dt_unsupported_methods:
        nnxav__tqjv = 'Series.dt.' + tdzlu__iwm
        overload_method(SeriesDatetimePropertiesType, tdzlu__iwm,
            no_unliteral=True)(create_unsupported_overload(nnxav__tqjv))


_install_series_dt_unsupported()
