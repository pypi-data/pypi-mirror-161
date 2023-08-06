"""
Common IR extension functions for connectors such as CSV, Parquet and JSON readers.
"""
import sys
from collections import defaultdict
from typing import Literal, Set, Tuple
import numba
from numba.core import ir, types
from numba.core.ir_utils import replace_vars_inner, visit_vars_inner
from bodo.hiframes.table import TableType
from bodo.transforms.distributed_analysis import Distribution
from bodo.transforms.table_column_del_pass import get_live_column_nums_block
from bodo.utils.py_objs import install_py_obj_class
from bodo.utils.typing import BodoError
from bodo.utils.utils import debug_prints


def connector_array_analysis(node, equiv_set, typemap, array_analysis):
    yaemj__qkrm = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    adv__bdcqw = []
    for qzh__dwmb in node.out_vars:
        lqjy__hxjwl = typemap[qzh__dwmb.name]
        if lqjy__hxjwl == types.none:
            continue
        qzwm__mwlyd = array_analysis._gen_shape_call(equiv_set, qzh__dwmb,
            lqjy__hxjwl.ndim, None, yaemj__qkrm)
        equiv_set.insert_equiv(qzh__dwmb, qzwm__mwlyd)
        adv__bdcqw.append(qzwm__mwlyd[0])
        equiv_set.define(qzh__dwmb, set())
    if len(adv__bdcqw) > 1:
        equiv_set.insert_equiv(*adv__bdcqw)
    return [], yaemj__qkrm


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        jhn__xyw = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        jhn__xyw = Distribution.OneD_Var
    else:
        jhn__xyw = Distribution.OneD
    for bwivs__pahd in node.out_vars:
        if bwivs__pahd.name in array_dists:
            jhn__xyw = Distribution(min(jhn__xyw.value, array_dists[
                bwivs__pahd.name].value))
    for bwivs__pahd in node.out_vars:
        array_dists[bwivs__pahd.name] = jhn__xyw


