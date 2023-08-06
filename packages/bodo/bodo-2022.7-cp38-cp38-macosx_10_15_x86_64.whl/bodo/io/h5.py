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
        cydhw__nipxj = self._get_h5_type(lhs, rhs)
        if cydhw__nipxj is not None:
            mafw__hif = str(cydhw__nipxj.dtype)
            cbylx__tmezu = 'def _h5_read_impl(dset, index):\n'
            cbylx__tmezu += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(cydhw__nipxj.ndim, mafw__hif))
            srcus__lvs = {}
            exec(cbylx__tmezu, {}, srcus__lvs)
            bdcc__wgp = srcus__lvs['_h5_read_impl']
            ukt__atwa = compile_to_numba_ir(bdcc__wgp, {'bodo': bodo}
                ).blocks.popitem()[1]
            iue__nhc = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(ukt__atwa, [rhs.value, iue__nhc])
            lvovx__rutpz = ukt__atwa.body[:-3]
            lvovx__rutpz[-1].target = assign.target
            return lvovx__rutpz
        return None

    def _get_h5_type(self, lhs, rhs):
        cydhw__nipxj = self._get_h5_type_locals(lhs)
        if cydhw__nipxj is not None:
            return cydhw__nipxj
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        iue__nhc = rhs.index if rhs.op == 'getitem' else rhs.index_var
        gvuql__slmjy = guard(find_const, self.func_ir, iue__nhc)
        require(not isinstance(gvuql__slmjy, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            jqgkz__njjk = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            zszar__iuegi = get_const_value_inner(self.func_ir, jqgkz__njjk,
                arg_types=self.arg_types)
            obj_name_list.append(zszar__iuegi)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        gyz__teb = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        tml__pkg = h5py.File(gyz__teb, 'r')
        npkn__hakr = tml__pkg
        for zszar__iuegi in obj_name_list:
            npkn__hakr = npkn__hakr[zszar__iuegi]
        require(isinstance(npkn__hakr, h5py.Dataset))
        dpy__hhg = len(npkn__hakr.shape)
        ycewm__jog = numba.np.numpy_support.from_dtype(npkn__hakr.dtype)
        tml__pkg.close()
        return types.Array(ycewm__jog, dpy__hhg, 'C')

    def _get_h5_type_locals(self, varname):
        uuz__tehsp = self.locals.pop(varname, None)
        if uuz__tehsp is None and varname is not None:
            uuz__tehsp = self.flags.h5_types.get(varname, None)
        return uuz__tehsp
