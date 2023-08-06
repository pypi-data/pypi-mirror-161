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
    jfn__cna = urlparse(conn_str)
    tuo__mdm = {}
    if jfn__cna.username:
        tuo__mdm['user'] = jfn__cna.username
    if jfn__cna.password:
        tuo__mdm['password'] = jfn__cna.password
    if jfn__cna.hostname:
        tuo__mdm['account'] = jfn__cna.hostname
    if jfn__cna.port:
        tuo__mdm['port'] = jfn__cna.port
    if jfn__cna.path:
        iuv__pidq = jfn__cna.path
        if iuv__pidq.startswith('/'):
            iuv__pidq = iuv__pidq[1:]
        bldds__pug = iuv__pidq.split('/')
        if len(bldds__pug) == 2:
            vpvu__kmkt, schema = bldds__pug
        elif len(bldds__pug) == 1:
            vpvu__kmkt = bldds__pug[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        tuo__mdm['database'] = vpvu__kmkt
        if schema:
            tuo__mdm['schema'] = schema
    if jfn__cna.query:
        for aiom__ubzwd, lvy__afm in parse_qsl(jfn__cna.query):
            tuo__mdm[aiom__ubzwd] = lvy__afm
            if aiom__ubzwd == 'session_parameters':
                tuo__mdm[aiom__ubzwd] = json.loads(lvy__afm)
    tuo__mdm['application'] = 'bodo'
    return tuo__mdm


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for aolp__qhd in batches:
            aolp__qhd._bodo_num_rows = aolp__qhd.rowcount
            self._bodo_total_rows += aolp__qhd._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    jgg__nceoh = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    nwf__vqzf = MPI.COMM_WORLD
    yko__czl = tracing.Event('snowflake_connect', is_parallel=False)
    kdqky__pqbke = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**kdqky__pqbke)
    yko__czl.finalize()
    if bodo.get_rank() == 0:
        bix__los = conn.cursor()
        hvm__gyevy = tracing.Event('get_schema', is_parallel=False)
        kqwc__gwuxx = f'select * from ({query}) x LIMIT {100}'
        fms__suv = bix__los.execute(kqwc__gwuxx).fetch_arrow_all()
        if fms__suv is None:
            bxbrl__gyaat = bix__los.describe(query)
            uifiz__ehn = [pa.field(lmwz__oixei.name, FIELD_TYPE_TO_PA_TYPE[
                lmwz__oixei.type_code]) for lmwz__oixei in bxbrl__gyaat]
            schema = pa.schema(uifiz__ehn)
        else:
            schema = fms__suv.schema
        hvm__gyevy.finalize()
        hplu__klw = tracing.Event('execute_query', is_parallel=False)
        bix__los.execute(query)
        hplu__klw.finalize()
        batches = bix__los.get_result_batches()
        nwf__vqzf.bcast((batches, schema))
    else:
        batches, schema = nwf__vqzf.bcast(None)
    niy__ukznd = SnowflakeDataset(batches, schema, conn)
    jgg__nceoh.finalize()
    return niy__ukznd
