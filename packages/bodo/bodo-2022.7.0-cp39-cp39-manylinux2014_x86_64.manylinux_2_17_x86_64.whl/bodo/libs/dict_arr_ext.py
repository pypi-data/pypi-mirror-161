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
        kxpe__yawb = [('data', fe_type.data), ('indices',
            dict_indices_arr_type), ('has_global_dictionary', types.bool_)]
        models.StructModel.__init__(self, dmm, fe_type, kxpe__yawb)


make_attribute_wrapper(DictionaryArrayType, 'data', '_data')
make_attribute_wrapper(DictionaryArrayType, 'indices', '_indices')
make_attribute_wrapper(DictionaryArrayType, 'has_global_dictionary',
    '_has_global_dictionary')
lower_builtin('getiter', dict_str_arr_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_dict_arr(typingctx, data_t, indices_t, glob_dict_t=None):
    assert indices_t == dict_indices_arr_type, 'invalid indices type for dict array'

    def codegen(context, builder, signature, args):
        rekr__frkjs, fygyu__zfckq, cdp__xjrr = args
        vdtz__lny = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        vdtz__lny.data = rekr__frkjs
        vdtz__lny.indices = fygyu__zfckq
        vdtz__lny.has_global_dictionary = cdp__xjrr
        context.nrt.incref(builder, signature.args[0], rekr__frkjs)
        context.nrt.incref(builder, signature.args[1], fygyu__zfckq)
        return vdtz__lny._getvalue()
    tyvw__awos = DictionaryArrayType(data_t)
    zpj__ppln = tyvw__awos(data_t, indices_t, types.bool_)
    return zpj__ppln, codegen


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
        ejxlj__wrsw = c.pyapi.unserialize(c.pyapi.serialize_object(
            to_pa_dict_arr))
        val = c.pyapi.call_function_objargs(ejxlj__wrsw, [val])
        c.pyapi.decref(ejxlj__wrsw)
    vdtz__lny = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pmwtb__dwx = c.pyapi.object_getattr_string(val, 'dictionary')
    fkvv__dwgqy = c.pyapi.bool_from_bool(c.context.get_constant(types.bool_,
        False))
    npr__nrsfj = c.pyapi.call_method(pmwtb__dwx, 'to_numpy', (fkvv__dwgqy,))
    vdtz__lny.data = c.unbox(typ.data, npr__nrsfj).value
    qmj__gzj = c.pyapi.object_getattr_string(val, 'indices')
    fkwoh__ulwd = c.context.insert_const_string(c.builder.module, 'pandas')
    zrk__cdhg = c.pyapi.import_module_noblock(fkwoh__ulwd)
    gqw__mqlae = c.pyapi.string_from_constant_string('Int32')
    wmvpc__dpkb = c.pyapi.call_method(zrk__cdhg, 'array', (qmj__gzj,
        gqw__mqlae))
    vdtz__lny.indices = c.unbox(dict_indices_arr_type, wmvpc__dpkb).value
    vdtz__lny.has_global_dictionary = c.context.get_constant(types.bool_, False
        )
    c.pyapi.decref(pmwtb__dwx)
    c.pyapi.decref(fkvv__dwgqy)
    c.pyapi.decref(npr__nrsfj)
    c.pyapi.decref(qmj__gzj)
    c.pyapi.decref(zrk__cdhg)
    c.pyapi.decref(gqw__mqlae)
    c.pyapi.decref(wmvpc__dpkb)
    if bodo.hiframes.boxing._use_dict_str_type:
        c.pyapi.decref(val)
    rweaa__htle = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(vdtz__lny._getvalue(), is_error=rweaa__htle)


@box(DictionaryArrayType)
def box_dict_arr(typ, val, c):
    vdtz__lny = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ == dict_str_arr_type:
        c.context.nrt.incref(c.builder, typ.data, vdtz__lny.data)
        fkrd__jbkbo = c.box(typ.data, vdtz__lny.data)
        mekl__vvbgn = cgutils.create_struct_proxy(dict_indices_arr_type)(c.
            context, c.builder, vdtz__lny.indices)
        osi__gifds = lir.FunctionType(c.pyapi.pyobj, [lir.IntType(64), c.
            pyapi.pyobj, lir.IntType(32).as_pointer(), lir.IntType(8).
            as_pointer()])
        ihny__ssm = cgutils.get_or_insert_function(c.builder.module,
            osi__gifds, name='box_dict_str_array')
        xvbd__hmag = cgutils.create_struct_proxy(types.Array(types.int32, 1,
            'C'))(c.context, c.builder, mekl__vvbgn.data)
        zvwma__qbc = c.builder.extract_value(xvbd__hmag.shape, 0)
        nbc__efo = xvbd__hmag.data
        aqxw__yuhhb = cgutils.create_struct_proxy(types.Array(types.int8, 1,
            'C'))(c.context, c.builder, mekl__vvbgn.null_bitmap).data
        npr__nrsfj = c.builder.call(ihny__ssm, [zvwma__qbc, fkrd__jbkbo,
            nbc__efo, aqxw__yuhhb])
        c.pyapi.decref(fkrd__jbkbo)
    else:
        fkwoh__ulwd = c.context.insert_const_string(c.builder.module, 'pyarrow'
            )
        ycu__vhhy = c.pyapi.import_module_noblock(fkwoh__ulwd)
        bko__roin = c.pyapi.object_getattr_string(ycu__vhhy, 'DictionaryArray')
        c.context.nrt.incref(c.builder, typ.data, vdtz__lny.data)
        fkrd__jbkbo = c.box(typ.data, vdtz__lny.data)
        c.context.nrt.incref(c.builder, dict_indices_arr_type, vdtz__lny.
            indices)
        qmj__gzj = c.box(dict_indices_arr_type, vdtz__lny.indices)
        iyuf__eny = c.pyapi.call_method(bko__roin, 'from_arrays', (qmj__gzj,
            fkrd__jbkbo))
        fkvv__dwgqy = c.pyapi.bool_from_bool(c.context.get_constant(types.
            bool_, False))
        npr__nrsfj = c.pyapi.call_method(iyuf__eny, 'to_numpy', (fkvv__dwgqy,))
        c.pyapi.decref(ycu__vhhy)
        c.pyapi.decref(fkrd__jbkbo)
        c.pyapi.decref(qmj__gzj)
        c.pyapi.decref(bko__roin)
        c.pyapi.decref(iyuf__eny)
        c.pyapi.decref(fkvv__dwgqy)
    c.context.nrt.decref(c.builder, typ, val)
    return npr__nrsfj


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
    eomw__ccnxe = pyval.dictionary.to_numpy(False)
    deuv__lbdq = pd.array(pyval.indices, 'Int32')
    eomw__ccnxe = context.get_constant_generic(builder, typ.data, eomw__ccnxe)
    deuv__lbdq = context.get_constant_generic(builder,
        dict_indices_arr_type, deuv__lbdq)
    qahdd__nhk = context.get_constant(types.bool_, False)
    bbod__zpt = lir.Constant.literal_struct([eomw__ccnxe, deuv__lbdq,
        qahdd__nhk])
    return bbod__zpt


@overload(operator.getitem, no_unliteral=True)
def dict_arr_getitem(A, ind):
    if not isinstance(A, DictionaryArrayType):
        return
    if isinstance(ind, types.Integer):

        def dict_arr_getitem_impl(A, ind):
            if bodo.libs.array_kernels.isna(A._indices, ind):
                return ''
            eaq__eog = A._indices[ind]
            return A._data[eaq__eog]
        return dict_arr_getitem_impl
    return lambda A, ind: init_dict_arr(A._data, A._indices[ind], A.
        _has_global_dictionary)


@overload_method(DictionaryArrayType, '_decode', no_unliteral=True)
def overload_dict_arr_decode(A):

    def impl(A):
        rekr__frkjs = A._data
        fygyu__zfckq = A._indices
        zvwma__qbc = len(fygyu__zfckq)
        gmme__vufq = [get_str_arr_item_length(rekr__frkjs, i) for i in
            range(len(rekr__frkjs))]
        ghvmj__gdgi = 0
        for i in range(zvwma__qbc):
            if not bodo.libs.array_kernels.isna(fygyu__zfckq, i):
                ghvmj__gdgi += gmme__vufq[fygyu__zfckq[i]]
        jpdh__ewj = pre_alloc_string_array(zvwma__qbc, ghvmj__gdgi)
        for i in range(zvwma__qbc):
            if bodo.libs.array_kernels.isna(fygyu__zfckq, i):
                bodo.libs.array_kernels.setna(jpdh__ewj, i)
                continue
            ind = fygyu__zfckq[i]
            if bodo.libs.array_kernels.isna(rekr__frkjs, ind):
                bodo.libs.array_kernels.setna(jpdh__ewj, i)
                continue
            jpdh__ewj[i] = rekr__frkjs[ind]
        return jpdh__ewj
    return impl


@overload(operator.setitem)
def dict_arr_setitem(A, idx, val):
    if not isinstance(A, DictionaryArrayType):
        return
    raise_bodo_error(
        "DictionaryArrayType is read-only and doesn't support setitem yet")


@numba.njit(no_cpython_wrapper=True)
def find_dict_ind(arr, val):
    eaq__eog = -1
    rekr__frkjs = arr._data
    for i in range(len(rekr__frkjs)):
        if bodo.libs.array_kernels.isna(rekr__frkjs, i):
            continue
        if rekr__frkjs[i] == val:
            eaq__eog = i
            break
    return eaq__eog


@numba.njit(no_cpython_wrapper=True)
def dict_arr_eq(arr, val):
    zvwma__qbc = len(arr)
    eaq__eog = find_dict_ind(arr, val)
    if eaq__eog == -1:
        return init_bool_array(np.full(zvwma__qbc, False, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices == eaq__eog


@numba.njit(no_cpython_wrapper=True)
def dict_arr_ne(arr, val):
    zvwma__qbc = len(arr)
    eaq__eog = find_dict_ind(arr, val)
    if eaq__eog == -1:
        return init_bool_array(np.full(zvwma__qbc, True, np.bool_), arr.
            _indices._null_bitmap.copy())
    return arr._indices != eaq__eog


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
        bnxd__aaq = arr._data
        wxk__kmfm = bodo.libs.int_arr_ext.alloc_int_array(len(bnxd__aaq), dtype
            )
        for dgz__vgbe in range(len(bnxd__aaq)):
            if bodo.libs.array_kernels.isna(bnxd__aaq, dgz__vgbe):
                bodo.libs.array_kernels.setna(wxk__kmfm, dgz__vgbe)
                continue
            wxk__kmfm[dgz__vgbe] = np.int64(bnxd__aaq[dgz__vgbe])
        zvwma__qbc = len(arr)
        fygyu__zfckq = arr._indices
        jpdh__ewj = bodo.libs.int_arr_ext.alloc_int_array(zvwma__qbc, dtype)
        for i in range(zvwma__qbc):
            if bodo.libs.array_kernels.isna(fygyu__zfckq, i):
                bodo.libs.array_kernels.setna(jpdh__ewj, i)
                continue
            jpdh__ewj[i] = wxk__kmfm[fygyu__zfckq[i]]
        return jpdh__ewj
    return impl


def cat_dict_str(arrs, sep):
    pass


@overload(cat_dict_str)
def cat_dict_str_overload(arrs, sep):
    bhg__cmcrg = len(arrs)
    mdei__sqbf = 'def impl(arrs, sep):\n'
    mdei__sqbf += '  ind_map = {}\n'
    mdei__sqbf += '  out_strs = []\n'
    mdei__sqbf += '  n = len(arrs[0])\n'
    for i in range(bhg__cmcrg):
        mdei__sqbf += f'  indices{i} = arrs[{i}]._indices\n'
    for i in range(bhg__cmcrg):
        mdei__sqbf += f'  data{i} = arrs[{i}]._data\n'
    mdei__sqbf += (
        '  out_indices = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)\n')
    mdei__sqbf += '  for i in range(n):\n'
    hyf__fofm = ' or '.join([f'bodo.libs.array_kernels.isna(arrs[{i}], i)' for
        i in range(bhg__cmcrg)])
    mdei__sqbf += f'    if {hyf__fofm}:\n'
    mdei__sqbf += '      bodo.libs.array_kernels.setna(out_indices, i)\n'
    mdei__sqbf += '      continue\n'
    for i in range(bhg__cmcrg):
        mdei__sqbf += f'    ind{i} = indices{i}[i]\n'
    dpkem__xne = '(' + ', '.join(f'ind{i}' for i in range(bhg__cmcrg)) + ')'
    mdei__sqbf += f'    if {dpkem__xne} not in ind_map:\n'
    mdei__sqbf += '      out_ind = len(out_strs)\n'
    mdei__sqbf += f'      ind_map[{dpkem__xne}] = out_ind\n'
    bzvpq__skd = "''" if is_overload_none(sep) else 'sep'
    hec__wlt = ', '.join([f'data{i}[ind{i}]' for i in range(bhg__cmcrg)])
    mdei__sqbf += f'      v = {bzvpq__skd}.join([{hec__wlt}])\n'
    mdei__sqbf += '      out_strs.append(v)\n'
    mdei__sqbf += '    else:\n'
    mdei__sqbf += f'      out_ind = ind_map[{dpkem__xne}]\n'
    mdei__sqbf += '    out_indices[i] = out_ind\n'
    mdei__sqbf += (
        '  out_str_arr = bodo.libs.str_arr_ext.str_arr_from_sequence(out_strs)\n'
        )
    mdei__sqbf += """  return bodo.libs.dict_arr_ext.init_dict_arr(out_str_arr, out_indices, False)
"""
    kaix__uuxc = {}
    exec(mdei__sqbf, {'bodo': bodo, 'numba': numba, 'np': np}, kaix__uuxc)
    impl = kaix__uuxc['impl']
    return impl


@lower_cast(DictionaryArrayType, StringArrayType)
def cast_dict_str_arr_to_str_arr(context, builder, fromty, toty, val):
    if fromty != dict_str_arr_type:
        return
    lvto__jzsto = bodo.utils.typing.decode_if_dict_array_overload(fromty)
    zpj__ppln = toty(fromty)
    lbrf__fmpdm = context.compile_internal(builder, lvto__jzsto, zpj__ppln,
        (val,))
    return impl_ret_new_ref(context, builder, toty, lbrf__fmpdm)


@register_jitable
def str_replace(arr, pat, repl, flags, regex):
    eomw__ccnxe = arr._data
    ejkj__hur = len(eomw__ccnxe)
    byh__qrx = pre_alloc_string_array(ejkj__hur, -1)
    if regex:
        ptnrd__faeh = re.compile(pat, flags)
        for i in range(ejkj__hur):
            if bodo.libs.array_kernels.isna(eomw__ccnxe, i):
                bodo.libs.array_kernels.setna(byh__qrx, i)
                continue
            byh__qrx[i] = ptnrd__faeh.sub(repl=repl, string=eomw__ccnxe[i])
    else:
        for i in range(ejkj__hur):
            if bodo.libs.array_kernels.isna(eomw__ccnxe, i):
                bodo.libs.array_kernels.setna(byh__qrx, i)
                continue
            byh__qrx[i] = eomw__ccnxe[i].replace(pat, repl)
    return init_dict_arr(byh__qrx, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_startswith(arr, pat, na):
    vdtz__lny = arr._data
    qyu__usvl = len(vdtz__lny)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(qyu__usvl)
    for i in range(qyu__usvl):
        dict_arr_out[i] = vdtz__lny[i].startswith(pat)
    deuv__lbdq = arr._indices
    lajhp__wkc = len(deuv__lbdq)
    jpdh__ewj = bodo.libs.bool_arr_ext.alloc_bool_array(lajhp__wkc)
    for i in range(lajhp__wkc):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jpdh__ewj, i)
        else:
            jpdh__ewj[i] = dict_arr_out[deuv__lbdq[i]]
    return jpdh__ewj


@register_jitable
def str_endswith(arr, pat, na):
    vdtz__lny = arr._data
    qyu__usvl = len(vdtz__lny)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(qyu__usvl)
    for i in range(qyu__usvl):
        dict_arr_out[i] = vdtz__lny[i].endswith(pat)
    deuv__lbdq = arr._indices
    lajhp__wkc = len(deuv__lbdq)
    jpdh__ewj = bodo.libs.bool_arr_ext.alloc_bool_array(lajhp__wkc)
    for i in range(lajhp__wkc):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jpdh__ewj, i)
        else:
            jpdh__ewj[i] = dict_arr_out[deuv__lbdq[i]]
    return jpdh__ewj


@numba.njit
def str_series_contains_regex(arr, pat, case, flags, na, regex):
    vdtz__lny = arr._data
    nixg__ifrf = pd.Series(vdtz__lny)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = nixg__ifrf.array._str_contains(pat, case, flags, na,
            regex)
    deuv__lbdq = arr._indices
    lajhp__wkc = len(deuv__lbdq)
    jpdh__ewj = bodo.libs.bool_arr_ext.alloc_bool_array(lajhp__wkc)
    for i in range(lajhp__wkc):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jpdh__ewj, i)
        else:
            jpdh__ewj[i] = dict_arr_out[deuv__lbdq[i]]
    return jpdh__ewj


@register_jitable
def str_contains_non_regex(arr, pat, case):
    vdtz__lny = arr._data
    qyu__usvl = len(vdtz__lny)
    dict_arr_out = bodo.libs.bool_arr_ext.alloc_bool_array(qyu__usvl)
    if not case:
        jfcvj__ppstr = pat.upper()
    for i in range(qyu__usvl):
        if case:
            dict_arr_out[i] = pat in vdtz__lny[i]
        else:
            dict_arr_out[i] = jfcvj__ppstr in vdtz__lny[i].upper()
    deuv__lbdq = arr._indices
    lajhp__wkc = len(deuv__lbdq)
    jpdh__ewj = bodo.libs.bool_arr_ext.alloc_bool_array(lajhp__wkc)
    for i in range(lajhp__wkc):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jpdh__ewj, i)
        else:
            jpdh__ewj[i] = dict_arr_out[deuv__lbdq[i]]
    return jpdh__ewj


