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
        zjp__sol = 'SeriesStrMethodType({})'.format(stype)
        super(SeriesStrMethodType, self).__init__(zjp__sol)


@register_model(SeriesStrMethodType)
class SeriesStrModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ddc__xltp = [('obj', fe_type.stype)]
        super(SeriesStrModel, self).__init__(dmm, fe_type, ddc__xltp)


make_attribute_wrapper(SeriesStrMethodType, 'obj', '_obj')


@intrinsic
def init_series_str_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        zjl__odgdq, = args
        webbl__qwfy = signature.return_type
        dpqq__nkns = cgutils.create_struct_proxy(webbl__qwfy)(context, builder)
        dpqq__nkns.obj = zjl__odgdq
        context.nrt.incref(builder, signature.args[0], zjl__odgdq)
        return dpqq__nkns._getvalue()
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
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_len(jmaap__qmubh)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_len_dict_impl

    def impl(S_str):
        S = S_str._obj
        jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.array_kernels.get_arr_lens(jmaap__qmubh, False)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
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
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.hiframes.split_impl.compute_split_view(jmaap__qmubh,
                pat)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_split_view_impl

    def _str_split_impl(S_str, pat=None, n=-1, expand=False):
        S = S_str._obj
        jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        out_arr = bodo.libs.str_ext.str_split(jmaap__qmubh, pat, n)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
    return _str_split_impl


