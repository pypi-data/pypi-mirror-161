"""Tools for handling bodo arrays, e.g. passing to C/C++ code
"""
from collections import defaultdict
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import intrinsic, models, register_model
from numba.np.arrayobj import _getitem_array_single_int
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, get_categories_int_type
from bodo.libs import array_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, define_array_item_dtor, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType, int128_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType, _get_map_arr_data_type, init_map_arr_codegen
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, char_arr_type, null_bitmap_arr_type, offset_arr_type, string_array_type
from bodo.libs.struct_arr_ext import StructArrayPayloadType, StructArrayType, StructType, _get_struct_arr_payload, define_struct_arr_dtor
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, get_overload_const_int, is_overload_none, is_str_arr_type, raise_bodo_error, type_has_unknown_cats, unwrap_typeref
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, numba_to_c_type
ll.add_symbol('list_string_array_to_info', array_ext.list_string_array_to_info)
ll.add_symbol('nested_array_to_info', array_ext.nested_array_to_info)
ll.add_symbol('string_array_to_info', array_ext.string_array_to_info)
ll.add_symbol('dict_str_array_to_info', array_ext.dict_str_array_to_info)
ll.add_symbol('get_nested_info', array_ext.get_nested_info)
ll.add_symbol('get_has_global_dictionary', array_ext.get_has_global_dictionary)
ll.add_symbol('numpy_array_to_info', array_ext.numpy_array_to_info)
ll.add_symbol('categorical_array_to_info', array_ext.categorical_array_to_info)
ll.add_symbol('nullable_array_to_info', array_ext.nullable_array_to_info)
ll.add_symbol('interval_array_to_info', array_ext.interval_array_to_info)
ll.add_symbol('decimal_array_to_info', array_ext.decimal_array_to_info)
ll.add_symbol('info_to_nested_array', array_ext.info_to_nested_array)
ll.add_symbol('info_to_list_string_array', array_ext.info_to_list_string_array)
ll.add_symbol('info_to_string_array', array_ext.info_to_string_array)
ll.add_symbol('info_to_numpy_array', array_ext.info_to_numpy_array)
ll.add_symbol('info_to_nullable_array', array_ext.info_to_nullable_array)
ll.add_symbol('info_to_interval_array', array_ext.info_to_interval_array)
ll.add_symbol('alloc_numpy', array_ext.alloc_numpy)
ll.add_symbol('alloc_string_array', array_ext.alloc_string_array)
ll.add_symbol('arr_info_list_to_table', array_ext.arr_info_list_to_table)
ll.add_symbol('info_from_table', array_ext.info_from_table)
ll.add_symbol('delete_info_decref_array', array_ext.delete_info_decref_array)
ll.add_symbol('delete_table_decref_arrays', array_ext.
    delete_table_decref_arrays)
ll.add_symbol('decref_table_array', array_ext.decref_table_array)
ll.add_symbol('delete_table', array_ext.delete_table)
ll.add_symbol('shuffle_table', array_ext.shuffle_table)
ll.add_symbol('get_shuffle_info', array_ext.get_shuffle_info)
ll.add_symbol('delete_shuffle_info', array_ext.delete_shuffle_info)
ll.add_symbol('reverse_shuffle_table', array_ext.reverse_shuffle_table)
ll.add_symbol('hash_join_table', array_ext.hash_join_table)
ll.add_symbol('drop_duplicates_table', array_ext.drop_duplicates_table)
ll.add_symbol('sort_values_table', array_ext.sort_values_table)
ll.add_symbol('sample_table', array_ext.sample_table)
ll.add_symbol('shuffle_renormalization', array_ext.shuffle_renormalization)
ll.add_symbol('shuffle_renormalization_group', array_ext.
    shuffle_renormalization_group)
ll.add_symbol('groupby_and_aggregate', array_ext.groupby_and_aggregate)
ll.add_symbol('get_groupby_labels', array_ext.get_groupby_labels)
ll.add_symbol('array_isin', array_ext.array_isin)
ll.add_symbol('get_search_regex', array_ext.get_search_regex)
ll.add_symbol('array_info_getitem', array_ext.array_info_getitem)
ll.add_symbol('array_info_getdata1', array_ext.array_info_getdata1)


class ArrayInfoType(types.Type):

    def __init__(self):
        super(ArrayInfoType, self).__init__(name='ArrayInfoType()')


array_info_type = ArrayInfoType()
register_model(ArrayInfoType)(models.OpaqueModel)


class TableTypeCPP(types.Type):

    def __init__(self):
        super(TableTypeCPP, self).__init__(name='TableTypeCPP()')


table_type = TableTypeCPP()
register_model(TableTypeCPP)(models.OpaqueModel)


@intrinsic
def array_to_info(typingctx, arr_type_t=None):
    return array_info_type(arr_type_t), array_to_info_codegen