@numba.njit
def str_match(arr, pat, case, flags, na):
    vdtz__lny = arr._data
    deuv__lbdq = arr._indices
    lajhp__wkc = len(deuv__lbdq)
    jpdh__ewj = bodo.libs.bool_arr_ext.alloc_bool_array(lajhp__wkc)
    nixg__ifrf = pd.Series(vdtz__lny)
    with numba.objmode(dict_arr_out=bodo.boolean_array):
        dict_arr_out = nixg__ifrf.array._str_match(pat, case, flags, na)
    for i in range(lajhp__wkc):
        if bodo.libs.array_kernels.isna(arr, i):
            bodo.libs.array_kernels.setna(jpdh__ewj, i)
        else:
            jpdh__ewj[i] = dict_arr_out[deuv__lbdq[i]]
    return jpdh__ewj


def create_simple_str2str_methods(func_name, func_args):
    mdei__sqbf = f"""def str_{func_name}({', '.join(func_args)}):
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
    kaix__uuxc = {}
    exec(mdei__sqbf, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr}, kaix__uuxc)
    return kaix__uuxc[f'str_{func_name}']


def _register_simple_str2str_methods():
    ecgq__jhvtl = {**dict.fromkeys(['capitalize', 'lower', 'swapcase',
        'title', 'upper'], ('arr',)), **dict.fromkeys(['lstrip', 'rstrip',
        'strip'], ('arr', 'to_strip')), **dict.fromkeys(['center', 'ljust',
        'rjust'], ('arr', 'width', 'fillchar')), **dict.fromkeys(['zfill'],
        ('arr', 'width'))}
    for func_name in ecgq__jhvtl.keys():
        spg__mhofg = create_simple_str2str_methods(func_name, ecgq__jhvtl[
            func_name])
        spg__mhofg = register_jitable(spg__mhofg)
        globals()[f'str_{func_name}'] = spg__mhofg


_register_simple_str2str_methods()


def create_find_methods(func_name):
    mdei__sqbf = f"""def str_{func_name}(arr, sub, start, end):
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
    kaix__uuxc = {}
    exec(mdei__sqbf, {'bodo': bodo, 'numba': numba, 'init_dict_arr':
        init_dict_arr, 'np': np}, kaix__uuxc)
    return kaix__uuxc[f'str_{func_name}']


