"""
Implements array kernels that are specific to BodoSQL
"""
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.extending import overload
import bodo
from bodo.utils.typing import get_overload_const_bool, get_overload_const_str, is_overload_bool, is_overload_constant_bool, is_overload_constant_number, is_overload_constant_str, is_overload_int, raise_bodo_error


def rank_sql(arr_tup, method='average', pct=False):
    return


@overload(rank_sql, no_unliteral=True)
def overload_rank_sql(arr_tup, method='average', pct=False):
    if not is_overload_constant_str(method):
        raise_bodo_error(
            "Series.rank(): 'method' argument must be a constant string")
    method = get_overload_const_str(method)
    if not is_overload_constant_bool(pct):
        raise_bodo_error(
            "Series.rank(): 'pct' argument must be a constant boolean")
    pct = get_overload_const_bool(pct)
    nmwzm__iajit = 'def impl(arr_tup, method="average", pct=False):\n'
    if method == 'first':
        nmwzm__iajit += '  ret = np.arange(1, n + 1, 1, np.float64)\n'
    else:
        nmwzm__iajit += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr_tup[0])\n')
        nmwzm__iajit += '  for arr in arr_tup:\n'
        nmwzm__iajit += (
            '    next_obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        nmwzm__iajit += '    obs = obs | next_obs \n'
        nmwzm__iajit += '  dense = obs.cumsum()\n'
        if method == 'dense':
            nmwzm__iajit += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            nmwzm__iajit += '    dense,\n'
            nmwzm__iajit += '    new_dtype=np.float64,\n'
            nmwzm__iajit += '    copy=True,\n'
            nmwzm__iajit += '    nan_to_str=False,\n'
            nmwzm__iajit += '    from_series=True,\n'
            nmwzm__iajit += '  )\n'
        else:
            nmwzm__iajit += """  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))
"""
            nmwzm__iajit += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                nmwzm__iajit += '  ret = count_float[dense]\n'
            elif method == 'min':
                nmwzm__iajit += '  ret = count_float[dense - 1] + 1\n'
            else:
                nmwzm__iajit += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            nmwzm__iajit += '  div_val = np.max(ret)\n'
        else:
            nmwzm__iajit += '  div_val = arr.size\n'
        nmwzm__iajit += '  for i in range(len(ret)):\n'
        nmwzm__iajit += '    ret[i] = ret[i] / div_val\n'
    nmwzm__iajit += '  return ret\n'
    dtaq__idvh = {}
    exec(nmwzm__iajit, {'np': np, 'pd': pd, 'bodo': bodo}, dtaq__idvh)
    return dtaq__idvh['impl']


broadcasted_fixed_arg_functions = {'cond', 'lpad', 'rpad', 'last_day',
    'dayname', 'monthname', 'weekday', 'yearofweekiso', 'makedate',
    'format', 'left', 'right', 'ord_ascii', 'char', 'repeat', 'reverse',
    'replace', 'space', 'int_to_days', 'second_timestamp', 'day_timestamp',
    'year_timestamp', 'month_diff', 'conv', 'substring', 'substring_index',
    'nullif', 'negate', 'log', 'strcmp', 'instr'}


def gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
    out_dtype, arg_string=None, arg_sources=None, array_override=None):
    wie__ufld = [bodo.utils.utils.is_array_typ(vcg__vpg, True) for vcg__vpg in
        arg_types]
    aews__ctajc = not any(wie__ufld)
    bar__qwlm = any([propagate_null[i] for i in range(len(arg_types)) if 
        arg_types[i] == bodo.none])
    uxdr__quo = scalar_text.splitlines()[0]
    qqnrd__wwp = len(uxdr__quo) - len(uxdr__quo.lstrip())
    if arg_string is None:
        arg_string = ', '.join(arg_names)
    nmwzm__iajit = f'def impl({arg_string}):\n'
    if arg_sources is not None:
        for kpe__hcbw, xkox__rgs in arg_sources.items():
            nmwzm__iajit += f'   {kpe__hcbw} = {xkox__rgs}\n'
    if aews__ctajc and array_override == None:
        if bar__qwlm:
            nmwzm__iajit += '   return None'
        else:
            for i in range(len(arg_names)):
                nmwzm__iajit += f'   arg{i} = {arg_names[i]}\n'
            for epeg__lwkgc in scalar_text.splitlines():
                nmwzm__iajit += ' ' * 3 + epeg__lwkgc[qqnrd__wwp:].replace(
                    'res[i] =', 'answer =').replace(
                    'bodo.libs.array_kernels.setna(res, i)', 'return None'
                    ) + '\n'
            nmwzm__iajit += '   return answer'
    else:
        if array_override != None:
            svib__rmehz = True
            oya__mnnt = f'len({array_override})'
        svib__rmehz = False
        for i in range(len(arg_names)):
            if wie__ufld[i]:
                if not svib__rmehz:
                    oya__mnnt = f'len({arg_names[i]})'
                    svib__rmehz = True
                if not bodo.utils.utils.is_array_typ(arg_types[i], False):
                    nmwzm__iajit += f"""   {arg_names[i]} = bodo.hiframes.pd_series_ext.get_series_data({arg_names[i]})
"""
        nmwzm__iajit += f'   n = {oya__mnnt}\n'
        nmwzm__iajit += (
            f'   res = bodo.utils.utils.alloc_type(n, out_dtype, (-1,))\n')
        nmwzm__iajit += '   numba.parfors.parfor.init_prange()\n'
        nmwzm__iajit += (
            '   for i in numba.parfors.parfor.internal_prange(n):\n')
        if bar__qwlm:
            nmwzm__iajit += f'      bodo.libs.array_kernels.setna(res, i)\n'
        else:
            for i in range(len(arg_names)):
                if wie__ufld[i]:
                    if propagate_null[i]:
                        nmwzm__iajit += f"""      if bodo.libs.array_kernels.isna({arg_names[i]}, i):
"""
                        nmwzm__iajit += (
                            '         bodo.libs.array_kernels.setna(res, i)\n')
                        nmwzm__iajit += '         continue\n'
            for i in range(len(arg_names)):
                if wie__ufld[i]:
                    nmwzm__iajit += f'      arg{i} = {arg_names[i]}[i]\n'
                else:
                    nmwzm__iajit += f'      arg{i} = {arg_names[i]}\n'
            for epeg__lwkgc in scalar_text.splitlines():
                nmwzm__iajit += ' ' * 6 + epeg__lwkgc[qqnrd__wwp:] + '\n'
        nmwzm__iajit += (
            '   return bodo.hiframes.pd_series_ext.init_series(res, bodo.hiframes.pd_index_ext.init_range_index(0, n, 1), None)'
            )
    dtaq__idvh = {}
    exec(nmwzm__iajit, {'bodo': bodo, 'numba': numba, 'np': np, 'out_dtype':
        out_dtype, 'pd': pd}, dtaq__idvh)
    impl = dtaq__idvh['impl']
    return impl


