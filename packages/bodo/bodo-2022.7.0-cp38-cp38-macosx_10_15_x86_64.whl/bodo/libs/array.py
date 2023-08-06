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
        bzhf__uzdnu = context.make_helper(builder, arr_type, in_arr)
        in_arr = bzhf__uzdnu.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        pehha__luop = context.make_helper(builder, arr_type, in_arr)
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='list_string_array_to_info')
        return builder.call(bgyo__sfraj, [pehha__luop.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                yjeoa__lsix = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for ahcoo__ukmuv in arr_typ.data:
                    yjeoa__lsix += get_types(ahcoo__ukmuv)
                return yjeoa__lsix
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
            lwl__smi = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                ovs__pec = context.make_helper(builder, arr_typ, value=arr)
                qbgsf__hjftg = get_lengths(_get_map_arr_data_type(arr_typ),
                    ovs__pec.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                sqloz__debpj = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                qbgsf__hjftg = get_lengths(arr_typ.dtype, sqloz__debpj.data)
                qbgsf__hjftg = cgutils.pack_array(builder, [sqloz__debpj.
                    n_arrays] + [builder.extract_value(qbgsf__hjftg,
                    apcca__shwxe) for apcca__shwxe in range(qbgsf__hjftg.
                    type.count)])
            elif isinstance(arr_typ, StructArrayType):
                sqloz__debpj = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                qbgsf__hjftg = []
                for apcca__shwxe, ahcoo__ukmuv in enumerate(arr_typ.data):
                    ajx__tdaaw = get_lengths(ahcoo__ukmuv, builder.
                        extract_value(sqloz__debpj.data, apcca__shwxe))
                    qbgsf__hjftg += [builder.extract_value(ajx__tdaaw,
                        oqoz__opb) for oqoz__opb in range(ajx__tdaaw.type.
                        count)]
                qbgsf__hjftg = cgutils.pack_array(builder, [lwl__smi,
                    context.get_constant(types.int64, -1)] + qbgsf__hjftg)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                qbgsf__hjftg = cgutils.pack_array(builder, [lwl__smi])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return qbgsf__hjftg

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                ovs__pec = context.make_helper(builder, arr_typ, value=arr)
                rhmrz__gbn = get_buffers(_get_map_arr_data_type(arr_typ),
                    ovs__pec.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                sqloz__debpj = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                gldm__hjyex = get_buffers(arr_typ.dtype, sqloz__debpj.data)
                zjzp__slua = context.make_array(types.Array(offset_type, 1,
                    'C'))(context, builder, sqloz__debpj.offsets)
                jmpxd__ysecr = builder.bitcast(zjzp__slua.data, lir.IntType
                    (8).as_pointer())
                lcyqy__zmay = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, sqloz__debpj.null_bitmap)
                vlql__uhvk = builder.bitcast(lcyqy__zmay.data, lir.IntType(
                    8).as_pointer())
                rhmrz__gbn = cgutils.pack_array(builder, [jmpxd__ysecr,
                    vlql__uhvk] + [builder.extract_value(gldm__hjyex,
                    apcca__shwxe) for apcca__shwxe in range(gldm__hjyex.
                    type.count)])
            elif isinstance(arr_typ, StructArrayType):
                sqloz__debpj = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                gldm__hjyex = []
                for apcca__shwxe, ahcoo__ukmuv in enumerate(arr_typ.data):
                    gvgx__kezhe = get_buffers(ahcoo__ukmuv, builder.
                        extract_value(sqloz__debpj.data, apcca__shwxe))
                    gldm__hjyex += [builder.extract_value(gvgx__kezhe,
                        oqoz__opb) for oqoz__opb in range(gvgx__kezhe.type.
                        count)]
                lcyqy__zmay = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, sqloz__debpj.null_bitmap)
                vlql__uhvk = builder.bitcast(lcyqy__zmay.data, lir.IntType(
                    8).as_pointer())
                rhmrz__gbn = cgutils.pack_array(builder, [vlql__uhvk] +
                    gldm__hjyex)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                grjze__loe = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    grjze__loe = int128_type
                elif arr_typ == datetime_date_array_type:
                    grjze__loe = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                jhg__ijpk = context.make_array(types.Array(grjze__loe, 1, 'C')
                    )(context, builder, arr.data)
                lcyqy__zmay = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, arr.null_bitmap)
                gplsx__oagma = builder.bitcast(jhg__ijpk.data, lir.IntType(
                    8).as_pointer())
                vlql__uhvk = builder.bitcast(lcyqy__zmay.data, lir.IntType(
                    8).as_pointer())
                rhmrz__gbn = cgutils.pack_array(builder, [vlql__uhvk,
                    gplsx__oagma])
            elif arr_typ in (string_array_type, binary_array_type):
                sqloz__debpj = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                nff__swsj = context.make_helper(builder, offset_arr_type,
                    sqloz__debpj.offsets).data
                qtae__gii = context.make_helper(builder, char_arr_type,
                    sqloz__debpj.data).data
                ajto__qwvn = context.make_helper(builder,
                    null_bitmap_arr_type, sqloz__debpj.null_bitmap).data
                rhmrz__gbn = cgutils.pack_array(builder, [builder.bitcast(
                    nff__swsj, lir.IntType(8).as_pointer()), builder.
                    bitcast(ajto__qwvn, lir.IntType(8).as_pointer()),
                    builder.bitcast(qtae__gii, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                gplsx__oagma = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                eyt__mzg = lir.Constant(lir.IntType(8).as_pointer(), None)
                rhmrz__gbn = cgutils.pack_array(builder, [eyt__mzg,
                    gplsx__oagma])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return rhmrz__gbn

        def get_field_names(arr_typ):
            kepdl__pgy = []
            if isinstance(arr_typ, StructArrayType):
                for mfj__xlgfq, emrbc__vmdlk in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    kepdl__pgy.append(mfj__xlgfq)
                    kepdl__pgy += get_field_names(emrbc__vmdlk)
            elif isinstance(arr_typ, ArrayItemArrayType):
                kepdl__pgy += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                kepdl__pgy += get_field_names(_get_map_arr_data_type(arr_typ))
            return kepdl__pgy
        yjeoa__lsix = get_types(arr_type)
        ytv__mqb = cgutils.pack_array(builder, [context.get_constant(types.
            int32, t) for t in yjeoa__lsix])
        pyta__glxbd = cgutils.alloca_once_value(builder, ytv__mqb)
        qbgsf__hjftg = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, qbgsf__hjftg)
        rhmrz__gbn = get_buffers(arr_type, in_arr)
        bqupo__eei = cgutils.alloca_once_value(builder, rhmrz__gbn)
        kepdl__pgy = get_field_names(arr_type)
        if len(kepdl__pgy) == 0:
            kepdl__pgy = ['irrelevant']
        wit__bjs = cgutils.pack_array(builder, [context.insert_const_string
            (builder.module, a) for a in kepdl__pgy])
        fggn__ibf = cgutils.alloca_once_value(builder, wit__bjs)
        if isinstance(arr_type, MapArrayType):
            vof__pnrbn = _get_map_arr_data_type(arr_type)
            kijd__fjc = context.make_helper(builder, arr_type, value=in_arr)
            trnr__xzf = kijd__fjc.data
        else:
            vof__pnrbn = arr_type
            trnr__xzf = in_arr
        cwy__pcwuc = context.make_helper(builder, vof__pnrbn, trnr__xzf)
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='nested_array_to_info')
        gqmxg__hcked = builder.call(bgyo__sfraj, [builder.bitcast(
            pyta__glxbd, lir.IntType(32).as_pointer()), builder.bitcast(
            bqupo__eei, lir.IntType(8).as_pointer().as_pointer()), builder.
            bitcast(lengths_ptr, lir.IntType(64).as_pointer()), builder.
            bitcast(fggn__ibf, lir.IntType(8).as_pointer()), cwy__pcwuc.
            meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return gqmxg__hcked
    if arr_type in (string_array_type, binary_array_type):
        mhmc__boqnr = context.make_helper(builder, arr_type, in_arr)
        rmh__wgxp = ArrayItemArrayType(char_arr_type)
        pehha__luop = context.make_helper(builder, rmh__wgxp, mhmc__boqnr.data)
        sqloz__debpj = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        nff__swsj = context.make_helper(builder, offset_arr_type,
            sqloz__debpj.offsets).data
        qtae__gii = context.make_helper(builder, char_arr_type,
            sqloz__debpj.data).data
        ajto__qwvn = context.make_helper(builder, null_bitmap_arr_type,
            sqloz__debpj.null_bitmap).data
        eorn__jhqx = builder.zext(builder.load(builder.gep(nff__swsj, [
            sqloz__debpj.n_arrays])), lir.IntType(64))
        typ__rrti = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='string_array_to_info')
        return builder.call(bgyo__sfraj, [sqloz__debpj.n_arrays, eorn__jhqx,
            qtae__gii, nff__swsj, ajto__qwvn, pehha__luop.meminfo, typ__rrti])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        uot__wdh = arr.data
        avp__cmxtv = arr.indices
        sig = array_info_type(arr_type.data)
        yfw__cadvv = array_to_info_codegen(context, builder, sig, (uot__wdh
            ,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        byt__bxyxh = array_to_info_codegen(context, builder, sig, (
            avp__cmxtv,), False)
        tbx__ydq = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, avp__cmxtv)
        vlql__uhvk = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, tbx__ydq.null_bitmap).data
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='dict_str_array_to_info')
        ackny__mcafl = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(bgyo__sfraj, [yfw__cadvv, byt__bxyxh, builder.
            bitcast(vlql__uhvk, lir.IntType(8).as_pointer()), ackny__mcafl])
    igwh__xze = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        mlt__xlulk = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        eusw__dyjpt = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(eusw__dyjpt, 1, 'C')
        igwh__xze = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if igwh__xze:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        lwl__smi = builder.extract_value(arr.shape, 0)
        phgb__jgx = arr_type.dtype
        ygp__dztvt = numba_to_c_type(phgb__jgx)
        ojtbj__iddh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ygp__dztvt))
        if igwh__xze:
            rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
                rcvi__body, name='categorical_array_to_info')
            return builder.call(bgyo__sfraj, [lwl__smi, builder.bitcast(arr
                .data, lir.IntType(8).as_pointer()), builder.load(
                ojtbj__iddh), mlt__xlulk, arr.meminfo])
        else:
            rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
                rcvi__body, name='numpy_array_to_info')
            return builder.call(bgyo__sfraj, [lwl__smi, builder.bitcast(arr
                .data, lir.IntType(8).as_pointer()), builder.load(
                ojtbj__iddh), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        phgb__jgx = arr_type.dtype
        grjze__loe = phgb__jgx
        if isinstance(arr_type, DecimalArrayType):
            grjze__loe = int128_type
        if arr_type == datetime_date_array_type:
            grjze__loe = types.int64
        jhg__ijpk = context.make_array(types.Array(grjze__loe, 1, 'C'))(context
            , builder, arr.data)
        lwl__smi = builder.extract_value(jhg__ijpk.shape, 0)
        kslv__lseor = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        ygp__dztvt = numba_to_c_type(phgb__jgx)
        ojtbj__iddh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ygp__dztvt))
        if isinstance(arr_type, DecimalArrayType):
            rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
                rcvi__body, name='decimal_array_to_info')
            return builder.call(bgyo__sfraj, [lwl__smi, builder.bitcast(
                jhg__ijpk.data, lir.IntType(8).as_pointer()), builder.load(
                ojtbj__iddh), builder.bitcast(kslv__lseor.data, lir.IntType
                (8).as_pointer()), jhg__ijpk.meminfo, kslv__lseor.meminfo,
                context.get_constant(types.int32, arr_type.precision),
                context.get_constant(types.int32, arr_type.scale)])
        else:
            rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
                rcvi__body, name='nullable_array_to_info')
            return builder.call(bgyo__sfraj, [lwl__smi, builder.bitcast(
                jhg__ijpk.data, lir.IntType(8).as_pointer()), builder.load(
                ojtbj__iddh), builder.bitcast(kslv__lseor.data, lir.IntType
                (8).as_pointer()), jhg__ijpk.meminfo, kslv__lseor.meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        wmu__vgdxn = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        qcc__kwv = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        lwl__smi = builder.extract_value(wmu__vgdxn.shape, 0)
        ygp__dztvt = numba_to_c_type(arr_type.arr_type.dtype)
        ojtbj__iddh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ygp__dztvt))
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='interval_array_to_info')
        return builder.call(bgyo__sfraj, [lwl__smi, builder.bitcast(
            wmu__vgdxn.data, lir.IntType(8).as_pointer()), builder.bitcast(
            qcc__kwv.data, lir.IntType(8).as_pointer()), builder.load(
            ojtbj__iddh), wmu__vgdxn.meminfo, qcc__kwv.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    ell__lqyz = cgutils.alloca_once(builder, lir.IntType(64))
    gplsx__oagma = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    dhmu__tlb = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    rcvi__body = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    bgyo__sfraj = cgutils.get_or_insert_function(builder.module, rcvi__body,
        name='info_to_numpy_array')
    builder.call(bgyo__sfraj, [in_info, ell__lqyz, gplsx__oagma, dhmu__tlb])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    asbz__pfx = context.get_value_type(types.intp)
    mjrok__mty = cgutils.pack_array(builder, [builder.load(ell__lqyz)], ty=
        asbz__pfx)
    azuon__bbqfc = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    yhs__oil = cgutils.pack_array(builder, [azuon__bbqfc], ty=asbz__pfx)
    qtae__gii = builder.bitcast(builder.load(gplsx__oagma), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=qtae__gii, shape=mjrok__mty,
        strides=yhs__oil, itemsize=azuon__bbqfc, meminfo=builder.load(
        dhmu__tlb))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    otyy__quda = context.make_helper(builder, arr_type)
    rcvi__body = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    bgyo__sfraj = cgutils.get_or_insert_function(builder.module, rcvi__body,
        name='info_to_list_string_array')
    builder.call(bgyo__sfraj, [in_info, otyy__quda._get_ptr_by_name('meminfo')]
        )
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return otyy__quda._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    jxd__xsyru = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        pttr__xxc = lengths_pos
        gzxxa__xpj = infos_pos
        minnn__yjrm, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        otyvr__ljjtu = ArrayItemArrayPayloadType(arr_typ)
        gbki__xdm = context.get_data_type(otyvr__ljjtu)
        irvwn__rkgpi = context.get_abi_sizeof(gbki__xdm)
        rhbyh__golfh = define_array_item_dtor(context, builder, arr_typ,
            otyvr__ljjtu)
        bhl__wrni = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, irvwn__rkgpi), rhbyh__golfh)
        rjvnm__nfkng = context.nrt.meminfo_data(builder, bhl__wrni)
        kfo__ctgpk = builder.bitcast(rjvnm__nfkng, gbki__xdm.as_pointer())
        sqloz__debpj = cgutils.create_struct_proxy(otyvr__ljjtu)(context,
            builder)
        sqloz__debpj.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), pttr__xxc)
        sqloz__debpj.data = minnn__yjrm
        jybk__khtz = builder.load(array_infos_ptr)
        kzh__yfbcf = builder.bitcast(builder.extract_value(jybk__khtz,
            gzxxa__xpj), jxd__xsyru)
        sqloz__debpj.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, kzh__yfbcf)
        eqdwr__urxhk = builder.bitcast(builder.extract_value(jybk__khtz, 
            gzxxa__xpj + 1), jxd__xsyru)
        sqloz__debpj.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, eqdwr__urxhk)
        builder.store(sqloz__debpj._getvalue(), kfo__ctgpk)
        pehha__luop = context.make_helper(builder, arr_typ)
        pehha__luop.meminfo = bhl__wrni
        return pehha__luop._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        qayd__bin = []
        gzxxa__xpj = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for zker__vgug in arr_typ.data:
            minnn__yjrm, lengths_pos, infos_pos = nested_to_array(context,
                builder, zker__vgug, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            qayd__bin.append(minnn__yjrm)
        otyvr__ljjtu = StructArrayPayloadType(arr_typ.data)
        gbki__xdm = context.get_value_type(otyvr__ljjtu)
        irvwn__rkgpi = context.get_abi_sizeof(gbki__xdm)
        rhbyh__golfh = define_struct_arr_dtor(context, builder, arr_typ,
            otyvr__ljjtu)
        bhl__wrni = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, irvwn__rkgpi), rhbyh__golfh)
        rjvnm__nfkng = context.nrt.meminfo_data(builder, bhl__wrni)
        kfo__ctgpk = builder.bitcast(rjvnm__nfkng, gbki__xdm.as_pointer())
        sqloz__debpj = cgutils.create_struct_proxy(otyvr__ljjtu)(context,
            builder)
        sqloz__debpj.data = cgutils.pack_array(builder, qayd__bin
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, qayd__bin)
        jybk__khtz = builder.load(array_infos_ptr)
        eqdwr__urxhk = builder.bitcast(builder.extract_value(jybk__khtz,
            gzxxa__xpj), jxd__xsyru)
        sqloz__debpj.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, eqdwr__urxhk)
        builder.store(sqloz__debpj._getvalue(), kfo__ctgpk)
        zqn__eklp = context.make_helper(builder, arr_typ)
        zqn__eklp.meminfo = bhl__wrni
        return zqn__eklp._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        jybk__khtz = builder.load(array_infos_ptr)
        xncxb__waf = builder.bitcast(builder.extract_value(jybk__khtz,
            infos_pos), jxd__xsyru)
        mhmc__boqnr = context.make_helper(builder, arr_typ)
        rmh__wgxp = ArrayItemArrayType(char_arr_type)
        pehha__luop = context.make_helper(builder, rmh__wgxp)
        rcvi__body = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='info_to_string_array')
        builder.call(bgyo__sfraj, [xncxb__waf, pehha__luop._get_ptr_by_name
            ('meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        mhmc__boqnr.data = pehha__luop._getvalue()
        return mhmc__boqnr._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        jybk__khtz = builder.load(array_infos_ptr)
        yqxaw__xcc = builder.bitcast(builder.extract_value(jybk__khtz, 
            infos_pos + 1), jxd__xsyru)
        return _lower_info_to_array_numpy(arr_typ, context, builder, yqxaw__xcc
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        grjze__loe = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            grjze__loe = int128_type
        elif arr_typ == datetime_date_array_type:
            grjze__loe = types.int64
        jybk__khtz = builder.load(array_infos_ptr)
        eqdwr__urxhk = builder.bitcast(builder.extract_value(jybk__khtz,
            infos_pos), jxd__xsyru)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, eqdwr__urxhk)
        yqxaw__xcc = builder.bitcast(builder.extract_value(jybk__khtz, 
            infos_pos + 1), jxd__xsyru)
        arr.data = _lower_info_to_array_numpy(types.Array(grjze__loe, 1,
            'C'), context, builder, yqxaw__xcc)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, hlmx__mxpo = args
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
                return 1 + sum([get_num_arrays(zker__vgug) for zker__vgug in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(zker__vgug) for zker__vgug in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            ximpd__kpu = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            ximpd__kpu = _get_map_arr_data_type(arr_type)
        else:
            ximpd__kpu = arr_type
        vfplb__wlry = get_num_arrays(ximpd__kpu)
        qbgsf__hjftg = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), 0) for hlmx__mxpo in range(vfplb__wlry)])
        lengths_ptr = cgutils.alloca_once_value(builder, qbgsf__hjftg)
        eyt__mzg = lir.Constant(lir.IntType(8).as_pointer(), None)
        nmvb__neqrg = cgutils.pack_array(builder, [eyt__mzg for hlmx__mxpo in
            range(get_num_infos(ximpd__kpu))])
        array_infos_ptr = cgutils.alloca_once_value(builder, nmvb__neqrg)
        rcvi__body = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='info_to_nested_array')
        builder.call(bgyo__sfraj, [in_info, builder.bitcast(lengths_ptr,
            lir.IntType(64).as_pointer()), builder.bitcast(array_infos_ptr,
            lir.IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, hlmx__mxpo, hlmx__mxpo = nested_to_array(context, builder,
            ximpd__kpu, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            bzhf__uzdnu = context.make_helper(builder, arr_type)
            bzhf__uzdnu.data = arr
            context.nrt.incref(builder, ximpd__kpu, arr)
            arr = bzhf__uzdnu._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, ximpd__kpu)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        mhmc__boqnr = context.make_helper(builder, arr_type)
        rmh__wgxp = ArrayItemArrayType(char_arr_type)
        pehha__luop = context.make_helper(builder, rmh__wgxp)
        rcvi__body = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='info_to_string_array')
        builder.call(bgyo__sfraj, [in_info, pehha__luop._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        mhmc__boqnr.data = pehha__luop._getvalue()
        return mhmc__boqnr._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='get_nested_info')
        yfw__cadvv = builder.call(bgyo__sfraj, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        byt__bxyxh = builder.call(bgyo__sfraj, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        yyha__pfyu = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        yyha__pfyu.data = info_to_array_codegen(context, builder, sig, (
            yfw__cadvv, context.get_constant_null(arr_type.data)))
        eqjs__tuy = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = eqjs__tuy(array_info_type, eqjs__tuy)
        yyha__pfyu.indices = info_to_array_codegen(context, builder, sig, (
            byt__bxyxh, context.get_constant_null(eqjs__tuy)))
        rcvi__body = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='get_has_global_dictionary')
        ackny__mcafl = builder.call(bgyo__sfraj, [in_info])
        yyha__pfyu.has_global_dictionary = builder.trunc(ackny__mcafl,
            cgutils.bool_t)
        return yyha__pfyu._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        eusw__dyjpt = get_categories_int_type(arr_type.dtype)
        jday__exkh = types.Array(eusw__dyjpt, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(jday__exkh, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            ovc__ypo = bodo.utils.utils.create_categorical_type(arr_type.
                dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(ovc__ypo))
            int_type = arr_type.dtype.int_type
            dpf__yuy = arr_type.dtype.data.data
            rvy__ngy = context.get_constant_generic(builder, dpf__yuy, ovc__ypo
                )
            phgb__jgx = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(dpf__yuy), [rvy__ngy])
        else:
            phgb__jgx = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, phgb__jgx)
        out_arr.dtype = phgb__jgx
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        qtae__gii = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = qtae__gii
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        grjze__loe = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            grjze__loe = int128_type
        elif arr_type == datetime_date_array_type:
            grjze__loe = types.int64
        wfp__qcnb = types.Array(grjze__loe, 1, 'C')
        jhg__ijpk = context.make_array(wfp__qcnb)(context, builder)
        hoj__rmqmi = types.Array(types.uint8, 1, 'C')
        fsjn__iqbju = context.make_array(hoj__rmqmi)(context, builder)
        ell__lqyz = cgutils.alloca_once(builder, lir.IntType(64))
        honz__rpazc = cgutils.alloca_once(builder, lir.IntType(64))
        gplsx__oagma = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
            )
        bxir__zkofl = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        dhmu__tlb = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        nzjwj__vdbd = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        rcvi__body = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='info_to_nullable_array')
        builder.call(bgyo__sfraj, [in_info, ell__lqyz, honz__rpazc,
            gplsx__oagma, bxir__zkofl, dhmu__tlb, nzjwj__vdbd])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        asbz__pfx = context.get_value_type(types.intp)
        mjrok__mty = cgutils.pack_array(builder, [builder.load(ell__lqyz)],
            ty=asbz__pfx)
        azuon__bbqfc = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(grjze__loe)))
        yhs__oil = cgutils.pack_array(builder, [azuon__bbqfc], ty=asbz__pfx)
        qtae__gii = builder.bitcast(builder.load(gplsx__oagma), context.
            get_data_type(grjze__loe).as_pointer())
        numba.np.arrayobj.populate_array(jhg__ijpk, data=qtae__gii, shape=
            mjrok__mty, strides=yhs__oil, itemsize=azuon__bbqfc, meminfo=
            builder.load(dhmu__tlb))
        arr.data = jhg__ijpk._getvalue()
        mjrok__mty = cgutils.pack_array(builder, [builder.load(honz__rpazc)
            ], ty=asbz__pfx)
        azuon__bbqfc = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(types.uint8)))
        yhs__oil = cgutils.pack_array(builder, [azuon__bbqfc], ty=asbz__pfx)
        qtae__gii = builder.bitcast(builder.load(bxir__zkofl), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(fsjn__iqbju, data=qtae__gii, shape
            =mjrok__mty, strides=yhs__oil, itemsize=azuon__bbqfc, meminfo=
            builder.load(nzjwj__vdbd))
        arr.null_bitmap = fsjn__iqbju._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        wmu__vgdxn = context.make_array(arr_type.arr_type)(context, builder)
        qcc__kwv = context.make_array(arr_type.arr_type)(context, builder)
        ell__lqyz = cgutils.alloca_once(builder, lir.IntType(64))
        lwcns__nztf = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        frzg__eal = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        giel__prg = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        hansy__pdoi = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        rcvi__body = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='info_to_interval_array')
        builder.call(bgyo__sfraj, [in_info, ell__lqyz, lwcns__nztf,
            frzg__eal, giel__prg, hansy__pdoi])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        asbz__pfx = context.get_value_type(types.intp)
        mjrok__mty = cgutils.pack_array(builder, [builder.load(ell__lqyz)],
            ty=asbz__pfx)
        azuon__bbqfc = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
        yhs__oil = cgutils.pack_array(builder, [azuon__bbqfc], ty=asbz__pfx)
        raj__fqu = builder.bitcast(builder.load(lwcns__nztf), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(wmu__vgdxn, data=raj__fqu, shape=
            mjrok__mty, strides=yhs__oil, itemsize=azuon__bbqfc, meminfo=
            builder.load(giel__prg))
        arr.left = wmu__vgdxn._getvalue()
        ykn__ehu = builder.bitcast(builder.load(frzg__eal), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(qcc__kwv, data=ykn__ehu, shape=
            mjrok__mty, strides=yhs__oil, itemsize=azuon__bbqfc, meminfo=
            builder.load(hansy__pdoi))
        arr.right = qcc__kwv._getvalue()
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
        lwl__smi, hlmx__mxpo = args
        ygp__dztvt = numba_to_c_type(array_type.dtype)
        ojtbj__iddh = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ygp__dztvt))
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='alloc_numpy')
        return builder.call(bgyo__sfraj, [lwl__smi, builder.load(ojtbj__iddh)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        lwl__smi, fnodp__uplo = args
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='alloc_string_array')
        return builder.call(bgyo__sfraj, [lwl__smi, fnodp__uplo])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    uhks__gbb, = args
    dmb__bef = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], uhks__gbb)
    rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer().as_pointer(), lir.IntType(64)])
    bgyo__sfraj = cgutils.get_or_insert_function(builder.module, rcvi__body,
        name='arr_info_list_to_table')
    return builder.call(bgyo__sfraj, [dmb__bef.data, dmb__bef.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='info_from_table')
        return builder.call(bgyo__sfraj, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    mne__nak = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, htemm__wjtay, hlmx__mxpo = args
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='info_from_table')
        nxhhw__qaa = cgutils.create_struct_proxy(mne__nak)(context, builder)
        nxhhw__qaa.parent = cgutils.get_null_value(nxhhw__qaa.parent.type)
        mfqwy__rrm = context.make_array(table_idx_arr_t)(context, builder,
            htemm__wjtay)
        ppf__vakq = context.get_constant(types.int64, -1)
        xpcg__yjtu = context.get_constant(types.int64, 0)
        gsi__vuji = cgutils.alloca_once_value(builder, xpcg__yjtu)
        for t, anf__iavrx in mne__nak.type_to_blk.items():
            lzeq__mjajs = context.get_constant(types.int64, len(mne__nak.
                block_to_arr_ind[anf__iavrx]))
            hlmx__mxpo, ykf__thcb = ListInstance.allocate_ex(context,
                builder, types.List(t), lzeq__mjajs)
            ykf__thcb.size = lzeq__mjajs
            dznjj__bbcry = context.make_constant_array(builder, types.Array
                (types.int64, 1, 'C'), np.array(mne__nak.block_to_arr_ind[
                anf__iavrx], dtype=np.int64))
            ewfuv__fbxce = context.make_array(types.Array(types.int64, 1, 'C')
                )(context, builder, dznjj__bbcry)
            with cgutils.for_range(builder, lzeq__mjajs) as gpq__xwm:
                apcca__shwxe = gpq__xwm.index
                uyoqr__cxl = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    ewfuv__fbxce, apcca__shwxe)
                imkse__yssh = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, mfqwy__rrm, uyoqr__cxl)
                zbcr__bomd = builder.icmp_unsigned('!=', imkse__yssh, ppf__vakq
                    )
                with builder.if_else(zbcr__bomd) as (ymo__glfcm, qvb__edmla):
                    with ymo__glfcm:
                        hwj__cuwrl = builder.call(bgyo__sfraj, [cpp_table,
                            imkse__yssh])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            hwj__cuwrl])
                        ykf__thcb.inititem(apcca__shwxe, arr, incref=False)
                        lwl__smi = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(lwl__smi, gsi__vuji)
                    with qvb__edmla:
                        oait__mxznp = context.get_constant_null(t)
                        ykf__thcb.inititem(apcca__shwxe, oait__mxznp,
                            incref=False)
            setattr(nxhhw__qaa, f'block_{anf__iavrx}', ykf__thcb.value)
        nxhhw__qaa.len = builder.load(gsi__vuji)
        return nxhhw__qaa._getvalue()
    return mne__nak(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    mln__tsilq = out_col_inds_t.instance_type.meta
    mne__nak = unwrap_typeref(out_types_t.types[0])
    slizq__ufne = [unwrap_typeref(out_types_t.types[apcca__shwxe]) for
        apcca__shwxe in range(1, len(out_types_t.types))]
    vbc__fqf = {}
    vqez__mfv = get_overload_const_int(n_table_cols_t)
    lix__kmnbc = {ljtb__vzsu: apcca__shwxe for apcca__shwxe, ljtb__vzsu in
        enumerate(mln__tsilq)}
    if not is_overload_none(unknown_cat_arrs_t):
        xnk__zix = {basd__gdt: apcca__shwxe for apcca__shwxe, basd__gdt in
            enumerate(cat_inds_t.instance_type.meta)}
    pwmnc__bjzc = []
    vdap__zxeml = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(mne__nak, bodo.TableType):
        vdap__zxeml += f'  py_table = init_table(py_table_type, False)\n'
        vdap__zxeml += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for zfahk__mrv, anf__iavrx in mne__nak.type_to_blk.items():
            asetj__bslj = [lix__kmnbc.get(apcca__shwxe, -1) for
                apcca__shwxe in mne__nak.block_to_arr_ind[anf__iavrx]]
            vbc__fqf[f'out_inds_{anf__iavrx}'] = np.array(asetj__bslj, np.int64
                )
            vbc__fqf[f'out_type_{anf__iavrx}'] = zfahk__mrv
            vbc__fqf[f'typ_list_{anf__iavrx}'] = types.List(zfahk__mrv)
            pytqk__zyxl = f'out_type_{anf__iavrx}'
            if type_has_unknown_cats(zfahk__mrv):
                if is_overload_none(unknown_cat_arrs_t):
                    vdap__zxeml += f"""  in_arr_list_{anf__iavrx} = get_table_block(out_types_t[0], {anf__iavrx})
"""
                    pytqk__zyxl = f'in_arr_list_{anf__iavrx}[i]'
                else:
                    vbc__fqf[f'cat_arr_inds_{anf__iavrx}'] = np.array([
                        xnk__zix.get(apcca__shwxe, -1) for apcca__shwxe in
                        mne__nak.block_to_arr_ind[anf__iavrx]], np.int64)
                    pytqk__zyxl = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{anf__iavrx}[i]]')
            lzeq__mjajs = len(mne__nak.block_to_arr_ind[anf__iavrx])
            vdap__zxeml += f"""  arr_list_{anf__iavrx} = alloc_list_like(typ_list_{anf__iavrx}, {lzeq__mjajs}, False)
"""
            vdap__zxeml += f'  for i in range(len(arr_list_{anf__iavrx})):\n'
            vdap__zxeml += (
                f'    cpp_ind_{anf__iavrx} = out_inds_{anf__iavrx}[i]\n')
            vdap__zxeml += f'    if cpp_ind_{anf__iavrx} == -1:\n'
            vdap__zxeml += f'      continue\n'
            vdap__zxeml += f"""    arr_{anf__iavrx} = info_to_array(info_from_table(cpp_table, cpp_ind_{anf__iavrx}), {pytqk__zyxl})
"""
            vdap__zxeml += f'    arr_list_{anf__iavrx}[i] = arr_{anf__iavrx}\n'
            vdap__zxeml += f"""  py_table = set_table_block(py_table, arr_list_{anf__iavrx}, {anf__iavrx})
"""
        pwmnc__bjzc.append('py_table')
    elif mne__nak != types.none:
        iofti__ipik = lix__kmnbc.get(0, -1)
        if iofti__ipik != -1:
            vbc__fqf[f'arr_typ_arg0'] = mne__nak
            pytqk__zyxl = f'arr_typ_arg0'
            if type_has_unknown_cats(mne__nak):
                if is_overload_none(unknown_cat_arrs_t):
                    pytqk__zyxl = f'out_types_t[0]'
                else:
                    pytqk__zyxl = f'unknown_cat_arrs_t[{xnk__zix[0]}]'
            vdap__zxeml += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {iofti__ipik}), {pytqk__zyxl})
