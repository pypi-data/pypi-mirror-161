from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
from numba.extending import intrinsic
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import Table, TableType
from bodo.io.fs_io import get_storage_options_pyobject, storage_options_dict_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import check_and_propagate_cpp_exception, sanitize_varname


class CsvReader(ir.Stmt):

    def __init__(self, file_name, df_out, sep, df_colnames, out_vars,
        out_types, usecols, loc, header, compression, nrows, skiprows,
        chunksize, is_skiprows_list, low_memory, escapechar,
        storage_options=None, index_column_index=None, index_column_typ=
        types.none):
        self.connector_typ = 'csv'
        self.file_name = file_name
        self.df_out = df_out
        self.sep = sep
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.usecols = usecols
        self.loc = loc
        self.skiprows = skiprows
        self.nrows = nrows
        self.header = header
        self.compression = compression
        self.chunksize = chunksize
        self.is_skiprows_list = is_skiprows_list
        self.pd_low_memory = low_memory
        self.escapechar = escapechar
        self.storage_options = storage_options
        self.index_column_index = index_column_index
        self.index_column_typ = index_column_typ
        self.out_used_cols = list(range(len(usecols)))

    def __repr__(self):
        return (
            '{} = ReadCsv(file={}, col_names={}, types={}, vars={}, nrows={}, skiprows={}, chunksize={}, is_skiprows_list={}, pd_low_memory={}, escapechar={}, storage_options={}, index_column_index={}, index_colum_typ = {}, out_used_colss={})'
            .format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars, self.nrows, self.skiprows, self.
            chunksize, self.is_skiprows_list, self.pd_low_memory, self.
            escapechar, self.storage_options, self.index_column_index, self
            .index_column_typ, self.out_used_cols))


