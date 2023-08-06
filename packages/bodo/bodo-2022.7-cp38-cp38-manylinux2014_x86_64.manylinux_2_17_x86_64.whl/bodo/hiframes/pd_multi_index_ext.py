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
        osx__pia = [('data', types.Tuple(fe_type.array_types)), ('names',
            types.Tuple(fe_type.names_typ)), ('name', fe_type.name_typ)]
        super(MultiIndexModel, self).__init__(dmm, fe_type, osx__pia)


make_attribute_wrapper(MultiIndexType, 'data', '_data')
make_attribute_wrapper(MultiIndexType, 'names', '_names')
make_attribute_wrapper(MultiIndexType, 'name', '_name')


@typeof_impl.register(pd.MultiIndex)
def typeof_multi_index(val, c):
    array_types = tuple(numba.typeof(val.levels[wyxay__ludsc].values) for
        wyxay__ludsc in range(val.nlevels))
    return MultiIndexType(array_types, tuple(get_val_type_maybe_str_literal
        (lwkq__xwsmn) for lwkq__xwsmn in val.names), numba.typeof(val.name))


@box(MultiIndexType)
def box_multi_index(typ, val, c):
    llw__bmmj = c.context.insert_const_string(c.builder.module, 'pandas')
    nlyfx__yqwtr = c.pyapi.import_module_noblock(llw__bmmj)
    gkk__cem = c.pyapi.object_getattr_string(nlyfx__yqwtr, 'MultiIndex')
    grkxp__fjzsp = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Tuple(typ.array_types),
        grkxp__fjzsp.data)
    foxz__swhs = c.pyapi.from_native_value(types.Tuple(typ.array_types),
        grkxp__fjzsp.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Tuple(typ.names_typ),
        grkxp__fjzsp.names)
    muypz__snmli = c.pyapi.from_native_value(types.Tuple(typ.names_typ),
        grkxp__fjzsp.names, c.env_manager)
    c.context.nrt.incref(c.builder, typ.name_typ, grkxp__fjzsp.name)
    yochm__hux = c.pyapi.from_native_value(typ.name_typ, grkxp__fjzsp.name,
        c.env_manager)
    pdl__wqc = c.pyapi.borrow_none()
    wwe__qfp = c.pyapi.call_method(gkk__cem, 'from_arrays', (foxz__swhs,
        pdl__wqc, muypz__snmli))
    c.pyapi.object_setattr_string(wwe__qfp, 'name', yochm__hux)
    c.pyapi.decref(foxz__swhs)
    c.pyapi.decref(muypz__snmli)
    c.pyapi.decref(yochm__hux)
    c.pyapi.decref(nlyfx__yqwtr)
    c.pyapi.decref(gkk__cem)
    c.context.nrt.decref(c.builder, typ, val)
    return wwe__qfp


@unbox(MultiIndexType)
def unbox_multi_index(typ, val, c):
    wjy__zvasn = []
    rul__hqwki = []
    for wyxay__ludsc in range(typ.nlevels):
        fizii__bam = c.pyapi.unserialize(c.pyapi.serialize_object(wyxay__ludsc)
            )
        sdd__fvykq = c.pyapi.call_method(val, 'get_level_values', (fizii__bam,)
            )
        kuka__hda = c.pyapi.object_getattr_string(sdd__fvykq, 'values')
        c.pyapi.decref(sdd__fvykq)
        c.pyapi.decref(fizii__bam)
        vxke__huxqz = c.pyapi.to_native_value(typ.array_types[wyxay__ludsc],
            kuka__hda).value
        wjy__zvasn.append(vxke__huxqz)
        rul__hqwki.append(kuka__hda)
    if isinstance(types.Tuple(typ.array_types), types.UniTuple):
        data = cgutils.pack_array(c.builder, wjy__zvasn)
    else:
        data = cgutils.pack_struct(c.builder, wjy__zvasn)
    muypz__snmli = c.pyapi.object_getattr_string(val, 'names')
    zbi__nrhl = c.pyapi.unserialize(c.pyapi.serialize_object(tuple))
    bbo__nbjfa = c.pyapi.call_function_objargs(zbi__nrhl, (muypz__snmli,))
    names = c.pyapi.to_native_value(types.Tuple(typ.names_typ), bbo__nbjfa
        ).value
    yochm__hux = c.pyapi.object_getattr_string(val, 'name')
    name = c.pyapi.to_native_value(typ.name_typ, yochm__hux).value
    grkxp__fjzsp = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    grkxp__fjzsp.data = data
    grkxp__fjzsp.names = names
    grkxp__fjzsp.name = name
    for kuka__hda in rul__hqwki:
        c.pyapi.decref(kuka__hda)
    c.pyapi.decref(muypz__snmli)
    c.pyapi.decref(zbi__nrhl)
    c.pyapi.decref(bbo__nbjfa)
    c.pyapi.decref(yochm__hux)
    return NativeValue(grkxp__fjzsp._getvalue())