def unopt_argument(func_name, arg_names, i, container_length=None):
    if container_length != None:
        lafip__ude = [(f'{arg_names[0]}{[spn__cyauh]}' if spn__cyauh != i else
            'None') for spn__cyauh in range(container_length)]
        ola__xcx = [(f'{arg_names[0]}{[spn__cyauh]}' if spn__cyauh != i else
            f'bodo.utils.indexing.unoptional({arg_names[0]}[{spn__cyauh}])'
            ) for spn__cyauh in range(container_length)]
        nmwzm__iajit = f"def impl({', '.join(arg_names)}):\n"
        nmwzm__iajit += f'   if {arg_names[0]}[{i}] is None:\n'
        nmwzm__iajit += (
            f"      return {func_name}(({', '.join(lafip__ude)}))\n")
        nmwzm__iajit += f'   else:\n'
        nmwzm__iajit += f"      return {func_name}(({', '.join(ola__xcx)}))"
    else:
        lafip__ude = [(arg_names[spn__cyauh] if spn__cyauh != i else 'None'
            ) for spn__cyauh in range(len(arg_names))]
        ola__xcx = [(arg_names[spn__cyauh] if spn__cyauh != i else
            f'bodo.utils.indexing.unoptional({arg_names[spn__cyauh]})') for
            spn__cyauh in range(len(arg_names))]
        nmwzm__iajit = f"def impl({', '.join(arg_names)}):\n"
        nmwzm__iajit += f'   if {arg_names[i]} is None:\n'
        nmwzm__iajit += f"      return {func_name}({', '.join(lafip__ude)})\n"
        nmwzm__iajit += f'   else:\n'
        nmwzm__iajit += f"      return {func_name}({', '.join(ola__xcx)})"
    dtaq__idvh = {}
    exec(nmwzm__iajit, {'bodo': bodo, 'numba': numba}, dtaq__idvh)
    impl = dtaq__idvh['impl']
    return impl


def verify_int_arg(arg, f_name, a_name):
    if arg != types.none and not isinstance(arg, types.Integer) and not (bodo
        .utils.utils.is_array_typ(arg, True) and isinstance(arg.dtype,
        types.Integer)) and not is_overload_int(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be an integer, integer column, or null'
            )


def verify_int_float_arg(arg, f_name, a_name):
    if arg != types.none and not isinstance(arg, (types.Integer, types.Float)
        ) and not (bodo.utils.utils.is_array_typ(arg, True) and isinstance(
        arg.dtype, (types.Integer, types.Float))
        ) and not is_overload_constant_number(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a numeric, numeric column, or null'
            )


def verify_string_arg(arg, f_name, a_name):
    if arg not in (types.none, types.unicode_type) and not isinstance(arg,
        types.StringLiteral) and not (bodo.utils.utils.is_array_typ(arg, 
        True) and arg.dtype == types.unicode_type
        ) and not is_overload_constant_str(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a string, string column, or null'
            )


