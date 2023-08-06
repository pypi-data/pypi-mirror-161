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
    shk__pbwhk = not is_overload_none(func_name)
    if shk__pbwhk:
        func_name = get_overload_const_str(func_name)
        xttze__bhqnw = get_overload_const_bool(is_method)
    vdp__geoq = out_arr_typ.instance_type if isinstance(out_arr_typ, types.
        TypeRef) else out_arr_typ
    popun__kogqr = vdp__geoq == types.none
    uax__cihqc = len(table.arr_types)
    if popun__kogqr:
        szc__lrl = table
    else:
        nsco__tiz = tuple([vdp__geoq] * uax__cihqc)
        szc__lrl = TableType(nsco__tiz)
    ilea__bpydi = {'bodo': bodo, 'lst_dtype': vdp__geoq, 'table_typ': szc__lrl}
    nsew__liubs = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if popun__kogqr:
        nsew__liubs += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        nsew__liubs += f'  l = len(table)\n'
    else:
        nsew__liubs += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({uax__cihqc}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        dvbgk__bfzw = used_cols.instance_type
        qudg__pyj = np.array(dvbgk__bfzw.meta, dtype=np.int64)
        ilea__bpydi['used_cols_glbl'] = qudg__pyj
        ccgvr__mzf = set([table.block_nums[otluf__duw] for otluf__duw in
            qudg__pyj])
        nsew__liubs += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        nsew__liubs += f'  used_cols_set = None\n'
        qudg__pyj = None
    nsew__liubs += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for laxy__zbxu in table.type_to_blk.values():
        nsew__liubs += f"""  blk_{laxy__zbxu} = bodo.hiframes.table.get_table_block(table, {laxy__zbxu})
"""
        if popun__kogqr:
            nsew__liubs += f"""  out_list_{laxy__zbxu} = bodo.hiframes.table.alloc_list_like(blk_{laxy__zbxu}, len(blk_{laxy__zbxu}), False)
"""
            hrkz__bzug = f'out_list_{laxy__zbxu}'
        else:
            hrkz__bzug = 'out_list'
        if qudg__pyj is None or laxy__zbxu in ccgvr__mzf:
            nsew__liubs += f'  for i in range(len(blk_{laxy__zbxu})):\n'
            ilea__bpydi[f'col_indices_{laxy__zbxu}'] = np.array(table.
                block_to_arr_ind[laxy__zbxu], dtype=np.int64)
            nsew__liubs += f'    col_loc = col_indices_{laxy__zbxu}[i]\n'
            if qudg__pyj is not None:
                nsew__liubs += f'    if col_loc not in used_cols_set:\n'
                nsew__liubs += f'        continue\n'
            if popun__kogqr:
                xkuh__ceo = 'i'
            else:
                xkuh__ceo = 'col_loc'
            if not shk__pbwhk:
                nsew__liubs += (
                    f'    {hrkz__bzug}[{xkuh__ceo}] = blk_{laxy__zbxu}[i]\n')
            elif xttze__bhqnw:
                nsew__liubs += f"""    {hrkz__bzug}[{xkuh__ceo}] = blk_{laxy__zbxu}[i].{func_name}()
"""
            else:
                nsew__liubs += (
                    f'    {hrkz__bzug}[{xkuh__ceo}] = {func_name}(blk_{laxy__zbxu}[i])\n'
                    )
        if popun__kogqr:
            nsew__liubs += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {hrkz__bzug}, {laxy__zbxu})
