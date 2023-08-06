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
    uixfk__zlmyu = urlparse(conn_str)
    if not conn_str.startswith('iceberg+glue') and uixfk__zlmyu.scheme not in (
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
    sprv__whw = schema
    for mgmp__pjfq in range(len(schema)):
        ioqd__uyzit = schema.field(mgmp__pjfq)
        if pa.types.is_floating(ioqd__uyzit.type):
            sprv__whw = sprv__whw.set(mgmp__pjfq, ioqd__uyzit.with_nullable
                (False))
        elif pa.types.is_list(ioqd__uyzit.type):
            sprv__whw = sprv__whw.set(mgmp__pjfq, ioqd__uyzit.with_type(pa.
                list_(pa.field('element', ioqd__uyzit.type.value_type))))
    return sprv__whw


def _schemas_equal(schema: pa.Schema, other: pa.Schema) ->bool:
    if schema.equals(other):
        return True
    oyxmw__nuh = _clean_schema(schema)
    zrz__syxse = _clean_schema(other)
    return oyxmw__nuh.equals(zrz__syxse)


def get_iceberg_type_info(table_name: str, con: str, database_schema: str):
    import bodo_iceberg_connector
    import numba.core
    from bodo.io.parquet_pio import _get_numba_typ_from_pa_typ
    rrsk__xlfi = None
    ngnzr__hvvot = None
    pyarrow_schema = None
    if bodo.get_rank() == 0:
        try:
            rrsk__xlfi, ngnzr__hvvot, pyarrow_schema = (bodo_iceberg_connector
                .get_iceberg_typing_schema(con, database_schema, table_name))
            if pyarrow_schema is None:
                raise BodoError('No such Iceberg table found')
        except bodo_iceberg_connector.IcebergError as udwpt__degt:
            if isinstance(udwpt__degt, bodo_iceberg_connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                rrsk__xlfi = BodoError(
                    f'{udwpt__degt.message}: {udwpt__degt.java_error}')
            else:
                rrsk__xlfi = BodoError(udwpt__degt.message)
    bfn__osb = MPI.COMM_WORLD
    rrsk__xlfi = bfn__osb.bcast(rrsk__xlfi)
    if isinstance(rrsk__xlfi, Exception):
        raise rrsk__xlfi
    col_names = rrsk__xlfi
    ngnzr__hvvot = bfn__osb.bcast(ngnzr__hvvot)
    pyarrow_schema = bfn__osb.bcast(pyarrow_schema)
    dpu__vvxa = [_get_numba_typ_from_pa_typ(shczf__nplgb, False, True, None
        )[0] for shczf__nplgb in ngnzr__hvvot]
    return col_names, dpu__vvxa, pyarrow_schema


def get_iceberg_file_list(table_name: str, conn: str, database_schema: str,
    filters) ->List[str]:
    import bodo_iceberg_connector
    import numba.core
    assert bodo.get_rank(
        ) == 0, 'get_iceberg_file_list should only ever be called on rank 0, as the operation requires access to the py4j server, which is only available on rank 0'
    try:
        cpfsd__akmzg = (bodo_iceberg_connector.
            bodo_connector_get_parquet_file_list(conn, database_schema,
            table_name, filters))
    except bodo_iceberg_connector.IcebergError as udwpt__degt:
        if isinstance(udwpt__degt, bodo_iceberg_connector.IcebergJavaError
            ) and numba.core.config.DEVELOPER_MODE:
            raise BodoError(f'{udwpt__degt.message}:\n{udwpt__degt.java_error}'
                )
        else:
            raise BodoError(udwpt__degt.message)
    return cpfsd__akmzg


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
    euln__zru = tracing.Event('get_iceberg_pq_dataset')
    bfn__osb = MPI.COMM_WORLD
    sclb__pzt = []
    if bodo.get_rank() == 0:
        forgc__vcb = tracing.Event('get_iceberg_file_list', is_parallel=False)
        try:
            sclb__pzt = get_iceberg_file_list(table_name, conn,
                database_schema, dnf_filters)
            if tracing.is_tracing():
                rhjud__bssp = int(os.environ.get(
                    'BODO_ICEBERG_TRACING_NUM_FILES_TO_LOG', '50'))
                forgc__vcb.add_attribute('num_files', len(sclb__pzt))
                forgc__vcb.add_attribute(f'first_{rhjud__bssp}_files', ', '
                    .join(sclb__pzt[:rhjud__bssp]))
        except Exception as udwpt__degt:
            sclb__pzt = udwpt__degt
        forgc__vcb.finalize()
    sclb__pzt = bfn__osb.bcast(sclb__pzt)
    if isinstance(sclb__pzt, Exception):
        dvl__shq = sclb__pzt
        raise BodoError(
            f'Error reading Iceberg Table: {type(dvl__shq).__name__}: {str(dvl__shq)}\n'
            )
    lobnq__keaau: List[str] = sclb__pzt
    if len(lobnq__keaau) == 0:
        pq_dataset = None
    else:
        try:
            pq_dataset = bodo.io.parquet_pio.get_parquet_dataset(lobnq__keaau,
                get_row_counts=True, expr_filters=expr_filters, is_parallel
                =is_parallel, typing_pa_schema=typing_pa_table_schema,
                partitioning=None)
        except BodoError as udwpt__degt:
            if re.search('Schema .* was different', str(udwpt__degt), re.
                IGNORECASE):
                raise BodoError(
                    f"""Bodo currently doesn't support reading Iceberg tables with schema evolution.
{udwpt__degt}"""
                    )
            else:
                raise
    bpd__frxih = IcebergParquetDataset(conn, database_schema, table_name,
        typing_pa_table_schema, pq_dataset)
    euln__zru.finalize()
    return bpd__frxih


_numba_pyarrow_type_map = {types.int8: pa.int8(), types.int16: pa.int16(),
    types.int32: pa.int32(), types.int64: pa.int64(), types.uint8: pa.uint8
    (), types.uint16: pa.uint16(), types.uint32: pa.uint32(), types.uint64:
    pa.uint64(), types.float32: pa.float32(), types.float64: pa.float64(),
    types.NPDatetime('ns'): pa.date64(), bodo.datetime64ns: pa.timestamp(
    'us', 'UTC')}


def _numba_to_pyarrow_type(numba_type: types.ArrayCompatible):
    if isinstance(numba_type, ArrayItemArrayType):
        qisvj__jdtf = pa.list_(_numba_to_pyarrow_type(numba_type.dtype)[0])
    elif isinstance(numba_type, StructArrayType):
        ywmg__vpv = []
        for algc__nvj, yqqjc__dpj in zip(numba_type.names, numba_type.data):
            bdru__qfx, bptuc__ahztp = _numba_to_pyarrow_type(yqqjc__dpj)
            ywmg__vpv.append(pa.field(algc__nvj, bdru__qfx, True))
        qisvj__jdtf = pa.struct(ywmg__vpv)
    elif isinstance(numba_type, DecimalArrayType):
        qisvj__jdtf = pa.decimal128(numba_type.precision, numba_type.scale)
    elif isinstance(numba_type, CategoricalArrayType):
        bpyv__cgkq: PDCategoricalDtype = numba_type.dtype
        qisvj__jdtf = pa.dictionary(_numba_to_pyarrow_type(bpyv__cgkq.
            int_type)[0], _numba_to_pyarrow_type(bpyv__cgkq.elem_type)[0],
            ordered=False if bpyv__cgkq.ordered is None else bpyv__cgkq.ordered
            )
    elif numba_type == boolean_array:
        qisvj__jdtf = pa.bool_()
    elif numba_type in (string_array_type, bodo.dict_str_arr_type):
        qisvj__jdtf = pa.string()
    elif numba_type == binary_array_type:
        qisvj__jdtf = pa.binary()
    elif numba_type == datetime_date_array_type:
        qisvj__jdtf = pa.date32()
    elif isinstance(numba_type, bodo.DatetimeArrayType):
        qisvj__jdtf = pa.timestamp('us', 'UTC')
    elif isinstance(numba_type, (types.Array, IntegerArrayType)
        ) and numba_type.dtype in _numba_pyarrow_type_map:
        qisvj__jdtf = _numba_pyarrow_type_map[numba_type.dtype]
    else:
        raise BodoError(
            'Conversion from Bodo array type {} to PyArrow type not supported yet'
            .format(numba_type))
    return qisvj__jdtf, is_nullable(numba_type)


def pyarrow_schema(df: DataFrameType) ->pa.Schema:
    ywmg__vpv = []
    for algc__nvj, dmyhc__haxqs in zip(df.columns, df.data):
        try:
            chm__nipx, gtjs__hffc = _numba_to_pyarrow_type(dmyhc__haxqs)
        except BodoError as udwpt__degt:
            raise_bodo_error(udwpt__degt.msg, udwpt__degt.loc)
        ywmg__vpv.append(pa.field(algc__nvj, chm__nipx, gtjs__hffc))
    return pa.schema(ywmg__vpv)


@numba.njit
def gen_iceberg_pq_fname():
    with numba.objmode(file_name='unicode_type'):
        bfn__osb = MPI.COMM_WORLD
        bbswx__klmfi = bfn__osb.Get_rank()
        file_name = f'{bbswx__klmfi:05}-{bbswx__klmfi}-{uuid4()}.parquet'
    return file_name


def get_table_details_before_write(table_name: str, conn: str,
    database_schema: str, df_pyarrow_schema, if_exists: str):
    import bodo_iceberg_connector as connector
    bfn__osb = MPI.COMM_WORLD
    tio__oxh = None
    iceberg_schema_id = None
    table_loc = ''
    partition_spec = ''
    sort_order = ''
    iceberg_schema_str = ''
    if bfn__osb.Get_rank() == 0:
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
        except connector.IcebergError as udwpt__degt:
            if isinstance(udwpt__degt, connector.IcebergJavaError
                ) and numba.core.config.DEVELOPER_MODE:
                tio__oxh = BodoError(
                    f'{udwpt__degt.message}: {udwpt__degt.java_error}')
            else:
                tio__oxh = BodoError(udwpt__degt.message)
        except Exception as udwpt__degt:
            tio__oxh = udwpt__degt
    tio__oxh = bfn__osb.bcast(tio__oxh)
    if isinstance(tio__oxh, Exception):
        raise tio__oxh
    table_loc = bfn__osb.bcast(table_loc)
    iceberg_schema_id = bfn__osb.bcast(iceberg_schema_id)
    partition_spec = bfn__osb.bcast(partition_spec)
    sort_order = bfn__osb.bcast(sort_order)
    iceberg_schema_str = bfn__osb.bcast(iceberg_schema_str)
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
    bfn__osb = MPI.COMM_WORLD
    success = False
    if bfn__osb.Get_rank() == 0:
        acyo__letuv = None if iceberg_schema_id < 0 else iceberg_schema_id
        success = bodo_iceberg_connector.commit_write(conn_str, db_name,
            table_name, table_loc, fnames, all_metrics, acyo__letuv,
            pa_schema, partition_spec, sort_order, mode)
    success = bfn__osb.bcast(success)
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
    qmycu__tdu = gen_iceberg_pq_fname()
    bucket_region = get_s3_bucket_region_njit(table_loc, is_parallel)
    kvwv__clx = 'snappy'
    ccbl__ihzcs = -1
    babn__ssax = np.zeros(1, dtype=np.int64)
    lqe__afx = np.zeros(1, dtype=np.int64)
    if not partition_spec and not sort_order:
        iceberg_pq_write_table_cpp(unicode_to_utf8(qmycu__tdu),
            unicode_to_utf8(table_loc), bodo_table, col_names,
            unicode_to_utf8(kvwv__clx), is_parallel, unicode_to_utf8(
            bucket_region), ccbl__ihzcs, unicode_to_utf8(iceberg_schema_str
            ), babn__ssax.ctypes, lqe__afx.ctypes)
    else:
        raise Exception('Partition Spec and Sort Order not supported yet.')
    with numba.objmode(fnames='types.List(types.unicode_type)'):
        bfn__osb = MPI.COMM_WORLD
        fnames = bfn__osb.gather(qmycu__tdu)
        if bfn__osb.Get_rank() != 0:
            fnames = ['a', 'b']
    verca__lbhw = bodo.gatherv(babn__ssax)
    ipe__qavke = bodo.gatherv(lqe__afx)
    with numba.objmode(success='bool_'):
        success = register_table_write(conn, database_schema, table_name,
            table_loc, fnames, {'size': ipe__qavke.tolist(), 'record_count':
            verca__lbhw.tolist()}, iceberg_schema_id, df_pyarrow_schema,
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
        plae__mkjfa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(8).as_pointer(), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        weky__dnrlx = cgutils.get_or_insert_function(builder.module,
            plae__mkjfa, name='iceberg_pq_write')
        builder.call(weky__dnrlx, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, types.voidptr, table_t, col_names_t,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.
        voidptr, types.voidptr, types.voidptr), codegen
