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
    jpmg__syq = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        gpqrw__rwwrp, = args
        ihi__zfb = cgutils.create_struct_proxy(string_type)(context,
            builder, value=gpqrw__rwwrp)
        gbt__gdy = cgutils.create_struct_proxy(utf8_str_type)(context, builder)
        gnyt__vpw = cgutils.create_struct_proxy(jpmg__syq)(context, builder)
        is_ascii = builder.icmp_unsigned('==', ihi__zfb.is_ascii, lir.
            Constant(ihi__zfb.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (mhedm__lsx, bdu__vbfsx):
            with mhedm__lsx:
                context.nrt.incref(builder, string_type, gpqrw__rwwrp)
                gbt__gdy.data = ihi__zfb.data
                gbt__gdy.meminfo = ihi__zfb.meminfo
                gnyt__vpw.f1 = ihi__zfb.length
            with bdu__vbfsx:
                zeov__tljme = lir.FunctionType(lir.IntType(64), [lir.
                    IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                    lir.IntType(64), lir.IntType(32)])
                njp__wdd = cgutils.get_or_insert_function(builder.module,
                    zeov__tljme, name='unicode_to_utf8')
                usy__mzpj = context.get_constant_null(types.voidptr)
                gddt__pyuqg = builder.call(njp__wdd, [usy__mzpj, ihi__zfb.
                    data, ihi__zfb.length, ihi__zfb.kind])
                gnyt__vpw.f1 = gddt__pyuqg
                ofo__oygfr = builder.add(gddt__pyuqg, lir.Constant(lir.
                    IntType(64), 1))
                gbt__gdy.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=ofo__oygfr, align=32)
                gbt__gdy.data = context.nrt.meminfo_data(builder, gbt__gdy.
                    meminfo)
                builder.call(njp__wdd, [gbt__gdy.data, ihi__zfb.data,
                    ihi__zfb.length, ihi__zfb.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    gbt__gdy.data, [gddt__pyuqg]))
        gnyt__vpw.f0 = gbt__gdy._getvalue()
        return gnyt__vpw._getvalue()
    return jpmg__syq(string_type), codegen


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
        zeov__tljme = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        ggnh__mut = cgutils.get_or_insert_function(builder.module,
            zeov__tljme, name='memcmp')
        return builder.call(ggnh__mut, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    tjl__lmy = n(10)

    def impl(n):
        if n == 0:
            return 1
        glr__wfpmz = 0
        if n < 0:
            n = -n
            glr__wfpmz += 1
        while n > 0:
            n = n // tjl__lmy
            glr__wfpmz += 1
        return glr__wfpmz
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
        [qneiy__jdzih] = args
        if isinstance(qneiy__jdzih, StdStringType):
            return signature(types.float64, qneiy__jdzih)
        if qneiy__jdzih == string_type:
            return signature(types.float64, qneiy__jdzih)


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
    ihi__zfb = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    zeov__tljme = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    tqza__wgubx = cgutils.get_or_insert_function(builder.module,
        zeov__tljme, name='init_string_const')
    return builder.call(tqza__wgubx, [ihi__zfb.data, ihi__zfb.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        pmpk__qrv = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(pmpk__qrv._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return pmpk__qrv
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    ihi__zfb = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return ihi__zfb.data


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
        ezact__twy = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, ezact__twy)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        myuu__dpxj, = args
        qwet__sgq = types.List(string_type)
        ntxx__wnvbt = numba.cpython.listobj.ListInstance.allocate(context,
            builder, qwet__sgq, myuu__dpxj)
        ntxx__wnvbt.size = myuu__dpxj
        ajm__lbxg = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        ajm__lbxg.data = ntxx__wnvbt.value
        return ajm__lbxg._getvalue()
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
            kyeth__opakl = 0
            aucfx__bxt = v
            if aucfx__bxt < 0:
                kyeth__opakl = 1
                aucfx__bxt = -aucfx__bxt
            if aucfx__bxt < 1:
                pfe__nlsjr = 1
            else:
                pfe__nlsjr = 1 + int(np.floor(np.log10(aucfx__bxt)))
            length = kyeth__opakl + pfe__nlsjr + 1 + 6
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
    zeov__tljme = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    tqza__wgubx = cgutils.get_or_insert_function(builder.module,
        zeov__tljme, name='str_to_float64')
    res = builder.call(tqza__wgubx, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    zeov__tljme = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    tqza__wgubx = cgutils.get_or_insert_function(builder.module,
        zeov__tljme, name='str_to_float32')
    res = builder.call(tqza__wgubx, (val,))
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
    ihi__zfb = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    zeov__tljme = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    tqza__wgubx = cgutils.get_or_insert_function(builder.module,
        zeov__tljme, name='str_to_int64')
    res = builder.call(tqza__wgubx, (ihi__zfb.data, ihi__zfb.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    ihi__zfb = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    zeov__tljme = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    tqza__wgubx = cgutils.get_or_insert_function(builder.module,
        zeov__tljme, name='str_to_uint64')
    res = builder.call(tqza__wgubx, (ihi__zfb.data, ihi__zfb.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        jgxjz__neugn = ', '.join('e{}'.format(dtpk__eygjg) for dtpk__eygjg in
            range(len(args)))
        if jgxjz__neugn:
            jgxjz__neugn += ', '
        qfl__krh = ', '.join("{} = ''".format(a) for a in kws.keys())
        adou__biyub = f'def format_stub(string, {jgxjz__neugn} {qfl__krh}):\n'
        adou__biyub += '    pass\n'
        tjvhz__hqm = {}
        exec(adou__biyub, {}, tjvhz__hqm)
        yce__hidy = tjvhz__hqm['format_stub']
        fpxhl__wzdf = numba.core.utils.pysignature(yce__hidy)
        ple__nka = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, ple__nka).replace(pysig=fpxhl__wzdf)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    eustj__rksd = pat is not None and len(pat) > 1
    if eustj__rksd:
        enxde__gudme = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    ntxx__wnvbt = len(arr)
    fnn__uvg = 0
    qwdam__iab = 0
    for dtpk__eygjg in numba.parfors.parfor.internal_prange(ntxx__wnvbt):
        if bodo.libs.array_kernels.isna(arr, dtpk__eygjg):
            continue
        if eustj__rksd:
            qvflp__qzus = enxde__gudme.split(arr[dtpk__eygjg], maxsplit=n)
        elif pat == '':
            qvflp__qzus = [''] + list(arr[dtpk__eygjg]) + ['']
        else:
            qvflp__qzus = arr[dtpk__eygjg].split(pat, n)
        fnn__uvg += len(qvflp__qzus)
        for s in qvflp__qzus:
            qwdam__iab += bodo.libs.str_arr_ext.get_utf8_size(s)
    cdc__yfek = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        ntxx__wnvbt, (fnn__uvg, qwdam__iab), bodo.libs.str_arr_ext.
        string_array_type)
    tpd__lkdr = bodo.libs.array_item_arr_ext.get_offsets(cdc__yfek)
    wgreb__afiqc = bodo.libs.array_item_arr_ext.get_null_bitmap(cdc__yfek)
    xzjq__crpfh = bodo.libs.array_item_arr_ext.get_data(cdc__yfek)
    mglux__wcxqn = 0
    for wrgo__pwjz in numba.parfors.parfor.internal_prange(ntxx__wnvbt):
        tpd__lkdr[wrgo__pwjz] = mglux__wcxqn
        if bodo.libs.array_kernels.isna(arr, wrgo__pwjz):
            bodo.libs.int_arr_ext.set_bit_to_arr(wgreb__afiqc, wrgo__pwjz, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(wgreb__afiqc, wrgo__pwjz, 1)
        if eustj__rksd:
            qvflp__qzus = enxde__gudme.split(arr[wrgo__pwjz], maxsplit=n)
        elif pat == '':
            qvflp__qzus = [''] + list(arr[wrgo__pwjz]) + ['']
        else:
            qvflp__qzus = arr[wrgo__pwjz].split(pat, n)
        lhota__zog = len(qvflp__qzus)
        for sywyy__gly in range(lhota__zog):
            s = qvflp__qzus[sywyy__gly]
            xzjq__crpfh[mglux__wcxqn] = s
            mglux__wcxqn += 1
    tpd__lkdr[ntxx__wnvbt] = mglux__wcxqn
    return cdc__yfek


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                sdgzz__www = '-0x'
                x = x * -1
            else:
                sdgzz__www = '0x'
            x = np.uint64(x)
            if x == 0:
                itb__ctikh = 1
            else:
                itb__ctikh = fast_ceil_log2(x + 1)
                itb__ctikh = (itb__ctikh + 3) // 4
            length = len(sdgzz__www) + itb__ctikh
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, sdgzz__www._data,
                len(sdgzz__www), 1)
            int_to_hex(output, itb__ctikh, len(sdgzz__www), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    xro__isat = 0 if x & x - 1 == 0 else 1
    mch__pcb = [np.uint64(18446744069414584320), np.uint64(4294901760), np.
        uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    ghpzu__hhvzo = 32
    for dtpk__eygjg in range(len(mch__pcb)):
        hegl__gtsx = 0 if x & mch__pcb[dtpk__eygjg] == 0 else ghpzu__hhvzo
        xro__isat = xro__isat + hegl__gtsx
        x = x >> hegl__gtsx
        ghpzu__hhvzo = ghpzu__hhvzo >> 1
    return xro__isat


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        wkdr__yjft = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        zeov__tljme = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        osap__mco = cgutils.get_or_insert_function(builder.module,
            zeov__tljme, name='int_to_hex')
        xsw__ten = builder.inttoptr(builder.add(builder.ptrtoint(wkdr__yjft
            .data, lir.IntType(64)), header_len), lir.IntType(8).as_pointer())
        builder.call(osap__mco, (xsw__ten, out_len, int_val))
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
