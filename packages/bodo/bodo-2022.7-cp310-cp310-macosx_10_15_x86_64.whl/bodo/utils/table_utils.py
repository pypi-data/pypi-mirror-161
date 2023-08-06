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
    mfh__cne = not is_overload_none(func_name)
    if mfh__cne:
        func_name = get_overload_const_str(func_name)
        bnv__xuk = get_overload_const_bool(is_method)
    wubd__hnrf = out_arr_typ.instance_type if isinstance(out_arr_typ, types
        .TypeRef) else out_arr_typ
    hra__awh = wubd__hnrf == types.none
    spmqs__qlsbp = len(table.arr_types)
    if hra__awh:
        qcki__fzpny = table
    else:
        rhq__yqqv = tuple([wubd__hnrf] * spmqs__qlsbp)
        qcki__fzpny = TableType(rhq__yqqv)
    saizx__nirm = {'bodo': bodo, 'lst_dtype': wubd__hnrf, 'table_typ':
        qcki__fzpny}
    qzk__titk = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if hra__awh:
        qzk__titk += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        qzk__titk += f'  l = len(table)\n'
    else:
        qzk__titk += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({spmqs__qlsbp}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        ikg__yzu = used_cols.instance_type
        kun__rikvb = np.array(ikg__yzu.meta, dtype=np.int64)
        saizx__nirm['used_cols_glbl'] = kun__rikvb
        hixro__vmfc = set([table.block_nums[xik__nlwhv] for xik__nlwhv in
            kun__rikvb])
        qzk__titk += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        qzk__titk += f'  used_cols_set = None\n'
        kun__rikvb = None
    qzk__titk += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for mqmm__bxgnh in table.type_to_blk.values():
        qzk__titk += f"""  blk_{mqmm__bxgnh} = bodo.hiframes.table.get_table_block(table, {mqmm__bxgnh})
"""
        if hra__awh:
            qzk__titk += f"""  out_list_{mqmm__bxgnh} = bodo.hiframes.table.alloc_list_like(blk_{mqmm__bxgnh}, len(blk_{mqmm__bxgnh}), False)
"""
            apjro__eoj = f'out_list_{mqmm__bxgnh}'
        else:
            apjro__eoj = 'out_list'
        if kun__rikvb is None or mqmm__bxgnh in hixro__vmfc:
            qzk__titk += f'  for i in range(len(blk_{mqmm__bxgnh})):\n'
            saizx__nirm[f'col_indices_{mqmm__bxgnh}'] = np.array(table.
                block_to_arr_ind[mqmm__bxgnh], dtype=np.int64)
            qzk__titk += f'    col_loc = col_indices_{mqmm__bxgnh}[i]\n'
            if kun__rikvb is not None:
                qzk__titk += f'    if col_loc not in used_cols_set:\n'
                qzk__titk += f'        continue\n'
            if hra__awh:
                fywqi__kzrj = 'i'
            else:
                fywqi__kzrj = 'col_loc'
            if not mfh__cne:
                qzk__titk += (
                    f'    {apjro__eoj}[{fywqi__kzrj}] = blk_{mqmm__bxgnh}[i]\n'
                    )
            elif bnv__xuk:
                qzk__titk += f"""    {apjro__eoj}[{fywqi__kzrj}] = blk_{mqmm__bxgnh}[i].{func_name}()
"""
            else:
                qzk__titk += f"""    {apjro__eoj}[{fywqi__kzrj}] = {func_name}(blk_{mqmm__bxgnh}[i])
"""
        if hra__awh:
            qzk__titk += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {apjro__eoj}, {mqmm__bxgnh})
