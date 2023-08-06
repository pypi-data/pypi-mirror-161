import os
import warnings
from collections import defaultdict
from glob import has_magic
from urllib.parse import urlparse
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow
import pyarrow as pa
import pyarrow.dataset as ds
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, get_definition, guard, mk_unique_var, next_label, replace_arg_nodes
from numba.extending import NativeValue, box, intrinsic, models, overload, register_model, unbox
from pyarrow._fs import PyFileSystem
from pyarrow.fs import FSSpecHandler
import bodo
import bodo.ir.parquet_ext
import bodo.utils.tracing as tracing
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import TableType
from bodo.io.fs_io import get_hdfs_fs, get_s3_fs_from_path, get_storage_options_pyobject, storage_options_dict_type
from bodo.io.helpers import _get_numba_typ_from_pa_typ, is_nullable
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.dict_arr_ext import dict_str_arr_type
from bodo.libs.distributed_api import get_end, get_start
from bodo.libs.str_ext import unicode_to_utf8
from bodo.transforms import distributed_pass
from bodo.utils.transform import get_const_value
from bodo.utils.typing import BodoError, BodoWarning, FileInfo, get_overload_const_str
from bodo.utils.utils import check_and_propagate_cpp_exception, numba_to_c_type, sanitize_varname
REMOTE_FILESYSTEMS = {'s3', 'gcs', 'gs', 'http', 'hdfs', 'abfs', 'abfss'}
READ_STR_AS_DICT_THRESHOLD = 1.0
list_of_files_error_msg = (
    '. Make sure the list/glob passed to read_parquet() only contains paths to files (no directories)'
    )


class ParquetPredicateType(types.Type):

    def __init__(self):
        super(ParquetPredicateType, self).__init__(name=
            'ParquetPredicateType()')


parquet_predicate_type = ParquetPredicateType()
types.parquet_predicate_type = parquet_predicate_type
register_model(ParquetPredicateType)(models.OpaqueModel)


@unbox(ParquetPredicateType)
def unbox_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


@box(ParquetPredicateType)
def box_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return val


class ReadParquetFilepathType(types.Opaque):

    def __init__(self):
        super(ReadParquetFilepathType, self).__init__(name=
            'ReadParquetFilepathType')


read_parquet_fpath_type = ReadParquetFilepathType()
types.read_parquet_fpath_type = read_parquet_fpath_type
register_model(ReadParquetFilepathType)(models.OpaqueModel)


