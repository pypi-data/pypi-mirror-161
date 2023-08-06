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
    batnv__gcqu = urlparse(con_str)
    db_type = batnv__gcqu.scheme
    iidfb__sxyf = batnv__gcqu.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', iidfb__sxyf
    if db_type == 'mysql+pymysql':
        return 'mysql', iidfb__sxyf
    if con_str == 'iceberg+glue' or batnv__gcqu.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', iidfb__sxyf
    return db_type, iidfb__sxyf


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
    prd__cxcci = sql_node.out_vars[0].name
    ugfb__negsr = sql_node.out_vars[1].name
    if prd__cxcci not in lives and ugfb__negsr not in lives:
        return None
    elif prd__cxcci not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif ugfb__negsr not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        nnci__uinz = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        uuy__zipt = []
        dljyb__rin = []
        for miexi__cjhtm in sql_node.out_used_cols:
            nhd__rcglc = sql_node.df_colnames[miexi__cjhtm]
            uuy__zipt.append(nhd__rcglc)
            if isinstance(sql_node.out_types[miexi__cjhtm], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                dljyb__rin.append(nhd__rcglc)
        if sql_node.index_column_name:
            uuy__zipt.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                dljyb__rin.append(sql_node.index_column_name)
        rebac__zzxc = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', nnci__uinz,
            rebac__zzxc, uuy__zipt)
        if dljyb__rin:
            easgb__dvei = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                easgb__dvei, rebac__zzxc, dljyb__rin)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        suwu__phaap = set(sql_node.unsupported_columns)
        lpltj__nih = set(sql_node.out_used_cols)
        tgqs__nlwb = lpltj__nih & suwu__phaap
        if tgqs__nlwb:
            dxyr__hjjft = sorted(tgqs__nlwb)
            dlfm__motvb = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            gzkl__nznq = 0
            for extvk__sdut in dxyr__hjjft:
                while sql_node.unsupported_columns[gzkl__nznq] != extvk__sdut:
                    gzkl__nznq += 1
                dlfm__motvb.append(
                    f"Column '{sql_node.original_df_colnames[extvk__sdut]}' with unsupported arrow type {sql_node.unsupported_arrow_types[gzkl__nznq]}"
                    )
                gzkl__nznq += 1
            qbwh__dee = '\n'.join(dlfm__motvb)
            raise BodoError(qbwh__dee, loc=sql_node.loc)
    rcgzg__byg, kptn__vtym = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    bcm__veiyc = ', '.join(rcgzg__byg.values())
    znubo__opseb = (
        f'def sql_impl(sql_request, conn, database_schema, {bcm__veiyc}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        hcqf__oykp = []
        for qzqs__qpcx in sql_node.filters:
            ttp__igy = []
            for xacy__azzc in qzqs__qpcx:
                kgmx__cta = '{' + rcgzg__byg[xacy__azzc[2].name
                    ] + '}' if isinstance(xacy__azzc[2], ir.Var
                    ) else xacy__azzc[2]
                if xacy__azzc[1] in ('startswith', 'endswith'):
                    yzal__tdlz = ['(', xacy__azzc[1], '(', xacy__azzc[0],
                        ',', kgmx__cta, ')', ')']
                else:
                    yzal__tdlz = ['(', xacy__azzc[0], xacy__azzc[1],
                        kgmx__cta, ')']
                ttp__igy.append(' '.join(yzal__tdlz))
            hcqf__oykp.append(' ( ' + ' AND '.join(ttp__igy) + ' ) ')
        psf__fpaf = ' WHERE ' + ' OR '.join(hcqf__oykp)
        for miexi__cjhtm, kil__jrnj in enumerate(rcgzg__byg.values()):
            znubo__opseb += f'    {kil__jrnj} = get_sql_literal({kil__jrnj})\n'
        znubo__opseb += f'    sql_request = f"{{sql_request}} {psf__fpaf}"\n'
    pajx__bvtr = ''
    if sql_node.db_type == 'iceberg':
        pajx__bvtr = bcm__veiyc
    znubo__opseb += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {pajx__bvtr})
