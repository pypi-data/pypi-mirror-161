"""CSR Matrix data type implementation for scipy.sparse.csr_matrix
"""
import operator
import numba
import numpy as np
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, typeof_impl, unbox
import bodo
from bodo.utils.typing import BodoError


class CSRMatrixType(types.ArrayCompatible):
    ndim = 2

    def __init__(self, dtype, idx_dtype):
        self.dtype = dtype
        self.idx_dtype = idx_dtype
        super(CSRMatrixType, self).__init__(name=
            f'CSRMatrixType({dtype}, {idx_dtype})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    def copy(self):
        return CSRMatrixType(self.dtype, self.idx_dtype)


@register_model(CSRMatrixType)
class CSRMatrixModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        aln__oepdd = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, aln__oepdd)


make_attribute_wrapper(CSRMatrixType, 'data', 'data')
make_attribute_wrapper(CSRMatrixType, 'indices', 'indices')
make_attribute_wrapper(CSRMatrixType, 'indptr', 'indptr')
make_attribute_wrapper(CSRMatrixType, 'shape', 'shape')


@intrinsic
def init_csr_matrix(typingctx, data_t, indices_t, indptr_t, shape_t=None):
    assert isinstance(data_t, types.Array)
    assert isinstance(indices_t, types.Array) and isinstance(indices_t.
        dtype, types.Integer)
    assert indices_t == indptr_t

    def codegen(context, builder, signature, args):
        cbc__efn, ioi__oio, pfh__tbtfa, egh__pskb = args
        tfgq__toftx = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        tfgq__toftx.data = cbc__efn
        tfgq__toftx.indices = ioi__oio
        tfgq__toftx.indptr = pfh__tbtfa
        tfgq__toftx.shape = egh__pskb
        context.nrt.incref(builder, signature.args[0], cbc__efn)
        context.nrt.incref(builder, signature.args[1], ioi__oio)
        context.nrt.incref(builder, signature.args[2], pfh__tbtfa)
        return tfgq__toftx._getvalue()
    fzn__zrial = CSRMatrixType(data_t.dtype, indices_t.dtype)
    ncwjj__qsmtf = fzn__zrial(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return ncwjj__qsmtf, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    tfgq__toftx = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oqqxm__zum = c.pyapi.object_getattr_string(val, 'data')
    gkloq__lnzo = c.pyapi.object_getattr_string(val, 'indices')
    dmdc__ampy = c.pyapi.object_getattr_string(val, 'indptr')
    yvt__hhnj = c.pyapi.object_getattr_string(val, 'shape')
    tfgq__toftx.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1,
        'C'), oqqxm__zum).value
    tfgq__toftx.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), gkloq__lnzo).value
    tfgq__toftx.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), dmdc__ampy).value
    tfgq__toftx.shape = c.pyapi.to_native_value(types.UniTuple(types.int64,
        2), yvt__hhnj).value
    c.pyapi.decref(oqqxm__zum)
    c.pyapi.decref(gkloq__lnzo)
    c.pyapi.decref(dmdc__ampy)
    c.pyapi.decref(yvt__hhnj)
    ejtxv__nvp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(tfgq__toftx._getvalue(), is_error=ejtxv__nvp)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    vtyi__gmut = c.context.insert_const_string(c.builder.module, 'scipy.sparse'
        )
    xub__bmxza = c.pyapi.import_module_noblock(vtyi__gmut)
    tfgq__toftx = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        tfgq__toftx.data)
    oqqxm__zum = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        tfgq__toftx.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        tfgq__toftx.indices)
    gkloq__lnzo = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), tfgq__toftx.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        tfgq__toftx.indptr)
    dmdc__ampy = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), tfgq__toftx.indptr, c.env_manager)
    yvt__hhnj = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        tfgq__toftx.shape, c.env_manager)
    ywa__zcv = c.pyapi.tuple_pack([oqqxm__zum, gkloq__lnzo, dmdc__ampy])
    zbap__nnfyf = c.pyapi.call_method(xub__bmxza, 'csr_matrix', (ywa__zcv,
        yvt__hhnj))
    c.pyapi.decref(ywa__zcv)
    c.pyapi.decref(oqqxm__zum)
    c.pyapi.decref(gkloq__lnzo)
    c.pyapi.decref(dmdc__ampy)
    c.pyapi.decref(yvt__hhnj)
    c.pyapi.decref(xub__bmxza)
    c.context.nrt.decref(c.builder, typ, val)
    return zbap__nnfyf


@overload(len, no_unliteral=True)
def overload_csr_matrix_len(A):
    if isinstance(A, CSRMatrixType):
        return lambda A: A.shape[0]


@overload_attribute(CSRMatrixType, 'ndim')
def overload_csr_matrix_ndim(A):
    return lambda A: 2


@overload_method(CSRMatrixType, 'copy', no_unliteral=True)
def overload_csr_matrix_copy(A):

    def copy_impl(A):
        return init_csr_matrix(A.data.copy(), A.indices.copy(), A.indptr.
            copy(), A.shape)
    return copy_impl