"""
            pwmnc__bjzc.append('out_arg0')
    for apcca__shwxe, t in enumerate(slizq__ufne):
        iofti__ipik = lix__kmnbc.get(vqez__mfv + apcca__shwxe, -1)
        if iofti__ipik != -1:
            vbc__fqf[f'extra_arr_type_{apcca__shwxe}'] = t
            pytqk__zyxl = f'extra_arr_type_{apcca__shwxe}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    pytqk__zyxl = f'out_types_t[{apcca__shwxe + 1}]'
                else:
                    pytqk__zyxl = (
                        f'unknown_cat_arrs_t[{xnk__zix[vqez__mfv + apcca__shwxe]}]'
                        )
            vdap__zxeml += f"""  out_{apcca__shwxe} = info_to_array(info_from_table(cpp_table, {iofti__ipik}), {pytqk__zyxl})
"""
            pwmnc__bjzc.append(f'out_{apcca__shwxe}')
    vyui__bpttn = ',' if len(pwmnc__bjzc) == 1 else ''
    vdap__zxeml += f"  return ({', '.join(pwmnc__bjzc)}{vyui__bpttn})\n"
    vbc__fqf.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(mln__tsilq), 'py_table_type': mne__nak})
    xqrc__qehzi = {}
    exec(vdap__zxeml, vbc__fqf, xqrc__qehzi)
    return xqrc__qehzi['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    mne__nak = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, hlmx__mxpo = args
        utsrg__jyyp = cgutils.create_struct_proxy(mne__nak)(context,
            builder, py_table)
        if mne__nak.has_runtime_cols:
            hid__vkff = lir.Constant(lir.IntType(64), 0)
            for anf__iavrx, t in enumerate(mne__nak.arr_types):
                qnuo__vjvfi = getattr(utsrg__jyyp, f'block_{anf__iavrx}')
                ogq__qezda = ListInstance(context, builder, types.List(t),
                    qnuo__vjvfi)
                hid__vkff = builder.add(hid__vkff, ogq__qezda.size)
        else:
            hid__vkff = lir.Constant(lir.IntType(64), len(mne__nak.arr_types))
        hlmx__mxpo, ejmw__abe = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), hid__vkff)
        ejmw__abe.size = hid__vkff
        if mne__nak.has_runtime_cols:
            cefnw__cbqyc = lir.Constant(lir.IntType(64), 0)
            for anf__iavrx, t in enumerate(mne__nak.arr_types):
                qnuo__vjvfi = getattr(utsrg__jyyp, f'block_{anf__iavrx}')
                ogq__qezda = ListInstance(context, builder, types.List(t),
                    qnuo__vjvfi)
                lzeq__mjajs = ogq__qezda.size
                with cgutils.for_range(builder, lzeq__mjajs) as gpq__xwm:
                    apcca__shwxe = gpq__xwm.index
                    arr = ogq__qezda.getitem(apcca__shwxe)
                    fubo__lto = signature(array_info_type, t)
                    esf__zbzz = arr,
                    bglg__yey = array_to_info_codegen(context, builder,
                        fubo__lto, esf__zbzz)
                    ejmw__abe.inititem(builder.add(cefnw__cbqyc,
                        apcca__shwxe), bglg__yey, incref=False)
                cefnw__cbqyc = builder.add(cefnw__cbqyc, lzeq__mjajs)
        else:
            for t, anf__iavrx in mne__nak.type_to_blk.items():
                lzeq__mjajs = context.get_constant(types.int64, len(
                    mne__nak.block_to_arr_ind[anf__iavrx]))
                qnuo__vjvfi = getattr(utsrg__jyyp, f'block_{anf__iavrx}')
                ogq__qezda = ListInstance(context, builder, types.List(t),
                    qnuo__vjvfi)
                dznjj__bbcry = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(mne__nak.
                    block_to_arr_ind[anf__iavrx], dtype=np.int64))
                ewfuv__fbxce = context.make_array(types.Array(types.int64, 
                    1, 'C'))(context, builder, dznjj__bbcry)
                with cgutils.for_range(builder, lzeq__mjajs) as gpq__xwm:
                    apcca__shwxe = gpq__xwm.index
                    uyoqr__cxl = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        ewfuv__fbxce, apcca__shwxe)
                    hok__eep = signature(types.none, mne__nak, types.List(t
                        ), types.int64, types.int64)
                    cuxt__bzyc = (py_table, qnuo__vjvfi, apcca__shwxe,
                        uyoqr__cxl)
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, hok__eep, cuxt__bzyc)
                    arr = ogq__qezda.getitem(apcca__shwxe)
                    fubo__lto = signature(array_info_type, t)
                    esf__zbzz = arr,
                    bglg__yey = array_to_info_codegen(context, builder,
                        fubo__lto, esf__zbzz)
                    ejmw__abe.inititem(uyoqr__cxl, bglg__yey, incref=False)
        gkmi__accl = ejmw__abe.value
        jao__lyn = signature(table_type, types.List(array_info_type))
        iaa__wteb = gkmi__accl,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            jao__lyn, iaa__wteb)
        context.nrt.decref(builder, types.List(array_info_type), gkmi__accl)
        return cpp_table
    return table_type(mne__nak, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    mij__nyk = in_col_inds_t.instance_type.meta
    vbc__fqf = {}
    vqez__mfv = get_overload_const_int(n_table_cols_t)
    hlgc__ulqg = defaultdict(list)
    lix__kmnbc = {}
    for apcca__shwxe, ljtb__vzsu in enumerate(mij__nyk):
        if ljtb__vzsu in lix__kmnbc:
            hlgc__ulqg[ljtb__vzsu].append(apcca__shwxe)
        else:
            lix__kmnbc[ljtb__vzsu] = apcca__shwxe
    vdap__zxeml = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    vdap__zxeml += (
        f'  cpp_arr_list = alloc_empty_list_type({len(mij__nyk)}, array_info_type)\n'
        )
    if py_table != types.none:
        for anf__iavrx in py_table.type_to_blk.values():
            asetj__bslj = [lix__kmnbc.get(apcca__shwxe, -1) for
                apcca__shwxe in py_table.block_to_arr_ind[anf__iavrx]]
            vbc__fqf[f'out_inds_{anf__iavrx}'] = np.array(asetj__bslj, np.int64
                )
            vbc__fqf[f'arr_inds_{anf__iavrx}'] = np.array(py_table.
                block_to_arr_ind[anf__iavrx], np.int64)
            vdap__zxeml += (
                f'  arr_list_{anf__iavrx} = get_table_block(py_table, {anf__iavrx})\n'
                )
            vdap__zxeml += f'  for i in range(len(arr_list_{anf__iavrx})):\n'
            vdap__zxeml += (
                f'    out_arr_ind_{anf__iavrx} = out_inds_{anf__iavrx}[i]\n')
            vdap__zxeml += f'    if out_arr_ind_{anf__iavrx} == -1:\n'
            vdap__zxeml += f'      continue\n'
            vdap__zxeml += (
                f'    arr_ind_{anf__iavrx} = arr_inds_{anf__iavrx}[i]\n')
            vdap__zxeml += f"""    ensure_column_unboxed(py_table, arr_list_{anf__iavrx}, i, arr_ind_{anf__iavrx})
