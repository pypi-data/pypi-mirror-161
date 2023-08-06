import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
from numba.extending import intrinsic
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.io.fs_io import get_storage_options_pyobject, storage_options_dict_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.utils.utils import check_and_propagate_cpp_exception, check_java_installation, sanitize_varname


class JsonReader(ir.Stmt):

    def __init__(self, df_out, loc, out_vars, out_types, file_name,
        df_colnames, orient, convert_dates, precise_float, lines,
        compression, storage_options):
        self.connector_typ = 'json'
        self.df_out = df_out
        self.loc = loc
        self.out_vars = out_vars
        self.out_types = out_types
        self.file_name = file_name
        self.df_colnames = df_colnames
        self.orient = orient
        self.convert_dates = convert_dates
        self.precise_float = precise_float
        self.lines = lines
        self.compression = compression
        self.storage_options = storage_options

    def __repr__(self):
        return ('{} = ReadJson(file={}, col_names={}, types={}, vars={})'.
            format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars))


import llvmlite.binding as ll
from bodo.io import json_cpp
ll.add_symbol('json_file_chunk_reader', json_cpp.json_file_chunk_reader)


@intrinsic
def json_file_chunk_reader(typingctx, fname_t, lines_t, is_parallel_t,
    nrows_t, compression_t, bucket_region_t, storage_options_t):
    assert storage_options_t == storage_options_dict_type, "Storage options don't match expected type"

    def codegen(context, builder, sig, args):
        jqh__trthf = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        erf__zuunq = cgutils.get_or_insert_function(builder.module,
            jqh__trthf, name='json_file_chunk_reader')
        joctj__vaj = builder.call(erf__zuunq, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        fjxf__srpw = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        lcp__owd = context.get_python_api(builder)
        fjxf__srpw.meminfo = lcp__owd.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), joctj__vaj)
        fjxf__srpw.pyobj = joctj__vaj
        lcp__owd.decref(joctj__vaj)
        return fjxf__srpw._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.bool_,
        types.int64, types.voidptr, types.voidptr, storage_options_dict_type
        ), codegen


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    vmg__xca = []
    dhc__vrxuy = []
    zsgl__oek = []
    for dqtek__prr, wkhec__cvsb in enumerate(json_node.out_vars):
        if wkhec__cvsb.name in lives:
            vmg__xca.append(json_node.df_colnames[dqtek__prr])
            dhc__vrxuy.append(json_node.out_vars[dqtek__prr])
            zsgl__oek.append(json_node.out_types[dqtek__prr])
    json_node.df_colnames = vmg__xca
    json_node.out_vars = dhc__vrxuy
    json_node.out_types = zsgl__oek
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        bdl__bght = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        pupti__xrc = json_node.loc.strformat()
        ahtg__dcgt = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', bdl__bght,
            pupti__xrc, ahtg__dcgt)
        owylk__ydc = [qxqf__pag for dqtek__prr, qxqf__pag in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            dqtek__prr], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if owylk__ydc:
            ainbo__zbrh = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                ainbo__zbrh, pupti__xrc, owylk__ydc)
    parallel = False
    if array_dists is not None:
        parallel = True
        for gaf__uxxjr in json_node.out_vars:
            if array_dists[gaf__uxxjr.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                gaf__uxxjr.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    dbku__yymu = len(json_node.out_vars)
    mhq__yziz = ', '.join('arr' + str(dqtek__prr) for dqtek__prr in range(
        dbku__yymu))
    lswq__xjbvz = 'def json_impl(fname):\n'
    lswq__xjbvz += '    ({},) = _json_reader_py(fname)\n'.format(mhq__yziz)
    jvk__mqcg = {}
    exec(lswq__xjbvz, {}, jvk__mqcg)
    tsy__iaydb = jvk__mqcg['json_impl']
    ofit__ffoq = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    amnj__oogvl = compile_to_numba_ir(tsy__iaydb, {'_json_reader_py':
        ofit__ffoq}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(amnj__oogvl, [json_node.file_name])
    fft__xwonw = amnj__oogvl.body[:-3]
    for dqtek__prr in range(len(json_node.out_vars)):
        fft__xwonw[-len(json_node.out_vars) + dqtek__prr
            ].target = json_node.out_vars[dqtek__prr]
    return fft__xwonw


numba.parfors.array_analysis.array_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[JsonReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[JsonReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[JsonReader] = remove_dead_json
numba.core.analysis.ir_extension_usedefs[JsonReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[JsonReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[JsonReader] = json_distributed_run
compiled_funcs = []


def _gen_json_reader_py(col_names, col_typs, typingctx, targetctx, parallel,
    orient, convert_dates, precise_float, lines, compression, storage_options):
    lly__qxz = [sanitize_varname(qxqf__pag) for qxqf__pag in col_names]
    tax__ppgx = ', '.join(str(dqtek__prr) for dqtek__prr, embeo__tydk in
        enumerate(col_typs) if embeo__tydk.dtype == types.NPDatetime('ns'))
    gyks__qorqq = ', '.join(["{}='{}'".format(hfei__vqeax, bodo.ir.csv_ext.
        _get_dtype_str(embeo__tydk)) for hfei__vqeax, embeo__tydk in zip(
        lly__qxz, col_typs)])
    zji__wzjdj = ', '.join(["'{}':{}".format(ksdv__kjiy, bodo.ir.csv_ext.
        _get_pd_dtype_str(embeo__tydk)) for ksdv__kjiy, embeo__tydk in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    lswq__xjbvz = 'def json_reader_py(fname):\n'
    lswq__xjbvz += '  df_typeref_2 = df_typeref\n'
    lswq__xjbvz += '  check_java_installation(fname)\n'
    lswq__xjbvz += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    lswq__xjbvz += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    lswq__xjbvz += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    lswq__xjbvz += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    lswq__xjbvz += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    lswq__xjbvz += "      raise FileNotFoundError('File does not exist')\n"
    lswq__xjbvz += f'  with objmode({gyks__qorqq}):\n'
    lswq__xjbvz += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    lswq__xjbvz += f'       convert_dates = {convert_dates}, \n'
    lswq__xjbvz += f'       precise_float={precise_float}, \n'
    lswq__xjbvz += f'       lines={lines}, \n'
    lswq__xjbvz += '       dtype={{{}}},\n'.format(zji__wzjdj)
    lswq__xjbvz += '       )\n'
    lswq__xjbvz += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for hfei__vqeax, ksdv__kjiy in zip(lly__qxz, col_names):
        lswq__xjbvz += '    if len(df) > 0:\n'
        lswq__xjbvz += "        {} = df['{}'].values\n".format(hfei__vqeax,
            ksdv__kjiy)
        lswq__xjbvz += '    else:\n'
        lswq__xjbvz += '        {} = np.array([])\n'.format(hfei__vqeax)
    lswq__xjbvz += '  return ({},)\n'.format(', '.join(tgr__oll for
        tgr__oll in lly__qxz))
    ahbc__mqhm = globals()
    ahbc__mqhm.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode': objmode,
        'check_java_installation': check_java_installation, 'df_typeref':
        bodo.DataFrameType(tuple(col_typs), bodo.RangeIndexType(None),
        tuple(col_names)), 'get_storage_options_pyobject':
        get_storage_options_pyobject})
    jvk__mqcg = {}
    exec(lswq__xjbvz, ahbc__mqhm, jvk__mqcg)
    ofit__ffoq = jvk__mqcg['json_reader_py']
    ojit__cekvm = numba.njit(ofit__ffoq)
    compiled_funcs.append(ojit__cekvm)
    return ojit__cekvm
