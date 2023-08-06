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
    qqkis__fwyep = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    ehi__ptrv = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    zla__bbwcl = builder.gep(null_bitmap_ptr, [qqkis__fwyep], inbounds=True)
    zjtqe__zabo = builder.load(zla__bbwcl)
    qzzvu__omyjk = lir.ArrayType(lir.IntType(8), 8)
    pver__nyyr = cgutils.alloca_once_value(builder, lir.Constant(
        qzzvu__omyjk, (1, 2, 4, 8, 16, 32, 64, 128)))
    rirs__krtd = builder.load(builder.gep(pver__nyyr, [lir.Constant(lir.
        IntType(64), 0), ehi__ptrv], inbounds=True))
    if val:
        builder.store(builder.or_(zjtqe__zabo, rirs__krtd), zla__bbwcl)
    else:
        rirs__krtd = builder.xor(rirs__krtd, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(zjtqe__zabo, rirs__krtd), zla__bbwcl)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    qqkis__fwyep = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    ehi__ptrv = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    zjtqe__zabo = builder.load(builder.gep(null_bitmap_ptr, [qqkis__fwyep],
        inbounds=True))
    qzzvu__omyjk = lir.ArrayType(lir.IntType(8), 8)
    pver__nyyr = cgutils.alloca_once_value(builder, lir.Constant(
        qzzvu__omyjk, (1, 2, 4, 8, 16, 32, 64, 128)))
    rirs__krtd = builder.load(builder.gep(pver__nyyr, [lir.Constant(lir.
        IntType(64), 0), ehi__ptrv], inbounds=True))
    return builder.and_(zjtqe__zabo, rirs__krtd)


