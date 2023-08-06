"""
Implementation of pd.read_sql in BODO.
We piggyback on the pandas implementation. Future plan is to have a faster
version for this task.
"""
from typing import List, Optional
from urllib.parse import urlparse
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.table import Table, TableType
from bodo.io.helpers import PyArrowTableSchemaType, is_nullable
from bodo.io.parquet_pio import ParquetPredicateType
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.distributed_api import bcast, bcast_scalar
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_and_propagate_cpp_exception
MPI_ROOT = 0


class SqlReader(ir.Stmt):

    def __init__(self, sql_request, connection, df_out, df_colnames,
        out_vars, out_types, converted_colnames, db_type, loc,
        unsupported_columns, unsupported_arrow_types, is_select_query,
        index_column_name, index_column_type, database_schema,
        pyarrow_table_schema=None):
        self.connector_typ = 'sql'
        self.sql_request = sql_request
        self.connection = connection
        self.df_out = df_out
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.converted_colnames = converted_colnames
        self.loc = loc
        self.limit = req_limit(sql_request)
        self.db_type = db_type
        self.filters = None
        self.unsupported_columns = unsupported_columns
        self.unsupported_arrow_types = unsupported_arrow_types
        self.is_select_query = is_select_query
        self.index_column_name = index_column_name
        self.index_column_type = index_column_type
        self.out_used_cols = list(range(len(df_colnames)))
        self.database_schema = database_schema
        self.pyarrow_table_schema = pyarrow_table_schema

    def __repr__(self):
        return (
            f'{self.df_out} = ReadSql(sql_request={self.sql_request}, connection={self.connection}, col_names={self.df_colnames}, types={self.out_types}, vars={self.out_vars}, limit={self.limit}, unsupported_columns={self.unsupported_columns}, unsupported_arrow_types={self.unsupported_arrow_types}, is_select_query={self.is_select_query}, index_column_name={self.index_column_name}, index_column_type={self.index_column_type}, out_used_cols={self.out_used_cols}, database_schema={self.database_schema}, pyarrow_table_schema={self.pyarrow_table_schema})'
            )


def parse_dbtype(con_str):
    lku__asiiq = urlparse(con_str)
    db_type = lku__asiiq.scheme
    gpxo__jnnc = lku__asiiq.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', gpxo__jnnc
    if db_type == 'mysql+pymysql':
        return 'mysql', gpxo__jnnc
    if con_str == 'iceberg+glue' or lku__asiiq.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', gpxo__jnnc
    return db_type, gpxo__jnnc


def remove_iceberg_prefix(con):
    import sys
    if sys.version_info.minor < 9:
        if con.startswith('iceberg+'):
            con = con[len('iceberg+'):]
        if con.startswith('iceberg://'):
            con = con[len('iceberg://'):]
    else:
        con = con.removeprefix('iceberg+').removeprefix('iceberg://')
    return con