def verify_boolean_arg(arg, f_name, a_name):
    if arg not in (types.none, types.boolean) and not (bodo.utils.utils.
        is_array_typ(arg, True) and arg.dtype == types.boolean
        ) and not is_overload_bool(arg):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a boolean, boolean column, or null'
            )


def verify_datetime_arg(arg, f_name, a_name):
    if arg not in (types.none, bodo.datetime64ns, bodo.pd_timestamp_type,
        bodo.hiframes.datetime_date_ext.DatetimeDateType()) and not (bodo.
        utils.utils.is_array_typ(arg, True) and arg.dtype in (bodo.
        datetime64ns, bodo.hiframes.datetime_date_ext.DatetimeDateType())):
        raise_bodo_error(
            f'{f_name} {a_name} argument must be a datetime, datetime column, or null'
            )


def get_common_broadcasted_type(arg_types, func_name):
    ujkxe__vpu = []
    for i in range(len(arg_types)):
        if bodo.utils.utils.is_array_typ(arg_types[i], False):
            ujkxe__vpu.append(arg_types[i])
        elif bodo.utils.utils.is_array_typ(arg_types[i], True):
            ujkxe__vpu.append(arg_types[i].data)
        else:
            ujkxe__vpu.append(arg_types[i])
    if len(ujkxe__vpu) == 0:
        return bodo.none
    elif len(ujkxe__vpu) == 1:
        if bodo.utils.utils.is_array_typ(ujkxe__vpu[0]):
            return bodo.utils.typing.to_nullable_type(ujkxe__vpu[0])
        elif ujkxe__vpu[0] == bodo.none:
            return bodo.none
        else:
            return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
                dtype_to_array_type(ujkxe__vpu[0]))
    else:
        vhb__fbr = []
        for i in range(len(arg_types)):
            if bodo.utils.utils.is_array_typ(arg_types[i]):
                vhb__fbr.append(ujkxe__vpu[i].dtype)
            elif ujkxe__vpu[i] == bodo.none:
                pass
            else:
                vhb__fbr.append(ujkxe__vpu[i])
        if len(vhb__fbr) == 0:
            return bodo.none
        wse__waglm, jae__dlct = bodo.utils.typing.get_common_scalar_dtype(
            vhb__fbr)
        if not jae__dlct:
            raise_bodo_error(
                f'Cannot call {func_name} on columns with different dtypes')
        return bodo.utils.typing.to_nullable_type(bodo.utils.typing.
            dtype_to_array_type(wse__waglm))


@numba.generated_jit(nopython=True)
def last_day(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.last_day_util',
            ['arr'], 0)

    def impl(arr):
        return last_day_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def last_day_util(arr):
    verify_datetime_arg(arr, 'LAST_DAY', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = (
        'res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(arg0) + pd.tseries.offsets.MonthEnd(n=0, normalize=True))'
        )
    out_dtype = np.dtype('datetime64[ns]')
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def dayname(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.dayname_util',
            ['arr'], 0)

    def impl(arr):
        return dayname_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def dayname_util(arr):
    verify_datetime_arg(arr, 'DAYNAME', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = 'res[i] = pd.Timestamp(arg0).day_name()'
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def monthname(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.monthname_util',
            ['arr'], 0)

    def impl(arr):
        return monthname_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def monthname_util(arr):
    verify_datetime_arg(arr, 'MONTHNAME', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = 'res[i] = pd.Timestamp(arg0).month_name()'
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def weekday(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.weekday_util',
            ['arr'], 0)

    def impl(arr):
        return weekday_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def weekday_util(arr):
    verify_datetime_arg(arr, 'WEEKDAY', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = 'dt = pd.Timestamp(arg0)\n'
    scalar_text += (
        'res[i] = bodo.hiframes.pd_timestamp_ext.get_day_of_week(dt.year, dt.month, dt.day)'
        )
    out_dtype = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def yearofweekiso(arr):
    if isinstance(arr, types.optional):
        return unopt_argument(
            'bodo.libs.bodosql_array_kernels.yearofweekiso_util', ['arr'], 0)

    def impl(arr):
        return yearofweekiso_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def yearofweekiso_util(arr):
    verify_datetime_arg(arr, 'YEAROFWEEKISO', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = 'dt = pd.Timestamp(arg0)\n'
    scalar_text += 'res[i] = dt.isocalendar()[0]'
    out_dtype = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def makedate(year, day):
    args = [year, day]
    for i in range(2):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.makedate',
                ['year', 'day'], i)

    def impl(year, day):
        return makedate_util(year, day)
    return impl


@numba.generated_jit(nopython=True)
def makedate_util(year, day):
    verify_int_arg(year, 'MAKEDATE', 'year')
    verify_int_arg(day, 'MAKEDATE', 'day')
    arg_names = ['year', 'day']
    arg_types = [year, day]
    propagate_null = [True] * 2
    scalar_text = (
        'res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(year=arg0, month=1, day=1) + pd.Timedelta(days=arg1-1))'
        )
    out_dtype = np.dtype('datetime64[ns]')
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


def lpad(arr, length, padstr):
    return


def rpad(arr, length, padstr):
    return


def lpad_util(arr, length, padstr):
    return


def rpad_util(arr, length, padstr):
    return


@overload(lpad)
def overload_lpad(arr, length, padstr):
    args = [arr, length, padstr]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.lpad', [
                'arr', 'length', 'padstr'], i)

    def impl(arr, length, padstr):
        return lpad_util(arr, length, padstr)
    return impl


@overload(rpad)
def overload_rpad(arr, length, padstr):
    args = [arr, length, padstr]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.rpad', [
                'arr', 'length', 'padstr'], i)

    def impl(arr, length, padstr):
        return rpad_util(arr, length, padstr)
    return impl


