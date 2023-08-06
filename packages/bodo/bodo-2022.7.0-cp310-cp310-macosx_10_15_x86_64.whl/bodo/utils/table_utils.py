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
    aml__mswfm = not is_overload_none(func_name)
    if aml__mswfm:
        func_name = get_overload_const_str(func_name)
        zirvs__sgy = get_overload_const_bool(is_method)
    pdz__extho = out_arr_typ.instance_type if isinstance(out_arr_typ, types
        .TypeRef) else out_arr_typ
    ivbpc__aswj = pdz__extho == types.none
    fqoz__mnw = len(table.arr_types)
    if ivbpc__aswj:
        mnmt__todm = table
    else:
        nhiez__bjfi = tuple([pdz__extho] * fqoz__mnw)
        mnmt__todm = TableType(nhiez__bjfi)
    orqsw__xomg = {'bodo': bodo, 'lst_dtype': pdz__extho, 'table_typ':
        mnmt__todm}
    jbzom__uofk = (
        'def impl(table, func_name, out_arr_typ, is_method, used_cols=None):\n'
        )
    if ivbpc__aswj:
        jbzom__uofk += (
            f'  out_table = bodo.hiframes.table.init_table(table, False)\n')
        jbzom__uofk += f'  l = len(table)\n'
    else:
        jbzom__uofk += f"""  out_list = bodo.hiframes.table.alloc_empty_list_type({fqoz__mnw}, lst_dtype)
"""
    if not is_overload_none(used_cols):
        glk__zejmt = used_cols.instance_type
        amhhp__tjit = np.array(glk__zejmt.meta, dtype=np.int64)
        orqsw__xomg['used_cols_glbl'] = amhhp__tjit
        whj__xzrl = set([table.block_nums[waz__jdd] for waz__jdd in
            amhhp__tjit])
        jbzom__uofk += f'  used_cols_set = set(used_cols_glbl)\n'
    else:
        jbzom__uofk += f'  used_cols_set = None\n'
        amhhp__tjit = None
    jbzom__uofk += (
        f'  bodo.hiframes.table.ensure_table_unboxed(table, used_cols_set)\n')
    for rpd__wuqy in table.type_to_blk.values():
        jbzom__uofk += f"""  blk_{rpd__wuqy} = bodo.hiframes.table.get_table_block(table, {rpd__wuqy})
"""
        if ivbpc__aswj:
            jbzom__uofk += f"""  out_list_{rpd__wuqy} = bodo.hiframes.table.alloc_list_like(blk_{rpd__wuqy}, len(blk_{rpd__wuqy}), False)
"""
            usg__rtfxo = f'out_list_{rpd__wuqy}'
        else:
            usg__rtfxo = 'out_list'
        if amhhp__tjit is None or rpd__wuqy in whj__xzrl:
            jbzom__uofk += f'  for i in range(len(blk_{rpd__wuqy})):\n'
            orqsw__xomg[f'col_indices_{rpd__wuqy}'] = np.array(table.
                block_to_arr_ind[rpd__wuqy], dtype=np.int64)
            jbzom__uofk += f'    col_loc = col_indices_{rpd__wuqy}[i]\n'
            if amhhp__tjit is not None:
                jbzom__uofk += f'    if col_loc not in used_cols_set:\n'
                jbzom__uofk += f'        continue\n'
            if ivbpc__aswj:
                wbqyz__efeq = 'i'
            else:
                wbqyz__efeq = 'col_loc'
            if not aml__mswfm:
                jbzom__uofk += (
                    f'    {usg__rtfxo}[{wbqyz__efeq}] = blk_{rpd__wuqy}[i]\n')
            elif zirvs__sgy:
                jbzom__uofk += f"""    {usg__rtfxo}[{wbqyz__efeq}] = blk_{rpd__wuqy}[i].{func_name}()
"""
            else:
                jbzom__uofk += f"""    {usg__rtfxo}[{wbqyz__efeq}] = {func_name}(blk_{rpd__wuqy}[i])
"""
        if ivbpc__aswj:
            jbzom__uofk += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, {usg__rtfxo}, {rpd__wuqy})
"""
    if ivbpc__aswj:
        jbzom__uofk += (
            f'  out_table = bodo.hiframes.table.set_table_len(out_table, l)\n')
        jbzom__uofk += '  return out_table\n'
    else:
        jbzom__uofk += """  return bodo.hiframes.table.init_table_from_lists((out_list,), table_typ)
