from urllib.parse import parse_qsl, urlparse
import pyarrow as pa
import snowflake.connector
import bodo
from bodo.utils import tracing
from bodo.utils.typing import BodoError
FIELD_TYPE_TO_PA_TYPE = [pa.int64(), pa.float64(), pa.string(), pa.date32(),
    pa.timestamp('ns'), pa.string(), pa.timestamp('ns'), pa.timestamp('ns'),
    pa.timestamp('ns'), pa.string(), pa.string(), pa.binary(), pa.time64(
    'ns'), pa.bool_()]


def get_connection_params(conn_str):
    import json
    zeign__nsc = urlparse(conn_str)
    grogq__htebp = {}
    if zeign__nsc.username:
        grogq__htebp['user'] = zeign__nsc.username
    if zeign__nsc.password:
        grogq__htebp['password'] = zeign__nsc.password
    if zeign__nsc.hostname:
        grogq__htebp['account'] = zeign__nsc.hostname
    if zeign__nsc.port:
        grogq__htebp['port'] = zeign__nsc.port
    if zeign__nsc.path:
        mtd__ybi = zeign__nsc.path
        if mtd__ybi.startswith('/'):
            mtd__ybi = mtd__ybi[1:]
        sgmoe__xanbv = mtd__ybi.split('/')
        if len(sgmoe__xanbv) == 2:
            fvwl__wxfp, schema = sgmoe__xanbv
        elif len(sgmoe__xanbv) == 1:
            fvwl__wxfp = sgmoe__xanbv[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        grogq__htebp['database'] = fvwl__wxfp
        if schema:
            grogq__htebp['schema'] = schema
    if zeign__nsc.query:
        for nnyq__uyuh, lcka__knoq in parse_qsl(zeign__nsc.query):
            grogq__htebp[nnyq__uyuh] = lcka__knoq
            if nnyq__uyuh == 'session_parameters':
                grogq__htebp[nnyq__uyuh] = json.loads(lcka__knoq)
    grogq__htebp['application'] = 'bodo'
    return grogq__htebp


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for szyi__abmgy in batches:
            szyi__abmgy._bodo_num_rows = szyi__abmgy.rowcount
            self._bodo_total_rows += szyi__abmgy._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    bvb__lrrx = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    cnh__cgkm = MPI.COMM_WORLD
    nnpy__ymaik = tracing.Event('snowflake_connect', is_parallel=False)
    elov__xqt = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**elov__xqt)
    nnpy__ymaik.finalize()
    if bodo.get_rank() == 0:
        hxtb__lgv = conn.cursor()
        jdrfe__uqle = tracing.Event('get_schema', is_parallel=False)
        axe__roy = f'select * from ({query}) x LIMIT {100}'
        hcts__elbuy = hxtb__lgv.execute(axe__roy).fetch_arrow_all()
        if hcts__elbuy is None:
            tokbj__ppsay = hxtb__lgv.describe(query)
            lqdgs__liovb = [pa.field(poys__ceqnu.name,
                FIELD_TYPE_TO_PA_TYPE[poys__ceqnu.type_code]) for
                poys__ceqnu in tokbj__ppsay]
            schema = pa.schema(lqdgs__liovb)
        else:
            schema = hcts__elbuy.schema
        jdrfe__uqle.finalize()
        foan__uxut = tracing.Event('execute_query', is_parallel=False)
        hxtb__lgv.execute(query)
        foan__uxut.finalize()
        batches = hxtb__lgv.get_result_batches()
        cnh__cgkm.bcast((batches, schema))
    else:
        batches, schema = cnh__cgkm.bcast(None)
    dhu__ryf = SnowflakeDataset(batches, schema, conn)
    bvb__lrrx.finalize()
    return dhu__ryf
