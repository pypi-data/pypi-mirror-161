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
            zcmz__eaiuj = 0
            watxw__ohb = []
            for i in range(usecols[-1] + 1):
                if i == usecols[zcmz__eaiuj]:
                    watxw__ohb.append(arrs[zcmz__eaiuj])
                    zcmz__eaiuj += 1
                else:
                    watxw__ohb.append(None)
            for husd__ume in range(usecols[-1] + 1, num_arrs):
                watxw__ohb.append(None)
            self.arrays = watxw__ohb
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((jmr__xpex == sayl__rms).all() for jmr__xpex,
            sayl__rms in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        osv__mtl = len(self.arrays)
        piz__kwh = dict(zip(range(osv__mtl), self.arrays))
        df = pd.DataFrame(piz__kwh, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        gapvv__wceoo = []
        exkwj__ijf = []
        ivo__oyrcq = {}
        xxcm__nhsml = {}
        kllva__seutk = defaultdict(int)
        ysod__fmvrf = defaultdict(list)
        if not has_runtime_cols:
            for i, qusa__ywp in enumerate(arr_types):
                if qusa__ywp not in ivo__oyrcq:
                    lhpy__hiqcm = len(ivo__oyrcq)
                    ivo__oyrcq[qusa__ywp] = lhpy__hiqcm
                    xxcm__nhsml[lhpy__hiqcm] = qusa__ywp
                mhx__ycy = ivo__oyrcq[qusa__ywp]
                gapvv__wceoo.append(mhx__ycy)
                exkwj__ijf.append(kllva__seutk[mhx__ycy])
                kllva__seutk[mhx__ycy] += 1
                ysod__fmvrf[mhx__ycy].append(i)
        self.block_nums = gapvv__wceoo
        self.block_offsets = exkwj__ijf
        self.type_to_blk = ivo__oyrcq
        self.blk_to_type = xxcm__nhsml
        self.block_to_arr_ind = ysod__fmvrf
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
            qpsa__sbp = [(f'block_{i}', types.List(qusa__ywp)) for i,
                qusa__ywp in enumerate(fe_type.arr_types)]
        else:
            qpsa__sbp = [(f'block_{mhx__ycy}', types.List(qusa__ywp)) for 
                qusa__ywp, mhx__ycy in fe_type.type_to_blk.items()]
        qpsa__sbp.append(('parent', types.pyobject))
        qpsa__sbp.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, qpsa__sbp)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    awrn__ahghp = c.pyapi.object_getattr_string(val, 'arrays')
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    table.parent = cgutils.get_null_value(table.parent.type)
    kaupy__seaai = c.pyapi.make_none()
    rjwld__edmn = c.context.get_constant(types.int64, 0)
    khopx__adqne = cgutils.alloca_once_value(c.builder, rjwld__edmn)
    for qusa__ywp, mhx__ycy in typ.type_to_blk.items():
        hig__vlf = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[mhx__ycy]))
        husd__ume, gyg__ytg = ListInstance.allocate_ex(c.context, c.builder,
            types.List(qusa__ywp), hig__vlf)
        gyg__ytg.size = hig__vlf
        qfr__toypc = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[mhx__ycy],
            dtype=np.int64))
        lhrn__wuhnk = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, qfr__toypc)
        with cgutils.for_range(c.builder, hig__vlf) as tkbuu__twrc:
            i = tkbuu__twrc.index
            pac__fhjd = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), lhrn__wuhnk, i)
            dmxaq__fpp = c.pyapi.long_from_longlong(pac__fhjd)
            yrq__rbc = c.pyapi.object_getitem(awrn__ahghp, dmxaq__fpp)
            gsq__lqjx = c.builder.icmp_unsigned('==', yrq__rbc, kaupy__seaai)
            with c.builder.if_else(gsq__lqjx) as (tgppp__gtetj, uxd__jkif):
                with tgppp__gtetj:
                    sbp__iimv = c.context.get_constant_null(qusa__ywp)
                    gyg__ytg.inititem(i, sbp__iimv, incref=False)
                with uxd__jkif:
                    yrmmm__unl = c.pyapi.call_method(yrq__rbc, '__len__', ())
                    uemv__gsae = c.pyapi.long_as_longlong(yrmmm__unl)
                    c.builder.store(uemv__gsae, khopx__adqne)
                    c.pyapi.decref(yrmmm__unl)
                    arr = c.pyapi.to_native_value(qusa__ywp, yrq__rbc).value
                    gyg__ytg.inititem(i, arr, incref=False)
            c.pyapi.decref(yrq__rbc)
            c.pyapi.decref(dmxaq__fpp)
        setattr(table, f'block_{mhx__ycy}', gyg__ytg.value)
    table.len = c.builder.load(khopx__adqne)
    c.pyapi.decref(awrn__ahghp)
    c.pyapi.decref(kaupy__seaai)
    mdkt__qyvvh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(table._getvalue(), is_error=mdkt__qyvvh)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        rzv__awekt = c.context.get_constant(types.int64, 0)
        for i, qusa__ywp in enumerate(typ.arr_types):
            watxw__ohb = getattr(table, f'block_{i}')
            fqt__iyiup = ListInstance(c.context, c.builder, types.List(
                qusa__ywp), watxw__ohb)
            rzv__awekt = c.builder.add(rzv__awekt, fqt__iyiup.size)
        xlzvw__zik = c.pyapi.list_new(rzv__awekt)
        sta__aekd = c.context.get_constant(types.int64, 0)
        for i, qusa__ywp in enumerate(typ.arr_types):
            watxw__ohb = getattr(table, f'block_{i}')
            fqt__iyiup = ListInstance(c.context, c.builder, types.List(
                qusa__ywp), watxw__ohb)
            with cgutils.for_range(c.builder, fqt__iyiup.size) as tkbuu__twrc:
                i = tkbuu__twrc.index
                arr = fqt__iyiup.getitem(i)
                c.context.nrt.incref(c.builder, qusa__ywp, arr)
                idx = c.builder.add(sta__aekd, i)
                c.pyapi.list_setitem(xlzvw__zik, idx, c.pyapi.
                    from_native_value(qusa__ywp, arr, c.env_manager))
            sta__aekd = c.builder.add(sta__aekd, fqt__iyiup.size)
        yuor__jxdn = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        zuzjl__gfga = c.pyapi.call_function_objargs(yuor__jxdn, (xlzvw__zik,))
        c.pyapi.decref(yuor__jxdn)
        c.pyapi.decref(xlzvw__zik)
        c.context.nrt.decref(c.builder, typ, val)
        return zuzjl__gfga
    xlzvw__zik = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    bquy__fbjes = cgutils.is_not_null(c.builder, table.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for qusa__ywp, mhx__ycy in typ.type_to_blk.items():
        watxw__ohb = getattr(table, f'block_{mhx__ycy}')
        fqt__iyiup = ListInstance(c.context, c.builder, types.List(
            qusa__ywp), watxw__ohb)
        qfr__toypc = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[mhx__ycy],
            dtype=np.int64))
        lhrn__wuhnk = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, qfr__toypc)
        with cgutils.for_range(c.builder, fqt__iyiup.size) as tkbuu__twrc:
            i = tkbuu__twrc.index
            pac__fhjd = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), lhrn__wuhnk, i)
            arr = fqt__iyiup.getitem(i)
            pceg__eddy = cgutils.alloca_once_value(c.builder, arr)
            mva__bnbs = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(qusa__ywp))
            is_null = is_ll_eq(c.builder, pceg__eddy, mva__bnbs)
            with c.builder.if_else(c.builder.and_(is_null, c.builder.not_(
                ensure_unboxed))) as (tgppp__gtetj, uxd__jkif):
                with tgppp__gtetj:
                    kaupy__seaai = c.pyapi.make_none()
                    c.pyapi.list_setitem(xlzvw__zik, pac__fhjd, kaupy__seaai)
                with uxd__jkif:
                    yrq__rbc = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(is_null, bquy__fbjes)
                        ) as (ilz__ogcil, tahw__axqvw):
                        with ilz__ogcil:
                            vlf__dqp = get_df_obj_column_codegen(c.context,
                                c.builder, c.pyapi, table.parent, pac__fhjd,
                                qusa__ywp)
                            c.builder.store(vlf__dqp, yrq__rbc)
                        with tahw__axqvw:
                            c.context.nrt.incref(c.builder, qusa__ywp, arr)
                            c.builder.store(c.pyapi.from_native_value(
                                qusa__ywp, arr, c.env_manager), yrq__rbc)
                    c.pyapi.list_setitem(xlzvw__zik, pac__fhjd, c.builder.
                        load(yrq__rbc))
    yuor__jxdn = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    zuzjl__gfga = c.pyapi.call_function_objargs(yuor__jxdn, (xlzvw__zik,))
    c.pyapi.decref(yuor__jxdn)
    c.pyapi.decref(xlzvw__zik)
    c.context.nrt.decref(c.builder, typ, val)
    return zuzjl__gfga


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
        mkm__mglo = context.get_constant(types.int64, 0)
        for i, qusa__ywp in enumerate(table_type.arr_types):
            watxw__ohb = getattr(table, f'block_{i}')
            fqt__iyiup = ListInstance(context, builder, types.List(
                qusa__ywp), watxw__ohb)
            mkm__mglo = builder.add(mkm__mglo, fqt__iyiup.size)
        return mkm__mglo
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    table = cgutils.create_struct_proxy(table_type)(context, builder, table_arg
        )
    mhx__ycy = table_type.block_nums[col_ind]
    gpalm__jpsju = table_type.block_offsets[col_ind]
    watxw__ohb = getattr(table, f'block_{mhx__ycy}')
    tvj__vwqo = types.none(table_type, types.List(arr_type), types.int64,
        types.int64)
    bnce__juimz = context.get_constant(types.int64, col_ind)
    jnmah__pxf = context.get_constant(types.int64, gpalm__jpsju)
    tliz__nuej = table_arg, watxw__ohb, jnmah__pxf, bnce__juimz
    ensure_column_unboxed_codegen(context, builder, tvj__vwqo, tliz__nuej)
    fqt__iyiup = ListInstance(context, builder, types.List(arr_type),
        watxw__ohb)
    arr = fqt__iyiup.getitem(gpalm__jpsju)
    return arr


