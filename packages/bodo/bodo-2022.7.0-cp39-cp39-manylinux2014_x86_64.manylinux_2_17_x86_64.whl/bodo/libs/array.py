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
        ltj__kafi = context.make_helper(builder, arr_type, in_arr)
        in_arr = ltj__kafi.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        okho__qxfc = context.make_helper(builder, arr_type, in_arr)
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='list_string_array_to_info')
        return builder.call(pdghq__kyix, [okho__qxfc.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                bfq__copb = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for gcxv__uim in arr_typ.data:
                    bfq__copb += get_types(gcxv__uim)
                return bfq__copb
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
            yoh__vwvmm = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                lwl__ige = context.make_helper(builder, arr_typ, value=arr)
                zklje__pmip = get_lengths(_get_map_arr_data_type(arr_typ),
                    lwl__ige.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                kzgd__hvzi = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                zklje__pmip = get_lengths(arr_typ.dtype, kzgd__hvzi.data)
                zklje__pmip = cgutils.pack_array(builder, [kzgd__hvzi.
                    n_arrays] + [builder.extract_value(zklje__pmip,
                    rpnlb__brd) for rpnlb__brd in range(zklje__pmip.type.
                    count)])
            elif isinstance(arr_typ, StructArrayType):
                kzgd__hvzi = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                zklje__pmip = []
                for rpnlb__brd, gcxv__uim in enumerate(arr_typ.data):
                    xvm__nvqc = get_lengths(gcxv__uim, builder.
                        extract_value(kzgd__hvzi.data, rpnlb__brd))
                    zklje__pmip += [builder.extract_value(xvm__nvqc,
                        zjysf__vpc) for zjysf__vpc in range(xvm__nvqc.type.
                        count)]
                zklje__pmip = cgutils.pack_array(builder, [yoh__vwvmm,
                    context.get_constant(types.int64, -1)] + zklje__pmip)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                zklje__pmip = cgutils.pack_array(builder, [yoh__vwvmm])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return zklje__pmip

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                lwl__ige = context.make_helper(builder, arr_typ, value=arr)
                dfx__jlp = get_buffers(_get_map_arr_data_type(arr_typ),
                    lwl__ige.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                kzgd__hvzi = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                whyfq__yltes = get_buffers(arr_typ.dtype, kzgd__hvzi.data)
                cmh__nsk = context.make_array(types.Array(offset_type, 1, 'C')
                    )(context, builder, kzgd__hvzi.offsets)
                eyq__fnp = builder.bitcast(cmh__nsk.data, lir.IntType(8).
                    as_pointer())
                cfb__junjy = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, kzgd__hvzi.null_bitmap)
                qyvbp__tjt = builder.bitcast(cfb__junjy.data, lir.IntType(8
                    ).as_pointer())
                dfx__jlp = cgutils.pack_array(builder, [eyq__fnp,
                    qyvbp__tjt] + [builder.extract_value(whyfq__yltes,
                    rpnlb__brd) for rpnlb__brd in range(whyfq__yltes.type.
                    count)])
            elif isinstance(arr_typ, StructArrayType):
                kzgd__hvzi = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                whyfq__yltes = []
                for rpnlb__brd, gcxv__uim in enumerate(arr_typ.data):
                    kjw__inzqi = get_buffers(gcxv__uim, builder.
                        extract_value(kzgd__hvzi.data, rpnlb__brd))
                    whyfq__yltes += [builder.extract_value(kjw__inzqi,
                        zjysf__vpc) for zjysf__vpc in range(kjw__inzqi.type
                        .count)]
                cfb__junjy = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, kzgd__hvzi.null_bitmap)
                qyvbp__tjt = builder.bitcast(cfb__junjy.data, lir.IntType(8
                    ).as_pointer())
                dfx__jlp = cgutils.pack_array(builder, [qyvbp__tjt] +
                    whyfq__yltes)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                bnw__tzrf = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    bnw__tzrf = int128_type
                elif arr_typ == datetime_date_array_type:
                    bnw__tzrf = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                jenww__ltby = context.make_array(types.Array(bnw__tzrf, 1, 'C')
                    )(context, builder, arr.data)
                cfb__junjy = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, arr.null_bitmap)
                styp__kym = builder.bitcast(jenww__ltby.data, lir.IntType(8
                    ).as_pointer())
                qyvbp__tjt = builder.bitcast(cfb__junjy.data, lir.IntType(8
                    ).as_pointer())
                dfx__jlp = cgutils.pack_array(builder, [qyvbp__tjt, styp__kym])
            elif arr_typ in (string_array_type, binary_array_type):
                kzgd__hvzi = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                ere__bex = context.make_helper(builder, offset_arr_type,
                    kzgd__hvzi.offsets).data
                hhkt__vop = context.make_helper(builder, char_arr_type,
                    kzgd__hvzi.data).data
                johs__tiw = context.make_helper(builder,
                    null_bitmap_arr_type, kzgd__hvzi.null_bitmap).data
                dfx__jlp = cgutils.pack_array(builder, [builder.bitcast(
                    ere__bex, lir.IntType(8).as_pointer()), builder.bitcast
                    (johs__tiw, lir.IntType(8).as_pointer()), builder.
                    bitcast(hhkt__vop, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                styp__kym = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                snij__coapx = lir.Constant(lir.IntType(8).as_pointer(), None)
                dfx__jlp = cgutils.pack_array(builder, [snij__coapx, styp__kym]
                    )
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return dfx__jlp

        def get_field_names(arr_typ):
            rvi__ofji = []
            if isinstance(arr_typ, StructArrayType):
                for hczzf__debj, xeojr__jxqg in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    rvi__ofji.append(hczzf__debj)
                    rvi__ofji += get_field_names(xeojr__jxqg)
            elif isinstance(arr_typ, ArrayItemArrayType):
                rvi__ofji += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                rvi__ofji += get_field_names(_get_map_arr_data_type(arr_typ))
            return rvi__ofji
        bfq__copb = get_types(arr_type)
        spwaq__nsj = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in bfq__copb])
        bif__oncyk = cgutils.alloca_once_value(builder, spwaq__nsj)
        zklje__pmip = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, zklje__pmip)
        dfx__jlp = get_buffers(arr_type, in_arr)
        etif__tkniy = cgutils.alloca_once_value(builder, dfx__jlp)
        rvi__ofji = get_field_names(arr_type)
        if len(rvi__ofji) == 0:
            rvi__ofji = ['irrelevant']
        eny__pcj = cgutils.pack_array(builder, [context.insert_const_string
            (builder.module, a) for a in rvi__ofji])
        buzpz__oxl = cgutils.alloca_once_value(builder, eny__pcj)
        if isinstance(arr_type, MapArrayType):
            uqhhv__hbi = _get_map_arr_data_type(arr_type)
            cns__xyfq = context.make_helper(builder, arr_type, value=in_arr)
            wtk__mabm = cns__xyfq.data
        else:
            uqhhv__hbi = arr_type
            wtk__mabm = in_arr
        yfn__hru = context.make_helper(builder, uqhhv__hbi, wtk__mabm)
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='nested_array_to_info')
        plbk__axwsl = builder.call(pdghq__kyix, [builder.bitcast(bif__oncyk,
            lir.IntType(32).as_pointer()), builder.bitcast(etif__tkniy, lir
            .IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            buzpz__oxl, lir.IntType(8).as_pointer()), yfn__hru.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return plbk__axwsl
    if arr_type in (string_array_type, binary_array_type):
        jabc__qszda = context.make_helper(builder, arr_type, in_arr)
        plop__oyviz = ArrayItemArrayType(char_arr_type)
        okho__qxfc = context.make_helper(builder, plop__oyviz, jabc__qszda.data
            )
        kzgd__hvzi = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        ere__bex = context.make_helper(builder, offset_arr_type, kzgd__hvzi
            .offsets).data
        hhkt__vop = context.make_helper(builder, char_arr_type, kzgd__hvzi.data
            ).data
        johs__tiw = context.make_helper(builder, null_bitmap_arr_type,
            kzgd__hvzi.null_bitmap).data
        faokm__vuv = builder.zext(builder.load(builder.gep(ere__bex, [
            kzgd__hvzi.n_arrays])), lir.IntType(64))
        hkffd__rua = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='string_array_to_info')
        return builder.call(pdghq__kyix, [kzgd__hvzi.n_arrays, faokm__vuv,
            hhkt__vop, ere__bex, johs__tiw, okho__qxfc.meminfo, hkffd__rua])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        kol__ukbcn = arr.data
        tzs__pbwdu = arr.indices
        sig = array_info_type(arr_type.data)
        fbic__ztku = array_to_info_codegen(context, builder, sig, (
            kol__ukbcn,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        iohuk__qgyh = array_to_info_codegen(context, builder, sig, (
            tzs__pbwdu,), False)
        rtppy__aqafb = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, tzs__pbwdu)
        qyvbp__tjt = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, rtppy__aqafb.null_bitmap).data
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='dict_str_array_to_info')
        qcbf__ggja = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(pdghq__kyix, [fbic__ztku, iohuk__qgyh, builder.
            bitcast(qyvbp__tjt, lir.IntType(8).as_pointer()), qcbf__ggja])
    psyct__dxrg = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        yfh__riry = context.compile_internal(builder, lambda a: len(a.dtype
            .categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        wxd__gkua = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(wxd__gkua, 1, 'C')
        psyct__dxrg = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if psyct__dxrg:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        yoh__vwvmm = builder.extract_value(arr.shape, 0)
        iorud__mkyjn = arr_type.dtype
        nvr__ndcmb = numba_to_c_type(iorud__mkyjn)
        zmwl__xrrzy = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), nvr__ndcmb))
        if psyct__dxrg:
            caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(64), lir.IntType(8).as_pointer()])
            pdghq__kyix = cgutils.get_or_insert_function(builder.module,
                caiag__mkfia, name='categorical_array_to_info')
            return builder.call(pdghq__kyix, [yoh__vwvmm, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                zmwl__xrrzy), yfh__riry, arr.meminfo])
        else:
            caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer()])
            pdghq__kyix = cgutils.get_or_insert_function(builder.module,
                caiag__mkfia, name='numpy_array_to_info')
            return builder.call(pdghq__kyix, [yoh__vwvmm, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                zmwl__xrrzy), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        iorud__mkyjn = arr_type.dtype
        bnw__tzrf = iorud__mkyjn
        if isinstance(arr_type, DecimalArrayType):
            bnw__tzrf = int128_type
        if arr_type == datetime_date_array_type:
            bnw__tzrf = types.int64
        jenww__ltby = context.make_array(types.Array(bnw__tzrf, 1, 'C'))(
            context, builder, arr.data)
        yoh__vwvmm = builder.extract_value(jenww__ltby.shape, 0)
        tvh__xcd = context.make_array(types.Array(types.uint8, 1, 'C'))(context
            , builder, arr.null_bitmap)
        nvr__ndcmb = numba_to_c_type(iorud__mkyjn)
        zmwl__xrrzy = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), nvr__ndcmb))
        if isinstance(arr_type, DecimalArrayType):
            caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer(), lir.IntType(32), lir.
                IntType(32)])
            pdghq__kyix = cgutils.get_or_insert_function(builder.module,
                caiag__mkfia, name='decimal_array_to_info')
            return builder.call(pdghq__kyix, [yoh__vwvmm, builder.bitcast(
                jenww__ltby.data, lir.IntType(8).as_pointer()), builder.
                load(zmwl__xrrzy), builder.bitcast(tvh__xcd.data, lir.
                IntType(8).as_pointer()), jenww__ltby.meminfo, tvh__xcd.
                meminfo, context.get_constant(types.int32, arr_type.
                precision), context.get_constant(types.int32, arr_type.scale)])
        else:
            caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer()])
            pdghq__kyix = cgutils.get_or_insert_function(builder.module,
                caiag__mkfia, name='nullable_array_to_info')
            return builder.call(pdghq__kyix, [yoh__vwvmm, builder.bitcast(
                jenww__ltby.data, lir.IntType(8).as_pointer()), builder.
                load(zmwl__xrrzy), builder.bitcast(tvh__xcd.data, lir.
                IntType(8).as_pointer()), jenww__ltby.meminfo, tvh__xcd.
                meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        rprda__zgvg = context.make_array(arr_type.arr_type)(context,
            builder, arr.left)
        xza__ema = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        yoh__vwvmm = builder.extract_value(rprda__zgvg.shape, 0)
        nvr__ndcmb = numba_to_c_type(arr_type.arr_type.dtype)
        zmwl__xrrzy = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), nvr__ndcmb))
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='interval_array_to_info')
        return builder.call(pdghq__kyix, [yoh__vwvmm, builder.bitcast(
            rprda__zgvg.data, lir.IntType(8).as_pointer()), builder.bitcast
            (xza__ema.data, lir.IntType(8).as_pointer()), builder.load(
            zmwl__xrrzy), rprda__zgvg.meminfo, xza__ema.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    yquy__wzkhp = cgutils.alloca_once(builder, lir.IntType(64))
    styp__kym = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    tnpqm__tjrio = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    caiag__mkfia = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    pdghq__kyix = cgutils.get_or_insert_function(builder.module,
        caiag__mkfia, name='info_to_numpy_array')
    builder.call(pdghq__kyix, [in_info, yquy__wzkhp, styp__kym, tnpqm__tjrio])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    msz__mdub = context.get_value_type(types.intp)
    cpz__dqlu = cgutils.pack_array(builder, [builder.load(yquy__wzkhp)], ty
        =msz__mdub)
    pvs__kwnud = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    gkdrl__oie = cgutils.pack_array(builder, [pvs__kwnud], ty=msz__mdub)
    hhkt__vop = builder.bitcast(builder.load(styp__kym), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=hhkt__vop, shape=cpz__dqlu,
        strides=gkdrl__oie, itemsize=pvs__kwnud, meminfo=builder.load(
        tnpqm__tjrio))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    rxtgb__iav = context.make_helper(builder, arr_type)
    caiag__mkfia = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    pdghq__kyix = cgutils.get_or_insert_function(builder.module,
        caiag__mkfia, name='info_to_list_string_array')
    builder.call(pdghq__kyix, [in_info, rxtgb__iav._get_ptr_by_name('meminfo')]
        )
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return rxtgb__iav._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    dmwm__jrzxp = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        euiu__wayx = lengths_pos
        xmw__vazvf = infos_pos
        bbh__bds, lengths_pos, infos_pos = nested_to_array(context, builder,
            arr_typ.dtype, lengths_ptr, array_infos_ptr, lengths_pos + 1, 
            infos_pos + 2)
        hydbm__rzt = ArrayItemArrayPayloadType(arr_typ)
        naajt__yoq = context.get_data_type(hydbm__rzt)
        xrr__lkhuo = context.get_abi_sizeof(naajt__yoq)
        kkwmv__ioxr = define_array_item_dtor(context, builder, arr_typ,
            hydbm__rzt)
        rqng__cijf = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, xrr__lkhuo), kkwmv__ioxr)
        exnrq__exjgz = context.nrt.meminfo_data(builder, rqng__cijf)
        gdryr__jbhc = builder.bitcast(exnrq__exjgz, naajt__yoq.as_pointer())
        kzgd__hvzi = cgutils.create_struct_proxy(hydbm__rzt)(context, builder)
        kzgd__hvzi.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), euiu__wayx)
        kzgd__hvzi.data = bbh__bds
        vmh__aje = builder.load(array_infos_ptr)
        yyxf__viy = builder.bitcast(builder.extract_value(vmh__aje,
            xmw__vazvf), dmwm__jrzxp)
        kzgd__hvzi.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, yyxf__viy)
        kdsd__puij = builder.bitcast(builder.extract_value(vmh__aje, 
            xmw__vazvf + 1), dmwm__jrzxp)
        kzgd__hvzi.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, kdsd__puij)
        builder.store(kzgd__hvzi._getvalue(), gdryr__jbhc)
        okho__qxfc = context.make_helper(builder, arr_typ)
        okho__qxfc.meminfo = rqng__cijf
        return okho__qxfc._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        qsoy__wgh = []
        xmw__vazvf = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for bqesb__igy in arr_typ.data:
            bbh__bds, lengths_pos, infos_pos = nested_to_array(context,
                builder, bqesb__igy, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            qsoy__wgh.append(bbh__bds)
        hydbm__rzt = StructArrayPayloadType(arr_typ.data)
        naajt__yoq = context.get_value_type(hydbm__rzt)
        xrr__lkhuo = context.get_abi_sizeof(naajt__yoq)
        kkwmv__ioxr = define_struct_arr_dtor(context, builder, arr_typ,
            hydbm__rzt)
        rqng__cijf = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, xrr__lkhuo), kkwmv__ioxr)
        exnrq__exjgz = context.nrt.meminfo_data(builder, rqng__cijf)
        gdryr__jbhc = builder.bitcast(exnrq__exjgz, naajt__yoq.as_pointer())
        kzgd__hvzi = cgutils.create_struct_proxy(hydbm__rzt)(context, builder)
        kzgd__hvzi.data = cgutils.pack_array(builder, qsoy__wgh
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, qsoy__wgh)
        vmh__aje = builder.load(array_infos_ptr)
        kdsd__puij = builder.bitcast(builder.extract_value(vmh__aje,
            xmw__vazvf), dmwm__jrzxp)
        kzgd__hvzi.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, kdsd__puij)
        builder.store(kzgd__hvzi._getvalue(), gdryr__jbhc)
        cps__lfuq = context.make_helper(builder, arr_typ)
        cps__lfuq.meminfo = rqng__cijf
        return cps__lfuq._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        vmh__aje = builder.load(array_infos_ptr)
        pez__tiol = builder.bitcast(builder.extract_value(vmh__aje,
            infos_pos), dmwm__jrzxp)
        jabc__qszda = context.make_helper(builder, arr_typ)
        plop__oyviz = ArrayItemArrayType(char_arr_type)
        okho__qxfc = context.make_helper(builder, plop__oyviz)
        caiag__mkfia = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='info_to_string_array')
        builder.call(pdghq__kyix, [pez__tiol, okho__qxfc._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        jabc__qszda.data = okho__qxfc._getvalue()
        return jabc__qszda._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        vmh__aje = builder.load(array_infos_ptr)
        zls__rskl = builder.bitcast(builder.extract_value(vmh__aje, 
            infos_pos + 1), dmwm__jrzxp)
        return _lower_info_to_array_numpy(arr_typ, context, builder, zls__rskl
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        bnw__tzrf = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            bnw__tzrf = int128_type
        elif arr_typ == datetime_date_array_type:
            bnw__tzrf = types.int64
        vmh__aje = builder.load(array_infos_ptr)
        kdsd__puij = builder.bitcast(builder.extract_value(vmh__aje,
            infos_pos), dmwm__jrzxp)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, kdsd__puij)
        zls__rskl = builder.bitcast(builder.extract_value(vmh__aje, 
            infos_pos + 1), dmwm__jrzxp)
        arr.data = _lower_info_to_array_numpy(types.Array(bnw__tzrf, 1, 'C'
            ), context, builder, zls__rskl)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, nxgso__lwfmt = args
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
                return 1 + sum([get_num_arrays(bqesb__igy) for bqesb__igy in
                    arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(bqesb__igy) for bqesb__igy in
                    arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            vysk__ywv = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            vysk__ywv = _get_map_arr_data_type(arr_type)
        else:
            vysk__ywv = arr_type
        wuzjc__zao = get_num_arrays(vysk__ywv)
        zklje__pmip = cgutils.pack_array(builder, [lir.Constant(lir.IntType
            (64), 0) for nxgso__lwfmt in range(wuzjc__zao)])
        lengths_ptr = cgutils.alloca_once_value(builder, zklje__pmip)
        snij__coapx = lir.Constant(lir.IntType(8).as_pointer(), None)
        skkr__rzhx = cgutils.pack_array(builder, [snij__coapx for
            nxgso__lwfmt in range(get_num_infos(vysk__ywv))])
        array_infos_ptr = cgutils.alloca_once_value(builder, skkr__rzhx)
        caiag__mkfia = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='info_to_nested_array')
        builder.call(pdghq__kyix, [in_info, builder.bitcast(lengths_ptr,
            lir.IntType(64).as_pointer()), builder.bitcast(array_infos_ptr,
            lir.IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, nxgso__lwfmt, nxgso__lwfmt = nested_to_array(context, builder,
            vysk__ywv, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            ltj__kafi = context.make_helper(builder, arr_type)
            ltj__kafi.data = arr
            context.nrt.incref(builder, vysk__ywv, arr)
            arr = ltj__kafi._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, vysk__ywv)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        jabc__qszda = context.make_helper(builder, arr_type)
        plop__oyviz = ArrayItemArrayType(char_arr_type)
        okho__qxfc = context.make_helper(builder, plop__oyviz)
        caiag__mkfia = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='info_to_string_array')
        builder.call(pdghq__kyix, [in_info, okho__qxfc._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        jabc__qszda.data = okho__qxfc._getvalue()
        return jabc__qszda._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='get_nested_info')
        fbic__ztku = builder.call(pdghq__kyix, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        iohuk__qgyh = builder.call(pdghq__kyix, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        oiqks__vhtzy = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        oiqks__vhtzy.data = info_to_array_codegen(context, builder, sig, (
            fbic__ztku, context.get_constant_null(arr_type.data)))
        rmb__rvsr = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = rmb__rvsr(array_info_type, rmb__rvsr)
        oiqks__vhtzy.indices = info_to_array_codegen(context, builder, sig,
            (iohuk__qgyh, context.get_constant_null(rmb__rvsr)))
        caiag__mkfia = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='get_has_global_dictionary')
        qcbf__ggja = builder.call(pdghq__kyix, [in_info])
        oiqks__vhtzy.has_global_dictionary = builder.trunc(qcbf__ggja,
            cgutils.bool_t)
        return oiqks__vhtzy._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        wxd__gkua = get_categories_int_type(arr_type.dtype)
        khbya__vvrp = types.Array(wxd__gkua, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(khbya__vvrp, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            mmeu__unpt = bodo.utils.utils.create_categorical_type(arr_type.
                dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(mmeu__unpt))
            int_type = arr_type.dtype.int_type
            npx__qfh = arr_type.dtype.data.data
            wob__otd = context.get_constant_generic(builder, npx__qfh,
                mmeu__unpt)
            iorud__mkyjn = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(npx__qfh), [wob__otd])
        else:
            iorud__mkyjn = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, iorud__mkyjn)
        out_arr.dtype = iorud__mkyjn
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        hhkt__vop = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = hhkt__vop
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        bnw__tzrf = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            bnw__tzrf = int128_type
        elif arr_type == datetime_date_array_type:
            bnw__tzrf = types.int64
        utyr__bpd = types.Array(bnw__tzrf, 1, 'C')
        jenww__ltby = context.make_array(utyr__bpd)(context, builder)
        bdmm__avxk = types.Array(types.uint8, 1, 'C')
        mlzq__hjvbn = context.make_array(bdmm__avxk)(context, builder)
        yquy__wzkhp = cgutils.alloca_once(builder, lir.IntType(64))
        ozl__vwtpg = cgutils.alloca_once(builder, lir.IntType(64))
        styp__kym = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        wrpq__zzov = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        tnpqm__tjrio = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
            )
        wsa__zxddh = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        caiag__mkfia = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='info_to_nullable_array')
        builder.call(pdghq__kyix, [in_info, yquy__wzkhp, ozl__vwtpg,
            styp__kym, wrpq__zzov, tnpqm__tjrio, wsa__zxddh])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        msz__mdub = context.get_value_type(types.intp)
        cpz__dqlu = cgutils.pack_array(builder, [builder.load(yquy__wzkhp)],
            ty=msz__mdub)
        pvs__kwnud = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(bnw__tzrf)))
        gkdrl__oie = cgutils.pack_array(builder, [pvs__kwnud], ty=msz__mdub)
        hhkt__vop = builder.bitcast(builder.load(styp__kym), context.
            get_data_type(bnw__tzrf).as_pointer())
        numba.np.arrayobj.populate_array(jenww__ltby, data=hhkt__vop, shape
            =cpz__dqlu, strides=gkdrl__oie, itemsize=pvs__kwnud, meminfo=
            builder.load(tnpqm__tjrio))
        arr.data = jenww__ltby._getvalue()
        cpz__dqlu = cgutils.pack_array(builder, [builder.load(ozl__vwtpg)],
            ty=msz__mdub)
        pvs__kwnud = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(types.uint8)))
        gkdrl__oie = cgutils.pack_array(builder, [pvs__kwnud], ty=msz__mdub)
        hhkt__vop = builder.bitcast(builder.load(wrpq__zzov), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(mlzq__hjvbn, data=hhkt__vop, shape
            =cpz__dqlu, strides=gkdrl__oie, itemsize=pvs__kwnud, meminfo=
            builder.load(wsa__zxddh))
        arr.null_bitmap = mlzq__hjvbn._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        rprda__zgvg = context.make_array(arr_type.arr_type)(context, builder)
        xza__ema = context.make_array(arr_type.arr_type)(context, builder)
        yquy__wzkhp = cgutils.alloca_once(builder, lir.IntType(64))
        pbsq__dor = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        onlx__eclt = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        stytz__iqwhq = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
            )
        tihii__ixhd = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        caiag__mkfia = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='info_to_interval_array')
        builder.call(pdghq__kyix, [in_info, yquy__wzkhp, pbsq__dor,
            onlx__eclt, stytz__iqwhq, tihii__ixhd])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        msz__mdub = context.get_value_type(types.intp)
        cpz__dqlu = cgutils.pack_array(builder, [builder.load(yquy__wzkhp)],
            ty=msz__mdub)
        pvs__kwnud = context.get_constant(types.intp, context.
            get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
        gkdrl__oie = cgutils.pack_array(builder, [pvs__kwnud], ty=msz__mdub)
        rgt__bpv = builder.bitcast(builder.load(pbsq__dor), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(rprda__zgvg, data=rgt__bpv, shape=
            cpz__dqlu, strides=gkdrl__oie, itemsize=pvs__kwnud, meminfo=
            builder.load(stytz__iqwhq))
        arr.left = rprda__zgvg._getvalue()
        fbuv__rtssp = builder.bitcast(builder.load(onlx__eclt), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(xza__ema, data=fbuv__rtssp, shape=
            cpz__dqlu, strides=gkdrl__oie, itemsize=pvs__kwnud, meminfo=
            builder.load(tihii__ixhd))
        arr.right = xza__ema._getvalue()
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
        yoh__vwvmm, nxgso__lwfmt = args
        nvr__ndcmb = numba_to_c_type(array_type.dtype)
        zmwl__xrrzy = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), nvr__ndcmb))
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='alloc_numpy')
        return builder.call(pdghq__kyix, [yoh__vwvmm, builder.load(
            zmwl__xrrzy)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        yoh__vwvmm, fccn__wykf = args
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='alloc_string_array')
        return builder.call(pdghq__kyix, [yoh__vwvmm, fccn__wykf])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    ndo__kpea, = args
    xmjyj__nrm = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], ndo__kpea)
    caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer().as_pointer(), lir.IntType(64)])
    pdghq__kyix = cgutils.get_or_insert_function(builder.module,
        caiag__mkfia, name='arr_info_list_to_table')
    return builder.call(pdghq__kyix, [xmjyj__nrm.data, xmjyj__nrm.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='info_from_table')
        return builder.call(pdghq__kyix, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    ghmpr__snpj = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, tnsyh__xppp, nxgso__lwfmt = args
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='info_from_table')
        twm__jbfi = cgutils.create_struct_proxy(ghmpr__snpj)(context, builder)
        twm__jbfi.parent = cgutils.get_null_value(twm__jbfi.parent.type)
        mlzez__shnfu = context.make_array(table_idx_arr_t)(context, builder,
            tnsyh__xppp)
        dwcr__atn = context.get_constant(types.int64, -1)
        vblbo__eqen = context.get_constant(types.int64, 0)
        xrw__rmnfl = cgutils.alloca_once_value(builder, vblbo__eqen)
        for t, qkdal__vwnee in ghmpr__snpj.type_to_blk.items():
            zwk__cmxu = context.get_constant(types.int64, len(ghmpr__snpj.
                block_to_arr_ind[qkdal__vwnee]))
            nxgso__lwfmt, dwt__kzof = ListInstance.allocate_ex(context,
                builder, types.List(t), zwk__cmxu)
            dwt__kzof.size = zwk__cmxu
            aez__ayuc = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(ghmpr__snpj.block_to_arr_ind
                [qkdal__vwnee], dtype=np.int64))
            helw__hiiv = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, aez__ayuc)
            with cgutils.for_range(builder, zwk__cmxu) as bsrli__hxhc:
                rpnlb__brd = bsrli__hxhc.index
                uqcf__kmcbr = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    helw__hiiv, rpnlb__brd)
                ssyp__glpka = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, mlzez__shnfu, uqcf__kmcbr)
                egru__xbeln = builder.icmp_unsigned('!=', ssyp__glpka,
                    dwcr__atn)
                with builder.if_else(egru__xbeln) as (ageak__ncas, ozr__zautj):
                    with ageak__ncas:
                        pdy__ypc = builder.call(pdghq__kyix, [cpp_table,
                            ssyp__glpka])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            pdy__ypc])
                        dwt__kzof.inititem(rpnlb__brd, arr, incref=False)
                        yoh__vwvmm = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(yoh__vwvmm, xrw__rmnfl)
                    with ozr__zautj:
                        gqvw__uvmz = context.get_constant_null(t)
                        dwt__kzof.inititem(rpnlb__brd, gqvw__uvmz, incref=False
                            )
            setattr(twm__jbfi, f'block_{qkdal__vwnee}', dwt__kzof.value)
        twm__jbfi.len = builder.load(xrw__rmnfl)
        return twm__jbfi._getvalue()
    return ghmpr__snpj(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    dktap__ztng = out_col_inds_t.instance_type.meta
    ghmpr__snpj = unwrap_typeref(out_types_t.types[0])
    lial__uab = [unwrap_typeref(out_types_t.types[rpnlb__brd]) for
        rpnlb__brd in range(1, len(out_types_t.types))]
    mdp__lxeu = {}
    aemum__ewz = get_overload_const_int(n_table_cols_t)
    yxsh__yrdg = {ywon__rxaub: rpnlb__brd for rpnlb__brd, ywon__rxaub in
        enumerate(dktap__ztng)}
    if not is_overload_none(unknown_cat_arrs_t):
        zbu__udul = {fmk__coi: rpnlb__brd for rpnlb__brd, fmk__coi in
            enumerate(cat_inds_t.instance_type.meta)}
    hgi__xehj = []
    fwfxa__rcsj = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(ghmpr__snpj, bodo.TableType):
        fwfxa__rcsj += f'  py_table = init_table(py_table_type, False)\n'
        fwfxa__rcsj += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for pgjz__ffnke, qkdal__vwnee in ghmpr__snpj.type_to_blk.items():
            seypw__jmn = [yxsh__yrdg.get(rpnlb__brd, -1) for rpnlb__brd in
                ghmpr__snpj.block_to_arr_ind[qkdal__vwnee]]
            mdp__lxeu[f'out_inds_{qkdal__vwnee}'] = np.array(seypw__jmn, np
                .int64)
            mdp__lxeu[f'out_type_{qkdal__vwnee}'] = pgjz__ffnke
            mdp__lxeu[f'typ_list_{qkdal__vwnee}'] = types.List(pgjz__ffnke)
            edi__euidm = f'out_type_{qkdal__vwnee}'
            if type_has_unknown_cats(pgjz__ffnke):
                if is_overload_none(unknown_cat_arrs_t):
                    fwfxa__rcsj += f"""  in_arr_list_{qkdal__vwnee} = get_table_block(out_types_t[0], {qkdal__vwnee})
"""
                    edi__euidm = f'in_arr_list_{qkdal__vwnee}[i]'
                else:
                    mdp__lxeu[f'cat_arr_inds_{qkdal__vwnee}'] = np.array([
                        zbu__udul.get(rpnlb__brd, -1) for rpnlb__brd in
                        ghmpr__snpj.block_to_arr_ind[qkdal__vwnee]], np.int64)
                    edi__euidm = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{qkdal__vwnee}[i]]')
            zwk__cmxu = len(ghmpr__snpj.block_to_arr_ind[qkdal__vwnee])
            fwfxa__rcsj += f"""  arr_list_{qkdal__vwnee} = alloc_list_like(typ_list_{qkdal__vwnee}, {zwk__cmxu}, False)
"""
            fwfxa__rcsj += f'  for i in range(len(arr_list_{qkdal__vwnee})):\n'
            fwfxa__rcsj += (
                f'    cpp_ind_{qkdal__vwnee} = out_inds_{qkdal__vwnee}[i]\n')
            fwfxa__rcsj += f'    if cpp_ind_{qkdal__vwnee} == -1:\n'
            fwfxa__rcsj += f'      continue\n'
            fwfxa__rcsj += f"""    arr_{qkdal__vwnee} = info_to_array(info_from_table(cpp_table, cpp_ind_{qkdal__vwnee}), {edi__euidm})
"""
            fwfxa__rcsj += (
                f'    arr_list_{qkdal__vwnee}[i] = arr_{qkdal__vwnee}\n')
            fwfxa__rcsj += f"""  py_table = set_table_block(py_table, arr_list_{qkdal__vwnee}, {qkdal__vwnee})
"""
        hgi__xehj.append('py_table')
    elif ghmpr__snpj != types.none:
        qslu__whiq = yxsh__yrdg.get(0, -1)
        if qslu__whiq != -1:
            mdp__lxeu[f'arr_typ_arg0'] = ghmpr__snpj
            edi__euidm = f'arr_typ_arg0'
            if type_has_unknown_cats(ghmpr__snpj):
                if is_overload_none(unknown_cat_arrs_t):
                    edi__euidm = f'out_types_t[0]'
                else:
                    edi__euidm = f'unknown_cat_arrs_t[{zbu__udul[0]}]'
            fwfxa__rcsj += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {qslu__whiq}), {edi__euidm})
