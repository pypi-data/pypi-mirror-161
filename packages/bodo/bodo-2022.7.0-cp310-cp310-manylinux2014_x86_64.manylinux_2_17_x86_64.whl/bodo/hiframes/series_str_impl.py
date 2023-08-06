"""
Support for Series.str methods
"""
import operator
import re
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model
import bodo
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.pd_index_ext import StringIndexType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.hiframes.split_impl import get_split_view_data_ptr, get_split_view_index, string_array_split_view_type
from bodo.libs.array import get_search_regex
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.str_arr_ext import get_utf8_size, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import str_findall_count
from bodo.utils.typing import BodoError, create_unsupported_overload, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_str_len, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_constant_list, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, is_str_arr_type, raise_bodo_error


class SeriesStrMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        rmtlw__gdd = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(rmtlw__gdd)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        gqao__xtaz = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, gqao__xtaz)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        yhb__cxu, = args
        utgdg__hsdf = signature.return_type
        wcphq__cpnp = cgutils.create_struct_proxy(utgdg__hsdf)(context, builder
            )
        wcphq__cpnp.obj = yhb__cxu
        context.nrt.incref(builder, signature.args[0], yhb__cxu)
        return wcphq__cpnp._getvalue()
    return SeriesStrMethodType(obj)(obj), codegen


def str_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.UnicodeType) and not is_overload_constant_str(
        arg):
        raise_bodo_error(
            "Series.str.{}(): parameter '{}' expected a string object, not {}"
            .format(func_name, arg_name, arg))


def int_arg_check(func_name, arg_name, arg):
    if not isinstance(arg, types.Integer) and not is_overload_constant_int(arg
        ):
        raise BodoError(
            "Series.str.{}(): parameter '{}' expected an int object, not {}"
            .format(func_name, arg_name, arg))


def not_supported_arg_check(func_name, arg_name, arg, defval):
    if arg_name == 'na':
        if not isinstance(arg, types.Omitted) and (not isinstance(arg,
            float) or not np.isnan(arg)):
            raise BodoError(
                "Series.str.{}(): parameter '{}' is not supported, default: np.nan"
                .format(func_name, arg_name))
    elif not isinstance(arg, types.Omitted) and arg != defval:
        raise BodoError(
            "Series.str.{}(): parameter '{}' is not supported, default: {}"
            .format(func_name, arg_name, defval))


def common_validate_padding(func_name, width, fillchar):
    if is_overload_constant_str(fillchar):
        if get_overload_const_str_len(fillchar) != 1:
            raise BodoError(
                'Series.str.{}(): fillchar must be a character, not str'.
                format(func_name))
    elif not isinstance(fillchar, types.UnicodeType):
        raise BodoError('Series.str.{}(): fillchar must be a character, not {}'
            .format(func_name, fillchar))
    int_arg_check(func_name, 'width', width)


@overload_attribute(SeriesType, 'str')
def overload_series_str(S):
    if not (is_str_arr_type(S.data) or S.data ==
        string_array_split_view_type or isinstance(S.data, ArrayItemArrayType)
        ):
        raise_bodo_error(
            'Series.str: input should be a series of string or arrays')
    return lambda S: bodo.hiframes.series_str_impl.init_series_str_method(S)


@overload_method(SeriesStrMethodType, 'len', inline='always', no_unliteral=True
    )
