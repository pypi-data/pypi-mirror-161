"""helper functions for code generation with llvmlite
"""
import llvmlite.binding as ll
from llvmlite import ir as lir
from numba.core import cgutils, types
import bodo
from bodo.libs import array_ext, hdist
ll.add_symbol('array_getitem', array_ext.array_getitem)
ll.add_symbol('seq_getitem', array_ext.seq_getitem)
ll.add_symbol('list_check', array_ext.list_check)
ll.add_symbol('dict_keys', array_ext.dict_keys)
ll.add_symbol('dict_values', array_ext.dict_values)
ll.add_symbol('dict_merge_from_seq2', array_ext.dict_merge_from_seq2)
ll.add_symbol('is_na_value', array_ext.is_na_value)


def set_bitmap_bit(builder, null_bitmap_ptr, ind, val):
    hfe__qemh = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    grxb__itrok = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    irezi__swyi = builder.gep(null_bitmap_ptr, [hfe__qemh], inbounds=True)
    ulfmt__sfx = builder.load(irezi__swyi)
    njvs__igtyw = lir.ArrayType(lir.IntType(8), 8)
    vmwmj__zbn = cgutils.alloca_once_value(builder, lir.Constant(
        njvs__igtyw, (1, 2, 4, 8, 16, 32, 64, 128)))
    iwbsd__yexcq = builder.load(builder.gep(vmwmj__zbn, [lir.Constant(lir.
        IntType(64), 0), grxb__itrok], inbounds=True))
    if val:
        builder.store(builder.or_(ulfmt__sfx, iwbsd__yexcq), irezi__swyi)
    else:
        iwbsd__yexcq = builder.xor(iwbsd__yexcq, lir.Constant(lir.IntType(8
            ), -1))
        builder.store(builder.and_(ulfmt__sfx, iwbsd__yexcq), irezi__swyi)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    hfe__qemh = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    grxb__itrok = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    ulfmt__sfx = builder.load(builder.gep(null_bitmap_ptr, [hfe__qemh],
        inbounds=True))
    njvs__igtyw = lir.ArrayType(lir.IntType(8), 8)
    vmwmj__zbn = cgutils.alloca_once_value(builder, lir.Constant(
        njvs__igtyw, (1, 2, 4, 8, 16, 32, 64, 128)))
    iwbsd__yexcq = builder.load(builder.gep(vmwmj__zbn, [lir.Constant(lir.
        IntType(64), 0), grxb__itrok], inbounds=True))
    return builder.and_(ulfmt__sfx, iwbsd__yexcq)


