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
        sqblu__dauj = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'indices', types.Array(fe_type.idx_dtype, 1, 'C')), ('indptr',
            types.Array(fe_type.idx_dtype, 1, 'C')), ('shape', types.
            UniTuple(types.int64, 2))]
        models.StructModel.__init__(self, dmm, fe_type, sqblu__dauj)


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
        neel__oui, tbjnp__lafe, ryksf__osw, hhgs__crsvt = args
        skx__tcbr = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        skx__tcbr.data = neel__oui
        skx__tcbr.indices = tbjnp__lafe
        skx__tcbr.indptr = ryksf__osw
        skx__tcbr.shape = hhgs__crsvt
        context.nrt.incref(builder, signature.args[0], neel__oui)
        context.nrt.incref(builder, signature.args[1], tbjnp__lafe)
        context.nrt.incref(builder, signature.args[2], ryksf__osw)
        return skx__tcbr._getvalue()
    lwuu__nvgqb = CSRMatrixType(data_t.dtype, indices_t.dtype)
    pmgr__gfave = lwuu__nvgqb(data_t, indices_t, indptr_t, types.UniTuple(
        types.int64, 2))
    return pmgr__gfave, codegen


if bodo.utils.utils.has_scipy():
    import scipy.sparse

    @typeof_impl.register(scipy.sparse.csr_matrix)
    def _typeof_csr_matrix(val, c):
        dtype = numba.from_dtype(val.dtype)
        idx_dtype = numba.from_dtype(val.indices.dtype)
        return CSRMatrixType(dtype, idx_dtype)


@unbox(CSRMatrixType)
def unbox_csr_matrix(typ, val, c):
    skx__tcbr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    leq__bnmg = c.pyapi.object_getattr_string(val, 'data')
    cqg__lxx = c.pyapi.object_getattr_string(val, 'indices')
    tpy__nsq = c.pyapi.object_getattr_string(val, 'indptr')
    qatw__igfr = c.pyapi.object_getattr_string(val, 'shape')
    skx__tcbr.data = c.pyapi.to_native_value(types.Array(typ.dtype, 1, 'C'),
        leq__bnmg).value
    skx__tcbr.indices = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 
        1, 'C'), cqg__lxx).value
    skx__tcbr.indptr = c.pyapi.to_native_value(types.Array(typ.idx_dtype, 1,
        'C'), tpy__nsq).value
    skx__tcbr.shape = c.pyapi.to_native_value(types.UniTuple(types.int64, 2
        ), qatw__igfr).value
    c.pyapi.decref(leq__bnmg)
    c.pyapi.decref(cqg__lxx)
    c.pyapi.decref(tpy__nsq)
    c.pyapi.decref(qatw__igfr)
    ypjwg__wamde = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(skx__tcbr._getvalue(), is_error=ypjwg__wamde)


