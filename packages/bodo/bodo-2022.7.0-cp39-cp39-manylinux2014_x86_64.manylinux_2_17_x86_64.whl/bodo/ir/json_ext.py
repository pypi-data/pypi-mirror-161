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
        nmbp__xijym = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        gdso__qmcv = cgutils.get_or_insert_function(builder.module,
            nmbp__xijym, name='json_file_chunk_reader')
        nmp__gajrq = builder.call(gdso__qmcv, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        cin__ijsg = cgutils.create_struct_proxy(types.stream_reader_type)(
            context, builder)
        dqa__rytul = context.get_python_api(builder)
        cin__ijsg.meminfo = dqa__rytul.nrt_meminfo_new_from_pyobject(context
            .get_constant_null(types.voidptr), nmp__gajrq)
        cin__ijsg.pyobj = nmp__gajrq
        dqa__rytul.decref(nmp__gajrq)
        return cin__ijsg._getvalue()
    return types.stream_reader_type(types.voidptr, types.bool_, types.bool_,
        types.int64, types.voidptr, types.voidptr, storage_options_dict_type
        ), codegen


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    qjxx__rxkyt = []
    kszuu__eduyq = []
    jykkw__kga = []
    for veb__ria, azujd__veoxe in enumerate(json_node.out_vars):
        if azujd__veoxe.name in lives:
            qjxx__rxkyt.append(json_node.df_colnames[veb__ria])
            kszuu__eduyq.append(json_node.out_vars[veb__ria])
            jykkw__kga.append(json_node.out_types[veb__ria])
    json_node.df_colnames = qjxx__rxkyt
    json_node.out_vars = kszuu__eduyq
    json_node.out_types = jykkw__kga
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    if bodo.user_logging.get_verbose_level() >= 1:
        uyw__mxmg = (
            'Finish column pruning on read_json node:\n%s\nColumns loaded %s\n'
            )
        dfc__oksoi = json_node.loc.strformat()
        wyqno__dqglb = json_node.df_colnames
        bodo.user_logging.log_message('Column Pruning', uyw__mxmg,
            dfc__oksoi, wyqno__dqglb)
        xtpu__ylfp = [jpu__wcku for veb__ria, jpu__wcku in enumerate(
            json_node.df_colnames) if isinstance(json_node.out_types[
            veb__ria], bodo.libs.dict_arr_ext.DictionaryArrayType)]
        if xtpu__ylfp:
            quo__smr = """Finished optimized encoding on read_json node:
%s
Columns %s using dictionary encoding to reduce memory usage.
"""
            bodo.user_logging.log_message('Dictionary Encoding', quo__smr,
                dfc__oksoi, xtpu__ylfp)
    parallel = False
    if array_dists is not None:
        parallel = True
        for scia__ydzn in json_node.out_vars:
            if array_dists[scia__ydzn.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                scia__ydzn.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    jttcu__dspbt = len(json_node.out_vars)
    fds__aohoi = ', '.join('arr' + str(veb__ria) for veb__ria in range(
        jttcu__dspbt))
    hsig__pzsm = 'def json_impl(fname):\n'
    hsig__pzsm += '    ({},) = _json_reader_py(fname)\n'.format(fds__aohoi)
    uyxht__vdltg = {}
    exec(hsig__pzsm, {}, uyxht__vdltg)
    gkqn__scs = uyxht__vdltg['json_impl']
    bpcsy__simub = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression, json_node.storage_options)
    tpkly__thne = compile_to_numba_ir(gkqn__scs, {'_json_reader_py':
        bpcsy__simub}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(tpkly__thne, [json_node.file_name])
    ppbu__wojxe = tpkly__thne.body[:-3]
    for veb__ria in range(len(json_node.out_vars)):
        ppbu__wojxe[-len(json_node.out_vars) + veb__ria
            ].target = json_node.out_vars[veb__ria]
    return ppbu__wojxe


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
    kkvbx__vnecw = [sanitize_varname(jpu__wcku) for jpu__wcku in col_names]
    evt__nwum = ', '.join(str(veb__ria) for veb__ria, anu__smcmv in
        enumerate(col_typs) if anu__smcmv.dtype == types.NPDatetime('ns'))
    xlpnv__iyle = ', '.join(["{}='{}'".format(wynkr__hhat, bodo.ir.csv_ext.
        _get_dtype_str(anu__smcmv)) for wynkr__hhat, anu__smcmv in zip(
        kkvbx__vnecw, col_typs)])
    evstl__hnzj = ', '.join(["'{}':{}".format(cykr__hqx, bodo.ir.csv_ext.
        _get_pd_dtype_str(anu__smcmv)) for cykr__hqx, anu__smcmv in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    hsig__pzsm = 'def json_reader_py(fname):\n'
    hsig__pzsm += '  df_typeref_2 = df_typeref\n'
    hsig__pzsm += '  check_java_installation(fname)\n'
    hsig__pzsm += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    if storage_options is None:
        storage_options = {}
    storage_options['bodo_dummy'] = 'dummy'
    hsig__pzsm += (
        f'  storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    hsig__pzsm += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    hsig__pzsm += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), storage_options_py )
"""
        .format(lines, parallel, compression))
    hsig__pzsm += '  if bodo.utils.utils.is_null_pointer(f_reader._pyobj):\n'
    hsig__pzsm += "      raise FileNotFoundError('File does not exist')\n"
    hsig__pzsm += f'  with objmode({xlpnv__iyle}):\n'
    hsig__pzsm += f"    df = pd.read_json(f_reader, orient='{orient}',\n"
    hsig__pzsm += f'       convert_dates = {convert_dates}, \n'
    hsig__pzsm += f'       precise_float={precise_float}, \n'
    hsig__pzsm += f'       lines={lines}, \n'
    hsig__pzsm += '       dtype={{{}}},\n'.format(evstl__hnzj)
    hsig__pzsm += '       )\n'
    hsig__pzsm += (
        '    bodo.ir.connector.cast_float_to_nullable(df, df_typeref_2)\n')
    for wynkr__hhat, cykr__hqx in zip(kkvbx__vnecw, col_names):
        hsig__pzsm += '    if len(df) > 0:\n'
        hsig__pzsm += "        {} = df['{}'].values\n".format(wynkr__hhat,
            cykr__hqx)
        hsig__pzsm += '    else:\n'
        hsig__pzsm += '        {} = np.array([])\n'.format(wynkr__hhat)
    hsig__pzsm += '  return ({},)\n'.format(', '.join(fbg__rol for fbg__rol in
        kkvbx__vnecw))
    piff__nxel = globals()
    piff__nxel.update({'bodo': bodo, 'pd': pd, 'np': np, 'objmode': objmode,
        'check_java_installation': check_java_installation, 'df_typeref':
        bodo.DataFrameType(tuple(col_typs), bodo.RangeIndexType(None),
        tuple(col_names)), 'get_storage_options_pyobject':
        get_storage_options_pyobject})
    uyxht__vdltg = {}
    exec(hsig__pzsm, piff__nxel, uyxht__vdltg)
    bpcsy__simub = uyxht__vdltg['json_reader_py']
    zwveh__fhrx = numba.njit(bpcsy__simub)
    compiled_funcs.append(zwveh__fhrx)
    return zwveh__fhrx
