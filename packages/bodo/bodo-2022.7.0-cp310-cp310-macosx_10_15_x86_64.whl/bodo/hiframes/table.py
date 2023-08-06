"""Table data type for storing dataframe column arrays. Supports storing many columns
(e.g. >10k) efficiently.
"""
import operator
from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.ir_utils import guard
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_getattr, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from numba.np.arrayobj import _getitem_array_single_int
from numba.parfors.array_analysis import ArrayAnalysis
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.typing import BodoError, MetaType, decode_if_dict_array, get_overload_const_int, is_list_like_index_type, is_overload_constant_bool, is_overload_constant_int, is_overload_none, is_overload_true, raise_bodo_error, to_str_arr_if_dict_array, unwrap_typeref
from bodo.utils.utils import is_whole_slice


class Table:

    def __init__(self, arrs, usecols=None, num_arrs=-1):
        if usecols is not None:
            assert num_arrs != -1, 'num_arrs must be provided if usecols is not None'
            tyz__qmaiz = 0
            nxyks__wlj = []
            for i in range(usecols[-1] + 1):
                if i == usecols[tyz__qmaiz]:
                    nxyks__wlj.append(arrs[tyz__qmaiz])
                    tyz__qmaiz += 1
                else:
                    nxyks__wlj.append(None)
            for kxql__zfgnu in range(usecols[-1] + 1, num_arrs):
                nxyks__wlj.append(None)
            self.arrays = nxyks__wlj
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((viut__srs == xsq__fbqqc).all() for viut__srs,
            xsq__fbqqc in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        faa__fgsyw = len(self.arrays)
        rkg__vcvy = dict(zip(range(faa__fgsyw), self.arrays))
        df = pd.DataFrame(rkg__vcvy, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        qxkx__lgmlg = []
        qxd__hjqn = []
        uioug__jwi = {}
        pbi__exu = {}
        klm__qrhvi = defaultdict(int)
        eef__ueq = defaultdict(list)
        if not has_runtime_cols:
            for i, egbab__pfjm in enumerate(arr_types):
                if egbab__pfjm not in uioug__jwi:
                    jir__gbdi = len(uioug__jwi)
                    uioug__jwi[egbab__pfjm] = jir__gbdi
                    pbi__exu[jir__gbdi] = egbab__pfjm
                zrkev__ihynj = uioug__jwi[egbab__pfjm]
                qxkx__lgmlg.append(zrkev__ihynj)
                qxd__hjqn.append(klm__qrhvi[zrkev__ihynj])
                klm__qrhvi[zrkev__ihynj] += 1
                eef__ueq[zrkev__ihynj].append(i)
        self.block_nums = qxkx__lgmlg
        self.block_offsets = qxd__hjqn
        self.type_to_blk = uioug__jwi
        self.blk_to_type = pbi__exu
        self.block_to_arr_ind = eef__ueq
        super(TableType, self).__init__(name=
            f'TableType({arr_types}, {has_runtime_cols})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return self.arr_types, self.has_runtime_cols

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(Table)
def typeof_table(val, c):
    return TableType(tuple(numba.typeof(arr) for arr in val.arrays))


@register_model(TableType)
class TableTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        if fe_type.has_runtime_cols:
            dqyxx__iqkrm = [(f'block_{i}', types.List(egbab__pfjm)) for i,
                egbab__pfjm in enumerate(fe_type.arr_types)]
        else:
            dqyxx__iqkrm = [(f'block_{zrkev__ihynj}', types.List(
                egbab__pfjm)) for egbab__pfjm, zrkev__ihynj in fe_type.
                type_to_blk.items()]
        dqyxx__iqkrm.append(('parent', types.pyobject))
        dqyxx__iqkrm.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, dqyxx__iqkrm)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    diitw__bdia = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    iqks__jhsjr = c.pyapi.make_none()
    tty__ozs = c.context.get_constant(types.int64, 0)
    pnggw__jdvye = cgutils.alloca_once_value(c.builder, tty__ozs)
    for egbab__pfjm, zrkev__ihynj in typ.type_to_blk.items():
        lwoaa__pgmq = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[zrkev__ihynj]))
        kxql__zfgnu, jcbsx__khkfi = ListInstance.allocate_ex(c.context, c.
            builder, types.List(egbab__pfjm), lwoaa__pgmq)
        jcbsx__khkfi.size = lwoaa__pgmq
        lfj__szn = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            zrkev__ihynj], dtype=np.int64))
        ocmuq__cgk = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, lfj__szn)
        with cgutils.for_range(c.builder, lwoaa__pgmq) as jcdn__rnv:
            i = jcdn__rnv.index
            zro__dwhr = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), ocmuq__cgk, i)
            bawki__tiu = c.pyapi.long_from_longlong(zro__dwhr)
            qiu__gth = c.pyapi.object_getitem(diitw__bdia, bawki__tiu)
            ara__hstbr = c.builder.icmp_unsigned('==', qiu__gth, iqks__jhsjr)
            with c.builder.if_else(ara__hstbr) as (pny__czfro, aobjz__mbk):
                with pny__czfro:
                    vlof__iyg = c.context.get_constant_null(egbab__pfjm)
                    jcbsx__khkfi.inititem(i, vlof__iyg, incref=False)
                with aobjz__mbk:
                    qyqlr__ymsy = c.pyapi.call_method(qiu__gth, '__len__', ())
                    ihkx__zdz = c.pyapi.long_as_longlong(qyqlr__ymsy)
                    c.builder.store(ihkx__zdz, pnggw__jdvye)
                    c.pyapi.decref(qyqlr__ymsy)
                    arr = c.pyapi.to_native_value(egbab__pfjm, qiu__gth).value
                    jcbsx__khkfi.inititem(i, arr, incref=False)
            c.pyapi.decref(qiu__gth)
            c.pyapi.decref(bawki__tiu)
        setattr(table, f'block_{zrkev__ihynj}', jcbsx__khkfi.value)
    table.len = c.builder.load(pnggw__jdvye)
    c.pyapi.decref(diitw__bdia)
    c.pyapi.decref(iqks__jhsjr)
    nxovs__mon = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=nxovs__mon)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        pwz__zuz = c.context.get_constant(types.int64, 0)
        for i, egbab__pfjm in enumerate(typ.arr_types):
            nxyks__wlj = getattr(table, f'block_{i}')
            hngbn__mbs = ListInstance(c.context, c.builder, types.List(
                egbab__pfjm), nxyks__wlj)
            pwz__zuz = c.builder.add(pwz__zuz, hngbn__mbs.size)
        sytdn__gbw = c.pyapi.list_new(pwz__zuz)
        hmeyu__vim = c.context.get_constant(types.int64, 0)
        for i, egbab__pfjm in enumerate(typ.arr_types):
            nxyks__wlj = getattr(table, f'block_{i}')
            hngbn__mbs = ListInstance(c.context, c.builder, types.List(
                egbab__pfjm), nxyks__wlj)
            with cgutils.for_range(c.builder, hngbn__mbs.size) as jcdn__rnv:
                i = jcdn__rnv.index
                arr = hngbn__mbs.getitem(i)
                c.context.nrt.incref(c.builder, egbab__pfjm, arr)
                idx = c.builder.add(hmeyu__vim, i)
                c.pyapi.list_setitem(sytdn__gbw, idx, c.pyapi.
                    from_native_value(egbab__pfjm, arr, c.env_manager))
            hmeyu__vim = c.builder.add(hmeyu__vim, hngbn__mbs.size)
        ivwno__nhe = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        hyw__olq = c.pyapi.call_function_objargs(ivwno__nhe, (sytdn__gbw,))
        c.pyapi.decref(ivwno__nhe)
        c.pyapi.decref(sytdn__gbw)
        c.context.nrt.decref(c.builder, typ, val)
        return hyw__olq
    sytdn__gbw = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    eggb__qdgo = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for egbab__pfjm, zrkev__ihynj in typ.type_to_blk.items():
        nxyks__wlj = getattr(table, f'block_{zrkev__ihynj}')
        hngbn__mbs = ListInstance(c.context, c.builder, types.List(
            egbab__pfjm), nxyks__wlj)
        lfj__szn = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            zrkev__ihynj], dtype=np.int64))
        ocmuq__cgk = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, lfj__szn)
        with cgutils.for_range(c.builder, hngbn__mbs.size) as jcdn__rnv:
            i = jcdn__rnv.index
            zro__dwhr = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), ocmuq__cgk, i)
            arr = hngbn__mbs.getitem(i)
            ibaet__iumiv = cgutils.alloca_once_value(c.builder, arr)
            icnau__ncar = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(egbab__pfjm))
            is_null = is_ll_eq(c.builder, ibaet__iumiv, icnau__ncar)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (pny__czfro, aobjz__mbk):
                with pny__czfro:
                    iqks__jhsjr = c.pyapi.make_none()
                    c.pyapi.list_setitem(sytdn__gbw, zro__dwhr, iqks__jhsjr)
                with aobjz__mbk:
                    qiu__gth = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, eggb__qdgo)
                        ) as (axexo__nvuu, vfoi__wyyfg):
                        with axexo__nvuu:
                            pryle__tmdei = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                zro__dwhr, egbab__pfjm)
                            c.builder.store(pryle__tmdei, qiu__gth)
                        with vfoi__wyyfg:
                            c.context.nrt.incref(c.builder, egbab__pfjm, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                egbab__pfjm, arr, c.env_manager), qiu__gth)
                    c.pyapi.list_setitem(sytdn__gbw, zro__dwhr, c.builder.
                        load(qiu__gth))
    ivwno__nhe = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    hyw__olq = c.pyapi.call_function_objargs(ivwno__nhe, (sytdn__gbw,))
    c.pyapi.decref(ivwno__nhe)
    c.pyapi.decref(sytdn__gbw)
    c.context.nrt.decref(c.builder, typ, val)
    return hyw__olq