def connector_typeinfer(node, typeinferer):
    if node.connector_typ == 'csv':
        if node.chunksize is not None:
            typeinferer.lock_type(node.out_vars[0].name, node.out_types[0],
                loc=node.loc)
        else:
            typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(
                node.out_types)), loc=node.loc)
            typeinferer.lock_type(node.out_vars[1].name, node.
                index_column_typ, loc=node.loc)
        return
    if node.connector_typ in ('parquet', 'sql'):
        typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(node.
            out_types)), loc=node.loc)
        typeinferer.lock_type(node.out_vars[1].name, node.index_column_type,
            loc=node.loc)
        return
    for qzh__dwmb, lqjy__hxjwl in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(qzh__dwmb.name, lqjy__hxjwl, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    kdr__xpou = []
    for qzh__dwmb in node.out_vars:
        hisin__jgs = visit_vars_inner(qzh__dwmb, callback, cbdata)
        kdr__xpou.append(hisin__jgs)
    node.out_vars = kdr__xpou
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for wnqor__ujocr in node.filters:
            for dxzli__nor in range(len(wnqor__ujocr)):
                hgbh__xyh = wnqor__ujocr[dxzli__nor]
                wnqor__ujocr[dxzli__nor] = hgbh__xyh[0], hgbh__xyh[1
                    ], visit_vars_inner(hgbh__xyh[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({bwivs__pahd.name for bwivs__pahd in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for wkjxp__piw in node.filters:
            for bwivs__pahd in wkjxp__piw:
                if isinstance(bwivs__pahd[2], ir.Var):
                    use_set.add(bwivs__pahd[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    qbc__tsnzu = set(bwivs__pahd.name for bwivs__pahd in node.out_vars)
    return set(), qbc__tsnzu


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    kdr__xpou = []
    for qzh__dwmb in node.out_vars:
        hisin__jgs = replace_vars_inner(qzh__dwmb, var_dict)
        kdr__xpou.append(hisin__jgs)
    node.out_vars = kdr__xpou
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for wnqor__ujocr in node.filters:
            for dxzli__nor in range(len(wnqor__ujocr)):
                hgbh__xyh = wnqor__ujocr[dxzli__nor]
                wnqor__ujocr[dxzli__nor] = hgbh__xyh[0], hgbh__xyh[1
                    ], replace_vars_inner(hgbh__xyh[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for qzh__dwmb in node.out_vars:
        agdm__mxcb = definitions[qzh__dwmb.name]
        if node not in agdm__mxcb:
            agdm__mxcb.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        qgj__tnx = [bwivs__pahd[2] for wkjxp__piw in filters for
            bwivs__pahd in wkjxp__piw]
        mgq__xcyxt = set()
        for vamdr__voi in qgj__tnx:
            if isinstance(vamdr__voi, ir.Var):
                if vamdr__voi.name not in mgq__xcyxt:
                    filter_vars.append(vamdr__voi)
                mgq__xcyxt.add(vamdr__voi.name)
        return {bwivs__pahd.name: f'f{dxzli__nor}' for dxzli__nor,
            bwivs__pahd in enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {dxzli__nor for dxzli__nor in used_columns if dxzli__nor <
        num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    jvo__dvbc = {}
    for dxzli__nor, zboc__mvyt in enumerate(df_type.data):
        if isinstance(zboc__mvyt, bodo.IntegerArrayType):
            zvwr__xdji = zboc__mvyt.get_pandas_scalar_type_instance
            if zvwr__xdji not in jvo__dvbc:
                jvo__dvbc[zvwr__xdji] = []
            jvo__dvbc[zvwr__xdji].append(df.columns[dxzli__nor])
    for lqjy__hxjwl, jlyj__rzc in jvo__dvbc.items():
        df[jlyj__rzc] = df[jlyj__rzc].astype(lqjy__hxjwl)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    zzil__hazgt = node.out_vars[0].name
    assert isinstance(typemap[zzil__hazgt], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, xjrfg__wbjjp, vijj__dfgqr = get_live_column_nums_block(
            column_live_map, equiv_vars, zzil__hazgt)
        if not (xjrfg__wbjjp or vijj__dfgqr):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    iie__thhth = False
    if array_dists is not None:
        urfx__xcld = node.out_vars[0].name
        iie__thhth = array_dists[urfx__xcld] in (Distribution.OneD,
            Distribution.OneD_Var)
        bsjzf__ule = node.out_vars[1].name
        assert typemap[bsjzf__ule
            ] == types.none or not iie__thhth or array_dists[bsjzf__ule] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return iie__thhth


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    xou__kid = 'None'
    gjrhw__qgf = 'None'
    if filters:
        bwwt__qki = []
        yhia__wxn = []
        gnuj__fdlyj = False
        orig_colname_map = {hthfm__hbdel: dxzli__nor for dxzli__nor,
            hthfm__hbdel in enumerate(col_names)}
        for wnqor__ujocr in filters:
            mgrjq__lop = []
            jsi__wqf = []
            for bwivs__pahd in wnqor__ujocr:
                if isinstance(bwivs__pahd[2], ir.Var):
                    zsi__eoc, zvb__jhshs = determine_filter_cast(
                        original_out_types, typemap, bwivs__pahd,
                        orig_colname_map, partition_names, source)
                    if bwivs__pahd[1] == 'in':
                        gapg__qkxe = (
                            f"(ds.field('{bwivs__pahd[0]}').isin({filter_map[bwivs__pahd[2].name]}))"
                            )
                    else:
                        gapg__qkxe = (
                            f"(ds.field('{bwivs__pahd[0]}'){zsi__eoc} {bwivs__pahd[1]} ds.scalar({filter_map[bwivs__pahd[2].name]}){zvb__jhshs})"
                            )
                else:
                    assert bwivs__pahd[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if bwivs__pahd[1] == 'is not':
                        iij__nmz = '~'
                    else:
                        iij__nmz = ''
                    gapg__qkxe = (
                        f"({iij__nmz}ds.field('{bwivs__pahd[0]}').is_null())")
                jsi__wqf.append(gapg__qkxe)
                if not gnuj__fdlyj:
                    if bwivs__pahd[0] in partition_names and isinstance(
                        bwivs__pahd[2], ir.Var):
                        if output_dnf:
                            uktzi__rlq = (
                                f"('{bwivs__pahd[0]}', '{bwivs__pahd[1]}', {filter_map[bwivs__pahd[2].name]})"
                                )
                        else:
                            uktzi__rlq = gapg__qkxe
                        mgrjq__lop.append(uktzi__rlq)
                    elif bwivs__pahd[0] in partition_names and not isinstance(
                        bwivs__pahd[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            uktzi__rlq = (
                                f"('{bwivs__pahd[0]}', '{bwivs__pahd[1]}', '{bwivs__pahd[2]}')"
                                )
                        else:
                            uktzi__rlq = gapg__qkxe
                        mgrjq__lop.append(uktzi__rlq)
            jzs__fbhxj = ''
            if mgrjq__lop:
                if output_dnf:
                    jzs__fbhxj = ', '.join(mgrjq__lop)
                else:
                    jzs__fbhxj = ' & '.join(mgrjq__lop)
            else:
                gnuj__fdlyj = True
            znghv__zyo = ' & '.join(jsi__wqf)
            if jzs__fbhxj:
                if output_dnf:
                    bwwt__qki.append(f'[{jzs__fbhxj}]')
                else:
                    bwwt__qki.append(f'({jzs__fbhxj})')
            yhia__wxn.append(f'({znghv__zyo})')
        if output_dnf:
            xndav__icy = ', '.join(bwwt__qki)
        else:
            xndav__icy = ' | '.join(bwwt__qki)
        mmmw__iiio = ' | '.join(yhia__wxn)
        if xndav__icy and not gnuj__fdlyj:
            if output_dnf:
                xou__kid = f'[{xndav__icy}]'
            else:
                xou__kid = f'({xndav__icy})'
        gjrhw__qgf = f'({mmmw__iiio})'
    return xou__kid, gjrhw__qgf


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    tro__wnb = filter_val[0]
    ghdnm__zxmok = col_types[orig_colname_map[tro__wnb]]
    dpr__bgkf = bodo.utils.typing.element_type(ghdnm__zxmok)
    if source == 'parquet' and tro__wnb in partition_names:
        if dpr__bgkf == types.unicode_type:
            pohgi__upgv = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(dpr__bgkf, types.Integer):
            pohgi__upgv = f'.cast(pyarrow.{dpr__bgkf.name}(), safe=False)'
        else:
            pohgi__upgv = ''
    else:
        pohgi__upgv = ''
    aitzh__nvq = typemap[filter_val[2].name]
    if isinstance(aitzh__nvq, (types.List, types.Set)):
        nhewx__wznb = aitzh__nvq.dtype
    else:
        nhewx__wznb = aitzh__nvq
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dpr__bgkf,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(nhewx__wznb,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([dpr__bgkf, nhewx__wznb]):
        if not bodo.utils.typing.is_safe_arrow_cast(dpr__bgkf, nhewx__wznb):
            raise BodoError(
                f'Unsupported Arrow cast from {dpr__bgkf} to {nhewx__wznb} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if dpr__bgkf == types.unicode_type and nhewx__wznb in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif nhewx__wznb == types.unicode_type and dpr__bgkf in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(aitzh__nvq, (types.List, types.Set)):
                geyx__uqgt = 'list' if isinstance(aitzh__nvq, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {geyx__uqgt} values with isin filter pushdown.'
                    )
            return pohgi__upgv, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif dpr__bgkf == bodo.datetime_date_type and nhewx__wznb in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif nhewx__wznb == bodo.datetime_date_type and dpr__bgkf in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return pohgi__upgv, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return pohgi__upgv, ''
