"""
File that contains the main functionality for the Iceberg
integration within the Bodo repo. This does not contain the
main IR transformation.
"""
import os
import re
import sys
from typing import Any, Dict, List
from urllib.parse import urlparse
from uuid import uuid4
import numba
import numpy as np
import pyarrow as pa
from mpi4py import MPI
from numba.core import types
from numba.extending import intrinsic
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.io.fs_io import get_s3_bucket_region_njit
from bodo.io.helpers import is_nullable
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils import tracing
from bodo.utils.typing import BodoError, raise_bodo_error


def format_iceberg_conn(conn_str: str) ->str:
    ezfls__dhsro = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and ezfls__dhsro.scheme not in (
        'iceberg', 'iceberg+file', 'iceberg+s3', 'iceberg+thrift',
        'iceberg+http', 'iceberg+https'):
        raise BodoError(
            "'con' must start with one of the following: 'iceberg://', 'iceberg+file://', 'iceberg+s3://', 'iceberg+thrift://', 'iceberg+http://', 'iceberg+https://', 'iceberg+glue'"
            )
    if sys.version_info.minor < 9:
        if conn_str.startswith('iceberg+'):
            conn_str = conn_str[len('iceberg+'):]
        if conn_str.startswith('iceberg://'):
            conn_str = conn_str[len('iceberg://'):]
    else:
        conn_str = conn_str.removeprefix('iceberg+').removeprefix('iceberg://')
    return conn_str


@numba.njit
def format_iceberg_conn_njit(conn_str):
    with numba.objmode(conn_str='unicode_type'):
        conn_str = format_iceberg_conn(conn_str)
    return conn_str


