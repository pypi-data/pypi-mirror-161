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
        vus__hhumr = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(vus__hhumr)
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
        iqo__cpq = [('csv_reader', types.stream_reader_type), ('index',
            types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, iqo__cpq)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    ttm__tubof = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    tnzgp__aisbl = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer()])
    lmr__enu = cgutils.get_or_insert_function(builder.module, tnzgp__aisbl,
        name='initialize_csv_reader')
    myqbl__sisn = cgutils.create_struct_proxy(types.stream_reader_type)(context
        , builder, value=ttm__tubof.csv_reader)
    builder.call(lmr__enu, [myqbl__sisn.pyobj])
    builder.store(context.get_constant(types.uint64, 0), ttm__tubof.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [iaeq__gevuz] = sig.args
    [dlhg__lmb] = args
    ttm__tubof = cgutils.create_struct_proxy(iaeq__gevuz)(context, builder,
        value=dlhg__lmb)
    tnzgp__aisbl = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer()])
    lmr__enu = cgutils.get_or_insert_function(builder.module, tnzgp__aisbl,
        name='update_csv_reader')
    myqbl__sisn = cgutils.create_struct_proxy(types.stream_reader_type)(context
        , builder, value=ttm__tubof.csv_reader)
    mcaw__vbm = builder.call(lmr__enu, [myqbl__sisn.pyobj])
    result.set_valid(mcaw__vbm)
    with builder.if_then(mcaw__vbm):
        psy__sea = builder.load(ttm__tubof.index)
        csbr__gjds = types.Tuple([sig.return_type.first_type, types.int64])
        hqocc__yig = gen_read_csv_objmode(sig.args[0])
        nwomu__jlu = signature(csbr__gjds, types.stream_reader_type, types.
            int64)
        pklx__uhcr = context.compile_internal(builder, hqocc__yig,
            nwomu__jlu, [ttm__tubof.csv_reader, psy__sea])
        pnfpv__wjni, wnvby__hlcc = cgutils.unpack_tuple(builder, pklx__uhcr)
        dqihd__bmefj = builder.add(psy__sea, wnvby__hlcc, flags=['nsw'])
        builder.store(dqihd__bmefj, ttm__tubof.index)
        result.yield_(pnfpv__wjni)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        aoshc__aqjiw = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        context.nrt.incref(builder, signature.args[0], args[0])
        aoshc__aqjiw.csv_reader = args[0]
        qmz__wldn = context.get_constant(types.uintp, 0)
        aoshc__aqjiw.index = cgutils.alloca_once_value(builder, qmz__wldn)
        return aoshc__aqjiw._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    qbwr__crr = csv_iterator_typeref.instance_type
    sig = signature(qbwr__crr, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    sggr__ggoy = 'def read_csv_objmode(f_reader):\n'
    rtyu__nmb = [sanitize_varname(ofmgv__ckfg) for ofmgv__ckfg in
        csv_iterator_type._out_colnames]
    zneiw__djmn = ir_utils.next_label()
    dzzoh__shgxi = globals()
    out_types = csv_iterator_type._out_types
    dzzoh__shgxi[f'table_type_{zneiw__djmn}'] = TableType(tuple(out_types))
    dzzoh__shgxi[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    bnf__vsz = list(range(len(csv_iterator_type._usecols)))
    sggr__ggoy += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        rtyu__nmb, out_types, csv_iterator_type._usecols, bnf__vsz,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, zneiw__djmn, dzzoh__shgxi,
        parallel=False, check_parallel_runtime=True, idx_col_index=
        csv_iterator_type._index_ind, idx_col_typ=csv_iterator_type.
        _index_arr_typ)
    xfovv__vhcgo = bodo.ir.csv_ext._gen_parallel_flag_name(rtyu__nmb)
    nzozo__fxtmm = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [xfovv__vhcgo]
    sggr__ggoy += f"  return {', '.join(nzozo__fxtmm)}"
    dzzoh__shgxi = globals()
    tmkq__kry = {}
    exec(sggr__ggoy, dzzoh__shgxi, tmkq__kry)
    mkowc__bugzs = tmkq__kry['read_csv_objmode']
    lms__ykjh = numba.njit(mkowc__bugzs)
    bodo.ir.csv_ext.compiled_funcs.append(lms__ykjh)
    pjc__nuo = 'def read_func(reader, local_start):\n'
    pjc__nuo += f"  {', '.join(nzozo__fxtmm)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        pjc__nuo += f'  local_len = len(T)\n'
        pjc__nuo += '  total_size = local_len\n'
        pjc__nuo += f'  if ({xfovv__vhcgo}):\n'
        pjc__nuo += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        pjc__nuo += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        tfo__ovqzo = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        pjc__nuo += '  total_size = 0\n'
        tfo__ovqzo = (
            f'bodo.utils.conversion.convert_to_index({nzozo__fxtmm[1]}, {csv_iterator_type._index_name!r})'
            )
    pjc__nuo += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({nzozo__fxtmm[0]},), {tfo__ovqzo}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(pjc__nuo, {'bodo': bodo, 'objmode_func': lms__ykjh, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, tmkq__kry)
    return tmkq__kry['read_func']