def pyarray_check(builder, context, obj):
    zzve__ensj = context.get_argument_type(types.pyobject)
    zijju__emv = lir.FunctionType(lir.IntType(32), [zzve__ensj])
    ifcge__bmlks = cgutils.get_or_insert_function(builder.module,
        zijju__emv, name='is_np_array')
    return builder.call(ifcge__bmlks, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    zzve__ensj = context.get_argument_type(types.pyobject)
    vzt__ekqz = context.get_value_type(types.intp)
    edbxe__czvjn = lir.FunctionType(lir.IntType(8).as_pointer(), [
        zzve__ensj, vzt__ekqz])
    xid__vpr = cgutils.get_or_insert_function(builder.module, edbxe__czvjn,
        name='array_getptr1')
    lrjet__bgkqw = lir.FunctionType(zzve__ensj, [zzve__ensj, lir.IntType(8)
        .as_pointer()])
    obxv__nbaow = cgutils.get_or_insert_function(builder.module,
        lrjet__bgkqw, name='array_getitem')
    mul__zyz = builder.call(xid__vpr, [arr_obj, ind])
    return builder.call(obxv__nbaow, [arr_obj, mul__zyz])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    zzve__ensj = context.get_argument_type(types.pyobject)
    vzt__ekqz = context.get_value_type(types.intp)
    edbxe__czvjn = lir.FunctionType(lir.IntType(8).as_pointer(), [
        zzve__ensj, vzt__ekqz])
    xid__vpr = cgutils.get_or_insert_function(builder.module, edbxe__czvjn,
        name='array_getptr1')
    xykk__ptw = lir.FunctionType(lir.VoidType(), [zzve__ensj, lir.IntType(8
        ).as_pointer(), zzve__ensj])
    vcvhb__fsfog = cgutils.get_or_insert_function(builder.module, xykk__ptw,
        name='array_setitem')
    mul__zyz = builder.call(xid__vpr, [arr_obj, ind])
    builder.call(vcvhb__fsfog, [arr_obj, mul__zyz, val_obj])


def seq_getitem(builder, context, obj, ind):
    zzve__ensj = context.get_argument_type(types.pyobject)
    vzt__ekqz = context.get_value_type(types.intp)
    calt__zxg = lir.FunctionType(zzve__ensj, [zzve__ensj, vzt__ekqz])
    xxirl__die = cgutils.get_or_insert_function(builder.module, calt__zxg,
        name='seq_getitem')
    return builder.call(xxirl__die, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    zzve__ensj = context.get_argument_type(types.pyobject)
    sizm__lmxiv = lir.FunctionType(lir.IntType(32), [zzve__ensj, zzve__ensj])
    vjn__soyn = cgutils.get_or_insert_function(builder.module, sizm__lmxiv,
        name='is_na_value')
    return builder.call(vjn__soyn, [val, C_NA])


def list_check(builder, context, obj):
    zzve__ensj = context.get_argument_type(types.pyobject)
    kfze__zey = context.get_value_type(types.int32)
    voyd__wiq = lir.FunctionType(kfze__zey, [zzve__ensj])
    wjxu__zbicl = cgutils.get_or_insert_function(builder.module, voyd__wiq,
        name='list_check')
    return builder.call(wjxu__zbicl, [obj])


def dict_keys(builder, context, obj):
    zzve__ensj = context.get_argument_type(types.pyobject)
    voyd__wiq = lir.FunctionType(zzve__ensj, [zzve__ensj])
    wjxu__zbicl = cgutils.get_or_insert_function(builder.module, voyd__wiq,
        name='dict_keys')
    return builder.call(wjxu__zbicl, [obj])


def dict_values(builder, context, obj):
    zzve__ensj = context.get_argument_type(types.pyobject)
    voyd__wiq = lir.FunctionType(zzve__ensj, [zzve__ensj])
    wjxu__zbicl = cgutils.get_or_insert_function(builder.module, voyd__wiq,
        name='dict_values')
    return builder.call(wjxu__zbicl, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    zzve__ensj = context.get_argument_type(types.pyobject)
    voyd__wiq = lir.FunctionType(lir.VoidType(), [zzve__ensj, zzve__ensj])
    wjxu__zbicl = cgutils.get_or_insert_function(builder.module, voyd__wiq,
        name='dict_merge_from_seq2')
    builder.call(wjxu__zbicl, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    jouvt__mktjm = cgutils.alloca_once_value(builder, val)
    rga__aeeod = list_check(builder, context, val)
    tjqb__pxalb = builder.icmp_unsigned('!=', rga__aeeod, lir.Constant(
        rga__aeeod.type, 0))
    with builder.if_then(tjqb__pxalb):
        oii__xwb = context.insert_const_string(builder.module, 'numpy')
        wjbp__jorv = c.pyapi.import_module_noblock(oii__xwb)
        plgb__rqngp = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            plgb__rqngp = str(typ.dtype)
        smlt__okehq = c.pyapi.object_getattr_string(wjbp__jorv, plgb__rqngp)
        aepec__nfqui = builder.load(jouvt__mktjm)
        smnxd__iak = c.pyapi.call_method(wjbp__jorv, 'asarray', (
            aepec__nfqui, smlt__okehq))
        builder.store(smnxd__iak, jouvt__mktjm)
        c.pyapi.decref(wjbp__jorv)
        c.pyapi.decref(smlt__okehq)
    val = builder.load(jouvt__mktjm)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        goc__cat = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        anooa__zhc, rpkhh__ullmp = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [goc__cat])
        context.nrt.decref(builder, typ, goc__cat)
        return cgutils.pack_array(builder, [rpkhh__ullmp])
    if isinstance(typ, (StructType, types.BaseTuple)):
        oii__xwb = context.insert_const_string(builder.module, 'pandas')
        gwpmj__mppxt = c.pyapi.import_module_noblock(oii__xwb)
        C_NA = c.pyapi.object_getattr_string(gwpmj__mppxt, 'NA')
        wkl__vnwj = bodo.utils.transform.get_type_alloc_counts(typ)
        txtzk__zlmnd = context.make_tuple(builder, types.Tuple(wkl__vnwj *
            [types.int64]), wkl__vnwj * [context.get_constant(types.int64, 0)])
        kxd__bduvx = cgutils.alloca_once_value(builder, txtzk__zlmnd)
        vlg__jnk = 0
        gcij__pca = typ.data if isinstance(typ, StructType) else typ.types
        for lpfi__tnpd, t in enumerate(gcij__pca):
            mxuz__zpi = bodo.utils.transform.get_type_alloc_counts(t)
            if mxuz__zpi == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    lpfi__tnpd])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, lpfi__tnpd)
            oau__vvqhw = is_na_value(builder, context, val_obj, C_NA)
            tqwe__qph = builder.icmp_unsigned('!=', oau__vvqhw, lir.
                Constant(oau__vvqhw.type, 1))
            with builder.if_then(tqwe__qph):
                txtzk__zlmnd = builder.load(kxd__bduvx)
                bhnz__xju = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for lpfi__tnpd in range(mxuz__zpi):
                    iep__knbve = builder.extract_value(txtzk__zlmnd, 
                        vlg__jnk + lpfi__tnpd)
                    fqx__lhxp = builder.extract_value(bhnz__xju, lpfi__tnpd)
                    txtzk__zlmnd = builder.insert_value(txtzk__zlmnd,
                        builder.add(iep__knbve, fqx__lhxp), vlg__jnk +
                        lpfi__tnpd)
                builder.store(txtzk__zlmnd, kxd__bduvx)
            vlg__jnk += mxuz__zpi
        c.pyapi.decref(gwpmj__mppxt)
        c.pyapi.decref(C_NA)
        return builder.load(kxd__bduvx)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    oii__xwb = context.insert_const_string(builder.module, 'pandas')
    gwpmj__mppxt = c.pyapi.import_module_noblock(oii__xwb)
    C_NA = c.pyapi.object_getattr_string(gwpmj__mppxt, 'NA')
    wkl__vnwj = bodo.utils.transform.get_type_alloc_counts(typ)
    txtzk__zlmnd = context.make_tuple(builder, types.Tuple(wkl__vnwj * [
        types.int64]), [n] + (wkl__vnwj - 1) * [context.get_constant(types.
        int64, 0)])
    kxd__bduvx = cgutils.alloca_once_value(builder, txtzk__zlmnd)
    with cgutils.for_range(builder, n) as hrt__cfz:
        try__ghyoz = hrt__cfz.index
        cythn__tfl = seq_getitem(builder, context, arr_obj, try__ghyoz)
        oau__vvqhw = is_na_value(builder, context, cythn__tfl, C_NA)
        tqwe__qph = builder.icmp_unsigned('!=', oau__vvqhw, lir.Constant(
            oau__vvqhw.type, 1))
        with builder.if_then(tqwe__qph):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                txtzk__zlmnd = builder.load(kxd__bduvx)
                bhnz__xju = get_array_elem_counts(c, builder, context,
                    cythn__tfl, typ.dtype)
                for lpfi__tnpd in range(wkl__vnwj - 1):
                    iep__knbve = builder.extract_value(txtzk__zlmnd, 
                        lpfi__tnpd + 1)
                    fqx__lhxp = builder.extract_value(bhnz__xju, lpfi__tnpd)
                    txtzk__zlmnd = builder.insert_value(txtzk__zlmnd,
                        builder.add(iep__knbve, fqx__lhxp), lpfi__tnpd + 1)
                builder.store(txtzk__zlmnd, kxd__bduvx)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                vlg__jnk = 1
                for lpfi__tnpd, t in enumerate(typ.data):
                    mxuz__zpi = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if mxuz__zpi == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(cythn__tfl, lpfi__tnpd)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(cythn__tfl,
                            typ.names[lpfi__tnpd])
                    oau__vvqhw = is_na_value(builder, context, val_obj, C_NA)
                    tqwe__qph = builder.icmp_unsigned('!=', oau__vvqhw, lir
                        .Constant(oau__vvqhw.type, 1))
                    with builder.if_then(tqwe__qph):
                        txtzk__zlmnd = builder.load(kxd__bduvx)
                        bhnz__xju = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for lpfi__tnpd in range(mxuz__zpi):
                            iep__knbve = builder.extract_value(txtzk__zlmnd,
                                vlg__jnk + lpfi__tnpd)
                            fqx__lhxp = builder.extract_value(bhnz__xju,
                                lpfi__tnpd)
                            txtzk__zlmnd = builder.insert_value(txtzk__zlmnd,
                                builder.add(iep__knbve, fqx__lhxp), 
                                vlg__jnk + lpfi__tnpd)
                        builder.store(txtzk__zlmnd, kxd__bduvx)
                    vlg__jnk += mxuz__zpi
            else:
                assert isinstance(typ, MapArrayType), typ
                txtzk__zlmnd = builder.load(kxd__bduvx)
                rqv__blqx = dict_keys(builder, context, cythn__tfl)
                gitc__qgjbj = dict_values(builder, context, cythn__tfl)
                dfzh__jnq = get_array_elem_counts(c, builder, context,
                    rqv__blqx, typ.key_arr_type)
                mlu__zwmgz = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for lpfi__tnpd in range(1, mlu__zwmgz + 1):
                    iep__knbve = builder.extract_value(txtzk__zlmnd, lpfi__tnpd
                        )
                    fqx__lhxp = builder.extract_value(dfzh__jnq, lpfi__tnpd - 1
                        )
                    txtzk__zlmnd = builder.insert_value(txtzk__zlmnd,
                        builder.add(iep__knbve, fqx__lhxp), lpfi__tnpd)
                ulzx__rzmd = get_array_elem_counts(c, builder, context,
                    gitc__qgjbj, typ.value_arr_type)
                for lpfi__tnpd in range(mlu__zwmgz + 1, wkl__vnwj):
                    iep__knbve = builder.extract_value(txtzk__zlmnd, lpfi__tnpd
                        )
                    fqx__lhxp = builder.extract_value(ulzx__rzmd, 
                        lpfi__tnpd - mlu__zwmgz)
                    txtzk__zlmnd = builder.insert_value(txtzk__zlmnd,
                        builder.add(iep__knbve, fqx__lhxp), lpfi__tnpd)
                builder.store(txtzk__zlmnd, kxd__bduvx)
                c.pyapi.decref(rqv__blqx)
                c.pyapi.decref(gitc__qgjbj)
        c.pyapi.decref(cythn__tfl)
    c.pyapi.decref(gwpmj__mppxt)
    c.pyapi.decref(C_NA)
    return builder.load(kxd__bduvx)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    ttnr__mtifp = n_elems.type.count
    assert ttnr__mtifp >= 1
    gfhc__bxkhi = builder.extract_value(n_elems, 0)
    if ttnr__mtifp != 1:
        dizb__mbgcv = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, lpfi__tnpd) for lpfi__tnpd in range(1, ttnr__mtifp)])
        qihv__fwgi = types.Tuple([types.int64] * (ttnr__mtifp - 1))
    else:
        dizb__mbgcv = context.get_dummy_value()
        qihv__fwgi = types.none
    xnl__lat = types.TypeRef(arr_type)
    nqej__vzoy = arr_type(types.int64, xnl__lat, qihv__fwgi)
    args = [gfhc__bxkhi, context.get_dummy_value(), dizb__mbgcv]
    ogv__lycb = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        anooa__zhc, heml__xtowo = c.pyapi.call_jit_code(ogv__lycb,
            nqej__vzoy, args)
    else:
        heml__xtowo = context.compile_internal(builder, ogv__lycb,
            nqej__vzoy, args)
    return heml__xtowo