def create_lpad_rpad_util_overload(func_name):

    def overload_lpad_rpad_util(arr, length, pad_string):
        verify_string_arg(arr, func_name, 'arr')
        verify_int_arg(length, func_name, 'length')
        verify_string_arg(pad_string, func_name, f'{func_name.lower()}_string')
        if func_name == 'LPAD':
            djqc__vhz = f'(arg2 * quotient) + arg2[:remainder] + arg0'
        elif func_name == 'RPAD':
            djqc__vhz = f'arg0 + (arg2 * quotient) + arg2[:remainder]'
        arg_names = ['arr', 'length', 'pad_string']
        arg_types = [arr, length, pad_string]
        propagate_null = [True] * 3
        scalar_text = f"""            if arg1 <= 0:
                res[i] =  ''
            elif len(arg2) == 0:
                res[i] = arg0
            elif len(arg0) >= arg1:
                res[i] = arg0[:arg1]
            else:
                quotient = (arg1 - len(arg0)) // len(arg2)
                remainder = (arg1 - len(arg0)) % len(arg2)
                res[i] = {djqc__vhz}"""
        out_dtype = bodo.string_array_type
        return gen_vectorized(arg_names, arg_types, propagate_null,
            scalar_text, out_dtype)
    return overload_lpad_rpad_util


def _install_lpad_rpad_overload():
    for eqjr__pfnfm, func_name in zip((lpad_util, rpad_util), ('LPAD', 'RPAD')
        ):
        mzu__wneql = create_lpad_rpad_util_overload(func_name)
        overload(eqjr__pfnfm)(mzu__wneql)


_install_lpad_rpad_overload()


@numba.generated_jit(nopython=True)
def cond(arr, ifbranch, elsebranch):
    args = [arr, ifbranch, elsebranch]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.cond', [
                'arr', 'ifbranch', 'elsebranch'], i)

    def impl(arr, ifbranch, elsebranch):
        return cond_util(arr, ifbranch, elsebranch)
    return impl


@numba.generated_jit(nopython=True)
def cond_util(arr, ifbranch, elsebranch):
    verify_boolean_arg(arr, 'cond', 'arr')
    if bodo.utils.utils.is_array_typ(arr, True
        ) and ifbranch == bodo.none and elsebranch == bodo.none:
        raise_bodo_error('Both branches of IF() cannot be scalar NULL')
    arg_names = ['arr', 'ifbranch', 'elsebranch']
    arg_types = [arr, ifbranch, elsebranch]
    propagate_null = [False] * 3
    if bodo.utils.utils.is_array_typ(arr, True):
        scalar_text = (
            'if (not bodo.libs.array_kernels.isna(arr, i)) and arg0:\n')
    elif arr != bodo.none:
        scalar_text = 'if arg0:\n'
    else:
        scalar_text = ''
    if arr != bodo.none:
        if bodo.utils.utils.is_array_typ(ifbranch, True):
            scalar_text += '   if bodo.libs.array_kernels.isna(ifbranch, i):\n'
            scalar_text += '      bodo.libs.array_kernels.setna(res, i)\n'
            scalar_text += '   else:\n'
            scalar_text += '      res[i] = arg1\n'
        elif ifbranch == bodo.none:
            scalar_text += '   bodo.libs.array_kernels.setna(res, i)\n'
        else:
            scalar_text += '   res[i] = arg1\n'
        scalar_text += 'else:\n'
    if bodo.utils.utils.is_array_typ(elsebranch, True):
        scalar_text += '   if bodo.libs.array_kernels.isna(elsebranch, i):\n'
        scalar_text += '      bodo.libs.array_kernels.setna(res, i)\n'
        scalar_text += '   else:\n'
        scalar_text += '      res[i] = arg2\n'
    elif elsebranch == bodo.none:
        scalar_text += '   bodo.libs.array_kernels.setna(res, i)\n'
    else:
        scalar_text += '   res[i] = arg2\n'
    out_dtype = get_common_broadcasted_type([ifbranch, elsebranch], 'IF')
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def substring(arr, start, length):
    args = [arr, start, length]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.substring',
                ['arr', 'start', 'length'], i)

    def impl(arr, start, length):
        return substring_util(arr, start, length)
    return impl