def _register_find_methods():
    xetid__ldya = ['find', 'rfind']
    for func_name in xetid__ldya:
        spg__mhofg = create_find_methods(func_name)
        spg__mhofg = register_jitable(spg__mhofg)
        globals()[f'str_{func_name}'] = spg__mhofg


_register_find_methods()


@register_jitable
def str_count(arr, pat, flags):
    eomw__ccnxe = arr._data
    deuv__lbdq = arr._indices
    ejkj__hur = len(eomw__ccnxe)
    lajhp__wkc = len(deuv__lbdq)
    dnwga__opj = bodo.libs.int_arr_ext.alloc_int_array(ejkj__hur, np.int64)
    fca__kkz = bodo.libs.int_arr_ext.alloc_int_array(lajhp__wkc, np.int64)
    regex = re.compile(pat, flags)
    for i in range(ejkj__hur):
        if bodo.libs.array_kernels.isna(eomw__ccnxe, i):
            bodo.libs.array_kernels.setna(dnwga__opj, i)
            continue
        dnwga__opj[i] = bodo.libs.str_ext.str_findall_count(regex,
            eomw__ccnxe[i])
    for i in range(lajhp__wkc):
        if bodo.libs.array_kernels.isna(deuv__lbdq, i
            ) or bodo.libs.array_kernels.isna(dnwga__opj, deuv__lbdq[i]):
            bodo.libs.array_kernels.setna(fca__kkz, i)
        else:
            fca__kkz[i] = dnwga__opj[deuv__lbdq[i]]
    return fca__kkz