def array_to_info_codegen(context, builder, sig, args, incref=True):
    in_arr, = args
    arr_type = sig.args[0]
    if incref:
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, TupleArrayType):
        rbbt__qze = context.make_helper(builder, arr_type, in_arr)
        in_arr = rbbt__qze.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        dcv__hpmij = context.make_helper(builder, arr_type, in_arr)
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='list_string_array_to_info')
        return builder.call(cspms__ezn, [dcv__hpmij.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                qiu__kyahq = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for jkqnj__mboh in arr_typ.data:
                    qiu__kyahq += get_types(jkqnj__mboh)
                return qiu__kyahq
            elif isinstance(arr_typ, (types.Array, IntegerArrayType)
                ) or arr_typ == boolean_array:
                return get_types(arr_typ.dtype)
            elif arr_typ == string_array_type:
                return [CTypeEnum.STRING.value]
            elif arr_typ == binary_array_type:
                return [CTypeEnum.BINARY.value]
            elif isinstance(arr_typ, DecimalArrayType):
                return [CTypeEnum.Decimal.value, arr_typ.precision, arr_typ
                    .scale]
            else:
                return [numba_to_c_type(arr_typ)]

        def get_lengths(arr_typ, arr):
            dvf__rnzz = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                qscy__xsdy = context.make_helper(builder, arr_typ, value=arr)
                eagb__gsguy = get_lengths(_get_map_arr_data_type(arr_typ),
                    qscy__xsdy.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ins__jhbrq = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                eagb__gsguy = get_lengths(arr_typ.dtype, ins__jhbrq.data)
                eagb__gsguy = cgutils.pack_array(builder, [ins__jhbrq.
                    n_arrays] + [builder.extract_value(eagb__gsguy,
                    zjn__wpl) for zjn__wpl in range(eagb__gsguy.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                ins__jhbrq = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                eagb__gsguy = []
                for zjn__wpl, jkqnj__mboh in enumerate(arr_typ.data):
                    ikok__vbct = get_lengths(jkqnj__mboh, builder.
                        extract_value(ins__jhbrq.data, zjn__wpl))
                    eagb__gsguy += [builder.extract_value(ikok__vbct,
                        rpgj__xyzsi) for rpgj__xyzsi in range(ikok__vbct.
                        type.count)]
                eagb__gsguy = cgutils.pack_array(builder, [dvf__rnzz,
                    context.get_constant(types.int64, -1)] + eagb__gsguy)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                eagb__gsguy = cgutils.pack_array(builder, [dvf__rnzz])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return eagb__gsguy

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                qscy__xsdy = context.make_helper(builder, arr_typ, value=arr)
                ahjpg__duxm = get_buffers(_get_map_arr_data_type(arr_typ),
                    qscy__xsdy.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ins__jhbrq = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                dvvs__dxu = get_buffers(arr_typ.dtype, ins__jhbrq.data)
                yhqb__qof = context.make_array(types.Array(offset_type, 1, 'C')
                    )(context, builder, ins__jhbrq.offsets)
                tbtaw__smnc = builder.bitcast(yhqb__qof.data, lir.IntType(8
                    ).as_pointer())
                gwxn__oel = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, ins__jhbrq.null_bitmap)
                cwfe__qup = builder.bitcast(gwxn__oel.data, lir.IntType(8).
                    as_pointer())
                ahjpg__duxm = cgutils.pack_array(builder, [tbtaw__smnc,
                    cwfe__qup] + [builder.extract_value(dvvs__dxu, zjn__wpl
                    ) for zjn__wpl in range(dvvs__dxu.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                ins__jhbrq = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                dvvs__dxu = []
                for zjn__wpl, jkqnj__mboh in enumerate(arr_typ.data):
                    vczsp__cxkj = get_buffers(jkqnj__mboh, builder.
                        extract_value(ins__jhbrq.data, zjn__wpl))
                    dvvs__dxu += [builder.extract_value(vczsp__cxkj,
                        rpgj__xyzsi) for rpgj__xyzsi in range(vczsp__cxkj.
                        type.count)]
                gwxn__oel = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, ins__jhbrq.null_bitmap)
                cwfe__qup = builder.bitcast(gwxn__oel.data, lir.IntType(8).
                    as_pointer())
                ahjpg__duxm = cgutils.pack_array(builder, [cwfe__qup] +
                    dvvs__dxu)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                cmyfb__wpdj = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    cmyfb__wpdj = int128_type
                elif arr_typ == datetime_date_array_type:
                    cmyfb__wpdj = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                yyg__bohca = context.make_array(types.Array(cmyfb__wpdj, 1,
                    'C'))(context, builder, arr.data)
                gwxn__oel = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, arr.null_bitmap)
                oxhi__hbb = builder.bitcast(yyg__bohca.data, lir.IntType(8)
                    .as_pointer())
                cwfe__qup = builder.bitcast(gwxn__oel.data, lir.IntType(8).
                    as_pointer())
                ahjpg__duxm = cgutils.pack_array(builder, [cwfe__qup,
                    oxhi__hbb])
            elif arr_typ in (string_array_type, binary_array_type):
                ins__jhbrq = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                tsssx__tkt = context.make_helper(builder, offset_arr_type,
                    ins__jhbrq.offsets).data
                zsao__mkla = context.make_helper(builder, char_arr_type,
                    ins__jhbrq.data).data
                ikgz__siwg = context.make_helper(builder,
                    null_bitmap_arr_type, ins__jhbrq.null_bitmap).data
                ahjpg__duxm = cgutils.pack_array(builder, [builder.bitcast(
                    tsssx__tkt, lir.IntType(8).as_pointer()), builder.
                    bitcast(ikgz__siwg, lir.IntType(8).as_pointer()),
                    builder.bitcast(zsao__mkla, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                oxhi__hbb = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                ubehn__cgsu = lir.Constant(lir.IntType(8).as_pointer(), None)
                ahjpg__duxm = cgutils.pack_array(builder, [ubehn__cgsu,
                    oxhi__hbb])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return ahjpg__duxm

        def get_field_names(arr_typ):
            ngeq__zfll = []
            if isinstance(arr_typ, StructArrayType):
                for raca__vncl, osy__jksl in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    ngeq__zfll.append(raca__vncl)
                    ngeq__zfll += get_field_names(osy__jksl)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ngeq__zfll += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                ngeq__zfll += get_field_names(_get_map_arr_data_type(arr_typ))
            return ngeq__zfll
        qiu__kyahq = get_types(arr_type)
        zus__qnrq = cgutils.pack_array(builder, [context.get_constant(types
            .int32, t) for t in qiu__kyahq])
        nkxpk__wtb = cgutils.alloca_once_value(builder, zus__qnrq)
        eagb__gsguy = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, eagb__gsguy)
        ahjpg__duxm = get_buffers(arr_type, in_arr)
        lhh__nmvd = cgutils.alloca_once_value(builder, ahjpg__duxm)
        ngeq__zfll = get_field_names(arr_type)
        if len(ngeq__zfll) == 0:
            ngeq__zfll = ['irrelevant']
        qsf__tttw = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in ngeq__zfll])
        xqs__udixo = cgutils.alloca_once_value(builder, qsf__tttw)
        if isinstance(arr_type, MapArrayType):
            ttoow__oygwy = _get_map_arr_data_type(arr_type)
            vmtq__dqiq = context.make_helper(builder, arr_type, value=in_arr)
            tpxt__qyfvx = vmtq__dqiq.data
        else:
            ttoow__oygwy = arr_type
            tpxt__qyfvx = in_arr
        uhkop__wytq = context.make_helper(builder, ttoow__oygwy, tpxt__qyfvx)
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='nested_array_to_info')
        nscf__cgqyq = builder.call(cspms__ezn, [builder.bitcast(nkxpk__wtb,
            lir.IntType(32).as_pointer()), builder.bitcast(lhh__nmvd, lir.
            IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            xqs__udixo, lir.IntType(8).as_pointer()), uhkop__wytq.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return nscf__cgqyq
    if arr_type in (string_array_type, binary_array_type):
        clug__plepl = context.make_helper(builder, arr_type, in_arr)
        hquv__ewih = ArrayItemArrayType(char_arr_type)
        dcv__hpmij = context.make_helper(builder, hquv__ewih, clug__plepl.data)
        ins__jhbrq = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        tsssx__tkt = context.make_helper(builder, offset_arr_type,
            ins__jhbrq.offsets).data
        zsao__mkla = context.make_helper(builder, char_arr_type, ins__jhbrq
            .data).data
        ikgz__siwg = context.make_helper(builder, null_bitmap_arr_type,
            ins__jhbrq.null_bitmap).data
        pgk__xhhcw = builder.zext(builder.load(builder.gep(tsssx__tkt, [
            ins__jhbrq.n_arrays])), lir.IntType(64))
        zdwd__rdn = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='string_array_to_info')
        return builder.call(cspms__ezn, [ins__jhbrq.n_arrays, pgk__xhhcw,
            zsao__mkla, tsssx__tkt, ikgz__siwg, dcv__hpmij.meminfo, zdwd__rdn])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        lew__yvt = arr.data
        vxgv__fufp = arr.indices
        sig = array_info_type(arr_type.data)
        mlz__fkfj = array_to_info_codegen(context, builder, sig, (lew__yvt,
            ), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        mxnef__wgraf = array_to_info_codegen(context, builder, sig, (
            vxgv__fufp,), False)
        awu__bgcc = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, vxgv__fufp)
        cwfe__qup = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, awu__bgcc.null_bitmap).data
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='dict_str_array_to_info')
        qte__klyt = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(cspms__ezn, [mlz__fkfj, mxnef__wgraf, builder.
            bitcast(cwfe__qup, lir.IntType(8).as_pointer()), qte__klyt])
    ulfg__nfuud = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        uwerp__dcfw = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        xusis__vzwg = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(xusis__vzwg, 1, 'C')
        ulfg__nfuud = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if ulfg__nfuud:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        dvf__rnzz = builder.extract_value(arr.shape, 0)
        wmyrz__jag = arr_type.dtype
        zde__ypfg = numba_to_c_type(wmyrz__jag)
        timxg__uriov = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), zde__ypfg))
        if ulfg__nfuud:
            lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            cspms__ezn = cgutils.get_or_insert_function(builder.module,
                lklj__zmzr, name='categorical_array_to_info')
            return builder.call(cspms__ezn, [dvf__rnzz, builder.bitcast(arr
                .data, lir.IntType(8).as_pointer()), builder.load(
                timxg__uriov), uwerp__dcfw, arr.meminfo])
        else:
            lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            cspms__ezn = cgutils.get_or_insert_function(builder.module,
                lklj__zmzr, name='numpy_array_to_info')
            return builder.call(cspms__ezn, [dvf__rnzz, builder.bitcast(arr
                .data, lir.IntType(8).as_pointer()), builder.load(
                timxg__uriov), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        wmyrz__jag = arr_type.dtype
        cmyfb__wpdj = wmyrz__jag
        if isinstance(arr_type, DecimalArrayType):
            cmyfb__wpdj = int128_type
        if arr_type == datetime_date_array_type:
            cmyfb__wpdj = types.int64
        yyg__bohca = context.make_array(types.Array(cmyfb__wpdj, 1, 'C'))(
            context, builder, arr.data)
        dvf__rnzz = builder.extract_value(yyg__bohca.shape, 0)
        yixdg__rqauf = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        zde__ypfg = numba_to_c_type(wmyrz__jag)
        timxg__uriov = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), zde__ypfg))
        if isinstance(arr_type, DecimalArrayType):
            lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            cspms__ezn = cgutils.get_or_insert_function(builder.module,
                lklj__zmzr, name='decimal_array_to_info')
            return builder.call(cspms__ezn, [dvf__rnzz, builder.bitcast(
                yyg__bohca.data, lir.IntType(8).as_pointer()), builder.load
                (timxg__uriov), builder.bitcast(yixdg__rqauf.data, lir.
                IntType(8).as_pointer()), yyg__bohca.meminfo, yixdg__rqauf.
                meminfo, context.get_constant(types.int32, arr_type.
                precision), context.get_constant(types.int32, arr_type.scale)])
        else:
            lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            cspms__ezn = cgutils.get_or_insert_function(builder.module,
                lklj__zmzr, name='nullable_array_to_info')
            return builder.call(cspms__ezn, [dvf__rnzz, builder.bitcast(
                yyg__bohca.data, lir.IntType(8).as_pointer()), builder.load
                (timxg__uriov), builder.bitcast(yixdg__rqauf.data, lir.
                IntType(8).as_pointer()), yyg__bohca.meminfo, yixdg__rqauf.
                meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        yxzbf__pmf = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        kkpg__iiio = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        dvf__rnzz = builder.extract_value(yxzbf__pmf.shape, 0)
        zde__ypfg = numba_to_c_type(arr_type.arr_type.dtype)
        timxg__uriov = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), zde__ypfg))
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='interval_array_to_info')
        return builder.call(cspms__ezn, [dvf__rnzz, builder.bitcast(
            yxzbf__pmf.data, lir.IntType(8).as_pointer()), builder.bitcast(
            kkpg__iiio.data, lir.IntType(8).as_pointer()), builder.load(
            timxg__uriov), yxzbf__pmf.meminfo, kkpg__iiio.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    vzyd__inwjx = cgutils.alloca_once(builder, lir.IntType(64))
    oxhi__hbb = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    xxykl__wlxh = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    lklj__zmzr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    cspms__ezn = cgutils.get_or_insert_function(builder.module, lklj__zmzr,
        name='info_to_numpy_array')
    builder.call(cspms__ezn, [in_info, vzyd__inwjx, oxhi__hbb, xxykl__wlxh])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    bls__ateip = context.get_value_type(types.intp)
    yxnt__utty = cgutils.pack_array(builder, [builder.load(vzyd__inwjx)],
        ty=bls__ateip)
    twaqn__grvbm = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    yjvqx__mjft = cgutils.pack_array(builder, [twaqn__grvbm], ty=bls__ateip)
    zsao__mkla = builder.bitcast(builder.load(oxhi__hbb), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=zsao__mkla, shape=yxnt__utty,
        strides=yjvqx__mjft, itemsize=twaqn__grvbm, meminfo=builder.load(
        xxykl__wlxh))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    bmvq__vwf = context.make_helper(builder, arr_type)
    lklj__zmzr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    cspms__ezn = cgutils.get_or_insert_function(builder.module, lklj__zmzr,
        name='info_to_list_string_array')
    builder.call(cspms__ezn, [in_info, bmvq__vwf._get_ptr_by_name('meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return bmvq__vwf._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    xhdez__iyyd = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        ctic__capx = lengths_pos
        ity__yjylk = infos_pos
        wlw__ffgsw, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        wmfte__fnl = ArrayItemArrayPayloadType(arr_typ)
        gsnls__flb = context.get_data_type(wmfte__fnl)
        fdu__cvub = context.get_abi_sizeof(gsnls__flb)
        asmn__iho = define_array_item_dtor(context, builder, arr_typ,
            wmfte__fnl)
        awm__aaq = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, fdu__cvub), asmn__iho)
        oyua__gxl = context.nrt.meminfo_data(builder, awm__aaq)
        gqdc__gfgjz = builder.bitcast(oyua__gxl, gsnls__flb.as_pointer())
        ins__jhbrq = cgutils.create_struct_proxy(wmfte__fnl)(context, builder)
        ins__jhbrq.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), ctic__capx)
        ins__jhbrq.data = wlw__ffgsw
        pemyg__xegtc = builder.load(array_infos_ptr)
        gbsov__wkwn = builder.bitcast(builder.extract_value(pemyg__xegtc,
            ity__yjylk), xhdez__iyyd)
        ins__jhbrq.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, gbsov__wkwn)
        ejlp__thtat = builder.bitcast(builder.extract_value(pemyg__xegtc, 
            ity__yjylk + 1), xhdez__iyyd)
        ins__jhbrq.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, ejlp__thtat)
        builder.store(ins__jhbrq._getvalue(), gqdc__gfgjz)
        dcv__hpmij = context.make_helper(builder, arr_typ)
        dcv__hpmij.meminfo = awm__aaq
        return dcv__hpmij._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        pbpw__mqs = []
        ity__yjylk = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for qmpd__hzvtv in arr_typ.data:
            wlw__ffgsw, lengths_pos, infos_pos = nested_to_array(context,
                builder, qmpd__hzvtv, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            pbpw__mqs.append(wlw__ffgsw)
        wmfte__fnl = StructArrayPayloadType(arr_typ.data)
        gsnls__flb = context.get_value_type(wmfte__fnl)
        fdu__cvub = context.get_abi_sizeof(gsnls__flb)
        asmn__iho = define_struct_arr_dtor(context, builder, arr_typ,
            wmfte__fnl)
        awm__aaq = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, fdu__cvub), asmn__iho)
        oyua__gxl = context.nrt.meminfo_data(builder, awm__aaq)
        gqdc__gfgjz = builder.bitcast(oyua__gxl, gsnls__flb.as_pointer())
        ins__jhbrq = cgutils.create_struct_proxy(wmfte__fnl)(context, builder)
        ins__jhbrq.data = cgutils.pack_array(builder, pbpw__mqs
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, pbpw__mqs)
        pemyg__xegtc = builder.load(array_infos_ptr)
        ejlp__thtat = builder.bitcast(builder.extract_value(pemyg__xegtc,
            ity__yjylk), xhdez__iyyd)
        ins__jhbrq.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, ejlp__thtat)
        builder.store(ins__jhbrq._getvalue(), gqdc__gfgjz)
        okx__obitx = context.make_helper(builder, arr_typ)
        okx__obitx.meminfo = awm__aaq
        return okx__obitx._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        pemyg__xegtc = builder.load(array_infos_ptr)
        vdbmz__zhvt = builder.bitcast(builder.extract_value(pemyg__xegtc,
            infos_pos), xhdez__iyyd)
        clug__plepl = context.make_helper(builder, arr_typ)
        hquv__ewih = ArrayItemArrayType(char_arr_type)
        dcv__hpmij = context.make_helper(builder, hquv__ewih)
        lklj__zmzr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='info_to_string_array')
        builder.call(cspms__ezn, [vdbmz__zhvt, dcv__hpmij._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        clug__plepl.data = dcv__hpmij._getvalue()
        return clug__plepl._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        pemyg__xegtc = builder.load(array_infos_ptr)
        fui__wblfx = builder.bitcast(builder.extract_value(pemyg__xegtc, 
            infos_pos + 1), xhdez__iyyd)
        return _lower_info_to_array_numpy(arr_typ, context, builder, fui__wblfx
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        cmyfb__wpdj = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            cmyfb__wpdj = int128_type
        elif arr_typ == datetime_date_array_type:
            cmyfb__wpdj = types.int64
        pemyg__xegtc = builder.load(array_infos_ptr)
        ejlp__thtat = builder.bitcast(builder.extract_value(pemyg__xegtc,
            infos_pos), xhdez__iyyd)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, ejlp__thtat)
        fui__wblfx = builder.bitcast(builder.extract_value(pemyg__xegtc, 
            infos_pos + 1), xhdez__iyyd)
        arr.data = _lower_info_to_array_numpy(types.Array(cmyfb__wpdj, 1,
            'C'), context, builder, fui__wblfx)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, vzodi__blsn = args
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        return _lower_info_to_array_list_string_array(arr_type, context,
            builder, in_info)
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType,
        StructArrayType, TupleArrayType)):

        def get_num_arrays(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 1 + get_num_arrays(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_arrays(qmpd__hzvtv) for qmpd__hzvtv in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(qmpd__hzvtv) for qmpd__hzvtv in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            pfke__kdk = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            pfke__kdk = _get_map_arr_data_type(arr_type)
        else:
            pfke__kdk = arr_type
        jefau__hfqjn = get_num_arrays(pfke__kdk)
        eagb__gsguy = cgutils.pack_array(builder, [lir.Constant(lir.IntType
            (64), 0) for vzodi__blsn in range(jefau__hfqjn)])
        lengths_ptr = cgutils.alloca_once_value(builder, eagb__gsguy)
        ubehn__cgsu = lir.Constant(lir.IntType(8).as_pointer(), None)
        epm__mgj = cgutils.pack_array(builder, [ubehn__cgsu for vzodi__blsn in
            range(get_num_infos(pfke__kdk))])
        array_infos_ptr = cgutils.alloca_once_value(builder, epm__mgj)
        lklj__zmzr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='info_to_nested_array')
        builder.call(cspms__ezn, [in_info, builder.bitcast(lengths_ptr, lir
            .IntType(64).as_pointer()), builder.bitcast(array_infos_ptr,
            lir.IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, vzodi__blsn, vzodi__blsn = nested_to_array(context, builder,
            pfke__kdk, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            rbbt__qze = context.make_helper(builder, arr_type)
            rbbt__qze.data = arr
            context.nrt.incref(builder, pfke__kdk, arr)
            arr = rbbt__qze._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, pfke__kdk)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        clug__plepl = context.make_helper(builder, arr_type)
        hquv__ewih = ArrayItemArrayType(char_arr_type)
        dcv__hpmij = context.make_helper(builder, hquv__ewih)
        lklj__zmzr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='info_to_string_array')
        builder.call(cspms__ezn, [in_info, dcv__hpmij._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        clug__plepl.data = dcv__hpmij._getvalue()
        return clug__plepl._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='get_nested_info')
        mlz__fkfj = builder.call(cspms__ezn, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        mxnef__wgraf = builder.call(cspms__ezn, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        spi__dyl = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        spi__dyl.data = info_to_array_codegen(context, builder, sig, (
            mlz__fkfj, context.get_constant_null(arr_type.data)))
        tzx__hkp = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = tzx__hkp(array_info_type, tzx__hkp)
        spi__dyl.indices = info_to_array_codegen(context, builder, sig, (
            mxnef__wgraf, context.get_constant_null(tzx__hkp)))
        lklj__zmzr = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='get_has_global_dictionary')
        qte__klyt = builder.call(cspms__ezn, [in_info])
        spi__dyl.has_global_dictionary = builder.trunc(qte__klyt, cgutils.
            bool_t)
        return spi__dyl._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        xusis__vzwg = get_categories_int_type(arr_type.dtype)
        xxaxv__lil = types.Array(xusis__vzwg, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(xxaxv__lil, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            engz__ezl = bodo.utils.utils.create_categorical_type(arr_type.
                dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(engz__ezl))
            int_type = arr_type.dtype.int_type
            ppu__jfx = arr_type.dtype.data.data
            mff__qpxil = context.get_constant_generic(builder, ppu__jfx,
                engz__ezl)
            wmyrz__jag = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(ppu__jfx), [mff__qpxil])
        else:
            wmyrz__jag = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, wmyrz__jag)
        out_arr.dtype = wmyrz__jag
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        zsao__mkla = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = zsao__mkla
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        cmyfb__wpdj = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            cmyfb__wpdj = int128_type
        elif arr_type == datetime_date_array_type:
            cmyfb__wpdj = types.int64
        vxtng__qye = types.Array(cmyfb__wpdj, 1, 'C')
        yyg__bohca = context.make_array(vxtng__qye)(context, builder)
        kle__nkpp = types.Array(types.uint8, 1, 'C')
        ean__gegu = context.make_array(kle__nkpp)(context, builder)
        vzyd__inwjx = cgutils.alloca_once(builder, lir.IntType(64))
        iyr__shn = cgutils.alloca_once(builder, lir.IntType(64))
        oxhi__hbb = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        ahwq__ntkcg = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        xxykl__wlxh = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        miwaf__rfck = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        lklj__zmzr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='info_to_nullable_array')
        builder.call(cspms__ezn, [in_info, vzyd__inwjx, iyr__shn, oxhi__hbb,
            ahwq__ntkcg, xxykl__wlxh, miwaf__rfck])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        bls__ateip = context.get_value_type(types.intp)
        yxnt__utty = cgutils.pack_array(builder, [builder.load(vzyd__inwjx)
            ], ty=bls__ateip)
        twaqn__grvbm = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(cmyfb__wpdj)))
        yjvqx__mjft = cgutils.pack_array(builder, [twaqn__grvbm], ty=bls__ateip
            )
        zsao__mkla = builder.bitcast(builder.load(oxhi__hbb), context.
            get_data_type(cmyfb__wpdj).as_pointer())
        numba.np.arrayobj.populate_array(yyg__bohca, data=zsao__mkla, shape
            =yxnt__utty, strides=yjvqx__mjft, itemsize=twaqn__grvbm,
            meminfo=builder.load(xxykl__wlxh))
        arr.data = yyg__bohca._getvalue()
        yxnt__utty = cgutils.pack_array(builder, [builder.load(iyr__shn)],
            ty=bls__ateip)
        twaqn__grvbm = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(types.uint8)))
        yjvqx__mjft = cgutils.pack_array(builder, [twaqn__grvbm], ty=bls__ateip
            )
        zsao__mkla = builder.bitcast(builder.load(ahwq__ntkcg), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(ean__gegu, data=zsao__mkla, shape=
            yxnt__utty, strides=yjvqx__mjft, itemsize=twaqn__grvbm, meminfo
            =builder.load(miwaf__rfck))
        arr.null_bitmap = ean__gegu._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        yxzbf__pmf = context.make_array(arr_type.arr_type)(context, builder)
        kkpg__iiio = context.make_array(arr_type.arr_type)(context, builder)
        vzyd__inwjx = cgutils.alloca_once(builder, lir.IntType(64))
        npjsq__nfma = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        slm__uhs = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        ovo__sik = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        disv__rodyu = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        lklj__zmzr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='info_to_interval_array')
        builder.call(cspms__ezn, [in_info, vzyd__inwjx, npjsq__nfma,
            slm__uhs, ovo__sik, disv__rodyu])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        bls__ateip = context.get_value_type(types.intp)
        yxnt__utty = cgutils.pack_array(builder, [builder.load(vzyd__inwjx)
            ], ty=bls__ateip)
        twaqn__grvbm = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
        yjvqx__mjft = cgutils.pack_array(builder, [twaqn__grvbm], ty=bls__ateip
            )
        mkuwu__rykv = builder.bitcast(builder.load(npjsq__nfma), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(yxzbf__pmf, data=mkuwu__rykv,
            shape=yxnt__utty, strides=yjvqx__mjft, itemsize=twaqn__grvbm,
            meminfo=builder.load(ovo__sik))
        arr.left = yxzbf__pmf._getvalue()
        ugbb__snshv = builder.bitcast(builder.load(slm__uhs), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(kkpg__iiio, data=ugbb__snshv,
            shape=yxnt__utty, strides=yjvqx__mjft, itemsize=twaqn__grvbm,
            meminfo=builder.load(disv__rodyu))
        arr.right = kkpg__iiio._getvalue()
        return arr._getvalue()
    raise_bodo_error(f'info_to_array(): array type {arr_type} is not supported'
        )


@intrinsic
def info_to_array(typingctx, info_type, array_type):
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    assert info_type == array_info_type, 'info_to_array: expected info type'
    return arr_type(info_type, array_type), info_to_array_codegen


@intrinsic
def test_alloc_np(typingctx, len_typ, arr_type):
    array_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type

    def codegen(context, builder, sig, args):
        dvf__rnzz, vzodi__blsn = args
        zde__ypfg = numba_to_c_type(array_type.dtype)
        timxg__uriov = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), zde__ypfg))
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='alloc_numpy')
        return builder.call(cspms__ezn, [dvf__rnzz, builder.load(timxg__uriov)]
            )
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        dvf__rnzz, xjhw__gkpxi = args
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='alloc_string_array')
        return builder.call(cspms__ezn, [dvf__rnzz, xjhw__gkpxi])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    plag__wjeb, = args
    mqzhu__mvrse = numba.cpython.listobj.ListInstance(context, builder, sig
        .args[0], plag__wjeb)
    lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer().as_pointer(), lir.IntType(64)])
    cspms__ezn = cgutils.get_or_insert_function(builder.module, lklj__zmzr,
        name='arr_info_list_to_table')
    return builder.call(cspms__ezn, [mqzhu__mvrse.data, mqzhu__mvrse.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='info_from_table')
        return builder.call(cspms__ezn, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    pwfk__amscz = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, umya__ylrnq, vzodi__blsn = args
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='info_from_table')
        wol__pxrmd = cgutils.create_struct_proxy(pwfk__amscz)(context, builder)
        wol__pxrmd.parent = cgutils.get_null_value(wol__pxrmd.parent.type)
        ftkng__evdl = context.make_array(table_idx_arr_t)(context, builder,
            umya__ylrnq)
        hsl__jcfz = context.get_constant(types.int64, -1)
        ynu__cxt = context.get_constant(types.int64, 0)
        aen__wfarp = cgutils.alloca_once_value(builder, ynu__cxt)
        for t, req__usxzv in pwfk__amscz.type_to_blk.items():
            ohxrg__majt = context.get_constant(types.int64, len(pwfk__amscz
                .block_to_arr_ind[req__usxzv]))
            vzodi__blsn, qgxvc__xozn = ListInstance.allocate_ex(context,
                builder, types.List(t), ohxrg__majt)
            qgxvc__xozn.size = ohxrg__majt
            wanpi__plmr = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(pwfk__amscz.block_to_arr_ind
                [req__usxzv], dtype=np.int64))
            ygdz__wdoc = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, wanpi__plmr)
            with cgutils.for_range(builder, ohxrg__majt) as ptn__mjje:
                zjn__wpl = ptn__mjje.index
                tmjft__jiz = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    ygdz__wdoc, zjn__wpl)
                zuagz__kbxft = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, ftkng__evdl, tmjft__jiz)
                zgzvq__nyy = builder.icmp_unsigned('!=', zuagz__kbxft,
                    hsl__jcfz)
                with builder.if_else(zgzvq__nyy) as (vfstv__ifzjg, cdp__rxt):
                    with vfstv__ifzjg:
                        zoqn__evi = builder.call(cspms__ezn, [cpp_table,
                            zuagz__kbxft])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            zoqn__evi])
                        qgxvc__xozn.inititem(zjn__wpl, arr, incref=False)
                        dvf__rnzz = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(dvf__rnzz, aen__wfarp)
                    with cdp__rxt:
                        gjfqf__nvbb = context.get_constant_null(t)
                        qgxvc__xozn.inititem(zjn__wpl, gjfqf__nvbb, incref=
                            False)
            setattr(wol__pxrmd, f'block_{req__usxzv}', qgxvc__xozn.value)
        wol__pxrmd.len = builder.load(aen__wfarp)
        return wol__pxrmd._getvalue()
    return pwfk__amscz(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    yxii__gdhvq = out_col_inds_t.instance_type.meta
    pwfk__amscz = unwrap_typeref(out_types_t.types[0])
    hzk__fpkk = [unwrap_typeref(out_types_t.types[zjn__wpl]) for zjn__wpl in
        range(1, len(out_types_t.types))]
    giay__lbfnc = {}
    got__fqkr = get_overload_const_int(n_table_cols_t)
    moro__dba = {ysjcz__nyfe: zjn__wpl for zjn__wpl, ysjcz__nyfe in
        enumerate(yxii__gdhvq)}
    if not is_overload_none(unknown_cat_arrs_t):
        ahu__stl = {vjx__nmab: zjn__wpl for zjn__wpl, vjx__nmab in
            enumerate(cat_inds_t.instance_type.meta)}
    dhb__glncc = []
    apg__svzte = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(pwfk__amscz, bodo.TableType):
        apg__svzte += f'  py_table = init_table(py_table_type, False)\n'
        apg__svzte += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for rtjl__ygnfd, req__usxzv in pwfk__amscz.type_to_blk.items():
            cft__meg = [moro__dba.get(zjn__wpl, -1) for zjn__wpl in
                pwfk__amscz.block_to_arr_ind[req__usxzv]]
            giay__lbfnc[f'out_inds_{req__usxzv}'] = np.array(cft__meg, np.int64
                )
            giay__lbfnc[f'out_type_{req__usxzv}'] = rtjl__ygnfd
            giay__lbfnc[f'typ_list_{req__usxzv}'] = types.List(rtjl__ygnfd)
            hyvh__ibm = f'out_type_{req__usxzv}'
            if type_has_unknown_cats(rtjl__ygnfd):
                if is_overload_none(unknown_cat_arrs_t):
                    apg__svzte += f"""  in_arr_list_{req__usxzv} = get_table_block(out_types_t[0], {req__usxzv})
"""
                    hyvh__ibm = f'in_arr_list_{req__usxzv}[i]'
                else:
                    giay__lbfnc[f'cat_arr_inds_{req__usxzv}'] = np.array([
                        ahu__stl.get(zjn__wpl, -1) for zjn__wpl in
                        pwfk__amscz.block_to_arr_ind[req__usxzv]], np.int64)
                    hyvh__ibm = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{req__usxzv}[i]]')
            ohxrg__majt = len(pwfk__amscz.block_to_arr_ind[req__usxzv])
            apg__svzte += f"""  arr_list_{req__usxzv} = alloc_list_like(typ_list_{req__usxzv}, {ohxrg__majt}, False)
"""
            apg__svzte += f'  for i in range(len(arr_list_{req__usxzv})):\n'
            apg__svzte += (
                f'    cpp_ind_{req__usxzv} = out_inds_{req__usxzv}[i]\n')
            apg__svzte += f'    if cpp_ind_{req__usxzv} == -1:\n'
            apg__svzte += f'      continue\n'
            apg__svzte += f"""    arr_{req__usxzv} = info_to_array(info_from_table(cpp_table, cpp_ind_{req__usxzv}), {hyvh__ibm})
"""
            apg__svzte += f'    arr_list_{req__usxzv}[i] = arr_{req__usxzv}\n'
            apg__svzte += f"""  py_table = set_table_block(py_table, arr_list_{req__usxzv}, {req__usxzv})
"""
        dhb__glncc.append('py_table')
    elif pwfk__amscz != types.none:
        zhnaz__tryu = moro__dba.get(0, -1)
        if zhnaz__tryu != -1:
            giay__lbfnc[f'arr_typ_arg0'] = pwfk__amscz
            hyvh__ibm = f'arr_typ_arg0'
            if type_has_unknown_cats(pwfk__amscz):
                if is_overload_none(unknown_cat_arrs_t):
                    hyvh__ibm = f'out_types_t[0]'
                else:
                    hyvh__ibm = f'unknown_cat_arrs_t[{ahu__stl[0]}]'
            apg__svzte += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {zhnaz__tryu}), {hyvh__ibm})