@numba.generated_jit(nopython=True)
def substring_util(arr, start, length):
    verify_string_arg(arr, 'SUBSTRING', 'arr')
    verify_int_arg(start, 'SUBSTRING', 'start')
    verify_int_arg(length, 'SUBSTRING', 'length')
    arg_names = ['arr', 'start', 'length']
    arg_types = [arr, start, length]
    propagate_null = [True] * 3
    scalar_text = 'if arg2 <= 0:\n'
    scalar_text += "   res[i] = ''\n"
    scalar_text += 'elif arg1 < 0 and arg1 + arg2 >= 0:\n'
    scalar_text += '   res[i] = arg0[arg1:]\n'
    scalar_text += 'else:\n'
    scalar_text += '   if arg1 > 0: arg1 -= 1\n'
    scalar_text += '   res[i] = arg0[arg1:arg1+arg2]\n'
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def substring_index(arr, delimiter, occurrences):
    args = [arr, delimiter, occurrences]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument(
                'bodo.libs.bodosql_array_kernels.substring_index', ['arr',
                'delimiter', 'occurrences'], i)

    def impl(arr, delimiter, occurrences):
        return substring_index_util(arr, delimiter, occurrences)
    return impl


@numba.generated_jit(nopython=True)
def substring_index_util(arr, delimiter, occurrences):
    verify_string_arg(arr, 'SUBSTRING_INDEX', 'arr')
    verify_string_arg(delimiter, 'SUBSTRING_INDEX', 'delimiter')
    verify_int_arg(occurrences, 'SUBSTRING_INDEX', 'occurrences')
    arg_names = ['arr', 'delimiter', 'occurrences']
    arg_types = [arr, delimiter, occurrences]
    propagate_null = [True] * 3
    scalar_text = "if arg1 == '' or arg2 == 0:\n"
    scalar_text += "   res[i] = ''\n"
    scalar_text += 'elif arg2 >= 0:\n'
    scalar_text += '   res[i] = arg1.join(arg0.split(arg1, arg2+1)[:arg2])\n'
    scalar_text += 'else:\n'
    scalar_text += '   res[i] = arg1.join(arg0.split(arg1)[arg2:])\n'
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


def coalesce(A):
    return


def coalesce_util(A):
    return


@overload(coalesce)
def overload_coalesce(A):
    if not isinstance(A, (types.Tuple, types.UniTuple)):
        raise_bodo_error('Coalesce argument must be a tuple')
    for i in range(len(A)):
        if isinstance(A[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.coalesce',
                ['A'], i, container_length=len(A))

    def impl(A):
        return coalesce_util(A)
    return impl


@overload(coalesce_util, no_unliteral=True)
def overload_coalesce_util(A):
    if len(A) == 0:
        raise_bodo_error('Cannot coalesce 0 columns')
    array_override = None
    bhv__latq = []
    for i in range(len(A)):
        if A[i] == bodo.none:
            bhv__latq.append(i)
        elif not bodo.utils.utils.is_array_typ(A[i]):
            for spn__cyauh in range(i + 1, len(A)):
                bhv__latq.append(spn__cyauh)
                if bodo.utils.utils.is_array_typ(A[spn__cyauh]):
                    array_override = f'A[{spn__cyauh}]'
            break
    arg_names = [f'A{i}' for i in range(len(A)) if i not in bhv__latq]
    arg_types = [A[i] for i in range(len(A)) if i not in bhv__latq]
    propagate_null = [False] * (len(A) - len(bhv__latq))
    scalar_text = ''
    zvcyf__aaw = True
    xohc__cwe = False
    arnzh__ukt = 0
    for i in range(len(A)):
        if i in bhv__latq:
            arnzh__ukt += 1
            continue
        elif bodo.utils.utils.is_array_typ(A[i]):
            cond = 'if' if zvcyf__aaw else 'elif'
            scalar_text += (
                f'{cond} not bodo.libs.array_kernels.isna(A{i}, i):\n')
            scalar_text += f'   res[i] = arg{i - arnzh__ukt}\n'
            zvcyf__aaw = False
        else:
            assert not xohc__cwe, 'should not encounter more than one scalar due to dead column pruning'
            if zvcyf__aaw:
                scalar_text += f'res[i] = arg{i - arnzh__ukt}\n'
            else:
                scalar_text += 'else:\n'
                scalar_text += f'   res[i] = arg{i - arnzh__ukt}\n'
            xohc__cwe = True
            break
    if not xohc__cwe:
        if not zvcyf__aaw:
            scalar_text += 'else:\n'
            scalar_text += '   bodo.libs.array_kernels.setna(res, i)'
        else:
            scalar_text += 'bodo.libs.array_kernels.setna(res, i)'
    arg_string = 'A'
    arg_sources = {f'A{i}': f'A[{i}]' for i in range(len(A)) if i not in
        bhv__latq}
    out_dtype = get_common_broadcasted_type(arg_types, 'COALESCE')
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype, arg_string, arg_sources, array_override)


def left(arr, n_chars):
    return


