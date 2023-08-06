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
    agiz__bek = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and agiz__bek.scheme not in (
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
    ume__togi = schema
    for tyohr__dhjl in range(len(schema)):
        fre__mzsfn = schema.field(tyohr__dhjl)
        if pa.types.is_floating(fre__mzsfn.type):
            ume__togi = ume__togi.set(tyohr__dhjl, fre__mzsfn.with_nullable
                (False))
        elif pa.types.is_list(fre__mzsfn.type):
            ume__togi = ume__togi.set(tyohr__dhjl, fre__mzsfn.with_type(pa.
                list_(pa.field('element', fre__mzsfn.type.value_type))))
    return ume__togi


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    ipwke__lacxv = _clean_schema(schema)
    vuqs__vyg = _clean_schema(other)
    return ipwke__lacxv.equals(vuqs__vyg)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    pfq__msca = None
    axqh__vzpa = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            pfq__msca, axqh__vzpa, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as dud__wmd:
            if isinstance(dud__wmd, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                pfq__msca = BodoError(
                    f'{dud__wmd.message}: {dud__wmd.java_error}')
            else:
                pfq__msca = BodoError(dud__wmd.message)
    jqd__dqy = MPI.COMM_WORLD
    pfq__msca = jqd__dqy.bcast(pfq__msca)
    if isinstance(pfq__msca, Exception):
        raise pfq__msca
    col_names = pfq__msca
    axqh__vzpa = jqd__dqy.bcast(axqh__vzpa)
    pyarrow_schema = jqd__dqy.bcast(pyarrow_schema)
    cyxkp__qwh = [_get_numba_typ_from_pa_typ(ikcpb__ckvaa, False, True,
        None)[0] for ikcpb__ckvaa in axqh__vzpa]
    return col_names, cyxkp__qwh, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        wbcxe__zsjty = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as dud__wmd:
        if isinstance(dud__wmd, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(f'{dud__wmd.message}:\n{dud__wmd.java_error}')
        else:
            raise BodoError(dud__wmd.message)
    return wbcxe__zsjty


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
    lmnx__fdgtt = tracing.Event('get_iceberg_pq_dataset')
    jqd__dqy = MPI.COMM_WORLD
    vjq__taj = []
    if bodo.get_rank() == 0:
        qfhh__igkyu = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            vjq__taj = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                fzum__ijoo = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                qfhh__igkyu.add_attribute('num_files', len(vjq__taj))
                qfhh__igkyu.add_attribute(f'first_{fzum__ijoo}_files', ', '
                    .join(vjq__taj[:fzum__ijoo]))
        except Exception as dud__wmd:
            vjq__taj = dud__wmd
        qfhh__igkyu.finalize()
    vjq__taj = jqd__dqy.bcast(vjq__taj)
    if isinstance(vjq__taj, Exception):
        bmj__dbh = vjq__taj
        raise BodoError(
            f'Error reading Iceberg Table: {type(bmj__dbh).__name__}: {str(bmj__dbh)}\n'
            )
    hpz__drv: List[str] = vjq__taj
    if len(hpz__drv) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(hpz__drv,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as dud__wmd:
            if re.search('Schema .* was different', str(dud__wmd), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{dud__wmd}"""
                    )
            else:
                raise
    swlp__luyg = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    lmnx__fdgtt.finalize()
    return swlp__luyg


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        kitqv__qahjs = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        xev__kpfc = []
        for vrn__vfky, wkp__fuzlc in zip(numba_type.names, numba_type.data):
            nfic__atj, koadt__uwn = _numba_to_pyarrow_type(wkp__fuzlc)
            xev__kpfc.append(pa.field(vrn__vfky, nfic__atj, True))
        kitqv__qahjs = pa.struct(xev__kpfc)
    elif isinstance(numba_type, DecimalArrayType):
        kitqv__qahjs = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        flk__sxdj: PDCategoricalDtype = numba_type.dtype
        kitqv__qahjs = pa.dictionary(_numba_to_pyarrow_type(flk__sxdj.
            int_type)[0], _numba_to_pyarrow_type(flk__sxdj.elem_type)[0],
            ordered=False if flk__sxdj.ordered is None else flk__sxdj.ordered)
    elif numba_type == boolean_array:
        kitqv__qahjs = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        kitqv__qahjs = pa.string()
    elif numba_type == binary_array_type:
        kitqv__qahjs = pa.binary()
    elif numba_type == datetime_date_array_type:
        kitqv__qahjs = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        kitqv__qahjs = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        kitqv__qahjs = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return kitqv__qahjs, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    xev__kpfc = []
    for vrn__vfky, gamt__rtia in zip(df.columns, df.data):
        try:
            ecx__xgmp, rzqh__qmn = _numba_to_pyarrow_type(gamt__rtia)
        except BodoError as dud__wmd:
            raise_bodo_error(dud__wmd.msg, dud__wmd.loc)
        xev__kpfc.append(pa.field(vrn__vfky, ecx__xgmp, rzqh__qmn))
    return pa.schema(xev__kpfc)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        jqd__dqy = MPI.COMM_WORLD
        objc__obw = jqd__dqy.Get_rank()
        file_name = f'{objc__obw:05}-{objc__obw}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    jqd__dqy = MPI.COMM_WORLD
    fuiv__fnfbz = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if jqd__dqy.Get_rank() == 0:
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
        except connector.IcebergError as dud__wmd:
            if isinstance(dud__wmd, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                fuiv__fnfbz = BodoError(
                    f'{dud__wmd.message}: {dud__wmd.java_error}')
            else:
                fuiv__fnfbz = BodoError(dud__wmd.message)
        except Exception as dud__wmd:
            fuiv__fnfbz = dud__wmd
    fuiv__fnfbz = jqd__dqy.bcast(fuiv__fnfbz)
    if isinstance(fuiv__fnfbz, Exception):
        raise fuiv__fnfbz
    table_loc = jqd__dqy.bcast(table_loc)
    iceberg_schema_id = jqd__dqy.bcast(iceberg_schema_id)
    partition_spec = jqd__dqy.bcast(partition_spec)
    sort_order = jqd__dqy.bcast(sort_order)
    iceberg_schema_str = jqd__dqy.bcast(iceberg_schema_str)
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
    jqd__dqy = MPI.COMM_WORLD
    success = False
    if jqd__dqy.Get_rank() == 0:
        ewq__cxly = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, ewq__cxly,
            pa_schema, partition_spec, sort_order, mode)
    success = jqd__dqy.bcast(success)
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
    kixy__vjbw = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    nyf__nejw = 'snappy'
    jwkb__lgnys = -1
    chdpr__qrqrg = np.zeros(1, dtype=np.int64)
    pliq__wnvjs = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(kixy__vjbw),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(nyf__nejw), is_parallel, unicode_to_utf8(
            bucket_region), jwkb__lgnys, unicode_to_utf8(iceberg_schema_str
            ), chdpr__qrqrg.ctypes, pliq__wnvjs.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        jqd__dqy = MPI.COMM_WORLD
        fnames = jqd__dqy.gather(kixy__vjbw)
        if jqd__dqy.Get_rank() != 0:
            fnames = ['a', 'b']
    kqabb__svdrn = bodo.gatherv(chdpr__qrqrg)
    cfzqx__gsc = bodo.gatherv(pliq__wnvjs)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': cfzqx__gsc.tolist(), 'record_count':
            kqabb__svdrn.tolist()}, iceberg_schema_id, df_pyarrow_schema,
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
        wanej__rplpb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        kha__cagbf = cgutils.get_or_insert_function(builder.module,
            wanej__rplpb, name='iceberg_pq_write')
        builder.call(kha__cagbf, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