"""
    oew__uiqm = {}
    exec(znubo__opseb, {}, oew__uiqm)
    gkg__aszq = oew__uiqm['sql_impl']
    prn__ggthj = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, sql_node.index_column_name, sql_node.index_column_type,
        sql_node.out_used_cols, typingctx, targetctx, sql_node.db_type,
        sql_node.limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    apy__qoa = types.none if sql_node.database_schema is None else string_type
    cflcw__mlqr = compile_to_numba_ir(gkg__aszq, {'_sql_reader_py':
        prn__ggthj, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type, apy__qoa) +
        tuple(typemap[oslt__mvtdc.name] for oslt__mvtdc in kptn__vtym),
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        wvhc__prwff = [sql_node.df_colnames[miexi__cjhtm] for miexi__cjhtm in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            wvhc__prwff.append(sql_node.index_column_name)
        ftjly__pjset = escape_column_names(wvhc__prwff, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            tnxpf__tcead = ('SELECT ' + ftjly__pjset + ' FROM (' + sql_node
                .sql_request + ') TEMP')
        else:
            tnxpf__tcead = ('SELECT ' + ftjly__pjset + ' FROM (' + sql_node
                .sql_request + ') as TEMP')
    else:
        tnxpf__tcead = sql_node.sql_request
    replace_arg_nodes(cflcw__mlqr, [ir.Const(tnxpf__tcead, sql_node.loc),
        ir.Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + kptn__vtym)
    efm__qdez = cflcw__mlqr.body[:-3]
    efm__qdez[-2].target = sql_node.out_vars[0]
    efm__qdez[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        efm__qdez.pop(-1)
    elif not sql_node.out_used_cols:
        efm__qdez.pop(-2)
    return efm__qdez


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        wvhc__prwff = [(mpiq__vxso.upper() if mpiq__vxso in
            converted_colnames else mpiq__vxso) for mpiq__vxso in col_names]
        ftjly__pjset = ', '.join([f'"{mpiq__vxso}"' for mpiq__vxso in
            wvhc__prwff])
    elif db_type == 'mysql':
        ftjly__pjset = ', '.join([f'`{mpiq__vxso}`' for mpiq__vxso in
            col_names])
    else:
        ftjly__pjset = ', '.join([f'"{mpiq__vxso}"' for mpiq__vxso in
            col_names])
    return ftjly__pjset


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    rkve__tbbpo = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(rkve__tbbpo,
        'Filter pushdown')
    if rkve__tbbpo == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(rkve__tbbpo, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif rkve__tbbpo == bodo.pd_timestamp_type:

        def impl(filter_value):
            vga__lef = filter_value.nanosecond
            pdcx__iwla = ''
            if vga__lef < 10:
                pdcx__iwla = '00'
            elif vga__lef < 100:
                pdcx__iwla = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{pdcx__iwla}{vga__lef}'"
                )
        return impl
    elif rkve__tbbpo == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {rkve__tbbpo} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    kqg__zls = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    rkve__tbbpo = types.unliteral(filter_value)
    if isinstance(rkve__tbbpo, types.List) and (isinstance(rkve__tbbpo.
        dtype, scalar_isinstance) or rkve__tbbpo.dtype in kqg__zls):

        def impl(filter_value):
            bfs__xvk = ', '.join([_get_snowflake_sql_literal_scalar(
                mpiq__vxso) for mpiq__vxso in filter_value])
            return f'({bfs__xvk})'
        return impl
    elif isinstance(rkve__tbbpo, scalar_isinstance) or rkve__tbbpo in kqg__zls:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {rkve__tbbpo} used in filter pushdown.'
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
    except ImportError as lji__fqi:
        itw__fvkwa = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(itw__fvkwa)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as lji__fqi:
        itw__fvkwa = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(itw__fvkwa)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as lji__fqi:
        itw__fvkwa = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(itw__fvkwa)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as lji__fqi:
        itw__fvkwa = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(itw__fvkwa)


def req_limit(sql_request):
    import re
    rwh__hii = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    luen__msfv = rwh__hii.search(sql_request)
    if luen__msfv:
        return int(luen__msfv.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type, limit, parallel, typemap, filters, pyarrow_table_schema:
    'Optional[pyarrow.Schema]'):
    ryxww__eiyp = next_label()
    wvhc__prwff = [col_names[miexi__cjhtm] for miexi__cjhtm in out_used_cols]
    bdfah__upipo = [col_typs[miexi__cjhtm] for miexi__cjhtm in out_used_cols]
    if index_column_name:
        wvhc__prwff.append(index_column_name)
        bdfah__upipo.append(index_column_type)
    zsrtn__jec = None
    lkhfw__fznf = None
    bbw__wai = TableType(tuple(col_typs)) if out_used_cols else types.none
    pajx__bvtr = ''
    rcgzg__byg = {}
    kptn__vtym = []
    if filters and db_type == 'iceberg':
        rcgzg__byg, kptn__vtym = bodo.ir.connector.generate_filter_map(filters)
        pajx__bvtr = ', '.join(rcgzg__byg.values())
    znubo__opseb = (
        f'def sql_reader_py(sql_request, conn, database_schema, {pajx__bvtr}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        kbe__talcs, yfwc__zqc = bodo.ir.connector.generate_arrow_filters(
            filters, rcgzg__byg, kptn__vtym, col_names, col_names, col_typs,
            typemap, 'iceberg')
        apc__igei: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[miexi__cjhtm]) for miexi__cjhtm in out_used_cols]
        xnlwy__foub = {umty__uhy: miexi__cjhtm for miexi__cjhtm, umty__uhy in
            enumerate(apc__igei)}
        dkm__efwei = [int(is_nullable(col_typs[miexi__cjhtm])) for
            miexi__cjhtm in apc__igei]
        ogj__rrch = ',' if pajx__bvtr else ''
        znubo__opseb += (
            f"  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})\n")
        znubo__opseb += f"""  dnf_filters, expr_filters = get_filters_pyobject("{kbe__talcs}", "{yfwc__zqc}", ({pajx__bvtr}{ogj__rrch}))
