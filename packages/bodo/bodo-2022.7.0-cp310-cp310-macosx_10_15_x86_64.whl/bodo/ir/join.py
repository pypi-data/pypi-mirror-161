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
        mre__rsj = func.signature
        gdu__gvm = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        vnndt__swl = cgutils.get_or_insert_function(builder.module,
            gdu__gvm, sym._literal_value)
        builder.call(vnndt__swl, [context.get_constant_null(mre__rsj.args[0
            ]), context.get_constant_null(mre__rsj.args[1]), context.
            get_constant_null(mre__rsj.args[2]), context.get_constant_null(
            mre__rsj.args[3]), context.get_constant_null(mre__rsj.args[4]),
            context.get_constant_null(mre__rsj.args[5]), context.
            get_constant(types.int64, 0), context.get_constant(types.int64, 0)]
            )
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
        dlrdh__eah = left_df_type.columns
        mpyhz__iqy = right_df_type.columns
        self.left_col_names = dlrdh__eah
        self.right_col_names = mpyhz__iqy
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(dlrdh__eah) if self.is_left_table else 0
        self.n_right_table_cols = len(mpyhz__iqy) if self.is_right_table else 0
        tcl__joy = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        vkzn__wzcs = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(tcl__joy)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(vkzn__wzcs)
        self.left_var_map = {tmug__vaho: qeozq__zaw for qeozq__zaw,
            tmug__vaho in enumerate(dlrdh__eah)}
        self.right_var_map = {tmug__vaho: qeozq__zaw for qeozq__zaw,
            tmug__vaho in enumerate(mpyhz__iqy)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = tcl__joy
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = vkzn__wzcs
        self.left_key_set = set(self.left_var_map[tmug__vaho] for
            tmug__vaho in left_keys)
        self.right_key_set = set(self.right_var_map[tmug__vaho] for
            tmug__vaho in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[tmug__vaho] for
                tmug__vaho in dlrdh__eah if f'(left.{tmug__vaho})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[tmug__vaho] for
                tmug__vaho in mpyhz__iqy if f'(right.{tmug__vaho})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        iywc__hcuxg: int = -1
        xiyto__ntxiz = set(left_keys) & set(right_keys)
        tvjfr__qqvsi = set(dlrdh__eah) & set(mpyhz__iqy)
        fgj__dpwdf = tvjfr__qqvsi - xiyto__ntxiz
        bshas__dkf: Dict[int, (Literal['left', 'right'], int)] = {}
        qghu__plteu: Dict[int, int] = {}
        rnq__vuaue: Dict[int, int] = {}
        for qeozq__zaw, tmug__vaho in enumerate(dlrdh__eah):
            if tmug__vaho in fgj__dpwdf:
                nbphv__tbr = str(tmug__vaho) + suffix_left
                wfp__xrbn = out_df_type.column_index[nbphv__tbr]
                if (right_index and not left_index and qeozq__zaw in self.
                    left_key_set):
                    iywc__hcuxg = out_df_type.column_index[tmug__vaho]
                    bshas__dkf[iywc__hcuxg] = 'left', qeozq__zaw
            else:
                wfp__xrbn = out_df_type.column_index[tmug__vaho]
            bshas__dkf[wfp__xrbn] = 'left', qeozq__zaw
            qghu__plteu[qeozq__zaw] = wfp__xrbn
        for qeozq__zaw, tmug__vaho in enumerate(mpyhz__iqy):
            if tmug__vaho not in xiyto__ntxiz:
                if tmug__vaho in fgj__dpwdf:
                    iqrrh__xxn = str(tmug__vaho) + suffix_right
                    wfp__xrbn = out_df_type.column_index[iqrrh__xxn]
                    if (left_index and not right_index and qeozq__zaw in
                        self.right_key_set):
                        iywc__hcuxg = out_df_type.column_index[tmug__vaho]
                        bshas__dkf[iywc__hcuxg] = 'right', qeozq__zaw
                else:
                    wfp__xrbn = out_df_type.column_index[tmug__vaho]
                bshas__dkf[wfp__xrbn] = 'right', qeozq__zaw
                rnq__vuaue[qeozq__zaw] = wfp__xrbn
        if self.left_vars[-1] is not None:
            qghu__plteu[tcl__joy] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            rnq__vuaue[vkzn__wzcs] = self.n_out_table_cols
        self.out_to_input_col_map = bshas__dkf
        self.left_to_output_map = qghu__plteu
        self.right_to_output_map = rnq__vuaue
        self.extra_data_col_num = iywc__hcuxg
        if len(out_data_vars) > 1:
            mgj__wkg = 'left' if right_index else 'right'
            if mgj__wkg == 'left':
                bfwc__tlxt = tcl__joy
            elif mgj__wkg == 'right':
                bfwc__tlxt = vkzn__wzcs
        else:
            mgj__wkg = None
            bfwc__tlxt = -1
        self.index_source = mgj__wkg
        self.index_col_num = bfwc__tlxt
        pkese__jzy = []
        zcgd__hsz = len(left_keys)
        for zhb__ivfi in range(zcgd__hsz):
            vgxg__xekxw = left_keys[zhb__ivfi]
            mqxm__ipgm = right_keys[zhb__ivfi]
            pkese__jzy.append(vgxg__xekxw == mqxm__ipgm)
        self.vect_same_key = pkese__jzy

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
        for fjw__xzguw in self.left_vars:
            if fjw__xzguw is not None:
                vars.append(fjw__xzguw)
        return vars

    def get_live_right_vars(self):
        vars = []
        for fjw__xzguw in self.right_vars:
            if fjw__xzguw is not None:
                vars.append(fjw__xzguw)
        return vars

    def get_live_out_vars(self):
        vars = []
        for fjw__xzguw in self.out_data_vars:
            if fjw__xzguw is not None:
                vars.append(fjw__xzguw)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        uwggu__phdxm = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[uwggu__phdxm])
                uwggu__phdxm += 1
            else:
                left_vars.append(None)
            start = 1
        wznnk__prcik = max(self.n_left_table_cols - 1, 0)
        for qeozq__zaw in range(start, len(self.left_vars)):
            if qeozq__zaw + wznnk__prcik in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[uwggu__phdxm])
                uwggu__phdxm += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        uwggu__phdxm = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[uwggu__phdxm])
                uwggu__phdxm += 1
            else:
                right_vars.append(None)
            start = 1
        wznnk__prcik = max(self.n_right_table_cols - 1, 0)
        for qeozq__zaw in range(start, len(self.right_vars)):
            if qeozq__zaw + wznnk__prcik in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[uwggu__phdxm])
                uwggu__phdxm += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        uxx__jbkwl = [self.has_live_out_table_var, self.has_live_out_index_var]
        uwggu__phdxm = 0
        for qeozq__zaw in range(len(self.out_data_vars)):
            if not uxx__jbkwl[qeozq__zaw]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[uwggu__phdxm])
                uwggu__phdxm += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {qeozq__zaw for qeozq__zaw in self.out_used_cols if 
            qeozq__zaw < self.n_out_table_cols}

    def __repr__(self):
        qohiu__xwxr = ', '.join([f'{tmug__vaho}' for tmug__vaho in self.
            left_col_names])
        nztan__lus = f'left={{{qohiu__xwxr}}}'
        qohiu__xwxr = ', '.join([f'{tmug__vaho}' for tmug__vaho in self.
            right_col_names])
        cjvuu__nwhlh = f'right={{{qohiu__xwxr}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, nztan__lus, cjvuu__nwhlh)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    gnjvq__vxm = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    mfmjt__shz = []
    goa__lhgnm = join_node.get_live_left_vars()
    for iwey__rwwy in goa__lhgnm:
        spdpx__lig = typemap[iwey__rwwy.name]
        qzul__knuon = equiv_set.get_shape(iwey__rwwy)
        if qzul__knuon:
            mfmjt__shz.append(qzul__knuon[0])
    if len(mfmjt__shz) > 1:
        equiv_set.insert_equiv(*mfmjt__shz)
    mfmjt__shz = []
    goa__lhgnm = list(join_node.get_live_right_vars())
    for iwey__rwwy in goa__lhgnm:
        spdpx__lig = typemap[iwey__rwwy.name]
        qzul__knuon = equiv_set.get_shape(iwey__rwwy)
        if qzul__knuon:
            mfmjt__shz.append(qzul__knuon[0])
    if len(mfmjt__shz) > 1:
        equiv_set.insert_equiv(*mfmjt__shz)
    mfmjt__shz = []
    for gtrlu__vvr in join_node.get_live_out_vars():
        spdpx__lig = typemap[gtrlu__vvr.name]
        vmqem__qosde = array_analysis._gen_shape_call(equiv_set, gtrlu__vvr,
            spdpx__lig.ndim, None, gnjvq__vxm)
        equiv_set.insert_equiv(gtrlu__vvr, vmqem__qosde)
        mfmjt__shz.append(vmqem__qosde[0])
        equiv_set.define(gtrlu__vvr, set())
    if len(mfmjt__shz) > 1:
        equiv_set.insert_equiv(*mfmjt__shz)
    return [], gnjvq__vxm


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    jxd__bktle = Distribution.OneD
    kjvg__bkxf = Distribution.OneD
    for iwey__rwwy in join_node.get_live_left_vars():
        jxd__bktle = Distribution(min(jxd__bktle.value, array_dists[
            iwey__rwwy.name].value))
    for iwey__rwwy in join_node.get_live_right_vars():
        kjvg__bkxf = Distribution(min(kjvg__bkxf.value, array_dists[
            iwey__rwwy.name].value))
    iylk__xnu = Distribution.OneD_Var
    for gtrlu__vvr in join_node.get_live_out_vars():
        if gtrlu__vvr.name in array_dists:
            iylk__xnu = Distribution(min(iylk__xnu.value, array_dists[
                gtrlu__vvr.name].value))
    kqje__mhyq = Distribution(min(iylk__xnu.value, jxd__bktle.value))
    hfmf__wvf = Distribution(min(iylk__xnu.value, kjvg__bkxf.value))
    iylk__xnu = Distribution(max(kqje__mhyq.value, hfmf__wvf.value))
    for gtrlu__vvr in join_node.get_live_out_vars():
        array_dists[gtrlu__vvr.name] = iylk__xnu
    if iylk__xnu != Distribution.OneD_Var:
        jxd__bktle = iylk__xnu
        kjvg__bkxf = iylk__xnu
    for iwey__rwwy in join_node.get_live_left_vars():
        array_dists[iwey__rwwy.name] = jxd__bktle
    for iwey__rwwy in join_node.get_live_right_vars():
        array_dists[iwey__rwwy.name] = kjvg__bkxf
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(fjw__xzguw, callback,
        cbdata) for fjw__xzguw in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(fjw__xzguw, callback,
        cbdata) for fjw__xzguw in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(fjw__xzguw, callback,
        cbdata) for fjw__xzguw in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        xnnn__yipm = []
        kkmzx__gxgk = join_node.get_out_table_var()
        if kkmzx__gxgk.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for vid__bkbs in join_node.out_to_input_col_map.keys():
            if vid__bkbs in join_node.out_used_cols:
                continue
            xnnn__yipm.append(vid__bkbs)
            if join_node.indicator_col_num == vid__bkbs:
                join_node.indicator_col_num = -1
                continue
            if vid__bkbs == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            ffu__kixh, vid__bkbs = join_node.out_to_input_col_map[vid__bkbs]
            if ffu__kixh == 'left':
                if (vid__bkbs not in join_node.left_key_set and vid__bkbs
                     not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(vid__bkbs)
                    if not join_node.is_left_table:
                        join_node.left_vars[vid__bkbs] = None
            elif ffu__kixh == 'right':
                if (vid__bkbs not in join_node.right_key_set and vid__bkbs
                     not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(vid__bkbs)
                    if not join_node.is_right_table:
                        join_node.right_vars[vid__bkbs] = None
        for qeozq__zaw in xnnn__yipm:
            del join_node.out_to_input_col_map[qeozq__zaw]
        if join_node.is_left_table:
            jcaya__phz = set(range(join_node.n_left_table_cols))
            niiow__deomf = not bool(jcaya__phz - join_node.left_dead_var_inds)
            if niiow__deomf:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            jcaya__phz = set(range(join_node.n_right_table_cols))
            niiow__deomf = not bool(jcaya__phz - join_node.right_dead_var_inds)
            if niiow__deomf:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        xlf__rygpk = join_node.get_out_index_var()
        if xlf__rygpk.name not in lives:
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
    zkx__btj = False
    if join_node.has_live_out_table_var:
        vdtll__ibr = join_node.get_out_table_var().name
        onzc__eznnk, jmd__kjvm, mzwx__vcnj = get_live_column_nums_block(
            column_live_map, equiv_vars, vdtll__ibr)
        if not (jmd__kjvm or mzwx__vcnj):
            onzc__eznnk = trim_extra_used_columns(onzc__eznnk, join_node.
                n_out_table_cols)
            sdgwt__xbc = join_node.get_out_table_used_cols()
            if len(onzc__eznnk) != len(sdgwt__xbc):
                zkx__btj = not (join_node.is_left_table and join_node.
                    is_right_table)
                ftzuv__qdgpo = sdgwt__xbc - onzc__eznnk
                join_node.out_used_cols = (join_node.out_used_cols -
                    ftzuv__qdgpo)
    return zkx__btj


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        zzhy__jlpim = join_node.get_out_table_var()
        imvfj__hprw, jmd__kjvm, mzwx__vcnj = _compute_table_column_uses(
            zzhy__jlpim.name, table_col_use_map, equiv_vars)
    else:
        imvfj__hprw, jmd__kjvm, mzwx__vcnj = set(), False, False
    if join_node.has_live_left_table_var:
        uxhp__xrivx = join_node.left_vars[0].name
        pnn__cly, tdcn__hfl, ygsra__bvch = block_use_map[uxhp__xrivx]
        if not (tdcn__hfl or ygsra__bvch):
            vmvay__cozm = set([join_node.out_to_input_col_map[qeozq__zaw][1
                ] for qeozq__zaw in imvfj__hprw if join_node.
                out_to_input_col_map[qeozq__zaw][0] == 'left'])
            sihwc__gnfwv = set(qeozq__zaw for qeozq__zaw in join_node.
                left_key_set | join_node.left_cond_cols if qeozq__zaw <
                join_node.n_left_table_cols)
            if not (jmd__kjvm or mzwx__vcnj):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (vmvay__cozm | sihwc__gnfwv)
            block_use_map[uxhp__xrivx] = (pnn__cly | vmvay__cozm |
                sihwc__gnfwv, jmd__kjvm or mzwx__vcnj, False)
    if join_node.has_live_right_table_var:
        nmn__biqku = join_node.right_vars[0].name
        pnn__cly, tdcn__hfl, ygsra__bvch = block_use_map[nmn__biqku]
        if not (tdcn__hfl or ygsra__bvch):
            oqfz__slqhc = set([join_node.out_to_input_col_map[qeozq__zaw][1
                ] for qeozq__zaw in imvfj__hprw if join_node.
                out_to_input_col_map[qeozq__zaw][0] == 'right'])
            khlf__ofe = set(qeozq__zaw for qeozq__zaw in join_node.
                right_key_set | join_node.right_cond_cols if qeozq__zaw <
                join_node.n_right_table_cols)
            if not (jmd__kjvm or mzwx__vcnj):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (oqfz__slqhc | khlf__ofe)
            block_use_map[nmn__biqku] = (pnn__cly | oqfz__slqhc | khlf__ofe,
                jmd__kjvm or mzwx__vcnj, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({nto__gfj.name for nto__gfj in join_node.
        get_live_left_vars()})
    use_set.update({nto__gfj.name for nto__gfj in join_node.
        get_live_right_vars()})
    def_set.update({nto__gfj.name for nto__gfj in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    bgvz__rmo = set(nto__gfj.name for nto__gfj in join_node.get_live_out_vars()
        )
    return set(), bgvz__rmo


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(fjw__xzguw, var_dict) for
        fjw__xzguw in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(fjw__xzguw, var_dict) for
        fjw__xzguw in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(fjw__xzguw,
        var_dict) for fjw__xzguw in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for iwey__rwwy in join_node.get_live_out_vars():
        definitions[iwey__rwwy.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        uutix__jrykg = join_node.loc.strformat()
        frtjx__gwkjt = [join_node.left_col_names[qeozq__zaw] for qeozq__zaw in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        fyy__rcvln = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', fyy__rcvln,
            uutix__jrykg, frtjx__gwkjt)
        pfm__bzhe = [join_node.right_col_names[qeozq__zaw] for qeozq__zaw in
            sorted(set(range(len(join_node.right_col_names))) - join_node.
            right_dead_var_inds)]
        fyy__rcvln = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', fyy__rcvln,
            uutix__jrykg, pfm__bzhe)
        awp__wfgv = [join_node.out_col_names[qeozq__zaw] for qeozq__zaw in
            sorted(join_node.get_out_table_used_cols())]
        fyy__rcvln = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', fyy__rcvln,
            uutix__jrykg, awp__wfgv)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    zcgd__hsz = len(join_node.left_keys)
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
    ebpg__qmhm = 0
    yhqhz__mddlv = 0
    imyj__xqhsi = []
    for tmug__vaho in join_node.left_keys:
        vyry__xhgk = join_node.left_var_map[tmug__vaho]
        if not join_node.is_left_table:
            imyj__xqhsi.append(join_node.left_vars[vyry__xhgk])
        uxx__jbkwl = 1
        wfp__xrbn = join_node.left_to_output_map[vyry__xhgk]
        if tmug__vaho == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == vyry__xhgk):
                out_physical_to_logical_list.append(wfp__xrbn)
                left_used_key_nums.add(vyry__xhgk)
            else:
                uxx__jbkwl = 0
        elif wfp__xrbn not in join_node.out_used_cols:
            uxx__jbkwl = 0
        elif vyry__xhgk in left_used_key_nums:
            uxx__jbkwl = 0
        else:
            left_used_key_nums.add(vyry__xhgk)
            out_physical_to_logical_list.append(wfp__xrbn)
        left_physical_to_logical_list.append(vyry__xhgk)
        left_logical_physical_map[vyry__xhgk] = ebpg__qmhm
        ebpg__qmhm += 1
        left_key_in_output.append(uxx__jbkwl)
    imyj__xqhsi = tuple(imyj__xqhsi)
    nmxu__ckxki = []
    for qeozq__zaw in range(len(join_node.left_col_names)):
        if (qeozq__zaw not in join_node.left_dead_var_inds and qeozq__zaw
             not in join_node.left_key_set):
            if not join_node.is_left_table:
                nto__gfj = join_node.left_vars[qeozq__zaw]
                nmxu__ckxki.append(nto__gfj)
            mwpu__zmg = 1
            vho__tpm = 1
            wfp__xrbn = join_node.left_to_output_map[qeozq__zaw]
            if qeozq__zaw in join_node.left_cond_cols:
                if wfp__xrbn not in join_node.out_used_cols:
                    mwpu__zmg = 0
                left_key_in_output.append(mwpu__zmg)
            elif qeozq__zaw in join_node.left_dead_var_inds:
                mwpu__zmg = 0
                vho__tpm = 0
            if mwpu__zmg:
                out_physical_to_logical_list.append(wfp__xrbn)
            if vho__tpm:
                left_physical_to_logical_list.append(qeozq__zaw)
                left_logical_physical_map[qeozq__zaw] = ebpg__qmhm
                ebpg__qmhm += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            nmxu__ckxki.append(join_node.left_vars[join_node.index_col_num])
        wfp__xrbn = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(wfp__xrbn)
        left_physical_to_logical_list.append(join_node.index_col_num)
    nmxu__ckxki = tuple(nmxu__ckxki)
    if join_node.is_left_table:
        nmxu__ckxki = tuple(join_node.get_live_left_vars())
    oyt__jnim = []
    for qeozq__zaw, tmug__vaho in enumerate(join_node.right_keys):
        vyry__xhgk = join_node.right_var_map[tmug__vaho]
        if not join_node.is_right_table:
            oyt__jnim.append(join_node.right_vars[vyry__xhgk])
        if not join_node.vect_same_key[qeozq__zaw] and not join_node.is_join:
            uxx__jbkwl = 1
            if vyry__xhgk not in join_node.right_to_output_map:
                uxx__jbkwl = 0
            else:
                wfp__xrbn = join_node.right_to_output_map[vyry__xhgk]
                if tmug__vaho == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        vyry__xhgk):
                        out_physical_to_logical_list.append(wfp__xrbn)
                        right_used_key_nums.add(vyry__xhgk)
                    else:
                        uxx__jbkwl = 0
                elif wfp__xrbn not in join_node.out_used_cols:
                    uxx__jbkwl = 0
                elif vyry__xhgk in right_used_key_nums:
                    uxx__jbkwl = 0
                else:
                    right_used_key_nums.add(vyry__xhgk)
                    out_physical_to_logical_list.append(wfp__xrbn)
            right_key_in_output.append(uxx__jbkwl)
        right_physical_to_logical_list.append(vyry__xhgk)
        right_logical_physical_map[vyry__xhgk] = yhqhz__mddlv
        yhqhz__mddlv += 1
    oyt__jnim = tuple(oyt__jnim)
    msmtn__eivj = []
    for qeozq__zaw in range(len(join_node.right_col_names)):
        if (qeozq__zaw not in join_node.right_dead_var_inds and qeozq__zaw
             not in join_node.right_key_set):
            if not join_node.is_right_table:
                msmtn__eivj.append(join_node.right_vars[qeozq__zaw])
            mwpu__zmg = 1
            vho__tpm = 1
            wfp__xrbn = join_node.right_to_output_map[qeozq__zaw]
            if qeozq__zaw in join_node.right_cond_cols:
                if wfp__xrbn not in join_node.out_used_cols:
                    mwpu__zmg = 0
                right_key_in_output.append(mwpu__zmg)
            elif qeozq__zaw in join_node.right_dead_var_inds:
                mwpu__zmg = 0
                vho__tpm = 0
            if mwpu__zmg:
                out_physical_to_logical_list.append(wfp__xrbn)
            if vho__tpm:
                right_physical_to_logical_list.append(qeozq__zaw)
                right_logical_physical_map[qeozq__zaw] = yhqhz__mddlv
                yhqhz__mddlv += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            msmtn__eivj.append(join_node.right_vars[join_node.index_col_num])
        wfp__xrbn = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(wfp__xrbn)
        right_physical_to_logical_list.append(join_node.index_col_num)
    msmtn__eivj = tuple(msmtn__eivj)
    if join_node.is_right_table:
        msmtn__eivj = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    moen__rmpf = imyj__xqhsi + oyt__jnim + nmxu__ckxki + msmtn__eivj
    lxaf__sez = tuple(typemap[nto__gfj.name] for nto__gfj in moen__rmpf)
    left_other_names = tuple('t1_c' + str(qeozq__zaw) for qeozq__zaw in
        range(len(nmxu__ckxki)))
    right_other_names = tuple('t2_c' + str(qeozq__zaw) for qeozq__zaw in
        range(len(msmtn__eivj)))
    if join_node.is_left_table:
        utcup__ugv = ()
    else:
        utcup__ugv = tuple('t1_key' + str(qeozq__zaw) for qeozq__zaw in
            range(zcgd__hsz))
    if join_node.is_right_table:
        kxk__ausla = ()
    else:
        kxk__ausla = tuple('t2_key' + str(qeozq__zaw) for qeozq__zaw in
            range(zcgd__hsz))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(utcup__ugv + kxk__ausla +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            jbtd__zmg = typemap[join_node.left_vars[0].name]
        else:
            jbtd__zmg = types.none
        for xtdh__vqj in left_physical_to_logical_list:
            if xtdh__vqj < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                spdpx__lig = jbtd__zmg.arr_types[xtdh__vqj]
            else:
                spdpx__lig = typemap[join_node.left_vars[-1].name]
            if xtdh__vqj in join_node.left_key_set:
                left_key_types.append(spdpx__lig)
            else:
                left_other_types.append(spdpx__lig)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[nto__gfj.name] for nto__gfj in
            imyj__xqhsi)
        left_other_types = tuple([typemap[tmug__vaho.name] for tmug__vaho in
            nmxu__ckxki])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            jbtd__zmg = typemap[join_node.right_vars[0].name]
        else:
            jbtd__zmg = types.none
        for xtdh__vqj in right_physical_to_logical_list:
            if xtdh__vqj < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                spdpx__lig = jbtd__zmg.arr_types[xtdh__vqj]
            else:
                spdpx__lig = typemap[join_node.right_vars[-1].name]
            if xtdh__vqj in join_node.right_key_set:
                right_key_types.append(spdpx__lig)
            else:
                right_other_types.append(spdpx__lig)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[nto__gfj.name] for nto__gfj in
            oyt__jnim)
        right_other_types = tuple([typemap[tmug__vaho.name] for tmug__vaho in
            msmtn__eivj])
    matched_key_types = []
    for qeozq__zaw in range(zcgd__hsz):
        wgwe__jwfy = _match_join_key_types(left_key_types[qeozq__zaw],
            right_key_types[qeozq__zaw], loc)
        glbs[f'key_type_{qeozq__zaw}'] = wgwe__jwfy
        matched_key_types.append(wgwe__jwfy)
    if join_node.is_left_table:
        fpu__jedyz = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if fpu__jedyz:
            oir__mqwu = False
            usgme__auhs = False
            rqb__juasb = None
            if join_node.has_live_left_table_var:
                ddgwg__ttziw = list(typemap[join_node.left_vars[0].name].
                    arr_types)
            else:
                ddgwg__ttziw = None
            for vid__bkbs, spdpx__lig in fpu__jedyz.items():
                if vid__bkbs < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    ddgwg__ttziw[vid__bkbs] = spdpx__lig
                    oir__mqwu = True
                else:
                    rqb__juasb = spdpx__lig
                    usgme__auhs = True
            if oir__mqwu:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(ddgwg__ttziw))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if usgme__auhs:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = rqb__juasb
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({utcup__ugv[qeozq__zaw]}, key_type_{qeozq__zaw})'
             if left_key_types[qeozq__zaw] != matched_key_types[qeozq__zaw]
             else f'{utcup__ugv[qeozq__zaw]}' for qeozq__zaw in range(
            zcgd__hsz)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        fpu__jedyz = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if fpu__jedyz:
            oir__mqwu = False
            usgme__auhs = False
            rqb__juasb = None
            if join_node.has_live_right_table_var:
                ddgwg__ttziw = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                ddgwg__ttziw = None
            for vid__bkbs, spdpx__lig in fpu__jedyz.items():
                if vid__bkbs < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    ddgwg__ttziw[vid__bkbs] = spdpx__lig
                    oir__mqwu = True
                else:
                    rqb__juasb = spdpx__lig
                    usgme__auhs = True
            if oir__mqwu:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(ddgwg__ttziw))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if usgme__auhs:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = rqb__juasb
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({kxk__ausla[qeozq__zaw]}, key_type_{qeozq__zaw})'
             if right_key_types[qeozq__zaw] != matched_key_types[qeozq__zaw
            ] else f'{kxk__ausla[qeozq__zaw]}' for qeozq__zaw in range(
            zcgd__hsz)))
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
        for qeozq__zaw in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(qeozq__zaw,
                qeozq__zaw)
        for qeozq__zaw in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(
                qeozq__zaw, qeozq__zaw)
        for qeozq__zaw in range(zcgd__hsz):
            func_text += (
                f'    t1_keys_{qeozq__zaw} = out_t1_keys[{qeozq__zaw}]\n')
        for qeozq__zaw in range(zcgd__hsz):
            func_text += (
                f'    t2_keys_{qeozq__zaw} = out_t2_keys[{qeozq__zaw}]\n')
    arh__ixexm = {}
    exec(func_text, {}, arh__ixexm)
    lgsmd__ahaj = arh__ixexm['f']
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
    obt__aqd = compile_to_numba_ir(lgsmd__ahaj, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=lxaf__sez, typemap=typemap, calltypes
        =calltypes).blocks.popitem()[1]
    replace_arg_nodes(obt__aqd, moen__rmpf)
    fro__zmta = obt__aqd.body[:-3]
    if join_node.has_live_out_index_var:
        fro__zmta[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        fro__zmta[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        fro__zmta.pop(-1)
    elif not join_node.has_live_out_table_var:
        fro__zmta.pop(-2)
    return fro__zmta


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    sbv__komyn = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{sbv__komyn}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
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
    arh__ixexm = {}
    exec(func_text, table_getitem_funcs, arh__ixexm)
    pbog__rjjhj = arh__ixexm[f'bodo_join_gen_cond{sbv__komyn}']
    oxpr__sua = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    gdewy__xugk = numba.cfunc(oxpr__sua, nopython=True)(pbog__rjjhj)
    join_gen_cond_cfunc[gdewy__xugk.native_name] = gdewy__xugk
    join_gen_cond_cfunc_addr[gdewy__xugk.native_name] = gdewy__xugk.address
    return gdewy__xugk, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    spkp__jxmgj = []
    for tmug__vaho, pitd__lapop in name_to_var_map.items():
        ofx__cdfo = f'({table_name}.{tmug__vaho})'
        if ofx__cdfo not in expr:
            continue
        fqu__iks = f'getitem_{table_name}_val_{pitd__lapop}'
        zidiq__ytv = f'_bodo_{table_name}_val_{pitd__lapop}'
        if is_table_var:
            drkvi__xabet = typemap[col_vars[0].name].arr_types[pitd__lapop]
        else:
            drkvi__xabet = typemap[col_vars[pitd__lapop].name]
        if is_str_arr_type(drkvi__xabet
            ) or drkvi__xabet == bodo.binary_array_type:
            func_text += f"""  {zidiq__ytv}, {zidiq__ytv}_size = {fqu__iks}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {zidiq__ytv} = bodo.libs.str_arr_ext.decode_utf8({zidiq__ytv}, {zidiq__ytv}_size)
"""
        else:
            func_text += (
                f'  {zidiq__ytv} = {fqu__iks}({table_name}_data1, {table_name}_ind)\n'
                )
        lfff__ixup = logical_to_physical_ind[pitd__lapop]
        table_getitem_funcs[fqu__iks
            ] = bodo.libs.array._gen_row_access_intrinsic(drkvi__xabet,
            lfff__ixup)
        expr = expr.replace(ofx__cdfo, zidiq__ytv)
        gnug__bxp = f'({na_check_name}.{table_name}.{tmug__vaho})'
        if gnug__bxp in expr:
            uab__rgue = f'nacheck_{table_name}_val_{pitd__lapop}'
            lljg__zvuq = f'_bodo_isna_{table_name}_val_{pitd__lapop}'
            if isinstance(drkvi__xabet, bodo.libs.int_arr_ext.IntegerArrayType
                ) or drkvi__xabet in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(drkvi__xabet):
                func_text += f"""  {lljg__zvuq} = {uab__rgue}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += (
                    f'  {lljg__zvuq} = {uab__rgue}({table_name}_data1, {table_name}_ind)\n'
                    )
            table_getitem_funcs[uab__rgue
                ] = bodo.libs.array._gen_row_na_check_intrinsic(drkvi__xabet,
                lfff__ixup)
            expr = expr.replace(gnug__bxp, lljg__zvuq)
        if pitd__lapop not in key_set:
            spkp__jxmgj.append(lfff__ixup)
    return expr, func_text, spkp__jxmgj


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as pxq__trfo:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    wfxo__quc = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[nto__gfj.name] in wfxo__quc for
        nto__gfj in join_node.get_live_left_vars())
    right_parallel = all(array_dists[nto__gfj.name] in wfxo__quc for
        nto__gfj in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[nto__gfj.name] in wfxo__quc for nto__gfj in
            join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[nto__gfj.name] in wfxo__quc for nto__gfj in
            join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[nto__gfj.name] in wfxo__quc for nto__gfj in
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
    kjg__whinp = set(left_col_nums)
    vekb__erif = set(right_col_nums)
    pkese__jzy = join_node.vect_same_key
    flse__dxsxo = []
    for qeozq__zaw in range(len(left_key_types)):
        if left_key_in_output[qeozq__zaw]:
            flse__dxsxo.append(needs_typechange(matched_key_types[
                qeozq__zaw], join_node.is_right, pkese__jzy[qeozq__zaw]))
    qqejz__mfue = len(left_key_types)
    qtzh__vjxky = 0
    zcfy__cvy = left_physical_to_logical_list[len(left_key_types):]
    for qeozq__zaw, xtdh__vqj in enumerate(zcfy__cvy):
        epos__egm = True
        if xtdh__vqj in kjg__whinp:
            epos__egm = left_key_in_output[qqejz__mfue]
            qqejz__mfue += 1
        if epos__egm:
            flse__dxsxo.append(needs_typechange(left_other_types[qeozq__zaw
                ], join_node.is_right, False))
    for qeozq__zaw in range(len(right_key_types)):
        if not pkese__jzy[qeozq__zaw] and not join_node.is_join:
            if right_key_in_output[qtzh__vjxky]:
                flse__dxsxo.append(needs_typechange(matched_key_types[
                    qeozq__zaw], join_node.is_left, False))
            qtzh__vjxky += 1
    lii__wwbum = right_physical_to_logical_list[len(right_key_types):]
    for qeozq__zaw, xtdh__vqj in enumerate(lii__wwbum):
        epos__egm = True
        if xtdh__vqj in vekb__erif:
            epos__egm = right_key_in_output[qtzh__vjxky]
            qtzh__vjxky += 1
        if epos__egm:
            flse__dxsxo.append(needs_typechange(right_other_types[
                qeozq__zaw], join_node.is_left, False))
    zcgd__hsz = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            ghmv__lkr = left_other_names[1:]
            kkmzx__gxgk = left_other_names[0]
        else:
            ghmv__lkr = left_other_names
            kkmzx__gxgk = None
        dqlu__foomn = '()' if len(ghmv__lkr) == 0 else f'({ghmv__lkr[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({kkmzx__gxgk}, {dqlu__foomn}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        acsc__rebg = []
        for qeozq__zaw in range(zcgd__hsz):
            acsc__rebg.append('t1_keys[{}]'.format(qeozq__zaw))
        for qeozq__zaw in range(len(left_other_names)):
            acsc__rebg.append('data_left[{}]'.format(qeozq__zaw))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(shbb__ufm) for shbb__ufm in acsc__rebg))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            ebxyd__gdp = right_other_names[1:]
            kkmzx__gxgk = right_other_names[0]
        else:
            ebxyd__gdp = right_other_names
            kkmzx__gxgk = None
        dqlu__foomn = '()' if len(ebxyd__gdp) == 0 else f'({ebxyd__gdp[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({kkmzx__gxgk}, {dqlu__foomn}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        agdt__xisiz = []
        for qeozq__zaw in range(zcgd__hsz):
            agdt__xisiz.append('t2_keys[{}]'.format(qeozq__zaw))
        for qeozq__zaw in range(len(right_other_names)):
            agdt__xisiz.append('data_right[{}]'.format(qeozq__zaw))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(shbb__ufm) for shbb__ufm in agdt__xisiz)
            )
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(pkese__jzy, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(flse__dxsxo, dtype=np.int64)
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
        .format(left_parallel, right_parallel, zcgd__hsz, len(zcfy__cvy),
        len(lii__wwbum), join_node.is_left, join_node.is_right, join_node.
        is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    nfzyj__lnsp = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {nfzyj__lnsp}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        uwggu__phdxm = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{uwggu__phdxm}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        fpu__jedyz = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        fpu__jedyz.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        oir__mqwu = False
        usgme__auhs = False
        if join_node.has_live_out_table_var:
            ddgwg__ttziw = list(out_table_type.arr_types)
        else:
            ddgwg__ttziw = None
        for vid__bkbs, spdpx__lig in fpu__jedyz.items():
            if vid__bkbs < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                ddgwg__ttziw[vid__bkbs] = spdpx__lig
                oir__mqwu = True
            else:
                rqb__juasb = spdpx__lig
                usgme__auhs = True
        if oir__mqwu:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            xnlw__ogvt = bodo.TableType(tuple(ddgwg__ttziw))
            glbs['py_table_type'] = xnlw__ogvt
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if usgme__auhs:
            glbs['index_col_type'] = rqb__juasb
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
    fpu__jedyz: Dict[int, types.Type] = {}
    zcgd__hsz = len(matched_key_types)
    for qeozq__zaw in range(zcgd__hsz):
        if used_key_nums is None or qeozq__zaw in used_key_nums:
            if matched_key_types[qeozq__zaw] != key_types[qeozq__zaw] and (
                convert_dict_col or key_types[qeozq__zaw] != bodo.
                dict_str_arr_type):
                if output_map:
                    uwggu__phdxm = output_map[qeozq__zaw]
                else:
                    uwggu__phdxm = qeozq__zaw
                fpu__jedyz[uwggu__phdxm] = matched_key_types[qeozq__zaw]
    return fpu__jedyz


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    knnr__wxtoa = bodo.libs.distributed_api.get_size()
    cfmt__rbsc = np.empty(knnr__wxtoa, left_key_arrs[0].dtype)
    wnb__ojjw = np.empty(knnr__wxtoa, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(cfmt__rbsc, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(wnb__ojjw, left_key_arrs[0][-1])
    yqeiw__nzq = np.zeros(knnr__wxtoa, np.int32)
    vlsg__abxg = np.zeros(knnr__wxtoa, np.int32)
    ofh__aopp = np.zeros(knnr__wxtoa, np.int32)
    uytnu__qajy = right_key_arrs[0][0]
    unm__bhnpa = right_key_arrs[0][-1]
    wznnk__prcik = -1
    qeozq__zaw = 0
    while qeozq__zaw < knnr__wxtoa - 1 and wnb__ojjw[qeozq__zaw] < uytnu__qajy:
        qeozq__zaw += 1
    while qeozq__zaw < knnr__wxtoa and cfmt__rbsc[qeozq__zaw] <= unm__bhnpa:
        wznnk__prcik, kcam__tzymb = _count_overlap(right_key_arrs[0],
            cfmt__rbsc[qeozq__zaw], wnb__ojjw[qeozq__zaw])
        if wznnk__prcik != 0:
            wznnk__prcik -= 1
            kcam__tzymb += 1
        yqeiw__nzq[qeozq__zaw] = kcam__tzymb
        vlsg__abxg[qeozq__zaw] = wznnk__prcik
        qeozq__zaw += 1
    while qeozq__zaw < knnr__wxtoa:
        yqeiw__nzq[qeozq__zaw] = 1
        vlsg__abxg[qeozq__zaw] = len(right_key_arrs[0]) - 1
        qeozq__zaw += 1
    bodo.libs.distributed_api.alltoall(yqeiw__nzq, ofh__aopp, 1)
    chl__eda = ofh__aopp.sum()
    fbqt__dyny = np.empty(chl__eda, right_key_arrs[0].dtype)
    ftqn__chiud = alloc_arr_tup(chl__eda, right_data)
    pdhrq__lam = bodo.ir.join.calc_disp(ofh__aopp)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], fbqt__dyny,
        yqeiw__nzq, ofh__aopp, vlsg__abxg, pdhrq__lam)
    bodo.libs.distributed_api.alltoallv_tup(right_data, ftqn__chiud,
        yqeiw__nzq, ofh__aopp, vlsg__abxg, pdhrq__lam)
    return (fbqt__dyny,), ftqn__chiud


@numba.njit
def _count_overlap(r_key_arr, start, end):
    kcam__tzymb = 0
    wznnk__prcik = 0
    wpx__okqbg = 0
    while wpx__okqbg < len(r_key_arr) and r_key_arr[wpx__okqbg] < start:
        wznnk__prcik += 1
        wpx__okqbg += 1
    while wpx__okqbg < len(r_key_arr) and start <= r_key_arr[wpx__okqbg
        ] <= end:
        wpx__okqbg += 1
        kcam__tzymb += 1
    return wznnk__prcik, kcam__tzymb


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    ijwlp__wkd = np.empty_like(arr)
    ijwlp__wkd[0] = 0
    for qeozq__zaw in range(1, len(arr)):
        ijwlp__wkd[qeozq__zaw] = ijwlp__wkd[qeozq__zaw - 1] + arr[
            qeozq__zaw - 1]
    return ijwlp__wkd


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    dkt__fqdft = len(left_keys[0])
    amjdi__peeuz = len(right_keys[0])
    svg__jrs = alloc_arr_tup(dkt__fqdft, left_keys)
    cpzfr__qvw = alloc_arr_tup(dkt__fqdft, right_keys)
    ztbon__wjaom = alloc_arr_tup(dkt__fqdft, data_left)
    ros__yxqg = alloc_arr_tup(dkt__fqdft, data_right)
    psbr__kquzj = 0
    apkik__zjg = 0
    for psbr__kquzj in range(dkt__fqdft):
        if apkik__zjg < 0:
            apkik__zjg = 0
        while apkik__zjg < amjdi__peeuz and getitem_arr_tup(right_keys,
            apkik__zjg) <= getitem_arr_tup(left_keys, psbr__kquzj):
            apkik__zjg += 1
        apkik__zjg -= 1
        setitem_arr_tup(svg__jrs, psbr__kquzj, getitem_arr_tup(left_keys,
            psbr__kquzj))
        setitem_arr_tup(ztbon__wjaom, psbr__kquzj, getitem_arr_tup(
            data_left, psbr__kquzj))
        if apkik__zjg >= 0:
            setitem_arr_tup(cpzfr__qvw, psbr__kquzj, getitem_arr_tup(
                right_keys, apkik__zjg))
            setitem_arr_tup(ros__yxqg, psbr__kquzj, getitem_arr_tup(
                data_right, apkik__zjg))
        else:
            bodo.libs.array_kernels.setna_tup(cpzfr__qvw, psbr__kquzj)
            bodo.libs.array_kernels.setna_tup(ros__yxqg, psbr__kquzj)
    return svg__jrs, cpzfr__qvw, ztbon__wjaom, ros__yxqg
