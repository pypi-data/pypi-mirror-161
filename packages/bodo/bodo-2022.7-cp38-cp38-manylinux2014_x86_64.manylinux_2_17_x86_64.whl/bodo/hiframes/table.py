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
            muw__ibn = 0
            snckz__stgwx = []
            for i in range(usecols[-1] + 1):
                if i == usecols[muw__ibn]:
                    snckz__stgwx.append(arrs[muw__ibn])
                    muw__ibn += 1
                else:
                    snckz__stgwx.append(None)
            for bdzrj__fdwwu in range(usecols[-1] + 1, num_arrs):
                snckz__stgwx.append(None)
            self.arrays = snckz__stgwx
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((wdfsz__ddp == lfuv__pakle).all() for 
            wdfsz__ddp, lfuv__pakle in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        wwgm__uqw = len(self.arrays)
        wejld__nkkjd = dict(zip(range(wwgm__uqw), self.arrays))
        df = pd.DataFrame(wejld__nkkjd, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        strv__rap = []
        lwjtz__fld = []
        ubqve__pjesz = {}
        slys__qrkuh = {}
        yrme__vryq = defaultdict(int)
        tpkg__pgzg = defaultdict(list)
        if not has_runtime_cols:
            for i, jewg__jkmfl in enumerate(arr_types):
                if jewg__jkmfl not in ubqve__pjesz:
                    luwv__lxx = len(ubqve__pjesz)
                    ubqve__pjesz[jewg__jkmfl] = luwv__lxx
                    slys__qrkuh[luwv__lxx] = jewg__jkmfl
                ghm__frmpy = ubqve__pjesz[jewg__jkmfl]
                strv__rap.append(ghm__frmpy)
                lwjtz__fld.append(yrme__vryq[ghm__frmpy])
                yrme__vryq[ghm__frmpy] += 1
                tpkg__pgzg[ghm__frmpy].append(i)
        self.block_nums = strv__rap
        self.block_offsets = lwjtz__fld
        self.type_to_blk = ubqve__pjesz
        self.blk_to_type = slys__qrkuh
        self.block_to_arr_ind = tpkg__pgzg
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
            gizk__crb = [(f'block_{i}', types.List(jewg__jkmfl)) for i,
                jewg__jkmfl in enumerate(fe_type.arr_types)]
        else:
            gizk__crb = [(f'block_{ghm__frmpy}', types.List(jewg__jkmfl)) for
                jewg__jkmfl, ghm__frmpy in fe_type.type_to_blk.items()]
        gizk__crb.append(('parent', types.pyobject))
        gizk__crb.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, gizk__crb)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    rfuse__iefu = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    qgp__ucvj = c.pyapi.make_none()
    faa__ridzv = c.context.get_constant(types.int64, 0)
    qjsh__xaoyk = cgutils.alloca_once_value(c.builder, faa__ridzv)
    for jewg__jkmfl, ghm__frmpy in typ.type_to_blk.items():
        modn__ssj = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[ghm__frmpy]))
        bdzrj__fdwwu, uthj__uhs = ListInstance.allocate_ex(c.context, c.
            builder, types.List(jewg__jkmfl), modn__ssj)
        uthj__uhs.size = modn__ssj
        rifu__dfbb = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[ghm__frmpy],
            dtype=np.int64))
        wihk__qtfb = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, rifu__dfbb)
        with cgutils.for_range(c.builder, modn__ssj) as zqa__mnx:
            i = zqa__mnx.index
            sbh__jirqz = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), wihk__qtfb, i)
            ccsh__sxyvm = c.pyapi.long_from_longlong(sbh__jirqz)
            mvf__yqlm = c.pyapi.object_getitem(rfuse__iefu, ccsh__sxyvm)
            ibqzp__amemg = c.builder.icmp_unsigned('==', mvf__yqlm, qgp__ucvj)
            with c.builder.if_else(ibqzp__amemg) as (woixl__eao, hqful__nsxyk):
                with woixl__eao:
                    kabr__zuf = c.context.get_constant_null(jewg__jkmfl)
                    uthj__uhs.inititem(i, kabr__zuf, incref=False)
                with hqful__nsxyk:
                    jok__axgm = c.pyapi.call_method(mvf__yqlm, '__len__', ())
                    bktsb__cla = c.pyapi.long_as_longlong(jok__axgm)
                    c.builder.store(bktsb__cla, qjsh__xaoyk)
                    c.pyapi.decref(jok__axgm)
                    arr = c.pyapi.to_native_value(jewg__jkmfl, mvf__yqlm).value
                    uthj__uhs.inititem(i, arr, incref=False)
            c.pyapi.decref(mvf__yqlm)
            c.pyapi.decref(ccsh__sxyvm)
        setattr(table, f'block_{ghm__frmpy}', uthj__uhs.value)
    table.len = c.builder.load(qjsh__xaoyk)
    c.pyapi.decref(rfuse__iefu)
    c.pyapi.decref(qgp__ucvj)
    idzf__ogk = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=idzf__ogk)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        zzgb__mcs = c.context.get_constant(types.int64, 0)
        for i, jewg__jkmfl in enumerate(typ.arr_types):
            snckz__stgwx = getattr(table, f'block_{i}')
            tucv__bsl = ListInstance(c.context, c.builder, types.List(
                jewg__jkmfl), snckz__stgwx)
            zzgb__mcs = c.builder.add(zzgb__mcs, tucv__bsl.size)
        gtdj__tie = c.pyapi.list_new(zzgb__mcs)
        maz__ibyt = c.context.get_constant(types.int64, 0)
        for i, jewg__jkmfl in enumerate(typ.arr_types):
            snckz__stgwx = getattr(table, f'block_{i}')
            tucv__bsl = ListInstance(c.context, c.builder, types.List(
                jewg__jkmfl), snckz__stgwx)
            with cgutils.for_range(c.builder, tucv__bsl.size) as zqa__mnx:
                i = zqa__mnx.index
                arr = tucv__bsl.getitem(i)
                c.context.nrt.incref(c.builder, jewg__jkmfl, arr)
                idx = c.builder.add(maz__ibyt, i)
                c.pyapi.list_setitem(gtdj__tie, idx, c.pyapi.
                    from_native_value(jewg__jkmfl, arr, c.env_manager))
            maz__ibyt = c.builder.add(maz__ibyt, tucv__bsl.size)
        ugkk__zwq = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        qwm__zdbd = c.pyapi.call_function_objargs(ugkk__zwq, (gtdj__tie,))
        c.pyapi.decref(ugkk__zwq)
        c.pyapi.decref(gtdj__tie)
        c.context.nrt.decref(c.builder, typ, val)
        return qwm__zdbd
    gtdj__tie = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    iuelp__xgl = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for jewg__jkmfl, ghm__frmpy in typ.type_to_blk.items():
        snckz__stgwx = getattr(table, f'block_{ghm__frmpy}')
        tucv__bsl = ListInstance(c.context, c.builder, types.List(
            jewg__jkmfl), snckz__stgwx)
        rifu__dfbb = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[ghm__frmpy],
            dtype=np.int64))
        wihk__qtfb = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, rifu__dfbb)
        with cgutils.for_range(c.builder, tucv__bsl.size) as zqa__mnx:
            i = zqa__mnx.index
            sbh__jirqz = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), wihk__qtfb, i)
            arr = tucv__bsl.getitem(i)
            rpkw__bsyo = cgutils.alloca_once_value(c.builder, arr)
            gki__runc = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(jewg__jkmfl))
            is_null = is_ll_eq(c.builder, rpkw__bsyo, gki__runc)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (woixl__eao, hqful__nsxyk):
                with woixl__eao:
                    qgp__ucvj = c.pyapi.make_none()
                    c.pyapi.list_setitem(gtdj__tie, sbh__jirqz, qgp__ucvj)
                with hqful__nsxyk:
                    mvf__yqlm = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, iuelp__xgl)
                        ) as (jnn__vqwk, slhka__uaa):
                        with jnn__vqwk:
                            fxtrk__fxa = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, table.parent,
                                sbh__jirqz, jewg__jkmfl)
                            c.builder.store(fxtrk__fxa, mvf__yqlm)
                        with slhka__uaa:
                            c.context.nrt.incref(c.builder, jewg__jkmfl, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                jewg__jkmfl, arr, c.env_manager), mvf__yqlm)
                    c.pyapi.list_setitem(gtdj__tie, sbh__jirqz, c.builder.
                        load(mvf__yqlm))
    ugkk__zwq = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    qwm__zdbd = c.pyapi.call_function_objargs(ugkk__zwq, (gtdj__tie,))
    c.pyapi.decref(ugkk__zwq)
    c.pyapi.decref(gtdj__tie)
    c.context.nrt.decref(c.builder, typ, val)
    return qwm__zdbd


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
        eshc__sgbt = context.get_constant(types.int64, 0)
        for i, jewg__jkmfl in enumerate(table_type.arr_types):
            snckz__stgwx = getattr(table, f'block_{i}')
            tucv__bsl = ListInstance(context, builder, types.List(
                jewg__jkmfl), snckz__stgwx)
            eshc__sgbt = builder.add(eshc__sgbt, tucv__bsl.size)
        return eshc__sgbt
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    ghm__frmpy = table_type.block_nums[col_ind]
    blmu__avro = table_type.block_offsets[col_ind]
    snckz__stgwx = getattr(table, f'block_{ghm__frmpy}')
    btxsw__sdmob = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    tkydp__fxtwj = context.get_constant(types.int64, col_ind)
    qzno__boa = context.get_constant(types.int64, blmu__avro)
    vccfc__bpfar = table_arg, snckz__stgwx, qzno__boa, tkydp__fxtwj
    ensure_column_unboxed_codegen(context, builder, btxsw__sdmob, vccfc__bpfar)
    tucv__bsl = ListInstance(context, builder, types.List(arr_type),
        snckz__stgwx)
    arr = tucv__bsl.getitem(blmu__avro)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, bdzrj__fdwwu = args
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
    hzo__vpfow = list(ind_typ.instance_type.meta)
    scax__zxwt = defaultdict(list)
    for ind in hzo__vpfow:
        scax__zxwt[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, bdzrj__fdwwu = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for ghm__frmpy, oxp__nmkcw in scax__zxwt.items():
            arr_type = table_type.blk_to_type[ghm__frmpy]
            snckz__stgwx = getattr(table, f'block_{ghm__frmpy}')
            tucv__bsl = ListInstance(context, builder, types.List(arr_type),
                snckz__stgwx)
            kabr__zuf = context.get_constant_null(arr_type)
            if len(oxp__nmkcw) == 1:
                blmu__avro = oxp__nmkcw[0]
                arr = tucv__bsl.getitem(blmu__avro)
                context.nrt.decref(builder, arr_type, arr)
                tucv__bsl.inititem(blmu__avro, kabr__zuf, incref=False)
            else:
                modn__ssj = context.get_constant(types.int64, len(oxp__nmkcw))
                gzidz__xqgx = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(oxp__nmkcw, dtype=
                    np.int64))
                mdzd__uchvx = context.make_array(types.Array(types.int64, 1,
                    'C'))(context, builder, gzidz__xqgx)
                with cgutils.for_range(builder, modn__ssj) as zqa__mnx:
                    i = zqa__mnx.index
                    blmu__avro = _getitem_array_single_int(context, builder,
                        types.int64, types.Array(types.int64, 1, 'C'),
                        mdzd__uchvx, i)
                    arr = tucv__bsl.getitem(blmu__avro)
                    context.nrt.decref(builder, arr_type, arr)
                    tucv__bsl.inititem(blmu__avro, kabr__zuf, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    faa__ridzv = context.get_constant(types.int64, 0)
    cxgjh__hlew = context.get_constant(types.int64, 1)
    sivgh__vass = arr_type not in in_table_type.type_to_blk
    for jewg__jkmfl, ghm__frmpy in out_table_type.type_to_blk.items():
        if jewg__jkmfl in in_table_type.type_to_blk:
            wwzau__tzrr = in_table_type.type_to_blk[jewg__jkmfl]
            uthj__uhs = ListInstance(context, builder, types.List(
                jewg__jkmfl), getattr(in_table, f'block_{wwzau__tzrr}'))
            context.nrt.incref(builder, types.List(jewg__jkmfl), uthj__uhs.
                value)
            setattr(out_table, f'block_{ghm__frmpy}', uthj__uhs.value)
    if sivgh__vass:
        bdzrj__fdwwu, uthj__uhs = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), cxgjh__hlew)
        uthj__uhs.size = cxgjh__hlew
        uthj__uhs.inititem(faa__ridzv, arr_arg, incref=True)
        ghm__frmpy = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{ghm__frmpy}', uthj__uhs.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        ghm__frmpy = out_table_type.type_to_blk[arr_type]
        uthj__uhs = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{ghm__frmpy}'))
        if is_new_col:
            n = uthj__uhs.size
            wwxx__hemug = builder.add(n, cxgjh__hlew)
            uthj__uhs.resize(wwxx__hemug)
            uthj__uhs.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            abm__tnv = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            uthj__uhs.setitem(abm__tnv, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            abm__tnv = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = uthj__uhs.size
            wwxx__hemug = builder.add(n, cxgjh__hlew)
            uthj__uhs.resize(wwxx__hemug)
            context.nrt.incref(builder, arr_type, uthj__uhs.getitem(abm__tnv))
            uthj__uhs.move(builder.add(abm__tnv, cxgjh__hlew), abm__tnv,
                builder.sub(n, abm__tnv))
            uthj__uhs.setitem(abm__tnv, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    kncp__zhnj = in_table_type.arr_types[col_ind]
    if kncp__zhnj in out_table_type.type_to_blk:
        ghm__frmpy = out_table_type.type_to_blk[kncp__zhnj]
        filas__onx = getattr(out_table, f'block_{ghm__frmpy}')
        utt__votg = types.List(kncp__zhnj)
        abm__tnv = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        uhp__ust = utt__votg.dtype(utt__votg, types.intp)
        qbtj__pom = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), uhp__ust, (filas__onx, abm__tnv))
        context.nrt.decref(builder, kncp__zhnj, qbtj__pom)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    fjn__tfxn = list(table.arr_types)
    if ind == len(fjn__tfxn):
        wqy__jjw = None
        fjn__tfxn.append(arr_type)
    else:
        wqy__jjw = table.arr_types[ind]
        fjn__tfxn[ind] = arr_type
    nnyq__bbgfj = TableType(tuple(fjn__tfxn))
    uqzt__wro = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': nnyq__bbgfj}
    agrqm__kyayj = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    agrqm__kyayj += f'  T2 = init_table(out_table_typ, False)\n'
    agrqm__kyayj += f'  T2 = set_table_len(T2, len(table))\n'
    agrqm__kyayj += f'  T2 = set_table_parent(T2, table)\n'
    for typ, ghm__frmpy in nnyq__bbgfj.type_to_blk.items():
        if typ in table.type_to_blk:
            lkm__uweym = table.type_to_blk[typ]
            agrqm__kyayj += (
                f'  arr_list_{ghm__frmpy} = get_table_block(table, {lkm__uweym})\n'
                )
            agrqm__kyayj += f"""  out_arr_list_{ghm__frmpy} = alloc_list_like(arr_list_{ghm__frmpy}, {len(nnyq__bbgfj.block_to_arr_ind[ghm__frmpy])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[lkm__uweym]
                ) & used_cols:
                agrqm__kyayj += (
                    f'  for i in range(len(arr_list_{ghm__frmpy})):\n')
                if typ not in (wqy__jjw, arr_type):
                    agrqm__kyayj += (
                        f'    out_arr_list_{ghm__frmpy}[i] = arr_list_{ghm__frmpy}[i]\n'
                        )
                else:
                    tdlp__wsnf = table.block_to_arr_ind[lkm__uweym]
                    hbch__igjly = np.empty(len(tdlp__wsnf), np.int64)
                    xwxal__wsrn = False
                    for qij__rdtnj, sbh__jirqz in enumerate(tdlp__wsnf):
                        if sbh__jirqz != ind:
                            upa__eaga = nnyq__bbgfj.block_offsets[sbh__jirqz]
                        else:
                            upa__eaga = -1
                            xwxal__wsrn = True
                        hbch__igjly[qij__rdtnj] = upa__eaga
                    uqzt__wro[f'out_idxs_{ghm__frmpy}'] = np.array(hbch__igjly,
                        np.int64)
                    agrqm__kyayj += f'    out_idx = out_idxs_{ghm__frmpy}[i]\n'
                    if xwxal__wsrn:
                        agrqm__kyayj += f'    if out_idx == -1:\n'
                        agrqm__kyayj += f'      continue\n'
                    agrqm__kyayj += f"""    out_arr_list_{ghm__frmpy}[out_idx] = arr_list_{ghm__frmpy}[i]
