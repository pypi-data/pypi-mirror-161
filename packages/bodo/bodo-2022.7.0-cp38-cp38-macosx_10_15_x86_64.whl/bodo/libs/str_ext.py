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
    dxrsr__rkjg = types.Tuple([utf8_str_type, types.int64])

    def codegen(context, builder, sig, args):
        lpni__fsxp, = args
        bul__pjor = cgutils.create_struct_proxy(string_type)(context,
            builder, value=lpni__fsxp)
        iide__krx = cgutils.create_struct_proxy(utf8_str_type)(context, builder
            )
        dao__eyl = cgutils.create_struct_proxy(dxrsr__rkjg)(context, builder)
        is_ascii = builder.icmp_unsigned('==', bul__pjor.is_ascii, lir.
            Constant(bul__pjor.is_ascii.type, 1))
        with builder.if_else(is_ascii) as (gtvy__ohcru, woka__huqj):
            with gtvy__ohcru:
                context.nrt.incref(builder, string_type, lpni__fsxp)
                iide__krx.data = bul__pjor.data
                iide__krx.meminfo = bul__pjor.meminfo
                dao__eyl.f1 = bul__pjor.length
            with woka__huqj:
                usy__shp = lir.FunctionType(lir.IntType(64), [lir.IntType(8
                    ).as_pointer(), lir.IntType(8).as_pointer(), lir.
                    IntType(64), lir.IntType(32)])
                iijrz__crnii = cgutils.get_or_insert_function(builder.
                    module, usy__shp, name='unicode_to_utf8')
                ekflj__ysu = context.get_constant_null(types.voidptr)
                tyyt__sjjau = builder.call(iijrz__crnii, [ekflj__ysu,
                    bul__pjor.data, bul__pjor.length, bul__pjor.kind])
                dao__eyl.f1 = tyyt__sjjau
                lbpx__aov = builder.add(tyyt__sjjau, lir.Constant(lir.
                    IntType(64), 1))
                iide__krx.meminfo = context.nrt.meminfo_alloc_aligned(builder,
                    size=lbpx__aov, align=32)
                iide__krx.data = context.nrt.meminfo_data(builder,
                    iide__krx.meminfo)
                builder.call(iijrz__crnii, [iide__krx.data, bul__pjor.data,
                    bul__pjor.length, bul__pjor.kind])
                builder.store(lir.Constant(lir.IntType(8), 0), builder.gep(
                    iide__krx.data, [tyyt__sjjau]))
        dao__eyl.f0 = iide__krx._getvalue()
        return dao__eyl._getvalue()
    return dxrsr__rkjg(string_type), codegen


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
        usy__shp = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
        ggqqx__esv = cgutils.get_or_insert_function(builder.module,
            usy__shp, name='memcmp')
        return builder.call(ggqqx__esv, args)
    return types.int32(types.voidptr, types.voidptr, types.intp), codegen


def int_to_str_len(n):
    return len(str(n))


@overload(int_to_str_len)
def overload_int_to_str_len(n):
    igbi__zzwk = n(10)

    def impl(n):
        if n == 0:
            return 1
        iqwr__mlmi = 0
        if n < 0:
            n = -n
            iqwr__mlmi += 1
        while n > 0:
            n = n // igbi__zzwk
            iqwr__mlmi += 1
        return iqwr__mlmi
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
        [dmbfn__kaa] = args
        if isinstance(dmbfn__kaa, StdStringType):
            return signature(types.float64, dmbfn__kaa)
        if dmbfn__kaa == string_type:
            return signature(types.float64, dmbfn__kaa)


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
    bul__pjor = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    usy__shp = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType(8
        ).as_pointer(), lir.IntType(64)])
    xddu__mbkv = cgutils.get_or_insert_function(builder.module, usy__shp,
        name='init_string_const')
    return builder.call(xddu__mbkv, [bul__pjor.data, bul__pjor.length])


def gen_std_str_to_unicode(context, builder, std_str_val, del_str=False):
    kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def _std_str_to_unicode(std_str):
        length = bodo.libs.str_ext.get_std_str_len(std_str)
        oclg__iwo = numba.cpython.unicode._empty_string(kind, length, 1)
        bodo.libs.str_arr_ext._memcpy(oclg__iwo._data, bodo.libs.str_ext.
            get_c_str(std_str), length, 1)
        if del_str:
            bodo.libs.str_ext.del_str(std_str)
        return oclg__iwo
    val = context.compile_internal(builder, _std_str_to_unicode,
        string_type(bodo.libs.str_ext.std_str_type), [std_str_val])
    return val


