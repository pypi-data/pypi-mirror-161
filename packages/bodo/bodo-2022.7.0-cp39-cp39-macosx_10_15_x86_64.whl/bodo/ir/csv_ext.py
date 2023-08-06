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
    mvhte__awval = typemap[node.file_name.name]
    if types.unliteral(mvhte__awval) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {mvhte__awval}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        zybzr__jwcu = typemap[node.skiprows.name]
        if isinstance(zybzr__jwcu, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(zybzr__jwcu, types.Integer) and not (isinstance
            (zybzr__jwcu, (types.List, types.Tuple)) and isinstance(
            zybzr__jwcu.dtype, types.Integer)) and not isinstance(zybzr__jwcu,
            (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {zybzr__jwcu}."
                , loc=node.skiprows.loc)
        elif isinstance(zybzr__jwcu, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        vxhkb__poyrq = typemap[node.nrows.name]
        if not isinstance(vxhkb__poyrq, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {vxhkb__poyrq}."
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
        olixy__petp = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(1), lir.IntType(64),
            lir.IntType(1)])
        kbcv__bpe = cgutils.get_or_insert_function(builder.module,
            olixy__petp, name='csv_file_chunk_reader')
        dgiv__zuda = builder.call(kbcv__bpe, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        spd__ryp = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        yomox__odjg = context.get_python_api(builder)
        spd__ryp.meminfo = yomox__odjg.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), dgiv__zuda)
        spd__ryp.pyobj = dgiv__zuda
        yomox__odjg.decref(dgiv__zuda)
        return spd__ryp._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.
        voidptr, types.int64, types.bool_, types.voidptr, types.voidptr,
        storage_options_dict_type, types.int64, types.bool_, types.int64,
        types.bool_), codegen


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        bnsdp__xks = csv_node.out_vars[0]
        if bnsdp__xks.name not in lives:
            return None
    else:
        cghbo__nkt = csv_node.out_vars[0]
        nocw__tfeps = csv_node.out_vars[1]
        if cghbo__nkt.name not in lives and nocw__tfeps.name not in lives:
            return None
        elif nocw__tfeps.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif cghbo__nkt.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.out_used_cols = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    zybzr__jwcu = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        parallel = False
        if bodo.user_logging.get_verbose_level() >= 1:
            moub__fzjy = (
                'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n'
                )
            ugm__eojfd = csv_node.loc.strformat()
            mbk__pdyn = csv_node.df_colnames
            bodo.user_logging.log_message('Column Pruning', moub__fzjy,
                ugm__eojfd, mbk__pdyn)
            szhab__lel = csv_node.out_types[0].yield_type.data
            sgczl__ivk = [nhr__whcii for cwmc__xvp, nhr__whcii in enumerate
                (csv_node.df_colnames) if isinstance(szhab__lel[cwmc__xvp],
                bodo.libs.dict_arr_ext.DictionaryArrayType)]
            if sgczl__ivk:
                dat__vgr = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
                bodo.user_logging.log_message('Dictionary Encoding',
                    dat__vgr, ugm__eojfd, sgczl__ivk)
        if array_dists is not None:
            ssrj__kpifj = csv_node.out_vars[0].name
            parallel = array_dists[ssrj__kpifj] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        tlvwi__lvfs = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        tlvwi__lvfs += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        tlvwi__lvfs += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        xdqzi__nqlhj = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(tlvwi__lvfs, {}, xdqzi__nqlhj)
        pym__ngzye = xdqzi__nqlhj['csv_iterator_impl']
        bbq__jycce = 'def csv_reader_init(fname, nrows, skiprows):\n'
        bbq__jycce += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory, csv_node.storage_options)
        bbq__jycce += '  return f_reader\n'
        exec(bbq__jycce, globals(), xdqzi__nqlhj)
        zjh__tzkpw = xdqzi__nqlhj['csv_reader_init']
        vmyv__rxxzk = numba.njit(zjh__tzkpw)
        compiled_funcs.append(vmyv__rxxzk)
        yhh__ipinr = compile_to_numba_ir(pym__ngzye, {'_csv_reader_init':
            vmyv__rxxzk, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, zybzr__jwcu), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(yhh__ipinr, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        grml__tfl = yhh__ipinr.body[:-3]
        grml__tfl[-1].target = csv_node.out_vars[0]
        return grml__tfl
    parallel = bodo.ir.connector.is_connector_table_parallel(csv_node,
        array_dists, typemap, 'CSVReader')
    tlvwi__lvfs = 'def csv_impl(fname, nrows, skiprows):\n'
    tlvwi__lvfs += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    xdqzi__nqlhj = {}
    exec(tlvwi__lvfs, {}, xdqzi__nqlhj)
    pvy__gdh = xdqzi__nqlhj['csv_impl']
    rsqe__pymr = csv_node.usecols
    if rsqe__pymr:
        rsqe__pymr = [csv_node.usecols[cwmc__xvp] for cwmc__xvp in csv_node
            .out_used_cols]
    if bodo.user_logging.get_verbose_level() >= 1:
        moub__fzjy = (
            'Finish column pruning on read_csv node:\n%s\nColumns loaded %s\n')
        ugm__eojfd = csv_node.loc.strformat()
        mbk__pdyn = []
        sgczl__ivk = []
        if rsqe__pymr:
            for cwmc__xvp in csv_node.out_used_cols:
                kjxdh__bijk = csv_node.df_colnames[cwmc__xvp]
                mbk__pdyn.append(kjxdh__bijk)
                if isinstance(csv_node.out_types[cwmc__xvp], bodo.libs.
                    dict_arr_ext.DictionaryArrayType):
                    sgczl__ivk.append(kjxdh__bijk)
        bodo.user_logging.log_message('Column Pruning', moub__fzjy,
            ugm__eojfd, mbk__pdyn)
        if sgczl__ivk:
            dat__vgr = """Finished optimized encoding on read_csv node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', dat__vgr,
                ugm__eojfd, sgczl__ivk)
    wklsj__qeffj = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, rsqe__pymr, csv_node.out_used_cols, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        csv_node.storage_options, idx_col_index=csv_node.index_column_index,
        idx_col_typ=csv_node.index_column_typ)
    yhh__ipinr = compile_to_numba_ir(pvy__gdh, {'_csv_reader_py':
        wklsj__qeffj}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, zybzr__jwcu), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(yhh__ipinr, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    grml__tfl = yhh__ipinr.body[:-3]
    grml__tfl[-1].target = csv_node.out_vars[1]
    grml__tfl[-2].target = csv_node.out_vars[0]
    assert not (csv_node.index_column_index is None and not rsqe__pymr
        ), 'At most one of table and index should be dead if the CSV IR node is live'
    if csv_node.index_column_index is None:
        grml__tfl.pop(-1)
    elif not rsqe__pymr:
        grml__tfl.pop(-2)
    return grml__tfl


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
    jqbw__upls = t.dtype
    if isinstance(jqbw__upls, PDCategoricalDtype):
        lhmu__zdok = CategoricalArrayType(jqbw__upls)
        fcwhv__ntkfb = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, fcwhv__ntkfb, lhmu__zdok)
        return fcwhv__ntkfb
    if jqbw__upls == types.NPDatetime('ns'):
        jqbw__upls = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        yxke__eksy = 'int_arr_{}'.format(jqbw__upls)
        setattr(types, yxke__eksy, t)
        return yxke__eksy
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if jqbw__upls == types.bool_:
        jqbw__upls = 'bool_'
    if jqbw__upls == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(jqbw__upls, (
        StringArrayType, ArrayItemArrayType)):
        vzvrl__myyl = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, vzvrl__myyl, t)
        return vzvrl__myyl
    return '{}[::1]'.format(jqbw__upls)


def _get_pd_dtype_str(t):
    jqbw__upls = t.dtype
    if isinstance(jqbw__upls, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(jqbw__upls.categories)
    if jqbw__upls == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if jqbw__upls.signed else 'U',
            jqbw__upls.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(jqbw__upls, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(jqbw__upls)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    ovjp__mlnep = ''
    from collections import defaultdict
    ubo__umhhz = defaultdict(list)
    for iyte__ppcs, jzfq__pnc in typemap.items():
        ubo__umhhz[jzfq__pnc].append(iyte__ppcs)
    bxio__pwri = df.columns.to_list()
    xbmqc__hjust = []
    for jzfq__pnc, ygzk__nidwe in ubo__umhhz.items():
        try:
            xbmqc__hjust.append(df.loc[:, ygzk__nidwe].astype(jzfq__pnc,
                copy=False))
            df = df.drop(ygzk__nidwe, axis=1)
        except (ValueError, TypeError) as vytsl__xcih:
            ovjp__mlnep = (
                f"Caught the runtime error '{vytsl__xcih}' on columns {ygzk__nidwe}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    ubng__cathi = bool(ovjp__mlnep)
    if parallel:
        mgvko__ygfk = MPI.COMM_WORLD
        ubng__cathi = mgvko__ygfk.allreduce(ubng__cathi, op=MPI.LOR)
    if ubng__cathi:
        kvlw__nll = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if ovjp__mlnep:
            raise TypeError(f'{kvlw__nll}\n{ovjp__mlnep}')
        else:
            raise TypeError(
                f'{kvlw__nll}\nPlease refer to errors on other ranks.')
    df = pd.concat(xbmqc__hjust + [df], axis=1)
    xwq__nraux = df.loc[:, bxio__pwri]
    return xwq__nraux


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory, storage_options):
    nqsh__hkjvx = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        tlvwi__lvfs = '  skiprows = sorted(set(skiprows))\n'
    else:
        tlvwi__lvfs = '  skiprows = [skiprows]\n'
    tlvwi__lvfs += '  skiprows_list_len = len(skiprows)\n'
    tlvwi__lvfs += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    tlvwi__lvfs += '  check_java_installation(fname)\n'
    tlvwi__lvfs += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    tlvwi__lvfs += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tlvwi__lvfs += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    tlvwi__lvfs += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py, {}, {}, skiprows_list_len, {})
"""
        .format(parallel, nqsh__hkjvx, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    tlvwi__lvfs += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    tlvwi__lvfs += "      raise FileNotFoundError('File does not exist')\n"
    return tlvwi__lvfs


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    out_used_cols, sep, escapechar, storage_options, call_id, glbs,
    parallel, check_parallel_runtime, idx_col_index, idx_col_typ):
    eoixy__gvepc = [str(cwmc__xvp) for cwmc__xvp, pfy__bap in enumerate(
        usecols) if col_typs[out_used_cols[cwmc__xvp]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        eoixy__gvepc.append(str(idx_col_index))
    uvkhz__tys = ', '.join(eoixy__gvepc)
    ndi__fnhfv = _gen_parallel_flag_name(sanitized_cnames)
    ubxug__nfel = f"{ndi__fnhfv}='bool_'" if check_parallel_runtime else ''
    xqxu__hgzaj = [_get_pd_dtype_str(col_typs[out_used_cols[cwmc__xvp]]) for
        cwmc__xvp in range(len(usecols))]
    zorrl__ehlmu = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    owkel__zfa = [pfy__bap for cwmc__xvp, pfy__bap in enumerate(usecols) if
        xqxu__hgzaj[cwmc__xvp] == 'str']
    if idx_col_index is not None and zorrl__ehlmu == 'str':
        owkel__zfa.append(idx_col_index)
    wnz__dxy = np.array(owkel__zfa, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = wnz__dxy
    tlvwi__lvfs = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    fbm__ikx = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []), dtype=np.int64)
    glbs[f'usecols_arr_{call_id}'] = fbm__ikx
    tlvwi__lvfs += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    lruy__zkq = np.array(out_used_cols, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = lruy__zkq
        tlvwi__lvfs += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    ebd__ktu = defaultdict(list)
    for cwmc__xvp, pfy__bap in enumerate(usecols):
        if xqxu__hgzaj[cwmc__xvp] == 'str':
            continue
        ebd__ktu[xqxu__hgzaj[cwmc__xvp]].append(pfy__bap)
    if idx_col_index is not None and zorrl__ehlmu != 'str':
        ebd__ktu[zorrl__ehlmu].append(idx_col_index)
    for cwmc__xvp, urgf__mxful in enumerate(ebd__ktu.values()):
        glbs[f't_arr_{cwmc__xvp}_{call_id}'] = np.asarray(urgf__mxful)
        tlvwi__lvfs += (
            f'  t_arr_{cwmc__xvp}_{call_id}_2 = t_arr_{cwmc__xvp}_{call_id}\n')
    if idx_col_index != None:
        tlvwi__lvfs += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {ubxug__nfel}):
"""
    else:
        tlvwi__lvfs += (
            f'  with objmode(T=table_type_{call_id}, {ubxug__nfel}):\n')
    tlvwi__lvfs += f'    typemap = {{}}\n'
    for cwmc__xvp, tsjx__yexw in enumerate(ebd__ktu.keys()):
        tlvwi__lvfs += f"""    typemap.update({{i:{tsjx__yexw} for i in t_arr_{cwmc__xvp}_{call_id}_2}})
"""
    tlvwi__lvfs += '    if f_reader.get_chunk_size() == 0:\n'
    tlvwi__lvfs += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    tlvwi__lvfs += '    else:\n'
    tlvwi__lvfs += '      df = pd.read_csv(f_reader,\n'
    tlvwi__lvfs += '        header=None,\n'
    tlvwi__lvfs += '        parse_dates=[{}],\n'.format(uvkhz__tys)
    tlvwi__lvfs += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    tlvwi__lvfs += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        tlvwi__lvfs += f'    {ndi__fnhfv} = f_reader.is_parallel()\n'
    else:
        tlvwi__lvfs += f'    {ndi__fnhfv} = {parallel}\n'
    tlvwi__lvfs += f'    df = astype(df, typemap, {ndi__fnhfv})\n'
    if idx_col_index != None:
        cflx__pqcd = sorted(fbm__ikx).index(idx_col_index)
        tlvwi__lvfs += f'    idx_arr = df.iloc[:, {cflx__pqcd}].values\n'
        tlvwi__lvfs += (
            f'    df.drop(columns=df.columns[{cflx__pqcd}], inplace=True)\n')
    if len(usecols) == 0:
        tlvwi__lvfs += f'    T = None\n'
    else:
        tlvwi__lvfs += f'    arrs = []\n'
        tlvwi__lvfs += f'    for i in range(df.shape[1]):\n'
        tlvwi__lvfs += f'      arrs.append(df.iloc[:, i].values)\n'
        tlvwi__lvfs += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return tlvwi__lvfs


def _gen_parallel_flag_name(sanitized_cnames):
    ndi__fnhfv = '_parallel_value'
    while ndi__fnhfv in sanitized_cnames:
        ndi__fnhfv = '_' + ndi__fnhfv
    return ndi__fnhfv


def _gen_csv_reader_py(col_names, col_typs, usecols, out_used_cols, sep,
    parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, storage_options, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(nhr__whcii) for nhr__whcii in
        col_names]
    tlvwi__lvfs = 'def csv_reader_py(fname, nrows, skiprows):\n'
    tlvwi__lvfs += _gen_csv_file_reader_init(parallel, header, compression,
        -1, is_skiprows_list, pd_low_memory, storage_options)
    call_id = ir_utils.next_label()
    wig__buzpp = globals()
    if idx_col_typ != types.none:
        wig__buzpp[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        wig__buzpp[f'table_type_{call_id}'] = types.none
    else:
        wig__buzpp[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    tlvwi__lvfs += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, out_used_cols, sep, escapechar, storage_options,
        call_id, wig__buzpp, parallel=parallel, check_parallel_runtime=
        False, idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        tlvwi__lvfs += '  return (T, idx_arr)\n'
    else:
        tlvwi__lvfs += '  return (T, None)\n'
    xdqzi__nqlhj = {}
    wig__buzpp['get_storage_options_pyobject'] = get_storage_options_pyobject
    exec(tlvwi__lvfs, wig__buzpp, xdqzi__nqlhj)
    wklsj__qeffj = xdqzi__nqlhj['csv_reader_py']
    vmyv__rxxzk = numba.njit(wklsj__qeffj)
    compiled_funcs.append(vmyv__rxxzk)
    return vmyv__rxxzk
