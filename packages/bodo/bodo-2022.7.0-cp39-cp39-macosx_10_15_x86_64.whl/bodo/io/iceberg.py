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
    ldka__vqnf = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and ldka__vqnf.scheme not in (
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
    sxt__wabqi = schema
    for dqwt__jbq in range(len(schema)):
        ltq__wxfl = schema.field(dqwt__jbq)
        if pa.types.is_floating(ltq__wxfl.type):
            sxt__wabqi = sxt__wabqi.set(dqwt__jbq, ltq__wxfl.with_nullable(
                False))
        elif pa.types.is_list(ltq__wxfl.type):
            sxt__wabqi = sxt__wabqi.set(dqwt__jbq, ltq__wxfl.with_type(pa.
                list_(pa.field('element', ltq__wxfl.type.value_type))))
    return sxt__wabqi


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    femfp__cxaib = _clean_schema(schema)
    xnx__trre = _clean_schema(other)
    return femfp__cxaib.equals(xnx__trre)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    troby__slv = None
    pacz__icme = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            troby__slv, pacz__icme, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as ptp__mszvr:
            if isinstance(ptp__mszvr, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                troby__slv = BodoError(
                    f'{ptp__mszvr.message}: {ptp__mszvr.java_error}')
            else:
                troby__slv = BodoError(ptp__mszvr.message)
    ityh__yonk = MPI.COMM_WORLD
    troby__slv = ityh__yonk.bcast(troby__slv)
    if isinstance(troby__slv, Exception):
        raise troby__slv
    col_names = troby__slv
    pacz__icme = ityh__yonk.bcast(pacz__icme)
    pyarrow_schema = ityh__yonk.bcast(pyarrow_schema)
    daf__vogek = [_get_numba_typ_from_pa_typ(aog__wdc, False, True, None)[0
        ] for aog__wdc in pacz__icme]
    return col_names, daf__vogek, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        ukb__zalp = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as ptp__mszvr:
        if isinstance(ptp__mszvr, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(f'{ptp__mszvr.message}:\n{ptp__mszvr.java_error}')
        else:
            raise BodoError(ptp__mszvr.message)
    return ukb__zalp


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
    pffcf__gjy = tracing.Event('get_iceberg_pq_dataset')
    ityh__yonk = MPI.COMM_WORLD
    abyr__yuuj = []
    if bodo.get_rank() == 0:
        cimy__zaf = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            abyr__yuuj = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                sqxc__zqsj = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                cimy__zaf.add_attribute('num_files', len(abyr__yuuj))
                cimy__zaf.add_attribute(f'first_{sqxc__zqsj}_files', ', '.
                    join(abyr__yuuj[:sqxc__zqsj]))
        except Exception as ptp__mszvr:
            abyr__yuuj = ptp__mszvr
        cimy__zaf.finalize()
    abyr__yuuj = ityh__yonk.bcast(abyr__yuuj)
    if isinstance(abyr__yuuj, Exception):
        kbtfb__uedti = abyr__yuuj
        raise BodoError(
            f"""Error reading Iceberg Table: {type(kbtfb__uedti).__name__}: {str(kbtfb__uedti)}
"""
            )
    bjlc__pilje: List[str] = abyr__yuuj
    if len(bjlc__pilje) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(bjlc__pilje,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as ptp__mszvr:
            if re.search('Schema .* was different', str(ptp__mszvr), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{ptp__mszvr}"""
                    )
            else:
                raise
    xhd__qzm = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    pffcf__gjy.finalize()
    return xhd__qzm


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        lyb__dknk = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        gmax__kttmi = []
        for qzab__xli, gur__uqvq in zip(numba_type.names, numba_type.data):
            hvy__gets, zqqxm__zwzlp = _numba_to_pyarrow_type(gur__uqvq)
            gmax__kttmi.append(pa.field(qzab__xli, hvy__gets, True))
        lyb__dknk = pa.struct(gmax__kttmi)
    elif isinstance(numba_type, DecimalArrayType):
        lyb__dknk = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        orzs__ybinn: PDCategoricalDtype = numba_type.dtype
        lyb__dknk = pa.dictionary(_numba_to_pyarrow_type(orzs__ybinn.
            int_type)[0], _numba_to_pyarrow_type(orzs__ybinn.elem_type)[0],
            ordered=False if orzs__ybinn.ordered is None else orzs__ybinn.
            ordered)
    elif numba_type == boolean_array:
        lyb__dknk = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        lyb__dknk = pa.string()
    elif numba_type == binary_array_type:
        lyb__dknk = pa.binary()
    elif numba_type == datetime_date_array_type:
        lyb__dknk = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        lyb__dknk = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        lyb__dknk = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return lyb__dknk, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    gmax__kttmi = []
    for qzab__xli, wva__vfqaf in zip(df.columns, df.data):
        try:
            gqi__vbbu, yoeu__ssq = _numba_to_pyarrow_type(wva__vfqaf)
        except BodoError as ptp__mszvr:
            raise_bodo_error(ptp__mszvr.msg, ptp__mszvr.loc)
        gmax__kttmi.append(pa.field(qzab__xli, gqi__vbbu, yoeu__ssq))
    return pa.schema(gmax__kttmi)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        ityh__yonk = MPI.COMM_WORLD
        jab__utvy = ityh__yonk.Get_rank()
        file_name = f'{jab__utvy:05}-{jab__utvy}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    ityh__yonk = MPI.COMM_WORLD
    fmz__drrqu = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if ityh__yonk.Get_rank() == 0:
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
        except connector.IcebergError as ptp__mszvr:
            if isinstance(ptp__mszvr, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                fmz__drrqu = BodoError(
                    f'{ptp__mszvr.message}: {ptp__mszvr.java_error}')
            else:
                fmz__drrqu = BodoError(ptp__mszvr.message)
        except Exception as ptp__mszvr:
            fmz__drrqu = ptp__mszvr
    fmz__drrqu = ityh__yonk.bcast(fmz__drrqu)
    if isinstance(fmz__drrqu, Exception):
        raise fmz__drrqu
    table_loc = ityh__yonk.bcast(table_loc)
    iceberg_schema_id = ityh__yonk.bcast(iceberg_schema_id)
    partition_spec = ityh__yonk.bcast(partition_spec)
    sort_order = ityh__yonk.bcast(sort_order)
    iceberg_schema_str = ityh__yonk.bcast(iceberg_schema_str)
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
    ityh__yonk = MPI.COMM_WORLD
    success = False
    if ityh__yonk.Get_rank() == 0:
        aiy__yuhmn = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, aiy__yuhmn,
            pa_schema, partition_spec, sort_order, mode)
    success = ityh__yonk.bcast(success)
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
    tfj__wntyl = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    yaebk__wqosf = 'snappy'
    lwu__axqi = -1
    ddmgj__oezjv = np.zeros(1, dtype=np.int64)
    lrqnx__luia = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(tfj__wntyl),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(yaebk__wqosf), is_parallel, unicode_to_utf8(
            bucket_region), lwu__axqi, unicode_to_utf8(iceberg_schema_str),
            ddmgj__oezjv.ctypes, lrqnx__luia.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        ityh__yonk = MPI.COMM_WORLD
        fnames = ityh__yonk.gather(tfj__wntyl)
        if ityh__yonk.Get_rank() != 0:
            fnames = ['a', 'b']
    ljq__gptkt = bodo.gatherv(ddmgj__oezjv)
    wlyn__lhl = bodo.gatherv(lrqnx__luia)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': wlyn__lhl.tolist(), 'record_count':
            ljq__gptkt.tolist()}, iceberg_schema_id, df_pyarrow_schema,
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
        vxd__dxelh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        jbd__jig = cgutils.get_or_insert_function(builder.module,
            vxd__dxelh, name='iceberg_pq_write')
        builder.call(jbd__jig, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
