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
    twbcc__mdv = urlparse(con_str)
    db_type = twbcc__mdv.scheme
    qejk__gfy = twbcc__mdv.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', qejk__gfy
    if db_type == 'mysql+pymysql':
        return 'mysql', qejk__gfy
    if con_str == 'iceberg+glue' or twbcc__mdv.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', qejk__gfy
    return db_type, qejk__gfy


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
    xrd__vipt = sql_node.out_vars[0].name
    qpf__gkuh = sql_node.out_vars[1].name
    if xrd__vipt not in lives and qpf__gkuh not in lives:
        return None
    elif xrd__vipt not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif qpf__gkuh not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        jvltg__umib = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        crs__tovq = []
        dszpp__skyc = []
        for sbb__uzpjk in sql_node.out_used_cols:
            rnxzb__xuclx = sql_node.df_colnames[sbb__uzpjk]
            crs__tovq.append(rnxzb__xuclx)
            if isinstance(sql_node.out_types[sbb__uzpjk], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                dszpp__skyc.append(rnxzb__xuclx)
        if sql_node.index_column_name:
            crs__tovq.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                dszpp__skyc.append(sql_node.index_column_name)
        bpej__znvj = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', jvltg__umib,
            bpej__znvj, crs__tovq)
        if dszpp__skyc:
            kxene__lozp = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                kxene__lozp, bpej__znvj, dszpp__skyc)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        tpdy__mdd = set(sql_node.unsupported_columns)
        xmqrh__pszvn = set(sql_node.out_used_cols)
        rir__fivdw = xmqrh__pszvn & tpdy__mdd
        if rir__fivdw:
            dmskr__ltum = sorted(rir__fivdw)
            eidgw__cfycu = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            jrkyg__awsb = 0
            for uwab__vacz in dmskr__ltum:
                while sql_node.unsupported_columns[jrkyg__awsb] != uwab__vacz:
                    jrkyg__awsb += 1
                eidgw__cfycu.append(
                    f"Column '{sql_node.original_df_colnames[uwab__vacz]}' with unsupported arrow type {sql_node.unsupported_arrow_types[jrkyg__awsb]}"
                    )
                jrkyg__awsb += 1
            ophex__piu = '\n'.join(eidgw__cfycu)
            raise BodoError(ophex__piu, loc=sql_node.loc)
    qbv__vslh, sxzw__viryk = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    zhz__zvvxf = ', '.join(qbv__vslh.values())
    jha__mxaax = (
        f'def sql_impl(sql_request, conn, database_schema, {zhz__zvvxf}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        ygdlu__sjxq = []
        for lavqk__eyt in sql_node.filters:
            ndl__aivc = []
            for okdj__uhzd in lavqk__eyt:
                ufpd__fkm = '{' + qbv__vslh[okdj__uhzd[2].name
                    ] + '}' if isinstance(okdj__uhzd[2], ir.Var
                    ) else okdj__uhzd[2]
                if okdj__uhzd[1] in ('startswith', 'endswith'):
                    vbkrj__mrfn = ['(', okdj__uhzd[1], '(', okdj__uhzd[0],
                        ',', ufpd__fkm, ')', ')']
                else:
                    vbkrj__mrfn = ['(', okdj__uhzd[0], okdj__uhzd[1],
                        ufpd__fkm, ')']
                ndl__aivc.append(' '.join(vbkrj__mrfn))
            ygdlu__sjxq.append(' ( ' + ' AND '.join(ndl__aivc) + ' ) ')
        oikzb__qxp = ' WHERE ' + ' OR '.join(ygdlu__sjxq)
        for sbb__uzpjk, hhm__yapjt in enumerate(qbv__vslh.values()):
            jha__mxaax += f'    {hhm__yapjt} = get_sql_literal({hhm__yapjt})\n'
        jha__mxaax += f'    sql_request = f"{{sql_request}} {oikzb__qxp}"\n'
    bdus__tjpvo = ''
    if sql_node.db_type == 'iceberg':
        bdus__tjpvo = zhz__zvvxf
    jha__mxaax += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {bdus__tjpvo})