def right(arr, n_chars):
    return


def left_util(arr, n_chars):
    return


def right_util(arr, n_chars):
    return


@overload(left)
def overload_left(arr, n_chars):
    args = [arr, n_chars]
    for i in range(2):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.left', [
                'arr', 'n_chars'], i)

    def impl(arr, n_chars):
        return left_util(arr, n_chars)
    return impl


@overload(right)
def overload_right(arr, n_chars):
    args = [arr, n_chars]
    for i in range(2):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.right',
                ['arr', 'n_chars'], i)

    def impl(arr, n_chars):
        return right_util(arr, n_chars)
    return impl


def create_left_right_util_overload(func_name):

    def overload_left_right_util(arr, n_chars):
        verify_string_arg(arr, func_name, 'arr')
        verify_int_arg(n_chars, func_name, 'n_chars')
        arg_names = ['arr', 'n_chars']
        arg_types = [arr, n_chars]
        propagate_null = [True] * 2
        scalar_text = 'if arg1 <= 0:\n'
        scalar_text += "   res[i] = ''\n"
        scalar_text += 'else:\n'
        if func_name == 'LEFT':
            scalar_text += '   res[i] = arg0[:arg1]'
        elif func_name == 'RIGHT':
            scalar_text += '   res[i] = arg0[-arg1:]'
        out_dtype = bodo.string_array_type
        return gen_vectorized(arg_names, arg_types, propagate_null,
            scalar_text, out_dtype)
    return overload_left_right_util


def _install_left_right_overload():
    for eqjr__pfnfm, func_name in zip((left_util, right_util), ('LEFT',
        'RIGHT')):
        mzu__wneql = create_left_right_util_overload(func_name)
        overload(eqjr__pfnfm)(mzu__wneql)


_install_left_right_overload()


@numba.generated_jit(nopython=True)
def repeat(arr, repeats):
    args = [arr, repeats]
    for i in range(2):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.repeat',
                ['arr', 'repeats'], i)

    def impl(arr, repeats):
        return repeat_util(arr, repeats)
    return impl


@numba.generated_jit(nopython=True)
def repeat_util(arr, repeats):
    verify_string_arg(arr, 'REPEAT', 'arr')
    verify_int_arg(repeats, 'REPEAT', 'repeats')
    arg_names = ['arr', 'repeats']
    arg_types = [arr, repeats]
    propagate_null = [True] * 2
    scalar_text = 'if arg1 <= 0:\n'
    scalar_text += "   res[i] = ''\n"
    scalar_text += 'else:\n'
    scalar_text += '   res[i] = arg0 * arg1'
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def space(n_chars):
    if isinstance(n_chars, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.space_util',
            ['n_chars'], 0)

    def impl(n_chars):
        return space_util(n_chars)
    return impl


@numba.generated_jit(nopython=True)
def space_util(n_chars):
    verify_int_arg(n_chars, 'SPACE', 'n_chars')
    arg_names = ['n_chars']
    arg_types = [n_chars]
    propagate_null = [True]
    scalar_text = 'if arg0 <= 0:\n'
    scalar_text += "   res[i] = ''\n"
    scalar_text += 'else:\n'
    scalar_text += "   res[i] = ' ' * arg0"
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def reverse(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.reverse_util',
            ['arr'], 0)

    def impl(arr):
        return reverse_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def reverse_util(arr):
    verify_string_arg(arr, 'REVERSE', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = 'res[i] = arg0[::-1]'
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def replace(arr, to_replace, replace_with):
    args = [arr, to_replace, replace_with]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.replace',
                ['arr', 'to_replace', 'replace_with'], i)

    def impl(arr, to_replace, replace_with):
        return replace_util(arr, to_replace, replace_with)
    return impl