@unbox(ReadParquetFilepathType)
def unbox_read_parquet_fpath_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class ParquetFileInfo(FileInfo):

    def __init__(self, columns, storage_options=None, input_file_name_col=
        None, read_as_dict_cols=None):
        self.columns = columns
        self.storage_options = storage_options
        self.input_file_name_col = input_file_name_col
        self.read_as_dict_cols = read_as_dict_cols
        super().__init__()

    def _get_schema(self, fname):
        try:
            return parquet_file_schema(fname, selected_columns=self.columns,
                storage_options=self.storage_options, input_file_name_col=
                self.input_file_name_col, read_as_dict_cols=self.
                read_as_dict_cols)
        except OSError as mawys__iun:
            if 'non-file path' in str(mawys__iun):
                raise FileNotFoundError(str(mawys__iun))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        oqk__qbqn = lhs.scope
        ugtx__iirrf = lhs.loc
        yzdta__dhqe = None
        if lhs.name in self.locals:
            yzdta__dhqe = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        zjz__qnyro = {}
        if lhs.name + ':convert' in self.locals:
            zjz__qnyro = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if yzdta__dhqe is None:
            zbmgn__svui = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            rwnos__qssjn = get_const_value(file_name, self.func_ir,
                zbmgn__svui, arg_types=self.args, file_info=ParquetFileInfo
                (columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            aaeg__ehqj = False
            dhw__qkx = guard(get_definition, self.func_ir, file_name)
            if isinstance(dhw__qkx, ir.Arg):
                typ = self.args[dhw__qkx.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, zhlxc__efi, ebr__lnygi, col_indices,
                        partition_names, cyyt__xvgw, gff__xgy) = typ.schema
                    aaeg__ehqj = True
            if not aaeg__ehqj:
                (col_names, zhlxc__efi, ebr__lnygi, col_indices,
                    partition_names, cyyt__xvgw, gff__xgy) = (
                    parquet_file_schema(rwnos__qssjn, columns,
                    storage_options=storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            ryd__fnph = list(yzdta__dhqe.keys())
            xuooq__qry = {c: rro__bhmsm for rro__bhmsm, c in enumerate(
                ryd__fnph)}
            gsj__zlogn = [zxpm__xbeb for zxpm__xbeb in yzdta__dhqe.values()]
            ebr__lnygi = 'index' if 'index' in xuooq__qry else None
            if columns is None:
                selected_columns = ryd__fnph
            else:
                selected_columns = columns
            col_indices = [xuooq__qry[c] for c in selected_columns]
            zhlxc__efi = [gsj__zlogn[xuooq__qry[c]] for c in selected_columns]
            col_names = selected_columns
            ebr__lnygi = ebr__lnygi if ebr__lnygi in col_names else None
            partition_names = []
            cyyt__xvgw = []
            gff__xgy = []
        eavhr__khpo = None if isinstance(ebr__lnygi, dict
            ) or ebr__lnygi is None else ebr__lnygi
        index_column_index = None
        index_column_type = types.none
        if eavhr__khpo:
            yhung__sqckt = col_names.index(eavhr__khpo)
            index_column_index = col_indices.pop(yhung__sqckt)
            index_column_type = zhlxc__efi.pop(yhung__sqckt)
            col_names.pop(yhung__sqckt)
        for rro__bhmsm, c in enumerate(col_names):
            if c in zjz__qnyro:
                zhlxc__efi[rro__bhmsm] = zjz__qnyro[c]
        ujs__uvfwg = [ir.Var(oqk__qbqn, mk_unique_var('pq_table'),
            ugtx__iirrf), ir.Var(oqk__qbqn, mk_unique_var('pq_index'),
            ugtx__iirrf)]
        urjk__nnhku = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.
            name, col_names, col_indices, zhlxc__efi, ujs__uvfwg,
            ugtx__iirrf, partition_names, storage_options,
            index_column_index, index_column_type, input_file_name_col,
            cyyt__xvgw, gff__xgy)]
        return (col_names, ujs__uvfwg, ebr__lnygi, urjk__nnhku, zhlxc__efi,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    apkp__nah = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    lnysh__xvmc, lrcv__kgsw = bodo.ir.connector.generate_filter_map(pq_node
        .filters)
    extra_args = ', '.join(lnysh__xvmc.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, lnysh__xvmc, lrcv__kgsw, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    ngghp__rmw = ', '.join(f'out{rro__bhmsm}' for rro__bhmsm in range(
        apkp__nah))
    cpgq__aadzo = f'def pq_impl(fname, {extra_args}):\n'
    cpgq__aadzo += (
        f'    (total_rows, {ngghp__rmw},) = _pq_reader_py(fname, {extra_args})\n'
        )
    cak__auex = {}
    exec(cpgq__aadzo, {}, cak__auex)
    kzjws__svds = cak__auex['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        dbfq__sft = pq_node.loc.strformat()
        mxbr__blfc = []
        ecdu__yugh = []
        for rro__bhmsm in pq_node.out_used_cols:
            mtps__txv = pq_node.df_colnames[rro__bhmsm]
            mxbr__blfc.append(mtps__txv)
            if isinstance(pq_node.out_types[rro__bhmsm], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                ecdu__yugh.append(mtps__txv)
        wzjmo__dav = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', wzjmo__dav,
            dbfq__sft, mxbr__blfc)
        if ecdu__yugh:
            bxa__dko = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', bxa__dko,
                dbfq__sft, ecdu__yugh)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        vnaso__jlzy = set(pq_node.out_used_cols)
        hrfoz__iki = set(pq_node.unsupported_columns)
        guhz__tpu = vnaso__jlzy & hrfoz__iki
        if guhz__tpu:
            mrum__qcech = sorted(guhz__tpu)
            zfqb__vtzug = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            kqqj__oaqap = 0
            for rnxi__imogp in mrum__qcech:
                while pq_node.unsupported_columns[kqqj__oaqap] != rnxi__imogp:
                    kqqj__oaqap += 1
                zfqb__vtzug.append(
                    f"Column '{pq_node.df_colnames[rnxi__imogp]}' with unsupported arrow type {pq_node.unsupported_arrow_types[kqqj__oaqap]}"
                    )
                kqqj__oaqap += 1
            ydl__jvmp = '\n'.join(zfqb__vtzug)
            raise BodoError(ydl__jvmp, loc=pq_node.loc)
    xcgdq__bqmfu = _gen_pq_reader_py(pq_node.df_colnames, pq_node.
        col_indices, pq_node.out_used_cols, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    tamtb__vkfrk = typemap[pq_node.file_name.name]
    wup__jautw = (tamtb__vkfrk,) + tuple(typemap[kkuww__rorw.name] for
        kkuww__rorw in lrcv__kgsw)
    gjml__qkbkl = compile_to_numba_ir(kzjws__svds, {'_pq_reader_py':
        xcgdq__bqmfu}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        wup__jautw, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(gjml__qkbkl, [pq_node.file_name] + lrcv__kgsw)
    urjk__nnhku = gjml__qkbkl.body[:-3]
    if meta_head_only_info:
        urjk__nnhku[-3].target = meta_head_only_info[1]
    urjk__nnhku[-2].target = pq_node.out_vars[0]
    urjk__nnhku[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        urjk__nnhku.pop(-1)
    elif not pq_node.out_used_cols:
        urjk__nnhku.pop(-2)
    return urjk__nnhku


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    dqss__mmyvr = get_overload_const_str(dnf_filter_str)
    lsdl__fyw = get_overload_const_str(expr_filter_str)
    chr__ami = ', '.join(f'f{rro__bhmsm}' for rro__bhmsm in range(len(var_tup))
        )
    cpgq__aadzo = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        cpgq__aadzo += f'  {chr__ami}, = var_tup\n'
    cpgq__aadzo += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    cpgq__aadzo += f'    dnf_filters_py = {dqss__mmyvr}\n'
    cpgq__aadzo += f'    expr_filters_py = {lsdl__fyw}\n'
    cpgq__aadzo += '  return (dnf_filters_py, expr_filters_py)\n'
    cak__auex = {}
    exec(cpgq__aadzo, globals(), cak__auex)
    return cak__auex['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    vdw__mqsw = next_label()
    yml__eqpd = ',' if extra_args else ''
    cpgq__aadzo = f'def pq_reader_py(fname,{extra_args}):\n'
    cpgq__aadzo += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    cpgq__aadzo += f"    ev.add_attribute('g_fname', fname)\n"
    cpgq__aadzo += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{yml__eqpd}))
"""
    cpgq__aadzo += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    cpgq__aadzo += f"""    storage_options_py = get_storage_options_pyobject({str(storage_options)})
"""
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    rmafu__ebcck = not out_used_cols
    cydvq__nws = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    obr__oqqzr = {c: rro__bhmsm for rro__bhmsm, c in enumerate(col_indices)}
    cox__rfkhu = {c: rro__bhmsm for rro__bhmsm, c in enumerate(cydvq__nws)}
    eaic__qsyi = []
    jpwbt__pglxm = set()
    gnfm__uycbl = partition_names + [input_file_name_col]
    for rro__bhmsm in out_used_cols:
        if cydvq__nws[rro__bhmsm] not in gnfm__uycbl:
            eaic__qsyi.append(col_indices[rro__bhmsm])
        elif not input_file_name_col or cydvq__nws[rro__bhmsm
            ] != input_file_name_col:
            jpwbt__pglxm.add(col_indices[rro__bhmsm])
    if index_column_index is not None:
        eaic__qsyi.append(index_column_index)
    eaic__qsyi = sorted(eaic__qsyi)
    ioup__fia = {c: rro__bhmsm for rro__bhmsm, c in enumerate(eaic__qsyi)}
    usmbt__alkg = [(int(is_nullable(out_types[obr__oqqzr[gtiy__xeac]])) if 
        gtiy__xeac != index_column_index else int(is_nullable(
        index_column_type))) for gtiy__xeac in eaic__qsyi]
    str_as_dict_cols = []
    for gtiy__xeac in eaic__qsyi:
        if gtiy__xeac == index_column_index:
            zxpm__xbeb = index_column_type
        else:
            zxpm__xbeb = out_types[obr__oqqzr[gtiy__xeac]]
        if zxpm__xbeb == dict_str_arr_type:
            str_as_dict_cols.append(gtiy__xeac)
    hinit__foi = []
    fro__ozow = {}
    tsyh__rhnd = []
    pykip__qero = []
    for rro__bhmsm, iqad__edrjr in enumerate(partition_names):
        try:
            ogm__sjmbn = cox__rfkhu[iqad__edrjr]
            if col_indices[ogm__sjmbn] not in jpwbt__pglxm:
                continue
        except (KeyError, ValueError) as tsese__pmji:
            continue
        fro__ozow[iqad__edrjr] = len(hinit__foi)
        hinit__foi.append(iqad__edrjr)
        tsyh__rhnd.append(rro__bhmsm)
        lrfa__wuez = out_types[ogm__sjmbn].dtype
        xygzs__nokt = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            lrfa__wuez)
        pykip__qero.append(numba_to_c_type(xygzs__nokt))
    cpgq__aadzo += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    cpgq__aadzo += f'    out_table = pq_read(\n'
    cpgq__aadzo += f'        fname_py, {is_parallel},\n'
    cpgq__aadzo += f'        dnf_filters, expr_filters,\n'
    cpgq__aadzo += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{vdw__mqsw}.ctypes,
"""
    cpgq__aadzo += f'        {len(eaic__qsyi)},\n'
    cpgq__aadzo += f'        nullable_cols_arr_{vdw__mqsw}.ctypes,\n'
    if len(tsyh__rhnd) > 0:
        cpgq__aadzo += (
            f'        np.array({tsyh__rhnd}, dtype=np.int32).ctypes,\n')
        cpgq__aadzo += (
            f'        np.array({pykip__qero}, dtype=np.int32).ctypes,\n')
        cpgq__aadzo += f'        {len(tsyh__rhnd)},\n'
    else:
        cpgq__aadzo += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        cpgq__aadzo += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        cpgq__aadzo += f'        0, 0,\n'
    cpgq__aadzo += f'        total_rows_np.ctypes,\n'
    cpgq__aadzo += f'        {input_file_name_col is not None},\n'
    cpgq__aadzo += f'    )\n'
    cpgq__aadzo += f'    check_and_propagate_cpp_exception()\n'
    lij__okpd = 'None'
    alpz__sjly = index_column_type
    spou__smez = TableType(tuple(out_types))
    if rmafu__ebcck:
        spou__smez = types.none
    if index_column_index is not None:
        poq__wfi = ioup__fia[index_column_index]
        lij__okpd = (
            f'info_to_array(info_from_table(out_table, {poq__wfi}), index_arr_type)'
            )
    cpgq__aadzo += f'    index_arr = {lij__okpd}\n'
    if rmafu__ebcck:
        mfhe__zpz = None
    else:
        mfhe__zpz = []
        tmild__svktx = 0
        easvr__msanb = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for rro__bhmsm, rnxi__imogp in enumerate(col_indices):
            if tmild__svktx < len(out_used_cols
                ) and rro__bhmsm == out_used_cols[tmild__svktx]:
                okob__ttovf = col_indices[rro__bhmsm]
                if easvr__msanb and okob__ttovf == easvr__msanb:
                    mfhe__zpz.append(len(eaic__qsyi) + len(hinit__foi))
                elif okob__ttovf in jpwbt__pglxm:
                    uiahu__eheqj = cydvq__nws[rro__bhmsm]
                    mfhe__zpz.append(len(eaic__qsyi) + fro__ozow[uiahu__eheqj])
                else:
                    mfhe__zpz.append(ioup__fia[rnxi__imogp])
                tmild__svktx += 1
            else:
                mfhe__zpz.append(-1)
        mfhe__zpz = np.array(mfhe__zpz, dtype=np.int64)
    if rmafu__ebcck:
        cpgq__aadzo += '    T = None\n'
    else:
        cpgq__aadzo += f"""    T = cpp_table_to_py_table(out_table, table_idx_{vdw__mqsw}, py_table_type_{vdw__mqsw})
"""
    cpgq__aadzo += f'    delete_table(out_table)\n'
    cpgq__aadzo += f'    total_rows = total_rows_np[0]\n'
    cpgq__aadzo += f'    ev.finalize()\n'
    cpgq__aadzo += f'    return (total_rows, T, index_arr)\n'
    cak__auex = {}
    gch__syx = {f'py_table_type_{vdw__mqsw}': spou__smez,
        f'table_idx_{vdw__mqsw}': mfhe__zpz,
        f'selected_cols_arr_{vdw__mqsw}': np.array(eaic__qsyi, np.int32),
        f'nullable_cols_arr_{vdw__mqsw}': np.array(usmbt__alkg, np.int32),
        'index_arr_type': alpz__sjly, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(cpgq__aadzo, gch__syx, cak__auex)
    xcgdq__bqmfu = cak__auex['pq_reader_py']
    yjay__hau = numba.njit(xcgdq__bqmfu, no_cpython_wrapper=True)
    return yjay__hau


def unify_schemas(schemas):
    ymqx__bjk = []
    for schema in schemas:
        for rro__bhmsm in range(len(schema)):
            mun__xmui = schema.field(rro__bhmsm)
            if mun__xmui.type == pa.large_string():
                schema = schema.set(rro__bhmsm, mun__xmui.with_type(pa.
                    string()))
            elif mun__xmui.type == pa.large_binary():
                schema = schema.set(rro__bhmsm, mun__xmui.with_type(pa.
                    binary()))
            elif isinstance(mun__xmui.type, (pa.ListType, pa.LargeListType)
                ) and mun__xmui.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(rro__bhmsm, mun__xmui.with_type(pa.
                    list_(pa.field(mun__xmui.type.value_field.name, pa.
                    string()))))
            elif isinstance(mun__xmui.type, pa.LargeListType):
                schema = schema.set(rro__bhmsm, mun__xmui.with_type(pa.
                    list_(pa.field(mun__xmui.type.value_field.name,
                    mun__xmui.type.value_type))))
        ymqx__bjk.append(schema)
    return pa.unify_schemas(ymqx__bjk)


class ParquetDataset(object):

    def __init__(self, pa_pq_dataset, prefix=''):
        self.schema = pa_pq_dataset.schema
        self.filesystem = None
        self._bodo_total_rows = 0
        self._prefix = prefix
        self.partitioning = None
        partitioning = pa_pq_dataset.partitioning
        self.partition_names = ([] if partitioning is None or partitioning.
            schema == pa_pq_dataset.schema else list(partitioning.schema.names)
            )
        if self.partition_names:
            self.partitioning_dictionaries = partitioning.dictionaries
            self.partitioning_cls = partitioning.__class__
            self.partitioning_schema = partitioning.schema
        else:
            self.partitioning_dictionaries = {}
        for rro__bhmsm in range(len(self.schema)):
            mun__xmui = self.schema.field(rro__bhmsm)
            if mun__xmui.type == pa.large_string():
                self.schema = self.schema.set(rro__bhmsm, mun__xmui.
                    with_type(pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for xqiv__mbyew in self.pieces:
            xqiv__mbyew.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            fbixq__hsqi = {xqiv__mbyew: self.partitioning_dictionaries[
                rro__bhmsm] for rro__bhmsm, xqiv__mbyew in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, fbixq__hsqi)


class ParquetPiece(object):

    def __init__(self, frag, partitioning, partition_names):
        self._frag = None
        self.format = frag.format
        self.path = frag.path
        self._bodo_num_rows = 0
        self.partition_keys = []
        if partitioning is not None:
            self.partition_keys = ds._get_partition_keys(frag.
                partition_expression)
            self.partition_keys = [(iqad__edrjr, partitioning.dictionaries[
                rro__bhmsm].index(self.partition_keys[iqad__edrjr]).as_py()
                ) for rro__bhmsm, iqad__edrjr in enumerate(partition_names)]

    @property
    def frag(self):
        if self._frag is None:
            self._frag = self.format.make_fragment(self.path, self.filesystem)
            del self.format
        return self._frag

    @property
    def metadata(self):
        return self.frag.metadata

    @property
    def num_row_groups(self):
        return self.frag.num_row_groups


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False, tot_rows_to_read=None, typing_pa_schema=None,
    partitioning='hive'):
    if get_row_counts:
        rhyxe__rpx = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    kldao__obi = MPI.COMM_WORLD
    if isinstance(fpath, list):
        ccoyl__uaq = urlparse(fpath[0])
        protocol = ccoyl__uaq.scheme
        dib__oxhrf = ccoyl__uaq.netloc
        for rro__bhmsm in range(len(fpath)):
            mun__xmui = fpath[rro__bhmsm]
            xher__ide = urlparse(mun__xmui)
            if xher__ide.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if xher__ide.netloc != dib__oxhrf:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[rro__bhmsm] = mun__xmui.rstrip('/')
    else:
        ccoyl__uaq = urlparse(fpath)
        protocol = ccoyl__uaq.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as tsese__pmji:
            frszg__nhac = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(frszg__nhac)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as tsese__pmji:
            frszg__nhac = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
"""
    fs = []

    def getfs(parallel=False):
        if len(fs) == 1:
            return fs[0]
        if protocol == 's3':
            fs.append(get_s3_fs_from_path(fpath, parallel=parallel,
                storage_options=storage_options) if not isinstance(fpath,
                list) else get_s3_fs_from_path(fpath[0], parallel=parallel,
                storage_options=storage_options))
        elif protocol in {'gcs', 'gs'}:
            gcs__eblva = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(gcs__eblva)))
        elif protocol == 'http':
            fs.append(PyFileSystem(FSSpecHandler(fsspec.filesystem('http'))))
        elif protocol in {'hdfs', 'abfs', 'abfss'}:
            fs.append(get_hdfs_fs(fpath) if not isinstance(fpath, list) else
                get_hdfs_fs(fpath[0]))
        else:
            fs.append(pa.fs.LocalFileSystem())
        return fs[0]

    def glob(protocol, fs, path):
        if not protocol and fs is None:
            from fsspec.implementations.local import LocalFileSystem
            fs = LocalFileSystem()
        if isinstance(fs, pa.fs.FileSystem):
            from fsspec.implementations.arrow import ArrowFSWrapper
            fs = ArrowFSWrapper(fs)
        try:
            fkbi__rkf = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(fkbi__rkf) == 0:
            raise BodoError('No files found matching glob pattern')
        return fkbi__rkf
    phhyl__jevsv = False
    if get_row_counts:
        zba__ltj = getfs(parallel=True)
        phhyl__jevsv = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        ycon__nja = 1
        qbco__yxxp = os.cpu_count()
        if qbco__yxxp is not None and qbco__yxxp > 1:
            ycon__nja = qbco__yxxp // 2
        try:
            if get_row_counts:
                req__tkc = tracing.Event('pq.ParquetDataset', is_parallel=False
                    )
                if tracing.is_tracing():
                    req__tkc.add_attribute('g_dnf_filter', str(dnf_filters))
            eedq__qsp = pa.io_thread_count()
            pa.set_io_thread_count(ycon__nja)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{ccoyl__uaq.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    ysv__rvkdz = [mun__xmui[len(prefix):] for mun__xmui in
                        fpath]
                else:
                    ysv__rvkdz = fpath[len(prefix):]
            else:
                ysv__rvkdz = fpath
            if isinstance(ysv__rvkdz, list):
                rxru__khc = []
                for xqiv__mbyew in ysv__rvkdz:
                    if has_magic(xqiv__mbyew):
                        rxru__khc += glob(protocol, getfs(), xqiv__mbyew)
                    else:
                        rxru__khc.append(xqiv__mbyew)
                ysv__rvkdz = rxru__khc
            elif has_magic(ysv__rvkdz):
                ysv__rvkdz = glob(protocol, getfs(), ysv__rvkdz)
            utbmq__xfbr = pq.ParquetDataset(ysv__rvkdz, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                utbmq__xfbr._filters = dnf_filters
                utbmq__xfbr._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            wmdj__isl = len(utbmq__xfbr.files)
            utbmq__xfbr = ParquetDataset(utbmq__xfbr, prefix)
            pa.set_io_thread_count(eedq__qsp)
            if typing_pa_schema:
                utbmq__xfbr.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    req__tkc.add_attribute('num_pieces_before_filter',
                        wmdj__isl)
                    req__tkc.add_attribute('num_pieces_after_filter', len(
                        utbmq__xfbr.pieces))
                req__tkc.finalize()
        except Exception as mawys__iun:
            if isinstance(mawys__iun, IsADirectoryError):
                mawys__iun = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(mawys__iun, (
                OSError, FileNotFoundError)):
                mawys__iun = BodoError(str(mawys__iun) +
                    list_of_files_error_msg)
            else:
                mawys__iun = BodoError(
                    f"""error from pyarrow: {type(mawys__iun).__name__}: {str(mawys__iun)}
"""
                    )
            kldao__obi.bcast(mawys__iun)
            raise mawys__iun
        if get_row_counts:
            yab__jyq = tracing.Event('bcast dataset')
        utbmq__xfbr = kldao__obi.bcast(utbmq__xfbr)
    else:
        if get_row_counts:
            yab__jyq = tracing.Event('bcast dataset')
        utbmq__xfbr = kldao__obi.bcast(None)
        if isinstance(utbmq__xfbr, Exception):
            hvbc__kuqyw = utbmq__xfbr
            raise hvbc__kuqyw
    utbmq__xfbr.set_fs(getfs())
    if get_row_counts:
        yab__jyq.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = phhyl__jevsv = False
    if get_row_counts or phhyl__jevsv:
        if get_row_counts and tracing.is_tracing():
            ufnce__tteq = tracing.Event('get_row_counts')
            ufnce__tteq.add_attribute('g_num_pieces', len(utbmq__xfbr.pieces))
            ufnce__tteq.add_attribute('g_expr_filters', str(expr_filters))
        oyjme__hqcy = 0.0
        num_pieces = len(utbmq__xfbr.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        clcu__xgik = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        guwa__ciwsu = 0
        zppkb__ltlp = 0
        zzck__yah = 0
        kqwsf__quhjt = True
        if expr_filters is not None:
            import random
            random.seed(37)
            uvsai__cwn = random.sample(utbmq__xfbr.pieces, k=len(
                utbmq__xfbr.pieces))
        else:
            uvsai__cwn = utbmq__xfbr.pieces
        fpaths = [xqiv__mbyew.path for xqiv__mbyew in uvsai__cwn[start:
            clcu__xgik]]
        ycon__nja = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(ycon__nja)
        pa.set_cpu_count(ycon__nja)
        hvbc__kuqyw = None
        try:
            uzi__mrpx = ds.dataset(fpaths, filesystem=utbmq__xfbr.
                filesystem, partitioning=utbmq__xfbr.partitioning)
            for mlkty__yhhkr, frag in zip(uvsai__cwn[start:clcu__xgik],
                uzi__mrpx.get_fragments()):
                if phhyl__jevsv:
                    qfe__duiec = frag.metadata.schema.to_arrow_schema()
                    guyzw__wimmr = set(qfe__duiec.names)
                    zloxq__yqtqb = set(utbmq__xfbr.schema.names) - set(
                        utbmq__xfbr.partition_names)
                    if zloxq__yqtqb != guyzw__wimmr:
                        hkas__gaakc = guyzw__wimmr - zloxq__yqtqb
                        yrb__qcr = zloxq__yqtqb - guyzw__wimmr
                        zbmgn__svui = (
                            f'Schema in {mlkty__yhhkr} was different.\n')
                        if hkas__gaakc:
                            zbmgn__svui += f"""File contains column(s) {hkas__gaakc} not found in other files in the dataset.
"""
                        if yrb__qcr:
                            zbmgn__svui += f"""File missing column(s) {yrb__qcr} found in other files in the dataset.
"""
                        raise BodoError(zbmgn__svui)
                    try:
                        utbmq__xfbr.schema = unify_schemas([utbmq__xfbr.
                            schema, qfe__duiec])
                    except Exception as mawys__iun:
                        zbmgn__svui = (
                            f'Schema in {mlkty__yhhkr} was different.\n' +
                            str(mawys__iun))
                        raise BodoError(zbmgn__svui)
                une__ctq = time.time()
                aea__nhlq = frag.scanner(schema=uzi__mrpx.schema, filter=
                    expr_filters, use_threads=True).count_rows()
                oyjme__hqcy += time.time() - une__ctq
                mlkty__yhhkr._bodo_num_rows = aea__nhlq
                guwa__ciwsu += aea__nhlq
                zppkb__ltlp += frag.num_row_groups
                zzck__yah += sum(gdm__rgqi.total_byte_size for gdm__rgqi in
                    frag.row_groups)
        except Exception as mawys__iun:
            hvbc__kuqyw = mawys__iun
        if kldao__obi.allreduce(hvbc__kuqyw is not None, op=MPI.LOR):
            for hvbc__kuqyw in kldao__obi.allgather(hvbc__kuqyw):
                if hvbc__kuqyw:
                    if isinstance(fpath, list) and isinstance(hvbc__kuqyw,
                        (OSError, FileNotFoundError)):
                        raise BodoError(str(hvbc__kuqyw) +
                            list_of_files_error_msg)
                    raise hvbc__kuqyw
        if phhyl__jevsv:
            kqwsf__quhjt = kldao__obi.allreduce(kqwsf__quhjt, op=MPI.LAND)
            if not kqwsf__quhjt:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            utbmq__xfbr._bodo_total_rows = kldao__obi.allreduce(guwa__ciwsu,
                op=MPI.SUM)
            zvv__fjp = kldao__obi.allreduce(zppkb__ltlp, op=MPI.SUM)
            fhl__rqe = kldao__obi.allreduce(zzck__yah, op=MPI.SUM)
            sskc__rqz = np.array([xqiv__mbyew._bodo_num_rows for
                xqiv__mbyew in utbmq__xfbr.pieces])
            sskc__rqz = kldao__obi.allreduce(sskc__rqz, op=MPI.SUM)
            for xqiv__mbyew, yayrj__pyb in zip(utbmq__xfbr.pieces, sskc__rqz):
                xqiv__mbyew._bodo_num_rows = yayrj__pyb
            if is_parallel and bodo.get_rank(
                ) == 0 and zvv__fjp < bodo.get_size() and zvv__fjp != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({zvv__fjp}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if zvv__fjp == 0:
                vrf__puzn = 0
            else:
                vrf__puzn = fhl__rqe // zvv__fjp
            if (bodo.get_rank() == 0 and fhl__rqe >= 20 * 1048576 and 
                vrf__puzn < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({vrf__puzn} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                ufnce__tteq.add_attribute('g_total_num_row_groups', zvv__fjp)
                ufnce__tteq.add_attribute('total_scan_time', oyjme__hqcy)
                gdcw__kvsg = np.array([xqiv__mbyew._bodo_num_rows for
                    xqiv__mbyew in utbmq__xfbr.pieces])
                rzxe__ngplf = np.percentile(gdcw__kvsg, [25, 50, 75])
                ufnce__tteq.add_attribute('g_row_counts_min', gdcw__kvsg.min())
                ufnce__tteq.add_attribute('g_row_counts_Q1', rzxe__ngplf[0])
                ufnce__tteq.add_attribute('g_row_counts_median', rzxe__ngplf[1]
                    )
                ufnce__tteq.add_attribute('g_row_counts_Q3', rzxe__ngplf[2])
                ufnce__tteq.add_attribute('g_row_counts_max', gdcw__kvsg.max())
                ufnce__tteq.add_attribute('g_row_counts_mean', gdcw__kvsg.
                    mean())
                ufnce__tteq.add_attribute('g_row_counts_std', gdcw__kvsg.std())
                ufnce__tteq.add_attribute('g_row_counts_sum', gdcw__kvsg.sum())
                ufnce__tteq.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(utbmq__xfbr)
    if get_row_counts:
        rhyxe__rpx.finalize()
    if phhyl__jevsv and is_parallel:
        if tracing.is_tracing():
            sqhop__wbh = tracing.Event('unify_schemas_across_ranks')
        hvbc__kuqyw = None
        try:
            utbmq__xfbr.schema = kldao__obi.allreduce(utbmq__xfbr.schema,
                bodo.io.helpers.pa_schema_unify_mpi_op)
        except Exception as mawys__iun:
            hvbc__kuqyw = mawys__iun
        if tracing.is_tracing():
            sqhop__wbh.finalize()
        if kldao__obi.allreduce(hvbc__kuqyw is not None, op=MPI.LOR):
            for hvbc__kuqyw in kldao__obi.allgather(hvbc__kuqyw):
                if hvbc__kuqyw:
                    zbmgn__svui = (
                        f'Schema in some files were different.\n' + str(
                        hvbc__kuqyw))
                    raise BodoError(zbmgn__svui)
    return utbmq__xfbr


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    qbco__yxxp = os.cpu_count()
    if qbco__yxxp is None or qbco__yxxp == 0:
        qbco__yxxp = 2
    cmg__jal = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), qbco__yxxp)
    tbezm__lgpg = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)),
        qbco__yxxp)
    if is_parallel and len(fpaths) > tbezm__lgpg and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(tbezm__lgpg)
        pa.set_cpu_count(tbezm__lgpg)
    else:
        pa.set_io_thread_count(cmg__jal)
        pa.set_cpu_count(cmg__jal)
    tsj__yfl = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    bakt__rrsl = set(str_as_dict_cols)
    for rro__bhmsm, name in enumerate(schema.names):
        if name in bakt__rrsl:
            pltdn__jznt = schema.field(rro__bhmsm)
            uljp__wqa = pa.field(name, pa.dictionary(pa.int32(),
                pltdn__jznt.type), pltdn__jznt.nullable)
            schema = schema.remove(rro__bhmsm).insert(rro__bhmsm, uljp__wqa)
    utbmq__xfbr = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=tsj__yfl)
    col_names = utbmq__xfbr.schema.names
    uhab__whsyh = [col_names[bxib__cdxo] for bxib__cdxo in selected_fields]
    yzs__dmbj = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if yzs__dmbj and expr_filters is None:
        zgd__dfw = []
        untk__sxdv = 0
        utj__jeqdp = 0
        for frag in utbmq__xfbr.get_fragments():
            wce__kwrtf = []
            for gdm__rgqi in frag.row_groups:
                opfy__obfm = gdm__rgqi.num_rows
                if start_offset < untk__sxdv + opfy__obfm:
                    if utj__jeqdp == 0:
                        zlefz__ankff = start_offset - untk__sxdv
                        xio__oubno = min(opfy__obfm - zlefz__ankff,
                            rows_to_read)
                    else:
                        xio__oubno = min(opfy__obfm, rows_to_read - utj__jeqdp)
                    utj__jeqdp += xio__oubno
                    wce__kwrtf.append(gdm__rgqi.id)
                untk__sxdv += opfy__obfm
                if utj__jeqdp == rows_to_read:
                    break
            zgd__dfw.append(frag.subset(row_group_ids=wce__kwrtf))
            if utj__jeqdp == rows_to_read:
                break
        utbmq__xfbr = ds.FileSystemDataset(zgd__dfw, utbmq__xfbr.schema,
            tsj__yfl, filesystem=utbmq__xfbr.filesystem)
        start_offset = zlefz__ankff
    eia__lrj = utbmq__xfbr.scanner(columns=uhab__whsyh, filter=expr_filters,
        use_threads=True).to_reader()
    return utbmq__xfbr, eia__lrj, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    whg__udpfv = [c for c in pa_schema.names if isinstance(pa_schema.field(
        c).type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(whg__udpfv) == 0:
        pq_dataset._category_info = {}
        return
    kldao__obi = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            wfmri__pbkt = pq_dataset.pieces[0].frag.head(100, columns=
                whg__udpfv)
            elx__yae = {c: tuple(wfmri__pbkt.column(c).chunk(0).dictionary.
                to_pylist()) for c in whg__udpfv}
            del wfmri__pbkt
        except Exception as mawys__iun:
            kldao__obi.bcast(mawys__iun)
            raise mawys__iun
        kldao__obi.bcast(elx__yae)
    else:
        elx__yae = kldao__obi.bcast(None)
        if isinstance(elx__yae, Exception):
            hvbc__kuqyw = elx__yae
            raise hvbc__kuqyw
    pq_dataset._category_info = elx__yae


def get_pandas_metadata(schema, num_pieces):
    ebr__lnygi = None
    ftbv__lpjjb = defaultdict(lambda : None)
    ggsz__kuk = b'pandas'
    if schema.metadata is not None and ggsz__kuk in schema.metadata:
        import json
        ckm__vplq = json.loads(schema.metadata[ggsz__kuk].decode('utf8'))
        qqoyr__xhnek = len(ckm__vplq['index_columns'])
        if qqoyr__xhnek > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        ebr__lnygi = ckm__vplq['index_columns'][0] if qqoyr__xhnek else None
        if not isinstance(ebr__lnygi, str) and not isinstance(ebr__lnygi, dict
            ):
            ebr__lnygi = None
        for wqo__ujd in ckm__vplq['columns']:
            tgma__orfax = wqo__ujd['name']
            if wqo__ujd['pandas_type'].startswith('int'
                ) and tgma__orfax is not None:
                if wqo__ujd['numpy_type'].startswith('Int'):
                    ftbv__lpjjb[tgma__orfax] = True
                else:
                    ftbv__lpjjb[tgma__orfax] = False
    return ebr__lnygi, ftbv__lpjjb


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for tgma__orfax in pa_schema.names:
        nawy__ljg = pa_schema.field(tgma__orfax)
        if nawy__ljg.type in (pa.string(), pa.large_string()):
            str_columns.append(tgma__orfax)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    kldao__obi = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        uvsai__cwn = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        uvsai__cwn = pq_dataset.pieces
    ioiz__ajgu = np.zeros(len(str_columns), dtype=np.int64)
    gxvsn__ocd = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(uvsai__cwn):
        mlkty__yhhkr = uvsai__cwn[bodo.get_rank()]
        try:
            metadata = mlkty__yhhkr.metadata
            for rro__bhmsm in range(mlkty__yhhkr.num_row_groups):
                for tmild__svktx, tgma__orfax in enumerate(str_columns):
                    kqqj__oaqap = pa_schema.get_field_index(tgma__orfax)
                    ioiz__ajgu[tmild__svktx] += metadata.row_group(rro__bhmsm
                        ).column(kqqj__oaqap).total_uncompressed_size
            ljl__tedbn = metadata.num_rows
        except Exception as mawys__iun:
            if isinstance(mawys__iun, (OSError, FileNotFoundError)):
                ljl__tedbn = 0
            else:
                raise
    else:
        ljl__tedbn = 0
    ltpek__wmbuj = kldao__obi.allreduce(ljl__tedbn, op=MPI.SUM)
    if ltpek__wmbuj == 0:
        return set()
    kldao__obi.Allreduce(ioiz__ajgu, gxvsn__ocd, op=MPI.SUM)
    gxhyf__buq = gxvsn__ocd / ltpek__wmbuj
    nafow__ffwuu = set()
    for rro__bhmsm, tpz__amlay in enumerate(gxhyf__buq):
        if tpz__amlay < READ_STR_AS_DICT_THRESHOLD:
            tgma__orfax = str_columns[rro__bhmsm][0]
            nafow__ffwuu.add(tgma__orfax)
    return nafow__ffwuu


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    zhlxc__efi = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    onx__gszu = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    nitl__kki = read_as_dict_cols - onx__gszu
    if len(nitl__kki) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {nitl__kki}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(onx__gszu)
    onx__gszu = onx__gszu - read_as_dict_cols
    str_columns = [ftkdf__tbk for ftkdf__tbk in str_columns if ftkdf__tbk in
        onx__gszu]
    nafow__ffwuu: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    nafow__ffwuu.update(read_as_dict_cols)
    col_names = pa_schema.names
    ebr__lnygi, ftbv__lpjjb = get_pandas_metadata(pa_schema, num_pieces)
    gsj__zlogn = []
    zvbie__ukpq = []
    mxbk__trk = []
    for rro__bhmsm, c in enumerate(col_names):
        if c in partition_names:
            continue
        nawy__ljg = pa_schema.field(c)
        cqdeq__cmtz, dtz__nuwh = _get_numba_typ_from_pa_typ(nawy__ljg, c ==
            ebr__lnygi, ftbv__lpjjb[c], pq_dataset._category_info,
            str_as_dict=c in nafow__ffwuu)
        gsj__zlogn.append(cqdeq__cmtz)
        zvbie__ukpq.append(dtz__nuwh)
        mxbk__trk.append(nawy__ljg.type)
    if partition_names:
        gsj__zlogn += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[rro__bhmsm]) for rro__bhmsm in range(
            len(partition_names))]
        zvbie__ukpq.extend([True] * len(partition_names))
        mxbk__trk.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        gsj__zlogn += [dict_str_arr_type]
        zvbie__ukpq.append(True)
        mxbk__trk.append(None)
    seli__ojrgx = {c: rro__bhmsm for rro__bhmsm, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in seli__ojrgx:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if ebr__lnygi and not isinstance(ebr__lnygi, dict
        ) and ebr__lnygi not in selected_columns:
        selected_columns.append(ebr__lnygi)
    col_names = selected_columns
    col_indices = []
    zhlxc__efi = []
    cyyt__xvgw = []
    gff__xgy = []
    for rro__bhmsm, c in enumerate(col_names):
        okob__ttovf = seli__ojrgx[c]
        col_indices.append(okob__ttovf)
        zhlxc__efi.append(gsj__zlogn[okob__ttovf])
        if not zvbie__ukpq[okob__ttovf]:
            cyyt__xvgw.append(rro__bhmsm)
            gff__xgy.append(mxbk__trk[okob__ttovf])
    return (col_names, zhlxc__efi, ebr__lnygi, col_indices, partition_names,
        cyyt__xvgw, gff__xgy)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    ksnd__anv = dictionary.to_pandas()
    iitx__vjnd = bodo.typeof(ksnd__anv).dtype
    if isinstance(iitx__vjnd, types.Integer):
        ipf__pli = PDCategoricalDtype(tuple(ksnd__anv), iitx__vjnd, False,
            int_type=iitx__vjnd)
    else:
        ipf__pli = PDCategoricalDtype(tuple(ksnd__anv), iitx__vjnd, False)
    return CategoricalArrayType(ipf__pli)


_pq_read = types.ExternalFunction('pq_read', table_type(
    read_parquet_fpath_type, types.boolean, parquet_predicate_type,
    parquet_predicate_type, storage_options_dict_type, types.int64, types.
    voidptr, types.int32, types.voidptr, types.voidptr, types.voidptr,
    types.int32, types.voidptr, types.int32, types.voidptr, types.boolean))
from llvmlite import ir as lir
from numba.core import cgutils
if bodo.utils.utils.has_pyarrow():
    from bodo.io import arrow_cpp
    ll.add_symbol('pq_read', arrow_cpp.pq_read)
    ll.add_symbol('pq_write', arrow_cpp.pq_write)
    ll.add_symbol('pq_write_partitioned', arrow_cpp.pq_write_partitioned)


@intrinsic
def parquet_write_table_cpp(typingctx, filename_t, table_t, col_names_t,
    index_t, write_index, metadata_t, compression_t, is_parallel_t,
    write_range_index, start, stop, step, name, bucket_region,
    row_group_size, file_prefix):

    def codegen(context, builder, sig, args):
        viv__sccj = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        lvb__tvx = cgutils.get_or_insert_function(builder.module, viv__sccj,
            name='pq_write')
        kpzio__irfn = builder.call(lvb__tvx, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return kpzio__irfn
    return types.int64(types.voidptr, table_t, col_names_t, index_t, types.
        boolean, types.voidptr, types.voidptr, types.boolean, types.boolean,
        types.int32, types.int32, types.int32, types.voidptr, types.voidptr,
        types.int64, types.voidptr), codegen


@intrinsic
def parquet_write_table_partitioned_cpp(typingctx, filename_t, data_table_t,
    col_names_t, col_names_no_partitions_t, cat_table_t, part_col_idxs_t,
    num_part_col_t, compression_t, is_parallel_t, bucket_region,
    row_group_size, file_prefix):

    def codegen(context, builder, sig, args):
        viv__sccj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        lvb__tvx = cgutils.get_or_insert_function(builder.module, viv__sccj,
            name='pq_write_partitioned')
        builder.call(lvb__tvx, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