"""
            if typ == arr_type and not is_null:
                agrqm__kyayj += f"""  out_arr_list_{ghm__frmpy}[{nnyq__bbgfj.block_offsets[ind]}] = arr
"""
        else:
            uqzt__wro[f'arr_list_typ_{ghm__frmpy}'] = types.List(arr_type)
            agrqm__kyayj += f"""  out_arr_list_{ghm__frmpy} = alloc_list_like(arr_list_typ_{ghm__frmpy}, 1, False)
"""
            if not is_null:
                agrqm__kyayj += f'  out_arr_list_{ghm__frmpy}[0] = arr\n'
        agrqm__kyayj += (
            f'  T2 = set_table_block(T2, out_arr_list_{ghm__frmpy}, {ghm__frmpy})\n'
            )
    agrqm__kyayj += f'  return T2\n'
    jfy__jqzuc = {}
    exec(agrqm__kyayj, uqzt__wro, jfy__jqzuc)
    return jfy__jqzuc['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        kwhi__fsrs = None
    else:
        kwhi__fsrs = set(used_cols.instance_type.meta)
    wqbxh__dvsv = get_overload_const_int(ind)
    return generate_set_table_data_code(table, wqbxh__dvsv, arr, kwhi__fsrs)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    wqbxh__dvsv = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        kwhi__fsrs = None
    else:
        kwhi__fsrs = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, wqbxh__dvsv, arr_type,
        kwhi__fsrs, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    wmmfr__gmi = args[0]
    if equiv_set.has_shape(wmmfr__gmi):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            wmmfr__gmi)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    illq__mqu = []
    for jewg__jkmfl, ghm__frmpy in table_type.type_to_blk.items():
        dwi__bch = len(table_type.block_to_arr_ind[ghm__frmpy])
        ugf__anqe = []
        for i in range(dwi__bch):
            sbh__jirqz = table_type.block_to_arr_ind[ghm__frmpy][i]
            ugf__anqe.append(pyval.arrays[sbh__jirqz])
        illq__mqu.append(context.get_constant_generic(builder, types.List(
            jewg__jkmfl), ugf__anqe))
    wria__uxi = context.get_constant_null(types.pyobject)
    dbb__erxog = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(illq__mqu + [wria__uxi, dbb__erxog])


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
        for jewg__jkmfl, ghm__frmpy in out_table_type.type_to_blk.items():
            oqigt__wrsa = context.get_constant_null(types.List(jewg__jkmfl))
            setattr(table, f'block_{ghm__frmpy}', oqigt__wrsa)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    sxha__lrll = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        sxha__lrll[typ.dtype] = i
    oddz__ajp = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(oddz__ajp, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        ijevy__hxpwn, bdzrj__fdwwu = args
        table = cgutils.create_struct_proxy(oddz__ajp)(context, builder)
        for jewg__jkmfl, ghm__frmpy in oddz__ajp.type_to_blk.items():
            idx = sxha__lrll[jewg__jkmfl]
            tdyj__ekm = signature(types.List(jewg__jkmfl),
                tuple_of_lists_type, types.literal(idx))
            uvpbv__xinuo = ijevy__hxpwn, idx
            jhfpb__fkkzn = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, tdyj__ekm, uvpbv__xinuo)
            setattr(table, f'block_{ghm__frmpy}', jhfpb__fkkzn)
        return table._getvalue()
    sig = oddz__ajp(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    ghm__frmpy = get_overload_const_int(blk_type)
    arr_type = None
    for jewg__jkmfl, lfuv__pakle in table_type.type_to_blk.items():
        if lfuv__pakle == ghm__frmpy:
            arr_type = jewg__jkmfl
            break
    assert arr_type is not None, 'invalid table type block'
    yxlli__wzfk = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        snckz__stgwx = getattr(table, f'block_{ghm__frmpy}')
        return impl_ret_borrowed(context, builder, yxlli__wzfk, snckz__stgwx)
    sig = yxlli__wzfk(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, qux__djkaz = args
        uuwz__ner = context.get_python_api(builder)
        zun__xfexf = used_cols_typ == types.none
        if not zun__xfexf:
            dxy__bwtx = numba.cpython.setobj.SetInstance(context, builder,
                types.Set(types.int64), qux__djkaz)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for jewg__jkmfl, ghm__frmpy in table_type.type_to_blk.items():
            modn__ssj = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[ghm__frmpy]))
            rifu__dfbb = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                ghm__frmpy], dtype=np.int64))
            wihk__qtfb = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, rifu__dfbb)
            snckz__stgwx = getattr(table, f'block_{ghm__frmpy}')
            with cgutils.for_range(builder, modn__ssj) as zqa__mnx:
                i = zqa__mnx.index
                sbh__jirqz = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    wihk__qtfb, i)
                btxsw__sdmob = types.none(table_type, types.List(
                    jewg__jkmfl), types.int64, types.int64)
                vccfc__bpfar = table_arg, snckz__stgwx, i, sbh__jirqz
                if zun__xfexf:
                    ensure_column_unboxed_codegen(context, builder,
                        btxsw__sdmob, vccfc__bpfar)
                else:
                    vaym__pkexi = dxy__bwtx.contains(sbh__jirqz)
                    with builder.if_then(vaym__pkexi):
                        ensure_column_unboxed_codegen(context, builder,
                            btxsw__sdmob, vccfc__bpfar)
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
    table_arg, zkj__wwcrt, xmypx__tbw, msnvq__nqy = args
    uuwz__ner = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    iuelp__xgl = cgutils.is_not_null(builder, table.parent)
    tucv__bsl = ListInstance(context, builder, sig.args[1], zkj__wwcrt)
    pjga__xaojk = tucv__bsl.getitem(xmypx__tbw)
    rpkw__bsyo = cgutils.alloca_once_value(builder, pjga__xaojk)
    gki__runc = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, rpkw__bsyo, gki__runc)
    with builder.if_then(is_null):
        with builder.if_else(iuelp__xgl) as (woixl__eao, hqful__nsxyk):
            with woixl__eao:
                mvf__yqlm = get_df_obj_column_codegen(context, builder,
                    uuwz__ner, table.parent, msnvq__nqy, sig.args[1].dtype)
                arr = uuwz__ner.to_native_value(sig.args[1].dtype, mvf__yqlm
                    ).value
                tucv__bsl.inititem(xmypx__tbw, arr, incref=False)
                uuwz__ner.decref(mvf__yqlm)
            with hqful__nsxyk:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    ghm__frmpy = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, dljjp__kjcok, bdzrj__fdwwu = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{ghm__frmpy}', dljjp__kjcok)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, yktr__inzbj = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = yktr__inzbj
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        fdyke__rhbk, ubmyo__stzwj = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, ubmyo__stzwj)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, fdyke__rhbk)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    yxlli__wzfk = list_type.instance_type if isinstance(list_type, types.
        TypeRef) else list_type
    assert isinstance(yxlli__wzfk, types.List), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        yxlli__wzfk = types.List(to_str_arr_if_dict_array(yxlli__wzfk.dtype))

    def codegen(context, builder, sig, args):
        zilk__bmlc = args[1]
        bdzrj__fdwwu, uthj__uhs = ListInstance.allocate_ex(context, builder,
            yxlli__wzfk, zilk__bmlc)
        uthj__uhs.size = zilk__bmlc
        return uthj__uhs.value
    sig = yxlli__wzfk(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    pwwp__xbt = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(pwwp__xbt)

    def codegen(context, builder, sig, args):
        zilk__bmlc, bdzrj__fdwwu = args
        bdzrj__fdwwu, uthj__uhs = ListInstance.allocate_ex(context, builder,
            list_type, zilk__bmlc)
        uthj__uhs.size = zilk__bmlc
        return uthj__uhs.value
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
        yash__dcmod = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(yash__dcmod)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    uqzt__wro = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        kfmu__euvof = used_cols.instance_type
        fgc__moxnr = np.array(kfmu__euvof.meta, dtype=np.int64)
        uqzt__wro['used_cols_vals'] = fgc__moxnr
        goqp__kwnf = set([T.block_nums[i] for i in fgc__moxnr])
    else:
        fgc__moxnr = None
    agrqm__kyayj = 'def table_filter_func(T, idx, used_cols=None):\n'
    agrqm__kyayj += f'  T2 = init_table(T, False)\n'
    agrqm__kyayj += f'  l = 0\n'
    if fgc__moxnr is not None and len(fgc__moxnr) == 0:
        agrqm__kyayj += f'  l = _get_idx_length(idx, len(T))\n'
        agrqm__kyayj += f'  T2 = set_table_len(T2, l)\n'
        agrqm__kyayj += f'  return T2\n'
        jfy__jqzuc = {}
        exec(agrqm__kyayj, uqzt__wro, jfy__jqzuc)
        return jfy__jqzuc['table_filter_func']
    if fgc__moxnr is not None:
        agrqm__kyayj += f'  used_set = set(used_cols_vals)\n'
    for ghm__frmpy in T.type_to_blk.values():
        agrqm__kyayj += (
            f'  arr_list_{ghm__frmpy} = get_table_block(T, {ghm__frmpy})\n')
        agrqm__kyayj += f"""  out_arr_list_{ghm__frmpy} = alloc_list_like(arr_list_{ghm__frmpy}, len(arr_list_{ghm__frmpy}), False)