@numba.generated_jit(nopython=True)
def replace_util(arr, to_replace, replace_with):
    verify_string_arg(arr, 'REPLACE', 'arr')
    verify_string_arg(to_replace, 'REPLACE', 'to_replace')
    verify_string_arg(replace_with, 'REPLACE', 'replace_with')
    arg_names = ['arr', 'to_replace', 'replace_with']
    arg_types = [arr, to_replace, replace_with]
    propagate_null = [True] * 3
    scalar_text = "if arg1 == '':\n"
    scalar_text += '   res[i] = arg0\n'
    scalar_text += 'else:\n'
    scalar_text += '   res[i] = arg0.replace(arg1, arg2)'
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def int_to_days(arr):
    if isinstance(arr, types.optional):
        return unopt_argument(
            'bodo.libs.bodosql_array_kernels.int_to_days_util', ['arr'], 0)

    def impl(arr):
        return int_to_days_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def second_timestamp(arr):
    if isinstance(arr, types.optional):
        return unopt_argument(
            'bodo.libs.bodosql_array_kernels.second_timestamp_util', ['arr'], 0
            )

    def impl(arr):
        return second_timestamp_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def day_timestamp(arr):
    if isinstance(arr, types.optional):
        return unopt_argument(
            'bodo.libs.bodosql_array_kernels.day_timestamp_util', ['arr'], 0)

    def impl(arr):
        return day_timestamp_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def month_diff(arr0, arr1):
    args = [arr0, arr1]
    for i in range(2):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.month_diff',
                ['arr0', 'arr1'], i)

    def impl(arr0, arr1):
        return month_diff_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def int_to_days_util(arr):
    verify_int_arg(arr, 'int_to_days', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = (
        'res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timedelta(days=arg0))'
        )
    out_dtype = np.dtype('timedelta64[ns]')
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def second_timestamp_util(arr):
    verify_int_arg(arr, 'second_timestamp', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = (
        "res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(arg0, unit='s'))"
        )
    out_dtype = np.dtype('datetime64[ns]')
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def day_timestamp_util(arr):
    verify_int_arg(arr, 'day_timestamp', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = (
        "res[i] = bodo.utils.conversion.unbox_if_timestamp(pd.Timestamp(arg0, unit='D'))"
        )
    out_dtype = np.dtype('datetime64[ns]')
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def month_diff_util(arr0, arr1):
    verify_datetime_arg(arr0, 'month_diff', 'arr0')
    verify_datetime_arg(arr1, 'month_diff', 'arr1')
    arg_names = ['arr0', 'arr1']
    arg_types = [arr0, arr1]
    propagate_null = [True] * 2
    scalar_text = 'A0 = bodo.utils.conversion.box_if_dt64(arg0)\n'
    scalar_text += 'A1 = bodo.utils.conversion.box_if_dt64(arg1)\n'
    scalar_text += 'delta = 12 * (A0.year - A1.year) + (A0.month - A1.month)\n'
    scalar_text += (
        'remainder = ((A0 - pd.DateOffset(months=delta)) - A1).value\n')
    scalar_text += 'if delta > 0 and remainder < 0:\n'
    scalar_text += '   res[i] = -(delta - 1)\n'
    scalar_text += 'elif delta < 0 and remainder > 0:\n'
    scalar_text += '   res[i] = -(delta + 1)\n'
    scalar_text += 'else:\n'
    scalar_text += '   res[i] = -delta'
    out_dtype = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def conv(arr, old_base, new_base):
    args = [arr, old_base, new_base]
    for i in range(3):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.conv', [
                'arr', 'old_base', 'new_base'], i)

    def impl(arr, old_base, new_base):
        return conv_util(arr, old_base, new_base)
    return impl


@numba.generated_jit(nopython=True)
def conv_util(arr, old_base, new_base):
    verify_string_arg(arr, 'CONV', 'arr')
    verify_int_arg(old_base, 'CONV', 'old_base')
    verify_int_arg(new_base, 'CONV', 'new_base')
    arg_names = ['arr', 'old_base', 'new_base']
    arg_types = [arr, old_base, new_base]
    propagate_null = [True] * 3
    scalar_text = 'old_val = int(arg0, arg1)\n'
    scalar_text += 'if arg2 == 2:\n'
    scalar_text += "   res[i] = format(old_val, 'b')\n"
    scalar_text += 'elif arg2 == 8:\n'
    scalar_text += "   res[i] = format(old_val, 'o')\n"
    scalar_text += 'elif arg2 == 10:\n'
    scalar_text += "   res[i] = format(old_val, 'd')\n"
    scalar_text += 'elif arg2 == 16:\n'
    scalar_text += "   res[i] = format(old_val, 'x')\n"
    scalar_text += 'else:\n'
    scalar_text += '   bodo.libs.array_kernels.setna(res, i)\n'
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def ord_ascii(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.ord_ascii_util',
            ['arr'], 0)

    def impl(arr):
        return ord_ascii_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def ord_ascii_util(arr):
    verify_string_arg(arr, 'ORD', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = 'if len(arg0) == 0:\n'
    scalar_text += '   bodo.libs.array_kernels.setna(res, i)\n'
    scalar_text += 'else:\n'
    scalar_text += '   res[i] = ord(arg0[0])'
    out_dtype = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def char(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.char_util',
            ['arr'], 0)

    def impl(arr):
        return char_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def char_util(arr):
    verify_int_arg(arr, 'CHAR', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    scalar_text = 'if 0 <= arg0 <= 127:\n'
    scalar_text += '   res[i] = chr(arg0)\n'
    scalar_text += 'else:\n'
    scalar_text += '   bodo.libs.array_kernels.setna(res, i)\n'
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def format(arr, places):
    args = [arr, places]
    for i in range(2):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.format',
                ['arr', 'places'], i)

    def impl(arr, places):
        return format_util(arr, places)
    return impl


@numba.generated_jit(nopython=True)
def format_util(arr, places):
    verify_int_float_arg(arr, 'FORMAT', 'arr')
    verify_int_arg(places, 'FORMAT', 'places')
    arg_names = ['arr', 'places']
    arg_types = [arr, places]
    propagate_null = [True] * 2
    scalar_text = 'prec = max(arg1, 0)\n'
    scalar_text += "res[i] = format(arg0, f',.{prec}f')"
    out_dtype = bodo.string_array_type
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def strcmp(arr0, arr1):
    args = [arr0, arr1]
    for i in range(2):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.strcmp',
                ['arr0', 'arr1'], i)

    def impl(arr0, arr1):
        return strcmp_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def strcmp_util(arr0, arr1):
    verify_string_arg(arr0, 'strcmp', 'arr0')
    verify_string_arg(arr1, 'strcmp', 'arr1')
    arg_names = ['arr0', 'arr1']
    arg_types = [arr0, arr1]
    propagate_null = [True] * 2
    scalar_text = 'if arg0 < arg1:\n'
    scalar_text += '   res[i] = -1\n'
    scalar_text += 'elif arg0 > arg1:\n'
    scalar_text += '   res[i] = 1\n'
    scalar_text += 'else:\n'
    scalar_text += '   res[i] = 0\n'
    out_dtype = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def instr(arr, target):
    args = [arr, target]
    for i in range(2):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.instr',
                ['arr', 'target'], i)

    def impl(arr, target):
        return instr_util(arr, target)
    return impl