"""
    if hra__awh:
        qzk__titk += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        qzk__titk += '  return out_table\n'
    else:
        qzk__titk += (
            '  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)\n'
            )
    ltwn__mpkq = {}
    exec(qzk__titk, saizx__nirm, ltwn__mpkq)
    return ltwn__mpkq['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    yyoce__gly = args[0]
    if equiv_set.has_shape(yyoce__gly):
        return ArrayAnalysis.AnalyzeResult(shape=yyoce__gly, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    saizx__nirm = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.
        distributed_api.Reduce_Type.Sum.value)}
    qzk__titk = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    qzk__titk += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for mqmm__bxgnh in table.type_to_blk.values():
        qzk__titk += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {mqmm__bxgnh})\n'
            )
        saizx__nirm[f'col_indices_{mqmm__bxgnh}'] = np.array(table.
            block_to_arr_ind[mqmm__bxgnh], dtype=np.int64)
        qzk__titk += '  for i in range(len(blk)):\n'
        qzk__titk += f'    col_loc = col_indices_{mqmm__bxgnh}[i]\n'
        qzk__titk += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    qzk__titk += '  if parallel:\n'
    qzk__titk += '    for i in range(start_offset, len(out_arr)):\n'
    qzk__titk += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    ltwn__mpkq = {}
    exec(qzk__titk, saizx__nirm, ltwn__mpkq)
    return ltwn__mpkq['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    ntrxq__qiac = table.type_to_blk[arr_type]
    saizx__nirm = {'bodo': bodo}
    saizx__nirm['col_indices'] = np.array(table.block_to_arr_ind[
        ntrxq__qiac], dtype=np.int64)
    izsey__fcra = col_nums_meta.instance_type
    saizx__nirm['col_nums'] = np.array(izsey__fcra.meta, np.int64)
    qzk__titk = 'def impl(table, col_nums_meta, arr_type):\n'
    qzk__titk += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {ntrxq__qiac})\n')
    qzk__titk += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    qzk__titk += '  n = len(table)\n'
    srp__auug = bodo.utils.typing.is_str_arr_type(arr_type)
    if srp__auug:
        qzk__titk += '  total_chars = 0\n'
        qzk__titk += '  for c in col_nums:\n'
        qzk__titk += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        qzk__titk += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        qzk__titk += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        qzk__titk += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        qzk__titk += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    qzk__titk += '  for i in range(len(col_nums)):\n'
    qzk__titk += '    c = col_nums[i]\n'
    if not srp__auug:
        qzk__titk += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    qzk__titk += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    qzk__titk += '    off = i * n\n'
    qzk__titk += '    for j in range(len(arr)):\n'
    qzk__titk += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    qzk__titk += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    qzk__titk += '      else:\n'
    qzk__titk += '        out_arr[off+j] = arr[j]\n'
    qzk__titk += '  return out_arr\n'
    timwq__zyg = {}
    exec(qzk__titk, saizx__nirm, timwq__zyg)
    tpk__tmoon = timwq__zyg['impl']
    return tpk__tmoon


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    mqttv__ugewk = not is_overload_false(copy)
    qlcrv__bdfue = is_overload_true(copy)
    saizx__nirm = {'bodo': bodo}
    had__nbdhm = table.arr_types
    znc__wmcw = new_table_typ.arr_types
    kqv__kgxiu: Set[int] = set()
    bhut__jobh: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    nzrzj__gltr: Set[types.Type] = set()
    for xik__nlwhv, wout__kaf in enumerate(had__nbdhm):
        dquzb__odh = znc__wmcw[xik__nlwhv]
        if wout__kaf == dquzb__odh:
            nzrzj__gltr.add(wout__kaf)
        else:
            kqv__kgxiu.add(xik__nlwhv)
            bhut__jobh[dquzb__odh].add(wout__kaf)
    qzk__titk = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    qzk__titk += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    qzk__titk += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    jnr__jkgox = set(range(len(had__nbdhm)))
    yiyf__lfldi = jnr__jkgox - kqv__kgxiu
    if not is_overload_none(used_cols):
        ikg__yzu = used_cols.instance_type
        jeic__ymr = set(ikg__yzu.meta)
        kqv__kgxiu = kqv__kgxiu & jeic__ymr
        yiyf__lfldi = yiyf__lfldi & jeic__ymr
        hixro__vmfc = set([table.block_nums[xik__nlwhv] for xik__nlwhv in
            jeic__ymr])
    else:
        jeic__ymr = None
    saizx__nirm['cast_cols'] = np.array(list(kqv__kgxiu), dtype=np.int64)
    saizx__nirm['copied_cols'] = np.array(list(yiyf__lfldi), dtype=np.int64)
    qzk__titk += f'  copied_cols_set = set(copied_cols)\n'
    qzk__titk += f'  cast_cols_set = set(cast_cols)\n'
    for zivrg__ipwo, mqmm__bxgnh in new_table_typ.type_to_blk.items():
        saizx__nirm[f'typ_list_{mqmm__bxgnh}'] = types.List(zivrg__ipwo)
        qzk__titk += f"""  out_arr_list_{mqmm__bxgnh} = bodo.hiframes.table.alloc_list_like(typ_list_{mqmm__bxgnh}, {len(new_table_typ.block_to_arr_ind[mqmm__bxgnh])}, False)
"""
        if zivrg__ipwo in nzrzj__gltr:
            otvj__dldj = table.type_to_blk[zivrg__ipwo]
            if jeic__ymr is None or otvj__dldj in hixro__vmfc:
                cjik__gpb = table.block_to_arr_ind[otvj__dldj]
                fhcj__qqd = [new_table_typ.block_offsets[nsfl__lsc] for
                    nsfl__lsc in cjik__gpb]
                saizx__nirm[f'new_idx_{otvj__dldj}'] = np.array(fhcj__qqd,
                    np.int64)
                saizx__nirm[f'orig_arr_inds_{otvj__dldj}'] = np.array(cjik__gpb
                    , np.int64)
                qzk__titk += f"""  arr_list_{otvj__dldj} = bodo.hiframes.table.get_table_block(table, {otvj__dldj})