@lower_builtin(len, TableType)
def table_len_lower(context, builder, sig, args):
    impl = table_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def table_len_overload(T):
    if not isinstance(T, TableType):
        return

    def impl(T):
        return T._len
    return impl


@lower_getattr(TableType, 'shape')
def lower_table_shape(context, builder, typ, val):
    impl = table_shape_overload(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def table_shape_overload(T):
    if T.has_runtime_cols:

        def impl(T):
            return T._len, compute_num_runtime_columns(T)
        return impl
    ncols = len(T.arr_types)
    return lambda T: (T._len, types.int64(ncols))


@intrinsic
def compute_num_runtime_columns(typingctx, table_type):
    assert isinstance(table_type, TableType)

    def codegen(context, builder, sig, args):
        table_arg, = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        jkzl__rgxq = context.get_constant(types.int64, 0)
        for i, egbab__pfjm in enumerate(table_type.arr_types):
            nxyks__wlj = getattr(table, f'block_{i}')
            hngbn__mbs = ListInstance(context, builder, types.List(
                egbab__pfjm), nxyks__wlj)
            jkzl__rgxq = builder.add(jkzl__rgxq, hngbn__mbs.size)
        return jkzl__rgxq
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    zrkev__ihynj = table_type.block_nums[col_ind]
    chija__rklk = table_type.block_offsets[col_ind]
    nxyks__wlj = getattr(table, f'block_{zrkev__ihynj}')
    dnzxj__wlw = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    htrig__wzkcj = context.get_constant(types.int64, col_ind)
    wcd__nei = context.get_constant(types.int64, chija__rklk)
    mpz__jqkg = table_arg, nxyks__wlj, wcd__nei, htrig__wzkcj
    ensure_column_unboxed_codegen(context, builder, dnzxj__wlw, mpz__jqkg)
    hngbn__mbs = ListInstance(context, builder, types.List(arr_type),
        nxyks__wlj)
    arr = hngbn__mbs.getitem(chija__rklk)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, kxql__zfgnu = args
        arr = get_table_data_codegen(context, builder, table_arg, col_ind,
            table_type)
        return impl_ret_borrowed(context, builder, arr_type, arr)
    sig = arr_type(table_type, ind_typ)
    return sig, codegen


@intrinsic
def del_column(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType
        ), 'Can only delete columns from a table'
    assert isinstance(ind_typ, types.TypeRef) and isinstance(ind_typ.
        instance_type, MetaType), 'ind_typ must be a typeref for a meta type'
    vimts__xor = list(ind_typ.instance_type.meta)
    vfx__awk = defaultdict(list)
    for ind in vimts__xor:
        vfx__awk[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, kxql__zfgnu = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for zrkev__ihynj, fhyy__nsl in vfx__awk.items():
            arr_type = table_type.blk_to_type[zrkev__ihynj]
            nxyks__wlj = getattr(table, f'block_{zrkev__ihynj}')
            hngbn__mbs = ListInstance(context, builder, types.List(arr_type
                ), nxyks__wlj)
            vlof__iyg = context.get_constant_null(arr_type)
            if len(fhyy__nsl) == 1:
                chija__rklk = fhyy__nsl[0]
                arr = hngbn__mbs.getitem(chija__rklk)
                context.nrt.decref(builder, arr_type, arr)
                hngbn__mbs.inititem(chija__rklk, vlof__iyg, incref=False)
            else:
                lwoaa__pgmq = context.get_constant(types.int64, len(fhyy__nsl))
                qbatr__ooy = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(fhyy__nsl, dtype=
                    np.int64))
                avvx__lcm = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, qbatr__ooy)
                with cgutils.for_range(builder, lwoaa__pgmq) as jcdn__rnv:
                    i = jcdn__rnv.index
                    chija__rklk = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), avvx__lcm, i)
                    arr = hngbn__mbs.getitem(chija__rklk)
                    context.nrt.decref(builder, arr_type, arr)
                    hngbn__mbs.inititem(chija__rklk, vlof__iyg, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    tty__ozs = context.get_constant(types.int64, 0)
    yewfj__szyyg = context.get_constant(types.int64, 1)
    elai__wav = arr_type not in in_table_type.type_to_blk
    for egbab__pfjm, zrkev__ihynj in out_table_type.type_to_blk.items():
        if egbab__pfjm in in_table_type.type_to_blk:
            vas__kvy = in_table_type.type_to_blk[egbab__pfjm]
            jcbsx__khkfi = ListInstance(context, builder, types.List(
                egbab__pfjm), getattr(in_table, f'block_{vas__kvy}'))
            context.nrt.incref(builder, types.List(egbab__pfjm),
                jcbsx__khkfi.value)
            setattr(out_table, f'block_{zrkev__ihynj}', jcbsx__khkfi.value)
    if elai__wav:
        kxql__zfgnu, jcbsx__khkfi = ListInstance.allocate_ex(context,
            builder, types.List(arr_type), yewfj__szyyg)
        jcbsx__khkfi.size = yewfj__szyyg
        jcbsx__khkfi.inititem(tty__ozs, arr_arg, incref=True)
        zrkev__ihynj = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{zrkev__ihynj}', jcbsx__khkfi.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        zrkev__ihynj = out_table_type.type_to_blk[arr_type]
        jcbsx__khkfi = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{zrkev__ihynj}'))
        if is_new_col:
            n = jcbsx__khkfi.size
            bnmat__ekajx = builder.add(n, yewfj__szyyg)
            jcbsx__khkfi.resize(bnmat__ekajx)
            jcbsx__khkfi.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            dhr__qpb = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            jcbsx__khkfi.setitem(dhr__qpb, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            dhr__qpb = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = jcbsx__khkfi.size
            bnmat__ekajx = builder.add(n, yewfj__szyyg)
            jcbsx__khkfi.resize(bnmat__ekajx)
            context.nrt.incref(builder, arr_type, jcbsx__khkfi.getitem(
                dhr__qpb))
            jcbsx__khkfi.move(builder.add(dhr__qpb, yewfj__szyyg), dhr__qpb,
                builder.sub(n, dhr__qpb))
            jcbsx__khkfi.setitem(dhr__qpb, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    yvwtm__xsnv = in_table_type.arr_types[col_ind]
    if yvwtm__xsnv in out_table_type.type_to_blk:
        zrkev__ihynj = out_table_type.type_to_blk[yvwtm__xsnv]
        ndqa__ztqrb = getattr(out_table, f'block_{zrkev__ihynj}')
        ujw__ygi = types.List(yvwtm__xsnv)
        dhr__qpb = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        fwztw__ibq = ujw__ygi.dtype(ujw__ygi, types.intp)
        ygtm__milp = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), fwztw__ibq, (ndqa__ztqrb, dhr__qpb))
        context.nrt.decref(builder, yvwtm__xsnv, ygtm__milp)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    uvu__ewjz = list(table.arr_types)
    if ind == len(uvu__ewjz):
        utnbg__vke = None
        uvu__ewjz.append(arr_type)
    else:
        utnbg__vke = table.arr_types[ind]
        uvu__ewjz[ind] = arr_type
    xzdkh__lxlb = TableType(tuple(uvu__ewjz))
    kzisj__tpo = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': xzdkh__lxlb}
    swszw__aevv = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    swszw__aevv += f'  T2 = init_table(out_table_typ, False)\n'
    swszw__aevv += f'  T2 = set_table_len(T2, len(table))\n'
    swszw__aevv += f'  T2 = set_table_parent(T2, table)\n'
    for typ, zrkev__ihynj in xzdkh__lxlb.type_to_blk.items():
        if typ in table.type_to_blk:
            lvlt__dlrho = table.type_to_blk[typ]
            swszw__aevv += (
                f'  arr_list_{zrkev__ihynj} = get_table_block(table, {lvlt__dlrho})\n'
                )
            swszw__aevv += f"""  out_arr_list_{zrkev__ihynj} = alloc_list_like(arr_list_{zrkev__ihynj}, {len(xzdkh__lxlb.block_to_arr_ind[zrkev__ihynj])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[lvlt__dlrho]
                ) & used_cols:
                swszw__aevv += (
                    f'  for i in range(len(arr_list_{zrkev__ihynj})):\n')
                if typ not in (utnbg__vke, arr_type):
                    swszw__aevv += f"""    out_arr_list_{zrkev__ihynj}[i] = arr_list_{zrkev__ihynj}[i]
"""
                else:
                    gei__gcg = table.block_to_arr_ind[lvlt__dlrho]
                    eoa__jviw = np.empty(len(gei__gcg), np.int64)
                    yihx__hwc = False
                    for tstrm__gbz, zro__dwhr in enumerate(gei__gcg):
                        if zro__dwhr != ind:
                            tjot__xxzh = xzdkh__lxlb.block_offsets[zro__dwhr]
                        else:
                            tjot__xxzh = -1
                            yihx__hwc = True
                        eoa__jviw[tstrm__gbz] = tjot__xxzh
                    kzisj__tpo[f'out_idxs_{zrkev__ihynj}'] = np.array(eoa__jviw
                        , np.int64)
                    swszw__aevv += (
                        f'    out_idx = out_idxs_{zrkev__ihynj}[i]\n')
                    if yihx__hwc:
                        swszw__aevv += f'    if out_idx == -1:\n'
                        swszw__aevv += f'      continue\n'
                    swszw__aevv += f"""    out_arr_list_{zrkev__ihynj}[out_idx] = arr_list_{zrkev__ihynj}[i]
"""
            if typ == arr_type and not is_null:
                swszw__aevv += f"""  out_arr_list_{zrkev__ihynj}[{xzdkh__lxlb.block_offsets[ind]}] = arr
"""
        else:
            kzisj__tpo[f'arr_list_typ_{zrkev__ihynj}'] = types.List(arr_type)
            swszw__aevv += f"""  out_arr_list_{zrkev__ihynj} = alloc_list_like(arr_list_typ_{zrkev__ihynj}, 1, False)
"""
            if not is_null:
                swszw__aevv += f'  out_arr_list_{zrkev__ihynj}[0] = arr\n'
        swszw__aevv += (
            f'  T2 = set_table_block(T2, out_arr_list_{zrkev__ihynj}, {zrkev__ihynj})\n'
            )
    swszw__aevv += f'  return T2\n'
    fglw__zhx = {}
    exec(swszw__aevv, kzisj__tpo, fglw__zhx)
    return fglw__zhx['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        rml__ovyr = None
    else:
        rml__ovyr = set(used_cols.instance_type.meta)
    yop__jhfkg = get_overload_const_int(ind)
    return generate_set_table_data_code(table, yop__jhfkg, arr, rml__ovyr)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    yop__jhfkg = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        rml__ovyr = None
    else:
        rml__ovyr = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, yop__jhfkg, arr_type,
        rml__ovyr, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    jfb__lyj = args[0]
    if equiv_set.has_shape(jfb__lyj):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            jfb__lyj)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    ajwe__pgds = []
    for egbab__pfjm, zrkev__ihynj in table_type.type_to_blk.items():
        uawpu__lpk = len(table_type.block_to_arr_ind[zrkev__ihynj])
        qiwwp__xqvr = []
        for i in range(uawpu__lpk):
            zro__dwhr = table_type.block_to_arr_ind[zrkev__ihynj][i]
            qiwwp__xqvr.append(pyval.arrays[zro__dwhr])
        ajwe__pgds.append(context.get_constant_generic(builder, types.List(
            egbab__pfjm), qiwwp__xqvr))
    bzw__qecnh = context.get_constant_null(types.pyobject)
    crufp__zacwc = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(ajwe__pgds + [bzw__qecnh, crufp__zacwc])


@intrinsic
def init_table(typingctx, table_type, to_str_if_dict_t):
    out_table_type = table_type.instance_type if isinstance(table_type,
        types.TypeRef) else table_type
    assert isinstance(out_table_type, TableType
        ), 'table type or typeref expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        out_table_type = to_str_arr_if_dict_array(out_table_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(out_table_type)(context, builder)
        for egbab__pfjm, zrkev__ihynj in out_table_type.type_to_blk.items():
            oukow__hymr = context.get_constant_null(types.List(egbab__pfjm))
            setattr(table, f'block_{zrkev__ihynj}', oukow__hymr)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    jkf__gnen = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        jkf__gnen[typ.dtype] = i
    uoio__tyln = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(uoio__tyln, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        auv__hbme, kxql__zfgnu = args
        table = cgutils.create_struct_proxy(uoio__tyln)(context, builder)
        for egbab__pfjm, zrkev__ihynj in uoio__tyln.type_to_blk.items():
            idx = jkf__gnen[egbab__pfjm]
            xkhab__rsq = signature(types.List(egbab__pfjm),
                tuple_of_lists_type, types.literal(idx))
            oxl__yoa = auv__hbme, idx
            geet__ooqsp = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, xkhab__rsq, oxl__yoa)
            setattr(table, f'block_{zrkev__ihynj}', geet__ooqsp)
        return table._getvalue()
    sig = uoio__tyln(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    zrkev__ihynj = get_overload_const_int(blk_type)
    arr_type = None
    for egbab__pfjm, xsq__fbqqc in table_type.type_to_blk.items():
        if xsq__fbqqc == zrkev__ihynj:
            arr_type = egbab__pfjm
            break
    assert arr_type is not None, 'invalid table type block'
    davxn__tgrrh = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        nxyks__wlj = getattr(table, f'block_{zrkev__ihynj}')
        return impl_ret_borrowed(context, builder, davxn__tgrrh, nxyks__wlj)
    sig = davxn__tgrrh(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, mxg__tys = args
        ico__hutuv = context.get_python_api(builder)
        ippp__tyzw = used_cols_typ == types.none
        if not ippp__tyzw:
            znd__xmeu = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), mxg__tys)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for egbab__pfjm, zrkev__ihynj in table_type.type_to_blk.items():
            lwoaa__pgmq = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[zrkev__ihynj]))
            lfj__szn = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                zrkev__ihynj], dtype=np.int64))
            ocmuq__cgk = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, lfj__szn)
            nxyks__wlj = getattr(table, f'block_{zrkev__ihynj}')
            with cgutils.for_range(builder, lwoaa__pgmq) as jcdn__rnv:
                i = jcdn__rnv.index
                zro__dwhr = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    ocmuq__cgk, i)
                dnzxj__wlw = types.none(table_type, types.List(egbab__pfjm),
                    types.int64, types.int64)
                mpz__jqkg = table_arg, nxyks__wlj, i, zro__dwhr
                if ippp__tyzw:
                    ensure_column_unboxed_codegen(context, builder,
                        dnzxj__wlw, mpz__jqkg)
                else:
                    sjiwa__sic = znd__xmeu.contains(zro__dwhr)
                    with builder.if_then(sjiwa__sic):
                        ensure_column_unboxed_codegen(context, builder,
                            dnzxj__wlw, mpz__jqkg)
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, used_cols_typ)
    return sig, codegen


@intrinsic
def ensure_column_unboxed(typingctx, table_type, arr_list_t, ind_t, arr_ind_t):
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, arr_list_t, ind_t, arr_ind_t)
    return sig, ensure_column_unboxed_codegen


def ensure_column_unboxed_codegen(context, builder, sig, args):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table_arg, cle__ijv, zncst__yqco, dcho__pahy = args
    ico__hutuv = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    eggb__qdgo = cgutils.is_not_null(builder, table.parent)
    hngbn__mbs = ListInstance(context, builder, sig.args[1], cle__ijv)
    bygaq__bgdz = hngbn__mbs.getitem(zncst__yqco)
    ibaet__iumiv = cgutils.alloca_once_value(builder, bygaq__bgdz)
    icnau__ncar = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, ibaet__iumiv, icnau__ncar)
    with builder.if_then(is_null):
        with builder.if_else(eggb__qdgo) as (pny__czfro, aobjz__mbk):
            with pny__czfro:
                qiu__gth = get_df_obj_column_codegen(context, builder,
                    ico__hutuv, table.parent, dcho__pahy, sig.args[1].dtype)
                arr = ico__hutuv.to_native_value(sig.args[1].dtype, qiu__gth
                    ).value
                hngbn__mbs.inititem(zncst__yqco, arr, incref=False)
                ico__hutuv.decref(qiu__gth)
            with aobjz__mbk:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    zrkev__ihynj = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, oiz__reya, kxql__zfgnu = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{zrkev__ihynj}', oiz__reya)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, sbuqx__fza = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = sbuqx__fza
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        ppmyo__rpr, hhyz__ljp = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, hhyz__ljp)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, ppmyo__rpr)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    davxn__tgrrh = list_type.instance_type if isinstance(list_type, types.
        TypeRef) else list_type
    assert isinstance(davxn__tgrrh, types.List
        ), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        davxn__tgrrh = types.List(to_str_arr_if_dict_array(davxn__tgrrh.dtype))

    def codegen(context, builder, sig, args):
        opcrb__njy = args[1]
        kxql__zfgnu, jcbsx__khkfi = ListInstance.allocate_ex(context,
            builder, davxn__tgrrh, opcrb__njy)
        jcbsx__khkfi.size = opcrb__njy
        return jcbsx__khkfi.value
    sig = davxn__tgrrh(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    ncnz__ikka = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(ncnz__ikka)

    def codegen(context, builder, sig, args):
        opcrb__njy, kxql__zfgnu = args
        kxql__zfgnu, jcbsx__khkfi = ListInstance.allocate_ex(context,
            builder, list_type, opcrb__njy)
        jcbsx__khkfi.size = opcrb__njy
        return jcbsx__khkfi.value
    sig = list_type(size_typ, data_typ)
    return sig, codegen


def _get_idx_length(idx):
    pass


@overload(_get_idx_length)
def overload_get_idx_length(idx, n):
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        return lambda idx, n: idx.sum()
    assert isinstance(idx, types.SliceType), 'slice index expected'

    def impl(idx, n):
        hoy__dyno = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(hoy__dyno)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    kzisj__tpo = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        mubq__wtkv = used_cols.instance_type
        wmnuz__oph = np.array(mubq__wtkv.meta, dtype=np.int64)
        kzisj__tpo['used_cols_vals'] = wmnuz__oph
        fxoda__mxm = set([T.block_nums[i] for i in wmnuz__oph])
    else:
        wmnuz__oph = None
    swszw__aevv = 'def table_filter_func(T, idx, used_cols=None):\n'
    swszw__aevv += f'  T2 = init_table(T, False)\n'
    swszw__aevv += f'  l = 0\n'
    if wmnuz__oph is not None and len(wmnuz__oph) == 0:
        swszw__aevv += f'  l = _get_idx_length(idx, len(T))\n'
        swszw__aevv += f'  T2 = set_table_len(T2, l)\n'
        swszw__aevv += f'  return T2\n'
        fglw__zhx = {}
        exec(swszw__aevv, kzisj__tpo, fglw__zhx)
        return fglw__zhx['table_filter_func']
    if wmnuz__oph is not None:
        swszw__aevv += f'  used_set = set(used_cols_vals)\n'
    for zrkev__ihynj in T.type_to_blk.values():
        swszw__aevv += (
            f'  arr_list_{zrkev__ihynj} = get_table_block(T, {zrkev__ihynj})\n'
            )
        swszw__aevv += f"""  out_arr_list_{zrkev__ihynj} = alloc_list_like(arr_list_{zrkev__ihynj}, len(arr_list_{zrkev__ihynj}), False)
"""
        if wmnuz__oph is None or zrkev__ihynj in fxoda__mxm:
            kzisj__tpo[f'arr_inds_{zrkev__ihynj}'] = np.array(T.
                block_to_arr_ind[zrkev__ihynj], dtype=np.int64)
            swszw__aevv += f'  for i in range(len(arr_list_{zrkev__ihynj})):\n'
            swszw__aevv += (
                f'    arr_ind_{zrkev__ihynj} = arr_inds_{zrkev__ihynj}[i]\n')
            if wmnuz__oph is not None:
                swszw__aevv += (
                    f'    if arr_ind_{zrkev__ihynj} not in used_set: continue\n'
                    )
            swszw__aevv += f"""    ensure_column_unboxed(T, arr_list_{zrkev__ihynj}, i, arr_ind_{zrkev__ihynj})
"""
            swszw__aevv += f"""    out_arr_{zrkev__ihynj} = ensure_contig_if_np(arr_list_{zrkev__ihynj}[i][idx])
"""
            swszw__aevv += f'    l = len(out_arr_{zrkev__ihynj})\n'
            swszw__aevv += (
                f'    out_arr_list_{zrkev__ihynj}[i] = out_arr_{zrkev__ihynj}\n'
                )
        swszw__aevv += (
            f'  T2 = set_table_block(T2, out_arr_list_{zrkev__ihynj}, {zrkev__ihynj})\n'
            )
    swszw__aevv += f'  T2 = set_table_len(T2, l)\n'
    swszw__aevv += f'  return T2\n'
    fglw__zhx = {}
    exec(swszw__aevv, kzisj__tpo, fglw__zhx)
    return fglw__zhx['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    cqza__amiiq = list(idx.instance_type.meta)
    uvu__ewjz = tuple(np.array(T.arr_types, dtype=object)[cqza__amiiq])
    xzdkh__lxlb = TableType(uvu__ewjz)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    pjgf__dqeri = is_overload_true(copy_arrs)
    kzisj__tpo = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': xzdkh__lxlb}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        rznw__toi = set(kept_cols)
        kzisj__tpo['kept_cols'] = np.array(kept_cols, np.int64)
        takxs__euv = True
    else:
        takxs__euv = False
    rmx__joeij = {i: c for i, c in enumerate(cqza__amiiq)}
    swszw__aevv = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    swszw__aevv += f'  T2 = init_table(out_table_typ, False)\n'
    swszw__aevv += f'  T2 = set_table_len(T2, len(T))\n'
    if takxs__euv and len(rznw__toi) == 0:
        swszw__aevv += f'  return T2\n'
        fglw__zhx = {}
        exec(swszw__aevv, kzisj__tpo, fglw__zhx)
        return fglw__zhx['table_subset']
    if takxs__euv:
        swszw__aevv += f'  kept_cols_set = set(kept_cols)\n'
    for typ, zrkev__ihynj in xzdkh__lxlb.type_to_blk.items():
        lvlt__dlrho = T.type_to_blk[typ]
        swszw__aevv += (
            f'  arr_list_{zrkev__ihynj} = get_table_block(T, {lvlt__dlrho})\n')
        swszw__aevv += f"""  out_arr_list_{zrkev__ihynj} = alloc_list_like(arr_list_{zrkev__ihynj}, {len(xzdkh__lxlb.block_to_arr_ind[zrkev__ihynj])}, False)
"""
        xpgk__gbti = True
        if takxs__euv:
            raim__qxnn = set(xzdkh__lxlb.block_to_arr_ind[zrkev__ihynj])
            ttc__czql = raim__qxnn & rznw__toi
            xpgk__gbti = len(ttc__czql) > 0
        if xpgk__gbti:
            kzisj__tpo[f'out_arr_inds_{zrkev__ihynj}'] = np.array(xzdkh__lxlb
                .block_to_arr_ind[zrkev__ihynj], dtype=np.int64)
            swszw__aevv += (
                f'  for i in range(len(out_arr_list_{zrkev__ihynj})):\n')
            swszw__aevv += (
                f'    out_arr_ind_{zrkev__ihynj} = out_arr_inds_{zrkev__ihynj}[i]\n'
                )
            if takxs__euv:
                swszw__aevv += (
                    f'    if out_arr_ind_{zrkev__ihynj} not in kept_cols_set: continue\n'
                    )
            plnn__danys = []
            hvh__wye = []
            for pmz__mhhzc in xzdkh__lxlb.block_to_arr_ind[zrkev__ihynj]:
                pht__ljh = rmx__joeij[pmz__mhhzc]
                plnn__danys.append(pht__ljh)
                fqibe__zfab = T.block_offsets[pht__ljh]
                hvh__wye.append(fqibe__zfab)
            kzisj__tpo[f'in_logical_idx_{zrkev__ihynj}'] = np.array(plnn__danys
                , dtype=np.int64)
            kzisj__tpo[f'in_physical_idx_{zrkev__ihynj}'] = np.array(hvh__wye,
                dtype=np.int64)
            swszw__aevv += (
                f'    logical_idx_{zrkev__ihynj} = in_logical_idx_{zrkev__ihynj}[i]\n'
                )
            swszw__aevv += (
                f'    physical_idx_{zrkev__ihynj} = in_physical_idx_{zrkev__ihynj}[i]\n'
                )
            swszw__aevv += f"""    ensure_column_unboxed(T, arr_list_{zrkev__ihynj}, physical_idx_{zrkev__ihynj}, logical_idx_{zrkev__ihynj})
"""
            ycj__kazk = '.copy()' if pjgf__dqeri else ''
            swszw__aevv += f"""    out_arr_list_{zrkev__ihynj}[i] = arr_list_{zrkev__ihynj}[physical_idx_{zrkev__ihynj}]{ycj__kazk}
"""
        swszw__aevv += (
            f'  T2 = set_table_block(T2, out_arr_list_{zrkev__ihynj}, {zrkev__ihynj})\n'
            )
    swszw__aevv += f'  return T2\n'
    fglw__zhx = {}
    exec(swszw__aevv, kzisj__tpo, fglw__zhx)
    return fglw__zhx['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    jfb__lyj = args[0]
    if equiv_set.has_shape(jfb__lyj):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=jfb__lyj, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (jfb__lyj)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    jfb__lyj = args[0]
    if equiv_set.has_shape(jfb__lyj):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            jfb__lyj)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    swszw__aevv = 'def impl(T):\n'
    swszw__aevv += f'  T2 = init_table(T, True)\n'
    swszw__aevv += f'  l = len(T)\n'
    kzisj__tpo = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for zrkev__ihynj in T.type_to_blk.values():
        kzisj__tpo[f'arr_inds_{zrkev__ihynj}'] = np.array(T.
            block_to_arr_ind[zrkev__ihynj], dtype=np.int64)
        swszw__aevv += (
            f'  arr_list_{zrkev__ihynj} = get_table_block(T, {zrkev__ihynj})\n'
            )
        swszw__aevv += f"""  out_arr_list_{zrkev__ihynj} = alloc_list_like(arr_list_{zrkev__ihynj}, len(arr_list_{zrkev__ihynj}), True)
"""
        swszw__aevv += f'  for i in range(len(arr_list_{zrkev__ihynj})):\n'
        swszw__aevv += (
            f'    arr_ind_{zrkev__ihynj} = arr_inds_{zrkev__ihynj}[i]\n')
        swszw__aevv += f"""    ensure_column_unboxed(T, arr_list_{zrkev__ihynj}, i, arr_ind_{zrkev__ihynj})
"""
        swszw__aevv += f"""    out_arr_{zrkev__ihynj} = decode_if_dict_array(arr_list_{zrkev__ihynj}[i])
"""
        swszw__aevv += (
            f'    out_arr_list_{zrkev__ihynj}[i] = out_arr_{zrkev__ihynj}\n')
        swszw__aevv += (
            f'  T2 = set_table_block(T2, out_arr_list_{zrkev__ihynj}, {zrkev__ihynj})\n'
            )
    swszw__aevv += f'  T2 = set_table_len(T2, l)\n'
    swszw__aevv += f'  return T2\n'
    fglw__zhx = {}
    exec(swszw__aevv, kzisj__tpo, fglw__zhx)
    return fglw__zhx['impl']


@overload(operator.getitem, no_unliteral=True, inline='always')
def overload_table_getitem(T, idx):
    if not isinstance(T, TableType):
        return
    return lambda T, idx: table_filter(T, idx)


@intrinsic
def init_runtime_table_from_lists(typingctx, arr_list_tup_typ, nrows_typ=None):
    assert isinstance(arr_list_tup_typ, types.BaseTuple
        ), 'init_runtime_table_from_lists requires a tuple of list of arrays'
    if isinstance(arr_list_tup_typ, types.UniTuple):
        if arr_list_tup_typ.dtype.dtype == types.undefined:
            return
        dkl__pudnq = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        dkl__pudnq = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            dkl__pudnq.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        vzqwv__ekxlw, icna__qfyu = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = icna__qfyu
        ajwe__pgds = cgutils.unpack_tuple(builder, vzqwv__ekxlw)
        for i, nxyks__wlj in enumerate(ajwe__pgds):
            setattr(table, f'block_{i}', nxyks__wlj)
            context.nrt.incref(builder, types.List(dkl__pudnq[i]), nxyks__wlj)
        return table._getvalue()
    table_type = TableType(tuple(dkl__pudnq), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    kzisj__tpo = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        kzisj__tpo['kept_cols'] = np.array(list(kept_cols), np.int64)
        takxs__euv = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        takxs__euv = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    wwqww__ngnb = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        wwqww__ngnb else extra_arrs_t.types[i - wwqww__ngnb] for i in
        in_col_inds)) if is_overload_none(out_table_type_t
        ) else unwrap_typeref(out_table_type_t)
    swszw__aevv = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    swszw__aevv += f'  T1 = in_table_t\n'
    swszw__aevv += f'  T2 = init_table(out_table_type, False)\n'
    swszw__aevv += f'  T2 = set_table_len(T2, len(T1))\n'
    if takxs__euv and len(kept_cols) == 0:
        swszw__aevv += f'  return T2\n'
        fglw__zhx = {}
        exec(swszw__aevv, kzisj__tpo, fglw__zhx)
        return fglw__zhx['impl']
    if takxs__euv:
        swszw__aevv += f'  kept_cols_set = set(kept_cols)\n'
    for typ, zrkev__ihynj in out_table_type.type_to_blk.items():
        kzisj__tpo[f'arr_list_typ_{zrkev__ihynj}'] = types.List(typ)
        lwoaa__pgmq = len(out_table_type.block_to_arr_ind[zrkev__ihynj])
        swszw__aevv += f"""  out_arr_list_{zrkev__ihynj} = alloc_list_like(arr_list_typ_{zrkev__ihynj}, {lwoaa__pgmq}, False)
"""
        if typ in in_table_t.type_to_blk:
            rth__afa = in_table_t.type_to_blk[typ]
            qjblj__qhtmn = []
            xqmlo__tyx = []
            for zedyg__zjzay in out_table_type.block_to_arr_ind[zrkev__ihynj]:
                diqkv__syph = in_col_inds[zedyg__zjzay]
                if diqkv__syph < wwqww__ngnb:
                    qjblj__qhtmn.append(in_table_t.block_offsets[diqkv__syph])
                    xqmlo__tyx.append(diqkv__syph)
                else:
                    qjblj__qhtmn.append(-1)
                    xqmlo__tyx.append(-1)
            kzisj__tpo[f'in_idxs_{zrkev__ihynj}'] = np.array(qjblj__qhtmn,
                np.int64)
            kzisj__tpo[f'in_arr_inds_{zrkev__ihynj}'] = np.array(xqmlo__tyx,
                np.int64)
            if takxs__euv:
                kzisj__tpo[f'out_arr_inds_{zrkev__ihynj}'] = np.array(
                    out_table_type.block_to_arr_ind[zrkev__ihynj], dtype=np
                    .int64)
            swszw__aevv += (
                f'  in_arr_list_{zrkev__ihynj} = get_table_block(T1, {rth__afa})\n'
                )
            swszw__aevv += (
                f'  for i in range(len(out_arr_list_{zrkev__ihynj})):\n')
            swszw__aevv += (
                f'    in_offset_{zrkev__ihynj} = in_idxs_{zrkev__ihynj}[i]\n')
            swszw__aevv += f'    if in_offset_{zrkev__ihynj} == -1:\n'
            swszw__aevv += f'      continue\n'
            swszw__aevv += (
                f'    in_arr_ind_{zrkev__ihynj} = in_arr_inds_{zrkev__ihynj}[i]\n'
                )
            if takxs__euv:
                swszw__aevv += f"""    if out_arr_inds_{zrkev__ihynj}[i] not in kept_cols_set: continue
"""
            swszw__aevv += f"""    ensure_column_unboxed(T1, in_arr_list_{zrkev__ihynj}, in_offset_{zrkev__ihynj}, in_arr_ind_{zrkev__ihynj})
"""
            swszw__aevv += f"""    out_arr_list_{zrkev__ihynj}[i] = in_arr_list_{zrkev__ihynj}[in_offset_{zrkev__ihynj}]
"""
        for i, zedyg__zjzay in enumerate(out_table_type.block_to_arr_ind[
            zrkev__ihynj]):
            if zedyg__zjzay not in kept_cols:
                continue
            diqkv__syph = in_col_inds[zedyg__zjzay]
            if diqkv__syph >= wwqww__ngnb:
                swszw__aevv += f"""  out_arr_list_{zrkev__ihynj}[{i}] = extra_arrs_t[{diqkv__syph - wwqww__ngnb}]
"""
        swszw__aevv += (
            f'  T2 = set_table_block(T2, out_arr_list_{zrkev__ihynj}, {zrkev__ihynj})\n'
            )
    swszw__aevv += f'  return T2\n'
    kzisj__tpo.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    fglw__zhx = {}
    exec(swszw__aevv, kzisj__tpo, fglw__zhx)
    return fglw__zhx['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    wwqww__ngnb = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < wwqww__ngnb
         else extra_arrs_t.types[i - wwqww__ngnb] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    fmv__hexke = None
    if not is_overload_none(in_table_t):
        for i, egbab__pfjm in enumerate(in_table_t.types):
            if egbab__pfjm != types.none:
                fmv__hexke = f'in_table_t[{i}]'
                break
    if fmv__hexke is None:
        for i, egbab__pfjm in enumerate(extra_arrs_t.types):
            if egbab__pfjm != types.none:
                fmv__hexke = f'extra_arrs_t[{i}]'
                break
    assert fmv__hexke is not None, 'no array found in input data'
    swszw__aevv = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    swszw__aevv += f'  T1 = in_table_t\n'
    swszw__aevv += f'  T2 = init_table(out_table_type, False)\n'
    swszw__aevv += f'  T2 = set_table_len(T2, len({fmv__hexke}))\n'
    kzisj__tpo = {}
    for typ, zrkev__ihynj in out_table_type.type_to_blk.items():
        kzisj__tpo[f'arr_list_typ_{zrkev__ihynj}'] = types.List(typ)
        lwoaa__pgmq = len(out_table_type.block_to_arr_ind[zrkev__ihynj])
        swszw__aevv += f"""  out_arr_list_{zrkev__ihynj} = alloc_list_like(arr_list_typ_{zrkev__ihynj}, {lwoaa__pgmq}, False)
"""
        for i, zedyg__zjzay in enumerate(out_table_type.block_to_arr_ind[
            zrkev__ihynj]):
            if zedyg__zjzay not in kept_cols:
                continue
            diqkv__syph = in_col_inds[zedyg__zjzay]
            if diqkv__syph < wwqww__ngnb:
                swszw__aevv += (
                    f'  out_arr_list_{zrkev__ihynj}[{i}] = T1[{diqkv__syph}]\n'
                    )
            else:
                swszw__aevv += f"""  out_arr_list_{zrkev__ihynj}[{i}] = extra_arrs_t[{diqkv__syph - wwqww__ngnb}]
"""
        swszw__aevv += (
            f'  T2 = set_table_block(T2, out_arr_list_{zrkev__ihynj}, {zrkev__ihynj})\n'
            )
    swszw__aevv += f'  return T2\n'
    kzisj__tpo.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    fglw__zhx = {}
    exec(swszw__aevv, kzisj__tpo, fglw__zhx)
    return fglw__zhx['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    iiloe__wgy = args[0]
    aut__kiyhc = args[1]
    if equiv_set.has_shape(iiloe__wgy):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            iiloe__wgy)[0], None), pre=[])
    if equiv_set.has_shape(aut__kiyhc):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            aut__kiyhc)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
