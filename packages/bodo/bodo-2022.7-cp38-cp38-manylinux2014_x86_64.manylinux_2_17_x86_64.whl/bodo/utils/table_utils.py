"""File containing utility functions for supporting DataFrame operations with Table Format."""
from collections import defaultdict
from typing import Dict, Set
import numba
import numpy as np
from numba.core import types
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.table import TableType
from bodo.utils.typing import get_overload_const_bool, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, is_overload_false, is_overload_none, is_overload_true, raise_bodo_error


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_mappable_table_func(table, func_name, out_arr_typ, is_method,
    used_cols=None):
    if not is_overload_constant_str(func_name) and not is_overload_none(
        func_name):
        raise_bodo_error(
            'generate_mappable_table_func(): func_name must be a constant string'
            )
    if not is_overload_constant_bool(is_method):
        raise_bodo_error(
            'generate_mappable_table_func(): is_method must be a constant boolean'
            )
    pazwn__jdwon = not is_overload_none(func_name)
    if pazwn__jdwon:
        func_name = get_overload_const_str(func_name)
        ouaxk__tjkvj = get_overload_const_bool(is_method)
    whivz__yvygy = out_arr_typ.instance_type if isinstance(out_arr_typ,
        types.TypeRef) else out_arr_typ
    qwlzj__yvcc = whivz__yvygy == types.none
    tfop__rso = len(table.arr_types)
    if qwlzj__yvcc:
        inmc__omju = table
    else:
        zwzy__wrlf = tuple([whivz__yvygy] * tfop__rso)
        inmc__omju = TableType(zwzy__wrlf)
    vpd__mkcm = {'bodo': bodo, 'lst_dtype': whivz__yvygy, 'table_typ':
        inmc__omju}
    cyo__krure = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if qwlzj__yvcc:
        cyo__krure += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        cyo__krure += f'  l = len(table)\n'
    else:
        cyo__krure += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({tfop__rso}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        laxk__viwk = used_cols.instance_type
        dqx__eaabc = np.array(laxk__viwk.meta, dtype=np.int64)
        vpd__mkcm['used_cols_glbl'] = dqx__eaabc
        giur__zal = set([table.block_nums[riat__shvyp] for riat__shvyp in
            dqx__eaabc])
        cyo__krure += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        cyo__krure += f'  used_cols_set = None\n'
        dqx__eaabc = None
    cyo__krure += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for wloj__eol in table.type_to_blk.values():
        cyo__krure += f"""  blk_{wloj__eol} = bodo.hiframes.table.get_table_block(table, {wloj__eol})
"""
        if qwlzj__yvcc:
            cyo__krure += f"""  out_list_{wloj__eol} = bodo.hiframes.table.alloc_list_like(blk_{wloj__eol}, len(blk_{wloj__eol}), False)
"""
            qyn__lidfi = f'out_list_{wloj__eol}'
        else:
            qyn__lidfi = 'out_list'
        if dqx__eaabc is None or wloj__eol in giur__zal:
            cyo__krure += f'  for i in range(len(blk_{wloj__eol})):\n'
            vpd__mkcm[f'col_indices_{wloj__eol}'] = np.array(table.
                block_to_arr_ind[wloj__eol], dtype=np.int64)
            cyo__krure += f'    col_loc = col_indices_{wloj__eol}[i]\n'
            if dqx__eaabc is not None:
                cyo__krure += f'    if col_loc not in used_cols_set:\n'
                cyo__krure += f'        continue\n'
            if qwlzj__yvcc:
                xwv__augr = 'i'
            else:
                xwv__augr = 'col_loc'
            if not pazwn__jdwon:
                cyo__krure += (
                    f'    {qyn__lidfi}[{xwv__augr}] = blk_{wloj__eol}[i]\n')
            elif ouaxk__tjkvj:
                cyo__krure += (
                    f'    {qyn__lidfi}[{xwv__augr}] = blk_{wloj__eol}[i].{func_name}()\n'
                    )
            else:
                cyo__krure += (
                    f'    {qyn__lidfi}[{xwv__augr}] = {func_name}(blk_{wloj__eol}[i])\n'
                    )
        if qwlzj__yvcc:
            cyo__krure += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {qyn__lidfi}, {wloj__eol})