"""
                qzk__titk += f'  for i in range(len(arr_list_{otvj__dldj})):\n'
                qzk__titk += (
                    f'    arr_ind_{otvj__dldj} = orig_arr_inds_{otvj__dldj}[i]\n'
                    )
                qzk__titk += (
                    f'    if arr_ind_{otvj__dldj} not in copied_cols_set:\n')
                qzk__titk += f'      continue\n'
                qzk__titk += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{otvj__dldj}, i, arr_ind_{otvj__dldj})
"""
                qzk__titk += (
                    f'    out_idx_{mqmm__bxgnh}_{otvj__dldj} = new_idx_{otvj__dldj}[i]\n'
                    )
                qzk__titk += (
                    f'    arr_val_{otvj__dldj} = arr_list_{otvj__dldj}[i]\n')
                if qlcrv__bdfue:
                    qzk__titk += (
                        f'    arr_val_{otvj__dldj} = arr_val_{otvj__dldj}.copy()\n'
                        )
                elif mqttv__ugewk:
                    qzk__titk += f"""    arr_val_{otvj__dldj} = arr_val_{otvj__dldj}.copy() if copy else arr_val_{mqmm__bxgnh}
"""
                qzk__titk += f"""    out_arr_list_{mqmm__bxgnh}[out_idx_{mqmm__bxgnh}_{otvj__dldj}] = arr_val_{otvj__dldj}
"""
    mazk__neyb = set()
    for zivrg__ipwo, mqmm__bxgnh in new_table_typ.type_to_blk.items():
        if zivrg__ipwo in bhut__jobh:
            if isinstance(zivrg__ipwo, bodo.IntegerArrayType):
                slyw__qvjgz = zivrg__ipwo.get_pandas_scalar_type_instance.name
            else:
                slyw__qvjgz = zivrg__ipwo.dtype
            saizx__nirm[f'typ_{mqmm__bxgnh}'] = slyw__qvjgz
            ahb__otxl = bhut__jobh[zivrg__ipwo]
            for ukk__gvw in ahb__otxl:
                otvj__dldj = table.type_to_blk[ukk__gvw]
                if jeic__ymr is None or otvj__dldj in hixro__vmfc:
                    if (ukk__gvw not in nzrzj__gltr and ukk__gvw not in
                        mazk__neyb):
                        cjik__gpb = table.block_to_arr_ind[otvj__dldj]
                        fhcj__qqd = [new_table_typ.block_offsets[nsfl__lsc] for
                            nsfl__lsc in cjik__gpb]
                        saizx__nirm[f'new_idx_{otvj__dldj}'] = np.array(
                            fhcj__qqd, np.int64)
                        saizx__nirm[f'orig_arr_inds_{otvj__dldj}'] = np.array(
                            cjik__gpb, np.int64)
                        qzk__titk += f"""  arr_list_{otvj__dldj} = bodo.hiframes.table.get_table_block(table, {otvj__dldj})
"""
                    mazk__neyb.add(ukk__gvw)
                    qzk__titk += (
                        f'  for i in range(len(arr_list_{otvj__dldj})):\n')
                    qzk__titk += (
                        f'    arr_ind_{otvj__dldj} = orig_arr_inds_{otvj__dldj}[i]\n'
                        )
                    qzk__titk += (
                        f'    if arr_ind_{otvj__dldj} not in cast_cols_set:\n')
                    qzk__titk += f'      continue\n'
                    qzk__titk += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{otvj__dldj}, i, arr_ind_{otvj__dldj})
"""
                    qzk__titk += f"""    out_idx_{mqmm__bxgnh}_{otvj__dldj} = new_idx_{otvj__dldj}[i]
"""
                    qzk__titk += f"""    arr_val_{mqmm__bxgnh} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{otvj__dldj}[i], typ_{mqmm__bxgnh}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    qzk__titk += f"""    out_arr_list_{mqmm__bxgnh}[out_idx_{mqmm__bxgnh}_{otvj__dldj}] = arr_val_{mqmm__bxgnh}
"""
        qzk__titk += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{mqmm__bxgnh}, {mqmm__bxgnh})
"""
    qzk__titk += '  return out_table\n'
    ltwn__mpkq = {}
    exec(qzk__titk, saizx__nirm, ltwn__mpkq)
    return ltwn__mpkq['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    yyoce__gly = args[0]
    if equiv_set.has_shape(yyoce__gly):
        return ArrayAnalysis.AnalyzeResult(shape=yyoce__gly, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