@overload_method(SeriesStrMethodType, 'get', no_unliteral=True)
def overload_str_method_get(S_str, i):
    bbltf__fyr = S_str.stype.data
    if (bbltf__fyr != string_array_split_view_type and not is_str_arr_type(
        bbltf__fyr)) and not isinstance(bbltf__fyr, ArrayItemArrayType):
        raise_bodo_error(
            'Series.str.get(): only supports input type of Series(array(item)) and Series(str)'
            )
    int_arg_check('get', 'i', i)
    if isinstance(bbltf__fyr, ArrayItemArrayType):

        def _str_get_array_impl(S_str, i):
            S = S_str._obj
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.array_kernels.get(jmaap__qmubh, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_get_array_impl
    if bbltf__fyr == string_array_split_view_type:

        def _str_get_split_impl(S_str, i):
            S = S_str._obj
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            n = len(jmaap__qmubh)
            fwekq__hgfe = 0
            for ytcwq__qpop in numba.parfors.parfor.internal_prange(n):
                sfz__lkf, sfz__lkf, airaw__swno = get_split_view_index(
                    jmaap__qmubh, ytcwq__qpop, i)
                fwekq__hgfe += airaw__swno
            numba.parfors.parfor.init_prange()
            out_arr = pre_alloc_string_array(n, fwekq__hgfe)
            for gciot__vklca in numba.parfors.parfor.internal_prange(n):
                iusdu__mdgq, ool__bqneb, airaw__swno = get_split_view_index(
                    jmaap__qmubh, gciot__vklca, i)
                if iusdu__mdgq == 0:
                    bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
                    sqmf__vsvyr = get_split_view_data_ptr(jmaap__qmubh, 0)
                else:
                    bodo.libs.str_arr_ext.str_arr_set_not_na(out_arr,
                        gciot__vklca)
                    sqmf__vsvyr = get_split_view_data_ptr(jmaap__qmubh,
                        ool__bqneb)
                bodo.libs.str_arr_ext.setitem_str_arr_ptr(out_arr,
                    gciot__vklca, sqmf__vsvyr, airaw__swno)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_get_split_impl
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_get_dict_impl(S_str, i):
            S = S_str._obj
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_get(jmaap__qmubh, i)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_get_dict_impl

    def _str_get_impl(S_str, i):
        S = S_str._obj
        jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(jmaap__qmubh)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(n, -1)
        for gciot__vklca in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(jmaap__qmubh, gciot__vklca
                ) or not len(jmaap__qmubh[gciot__vklca]) > i >= -len(
                jmaap__qmubh[gciot__vklca]):
                out_arr[gciot__vklca] = ''
                bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
            else:
                out_arr[gciot__vklca] = jmaap__qmubh[gciot__vklca][i]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
    return _str_get_impl


@overload_method(SeriesStrMethodType, 'join', inline='always', no_unliteral
    =True)
def overload_str_method_join(S_str, sep):
    bbltf__fyr = S_str.stype.data
    if (bbltf__fyr != string_array_split_view_type and bbltf__fyr !=
        ArrayItemArrayType(string_array_type) and not is_str_arr_type(
        bbltf__fyr)):
        raise_bodo_error(
            'Series.str.join(): only supports input type of Series(list(str)) and Series(str)'
            )
    str_arg_check('join', 'sep', sep)

    def impl(S_str, sep):
        S = S_str._obj
        fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        n = len(fez__pwhat)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
        for gciot__vklca in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(fez__pwhat, gciot__vklca):
                out_arr[gciot__vklca] = ''
                bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
            else:
                tnlcx__hegp = fez__pwhat[gciot__vklca]
                out_arr[gciot__vklca] = sep.join(tnlcx__hegp)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
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
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_replace(jmaap__qmubh, pat,
                repl, flags, regex)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_replace_dict_impl
    if is_overload_true(regex):

        def _str_replace_regex_impl(S_str, pat, repl, n=-1, case=None,
            flags=0, regex=True):
            S = S_str._obj
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            numba.parfors.parfor.init_prange()
            wdx__dlbe = re.compile(pat, flags)
            xir__sephv = len(jmaap__qmubh)
            out_arr = pre_alloc_string_array(xir__sephv, -1)
            for gciot__vklca in numba.parfors.parfor.internal_prange(xir__sephv
                ):
                if bodo.libs.array_kernels.isna(jmaap__qmubh, gciot__vklca):
                    out_arr[gciot__vklca] = ''
                    bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
                    continue
                out_arr[gciot__vklca] = wdx__dlbe.sub(repl, jmaap__qmubh[
                    gciot__vklca])
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_replace_regex_impl
    if not is_overload_false(regex):
        raise BodoError('Series.str.replace(): regex argument should be bool')

    def _str_replace_noregex_impl(S_str, pat, repl, n=-1, case=None, flags=
        0, regex=True):
        S = S_str._obj
        jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        xir__sephv = len(jmaap__qmubh)
        numba.parfors.parfor.init_prange()
        out_arr = pre_alloc_string_array(xir__sephv, -1)
        for gciot__vklca in numba.parfors.parfor.internal_prange(xir__sephv):
            if bodo.libs.array_kernels.isna(jmaap__qmubh, gciot__vklca):
                out_arr[gciot__vklca] = ''
                bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
                continue
            out_arr[gciot__vklca] = jmaap__qmubh[gciot__vklca].replace(pat,
                repl)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
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
    xor__cegp = ['(?a', '(?i', '(?L', '(?m', '(?s', '(?u', '(?x', '(?#']
    if is_overload_constant_str(pat):
        if isinstance(pat, types.StringLiteral):
            pat = pat.literal_value
        return any([(fkseo__qheec in pat) for fkseo__qheec in xor__cegp])
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
    rzo__fvnu = re.IGNORECASE.value
    ijct__nmihz = 'def impl(\n'
    ijct__nmihz += (
        '    S_str, pat, case=True, flags=0, na=np.nan, regex=True\n')
    ijct__nmihz += '):\n'
    ijct__nmihz += '  S = S_str._obj\n'
    ijct__nmihz += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ijct__nmihz += (
        '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ijct__nmihz += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    ijct__nmihz += '  l = len(arr)\n'
    ijct__nmihz += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    if is_overload_true(regex):
        if is_regex_unsupported(pat) or flags:
            if S_str.stype.data == bodo.dict_str_arr_type:
                ijct__nmihz += """  out_arr = bodo.libs.dict_arr_ext.str_series_contains_regex(arr, pat, case, flags, na, regex)
"""
            else:
                ijct__nmihz += """  out_arr = bodo.hiframes.series_str_impl.series_contains_regex(S, pat, case, flags, na, regex)
"""
        else:
            ijct__nmihz += """  get_search_regex(arr, case, False, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        ijct__nmihz += """  out_arr = bodo.libs.dict_arr_ext.str_contains_non_regex(arr, pat, case)
"""
    else:
        ijct__nmihz += '  numba.parfors.parfor.init_prange()\n'
        if is_overload_false(case):
            ijct__nmihz += '  upper_pat = pat.upper()\n'
        ijct__nmihz += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        ijct__nmihz += '      if bodo.libs.array_kernels.isna(arr, i):\n'
        ijct__nmihz += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        ijct__nmihz += '      else: \n'
        if is_overload_true(case):
            ijct__nmihz += '          out_arr[i] = pat in arr[i]\n'
        else:
            ijct__nmihz += (
                '          out_arr[i] = upper_pat in arr[i].upper()\n')
    ijct__nmihz += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    ggtfl__lxtcm = {}
    exec(ijct__nmihz, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': rzo__fvnu, 'get_search_regex':
        get_search_regex}, ggtfl__lxtcm)
    impl = ggtfl__lxtcm['impl']
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
    rzo__fvnu = re.IGNORECASE.value
    ijct__nmihz = 'def impl(S_str, pat, case=True, flags=0, na=np.nan):\n'
    ijct__nmihz += '        S = S_str._obj\n'
    ijct__nmihz += (
        '        arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ijct__nmihz += '        l = len(arr)\n'
    ijct__nmihz += (
        '        index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ijct__nmihz += (
        '        name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if not is_regex_unsupported(pat) and flags == 0:
        ijct__nmihz += (
            '        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n')
        ijct__nmihz += """        get_search_regex(arr, case, True, bodo.libs.str_ext.unicode_to_utf8(pat), out_arr)
"""
    elif S_str.stype.data == bodo.dict_str_arr_type:
        ijct__nmihz += """        out_arr = bodo.libs.dict_arr_ext.str_match(arr, pat, case, flags, na)
"""
    else:
        ijct__nmihz += (
            '        out_arr = series_match_regex(S, pat, case, flags, na)\n')
    ijct__nmihz += (
        '        return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    ggtfl__lxtcm = {}
    exec(ijct__nmihz, {'re': re, 'bodo': bodo, 'numba': numba, 'np': np,
        're_ignorecase_value': rzo__fvnu, 'get_search_regex':
        get_search_regex}, ggtfl__lxtcm)
    impl = ggtfl__lxtcm['impl']
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
    ijct__nmihz = (
        "def impl(S_str, others=None, sep=None, na_rep=None, join='left'):\n")
    ijct__nmihz += '  S = S_str._obj\n'
    ijct__nmihz += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ijct__nmihz += (
        '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ijct__nmihz += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    ijct__nmihz += '  l = len(arr)\n'
    for i in range(len(others.columns)):
        ijct__nmihz += f"""  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(others, {i})
"""
    if S_str.stype.data == bodo.dict_str_arr_type and all(cyoa__yks == bodo
        .dict_str_arr_type for cyoa__yks in others.data):
        qeymp__ojptr = ', '.join(f'data{i}' for i in range(len(others.columns))
            )
        ijct__nmihz += f"""  out_arr = bodo.libs.dict_arr_ext.cat_dict_str((arr, {qeymp__ojptr}), sep)
"""
    else:
        zai__pcvu = ' or '.join(['bodo.libs.array_kernels.isna(arr, i)'] +
            [f'bodo.libs.array_kernels.isna(data{i}, i)' for i in range(len
            (others.columns))])
        ijct__nmihz += (
            '  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)\n'
            )
        ijct__nmihz += '  numba.parfors.parfor.init_prange()\n'
        ijct__nmihz += '  for i in numba.parfors.parfor.internal_prange(l):\n'
        ijct__nmihz += f'      if {zai__pcvu}:\n'
        ijct__nmihz += '          bodo.libs.array_kernels.setna(out_arr, i)\n'
        ijct__nmihz += '          continue\n'
        eytnp__ydurn = ', '.join(['arr[i]'] + [f'data{i}[i]' for i in range
            (len(others.columns))])
        vdzgl__yvh = "''" if is_overload_none(sep) else 'sep'
        ijct__nmihz += (
            f'      out_arr[i] = {vdzgl__yvh}.join([{eytnp__ydurn}])\n')
    ijct__nmihz += (
        '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    ggtfl__lxtcm = {}
    exec(ijct__nmihz, {'bodo': bodo, 'numba': numba}, ggtfl__lxtcm)
    impl = ggtfl__lxtcm['impl']
    return impl


@overload_method(SeriesStrMethodType, 'count', inline='always',
    no_unliteral=True)
def overload_str_method_count(S_str, pat, flags=0):
    str_arg_check('count', 'pat', pat)
    int_arg_check('count', 'flags', flags)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_count_dict_impl(S_str, pat, flags=0):
            S = S_str._obj
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_count(jmaap__qmubh, pat, flags
                )
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_count_dict_impl

    def impl(S_str, pat, flags=0):
        S = S_str._obj
        fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        wdx__dlbe = re.compile(pat, flags)
        numba.parfors.parfor.init_prange()
        xir__sephv = len(fez__pwhat)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(xir__sephv, np.int64)
        for i in numba.parfors.parfor.internal_prange(xir__sephv):
            if bodo.libs.array_kernels.isna(fez__pwhat, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = str_findall_count(wdx__dlbe, fez__pwhat[i])
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
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
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_find(jmaap__qmubh, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_find_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xir__sephv = len(fez__pwhat)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(xir__sephv, np.int64)
        for i in numba.parfors.parfor.internal_prange(xir__sephv):
            if bodo.libs.array_kernels.isna(fez__pwhat, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = fez__pwhat[i].find(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
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
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_rfind(jmaap__qmubh, sub,
                start, end)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_rfind_dict_impl

    def impl(S_str, sub, start=0, end=None):
        S = S_str._obj
        fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xir__sephv = len(fez__pwhat)
        out_arr = bodo.libs.int_arr_ext.alloc_int_array(xir__sephv, np.int64)
        for i in numba.parfors.parfor.internal_prange(xir__sephv):
            if bodo.libs.array_kernels.isna(fez__pwhat, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = fez__pwhat[i].rfind(sub, start, end)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
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
        fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xir__sephv = len(fez__pwhat)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xir__sephv, -1)
        for gciot__vklca in numba.parfors.parfor.internal_prange(xir__sephv):
            if bodo.libs.array_kernels.isna(fez__pwhat, gciot__vklca):
                bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
            else:
                if stop is not None:
                    yppbe__nidj = fez__pwhat[gciot__vklca][stop:]
                else:
                    yppbe__nidj = ''
                out_arr[gciot__vklca] = fez__pwhat[gciot__vklca][:start
                    ] + repl + yppbe__nidj
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
    return impl


@overload_method(SeriesStrMethodType, 'repeat', inline='always',
    no_unliteral=True)
def overload_str_method_repeat(S_str, repeats):
    if isinstance(repeats, types.Integer) or is_overload_constant_int(repeats):
        if S_str.stype.data == bodo.dict_str_arr_type:

            def _str_repeat_int_dict_impl(S_str, repeats):
                S = S_str._obj
                jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
                thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
                zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
                out_arr = bodo.libs.dict_arr_ext.str_repeat_int(jmaap__qmubh,
                    repeats)
                return bodo.hiframes.pd_series_ext.init_series(out_arr,
                    thm__eoku, zjp__sol)
            return _str_repeat_int_dict_impl

        def impl(S_str, repeats):
            S = S_str._obj
            fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            numba.parfors.parfor.init_prange()
            xir__sephv = len(fez__pwhat)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xir__sephv,
                -1)
            for gciot__vklca in numba.parfors.parfor.internal_prange(xir__sephv
                ):
                if bodo.libs.array_kernels.isna(fez__pwhat, gciot__vklca):
                    bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
                else:
                    out_arr[gciot__vklca] = fez__pwhat[gciot__vklca] * repeats
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return impl
    elif is_overload_constant_list(repeats):
        doqqw__ghbxh = get_overload_const_list(repeats)
        duun__hbujr = all([isinstance(trq__wkw, int) for trq__wkw in
            doqqw__ghbxh])
    elif is_list_like_index_type(repeats) and isinstance(repeats.dtype,
        types.Integer):
        duun__hbujr = True
    else:
        duun__hbujr = False
    if duun__hbujr:

        def impl(S_str, repeats):
            S = S_str._obj
            fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            vdap__hmi = bodo.utils.conversion.coerce_to_array(repeats)
            numba.parfors.parfor.init_prange()
            xir__sephv = len(fez__pwhat)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xir__sephv,
                -1)
            for gciot__vklca in numba.parfors.parfor.internal_prange(xir__sephv
                ):
                if bodo.libs.array_kernels.isna(fez__pwhat, gciot__vklca):
                    bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
                else:
                    out_arr[gciot__vklca] = fez__pwhat[gciot__vklca
                        ] * vdap__hmi[gciot__vklca]
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return impl
    else:
        raise BodoError(
            'Series.str.repeat(): repeats argument must either be an integer or a sequence of integers'
            )


def create_ljust_rjust_center_overload(func_name):
    ijct__nmihz = f"""def dict_impl(S_str, width, fillchar=' '):
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
    ggtfl__lxtcm = {}
    hdq__rlqv = {'bodo': bodo, 'numba': numba}
    exec(ijct__nmihz, hdq__rlqv, ggtfl__lxtcm)
    impl = ggtfl__lxtcm['impl']
    lku__mqnb = ggtfl__lxtcm['dict_impl']

    def overload_ljust_rjust_center_method(S_str, width, fillchar=' '):
        common_validate_padding(func_name, width, fillchar)
        if S_str.stype.data == bodo.dict_str_arr_type:
            return lku__mqnb
        return impl
    return overload_ljust_rjust_center_method


def _install_ljust_rjust_center():
    for txpnq__lwqw in ['ljust', 'rjust', 'center']:
        impl = create_ljust_rjust_center_overload(txpnq__lwqw)
        overload_method(SeriesStrMethodType, txpnq__lwqw, inline='always',
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
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            if side == 'left':
                out_arr = bodo.libs.dict_arr_ext.str_rjust(jmaap__qmubh,
                    width, fillchar)
            elif side == 'right':
                out_arr = bodo.libs.dict_arr_ext.str_ljust(jmaap__qmubh,
                    width, fillchar)
            elif side == 'both':
                out_arr = bodo.libs.dict_arr_ext.str_center(jmaap__qmubh,
                    width, fillchar)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_pad_dict_impl

    def impl(S_str, width, side='left', fillchar=' '):
        S = S_str._obj
        fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xir__sephv = len(fez__pwhat)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xir__sephv, -1)
        for gciot__vklca in numba.parfors.parfor.internal_prange(xir__sephv):
            if bodo.libs.array_kernels.isna(fez__pwhat, gciot__vklca):
                out_arr[gciot__vklca] = ''
                bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
            elif side == 'left':
                out_arr[gciot__vklca] = fez__pwhat[gciot__vklca].rjust(width,
                    fillchar)
            elif side == 'right':
                out_arr[gciot__vklca] = fez__pwhat[gciot__vklca].ljust(width,
                    fillchar)
            elif side == 'both':
                out_arr[gciot__vklca] = fez__pwhat[gciot__vklca].center(width,
                    fillchar)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
    return impl


@overload_method(SeriesStrMethodType, 'zfill', inline='always',
    no_unliteral=True)
def overload_str_method_zfill(S_str, width):
    int_arg_check('zfill', 'width', width)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_zfill_dict_impl(S_str, width):
            S = S_str._obj
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_zfill(jmaap__qmubh, width)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_zfill_dict_impl

    def impl(S_str, width):
        S = S_str._obj
        fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xir__sephv = len(fez__pwhat)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xir__sephv, -1)
        for gciot__vklca in numba.parfors.parfor.internal_prange(xir__sephv):
            if bodo.libs.array_kernels.isna(fez__pwhat, gciot__vklca):
                out_arr[gciot__vklca] = ''
                bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
            else:
                out_arr[gciot__vklca] = fez__pwhat[gciot__vklca].zfill(width)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
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
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_slice(jmaap__qmubh, start,
                stop, step)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_slice_dict_impl

    def impl(S_str, start=None, stop=None, step=None):
        S = S_str._obj
        fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xir__sephv = len(fez__pwhat)
        out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(xir__sephv, -1)
        for gciot__vklca in numba.parfors.parfor.internal_prange(xir__sephv):
            if bodo.libs.array_kernels.isna(fez__pwhat, gciot__vklca):
                out_arr[gciot__vklca] = ''
                bodo.libs.array_kernels.setna(out_arr, gciot__vklca)
            else:
                out_arr[gciot__vklca] = fez__pwhat[gciot__vklca][start:stop
                    :step]
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
    return impl


@overload_method(SeriesStrMethodType, 'startswith', inline='always',
    no_unliteral=True)
def overload_str_method_startswith(S_str, pat, na=np.nan):
    not_supported_arg_check('startswith', 'na', na, np.nan)
    str_arg_check('startswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_startswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_startswith(jmaap__qmubh,
                pat, na)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_startswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xir__sephv = len(fez__pwhat)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(xir__sephv)
        for i in numba.parfors.parfor.internal_prange(xir__sephv):
            if bodo.libs.array_kernels.isna(fez__pwhat, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = fez__pwhat[i].startswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
    return impl


@overload_method(SeriesStrMethodType, 'endswith', inline='always',
    no_unliteral=True)
def overload_str_method_endswith(S_str, pat, na=np.nan):
    not_supported_arg_check('endswith', 'na', na, np.nan)
    str_arg_check('endswith', 'pat', pat)
    if S_str.stype.data == bodo.dict_str_arr_type:

        def _str_endswith_dict_impl(S_str, pat, na=np.nan):
            S = S_str._obj
            jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
            thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
            zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
            out_arr = bodo.libs.dict_arr_ext.str_endswith(jmaap__qmubh, pat, na
                )
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                thm__eoku, zjp__sol)
        return _str_endswith_dict_impl

    def impl(S_str, pat, na=np.nan):
        S = S_str._obj
        fez__pwhat = bodo.hiframes.pd_series_ext.get_series_data(S)
        zjp__sol = bodo.hiframes.pd_series_ext.get_series_name(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        numba.parfors.parfor.init_prange()
        xir__sephv = len(fez__pwhat)
        out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(xir__sephv)
        for i in numba.parfors.parfor.internal_prange(xir__sephv):
            if bodo.libs.array_kernels.isna(fez__pwhat, i):
                bodo.libs.array_kernels.setna(out_arr, i)
            else:
                out_arr[i] = fez__pwhat[i].endswith(pat)
        return bodo.hiframes.pd_series_ext.init_series(out_arr, thm__eoku,
            zjp__sol)
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
    yljfg__tfps, regex = _get_column_names_from_regex(pat, flags, 'extract')
    lkbv__tnqaw = len(yljfg__tfps)
    if S_str.stype.data == bodo.dict_str_arr_type:
        ijct__nmihz = 'def impl(S_str, pat, flags=0, expand=True):\n'
        ijct__nmihz += '  S = S_str._obj\n'
        ijct__nmihz += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ijct__nmihz += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ijct__nmihz += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ijct__nmihz += f"""  out_arr_list = bodo.libs.dict_arr_ext.str_extract(arr, pat, flags, {lkbv__tnqaw})
"""
        for i in range(lkbv__tnqaw):
            ijct__nmihz += f'  out_arr_{i} = out_arr_list[{i}]\n'
    else:
        ijct__nmihz = 'def impl(S_str, pat, flags=0, expand=True):\n'
        ijct__nmihz += '  regex = re.compile(pat, flags=flags)\n'
        ijct__nmihz += '  S = S_str._obj\n'
        ijct__nmihz += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ijct__nmihz += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ijct__nmihz += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ijct__nmihz += '  numba.parfors.parfor.init_prange()\n'
        ijct__nmihz += '  n = len(str_arr)\n'
        for i in range(lkbv__tnqaw):
            ijct__nmihz += (
                '  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)\n'
                .format(i))
        ijct__nmihz += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        ijct__nmihz += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        for i in range(lkbv__tnqaw):
            ijct__nmihz += "          out_arr_{}[j] = ''\n".format(i)
            ijct__nmihz += (
                '          bodo.libs.array_kernels.setna(out_arr_{}, j)\n'.
                format(i))
        ijct__nmihz += '      else:\n'
        ijct__nmihz += '          m = regex.search(str_arr[j])\n'
        ijct__nmihz += '          if m:\n'
        ijct__nmihz += '            g = m.groups()\n'
        for i in range(lkbv__tnqaw):
            ijct__nmihz += '            out_arr_{0}[j] = g[{0}]\n'.format(i)
        ijct__nmihz += '          else:\n'
        for i in range(lkbv__tnqaw):
            ijct__nmihz += "            out_arr_{}[j] = ''\n".format(i)
            ijct__nmihz += (
                '            bodo.libs.array_kernels.setna(out_arr_{}, j)\n'
                .format(i))
    if is_overload_false(expand) and regex.groups == 1:
        zjp__sol = "'{}'".format(list(regex.groupindex.keys()).pop()) if len(
            regex.groupindex.keys()) > 0 else 'name'
        ijct__nmihz += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr_0, index, {})\n'
            .format(zjp__sol))
        ggtfl__lxtcm = {}
        exec(ijct__nmihz, {'re': re, 'bodo': bodo, 'numba': numba,
            'get_utf8_size': get_utf8_size}, ggtfl__lxtcm)
        impl = ggtfl__lxtcm['impl']
        return impl
    qmdx__lzkx = ', '.join('out_arr_{}'.format(i) for i in range(lkbv__tnqaw))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(ijct__nmihz,
        yljfg__tfps, qmdx__lzkx, 'index', extra_globals={'get_utf8_size':
        get_utf8_size, 're': re})
    return impl


