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
        ymjyc__xmqw = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(ymjyc__xmqw)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        uio__vaw = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, uio__vaw)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        hkf__uegv, = args
        yjii__wtygg = signature.return_type
        vgy__ygj = cgutils.create_struct_proxy(yjii__wtygg)(context, builder)
        vgy__ygj.obj = hkf__uegv
        context.nrt.incref(builder, signature.args[0], hkf__uegv)
        return vgy__ygj._getvalue()
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
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(dpff__yrnr)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(dpff__yrnr, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
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
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(dpff__yrnr,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(dpff__yrnr, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    jlcz__rcpm = S_str.stype.data
    if (jlcz__rcpm != string_array_split_view_type and not is_str_arr_type(
        jlcz__rcpm)) and not isinstance(jlcz__rcpm, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(jlcz__rcpm, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(dpff__yrnr, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_get_array_impl
    if jlcz__rcpm == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(dpff__yrnr)
            vxn__fgo = 0
            for viwhy__dpw in numba.parfors.parfor.internal_prange(n):
                fda__huhkq, fda__huhkq, ddnl__cgsaz = get_split_view_index(
                    dpff__yrnr, viwhy__dpw, i)
                vxn__fgo += ddnl__cgsaz
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, vxn__fgo)
            for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(n):
                zpnoy__fig, oyro__cci, ddnl__cgsaz = get_split_view_index(
                    dpff__yrnr, bqcmq__pfhwa, i)
                if zpnoy__fig == 0:
                    bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
                    srtd__grcwh = get_split_view_data_ptr(dpff__yrnr, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        bqcmq__pfhwa)
                    srtd__grcwh = get_split_view_data_ptr(dpff__yrnr, oyro__cci
                        )
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    bqcmq__pfhwa, srtd__grcwh, ddnl__cgsaz)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(dpff__yrnr, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(dpff__yrnr)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(dpff__yrnr, bqcmq__pfhwa
                ) or not len(dpff__yrnr[bqcmq__pfhwa]) > i >= -len(dpff__yrnr
                [bqcmq__pfhwa]):
                out_arr[bqcmq__pfhwa] = ''
                bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
            else:
                out_arr[bqcmq__pfhwa] = dpff__yrnr[bqcmq__pfhwa][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    jlcz__rcpm = S_str.stype.data
    if (jlcz__rcpm != string_array_split_view_type and jlcz__rcpm !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        jlcz__rcpm)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(lshcn__jmvg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(lshcn__jmvg, bqcmq__pfhwa):
                out_arr[bqcmq__pfhwa] = ''
                bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
            else:
                mjkh__cpmy = lshcn__jmvg[bqcmq__pfhwa]
                out_arr[bqcmq__pfhwa] = sep.join(mjkh__cpmy)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
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
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(dpff__yrnr, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            ccud__hyrd = re.compile(pat, flags)
            fhqvm__ofa = len(dpff__yrnr)
            out_arr = pre_alloc_string_array(fhqvm__ofa, -1)
            for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(fhqvm__ofa
                ):
                if bodo.libs.array_kernels.isna(dpff__yrnr, bqcmq__pfhwa):
                    out_arr[bqcmq__pfhwa] = ''
                    bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
                    continue
                out_arr[bqcmq__pfhwa] = ccud__hyrd.sub(repl, dpff__yrnr[
                    bqcmq__pfhwa])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        fhqvm__ofa = len(dpff__yrnr)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(fhqvm__ofa, -1)
        for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(fhqvm__ofa):
            if bodo.libs.array_kernels.isna(dpff__yrnr, bqcmq__pfhwa):
                out_arr[bqcmq__pfhwa] = ''
                bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
                continue
            out_arr[bqcmq__pfhwa] = dpff__yrnr[bqcmq__pfhwa].replace(pat, repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
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
    wreh__puf = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(hiwa__bfstp in pat) for hiwa__bfstp in wreh__puf])
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
    qid__qybau = re.IGNORECASE.value
    oygit__byn = 'def impl(\n'
    oygit__byn += '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n'
    oygit__byn += '):\n'
    oygit__byn += '  S = S_str._obj\n'
    oygit__byn += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    oygit__byn += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    oygit__byn += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    oygit__byn += '  l = len(arr)\n'
    oygit__byn += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                oygit__byn += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                oygit__byn += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            oygit__byn += """  get_search_regex(arr, case, False, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        oygit__byn += (
            '  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)\n'
            )
    else:
        oygit__byn += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            oygit__byn += '  upper_pat = pat.upper()\n'
        oygit__byn += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        oygit__byn += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        oygit__byn += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        oygit__byn += '      else: \n'
        if is_overload_true(case):
            oygit__byn += '          out_arr[i] = pat in arr[i]\n'
        else:
            oygit__byn += (
                '          out_arr[i] = upper_pat in arr[i].upper()\n')
    oygit__byn += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    wwcmy__rnki = {}
    exec(oygit__byn, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': qid__qybau, 'get_search_regex':
        get_search_regex}, wwcmy__rnki)
    impl = wwcmy__rnki['impl']
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
    qid__qybau = re.IGNORECASE.value
    oygit__byn = 'def impl(S_str, pat, case=True, flags=0, na=np.nan):\n'
    oygit__byn += '        S = S_str._obj\n'
    oygit__byn += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    oygit__byn += '        l = len(arr)\n'
    oygit__byn += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    oygit__byn += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if not is_regex_unsupported(pat) and flags == 0:
        oygit__byn += (
            '        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        oygit__byn += """        get_search_regex(arr, case, True, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        oygit__byn += """        out_arr = bodo.libs.dict_arr_ext.str_match(arr, pat, case, flags, na)
"""
    else:
        oygit__byn += (
            '        out_arr = series_match_regex(S, pat, case, flags, na)\n')
    oygit__byn += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    wwcmy__rnki = {}
    exec(oygit__byn, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': qid__qybau, 'get_search_regex':
        get_search_regex}, wwcmy__rnki)
    impl = wwcmy__rnki['impl']
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
    oygit__byn = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    oygit__byn += '  S = S_str._obj\n'
    oygit__byn += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    oygit__byn += '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    oygit__byn += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    oygit__byn += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        oygit__byn += f"""  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})
"""
    if S_str.stype.data == bodo.dict_str_arr_type and all(xbh__tdqns ==
        bodo.dict_str_arr_type for xbh__tdqns in others.data):
        gox__zpap = ', '.join(f'data{i}' for i in range(len(others.columns)))
        oygit__byn += (
            f'  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {gox__zpap}), sep)\n'
            )
    else:
        zkl__rbrzj = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] +
            [f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len
            (others.columns))])
        oygit__byn += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        oygit__byn += '  numba.parfors.parfor.init_prange()\n'
        oygit__byn += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        oygit__byn += f'      if {zkl__rbrzj}:\n'
        oygit__byn += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        oygit__byn += '          continue\n'
        wdrbz__wxyf = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range(
            len(others.columns))])
        ahvz__gjmrh = "''" if is_overload_none(sep) else 'sep'
        oygit__byn += (
            f'      out_arr[i] = {ahvz__gjmrh}.join([{wdrbz__wxyf}])\n')
    oygit__byn += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    wwcmy__rnki = {}
    exec(oygit__byn, {'bodo': bodo, 'numba': numba}, wwcmy__rnki)
    impl = wwcmy__rnki['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(dpff__yrnr, pat, flags)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        ccud__hyrd = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        fhqvm__ofa = len(lshcn__jmvg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(fhqvm__ofa, np.int64)
        for i in numba.parfors.parfor.internal_prange(fhqvm__ofa):
            if bodo.libs.array_kernels.isna(lshcn__jmvg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(ccud__hyrd, lshcn__jmvg[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
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
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(dpff__yrnr, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        fhqvm__ofa = len(lshcn__jmvg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(fhqvm__ofa, np.int64)
        for i in numba.parfors.parfor.internal_prange(fhqvm__ofa):
            if bodo.libs.array_kernels.isna(lshcn__jmvg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = lshcn__jmvg[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
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
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(dpff__yrnr, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        fhqvm__ofa = len(lshcn__jmvg)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(fhqvm__ofa, np.int64)
        for i in numba.parfors.parfor.internal_prange(fhqvm__ofa):
            if bodo.libs.array_kernels.isna(lshcn__jmvg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = lshcn__jmvg[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
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
        lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        fhqvm__ofa = len(lshcn__jmvg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(fhqvm__ofa, -1)
        for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(fhqvm__ofa):
            if bodo.libs.array_kernels.isna(lshcn__jmvg, bqcmq__pfhwa):
                bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
            else:
                if stop is not None:
                    ilg__lit = lshcn__jmvg[bqcmq__pfhwa][stop:]
                else:
                    ilg__lit = ''
                out_arr[bqcmq__pfhwa] = lshcn__jmvg[bqcmq__pfhwa][:start
                    ] + repl + ilg__lit
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
                hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
                ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(dpff__yrnr,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    hhvlv__gba, ymjyc__xmqw)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            fhqvm__ofa = len(lshcn__jmvg)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(fhqvm__ofa,
                -1)
            for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(fhqvm__ofa
                ):
                if bodo.libs.array_kernels.isna(lshcn__jmvg, bqcmq__pfhwa):
                    bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
                else:
                    out_arr[bqcmq__pfhwa] = lshcn__jmvg[bqcmq__pfhwa] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return impl
    elif is_overload_constant_list(repeats):
        kyfbb__jbdgj = get_overload_const_list(repeats)
        dxdku__tzyf = all([isinstance(prbl__jddhc, int) for prbl__jddhc in
            kyfbb__jbdgj])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        dxdku__tzyf = True
    else:
        dxdku__tzyf = False
    if dxdku__tzyf:

        def impl(S_str, repeats):
            S = S_str._obj
            lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            kcxe__fxliu = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            fhqvm__ofa = len(lshcn__jmvg)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(fhqvm__ofa,
                -1)
            for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(fhqvm__ofa
                ):
                if bodo.libs.array_kernels.isna(lshcn__jmvg, bqcmq__pfhwa):
                    bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
                else:
                    out_arr[bqcmq__pfhwa] = lshcn__jmvg[bqcmq__pfhwa
                        ] * kcxe__fxliu[bqcmq__pfhwa]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    oygit__byn = f"""def dict_impl(S_str, width, fillchar=' '):
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
    wwcmy__rnki = {}
    nydnx__ffaah = {'bodo': bodo, 'numba': numba}
    exec(oygit__byn, nydnx__ffaah, wwcmy__rnki)
    impl = wwcmy__rnki['impl']
    whg__mland = wwcmy__rnki['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return whg__mland
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for mghbt__gay in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(mghbt__gay)
        overload_method(SeriesStrMethodType, mghbt__gay, inline='always',
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
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(dpff__yrnr,
                    width, fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(dpff__yrnr,
                    width, fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(dpff__yrnr,
                    width, fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        fhqvm__ofa = len(lshcn__jmvg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(fhqvm__ofa, -1)
        for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(fhqvm__ofa):
            if bodo.libs.array_kernels.isna(lshcn__jmvg, bqcmq__pfhwa):
                out_arr[bqcmq__pfhwa] = ''
                bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
            elif side == 'left':
                out_arr[bqcmq__pfhwa] = lshcn__jmvg[bqcmq__pfhwa].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[bqcmq__pfhwa] = lshcn__jmvg[bqcmq__pfhwa].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[bqcmq__pfhwa] = lshcn__jmvg[bqcmq__pfhwa].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(dpff__yrnr, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        fhqvm__ofa = len(lshcn__jmvg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(fhqvm__ofa, -1)
        for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(fhqvm__ofa):
            if bodo.libs.array_kernels.isna(lshcn__jmvg, bqcmq__pfhwa):
                out_arr[bqcmq__pfhwa] = ''
                bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
            else:
                out_arr[bqcmq__pfhwa] = lshcn__jmvg[bqcmq__pfhwa].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
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
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(dpff__yrnr, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        fhqvm__ofa = len(lshcn__jmvg)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(fhqvm__ofa, -1)
        for bqcmq__pfhwa in numba.parfors.parfor.internal_prange(fhqvm__ofa):
            if bodo.libs.array_kernels.isna(lshcn__jmvg, bqcmq__pfhwa):
                out_arr[bqcmq__pfhwa] = ''
                bodo.libs.array_kernels.setna(out_arr, bqcmq__pfhwa)
            else:
                out_arr[bqcmq__pfhwa] = lshcn__jmvg[bqcmq__pfhwa][start:
                    stop:step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(dpff__yrnr, pat, na
                )
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        fhqvm__ofa = len(lshcn__jmvg)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(fhqvm__ofa)
        for i in numba.parfors.parfor.internal_prange(fhqvm__ofa):
            if bodo.libs.array_kernels.isna(lshcn__jmvg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = lshcn__jmvg[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
            ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(dpff__yrnr, pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hhvlv__gba, ymjyc__xmqw)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        lshcn__jmvg = bodo.hiframes.pd_series_ext.get_series_data(S)
        ymjyc__xmqw = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        fhqvm__ofa = len(lshcn__jmvg)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(fhqvm__ofa)
        for i in numba.parfors.parfor.internal_prange(fhqvm__ofa):
            if bodo.libs.array_kernels.isna(lshcn__jmvg, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = lshcn__jmvg[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, hhvlv__gba,
            ymjyc__xmqw)
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
    lpwje__unph, regex = _get_column_names_from_regex(pat, flags, 'extract')
    kipbt__hfc = len(lpwje__unph)
    if S_str.stype.data == bodo.dict_str_arr_type:
        oygit__byn = 'def impl(S_str, pat, flags=0, expand=True):\n'
        oygit__byn += '  S = S_str._obj\n'
        oygit__byn += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        oygit__byn += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        oygit__byn += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        oygit__byn += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {kipbt__hfc})
"""
        for i in range(kipbt__hfc):
            oygit__byn += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        oygit__byn = 'def impl(S_str, pat, flags=0, expand=True):\n'
        oygit__byn += '  regex = re.compile(pat, flags=flags)\n'
        oygit__byn += '  S = S_str._obj\n'
        oygit__byn += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        oygit__byn += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        oygit__byn += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        oygit__byn += '  numba.parfors.parfor.init_prange()\n'
        oygit__byn += '  n = len(str_arr)\n'
        for i in range(kipbt__hfc):
            oygit__byn += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        oygit__byn += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        oygit__byn += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(kipbt__hfc):
            oygit__byn += "          out_arr_{}[j] = ''\n".format(i)
            oygit__byn += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        oygit__byn += '      else:\n'
        oygit__byn += '          m = regex.search(str_arr[j])\n'
        oygit__byn += '          if m:\n'
        oygit__byn += '            g = m.groups()\n'
        for i in range(kipbt__hfc):
            oygit__byn += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        oygit__byn += '          else:\n'
        for i in range(kipbt__hfc):
            oygit__byn += "            out_arr_{}[j] = ''\n".format(i)
            oygit__byn += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        ymjyc__xmqw = "'{}'".format(list(regex.groupindex.keys()).pop()
            ) if len(regex.groupindex.keys()) > 0 else 'name'
        oygit__byn += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(ymjyc__xmqw))
        wwcmy__rnki = {}
        exec(oygit__byn, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, wwcmy__rnki)
        impl = wwcmy__rnki['impl']
        return impl
    yipbi__hbqe = ', '.join('out_arr_{}'.format(i) for i in range(kipbt__hfc))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(oygit__byn,
        lpwje__unph, yipbi__hbqe, 'index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    lpwje__unph, fda__huhkq = _get_column_names_from_regex(pat, flags,
        'extractall')
    kipbt__hfc = len(lpwje__unph)
    nvdxy__qho = isinstance(S_str.stype.index, StringIndexType)
    qpua__mpz = kipbt__hfc > 1
    ikfz__qwywm = '_multi' if qpua__mpz else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        oygit__byn = 'def impl(S_str, pat, flags=0):\n'
        oygit__byn += '  S = S_str._obj\n'
        oygit__byn += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        oygit__byn += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        oygit__byn += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        oygit__byn += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        oygit__byn += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        oygit__byn += '  regex = re.compile(pat, flags=flags)\n'
        oygit__byn += '  out_ind_arr, out_match_arr, out_arr_list = '
        oygit__byn += f'bodo.libs.dict_arr_ext.str_extractall{ikfz__qwywm}(\n'
        oygit__byn += f'arr, regex, {kipbt__hfc}, index_arr)\n'
        for i in range(kipbt__hfc):
            oygit__byn += f'  out_arr_{i} = out_arr_list[{i}]\n'
        oygit__byn += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        oygit__byn += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        oygit__byn = 'def impl(S_str, pat, flags=0):\n'
        oygit__byn += '  regex = re.compile(pat, flags=flags)\n'
        oygit__byn += '  S = S_str._obj\n'
        oygit__byn += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        oygit__byn += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        oygit__byn += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        oygit__byn += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        oygit__byn += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        oygit__byn += '  numba.parfors.parfor.init_prange()\n'
        oygit__byn += '  n = len(str_arr)\n'
        oygit__byn += '  out_n_l = [0]\n'
        for i in range(kipbt__hfc):
            oygit__byn += '  num_chars_{} = 0\n'.format(i)
        if nvdxy__qho:
            oygit__byn += '  index_num_chars = 0\n'
        oygit__byn += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if nvdxy__qho:
            oygit__byn += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        oygit__byn += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        oygit__byn += '          continue\n'
        oygit__byn += '      m = regex.findall(str_arr[i])\n'
        oygit__byn += '      out_n_l[0] += len(m)\n'
        for i in range(kipbt__hfc):
            oygit__byn += '      l_{} = 0\n'.format(i)
        oygit__byn += '      for s in m:\n'
        for i in range(kipbt__hfc):
            oygit__byn += '        l_{} += get_utf8_size(s{})\n'.format(i, 
                '[{}]'.format(i) if kipbt__hfc > 1 else '')
        for i in range(kipbt__hfc):
            oygit__byn += '      num_chars_{0} += l_{0}\n'.format(i)
        oygit__byn += (
            '  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)\n'
            )
        for i in range(kipbt__hfc):
            oygit__byn += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if nvdxy__qho:
            oygit__byn += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            oygit__byn += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
        oygit__byn += '  out_match_arr = np.empty(out_n, np.int64)\n'
        oygit__byn += '  out_ind = 0\n'
        oygit__byn += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        oygit__byn += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        oygit__byn += '          continue\n'
        oygit__byn += '      m = regex.findall(str_arr[j])\n'
        oygit__byn += '      for k, s in enumerate(m):\n'
        for i in range(kipbt__hfc):
            oygit__byn += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if kipbt__hfc > 1 else ''))
        oygit__byn += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        oygit__byn += """        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)
"""
        oygit__byn += '        out_ind += 1\n'
        oygit__byn += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        oygit__byn += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    yipbi__hbqe = ', '.join('out_arr_{}'.format(i) for i in range(kipbt__hfc))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(oygit__byn,
        lpwje__unph, yipbi__hbqe, 'out_index', extra_globals={
        'get_utf8_size': get_utf8_size, 're': re})
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
    mmqvu__ivq = dict(zip(regex.groupindex.values(), regex.groupindex.keys()))
    lpwje__unph = [mmqvu__ivq.get(1 + i, i) for i in range(regex.groups)]
    return lpwje__unph, regex


def create_str2str_methods_overload(func_name):
    ogxx__kgvvl = func_name in ['lstrip', 'rstrip', 'strip']
    oygit__byn = f"""def f({'S_str, to_strip=None' if ogxx__kgvvl else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if ogxx__kgvvl else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if ogxx__kgvvl else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    oygit__byn += f"""def _dict_impl({'S_str, to_strip=None' if ogxx__kgvvl else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if ogxx__kgvvl else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    wwcmy__rnki = {}
    exec(oygit__byn, {'bodo': bodo, 'numba': numba, 'num_total_chars': bodo
        .libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, wwcmy__rnki)
    hpz__zzlz = wwcmy__rnki['f']
    xrarv__udse = wwcmy__rnki['_dict_impl']
    if ogxx__kgvvl:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return xrarv__udse
            return hpz__zzlz
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return xrarv__udse
            return hpz__zzlz
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    oygit__byn = 'def dict_impl(S_str):\n'
    oygit__byn += '    S = S_str._obj\n'
    oygit__byn += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    oygit__byn += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    oygit__byn += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    oygit__byn += (
        f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n')
    oygit__byn += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    oygit__byn += 'def impl(S_str):\n'
    oygit__byn += '    S = S_str._obj\n'
    oygit__byn += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    oygit__byn += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    oygit__byn += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    oygit__byn += '    numba.parfors.parfor.init_prange()\n'
    oygit__byn += '    l = len(str_arr)\n'
    oygit__byn += '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    oygit__byn += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    oygit__byn += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    oygit__byn += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    oygit__byn += '        else:\n'
    oygit__byn += ('            out_arr[i] = np.bool_(str_arr[i].{}())\n'.
        format(func_name))
    oygit__byn += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    oygit__byn += '      out_arr,index, name)\n'
    wwcmy__rnki = {}
    exec(oygit__byn, {'bodo': bodo, 'numba': numba, 'np': np}, wwcmy__rnki)
    impl = wwcmy__rnki['impl']
    whg__mland = wwcmy__rnki['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return whg__mland
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for hsji__yxuw in bodo.hiframes.pd_series_ext.str2str_methods:
        tcum__mpdno = create_str2str_methods_overload(hsji__yxuw)
        overload_method(SeriesStrMethodType, hsji__yxuw, inline='always',
            no_unliteral=True)(tcum__mpdno)


def _install_str2bool_methods():
    for hsji__yxuw in bodo.hiframes.pd_series_ext.str2bool_methods:
        tcum__mpdno = create_str2bool_methods_overload(hsji__yxuw)
        overload_method(SeriesStrMethodType, hsji__yxuw, inline='always',
            no_unliteral=True)(tcum__mpdno)


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
        ymjyc__xmqw = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(ymjyc__xmqw)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        uio__vaw = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, uio__vaw)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        hkf__uegv, = args
        ldo__lhe = signature.return_type
        nmw__vgb = cgutils.create_struct_proxy(ldo__lhe)(context, builder)
        nmw__vgb.obj = hkf__uegv
        context.nrt.incref(builder, signature.args[0], hkf__uegv)
        return nmw__vgb._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        dpff__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
        hhvlv__gba = bodo.hiframes.pd_series_ext.get_series_index(S)
        ymjyc__xmqw = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(dpff__yrnr),
            hhvlv__gba, ymjyc__xmqw)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for ctd__ycut in unsupported_cat_attrs:
        frre__esd = 'Series.cat.' + ctd__ycut
        overload_attribute(SeriesCatMethodType, ctd__ycut)(
            create_unsupported_overload(frre__esd))
    for sxv__lshd in unsupported_cat_methods:
        frre__esd = 'Series.cat.' + sxv__lshd
        overload_method(SeriesCatMethodType, sxv__lshd)(
            create_unsupported_overload(frre__esd))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for sxv__lshd in unsupported_str_methods:
        frre__esd = 'Series.str.' + sxv__lshd
        overload_method(SeriesStrMethodType, sxv__lshd)(
            create_unsupported_overload(frre__esd))


_install_strseries_unsupported()