"""
            hgi__xehj.append('out_arg0')
    for rpnlb__brd, t in enumerate(lial__uab):
        qslu__whiq = yxsh__yrdg.get(aemum__ewz + rpnlb__brd, -1)
        if qslu__whiq != -1:
            mdp__lxeu[f'extra_arr_type_{rpnlb__brd}'] = t
            edi__euidm = f'extra_arr_type_{rpnlb__brd}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    edi__euidm = f'out_types_t[{rpnlb__brd + 1}]'
                else:
                    edi__euidm = (
                        f'unknown_cat_arrs_t[{zbu__udul[aemum__ewz + rpnlb__brd]}]'
                        )
            fwfxa__rcsj += f"""  out_{rpnlb__brd} = info_to_array(info_from_table(cpp_table, {qslu__whiq}), {edi__euidm})
"""
            hgi__xehj.append(f'out_{rpnlb__brd}')
    hlf__zqxin = ',' if len(hgi__xehj) == 1 else ''
    fwfxa__rcsj += f"  return ({', '.join(hgi__xehj)}{hlf__zqxin})\n"
    mdp__lxeu.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(dktap__ztng), 'py_table_type': ghmpr__snpj})
    pmia__tyctd = {}
    exec(fwfxa__rcsj, mdp__lxeu, pmia__tyctd)
    return pmia__tyctd['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    ghmpr__snpj = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, nxgso__lwfmt = args
        ayj__nmuzx = cgutils.create_struct_proxy(ghmpr__snpj)(context,
            builder, py_table)
        if ghmpr__snpj.has_runtime_cols:
            ebv__iqc = lir.Constant(lir.IntType(64), 0)
            for qkdal__vwnee, t in enumerate(ghmpr__snpj.arr_types):
                qijqz__sri = getattr(ayj__nmuzx, f'block_{qkdal__vwnee}')
                pouno__cqyh = ListInstance(context, builder, types.List(t),
                    qijqz__sri)
                ebv__iqc = builder.add(ebv__iqc, pouno__cqyh.size)
        else:
            ebv__iqc = lir.Constant(lir.IntType(64), len(ghmpr__snpj.arr_types)
                )
        nxgso__lwfmt, lejk__hjk = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), ebv__iqc)
        lejk__hjk.size = ebv__iqc
        if ghmpr__snpj.has_runtime_cols:
            cxb__ocinb = lir.Constant(lir.IntType(64), 0)
            for qkdal__vwnee, t in enumerate(ghmpr__snpj.arr_types):
                qijqz__sri = getattr(ayj__nmuzx, f'block_{qkdal__vwnee}')
                pouno__cqyh = ListInstance(context, builder, types.List(t),
                    qijqz__sri)
                zwk__cmxu = pouno__cqyh.size
                with cgutils.for_range(builder, zwk__cmxu) as bsrli__hxhc:
                    rpnlb__brd = bsrli__hxhc.index
                    arr = pouno__cqyh.getitem(rpnlb__brd)
                    ssamr__fdqr = signature(array_info_type, t)
                    ksp__csl = arr,
                    gmknu__eyzi = array_to_info_codegen(context, builder,
                        ssamr__fdqr, ksp__csl)
                    lejk__hjk.inititem(builder.add(cxb__ocinb, rpnlb__brd),
                        gmknu__eyzi, incref=False)
                cxb__ocinb = builder.add(cxb__ocinb, zwk__cmxu)
        else:
            for t, qkdal__vwnee in ghmpr__snpj.type_to_blk.items():
                zwk__cmxu = context.get_constant(types.int64, len(
                    ghmpr__snpj.block_to_arr_ind[qkdal__vwnee]))
                qijqz__sri = getattr(ayj__nmuzx, f'block_{qkdal__vwnee}')
                pouno__cqyh = ListInstance(context, builder, types.List(t),
                    qijqz__sri)
                aez__ayuc = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(ghmpr__snpj.
                    block_to_arr_ind[qkdal__vwnee], dtype=np.int64))
                helw__hiiv = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, aez__ayuc)
                with cgutils.for_range(builder, zwk__cmxu) as bsrli__hxhc:
                    rpnlb__brd = bsrli__hxhc.index
                    uqcf__kmcbr = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), helw__hiiv, rpnlb__brd)
                    mdx__zon = signature(types.none, ghmpr__snpj, types.
                        List(t), types.int64, types.int64)
                    rbru__zosom = py_table, qijqz__sri, rpnlb__brd, uqcf__kmcbr
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, mdx__zon, rbru__zosom)
                    arr = pouno__cqyh.getitem(rpnlb__brd)
                    ssamr__fdqr = signature(array_info_type, t)
                    ksp__csl = arr,
                    gmknu__eyzi = array_to_info_codegen(context, builder,
                        ssamr__fdqr, ksp__csl)
                    lejk__hjk.inititem(uqcf__kmcbr, gmknu__eyzi, incref=False)
        klqo__fdkra = lejk__hjk.value
        mprd__zbsd = signature(table_type, types.List(array_info_type))
        putm__lfg = klqo__fdkra,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            mprd__zbsd, putm__lfg)
        context.nrt.decref(builder, types.List(array_info_type), klqo__fdkra)
        return cpp_table
    return table_type(ghmpr__snpj, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    efx__dtcil = in_col_inds_t.instance_type.meta
    mdp__lxeu = {}
    aemum__ewz = get_overload_const_int(n_table_cols_t)
    drms__qdids = defaultdict(list)
    yxsh__yrdg = {}
    for rpnlb__brd, ywon__rxaub in enumerate(efx__dtcil):
        if ywon__rxaub in yxsh__yrdg:
            drms__qdids[ywon__rxaub].append(rpnlb__brd)
        else:
            yxsh__yrdg[ywon__rxaub] = rpnlb__brd
    fwfxa__rcsj = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    fwfxa__rcsj += (
        f'  cpp_arr_list = alloc_empty_list_type({len(efx__dtcil)}, array_info_type)\n'
        )
    if py_table != types.none:
        for qkdal__vwnee in py_table.type_to_blk.values():
            seypw__jmn = [yxsh__yrdg.get(rpnlb__brd, -1) for rpnlb__brd in
                py_table.block_to_arr_ind[qkdal__vwnee]]
            mdp__lxeu[f'out_inds_{qkdal__vwnee}'] = np.array(seypw__jmn, np
                .int64)
            mdp__lxeu[f'arr_inds_{qkdal__vwnee}'] = np.array(py_table.
                block_to_arr_ind[qkdal__vwnee], np.int64)
            fwfxa__rcsj += f"""  arr_list_{qkdal__vwnee} = get_table_block(py_table, {qkdal__vwnee})