"""
    uwhvt__gltw = {}
    exec(jha__mxaax, {}, uwhvt__gltw)
    konuv__qbcd = uwhvt__gltw['sql_impl']
    vpnl__snmg = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        sql_node.limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    wlcp__mkn = types.none if sql_node.database_schema is None else string_type
    ushwp__fts = compile_to_numba_ir(konuv__qbcd, {'_sql_reader_py':
        vpnl__snmg, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type, wlcp__mkn) +
        tuple(typemap[ghgaq__agvo.name] for ghgaq__agvo in sxzw__viryk),
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        jpjv__ruhcw = [sql_node.df_colnames[sbb__uzpjk] for sbb__uzpjk in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            jpjv__ruhcw.append(sql_node.index_column_name)
        hvu__hjun = escape_column_names(jpjv__ruhcw, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            fbxy__krdl = ('SELECT ' + hvu__hjun + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            fbxy__krdl = ('SELECT ' + hvu__hjun + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        fbxy__krdl = sql_node.sql_request
    replace_arg_nodes(ushwp__fts, [ir.Const(fbxy__krdl, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + sxzw__viryk)
    gvogr__gyml = ushwp__fts.body[:-3]
    gvogr__gyml[-2].target = sql_node.out_vars[0]
    gvogr__gyml[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        gvogr__gyml.pop(-1)
    elif not sql_node.out_used_cols:
        gvogr__gyml.pop(-2)
    return gvogr__gyml


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        jpjv__ruhcw = [(zbpac__bvdwu.upper() if zbpac__bvdwu in
            converted_colnames else zbpac__bvdwu) for zbpac__bvdwu in col_names
            ]
        hvu__hjun = ', '.join([f'"{zbpac__bvdwu}"' for zbpac__bvdwu in
            jpjv__ruhcw])
    elif db_type == 'mysql':
        hvu__hjun = ', '.join([f'`{zbpac__bvdwu}`' for zbpac__bvdwu in
            col_names])
    else:
        hvu__hjun = ', '.join([f'"{zbpac__bvdwu}"' for zbpac__bvdwu in
            col_names])
    return hvu__hjun


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    ybta__whn = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(ybta__whn,
        'Filter pushdown')
    if ybta__whn == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(ybta__whn, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif ybta__whn == bodo.pd_timestamp_type:

        def impl(filter_value):
            hjlbu__niimf = filter_value.nanosecond
            ebwn__hpyrk = ''
            if hjlbu__niimf < 10:
                ebwn__hpyrk = '00'
            elif hjlbu__niimf < 100:
                ebwn__hpyrk = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{ebwn__hpyrk}{hjlbu__niimf}'"
                )
        return impl
    elif ybta__whn == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {ybta__whn} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    yzhg__yafyc = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    ybta__whn = types.unliteral(filter_value)
    if isinstance(ybta__whn, types.List) and (isinstance(ybta__whn.dtype,
        scalar_isinstance) or ybta__whn.dtype in yzhg__yafyc):

        def impl(filter_value):
            ewn__scxgw = ', '.join([_get_snowflake_sql_literal_scalar(
                zbpac__bvdwu) for zbpac__bvdwu in filter_value])
            return f'({ewn__scxgw})'
        return impl
    elif isinstance(ybta__whn, scalar_isinstance) or ybta__whn in yzhg__yafyc:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {ybta__whn} used in filter pushdown.'
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
    except ImportError as oiaf__aqyt:
        exwgl__dty = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(exwgl__dty)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as oiaf__aqyt:
        exwgl__dty = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(exwgl__dty)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as oiaf__aqyt:
        exwgl__dty = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(exwgl__dty)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as oiaf__aqyt:
        exwgl__dty = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(exwgl__dty)


def req_limit(sql_request):
    import re
    ssakx__vmsq = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    jzir__jan = ssakx__vmsq.search(sql_request)
    if jzir__jan:
        return int(jzir__jan.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type, limit, parallel, typemap, filters, pyarrow_table_schema:
    'Optional[pyarrow.Schema]'):
    deo__pai = next_label()
    jpjv__ruhcw = [col_names[sbb__uzpjk] for sbb__uzpjk in out_used_cols]
    wmkjm__zyrs = [col_typs[sbb__uzpjk] for sbb__uzpjk in out_used_cols]
    if index_column_name:
        jpjv__ruhcw.append(index_column_name)
        wmkjm__zyrs.append(index_column_type)
    kmgys__tksv = None
    xjpw__fpd = None
    ysmis__ola = TableType(tuple(col_typs)) if out_used_cols else types.none
    bdus__tjpvo = ''
    qbv__vslh = {}
    sxzw__viryk = []
    if filters and db_type == 'iceberg':
        qbv__vslh, sxzw__viryk = bodo.ir.connector.generate_filter_map(filters)
        bdus__tjpvo = ', '.join(qbv__vslh.values())
    jha__mxaax = (
        f'def sql_reader_py(sql_request, conn, database_schema, {bdus__tjpvo}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        ghd__djo, vcsub__itjeo = bodo.ir.connector.generate_arrow_filters(
            filters, qbv__vslh, sxzw__viryk, col_names, col_names, col_typs,
            typemap, 'iceberg')
        pzre__yfv: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[sbb__uzpjk]) for sbb__uzpjk in out_used_cols]
        pxf__hkwh = {sumt__mbi: sbb__uzpjk for sbb__uzpjk, sumt__mbi in
            enumerate(pzre__yfv)}
        gob__cytgn = [int(is_nullable(col_typs[sbb__uzpjk])) for sbb__uzpjk in
            pzre__yfv]
        hpvl__ifj = ',' if bdus__tjpvo else ''
        jha__mxaax += (
            f"  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})\n")
        jha__mxaax += f"""  dnf_filters, expr_filters = get_filters_pyobject("{ghd__djo}", "{vcsub__itjeo}", ({bdus__tjpvo}{hpvl__ifj}))