def gen_get_unicode_chars(context, builder, unicode_val):
    bul__pjor = cgutils.create_struct_proxy(string_type)(context, builder,
        value=unicode_val)
    return bul__pjor.data


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
        vus__zdyfb = [('data', types.List(string_type))]
        models.StructModel.__init__(self, dmm, fe_type, vus__zdyfb)


make_attribute_wrapper(RandomAccessStringArrayType, 'data', '_data')


@intrinsic
def alloc_random_access_string_array(typingctx, n_t=None):

    def codegen(context, builder, sig, args):
        myjc__znu, = args
        bmae__hmrf = types.List(string_type)
        frw__gfutn = numba.cpython.listobj.ListInstance.allocate(context,
            builder, bmae__hmrf, myjc__znu)
        frw__gfutn.size = myjc__znu
        rch__vmqxm = cgutils.create_struct_proxy(sig.return_type)(context,
            builder)
        rch__vmqxm.data = frw__gfutn.value
        return rch__vmqxm._getvalue()
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
            hjae__yaho = 0
            nut__rbw = v
            if nut__rbw < 0:
                hjae__yaho = 1
                nut__rbw = -nut__rbw
            if nut__rbw < 1:
                drv__ulbj = 1
            else:
                drv__ulbj = 1 + int(np.floor(np.log10(nut__rbw)))
            length = hjae__yaho + drv__ulbj + 1 + 6
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
    usy__shp = lir.FunctionType(lir.DoubleType(), [lir.IntType(8).as_pointer()]
        )
    xddu__mbkv = cgutils.get_or_insert_function(builder.module, usy__shp,
        name='str_to_float64')
    res = builder.call(xddu__mbkv, (val,))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(StdStringType, types.float32)
