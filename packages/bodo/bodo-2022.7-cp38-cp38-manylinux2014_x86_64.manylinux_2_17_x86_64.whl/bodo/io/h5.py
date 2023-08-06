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
        hhq__qnq = self._get_h5_type(lhs, rhs)
        if hhq__qnq is not None:
            cwepa__ipac = str(hhq__qnq.dtype)
            smzp__hduy = 'def _h5_read_impl(dset, index):\n'
            smzp__hduy += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(hhq__qnq.ndim, cwepa__ipac))
            qyci__kpd = {}
            exec(smzp__hduy, {}, qyci__kpd)
            dndjm__cks = qyci__kpd['_h5_read_impl']
            urx__neb = compile_to_numba_ir(dndjm__cks, {'bodo': bodo}
                ).blocks.popitem()[1]
            ukprk__rnzqe = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(urx__neb, [rhs.value, ukprk__rnzqe])
            mlabq__lawwl = urx__neb.body[:-3]
            mlabq__lawwl[-1].target = assign.target
            return mlabq__lawwl
        return None

    def _get_h5_type(self, lhs, rhs):
        hhq__qnq = self._get_h5_type_locals(lhs)
        if hhq__qnq is not None:
            return hhq__qnq
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        ukprk__rnzqe = rhs.index if rhs.op == 'getitem' else rhs.index_var
        ufs__thjv = guard(find_const, self.func_ir, ukprk__rnzqe)
        require(not isinstance(ufs__thjv, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            vzu__yih = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            nfq__bdfk = get_const_value_inner(self.func_ir, vzu__yih,
                arg_types=self.arg_types)
            obj_name_list.append(nfq__bdfk)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        trnsu__vxuh = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        xmyr__var = h5py.File(trnsu__vxuh, 'r')
        mbih__kjodq = xmyr__var
        for nfq__bdfk in obj_name_list:
            mbih__kjodq = mbih__kjodq[nfq__bdfk]
        require(isinstance(mbih__kjodq, h5py.Dataset))
        qpc__siqw = len(mbih__kjodq.shape)
        maft__vnh = numba.np.numpy_support.from_dtype(mbih__kjodq.dtype)
        xmyr__var.close()
        return types.Array(maft__vnh, qpc__siqw, 'C')

    def _get_h5_type_locals(self, varname):
        ahb__qsh = self.locals.pop(varname, None)
        if ahb__qsh is None and varname is not None:
            ahb__qsh = self.flags.h5_types.get(varname, None)
        return ahb__qsh