@register_jitable
def str_len(arr):
    eomw__ccnxe = arr._data
    deuv__lbdq = arr._indices
    lajhp__wkc = len(deuv__lbdq)
    dnwga__opj = bodo.libs.array_kernels.get_arr_lens(eomw__ccnxe, False)
    fca__kkz = bodo.libs.int_arr_ext.alloc_int_array(lajhp__wkc, np.int64)
    for i in range(lajhp__wkc):
        if bodo.libs.array_kernels.isna(deuv__lbdq, i
            ) or bodo.libs.array_kernels.isna(dnwga__opj, deuv__lbdq[i]):
            bodo.libs.array_kernels.setna(fca__kkz, i)
        else:
            fca__kkz[i] = dnwga__opj[deuv__lbdq[i]]
    return fca__kkz


@register_jitable
def str_slice(arr, start, stop, step):
    eomw__ccnxe = arr._data
    ejkj__hur = len(eomw__ccnxe)
    byh__qrx = bodo.libs.str_arr_ext.pre_alloc_string_array(ejkj__hur, -1)
    for i in range(ejkj__hur):
        if bodo.libs.array_kernels.isna(eomw__ccnxe, i):
            bodo.libs.array_kernels.setna(byh__qrx, i)
            continue
        byh__qrx[i] = eomw__ccnxe[i][start:stop:step]
    return init_dict_arr(byh__qrx, arr._indices.copy(), arr.
        _has_global_dictionary)