def remove_dead_sql(sql_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    zfnc__ujjq = sql_node.out_vars[0].name
    cgkvj__lsvw = sql_node.out_vars[1].name
    if zfnc__ujjq not in lives and cgkvj__lsvw not in lives:
        return None
    elif zfnc__ujjq not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif cgkvj__lsvw not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        kfz__myu = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        dwuvi__aikz = []
        dlp__zjjqc = []
        for fen__dmb in sql_node.out_used_cols:
            mvtkj__pyrtc = sql_node.df_colnames[fen__dmb]
            dwuvi__aikz.append(mvtkj__pyrtc)
            if isinstance(sql_node.out_types[fen__dmb], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                dlp__zjjqc.append(mvtkj__pyrtc)
        if sql_node.index_column_name:
            dwuvi__aikz.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                dlp__zjjqc.append(sql_node.index_column_name)
        npqi__svpy = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', kfz__myu,
            npqi__svpy, dwuvi__aikz)
        if dlp__zjjqc:
            itw__vswzq = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', itw__vswzq,
                npqi__svpy, dlp__zjjqc)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        nqfbg__uoot = set(sql_node.unsupported_columns)
        snn__wfn = set(sql_node.out_used_cols)
        dke__ouz = snn__wfn & nqfbg__uoot
        if dke__ouz:
            sppd__tqykz = sorted(dke__ouz)
            fbha__rwvku = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            eiqcs__sio = 0
            for ppuq__digwe in sppd__tqykz:
                while sql_node.unsupported_columns[eiqcs__sio] != ppuq__digwe:
                    eiqcs__sio += 1
                fbha__rwvku.append(
                    f"Column '{sql_node.original_df_colnames[ppuq__digwe]}' with unsupported arrow type {sql_node.unsupported_arrow_types[eiqcs__sio]}"
                    )
                eiqcs__sio += 1
            qtrb__hnyul = '\n'.join(fbha__rwvku)
            raise BodoError(qtrb__hnyul, loc=sql_node.loc)
    trda__szisj, cde__sufdk = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    ytmdb__hzww = ', '.join(trda__szisj.values())
    tdtj__phcag = (
        f'def sql_impl(sql_request, conn, database_schema, {ytmdb__hzww}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        gpvpb__aarb = []
        for srp__pped in sql_node.filters:
            xef__oexa = []
            for huzb__aje in srp__pped:
                agyfi__gtbm = '{' + trda__szisj[huzb__aje[2].name
                    ] + '}' if isinstance(huzb__aje[2], ir.Var) else huzb__aje[
                    2]
                if huzb__aje[1] in ('startswith', 'endswith'):
                    nbru__sdg = ['(', huzb__aje[1], '(', huzb__aje[0], ',',
                        agyfi__gtbm, ')', ')']
                else:
                    nbru__sdg = ['(', huzb__aje[0], huzb__aje[1],
                        agyfi__gtbm, ')']
                xef__oexa.append(' '.join(nbru__sdg))
            gpvpb__aarb.append(' ( ' + ' AND '.join(xef__oexa) + ' ) ')
        idbi__uii = ' WHERE ' + ' OR '.join(gpvpb__aarb)
        for fen__dmb, tiap__mok in enumerate(trda__szisj.values()):
            tdtj__phcag += f'    {tiap__mok} = get_sql_literal({tiap__mok})\n'
        tdtj__phcag += f'    sql_request = f"{{sql_request}} {idbi__uii}"\n'
    ezt__scdv = ''
    if sql_node.db_type == 'iceberg':
        ezt__scdv = ytmdb__hzww
    tdtj__phcag += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {ezt__scdv})
