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
    vpdo__jmm = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    ffbos__cxrkl = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    roqn__zdzrt = builder.gep(null_bitmap_ptr, [vpdo__jmm], inbounds=True)
    kdp__cxf = builder.load(roqn__zdzrt)
    knkdw__fbgm = lir.ArrayType(lir.IntType(8), 8)
    rha__icin = cgutils.alloca_once_value(builder, lir.Constant(knkdw__fbgm,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    kxh__bneh = builder.load(builder.gep(rha__icin, [lir.Constant(lir.
        IntType(64), 0), ffbos__cxrkl], inbounds=True))
    if val:
        builder.store(builder.or_(kdp__cxf, kxh__bneh), roqn__zdzrt)
    else:
        kxh__bneh = builder.xor(kxh__bneh, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(kdp__cxf, kxh__bneh), roqn__zdzrt)


def get_bitmap_bit(builder, null_bitmap_ptr, ind):
    vpdo__jmm = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
    ffbos__cxrkl = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
    kdp__cxf = builder.load(builder.gep(null_bitmap_ptr, [vpdo__jmm],
        inbounds=True))
    knkdw__fbgm = lir.ArrayType(lir.IntType(8), 8)
    rha__icin = cgutils.alloca_once_value(builder, lir.Constant(knkdw__fbgm,
        (1, 2, 4, 8, 16, 32, 64, 128)))
    kxh__bneh = builder.load(builder.gep(rha__icin, [lir.Constant(lir.
        IntType(64), 0), ffbos__cxrkl], inbounds=True))
    return builder.and_(kdp__cxf, kxh__bneh)


def pyarray_check(builder, context, obj):
    zlpo__yzggb = context.get_argument_type(types.pyobject)
    ahrrp__niui = lir.FunctionType(lir.IntType(32), [zlpo__yzggb])
    mcehi__min = cgutils.get_or_insert_function(builder.module, ahrrp__niui,
        name='is_np_array')
    return builder.call(mcehi__min, [obj])


def pyarray_getitem(builder, context, arr_obj, ind):
    zlpo__yzggb = context.get_argument_type(types.pyobject)
    qbg__gyct = context.get_value_type(types.intp)
    ymyiv__cjopm = lir.FunctionType(lir.IntType(8).as_pointer(), [
        zlpo__yzggb, qbg__gyct])
    fqox__fzzr = cgutils.get_or_insert_function(builder.module,
        ymyiv__cjopm, name='array_getptr1')
    vhmaj__jbla = lir.FunctionType(zlpo__yzggb, [zlpo__yzggb, lir.IntType(8
        ).as_pointer()])
    nho__gvau = cgutils.get_or_insert_function(builder.module, vhmaj__jbla,
        name='array_getitem')
    hco__zuw = builder.call(fqox__fzzr, [arr_obj, ind])
    return builder.call(nho__gvau, [arr_obj, hco__zuw])


def pyarray_setitem(builder, context, arr_obj, ind, val_obj):
    zlpo__yzggb = context.get_argument_type(types.pyobject)
    qbg__gyct = context.get_value_type(types.intp)
    ymyiv__cjopm = lir.FunctionType(lir.IntType(8).as_pointer(), [
        zlpo__yzggb, qbg__gyct])
    fqox__fzzr = cgutils.get_or_insert_function(builder.module,
        ymyiv__cjopm, name='array_getptr1')
    jvq__lqzke = lir.FunctionType(lir.VoidType(), [zlpo__yzggb, lir.IntType
        (8).as_pointer(), zlpo__yzggb])
    uhw__rlf = cgutils.get_or_insert_function(builder.module, jvq__lqzke,
        name='array_setitem')
    hco__zuw = builder.call(fqox__fzzr, [arr_obj, ind])
    builder.call(uhw__rlf, [arr_obj, hco__zuw, val_obj])


def seq_getitem(builder, context, obj, ind):
    zlpo__yzggb = context.get_argument_type(types.pyobject)
    qbg__gyct = context.get_value_type(types.intp)
    ukw__flnr = lir.FunctionType(zlpo__yzggb, [zlpo__yzggb, qbg__gyct])
    vtu__dvj = cgutils.get_or_insert_function(builder.module, ukw__flnr,
        name='seq_getitem')
    return builder.call(vtu__dvj, [obj, ind])


def is_na_value(builder, context, val, C_NA):
    zlpo__yzggb = context.get_argument_type(types.pyobject)
    sjo__kklvu = lir.FunctionType(lir.IntType(32), [zlpo__yzggb, zlpo__yzggb])
    gxfz__exd = cgutils.get_or_insert_function(builder.module, sjo__kklvu,
        name='is_na_value')
    return builder.call(gxfz__exd, [val, C_NA])


def list_check(builder, context, obj):
    zlpo__yzggb = context.get_argument_type(types.pyobject)
    kwj__nip = context.get_value_type(types.int32)
    nxd__kvsf = lir.FunctionType(kwj__nip, [zlpo__yzggb])
    boio__xzxsc = cgutils.get_or_insert_function(builder.module, nxd__kvsf,
        name='list_check')
    return builder.call(boio__xzxsc, [obj])


def dict_keys(builder, context, obj):
    zlpo__yzggb = context.get_argument_type(types.pyobject)
    nxd__kvsf = lir.FunctionType(zlpo__yzggb, [zlpo__yzggb])
    boio__xzxsc = cgutils.get_or_insert_function(builder.module, nxd__kvsf,
        name='dict_keys')
    return builder.call(boio__xzxsc, [obj])


def dict_values(builder, context, obj):
    zlpo__yzggb = context.get_argument_type(types.pyobject)
    nxd__kvsf = lir.FunctionType(zlpo__yzggb, [zlpo__yzggb])
    boio__xzxsc = cgutils.get_or_insert_function(builder.module, nxd__kvsf,
        name='dict_values')
    return builder.call(boio__xzxsc, [obj])


def dict_merge_from_seq2(builder, context, dict_obj, seq2_obj):
    zlpo__yzggb = context.get_argument_type(types.pyobject)
    nxd__kvsf = lir.FunctionType(lir.VoidType(), [zlpo__yzggb, zlpo__yzggb])
    boio__xzxsc = cgutils.get_or_insert_function(builder.module, nxd__kvsf,
        name='dict_merge_from_seq2')
    builder.call(boio__xzxsc, [dict_obj, seq2_obj])


def to_arr_obj_if_list_obj(c, context, builder, val, typ):
    if not (isinstance(typ, types.List) or bodo.utils.utils.is_array_typ(
        typ, False)):
        return val
    uymq__etdjs = cgutils.alloca_once_value(builder, val)
    lse__aukxn = list_check(builder, context, val)
    fpcdd__dnknk = builder.icmp_unsigned('!=', lse__aukxn, lir.Constant(
        lse__aukxn.type, 0))
    with builder.if_then(fpcdd__dnknk):
        pmpg__mrz = context.insert_const_string(builder.module, 'numpy')
        sms__vmi = c.pyapi.import_module_noblock(pmpg__mrz)
        ngkk__gwka = 'object_'
        if isinstance(typ, types.Array) or isinstance(typ.dtype, types.Float):
            ngkk__gwka = str(typ.dtype)
        hhyvf__fukua = c.pyapi.object_getattr_string(sms__vmi, ngkk__gwka)
        qtpda__nwxwh = builder.load(uymq__etdjs)
        bpk__leh = c.pyapi.call_method(sms__vmi, 'asarray', (qtpda__nwxwh,
            hhyvf__fukua))
        builder.store(bpk__leh, uymq__etdjs)
        c.pyapi.decref(sms__vmi)
        c.pyapi.decref(hhyvf__fukua)
    val = builder.load(uymq__etdjs)
    return val


def get_array_elem_counts(c, builder, context, arr_obj, typ):
    from bodo.libs.array_item_arr_ext import ArrayItemArrayType
    from bodo.libs.map_arr_ext import MapArrayType
    from bodo.libs.str_arr_ext import get_utf8_size, string_array_type
    from bodo.libs.struct_arr_ext import StructArrayType, StructType
    from bodo.libs.tuple_arr_ext import TupleArrayType
    if typ == bodo.string_type:
        fjm__cin = c.pyapi.to_native_value(bodo.string_type, arr_obj).value
        mei__zabc, ixr__pter = c.pyapi.call_jit_code(lambda a:
            get_utf8_size(a), types.int64(bodo.string_type), [fjm__cin])
        context.nrt.decref(builder, typ, fjm__cin)
        return cgutils.pack_array(builder, [ixr__pter])
    if isinstance(typ, (StructType, types.BaseTuple)):
        pmpg__mrz = context.insert_const_string(builder.module, 'pandas')
        wgcf__nuts = c.pyapi.import_module_noblock(pmpg__mrz)
        C_NA = c.pyapi.object_getattr_string(wgcf__nuts, 'NA')
        wurp__rgm = bodo.utils.transform.get_type_alloc_counts(typ)
        fcnup__kubj = context.make_tuple(builder, types.Tuple(wurp__rgm * [
            types.int64]), wurp__rgm * [context.get_constant(types.int64, 0)])
        ppql__sjemx = cgutils.alloca_once_value(builder, fcnup__kubj)
        tef__mqlws = 0
        btc__cclu = typ.data if isinstance(typ, StructType) else typ.types
        for joywx__cag, t in enumerate(btc__cclu):
            xssv__jkon = bodo.utils.transform.get_type_alloc_counts(t)
            if xssv__jkon == 0:
                continue
            if isinstance(typ, StructType):
                val_obj = c.pyapi.dict_getitem_string(arr_obj, typ.names[
                    joywx__cag])
            else:
                val_obj = c.pyapi.tuple_getitem(arr_obj, joywx__cag)
            elien__lxyxy = is_na_value(builder, context, val_obj, C_NA)
            oyii__cxxcf = builder.icmp_unsigned('!=', elien__lxyxy, lir.
                Constant(elien__lxyxy.type, 1))
            with builder.if_then(oyii__cxxcf):
                fcnup__kubj = builder.load(ppql__sjemx)
                wwlkx__vzyle = get_array_elem_counts(c, builder, context,
                    val_obj, t)
                for joywx__cag in range(xssv__jkon):
                    cckz__cdtof = builder.extract_value(fcnup__kubj, 
                        tef__mqlws + joywx__cag)
                    jihc__uvjoo = builder.extract_value(wwlkx__vzyle,
                        joywx__cag)
                    fcnup__kubj = builder.insert_value(fcnup__kubj, builder
                        .add(cckz__cdtof, jihc__uvjoo), tef__mqlws + joywx__cag
                        )
                builder.store(fcnup__kubj, ppql__sjemx)
            tef__mqlws += xssv__jkon
        c.pyapi.decref(wgcf__nuts)
        c.pyapi.decref(C_NA)
        return builder.load(ppql__sjemx)
    if not bodo.utils.utils.is_array_typ(typ, False):
        return cgutils.pack_array(builder, [], lir.IntType(64))
    n = bodo.utils.utils.object_length(c, arr_obj)
    if not (isinstance(typ, (ArrayItemArrayType, StructArrayType,
        TupleArrayType, MapArrayType)) or typ == string_array_type):
        return cgutils.pack_array(builder, [n])
    pmpg__mrz = context.insert_const_string(builder.module, 'pandas')
    wgcf__nuts = c.pyapi.import_module_noblock(pmpg__mrz)
    C_NA = c.pyapi.object_getattr_string(wgcf__nuts, 'NA')
    wurp__rgm = bodo.utils.transform.get_type_alloc_counts(typ)
    fcnup__kubj = context.make_tuple(builder, types.Tuple(wurp__rgm * [
        types.int64]), [n] + (wurp__rgm - 1) * [context.get_constant(types.
        int64, 0)])
    ppql__sjemx = cgutils.alloca_once_value(builder, fcnup__kubj)
    with cgutils.for_range(builder, n) as thu__blqra:
        otykb__qupf = thu__blqra.index
        gmv__zejx = seq_getitem(builder, context, arr_obj, otykb__qupf)
        elien__lxyxy = is_na_value(builder, context, gmv__zejx, C_NA)
        oyii__cxxcf = builder.icmp_unsigned('!=', elien__lxyxy, lir.
            Constant(elien__lxyxy.type, 1))
        with builder.if_then(oyii__cxxcf):
            if isinstance(typ, ArrayItemArrayType) or typ == string_array_type:
                fcnup__kubj = builder.load(ppql__sjemx)
                wwlkx__vzyle = get_array_elem_counts(c, builder, context,
                    gmv__zejx, typ.dtype)
                for joywx__cag in range(wurp__rgm - 1):
                    cckz__cdtof = builder.extract_value(fcnup__kubj, 
                        joywx__cag + 1)
                    jihc__uvjoo = builder.extract_value(wwlkx__vzyle,
                        joywx__cag)
                    fcnup__kubj = builder.insert_value(fcnup__kubj, builder
                        .add(cckz__cdtof, jihc__uvjoo), joywx__cag + 1)
                builder.store(fcnup__kubj, ppql__sjemx)
            elif isinstance(typ, (StructArrayType, TupleArrayType)):
                tef__mqlws = 1
                for joywx__cag, t in enumerate(typ.data):
                    xssv__jkon = bodo.utils.transform.get_type_alloc_counts(t
                        .dtype)
                    if xssv__jkon == 0:
                        continue
                    if isinstance(typ, TupleArrayType):
                        val_obj = c.pyapi.tuple_getitem(gmv__zejx, joywx__cag)
                    else:
                        val_obj = c.pyapi.dict_getitem_string(gmv__zejx,
                            typ.names[joywx__cag])
                    elien__lxyxy = is_na_value(builder, context, val_obj, C_NA)
                    oyii__cxxcf = builder.icmp_unsigned('!=', elien__lxyxy,
                        lir.Constant(elien__lxyxy.type, 1))
                    with builder.if_then(oyii__cxxcf):
                        fcnup__kubj = builder.load(ppql__sjemx)
                        wwlkx__vzyle = get_array_elem_counts(c, builder,
                            context, val_obj, t.dtype)
                        for joywx__cag in range(xssv__jkon):
                            cckz__cdtof = builder.extract_value(fcnup__kubj,
                                tef__mqlws + joywx__cag)
                            jihc__uvjoo = builder.extract_value(wwlkx__vzyle,
                                joywx__cag)
                            fcnup__kubj = builder.insert_value(fcnup__kubj,
                                builder.add(cckz__cdtof, jihc__uvjoo), 
                                tef__mqlws + joywx__cag)
                        builder.store(fcnup__kubj, ppql__sjemx)
                    tef__mqlws += xssv__jkon
            else:
                assert isinstance(typ, MapArrayType), typ
                fcnup__kubj = builder.load(ppql__sjemx)
                qftt__rxknk = dict_keys(builder, context, gmv__zejx)
                bhlob__pveqz = dict_values(builder, context, gmv__zejx)
                qvbtq__taob = get_array_elem_counts(c, builder, context,
                    qftt__rxknk, typ.key_arr_type)
                gjldr__zsqfj = bodo.utils.transform.get_type_alloc_counts(typ
                    .key_arr_type)
                for joywx__cag in range(1, gjldr__zsqfj + 1):
                    cckz__cdtof = builder.extract_value(fcnup__kubj, joywx__cag
                        )
                    jihc__uvjoo = builder.extract_value(qvbtq__taob, 
                        joywx__cag - 1)
                    fcnup__kubj = builder.insert_value(fcnup__kubj, builder
                        .add(cckz__cdtof, jihc__uvjoo), joywx__cag)
                otxrf__fbxc = get_array_elem_counts(c, builder, context,
                    bhlob__pveqz, typ.value_arr_type)
                for joywx__cag in range(gjldr__zsqfj + 1, wurp__rgm):
                    cckz__cdtof = builder.extract_value(fcnup__kubj, joywx__cag
                        )
                    jihc__uvjoo = builder.extract_value(otxrf__fbxc, 
                        joywx__cag - gjldr__zsqfj)
                    fcnup__kubj = builder.insert_value(fcnup__kubj, builder
                        .add(cckz__cdtof, jihc__uvjoo), joywx__cag)
                builder.store(fcnup__kubj, ppql__sjemx)
                c.pyapi.decref(qftt__rxknk)
                c.pyapi.decref(bhlob__pveqz)
        c.pyapi.decref(gmv__zejx)
    c.pyapi.decref(wgcf__nuts)
    c.pyapi.decref(C_NA)
    return builder.load(ppql__sjemx)


def gen_allocate_array(context, builder, arr_type, n_elems, c=None):
    rip__ircwd = n_elems.type.count
    assert rip__ircwd >= 1
    slqex__kgq = builder.extract_value(n_elems, 0)
    if rip__ircwd != 1:
        jix__ifht = cgutils.pack_array(builder, [builder.extract_value(
            n_elems, joywx__cag) for joywx__cag in range(1, rip__ircwd)])
        xtfk__ikqkb = types.Tuple([types.int64] * (rip__ircwd - 1))
    else:
        jix__ifht = context.get_dummy_value()
        xtfk__ikqkb = types.none
    jttis__kcdpd = types.TypeRef(arr_type)
    hbn__pid = arr_type(types.int64, jttis__kcdpd, xtfk__ikqkb)
    args = [slqex__kgq, context.get_dummy_value(), jix__ifht]
    tikc__obfx = lambda n, t, s: bodo.utils.utils.alloc_type(n, t, s)
    if c:
        mei__zabc, hrxn__ulztq = c.pyapi.call_jit_code(tikc__obfx, hbn__pid,
            args)
    else:
        hrxn__ulztq = context.compile_internal(builder, tikc__obfx,
            hbn__pid, args)
    return hrxn__ulztq


def is_ll_eq(builder, val1, val2):
    brmo__kgaa = val1.type.pointee
    hfwn__sxws = val2.type.pointee
    assert brmo__kgaa == hfwn__sxws, 'invalid llvm value comparison'
    if isinstance(brmo__kgaa, (lir.BaseStructType, lir.ArrayType)):
        n_elems = len(brmo__kgaa.elements) if isinstance(brmo__kgaa, lir.
            BaseStructType) else brmo__kgaa.count
        dos__avxi = lir.Constant(lir.IntType(1), 1)
        for joywx__cag in range(n_elems):
            mvjqt__axgl = lir.IntType(32)(0)
            xzz__viw = lir.IntType(32)(joywx__cag)
            isbn__gffy = builder.gep(val1, [mvjqt__axgl, xzz__viw],
                inbounds=True)
            izos__lbpfu = builder.gep(val2, [mvjqt__axgl, xzz__viw],
                inbounds=True)
            dos__avxi = builder.and_(dos__avxi, is_ll_eq(builder,
                isbn__gffy, izos__lbpfu))
        return dos__avxi
    hsg__azmz = builder.load(val1)
    euy__vzp = builder.load(val2)
    if hsg__azmz.type in (lir.FloatType(), lir.DoubleType()):
        dyr__qve = 32 if hsg__azmz.type == lir.FloatType() else 64
        hsg__azmz = builder.bitcast(hsg__azmz, lir.IntType(dyr__qve))
        euy__vzp = builder.bitcast(euy__vzp, lir.IntType(dyr__qve))
    return builder.icmp_unsigned('==', hsg__azmz, euy__vzp)
