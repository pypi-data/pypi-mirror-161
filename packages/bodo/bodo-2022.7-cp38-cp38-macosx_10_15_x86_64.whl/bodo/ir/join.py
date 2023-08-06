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
        xtj__jqot = func.signature
        ojte__ljhfw = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        asenm__oxgk = cgutils.get_or_insert_function(builder.module,
            ojte__ljhfw, sym._literal_value)
        builder.call(asenm__oxgk, [context.get_constant_null(xtj__jqot.args
            [0]), context.get_constant_null(xtj__jqot.args[1]), context.
            get_constant_null(xtj__jqot.args[2]), context.get_constant_null
            (xtj__jqot.args[3]), context.get_constant_null(xtj__jqot.args[4
            ]), context.get_constant_null(xtj__jqot.args[5]), context.
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
        dpeht__jfwoi = left_df_type.columns
        djcyd__qbtqt = right_df_type.columns
        self.left_col_names = dpeht__jfwoi
        self.right_col_names = djcyd__qbtqt
        self.is_left_table = left_df_type.is_table_format
        self.is_right_table = right_df_type.is_table_format
        self.n_left_table_cols = len(dpeht__jfwoi) if self.is_left_table else 0
        self.n_right_table_cols = len(djcyd__qbtqt
            ) if self.is_right_table else 0
        qizzh__mhx = self.n_left_table_cols if self.is_left_table else len(
            left_vars) - 1
        buviu__dmw = self.n_right_table_cols if self.is_right_table else len(
            right_vars) - 1
        self.left_dead_var_inds = set()
        self.right_dead_var_inds = set()
        if self.left_vars[-1] is None:
            self.left_dead_var_inds.add(qizzh__mhx)
        if self.right_vars[-1] is None:
            self.right_dead_var_inds.add(buviu__dmw)
        self.left_var_map = {zze__ejjed: mce__hptj for mce__hptj,
            zze__ejjed in enumerate(dpeht__jfwoi)}
        self.right_var_map = {zze__ejjed: mce__hptj for mce__hptj,
            zze__ejjed in enumerate(djcyd__qbtqt)}
        if self.left_vars[-1] is not None:
            self.left_var_map[INDEX_SENTINEL] = qizzh__mhx
        if self.right_vars[-1] is not None:
            self.right_var_map[INDEX_SENTINEL] = buviu__dmw
        self.left_key_set = set(self.left_var_map[zze__ejjed] for
            zze__ejjed in left_keys)
        self.right_key_set = set(self.right_var_map[zze__ejjed] for
            zze__ejjed in right_keys)
        if gen_cond_expr:
            self.left_cond_cols = set(self.left_var_map[zze__ejjed] for
                zze__ejjed in dpeht__jfwoi if f'(left.{zze__ejjed})' in
                gen_cond_expr)
            self.right_cond_cols = set(self.right_var_map[zze__ejjed] for
                zze__ejjed in djcyd__qbtqt if f'(right.{zze__ejjed})' in
                gen_cond_expr)
        else:
            self.left_cond_cols = set()
            self.right_cond_cols = set()
        wuz__vlrw: int = -1
        nwf__aqdy = set(left_keys) & set(right_keys)
        xhl__lgm = set(dpeht__jfwoi) & set(djcyd__qbtqt)
        yayu__fyvl = xhl__lgm - nwf__aqdy
        amtf__hdru: Dict[int, (Literal['left', 'right'], int)] = {}
        pelw__shodn: Dict[int, int] = {}
        yewp__ydraw: Dict[int, int] = {}
        for mce__hptj, zze__ejjed in enumerate(dpeht__jfwoi):
            if zze__ejjed in yayu__fyvl:
                zwxgk__onmf = str(zze__ejjed) + suffix_left
                rxvpk__uicw = out_df_type.column_index[zwxgk__onmf]
                if (right_index and not left_index and mce__hptj in self.
                    left_key_set):
                    wuz__vlrw = out_df_type.column_index[zze__ejjed]
                    amtf__hdru[wuz__vlrw] = 'left', mce__hptj
            else:
                rxvpk__uicw = out_df_type.column_index[zze__ejjed]
            amtf__hdru[rxvpk__uicw] = 'left', mce__hptj
            pelw__shodn[mce__hptj] = rxvpk__uicw
        for mce__hptj, zze__ejjed in enumerate(djcyd__qbtqt):
            if zze__ejjed not in nwf__aqdy:
                if zze__ejjed in yayu__fyvl:
                    vfwa__lto = str(zze__ejjed) + suffix_right
                    rxvpk__uicw = out_df_type.column_index[vfwa__lto]
                    if (left_index and not right_index and mce__hptj in
                        self.right_key_set):
                        wuz__vlrw = out_df_type.column_index[zze__ejjed]
                        amtf__hdru[wuz__vlrw] = 'right', mce__hptj
                else:
                    rxvpk__uicw = out_df_type.column_index[zze__ejjed]
                amtf__hdru[rxvpk__uicw] = 'right', mce__hptj
                yewp__ydraw[mce__hptj] = rxvpk__uicw
        if self.left_vars[-1] is not None:
            pelw__shodn[qizzh__mhx] = self.n_out_table_cols
        if self.right_vars[-1] is not None:
            yewp__ydraw[buviu__dmw] = self.n_out_table_cols
        self.out_to_input_col_map = amtf__hdru
        self.left_to_output_map = pelw__shodn
        self.right_to_output_map = yewp__ydraw
        self.extra_data_col_num = wuz__vlrw
        if len(out_data_vars) > 1:
            sqdbx__jebsc = 'left' if right_index else 'right'
            if sqdbx__jebsc == 'left':
                hfb__gzeaf = qizzh__mhx
            elif sqdbx__jebsc == 'right':
                hfb__gzeaf = buviu__dmw
        else:
            sqdbx__jebsc = None
            hfb__gzeaf = -1
        self.index_source = sqdbx__jebsc
        self.index_col_num = hfb__gzeaf
        fpyj__odg = []
        enteh__htbvy = len(left_keys)
        for ioxu__vmkjy in range(enteh__htbvy):
            fabhh__abh = left_keys[ioxu__vmkjy]
            wvw__ort = right_keys[ioxu__vmkjy]
            fpyj__odg.append(fabhh__abh == wvw__ort)
        self.vect_same_key = fpyj__odg

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
        for cwoo__ijd in self.left_vars:
            if cwoo__ijd is not None:
                vars.append(cwoo__ijd)
        return vars

    def get_live_right_vars(self):
        vars = []
        for cwoo__ijd in self.right_vars:
            if cwoo__ijd is not None:
                vars.append(cwoo__ijd)
        return vars

    def get_live_out_vars(self):
        vars = []
        for cwoo__ijd in self.out_data_vars:
            if cwoo__ijd is not None:
                vars.append(cwoo__ijd)
        return vars

    def set_live_left_vars(self, live_data_vars):
        left_vars = []
        ixlam__dwvrx = 0
        start = 0
        if self.is_left_table:
            if self.has_live_left_table_var:
                left_vars.append(live_data_vars[ixlam__dwvrx])
                ixlam__dwvrx += 1
            else:
                left_vars.append(None)
            start = 1
        lomti__jep = max(self.n_left_table_cols - 1, 0)
        for mce__hptj in range(start, len(self.left_vars)):
            if mce__hptj + lomti__jep in self.left_dead_var_inds:
                left_vars.append(None)
            else:
                left_vars.append(live_data_vars[ixlam__dwvrx])
                ixlam__dwvrx += 1
        self.left_vars = left_vars

    def set_live_right_vars(self, live_data_vars):
        right_vars = []
        ixlam__dwvrx = 0
        start = 0
        if self.is_right_table:
            if self.has_live_right_table_var:
                right_vars.append(live_data_vars[ixlam__dwvrx])
                ixlam__dwvrx += 1
            else:
                right_vars.append(None)
            start = 1
        lomti__jep = max(self.n_right_table_cols - 1, 0)
        for mce__hptj in range(start, len(self.right_vars)):
            if mce__hptj + lomti__jep in self.right_dead_var_inds:
                right_vars.append(None)
            else:
                right_vars.append(live_data_vars[ixlam__dwvrx])
                ixlam__dwvrx += 1
        self.right_vars = right_vars

    def set_live_out_data_vars(self, live_data_vars):
        out_data_vars = []
        sahsw__vxw = [self.has_live_out_table_var, self.has_live_out_index_var]
        ixlam__dwvrx = 0
        for mce__hptj in range(len(self.out_data_vars)):
            if not sahsw__vxw[mce__hptj]:
                out_data_vars.append(None)
            else:
                out_data_vars.append(live_data_vars[ixlam__dwvrx])
                ixlam__dwvrx += 1
        self.out_data_vars = out_data_vars

    def get_out_table_used_cols(self):
        return {mce__hptj for mce__hptj in self.out_used_cols if mce__hptj <
            self.n_out_table_cols}

    def __repr__(self):
        grfpj__ytow = ', '.join([f'{zze__ejjed}' for zze__ejjed in self.
            left_col_names])
        ubd__gxqk = f'left={{{grfpj__ytow}}}'
        grfpj__ytow = ', '.join([f'{zze__ejjed}' for zze__ejjed in self.
            right_col_names])
        cvnhc__oqh = f'right={{{grfpj__ytow}}}'
        return 'join [{}={}]: {}, {}'.format(self.left_keys, self.
            right_keys, ubd__gxqk, cvnhc__oqh)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    okb__cfb = []
    assert len(join_node.get_live_out_vars()
        ) > 0, 'empty join in array analysis'
    fgcn__qqbiu = []
    aqi__brmxf = join_node.get_live_left_vars()
    for jxxsc__hxefo in aqi__brmxf:
        tfo__ckov = typemap[jxxsc__hxefo.name]
        fxd__wdn = equiv_set.get_shape(jxxsc__hxefo)
        if fxd__wdn:
            fgcn__qqbiu.append(fxd__wdn[0])
    if len(fgcn__qqbiu) > 1:
        equiv_set.insert_equiv(*fgcn__qqbiu)
    fgcn__qqbiu = []
    aqi__brmxf = list(join_node.get_live_right_vars())
    for jxxsc__hxefo in aqi__brmxf:
        tfo__ckov = typemap[jxxsc__hxefo.name]
        fxd__wdn = equiv_set.get_shape(jxxsc__hxefo)
        if fxd__wdn:
            fgcn__qqbiu.append(fxd__wdn[0])
    if len(fgcn__qqbiu) > 1:
        equiv_set.insert_equiv(*fgcn__qqbiu)
    fgcn__qqbiu = []
    for ioot__gfp in join_node.get_live_out_vars():
        tfo__ckov = typemap[ioot__gfp.name]
        epv__mtun = array_analysis._gen_shape_call(equiv_set, ioot__gfp,
            tfo__ckov.ndim, None, okb__cfb)
        equiv_set.insert_equiv(ioot__gfp, epv__mtun)
        fgcn__qqbiu.append(epv__mtun[0])
        equiv_set.define(ioot__gfp, set())
    if len(fgcn__qqbiu) > 1:
        equiv_set.insert_equiv(*fgcn__qqbiu)
    return [], okb__cfb


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    ajpmx__xfsvh = Distribution.OneD
    mub__drya = Distribution.OneD
    for jxxsc__hxefo in join_node.get_live_left_vars():
        ajpmx__xfsvh = Distribution(min(ajpmx__xfsvh.value, array_dists[
            jxxsc__hxefo.name].value))
    for jxxsc__hxefo in join_node.get_live_right_vars():
        mub__drya = Distribution(min(mub__drya.value, array_dists[
            jxxsc__hxefo.name].value))
    eezh__lkj = Distribution.OneD_Var
    for ioot__gfp in join_node.get_live_out_vars():
        if ioot__gfp.name in array_dists:
            eezh__lkj = Distribution(min(eezh__lkj.value, array_dists[
                ioot__gfp.name].value))
    gin__llx = Distribution(min(eezh__lkj.value, ajpmx__xfsvh.value))
    avv__cbo = Distribution(min(eezh__lkj.value, mub__drya.value))
    eezh__lkj = Distribution(max(gin__llx.value, avv__cbo.value))
    for ioot__gfp in join_node.get_live_out_vars():
        array_dists[ioot__gfp.name] = eezh__lkj
    if eezh__lkj != Distribution.OneD_Var:
        ajpmx__xfsvh = eezh__lkj
        mub__drya = eezh__lkj
    for jxxsc__hxefo in join_node.get_live_left_vars():
        array_dists[jxxsc__hxefo.name] = ajpmx__xfsvh
    for jxxsc__hxefo in join_node.get_live_right_vars():
        array_dists[jxxsc__hxefo.name] = mub__drya
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def visit_vars_join(join_node, callback, cbdata):
    join_node.set_live_left_vars([visit_vars_inner(cwoo__ijd, callback,
        cbdata) for cwoo__ijd in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([visit_vars_inner(cwoo__ijd, callback,
        cbdata) for cwoo__ijd in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([visit_vars_inner(cwoo__ijd, callback,
        cbdata) for cwoo__ijd in join_node.get_live_out_vars()])


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if join_node.has_live_out_table_var:
        tvaou__szb = []
        jopmc__crsy = join_node.get_out_table_var()
        if jopmc__crsy.name not in lives:
            join_node.out_data_vars[0] = None
            join_node.out_used_cols.difference_update(join_node.
                get_out_table_used_cols())
        for cjlzd__mol in join_node.out_to_input_col_map.keys():
            if cjlzd__mol in join_node.out_used_cols:
                continue
            tvaou__szb.append(cjlzd__mol)
            if join_node.indicator_col_num == cjlzd__mol:
                join_node.indicator_col_num = -1
                continue
            if cjlzd__mol == join_node.extra_data_col_num:
                join_node.extra_data_col_num = -1
                continue
            vvvc__hysf, cjlzd__mol = join_node.out_to_input_col_map[cjlzd__mol]
            if vvvc__hysf == 'left':
                if (cjlzd__mol not in join_node.left_key_set and cjlzd__mol
                     not in join_node.left_cond_cols):
                    join_node.left_dead_var_inds.add(cjlzd__mol)
                    if not join_node.is_left_table:
                        join_node.left_vars[cjlzd__mol] = None
            elif vvvc__hysf == 'right':
                if (cjlzd__mol not in join_node.right_key_set and 
                    cjlzd__mol not in join_node.right_cond_cols):
                    join_node.right_dead_var_inds.add(cjlzd__mol)
                    if not join_node.is_right_table:
                        join_node.right_vars[cjlzd__mol] = None
        for mce__hptj in tvaou__szb:
            del join_node.out_to_input_col_map[mce__hptj]
        if join_node.is_left_table:
            iikc__cvfx = set(range(join_node.n_left_table_cols))
            meg__uth = not bool(iikc__cvfx - join_node.left_dead_var_inds)
            if meg__uth:
                join_node.left_vars[0] = None
        if join_node.is_right_table:
            iikc__cvfx = set(range(join_node.n_right_table_cols))
            meg__uth = not bool(iikc__cvfx - join_node.right_dead_var_inds)
            if meg__uth:
                join_node.right_vars[0] = None
    if join_node.has_live_out_index_var:
        hurs__dwtsy = join_node.get_out_index_var()
        if hurs__dwtsy.name not in lives:
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
    jssyq__wqhxo = False
    if join_node.has_live_out_table_var:
        khk__mbays = join_node.get_out_table_var().name
        ntkuz__jrehh, zcu__abzl, ukkb__uhx = get_live_column_nums_block(
            column_live_map, equiv_vars, khk__mbays)
        if not (zcu__abzl or ukkb__uhx):
            ntkuz__jrehh = trim_extra_used_columns(ntkuz__jrehh, join_node.
                n_out_table_cols)
            neyo__gszn = join_node.get_out_table_used_cols()
            if len(ntkuz__jrehh) != len(neyo__gszn):
                jssyq__wqhxo = not (join_node.is_left_table and join_node.
                    is_right_table)
                ayuu__dnlx = neyo__gszn - ntkuz__jrehh
                join_node.out_used_cols = join_node.out_used_cols - ayuu__dnlx
    return jssyq__wqhxo


remove_dead_column_extensions[Join] = join_remove_dead_column


def join_table_column_use(join_node: Join, block_use_map: Dict[str, Tuple[
    Set[int], bool, bool]], equiv_vars: Dict[str, Set[str]], typemap: Dict[
    str, types.Type], table_col_use_map: Dict[int, Dict[str, Tuple[Set[int],
    bool, bool]]]):
    if not (join_node.is_left_table or join_node.is_right_table):
        return
    if join_node.has_live_out_table_var:
        wbufc__qkgi = join_node.get_out_table_var()
        mgxr__ciwht, zcu__abzl, ukkb__uhx = _compute_table_column_uses(
            wbufc__qkgi.name, table_col_use_map, equiv_vars)
    else:
        mgxr__ciwht, zcu__abzl, ukkb__uhx = set(), False, False
    if join_node.has_live_left_table_var:
        nrwyx__ytdaw = join_node.left_vars[0].name
        qfh__isl, veuko__owpip, nqjak__bgu = block_use_map[nrwyx__ytdaw]
        if not (veuko__owpip or nqjak__bgu):
            busp__anrd = set([join_node.out_to_input_col_map[mce__hptj][1] for
                mce__hptj in mgxr__ciwht if join_node.out_to_input_col_map[
                mce__hptj][0] == 'left'])
            dbx__svzgp = set(mce__hptj for mce__hptj in join_node.
                left_key_set | join_node.left_cond_cols if mce__hptj <
                join_node.n_left_table_cols)
            if not (zcu__abzl or ukkb__uhx):
                join_node.left_dead_var_inds |= set(range(join_node.
                    n_left_table_cols)) - (busp__anrd | dbx__svzgp)
            block_use_map[nrwyx__ytdaw] = (qfh__isl | busp__anrd |
                dbx__svzgp, zcu__abzl or ukkb__uhx, False)
    if join_node.has_live_right_table_var:
        jnq__svpak = join_node.right_vars[0].name
        qfh__isl, veuko__owpip, nqjak__bgu = block_use_map[jnq__svpak]
        if not (veuko__owpip or nqjak__bgu):
            qkpx__vkp = set([join_node.out_to_input_col_map[mce__hptj][1] for
                mce__hptj in mgxr__ciwht if join_node.out_to_input_col_map[
                mce__hptj][0] == 'right'])
            pmzue__eqmc = set(mce__hptj for mce__hptj in join_node.
                right_key_set | join_node.right_cond_cols if mce__hptj <
                join_node.n_right_table_cols)
            if not (zcu__abzl or ukkb__uhx):
                join_node.right_dead_var_inds |= set(range(join_node.
                    n_right_table_cols)) - (qkpx__vkp | pmzue__eqmc)
            block_use_map[jnq__svpak] = (qfh__isl | qkpx__vkp | pmzue__eqmc,
                zcu__abzl or ukkb__uhx, False)


ir_extension_table_column_use[Join] = join_table_column_use


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({jiarb__ztg.name for jiarb__ztg in join_node.
        get_live_left_vars()})
    use_set.update({jiarb__ztg.name for jiarb__ztg in join_node.
        get_live_right_vars()})
    def_set.update({jiarb__ztg.name for jiarb__ztg in join_node.
        get_live_out_vars()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    kapyk__szwbv = set(jiarb__ztg.name for jiarb__ztg in join_node.
        get_live_out_vars())
    return set(), kapyk__szwbv


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    join_node.set_live_left_vars([replace_vars_inner(cwoo__ijd, var_dict) for
        cwoo__ijd in join_node.get_live_left_vars()])
    join_node.set_live_right_vars([replace_vars_inner(cwoo__ijd, var_dict) for
        cwoo__ijd in join_node.get_live_right_vars()])
    join_node.set_live_out_data_vars([replace_vars_inner(cwoo__ijd,
        var_dict) for cwoo__ijd in join_node.get_live_out_vars()])


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for jxxsc__hxefo in join_node.get_live_out_vars():
        definitions[jxxsc__hxefo.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 2:
        aaho__bexhn = join_node.loc.strformat()
        bzoh__evo = [join_node.left_col_names[mce__hptj] for mce__hptj in
            sorted(set(range(len(join_node.left_col_names))) - join_node.
            left_dead_var_inds)]
        nnzct__loruu = """Finished column elimination on join's left input:
%s
Left input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', nnzct__loruu,
            aaho__bexhn, bzoh__evo)
        zup__fzyd = [join_node.right_col_names[mce__hptj] for mce__hptj in
            sorted(set(range(len(join_node.right_col_names))) - join_node.
            right_dead_var_inds)]
        nnzct__loruu = """Finished column elimination on join's right input:
%s
Right input columns: %s
"""
        bodo.user_logging.log_message('Column Pruning', nnzct__loruu,
            aaho__bexhn, zup__fzyd)
        sjhc__znqp = [join_node.out_col_names[mce__hptj] for mce__hptj in
            sorted(join_node.get_out_table_used_cols())]
        nnzct__loruu = (
            'Finished column pruning on join node:\n%s\nOutput columns: %s\n')
        bodo.user_logging.log_message('Column Pruning', nnzct__loruu,
            aaho__bexhn, sjhc__znqp)
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    enteh__htbvy = len(join_node.left_keys)
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
    slmy__ucj = 0
    yro__mtpf = 0
    moetr__gjomd = []
    for zze__ejjed in join_node.left_keys:
        vxs__rrie = join_node.left_var_map[zze__ejjed]
        if not join_node.is_left_table:
            moetr__gjomd.append(join_node.left_vars[vxs__rrie])
        sahsw__vxw = 1
        rxvpk__uicw = join_node.left_to_output_map[vxs__rrie]
        if zze__ejjed == INDEX_SENTINEL:
            if (join_node.has_live_out_index_var and join_node.index_source ==
                'left' and join_node.index_col_num == vxs__rrie):
                out_physical_to_logical_list.append(rxvpk__uicw)
                left_used_key_nums.add(vxs__rrie)
            else:
                sahsw__vxw = 0
        elif rxvpk__uicw not in join_node.out_used_cols:
            sahsw__vxw = 0
        elif vxs__rrie in left_used_key_nums:
            sahsw__vxw = 0
        else:
            left_used_key_nums.add(vxs__rrie)
            out_physical_to_logical_list.append(rxvpk__uicw)
        left_physical_to_logical_list.append(vxs__rrie)
        left_logical_physical_map[vxs__rrie] = slmy__ucj
        slmy__ucj += 1
        left_key_in_output.append(sahsw__vxw)
    moetr__gjomd = tuple(moetr__gjomd)
    vhx__bng = []
    for mce__hptj in range(len(join_node.left_col_names)):
        if (mce__hptj not in join_node.left_dead_var_inds and mce__hptj not in
            join_node.left_key_set):
            if not join_node.is_left_table:
                jiarb__ztg = join_node.left_vars[mce__hptj]
                vhx__bng.append(jiarb__ztg)
            bgw__xhq = 1
            urgsh__jvalq = 1
            rxvpk__uicw = join_node.left_to_output_map[mce__hptj]
            if mce__hptj in join_node.left_cond_cols:
                if rxvpk__uicw not in join_node.out_used_cols:
                    bgw__xhq = 0
                left_key_in_output.append(bgw__xhq)
            elif mce__hptj in join_node.left_dead_var_inds:
                bgw__xhq = 0
                urgsh__jvalq = 0
            if bgw__xhq:
                out_physical_to_logical_list.append(rxvpk__uicw)
            if urgsh__jvalq:
                left_physical_to_logical_list.append(mce__hptj)
                left_logical_physical_map[mce__hptj] = slmy__ucj
                slmy__ucj += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'left' and join_node.index_col_num not in join_node.left_key_set):
        if not join_node.is_left_table:
            vhx__bng.append(join_node.left_vars[join_node.index_col_num])
        rxvpk__uicw = join_node.left_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(rxvpk__uicw)
        left_physical_to_logical_list.append(join_node.index_col_num)
    vhx__bng = tuple(vhx__bng)
    if join_node.is_left_table:
        vhx__bng = tuple(join_node.get_live_left_vars())
    ttk__vbx = []
    for mce__hptj, zze__ejjed in enumerate(join_node.right_keys):
        vxs__rrie = join_node.right_var_map[zze__ejjed]
        if not join_node.is_right_table:
            ttk__vbx.append(join_node.right_vars[vxs__rrie])
        if not join_node.vect_same_key[mce__hptj] and not join_node.is_join:
            sahsw__vxw = 1
            if vxs__rrie not in join_node.right_to_output_map:
                sahsw__vxw = 0
            else:
                rxvpk__uicw = join_node.right_to_output_map[vxs__rrie]
                if zze__ejjed == INDEX_SENTINEL:
                    if (join_node.has_live_out_index_var and join_node.
                        index_source == 'right' and join_node.index_col_num ==
                        vxs__rrie):
                        out_physical_to_logical_list.append(rxvpk__uicw)
                        right_used_key_nums.add(vxs__rrie)
                    else:
                        sahsw__vxw = 0
                elif rxvpk__uicw not in join_node.out_used_cols:
                    sahsw__vxw = 0
                elif vxs__rrie in right_used_key_nums:
                    sahsw__vxw = 0
                else:
                    right_used_key_nums.add(vxs__rrie)
                    out_physical_to_logical_list.append(rxvpk__uicw)
            right_key_in_output.append(sahsw__vxw)
        right_physical_to_logical_list.append(vxs__rrie)
        right_logical_physical_map[vxs__rrie] = yro__mtpf
        yro__mtpf += 1
    ttk__vbx = tuple(ttk__vbx)
    rvddl__gvqf = []
    for mce__hptj in range(len(join_node.right_col_names)):
        if (mce__hptj not in join_node.right_dead_var_inds and mce__hptj not in
            join_node.right_key_set):
            if not join_node.is_right_table:
                rvddl__gvqf.append(join_node.right_vars[mce__hptj])
            bgw__xhq = 1
            urgsh__jvalq = 1
            rxvpk__uicw = join_node.right_to_output_map[mce__hptj]
            if mce__hptj in join_node.right_cond_cols:
                if rxvpk__uicw not in join_node.out_used_cols:
                    bgw__xhq = 0
                right_key_in_output.append(bgw__xhq)
            elif mce__hptj in join_node.right_dead_var_inds:
                bgw__xhq = 0
                urgsh__jvalq = 0
            if bgw__xhq:
                out_physical_to_logical_list.append(rxvpk__uicw)
            if urgsh__jvalq:
                right_physical_to_logical_list.append(mce__hptj)
                right_logical_physical_map[mce__hptj] = yro__mtpf
                yro__mtpf += 1
    if (join_node.has_live_out_index_var and join_node.index_source ==
        'right' and join_node.index_col_num not in join_node.right_key_set):
        if not join_node.is_right_table:
            rvddl__gvqf.append(join_node.right_vars[join_node.index_col_num])
        rxvpk__uicw = join_node.right_to_output_map[join_node.index_col_num]
        out_physical_to_logical_list.append(rxvpk__uicw)
        right_physical_to_logical_list.append(join_node.index_col_num)
    rvddl__gvqf = tuple(rvddl__gvqf)
    if join_node.is_right_table:
        rvddl__gvqf = tuple(join_node.get_live_right_vars())
    if join_node.indicator_col_num != -1:
        out_physical_to_logical_list.append(join_node.indicator_col_num)
    ziv__qhap = moetr__gjomd + ttk__vbx + vhx__bng + rvddl__gvqf
    wftib__cwqun = tuple(typemap[jiarb__ztg.name] for jiarb__ztg in ziv__qhap)
    left_other_names = tuple('t1_c' + str(mce__hptj) for mce__hptj in range
        (len(vhx__bng)))
    right_other_names = tuple('t2_c' + str(mce__hptj) for mce__hptj in
        range(len(rvddl__gvqf)))
    if join_node.is_left_table:
        bgff__plmkw = ()
    else:
        bgff__plmkw = tuple('t1_key' + str(mce__hptj) for mce__hptj in
            range(enteh__htbvy))
    if join_node.is_right_table:
        jrusr__vtl = ()
    else:
        jrusr__vtl = tuple('t2_key' + str(mce__hptj) for mce__hptj in range
            (enteh__htbvy))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}):\n'.format(','.join(bgff__plmkw + jrusr__vtl +
        left_other_names + right_other_names))
    if join_node.is_left_table:
        left_key_types = []
        left_other_types = []
        if join_node.has_live_left_table_var:
            gbm__aku = typemap[join_node.left_vars[0].name]
        else:
            gbm__aku = types.none
        for lpund__mtq in left_physical_to_logical_list:
            if lpund__mtq < join_node.n_left_table_cols:
                assert join_node.has_live_left_table_var, 'No logical columns should refer to a dead table'
                tfo__ckov = gbm__aku.arr_types[lpund__mtq]
            else:
                tfo__ckov = typemap[join_node.left_vars[-1].name]
            if lpund__mtq in join_node.left_key_set:
                left_key_types.append(tfo__ckov)
            else:
                left_other_types.append(tfo__ckov)
        left_key_types = tuple(left_key_types)
        left_other_types = tuple(left_other_types)
    else:
        left_key_types = tuple(typemap[jiarb__ztg.name] for jiarb__ztg in
            moetr__gjomd)
        left_other_types = tuple([typemap[zze__ejjed.name] for zze__ejjed in
            vhx__bng])
    if join_node.is_right_table:
        right_key_types = []
        right_other_types = []
        if join_node.has_live_right_table_var:
            gbm__aku = typemap[join_node.right_vars[0].name]
        else:
            gbm__aku = types.none
        for lpund__mtq in right_physical_to_logical_list:
            if lpund__mtq < join_node.n_right_table_cols:
                assert join_node.has_live_right_table_var, 'No logical columns should refer to a dead table'
                tfo__ckov = gbm__aku.arr_types[lpund__mtq]
            else:
                tfo__ckov = typemap[join_node.right_vars[-1].name]
            if lpund__mtq in join_node.right_key_set:
                right_key_types.append(tfo__ckov)
            else:
                right_other_types.append(tfo__ckov)
        right_key_types = tuple(right_key_types)
        right_other_types = tuple(right_other_types)
    else:
        right_key_types = tuple(typemap[jiarb__ztg.name] for jiarb__ztg in
            ttk__vbx)
        right_other_types = tuple([typemap[zze__ejjed.name] for zze__ejjed in
            rvddl__gvqf])
    matched_key_types = []
    for mce__hptj in range(enteh__htbvy):
        jyph__hmgt = _match_join_key_types(left_key_types[mce__hptj],
            right_key_types[mce__hptj], loc)
        glbs[f'key_type_{mce__hptj}'] = jyph__hmgt
        matched_key_types.append(jyph__hmgt)
    if join_node.is_left_table:
        sqngd__orzzx = determine_table_cast_map(matched_key_types,
            left_key_types, None, None, True, loc)
        if sqngd__orzzx:
            fcew__llou = False
            mejkc__tbdz = False
            znrzw__qhglq = None
            if join_node.has_live_left_table_var:
                hooju__tmzu = list(typemap[join_node.left_vars[0].name].
                    arr_types)
            else:
                hooju__tmzu = None
            for cjlzd__mol, tfo__ckov in sqngd__orzzx.items():
                if cjlzd__mol < join_node.n_left_table_cols:
                    assert join_node.has_live_left_table_var, 'Casting columns for a dead table should not occur'
                    hooju__tmzu[cjlzd__mol] = tfo__ckov
                    fcew__llou = True
                else:
                    znrzw__qhglq = tfo__ckov
                    mejkc__tbdz = True
            if fcew__llou:
                func_text += f"""    {left_other_names[0]} = bodo.utils.table_utils.table_astype({left_other_names[0]}, left_cast_table_type, False, _bodo_nan_to_str=False, used_cols=left_used_cols)
"""
                glbs['left_cast_table_type'] = TableType(tuple(hooju__tmzu))
                glbs['left_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_left_table_cols)) - join_node.
                    left_dead_var_inds)))
            if mejkc__tbdz:
                func_text += f"""    {left_other_names[1]} = bodo.utils.utils.astype({left_other_names[1]}, left_cast_index_type)
"""
                glbs['left_cast_index_type'] = znrzw__qhglq
    else:
        func_text += '    t1_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({bgff__plmkw[mce__hptj]}, key_type_{mce__hptj})'
             if left_key_types[mce__hptj] != matched_key_types[mce__hptj] else
            f'{bgff__plmkw[mce__hptj]}' for mce__hptj in range(enteh__htbvy)))
        func_text += '    data_left = ({}{})\n'.format(','.join(
            left_other_names), ',' if len(left_other_names) != 0 else '')
    if join_node.is_right_table:
        sqngd__orzzx = determine_table_cast_map(matched_key_types,
            right_key_types, None, None, True, loc)
        if sqngd__orzzx:
            fcew__llou = False
            mejkc__tbdz = False
            znrzw__qhglq = None
            if join_node.has_live_right_table_var:
                hooju__tmzu = list(typemap[join_node.right_vars[0].name].
                    arr_types)
            else:
                hooju__tmzu = None
            for cjlzd__mol, tfo__ckov in sqngd__orzzx.items():
                if cjlzd__mol < join_node.n_right_table_cols:
                    assert join_node.has_live_right_table_var, 'Casting columns for a dead table should not occur'
                    hooju__tmzu[cjlzd__mol] = tfo__ckov
                    fcew__llou = True
                else:
                    znrzw__qhglq = tfo__ckov
                    mejkc__tbdz = True
            if fcew__llou:
                func_text += f"""    {right_other_names[0]} = bodo.utils.table_utils.table_astype({right_other_names[0]}, right_cast_table_type, False, _bodo_nan_to_str=False, used_cols=right_used_cols)
"""
                glbs['right_cast_table_type'] = TableType(tuple(hooju__tmzu))
                glbs['right_used_cols'] = MetaType(tuple(sorted(set(range(
                    join_node.n_right_table_cols)) - join_node.
                    right_dead_var_inds)))
            if mejkc__tbdz:
                func_text += f"""    {right_other_names[1]} = bodo.utils.utils.astype({right_other_names[1]}, left_cast_index_type)
"""
                glbs['right_cast_index_type'] = znrzw__qhglq
    else:
        func_text += '    t2_keys = ({},)\n'.format(', '.join(
            f'bodo.utils.utils.astype({jrusr__vtl[mce__hptj]}, key_type_{mce__hptj})'
             if right_key_types[mce__hptj] != matched_key_types[mce__hptj] else
            f'{jrusr__vtl[mce__hptj]}' for mce__hptj in range(enteh__htbvy)))
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
        for mce__hptj in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(mce__hptj,
                mce__hptj)
        for mce__hptj in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(mce__hptj
                , mce__hptj)
        for mce__hptj in range(enteh__htbvy):
            func_text += (
                f'    t1_keys_{mce__hptj} = out_t1_keys[{mce__hptj}]\n')
        for mce__hptj in range(enteh__htbvy):
            func_text += (
                f'    t2_keys_{mce__hptj} = out_t2_keys[{mce__hptj}]\n')
    xnb__nymtr = {}
    exec(func_text, {}, xnb__nymtr)
    lfsm__jos = xnb__nymtr['f']
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
    skg__lgqr = compile_to_numba_ir(lfsm__jos, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=wftib__cwqun, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(skg__lgqr, ziv__qhap)
    dwso__ppw = skg__lgqr.body[:-3]
    if join_node.has_live_out_index_var:
        dwso__ppw[-1].target = join_node.out_data_vars[1]
    if join_node.has_live_out_table_var:
        dwso__ppw[-2].target = join_node.out_data_vars[0]
    assert join_node.has_live_out_index_var or join_node.has_live_out_table_var, 'At most one of table and index should be dead if the Join IR node is live'
    if not join_node.has_live_out_index_var:
        dwso__ppw.pop(-1)
    elif not join_node.has_live_out_table_var:
        dwso__ppw.pop(-2)
    return dwso__ppw


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap, left_logical_physical_map,
    right_logical_physical_map):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    mxaaf__lsoo = next_label()
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{mxaaf__lsoo}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
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
    xnb__nymtr = {}
    exec(func_text, table_getitem_funcs, xnb__nymtr)
    znxp__yxpex = xnb__nymtr[f'bodo_join_gen_cond{mxaaf__lsoo}']
    dpv__pektw = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    wgrr__kqr = numba.cfunc(dpv__pektw, nopython=True)(znxp__yxpex)
    join_gen_cond_cfunc[wgrr__kqr.native_name] = wgrr__kqr
    join_gen_cond_cfunc_addr[wgrr__kqr.native_name] = wgrr__kqr.address
    return wgrr__kqr, left_col_nums, right_col_nums


def _replace_column_accesses(expr, logical_to_physical_ind, name_to_var_map,
    typemap, col_vars, table_getitem_funcs, func_text, table_name, key_set,
    na_check_name, is_table_var):
    iwvwm__hmci = []
    for zze__ejjed, vvgie__nyb in name_to_var_map.items():
        odakl__ffcd = f'({table_name}.{zze__ejjed})'
        if odakl__ffcd not in expr:
            continue
        gld__yhjrx = f'getitem_{table_name}_val_{vvgie__nyb}'
        itla__wzo = f'_bodo_{table_name}_val_{vvgie__nyb}'
        if is_table_var:
            cngue__qmy = typemap[col_vars[0].name].arr_types[vvgie__nyb]
        else:
            cngue__qmy = typemap[col_vars[vvgie__nyb].name]
        if is_str_arr_type(cngue__qmy) or cngue__qmy == bodo.binary_array_type:
            func_text += f"""  {itla__wzo}, {itla__wzo}_size = {gld__yhjrx}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {itla__wzo} = bodo.libs.str_arr_ext.decode_utf8({itla__wzo}, {itla__wzo}_size)
"""
        else:
            func_text += (
                f'  {itla__wzo} = {gld__yhjrx}({table_name}_data1, {table_name}_ind)\n'
                )
        yyih__verb = logical_to_physical_ind[vvgie__nyb]
        table_getitem_funcs[gld__yhjrx
            ] = bodo.libs.array._gen_row_access_intrinsic(cngue__qmy,
            yyih__verb)
        expr = expr.replace(odakl__ffcd, itla__wzo)
        cpc__jiphf = f'({na_check_name}.{table_name}.{zze__ejjed})'
        if cpc__jiphf in expr:
            gzs__osk = f'nacheck_{table_name}_val_{vvgie__nyb}'
            bpwku__nlh = f'_bodo_isna_{table_name}_val_{vvgie__nyb}'
            if isinstance(cngue__qmy, bodo.libs.int_arr_ext.IntegerArrayType
                ) or cngue__qmy in (bodo.libs.bool_arr_ext.boolean_array,
                bodo.binary_array_type) or is_str_arr_type(cngue__qmy):
                func_text += f"""  {bpwku__nlh} = {gzs__osk}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += (
                    f'  {bpwku__nlh} = {gzs__osk}({table_name}_data1, {table_name}_ind)\n'
                    )
            table_getitem_funcs[gzs__osk
                ] = bodo.libs.array._gen_row_na_check_intrinsic(cngue__qmy,
                yyih__verb)
            expr = expr.replace(cpc__jiphf, bpwku__nlh)
        if vvgie__nyb not in key_set:
            iwvwm__hmci.append(yyih__verb)
    return expr, func_text, iwvwm__hmci


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    if is_str_arr_type(t1) and is_str_arr_type(t2):
        return bodo.string_array_type
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except Exception as bfg__vaeg:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    txdhc__wdjut = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[jiarb__ztg.name] in txdhc__wdjut for
        jiarb__ztg in join_node.get_live_left_vars())
    right_parallel = all(array_dists[jiarb__ztg.name] in txdhc__wdjut for
        jiarb__ztg in join_node.get_live_right_vars())
    if not left_parallel:
        assert not any(array_dists[jiarb__ztg.name] in txdhc__wdjut for
            jiarb__ztg in join_node.get_live_left_vars())
    if not right_parallel:
        assert not any(array_dists[jiarb__ztg.name] in txdhc__wdjut for
            jiarb__ztg in join_node.get_live_right_vars())
    if left_parallel or right_parallel:
        assert all(array_dists[jiarb__ztg.name] in txdhc__wdjut for
            jiarb__ztg in join_node.get_live_out_vars())
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
    ggysd__ueib = set(left_col_nums)
    viyi__bvirr = set(right_col_nums)
    fpyj__odg = join_node.vect_same_key
    zfxf__arlrm = []
    for mce__hptj in range(len(left_key_types)):
        if left_key_in_output[mce__hptj]:
            zfxf__arlrm.append(needs_typechange(matched_key_types[mce__hptj
                ], join_node.is_right, fpyj__odg[mce__hptj]))
    woicj__hio = len(left_key_types)
    gdkwj__yvodv = 0
    whx__osxk = left_physical_to_logical_list[len(left_key_types):]
    for mce__hptj, lpund__mtq in enumerate(whx__osxk):
        dofno__vjz = True
        if lpund__mtq in ggysd__ueib:
            dofno__vjz = left_key_in_output[woicj__hio]
            woicj__hio += 1
        if dofno__vjz:
            zfxf__arlrm.append(needs_typechange(left_other_types[mce__hptj],
                join_node.is_right, False))
    for mce__hptj in range(len(right_key_types)):
        if not fpyj__odg[mce__hptj] and not join_node.is_join:
            if right_key_in_output[gdkwj__yvodv]:
                zfxf__arlrm.append(needs_typechange(matched_key_types[
                    mce__hptj], join_node.is_left, False))
            gdkwj__yvodv += 1
    qor__fndnt = right_physical_to_logical_list[len(right_key_types):]
    for mce__hptj, lpund__mtq in enumerate(qor__fndnt):
        dofno__vjz = True
        if lpund__mtq in viyi__bvirr:
            dofno__vjz = right_key_in_output[gdkwj__yvodv]
            gdkwj__yvodv += 1
        if dofno__vjz:
            zfxf__arlrm.append(needs_typechange(right_other_types[mce__hptj
                ], join_node.is_left, False))
    enteh__htbvy = len(left_key_types)
    func_text = '    # beginning of _gen_local_hash_join\n'
    if join_node.is_left_table:
        if join_node.has_live_left_table_var:
            yvec__plrc = left_other_names[1:]
            jopmc__crsy = left_other_names[0]
        else:
            yvec__plrc = left_other_names
            jopmc__crsy = None
        nzb__lrd = '()' if len(yvec__plrc) == 0 else f'({yvec__plrc[0]},)'
        func_text += f"""    table_left = py_data_to_cpp_table({jopmc__crsy}, {nzb__lrd}, left_in_cols, {join_node.n_left_table_cols})
"""
        glbs['left_in_cols'] = MetaType(tuple(left_physical_to_logical_list))
    else:
        ylr__ljt = []
        for mce__hptj in range(enteh__htbvy):
            ylr__ljt.append('t1_keys[{}]'.format(mce__hptj))
        for mce__hptj in range(len(left_other_names)):
            ylr__ljt.append('data_left[{}]'.format(mce__hptj))
        func_text += '    info_list_total_l = [{}]\n'.format(','.join(
            'array_to_info({})'.format(teyf__jvj) for teyf__jvj in ylr__ljt))
        func_text += (
            '    table_left = arr_info_list_to_table(info_list_total_l)\n')
    if join_node.is_right_table:
        if join_node.has_live_right_table_var:
            eau__vnya = right_other_names[1:]
            jopmc__crsy = right_other_names[0]
        else:
            eau__vnya = right_other_names
            jopmc__crsy = None
        nzb__lrd = '()' if len(eau__vnya) == 0 else f'({eau__vnya[0]},)'
        func_text += f"""    table_right = py_data_to_cpp_table({jopmc__crsy}, {nzb__lrd}, right_in_cols, {join_node.n_right_table_cols})
"""
        glbs['right_in_cols'] = MetaType(tuple(right_physical_to_logical_list))
    else:
        zjbwa__duib = []
        for mce__hptj in range(enteh__htbvy):
            zjbwa__duib.append('t2_keys[{}]'.format(mce__hptj))
        for mce__hptj in range(len(right_other_names)):
            zjbwa__duib.append('data_right[{}]'.format(mce__hptj))
        func_text += '    info_list_total_r = [{}]\n'.format(','.join(
            'array_to_info({})'.format(teyf__jvj) for teyf__jvj in zjbwa__duib)
            )
        func_text += (
            '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    glbs['vect_same_key'] = np.array(fpyj__odg, dtype=np.int64)
    glbs['vect_need_typechange'] = np.array(zfxf__arlrm, dtype=np.int64)
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
        .format(left_parallel, right_parallel, enteh__htbvy, len(whx__osxk),
        len(qor__fndnt), join_node.is_left, join_node.is_right, join_node.
        is_join, join_node.extra_data_col_num != -1, join_node.
        indicator_col_num != -1, join_node.is_na_equal, len(left_col_nums),
        len(right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    leqnp__gnga = '(py_table_type, index_col_type)'
    func_text += f"""    out_data = cpp_table_to_py_data(out_table, out_col_inds, {leqnp__gnga}, total_rows_np[0], {join_node.n_out_table_cols})
"""
    if join_node.has_live_out_table_var:
        func_text += f'    T = out_data[0]\n'
    else:
        func_text += f'    T = None\n'
    if join_node.has_live_out_index_var:
        ixlam__dwvrx = 1 if join_node.has_live_out_table_var else 0
        func_text += f'    index_var = out_data[{ixlam__dwvrx}]\n'
    else:
        func_text += f'    index_var = None\n'
    glbs['py_table_type'] = out_table_type
    glbs['index_col_type'] = index_col_type
    glbs['out_col_inds'] = MetaType(tuple(out_physical_to_logical_list))
    if bool(join_node.out_used_cols) or index_col_type != types.none:
        func_text += '    delete_table(out_table)\n'
    if out_table_type != types.none:
        sqngd__orzzx = determine_table_cast_map(matched_key_types,
            left_key_types, left_used_key_nums, join_node.
            left_to_output_map, False, join_node.loc)
        sqngd__orzzx.update(determine_table_cast_map(matched_key_types,
            right_key_types, right_used_key_nums, join_node.
            right_to_output_map, False, join_node.loc))
        fcew__llou = False
        mejkc__tbdz = False
        if join_node.has_live_out_table_var:
            hooju__tmzu = list(out_table_type.arr_types)
        else:
            hooju__tmzu = None
        for cjlzd__mol, tfo__ckov in sqngd__orzzx.items():
            if cjlzd__mol < join_node.n_out_table_cols:
                assert join_node.has_live_out_table_var, 'Casting columns for a dead table should not occur'
                hooju__tmzu[cjlzd__mol] = tfo__ckov
                fcew__llou = True
            else:
                znrzw__qhglq = tfo__ckov
                mejkc__tbdz = True
        if fcew__llou:
            func_text += f"""    T = bodo.utils.table_utils.table_astype(T, cast_table_type, False, _bodo_nan_to_str=False, used_cols=used_cols)
"""
            adr__nnrv = bodo.TableType(tuple(hooju__tmzu))
            glbs['py_table_type'] = adr__nnrv
            glbs['cast_table_type'] = out_table_type
            glbs['used_cols'] = MetaType(tuple(out_table_used_cols))
        if mejkc__tbdz:
            glbs['index_col_type'] = znrzw__qhglq
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
    sqngd__orzzx: Dict[int, types.Type] = {}
    enteh__htbvy = len(matched_key_types)
    for mce__hptj in range(enteh__htbvy):
        if used_key_nums is None or mce__hptj in used_key_nums:
            if matched_key_types[mce__hptj] != key_types[mce__hptj] and (
                convert_dict_col or key_types[mce__hptj] != bodo.
                dict_str_arr_type):
                if output_map:
                    ixlam__dwvrx = output_map[mce__hptj]
                else:
                    ixlam__dwvrx = mce__hptj
                sqngd__orzzx[ixlam__dwvrx] = matched_key_types[mce__hptj]
    return sqngd__orzzx


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    nffvb__yrp = bodo.libs.distributed_api.get_size()
    kos__dfza = np.empty(nffvb__yrp, left_key_arrs[0].dtype)
    xxbie__ctjwk = np.empty(nffvb__yrp, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(kos__dfza, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(xxbie__ctjwk, left_key_arrs[0][-1])
    evfv__pgiqe = np.zeros(nffvb__yrp, np.int32)
    nbj__rzt = np.zeros(nffvb__yrp, np.int32)
    kjp__lbnlv = np.zeros(nffvb__yrp, np.int32)
    tga__vvad = right_key_arrs[0][0]
    fkmp__dgwy = right_key_arrs[0][-1]
    lomti__jep = -1
    mce__hptj = 0
    while mce__hptj < nffvb__yrp - 1 and xxbie__ctjwk[mce__hptj] < tga__vvad:
        mce__hptj += 1
    while mce__hptj < nffvb__yrp and kos__dfza[mce__hptj] <= fkmp__dgwy:
        lomti__jep, mcu__dkom = _count_overlap(right_key_arrs[0], kos__dfza
            [mce__hptj], xxbie__ctjwk[mce__hptj])
        if lomti__jep != 0:
            lomti__jep -= 1
            mcu__dkom += 1
        evfv__pgiqe[mce__hptj] = mcu__dkom
        nbj__rzt[mce__hptj] = lomti__jep
        mce__hptj += 1
    while mce__hptj < nffvb__yrp:
        evfv__pgiqe[mce__hptj] = 1
        nbj__rzt[mce__hptj] = len(right_key_arrs[0]) - 1
        mce__hptj += 1
    bodo.libs.distributed_api.alltoall(evfv__pgiqe, kjp__lbnlv, 1)
    bcm__pnnfi = kjp__lbnlv.sum()
    edco__mgof = np.empty(bcm__pnnfi, right_key_arrs[0].dtype)
    zbbj__yybtx = alloc_arr_tup(bcm__pnnfi, right_data)
    nnr__rcpf = bodo.ir.join.calc_disp(kjp__lbnlv)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], edco__mgof,
        evfv__pgiqe, kjp__lbnlv, nbj__rzt, nnr__rcpf)
    bodo.libs.distributed_api.alltoallv_tup(right_data, zbbj__yybtx,
        evfv__pgiqe, kjp__lbnlv, nbj__rzt, nnr__rcpf)
    return (edco__mgof,), zbbj__yybtx


@numba.njit
def _count_overlap(r_key_arr, start, end):
    mcu__dkom = 0
    lomti__jep = 0
    jwk__ahr = 0
    while jwk__ahr < len(r_key_arr) and r_key_arr[jwk__ahr] < start:
        lomti__jep += 1
        jwk__ahr += 1
    while jwk__ahr < len(r_key_arr) and start <= r_key_arr[jwk__ahr] <= end:
        jwk__ahr += 1
        mcu__dkom += 1
    return lomti__jep, mcu__dkom


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    ghlvq__dhos = np.empty_like(arr)
    ghlvq__dhos[0] = 0
    for mce__hptj in range(1, len(arr)):
        ghlvq__dhos[mce__hptj] = ghlvq__dhos[mce__hptj - 1] + arr[mce__hptj - 1
            ]
    return ghlvq__dhos


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    yixnm__rfpg = len(left_keys[0])
    vum__zvt = len(right_keys[0])
    bxhcm__fwgb = alloc_arr_tup(yixnm__rfpg, left_keys)
    upu__sku = alloc_arr_tup(yixnm__rfpg, right_keys)
    gvqsa__txoh = alloc_arr_tup(yixnm__rfpg, data_left)
    hdkih__ufivv = alloc_arr_tup(yixnm__rfpg, data_right)
    jekq__cvh = 0
    ixsoq__mmbjb = 0
    for jekq__cvh in range(yixnm__rfpg):
        if ixsoq__mmbjb < 0:
            ixsoq__mmbjb = 0
        while ixsoq__mmbjb < vum__zvt and getitem_arr_tup(right_keys,
            ixsoq__mmbjb) <= getitem_arr_tup(left_keys, jekq__cvh):
            ixsoq__mmbjb += 1
        ixsoq__mmbjb -= 1
        setitem_arr_tup(bxhcm__fwgb, jekq__cvh, getitem_arr_tup(left_keys,
            jekq__cvh))
        setitem_arr_tup(gvqsa__txoh, jekq__cvh, getitem_arr_tup(data_left,
            jekq__cvh))
        if ixsoq__mmbjb >= 0:
            setitem_arr_tup(upu__sku, jekq__cvh, getitem_arr_tup(right_keys,
                ixsoq__mmbjb))
            setitem_arr_tup(hdkih__ufivv, jekq__cvh, getitem_arr_tup(
                data_right, ixsoq__mmbjb))
        else:
            bodo.libs.array_kernels.setna_tup(upu__sku, jekq__cvh)
            bodo.libs.array_kernels.setna_tup(hdkih__ufivv, jekq__cvh)
    return bxhcm__fwgb, upu__sku, gvqsa__txoh, hdkih__ufivv