"""
    hgigi__ztnr = {}
    exec(tdtj__phcag, {}, hgigi__ztnr)
    jehw__ecdl = hgigi__ztnr['sql_impl']
    vwf__noe = _gen_sql_reader_py(sql_node.df_colnames, sql_node.out_types,
        sql_node.index_column_name, sql_node.index_column_type, sql_node.
        out_used_cols, typingctx, targetctx, sql_node.db_type, sql_node.
        limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    plq__anown = (types.none if sql_node.database_schema is None else
        string_type)
    ocdd__uurjp = compile_to_numba_ir(jehw__ecdl, {'_sql_reader_py':
        vwf__noe, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type, plq__anown
        ) + tuple(typemap[jctz__zqsqw.name] for jctz__zqsqw in cde__sufdk),
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        ujb__euvsm = [sql_node.df_colnames[fen__dmb] for fen__dmb in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            ujb__euvsm.append(sql_node.index_column_name)
        imm__ajll = escape_column_names(ujb__euvsm, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            hesxi__gqdnq = ('SELECT ' + imm__ajll + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            hesxi__gqdnq = ('SELECT ' + imm__ajll + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        hesxi__gqdnq = sql_node.sql_request
    replace_arg_nodes(ocdd__uurjp, [ir.Const(hesxi__gqdnq, sql_node.loc),
        ir.Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + cde__sufdk)
    bpi__vouxr = ocdd__uurjp.body[:-3]
    bpi__vouxr[-2].target = sql_node.out_vars[0]
    bpi__vouxr[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        bpi__vouxr.pop(-1)
    elif not sql_node.out_used_cols:
        bpi__vouxr.pop(-2)
    return bpi__vouxr


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        ujb__euvsm = [(mhmhy__oogte.upper() if mhmhy__oogte in
            converted_colnames else mhmhy__oogte) for mhmhy__oogte in col_names
            ]
        imm__ajll = ', '.join([f'"{mhmhy__oogte}"' for mhmhy__oogte in
            ujb__euvsm])
    elif db_type == 'mysql':
        imm__ajll = ', '.join([f'`{mhmhy__oogte}`' for mhmhy__oogte in
            col_names])
    else:
        imm__ajll = ', '.join([f'"{mhmhy__oogte}"' for mhmhy__oogte in
            col_names])
    return imm__ajll


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    puxht__pnd = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(puxht__pnd,
        'Filter pushdown')
    if puxht__pnd == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(puxht__pnd, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif puxht__pnd == bodo.pd_timestamp_type:

        def impl(filter_value):
            ojq__kgiru = filter_value.nanosecond
            hyu__zmej = ''
            if ojq__kgiru < 10:
                hyu__zmej = '00'
            elif ojq__kgiru < 100:
                hyu__zmej = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{hyu__zmej}{ojq__kgiru}'"
                )
        return impl
    elif puxht__pnd == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {puxht__pnd} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    ziaki__rirbo = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    puxht__pnd = types.unliteral(filter_value)
    if isinstance(puxht__pnd, types.List) and (isinstance(puxht__pnd.dtype,
        scalar_isinstance) or puxht__pnd.dtype in ziaki__rirbo):

        def impl(filter_value):
            kdsi__qejnz = ', '.join([_get_snowflake_sql_literal_scalar(
                mhmhy__oogte) for mhmhy__oogte in filter_value])
            return f'({kdsi__qejnz})'
        return impl
    elif isinstance(puxht__pnd, scalar_isinstance
        ) or puxht__pnd in ziaki__rirbo:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {puxht__pnd} used in filter pushdown.'
            )


def sql_remove_dead_column(sql_node, column_live_map, equiv_vars, typemap):
    return bodo.ir.connector.base_connector_remove_dead_columns(sql_node,
        column_live_map, equiv_vars, typemap, 'SQLReader', sql_node.df_colnames
        )


numba.parfors.array_analysis.array_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[SqlReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[SqlReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[SqlReader] = remove_dead_sql
numba.core.analysis.ir_extension_usedefs[SqlReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[SqlReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[SqlReader] = sql_distributed_run
remove_dead_column_extensions[SqlReader] = sql_remove_dead_column
ir_extension_table_column_use[SqlReader
    ] = bodo.ir.connector.connector_table_column_use
compiled_funcs = []


@numba.njit
def sqlalchemy_check():
    with numba.objmode():
        sqlalchemy_check_()


def sqlalchemy_check_():
    try:
        import sqlalchemy
    except ImportError as grch__rmjs:
        eir__cdjzi = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(eir__cdjzi)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as grch__rmjs:
        eir__cdjzi = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(eir__cdjzi)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as grch__rmjs:
        eir__cdjzi = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(eir__cdjzi)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as grch__rmjs:
        eir__cdjzi = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(eir__cdjzi)


def req_limit(sql_request):
    import re
    vkny__bou = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    qrwk__nee = vkny__bou.search(sql_request)
    if qrwk__nee:
        return int(qrwk__nee.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type, limit, parallel, typemap, filters, pyarrow_table_schema:
    'Optional[pyarrow.Schema]'):
    epz__iwnm = next_label()
    ujb__euvsm = [col_names[fen__dmb] for fen__dmb in out_used_cols]
    bkkz__loi = [col_typs[fen__dmb] for fen__dmb in out_used_cols]
    if index_column_name:
        ujb__euvsm.append(index_column_name)
        bkkz__loi.append(index_column_type)
    rkj__qlgqa = None
    hhwy__bnnbn = None
    nddn__wpj = TableType(tuple(col_typs)) if out_used_cols else types.none
    ezt__scdv = ''
    trda__szisj = {}
    cde__sufdk = []
    if filters and db_type == 'iceberg':
        trda__szisj, cde__sufdk = bodo.ir.connector.generate_filter_map(filters
            )
        ezt__scdv = ', '.join(trda__szisj.values())
    tdtj__phcag = (
        f'def sql_reader_py(sql_request, conn, database_schema, {ezt__scdv}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        ysm__avp, lkth__nkkql = bodo.ir.connector.generate_arrow_filters(
            filters, trda__szisj, cde__sufdk, col_names, col_names,
            col_typs, typemap, 'iceberg')
        pbmx__wawjj: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[fen__dmb]) for fen__dmb in out_used_cols]
        nnb__aydlz = {ibib__fmj: fen__dmb for fen__dmb, ibib__fmj in
            enumerate(pbmx__wawjj)}
        bakw__lyq = [int(is_nullable(col_typs[fen__dmb])) for fen__dmb in
            pbmx__wawjj]
        igr__zguj = ',' if ezt__scdv else ''
        tdtj__phcag += (
            f"  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})\n")
        tdtj__phcag += f"""  dnf_filters, expr_filters = get_filters_pyobject("{ysm__avp}", "{lkth__nkkql}", ({ezt__scdv}{igr__zguj}))
