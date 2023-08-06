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
            axzkv__zofi = 0
            plnrp__dzvrd = []
            for i in range(usecols[-1] + 1):
                if i == usecols[axzkv__zofi]:
                    plnrp__dzvrd.append(arrs[axzkv__zofi])
                    axzkv__zofi += 1
                else:
                    plnrp__dzvrd.append(None)
            for rojp__yiwhm in range(usecols[-1] + 1, num_arrs):
                plnrp__dzvrd.append(None)
            self.arrays = plnrp__dzvrd
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((rvcti__paiq == tmysp__rof).all() for 
            rvcti__paiq, tmysp__rof in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        yivyn__yvvw = len(self.arrays)
        lfds__foj = dict(zip(range(yivyn__yvvw), self.arrays))
        df = pd.DataFrame(lfds__foj, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        djnk__eixyw = []
        hqjvd__mnq = []
        hvyi__iycd = {}
        yruc__wbh = {}
        azfdk__cdhgr = defaultdict(int)
        prc__bbmi = defaultdict(list)
        if not has_runtime_cols:
            for i, qwqjx__unnu in enumerate(arr_types):
                if qwqjx__unnu not in hvyi__iycd:
                    wxnxx__gyc = len(hvyi__iycd)
                    hvyi__iycd[qwqjx__unnu] = wxnxx__gyc
                    yruc__wbh[wxnxx__gyc] = qwqjx__unnu
                vbftj__bjbbv = hvyi__iycd[qwqjx__unnu]
                djnk__eixyw.append(vbftj__bjbbv)
                hqjvd__mnq.append(azfdk__cdhgr[vbftj__bjbbv])
                azfdk__cdhgr[vbftj__bjbbv] += 1
                prc__bbmi[vbftj__bjbbv].append(i)
        self.block_nums = djnk__eixyw
        self.block_offsets = hqjvd__mnq
        self.type_to_blk = hvyi__iycd
        self.blk_to_type = yruc__wbh
        self.block_to_arr_ind = prc__bbmi
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
            xukvk__trcqc = [(f'block_{i}', types.List(qwqjx__unnu)) for i,
                qwqjx__unnu in enumerate(fe_type.arr_types)]
        else:
            xukvk__trcqc = [(f'block_{vbftj__bjbbv}', types.List(
                qwqjx__unnu)) for qwqjx__unnu, vbftj__bjbbv in fe_type.
                type_to_blk.items()]
        xukvk__trcqc.append(('parent', types.pyobject))
        xukvk__trcqc.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, xukvk__trcqc)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    zbldd__sut = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    mizt__hcerh = c.pyapi.make_none()
    uzlib__huvl = c.context.get_constant(types.int64, 0)
    sucu__gbrnf = cgutils.alloca_once_value(c.builder, uzlib__huvl)
    for qwqjx__unnu, vbftj__bjbbv in typ.type_to_blk.items():
        iisjq__gqd = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[vbftj__bjbbv]))
        rojp__yiwhm, etlma__vqox = ListInstance.allocate_ex(c.context, c.
            builder, types.List(qwqjx__unnu), iisjq__gqd)
        etlma__vqox.size = iisjq__gqd
        onp__avzzm = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            vbftj__bjbbv], dtype=np.int64))
        xqiv__nboju = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, onp__avzzm)
        with cgutils.for_range(c.builder, iisjq__gqd) as uvqa__gjlg:
            i = uvqa__gjlg.index
            tzplw__rnd = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), xqiv__nboju, i)
            havf__mniyp = c.pyapi.long_from_longlong(tzplw__rnd)
            qlhot__hwmt = c.pyapi.object_getitem(zbldd__sut, havf__mniyp)
            tgwhw__cuit = c.builder.icmp_unsigned('==', qlhot__hwmt,
                mizt__hcerh)
            with c.builder.if_else(tgwhw__cuit) as (ruz__ngjcg, djd__fwxn):
                with ruz__ngjcg:
                    gkswt__fkeyy = c.context.get_constant_null(qwqjx__unnu)
                    etlma__vqox.inititem(i, gkswt__fkeyy, incref=False)
                with djd__fwxn:
                    ppzm__hyhf = c.pyapi.call_method(qlhot__hwmt, '__len__', ()
                        )
                    chqe__ldv = c.pyapi.long_as_longlong(ppzm__hyhf)
                    c.builder.store(chqe__ldv, sucu__gbrnf)
                    c.pyapi.decref(ppzm__hyhf)
                    arr = c.pyapi.to_native_value(qwqjx__unnu, qlhot__hwmt
                        ).value
                    etlma__vqox.inititem(i, arr, incref=False)
            c.pyapi.decref(qlhot__hwmt)
            c.pyapi.decref(havf__mniyp)
        setattr(table, f'block_{vbftj__bjbbv}', etlma__vqox.value)
    table.len = c.builder.load(sucu__gbrnf)
    c.pyapi.decref(zbldd__sut)
    c.pyapi.decref(mizt__hcerh)
    uxu__rpvsl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=uxu__rpvsl)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        rtvqx__bsrz = c.context.get_constant(types.int64, 0)
        for i, qwqjx__unnu in enumerate(typ.arr_types):
            plnrp__dzvrd = getattr(table, f'block_{i}')
            pcd__kwxg = ListInstance(c.context, c.builder, types.List(
                qwqjx__unnu), plnrp__dzvrd)
            rtvqx__bsrz = c.builder.add(rtvqx__bsrz, pcd__kwxg.size)
        pmosh__jjy = c.pyapi.list_new(rtvqx__bsrz)
        lukhh__lzwd = c.context.get_constant(types.int64, 0)
        for i, qwqjx__unnu in enumerate(typ.arr_types):
            plnrp__dzvrd = getattr(table, f'block_{i}')
            pcd__kwxg = ListInstance(c.context, c.builder, types.List(
                qwqjx__unnu), plnrp__dzvrd)
            with cgutils.for_range(c.builder, pcd__kwxg.size) as uvqa__gjlg:
                i = uvqa__gjlg.index
                arr = pcd__kwxg.getitem(i)
                c.context.nrt.incref(c.builder, qwqjx__unnu, arr)
                idx = c.builder.add(lukhh__lzwd, i)
                c.pyapi.list_setitem(pmosh__jjy, idx, c.pyapi.
                    from_native_value(qwqjx__unnu, arr, c.env_manager))
            lukhh__lzwd = c.builder.add(lukhh__lzwd, pcd__kwxg.size)
        qouqw__yout = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        zcmp__jjbdv = c.pyapi.call_function_objargs(qouqw__yout, (pmosh__jjy,))
        c.pyapi.decref(qouqw__yout)
        c.pyapi.decref(pmosh__jjy)
        c.context.nrt.decref(c.builder, typ, val)
        return zcmp__jjbdv
    pmosh__jjy = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    fsqe__atax = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for qwqjx__unnu, vbftj__bjbbv in typ.type_to_blk.items():
        plnrp__dzvrd = getattr(table, f'block_{vbftj__bjbbv}')
        pcd__kwxg = ListInstance(c.context, c.builder, types.List(
            qwqjx__unnu), plnrp__dzvrd)
        onp__avzzm = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[
            vbftj__bjbbv], dtype=np.int64))
        xqiv__nboju = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, onp__avzzm)
        with cgutils.for_range(c.builder, pcd__kwxg.size) as uvqa__gjlg:
            i = uvqa__gjlg.index
            tzplw__rnd = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), xqiv__nboju, i)
            arr = pcd__kwxg.getitem(i)
            zkqop__myb = cgutils.alloca_once_value(c.builder, arr)
            ftimy__uwi = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(qwqjx__unnu))
            is_null = is_ll_eq(c.builder, zkqop__myb, ftimy__uwi)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (ruz__ngjcg, djd__fwxn):
                with ruz__ngjcg:
                    mizt__hcerh = c.pyapi.make_none()
                    c.pyapi.list_setitem(pmosh__jjy, tzplw__rnd, mizt__hcerh)
                with djd__fwxn:
                    qlhot__hwmt = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, fsqe__atax)
                        ) as (pxl__opt, ahaqm__eacn):
                        with pxl__opt:
                            uwat__zidjv = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                tzplw__rnd, qwqjx__unnu)
                            c.builder.store(uwat__zidjv, qlhot__hwmt)
                        with ahaqm__eacn:
                            c.context.nrt.incref(c.builder, qwqjx__unnu, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                qwqjx__unnu, arr, c.env_manager), qlhot__hwmt)
                    c.pyapi.list_setitem(pmosh__jjy, tzplw__rnd, c.builder.
                        load(qlhot__hwmt))
    qouqw__yout = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    zcmp__jjbdv = c.pyapi.call_function_objargs(qouqw__yout, (pmosh__jjy,))
    c.pyapi.decref(qouqw__yout)
    c.pyapi.decref(pmosh__jjy)
    c.context.nrt.decref(c.builder, typ, val)
    return zcmp__jjbdv


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
        dha__cbvz = context.get_constant(types.int64, 0)
        for i, qwqjx__unnu in enumerate(table_type.arr_types):
            plnrp__dzvrd = getattr(table, f'block_{i}')
            pcd__kwxg = ListInstance(context, builder, types.List(
                qwqjx__unnu), plnrp__dzvrd)
            dha__cbvz = builder.add(dha__cbvz, pcd__kwxg.size)
        return dha__cbvz
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    vbftj__bjbbv = table_type.block_nums[col_ind]
    ght__riy = table_type.block_offsets[col_ind]
    plnrp__dzvrd = getattr(table, f'block_{vbftj__bjbbv}')
    cnv__qdrgc = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    paq__wdzix = context.get_constant(types.int64, col_ind)
    wezuo__dhk = context.get_constant(types.int64, ght__riy)
    djcq__ftx = table_arg, plnrp__dzvrd, wezuo__dhk, paq__wdzix
    ensure_column_unboxed_codegen(context, builder, cnv__qdrgc, djcq__ftx)
    pcd__kwxg = ListInstance(context, builder, types.List(arr_type),
        plnrp__dzvrd)
    arr = pcd__kwxg.getitem(ght__riy)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, rojp__yiwhm = args
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
    mxy__ntz = list(ind_typ.instance_type.meta)
    bgnf__mrdeh = defaultdict(list)
    for ind in mxy__ntz:
        bgnf__mrdeh[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, rojp__yiwhm = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for vbftj__bjbbv, ujka__heeqk in bgnf__mrdeh.items():
            arr_type = table_type.blk_to_type[vbftj__bjbbv]
            plnrp__dzvrd = getattr(table, f'block_{vbftj__bjbbv}')
            pcd__kwxg = ListInstance(context, builder, types.List(arr_type),
                plnrp__dzvrd)
            gkswt__fkeyy = context.get_constant_null(arr_type)
            if len(ujka__heeqk) == 1:
                ght__riy = ujka__heeqk[0]
                arr = pcd__kwxg.getitem(ght__riy)
                context.nrt.decref(builder, arr_type, arr)
                pcd__kwxg.inititem(ght__riy, gkswt__fkeyy, incref=False)
            else:
                iisjq__gqd = context.get_constant(types.int64, len(ujka__heeqk)
                    )
                xkk__fos = context.make_constant_array(builder, types.Array
                    (types.int64, 1, 'C'), np.array(ujka__heeqk, dtype=np.
                    int64))
                hoql__mec = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, xkk__fos)
                with cgutils.for_range(builder, iisjq__gqd) as uvqa__gjlg:
                    i = uvqa__gjlg.index
                    ght__riy = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        hoql__mec, i)
                    arr = pcd__kwxg.getitem(ght__riy)
                    context.nrt.decref(builder, arr_type, arr)
                    pcd__kwxg.inititem(ght__riy, gkswt__fkeyy, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    uzlib__huvl = context.get_constant(types.int64, 0)
    qnhk__bct = context.get_constant(types.int64, 1)
    wfmbd__usshu = arr_type not in in_table_type.type_to_blk
    for qwqjx__unnu, vbftj__bjbbv in out_table_type.type_to_blk.items():
        if qwqjx__unnu in in_table_type.type_to_blk:
            imja__qrhb = in_table_type.type_to_blk[qwqjx__unnu]
            etlma__vqox = ListInstance(context, builder, types.List(
                qwqjx__unnu), getattr(in_table, f'block_{imja__qrhb}'))
            context.nrt.incref(builder, types.List(qwqjx__unnu),
                etlma__vqox.value)
            setattr(out_table, f'block_{vbftj__bjbbv}', etlma__vqox.value)
    if wfmbd__usshu:
        rojp__yiwhm, etlma__vqox = ListInstance.allocate_ex(context,
            builder, types.List(arr_type), qnhk__bct)
        etlma__vqox.size = qnhk__bct
        etlma__vqox.inititem(uzlib__huvl, arr_arg, incref=True)
        vbftj__bjbbv = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{vbftj__bjbbv}', etlma__vqox.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        vbftj__bjbbv = out_table_type.type_to_blk[arr_type]
        etlma__vqox = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{vbftj__bjbbv}'))
        if is_new_col:
            n = etlma__vqox.size
            eccg__hzhr = builder.add(n, qnhk__bct)
            etlma__vqox.resize(eccg__hzhr)
            etlma__vqox.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            lqubx__rar = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            etlma__vqox.setitem(lqubx__rar, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            lqubx__rar = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = etlma__vqox.size
            eccg__hzhr = builder.add(n, qnhk__bct)
            etlma__vqox.resize(eccg__hzhr)
            context.nrt.incref(builder, arr_type, etlma__vqox.getitem(
                lqubx__rar))
            etlma__vqox.move(builder.add(lqubx__rar, qnhk__bct), lqubx__rar,
                builder.sub(n, lqubx__rar))
            etlma__vqox.setitem(lqubx__rar, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    csrte__calx = in_table_type.arr_types[col_ind]
    if csrte__calx in out_table_type.type_to_blk:
        vbftj__bjbbv = out_table_type.type_to_blk[csrte__calx]
        myas__mmar = getattr(out_table, f'block_{vbftj__bjbbv}')
        htxbq__dsuif = types.List(csrte__calx)
        lqubx__rar = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        ambem__pio = htxbq__dsuif.dtype(htxbq__dsuif, types.intp)
        dpv__psqr = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), ambem__pio, (myas__mmar, lqubx__rar))
        context.nrt.decref(builder, csrte__calx, dpv__psqr)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    bovjq__asxsr = list(table.arr_types)
    if ind == len(bovjq__asxsr):
        tracp__nyfz = None
        bovjq__asxsr.append(arr_type)
    else:
        tracp__nyfz = table.arr_types[ind]
        bovjq__asxsr[ind] = arr_type
    uojh__eheme = TableType(tuple(bovjq__asxsr))
    kzwop__efo = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': uojh__eheme}
    afwnw__mmtx = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    afwnw__mmtx += f'  T2 = init_table(out_table_typ, False)\n'
    afwnw__mmtx += f'  T2 = set_table_len(T2, len(table))\n'
    afwnw__mmtx += f'  T2 = set_table_parent(T2, table)\n'
    for typ, vbftj__bjbbv in uojh__eheme.type_to_blk.items():
        if typ in table.type_to_blk:
            oiytm__epjl = table.type_to_blk[typ]
            afwnw__mmtx += (
                f'  arr_list_{vbftj__bjbbv} = get_table_block(table, {oiytm__epjl})\n'
                )
            afwnw__mmtx += f"""  out_arr_list_{vbftj__bjbbv} = alloc_list_like(arr_list_{vbftj__bjbbv}, {len(uojh__eheme.block_to_arr_ind[vbftj__bjbbv])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[oiytm__epjl]
                ) & used_cols:
                afwnw__mmtx += (
                    f'  for i in range(len(arr_list_{vbftj__bjbbv})):\n')
                if typ not in (tracp__nyfz, arr_type):
                    afwnw__mmtx += f"""    out_arr_list_{vbftj__bjbbv}[i] = arr_list_{vbftj__bjbbv}[i]
"""
                else:
                    piz__bwil = table.block_to_arr_ind[oiytm__epjl]
                    sdaer__haku = np.empty(len(piz__bwil), np.int64)
                    jcka__suabo = False
                    for qiodj__yej, tzplw__rnd in enumerate(piz__bwil):
                        if tzplw__rnd != ind:
                            izdd__whc = uojh__eheme.block_offsets[tzplw__rnd]
                        else:
                            izdd__whc = -1
                            jcka__suabo = True
                        sdaer__haku[qiodj__yej] = izdd__whc
                    kzwop__efo[f'out_idxs_{vbftj__bjbbv}'] = np.array(
                        sdaer__haku, np.int64)
                    afwnw__mmtx += (
                        f'    out_idx = out_idxs_{vbftj__bjbbv}[i]\n')
                    if jcka__suabo:
                        afwnw__mmtx += f'    if out_idx == -1:\n'
                        afwnw__mmtx += f'      continue\n'
                    afwnw__mmtx += f"""    out_arr_list_{vbftj__bjbbv}[out_idx] = arr_list_{vbftj__bjbbv}[i]
"""
            if typ == arr_type and not is_null:
                afwnw__mmtx += f"""  out_arr_list_{vbftj__bjbbv}[{uojh__eheme.block_offsets[ind]}] = arr
"""
        else:
            kzwop__efo[f'arr_list_typ_{vbftj__bjbbv}'] = types.List(arr_type)
            afwnw__mmtx += f"""  out_arr_list_{vbftj__bjbbv} = alloc_list_like(arr_list_typ_{vbftj__bjbbv}, 1, False)
"""
            if not is_null:
                afwnw__mmtx += f'  out_arr_list_{vbftj__bjbbv}[0] = arr\n'
        afwnw__mmtx += (
            f'  T2 = set_table_block(T2, out_arr_list_{vbftj__bjbbv}, {vbftj__bjbbv})\n'
            )
    afwnw__mmtx += f'  return T2\n'
    ikmn__mzkqa = {}
    exec(afwnw__mmtx, kzwop__efo, ikmn__mzkqa)
    return ikmn__mzkqa['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        kulcx__hwy = None
    else:
        kulcx__hwy = set(used_cols.instance_type.meta)
    pliw__cznb = get_overload_const_int(ind)
    return generate_set_table_data_code(table, pliw__cznb, arr, kulcx__hwy)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    pliw__cznb = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        kulcx__hwy = None
    else:
        kulcx__hwy = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, pliw__cznb, arr_type,
        kulcx__hwy, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    xsnxm__kaqzq = args[0]
    if equiv_set.has_shape(xsnxm__kaqzq):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            xsnxm__kaqzq)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    hdc__bwzjj = []
    for qwqjx__unnu, vbftj__bjbbv in table_type.type_to_blk.items():
        lhndu__fhvk = len(table_type.block_to_arr_ind[vbftj__bjbbv])
        qkrm__bxay = []
        for i in range(lhndu__fhvk):
            tzplw__rnd = table_type.block_to_arr_ind[vbftj__bjbbv][i]
            qkrm__bxay.append(pyval.arrays[tzplw__rnd])
        hdc__bwzjj.append(context.get_constant_generic(builder, types.List(
            qwqjx__unnu), qkrm__bxay))
    vay__sxi = context.get_constant_null(types.pyobject)
    vcow__gtw = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(hdc__bwzjj + [vay__sxi, vcow__gtw])


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
        for qwqjx__unnu, vbftj__bjbbv in out_table_type.type_to_blk.items():
            oalp__kcqww = context.get_constant_null(types.List(qwqjx__unnu))
            setattr(table, f'block_{vbftj__bjbbv}', oalp__kcqww)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    qtffg__usz = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        qtffg__usz[typ.dtype] = i
    ydyub__rttk = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(ydyub__rttk, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        mtho__qgu, rojp__yiwhm = args
        table = cgutils.create_struct_proxy(ydyub__rttk)(context, builder)
        for qwqjx__unnu, vbftj__bjbbv in ydyub__rttk.type_to_blk.items():
            idx = qtffg__usz[qwqjx__unnu]
            uoysq__zzd = signature(types.List(qwqjx__unnu),
                tuple_of_lists_type, types.literal(idx))
            ksrr__ndq = mtho__qgu, idx
            wnt__rnu = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, uoysq__zzd, ksrr__ndq)
            setattr(table, f'block_{vbftj__bjbbv}', wnt__rnu)
        return table._getvalue()
    sig = ydyub__rttk(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    vbftj__bjbbv = get_overload_const_int(blk_type)
    arr_type = None
    for qwqjx__unnu, tmysp__rof in table_type.type_to_blk.items():
        if tmysp__rof == vbftj__bjbbv:
            arr_type = qwqjx__unnu
            break
    assert arr_type is not None, 'invalid table type block'
    yfr__bdvf = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        plnrp__dzvrd = getattr(table, f'block_{vbftj__bjbbv}')
        return impl_ret_borrowed(context, builder, yfr__bdvf, plnrp__dzvrd)
    sig = yfr__bdvf(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, metw__kvm = args
        ddhc__nkhl = context.get_python_api(builder)
        aswsd__phmze = used_cols_typ == types.none
        if not aswsd__phmze:
            ubxh__qex = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), metw__kvm)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for qwqjx__unnu, vbftj__bjbbv in table_type.type_to_blk.items():
            iisjq__gqd = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[vbftj__bjbbv]))
            onp__avzzm = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                vbftj__bjbbv], dtype=np.int64))
            xqiv__nboju = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, onp__avzzm)
            plnrp__dzvrd = getattr(table, f'block_{vbftj__bjbbv}')
            with cgutils.for_range(builder, iisjq__gqd) as uvqa__gjlg:
                i = uvqa__gjlg.index
                tzplw__rnd = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    xqiv__nboju, i)
                cnv__qdrgc = types.none(table_type, types.List(qwqjx__unnu),
                    types.int64, types.int64)
                djcq__ftx = table_arg, plnrp__dzvrd, i, tzplw__rnd
                if aswsd__phmze:
                    ensure_column_unboxed_codegen(context, builder,
                        cnv__qdrgc, djcq__ftx)
                else:
                    rdwua__jhrdx = ubxh__qex.contains(tzplw__rnd)
                    with builder.if_then(rdwua__jhrdx):
                        ensure_column_unboxed_codegen(context, builder,
                            cnv__qdrgc, djcq__ftx)
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
    table_arg, tzqq__gqp, scctn__kesk, aqn__qrubp = args
    ddhc__nkhl = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    fsqe__atax = cgutils.is_not_null(builder, table.parent)
    pcd__kwxg = ListInstance(context, builder, sig.args[1], tzqq__gqp)
    bfokt__ybib = pcd__kwxg.getitem(scctn__kesk)
    zkqop__myb = cgutils.alloca_once_value(builder, bfokt__ybib)
    ftimy__uwi = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, zkqop__myb, ftimy__uwi)
    with builder.if_then(is_null):
        with builder.if_else(fsqe__atax) as (ruz__ngjcg, djd__fwxn):
            with ruz__ngjcg:
                qlhot__hwmt = get_df_obj_column_codegen(context, builder,
                    ddhc__nkhl, table.parent, aqn__qrubp, sig.args[1].dtype)
                arr = ddhc__nkhl.to_native_value(sig.args[1].dtype, qlhot__hwmt
                    ).value
                pcd__kwxg.inititem(scctn__kesk, arr, incref=False)
                ddhc__nkhl.decref(qlhot__hwmt)
            with djd__fwxn:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    vbftj__bjbbv = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, agi__qyvj, rojp__yiwhm = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{vbftj__bjbbv}', agi__qyvj)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, iae__lfj = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = iae__lfj
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        gguk__vmips, daha__ifz = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, daha__ifz)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, gguk__vmips)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    yfr__bdvf = list_type.instance_type if isinstance(list_type, types.TypeRef
        ) else list_type
    assert isinstance(yfr__bdvf, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        yfr__bdvf = types.List(to_str_arr_if_dict_array(yfr__bdvf.dtype))

    def codegen(context, builder, sig, args):
        jhs__iycxi = args[1]
        rojp__yiwhm, etlma__vqox = ListInstance.allocate_ex(context,
            builder, yfr__bdvf, jhs__iycxi)
        etlma__vqox.size = jhs__iycxi
        return etlma__vqox.value
    sig = yfr__bdvf(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    yfx__smz = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(yfx__smz)

    def codegen(context, builder, sig, args):
        jhs__iycxi, rojp__yiwhm = args
        rojp__yiwhm, etlma__vqox = ListInstance.allocate_ex(context,
            builder, list_type, jhs__iycxi)
        etlma__vqox.size = jhs__iycxi
        return etlma__vqox.value
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
        dsmh__ilz = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(dsmh__ilz)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    kzwop__efo = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        rxlbl__kbaf = used_cols.instance_type
        tshm__onw = np.array(rxlbl__kbaf.meta, dtype=np.int64)
        kzwop__efo['used_cols_vals'] = tshm__onw
        wbfs__irnx = set([T.block_nums[i] for i in tshm__onw])
    else:
        tshm__onw = None
    afwnw__mmtx = 'def table_filter_func(T, idx, used_cols=None):\n'
    afwnw__mmtx += f'  T2 = init_table(T, False)\n'
    afwnw__mmtx += f'  l = 0\n'
    if tshm__onw is not None and len(tshm__onw) == 0:
        afwnw__mmtx += f'  l = _get_idx_length(idx, len(T))\n'
        afwnw__mmtx += f'  T2 = set_table_len(T2, l)\n'
        afwnw__mmtx += f'  return T2\n'
        ikmn__mzkqa = {}
        exec(afwnw__mmtx, kzwop__efo, ikmn__mzkqa)
        return ikmn__mzkqa['table_filter_func']
    if tshm__onw is not None:
        afwnw__mmtx += f'  used_set = set(used_cols_vals)\n'
    for vbftj__bjbbv in T.type_to_blk.values():
        afwnw__mmtx += (
            f'  arr_list_{vbftj__bjbbv} = get_table_block(T, {vbftj__bjbbv})\n'
            )
        afwnw__mmtx += f"""  out_arr_list_{vbftj__bjbbv} = alloc_list_like(arr_list_{vbftj__bjbbv}, len(arr_list_{vbftj__bjbbv}), False)
"""
        if tshm__onw is None or vbftj__bjbbv in wbfs__irnx:
            kzwop__efo[f'arr_inds_{vbftj__bjbbv}'] = np.array(T.
                block_to_arr_ind[vbftj__bjbbv], dtype=np.int64)
            afwnw__mmtx += f'  for i in range(len(arr_list_{vbftj__bjbbv})):\n'
            afwnw__mmtx += (
                f'    arr_ind_{vbftj__bjbbv} = arr_inds_{vbftj__bjbbv}[i]\n')
            if tshm__onw is not None:
                afwnw__mmtx += (
                    f'    if arr_ind_{vbftj__bjbbv} not in used_set: continue\n'
                    )
            afwnw__mmtx += f"""    ensure_column_unboxed(T, arr_list_{vbftj__bjbbv}, i, arr_ind_{vbftj__bjbbv})
"""
            afwnw__mmtx += f"""    out_arr_{vbftj__bjbbv} = ensure_contig_if_np(arr_list_{vbftj__bjbbv}[i][idx])
"""
            afwnw__mmtx += f'    l = len(out_arr_{vbftj__bjbbv})\n'
            afwnw__mmtx += (
                f'    out_arr_list_{vbftj__bjbbv}[i] = out_arr_{vbftj__bjbbv}\n'
                )
        afwnw__mmtx += (
            f'  T2 = set_table_block(T2, out_arr_list_{vbftj__bjbbv}, {vbftj__bjbbv})\n'
            )
    afwnw__mmtx += f'  T2 = set_table_len(T2, l)\n'
    afwnw__mmtx += f'  return T2\n'
    ikmn__mzkqa = {}
    exec(afwnw__mmtx, kzwop__efo, ikmn__mzkqa)
    return ikmn__mzkqa['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    pqzc__hvpk = list(idx.instance_type.meta)
    bovjq__asxsr = tuple(np.array(T.arr_types, dtype=object)[pqzc__hvpk])
    uojh__eheme = TableType(bovjq__asxsr)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    iorem__lkeef = is_overload_true(copy_arrs)
    kzwop__efo = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': uojh__eheme}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        pfgo__wadq = set(kept_cols)
        kzwop__efo['kept_cols'] = np.array(kept_cols, np.int64)
        xnf__pcydj = True
    else:
        xnf__pcydj = False
    hek__sugz = {i: c for i, c in enumerate(pqzc__hvpk)}
    afwnw__mmtx = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    afwnw__mmtx += f'  T2 = init_table(out_table_typ, False)\n'
    afwnw__mmtx += f'  T2 = set_table_len(T2, len(T))\n'
    if xnf__pcydj and len(pfgo__wadq) == 0:
        afwnw__mmtx += f'  return T2\n'
        ikmn__mzkqa = {}
        exec(afwnw__mmtx, kzwop__efo, ikmn__mzkqa)
        return ikmn__mzkqa['table_subset']
    if xnf__pcydj:
        afwnw__mmtx += f'  kept_cols_set = set(kept_cols)\n'
    for typ, vbftj__bjbbv in uojh__eheme.type_to_blk.items():
        oiytm__epjl = T.type_to_blk[typ]
        afwnw__mmtx += (
            f'  arr_list_{vbftj__bjbbv} = get_table_block(T, {oiytm__epjl})\n')
        afwnw__mmtx += f"""  out_arr_list_{vbftj__bjbbv} = alloc_list_like(arr_list_{vbftj__bjbbv}, {len(uojh__eheme.block_to_arr_ind[vbftj__bjbbv])}, False)
"""
        vlaok__gjnp = True
        if xnf__pcydj:
            zgwml__xak = set(uojh__eheme.block_to_arr_ind[vbftj__bjbbv])
            wojd__kafh = zgwml__xak & pfgo__wadq
            vlaok__gjnp = len(wojd__kafh) > 0
        if vlaok__gjnp:
            kzwop__efo[f'out_arr_inds_{vbftj__bjbbv}'] = np.array(uojh__eheme
                .block_to_arr_ind[vbftj__bjbbv], dtype=np.int64)
            afwnw__mmtx += (
                f'  for i in range(len(out_arr_list_{vbftj__bjbbv})):\n')
            afwnw__mmtx += (
                f'    out_arr_ind_{vbftj__bjbbv} = out_arr_inds_{vbftj__bjbbv}[i]\n'
                )
            if xnf__pcydj:
                afwnw__mmtx += (
                    f'    if out_arr_ind_{vbftj__bjbbv} not in kept_cols_set: continue\n'
                    )
            sgns__fct = []
            hzbbl__kjdc = []
            for rsrd__aoqe in uojh__eheme.block_to_arr_ind[vbftj__bjbbv]:
                cks__nlvh = hek__sugz[rsrd__aoqe]
                sgns__fct.append(cks__nlvh)
                lmqk__hhxtf = T.block_offsets[cks__nlvh]
                hzbbl__kjdc.append(lmqk__hhxtf)
            kzwop__efo[f'in_logical_idx_{vbftj__bjbbv}'] = np.array(sgns__fct,
                dtype=np.int64)
            kzwop__efo[f'in_physical_idx_{vbftj__bjbbv}'] = np.array(
                hzbbl__kjdc, dtype=np.int64)
            afwnw__mmtx += (
                f'    logical_idx_{vbftj__bjbbv} = in_logical_idx_{vbftj__bjbbv}[i]\n'
                )
            afwnw__mmtx += (
                f'    physical_idx_{vbftj__bjbbv} = in_physical_idx_{vbftj__bjbbv}[i]\n'
                )
            afwnw__mmtx += f"""    ensure_column_unboxed(T, arr_list_{vbftj__bjbbv}, physical_idx_{vbftj__bjbbv}, logical_idx_{vbftj__bjbbv})
"""
            gatx__kdgnk = '.copy()' if iorem__lkeef else ''
            afwnw__mmtx += f"""    out_arr_list_{vbftj__bjbbv}[i] = arr_list_{vbftj__bjbbv}[physical_idx_{vbftj__bjbbv}]{gatx__kdgnk}
"""
        afwnw__mmtx += (
            f'  T2 = set_table_block(T2, out_arr_list_{vbftj__bjbbv}, {vbftj__bjbbv})\n'
            )
    afwnw__mmtx += f'  return T2\n'
    ikmn__mzkqa = {}
    exec(afwnw__mmtx, kzwop__efo, ikmn__mzkqa)
    return ikmn__mzkqa['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    xsnxm__kaqzq = args[0]
    if equiv_set.has_shape(xsnxm__kaqzq):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=xsnxm__kaqzq, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (xsnxm__kaqzq)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    xsnxm__kaqzq = args[0]
    if equiv_set.has_shape(xsnxm__kaqzq):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            xsnxm__kaqzq)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    afwnw__mmtx = 'def impl(T):\n'
    afwnw__mmtx += f'  T2 = init_table(T, True)\n'
    afwnw__mmtx += f'  l = len(T)\n'
    kzwop__efo = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for vbftj__bjbbv in T.type_to_blk.values():
        kzwop__efo[f'arr_inds_{vbftj__bjbbv}'] = np.array(T.
            block_to_arr_ind[vbftj__bjbbv], dtype=np.int64)
        afwnw__mmtx += (
            f'  arr_list_{vbftj__bjbbv} = get_table_block(T, {vbftj__bjbbv})\n'
            )
        afwnw__mmtx += f"""  out_arr_list_{vbftj__bjbbv} = alloc_list_like(arr_list_{vbftj__bjbbv}, len(arr_list_{vbftj__bjbbv}), True)
"""
        afwnw__mmtx += f'  for i in range(len(arr_list_{vbftj__bjbbv})):\n'
        afwnw__mmtx += (
            f'    arr_ind_{vbftj__bjbbv} = arr_inds_{vbftj__bjbbv}[i]\n')
        afwnw__mmtx += f"""    ensure_column_unboxed(T, arr_list_{vbftj__bjbbv}, i, arr_ind_{vbftj__bjbbv})
"""
        afwnw__mmtx += f"""    out_arr_{vbftj__bjbbv} = decode_if_dict_array(arr_list_{vbftj__bjbbv}[i])
"""
        afwnw__mmtx += (
            f'    out_arr_list_{vbftj__bjbbv}[i] = out_arr_{vbftj__bjbbv}\n')
        afwnw__mmtx += (
            f'  T2 = set_table_block(T2, out_arr_list_{vbftj__bjbbv}, {vbftj__bjbbv})\n'
            )
    afwnw__mmtx += f'  T2 = set_table_len(T2, l)\n'
    afwnw__mmtx += f'  return T2\n'
    ikmn__mzkqa = {}
    exec(afwnw__mmtx, kzwop__efo, ikmn__mzkqa)
    return ikmn__mzkqa['impl']


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
        nbh__uzdv = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        nbh__uzdv = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            nbh__uzdv.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        bfx__mvbr, lsfsf__bmg = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = lsfsf__bmg
        hdc__bwzjj = cgutils.unpack_tuple(builder, bfx__mvbr)
        for i, plnrp__dzvrd in enumerate(hdc__bwzjj):
            setattr(table, f'block_{i}', plnrp__dzvrd)
            context.nrt.incref(builder, types.List(nbh__uzdv[i]), plnrp__dzvrd)
        return table._getvalue()
    table_type = TableType(tuple(nbh__uzdv), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    kzwop__efo = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        kzwop__efo['kept_cols'] = np.array(list(kept_cols), np.int64)
        xnf__pcydj = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        xnf__pcydj = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    sgtp__iax = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        sgtp__iax else extra_arrs_t.types[i - sgtp__iax] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    afwnw__mmtx = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    afwnw__mmtx += f'  T1 = in_table_t\n'
    afwnw__mmtx += f'  T2 = init_table(out_table_type, False)\n'
    afwnw__mmtx += f'  T2 = set_table_len(T2, len(T1))\n'
    if xnf__pcydj and len(kept_cols) == 0:
        afwnw__mmtx += f'  return T2\n'
        ikmn__mzkqa = {}
        exec(afwnw__mmtx, kzwop__efo, ikmn__mzkqa)
        return ikmn__mzkqa['impl']
    if xnf__pcydj:
        afwnw__mmtx += f'  kept_cols_set = set(kept_cols)\n'
    for typ, vbftj__bjbbv in out_table_type.type_to_blk.items():
        kzwop__efo[f'arr_list_typ_{vbftj__bjbbv}'] = types.List(typ)
        iisjq__gqd = len(out_table_type.block_to_arr_ind[vbftj__bjbbv])
        afwnw__mmtx += f"""  out_arr_list_{vbftj__bjbbv} = alloc_list_like(arr_list_typ_{vbftj__bjbbv}, {iisjq__gqd}, False)
"""
        if typ in in_table_t.type_to_blk:
            xiu__xgbj = in_table_t.type_to_blk[typ]
            xbz__kbnj = []
            smpgc__jytju = []
            for bqh__eil in out_table_type.block_to_arr_ind[vbftj__bjbbv]:
                pscd__eevk = in_col_inds[bqh__eil]
                if pscd__eevk < sgtp__iax:
                    xbz__kbnj.append(in_table_t.block_offsets[pscd__eevk])
                    smpgc__jytju.append(pscd__eevk)
                else:
                    xbz__kbnj.append(-1)
                    smpgc__jytju.append(-1)
            kzwop__efo[f'in_idxs_{vbftj__bjbbv}'] = np.array(xbz__kbnj, np.
                int64)
            kzwop__efo[f'in_arr_inds_{vbftj__bjbbv}'] = np.array(smpgc__jytju,
                np.int64)
            if xnf__pcydj:
                kzwop__efo[f'out_arr_inds_{vbftj__bjbbv}'] = np.array(
                    out_table_type.block_to_arr_ind[vbftj__bjbbv], dtype=np
                    .int64)
            afwnw__mmtx += (
                f'  in_arr_list_{vbftj__bjbbv} = get_table_block(T1, {xiu__xgbj})\n'
                )
            afwnw__mmtx += (
                f'  for i in range(len(out_arr_list_{vbftj__bjbbv})):\n')
            afwnw__mmtx += (
                f'    in_offset_{vbftj__bjbbv} = in_idxs_{vbftj__bjbbv}[i]\n')
            afwnw__mmtx += f'    if in_offset_{vbftj__bjbbv} == -1:\n'
            afwnw__mmtx += f'      continue\n'
            afwnw__mmtx += (
                f'    in_arr_ind_{vbftj__bjbbv} = in_arr_inds_{vbftj__bjbbv}[i]\n'
                )
            if xnf__pcydj:
                afwnw__mmtx += f"""    if out_arr_inds_{vbftj__bjbbv}[i] not in kept_cols_set: continue
"""
            afwnw__mmtx += f"""    ensure_column_unboxed(T1, in_arr_list_{vbftj__bjbbv}, in_offset_{vbftj__bjbbv}, in_arr_ind_{vbftj__bjbbv})
"""
            afwnw__mmtx += f"""    out_arr_list_{vbftj__bjbbv}[i] = in_arr_list_{vbftj__bjbbv}[in_offset_{vbftj__bjbbv}]
"""
        for i, bqh__eil in enumerate(out_table_type.block_to_arr_ind[
            vbftj__bjbbv]):
            if bqh__eil not in kept_cols:
                continue
            pscd__eevk = in_col_inds[bqh__eil]
            if pscd__eevk >= sgtp__iax:
                afwnw__mmtx += f"""  out_arr_list_{vbftj__bjbbv}[{i}] = extra_arrs_t[{pscd__eevk - sgtp__iax}]
"""
        afwnw__mmtx += (
            f'  T2 = set_table_block(T2, out_arr_list_{vbftj__bjbbv}, {vbftj__bjbbv})\n'
            )
    afwnw__mmtx += f'  return T2\n'
    kzwop__efo.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    ikmn__mzkqa = {}
    exec(afwnw__mmtx, kzwop__efo, ikmn__mzkqa)
    return ikmn__mzkqa['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    sgtp__iax = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < sgtp__iax else
        extra_arrs_t.types[i - sgtp__iax] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    hcz__ibz = None
    if not is_overload_none(in_table_t):
        for i, qwqjx__unnu in enumerate(in_table_t.types):
            if qwqjx__unnu != types.none:
                hcz__ibz = f'in_table_t[{i}]'
                break
    if hcz__ibz is None:
        for i, qwqjx__unnu in enumerate(extra_arrs_t.types):
            if qwqjx__unnu != types.none:
                hcz__ibz = f'extra_arrs_t[{i}]'
                break
    assert hcz__ibz is not None, 'no array found in input data'
    afwnw__mmtx = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    afwnw__mmtx += f'  T1 = in_table_t\n'
    afwnw__mmtx += f'  T2 = init_table(out_table_type, False)\n'
    afwnw__mmtx += f'  T2 = set_table_len(T2, len({hcz__ibz}))\n'
    kzwop__efo = {}
    for typ, vbftj__bjbbv in out_table_type.type_to_blk.items():
        kzwop__efo[f'arr_list_typ_{vbftj__bjbbv}'] = types.List(typ)
        iisjq__gqd = len(out_table_type.block_to_arr_ind[vbftj__bjbbv])
        afwnw__mmtx += f"""  out_arr_list_{vbftj__bjbbv} = alloc_list_like(arr_list_typ_{vbftj__bjbbv}, {iisjq__gqd}, False)
"""
        for i, bqh__eil in enumerate(out_table_type.block_to_arr_ind[
            vbftj__bjbbv]):
            if bqh__eil not in kept_cols:
                continue
            pscd__eevk = in_col_inds[bqh__eil]
            if pscd__eevk < sgtp__iax:
                afwnw__mmtx += (
                    f'  out_arr_list_{vbftj__bjbbv}[{i}] = T1[{pscd__eevk}]\n')
            else:
                afwnw__mmtx += f"""  out_arr_list_{vbftj__bjbbv}[{i}] = extra_arrs_t[{pscd__eevk - sgtp__iax}]
"""
        afwnw__mmtx += (
            f'  T2 = set_table_block(T2, out_arr_list_{vbftj__bjbbv}, {vbftj__bjbbv})\n'
            )
    afwnw__mmtx += f'  return T2\n'
    kzwop__efo.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    ikmn__mzkqa = {}
    exec(afwnw__mmtx, kzwop__efo, ikmn__mzkqa)
    return ikmn__mzkqa['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    gaijb__eviz = args[0]
    blyic__azm = args[1]
    if equiv_set.has_shape(gaijb__eviz):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            gaijb__eviz)[0], None), pre=[])
    if equiv_set.has_shape(blyic__azm):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            blyic__azm)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
