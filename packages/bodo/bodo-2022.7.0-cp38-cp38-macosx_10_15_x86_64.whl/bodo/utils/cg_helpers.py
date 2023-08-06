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
    dnmo__arqap = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    dekrv__yyi = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    cdro__ulsse = builder.gep(null_bitmap_ptr, [dnmo__arqap], inbounds=True)
    hbp__ycw = builder.load(cdro__ulsse)
    ctn__jsv = lir.ArrayType(lir.IntType(8), 8)
    slf__tonbf = cgutils.alloca_once_value(builder, lir.Constant(ctn__jsv,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    lzcro__meadt = builder.load(builder.gep(slf__tonbf, [lir.Constant(lir.
        IntType(64), 0), dekrv__yyi], inbounds=True))
    if val:
        builder.store(builder.or_(hbp__ycw, lzcro__meadt), cdro__ulsse)
    else:
        lzcro__meadt = builder.xor(lzcro__meadt, lir.Constant(lir.IntType(8
            ), -1))
        builder.store(builder.and_(hbp__ycw, lzcro__meadt), cdro__ulsse)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    dnmo__arqap = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    dekrv__yyi = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    hbp__ycw = builder.load(builder.gep(null_bitmap_ptr, [dnmo__arqap],
        inbounds=True))
    ctn__jsv = lir.ArrayType(lir.IntType(8), 8)
    slf__tonbf = cgutils.alloca_once_value(builder, lir.Constant(ctn__jsv,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    lzcro__meadt = builder.load(builder.gep(slf__tonbf, [lir.Constant(lir.
        IntType(64), 0), dekrv__yyi], inbounds=True))
    return builder.and_(hbp__ycw, lzcro__meadt)


def pyarray_check(builder, context, obj):
    lsdlo__rfqeo = context.get_argument_type(types.pyobject)
    rukqu__dolcz = lir.FunctionType(lir.IntType(32), [lsdlo__rfqeo])
    aciwt__fylc = cgutils.get_or_insert_function(builder.module,
        rukqu__dolcz, name='is_np_array')
    return builder.call(aciwt__fylc, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    lsdlo__rfqeo = context.get_argument_type(types.pyobject)
    poyiz__qil = context.get_value_type(types.intp)
    rzxsw__qxw = lir.FunctionType(lir.IntType(8).as_pointer(), [
        lsdlo__rfqeo, poyiz__qil])
    wmsoi__zuejs = cgutils.get_or_insert_function(builder.module,
        rzxsw__qxw, name='array_getptr1')
    rtgna__ilgdc = lir.FunctionType(lsdlo__rfqeo, [lsdlo__rfqeo, lir.
        IntType(8).as_pointer()])
    mlfx__zce = cgutils.get_or_insert_function(builder.module, rtgna__ilgdc,
        name='array_getitem')
    eepre__pggcd = builder.call(wmsoi__zuejs, [arr_obj, ind])
    return builder.call(mlfx__zce, [arr_obj, eepre__pggcd])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    lsdlo__rfqeo = context.get_argument_type(types.pyobject)
    poyiz__qil = context.get_value_type(types.intp)
    rzxsw__qxw = lir.FunctionType(lir.IntType(8).as_pointer(), [
        lsdlo__rfqeo, poyiz__qil])
    wmsoi__zuejs = cgutils.get_or_insert_function(builder.module,
        rzxsw__qxw, name='array_getptr1')
    cic__spvx = lir.FunctionType(lir.VoidType(), [lsdlo__rfqeo, lir.IntType
        (8).as_pointer(), lsdlo__rfqeo])
    riwvf__mlm = cgutils.get_or_insert_function(builder.module, cic__spvx,
        name='array_setitem')
    eepre__pggcd = builder.call(wmsoi__zuejs, [arr_obj, ind])
    builder.call(riwvf__mlm, [arr_obj, eepre__pggcd, val_obj])


def seq_getitem(builder, context, obj, ind):
    lsdlo__rfqeo = context.get_argument_type(types.pyobject)
    poyiz__qil = context.get_value_type(types.intp)
    ntc__rac = lir.FunctionType(lsdlo__rfqeo, [lsdlo__rfqeo, poyiz__qil])
    svg__qfy = cgutils.get_or_insert_function(builder.module, ntc__rac,
        name='seq_getitem')
    return builder.call(svg__qfy, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    lsdlo__rfqeo = context.get_argument_type(types.pyobject)
    zlgxf__tvuu = lir.FunctionType(lir.IntType(32), [lsdlo__rfqeo,
        lsdlo__rfqeo])
    ucbw__lzu = cgutils.get_or_insert_function(builder.module, zlgxf__tvuu,
        name='is_na_value')
    return builder.call(ucbw__lzu, [val, C_NA])


def list_check(builder, context, obj):
    lsdlo__rfqeo = context.get_argument_type(types.pyobject)
    jcsj__hvg = context.get_value_type(types.int32)
    cidbt__vnx = lir.FunctionType(jcsj__hvg, [lsdlo__rfqeo])
    ywrk__ddt = cgutils.get_or_insert_function(builder.module, cidbt__vnx,
        name='list_check')
    return builder.call(ywrk__ddt, [obj])


def dict_keys(builder, context, obj):
    lsdlo__rfqeo = context.get_argument_type(types.pyobject)
    cidbt__vnx = lir.FunctionType(lsdlo__rfqeo, [lsdlo__rfqeo])
    ywrk__ddt = cgutils.get_or_insert_function(builder.module, cidbt__vnx,
        name='dict_keys')
    return builder.call(ywrk__ddt, [obj])


def dict_values(builder, context, obj):
    lsdlo__rfqeo = context.get_argument_type(types.pyobject)
    cidbt__vnx = lir.FunctionType(lsdlo__rfqeo, [lsdlo__rfqeo])
    ywrk__ddt = cgutils.get_or_insert_function(builder.module, cidbt__vnx,
        name='dict_values')
    return builder.call(ywrk__ddt, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    lsdlo__rfqeo = context.get_argument_type(types.pyobject)
    cidbt__vnx = lir.FunctionType(lir.VoidType(), [lsdlo__rfqeo, lsdlo__rfqeo])
    ywrk__ddt = cgutils.get_or_insert_function(builder.module, cidbt__vnx,
        name='dict_merge_from_seq2')
    builder.call(ywrk__ddt, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    itpng__tacms = cgutils.alloca_once_value(builder, val)
    pih__atcp = list_check(builder, context, val)
    kaj__ehru = builder.icmp_unsigned('!=', pih__atcp, lir.Constant(
        pih__atcp.type, 0))
    with builder.if_then(kaj__ehru):
        urbl__kej = context.insert_const_string(builder.module, 'numpy')
        pmu__pryqa = c.pyapi.import_module_noblock(urbl__kej)
        dhpnf__nyrg = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            dhpnf__nyrg = str(typ.dtype)
        wyxah__ecvrs = c.pyapi.object_getattr_string(pmu__pryqa, dhpnf__nyrg)
        itcxj__yrf = builder.load(itpng__tacms)
        pemud__kan = c.pyapi.call_method(pmu__pryqa, 'asarray', (itcxj__yrf,
            wyxah__ecvrs))
        builder.store(pemud__kan, itpng__tacms)
        c.pyapi.decref(pmu__pryqa)
        c.pyapi.decref(wyxah__ecvrs)
    val = builder.load(itpng__tacms)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        hqk__fcl = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        ytcj__nls, grqkt__wgcy = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [hqk__fcl])
        context.nrt.decref(builder, typ, hqk__fcl)
        return cgutils.pack_array(builder, [grqkt__wgcy])
    if isinstance(typ, (StructType, types.BaseTuple)):
        urbl__kej = context.insert_const_string(builder.module, 'pandas')
        tst__qumqx = c.pyapi.import_module_noblock(urbl__kej)
        C_NA = c.pyapi.object_getattr_string(tst__qumqx, 'NA')
        oiro__dkjpu = bodo.utils.transform.get_type_alloc_counts(typ)
        xio__zgafh = context.make_tuple(builder, types.Tuple(oiro__dkjpu *
            [types.int64]), oiro__dkjpu * [context.get_constant(types.int64,
            0)])
        wfdl__nrez = cgutils.alloca_once_value(builder, xio__zgafh)
        smm__ibg = 0
        mht__ztsnv = typ.data if isinstance(typ, StructType) else typ.types
        for cgdo__unx, t in enumerate(mht__ztsnv):
            yfa__bsdv = bodo.utils.transform.get_type_alloc_counts(t)
            if yfa__bsdv == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    cgdo__unx])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, cgdo__unx)
            yddrr__pvmo = is_na_value(builder, context, val_obj, C_NA)
            hbjv__spil = builder.icmp_unsigned('!=', yddrr__pvmo, lir.
                Constant(yddrr__pvmo.type, 1))
            with builder.if_then(hbjv__spil):
                xio__zgafh = builder.load(wfdl__nrez)
                zsgpr__lvo = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for cgdo__unx in range(yfa__bsdv):
                    mzpv__deocn = builder.extract_value(xio__zgafh, 
                        smm__ibg + cgdo__unx)
                    awu__rtl = builder.extract_value(zsgpr__lvo, cgdo__unx)
                    xio__zgafh = builder.insert_value(xio__zgafh, builder.
                        add(mzpv__deocn, awu__rtl), smm__ibg + cgdo__unx)
                builder.store(xio__zgafh, wfdl__nrez)
            smm__ibg += yfa__bsdv
        c.pyapi.decref(tst__qumqx)
        c.pyapi.decref(C_NA)
        return builder.load(wfdl__nrez)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    urbl__kej = context.insert_const_string(builder.module, 'pandas')
    tst__qumqx = c.pyapi.import_module_noblock(urbl__kej)
    C_NA = c.pyapi.object_getattr_string(tst__qumqx, 'NA')
    oiro__dkjpu = bodo.utils.transform.get_type_alloc_counts(typ)
    xio__zgafh = context.make_tuple(builder, types.Tuple(oiro__dkjpu * [
        types.int64]), [n] + (oiro__dkjpu - 1) * [context.get_constant(
        types.int64, 0)])
    wfdl__nrez = cgutils.alloca_once_value(builder, xio__zgafh)
    with cgutils.for_range(builder, n) as pgs__jqnt:
        vcmwp__nqdfm = pgs__jqnt.index
        qumj__rxsj = seq_getitem(builder, context, arr_obj, vcmwp__nqdfm)
        yddrr__pvmo = is_na_value(builder, context, qumj__rxsj, C_NA)
        hbjv__spil = builder.icmp_unsigned('!=', yddrr__pvmo, lir.Constant(
            yddrr__pvmo.type, 1))
        with builder.if_then(hbjv__spil):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                xio__zgafh = builder.load(wfdl__nrez)
                zsgpr__lvo = get_array_elem_counts(c, builder, context,
                    qumj__rxsj, typ.dtype)
                for cgdo__unx in range(oiro__dkjpu - 1):
                    mzpv__deocn = builder.extract_value(xio__zgafh, 
                        cgdo__unx + 1)
                    awu__rtl = builder.extract_value(zsgpr__lvo, cgdo__unx)
                    xio__zgafh = builder.insert_value(xio__zgafh, builder.
                        add(mzpv__deocn, awu__rtl), cgdo__unx + 1)
                builder.store(xio__zgafh, wfdl__nrez)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                smm__ibg = 1
                for cgdo__unx, t in enumerate(typ.data):
                    yfa__bsdv = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if yfa__bsdv == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(qumj__rxsj, cgdo__unx)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(qumj__rxsj,
                            typ.names[cgdo__unx])
                    yddrr__pvmo = is_na_value(builder, context, val_obj, C_NA)
                    hbjv__spil = builder.icmp_unsigned('!=', yddrr__pvmo,
                        lir.Constant(yddrr__pvmo.type, 1))
                    with builder.if_then(hbjv__spil):
                        xio__zgafh = builder.load(wfdl__nrez)
                        zsgpr__lvo = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for cgdo__unx in range(yfa__bsdv):
                            mzpv__deocn = builder.extract_value(xio__zgafh,
                                smm__ibg + cgdo__unx)
                            awu__rtl = builder.extract_value(zsgpr__lvo,
                                cgdo__unx)
                            xio__zgafh = builder.insert_value(xio__zgafh,
                                builder.add(mzpv__deocn, awu__rtl), 
                                smm__ibg + cgdo__unx)
                        builder.store(xio__zgafh, wfdl__nrez)
                    smm__ibg += yfa__bsdv
            else:
                assert isinstance(typ, MapArrayType), typ
                xio__zgafh = builder.load(wfdl__nrez)
                wmmy__hvh = dict_keys(builder, context, qumj__rxsj)
                clk__zrwg = dict_values(builder, context, qumj__rxsj)
                bcte__yty = get_array_elem_counts(c, builder, context,
                    wmmy__hvh, typ.key_arr_type)
                pmsf__mmtjq = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for cgdo__unx in range(1, pmsf__mmtjq + 1):
                    mzpv__deocn = builder.extract_value(xio__zgafh, cgdo__unx)
                    awu__rtl = builder.extract_value(bcte__yty, cgdo__unx - 1)
                    xio__zgafh = builder.insert_value(xio__zgafh, builder.
                        add(mzpv__deocn, awu__rtl), cgdo__unx)
                oye__qfx = get_array_elem_counts(c, builder, context,
                    clk__zrwg, typ.value_arr_type)
                for cgdo__unx in range(pmsf__mmtjq + 1, oiro__dkjpu):
                    mzpv__deocn = builder.extract_value(xio__zgafh, cgdo__unx)
                    awu__rtl = builder.extract_value(oye__qfx, cgdo__unx -
                        pmsf__mmtjq)
                    xio__zgafh = builder.insert_value(xio__zgafh, builder.
                        add(mzpv__deocn, awu__rtl), cgdo__unx)
                builder.store(xio__zgafh, wfdl__nrez)
                c.pyapi.decref(wmmy__hvh)
                c.pyapi.decref(clk__zrwg)
        c.pyapi.decref(qumj__rxsj)
    c.pyapi.decref(tst__qumqx)
    c.pyapi.decref(C_NA)
    return builder.load(wfdl__nrez)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    qtslp__rnoy = n_elems.type.count
    assert qtslp__rnoy >= 1
    plf__sqn = builder.extract_value(n_elems, 0)
    if qtslp__rnoy != 1:
        lgykb__hfnez = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, cgdo__unx) for cgdo__unx in range(1, qtslp__rnoy)])
        isnw__isfae = types.Tuple([types.int64] * (qtslp__rnoy - 1))
    else:
        lgykb__hfnez = context.get_dummy_value()
        isnw__isfae = types.none
    jji__itrc = types.TypeRef(arr_type)
    pthw__zfu = arr_type(types.int64, jji__itrc, isnw__isfae)
    args = [plf__sqn, context.get_dummy_value(), lgykb__hfnez]
    rrmy__mijqk = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        ytcj__nls, sxfjl__wyqqp = c.pyapi.call_jit_code(rrmy__mijqk,
            pthw__zfu, args)
    else:
        sxfjl__wyqqp = context.compile_internal(builder, rrmy__mijqk,
            pthw__zfu, args)
    return sxfjl__wyqqp


def is_ll_eq(builder, val1, val2):
    apfd__ljkrw = val1.type.pointee
    vnkm__cdosg = val2.type.pointee
    assert apfd__ljkrw == vnkm__cdosg, 'invalid llvm value comparison'
    if isinstance(apfd__ljkrw, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(apfd__ljkrw.elements) if isinstance(apfd__ljkrw, lir.
            BaseStructType) else apfd__ljkrw.count
        pagf__ayt = lir.Constant(lir.IntType(1), 1)
        for cgdo__unx in range(n_elems):
            dpjg__mtg = lir.IntType(32)(0)
            yzy__ikjv = lir.IntType(32)(cgdo__unx)
            tjdui__gfu = builder.gep(val1, [dpjg__mtg, yzy__ikjv], inbounds
                =True)
            jznbj__chpha = builder.gep(val2, [dpjg__mtg, yzy__ikjv],
                inbounds=True)
            pagf__ayt = builder.and_(pagf__ayt, is_ll_eq(builder,
                tjdui__gfu, jznbj__chpha))
        return pagf__ayt
    mbf__ksp = builder.load(val1)
    ocoj__oxk = builder.load(val2)
    if mbf__ksp.type in (lir.FloatType(), lir.DoubleType()):
        ilcz__muc = 32 if mbf__ksp.type == lir.FloatType() else 64
        mbf__ksp = builder.bitcast(mbf__ksp, lir.IntType(ilcz__muc))
        ocoj__oxk = builder.bitcast(ocoj__oxk, lir.IntType(ilcz__muc))
    return builder.icmp_unsigned('==', mbf__ksp, ocoj__oxk)
