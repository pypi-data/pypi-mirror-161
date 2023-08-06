"""Dictionary encoded array data type, similar to DictionaryArray of Arrow.
The purpose is to improve memory consumption and performance over string_array_type for
string arrays that have a lot of repetitive values (typical in practice).
Can be extended to be used with types other than strings as well.
See:
https://bodo.atlassian.net/browse/BE-2295
https://bodo.atlassian.net/wiki/spaces/B/pages/993722369/Dictionary-encoded+String+Array+Support+in+Parquet+read+compute+...
https://arrow.apache.org/docs/cpp/api/array.html#dictionary-encoded
"""
import operator
import re
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow as pa
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_new_ref, lower_builtin, lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, typeof_impl, unbox
import bodo
from bodo.libs import hstr_ext
from bodo.libs.bool_arr_ext import init_bool_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, get_str_arr_item_length, overload_str_arr_astype, pre_alloc_string_array, string_array_type
from bodo.utils.typing import BodoArrayIterator, is_overload_none, raise_bodo_error
ll.add_symbol('box_dict_str_array', hstr_ext.box_dict_str_array)
dict_indices_arr_type = IntegerArrayType(types.int32)


class DictionaryArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self, arr_data_type):
        self.data = arr_data_type
        super(DictionaryArrayType, self).__init__(name=
            f'DictionaryArrayType({arr_data_type})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    @property
    def dtype(self):
        return self.data.dtype

    def copy(self):
        return DictionaryArrayType(self.data)

    @property
    def indices_type(self):
        return dict_indices_arr_type

    @property
    def indices_dtype(self):
        return dict_indices_arr_type.dtype

    def unify(self, typingctx, other):
        if other == string_array_type:
            return string_array_type


dict_str_arr_type = DictionaryArrayType(string_array_type)


@register_model(DictionaryArrayType)
class DictionaryArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        hoc__pfg = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, hoc__pfg)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        npoqn__hwphz, kfu__ecgp, fvnfz__qgag = args
        fbj__gzuyt = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        fbj__gzuyt.data = npoqn__hwphz
        fbj__gzuyt.indices = kfu__ecgp
        fbj__gzuyt.has_global_dictionary = fvnfz__qgag
        context.nrt.incref(builder, signature.args[0], npoqn__hwphz)
        context.nrt.incref(builder, signature.args[1], kfu__ecgp)
        return fbj__gzuyt._getvalue()
    pdfvo__mtuiw = DictionaryArrayType(data_t)
    brr__wlmts = pdfvo__mtuiw(data_t, indices_t, types.bool_)
    return brr__wlmts, codegen


@typeof_impl.register(pa.DictionaryArray)
def typeof_dict_value(val, c):
    if val.type.value_type == pa.string():
        return dict_str_arr_type


def to_pa_dict_arr(A):
    if isinstance(A, pa.DictionaryArray):
        return A
    for i in range(len(A)):
        if pd.isna(A[i]):
            A[i] = None
    return pa.array(A).dictionary_encode()