@numba.generated_jit(nopython=True)
def instr_util(arr, target):
    verify_string_arg(arr, 'instr', 'arr')
    verify_string_arg(target, 'instr', 'target')
    arg_names = ['arr', 'target']
    arg_types = [arr, target]
    propagate_null = [True] * 2
    scalar_text = 'res[i] = arg0.find(arg1) + 1'
    out_dtype = bodo.libs.int_arr_ext.IntegerArrayType(types.int32)
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def log(arr, base):
    args = [arr, base]
    for i in range(2):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.log', [
                'arr', 'base'], i)

    def impl(arr, base):
        return log_util(arr, base)
    return impl


@numba.generated_jit(nopython=True)
def log_util(arr, base):
    verify_int_float_arg(arr, 'log', 'arr')
    verify_int_float_arg(base, 'log', 'base')
    arg_names = ['arr', 'base']
    arg_types = [arr, base]
    propagate_null = [True] * 2
    scalar_text = 'res[i] = np.log(arg0) / np.log(arg1)'
    out_dtype = types.Array(bodo.float64, 1, 'C')
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def negate(arr):
    if isinstance(arr, types.optional):
        return unopt_argument('bodo.libs.bodosql_array_kernels.negate_util',
            ['arr'], 0)

    def impl(arr):
        return negate_util(arr)
    return impl


@numba.generated_jit(nopython=True)
def negate_util(arr):
    verify_int_float_arg(arr, 'negate', 'arr')
    arg_names = ['arr']
    arg_types = [arr]
    propagate_null = [True]
    if arr == bodo.none:
        qrki__bsj = types.int32
    elif bodo.utils.utils.is_array_typ(arr, False):
        qrki__bsj = arr.dtype
    elif bodo.utils.utils.is_array_typ(arr, True):
        qrki__bsj = arr.data.dtype
    else:
        qrki__bsj = arr
    scalar_text = {types.uint8: 'res[i] = -np.int16(arg0)', types.uint16:
        'res[i] = -np.int32(arg0)', types.uint32: 'res[i] = -np.int64(arg0)'
        }.get(qrki__bsj, 'res[i] = -arg0')
    qrki__bsj = {types.uint8: types.int16, types.uint16: types.int32, types
        .uint32: types.int64, types.uint64: types.int64}.get(qrki__bsj,
        qrki__bsj)
    out_dtype = bodo.utils.typing.to_nullable_type(bodo.utils.typing.
        dtype_to_array_type(qrki__bsj))
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)


@numba.generated_jit(nopython=True)
def nullif(arr0, arr1):
    args = [arr0, arr1]
    for i in range(2):
        if isinstance(args[i], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.nullif',
                ['arr0', 'arr1'], i)

    def impl(arr0, arr1):
        return nullif_util(arr0, arr1)
    return impl


@numba.generated_jit(nopython=True)
def nullif_util(arr0, arr1):
    arg_names = ['arr0', 'arr1']
    arg_types = [arr0, arr1]
    propagate_null = [True, False]
    if arr1 == bodo.none:
        scalar_text = 'res[i] = arg0\n'
    elif bodo.utils.utils.is_array_typ(arr1, True):
        scalar_text = (
            'if bodo.libs.array_kernels.isna(arr1, i) or arg0 != arg1:\n')
        scalar_text += '   res[i] = arg0\n'
        scalar_text += 'else:\n'
        scalar_text += '   bodo.libs.array_kernels.setna(res, i)'
    else:
        scalar_text = 'if arg0 != arg1:\n'
        scalar_text += '   res[i] = arg0\n'
        scalar_text += 'else:\n'
        scalar_text += '   bodo.libs.array_kernels.setna(res, i)'
    out_dtype = get_common_broadcasted_type([arr0, arr1], 'NULLIF')
    return gen_vectorized(arg_names, arg_types, propagate_null, scalar_text,
        out_dtype)
