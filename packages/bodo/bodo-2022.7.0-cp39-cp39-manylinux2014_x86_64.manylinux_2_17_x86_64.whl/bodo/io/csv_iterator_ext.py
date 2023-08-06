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
        mlrl__ykp = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(mlrl__ykp)
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
        dbbp__ngjf = [('csv_reader', types.stream_reader_type), ('index',
            types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, dbbp__ngjf)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    jnuw__owgzf = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    ysts__oznh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer()]
        )
    bocqb__mbxvh = cgutils.get_or_insert_function(builder.module,
        ysts__oznh, name='initialize_csv_reader')
    bxnx__vcwcb = cgutils.create_struct_proxy(types.stream_reader_type)(context
        , builder, value=jnuw__owgzf.csv_reader)
    builder.call(bocqb__mbxvh, [bxnx__vcwcb.pyobj])
    builder.store(context.get_constant(types.uint64, 0), jnuw__owgzf.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [rnd__qzcb] = sig.args
    [iyhau__kinr] = args
    jnuw__owgzf = cgutils.create_struct_proxy(rnd__qzcb)(context, builder,
        value=iyhau__kinr)
    ysts__oznh = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer()]
        )
    bocqb__mbxvh = cgutils.get_or_insert_function(builder.module,
        ysts__oznh, name='update_csv_reader')
    bxnx__vcwcb = cgutils.create_struct_proxy(types.stream_reader_type)(context
        , builder, value=jnuw__owgzf.csv_reader)
    evxha__wuxbq = builder.call(bocqb__mbxvh, [bxnx__vcwcb.pyobj])
    result.set_valid(evxha__wuxbq)
    with builder.if_then(evxha__wuxbq):
        zqi__sum = builder.load(jnuw__owgzf.index)
        bghz__oprr = types.Tuple([sig.return_type.first_type, types.int64])
        kufn__vfs = gen_read_csv_objmode(sig.args[0])
        gmyve__meqe = signature(bghz__oprr, types.stream_reader_type, types
            .int64)
        bszbx__savhx = context.compile_internal(builder, kufn__vfs,
            gmyve__meqe, [jnuw__owgzf.csv_reader, zqi__sum])
        seu__lgxm, dfln__qzyb = cgutils.unpack_tuple(builder, bszbx__savhx)
        waniv__cgrq = builder.add(zqi__sum, dfln__qzyb, flags=['nsw'])
        builder.store(waniv__cgrq, jnuw__owgzf.index)
        result.yield_(seu__lgxm)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        oam__zlv = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        context.nrt.incref(builder, signature.args[0], args[0])
        oam__zlv.csv_reader = args[0]
        rqye__ual = context.get_constant(types.uintp, 0)
        oam__zlv.index = cgutils.alloca_once_value(builder, rqye__ual)
        return oam__zlv._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    zosb__adtpp = csv_iterator_typeref.instance_type
    sig = signature(zosb__adtpp, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    ltwzq__japz = 'def read_csv_objmode(f_reader):\n'
    eqii__gimv = [sanitize_varname(igjjx__gcen) for igjjx__gcen in
        csv_iterator_type._out_colnames]
    khov__xfb = ir_utils.next_label()
    zgk__wsoy = globals()
    out_types = csv_iterator_type._out_types
    zgk__wsoy[f'table_type_{khov__xfb}'] = TableType(tuple(out_types))
    zgk__wsoy[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    xvqb__jcnn = list(range(len(csv_iterator_type._usecols)))
    ltwzq__japz += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        eqii__gimv, out_types, csv_iterator_type._usecols, xvqb__jcnn,
        csv_iterator_type._sep, csv_iterator_type._escapechar,
        csv_iterator_type._storage_options, khov__xfb, zgk__wsoy, parallel=
        False, check_parallel_runtime=True, idx_col_index=csv_iterator_type
        ._index_ind, idx_col_typ=csv_iterator_type._index_arr_typ)
    tqsx__xwqnh = bodo.ir.csv_ext._gen_parallel_flag_name(eqii__gimv)
    til__bzco = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [tqsx__xwqnh]
    ltwzq__japz += f"  return {', '.join(til__bzco)}"
    zgk__wsoy = globals()
    zek__wkj = {}
    exec(ltwzq__japz, zgk__wsoy, zek__wkj)
    rqqq__wjrty = zek__wkj['read_csv_objmode']
    armm__qpixw = numba.njit(rqqq__wjrty)
    bodo.ir.csv_ext.compiled_funcs.append(armm__qpixw)
    yxamq__uiuch = 'def read_func(reader, local_start):\n'
    yxamq__uiuch += f"  {', '.join(til__bzco)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        yxamq__uiuch += f'  local_len = len(T)\n'
        yxamq__uiuch += '  total_size = local_len\n'
        yxamq__uiuch += f'  if ({tqsx__xwqnh}):\n'
        yxamq__uiuch += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        yxamq__uiuch += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        nir__agkis = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        yxamq__uiuch += '  total_size = 0\n'
        nir__agkis = (
            f'bodo.utils.conversion.convert_to_index({til__bzco[1]}, {csv_iterator_type._index_name!r})'
            )
    yxamq__uiuch += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({til__bzco[0]},), {nir__agkis}, __col_name_meta_value_read_csv_objmode), total_size)
"""
    exec(yxamq__uiuch, {'bodo': bodo, 'objmode_func': armm__qpixw, '_op':
        np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        '__col_name_meta_value_read_csv_objmode': ColNamesMetaType(
        csv_iterator_type.yield_type.columns)}, zek__wkj)
    return zek__wkj['read_func']