@unbox(DictionaryArrayType)
def unbox_dict_arr(typ, val, c):
    if bodo.hiframes.boxing._use_dict_str_type:
        usgb__gdz = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(usgb__gdz, [val])
        c.pyapi.decref(usgb__gdz)
    fbj__gzuyt = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qoy__wzrr = c.pyapi.object_getattr_string(val, 'dictionary')
    pqihk__sqyfm = c.pyapi.bool_from_bool(c.context.get_constant(types.
        bool_, False))
    qtrb__ljw = c.pyapi.call_method(qoy__wzrr, 'to_numpy', (pqihk__sqyfm,))
    fbj__gzuyt.data = c.unbox(typ.data, qtrb__ljw).value
    xdody__vbhfs = c.pyapi.object_getattr_string(val, 'indices')
    bxq__pyx = c.context.insert_const_string(c.builder.module, 'pandas')
    cgazq__jyxr = c.pyapi.import_module_noblock(bxq__pyx)
    ipfj__lyfz = c.pyapi.string_from_constant_string('Int32')
    huj__vhjot = c.pyapi.call_method(cgazq__jyxr, 'array', (xdody__vbhfs,
        ipfj__lyfz))
    fbj__gzuyt.indices = c.unbox(dict_indices_arr_type, huj__vhjot).value
    fbj__gzuyt.has_global_dictionary = c.context.get_constant(types.bool_, 
        False)
    c.pyapi.decref(qoy__wzrr)
    c.pyapi.decref(pqihk__sqyfm)
    c.pyapi.decref(qtrb__ljw)
    c.pyapi.decref(xdody__vbhfs)
    c.pyapi.decref(cgazq__jyxr)
    c.pyapi.decref(ipfj__lyfz)
    c.pyapi.decref(huj__vhjot)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    zqa__idg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(fbj__gzuyt._getvalue(), is_error=zqa__idg)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    fbj__gzuyt = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, fbj__gzuyt.data)
        urmc__odxsv = c.box(typ.data, fbj__gzuyt.data)
        ajkd__chuub = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, fbj__gzuyt.indices)
        qbun__abqn = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        ynepc__echt = cgutils.get_or_insert_function(c.builder.module,
            qbun__abqn, name='box_dict_str_array')
        lfxt__pnprt = cgutils.create_struct_proxy(types.Array(types.int32, 
            1, 'C'))(c.context, c.builder, ajkd__chuub.data)
        gzsyf__hyp = c.builder.extract_value(lfxt__pnprt.shape, 0)
        ltqf__nsi = lfxt__pnprt.data
        rnv__vpy = cgutils.create_struct_proxy(types.Array(types.int8, 1, 'C')
            )(c.context, c.builder, ajkd__chuub.null_bitmap).data
        qtrb__ljw = c.builder.call(ynepc__echt, [gzsyf__hyp, urmc__odxsv,
            ltqf__nsi, rnv__vpy])
        c.pyapi.decref(urmc__odxsv)
    else:
        bxq__pyx = c.context.insert_const_string(c.builder.module, 'pyarrow')
        sfru__ectsl = c.pyapi.import_module_noblock(bxq__pyx)
        vezo__slvj = c.pyapi.object_getattr_string(sfru__ectsl,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, fbj__gzuyt.data)
        urmc__odxsv = c.box(typ.data, fbj__gzuyt.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, fbj__gzuyt.
            indices)
        xdody__vbhfs = c.box(dict_indices_arr_type, fbj__gzuyt.indices)
        rjng__wgeh = c.pyapi.call_method(vezo__slvj, 'from_arrays', (
            xdody__vbhfs, urmc__odxsv))
        pqihk__sqyfm = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        qtrb__ljw = c.pyapi.call_method(rjng__wgeh, 'to_numpy', (pqihk__sqyfm,)
            )
        c.pyapi.decref(sfru__ectsl)
        c.pyapi.decref(urmc__odxsv)
        c.pyapi.decref(xdody__vbhfs)
        c.pyapi.decref(vezo__slvj)
        c.pyapi.decref(rjng__wgeh)
        c.pyapi.decref(pqihk__sqyfm)
    c.context.nrt.decref(c.builder, typ, val)
    return qtrb__ljw


@overload(len, no_unliteral=True)
def overload_dict_arr_len(A):
    if isinstance(A, DictionaryArrayType):
        return lambda A: len(A._indices)


@overload_attribute(DictionaryArrayType, 'shape')
def overload_dict_arr_shape(A):
    return lambda A: (len(A._indices),)


@overload_attribute(DictionaryArrayType, 'ndim')
def overload_dict_arr_ndim(A):
    return lambda A: 1


@overload_attribute(DictionaryArrayType, 'size')
def overload_dict_arr_size(A):
    return lambda A: len(A._indices)


@overload_method(DictionaryArrayType, 'tolist', no_unliteral=True)
def overload_dict_arr_tolist(A):
    return lambda A: list(A)


overload_method(DictionaryArrayType, 'astype', no_unliteral=True)(
    overload_str_arr_astype)


