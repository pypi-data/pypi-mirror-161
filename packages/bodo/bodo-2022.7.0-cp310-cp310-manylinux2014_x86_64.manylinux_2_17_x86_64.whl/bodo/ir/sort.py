"""IR node for the data sorting"""
from collections import defaultdict
from typing import List, Set, Tuple, Union
import numba
import numpy as np
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes, replace_vars_inner, visit_vars_inner
import bodo
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, py_data_to_cpp_table, sort_values_table
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, _find_used_columns, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import MetaType, type_has_unknown_cats
from bodo.utils.utils import gen_getitem


class Sort(ir.Stmt):

    def __init__(self, df_in: str, df_out: str, in_vars: List[ir.Var],
        out_vars: List[ir.Var], key_inds: Tuple[int], inplace: bool, loc:
        ir.Loc, ascending_list: Union[List[bool], bool]=True, na_position:
        Union[List[str], str]='last', is_table_format: bool=False,
        num_table_arrays: int=0):
        self.df_in = df_in
        self.df_out = df_out
        self.in_vars = in_vars
        self.out_vars = out_vars
        self.key_inds = key_inds
        self.inplace = inplace
        self.is_table_format = is_table_format
        self.num_table_arrays = num_table_arrays
        self.dead_var_inds: Set[int] = set()
        self.dead_key_var_inds: Set[int] = set()
        if isinstance(na_position, str):
            if na_position == 'last':
                self.na_position_b = (True,) * len(key_inds)
            else:
                self.na_position_b = (False,) * len(key_inds)
        else:
            self.na_position_b = tuple([(True if hzoy__hbrz == 'last' else 
                False) for hzoy__hbrz in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [npj__geiek for npj__geiek in self.in_vars if npj__geiek is not
            None]

    def get_live_out_vars(self):
        return [npj__geiek for npj__geiek in self.out_vars if npj__geiek is not
            None]

    def __repr__(self):
        rxgbj__zsr = ', '.join(npj__geiek.name for npj__geiek in self.
            get_live_in_vars())
        yqb__ymd = f'{self.df_in}{{{rxgbj__zsr}}}'
        bzcl__pfvh = ', '.join(npj__geiek.name for npj__geiek in self.
            get_live_out_vars())
        kxgb__ifrvm = f'{self.df_out}{{{bzcl__pfvh}}}'
        return f'Sort (keys: {self.key_inds}): {yqb__ymd} {kxgb__ifrvm}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    fec__fsy = []
    for bvumk__evrqn in sort_node.get_live_in_vars():
        asu__frg = equiv_set.get_shape(bvumk__evrqn)
        if asu__frg is not None:
            fec__fsy.append(asu__frg[0])
    if len(fec__fsy) > 1:
        equiv_set.insert_equiv(*fec__fsy)
    hri__poia = []
    fec__fsy = []
    for bvumk__evrqn in sort_node.get_live_out_vars():
        vstbu__rfyvr = typemap[bvumk__evrqn.name]
        vmlpw__uxtp = array_analysis._gen_shape_call(equiv_set,
            bvumk__evrqn, vstbu__rfyvr.ndim, None, hri__poia)
        equiv_set.insert_equiv(bvumk__evrqn, vmlpw__uxtp)
        fec__fsy.append(vmlpw__uxtp[0])
        equiv_set.define(bvumk__evrqn, set())
    if len(fec__fsy) > 1:
        equiv_set.insert_equiv(*fec__fsy)
    return [], hri__poia


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    reuhr__tjd = sort_node.get_live_in_vars()
    ohrby__mift = sort_node.get_live_out_vars()
    ofe__wqr = Distribution.OneD
    for bvumk__evrqn in reuhr__tjd:
        ofe__wqr = Distribution(min(ofe__wqr.value, array_dists[
            bvumk__evrqn.name].value))
    jiu__fznw = Distribution(min(ofe__wqr.value, Distribution.OneD_Var.value))
    for bvumk__evrqn in ohrby__mift:
        if bvumk__evrqn.name in array_dists:
            jiu__fznw = Distribution(min(jiu__fznw.value, array_dists[
                bvumk__evrqn.name].value))
    if jiu__fznw != Distribution.OneD_Var:
        ofe__wqr = jiu__fznw
    for bvumk__evrqn in reuhr__tjd:
        array_dists[bvumk__evrqn.name] = ofe__wqr
    for bvumk__evrqn in ohrby__mift:
        array_dists[bvumk__evrqn.name] = jiu__fznw


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for rpiii__zaich, dljv__ykuep in enumerate(sort_node.out_vars):
        fcj__boi = sort_node.in_vars[rpiii__zaich]
        if fcj__boi is not None and dljv__ykuep is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                dljv__ykuep.name, src=fcj__boi.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for bvumk__evrqn in sort_node.get_live_out_vars():
            definitions[bvumk__evrqn.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for rpiii__zaich in range(len(sort_node.in_vars)):
        if sort_node.in_vars[rpiii__zaich] is not None:
            sort_node.in_vars[rpiii__zaich] = visit_vars_inner(sort_node.
                in_vars[rpiii__zaich], callback, cbdata)
        if sort_node.out_vars[rpiii__zaich] is not None:
            sort_node.out_vars[rpiii__zaich] = visit_vars_inner(sort_node.
                out_vars[rpiii__zaich], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        fztb__zno = sort_node.out_vars[0]
        if fztb__zno is not None and fztb__zno.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            wvl__nzom = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & wvl__nzom)
            sort_node.dead_var_inds.update(dead_cols - wvl__nzom)
            if len(wvl__nzom & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for rpiii__zaich in range(1, len(sort_node.out_vars)):
            npj__geiek = sort_node.out_vars[rpiii__zaich]
            if npj__geiek is not None and npj__geiek.name not in lives:
                sort_node.out_vars[rpiii__zaich] = None
                kifa__fkye = sort_node.num_table_arrays + rpiii__zaich - 1
                if kifa__fkye in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(kifa__fkye)
                else:
                    sort_node.dead_var_inds.add(kifa__fkye)
                    sort_node.in_vars[rpiii__zaich] = None
    else:
        for rpiii__zaich in range(len(sort_node.out_vars)):
            npj__geiek = sort_node.out_vars[rpiii__zaich]
            if npj__geiek is not None and npj__geiek.name not in lives:
                sort_node.out_vars[rpiii__zaich] = None
                if rpiii__zaich in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(rpiii__zaich)
                else:
                    sort_node.dead_var_inds.add(rpiii__zaich)
                    sort_node.in_vars[rpiii__zaich] = None
    if all(npj__geiek is None for npj__geiek in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({npj__geiek.name for npj__geiek in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({npj__geiek.name for npj__geiek in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    kgnsl__ebkq = set()
    if not sort_node.inplace:
        kgnsl__ebkq.update({npj__geiek.name for npj__geiek in sort_node.
            get_live_out_vars()})
    return set(), kgnsl__ebkq


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for rpiii__zaich in range(len(sort_node.in_vars)):
        if sort_node.in_vars[rpiii__zaich] is not None:
            sort_node.in_vars[rpiii__zaich] = replace_vars_inner(sort_node.
                in_vars[rpiii__zaich], var_dict)
        if sort_node.out_vars[rpiii__zaich] is not None:
            sort_node.out_vars[rpiii__zaich] = replace_vars_inner(sort_node
                .out_vars[rpiii__zaich], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for npj__geiek in (in_vars + out_vars):
            if array_dists[npj__geiek.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                npj__geiek.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        djeft__rxyz = []
        for npj__geiek in in_vars:
            zxfqc__nxmq = _copy_array_nodes(npj__geiek, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            djeft__rxyz.append(zxfqc__nxmq)
        in_vars = djeft__rxyz
    out_types = [(typemap[npj__geiek.name] if npj__geiek is not None else
        types.none) for npj__geiek in sort_node.out_vars]
    pzgg__wnqnu, lekg__top = get_sort_cpp_section(sort_node, out_types,
        parallel)
    eai__grlw = {}
    exec(pzgg__wnqnu, {}, eai__grlw)
    mozw__zijex = eai__grlw['f']
    lekg__top.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    lekg__top.update({f'out_type{rpiii__zaich}': out_types[rpiii__zaich] for
        rpiii__zaich in range(len(out_types))})
    yuip__bwh = compile_to_numba_ir(mozw__zijex, lekg__top, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[npj__geiek.
        name] for npj__geiek in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(yuip__bwh, in_vars)
    rnqu__jzmre = yuip__bwh.body[-2].value.value
    nodes += yuip__bwh.body[:-2]
    for rpiii__zaich, npj__geiek in enumerate(out_vars):
        gen_getitem(npj__geiek, rnqu__jzmre, rpiii__zaich, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    nmafq__tbxi = lambda arr: arr.copy()
    jql__tap = None
    if isinstance(typemap[var.name], TableType):
        wnoi__lsjtk = len(typemap[var.name].arr_types)
        jql__tap = set(range(wnoi__lsjtk)) - dead_cols
        jql__tap = MetaType(tuple(sorted(jql__tap)))
        nmafq__tbxi = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    yuip__bwh = compile_to_numba_ir(nmafq__tbxi, {'bodo': bodo, 'types':
        types, '_used_columns': jql__tap}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(yuip__bwh, [var])
    nodes += yuip__bwh.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    vcjk__per = len(sort_node.key_inds)
    wgd__rbniz = len(sort_node.in_vars)
    vjot__pxsk = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + wgd__rbniz - 1 if sort_node.
        is_table_format else wgd__rbniz)
    vxzvk__uxgu, pshp__coyz, memsv__qbyu = _get_cpp_col_ind_mappings(sort_node
        .key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols
        )
    cdri__vhpug = []
    if sort_node.is_table_format:
        cdri__vhpug.append('arg0')
        for rpiii__zaich in range(1, wgd__rbniz):
            kifa__fkye = sort_node.num_table_arrays + rpiii__zaich - 1
            if kifa__fkye not in sort_node.dead_var_inds:
                cdri__vhpug.append(f'arg{kifa__fkye}')
    else:
        for rpiii__zaich in range(n_cols):
            if rpiii__zaich not in sort_node.dead_var_inds:
                cdri__vhpug.append(f'arg{rpiii__zaich}')
    pzgg__wnqnu = f"def f({', '.join(cdri__vhpug)}):\n"
    if sort_node.is_table_format:
        znwoq__ocj = ',' if wgd__rbniz - 1 == 1 else ''
        ucht__udp = []
        for rpiii__zaich in range(sort_node.num_table_arrays, n_cols):
            if rpiii__zaich in sort_node.dead_var_inds:
                ucht__udp.append('None')
            else:
                ucht__udp.append(f'arg{rpiii__zaich}')
        pzgg__wnqnu += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(ucht__udp)}{znwoq__ocj}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        uwu__jcy = {nrqti__pvfv: rpiii__zaich for rpiii__zaich, nrqti__pvfv in
            enumerate(vxzvk__uxgu)}
        crevg__qod = [None] * len(vxzvk__uxgu)
        for rpiii__zaich in range(n_cols):
            nepi__jeamh = uwu__jcy.get(rpiii__zaich, -1)
            if nepi__jeamh != -1:
                crevg__qod[nepi__jeamh] = f'array_to_info(arg{rpiii__zaich})'
        pzgg__wnqnu += '  info_list_total = [{}]\n'.format(','.join(crevg__qod)
            )
        pzgg__wnqnu += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    pzgg__wnqnu += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if ebg__mbh else '0' for ebg__mbh in sort_node.
        ascending_list))
    pzgg__wnqnu += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if ebg__mbh else '0' for ebg__mbh in sort_node.na_position_b))
    pzgg__wnqnu += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if rpiii__zaich in memsv__qbyu else '0' for rpiii__zaich in
        range(vcjk__per)))
    pzgg__wnqnu += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    pzgg__wnqnu += f"""  out_cpp_table = sort_values_table(in_cpp_table, {vcjk__per}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        znwoq__ocj = ',' if vjot__pxsk == 1 else ''
        mdk__tdx = (
            f"({', '.join(f'out_type{rpiii__zaich}' if not type_has_unknown_cats(out_types[rpiii__zaich]) else f'arg{rpiii__zaich}' for rpiii__zaich in range(vjot__pxsk))}{znwoq__ocj})"
            )
        pzgg__wnqnu += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {mdk__tdx}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        uwu__jcy = {nrqti__pvfv: rpiii__zaich for rpiii__zaich, nrqti__pvfv in
            enumerate(pshp__coyz)}
        crevg__qod = []
        for rpiii__zaich in range(n_cols):
            nepi__jeamh = uwu__jcy.get(rpiii__zaich, -1)
            if nepi__jeamh != -1:
                yvo__jajg = (f'out_type{rpiii__zaich}' if not
                    type_has_unknown_cats(out_types[rpiii__zaich]) else
                    f'arg{rpiii__zaich}')
                pzgg__wnqnu += f"""  out{rpiii__zaich} = info_to_array(info_from_table(out_cpp_table, {nepi__jeamh}), {yvo__jajg})
"""
                crevg__qod.append(f'out{rpiii__zaich}')
        znwoq__ocj = ',' if len(crevg__qod) == 1 else ''
        nzkj__ooknl = f"({', '.join(crevg__qod)}{znwoq__ocj})"
        pzgg__wnqnu += f'  out_data = {nzkj__ooknl}\n'
    pzgg__wnqnu += '  delete_table(out_cpp_table)\n'
    pzgg__wnqnu += '  delete_table(in_cpp_table)\n'
    pzgg__wnqnu += f'  return out_data\n'
    return pzgg__wnqnu, {'in_col_inds': MetaType(tuple(vxzvk__uxgu)),
        'out_col_inds': MetaType(tuple(pshp__coyz))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    vxzvk__uxgu = []
    pshp__coyz = []
    memsv__qbyu = []
    for nrqti__pvfv, rpiii__zaich in enumerate(key_inds):
        vxzvk__uxgu.append(rpiii__zaich)
        if rpiii__zaich in dead_key_var_inds:
            memsv__qbyu.append(nrqti__pvfv)
        else:
            pshp__coyz.append(rpiii__zaich)
    for rpiii__zaich in range(n_cols):
        if rpiii__zaich in dead_var_inds or rpiii__zaich in key_inds:
            continue
        vxzvk__uxgu.append(rpiii__zaich)
        pshp__coyz.append(rpiii__zaich)
    return vxzvk__uxgu, pshp__coyz, memsv__qbyu


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    abe__dyt = sort_node.in_vars[0].name
    tbyr__niqdi = sort_node.out_vars[0].name
    vvxbp__atnn, ist__mngb, cpz__ucha = block_use_map[abe__dyt]
    if ist__mngb or cpz__ucha:
        return
    ycxbj__lnzn, bzuw__zzo, mnqb__lyh = _compute_table_column_uses(tbyr__niqdi,
        table_col_use_map, equiv_vars)
    tfte__ctgo = set(rpiii__zaich for rpiii__zaich in sort_node.key_inds if
        rpiii__zaich < sort_node.num_table_arrays)
    block_use_map[abe__dyt
        ] = vvxbp__atnn | ycxbj__lnzn | tfte__ctgo, bzuw__zzo or mnqb__lyh, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    wnoi__lsjtk = sort_node.num_table_arrays
    tbyr__niqdi = sort_node.out_vars[0].name
    jql__tap = _find_used_columns(tbyr__niqdi, wnoi__lsjtk, column_live_map,
        equiv_vars)
    if jql__tap is None:
        return False
    tej__msm = set(range(wnoi__lsjtk)) - jql__tap
    tfte__ctgo = set(rpiii__zaich for rpiii__zaich in sort_node.key_inds if
        rpiii__zaich < wnoi__lsjtk)
    qpl__luro = sort_node.dead_key_var_inds | tej__msm & tfte__ctgo
    kdp__yexo = sort_node.dead_var_inds | tej__msm - tfte__ctgo
    jhxic__tbxh = (qpl__luro != sort_node.dead_key_var_inds) | (kdp__yexo !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = qpl__luro
    sort_node.dead_var_inds = kdp__yexo
    return jhxic__tbxh


remove_dead_column_extensions[Sort] = sort_remove_dead_column
