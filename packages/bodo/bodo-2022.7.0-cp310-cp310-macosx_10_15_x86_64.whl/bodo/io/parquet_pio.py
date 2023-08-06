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
        except OSError as ylyes__oghlj:
            if 'non-file path' in str(ylyes__oghlj):
                raise FileNotFoundError(str(ylyes__oghlj))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        kyfr__efiai = lhs.scope
        rvipb__kjyq = lhs.loc
        wzekt__cxnhv = None
        if lhs.name in self.locals:
            wzekt__cxnhv = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        lgv__zigon = {}
        if lhs.name + ':convert' in self.locals:
            lgv__zigon = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if wzekt__cxnhv is None:
            jgmvu__xocn = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            vha__fgcbe = get_const_value(file_name, self.func_ir,
                jgmvu__xocn, arg_types=self.args, file_info=ParquetFileInfo
                (columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            egq__gkiaa = False
            zdjks__dvr = guard(get_definition, self.func_ir, file_name)
            if isinstance(zdjks__dvr, ir.Arg):
                typ = self.args[zdjks__dvr.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, xkzg__winlf, dzb__bcgj, col_indices,
                        partition_names, hzcd__sph, cxmw__lup) = typ.schema
                    egq__gkiaa = True
            if not egq__gkiaa:
                (col_names, xkzg__winlf, dzb__bcgj, col_indices,
                    partition_names, hzcd__sph, cxmw__lup) = (
                    parquet_file_schema(vha__fgcbe, columns,
                    storage_options=storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            cora__myvkk = list(wzekt__cxnhv.keys())
            vhbze__nqz = {c: xrg__ook for xrg__ook, c in enumerate(cora__myvkk)
                }
            lem__mpd = [ffi__hiwv for ffi__hiwv in wzekt__cxnhv.values()]
            dzb__bcgj = 'index' if 'index' in vhbze__nqz else None
            if columns is None:
                selected_columns = cora__myvkk
            else:
                selected_columns = columns
            col_indices = [vhbze__nqz[c] for c in selected_columns]
            xkzg__winlf = [lem__mpd[vhbze__nqz[c]] for c in selected_columns]
            col_names = selected_columns
            dzb__bcgj = dzb__bcgj if dzb__bcgj in col_names else None
            partition_names = []
            hzcd__sph = []
            cxmw__lup = []
        fiz__bii = None if isinstance(dzb__bcgj, dict
            ) or dzb__bcgj is None else dzb__bcgj
        index_column_index = None
        index_column_type = types.none
        if fiz__bii:
            cxjmj__bdoeg = col_names.index(fiz__bii)
            index_column_index = col_indices.pop(cxjmj__bdoeg)
            index_column_type = xkzg__winlf.pop(cxjmj__bdoeg)
            col_names.pop(cxjmj__bdoeg)
        for xrg__ook, c in enumerate(col_names):
            if c in lgv__zigon:
                xkzg__winlf[xrg__ook] = lgv__zigon[c]
        cgppt__xvlch = [ir.Var(kyfr__efiai, mk_unique_var('pq_table'),
            rvipb__kjyq), ir.Var(kyfr__efiai, mk_unique_var('pq_index'),
            rvipb__kjyq)]
        huoe__oiba = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, xkzg__winlf, cgppt__xvlch, rvipb__kjyq,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, hzcd__sph, cxmw__lup)]
        return (col_names, cgppt__xvlch, dzb__bcgj, huoe__oiba, xkzg__winlf,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    qfwcr__wiz = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    zirsl__dqdts, gusw__cusv = bodo.ir.connector.generate_filter_map(pq_node
        .filters)
    extra_args = ', '.join(zirsl__dqdts.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, zirsl__dqdts, gusw__cusv, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    eqy__fee = ', '.join(f'out{xrg__ook}' for xrg__ook in range(qfwcr__wiz))
    uvjwh__bfqmp = f'def pq_impl(fname, {extra_args}):\n'
    uvjwh__bfqmp += (
        f'    (total_rows, {eqy__fee},) = _pq_reader_py(fname, {extra_args})\n'
        )
    rzr__xnj = {}
    exec(uvjwh__bfqmp, {}, rzr__xnj)
    kvm__xxt = rzr__xnj['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        ygb__ecxe = pq_node.loc.strformat()
        fhxts__lva = []
        dmenl__ecol = []
        for xrg__ook in pq_node.out_used_cols:
            msxol__zddzh = pq_node.df_colnames[xrg__ook]
            fhxts__lva.append(msxol__zddzh)
            if isinstance(pq_node.out_types[xrg__ook], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                dmenl__ecol.append(msxol__zddzh)
        dlsfl__fdz = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', dlsfl__fdz,
            ygb__ecxe, fhxts__lva)
        if dmenl__ecol:
            ibdpv__levea = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                ibdpv__levea, ygb__ecxe, dmenl__ecol)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        eqi__baf = set(pq_node.out_used_cols)
        quw__cgpnf = set(pq_node.unsupported_columns)
        pvqss__xpb = eqi__baf & quw__cgpnf
        if pvqss__xpb:
            nsr__wtdjh = sorted(pvqss__xpb)
            nsi__lzode = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            pplxg__xwlra = 0
            for qir__llf in nsr__wtdjh:
                while pq_node.unsupported_columns[pplxg__xwlra] != qir__llf:
                    pplxg__xwlra += 1
                nsi__lzode.append(
                    f"Column '{pq_node.df_colnames[qir__llf]}' with unsupported arrow type {pq_node.unsupported_arrow_types[pplxg__xwlra]}"
                    )
                pplxg__xwlra += 1
            khyo__qfa = '\n'.join(nsi__lzode)
            raise BodoError(khyo__qfa, loc=pq_node.loc)
    ahohc__bhjcv = _gen_pq_reader_py(pq_node.df_colnames, pq_node.
        col_indices, pq_node.out_used_cols, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    yju__nfcp = typemap[pq_node.file_name.name]
    wdek__ndad = (yju__nfcp,) + tuple(typemap[qefj__jsx.name] for qefj__jsx in
        gusw__cusv)
    wqt__ngdma = compile_to_numba_ir(kvm__xxt, {'_pq_reader_py':
        ahohc__bhjcv}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        wdek__ndad, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(wqt__ngdma, [pq_node.file_name] + gusw__cusv)
    huoe__oiba = wqt__ngdma.body[:-3]
    if meta_head_only_info:
        huoe__oiba[-3].target = meta_head_only_info[1]
    huoe__oiba[-2].target = pq_node.out_vars[0]
    huoe__oiba[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        huoe__oiba.pop(-1)
    elif not pq_node.out_used_cols:
        huoe__oiba.pop(-2)
    return huoe__oiba


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    elune__bky = get_overload_const_str(dnf_filter_str)
    fgr__xznhf = get_overload_const_str(expr_filter_str)
    wgr__rqtch = ', '.join(f'f{xrg__ook}' for xrg__ook in range(len(var_tup)))
    uvjwh__bfqmp = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        uvjwh__bfqmp += f'  {wgr__rqtch}, = var_tup\n'
    uvjwh__bfqmp += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    uvjwh__bfqmp += f'    dnf_filters_py = {elune__bky}\n'
    uvjwh__bfqmp += f'    expr_filters_py = {fgr__xznhf}\n'
    uvjwh__bfqmp += '  return (dnf_filters_py, expr_filters_py)\n'
    rzr__xnj = {}
    exec(uvjwh__bfqmp, globals(), rzr__xnj)
    return rzr__xnj['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    olda__cbwqf = next_label()
    ghdc__dghwx = ',' if extra_args else ''
    uvjwh__bfqmp = f'def pq_reader_py(fname,{extra_args}):\n'
    uvjwh__bfqmp += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    uvjwh__bfqmp += f"    ev.add_attribute('g_fname', fname)\n"
    uvjwh__bfqmp += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{ghdc__dghwx}))
"""
    uvjwh__bfqmp += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    uvjwh__bfqmp += f"""    storage_options_py = get_storage_options_pyobject({str(storage_options)})
"""
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    bvag__zbu = not out_used_cols
    vfb__ztq = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    pcgot__ktx = {c: xrg__ook for xrg__ook, c in enumerate(col_indices)}
    xiwny__ypudz = {c: xrg__ook for xrg__ook, c in enumerate(vfb__ztq)}
    fsepp__mqz = []
    gqiwe__vffyk = set()
    uzoo__kfk = partition_names + [input_file_name_col]
    for xrg__ook in out_used_cols:
        if vfb__ztq[xrg__ook] not in uzoo__kfk:
            fsepp__mqz.append(col_indices[xrg__ook])
        elif not input_file_name_col or vfb__ztq[xrg__ook
            ] != input_file_name_col:
            gqiwe__vffyk.add(col_indices[xrg__ook])
    if index_column_index is not None:
        fsepp__mqz.append(index_column_index)
    fsepp__mqz = sorted(fsepp__mqz)
    qiubj__rlpo = {c: xrg__ook for xrg__ook, c in enumerate(fsepp__mqz)}
    cklio__fun = [(int(is_nullable(out_types[pcgot__ktx[lxet__vxia]])) if 
        lxet__vxia != index_column_index else int(is_nullable(
        index_column_type))) for lxet__vxia in fsepp__mqz]
    str_as_dict_cols = []
    for lxet__vxia in fsepp__mqz:
        if lxet__vxia == index_column_index:
            ffi__hiwv = index_column_type
        else:
            ffi__hiwv = out_types[pcgot__ktx[lxet__vxia]]
        if ffi__hiwv == dict_str_arr_type:
            str_as_dict_cols.append(lxet__vxia)
    naizd__qgl = []
    ude__cut = {}
    cwzt__bkl = []
    cgam__ddqcz = []
    for xrg__ook, nfz__fqr in enumerate(partition_names):
        try:
            lfjv__cxhei = xiwny__ypudz[nfz__fqr]
            if col_indices[lfjv__cxhei] not in gqiwe__vffyk:
                continue
        except (KeyError, ValueError) as ovaap__fqxv:
            continue
        ude__cut[nfz__fqr] = len(naizd__qgl)
        naizd__qgl.append(nfz__fqr)
        cwzt__bkl.append(xrg__ook)
        ilxjj__hib = out_types[lfjv__cxhei].dtype
        ofky__qkqi = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            ilxjj__hib)
        cgam__ddqcz.append(numba_to_c_type(ofky__qkqi))
    uvjwh__bfqmp += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    uvjwh__bfqmp += f'    out_table = pq_read(\n'
    uvjwh__bfqmp += f'        fname_py, {is_parallel},\n'
    uvjwh__bfqmp += f'        dnf_filters, expr_filters,\n'
    uvjwh__bfqmp += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{olda__cbwqf}.ctypes,
"""
    uvjwh__bfqmp += f'        {len(fsepp__mqz)},\n'
    uvjwh__bfqmp += f'        nullable_cols_arr_{olda__cbwqf}.ctypes,\n'
    if len(cwzt__bkl) > 0:
        uvjwh__bfqmp += (
            f'        np.array({cwzt__bkl}, dtype=np.int32).ctypes,\n')
        uvjwh__bfqmp += (
            f'        np.array({cgam__ddqcz}, dtype=np.int32).ctypes,\n')
        uvjwh__bfqmp += f'        {len(cwzt__bkl)},\n'
    else:
        uvjwh__bfqmp += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        uvjwh__bfqmp += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        uvjwh__bfqmp += f'        0, 0,\n'
    uvjwh__bfqmp += f'        total_rows_np.ctypes,\n'
    uvjwh__bfqmp += f'        {input_file_name_col is not None},\n'
    uvjwh__bfqmp += f'    )\n'
    uvjwh__bfqmp += f'    check_and_propagate_cpp_exception()\n'
    ycb__jwnbu = 'None'
    ida__ihc = index_column_type
    peys__bnbcg = TableType(tuple(out_types))
    if bvag__zbu:
        peys__bnbcg = types.none
    if index_column_index is not None:
        uijzc__gxxoi = qiubj__rlpo[index_column_index]
        ycb__jwnbu = (
            f'info_to_array(info_from_table(out_table, {uijzc__gxxoi}), index_arr_type)'
            )
    uvjwh__bfqmp += f'    index_arr = {ycb__jwnbu}\n'
    if bvag__zbu:
        ojn__ekeuy = None
    else:
        ojn__ekeuy = []
        xkl__clk = 0
        pyr__lra = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for xrg__ook, qir__llf in enumerate(col_indices):
            if xkl__clk < len(out_used_cols) and xrg__ook == out_used_cols[
                xkl__clk]:
                fqx__uto = col_indices[xrg__ook]
                if pyr__lra and fqx__uto == pyr__lra:
                    ojn__ekeuy.append(len(fsepp__mqz) + len(naizd__qgl))
                elif fqx__uto in gqiwe__vffyk:
                    uilt__vhry = vfb__ztq[xrg__ook]
                    ojn__ekeuy.append(len(fsepp__mqz) + ude__cut[uilt__vhry])
                else:
                    ojn__ekeuy.append(qiubj__rlpo[qir__llf])
                xkl__clk += 1
            else:
                ojn__ekeuy.append(-1)
        ojn__ekeuy = np.array(ojn__ekeuy, dtype=np.int64)
    if bvag__zbu:
        uvjwh__bfqmp += '    T = None\n'
    else:
        uvjwh__bfqmp += f"""    T = cpp_table_to_py_table(out_table, table_idx_{olda__cbwqf}, py_table_type_{olda__cbwqf})
"""
    uvjwh__bfqmp += f'    delete_table(out_table)\n'
    uvjwh__bfqmp += f'    total_rows = total_rows_np[0]\n'
    uvjwh__bfqmp += f'    ev.finalize()\n'
    uvjwh__bfqmp += f'    return (total_rows, T, index_arr)\n'
    rzr__xnj = {}
    uaak__tnfu = {f'py_table_type_{olda__cbwqf}': peys__bnbcg,
        f'table_idx_{olda__cbwqf}': ojn__ekeuy,
        f'selected_cols_arr_{olda__cbwqf}': np.array(fsepp__mqz, np.int32),
        f'nullable_cols_arr_{olda__cbwqf}': np.array(cklio__fun, np.int32),
        'index_arr_type': ida__ihc, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(uvjwh__bfqmp, uaak__tnfu, rzr__xnj)
    ahohc__bhjcv = rzr__xnj['pq_reader_py']
    wmqae__jood = numba.njit(ahohc__bhjcv, no_cpython_wrapper=True)
    return wmqae__jood


def unify_schemas(schemas):
    lkrgn__lceva = []
    for schema in schemas:
        for xrg__ook in range(len(schema)):
            zssbu__auzaq = schema.field(xrg__ook)
            if zssbu__auzaq.type == pa.large_string():
                schema = schema.set(xrg__ook, zssbu__auzaq.with_type(pa.
                    string()))
            elif zssbu__auzaq.type == pa.large_binary():
                schema = schema.set(xrg__ook, zssbu__auzaq.with_type(pa.
                    binary()))
            elif isinstance(zssbu__auzaq.type, (pa.ListType, pa.LargeListType)
                ) and zssbu__auzaq.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(xrg__ook, zssbu__auzaq.with_type(pa.
                    list_(pa.field(zssbu__auzaq.type.value_field.name, pa.
                    string()))))
            elif isinstance(zssbu__auzaq.type, pa.LargeListType):
                schema = schema.set(xrg__ook, zssbu__auzaq.with_type(pa.
                    list_(pa.field(zssbu__auzaq.type.value_field.name,
                    zssbu__auzaq.type.value_type))))
        lkrgn__lceva.append(schema)
    return pa.unify_schemas(lkrgn__lceva)


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
        for xrg__ook in range(len(self.schema)):
            zssbu__auzaq = self.schema.field(xrg__ook)
            if zssbu__auzaq.type == pa.large_string():
                self.schema = self.schema.set(xrg__ook, zssbu__auzaq.
                    with_type(pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for qnz__xrmm in self.pieces:
            qnz__xrmm.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            dxu__cbbar = {qnz__xrmm: self.partitioning_dictionaries[
                xrg__ook] for xrg__ook, qnz__xrmm in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, dxu__cbbar)


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
            self.partition_keys = [(nfz__fqr, partitioning.dictionaries[
                xrg__ook].index(self.partition_keys[nfz__fqr]).as_py()) for
                xrg__ook, nfz__fqr in enumerate(partition_names)]

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
        jljo__zmf = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    simv__xzj = MPI.COMM_WORLD
    if isinstance(fpath, list):
        hru__vdui = urlparse(fpath[0])
        protocol = hru__vdui.scheme
        fbfmx__uoql = hru__vdui.netloc
        for xrg__ook in range(len(fpath)):
            zssbu__auzaq = fpath[xrg__ook]
            nxwl__rif = urlparse(zssbu__auzaq)
            if nxwl__rif.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if nxwl__rif.netloc != fbfmx__uoql:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[xrg__ook] = zssbu__auzaq.rstrip('/')
    else:
        hru__vdui = urlparse(fpath)
        protocol = hru__vdui.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as ovaap__fqxv:
            lndc__ijc = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(lndc__ijc)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as ovaap__fqxv:
            lndc__ijc = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            cmx__bsoc = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(cmx__bsoc)))
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
            ujcp__fxb = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(ujcp__fxb) == 0:
            raise BodoError('No files found matching glob pattern')
        return ujcp__fxb
    ypvwf__utai = False
    if get_row_counts:
        wtwc__xjojj = getfs(parallel=True)
        ypvwf__utai = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        vex__fgkoz = 1
        dohg__iiltc = os.cpu_count()
        if dohg__iiltc is not None and dohg__iiltc > 1:
            vex__fgkoz = dohg__iiltc // 2
        try:
            if get_row_counts:
                vavoh__gkloz = tracing.Event('pq.ParquetDataset',
                    is_parallel=False)
                if tracing.is_tracing():
                    vavoh__gkloz.add_attribute('g_dnf_filter', str(dnf_filters)
                        )
            fahra__hbx = pa.io_thread_count()
            pa.set_io_thread_count(vex__fgkoz)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{hru__vdui.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    feq__vbqxx = [zssbu__auzaq[len(prefix):] for
                        zssbu__auzaq in fpath]
                else:
                    feq__vbqxx = fpath[len(prefix):]
            else:
                feq__vbqxx = fpath
            if isinstance(feq__vbqxx, list):
                icdbb__wvgtr = []
                for qnz__xrmm in feq__vbqxx:
                    if has_magic(qnz__xrmm):
                        icdbb__wvgtr += glob(protocol, getfs(), qnz__xrmm)
                    else:
                        icdbb__wvgtr.append(qnz__xrmm)
                feq__vbqxx = icdbb__wvgtr
            elif has_magic(feq__vbqxx):
                feq__vbqxx = glob(protocol, getfs(), feq__vbqxx)
            fbr__lql = pq.ParquetDataset(feq__vbqxx, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                fbr__lql._filters = dnf_filters
                fbr__lql._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            yatkz__inafs = len(fbr__lql.files)
            fbr__lql = ParquetDataset(fbr__lql, prefix)
            pa.set_io_thread_count(fahra__hbx)
            if typing_pa_schema:
                fbr__lql.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    vavoh__gkloz.add_attribute('num_pieces_before_filter',
                        yatkz__inafs)
                    vavoh__gkloz.add_attribute('num_pieces_after_filter',
                        len(fbr__lql.pieces))
                vavoh__gkloz.finalize()
        except Exception as ylyes__oghlj:
            if isinstance(ylyes__oghlj, IsADirectoryError):
                ylyes__oghlj = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(ylyes__oghlj, (
                OSError, FileNotFoundError)):
                ylyes__oghlj = BodoError(str(ylyes__oghlj) +
                    list_of_files_error_msg)
            else:
                ylyes__oghlj = BodoError(
                    f"""error from pyarrow: {type(ylyes__oghlj).__name__}: {str(ylyes__oghlj)}
"""
                    )
            simv__xzj.bcast(ylyes__oghlj)
            raise ylyes__oghlj
        if get_row_counts:
            fqrlu__jgm = tracing.Event('bcast dataset')
        fbr__lql = simv__xzj.bcast(fbr__lql)
    else:
        if get_row_counts:
            fqrlu__jgm = tracing.Event('bcast dataset')
        fbr__lql = simv__xzj.bcast(None)
        if isinstance(fbr__lql, Exception):
            jjzr__qze = fbr__lql
            raise jjzr__qze
    fbr__lql.set_fs(getfs())
    if get_row_counts:
        fqrlu__jgm.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = ypvwf__utai = False
    if get_row_counts or ypvwf__utai:
        if get_row_counts and tracing.is_tracing():
            rtlwc__ail = tracing.Event('get_row_counts')
            rtlwc__ail.add_attribute('g_num_pieces', len(fbr__lql.pieces))
            rtlwc__ail.add_attribute('g_expr_filters', str(expr_filters))
        vmx__yxjc = 0.0
        num_pieces = len(fbr__lql.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        iffuo__jja = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        wxmh__snd = 0
        okp__djllu = 0
        wgyvk__mznq = 0
        nlhf__vouff = True
        if expr_filters is not None:
            import random
            random.seed(37)
            hcknp__himbr = random.sample(fbr__lql.pieces, k=len(fbr__lql.
                pieces))
        else:
            hcknp__himbr = fbr__lql.pieces
        fpaths = [qnz__xrmm.path for qnz__xrmm in hcknp__himbr[start:
            iffuo__jja]]
        vex__fgkoz = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(vex__fgkoz)
        pa.set_cpu_count(vex__fgkoz)
        jjzr__qze = None
        try:
            kpq__cebyf = ds.dataset(fpaths, filesystem=fbr__lql.filesystem,
                partitioning=fbr__lql.partitioning)
            for dyfm__lgma, frag in zip(hcknp__himbr[start:iffuo__jja],
                kpq__cebyf.get_fragments()):
                if ypvwf__utai:
                    osngg__uyhap = frag.metadata.schema.to_arrow_schema()
                    devv__zazgr = set(osngg__uyhap.names)
                    wqi__mpic = set(fbr__lql.schema.names) - set(fbr__lql.
                        partition_names)
                    if wqi__mpic != devv__zazgr:
                        vviy__cblu = devv__zazgr - wqi__mpic
                        ngrzx__ziyue = wqi__mpic - devv__zazgr
                        jgmvu__xocn = (
                            f'Schema in {dyfm__lgma} was different.\n')
                        if vviy__cblu:
                            jgmvu__xocn += f"""File contains column(s) {vviy__cblu} not found in other files in the dataset.
"""
                        if ngrzx__ziyue:
                            jgmvu__xocn += f"""File missing column(s) {ngrzx__ziyue} found in other files in the dataset.
"""
                        raise BodoError(jgmvu__xocn)
                    try:
                        fbr__lql.schema = unify_schemas([fbr__lql.schema,
                            osngg__uyhap])
                    except Exception as ylyes__oghlj:
                        jgmvu__xocn = (
                            f'Schema in {dyfm__lgma} was different.\n' +
                            str(ylyes__oghlj))
                        raise BodoError(jgmvu__xocn)
                lky__kwbn = time.time()
                dwst__tbp = frag.scanner(schema=kpq__cebyf.schema, filter=
                    expr_filters, use_threads=True).count_rows()
                vmx__yxjc += time.time() - lky__kwbn
                dyfm__lgma._bodo_num_rows = dwst__tbp
                wxmh__snd += dwst__tbp
                okp__djllu += frag.num_row_groups
                wgyvk__mznq += sum(vug__ekjg.total_byte_size for vug__ekjg in
                    frag.row_groups)
        except Exception as ylyes__oghlj:
            jjzr__qze = ylyes__oghlj
        if simv__xzj.allreduce(jjzr__qze is not None, op=MPI.LOR):
            for jjzr__qze in simv__xzj.allgather(jjzr__qze):
                if jjzr__qze:
                    if isinstance(fpath, list) and isinstance(jjzr__qze, (
                        OSError, FileNotFoundError)):
                        raise BodoError(str(jjzr__qze) +
                            list_of_files_error_msg)
                    raise jjzr__qze
        if ypvwf__utai:
            nlhf__vouff = simv__xzj.allreduce(nlhf__vouff, op=MPI.LAND)
            if not nlhf__vouff:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            fbr__lql._bodo_total_rows = simv__xzj.allreduce(wxmh__snd, op=
                MPI.SUM)
            ggo__iww = simv__xzj.allreduce(okp__djllu, op=MPI.SUM)
            xbvx__xcn = simv__xzj.allreduce(wgyvk__mznq, op=MPI.SUM)
            icwdi__ytm = np.array([qnz__xrmm._bodo_num_rows for qnz__xrmm in
                fbr__lql.pieces])
            icwdi__ytm = simv__xzj.allreduce(icwdi__ytm, op=MPI.SUM)
            for qnz__xrmm, vxb__ghct in zip(fbr__lql.pieces, icwdi__ytm):
                qnz__xrmm._bodo_num_rows = vxb__ghct
            if is_parallel and bodo.get_rank(
                ) == 0 and ggo__iww < bodo.get_size() and ggo__iww != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({ggo__iww}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if ggo__iww == 0:
                uft__lywu = 0
            else:
                uft__lywu = xbvx__xcn // ggo__iww
            if (bodo.get_rank() == 0 and xbvx__xcn >= 20 * 1048576 and 
                uft__lywu < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({uft__lywu} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                rtlwc__ail.add_attribute('g_total_num_row_groups', ggo__iww)
                rtlwc__ail.add_attribute('total_scan_time', vmx__yxjc)
                xhxhd__lythf = np.array([qnz__xrmm._bodo_num_rows for
                    qnz__xrmm in fbr__lql.pieces])
                osz__iiv = np.percentile(xhxhd__lythf, [25, 50, 75])
                rtlwc__ail.add_attribute('g_row_counts_min', xhxhd__lythf.min()
                    )
                rtlwc__ail.add_attribute('g_row_counts_Q1', osz__iiv[0])
                rtlwc__ail.add_attribute('g_row_counts_median', osz__iiv[1])
                rtlwc__ail.add_attribute('g_row_counts_Q3', osz__iiv[2])
                rtlwc__ail.add_attribute('g_row_counts_max', xhxhd__lythf.max()
                    )
                rtlwc__ail.add_attribute('g_row_counts_mean', xhxhd__lythf.
                    mean())
                rtlwc__ail.add_attribute('g_row_counts_std', xhxhd__lythf.std()
                    )
                rtlwc__ail.add_attribute('g_row_counts_sum', xhxhd__lythf.sum()
                    )
                rtlwc__ail.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(fbr__lql)
    if get_row_counts:
        jljo__zmf.finalize()
    if ypvwf__utai and is_parallel:
        if tracing.is_tracing():
            esiw__rsm = tracing.Event('unify_schemas_across_ranks')
        jjzr__qze = None
        try:
            fbr__lql.schema = simv__xzj.allreduce(fbr__lql.schema, bodo.io.
                helpers.pa_schema_unify_mpi_op)
        except Exception as ylyes__oghlj:
            jjzr__qze = ylyes__oghlj
        if tracing.is_tracing():
            esiw__rsm.finalize()
        if simv__xzj.allreduce(jjzr__qze is not None, op=MPI.LOR):
            for jjzr__qze in simv__xzj.allgather(jjzr__qze):
                if jjzr__qze:
                    jgmvu__xocn = (
                        f'Schema in some files were different.\n' + str(
                        jjzr__qze))
                    raise BodoError(jgmvu__xocn)
    return fbr__lql


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    dohg__iiltc = os.cpu_count()
    if dohg__iiltc is None or dohg__iiltc == 0:
        dohg__iiltc = 2
    acmb__agyo = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), dohg__iiltc
        )
    sul__qxh = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)), dohg__iiltc)
    if is_parallel and len(fpaths) > sul__qxh and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(sul__qxh)
        pa.set_cpu_count(sul__qxh)
    else:
        pa.set_io_thread_count(acmb__agyo)
        pa.set_cpu_count(acmb__agyo)
    vfvz__ehg = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    ohydg__mub = set(str_as_dict_cols)
    for xrg__ook, name in enumerate(schema.names):
        if name in ohydg__mub:
            olpc__fsmsg = schema.field(xrg__ook)
            bbq__dnl = pa.field(name, pa.dictionary(pa.int32(), olpc__fsmsg
                .type), olpc__fsmsg.nullable)
            schema = schema.remove(xrg__ook).insert(xrg__ook, bbq__dnl)
    fbr__lql = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=vfvz__ehg)
    col_names = fbr__lql.schema.names
    kqv__sfvhn = [col_names[olp__fhi] for olp__fhi in selected_fields]
    rjltg__puvle = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if rjltg__puvle and expr_filters is None:
        nmled__uqt = []
        gswzb__zqgyh = 0
        rpix__zoar = 0
        for frag in fbr__lql.get_fragments():
            andr__blgws = []
            for vug__ekjg in frag.row_groups:
                lykp__trkx = vug__ekjg.num_rows
                if start_offset < gswzb__zqgyh + lykp__trkx:
                    if rpix__zoar == 0:
                        mhdj__vel = start_offset - gswzb__zqgyh
                        gon__eqrj = min(lykp__trkx - mhdj__vel, rows_to_read)
                    else:
                        gon__eqrj = min(lykp__trkx, rows_to_read - rpix__zoar)
                    rpix__zoar += gon__eqrj
                    andr__blgws.append(vug__ekjg.id)
                gswzb__zqgyh += lykp__trkx
                if rpix__zoar == rows_to_read:
                    break
            nmled__uqt.append(frag.subset(row_group_ids=andr__blgws))
            if rpix__zoar == rows_to_read:
                break
        fbr__lql = ds.FileSystemDataset(nmled__uqt, fbr__lql.schema,
            vfvz__ehg, filesystem=fbr__lql.filesystem)
        start_offset = mhdj__vel
    eqn__ljp = fbr__lql.scanner(columns=kqv__sfvhn, filter=expr_filters,
        use_threads=True).to_reader()
    return fbr__lql, eqn__ljp, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    fsl__kbt = [c for c in pa_schema.names if isinstance(pa_schema.field(c)
        .type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(fsl__kbt) == 0:
        pq_dataset._category_info = {}
        return
    simv__xzj = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            ucypn__fynz = pq_dataset.pieces[0].frag.head(100, columns=fsl__kbt)
            oozuw__wnkzq = {c: tuple(ucypn__fynz.column(c).chunk(0).
                dictionary.to_pylist()) for c in fsl__kbt}
            del ucypn__fynz
        except Exception as ylyes__oghlj:
            simv__xzj.bcast(ylyes__oghlj)
            raise ylyes__oghlj
        simv__xzj.bcast(oozuw__wnkzq)
    else:
        oozuw__wnkzq = simv__xzj.bcast(None)
        if isinstance(oozuw__wnkzq, Exception):
            jjzr__qze = oozuw__wnkzq
            raise jjzr__qze
    pq_dataset._category_info = oozuw__wnkzq


def get_pandas_metadata(schema, num_pieces):
    dzb__bcgj = None
    xoqg__oev = defaultdict(lambda : None)
    mpftm__kht = b'pandas'
    if schema.metadata is not None and mpftm__kht in schema.metadata:
        import json
        phi__psld = json.loads(schema.metadata[mpftm__kht].decode('utf8'))
        omc__whlje = len(phi__psld['index_columns'])
        if omc__whlje > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        dzb__bcgj = phi__psld['index_columns'][0] if omc__whlje else None
        if not isinstance(dzb__bcgj, str) and not isinstance(dzb__bcgj, dict):
            dzb__bcgj = None
        for ttqrr__ikwtq in phi__psld['columns']:
            dbt__brdsk = ttqrr__ikwtq['name']
            if ttqrr__ikwtq['pandas_type'].startswith('int'
                ) and dbt__brdsk is not None:
                if ttqrr__ikwtq['numpy_type'].startswith('Int'):
                    xoqg__oev[dbt__brdsk] = True
                else:
                    xoqg__oev[dbt__brdsk] = False
    return dzb__bcgj, xoqg__oev


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for dbt__brdsk in pa_schema.names:
        nql__ghk = pa_schema.field(dbt__brdsk)
        if nql__ghk.type in (pa.string(), pa.large_string()):
            str_columns.append(dbt__brdsk)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    simv__xzj = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        hcknp__himbr = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        hcknp__himbr = pq_dataset.pieces
    pqvu__favgo = np.zeros(len(str_columns), dtype=np.int64)
    ibwpt__tqvm = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(hcknp__himbr):
        dyfm__lgma = hcknp__himbr[bodo.get_rank()]
        try:
            metadata = dyfm__lgma.metadata
            for xrg__ook in range(dyfm__lgma.num_row_groups):
                for xkl__clk, dbt__brdsk in enumerate(str_columns):
                    pplxg__xwlra = pa_schema.get_field_index(dbt__brdsk)
                    pqvu__favgo[xkl__clk] += metadata.row_group(xrg__ook
                        ).column(pplxg__xwlra).total_uncompressed_size
            zjsu__eun = metadata.num_rows
        except Exception as ylyes__oghlj:
            if isinstance(ylyes__oghlj, (OSError, FileNotFoundError)):
                zjsu__eun = 0
            else:
                raise
    else:
        zjsu__eun = 0
    ifmc__yrx = simv__xzj.allreduce(zjsu__eun, op=MPI.SUM)
    if ifmc__yrx == 0:
        return set()
    simv__xzj.Allreduce(pqvu__favgo, ibwpt__tqvm, op=MPI.SUM)
    zjj__mvljk = ibwpt__tqvm / ifmc__yrx
    bsc__coyr = set()
    for xrg__ook, ejigw__zbl in enumerate(zjj__mvljk):
        if ejigw__zbl < READ_STR_AS_DICT_THRESHOLD:
            dbt__brdsk = str_columns[xrg__ook][0]
            bsc__coyr.add(dbt__brdsk)
    return bsc__coyr


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    xkzg__winlf = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    boru__bkgu = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    eww__wlz = read_as_dict_cols - boru__bkgu
    if len(eww__wlz) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {eww__wlz}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(boru__bkgu)
    boru__bkgu = boru__bkgu - read_as_dict_cols
    str_columns = [tzphf__fggg for tzphf__fggg in str_columns if 
        tzphf__fggg in boru__bkgu]
    bsc__coyr: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    bsc__coyr.update(read_as_dict_cols)
    col_names = pa_schema.names
    dzb__bcgj, xoqg__oev = get_pandas_metadata(pa_schema, num_pieces)
    lem__mpd = []
    qpc__orpgj = []
    nnl__flu = []
    for xrg__ook, c in enumerate(col_names):
        if c in partition_names:
            continue
        nql__ghk = pa_schema.field(c)
        jjymt__xrj, xukov__xwnuo = _get_numba_typ_from_pa_typ(nql__ghk, c ==
            dzb__bcgj, xoqg__oev[c], pq_dataset._category_info, str_as_dict
            =c in bsc__coyr)
        lem__mpd.append(jjymt__xrj)
        qpc__orpgj.append(xukov__xwnuo)
        nnl__flu.append(nql__ghk.type)
    if partition_names:
        lem__mpd += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[xrg__ook]) for xrg__ook in range(len(
            partition_names))]
        qpc__orpgj.extend([True] * len(partition_names))
        nnl__flu.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        lem__mpd += [dict_str_arr_type]
        qpc__orpgj.append(True)
        nnl__flu.append(None)
    jzxg__knut = {c: xrg__ook for xrg__ook, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in jzxg__knut:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if dzb__bcgj and not isinstance(dzb__bcgj, dict
        ) and dzb__bcgj not in selected_columns:
        selected_columns.append(dzb__bcgj)
    col_names = selected_columns
    col_indices = []
    xkzg__winlf = []
    hzcd__sph = []
    cxmw__lup = []
    for xrg__ook, c in enumerate(col_names):
        fqx__uto = jzxg__knut[c]
        col_indices.append(fqx__uto)
        xkzg__winlf.append(lem__mpd[fqx__uto])
        if not qpc__orpgj[fqx__uto]:
            hzcd__sph.append(xrg__ook)
            cxmw__lup.append(nnl__flu[fqx__uto])
    return (col_names, xkzg__winlf, dzb__bcgj, col_indices, partition_names,
        hzcd__sph, cxmw__lup)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    tzyyf__kjmmw = dictionary.to_pandas()
    mvxr__nhzau = bodo.typeof(tzyyf__kjmmw).dtype
    if isinstance(mvxr__nhzau, types.Integer):
        wqs__jxag = PDCategoricalDtype(tuple(tzyyf__kjmmw), mvxr__nhzau, 
            False, int_type=mvxr__nhzau)
    else:
        wqs__jxag = PDCategoricalDtype(tuple(tzyyf__kjmmw), mvxr__nhzau, False)
    return CategoricalArrayType(wqs__jxag)


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
        fflkb__ursk = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        wxufx__rhstm = cgutils.get_or_insert_function(builder.module,
            fflkb__ursk, name='pq_write')
        myo__soon = builder.call(wxufx__rhstm, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return myo__soon
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
        fflkb__ursk = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        wxufx__rhstm = cgutils.get_or_insert_function(builder.module,
            fflkb__ursk, name='pq_write_partitioned')
        builder.call(wxufx__rhstm, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
