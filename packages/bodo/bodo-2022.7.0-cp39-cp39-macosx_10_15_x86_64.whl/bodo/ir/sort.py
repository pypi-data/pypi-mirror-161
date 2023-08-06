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
            self.na_position_b = tuple([(True if evd__dpb == 'last' else 
                False) for evd__dpb in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [iupp__jjt for iupp__jjt in self.in_vars if iupp__jjt is not
            None]

    def get_live_out_vars(self):
        return [iupp__jjt for iupp__jjt in self.out_vars if iupp__jjt is not
            None]

    def __repr__(self):
        vuq__svxxt = ', '.join(iupp__jjt.name for iupp__jjt in self.
            get_live_in_vars())
        leqym__efj = f'{self.df_in}{{{vuq__svxxt}}}'
        owj__tbaea = ', '.join(iupp__jjt.name for iupp__jjt in self.
            get_live_out_vars())
        ckaxz__mpp = f'{self.df_out}{{{owj__tbaea}}}'
        return f'Sort (keys: {self.key_inds}): {leqym__efj} {ckaxz__mpp}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    tnnr__uqp = []
    for qii__yim in sort_node.get_live_in_vars():
        lsvk__tdm = equiv_set.get_shape(qii__yim)
        if lsvk__tdm is not None:
            tnnr__uqp.append(lsvk__tdm[0])
    if len(tnnr__uqp) > 1:
        equiv_set.insert_equiv(*tnnr__uqp)
    bddy__nkki = []
    tnnr__uqp = []
    for qii__yim in sort_node.get_live_out_vars():
        ekh__sjk = typemap[qii__yim.name]
        rjcmy__vxx = array_analysis._gen_shape_call(equiv_set, qii__yim,
            ekh__sjk.ndim, None, bddy__nkki)
        equiv_set.insert_equiv(qii__yim, rjcmy__vxx)
        tnnr__uqp.append(rjcmy__vxx[0])
        equiv_set.define(qii__yim, set())
    if len(tnnr__uqp) > 1:
        equiv_set.insert_equiv(*tnnr__uqp)
    return [], bddy__nkki


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    wjp__jyktr = sort_node.get_live_in_vars()
    exe__mgby = sort_node.get_live_out_vars()
    mceug__nvhxi = Distribution.OneD
    for qii__yim in wjp__jyktr:
        mceug__nvhxi = Distribution(min(mceug__nvhxi.value, array_dists[
            qii__yim.name].value))
    mwmdv__taxy = Distribution(min(mceug__nvhxi.value, Distribution.
        OneD_Var.value))
    for qii__yim in exe__mgby:
        if qii__yim.name in array_dists:
            mwmdv__taxy = Distribution(min(mwmdv__taxy.value, array_dists[
                qii__yim.name].value))
    if mwmdv__taxy != Distribution.OneD_Var:
        mceug__nvhxi = mwmdv__taxy
    for qii__yim in wjp__jyktr:
        array_dists[qii__yim.name] = mceug__nvhxi
    for qii__yim in exe__mgby:
        array_dists[qii__yim.name] = mwmdv__taxy


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for jqnua__gpllj, eynna__lpg in enumerate(sort_node.out_vars):
        bheem__vhxiz = sort_node.in_vars[jqnua__gpllj]
        if bheem__vhxiz is not None and eynna__lpg is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                eynna__lpg.name, src=bheem__vhxiz.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for qii__yim in sort_node.get_live_out_vars():
            definitions[qii__yim.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for jqnua__gpllj in range(len(sort_node.in_vars)):
        if sort_node.in_vars[jqnua__gpllj] is not None:
            sort_node.in_vars[jqnua__gpllj] = visit_vars_inner(sort_node.
                in_vars[jqnua__gpllj], callback, cbdata)
        if sort_node.out_vars[jqnua__gpllj] is not None:
            sort_node.out_vars[jqnua__gpllj] = visit_vars_inner(sort_node.
                out_vars[jqnua__gpllj], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        kosq__quzlm = sort_node.out_vars[0]
        if kosq__quzlm is not None and kosq__quzlm.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            iisdt__kakoy = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & iisdt__kakoy)
            sort_node.dead_var_inds.update(dead_cols - iisdt__kakoy)
            if len(iisdt__kakoy & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for jqnua__gpllj in range(1, len(sort_node.out_vars)):
            iupp__jjt = sort_node.out_vars[jqnua__gpllj]
            if iupp__jjt is not None and iupp__jjt.name not in lives:
                sort_node.out_vars[jqnua__gpllj] = None
                umdeo__zmg = sort_node.num_table_arrays + jqnua__gpllj - 1
                if umdeo__zmg in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(umdeo__zmg)
                else:
                    sort_node.dead_var_inds.add(umdeo__zmg)
                    sort_node.in_vars[jqnua__gpllj] = None
    else:
        for jqnua__gpllj in range(len(sort_node.out_vars)):
            iupp__jjt = sort_node.out_vars[jqnua__gpllj]
            if iupp__jjt is not None and iupp__jjt.name not in lives:
                sort_node.out_vars[jqnua__gpllj] = None
                if jqnua__gpllj in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(jqnua__gpllj)
                else:
                    sort_node.dead_var_inds.add(jqnua__gpllj)
                    sort_node.in_vars[jqnua__gpllj] = None
    if all(iupp__jjt is None for iupp__jjt in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({iupp__jjt.name for iupp__jjt in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({iupp__jjt.name for iupp__jjt in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    owycr__dxn = set()
    if not sort_node.inplace:
        owycr__dxn.update({iupp__jjt.name for iupp__jjt in sort_node.
            get_live_out_vars()})
    return set(), owycr__dxn


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for jqnua__gpllj in range(len(sort_node.in_vars)):
        if sort_node.in_vars[jqnua__gpllj] is not None:
            sort_node.in_vars[jqnua__gpllj] = replace_vars_inner(sort_node.
                in_vars[jqnua__gpllj], var_dict)
        if sort_node.out_vars[jqnua__gpllj] is not None:
            sort_node.out_vars[jqnua__gpllj] = replace_vars_inner(sort_node
                .out_vars[jqnua__gpllj], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for iupp__jjt in (in_vars + out_vars):
            if array_dists[iupp__jjt.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                iupp__jjt.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        sibc__zbw = []
        for iupp__jjt in in_vars:
            miiu__tue = _copy_array_nodes(iupp__jjt, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            sibc__zbw.append(miiu__tue)
        in_vars = sibc__zbw
    out_types = [(typemap[iupp__jjt.name] if iupp__jjt is not None else
        types.none) for iupp__jjt in sort_node.out_vars]
    njrtp__labmg, srex__fmve = get_sort_cpp_section(sort_node, out_types,
        parallel)
    lues__luf = {}
    exec(njrtp__labmg, {}, lues__luf)
    imtw__sbxm = lues__luf['f']
    srex__fmve.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    srex__fmve.update({f'out_type{jqnua__gpllj}': out_types[jqnua__gpllj] for
        jqnua__gpllj in range(len(out_types))})
    gmtf__gnxs = compile_to_numba_ir(imtw__sbxm, srex__fmve, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[iupp__jjt.
        name] for iupp__jjt in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(gmtf__gnxs, in_vars)
    aqb__mfgcw = gmtf__gnxs.body[-2].value.value
    nodes += gmtf__gnxs.body[:-2]
    for jqnua__gpllj, iupp__jjt in enumerate(out_vars):
        gen_getitem(iupp__jjt, aqb__mfgcw, jqnua__gpllj, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    kull__umqrx = lambda arr: arr.copy()
    dfq__qjka = None
    if isinstance(typemap[var.name], TableType):
        leezn__wvhf = len(typemap[var.name].arr_types)
        dfq__qjka = set(range(leezn__wvhf)) - dead_cols
        dfq__qjka = MetaType(tuple(sorted(dfq__qjka)))
        kull__umqrx = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    gmtf__gnxs = compile_to_numba_ir(kull__umqrx, {'bodo': bodo, 'types':
        types, '_used_columns': dfq__qjka}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(gmtf__gnxs, [var])
    nodes += gmtf__gnxs.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    oaxrs__kxz = len(sort_node.key_inds)
    yjrxw__uctyo = len(sort_node.in_vars)
    wllka__ddaik = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + yjrxw__uctyo - 1 if sort_node.
        is_table_format else yjrxw__uctyo)
    hulny__abl, vtw__ythcg, invqw__iikim = _get_cpp_col_ind_mappings(sort_node
        .key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols
        )
    ueekp__umru = []
    if sort_node.is_table_format:
        ueekp__umru.append('arg0')
        for jqnua__gpllj in range(1, yjrxw__uctyo):
            umdeo__zmg = sort_node.num_table_arrays + jqnua__gpllj - 1
            if umdeo__zmg not in sort_node.dead_var_inds:
                ueekp__umru.append(f'arg{umdeo__zmg}')
    else:
        for jqnua__gpllj in range(n_cols):
            if jqnua__gpllj not in sort_node.dead_var_inds:
                ueekp__umru.append(f'arg{jqnua__gpllj}')
    njrtp__labmg = f"def f({', '.join(ueekp__umru)}):\n"
    if sort_node.is_table_format:
        zrbjd__oqa = ',' if yjrxw__uctyo - 1 == 1 else ''
        dqr__pamff = []
        for jqnua__gpllj in range(sort_node.num_table_arrays, n_cols):
            if jqnua__gpllj in sort_node.dead_var_inds:
                dqr__pamff.append('None')
            else:
                dqr__pamff.append(f'arg{jqnua__gpllj}')
        njrtp__labmg += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(dqr__pamff)}{zrbjd__oqa}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        zzol__igw = {nhzk__inn: jqnua__gpllj for jqnua__gpllj, nhzk__inn in
            enumerate(hulny__abl)}
        swdg__cpw = [None] * len(hulny__abl)
        for jqnua__gpllj in range(n_cols):
            fdv__hdsx = zzol__igw.get(jqnua__gpllj, -1)
            if fdv__hdsx != -1:
                swdg__cpw[fdv__hdsx] = f'array_to_info(arg{jqnua__gpllj})'
        njrtp__labmg += '  info_list_total = [{}]\n'.format(','.join(swdg__cpw)
            )
        njrtp__labmg += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    njrtp__labmg += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if rhyow__scvq else '0' for rhyow__scvq in sort_node.
        ascending_list))
    njrtp__labmg += '  na_position = np.array([{}], np.int64)\n'.format(','
        .join('1' if rhyow__scvq else '0' for rhyow__scvq in sort_node.
        na_position_b))
    njrtp__labmg += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if jqnua__gpllj in invqw__iikim else '0' for jqnua__gpllj in
        range(oaxrs__kxz)))
    njrtp__labmg += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    njrtp__labmg += f"""  out_cpp_table = sort_values_table(in_cpp_table, {oaxrs__kxz}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        zrbjd__oqa = ',' if wllka__ddaik == 1 else ''
        glj__ibb = (
            f"({', '.join(f'out_type{jqnua__gpllj}' if not type_has_unknown_cats(out_types[jqnua__gpllj]) else f'arg{jqnua__gpllj}' for jqnua__gpllj in range(wllka__ddaik))}{zrbjd__oqa})"
            )
        njrtp__labmg += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {glj__ibb}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        zzol__igw = {nhzk__inn: jqnua__gpllj for jqnua__gpllj, nhzk__inn in
            enumerate(vtw__ythcg)}
        swdg__cpw = []
        for jqnua__gpllj in range(n_cols):
            fdv__hdsx = zzol__igw.get(jqnua__gpllj, -1)
            if fdv__hdsx != -1:
                xppg__yfgm = (f'out_type{jqnua__gpllj}' if not
                    type_has_unknown_cats(out_types[jqnua__gpllj]) else
                    f'arg{jqnua__gpllj}')
                njrtp__labmg += f"""  out{jqnua__gpllj} = info_to_array(info_from_table(out_cpp_table, {fdv__hdsx}), {xppg__yfgm})
"""
                swdg__cpw.append(f'out{jqnua__gpllj}')
        zrbjd__oqa = ',' if len(swdg__cpw) == 1 else ''
        ulh__xfonj = f"({', '.join(swdg__cpw)}{zrbjd__oqa})"
        njrtp__labmg += f'  out_data = {ulh__xfonj}\n'
    njrtp__labmg += '  delete_table(out_cpp_table)\n'
    njrtp__labmg += '  delete_table(in_cpp_table)\n'
    njrtp__labmg += f'  return out_data\n'
    return njrtp__labmg, {'in_col_inds': MetaType(tuple(hulny__abl)),
        'out_col_inds': MetaType(tuple(vtw__ythcg))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    hulny__abl = []
    vtw__ythcg = []
    invqw__iikim = []
    for nhzk__inn, jqnua__gpllj in enumerate(key_inds):
        hulny__abl.append(jqnua__gpllj)
        if jqnua__gpllj in dead_key_var_inds:
            invqw__iikim.append(nhzk__inn)
        else:
            vtw__ythcg.append(jqnua__gpllj)
    for jqnua__gpllj in range(n_cols):
        if jqnua__gpllj in dead_var_inds or jqnua__gpllj in key_inds:
            continue
        hulny__abl.append(jqnua__gpllj)
        vtw__ythcg.append(jqnua__gpllj)
    return hulny__abl, vtw__ythcg, invqw__iikim


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    vavk__gffd = sort_node.in_vars[0].name
    dkt__gvtw = sort_node.out_vars[0].name
    aci__khz, ajvoe__xhjdq, iba__algi = block_use_map[vavk__gffd]
    if ajvoe__xhjdq or iba__algi:
        return
    jom__zkj, mcuyf__ytjit, qrwqh__ioby = _compute_table_column_uses(dkt__gvtw,
        table_col_use_map, equiv_vars)
    xib__iumnj = set(jqnua__gpllj for jqnua__gpllj in sort_node.key_inds if
        jqnua__gpllj < sort_node.num_table_arrays)
    block_use_map[vavk__gffd
        ] = aci__khz | jom__zkj | xib__iumnj, mcuyf__ytjit or qrwqh__ioby, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    leezn__wvhf = sort_node.num_table_arrays
    dkt__gvtw = sort_node.out_vars[0].name
    dfq__qjka = _find_used_columns(dkt__gvtw, leezn__wvhf, column_live_map,
        equiv_vars)
    if dfq__qjka is None:
        return False
    tkuqz__rryh = set(range(leezn__wvhf)) - dfq__qjka
    xib__iumnj = set(jqnua__gpllj for jqnua__gpllj in sort_node.key_inds if
        jqnua__gpllj < leezn__wvhf)
    jmdpm__jalh = sort_node.dead_key_var_inds | tkuqz__rryh & xib__iumnj
    nkbq__rww = sort_node.dead_var_inds | tkuqz__rryh - xib__iumnj
    txx__qgji = (jmdpm__jalh != sort_node.dead_key_var_inds) | (nkbq__rww !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = jmdpm__jalh
    sort_node.dead_var_inds = nkbq__rww
    return txx__qgji


remove_dead_column_extensions[Sort] = sort_remove_dead_column