"""
            fwfxa__rcsj += f'  for i in range(len(arr_list_{qkdal__vwnee})):\n'
            fwfxa__rcsj += (
                f'    out_arr_ind_{qkdal__vwnee} = out_inds_{qkdal__vwnee}[i]\n'
                )
            fwfxa__rcsj += f'    if out_arr_ind_{qkdal__vwnee} == -1:\n'
            fwfxa__rcsj += f'      continue\n'
            fwfxa__rcsj += (
                f'    arr_ind_{qkdal__vwnee} = arr_inds_{qkdal__vwnee}[i]\n')
            fwfxa__rcsj += f"""    ensure_column_unboxed(py_table, arr_list_{qkdal__vwnee}, i, arr_ind_{qkdal__vwnee})
"""
            fwfxa__rcsj += f"""    cpp_arr_list[out_arr_ind_{qkdal__vwnee}] = array_to_info(arr_list_{qkdal__vwnee}[i])
"""
        for zbx__sbunm, yiugs__khoo in drms__qdids.items():
            if zbx__sbunm < aemum__ewz:
                qkdal__vwnee = py_table.block_nums[zbx__sbunm]
                jiymr__vyn = py_table.block_offsets[zbx__sbunm]
                for qslu__whiq in yiugs__khoo:
                    fwfxa__rcsj += f"""  cpp_arr_list[{qslu__whiq}] = array_to_info(arr_list_{qkdal__vwnee}[{jiymr__vyn}])
