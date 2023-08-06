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
        except OSError as orsn__dvxyw:
            if 'non-file path' in str(orsn__dvxyw):
                raise FileNotFoundError(str(orsn__dvxyw))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=
        None, input_file_name_col=None, read_as_dict_cols=None):
        ibswb__pti = lhs.scope
        erc__fxjia = lhs.loc
        xblu__qsx = None
        if lhs.name in self.locals:
            xblu__qsx = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        pfi__qkkz = {}
        if lhs.name + ':convert' in self.locals:
            pfi__qkkz = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if xblu__qsx is None:
            coimu__iqs = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/file_io/#parquet-section.'
                )
            eeml__anzrs = get_const_value(file_name, self.func_ir,
                coimu__iqs, arg_types=self.args, file_info=ParquetFileInfo(
                columns, storage_options=storage_options,
                input_file_name_col=input_file_name_col, read_as_dict_cols=
                read_as_dict_cols))
            wqh__gjyx = False
            zqq__rudz = guard(get_definition, self.func_ir, file_name)
            if isinstance(zqq__rudz, ir.Arg):
                typ = self.args[zqq__rudz.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, kyqp__ueb, qcy__bijqo, col_indices,
                        partition_names, ptgsv__rdhdd, zkqku__fcq) = typ.schema
                    wqh__gjyx = True
            if not wqh__gjyx:
                (col_names, kyqp__ueb, qcy__bijqo, col_indices,
                    partition_names, ptgsv__rdhdd, zkqku__fcq) = (
                    parquet_file_schema(eeml__anzrs, columns,
                    storage_options=storage_options, input_file_name_col=
                    input_file_name_col, read_as_dict_cols=read_as_dict_cols))
        else:
            sfloo__rddv = list(xblu__qsx.keys())
            ngbrt__jedjo = {c: bhxc__mtm for bhxc__mtm, c in enumerate(
                sfloo__rddv)}
            ofdau__fymdx = [sdqar__hxthq for sdqar__hxthq in xblu__qsx.values()
                ]
            qcy__bijqo = 'index' if 'index' in ngbrt__jedjo else None
            if columns is None:
                selected_columns = sfloo__rddv
            else:
                selected_columns = columns
            col_indices = [ngbrt__jedjo[c] for c in selected_columns]
            kyqp__ueb = [ofdau__fymdx[ngbrt__jedjo[c]] for c in
                selected_columns]
            col_names = selected_columns
            qcy__bijqo = qcy__bijqo if qcy__bijqo in col_names else None
            partition_names = []
            ptgsv__rdhdd = []
            zkqku__fcq = []
        jiotp__drnpi = None if isinstance(qcy__bijqo, dict
            ) or qcy__bijqo is None else qcy__bijqo
        index_column_index = None
        index_column_type = types.none
        if jiotp__drnpi:
            ztghi__ati = col_names.index(jiotp__drnpi)
            index_column_index = col_indices.pop(ztghi__ati)
            index_column_type = kyqp__ueb.pop(ztghi__ati)
            col_names.pop(ztghi__ati)
        for bhxc__mtm, c in enumerate(col_names):
            if c in pfi__qkkz:
                kyqp__ueb[bhxc__mtm] = pfi__qkkz[c]
        cbtg__myfs = [ir.Var(ibswb__pti, mk_unique_var('pq_table'),
            erc__fxjia), ir.Var(ibswb__pti, mk_unique_var('pq_index'),
            erc__fxjia)]
        ikanj__enes = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.
            name, col_names, col_indices, kyqp__ueb, cbtg__myfs, erc__fxjia,
            partition_names, storage_options, index_column_index,
            index_column_type, input_file_name_col, ptgsv__rdhdd, zkqku__fcq)]
        return (col_names, cbtg__myfs, qcy__bijqo, ikanj__enes, kyqp__ueb,
            index_column_type)


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    rxbde__fvsp = len(pq_node.out_vars)
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    hfld__dbh, gnn__ebpqc = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    extra_args = ', '.join(hfld__dbh.values())
    dnf_filter_str, expr_filter_str = bodo.ir.connector.generate_arrow_filters(
        pq_node.filters, hfld__dbh, gnn__ebpqc, pq_node.
        original_df_colnames, pq_node.partition_names, pq_node.
        original_out_types, typemap, 'parquet', output_dnf=False)
    rzr__ayug = ', '.join(f'out{bhxc__mtm}' for bhxc__mtm in range(rxbde__fvsp)
        )
    dyl__jwuh = f'def pq_impl(fname, {extra_args}):\n'
    dyl__jwuh += (
        f'    (total_rows, {rzr__ayug},) = _pq_reader_py(fname, {extra_args})\n'
        )
    rll__updig = {}
    exec(dyl__jwuh, {}, rll__updig)
    yhdz__trzdo = rll__updig['pq_impl']
    if bodo.user_logging.get_verbose_level() >= 1:
        mik__rqzt = pq_node.loc.strformat()
        abjrc__danb = []
        wrjb__avs = []
        for bhxc__mtm in pq_node.out_used_cols:
            igsih__qyeh = pq_node.df_colnames[bhxc__mtm]
            abjrc__danb.append(igsih__qyeh)
            if isinstance(pq_node.out_types[bhxc__mtm], bodo.libs.
                dict_arr_ext.DictionaryArrayType):
                wrjb__avs.append(igsih__qyeh)
        rrc__rbv = (
            'Finish column pruning on read_parquet node:\n%s\nColumns loaded %s\n'
            )
        bodo.user_logging.log_message('Column Pruning', rrc__rbv, mik__rqzt,
            abjrc__danb)
        if wrjb__avs:
            poh__oyf = """Finished optimized encoding on read_parquet node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', poh__oyf,
                mik__rqzt, wrjb__avs)
    parallel = bodo.ir.connector.is_connector_table_parallel(pq_node,
        array_dists, typemap, 'ParquetReader')
    if pq_node.unsupported_columns:
        nji__xxfn = set(pq_node.out_used_cols)
        djcva__lpisp = set(pq_node.unsupported_columns)
        vdnx__aonat = nji__xxfn & djcva__lpisp
        if vdnx__aonat:
            cmwze__oudf = sorted(vdnx__aonat)
            wyd__nfi = [
                f'pandas.read_parquet(): 1 or more columns found with Arrow types that are not supported in Bodo and could not be eliminated. '
                 +
                "Please manually remove these columns from your read_parquet with the 'columns' argument. If these "
                 +
                'columns are needed, you will need to modify your dataset to use a supported type.'
                , 'Unsupported Columns:']
            fyvq__gqobh = 0
            for azso__gbn in cmwze__oudf:
                while pq_node.unsupported_columns[fyvq__gqobh] != azso__gbn:
                    fyvq__gqobh += 1
                wyd__nfi.append(
                    f"Column '{pq_node.df_colnames[azso__gbn]}' with unsupported arrow type {pq_node.unsupported_arrow_types[fyvq__gqobh]}"
                    )
                fyvq__gqobh += 1
            gha__mkua = '\n'.join(wyd__nfi)
            raise BodoError(gha__mkua, loc=pq_node.loc)
    jxli__hsm = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.out_used_cols, pq_node.out_types, pq_node.storage_options,
        pq_node.partition_names, dnf_filter_str, expr_filter_str,
        extra_args, parallel, meta_head_only_info, pq_node.
        index_column_index, pq_node.index_column_type, pq_node.
        input_file_name_col)
    vinu__jus = typemap[pq_node.file_name.name]
    sgvjd__sih = (vinu__jus,) + tuple(typemap[hnnzf__ring.name] for
        hnnzf__ring in gnn__ebpqc)
    uuk__mkiy = compile_to_numba_ir(yhdz__trzdo, {'_pq_reader_py':
        jxli__hsm}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        sgvjd__sih, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(uuk__mkiy, [pq_node.file_name] + gnn__ebpqc)
    ikanj__enes = uuk__mkiy.body[:-3]
    if meta_head_only_info:
        ikanj__enes[-3].target = meta_head_only_info[1]
    ikanj__enes[-2].target = pq_node.out_vars[0]
    ikanj__enes[-1].target = pq_node.out_vars[1]
    assert not (pq_node.index_column_index is None and not pq_node.
        out_used_cols
        ), 'At most one of table and index should be dead if the Parquet IR node is live'
    if pq_node.index_column_index is None:
        ikanj__enes.pop(-1)
    elif not pq_node.out_used_cols:
        ikanj__enes.pop(-2)
    return ikanj__enes


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    dzfub__gfl = get_overload_const_str(dnf_filter_str)
    rxyfj__okkbt = get_overload_const_str(expr_filter_str)
    zug__fzlf = ', '.join(f'f{bhxc__mtm}' for bhxc__mtm in range(len(var_tup)))
    dyl__jwuh = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        dyl__jwuh += f'  {zug__fzlf}, = var_tup\n'
    dyl__jwuh += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    dyl__jwuh += f'    dnf_filters_py = {dzfub__gfl}\n'
    dyl__jwuh += f'    expr_filters_py = {rxyfj__okkbt}\n'
    dyl__jwuh += '  return (dnf_filters_py, expr_filters_py)\n'
    rll__updig = {}
    exec(dyl__jwuh, globals(), rll__updig)
    return rll__updig['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def _gen_pq_reader_py(col_names, col_indices, out_used_cols, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type, input_file_name_col):
    oyji__etue = next_label()
    upk__gdh = ',' if extra_args else ''
    dyl__jwuh = f'def pq_reader_py(fname,{extra_args}):\n'
    dyl__jwuh += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    dyl__jwuh += f"    ev.add_attribute('g_fname', fname)\n"
    dyl__jwuh += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{upk__gdh}))
"""
    dyl__jwuh += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    dyl__jwuh += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    rgc__myxho = not out_used_cols
    rwfi__vombc = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    input_file_name_col = sanitize_varname(input_file_name_col
        ) if input_file_name_col is not None and col_names.index(
        input_file_name_col) in out_used_cols else None
    fydte__wsovp = {c: bhxc__mtm for bhxc__mtm, c in enumerate(col_indices)}
    meez__ctoc = {c: bhxc__mtm for bhxc__mtm, c in enumerate(rwfi__vombc)}
    lrp__cty = []
    ymtq__iiq = set()
    xkacc__wlr = partition_names + [input_file_name_col]
    for bhxc__mtm in out_used_cols:
        if rwfi__vombc[bhxc__mtm] not in xkacc__wlr:
            lrp__cty.append(col_indices[bhxc__mtm])
        elif not input_file_name_col or rwfi__vombc[bhxc__mtm
            ] != input_file_name_col:
            ymtq__iiq.add(col_indices[bhxc__mtm])
    if index_column_index is not None:
        lrp__cty.append(index_column_index)
    lrp__cty = sorted(lrp__cty)
    oysee__bfo = {c: bhxc__mtm for bhxc__mtm, c in enumerate(lrp__cty)}
    blktx__ynluw = [(int(is_nullable(out_types[fydte__wsovp[gwakt__vsyj]])) if
        gwakt__vsyj != index_column_index else int(is_nullable(
        index_column_type))) for gwakt__vsyj in lrp__cty]
    str_as_dict_cols = []
    for gwakt__vsyj in lrp__cty:
        if gwakt__vsyj == index_column_index:
            sdqar__hxthq = index_column_type
        else:
            sdqar__hxthq = out_types[fydte__wsovp[gwakt__vsyj]]
        if sdqar__hxthq == dict_str_arr_type:
            str_as_dict_cols.append(gwakt__vsyj)
    dwr__ueqxq = []
    iqva__ndyc = {}
    ezaae__jndk = []
    tim__bis = []
    for bhxc__mtm, dkmsz__hik in enumerate(partition_names):
        try:
            evz__veoyu = meez__ctoc[dkmsz__hik]
            if col_indices[evz__veoyu] not in ymtq__iiq:
                continue
        except (KeyError, ValueError) as jgyah__qzphe:
            continue
        iqva__ndyc[dkmsz__hik] = len(dwr__ueqxq)
        dwr__ueqxq.append(dkmsz__hik)
        ezaae__jndk.append(bhxc__mtm)
        nfome__wvprb = out_types[evz__veoyu].dtype
        nyugv__dlg = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            nfome__wvprb)
        tim__bis.append(numba_to_c_type(nyugv__dlg))
    dyl__jwuh += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    dyl__jwuh += f'    out_table = pq_read(\n'
    dyl__jwuh += f'        fname_py, {is_parallel},\n'
    dyl__jwuh += f'        dnf_filters, expr_filters,\n'
    dyl__jwuh += f"""        storage_options_py, {tot_rows_to_read}, selected_cols_arr_{oyji__etue}.ctypes,
"""
    dyl__jwuh += f'        {len(lrp__cty)},\n'
    dyl__jwuh += f'        nullable_cols_arr_{oyji__etue}.ctypes,\n'
    if len(ezaae__jndk) > 0:
        dyl__jwuh += (
            f'        np.array({ezaae__jndk}, dtype=np.int32).ctypes,\n')
        dyl__jwuh += f'        np.array({tim__bis}, dtype=np.int32).ctypes,\n'
        dyl__jwuh += f'        {len(ezaae__jndk)},\n'
    else:
        dyl__jwuh += f'        0, 0, 0,\n'
    if len(str_as_dict_cols) > 0:
        dyl__jwuh += f"""        np.array({str_as_dict_cols}, dtype=np.int32).ctypes, {len(str_as_dict_cols)},
"""
    else:
        dyl__jwuh += f'        0, 0,\n'
    dyl__jwuh += f'        total_rows_np.ctypes,\n'
    dyl__jwuh += f'        {input_file_name_col is not None},\n'
    dyl__jwuh += f'    )\n'
    dyl__jwuh += f'    check_and_propagate_cpp_exception()\n'
    okfc__gagnk = 'None'
    dks__svb = index_column_type
    ihetw__hunbe = TableType(tuple(out_types))
    if rgc__myxho:
        ihetw__hunbe = types.none
    if index_column_index is not None:
        zeyeu__redm = oysee__bfo[index_column_index]
        okfc__gagnk = (
            f'info_to_array(info_from_table(out_table, {zeyeu__redm}), index_arr_type)'
            )
    dyl__jwuh += f'    index_arr = {okfc__gagnk}\n'
    if rgc__myxho:
        tmmmo__wcx = None
    else:
        tmmmo__wcx = []
        yju__bgsm = 0
        bpimt__xgt = col_indices[col_names.index(input_file_name_col)
            ] if input_file_name_col is not None else None
        for bhxc__mtm, azso__gbn in enumerate(col_indices):
            if yju__bgsm < len(out_used_cols) and bhxc__mtm == out_used_cols[
                yju__bgsm]:
                eukx__totgt = col_indices[bhxc__mtm]
                if bpimt__xgt and eukx__totgt == bpimt__xgt:
                    tmmmo__wcx.append(len(lrp__cty) + len(dwr__ueqxq))
                elif eukx__totgt in ymtq__iiq:
                    xwgtp__vnptk = rwfi__vombc[bhxc__mtm]
                    tmmmo__wcx.append(len(lrp__cty) + iqva__ndyc[xwgtp__vnptk])
                else:
                    tmmmo__wcx.append(oysee__bfo[azso__gbn])
                yju__bgsm += 1
            else:
                tmmmo__wcx.append(-1)
        tmmmo__wcx = np.array(tmmmo__wcx, dtype=np.int64)
    if rgc__myxho:
        dyl__jwuh += '    T = None\n'
    else:
        dyl__jwuh += f"""    T = cpp_table_to_py_table(out_table, table_idx_{oyji__etue}, py_table_type_{oyji__etue})
"""
    dyl__jwuh += f'    delete_table(out_table)\n'
    dyl__jwuh += f'    total_rows = total_rows_np[0]\n'
    dyl__jwuh += f'    ev.finalize()\n'
    dyl__jwuh += f'    return (total_rows, T, index_arr)\n'
    rll__updig = {}
    oag__snk = {f'py_table_type_{oyji__etue}': ihetw__hunbe,
        f'table_idx_{oyji__etue}': tmmmo__wcx,
        f'selected_cols_arr_{oyji__etue}': np.array(lrp__cty, np.int32),
        f'nullable_cols_arr_{oyji__etue}': np.array(blktx__ynluw, np.int32),
        'index_arr_type': dks__svb, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(dyl__jwuh, oag__snk, rll__updig)
    jxli__hsm = rll__updig['pq_reader_py']
    vxju__ahez = numba.njit(jxli__hsm, no_cpython_wrapper=True)
    return vxju__ahez


def unify_schemas(schemas):
    zfdjk__kmfm = []
    for schema in schemas:
        for bhxc__mtm in range(len(schema)):
            yij__hao = schema.field(bhxc__mtm)
            if yij__hao.type == pa.large_string():
                schema = schema.set(bhxc__mtm, yij__hao.with_type(pa.string()))
            elif yij__hao.type == pa.large_binary():
                schema = schema.set(bhxc__mtm, yij__hao.with_type(pa.binary()))
            elif isinstance(yij__hao.type, (pa.ListType, pa.LargeListType)
                ) and yij__hao.type.value_type in (pa.string(), pa.
                large_string()):
                schema = schema.set(bhxc__mtm, yij__hao.with_type(pa.list_(
                    pa.field(yij__hao.type.value_field.name, pa.string()))))
            elif isinstance(yij__hao.type, pa.LargeListType):
                schema = schema.set(bhxc__mtm, yij__hao.with_type(pa.list_(
                    pa.field(yij__hao.type.value_field.name, yij__hao.type.
                    value_type))))
        zfdjk__kmfm.append(schema)
    return pa.unify_schemas(zfdjk__kmfm)


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
        for bhxc__mtm in range(len(self.schema)):
            yij__hao = self.schema.field(bhxc__mtm)
            if yij__hao.type == pa.large_string():
                self.schema = self.schema.set(bhxc__mtm, yij__hao.with_type
                    (pa.string()))
        self.pieces = [ParquetPiece(frag, partitioning, self.
            partition_names) for frag in pa_pq_dataset._dataset.
            get_fragments(filter=pa_pq_dataset._filter_expression)]

    def set_fs(self, fs):
        self.filesystem = fs
        for yucx__dov in self.pieces:
            yucx__dov.filesystem = fs

    def __setstate__(self, state):
        self.__dict__ = state
        if self.partition_names:
            wjz__cbgmo = {yucx__dov: self.partitioning_dictionaries[
                bhxc__mtm] for bhxc__mtm, yucx__dov in enumerate(self.
                partition_names)}
            self.partitioning = self.partitioning_cls(self.
                partitioning_schema, wjz__cbgmo)


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
            self.partition_keys = [(dkmsz__hik, partitioning.dictionaries[
                bhxc__mtm].index(self.partition_keys[dkmsz__hik]).as_py()) for
                bhxc__mtm, dkmsz__hik in enumerate(partition_names)]

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
        nxe__fxlck = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    hjyyo__rif = MPI.COMM_WORLD
    if isinstance(fpath, list):
        rsa__cda = urlparse(fpath[0])
        protocol = rsa__cda.scheme
        gpuhe__vtpvl = rsa__cda.netloc
        for bhxc__mtm in range(len(fpath)):
            yij__hao = fpath[bhxc__mtm]
            nosx__epxf = urlparse(yij__hao)
            if nosx__epxf.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if nosx__epxf.netloc != gpuhe__vtpvl:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[bhxc__mtm] = yij__hao.rstrip('/')
    else:
        rsa__cda = urlparse(fpath)
        protocol = rsa__cda.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as jgyah__qzphe:
            ivb__paae = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(ivb__paae)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as jgyah__qzphe:
            ivb__paae = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            cmzq__jlsg = gcsfs.GCSFileSystem(token=None)
            fs.append(PyFileSystem(FSSpecHandler(cmzq__jlsg)))
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
            ljhb__hyozs = fs.glob(path)
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(ljhb__hyozs) == 0:
            raise BodoError('No files found matching glob pattern')
        return ljhb__hyozs
    ids__sti = False
    if get_row_counts:
        ggztr__hfs = getfs(parallel=True)
        ids__sti = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        iqq__kck = 1
        hba__qimw = os.cpu_count()
        if hba__qimw is not None and hba__qimw > 1:
            iqq__kck = hba__qimw // 2
        try:
            if get_row_counts:
                wndm__vbyu = tracing.Event('pq.ParquetDataset', is_parallel
                    =False)
                if tracing.is_tracing():
                    wndm__vbyu.add_attribute('g_dnf_filter', str(dnf_filters))
            cwlfu__ndyyh = pa.io_thread_count()
            pa.set_io_thread_count(iqq__kck)
            prefix = ''
            if protocol == 's3':
                prefix = 's3://'
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{rsa__cda.netloc}'
            if prefix:
                if isinstance(fpath, list):
                    iyan__qxhk = [yij__hao[len(prefix):] for yij__hao in fpath]
                else:
                    iyan__qxhk = fpath[len(prefix):]
            else:
                iyan__qxhk = fpath
            if isinstance(iyan__qxhk, list):
                evwol__pcze = []
                for yucx__dov in iyan__qxhk:
                    if has_magic(yucx__dov):
                        evwol__pcze += glob(protocol, getfs(), yucx__dov)
                    else:
                        evwol__pcze.append(yucx__dov)
                iyan__qxhk = evwol__pcze
            elif has_magic(iyan__qxhk):
                iyan__qxhk = glob(protocol, getfs(), iyan__qxhk)
            sjval__etf = pq.ParquetDataset(iyan__qxhk, filesystem=getfs(),
                filters=None, use_legacy_dataset=False, partitioning=
                partitioning)
            if dnf_filters is not None:
                sjval__etf._filters = dnf_filters
                sjval__etf._filter_expression = pq._filters_to_expression(
                    dnf_filters)
            dej__knd = len(sjval__etf.files)
            sjval__etf = ParquetDataset(sjval__etf, prefix)
            pa.set_io_thread_count(cwlfu__ndyyh)
            if typing_pa_schema:
                sjval__etf.schema = typing_pa_schema
            if get_row_counts:
                if dnf_filters is not None:
                    wndm__vbyu.add_attribute('num_pieces_before_filter',
                        dej__knd)
                    wndm__vbyu.add_attribute('num_pieces_after_filter', len
                        (sjval__etf.pieces))
                wndm__vbyu.finalize()
        except Exception as orsn__dvxyw:
            if isinstance(orsn__dvxyw, IsADirectoryError):
                orsn__dvxyw = BodoError(list_of_files_error_msg)
            elif isinstance(fpath, list) and isinstance(orsn__dvxyw, (
                OSError, FileNotFoundError)):
                orsn__dvxyw = BodoError(str(orsn__dvxyw) +
                    list_of_files_error_msg)
            else:
                orsn__dvxyw = BodoError(
                    f"""error from pyarrow: {type(orsn__dvxyw).__name__}: {str(orsn__dvxyw)}
"""
                    )
            hjyyo__rif.bcast(orsn__dvxyw)
            raise orsn__dvxyw
        if get_row_counts:
            lnj__wrg = tracing.Event('bcast dataset')
        sjval__etf = hjyyo__rif.bcast(sjval__etf)
    else:
        if get_row_counts:
            lnj__wrg = tracing.Event('bcast dataset')
        sjval__etf = hjyyo__rif.bcast(None)
        if isinstance(sjval__etf, Exception):
            fok__uzt = sjval__etf
            raise fok__uzt
    sjval__etf.set_fs(getfs())
    if get_row_counts:
        lnj__wrg.finalize()
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = ids__sti = False
    if get_row_counts or ids__sti:
        if get_row_counts and tracing.is_tracing():
            fvrf__tdgh = tracing.Event('get_row_counts')
            fvrf__tdgh.add_attribute('g_num_pieces', len(sjval__etf.pieces))
            fvrf__tdgh.add_attribute('g_expr_filters', str(expr_filters))
        gwelj__kwhkk = 0.0
        num_pieces = len(sjval__etf.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        vdevm__osdlm = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        pugs__mcm = 0
        ouxgs__ekzpa = 0
        uue__unzc = 0
        imi__dbbtj = True
        if expr_filters is not None:
            import random
            random.seed(37)
            srq__bdac = random.sample(sjval__etf.pieces, k=len(sjval__etf.
                pieces))
        else:
            srq__bdac = sjval__etf.pieces
        fpaths = [yucx__dov.path for yucx__dov in srq__bdac[start:vdevm__osdlm]
            ]
        iqq__kck = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), 4)
        pa.set_io_thread_count(iqq__kck)
        pa.set_cpu_count(iqq__kck)
        fok__uzt = None
        try:
            asga__vlix = ds.dataset(fpaths, filesystem=sjval__etf.
                filesystem, partitioning=sjval__etf.partitioning)
            for fqyf__cigmj, frag in zip(srq__bdac[start:vdevm__osdlm],
                asga__vlix.get_fragments()):
                if ids__sti:
                    afmto__ibe = frag.metadata.schema.to_arrow_schema()
                    bucju__yuepg = set(afmto__ibe.names)
                    xbc__eopb = set(sjval__etf.schema.names) - set(sjval__etf
                        .partition_names)
                    if xbc__eopb != bucju__yuepg:
                        bvqyy__reje = bucju__yuepg - xbc__eopb
                        dxlfv__mijl = xbc__eopb - bucju__yuepg
                        coimu__iqs = (
                            f'Schema in {fqyf__cigmj} was different.\n')
                        if bvqyy__reje:
                            coimu__iqs += f"""File contains column(s) {bvqyy__reje} not found in other files in the dataset.
"""
                        if dxlfv__mijl:
                            coimu__iqs += f"""File missing column(s) {dxlfv__mijl} found in other files in the dataset.
"""
                        raise BodoError(coimu__iqs)
                    try:
                        sjval__etf.schema = unify_schemas([sjval__etf.
                            schema, afmto__ibe])
                    except Exception as orsn__dvxyw:
                        coimu__iqs = (
                            f'Schema in {fqyf__cigmj} was different.\n' +
                            str(orsn__dvxyw))
                        raise BodoError(coimu__iqs)
                jzsye__shxnn = time.time()
                say__algc = frag.scanner(schema=asga__vlix.schema, filter=
                    expr_filters, use_threads=True).count_rows()
                gwelj__kwhkk += time.time() - jzsye__shxnn
                fqyf__cigmj._bodo_num_rows = say__algc
                pugs__mcm += say__algc
                ouxgs__ekzpa += frag.num_row_groups
                uue__unzc += sum(fene__ddf.total_byte_size for fene__ddf in
                    frag.row_groups)
        except Exception as orsn__dvxyw:
            fok__uzt = orsn__dvxyw
        if hjyyo__rif.allreduce(fok__uzt is not None, op=MPI.LOR):
            for fok__uzt in hjyyo__rif.allgather(fok__uzt):
                if fok__uzt:
                    if isinstance(fpath, list) and isinstance(fok__uzt, (
                        OSError, FileNotFoundError)):
                        raise BodoError(str(fok__uzt) + list_of_files_error_msg
                            )
                    raise fok__uzt
        if ids__sti:
            imi__dbbtj = hjyyo__rif.allreduce(imi__dbbtj, op=MPI.LAND)
            if not imi__dbbtj:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            sjval__etf._bodo_total_rows = hjyyo__rif.allreduce(pugs__mcm,
                op=MPI.SUM)
            drq__jmem = hjyyo__rif.allreduce(ouxgs__ekzpa, op=MPI.SUM)
            ahr__rvwe = hjyyo__rif.allreduce(uue__unzc, op=MPI.SUM)
            pwliz__oehh = np.array([yucx__dov._bodo_num_rows for yucx__dov in
                sjval__etf.pieces])
            pwliz__oehh = hjyyo__rif.allreduce(pwliz__oehh, op=MPI.SUM)
            for yucx__dov, kcyjl__whjys in zip(sjval__etf.pieces, pwliz__oehh):
                yucx__dov._bodo_num_rows = kcyjl__whjys
            if is_parallel and bodo.get_rank(
                ) == 0 and drq__jmem < bodo.get_size() and drq__jmem != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({drq__jmem}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()}). For more details, refer to