"""
        jha__mxaax += f'  out_table = iceberg_read(\n'
        jha__mxaax += (
            f'    unicode_to_utf8(conn), unicode_to_utf8(database_schema),\n')
        jha__mxaax += (
            f'    unicode_to_utf8(sql_request), {parallel}, dnf_filters,\n')
        jha__mxaax += (
            f'    expr_filters, selected_cols_arr_{deo__pai}.ctypes,\n')
        jha__mxaax += (
            f'    {len(pzre__yfv)}, nullable_cols_arr_{deo__pai}.ctypes,\n')
        jha__mxaax += f'    pyarrow_table_schema_{deo__pai},\n'
        jha__mxaax += f'  )\n'
        jha__mxaax += f'  check_and_propagate_cpp_exception()\n'
        qgs__kdiq = not out_used_cols
        ysmis__ola = TableType(tuple(col_typs))
        if qgs__kdiq:
            ysmis__ola = types.none
        qpf__gkuh = 'None'
        if index_column_name is not None:
            cvzuv__zhrob = len(out_used_cols) + 1 if not qgs__kdiq else 0
            qpf__gkuh = (
                f'info_to_array(info_from_table(out_table, {cvzuv__zhrob}), index_col_typ)'
                )
        jha__mxaax += f'  index_var = {qpf__gkuh}\n'
        kmgys__tksv = None
        if not qgs__kdiq:
            kmgys__tksv = []
            kdk__sawtp = 0
            for sbb__uzpjk in range(len(col_names)):
                if kdk__sawtp < len(out_used_cols
                    ) and sbb__uzpjk == out_used_cols[kdk__sawtp]:
                    kmgys__tksv.append(pxf__hkwh[sbb__uzpjk])
                    kdk__sawtp += 1
                else:
                    kmgys__tksv.append(-1)
            kmgys__tksv = np.array(kmgys__tksv, dtype=np.int64)
        if qgs__kdiq:
            jha__mxaax += '  table_var = None\n'
        else:
            jha__mxaax += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{deo__pai}, py_table_type_{deo__pai})
"""
        jha__mxaax += f'  delete_table(out_table)\n'
        jha__mxaax += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        jha__mxaax += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        gob__cytgn = [int(is_nullable(col_typs[sbb__uzpjk])) for sbb__uzpjk in
            out_used_cols]
        if index_column_name:
            gob__cytgn.append(int(is_nullable(index_column_type)))
        jha__mxaax += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(gob__cytgn)}, np.array({gob__cytgn}, dtype=np.int32).ctypes)
