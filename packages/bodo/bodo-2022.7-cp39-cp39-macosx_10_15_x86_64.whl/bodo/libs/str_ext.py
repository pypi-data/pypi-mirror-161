import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import AbstractTemplate, AttributeTemplate, bound_function, infer_getattr, infer_global, signature
from numba.extending import intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, register_jitable, register_model
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.utils.typing import BodoError, get_overload_const_int, get_overload_const_str, is_overload_constant_int, is_overload_constant_str


def unliteral_all(args):
    return tuple(types.unliteral(a) for a in args)


ll.add_symbol('del_str', hstr_ext.del_str)
ll.add_symbol('unicode_to_utf8', hstr_ext.unicode_to_utf8)
ll.add_symbol('memcmp', hstr_ext.memcmp)
ll.add_symbol('int_to_hex', hstr_ext.int_to_hex)
string_type = types.unicode_type


@numba.njit
def contains_regex(e, in_str):
    with numba.objmode(res='bool_'):
        res = bool(e.search(in_str))
    return res


@numba.generated_jit
def str_findall_count(regex, in_str):

    def _str_findall_count_impl(regex, in_str):
        with numba.objmode(res='int64'):
            res = len(regex.findall(in_str))
        return res
    return _str_findall_count_impl


utf8_str_type = types.ArrayCTypes(types.Array(types.uint8, 1, 'C'))