"""
    if popun__kogqr:
        nsew__liubs += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        nsew__liubs += '  return out_table\n'
    else:
        nsew__liubs += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    wppzq__tcqbh = {}
    exec(nsew__liubs, ilea__bpydi, wppzq__tcqbh)
    return wppzq__tcqbh['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    phlta__jzcwj = args[0]
    if equiv_set.has_shape(phlta__jzcwj):
        return ArrayAnalysis.AnalyzeResult(shape=phlta__jzcwj, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    ilea__bpydi = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.
        distributed_api.Reduce_Type.Sum.value)}
    nsew__liubs = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    nsew__liubs += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for laxy__zbxu in table.type_to_blk.values():
        nsew__liubs += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {laxy__zbxu})\n'
            )
        ilea__bpydi[f'col_indices_{laxy__zbxu}'] = np.array(table.
            block_to_arr_ind[laxy__zbxu], dtype=np.int64)
        nsew__liubs += '  for i in range(len(blk)):\n'
        nsew__liubs += f'    col_loc = col_indices_{laxy__zbxu}[i]\n'
        nsew__liubs += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    nsew__liubs += '  if parallel:\n'
    nsew__liubs += '    for i in range(start_offset, len(out_arr)):\n'
    nsew__liubs += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    wppzq__tcqbh = {}
    exec(nsew__liubs, ilea__bpydi, wppzq__tcqbh)
    return wppzq__tcqbh['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    pcm__qtmr = table.type_to_blk[arr_type]
    ilea__bpydi = {'bodo': bodo}
    ilea__bpydi['col_indices'] = np.array(table.block_to_arr_ind[pcm__qtmr],
        dtype=np.int64)
    vysbq__ckuq = col_nums_meta.instance_type
    ilea__bpydi['col_nums'] = np.array(vysbq__ckuq.meta, np.int64)
    nsew__liubs = 'def impl(table, col_nums_meta, arr_type):\n'
    nsew__liubs += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {pcm__qtmr})\n')
    nsew__liubs += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    nsew__liubs += '  n = len(table)\n'
    zta__fst = bodo.utils.typing.is_str_arr_type(arr_type)
    if zta__fst:
        nsew__liubs += '  total_chars = 0\n'
        nsew__liubs += '  for c in col_nums:\n'
        nsew__liubs += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        nsew__liubs += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        nsew__liubs += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        nsew__liubs += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        nsew__liubs += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    nsew__liubs += '  for i in range(len(col_nums)):\n'
    nsew__liubs += '    c = col_nums[i]\n'
    if not zta__fst:
        nsew__liubs += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    nsew__liubs += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    nsew__liubs += '    off = i * n\n'
    nsew__liubs += '    for j in range(len(arr)):\n'
    nsew__liubs += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    nsew__liubs += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    nsew__liubs += '      else:\n'
    nsew__liubs += '        out_arr[off+j] = arr[j]\n'
    nsew__liubs += '  return out_arr\n'
    yhtml__hzgw = {}
    exec(nsew__liubs, ilea__bpydi, yhtml__hzgw)
    eyjnm__eho = yhtml__hzgw['impl']
    return eyjnm__eho


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    tbw__csiz = not is_overload_false(copy)
    aym__rbksx = is_overload_true(copy)
    ilea__bpydi = {'bodo': bodo}
    xxmwe__lsozf = table.arr_types
    mfisj__creyy = new_table_typ.arr_types
    zyj__qdj: Set[int] = set()
    wvlv__zge: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    aeko__ljd: Set[types.Type] = set()
    for otluf__duw, emvj__bhwkp in enumerate(xxmwe__lsozf):
        amy__kcn = mfisj__creyy[otluf__duw]
        if emvj__bhwkp == amy__kcn:
            aeko__ljd.add(emvj__bhwkp)
        else:
            zyj__qdj.add(otluf__duw)
            wvlv__zge[amy__kcn].add(emvj__bhwkp)
    nsew__liubs = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    nsew__liubs += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    nsew__liubs += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    ffri__vpv = set(range(len(xxmwe__lsozf)))
    kyh__mdz = ffri__vpv - zyj__qdj
    if not is_overload_none(used_cols):
        dvbgk__bfzw = used_cols.instance_type
        oni__fprub = set(dvbgk__bfzw.meta)
        zyj__qdj = zyj__qdj & oni__fprub
        kyh__mdz = kyh__mdz & oni__fprub
        ccgvr__mzf = set([table.block_nums[otluf__duw] for otluf__duw in
            oni__fprub])
    else:
        oni__fprub = None
    ilea__bpydi['cast_cols'] = np.array(list(zyj__qdj), dtype=np.int64)
    ilea__bpydi['copied_cols'] = np.array(list(kyh__mdz), dtype=np.int64)
    nsew__liubs += f'  copied_cols_set = set(copied_cols)\n'
    nsew__liubs += f'  cast_cols_set = set(cast_cols)\n'
    for jpvs__ftb, laxy__zbxu in new_table_typ.type_to_blk.items():
        ilea__bpydi[f'typ_list_{laxy__zbxu}'] = types.List(jpvs__ftb)
        nsew__liubs += f"""  out_arr_list_{laxy__zbxu} = bodo.hiframes.table.alloc_list_like(typ_list_{laxy__zbxu}, {len(new_table_typ.block_to_arr_ind[laxy__zbxu])}, False)
"""
        if jpvs__ftb in aeko__ljd:
            nxmd__uza = table.type_to_blk[jpvs__ftb]
            if oni__fprub is None or nxmd__uza in ccgvr__mzf:
                cztn__vvvpy = table.block_to_arr_ind[nxmd__uza]
                apq__pue = [new_table_typ.block_offsets[rkx__gduqa] for
                    rkx__gduqa in cztn__vvvpy]
                ilea__bpydi[f'new_idx_{nxmd__uza}'] = np.array(apq__pue, np
                    .int64)
                ilea__bpydi[f'orig_arr_inds_{nxmd__uza}'] = np.array(
                    cztn__vvvpy, np.int64)
                nsew__liubs += f"""  arr_list_{nxmd__uza} = bodo.hiframes.table.get_table_block(table, {nxmd__uza})
