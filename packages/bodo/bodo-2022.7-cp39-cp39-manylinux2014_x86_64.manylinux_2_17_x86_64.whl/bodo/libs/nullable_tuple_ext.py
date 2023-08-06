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
        jhvb__pyzwm = [('data', fe_type.tuple_typ), ('null_values', fe_type
            .null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, jhvb__pyzwm)


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
        bhvnx__kgd = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        bhvnx__kgd.data = data_tuple
        bhvnx__kgd.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return bhvnx__kgd._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    zeg__ruu = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    c.context.nrt.incref(c.builder, typ.tuple_typ, zeg__ruu.data)
    c.context.nrt.incref(c.builder, typ.null_typ, zeg__ruu.null_values)
    jwf__envui = c.pyapi.from_native_value(typ.tuple_typ, zeg__ruu.data, c.
        env_manager)
    wzr__ejj = c.pyapi.from_native_value(typ.null_typ, zeg__ruu.null_values,
        c.env_manager)
    obvfh__sglku = c.context.get_constant(types.int64, len(typ.tuple_typ))
    hlyme__fsa = c.pyapi.list_new(obvfh__sglku)
    with cgutils.for_range(c.builder, obvfh__sglku) as hth__xrvd:
        i = hth__xrvd.index
        kaafy__ftrl = c.pyapi.long_from_longlong(i)
        kangu__kutl = c.pyapi.object_getitem(wzr__ejj, kaafy__ftrl)
        yun__hdof = c.pyapi.to_native_value(types.bool_, kangu__kutl).value
        with c.builder.if_else(yun__hdof) as (nujy__hgk, nrk__lyfz):
            with nujy__hgk:
                c.pyapi.list_setitem(hlyme__fsa, i, c.pyapi.make_none())
            with nrk__lyfz:
                bymst__vcf = c.pyapi.object_getitem(jwf__envui, kaafy__ftrl)
                c.pyapi.list_setitem(hlyme__fsa, i, bymst__vcf)
        c.pyapi.decref(kaafy__ftrl)
        c.pyapi.decref(kangu__kutl)
    atyoh__qeh = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    yhedf__wmfuk = c.pyapi.call_function_objargs(atyoh__qeh, (hlyme__fsa,))
    c.pyapi.decref(jwf__envui)
    c.pyapi.decref(wzr__ejj)
    c.pyapi.decref(atyoh__qeh)
    c.pyapi.decref(hlyme__fsa)
    c.context.nrt.decref(c.builder, typ, val)
    return yhedf__wmfuk


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
    bhvnx__kgd = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (bhvnx__kgd.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    vct__reqn = 'def impl(val1, val2):\n'
    vct__reqn += '    data_tup1 = val1._data\n'
    vct__reqn += '    null_tup1 = val1._null_values\n'
    vct__reqn += '    data_tup2 = val2._data\n'
    vct__reqn += '    null_tup2 = val2._null_values\n'
    tnmll__fwovm = val1._tuple_typ
    for i in range(len(tnmll__fwovm)):
        vct__reqn += f'    null1_{i} = null_tup1[{i}]\n'
        vct__reqn += f'    null2_{i} = null_tup2[{i}]\n'
        vct__reqn += f'    data1_{i} = data_tup1[{i}]\n'
        vct__reqn += f'    data2_{i} = data_tup2[{i}]\n'
        vct__reqn += f'    if null1_{i} != null2_{i}:\n'
        vct__reqn += '        return False\n'
        vct__reqn += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        vct__reqn += f'        return False\n'
    vct__reqn += f'    return True\n'
    laq__iariy = {}
    exec(vct__reqn, {}, laq__iariy)
    impl = laq__iariy['impl']
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
    vct__reqn = 'def impl(nullable_tup):\n'
    vct__reqn += '    data_tup = nullable_tup._data\n'
    vct__reqn += '    null_tup = nullable_tup._null_values\n'
    vct__reqn += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    vct__reqn += '    acc = _PyHASH_XXPRIME_5\n'
    tnmll__fwovm = nullable_tup._tuple_typ
    for i in range(len(tnmll__fwovm)):
        vct__reqn += f'    null_val_{i} = null_tup[{i}]\n'
        vct__reqn += f'    null_lane_{i} = hash(null_val_{i})\n'
        vct__reqn += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        vct__reqn += '        return -1\n'
        vct__reqn += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        vct__reqn += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        vct__reqn += '    acc *= _PyHASH_XXPRIME_1\n'
        vct__reqn += f'    if not null_val_{i}:\n'
        vct__reqn += f'        lane_{i} = hash(data_tup[{i}])\n'
        vct__reqn += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        vct__reqn += f'            return -1\n'
        vct__reqn += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        vct__reqn += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        vct__reqn += '        acc *= _PyHASH_XXPRIME_1\n'
    vct__reqn += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    vct__reqn += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    vct__reqn += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    vct__reqn += '    return numba.cpython.hashing.process_return(acc)\n'
    laq__iariy = {}
    exec(vct__reqn, {'numba': numba, '_PyHASH_XXPRIME_1': _PyHASH_XXPRIME_1,
        '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2, '_PyHASH_XXPRIME_5':
        _PyHASH_XXPRIME_5}, laq__iariy)
    impl = laq__iariy['impl']
    return impl