def pyarray_check(builder, context, obj):
    cfu__jfco = context.get_argument_type(types.pyobject)
    mjqu__ohtr = lir.FunctionType(lir.IntType(32), [cfu__jfco])
    jotzk__odq = cgutils.get_or_insert_function(builder.module, mjqu__ohtr,
        name='is_np_array')
    return builder.call(jotzk__odq, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    cfu__jfco = context.get_argument_type(types.pyobject)
    nzf__gatw = context.get_value_type(types.intp)
    kop__liw = lir.FunctionType(lir.IntType(8).as_pointer(), [cfu__jfco,
        nzf__gatw])
    uapoh__jjcyb = cgutils.get_or_insert_function(builder.module, kop__liw,
        name='array_getptr1')
    acxy__nkks = lir.FunctionType(cfu__jfco, [cfu__jfco, lir.IntType(8).
        as_pointer()])
    ify__pzi = cgutils.get_or_insert_function(builder.module, acxy__nkks,
        name='array_getitem')
    fckbn__uis = builder.call(uapoh__jjcyb, [arr_obj, ind])
    return builder.call(ify__pzi, [arr_obj, fckbn__uis])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    cfu__jfco = context.get_argument_type(types.pyobject)
    nzf__gatw = context.get_value_type(types.intp)
    kop__liw = lir.FunctionType(lir.IntType(8).as_pointer(), [cfu__jfco,
        nzf__gatw])
    uapoh__jjcyb = cgutils.get_or_insert_function(builder.module, kop__liw,
        name='array_getptr1')
    nnrij__tcmk = lir.FunctionType(lir.VoidType(), [cfu__jfco, lir.IntType(
        8).as_pointer(), cfu__jfco])
    cddut__uahei = cgutils.get_or_insert_function(builder.module,
        nnrij__tcmk, name='array_setitem')
    fckbn__uis = builder.call(uapoh__jjcyb, [arr_obj, ind])
    builder.call(cddut__uahei, [arr_obj, fckbn__uis, val_obj])


def seq_getitem(builder, context, obj, ind):
    cfu__jfco = context.get_argument_type(types.pyobject)
    nzf__gatw = context.get_value_type(types.intp)
    sgv__njwbw = lir.FunctionType(cfu__jfco, [cfu__jfco, nzf__gatw])
    fevtq__ppt = cgutils.get_or_insert_function(builder.module, sgv__njwbw,
        name='seq_getitem')
    return builder.call(fevtq__ppt, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    cfu__jfco = context.get_argument_type(types.pyobject)
    owt__wci = lir.FunctionType(lir.IntType(32), [cfu__jfco, cfu__jfco])
    drtpf__lyk = cgutils.get_or_insert_function(builder.module, owt__wci,
        name='is_na_value')
    return builder.call(drtpf__lyk, [val, C_NA])


def list_check(builder, context, obj):
    cfu__jfco = context.get_argument_type(types.pyobject)
    cxft__xvhi = context.get_value_type(types.int32)
    wwbwf__vhdye = lir.FunctionType(cxft__xvhi, [cfu__jfco])
    reu__via = cgutils.get_or_insert_function(builder.module, wwbwf__vhdye,
        name='list_check')
    return builder.call(reu__via, [obj])


def dict_keys(builder, context, obj):
    cfu__jfco = context.get_argument_type(types.pyobject)
    wwbwf__vhdye = lir.FunctionType(cfu__jfco, [cfu__jfco])
    reu__via = cgutils.get_or_insert_function(builder.module, wwbwf__vhdye,
        name='dict_keys')
    return builder.call(reu__via, [obj])


def dict_values(builder, context, obj):
    cfu__jfco = context.get_argument_type(types.pyobject)
    wwbwf__vhdye = lir.FunctionType(cfu__jfco, [cfu__jfco])
    reu__via = cgutils.get_or_insert_function(builder.module, wwbwf__vhdye,
        name='dict_values')
    return builder.call(reu__via, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    cfu__jfco = context.get_argument_type(types.pyobject)
    wwbwf__vhdye = lir.FunctionType(lir.VoidType(), [cfu__jfco, cfu__jfco])
    reu__via = cgutils.get_or_insert_function(builder.module, wwbwf__vhdye,
        name='dict_merge_from_seq2')
    builder.call(reu__via, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    dacn__hpmxw = cgutils.alloca_once_value(builder, val)
    ixjbh__znen = list_check(builder, context, val)
    inq__gyv = builder.icmp_unsigned('!=', ixjbh__znen, lir.Constant(
        ixjbh__znen.type, 0))
    with builder.if_then(inq__gyv):
        kac__zxl = context.insert_const_string(builder.module, 'numpy')
        pmf__srcc = c.pyapi.import_module_noblock(kac__zxl)
        jtph__uwcry = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            jtph__uwcry = str(typ.dtype)
        rsev__gmj = c.pyapi.object_getattr_string(pmf__srcc, jtph__uwcry)
        excrg__fode = builder.load(dacn__hpmxw)
        rin__qzx = c.pyapi.call_method(pmf__srcc, 'asarray', (excrg__fode,
            rsev__gmj))
        builder.store(rin__qzx, dacn__hpmxw)
        c.pyapi.decref(pmf__srcc)
        c.pyapi.decref(rsev__gmj)
    val = builder.load(dacn__hpmxw)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        sfgqo__mln = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        akb__ngfeq, jvlg__pgoet = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [sfgqo__mln])
        context.nrt.decref(builder, typ, sfgqo__mln)
        return cgutils.pack_array(builder, [jvlg__pgoet])
    if isinstance(typ, (StructType, types.BaseTuple)):
        kac__zxl = context.insert_const_string(builder.module, 'pandas')
        znj__wquwg = c.pyapi.import_module_noblock(kac__zxl)
        C_NA = c.pyapi.object_getattr_string(znj__wquwg, 'NA')
        ufuka__xll = bodo.utils.transform.get_type_alloc_counts(typ)
        iql__ost = context.make_tuple(builder, types.Tuple(ufuka__xll * [
            types.int64]), ufuka__xll * [context.get_constant(types.int64, 0)])
        vtysc__fqo = cgutils.alloca_once_value(builder, iql__ost)
        rlvhj__avpew = 0
        wgghb__mqzh = typ.data if isinstance(typ, StructType) else typ.types
        for oncqg__ypsg, t in enumerate(wgghb__mqzh):
            pgbuu__auou = bodo.utils.transform.get_type_alloc_counts(t)
            if pgbuu__auou == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    oncqg__ypsg])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, oncqg__ypsg)
            hfcn__mgi = is_na_value(builder, context, val_obj, C_NA)
            dxof__bvkr = builder.icmp_unsigned('!=', hfcn__mgi, lir.
                Constant(hfcn__mgi.type, 1))
            with builder.if_then(dxof__bvkr):
                iql__ost = builder.load(vtysc__fqo)
                ajr__xdfm = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for oncqg__ypsg in range(pgbuu__auou):
                    kat__tgeow = builder.extract_value(iql__ost, 
                        rlvhj__avpew + oncqg__ypsg)
                    koc__vls = builder.extract_value(ajr__xdfm, oncqg__ypsg)
                    iql__ost = builder.insert_value(iql__ost, builder.add(
                        kat__tgeow, koc__vls), rlvhj__avpew + oncqg__ypsg)
                builder.store(iql__ost, vtysc__fqo)
            rlvhj__avpew += pgbuu__auou
        c.pyapi.decref(znj__wquwg)
        c.pyapi.decref(C_NA)
        return builder.load(vtysc__fqo)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    kac__zxl = context.insert_const_string(builder.module, 'pandas')
    znj__wquwg = c.pyapi.import_module_noblock(kac__zxl)
    C_NA = c.pyapi.object_getattr_string(znj__wquwg, 'NA')
    ufuka__xll = bodo.utils.transform.get_type_alloc_counts(typ)
    iql__ost = context.make_tuple(builder, types.Tuple(ufuka__xll * [types.
        int64]), [n] + (ufuka__xll - 1) * [context.get_constant(types.int64,
        0)])
    vtysc__fqo = cgutils.alloca_once_value(builder, iql__ost)
    with cgutils.for_range(builder, n) as slj__kwadg:
        gdl__lat = slj__kwadg.index
        qcxva__wkjx = seq_getitem(builder, context, arr_obj, gdl__lat)
        hfcn__mgi = is_na_value(builder, context, qcxva__wkjx, C_NA)
        dxof__bvkr = builder.icmp_unsigned('!=', hfcn__mgi, lir.Constant(
            hfcn__mgi.type, 1))
        with builder.if_then(dxof__bvkr):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                iql__ost = builder.load(vtysc__fqo)
                ajr__xdfm = get_array_elem_counts(c, builder, context,
                    qcxva__wkjx, typ.dtype)
                for oncqg__ypsg in range(ufuka__xll - 1):
                    kat__tgeow = builder.extract_value(iql__ost, 
                        oncqg__ypsg + 1)
                    koc__vls = builder.extract_value(ajr__xdfm, oncqg__ypsg)
                    iql__ost = builder.insert_value(iql__ost, builder.add(
                        kat__tgeow, koc__vls), oncqg__ypsg + 1)
                builder.store(iql__ost, vtysc__fqo)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                rlvhj__avpew = 1
                for oncqg__ypsg, t in enumerate(typ.data):
                    pgbuu__auou = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if pgbuu__auou == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(qcxva__wkjx,
                            oncqg__ypsg)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(qcxva__wkjx,
                            typ.names[oncqg__ypsg])
                    hfcn__mgi = is_na_value(builder, context, val_obj, C_NA)
                    dxof__bvkr = builder.icmp_unsigned('!=', hfcn__mgi, lir
                        .Constant(hfcn__mgi.type, 1))
                    with builder.if_then(dxof__bvkr):
                        iql__ost = builder.load(vtysc__fqo)
                        ajr__xdfm = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for oncqg__ypsg in range(pgbuu__auou):
                            kat__tgeow = builder.extract_value(iql__ost, 
                                rlvhj__avpew + oncqg__ypsg)
                            koc__vls = builder.extract_value(ajr__xdfm,
                                oncqg__ypsg)
                            iql__ost = builder.insert_value(iql__ost,
                                builder.add(kat__tgeow, koc__vls), 
                                rlvhj__avpew + oncqg__ypsg)
                        builder.store(iql__ost, vtysc__fqo)
                    rlvhj__avpew += pgbuu__auou
            else:
                assert isinstance(typ, MapArrayType), typ
                iql__ost = builder.load(vtysc__fqo)
                mqmx__xab = dict_keys(builder, context, qcxva__wkjx)
                svvt__agsag = dict_values(builder, context, qcxva__wkjx)
                piy__tod = get_array_elem_counts(c, builder, context,
                    mqmx__xab, typ.key_arr_type)
                rgj__vjwvh = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for oncqg__ypsg in range(1, rgj__vjwvh + 1):
                    kat__tgeow = builder.extract_value(iql__ost, oncqg__ypsg)
                    koc__vls = builder.extract_value(piy__tod, oncqg__ypsg - 1)
                    iql__ost = builder.insert_value(iql__ost, builder.add(
                        kat__tgeow, koc__vls), oncqg__ypsg)
                wmyzr__ymbf = get_array_elem_counts(c, builder, context,
                    svvt__agsag, typ.value_arr_type)
                for oncqg__ypsg in range(rgj__vjwvh + 1, ufuka__xll):
                    kat__tgeow = builder.extract_value(iql__ost, oncqg__ypsg)
                    koc__vls = builder.extract_value(wmyzr__ymbf, 
                        oncqg__ypsg - rgj__vjwvh)
                    iql__ost = builder.insert_value(iql__ost, builder.add(
                        kat__tgeow, koc__vls), oncqg__ypsg)
                builder.store(iql__ost, vtysc__fqo)
                c.pyapi.decref(mqmx__xab)
                c.pyapi.decref(svvt__agsag)
        c.pyapi.decref(qcxva__wkjx)
    c.pyapi.decref(znj__wquwg)
    c.pyapi.decref(C_NA)
    return builder.load(vtysc__fqo)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    qmhj__asb = n_elems.type.count
    assert qmhj__asb >= 1
    xelc__tzgph = builder.extract_value(n_elems, 0)
    if qmhj__asb != 1:
        auqut__lrl = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, oncqg__ypsg) for oncqg__ypsg in range(1, qmhj__asb)])
        pjy__zani = types.Tuple([types.int64] * (qmhj__asb - 1))
    else:
        auqut__lrl = context.get_dummy_value()
        pjy__zani = types.none
    rhrxo__estj = types.TypeRef(arr_type)
    lxh__yojt = arr_type(types.int64, rhrxo__estj, pjy__zani)
    args = [xelc__tzgph, context.get_dummy_value(), auqut__lrl]
    enmkr__lxbe = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        akb__ngfeq, udj__tqfwe = c.pyapi.call_jit_code(enmkr__lxbe,
            lxh__yojt, args)
    else:
        udj__tqfwe = context.compile_internal(builder, enmkr__lxbe,
            lxh__yojt, args)
    return udj__tqfwe


