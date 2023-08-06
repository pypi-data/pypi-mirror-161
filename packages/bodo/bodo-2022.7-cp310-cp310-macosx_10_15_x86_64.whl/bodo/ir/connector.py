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
    ahqzf__xqol = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    uoztz__vgujt = []
    for ned__ayg in node.out_vars:
        ulma__jalg = typemap[ned__ayg.name]
        if ulma__jalg == types.none:
            continue
        ajt__ftroi = array_analysis._gen_shape_call(equiv_set, ned__ayg,
            ulma__jalg.ndim, None, ahqzf__xqol)
        equiv_set.insert_equiv(ned__ayg, ajt__ftroi)
        uoztz__vgujt.append(ajt__ftroi[0])
        equiv_set.define(ned__ayg, set())
    if len(uoztz__vgujt) > 1:
        equiv_set.insert_equiv(*uoztz__vgujt)
    return [], ahqzf__xqol


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        rlco__baje = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        rlco__baje = Distribution.OneD_Var
    else:
        rlco__baje = Distribution.OneD
    for hrrsv__nitu in node.out_vars:
        if hrrsv__nitu.name in array_dists:
            rlco__baje = Distribution(min(rlco__baje.value, array_dists[
                hrrsv__nitu.name].value))
    for hrrsv__nitu in node.out_vars:
        array_dists[hrrsv__nitu.name] = rlco__baje


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
    for ned__ayg, ulma__jalg in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(ned__ayg.name, ulma__jalg, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    zhu__xqbe = []
    for ned__ayg in node.out_vars:
        zmkaf__hfd = visit_vars_inner(ned__ayg, callback, cbdata)
        zhu__xqbe.append(zmkaf__hfd)
    node.out_vars = zhu__xqbe
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for hsl__mgz in node.filters:
            for khic__ntcc in range(len(hsl__mgz)):
                fhsy__qoa = hsl__mgz[khic__ntcc]
                hsl__mgz[khic__ntcc] = fhsy__qoa[0], fhsy__qoa[1
                    ], visit_vars_inner(fhsy__qoa[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({hrrsv__nitu.name for hrrsv__nitu in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for ixja__sqo in node.filters:
            for hrrsv__nitu in ixja__sqo:
                if isinstance(hrrsv__nitu[2], ir.Var):
                    use_set.add(hrrsv__nitu[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    jznzk__rxp = set(hrrsv__nitu.name for hrrsv__nitu in node.out_vars)
    return set(), jznzk__rxp


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    zhu__xqbe = []
    for ned__ayg in node.out_vars:
        zmkaf__hfd = replace_vars_inner(ned__ayg, var_dict)
        zhu__xqbe.append(zmkaf__hfd)
    node.out_vars = zhu__xqbe
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for hsl__mgz in node.filters:
            for khic__ntcc in range(len(hsl__mgz)):
                fhsy__qoa = hsl__mgz[khic__ntcc]
                hsl__mgz[khic__ntcc] = fhsy__qoa[0], fhsy__qoa[1
                    ], replace_vars_inner(fhsy__qoa[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for ned__ayg in node.out_vars:
        esgw__nkb = definitions[ned__ayg.name]
        if node not in esgw__nkb:
            esgw__nkb.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        waujj__amgbi = [hrrsv__nitu[2] for ixja__sqo in filters for
            hrrsv__nitu in ixja__sqo]
        hvck__alzqq = set()
        for rvr__ybb in waujj__amgbi:
            if isinstance(rvr__ybb, ir.Var):
                if rvr__ybb.name not in hvck__alzqq:
                    filter_vars.append(rvr__ybb)
                hvck__alzqq.add(rvr__ybb.name)
        return {hrrsv__nitu.name: f'f{khic__ntcc}' for khic__ntcc,
            hrrsv__nitu in enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {khic__ntcc for khic__ntcc in used_columns if khic__ntcc <
        num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    eaijg__xoga = {}
    for khic__ntcc, bvh__euq in enumerate(df_type.data):
        if isinstance(bvh__euq, bodo.IntegerArrayType):
            rvi__qdb = bvh__euq.get_pandas_scalar_type_instance
            if rvi__qdb not in eaijg__xoga:
                eaijg__xoga[rvi__qdb] = []
            eaijg__xoga[rvi__qdb].append(df.columns[khic__ntcc])
    for ulma__jalg, xmx__jfhqd in eaijg__xoga.items():
        df[xmx__jfhqd] = df[xmx__jfhqd].astype(ulma__jalg)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    fhf__rai = node.out_vars[0].name
    assert isinstance(typemap[fhf__rai], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, fnpqp__rzfpt, nzjqy__cvti = get_live_column_nums_block(
            column_live_map, equiv_vars, fhf__rai)
        if not (fnpqp__rzfpt or nzjqy__cvti):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    lexa__slcrq = False
    if array_dists is not None:
        tvm__ehiqi = node.out_vars[0].name
        lexa__slcrq = array_dists[tvm__ehiqi] in (Distribution.OneD,
            Distribution.OneD_Var)
        lxuf__aoygz = node.out_vars[1].name
        assert typemap[lxuf__aoygz
            ] == types.none or not lexa__slcrq or array_dists[lxuf__aoygz] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return lexa__slcrq


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    bevps__rkqy = 'None'
    tkpr__jqjkc = 'None'
    if filters:
        rpeu__hhe = []
        tczgr__hatqn = []
        ignp__xxeba = False
        orig_colname_map = {bmdbh__mlc: khic__ntcc for khic__ntcc,
            bmdbh__mlc in enumerate(col_names)}
        for hsl__mgz in filters:
            jiiu__llsm = []
            bsn__xem = []
            for hrrsv__nitu in hsl__mgz:
                if isinstance(hrrsv__nitu[2], ir.Var):
                    tapo__ijqti, joq__nfk = determine_filter_cast(
                        original_out_types, typemap, hrrsv__nitu,
                        orig_colname_map, partition_names, source)
                    if hrrsv__nitu[1] == 'in':
                        aftgf__jttzi = (
                            f"(ds.field('{hrrsv__nitu[0]}').isin({filter_map[hrrsv__nitu[2].name]}))"
                            )
                    else:
                        aftgf__jttzi = (
                            f"(ds.field('{hrrsv__nitu[0]}'){tapo__ijqti} {hrrsv__nitu[1]} ds.scalar({filter_map[hrrsv__nitu[2].name]}){joq__nfk})"
                            )
                else:
                    assert hrrsv__nitu[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if hrrsv__nitu[1] == 'is not':
                        syhx__nscp = '~'
                    else:
                        syhx__nscp = ''
                    aftgf__jttzi = (
                        f"({syhx__nscp}ds.field('{hrrsv__nitu[0]}').is_null())"
                        )
                bsn__xem.append(aftgf__jttzi)
                if not ignp__xxeba:
                    if hrrsv__nitu[0] in partition_names and isinstance(
                        hrrsv__nitu[2], ir.Var):
                        if output_dnf:
                            fxr__sdthv = (
                                f"('{hrrsv__nitu[0]}', '{hrrsv__nitu[1]}', {filter_map[hrrsv__nitu[2].name]})"
                                )
                        else:
                            fxr__sdthv = aftgf__jttzi
                        jiiu__llsm.append(fxr__sdthv)
                    elif hrrsv__nitu[0] in partition_names and not isinstance(
                        hrrsv__nitu[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            fxr__sdthv = (
                                f"('{hrrsv__nitu[0]}', '{hrrsv__nitu[1]}', '{hrrsv__nitu[2]}')"
                                )
                        else:
                            fxr__sdthv = aftgf__jttzi
                        jiiu__llsm.append(fxr__sdthv)
            ryxu__zwnw = ''
            if jiiu__llsm:
                if output_dnf:
                    ryxu__zwnw = ', '.join(jiiu__llsm)
                else:
                    ryxu__zwnw = ' & '.join(jiiu__llsm)
            else:
                ignp__xxeba = True
            ccq__sflw = ' & '.join(bsn__xem)
            if ryxu__zwnw:
                if output_dnf:
                    rpeu__hhe.append(f'[{ryxu__zwnw}]')
                else:
                    rpeu__hhe.append(f'({ryxu__zwnw})')
            tczgr__hatqn.append(f'({ccq__sflw})')
        if output_dnf:
            mskxn__rqku = ', '.join(rpeu__hhe)
        else:
            mskxn__rqku = ' | '.join(rpeu__hhe)
        moks__ejtc = ' | '.join(tczgr__hatqn)
        if mskxn__rqku and not ignp__xxeba:
            if output_dnf:
                bevps__rkqy = f'[{mskxn__rqku}]'
            else:
                bevps__rkqy = f'({mskxn__rqku})'
        tkpr__jqjkc = f'({moks__ejtc})'
    return bevps__rkqy, tkpr__jqjkc


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    vsr__bjv = filter_val[0]
    kgxd__kbujf = col_types[orig_colname_map[vsr__bjv]]
    cpgy__csc = bodo.utils.typing.element_type(kgxd__kbujf)
    if source == 'parquet' and vsr__bjv in partition_names:
        if cpgy__csc == types.unicode_type:
            nqr__qksyf = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(cpgy__csc, types.Integer):
            nqr__qksyf = f'.cast(pyarrow.{cpgy__csc.name}(), safe=False)'
        else:
            nqr__qksyf = ''
    else:
        nqr__qksyf = ''
    uvy__wzjzg = typemap[filter_val[2].name]
    if isinstance(uvy__wzjzg, (types.List, types.Set)):
        ykzpi__ssz = uvy__wzjzg.dtype
    else:
        ykzpi__ssz = uvy__wzjzg
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(cpgy__csc,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ykzpi__ssz,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([cpgy__csc, ykzpi__ssz]):
        if not bodo.utils.typing.is_safe_arrow_cast(cpgy__csc, ykzpi__ssz):
            raise BodoError(
                f'Unsupported Arrow cast from {cpgy__csc} to {ykzpi__ssz} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if cpgy__csc == types.unicode_type and ykzpi__ssz in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif ykzpi__ssz == types.unicode_type and cpgy__csc in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(uvy__wzjzg, (types.List, types.Set)):
                fsj__hjqs = 'list' if isinstance(uvy__wzjzg, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {fsj__hjqs} values with isin filter pushdown.'
                    )
            return nqr__qksyf, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif cpgy__csc == bodo.datetime_date_type and ykzpi__ssz in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif ykzpi__ssz == bodo.datetime_date_type and cpgy__csc in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return nqr__qksyf, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return nqr__qksyf, ''