"""
    exihg__ppkvw = {}
    exec(jbzom__uofk, orqsw__xomg, exihg__ppkvw)
    return exihg__ppkvw['impl']


def generate_mappable_table_func_equiv(self, scope, equiv_set, loc, args, kws):
    genl__mcmvm = args[0]
    if equiv_set.has_shape(genl__mcmvm):
        return ArrayAnalysis.AnalyzeResult(shape=genl__mcmvm, pre=[])
    return None


(ArrayAnalysis.
    _analyze_op_call_bodo_utils_table_utils_generate_mappable_table_func
    ) = generate_mappable_table_func_equiv


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def generate_table_nbytes(table, out_arr, start_offset, parallel=False):
    orqsw__xomg = {'bodo': bodo, 'sum_op': np.int32(bodo.libs.
        distributed_api.Reduce_Type.Sum.value)}
    jbzom__uofk = 'def impl(table, out_arr, start_offset, parallel=False):\n'
    jbzom__uofk += '  bodo.hiframes.table.ensure_table_unboxed(table, None)\n'
    for rpd__wuqy in table.type_to_blk.values():
        jbzom__uofk += (
            f'  blk = bodo.hiframes.table.get_table_block(table, {rpd__wuqy})\n'
            )
        orqsw__xomg[f'col_indices_{rpd__wuqy}'] = np.array(table.
            block_to_arr_ind[rpd__wuqy], dtype=np.int64)
        jbzom__uofk += '  for i in range(len(blk)):\n'
        jbzom__uofk += f'    col_loc = col_indices_{rpd__wuqy}[i]\n'
        jbzom__uofk += '    out_arr[col_loc + start_offset] = blk[i].nbytes\n'
    jbzom__uofk += '  if parallel:\n'
    jbzom__uofk += '    for i in range(start_offset, len(out_arr)):\n'
    jbzom__uofk += (
        '      out_arr[i] = bodo.libs.distributed_api.dist_reduce(out_arr[i], sum_op)\n'
        )
    exihg__ppkvw = {}
    exec(jbzom__uofk, orqsw__xomg, exihg__ppkvw)
    return exihg__ppkvw['impl']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_concat(table, col_nums_meta, arr_type):
    arr_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type
    aalq__imtty = table.type_to_blk[arr_type]
    orqsw__xomg = {'bodo': bodo}
    orqsw__xomg['col_indices'] = np.array(table.block_to_arr_ind[
        aalq__imtty], dtype=np.int64)
    lffld__ctxu = col_nums_meta.instance_type
    orqsw__xomg['col_nums'] = np.array(lffld__ctxu.meta, np.int64)
    jbzom__uofk = 'def impl(table, col_nums_meta, arr_type):\n'
    jbzom__uofk += (
        f'  blk = bodo.hiframes.table.get_table_block(table, {aalq__imtty})\n')
    jbzom__uofk += (
        '  col_num_to_ind_in_blk = {c : i for i, c in enumerate(col_indices)}\n'
        )
    jbzom__uofk += '  n = len(table)\n'
    idpw__mtg = bodo.utils.typing.is_str_arr_type(arr_type)
    if idpw__mtg:
        jbzom__uofk += '  total_chars = 0\n'
        jbzom__uofk += '  for c in col_nums:\n'
        jbzom__uofk += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
        jbzom__uofk += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
        jbzom__uofk += (
            '    total_chars += bodo.libs.str_arr_ext.num_total_chars(arr)\n')
        jbzom__uofk += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n * len(col_nums), total_chars)
"""
    else:
        jbzom__uofk += """  out_arr = bodo.utils.utils.alloc_type(n * len(col_nums), arr_type, (-1,))
"""
    jbzom__uofk += '  for i in range(len(col_nums)):\n'
    jbzom__uofk += '    c = col_nums[i]\n'
    if not idpw__mtg:
        jbzom__uofk += """    bodo.hiframes.table.ensure_column_unboxed(table, blk, col_num_to_ind_in_blk[c], c)
"""
    jbzom__uofk += '    arr = blk[col_num_to_ind_in_blk[c]]\n'
    jbzom__uofk += '    off = i * n\n'
    jbzom__uofk += '    for j in range(len(arr)):\n'
    jbzom__uofk += '      if bodo.libs.array_kernels.isna(arr, j):\n'
    jbzom__uofk += '        bodo.libs.array_kernels.setna(out_arr, off+j)\n'
    jbzom__uofk += '      else:\n'
    jbzom__uofk += '        out_arr[off+j] = arr[j]\n'
    jbzom__uofk += '  return out_arr\n'
    jekdd__isal = {}
    exec(jbzom__uofk, orqsw__xomg, jekdd__isal)
    qyvx__ltoop = jekdd__isal['impl']
    return qyvx__ltoop


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_astype(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):
    new_table_typ = new_table_typ.instance_type
    duyd__pmw = not is_overload_false(copy)
    nmzua__fzd = is_overload_true(copy)
    orqsw__xomg = {'bodo': bodo}
    znk__edr = table.arr_types
    koxc__qxtwy = new_table_typ.arr_types
    qzur__zezdq: Set[int] = set()
    mohsp__hwc: Dict[types.Type, Set[types.Type]] = defaultdict(set)
    fvp__jeg: Set[types.Type] = set()
    for waz__jdd, ojsy__lupv in enumerate(znk__edr):
        zyxgp__zgvnl = koxc__qxtwy[waz__jdd]
        if ojsy__lupv == zyxgp__zgvnl:
            fvp__jeg.add(ojsy__lupv)
        else:
            qzur__zezdq.add(waz__jdd)
            mohsp__hwc[zyxgp__zgvnl].add(ojsy__lupv)
    jbzom__uofk = (
        'def impl(table, new_table_typ, copy, _bodo_nan_to_str, used_cols=None):\n'
        )
    jbzom__uofk += (
        f'  out_table = bodo.hiframes.table.init_table(new_table_typ, False)\n'
        )
    jbzom__uofk += (
        f'  out_table = bodo.hiframes.table.set_table_len(out_table, len(table))\n'
        )
    cir__frl = set(range(len(znk__edr)))
    sncz__kge = cir__frl - qzur__zezdq
    if not is_overload_none(used_cols):
        glk__zejmt = used_cols.instance_type
        eza__nfkg = set(glk__zejmt.meta)
        qzur__zezdq = qzur__zezdq & eza__nfkg
        sncz__kge = sncz__kge & eza__nfkg
        whj__xzrl = set([table.block_nums[waz__jdd] for waz__jdd in eza__nfkg])
    else:
        eza__nfkg = None
    orqsw__xomg['cast_cols'] = np.array(list(qzur__zezdq), dtype=np.int64)
    orqsw__xomg['copied_cols'] = np.array(list(sncz__kge), dtype=np.int64)
    jbzom__uofk += f'  copied_cols_set = set(copied_cols)\n'
    jbzom__uofk += f'  cast_cols_set = set(cast_cols)\n'
    for bnw__val, rpd__wuqy in new_table_typ.type_to_blk.items():
        orqsw__xomg[f'typ_list_{rpd__wuqy}'] = types.List(bnw__val)
        jbzom__uofk += f"""  out_arr_list_{rpd__wuqy} = bodo.hiframes.table.alloc_list_like(typ_list_{rpd__wuqy}, {len(new_table_typ.block_to_arr_ind[rpd__wuqy])}, False)
"""
        if bnw__val in fvp__jeg:
            rqp__alxq = table.type_to_blk[bnw__val]
            if eza__nfkg is None or rqp__alxq in whj__xzrl:
                rqskv__ylsm = table.block_to_arr_ind[rqp__alxq]
                iohe__bfey = [new_table_typ.block_offsets[hbbdv__oxkg] for
                    hbbdv__oxkg in rqskv__ylsm]
                orqsw__xomg[f'new_idx_{rqp__alxq}'] = np.array(iohe__bfey,
                    np.int64)
                orqsw__xomg[f'orig_arr_inds_{rqp__alxq}'] = np.array(
                    rqskv__ylsm, np.int64)
                jbzom__uofk += f"""  arr_list_{rqp__alxq} = bodo.hiframes.table.get_table_block(table, {rqp__alxq})
"""
                jbzom__uofk += (
                    f'  for i in range(len(arr_list_{rqp__alxq})):\n')
                jbzom__uofk += (
                    f'    arr_ind_{rqp__alxq} = orig_arr_inds_{rqp__alxq}[i]\n'
                    )
                jbzom__uofk += (
                    f'    if arr_ind_{rqp__alxq} not in copied_cols_set:\n')
                jbzom__uofk += f'      continue\n'
                jbzom__uofk += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{rqp__alxq}, i, arr_ind_{rqp__alxq})