"""
        znubo__opseb += f'  out_table = iceberg_read(\n'
        znubo__opseb += (
            f'    unicode_to_utf8(conn), unicode_to_utf8(database_schema),\n')
        znubo__opseb += (
            f'    unicode_to_utf8(sql_request), {parallel}, dnf_filters,\n')
        znubo__opseb += (
            f'    expr_filters, selected_cols_arr_{ryxww__eiyp}.ctypes,\n')
        znubo__opseb += (
            f'    {len(apc__igei)}, nullable_cols_arr_{ryxww__eiyp}.ctypes,\n')
        znubo__opseb += f'    pyarrow_table_schema_{ryxww__eiyp},\n'
        znubo__opseb += f'  )\n'
        znubo__opseb += f'  check_and_propagate_cpp_exception()\n'
        cnqt__mch = not out_used_cols
        bbw__wai = TableType(tuple(col_typs))
        if cnqt__mch:
            bbw__wai = types.none
        ugfb__negsr = 'None'
        if index_column_name is not None:
            uzpay__tjgw = len(out_used_cols) + 1 if not cnqt__mch else 0
            ugfb__negsr = (
                f'info_to_array(info_from_table(out_table, {uzpay__tjgw}), index_col_typ)'
                )
        znubo__opseb += f'  index_var = {ugfb__negsr}\n'
        zsrtn__jec = None
        if not cnqt__mch:
            zsrtn__jec = []
            sbex__ipwwx = 0
            for miexi__cjhtm in range(len(col_names)):
                if sbex__ipwwx < len(out_used_cols
                    ) and miexi__cjhtm == out_used_cols[sbex__ipwwx]:
                    zsrtn__jec.append(xnlwy__foub[miexi__cjhtm])
                    sbex__ipwwx += 1
                else:
                    zsrtn__jec.append(-1)
            zsrtn__jec = np.array(zsrtn__jec, dtype=np.int64)
        if cnqt__mch:
            znubo__opseb += '  table_var = None\n'
        else:
            znubo__opseb += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{ryxww__eiyp}, py_table_type_{ryxww__eiyp})
"""
        znubo__opseb += f'  delete_table(out_table)\n'
        znubo__opseb += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        znubo__opseb += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        dkm__efwei = [int(is_nullable(col_typs[miexi__cjhtm])) for
            miexi__cjhtm in out_used_cols]
        if index_column_name:
            dkm__efwei.append(int(is_nullable(index_column_type)))
        znubo__opseb += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(dkm__efwei)}, np.array({dkm__efwei}, dtype=np.int32).ctypes)