@overload_method(DictionaryArrayType, 'copy', no_unliteral=True)
def overload_dict_arr_copy(A):

    def copy_impl(A):
        return init_dict_arr(A._data.copy(), A._indices.copy(), A.
            _has_global_dictionary)
    return copy_impl


@overload_attribute(DictionaryArrayType, 'dtype')
def overload_dict_arr_dtype(A):
    return lambda A: A._data.dtype


@overload_attribute(DictionaryArrayType, 'nbytes')
def dict_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._indices.nbytes


@lower_constant(DictionaryArrayType)
def lower_constant_dict_arr(context, builder, typ, pyval):
    if bodo.hiframes.boxing._use_dict_str_type and isinstance(pyval, np.ndarray
        ):
        pyval = pa.array(pyval).dictionary_encode()
    kjcnq__akb = pyval.dictionary.to_numpy(False)
    mltp__mldv = pd.array(pyval.indices, 'Int32')
    kjcnq__akb = context.get_constant_generic(builder, typ.data, kjcnq__akb)
    mltp__mldv = context.get_constant_generic(builder,
        dict_indices_arr_type, mltp__mldv)
    nzg__zgxh = context.get_constant(types.bool_, False)
    qtct__mebxw = lir.Constant.literal_struct([kjcnq__akb, mltp__mldv,
        nzg__zgxh])
    return qtct__mebxw


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            mcc__umxea = A._indices[ind]
            return A._data[mcc__umxea]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        npoqn__hwphz = A._data
        kfu__ecgp = A._indices
        gzsyf__hyp = len(kfu__ecgp)
        fshd__wbi = [get_str_arr_item_length(npoqn__hwphz, i) for i in
            range(len(npoqn__hwphz))]
        vds__mhd = 0
        for i in range(gzsyf__hyp):
            if not bodo.libs.array_kernels.isna(kfu__ecgp, i):
                vds__mhd += fshd__wbi[kfu__ecgp[i]]
        ekvf__iucp = pre_alloc_string_array(gzsyf__hyp, vds__mhd)
        for i in range(gzsyf__hyp):
            if bodo.libs.array_kernels.isna(kfu__ecgp, i):
                bodo.libs.array_kernels.setna(ekvf__iucp, i)
                continue
            ind = kfu__ecgp[i]
            if bodo.libs.array_kernels.isna(npoqn__hwphz, ind):
                bodo.libs.array_kernels.setna(ekvf__iucp, i)
                continue
            ekvf__iucp[i] = npoqn__hwphz[ind]
        return ekvf__iucp
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    mcc__umxea = -1
    npoqn__hwphz = arr._data
    for i in range(len(npoqn__hwphz)):
        if bodo.libs.array_kernels.isna(npoqn__hwphz, i):
            continue
        if npoqn__hwphz[i] == val:
            mcc__umxea = i
            break
    return mcc__umxea


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    gzsyf__hyp = len(arr)
    mcc__umxea = find_dict_ind(arr, val)
    if mcc__umxea == -1:
        return init_bool_array(np.full(gzsyf__hyp, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == mcc__umxea


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    gzsyf__hyp = len(arr)
    mcc__umxea = find_dict_ind(arr, val)
    if mcc__umxea == -1:
        return init_bool_array(np.full(gzsyf__hyp, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != mcc__umxea


def get_binary_op_overload(op, lhs, rhs):
    if op == operator.eq:
        if lhs == dict_str_arr_type and types.unliteral(rhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_eq(lhs, rhs)
        if rhs == dict_str_arr_type and types.unliteral(lhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_eq(rhs, lhs)
    if op == operator.ne:
        if lhs == dict_str_arr_type and types.unliteral(rhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_ne(lhs, rhs)
        if rhs == dict_str_arr_type and types.unliteral(lhs
            ) == bodo.string_type:
            return lambda lhs, rhs: dict_arr_ne(rhs, lhs)


def convert_dict_arr_to_int(arr, dtype):
    return arr


@overload(convert_dict_arr_to_int)
def convert_dict_arr_to_int_overload(arr, dtype):

    def impl(arr, dtype):
        cthta__eam = arr._data
        pja__byr = bodo.libs.int_arr_ext.alloc_int_array(len(cthta__eam), dtype
            )
        for zixp__giu in range(len(cthta__eam)):
            if bodo.libs.array_kernels.isna(cthta__eam, zixp__giu):
                bodo.libs.array_kernels.setna(pja__byr, zixp__giu)
                continue
            pja__byr[zixp__giu] = np.int64(cthta__eam[zixp__giu])
        gzsyf__hyp = len(arr)
        kfu__ecgp = arr._indices
        ekvf__iucp = bodo.libs.int_arr_ext.alloc_int_array(gzsyf__hyp, dtype)
        for i in range(gzsyf__hyp):
            if bodo.libs.array_kernels.isna(kfu__ecgp, i):
                bodo.libs.array_kernels.setna(ekvf__iucp, i)
                continue
            ekvf__iucp[i] = pja__byr[kfu__ecgp[i]]
        return ekvf__iucp
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    csw__qwk = len(arrs)
    dii__fnjct = 'def impl(arrs, sep):\n'
    dii__fnjct += '  ind_map = {}\n'
    dii__fnjct += '  out_strs = []\n'
    dii__fnjct += '  n = len(arrs[0])\n'
    for i in range(csw__qwk):
        dii__fnjct += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(csw__qwk):
        dii__fnjct += f'  data{i} = arrs[{i}]._data\n'
    dii__fnjct += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    dii__fnjct += '  for i in range(n):\n'
    rvwui__elrm = ' or '.join([
        f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for i in range(csw__qwk)]
        )
    dii__fnjct += f'    if {rvwui__elrm}:\n'
    dii__fnjct += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    dii__fnjct += '      continue\n'
    for i in range(csw__qwk):
        dii__fnjct += f'    ind{i} = indices{i}[i]\n'
    xcqb__sseo = '(' + ', '.join(f'ind{i}' for i in range(csw__qwk)) + ')'
    dii__fnjct += f'    if {xcqb__sseo} not in ind_map:\n'
    dii__fnjct += '      out_ind = len(out_strs)\n'
    dii__fnjct += f'      ind_map[{xcqb__sseo}] = out_ind\n'
    vay__puj = "''" if is_overload_none(sep) else 'sep'
    hqbpk__zwshu = ', '.join([f'data{i}[ind{i}]' for i in range(csw__qwk)])
    dii__fnjct += f'      v = {vay__puj}.join([{hqbpk__zwshu}])\n'
    dii__fnjct += '      out_strs.append(v)\n'
    dii__fnjct += '    else:\n'
    dii__fnjct += f'      out_ind = ind_map[{xcqb__sseo}]\n'
    dii__fnjct += '    out_indices[i] = out_ind\n'
    dii__fnjct += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    dii__fnjct += """  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)
"""
    xgkt__nty = {}
    exec(dii__fnjct, {'bodo': bodo, 'numba': numba, 'np': np}, xgkt__nty)
    impl = xgkt__nty['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    fnw__fzq = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    brr__wlmts = toty(fromty)
    ulgwn__rvdsn = context.compile_internal(builder, fnw__fzq, brr__wlmts,
        (val,))
    return impl_ret_new_ref(context, builder, toty, ulgwn__rvdsn)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    kjcnq__akb = arr._data
    jfjp__yzbl = len(kjcnq__akb)
    dzdl__blqpg = pre_alloc_string_array(jfjp__yzbl, -1)
    if regex:
        dmxq__muml = re.compile(pat, flags)
        for i in range(jfjp__yzbl):
            if bodo.libs.array_kernels.isna(kjcnq__akb, i):
                bodo.libs.array_kernels.setna(dzdl__blqpg, i)
                continue
            dzdl__blqpg[i] = dmxq__muml.sub(repl=repl, string=kjcnq__akb[i])
    else:
        for i in range(jfjp__yzbl):
            if bodo.libs.array_kernels.isna(kjcnq__akb, i):
                bodo.libs.array_kernels.setna(dzdl__blqpg, i)
                continue
            dzdl__blqpg[i] = kjcnq__akb[i].replace(pat, repl)
    return init_dict_arr(dzdl__blqpg, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    fbj__gzuyt = arr._data
    iugs__iupbw = len(fbj__gzuyt)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(iugs__iupbw)
    for i in range(iugs__iupbw):
        dict_arr_out[i] = fbj__gzuyt[i].startswith(pat)
    mltp__mldv = arr._indices
    arst__imgpa = len(mltp__mldv)
    ekvf__iucp = bodo.libs.bool_arr_ext.alloc_bool_array(arst__imgpa)
    for i in range(arst__imgpa):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(ekvf__iucp, i)
        else:
            ekvf__iucp[i] = dict_arr_out[mltp__mldv[i]]
    return ekvf__iucp


@register_jitable
def str_endswith(arr, pat, na):
    fbj__gzuyt = arr._data
    iugs__iupbw = len(fbj__gzuyt)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(iugs__iupbw)
    for i in range(iugs__iupbw):
        dict_arr_out[i] = fbj__gzuyt[i].endswith(pat)
    mltp__mldv = arr._indices
    arst__imgpa = len(mltp__mldv)
    ekvf__iucp = bodo.libs.bool_arr_ext.alloc_bool_array(arst__imgpa)
    for i in range(arst__imgpa):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(ekvf__iucp, i)
        else:
            ekvf__iucp[i] = dict_arr_out[mltp__mldv[i]]
    return ekvf__iucp


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    fbj__gzuyt = arr._data
    uhna__wxx = pd.Series(fbj__gzuyt)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = uhna__wxx.array._str_contains(pat, case, flags, na,
            regex)
    mltp__mldv = arr._indices
    arst__imgpa = len(mltp__mldv)
    ekvf__iucp = bodo.libs.bool_arr_ext.alloc_bool_array(arst__imgpa)
    for i in range(arst__imgpa):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(ekvf__iucp, i)
        else:
            ekvf__iucp[i] = dict_arr_out[mltp__mldv[i]]
    return ekvf__iucp


@register_jitable
def str_contains_non_regex(arr, pat, case):
    fbj__gzuyt = arr._data
    iugs__iupbw = len(fbj__gzuyt)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(iugs__iupbw)
    if not case:
        jpfu__govt = pat.upper()
    for i in range(iugs__iupbw):
        if case:
            dict_arr_out[i] = pat in fbj__gzuyt[i]
        else:
            dict_arr_out[i] = jpfu__govt in fbj__gzuyt[i].upper()
    mltp__mldv = arr._indices
    arst__imgpa = len(mltp__mldv)
    ekvf__iucp = bodo.libs.bool_arr_ext.alloc_bool_array(arst__imgpa)
    for i in range(arst__imgpa):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(ekvf__iucp, i)
        else:
            ekvf__iucp[i] = dict_arr_out[mltp__mldv[i]]
    return ekvf__iucp


@numba.njit
def str_match(arr, pat, case, flags, na):
    fbj__gzuyt = arr._data
    mltp__mldv = arr._indices
    arst__imgpa = len(mltp__mldv)
    ekvf__iucp = bodo.libs.bool_arr_ext.alloc_bool_array(arst__imgpa)
    uhna__wxx = pd.Series(fbj__gzuyt)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = uhna__wxx.array._str_match(pat, case, flags, na)
    for i in range(arst__imgpa):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(ekvf__iucp, i)
        else:
            ekvf__iucp[i] = dict_arr_out[mltp__mldv[i]]
    return ekvf__iucp


def create_simple_str2str_methods(func_name, func_args):
    dii__fnjct = f"""def str_{func_name}({', '.join(func_args)}):
    data_arr = arr._data
    n_data = len(data_arr)
    out_str_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_data, -1)
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            bodo.libs.array_kernels.setna(out_str_arr, i)
            continue
        out_str_arr[i] = data_arr[i].{func_name}({', '.join(func_args[1:])})
    return init_dict_arr(out_str_arr, arr._indices.copy(), arr._has_global_dictionary)
"""
    xgkt__nty = {}
    exec(dii__fnjct, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, xgkt__nty)
    return xgkt__nty[f'str_{func_name}']


def _register_simple_str2str_methods():
    yiv__kfj = {**dict.fromkeys(['capitalize', 'lower', 'swapcase', 'title',
        'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip', 'strip'],
        ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust', 'rjust'],
        ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'], ('arr',
        'width'))}
    for func_name in yiv__kfj.keys():
        qytk__cuwc = create_simple_str2str_methods(func_name, yiv__kfj[
            func_name])
        qytk__cuwc = register_jitable(qytk__cuwc)
        globals()[f'str_{func_name}'] = qytk__cuwc


_register_simple_str2str_methods()


def create_find_methods(func_name):
    dii__fnjct = f"""def str_{func_name}(arr, sub, start, end):
  data_arr = arr._data
  indices_arr = arr._indices
  n_data = len(data_arr)
  n_indices = len(indices_arr)
  tmp_dict_arr = bodo.libs.int_arr_ext.alloc_int_array(n_data, np.int64)
  out_int_arr = bodo.libs.int_arr_ext.alloc_int_array(n_indices, np.int64)
  for i in range(n_data):
    if bodo.libs.array_kernels.isna(data_arr, i):
      bodo.libs.array_kernels.setna(tmp_dict_arr, i)
      continue
    tmp_dict_arr[i] = data_arr[i].{func_name}(sub, start, end)
  for i in range(n_indices):
    if bodo.libs.array_kernels.isna(indices_arr, i) or bodo.libs.array_kernels.isna(
      tmp_dict_arr, indices_arr[i]
    ):
      bodo.libs.array_kernels.setna(out_int_arr, i)
    else:
      out_int_arr[i] = tmp_dict_arr[indices_arr[i]]
  return out_int_arr"""
    xgkt__nty = {}
    exec(dii__fnjct, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, xgkt__nty)
    return xgkt__nty[f'str_{func_name}']


def _register_find_methods():
    snd__feeh = ['find', 'rfind']
    for func_name in snd__feeh:
        qytk__cuwc = create_find_methods(func_name)
        qytk__cuwc = register_jitable(qytk__cuwc)
        globals()[f'str_{func_name}'] = qytk__cuwc


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    kjcnq__akb = arr._data
    mltp__mldv = arr._indices
    jfjp__yzbl = len(kjcnq__akb)
    arst__imgpa = len(mltp__mldv)
    usbe__ltqg = bodo.libs.int_arr_ext.alloc_int_array(jfjp__yzbl, np.int64)
    fbvl__emn = bodo.libs.int_arr_ext.alloc_int_array(arst__imgpa, np.int64)
    regex = re.compile(pat, flags)
    for i in range(jfjp__yzbl):
        if bodo.libs.array_kernels.isna(kjcnq__akb, i):
            bodo.libs.array_kernels.setna(usbe__ltqg, i)
            continue
        usbe__ltqg[i] = bodo.libs.str_ext.str_findall_count(regex,
            kjcnq__akb[i])
    for i in range(arst__imgpa):
        if bodo.libs.array_kernels.isna(mltp__mldv, i
            ) or bodo.libs.array_kernels.isna(usbe__ltqg, mltp__mldv[i]):
            bodo.libs.array_kernels.setna(fbvl__emn, i)
        else:
            fbvl__emn[i] = usbe__ltqg[mltp__mldv[i]]
    return fbvl__emn


@register_jitable
def str_len(arr):
    kjcnq__akb = arr._data
    mltp__mldv = arr._indices
    arst__imgpa = len(mltp__mldv)
    usbe__ltqg = bodo.libs.array_kernels.get_arr_lens(kjcnq__akb, False)
    fbvl__emn = bodo.libs.int_arr_ext.alloc_int_array(arst__imgpa, np.int64)
    for i in range(arst__imgpa):
        if bodo.libs.array_kernels.isna(mltp__mldv, i
            ) or bodo.libs.array_kernels.isna(usbe__ltqg, mltp__mldv[i]):
            bodo.libs.array_kernels.setna(fbvl__emn, i)
        else:
            fbvl__emn[i] = usbe__ltqg[mltp__mldv[i]]
    return fbvl__emn


@register_jitable
def str_slice(arr, start, stop, step):
    kjcnq__akb = arr._data
    jfjp__yzbl = len(kjcnq__akb)
    dzdl__blqpg = bodo.libs.str_arr_ext.pre_alloc_string_array(jfjp__yzbl, -1)
    for i in range(jfjp__yzbl):
        if bodo.libs.array_kernels.isna(kjcnq__akb, i):
            bodo.libs.array_kernels.setna(dzdl__blqpg, i)
            continue
        dzdl__blqpg[i] = kjcnq__akb[i][start:stop:step]
    return init_dict_arr(dzdl__blqpg, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    kjcnq__akb = arr._data
    mltp__mldv = arr._indices
    jfjp__yzbl = len(kjcnq__akb)
    arst__imgpa = len(mltp__mldv)
    dzdl__blqpg = pre_alloc_string_array(jfjp__yzbl, -1)
    ekvf__iucp = pre_alloc_string_array(arst__imgpa, -1)
    for zixp__giu in range(jfjp__yzbl):
        if bodo.libs.array_kernels.isna(kjcnq__akb, zixp__giu) or not -len(
            kjcnq__akb[zixp__giu]) <= i < len(kjcnq__akb[zixp__giu]):
            bodo.libs.array_kernels.setna(dzdl__blqpg, zixp__giu)
            continue
        dzdl__blqpg[zixp__giu] = kjcnq__akb[zixp__giu][i]
    for zixp__giu in range(arst__imgpa):
        if bodo.libs.array_kernels.isna(mltp__mldv, zixp__giu
            ) or bodo.libs.array_kernels.isna(dzdl__blqpg, mltp__mldv[
            zixp__giu]):
            bodo.libs.array_kernels.setna(ekvf__iucp, zixp__giu)
            continue
        ekvf__iucp[zixp__giu] = dzdl__blqpg[mltp__mldv[zixp__giu]]
    return ekvf__iucp


@register_jitable
def str_repeat_int(arr, repeats):
    kjcnq__akb = arr._data
    jfjp__yzbl = len(kjcnq__akb)
    dzdl__blqpg = pre_alloc_string_array(jfjp__yzbl, -1)
    for i in range(jfjp__yzbl):
        if bodo.libs.array_kernels.isna(kjcnq__akb, i):
            bodo.libs.array_kernels.setna(dzdl__blqpg, i)
            continue
        dzdl__blqpg[i] = kjcnq__akb[i] * repeats
    return init_dict_arr(dzdl__blqpg, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    dii__fnjct = f"""def str_{func_name}(arr):
    data_arr = arr._data
    indices_arr = arr._indices
    n_data = len(data_arr)
    n_indices = len(indices_arr)
    out_dict_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n_data)
    out_bool_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n_indices)
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            bodo.libs.array_kernels.setna(out_dict_arr, i)
            continue
        out_dict_arr[i] = np.bool_(data_arr[i].{func_name}())
    for i in range(n_indices):
        if bodo.libs.array_kernels.isna(indices_arr, i) or bodo.libs.array_kernels.isna(
            data_arr, indices_arr[i]        ):
            bodo.libs.array_kernels.setna(out_bool_arr, i)
        else:
            out_bool_arr[i] = out_dict_arr[indices_arr[i]]
    return out_bool_arr"""
    xgkt__nty = {}
    exec(dii__fnjct, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, xgkt__nty)
    return xgkt__nty[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        qytk__cuwc = create_str2bool_methods(func_name)
        qytk__cuwc = register_jitable(qytk__cuwc)
        globals()[f'str_{func_name}'] = qytk__cuwc


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    kjcnq__akb = arr._data
    mltp__mldv = arr._indices
    jfjp__yzbl = len(kjcnq__akb)
    arst__imgpa = len(mltp__mldv)
    regex = re.compile(pat, flags=flags)
    oqt__naqdj = []
    for fpgt__arc in range(n_cols):
        oqt__naqdj.append(pre_alloc_string_array(jfjp__yzbl, -1))
    kwsn__ccgf = bodo.libs.bool_arr_ext.alloc_bool_array(jfjp__yzbl)
    rjj__fglep = mltp__mldv.copy()
    for i in range(jfjp__yzbl):
        if bodo.libs.array_kernels.isna(kjcnq__akb, i):
            kwsn__ccgf[i] = True
            for zixp__giu in range(n_cols):
                bodo.libs.array_kernels.setna(oqt__naqdj[zixp__giu], i)
            continue
        rthd__kkzw = regex.search(kjcnq__akb[i])
        if rthd__kkzw:
            kwsn__ccgf[i] = False
            sftkj__adqfk = rthd__kkzw.groups()
            for zixp__giu in range(n_cols):
                oqt__naqdj[zixp__giu][i] = sftkj__adqfk[zixp__giu]
        else:
            kwsn__ccgf[i] = True
            for zixp__giu in range(n_cols):
                bodo.libs.array_kernels.setna(oqt__naqdj[zixp__giu], i)
    for i in range(arst__imgpa):
        if kwsn__ccgf[rjj__fglep[i]]:
            bodo.libs.array_kernels.setna(rjj__fglep, i)
    bqso__msxb = [init_dict_arr(oqt__naqdj[i], rjj__fglep.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return bqso__msxb


def create_extractall_methods(is_multi_group):
    bnfqs__ktxr = '_multi' if is_multi_group else ''
    dii__fnjct = f"""def str_extractall{bnfqs__ktxr}(arr, regex, n_cols, index_arr):
    data_arr = arr._data
    indices_arr = arr._indices
    n_data = len(data_arr)
    n_indices = len(indices_arr)
    indices_count = [0 for _ in range(n_data)]
    for i in range(n_indices):
        if not bodo.libs.array_kernels.isna(indices_arr, i):
            indices_count[indices_arr[i]] += 1
    dict_group_count = []
    out_dict_len = out_ind_len = 0
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            continue
        m = regex.findall(data_arr[i])
        dict_group_count.append((out_dict_len, len(m)))
        out_dict_len += len(m)
        out_ind_len += indices_count[i] * len(m)
    out_dict_arr_list = []
    for _ in range(n_cols):
        out_dict_arr_list.append(pre_alloc_string_array(out_dict_len, -1))
    out_indices_arr = bodo.libs.int_arr_ext.alloc_int_array(out_ind_len, np.int32)
    out_ind_arr = bodo.utils.utils.alloc_type(out_ind_len, index_arr, (-1,))
    out_match_arr = np.empty(out_ind_len, np.int64)
    curr_ind = 0
    for i in range(n_data):
        if bodo.libs.array_kernels.isna(data_arr, i):
            continue
        m = regex.findall(data_arr[i])
        for s in m:
            for j in range(n_cols):
                out_dict_arr_list[j][curr_ind] = s{'[j]' if is_multi_group else ''}
            curr_ind += 1
    curr_ind = 0
    for i in range(n_indices):
        if bodo.libs.array_kernels.isna(indices_arr, i):
            continue
        n_rows = dict_group_count[indices_arr[i]][1]
        for k in range(n_rows):
            out_indices_arr[curr_ind] = dict_group_count[indices_arr[i]][0] + k
            out_ind_arr[curr_ind] = index_arr[i]
            out_match_arr[curr_ind] = k
            curr_ind += 1
    out_arr_list = [
        init_dict_arr(
            out_dict_arr_list[i], out_indices_arr.copy(), arr._has_global_dictionary
        )
        for i in range(n_cols)
    ]
    return (out_ind_arr, out_match_arr, out_arr_list) 
"""
    xgkt__nty = {}
    exec(dii__fnjct, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, xgkt__nty)
    return xgkt__nty[f'str_extractall{bnfqs__ktxr}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        bnfqs__ktxr = '_multi' if is_multi_group else ''
        qytk__cuwc = create_extractall_methods(is_multi_group)
        qytk__cuwc = register_jitable(qytk__cuwc)
        globals()[f'str_extractall{bnfqs__ktxr}'] = qytk__cuwc


_register_extractall_methods()
