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
        ydkbk__ffcn = self._get_h5_type(lhs, rhs)
        if ydkbk__ffcn is not None:
            ivfa__oytp = str(ydkbk__ffcn.dtype)
            folxn__vbluw = 'def _h5_read_impl(dset, index):\n'
            folxn__vbluw += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(ydkbk__ffcn.ndim, ivfa__oytp))
            gil__cren = {}
            exec(folxn__vbluw, {}, gil__cren)
            udhrm__rwte = gil__cren['_h5_read_impl']
            fvfe__qtar = compile_to_numba_ir(udhrm__rwte, {'bodo': bodo}
                ).blocks.popitem()[1]
            itu__mnhy = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(fvfe__qtar, [rhs.value, itu__mnhy])
            xzwt__xyo = fvfe__qtar.body[:-3]
            xzwt__xyo[-1].target = assign.target
            return xzwt__xyo
        return None

    def _get_h5_type(self, lhs, rhs):
        ydkbk__ffcn = self._get_h5_type_locals(lhs)
        if ydkbk__ffcn is not None:
            return ydkbk__ffcn
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        itu__mnhy = rhs.index if rhs.op == 'getitem' else rhs.index_var
        mjg__xojt = guard(find_const, self.func_ir, itu__mnhy)
        require(not isinstance(mjg__xojt, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            nlub__tbcw = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            ftw__bsh = get_const_value_inner(self.func_ir, nlub__tbcw,
                arg_types=self.arg_types)
            obj_name_list.append(ftw__bsh)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        xjo__rucl = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        itfcq__qldna = h5py.File(xjo__rucl, 'r')
        ruo__vbosl = itfcq__qldna
        for ftw__bsh in obj_name_list:
            ruo__vbosl = ruo__vbosl[ftw__bsh]
        require(isinstance(ruo__vbosl, h5py.Dataset))
        kgo__ehxr = len(ruo__vbosl.shape)
        ligyt__abp = numba.np.numpy_support.from_dtype(ruo__vbosl.dtype)
        itfcq__qldna.close()
        return types.Array(ligyt__abp, kgo__ehxr, 'C')

    def _get_h5_type_locals(self, varname):
        qles__ygnc = self.locals.pop(varname, None)
        if qles__ygnc is None and varname is not None:
            qles__ygnc = self.flags.h5_types.get(varname, None)
        return qles__ygnc