"""
        if fgc__moxnr is None or ghm__frmpy in goqp__kwnf:
            uqzt__wro[f'arr_inds_{ghm__frmpy}'] = np.array(T.
                block_to_arr_ind[ghm__frmpy], dtype=np.int64)
            agrqm__kyayj += f'  for i in range(len(arr_list_{ghm__frmpy})):\n'
            agrqm__kyayj += (
                f'    arr_ind_{ghm__frmpy} = arr_inds_{ghm__frmpy}[i]\n')
            if fgc__moxnr is not None:
                agrqm__kyayj += (
                    f'    if arr_ind_{ghm__frmpy} not in used_set: continue\n')
            agrqm__kyayj += f"""    ensure_column_unboxed(T, arr_list_{ghm__frmpy}, i, arr_ind_{ghm__frmpy})
"""
            agrqm__kyayj += f"""    out_arr_{ghm__frmpy} = ensure_contig_if_np(arr_list_{ghm__frmpy}[i][idx])
"""
            agrqm__kyayj += f'    l = len(out_arr_{ghm__frmpy})\n'
            agrqm__kyayj += (
                f'    out_arr_list_{ghm__frmpy}[i] = out_arr_{ghm__frmpy}\n')
        agrqm__kyayj += (
            f'  T2 = set_table_block(T2, out_arr_list_{ghm__frmpy}, {ghm__frmpy})\n'
            )
    agrqm__kyayj += f'  T2 = set_table_len(T2, l)\n'
    agrqm__kyayj += f'  return T2\n'
    jfy__jqzuc = {}
    exec(agrqm__kyayj, uqzt__wro, jfy__jqzuc)
    return jfy__jqzuc['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    jto__nsgx = list(idx.instance_type.meta)
    fjn__tfxn = tuple(np.array(T.arr_types, dtype=object)[jto__nsgx])
    nnyq__bbgfj = TableType(fjn__tfxn)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    bbp__hyja = is_overload_true(copy_arrs)
    uqzt__wro = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': nnyq__bbgfj}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        udtbh__upah = set(kept_cols)
        uqzt__wro['kept_cols'] = np.array(kept_cols, np.int64)
        fnq__fvf = True
    else:
        fnq__fvf = False
    fdcfx__xii = {i: c for i, c in enumerate(jto__nsgx)}
    agrqm__kyayj = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    agrqm__kyayj += f'  T2 = init_table(out_table_typ, False)\n'
    agrqm__kyayj += f'  T2 = set_table_len(T2, len(T))\n'
    if fnq__fvf and len(udtbh__upah) == 0:
        agrqm__kyayj += f'  return T2\n'
        jfy__jqzuc = {}
        exec(agrqm__kyayj, uqzt__wro, jfy__jqzuc)
        return jfy__jqzuc['table_subset']
    if fnq__fvf:
        agrqm__kyayj += f'  kept_cols_set = set(kept_cols)\n'
    for typ, ghm__frmpy in nnyq__bbgfj.type_to_blk.items():
        lkm__uweym = T.type_to_blk[typ]
        agrqm__kyayj += (
            f'  arr_list_{ghm__frmpy} = get_table_block(T, {lkm__uweym})\n')
        agrqm__kyayj += f"""  out_arr_list_{ghm__frmpy} = alloc_list_like(arr_list_{ghm__frmpy}, {len(nnyq__bbgfj.block_to_arr_ind[ghm__frmpy])}, False)
