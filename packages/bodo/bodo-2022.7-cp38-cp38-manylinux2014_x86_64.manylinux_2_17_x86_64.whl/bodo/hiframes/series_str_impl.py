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
        odjb__skzl = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(odjb__skzl)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ncp__jvl = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, ncp__jvl)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        uyat__ybekj, = args
        oidfb__ldifm = signature.return_type
        zavm__qlq = cgutils.create_struct_proxy(oidfb__ldifm)(context, builder)
        zavm__qlq.obj = uyat__ybekj
        context.nrt.incref(builder, signature.args[0], uyat__ybekj)
        return zavm__qlq._getvalue()
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
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(zmy__pux)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(zmy__pux, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
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
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(zmy__pux, pat
                )
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(zmy__pux, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    bdd__skiz = S_str.stype.data
    if (bdd__skiz != string_array_split_view_type and not is_str_arr_type(
        bdd__skiz)) and not isinstance(bdd__skiz, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(bdd__skiz, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(zmy__pux, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_get_array_impl
    if bdd__skiz == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(zmy__pux)
            egzmo__cryh = 0
            for nisd__wwdpj in numba.parfors.parfor.internal_prange(n):
                hnuhg__srp, hnuhg__srp, uomi__muitb = get_split_view_index(
                    zmy__pux, nisd__wwdpj, i)
                egzmo__cryh += uomi__muitb
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, egzmo__cryh)
            for lpzr__upsz in numba.parfors.parfor.internal_prange(n):
                orm__hpqhh, jmpzt__fib, uomi__muitb = get_split_view_index(
                    zmy__pux, lpzr__upsz, i)
                if orm__hpqhh == 0:
                    bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
                    vhljw__ldp = get_split_view_data_ptr(zmy__pux, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        lpzr__upsz)
                    vhljw__ldp = get_split_view_data_ptr(zmy__pux, jmpzt__fib)
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    lpzr__upsz, vhljw__ldp, uomi__muitb)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(zmy__pux, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(zmy__pux)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for lpzr__upsz in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(zmy__pux, lpzr__upsz) or not len(
                zmy__pux[lpzr__upsz]) > i >= -len(zmy__pux[lpzr__upsz]):
                out_arr[lpzr__upsz] = ''
                bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
            else:
                out_arr[lpzr__upsz] = zmy__pux[lpzr__upsz][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    bdd__skiz = S_str.stype.data
    if (bdd__skiz != string_array_split_view_type and bdd__skiz !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        bdd__skiz)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(gvcu__ogpva)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for lpzr__upsz in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(gvcu__ogpva, lpzr__upsz):
                out_arr[lpzr__upsz] = ''
                bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
            else:
                zrbdo__lfuaj = gvcu__ogpva[lpzr__upsz]
                out_arr[lpzr__upsz] = sep.join(zrbdo__lfuaj)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
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
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(zmy__pux, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            tpweb__gurf = re.compile(pat, flags)
            riau__xwt = len(zmy__pux)
            out_arr = pre_alloc_string_array(riau__xwt, -1)
            for lpzr__upsz in numba.parfors.parfor.internal_prange(riau__xwt):
                if bodo.libs.array_kernels.isna(zmy__pux, lpzr__upsz):
                    out_arr[lpzr__upsz] = ''
                    bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
                    continue
                out_arr[lpzr__upsz] = tpweb__gurf.sub(repl, zmy__pux[
                    lpzr__upsz])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        riau__xwt = len(zmy__pux)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(riau__xwt, -1)
        for lpzr__upsz in numba.parfors.parfor.internal_prange(riau__xwt):
            if bodo.libs.array_kernels.isna(zmy__pux, lpzr__upsz):
                out_arr[lpzr__upsz] = ''
                bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
                continue
            out_arr[lpzr__upsz] = zmy__pux[lpzr__upsz].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
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
    obpl__wvmt = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(kmol__ctcd in pat) for kmol__ctcd in obpl__wvmt])
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
    ukpb__thk = re.IGNORECASE.value
    hqy__apip = 'def impl(\n'
    hqy__apip += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    hqy__apip += '):\n'
    hqy__apip += '  S = S_str._obj\n'
    hqy__apip += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    hqy__apip += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    hqy__apip += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    hqy__apip += '  l = len(arr)\n'
    hqy__apip += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                hqy__apip += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                hqy__apip += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            hqy__apip += """  get_search_regex(arr, case, False, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        hqy__apip += (
            '  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)\n'
            )
    else:
        hqy__apip += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            hqy__apip += '  upper_pat = pat.upper()\n'
        hqy__apip += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        hqy__apip += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        hqy__apip += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        hqy__apip += '      else: \n'
        if is_overload_true(case):
            hqy__apip += '          out_arr[i] = pat in arr[i]\n'
        else:
            hqy__apip += '          out_arr[i] = upper_pat in arr[i].upper()\n'
    hqy__apip += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    zlj__afivt = {}
    exec(hqy__apip, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': ukpb__thk, 'get_search_regex':
        get_search_regex}, zlj__afivt)
    impl = zlj__afivt['impl']
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
    ukpb__thk = re.IGNORECASE.value
    hqy__apip = 'def impl(S_str, pat, case=True, flags=0, na=np.nan):\n'
    hqy__apip += '        S = S_str._obj\n'
    hqy__apip += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    hqy__apip += '        l = len(arr)\n'
    hqy__apip += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    hqy__apip += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if not is_regex_unsupported(pat) and flags == 0:
        hqy__apip += (
            '        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        hqy__apip += """        get_search_regex(arr, case, True, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        hqy__apip += """        out_arr = bodo.libs.dict_arr_ext.str_match(arr, pat, case, flags, na)
"""
    else:
        hqy__apip += (
            '        out_arr = series_match_regex(S, pat, case, flags, na)\n')
    hqy__apip += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    zlj__afivt = {}
    exec(hqy__apip, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': ukpb__thk, 'get_search_regex':
        get_search_regex}, zlj__afivt)
    impl = zlj__afivt['impl']
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
    hqy__apip = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    hqy__apip += '  S = S_str._obj\n'
    hqy__apip += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    hqy__apip += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    hqy__apip += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    hqy__apip += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        hqy__apip += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})\n'
            )
    if S_str.stype.data == bodo.dict_str_arr_type and all(cotp__bekx ==
        bodo.dict_str_arr_type for cotp__bekx in others.data):
        hyd__wap = ', '.join(f'data{i}' for i in range(len(others.columns)))
        hqy__apip += (
            f'  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {hyd__wap}), sep)\n'
            )
    else:
        pedur__hic = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] +
            [f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len
            (others.columns))])
        hqy__apip += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        hqy__apip += '  numba.parfors.parfor.init_prange()\n'
        hqy__apip += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        hqy__apip += f'      if {pedur__hic}:\n'
        hqy__apip += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        hqy__apip += '          continue\n'
        xrb__ykh = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range(len
            (others.columns))])
        war__pwfnj = "''" if is_overload_none(sep) else 'sep'
        hqy__apip += f'      out_arr[i] = {war__pwfnj}.join([{xrb__ykh}])\n'
    hqy__apip += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    zlj__afivt = {}
    exec(hqy__apip, {'bodo': bodo, 'numba': numba}, zlj__afivt)
    impl = zlj__afivt['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(zmy__pux, pat, flags)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        tpweb__gurf = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        riau__xwt = len(gvcu__ogpva)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(riau__xwt, np.int64)
        for i in numba.parfors.parfor.internal_prange(riau__xwt):
            if bodo.libs.array_kernels.isna(gvcu__ogpva, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(tpweb__gurf, gvcu__ogpva[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
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
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(zmy__pux, sub, start, end
                )
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        riau__xwt = len(gvcu__ogpva)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(riau__xwt, np.int64)
        for i in numba.parfors.parfor.internal_prange(riau__xwt):
            if bodo.libs.array_kernels.isna(gvcu__ogpva, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = gvcu__ogpva[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
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
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(zmy__pux, sub, start,
                end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        riau__xwt = len(gvcu__ogpva)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(riau__xwt, np.int64)
        for i in numba.parfors.parfor.internal_prange(riau__xwt):
            if bodo.libs.array_kernels.isna(gvcu__ogpva, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = gvcu__ogpva[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
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
        gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        riau__xwt = len(gvcu__ogpva)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(riau__xwt, -1)
        for lpzr__upsz in numba.parfors.parfor.internal_prange(riau__xwt):
            if bodo.libs.array_kernels.isna(gvcu__ogpva, lpzr__upsz):
                bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
            else:
                if stop is not None:
                    zpfej__vlc = gvcu__ogpva[lpzr__upsz][stop:]
                else:
                    zpfej__vlc = ''
                out_arr[lpzr__upsz] = gvcu__ogpva[lpzr__upsz][:start
                    ] + repl + zpfej__vlc
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
                yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
                odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(zmy__pux,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    yidnv__zgyd, odjb__skzl)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            riau__xwt = len(gvcu__ogpva)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(riau__xwt,
                -1)
            for lpzr__upsz in numba.parfors.parfor.internal_prange(riau__xwt):
                if bodo.libs.array_kernels.isna(gvcu__ogpva, lpzr__upsz):
                    bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
                else:
                    out_arr[lpzr__upsz] = gvcu__ogpva[lpzr__upsz] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return impl
    elif is_overload_constant_list(repeats):
        mbq__lvcre = get_overload_const_list(repeats)
        kumhx__cstv = all([isinstance(jmumy__zkhtl, int) for jmumy__zkhtl in
            mbq__lvcre])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        kumhx__cstv = True
    else:
        kumhx__cstv = False
    if kumhx__cstv:

        def impl(S_str, repeats):
            S = S_str._obj
            gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            gdl__vlx = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            riau__xwt = len(gvcu__ogpva)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(riau__xwt,
                -1)
            for lpzr__upsz in numba.parfors.parfor.internal_prange(riau__xwt):
                if bodo.libs.array_kernels.isna(gvcu__ogpva, lpzr__upsz):
                    bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
                else:
                    out_arr[lpzr__upsz] = gvcu__ogpva[lpzr__upsz] * gdl__vlx[
                        lpzr__upsz]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    hqy__apip = f"""def dict_impl(S_str, width, fillchar=' '):
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
    zlj__afivt = {}
    jtc__yyk = {'bodo': bodo, 'numba': numba}
    exec(hqy__apip, jtc__yyk, zlj__afivt)
    impl = zlj__afivt['impl']
    jgld__ksiir = zlj__afivt['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return jgld__ksiir
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for ckl__btv in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(ckl__btv)
        overload_method(SeriesStrMethodType, ckl__btv, inline='always',
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
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(zmy__pux, width,
                    fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(zmy__pux, width,
                    fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(zmy__pux, width,
                    fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        riau__xwt = len(gvcu__ogpva)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(riau__xwt, -1)
        for lpzr__upsz in numba.parfors.parfor.internal_prange(riau__xwt):
            if bodo.libs.array_kernels.isna(gvcu__ogpva, lpzr__upsz):
                out_arr[lpzr__upsz] = ''
                bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
            elif side == 'left':
                out_arr[lpzr__upsz] = gvcu__ogpva[lpzr__upsz].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[lpzr__upsz] = gvcu__ogpva[lpzr__upsz].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[lpzr__upsz] = gvcu__ogpva[lpzr__upsz].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(zmy__pux, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        riau__xwt = len(gvcu__ogpva)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(riau__xwt, -1)
        for lpzr__upsz in numba.parfors.parfor.internal_prange(riau__xwt):
            if bodo.libs.array_kernels.isna(gvcu__ogpva, lpzr__upsz):
                out_arr[lpzr__upsz] = ''
                bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
            else:
                out_arr[lpzr__upsz] = gvcu__ogpva[lpzr__upsz].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
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
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(zmy__pux, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        riau__xwt = len(gvcu__ogpva)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(riau__xwt, -1)
        for lpzr__upsz in numba.parfors.parfor.internal_prange(riau__xwt):
            if bodo.libs.array_kernels.isna(gvcu__ogpva, lpzr__upsz):
                out_arr[lpzr__upsz] = ''
                bodo.libs.array_kernels.setna(out_arr, lpzr__upsz)
            else:
                out_arr[lpzr__upsz] = gvcu__ogpva[lpzr__upsz][start:stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(zmy__pux, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        riau__xwt = len(gvcu__ogpva)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(riau__xwt)
        for i in numba.parfors.parfor.internal_prange(riau__xwt):
            if bodo.libs.array_kernels.isna(gvcu__ogpva, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = gvcu__ogpva[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
            yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
            odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(zmy__pux, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                yidnv__zgyd, odjb__skzl)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        gvcu__ogpva = bodo.hiframes.pd_series_ext.get_series_data(S)
        odjb__skzl = bodo.hiframes.pd_series_ext.get_series_name(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        riau__xwt = len(gvcu__ogpva)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(riau__xwt)
        for i in numba.parfors.parfor.internal_prange(riau__xwt):
            if bodo.libs.array_kernels.isna(gvcu__ogpva, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = gvcu__ogpva[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, yidnv__zgyd,
            odjb__skzl)
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
    vnp__jdm, regex = _get_column_names_from_regex(pat, flags, 'extract')
    vfm__iew = len(vnp__jdm)
    if S_str.stype.data == bodo.dict_str_arr_type:
        hqy__apip = 'def impl(S_str, pat, flags=0, expand=True):\n'
        hqy__apip += '  S = S_str._obj\n'
        hqy__apip += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        hqy__apip += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        hqy__apip += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        hqy__apip += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {vfm__iew})
"""
        for i in range(vfm__iew):
            hqy__apip += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        hqy__apip = 'def impl(S_str, pat, flags=0, expand=True):\n'
        hqy__apip += '  regex = re.compile(pat, flags=flags)\n'
        hqy__apip += '  S = S_str._obj\n'
        hqy__apip += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        hqy__apip += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        hqy__apip += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        hqy__apip += '  numba.parfors.parfor.init_prange()\n'
        hqy__apip += '  n = len(str_arr)\n'
        for i in range(vfm__iew):
            hqy__apip += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        hqy__apip += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        hqy__apip += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(vfm__iew):
            hqy__apip += "          out_arr_{}[j] = ''\n".format(i)
            hqy__apip += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        hqy__apip += '      else:\n'
        hqy__apip += '          m = regex.search(str_arr[j])\n'
        hqy__apip += '          if m:\n'
        hqy__apip += '            g = m.groups()\n'
        for i in range(vfm__iew):
            hqy__apip += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        hqy__apip += '          else:\n'
        for i in range(vfm__iew):
            hqy__apip += "            out_arr_{}[j] = ''\n".format(i)
            hqy__apip += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        odjb__skzl = "'{}'".format(list(regex.groupindex.keys()).pop()) if len(
            regex.groupindex.keys()) > 0 else 'name'
        hqy__apip += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(odjb__skzl))
        zlj__afivt = {}
        exec(hqy__apip, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, zlj__afivt)
        impl = zlj__afivt['impl']
        return impl
    wbei__qxko = ', '.join('out_arr_{}'.format(i) for i in range(vfm__iew))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(hqy__apip, vnp__jdm,
        wbei__qxko, 'index', extra_globals={'get_utf8_size': get_utf8_size,
        're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    vnp__jdm, hnuhg__srp = _get_column_names_from_regex(pat, flags,
        'extractall')
    vfm__iew = len(vnp__jdm)
    vrbo__khua = isinstance(S_str.stype.index, StringIndexType)
    ajn__hnprz = vfm__iew > 1
    fzw__fsido = '_multi' if ajn__hnprz else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        hqy__apip = 'def impl(S_str, pat, flags=0):\n'
        hqy__apip += '  S = S_str._obj\n'
        hqy__apip += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        hqy__apip += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        hqy__apip += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        hqy__apip += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        hqy__apip += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        hqy__apip += '  regex = re.compile(pat, flags=flags)\n'
        hqy__apip += '  out_ind_arr, out_match_arr, out_arr_list = '
        hqy__apip += f'bodo.libs.dict_arr_ext.str_extractall{fzw__fsido}(\n'
        hqy__apip += f'arr, regex, {vfm__iew}, index_arr)\n'
        for i in range(vfm__iew):
            hqy__apip += f'  out_arr_{i} = out_arr_list[{i}]\n'
        hqy__apip += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        hqy__apip += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        hqy__apip = 'def impl(S_str, pat, flags=0):\n'
        hqy__apip += '  regex = re.compile(pat, flags=flags)\n'
        hqy__apip += '  S = S_str._obj\n'
        hqy__apip += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        hqy__apip += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        hqy__apip += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        hqy__apip += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        hqy__apip += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        hqy__apip += '  numba.parfors.parfor.init_prange()\n'
        hqy__apip += '  n = len(str_arr)\n'
        hqy__apip += '  out_n_l = [0]\n'
        for i in range(vfm__iew):
            hqy__apip += '  num_chars_{} = 0\n'.format(i)
        if vrbo__khua:
            hqy__apip += '  index_num_chars = 0\n'
        hqy__apip += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if vrbo__khua:
            hqy__apip += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        hqy__apip += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        hqy__apip += '          continue\n'
        hqy__apip += '      m = regex.findall(str_arr[i])\n'
        hqy__apip += '      out_n_l[0] += len(m)\n'
        for i in range(vfm__iew):
            hqy__apip += '      l_{} = 0\n'.format(i)
        hqy__apip += '      for s in m:\n'
        for i in range(vfm__iew):
            hqy__apip += '        l_{} += get_utf8_size(s{})\n'.format(i, 
                '[{}]'.format(i) if vfm__iew > 1 else '')
        for i in range(vfm__iew):
            hqy__apip += '      num_chars_{0} += l_{0}\n'.format(i)
        hqy__apip += (
            '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
            )
        for i in range(vfm__iew):
            hqy__apip += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if vrbo__khua:
            hqy__apip += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            hqy__apip += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
        hqy__apip += '  out_match_arr = np.empty(out_n, np.int64)\n'
        hqy__apip += '  out_ind = 0\n'
        hqy__apip += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        hqy__apip += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        hqy__apip += '          continue\n'
        hqy__apip += '      m = regex.findall(str_arr[j])\n'
        hqy__apip += '      for k, s in enumerate(m):\n'
        for i in range(vfm__iew):
            hqy__apip += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if vfm__iew > 1 else ''))
        hqy__apip += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        hqy__apip += (
            '        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)\n'
            )
        hqy__apip += '        out_ind += 1\n'
        hqy__apip += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        hqy__apip += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    wbei__qxko = ', '.join('out_arr_{}'.format(i) for i in range(vfm__iew))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(hqy__apip, vnp__jdm,
        wbei__qxko, 'out_index', extra_globals={'get_utf8_size':
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
    jquih__hfc = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    vnp__jdm = [jquih__hfc.get(1 + i, i) for i in range(regex.groups)]
    return vnp__jdm, regex


def create_str2str_methods_overload(func_name):
    irc__vrcy = func_name in ['lstrip', 'rstrip', 'strip']
    hqy__apip = f"""def f({'S_str, to_strip=None' if irc__vrcy else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if irc__vrcy else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if irc__vrcy else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    hqy__apip += f"""def _dict_impl({'S_str, to_strip=None' if irc__vrcy else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if irc__vrcy else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    zlj__afivt = {}
    exec(hqy__apip, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo.
        libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, zlj__afivt)
    jpd__kpyl = zlj__afivt['f']
    myngw__ixyaf = zlj__afivt['_dict_impl']
    if irc__vrcy:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return myngw__ixyaf
            return jpd__kpyl
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return myngw__ixyaf
            return jpd__kpyl
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    hqy__apip = 'def dict_impl(S_str):\n'
    hqy__apip += '    S = S_str._obj\n'
    hqy__apip += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    hqy__apip += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    hqy__apip += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    hqy__apip += f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n'
    hqy__apip += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    hqy__apip += 'def impl(S_str):\n'
    hqy__apip += '    S = S_str._obj\n'
    hqy__apip += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    hqy__apip += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    hqy__apip += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    hqy__apip += '    numba.parfors.parfor.init_prange()\n'
    hqy__apip += '    l = len(str_arr)\n'
    hqy__apip += '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    hqy__apip += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    hqy__apip += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    hqy__apip += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    hqy__apip += '        else:\n'
    hqy__apip += '            out_arr[i] = np.bool_(str_arr[i].{}())\n'.format(
        func_name)
    hqy__apip += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    hqy__apip += '      out_arr,index, name)\n'
    zlj__afivt = {}
    exec(hqy__apip, {'bodo': bodo, 'numba': numba, 'np': np}, zlj__afivt)
    impl = zlj__afivt['impl']
    jgld__ksiir = zlj__afivt['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return jgld__ksiir
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for pzkk__kyhs in bodo.hiframes.pd_series_ext.str2str_methods:
        gfb__fbhib = create_str2str_methods_overload(pzkk__kyhs)
        overload_method(SeriesStrMethodType, pzkk__kyhs, inline='always',
            no_unliteral=True)(gfb__fbhib)


def _install_str2bool_methods():
    for pzkk__kyhs in bodo.hiframes.pd_series_ext.str2bool_methods:
        gfb__fbhib = create_str2bool_methods_overload(pzkk__kyhs)
        overload_method(SeriesStrMethodType, pzkk__kyhs, inline='always',
            no_unliteral=True)(gfb__fbhib)


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
        odjb__skzl = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(odjb__skzl)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ncp__jvl = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, ncp__jvl)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        uyat__ybekj, = args
        bugj__djm = signature.return_type
        spfso__yrxov = cgutils.create_struct_proxy(bugj__djm)(context, builder)
        spfso__yrxov.obj = uyat__ybekj
        context.nrt.incref(builder, signature.args[0], uyat__ybekj)
        return spfso__yrxov._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        zmy__pux = bodo.hiframes.pd_series_ext.get_series_data(S)
        yidnv__zgyd = bodo.hiframes.pd_series_ext.get_series_index(S)
        odjb__skzl = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(zmy__pux),
            yidnv__zgyd, odjb__skzl)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for wvi__ernx in unsupported_cat_attrs:
        jgtos__iwqow = 'Series.cat.' + wvi__ernx
        overload_attribute(SeriesCatMethodType, wvi__ernx)(
            create_unsupported_overload(jgtos__iwqow))
    for wphqa__rdy in unsupported_cat_methods:
        jgtos__iwqow = 'Series.cat.' + wphqa__rdy
        overload_method(SeriesCatMethodType, wphqa__rdy)(
            create_unsupported_overload(jgtos__iwqow))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for wphqa__rdy in unsupported_str_methods:
        jgtos__iwqow = 'Series.str.' + wphqa__rdy
        overload_method(SeriesStrMethodType, wphqa__rdy)(
            create_unsupported_overload(jgtos__iwqow))


_install_strseries_unsupported()
