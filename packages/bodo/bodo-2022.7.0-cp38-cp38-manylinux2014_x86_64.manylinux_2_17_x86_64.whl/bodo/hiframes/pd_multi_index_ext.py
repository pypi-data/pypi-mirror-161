"""Support for MultiIndex type of Pandas
"""
import operator
import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from bodo.utils.conversion import ensure_contig_if_np
from bodo.utils.typing import BodoError, check_unsupported_args, dtype_to_array_type, get_val_type_maybe_str_literal, is_overload_none


class MultiIndexType(types.ArrayCompatible):

    def __init__(self, array_types, names_typ=None, name_typ=None):
        names_typ = (types.none,) * len(array_types
            ) if names_typ is None else names_typ
        name_typ = types.none if name_typ is None else name_typ
        self.array_types = array_types
        self.names_typ = names_typ
        self.name_typ = name_typ
        super(MultiIndexType, self).__init__(name=
            'MultiIndexType({}, {}, {})'.format(array_types, names_typ,
            name_typ))
    ndim = 1

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return MultiIndexType(self.array_types, self.names_typ, self.name_typ)

    @property
    def nlevels(self):
        return len(self.array_types)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(MultiIndexType)
class MultiIndexModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        mkp__lyo = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, mkp__lyo)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[giy__xgu].values) for
        giy__xgu in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (hzs__lszu) for hzs__lszu in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    dort__ofa = c.context.insert_const_string(c.builder.module, 'pandas')
    kis__aeaan = c.pyapi.import_module_noblock(dort__ofa)
    atob__wqb = c.pyapi.object_getattr_string(kis__aeaan, 'MultiIndex')
    ufk__mdjc = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types), ufk__mdjc
        .data)
    mck__dyd = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        ufk__mdjc.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), ufk__mdjc.names
        )
    cslqe__diu = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        ufk__mdjc.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, ufk__mdjc.name)
    tela__mszwz = c.pyapi.from_native_value(typ.name_typ, ufk__mdjc.name, c
        .env_manager)
    aocze__hdeia = c.pyapi.borrow_none()
    fwau__afkns = c.pyapi.call_method(atob__wqb, 'from_arrays', (mck__dyd,
        aocze__hdeia, cslqe__diu))
    c.pyapi.object_setattr_string(fwau__afkns, 'name', tela__mszwz)
    c.pyapi.decref(mck__dyd)
    c.pyapi.decref(cslqe__diu)
    c.pyapi.decref(tela__mszwz)
    c.pyapi.decref(kis__aeaan)
    c.pyapi.decref(atob__wqb)
    c.context.nrt.decref(c.builder, typ, val)
    return fwau__afkns


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    cntz__zuxi = []
    wmjts__mucs = []
    for giy__xgu in range(typ.nlevels):
        yho__hvqak = c.pyapi.unserialize(c.pyapi.serialize_object(giy__xgu))
        bkzlp__llqw = c.pyapi.call_method(val, 'get_level_values', (
            yho__hvqak,))
        zsvux__nfs = c.pyapi.object_getattr_string(bkzlp__llqw, 'values')
        c.pyapi.decref(bkzlp__llqw)
        c.pyapi.decref(yho__hvqak)
        sber__nhkvf = c.pyapi.to_native_value(typ.array_types[giy__xgu],
            zsvux__nfs).value
        cntz__zuxi.append(sber__nhkvf)
        wmjts__mucs.append(zsvux__nfs)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, cntz__zuxi)
    else:
        data = cgutils.pack_struct(c.builder, cntz__zuxi)
    cslqe__diu = c.pyapi.object_getattr_string(val, 'names')
    gotzi__hjkw = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    wxtwe__twyq = c.pyapi.call_function_objargs(gotzi__hjkw, (cslqe__diu,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), wxtwe__twyq
        ).value
    tela__mszwz = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, tela__mszwz).value
    ufk__mdjc = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ufk__mdjc.data = data
    ufk__mdjc.names = names
    ufk__mdjc.name = name
    for zsvux__nfs in wmjts__mucs:
        c.pyapi.decref(zsvux__nfs)
    c.pyapi.decref(cslqe__diu)
    c.pyapi.decref(gotzi__hjkw)
    c.pyapi.decref(wxtwe__twyq)
    c.pyapi.decref(tela__mszwz)
    return NativeValue(ufk__mdjc._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    ryop__pkhdj = 'pandas.MultiIndex.from_product'
    keq__yda = dict(sortorder=sortorder)
    buv__qnkd = dict(sortorder=None)
    check_unsupported_args(ryop__pkhdj, keq__yda, buv__qnkd, package_name=
        'pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{ryop__pkhdj}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{ryop__pkhdj}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{ryop__pkhdj}: iterables and names must be of the same length.')


def from_product(iterable, sortorder=None, names=None):
    pass


@overload(from_product)
def from_product_overload(iterables, sortorder=None, names=None):
    from_product_error_checking(iterables, sortorder, names)
    array_types = tuple(dtype_to_array_type(iterable.dtype) for iterable in
        iterables)
    if is_overload_none(names):
        names_typ = tuple([types.none] * len(iterables))
    else:
        names_typ = names.types
    yhhr__rajdr = MultiIndexType(array_types, names_typ)
    wwns__swfp = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, wwns__swfp, yhhr__rajdr)
    hyjl__vyxfi = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{wwns__swfp}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    upp__likyy = {}
    exec(hyjl__vyxfi, globals(), upp__likyy)
    wara__dgtv = upp__likyy['impl']
    return wara__dgtv


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        qwifn__aewf, stny__acs, hve__bfnwr = args
        jgm__ctk = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        jgm__ctk.data = qwifn__aewf
        jgm__ctk.names = stny__acs
        jgm__ctk.name = hve__bfnwr
        context.nrt.incref(builder, signature.args[0], qwifn__aewf)
        context.nrt.incref(builder, signature.args[1], stny__acs)
        context.nrt.incref(builder, signature.args[2], hve__bfnwr)
        return jgm__ctk._getvalue()
    vgc__udt = MultiIndexType(data.types, names.types, name)
    return vgc__udt(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        jprh__dam = len(I.array_types)
        hyjl__vyxfi = 'def impl(I, ind):\n'
        hyjl__vyxfi += '  data = I._data\n'
        hyjl__vyxfi += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(f'ensure_contig_if_np(data[{giy__xgu}][ind])' for
            giy__xgu in range(jprh__dam))))
        upp__likyy = {}
        exec(hyjl__vyxfi, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, upp__likyy)
        wara__dgtv = upp__likyy['impl']
        return wara__dgtv


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    yexjc__uavfl, vcvp__fwsbg = sig.args
    if yexjc__uavfl != vcvp__fwsbg:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