"""
        ykw__swlot = True
        if fnq__fvf:
            rqb__ebo = set(nnyq__bbgfj.block_to_arr_ind[ghm__frmpy])
            dbhi__bogxa = rqb__ebo & udtbh__upah
            ykw__swlot = len(dbhi__bogxa) > 0
        if ykw__swlot:
            uqzt__wro[f'out_arr_inds_{ghm__frmpy}'] = np.array(nnyq__bbgfj.
                block_to_arr_ind[ghm__frmpy], dtype=np.int64)
            agrqm__kyayj += (
                f'  for i in range(len(out_arr_list_{ghm__frmpy})):\n')
            agrqm__kyayj += (
                f'    out_arr_ind_{ghm__frmpy} = out_arr_inds_{ghm__frmpy}[i]\n'
                )
            if fnq__fvf:
                agrqm__kyayj += (
                    f'    if out_arr_ind_{ghm__frmpy} not in kept_cols_set: continue\n'
                    )
            ibqh__aswca = []
            aify__cvhyd = []
            for cyc__erd in nnyq__bbgfj.block_to_arr_ind[ghm__frmpy]:
                drya__gxq = fdcfx__xii[cyc__erd]
                ibqh__aswca.append(drya__gxq)
                lcenz__hxnj = T.block_offsets[drya__gxq]
                aify__cvhyd.append(lcenz__hxnj)
            uqzt__wro[f'in_logical_idx_{ghm__frmpy}'] = np.array(ibqh__aswca,
                dtype=np.int64)
            uqzt__wro[f'in_physical_idx_{ghm__frmpy}'] = np.array(aify__cvhyd,
                dtype=np.int64)
            agrqm__kyayj += (
                f'    logical_idx_{ghm__frmpy} = in_logical_idx_{ghm__frmpy}[i]\n'
                )
            agrqm__kyayj += (
                f'    physical_idx_{ghm__frmpy} = in_physical_idx_{ghm__frmpy}[i]\n'
                )
            agrqm__kyayj += f"""    ensure_column_unboxed(T, arr_list_{ghm__frmpy}, physical_idx_{ghm__frmpy}, logical_idx_{ghm__frmpy})
