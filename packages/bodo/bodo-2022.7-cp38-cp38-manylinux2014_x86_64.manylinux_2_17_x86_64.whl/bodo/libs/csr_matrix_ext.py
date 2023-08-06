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
        pvns__zmvsx = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, pvns__zmvsx)


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
        ewdzc__ksoqy, ubh__cyq, fcu__etfni, rgpoa__yfe = args
        jwdl__hbh = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        jwdl__hbh.data = ewdzc__ksoqy
        jwdl__hbh.indices = ubh__cyq
        jwdl__hbh.indptr = fcu__etfni
        jwdl__hbh.shape = rgpoa__yfe
        context.nrt.incref(builder, signature.args[0], ewdzc__ksoqy)
        context.nrt.incref(builder, signature.args[1], ubh__cyq)
        context.nrt.incref(builder, signature.args[2], fcu__etfni)
        return jwdl__hbh._getvalue()
    rdvu__xrc = CSRMatrixType(data_t.dtype, indices_t.dtype)
    vadfk__osxae = rdvu__xrc(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return vadfk__osxae, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    jwdl__hbh = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    bzt__mpgc = c.pyapi.object_getattr_string(val, 'data')
    rvi__kxe = c.pyapi.object_getattr_string(val, 'indices')
    jymgp__gjqu = c.pyapi.object_getattr_string(val, 'indptr')
    zkhfo__pui = c.pyapi.object_getattr_string(val, 'shape')
    jwdl__hbh.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        bzt__mpgc).value
    jwdl__hbh.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 
        1, 'C'), rvi__kxe).value
    jwdl__hbh.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), jymgp__gjqu).value
    jwdl__hbh.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2
        ), zkhfo__pui).value
    c.pyapi.decref(bzt__mpgc)
    c.pyapi.decref(rvi__kxe)
    c.pyapi.decref(jymgp__gjqu)
    c.pyapi.decref(zkhfo__pui)
    nfx__bdi = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jwdl__hbh._getvalue(), is_error=nfx__bdi)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    ryua__gyh = c.context.insert_const_string(c.builder.module, 'scipy.sparse')
    ezn__dyth = c.pyapi.import_module_noblock(ryua__gyh)
    jwdl__hbh = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        jwdl__hbh.data)
    bzt__mpgc = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        jwdl__hbh.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        jwdl__hbh.indices)
    rvi__kxe = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'),
        jwdl__hbh.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        jwdl__hbh.indptr)
    jymgp__gjqu = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), jwdl__hbh.indptr, c.env_manager)
    zkhfo__pui = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        jwdl__hbh.shape, c.env_manager)
    kzk__evh = c.pyapi.tuple_pack([bzt__mpgc, rvi__kxe, jymgp__gjqu])
    evmb__xwvb = c.pyapi.call_method(ezn__dyth, 'csr_matrix', (kzk__evh,
        zkhfo__pui))
    c.pyapi.decref(kzk__evh)
    c.pyapi.decref(bzt__mpgc)
    c.pyapi.decref(rvi__kxe)
    c.pyapi.decref(jymgp__gjqu)
    c.pyapi.decref(zkhfo__pui)
    c.pyapi.decref(ezn__dyth)
    c.context.nrt.decref(c.builder, typ, val)
    return evmb__xwvb


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
    peg__criq = A.dtype
    fio__ciizl = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            fcuw__pxw, qul__kpro = A.shape
            kjjf__tlnhh = numba.cpython.unicode._normalize_slice(idx[0],
                fcuw__pxw)
            axqla__ufsai = numba.cpython.unicode._normalize_slice(idx[1],
                qul__kpro)
            if kjjf__tlnhh.step != 1 or axqla__ufsai.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            rqypx__gnues = kjjf__tlnhh.start
            plcym__wbu = kjjf__tlnhh.stop
            kqce__knand = axqla__ufsai.start
            ivnsc__hkls = axqla__ufsai.stop
            tttua__rnyse = A.indptr
            axv__qnv = A.indices
            qzu__txvc = A.data
            kyc__umhqn = plcym__wbu - rqypx__gnues
            fnt__vbc = ivnsc__hkls - kqce__knand
            rbus__vbd = 0
            vsxg__fwpn = 0
            for zbhjr__rvhnw in range(kyc__umhqn):
                qzl__scocl = tttua__rnyse[rqypx__gnues + zbhjr__rvhnw]
                iuc__obc = tttua__rnyse[rqypx__gnues + zbhjr__rvhnw + 1]
                for udyl__vdpj in range(qzl__scocl, iuc__obc):
                    if axv__qnv[udyl__vdpj] >= kqce__knand and axv__qnv[
                        udyl__vdpj] < ivnsc__hkls:
                        rbus__vbd += 1
            jtwq__dsv = np.empty(kyc__umhqn + 1, fio__ciizl)
            wqmg__ttbr = np.empty(rbus__vbd, fio__ciizl)
            tkxxa__uwaa = np.empty(rbus__vbd, peg__criq)
            jtwq__dsv[0] = 0
            for zbhjr__rvhnw in range(kyc__umhqn):
                qzl__scocl = tttua__rnyse[rqypx__gnues + zbhjr__rvhnw]
                iuc__obc = tttua__rnyse[rqypx__gnues + zbhjr__rvhnw + 1]
                for udyl__vdpj in range(qzl__scocl, iuc__obc):
                    if axv__qnv[udyl__vdpj] >= kqce__knand and axv__qnv[
                        udyl__vdpj] < ivnsc__hkls:
                        wqmg__ttbr[vsxg__fwpn] = axv__qnv[udyl__vdpj
                            ] - kqce__knand
                        tkxxa__uwaa[vsxg__fwpn] = qzu__txvc[udyl__vdpj]
                        vsxg__fwpn += 1
                jtwq__dsv[zbhjr__rvhnw + 1] = vsxg__fwpn
            return init_csr_matrix(tkxxa__uwaa, wqmg__ttbr, jtwq__dsv, (
                kyc__umhqn, fnt__vbc))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == fio__ciizl:

        def impl(A, idx):
            fcuw__pxw, qul__kpro = A.shape
            tttua__rnyse = A.indptr
            axv__qnv = A.indices
            qzu__txvc = A.data
            kyc__umhqn = len(idx)
            rbus__vbd = 0
            vsxg__fwpn = 0
            for zbhjr__rvhnw in range(kyc__umhqn):
                ahk__kqix = idx[zbhjr__rvhnw]
                qzl__scocl = tttua__rnyse[ahk__kqix]
                iuc__obc = tttua__rnyse[ahk__kqix + 1]
                rbus__vbd += iuc__obc - qzl__scocl
            jtwq__dsv = np.empty(kyc__umhqn + 1, fio__ciizl)
            wqmg__ttbr = np.empty(rbus__vbd, fio__ciizl)
            tkxxa__uwaa = np.empty(rbus__vbd, peg__criq)
            jtwq__dsv[0] = 0
            for zbhjr__rvhnw in range(kyc__umhqn):
                ahk__kqix = idx[zbhjr__rvhnw]
                qzl__scocl = tttua__rnyse[ahk__kqix]
                iuc__obc = tttua__rnyse[ahk__kqix + 1]
                wqmg__ttbr[vsxg__fwpn:vsxg__fwpn + iuc__obc - qzl__scocl
                    ] = axv__qnv[qzl__scocl:iuc__obc]
                tkxxa__uwaa[vsxg__fwpn:vsxg__fwpn + iuc__obc - qzl__scocl
                    ] = qzu__txvc[qzl__scocl:iuc__obc]
                vsxg__fwpn += iuc__obc - qzl__scocl
                jtwq__dsv[zbhjr__rvhnw + 1] = vsxg__fwpn
            ymgu__unl = init_csr_matrix(tkxxa__uwaa, wqmg__ttbr, jtwq__dsv,
                (kyc__umhqn, qul__kpro))
            return ymgu__unl
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