"""
        tdtj__phcag += f'  out_table = iceberg_read(\n'
        tdtj__phcag += (
            f'    unicode_to_utf8(conn), unicode_to_utf8(database_schema),\n')
        tdtj__phcag += (
            f'    unicode_to_utf8(sql_request), {parallel}, dnf_filters,\n')
        tdtj__phcag += (
            f'    expr_filters, selected_cols_arr_{epz__iwnm}.ctypes,\n')
        tdtj__phcag += (
            f'    {len(pbmx__wawjj)}, nullable_cols_arr_{epz__iwnm}.ctypes,\n')
        tdtj__phcag += f'    pyarrow_table_schema_{epz__iwnm},\n'
        tdtj__phcag += f'  )\n'
        tdtj__phcag += f'  check_and_propagate_cpp_exception()\n'
        qme__uhff = not out_used_cols
        nddn__wpj = TableType(tuple(col_typs))
        if qme__uhff:
            nddn__wpj = types.none
        cgkvj__lsvw = 'None'
        if index_column_name is not None:
            tvd__xlzl = len(out_used_cols) + 1 if not qme__uhff else 0
            cgkvj__lsvw = (
                f'info_to_array(info_from_table(out_table, {tvd__xlzl}), index_col_typ)'
                )
        tdtj__phcag += f'  index_var = {cgkvj__lsvw}\n'
        rkj__qlgqa = None
        if not qme__uhff:
            rkj__qlgqa = []
            hpom__elsjp = 0
            for fen__dmb in range(len(col_names)):
                if hpom__elsjp < len(out_used_cols
                    ) and fen__dmb == out_used_cols[hpom__elsjp]:
                    rkj__qlgqa.append(nnb__aydlz[fen__dmb])
                    hpom__elsjp += 1
                else:
                    rkj__qlgqa.append(-1)
            rkj__qlgqa = np.array(rkj__qlgqa, dtype=np.int64)
        if qme__uhff:
            tdtj__phcag += '  table_var = None\n'
        else:
            tdtj__phcag += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{epz__iwnm}, py_table_type_{epz__iwnm})
"""
        tdtj__phcag += f'  delete_table(out_table)\n'
        tdtj__phcag += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        tdtj__phcag += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        bakw__lyq = [int(is_nullable(col_typs[fen__dmb])) for fen__dmb in
            out_used_cols]
        if index_column_name:
            bakw__lyq.append(int(is_nullable(index_column_type)))
        tdtj__phcag += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(bakw__lyq)}, np.array({bakw__lyq}, dtype=np.int32).ctypes)