"""
            slzn__zzq = '.copy()' if bbp__hyja else ''
            agrqm__kyayj += f"""    out_arr_list_{ghm__frmpy}[i] = arr_list_{ghm__frmpy}[physical_idx_{ghm__frmpy}]{slzn__zzq}
"""
        agrqm__kyayj += (
            f'  T2 = set_table_block(T2, out_arr_list_{ghm__frmpy}, {ghm__frmpy})\n'
            )
    agrqm__kyayj += f'  return T2\n'
    jfy__jqzuc = {}
    exec(agrqm__kyayj, uqzt__wro, jfy__jqzuc)
    return jfy__jqzuc['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    wmmfr__gmi = args[0]
    if equiv_set.has_shape(wmmfr__gmi):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=wmmfr__gmi, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (wmmfr__gmi)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    wmmfr__gmi = args[0]
    if equiv_set.has_shape(wmmfr__gmi):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            wmmfr__gmi)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    agrqm__kyayj = 'def impl(T):\n'
    agrqm__kyayj += f'  T2 = init_table(T, True)\n'
    agrqm__kyayj += f'  l = len(T)\n'
    uqzt__wro = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for ghm__frmpy in T.type_to_blk.values():
        uqzt__wro[f'arr_inds_{ghm__frmpy}'] = np.array(T.block_to_arr_ind[
            ghm__frmpy], dtype=np.int64)
        agrqm__kyayj += (
            f'  arr_list_{ghm__frmpy} = get_table_block(T, {ghm__frmpy})\n')
        agrqm__kyayj += f"""  out_arr_list_{ghm__frmpy} = alloc_list_like(arr_list_{ghm__frmpy}, len(arr_list_{ghm__frmpy}), True)