@overload_method(SeriesStrMethodType, 'extractall', inline='always',
    no_unliteral=True)
def overload_str_method_extractall(S_str, pat, flags=0):
    yljfg__tfps, sfz__lkf = _get_column_names_from_regex(pat, flags,
        'extractall')
    lkbv__tnqaw = len(yljfg__tfps)
    ync__ivw = isinstance(S_str.stype.index, StringIndexType)
    lruj__eeed = lkbv__tnqaw > 1
    ufxiv__rcfqe = '_multi' if lruj__eeed else ''
    if S_str.stype.data == bodo.dict_str_arr_type:
        ijct__nmihz = 'def impl(S_str, pat, flags=0):\n'
        ijct__nmihz += '  S = S_str._obj\n'
        ijct__nmihz += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ijct__nmihz += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ijct__nmihz += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ijct__nmihz += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        ijct__nmihz += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        ijct__nmihz += '  regex = re.compile(pat, flags=flags)\n'
        ijct__nmihz += '  out_ind_arr, out_match_arr, out_arr_list = '
        ijct__nmihz += (
            f'bodo.libs.dict_arr_ext.str_extractall{ufxiv__rcfqe}(\n')
        ijct__nmihz += f'arr, regex, {lkbv__tnqaw}, index_arr)\n'
        for i in range(lkbv__tnqaw):
            ijct__nmihz += f'  out_arr_{i} = out_arr_list[{i}]\n'
        ijct__nmihz += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        ijct__nmihz += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    else:
        ijct__nmihz = 'def impl(S_str, pat, flags=0):\n'
        ijct__nmihz += '  regex = re.compile(pat, flags=flags)\n'
        ijct__nmihz += '  S = S_str._obj\n'
        ijct__nmihz += (
            '  str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        ijct__nmihz += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ijct__nmihz += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        ijct__nmihz += (
            '  index_arr = bodo.utils.conversion.index_to_array(index)\n')
        ijct__nmihz += (
            '  index_name = bodo.hiframes.pd_index_ext.get_index_name(index)\n'
            )
        ijct__nmihz += '  numba.parfors.parfor.init_prange()\n'
        ijct__nmihz += '  n = len(str_arr)\n'
        ijct__nmihz += '  out_n_l = [0]\n'
        for i in range(lkbv__tnqaw):
            ijct__nmihz += '  num_chars_{} = 0\n'.format(i)
        if ync__ivw:
            ijct__nmihz += '  index_num_chars = 0\n'
        ijct__nmihz += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if ync__ivw:
            ijct__nmihz += (
                '      index_num_chars += get_utf8_size(index_arr[i])\n')
        ijct__nmihz += '      if bodo.libs.array_kernels.isna(str_arr, i):\n'
        ijct__nmihz += '          continue\n'
        ijct__nmihz += '      m = regex.findall(str_arr[i])\n'
        ijct__nmihz += '      out_n_l[0] += len(m)\n'
        for i in range(lkbv__tnqaw):
            ijct__nmihz += '      l_{} = 0\n'.format(i)
        ijct__nmihz += '      for s in m:\n'
        for i in range(lkbv__tnqaw):
            ijct__nmihz += '        l_{} += get_utf8_size(s{})\n'.format(i,
                '[{}]'.format(i) if lkbv__tnqaw > 1 else '')
        for i in range(lkbv__tnqaw):
            ijct__nmihz += '      num_chars_{0} += l_{0}\n'.format(i)
        ijct__nmihz += """  out_n = bodo.libs.distributed_api.local_alloc_size(out_n_l[0], str_arr)
"""
        for i in range(lkbv__tnqaw):
            ijct__nmihz += (
                """  out_arr_{0} = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, num_chars_{0})
"""
                .format(i))
        if ync__ivw:
            ijct__nmihz += """  out_ind_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(out_n, index_num_chars)
"""
        else:
            ijct__nmihz += '  out_ind_arr = np.empty(out_n, index_arr.dtype)\n'
        ijct__nmihz += '  out_match_arr = np.empty(out_n, np.int64)\n'
        ijct__nmihz += '  out_ind = 0\n'
        ijct__nmihz += '  for j in numba.parfors.parfor.internal_prange(n):\n'
        ijct__nmihz += '      if bodo.libs.array_kernels.isna(str_arr, j):\n'
        ijct__nmihz += '          continue\n'
        ijct__nmihz += '      m = regex.findall(str_arr[j])\n'
        ijct__nmihz += '      for k, s in enumerate(m):\n'
        for i in range(lkbv__tnqaw):
            ijct__nmihz += (
                """        bodo.libs.distributed_api.set_arr_local(out_arr_{}, out_ind, s{})
"""
                .format(i, '[{}]'.format(i) if lkbv__tnqaw > 1 else ''))
        ijct__nmihz += """        bodo.libs.distributed_api.set_arr_local(out_ind_arr, out_ind, index_arr[j])
"""
        ijct__nmihz += """        bodo.libs.distributed_api.set_arr_local(out_match_arr, out_ind, k)
"""
        ijct__nmihz += '        out_ind += 1\n'
        ijct__nmihz += (
            '  out_index = bodo.hiframes.pd_multi_index_ext.init_multi_index(\n'
            )
        ijct__nmihz += (
            "    (out_ind_arr, out_match_arr), (index_name, 'match'))\n")
    qmdx__lzkx = ', '.join('out_arr_{}'.format(i) for i in range(lkbv__tnqaw))
    impl = bodo.hiframes.dataframe_impl._gen_init_df(ijct__nmihz,
        yljfg__tfps, qmdx__lzkx, 'out_index', extra_globals={
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
    fxezn__vjwxb = dict(zip(regex.groupindex.values(), regex.groupindex.keys())
        )
    yljfg__tfps = [fxezn__vjwxb.get(1 + i, i) for i in range(regex.groups)]
    return yljfg__tfps, regex


def create_str2str_methods_overload(func_name):
    wvc__ipw = func_name in ['lstrip', 'rstrip', 'strip']
    ijct__nmihz = f"""def f({'S_str, to_strip=None' if wvc__ipw else 'S_str'}):
    S = S_str._obj
    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    str_arr = decode_if_dict_array(str_arr)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    numba.parfors.parfor.init_prange()
    n = len(str_arr)
    num_chars = {'-1' if wvc__ipw else 'num_total_chars(str_arr)'}
    out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n, num_chars)
    for j in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(str_arr, j):
            out_arr[j] = ""
            bodo.libs.array_kernels.setna(out_arr, j)
        else:
            out_arr[j] = str_arr[j].{func_name}({'to_strip' if wvc__ipw else ''})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    ijct__nmihz += f"""def _dict_impl({'S_str, to_strip=None' if wvc__ipw else 'S_str'}):
    S = S_str._obj
    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    out_arr = bodo.libs.dict_arr_ext.str_{func_name}({'arr, to_strip' if wvc__ipw else 'arr'})
    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)
"""
    ggtfl__lxtcm = {}
    exec(ijct__nmihz, {'bodo': bodo, 'numba': numba, 'num_total_chars':
        bodo.libs.str_arr_ext.num_total_chars, 'get_utf8_size': bodo.libs.
        str_arr_ext.get_utf8_size, 'decode_if_dict_array': bodo.utils.
        typing.decode_if_dict_array}, ggtfl__lxtcm)
    juxz__uiyvs = ggtfl__lxtcm['f']
    dhfp__xoa = ggtfl__lxtcm['_dict_impl']
    if wvc__ipw:

        def overload_strip_method(S_str, to_strip=None):
            if not is_overload_none(to_strip):
                str_arg_check(func_name, 'to_strip', to_strip)
            if S_str.stype.data == bodo.dict_str_arr_type:
                return dhfp__xoa
            return juxz__uiyvs
        return overload_strip_method
    else:

        def overload_str_method_dict_supported(S_str):
            if S_str.stype.data == bodo.dict_str_arr_type:
                return dhfp__xoa
            return juxz__uiyvs
        return overload_str_method_dict_supported


def create_str2bool_methods_overload(func_name):
    ijct__nmihz = 'def dict_impl(S_str):\n'
    ijct__nmihz += '    S = S_str._obj\n'
    ijct__nmihz += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ijct__nmihz += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ijct__nmihz += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    ijct__nmihz += (
        f'    out_arr = bodo.libs.dict_arr_ext.str_{func_name}(arr)\n')
    ijct__nmihz += (
        '    return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
        )
    ijct__nmihz += 'def impl(S_str):\n'
    ijct__nmihz += '    S = S_str._obj\n'
    ijct__nmihz += (
        '    str_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    ijct__nmihz += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    ijct__nmihz += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    ijct__nmihz += '    numba.parfors.parfor.init_prange()\n'
    ijct__nmihz += '    l = len(str_arr)\n'
    ijct__nmihz += '    out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(l)\n'
    ijct__nmihz += '    for i in numba.parfors.parfor.internal_prange(l):\n'
    ijct__nmihz += '        if bodo.libs.array_kernels.isna(str_arr, i):\n'
    ijct__nmihz += '            bodo.libs.array_kernels.setna(out_arr, i)\n'
    ijct__nmihz += '        else:\n'
    ijct__nmihz += ('            out_arr[i] = np.bool_(str_arr[i].{}())\n'.
        format(func_name))
    ijct__nmihz += '    return bodo.hiframes.pd_series_ext.init_series(\n'
    ijct__nmihz += '      out_arr,index, name)\n'
    ggtfl__lxtcm = {}
    exec(ijct__nmihz, {'bodo': bodo, 'numba': numba, 'np': np}, ggtfl__lxtcm)
    impl = ggtfl__lxtcm['impl']
    lku__mqnb = ggtfl__lxtcm['dict_impl']

    def overload_str2bool_methods(S_str):
        if S_str.stype.data == bodo.dict_str_arr_type:
            return lku__mqnb
        return impl
    return overload_str2bool_methods


def _install_str2str_methods():
    for qwq__kkagu in bodo.hiframes.pd_series_ext.str2str_methods:
        eodvl__khi = create_str2str_methods_overload(qwq__kkagu)
        overload_method(SeriesStrMethodType, qwq__kkagu, inline='always',
            no_unliteral=True)(eodvl__khi)


def _install_str2bool_methods():
    for qwq__kkagu in bodo.hiframes.pd_series_ext.str2bool_methods:
        eodvl__khi = create_str2bool_methods_overload(qwq__kkagu)
        overload_method(SeriesStrMethodType, qwq__kkagu, inline='always',
            no_unliteral=True)(eodvl__khi)


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
        zjp__sol = 'SeriesCatMethodType({})'.format(stype)
        super(SeriesCatMethodType, self).__init__(zjp__sol)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(SeriesCatMethodType)
class SeriesCatModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ddc__xltp = [('obj', fe_type.stype)]
        super(SeriesCatModel, self).__init__(dmm, fe_type, ddc__xltp)


make_attribute_wrapper(SeriesCatMethodType, 'obj', '_obj')


@intrinsic
def init_series_cat_method(typingctx, obj=None):

    def codegen(context, builder, signature, args):
        zjl__odgdq, = args
        xtfgx__hmfo = signature.return_type
        qbtmz__asxa = cgutils.create_struct_proxy(xtfgx__hmfo)(context, builder
            )
        qbtmz__asxa.obj = zjl__odgdq
        context.nrt.incref(builder, signature.args[0], zjl__odgdq)
        return qbtmz__asxa._getvalue()
    return SeriesCatMethodType(obj)(obj), codegen


@overload_attribute(SeriesCatMethodType, 'codes')
def series_cat_codes_overload(S_dt):

    def impl(S_dt):
        S = S_dt._obj
        jmaap__qmubh = bodo.hiframes.pd_series_ext.get_series_data(S)
        thm__eoku = bodo.hiframes.pd_series_ext.get_series_index(S)
        zjp__sol = None
        return bodo.hiframes.pd_series_ext.init_series(bodo.hiframes.
            pd_categorical_ext.get_categorical_arr_codes(jmaap__qmubh),
            thm__eoku, zjp__sol)
    return impl


unsupported_cat_attrs = {'categories', 'ordered'}
unsupported_cat_methods = {'rename_categories', 'reorder_categories',
    'add_categories', 'remove_categories', 'remove_unused_categories',
    'set_categories', 'as_ordered', 'as_unordered'}


def _install_catseries_unsupported():
    for huwl__vvhe in unsupported_cat_attrs:
        osbqq__vcre = 'Series.cat.' + huwl__vvhe
        overload_attribute(SeriesCatMethodType, huwl__vvhe)(
            create_unsupported_overload(osbqq__vcre))
    for rdy__yjj in unsupported_cat_methods:
        osbqq__vcre = 'Series.cat.' + rdy__yjj
        overload_method(SeriesCatMethodType, rdy__yjj)(
            create_unsupported_overload(osbqq__vcre))


_install_catseries_unsupported()
unsupported_str_methods = {'casefold', 'decode', 'encode', 'findall',
    'fullmatch', 'index', 'match', 'normalize', 'partition', 'rindex',
    'rpartition', 'slice_replace', 'rsplit', 'translate', 'wrap', 'get_dummies'
    }


def _install_strseries_unsupported():
    for rdy__yjj in unsupported_str_methods:
        osbqq__vcre = 'Series.str.' + rdy__yjj
        overload_method(SeriesStrMethodType, rdy__yjj)(
            create_unsupported_overload(osbqq__vcre))


_install_strseries_unsupported()
