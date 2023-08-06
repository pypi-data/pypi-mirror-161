"""
Analysis and transformation for HDF5 support.
"""
import types as pytypes
import numba
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, find_callname, find_const, get_definition, guard, replace_arg_nodes, require
import bodo
import bodo.io
from bodo.utils.transform import get_const_value_inner


class H5_IO:

    def __init__(self, func_ir, _locals, flags, arg_types):
        self.func_ir = func_ir
        self.locals = _locals
        self.flags = flags
        self.arg_types = arg_types

    def handle_possible_h5_read(self, assign, lhs, rhs):
        fgf__wvpcg = self._get_h5_type(lhs, rhs)
        if fgf__wvpcg is not None:
            supn__bluz = str(fgf__wvpcg.dtype)
            whce__abcpv = 'def _h5_read_impl(dset, index):\n'
            whce__abcpv += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(fgf__wvpcg.ndim, supn__bluz))
            oggp__zscm = {}
            exec(whce__abcpv, {}, oggp__zscm)
            xkzs__edt = oggp__zscm['_h5_read_impl']
            ffwjq__pqp = compile_to_numba_ir(xkzs__edt, {'bodo': bodo}
                ).blocks.popitem()[1]
            ipion__xor = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(ffwjq__pqp, [rhs.value, ipion__xor])
            amdq__pagj = ffwjq__pqp.body[:-3]
            amdq__pagj[-1].target = assign.target
            return amdq__pagj
        return None

    def _get_h5_type(self, lhs, rhs):
        fgf__wvpcg = self._get_h5_type_locals(lhs)
        if fgf__wvpcg is not None:
            return fgf__wvpcg
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        ipion__xor = rhs.index if rhs.op == 'getitem' else rhs.index_var
        bqpln__tbn = guard(find_const, self.func_ir, ipion__xor)
        require(not isinstance(bqpln__tbn, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            rhfoc__rshga = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            iidcv__hgan = get_const_value_inner(self.func_ir, rhfoc__rshga,
                arg_types=self.arg_types)
            obj_name_list.append(iidcv__hgan)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        kmtl__msn = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        oiu__reby = h5py.File(kmtl__msn, 'r')
        hyzwh__xdmk = oiu__reby
        for iidcv__hgan in obj_name_list:
            hyzwh__xdmk = hyzwh__xdmk[iidcv__hgan]
        require(isinstance(hyzwh__xdmk, h5py.Dataset))
        jec__yqg = len(hyzwh__xdmk.shape)
        qspls__elbqh = numba.np.numpy_support.from_dtype(hyzwh__xdmk.dtype)
        oiu__reby.close()
        return types.Array(qspls__elbqh, jec__yqg, 'C')

    def _get_h5_type_locals(self, varname):
        grjdj__noozv = self.locals.pop(varname, None)
        if grjdj__noozv is None and varname is not None:
            grjdj__noozv = self.flags.h5_types.get(varname, None)
        return grjdj__noozv