"""
        agrqm__kyayj += f'  for i in range(len(arr_list_{ghm__frmpy})):\n'
        agrqm__kyayj += (
            f'    arr_ind_{ghm__frmpy} = arr_inds_{ghm__frmpy}[i]\n')
        agrqm__kyayj += f"""    ensure_column_unboxed(T, arr_list_{ghm__frmpy}, i, arr_ind_{ghm__frmpy})
"""
        agrqm__kyayj += f"""    out_arr_{ghm__frmpy} = decode_if_dict_array(arr_list_{ghm__frmpy}[i])
"""
        agrqm__kyayj += (
            f'    out_arr_list_{ghm__frmpy}[i] = out_arr_{ghm__frmpy}\n')
        agrqm__kyayj += (
            f'  T2 = set_table_block(T2, out_arr_list_{ghm__frmpy}, {ghm__frmpy})\n'
            )
    agrqm__kyayj += f'  T2 = set_table_len(T2, l)\n'
    agrqm__kyayj += f'  return T2\n'
    jfy__jqzuc = {}
    exec(agrqm__kyayj, uqzt__wro, jfy__jqzuc)
    return jfy__jqzuc['impl']


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
        vmso__lkzx = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        vmso__lkzx = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            vmso__lkzx.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        jpwa__sxf, kuor__ciy = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = kuor__ciy
        illq__mqu = cgutils.unpack_tuple(builder, jpwa__sxf)
        for i, snckz__stgwx in enumerate(illq__mqu):
            setattr(table, f'block_{i}', snckz__stgwx)
            context.nrt.incref(builder, types.List(vmso__lkzx[i]), snckz__stgwx
                )
        return table._getvalue()
    table_type = TableType(tuple(vmso__lkzx), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    uqzt__wro = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        uqzt__wro['kept_cols'] = np.array(list(kept_cols), np.int64)
        fnq__fvf = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        fnq__fvf = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    wtpe__dfji = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        wtpe__dfji else extra_arrs_t.types[i - wtpe__dfji] for i in
        in_col_inds)) if is_overload_none(out_table_type_t
        ) else unwrap_typeref(out_table_type_t)
    agrqm__kyayj = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    agrqm__kyayj += f'  T1 = in_table_t\n'
    agrqm__kyayj += f'  T2 = init_table(out_table_type, False)\n'
    agrqm__kyayj += f'  T2 = set_table_len(T2, len(T1))\n'
    if fnq__fvf and len(kept_cols) == 0:
        agrqm__kyayj += f'  return T2\n'
        jfy__jqzuc = {}
        exec(agrqm__kyayj, uqzt__wro, jfy__jqzuc)
        return jfy__jqzuc['impl']
    if fnq__fvf:
        agrqm__kyayj += f'  kept_cols_set = set(kept_cols)\n'
    for typ, ghm__frmpy in out_table_type.type_to_blk.items():
        uqzt__wro[f'arr_list_typ_{ghm__frmpy}'] = types.List(typ)
        modn__ssj = len(out_table_type.block_to_arr_ind[ghm__frmpy])
        agrqm__kyayj += f"""  out_arr_list_{ghm__frmpy} = alloc_list_like(arr_list_typ_{ghm__frmpy}, {modn__ssj}, False)