"""
        jha__mxaax += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            jha__mxaax += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            jha__mxaax += '  index_var = None\n'
        if out_used_cols:
            jrkyg__awsb = []
            kdk__sawtp = 0
            for sbb__uzpjk in range(len(col_names)):
                if kdk__sawtp < len(out_used_cols
                    ) and sbb__uzpjk == out_used_cols[kdk__sawtp]:
                    jrkyg__awsb.append(kdk__sawtp)
                    kdk__sawtp += 1
                else:
                    jrkyg__awsb.append(-1)
            kmgys__tksv = np.array(jrkyg__awsb, dtype=np.int64)
            jha__mxaax += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{deo__pai}, py_table_type_{deo__pai})
"""
        else:
            jha__mxaax += '  table_var = None\n'
        jha__mxaax += '  delete_table(out_table)\n'
        jha__mxaax += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            jha__mxaax += f"""  type_usecols_offsets_arr_{deo__pai}_2 = type_usecols_offsets_arr_{deo__pai}
"""
            xjpw__fpd = np.array(out_used_cols, dtype=np.int64)
        jha__mxaax += '  df_typeref_2 = df_typeref\n'
        jha__mxaax += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            jha__mxaax += '  pymysql_check()\n'
        elif db_type == 'oracle':
            jha__mxaax += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            jha__mxaax += '  psycopg2_check()\n'
        if parallel:
            jha__mxaax += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                jha__mxaax += f'  nb_row = {limit}\n'
            else:
                jha__mxaax += '  with objmode(nb_row="int64"):\n'
                jha__mxaax += f'     if rank == {MPI_ROOT}:\n'
                jha__mxaax += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                jha__mxaax += '         frame = pd.read_sql(sql_cons, conn)\n'
                jha__mxaax += '         nb_row = frame.iat[0,0]\n'
                jha__mxaax += '     else:\n'
                jha__mxaax += '         nb_row = 0\n'
                jha__mxaax += '  nb_row = bcast_scalar(nb_row)\n'
            jha__mxaax += f"""  with objmode(table_var=py_table_type_{deo__pai}, index_var=index_col_typ):
"""
            jha__mxaax += (
                '    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)\n'
                )
            if db_type == 'oracle':
                jha__mxaax += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                jha__mxaax += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            jha__mxaax += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            jha__mxaax += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            jha__mxaax += f"""  with objmode(table_var=py_table_type_{deo__pai}, index_var=index_col_typ):
"""
            jha__mxaax += '    df_ret = pd.read_sql(sql_request, conn)\n'
            jha__mxaax += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            jha__mxaax += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            jha__mxaax += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            jha__mxaax += '    index_var = None\n'
        if out_used_cols:
            jha__mxaax += f'    arrs = []\n'
            jha__mxaax += f'    for i in range(df_ret.shape[1]):\n'
            jha__mxaax += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            jha__mxaax += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{deo__pai}_2, {len(col_names)})
"""
        else:
            jha__mxaax += '    table_var = None\n'
    jha__mxaax += '  return (table_var, index_var)\n'
    mjr__haf = globals()
    mjr__haf.update({'bodo': bodo, f'py_table_type_{deo__pai}': ysmis__ola,
        'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        mjr__haf.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{deo__pai}': kmgys__tksv})
    if db_type == 'iceberg':
        mjr__haf.update({f'selected_cols_arr_{deo__pai}': np.array(
            pzre__yfv, np.int32), f'nullable_cols_arr_{deo__pai}': np.array
            (gob__cytgn, np.int32), f'py_table_type_{deo__pai}': ysmis__ola,
            f'pyarrow_table_schema_{deo__pai}': pyarrow_table_schema,
            'get_filters_pyobject': bodo.io.parquet_pio.
            get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        mjr__haf.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        mjr__haf.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(wmkjm__zyrs), bodo.RangeIndexType(None
            ), tuple(jpjv__ruhcw)), 'Table': Table,
            f'type_usecols_offsets_arr_{deo__pai}': xjpw__fpd})
    uwhvt__gltw = {}
    exec(jha__mxaax, mjr__haf, uwhvt__gltw)
    vpnl__snmg = uwhvt__gltw['sql_reader_py']
    jat__fitq = numba.njit(vpnl__snmg)
    compiled_funcs.append(jat__fitq)
    return jat__fitq


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
