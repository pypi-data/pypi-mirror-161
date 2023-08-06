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
    ubsdy__ahoz = typemap[node.file_name.name]
    if types.unliteral(ubsdy__ahoz) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {ubsdy__ahoz}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        lqd__fpqd = typemap[node.skiprows.name]
        if isinstance(lqd__fpqd, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(lqd__fpqd, types.Integer) and not (isinstance(
            lqd__fpqd, (types.List, types.Tuple)) and isinstance(lqd__fpqd.
            dtype, types.Integer)) and not isinstance(lqd__fpqd, (types.
            LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {lqd__fpqd}."
                , loc=node.skiprows.loc)
        elif isinstance(lqd__fpqd, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        orbpb__hno = typemap[node.nrows.name]
        if not isinstance(orbpb__hno, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {orbpb__hno}."
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
        zuaxu__sntjv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        gexfu__adu = cgutils.get_or_insert_function(builder.module,
            zuaxu__sntjv, name='csv_file_chunk_reader')
        kgm__yil = builder.call(gexfu__adu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        zoxux__ouo = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        aqjz__lxy = context.get_python_api(builder)
        zoxux__ouo.meminfo = aqjz__lxy.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), kgm__yil)
        zoxux__ouo.pyobj = kgm__yil
        aqjz__lxy.decref(kgm__yil)
        return zoxux__ouo._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        mxom__rcfdh = csv_node.out_vars[0]
        if mxom__rcfdh.name not in lives:
            return None
    else:
        hyvf__zui = csv_node.out_vars[0]
        zsq__wlj = csv_node.out_vars[1]
        if hyvf__zui.name not in lives and zsq__wlj.name not in lives:
            return None
        elif zsq__wlj.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif hyvf__zui.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    lqd__fpqd = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            jllj__efeu = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            bso__swn = csv_node.loc.strformat()
            ewkbs__ugvji = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', jllj__efeu,
                bso__swn, ewkbs__ugvji)
            oixgp__fxe = csv_node.out_types[0].yield_type.data
            qdhy__lnw = [ofde__kvzbj for tcdin__eqw, ofde__kvzbj in
                enumerate(csv_node.df_colnames) if isinstance(oixgp__fxe[
                tcdin__eqw], bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if qdhy__lnw:
                bez__amczo = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    bez__amczo, bso__swn, qdhy__lnw)
        if array_dists is not None:
            epdlw__uuvyz = csv_node.out_vars[0].name
            parallel = array_dists[epdlw__uuvyz] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        xdle__vlgp = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        xdle__vlgp += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        xdle__vlgp += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        ilam__wbn = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(xdle__vlgp, {}, ilam__wbn)
        ebv__qivb = ilam__wbn['csv_iterator_impl']
        nerz__pxawq = 'def csv_reader_init(fname, nrows, skiprows):\n'
        nerz__pxawq += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        nerz__pxawq += '  return f_reader\n'
        exec(nerz__pxawq, globals(), ilam__wbn)
        zox__wheob = ilam__wbn['csv_reader_init']
        ckt__gepr = numba.njit(zox__wheob)
        compiled_funcs.append(ckt__gepr)
        uffnb__vej = compile_to_numba_ir(ebv__qivb, {'_csv_reader_init':
            ckt__gepr, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, lqd__fpqd), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(uffnb__vej, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        eheiz__hmjmz = uffnb__vej.body[:-3]
        eheiz__hmjmz[-1].target = csv_node.out_vars[0]
        return eheiz__hmjmz
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    xdle__vlgp = 'def csv_impl(fname, nrows, skiprows):\n'
    xdle__vlgp += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    ilam__wbn = {}
    exec(xdle__vlgp, {}, ilam__wbn)
    jfy__bdiw = ilam__wbn['csv_impl']
    eupb__qbsm = csv_node.usecols
    if eupb__qbsm:
        eupb__qbsm = [csv_node.usecols[tcdin__eqw] for tcdin__eqw in
            csv_node.out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        jllj__efeu = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        bso__swn = csv_node.loc.strformat()
        ewkbs__ugvji = []
        qdhy__lnw = []
        if eupb__qbsm:
            for tcdin__eqw in csv_node.out_used_cols:
                gtmz__wmen = csv_node.df_colnames[tcdin__eqw]
                ewkbs__ugvji.append(gtmz__wmen)
                if isinstance(csv_node.out_types[tcdin__eqw], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    qdhy__lnw.append(gtmz__wmen)
        bodo.user_logging.log_message('Column Pruning', jllj__efeu,
            bso__swn, ewkbs__ugvji)
        if qdhy__lnw:
            bez__amczo = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', bez__amczo,
                bso__swn, qdhy__lnw)
    ukkn__jrpme = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, eupb__qbsm, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    uffnb__vej = compile_to_numba_ir(jfy__bdiw, {'_csv_reader_py':
        ukkn__jrpme}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, lqd__fpqd), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(uffnb__vej, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    eheiz__hmjmz = uffnb__vej.body[:-3]
    eheiz__hmjmz[-1].target = csv_node.out_vars[1]
    eheiz__hmjmz[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not eupb__qbsm
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        eheiz__hmjmz.pop(-1)
    elif not eupb__qbsm:
        eheiz__hmjmz.pop(-2)
    return eheiz__hmjmz


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
    qlyx__rmv = t.dtype
    if isinstance(qlyx__rmv, PDCategoricalDtype):
        igt__fnjp = CategoricalArrayType(qlyx__rmv)
        peik__iit = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, peik__iit, igt__fnjp)
        return peik__iit
    if qlyx__rmv == types.NPDatetime('ns'):
        qlyx__rmv = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        wgcop__jlwyq = 'int_arr_{}'.format(qlyx__rmv)
        setattr(types, wgcop__jlwyq, t)
        return wgcop__jlwyq
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if qlyx__rmv == types.bool_:
        qlyx__rmv = 'bool_'
    if qlyx__rmv == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(qlyx__rmv, (
        StringArrayType, ArrayItemArrayType)):
        vgrf__uqq = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, vgrf__uqq, t)
        return vgrf__uqq
    return '{}[::1]'.format(qlyx__rmv)


def _get_pd_dtype_str(t):
    qlyx__rmv = t.dtype
    if isinstance(qlyx__rmv, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(qlyx__rmv.categories)
    if qlyx__rmv == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if qlyx__rmv.signed else 'U',
            qlyx__rmv.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(qlyx__rmv, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(qlyx__rmv)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    tnre__xho = ''
    from collections import defaultdict
    jijjv__ycmqc = defaultdict(list)
    for ejhyu__ekwa, iwcc__cpvn in typemap.items():
        jijjv__ycmqc[iwcc__cpvn].append(ejhyu__ekwa)
    pltkx__gin = df.columns.to_list()
    jryp__efsp = []
    for iwcc__cpvn, iwhw__fga in jijjv__ycmqc.items():
        try:
            jryp__efsp.append(df.loc[:, iwhw__fga].astype(iwcc__cpvn, copy=
                False))
            df = df.drop(iwhw__fga, axis=1)
        except (ValueError, TypeError) as xwhge__pnbmy:
            tnre__xho = (
                f"Caught the runtime error '{xwhge__pnbmy}' on columns {iwhw__fga}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    wyw__rzq = bool(tnre__xho)
    if parallel:
        qwind__hsw = MPI.COMM_WORLD
        wyw__rzq = qwind__hsw.allreduce(wyw__rzq, op=MPI.LOR)
    if wyw__rzq:
        qenj__sgiw = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if tnre__xho:
            raise TypeError(f'{qenj__sgiw}\n{tnre__xho}')
        else:
            raise TypeError(
                f'{qenj__sgiw}\nPlease refer to errors on other ranks.')
    df = pd.concat(jryp__efsp + [df], axis=1)
    aerk__fzq = df.loc[:, pltkx__gin]
    return aerk__fzq


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    nyxrz__vuqtj = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        xdle__vlgp = '  skiprows = sorted(set(skiprows))\n'
    else:
        xdle__vlgp = '  skiprows = [skiprows]\n'
    xdle__vlgp += '  skiprows_list_len = len(skiprows)\n'
    xdle__vlgp += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    xdle__vlgp += '  check_java_installation(fname)\n'
    xdle__vlgp += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    xdle__vlgp += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    xdle__vlgp += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    xdle__vlgp += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, nyxrz__vuqtj, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    xdle__vlgp += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    xdle__vlgp += "      raise FileNotFoundError('File does not exist')\n"
    return xdle__vlgp


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    ukhwn__edokg = [str(tcdin__eqw) for tcdin__eqw, byal__xykd in enumerate
        (usecols) if col_typs[out_used_cols[tcdin__eqw]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        ukhwn__edokg.append(str(idx_col_index))
    nejku__zbbe = ', '.join(ukhwn__edokg)
    scjyc__ohbjw = _gen_parallel_flag_name(sanitized_cnames)
    voma__mvcr = f"{scjyc__ohbjw}='bool_'" if check_parallel_runtime else ''
    ixe__fsa = [_get_pd_dtype_str(col_typs[out_used_cols[tcdin__eqw]]) for
        tcdin__eqw in range(len(usecols))]
    ubd__lccuh = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    szw__gpulw = [byal__xykd for tcdin__eqw, byal__xykd in enumerate(
        usecols) if ixe__fsa[tcdin__eqw] == 'str']
    if idx_col_index is not None and ubd__lccuh == 'str':
        szw__gpulw.append(idx_col_index)
    edjbn__oem = np.array(szw__gpulw, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = edjbn__oem
    xdle__vlgp = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    vvcc__klh = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = vvcc__klh
    xdle__vlgp += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    ubwxi__pqss = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = ubwxi__pqss
        xdle__vlgp += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    johhk__wtjb = defaultdict(list)
    for tcdin__eqw, byal__xykd in enumerate(usecols):
        if ixe__fsa[tcdin__eqw] == 'str':
            continue
        johhk__wtjb[ixe__fsa[tcdin__eqw]].append(byal__xykd)
    if idx_col_index is not None and ubd__lccuh != 'str':
        johhk__wtjb[ubd__lccuh].append(idx_col_index)
    for tcdin__eqw, asrj__umxh in enumerate(johhk__wtjb.values()):
        glbs[f't_arr_{tcdin__eqw}_{call_id}'] = np.asarray(asrj__umxh)
        xdle__vlgp += (
            f'  t_arr_{tcdin__eqw}_{call_id}_2 = t_arr_{tcdin__eqw}_{call_id}\n'
            )
    if idx_col_index != None:
        xdle__vlgp += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {voma__mvcr}):
"""
    else:
        xdle__vlgp += (
            f'  with objmode(T=table_type_{call_id}, {voma__mvcr}):\n')
    xdle__vlgp += f'    typemap = {{}}\n'
    for tcdin__eqw, mvnlc__skz in enumerate(johhk__wtjb.keys()):
        xdle__vlgp += f"""    typemap.update({{i:{mvnlc__skz} for i in t_arr_{tcdin__eqw}_{call_id}_2}})
"""
    xdle__vlgp += '    if f_reader.get_chunk_size() == 0:\n'
    xdle__vlgp += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    xdle__vlgp += '    else:\n'
    xdle__vlgp += '      df = pd.read_csv(f_reader,\n'
    xdle__vlgp += '        header=None,\n'
    xdle__vlgp += '        parse_dates=[{}],\n'.format(nejku__zbbe)
    xdle__vlgp += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    xdle__vlgp += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        xdle__vlgp += f'    {scjyc__ohbjw} = f_reader.is_parallel()\n'
    else:
        xdle__vlgp += f'    {scjyc__ohbjw} = {parallel}\n'
    xdle__vlgp += f'    df = astype(df, typemap, {scjyc__ohbjw})\n'
    if idx_col_index != None:
        ccuff__lodc = sorted(vvcc__klh).index(idx_col_index)
        xdle__vlgp += f'    idx_arr = df.iloc[:, {ccuff__lodc}].values\n'
        xdle__vlgp += (
            f'    df.drop(columns=df.columns[{ccuff__lodc}], inplace=True)\n')
    if len(usecols) == 0:
        xdle__vlgp += f'    T = None\n'
    else:
        xdle__vlgp += f'    arrs = []\n'
        xdle__vlgp += f'    for i in range(df.shape[1]):\n'
        xdle__vlgp += f'      arrs.append(df.iloc[:, i].values)\n'
        xdle__vlgp += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return xdle__vlgp


def _gen_parallel_flag_name(sanitized_cnames):
    scjyc__ohbjw = '_parallel_value'
    while scjyc__ohbjw in sanitized_cnames:
        scjyc__ohbjw = '_' + scjyc__ohbjw
    return scjyc__ohbjw


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(ofde__kvzbj) for ofde__kvzbj in
        col_names]
    xdle__vlgp = 'def csv_reader_py(fname, nrows, skiprows):\n'
    xdle__vlgp += _gen_csv_file_reader_init(parallel, header, compression, 
        -1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    ohc__bvv = globals()
    if idx_col_typ != types.none:
        ohc__bvv[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        ohc__bvv[f'table_type_{call_id}'] = types.none
    else:
        ohc__bvv[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    xdle__vlgp += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, ohc__bvv, parallel=parallel, check_parallel_runtime=False,
        idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        xdle__vlgp += '  return (T, idx_arr)\n'
    else:
        xdle__vlgp += '  return (T, None)\n'
    ilam__wbn = {}
    ohc__bvv['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(xdle__vlgp, ohc__bvv, ilam__wbn)
    ukkn__jrpme = ilam__wbn['csv_reader_py']
    ckt__gepr = numba.njit(ukkn__jrpme)
    compiled_funcs.append(ckt__gepr)
    return ckt__gepr