"""
        if typ in in_table_t.type_to_blk:
            ixgcm__fqmv = in_table_t.type_to_blk[typ]
            hwwn__dfrmx = []
            yve__bvkd = []
            for owvzw__tti in out_table_type.block_to_arr_ind[ghm__frmpy]:
                hzi__wkvn = in_col_inds[owvzw__tti]
                if hzi__wkvn < wtpe__dfji:
                    hwwn__dfrmx.append(in_table_t.block_offsets[hzi__wkvn])
                    yve__bvkd.append(hzi__wkvn)
                else:
                    hwwn__dfrmx.append(-1)
                    yve__bvkd.append(-1)
            uqzt__wro[f'in_idxs_{ghm__frmpy}'] = np.array(hwwn__dfrmx, np.int64
                )
            uqzt__wro[f'in_arr_inds_{ghm__frmpy}'] = np.array(yve__bvkd, np
                .int64)
            if fnq__fvf:
                uqzt__wro[f'out_arr_inds_{ghm__frmpy}'] = np.array(
                    out_table_type.block_to_arr_ind[ghm__frmpy], dtype=np.int64
                    )
            agrqm__kyayj += (
                f'  in_arr_list_{ghm__frmpy} = get_table_block(T1, {ixgcm__fqmv})\n'
                )
            agrqm__kyayj += (
                f'  for i in range(len(out_arr_list_{ghm__frmpy})):\n')
            agrqm__kyayj += (
                f'    in_offset_{ghm__frmpy} = in_idxs_{ghm__frmpy}[i]\n')
            agrqm__kyayj += f'    if in_offset_{ghm__frmpy} == -1:\n'
            agrqm__kyayj += f'      continue\n'
            agrqm__kyayj += (
                f'    in_arr_ind_{ghm__frmpy} = in_arr_inds_{ghm__frmpy}[i]\n')
            if fnq__fvf:
                agrqm__kyayj += f"""    if out_arr_inds_{ghm__frmpy}[i] not in kept_cols_set: continue