def check_node_typing(node, typemap):
    dksem__vlnw = typemap[node.file_name.name]
    if types.unliteral(dksem__vlnw) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {dksem__vlnw}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        gfu__gdyw = typemap[node.skiprows.name]
        if isinstance(gfu__gdyw, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(gfu__gdyw, types.Integer) and not (isinstance(
            gfu__gdyw, (types.List, types.Tuple)) and isinstance(gfu__gdyw.
            dtype, types.Integer)) and not isinstance(gfu__gdyw, (types.
            LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {gfu__gdyw}."
                , loc=node.skiprows.loc)
        elif isinstance(gfu__gdyw, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        gndb__zji = typemap[node.nrows.name]
        if not isinstance(gndb__zji, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {gndb__zji}."
                , loc=node.nrows.loc)


import llvmlite.binding as ll
from bodo.io import csv_cpp
ll.add_symbol('csv_file_chunk_reader', csv_cpp.csv_file_chunk_reader)


@intrinsic
def csv_file_chunk_reader(typingctx, fname_t, is_parallel_t, skiprows_t,
    nrows_t, header_t, compression_t, bucket_region_t, storage_options_t,
    chunksize_t, is_skiprows_list_t, skiprows_list_len_t, pd_low_memory_t):
    assert storage_options_t == storage_options_dict_type, "Storage options don't match expected type"

    def codegen(context, builder, sig, args):
        idkqy__gaqy = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        lbhqz__vngji = cgutils.get_or_insert_function(builder.module,
            idkqy__gaqy, name='csv_file_chunk_reader')
        fbzs__ojbyt = builder.call(lbhqz__vngji, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        dox__pjxx = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        voxrn__kjhbo = context.get_python_api(builder)
        dox__pjxx.meminfo = voxrn__kjhbo.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), fbzs__ojbyt)
        dox__pjxx.pyobj = fbzs__ojbyt
        voxrn__kjhbo.decref(fbzs__ojbyt)
        return dox__pjxx._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        ffzx__moo = csv_node.out_vars[0]
        if ffzx__moo.name not in lives:
            return None
    else:
        mshp__nxnk = csv_node.out_vars[0]
        ycehe__vjc = csv_node.out_vars[1]
        if mshp__nxnk.name not in lives and ycehe__vjc.name not in lives:
            return None
        elif ycehe__vjc.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif mshp__nxnk.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    gfu__gdyw = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            sqpos__clvo = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            apq__mjo = csv_node.loc.strformat()
            bxlef__rlgo = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', sqpos__clvo,
                apq__mjo, bxlef__rlgo)
            yinos__rfnk = csv_node.out_types[0].yield_type.data
            tbps__sxz = [cba__beslt for hntwj__dmkyn, cba__beslt in
                enumerate(csv_node.df_colnames) if isinstance(yinos__rfnk[
                hntwj__dmkyn], bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if tbps__sxz:
                crz__btnx = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    crz__btnx, apq__mjo, tbps__sxz)
        if array_dists is not None:
            vmpj__semx = csv_node.out_vars[0].name
            parallel = array_dists[vmpj__semx] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        qsm__jzt = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        qsm__jzt += f'    reader = _csv_reader_init(fname, nrows, skiprows)\n'
        qsm__jzt += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        igb__xmh = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(qsm__jzt, {}, igb__xmh)
        ckfe__ohfzd = igb__xmh['csv_iterator_impl']
        kae__dzh = 'def csv_reader_init(fname, nrows, skiprows):\n'
        kae__dzh += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        kae__dzh += '  return f_reader\n'
        exec(kae__dzh, globals(), igb__xmh)
        luh__vmwaa = igb__xmh['csv_reader_init']
        cud__lyl = numba.njit(luh__vmwaa)
        compiled_funcs.append(cud__lyl)
        mkhuz__bsa = compile_to_numba_ir(ckfe__ohfzd, {'_csv_reader_init':
            cud__lyl, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, gfu__gdyw), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(mkhuz__bsa, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        pmcw__fsp = mkhuz__bsa.body[:-3]
        pmcw__fsp[-1].target = csv_node.out_vars[0]
        return pmcw__fsp
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    qsm__jzt = 'def csv_impl(fname, nrows, skiprows):\n'
    qsm__jzt += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    igb__xmh = {}
    exec(qsm__jzt, {}, igb__xmh)
    vlorx__zlbl = igb__xmh['csv_impl']
    ljrov__fjsv = csv_node.usecols
    if ljrov__fjsv:
        ljrov__fjsv = [csv_node.usecols[hntwj__dmkyn] for hntwj__dmkyn in
            csv_node.out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        sqpos__clvo = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        apq__mjo = csv_node.loc.strformat()
        bxlef__rlgo = []
        tbps__sxz = []
        if ljrov__fjsv:
            for hntwj__dmkyn in csv_node.out_used_cols:
                pgdu__nsy = csv_node.df_colnames[hntwj__dmkyn]
                bxlef__rlgo.append(pgdu__nsy)
                if isinstance(csv_node.out_types[hntwj__dmkyn], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    tbps__sxz.append(pgdu__nsy)
        bodo.user_logging.log_message('Column Pruning', sqpos__clvo,
            apq__mjo, bxlef__rlgo)
        if tbps__sxz:
            crz__btnx = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', crz__btnx,
                apq__mjo, tbps__sxz)
    orx__ovm = _gen_csv_reader_py(csv_node.df_colnames, csv_node.out_types,
        ljrov__fjsv, csv_node.out_used_cols, csv_node.sep, parallel,
        csv_node.header, csv_node.compression, csv_node.is_skiprows_list,
        csv_node.pd_low_memory, csv_node.escapechar, csv_node.
        storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    mkhuz__bsa = compile_to_numba_ir(vlorx__zlbl, {'_csv_reader_py':
        orx__ovm}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, gfu__gdyw), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(mkhuz__bsa, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    pmcw__fsp = mkhuz__bsa.body[:-3]
    pmcw__fsp[-1].target = csv_node.out_vars[1]
    pmcw__fsp[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not ljrov__fjsv
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        pmcw__fsp.pop(-1)
    elif not ljrov__fjsv:
        pmcw__fsp.pop(-2)
    return pmcw__fsp


def csv_remove_dead_column(csv_node, column_live_map, equiv_vars, typemap):
    if csv_node.chunksize is not None:
        return False
    return bodo.ir.connector.base_connector_remove_dead_columns(csv_node,
        column_live_map, equiv_vars, typemap, 'CSVReader', csv_node.usecols)


numba.parfors.array_analysis.array_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[CsvReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[CsvReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[CsvReader] = remove_dead_csv
numba.core.analysis.ir_extension_usedefs[CsvReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[CsvReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[CsvReader] = csv_distributed_run
remove_dead_column_extensions[CsvReader] = csv_remove_dead_column
ir_extension_table_column_use[CsvReader
    ] = bodo.ir.connector.connector_table_column_use


def _get_dtype_str(t):
    ddq__ilsr = t.dtype
    if isinstance(ddq__ilsr, PDCategoricalDtype):
        ihxtn__yhgb = CategoricalArrayType(ddq__ilsr)
        wua__cbl = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, wua__cbl, ihxtn__yhgb)
        return wua__cbl
    if ddq__ilsr == types.NPDatetime('ns'):
        ddq__ilsr = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        nhh__aismr = 'int_arr_{}'.format(ddq__ilsr)
        setattr(types, nhh__aismr, t)
        return nhh__aismr
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if ddq__ilsr == types.bool_:
        ddq__ilsr = 'bool_'
    if ddq__ilsr == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(ddq__ilsr, (
        StringArrayType, ArrayItemArrayType)):
        ews__qmza = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, ews__qmza, t)
        return ews__qmza
    return '{}[::1]'.format(ddq__ilsr)


def _get_pd_dtype_str(t):
    ddq__ilsr = t.dtype
    if isinstance(ddq__ilsr, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(ddq__ilsr.categories)
    if ddq__ilsr == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if ddq__ilsr.signed else 'U',
            ddq__ilsr.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(ddq__ilsr, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(ddq__ilsr)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    uca__wtzpz = ''
    from collections import defaultdict
    qgif__asq = defaultdict(list)
    for pqfcv__nndmp, iwoe__dbx in typemap.items():
        qgif__asq[iwoe__dbx].append(pqfcv__nndmp)
    cfhcc__ozord = df.columns.to_list()
    ioou__tpgba = []
    for iwoe__dbx, sad__abp in qgif__asq.items():
        try:
            ioou__tpgba.append(df.loc[:, sad__abp].astype(iwoe__dbx, copy=
                False))
            df = df.drop(sad__abp, axis=1)
        except (ValueError, TypeError) as aqgu__wrl:
            uca__wtzpz = (
                f"Caught the runtime error '{aqgu__wrl}' on columns {sad__abp}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    shnl__kqybe = bool(uca__wtzpz)
    if parallel:
        mwjgo__awrfz = MPI.COMM_WORLD
        shnl__kqybe = mwjgo__awrfz.allreduce(shnl__kqybe, op=MPI.LOR)
    if shnl__kqybe:
        tfom__mstry = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if uca__wtzpz:
            raise TypeError(f'{tfom__mstry}\n{uca__wtzpz}')
        else:
            raise TypeError(
                f'{tfom__mstry}\nPlease refer to errors on other ranks.')
    df = pd.concat(ioou__tpgba + [df], axis=1)
    wau__atykb = df.loc[:, cfhcc__ozord]
    return wau__atykb


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    siovy__ewe = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        qsm__jzt = '  skiprows = sorted(set(skiprows))\n'
    else:
        qsm__jzt = '  skiprows = [skiprows]\n'
    qsm__jzt += '  skiprows_list_len = len(skiprows)\n'
    qsm__jzt += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    qsm__jzt += '  check_java_installation(fname)\n'
    qsm__jzt += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    qsm__jzt += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    qsm__jzt += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    qsm__jzt += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, siovy__ewe, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    qsm__jzt += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    qsm__jzt += "      raise FileNotFoundError('File does not exist')\n"
    return qsm__jzt


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    agj__lok = [str(hntwj__dmkyn) for hntwj__dmkyn, lrtoc__munum in
        enumerate(usecols) if col_typs[out_used_cols[hntwj__dmkyn]].dtype ==
        types.NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        agj__lok.append(str(idx_col_index))
    vpnhu__cly = ', '.join(agj__lok)
    vrb__mynpq = _gen_parallel_flag_name(sanitized_cnames)
    ufzaz__mxz = f"{vrb__mynpq}='bool_'" if check_parallel_runtime else ''
    kum__ezwqf = [_get_pd_dtype_str(col_typs[out_used_cols[hntwj__dmkyn]]) for
        hntwj__dmkyn in range(len(usecols))]
    qgnw__nyyea = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    lhxo__yfnz = [lrtoc__munum for hntwj__dmkyn, lrtoc__munum in enumerate(
        usecols) if kum__ezwqf[hntwj__dmkyn] == 'str']
    if idx_col_index is not None and qgnw__nyyea == 'str':
        lhxo__yfnz.append(idx_col_index)
    xcp__fczba = np.array(lhxo__yfnz, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = xcp__fczba
    qsm__jzt = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    hpid__sycvz = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = hpid__sycvz
    qsm__jzt += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    moiqw__mfl = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = moiqw__mfl
        qsm__jzt += (
            f'  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}\n'
            )
    lfal__ujay = defaultdict(list)
    for hntwj__dmkyn, lrtoc__munum in enumerate(usecols):
        if kum__ezwqf[hntwj__dmkyn] == 'str':
            continue
        lfal__ujay[kum__ezwqf[hntwj__dmkyn]].append(lrtoc__munum)
    if idx_col_index is not None and qgnw__nyyea != 'str':
        lfal__ujay[qgnw__nyyea].append(idx_col_index)
    for hntwj__dmkyn, cfw__tmgig in enumerate(lfal__ujay.values()):
        glbs[f't_arr_{hntwj__dmkyn}_{call_id}'] = np.asarray(cfw__tmgig)
        qsm__jzt += (
            f'  t_arr_{hntwj__dmkyn}_{call_id}_2 = t_arr_{hntwj__dmkyn}_{call_id}\n'
            )
    if idx_col_index != None:
        qsm__jzt += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {ufzaz__mxz}):
"""
    else:
        qsm__jzt += f'  with objmode(T=table_type_{call_id}, {ufzaz__mxz}):\n'
    qsm__jzt += f'    typemap = {{}}\n'
    for hntwj__dmkyn, victh__kcm in enumerate(lfal__ujay.keys()):
        qsm__jzt += f"""    typemap.update({{i:{victh__kcm} for i in t_arr_{hntwj__dmkyn}_{call_id}_2}})
"""
    qsm__jzt += '    if f_reader.get_chunk_size() == 0:\n'
    qsm__jzt += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    qsm__jzt += '    else:\n'
    qsm__jzt += '      df = pd.read_csv(f_reader,\n'
    qsm__jzt += '        header=None,\n'
    qsm__jzt += '        parse_dates=[{}],\n'.format(vpnhu__cly)
    qsm__jzt += f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n'
    qsm__jzt += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        qsm__jzt += f'    {vrb__mynpq} = f_reader.is_parallel()\n'
    else:
        qsm__jzt += f'    {vrb__mynpq} = {parallel}\n'
    qsm__jzt += f'    df = astype(df, typemap, {vrb__mynpq})\n'
    if idx_col_index != None:
        vsihj__nhnm = sorted(hpid__sycvz).index(idx_col_index)
        qsm__jzt += f'    idx_arr = df.iloc[:, {vsihj__nhnm}].values\n'
        qsm__jzt += (
            f'    df.drop(columns=df.columns[{vsihj__nhnm}], inplace=True)\n')
    if len(usecols) == 0:
        qsm__jzt += f'    T = None\n'
    else:
        qsm__jzt += f'    arrs = []\n'
        qsm__jzt += f'    for i in range(df.shape[1]):\n'
        qsm__jzt += f'      arrs.append(df.iloc[:, i].values)\n'
        qsm__jzt += (
            f'    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})\n'
            )
    return qsm__jzt


def _gen_parallel_flag_name(sanitized_cnames):
    vrb__mynpq = '_parallel_value'
    while vrb__mynpq in sanitized_cnames:
        vrb__mynpq = '_' + vrb__mynpq
    return vrb__mynpq


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(cba__beslt) for cba__beslt in
        col_names]
    qsm__jzt = 'def csv_reader_py(fname, nrows, skiprows):\n'
    qsm__jzt += _gen_csv_file_reader_init(parallel, header, compression, -1,
        is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    rdb__hqk = globals()
    if idx_col_typ != types.none:
        rdb__hqk[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        rdb__hqk[f'table_type_{call_id}'] = types.none
    else:
        rdb__hqk[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    qsm__jzt += _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs,
        usecols, out_used_cols, sep, escapechar, storage_options, call_id,
        rdb__hqk, parallel=parallel, check_parallel_runtime=False,
        idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        qsm__jzt += '  return (T, idx_arr)\n'
    else:
        qsm__jzt += '  return (T, None)\n'
    igb__xmh = {}
    rdb__hqk['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(qsm__jzt, rdb__hqk, igb__xmh)
    orx__ovm = igb__xmh['csv_reader_py']
    cud__lyl = numba.njit(orx__ovm)
    compiled_funcs.append(cud__lyl)
    return cud__lyl