def is_ll_eq(builder, val1, val2):
    nqgs__jkvi = val1.type.pointee
    znm__gck = val2.type.pointee
    assert nqgs__jkvi == znm__gck, 'invalid llvm value comparison'
    if isinstance(nqgs__jkvi, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(nqgs__jkvi.elements) if isinstance(nqgs__jkvi, lir.
            BaseStructType) else nqgs__jkvi.count
        uxe__nfi = lir.Constant(lir.IntType(1), 1)
        for oncqg__ypsg in range(n_elems):
            mooa__ydr = lir.IntType(32)(0)
            wbm__ajzv = lir.IntType(32)(oncqg__ypsg)
            vtm__iazz = builder.gep(val1, [mooa__ydr, wbm__ajzv], inbounds=True
                )
            bnr__mhdt = builder.gep(val2, [mooa__ydr, wbm__ajzv], inbounds=True
                )
            uxe__nfi = builder.and_(uxe__nfi, is_ll_eq(builder, vtm__iazz,
                bnr__mhdt))
        return uxe__nfi
    cuav__aruz = builder.load(val1)
    ato__zmqj = builder.load(val2)
    if cuav__aruz.type in (lir.FloatType(), lir.DoubleType()):
        wyybk__fzpq = 32 if cuav__aruz.type == lir.FloatType() else 64
        cuav__aruz = builder.bitcast(cuav__aruz, lir.IntType(wyybk__fzpq))
        ato__zmqj = builder.bitcast(ato__zmqj, lir.IntType(wyybk__fzpq))
    return builder.icmp_unsigned('==', cuav__aruz, ato__zmqj)