def from_product_error_checking(iterables, sortorder, names):
    sgcv__owusr = 'pandas.MultiIndex.from_product'
    eithh__necv = dict(sortorder=sortorder)
    vty__mqg = dict(sortorder=None)
    check_unsupported_args(sgcv__owusr, eithh__necv, vty__mqg, package_name
        ='pandas', module_name='Index')
    if not (is_overload_none(names) or isinstance(names, types.BaseTuple)):
        raise BodoError(f'{sgcv__owusr}: names must be None or a tuple.')
    elif not isinstance(iterables, types.BaseTuple):
        raise BodoError(f'{sgcv__owusr}: iterables must be a tuple.')
    elif not is_overload_none(names) and len(iterables) != len(names):
        raise BodoError(
            f'{sgcv__owusr}: iterables and names must be of the same length.')


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
    qsvg__qkk = MultiIndexType(array_types, names_typ)
    upqb__jzm = f'from_product_multiindex{numba.core.ir_utils.next_label()}'
    setattr(types, upqb__jzm, qsvg__qkk)
    iei__ednxq = f"""
def impl(iterables, sortorder=None, names=None):
    with numba.objmode(mi='{upqb__jzm}'):
        mi = pd.MultiIndex.from_product(iterables, names=names)
    return mi
"""
    dki__xharb = {}
    exec(iei__ednxq, globals(), dki__xharb)
    npkif__kjk = dki__xharb['impl']
    return npkif__kjk


@intrinsic
def init_multi_index(typingctx, data, names, name=None):
    name = types.none if name is None else name
    names = types.Tuple(names.types)

    def codegen(context, builder, signature, args):
        rsyus__vipuw, levmo__wgho, jxmtm__kbgo = args
        odm__wqwfh = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        odm__wqwfh.data = rsyus__vipuw
        odm__wqwfh.names = levmo__wgho
        odm__wqwfh.name = jxmtm__kbgo
        context.nrt.incref(builder, signature.args[0], rsyus__vipuw)
        context.nrt.incref(builder, signature.args[1], levmo__wgho)
        context.nrt.incref(builder, signature.args[2], jxmtm__kbgo)
        return odm__wqwfh._getvalue()
    cgzz__biuac = MultiIndexType(data.types, names.types, name)
    return cgzz__biuac(data, names, name), codegen


@overload(len, no_unliteral=True)
def overload_len_pd_multiindex(A):
    if isinstance(A, MultiIndexType):
        return lambda A: len(A._data[0])


@overload(operator.getitem, no_unliteral=True)
def overload_multi_index_getitem(I, ind):
    if not isinstance(I, MultiIndexType):
        return
    if not isinstance(ind, types.Integer):
        yrmw__unb = len(I.array_types)
        iei__ednxq = 'def impl(I, ind):\n'
        iei__ednxq += '  data = I._data\n'
        iei__ednxq += ('  return init_multi_index(({},), I._names, I._name)\n'
            .format(', '.join(
            f'ensure_contig_if_np(data[{wyxay__ludsc}][ind])' for
            wyxay__ludsc in range(yrmw__unb))))
        dki__xharb = {}
        exec(iei__ednxq, {'init_multi_index': init_multi_index,
            'ensure_contig_if_np': ensure_contig_if_np}, dki__xharb)
        npkif__kjk = dki__xharb['impl']
        return npkif__kjk


@lower_builtin(operator.is_, MultiIndexType, MultiIndexType)
def multi_index_is(context, builder, sig, args):
    xadt__ljvli, guzue__wqpy = sig.args
    if xadt__ljvli != guzue__wqpy:
        return cgutils.false_bit

    def index_is_impl(a, b):
        return (a._data is b._data and a._names is b._names and a._name is
            b._name)
    return context.compile_internal(builder, index_is_impl, sig, args)
