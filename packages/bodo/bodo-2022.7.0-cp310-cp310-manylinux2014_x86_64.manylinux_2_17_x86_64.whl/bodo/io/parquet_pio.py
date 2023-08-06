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
        except OSError as fnj__kyfi:
            if 'non-file path' in str(fnj__kyfi):
                raise FileNotFoundError(str(fnj__kyfi))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        hksor__xaes = lhs.scope
        lnbbq__aji = lhs.loc
        cfbqx__wrbi = None
        if lhs.name in self.locals:
            cfbqx__wrbi = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        lmn__ymttn = {}
        if lhs.name + ':convert' in self.locals:
            lmn__ymttn = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if cfbqx__wrbi is None:
            qoc__gdyy = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            bft__bruu = get_const_value(file_name, self.func_ir, qoc__gdyy,
                arg_types=self.args, file_info=ParquetFileInfo(columns,
                storage_options=storage_options, input_file_name_col=
                input_file_name_col, read_as_dict_cols=read_as_dict_cols))
            wdiz__yok = False
            wnj__yyk = guard(get_definition, self.func_ir, file_name)
            if isinstance(wnj__yyk, ir.Arg):
                typ = self.args[wnj__yyk.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, jeu__zlc, fkcus__jes, col_indices,
                        partition_names, nfzl__bimk, jxhm__rnrb) = typ.schema
                    wdiz__yok = True
            if not wdiz__yok:
                (col_names, jeu__zlc, fkcus__jes, col_indices,
                    partition_names, nfzl__bimk, jxhm__rnrb) = (
                    parquet_file_schema(bft__bruu, columns, storage_options
                    =storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            tvpoz__ilsef = list(cfbqx__wrbi.keys())
            bhixz__hkvml = {c: ksa__hpt for ksa__hpt, c in enumerate(
                tvpoz__ilsef)}
            ilby__erf = [wfpfk__kkus for wfpfk__kkus in cfbqx__wrbi.values()]
            fkcus__jes = 'index' if 'index' in bhixz__hkvml else None
            if columns is None:
                selected_columns = tvpoz__ilsef
            else:
                selected_columns = columns
            col_indices = [bhixz__hkvml[c] for c in selected_columns]
            jeu__zlc = [ilby__erf[bhixz__hkvml[c]] for c in selected_columns]
            col_names = selected_columns
            fkcus__jes = fkcus__jes if fkcus__jes in col_names else None
            partition_names = []
            nfzl__bimk = []
            jxhm__rnrb = []
        txjay__crvw = None if isinstance(fkcus__jes, dict
            ) or fkcus__jes is None else fkcus__jes
        index_column_index = None
        index_column_type = types.none
        if txjay__crvw:
            qxnhq__hpc = col_names.index(txjay__crvw)
            index_column_index = col_indices.pop(qxnhq__hpc)
            index_column_type = jeu__zlc.pop(qxnhq__hpc)
            col_names.pop(qxnhq__hpc)
        for ksa__hpt, c in enumerate(col_names):
            if c in lmn__ymttn:
                jeu__zlc[ksa__hpt] = lmn__ymttn[c]
        jhp__kzug = [ir.Var(hksor__xaes, mk_unique_var('pq_table'),
            lnbbq__aji), ir.Var(hksor__xaes, mk_unique_var('pq_index'),
            lnbbq__aji)]
        rxsdf__wenx = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.
            name, col_names, col_indices, jeu__zlc, jhp__kzug, lnbbq__aji,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, nfzl__bimk, jxhm__rnrb)]
        return (col_names, jhp__kzug, fkcus__jes, rxsdf__wenx, jeu__zlc,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    djbub__igjl = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    jefsm__ronh, hrdll__iwffa = bodo.ir.connector.generate_filter_map(pq_node
        .filters)
    extra_args = ', '.join(jefsm__ronh.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, jefsm__ronh, hrdll__iwffa, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    dms__jyfu = ', '.join(f'out{ksa__hpt}' for ksa__hpt in range(djbub__igjl))
    ujd__zrrz = f'def pq_impl(fname, {extra_args}):\n'
    ujd__zrrz += (
        f'    (total_rows, {dms__jyfu},) = _pq_reader_py(fname, {extra_args})\n'
        )
    dyyk__qtot = {}
    exec(ujd__zrrz, {}, dyyk__qtot)
    qvk__hig = dyyk__qtot['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        mxw__qvq = pq_node.loc.strformat()
        svgf__aslmf = []
        kgjl__pcb = []
        for ksa__hpt in pq_node.out_used_cols:
            nsv__fgzw = pq_node.df_colnames[ksa__hpt]
            svgf__aslmf.append(nsv__fgzw)
            if isinstance(pq_node.out_types[ksa__hpt], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                kgjl__pcb.append(nsv__fgzw)
        vfxc__nrgi = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', vfxc__nrgi,
            mxw__qvq, svgf__aslmf)
        if kgjl__pcb:
            ozeyn__ybp = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', ozeyn__ybp,
                mxw__qvq, kgjl__pcb)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        hbef__vxjst = set(pq_node.out_used_cols)
        dyfy__ueffm = set(pq_node.unsupported_columns)
        ydn__pkguw = hbef__vxjst & dyfy__ueffm
        if ydn__pkguw:
            ermzr__zch = sorted(ydn__pkguw)
            dvctu__xhzq = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            rrq__bvoij = 0
            for gaq__wtwvw in ermzr__zch:
                while pq_node.unsupported_columns[rrq__bvoij] != gaq__wtwvw:
                    rrq__bvoij += 1
                dvctu__xhzq.append(
                    f"Column '{pq_node.df_colnames[gaq__wtwvw]}' with unsupported arrow type {pq_node.unsupported_arrow_types[rrq__bvoij]}"
                    )
                rrq__bvoij += 1
            vxet__ixit = '\n'.join(dvctu__xhzq)
            raise BodoError(vxet__ixit, loc=pq_node.loc)
    szx__ehah = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.out_used_cols, pq_node.out_types, pq_node.storage_options,
        pq_node.partition_names, dnf_filter_str, expr_filter_str,
        extra_args, parallel, meta_head_only_info, pq_node.
        index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    tdydo__zwqnk = typemap[pq_node.file_name.name]
    emq__esxcf = (tdydo__zwqnk,) + tuple(typemap[igxno__kuo.name] for
        igxno__kuo in hrdll__iwffa)
    jxl__aeuh = compile_to_numba_ir(qvk__hig, {'_pq_reader_py': szx__ehah},
        typingctx=typingctx, targetctx=targetctx, arg_typs=emq__esxcf,
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(jxl__aeuh, [pq_node.file_name] + hrdll__iwffa)
    rxsdf__wenx = jxl__aeuh.body[:-3]
    if meta_head_only_info:
        rxsdf__wenx[-3].target = meta_head_only_info[1]
    rxsdf__wenx[-2].target = pq_node.out_vars[0]
    rxsdf__wenx[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        rxsdf__wenx.pop(-1)
    elif not pq_node.out_used_cols:
        rxsdf__wenx.pop(-2)
    return rxsdf__wenx


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    kqklx__forq = get_overload_const_str(dnf_filter_str)
    dggun__oiix = get_overload_const_str(expr_filter_str)
    xwf__twtw = ', '.join(f'f{ksa__hpt}' for ksa__hpt in range(len(var_tup)))
    ujd__zrrz = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        ujd__zrrz += f'  {xwf__twtw}, = var_tup\n'
    ujd__zrrz += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    ujd__zrrz += f'    dnf_filters_py = {kqklx__forq}\n'
    ujd__zrrz += f'    expr_filters_py = {dggun__oiix}\n'
    ujd__zrrz += '  return (dnf_filters_py, expr_filters_py)\n'
    dyyk__qtot = {}
    exec(ujd__zrrz, globals(), dyyk__qtot)
    return dyyk__qtot['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    igtrn__gxfd = next_label()
    rdv__pgjm = ',' if extra_args else ''
    ujd__zrrz = f'def pq_reader_py(fname,{extra_args}):\n'
    ujd__zrrz += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    ujd__zrrz += f"    ev.add_attribute('g_fname', fname)\n"
    ujd__zrrz += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{rdv__pgjm}))
"""
    ujd__zrrz += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    ujd__zrrz += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    fact__pzrya = not out_used_cols
    ecz__ieahp = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    xdu__xlszw = {c: ksa__hpt for ksa__hpt, c in enumerate(col_indices)}
    dpfu__zpyy = {c: ksa__hpt for ksa__hpt, c in enumerate(ecz__ieahp)}
    xfl__pgje = []
    gmyan__nzo = set()
    ryl__pnm = partition_names + [input_file_name_col]
    for ksa__hpt in out_used_cols:
        if ecz__ieahp[ksa__hpt] not in ryl__pnm:
            xfl__pgje.append(col_indices[ksa__hpt])
        elif not input_file_name_col or ecz__ieahp[ksa__hpt
            ] != input_file_name_col:
            gmyan__nzo.add(col_indices[ksa__hpt])
    if index_column_index is not None:
        xfl__pgje.append(index_column_index)
    xfl__pgje = sorted(xfl__pgje)
    shn__gfco = {c: ksa__hpt for ksa__hpt, c in enumerate(xfl__pgje)}
    ezooz__rfw = [(int(is_nullable(out_types[xdu__xlszw[hltd__qyeg]])) if 
        hltd__qyeg != index_column_index else int(is_nullable(
        index_column_type))) for hltd__qyeg in xfl__pgje]
    str_as_dict_cols = []
    for hltd__qyeg in xfl__pgje:
        if hltd__qyeg == index_column_index:
            wfpfk__kkus = index_column_type
        else:
            wfpfk__kkus = out_types[xdu__xlszw[hltd__qyeg]]
        if wfpfk__kkus == dict_str_arr_type:
            str_as_dict_cols.append(hltd__qyeg)
    kievh__eysk = []
    aed__esnef = {}
    geb__iizf = []
    gtg__cqxt = []
    for ksa__hpt, vppgv__qok in enumerate(partition_names):
        try:
            ncr__ecnwu = dpfu__zpyy[vppgv__qok]
            if col_indices[ncr__ecnwu] not in gmyan__nzo:
                continue
        except (KeyError, ValueError) as mfat__ysfr:
            continue
        aed__esnef[vppgv__qok] = len(kievh__eysk)
        kievh__eysk.append(vppgv__qok)
        geb__iizf.append(ksa__hpt)
        uci__ipgkw = out_types[ncr__ecnwu].dtype
        ikht__cbc = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            uci__ipgkw)
        gtg__cqxt.append(numba_to_c_type(ikht__cbc))
    ujd__zrrz += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    ujd__zrrz += f'    out_table = pq_read(\n'
    ujd__zrrz += f'        fname_py, {is_parallel},\n'
    ujd__zrrz += f'        dnf_filters, expr_filters,\n'
    ujd__zrrz += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{igtrn__gxfd}.ctypes,
"""
    ujd__zrrz += f'        {len(xfl__pgje)},\n'
    ujd__zrrz += f'        nullable_cols_arr_{igtrn__gxfd}.ctypes,\n'
    if len(geb__iizf) > 0:
        ujd__zrrz += f'        np.array({geb__iizf}, dtype=np.int32).ctypes,\n'
        ujd__zrrz += f'        np.array({gtg__cqxt}, dtype=np.int32).ctypes,\n'
        ujd__zrrz += f'        {len(geb__iizf)},\n'
    else:
        ujd__zrrz += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        ujd__zrrz += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        ujd__zrrz += f'        0, 0,\n'
    ujd__zrrz += f'        total_rows_np.ctypes,\n'
    ujd__zrrz += f'        {input_file_name_col is not None},\n'
    ujd__zrrz += f'    )\n'
    ujd__zrrz += f'    check_and_propagate_cpp_exception()\n'
    hhchv__ttwde = 'None'
    xwag__rsilv = index_column_type
    hskn__hxryi = TableType(tuple(out_types))
    if fact__pzrya:
        hskn__hxryi = types.none
    if index_column_index is not None:
        bfdv__zsjb = shn__gfco[index_column_index]
        hhchv__ttwde = (
            f'info_to_array(info_from_table(out_table, {bfdv__zsjb}), index_arr_type)'
            )
    ujd__zrrz += f'    index_arr = {hhchv__ttwde}\n'
    if fact__pzrya:
        ppqc__xtzw = None
    else:
        ppqc__xtzw = []
        wscrp__ywf = 0
        vluy__mzo = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for ksa__hpt, gaq__wtwvw in enumerate(col_indices):
            if wscrp__ywf < len(out_used_cols) and ksa__hpt == out_used_cols[
                wscrp__ywf]:
                yhbz__bqlzp = col_indices[ksa__hpt]
                if vluy__mzo and yhbz__bqlzp == vluy__mzo:
                    ppqc__xtzw.append(len(xfl__pgje) + len(kievh__eysk))
                elif yhbz__bqlzp in gmyan__nzo:
                    mdig__qdh = ecz__ieahp[ksa__hpt]
                    ppqc__xtzw.append(len(xfl__pgje) + aed__esnef[mdig__qdh])
                else:
                    ppqc__xtzw.append(shn__gfco[gaq__wtwvw])
                wscrp__ywf += 1
            else:
                ppqc__xtzw.append(-1)
        ppqc__xtzw = np.array(ppqc__xtzw, dtype=np.int64)
    if fact__pzrya:
        ujd__zrrz += '    T = None\n'
    else:
        ujd__zrrz += f"""    T = cpp_table_to_py_table(out_table, table_idx_{igtrn__gxfd}, py_table_type_{igtrn__gxfd})
"""
    ujd__zrrz += f'    delete_table(out_table)\n'
    ujd__zrrz += f'    total_rows = total_rows_np[0]\n'
    ujd__zrrz += f'    ev.finalize()\n'
    ujd__zrrz += f'    return (total_rows, T, index_arr)\n'
    dyyk__qtot = {}
    bucoh__emtv = {f'py_table_type_{igtrn__gxfd}': hskn__hxryi,
        f'table_idx_{igtrn__gxfd}': ppqc__xtzw,
        f'selected_cols_arr_{igtrn__gxfd}': np.array(xfl__pgje, np.int32),
        f'nullable_cols_arr_{igtrn__gxfd}': np.array(ezooz__rfw, np.int32),
        'index_arr_type': xwag__rsilv, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(ujd__zrrz, bucoh__emtv, dyyk__qtot)
    szx__ehah = dyyk__qtot['pq_reader_py']
    gkl__yzf = numba.njit(szx__ehah, no_cpython_wrapper=True)
    return gkl__yzf


def unify_schemas(schemas):
    yqcbm__zvk = []
    for schema in schemas:
        for ksa__hpt in range(len(schema)):
            yaped__rirnn = schema.field(ksa__hpt)
            if yaped__rirnn.type == pa.large_string():
                schema = schema.set(ksa__hpt, yaped__rirnn.with_type(pa.
                    string()))
            elif yaped__rirnn.type == pa.large_binary():
                schema = schema.set(ksa__hpt, yaped__rirnn.with_type(pa.
                    binary()))
            elif isinstance(yaped__rirnn.type, (pa.ListType, pa.LargeListType)
                ) and yaped__rirnn.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(ksa__hpt, yaped__rirnn.with_type(pa.
                    list_(pa.field(yaped__rirnn.type.value_field.name, pa.
                    string()))))
            elif isinstance(yaped__rirnn.type, pa.LargeListType):
                schema = schema.set(ksa__hpt, yaped__rirnn.with_type(pa.
                    list_(pa.field(yaped__rirnn.type.value_field.name,
                    yaped__rirnn.type.value_type))))
        yqcbm__zvk.append(schema)
    return pa.unify_schemas(yqcbm__zvk)


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
        for ksa__hpt in range(len(self.schema)):
            yaped__rirnn = self.schema.field(ksa__hpt)
            if yaped__rirnn.type == pa.large_string():
                self.schema = self.schema.set(ksa__hpt, yaped__rirnn.
                    with_type(pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for nxryt__kktwm in self.pieces:
            nxryt__kktwm.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            slvzu__umyua = {nxryt__kktwm: self.partitioning_dictionaries[
                ksa__hpt] for ksa__hpt, nxryt__kktwm in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, slvzu__umyua)


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
            self.partition_keys = [(vppgv__qok, partitioning.dictionaries[
                ksa__hpt].index(self.partition_keys[vppgv__qok]).as_py()) for
                ksa__hpt, vppgv__qok in enumerate(partition_names)]

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
        crvk__bch = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    bsent__iazg = MPI.COMM_WORLD
    if isinstance(fpath, list):
        svaz__junc = urlparse(fpath[0])
        protocol = svaz__junc.scheme
        pxc__ptvv = svaz__junc.netloc
        for ksa__hpt in range(len(fpath)):
            yaped__rirnn = fpath[ksa__hpt]
            abs__hht = urlparse(yaped__rirnn)
            if abs__hht.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if abs__hht.netloc != pxc__ptvv:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[ksa__hpt] = yaped__rirnn.rstrip('/')
    else:
        svaz__junc = urlparse(fpath)
        protocol = svaz__junc.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as mfat__ysfr:
            ijuiu__apcbf = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(ijuiu__apcbf)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as mfat__ysfr:
            ijuiu__apcbf = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            ootwr__fko = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(ootwr__fko)))
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
            davhz__mjf = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(davhz__mjf) == 0:
            raise BodoError('No files found matching glob pattern')
        return davhz__mjf
    flb__hrqbx = False
    if get_row_counts:
        lcsyt__mwwlf = getfs(parallel=True)
        flb__hrqbx = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        mhz__aba = 1
        bhmg__sww = os.cpu_count()
        if bhmg__sww is not None and bhmg__sww > 1:
            mhz__aba = bhmg__sww // 2
        try:
            if get_row_counts:
                ppny__mmvyu = tracing.Event('pq.ParquetDataset',
                    is_parallel=False)
                if tracing.is_tracing():
                    ppny__mmvyu.add_attribute('g_dnf_filter', str(dnf_filters))
            rfeo__thsu = pa.io_thread_count()
            pa.set_io_thread_count(mhz__aba)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{svaz__junc.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    nwf__jxp = [yaped__rirnn[len(prefix):] for yaped__rirnn in
                        fpath]
                else:
                    nwf__jxp = fpath[len(prefix):]
            else:
                nwf__jxp = fpath
            if isinstance(nwf__jxp, list):
                fqmfh__jts = []
                for nxryt__kktwm in nwf__jxp:
                    if has_magic(nxryt__kktwm):
                        fqmfh__jts += glob(protocol, getfs(), nxryt__kktwm)
                    else:
                        fqmfh__jts.append(nxryt__kktwm)
                nwf__jxp = fqmfh__jts
            elif has_magic(nwf__jxp):
                nwf__jxp = glob(protocol, getfs(), nwf__jxp)
            irazt__stql = pq.ParquetDataset(nwf__jxp, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                irazt__stql._filters = dnf_filters
                irazt__stql._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            oyh__epnsu = len(irazt__stql.files)
            irazt__stql = ParquetDataset(irazt__stql, prefix)
            pa.set_io_thread_count(rfeo__thsu)
            if typing_pa_schema:
                irazt__stql.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    ppny__mmvyu.add_attribute('num_pieces_before_filter',
                        oyh__epnsu)
                    ppny__mmvyu.add_attribute('num_pieces_after_filter',
                        len(irazt__stql.pieces))
                ppny__mmvyu.finalize()
        except Exception as fnj__kyfi:
            if isinstance(fnj__kyfi, IsADirectoryError):
                fnj__kyfi = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(fnj__kyfi, (OSError,
                FileNotFoundError)):
                fnj__kyfi = BodoError(str(fnj__kyfi) + list_of_files_error_msg)
            else:
                fnj__kyfi = BodoError(
                    f"""error from pyarrow: {type(fnj__kyfi).__name__}: {str(fnj__kyfi)}
"""
                    )
            bsent__iazg.bcast(fnj__kyfi)
            raise fnj__kyfi
        if get_row_counts:
            wlh__pcgbz = tracing.Event('bcast dataset')
        irazt__stql = bsent__iazg.bcast(irazt__stql)
    else:
        if get_row_counts:
            wlh__pcgbz = tracing.Event('bcast dataset')
        irazt__stql = bsent__iazg.bcast(None)
        if isinstance(irazt__stql, Exception):
            uauu__pog = irazt__stql
            raise uauu__pog
    irazt__stql.set_fs(getfs())
    if get_row_counts:
        wlh__pcgbz.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = flb__hrqbx = False
    if get_row_counts or flb__hrqbx:
        if get_row_counts and tracing.is_tracing():
            txc__rjq = tracing.Event('get_row_counts')
            txc__rjq.add_attribute('g_num_pieces', len(irazt__stql.pieces))
            txc__rjq.add_attribute('g_expr_filters', str(expr_filters))
        bzcxc__nqcit = 0.0
        num_pieces = len(irazt__stql.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        jigqk__jntlf = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        vws__eltul = 0
        iyvo__uwk = 0
        omcng__bafal = 0
        jkfm__pjlqb = True
        if expr_filters is not None:
            import random
            random.seed(37)
            nlkp__gazk = random.sample(irazt__stql.pieces, k=len(
                irazt__stql.pieces))
        else:
            nlkp__gazk = irazt__stql.pieces
        fpaths = [nxryt__kktwm.path for nxryt__kktwm in nlkp__gazk[start:
            jigqk__jntlf]]
        mhz__aba = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(mhz__aba)
        pa.set_cpu_count(mhz__aba)
        uauu__pog = None
        try:
            ywwol__zrq = ds.dataset(fpaths, filesystem=irazt__stql.
                filesystem, partitioning=irazt__stql.partitioning)
            for skyk__ajae, frag in zip(nlkp__gazk[start:jigqk__jntlf],
                ywwol__zrq.get_fragments()):
                if flb__hrqbx:
                    mgikf__jqm = frag.metadata.schema.to_arrow_schema()
                    dfc__sld = set(mgikf__jqm.names)
                    iwsgz__aqju = set(irazt__stql.schema.names) - set(
                        irazt__stql.partition_names)
                    if iwsgz__aqju != dfc__sld:
                        smeqd__ach = dfc__sld - iwsgz__aqju
                        lqo__edmd = iwsgz__aqju - dfc__sld
                        qoc__gdyy = f'Schema in {skyk__ajae} was different.\n'
                        if smeqd__ach:
                            qoc__gdyy += f"""File contains column(s) {smeqd__ach} not found in other files in the dataset.
"""
                        if lqo__edmd:
                            qoc__gdyy += f"""File missing column(s) {lqo__edmd} found in other files in the dataset.
"""
                        raise BodoError(qoc__gdyy)
                    try:
                        irazt__stql.schema = unify_schemas([irazt__stql.
                            schema, mgikf__jqm])
                    except Exception as fnj__kyfi:
                        qoc__gdyy = (
                            f'Schema in {skyk__ajae} was different.\n' +
                            str(fnj__kyfi))
                        raise BodoError(qoc__gdyy)
                orlzu__uvi = time.time()
                pfn__cdobk = frag.scanner(schema=ywwol__zrq.schema, filter=
                    expr_filters, use_threads=True).count_rows()
                bzcxc__nqcit += time.time() - orlzu__uvi
                skyk__ajae._bodo_num_rows = pfn__cdobk
                vws__eltul += pfn__cdobk
                iyvo__uwk += frag.num_row_groups
                omcng__bafal += sum(rreji__thftk.total_byte_size for
                    rreji__thftk in frag.row_groups)
        except Exception as fnj__kyfi:
            uauu__pog = fnj__kyfi
        if bsent__iazg.allreduce(uauu__pog is not None, op=MPI.LOR):
            for uauu__pog in bsent__iazg.allgather(uauu__pog):
                if uauu__pog:
                    if isinstance(fpath, list) and isinstance(uauu__pog, (
                        OSError, FileNotFoundError)):
                        raise BodoError(str(uauu__pog) +
                            list_of_files_error_msg)
                    raise uauu__pog
        if flb__hrqbx:
            jkfm__pjlqb = bsent__iazg.allreduce(jkfm__pjlqb, op=MPI.LAND)
            if not jkfm__pjlqb:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            irazt__stql._bodo_total_rows = bsent__iazg.allreduce(vws__eltul,
                op=MPI.SUM)
            nkuj__xys = bsent__iazg.allreduce(iyvo__uwk, op=MPI.SUM)
            tgjf__dwhlr = bsent__iazg.allreduce(omcng__bafal, op=MPI.SUM)
            opsxe__qlrh = np.array([nxryt__kktwm._bodo_num_rows for
                nxryt__kktwm in irazt__stql.pieces])
            opsxe__qlrh = bsent__iazg.allreduce(opsxe__qlrh, op=MPI.SUM)
            for nxryt__kktwm, couqb__xzm in zip(irazt__stql.pieces, opsxe__qlrh
                ):
                nxryt__kktwm._bodo_num_rows = couqb__xzm
            if is_parallel and bodo.get_rank(
                ) == 0 and nkuj__xys < bodo.get_size() and nkuj__xys != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({nkuj__xys}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if nkuj__xys == 0:
                vjs__cpq = 0
            else:
                vjs__cpq = tgjf__dwhlr // nkuj__xys
            if (bodo.get_rank() == 0 and tgjf__dwhlr >= 20 * 1048576 and 
                vjs__cpq < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({vjs__cpq} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                txc__rjq.add_attribute('g_total_num_row_groups', nkuj__xys)
                txc__rjq.add_attribute('total_scan_time', bzcxc__nqcit)
                lqvku__sdwq = np.array([nxryt__kktwm._bodo_num_rows for
                    nxryt__kktwm in irazt__stql.pieces])
                nmtdx__xngdu = np.percentile(lqvku__sdwq, [25, 50, 75])
                txc__rjq.add_attribute('g_row_counts_min', lqvku__sdwq.min())
                txc__rjq.add_attribute('g_row_counts_Q1', nmtdx__xngdu[0])
                txc__rjq.add_attribute('g_row_counts_median', nmtdx__xngdu[1])
                txc__rjq.add_attribute('g_row_counts_Q3', nmtdx__xngdu[2])
                txc__rjq.add_attribute('g_row_counts_max', lqvku__sdwq.max())
                txc__rjq.add_attribute('g_row_counts_mean', lqvku__sdwq.mean())
                txc__rjq.add_attribute('g_row_counts_std', lqvku__sdwq.std())
                txc__rjq.add_attribute('g_row_counts_sum', lqvku__sdwq.sum())
                txc__rjq.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(irazt__stql)
    if get_row_counts:
        crvk__bch.finalize()
    if flb__hrqbx and is_parallel:
        if tracing.is_tracing():
            jgkx__qcqvj = tracing.Event('unify_schemas_across_ranks')
        uauu__pog = None
        try:
            irazt__stql.schema = bsent__iazg.allreduce(irazt__stql.schema,
                bodo.io.helpers.pa_schema_unify_mpi_op)
        except Exception as fnj__kyfi:
            uauu__pog = fnj__kyfi
        if tracing.is_tracing():
            jgkx__qcqvj.finalize()
        if bsent__iazg.allreduce(uauu__pog is not None, op=MPI.LOR):
            for uauu__pog in bsent__iazg.allgather(uauu__pog):
                if uauu__pog:
                    qoc__gdyy = (f'Schema in some files were different.\n' +
                        str(uauu__pog))
                    raise BodoError(qoc__gdyy)
    return irazt__stql


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    bhmg__sww = os.cpu_count()
    if bhmg__sww is None or bhmg__sww == 0:
        bhmg__sww = 2
    iro__kiip = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), bhmg__sww)
    uzpin__whqzo = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)),
        bhmg__sww)
    if is_parallel and len(fpaths) > uzpin__whqzo and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(uzpin__whqzo)
        pa.set_cpu_count(uzpin__whqzo)
    else:
        pa.set_io_thread_count(iro__kiip)
        pa.set_cpu_count(iro__kiip)
    vzhqj__bcqxg = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    ifanu__juo = set(str_as_dict_cols)
    for ksa__hpt, name in enumerate(schema.names):
        if name in ifanu__juo:
            xpj__nff = schema.field(ksa__hpt)
            jpkcl__smvoa = pa.field(name, pa.dictionary(pa.int32(),
                xpj__nff.type), xpj__nff.nullable)
            schema = schema.remove(ksa__hpt).insert(ksa__hpt, jpkcl__smvoa)
    irazt__stql = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=vzhqj__bcqxg)
    col_names = irazt__stql.schema.names
    urqq__bcbb = [col_names[ovjl__kpdk] for ovjl__kpdk in selected_fields]
    sbwrb__czh = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if sbwrb__czh and expr_filters is None:
        cmabw__ipmus = []
        mjr__ampmq = 0
        lidh__xdln = 0
        for frag in irazt__stql.get_fragments():
            nsrhd__uag = []
            for rreji__thftk in frag.row_groups:
                qvax__anpi = rreji__thftk.num_rows
                if start_offset < mjr__ampmq + qvax__anpi:
                    if lidh__xdln == 0:
                        cex__nhsvj = start_offset - mjr__ampmq
                        fxblw__pjyt = min(qvax__anpi - cex__nhsvj, rows_to_read
                            )
                    else:
                        fxblw__pjyt = min(qvax__anpi, rows_to_read - lidh__xdln
                            )
                    lidh__xdln += fxblw__pjyt
                    nsrhd__uag.append(rreji__thftk.id)
                mjr__ampmq += qvax__anpi
                if lidh__xdln == rows_to_read:
                    break
            cmabw__ipmus.append(frag.subset(row_group_ids=nsrhd__uag))
            if lidh__xdln == rows_to_read:
                break
        irazt__stql = ds.FileSystemDataset(cmabw__ipmus, irazt__stql.schema,
            vzhqj__bcqxg, filesystem=irazt__stql.filesystem)
        start_offset = cex__nhsvj
    orci__bbslq = irazt__stql.scanner(columns=urqq__bcbb, filter=
        expr_filters, use_threads=True).to_reader()
    return irazt__stql, orci__bbslq, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    jxo__ghckl = [c for c in pa_schema.names if isinstance(pa_schema.field(
        c).type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(jxo__ghckl) == 0:
        pq_dataset._category_info = {}
        return
    bsent__iazg = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            suj__jshrr = pq_dataset.pieces[0].frag.head(100, columns=jxo__ghckl
                )
            yqr__ooegh = {c: tuple(suj__jshrr.column(c).chunk(0).dictionary
                .to_pylist()) for c in jxo__ghckl}
            del suj__jshrr
        except Exception as fnj__kyfi:
            bsent__iazg.bcast(fnj__kyfi)
            raise fnj__kyfi
        bsent__iazg.bcast(yqr__ooegh)
    else:
        yqr__ooegh = bsent__iazg.bcast(None)
        if isinstance(yqr__ooegh, Exception):
            uauu__pog = yqr__ooegh
            raise uauu__pog
    pq_dataset._category_info = yqr__ooegh


def get_pandas_metadata(schema, num_pieces):
    fkcus__jes = None
    qmr__kcd = defaultdict(lambda : None)
    lvd__iyqzl = b'pandas'
    if schema.metadata is not None and lvd__iyqzl in schema.metadata:
        import json
        kmzw__tumgy = json.loads(schema.metadata[lvd__iyqzl].decode('utf8'))
        kseux__vto = len(kmzw__tumgy['index_columns'])
        if kseux__vto > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        fkcus__jes = kmzw__tumgy['index_columns'][0] if kseux__vto else None
        if not isinstance(fkcus__jes, str) and not isinstance(fkcus__jes, dict
            ):
            fkcus__jes = None
        for quhk__ihoui in kmzw__tumgy['columns']:
            lqnwd__mtfq = quhk__ihoui['name']
            if quhk__ihoui['pandas_type'].startswith('int'
                ) and lqnwd__mtfq is not None:
                if quhk__ihoui['numpy_type'].startswith('Int'):
                    qmr__kcd[lqnwd__mtfq] = True
                else:
                    qmr__kcd[lqnwd__mtfq] = False
    return fkcus__jes, qmr__kcd


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for lqnwd__mtfq in pa_schema.names:
        gfr__iloi = pa_schema.field(lqnwd__mtfq)
        if gfr__iloi.type in (pa.string(), pa.large_string()):
            str_columns.append(lqnwd__mtfq)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    bsent__iazg = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        nlkp__gazk = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        nlkp__gazk = pq_dataset.pieces
    wifg__uew = np.zeros(len(str_columns), dtype=np.int64)
    oaq__slrmx = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(nlkp__gazk):
        skyk__ajae = nlkp__gazk[bodo.get_rank()]
        try:
            metadata = skyk__ajae.metadata
            for ksa__hpt in range(skyk__ajae.num_row_groups):
                for wscrp__ywf, lqnwd__mtfq in enumerate(str_columns):
                    rrq__bvoij = pa_schema.get_field_index(lqnwd__mtfq)
                    wifg__uew[wscrp__ywf] += metadata.row_group(ksa__hpt
                        ).column(rrq__bvoij).total_uncompressed_size
            qzrn__mvde = metadata.num_rows
        except Exception as fnj__kyfi:
            if isinstance(fnj__kyfi, (OSError, FileNotFoundError)):
                qzrn__mvde = 0
            else:
                raise
    else:
        qzrn__mvde = 0
    yqqro__zuigk = bsent__iazg.allreduce(qzrn__mvde, op=MPI.SUM)
    if yqqro__zuigk == 0:
        return set()
    bsent__iazg.Allreduce(wifg__uew, oaq__slrmx, op=MPI.SUM)
    fioil__ykde = oaq__slrmx / yqqro__zuigk
    wwzw__bthmk = set()
    for ksa__hpt, lkd__ykzdu in enumerate(fioil__ykde):
        if lkd__ykzdu < READ_STR_AS_DICT_THRESHOLD:
            lqnwd__mtfq = str_columns[ksa__hpt][0]
            wwzw__bthmk.add(lqnwd__mtfq)
    return wwzw__bthmk


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    jeu__zlc = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    ftevk__hsjsu = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    gek__wzd = read_as_dict_cols - ftevk__hsjsu
    if len(gek__wzd) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {gek__wzd}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(ftevk__hsjsu)
    ftevk__hsjsu = ftevk__hsjsu - read_as_dict_cols
    str_columns = [jdeq__mcdvp for jdeq__mcdvp in str_columns if 
        jdeq__mcdvp in ftevk__hsjsu]
    wwzw__bthmk: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    wwzw__bthmk.update(read_as_dict_cols)
    col_names = pa_schema.names
    fkcus__jes, qmr__kcd = get_pandas_metadata(pa_schema, num_pieces)
    ilby__erf = []
    jmese__tlr = []
    wupo__zmnpb = []
    for ksa__hpt, c in enumerate(col_names):
        if c in partition_names:
            continue
        gfr__iloi = pa_schema.field(c)
        focey__zcd, zqr__cszk = _get_numba_typ_from_pa_typ(gfr__iloi, c ==
            fkcus__jes, qmr__kcd[c], pq_dataset._category_info, str_as_dict
            =c in wwzw__bthmk)
        ilby__erf.append(focey__zcd)
        jmese__tlr.append(zqr__cszk)
        wupo__zmnpb.append(gfr__iloi.type)
    if partition_names:
        ilby__erf += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[ksa__hpt]) for ksa__hpt in range(len(
            partition_names))]
        jmese__tlr.extend([True] * len(partition_names))
        wupo__zmnpb.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        ilby__erf += [dict_str_arr_type]
        jmese__tlr.append(True)
        wupo__zmnpb.append(None)
    oukpb__qdtgh = {c: ksa__hpt for ksa__hpt, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in oukpb__qdtgh:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if fkcus__jes and not isinstance(fkcus__jes, dict
        ) and fkcus__jes not in selected_columns:
        selected_columns.append(fkcus__jes)
    col_names = selected_columns
    col_indices = []
    jeu__zlc = []
    nfzl__bimk = []
    jxhm__rnrb = []
    for ksa__hpt, c in enumerate(col_names):
        yhbz__bqlzp = oukpb__qdtgh[c]
        col_indices.append(yhbz__bqlzp)
        jeu__zlc.append(ilby__erf[yhbz__bqlzp])
        if not jmese__tlr[yhbz__bqlzp]:
            nfzl__bimk.append(ksa__hpt)
            jxhm__rnrb.append(wupo__zmnpb[yhbz__bqlzp])
    return (col_names, jeu__zlc, fkcus__jes, col_indices, partition_names,
        nfzl__bimk, jxhm__rnrb)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    mxj__yeys = dictionary.to_pandas()
    zdf__nup = bodo.typeof(mxj__yeys).dtype
    if isinstance(zdf__nup, types.Integer):
        uevl__msymp = PDCategoricalDtype(tuple(mxj__yeys), zdf__nup, False,
            int_type=zdf__nup)
    else:
        uevl__msymp = PDCategoricalDtype(tuple(mxj__yeys), zdf__nup, False)
    return CategoricalArrayType(uevl__msymp)


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
        tttin__qoxwt = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        ytgco__ojhvd = cgutils.get_or_insert_function(builder.module,
            tttin__qoxwt, name='pq_write')
        ubdgg__zedhd = builder.call(ytgco__ojhvd, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return ubdgg__zedhd
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
        tttin__qoxwt = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        ytgco__ojhvd = cgutils.get_or_insert_function(builder.module,
            tttin__qoxwt, name='pq_write_partitioned')
        builder.call(ytgco__ojhvd, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