"""
            vdap__zxeml += f"""    cpp_arr_list[out_arr_ind_{anf__iavrx}] = array_to_info(arr_list_{anf__iavrx}[i])
"""
        for jvrx__ajyx, ivg__thotm in hlgc__ulqg.items():
            if jvrx__ajyx < vqez__mfv:
                anf__iavrx = py_table.block_nums[jvrx__ajyx]
                jqd__ajofg = py_table.block_offsets[jvrx__ajyx]
                for iofti__ipik in ivg__thotm:
                    vdap__zxeml += f"""  cpp_arr_list[{iofti__ipik}] = array_to_info(arr_list_{anf__iavrx}[{jqd__ajofg}])
"""
    for apcca__shwxe in range(len(extra_arrs_tup)):
        losyh__hrq = lix__kmnbc.get(vqez__mfv + apcca__shwxe, -1)
        if losyh__hrq != -1:
            kgkmv__bwqh = [losyh__hrq] + hlgc__ulqg.get(vqez__mfv +
                apcca__shwxe, [])
            for iofti__ipik in kgkmv__bwqh:
                vdap__zxeml += f"""  cpp_arr_list[{iofti__ipik}] = array_to_info(extra_arrs_tup[{apcca__shwxe}])
"""
    vdap__zxeml += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    vbc__fqf.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    xqrc__qehzi = {}
    exec(vdap__zxeml, vbc__fqf, xqrc__qehzi)
    return xqrc__qehzi['impl']


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
        rcvi__body = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='delete_table')
        builder.call(bgyo__sfraj, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='shuffle_table')
        gqmxg__hcked = builder.call(bgyo__sfraj, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return gqmxg__hcked
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
        rcvi__body = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='delete_shuffle_info')
        return builder.call(bgyo__sfraj, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='reverse_shuffle_table')
        return builder.call(bgyo__sfraj, args)
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
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='hash_join_table')
        gqmxg__hcked = builder.call(bgyo__sfraj, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return gqmxg__hcked
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
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='sort_values_table')
        gqmxg__hcked = builder.call(bgyo__sfraj, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return gqmxg__hcked
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='sample_table')
        gqmxg__hcked = builder.call(bgyo__sfraj, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return gqmxg__hcked
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='shuffle_renormalization')
        gqmxg__hcked = builder.call(bgyo__sfraj, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return gqmxg__hcked
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='shuffle_renormalization_group')
        gqmxg__hcked = builder.call(bgyo__sfraj, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return gqmxg__hcked
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='drop_duplicates_table')
        gqmxg__hcked = builder.call(bgyo__sfraj, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return gqmxg__hcked
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
        rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer()])
        bgyo__sfraj = cgutils.get_or_insert_function(builder.module,
            rcvi__body, name='groupby_and_aggregate')
        gqmxg__hcked = builder.call(bgyo__sfraj, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return gqmxg__hcked
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
    cdbha__uods = array_to_info(in_arr)
    khe__zfp = array_to_info(in_values)
    vdekc__ebyen = array_to_info(out_arr)
    gbo__lbjr = arr_info_list_to_table([cdbha__uods, khe__zfp, vdekc__ebyen])
    _array_isin(vdekc__ebyen, cdbha__uods, khe__zfp, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(gbo__lbjr)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    cdbha__uods = array_to_info(in_arr)
    vdekc__ebyen = array_to_info(out_arr)
    _get_search_regex(cdbha__uods, case, match, pat, vdekc__ebyen)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    fap__fbgos = col_array_typ.dtype
    if isinstance(fap__fbgos, types.Number) or fap__fbgos in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                nxhhw__qaa, luwbm__amvei = args
                nxhhw__qaa = builder.bitcast(nxhhw__qaa, lir.IntType(8).
                    as_pointer().as_pointer())
                zgp__fiqgy = lir.Constant(lir.IntType(64), c_ind)
                mthz__vmi = builder.load(builder.gep(nxhhw__qaa, [zgp__fiqgy]))
                mthz__vmi = builder.bitcast(mthz__vmi, context.
                    get_data_type(fap__fbgos).as_pointer())
                return builder.load(builder.gep(mthz__vmi, [luwbm__amvei]))
            return fap__fbgos(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                nxhhw__qaa, luwbm__amvei = args
                nxhhw__qaa = builder.bitcast(nxhhw__qaa, lir.IntType(8).
                    as_pointer().as_pointer())
                zgp__fiqgy = lir.Constant(lir.IntType(64), c_ind)
                mthz__vmi = builder.load(builder.gep(nxhhw__qaa, [zgp__fiqgy]))
                rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                ndm__kqtpb = cgutils.get_or_insert_function(builder.module,
                    rcvi__body, name='array_info_getitem')
                fttfb__omrt = cgutils.alloca_once(builder, lir.IntType(64))
                args = mthz__vmi, luwbm__amvei, fttfb__omrt
                gplsx__oagma = builder.call(ndm__kqtpb, args)
                return context.make_tuple(builder, sig.return_type, [
                    gplsx__oagma, builder.load(fttfb__omrt)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                xiy__aha = lir.Constant(lir.IntType(64), 1)
                eqm__avz = lir.Constant(lir.IntType(64), 2)
                nxhhw__qaa, luwbm__amvei = args
                nxhhw__qaa = builder.bitcast(nxhhw__qaa, lir.IntType(8).
                    as_pointer().as_pointer())
                zgp__fiqgy = lir.Constant(lir.IntType(64), c_ind)
                mthz__vmi = builder.load(builder.gep(nxhhw__qaa, [zgp__fiqgy]))
                rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                edhb__iunfo = cgutils.get_or_insert_function(builder.module,
                    rcvi__body, name='get_nested_info')
                args = mthz__vmi, eqm__avz
                tghyn__lmv = builder.call(edhb__iunfo, args)
                rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                snbe__wwlzh = cgutils.get_or_insert_function(builder.module,
                    rcvi__body, name='array_info_getdata1')
                args = tghyn__lmv,
                glwkb__fjwa = builder.call(snbe__wwlzh, args)
                glwkb__fjwa = builder.bitcast(glwkb__fjwa, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                lhmu__bvh = builder.sext(builder.load(builder.gep(
                    glwkb__fjwa, [luwbm__amvei])), lir.IntType(64))
                args = mthz__vmi, xiy__aha
                ntn__zwkrf = builder.call(edhb__iunfo, args)
                rcvi__body = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                ndm__kqtpb = cgutils.get_or_insert_function(builder.module,
                    rcvi__body, name='array_info_getitem')
                fttfb__omrt = cgutils.alloca_once(builder, lir.IntType(64))
                args = ntn__zwkrf, lhmu__bvh, fttfb__omrt
                gplsx__oagma = builder.call(ndm__kqtpb, args)
                return context.make_tuple(builder, sig.return_type, [
                    gplsx__oagma, builder.load(fttfb__omrt)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{fap__fbgos}' column data type not supported"
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
                ysbbe__gzsff, luwbm__amvei = args
                ysbbe__gzsff = builder.bitcast(ysbbe__gzsff, lir.IntType(8)
                    .as_pointer().as_pointer())
                zgp__fiqgy = lir.Constant(lir.IntType(64), c_ind)
                mthz__vmi = builder.load(builder.gep(ysbbe__gzsff, [
                    zgp__fiqgy]))
                ajto__qwvn = builder.bitcast(mthz__vmi, context.
                    get_data_type(types.bool_).as_pointer())
                bcc__wvfzq = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    ajto__qwvn, luwbm__amvei)
                gmqx__vyvy = builder.icmp_unsigned('!=', bcc__wvfzq, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(gmqx__vyvy, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        fap__fbgos = col_array_dtype.dtype
        if fap__fbgos in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    nxhhw__qaa, luwbm__amvei = args
                    nxhhw__qaa = builder.bitcast(nxhhw__qaa, lir.IntType(8)
                        .as_pointer().as_pointer())
                    zgp__fiqgy = lir.Constant(lir.IntType(64), c_ind)
                    mthz__vmi = builder.load(builder.gep(nxhhw__qaa, [
                        zgp__fiqgy]))
                    mthz__vmi = builder.bitcast(mthz__vmi, context.
                        get_data_type(fap__fbgos).as_pointer())
                    dzt__mvi = builder.load(builder.gep(mthz__vmi, [
                        luwbm__amvei]))
                    gmqx__vyvy = builder.icmp_unsigned('!=', dzt__mvi, lir.
                        Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(gmqx__vyvy, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(fap__fbgos, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    nxhhw__qaa, luwbm__amvei = args
                    nxhhw__qaa = builder.bitcast(nxhhw__qaa, lir.IntType(8)
                        .as_pointer().as_pointer())
                    zgp__fiqgy = lir.Constant(lir.IntType(64), c_ind)
                    mthz__vmi = builder.load(builder.gep(nxhhw__qaa, [
                        zgp__fiqgy]))
                    mthz__vmi = builder.bitcast(mthz__vmi, context.
                        get_data_type(fap__fbgos).as_pointer())
                    dzt__mvi = builder.load(builder.gep(mthz__vmi, [
                        luwbm__amvei]))
                    glmf__nesr = signature(types.bool_, fap__fbgos)
                    bcc__wvfzq = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, glmf__nesr, (dzt__mvi,))
                    return builder.not_(builder.sext(bcc__wvfzq, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
