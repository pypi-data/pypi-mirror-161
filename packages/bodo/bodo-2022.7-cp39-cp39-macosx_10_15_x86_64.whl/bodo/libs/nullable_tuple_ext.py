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
        bao__azhdl = [('data', fe_type.tuple_typ), ('null_values', fe_type.
            null_typ)]
        super(NullableTupleModel, self).__init__(dmm, fe_type, bao__azhdl)


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
        slsbw__nziug = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        slsbw__nziug.data = data_tuple
        slsbw__nziug.null_values = null_values
        context.nrt.incref(builder, signature.args[0], data_tuple)
        context.nrt.incref(builder, signature.args[1], null_values)
        return slsbw__nziug._getvalue()
    sig = NullableTupleType(data_tuple, null_values)(data_tuple, null_values)
    return sig, codegen


@box(NullableTupleType)
def box_nullable_tuple(typ, val, c):
    knh__gdg = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val
        )
    c.context.nrt.incref(c.builder, typ.tuple_typ, knh__gdg.data)
    c.context.nrt.incref(c.builder, typ.null_typ, knh__gdg.null_values)
    jlay__sjnh = c.pyapi.from_native_value(typ.tuple_typ, knh__gdg.data, c.
        env_manager)
    uyxa__mcjkr = c.pyapi.from_native_value(typ.null_typ, knh__gdg.
        null_values, c.env_manager)
    brdz__kyxft = c.context.get_constant(types.int64, len(typ.tuple_typ))
    lai__gcw = c.pyapi.list_new(brdz__kyxft)
    with cgutils.for_range(c.builder, brdz__kyxft) as iqrmn__hzgfp:
        i = iqrmn__hzgfp.index
        rucx__mgjjl = c.pyapi.long_from_longlong(i)
        cpkqj__llb = c.pyapi.object_getitem(uyxa__mcjkr, rucx__mgjjl)
        fbfux__xnvyd = c.pyapi.to_native_value(types.bool_, cpkqj__llb).value
        with c.builder.if_else(fbfux__xnvyd) as (ejok__xrz, soou__qnd):
            with ejok__xrz:
                c.pyapi.list_setitem(lai__gcw, i, c.pyapi.make_none())
            with soou__qnd:
                jkbb__pjb = c.pyapi.object_getitem(jlay__sjnh, rucx__mgjjl)
                c.pyapi.list_setitem(lai__gcw, i, jkbb__pjb)
        c.pyapi.decref(rucx__mgjjl)
        c.pyapi.decref(cpkqj__llb)
    ymr__jtle = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    hvy__aztn = c.pyapi.call_function_objargs(ymr__jtle, (lai__gcw,))
    c.pyapi.decref(jlay__sjnh)
    c.pyapi.decref(uyxa__mcjkr)
    c.pyapi.decref(ymr__jtle)
    c.pyapi.decref(lai__gcw)
    c.context.nrt.decref(c.builder, typ, val)
    return hvy__aztn


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
    slsbw__nziug = cgutils.create_struct_proxy(sig.args[0])(context,
        builder, value=args[0])
    impl = context.get_function('getiter', sig.return_type(sig.args[0].
        tuple_typ))
    return impl(builder, (slsbw__nziug.data,))


@overload(operator.eq)
def nullable_tuple_eq(val1, val2):
    if not isinstance(val1, NullableTupleType) or not isinstance(val2,
        NullableTupleType):
        return
    if val1 != val2:
        return lambda val1, val2: False
    msn__koqw = 'def impl(val1, val2):\n'
    msn__koqw += '    data_tup1 = val1._data\n'
    msn__koqw += '    null_tup1 = val1._null_values\n'
    msn__koqw += '    data_tup2 = val2._data\n'
    msn__koqw += '    null_tup2 = val2._null_values\n'
    fxqw__soolb = val1._tuple_typ
    for i in range(len(fxqw__soolb)):
        msn__koqw += f'    null1_{i} = null_tup1[{i}]\n'
        msn__koqw += f'    null2_{i} = null_tup2[{i}]\n'
        msn__koqw += f'    data1_{i} = data_tup1[{i}]\n'
        msn__koqw += f'    data2_{i} = data_tup2[{i}]\n'
        msn__koqw += f'    if null1_{i} != null2_{i}:\n'
        msn__koqw += '        return False\n'
        msn__koqw += f'    if null1_{i} and (data1_{i} != data2_{i}):\n'
        msn__koqw += f'        return False\n'
    msn__koqw += f'    return True\n'
    orko__ymy = {}
    exec(msn__koqw, {}, orko__ymy)
    impl = orko__ymy['impl']
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
    msn__koqw = 'def impl(nullable_tup):\n'
    msn__koqw += '    data_tup = nullable_tup._data\n'
    msn__koqw += '    null_tup = nullable_tup._null_values\n'
    msn__koqw += '    tl = numba.cpython.hashing._Py_uhash_t(len(data_tup))\n'
    msn__koqw += '    acc = _PyHASH_XXPRIME_5\n'
    fxqw__soolb = nullable_tup._tuple_typ
    for i in range(len(fxqw__soolb)):
        msn__koqw += f'    null_val_{i} = null_tup[{i}]\n'
        msn__koqw += f'    null_lane_{i} = hash(null_val_{i})\n'
        msn__koqw += (
            f'    if null_lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n'
            )
        msn__koqw += '        return -1\n'
        msn__koqw += f'    acc += null_lane_{i} * _PyHASH_XXPRIME_2\n'
        msn__koqw += '    acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n'
        msn__koqw += '    acc *= _PyHASH_XXPRIME_1\n'
        msn__koqw += f'    if not null_val_{i}:\n'
        msn__koqw += f'        lane_{i} = hash(data_tup[{i}])\n'
        msn__koqw += (
            f'        if lane_{i} == numba.cpython.hashing._Py_uhash_t(-1):\n')
        msn__koqw += f'            return -1\n'
        msn__koqw += f'        acc += lane_{i} * _PyHASH_XXPRIME_2\n'
        msn__koqw += (
            '        acc = numba.cpython.hashing._PyHASH_XXROTATE(acc)\n')
        msn__koqw += '        acc *= _PyHASH_XXPRIME_1\n'
    msn__koqw += """    acc += tl ^ (_PyHASH_XXPRIME_5 ^ numba.cpython.hashing._Py_uhash_t(3527539))
"""
    msn__koqw += '    if acc == numba.cpython.hashing._Py_uhash_t(-1):\n'
    msn__koqw += (
        '        return numba.cpython.hashing.process_return(1546275796)\n')
    msn__koqw += '    return numba.cpython.hashing.process_return(acc)\n'
    orko__ymy = {}
    exec(msn__koqw, {'numba': numba, '_PyHASH_XXPRIME_1': _PyHASH_XXPRIME_1,
        '_PyHASH_XXPRIME_2': _PyHASH_XXPRIME_2, '_PyHASH_XXPRIME_5':
        _PyHASH_XXPRIME_5}, orko__ymy)
    impl = orko__ymy['impl']
    return impl