def overload_str_method_len(S_str):
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_len_dict_impl(S_str):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(rap__rotl)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(rap__rotl, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload_method(SeriesStrMethodType, 'split', inline='always',
    no_unliteral=True)
def overload_str_method_split(S_str, pat=None, n=-1, expand=False):
    if not is_overload_none(pat):
        str_arg_check('split', 'pat', pat)
    int_arg_check('split', 'n', n)
    not_supported_arg_check('split', 'expand', expand, False)
    if is_overload_constant_str(pat) and len(get_overload_const_str(pat)
        ) == 1 and get_overload_const_str(pat).isascii(
        ) and is_overload_constant_int(n) and get_overload_const_int(n
        ) == -1 and S_str.stype.data == string_array_type:

        def _str_split_view_impl(S_str, pat=None, n=-1, expand=False):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(rap__rotl,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(rap__rotl, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    rcr__zlhp = S_str.stype.data
    if (rcr__zlhp != string_array_split_view_type and not is_str_arr_type(
        rcr__zlhp)) and not isinstance(rcr__zlhp, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(rcr__zlhp, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(rap__rotl, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_get_array_impl
    if rcr__zlhp == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(rap__rotl)
            slqs__giio = 0
            for niuhg__zbjnx in numba.parfors.parfor.internal_prange(n):
                nzt__vfzr, nzt__vfzr, npcf__shdak = get_split_view_index(
                    rap__rotl, niuhg__zbjnx, i)
                slqs__giio += npcf__shdak
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, slqs__giio)
            for ubar__kwhld in numba.parfors.parfor.internal_prange(n):
                lgoqd__eep, sdb__abw, npcf__shdak = get_split_view_index(
                    rap__rotl, ubar__kwhld, i)
                if lgoqd__eep == 0:
                    bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
                    aekzi__jsyhu = get_split_view_data_ptr(rap__rotl, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        ubar__kwhld)
                    aekzi__jsyhu = get_split_view_data_ptr(rap__rotl, sdb__abw)
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    ubar__kwhld, aekzi__jsyhu, npcf__shdak)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(rap__rotl, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(rap__rotl)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for ubar__kwhld in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(rap__rotl, ubar__kwhld) or not len(
                rap__rotl[ubar__kwhld]) > i >= -len(rap__rotl[ubar__kwhld]):
                out_arr[ubar__kwhld] = ''
                bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
            else:
                out_arr[ubar__kwhld] = rap__rotl[ubar__kwhld][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    rcr__zlhp = S_str.stype.data
    if (rcr__zlhp != string_array_split_view_type and rcr__zlhp !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        rcr__zlhp)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(ber__wzg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for ubar__kwhld in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(ber__wzg, ubar__kwhld):
                out_arr[ubar__kwhld] = ''
                bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
            else:
                lyo__efwf = ber__wzg[ubar__kwhld]
                out_arr[ubar__kwhld] = sep.join(lyo__efwf)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload_method(SeriesStrMethodType, 'replace', inline='always',
    no_unliteral=True)
def overload_str_method_replace(S_str, pat, repl, n=-1, case=None, flags=0,
    regex=True):
    not_supported_arg_check('replace', 'n', n, -1)
    not_supported_arg_check('replace', 'case', case, None)
    str_arg_check('replace', 'pat', pat)
    str_arg_check('replace', 'repl', repl)
    int_arg_check('replace', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_replace_dict_impl(S_str, pat, repl, n=-1, case=None, flags
            =0, regex=True):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(rap__rotl, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            bhnxe__rao = re.compile(pat, flags)
            qpx__npcxs = len(rap__rotl)
            out_arr = pre_alloc_string_array(qpx__npcxs, -1)
            for ubar__kwhld in numba.parfors.parfor.internal_prange(qpx__npcxs
                ):
                if bodo.libs.array_kernels.isna(rap__rotl, ubar__kwhld):
                    out_arr[ubar__kwhld] = ''
                    bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
                    continue
                out_arr[ubar__kwhld] = bhnxe__rao.sub(repl, rap__rotl[
                    ubar__kwhld])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        qpx__npcxs = len(rap__rotl)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(qpx__npcxs, -1)
        for ubar__kwhld in numba.parfors.parfor.internal_prange(qpx__npcxs):
            if bodo.libs.array_kernels.isna(rap__rotl, ubar__kwhld):
                out_arr[ubar__kwhld] = ''
                bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
                continue
            out_arr[ubar__kwhld] = rap__rotl[ubar__kwhld].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return _str_replace_noregex_impl


@numba.njit
def series_contains_regex(S, pat, case, flags, na, regex):
    with numba.objmode(out_arr=bodo.boolean_array):
        out_arr = S.array._str_contains(pat, case, flags, na, regex)
    return out_arr


@numba.njit
def series_match_regex(S, pat, case, flags, na):
    with numba.objmode(out_arr=bodo.boolean_array):
        out_arr = S.array._str_match(pat, case, flags, na)
    return out_arr


def is_regex_unsupported(pat):
    ovyih__qkei = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(zqf__uqq in pat) for zqf__uqq in ovyih__qkei])
    else:
        return True


@overload_method(SeriesStrMethodType, 'contains', no_unliteral=True)
def overload_str_method_contains(S_str, pat, case=True, flags=0, na=np.nan,
    regex=True):
    not_supported_arg_check('contains', 'na', na, np.nan)
    str_arg_check('contains', 'pat', pat)
    int_arg_check('contains', 'flags', flags)
    if not is_overload_constant_bool(regex):
        raise BodoError(
            "Series.str.contains(): 'regex' argument should be a constant boolean"
            )
    if not is_overload_constant_bool(case):
        raise BodoError(
            "Series.str.contains(): 'case' argument should be a constant boolean"
            )
    rktja__ugl = re.IGNORECASE.value
    mhwt__aca = 'def impl(\n'
    mhwt__aca += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    mhwt__aca += '):\n'
    mhwt__aca += '  S = S_str._obj\n'
    mhwt__aca += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    mhwt__aca += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    mhwt__aca += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    mhwt__aca += '  l = len(arr)\n'
    mhwt__aca += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                mhwt__aca += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                mhwt__aca += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            mhwt__aca += """  get_search_regex(arr, case, False, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        mhwt__aca += (
            '  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)\n'
            )
    else:
        mhwt__aca += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            mhwt__aca += '  upper_pat = pat.upper()\n'
        mhwt__aca += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        mhwt__aca += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        mhwt__aca += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        mhwt__aca += '      else: \n'
        if is_overload_true(case):
            mhwt__aca += '          out_arr[i] = pat in arr[i]\n'
        else:
            mhwt__aca += '          out_arr[i] = upper_pat in arr[i].upper()\n'
    mhwt__aca += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    upw__ptyr = {}
    exec(mhwt__aca, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': rktja__ugl, 'get_search_regex':
        get_search_regex}, upw__ptyr)
    impl = upw__ptyr['impl']
    return impl


@overload_method(SeriesStrMethodType, 'match', inline='always',
    no_unliteral=True)
def overload_str_method_match(S_str, pat, case=True, flags=0, na=np.nan):
    not_supported_arg_check('match', 'na', na, np.nan)
    str_arg_check('match', 'pat', pat)
    int_arg_check('match', 'flags', flags)
    if not is_overload_constant_bool(case):
        raise BodoError(
            "Series.str.match(): 'case' argument should be a constant boolean")
    rktja__ugl = re.IGNORECASE.value
    mhwt__aca = 'def impl(S_str, pat, case=True, flags=0, na=np.nan):\n'
    mhwt__aca += '        S = S_str._obj\n'
    mhwt__aca += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    mhwt__aca += '        l = len(arr)\n'
    mhwt__aca += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    mhwt__aca += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if not is_regex_unsupported(pat) and flags == 0:
        mhwt__aca += (
            '        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        mhwt__aca += """        get_search_regex(arr, case, True, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        mhwt__aca += """        out_arr = bodo.libs.dict_arr_ext.str_match(arr, pat, case, flags, na)
"""
    else:
        mhwt__aca += (
            '        out_arr = series_match_regex(S, pat, case, flags, na)\n')
    mhwt__aca += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    upw__ptyr = {}
    exec(mhwt__aca, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': rktja__ugl, 'get_search_regex':
        get_search_regex}, upw__ptyr)
    impl = upw__ptyr['impl']
    return impl


@overload_method(SeriesStrMethodType, 'cat', no_unliteral=True)
def overload_str_method_cat(S_str, others=None, sep=None, na_rep=None, join
    ='left'):
    if not isinstance(others, DataFrameType):
        raise_bodo_error(
            "Series.str.cat(): 'others' must be a DataFrame currently")
    if not is_overload_none(sep):
        str_arg_check('cat', 'sep', sep)
    if not is_overload_constant_str(join) or get_overload_const_str(join
        ) != 'left':
        raise_bodo_error("Series.str.cat(): 'join' not supported yet")
    mhwt__aca = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    mhwt__aca += '  S = S_str._obj\n'
    mhwt__aca += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    mhwt__aca += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    mhwt__aca += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    mhwt__aca += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        mhwt__aca += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})\n'
            )
    if S_str.stype.data == bodo.dict_str_arr_type and all(krjy__biig ==
        bodo.dict_str_arr_type for krjy__biig in others.data):
        hpbch__jcxzz = ', '.join(f'data{i}' for i in range(len(others.columns))
            )
        mhwt__aca += f"""  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {hpbch__jcxzz}), sep)
"""
    else:
        zzd__mfst = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] +
            [f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len
            (others.columns))])
        mhwt__aca += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        mhwt__aca += '  numba.parfors.parfor.init_prange()\n'
        mhwt__aca += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        mhwt__aca += f'      if {zzd__mfst}:\n'
        mhwt__aca += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        mhwt__aca += '          continue\n'
        uxt__kxro = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range(
            len(others.columns))])
        wnfpj__uzt = "''" if is_overload_none(sep) else 'sep'
        mhwt__aca += f'      out_arr[i] = {wnfpj__uzt}.join([{uxt__kxro}])\n'
    mhwt__aca += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    upw__ptyr = {}
    exec(mhwt__aca, {'bodo': bodo, 'numba': numba}, upw__ptyr)
    impl = upw__ptyr['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(rap__rotl, pat, flags)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        bhnxe__rao = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        qpx__npcxs = len(ber__wzg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(qpx__npcxs, np.int64)
        for i in numba.parfors.parfor.internal_prange(qpx__npcxs):
            if bodo.libs.array_kernels.isna(ber__wzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(bhnxe__rao, ber__wzg[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload_method(SeriesStrMethodType, 'find', inline='always', no_unliteral
    =True)
def overload_str_method_find(S_str, sub, start=0, end=None):
    str_arg_check('find', 'sub', sub)
    int_arg_check('find', 'start', start)
    if not is_overload_none(end):
        int_arg_check('find', 'end', end)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_find_dict_impl(S_str, sub, start=0, end=None):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(rap__rotl, sub, start,
                end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        qpx__npcxs = len(ber__wzg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(qpx__npcxs, np.int64)
        for i in numba.parfors.parfor.internal_prange(qpx__npcxs):
            if bodo.libs.array_kernels.isna(ber__wzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ber__wzg[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload_method(SeriesStrMethodType, 'rfind', inline='always',
    no_unliteral=True)
def overload_str_method_rfind(S_str, sub, start=0, end=None):
    str_arg_check('rfind', 'sub', sub)
    if start != 0:
        int_arg_check('rfind', 'start', start)
    if not is_overload_none(end):
        int_arg_check('rfind', 'end', end)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_rfind_dict_impl(S_str, sub, start=0, end=None):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(rap__rotl, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        qpx__npcxs = len(ber__wzg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(qpx__npcxs, np.int64)
        for i in numba.parfors.parfor.internal_prange(qpx__npcxs):
            if bodo.libs.array_kernels.isna(ber__wzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ber__wzg[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload_method(SeriesStrMethodType, 'slice_replace', inline='always',
    no_unliteral=True)
def overload_str_method_slice_replace(S_str, start=0, stop=None, repl=''):
    int_arg_check('slice_replace', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice_replace', 'stop', stop)
    str_arg_check('slice_replace', 'repl', repl)

    def impl(S_str, start=0, stop=None, repl=''):
        S = S_str._obj
        ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        qpx__npcxs = len(ber__wzg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(qpx__npcxs, -1)
        for ubar__kwhld in numba.parfors.parfor.internal_prange(qpx__npcxs):
            if bodo.libs.array_kernels.isna(ber__wzg, ubar__kwhld):
                bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
            else:
                if stop is not None:
                    yhfb__veep = ber__wzg[ubar__kwhld][stop:]
                else:
                    yhfb__veep = ''
                out_arr[ubar__kwhld] = ber__wzg[ubar__kwhld][:start
                    ] + repl + yhfb__veep
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
                kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
                rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(rap__rotl,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    kdb__qjbtx, rmtlw__gdd)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            qpx__npcxs = len(ber__wzg)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(qpx__npcxs,
                -1)
            for ubar__kwhld in numba.parfors.parfor.internal_prange(qpx__npcxs
                ):
                if bodo.libs.array_kernels.isna(ber__wzg, ubar__kwhld):
                    bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
                else:
                    out_arr[ubar__kwhld] = ber__wzg[ubar__kwhld] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return impl
    elif is_overload_constant_list(repeats):
        lkngv__yztht = get_overload_const_list(repeats)
        lhc__zlc = all([isinstance(deib__bqgg, int) for deib__bqgg in
            lkngv__yztht])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        lhc__zlc = True
    else:
        lhc__zlc = False
    if lhc__zlc:

        def impl(S_str, repeats):
            S = S_str._obj
            ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            ogg__dhthw = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            qpx__npcxs = len(ber__wzg)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(qpx__npcxs,
                -1)
            for ubar__kwhld in numba.parfors.parfor.internal_prange(qpx__npcxs
                ):
                if bodo.libs.array_kernels.isna(ber__wzg, ubar__kwhld):
                    bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
                else:
                    out_arr[ubar__kwhld] = ber__wzg[ubar__kwhld] * ogg__dhthw[
                        ubar__kwhld]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    mhwt__aca = f"""def dict_impl(S_str, width, fillchar=' '):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr, width, fillchar)
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
def impl(S_str, width, fillchar=' '):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    numba.parfors.parfor.init_prange()
    l = len(str_arr)
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
    for j in numba.parfors.parfor.internal_prange(l):
        if bodo.libs.array_kernels.isna(str_arr, j):
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}(width, fillchar)
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    upw__ptyr = {}
    fxadc__mtngf = {'bodo': bodo, 'numba': numba}
    exec(mhwt__aca, fxadc__mtngf, upw__ptyr)
    impl = upw__ptyr['impl']
    fxnz__zud = upw__ptyr['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return fxnz__zud
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for riykm__ltbd in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(riykm__ltbd)
        overload_method(SeriesStrMethodType, riykm__ltbd, inline='always',
            no_unliteral=True)(impl)


_install_ljust_rjust_center()


@overload_method(SeriesStrMethodType, 'pad', no_unliteral=True)
def overload_str_method_pad(S_str, width, side='left', fillchar=' '):
    common_validate_padding('pad', width, fillchar)
    if is_overload_constant_str(side):
        if get_overload_const_str(side) not in ['left', 'right', 'both']:
            raise BodoError('Series.str.pad(): Invalid Side')
    else:
        raise BodoError('Series.str.pad(): Invalid Side')
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_pad_dict_impl(S_str, width, side='left', fillchar=' '):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(rap__rotl, width,
                    fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(rap__rotl, width,
                    fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(rap__rotl,
                    width, fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        qpx__npcxs = len(ber__wzg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(qpx__npcxs, -1)
        for ubar__kwhld in numba.parfors.parfor.internal_prange(qpx__npcxs):
            if bodo.libs.array_kernels.isna(ber__wzg, ubar__kwhld):
                out_arr[ubar__kwhld] = ''
                bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
            elif side == 'left':
                out_arr[ubar__kwhld] = ber__wzg[ubar__kwhld].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[ubar__kwhld] = ber__wzg[ubar__kwhld].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[ubar__kwhld] = ber__wzg[ubar__kwhld].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(rap__rotl, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        qpx__npcxs = len(ber__wzg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(qpx__npcxs, -1)
        for ubar__kwhld in numba.parfors.parfor.internal_prange(qpx__npcxs):
            if bodo.libs.array_kernels.isna(ber__wzg, ubar__kwhld):
                out_arr[ubar__kwhld] = ''
                bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
            else:
                out_arr[ubar__kwhld] = ber__wzg[ubar__kwhld].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload_method(SeriesStrMethodType, 'slice', no_unliteral=True)
def overload_str_method_slice(S_str, start=None, stop=None, step=None):
    if not is_overload_none(start):
        int_arg_check('slice', 'start', start)
    if not is_overload_none(stop):
        int_arg_check('slice', 'stop', stop)
    if not is_overload_none(step):
        int_arg_check('slice', 'step', step)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_slice_dict_impl(S_str, start=None, stop=None, step=None):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(rap__rotl, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        qpx__npcxs = len(ber__wzg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(qpx__npcxs, -1)
        for ubar__kwhld in numba.parfors.parfor.internal_prange(qpx__npcxs):
            if bodo.libs.array_kernels.isna(ber__wzg, ubar__kwhld):
                out_arr[ubar__kwhld] = ''
                bodo.libs.array_kernels.setna(out_arr, ubar__kwhld)
            else:
                out_arr[ubar__kwhld] = ber__wzg[ubar__kwhld][start:stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(rap__rotl, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        qpx__npcxs = len(ber__wzg)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(qpx__npcxs)
        for i in numba.parfors.parfor.internal_prange(qpx__npcxs):
            if bodo.libs.array_kernels.isna(ber__wzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ber__wzg[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
            kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
            rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(rap__rotl, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                kdb__qjbtx, rmtlw__gdd)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        ber__wzg = bodo.hiframes.pd_series_ext.get_series_data(S)
        rmtlw__gdd = bodo.hiframes.pd_series_ext.get_series_name(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        qpx__npcxs = len(ber__wzg)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(qpx__npcxs)
        for i in numba.parfors.parfor.internal_prange(qpx__npcxs):
            if bodo.libs.array_kernels.isna(ber__wzg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = ber__wzg[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, kdb__qjbtx,
            rmtlw__gdd)
    return impl


@overload(operator.getitem, no_unliteral=True)
def overload_str_method_getitem(S_str, ind):
    if not isinstance(S_str, SeriesStrMethodType):
        return
    if not isinstance(types.unliteral(ind), (types.SliceType, types.Integer)):
        raise BodoError(
            'index input to Series.str[] should be a slice or an integer')
    if isinstance(ind, types.SliceType):
        return lambda S_str, ind: S_str.slice(ind.start, ind.stop, ind.step)
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda S_str, ind: S_str.get(ind)


@overload_method(SeriesStrMethodType, 'extract', inline='always',
    no_unliteral=True)
def overload_str_method_extract(S_str, pat, flags=0, expand=True):
    if not is_overload_constant_bool(expand):
        raise BodoError(
            "Series.str.extract(): 'expand' argument should be a constant bool"
            )
    lwwf__crw, regex = _get_column_names_from_regex(pat, flags, 'extract')
    esip__zagty = len(lwwf__crw)
    if S_str.stype.data == bodo.dict_str_arr_type:
        mhwt__aca = 'def impl(S_str, pat, flags=0, expand=True):\n'
        mhwt__aca += '  S = S_str._obj\n'
        mhwt__aca += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        mhwt__aca += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        mhwt__aca += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        mhwt__aca += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {esip__zagty})
"""
        for i in range(esip__zagty):
            mhwt__aca += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        mhwt__aca = 'def impl(S_str, pat, flags=0, expand=True):\n'
        mhwt__aca += '  regex = re.compile(pat, flags=flags)\n'
        mhwt__aca += '  S = S_str._obj\n'
        mhwt__aca += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        mhwt__aca += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        mhwt__aca += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        mhwt__aca += '  numba.parfors.parfor.init_prange()\n'
        mhwt__aca += '  n = len(str_arr)\n'
        for i in range(esip__zagty):
            mhwt__aca += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        mhwt__aca += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        mhwt__aca += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(esip__zagty):
            mhwt__aca += "          out_arr_{}[j] = ''\n".format(i)
            mhwt__aca += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        mhwt__aca += '      else:\n'
        mhwt__aca += '          m = regex.search(str_arr[j])\n'
        mhwt__aca += '          if m:\n'
        mhwt__aca += '            g = m.groups()\n'
        for i in range(esip__zagty):
            mhwt__aca += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        mhwt__aca += '          else:\n'
        for i in range(esip__zagty):
            mhwt__aca += "            out_arr_{}[j] = ''\n".format(i)
            mhwt__aca += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        rmtlw__gdd = "'{}'".format(list(regex.groupindex.keys()).pop()) if len(
            regex.groupindex.keys()) > 0 else 'name'
        mhwt__aca += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(rmtlw__gdd))
        upw__ptyr = {}
        exec(mhwt__aca, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, upw__ptyr)
        impl = upw__ptyr['impl']
        return impl
    yfa__uuch = ', '.join('out_arr_{}'.format(i) for i in range(esip__zagty))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(mhwt__aca, lwwf__crw,
        yfa__uuch, 'index', extra_globals={'get_utf8_size': get_utf8_size,
        're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    lwwf__crw, nzt__vfzr = _get_column_names_from_regex(pat, flags,
        'extractall')
    esip__zagty = len(lwwf__crw)
    qzmwj__lmjj = isinstance(S_str.stype.index, StringIndexType)
    lghq__hnwn = esip__zagty > 1
    mww__scvjo = '_multi' if lghq__hnwn else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        mhwt__aca = 'def impl(S_str, pat, flags=0):\n'
        mhwt__aca += '  S = S_str._obj\n'
        mhwt__aca += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        mhwt__aca += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        mhwt__aca += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        mhwt__aca += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        mhwt__aca += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        mhwt__aca += '  regex = re.compile(pat, flags=flags)\n'
        mhwt__aca += '  out_ind_arr, out_match_arr, out_arr_list = '
        mhwt__aca += f'bodo.libs.dict_arr_ext.str_extractall{mww__scvjo}(\n'
        mhwt__aca += f'arr, regex, {esip__zagty}, index_arr)\n'
        for i in range(esip__zagty):
            mhwt__aca += f'  out_arr_{i} = out_arr_list[{i}]\n'
        mhwt__aca += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        mhwt__aca += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        mhwt__aca = 'def impl(S_str, pat, flags=0):\n'
        mhwt__aca += '  regex = re.compile(pat, flags=flags)\n'
        mhwt__aca += '  S = S_str._obj\n'
        mhwt__aca += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        mhwt__aca += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        mhwt__aca += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        mhwt__aca += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        mhwt__aca += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        mhwt__aca += '  numba.parfors.parfor.init_prange()\n'
        mhwt__aca += '  n = len(str_arr)\n'
        mhwt__aca += '  out_n_l = [0]\n'
        for i in range(esip__zagty):
            mhwt__aca += '  num_chars_{} = 0\n'.format(i)
        if qzmwj__lmjj:
            mhwt__aca += '  index_num_chars = 0\n'
        mhwt__aca += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if qzmwj__lmjj:
            mhwt__aca += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        mhwt__aca += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        mhwt__aca += '          continue\n'
        mhwt__aca += '      m = regex.findall(str_arr[i])\n'
        mhwt__aca += '      out_n_l[0] += len(m)\n'
        for i in range(esip__zagty):
            mhwt__aca += '      l_{} = 0\n'.format(i)
        mhwt__aca += '      for s in m:\n'
        for i in range(esip__zagty):
            mhwt__aca += '        l_{} += get_utf8_size(s{})\n'.format(i, 
                '[{}]'.format(i) if esip__zagty > 1 else '')
        for i in range(esip__zagty):
            mhwt__aca += '      num_chars_{0} += l_{0}\n'.format(i)
        mhwt__aca += (
            '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
            )
        for i in range(esip__zagty):
            mhwt__aca += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if qzmwj__lmjj:
            mhwt__aca += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            mhwt__aca += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
        mhwt__aca += '  out_match_arr = np.empty(out_n, np.int64)\n'
        mhwt__aca += '  out_ind = 0\n'
        mhwt__aca += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        mhwt__aca += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        mhwt__aca += '          continue\n'
        mhwt__aca += '      m = regex.findall(str_arr[j])\n'
        mhwt__aca += '      for k, s in enumerate(m):\n'
        for i in range(esip__zagty):
            mhwt__aca += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if esip__zagty > 1 else ''))
        mhwt__aca += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        mhwt__aca += (
            '        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)\n'
            )
        mhwt__aca += '        out_ind += 1\n'
        mhwt__aca += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        mhwt__aca += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    yfa__uuch = ', '.join('out_arr_{}'.format(i) for i in range(esip__zagty))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(mhwt__aca, lwwf__crw,
        yfa__uuch, 'out_index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
    return impl


def _get_column_names_from_regex(pat, flags, func_name):
    if not is_overload_constant_str(pat):
        raise BodoError(
            "Series.str.{}(): 'pat' argument should be a constant string".
            format(func_name))
    if not is_overload_constant_int(flags):
        raise BodoError(
            "Series.str.{}(): 'flags' argument should be a constant int".
            format(func_name))
    pat = get_overload_const_str(pat)
    flags = get_overload_const_int(flags)
    regex = re.compile(pat, flags=flags)
    if regex.groups == 0:
        raise BodoError(
            'Series.str.{}(): pattern {} contains no capture groups'.format
            (func_name, pat))
    fwcr__qadty = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    lwwf__crw = [fwcr__qadty.get(1 + i, i) for i in range(regex.groups)]
    return lwwf__crw, regex


def create_str2str_methods_overload(func_name):
    ysy__egdk = func_name in ['lstrip', 'rstrip', 'strip']
    mhwt__aca = f"""def f({'S_str, to_strip=None' if ysy__egdk else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if ysy__egdk else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if ysy__egdk else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    mhwt__aca += f"""def _dict_impl({'S_str, to_strip=None' if ysy__egdk else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if ysy__egdk else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    upw__ptyr = {}
    exec(mhwt__aca, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo.
        libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, upw__ptyr)
    rtlx__qlz = upw__ptyr['f']
    poecm__ysi = upw__ptyr['_dict_impl']
    if ysy__egdk:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return poecm__ysi
            return rtlx__qlz
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return poecm__ysi
            return rtlx__qlz
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    mhwt__aca = 'def dict_impl(S_str):\n'
    mhwt__aca += '    S = S_str._obj\n'
    mhwt__aca += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    mhwt__aca += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    mhwt__aca += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    mhwt__aca += f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n'
    mhwt__aca += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    mhwt__aca += 'def impl(S_str):\n'
    mhwt__aca += '    S = S_str._obj\n'
    mhwt__aca += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    mhwt__aca += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    mhwt__aca += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    mhwt__aca += '    numba.parfors.parfor.init_prange()\n'
    mhwt__aca += '    l = len(str_arr)\n'
    mhwt__aca += '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    mhwt__aca += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    mhwt__aca += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    mhwt__aca += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    mhwt__aca += '        else:\n'
    mhwt__aca += '            out_arr[i] = np.bool_(str_arr[i].{}())\n'.format(
        func_name)
    mhwt__aca += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    mhwt__aca += '      out_arr,index, name)\n'
    upw__ptyr = {}
    exec(mhwt__aca, {'bodo': bodo, 'numba': numba, 'np': np}, upw__ptyr)
    impl = upw__ptyr['impl']
    fxnz__zud = upw__ptyr['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return fxnz__zud
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for taji__sugq in bodo.hiframes.pd_series_ext.str2str_methods:
        hsnjh__uzjvw = create_str2str_methods_overload(taji__sugq)
        overload_method(SeriesStrMethodType, taji__sugq, inline='always',
            no_unliteral=True)(hsnjh__uzjvw)


def _install_str2bool_methods():
    for taji__sugq in bodo.hiframes.pd_series_ext.str2bool_methods:
        hsnjh__uzjvw = create_str2bool_methods_overload(taji__sugq)
        overload_method(SeriesStrMethodType, taji__sugq, inline='always',
            no_unliteral=True)(hsnjh__uzjvw)


_install_str2str_methods()
_install_str2bool_methods()


@overload_attribute(SeriesType, 'cat')
def overload_series_cat(s):
    if not isinstance(s.dtype, bodo.hiframes.pd_categorical_ext.
        PDCategoricalDtype):
        raise BodoError('Can only use .cat accessor with categorical values.')
    return lambda s: bodo.hiframes.series_str_impl.init_series_cat_method(s)


class SeriesCatMethodType(types.Type):

    def __init__(self, stype):
        self.stype = stype
        rmtlw__gdd = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(rmtlw__gdd)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        gqao__xtaz = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, gqao__xtaz)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        yhb__cxu, = args
        dqq__miutz = signature.return_type
        wrlmu__ihf = cgutils.create_struct_proxy(dqq__miutz)(context, builder)
        wrlmu__ihf.obj = yhb__cxu
        context.nrt.incref(builder, signature.args[0], yhb__cxu)
        return wrlmu__ihf._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        rap__rotl = bodo.hiframes.pd_series_ext.get_series_data(S)
        kdb__qjbtx = bodo.hiframes.pd_series_ext.get_series_index(S)
        rmtlw__gdd = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(rap__rotl),
            kdb__qjbtx, rmtlw__gdd)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for dea__pfpi in unsupported_cat_attrs:
        dzvjf__zpd = 'Series.cat.' + dea__pfpi
        overload_attribute(SeriesCatMethodType, dea__pfpi)(
            create_unsupported_overload(dzvjf__zpd))
    for nklu__qplne in unsupported_cat_methods:
        dzvjf__zpd = 'Series.cat.' + nklu__qplne
        overload_method(SeriesCatMethodType, nklu__qplne)(
            create_unsupported_overload(dzvjf__zpd))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for nklu__qplne in unsupported_str_methods:
        dzvjf__zpd = 'Series.str.' + nklu__qplne
        overload_method(SeriesStrMethodType, nklu__qplne)(
            create_unsupported_overload(dzvjf__zpd))


_install_strseries_unsupported()
