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
    eeqbl__gbxx = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    wlzh__buzfv = []
    for gue__gaeb in node.out_vars:
        twnld__zthj = typemap[gue__gaeb.name]
        if twnld__zthj == types.none:
            continue
        limy__acgds = array_analysis._gen_shape_call(equiv_set, gue__gaeb,
            twnld__zthj.ndim, None, eeqbl__gbxx)
        equiv_set.insert_equiv(gue__gaeb, limy__acgds)
        wlzh__buzfv.append(limy__acgds[0])
        equiv_set.define(gue__gaeb, set())
    if len(wlzh__buzfv) > 1:
        equiv_set.insert_equiv(*wlzh__buzfv)
    return [], eeqbl__gbxx


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        hwn__jrstd = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        hwn__jrstd = Distribution.OneD_Var
    else:
        hwn__jrstd = Distribution.OneD
    for fsg__zvsms in node.out_vars:
        if fsg__zvsms.name in array_dists:
            hwn__jrstd = Distribution(min(hwn__jrstd.value, array_dists[
                fsg__zvsms.name].value))
    for fsg__zvsms in node.out_vars:
        array_dists[fsg__zvsms.name] = hwn__jrstd


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
    for gue__gaeb, twnld__zthj in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(gue__gaeb.name, twnld__zthj, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    xecx__lkna = []
    for gue__gaeb in node.out_vars:
        pqvyc__fdetv = visit_vars_inner(gue__gaeb, callback, cbdata)
        xecx__lkna.append(pqvyc__fdetv)
    node.out_vars = xecx__lkna
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for lkkh__hki in node.filters:
            for ialr__hevgd in range(len(lkkh__hki)):
                almxi__hnkt = lkkh__hki[ialr__hevgd]
                lkkh__hki[ialr__hevgd] = almxi__hnkt[0], almxi__hnkt[1
                    ], visit_vars_inner(almxi__hnkt[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({fsg__zvsms.name for fsg__zvsms in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for adfoj__mdzu in node.filters:
            for fsg__zvsms in adfoj__mdzu:
                if isinstance(fsg__zvsms[2], ir.Var):
                    use_set.add(fsg__zvsms[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    epge__asfp = set(fsg__zvsms.name for fsg__zvsms in node.out_vars)
    return set(), epge__asfp


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    xecx__lkna = []
    for gue__gaeb in node.out_vars:
        pqvyc__fdetv = replace_vars_inner(gue__gaeb, var_dict)
        xecx__lkna.append(pqvyc__fdetv)
    node.out_vars = xecx__lkna
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for lkkh__hki in node.filters:
            for ialr__hevgd in range(len(lkkh__hki)):
                almxi__hnkt = lkkh__hki[ialr__hevgd]
                lkkh__hki[ialr__hevgd] = almxi__hnkt[0], almxi__hnkt[1
                    ], replace_vars_inner(almxi__hnkt[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for gue__gaeb in node.out_vars:
        fgdwx__xkzg = definitions[gue__gaeb.name]
        if node not in fgdwx__xkzg:
            fgdwx__xkzg.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        cmudn__jfqpk = [fsg__zvsms[2] for adfoj__mdzu in filters for
            fsg__zvsms in adfoj__mdzu]
        uube__rpiim = set()
        for guv__zvil in cmudn__jfqpk:
            if isinstance(guv__zvil, ir.Var):
                if guv__zvil.name not in uube__rpiim:
                    filter_vars.append(guv__zvil)
                uube__rpiim.add(guv__zvil.name)
        return {fsg__zvsms.name: f'f{ialr__hevgd}' for ialr__hevgd,
            fsg__zvsms in enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {ialr__hevgd for ialr__hevgd in used_columns if ialr__hevgd <
        num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    kwtmt__wte = {}
    for ialr__hevgd, llmh__dkow in enumerate(df_type.data):
        if isinstance(llmh__dkow, bodo.IntegerArrayType):
            fduru__kbbdv = llmh__dkow.get_pandas_scalar_type_instance
            if fduru__kbbdv not in kwtmt__wte:
                kwtmt__wte[fduru__kbbdv] = []
            kwtmt__wte[fduru__kbbdv].append(df.columns[ialr__hevgd])
    for twnld__zthj, ltx__nfhrl in kwtmt__wte.items():
        df[ltx__nfhrl] = df[ltx__nfhrl].astype(twnld__zthj)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    rcz__bbieg = node.out_vars[0].name
    assert isinstance(typemap[rcz__bbieg], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, aogix__kbhrz, vbqiw__bbj = get_live_column_nums_block(
            column_live_map, equiv_vars, rcz__bbieg)
        if not (aogix__kbhrz or vbqiw__bbj):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    nfg__ylf = False
    if array_dists is not None:
        rfeo__ara = node.out_vars[0].name
        nfg__ylf = array_dists[rfeo__ara] in (Distribution.OneD,
            Distribution.OneD_Var)
        oweij__okco = node.out_vars[1].name
        assert typemap[oweij__okco
            ] == types.none or not nfg__ylf or array_dists[oweij__okco] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return nfg__ylf


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    hhw__xtsrc = 'None'
    zhn__yigpw = 'None'
    if filters:
        tma__bbplf = []
        ntq__svoql = []
        gia__kosws = False
        orig_colname_map = {qvyd__viy: ialr__hevgd for ialr__hevgd,
            qvyd__viy in enumerate(col_names)}
        for lkkh__hki in filters:
            kyahe__gucmf = []
            exavi__dnkmb = []
            for fsg__zvsms in lkkh__hki:
                if isinstance(fsg__zvsms[2], ir.Var):
                    dait__jde, kou__yjukm = determine_filter_cast(
                        original_out_types, typemap, fsg__zvsms,
                        orig_colname_map, partition_names, source)
                    if fsg__zvsms[1] == 'in':
                        ryjr__hnwy = (
                            f"(ds.field('{fsg__zvsms[0]}').isin({filter_map[fsg__zvsms[2].name]}))"
                            )
                    else:
                        ryjr__hnwy = (
                            f"(ds.field('{fsg__zvsms[0]}'){dait__jde} {fsg__zvsms[1]} ds.scalar({filter_map[fsg__zvsms[2].name]}){kou__yjukm})"
                            )
                else:
                    assert fsg__zvsms[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if fsg__zvsms[1] == 'is not':
                        hubmq__wkyo = '~'
                    else:
                        hubmq__wkyo = ''
                    ryjr__hnwy = (
                        f"({hubmq__wkyo}ds.field('{fsg__zvsms[0]}').is_null())"
                        )
                exavi__dnkmb.append(ryjr__hnwy)
                if not gia__kosws:
                    if fsg__zvsms[0] in partition_names and isinstance(
                        fsg__zvsms[2], ir.Var):
                        if output_dnf:
                            gacfj__hjdt = (
                                f"('{fsg__zvsms[0]}', '{fsg__zvsms[1]}', {filter_map[fsg__zvsms[2].name]})"
                                )
                        else:
                            gacfj__hjdt = ryjr__hnwy
                        kyahe__gucmf.append(gacfj__hjdt)
                    elif fsg__zvsms[0] in partition_names and not isinstance(
                        fsg__zvsms[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            gacfj__hjdt = (
                                f"('{fsg__zvsms[0]}', '{fsg__zvsms[1]}', '{fsg__zvsms[2]}')"
                                )
                        else:
                            gacfj__hjdt = ryjr__hnwy
                        kyahe__gucmf.append(gacfj__hjdt)
            sgj__uhfp = ''
            if kyahe__gucmf:
                if output_dnf:
                    sgj__uhfp = ', '.join(kyahe__gucmf)
                else:
                    sgj__uhfp = ' & '.join(kyahe__gucmf)
            else:
                gia__kosws = True
            xhllf__sdxy = ' & '.join(exavi__dnkmb)
            if sgj__uhfp:
                if output_dnf:
                    tma__bbplf.append(f'[{sgj__uhfp}]')
                else:
                    tma__bbplf.append(f'({sgj__uhfp})')
            ntq__svoql.append(f'({xhllf__sdxy})')
        if output_dnf:
            yrvg__ntqmv = ', '.join(tma__bbplf)
        else:
            yrvg__ntqmv = ' | '.join(tma__bbplf)
        sid__fjcwh = ' | '.join(ntq__svoql)
        if yrvg__ntqmv and not gia__kosws:
            if output_dnf:
                hhw__xtsrc = f'[{yrvg__ntqmv}]'
            else:
                hhw__xtsrc = f'({yrvg__ntqmv})'
        zhn__yigpw = f'({sid__fjcwh})'
    return hhw__xtsrc, zhn__yigpw


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    sil__apzfi = filter_val[0]
    spurj__hfy = col_types[orig_colname_map[sil__apzfi]]
    pql__mnp = bodo.utils.typing.element_type(spurj__hfy)
    if source == 'parquet' and sil__apzfi in partition_names:
        if pql__mnp == types.unicode_type:
            jlm__flke = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(pql__mnp, types.Integer):
            jlm__flke = f'.cast(pyarrow.{pql__mnp.name}(), safe=False)'
        else:
            jlm__flke = ''
    else:
        jlm__flke = ''
    curt__kms = typemap[filter_val[2].name]
    if isinstance(curt__kms, (types.List, types.Set)):
        wvrr__zgqp = curt__kms.dtype
    else:
        wvrr__zgqp = curt__kms
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(pql__mnp,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(wvrr__zgqp,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([pql__mnp, wvrr__zgqp]):
        if not bodo.utils.typing.is_safe_arrow_cast(pql__mnp, wvrr__zgqp):
            raise BodoError(
                f'Unsupported Arrow cast from {pql__mnp} to {wvrr__zgqp} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if pql__mnp == types.unicode_type and wvrr__zgqp in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif wvrr__zgqp == types.unicode_type and pql__mnp in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(curt__kms, (types.List, types.Set)):
                fbiac__clvrm = 'list' if isinstance(curt__kms, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {fbiac__clvrm} values with isin filter pushdown.'
                    )
            return jlm__flke, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif pql__mnp == bodo.datetime_date_type and wvrr__zgqp in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif wvrr__zgqp == bodo.datetime_date_type and pql__mnp in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return jlm__flke, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return jlm__flke, ''
