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
        tof__gqb = context.make_helper(builder, arr_type, in_arr)
        in_arr = tof__gqb.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        qdm__xln = context.make_helper(builder, arr_type, in_arr)
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='list_string_array_to_info')
        return builder.call(iox__vifm, [qdm__xln.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                ufmsg__ppg = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for ujcvh__scf in arr_typ.data:
                    ufmsg__ppg += get_types(ujcvh__scf)
                return ufmsg__ppg
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
            qmhro__nbgcm = context.compile_internal(builder, lambda a: len(
                a), types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                ifymr__krfmo = context.make_helper(builder, arr_typ, value=arr)
                lnr__odc = get_lengths(_get_map_arr_data_type(arr_typ),
                    ifymr__krfmo.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                cqm__nospe = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                lnr__odc = get_lengths(arr_typ.dtype, cqm__nospe.data)
                lnr__odc = cgutils.pack_array(builder, [cqm__nospe.n_arrays
                    ] + [builder.extract_value(lnr__odc, srroo__kwogj) for
                    srroo__kwogj in range(lnr__odc.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                cqm__nospe = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                lnr__odc = []
                for srroo__kwogj, ujcvh__scf in enumerate(arr_typ.data):
                    pqfp__gnnfp = get_lengths(ujcvh__scf, builder.
                        extract_value(cqm__nospe.data, srroo__kwogj))
                    lnr__odc += [builder.extract_value(pqfp__gnnfp,
                        jfqj__ggsg) for jfqj__ggsg in range(pqfp__gnnfp.
                        type.count)]
                lnr__odc = cgutils.pack_array(builder, [qmhro__nbgcm,
                    context.get_constant(types.int64, -1)] + lnr__odc)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                lnr__odc = cgutils.pack_array(builder, [qmhro__nbgcm])
            else:
                raise BodoError(
                    f'array_to_info: unsupported type for subarray {arr_typ}')
            return lnr__odc

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                ifymr__krfmo = context.make_helper(builder, arr_typ, value=arr)
                tgt__ymybt = get_buffers(_get_map_arr_data_type(arr_typ),
                    ifymr__krfmo.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                cqm__nospe = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                izj__phbi = get_buffers(arr_typ.dtype, cqm__nospe.data)
                kkc__lrs = context.make_array(types.Array(offset_type, 1, 'C')
                    )(context, builder, cqm__nospe.offsets)
                mjs__rmmms = builder.bitcast(kkc__lrs.data, lir.IntType(8).
                    as_pointer())
                tey__ubs = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, cqm__nospe.null_bitmap)
                yjq__wzedh = builder.bitcast(tey__ubs.data, lir.IntType(8).
                    as_pointer())
                tgt__ymybt = cgutils.pack_array(builder, [mjs__rmmms,
                    yjq__wzedh] + [builder.extract_value(izj__phbi,
                    srroo__kwogj) for srroo__kwogj in range(izj__phbi.type.
                    count)])
            elif isinstance(arr_typ, StructArrayType):
                cqm__nospe = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                izj__phbi = []
                for srroo__kwogj, ujcvh__scf in enumerate(arr_typ.data):
                    cld__stty = get_buffers(ujcvh__scf, builder.
                        extract_value(cqm__nospe.data, srroo__kwogj))
                    izj__phbi += [builder.extract_value(cld__stty,
                        jfqj__ggsg) for jfqj__ggsg in range(cld__stty.type.
                        count)]
                tey__ubs = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, cqm__nospe.null_bitmap)
                yjq__wzedh = builder.bitcast(tey__ubs.data, lir.IntType(8).
                    as_pointer())
                tgt__ymybt = cgutils.pack_array(builder, [yjq__wzedh] +
                    izj__phbi)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                prd__gjx = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    prd__gjx = int128_type
                elif arr_typ == datetime_date_array_type:
                    prd__gjx = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                epg__jgak = context.make_array(types.Array(prd__gjx, 1, 'C'))(
                    context, builder, arr.data)
                tey__ubs = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, arr.null_bitmap)
                tnk__nfvse = builder.bitcast(epg__jgak.data, lir.IntType(8)
                    .as_pointer())
                yjq__wzedh = builder.bitcast(tey__ubs.data, lir.IntType(8).
                    as_pointer())
                tgt__ymybt = cgutils.pack_array(builder, [yjq__wzedh,
                    tnk__nfvse])
            elif arr_typ in (string_array_type, binary_array_type):
                cqm__nospe = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                ksmz__vhn = context.make_helper(builder, offset_arr_type,
                    cqm__nospe.offsets).data
                njtq__xlm = context.make_helper(builder, char_arr_type,
                    cqm__nospe.data).data
                sxpb__dwua = context.make_helper(builder,
                    null_bitmap_arr_type, cqm__nospe.null_bitmap).data
                tgt__ymybt = cgutils.pack_array(builder, [builder.bitcast(
                    ksmz__vhn, lir.IntType(8).as_pointer()), builder.
                    bitcast(sxpb__dwua, lir.IntType(8).as_pointer()),
                    builder.bitcast(njtq__xlm, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                tnk__nfvse = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                vhxik__blk = lir.Constant(lir.IntType(8).as_pointer(), None)
                tgt__ymybt = cgutils.pack_array(builder, [vhxik__blk,
                    tnk__nfvse])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return tgt__ymybt

        def get_field_names(arr_typ):
            vriw__ygkf = []
            if isinstance(arr_typ, StructArrayType):
                for ceiyt__nxga, kzc__zozq in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    vriw__ygkf.append(ceiyt__nxga)
                    vriw__ygkf += get_field_names(kzc__zozq)
            elif isinstance(arr_typ, ArrayItemArrayType):
                vriw__ygkf += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                vriw__ygkf += get_field_names(_get_map_arr_data_type(arr_typ))
            return vriw__ygkf
        ufmsg__ppg = get_types(arr_type)
        wvntx__ekdg = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in ufmsg__ppg])
        bzqik__mmqii = cgutils.alloca_once_value(builder, wvntx__ekdg)
        lnr__odc = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, lnr__odc)
        tgt__ymybt = get_buffers(arr_type, in_arr)
        khc__kwgu = cgutils.alloca_once_value(builder, tgt__ymybt)
        vriw__ygkf = get_field_names(arr_type)
        if len(vriw__ygkf) == 0:
            vriw__ygkf = ['irrelevant']
        rwarh__rpx = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in vriw__ygkf])
        snu__xrmzq = cgutils.alloca_once_value(builder, rwarh__rpx)
        if isinstance(arr_type, MapArrayType):
            smf__hos = _get_map_arr_data_type(arr_type)
            xcxw__cfotf = context.make_helper(builder, arr_type, value=in_arr)
            xlsf__meah = xcxw__cfotf.data
        else:
            smf__hos = arr_type
            xlsf__meah = in_arr
        epjk__dibwt = context.make_helper(builder, smf__hos, xlsf__meah)
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='nested_array_to_info')
        upaic__fxia = builder.call(iox__vifm, [builder.bitcast(bzqik__mmqii,
            lir.IntType(32).as_pointer()), builder.bitcast(khc__kwgu, lir.
            IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            snu__xrmzq, lir.IntType(8).as_pointer()), epjk__dibwt.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return upaic__fxia
    if arr_type in (string_array_type, binary_array_type):
        gcpey__igicj = context.make_helper(builder, arr_type, in_arr)
        rrrtm__cbjt = ArrayItemArrayType(char_arr_type)
        qdm__xln = context.make_helper(builder, rrrtm__cbjt, gcpey__igicj.data)
        cqm__nospe = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        ksmz__vhn = context.make_helper(builder, offset_arr_type,
            cqm__nospe.offsets).data
        njtq__xlm = context.make_helper(builder, char_arr_type, cqm__nospe.data
            ).data
        sxpb__dwua = context.make_helper(builder, null_bitmap_arr_type,
            cqm__nospe.null_bitmap).data
        bzddp__tbokm = builder.zext(builder.load(builder.gep(ksmz__vhn, [
            cqm__nospe.n_arrays])), lir.IntType(64))
        wihq__gmud = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='string_array_to_info')
        return builder.call(iox__vifm, [cqm__nospe.n_arrays, bzddp__tbokm,
            njtq__xlm, ksmz__vhn, sxpb__dwua, qdm__xln.meminfo, wihq__gmud])
    if arr_type == bodo.dict_str_arr_type:
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        lhy__mwhi = arr.data
        hqn__avarn = arr.indices
        sig = array_info_type(arr_type.data)
        jixw__wqwlv = array_to_info_codegen(context, builder, sig, (
            lhy__mwhi,), False)
        sig = array_info_type(bodo.libs.dict_arr_ext.dict_indices_arr_type)
        cdau__ivgge = array_to_info_codegen(context, builder, sig, (
            hqn__avarn,), False)
        hxev__ocomz = cgutils.create_struct_proxy(bodo.libs.dict_arr_ext.
            dict_indices_arr_type)(context, builder, hqn__avarn)
        yjq__wzedh = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, hxev__ocomz.null_bitmap).data
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='dict_str_array_to_info')
        miq__zlqtv = builder.zext(arr.has_global_dictionary, lir.IntType(32))
        return builder.call(iox__vifm, [jixw__wqwlv, cdau__ivgge, builder.
            bitcast(yjq__wzedh, lir.IntType(8).as_pointer()), miq__zlqtv])
    auvn__udp = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        vygn__yzmv = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        hkqv__eqss = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(hkqv__eqss, 1, 'C')
        auvn__udp = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, bodo.DatetimeArrayType):
        if auvn__udp:
            raise BodoError(
                'array_to_info(): Categorical PandasDatetimeArrayType not supported'
                )
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).data
        arr_type = arr_type.data_array_type
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        qmhro__nbgcm = builder.extract_value(arr.shape, 0)
        ylxb__rgp = arr_type.dtype
        bidx__hqs = numba_to_c_type(ylxb__rgp)
        ircd__suygj = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), bidx__hqs))
        if auvn__udp:
            yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(64), lir.IntType(8).as_pointer()])
            iox__vifm = cgutils.get_or_insert_function(builder.module,
                yfpdh__saht, name='categorical_array_to_info')
            return builder.call(iox__vifm, [qmhro__nbgcm, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                ircd__suygj), vygn__yzmv, arr.meminfo])
        else:
            yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer()])
            iox__vifm = cgutils.get_or_insert_function(builder.module,
                yfpdh__saht, name='numpy_array_to_info')
            return builder.call(iox__vifm, [qmhro__nbgcm, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                ircd__suygj), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        ylxb__rgp = arr_type.dtype
        prd__gjx = ylxb__rgp
        if isinstance(arr_type, DecimalArrayType):
            prd__gjx = int128_type
        if arr_type == datetime_date_array_type:
            prd__gjx = types.int64
        epg__jgak = context.make_array(types.Array(prd__gjx, 1, 'C'))(context,
            builder, arr.data)
        qmhro__nbgcm = builder.extract_value(epg__jgak.shape, 0)
        nfil__tmfi = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        bidx__hqs = numba_to_c_type(ylxb__rgp)
        ircd__suygj = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), bidx__hqs))
        if isinstance(arr_type, DecimalArrayType):
            yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer(), lir.IntType(32), lir.
                IntType(32)])
            iox__vifm = cgutils.get_or_insert_function(builder.module,
                yfpdh__saht, name='decimal_array_to_info')
            return builder.call(iox__vifm, [qmhro__nbgcm, builder.bitcast(
                epg__jgak.data, lir.IntType(8).as_pointer()), builder.load(
                ircd__suygj), builder.bitcast(nfil__tmfi.data, lir.IntType(
                8).as_pointer()), epg__jgak.meminfo, nfil__tmfi.meminfo,
                context.get_constant(types.int32, arr_type.precision),
                context.get_constant(types.int32, arr_type.scale)])
        else:
            yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer()])
            iox__vifm = cgutils.get_or_insert_function(builder.module,
                yfpdh__saht, name='nullable_array_to_info')
            return builder.call(iox__vifm, [qmhro__nbgcm, builder.bitcast(
                epg__jgak.data, lir.IntType(8).as_pointer()), builder.load(
                ircd__suygj), builder.bitcast(nfil__tmfi.data, lir.IntType(
                8).as_pointer()), epg__jgak.meminfo, nfil__tmfi.meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        zwil__dddd = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        eay__nggk = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        qmhro__nbgcm = builder.extract_value(zwil__dddd.shape, 0)
        bidx__hqs = numba_to_c_type(arr_type.arr_type.dtype)
        ircd__suygj = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), bidx__hqs))
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='interval_array_to_info')
        return builder.call(iox__vifm, [qmhro__nbgcm, builder.bitcast(
            zwil__dddd.data, lir.IntType(8).as_pointer()), builder.bitcast(
            eay__nggk.data, lir.IntType(8).as_pointer()), builder.load(
            ircd__suygj), zwil__dddd.meminfo, eay__nggk.meminfo])
    raise_bodo_error(f'array_to_info(): array type {arr_type} is not supported'
        )


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    jjvj__kacf = cgutils.alloca_once(builder, lir.IntType(64))
    tnk__nfvse = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    mym__botl = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    yfpdh__saht = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    iox__vifm = cgutils.get_or_insert_function(builder.module, yfpdh__saht,
        name='info_to_numpy_array')
    builder.call(iox__vifm, [in_info, jjvj__kacf, tnk__nfvse, mym__botl])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    aegd__livp = context.get_value_type(types.intp)
    dfgg__bxq = cgutils.pack_array(builder, [builder.load(jjvj__kacf)], ty=
        aegd__livp)
    ncu__azrl = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    rmz__yrpn = cgutils.pack_array(builder, [ncu__azrl], ty=aegd__livp)
    njtq__xlm = builder.bitcast(builder.load(tnk__nfvse), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=njtq__xlm, shape=dfgg__bxq,
        strides=rmz__yrpn, itemsize=ncu__azrl, meminfo=builder.load(mym__botl))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    ugghw__vwa = context.make_helper(builder, arr_type)
    yfpdh__saht = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    iox__vifm = cgutils.get_or_insert_function(builder.module, yfpdh__saht,
        name='info_to_list_string_array')
    builder.call(iox__vifm, [in_info, ugghw__vwa._get_ptr_by_name('meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return ugghw__vwa._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    pcrun__idedg = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        isqwt__vca = lengths_pos
        foy__mbh = infos_pos
        xbbwn__tkmn, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        mgvo__pxi = ArrayItemArrayPayloadType(arr_typ)
        szd__vbg = context.get_data_type(mgvo__pxi)
        uysu__sak = context.get_abi_sizeof(szd__vbg)
        rtxza__cumyd = define_array_item_dtor(context, builder, arr_typ,
            mgvo__pxi)
        ffqlf__cnuls = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, uysu__sak), rtxza__cumyd)
        iqxn__tcq = context.nrt.meminfo_data(builder, ffqlf__cnuls)
        fkd__hsqe = builder.bitcast(iqxn__tcq, szd__vbg.as_pointer())
        cqm__nospe = cgutils.create_struct_proxy(mgvo__pxi)(context, builder)
        cqm__nospe.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), isqwt__vca)
        cqm__nospe.data = xbbwn__tkmn
        ojsye__ohhcm = builder.load(array_infos_ptr)
        mucef__fuz = builder.bitcast(builder.extract_value(ojsye__ohhcm,
            foy__mbh), pcrun__idedg)
        cqm__nospe.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, mucef__fuz)
        ctutl__ple = builder.bitcast(builder.extract_value(ojsye__ohhcm, 
            foy__mbh + 1), pcrun__idedg)
        cqm__nospe.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, ctutl__ple)
        builder.store(cqm__nospe._getvalue(), fkd__hsqe)
        qdm__xln = context.make_helper(builder, arr_typ)
        qdm__xln.meminfo = ffqlf__cnuls
        return qdm__xln._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        gxh__zsj = []
        foy__mbh = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for hayea__cyhan in arr_typ.data:
            xbbwn__tkmn, lengths_pos, infos_pos = nested_to_array(context,
                builder, hayea__cyhan, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            gxh__zsj.append(xbbwn__tkmn)
        mgvo__pxi = StructArrayPayloadType(arr_typ.data)
        szd__vbg = context.get_value_type(mgvo__pxi)
        uysu__sak = context.get_abi_sizeof(szd__vbg)
        rtxza__cumyd = define_struct_arr_dtor(context, builder, arr_typ,
            mgvo__pxi)
        ffqlf__cnuls = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, uysu__sak), rtxza__cumyd)
        iqxn__tcq = context.nrt.meminfo_data(builder, ffqlf__cnuls)
        fkd__hsqe = builder.bitcast(iqxn__tcq, szd__vbg.as_pointer())
        cqm__nospe = cgutils.create_struct_proxy(mgvo__pxi)(context, builder)
        cqm__nospe.data = cgutils.pack_array(builder, gxh__zsj
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, gxh__zsj)
        ojsye__ohhcm = builder.load(array_infos_ptr)
        ctutl__ple = builder.bitcast(builder.extract_value(ojsye__ohhcm,
            foy__mbh), pcrun__idedg)
        cqm__nospe.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, ctutl__ple)
        builder.store(cqm__nospe._getvalue(), fkd__hsqe)
        wfmeh__gow = context.make_helper(builder, arr_typ)
        wfmeh__gow.meminfo = ffqlf__cnuls
        return wfmeh__gow._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        ojsye__ohhcm = builder.load(array_infos_ptr)
        bqtkm__qrlm = builder.bitcast(builder.extract_value(ojsye__ohhcm,
            infos_pos), pcrun__idedg)
        gcpey__igicj = context.make_helper(builder, arr_typ)
        rrrtm__cbjt = ArrayItemArrayType(char_arr_type)
        qdm__xln = context.make_helper(builder, rrrtm__cbjt)
        yfpdh__saht = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='info_to_string_array')
        builder.call(iox__vifm, [bqtkm__qrlm, qdm__xln._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        gcpey__igicj.data = qdm__xln._getvalue()
        return gcpey__igicj._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        ojsye__ohhcm = builder.load(array_infos_ptr)
        yvjbz__ezila = builder.bitcast(builder.extract_value(ojsye__ohhcm, 
            infos_pos + 1), pcrun__idedg)
        return _lower_info_to_array_numpy(arr_typ, context, builder,
            yvjbz__ezila), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        prd__gjx = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            prd__gjx = int128_type
        elif arr_typ == datetime_date_array_type:
            prd__gjx = types.int64
        ojsye__ohhcm = builder.load(array_infos_ptr)
        ctutl__ple = builder.bitcast(builder.extract_value(ojsye__ohhcm,
            infos_pos), pcrun__idedg)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, ctutl__ple)
        yvjbz__ezila = builder.bitcast(builder.extract_value(ojsye__ohhcm, 
            infos_pos + 1), pcrun__idedg)
        arr.data = _lower_info_to_array_numpy(types.Array(prd__gjx, 1, 'C'),
            context, builder, yvjbz__ezila)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


def info_to_array_codegen(context, builder, sig, args):
    array_type = sig.args[1]
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    in_info, azf__fsp = args
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
                return 1 + sum([get_num_arrays(hayea__cyhan) for
                    hayea__cyhan in arr_typ.data])
            else:
                return 1

        def get_num_infos(arr_typ):
            if isinstance(arr_typ, ArrayItemArrayType):
                return 2 + get_num_infos(arr_typ.dtype)
            elif isinstance(arr_typ, StructArrayType):
                return 1 + sum([get_num_infos(hayea__cyhan) for
                    hayea__cyhan in arr_typ.data])
            elif arr_typ in (string_array_type, binary_array_type):
                return 1
            else:
                return 2
        if isinstance(arr_type, TupleArrayType):
            tacgv__asj = StructArrayType(arr_type.data, ('dummy',) * len(
                arr_type.data))
        elif isinstance(arr_type, MapArrayType):
            tacgv__asj = _get_map_arr_data_type(arr_type)
        else:
            tacgv__asj = arr_type
        nsvj__puqwu = get_num_arrays(tacgv__asj)
        lnr__odc = cgutils.pack_array(builder, [lir.Constant(lir.IntType(64
            ), 0) for azf__fsp in range(nsvj__puqwu)])
        lengths_ptr = cgutils.alloca_once_value(builder, lnr__odc)
        vhxik__blk = lir.Constant(lir.IntType(8).as_pointer(), None)
        ajwf__oia = cgutils.pack_array(builder, [vhxik__blk for azf__fsp in
            range(get_num_infos(tacgv__asj))])
        array_infos_ptr = cgutils.alloca_once_value(builder, ajwf__oia)
        yfpdh__saht = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='info_to_nested_array')
        builder.call(iox__vifm, [in_info, builder.bitcast(lengths_ptr, lir.
            IntType(64).as_pointer()), builder.bitcast(array_infos_ptr, lir
            .IntType(8).as_pointer().as_pointer())])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        arr, azf__fsp, azf__fsp = nested_to_array(context, builder,
            tacgv__asj, lengths_ptr, array_infos_ptr, 0, 0)
        if isinstance(arr_type, TupleArrayType):
            tof__gqb = context.make_helper(builder, arr_type)
            tof__gqb.data = arr
            context.nrt.incref(builder, tacgv__asj, arr)
            arr = tof__gqb._getvalue()
        elif isinstance(arr_type, MapArrayType):
            sig = signature(arr_type, tacgv__asj)
            arr = init_map_arr_codegen(context, builder, sig, (arr,))
        return arr
    if arr_type in (string_array_type, binary_array_type):
        gcpey__igicj = context.make_helper(builder, arr_type)
        rrrtm__cbjt = ArrayItemArrayType(char_arr_type)
        qdm__xln = context.make_helper(builder, rrrtm__cbjt)
        yfpdh__saht = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='info_to_string_array')
        builder.call(iox__vifm, [in_info, qdm__xln._get_ptr_by_name('meminfo')]
            )
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        gcpey__igicj.data = qdm__xln._getvalue()
        return gcpey__igicj._getvalue()
    if arr_type == bodo.dict_str_arr_type:
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='get_nested_info')
        jixw__wqwlv = builder.call(iox__vifm, [in_info, lir.Constant(lir.
            IntType(32), 1)])
        cdau__ivgge = builder.call(iox__vifm, [in_info, lir.Constant(lir.
            IntType(32), 2)])
        dzy__brq = context.make_helper(builder, arr_type)
        sig = arr_type.data(array_info_type, arr_type.data)
        dzy__brq.data = info_to_array_codegen(context, builder, sig, (
            jixw__wqwlv, context.get_constant_null(arr_type.data)))
        fxv__ahvvr = bodo.libs.dict_arr_ext.dict_indices_arr_type
        sig = fxv__ahvvr(array_info_type, fxv__ahvvr)
        dzy__brq.indices = info_to_array_codegen(context, builder, sig, (
            cdau__ivgge, context.get_constant_null(fxv__ahvvr)))
        yfpdh__saht = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='get_has_global_dictionary')
        miq__zlqtv = builder.call(iox__vifm, [in_info])
        dzy__brq.has_global_dictionary = builder.trunc(miq__zlqtv, cgutils.
            bool_t)
        return dzy__brq._getvalue()
    if isinstance(arr_type, CategoricalArrayType):
        out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        hkqv__eqss = get_categories_int_type(arr_type.dtype)
        websz__evpfn = types.Array(hkqv__eqss, 1, 'C')
        out_arr.codes = _lower_info_to_array_numpy(websz__evpfn, context,
            builder, in_info)
        if isinstance(array_type, types.TypeRef):
            assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
            is_ordered = arr_type.dtype.ordered
            ejjgs__vowi = bodo.utils.utils.create_categorical_type(arr_type
                .dtype.categories, arr_type.dtype.data.data, is_ordered)
            new_cats_tup = MetaType(tuple(ejjgs__vowi))
            int_type = arr_type.dtype.int_type
            rvc__vwz = arr_type.dtype.data.data
            uucc__iuyuj = context.get_constant_generic(builder, rvc__vwz,
                ejjgs__vowi)
            ylxb__rgp = context.compile_internal(builder, lambda c_arr:
                bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.utils.
                conversion.index_from_array(c_arr), is_ordered, int_type,
                new_cats_tup), arr_type.dtype(rvc__vwz), [uucc__iuyuj])
        else:
            ylxb__rgp = cgutils.create_struct_proxy(arr_type)(context,
                builder, args[1]).dtype
            context.nrt.incref(builder, arr_type.dtype, ylxb__rgp)
        out_arr.dtype = ylxb__rgp
        return out_arr._getvalue()
    if isinstance(arr_type, bodo.DatetimeArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        njtq__xlm = _lower_info_to_array_numpy(arr_type.data_array_type,
            context, builder, in_info)
        arr.data = njtq__xlm
        return arr._getvalue()
    if isinstance(arr_type, types.Array):
        return _lower_info_to_array_numpy(arr_type, context, builder, in_info)
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        prd__gjx = arr_type.dtype
        if isinstance(arr_type, DecimalArrayType):
            prd__gjx = int128_type
        elif arr_type == datetime_date_array_type:
            prd__gjx = types.int64
        pguk__yjt = types.Array(prd__gjx, 1, 'C')
        epg__jgak = context.make_array(pguk__yjt)(context, builder)
        gei__wad = types.Array(types.uint8, 1, 'C')
        pnqpb__utxkz = context.make_array(gei__wad)(context, builder)
        jjvj__kacf = cgutils.alloca_once(builder, lir.IntType(64))
        arerw__epxdz = cgutils.alloca_once(builder, lir.IntType(64))
        tnk__nfvse = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        hmbe__gdzc = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        mym__botl = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        oojh__tkjor = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        yfpdh__saht = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer(), lir.IntType(8).as_pointer
            ().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='info_to_nullable_array')
        builder.call(iox__vifm, [in_info, jjvj__kacf, arerw__epxdz,
            tnk__nfvse, hmbe__gdzc, mym__botl, oojh__tkjor])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        aegd__livp = context.get_value_type(types.intp)
        dfgg__bxq = cgutils.pack_array(builder, [builder.load(jjvj__kacf)],
            ty=aegd__livp)
        ncu__azrl = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(prd__gjx)))
        rmz__yrpn = cgutils.pack_array(builder, [ncu__azrl], ty=aegd__livp)
        njtq__xlm = builder.bitcast(builder.load(tnk__nfvse), context.
            get_data_type(prd__gjx).as_pointer())
        numba.np.arrayobj.populate_array(epg__jgak, data=njtq__xlm, shape=
            dfgg__bxq, strides=rmz__yrpn, itemsize=ncu__azrl, meminfo=
            builder.load(mym__botl))
        arr.data = epg__jgak._getvalue()
        dfgg__bxq = cgutils.pack_array(builder, [builder.load(arerw__epxdz)
            ], ty=aegd__livp)
        ncu__azrl = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(types.uint8)))
        rmz__yrpn = cgutils.pack_array(builder, [ncu__azrl], ty=aegd__livp)
        njtq__xlm = builder.bitcast(builder.load(hmbe__gdzc), context.
            get_data_type(types.uint8).as_pointer())
        numba.np.arrayobj.populate_array(pnqpb__utxkz, data=njtq__xlm,
            shape=dfgg__bxq, strides=rmz__yrpn, itemsize=ncu__azrl, meminfo
            =builder.load(oojh__tkjor))
        arr.null_bitmap = pnqpb__utxkz._getvalue()
        return arr._getvalue()
    if isinstance(arr_type, IntervalArrayType):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder)
        zwil__dddd = context.make_array(arr_type.arr_type)(context, builder)
        eay__nggk = context.make_array(arr_type.arr_type)(context, builder)
        jjvj__kacf = cgutils.alloca_once(builder, lir.IntType(64))
        scdw__rrw = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        wace__nvc = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        qtm__wbsb = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        baknb__iywr = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
        yfpdh__saht = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer().as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir.
            IntType(8).as_pointer().as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='info_to_interval_array')
        builder.call(iox__vifm, [in_info, jjvj__kacf, scdw__rrw, wace__nvc,
            qtm__wbsb, baknb__iywr])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        aegd__livp = context.get_value_type(types.intp)
        dfgg__bxq = cgutils.pack_array(builder, [builder.load(jjvj__kacf)],
            ty=aegd__livp)
        ncu__azrl = context.get_constant(types.intp, context.get_abi_sizeof
            (context.get_data_type(arr_type.arr_type.dtype)))
        rmz__yrpn = cgutils.pack_array(builder, [ncu__azrl], ty=aegd__livp)
        xzenn__svn = builder.bitcast(builder.load(scdw__rrw), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(zwil__dddd, data=xzenn__svn, shape
            =dfgg__bxq, strides=rmz__yrpn, itemsize=ncu__azrl, meminfo=
            builder.load(qtm__wbsb))
        arr.left = zwil__dddd._getvalue()
        ghcjc__dgdde = builder.bitcast(builder.load(wace__nvc), context.
            get_data_type(arr_type.arr_type.dtype).as_pointer())
        numba.np.arrayobj.populate_array(eay__nggk, data=ghcjc__dgdde,
            shape=dfgg__bxq, strides=rmz__yrpn, itemsize=ncu__azrl, meminfo
            =builder.load(baknb__iywr))
        arr.right = eay__nggk._getvalue()
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
        qmhro__nbgcm, azf__fsp = args
        bidx__hqs = numba_to_c_type(array_type.dtype)
        ircd__suygj = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), bidx__hqs))
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='alloc_numpy')
        return builder.call(iox__vifm, [qmhro__nbgcm, builder.load(
            ircd__suygj)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        qmhro__nbgcm, vpr__soh = args
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='alloc_string_array')
        return builder.call(iox__vifm, [qmhro__nbgcm, vpr__soh])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    emmzn__widyl, = args
    zxkj__xslfl = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], emmzn__widyl)
    yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer().as_pointer(), lir.IntType(64)])
    iox__vifm = cgutils.get_or_insert_function(builder.module, yfpdh__saht,
        name='arr_info_list_to_table')
    return builder.call(iox__vifm, [zxkj__xslfl.data, zxkj__xslfl.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='info_from_table')
        return builder.call(iox__vifm, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    uykad__nard = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        cpp_table, qetji__xsgmv, azf__fsp = args
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='info_from_table')
        dsunn__zdbp = cgutils.create_struct_proxy(uykad__nard)(context, builder
            )
        dsunn__zdbp.parent = cgutils.get_null_value(dsunn__zdbp.parent.type)
        uysc__iaew = context.make_array(table_idx_arr_t)(context, builder,
            qetji__xsgmv)
        ddw__ikx = context.get_constant(types.int64, -1)
        kzbm__ynnw = context.get_constant(types.int64, 0)
        mhem__kza = cgutils.alloca_once_value(builder, kzbm__ynnw)
        for t, kmxx__agnd in uykad__nard.type_to_blk.items():
            jbbup__jilws = context.get_constant(types.int64, len(
                uykad__nard.block_to_arr_ind[kmxx__agnd]))
            azf__fsp, eurx__rkaak = ListInstance.allocate_ex(context,
                builder, types.List(t), jbbup__jilws)
            eurx__rkaak.size = jbbup__jilws
            mor__lfvrp = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(uykad__nard.block_to_arr_ind
                [kmxx__agnd], dtype=np.int64))
            qep__wtaq = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, mor__lfvrp)
            with cgutils.for_range(builder, jbbup__jilws) as imzw__jxk:
                srroo__kwogj = imzw__jxk.index
                ycfs__mrxom = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    qep__wtaq, srroo__kwogj)
                wze__teorz = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, uysc__iaew, ycfs__mrxom)
                oqzc__auu = builder.icmp_unsigned('!=', wze__teorz, ddw__ikx)
                with builder.if_else(oqzc__auu) as (jiqj__gjg, zav__htd):
                    with jiqj__gjg:
                        nqgr__lugf = builder.call(iox__vifm, [cpp_table,
                            wze__teorz])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            nqgr__lugf])
                        eurx__rkaak.inititem(srroo__kwogj, arr, incref=False)
                        qmhro__nbgcm = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(qmhro__nbgcm, mhem__kza)
                    with zav__htd:
                        hlabo__ncfq = context.get_constant_null(t)
                        eurx__rkaak.inititem(srroo__kwogj, hlabo__ncfq,
                            incref=False)
            setattr(dsunn__zdbp, f'block_{kmxx__agnd}', eurx__rkaak.value)
        dsunn__zdbp.len = builder.load(mhem__kza)
        return dsunn__zdbp._getvalue()
    return uykad__nard(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def cpp_table_to_py_data(cpp_table, out_col_inds_t, out_types_t, n_rows_t,
    n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
    iam__bzys = out_col_inds_t.instance_type.meta
    uykad__nard = unwrap_typeref(out_types_t.types[0])
    ikk__nqlvs = [unwrap_typeref(out_types_t.types[srroo__kwogj]) for
        srroo__kwogj in range(1, len(out_types_t.types))]
    azejx__tavuk = {}
    wjyyi__lqk = get_overload_const_int(n_table_cols_t)
    mdivj__gzn = {pui__esvz: srroo__kwogj for srroo__kwogj, pui__esvz in
        enumerate(iam__bzys)}
    if not is_overload_none(unknown_cat_arrs_t):
        tpb__jtaah = {clpbq__khrid: srroo__kwogj for srroo__kwogj,
            clpbq__khrid in enumerate(cat_inds_t.instance_type.meta)}
    pzca__cxz = []
    xckm__lyk = """def impl(cpp_table, out_col_inds_t, out_types_t, n_rows_t, n_table_cols_t, unknown_cat_arrs_t=None, cat_inds_t=None):
"""
    if isinstance(uykad__nard, bodo.TableType):
        xckm__lyk += f'  py_table = init_table(py_table_type, False)\n'
        xckm__lyk += f'  py_table = set_table_len(py_table, n_rows_t)\n'
        for ulshb__lek, kmxx__agnd in uykad__nard.type_to_blk.items():
            leuj__xhri = [mdivj__gzn.get(srroo__kwogj, -1) for srroo__kwogj in
                uykad__nard.block_to_arr_ind[kmxx__agnd]]
            azejx__tavuk[f'out_inds_{kmxx__agnd}'] = np.array(leuj__xhri,
                np.int64)
            azejx__tavuk[f'out_type_{kmxx__agnd}'] = ulshb__lek
            azejx__tavuk[f'typ_list_{kmxx__agnd}'] = types.List(ulshb__lek)
            ecrj__otdoo = f'out_type_{kmxx__agnd}'
            if type_has_unknown_cats(ulshb__lek):
                if is_overload_none(unknown_cat_arrs_t):
                    xckm__lyk += f"""  in_arr_list_{kmxx__agnd} = get_table_block(out_types_t[0], {kmxx__agnd})
"""
                    ecrj__otdoo = f'in_arr_list_{kmxx__agnd}[i]'
                else:
                    azejx__tavuk[f'cat_arr_inds_{kmxx__agnd}'] = np.array([
                        tpb__jtaah.get(srroo__kwogj, -1) for srroo__kwogj in
                        uykad__nard.block_to_arr_ind[kmxx__agnd]], np.int64)
                    ecrj__otdoo = (
                        f'unknown_cat_arrs_t[cat_arr_inds_{kmxx__agnd}[i]]')
            jbbup__jilws = len(uykad__nard.block_to_arr_ind[kmxx__agnd])
            xckm__lyk += f"""  arr_list_{kmxx__agnd} = alloc_list_like(typ_list_{kmxx__agnd}, {jbbup__jilws}, False)
"""
            xckm__lyk += f'  for i in range(len(arr_list_{kmxx__agnd})):\n'
            xckm__lyk += (
                f'    cpp_ind_{kmxx__agnd} = out_inds_{kmxx__agnd}[i]\n')
            xckm__lyk += f'    if cpp_ind_{kmxx__agnd} == -1:\n'
            xckm__lyk += f'      continue\n'
            xckm__lyk += f"""    arr_{kmxx__agnd} = info_to_array(info_from_table(cpp_table, cpp_ind_{kmxx__agnd}), {ecrj__otdoo})
"""
            xckm__lyk += f'    arr_list_{kmxx__agnd}[i] = arr_{kmxx__agnd}\n'
            xckm__lyk += f"""  py_table = set_table_block(py_table, arr_list_{kmxx__agnd}, {kmxx__agnd})
"""
        pzca__cxz.append('py_table')
    elif uykad__nard != types.none:
        ndyp__bnbar = mdivj__gzn.get(0, -1)
        if ndyp__bnbar != -1:
            azejx__tavuk[f'arr_typ_arg0'] = uykad__nard
            ecrj__otdoo = f'arr_typ_arg0'
            if type_has_unknown_cats(uykad__nard):
                if is_overload_none(unknown_cat_arrs_t):
                    ecrj__otdoo = f'out_types_t[0]'
                else:
                    ecrj__otdoo = f'unknown_cat_arrs_t[{tpb__jtaah[0]}]'
            xckm__lyk += f"""  out_arg0 = info_to_array(info_from_table(cpp_table, {ndyp__bnbar}), {ecrj__otdoo})
"""
            pzca__cxz.append('out_arg0')
    for srroo__kwogj, t in enumerate(ikk__nqlvs):
        ndyp__bnbar = mdivj__gzn.get(wjyyi__lqk + srroo__kwogj, -1)
        if ndyp__bnbar != -1:
            azejx__tavuk[f'extra_arr_type_{srroo__kwogj}'] = t
            ecrj__otdoo = f'extra_arr_type_{srroo__kwogj}'
            if type_has_unknown_cats(t):
                if is_overload_none(unknown_cat_arrs_t):
                    ecrj__otdoo = f'out_types_t[{srroo__kwogj + 1}]'
                else:
                    ecrj__otdoo = (
                        f'unknown_cat_arrs_t[{tpb__jtaah[wjyyi__lqk + srroo__kwogj]}]'
                        )
            xckm__lyk += f"""  out_{srroo__kwogj} = info_to_array(info_from_table(cpp_table, {ndyp__bnbar}), {ecrj__otdoo})
"""
            pzca__cxz.append(f'out_{srroo__kwogj}')
    dya__swm = ',' if len(pzca__cxz) == 1 else ''
    xckm__lyk += f"  return ({', '.join(pzca__cxz)}{dya__swm})\n"
    azejx__tavuk.update({'init_table': bodo.hiframes.table.init_table,
        'alloc_list_like': bodo.hiframes.table.alloc_list_like,
        'set_table_block': bodo.hiframes.table.set_table_block,
        'set_table_len': bodo.hiframes.table.set_table_len,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'info_to_array': info_to_array, 'info_from_table': info_from_table,
        'out_col_inds': list(iam__bzys), 'py_table_type': uykad__nard})
    zyocr__rqepd = {}
    exec(xckm__lyk, azejx__tavuk, zyocr__rqepd)
    return zyocr__rqepd['impl']


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    uykad__nard = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        py_table, azf__fsp = args
        zrbip__pbem = cgutils.create_struct_proxy(uykad__nard)(context,
            builder, py_table)
        if uykad__nard.has_runtime_cols:
            ogb__wmv = lir.Constant(lir.IntType(64), 0)
            for kmxx__agnd, t in enumerate(uykad__nard.arr_types):
                cyh__rpcy = getattr(zrbip__pbem, f'block_{kmxx__agnd}')
                scfng__urg = ListInstance(context, builder, types.List(t),
                    cyh__rpcy)
                ogb__wmv = builder.add(ogb__wmv, scfng__urg.size)
        else:
            ogb__wmv = lir.Constant(lir.IntType(64), len(uykad__nard.arr_types)
                )
        azf__fsp, czy__bzpt = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), ogb__wmv)
        czy__bzpt.size = ogb__wmv
        if uykad__nard.has_runtime_cols:
            nic__ezmu = lir.Constant(lir.IntType(64), 0)
            for kmxx__agnd, t in enumerate(uykad__nard.arr_types):
                cyh__rpcy = getattr(zrbip__pbem, f'block_{kmxx__agnd}')
                scfng__urg = ListInstance(context, builder, types.List(t),
                    cyh__rpcy)
                jbbup__jilws = scfng__urg.size
                with cgutils.for_range(builder, jbbup__jilws) as imzw__jxk:
                    srroo__kwogj = imzw__jxk.index
                    arr = scfng__urg.getitem(srroo__kwogj)
                    jpy__orb = signature(array_info_type, t)
                    morfp__gauv = arr,
                    xkupc__jbj = array_to_info_codegen(context, builder,
                        jpy__orb, morfp__gauv)
                    czy__bzpt.inititem(builder.add(nic__ezmu, srroo__kwogj),
                        xkupc__jbj, incref=False)
                nic__ezmu = builder.add(nic__ezmu, jbbup__jilws)
        else:
            for t, kmxx__agnd in uykad__nard.type_to_blk.items():
                jbbup__jilws = context.get_constant(types.int64, len(
                    uykad__nard.block_to_arr_ind[kmxx__agnd]))
                cyh__rpcy = getattr(zrbip__pbem, f'block_{kmxx__agnd}')
                scfng__urg = ListInstance(context, builder, types.List(t),
                    cyh__rpcy)
                mor__lfvrp = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(uykad__nard.
                    block_to_arr_ind[kmxx__agnd], dtype=np.int64))
                qep__wtaq = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, mor__lfvrp)
                with cgutils.for_range(builder, jbbup__jilws) as imzw__jxk:
                    srroo__kwogj = imzw__jxk.index
                    ycfs__mrxom = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), qep__wtaq, srroo__kwogj)
                    ttqk__jgfm = signature(types.none, uykad__nard, types.
                        List(t), types.int64, types.int64)
                    cfdrb__uup = py_table, cyh__rpcy, srroo__kwogj, ycfs__mrxom
                    bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                        builder, ttqk__jgfm, cfdrb__uup)
                    arr = scfng__urg.getitem(srroo__kwogj)
                    jpy__orb = signature(array_info_type, t)
                    morfp__gauv = arr,
                    xkupc__jbj = array_to_info_codegen(context, builder,
                        jpy__orb, morfp__gauv)
                    czy__bzpt.inititem(ycfs__mrxom, xkupc__jbj, incref=False)
        oytk__epf = czy__bzpt.value
        iiwz__ghmy = signature(table_type, types.List(array_info_type))
        rpk__oadat = oytk__epf,
        cpp_table = arr_info_list_to_table_codegen(context, builder,
            iiwz__ghmy, rpk__oadat)
        context.nrt.decref(builder, types.List(array_info_type), oytk__epf)
        return cpp_table
    return table_type(uykad__nard, py_table_type_t), codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def py_data_to_cpp_table(py_table, extra_arrs_tup, in_col_inds_t,
    n_table_cols_t):
    hhz__phj = in_col_inds_t.instance_type.meta
    azejx__tavuk = {}
    wjyyi__lqk = get_overload_const_int(n_table_cols_t)
    krr__vmq = defaultdict(list)
    mdivj__gzn = {}
    for srroo__kwogj, pui__esvz in enumerate(hhz__phj):
        if pui__esvz in mdivj__gzn:
            krr__vmq[pui__esvz].append(srroo__kwogj)
        else:
            mdivj__gzn[pui__esvz] = srroo__kwogj
    xckm__lyk = (
        'def impl(py_table, extra_arrs_tup, in_col_inds_t, n_table_cols_t):\n')
    xckm__lyk += (
        f'  cpp_arr_list = alloc_empty_list_type({len(hhz__phj)}, array_info_type)\n'
        )
    if py_table != types.none:
        for kmxx__agnd in py_table.type_to_blk.values():
            leuj__xhri = [mdivj__gzn.get(srroo__kwogj, -1) for srroo__kwogj in
                py_table.block_to_arr_ind[kmxx__agnd]]
            azejx__tavuk[f'out_inds_{kmxx__agnd}'] = np.array(leuj__xhri,
                np.int64)
            azejx__tavuk[f'arr_inds_{kmxx__agnd}'] = np.array(py_table.
                block_to_arr_ind[kmxx__agnd], np.int64)
            xckm__lyk += (
                f'  arr_list_{kmxx__agnd} = get_table_block(py_table, {kmxx__agnd})\n'
                )
            xckm__lyk += f'  for i in range(len(arr_list_{kmxx__agnd})):\n'
            xckm__lyk += (
                f'    out_arr_ind_{kmxx__agnd} = out_inds_{kmxx__agnd}[i]\n')
            xckm__lyk += f'    if out_arr_ind_{kmxx__agnd} == -1:\n'
            xckm__lyk += f'      continue\n'
            xckm__lyk += (
                f'    arr_ind_{kmxx__agnd} = arr_inds_{kmxx__agnd}[i]\n')
            xckm__lyk += f"""    ensure_column_unboxed(py_table, arr_list_{kmxx__agnd}, i, arr_ind_{kmxx__agnd})
"""
            xckm__lyk += f"""    cpp_arr_list[out_arr_ind_{kmxx__agnd}] = array_to_info(arr_list_{kmxx__agnd}[i])
"""
        for ywk__zua, kibmq__kezy in krr__vmq.items():
            if ywk__zua < wjyyi__lqk:
                kmxx__agnd = py_table.block_nums[ywk__zua]
                kkkd__rouoe = py_table.block_offsets[ywk__zua]
                for ndyp__bnbar in kibmq__kezy:
                    xckm__lyk += f"""  cpp_arr_list[{ndyp__bnbar}] = array_to_info(arr_list_{kmxx__agnd}[{kkkd__rouoe}])
"""
    for srroo__kwogj in range(len(extra_arrs_tup)):
        gvhcq__ivem = mdivj__gzn.get(wjyyi__lqk + srroo__kwogj, -1)
        if gvhcq__ivem != -1:
            vmx__uzjfr = [gvhcq__ivem] + krr__vmq.get(wjyyi__lqk +
                srroo__kwogj, [])
            for ndyp__bnbar in vmx__uzjfr:
                xckm__lyk += f"""  cpp_arr_list[{ndyp__bnbar}] = array_to_info(extra_arrs_tup[{srroo__kwogj}])
"""
    xckm__lyk += f'  return arr_info_list_to_table(cpp_arr_list)\n'
    azejx__tavuk.update({'array_info_type': array_info_type,
        'alloc_empty_list_type': bodo.hiframes.table.alloc_empty_list_type,
        'get_table_block': bodo.hiframes.table.get_table_block,
        'ensure_column_unboxed': bodo.hiframes.table.ensure_column_unboxed,
        'array_to_info': array_to_info, 'arr_info_list_to_table':
        arr_info_list_to_table})
    zyocr__rqepd = {}
    exec(xckm__lyk, azejx__tavuk, zyocr__rqepd)
    return zyocr__rqepd['impl']


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
        yfpdh__saht = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='delete_table')
        builder.call(iox__vifm, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='shuffle_table')
        upaic__fxia = builder.call(iox__vifm, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return upaic__fxia
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
        yfpdh__saht = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='delete_shuffle_info')
        return builder.call(iox__vifm, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='reverse_shuffle_table')
        return builder.call(iox__vifm, args)
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
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(1), lir
            .IntType(1), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(8).as_pointer(), lir
            .IntType(64), lir.IntType(8).as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='hash_join_table')
        upaic__fxia = builder.call(iox__vifm, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return upaic__fxia
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
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='sort_values_table')
        upaic__fxia = builder.call(iox__vifm, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return upaic__fxia
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='sample_table')
        upaic__fxia = builder.call(iox__vifm, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return upaic__fxia
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='shuffle_renormalization')
        upaic__fxia = builder.call(iox__vifm, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return upaic__fxia
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='shuffle_renormalization_group')
        upaic__fxia = builder.call(iox__vifm, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return upaic__fxia
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna, drop_local_first):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1), lir.IntType(1)])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='drop_duplicates_table')
        upaic__fxia = builder.call(iox__vifm, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return upaic__fxia
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
        yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer()])
        iox__vifm = cgutils.get_or_insert_function(builder.module,
            yfpdh__saht, name='groupby_and_aggregate')
        upaic__fxia = builder.call(iox__vifm, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return upaic__fxia
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
    dpv__yxrn = array_to_info(in_arr)
    uopbv__guzi = array_to_info(in_values)
    kxqdd__gzzf = array_to_info(out_arr)
    htq__yzw = arr_info_list_to_table([dpv__yxrn, uopbv__guzi, kxqdd__gzzf])
    _array_isin(kxqdd__gzzf, dpv__yxrn, uopbv__guzi, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(htq__yzw)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.bool_, types.voidptr, array_info_type))


