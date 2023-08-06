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
            self.na_position_b = tuple([(True if bzyg__jgeta == 'last' else
                False) for bzyg__jgeta in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [rdyr__tzzph for rdyr__tzzph in self.in_vars if rdyr__tzzph
             is not None]

    def get_live_out_vars(self):
        return [rdyr__tzzph for rdyr__tzzph in self.out_vars if rdyr__tzzph
             is not None]

    def __repr__(self):
        yapnc__sib = ', '.join(rdyr__tzzph.name for rdyr__tzzph in self.
            get_live_in_vars())
        cqzs__lqqg = f'{self.df_in}{{{yapnc__sib}}}'
        zrx__zeqls = ', '.join(rdyr__tzzph.name for rdyr__tzzph in self.
            get_live_out_vars())
        deyg__kbxf = f'{self.df_out}{{{zrx__zeqls}}}'
        return f'Sort (keys: {self.key_inds}): {cqzs__lqqg} {deyg__kbxf}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    laqqj__gbtj = []
    for khz__arfoi in sort_node.get_live_in_vars():
        snx__dit = equiv_set.get_shape(khz__arfoi)
        if snx__dit is not None:
            laqqj__gbtj.append(snx__dit[0])
    if len(laqqj__gbtj) > 1:
        equiv_set.insert_equiv(*laqqj__gbtj)
    awk__xpqe = []
    laqqj__gbtj = []
    for khz__arfoi in sort_node.get_live_out_vars():
        gglf__ybyys = typemap[khz__arfoi.name]
        pgam__niu = array_analysis._gen_shape_call(equiv_set, khz__arfoi,
            gglf__ybyys.ndim, None, awk__xpqe)
        equiv_set.insert_equiv(khz__arfoi, pgam__niu)
        laqqj__gbtj.append(pgam__niu[0])
        equiv_set.define(khz__arfoi, set())
    if len(laqqj__gbtj) > 1:
        equiv_set.insert_equiv(*laqqj__gbtj)
    return [], awk__xpqe


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    zsnnb__mqm = sort_node.get_live_in_vars()
    anja__bwgls = sort_node.get_live_out_vars()
    enh__xehw = Distribution.OneD
    for khz__arfoi in zsnnb__mqm:
        enh__xehw = Distribution(min(enh__xehw.value, array_dists[
            khz__arfoi.name].value))
    hdl__ezyq = Distribution(min(enh__xehw.value, Distribution.OneD_Var.value))
    for khz__arfoi in anja__bwgls:
        if khz__arfoi.name in array_dists:
            hdl__ezyq = Distribution(min(hdl__ezyq.value, array_dists[
                khz__arfoi.name].value))
    if hdl__ezyq != Distribution.OneD_Var:
        enh__xehw = hdl__ezyq
    for khz__arfoi in zsnnb__mqm:
        array_dists[khz__arfoi.name] = enh__xehw
    for khz__arfoi in anja__bwgls:
        array_dists[khz__arfoi.name] = hdl__ezyq


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for gkqxu__ngvgp, slz__lqwz in enumerate(sort_node.out_vars):
        qya__baec = sort_node.in_vars[gkqxu__ngvgp]
        if qya__baec is not None and slz__lqwz is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                slz__lqwz.name, src=qya__baec.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for khz__arfoi in sort_node.get_live_out_vars():
            definitions[khz__arfoi.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for gkqxu__ngvgp in range(len(sort_node.in_vars)):
        if sort_node.in_vars[gkqxu__ngvgp] is not None:
            sort_node.in_vars[gkqxu__ngvgp] = visit_vars_inner(sort_node.
                in_vars[gkqxu__ngvgp], callback, cbdata)
        if sort_node.out_vars[gkqxu__ngvgp] is not None:
            sort_node.out_vars[gkqxu__ngvgp] = visit_vars_inner(sort_node.
                out_vars[gkqxu__ngvgp], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        dgymw__ikkdd = sort_node.out_vars[0]
        if dgymw__ikkdd is not None and dgymw__ikkdd.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            yoa__ylv = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & yoa__ylv)
            sort_node.dead_var_inds.update(dead_cols - yoa__ylv)
            if len(yoa__ylv & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for gkqxu__ngvgp in range(1, len(sort_node.out_vars)):
            rdyr__tzzph = sort_node.out_vars[gkqxu__ngvgp]
            if rdyr__tzzph is not None and rdyr__tzzph.name not in lives:
                sort_node.out_vars[gkqxu__ngvgp] = None
                uui__gjotf = sort_node.num_table_arrays + gkqxu__ngvgp - 1
                if uui__gjotf in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(uui__gjotf)
                else:
                    sort_node.dead_var_inds.add(uui__gjotf)
                    sort_node.in_vars[gkqxu__ngvgp] = None
    else:
        for gkqxu__ngvgp in range(len(sort_node.out_vars)):
            rdyr__tzzph = sort_node.out_vars[gkqxu__ngvgp]
            if rdyr__tzzph is not None and rdyr__tzzph.name not in lives:
                sort_node.out_vars[gkqxu__ngvgp] = None
                if gkqxu__ngvgp in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(gkqxu__ngvgp)
                else:
                    sort_node.dead_var_inds.add(gkqxu__ngvgp)
                    sort_node.in_vars[gkqxu__ngvgp] = None
    if all(rdyr__tzzph is None for rdyr__tzzph in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({rdyr__tzzph.name for rdyr__tzzph in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({rdyr__tzzph.name for rdyr__tzzph in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    pryl__ssral = set()
    if not sort_node.inplace:
        pryl__ssral.update({rdyr__tzzph.name for rdyr__tzzph in sort_node.
            get_live_out_vars()})
    return set(), pryl__ssral


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for gkqxu__ngvgp in range(len(sort_node.in_vars)):
        if sort_node.in_vars[gkqxu__ngvgp] is not None:
            sort_node.in_vars[gkqxu__ngvgp] = replace_vars_inner(sort_node.
                in_vars[gkqxu__ngvgp], var_dict)
        if sort_node.out_vars[gkqxu__ngvgp] is not None:
            sort_node.out_vars[gkqxu__ngvgp] = replace_vars_inner(sort_node
                .out_vars[gkqxu__ngvgp], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for rdyr__tzzph in (in_vars + out_vars):
            if array_dists[rdyr__tzzph.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                rdyr__tzzph.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        qiycj__pysjg = []
        for rdyr__tzzph in in_vars:
            fgikh__der = _copy_array_nodes(rdyr__tzzph, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            qiycj__pysjg.append(fgikh__der)
        in_vars = qiycj__pysjg
    out_types = [(typemap[rdyr__tzzph.name] if rdyr__tzzph is not None else
        types.none) for rdyr__tzzph in sort_node.out_vars]
    mkrcz__fzs, rkarq__irt = get_sort_cpp_section(sort_node, out_types,
        parallel)
    onep__anrwj = {}
    exec(mkrcz__fzs, {}, onep__anrwj)
    vna__vlzj = onep__anrwj['f']
    rkarq__irt.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    rkarq__irt.update({f'out_type{gkqxu__ngvgp}': out_types[gkqxu__ngvgp] for
        gkqxu__ngvgp in range(len(out_types))})
    pna__vjbo = compile_to_numba_ir(vna__vlzj, rkarq__irt, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[rdyr__tzzph.
        name] for rdyr__tzzph in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(pna__vjbo, in_vars)
    csaf__gpi = pna__vjbo.body[-2].value.value
    nodes += pna__vjbo.body[:-2]
    for gkqxu__ngvgp, rdyr__tzzph in enumerate(out_vars):
        gen_getitem(rdyr__tzzph, csaf__gpi, gkqxu__ngvgp, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    rdhb__fuk = lambda arr: arr.copy()
    towan__cpybl = None
    if isinstance(typemap[var.name], TableType):
        spsi__okiz = len(typemap[var.name].arr_types)
        towan__cpybl = set(range(spsi__okiz)) - dead_cols
        towan__cpybl = MetaType(tuple(sorted(towan__cpybl)))
        rdhb__fuk = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    pna__vjbo = compile_to_numba_ir(rdhb__fuk, {'bodo': bodo, 'types':
        types, '_used_columns': towan__cpybl}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(pna__vjbo, [var])
    nodes += pna__vjbo.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    duneq__lnej = len(sort_node.key_inds)
    yye__ize = len(sort_node.in_vars)
    vudb__aob = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + yye__ize - 1 if sort_node.
        is_table_format else yye__ize)
    fcqun__uepx, sbg__veox, ikkv__aia = _get_cpp_col_ind_mappings(sort_node
        .key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols
        )
    wxic__tfh = []
    if sort_node.is_table_format:
        wxic__tfh.append('arg0')
        for gkqxu__ngvgp in range(1, yye__ize):
            uui__gjotf = sort_node.num_table_arrays + gkqxu__ngvgp - 1
            if uui__gjotf not in sort_node.dead_var_inds:
                wxic__tfh.append(f'arg{uui__gjotf}')
    else:
        for gkqxu__ngvgp in range(n_cols):
            if gkqxu__ngvgp not in sort_node.dead_var_inds:
                wxic__tfh.append(f'arg{gkqxu__ngvgp}')
    mkrcz__fzs = f"def f({', '.join(wxic__tfh)}):\n"
    if sort_node.is_table_format:
        prtq__nsqnh = ',' if yye__ize - 1 == 1 else ''
        pxb__zjd = []
        for gkqxu__ngvgp in range(sort_node.num_table_arrays, n_cols):
            if gkqxu__ngvgp in sort_node.dead_var_inds:
                pxb__zjd.append('None')
            else:
                pxb__zjd.append(f'arg{gkqxu__ngvgp}')
        mkrcz__fzs += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(pxb__zjd)}{prtq__nsqnh}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        niqvs__qcvah = {qjf__dej: gkqxu__ngvgp for gkqxu__ngvgp, qjf__dej in
            enumerate(fcqun__uepx)}
        hcy__cdm = [None] * len(fcqun__uepx)
        for gkqxu__ngvgp in range(n_cols):
            tbc__llmx = niqvs__qcvah.get(gkqxu__ngvgp, -1)
            if tbc__llmx != -1:
                hcy__cdm[tbc__llmx] = f'array_to_info(arg{gkqxu__ngvgp})'
        mkrcz__fzs += '  info_list_total = [{}]\n'.format(','.join(hcy__cdm))
        mkrcz__fzs += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    mkrcz__fzs += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if amwqo__jwmmr else '0' for amwqo__jwmmr in sort_node.
        ascending_list))
    mkrcz__fzs += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if amwqo__jwmmr else '0' for amwqo__jwmmr in sort_node.
        na_position_b))
    mkrcz__fzs += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if gkqxu__ngvgp in ikkv__aia else '0' for gkqxu__ngvgp in
        range(duneq__lnej)))
    mkrcz__fzs += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    mkrcz__fzs += f"""  out_cpp_table = sort_values_table(in_cpp_table, {duneq__lnej}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        prtq__nsqnh = ',' if vudb__aob == 1 else ''
        ziwq__imsud = (
            f"({', '.join(f'out_type{gkqxu__ngvgp}' if not type_has_unknown_cats(out_types[gkqxu__ngvgp]) else f'arg{gkqxu__ngvgp}' for gkqxu__ngvgp in range(vudb__aob))}{prtq__nsqnh})"
            )
        mkrcz__fzs += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {ziwq__imsud}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        niqvs__qcvah = {qjf__dej: gkqxu__ngvgp for gkqxu__ngvgp, qjf__dej in
            enumerate(sbg__veox)}
        hcy__cdm = []
        for gkqxu__ngvgp in range(n_cols):
            tbc__llmx = niqvs__qcvah.get(gkqxu__ngvgp, -1)
            if tbc__llmx != -1:
                zps__uop = (f'out_type{gkqxu__ngvgp}' if not
                    type_has_unknown_cats(out_types[gkqxu__ngvgp]) else
                    f'arg{gkqxu__ngvgp}')
                mkrcz__fzs += f"""  out{gkqxu__ngvgp} = info_to_array(info_from_table(out_cpp_table, {tbc__llmx}), {zps__uop})
"""
                hcy__cdm.append(f'out{gkqxu__ngvgp}')
        prtq__nsqnh = ',' if len(hcy__cdm) == 1 else ''
        lpjls__qfts = f"({', '.join(hcy__cdm)}{prtq__nsqnh})"
        mkrcz__fzs += f'  out_data = {lpjls__qfts}\n'
    mkrcz__fzs += '  delete_table(out_cpp_table)\n'
    mkrcz__fzs += '  delete_table(in_cpp_table)\n'
    mkrcz__fzs += f'  return out_data\n'
    return mkrcz__fzs, {'in_col_inds': MetaType(tuple(fcqun__uepx)),
        'out_col_inds': MetaType(tuple(sbg__veox))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    fcqun__uepx = []
    sbg__veox = []
    ikkv__aia = []
    for qjf__dej, gkqxu__ngvgp in enumerate(key_inds):
        fcqun__uepx.append(gkqxu__ngvgp)
        if gkqxu__ngvgp in dead_key_var_inds:
            ikkv__aia.append(qjf__dej)
        else:
            sbg__veox.append(gkqxu__ngvgp)
    for gkqxu__ngvgp in range(n_cols):
        if gkqxu__ngvgp in dead_var_inds or gkqxu__ngvgp in key_inds:
            continue
        fcqun__uepx.append(gkqxu__ngvgp)
        sbg__veox.append(gkqxu__ngvgp)
    return fcqun__uepx, sbg__veox, ikkv__aia


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    qhz__kmyho = sort_node.in_vars[0].name
    nljv__vnhvz = sort_node.out_vars[0].name
    hrq__rbt, xdg__bmf, xuf__iif = block_use_map[qhz__kmyho]
    if xdg__bmf or xuf__iif:
        return
    aliel__ywsr, awvgy__tbwjf, rhax__fyr = _compute_table_column_uses(
        nljv__vnhvz, table_col_use_map, equiv_vars)
    oun__zovt = set(gkqxu__ngvgp for gkqxu__ngvgp in sort_node.key_inds if 
        gkqxu__ngvgp < sort_node.num_table_arrays)
    block_use_map[qhz__kmyho
        ] = hrq__rbt | aliel__ywsr | oun__zovt, awvgy__tbwjf or rhax__fyr, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    spsi__okiz = sort_node.num_table_arrays
    nljv__vnhvz = sort_node.out_vars[0].name
    towan__cpybl = _find_used_columns(nljv__vnhvz, spsi__okiz,
        column_live_map, equiv_vars)
    if towan__cpybl is None:
        return False
    fadj__ifd = set(range(spsi__okiz)) - towan__cpybl
    oun__zovt = set(gkqxu__ngvgp for gkqxu__ngvgp in sort_node.key_inds if 
        gkqxu__ngvgp < spsi__okiz)
    qdmhs__qtsg = sort_node.dead_key_var_inds | fadj__ifd & oun__zovt
    zgamb__yomsy = sort_node.dead_var_inds | fadj__ifd - oun__zovt
    bxowg__lntk = (qdmhs__qtsg != sort_node.dead_key_var_inds) | (zgamb__yomsy
         != sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = qdmhs__qtsg
    sort_node.dead_var_inds = zgamb__yomsy
    return bxowg__lntk


remove_dead_column_extensions[Sort] = sort_remove_dead_column