"""
    if qwlzj__yvcc:
        cyo__krure += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        cyo__krure += '  return out_table\n'
    else:
        cyo__krure += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    igl__thgx = {}
    exec(cyo__krure, vpd__mkcm, igl__thgx)
    return igl__thgx['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    csts__vqkl = args[0]
    if equiv_set.has_shape(csts__vqkl):
        return ArrayAnalysis.AnalyzeResult(shape=csts__vqkl, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    vpd__mkcm = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.distributed_api
        .Reduce_Type.Sum.value)}
    cyo__krure = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    cyo__krure += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for wloj__eol in table.type_to_blk.values():
        cyo__krure += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {wloj__eol})\n'
            )
        vpd__mkcm[f'col_indices_{wloj__eol}'] = np.array(table.
            block_to_arr_ind[wloj__eol], dtype=np.int64)
        cyo__krure += '  for i in range(len(blk)):\n'
        cyo__krure += f'    col_loc = col_indices_{wloj__eol}[i]\n'
        cyo__krure += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    cyo__krure += '  if parallel:\n'
    cyo__krure += '    for i in range(start_offset, len(out_arr)):\n'
    cyo__krure += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    igl__thgx = {}
    exec(cyo__krure, vpd__mkcm, igl__thgx)
    return igl__thgx['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    hfrdd__cyotg = table.type_to_blk[arr_type]
    vpd__mkcm = {'bodo': bodo}
    vpd__mkcm['col_indices'] = np.array(table.block_to_arr_ind[hfrdd__cyotg
        ], dtype=np.int64)
    elmb__uqx = col_nums_meta.instance_type
    vpd__mkcm['col_nums'] = np.array(elmb__uqx.meta, np.int64)
    cyo__krure = 'def impl(table, col_nums_meta, arr_type):\n'
    cyo__krure += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {hfrdd__cyotg})\n'
        )
    cyo__krure += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    cyo__krure += '  n = len(table)\n'
    xzddd__ddc = bodo.utils.typing.is_str_arr_type(arr_type)
    if xzddd__ddc:
        cyo__krure += '  total_chars = 0\n'
        cyo__krure += '  for c in col_nums:\n'
        cyo__krure += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        cyo__krure += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        cyo__krure += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        cyo__krure += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        cyo__krure += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    cyo__krure += '  for i in range(len(col_nums)):\n'
    cyo__krure += '    c = col_nums[i]\n'
    if not xzddd__ddc:
        cyo__krure += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    cyo__krure += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    cyo__krure += '    off = i * n\n'
    cyo__krure += '    for j in range(len(arr)):\n'
    cyo__krure += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    cyo__krure += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    cyo__krure += '      else:\n'
    cyo__krure += '        out_arr[off+j] = arr[j]\n'
    cyo__krure += '  return out_arr\n'
    acwdk__lxbbn = {}
    exec(cyo__krure, vpd__mkcm, acwdk__lxbbn)
    zvwlt__myz = acwdk__lxbbn['impl']
    return zvwlt__myz


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    nckw__accdt = not is_overload_false(copy)
    pffxe__glc = is_overload_true(copy)
    vpd__mkcm = {'bodo': bodo}
    ecfr__hofo = table.arr_types
    noicy__uay = new_table_typ.arr_types
    uixup__mwvs: Set[int] = set()
    qgc__qiyga: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    hcjsu__lol: Set[types.Type] = set()
    for riat__shvyp, xuk__vojw in enumerate(ecfr__hofo):
        asyc__xcf = noicy__uay[riat__shvyp]
        if xuk__vojw == asyc__xcf:
            hcjsu__lol.add(xuk__vojw)
        else:
            uixup__mwvs.add(riat__shvyp)
            qgc__qiyga[asyc__xcf].add(xuk__vojw)
    cyo__krure = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    cyo__krure += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    cyo__krure += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    jkmvb__vbg = set(range(len(ecfr__hofo)))
    gwxn__pku = jkmvb__vbg - uixup__mwvs
    if not is_overload_none(used_cols):
        laxk__viwk = used_cols.instance_type
        ogs__vuej = set(laxk__viwk.meta)
        uixup__mwvs = uixup__mwvs & ogs__vuej
        gwxn__pku = gwxn__pku & ogs__vuej
        giur__zal = set([table.block_nums[riat__shvyp] for riat__shvyp in
            ogs__vuej])
    else:
        ogs__vuej = None
    vpd__mkcm['cast_cols'] = np.array(list(uixup__mwvs), dtype=np.int64)
    vpd__mkcm['copied_cols'] = np.array(list(gwxn__pku), dtype=np.int64)
    cyo__krure += f'  copied_cols_set = set(copied_cols)\n'
    cyo__krure += f'  cast_cols_set = set(cast_cols)\n'
    for lif__iqnt, wloj__eol in new_table_typ.type_to_blk.items():
        vpd__mkcm[f'typ_list_{wloj__eol}'] = types.List(lif__iqnt)
        cyo__krure += f"""  out_arr_list_{wloj__eol} = bodo.hiframes.table.alloc_list_like(typ_list_{wloj__eol}, {len(new_table_typ.block_to_arr_ind[wloj__eol])}, False)