@numba.njit(no_cpython_wrapper=True)
def get_search_regex(in_arr, case, match, pat, out_arr):
    dpv__yxrn = array_to_info(in_arr)
    kxqdd__gzzf = array_to_info(out_arr)
    _get_search_regex(dpv__yxrn, case, match, pat, kxqdd__gzzf)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_array_typ, c_ind):
    from llvmlite import ir as lir
    vykw__ngr = col_array_typ.dtype
    if isinstance(vykw__ngr, types.Number) or vykw__ngr in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                dsunn__zdbp, yhwg__qzo = args
                dsunn__zdbp = builder.bitcast(dsunn__zdbp, lir.IntType(8).
                    as_pointer().as_pointer())
                pzcu__eycgw = lir.Constant(lir.IntType(64), c_ind)
                dknzi__pdfc = builder.load(builder.gep(dsunn__zdbp, [
                    pzcu__eycgw]))
                dknzi__pdfc = builder.bitcast(dknzi__pdfc, context.
                    get_data_type(vykw__ngr).as_pointer())
                return builder.load(builder.gep(dknzi__pdfc, [yhwg__qzo]))
            return vykw__ngr(types.voidptr, types.int64), codegen
        return getitem_func
    if col_array_typ in (bodo.string_array_type, bodo.binary_array_type):

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                dsunn__zdbp, yhwg__qzo = args
                dsunn__zdbp = builder.bitcast(dsunn__zdbp, lir.IntType(8).
                    as_pointer().as_pointer())
                pzcu__eycgw = lir.Constant(lir.IntType(64), c_ind)
                dknzi__pdfc = builder.load(builder.gep(dsunn__zdbp, [
                    pzcu__eycgw]))
                yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                ytqm__qys = cgutils.get_or_insert_function(builder.module,
                    yfpdh__saht, name='array_info_getitem')
                qjkn__eytk = cgutils.alloca_once(builder, lir.IntType(64))
                args = dknzi__pdfc, yhwg__qzo, qjkn__eytk
                tnk__nfvse = builder.call(ytqm__qys, args)
                return context.make_tuple(builder, sig.return_type, [
                    tnk__nfvse, builder.load(qjkn__eytk)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    if col_array_typ == bodo.libs.dict_arr_ext.dict_str_arr_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                uvl__rjijd = lir.Constant(lir.IntType(64), 1)
                pnz__ppzo = lir.Constant(lir.IntType(64), 2)
                dsunn__zdbp, yhwg__qzo = args
                dsunn__zdbp = builder.bitcast(dsunn__zdbp, lir.IntType(8).
                    as_pointer().as_pointer())
                pzcu__eycgw = lir.Constant(lir.IntType(64), c_ind)
                dknzi__pdfc = builder.load(builder.gep(dsunn__zdbp, [
                    pzcu__eycgw]))
                yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64)])
                hdzwf__pgx = cgutils.get_or_insert_function(builder.module,
                    yfpdh__saht, name='get_nested_info')
                args = dknzi__pdfc, pnz__ppzo
                ggf__kdfd = builder.call(hdzwf__pgx, args)
                yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer()])
                uidgm__zte = cgutils.get_or_insert_function(builder.module,
                    yfpdh__saht, name='array_info_getdata1')
                args = ggf__kdfd,
                imy__vgvuq = builder.call(uidgm__zte, args)
                imy__vgvuq = builder.bitcast(imy__vgvuq, context.
                    get_data_type(col_array_typ.indices_dtype).as_pointer())
                kob__nmxl = builder.sext(builder.load(builder.gep(
                    imy__vgvuq, [yhwg__qzo])), lir.IntType(64))
                args = dknzi__pdfc, uvl__rjijd
                biitj__npvm = builder.call(hdzwf__pgx, args)
                yfpdh__saht = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64).as_pointer()])
                ytqm__qys = cgutils.get_or_insert_function(builder.module,
                    yfpdh__saht, name='array_info_getitem')
                qjkn__eytk = cgutils.alloca_once(builder, lir.IntType(64))
                args = biitj__npvm, kob__nmxl, qjkn__eytk
                tnk__nfvse = builder.call(ytqm__qys, args)
                return context.make_tuple(builder, sig.return_type, [
                    tnk__nfvse, builder.load(qjkn__eytk)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{vykw__ngr}' column data type not supported"
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
                bjnw__hufpe, yhwg__qzo = args
                bjnw__hufpe = builder.bitcast(bjnw__hufpe, lir.IntType(8).
                    as_pointer().as_pointer())
                pzcu__eycgw = lir.Constant(lir.IntType(64), c_ind)
                dknzi__pdfc = builder.load(builder.gep(bjnw__hufpe, [
                    pzcu__eycgw]))
                sxpb__dwua = builder.bitcast(dknzi__pdfc, context.
                    get_data_type(types.bool_).as_pointer())
                njvjj__rauj = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    sxpb__dwua, yhwg__qzo)
                kttnl__neh = builder.icmp_unsigned('!=', njvjj__rauj, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(kttnl__neh, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        vykw__ngr = col_array_dtype.dtype
        if vykw__ngr in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    dsunn__zdbp, yhwg__qzo = args
                    dsunn__zdbp = builder.bitcast(dsunn__zdbp, lir.IntType(
                        8).as_pointer().as_pointer())
                    pzcu__eycgw = lir.Constant(lir.IntType(64), c_ind)
                    dknzi__pdfc = builder.load(builder.gep(dsunn__zdbp, [
                        pzcu__eycgw]))
                    dknzi__pdfc = builder.bitcast(dknzi__pdfc, context.
                        get_data_type(vykw__ngr).as_pointer())
                    gdof__exa = builder.load(builder.gep(dknzi__pdfc, [
                        yhwg__qzo]))
                    kttnl__neh = builder.icmp_unsigned('!=', gdof__exa, lir
                        .Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(kttnl__neh, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(vykw__ngr, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    dsunn__zdbp, yhwg__qzo = args
                    dsunn__zdbp = builder.bitcast(dsunn__zdbp, lir.IntType(
                        8).as_pointer().as_pointer())
                    pzcu__eycgw = lir.Constant(lir.IntType(64), c_ind)
                    dknzi__pdfc = builder.load(builder.gep(dsunn__zdbp, [
                        pzcu__eycgw]))
                    dknzi__pdfc = builder.bitcast(dknzi__pdfc, context.
                        get_data_type(vykw__ngr).as_pointer())
                    gdof__exa = builder.load(builder.gep(dknzi__pdfc, [
                        yhwg__qzo]))
                    uhdd__ugmge = signature(types.bool_, vykw__ngr)
                    njvjj__rauj = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, uhdd__ugmge, (gdof__exa,))
                    return builder.not_(builder.sext(njvjj__rauj, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