@register_jitable
def str_get(arr, i):
    eomw__ccnxe = arr._data
    deuv__lbdq = arr._indices
    ejkj__hur = len(eomw__ccnxe)
    lajhp__wkc = len(deuv__lbdq)
    byh__qrx = pre_alloc_string_array(ejkj__hur, -1)
    jpdh__ewj = pre_alloc_string_array(lajhp__wkc, -1)
    for dgz__vgbe in range(ejkj__hur):
        if bodo.libs.array_kernels.isna(eomw__ccnxe, dgz__vgbe) or not -len(
            eomw__ccnxe[dgz__vgbe]) <= i < len(eomw__ccnxe[dgz__vgbe]):
            bodo.libs.array_kernels.setna(byh__qrx, dgz__vgbe)
            continue
        byh__qrx[dgz__vgbe] = eomw__ccnxe[dgz__vgbe][i]
    for dgz__vgbe in range(lajhp__wkc):
        if bodo.libs.array_kernels.isna(deuv__lbdq, dgz__vgbe
            ) or bodo.libs.array_kernels.isna(byh__qrx, deuv__lbdq[dgz__vgbe]):
            bodo.libs.array_kernels.setna(jpdh__ewj, dgz__vgbe)
            continue
        jpdh__ewj[dgz__vgbe] = byh__qrx[deuv__lbdq[dgz__vgbe]]
    return jpdh__ewj


