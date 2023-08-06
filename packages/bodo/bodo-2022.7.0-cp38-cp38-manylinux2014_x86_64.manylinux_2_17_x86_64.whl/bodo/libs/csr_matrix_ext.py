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
        btg__nurw = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, btg__nurw)


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
        bzotg__mly, qqynm__qpe, ljl__weu, jxqsr__wwz = args
        yrwsv__rfoxy = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        yrwsv__rfoxy.data = bzotg__mly
        yrwsv__rfoxy.indices = qqynm__qpe
        yrwsv__rfoxy.indptr = ljl__weu
        yrwsv__rfoxy.shape = jxqsr__wwz
        context.nrt.incref(builder, signature.args[0], bzotg__mly)
        context.nrt.incref(builder, signature.args[1], qqynm__qpe)
        context.nrt.incref(builder, signature.args[2], ljl__weu)
        return yrwsv__rfoxy._getvalue()
    kzqh__xmxu = CSRMatrixType(data_t.dtype, indices_t.dtype)
    nts__jin = kzqh__xmxu(data_t, indices_t, indptr_t, types.UniTuple(types
        .int64, 2))
    return nts__jin, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    yrwsv__rfoxy = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hmofz__hxem = c.pyapi.object_getattr_string(val, 'data')
    dvenn__jtyqd = c.pyapi.object_getattr_string(val, 'indices')
    jod__xvig = c.pyapi.object_getattr_string(val, 'indptr')
    nluk__limc = c.pyapi.object_getattr_string(val, 'shape')
    yrwsv__rfoxy.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1,
        'C'), hmofz__hxem).value
    yrwsv__rfoxy.indices = c.pyapi.to_native_value(types.Array(typ.
        idx_dtype, 1, 'C'), dvenn__jtyqd).value
    yrwsv__rfoxy.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype,
        1, 'C'), jod__xvig).value
    yrwsv__rfoxy.shape = c.pyapi.to_native_value(types.UniTuple(types.int64,
        2), nluk__limc).value
    c.pyapi.decref(hmofz__hxem)
    c.pyapi.decref(dvenn__jtyqd)
    c.pyapi.decref(jod__xvig)
    c.pyapi.decref(nluk__limc)
    vumrq__gwyi = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(yrwsv__rfoxy._getvalue(), is_error=vumrq__gwyi)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    jcnh__mgzt = c.context.insert_const_string(c.builder.module, 'scipy.sparse'
        )
    ifh__lda = c.pyapi.import_module_noblock(jcnh__mgzt)
    yrwsv__rfoxy = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        yrwsv__rfoxy.data)
    hmofz__hxem = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        yrwsv__rfoxy.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        yrwsv__rfoxy.indices)
    dvenn__jtyqd = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1,
        'C'), yrwsv__rfoxy.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        yrwsv__rfoxy.indptr)
    jod__xvig = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'
        ), yrwsv__rfoxy.indptr, c.env_manager)
    nluk__limc = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        yrwsv__rfoxy.shape, c.env_manager)
    nfev__hlg = c.pyapi.tuple_pack([hmofz__hxem, dvenn__jtyqd, jod__xvig])
    anhbh__ptb = c.pyapi.call_method(ifh__lda, 'csr_matrix', (nfev__hlg,
        nluk__limc))
    c.pyapi.decref(nfev__hlg)
    c.pyapi.decref(hmofz__hxem)
    c.pyapi.decref(dvenn__jtyqd)
    c.pyapi.decref(jod__xvig)
    c.pyapi.decref(nluk__limc)
    c.pyapi.decref(ifh__lda)
    c.context.nrt.decref(c.builder, typ, val)
    return anhbh__ptb


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
    xaw__vkku = A.dtype
    bdc__pxhav = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            rnui__xgext, xqeo__hxwld = A.shape
            xcd__xik = numba.cpython.unicode._normalize_slice(idx[0],
                rnui__xgext)
            fsrfy__biq = numba.cpython.unicode._normalize_slice(idx[1],
                xqeo__hxwld)
            if xcd__xik.step != 1 or fsrfy__biq.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            atdt__wvqug = xcd__xik.start
            hnanl__pxluq = xcd__xik.stop
            mdms__ofyj = fsrfy__biq.start
            adi__yrr = fsrfy__biq.stop
            xxwt__yxd = A.indptr
            prl__kse = A.indices
            lnj__oltmp = A.data
            ocz__ntag = hnanl__pxluq - atdt__wvqug
            wrv__nhuv = adi__yrr - mdms__ofyj
            ohlsz__bofs = 0
            pzuzm__wvuq = 0
            for hyihi__dzytw in range(ocz__ntag):
                wkylk__anx = xxwt__yxd[atdt__wvqug + hyihi__dzytw]
                fme__cjl = xxwt__yxd[atdt__wvqug + hyihi__dzytw + 1]
                for gzjqs__sqdn in range(wkylk__anx, fme__cjl):
                    if prl__kse[gzjqs__sqdn] >= mdms__ofyj and prl__kse[
                        gzjqs__sqdn] < adi__yrr:
                        ohlsz__bofs += 1
            pflqa__pksag = np.empty(ocz__ntag + 1, bdc__pxhav)
            mkujm__jqbim = np.empty(ohlsz__bofs, bdc__pxhav)
            xbz__szo = np.empty(ohlsz__bofs, xaw__vkku)
            pflqa__pksag[0] = 0
            for hyihi__dzytw in range(ocz__ntag):
                wkylk__anx = xxwt__yxd[atdt__wvqug + hyihi__dzytw]
                fme__cjl = xxwt__yxd[atdt__wvqug + hyihi__dzytw + 1]
                for gzjqs__sqdn in range(wkylk__anx, fme__cjl):
                    if prl__kse[gzjqs__sqdn] >= mdms__ofyj and prl__kse[
                        gzjqs__sqdn] < adi__yrr:
                        mkujm__jqbim[pzuzm__wvuq] = prl__kse[gzjqs__sqdn
                            ] - mdms__ofyj
                        xbz__szo[pzuzm__wvuq] = lnj__oltmp[gzjqs__sqdn]
                        pzuzm__wvuq += 1
                pflqa__pksag[hyihi__dzytw + 1] = pzuzm__wvuq
            return init_csr_matrix(xbz__szo, mkujm__jqbim, pflqa__pksag, (
                ocz__ntag, wrv__nhuv))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == bdc__pxhav:

        def impl(A, idx):
            rnui__xgext, xqeo__hxwld = A.shape
            xxwt__yxd = A.indptr
            prl__kse = A.indices
            lnj__oltmp = A.data
            ocz__ntag = len(idx)
            ohlsz__bofs = 0
            pzuzm__wvuq = 0
            for hyihi__dzytw in range(ocz__ntag):
                vaoos__jihy = idx[hyihi__dzytw]
                wkylk__anx = xxwt__yxd[vaoos__jihy]
                fme__cjl = xxwt__yxd[vaoos__jihy + 1]
                ohlsz__bofs += fme__cjl - wkylk__anx
            pflqa__pksag = np.empty(ocz__ntag + 1, bdc__pxhav)
            mkujm__jqbim = np.empty(ohlsz__bofs, bdc__pxhav)
            xbz__szo = np.empty(ohlsz__bofs, xaw__vkku)
            pflqa__pksag[0] = 0
            for hyihi__dzytw in range(ocz__ntag):
                vaoos__jihy = idx[hyihi__dzytw]
                wkylk__anx = xxwt__yxd[vaoos__jihy]
                fme__cjl = xxwt__yxd[vaoos__jihy + 1]
                mkujm__jqbim[pzuzm__wvuq:pzuzm__wvuq + fme__cjl - wkylk__anx
                    ] = prl__kse[wkylk__anx:fme__cjl]
                xbz__szo[pzuzm__wvuq:pzuzm__wvuq + fme__cjl - wkylk__anx
                    ] = lnj__oltmp[wkylk__anx:fme__cjl]
                pzuzm__wvuq += fme__cjl - wkylk__anx
                pflqa__pksag[hyihi__dzytw + 1] = pzuzm__wvuq
            teh__dfwp = init_csr_matrix(xbz__szo, mkujm__jqbim,
                pflqa__pksag, (ocz__ntag, xqeo__hxwld))
            return teh__dfwp
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
