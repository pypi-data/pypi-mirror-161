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
    ikq__nsb = urlparse(conn_str)
    teqx__caka = {}
    if ikq__nsb.username:
        teqx__caka['user'] = ikq__nsb.username
    if ikq__nsb.password:
        teqx__caka['password'] = ikq__nsb.password
    if ikq__nsb.hostname:
        teqx__caka['account'] = ikq__nsb.hostname
    if ikq__nsb.port:
        teqx__caka['port'] = ikq__nsb.port
    if ikq__nsb.path:
        sdb__rgn = ikq__nsb.path
        if sdb__rgn.startswith('/'):
            sdb__rgn = sdb__rgn[1:]
        nzw__unl = sdb__rgn.split('/')
        if len(nzw__unl) == 2:
            vjdi__qbc, schema = nzw__unl
        elif len(nzw__unl) == 1:
            vjdi__qbc = nzw__unl[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        teqx__caka['database'] = vjdi__qbc
        if schema:
            teqx__caka['schema'] = schema
    if ikq__nsb.query:
        for wvxjb__dtf, merl__htbkn in parse_qsl(ikq__nsb.query):
            teqx__caka[wvxjb__dtf] = merl__htbkn
            if wvxjb__dtf == 'session_parameters':
                teqx__caka[wvxjb__dtf] = json.loads(merl__htbkn)
    teqx__caka['application'] = 'bodo'
    return teqx__caka


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for sgq__emvj in batches:
            sgq__emvj._bodo_num_rows = sgq__emvj.rowcount
            self._bodo_total_rows += sgq__emvj._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    zwn__amuiq = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    xio__tuu = MPI.COMM_WORLD
    qod__wje = tracing.Event('snowflake_connect', is_parallel=False)
    mdia__lvxca = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**mdia__lvxca)
    qod__wje.finalize()
    if bodo.get_rank() == 0:
        rndrr__hmnbe = conn.cursor()
        essw__vrmdu = tracing.Event('get_schema', is_parallel=False)
        wczzc__jopp = f'select * from ({query}) x LIMIT {100}'
        qfm__whzku = rndrr__hmnbe.execute(wczzc__jopp).fetch_arrow_all()
        if qfm__whzku is None:
            kouw__viibn = rndrr__hmnbe.describe(query)
            ntux__wcaas = [pa.field(wsp__bjkie.name, FIELD_TYPE_TO_PA_TYPE[
                wsp__bjkie.type_code]) for wsp__bjkie in kouw__viibn]
            schema = pa.schema(ntux__wcaas)
        else:
            schema = qfm__whzku.schema
        essw__vrmdu.finalize()
        sgrz__pqdsv = tracing.Event('execute_query', is_parallel=False)
        rndrr__hmnbe.execute(query)
        sgrz__pqdsv.finalize()
        batches = rndrr__hmnbe.get_result_batches()
        xio__tuu.bcast((batches, schema))
    else:
        batches, schema = xio__tuu.bcast(None)
    twcn__tkg = SnowflakeDataset(batches, schema, conn)
    zwn__amuiq.finalize()
    return twcn__tkg