@intrinsic
def get_table_data(typingctx, table_type, ind_typ):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, husd__ume = args
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
    ttt__zwsnt = list(ind_typ.instance_type.meta)
    xfk__aqo = defaultdict(list)
    for ind in ttt__zwsnt:
        xfk__aqo[table_type.block_nums[ind]].append(table_type.
            block_offsets[ind])

    def codegen(context, builder, sig, args):
        table_arg, husd__ume = args
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        for mhx__ycy, wzhf__oqf in xfk__aqo.items():
            arr_type = table_type.blk_to_type[mhx__ycy]
            watxw__ohb = getattr(table, f'block_{mhx__ycy}')
            fqt__iyiup = ListInstance(context, builder, types.List(arr_type
                ), watxw__ohb)
            sbp__iimv = context.get_constant_null(arr_type)
            if len(wzhf__oqf) == 1:
                gpalm__jpsju = wzhf__oqf[0]
                arr = fqt__iyiup.getitem(gpalm__jpsju)
                context.nrt.decref(builder, arr_type, arr)
                fqt__iyiup.inititem(gpalm__jpsju, sbp__iimv, incref=False)
            else:
                hig__vlf = context.get_constant(types.int64, len(wzhf__oqf))
                bzwev__rpu = context.make_constant_array(builder, types.
                    Array(types.int64, 1, 'C'), np.array(wzhf__oqf, dtype=
                    np.int64))
                keft__vkx = context.make_array(types.Array(types.int64, 1, 'C')
                    )(context, builder, bzwev__rpu)
                with cgutils.for_range(builder, hig__vlf) as tkbuu__twrc:
                    i = tkbuu__twrc.index
                    gpalm__jpsju = _getitem_array_single_int(context,
                        builder, types.int64, types.Array(types.int64, 1,
                        'C'), keft__vkx, i)
                    arr = fqt__iyiup.getitem(gpalm__jpsju)
                    context.nrt.decref(builder, arr_type, arr)
                    fqt__iyiup.inititem(gpalm__jpsju, sbp__iimv, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    rjwld__edmn = context.get_constant(types.int64, 0)
    ocz__ypgw = context.get_constant(types.int64, 1)
    accqw__xen = arr_type not in in_table_type.type_to_blk
    for qusa__ywp, mhx__ycy in out_table_type.type_to_blk.items():
        if qusa__ywp in in_table_type.type_to_blk:
            rkk__ohpj = in_table_type.type_to_blk[qusa__ywp]
            gyg__ytg = ListInstance(context, builder, types.List(qusa__ywp),
                getattr(in_table, f'block_{rkk__ohpj}'))
            context.nrt.incref(builder, types.List(qusa__ywp), gyg__ytg.value)
            setattr(out_table, f'block_{mhx__ycy}', gyg__ytg.value)
    if accqw__xen:
        husd__ume, gyg__ytg = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), ocz__ypgw)
        gyg__ytg.size = ocz__ypgw
        gyg__ytg.inititem(rjwld__edmn, arr_arg, incref=True)
        mhx__ycy = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{mhx__ycy}', gyg__ytg.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        mhx__ycy = out_table_type.type_to_blk[arr_type]
        gyg__ytg = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{mhx__ycy}'))
        if is_new_col:
            n = gyg__ytg.size
            hvczp__bkvqv = builder.add(n, ocz__ypgw)
            gyg__ytg.resize(hvczp__bkvqv)
            gyg__ytg.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            wxyis__cjtsh = context.get_constant(types.int64, out_table_type
                .block_offsets[col_ind])
            gyg__ytg.setitem(wxyis__cjtsh, arr_arg, incref=True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            wxyis__cjtsh = context.get_constant(types.int64, out_table_type
                .block_offsets[col_ind])
            n = gyg__ytg.size
            hvczp__bkvqv = builder.add(n, ocz__ypgw)
            gyg__ytg.resize(hvczp__bkvqv)
            context.nrt.incref(builder, arr_type, gyg__ytg.getitem(
                wxyis__cjtsh))
            gyg__ytg.move(builder.add(wxyis__cjtsh, ocz__ypgw),
                wxyis__cjtsh, builder.sub(n, wxyis__cjtsh))
            gyg__ytg.setitem(wxyis__cjtsh, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    ufcx__kyf = in_table_type.arr_types[col_ind]
    if ufcx__kyf in out_table_type.type_to_blk:
        mhx__ycy = out_table_type.type_to_blk[ufcx__kyf]
        ldn__mtnn = getattr(out_table, f'block_{mhx__ycy}')
        pau__ilmm = types.List(ufcx__kyf)
        wxyis__cjtsh = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        zeqo__yvykv = pau__ilmm.dtype(pau__ilmm, types.intp)
        ahv__nkol = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), zeqo__yvykv, (ldn__mtnn, wxyis__cjtsh))
        context.nrt.decref(builder, ufcx__kyf, ahv__nkol)


