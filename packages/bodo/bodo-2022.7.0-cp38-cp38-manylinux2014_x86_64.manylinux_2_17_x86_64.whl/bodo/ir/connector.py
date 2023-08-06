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
    ovgnf__kyfeq = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    dazii__fldet = []
    for arfyz__wcakl in node.out_vars:
        gmwbp__tct = typemap[arfyz__wcakl.name]
        if gmwbp__tct == types.none:
            continue
        afrl__ztkjf = array_analysis._gen_shape_call(equiv_set,
            arfyz__wcakl, gmwbp__tct.ndim, None, ovgnf__kyfeq)
        equiv_set.insert_equiv(arfyz__wcakl, afrl__ztkjf)
        dazii__fldet.append(afrl__ztkjf[0])
        equiv_set.define(arfyz__wcakl, set())
    if len(dazii__fldet) > 1:
        equiv_set.insert_equiv(*dazii__fldet)
    return [], ovgnf__kyfeq


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and not node.is_select_query:
        fnoaj__rbng = Distribution.REP
    elif isinstance(node, SqlReader) and node.limit is not None:
        fnoaj__rbng = Distribution.OneD_Var
    else:
        fnoaj__rbng = Distribution.OneD
    for jomw__llc in node.out_vars:
        if jomw__llc.name in array_dists:
            fnoaj__rbng = Distribution(min(fnoaj__rbng.value, array_dists[
                jomw__llc.name].value))
    for jomw__llc in node.out_vars:
        array_dists[jomw__llc.name] = fnoaj__rbng


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
    for arfyz__wcakl, gmwbp__tct in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(arfyz__wcakl.name, gmwbp__tct, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    lxd__srdyh = []
    for arfyz__wcakl in node.out_vars:
        jxgun__sqbr = visit_vars_inner(arfyz__wcakl, callback, cbdata)
        lxd__srdyh.append(jxgun__sqbr)
    node.out_vars = lxd__srdyh
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for ibfqt__crs in node.filters:
            for mqo__fvtd in range(len(ibfqt__crs)):
                hzj__iesz = ibfqt__crs[mqo__fvtd]
                ibfqt__crs[mqo__fvtd] = hzj__iesz[0], hzj__iesz[1
                    ], visit_vars_inner(hzj__iesz[2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({jomw__llc.name for jomw__llc in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for dht__icbz in node.filters:
            for jomw__llc in dht__icbz:
                if isinstance(jomw__llc[2], ir.Var):
                    use_set.add(jomw__llc[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    zyn__ftsy = set(jomw__llc.name for jomw__llc in node.out_vars)
    return set(), zyn__ftsy


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    lxd__srdyh = []
    for arfyz__wcakl in node.out_vars:
        jxgun__sqbr = replace_vars_inner(arfyz__wcakl, var_dict)
        lxd__srdyh.append(jxgun__sqbr)
    node.out_vars = lxd__srdyh
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for ibfqt__crs in node.filters:
            for mqo__fvtd in range(len(ibfqt__crs)):
                hzj__iesz = ibfqt__crs[mqo__fvtd]
                ibfqt__crs[mqo__fvtd] = hzj__iesz[0], hzj__iesz[1
                    ], replace_vars_inner(hzj__iesz[2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for arfyz__wcakl in node.out_vars:
        dti__ubkv = definitions[arfyz__wcakl.name]
        if node not in dti__ubkv:
            dti__ubkv.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        filter_vars = []
        lek__jni = [jomw__llc[2] for dht__icbz in filters for jomw__llc in
            dht__icbz]
        vegr__bqz = set()
        for jdxh__olt in lek__jni:
            if isinstance(jdxh__olt, ir.Var):
                if jdxh__olt.name not in vegr__bqz:
                    filter_vars.append(jdxh__olt)
                vegr__bqz.add(jdxh__olt.name)
        return {jomw__llc.name: f'f{mqo__fvtd}' for mqo__fvtd, jomw__llc in
            enumerate(filter_vars)}, filter_vars
    else:
        return {}, []


this_module = sys.modules[__name__]
StreamReaderType = install_py_obj_class(types_name='stream_reader_type',
    module=this_module, class_name='StreamReaderType', model_name=
    'StreamReaderModel')


def trim_extra_used_columns(used_columns: Set, num_columns: int):
    return {mqo__fvtd for mqo__fvtd in used_columns if mqo__fvtd < num_columns}


def cast_float_to_nullable(df, df_type):
    import bodo
    tdjyo__izn = {}
    for mqo__fvtd, ppp__pna in enumerate(df_type.data):
        if isinstance(ppp__pna, bodo.IntegerArrayType):
            cua__aajys = ppp__pna.get_pandas_scalar_type_instance
            if cua__aajys not in tdjyo__izn:
                tdjyo__izn[cua__aajys] = []
            tdjyo__izn[cua__aajys].append(df.columns[mqo__fvtd])
    for gmwbp__tct, dvcs__kvsn in tdjyo__izn.items():
        df[dvcs__kvsn] = df[dvcs__kvsn].astype(gmwbp__tct)


def connector_table_column_use(node, block_use_map, equiv_vars, typemap,
    table_col_use_map):
    return


def base_connector_remove_dead_columns(node, column_live_map, equiv_vars,
    typemap, nodename, possible_cols):
    assert len(node.out_vars) == 2, f'invalid {nodename} node'
    wjhp__rnsr = node.out_vars[0].name
    assert isinstance(typemap[wjhp__rnsr], TableType
        ), f'{nodename} Node Table must be a TableType'
    if possible_cols:
        used_columns, ejc__iwx, aeo__efz = get_live_column_nums_block(
            column_live_map, equiv_vars, wjhp__rnsr)
        if not (ejc__iwx or aeo__efz):
            used_columns = trim_extra_used_columns(used_columns, len(
                possible_cols))
            if not used_columns:
                used_columns = {0}
            if len(used_columns) != len(node.out_used_cols):
                node.out_used_cols = list(sorted(used_columns))
    """We return flase in all cases, as no changes performed in the file will allow for dead code elimination to do work."""
    return False


def is_connector_table_parallel(node, array_dists, typemap, node_name):
    mvumt__etdm = False
    if array_dists is not None:
        joz__cpyf = node.out_vars[0].name
        mvumt__etdm = array_dists[joz__cpyf] in (Distribution.OneD,
            Distribution.OneD_Var)
        rtnjj__ejv = node.out_vars[1].name
        assert typemap[rtnjj__ejv
            ] == types.none or not mvumt__etdm or array_dists[rtnjj__ejv] in (
            Distribution.OneD, Distribution.OneD_Var
            ), f'{node_name} data/index parallelization does not match'
    return mvumt__etdm


def generate_arrow_filters(filters, filter_map, filter_vars, col_names,
    partition_names, original_out_types, typemap, source: Literal['parquet',
    'iceberg'], output_dnf=True) ->Tuple[str, str]:
    psceu__dcdo = 'None'
    vqxa__nyk = 'None'
    if filters:
        dgw__mxug = []
        jroh__ijd = []
        bojxx__ubhyc = False
        orig_colname_map = {pwsvz__tnmlx: mqo__fvtd for mqo__fvtd,
            pwsvz__tnmlx in enumerate(col_names)}
        for ibfqt__crs in filters:
            qqqsr__rkm = []
            dwd__sckr = []
            for jomw__llc in ibfqt__crs:
                if isinstance(jomw__llc[2], ir.Var):
                    idr__jpy, ldse__jri = determine_filter_cast(
                        original_out_types, typemap, jomw__llc,
                        orig_colname_map, partition_names, source)
                    if jomw__llc[1] == 'in':
                        ehl__gio = (
                            f"(ds.field('{jomw__llc[0]}').isin({filter_map[jomw__llc[2].name]}))"
                            )
                    else:
                        ehl__gio = (
                            f"(ds.field('{jomw__llc[0]}'){idr__jpy} {jomw__llc[1]} ds.scalar({filter_map[jomw__llc[2].name]}){ldse__jri})"
                            )
                else:
                    assert jomw__llc[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if jomw__llc[1] == 'is not':
                        cma__clo = '~'
                    else:
                        cma__clo = ''
                    ehl__gio = (
                        f"({cma__clo}ds.field('{jomw__llc[0]}').is_null())")
                dwd__sckr.append(ehl__gio)
                if not bojxx__ubhyc:
                    if jomw__llc[0] in partition_names and isinstance(jomw__llc
                        [2], ir.Var):
                        if output_dnf:
                            ahnv__mcr = (
                                f"('{jomw__llc[0]}', '{jomw__llc[1]}', {filter_map[jomw__llc[2].name]})"
                                )
                        else:
                            ahnv__mcr = ehl__gio
                        qqqsr__rkm.append(ahnv__mcr)
                    elif jomw__llc[0] in partition_names and not isinstance(
                        jomw__llc[2], ir.Var) and source == 'iceberg':
                        if output_dnf:
                            ahnv__mcr = (
                                f"('{jomw__llc[0]}', '{jomw__llc[1]}', '{jomw__llc[2]}')"
                                )
                        else:
                            ahnv__mcr = ehl__gio
                        qqqsr__rkm.append(ahnv__mcr)
            jsaxr__lkyby = ''
            if qqqsr__rkm:
                if output_dnf:
                    jsaxr__lkyby = ', '.join(qqqsr__rkm)
                else:
                    jsaxr__lkyby = ' & '.join(qqqsr__rkm)
            else:
                bojxx__ubhyc = True
            svymz__hlca = ' & '.join(dwd__sckr)
            if jsaxr__lkyby:
                if output_dnf:
                    dgw__mxug.append(f'[{jsaxr__lkyby}]')
                else:
                    dgw__mxug.append(f'({jsaxr__lkyby})')
            jroh__ijd.append(f'({svymz__hlca})')
        if output_dnf:
            atd__uzhn = ', '.join(dgw__mxug)
        else:
            atd__uzhn = ' | '.join(dgw__mxug)
        dco__musl = ' | '.join(jroh__ijd)
        if atd__uzhn and not bojxx__ubhyc:
            if output_dnf:
                psceu__dcdo = f'[{atd__uzhn}]'
            else:
                psceu__dcdo = f'({atd__uzhn})'
        vqxa__nyk = f'({dco__musl})'
    return psceu__dcdo, vqxa__nyk


def determine_filter_cast(col_types, typemap, filter_val, orig_colname_map,
    partition_names, source):
    import bodo
    brh__vtug = filter_val[0]
    eeqm__wxpcy = col_types[orig_colname_map[brh__vtug]]
    ljv__oxaxl = bodo.utils.typing.element_type(eeqm__wxpcy)
    if source == 'parquet' and brh__vtug in partition_names:
        if ljv__oxaxl == types.unicode_type:
            losm__lrn = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(ljv__oxaxl, types.Integer):
            losm__lrn = f'.cast(pyarrow.{ljv__oxaxl.name}(), safe=False)'
        else:
            losm__lrn = ''
    else:
        losm__lrn = ''
    smaj__moe = typemap[filter_val[2].name]
    if isinstance(smaj__moe, (types.List, types.Set)):
        jema__hcns = smaj__moe.dtype
    else:
        jema__hcns = smaj__moe
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ljv__oxaxl,
        'Filter pushdown')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(jema__hcns,
        'Filter pushdown')
    if not bodo.utils.typing.is_common_scalar_dtype([ljv__oxaxl, jema__hcns]):
        if not bodo.utils.typing.is_safe_arrow_cast(ljv__oxaxl, jema__hcns):
            raise BodoError(
                f'Unsupported Arrow cast from {ljv__oxaxl} to {jema__hcns} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if ljv__oxaxl == types.unicode_type and jema__hcns in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif jema__hcns == types.unicode_type and ljv__oxaxl in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            if isinstance(smaj__moe, (types.List, types.Set)):
                udya__jkae = 'list' if isinstance(smaj__moe, types.List
                    ) else 'tuple'
                raise BodoError(
                    f'Cannot cast {udya__jkae} values with isin filter pushdown.'
                    )
            return losm__lrn, ".cast(pyarrow.timestamp('ns'), safe=False)"
        elif ljv__oxaxl == bodo.datetime_date_type and jema__hcns in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif jema__hcns == bodo.datetime_date_type and ljv__oxaxl in (bodo.
            datetime64ns, bodo.pd_timestamp_type):
            return losm__lrn, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return losm__lrn, ''