@box(CSRMatrixType)
def box_csr_matrix(typ, val, c):
    rbc__jep = c.context.insert_const_string(c.builder.module, 'scipy.sparse')
    mpzh__jjxqv = c.pyapi.import_module_noblock(rbc__jep)
    skx__tcbr = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    c.context.nrt.incref(c.builder, types.Array(typ.dtype, 1, 'C'),
        skx__tcbr.data)
    leq__bnmg = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        skx__tcbr.data, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        skx__tcbr.indices)
    cqg__lxx = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'),
        skx__tcbr.indices, c.env_manager)
    c.context.nrt.incref(c.builder, types.Array(typ.idx_dtype, 1, 'C'),
        skx__tcbr.indptr)
    tpy__nsq = c.pyapi.from_native_value(types.Array(typ.idx_dtype, 1, 'C'),
        skx__tcbr.indptr, c.env_manager)
    qatw__igfr = c.pyapi.from_native_value(types.UniTuple(types.int64, 2),
        skx__tcbr.shape, c.env_manager)
    nkfq__ajmha = c.pyapi.tuple_pack([leq__bnmg, cqg__lxx, tpy__nsq])
    scxhu__ina = c.pyapi.call_method(mpzh__jjxqv, 'csr_matrix', (
        nkfq__ajmha, qatw__igfr))
    c.pyapi.decref(nkfq__ajmha)
    c.pyapi.decref(leq__bnmg)
    c.pyapi.decref(cqg__lxx)
    c.pyapi.decref(tpy__nsq)
    c.pyapi.decref(qatw__igfr)
    c.pyapi.decref(mpzh__jjxqv)
    c.context.nrt.decref(c.builder, typ, val)
    return scxhu__ina


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
    aohd__xat = A.dtype
    via__kwh = A.idx_dtype
    if isinstance(idx, types.BaseTuple) and len(idx) == 2 and isinstance(idx
        [0], types.SliceType) and isinstance(idx[1], types.SliceType):

        def impl(A, idx):
            sbppz__kkvg, hqpou__ltvew = A.shape
            uqhf__vhr = numba.cpython.unicode._normalize_slice(idx[0],
                sbppz__kkvg)
            sug__djyd = numba.cpython.unicode._normalize_slice(idx[1],
                hqpou__ltvew)
            if uqhf__vhr.step != 1 or sug__djyd.step != 1:
                raise ValueError(
                    'CSR matrix slice getitem only supports step=1 currently')
            hyzwq__mnhjx = uqhf__vhr.start
            hbrxe__lonu = uqhf__vhr.stop
            tzaol__scfzl = sug__djyd.start
            qtp__rulg = sug__djyd.stop
            qvl__nol = A.indptr
            oxl__ykuzu = A.indices
            mdcsr__upq = A.data
            ddhq__omzsa = hbrxe__lonu - hyzwq__mnhjx
            nicip__silt = qtp__rulg - tzaol__scfzl
            rhv__oylk = 0
            tswn__dqo = 0
            for mrre__raa in range(ddhq__omzsa):
                kzti__lwsr = qvl__nol[hyzwq__mnhjx + mrre__raa]
                cenrd__hrge = qvl__nol[hyzwq__mnhjx + mrre__raa + 1]
                for rage__uaqz in range(kzti__lwsr, cenrd__hrge):
                    if oxl__ykuzu[rage__uaqz] >= tzaol__scfzl and oxl__ykuzu[
                        rage__uaqz] < qtp__rulg:
                        rhv__oylk += 1
            pume__henpf = np.empty(ddhq__omzsa + 1, via__kwh)
            klqqq__slo = np.empty(rhv__oylk, via__kwh)
            pfilc__ghx = np.empty(rhv__oylk, aohd__xat)
            pume__henpf[0] = 0
            for mrre__raa in range(ddhq__omzsa):
                kzti__lwsr = qvl__nol[hyzwq__mnhjx + mrre__raa]
                cenrd__hrge = qvl__nol[hyzwq__mnhjx + mrre__raa + 1]
                for rage__uaqz in range(kzti__lwsr, cenrd__hrge):
                    if oxl__ykuzu[rage__uaqz] >= tzaol__scfzl and oxl__ykuzu[
                        rage__uaqz] < qtp__rulg:
                        klqqq__slo[tswn__dqo] = oxl__ykuzu[rage__uaqz
                            ] - tzaol__scfzl
                        pfilc__ghx[tswn__dqo] = mdcsr__upq[rage__uaqz]
                        tswn__dqo += 1
                pume__henpf[mrre__raa + 1] = tswn__dqo
            return init_csr_matrix(pfilc__ghx, klqqq__slo, pume__henpf, (
                ddhq__omzsa, nicip__silt))
        return impl
    elif isinstance(idx, types.Array
        ) and idx.ndim == 1 and idx.dtype == via__kwh:

        def impl(A, idx):
            sbppz__kkvg, hqpou__ltvew = A.shape
            qvl__nol = A.indptr
            oxl__ykuzu = A.indices
            mdcsr__upq = A.data
            ddhq__omzsa = len(idx)
            rhv__oylk = 0
            tswn__dqo = 0
            for mrre__raa in range(ddhq__omzsa):
                hml__ibcuu = idx[mrre__raa]
                kzti__lwsr = qvl__nol[hml__ibcuu]
                cenrd__hrge = qvl__nol[hml__ibcuu + 1]
                rhv__oylk += cenrd__hrge - kzti__lwsr
            pume__henpf = np.empty(ddhq__omzsa + 1, via__kwh)
            klqqq__slo = np.empty(rhv__oylk, via__kwh)
            pfilc__ghx = np.empty(rhv__oylk, aohd__xat)
            pume__henpf[0] = 0
            for mrre__raa in range(ddhq__omzsa):
                hml__ibcuu = idx[mrre__raa]
                kzti__lwsr = qvl__nol[hml__ibcuu]
                cenrd__hrge = qvl__nol[hml__ibcuu + 1]
                klqqq__slo[tswn__dqo:tswn__dqo + cenrd__hrge - kzti__lwsr
                    ] = oxl__ykuzu[kzti__lwsr:cenrd__hrge]
                pfilc__ghx[tswn__dqo:tswn__dqo + cenrd__hrge - kzti__lwsr
                    ] = mdcsr__upq[kzti__lwsr:cenrd__hrge]
                tswn__dqo += cenrd__hrge - kzti__lwsr
                pume__henpf[mrre__raa + 1] = tswn__dqo
            srke__xdgs = init_csr_matrix(pfilc__ghx, klqqq__slo,
                pume__henpf, (ddhq__omzsa, hqpou__ltvew))
            return srke__xdgs
        return impl
    raise BodoError(
        f'getitem for CSR matrix with index type {idx} not supported yet.')