def is_ll_eq(builder, val1, val2):
    bkwm__ircl = val1.type.pointee
    xjf__xxuzn = val2.type.pointee
    assert bkwm__ircl == xjf__xxuzn, 'invalid llvm value comparison'
    if isinstance(bkwm__ircl, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(bkwm__ircl.elements) if isinstance(bkwm__ircl, lir.
            BaseStructType) else bkwm__ircl.count
        rqylj__yjcg = lir.Constant(lir.IntType(1), 1)
        for lpfi__tnpd in range(n_elems):
            bjhl__hdjv = lir.IntType(32)(0)
            rnrw__xft = lir.IntType(32)(lpfi__tnpd)
            lrlij__ebaxf = builder.gep(val1, [bjhl__hdjv, rnrw__xft],
                inbounds=True)
            rprzs__iopz = builder.gep(val2, [bjhl__hdjv, rnrw__xft],
                inbounds=True)
            rqylj__yjcg = builder.and_(rqylj__yjcg, is_ll_eq(builder,
                lrlij__ebaxf, rprzs__iopz))
        return rqylj__yjcg
    vnuhe__esh = builder.load(val1)
    gmo__oeat = builder.load(val2)
    if vnuhe__esh.type in (lir.FloatType(), lir.DoubleType()):
        nzlzr__amx = 32 if vnuhe__esh.type == lir.FloatType() else 64
        vnuhe__esh = builder.bitcast(vnuhe__esh, lir.IntType(nzlzr__amx))
        gmo__oeat = builder.bitcast(gmo__oeat, lir.IntType(nzlzr__amx))
    return builder.icmp_unsigned('==', vnuhe__esh, gmo__oeat)
