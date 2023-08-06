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
        emzo__ngvpa = [('data', fe_type.tuple_typ), ('null_values', fe_type
            .null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, emzo__ngvpa)


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
        vru__ivb = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        vru__ivb.data = data_tuple
        vru__ivb.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return vru__ivb._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    xbolr__ymocj = cgutils.create_struct_proxy(typ)(c.context, c.builder,
        value=val)
    c.context.nrt.incref(c.builder, typ.tuple_typ, xbolr__ymocj.data)
    c.context.nrt.incref(c.builder, typ.null_typ, xbolr__ymocj.null_values)
    nsy__yrefr = c.pyapi.from_native_value(typ.tuple_typ, xbolr__ymocj.data,
        c.env_manager)
    oafez__xrm = c.pyapi.from_native_value(typ.null_typ, xbolr__ymocj.
        null_values, c.env_manager)
    ixjy__fyj = c.context.get_constant(types.int64, len(typ.tuple_typ))
    oiagg__yxqm = c.pyapi.list_new(ixjy__fyj)
    with cgutils.for_range(c.builder, ixjy__fyj) as unlme__qsg:
        i = unlme__qsg.index
        jzm__gzllb = c.pyapi.long_from_longlong(i)
        noty__vjakw = c.pyapi.object_getitem(oafez__xrm, jzm__gzllb)
        uhd__hfl = c.pyapi.to_native_value(types.bool_, noty__vjakw).value
        with c.builder.if_else(uhd__hfl) as (fheib__rfiwb, una__sbgt):
            with fheib__rfiwb:
                c.pyapi.list_setitem(oiagg__yxqm, i, c.pyapi.make_none())
            with una__sbgt:
                avndb__fpwtv = c.pyapi.object_getitem(nsy__yrefr, jzm__gzllb)
                c.pyapi.list_setitem(oiagg__yxqm, i, avndb__fpwtv)
        c.pyapi.decref(jzm__gzllb)
        c.pyapi.decref(noty__vjakw)
    jcej__gdnhs = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    xqg__qxgp = c.pyapi.call_function_objargs(jcej__gdnhs, (oiagg__yxqm,))
    c.pyapi.decref(nsy__yrefr)
    c.pyapi.decref(oafez__xrm)
    c.pyapi.decref(jcej__gdnhs)
    c.pyapi.decref(oiagg__yxqm)
    c.context.nrt.decref(c.builder, typ, val)
    return xqg__qxgp


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
    vru__ivb = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (vru__ivb.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    pjzq__sugv = 'def impl(val1, val2):\n'
    pjzq__sugv += '    data_tup1 = val1._data\n'
    pjzq__sugv += '    null_tup1 = val1._null_values\n'
    pjzq__sugv += '    data_tup2 = val2._data\n'
    pjzq__sugv += '    null_tup2 = val2._null_values\n'
    keolb__numy = val1._tuple_typ
    for i in range(len(keolb__numy)):
        pjzq__sugv += f'    null1_{i} = null_tup1[{i}]\n'
        pjzq__sugv += f'    null2_{i} = null_tup2[{i}]\n'
        pjzq__sugv += f'    data1_{i} = data_tup1[{i}]\n'
        pjzq__sugv += f'    data2_{i} = data_tup2[{i}]\n'
        pjzq__sugv += f'    if null1_{i} != null2_{i}:\n'
        pjzq__sugv += '        return False\n'
        pjzq__sugv += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        pjzq__sugv += f'        return False\n'
    pjzq__sugv += f'    return True\n'
    ugn__xxiro = {}
    exec(pjzq__sugv, {}, ugn__xxiro)
    impl = ugn__xxiro['impl']
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
    pjzq__sugv = 'def impl(nullable_tup):\n'
    pjzq__sugv += '    data_tup = nullable_tup._data\n'
    pjzq__sugv += '    null_tup = nullable_tup._null_values\n'
    pjzq__sugv += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    pjzq__sugv += '    acc = _PyHASH_XXPRIME_5\n'
    keolb__numy = nullable_tup._tuple_typ
    for i in range(len(keolb__numy)):
        pjzq__sugv += f'    null_val_{i} = null_tup[{i}]\n'
        pjzq__sugv += f'    null_lane_{i} = hash(null_val_{i})\n'
        pjzq__sugv += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        pjzq__sugv += '        return -1\n'
        pjzq__sugv += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        pjzq__sugv += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        pjzq__sugv += '    acc *= _PyHASH_XXPRIME_1\n'
        pjzq__sugv += f'    if not null_val_{i}:\n'
        pjzq__sugv += f'        lane_{i} = hash(data_tup[{i}])\n'
        pjzq__sugv += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        pjzq__sugv += f'            return -1\n'
        pjzq__sugv += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        pjzq__sugv += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        pjzq__sugv += '        acc *= _PyHASH_XXPRIME_1\n'
    pjzq__sugv += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    pjzq__sugv += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    pjzq__sugv += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    pjzq__sugv += '    return numba.cpython.hashing.process_return(acc)\n'
    ugn__xxiro = {}
    exec(pjzq__sugv, {'numba': numba, '_PyHASH_XXPRIME_1':
        _PyHASH_XXPRIME_1, '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2,
        '_PyHASH_XXPRIME_5': _PyHASH_XXPRIME_5}, ugn__xxiro)
    impl = ugn__xxiro['impl']
    return impl
