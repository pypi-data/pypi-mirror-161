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
    aakg__seg = typemap[node.file_name.name]
    if types.unliteral(aakg__seg) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {aakg__seg}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        ytnvr__roome = typemap[node.skiprows.name]
        if isinstance(ytnvr__roome, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(ytnvr__roome, types.Integer) and not (isinstance
            (ytnvr__roome, (types.List, types.Tuple)) and isinstance(
            ytnvr__roome.dtype, types.Integer)) and not isinstance(ytnvr__roome
            , (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {ytnvr__roome}."
                , loc=node.skiprows.loc)
        elif isinstance(ytnvr__roome, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        jxzki__beht = typemap[node.nrows.name]
        if not isinstance(jxzki__beht, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {jxzki__beht}."
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
        flz__lkrcs = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        wupi__jjo = cgutils.get_or_insert_function(builder.module,
            flz__lkrcs, name='csv_file_chunk_reader')
        nyb__bxx = builder.call(wupi__jjo, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        bhtq__bqt = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        bbore__btdy = context.get_python_api(builder)
        bhtq__bqt.meminfo = bbore__btdy.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), nyb__bxx)
        bhtq__bqt.pyobj = nyb__bxx
        bbore__btdy.decref(nyb__bxx)
        return bhtq__bqt._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        rpgot__egh = csv_node.out_vars[0]
        if rpgot__egh.name not in lives:
            return None
    else:
        duvq__jabpf = csv_node.out_vars[0]
        yjrml__rhe = csv_node.out_vars[1]
        if duvq__jabpf.name not in lives and yjrml__rhe.name not in lives:
            return None
        elif yjrml__rhe.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif duvq__jabpf.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    ytnvr__roome = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            lhjci__wjzvb = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            hmb__dyc = csv_node.loc.strformat()
            pcupy__fiwqx = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', lhjci__wjzvb,
                hmb__dyc, pcupy__fiwqx)
            lvfk__ibkmf = csv_node.out_types[0].yield_type.data
            nfa__ptil = [qdar__uad for otqyj__lql, qdar__uad in enumerate(
                csv_node.df_colnames) if isinstance(lvfk__ibkmf[otqyj__lql],
                bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if nfa__ptil:
                yeyc__befat = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    yeyc__befat, hmb__dyc, nfa__ptil)
        if array_dists is not None:
            kqjwy__sjfk = csv_node.out_vars[0].name
            parallel = array_dists[kqjwy__sjfk] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        twedg__rvrbw = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        twedg__rvrbw += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        twedg__rvrbw += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        anc__plf = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(twedg__rvrbw, {}, anc__plf)
        sdy__vcmno = anc__plf['csv_iterator_impl']
        vrub__nwdof = 'def csv_reader_init(fname, nrows, skiprows):\n'
        vrub__nwdof += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        vrub__nwdof += '  return f_reader\n'
        exec(vrub__nwdof, globals(), anc__plf)
        cpwac__qoszg = anc__plf['csv_reader_init']
        fje__rlh = numba.njit(cpwac__qoszg)
        compiled_funcs.append(fje__rlh)
        bfd__gkyjt = compile_to_numba_ir(sdy__vcmno, {'_csv_reader_init':
            fje__rlh, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, ytnvr__roome), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(bfd__gkyjt, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        jjp__flqg = bfd__gkyjt.body[:-3]
        jjp__flqg[-1].target = csv_node.out_vars[0]
        return jjp__flqg
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    twedg__rvrbw = 'def csv_impl(fname, nrows, skiprows):\n'
    twedg__rvrbw += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    anc__plf = {}
    exec(twedg__rvrbw, {}, anc__plf)
    yagf__thgzu = anc__plf['csv_impl']
    mdq__kfza = csv_node.usecols
    if mdq__kfza:
        mdq__kfza = [csv_node.usecols[otqyj__lql] for otqyj__lql in
            csv_node.out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        lhjci__wjzvb = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        hmb__dyc = csv_node.loc.strformat()
        pcupy__fiwqx = []
        nfa__ptil = []
        if mdq__kfza:
            for otqyj__lql in csv_node.out_used_cols:
                jhz__jtv = csv_node.df_colnames[otqyj__lql]
                pcupy__fiwqx.append(jhz__jtv)
                if isinstance(csv_node.out_types[otqyj__lql], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    nfa__ptil.append(jhz__jtv)
        bodo.user_logging.log_message('Column Pruning', lhjci__wjzvb,
            hmb__dyc, pcupy__fiwqx)
        if nfa__ptil:
            yeyc__befat = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                yeyc__befat, hmb__dyc, nfa__ptil)
    ylawj__ftp = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, mdq__kfza, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    bfd__gkyjt = compile_to_numba_ir(yagf__thgzu, {'_csv_reader_py':
        ylawj__ftp}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, ytnvr__roome), typemap=typemap, calltypes
        =calltypes).blocks.popitem()[1]
    replace_arg_nodes(bfd__gkyjt, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    jjp__flqg = bfd__gkyjt.body[:-3]
    jjp__flqg[-1].target = csv_node.out_vars[1]
    jjp__flqg[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not mdq__kfza
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        jjp__flqg.pop(-1)
    elif not mdq__kfza:
        jjp__flqg.pop(-2)
    return jjp__flqg


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
    xqy__lvjd = t.dtype
    if isinstance(xqy__lvjd, PDCategoricalDtype):
        zivsd__nyo = CategoricalArrayType(xqy__lvjd)
        bzxk__wfzfk = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, bzxk__wfzfk, zivsd__nyo)
        return bzxk__wfzfk
    if xqy__lvjd == types.NPDatetime('ns'):
        xqy__lvjd = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        yzogx__jyuzm = 'int_arr_{}'.format(xqy__lvjd)
        setattr(types, yzogx__jyuzm, t)
        return yzogx__jyuzm
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if xqy__lvjd == types.bool_:
        xqy__lvjd = 'bool_'
    if xqy__lvjd == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(xqy__lvjd, (
        StringArrayType, ArrayItemArrayType)):
        aiaz__kxgt = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, aiaz__kxgt, t)
        return aiaz__kxgt
    return '{}[::1]'.format(xqy__lvjd)


def _get_pd_dtype_str(t):
    xqy__lvjd = t.dtype
    if isinstance(xqy__lvjd, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(xqy__lvjd.categories)
    if xqy__lvjd == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if xqy__lvjd.signed else 'U',
            xqy__lvjd.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(xqy__lvjd, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(xqy__lvjd)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    goz__wldyh = ''
    from collections import defaultdict
    kcuj__kyun = defaultdict(list)
    for ljyj__aup, avw__ghc in typemap.items():
        kcuj__kyun[avw__ghc].append(ljyj__aup)
    yfbbb__vpwd = df.columns.to_list()
    qzmpt__kzqim = []
    for avw__ghc, uzuvg__rhii in kcuj__kyun.items():
        try:
            qzmpt__kzqim.append(df.loc[:, uzuvg__rhii].astype(avw__ghc,
                copy=False))
            df = df.drop(uzuvg__rhii, axis=1)
        except (ValueError, TypeError) as bqg__uwt:
            goz__wldyh = (
                f"Caught the runtime error '{bqg__uwt}' on columns {uzuvg__rhii}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    iimsa__xbg = bool(goz__wldyh)
    if parallel:
        jbf__lbso = MPI.COMM_WORLD
        iimsa__xbg = jbf__lbso.allreduce(iimsa__xbg, op=MPI.LOR)
    if iimsa__xbg:
        ikc__rnsuh = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if goz__wldyh:
            raise TypeError(f'{ikc__rnsuh}\n{goz__wldyh}')
        else:
            raise TypeError(
                f'{ikc__rnsuh}\nPlease refer to errors on other ranks.')
    df = pd.concat(qzmpt__kzqim + [df], axis=1)
    uyazp__iyyhj = df.loc[:, yfbbb__vpwd]
    return uyazp__iyyhj


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    irp__axuw = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        twedg__rvrbw = '  skiprows = sorted(set(skiprows))\n'
    else:
        twedg__rvrbw = '  skiprows = [skiprows]\n'
    twedg__rvrbw += '  skiprows_list_len = len(skiprows)\n'
    twedg__rvrbw += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    twedg__rvrbw += '  check_java_installation(fname)\n'
    twedg__rvrbw += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    twedg__rvrbw += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    twedg__rvrbw += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    twedg__rvrbw += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, irp__axuw, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    twedg__rvrbw += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    twedg__rvrbw += "      raise FileNotFoundError('File does not exist')\n"
    return twedg__rvrbw


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    qpb__cyt = [str(otqyj__lql) for otqyj__lql, ryec__vtoa in enumerate(
        usecols) if col_typs[out_used_cols[otqyj__lql]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        qpb__cyt.append(str(idx_col_index))
    fua__xqbtu = ', '.join(qpb__cyt)
    jbds__ligib = _gen_parallel_flag_name(sanitized_cnames)
    zrv__ahg = f"{jbds__ligib}='bool_'" if check_parallel_runtime else ''
    nwonz__xeiev = [_get_pd_dtype_str(col_typs[out_used_cols[otqyj__lql]]) for
        otqyj__lql in range(len(usecols))]
    kqle__wjhzk = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    wizwf__ytc = [ryec__vtoa for otqyj__lql, ryec__vtoa in enumerate(
        usecols) if nwonz__xeiev[otqyj__lql] == 'str']
    if idx_col_index is not None and kqle__wjhzk == 'str':
        wizwf__ytc.append(idx_col_index)
    yfftc__pmdd = np.array(wizwf__ytc, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = yfftc__pmdd
    twedg__rvrbw = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    qgca__din = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = qgca__din
    twedg__rvrbw += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    xdwyy__itfwz = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = xdwyy__itfwz
        twedg__rvrbw += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    xjzt__ynwen = defaultdict(list)
    for otqyj__lql, ryec__vtoa in enumerate(usecols):
        if nwonz__xeiev[otqyj__lql] == 'str':
            continue
        xjzt__ynwen[nwonz__xeiev[otqyj__lql]].append(ryec__vtoa)
    if idx_col_index is not None and kqle__wjhzk != 'str':
        xjzt__ynwen[kqle__wjhzk].append(idx_col_index)
    for otqyj__lql, qdxf__uorc in enumerate(xjzt__ynwen.values()):
        glbs[f't_arr_{otqyj__lql}_{call_id}'] = np.asarray(qdxf__uorc)
        twedg__rvrbw += (
            f'  t_arr_{otqyj__lql}_{call_id}_2 = t_arr_{otqyj__lql}_{call_id}\n'
            )
    if idx_col_index != None:
        twedg__rvrbw += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {zrv__ahg}):
"""
    else:
        twedg__rvrbw += (
            f'  with objmode(T=table_type_{call_id}, {zrv__ahg}):\n')
    twedg__rvrbw += f'    typemap = {{}}\n'
    for otqyj__lql, jwvod__mrsj in enumerate(xjzt__ynwen.keys()):
        twedg__rvrbw += f"""    typemap.update({{i:{jwvod__mrsj} for i in t_arr_{otqyj__lql}_{call_id}_2}})
"""
    twedg__rvrbw += '    if f_reader.get_chunk_size() == 0:\n'
    twedg__rvrbw += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    twedg__rvrbw += '    else:\n'
    twedg__rvrbw += '      df = pd.read_csv(f_reader,\n'
    twedg__rvrbw += '        header=None,\n'
    twedg__rvrbw += '        parse_dates=[{}],\n'.format(fua__xqbtu)
    twedg__rvrbw += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    twedg__rvrbw += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        twedg__rvrbw += f'    {jbds__ligib} = f_reader.is_parallel()\n'
    else:
        twedg__rvrbw += f'    {jbds__ligib} = {parallel}\n'
    twedg__rvrbw += f'    df = astype(df, typemap, {jbds__ligib})\n'
    if idx_col_index != None:
        pnmu__vdnc = sorted(qgca__din).index(idx_col_index)
        twedg__rvrbw += f'    idx_arr = df.iloc[:, {pnmu__vdnc}].values\n'
        twedg__rvrbw += (
            f'    df.drop(columns=df.columns[{pnmu__vdnc}], inplace=True)\n')
    if len(usecols) == 0:
        twedg__rvrbw += f'    T = None\n'
    else:
        twedg__rvrbw += f'    arrs = []\n'
        twedg__rvrbw += f'    for i in range(df.shape[1]):\n'
        twedg__rvrbw += f'      arrs.append(df.iloc[:, i].values)\n'
        twedg__rvrbw += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return twedg__rvrbw


def _gen_parallel_flag_name(sanitized_cnames):
    jbds__ligib = '_parallel_value'
    while jbds__ligib in sanitized_cnames:
        jbds__ligib = '_' + jbds__ligib
    return jbds__ligib


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(qdar__uad) for qdar__uad in col_names]
    twedg__rvrbw = 'def csv_reader_py(fname, nrows, skiprows):\n'
    twedg__rvrbw += _gen_csv_file_reader_init(parallel, header, compression,
        -1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    zmv__ycpx = globals()
    if idx_col_typ != types.none:
        zmv__ycpx[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        zmv__ycpx[f'table_type_{call_id}'] = types.none
    else:
        zmv__ycpx[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    twedg__rvrbw += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, zmv__ycpx, parallel=parallel, check_parallel_runtime=False,
        idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        twedg__rvrbw += '  return (T, idx_arr)\n'
    else:
        twedg__rvrbw += '  return (T, None)\n'
    anc__plf = {}
    zmv__ycpx['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(twedg__rvrbw, zmv__ycpx, anc__plf)
    ylawj__ftp = anc__plf['csv_reader_py']
    fje__rlh = numba.njit(ylawj__ftp)
    compiled_funcs.append(fje__rlh)
    return fje__rlh
