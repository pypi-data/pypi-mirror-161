"""
Wrapper class for Tuples that supports tracking null entries.
This is primarily used for maintaining null information for
Series values used in df.apply
"""
import operator
import numba
from numba.core import cgutils, types
from numba.extending import box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_method, register_model


class NullableTupleType(types.IterableType):

    def __init__(self, tuple_typ, null_typ):
        self._tuple_typ = tuple_typ
        self._null_typ = null_typ
        super(NullableTupleType, self).__init__(name=
            f'NullableTupleType({tuple_typ}, {null_typ})')

    @property
    def tuple_typ(self):
        return self._tuple_typ

    @property
    def null_typ(self):
        return self._null_typ

    def __getitem__(self, i):
        return self._tuple_typ[i]

    @property
    def key(self):
        return self._tuple_typ

    @property
    def dtype(self):
        return self.tuple_typ.dtype

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)

    @property
    def iterator_type(self):
        return self.tuple_typ.iterator_type

    def __len__(self):
        return len(self.tuple_typ)


@register_model(NullableTupleType)
class NullableTupleModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ubjnt__icxg = [('data', fe_type.tuple_typ), ('null_values', fe_type
            .null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, ubjnt__icxg)


make_attribute_wrapper(NullableTupleType, 'data', '_data')
make_attribute_wrapper(NullableTupleType, 'null_values', '_null_values')


@intrinsic
def build_nullable_tuple(typingctx, data_tuple, null_values):
    assert isinstance(data_tuple, types.BaseTuple
        ), "build_nullable_tuple 'data_tuple' argument must be a tuple"
    assert isinstance(null_values, types.BaseTuple
        ), "build_nullable_tuple 'null_values' argument must be a tuple"
    data_tuple = types.unliteral(data_tuple)
    null_values = types.unliteral(null_values)

    def codegen(context, builder, signature, args):
        data_tuple, null_values = args
        zfzgz__ato = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        zfzgz__ato.data = data_tuple
        zfzgz__ato.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return zfzgz__ato._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    pig__vqjs = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, pig__vqjs.data)
    c.context.nrt.incref(c.builder, typ.null_typ, pig__vqjs.null_values)
    qevq__ozd = c.pyapi.from_native_value(typ.tuple_typ, pig__vqjs.data, c.
        env_manager)
    kjute__qgygg = c.pyapi.from_native_value(typ.null_typ, pig__vqjs.
        null_values, c.env_manager)
    aru__xphy = c.context.get_constant(types.int64, len(typ.tuple_typ))
    vmcn__rcf = c.pyapi.list_new(aru__xphy)
    with cgutils.for_range(c.builder, aru__xphy) as swy__csdv:
        i = swy__csdv.index
        iino__cgffl = c.pyapi.long_from_longlong(i)
        hfwzs__gzact = c.pyapi.object_getitem(kjute__qgygg, iino__cgffl)
        oibx__xxo = c.pyapi.to_native_value(types.bool_, hfwzs__gzact).value
        with c.builder.if_else(oibx__xxo) as (vykil__xehrv, trgq__neq):
            with vykil__xehrv:
                c.pyapi.list_setitem(vmcn__rcf, i, c.pyapi.make_none())
            with trgq__neq:
                htn__xkj = c.pyapi.object_getitem(qevq__ozd, iino__cgffl)
                c.pyapi.list_setitem(vmcn__rcf, i, htn__xkj)
        c.pyapi.decref(iino__cgffl)
        c.pyapi.decref(hfwzs__gzact)
    wts__gtjq = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    fptsy__gluok = c.pyapi.call_function_objargs(wts__gtjq, (vmcn__rcf,))
    c.pyapi.decref(qevq__ozd)
    c.pyapi.decref(kjute__qgygg)
    c.pyapi.decref(wts__gtjq)
    c.pyapi.decref(vmcn__rcf)
    c.context.nrt.decref(c.builder, typ, val)
    return fptsy__gluok


@overload(operator.getitem)
def overload_getitem(A, idx):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A, idx: A._data[idx]


@overload(len)
def overload_len(A):
    if not isinstance(A, NullableTupleType):
        return
    return lambda A: len(A._data)


@lower_builtin('getiter', NullableTupleType)
def nullable_tuple_getiter(context, builder, sig, args):
    zfzgz__ato = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (zfzgz__ato.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    lmtf__pvrep = 'def impl(val1, val2):\n'
    lmtf__pvrep += '    data_tup1 = val1._data\n'
    lmtf__pvrep += '    null_tup1 = val1._null_values\n'
    lmtf__pvrep += '    data_tup2 = val2._data\n'
    lmtf__pvrep += '    null_tup2 = val2._null_values\n'
    mhsow__yaxx = val1._tuple_typ
    for i in range(len(mhsow__yaxx)):
        lmtf__pvrep += f'    null1_{i} = null_tup1[{i}]\n'
        lmtf__pvrep += f'    null2_{i} = null_tup2[{i}]\n'
        lmtf__pvrep += f'    data1_{i} = data_tup1[{i}]\n'
        lmtf__pvrep += f'    data2_{i} = data_tup2[{i}]\n'
        lmtf__pvrep += f'    if null1_{i} != null2_{i}:\n'
        lmtf__pvrep += '        return False\n'
        lmtf__pvrep += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        lmtf__pvrep += f'        return False\n'
    lmtf__pvrep += f'    return True\n'
    hzh__dwum = {}
    exec(lmtf__pvrep, {}, hzh__dwum)
    impl = hzh__dwum['impl']
    return impl


@overload_method(NullableTupleType, '__hash__')
def nullable_tuple_hash(val):

    def impl(val):
        return _nullable_tuple_hash(val)
    return impl


_PyHASH_XXPRIME_1 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_2 = numba.cpython.hashing._PyHASH_XXPRIME_1
_PyHASH_XXPRIME_5 = numba.cpython.hashing._PyHASH_XXPRIME_1


@numba.generated_jit(nopython=True)
def _nullable_tuple_hash(nullable_tup):
    lmtf__pvrep = 'def impl(nullable_tup):\n'
    lmtf__pvrep += '    data_tup = nullable_tup._data\n'
    lmtf__pvrep += '    null_tup = nullable_tup._null_values\n'
    lmtf__pvrep += (
        '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n')
    lmtf__pvrep += '    acc = _PyHASH_XXPRIME_5\n'
    mhsow__yaxx = nullable_tup._tuple_typ
    for i in range(len(mhsow__yaxx)):
        lmtf__pvrep += f'    null_val_{i} = null_tup[{i}]\n'
        lmtf__pvrep += f'    null_lane_{i} = hash(null_val_{i})\n'
        lmtf__pvrep += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        lmtf__pvrep += '        return -1\n'
        lmtf__pvrep += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        lmtf__pvrep += (
            '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        lmtf__pvrep += '    acc *= _PyHASH_XXPRIME_1\n'
        lmtf__pvrep += f'    if not null_val_{i}:\n'
        lmtf__pvrep += f'        lane_{i} = hash(data_tup[{i}])\n'
        lmtf__pvrep += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        lmtf__pvrep += f'            return -1\n'
        lmtf__pvrep += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        lmtf__pvrep += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        lmtf__pvrep += '        acc *= _PyHASH_XXPRIME_1\n'
    lmtf__pvrep += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    lmtf__pvrep += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    lmtf__pvrep += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    lmtf__pvrep += '    return numba.cpython.hashing.process_return(acc)\n'
    hzh__dwum = {}
    exec(lmtf__pvrep, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, hzh__dwum)
    impl = hzh__dwum['impl']
    return impl
