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
        qyzjk__lmu = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, qyzjk__lmu)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[jyd__gzn].values) for
        jyd__gzn in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (efk__xfwt) for efk__xfwt in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    fdiau__ioonp = c.context.insert_const_string(c.builder.module, 'pandas')
    bzuu__ibd = c.pyapi.import_module_noblock(fdiau__ioonp)
    qhwhm__tzlt = c.pyapi.object_getattr_string(bzuu__ibd, 'MultiIndex')
    sznpc__vlw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        sznpc__vlw.data)
    tvwr__xsae = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        sznpc__vlw.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ), sznpc__vlw.
        names)
    imnwo__tsuo = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        sznpc__vlw.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, sznpc__vlw.name)
    vrfa__cxfbv = c.pyapi.from_native_value(typ.name_typ, sznpc__vlw.name,
        c.env_manager)
    yav__xqn = c.pyapi.borrow_none()
    tmr__pxqsw = c.pyapi.call_method(qhwhm__tzlt, 'from_arrays', (
        tvwr__xsae, yav__xqn, imnwo__tsuo))
    c.pyapi.object_setattr_string(tmr__pxqsw, 'name', vrfa__cxfbv)
    c.pyapi.decref(tvwr__xsae)
    c.pyapi.decref(imnwo__tsuo)
    c.pyapi.decref(vrfa__cxfbv)
    c.pyapi.decref(bzuu__ibd)
    c.pyapi.decref(qhwhm__tzlt)
    c.context.nrt.decref(c.builder, typ, val)
    return tmr__pxqsw


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    yhmag__ebq = []
    rza__maxix = []
    for jyd__gzn in range(typ.nlevels):
        vgg__ntr = c.pyapi.unserialize(c.pyapi.serialize_object(jyd__gzn))
        xkdux__igqg = c.pyapi.call_method(val, 'get_level_values', (vgg__ntr,))
        nvz__xot = c.pyapi.object_getattr_string(xkdux__igqg, 'values')
        c.pyapi.decref(xkdux__igqg)
        c.pyapi.decref(vgg__ntr)
        mxksf__dggvh = c.pyapi.to_native_value(typ.array_types[jyd__gzn],
            nvz__xot).value
        yhmag__ebq.append(mxksf__dggvh)
        rza__maxix.append(nvz__xot)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, yhmag__ebq)
    else:
        data = cgutils.pack_struct(c.builder, yhmag__ebq)
    imnwo__tsuo = c.pyapi.object_getattr_string(val, 'names')
    fwxpf__mqyxr = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    lfdk__coq = c.pyapi.call_function_objargs(fwxpf__mqyxr, (imnwo__tsuo,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), lfdk__coq
        ).value
    vrfa__cxfbv = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, vrfa__cxfbv).value
    sznpc__vlw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    sznpc__vlw.data = data
    sznpc__vlw.names = names
    sznpc__vlw.name = name
    for nvz__xot in rza__maxix:
        c.pyapi.decref(nvz__xot)
    c.pyapi.decref(imnwo__tsuo)
    c.pyapi.decref(fwxpf__mqyxr)
    c.pyapi.decref(lfdk__coq)
    c.pyapi.decref(vrfa__cxfbv)
    return NativeValue(sznpc__vlw._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    pxlfr__wbmig = 'pandas.MultiIndex.from_product'
    nfs__sajz = dict(sortorder=sortorder)
    voxbg__mgl = dict(sortorder=None)
    check_unsupported_args(pxlfr__wbmig, nfs__sajz, voxbg__mgl,
        package_name='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{pxlfr__wbmig}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{pxlfr__wbmig}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{pxlfr__wbmig}: iterables and names must be of the same length.')


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
    vxhbo__gcal = MultiIndexType(array_types, names_typ)
    jiyx__wgijo = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, jiyx__wgijo, vxhbo__gcal)
    mobdq__qzhhn = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{jiyx__wgijo}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    nhsa__gamlh = {}
    exec(mobdq__qzhhn, globals(), nhsa__gamlh)
    nwdqu__git = nhsa__gamlh['impl']
    return nwdqu__git


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        mus__jtlc, zqxj__uwt, hrmzl__kps = args
        mgx__cihc = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        mgx__cihc.data = mus__jtlc
        mgx__cihc.names = zqxj__uwt
        mgx__cihc.name = hrmzl__kps
        context.nrt.incref(builder, signature.args[0], mus__jtlc)
        context.nrt.incref(builder, signature.args[1], zqxj__uwt)
        context.nrt.incref(builder, signature.args[2], hrmzl__kps)
        return mgx__cihc._getvalue()
    yfv__ggmvg = MultiIndexType(data.types, names.types, name)
    return yfv__ggmvg(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        tzzjw__ajuvp = len(I.array_types)
        mobdq__qzhhn = 'def impl(I, ind):\n'
        mobdq__qzhhn += '  data = I._data\n'
        mobdq__qzhhn += (
            '  return init_multi_index(({},), I._names, I._name)\n'.format(
            ', '.join(f'ensure_contig_if_np(data[{jyd__gzn}][ind])' for
            jyd__gzn in range(tzzjw__ajuvp))))
        nhsa__gamlh = {}
        exec(mobdq__qzhhn, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, nhsa__gamlh)
        nwdqu__git = nhsa__gamlh['impl']
        return nwdqu__git


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    bpns__vus, swofm__wfyn = sig.args
    if bpns__vus != swofm__wfyn:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