def _clean_schema(schema: pa.Schema) ->pa.Schema:
    jpdm__svms = schema
    for mli__hpf in range(len(schema)):
        loo__amu = schema.field(mli__hpf)
        if pa.types.is_floating(loo__amu.type):
            jpdm__svms = jpdm__svms.set(mli__hpf, loo__amu.with_nullable(False)
                )
        elif pa.types.is_list(loo__amu.type):
            jpdm__svms = jpdm__svms.set(mli__hpf, loo__amu.with_type(pa.
                list_(pa.field('element', loo__amu.type.value_type))))
    return jpdm__svms


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    gfa__fbdu = _clean_schema(schema)
    hxak__rjqz = _clean_schema(other)
    return gfa__fbdu.equals(hxak__rjqz)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    ixjgh__ngou = None
    bqgtg__mkau = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            ixjgh__ngou, bqgtg__mkau, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as adox__rkpuk:
            if isinstance(adox__rkpuk, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                ixjgh__ngou = BodoError(
                    f'{adox__rkpuk.message}: {adox__rkpuk.java_error}')
            else:
                ixjgh__ngou = BodoError(adox__rkpuk.message)
    zmdkr__rnapz = MPI.COMM_WORLD
    ixjgh__ngou = zmdkr__rnapz.bcast(ixjgh__ngou)
    if isinstance(ixjgh__ngou, Exception):
        raise ixjgh__ngou
    col_names = ixjgh__ngou
    bqgtg__mkau = zmdkr__rnapz.bcast(bqgtg__mkau)
    pyarrow_schema = zmdkr__rnapz.bcast(pyarrow_schema)
    cyln__gsth = [_get_numba_typ_from_pa_typ(cvxg__hxfn, False, True, None)
        [0] for cvxg__hxfn in bqgtg__mkau]
    return col_names, cyln__gsth, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        zrt__qhc = bodo_iceberg_connector.bodo_connector_get_parquet_file_list(
            conn, database_schema, table_name, filters)
    except bodo_iceberg_connector.IcebergError as adox__rkpuk:
        if isinstance(adox__rkpuk, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(f'{adox__rkpuk.message}:\n{adox__rkpuk.java_error}'
                )
        else:
            raise BodoError(adox__rkpuk.message)
    return zrt__qhc


class IcebergParquetDataset(object):

    def __init__(self, conn, database_schema, table_name, pa_table_schema,
        pq_dataset=None):
        self.pq_dataset = pq_dataset
        self.conn = conn
        self.database_schema = database_schema
        self.table_name = table_name
        self.schema = pa_table_schema
        self.pieces = []
        self._bodo_total_rows = 0
        self._prefix = ''
        self.filesystem = None
        if pq_dataset is not None:
            self.pieces = pq_dataset.pieces
            self._bodo_total_rows = pq_dataset._bodo_total_rows
            self._prefix = pq_dataset._prefix
            self.filesystem = pq_dataset.filesystem


def get_iceberg_pq_dataset(conn, database_schema, table_name,
    typing_pa_table_schema, dnf_filters=None, expr_filters=None,
    is_parallel=False):
    saug__yntk = tracing.Event('get_iceberg_pq_dataset')
    zmdkr__rnapz = MPI.COMM_WORLD
    gul__qamo = []
    if bodo.get_rank() == 0:
        ptjm__lyo = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            gul__qamo = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                sjpw__jski = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                ptjm__lyo.add_attribute('num_files', len(gul__qamo))
                ptjm__lyo.add_attribute(f'first_{sjpw__jski}_files', ', '.
                    join(gul__qamo[:sjpw__jski]))
        except Exception as adox__rkpuk:
            gul__qamo = adox__rkpuk
        ptjm__lyo.finalize()
    gul__qamo = zmdkr__rnapz.bcast(gul__qamo)
    if isinstance(gul__qamo, Exception):
        qov__awrcz = gul__qamo
        raise BodoError(
            f"""Error reading Iceberg Table: {type(qov__awrcz).__name__}: {str(qov__awrcz)}
"""
            )
    oaign__joi: List[str] = gul__qamo
    if len(oaign__joi) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(oaign__joi,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as adox__rkpuk:
            if re.search('Schema .* was different', str(adox__rkpuk), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{adox__rkpuk}"""
                    )
            else:
                raise
    hih__nvvq = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    saug__yntk.finalize()
    return hih__nvvq


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        dpnw__cnvb = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        lus__nrof = []
        for bnlw__rzjxj, thixf__mxynv in zip(numba_type.names, numba_type.data
            ):
            owt__ltd, ysr__bvkv = _numba_to_pyarrow_type(thixf__mxynv)
            lus__nrof.append(pa.field(bnlw__rzjxj, owt__ltd, True))
        dpnw__cnvb = pa.struct(lus__nrof)
    elif isinstance(numba_type, DecimalArrayType):
        dpnw__cnvb = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        mkgqw__kino: PDCategoricalDtype = numba_type.dtype
        dpnw__cnvb = pa.dictionary(_numba_to_pyarrow_type(mkgqw__kino.
            int_type)[0], _numba_to_pyarrow_type(mkgqw__kino.elem_type)[0],
            ordered=False if mkgqw__kino.ordered is None else mkgqw__kino.
            ordered)
    elif numba_type == boolean_array:
        dpnw__cnvb = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        dpnw__cnvb = pa.string()
    elif numba_type == binary_array_type:
        dpnw__cnvb = pa.binary()
    elif numba_type == datetime_date_array_type:
        dpnw__cnvb = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        dpnw__cnvb = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        dpnw__cnvb = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return dpnw__cnvb, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    lus__nrof = []
    for bnlw__rzjxj, ftiv__nkpxa in zip(df.columns, df.data):
        try:
            kud__vkryf, fkll__fsnj = _numba_to_pyarrow_type(ftiv__nkpxa)
        except BodoError as adox__rkpuk:
            raise_bodo_error(adox__rkpuk.msg, adox__rkpuk.loc)
        lus__nrof.append(pa.field(bnlw__rzjxj, kud__vkryf, fkll__fsnj))
    return pa.schema(lus__nrof)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        zmdkr__rnapz = MPI.COMM_WORLD
        pru__rfxcb = zmdkr__rnapz.Get_rank()
        file_name = f'{pru__rfxcb:05}-{pru__rfxcb}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    zmdkr__rnapz = MPI.COMM_WORLD
    afb__zqldm = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if zmdkr__rnapz.Get_rank() == 0:
        try:
            (table_loc, iceberg_schema_id, pa_schema, iceberg_schema_str,
                partition_spec, sort_order) = (connector.get_typing_info(
                conn, database_schema, table_name))
            if (if_exists == 'append' and pa_schema is not None and not
                _schemas_equal(pa_schema, df_pyarrow_schema)):
                if numba.core.config.DEVELOPER_MODE:
                    raise BodoError(
                        f"""Iceberg Table and DataFrame Schemas Need to be Equal for Append

Iceberg:
{pa_schema}

DataFrame:
{df_pyarrow_schema}
"""
                        )
                else:
                    raise BodoError(
                        'Iceberg Table and DataFrame Schemas Need to be Equal for Append'
                        )
            if iceberg_schema_id is None:
                iceberg_schema_str = connector.pyarrow_to_iceberg_schema_str(
                    df_pyarrow_schema)
        except connector.IcebergError as adox__rkpuk:
            if isinstance(adox__rkpuk, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                afb__zqldm = BodoError(
                    f'{adox__rkpuk.message}: {adox__rkpuk.java_error}')
            else:
                afb__zqldm = BodoError(adox__rkpuk.message)
        except Exception as adox__rkpuk:
            afb__zqldm = adox__rkpuk
    afb__zqldm = zmdkr__rnapz.bcast(afb__zqldm)
    if isinstance(afb__zqldm, Exception):
        raise afb__zqldm
    table_loc = zmdkr__rnapz.bcast(table_loc)
    iceberg_schema_id = zmdkr__rnapz.bcast(iceberg_schema_id)
    partition_spec = zmdkr__rnapz.bcast(partition_spec)
    sort_order = zmdkr__rnapz.bcast(sort_order)
    iceberg_schema_str = zmdkr__rnapz.bcast(iceberg_schema_str)
    if iceberg_schema_id is None:
        already_exists = False
        iceberg_schema_id = -1
    else:
        already_exists = True
    return (already_exists, table_loc, iceberg_schema_id, partition_spec,
        sort_order, iceberg_schema_str)


def register_table_write(conn_str: str, db_name: str, table_name: str,
    table_loc: str, fnames: List[str], all_metrics: Dict[str, List[Any]],
    iceberg_schema_id: int, pa_schema, partition_spec, sort_order, mode: str):
    import bodo_iceberg_connector
    zmdkr__rnapz = MPI.COMM_WORLD
    success = False
    if zmdkr__rnapz.Get_rank() == 0:
        qbuq__ndse = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, qbuq__ndse,
            pa_schema, partition_spec, sort_order, mode)
    success = zmdkr__rnapz.bcast(success)
    return success


@numba.njit()
def iceberg_write(table_name, conn, database_schema, bodo_table, col_names,
    if_exists, is_parallel, df_pyarrow_schema):
    assert is_parallel, 'Iceberg Write only supported for distributed dataframes'
    with numba.objmode(already_exists='bool_', table_loc='unicode_type',
        iceberg_schema_id='i8', partition_spec='unicode_type', sort_order=
        'unicode_type', iceberg_schema_str='unicode_type'):
        (already_exists, table_loc, iceberg_schema_id, partition_spec,
            sort_order, iceberg_schema_str) = (get_table_details_before_write
            (table_name, conn, database_schema, df_pyarrow_schema, if_exists))
    if already_exists and if_exists == 'fail':
        raise ValueError(f'Table already exists.')
    if already_exists:
        mode = if_exists
    else:
        mode = 'create'
    edw__zoxfi = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    iep__mnwpk = 'snappy'
    lpzsc__hlgz = -1
    plwv__ykqn = np.zeros(1, dtype=np.int64)
    zgtss__rxq = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(edw__zoxfi),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(iep__mnwpk), is_parallel, unicode_to_utf8(
            bucket_region), lpzsc__hlgz, unicode_to_utf8(iceberg_schema_str
            ), plwv__ykqn.ctypes, zgtss__rxq.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        zmdkr__rnapz = MPI.COMM_WORLD
        fnames = zmdkr__rnapz.gather(edw__zoxfi)
        if zmdkr__rnapz.Get_rank() != 0:
            fnames = ['a', 'b']
    qnjuc__ioxz = bodo.gatherv(plwv__ykqn)
    xlh__tpkk = bodo.gatherv(zgtss__rxq)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': xlh__tpkk.tolist(), 'record_count':
            qnjuc__ioxz.tolist()}, iceberg_schema_id, df_pyarrow_schema,
            partition_spec, sort_order, mode)
    if not success:
        raise BodoError('Iceberg write failed.')


import llvmlite.binding as ll
from llvmlite import ir as lir
from numba.core import cgutils, types
if bodo.utils.utils.has_pyarrow():
    from bodo.io import arrow_cpp
    ll.add_symbol('iceberg_pq_write', arrow_cpp.iceberg_pq_write)


@intrinsic
def iceberg_pq_write_table_cpp(typingctx, fname_t, path_name_t, table_t,
    col_names_t, compression_t, is_parallel_t, bucket_region,
    row_group_size, iceberg_metadata_t, record_count_t, file_size_in_bytes_t):

    def codegen(context, builder, sig, args):
        vjb__ktrra = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        pqd__hvdkj = cgutils.get_or_insert_function(builder.module,
            vjb__ktrra, name='iceberg_pq_write')
        builder.call(pqd__hvdkj, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
