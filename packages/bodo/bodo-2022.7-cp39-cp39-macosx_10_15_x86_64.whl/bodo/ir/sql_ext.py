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
    ieym__zvkln = urlparse(con_str)
    db_type = ieym__zvkln.scheme
    zggpk__tmz = ieym__zvkln.password
    if con_str.startswith('oracle+cx_oracle://'):
        return 'oracle', zggpk__tmz
    if db_type == 'mysql+pymysql':
        return 'mysql', zggpk__tmz
    if con_str == 'iceberg+glue' or ieym__zvkln.scheme in ('iceberg',
        'iceberg+file', 'iceberg+s3', 'iceberg+thrift', 'iceberg+http',
        'iceberg+https'):
        return 'iceberg', zggpk__tmz
    return db_type, zggpk__tmz


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
    tqvi__xouzt = sql_node.out_vars[0].name
    minv__mya = sql_node.out_vars[1].name
    if tqvi__xouzt not in lives and minv__mya not in lives:
        return None
    elif tqvi__xouzt not in lives:
        sql_node.out_types = []
        sql_node.df_colnames = []
        sql_node.out_used_cols = []
    elif minv__mya not in lives:
        sql_node.index_column_name = None
        sql_node.index_arr_typ = types.none
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        sfe__xcag = (
            'Finish column pruning on read_sql node:\n%s\nColumns loaded %s\n')
        yqxwv__ijzl = []
        jqehn__bmo = []
        for nlmry__lyfzo in sql_node.out_used_cols:
            jstxf__gyd = sql_node.df_colnames[nlmry__lyfzo]
            yqxwv__ijzl.append(jstxf__gyd)
            if isinstance(sql_node.out_types[nlmry__lyfzo], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                jqehn__bmo.append(jstxf__gyd)
        if sql_node.index_column_name:
            yqxwv__ijzl.append(sql_node.index_column_name)
            if isinstance(sql_node.index_column_type, bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                jqehn__bmo.append(sql_node.index_column_name)
        hoojl__uaj = sql_node.loc.strformat()
        bodo.user_logging.log_message('Column Pruning', sfe__xcag,
            hoojl__uaj, yqxwv__ijzl)
        if jqehn__bmo:
            pcnle__nsk = """Finished optimized encoding on read_sql node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', pcnle__nsk,
                hoojl__uaj, jqehn__bmo)
    parallel = bodo.ir.connector.is_connector_table_parallel(sql_node,
        array_dists, typemap, 'SQLReader')
    if sql_node.unsupported_columns:
        cgk__ipeb = set(sql_node.unsupported_columns)
        ymjx__byx = set(sql_node.out_used_cols)
        qeok__anw = ymjx__byx & cgk__ipeb
        if qeok__anw:
            fzo__vvb = sorted(qeok__anw)
            hquld__ero = [
                f'pandas.read_sql(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                'Please manually remove these columns from your sql query by specifying the columns you need in your SELECT statement. If these '
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            ywem__fedx = 0
            for luyu__wsd in fzo__vvb:
                while sql_node.unsupported_columns[ywem__fedx] != luyu__wsd:
                    ywem__fedx += 1
                hquld__ero.append(
                    f"Column '{sql_node.original_df_colnames[luyu__wsd]}' with unsupported arrow type {sql_node.unsupported_arrow_types[ywem__fedx]}"
                    )
                ywem__fedx += 1
            qjyp__rnvm = '\n'.join(hquld__ero)
            raise BodoError(qjyp__rnvm, loc=sql_node.loc)
    cuerp__sugr, vqf__avdr = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    yqyov__nbla = ', '.join(cuerp__sugr.values())
    heeeq__pptyq = (
        f'def sql_impl(sql_request, conn, database_schema, {yqyov__nbla}):\n')
    if sql_node.filters and sql_node.db_type != 'iceberg':
        loqcn__cvwr = []
        for kosxo__mrog in sql_node.filters:
            vylza__jaj = []
            for qbh__sktcv in kosxo__mrog:
                ahebr__vbczi = '{' + cuerp__sugr[qbh__sktcv[2].name
                    ] + '}' if isinstance(qbh__sktcv[2], ir.Var
                    ) else qbh__sktcv[2]
                if qbh__sktcv[1] in ('startswith', 'endswith'):
                    qyh__fae = ['(', qbh__sktcv[1], '(', qbh__sktcv[0], ',',
                        ahebr__vbczi, ')', ')']
                else:
                    qyh__fae = ['(', qbh__sktcv[0], qbh__sktcv[1],
                        ahebr__vbczi, ')']
                vylza__jaj.append(' '.join(qyh__fae))
            loqcn__cvwr.append(' ( ' + ' AND '.join(vylza__jaj) + ' ) ')
        slwvl__knmy = ' WHERE ' + ' OR '.join(loqcn__cvwr)
        for nlmry__lyfzo, btba__kbh in enumerate(cuerp__sugr.values()):
            heeeq__pptyq += f'    {btba__kbh} = get_sql_literal({btba__kbh})\n'
        heeeq__pptyq += f'    sql_request = f"{{sql_request}} {slwvl__knmy}"\n'
    iznam__ygqac = ''
    if sql_node.db_type == 'iceberg':
        iznam__ygqac = yqyov__nbla
    heeeq__pptyq += f"""    (table_var, index_var) = _sql_reader_py(sql_request, conn, database_schema, {iznam__ygqac})
"""
    xjvnh__auqf = {}
    exec(heeeq__pptyq, {}, xjvnh__auqf)
    iwwto__yfjo = xjvnh__auqf['sql_impl']
    dthn__ibc = _gen_sql_reader_py(sql_node.df_colnames, sql_node.out_types,
        sql_node.index_column_name, sql_node.index_column_type, sql_node.
        out_used_cols, typingctx, targetctx, sql_node.db_type, sql_node.
        limit, parallel, typemap, sql_node.filters, sql_node.
        pyarrow_table_schema)
    kso__dopt = types.none if sql_node.database_schema is None else string_type
    hour__gbkj = compile_to_numba_ir(iwwto__yfjo, {'_sql_reader_py':
        dthn__ibc, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type, kso__dopt) +
        tuple(typemap[rywi__iur.name] for rywi__iur in vqf__avdr), typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    if sql_node.is_select_query and sql_node.db_type != 'iceberg':
        kpw__sxs = [sql_node.df_colnames[nlmry__lyfzo] for nlmry__lyfzo in
            sql_node.out_used_cols]
        if sql_node.index_column_name:
            kpw__sxs.append(sql_node.index_column_name)
        nsf__femfb = escape_column_names(kpw__sxs, sql_node.db_type,
            sql_node.converted_colnames)
        if sql_node.db_type == 'oracle':
            kwg__rsf = ('SELECT ' + nsf__femfb + ' FROM (' + sql_node.
                sql_request + ') TEMP')
        else:
            kwg__rsf = ('SELECT ' + nsf__femfb + ' FROM (' + sql_node.
                sql_request + ') as TEMP')
    else:
        kwg__rsf = sql_node.sql_request
    replace_arg_nodes(hour__gbkj, [ir.Const(kwg__rsf, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc), ir.Const(sql_node.
        database_schema, sql_node.loc)] + vqf__avdr)
    yssmo__dww = hour__gbkj.body[:-3]
    yssmo__dww[-2].target = sql_node.out_vars[0]
    yssmo__dww[-1].target = sql_node.out_vars[1]
    assert not (sql_node.index_column_name is None and not sql_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the SQL IR node is live'
    if sql_node.index_column_name is None:
        yssmo__dww.pop(-1)
    elif not sql_node.out_used_cols:
        yssmo__dww.pop(-2)
    return yssmo__dww


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        kpw__sxs = [(vla__ffhj.upper() if vla__ffhj in converted_colnames else
            vla__ffhj) for vla__ffhj in col_names]
        nsf__femfb = ', '.join([f'"{vla__ffhj}"' for vla__ffhj in kpw__sxs])
    elif db_type == 'mysql':
        nsf__femfb = ', '.join([f'`{vla__ffhj}`' for vla__ffhj in col_names])
    else:
        nsf__femfb = ', '.join([f'"{vla__ffhj}"' for vla__ffhj in col_names])
    return nsf__femfb


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal_scalar(filter_value):
    bjfrf__zdqph = types.unliteral(filter_value)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(bjfrf__zdqph,
        'Filter pushdown')
    if bjfrf__zdqph == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(bjfrf__zdqph, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif bjfrf__zdqph == bodo.pd_timestamp_type:

        def impl(filter_value):
            mxij__jki = filter_value.nanosecond
            jhs__vzyd = ''
            if mxij__jki < 10:
                jhs__vzyd = '00'
            elif mxij__jki < 100:
                jhs__vzyd = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{jhs__vzyd}{mxij__jki}'"
                )
        return impl
    elif bjfrf__zdqph == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported scalar type {bjfrf__zdqph} used in filter pushdown.'
            )


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    scalar_isinstance = types.Integer, types.Float
    uya__rqe = (bodo.datetime_date_type, bodo.pd_timestamp_type, types.
        unicode_type, types.bool_)
    bjfrf__zdqph = types.unliteral(filter_value)
    if isinstance(bjfrf__zdqph, types.List) and (isinstance(bjfrf__zdqph.
        dtype, scalar_isinstance) or bjfrf__zdqph.dtype in uya__rqe):

        def impl(filter_value):
            kvpr__hitg = ', '.join([_get_snowflake_sql_literal_scalar(
                vla__ffhj) for vla__ffhj in filter_value])
            return f'({kvpr__hitg})'
        return impl
    elif isinstance(bjfrf__zdqph, scalar_isinstance
        ) or bjfrf__zdqph in uya__rqe:
        return lambda filter_value: _get_snowflake_sql_literal_scalar(
            filter_value)
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {bjfrf__zdqph} used in filter pushdown.'
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
    except ImportError as vvfy__vraz:
        dbbht__emrqc = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(dbbht__emrqc)


@numba.njit
def pymysql_check():
    with numba.objmode():
        pymysql_check_()


def pymysql_check_():
    try:
        import pymysql
    except ImportError as vvfy__vraz:
        dbbht__emrqc = (
            "Using MySQL URI string requires pymsql to be installed. It can be installed by calling 'conda install -c conda-forge pymysql' or 'pip install PyMySQL'."
            )
        raise BodoError(dbbht__emrqc)


@numba.njit
def cx_oracle_check():
    with numba.objmode():
        cx_oracle_check_()


def cx_oracle_check_():
    try:
        import cx_Oracle
    except ImportError as vvfy__vraz:
        dbbht__emrqc = (
            "Using Oracle URI string requires cx_oracle to be installed. It can be installed by calling 'conda install -c conda-forge cx_oracle' or 'pip install cx-Oracle'."
            )
        raise BodoError(dbbht__emrqc)


@numba.njit
def psycopg2_check():
    with numba.objmode():
        psycopg2_check_()


def psycopg2_check_():
    try:
        import psycopg2
    except ImportError as vvfy__vraz:
        dbbht__emrqc = (
            "Using PostgreSQL URI string requires psycopg2 to be installed. It can be installed by calling 'conda install -c conda-forge psycopg2' or 'pip install psycopg2'."
            )
        raise BodoError(dbbht__emrqc)


def req_limit(sql_request):
    import re
    sxabq__bzmzn = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    upnl__fcdlf = sxabq__bzmzn.search(sql_request)
    if upnl__fcdlf:
        return int(upnl__fcdlf.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names: List[str], col_typs, index_column_name:
    str, index_column_type, out_used_cols: List[int], typingctx, targetctx,
    db_type, limit, parallel, typemap, filters, pyarrow_table_schema:
    'Optional[pyarrow.Schema]'):
    cghec__hkob = next_label()
    kpw__sxs = [col_names[nlmry__lyfzo] for nlmry__lyfzo in out_used_cols]
    xfgk__eufb = [col_typs[nlmry__lyfzo] for nlmry__lyfzo in out_used_cols]
    if index_column_name:
        kpw__sxs.append(index_column_name)
        xfgk__eufb.append(index_column_type)
    jxzja__ehvzh = None
    prt__rap = None
    lble__gucf = TableType(tuple(col_typs)) if out_used_cols else types.none
    iznam__ygqac = ''
    cuerp__sugr = {}
    vqf__avdr = []
    if filters and db_type == 'iceberg':
        cuerp__sugr, vqf__avdr = bodo.ir.connector.generate_filter_map(filters)
        iznam__ygqac = ', '.join(cuerp__sugr.values())
    heeeq__pptyq = (
        f'def sql_reader_py(sql_request, conn, database_schema, {iznam__ygqac}):\n'
        )
    if db_type == 'iceberg':
        assert pyarrow_table_schema is not None, 'SQLNode must contain a pyarrow_table_schema if reading from an Iceberg database'
        ygeq__ohgxz, pxw__qsrkz = bodo.ir.connector.generate_arrow_filters(
            filters, cuerp__sugr, vqf__avdr, col_names, col_names, col_typs,
            typemap, 'iceberg')
        igy__gcifs: List[int] = [pyarrow_table_schema.get_field_index(
            col_names[nlmry__lyfzo]) for nlmry__lyfzo in out_used_cols]
        qzzs__mfmqs = {bnels__odmn: nlmry__lyfzo for nlmry__lyfzo,
            bnels__odmn in enumerate(igy__gcifs)}
        uczz__frh = [int(is_nullable(col_typs[nlmry__lyfzo])) for
            nlmry__lyfzo in igy__gcifs]
        zijmg__lqcc = ',' if iznam__ygqac else ''
        heeeq__pptyq += (
            f"  ev = bodo.utils.tracing.Event('read_iceberg', {parallel})\n")
        heeeq__pptyq += f"""  dnf_filters, expr_filters = get_filters_pyobject("{ygeq__ohgxz}", "{pxw__qsrkz}", ({iznam__ygqac}{zijmg__lqcc}))
"""
        heeeq__pptyq += f'  out_table = iceberg_read(\n'
        heeeq__pptyq += (
            f'    unicode_to_utf8(conn), unicode_to_utf8(database_schema),\n')
        heeeq__pptyq += (
            f'    unicode_to_utf8(sql_request), {parallel}, dnf_filters,\n')
        heeeq__pptyq += (
            f'    expr_filters, selected_cols_arr_{cghec__hkob}.ctypes,\n')
        heeeq__pptyq += (
            f'    {len(igy__gcifs)}, nullable_cols_arr_{cghec__hkob}.ctypes,\n'
            )
        heeeq__pptyq += f'    pyarrow_table_schema_{cghec__hkob},\n'
        heeeq__pptyq += f'  )\n'
        heeeq__pptyq += f'  check_and_propagate_cpp_exception()\n'
        eqdh__nxdkg = not out_used_cols
        lble__gucf = TableType(tuple(col_typs))
        if eqdh__nxdkg:
            lble__gucf = types.none
        minv__mya = 'None'
        if index_column_name is not None:
            icq__hzte = len(out_used_cols) + 1 if not eqdh__nxdkg else 0
            minv__mya = (
                f'info_to_array(info_from_table(out_table, {icq__hzte}), index_col_typ)'
                )
        heeeq__pptyq += f'  index_var = {minv__mya}\n'
        jxzja__ehvzh = None
        if not eqdh__nxdkg:
            jxzja__ehvzh = []
            him__sxm = 0
            for nlmry__lyfzo in range(len(col_names)):
                if him__sxm < len(out_used_cols
                    ) and nlmry__lyfzo == out_used_cols[him__sxm]:
                    jxzja__ehvzh.append(qzzs__mfmqs[nlmry__lyfzo])
                    him__sxm += 1
                else:
                    jxzja__ehvzh.append(-1)
            jxzja__ehvzh = np.array(jxzja__ehvzh, dtype=np.int64)
        if eqdh__nxdkg:
            heeeq__pptyq += '  table_var = None\n'
        else:
            heeeq__pptyq += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{cghec__hkob}, py_table_type_{cghec__hkob})
"""
        heeeq__pptyq += f'  delete_table(out_table)\n'
        heeeq__pptyq += f'  ev.finalize()\n'
    elif db_type == 'snowflake':
        heeeq__pptyq += (
            f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n")
        uczz__frh = [int(is_nullable(col_typs[nlmry__lyfzo])) for
            nlmry__lyfzo in out_used_cols]
        if index_column_name:
            uczz__frh.append(int(is_nullable(index_column_type)))
        heeeq__pptyq += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(uczz__frh)}, np.array({uczz__frh}, dtype=np.int32).ctypes)
"""
        heeeq__pptyq += '  check_and_propagate_cpp_exception()\n'
        if index_column_name:
            heeeq__pptyq += f"""  index_var = info_to_array(info_from_table(out_table, {len(out_used_cols)}), index_col_typ)
"""
        else:
            heeeq__pptyq += '  index_var = None\n'
        if out_used_cols:
            ywem__fedx = []
            him__sxm = 0
            for nlmry__lyfzo in range(len(col_names)):
                if him__sxm < len(out_used_cols
                    ) and nlmry__lyfzo == out_used_cols[him__sxm]:
                    ywem__fedx.append(him__sxm)
                    him__sxm += 1
                else:
                    ywem__fedx.append(-1)
            jxzja__ehvzh = np.array(ywem__fedx, dtype=np.int64)
            heeeq__pptyq += f"""  table_var = cpp_table_to_py_table(out_table, table_idx_{cghec__hkob}, py_table_type_{cghec__hkob})
"""
        else:
            heeeq__pptyq += '  table_var = None\n'
        heeeq__pptyq += '  delete_table(out_table)\n'
        heeeq__pptyq += f'  ev.finalize()\n'
    else:
        if out_used_cols:
            heeeq__pptyq += f"""  type_usecols_offsets_arr_{cghec__hkob}_2 = type_usecols_offsets_arr_{cghec__hkob}
"""
            prt__rap = np.array(out_used_cols, dtype=np.int64)
        heeeq__pptyq += '  df_typeref_2 = df_typeref\n'
        heeeq__pptyq += '  sqlalchemy_check()\n'
        if db_type == 'mysql':
            heeeq__pptyq += '  pymysql_check()\n'
        elif db_type == 'oracle':
            heeeq__pptyq += '  cx_oracle_check()\n'
        elif db_type == 'postgresql' or db_type == 'postgresql+psycopg2':
            heeeq__pptyq += '  psycopg2_check()\n'
        if parallel:
            heeeq__pptyq += '  rank = bodo.libs.distributed_api.get_rank()\n'
            if limit is not None:
                heeeq__pptyq += f'  nb_row = {limit}\n'
            else:
                heeeq__pptyq += '  with objmode(nb_row="int64"):\n'
                heeeq__pptyq += f'     if rank == {MPI_ROOT}:\n'
                heeeq__pptyq += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                heeeq__pptyq += (
                    '         frame = pd.read_sql(sql_cons, conn)\n')
                heeeq__pptyq += '         nb_row = frame.iat[0,0]\n'
                heeeq__pptyq += '     else:\n'
                heeeq__pptyq += '         nb_row = 0\n'
                heeeq__pptyq += '  nb_row = bcast_scalar(nb_row)\n'
            heeeq__pptyq += f"""  with objmode(table_var=py_table_type_{cghec__hkob}, index_var=index_col_typ):
"""
            heeeq__pptyq += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
            if db_type == 'oracle':
                heeeq__pptyq += f"""    sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
            else:
                heeeq__pptyq += f"""    sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
            heeeq__pptyq += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            heeeq__pptyq += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        else:
            heeeq__pptyq += f"""  with objmode(table_var=py_table_type_{cghec__hkob}, index_var=index_col_typ):
"""
            heeeq__pptyq += '    df_ret = pd.read_sql(sql_request, conn)\n'
            heeeq__pptyq += (
                '    bodo.ir.connector.cast_float_to_nullable(df_ret, df_typeref_2)\n'
                )
        if index_column_name:
            heeeq__pptyq += (
                f'    index_var = df_ret.iloc[:, {len(out_used_cols)}].values\n'
                )
            heeeq__pptyq += f"""    df_ret.drop(columns=df_ret.columns[{len(out_used_cols)}], inplace=True)
"""
        else:
            heeeq__pptyq += '    index_var = None\n'
        if out_used_cols:
            heeeq__pptyq += f'    arrs = []\n'
            heeeq__pptyq += f'    for i in range(df_ret.shape[1]):\n'
            heeeq__pptyq += f'      arrs.append(df_ret.iloc[:, i].values)\n'
            heeeq__pptyq += f"""    table_var = Table(arrs, type_usecols_offsets_arr_{cghec__hkob}_2, {len(col_names)})
"""
        else:
            heeeq__pptyq += '    table_var = None\n'
    heeeq__pptyq += '  return (table_var, index_var)\n'
    dpzqy__hlv = globals()
    dpzqy__hlv.update({'bodo': bodo, f'py_table_type_{cghec__hkob}':
        lble__gucf, 'index_col_typ': index_column_type})
    if db_type in ('iceberg', 'snowflake'):
        dpzqy__hlv.update({'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'info_to_array':
            info_to_array, 'info_from_table': info_from_table,
            'delete_table': delete_table, 'cpp_table_to_py_table':
            cpp_table_to_py_table, f'table_idx_{cghec__hkob}': jxzja__ehvzh})
    if db_type == 'iceberg':
        dpzqy__hlv.update({f'selected_cols_arr_{cghec__hkob}': np.array(
            igy__gcifs, np.int32), f'nullable_cols_arr_{cghec__hkob}': np.
            array(uczz__frh, np.int32), f'py_table_type_{cghec__hkob}':
            lble__gucf, f'pyarrow_table_schema_{cghec__hkob}':
            pyarrow_table_schema, 'get_filters_pyobject': bodo.io.
            parquet_pio.get_filters_pyobject, 'iceberg_read': _iceberg_read})
    elif db_type == 'snowflake':
        dpzqy__hlv.update({'np': np, 'snowflake_read': _snowflake_read})
    else:
        dpzqy__hlv.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar,
            'pymysql_check': pymysql_check, 'cx_oracle_check':
            cx_oracle_check, 'psycopg2_check': psycopg2_check, 'df_typeref':
            bodo.DataFrameType(tuple(xfgk__eufb), bodo.RangeIndexType(None),
            tuple(kpw__sxs)), 'Table': Table,
            f'type_usecols_offsets_arr_{cghec__hkob}': prt__rap})
    xjvnh__auqf = {}
    exec(heeeq__pptyq, dpzqy__hlv, xjvnh__auqf)
    dthn__ibc = xjvnh__auqf['sql_reader_py']
    gbsnp__ruwio = numba.njit(dthn__ibc)
    compiled_funcs.append(gbsnp__ruwio)
    return gbsnp__ruwio


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
