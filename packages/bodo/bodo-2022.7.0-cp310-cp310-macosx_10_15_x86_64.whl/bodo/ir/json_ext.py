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
        zzxle__zoz = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        gup__pbwpu = cgutils.get_or_insert_function(builder.module,
            zzxle__zoz, name='json_file_chunk_reader')
        epbb__llk = builder.call(gup__pbwpu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        rvr__aort = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        spur__vljaf = context.get_python_api(builder)
        rvr__aort.meminfo = spur__vljaf.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), epbb__llk)
        rvr__aort.pyobj = epbb__llk
        spur__vljaf.decref(epbb__llk)
        return rvr__aort._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.bool_,
        types.int64, types.voidptr, types.voidptr, storage_options_dict_type
        ), codegen


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    jxhl__ajvp = []
    vmkxq__lyks = []
    ccu__jvkg = []
    for wwxsk__jflp, innfe__ccu in enumerate(json_node.out_vars):
        if innfe__ccu.name in lives:
            jxhl__ajvp.append(json_node.df_colnames[wwxsk__jflp])
            vmkxq__lyks.append(json_node.out_vars[wwxsk__jflp])
            ccu__jvkg.append(json_node.out_types[wwxsk__jflp])
    json_node.df_colnames = jxhl__ajvp
    json_node.out_vars = vmkxq__lyks
    json_node.out_types = ccu__jvkg
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        tffz__jiltv = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        pdld__quc = json_node.loc.strformat()
        mxtl__dpckg = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', tffz__jiltv,
            pdld__quc, mxtl__dpckg)
        wdt__afsi = [hvyr__cfgo for wwxsk__jflp, hvyr__cfgo in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            wwxsk__jflp], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if wdt__afsi:
            nmck__bxayp = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding',
                nmck__bxayp, pdld__quc, wdt__afsi)
    parallel = False
    if array_dists is not None:
        parallel = True
        for ugclj__xko in json_node.out_vars:
            if array_dists[ugclj__xko.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                ugclj__xko.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    zxewa__mjjmd = len(json_node.out_vars)
    wbx__zhfz = ', '.join('arr' + str(wwxsk__jflp) for wwxsk__jflp in range
        (zxewa__mjjmd))
    mihly__wir = 'def json_impl(fname):\n'
    mihly__wir += '    ({},) = _json_reader_py(fname)\n'.format(wbx__zhfz)
    ijtan__yymh = {}
    exec(mihly__wir, {}, ijtan__yymh)
    zxon__swp = ijtan__yymh['json_impl']
    qth__pau = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    idvtu__czq = compile_to_numba_ir(zxon__swp, {'_json_reader_py':
        qth__pau}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(idvtu__czq, [json_node.file_name])
    ygflv__gkkoe = idvtu__czq.body[:-3]
    for wwxsk__jflp in range(len(json_node.out_vars)):
        ygflv__gkkoe[-len(json_node.out_vars) + wwxsk__jflp
            ].target = json_node.out_vars[wwxsk__jflp]
    return ygflv__gkkoe


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
    qzhk__ubjwj = [sanitize_varname(hvyr__cfgo) for hvyr__cfgo in col_names]
    yiqql__qzh = ', '.join(str(wwxsk__jflp) for wwxsk__jflp, hdj__tzmv in
        enumerate(col_typs) if hdj__tzmv.dtype == types.NPDatetime('ns'))
    llqj__wgzm = ', '.join(["{}='{}'".format(qccx__xhk, bodo.ir.csv_ext.
        _get_dtype_str(hdj__tzmv)) for qccx__xhk, hdj__tzmv in zip(
        qzhk__ubjwj, col_typs)])
    ygkl__oqzxa = ', '.join(["'{}':{}".format(wbj__orrzw, bodo.ir.csv_ext.
        _get_pd_dtype_str(hdj__tzmv)) for wbj__orrzw, hdj__tzmv in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    mihly__wir = 'def json_reader_py(fname):\n'
    mihly__wir += '  df_typeref_2 = df_typeref\n'
    mihly__wir += '  check_java_installation(fname)\n'
    mihly__wir += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    mihly__wir += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    mihly__wir += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    mihly__wir += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    mihly__wir += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    mihly__wir += "      raise FileNotFoundError('File does not exist')\n"
    mihly__wir += f'  with objmode({llqj__wgzm}):\n'
    mihly__wir += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    mihly__wir += f'       convert_dates = {convert_dates}, \n'
    mihly__wir += f'       precise_float={precise_float}, \n'
    mihly__wir += f'       lines={lines}, \n'
    mihly__wir += '       dtype={{{}}},\n'.format(ygkl__oqzxa)
    mihly__wir += '       )\n'
    mihly__wir += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for qccx__xhk, wbj__orrzw in zip(qzhk__ubjwj, col_names):
        mihly__wir += '    if len(df) > 0:\n'
        mihly__wir += "        {} = df['{}'].values\n".format(qccx__xhk,
            wbj__orrzw)
        mihly__wir += '    else:\n'
        mihly__wir += '        {} = np.array([])\n'.format(qccx__xhk)
    mihly__wir += '  return ({},)\n'.format(', '.join(qdnz__ftuy for
        qdnz__ftuy in qzhk__ubjwj))
    maf__mut = globals()
    maf__mut.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode': objmode,
        'check_java_installation': check_java_installation, 'df_typeref':
        bodo.DataFrameType(tuple(col_typs), bodo.RangeIndexType(None),
        tuple(col_names)), 'get_storage_options_pyobject':
        get_storage_options_pyobject})
    ijtan__yymh = {}
    exec(mihly__wir, maf__mut, ijtan__yymh)
    qth__pau = ijtan__yymh['json_reader_py']
    pkyvv__vcho = numba.njit(qth__pau)
    compiled_funcs.append(pkyvv__vcho)
    return pkyvv__vcho