"""
        tdtj__phcag += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            tdtj__phcag += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            tdtj__phcag += '  index_var = None\n'
        if out_used_cols:
            eiqcs__sio = []
            hpom__elsjp = 0
            for fen__dmb in range(len(col_names)):
                if hpom__elsjp < len(out_used_cols
                    ) and fen__dmb == out_used_cols[hpom__elsjp]:
                    eiqcs__sio.append(hpom__elsjp)
                    hpom__elsjp += 1
                else:
                    eiqcs__sio.append(-1)
            rkj__qlgqa = np.array(eiqcs__sio, dtype=np.int64)
            tdtj__phcag += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{epz__iwnm}, py_table_type_{epz__iwnm})
"""
        else:
            tdtj__phcag += '  table_var = None\n'
        tdtj__phcag += '  delete_table(out_table)\n'
        tdtj__phcag += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            tdtj__phcag += f"""  type_usecols_offsets_arr_{epz__iwnm}_2 = type_usecols_offsets_arr_{epz__iwnm}
"""
            hhwy__bnnbn = np.array(out_used_cols, dtype=np.int64)
        tdtj__phcag += '  df_typeref_2 = df_typeref\n'
        tdtj__phcag += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            tdtj__phcag += '  pymysql_check()\n'
        elif db_type == 'oracle':
            tdtj__phcag += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            tdtj__phcag += '  psycopg2_check()\n'
        if parallel:
            tdtj__phcag += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                tdtj__phcag += f'  nb_row = {limit}\n'
            else:
                tdtj__phcag += '  with objmode(nb_row="int64"):\n'
                tdtj__phcag += f'     if rank == {MPI_ROOT}:\n'
                tdtj__phcag += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                tdtj__phcag += '         frame = pd.read_sql(sql_cons, conn)\n'
                tdtj__phcag += '         nb_row = frame.iat[0,0]\n'
                tdtj__phcag += '     else:\n'
                tdtj__phcag += '         nb_row = 0\n'
                tdtj__phcag += '  nb_row = bcast_scalar(nb_row)\n'
            tdtj__phcag += f"""  with objmode(table_var=py_table_type_{epz__iwnm}, index_var=index_col_typ):
"""
            tdtj__phcag += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
            if db_type == 'oracle':
                tdtj__phcag += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                tdtj__phcag += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            tdtj__phcag += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            tdtj__phcag += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            tdtj__phcag += f"""  with objmode(table_var=py_table_type_{epz__iwnm}, index_var=index_col_typ):
"""
            tdtj__phcag += '    df_ret = pd.read_sql(sql_request, conn)\n'
            tdtj__phcag += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            tdtj__phcag += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            tdtj__phcag += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            tdtj__phcag += '    index_var = None\n'
        if out_used_cols:
            tdtj__phcag += f'    arrs = []\n'
            tdtj__phcag += f'    for i in range(df_ret.shape[1]):\n'
            tdtj__phcag += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            tdtj__phcag += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{epz__iwnm}_2, {len(col_names)})
"""
        else:
            tdtj__phcag += '    table_var = None\n'
    tdtj__phcag += '  return (table_var, index_var)\n'
    dzefz__nwcm = globals()
    dzefz__nwcm.update({'bodo': bodo, f'py_table_type_{epz__iwnm}':
        nddn__wpj, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        dzefz__nwcm.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{epz__iwnm}': rkj__qlgqa})
    if db_type == 'iceberg':
        dzefz__nwcm.update({f'selected_cols_arr_{epz__iwnm}': np.array(
            pbmx__wawjj, np.int32), f'nullable_cols_arr_{epz__iwnm}': np.
            array(bakw__lyq, np.int32), f'py_table_type_{epz__iwnm}':
            nddn__wpj, f'pyarrow_table_schema_{epz__iwnm}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        dzefz__nwcm.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        dzefz__nwcm.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(bkkz__loi), bodo.RangeIndexType(None),
            tuple(ujb__euvsm)), 'Table': Table,
            f'type_usecols_offsets_arr_{epz__iwnm}': hhwy__bnnbn})
    hgigi__ztnr = {}
    exec(tdtj__phcag, dzefz__nwcm, hgigi__ztnr)
    vwf__noe = hgigi__ztnr['sql_reader_py']
    fates__qlp = numba.njit(vwf__noe)
    compiled_funcs.append(fates__qlp)
    return fates__qlp


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
parquet_predicate_type = ParquetPredicateType()
pyarrow_table_schema_type = PyArrowTableSchemaType()
_iceberg_read = types.ExternalFunction('iceberg_pq_read', table_type(types.
    voidptr, types.voidptr, types.voidptr, types.boolean,
    parquet_predicate_type, parquet_predicate_type, types.voidptr, types.
    int32, types.voidptr, pyarrow_table_schema_type))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
ll.add_symbol('iceberg_pq_read', arrow_cpp.iceberg_pq_read)