"""
                nsew__liubs += (
                    f'  for i in range(len(arr_list_{nxmd__uza})):\n')
                nsew__liubs += (
                    f'    arr_ind_{nxmd__uza} = orig_arr_inds_{nxmd__uza}[i]\n'
                    )
                nsew__liubs += (
                    f'    if arr_ind_{nxmd__uza} not in copied_cols_set:\n')
                nsew__liubs += f'      continue\n'
                nsew__liubs += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{nxmd__uza}, i, arr_ind_{nxmd__uza})
"""
                nsew__liubs += (
                    f'    out_idx_{laxy__zbxu}_{nxmd__uza} = new_idx_{nxmd__uza}[i]\n'
                    )
                nsew__liubs += (
                    f'    arr_val_{nxmd__uza} = arr_list_{nxmd__uza}[i]\n')
                if aym__rbksx:
                    nsew__liubs += (
                        f'    arr_val_{nxmd__uza} = arr_val_{nxmd__uza}.copy()\n'
                        )
                elif tbw__csiz:
                    nsew__liubs += f"""    arr_val_{nxmd__uza} = arr_val_{nxmd__uza}.copy() if copy else arr_val_{laxy__zbxu}
"""
                nsew__liubs += f"""    out_arr_list_{laxy__zbxu}[out_idx_{laxy__zbxu}_{nxmd__uza}] = arr_val_{nxmd__uza}
"""
    kuji__eqj = set()
    for jpvs__ftb, laxy__zbxu in new_table_typ.type_to_blk.items():
        if jpvs__ftb in wvlv__zge:
            if isinstance(jpvs__ftb, bodo.IntegerArrayType):
                cgebv__vzia = jpvs__ftb.get_pandas_scalar_type_instance.name
            else:
                cgebv__vzia = jpvs__ftb.dtype
            ilea__bpydi[f'typ_{laxy__zbxu}'] = cgebv__vzia
            cnhq__rariu = wvlv__zge[jpvs__ftb]
            for itrqd__nucxk in cnhq__rariu:
                nxmd__uza = table.type_to_blk[itrqd__nucxk]
                if oni__fprub is None or nxmd__uza in ccgvr__mzf:
                    if (itrqd__nucxk not in aeko__ljd and itrqd__nucxk not in
                        kuji__eqj):
                        cztn__vvvpy = table.block_to_arr_ind[nxmd__uza]
                        apq__pue = [new_table_typ.block_offsets[rkx__gduqa] for
                            rkx__gduqa in cztn__vvvpy]
                        ilea__bpydi[f'new_idx_{nxmd__uza}'] = np.array(apq__pue
                            , np.int64)
                        ilea__bpydi[f'orig_arr_inds_{nxmd__uza}'] = np.array(
                            cztn__vvvpy, np.int64)
                        nsew__liubs += f"""  arr_list_{nxmd__uza} = bodo.hiframes.table.get_table_block(table, {nxmd__uza})
"""
                    kuji__eqj.add(itrqd__nucxk)
                    nsew__liubs += (
                        f'  for i in range(len(arr_list_{nxmd__uza})):\n')
                    nsew__liubs += (
                        f'    arr_ind_{nxmd__uza} = orig_arr_inds_{nxmd__uza}[i]\n'
                        )
                    nsew__liubs += (
                        f'    if arr_ind_{nxmd__uza} not in cast_cols_set:\n')
                    nsew__liubs += f'      continue\n'
                    nsew__liubs += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{nxmd__uza}, i, arr_ind_{nxmd__uza})
"""
                    nsew__liubs += f"""    out_idx_{laxy__zbxu}_{nxmd__uza} = new_idx_{nxmd__uza}[i]
"""
                    nsew__liubs += f"""    arr_val_{laxy__zbxu} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{nxmd__uza}[i], typ_{laxy__zbxu}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    nsew__liubs += f"""    out_arr_list_{laxy__zbxu}[out_idx_{laxy__zbxu}_{nxmd__uza}] = arr_val_{laxy__zbxu}
"""
        nsew__liubs += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{laxy__zbxu}, {laxy__zbxu})
"""
    nsew__liubs += '  return out_table\n'
    wppzq__tcqbh = {}
    exec(nsew__liubs, ilea__bpydi, wppzq__tcqbh)
    return wppzq__tcqbh['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    phlta__jzcwj = args[0]
    if equiv_set.has_shape(phlta__jzcwj):
        return ArrayAnalysis.AnalyzeResult(shape=phlta__jzcwj, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