"""
    for rpnlb__brd in range(len(extra_arrs_tup)):
        bnn__egvp = yxsh__yrdg.get(aemum__ewz + rpnlb__brd, -1)
        if bnn__egvp != -1:
            txi__cnwrb = [bnn__egvp] + drms__qdids.get(aemum__ewz +
                rpnlb__brd, [])
            for qslu__whiq in txi__cnwrb:
                fwfxa__rcsj += f"""  cpp_arr_list[{qslu__whiq}] = array_to_info(extra_arrs_tup[{rpnlb__brd}])
"""
    fwfxa__rcsj += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    mdp__lxeu.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    pmia__tyctd = {}
    exec(fwfxa__rcsj, mdp__lxeu, pmia__tyctd)
    return pmia__tyctd['impl']


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
        caiag__mkfia = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='delete_table')
        builder.call(pdghq__kyix, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='shuffle_table')
        plbk__axwsl = builder.call(pdghq__kyix, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return plbk__axwsl
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
        caiag__mkfia = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='delete_shuffle_info')
        return builder.call(pdghq__kyix, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='reverse_shuffle_table')
        return builder.call(pdghq__kyix, args)
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
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='hash_join_table')
        plbk__axwsl = builder.call(pdghq__kyix, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return plbk__axwsl
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
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='sort_values_table')
        plbk__axwsl = builder.call(pdghq__kyix, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return plbk__axwsl
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='sample_table')
        plbk__axwsl = builder.call(pdghq__kyix, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return plbk__axwsl
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='shuffle_renormalization')
        plbk__axwsl = builder.call(pdghq__kyix, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return plbk__axwsl
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='shuffle_renormalization_group')
        plbk__axwsl = builder.call(pdghq__kyix, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return plbk__axwsl
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='drop_duplicates_table')
        plbk__axwsl = builder.call(pdghq__kyix, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return plbk__axwsl
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
        caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer()])
        pdghq__kyix = cgutils.get_or_insert_function(builder.module,
            caiag__mkfia, name='groupby_and_aggregate')
        plbk__axwsl = builder.call(pdghq__kyix, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return plbk__axwsl
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
    sou__emf = array_to_info(in_arr)
    dztsq__mgpo = array_to_info(in_values)
    eqp__gxe = array_to_info(out_arr)
    lreq__xenvk = arr_info_list_to_table([sou__emf, dztsq__mgpo, eqp__gxe])
    _array_isin(eqp__gxe, sou__emf, dztsq__mgpo, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(lreq__xenvk)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    sou__emf = array_to_info(in_arr)
    eqp__gxe = array_to_info(out_arr)
    _get_search_regex(sou__emf, case, match, pat, eqp__gxe)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    qacrk__htqvc = col_array_typ.dtype
    if isinstance(qacrk__htqvc, types.Number) or qacrk__htqvc in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                twm__jbfi, fwush__zmzcv = args
                twm__jbfi = builder.bitcast(twm__jbfi, lir.IntType(8).
                    as_pointer().as_pointer())
                hwlik__xzf = lir.Constant(lir.IntType(64), c_ind)
                wvmoj__hfkj = builder.load(builder.gep(twm__jbfi, [hwlik__xzf])
                    )
                wvmoj__hfkj = builder.bitcast(wvmoj__hfkj, context.
                    get_data_type(qacrk__htqvc).as_pointer())
                return builder.load(builder.gep(wvmoj__hfkj, [fwush__zmzcv]))
            return qacrk__htqvc(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                twm__jbfi, fwush__zmzcv = args
                twm__jbfi = builder.bitcast(twm__jbfi, lir.IntType(8).
                    as_pointer().as_pointer())
                hwlik__xzf = lir.Constant(lir.IntType(64), c_ind)
                wvmoj__hfkj = builder.load(builder.gep(twm__jbfi, [hwlik__xzf])
                    )
                caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                igg__xijk = cgutils.get_or_insert_function(builder.module,
                    caiag__mkfia, name='array_info_getitem')
                xld__kqsp = cgutils.alloca_once(builder, lir.IntType(64))
                args = wvmoj__hfkj, fwush__zmzcv, xld__kqsp
                styp__kym = builder.call(igg__xijk, args)
                return context.make_tuple(builder, sig.return_type, [
                    styp__kym, builder.load(xld__kqsp)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                tdk__ysuia = lir.Constant(lir.IntType(64), 1)
                zya__nvgx = lir.Constant(lir.IntType(64), 2)
                twm__jbfi, fwush__zmzcv = args
                twm__jbfi = builder.bitcast(twm__jbfi, lir.IntType(8).
                    as_pointer().as_pointer())
                hwlik__xzf = lir.Constant(lir.IntType(64), c_ind)
                wvmoj__hfkj = builder.load(builder.gep(twm__jbfi, [hwlik__xzf])
                    )
                caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                pogwr__bdp = cgutils.get_or_insert_function(builder.module,
                    caiag__mkfia, name='get_nested_info')
                args = wvmoj__hfkj, zya__nvgx
                gov__wpr = builder.call(pogwr__bdp, args)
                caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                bsppb__gucqb = cgutils.get_or_insert_function(builder.
                    module, caiag__mkfia, name='array_info_getdata1')
                args = gov__wpr,
                ipxf__wtb = builder.call(bsppb__gucqb, args)
                ipxf__wtb = builder.bitcast(ipxf__wtb, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                zshgt__tms = builder.sext(builder.load(builder.gep(
                    ipxf__wtb, [fwush__zmzcv])), lir.IntType(64))
                args = wvmoj__hfkj, tdk__ysuia
                fts__mwq = builder.call(pogwr__bdp, args)
                caiag__mkfia = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                igg__xijk = cgutils.get_or_insert_function(builder.module,
                    caiag__mkfia, name='array_info_getitem')
                xld__kqsp = cgutils.alloca_once(builder, lir.IntType(64))
                args = fts__mwq, zshgt__tms, xld__kqsp
                styp__kym = builder.call(igg__xijk, args)
                return context.make_tuple(builder, sig.return_type, [
                    styp__kym, builder.load(xld__kqsp)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{qacrk__htqvc}' column data type not supported"
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
                rpit__galy, fwush__zmzcv = args
                rpit__galy = builder.bitcast(rpit__galy, lir.IntType(8).
                    as_pointer().as_pointer())
                hwlik__xzf = lir.Constant(lir.IntType(64), c_ind)
                wvmoj__hfkj = builder.load(builder.gep(rpit__galy, [
                    hwlik__xzf]))
                johs__tiw = builder.bitcast(wvmoj__hfkj, context.
                    get_data_type(types.bool_).as_pointer())
                ulbo__ynzds = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    johs__tiw, fwush__zmzcv)
                icpf__qwzg = builder.icmp_unsigned('!=', ulbo__ynzds, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(icpf__qwzg, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        qacrk__htqvc = col_array_dtype.dtype
        if qacrk__htqvc in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    twm__jbfi, fwush__zmzcv = args
                    twm__jbfi = builder.bitcast(twm__jbfi, lir.IntType(8).
                        as_pointer().as_pointer())
                    hwlik__xzf = lir.Constant(lir.IntType(64), c_ind)
                    wvmoj__hfkj = builder.load(builder.gep(twm__jbfi, [
                        hwlik__xzf]))
                    wvmoj__hfkj = builder.bitcast(wvmoj__hfkj, context.
                        get_data_type(qacrk__htqvc).as_pointer())
                    aba__eydhk = builder.load(builder.gep(wvmoj__hfkj, [
                        fwush__zmzcv]))
                    icpf__qwzg = builder.icmp_unsigned('!=', aba__eydhk,
                        lir.Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(icpf__qwzg, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(qacrk__htqvc, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    twm__jbfi, fwush__zmzcv = args
                    twm__jbfi = builder.bitcast(twm__jbfi, lir.IntType(8).
                        as_pointer().as_pointer())
                    hwlik__xzf = lir.Constant(lir.IntType(64), c_ind)
                    wvmoj__hfkj = builder.load(builder.gep(twm__jbfi, [
                        hwlik__xzf]))
                    wvmoj__hfkj = builder.bitcast(wvmoj__hfkj, context.
                        get_data_type(qacrk__htqvc).as_pointer())
                    aba__eydhk = builder.load(builder.gep(wvmoj__hfkj, [
                        fwush__zmzcv]))
                    bjq__isbf = signature(types.bool_, qacrk__htqvc)
                    ulbo__ynzds = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, bjq__isbf, (aba__eydhk,))
                    return builder.not_(builder.sext(ulbo__ynzds, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
