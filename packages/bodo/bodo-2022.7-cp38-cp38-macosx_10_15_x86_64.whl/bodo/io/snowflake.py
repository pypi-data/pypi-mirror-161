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
    yll__dyb = urlparse(conn_str)
    qxubk__ykuzs = {}
    if yll__dyb.username:
        qxubk__ykuzs['user'] = yll__dyb.username
    if yll__dyb.password:
        qxubk__ykuzs['password'] = yll__dyb.password
    if yll__dyb.hostname:
        qxubk__ykuzs['account'] = yll__dyb.hostname
    if yll__dyb.port:
        qxubk__ykuzs['port'] = yll__dyb.port
    if yll__dyb.path:
        gslhn__rqqrb = yll__dyb.path
        if gslhn__rqqrb.startswith('/'):
            gslhn__rqqrb = gslhn__rqqrb[1:]
        ofgf__ocs = gslhn__rqqrb.split('/')
        if len(ofgf__ocs) == 2:
            lth__dicwn, schema = ofgf__ocs
        elif len(ofgf__ocs) == 1:
            lth__dicwn = ofgf__ocs[0]
            schema = None
        else:
            raise BodoError(
                f'Unexpected Snowflake connection string {conn_str}. Path is expected to contain database name and possibly schema'
                )
        qxubk__ykuzs['database'] = lth__dicwn
        if schema:
            qxubk__ykuzs['schema'] = schema
    if yll__dyb.query:
        for jux__gfhyq, grvsi__ieq in parse_qsl(yll__dyb.query):
            qxubk__ykuzs[jux__gfhyq] = grvsi__ieq
            if jux__gfhyq == 'session_parameters':
                qxubk__ykuzs[jux__gfhyq] = json.loads(grvsi__ieq)
    qxubk__ykuzs['application'] = 'bodo'
    return qxubk__ykuzs


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for zktf__hqyx in batches:
            zktf__hqyx._bodo_num_rows = zktf__hqyx.rowcount
            self._bodo_total_rows += zktf__hqyx._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    acz__mruy = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    eybd__xrklf = MPI.COMM_WORLD
    zlato__ixe = tracing.Event('snowflake_connect', is_parallel=False)
    uhi__gjkdg = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**uhi__gjkdg)
    zlato__ixe.finalize()
    if bodo.get_rank() == 0:
        gwnhe__lwl = conn.cursor()
        wkrn__uoy = tracing.Event('get_schema', is_parallel=False)
        lfch__ywqms = f'select * from ({query}) x LIMIT {100}'
        mvznx__ihzr = gwnhe__lwl.execute(lfch__ywqms).fetch_arrow_all()
        if mvznx__ihzr is None:
            mst__oohte = gwnhe__lwl.describe(query)
            alyu__zegw = [pa.field(soz__johp.name, FIELD_TYPE_TO_PA_TYPE[
                soz__johp.type_code]) for soz__johp in mst__oohte]
            schema = pa.schema(alyu__zegw)
        else:
            schema = mvznx__ihzr.schema
        wkrn__uoy.finalize()
        jdpr__rjkzl = tracing.Event('execute_query', is_parallel=False)
        gwnhe__lwl.execute(query)
        jdpr__rjkzl.finalize()
        batches = gwnhe__lwl.get_result_batches()
        eybd__xrklf.bcast((batches, schema))
    else:
        batches, schema = eybd__xrklf.bcast(None)
    foa__uodi = SnowflakeDataset(batches, schema, conn)
    acz__mruy.finalize()
    return foa__uodi