@register_jitable
def str_repeat_int(arr, repeats):
    eomw__ccnxe = arr._data
    ejkj__hur = len(eomw__ccnxe)
    byh__qrx = pre_alloc_string_array(ejkj__hur, -1)
    for i in range(ejkj__hur):
        if bodo.libs.array_kernels.isna(eomw__ccnxe, i):
            bodo.libs.array_kernels.setna(byh__qrx, i)
            continue
        byh__qrx[i] = eomw__ccnxe[i] * repeats
    return init_dict_arr(byh__qrx, arr._indices.copy(), arr.
        _has_global_dictionary)


def create_str2bool_methods(func_name):
    mdei__sqbf = f"""def str_{func_name}(arr):
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
    kaix__uuxc = {}
    exec(mdei__sqbf, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr}, kaix__uuxc)
    return kaix__uuxc[f'str_{func_name}']


def _register_str2bool_methods():
    for func_name in bodo.hiframes.pd_series_ext.str2bool_methods:
        spg__mhofg = create_str2bool_methods(func_name)
        spg__mhofg = register_jitable(spg__mhofg)
        globals()[f'str_{func_name}'] = spg__mhofg


_register_str2bool_methods()


@register_jitable
def str_extract(arr, pat, flags, n_cols):
    eomw__ccnxe = arr._data
    deuv__lbdq = arr._indices
    ejkj__hur = len(eomw__ccnxe)
    lajhp__wkc = len(deuv__lbdq)
    regex = re.compile(pat, flags=flags)
    glgk__vtlhw = []
    for wulj__heojs in range(n_cols):
        glgk__vtlhw.append(pre_alloc_string_array(ejkj__hur, -1))
    gxfkj__konyf = bodo.libs.bool_arr_ext.alloc_bool_array(ejkj__hur)
    rbdk__plj = deuv__lbdq.copy()
    for i in range(ejkj__hur):
        if bodo.libs.array_kernels.isna(eomw__ccnxe, i):
            gxfkj__konyf[i] = True
            for dgz__vgbe in range(n_cols):
                bodo.libs.array_kernels.setna(glgk__vtlhw[dgz__vgbe], i)
            continue
        dzgo__vpqe = regex.search(eomw__ccnxe[i])
        if dzgo__vpqe:
            gxfkj__konyf[i] = False
            lnvcr__xjjam = dzgo__vpqe.groups()
            for dgz__vgbe in range(n_cols):
                glgk__vtlhw[dgz__vgbe][i] = lnvcr__xjjam[dgz__vgbe]
        else:
            gxfkj__konyf[i] = True
            for dgz__vgbe in range(n_cols):
                bodo.libs.array_kernels.setna(glgk__vtlhw[dgz__vgbe], i)
    for i in range(lajhp__wkc):
        if gxfkj__konyf[rbdk__plj[i]]:
            bodo.libs.array_kernels.setna(rbdk__plj, i)
    zaql__unn = [init_dict_arr(glgk__vtlhw[i], rbdk__plj.copy(), arr.
        _has_global_dictionary) for i in range(n_cols)]
    return zaql__unn


def create_extractall_methods(is_multi_group):
    umpx__iqcm = '_multi' if is_multi_group else ''
    mdei__sqbf = f"""def str_extractall{umpx__iqcm}(arr, regex, n_cols, index_arr):
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
    kaix__uuxc = {}
    exec(mdei__sqbf, {'bodo': bodo, 'numba': numba, 'np': np,
        'init_dict_arr': init_dict_arr, 'pre_alloc_string_array':
        pre_alloc_string_array}, kaix__uuxc)
    return kaix__uuxc[f'str_extractall{umpx__iqcm}']


def _register_extractall_methods():
    for is_multi_group in [True, False]:
        umpx__iqcm = '_multi' if is_multi_group else ''
        spg__mhofg = create_extractall_methods(is_multi_group)
        spg__mhofg = register_jitable(spg__mhofg)
        globals()[f'str_extractall{umpx__iqcm}'] = spg__mhofg


_register_extractall_methods()