def generate_set_table_data_code(table, ind, arr_type, used_cols, is_null=False
    ):
    ecssq__dkrta = list(table.arr_types)
    if ind == len(ecssq__dkrta):
        tla__grmb = None
        ecssq__dkrta.append(arr_type)
    else:
        tla__grmb = table.arr_types[ind]
        ecssq__dkrta[ind] = arr_type
    gujcu__tjev = TableType(tuple(ecssq__dkrta))
    pya__nmwmj = {'init_table': init_table, 'get_table_block':
        get_table_block, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'set_table_parent':
        set_table_parent, 'alloc_list_like': alloc_list_like,
        'out_table_typ': gujcu__tjev}
    ahocy__xyea = 'def set_table_data(table, ind, arr, used_cols=None):\n'
    ahocy__xyea += f'  T2 = init_table(out_table_typ, False)\n'
    ahocy__xyea += f'  T2 = set_table_len(T2, len(table))\n'
    ahocy__xyea += f'  T2 = set_table_parent(T2, table)\n'
    for typ, mhx__ycy in gujcu__tjev.type_to_blk.items():
        if typ in table.type_to_blk:
            ikj__qlp = table.type_to_blk[typ]
            ahocy__xyea += (
                f'  arr_list_{mhx__ycy} = get_table_block(table, {ikj__qlp})\n'
                )
            ahocy__xyea += f"""  out_arr_list_{mhx__ycy} = alloc_list_like(arr_list_{mhx__ycy}, {len(gujcu__tjev.block_to_arr_ind[mhx__ycy])}, False)
"""
            if used_cols is None or set(table.block_to_arr_ind[ikj__qlp]
                ) & used_cols:
                ahocy__xyea += f'  for i in range(len(arr_list_{mhx__ycy})):\n'
                if typ not in (tla__grmb, arr_type):
                    ahocy__xyea += (
                        f'    out_arr_list_{mhx__ycy}[i] = arr_list_{mhx__ycy}[i]\n'
                        )
                else:
                    yehwq__qsqb = table.block_to_arr_ind[ikj__qlp]
                    znmy__wxt = np.empty(len(yehwq__qsqb), np.int64)
                    fvpb__owyn = False
                    for haldt__fgk, pac__fhjd in enumerate(yehwq__qsqb):
                        if pac__fhjd != ind:
                            vyokz__lrdpr = gujcu__tjev.block_offsets[pac__fhjd]
                        else:
                            vyokz__lrdpr = -1
                            fvpb__owyn = True
                        znmy__wxt[haldt__fgk] = vyokz__lrdpr
                    pya__nmwmj[f'out_idxs_{mhx__ycy}'] = np.array(znmy__wxt,
                        np.int64)
                    ahocy__xyea += f'    out_idx = out_idxs_{mhx__ycy}[i]\n'
                    if fvpb__owyn:
                        ahocy__xyea += f'    if out_idx == -1:\n'
                        ahocy__xyea += f'      continue\n'
                    ahocy__xyea += f"""    out_arr_list_{mhx__ycy}[out_idx] = arr_list_{mhx__ycy}[i]
"""
            if typ == arr_type and not is_null:
                ahocy__xyea += f"""  out_arr_list_{mhx__ycy}[{gujcu__tjev.block_offsets[ind]}] = arr
"""
        else:
            pya__nmwmj[f'arr_list_typ_{mhx__ycy}'] = types.List(arr_type)
            ahocy__xyea += f"""  out_arr_list_{mhx__ycy} = alloc_list_like(arr_list_typ_{mhx__ycy}, 1, False)
"""
            if not is_null:
                ahocy__xyea += f'  out_arr_list_{mhx__ycy}[0] = arr\n'
        ahocy__xyea += (
            f'  T2 = set_table_block(T2, out_arr_list_{mhx__ycy}, {mhx__ycy})\n'
            )
    ahocy__xyea += f'  return T2\n'
    kfyhn__xgcda = {}
    exec(ahocy__xyea, pya__nmwmj, kfyhn__xgcda)
    return kfyhn__xgcda['set_table_data']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data(table, ind, arr, used_cols=None):
    if is_overload_none(used_cols):
        cts__mauir = None
    else:
        cts__mauir = set(used_cols.instance_type.meta)
    ueovi__drf = get_overload_const_int(ind)
    return generate_set_table_data_code(table, ueovi__drf, arr, cts__mauir)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def set_table_data_null(table, ind, arr, used_cols=None):
    ueovi__drf = get_overload_const_int(ind)
    arr_type = arr.instance_type
    if is_overload_none(used_cols):
        cts__mauir = None
    else:
        cts__mauir = set(used_cols.instance_type.meta)
    return generate_set_table_data_code(table, ueovi__drf, arr_type,
        cts__mauir, is_null=True)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    xqlxb__hhy = args[0]
    if equiv_set.has_shape(xqlxb__hhy):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            xqlxb__hhy)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    avj__vilxa = []
    for qusa__ywp, mhx__ycy in table_type.type_to_blk.items():
        osp__wdrg = len(table_type.block_to_arr_ind[mhx__ycy])
        lzt__vxsic = []
        for i in range(osp__wdrg):
            pac__fhjd = table_type.block_to_arr_ind[mhx__ycy][i]
            lzt__vxsic.append(pyval.arrays[pac__fhjd])
        avj__vilxa.append(context.get_constant_generic(builder, types.List(
            qusa__ywp), lzt__vxsic))
    isew__fkd = context.get_constant_null(types.pyobject)
    hyney__lxzwt = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(avj__vilxa + [isew__fkd, hyney__lxzwt])


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
        for qusa__ywp, mhx__ycy in out_table_type.type_to_blk.items():
            ygis__csl = context.get_constant_null(types.List(qusa__ywp))
            setattr(table, f'block_{mhx__ycy}', ygis__csl)
        return table._getvalue()
    sig = out_table_type(table_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def init_table_from_lists(typingctx, tuple_of_lists_type, table_type):
    assert isinstance(tuple_of_lists_type, types.BaseTuple
        ), 'Tuple of data expected'
    pzpag__att = {}
    for i, typ in enumerate(tuple_of_lists_type):
        assert isinstance(typ, types.List), 'Each tuple element must be a list'
        pzpag__att[typ.dtype] = i
    mwu__fbsj = table_type.instance_type if isinstance(table_type, types.
        TypeRef) else table_type
    assert isinstance(mwu__fbsj, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        phpar__qgvwf, husd__ume = args
        table = cgutils.create_struct_proxy(mwu__fbsj)(context, builder)
        for qusa__ywp, mhx__ycy in mwu__fbsj.type_to_blk.items():
            idx = pzpag__att[qusa__ywp]
            jbwrz__kezd = signature(types.List(qusa__ywp),
                tuple_of_lists_type, types.literal(idx))
            yri__scyh = phpar__qgvwf, idx
            nefd__maqq = numba.cpython.tupleobj.static_getitem_tuple(context,
                builder, jbwrz__kezd, yri__scyh)
            setattr(table, f'block_{mhx__ycy}', nefd__maqq)
        return table._getvalue()
    sig = mwu__fbsj(tuple_of_lists_type, table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    mhx__ycy = get_overload_const_int(blk_type)
    arr_type = None
    for qusa__ywp, sayl__rms in table_type.type_to_blk.items():
        if sayl__rms == mhx__ycy:
            arr_type = qusa__ywp
            break
    assert arr_type is not None, 'invalid table type block'
    gdapo__nwmzo = types.List(arr_type)

    def codegen(context, builder, sig, args):
        table = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        watxw__ohb = getattr(table, f'block_{mhx__ycy}')
        return impl_ret_borrowed(context, builder, gdapo__nwmzo, watxw__ohb)
    sig = gdapo__nwmzo(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_table_unboxed(typingctx, table_type, used_cols_typ):

    def codegen(context, builder, sig, args):
        table_arg, fts__zxta = args
        hiwd__nbqq = context.get_python_api(builder)
        ldbpp__cyio = used_cols_typ == types.none
        if not ldbpp__cyio:
            lbmpm__kqpvi = numba.cpython.setobj.SetInstance(context,
                builder, types.Set(types.int64), fts__zxta)
        table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
            table_arg)
        for qusa__ywp, mhx__ycy in table_type.type_to_blk.items():
            hig__vlf = context.get_constant(types.int64, len(table_type.
                block_to_arr_ind[mhx__ycy]))
            qfr__toypc = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(table_type.block_to_arr_ind[
                mhx__ycy], dtype=np.int64))
            lhrn__wuhnk = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, qfr__toypc)
            watxw__ohb = getattr(table, f'block_{mhx__ycy}')
            with cgutils.for_range(builder, hig__vlf) as tkbuu__twrc:
                i = tkbuu__twrc.index
                pac__fhjd = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    lhrn__wuhnk, i)
                tvj__vwqo = types.none(table_type, types.List(qusa__ywp),
                    types.int64, types.int64)
                tliz__nuej = table_arg, watxw__ohb, i, pac__fhjd
                if ldbpp__cyio:
                    ensure_column_unboxed_codegen(context, builder,
                        tvj__vwqo, tliz__nuej)
                else:
                    eec__brpzt = lbmpm__kqpvi.contains(pac__fhjd)
                    with builder.if_then(eec__brpzt):
                        ensure_column_unboxed_codegen(context, builder,
                            tvj__vwqo, tliz__nuej)
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
    table_arg, fye__hswvx, jzvog__fzubt, ohkh__dadte = args
    hiwd__nbqq = context.get_python_api(builder)
    table = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    bquy__fbjes = cgutils.is_not_null(builder, table.parent)
    fqt__iyiup = ListInstance(context, builder, sig.args[1], fye__hswvx)
    kpqvp__fikg = fqt__iyiup.getitem(jzvog__fzubt)
    pceg__eddy = cgutils.alloca_once_value(builder, kpqvp__fikg)
    mva__bnbs = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    is_null = is_ll_eq(builder, pceg__eddy, mva__bnbs)
    with builder.if_then(is_null):
        with builder.if_else(bquy__fbjes) as (tgppp__gtetj, uxd__jkif):
            with tgppp__gtetj:
                yrq__rbc = get_df_obj_column_codegen(context, builder,
                    hiwd__nbqq, table.parent, ohkh__dadte, sig.args[1].dtype)
                arr = hiwd__nbqq.to_native_value(sig.args[1].dtype, yrq__rbc
                    ).value
                fqt__iyiup.inititem(jzvog__fzubt, arr, incref=False)
                hiwd__nbqq.decref(yrq__rbc)
            with uxd__jkif:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    mhx__ycy = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, xbws__exxss, husd__ume = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{mhx__ycy}', xbws__exxss)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, lvybr__sjey = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = lvybr__sjey
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def set_table_parent(typingctx, out_table_type, in_table_type):
    assert isinstance(in_table_type, TableType), 'table type expected'
    assert isinstance(out_table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        ohpc__gdpfx, zglc__gtnj = args
        in_table = cgutils.create_struct_proxy(in_table_type)(context,
            builder, zglc__gtnj)
        out_table = cgutils.create_struct_proxy(out_table_type)(context,
            builder, ohpc__gdpfx)
        out_table.parent = in_table.parent
        context.nrt.incref(builder, types.pyobject, out_table.parent)
        return impl_ret_borrowed(context, builder, out_table_type,
            out_table._getvalue())
    sig = out_table_type(out_table_type, in_table_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type, len_type, to_str_if_dict_t):
    gdapo__nwmzo = list_type.instance_type if isinstance(list_type, types.
        TypeRef) else list_type
    assert isinstance(gdapo__nwmzo, types.List
        ), 'list type or typeref expected'
    assert isinstance(len_type, types.Integer), 'integer type expected'
    assert is_overload_constant_bool(to_str_if_dict_t
        ), 'constant to_str_if_dict_t expected'
    if is_overload_true(to_str_if_dict_t):
        gdapo__nwmzo = types.List(to_str_arr_if_dict_array(gdapo__nwmzo.dtype))

    def codegen(context, builder, sig, args):
        hezo__uehjg = args[1]
        husd__ume, gyg__ytg = ListInstance.allocate_ex(context, builder,
            gdapo__nwmzo, hezo__uehjg)
        gyg__ytg.size = hezo__uehjg
        return gyg__ytg.value
    sig = gdapo__nwmzo(list_type, len_type, to_str_if_dict_t)
    return sig, codegen


@intrinsic
def alloc_empty_list_type(typingctx, size_typ, data_typ):
    assert isinstance(size_typ, types.Integer), 'Size must be an integer'
    khw__jyfs = data_typ.instance_type if isinstance(data_typ, types.TypeRef
        ) else data_typ
    list_type = types.List(khw__jyfs)

    def codegen(context, builder, sig, args):
        hezo__uehjg, husd__ume = args
        husd__ume, gyg__ytg = ListInstance.allocate_ex(context, builder,
            list_type, hezo__uehjg)
        gyg__ytg.size = hezo__uehjg
        return gyg__ytg.value
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
        kte__exuh = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(kte__exuh)
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_filter(T, idx, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    pya__nmwmj = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if not is_overload_none(used_cols):
        fjik__ypyy = used_cols.instance_type
        ltowp__eqb = np.array(fjik__ypyy.meta, dtype=np.int64)
        pya__nmwmj['used_cols_vals'] = ltowp__eqb
        pcywe__ihoo = set([T.block_nums[i] for i in ltowp__eqb])
    else:
        ltowp__eqb = None
    ahocy__xyea = 'def table_filter_func(T, idx, used_cols=None):\n'
    ahocy__xyea += f'  T2 = init_table(T, False)\n'
    ahocy__xyea += f'  l = 0\n'
    if ltowp__eqb is not None and len(ltowp__eqb) == 0:
        ahocy__xyea += f'  l = _get_idx_length(idx, len(T))\n'
        ahocy__xyea += f'  T2 = set_table_len(T2, l)\n'
        ahocy__xyea += f'  return T2\n'
        kfyhn__xgcda = {}
        exec(ahocy__xyea, pya__nmwmj, kfyhn__xgcda)
        return kfyhn__xgcda['table_filter_func']
    if ltowp__eqb is not None:
        ahocy__xyea += f'  used_set = set(used_cols_vals)\n'
    for mhx__ycy in T.type_to_blk.values():
        ahocy__xyea += (
            f'  arr_list_{mhx__ycy} = get_table_block(T, {mhx__ycy})\n')
        ahocy__xyea += f"""  out_arr_list_{mhx__ycy} = alloc_list_like(arr_list_{mhx__ycy}, len(arr_list_{mhx__ycy}), False)
"""
        if ltowp__eqb is None or mhx__ycy in pcywe__ihoo:
            pya__nmwmj[f'arr_inds_{mhx__ycy}'] = np.array(T.
                block_to_arr_ind[mhx__ycy], dtype=np.int64)
            ahocy__xyea += f'  for i in range(len(arr_list_{mhx__ycy})):\n'
            ahocy__xyea += f'    arr_ind_{mhx__ycy} = arr_inds_{mhx__ycy}[i]\n'
            if ltowp__eqb is not None:
                ahocy__xyea += (
                    f'    if arr_ind_{mhx__ycy} not in used_set: continue\n')
            ahocy__xyea += f"""    ensure_column_unboxed(T, arr_list_{mhx__ycy}, i, arr_ind_{mhx__ycy})
"""
            ahocy__xyea += f"""    out_arr_{mhx__ycy} = ensure_contig_if_np(arr_list_{mhx__ycy}[i][idx])
"""
            ahocy__xyea += f'    l = len(out_arr_{mhx__ycy})\n'
            ahocy__xyea += (
                f'    out_arr_list_{mhx__ycy}[i] = out_arr_{mhx__ycy}\n')
        ahocy__xyea += (
            f'  T2 = set_table_block(T2, out_arr_list_{mhx__ycy}, {mhx__ycy})\n'
            )
    ahocy__xyea += f'  T2 = set_table_len(T2, l)\n'
    ahocy__xyea += f'  return T2\n'
    kfyhn__xgcda = {}
    exec(ahocy__xyea, pya__nmwmj, kfyhn__xgcda)
    return kfyhn__xgcda['table_filter_func']


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def table_subset(T, idx, copy_arrs, used_cols=None):
    trjmc__iqhny = list(idx.instance_type.meta)
    ecssq__dkrta = tuple(np.array(T.arr_types, dtype=object)[trjmc__iqhny])
    gujcu__tjev = TableType(ecssq__dkrta)
    if not is_overload_constant_bool(copy_arrs):
        raise_bodo_error('table_subset(): copy_arrs must be a constant')
    cqg__has = is_overload_true(copy_arrs)
    pya__nmwmj = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'out_table_typ': gujcu__tjev}
    if not is_overload_none(used_cols):
        kept_cols = used_cols.instance_type.meta
        lku__lxjks = set(kept_cols)
        pya__nmwmj['kept_cols'] = np.array(kept_cols, np.int64)
        iabk__jtdwe = True
    else:
        iabk__jtdwe = False
    cjubk__hzzk = {i: c for i, c in enumerate(trjmc__iqhny)}
    ahocy__xyea = 'def table_subset(T, idx, copy_arrs, used_cols=None):\n'
    ahocy__xyea += f'  T2 = init_table(out_table_typ, False)\n'
    ahocy__xyea += f'  T2 = set_table_len(T2, len(T))\n'
    if iabk__jtdwe and len(lku__lxjks) == 0:
        ahocy__xyea += f'  return T2\n'
        kfyhn__xgcda = {}
        exec(ahocy__xyea, pya__nmwmj, kfyhn__xgcda)
        return kfyhn__xgcda['table_subset']
    if iabk__jtdwe:
        ahocy__xyea += f'  kept_cols_set = set(kept_cols)\n'
    for typ, mhx__ycy in gujcu__tjev.type_to_blk.items():
        ikj__qlp = T.type_to_blk[typ]
        ahocy__xyea += (
            f'  arr_list_{mhx__ycy} = get_table_block(T, {ikj__qlp})\n')
        ahocy__xyea += f"""  out_arr_list_{mhx__ycy} = alloc_list_like(arr_list_{mhx__ycy}, {len(gujcu__tjev.block_to_arr_ind[mhx__ycy])}, False)
"""
        kyvi__tcqd = True
        if iabk__jtdwe:
            pram__jysut = set(gujcu__tjev.block_to_arr_ind[mhx__ycy])
            olxy__taovi = pram__jysut & lku__lxjks
            kyvi__tcqd = len(olxy__taovi) > 0
        if kyvi__tcqd:
            pya__nmwmj[f'out_arr_inds_{mhx__ycy}'] = np.array(gujcu__tjev.
                block_to_arr_ind[mhx__ycy], dtype=np.int64)
            ahocy__xyea += f'  for i in range(len(out_arr_list_{mhx__ycy})):\n'
            ahocy__xyea += (
                f'    out_arr_ind_{mhx__ycy} = out_arr_inds_{mhx__ycy}[i]\n')
            if iabk__jtdwe:
                ahocy__xyea += (
                    f'    if out_arr_ind_{mhx__ycy} not in kept_cols_set: continue\n'
                    )
            spd__vzty = []
            pldcj__scphd = []
            for eud__qttre in gujcu__tjev.block_to_arr_ind[mhx__ycy]:
                dfe__ytwpd = cjubk__hzzk[eud__qttre]
                spd__vzty.append(dfe__ytwpd)
                xzx__riqkb = T.block_offsets[dfe__ytwpd]
                pldcj__scphd.append(xzx__riqkb)
            pya__nmwmj[f'in_logical_idx_{mhx__ycy}'] = np.array(spd__vzty,
                dtype=np.int64)
            pya__nmwmj[f'in_physical_idx_{mhx__ycy}'] = np.array(pldcj__scphd,
                dtype=np.int64)
            ahocy__xyea += (
                f'    logical_idx_{mhx__ycy} = in_logical_idx_{mhx__ycy}[i]\n')
            ahocy__xyea += (
                f'    physical_idx_{mhx__ycy} = in_physical_idx_{mhx__ycy}[i]\n'
                )
            ahocy__xyea += f"""    ensure_column_unboxed(T, arr_list_{mhx__ycy}, physical_idx_{mhx__ycy}, logical_idx_{mhx__ycy})
"""
            yxi__eapwa = '.copy()' if cqg__has else ''
            ahocy__xyea += f"""    out_arr_list_{mhx__ycy}[i] = arr_list_{mhx__ycy}[physical_idx_{mhx__ycy}]{yxi__eapwa}
"""
        ahocy__xyea += (
            f'  T2 = set_table_block(T2, out_arr_list_{mhx__ycy}, {mhx__ycy})\n'
            )
    ahocy__xyea += f'  return T2\n'
    kfyhn__xgcda = {}
    exec(ahocy__xyea, pya__nmwmj, kfyhn__xgcda)
    return kfyhn__xgcda['table_subset']


def table_filter_equiv(self, scope, equiv_set, loc, args, kws):
    xqlxb__hhy = args[0]
    if equiv_set.has_shape(xqlxb__hhy):
        if guard(is_whole_slice, self.typemap, self.func_ir, args[1]):
            return ArrayAnalysis.AnalyzeResult(shape=xqlxb__hhy, pre=[])
        return ArrayAnalysis.AnalyzeResult(shape=(None, equiv_set.get_shape
            (xqlxb__hhy)[1]), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_filter = (
    table_filter_equiv)


def table_subset_equiv(self, scope, equiv_set, loc, args, kws):
    xqlxb__hhy = args[0]
    if equiv_set.has_shape(xqlxb__hhy):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            xqlxb__hhy)[0], None), pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_table_subset = (
    table_subset_equiv)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def decode_if_dict_table(T):
    ahocy__xyea = 'def impl(T):\n'
    ahocy__xyea += f'  T2 = init_table(T, True)\n'
    ahocy__xyea += f'  l = len(T)\n'
    pya__nmwmj = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, 'decode_if_dict_array':
        decode_if_dict_array}
    for mhx__ycy in T.type_to_blk.values():
        pya__nmwmj[f'arr_inds_{mhx__ycy}'] = np.array(T.block_to_arr_ind[
            mhx__ycy], dtype=np.int64)
        ahocy__xyea += (
            f'  arr_list_{mhx__ycy} = get_table_block(T, {mhx__ycy})\n')
        ahocy__xyea += f"""  out_arr_list_{mhx__ycy} = alloc_list_like(arr_list_{mhx__ycy}, len(arr_list_{mhx__ycy}), True)
"""
        ahocy__xyea += f'  for i in range(len(arr_list_{mhx__ycy})):\n'
        ahocy__xyea += f'    arr_ind_{mhx__ycy} = arr_inds_{mhx__ycy}[i]\n'
        ahocy__xyea += (
            f'    ensure_column_unboxed(T, arr_list_{mhx__ycy}, i, arr_ind_{mhx__ycy})\n'
            )
        ahocy__xyea += (
            f'    out_arr_{mhx__ycy} = decode_if_dict_array(arr_list_{mhx__ycy}[i])\n'
            )
        ahocy__xyea += f'    out_arr_list_{mhx__ycy}[i] = out_arr_{mhx__ycy}\n'
        ahocy__xyea += (
            f'  T2 = set_table_block(T2, out_arr_list_{mhx__ycy}, {mhx__ycy})\n'
            )
    ahocy__xyea += f'  T2 = set_table_len(T2, l)\n'
    ahocy__xyea += f'  return T2\n'
    kfyhn__xgcda = {}
    exec(ahocy__xyea, pya__nmwmj, kfyhn__xgcda)
    return kfyhn__xgcda['impl']


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
        miu__rss = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        miu__rss = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            miu__rss.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        dmqyg__vvn, amwe__iefm = args
        table = cgutils.create_struct_proxy(table_type)(context, builder)
        table.len = amwe__iefm
        avj__vilxa = cgutils.unpack_tuple(builder, dmqyg__vvn)
        for i, watxw__ohb in enumerate(avj__vilxa):
            setattr(table, f'block_{i}', watxw__ohb)
            context.nrt.incref(builder, types.List(miu__rss[i]), watxw__ohb)
        return table._getvalue()
    table_type = TableType(tuple(miu__rss), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def logical_table_to_table(in_table_t, extra_arrs_t, in_col_inds_t,
    n_table_cols_t, out_table_type_t=None, used_cols=None):
    in_col_inds = in_col_inds_t.instance_type.meta
    assert isinstance(in_table_t, (TableType, types.BaseTuple, types.NoneType)
        ), 'logical_table_to_table: input table must be a TableType or tuple of arrays or None (for dead table)'
    pya__nmwmj = {}
    if not is_overload_none(used_cols):
        kept_cols = set(used_cols.instance_type.meta)
        pya__nmwmj['kept_cols'] = np.array(list(kept_cols), np.int64)
        iabk__jtdwe = True
    else:
        kept_cols = set(np.arange(len(in_col_inds)))
        iabk__jtdwe = False
    if isinstance(in_table_t, (types.BaseTuple, types.NoneType)):
        return _logical_tuple_table_to_table_codegen(in_table_t,
            extra_arrs_t, in_col_inds, kept_cols, n_table_cols_t,
            out_table_type_t)
    dlv__yrtwj = len(in_table_t.arr_types)
    out_table_type = TableType(tuple(in_table_t.arr_types[i] if i <
        dlv__yrtwj else extra_arrs_t.types[i - dlv__yrtwj] for i in
        in_col_inds)) if is_overload_none(out_table_type_t
        ) else unwrap_typeref(out_table_type_t)
    ahocy__xyea = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    ahocy__xyea += f'  T1 = in_table_t\n'
    ahocy__xyea += f'  T2 = init_table(out_table_type, False)\n'
    ahocy__xyea += f'  T2 = set_table_len(T2, len(T1))\n'
    if iabk__jtdwe and len(kept_cols) == 0:
        ahocy__xyea += f'  return T2\n'
        kfyhn__xgcda = {}
        exec(ahocy__xyea, pya__nmwmj, kfyhn__xgcda)
        return kfyhn__xgcda['impl']
    if iabk__jtdwe:
        ahocy__xyea += f'  kept_cols_set = set(kept_cols)\n'
    for typ, mhx__ycy in out_table_type.type_to_blk.items():
        pya__nmwmj[f'arr_list_typ_{mhx__ycy}'] = types.List(typ)
        hig__vlf = len(out_table_type.block_to_arr_ind[mhx__ycy])
        ahocy__xyea += f"""  out_arr_list_{mhx__ycy} = alloc_list_like(arr_list_typ_{mhx__ycy}, {hig__vlf}, False)
"""
        if typ in in_table_t.type_to_blk:
            veee__nogvm = in_table_t.type_to_blk[typ]
            welee__woxn = []
            xyml__czk = []
            for xbzr__gher in out_table_type.block_to_arr_ind[mhx__ycy]:
                bvr__qrr = in_col_inds[xbzr__gher]
                if bvr__qrr < dlv__yrtwj:
                    welee__woxn.append(in_table_t.block_offsets[bvr__qrr])
                    xyml__czk.append(bvr__qrr)
                else:
                    welee__woxn.append(-1)
                    xyml__czk.append(-1)
            pya__nmwmj[f'in_idxs_{mhx__ycy}'] = np.array(welee__woxn, np.int64)
            pya__nmwmj[f'in_arr_inds_{mhx__ycy}'] = np.array(xyml__czk, np.
                int64)
            if iabk__jtdwe:
                pya__nmwmj[f'out_arr_inds_{mhx__ycy}'] = np.array(
                    out_table_type.block_to_arr_ind[mhx__ycy], dtype=np.int64)
            ahocy__xyea += (
                f'  in_arr_list_{mhx__ycy} = get_table_block(T1, {veee__nogvm})\n'
                )
            ahocy__xyea += f'  for i in range(len(out_arr_list_{mhx__ycy})):\n'
            ahocy__xyea += (
                f'    in_offset_{mhx__ycy} = in_idxs_{mhx__ycy}[i]\n')
            ahocy__xyea += f'    if in_offset_{mhx__ycy} == -1:\n'
            ahocy__xyea += f'      continue\n'
            ahocy__xyea += (
                f'    in_arr_ind_{mhx__ycy} = in_arr_inds_{mhx__ycy}[i]\n')
            if iabk__jtdwe:
                ahocy__xyea += (
                    f'    if out_arr_inds_{mhx__ycy}[i] not in kept_cols_set: continue\n'
                    )
            ahocy__xyea += f"""    ensure_column_unboxed(T1, in_arr_list_{mhx__ycy}, in_offset_{mhx__ycy}, in_arr_ind_{mhx__ycy})
"""
            ahocy__xyea += f"""    out_arr_list_{mhx__ycy}[i] = in_arr_list_{mhx__ycy}[in_offset_{mhx__ycy}]
"""
        for i, xbzr__gher in enumerate(out_table_type.block_to_arr_ind[
            mhx__ycy]):
            if xbzr__gher not in kept_cols:
                continue
            bvr__qrr = in_col_inds[xbzr__gher]
            if bvr__qrr >= dlv__yrtwj:
                ahocy__xyea += f"""  out_arr_list_{mhx__ycy}[{i}] = extra_arrs_t[{bvr__qrr - dlv__yrtwj}]
"""
        ahocy__xyea += (
            f'  T2 = set_table_block(T2, out_arr_list_{mhx__ycy}, {mhx__ycy})\n'
            )
    ahocy__xyea += f'  return T2\n'
    pya__nmwmj.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'get_table_block': get_table_block,
        'ensure_column_unboxed': ensure_column_unboxed, 'out_table_type':
        out_table_type})
    kfyhn__xgcda = {}
    exec(ahocy__xyea, pya__nmwmj, kfyhn__xgcda)
    return kfyhn__xgcda['impl']


