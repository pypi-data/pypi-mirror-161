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
        fpmnd__natuq = [('data', types.Tuple(fe_type.array_types)), (
            'names', types.Tuple(fe_type.names_typ)), ('name', fe_type.
            name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, fpmnd__natuq)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[ifn__zqh].values) for
        ifn__zqh in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (vly__jjn) for vly__jjn in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    kxwb__iqebv = c.context.insert_const_string(c.builder.module, 'pandas')
    nrpf__tgwqj = c.pyapi.import_module_noblock(kxwb__iqebv)
    wnwra__wkys = c.pyapi.object_getattr_string(nrpf__tgwqj, 'MultiIndex')
    mkah__uhogz = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        mkah__uhogz.data)
    sby__cmc = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        mkah__uhogz.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), mkah__uhogz
        .names)
    sxr__cgpel = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        mkah__uhogz.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, mkah__uhogz.name)
    gcjx__nwf = c.pyapi.from_native_value(typ.name_typ, mkah__uhogz.name, c
        .env_manager)
    blt__igc = c.pyapi.borrow_none()
    yja__wcgdl = c.pyapi.call_method(wnwra__wkys, 'from_arrays', (sby__cmc,
        blt__igc, sxr__cgpel))
    c.pyapi.object_setattr_string(yja__wcgdl, 'name', gcjx__nwf)
    c.pyapi.decref(sby__cmc)
    c.pyapi.decref(sxr__cgpel)
    c.pyapi.decref(gcjx__nwf)
    c.pyapi.decref(nrpf__tgwqj)
    c.pyapi.decref(wnwra__wkys)
    c.context.nrt.decref(c.builder, typ, val)
    return yja__wcgdl


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    fskpo__rmn = []
    dya__pyav = []
    for ifn__zqh in range(typ.nlevels):
        pod__gihv = c.pyapi.unserialize(c.pyapi.serialize_object(ifn__zqh))
        kbqyd__jibm = c.pyapi.call_method(val, 'get_level_values', (pod__gihv,)
            )
        eppo__lhiq = c.pyapi.object_getattr_string(kbqyd__jibm, 'values')
        c.pyapi.decref(kbqyd__jibm)
        c.pyapi.decref(pod__gihv)
        dhont__yfjx = c.pyapi.to_native_value(typ.array_types[ifn__zqh],
            eppo__lhiq).value
        fskpo__rmn.append(dhont__yfjx)
        dya__pyav.append(eppo__lhiq)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, fskpo__rmn)
    else:
        data = cgutils.pack_struct(c.builder, fskpo__rmn)
    sxr__cgpel = c.pyapi.object_getattr_string(val, 'names')
    ybp__itf = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    smvo__szy = c.pyapi.call_function_objargs(ybp__itf, (sxr__cgpel,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), smvo__szy
        ).value
    gcjx__nwf = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, gcjx__nwf).value
    mkah__uhogz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    mkah__uhogz.data = data
    mkah__uhogz.names = names
    mkah__uhogz.name = name
    for eppo__lhiq in dya__pyav:
        c.pyapi.decref(eppo__lhiq)
    c.pyapi.decref(sxr__cgpel)
    c.pyapi.decref(ybp__itf)
    c.pyapi.decref(smvo__szy)
    c.pyapi.decref(gcjx__nwf)
    return NativeValue(mkah__uhogz._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    qwn__vxms = 'pandas.MultiIndex.from_product'
    jou__vuzu = dict(sortorder=sortorder)
    dne__qquzz = dict(sortorder=None)
    check_unsupported_args(qwn__vxms, jou__vuzu, dne__qquzz, package_name=
        'pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{qwn__vxms}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{qwn__vxms}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{qwn__vxms}: iterables and names must be of the same length.')


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
    otxtc__ryqe = MultiIndexType(array_types, names_typ)
    blga__wtq = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, blga__wtq, otxtc__ryqe)
    enckw__xrwxc = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{blga__wtq}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    hcnts__kmuu = {}
    exec(enckw__xrwxc, globals(), hcnts__kmuu)
    usg__leer = hcnts__kmuu['impl']
    return usg__leer


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        eqk__ewwq, zhh__esqb, jbnk__hgetw = args
        ssbc__btcmt = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        ssbc__btcmt.data = eqk__ewwq
        ssbc__btcmt.names = zhh__esqb
        ssbc__btcmt.name = jbnk__hgetw
        context.nrt.incref(builder, signature.args[0], eqk__ewwq)
        context.nrt.incref(builder, signature.args[1], zhh__esqb)
        context.nrt.incref(builder, signature.args[2], jbnk__hgetw)
        return ssbc__btcmt._getvalue()
    aan__ydv = MultiIndexType(data.types, names.types, name)
    return aan__ydv(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        vetzq__qak = len(I.array_types)
        enckw__xrwxc = 'def impl(I, ind):\n'
        enckw__xrwxc += '  data = I._data\n'
        enckw__xrwxc += (
            '  return init_multi_index(({},), I._names, I._name)\n'.format(
            ', '.join(f'ensure_contig_if_np(data[{ifn__zqh}][ind])' for
            ifn__zqh in range(vetzq__qak))))
        hcnts__kmuu = {}
        exec(enckw__xrwxc, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, hcnts__kmuu)
        usg__leer = hcnts__kmuu['impl']
        return usg__leer


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    piu__apyf, mvtvm__icnq = sig.args
    if piu__apyf != mvtvm__icnq:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