"""
        znubo__opseb += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            znubo__opseb += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            znubo__opseb += '  index_var = None\n'
        if out_used_cols:
            gzkl__nznq = []
            sbex__ipwwx = 0
            for miexi__cjhtm in range(len(col_names)):
                if sbex__ipwwx < len(out_used_cols
                    ) and miexi__cjhtm == out_used_cols[sbex__ipwwx]:
                    gzkl__nznq.append(sbex__ipwwx)
                    sbex__ipwwx += 1
                else:
                    gzkl__nznq.append(-1)
            zsrtn__jec = np.array(gzkl__nznq, dtype=np.int64)
            znubo__opseb += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{ryxww__eiyp}, py_table_type_{ryxww__eiyp})
"""
        else:
            znubo__opseb += '  table_var = None\n'
        znubo__opseb += '  delete_table(out_table)\n'
        znubo__opseb += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            znubo__opseb += f"""  type_usecols_offsets_arr_{ryxww__eiyp}_2 = type_usecols_offsets_arr_{ryxww__eiyp}
"""
            lkhfw__fznf = np.array(out_used_cols, dtype=np.int64)
        znubo__opseb += '  df_typeref_2 = df_typeref\n'
        znubo__opseb += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            znubo__opseb += '  pymysql_check()\n'
        elif db_type == 'oracle':
            znubo__opseb += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            znubo__opseb += '  psycopg2_check()\n'
        if parallel:
            znubo__opseb += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                znubo__opseb += f'  nb_row = {limit}\n'
            else:
                znubo__opseb += '  with objmode(nb_row="int64"):\n'
                znubo__opseb += f'     if rank == {MPI_ROOT}:\n'
                znubo__opseb += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                znubo__opseb += (
                    '         frame = pd.read_sql(sql_cons, conn)\n')
                znubo__opseb += '         nb_row = frame.iat[0,0]\n'
                znubo__opseb += '     else:\n'
                znubo__opseb += '         nb_row = 0\n'
                znubo__opseb += '  nb_row = bcast_scalar(nb_row)\n'
            znubo__opseb += f"""  with objmode(table_var=py_table_type_{ryxww__eiyp}, index_var=index_col_typ):
"""
            znubo__opseb += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
            if db_type == 'oracle':
                znubo__opseb += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                znubo__opseb += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            znubo__opseb += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            znubo__opseb += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            znubo__opseb += f"""  with objmode(table_var=py_table_type_{ryxww__eiyp}, index_var=index_col_typ):
"""
            znubo__opseb += '    df_ret = pd.read_sql(sql_request, conn)\n'
            znubo__opseb += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            znubo__opseb += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            znubo__opseb += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            znubo__opseb += '    index_var = None\n'
        if out_used_cols:
            znubo__opseb += f'    arrs = []\n'
            znubo__opseb += f'    for i in range(df_ret.shape[1]):\n'
            znubo__opseb += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            znubo__opseb += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{ryxww__eiyp}_2, {len(col_names)})
"""
        else:
            znubo__opseb += '    table_var = None\n'
    znubo__opseb += '  return (table_var, index_var)\n'
    qjbtp__zmsu = globals()
    qjbtp__zmsu.update({'bodo': bodo, f'py_table_type_{ryxww__eiyp}':
        bbw__wai, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        qjbtp__zmsu.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{ryxww__eiyp}': zsrtn__jec})
    if db_type == 'iceberg':
        qjbtp__zmsu.update({f'selected_cols_arr_{ryxww__eiyp}': np.array(
            apc__igei, np.int32), f'nullable_cols_arr_{ryxww__eiyp}': np.
            array(dkm__efwei, np.int32), f'py_table_type_{ryxww__eiyp}':
            bbw__wai, f'pyarrow_table_schema_{ryxww__eiyp}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        qjbtp__zmsu.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        qjbtp__zmsu.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(bdfah__upipo), bodo.RangeIndexType(
            None), tuple(wvhc__prwff)), 'Table': Table,
            f'type_usecols_offsets_arr_{ryxww__eiyp}': lkhfw__fznf})
    oew__uiqm = {}
    exec(znubo__opseb, qjbtp__zmsu, oew__uiqm)
    prn__ggthj = oew__uiqm['sql_reader_py']
    lsaks__rpd = numba.njit(prn__ggthj)
    compiled_funcs.append(lsaks__rpd)
    return lsaks__rpd


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