"""
        if lif__iqnt in hcjsu__lol:
            tcc__iuwh = table.type_to_blk[lif__iqnt]
            if ogs__vuej is None or tcc__iuwh in giur__zal:
                qlzok__mcxkb = table.block_to_arr_ind[tcc__iuwh]
                hbdtu__hxfa = [new_table_typ.block_offsets[renqo__pmsvq] for
                    renqo__pmsvq in qlzok__mcxkb]
                vpd__mkcm[f'new_idx_{tcc__iuwh}'] = np.array(hbdtu__hxfa,
                    np.int64)
                vpd__mkcm[f'orig_arr_inds_{tcc__iuwh}'] = np.array(qlzok__mcxkb
                    , np.int64)
                cyo__krure += f"""  arr_list_{tcc__iuwh} = bodo.hiframes.table.get_table_block(table, {tcc__iuwh})
"""
                cyo__krure += f'  for i in range(len(arr_list_{tcc__iuwh})):\n'
                cyo__krure += (
                    f'    arr_ind_{tcc__iuwh} = orig_arr_inds_{tcc__iuwh}[i]\n'
                    )
                cyo__krure += (
                    f'    if arr_ind_{tcc__iuwh} not in copied_cols_set:\n')
                cyo__krure += f'      continue\n'
                cyo__krure += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{tcc__iuwh}, i, arr_ind_{tcc__iuwh})
"""
                cyo__krure += (
                    f'    out_idx_{wloj__eol}_{tcc__iuwh} = new_idx_{tcc__iuwh}[i]\n'
                    )
                cyo__krure += (
                    f'    arr_val_{tcc__iuwh} = arr_list_{tcc__iuwh}[i]\n')
                if pffxe__glc:
                    cyo__krure += (
                        f'    arr_val_{tcc__iuwh} = arr_val_{tcc__iuwh}.copy()\n'
                        )
                elif nckw__accdt:
                    cyo__krure += f"""    arr_val_{tcc__iuwh} = arr_val_{tcc__iuwh}.copy() if copy else arr_val_{wloj__eol}
"""
                cyo__krure += f"""    out_arr_list_{wloj__eol}[out_idx_{wloj__eol}_{tcc__iuwh}] = arr_val_{tcc__iuwh}
"""
    dfe__fygd = set()
    for lif__iqnt, wloj__eol in new_table_typ.type_to_blk.items():
        if lif__iqnt in qgc__qiyga:
            if isinstance(lif__iqnt, bodo.IntegerArrayType):
                rlbfa__bmnso = lif__iqnt.get_pandas_scalar_type_instance.name
            else:
                rlbfa__bmnso = lif__iqnt.dtype
            vpd__mkcm[f'typ_{wloj__eol}'] = rlbfa__bmnso
            wnjm__xfukm = qgc__qiyga[lif__iqnt]
            for okn__hls in wnjm__xfukm:
                tcc__iuwh = table.type_to_blk[okn__hls]
                if ogs__vuej is None or tcc__iuwh in giur__zal:
                    if (okn__hls not in hcjsu__lol and okn__hls not in
                        dfe__fygd):
                        qlzok__mcxkb = table.block_to_arr_ind[tcc__iuwh]
                        hbdtu__hxfa = [new_table_typ.block_offsets[
                            renqo__pmsvq] for renqo__pmsvq in qlzok__mcxkb]
                        vpd__mkcm[f'new_idx_{tcc__iuwh}'] = np.array(
                            hbdtu__hxfa, np.int64)
                        vpd__mkcm[f'orig_arr_inds_{tcc__iuwh}'] = np.array(
                            qlzok__mcxkb, np.int64)
                        cyo__krure += f"""  arr_list_{tcc__iuwh} = bodo.hiframes.table.get_table_block(table, {tcc__iuwh})
"""
                    dfe__fygd.add(okn__hls)
                    cyo__krure += (
                        f'  for i in range(len(arr_list_{tcc__iuwh})):\n')
                    cyo__krure += (
                        f'    arr_ind_{tcc__iuwh} = orig_arr_inds_{tcc__iuwh}[i]\n'
                        )
                    cyo__krure += (
                        f'    if arr_ind_{tcc__iuwh} not in cast_cols_set:\n')
                    cyo__krure += f'      continue\n'
                    cyo__krure += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{tcc__iuwh}, i, arr_ind_{tcc__iuwh})
"""
                    cyo__krure += (
                        f'    out_idx_{wloj__eol}_{tcc__iuwh} = new_idx_{tcc__iuwh}[i]\n'
                        )
                    cyo__krure += f"""    arr_val_{wloj__eol} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{tcc__iuwh}[i], typ_{wloj__eol}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    cyo__krure += f"""    out_arr_list_{wloj__eol}[out_idx_{wloj__eol}_{tcc__iuwh}] = arr_val_{wloj__eol}
"""
        cyo__krure += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{wloj__eol}, {wloj__eol})
"""
    cyo__krure += '  return out_table\n'
    igl__thgx = {}
    exec(cyo__krure, vpd__mkcm, igl__thgx)
    return igl__thgx['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    csts__vqkl = args[0]
    if equiv_set.has_shape(csts__vqkl):
        return ArrayAnalysis.AnalyzeResult(shape=csts__vqkl, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
