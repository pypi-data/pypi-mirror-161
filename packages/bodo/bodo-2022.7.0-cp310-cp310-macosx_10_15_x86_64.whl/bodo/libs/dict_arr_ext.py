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
        nhn__orh = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, nhn__orh)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        byuha__bsys, qqdks__ogpt, zuudm__yumq = args
        xvj__fhih = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        xvj__fhih.data = byuha__bsys
        xvj__fhih.indices = qqdks__ogpt
        xvj__fhih.has_global_dictionary = zuudm__yumq
        context.nrt.incref(builder, signature.args[0], byuha__bsys)
        context.nrt.incref(builder, signature.args[1], qqdks__ogpt)
        return xvj__fhih._getvalue()
    qli__mxhm = DictionaryArrayType(data_t)
    gdzt__syq = qli__mxhm(data_t, indices_t, types.bool_)
    return gdzt__syq, codegen


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
        oxxom__hjlfv = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(oxxom__hjlfv, [val])
        c.pyapi.decref(oxxom__hjlfv)
    xvj__fhih = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    nqc__owrsp = c.pyapi.object_getattr_string(val, 'dictionary')
    doi__amvv = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_, 
        False))
    qezyo__kma = c.pyapi.call_method(nqc__owrsp, 'to_numpy', (doi__amvv,))
    xvj__fhih.data = c.unbox(typ.data, qezyo__kma).value
    jkqn__cylzd = c.pyapi.object_getattr_string(val, 'indices')
    wrc__ijch = c.context.insert_const_string(c.builder.module, 'pandas')
    dndyw__lrmmh = c.pyapi.import_module_noblock(wrc__ijch)
    fffqa__asve = c.pyapi.string_from_constant_string('Int32')
    xvki__iixk = c.pyapi.call_method(dndyw__lrmmh, 'array', (jkqn__cylzd,
        fffqa__asve))
    xvj__fhih.indices = c.unbox(dict_indices_arr_type, xvki__iixk).value
    xvj__fhih.has_global_dictionary = c.context.get_constant(types.bool_, False
        )
    c.pyapi.decref(nqc__owrsp)
    c.pyapi.decref(doi__amvv)
    c.pyapi.decref(qezyo__kma)
    c.pyapi.decref(jkqn__cylzd)
    c.pyapi.decref(dndyw__lrmmh)
    c.pyapi.decref(fffqa__asve)
    c.pyapi.decref(xvki__iixk)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    itodr__srqxk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xvj__fhih._getvalue(), is_error=itodr__srqxk)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    xvj__fhih = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, xvj__fhih.data)
        cewhl__giv = c.box(typ.data, xvj__fhih.data)
        ehuil__vuv = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, xvj__fhih.indices)
        duu__gjht = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        vsxp__dmlg = cgutils.get_or_insert_function(c.builder.module,
            duu__gjht, name='box_dict_str_array')
        abqk__amg = cgutils.create_struct_proxy(types.Array(types.int32, 1,
            'C'))(c.context, c.builder, ehuil__vuv.data)
        tgwgd__srde = c.builder.extract_value(abqk__amg.shape, 0)
        qcg__wyo = abqk__amg.data
        kbg__xtp = cgutils.create_struct_proxy(types.Array(types.int8, 1, 'C')
            )(c.context, c.builder, ehuil__vuv.null_bitmap).data
        qezyo__kma = c.builder.call(vsxp__dmlg, [tgwgd__srde, cewhl__giv,
            qcg__wyo, kbg__xtp])
        c.pyapi.decref(cewhl__giv)
    else:
        wrc__ijch = c.context.insert_const_string(c.builder.module, 'pyarrow')
        hpibn__uoinh = c.pyapi.import_module_noblock(wrc__ijch)
        pwy__gve = c.pyapi.object_getattr_string(hpibn__uoinh,
            'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, xvj__fhih.data)
        cewhl__giv = c.box(typ.data, xvj__fhih.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, xvj__fhih.
            indices)
        jkqn__cylzd = c.box(dict_indices_arr_type, xvj__fhih.indices)
        zgi__iauim = c.pyapi.call_method(pwy__gve, 'from_arrays', (
            jkqn__cylzd, cewhl__giv))
        doi__amvv = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        qezyo__kma = c.pyapi.call_method(zgi__iauim, 'to_numpy', (doi__amvv,))
        c.pyapi.decref(hpibn__uoinh)
        c.pyapi.decref(cewhl__giv)
        c.pyapi.decref(jkqn__cylzd)
        c.pyapi.decref(pwy__gve)
        c.pyapi.decref(zgi__iauim)
        c.pyapi.decref(doi__amvv)
    c.context.nrt.decref(c.builder, typ, val)
    return qezyo__kma


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
    hdmxo__bim = pyval.dictionary.to_numpy(False)
    wmgic__kfm = pd.array(pyval.indices, 'Int32')
    hdmxo__bim = context.get_constant_generic(builder, typ.data, hdmxo__bim)
    wmgic__kfm = context.get_constant_generic(builder,
        dict_indices_arr_type, wmgic__kfm)
    wvh__pjjii = context.get_constant(types.bool_, False)
    pxvs__ojspw = lir.Constant.literal_struct([hdmxo__bim, wmgic__kfm,
        wvh__pjjii])
    return pxvs__ojspw


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            hpovl__umf = A._indices[ind]
            return A._data[hpovl__umf]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        byuha__bsys = A._data
        qqdks__ogpt = A._indices
        tgwgd__srde = len(qqdks__ogpt)
        lklwn__synvm = [get_str_arr_item_length(byuha__bsys, i) for i in
            range(len(byuha__bsys))]
        zjb__tbtm = 0
        for i in range(tgwgd__srde):
            if not bodo.libs.array_kernels.isna(qqdks__ogpt, i):
                zjb__tbtm += lklwn__synvm[qqdks__ogpt[i]]
        evxft__cbob = pre_alloc_string_array(tgwgd__srde, zjb__tbtm)
        for i in range(tgwgd__srde):
            if bodo.libs.array_kernels.isna(qqdks__ogpt, i):
                bodo.libs.array_kernels.setna(evxft__cbob, i)
                continue
            ind = qqdks__ogpt[i]
            if bodo.libs.array_kernels.isna(byuha__bsys, ind):
                bodo.libs.array_kernels.setna(evxft__cbob, i)
                continue
            evxft__cbob[i] = byuha__bsys[ind]
        return evxft__cbob
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    hpovl__umf = -1
    byuha__bsys = arr._data
    for i in range(len(byuha__bsys)):
        if bodo.libs.array_kernels.isna(byuha__bsys, i):
            continue
        if byuha__bsys[i] == val:
            hpovl__umf = i
            break
    return hpovl__umf


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    tgwgd__srde = len(arr)
    hpovl__umf = find_dict_ind(arr, val)
    if hpovl__umf == -1:
        return init_bool_array(np.full(tgwgd__srde, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == hpovl__umf


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    tgwgd__srde = len(arr)
    hpovl__umf = find_dict_ind(arr, val)
    if hpovl__umf == -1:
        return init_bool_array(np.full(tgwgd__srde, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != hpovl__umf


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
        zsxfo__lbplk = arr._data
        nuf__fwnnp = bodo.libs.int_arr_ext.alloc_int_array(len(zsxfo__lbplk
            ), dtype)
        for yomb__nks in range(len(zsxfo__lbplk)):
            if bodo.libs.array_kernels.isna(zsxfo__lbplk, yomb__nks):
                bodo.libs.array_kernels.setna(nuf__fwnnp, yomb__nks)
                continue
            nuf__fwnnp[yomb__nks] = np.int64(zsxfo__lbplk[yomb__nks])
        tgwgd__srde = len(arr)
        qqdks__ogpt = arr._indices
        evxft__cbob = bodo.libs.int_arr_ext.alloc_int_array(tgwgd__srde, dtype)
        for i in range(tgwgd__srde):
            if bodo.libs.array_kernels.isna(qqdks__ogpt, i):
                bodo.libs.array_kernels.setna(evxft__cbob, i)
                continue
            evxft__cbob[i] = nuf__fwnnp[qqdks__ogpt[i]]
        return evxft__cbob
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    lffq__alacj = len(arrs)
    dsegd__uci = 'def impl(arrs, sep):\n'
    dsegd__uci += '  ind_map = {}\n'
    dsegd__uci += '  out_strs = []\n'
    dsegd__uci += '  n = len(arrs[0])\n'
    for i in range(lffq__alacj):
        dsegd__uci += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(lffq__alacj):
        dsegd__uci += f'  data{i} = arrs[{i}]._data\n'
    dsegd__uci += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    dsegd__uci += '  for i in range(n):\n'
    mmtjb__emcwd = ' or '.join([
        f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for i in range(
        lffq__alacj)])
    dsegd__uci += f'    if {mmtjb__emcwd}:\n'
    dsegd__uci += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    dsegd__uci += '      continue\n'
    for i in range(lffq__alacj):
        dsegd__uci += f'    ind{i} = indices{i}[i]\n'
    vfx__zyhb = '(' + ', '.join(f'ind{i}' for i in range(lffq__alacj)) + ')'
    dsegd__uci += f'    if {vfx__zyhb} not in ind_map:\n'
    dsegd__uci += '      out_ind = len(out_strs)\n'
    dsegd__uci += f'      ind_map[{vfx__zyhb}] = out_ind\n'
    ppm__ikl = "''" if is_overload_none(sep) else 'sep'
    dqszi__xfcs = ', '.join([f'data{i}[ind{i}]' for i in range(lffq__alacj)])
    dsegd__uci += f'      v = {ppm__ikl}.join([{dqszi__xfcs}])\n'
    dsegd__uci += '      out_strs.append(v)\n'
    dsegd__uci += '    else:\n'
    dsegd__uci += f'      out_ind = ind_map[{vfx__zyhb}]\n'
    dsegd__uci += '    out_indices[i] = out_ind\n'
    dsegd__uci += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    dsegd__uci += """  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)
"""
    blia__azhgw = {}
    exec(dsegd__uci, {'bodo': bodo, 'numba': numba, 'np': np}, blia__azhgw)
    impl = blia__azhgw['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    nsj__bpqb = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    gdzt__syq = toty(fromty)
    lttu__smv = context.compile_internal(builder, nsj__bpqb, gdzt__syq, (val,))
    return impl_ret_new_ref(context, builder, toty, lttu__smv)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    hdmxo__bim = arr._data
    yyr__bqw = len(hdmxo__bim)
    otwq__wrl = pre_alloc_string_array(yyr__bqw, -1)
    if regex:
        wvrao__wrjfj = re.compile(pat, flags)
        for i in range(yyr__bqw):
            if bodo.libs.array_kernels.isna(hdmxo__bim, i):
                bodo.libs.array_kernels.setna(otwq__wrl, i)
                continue
            otwq__wrl[i] = wvrao__wrjfj.sub(repl=repl, string=hdmxo__bim[i])
    else:
        for i in range(yyr__bqw):
            if bodo.libs.array_kernels.isna(hdmxo__bim, i):
                bodo.libs.array_kernels.setna(otwq__wrl, i)
                continue
            otwq__wrl[i] = hdmxo__bim[i].replace(pat, repl)
    return init_dict_arr(otwq__wrl, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    xvj__fhih = arr._data
    sij__zmct = len(xvj__fhih)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(sij__zmct)
    for i in range(sij__zmct):
        dict_arr_out[i] = xvj__fhih[i].startswith(pat)
    wmgic__kfm = arr._indices
    iyokx__wyxv = len(wmgic__kfm)
    evxft__cbob = bodo.libs.bool_arr_ext.alloc_bool_array(iyokx__wyxv)
    for i in range(iyokx__wyxv):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(evxft__cbob, i)
        else:
            evxft__cbob[i] = dict_arr_out[wmgic__kfm[i]]
    return evxft__cbob


@register_jitable
def str_endswith(arr, pat, na):
    xvj__fhih = arr._data
    sij__zmct = len(xvj__fhih)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(sij__zmct)
    for i in range(sij__zmct):
        dict_arr_out[i] = xvj__fhih[i].endswith(pat)
    wmgic__kfm = arr._indices
    iyokx__wyxv = len(wmgic__kfm)
    evxft__cbob = bodo.libs.bool_arr_ext.alloc_bool_array(iyokx__wyxv)
    for i in range(iyokx__wyxv):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(evxft__cbob, i)
        else:
            evxft__cbob[i] = dict_arr_out[wmgic__kfm[i]]
    return evxft__cbob


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    xvj__fhih = arr._data
    xfd__xzl = pd.Series(xvj__fhih)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = xfd__xzl.array._str_contains(pat, case, flags, na, regex
            )
    wmgic__kfm = arr._indices
    iyokx__wyxv = len(wmgic__kfm)
    evxft__cbob = bodo.libs.bool_arr_ext.alloc_bool_array(iyokx__wyxv)
    for i in range(iyokx__wyxv):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(evxft__cbob, i)
        else:
            evxft__cbob[i] = dict_arr_out[wmgic__kfm[i]]
    return evxft__cbob


@register_jitable
def str_contains_non_regex(arr, pat, case):
    xvj__fhih = arr._data
    sij__zmct = len(xvj__fhih)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(sij__zmct)
    if not case:
        nxt__vdw = pat.upper()
    for i in range(sij__zmct):
        if case:
            dict_arr_out[i] = pat in xvj__fhih[i]
        else:
            dict_arr_out[i] = nxt__vdw in xvj__fhih[i].upper()
    wmgic__kfm = arr._indices
    iyokx__wyxv = len(wmgic__kfm)
    evxft__cbob = bodo.libs.bool_arr_ext.alloc_bool_array(iyokx__wyxv)
    for i in range(iyokx__wyxv):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(evxft__cbob, i)
        else:
            evxft__cbob[i] = dict_arr_out[wmgic__kfm[i]]
    return evxft__cbob


@numba.njit
def str_match(arr, pat, case, flags, na):
    xvj__fhih = arr._data
    wmgic__kfm = arr._indices
    iyokx__wyxv = len(wmgic__kfm)
    evxft__cbob = bodo.libs.bool_arr_ext.alloc_bool_array(iyokx__wyxv)
    xfd__xzl = pd.Series(xvj__fhih)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = xfd__xzl.array._str_match(pat, case, flags, na)
    for i in range(iyokx__wyxv):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(evxft__cbob, i)
        else:
            evxft__cbob[i] = dict_arr_out[wmgic__kfm[i]]
    return evxft__cbob


def create_simple_str2str_methods(func_name, func_args):
    dsegd__uci = f"""def str_{func_name}({', '.join(func_args)}):
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
    blia__azhgw = {}
    exec(dsegd__uci, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, blia__azhgw)
    return blia__azhgw[f'str_{func_name}']


def _register_simple_str2str_methods():
    caru__roub = {**dict.fromkeys(['capitalize', 'lower', 'swapcase',
        'title', 'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip',
        'strip'], ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust',
        'rjust'], ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'],
        ('arr', 'width'))}
    for func_name in caru__roub.keys():
        uyqj__qtcoy = create_simple_str2str_methods(func_name, caru__roub[
            func_name])
        uyqj__qtcoy = register_jitable(uyqj__qtcoy)
        globals()[f'str_{func_name}'] = uyqj__qtcoy


_register_simple_str2str_methods()


def create_find_methods(func_name):
    dsegd__uci = f"""def str_{func_name}(arr, sub, start, end):
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
    blia__azhgw = {}
    exec(dsegd__uci, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, blia__azhgw)
    return blia__azhgw[f'str_{func_name}']


def _register_find_methods():
    bpnf__wxgdk = ['find', 'rfind']
    for func_name in bpnf__wxgdk:
        uyqj__qtcoy = create_find_methods(func_name)
        uyqj__qtcoy = register_jitable(uyqj__qtcoy)
        globals()[f'str_{func_name}'] = uyqj__qtcoy


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    hdmxo__bim = arr._data
    wmgic__kfm = arr._indices
    yyr__bqw = len(hdmxo__bim)
    iyokx__wyxv = len(wmgic__kfm)
    ltcn__wcihn = bodo.libs.int_arr_ext.alloc_int_array(yyr__bqw, np.int64)
    qhweq__yhmhk = bodo.libs.int_arr_ext.alloc_int_array(iyokx__wyxv, np.int64)
    regex = re.compile(pat, flags)
    for i in range(yyr__bqw):
        if bodo.libs.array_kernels.isna(hdmxo__bim, i):
            bodo.libs.array_kernels.setna(ltcn__wcihn, i)
            continue
        ltcn__wcihn[i] = bodo.libs.str_ext.str_findall_count(regex,
            hdmxo__bim[i])
    for i in range(iyokx__wyxv):
        if bodo.libs.array_kernels.isna(wmgic__kfm, i
            ) or bodo.libs.array_kernels.isna(ltcn__wcihn, wmgic__kfm[i]):
            bodo.libs.array_kernels.setna(qhweq__yhmhk, i)
        else:
            qhweq__yhmhk[i] = ltcn__wcihn[wmgic__kfm[i]]
    return qhweq__yhmhk


@register_jitable
def str_len(arr):
    hdmxo__bim = arr._data
    wmgic__kfm = arr._indices
    iyokx__wyxv = len(wmgic__kfm)
    ltcn__wcihn = bodo.libs.array_kernels.get_arr_lens(hdmxo__bim, False)
    qhweq__yhmhk = bodo.libs.int_arr_ext.alloc_int_array(iyokx__wyxv, np.int64)
    for i in range(iyokx__wyxv):
        if bodo.libs.array_kernels.isna(wmgic__kfm, i
            ) or bodo.libs.array_kernels.isna(ltcn__wcihn, wmgic__kfm[i]):
            bodo.libs.array_kernels.setna(qhweq__yhmhk, i)
        else:
            qhweq__yhmhk[i] = ltcn__wcihn[wmgic__kfm[i]]
    return qhweq__yhmhk


@register_jitable
def str_slice(arr, start, stop, step):
    hdmxo__bim = arr._data
    yyr__bqw = len(hdmxo__bim)
    otwq__wrl = bodo.libs.str_arr_ext.pre_alloc_string_array(yyr__bqw, -1)
    for i in range(yyr__bqw):
        if bodo.libs.array_kernels.isna(hdmxo__bim, i):
            bodo.libs.array_kernels.setna(otwq__wrl, i)
            continue
        otwq__wrl[i] = hdmxo__bim[i][start:stop:step]
    return init_dict_arr(otwq__wrl, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    hdmxo__bim = arr._data
    wmgic__kfm = arr._indices
    yyr__bqw = len(hdmxo__bim)
    iyokx__wyxv = len(wmgic__kfm)
    otwq__wrl = pre_alloc_string_array(yyr__bqw, -1)
    evxft__cbob = pre_alloc_string_array(iyokx__wyxv, -1)
    for yomb__nks in range(yyr__bqw):
        if bodo.libs.array_kernels.isna(hdmxo__bim, yomb__nks) or not -len(
            hdmxo__bim[yomb__nks]) <= i < len(hdmxo__bim[yomb__nks]):
            bodo.libs.array_kernels.setna(otwq__wrl, yomb__nks)
            continue
        otwq__wrl[yomb__nks] = hdmxo__bim[yomb__nks][i]
    for yomb__nks in range(iyokx__wyxv):
        if bodo.libs.array_kernels.isna(wmgic__kfm, yomb__nks
            ) or bodo.libs.array_kernels.isna(otwq__wrl, wmgic__kfm[yomb__nks]
            ):
            bodo.libs.array_kernels.setna(evxft__cbob, yomb__nks)
            continue
        evxft__cbob[yomb__nks] = otwq__wrl[wmgic__kfm[yomb__nks]]
    return evxft__cbob


@register_jitable
def str_repeat_int(arr, repeats):
    hdmxo__bim = arr._data
    yyr__bqw = len(hdmxo__bim)
    otwq__wrl = pre_alloc_string_array(yyr__bqw, -1)
    for i in range(yyr__bqw):
        if bodo.libs.array_kernels.isna(hdmxo__bim, i):
            bodo.libs.array_kernels.setna(otwq__wrl, i)
            continue
        otwq__wrl[i] = hdmxo__bim[i] * repeats
    return init_dict_arr(otwq__wrl, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    dsegd__uci = f"""def str_{func_name}(arr):
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
    blia__azhgw = {}
    exec(dsegd__uci, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, blia__azhgw)
    return blia__azhgw[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        uyqj__qtcoy = create_str2bool_methods(func_name)
        uyqj__qtcoy = register_jitable(uyqj__qtcoy)
        globals()[f'str_{func_name}'] = uyqj__qtcoy


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    hdmxo__bim = arr._data
    wmgic__kfm = arr._indices
    yyr__bqw = len(hdmxo__bim)
    iyokx__wyxv = len(wmgic__kfm)
    regex = re.compile(pat, flags=flags)
    ejpxt__dhwgt = []
    for nmffh__hpkn in range(n_cols):
        ejpxt__dhwgt.append(pre_alloc_string_array(yyr__bqw, -1))
    lyk__bfwl = bodo.libs.bool_arr_ext.alloc_bool_array(yyr__bqw)
    ugri__tthmb = wmgic__kfm.copy()
    for i in range(yyr__bqw):
        if bodo.libs.array_kernels.isna(hdmxo__bim, i):
            lyk__bfwl[i] = True
            for yomb__nks in range(n_cols):
                bodo.libs.array_kernels.setna(ejpxt__dhwgt[yomb__nks], i)
            continue
        yhc__bnde = regex.search(hdmxo__bim[i])
        if yhc__bnde:
            lyk__bfwl[i] = False
            cgv__rpsyh = yhc__bnde.groups()
            for yomb__nks in range(n_cols):
                ejpxt__dhwgt[yomb__nks][i] = cgv__rpsyh[yomb__nks]
        else:
            lyk__bfwl[i] = True
            for yomb__nks in range(n_cols):
                bodo.libs.array_kernels.setna(ejpxt__dhwgt[yomb__nks], i)
    for i in range(iyokx__wyxv):
        if lyk__bfwl[ugri__tthmb[i]]:
            bodo.libs.array_kernels.setna(ugri__tthmb, i)
    fvsda__tcruq = [init_dict_arr(ejpxt__dhwgt[i], ugri__tthmb.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return fvsda__tcruq


def create_extractall_methods(is_multi_group):
    hybnc__jae = '_multi' if is_multi_group else ''
    dsegd__uci = f"""def str_extractall{hybnc__jae}(arr, regex, n_cols, index_arr):
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
    blia__azhgw = {}
    exec(dsegd__uci, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, blia__azhgw)
    return blia__azhgw[f'str_extractall{hybnc__jae}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        hybnc__jae = '_multi' if is_multi_group else ''
        uyqj__qtcoy = create_extractall_methods(is_multi_group)
        uyqj__qtcoy = register_jitable(uyqj__qtcoy)
        globals()[f'str_extractall{hybnc__jae}'] = uyqj__qtcoy


_register_extractall_methods()
