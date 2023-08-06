"""
Class information for DataFrame iterators returned by pd.read_csv. This is used
to handle situations in which pd.read_csv is used to return chunks with separate
read calls instead of just a single read.
"""
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir_utils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl
from numba.core.typing.templates import signature
from numba.extending import intrinsic, lower_builtin, models, register_model
import bodo
import bodo.ir.connector
import bodo.ir.csv_ext
from bodo import objmode
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.table import Table, TableType
from bodo.io import csv_cpp
from bodo.ir.csv_ext import _gen_read_csv_objmode, astype
from bodo.utils.typing import ColNamesMetaType
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname
ll.add_symbol('update_csv_reader', csv_cpp.update_csv_reader)
ll.add_symbol('initialize_csv_reader', csv_cpp.initialize_csv_reader)


class CSVIteratorType(types.SimpleIteratorType):

    def __init__(self, df_type, out_colnames, out_types, usecols, sep,
        index_ind, index_arr_typ, index_name, escapechar, storage_options):
        assert isinstance(df_type, DataFrameType
            ), 'CSVIterator must return a DataFrame'
        anmn__metpq = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(anmn__metpq)
        self._yield_type = df_type
        self._out_colnames = out_colnames
        self._out_types = out_types
        self._usecols = usecols
        self._sep = sep
        self._index_ind = index_ind
        self._index_arr_typ = index_arr_typ
        self._index_name = index_name
        self._escapechar = escapechar
        self._storage_options = storage_options

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(CSVIteratorType)
class CSVIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        eeyk__nsdfc = [('csv_reader', types.stream_reader_type), ('index',
            types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, eeyk__nsdfc)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    hmpaq__sia = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    xpdm__wrue = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer()]
        )
    suf__jjdde = cgutils.get_or_insert_function(builder.module, xpdm__wrue,
        name='initialize_csv_reader')
    rvfoj__jpqt = cgutils.create_struct_proxy(types.stream_reader_type)(context
        , builder, value=hmpaq__sia.csv_reader)
    builder.call(suf__jjdde, [rvfoj__jpqt.pyobj])
    builder.store(context.get_constant(types.uint64, 0), hmpaq__sia.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [aysy__hlha] = sig.args
    [nerw__zgp] = args
    hmpaq__sia = cgutils.create_struct_proxy(aysy__hlha)(context, builder,
        value=nerw__zgp)
    xpdm__wrue = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer()]
        )
    suf__jjdde = cgutils.get_or_insert_function(builder.module, xpdm__wrue,
        name='update_csv_reader')
    rvfoj__jpqt = cgutils.create_struct_proxy(types.stream_reader_type)(context
        , builder, value=hmpaq__sia.csv_reader)
    otrdn__okw = builder.call(suf__jjdde, [rvfoj__jpqt.pyobj])
    result.set_valid(otrdn__okw)
    with builder.if_then(otrdn__okw):
        cxp__urtgy = builder.load(hmpaq__sia.index)
        tauny__qzdr = types.Tuple([sig.return_type.first_type, types.int64])
        lnui__brhf = gen_read_csv_objmode(sig.args[0])
        zgvch__avz = signature(tauny__qzdr, types.stream_reader_type, types
            .int64)
        xhgz__lccl = context.compile_internal(builder, lnui__brhf,
            zgvch__avz, [hmpaq__sia.csv_reader, cxp__urtgy])
        poov__gnp, ugo__hapnh = cgutils.unpack_tuple(builder, xhgz__lccl)
        pqz__virg = builder.add(cxp__urtgy, ugo__hapnh, flags=['nsw'])
        builder.store(pqz__virg, hmpaq__sia.index)
        result.yield_(poov__gnp)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        cvvon__brh = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        context.nrt.incref(builder, signature.args[0], args[0])
        cvvon__brh.csv_reader = args[0]
        ckjac__grd = context.get_constant(types.uintp, 0)
        cvvon__brh.index = cgutils.alloca_once_value(builder, ckjac__grd)
        return cvvon__brh._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    nnuzp__nxgu = csv_iterator_typeref.instance_type
    sig = signature(nnuzp__nxgu, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    zymue__qxp = 'def read_csv_objmode(f_reader):\n'
    nnrzb__srueq = [sanitize_varname(fqdl__nis) for fqdl__nis in
        csv_iterator_type._out_colnames]
    teemw__bvs = ir_utils.next_label()
    meig__rmjo = globals()
    out_types = csv_iterator_type._out_types
    meig__rmjo[f'table_type_{teemw__bvs}'] = TableType(tuple(out_types))
    meig__rmjo[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    vgcn__jvg = list(range(len(csv_iterator_type._usecols)))
    zymue__qxp += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        nnrzb__srueq, out_types, csv_iterator_type._usecols, vgcn__jvg,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, teemw__bvs, meig__rmjo,
        parallel=False, check_parallel_runtime=True, idx_col_index=
        csv_iterator_type._index_ind, idx_col_typ=csv_iterator_type.
        _index_arr_typ)
    krcl__baeyx = bodo.ir.csv_ext._gen_parallel_flag_name(nnrzb__srueq)
    fmrhk__kdse = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [krcl__baeyx]
    zymue__qxp += f"  return {', '.join(fmrhk__kdse)}"
    meig__rmjo = globals()
    bxgi__wmims = {}
    exec(zymue__qxp, meig__rmjo, bxgi__wmims)
    wdw__wuec = bxgi__wmims['read_csv_objmode']
    nve__rjjbq = numba.njit(wdw__wuec)
    bodo.ir.csv_ext.compiled_funcs.append(nve__rjjbq)
    cyxo__bdj = 'def read_func(reader, local_start):\n'
    cyxo__bdj += f"  {', '.join(fmrhk__kdse)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        cyxo__bdj += f'  local_len = len(T)\n'
        cyxo__bdj += '  total_size = local_len\n'
        cyxo__bdj += f'  if ({krcl__baeyx}):\n'
        cyxo__bdj += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        cyxo__bdj += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        ioykz__hji = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        cyxo__bdj += '  total_size = 0\n'
        ioykz__hji = (
            f'bodo.utils.conversion.convert_to_index({fmrhk__kdse[1]}, {csv_iterator_type._index_name!r})'
            )
    cyxo__bdj += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({fmrhk__kdse[0]},), {ioykz__hji}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(cyxo__bdj, {'bodo': bodo, 'objmode_func': nve__rjjbq, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, bxgi__wmims)
    return bxgi__wmims['read_func']
