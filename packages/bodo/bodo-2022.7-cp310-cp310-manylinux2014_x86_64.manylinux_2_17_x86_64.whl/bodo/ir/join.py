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
        ihu__ycdf = func.signature
        enb__szn = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        lvzx__khsz = cgutils.get_or_insert_function(builder.module,
            enb__szn, sym._literal_value)
        builder.call(lvzx__khsz, [context.get_constant_null(ihu__ycdf.args[
            0]), context.get_constant_null(ihu__ycdf.args[1]), context.
            get_constant_null(ihu__ycdf.args[2]), context.get_constant_null
            (ihu__ycdf.args[3]), context.get_constant_null(ihu__ycdf.args[4
            ]), context.get_constant_null(ihu__ycdf.args[5]), context.
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
        jic__wmv = left_df_type.columns
        pxum__tfp = right_df_type.columns
        self.left_col_names = jic__wmv
        self.right_col_names = pxum__tfp
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(jic__wmv) if self.is_left_table else 0
        self.n_right_table_cols = len(pxum__tfp) if self.is_right_table else 0
        nbu__eivk = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        edw__abtsh = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(nbu__eivk)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(edw__abtsh)
        self.left_var_map = {vcxb__sivzm: kucc__tefc for kucc__tefc,
            vcxb__sivzm in enumerate(jic__wmv)}
        self.right_var_map = {vcxb__sivzm: kucc__tefc for kucc__tefc,
            vcxb__sivzm in enumerate(pxum__tfp)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = nbu__eivk
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = edw__abtsh
        self.left_key_set = set(self.left_var_map[vcxb__sivzm] for
            vcxb__sivzm in left_keys)
        self.right_key_set = set(self.right_var_map[vcxb__sivzm] for
            vcxb__sivzm in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[vcxb__sivzm] for
                vcxb__sivzm in jic__wmv if f'(left.{vcxb__sivzm})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[vcxb__sivzm] for
                vcxb__sivzm in pxum__tfp if f'(right.{vcxb__sivzm})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        xxuiq__iosv: int = -1
        grz__jxakq = set(left_keys) & set(right_keys)
        vso__qal = set(jic__wmv) & set(pxum__tfp)
        funqh__zej = vso__qal - grz__jxakq
        hgi__ysqn: Dict[int, (Literal['left', 'right'], int)] = {}
        wkkv__kcn: Dict[int, int] = {}
        mjtjl__cxpdw: Dict[int, int] = {}
        for kucc__tefc, vcxb__sivzm in enumerate(jic__wmv):
            if vcxb__sivzm in funqh__zej:
                qhjwd__injrv = str(vcxb__sivzm) + suffix_left
                ybc__ybbyo = out_df_type.column_index[qhjwd__injrv]
                if (right_index and not left_index and kucc__tefc in self.
                    left_key_set):
                    xxuiq__iosv = out_df_type.column_index[vcxb__sivzm]
                    hgi__ysqn[xxuiq__iosv] = 'left', kucc__tefc
            else:
                ybc__ybbyo = out_df_type.column_index[vcxb__sivzm]
            hgi__ysqn[ybc__ybbyo] = 'left', kucc__tefc
            wkkv__kcn[kucc__tefc] = ybc__ybbyo
        for kucc__tefc, vcxb__sivzm in enumerate(pxum__tfp):
            if vcxb__sivzm not in grz__jxakq:
                if vcxb__sivzm in funqh__zej:
                    ttbp__ledw = str(vcxb__sivzm) + suffix_right
                    ybc__ybbyo = out_df_type.column_index[ttbp__ledw]
                    if (left_index and not right_index and kucc__tefc in
                        self.right_key_set):
                        xxuiq__iosv = out_df_type.column_index[vcxb__sivzm]
                        hgi__ysqn[xxuiq__iosv] = 'right', kucc__tefc
                else:
                    ybc__ybbyo = out_df_type.column_index[vcxb__sivzm]
                hgi__ysqn[ybc__ybbyo] = 'right', kucc__tefc
                mjtjl__cxpdw[kucc__tefc] = ybc__ybbyo
        if self.left_vars[-1] is not None:
            wkkv__kcn[nbu__eivk] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            mjtjl__cxpdw[edw__abtsh] = self.n_out_table_cols
        self.out_to_input_col_map = hgi__ysqn
        self.left_to_output_map = wkkv__kcn
        self.right_to_output_map = mjtjl__cxpdw
        self.extra_data_col_num = xxuiq__iosv
        if len(out_data_vars) > 1:
            ytykp__bpy = 'left' if right_index else 'right'
            if ytykp__bpy == 'left':
                ijf__wangk = nbu__eivk
            elif ytykp__bpy == 'right':
                ijf__wangk = edw__abtsh
        else:
            ytykp__bpy = None
            ijf__wangk = -1
        self.index_source = ytykp__bpy
        self.index_col_num = ijf__wangk
        dekzq__sghfe = []
        moh__iqpz = len(left_keys)
        for lphl__yhlk in range(moh__iqpz):
            firc__ejk = left_keys[lphl__yhlk]
            dqzzk__fldig = right_keys[lphl__yhlk]
            dekzq__sghfe.append(firc__ejk == dqzzk__fldig)
        self.vect_same_key = dekzq__sghfe

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
        for ugm__vva in self.left_vars:
            if ugm__vva is not None:
                vars.append(ugm__vva)
        return vars

    def get_live_right_vars(self):
        vars = []
        for ugm__vva in self.right_vars:
            if ugm__vva is not None:
                vars.append(ugm__vva)
        return vars

    def get_live_out_vars(self):
        vars = []
        for ugm__vva in self.out_data_vars:
            if ugm__vva is not None:
                vars.append(ugm__vva)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        iwuv__kxw = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[iwuv__kxw])
                iwuv__kxw += 1
            else:
                left_vars.append(None)
            start = 1
        zzcjy__exox = max(self.n_left_table_cols - 1, 0)
        for kucc__tefc in range(start, len(self.left_vars)):
            if kucc__tefc + zzcjy__exox in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[iwuv__kxw])
                iwuv__kxw += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        iwuv__kxw = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[iwuv__kxw])
                iwuv__kxw += 1
            else:
                right_vars.append(None)
            start = 1
        zzcjy__exox = max(self.n_right_table_cols - 1, 0)
        for kucc__tefc in range(start, len(self.right_vars)):
            if kucc__tefc + zzcjy__exox in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[iwuv__kxw])
                iwuv__kxw += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        eautz__lqx = [self.has_live_out_table_var, self.has_live_out_index_var]
        iwuv__kxw = 0
        for kucc__tefc in range(len(self.out_data_vars)):
            if not eautz__lqx[kucc__tefc]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[iwuv__kxw])
                iwuv__kxw += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {kucc__tefc for kucc__tefc in self.out_used_cols if 
            kucc__tefc < self.n_out_table_cols}

    def __repr__(self):
        cnu__unnea = ', '.join([f'{vcxb__sivzm}' for vcxb__sivzm in self.
            left_col_names])
        iyk__ycs = f'left={{{cnu__unnea}}}'
        cnu__unnea = ', '.join([f'{vcxb__sivzm}' for vcxb__sivzm in self.
            right_col_names])
        gdteq__zee = f'right={{{cnu__unnea}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, iyk__ycs, gdteq__zee)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    tywic__wopj = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    ieqhl__cuuh = []
    iltb__ssv = join_node.get_live_left_vars()
    for walr__yfiuv in iltb__ssv:
        qnotb__vveok = typemap[walr__yfiuv.name]
        mag__kou = equiv_set.get_shape(walr__yfiuv)
        if mag__kou:
            ieqhl__cuuh.append(mag__kou[0])
    if len(ieqhl__cuuh) > 1:
        equiv_set.insert_equiv(*ieqhl__cuuh)
    ieqhl__cuuh = []
    iltb__ssv = list(join_node.get_live_right_vars())
    for walr__yfiuv in iltb__ssv:
        qnotb__vveok = typemap[walr__yfiuv.name]
        mag__kou = equiv_set.get_shape(walr__yfiuv)
        if mag__kou:
            ieqhl__cuuh.append(mag__kou[0])
    if len(ieqhl__cuuh) > 1:
        equiv_set.insert_equiv(*ieqhl__cuuh)
    ieqhl__cuuh = []
    for jut__ptm in join_node.get_live_out_vars():
        qnotb__vveok = typemap[jut__ptm.name]
        cnj__pcv = array_analysis._gen_shape_call(equiv_set, jut__ptm,
            qnotb__vveok.ndim, None, tywic__wopj)
        equiv_set.insert_equiv(jut__ptm, cnj__pcv)
        ieqhl__cuuh.append(cnj__pcv[0])
        equiv_set.define(jut__ptm, set())
    if len(ieqhl__cuuh) > 1:
        equiv_set.insert_equiv(*ieqhl__cuuh)
    return [], tywic__wopj


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    vfkq__bszym = Distribution.OneD
    lqbkj__vclg = Distribution.OneD
    for walr__yfiuv in join_node.get_live_left_vars():
        vfkq__bszym = Distribution(min(vfkq__bszym.value, array_dists[
            walr__yfiuv.name].value))
    for walr__yfiuv in join_node.get_live_right_vars():
        lqbkj__vclg = Distribution(min(lqbkj__vclg.value, array_dists[
            walr__yfiuv.name].value))
    pvc__mhig = Distribution.OneD_Var
    for jut__ptm in join_node.get_live_out_vars():
        if jut__ptm.name in array_dists:
            pvc__mhig = Distribution(min(pvc__mhig.value, array_dists[
                jut__ptm.name].value))
    npnh__nhack = Distribution(min(pvc__mhig.value, vfkq__bszym.value))
    wdcun__chydg = Distribution(min(pvc__mhig.value, lqbkj__vclg.value))
    pvc__mhig = Distribution(max(npnh__nhack.value, wdcun__chydg.value))
    for jut__ptm in join_node.get_live_out_vars():
        array_dists[jut__ptm.name] = pvc__mhig
    if pvc__mhig != Distribution.OneD_Var:
        vfkq__bszym = pvc__mhig
        lqbkj__vclg = pvc__mhig
    for walr__yfiuv in join_node.get_live_left_vars():
        array_dists[walr__yfiuv.name] = vfkq__bszym
    for walr__yfiuv in join_node.get_live_right_vars():
        array_dists[walr__yfiuv.name] = lqbkj__vclg
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(ugm__vva, callback,
        cbdata) for ugm__vva in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(ugm__vva, callback,
        cbdata) for ugm__vva in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(ugm__vva, callback,
        cbdata) for ugm__vva in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        qym__uvyp = []
        xjxx__ujp = join_node.get_out_table_var()
        if xjxx__ujp.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for blmc__ipn in join_node.out_to_input_col_map.keys():
            if blmc__ipn in join_node.out_used_cols:
                continue
            qym__uvyp.append(blmc__ipn)
            if join_node.indicator_col_num == blmc__ipn:
                join_node.indicator_col_num = -1
                continue
            if blmc__ipn == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            oovd__ewrl, blmc__ipn = join_node.out_to_input_col_map[blmc__ipn]
            if oovd__ewrl == 'left':
                if (blmc__ipn not in join_node.left_key_set and blmc__ipn
                     not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(blmc__ipn)
                    if not join_node.is_left_table:
                        join_node.left_vars[blmc__ipn] = None
            elif oovd__ewrl == 'right':
                if (blmc__ipn not in join_node.right_key_set and blmc__ipn
                     not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(blmc__ipn)
                    if not join_node.is_right_table:
                        join_node.right_vars[blmc__ipn] = None
        for kucc__tefc in qym__uvyp:
            del join_node.out_to_input_col_map[kucc__tefc]
        if join_node.is_left_table:
            tkz__ent = set(range(join_node.n_left_table_cols))
            lfegx__hpi = not bool(tkz__ent - join_node.left_dead_var_inds)
            if lfegx__hpi:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            tkz__ent = set(range(join_node.n_right_table_cols))
            lfegx__hpi = not bool(tkz__ent - join_node.right_dead_var_inds)
            if lfegx__hpi:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        yjtd__mim = join_node.get_out_index_var()
        if yjtd__mim.name not in lives:
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
    gvxi__ikx = False
    if join_node.has_live_out_table_var:
        cmsbo__ofnce = join_node.get_out_table_var().name
        hmicy__ulesw, lsc__lgdy, ycf__frrx = get_live_column_nums_block(
            column_live_map, equiv_vars, cmsbo__ofnce)
        if not (lsc__lgdy or ycf__frrx):
            hmicy__ulesw = trim_extra_used_columns(hmicy__ulesw, join_node.
                n_out_table_cols)
            sbi__cppbn = join_node.get_out_table_used_cols()
            if len(hmicy__ulesw) != len(sbi__cppbn):
                gvxi__ikx = not (join_node.is_left_table and join_node.
                    is_right_table)
                kmqlq__blzj = sbi__cppbn - hmicy__ulesw
                join_node.out_used_cols = join_node.out_used_cols - kmqlq__blzj
    return gvxi__ikx


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        tsxd__kncqj = join_node.get_out_table_var()
        nkite__ptcu, lsc__lgdy, ycf__frrx = _compute_table_column_uses(
            tsxd__kncqj.name, table_col_use_map, equiv_vars)
    else:
        nkite__ptcu, lsc__lgdy, ycf__frrx = set(), False, False
    if join_node.has_live_left_table_var:
        xdtjg__jffaj = join_node.left_vars[0].name
        stu__foi, yanr__npqg, kgm__gsbm = block_use_map[xdtjg__jffaj]
        if not (yanr__npqg or kgm__gsbm):
            adcr__jlbt = set([join_node.out_to_input_col_map[kucc__tefc][1] for
                kucc__tefc in nkite__ptcu if join_node.out_to_input_col_map
                [kucc__tefc][0] == 'left'])
            ibhj__wzr = set(kucc__tefc for kucc__tefc in join_node.
                left_key_set | join_node.left_cond_cols if kucc__tefc <
                join_node.n_left_table_cols)
            if not (lsc__lgdy or ycf__frrx):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (adcr__jlbt | ibhj__wzr)
            block_use_map[xdtjg__jffaj] = (stu__foi | adcr__jlbt |
                ibhj__wzr, lsc__lgdy or ycf__frrx, False)
    if join_node.has_live_right_table_var:
        flxfi__hgrsn = join_node.right_vars[0].name
        stu__foi, yanr__npqg, kgm__gsbm = block_use_map[flxfi__hgrsn]
        if not (yanr__npqg or kgm__gsbm):
            jyoxp__gtr = set([join_node.out_to_input_col_map[kucc__tefc][1] for
                kucc__tefc in nkite__ptcu if join_node.out_to_input_col_map
                [kucc__tefc][0] == 'right'])
            owuob__laaaz = set(kucc__tefc for kucc__tefc in join_node.
                right_key_set | join_node.right_cond_cols if kucc__tefc <
                join_node.n_right_table_cols)
            if not (lsc__lgdy or ycf__frrx):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (jyoxp__gtr | owuob__laaaz)
            block_use_map[flxfi__hgrsn] = (stu__foi | jyoxp__gtr |
                owuob__laaaz, lsc__lgdy or ycf__frrx, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({cuxnd__kmfz.name for cuxnd__kmfz in join_node.
        get_live_left_vars()})
    use_set.update({cuxnd__kmfz.name for cuxnd__kmfz in join_node.
        get_live_right_vars()})
    def_set.update({cuxnd__kmfz.name for cuxnd__kmfz in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    opnfg__lfxvl = set(cuxnd__kmfz.name for cuxnd__kmfz in join_node.
        get_live_out_vars())
    return set(), opnfg__lfxvl


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(ugm__vva, var_dict) for
        ugm__vva in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(ugm__vva, var_dict) for
        ugm__vva in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(ugm__vva, var_dict
        ) for ugm__vva in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for walr__yfiuv in join_node.get_live_out_vars():
        definitions[walr__yfiuv.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        rim__cpdj = join_node.loc.strformat()
        hlas__arhhp = [join_node.left_col_names[kucc__tefc] for kucc__tefc in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        drut__xgdhp = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', drut__xgdhp,
            rim__cpdj, hlas__arhhp)
        beeoe__mqbij = [join_node.right_col_names[kucc__tefc] for
            kucc__tefc in sorted(set(range(len(join_node.right_col_names))) -
            join_node.right_dead_var_inds)]
        drut__xgdhp = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', drut__xgdhp,
            rim__cpdj, beeoe__mqbij)
        kdtc__vwmpa = [join_node.out_col_names[kucc__tefc] for kucc__tefc in
            sorted(join_node.get_out_table_used_cols())]
        drut__xgdhp = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', drut__xgdhp,
            rim__cpdj, kdtc__vwmpa)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    moh__iqpz = len(join_node.left_keys)
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
    ytkus__ejtw = 0
    wwsid__kpvk = 0
    usuee__roys = []
    for vcxb__sivzm in join_node.left_keys:
        mubd__pdu = join_node.left_var_map[vcxb__sivzm]
        if not join_node.is_left_table:
            usuee__roys.append(join_node.left_vars[mubd__pdu])
        eautz__lqx = 1
        ybc__ybbyo = join_node.left_to_output_map[mubd__pdu]
        if vcxb__sivzm == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == mubd__pdu):
                out_physical_to_logical_list.append(ybc__ybbyo)
                left_used_key_nums.add(mubd__pdu)
            else:
                eautz__lqx = 0
        elif ybc__ybbyo not in join_node.out_used_cols:
            eautz__lqx = 0
        elif mubd__pdu in left_used_key_nums:
            eautz__lqx = 0
        else:
            left_used_key_nums.add(mubd__pdu)
            out_physical_to_logical_list.append(ybc__ybbyo)
        left_physical_to_logical_list.append(mubd__pdu)
        left_logical_physical_map[mubd__pdu] = ytkus__ejtw
        ytkus__ejtw += 1
        left_key_in_output.append(eautz__lqx)
    usuee__roys = tuple(usuee__roys)
    osg__vsdbw = []
    for kucc__tefc in range(len(join_node.left_col_names)):
        if (kucc__tefc not in join_node.left_dead_var_inds and kucc__tefc
             not in join_node.left_key_set):
            if not join_node.is_left_table:
                cuxnd__kmfz = join_node.left_vars[kucc__tefc]
                osg__vsdbw.append(cuxnd__kmfz)
            pork__pzyzg = 1
            tkugo__wlmxb = 1
            ybc__ybbyo = join_node.left_to_output_map[kucc__tefc]
            if kucc__tefc in join_node.left_cond_cols:
                if ybc__ybbyo not in join_node.out_used_cols:
                    pork__pzyzg = 0
                left_key_in_output.append(pork__pzyzg)
            elif kucc__tefc in join_node.left_dead_var_inds:
                pork__pzyzg = 0
                tkugo__wlmxb = 0
            if pork__pzyzg:
                out_physical_to_logical_list.append(ybc__ybbyo)
            if tkugo__wlmxb:
                left_physical_to_logical_list.append(kucc__tefc)
                left_logical_physical_map[kucc__tefc] = ytkus__ejtw
                ytkus__ejtw += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            osg__vsdbw.append(join_node.left_vars[join_node.index_col_num])
        ybc__ybbyo = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(ybc__ybbyo)
        left_physical_to_logical_list.append(join_node.index_col_num)
    osg__vsdbw = tuple(osg__vsdbw)
    if join_node.is_left_table:
        osg__vsdbw = tuple(join_node.get_live_left_vars())
    qyrgu__goo = []
    for kucc__tefc, vcxb__sivzm in enumerate(join_node.right_keys):
        mubd__pdu = join_node.right_var_map[vcxb__sivzm]
        if not join_node.is_right_table:
            qyrgu__goo.append(join_node.right_vars[mubd__pdu])
        if not join_node.vect_same_key[kucc__tefc] and not join_node.is_join:
            eautz__lqx = 1
            if mubd__pdu not in join_node.right_to_output_map:
                eautz__lqx = 0
            else:
                ybc__ybbyo = join_node.right_to_output_map[mubd__pdu]
                if vcxb__sivzm == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        mubd__pdu):
                        out_physical_to_logical_list.append(ybc__ybbyo)
                        right_used_key_nums.add(mubd__pdu)
                    else:
                        eautz__lqx = 0
                elif ybc__ybbyo not in join_node.out_used_cols:
                    eautz__lqx = 0
                elif mubd__pdu in right_used_key_nums:
                    eautz__lqx = 0
                else:
                    right_used_key_nums.add(mubd__pdu)
                    out_physical_to_logical_list.append(ybc__ybbyo)
            right_key_in_output.append(eautz__lqx)
        right_physical_to_logical_list.append(mubd__pdu)
        right_logical_physical_map[mubd__pdu] = wwsid__kpvk
        wwsid__kpvk += 1
    qyrgu__goo = tuple(qyrgu__goo)
    imj__ghtc = []
    for kucc__tefc in range(len(join_node.right_col_names)):
        if (kucc__tefc not in join_node.right_dead_var_inds and kucc__tefc
             not in join_node.right_key_set):
            if not join_node.is_right_table:
                imj__ghtc.append(join_node.right_vars[kucc__tefc])
            pork__pzyzg = 1
            tkugo__wlmxb = 1
            ybc__ybbyo = join_node.right_to_output_map[kucc__tefc]
            if kucc__tefc in join_node.right_cond_cols:
                if ybc__ybbyo not in join_node.out_used_cols:
                    pork__pzyzg = 0
                right_key_in_output.append(pork__pzyzg)
            elif kucc__tefc in join_node.right_dead_var_inds:
                pork__pzyzg = 0
                tkugo__wlmxb = 0
            if pork__pzyzg:
                out_physical_to_logical_list.append(ybc__ybbyo)
            if tkugo__wlmxb:
                right_physical_to_logical_list.append(kucc__tefc)
                right_logical_physical_map[kucc__tefc] = wwsid__kpvk
                wwsid__kpvk += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            imj__ghtc.append(join_node.right_vars[join_node.index_col_num])
        ybc__ybbyo = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(ybc__ybbyo)
        right_physical_to_logical_list.append(join_node.index_col_num)
    imj__ghtc = tuple(imj__ghtc)
    if join_node.is_right_table:
        imj__ghtc = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    eok__wqyvs = usuee__roys + qyrgu__goo + osg__vsdbw + imj__ghtc
    scwuc__ennq = tuple(typemap[cuxnd__kmfz.name] for cuxnd__kmfz in eok__wqyvs
        )
    left_other_names = tuple('t1_c' + str(kucc__tefc) for kucc__tefc in
        range(len(osg__vsdbw)))
    right_other_names = tuple('t2_c' + str(kucc__tefc) for kucc__tefc in
        range(len(imj__ghtc)))
    if join_node.is_left_table:
        mqh__vxsrb = ()
    else:
        mqh__vxsrb = tuple('t1_key' + str(kucc__tefc) for kucc__tefc in
            range(moh__iqpz))
    if join_node.is_right_table:
        drsmu__fytdg = ()
    else:
        drsmu__fytdg = tuple('t2_key' + str(kucc__tefc) for kucc__tefc in
            range(moh__iqpz))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(mqh__vxsrb + drsmu__fytdg +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            fip__mxm = typemap[join_node.left_vars[0].name]
        else:
            fip__mxm = types.none
        for cdkm__xfqho in left_physical_to_logical_list:
            if cdkm__xfqho < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                qnotb__vveok = fip__mxm.arr_types[cdkm__xfqho]
            else:
                qnotb__vveok = typemap[join_node.left_vars[-1].name]
            if cdkm__xfqho in join_node.left_key_set:
                left_key_types.append(qnotb__vveok)
            else:
                left_other_types.append(qnotb__vveok)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[cuxnd__kmfz.name] for cuxnd__kmfz in
            usuee__roys)
        left_other_types = tuple([typemap[vcxb__sivzm.name] for vcxb__sivzm in
            osg__vsdbw])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            fip__mxm = typemap[join_node.right_vars[0].name]
        else:
            fip__mxm = types.none
        for cdkm__xfqho in right_physical_to_logical_list:
            if cdkm__xfqho < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                qnotb__vveok = fip__mxm.arr_types[cdkm__xfqho]
            else:
                qnotb__vveok = typemap[join_node.right_vars[-1].name]
            if cdkm__xfqho in join_node.right_key_set:
                right_key_types.append(qnotb__vveok)
            else:
                right_other_types.append(qnotb__vveok)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[cuxnd__kmfz.name] for cuxnd__kmfz in
            qyrgu__goo)
        right_other_types = tuple([typemap[vcxb__sivzm.name] for
            vcxb__sivzm in imj__ghtc])
    matched_key_types = []
    for kucc__tefc in range(moh__iqpz):
        azjgl__sckr = _match_join_key_types(left_key_types[kucc__tefc],
            right_key_types[kucc__tefc], loc)
        glbs[f'key_type_{kucc__tefc}'] = azjgl__sckr
        matched_key_types.append(azjgl__sckr)
    if join_node.is_left_table:
        qgavi__qlfv = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if qgavi__qlfv:
            xvrm__nvoze = False
            xlor__pyrbd = False
            vdbag__uhij = None
            if join_node.has_live_left_table_var:
                jyoyh__unjo = list(typemap[join_node.left_vars[0].name].
                    arr_types)
            else:
                jyoyh__unjo = None
            for blmc__ipn, qnotb__vveok in qgavi__qlfv.items():
                if blmc__ipn < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    jyoyh__unjo[blmc__ipn] = qnotb__vveok
                    xvrm__nvoze = True
                else:
                    vdbag__uhij = qnotb__vveok
                    xlor__pyrbd = True
            if xvrm__nvoze:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(jyoyh__unjo))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if xlor__pyrbd:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = vdbag__uhij
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({mqh__vxsrb[kucc__tefc]}, key_type_{kucc__tefc})'
             if left_key_types[kucc__tefc] != matched_key_types[kucc__tefc]
             else f'{mqh__vxsrb[kucc__tefc]}' for kucc__tefc in range(
            moh__iqpz)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        qgavi__qlfv = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if qgavi__qlfv:
            xvrm__nvoze = False
            xlor__pyrbd = False
            vdbag__uhij = None
            if join_node.has_live_right_table_var:
                jyoyh__unjo = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                jyoyh__unjo = None
            for blmc__ipn, qnotb__vveok in qgavi__qlfv.items():
                if blmc__ipn < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    jyoyh__unjo[blmc__ipn] = qnotb__vveok
                    xvrm__nvoze = True
                else:
                    vdbag__uhij = qnotb__vveok
                    xlor__pyrbd = True
            if xvrm__nvoze:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(jyoyh__unjo))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if xlor__pyrbd:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = vdbag__uhij
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({drsmu__fytdg[kucc__tefc]}, key_type_{kucc__tefc})'
             if right_key_types[kucc__tefc] != matched_key_types[kucc__tefc
            ] else f'{drsmu__fytdg[kucc__tefc]}' for kucc__tefc in range(
            moh__iqpz)))
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
        for kucc__tefc in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(kucc__tefc,
                kucc__tefc)
        for kucc__tefc in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(
                kucc__tefc, kucc__tefc)
        for kucc__tefc in range(moh__iqpz):
            func_text += (
                f'    t1_keys_{kucc__tefc} = out_t1_keys[{kucc__tefc}]\n')
        for kucc__tefc in range(moh__iqpz):
            func_text += (
                f'    t2_keys_{kucc__tefc} = out_t2_keys[{kucc__tefc}]\n')
    ybwvp__xqo = {}
    exec(func_text, {}, ybwvp__xqo)
    fqey__tgmef = ybwvp__xqo['f']
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
    hyl__vfsb = compile_to_numba_ir(fqey__tgmef, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=scwuc__ennq, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(hyl__vfsb, eok__wqyvs)
    rtexc__feq = hyl__vfsb.body[:-3]
    if join_node.has_live_out_index_var:
        rtexc__feq[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        rtexc__feq[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        rtexc__feq.pop(-1)
    elif not join_node.has_live_out_table_var:
        rtexc__feq.pop(-2)
    return rtexc__feq


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    uvj__hfyr = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{uvj__hfyr}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
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
    ybwvp__xqo = {}
    exec(func_text, table_getitem_funcs, ybwvp__xqo)
    agi__gtjk = ybwvp__xqo[f'bodo_join_gen_cond{uvj__hfyr}']
    sqt__bnl = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    dosa__lqxeq = numba.cfunc(sqt__bnl, nopython=True)(agi__gtjk)
    join_gen_cond_cfunc[dosa__lqxeq.native_name] = dosa__lqxeq
    join_gen_cond_cfunc_addr[dosa__lqxeq.native_name] = dosa__lqxeq.address
    return dosa__lqxeq, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    zbzj__noq = []
    for vcxb__sivzm, mdaqa__htkw in name_to_var_map.items():
        ttbd__cclo = f'({table_name}.{vcxb__sivzm})'
        if ttbd__cclo not in expr:
            continue
        aabch__dfo = f'getitem_{table_name}_val_{mdaqa__htkw}'
        yme__furs = f'_bodo_{table_name}_val_{mdaqa__htkw}'
        if is_table_var:
            kssmm__mva = typemap[col_vars[0].name].arr_types[mdaqa__htkw]
        else:
            kssmm__mva = typemap[col_vars[mdaqa__htkw].name]
        if is_str_arr_type(kssmm__mva) or kssmm__mva == bodo.binary_array_type:
            func_text += f"""  {yme__furs}, {yme__furs}_size = {aabch__dfo}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {yme__furs} = bodo.libs.str_arr_ext.decode_utf8({yme__furs}, {yme__furs}_size)
"""
        else:
            func_text += (
                f'  {yme__furs} = {aabch__dfo}({table_name}_data1, {table_name}_ind)\n'
                )
        lgh__pvyz = logical_to_physical_ind[mdaqa__htkw]
        table_getitem_funcs[aabch__dfo
            ] = bodo.libs.array._gen_row_access_intrinsic(kssmm__mva, lgh__pvyz
            )
        expr = expr.replace(ttbd__cclo, yme__furs)
        rfxc__ejpus = f'({na_check_name}.{table_name}.{vcxb__sivzm})'
        if rfxc__ejpus in expr:
            nmj__ntm = f'nacheck_{table_name}_val_{mdaqa__htkw}'
            teu__jcxlo = f'_bodo_isna_{table_name}_val_{mdaqa__htkw}'
            if isinstance(kssmm__mva, bodo.libs.int_arr_ext.IntegerArrayType
                ) or kssmm__mva in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(kssmm__mva):
                func_text += f"""  {teu__jcxlo} = {nmj__ntm}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += (
                    f'  {teu__jcxlo} = {nmj__ntm}({table_name}_data1, {table_name}_ind)\n'
                    )
            table_getitem_funcs[nmj__ntm
                ] = bodo.libs.array._gen_row_na_check_intrinsic(kssmm__mva,
                lgh__pvyz)
            expr = expr.replace(rfxc__ejpus, teu__jcxlo)
        if mdaqa__htkw not in key_set:
            zbzj__noq.append(lgh__pvyz)
    return expr, func_text, zbzj__noq


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as azuww__hclzz:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    xlr__hmvh = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[cuxnd__kmfz.name] in xlr__hmvh for
        cuxnd__kmfz in join_node.get_live_left_vars())
    right_parallel = all(array_dists[cuxnd__kmfz.name] in xlr__hmvh for
        cuxnd__kmfz in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[cuxnd__kmfz.name] in xlr__hmvh for
            cuxnd__kmfz in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[cuxnd__kmfz.name] in xlr__hmvh for
            cuxnd__kmfz in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[cuxnd__kmfz.name] in xlr__hmvh for
            cuxnd__kmfz in join_node.get_live_out_vars())
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
    kcpm__plras = set(left_col_nums)
    srkki__ytrqq = set(right_col_nums)
    dekzq__sghfe = join_node.vect_same_key
    wwkad__ofvg = []
    for kucc__tefc in range(len(left_key_types)):
        if left_key_in_output[kucc__tefc]:
            wwkad__ofvg.append(needs_typechange(matched_key_types[
                kucc__tefc], join_node.is_right, dekzq__sghfe[kucc__tefc]))
    mtjiz__bbh = len(left_key_types)
    pqw__kekgl = 0
    urxfy__cgfaq = left_physical_to_logical_list[len(left_key_types):]
    for kucc__tefc, cdkm__xfqho in enumerate(urxfy__cgfaq):
        trk__dyacb = True
        if cdkm__xfqho in kcpm__plras:
            trk__dyacb = left_key_in_output[mtjiz__bbh]
            mtjiz__bbh += 1
        if trk__dyacb:
            wwkad__ofvg.append(needs_typechange(left_other_types[kucc__tefc
                ], join_node.is_right, False))
    for kucc__tefc in range(len(right_key_types)):
        if not dekzq__sghfe[kucc__tefc] and not join_node.is_join:
            if right_key_in_output[pqw__kekgl]:
                wwkad__ofvg.append(needs_typechange(matched_key_types[
                    kucc__tefc], join_node.is_left, False))
            pqw__kekgl += 1
    gtu__djzak = right_physical_to_logical_list[len(right_key_types):]
    for kucc__tefc, cdkm__xfqho in enumerate(gtu__djzak):
        trk__dyacb = True
        if cdkm__xfqho in srkki__ytrqq:
            trk__dyacb = right_key_in_output[pqw__kekgl]
            pqw__kekgl += 1
        if trk__dyacb:
            wwkad__ofvg.append(needs_typechange(right_other_types[
                kucc__tefc], join_node.is_left, False))
    moh__iqpz = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            cjnav__lhf = left_other_names[1:]
            xjxx__ujp = left_other_names[0]
        else:
            cjnav__lhf = left_other_names
            xjxx__ujp = None
        mnkc__ygms = '()' if len(cjnav__lhf) == 0 else f'({cjnav__lhf[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({xjxx__ujp}, {mnkc__ygms}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        geh__vrq = []
        for kucc__tefc in range(moh__iqpz):
            geh__vrq.append('t1_keys[{}]'.format(kucc__tefc))
        for kucc__tefc in range(len(left_other_names)):
            geh__vrq.append('data_left[{}]'.format(kucc__tefc))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(opa__ijm) for opa__ijm in geh__vrq))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            cajs__yfwf = right_other_names[1:]
            xjxx__ujp = right_other_names[0]
        else:
            cajs__yfwf = right_other_names
            xjxx__ujp = None
        mnkc__ygms = '()' if len(cajs__yfwf) == 0 else f'({cajs__yfwf[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({xjxx__ujp}, {mnkc__ygms}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        bis__fbe = []
        for kucc__tefc in range(moh__iqpz):
            bis__fbe.append('t2_keys[{}]'.format(kucc__tefc))
        for kucc__tefc in range(len(right_other_names)):
            bis__fbe.append('data_right[{}]'.format(kucc__tefc))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(opa__ijm) for opa__ijm in bis__fbe))
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(dekzq__sghfe, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(wwkad__ofvg, dtype=np.int64)
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
        .format(left_parallel, right_parallel, moh__iqpz, len(urxfy__cgfaq),
        len(gtu__djzak), join_node.is_left, join_node.is_right, join_node.
        is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    qibp__rdwb = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {qibp__rdwb}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        iwuv__kxw = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{iwuv__kxw}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        qgavi__qlfv = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        qgavi__qlfv.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        xvrm__nvoze = False
        xlor__pyrbd = False
        if join_node.has_live_out_table_var:
            jyoyh__unjo = list(out_table_type.arr_types)
        else:
            jyoyh__unjo = None
        for blmc__ipn, qnotb__vveok in qgavi__qlfv.items():
            if blmc__ipn < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                jyoyh__unjo[blmc__ipn] = qnotb__vveok
                xvrm__nvoze = True
            else:
                vdbag__uhij = qnotb__vveok
                xlor__pyrbd = True
        if xvrm__nvoze:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            zvzh__zsfqe = bodo.TableType(tuple(jyoyh__unjo))
            glbs['py_table_type'] = zvzh__zsfqe
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if xlor__pyrbd:
            glbs['index_col_type'] = vdbag__uhij
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
    qgavi__qlfv: Dict[int, types.Type] = {}
    moh__iqpz = len(matched_key_types)
    for kucc__tefc in range(moh__iqpz):
        if used_key_nums is None or kucc__tefc in used_key_nums:
            if matched_key_types[kucc__tefc] != key_types[kucc__tefc] and (
                convert_dict_col or key_types[kucc__tefc] != bodo.
                dict_str_arr_type):
                if output_map:
                    iwuv__kxw = output_map[kucc__tefc]
                else:
                    iwuv__kxw = kucc__tefc
                qgavi__qlfv[iwuv__kxw] = matched_key_types[kucc__tefc]
    return qgavi__qlfv


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    ysiq__mdcyl = bodo.libs.distributed_api.get_size()
    iddkd__pnbo = np.empty(ysiq__mdcyl, left_key_arrs[0].dtype)
    xqvmi__tnd = np.empty(ysiq__mdcyl, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(iddkd__pnbo, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(xqvmi__tnd, left_key_arrs[0][-1])
    euivx__dbwre = np.zeros(ysiq__mdcyl, np.int32)
    jep__mgsrp = np.zeros(ysiq__mdcyl, np.int32)
    nqwtg__jwq = np.zeros(ysiq__mdcyl, np.int32)
    orr__fezko = right_key_arrs[0][0]
    bhoyc__ejhf = right_key_arrs[0][-1]
    zzcjy__exox = -1
    kucc__tefc = 0
    while kucc__tefc < ysiq__mdcyl - 1 and xqvmi__tnd[kucc__tefc] < orr__fezko:
        kucc__tefc += 1
    while kucc__tefc < ysiq__mdcyl and iddkd__pnbo[kucc__tefc] <= bhoyc__ejhf:
        zzcjy__exox, ulkh__gqv = _count_overlap(right_key_arrs[0],
            iddkd__pnbo[kucc__tefc], xqvmi__tnd[kucc__tefc])
        if zzcjy__exox != 0:
            zzcjy__exox -= 1
            ulkh__gqv += 1
        euivx__dbwre[kucc__tefc] = ulkh__gqv
        jep__mgsrp[kucc__tefc] = zzcjy__exox
        kucc__tefc += 1
    while kucc__tefc < ysiq__mdcyl:
        euivx__dbwre[kucc__tefc] = 1
        jep__mgsrp[kucc__tefc] = len(right_key_arrs[0]) - 1
        kucc__tefc += 1
    bodo.libs.distributed_api.alltoall(euivx__dbwre, nqwtg__jwq, 1)
    hnx__qcbol = nqwtg__jwq.sum()
    gkl__edq = np.empty(hnx__qcbol, right_key_arrs[0].dtype)
    iozs__rqpy = alloc_arr_tup(hnx__qcbol, right_data)
    why__slx = bodo.ir.join.calc_disp(nqwtg__jwq)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], gkl__edq,
        euivx__dbwre, nqwtg__jwq, jep__mgsrp, why__slx)
    bodo.libs.distributed_api.alltoallv_tup(right_data, iozs__rqpy,
        euivx__dbwre, nqwtg__jwq, jep__mgsrp, why__slx)
    return (gkl__edq,), iozs__rqpy


@numba.njit
def _count_overlap(r_key_arr, start, end):
    ulkh__gqv = 0
    zzcjy__exox = 0
    ebwm__hao = 0
    while ebwm__hao < len(r_key_arr) and r_key_arr[ebwm__hao] < start:
        zzcjy__exox += 1
        ebwm__hao += 1
    while ebwm__hao < len(r_key_arr) and start <= r_key_arr[ebwm__hao] <= end:
        ebwm__hao += 1
        ulkh__gqv += 1
    return zzcjy__exox, ulkh__gqv


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    ykv__iwblt = np.empty_like(arr)
    ykv__iwblt[0] = 0
    for kucc__tefc in range(1, len(arr)):
        ykv__iwblt[kucc__tefc] = ykv__iwblt[kucc__tefc - 1] + arr[
            kucc__tefc - 1]
    return ykv__iwblt


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    eiopz__empq = len(left_keys[0])
    ucrng__ihra = len(right_keys[0])
    mxuz__bszbe = alloc_arr_tup(eiopz__empq, left_keys)
    opimm__khqzs = alloc_arr_tup(eiopz__empq, right_keys)
    whjt__vdi = alloc_arr_tup(eiopz__empq, data_left)
    hbwnr__aoqq = alloc_arr_tup(eiopz__empq, data_right)
    aaqpj__woowq = 0
    bef__aiwq = 0
    for aaqpj__woowq in range(eiopz__empq):
        if bef__aiwq < 0:
            bef__aiwq = 0
        while bef__aiwq < ucrng__ihra and getitem_arr_tup(right_keys, bef__aiwq
            ) <= getitem_arr_tup(left_keys, aaqpj__woowq):
            bef__aiwq += 1
        bef__aiwq -= 1
        setitem_arr_tup(mxuz__bszbe, aaqpj__woowq, getitem_arr_tup(
            left_keys, aaqpj__woowq))
        setitem_arr_tup(whjt__vdi, aaqpj__woowq, getitem_arr_tup(data_left,
            aaqpj__woowq))
        if bef__aiwq >= 0:
            setitem_arr_tup(opimm__khqzs, aaqpj__woowq, getitem_arr_tup(
                right_keys, bef__aiwq))
            setitem_arr_tup(hbwnr__aoqq, aaqpj__woowq, getitem_arr_tup(
                data_right, bef__aiwq))
        else:
            bodo.libs.array_kernels.setna_tup(opimm__khqzs, aaqpj__woowq)
            bodo.libs.array_kernels.setna_tup(hbwnr__aoqq, aaqpj__woowq)
    return mxuz__bszbe, opimm__khqzs, whjt__vdi, hbwnr__aoqq
