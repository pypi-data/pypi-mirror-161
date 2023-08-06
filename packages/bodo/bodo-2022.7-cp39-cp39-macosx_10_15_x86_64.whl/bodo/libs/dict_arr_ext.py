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
        ebo__fdrml = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, ebo__fdrml)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        fyeu__mpmfx, fokjb__dix, eub__emjhk = args
        qui__ucq = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        qui__ucq.data = fyeu__mpmfx
        qui__ucq.indices = fokjb__dix
        qui__ucq.has_global_dictionary = eub__emjhk
        context.nrt.incref(builder, signature.args[0], fyeu__mpmfx)
        context.nrt.incref(builder, signature.args[1], fokjb__dix)
        return qui__ucq._getvalue()
    pxqxj__eddd = DictionaryArrayType(data_t)
    dbf__kbi = pxqxj__eddd(data_t, indices_t, types.bool_)
    return dbf__kbi, codegen


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
        rswhn__jrvo = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(rswhn__jrvo, [val])
        c.pyapi.decref(rswhn__jrvo)
    qui__ucq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    fojj__pvehk = c.pyapi.object_getattr_string(val, 'dictionary')
    oevx__rbokq = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    zoou__mbzqc = c.pyapi.call_method(fojj__pvehk, 'to_numpy', (oevx__rbokq,))
    qui__ucq.data = c.unbox(typ.data, zoou__mbzqc).value
    yxqfr__fesdo = c.pyapi.object_getattr_string(val, 'indices')
    eakqe__ynwgd = c.context.insert_const_string(c.builder.module, 'pandas')
    kql__ugoj = c.pyapi.import_module_noblock(eakqe__ynwgd)
    qaq__inlx = c.pyapi.string_from_constant_string('Int32')
    nsg__ncqw = c.pyapi.call_method(kql__ugoj, 'array', (yxqfr__fesdo,
        qaq__inlx))
    qui__ucq.indices = c.unbox(dict_indices_arr_type, nsg__ncqw).value
    qui__ucq.has_global_dictionary = c.context.get_constant(types.bool_, False)
    c.pyapi.decref(fojj__pvehk)
    c.pyapi.decref(oevx__rbokq)
    c.pyapi.decref(zoou__mbzqc)
    c.pyapi.decref(yxqfr__fesdo)
    c.pyapi.decref(kql__ugoj)
    c.pyapi.decref(qaq__inlx)
    c.pyapi.decref(nsg__ncqw)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    qtyws__yrqln = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(qui__ucq._getvalue(), is_error=qtyws__yrqln)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    qui__ucq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, qui__ucq.data)
        mwpsl__oxe = c.box(typ.data, qui__ucq.data)
        xnw__uut = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, qui__ucq.indices)
        ozgjo__hqsgq = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        eqymb__ngt = cgutils.get_or_insert_function(c.builder.module,
            ozgjo__hqsgq, name='box_dict_str_array')
        yampa__xtpcx = cgutils.create_struct_proxy(types.Array(types.int32,
            1, 'C'))(c.context, c.builder, xnw__uut.data)
        lfaff__azngv = c.builder.extract_value(yampa__xtpcx.shape, 0)
        utfc__ckccl = yampa__xtpcx.data
        gvupv__xxze = cgutils.create_struct_proxy(types.Array(types.int8, 1,
            'C'))(c.context, c.builder, xnw__uut.null_bitmap).data
        zoou__mbzqc = c.builder.call(eqymb__ngt, [lfaff__azngv, mwpsl__oxe,
            utfc__ckccl, gvupv__xxze])
        c.pyapi.decref(mwpsl__oxe)
    else:
        eakqe__ynwgd = c.context.insert_const_string(c.builder.module,
            'pyarrow')
        zba__xbww = c.pyapi.import_module_noblock(eakqe__ynwgd)
        umss__kpdds = c.pyapi.object_getattr_string(zba__xbww,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, qui__ucq.data)
        mwpsl__oxe = c.box(typ.data, qui__ucq.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, qui__ucq.indices
            )
        yxqfr__fesdo = c.box(dict_indices_arr_type, qui__ucq.indices)
        agd__ytmsu = c.pyapi.call_method(umss__kpdds, 'from_arrays', (
            yxqfr__fesdo, mwpsl__oxe))
        oevx__rbokq = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        zoou__mbzqc = c.pyapi.call_method(agd__ytmsu, 'to_numpy', (
            oevx__rbokq,))
        c.pyapi.decref(zba__xbww)
        c.pyapi.decref(mwpsl__oxe)
        c.pyapi.decref(yxqfr__fesdo)
        c.pyapi.decref(umss__kpdds)
        c.pyapi.decref(agd__ytmsu)
        c.pyapi.decref(oevx__rbokq)
    c.context.nrt.decref(c.builder, typ, val)
    return zoou__mbzqc


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
    bnx__aknpy = pyval.dictionary.to_numpy(False)
    tndti__egblo = pd.array(pyval.indices, 'Int32')
    bnx__aknpy = context.get_constant_generic(builder, typ.data, bnx__aknpy)
    tndti__egblo = context.get_constant_generic(builder,
        dict_indices_arr_type, tndti__egblo)
    ntbv__swl = context.get_constant(types.bool_, False)
    xyciq__rxauq = lir.Constant.literal_struct([bnx__aknpy, tndti__egblo,
        ntbv__swl])
    return xyciq__rxauq


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            epte__tjp = A._indices[ind]
            return A._data[epte__tjp]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        fyeu__mpmfx = A._data
        fokjb__dix = A._indices
        lfaff__azngv = len(fokjb__dix)
        yvff__bzbft = [get_str_arr_item_length(fyeu__mpmfx, i) for i in
            range(len(fyeu__mpmfx))]
        fgj__kop = 0
        for i in range(lfaff__azngv):
            if not bodo.libs.array_kernels.isna(fokjb__dix, i):
                fgj__kop += yvff__bzbft[fokjb__dix[i]]
        blvkv__kapu = pre_alloc_string_array(lfaff__azngv, fgj__kop)
        for i in range(lfaff__azngv):
            if bodo.libs.array_kernels.isna(fokjb__dix, i):
                bodo.libs.array_kernels.setna(blvkv__kapu, i)
                continue
            ind = fokjb__dix[i]
            if bodo.libs.array_kernels.isna(fyeu__mpmfx, ind):
                bodo.libs.array_kernels.setna(blvkv__kapu, i)
                continue
            blvkv__kapu[i] = fyeu__mpmfx[ind]
        return blvkv__kapu
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    epte__tjp = -1
    fyeu__mpmfx = arr._data
    for i in range(len(fyeu__mpmfx)):
        if bodo.libs.array_kernels.isna(fyeu__mpmfx, i):
            continue
        if fyeu__mpmfx[i] == val:
            epte__tjp = i
            break
    return epte__tjp


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    lfaff__azngv = len(arr)
    epte__tjp = find_dict_ind(arr, val)
    if epte__tjp == -1:
        return init_bool_array(np.full(lfaff__azngv, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == epte__tjp


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    lfaff__azngv = len(arr)
    epte__tjp = find_dict_ind(arr, val)
    if epte__tjp == -1:
        return init_bool_array(np.full(lfaff__azngv, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != epte__tjp


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
        uzu__dvzb = arr._data
        tpbu__ttoq = bodo.libs.int_arr_ext.alloc_int_array(len(uzu__dvzb),
            dtype)
        for jap__hdqt in range(len(uzu__dvzb)):
            if bodo.libs.array_kernels.isna(uzu__dvzb, jap__hdqt):
                bodo.libs.array_kernels.setna(tpbu__ttoq, jap__hdqt)
                continue
            tpbu__ttoq[jap__hdqt] = np.int64(uzu__dvzb[jap__hdqt])
        lfaff__azngv = len(arr)
        fokjb__dix = arr._indices
        blvkv__kapu = bodo.libs.int_arr_ext.alloc_int_array(lfaff__azngv, dtype
            )
        for i in range(lfaff__azngv):
            if bodo.libs.array_kernels.isna(fokjb__dix, i):
                bodo.libs.array_kernels.setna(blvkv__kapu, i)
                continue
            blvkv__kapu[i] = tpbu__ttoq[fokjb__dix[i]]
        return blvkv__kapu
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    nqm__bzokt = len(arrs)
    zxcu__jhb = 'def impl(arrs, sep):\n'
    zxcu__jhb += '  ind_map = {}\n'
    zxcu__jhb += '  out_strs = []\n'
    zxcu__jhb += '  n = len(arrs[0])\n'
    for i in range(nqm__bzokt):
        zxcu__jhb += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(nqm__bzokt):
        zxcu__jhb += f'  data{i} = arrs[{i}]._data\n'
    zxcu__jhb += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    zxcu__jhb += '  for i in range(n):\n'
    wgchp__lqm = ' or '.join([f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for
        i in range(nqm__bzokt)])
    zxcu__jhb += f'    if {wgchp__lqm}:\n'
    zxcu__jhb += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    zxcu__jhb += '      continue\n'
    for i in range(nqm__bzokt):
        zxcu__jhb += f'    ind{i} = indices{i}[i]\n'
    jhvq__vusos = '(' + ', '.join(f'ind{i}' for i in range(nqm__bzokt)) + ')'
    zxcu__jhb += f'    if {jhvq__vusos} not in ind_map:\n'
    zxcu__jhb += '      out_ind = len(out_strs)\n'
    zxcu__jhb += f'      ind_map[{jhvq__vusos}] = out_ind\n'
    dta__khr = "''" if is_overload_none(sep) else 'sep'
    inaio__furl = ', '.join([f'data{i}[ind{i}]' for i in range(nqm__bzokt)])
    zxcu__jhb += f'      v = {dta__khr}.join([{inaio__furl}])\n'
    zxcu__jhb += '      out_strs.append(v)\n'
    zxcu__jhb += '    else:\n'
    zxcu__jhb += f'      out_ind = ind_map[{jhvq__vusos}]\n'
    zxcu__jhb += '    out_indices[i] = out_ind\n'
    zxcu__jhb += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    zxcu__jhb += (
        '  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)\n'
        )
    qqcht__asiqg = {}
    exec(zxcu__jhb, {'bodo': bodo, 'numba': numba, 'np': np}, qqcht__asiqg)
    impl = qqcht__asiqg['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    kolkd__nzv = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    dbf__kbi = toty(fromty)
    gghpt__mqdfi = context.compile_internal(builder, kolkd__nzv, dbf__kbi,
        (val,))
    return impl_ret_new_ref(context, builder, toty, gghpt__mqdfi)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    bnx__aknpy = arr._data
    cydbf__brg = len(bnx__aknpy)
    jhak__itl = pre_alloc_string_array(cydbf__brg, -1)
    if regex:
        hhm__huyk = re.compile(pat, flags)
        for i in range(cydbf__brg):
            if bodo.libs.array_kernels.isna(bnx__aknpy, i):
                bodo.libs.array_kernels.setna(jhak__itl, i)
                continue
            jhak__itl[i] = hhm__huyk.sub(repl=repl, string=bnx__aknpy[i])
    else:
        for i in range(cydbf__brg):
            if bodo.libs.array_kernels.isna(bnx__aknpy, i):
                bodo.libs.array_kernels.setna(jhak__itl, i)
                continue
            jhak__itl[i] = bnx__aknpy[i].replace(pat, repl)
    return init_dict_arr(jhak__itl, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    qui__ucq = arr._data
    ywpo__oltm = len(qui__ucq)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(ywpo__oltm)
    for i in range(ywpo__oltm):
        dict_arr_out[i] = qui__ucq[i].startswith(pat)
    tndti__egblo = arr._indices
    frp__ixoz = len(tndti__egblo)
    blvkv__kapu = bodo.libs.bool_arr_ext.alloc_bool_array(frp__ixoz)
    for i in range(frp__ixoz):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(blvkv__kapu, i)
        else:
            blvkv__kapu[i] = dict_arr_out[tndti__egblo[i]]
    return blvkv__kapu


@register_jitable
def str_endswith(arr, pat, na):
    qui__ucq = arr._data
    ywpo__oltm = len(qui__ucq)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(ywpo__oltm)
    for i in range(ywpo__oltm):
        dict_arr_out[i] = qui__ucq[i].endswith(pat)
    tndti__egblo = arr._indices
    frp__ixoz = len(tndti__egblo)
    blvkv__kapu = bodo.libs.bool_arr_ext.alloc_bool_array(frp__ixoz)
    for i in range(frp__ixoz):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(blvkv__kapu, i)
        else:
            blvkv__kapu[i] = dict_arr_out[tndti__egblo[i]]
    return blvkv__kapu


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    qui__ucq = arr._data
    cct__twkzp = pd.Series(qui__ucq)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = cct__twkzp.array._str_contains(pat, case, flags, na,
            regex)
    tndti__egblo = arr._indices
    frp__ixoz = len(tndti__egblo)
    blvkv__kapu = bodo.libs.bool_arr_ext.alloc_bool_array(frp__ixoz)
    for i in range(frp__ixoz):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(blvkv__kapu, i)
        else:
            blvkv__kapu[i] = dict_arr_out[tndti__egblo[i]]
    return blvkv__kapu


@register_jitable
def str_contains_non_regex(arr, pat, case):
    qui__ucq = arr._data
    ywpo__oltm = len(qui__ucq)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(ywpo__oltm)
    if not case:
        nhfgr__wntg = pat.upper()
    for i in range(ywpo__oltm):
        if case:
            dict_arr_out[i] = pat in qui__ucq[i]
        else:
            dict_arr_out[i] = nhfgr__wntg in qui__ucq[i].upper()
    tndti__egblo = arr._indices
    frp__ixoz = len(tndti__egblo)
    blvkv__kapu = bodo.libs.bool_arr_ext.alloc_bool_array(frp__ixoz)
    for i in range(frp__ixoz):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(blvkv__kapu, i)
        else:
            blvkv__kapu[i] = dict_arr_out[tndti__egblo[i]]
    return blvkv__kapu


@numba.njit
def str_match(arr, pat, case, flags, na):
    qui__ucq = arr._data
    tndti__egblo = arr._indices
    frp__ixoz = len(tndti__egblo)
    blvkv__kapu = bodo.libs.bool_arr_ext.alloc_bool_array(frp__ixoz)
    cct__twkzp = pd.Series(qui__ucq)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = cct__twkzp.array._str_match(pat, case, flags, na)
    for i in range(frp__ixoz):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(blvkv__kapu, i)
        else:
            blvkv__kapu[i] = dict_arr_out[tndti__egblo[i]]
    return blvkv__kapu


def create_simple_str2str_methods(func_name, func_args):
    zxcu__jhb = f"""def str_{func_name}({', '.join(func_args)}):
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
    qqcht__asiqg = {}
    exec(zxcu__jhb, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, qqcht__asiqg)
    return qqcht__asiqg[f'str_{func_name}']


def _register_simple_str2str_methods():
    qqp__rea = {**dict.fromkeys(['capitalize', 'lower', 'swapcase', 'title',
        'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip', 'strip'],
        ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust', 'rjust'],
        ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'], ('arr',
        'width'))}
    for func_name in qqp__rea.keys():
        knj__bbtzd = create_simple_str2str_methods(func_name, qqp__rea[
            func_name])
        knj__bbtzd = register_jitable(knj__bbtzd)
        globals()[f'str_{func_name}'] = knj__bbtzd


_register_simple_str2str_methods()


def create_find_methods(func_name):
    zxcu__jhb = f"""def str_{func_name}(arr, sub, start, end):
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
    qqcht__asiqg = {}
    exec(zxcu__jhb, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, qqcht__asiqg)
    return qqcht__asiqg[f'str_{func_name}']


def _register_find_methods():
    nsxkr__hkgy = ['find', 'rfind']
    for func_name in nsxkr__hkgy:
        knj__bbtzd = create_find_methods(func_name)
        knj__bbtzd = register_jitable(knj__bbtzd)
        globals()[f'str_{func_name}'] = knj__bbtzd


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    bnx__aknpy = arr._data
    tndti__egblo = arr._indices
    cydbf__brg = len(bnx__aknpy)
    frp__ixoz = len(tndti__egblo)
    nooy__knual = bodo.libs.int_arr_ext.alloc_int_array(cydbf__brg, np.int64)
    yau__awy = bodo.libs.int_arr_ext.alloc_int_array(frp__ixoz, np.int64)
    regex = re.compile(pat, flags)
    for i in range(cydbf__brg):
        if bodo.libs.array_kernels.isna(bnx__aknpy, i):
            bodo.libs.array_kernels.setna(nooy__knual, i)
            continue
        nooy__knual[i] = bodo.libs.str_ext.str_findall_count(regex,
            bnx__aknpy[i])
    for i in range(frp__ixoz):
        if bodo.libs.array_kernels.isna(tndti__egblo, i
            ) or bodo.libs.array_kernels.isna(nooy__knual, tndti__egblo[i]):
            bodo.libs.array_kernels.setna(yau__awy, i)
        else:
            yau__awy[i] = nooy__knual[tndti__egblo[i]]
    return yau__awy


@register_jitable
def str_len(arr):
    bnx__aknpy = arr._data
    tndti__egblo = arr._indices
    frp__ixoz = len(tndti__egblo)
    nooy__knual = bodo.libs.array_kernels.get_arr_lens(bnx__aknpy, False)
    yau__awy = bodo.libs.int_arr_ext.alloc_int_array(frp__ixoz, np.int64)
    for i in range(frp__ixoz):
        if bodo.libs.array_kernels.isna(tndti__egblo, i
            ) or bodo.libs.array_kernels.isna(nooy__knual, tndti__egblo[i]):
            bodo.libs.array_kernels.setna(yau__awy, i)
        else:
            yau__awy[i] = nooy__knual[tndti__egblo[i]]
    return yau__awy


@register_jitable
def str_slice(arr, start, stop, step):
    bnx__aknpy = arr._data
    cydbf__brg = len(bnx__aknpy)
    jhak__itl = bodo.libs.str_arr_ext.pre_alloc_string_array(cydbf__brg, -1)
    for i in range(cydbf__brg):
        if bodo.libs.array_kernels.isna(bnx__aknpy, i):
            bodo.libs.array_kernels.setna(jhak__itl, i)
            continue
        jhak__itl[i] = bnx__aknpy[i][start:stop:step]
    return init_dict_arr(jhak__itl, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    bnx__aknpy = arr._data
    tndti__egblo = arr._indices
    cydbf__brg = len(bnx__aknpy)
    frp__ixoz = len(tndti__egblo)
    jhak__itl = pre_alloc_string_array(cydbf__brg, -1)
    blvkv__kapu = pre_alloc_string_array(frp__ixoz, -1)
    for jap__hdqt in range(cydbf__brg):
        if bodo.libs.array_kernels.isna(bnx__aknpy, jap__hdqt) or not -len(
            bnx__aknpy[jap__hdqt]) <= i < len(bnx__aknpy[jap__hdqt]):
            bodo.libs.array_kernels.setna(jhak__itl, jap__hdqt)
            continue
        jhak__itl[jap__hdqt] = bnx__aknpy[jap__hdqt][i]
    for jap__hdqt in range(frp__ixoz):
        if bodo.libs.array_kernels.isna(tndti__egblo, jap__hdqt
            ) or bodo.libs.array_kernels.isna(jhak__itl, tndti__egblo[
            jap__hdqt]):
            bodo.libs.array_kernels.setna(blvkv__kapu, jap__hdqt)
            continue
        blvkv__kapu[jap__hdqt] = jhak__itl[tndti__egblo[jap__hdqt]]
    return blvkv__kapu


@register_jitable
def str_repeat_int(arr, repeats):
    bnx__aknpy = arr._data
    cydbf__brg = len(bnx__aknpy)
    jhak__itl = pre_alloc_string_array(cydbf__brg, -1)
    for i in range(cydbf__brg):
        if bodo.libs.array_kernels.isna(bnx__aknpy, i):
            bodo.libs.array_kernels.setna(jhak__itl, i)
            continue
        jhak__itl[i] = bnx__aknpy[i] * repeats
    return init_dict_arr(jhak__itl, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    zxcu__jhb = f"""def str_{func_name}(arr):
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
    qqcht__asiqg = {}
    exec(zxcu__jhb, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, qqcht__asiqg)
    return qqcht__asiqg[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        knj__bbtzd = create_str2bool_methods(func_name)
        knj__bbtzd = register_jitable(knj__bbtzd)
        globals()[f'str_{func_name}'] = knj__bbtzd


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    bnx__aknpy = arr._data
    tndti__egblo = arr._indices
    cydbf__brg = len(bnx__aknpy)
    frp__ixoz = len(tndti__egblo)
    regex = re.compile(pat, flags=flags)
    glgom__doat = []
    for ntbz__ctec in range(n_cols):
        glgom__doat.append(pre_alloc_string_array(cydbf__brg, -1))
    ohtqv__orrs = bodo.libs.bool_arr_ext.alloc_bool_array(cydbf__brg)
    dvpmh__ednsl = tndti__egblo.copy()
    for i in range(cydbf__brg):
        if bodo.libs.array_kernels.isna(bnx__aknpy, i):
            ohtqv__orrs[i] = True
            for jap__hdqt in range(n_cols):
                bodo.libs.array_kernels.setna(glgom__doat[jap__hdqt], i)
            continue
        ltld__bhja = regex.search(bnx__aknpy[i])
        if ltld__bhja:
            ohtqv__orrs[i] = False
            bucq__bepw = ltld__bhja.groups()
            for jap__hdqt in range(n_cols):
                glgom__doat[jap__hdqt][i] = bucq__bepw[jap__hdqt]
        else:
            ohtqv__orrs[i] = True
            for jap__hdqt in range(n_cols):
                bodo.libs.array_kernels.setna(glgom__doat[jap__hdqt], i)
    for i in range(frp__ixoz):
        if ohtqv__orrs[dvpmh__ednsl[i]]:
            bodo.libs.array_kernels.setna(dvpmh__ednsl, i)
    mpj__auctx = [init_dict_arr(glgom__doat[i], dvpmh__ednsl.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return mpj__auctx


def create_extractall_methods(is_multi_group):
    ueu__pseww = '_multi' if is_multi_group else ''
    zxcu__jhb = f"""def str_extractall{ueu__pseww}(arr, regex, n_cols, index_arr):
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
    qqcht__asiqg = {}
    exec(zxcu__jhb, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, qqcht__asiqg)
    return qqcht__asiqg[f'str_extractall{ueu__pseww}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        ueu__pseww = '_multi' if is_multi_group else ''
        knj__bbtzd = create_extractall_methods(is_multi_group)
        knj__bbtzd = register_jitable(knj__bbtzd)
        globals()[f'str_extractall{ueu__pseww}'] = knj__bbtzd


_register_extractall_methods()