"""
            dhb__glncc.append('out_arg0')
    for zjn__wpl, t in enumerate(hzk__fpkk):
        zhnaz__tryu = moro__dba.get(got__fqkr + zjn__wpl, -1)
        if zhnaz__tryu != -1:
            giay__lbfnc[f'extra_arr_type_{zjn__wpl}'] = t
            hyvh__ibm = f'extra_arr_type_{zjn__wpl}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    hyvh__ibm = f'out_types_t[{zjn__wpl + 1}]'
                else:
                    hyvh__ibm = (
                        f'unknown_cat_arrs_t[{ahu__stl[got__fqkr + zjn__wpl]}]'
                        )
            apg__svzte += f"""  out_{zjn__wpl} = info_to_array(info_from_table(cpp_table, {zhnaz__tryu}), {hyvh__ibm})
"""
            dhb__glncc.append(f'out_{zjn__wpl}')
    afxf__fto = ',' if len(dhb__glncc) == 1 else ''
    apg__svzte += f"  return ({', '.join(dhb__glncc)}{afxf__fto})\n"
    giay__lbfnc.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(yxii__gdhvq), 'py_table_type': pwfk__amscz})
    eze__fwug = {}
    exec(apg__svzte, giay__lbfnc, eze__fwug)
    return eze__fwug['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    pwfk__amscz = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, vzodi__blsn = args
        ktlgi__liqg = cgutils.create_struct_proxy(pwfk__amscz)(context,
            builder, py_table)
        if pwfk__amscz.has_runtime_cols:
            ewiwp__ecom = lir.Constant(lir.IntType(64), 0)
            for req__usxzv, t in enumerate(pwfk__amscz.arr_types):
                aljd__ighld = getattr(ktlgi__liqg, f'block_{req__usxzv}')
                jjw__yds = ListInstance(context, builder, types.List(t),
                    aljd__ighld)
                ewiwp__ecom = builder.add(ewiwp__ecom, jjw__yds.size)
        else:
            ewiwp__ecom = lir.Constant(lir.IntType(64), len(pwfk__amscz.
                arr_types))
        vzodi__blsn, eqv__yyj = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), ewiwp__ecom)
        eqv__yyj.size = ewiwp__ecom
        if pwfk__amscz.has_runtime_cols:
            igwrb__lva = lir.Constant(lir.IntType(64), 0)
            for req__usxzv, t in enumerate(pwfk__amscz.arr_types):
                aljd__ighld = getattr(ktlgi__liqg, f'block_{req__usxzv}')
                jjw__yds = ListInstance(context, builder, types.List(t),
                    aljd__ighld)
                ohxrg__majt = jjw__yds.size
                with cgutils.for_range(builder, ohxrg__majt) as ptn__mjje:
                    zjn__wpl = ptn__mjje.index
                    arr = jjw__yds.getitem(zjn__wpl)
                    ntf__pffs = signature(array_info_type, t)
                    elkv__lupu = arr,
                    bsa__whttu = array_to_info_codegen(context, builder,
                        ntf__pffs, elkv__lupu)
                    eqv__yyj.inititem(builder.add(igwrb__lva, zjn__wpl),
                        bsa__whttu, incref=False)
                igwrb__lva = builder.add(igwrb__lva, ohxrg__majt)
        else:
            for t, req__usxzv in pwfk__amscz.type_to_blk.items():
                ohxrg__majt = context.get_constant(types.int64, len(
                    pwfk__amscz.block_to_arr_ind[req__usxzv]))
                aljd__ighld = getattr(ktlgi__liqg, f'block_{req__usxzv}')
                jjw__yds = ListInstance(context, builder, types.List(t),
                    aljd__ighld)
                wanpi__plmr = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(pwfk__amscz.
                    block_to_arr_ind[req__usxzv], dtype=np.int64))
                ygdz__wdoc = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, wanpi__plmr)
                with cgutils.for_range(builder, ohxrg__majt) as ptn__mjje:
                    zjn__wpl = ptn__mjje.index
                    tmjft__jiz = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        ygdz__wdoc, zjn__wpl)
                    eezx__rqzz = signature(types.none, pwfk__amscz, types.
                        List(t), types.int64, types.int64)
                    lbfr__cpbis = py_table, aljd__ighld, zjn__wpl, tmjft__jiz
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, eezx__rqzz, lbfr__cpbis)
                    arr = jjw__yds.getitem(zjn__wpl)
                    ntf__pffs = signature(array_info_type, t)
                    elkv__lupu = arr,
                    bsa__whttu = array_to_info_codegen(context, builder,
                        ntf__pffs, elkv__lupu)
                    eqv__yyj.inititem(tmjft__jiz, bsa__whttu, incref=False)
        iou__fhsx = eqv__yyj.value
        dmrev__iltc = signature(table_type, types.List(array_info_type))
        ehnk__qxgca = iou__fhsx,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            dmrev__iltc, ehnk__qxgca)
        context.nrt.decref(builder, types.List(array_info_type), iou__fhsx)
        return cpp_table
    return table_type(pwfk__amscz, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    fwko__cjb = in_col_inds_t.instance_type.meta
    giay__lbfnc = {}
    got__fqkr = get_overload_const_int(n_table_cols_t)
    ngi__prrd = defaultdict(list)
    moro__dba = {}
    for zjn__wpl, ysjcz__nyfe in enumerate(fwko__cjb):
        if ysjcz__nyfe in moro__dba:
            ngi__prrd[ysjcz__nyfe].append(zjn__wpl)
        else:
            moro__dba[ysjcz__nyfe] = zjn__wpl
    apg__svzte = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    apg__svzte += (
        f'  cpp_arr_list = alloc_empty_list_type({len(fwko__cjb)}, array_info_type)\n'
        )
    if py_table != types.none:
        for req__usxzv in py_table.type_to_blk.values():
            cft__meg = [moro__dba.get(zjn__wpl, -1) for zjn__wpl in
                py_table.block_to_arr_ind[req__usxzv]]
            giay__lbfnc[f'out_inds_{req__usxzv}'] = np.array(cft__meg, np.int64
                )
            giay__lbfnc[f'arr_inds_{req__usxzv}'] = np.array(py_table.
                block_to_arr_ind[req__usxzv], np.int64)
            apg__svzte += (
                f'  arr_list_{req__usxzv} = get_table_block(py_table, {req__usxzv})\n'
                )
            apg__svzte += f'  for i in range(len(arr_list_{req__usxzv})):\n'
            apg__svzte += (
                f'    out_arr_ind_{req__usxzv} = out_inds_{req__usxzv}[i]\n')
            apg__svzte += f'    if out_arr_ind_{req__usxzv} == -1:\n'
            apg__svzte += f'      continue\n'
            apg__svzte += (
                f'    arr_ind_{req__usxzv} = arr_inds_{req__usxzv}[i]\n')
            apg__svzte += f"""    ensure_column_unboxed(py_table, arr_list_{req__usxzv}, i, arr_ind_{req__usxzv})