"""
                jbzom__uofk += (
                    f'    out_idx_{rpd__wuqy}_{rqp__alxq} = new_idx_{rqp__alxq}[i]\n'
                    )
                jbzom__uofk += (
                    f'    arr_val_{rqp__alxq} = arr_list_{rqp__alxq}[i]\n')
                if nmzua__fzd:
                    jbzom__uofk += (
                        f'    arr_val_{rqp__alxq} = arr_val_{rqp__alxq}.copy()\n'
                        )
                elif duyd__pmw:
                    jbzom__uofk += f"""    arr_val_{rqp__alxq} = arr_val_{rqp__alxq}.copy() if copy else arr_val_{rpd__wuqy}
"""
                jbzom__uofk += f"""    out_arr_list_{rpd__wuqy}[out_idx_{rpd__wuqy}_{rqp__alxq}] = arr_val_{rqp__alxq}
"""
    ocf__hboju = set()
    for bnw__val, rpd__wuqy in new_table_typ.type_to_blk.items():
        if bnw__val in mohsp__hwc:
            if isinstance(bnw__val, bodo.IntegerArrayType):
                pma__uxw = bnw__val.get_pandas_scalar_type_instance.name
            else:
                pma__uxw = bnw__val.dtype
            orqsw__xomg[f'typ_{rpd__wuqy}'] = pma__uxw
            drli__egfcn = mohsp__hwc[bnw__val]
            for yvb__wqh in drli__egfcn:
                rqp__alxq = table.type_to_blk[yvb__wqh]
                if eza__nfkg is None or rqp__alxq in whj__xzrl:
                    if yvb__wqh not in fvp__jeg and yvb__wqh not in ocf__hboju:
                        rqskv__ylsm = table.block_to_arr_ind[rqp__alxq]
                        iohe__bfey = [new_table_typ.block_offsets[
                            hbbdv__oxkg] for hbbdv__oxkg in rqskv__ylsm]
                        orqsw__xomg[f'new_idx_{rqp__alxq}'] = np.array(
                            iohe__bfey, np.int64)
                        orqsw__xomg[f'orig_arr_inds_{rqp__alxq}'] = np.array(
                            rqskv__ylsm, np.int64)
                        jbzom__uofk += f"""  arr_list_{rqp__alxq} = bodo.hiframes.table.get_table_block(table, {rqp__alxq})
