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
            self.na_position_b = tuple([(True if upbb__wlhx == 'last' else 
                False) for upbb__wlhx in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_inds)
        self.ascending_list = ascending_list
        self.loc = loc

    def get_live_in_vars(self):
        return [qjphm__mffe for qjphm__mffe in self.in_vars if qjphm__mffe
             is not None]

    def get_live_out_vars(self):
        return [qjphm__mffe for qjphm__mffe in self.out_vars if qjphm__mffe
             is not None]

    def __repr__(self):
        ltv__xdvtp = ', '.join(qjphm__mffe.name for qjphm__mffe in self.
            get_live_in_vars())
        erzoy__gxi = f'{self.df_in}{{{ltv__xdvtp}}}'
        jjt__ewv = ', '.join(qjphm__mffe.name for qjphm__mffe in self.
            get_live_out_vars())
        bip__uwflx = f'{self.df_out}{{{jjt__ewv}}}'
        return f'Sort (keys: {self.key_inds}): {erzoy__gxi} {bip__uwflx}'


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    jzbfk__mlvct = []
    for stai__jjeb in sort_node.get_live_in_vars():
        rxxnf__gjusr = equiv_set.get_shape(stai__jjeb)
        if rxxnf__gjusr is not None:
            jzbfk__mlvct.append(rxxnf__gjusr[0])
    if len(jzbfk__mlvct) > 1:
        equiv_set.insert_equiv(*jzbfk__mlvct)
    yvlb__uidn = []
    jzbfk__mlvct = []
    for stai__jjeb in sort_node.get_live_out_vars():
        mqfi__piwzs = typemap[stai__jjeb.name]
        heka__qwkhs = array_analysis._gen_shape_call(equiv_set, stai__jjeb,
            mqfi__piwzs.ndim, None, yvlb__uidn)
        equiv_set.insert_equiv(stai__jjeb, heka__qwkhs)
        jzbfk__mlvct.append(heka__qwkhs[0])
        equiv_set.define(stai__jjeb, set())
    if len(jzbfk__mlvct) > 1:
        equiv_set.insert_equiv(*jzbfk__mlvct)
    return [], yvlb__uidn


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    rdhkr__tuqlv = sort_node.get_live_in_vars()
    lujun__jphpy = sort_node.get_live_out_vars()
    bsznc__emni = Distribution.OneD
    for stai__jjeb in rdhkr__tuqlv:
        bsznc__emni = Distribution(min(bsznc__emni.value, array_dists[
            stai__jjeb.name].value))
    zffut__mri = Distribution(min(bsznc__emni.value, Distribution.OneD_Var.
        value))
    for stai__jjeb in lujun__jphpy:
        if stai__jjeb.name in array_dists:
            zffut__mri = Distribution(min(zffut__mri.value, array_dists[
                stai__jjeb.name].value))
    if zffut__mri != Distribution.OneD_Var:
        bsznc__emni = zffut__mri
    for stai__jjeb in rdhkr__tuqlv:
        array_dists[stai__jjeb.name] = bsznc__emni
    for stai__jjeb in lujun__jphpy:
        array_dists[stai__jjeb.name] = zffut__mri


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for rqa__pra, pxnau__swczy in enumerate(sort_node.out_vars):
        ese__pkk = sort_node.in_vars[rqa__pra]
        if ese__pkk is not None and pxnau__swczy is not None:
            typeinferer.constraints.append(typeinfer.Propagate(dst=
                pxnau__swczy.name, src=ese__pkk.name, loc=sort_node.loc))


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for stai__jjeb in sort_node.get_live_out_vars():
            definitions[stai__jjeb.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    for rqa__pra in range(len(sort_node.in_vars)):
        if sort_node.in_vars[rqa__pra] is not None:
            sort_node.in_vars[rqa__pra] = visit_vars_inner(sort_node.
                in_vars[rqa__pra], callback, cbdata)
        if sort_node.out_vars[rqa__pra] is not None:
            sort_node.out_vars[rqa__pra] = visit_vars_inner(sort_node.
                out_vars[rqa__pra], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if sort_node.is_table_format:
        dnsd__flslf = sort_node.out_vars[0]
        if dnsd__flslf is not None and dnsd__flslf.name not in lives:
            sort_node.out_vars[0] = None
            dead_cols = set(range(sort_node.num_table_arrays))
            dbfik__hymb = set(sort_node.key_inds)
            sort_node.dead_key_var_inds.update(dead_cols & dbfik__hymb)
            sort_node.dead_var_inds.update(dead_cols - dbfik__hymb)
            if len(dbfik__hymb & dead_cols) == 0:
                sort_node.in_vars[0] = None
        for rqa__pra in range(1, len(sort_node.out_vars)):
            qjphm__mffe = sort_node.out_vars[rqa__pra]
            if qjphm__mffe is not None and qjphm__mffe.name not in lives:
                sort_node.out_vars[rqa__pra] = None
                metk__quy = sort_node.num_table_arrays + rqa__pra - 1
                if metk__quy in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(metk__quy)
                else:
                    sort_node.dead_var_inds.add(metk__quy)
                    sort_node.in_vars[rqa__pra] = None
    else:
        for rqa__pra in range(len(sort_node.out_vars)):
            qjphm__mffe = sort_node.out_vars[rqa__pra]
            if qjphm__mffe is not None and qjphm__mffe.name not in lives:
                sort_node.out_vars[rqa__pra] = None
                if rqa__pra in sort_node.key_inds:
                    sort_node.dead_key_var_inds.add(rqa__pra)
                else:
                    sort_node.dead_var_inds.add(rqa__pra)
                    sort_node.in_vars[rqa__pra] = None
    if all(qjphm__mffe is None for qjphm__mffe in sort_node.out_vars):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({qjphm__mffe.name for qjphm__mffe in sort_node.
        get_live_in_vars()})
    if not sort_node.inplace:
        def_set.update({qjphm__mffe.name for qjphm__mffe in sort_node.
            get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    koyms__mqqh = set()
    if not sort_node.inplace:
        koyms__mqqh.update({qjphm__mffe.name for qjphm__mffe in sort_node.
            get_live_out_vars()})
    return set(), koyms__mqqh


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for rqa__pra in range(len(sort_node.in_vars)):
        if sort_node.in_vars[rqa__pra] is not None:
            sort_node.in_vars[rqa__pra] = replace_vars_inner(sort_node.
                in_vars[rqa__pra], var_dict)
        if sort_node.out_vars[rqa__pra] is not None:
            sort_node.out_vars[rqa__pra] = replace_vars_inner(sort_node.
                out_vars[rqa__pra], var_dict)


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    in_vars = sort_node.get_live_in_vars()
    out_vars = sort_node.get_live_out_vars()
    if array_dists is not None:
        parallel = True
        for qjphm__mffe in (in_vars + out_vars):
            if array_dists[qjphm__mffe.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                qjphm__mffe.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nodes = []
    if not sort_node.inplace:
        oou__djm = []
        for qjphm__mffe in in_vars:
            pzed__eiqlo = _copy_array_nodes(qjphm__mffe, nodes, typingctx,
                targetctx, typemap, calltypes, sort_node.dead_var_inds)
            oou__djm.append(pzed__eiqlo)
        in_vars = oou__djm
    out_types = [(typemap[qjphm__mffe.name] if qjphm__mffe is not None else
        types.none) for qjphm__mffe in sort_node.out_vars]
    gtc__orjwk, gdu__vjqz = get_sort_cpp_section(sort_node, out_types, parallel
        )
    usrdn__vou = {}
    exec(gtc__orjwk, {}, usrdn__vou)
    anypg__hhfar = usrdn__vou['f']
    gdu__vjqz.update({'bodo': bodo, 'np': np, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'sort_values_table': sort_values_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'array_to_info': array_to_info,
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    gdu__vjqz.update({f'out_type{rqa__pra}': out_types[rqa__pra] for
        rqa__pra in range(len(out_types))})
    hhq__buwnu = compile_to_numba_ir(anypg__hhfar, gdu__vjqz, typingctx=
        typingctx, targetctx=targetctx, arg_typs=tuple(typemap[qjphm__mffe.
        name] for qjphm__mffe in in_vars), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(hhq__buwnu, in_vars)
    yhxjy__sknv = hhq__buwnu.body[-2].value.value
    nodes += hhq__buwnu.body[:-2]
    for rqa__pra, qjphm__mffe in enumerate(out_vars):
        gen_getitem(qjphm__mffe, yhxjy__sknv, rqa__pra, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes,
    dead_cols):
    from bodo.hiframes.table import TableType
    jjzf__gjem = lambda arr: arr.copy()
    nurb__riw = None
    if isinstance(typemap[var.name], TableType):
        sxglx__bqxu = len(typemap[var.name].arr_types)
        nurb__riw = set(range(sxglx__bqxu)) - dead_cols
        nurb__riw = MetaType(tuple(sorted(nurb__riw)))
        jjzf__gjem = (lambda T: bodo.utils.table_utils.
            generate_mappable_table_func(T, 'copy', types.none, True,
            used_cols=_used_columns))
    hhq__buwnu = compile_to_numba_ir(jjzf__gjem, {'bodo': bodo, 'types':
        types, '_used_columns': nurb__riw}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(hhq__buwnu, [var])
    nodes += hhq__buwnu.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(sort_node, out_types, parallel):
    xzga__fblwn = len(sort_node.key_inds)
    orkp__jzkqq = len(sort_node.in_vars)
    shua__kuv = len(sort_node.out_vars)
    n_cols = (sort_node.num_table_arrays + orkp__jzkqq - 1 if sort_node.
        is_table_format else orkp__jzkqq)
    ejtnc__rrjf, zqbc__hit, jewlo__fccji = _get_cpp_col_ind_mappings(sort_node
        .key_inds, sort_node.dead_var_inds, sort_node.dead_key_var_inds, n_cols
        )
    fnun__hkqk = []
    if sort_node.is_table_format:
        fnun__hkqk.append('arg0')
        for rqa__pra in range(1, orkp__jzkqq):
            metk__quy = sort_node.num_table_arrays + rqa__pra - 1
            if metk__quy not in sort_node.dead_var_inds:
                fnun__hkqk.append(f'arg{metk__quy}')
    else:
        for rqa__pra in range(n_cols):
            if rqa__pra not in sort_node.dead_var_inds:
                fnun__hkqk.append(f'arg{rqa__pra}')
    gtc__orjwk = f"def f({', '.join(fnun__hkqk)}):\n"
    if sort_node.is_table_format:
        hnbh__otyb = ',' if orkp__jzkqq - 1 == 1 else ''
        dlocd__bimsz = []
        for rqa__pra in range(sort_node.num_table_arrays, n_cols):
            if rqa__pra in sort_node.dead_var_inds:
                dlocd__bimsz.append('None')
            else:
                dlocd__bimsz.append(f'arg{rqa__pra}')
        gtc__orjwk += f"""  in_cpp_table = py_data_to_cpp_table(arg0, ({', '.join(dlocd__bimsz)}{hnbh__otyb}), in_col_inds, {sort_node.num_table_arrays})
"""
    else:
        jpcz__tpj = {rpov__feff: rqa__pra for rqa__pra, rpov__feff in
            enumerate(ejtnc__rrjf)}
        pfe__wmxo = [None] * len(ejtnc__rrjf)
        for rqa__pra in range(n_cols):
            brwsu__xwe = jpcz__tpj.get(rqa__pra, -1)
            if brwsu__xwe != -1:
                pfe__wmxo[brwsu__xwe] = f'array_to_info(arg{rqa__pra})'
        gtc__orjwk += '  info_list_total = [{}]\n'.format(','.join(pfe__wmxo))
        gtc__orjwk += (
            '  in_cpp_table = arr_info_list_to_table(info_list_total)\n')
    gtc__orjwk += '  vect_ascending = np.array([{}], np.int64)\n'.format(','
        .join('1' if chw__rcylh else '0' for chw__rcylh in sort_node.
        ascending_list))
    gtc__orjwk += '  na_position = np.array([{}], np.int64)\n'.format(','.
        join('1' if chw__rcylh else '0' for chw__rcylh in sort_node.
        na_position_b))
    gtc__orjwk += '  dead_keys = np.array([{}], np.int64)\n'.format(','.
        join('1' if rqa__pra in jewlo__fccji else '0' for rqa__pra in range
        (xzga__fblwn)))
    gtc__orjwk += f'  total_rows_np = np.array([0], dtype=np.int64)\n'
    gtc__orjwk += f"""  out_cpp_table = sort_values_table(in_cpp_table, {xzga__fblwn}, vect_ascending.ctypes, na_position.ctypes, dead_keys.ctypes, total_rows_np.ctypes, {parallel})
"""
    if sort_node.is_table_format:
        hnbh__otyb = ',' if shua__kuv == 1 else ''
        cyt__wqrk = (
            f"({', '.join(f'out_type{rqa__pra}' if not type_has_unknown_cats(out_types[rqa__pra]) else f'arg{rqa__pra}' for rqa__pra in range(shua__kuv))}{hnbh__otyb})"
            )
        gtc__orjwk += f"""  out_data = cpp_table_to_py_data(out_cpp_table, out_col_inds, {cyt__wqrk}, total_rows_np[0], {sort_node.num_table_arrays})
"""
    else:
        jpcz__tpj = {rpov__feff: rqa__pra for rqa__pra, rpov__feff in
            enumerate(zqbc__hit)}
        pfe__wmxo = []
        for rqa__pra in range(n_cols):
            brwsu__xwe = jpcz__tpj.get(rqa__pra, -1)
            if brwsu__xwe != -1:
                gvmyv__lssaf = (f'out_type{rqa__pra}' if not
                    type_has_unknown_cats(out_types[rqa__pra]) else
                    f'arg{rqa__pra}')
                gtc__orjwk += f"""  out{rqa__pra} = info_to_array(info_from_table(out_cpp_table, {brwsu__xwe}), {gvmyv__lssaf})
"""
                pfe__wmxo.append(f'out{rqa__pra}')
        hnbh__otyb = ',' if len(pfe__wmxo) == 1 else ''
        dsw__ink = f"({', '.join(pfe__wmxo)}{hnbh__otyb})"
        gtc__orjwk += f'  out_data = {dsw__ink}\n'
    gtc__orjwk += '  delete_table(out_cpp_table)\n'
    gtc__orjwk += '  delete_table(in_cpp_table)\n'
    gtc__orjwk += f'  return out_data\n'
    return gtc__orjwk, {'in_col_inds': MetaType(tuple(ejtnc__rrjf)),
        'out_col_inds': MetaType(tuple(zqbc__hit))}


def _get_cpp_col_ind_mappings(key_inds, dead_var_inds, dead_key_var_inds,
    n_cols):
    ejtnc__rrjf = []
    zqbc__hit = []
    jewlo__fccji = []
    for rpov__feff, rqa__pra in enumerate(key_inds):
        ejtnc__rrjf.append(rqa__pra)
        if rqa__pra in dead_key_var_inds:
            jewlo__fccji.append(rpov__feff)
        else:
            zqbc__hit.append(rqa__pra)
    for rqa__pra in range(n_cols):
        if rqa__pra in dead_var_inds or rqa__pra in key_inds:
            continue
        ejtnc__rrjf.append(rqa__pra)
        zqbc__hit.append(rqa__pra)
    return ejtnc__rrjf, zqbc__hit, jewlo__fccji


def sort_table_column_use(sort_node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    if not sort_node.is_table_format or sort_node.in_vars[0
        ] is None or sort_node.out_vars[0] is None:
        return
    lou__dbg = sort_node.in_vars[0].name
    mbkd__zuo = sort_node.out_vars[0].name
    honyo__kgtp, mdl__uljps, ibpp__hbnp = block_use_map[lou__dbg]
    if mdl__uljps or ibpp__hbnp:
        return
    eac__nmnwn, wnf__czj, xkj__vzc = _compute_table_column_uses(mbkd__zuo,
        table_col_use_map, equiv_vars)
    ipt__mcv = set(rqa__pra for rqa__pra in sort_node.key_inds if rqa__pra <
        sort_node.num_table_arrays)
    block_use_map[lou__dbg
        ] = honyo__kgtp | eac__nmnwn | ipt__mcv, wnf__czj or xkj__vzc, False


ir_extension_table_column_use[Sort] = sort_table_column_use


def sort_remove_dead_column(sort_node, column_live_map, equiv_vars, typemap):
    if not sort_node.is_table_format or sort_node.out_vars[0] is None:
        return False
    sxglx__bqxu = sort_node.num_table_arrays
    mbkd__zuo = sort_node.out_vars[0].name
    nurb__riw = _find_used_columns(mbkd__zuo, sxglx__bqxu, column_live_map,
        equiv_vars)
    if nurb__riw is None:
        return False
    ydadj__yju = set(range(sxglx__bqxu)) - nurb__riw
    ipt__mcv = set(rqa__pra for rqa__pra in sort_node.key_inds if rqa__pra <
        sxglx__bqxu)
    txvf__zjz = sort_node.dead_key_var_inds | ydadj__yju & ipt__mcv
    xin__bmmhe = sort_node.dead_var_inds | ydadj__yju - ipt__mcv
    fcbyq__noy = (txvf__zjz != sort_node.dead_key_var_inds) | (xin__bmmhe !=
        sort_node.dead_var_inds)
    sort_node.dead_key_var_inds = txvf__zjz
    sort_node.dead_var_inds = xin__bmmhe
    return fcbyq__noy


remove_dead_column_extensions[Sort] = sort_remove_dead_column