"""
            agrqm__kyayj += f"""    ensure_column_unboxed(T1, in_arr_list_{ghm__frmpy}, in_offset_{ghm__frmpy}, in_arr_ind_{ghm__frmpy})
"""
            agrqm__kyayj += f"""    out_arr_list_{ghm__frmpy}[i] = in_arr_list_{ghm__frmpy}[in_offset_{ghm__frmpy}]
"""
        for i, owvzw__tti in enumerate(out_table_type.block_to_arr_ind[
            ghm__frmpy]):
            if owvzw__tti not in kept_cols:
                continue
            hzi__wkvn = in_col_inds[owvzw__tti]
            if hzi__wkvn >= wtpe__dfji:
                agrqm__kyayj += f"""  out_arr_list_{ghm__frmpy}[{i}] = extra_arrs_t[{hzi__wkvn - wtpe__dfji}]
"""
        agrqm__kyayj += (
            f'  T2 = set_table_block(T2, out_arr_list_{ghm__frmpy}, {ghm__frmpy})\n'
            )
    agrqm__kyayj += f'  return T2\n'
    uqzt__wro.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    jfy__jqzuc = {}
    exec(agrqm__kyayj, uqzt__wro, jfy__jqzuc)
    return jfy__jqzuc['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    wtpe__dfji = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < wtpe__dfji else
        extra_arrs_t.types[i - wtpe__dfji] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    qmu__qwpy = None
    if not is_overload_none(in_table_t):
        for i, jewg__jkmfl in enumerate(in_table_t.types):
            if jewg__jkmfl != types.none:
                qmu__qwpy = f'in_table_t[{i}]'
                break
    if qmu__qwpy is None:
        for i, jewg__jkmfl in enumerate(extra_arrs_t.types):
            if jewg__jkmfl != types.none:
                qmu__qwpy = f'extra_arrs_t[{i}]'
                break
    assert qmu__qwpy is not None, 'no array found in input data'
    agrqm__kyayj = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    agrqm__kyayj += f'  T1 = in_table_t\n'
    agrqm__kyayj += f'  T2 = init_table(out_table_type, False)\n'
    agrqm__kyayj += f'  T2 = set_table_len(T2, len({qmu__qwpy}))\n'
    uqzt__wro = {}
    for typ, ghm__frmpy in out_table_type.type_to_blk.items():
        uqzt__wro[f'arr_list_typ_{ghm__frmpy}'] = types.List(typ)
        modn__ssj = len(out_table_type.block_to_arr_ind[ghm__frmpy])
        agrqm__kyayj += f"""  out_arr_list_{ghm__frmpy} = alloc_list_like(arr_list_typ_{ghm__frmpy}, {modn__ssj}, False)
"""
        for i, owvzw__tti in enumerate(out_table_type.block_to_arr_ind[
            ghm__frmpy]):
            if owvzw__tti not in kept_cols:
                continue
            hzi__wkvn = in_col_inds[owvzw__tti]
            if hzi__wkvn < wtpe__dfji:
                agrqm__kyayj += (
                    f'  out_arr_list_{ghm__frmpy}[{i}] = T1[{hzi__wkvn}]\n')
            else:
                agrqm__kyayj += f"""  out_arr_list_{ghm__frmpy}[{i}] = extra_arrs_t[{hzi__wkvn - wtpe__dfji}]
"""
        agrqm__kyayj += (
            f'  T2 = set_table_block(T2, out_arr_list_{ghm__frmpy}, {ghm__frmpy})\n'
            )
    agrqm__kyayj += f'  return T2\n'
    uqzt__wro.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    jfy__jqzuc = {}
    exec(agrqm__kyayj, uqzt__wro, jfy__jqzuc)
    return jfy__jqzuc['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    czypg__fhjf = args[0]
    wpbhg__rfhr = args[1]
    if equiv_set.has_shape(czypg__fhjf):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            czypg__fhjf)[0], None), pre=[])
    if equiv_set.has_shape(wpbhg__rfhr):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            wpbhg__rfhr)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