def cast_str_to_float32(context, builder, fromty, toty, val):
    usy__shp = lir.FunctionType(lir.FloatType(), [lir.IntType(8).as_pointer()])
    xddu__mbkv = cgutils.get_or_insert_function(builder.module, usy__shp,
        name='str_to_float32')
    res = builder.call(xddu__mbkv, (val,))
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
    bul__pjor = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    usy__shp = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(8)
        .as_pointer(), lir.IntType(64)])
    xddu__mbkv = cgutils.get_or_insert_function(builder.module, usy__shp,
        name='str_to_int64')
    res = builder.call(xddu__mbkv, (bul__pjor.data, bul__pjor.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@lower_cast(string_type, types.uint64)
@lower_cast(string_type, types.uint32)
@lower_cast(string_type, types.uint16)
@lower_cast(string_type, types.uint8)
def cast_unicode_str_to_uint64(context, builder, fromty, toty, val):
    bul__pjor = cgutils.create_struct_proxy(string_type)(context, builder,
        value=val)
    usy__shp = lir.FunctionType(lir.IntType(toty.bitwidth), [lir.IntType(8)
        .as_pointer(), lir.IntType(64)])
    xddu__mbkv = cgutils.get_or_insert_function(builder.module, usy__shp,
        name='str_to_uint64')
    res = builder.call(xddu__mbkv, (bul__pjor.data, bul__pjor.length))
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return res


@infer_getattr
class StringAttribute(AttributeTemplate):
    key = types.UnicodeType

    @bound_function('str.format', no_unliteral=True)
    def resolve_format(self, string_typ, args, kws):
        kws = dict(kws)
        xqml__jbgih = ', '.join('e{}'.format(lrzwi__dzqtg) for lrzwi__dzqtg in
            range(len(args)))
        if xqml__jbgih:
            xqml__jbgih += ', '
        rplw__fjey = ', '.join("{} = ''".format(a) for a in kws.keys())
        gleb__snis = f'def format_stub(string, {xqml__jbgih} {rplw__fjey}):\n'
        gleb__snis += '    pass\n'
        cioeo__vqri = {}
        exec(gleb__snis, {}, cioeo__vqri)
        agb__ljwm = cioeo__vqri['format_stub']
        pphw__ikr = numba.core.utils.pysignature(agb__ljwm)
        xgle__zmze = (string_typ,) + args + tuple(kws.values())
        return signature(string_typ, xgle__zmze).replace(pysig=pphw__ikr)


@numba.njit(cache=True)
def str_split(arr, pat, n):
    pjbn__xvbub = pat is not None and len(pat) > 1
    if pjbn__xvbub:
        hmv__egcb = re.compile(pat)
        if n == -1:
            n = 0
    elif n == 0:
        n = -1
    frw__gfutn = len(arr)
    trdo__koq = 0
    qpkad__zoe = 0
    for lrzwi__dzqtg in numba.parfors.parfor.internal_prange(frw__gfutn):
        if bodo.libs.array_kernels.isna(arr, lrzwi__dzqtg):
            continue
        if pjbn__xvbub:
            qaz__bhggz = hmv__egcb.split(arr[lrzwi__dzqtg], maxsplit=n)
        elif pat == '':
            qaz__bhggz = [''] + list(arr[lrzwi__dzqtg]) + ['']
        else:
            qaz__bhggz = arr[lrzwi__dzqtg].split(pat, n)
        trdo__koq += len(qaz__bhggz)
        for s in qaz__bhggz:
            qpkad__zoe += bodo.libs.str_arr_ext.get_utf8_size(s)
    dlwl__fkm = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        frw__gfutn, (trdo__koq, qpkad__zoe), bodo.libs.str_arr_ext.
        string_array_type)
    zle__mltfs = bodo.libs.array_item_arr_ext.get_offsets(dlwl__fkm)
    axj__htaw = bodo.libs.array_item_arr_ext.get_null_bitmap(dlwl__fkm)
    ecqi__volmz = bodo.libs.array_item_arr_ext.get_data(dlwl__fkm)
    jyyzl__aklbs = 0
    for ptw__zdzs in numba.parfors.parfor.internal_prange(frw__gfutn):
        zle__mltfs[ptw__zdzs] = jyyzl__aklbs
        if bodo.libs.array_kernels.isna(arr, ptw__zdzs):
            bodo.libs.int_arr_ext.set_bit_to_arr(axj__htaw, ptw__zdzs, 0)
            continue
        bodo.libs.int_arr_ext.set_bit_to_arr(axj__htaw, ptw__zdzs, 1)
        if pjbn__xvbub:
            qaz__bhggz = hmv__egcb.split(arr[ptw__zdzs], maxsplit=n)
        elif pat == '':
            qaz__bhggz = [''] + list(arr[ptw__zdzs]) + ['']
        else:
            qaz__bhggz = arr[ptw__zdzs].split(pat, n)
        ktw__huvkg = len(qaz__bhggz)
        for oaoj__rzxv in range(ktw__huvkg):
            s = qaz__bhggz[oaoj__rzxv]
            ecqi__volmz[jyyzl__aklbs] = s
            jyyzl__aklbs += 1
    zle__mltfs[frw__gfutn] = jyyzl__aklbs
    return dlwl__fkm


@overload(hex)
def overload_hex(x):
    if isinstance(x, types.Integer):
        kind = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(x):
            x = np.int64(x)
            if x < 0:
                muqjk__cduzd = '-0x'
                x = x * -1
            else:
                muqjk__cduzd = '0x'
            x = np.uint64(x)
            if x == 0:
                cht__xcwss = 1
            else:
                cht__xcwss = fast_ceil_log2(x + 1)
                cht__xcwss = (cht__xcwss + 3) // 4
            length = len(muqjk__cduzd) + cht__xcwss
            output = numba.cpython.unicode._empty_string(kind, length, 1)
            bodo.libs.str_arr_ext._memcpy(output._data, muqjk__cduzd._data,
                len(muqjk__cduzd), 1)
            int_to_hex(output, cht__xcwss, len(muqjk__cduzd), x)
            return output
        return impl


@register_jitable
def fast_ceil_log2(x):
    sti__awv = 0 if x & x - 1 == 0 else 1
    illy__rgn = [np.uint64(18446744069414584320), np.uint64(4294901760), np
        .uint64(65280), np.uint64(240), np.uint64(12), np.uint64(2)]
    zdlew__oka = 32
    for lrzwi__dzqtg in range(len(illy__rgn)):
        swza__cswe = 0 if x & illy__rgn[lrzwi__dzqtg] == 0 else zdlew__oka
        sti__awv = sti__awv + swza__cswe
        x = x >> swza__cswe
        zdlew__oka = zdlew__oka >> 1
    return sti__awv


@intrinsic
def int_to_hex(typingctx, output, out_len, header_len, int_val):

    def codegen(context, builder, sig, args):
        output, out_len, header_len, int_val = args
        qcm__dsjh = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=output)
        usy__shp = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        tgnru__bkajz = cgutils.get_or_insert_function(builder.module,
            usy__shp, name='int_to_hex')
        zdr__jltg = builder.inttoptr(builder.add(builder.ptrtoint(qcm__dsjh
            .data, lir.IntType(64)), header_len), lir.IntType(8).as_pointer())
        builder.call(tgnru__bkajz, (zdr__jltg, out_len, int_val))
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