https://docs.bodo.ai/latest/file_io/#parquet-section.
"""
                    ))
            if drq__jmem == 0:
                ssx__ccps = 0
            else:
                ssx__ccps = ahr__rvwe // drq__jmem
            if (bodo.get_rank() == 0 and ahr__rvwe >= 20 * 1048576 and 
                ssx__ccps < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({ssx__ccps} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                fvrf__tdgh.add_attribute('g_total_num_row_groups', drq__jmem)
                fvrf__tdgh.add_attribute('total_scan_time', gwelj__kwhkk)
                pzoy__dsam = np.array([yucx__dov._bodo_num_rows for
                    yucx__dov in sjval__etf.pieces])
                ggyj__zqi = np.percentile(pzoy__dsam, [25, 50, 75])
                fvrf__tdgh.add_attribute('g_row_counts_min', pzoy__dsam.min())
                fvrf__tdgh.add_attribute('g_row_counts_Q1', ggyj__zqi[0])
                fvrf__tdgh.add_attribute('g_row_counts_median', ggyj__zqi[1])
                fvrf__tdgh.add_attribute('g_row_counts_Q3', ggyj__zqi[2])
                fvrf__tdgh.add_attribute('g_row_counts_max', pzoy__dsam.max())
                fvrf__tdgh.add_attribute('g_row_counts_mean', pzoy__dsam.mean()
                    )
                fvrf__tdgh.add_attribute('g_row_counts_std', pzoy__dsam.std())
                fvrf__tdgh.add_attribute('g_row_counts_sum', pzoy__dsam.sum())
                fvrf__tdgh.finalize()
    if read_categories:
        _add_categories_to_pq_dataset(sjval__etf)
    if get_row_counts:
        nxe__fxlck.finalize()
    if ids__sti and is_parallel:
        if tracing.is_tracing():
            fpri__tical = tracing.Event('unify_schemas_across_ranks')
        fok__uzt = None
        try:
            sjval__etf.schema = hjyyo__rif.allreduce(sjval__etf.schema,
                bodo.io.helpers.pa_schema_unify_mpi_op)
        except Exception as orsn__dvxyw:
            fok__uzt = orsn__dvxyw
        if tracing.is_tracing():
            fpri__tical.finalize()
        if hjyyo__rif.allreduce(fok__uzt is not None, op=MPI.LOR):
            for fok__uzt in hjyyo__rif.allgather(fok__uzt):
                if fok__uzt:
                    coimu__iqs = (f'Schema in some files were different.\n' +
                        str(fok__uzt))
                    raise BodoError(coimu__iqs)
    return sjval__etf


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, filesystem, str_as_dict_cols, start_offset,
    rows_to_read, partitioning, schema):
    import pyarrow as pa
    hba__qimw = os.cpu_count()
    if hba__qimw is None or hba__qimw == 0:
        hba__qimw = 2
    msox__yhino = min(int(os.environ.get('BODO_MIN_IO_THREADS', 4)), hba__qimw)
    xbfa__nukiq = min(int(os.environ.get('BODO_MAX_IO_THREADS', 16)), hba__qimw
        )
    if is_parallel and len(fpaths) > xbfa__nukiq and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(xbfa__nukiq)
        pa.set_cpu_count(xbfa__nukiq)
    else:
        pa.set_io_thread_count(msox__yhino)
        pa.set_cpu_count(msox__yhino)
    qwv__jeyol = ds.ParquetFileFormat(dictionary_columns=str_as_dict_cols)
    kbbwc__zel = set(str_as_dict_cols)
    for bhxc__mtm, name in enumerate(schema.names):
        if name in kbbwc__zel:
            crmg__dnexk = schema.field(bhxc__mtm)
            msexj__nlvo = pa.field(name, pa.dictionary(pa.int32(),
                crmg__dnexk.type), crmg__dnexk.nullable)
            schema = schema.remove(bhxc__mtm).insert(bhxc__mtm, msexj__nlvo)
    sjval__etf = ds.dataset(fpaths, filesystem=filesystem, partitioning=
        partitioning, schema=schema, format=qwv__jeyol)
    col_names = sjval__etf.schema.names
    cgfr__fnv = [col_names[yjg__qnelz] for yjg__qnelz in selected_fields]
    bwrvv__dft = len(fpaths) <= 3 or start_offset > 0 and len(fpaths) <= 10
    if bwrvv__dft and expr_filters is None:
        kwhah__bvfry = []
        vrm__drqaz = 0
        maajm__gyk = 0
        for frag in sjval__etf.get_fragments():
            wyx__nkjjc = []
            for fene__ddf in frag.row_groups:
                pcj__xdg = fene__ddf.num_rows
                if start_offset < vrm__drqaz + pcj__xdg:
                    if maajm__gyk == 0:
                        gjz__oikd = start_offset - vrm__drqaz
                        ddxp__pcef = min(pcj__xdg - gjz__oikd, rows_to_read)
                    else:
                        ddxp__pcef = min(pcj__xdg, rows_to_read - maajm__gyk)
                    maajm__gyk += ddxp__pcef
                    wyx__nkjjc.append(fene__ddf.id)
                vrm__drqaz += pcj__xdg
                if maajm__gyk == rows_to_read:
                    break
            kwhah__bvfry.append(frag.subset(row_group_ids=wyx__nkjjc))
            if maajm__gyk == rows_to_read:
                break
        sjval__etf = ds.FileSystemDataset(kwhah__bvfry, sjval__etf.schema,
            qwv__jeyol, filesystem=sjval__etf.filesystem)
        start_offset = gjz__oikd
    szv__luoqu = sjval__etf.scanner(columns=cgfr__fnv, filter=expr_filters,
        use_threads=True).to_reader()
    return sjval__etf, szv__luoqu, start_offset


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    pa_schema = pq_dataset.schema
    vsllq__afx = [c for c in pa_schema.names if isinstance(pa_schema.field(
        c).type, pa.DictionaryType) and c not in pq_dataset.partition_names]
    if len(vsllq__afx) == 0:
        pq_dataset._category_info = {}
        return
    hjyyo__rif = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            nugym__javb = pq_dataset.pieces[0].frag.head(100, columns=
                vsllq__afx)
            cgci__lrxa = {c: tuple(nugym__javb.column(c).chunk(0).
                dictionary.to_pylist()) for c in vsllq__afx}
            del nugym__javb
        except Exception as orsn__dvxyw:
            hjyyo__rif.bcast(orsn__dvxyw)
            raise orsn__dvxyw
        hjyyo__rif.bcast(cgci__lrxa)
    else:
        cgci__lrxa = hjyyo__rif.bcast(None)
        if isinstance(cgci__lrxa, Exception):
            fok__uzt = cgci__lrxa
            raise fok__uzt
    pq_dataset._category_info = cgci__lrxa


def get_pandas_metadata(schema, num_pieces):
    qcy__bijqo = None
    uuzte__bzzmq = defaultdict(lambda : None)
    plr__fkhye = b'pandas'
    if schema.metadata is not None and plr__fkhye in schema.metadata:
        import json
        tauz__owtru = json.loads(schema.metadata[plr__fkhye].decode('utf8'))
        lzf__kyp = len(tauz__owtru['index_columns'])
        if lzf__kyp > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        qcy__bijqo = tauz__owtru['index_columns'][0] if lzf__kyp else None
        if not isinstance(qcy__bijqo, str) and not isinstance(qcy__bijqo, dict
            ):
            qcy__bijqo = None
        for cpwj__djclf in tauz__owtru['columns']:
            gea__ugycj = cpwj__djclf['name']
            if cpwj__djclf['pandas_type'].startswith('int'
                ) and gea__ugycj is not None:
                if cpwj__djclf['numpy_type'].startswith('Int'):
                    uuzte__bzzmq[gea__ugycj] = True
                else:
                    uuzte__bzzmq[gea__ugycj] = False
    return qcy__bijqo, uuzte__bzzmq


def get_str_columns_from_pa_schema(pa_schema):
    str_columns = []
    for gea__ugycj in pa_schema.names:
        heoqm__hbyae = pa_schema.field(gea__ugycj)
        if heoqm__hbyae.type in (pa.string(), pa.large_string()):
            str_columns.append(gea__ugycj)
    return str_columns


def determine_str_as_dict_columns(pq_dataset, pa_schema, str_columns):
    from mpi4py import MPI
    hjyyo__rif = MPI.COMM_WORLD
    if len(str_columns) == 0:
        return set()
    if len(pq_dataset.pieces) > bodo.get_size():
        import random
        random.seed(37)
        srq__bdac = random.sample(pq_dataset.pieces, bodo.get_size())
    else:
        srq__bdac = pq_dataset.pieces
    osmub__lfaa = np.zeros(len(str_columns), dtype=np.int64)
    hdbbb__mruin = np.zeros(len(str_columns), dtype=np.int64)
    if bodo.get_rank() < len(srq__bdac):
        fqyf__cigmj = srq__bdac[bodo.get_rank()]
        try:
            metadata = fqyf__cigmj.metadata
            for bhxc__mtm in range(fqyf__cigmj.num_row_groups):
                for yju__bgsm, gea__ugycj in enumerate(str_columns):
                    fyvq__gqobh = pa_schema.get_field_index(gea__ugycj)
                    osmub__lfaa[yju__bgsm] += metadata.row_group(bhxc__mtm
                        ).column(fyvq__gqobh).total_uncompressed_size
            neow__kbhz = metadata.num_rows
        except Exception as orsn__dvxyw:
            if isinstance(orsn__dvxyw, (OSError, FileNotFoundError)):
                neow__kbhz = 0
            else:
                raise
    else:
        neow__kbhz = 0
    wqnd__qrt = hjyyo__rif.allreduce(neow__kbhz, op=MPI.SUM)
    if wqnd__qrt == 0:
        return set()
    hjyyo__rif.Allreduce(osmub__lfaa, hdbbb__mruin, op=MPI.SUM)
    gtjgp__njnil = hdbbb__mruin / wqnd__qrt
    datq__zuve = set()
    for bhxc__mtm, qty__zkpil in enumerate(gtjgp__njnil):
        if qty__zkpil < READ_STR_AS_DICT_THRESHOLD:
            gea__ugycj = str_columns[bhxc__mtm][0]
            datq__zuve.add(gea__ugycj)
    return datq__zuve


def parquet_file_schema(file_name, selected_columns, storage_options=None,
    input_file_name_col=None, read_as_dict_cols=None):
    col_names = []
    kyqp__ueb = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = pq_dataset.partition_names
    pa_schema = pq_dataset.schema
    num_pieces = len(pq_dataset.pieces)
    str_columns = get_str_columns_from_pa_schema(pa_schema)
    ozudo__dvt = set(str_columns)
    if read_as_dict_cols is None:
        read_as_dict_cols = []
    read_as_dict_cols = set(read_as_dict_cols)
    vlc__rsmlt = read_as_dict_cols - ozudo__dvt
    if len(vlc__rsmlt) > 0:
        if bodo.get_rank() == 0:
            warnings.warn(
                f'The following columns are not of datatype string and hence cannot be read with dictionary encoding: {vlc__rsmlt}'
                , bodo.utils.typing.BodoWarning)
    read_as_dict_cols.intersection_update(ozudo__dvt)
    ozudo__dvt = ozudo__dvt - read_as_dict_cols
    str_columns = [mehg__xdkim for mehg__xdkim in str_columns if 
        mehg__xdkim in ozudo__dvt]
    datq__zuve: set = determine_str_as_dict_columns(pq_dataset, pa_schema,
        str_columns)
    datq__zuve.update(read_as_dict_cols)
    col_names = pa_schema.names
    qcy__bijqo, uuzte__bzzmq = get_pandas_metadata(pa_schema, num_pieces)
    ofdau__fymdx = []
    qjd__oxqus = []
    fzs__ovshz = []
    for bhxc__mtm, c in enumerate(col_names):
        if c in partition_names:
            continue
        heoqm__hbyae = pa_schema.field(c)
        zlyxw__btjo, ipb__olv = _get_numba_typ_from_pa_typ(heoqm__hbyae, c ==
            qcy__bijqo, uuzte__bzzmq[c], pq_dataset._category_info,
            str_as_dict=c in datq__zuve)
        ofdau__fymdx.append(zlyxw__btjo)
        qjd__oxqus.append(ipb__olv)
        fzs__ovshz.append(heoqm__hbyae.type)
    if partition_names:
        ofdau__fymdx += [_get_partition_cat_dtype(pq_dataset.
            partitioning_dictionaries[bhxc__mtm]) for bhxc__mtm in range(
            len(partition_names))]
        qjd__oxqus.extend([True] * len(partition_names))
        fzs__ovshz.extend([None] * len(partition_names))
    if input_file_name_col is not None:
        col_names += [input_file_name_col]
        ofdau__fymdx += [dict_str_arr_type]
        qjd__oxqus.append(True)
        fzs__ovshz.append(None)
    ykz__qrgn = {c: bhxc__mtm for bhxc__mtm, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in ykz__qrgn:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if qcy__bijqo and not isinstance(qcy__bijqo, dict
        ) and qcy__bijqo not in selected_columns:
        selected_columns.append(qcy__bijqo)
    col_names = selected_columns
    col_indices = []
    kyqp__ueb = []
    ptgsv__rdhdd = []
    zkqku__fcq = []
    for bhxc__mtm, c in enumerate(col_names):
        eukx__totgt = ykz__qrgn[c]
        col_indices.append(eukx__totgt)
        kyqp__ueb.append(ofdau__fymdx[eukx__totgt])
        if not qjd__oxqus[eukx__totgt]:
            ptgsv__rdhdd.append(bhxc__mtm)
            zkqku__fcq.append(fzs__ovshz[eukx__totgt])
    return (col_names, kyqp__ueb, qcy__bijqo, col_indices, partition_names,
        ptgsv__rdhdd, zkqku__fcq)


def _get_partition_cat_dtype(dictionary):
    assert dictionary is not None
    nyh__ngf = dictionary.to_pandas()
    onph__amghr = bodo.typeof(nyh__ngf).dtype
    if isinstance(onph__amghr, types.Integer):
        cptoi__rrf = PDCategoricalDtype(tuple(nyh__ngf), onph__amghr, False,
            int_type=onph__amghr)
    else:
        cptoi__rrf = PDCategoricalDtype(tuple(nyh__ngf), onph__amghr, False)
    return CategoricalArrayType(cptoi__rrf)


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
        uby__ppde = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        xng__cfs = cgutils.get_or_insert_function(builder.module, uby__ppde,
            name='pq_write')
        brns__flkc = builder.call(xng__cfs, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
        return brns__flkc
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
        uby__ppde = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer()])
        xng__cfs = cgutils.get_or_insert_function(builder.module, uby__ppde,
            name='pq_write_partitioned')
        builder.call(xng__cfs, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr, types.int64, types.voidptr
        ), codegen