@overload(operator.getitem, no_unliteral=True)
def csr_matrix_getitem(A, idx):
    if not isinstance(A, CSRMatrixType):
        return
    kyqx__wnghc = A.dtype
    mhg__ksn = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            ydk__fzqih, trsta__aqcgt = A.shape
            cyoc__szn = numba.cpython.unicode._normalize_slice(idx[0],
                ydk__fzqih)
            txa__yrdmy = numba.cpython.unicode._normalize_slice(idx[1],
                trsta__aqcgt)
            if cyoc__szn.step != 1 or txa__yrdmy.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            mph__duf = cyoc__szn.start
            dhv__yfmes = cyoc__szn.stop
            otdqj__fepdy = txa__yrdmy.start
            dnuz__xkek = txa__yrdmy.stop
            vihc__xsa = A.indptr
            rjmf__gke = A.indices
            pil__usb = A.data
            cxemp__kxcl = dhv__yfmes - mph__duf
            ydg__mzww = dnuz__xkek - otdqj__fepdy
            bnfvr__gqc = 0
            yfgt__pyp = 0
            for urcoj__vxhc in range(cxemp__kxcl):
                frqe__jpsg = vihc__xsa[mph__duf + urcoj__vxhc]
                oomt__tie = vihc__xsa[mph__duf + urcoj__vxhc + 1]
                for dhhdo__iiks in range(frqe__jpsg, oomt__tie):
                    if rjmf__gke[dhhdo__iiks] >= otdqj__fepdy and rjmf__gke[
                        dhhdo__iiks] < dnuz__xkek:
                        bnfvr__gqc += 1
            twib__bmk = np.empty(cxemp__kxcl + 1, mhg__ksn)
            rlcmi__cbegu = np.empty(bnfvr__gqc, mhg__ksn)
            isa__lhutu = np.empty(bnfvr__gqc, kyqx__wnghc)
            twib__bmk[0] = 0
            for urcoj__vxhc in range(cxemp__kxcl):
                frqe__jpsg = vihc__xsa[mph__duf + urcoj__vxhc]
                oomt__tie = vihc__xsa[mph__duf + urcoj__vxhc + 1]
                for dhhdo__iiks in range(frqe__jpsg, oomt__tie):
                    if rjmf__gke[dhhdo__iiks] >= otdqj__fepdy and rjmf__gke[
                        dhhdo__iiks] < dnuz__xkek:
                        rlcmi__cbegu[yfgt__pyp] = rjmf__gke[dhhdo__iiks
                            ] - otdqj__fepdy
                        isa__lhutu[yfgt__pyp] = pil__usb[dhhdo__iiks]
                        yfgt__pyp += 1
                twib__bmk[urcoj__vxhc + 1] = yfgt__pyp
            return init_csr_matrix(isa__lhutu, rlcmi__cbegu, twib__bmk, (
                cxemp__kxcl, ydg__mzww))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == mhg__ksn:

        def impl(A, idx):
            ydk__fzqih, trsta__aqcgt = A.shape
            vihc__xsa = A.indptr
            rjmf__gke = A.indices
            pil__usb = A.data
            cxemp__kxcl = len(idx)
            bnfvr__gqc = 0
            yfgt__pyp = 0
            for urcoj__vxhc in range(cxemp__kxcl):
                exnp__jzxmm = idx[urcoj__vxhc]
                frqe__jpsg = vihc__xsa[exnp__jzxmm]
                oomt__tie = vihc__xsa[exnp__jzxmm + 1]
                bnfvr__gqc += oomt__tie - frqe__jpsg
            twib__bmk = np.empty(cxemp__kxcl + 1, mhg__ksn)
            rlcmi__cbegu = np.empty(bnfvr__gqc, mhg__ksn)
            isa__lhutu = np.empty(bnfvr__gqc, kyqx__wnghc)
            twib__bmk[0] = 0
            for urcoj__vxhc in range(cxemp__kxcl):
                exnp__jzxmm = idx[urcoj__vxhc]
                frqe__jpsg = vihc__xsa[exnp__jzxmm]
                oomt__tie = vihc__xsa[exnp__jzxmm + 1]
                rlcmi__cbegu[yfgt__pyp:yfgt__pyp + oomt__tie - frqe__jpsg
                    ] = rjmf__gke[frqe__jpsg:oomt__tie]
                isa__lhutu[yfgt__pyp:yfgt__pyp + oomt__tie - frqe__jpsg
                    ] = pil__usb[frqe__jpsg:oomt__tie]
                yfgt__pyp += oomt__tie - frqe__jpsg
                twib__bmk[urcoj__vxhc + 1] = yfgt__pyp
            ypq__uyysp = init_csr_matrix(isa__lhutu, rlcmi__cbegu,
                twib__bmk, (cxemp__kxcl, trsta__aqcgt))
            return ypq__uyysp
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
