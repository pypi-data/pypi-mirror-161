"""IR node for the join and merge"""
from collections import defaultdict
from typing import Dict, List, Literal, Optional, Set, Tuple, Union
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes, replace_vars_inner, visit_vars_inner
from numba.extending import intrinsic
import bodo
from bodo.hiframes.table import TableType
from bodo.ir.connector import trim_extra_used_columns
from bodo.libs.array import arr_info_list_to_table, array_to_info, cpp_table_to_py_data, delete_table, hash_join_table, py_data_to_cpp_table
from bodo.libs.timsort import getitem_arr_tup, setitem_arr_tup
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import _compute_table_column_uses, get_live_column_nums_block, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import INDEX_SENTINEL, BodoError, MetaType, dtype_to_array_type, find_common_np_dtype, is_dtype_nullable, is_nullable_type, is_str_arr_type, to_nullable_type
from bodo.utils.utils import alloc_arr_tup, is_null_pointer
join_gen_cond_cfunc = {}
join_gen_cond_cfunc_addr = {}


@intrinsic
def add_join_gen_cond_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        omo__kfcjj = func.signature
        fgrot__bih = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        fyf__qtuko = cgutils.get_or_insert_function(builder.module,
            fgrot__bih, sym._literal_value)
        builder.call(fyf__qtuko, [context.get_constant_null(omo__kfcjj.args
            [0]), context.get_constant_null(omo__kfcjj.args[1]), context.
            get_constant_null(omo__kfcjj.args[2]), context.
            get_constant_null(omo__kfcjj.args[3]), context.
            get_constant_null(omo__kfcjj.args[4]), context.
            get_constant_null(omo__kfcjj.args[5]), context.get_constant(
            types.int64, 0), context.get_constant(types.int64, 0)])
        context.add_linking_libs([join_gen_cond_cfunc[sym._literal_value].
            _library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_join_cond_addr(name):
    with numba.objmode(addr='int64'):
        addr = join_gen_cond_cfunc_addr[name]
    return addr


HOW_OPTIONS = Literal['inner', 'left', 'right', 'outer', 'asof']


class Join(ir.Stmt):

    def __init__(self, left_keys: Union[List[str], str], right_keys: Union[
        List[str], str], out_data_vars: List[ir.Var], out_df_type: bodo.
        DataFrameType, left_vars: List[ir.Var], left_df_type: bodo.
        DataFrameType, right_vars: List[ir.Var], right_df_type: bodo.
        DataFrameType, how: HOW_OPTIONS, suffix_left: str, suffix_right:
        str, loc: ir.Loc, is_left: bool, is_right: bool, is_join: bool,
        left_index: bool, right_index: bool, indicator_col_num: int,
        is_na_equal: bool, gen_cond_expr: str):
        self.left_keys = left_keys
        self.right_keys = right_keys
        self.out_data_vars = out_data_vars
        self.out_col_names = out_df_type.columns
        self.left_vars = left_vars
        self.right_vars = right_vars
        self.how = how
        self.loc = loc
        self.is_left = is_left
        self.is_right = is_right
        self.is_join = is_join
        self.left_index = left_index
        self.right_index = right_index
        self.indicator_col_num = indicator_col_num
        self.is_na_equal = is_na_equal
        self.gen_cond_expr = gen_cond_expr
        self.n_out_table_cols = len(self.out_col_names)
        self.out_used_cols = set(range(self.n_out_table_cols))
        if self.out_data_vars[1] is not None:
            self.out_used_cols.add(self.n_out_table_cols)
        qbmiz__wgzuq = left_df_type.columns
        wyz__olszp = right_df_type.columns
        self.left_col_names = qbmiz__wgzuq
        self.right_col_names = wyz__olszp
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(qbmiz__wgzuq) if self.is_left_table else 0
        self.n_right_table_cols = len(wyz__olszp) if self.is_right_table else 0
        llju__tummg = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        gzaxf__jmxin = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(llju__tummg)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(gzaxf__jmxin)
        self.left_var_map = {nizgk__glvji: zur__ohwr for zur__ohwr,
            nizgk__glvji in enumerate(qbmiz__wgzuq)}
        self.right_var_map = {nizgk__glvji: zur__ohwr for zur__ohwr,
            nizgk__glvji in enumerate(wyz__olszp)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = llju__tummg
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = gzaxf__jmxin
        self.left_key_set = set(self.left_var_map[nizgk__glvji] for
            nizgk__glvji in left_keys)
        self.right_key_set = set(self.right_var_map[nizgk__glvji] for
            nizgk__glvji in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[nizgk__glvji] for
                nizgk__glvji in qbmiz__wgzuq if f'(left.{nizgk__glvji})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[nizgk__glvji] for
                nizgk__glvji in wyz__olszp if f'(right.{nizgk__glvji})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        cfoi__avvw: int = -1
        egqt__brb = set(left_keys) & set(right_keys)
        isq__pupqt = set(qbmiz__wgzuq) & set(wyz__olszp)
        qjk__qunz = isq__pupqt - egqt__brb
        zpybe__xib: Dict[int, (Literal['left', 'right'], int)] = {}
        zzju__vixvh: Dict[int, int] = {}
        ecj__nef: Dict[int, int] = {}
        for zur__ohwr, nizgk__glvji in enumerate(qbmiz__wgzuq):
            if nizgk__glvji in qjk__qunz:
                kuik__eyxqh = str(nizgk__glvji) + suffix_left
                zhqz__sgzzi = out_df_type.column_index[kuik__eyxqh]
                if (right_index and not left_index and zur__ohwr in self.
                    left_key_set):
                    cfoi__avvw = out_df_type.column_index[nizgk__glvji]
                    zpybe__xib[cfoi__avvw] = 'left', zur__ohwr
            else:
                zhqz__sgzzi = out_df_type.column_index[nizgk__glvji]
            zpybe__xib[zhqz__sgzzi] = 'left', zur__ohwr
            zzju__vixvh[zur__ohwr] = zhqz__sgzzi
        for zur__ohwr, nizgk__glvji in enumerate(wyz__olszp):
            if nizgk__glvji not in egqt__brb:
                if nizgk__glvji in qjk__qunz:
                    mvx__oxqy = str(nizgk__glvji) + suffix_right
                    zhqz__sgzzi = out_df_type.column_index[mvx__oxqy]
                    if (left_index and not right_index and zur__ohwr in
                        self.right_key_set):
                        cfoi__avvw = out_df_type.column_index[nizgk__glvji]
                        zpybe__xib[cfoi__avvw] = 'right', zur__ohwr
                else:
                    zhqz__sgzzi = out_df_type.column_index[nizgk__glvji]
                zpybe__xib[zhqz__sgzzi] = 'right', zur__ohwr
                ecj__nef[zur__ohwr] = zhqz__sgzzi
        if self.left_vars[-1] is not None:
            zzju__vixvh[llju__tummg] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            ecj__nef[gzaxf__jmxin] = self.n_out_table_cols
        self.out_to_input_col_map = zpybe__xib
        self.left_to_output_map = zzju__vixvh
        self.right_to_output_map = ecj__nef
        self.extra_data_col_num = cfoi__avvw
        if len(out_data_vars) > 1:
            thac__nlrs = 'left' if right_index else 'right'
            if thac__nlrs == 'left':
                vaml__tbo = llju__tummg
            elif thac__nlrs == 'right':
                vaml__tbo = gzaxf__jmxin
        else:
            thac__nlrs = None
            vaml__tbo = -1
        self.index_source = thac__nlrs
        self.index_col_num = vaml__tbo
        imjx__rzvhg = []
        qnaz__nafew = len(left_keys)
        for hob__agb in range(qnaz__nafew):
            dzwh__myjos = left_keys[hob__agb]
            oeil__exv = right_keys[hob__agb]
            imjx__rzvhg.append(dzwh__myjos == oeil__exv)
        self.vect_same_key = imjx__rzvhg

    @property
    def has_live_left_table_var(self):
        return self.is_left_table and self.left_vars[0] is not None

    @property
    def has_live_right_table_var(self):
        return self.is_right_table and self.right_vars[0] is not None

    @property
    def has_live_out_table_var(self):
        return self.out_data_vars[0] is not None

    @property
    def has_live_out_index_var(self):
        return self.out_data_vars[1] is not None

    def get_out_table_var(self):
        return self.out_data_vars[0]

    def get_out_index_var(self):
        return self.out_data_vars[1]

    def get_live_left_vars(self):
        vars = []
        for sao__jzp in self.left_vars:
            if sao__jzp is not None:
                vars.append(sao__jzp)
        return vars

    def get_live_right_vars(self):
        vars = []
        for sao__jzp in self.right_vars:
            if sao__jzp is not None:
                vars.append(sao__jzp)
        return vars

    def get_live_out_vars(self):
        vars = []
        for sao__jzp in self.out_data_vars:
            if sao__jzp is not None:
                vars.append(sao__jzp)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        lwevd__dmtk = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[lwevd__dmtk])
                lwevd__dmtk += 1
            else:
                left_vars.append(None)
            start = 1
        vwy__uznxa = max(self.n_left_table_cols - 1, 0)
        for zur__ohwr in range(start, len(self.left_vars)):
            if zur__ohwr + vwy__uznxa in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[lwevd__dmtk])
                lwevd__dmtk += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        lwevd__dmtk = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[lwevd__dmtk])
                lwevd__dmtk += 1
            else:
                right_vars.append(None)
            start = 1
        vwy__uznxa = max(self.n_right_table_cols - 1, 0)
        for zur__ohwr in range(start, len(self.right_vars)):
            if zur__ohwr + vwy__uznxa in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[lwevd__dmtk])
                lwevd__dmtk += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        pno__jmexo = [self.has_live_out_table_var, self.has_live_out_index_var]
        lwevd__dmtk = 0
        for zur__ohwr in range(len(self.out_data_vars)):
            if not pno__jmexo[zur__ohwr]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[lwevd__dmtk])
                lwevd__dmtk += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {zur__ohwr for zur__ohwr in self.out_used_cols if zur__ohwr <
            self.n_out_table_cols}

    def __repr__(self):
        mjjmg__ccyze = ', '.join([f'{nizgk__glvji}' for nizgk__glvji in
            self.left_col_names])
        ztz__cqiqf = f'left={{{mjjmg__ccyze}}}'
        mjjmg__ccyze = ', '.join([f'{nizgk__glvji}' for nizgk__glvji in
            self.right_col_names])
        rwe__zwtw = f'right={{{mjjmg__ccyze}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, ztz__cqiqf, rwe__zwtw)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    sng__tqlx = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    ojl__owwl = []
    auug__bkur = join_node.get_live_left_vars()
    for djvk__afnt in auug__bkur:
        vku__gch = typemap[djvk__afnt.name]
        okxky__ibtbe = equiv_set.get_shape(djvk__afnt)
        if okxky__ibtbe:
            ojl__owwl.append(okxky__ibtbe[0])
    if len(ojl__owwl) > 1:
        equiv_set.insert_equiv(*ojl__owwl)
    ojl__owwl = []
    auug__bkur = list(join_node.get_live_right_vars())
    for djvk__afnt in auug__bkur:
        vku__gch = typemap[djvk__afnt.name]
        okxky__ibtbe = equiv_set.get_shape(djvk__afnt)
        if okxky__ibtbe:
            ojl__owwl.append(okxky__ibtbe[0])
    if len(ojl__owwl) > 1:
        equiv_set.insert_equiv(*ojl__owwl)
    ojl__owwl = []
    for mnfzg__reha in join_node.get_live_out_vars():
        vku__gch = typemap[mnfzg__reha.name]
        onr__mhni = array_analysis._gen_shape_call(equiv_set, mnfzg__reha,
            vku__gch.ndim, None, sng__tqlx)
        equiv_set.insert_equiv(mnfzg__reha, onr__mhni)
        ojl__owwl.append(onr__mhni[0])
        equiv_set.define(mnfzg__reha, set())
    if len(ojl__owwl) > 1:
        equiv_set.insert_equiv(*ojl__owwl)
    return [], sng__tqlx


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    yvtm__xpac = Distribution.OneD
    fcxrk__ovlzp = Distribution.OneD
    for djvk__afnt in join_node.get_live_left_vars():
        yvtm__xpac = Distribution(min(yvtm__xpac.value, array_dists[
            djvk__afnt.name].value))
    for djvk__afnt in join_node.get_live_right_vars():
        fcxrk__ovlzp = Distribution(min(fcxrk__ovlzp.value, array_dists[
            djvk__afnt.name].value))
    gbdmq__dgp = Distribution.OneD_Var
    for mnfzg__reha in join_node.get_live_out_vars():
        if mnfzg__reha.name in array_dists:
            gbdmq__dgp = Distribution(min(gbdmq__dgp.value, array_dists[
                mnfzg__reha.name].value))
    zdya__rjlms = Distribution(min(gbdmq__dgp.value, yvtm__xpac.value))
    ksfmx__erqi = Distribution(min(gbdmq__dgp.value, fcxrk__ovlzp.value))
    gbdmq__dgp = Distribution(max(zdya__rjlms.value, ksfmx__erqi.value))
    for mnfzg__reha in join_node.get_live_out_vars():
        array_dists[mnfzg__reha.name] = gbdmq__dgp
    if gbdmq__dgp != Distribution.OneD_Var:
        yvtm__xpac = gbdmq__dgp
        fcxrk__ovlzp = gbdmq__dgp
    for djvk__afnt in join_node.get_live_left_vars():
        array_dists[djvk__afnt.name] = yvtm__xpac
    for djvk__afnt in join_node.get_live_right_vars():
        array_dists[djvk__afnt.name] = fcxrk__ovlzp
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(sao__jzp, callback,
        cbdata) for sao__jzp in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(sao__jzp, callback,
        cbdata) for sao__jzp in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(sao__jzp, callback,
        cbdata) for sao__jzp in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        pkei__pmrp = []
        jnun__wgft = join_node.get_out_table_var()
        if jnun__wgft.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for sbhf__bri in join_node.out_to_input_col_map.keys():
            if sbhf__bri in join_node.out_used_cols:
                continue
            pkei__pmrp.append(sbhf__bri)
            if join_node.indicator_col_num == sbhf__bri:
                join_node.indicator_col_num = -1
                continue
            if sbhf__bri == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            rbox__xgfl, sbhf__bri = join_node.out_to_input_col_map[sbhf__bri]
            if rbox__xgfl == 'left':
                if (sbhf__bri not in join_node.left_key_set and sbhf__bri
                     not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(sbhf__bri)
                    if not join_node.is_left_table:
                        join_node.left_vars[sbhf__bri] = None
            elif rbox__xgfl == 'right':
                if (sbhf__bri not in join_node.right_key_set and sbhf__bri
                     not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(sbhf__bri)
                    if not join_node.is_right_table:
                        join_node.right_vars[sbhf__bri] = None
        for zur__ohwr in pkei__pmrp:
            del join_node.out_to_input_col_map[zur__ohwr]
        if join_node.is_left_table:
            kfun__curzf = set(range(join_node.n_left_table_cols))
            kpq__edf = not bool(kfun__curzf - join_node.left_dead_var_inds)
            if kpq__edf:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            kfun__curzf = set(range(join_node.n_right_table_cols))
            kpq__edf = not bool(kfun__curzf - join_node.right_dead_var_inds)
            if kpq__edf:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        pbxtq__krwdp = join_node.get_out_index_var()
        if pbxtq__krwdp.name not in lives:
            join_node.out_data_vars[1] = None
            join_node.out_used_cols.remove(join_node.n_out_table_cols)
            if join_node.index_source == 'left':
                if (join_node.index_col_num not in join_node.left_key_set and
                    join_node.index_col_num not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(join_node.index_col_num)
                    join_node.left_vars[-1] = None
            elif join_node.index_col_num not in join_node.right_key_set and join_node.index_col_num not in join_node.right_cond_cols:
                join_node.right_dead_var_inds.add(join_node.index_col_num)
                join_node.right_vars[-1] = None
    if not (join_node.has_live_out_table_var or join_node.
        has_live_out_index_var):
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_remove_dead_column(join_node, column_live_map, equiv_vars, typemap):
    dgf__mqur = False
    if join_node.has_live_out_table_var:
        mps__ibcrt = join_node.get_out_table_var().name
        iae__bjent, dwh__jcrwz, bkpev__vhawu = get_live_column_nums_block(
            column_live_map, equiv_vars, mps__ibcrt)
        if not (dwh__jcrwz or bkpev__vhawu):
            iae__bjent = trim_extra_used_columns(iae__bjent, join_node.
                n_out_table_cols)
            wvpnt__rhhcy = join_node.get_out_table_used_cols()
            if len(iae__bjent) != len(wvpnt__rhhcy):
                dgf__mqur = not (join_node.is_left_table and join_node.
                    is_right_table)
                lxcec__iabd = wvpnt__rhhcy - iae__bjent
                join_node.out_used_cols = join_node.out_used_cols - lxcec__iabd
    return dgf__mqur


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        urjm__miojb = join_node.get_out_table_var()
        grl__idc, dwh__jcrwz, bkpev__vhawu = _compute_table_column_uses(
            urjm__miojb.name, table_col_use_map, equiv_vars)
    else:
        grl__idc, dwh__jcrwz, bkpev__vhawu = set(), False, False
    if join_node.has_live_left_table_var:
        kez__ioxmr = join_node.left_vars[0].name
        qzcb__vgcat, xtl__zljwx, ajw__caeu = block_use_map[kez__ioxmr]
        if not (xtl__zljwx or ajw__caeu):
            qdecj__quobg = set([join_node.out_to_input_col_map[zur__ohwr][1
                ] for zur__ohwr in grl__idc if join_node.
                out_to_input_col_map[zur__ohwr][0] == 'left'])
            uxqm__brv = set(zur__ohwr for zur__ohwr in join_node.
                left_key_set | join_node.left_cond_cols if zur__ohwr <
                join_node.n_left_table_cols)
            if not (dwh__jcrwz or bkpev__vhawu):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (qdecj__quobg | uxqm__brv)
            block_use_map[kez__ioxmr] = (qzcb__vgcat | qdecj__quobg |
                uxqm__brv, dwh__jcrwz or bkpev__vhawu, False)
    if join_node.has_live_right_table_var:
        raz__ohek = join_node.right_vars[0].name
        qzcb__vgcat, xtl__zljwx, ajw__caeu = block_use_map[raz__ohek]
        if not (xtl__zljwx or ajw__caeu):
            dnfx__ckdog = set([join_node.out_to_input_col_map[zur__ohwr][1] for
                zur__ohwr in grl__idc if join_node.out_to_input_col_map[
                zur__ohwr][0] == 'right'])
            ygyi__rlf = set(zur__ohwr for zur__ohwr in join_node.
                right_key_set | join_node.right_cond_cols if zur__ohwr <
                join_node.n_right_table_cols)
            if not (dwh__jcrwz or bkpev__vhawu):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (dnfx__ckdog | ygyi__rlf)
            block_use_map[raz__ohek] = (qzcb__vgcat | dnfx__ckdog |
                ygyi__rlf, dwh__jcrwz or bkpev__vhawu, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({omlx__hdzi.name for omlx__hdzi in join_node.
        get_live_left_vars()})
    use_set.update({omlx__hdzi.name for omlx__hdzi in join_node.
        get_live_right_vars()})
    def_set.update({omlx__hdzi.name for omlx__hdzi in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    fyibh__zqa = set(omlx__hdzi.name for omlx__hdzi in join_node.
        get_live_out_vars())
    return set(), fyibh__zqa


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(sao__jzp, var_dict) for
        sao__jzp in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(sao__jzp, var_dict) for
        sao__jzp in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(sao__jzp, var_dict
        ) for sao__jzp in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for djvk__afnt in join_node.get_live_out_vars():
        definitions[djvk__afnt.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        vcjd__jpj = join_node.loc.strformat()
        bra__wmur = [join_node.left_col_names[zur__ohwr] for zur__ohwr in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        vdr__pzi = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', vdr__pzi, vcjd__jpj,
            bra__wmur)
        wryqk__ruzgx = [join_node.right_col_names[zur__ohwr] for zur__ohwr in
            sorted(set(range(len(join_node.right_col_names))) - join_node.
            right_dead_var_inds)]
        vdr__pzi = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', vdr__pzi, vcjd__jpj,
            wryqk__ruzgx)
        tgex__djcl = [join_node.out_col_names[zur__ohwr] for zur__ohwr in
            sorted(join_node.get_out_table_used_cols())]
        vdr__pzi = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', vdr__pzi, vcjd__jpj,
            tgex__djcl)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    qnaz__nafew = len(join_node.left_keys)
    out_physical_to_logical_list = []
    if join_node.has_live_out_table_var:
        out_table_type = typemap[join_node.get_out_table_var().name]
    else:
        out_table_type = types.none
    if join_node.has_live_out_index_var:
        index_col_type = typemap[join_node.get_out_index_var().name]
    else:
        index_col_type = types.none
    if join_node.extra_data_col_num != -1:
        out_physical_to_logical_list.append(join_node.extra_data_col_num)
    left_key_in_output = []
    right_key_in_output = []
    left_used_key_nums = set()
    right_used_key_nums = set()
    left_logical_physical_map = {}
    right_logical_physical_map = {}
    left_physical_to_logical_list = []
    right_physical_to_logical_list = []
    vul__yvzvk = 0
    kcx__ebcdr = 0
    foc__rysim = []
    for nizgk__glvji in join_node.left_keys:
        fuhfw__fvfr = join_node.left_var_map[nizgk__glvji]
        if not join_node.is_left_table:
            foc__rysim.append(join_node.left_vars[fuhfw__fvfr])
        pno__jmexo = 1
        zhqz__sgzzi = join_node.left_to_output_map[fuhfw__fvfr]
        if nizgk__glvji == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == fuhfw__fvfr):
                out_physical_to_logical_list.append(zhqz__sgzzi)
                left_used_key_nums.add(fuhfw__fvfr)
            else:
                pno__jmexo = 0
        elif zhqz__sgzzi not in join_node.out_used_cols:
            pno__jmexo = 0
        elif fuhfw__fvfr in left_used_key_nums:
            pno__jmexo = 0
        else:
            left_used_key_nums.add(fuhfw__fvfr)
            out_physical_to_logical_list.append(zhqz__sgzzi)
        left_physical_to_logical_list.append(fuhfw__fvfr)
        left_logical_physical_map[fuhfw__fvfr] = vul__yvzvk
        vul__yvzvk += 1
        left_key_in_output.append(pno__jmexo)
    foc__rysim = tuple(foc__rysim)
    sjlr__krbsv = []
    for zur__ohwr in range(len(join_node.left_col_names)):
        if (zur__ohwr not in join_node.left_dead_var_inds and zur__ohwr not in
            join_node.left_key_set):
            if not join_node.is_left_table:
                omlx__hdzi = join_node.left_vars[zur__ohwr]
                sjlr__krbsv.append(omlx__hdzi)
            mzr__eeww = 1
            ikt__vtyeh = 1
            zhqz__sgzzi = join_node.left_to_output_map[zur__ohwr]
            if zur__ohwr in join_node.left_cond_cols:
                if zhqz__sgzzi not in join_node.out_used_cols:
                    mzr__eeww = 0
                left_key_in_output.append(mzr__eeww)
            elif zur__ohwr in join_node.left_dead_var_inds:
                mzr__eeww = 0
                ikt__vtyeh = 0
            if mzr__eeww:
                out_physical_to_logical_list.append(zhqz__sgzzi)
            if ikt__vtyeh:
                left_physical_to_logical_list.append(zur__ohwr)
                left_logical_physical_map[zur__ohwr] = vul__yvzvk
                vul__yvzvk += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            sjlr__krbsv.append(join_node.left_vars[join_node.index_col_num])
        zhqz__sgzzi = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(zhqz__sgzzi)
        left_physical_to_logical_list.append(join_node.index_col_num)
    sjlr__krbsv = tuple(sjlr__krbsv)
    if join_node.is_left_table:
        sjlr__krbsv = tuple(join_node.get_live_left_vars())
    ubw__ghjiz = []
    for zur__ohwr, nizgk__glvji in enumerate(join_node.right_keys):
        fuhfw__fvfr = join_node.right_var_map[nizgk__glvji]
        if not join_node.is_right_table:
            ubw__ghjiz.append(join_node.right_vars[fuhfw__fvfr])
        if not join_node.vect_same_key[zur__ohwr] and not join_node.is_join:
            pno__jmexo = 1
            if fuhfw__fvfr not in join_node.right_to_output_map:
                pno__jmexo = 0
            else:
                zhqz__sgzzi = join_node.right_to_output_map[fuhfw__fvfr]
                if nizgk__glvji == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        fuhfw__fvfr):
                        out_physical_to_logical_list.append(zhqz__sgzzi)
                        right_used_key_nums.add(fuhfw__fvfr)
                    else:
                        pno__jmexo = 0
                elif zhqz__sgzzi not in join_node.out_used_cols:
                    pno__jmexo = 0
                elif fuhfw__fvfr in right_used_key_nums:
                    pno__jmexo = 0
                else:
                    right_used_key_nums.add(fuhfw__fvfr)
                    out_physical_to_logical_list.append(zhqz__sgzzi)
            right_key_in_output.append(pno__jmexo)
        right_physical_to_logical_list.append(fuhfw__fvfr)
        right_logical_physical_map[fuhfw__fvfr] = kcx__ebcdr
        kcx__ebcdr += 1
    ubw__ghjiz = tuple(ubw__ghjiz)
    hbep__bwf = []
    for zur__ohwr in range(len(join_node.right_col_names)):
        if (zur__ohwr not in join_node.right_dead_var_inds and zur__ohwr not in
            join_node.right_key_set):
            if not join_node.is_right_table:
                hbep__bwf.append(join_node.right_vars[zur__ohwr])
            mzr__eeww = 1
            ikt__vtyeh = 1
            zhqz__sgzzi = join_node.right_to_output_map[zur__ohwr]
            if zur__ohwr in join_node.right_cond_cols:
                if zhqz__sgzzi not in join_node.out_used_cols:
                    mzr__eeww = 0
                right_key_in_output.append(mzr__eeww)
            elif zur__ohwr in join_node.right_dead_var_inds:
                mzr__eeww = 0
                ikt__vtyeh = 0
            if mzr__eeww:
                out_physical_to_logical_list.append(zhqz__sgzzi)
            if ikt__vtyeh:
                right_physical_to_logical_list.append(zur__ohwr)
                right_logical_physical_map[zur__ohwr] = kcx__ebcdr
                kcx__ebcdr += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            hbep__bwf.append(join_node.right_vars[join_node.index_col_num])
        zhqz__sgzzi = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(zhqz__sgzzi)
        right_physical_to_logical_list.append(join_node.index_col_num)
    hbep__bwf = tuple(hbep__bwf)
    if join_node.is_right_table:
        hbep__bwf = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    nxxp__ybdt = foc__rysim + ubw__ghjiz + sjlr__krbsv + hbep__bwf
    iikmo__jwjw = tuple(typemap[omlx__hdzi.name] for omlx__hdzi in nxxp__ybdt)
    left_other_names = tuple('t1_c' + str(zur__ohwr) for zur__ohwr in range
        (len(sjlr__krbsv)))
    right_other_names = tuple('t2_c' + str(zur__ohwr) for zur__ohwr in
        range(len(hbep__bwf)))
    if join_node.is_left_table:
        anldb__nvg = ()
    else:
        anldb__nvg = tuple('t1_key' + str(zur__ohwr) for zur__ohwr in range
            (qnaz__nafew))
    if join_node.is_right_table:
        deaj__pzu = ()
    else:
        deaj__pzu = tuple('t2_key' + str(zur__ohwr) for zur__ohwr in range(
            qnaz__nafew))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(anldb__nvg + deaj__pzu +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            qfwt__dxvz = typemap[join_node.left_vars[0].name]
        else:
            qfwt__dxvz = types.none
        for ylx__ezy in left_physical_to_logical_list:
            if ylx__ezy < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                vku__gch = qfwt__dxvz.arr_types[ylx__ezy]
            else:
                vku__gch = typemap[join_node.left_vars[-1].name]
            if ylx__ezy in join_node.left_key_set:
                left_key_types.append(vku__gch)
            else:
                left_other_types.append(vku__gch)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[omlx__hdzi.name] for omlx__hdzi in
            foc__rysim)
        left_other_types = tuple([typemap[nizgk__glvji.name] for
            nizgk__glvji in sjlr__krbsv])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            qfwt__dxvz = typemap[join_node.right_vars[0].name]
        else:
            qfwt__dxvz = types.none
        for ylx__ezy in right_physical_to_logical_list:
            if ylx__ezy < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                vku__gch = qfwt__dxvz.arr_types[ylx__ezy]
            else:
                vku__gch = typemap[join_node.right_vars[-1].name]
            if ylx__ezy in join_node.right_key_set:
                right_key_types.append(vku__gch)
            else:
                right_other_types.append(vku__gch)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[omlx__hdzi.name] for omlx__hdzi in
            ubw__ghjiz)
        right_other_types = tuple([typemap[nizgk__glvji.name] for
            nizgk__glvji in hbep__bwf])
    matched_key_types = []
    for zur__ohwr in range(qnaz__nafew):
        jynp__tjrf = _match_join_key_types(left_key_types[zur__ohwr],
            right_key_types[zur__ohwr], loc)
        glbs[f'key_type_{zur__ohwr}'] = jynp__tjrf
        matched_key_types.append(jynp__tjrf)
    if join_node.is_left_table:
        akn__aax = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if akn__aax:
            txlxj__fipa = False
            ecxmu__iew = False
            nlc__ovrsn = None
            if join_node.has_live_left_table_var:
                rspd__lnin = list(typemap[join_node.left_vars[0].name].
                    arr_types)
            else:
                rspd__lnin = None
            for sbhf__bri, vku__gch in akn__aax.items():
                if sbhf__bri < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    rspd__lnin[sbhf__bri] = vku__gch
                    txlxj__fipa = True
                else:
                    nlc__ovrsn = vku__gch
                    ecxmu__iew = True
            if txlxj__fipa:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(rspd__lnin))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if ecxmu__iew:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = nlc__ovrsn
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({anldb__nvg[zur__ohwr]}, key_type_{zur__ohwr})'
             if left_key_types[zur__ohwr] != matched_key_types[zur__ohwr] else
            f'{anldb__nvg[zur__ohwr]}' for zur__ohwr in range(qnaz__nafew)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        akn__aax = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if akn__aax:
            txlxj__fipa = False
            ecxmu__iew = False
            nlc__ovrsn = None
            if join_node.has_live_right_table_var:
                rspd__lnin = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                rspd__lnin = None
            for sbhf__bri, vku__gch in akn__aax.items():
                if sbhf__bri < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    rspd__lnin[sbhf__bri] = vku__gch
                    txlxj__fipa = True
                else:
                    nlc__ovrsn = vku__gch
                    ecxmu__iew = True
            if txlxj__fipa:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(rspd__lnin))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if ecxmu__iew:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = nlc__ovrsn
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({deaj__pzu[zur__ohwr]}, key_type_{zur__ohwr})'
             if right_key_types[zur__ohwr] != matched_key_types[zur__ohwr] else
            f'{deaj__pzu[zur__ohwr]}' for zur__ohwr in range(qnaz__nafew)))
        func_text += '    data_right = ({}{})\n'.format(','.join(
            right_other_names), ',' if len(right_other_names) != 0 else '')
    general_cond_cfunc, left_col_nums, right_col_nums = (
        _gen_general_cond_cfunc(join_node, typemap,
        left_logical_physical_map, right_logical_physical_map))
    if join_node.how == 'asof':
        if left_parallel or right_parallel:
            assert left_parallel and right_parallel, 'pd.merge_asof requires both left and right to be replicated or distributed'
            func_text += """    t2_keys, data_right = parallel_asof_comm(t1_keys, t2_keys, data_right)
"""
        func_text += """    out_t1_keys, out_t2_keys, out_data_left, out_data_right = bodo.ir.join.local_merge_asof(t1_keys, t2_keys, data_left, data_right)
"""
    else:
        func_text += _gen_local_hash_join(join_node, left_key_types,
            right_key_types, matched_key_types, left_other_names,
            right_other_names, left_other_types, right_other_types,
            left_key_in_output, right_key_in_output, left_parallel,
            right_parallel, glbs, out_physical_to_logical_list,
            out_table_type, index_col_type, join_node.
            get_out_table_used_cols(), left_used_key_nums,
            right_used_key_nums, general_cond_cfunc, left_col_nums,
            right_col_nums, left_physical_to_logical_list,
            right_physical_to_logical_list)
    if join_node.how == 'asof':
        for zur__ohwr in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(zur__ohwr,
                zur__ohwr)
        for zur__ohwr in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(zur__ohwr
                , zur__ohwr)
        for zur__ohwr in range(qnaz__nafew):
            func_text += (
                f'    t1_keys_{zur__ohwr} = out_t1_keys[{zur__ohwr}]\n')
        for zur__ohwr in range(qnaz__nafew):
            func_text += (
                f'    t2_keys_{zur__ohwr} = out_t2_keys[{zur__ohwr}]\n')
    vcgh__cvmk = {}
    exec(func_text, {}, vcgh__cvmk)
    uswv__rwx = vcgh__cvmk['f']
    glbs.update({'bodo': bodo, 'np': np, 'pd': pd, 'parallel_asof_comm':
        parallel_asof_comm, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'hash_join_table':
        hash_join_table, 'delete_table': delete_table,
        'add_join_gen_cond_cfunc_sym': add_join_gen_cond_cfunc_sym,
        'get_join_cond_addr': get_join_cond_addr, 'key_in_output': np.array
        (left_key_in_output + right_key_in_output, dtype=np.bool_),
        'py_data_to_cpp_table': py_data_to_cpp_table,
        'cpp_table_to_py_data': cpp_table_to_py_data})
    if general_cond_cfunc:
        glbs.update({'general_cond_cfunc': general_cond_cfunc})
    rka__lrl = compile_to_numba_ir(uswv__rwx, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=iikmo__jwjw, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(rka__lrl, nxxp__ybdt)
    oktfv__rclsu = rka__lrl.body[:-3]
    if join_node.has_live_out_index_var:
        oktfv__rclsu[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        oktfv__rclsu[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        oktfv__rclsu.pop(-1)
    elif not join_node.has_live_out_table_var:
        oktfv__rclsu.pop(-2)
    return oktfv__rclsu


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    zra__matax = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{zra__matax}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        left_logical_physical_map, join_node.left_var_map, typemap,
        join_node.left_vars, table_getitem_funcs, func_text, 'left',
        join_node.left_key_set, na_check_name, join_node.is_left_table)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        right_logical_physical_map, join_node.right_var_map, typemap,
        join_node.right_vars, table_getitem_funcs, func_text, 'right',
        join_node.right_key_set, na_check_name, join_node.is_right_table)
    func_text += f'  return {expr}'
    vcgh__cvmk = {}
    exec(func_text, table_getitem_funcs, vcgh__cvmk)
    bec__qmtk = vcgh__cvmk[f'bodo_join_gen_cond{zra__matax}']
    ejk__xojma = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    fpleg__spfz = numba.cfunc(ejk__xojma, nopython=True)(bec__qmtk)
    join_gen_cond_cfunc[fpleg__spfz.native_name] = fpleg__spfz
    join_gen_cond_cfunc_addr[fpleg__spfz.native_name] = fpleg__spfz.address
    return fpleg__spfz, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    fslsg__eqyla = []
    for nizgk__glvji, qkp__fjd in name_to_var_map.items():
        qec__tou = f'({table_name}.{nizgk__glvji})'
        if qec__tou not in expr:
            continue
        rlmva__ike = f'getitem_{table_name}_val_{qkp__fjd}'
        zxkku__zrz = f'_bodo_{table_name}_val_{qkp__fjd}'
        if is_table_var:
            ctfyy__vwbe = typemap[col_vars[0].name].arr_types[qkp__fjd]
        else:
            ctfyy__vwbe = typemap[col_vars[qkp__fjd].name]
        if is_str_arr_type(ctfyy__vwbe
            ) or ctfyy__vwbe == bodo.binary_array_type:
            func_text += f"""  {zxkku__zrz}, {zxkku__zrz}_size = {rlmva__ike}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {zxkku__zrz} = bodo.libs.str_arr_ext.decode_utf8({zxkku__zrz}, {zxkku__zrz}_size)
"""
        else:
            func_text += (
                f'  {zxkku__zrz} = {rlmva__ike}({table_name}_data1, {table_name}_ind)\n'
                )
        izb__nlhpl = logical_to_physical_ind[qkp__fjd]
        table_getitem_funcs[rlmva__ike
            ] = bodo.libs.array._gen_row_access_intrinsic(ctfyy__vwbe,
            izb__nlhpl)
        expr = expr.replace(qec__tou, zxkku__zrz)
        vvm__cts = f'({na_check_name}.{table_name}.{nizgk__glvji})'
        if vvm__cts in expr:
            oxvba__erudz = f'nacheck_{table_name}_val_{qkp__fjd}'
            efoc__vpv = f'_bodo_isna_{table_name}_val_{qkp__fjd}'
            if isinstance(ctfyy__vwbe, bodo.libs.int_arr_ext.IntegerArrayType
                ) or ctfyy__vwbe in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(ctfyy__vwbe):
                func_text += f"""  {efoc__vpv} = {oxvba__erudz}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += f"""  {efoc__vpv} = {oxvba__erudz}({table_name}_data1, {table_name}_ind)
"""
            table_getitem_funcs[oxvba__erudz
                ] = bodo.libs.array._gen_row_na_check_intrinsic(ctfyy__vwbe,
                izb__nlhpl)
            expr = expr.replace(vvm__cts, efoc__vpv)
        if qkp__fjd not in key_set:
            fslsg__eqyla.append(izb__nlhpl)
    return expr, func_text, fslsg__eqyla


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as bzma__ote:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    ffr__fnzr = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[omlx__hdzi.name] in ffr__fnzr for
        omlx__hdzi in join_node.get_live_left_vars())
    right_parallel = all(array_dists[omlx__hdzi.name] in ffr__fnzr for
        omlx__hdzi in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[omlx__hdzi.name] in ffr__fnzr for
            omlx__hdzi in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[omlx__hdzi.name] in ffr__fnzr for
            omlx__hdzi in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[omlx__hdzi.name] in ffr__fnzr for omlx__hdzi in
            join_node.get_live_out_vars())
    return left_parallel, right_parallel


def _gen_local_hash_join(join_node, left_key_types, right_key_types,
    matched_key_types, left_other_names, right_other_names,
    left_other_types, right_other_types, left_key_in_output,
    right_key_in_output, left_parallel, right_parallel, glbs,
    out_physical_to_logical_list, out_table_type, index_col_type,
    out_table_used_cols, left_used_key_nums, right_used_key_nums,
    general_cond_cfunc, left_col_nums, right_col_nums,
    left_physical_to_logical_list, right_physical_to_logical_list):

    def needs_typechange(in_type, need_nullable, is_same_key):
        return isinstance(in_type, types.Array) and not is_dtype_nullable(
            in_type.dtype) and need_nullable and not is_same_key
    mzzd__idnys = set(left_col_nums)
    bhhs__awfn = set(right_col_nums)
    imjx__rzvhg = join_node.vect_same_key
    kxv__oigjp = []
    for zur__ohwr in range(len(left_key_types)):
        if left_key_in_output[zur__ohwr]:
            kxv__oigjp.append(needs_typechange(matched_key_types[zur__ohwr],
                join_node.is_right, imjx__rzvhg[zur__ohwr]))
    dmwy__vwwyg = len(left_key_types)
    ukkkz__lagvb = 0
    ynvxo__zzky = left_physical_to_logical_list[len(left_key_types):]
    for zur__ohwr, ylx__ezy in enumerate(ynvxo__zzky):
        bun__tzvfh = True
        if ylx__ezy in mzzd__idnys:
            bun__tzvfh = left_key_in_output[dmwy__vwwyg]
            dmwy__vwwyg += 1
        if bun__tzvfh:
            kxv__oigjp.append(needs_typechange(left_other_types[zur__ohwr],
                join_node.is_right, False))
    for zur__ohwr in range(len(right_key_types)):
        if not imjx__rzvhg[zur__ohwr] and not join_node.is_join:
            if right_key_in_output[ukkkz__lagvb]:
                kxv__oigjp.append(needs_typechange(matched_key_types[
                    zur__ohwr], join_node.is_left, False))
            ukkkz__lagvb += 1
    gfyu__vvpbu = right_physical_to_logical_list[len(right_key_types):]
    for zur__ohwr, ylx__ezy in enumerate(gfyu__vvpbu):
        bun__tzvfh = True
        if ylx__ezy in bhhs__awfn:
            bun__tzvfh = right_key_in_output[ukkkz__lagvb]
            ukkkz__lagvb += 1
        if bun__tzvfh:
            kxv__oigjp.append(needs_typechange(right_other_types[zur__ohwr],
                join_node.is_left, False))
    qnaz__nafew = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            lwayf__stbcc = left_other_names[1:]
            jnun__wgft = left_other_names[0]
        else:
            lwayf__stbcc = left_other_names
            jnun__wgft = None
        zve__jav = '()' if len(lwayf__stbcc) == 0 else f'({lwayf__stbcc[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({jnun__wgft}, {zve__jav}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        qkozs__jery = []
        for zur__ohwr in range(qnaz__nafew):
            qkozs__jery.append('t1_keys[{}]'.format(zur__ohwr))
        for zur__ohwr in range(len(left_other_names)):
            qkozs__jery.append('data_left[{}]'.format(zur__ohwr))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(ydb__hieal) for ydb__hieal in
            qkozs__jery))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            zxju__aqci = right_other_names[1:]
            jnun__wgft = right_other_names[0]
        else:
            zxju__aqci = right_other_names
            jnun__wgft = None
        zve__jav = '()' if len(zxju__aqci) == 0 else f'({zxju__aqci[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({jnun__wgft}, {zve__jav}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        jgeh__hdtd = []
        for zur__ohwr in range(qnaz__nafew):
            jgeh__hdtd.append('t2_keys[{}]'.format(zur__ohwr))
        for zur__ohwr in range(len(right_other_names)):
            jgeh__hdtd.append('data_right[{}]'.format(zur__ohwr))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(ydb__hieal) for ydb__hieal in
            jgeh__hdtd))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(imjx__rzvhg, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(kxv__oigjp, dtype=np.int64)
    glbs['left_table_cond_columns'] = np.array(left_col_nums if len(
        left_col_nums) > 0 else [-1], dtype=np.int64)
    glbs['right_table_cond_columns'] = np.array(right_col_nums if len(
        right_col_nums) > 0 else [-1], dtype=np.int64)
    if general_cond_cfunc:
        func_text += f"""    cfunc_cond = add_join_gen_cond_cfunc_sym(general_cond_cfunc, '{general_cond_cfunc.native_name}')
"""
        func_text += (
            f"    cfunc_cond = get_join_cond_addr('{general_cond_cfunc.native_name}')\n"
            )
    else:
        func_text += '    cfunc_cond = 0\n'
    func_text += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    func_text += (
        """    out_table = hash_join_table(table_left, table_right, {}, {}, {}, {}, {}, vect_same_key.ctypes, key_in_output.ctypes, vect_need_typechange.ctypes, {}, {}, {}, {}, {}, {}, cfunc_cond, left_table_cond_columns.ctypes, {}, right_table_cond_columns.ctypes, {}, total_rows_np.ctypes)
"""
        .format(left_parallel, right_parallel, qnaz__nafew, len(ynvxo__zzky
        ), len(gfyu__vvpbu), join_node.is_left, join_node.is_right,
        join_node.is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    schg__lflna = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {schg__lflna}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        lwevd__dmtk = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{lwevd__dmtk}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        akn__aax = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        akn__aax.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        txlxj__fipa = False
        ecxmu__iew = False
        if join_node.has_live_out_table_var:
            rspd__lnin = list(out_table_type.arr_types)
        else:
            rspd__lnin = None
        for sbhf__bri, vku__gch in akn__aax.items():
            if sbhf__bri < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                rspd__lnin[sbhf__bri] = vku__gch
                txlxj__fipa = True
            else:
                nlc__ovrsn = vku__gch
                ecxmu__iew = True
        if txlxj__fipa:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            ftwda__zyn = bodo.TableType(tuple(rspd__lnin))
            glbs['py_table_type'] = ftwda__zyn
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if ecxmu__iew:
            glbs['index_col_type'] = nlc__ovrsn
            glbs['index_cast_type'] = index_col_type
            func_text += (
                f'    index_var = bodo.utils.utils.astype(index_var, index_cast_type)\n'
                )
    func_text += f'    out_table = T\n'
    func_text += f'    out_index = index_var\n'
    return func_text


def determine_table_cast_map(matched_key_types: List[types.Type], key_types:
    List[types.Type], used_key_nums: Optional[Set[int]], output_map:
    Optional[Dict[int, int]], convert_dict_col: bool, loc: ir.Loc):
    akn__aax: Dict[int, types.Type] = {}
    qnaz__nafew = len(matched_key_types)
    for zur__ohwr in range(qnaz__nafew):
        if used_key_nums is None or zur__ohwr in used_key_nums:
            if matched_key_types[zur__ohwr] != key_types[zur__ohwr] and (
                convert_dict_col or key_types[zur__ohwr] != bodo.
                dict_str_arr_type):
                if output_map:
                    lwevd__dmtk = output_map[zur__ohwr]
                else:
                    lwevd__dmtk = zur__ohwr
                akn__aax[lwevd__dmtk] = matched_key_types[zur__ohwr]
    return akn__aax


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    iwnp__jkh = bodo.libs.distributed_api.get_size()
    gvo__ttube = np.empty(iwnp__jkh, left_key_arrs[0].dtype)
    pzs__xzgzz = np.empty(iwnp__jkh, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(gvo__ttube, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(pzs__xzgzz, left_key_arrs[0][-1])
    yiao__yyj = np.zeros(iwnp__jkh, np.int32)
    gryr__whvl = np.zeros(iwnp__jkh, np.int32)
    ssib__zhy = np.zeros(iwnp__jkh, np.int32)
    siux__bkr = right_key_arrs[0][0]
    hjr__nmnc = right_key_arrs[0][-1]
    vwy__uznxa = -1
    zur__ohwr = 0
    while zur__ohwr < iwnp__jkh - 1 and pzs__xzgzz[zur__ohwr] < siux__bkr:
        zur__ohwr += 1
    while zur__ohwr < iwnp__jkh and gvo__ttube[zur__ohwr] <= hjr__nmnc:
        vwy__uznxa, odxtz__dbh = _count_overlap(right_key_arrs[0],
            gvo__ttube[zur__ohwr], pzs__xzgzz[zur__ohwr])
        if vwy__uznxa != 0:
            vwy__uznxa -= 1
            odxtz__dbh += 1
        yiao__yyj[zur__ohwr] = odxtz__dbh
        gryr__whvl[zur__ohwr] = vwy__uznxa
        zur__ohwr += 1
    while zur__ohwr < iwnp__jkh:
        yiao__yyj[zur__ohwr] = 1
        gryr__whvl[zur__ohwr] = len(right_key_arrs[0]) - 1
        zur__ohwr += 1
    bodo.libs.distributed_api.alltoall(yiao__yyj, ssib__zhy, 1)
    aprr__jtmg = ssib__zhy.sum()
    erd__oaz = np.empty(aprr__jtmg, right_key_arrs[0].dtype)
    qvyhw__qeczg = alloc_arr_tup(aprr__jtmg, right_data)
    ytn__rkvr = bodo.ir.join.calc_disp(ssib__zhy)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], erd__oaz,
        yiao__yyj, ssib__zhy, gryr__whvl, ytn__rkvr)
    bodo.libs.distributed_api.alltoallv_tup(right_data, qvyhw__qeczg,
        yiao__yyj, ssib__zhy, gryr__whvl, ytn__rkvr)
    return (erd__oaz,), qvyhw__qeczg


@numba.njit
def _count_overlap(r_key_arr, start, end):
    odxtz__dbh = 0
    vwy__uznxa = 0
    wgqq__ybu = 0
    while wgqq__ybu < len(r_key_arr) and r_key_arr[wgqq__ybu] < start:
        vwy__uznxa += 1
        wgqq__ybu += 1
    while wgqq__ybu < len(r_key_arr) and start <= r_key_arr[wgqq__ybu] <= end:
        wgqq__ybu += 1
        odxtz__dbh += 1
    return vwy__uznxa, odxtz__dbh


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    yloxf__zza = np.empty_like(arr)
    yloxf__zza[0] = 0
    for zur__ohwr in range(1, len(arr)):
        yloxf__zza[zur__ohwr] = yloxf__zza[zur__ohwr - 1] + arr[zur__ohwr - 1]
    return yloxf__zza


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    xac__pqs = len(left_keys[0])
    drsac__wsles = len(right_keys[0])
    zwhby__gew = alloc_arr_tup(xac__pqs, left_keys)
    guft__ccqr = alloc_arr_tup(xac__pqs, right_keys)
    gkmjh__avo = alloc_arr_tup(xac__pqs, data_left)
    vzhs__izaj = alloc_arr_tup(xac__pqs, data_right)
    wxl__vbig = 0
    ghf__zvck = 0
    for wxl__vbig in range(xac__pqs):
        if ghf__zvck < 0:
            ghf__zvck = 0
        while ghf__zvck < drsac__wsles and getitem_arr_tup(right_keys,
            ghf__zvck) <= getitem_arr_tup(left_keys, wxl__vbig):
            ghf__zvck += 1
        ghf__zvck -= 1
        setitem_arr_tup(zwhby__gew, wxl__vbig, getitem_arr_tup(left_keys,
            wxl__vbig))
        setitem_arr_tup(gkmjh__avo, wxl__vbig, getitem_arr_tup(data_left,
            wxl__vbig))
        if ghf__zvck >= 0:
            setitem_arr_tup(guft__ccqr, wxl__vbig, getitem_arr_tup(
                right_keys, ghf__zvck))
            setitem_arr_tup(vzhs__izaj, wxl__vbig, getitem_arr_tup(
                data_right, ghf__zvck))
        else:
            bodo.libs.array_kernels.setna_tup(guft__ccqr, wxl__vbig)
            bodo.libs.array_kernels.setna_tup(vzhs__izaj, wxl__vbig)
    return zwhby__gew, guft__ccqr, gkmjh__avo, vzhs__izaj