"""
            apg__svzte += f"""    cpp_arr_list[out_arr_ind_{req__usxzv}] = array_to_info(arr_list_{req__usxzv}[i])
"""
        for puei__jrasi, yzybx__idjfk in ngi__prrd.items():
            if puei__jrasi < got__fqkr:
                req__usxzv = py_table.block_nums[puei__jrasi]
                mti__wdwlp = py_table.block_offsets[puei__jrasi]
                for zhnaz__tryu in yzybx__idjfk:
                    apg__svzte += f"""  cpp_arr_list[{zhnaz__tryu}] = array_to_info(arr_list_{req__usxzv}[{mti__wdwlp}])
"""
    for zjn__wpl in range(len(extra_arrs_tup)):
        yovi__hgcvf = moro__dba.get(got__fqkr + zjn__wpl, -1)
        if yovi__hgcvf != -1:
            cfcml__ypl = [yovi__hgcvf] + ngi__prrd.get(got__fqkr + zjn__wpl, []
                )
            for zhnaz__tryu in cfcml__ypl:
                apg__svzte += f"""  cpp_arr_list[{zhnaz__tryu}] = array_to_info(extra_arrs_tup[{zjn__wpl}])
"""
    apg__svzte += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    giay__lbfnc.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    eze__fwug = {}
    exec(apg__svzte, giay__lbfnc, eze__fwug)
    return eze__fwug['impl']


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))
decref_table_array = types.ExternalFunction('decref_table_array', types.
    void(table_type, types.int32))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lklj__zmzr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='delete_table')
        builder.call(cspms__ezn, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='shuffle_table')
        nscf__cgqyq = builder.call(cspms__ezn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return nscf__cgqyq
    return table_type(table_t, types.int64, types.boolean, types.int32
        ), codegen


class ShuffleInfoType(types.Type):

    def __init__(self):
        super(ShuffleInfoType, self).__init__(name='ShuffleInfoType()')


shuffle_info_type = ShuffleInfoType()
register_model(ShuffleInfoType)(models.OpaqueModel)
get_shuffle_info = types.ExternalFunction('get_shuffle_info',
    shuffle_info_type(table_type))


@intrinsic
def delete_shuffle_info(typingctx, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[0] == types.none:
            return
        lklj__zmzr = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='delete_shuffle_info')
        return builder.call(cspms__ezn, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='reverse_shuffle_table')
        return builder.call(cspms__ezn, args)
    return table_type(table_type, shuffle_info_t), codegen


@intrinsic
def get_null_shuffle_info(typingctx):

    def codegen(context, builder, sig, args):
        return context.get_constant_null(sig.return_type)
    return shuffle_info_type(), codegen


@intrinsic
def hash_join_table(typingctx, left_table_t, right_table_t, left_parallel_t,
    right_parallel_t, n_keys_t, n_data_left_t, n_data_right_t, same_vect_t,
    key_in_out_t, same_need_typechange_t, is_left_t, is_right_t, is_join_t,
    extra_data_col_t, indicator, _bodo_na_equal, cond_func, left_col_nums,
    left_col_nums_len, right_col_nums, right_col_nums_len, num_rows_ptr_t):
    assert left_table_t == table_type
    assert right_table_t == table_type

    def codegen(context, builder, sig, args):
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='hash_join_table')
        nscf__cgqyq = builder.call(cspms__ezn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return nscf__cgqyq
    return table_type(left_table_t, right_table_t, types.boolean, types.
        boolean, types.int64, types.int64, types.int64, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        boolean, types.boolean, types.boolean, types.boolean, types.voidptr,
        types.voidptr, types.int64, types.voidptr, types.int64, types.voidptr
        ), codegen


@intrinsic
def sort_values_table(typingctx, table_t, n_keys_t, vect_ascending_t,
    na_position_b_t, dead_keys_t, n_rows_t, parallel_t):
    assert table_t == table_type, 'C++ table type expected'

    def codegen(context, builder, sig, args):
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='sort_values_table')
        nscf__cgqyq = builder.call(cspms__ezn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return nscf__cgqyq
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='sample_table')
        nscf__cgqyq = builder.call(cspms__ezn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return nscf__cgqyq
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='shuffle_renormalization')
        nscf__cgqyq = builder.call(cspms__ezn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return nscf__cgqyq
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='shuffle_renormalization_group')
        nscf__cgqyq = builder.call(cspms__ezn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return nscf__cgqyq
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='drop_duplicates_table')
        nscf__cgqyq = builder.call(cspms__ezn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return nscf__cgqyq
    return table_type(table_t, types.boolean, types.int64, types.int64,
        types.boolean, types.boolean), codegen


@intrinsic
def groupby_and_aggregate(typingctx, table_t, n_keys_t, input_has_index,
    ftypes, func_offsets, udf_n_redvars, is_parallel, skipdropna_t,
    shift_periods_t, transform_func, head_n, return_keys, return_index,
    dropna, update_cb, combine_cb, eval_cb, general_udfs_cb,
    udf_table_dummy_t, n_out_rows_t):
    assert table_t == table_type
    assert udf_table_dummy_t == table_type

    def codegen(context, builder, sig, args):
        lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer()])
        cspms__ezn = cgutils.get_or_insert_function(builder.module,
            lklj__zmzr, name='groupby_and_aggregate')
        nscf__cgqyq = builder.call(cspms__ezn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return nscf__cgqyq
    return table_type(table_t, types.int64, types.boolean, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        int64, types.int64, types.int64, types.boolean, types.boolean,
        types.boolean, types.voidptr, types.voidptr, types.voidptr, types.
        voidptr, table_t, types.voidptr), codegen


get_groupby_labels = types.ExternalFunction('get_groupby_labels', types.
    int64(table_type, types.voidptr, types.voidptr, types.boolean, types.bool_)
    )
_array_isin = types.ExternalFunction('array_isin', types.void(
    array_info_type, array_info_type, array_info_type, types.bool_))


@numba.njit(no_cpython_wrapper=True)
def array_isin(out_arr, in_arr, in_values, is_parallel):
    in_arr = decode_if_dict_array(in_arr)
    in_values = decode_if_dict_array(in_values)
    xpq__uqftm = array_to_info(in_arr)
    xti__aqer = array_to_info(in_values)
    gfls__seft = array_to_info(out_arr)
    xdmln__wpetj = arr_info_list_to_table([xpq__uqftm, xti__aqer, gfls__seft])
    _array_isin(gfls__seft, xpq__uqftm, xti__aqer, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(xdmln__wpetj)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    xpq__uqftm = array_to_info(in_arr)
    gfls__seft = array_to_info(out_arr)
    _get_search_regex(xpq__uqftm, case, match, pat, gfls__seft)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    kvwlz__zvvy = col_array_typ.dtype
    if isinstance(kvwlz__zvvy, types.Number) or kvwlz__zvvy in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                wol__pxrmd, kzyq__qzc = args
                wol__pxrmd = builder.bitcast(wol__pxrmd, lir.IntType(8).
                    as_pointer().as_pointer())
                zdla__giha = lir.Constant(lir.IntType(64), c_ind)
                lhm__alxdg = builder.load(builder.gep(wol__pxrmd, [zdla__giha])
                    )
                lhm__alxdg = builder.bitcast(lhm__alxdg, context.
                    get_data_type(kvwlz__zvvy).as_pointer())
                return builder.load(builder.gep(lhm__alxdg, [kzyq__qzc]))
            return kvwlz__zvvy(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                wol__pxrmd, kzyq__qzc = args
                wol__pxrmd = builder.bitcast(wol__pxrmd, lir.IntType(8).
                    as_pointer().as_pointer())
                zdla__giha = lir.Constant(lir.IntType(64), c_ind)
                lhm__alxdg = builder.load(builder.gep(wol__pxrmd, [zdla__giha])
                    )
                lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                piky__dqvfl = cgutils.get_or_insert_function(builder.module,
                    lklj__zmzr, name='array_info_getitem')
                yted__uzk = cgutils.alloca_once(builder, lir.IntType(64))
                args = lhm__alxdg, kzyq__qzc, yted__uzk
                oxhi__hbb = builder.call(piky__dqvfl, args)
                return context.make_tuple(builder, sig.return_type, [
                    oxhi__hbb, builder.load(yted__uzk)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                ykwqv__dwu = lir.Constant(lir.IntType(64), 1)
                ivemk__wyl = lir.Constant(lir.IntType(64), 2)
                wol__pxrmd, kzyq__qzc = args
                wol__pxrmd = builder.bitcast(wol__pxrmd, lir.IntType(8).
                    as_pointer().as_pointer())
                zdla__giha = lir.Constant(lir.IntType(64), c_ind)
                lhm__alxdg = builder.load(builder.gep(wol__pxrmd, [zdla__giha])
                    )
                lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                eyzh__ucitg = cgutils.get_or_insert_function(builder.module,
                    lklj__zmzr, name='get_nested_info')
                args = lhm__alxdg, ivemk__wyl
                nmdm__bhe = builder.call(eyzh__ucitg, args)
                lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                jmhnj__zjw = cgutils.get_or_insert_function(builder.module,
                    lklj__zmzr, name='array_info_getdata1')
                args = nmdm__bhe,
                quz__uqrf = builder.call(jmhnj__zjw, args)
                quz__uqrf = builder.bitcast(quz__uqrf, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                gzcj__nrsal = builder.sext(builder.load(builder.gep(
                    quz__uqrf, [kzyq__qzc])), lir.IntType(64))
                args = lhm__alxdg, ykwqv__dwu
                gxray__ife = builder.call(eyzh__ucitg, args)
                lklj__zmzr = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                piky__dqvfl = cgutils.get_or_insert_function(builder.module,
                    lklj__zmzr, name='array_info_getitem')
                yted__uzk = cgutils.alloca_once(builder, lir.IntType(64))
                args = gxray__ife, gzcj__nrsal, yted__uzk
                oxhi__hbb = builder.call(piky__dqvfl, args)
                return context.make_tuple(builder, sig.return_type, [
                    oxhi__hbb, builder.load(yted__uzk)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{kvwlz__zvvy}' column data type not supported"
        )


def _gen_row_na_check_intrinsic(col_array_dtype, c_ind):
    if isinstance(col_array_dtype, bodo.libs.int_arr_ext.IntegerArrayType
        ) or col_array_dtype in (bodo.libs.bool_arr_ext.boolean_array, bodo
        .binary_array_type) or is_str_arr_type(col_array_dtype) or isinstance(
        col_array_dtype, types.Array
        ) and col_array_dtype.dtype == bodo.datetime_date_type:

        @intrinsic
        def checkna_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                wviy__xvmz, kzyq__qzc = args
                wviy__xvmz = builder.bitcast(wviy__xvmz, lir.IntType(8).
                    as_pointer().as_pointer())
                zdla__giha = lir.Constant(lir.IntType(64), c_ind)
                lhm__alxdg = builder.load(builder.gep(wviy__xvmz, [zdla__giha])
                    )
                ikgz__siwg = builder.bitcast(lhm__alxdg, context.
                    get_data_type(types.bool_).as_pointer())
                tiaph__jafwe = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    ikgz__siwg, kzyq__qzc)
                wwkcf__cci = builder.icmp_unsigned('!=', tiaph__jafwe, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(wwkcf__cci, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        kvwlz__zvvy = col_array_dtype.dtype
        if kvwlz__zvvy in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    wol__pxrmd, kzyq__qzc = args
                    wol__pxrmd = builder.bitcast(wol__pxrmd, lir.IntType(8)
                        .as_pointer().as_pointer())
                    zdla__giha = lir.Constant(lir.IntType(64), c_ind)
                    lhm__alxdg = builder.load(builder.gep(wol__pxrmd, [
                        zdla__giha]))
                    lhm__alxdg = builder.bitcast(lhm__alxdg, context.
                        get_data_type(kvwlz__zvvy).as_pointer())
                    gysyl__vypps = builder.load(builder.gep(lhm__alxdg, [
                        kzyq__qzc]))
                    wwkcf__cci = builder.icmp_unsigned('!=', gysyl__vypps,
                        lir.Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(wwkcf__cci, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(kvwlz__zvvy, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    wol__pxrmd, kzyq__qzc = args
                    wol__pxrmd = builder.bitcast(wol__pxrmd, lir.IntType(8)
                        .as_pointer().as_pointer())
                    zdla__giha = lir.Constant(lir.IntType(64), c_ind)
                    lhm__alxdg = builder.load(builder.gep(wol__pxrmd, [
                        zdla__giha]))
                    lhm__alxdg = builder.bitcast(lhm__alxdg, context.
                        get_data_type(kvwlz__zvvy).as_pointer())
                    gysyl__vypps = builder.load(builder.gep(lhm__alxdg, [
                        kzyq__qzc]))
                    ikqq__jst = signature(types.bool_, kvwlz__zvvy)
                    tiaph__jafwe = numba.np.npyfuncs.np_real_isnan_impl(context
                        , builder, ikqq__jst, (gysyl__vypps,))
                    return builder.not_(builder.sext(tiaph__jafwe, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
