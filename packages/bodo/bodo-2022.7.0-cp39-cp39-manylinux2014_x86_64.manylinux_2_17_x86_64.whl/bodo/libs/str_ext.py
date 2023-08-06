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
    itds__wchix = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        edg__zewfw, = args
        tbpz__zca = cgutils.create_struct_proxy(string_type)(context,
            builder, value=edg__zewfw)
        jpgk__oipm = cgutils.create_struct_proxy(utf8_str_type)(context,
            builder)
        psjn__ayu = cgutils.create_struct_proxy(itds__wchix)(context, builder)
        is_ascii = builder.icmp_unsigned('==', tbpz__zca.is_ascii, lir.
            Constant(tbpz__zca.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (hfim__txamn, ugb__tea):
            with hfim__txamn:
                context.nrt.incref(builder, string_type, edg__zewfw)
                jpgk__oipm.data = tbpz__zca.data
                jpgk__oipm.meminfo = tbpz__zca.meminfo
                psjn__ayu.f1 = tbpz__zca.length
            with ugb__tea:
                inqfu__hone = lir.FunctionType(lir.IntType(64), [lir.
                    IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                    lir.IntType(64), lir.IntType(32)])
                iesmj__ebq = cgutils.get_or_insert_function(builder.module,
                    inqfu__hone, name='unicode_to_utf8')
                jguc__tae = context.get_constant_null(types.voidptr)
                vmsc__yztg = builder.call(iesmj__ebq, [jguc__tae, tbpz__zca
                    .data, tbpz__zca.length, tbpz__zca.kind])
                psjn__ayu.f1 = vmsc__yztg
                wmbrs__hib = builder.add(vmsc__yztg, lir.Constant(lir.
                    IntType(64), 1))
                jpgk__oipm.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=wmbrs__hib, align=32)
                jpgk__oipm.data = context.nrt.meminfo_data(builder,
                    jpgk__oipm.meminfo)
                builder.call(iesmj__ebq, [jpgk__oipm.data, tbpz__zca.data,
                    tbpz__zca.length, tbpz__zca.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    jpgk__oipm.data, [vmsc__yztg]))
        psjn__ayu.f0 = jpgk__oipm._getvalue()
        return psjn__ayu._getvalue()
    return itds__wchix(string_type), codegen


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
        inqfu__hone = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        cnlvf__zifi = cgutils.get_or_insert_function(builder.module,
            inqfu__hone, name='memcmp')
        return builder.call(cnlvf__zifi, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    drnc__ihlo = n(10)

    def impl(n):
        if n == 0:
            return 1
        fjv__tyhhb = 0
        if n < 0:
            n = -n
            fjv__tyhhb += 1
        while n > 0:
            n = n // drnc__ihlo
            fjv__tyhhb += 1
        return fjv__tyhhb
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
        [mityj__oanb] = args
        if isinstance(mityj__oanb, StdStringType):
            return signature(types.float64, mityj__oanb)
        if mityj__oanb == string_type:
            return signature(types.float64, mityj__oanb)


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
    tbpz__zca = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    inqfu__hone = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(64)])
    tktgi__hdm = cgutils.get_or_insert_function(builder.module, inqfu__hone,
        name='init_string_const')
    return builder.call(tktgi__hdm, [tbpz__zca.data, tbpz__zca.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        rycn__ueele = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(rycn__ueele._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return rycn__ueele
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    tbpz__zca = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return tbpz__zca.data


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
        dey__ocyp = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, dey__ocyp)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        ztc__wiuy, = args
        fvwiy__agrm = types.List(string_type)
        fwzl__gbv = numba.cpython.listobj.ListInstance.allocate(context,
            builder, fvwiy__agrm, ztc__wiuy)
        fwzl__gbv.size = ztc__wiuy
        ucrvi__muzoq = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        ucrvi__muzoq.data = fwzl__gbv.value
        return ucrvi__muzoq._getvalue()
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
            mfyan__rtknn = 0
            urc__hzq = v
            if urc__hzq < 0:
                mfyan__rtknn = 1
                urc__hzq = -urc__hzq
            if urc__hzq < 1:
                ipv__hzrvx = 1
            else:
                ipv__hzrvx = 1 + int(np.floor(np.log10(urc__hzq)))
            length = mfyan__rtknn + ipv__hzrvx + 1 + 6
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
    inqfu__hone = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).
        as_pointer()])
    tktgi__hdm = cgutils.get_or_insert_function(builder.module, inqfu__hone,
        name='str_to_float64')
    res = builder.call(tktgi__hdm, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    inqfu__hone = lir.FunctionType(lir.FloatType(), [lir.IntType(8).
        as_pointer()])
    tktgi__hdm = cgutils.get_or_insert_function(builder.module, inqfu__hone,
        name='str_to_float32')
    res = builder.call(tktgi__hdm, (val,))
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
    tbpz__zca = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    inqfu__hone = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    tktgi__hdm = cgutils.get_or_insert_function(builder.module, inqfu__hone,
        name='str_to_int64')
    res = builder.call(tktgi__hdm, (tbpz__zca.data, tbpz__zca.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    tbpz__zca = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    inqfu__hone = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType
        (8).as_pointer(), lir.IntType(64)])
    tktgi__hdm = cgutils.get_or_insert_function(builder.module, inqfu__hone,
        name='str_to_uint64')
    res = builder.call(tktgi__hdm, (tbpz__zca.data, tbpz__zca.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        ldx__xfie = ', '.join('e{}'.format(nvxsb__neps) for nvxsb__neps in
            range(len(args)))
        if ldx__xfie:
            ldx__xfie += ', '
        xxlz__hnjl = ', '.join("{} = ''".format(a) for a in kws.keys())
        hqu__bbbls = f'def format_stub(string, {ldx__xfie} {xxlz__hnjl}):\n'
        hqu__bbbls += '    pass\n'
        aoce__lqlh = {}
        exec(hqu__bbbls, {}, aoce__lqlh)
        veh__blqdt = aoce__lqlh['format_stub']
        ybmu__nvl = numba.core.utils.pysignature(veh__blqdt)
        xupcf__lhs = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, xupcf__lhs).replace(pysig=ybmu__nvl)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    frpot__dsc = pat is not None and len(pat) > 1
    if frpot__dsc:
        rofy__hfucl = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    fwzl__gbv = len(arr)
    sgdb__qzgj = 0
    orw__vacw = 0
    for nvxsb__neps in numba.parfors.parfor.internal_prange(fwzl__gbv):
        if bodo.libs.array_kernels.isna(arr, nvxsb__neps):
            continue
        if frpot__dsc:
            cyvo__rxlw = rofy__hfucl.split(arr[nvxsb__neps], maxsplit=n)
        elif pat == '':
            cyvo__rxlw = [''] + list(arr[nvxsb__neps]) + ['']
        else:
            cyvo__rxlw = arr[nvxsb__neps].split(pat, n)
        sgdb__qzgj += len(cyvo__rxlw)
        for s in cyvo__rxlw:
            orw__vacw += bodo.libs.str_arr_ext.get_utf8_size(s)
    ztgo__ppymj = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        fwzl__gbv, (sgdb__qzgj, orw__vacw), bodo.libs.str_arr_ext.
        string_array_type)
    zsfw__wkm = bodo.libs.array_item_arr_ext.get_offsets(ztgo__ppymj)
    cxu__lvyi = bodo.libs.array_item_arr_ext.get_null_bitmap(ztgo__ppymj)
    unxjq__raumq = bodo.libs.array_item_arr_ext.get_data(ztgo__ppymj)
    iydm__fvuq = 0
    for nvnj__mywl in numba.parfors.parfor.internal_prange(fwzl__gbv):
        zsfw__wkm[nvnj__mywl] = iydm__fvuq
        if bodo.libs.array_kernels.isna(arr, nvnj__mywl):
            bodo.libs.int_arr_ext.set_bit_to_arr(cxu__lvyi, nvnj__mywl, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(cxu__lvyi, nvnj__mywl, 1)
        if frpot__dsc:
            cyvo__rxlw = rofy__hfucl.split(arr[nvnj__mywl], maxsplit=n)
        elif pat == '':
            cyvo__rxlw = [''] + list(arr[nvnj__mywl]) + ['']
        else:
            cyvo__rxlw = arr[nvnj__mywl].split(pat, n)
        hhwoe__lxnh = len(cyvo__rxlw)
        for yesob__ccir in range(hhwoe__lxnh):
            s = cyvo__rxlw[yesob__ccir]
            unxjq__raumq[iydm__fvuq] = s
            iydm__fvuq += 1
    zsfw__wkm[fwzl__gbv] = iydm__fvuq
    return ztgo__ppymj


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                xnudy__nldj = '-0x'
                x = x * -1
            else:
                xnudy__nldj = '0x'
            x = np.uint64(x)
            if x == 0:
                bcbmd__bdgw = 1
            else:
                bcbmd__bdgw = fast_ceil_log2(x + 1)
                bcbmd__bdgw = (bcbmd__bdgw + 3) // 4
            length = len(xnudy__nldj) + bcbmd__bdgw
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, xnudy__nldj._data,
                len(xnudy__nldj), 1)
            int_to_hex(output, bcbmd__bdgw, len(xnudy__nldj), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    ycf__ifu = 0 if x & x - 1 == 0 else 1
    lnbdv__jwf = [np.uint64(18446744069414584320), np.uint64(4294901760),
        np.uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    xlmxw__tikdk = 32
    for nvxsb__neps in range(len(lnbdv__jwf)):
        gjtx__qpph = 0 if x & lnbdv__jwf[nvxsb__neps] == 0 else xlmxw__tikdk
        ycf__ifu = ycf__ifu + gjtx__qpph
        x = x >> gjtx__qpph
        xlmxw__tikdk = xlmxw__tikdk >> 1
    return ycf__ifu


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        chdmj__nxgqm = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        inqfu__hone = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        xkylt__dqxy = cgutils.get_or_insert_function(builder.module,
            inqfu__hone, name='int_to_hex')
        iincg__ihi = builder.inttoptr(builder.add(builder.ptrtoint(
            chdmj__nxgqm.data, lir.IntType(64)), header_len), lir.IntType(8
            ).as_pointer())
        builder.call(xkylt__dqxy, (iincg__ihi, out_len, int_val))
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
