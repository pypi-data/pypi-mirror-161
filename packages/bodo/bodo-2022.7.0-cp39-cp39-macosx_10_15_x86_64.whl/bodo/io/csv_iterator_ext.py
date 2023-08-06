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
        akru__ycuv = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(akru__ycuv)
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
        dqc__nua = [('csv_reader', types.stream_reader_type), ('index',
            types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, dqc__nua)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    wlwej__xfqv = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    nwckl__mirmt = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer()])
    zcden__tyv = cgutils.get_or_insert_function(builder.module,
        nwckl__mirmt, name='initialize_csv_reader')
    cpa__mniqk = cgutils.create_struct_proxy(types.stream_reader_type)(context,
        builder, value=wlwej__xfqv.csv_reader)
    builder.call(zcden__tyv, [cpa__mniqk.pyobj])
    builder.store(context.get_constant(types.uint64, 0), wlwej__xfqv.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [ymc__ztuiy] = sig.args
    [dxxs__ker] = args
    wlwej__xfqv = cgutils.create_struct_proxy(ymc__ztuiy)(context, builder,
        value=dxxs__ker)
    nwckl__mirmt = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer()])
    zcden__tyv = cgutils.get_or_insert_function(builder.module,
        nwckl__mirmt, name='update_csv_reader')
    cpa__mniqk = cgutils.create_struct_proxy(types.stream_reader_type)(context,
        builder, value=wlwej__xfqv.csv_reader)
    ibi__npl = builder.call(zcden__tyv, [cpa__mniqk.pyobj])
    result.set_valid(ibi__npl)
    with builder.if_then(ibi__npl):
        zrvb__nvte = builder.load(wlwej__xfqv.index)
        rlydz__dir = types.Tuple([sig.return_type.first_type, types.int64])
        mhcz__qrw = gen_read_csv_objmode(sig.args[0])
        lxju__hwrlb = signature(rlydz__dir, types.stream_reader_type, types
            .int64)
        wds__dli = context.compile_internal(builder, mhcz__qrw, lxju__hwrlb,
            [wlwej__xfqv.csv_reader, zrvb__nvte])
        qpbs__gcfuu, srrf__slgea = cgutils.unpack_tuple(builder, wds__dli)
        emrzg__dbml = builder.add(zrvb__nvte, srrf__slgea, flags=['nsw'])
        builder.store(emrzg__dbml, wlwej__xfqv.index)
        result.yield_(qpbs__gcfuu)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        dnrd__jyj = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        context.nrt.incref(builder, signature.args[0], args[0])
        dnrd__jyj.csv_reader = args[0]
        zyzf__ijim = context.get_constant(types.uintp, 0)
        dnrd__jyj.index = cgutils.alloca_once_value(builder, zyzf__ijim)
        return dnrd__jyj._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    rnay__mraud = csv_iterator_typeref.instance_type
    sig = signature(rnay__mraud, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    mjv__ghut = 'def read_csv_objmode(f_reader):\n'
    otru__pmkh = [sanitize_varname(vqs__dwdsh) for vqs__dwdsh in
        csv_iterator_type._out_colnames]
    kzo__ajng = ir_utils.next_label()
    dwhq__erg = globals()
    out_types = csv_iterator_type._out_types
    dwhq__erg[f'table_type_{kzo__ajng}'] = TableType(tuple(out_types))
    dwhq__erg[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    vvjun__vlo = list(range(len(csv_iterator_type._usecols)))
    mjv__ghut += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        otru__pmkh, out_types, csv_iterator_type._usecols, vvjun__vlo,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, kzo__ajng, dwhq__erg, parallel=
        False, check_parallel_runtime=True, idx_col_index=csv_iterator_type
        ._index_ind, idx_col_typ=csv_iterator_type._index_arr_typ)
    ooep__nnueu = bodo.ir.csv_ext._gen_parallel_flag_name(otru__pmkh)
    zjvp__ezc = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [ooep__nnueu]
    mjv__ghut += f"  return {', '.join(zjvp__ezc)}"
    dwhq__erg = globals()
    xadwi__iqmw = {}
    exec(mjv__ghut, dwhq__erg, xadwi__iqmw)
    cxz__tdt = xadwi__iqmw['read_csv_objmode']
    tuop__pmpzz = numba.njit(cxz__tdt)
    bodo.ir.csv_ext.compiled_funcs.append(tuop__pmpzz)
    jig__xblvh = 'def read_func(reader, local_start):\n'
    jig__xblvh += f"  {', '.join(zjvp__ezc)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        jig__xblvh += f'  local_len = len(T)\n'
        jig__xblvh += '  total_size = local_len\n'
        jig__xblvh += f'  if ({ooep__nnueu}):\n'
        jig__xblvh += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        jig__xblvh += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        fva__jojx = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        jig__xblvh += '  total_size = 0\n'
        fva__jojx = (
            f'bodo.utils.conversion.convert_to_index({zjvp__ezc[1]}, {csv_iterator_type._index_name!r})'
            )
    jig__xblvh += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({zjvp__ezc[0]},), {fva__jojx}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(jig__xblvh, {'bodo': bodo, 'objmode_func': tuop__pmpzz, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, xadwi__iqmw)
    return xadwi__iqmw['read_func']