@intrinsic
def unicode_to_utf8_and_len(typingctx, str_typ):
    assert str_typ in (string_type, types.Optional(string_type)) or isinstance(
        str_typ, types.StringLiteral)
    fqeva__ffioh = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        kpu__xzb, = args
        flci__owm = cgutils.create_struct_proxy(string_type)(context,
            builder, value=kpu__xzb)
        idc__bhh = cgutils.create_struct_proxy(utf8_str_type)(context, builder)
        lwqf__afwlr = cgutils.create_struct_proxy(fqeva__ffioh)(context,
            builder)
        is_ascii = builder.icmp_unsigned('==', flci__owm.is_ascii, lir.
            Constant(flci__owm.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (pjdk__mue, jjv__hjha):
            with pjdk__mue:
                context.nrt.incref(builder, string_type, kpu__xzb)
                idc__bhh.data = flci__owm.data
                idc__bhh.meminfo = flci__owm.meminfo
                lwqf__afwlr.f1 = flci__owm.length
            with jjv__hjha:
                gex__bdvi = lir.FunctionType(lir.IntType(64), [lir.IntType(
                    8).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                jqq__jytew = cgutils.get_or_insert_function(builder.module,
                    gex__bdvi, name='unicode_to_utf8')
                wow__wqq = context.get_constant_null(types.voidptr)
                lgyau__wni = builder.call(jqq__jytew, [wow__wqq, flci__owm.
                    data, flci__owm.length, flci__owm.kind])
                lwqf__afwlr.f1 = lgyau__wni
                nvvfi__rntu = builder.add(lgyau__wni, lir.Constant(lir.
                    IntType(64), 1))
                idc__bhh.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=nvvfi__rntu, align=32)
                idc__bhh.data = context.nrt.meminfo_data(builder, idc__bhh.
                    meminfo)
                builder.call(jqq__jytew, [idc__bhh.data, flci__owm.data,
                    flci__owm.length, flci__owm.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    idc__bhh.data, [lgyau__wni]))
        lwqf__afwlr.f0 = idc__bhh._getvalue()
        return lwqf__afwlr._getvalue()
    return fqeva__ffioh(string_type), codegen


def unicode_to_utf8(s):
    return s


@overload(unicode_to_utf8)
def overload_unicode_to_utf8(s):
    return lambda s: unicode_to_utf8_and_len(s)[0]


@overload(max)
def overload_builtin_max(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs > rhs else rhs
        return impl


@overload(min)
def overload_builtin_min(lhs, rhs):
    if lhs == types.unicode_type and rhs == types.unicode_type:

        def impl(lhs, rhs):
            return lhs if lhs < rhs else rhs
        return impl


@intrinsic
def memcmp(typingctx, dest_t, src_t, count_t=None):

    def codegen(context, builder, sig, args):
        gex__bdvi = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        tbx__vdb = cgutils.get_or_insert_function(builder.module, gex__bdvi,
            name='memcmp')
        return builder.call(tbx__vdb, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    wuo__hhfeu = n(10)

    def impl(n):
        if n == 0:
            return 1
        jecbl__irjjc = 0
        if n < 0:
            n = -n
            jecbl__irjjc += 1
        while n > 0:
            n = n // wuo__hhfeu
            jecbl__irjjc += 1
        return jecbl__irjjc
    return impl


class StdStringType(types.Opaque):

    def __init__(self):
        super(StdStringType, self).__init__(name='StdStringType')


std_str_type = StdStringType()
register_model(StdStringType)(models.OpaqueModel)
del_str = types.ExternalFunction('del_str', types.void(std_str_type))
get_c_str = types.ExternalFunction('get_c_str', types.voidptr(std_str_type))
dummy_use = numba.njit(lambda a: None)


@overload(int)
def int_str_overload(in_str, base=10):
    if in_str == string_type:
        if is_overload_constant_int(base) and get_overload_const_int(base
            ) == 10:

            def _str_to_int_impl(in_str, base=10):
                val = _str_to_int64(in_str._data, in_str._length)
                dummy_use(in_str)
                return val
            return _str_to_int_impl

        def _str_to_int_base_impl(in_str, base=10):
            val = _str_to_int64_base(in_str._data, in_str._length, base)
            dummy_use(in_str)
            return val
        return _str_to_int_base_impl


@infer_global(float)
class StrToFloat(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        [vtr__ubzk] = args
        if isinstance(vtr__ubzk, StdStringType):
            return signature(types.float64, vtr__ubzk)
        if vtr__ubzk == string_type:
            return signature(types.float64, vtr__ubzk)


ll.add_symbol('init_string_const', hstr_ext.init_string_const)
ll.add_symbol('get_c_str', hstr_ext.get_c_str)
ll.add_symbol('str_to_int64', hstr_ext.str_to_int64)
ll.add_symbol('str_to_uint64', hstr_ext.str_to_uint64)
ll.add_symbol('str_to_int64_base', hstr_ext.str_to_int64_base)
ll.add_symbol('str_to_float64', hstr_ext.str_to_float64)
ll.add_symbol('str_to_float32', hstr_ext.str_to_float32)
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('str_from_float32', hstr_ext.str_from_float32)
ll.add_symbol('str_from_float64', hstr_ext.str_from_float64)
get_std_str_len = types.ExternalFunction('get_str_len', signature(types.
    intp, std_str_type))
init_string_from_chars = types.ExternalFunction('init_string_const',
    std_str_type(types.voidptr, types.intp))
_str_to_int64 = types.ExternalFunction('str_to_int64', signature(types.
    int64, types.voidptr, types.int64))
_str_to_uint64 = types.ExternalFunction('str_to_uint64', signature(types.
    uint64, types.voidptr, types.int64))
_str_to_int64_base = types.ExternalFunction('str_to_int64_base', signature(
    types.int64, types.voidptr, types.int64, types.int64))


def gen_unicode_to_std_str(context, builder, unicode_val):
    flci__owm = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    gex__bdvi = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(
        8).as_pointer(), lir.IntType(64)])
    inftd__xiaht = cgutils.get_or_insert_function(builder.module, gex__bdvi,
        name='init_string_const')
    return builder.call(inftd__xiaht, [flci__owm.data, flci__owm.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        eicuk__gqq = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(eicuk__gqq._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return eicuk__gqq
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    flci__owm = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return flci__owm.data


@intrinsic
def unicode_to_std_str(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_unicode_to_std_str(context, builder, args[0])
    return std_str_type(string_type), codegen


@intrinsic
def std_str_to_unicode(typingctx, unicode_t=None):

    def codegen(context, builder, sig, args):
        return gen_std_str_to_unicode(context, builder, args[0], True)
    return string_type(std_str_type), codegen


class RandomAccessStringArrayType(types.ArrayCompatible):

    def __init__(self):
        super(RandomAccessStringArrayType, self).__init__(name=
            'RandomAccessStringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    def copy(self):
        RandomAccessStringArrayType()


random_access_string_array = RandomAccessStringArrayType()


@register_model(RandomAccessStringArrayType)
class RandomAccessStringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hmqwd__zckjz = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, hmqwd__zckjz)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        pocb__xogzv, = args
        rldh__gfka = types.List(string_type)
        rqqoa__epeq = numba.cpython.listobj.ListInstance.allocate(context,
            builder, rldh__gfka, pocb__xogzv)
        rqqoa__epeq.size = pocb__xogzv
        qowy__iitxc = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        qowy__iitxc.data = rqqoa__epeq.value
        return qowy__iitxc._getvalue()
    return random_access_string_array(types.intp), codegen


@overload(operator.getitem, no_unliteral=True)
def random_access_str_arr_getitem(A, ind):
    if A != random_access_string_array:
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]


@overload(operator.setitem)
def random_access_str_arr_setitem(A, idx, val):
    if A != random_access_string_array:
        return
    if isinstance(idx, types.Integer):
        assert val == string_type

        def impl_scalar(A, idx, val):
            A._data[idx] = val
        return impl_scalar


@overload(len, no_unliteral=True)
def overload_str_arr_len(A):
    if A == random_access_string_array:
        return lambda A: len(A._data)


@overload_attribute(RandomAccessStringArrayType, 'shape')
def overload_str_arr_shape(A):
    return lambda A: (len(A._data),)


def alloc_random_access_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_str_ext_alloc_random_access_string_array
    ) = alloc_random_access_str_arr_equiv
str_from_float32 = types.ExternalFunction('str_from_float32', types.void(
    types.voidptr, types.float32))
str_from_float64 = types.ExternalFunction('str_from_float64', types.void(
    types.voidptr, types.float64))


def float_to_str(s, v):
    pass


@overload(float_to_str)
def float_to_str_overload(s, v):
    assert isinstance(v, types.Float)
    if v == types.float32:
        return lambda s, v: str_from_float32(s._data, v)
    return lambda s, v: str_from_float64(s._data, v)


@overload(str)
def float_str_overload(v):
    if isinstance(v, types.Float):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(v):
            if v == 0:
                return '0.0'
            ngg__xfob = 0
            shmss__radc = v
            if shmss__radc < 0:
                ngg__xfob = 1
                shmss__radc = -shmss__radc
            if shmss__radc < 1:
                unv__foah = 1
            else:
                unv__foah = 1 + int(np.floor(np.log10(shmss__radc)))
            length = ngg__xfob + unv__foah + 1 + 6
            s = numba.cpython.unicode._malloc_string(kind, 1, length, True)
            float_to_str(s, v)
            return s
        return impl


@overload(format, no_unliteral=True)
def overload_format(value, format_spec=''):
    if is_overload_constant_str(format_spec) and get_overload_const_str(
        format_spec) == '':

        def impl_fast(value, format_spec=''):
            return str(value)
        return impl_fast

    def impl(value, format_spec=''):
        with numba.objmode(res='string'):
            res = format(value, format_spec)
        return res
    return impl


@lower_cast(StdStringType, types.float64)
def cast_str_to_float64(context, builder, fromty, toty, val):
    gex__bdvi = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    inftd__xiaht = cgutils.get_or_insert_function(builder.module, gex__bdvi,
        name='str_to_float64')
    res = builder.call(inftd__xiaht, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    gex__bdvi = lir.FunctionType(lir.FloatType(), [lir.IntType(8).as_pointer()]
        )
    inftd__xiaht = cgutils.get_or_insert_function(builder.module, gex__bdvi,
        name='str_to_float32')
    res = builder.call(inftd__xiaht, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.float64)
def cast_unicode_str_to_float64(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float64(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.float32)
def cast_unicode_str_to_float32(context, builder, fromty, toty, val):
    std_str = gen_unicode_to_std_str(context, builder, val)
    return cast_str_to_float32(context, builder, std_str_type, toty, std_str)


@lower_cast(string_type, types.int64)
@lower_cast(string_type, types.int32)
@lower_cast(string_type, types.int16)
@lower_cast(string_type, types.int8)
def cast_unicode_str_to_int64(context, builder, fromty, toty, val):
    flci__owm = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    gex__bdvi = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(8
        ).as_pointer(), lir.IntType(64)])
    inftd__xiaht = cgutils.get_or_insert_function(builder.module, gex__bdvi,
        name='str_to_int64')
    res = builder.call(inftd__xiaht, (flci__owm.data, flci__owm.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    flci__owm = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    gex__bdvi = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(8
        ).as_pointer(), lir.IntType(64)])
    inftd__xiaht = cgutils.get_or_insert_function(builder.module, gex__bdvi,
        name='str_to_uint64')
    res = builder.call(inftd__xiaht, (flci__owm.data, flci__owm.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        yohhs__kozi = ', '.join('e{}'.format(ava__axb) for ava__axb in
            range(len(args)))
        if yohhs__kozi:
            yohhs__kozi += ', '
        xkss__lthsn = ', '.join("{} = ''".format(a) for a in kws.keys())
        jxq__fsni = f'def format_stub(string, {yohhs__kozi} {xkss__lthsn}):\n'
        jxq__fsni += '    pass\n'
        sgrww__tdhta = {}
        exec(jxq__fsni, {}, sgrww__tdhta)
        yhm__hxlj = sgrww__tdhta['format_stub']
        soma__bokih = numba.core.utils.pysignature(yhm__hxlj)
        zwcns__odq = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, zwcns__odq).replace(pysig=soma__bokih)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    zxnp__tbnfb = pat is not None and len(pat) > 1
    if zxnp__tbnfb:
        mkyeh__cix = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    rqqoa__epeq = len(arr)
    bdgxa__eryo = 0
    avk__zwwhs = 0
    for ava__axb in numba.parfors.parfor.internal_prange(rqqoa__epeq):
        if bodo.libs.array_kernels.isna(arr, ava__axb):
            continue
        if zxnp__tbnfb:
            ykvr__hum = mkyeh__cix.split(arr[ava__axb], maxsplit=n)
        elif pat == '':
            ykvr__hum = [''] + list(arr[ava__axb]) + ['']
        else:
            ykvr__hum = arr[ava__axb].split(pat, n)
        bdgxa__eryo += len(ykvr__hum)
        for s in ykvr__hum:
            avk__zwwhs += bodo.libs.str_arr_ext.get_utf8_size(s)
    jrnv__sxo = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        rqqoa__epeq, (bdgxa__eryo, avk__zwwhs), bodo.libs.str_arr_ext.
        string_array_type)
    lqan__xfs = bodo.libs.array_item_arr_ext.get_offsets(jrnv__sxo)
    cxbu__snbj = bodo.libs.array_item_arr_ext.get_null_bitmap(jrnv__sxo)
    ncm__rtps = bodo.libs.array_item_arr_ext.get_data(jrnv__sxo)
    ewhue__ryd = 0
    for hxoh__ptvkh in numba.parfors.parfor.internal_prange(rqqoa__epeq):
        lqan__xfs[hxoh__ptvkh] = ewhue__ryd
        if bodo.libs.array_kernels.isna(arr, hxoh__ptvkh):
            bodo.libs.int_arr_ext.set_bit_to_arr(cxbu__snbj, hxoh__ptvkh, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(cxbu__snbj, hxoh__ptvkh, 1)
        if zxnp__tbnfb:
            ykvr__hum = mkyeh__cix.split(arr[hxoh__ptvkh], maxsplit=n)
        elif pat == '':
            ykvr__hum = [''] + list(arr[hxoh__ptvkh]) + ['']
        else:
            ykvr__hum = arr[hxoh__ptvkh].split(pat, n)
        upvkx__qbagl = len(ykvr__hum)
        for qpf__ltfc in range(upvkx__qbagl):
            s = ykvr__hum[qpf__ltfc]
            ncm__rtps[ewhue__ryd] = s
            ewhue__ryd += 1
    lqan__xfs[rqqoa__epeq] = ewhue__ryd
    return jrnv__sxo


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                oqh__olktt = '-0x'
                x = x * -1
            else:
                oqh__olktt = '0x'
            x = np.uint64(x)
            if x == 0:
                iuzn__nfy = 1
            else:
                iuzn__nfy = fast_ceil_log2(x + 1)
                iuzn__nfy = (iuzn__nfy + 3) // 4
            length = len(oqh__olktt) + iuzn__nfy
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, oqh__olktt._data,
                len(oqh__olktt), 1)
            int_to_hex(output, iuzn__nfy, len(oqh__olktt), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    lbuy__gooeq = 0 if x & x - 1 == 0 else 1
    hqy__unx = [np.uint64(18446744069414584320), np.uint64(4294901760), np.
        uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    cvr__ocs = 32
    for ava__axb in range(len(hqy__unx)):
        dkk__zxx = 0 if x & hqy__unx[ava__axb] == 0 else cvr__ocs
        lbuy__gooeq = lbuy__gooeq + dkk__zxx
        x = x >> dkk__zxx
        cvr__ocs = cvr__ocs >> 1
    return lbuy__gooeq


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        mke__ehr = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        gex__bdvi = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        rbcg__riaom = cgutils.get_or_insert_function(builder.module,
            gex__bdvi, name='int_to_hex')
        mplfc__zxd = builder.inttoptr(builder.add(builder.ptrtoint(mke__ehr
            .data, lir.IntType(64)), header_len), lir.IntType(8).as_pointer())
        builder.call(rbcg__riaom, (mplfc__zxd, out_len, int_val))
    return types.void(output, out_len, header_len, int_val), codegen


def alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    pass


@overload(alloc_empty_bytes_or_string_data)
def overload_alloc_empty_bytes_or_string_data(typ, kind, length, is_ascii=0):
    typ = typ.instance_type if isinstance(typ, types.TypeRef) else typ
    if typ == bodo.bytes_type:
        return lambda typ, kind, length, is_ascii=0: np.empty(length, np.uint8)
    if typ == string_type:
        return (lambda typ, kind, length, is_ascii=0: numba.cpython.unicode
            ._empty_string(kind, length, is_ascii))
    raise BodoError(
        f'Internal Error: Expected Bytes or String type, found {typ}')


def get_unicode_or_numpy_data(val):
    pass


@overload(get_unicode_or_numpy_data)
def overload_get_unicode_or_numpy_data(val):
    if val == string_type:
        return lambda val: val._data
    if isinstance(val, types.Array):
        return lambda val: val.ctypes
    raise BodoError(
        f'Internal Error: Expected String or Numpy Array, found {val}')