def _logical_tuple_table_to_table_codegen(in_table_t, extra_arrs_t,
    in_col_inds, kept_cols, n_table_cols_t, out_table_type_t):
    dlv__yrtwj = get_overload_const_int(n_table_cols_t
        ) if is_overload_constant_int(n_table_cols_t) else len(in_table_t.types
        )
    out_table_type = TableType(tuple(in_table_t.types[i] if i < dlv__yrtwj else
        extra_arrs_t.types[i - dlv__yrtwj] for i in in_col_inds)
        ) if is_overload_none(out_table_type_t) else unwrap_typeref(
        out_table_type_t)
    besxs__gdv = None
    if not is_overload_none(in_table_t):
        for i, qusa__ywp in enumerate(in_table_t.types):
            if qusa__ywp != types.none:
                besxs__gdv = f'in_table_t[{i}]'
                break
    if besxs__gdv is None:
        for i, qusa__ywp in enumerate(extra_arrs_t.types):
            if qusa__ywp != types.none:
                besxs__gdv = f'extra_arrs_t[{i}]'
                break
    assert besxs__gdv is not None, 'no array found in input data'
    ahocy__xyea = """def impl(in_table_t, extra_arrs_t, in_col_inds_t, n_table_cols_t, out_table_type_t=None, used_cols=None):
"""
    ahocy__xyea += f'  T1 = in_table_t\n'
    ahocy__xyea += f'  T2 = init_table(out_table_type, False)\n'
    ahocy__xyea += f'  T2 = set_table_len(T2, len({besxs__gdv}))\n'
    pya__nmwmj = {}
    for typ, mhx__ycy in out_table_type.type_to_blk.items():
        pya__nmwmj[f'arr_list_typ_{mhx__ycy}'] = types.List(typ)
        hig__vlf = len(out_table_type.block_to_arr_ind[mhx__ycy])
        ahocy__xyea += f"""  out_arr_list_{mhx__ycy} = alloc_list_like(arr_list_typ_{mhx__ycy}, {hig__vlf}, False)
"""
        for i, xbzr__gher in enumerate(out_table_type.block_to_arr_ind[
            mhx__ycy]):
            if xbzr__gher not in kept_cols:
                continue
            bvr__qrr = in_col_inds[xbzr__gher]
            if bvr__qrr < dlv__yrtwj:
                ahocy__xyea += (
                    f'  out_arr_list_{mhx__ycy}[{i}] = T1[{bvr__qrr}]\n')
            else:
                ahocy__xyea += f"""  out_arr_list_{mhx__ycy}[{i}] = extra_arrs_t[{bvr__qrr - dlv__yrtwj}]
"""
        ahocy__xyea += (
            f'  T2 = set_table_block(T2, out_arr_list_{mhx__ycy}, {mhx__ycy})\n'
            )
    ahocy__xyea += f'  return T2\n'
    pya__nmwmj.update({'init_table': init_table, 'alloc_list_like':
        alloc_list_like, 'set_table_block': set_table_block,
        'set_table_len': set_table_len, 'out_table_type': out_table_type})
    kfyhn__xgcda = {}
    exec(ahocy__xyea, pya__nmwmj, kfyhn__xgcda)
    return kfyhn__xgcda['impl']


def logical_table_to_table_equiv(self, scope, equiv_set, loc, args, kws):
    xecvs__vxh = args[0]
    wjqpe__xvt = args[1]
    if equiv_set.has_shape(xecvs__vxh):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            xecvs__vxh)[0], None), pre=[])
    if equiv_set.has_shape(wjqpe__xvt):
        return ArrayAnalysis.AnalyzeResult(shape=(equiv_set.get_shape(
            wjqpe__xvt)[0], None), pre=[])


(ArrayAnalysis._analyze_op_call_bodo_hiframes_table_logical_table_to_table
    ) = logical_table_to_table_equiv


def alias_ext_logical_table_to_table(lhs_name, args, alias_map, arg_aliases):
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['logical_table_to_table',
    'bodo.hiframes.table'] = alias_ext_logical_table_to_table