"""
                    ocf__hboju.add(yvb__wqh)
                    jbzom__uofk += (
                        f'  for i in range(len(arr_list_{rqp__alxq})):\n')
                    jbzom__uofk += (
                        f'    arr_ind_{rqp__alxq} = orig_arr_inds_{rqp__alxq}[i]\n'
                        )
                    jbzom__uofk += (
                        f'    if arr_ind_{rqp__alxq} not in cast_cols_set:\n')
                    jbzom__uofk += f'      continue\n'
                    jbzom__uofk += f"""    bodo.hiframes.table.ensure_column_unboxed(table, arr_list_{rqp__alxq}, i, arr_ind_{rqp__alxq})
"""
                    jbzom__uofk += (
                        f'    out_idx_{rpd__wuqy}_{rqp__alxq} = new_idx_{rqp__alxq}[i]\n'
                        )
                    jbzom__uofk += f"""    arr_val_{rpd__wuqy} =  bodo.utils.conversion.fix_arr_dtype(arr_list_{rqp__alxq}[i], typ_{rpd__wuqy}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)
"""
                    jbzom__uofk += f"""    out_arr_list_{rpd__wuqy}[out_idx_{rpd__wuqy}_{rqp__alxq}] = arr_val_{rpd__wuqy}
"""
        jbzom__uofk += f"""  out_table = bodo.hiframes.table.set_table_block(out_table, out_arr_list_{rpd__wuqy}, {rpd__wuqy})
"""
    jbzom__uofk += '  return out_table\n'
    exihg__ppkvw = {}
    exec(jbzom__uofk, orqsw__xomg, exihg__ppkvw)
    return exihg__ppkvw['impl']


def table_astype_equiv(self, scope, equiv_set, loc, args, kws):
    genl__mcmvm = args[0]
    if equiv_set.has_shape(genl__mcmvm):
        return ArrayAnalysis.AnalyzeResult(shape=genl__mcmvm, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_utils_table_utils_table_astype = (
    table_astype_equiv)
