"""
Numba monkey patches to fix issues related to Bodo. Should be imported before any
other module in bodo package.
"""
import copy
import functools
import hashlib
import inspect
import itertools
import operator
import os
import re
import sys
import textwrap
import traceback
import types as pytypes
import warnings
from collections import OrderedDict
from collections.abc import Sequence
from contextlib import ExitStack
import numba
import numba.core.boxing
import numba.core.inline_closurecall
import numba.core.typing.listdecl
import numba.np.linalg
from numba.core import analysis, cgutils, errors, ir, ir_utils, types
from numba.core.compiler import Compiler
from numba.core.errors import ForceLiteralArg, LiteralTypingError, TypingError
from numba.core.ir_utils import GuardException, _create_function_from_code_obj, analysis, build_definitions, find_callname, get_definition, guard, has_no_side_effect, mk_unique_var, remove_dead_extensions, replace_vars_inner, require, visit_vars_extensions, visit_vars_inner
from numba.core.types import literal
from numba.core.types.functions import _bt_as_lines, _ResolutionFailures, _termcolor, _unlit_non_poison
from numba.core.typing.templates import AbstractTemplate, Signature, _EmptyImplementationEntry, _inline_info, _OverloadAttributeTemplate, infer_global, signature
from numba.core.typing.typeof import Purpose, typeof
from numba.experimental.jitclass import base as jitclass_base
from numba.experimental.jitclass import decorators as jitclass_decorators
from numba.extending import NativeValue, lower_builtin, typeof_impl
from numba.parfors.parfor import get_expr_args
from bodo.utils.python_310_bytecode_pass import Bodo310ByteCodePass, peep_hole_call_function_ex_to_call_function_kw, peep_hole_fuse_dict_add_updates, peep_hole_fuse_tuple_adds
from bodo.utils.typing import BodoError, get_overload_const_str, is_overload_constant_str, raise_bodo_error
_check_numba_change = False
numba.core.typing.templates._IntrinsicTemplate.prefer_literal = True


def run_frontend(func, inline_closures=False, emit_dels=False):
    from numba.core.utils import PYVERSION
    zchme__ljp = numba.core.bytecode.FunctionIdentity.from_function(func)
    beet__hzkcf = numba.core.interpreter.Interpreter(zchme__ljp)
    jaekj__zpg = numba.core.bytecode.ByteCode(func_id=zchme__ljp)
    func_ir = beet__hzkcf.interpret(jaekj__zpg)
    if PYVERSION == (3, 10):
        func_ir = peep_hole_call_function_ex_to_call_function_kw(func_ir)
        func_ir = peep_hole_fuse_dict_add_updates(func_ir)
        func_ir = peep_hole_fuse_tuple_adds(func_ir)
    if inline_closures:
        from numba.core.inline_closurecall import InlineClosureCallPass


        class DummyPipeline:

            def __init__(self, f_ir):
                self.state = numba.core.compiler.StateDict()
                self.state.typingctx = None
                self.state.targetctx = None
                self.state.args = None
                self.state.func_ir = f_ir
                self.state.typemap = None
                self.state.return_type = None
                self.state.calltypes = None
        numba.core.rewrites.rewrite_registry.apply('before-inference',
            DummyPipeline(func_ir).state)
        grfu__nxtp = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        grfu__nxtp.run()
    pykp__xdg = numba.core.postproc.PostProcessor(func_ir)
    pykp__xdg.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, swrrw__nhlcz in visit_vars_extensions.items():
        if isinstance(stmt, t):
            swrrw__nhlcz(stmt, callback, cbdata)
            return
    if isinstance(stmt, ir.Assign):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Arg):
        stmt.name = visit_vars_inner(stmt.name, callback, cbdata)
    elif isinstance(stmt, ir.Return):
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Raise):
        stmt.exception = visit_vars_inner(stmt.exception, callback, cbdata)
    elif isinstance(stmt, ir.Branch):
        stmt.cond = visit_vars_inner(stmt.cond, callback, cbdata)
    elif isinstance(stmt, ir.Jump):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
    elif isinstance(stmt, ir.Del):
        var = ir.Var(None, stmt.value, stmt.loc)
        var = visit_vars_inner(var, callback, cbdata)
        stmt.value = var.name
    elif isinstance(stmt, ir.DelAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
    elif isinstance(stmt, ir.SetAttr):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.attr = visit_vars_inner(stmt.attr, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.DelItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
    elif isinstance(stmt, ir.StaticSetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index_var = visit_vars_inner(stmt.index_var, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.SetItem):
        stmt.target = visit_vars_inner(stmt.target, callback, cbdata)
        stmt.index = visit_vars_inner(stmt.index, callback, cbdata)
        stmt.value = visit_vars_inner(stmt.value, callback, cbdata)
    elif isinstance(stmt, ir.Print):
        stmt.args = [visit_vars_inner(x, callback, cbdata) for x in stmt.args]
        stmt.vararg = visit_vars_inner(stmt.vararg, callback, cbdata)
    else:
        pass
    return


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.visit_vars_stmt)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '52b7b645ba65c35f3cf564f936e113261db16a2dff1e80fbee2459af58844117':
        warnings.warn('numba.core.ir_utils.visit_vars_stmt has changed')
numba.core.ir_utils.visit_vars_stmt = visit_vars_stmt
old_run_pass = numba.core.typed_passes.InlineOverloads.run_pass


def InlineOverloads_run_pass(self, state):
    import bodo
    bodo.compiler.bodo_overload_inline_pass(state.func_ir, state.typingctx,
        state.targetctx, state.typemap, state.calltypes)
    return old_run_pass(self, state)


numba.core.typed_passes.InlineOverloads.run_pass = InlineOverloads_run_pass
from numba.core.ir_utils import _add_alias, alias_analysis_extensions, alias_func_extensions
_immutable_type_class = (types.Number, types.scalars._NPDatetimeBase, types
    .iterators.RangeType, types.UnicodeType)


def is_immutable_type(var, typemap):
    if typemap is None or var not in typemap:
        return False
    typ = typemap[var]
    if isinstance(typ, _immutable_type_class):
        return True
    if isinstance(typ, types.BaseTuple) and all(isinstance(t,
        _immutable_type_class) for t in typ.types):
        return True
    return False


def find_potential_aliases(blocks, args, typemap, func_ir, alias_map=None,
    arg_aliases=None):
    if alias_map is None:
        alias_map = {}
    if arg_aliases is None:
        arg_aliases = set(a for a in args if not is_immutable_type(a, typemap))
    func_ir._definitions = build_definitions(func_ir.blocks)
    dpx__vjrv = ['ravel', 'transpose', 'reshape']
    for ptm__xwm in blocks.values():
        for pkbaa__ftdc in ptm__xwm.body:
            if type(pkbaa__ftdc) in alias_analysis_extensions:
                swrrw__nhlcz = alias_analysis_extensions[type(pkbaa__ftdc)]
                swrrw__nhlcz(pkbaa__ftdc, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(pkbaa__ftdc, ir.Assign):
                vdgze__vys = pkbaa__ftdc.value
                vik__eolfp = pkbaa__ftdc.target.name
                if is_immutable_type(vik__eolfp, typemap):
                    continue
                if isinstance(vdgze__vys, ir.Var
                    ) and vik__eolfp != vdgze__vys.name:
                    _add_alias(vik__eolfp, vdgze__vys.name, alias_map,
                        arg_aliases)
                if isinstance(vdgze__vys, ir.Expr) and (vdgze__vys.op ==
                    'cast' or vdgze__vys.op in ['getitem', 'static_getitem']):
                    _add_alias(vik__eolfp, vdgze__vys.value.name, alias_map,
                        arg_aliases)
                if isinstance(vdgze__vys, ir.Expr
                    ) and vdgze__vys.op == 'inplace_binop':
                    _add_alias(vik__eolfp, vdgze__vys.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(vdgze__vys, ir.Expr
                    ) and vdgze__vys.op == 'getattr' and vdgze__vys.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(vik__eolfp, vdgze__vys.value.name, alias_map,
                        arg_aliases)
                if isinstance(vdgze__vys, ir.Expr
                    ) and vdgze__vys.op == 'getattr' and vdgze__vys.attr not in [
                    'shape'] and vdgze__vys.value.name in arg_aliases:
                    _add_alias(vik__eolfp, vdgze__vys.value.name, alias_map,
                        arg_aliases)
                if isinstance(vdgze__vys, ir.Expr
                    ) and vdgze__vys.op == 'getattr' and vdgze__vys.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(vik__eolfp, vdgze__vys.value.name, alias_map,
                        arg_aliases)
                if isinstance(vdgze__vys, ir.Expr) and vdgze__vys.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(vik__eolfp, typemap):
                    for cznz__nkdti in vdgze__vys.items:
                        _add_alias(vik__eolfp, cznz__nkdti.name, alias_map,
                            arg_aliases)
                if isinstance(vdgze__vys, ir.Expr) and vdgze__vys.op == 'call':
                    bvx__vpt = guard(find_callname, func_ir, vdgze__vys,
                        typemap)
                    if bvx__vpt is None:
                        continue
                    abxmr__whzja, gkf__yyy = bvx__vpt
                    if bvx__vpt in alias_func_extensions:
                        yzsx__rikp = alias_func_extensions[bvx__vpt]
                        yzsx__rikp(vik__eolfp, vdgze__vys.args, alias_map,
                            arg_aliases)
                    if gkf__yyy == 'numpy' and abxmr__whzja in dpx__vjrv:
                        _add_alias(vik__eolfp, vdgze__vys.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(gkf__yyy, ir.Var
                        ) and abxmr__whzja in dpx__vjrv:
                        _add_alias(vik__eolfp, gkf__yyy.name, alias_map,
                            arg_aliases)
    jxipr__obx = copy.deepcopy(alias_map)
    for cznz__nkdti in jxipr__obx:
        for anw__vqac in jxipr__obx[cznz__nkdti]:
            alias_map[cznz__nkdti] |= alias_map[anw__vqac]
        for anw__vqac in jxipr__obx[cznz__nkdti]:
            alias_map[anw__vqac] = alias_map[cznz__nkdti]
    return alias_map, arg_aliases


if _check_numba_change:
    lines = inspect.getsource(ir_utils.find_potential_aliases)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e6cf3e0f502f903453eb98346fc6854f87dc4ea1ac62f65c2d6aef3bf690b6c5':
        warnings.warn('ir_utils.find_potential_aliases has changed')
ir_utils.find_potential_aliases = find_potential_aliases
numba.parfors.array_analysis.find_potential_aliases = find_potential_aliases
if _check_numba_change:
    lines = inspect.getsource(ir_utils.dead_code_elimination)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '40a8626300a1a17523944ec7842b093c91258bbc60844bbd72191a35a4c366bf':
        warnings.warn('ir_utils.dead_code_elimination has changed')


def mini_dce(func_ir, typemap=None, alias_map=None, arg_aliases=None):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    jzg__kkqte = compute_cfg_from_blocks(func_ir.blocks)
    rkz__jfgj = compute_use_defs(func_ir.blocks)
    shis__ohq = compute_live_map(jzg__kkqte, func_ir.blocks, rkz__jfgj.
        usemap, rkz__jfgj.defmap)
    yioku__qaxyr = True
    while yioku__qaxyr:
        yioku__qaxyr = False
        for xpk__zwg, block in func_ir.blocks.items():
            lives = {cznz__nkdti.name for cznz__nkdti in block.terminator.
                list_vars()}
            for fre__zrrfa, bsya__klm in jzg__kkqte.successors(xpk__zwg):
                lives |= shis__ohq[fre__zrrfa]
            awu__ybblq = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    vik__eolfp = stmt.target
                    etnji__fwdf = stmt.value
                    if vik__eolfp.name not in lives:
                        if isinstance(etnji__fwdf, ir.Expr
                            ) and etnji__fwdf.op == 'make_function':
                            continue
                        if isinstance(etnji__fwdf, ir.Expr
                            ) and etnji__fwdf.op == 'getattr':
                            continue
                        if isinstance(etnji__fwdf, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(vik__eolfp,
                            None), types.Function):
                            continue
                        if isinstance(etnji__fwdf, ir.Expr
                            ) and etnji__fwdf.op == 'build_map':
                            continue
                        if isinstance(etnji__fwdf, ir.Expr
                            ) and etnji__fwdf.op == 'build_tuple':
                            continue
                    if isinstance(etnji__fwdf, ir.Var
                        ) and vik__eolfp.name == etnji__fwdf.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    hnvyg__ezy = analysis.ir_extension_usedefs[type(stmt)]
                    vpegs__rjwo, bzb__jqfis = hnvyg__ezy(stmt)
                    lives -= bzb__jqfis
                    lives |= vpegs__rjwo
                else:
                    lives |= {cznz__nkdti.name for cznz__nkdti in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(vik__eolfp.name)
                awu__ybblq.append(stmt)
            awu__ybblq.reverse()
            if len(block.body) != len(awu__ybblq):
                yioku__qaxyr = True
            block.body = awu__ybblq


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    jxexp__kzvmi = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (jxexp__kzvmi,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    xwodc__iznn = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), xwodc__iznn)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '7f6974584cb10e49995b652827540cc6732e497c0b9f8231b44fd83fcc1c0a83':
        warnings.warn(
            'numba.core.typing.templates.make_overload_template has changed')
numba.core.typing.templates.make_overload_template = make_overload_template


def _resolve(self, typ, attr):
    if self._attr != attr:
        return None
    if isinstance(typ, types.TypeRef):
        assert typ == self.key
    else:
        assert isinstance(typ, self.key)


    class MethodTemplate(AbstractTemplate):
        key = self.key, attr
        _inline = self._inline
        _no_unliteral = getattr(self, '_no_unliteral', False)
        _overload_func = staticmethod(self._overload_func)
        _inline_overloads = self._inline_overloads
        prefer_literal = self.prefer_literal

        def generic(_, args, kws):
            args = (typ,) + tuple(args)
            fnty = self._get_function_type(self.context, typ)
            sig = self._get_signature(self.context, fnty, args, kws)
            sig = sig.replace(pysig=numba.core.utils.pysignature(self.
                _overload_func))
            for ixdde__ckf in fnty.templates:
                self._inline_overloads.update(ixdde__ckf._inline_overloads)
            if sig is not None:
                return sig.as_method()
    return types.BoundFunction(MethodTemplate, typ)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadMethodTemplate._resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ce8e0935dc939d0867ef969e1ed2975adb3533a58a4133fcc90ae13c4418e4d6':
        warnings.warn(
            'numba.core.typing.templates._OverloadMethodTemplate._resolve has changed'
            )
numba.core.typing.templates._OverloadMethodTemplate._resolve = _resolve


def make_overload_attribute_template(typ, attr, overload_func, inline,
    prefer_literal=False, base=_OverloadAttributeTemplate, **kwargs):
    assert isinstance(typ, types.Type) or issubclass(typ, types.Type)
    name = 'OverloadAttributeTemplate_%s_%s' % (typ, attr)
    no_unliteral = kwargs.pop('no_unliteral', False)
    xwodc__iznn = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), xwodc__iznn)
    return obj


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        make_overload_attribute_template)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f066c38c482d6cf8bf5735a529c3264118ba9b52264b24e58aad12a6b1960f5d':
        warnings.warn(
            'numba.core.typing.templates.make_overload_attribute_template has changed'
            )
numba.core.typing.templates.make_overload_attribute_template = (
    make_overload_attribute_template)


def generic(self, args, kws):
    from numba.core.typed_passes import PreLowerStripPhis
    cwyga__yfj, rfpwb__uyknc = self._get_impl(args, kws)
    if cwyga__yfj is None:
        return
    jngn__exk = types.Dispatcher(cwyga__yfj)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        zxy__vuhxu = cwyga__yfj._compiler
        flags = compiler.Flags()
        pkob__govhu = zxy__vuhxu.targetdescr.typing_context
        hjz__vybe = zxy__vuhxu.targetdescr.target_context
        edr__rrizw = zxy__vuhxu.pipeline_class(pkob__govhu, hjz__vybe, None,
            None, None, flags, None)
        dyy__asgzh = InlineWorker(pkob__govhu, hjz__vybe, zxy__vuhxu.locals,
            edr__rrizw, flags, None)
        xmg__bsy = jngn__exk.dispatcher.get_call_template
        ixdde__ckf, wqq__joq, lev__rmtkj, kws = xmg__bsy(rfpwb__uyknc, kws)
        if lev__rmtkj in self._inline_overloads:
            return self._inline_overloads[lev__rmtkj]['iinfo'].signature
        ir = dyy__asgzh.run_untyped_passes(jngn__exk.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, hjz__vybe, ir, lev__rmtkj, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, lev__rmtkj, None)
        self._inline_overloads[sig.args] = {'folded_args': lev__rmtkj}
        lerkg__kdvr = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = lerkg__kdvr
        if not self._inline.is_always_inline:
            sig = jngn__exk.get_call_type(self.context, rfpwb__uyknc, kws)
            self._compiled_overloads[sig.args] = jngn__exk.get_overload(sig)
        xxzt__eyxe = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': lev__rmtkj,
            'iinfo': xxzt__eyxe}
    else:
        sig = jngn__exk.get_call_type(self.context, rfpwb__uyknc, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = jngn__exk.get_overload(sig)
    return sig


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5d453a6d0215ebf0bab1279ff59eb0040b34938623be99142ce20acc09cdeb64':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate.generic has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate.generic = generic


def bound_function(template_key, no_unliteral=False):

    def wrapper(method_resolver):

        @functools.wraps(method_resolver)
        def attribute_resolver(self, ty):


            class MethodTemplate(AbstractTemplate):
                key = template_key

                def generic(_, args, kws):
                    sig = method_resolver(self, ty, args, kws)
                    if sig is not None and sig.recvr is None:
                        sig = sig.replace(recvr=ty)
                    return sig
            MethodTemplate._no_unliteral = no_unliteral
            return types.BoundFunction(MethodTemplate, ty)
        return attribute_resolver
    return wrapper


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.bound_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a2feefe64eae6a15c56affc47bf0c1d04461f9566913442d539452b397103322':
        warnings.warn('numba.core.typing.templates.bound_function has changed')
numba.core.typing.templates.bound_function = bound_function


def get_call_type(self, context, args, kws):
    from numba.core import utils
    deq__ynvu = [True, False]
    ecot__ktedh = [False, True]
    zzqf__nhekw = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    cqzs__sfxm = get_local_target(context)
    nlg__fxuc = utils.order_by_target_specificity(cqzs__sfxm, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for etcou__mxpur in nlg__fxuc:
        jakw__aos = etcou__mxpur(context)
        ntpj__aeql = deq__ynvu if jakw__aos.prefer_literal else ecot__ktedh
        ntpj__aeql = [True] if getattr(jakw__aos, '_no_unliteral', False
            ) else ntpj__aeql
        for nfyec__jkrr in ntpj__aeql:
            try:
                if nfyec__jkrr:
                    sig = jakw__aos.apply(args, kws)
                else:
                    zqtku__ivphk = tuple([_unlit_non_poison(a) for a in args])
                    nuu__ohiq = {nuhbj__lgudm: _unlit_non_poison(
                        cznz__nkdti) for nuhbj__lgudm, cznz__nkdti in kws.
                        items()}
                    sig = jakw__aos.apply(zqtku__ivphk, nuu__ohiq)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    zzqf__nhekw.add_error(jakw__aos, False, e, nfyec__jkrr)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = jakw__aos.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    tmyh__xaaah = getattr(jakw__aos, 'cases', None)
                    if tmyh__xaaah is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            tmyh__xaaah)
                    else:
                        msg = 'No match.'
                    zzqf__nhekw.add_error(jakw__aos, True, msg, nfyec__jkrr)
    zzqf__nhekw.raise_error()


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BaseFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '25f038a7216f8e6f40068ea81e11fd9af8ad25d19888f7304a549941b01b7015':
        warnings.warn(
            'numba.core.types.functions.BaseFunction.get_call_type has changed'
            )
numba.core.types.functions.BaseFunction.get_call_type = get_call_type
bodo_typing_error_info = """
This is often caused by the use of unsupported features or typing issues.
See https://docs.bodo.ai/
"""


def get_call_type2(self, context, args, kws):
    ixdde__ckf = self.template(context)
    yowgc__dgp = None
    eal__tpali = None
    fvhv__soqi = None
    ntpj__aeql = [True, False] if ixdde__ckf.prefer_literal else [False, True]
    ntpj__aeql = [True] if getattr(ixdde__ckf, '_no_unliteral', False
        ) else ntpj__aeql
    for nfyec__jkrr in ntpj__aeql:
        if nfyec__jkrr:
            try:
                fvhv__soqi = ixdde__ckf.apply(args, kws)
            except Exception as hszx__vmqpa:
                if isinstance(hszx__vmqpa, errors.ForceLiteralArg):
                    raise hszx__vmqpa
                yowgc__dgp = hszx__vmqpa
                fvhv__soqi = None
            else:
                break
        else:
            biq__gzzvg = tuple([_unlit_non_poison(a) for a in args])
            kaxei__ggr = {nuhbj__lgudm: _unlit_non_poison(cznz__nkdti) for 
                nuhbj__lgudm, cznz__nkdti in kws.items()}
            bowd__jusvv = biq__gzzvg == args and kws == kaxei__ggr
            if not bowd__jusvv and fvhv__soqi is None:
                try:
                    fvhv__soqi = ixdde__ckf.apply(biq__gzzvg, kaxei__ggr)
                except Exception as hszx__vmqpa:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        hszx__vmqpa, errors.NumbaError):
                        raise hszx__vmqpa
                    if isinstance(hszx__vmqpa, errors.ForceLiteralArg):
                        if ixdde__ckf.prefer_literal:
                            raise hszx__vmqpa
                    eal__tpali = hszx__vmqpa
                else:
                    break
    if fvhv__soqi is None and (eal__tpali is not None or yowgc__dgp is not None
        ):
        wnvz__yaxu = '- Resolution failure for {} arguments:\n{}\n'
        qezx__cfq = _termcolor.highlight(wnvz__yaxu)
        if numba.core.config.DEVELOPER_MODE:
            iola__hexh = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    yqwpa__ssw = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    yqwpa__ssw = ['']
                umxwd__htrc = '\n{}'.format(2 * iola__hexh)
                ybhn__rxefk = _termcolor.reset(umxwd__htrc + umxwd__htrc.
                    join(_bt_as_lines(yqwpa__ssw)))
                return _termcolor.reset(ybhn__rxefk)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            nbe__bitox = str(e)
            nbe__bitox = nbe__bitox if nbe__bitox else str(repr(e)) + add_bt(e)
            allrl__voxk = errors.TypingError(textwrap.dedent(nbe__bitox))
            return qezx__cfq.format(literalness, str(allrl__voxk))
        import bodo
        if isinstance(yowgc__dgp, bodo.utils.typing.BodoError):
            raise yowgc__dgp
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', yowgc__dgp) +
                nested_msg('non-literal', eal__tpali))
        else:
            if 'missing a required argument' in yowgc__dgp.msg:
                msg = 'missing a required argument'
            else:
                msg = 'Compilation error for '
                if isinstance(self.this, bodo.hiframes.pd_dataframe_ext.
                    DataFrameType):
                    msg += 'DataFrame.'
                elif isinstance(self.this, bodo.hiframes.pd_series_ext.
                    SeriesType):
                    msg += 'Series.'
                msg += f'{self.typing_key[1]}().{bodo_typing_error_info}'
            raise errors.TypingError(msg, loc=yowgc__dgp.loc)
    return fvhv__soqi


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.BoundFunction.
        get_call_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '502cd77c0084452e903a45a0f1f8107550bfbde7179363b57dabd617ce135f4a':
        warnings.warn(
            'numba.core.types.functions.BoundFunction.get_call_type has changed'
            )
numba.core.types.functions.BoundFunction.get_call_type = get_call_type2


def string_from_string_and_size(self, string, size):
    from llvmlite import ir as lir
    fnty = lir.FunctionType(self.pyobj, [self.cstring, self.py_ssize_t])
    abxmr__whzja = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=abxmr__whzja)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            grw__xajvd = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), grw__xajvd)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    qtnsl__nilcf = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            qtnsl__nilcf.append(types.Omitted(a.value))
        else:
            qtnsl__nilcf.append(self.typeof_pyval(a))
    rfhn__ilffa = None
    try:
        error = None
        rfhn__ilffa = self.compile(tuple(qtnsl__nilcf))
    except errors.ForceLiteralArg as e:
        ozmu__wazg = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if ozmu__wazg:
            mfrtq__cpfi = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            gqlfh__wejc = ', '.join('Arg #{} is {}'.format(i, args[i]) for
                i in sorted(ozmu__wazg))
            raise errors.CompilerError(mfrtq__cpfi.format(gqlfh__wejc))
        rfpwb__uyknc = []
        try:
            for i, cznz__nkdti in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        rfpwb__uyknc.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        rfpwb__uyknc.append(types.literal(args[i]))
                else:
                    rfpwb__uyknc.append(args[i])
            args = rfpwb__uyknc
        except (OSError, FileNotFoundError) as tgops__vazzf:
            error = FileNotFoundError(str(tgops__vazzf) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                rfhn__ilffa = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        jdug__qamgl = []
        for i, tgy__tlmg in enumerate(args):
            val = tgy__tlmg.value if isinstance(tgy__tlmg, numba.core.
                dispatcher.OmittedArg) else tgy__tlmg
            try:
                glgpe__iutj = typeof(val, Purpose.argument)
            except ValueError as mbdf__cylf:
                jdug__qamgl.append((i, str(mbdf__cylf)))
            else:
                if glgpe__iutj is None:
                    jdug__qamgl.append((i,
                        f'cannot determine Numba type of value {val}'))
        if jdug__qamgl:
            tgrl__nsfl = '\n'.join(f'- argument {i}: {jdzp__gjcxa}' for i,
                jdzp__gjcxa in jdug__qamgl)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{tgrl__nsfl}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                hwm__gjxgj = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                keo__nwhdy = False
                for kdqa__pbjlw in hwm__gjxgj:
                    if kdqa__pbjlw in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        keo__nwhdy = True
                        break
                if not keo__nwhdy:
                    msg = f'{str(e)}'
                msg += '\n' + e.loc.strformat() + '\n'
                e.patch_message(msg)
        error_rewrite(e, 'typing')
    except errors.UnsupportedError as e:
        error_rewrite(e, 'unsupported_error')
    except (errors.NotDefinedError, errors.RedefinedError, errors.
        VerificationError) as e:
        error_rewrite(e, 'interpreter')
    except errors.ConstantInferenceError as e:
        error_rewrite(e, 'constant_inference')
    except bodo.utils.typing.BodoError as e:
        error = bodo.utils.typing.BodoError(str(e))
    except Exception as e:
        if numba.core.config.SHOW_HELP:
            if hasattr(e, 'patch_message'):
                grw__xajvd = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), grw__xajvd)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return rfhn__ilffa


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher._DispatcherBase.
        _compile_for_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5cdfbf0b13a528abf9f0408e70f67207a03e81d610c26b1acab5b2dc1f79bf06':
        warnings.warn(
            'numba.core.dispatcher._DispatcherBase._compile_for_args has changed'
            )
numba.core.dispatcher._DispatcherBase._compile_for_args = _compile_for_args


def resolve_gb_agg_funcs(cres):
    from bodo.ir.aggregate import gb_agg_cfunc_addr
    for cjyb__vllzp in cres.library._codegen._engine._defined_symbols:
        if cjyb__vllzp.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in cjyb__vllzp and (
            'bodo_gb_udf_update_local' in cjyb__vllzp or 
            'bodo_gb_udf_combine' in cjyb__vllzp or 'bodo_gb_udf_eval' in
            cjyb__vllzp or 'bodo_gb_apply_general_udfs' in cjyb__vllzp):
            gb_agg_cfunc_addr[cjyb__vllzp
                ] = cres.library.get_pointer_to_function(cjyb__vllzp)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for cjyb__vllzp in cres.library._codegen._engine._defined_symbols:
        if cjyb__vllzp.startswith('cfunc') and ('get_join_cond_addr' not in
            cjyb__vllzp or 'bodo_join_gen_cond' in cjyb__vllzp):
            join_gen_cond_cfunc_addr[cjyb__vllzp
                ] = cres.library.get_pointer_to_function(cjyb__vllzp)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    cwyga__yfj = self._get_dispatcher_for_current_target()
    if cwyga__yfj is not self:
        return cwyga__yfj.compile(sig)
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        if not self._can_compile:
            raise RuntimeError('compilation disabled')
        with self._compiling_counter:
            args, return_type = sigutils.normalize_signature(sig)
            jkn__nsyts = self.overloads.get(tuple(args))
            if jkn__nsyts is not None:
                return jkn__nsyts.entry_point
            cres = self._cache.load_overload(sig, self.targetctx)
            if cres is not None:
                resolve_gb_agg_funcs(cres)
                resolve_join_general_cond_funcs(cres)
                self._cache_hits[sig] += 1
                if not cres.objectmode:
                    self.targetctx.insert_user_function(cres.entry_point,
                        cres.fndesc, [cres.library])
                self.add_overload(cres)
                return cres.entry_point
            self._cache_misses[sig] += 1
            fvjty__ghix = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=fvjty__ghix):
                try:
                    cres = self._compiler.compile(args, return_type)
                except errors.ForceLiteralArg as e:

                    def folded(args, kws):
                        return self._compiler.fold_argument_types(args, kws)[1]
                    raise e.bind_fold_arguments(folded)
                self.add_overload(cres)
            if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:
                if bodo.get_rank() == 0:
                    self._cache.save_overload(sig, cres)
            else:
                nnac__petwm = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in nnac__petwm:
                    self._cache.save_overload(sig, cres)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.Dispatcher.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '934ec993577ea3b1c7dd2181ac02728abf8559fd42c17062cc821541b092ff8f':
        warnings.warn('numba.core.dispatcher.Dispatcher.compile has changed')
numba.core.dispatcher.Dispatcher.compile = compile


def _get_module_for_linking(self):
    import llvmlite.binding as ll
    self._ensure_finalized()
    if self._shared_module is not None:
        return self._shared_module
    mtqk__lnu = self._final_module
    krdmu__fwll = []
    kzssx__zorc = 0
    for fn in mtqk__lnu.functions:
        kzssx__zorc += 1
        if not fn.is_declaration and fn.linkage == ll.Linkage.external:
            if 'get_agg_udf_addr' not in fn.name:
                if 'bodo_gb_udf_update_local' in fn.name:
                    continue
                if 'bodo_gb_udf_combine' in fn.name:
                    continue
                if 'bodo_gb_udf_eval' in fn.name:
                    continue
                if 'bodo_gb_apply_general_udfs' in fn.name:
                    continue
            if 'get_join_cond_addr' not in fn.name:
                if 'bodo_join_gen_cond' in fn.name:
                    continue
            krdmu__fwll.append(fn.name)
    if kzssx__zorc == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if krdmu__fwll:
        mtqk__lnu = mtqk__lnu.clone()
        for name in krdmu__fwll:
            mtqk__lnu.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = mtqk__lnu
    return mtqk__lnu


if _check_numba_change:
    lines = inspect.getsource(numba.core.codegen.CPUCodeLibrary.
        _get_module_for_linking)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '56dde0e0555b5ec85b93b97c81821bce60784515a1fbf99e4542e92d02ff0a73':
        warnings.warn(
            'numba.core.codegen.CPUCodeLibrary._get_module_for_linking has changed'
            )
numba.core.codegen.CPUCodeLibrary._get_module_for_linking = (
    _get_module_for_linking)


def propagate(self, typeinfer):
    import bodo
    errors = []
    for slbtl__ocwy in self.constraints:
        loc = slbtl__ocwy.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                slbtl__ocwy(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                beq__fje = numba.core.errors.TypingError(str(e), loc=
                    slbtl__ocwy.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(beq__fje, e))
            except bodo.utils.typing.BodoError as e:
                if loc not in e.locs_in_msg:
                    errors.append(bodo.utils.typing.BodoError(str(e.msg) +
                        '\n' + loc.strformat() + '\n', locs_in_msg=e.
                        locs_in_msg + [loc]))
                else:
                    errors.append(bodo.utils.typing.BodoError(e.msg,
                        locs_in_msg=e.locs_in_msg))
            except Exception as e:
                from numba.core import utils
                if utils.use_old_style_errors():
                    numba.core.typeinfer._logger.debug('captured error',
                        exc_info=e)
                    msg = """Internal error at {con}.
{err}
Enable logging at debug level for details."""
                    beq__fje = numba.core.errors.TypingError(msg.format(con
                        =slbtl__ocwy, err=str(e)), loc=slbtl__ocwy.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(beq__fje, e))
                elif utils.use_new_style_errors():
                    raise e
                else:
                    msg = (
                        f"Unknown CAPTURED_ERRORS style: '{numba.core.config.CAPTURED_ERRORS}'."
                        )
                    assert 0, msg
    return errors


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.ConstraintNetwork.propagate)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e73635eeba9ba43cb3372f395b747ae214ce73b729fb0adba0a55237a1cb063':
        warnings.warn(
            'numba.core.typeinfer.ConstraintNetwork.propagate has changed')
numba.core.typeinfer.ConstraintNetwork.propagate = propagate


def raise_error(self):
    import bodo
    for jfx__fbj in self._failures.values():
        for jts__tgcy in jfx__fbj:
            if isinstance(jts__tgcy.error, ForceLiteralArg):
                raise jts__tgcy.error
            if isinstance(jts__tgcy.error, bodo.utils.typing.BodoError):
                raise jts__tgcy.error
    raise TypingError(self.format())


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.functions.
        _ResolutionFailures.raise_error)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84b89430f5c8b46cfc684804e6037f00a0f170005cd128ad245551787b2568ea':
        warnings.warn(
            'numba.core.types.functions._ResolutionFailures.raise_error has changed'
            )
numba.core.types.functions._ResolutionFailures.raise_error = raise_error


def bodo_remove_dead_block(block, lives, call_table, arg_aliases, alias_map,
    alias_set, func_ir, typemap):
    from bodo.transforms.distributed_pass import saved_array_analysis
    from bodo.utils.utils import is_array_typ, is_expr
    rrm__eeit = False
    awu__ybblq = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        yvfd__sef = set()
        edww__ekcqr = lives & alias_set
        for cznz__nkdti in edww__ekcqr:
            yvfd__sef |= alias_map[cznz__nkdti]
        lives_n_aliases = lives | yvfd__sef | arg_aliases
        if type(stmt) in remove_dead_extensions:
            swrrw__nhlcz = remove_dead_extensions[type(stmt)]
            stmt = swrrw__nhlcz(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                rrm__eeit = True
                continue
        if isinstance(stmt, ir.Assign):
            vik__eolfp = stmt.target
            etnji__fwdf = stmt.value
            if vik__eolfp.name not in lives:
                if has_no_side_effect(etnji__fwdf, lives_n_aliases, call_table
                    ):
                    rrm__eeit = True
                    continue
                if isinstance(etnji__fwdf, ir.Expr
                    ) and etnji__fwdf.op == 'call' and call_table[etnji__fwdf
                    .func.name] == ['astype']:
                    qrg__gcko = guard(get_definition, func_ir, etnji__fwdf.func
                        )
                    if (qrg__gcko is not None and qrg__gcko.op == 'getattr' and
                        isinstance(typemap[qrg__gcko.value.name], types.
                        Array) and qrg__gcko.attr == 'astype'):
                        rrm__eeit = True
                        continue
            if saved_array_analysis and vik__eolfp.name in lives and is_expr(
                etnji__fwdf, 'getattr'
                ) and etnji__fwdf.attr == 'shape' and is_array_typ(typemap[
                etnji__fwdf.value.name]
                ) and etnji__fwdf.value.name not in lives:
                buq__styb = {cznz__nkdti: nuhbj__lgudm for nuhbj__lgudm,
                    cznz__nkdti in func_ir.blocks.items()}
                if block in buq__styb:
                    xpk__zwg = buq__styb[block]
                    sxwz__oww = saved_array_analysis.get_equiv_set(xpk__zwg)
                    wssjw__carz = sxwz__oww.get_equiv_set(etnji__fwdf.value)
                    if wssjw__carz is not None:
                        for cznz__nkdti in wssjw__carz:
                            if cznz__nkdti.endswith('#0'):
                                cznz__nkdti = cznz__nkdti[:-2]
                            if cznz__nkdti in typemap and is_array_typ(typemap
                                [cznz__nkdti]) and cznz__nkdti in lives:
                                etnji__fwdf.value = ir.Var(etnji__fwdf.
                                    value.scope, cznz__nkdti, etnji__fwdf.
                                    value.loc)
                                rrm__eeit = True
                                break
            if isinstance(etnji__fwdf, ir.Var
                ) and vik__eolfp.name == etnji__fwdf.name:
                rrm__eeit = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                rrm__eeit = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            hnvyg__ezy = analysis.ir_extension_usedefs[type(stmt)]
            vpegs__rjwo, bzb__jqfis = hnvyg__ezy(stmt)
            lives -= bzb__jqfis
            lives |= vpegs__rjwo
        else:
            lives |= {cznz__nkdti.name for cznz__nkdti in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                ngs__hjh = set()
                if isinstance(etnji__fwdf, ir.Expr):
                    ngs__hjh = {cznz__nkdti.name for cznz__nkdti in
                        etnji__fwdf.list_vars()}
                if vik__eolfp.name not in ngs__hjh:
                    lives.remove(vik__eolfp.name)
        awu__ybblq.append(stmt)
    awu__ybblq.reverse()
    block.body = awu__ybblq
    return rrm__eeit


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            exv__unzg, = args
            if isinstance(exv__unzg, types.IterableType):
                dtype = exv__unzg.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), exv__unzg)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    iid__nwf = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (iid__nwf, self.dtype)
    super(types.Set, self).__init__(name=name)


types.Set.__init__ = Set__init__


@lower_builtin(operator.eq, types.UnicodeType, types.UnicodeType)
def eq_str(context, builder, sig, args):
    func = numba.cpython.unicode.unicode_eq(*sig.args)
    return context.compile_internal(builder, func, sig, args)


numba.parfors.parfor.push_call_vars = (lambda blocks, saved_globals,
    saved_getattrs, typemap, nested=False: None)


def maybe_literal(value):
    if isinstance(value, (list, dict, pytypes.FunctionType)):
        return
    if isinstance(value, tuple):
        try:
            return types.Tuple([literal(x) for x in value])
        except LiteralTypingError as akd__qnxd:
            return
    try:
        return literal(value)
    except LiteralTypingError as akd__qnxd:
        return


if _check_numba_change:
    lines = inspect.getsource(types.maybe_literal)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8fb2fd93acf214b28e33e37d19dc2f7290a42792ec59b650553ac278854b5081':
        warnings.warn('types.maybe_literal has changed')
types.maybe_literal = maybe_literal
types.misc.maybe_literal = maybe_literal


def CacheImpl__init__(self, py_func):
    self._lineno = py_func.__code__.co_firstlineno
    try:
        xdjm__uptgb = py_func.__qualname__
    except AttributeError as akd__qnxd:
        xdjm__uptgb = py_func.__name__
    yawn__cran = inspect.getfile(py_func)
    for cls in self._locator_classes:
        jrfg__jsbkx = cls.from_function(py_func, yawn__cran)
        if jrfg__jsbkx is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (xdjm__uptgb, yawn__cran))
    self._locator = jrfg__jsbkx
    zzaxs__rdk = inspect.getfile(py_func)
    vsbx__fwf = os.path.splitext(os.path.basename(zzaxs__rdk))[0]
    if yawn__cran.startswith('<ipython-'):
        xum__bpeyn = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', vsbx__fwf, count=1)
        if xum__bpeyn == vsbx__fwf:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        vsbx__fwf = xum__bpeyn
    bcb__dhrsm = '%s.%s' % (vsbx__fwf, xdjm__uptgb)
    xozz__dpbif = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(bcb__dhrsm, xozz__dpbif
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    yqqee__nvkt = list(filter(lambda a: self._istuple(a.name), args))
    if len(yqqee__nvkt) == 2 and fn.__name__ == 'add':
        aph__dwvt = self.typemap[yqqee__nvkt[0].name]
        zldob__key = self.typemap[yqqee__nvkt[1].name]
        if aph__dwvt.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                yqqee__nvkt[1]))
        if zldob__key.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                yqqee__nvkt[0]))
        try:
            robqe__sokkl = [equiv_set.get_shape(x) for x in yqqee__nvkt]
            if None in robqe__sokkl:
                return None
            igv__hdt = sum(robqe__sokkl, ())
            return ArrayAnalysis.AnalyzeResult(shape=igv__hdt)
        except GuardException as akd__qnxd:
            return None
    emlr__dtb = list(filter(lambda a: self._isarray(a.name), args))
    require(len(emlr__dtb) > 0)
    vgojq__sjtp = [x.name for x in emlr__dtb]
    iev__egtwm = [self.typemap[x.name].ndim for x in emlr__dtb]
    akc__vwsfy = max(iev__egtwm)
    require(akc__vwsfy > 0)
    robqe__sokkl = [equiv_set.get_shape(x) for x in emlr__dtb]
    if any(a is None for a in robqe__sokkl):
        return ArrayAnalysis.AnalyzeResult(shape=emlr__dtb[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, emlr__dtb))
    return self._broadcast_assert_shapes(scope, equiv_set, loc,
        robqe__sokkl, vgojq__sjtp)


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.array_analysis.ArrayAnalysis.
        _analyze_broadcast)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6c91fec038f56111338ea2b08f5f0e7f61ebdab1c81fb811fe26658cc354e40f':
        warnings.warn(
            'numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast has changed'
            )
numba.parfors.array_analysis.ArrayAnalysis._analyze_broadcast = (
    _analyze_broadcast)


def slice_size(self, index, dsize, equiv_set, scope, stmts):
    return None, None


numba.parfors.array_analysis.ArrayAnalysis.slice_size = slice_size


def convert_code_obj_to_function(code_obj, caller_ir):
    import bodo
    oibls__nhujw = code_obj.code
    zelbq__irgiu = len(oibls__nhujw.co_freevars)
    ssyp__wiptg = oibls__nhujw.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        hntw__pafcl, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        ssyp__wiptg = [cznz__nkdti.name for cznz__nkdti in hntw__pafcl]
    pxl__qrgk = caller_ir.func_id.func.__globals__
    try:
        pxl__qrgk = getattr(code_obj, 'globals', pxl__qrgk)
    except KeyError as akd__qnxd:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    zyg__hkbup = []
    for x in ssyp__wiptg:
        try:
            haght__xgn = caller_ir.get_definition(x)
        except KeyError as akd__qnxd:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(haght__xgn, (ir.Const, ir.Global, ir.FreeVar)):
            val = haght__xgn.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                jxexp__kzvmi = ir_utils.mk_unique_var('nested_func').replace(
                    '.', '_')
                pxl__qrgk[jxexp__kzvmi] = bodo.jit(distributed=False)(val)
                pxl__qrgk[jxexp__kzvmi].is_nested_func = True
                val = jxexp__kzvmi
            if isinstance(val, CPUDispatcher):
                jxexp__kzvmi = ir_utils.mk_unique_var('nested_func').replace(
                    '.', '_')
                pxl__qrgk[jxexp__kzvmi] = val
                val = jxexp__kzvmi
            zyg__hkbup.append(val)
        elif isinstance(haght__xgn, ir.Expr
            ) and haght__xgn.op == 'make_function':
            yyewk__xnoos = convert_code_obj_to_function(haght__xgn, caller_ir)
            jxexp__kzvmi = ir_utils.mk_unique_var('nested_func').replace('.',
                '_')
            pxl__qrgk[jxexp__kzvmi] = bodo.jit(distributed=False)(yyewk__xnoos)
            pxl__qrgk[jxexp__kzvmi].is_nested_func = True
            zyg__hkbup.append(jxexp__kzvmi)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    hbx__bzxdq = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        zyg__hkbup)])
    uin__miw = ','.join([('c_%d' % i) for i in range(zelbq__irgiu)])
    jwosy__jdlio = list(oibls__nhujw.co_varnames)
    hjj__ypmgy = 0
    cpwtw__dgqsh = oibls__nhujw.co_argcount
    suss__eztci = caller_ir.get_definition(code_obj.defaults)
    if suss__eztci is not None:
        if isinstance(suss__eztci, tuple):
            d = [caller_ir.get_definition(x).value for x in suss__eztci]
            hxp__mfo = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in suss__eztci.items]
            hxp__mfo = tuple(d)
        hjj__ypmgy = len(hxp__mfo)
    gpifo__egkg = cpwtw__dgqsh - hjj__ypmgy
    qlmop__fzl = ','.join([('%s' % jwosy__jdlio[i]) for i in range(
        gpifo__egkg)])
    if hjj__ypmgy:
        zzne__dfrn = [('%s = %s' % (jwosy__jdlio[i + gpifo__egkg], hxp__mfo
            [i])) for i in range(hjj__ypmgy)]
        qlmop__fzl += ', '
        qlmop__fzl += ', '.join(zzne__dfrn)
    return _create_function_from_code_obj(oibls__nhujw, hbx__bzxdq,
        qlmop__fzl, uin__miw, pxl__qrgk)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.convert_code_obj_to_function)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b840769812418d589460e924a15477e83e7919aac8a3dcb0188ff447344aa8ac':
        warnings.warn(
            'numba.core.ir_utils.convert_code_obj_to_function has changed')
numba.core.ir_utils.convert_code_obj_to_function = convert_code_obj_to_function
numba.core.untyped_passes.convert_code_obj_to_function = (
    convert_code_obj_to_function)


def passmanager_run(self, state):
    from numba.core.compiler import _EarlyPipelineCompletion
    if not self.finalized:
        raise RuntimeError('Cannot run non-finalised pipeline')
    from numba.core.compiler_machinery import CompilerPass, _pass_registry
    import bodo
    for hlh__dmxe, (rkupo__dprbd, gnk__ccbif) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % gnk__ccbif)
            ofhry__ieh = _pass_registry.get(rkupo__dprbd).pass_inst
            if isinstance(ofhry__ieh, CompilerPass):
                self._runPass(hlh__dmxe, ofhry__ieh, state)
            else:
                raise BaseException('Legacy pass in use')
        except _EarlyPipelineCompletion as e:
            raise e
        except bodo.utils.typing.BodoError as e:
            raise
        except Exception as e:
            if numba.core.config.DEVELOPER_MODE:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                msg = 'Failed in %s mode pipeline (step: %s)' % (self.
                    pipeline_name, gnk__ccbif)
                woo__pehlz = self._patch_error(msg, e)
                raise woo__pehlz
            else:
                raise e


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler_machinery.PassManager.run)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '43505782e15e690fd2d7e53ea716543bec37aa0633502956864edf649e790cdb':
        warnings.warn(
            'numba.core.compiler_machinery.PassManager.run has changed')
numba.core.compiler_machinery.PassManager.run = passmanager_run
if _check_numba_change:
    lines = inspect.getsource(numba.np.ufunc.parallel._launch_threads)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a57ef28c4168fdd436a5513bba4351ebc6d9fba76c5819f44046431a79b9030f':
        warnings.warn('numba.np.ufunc.parallel._launch_threads has changed')
numba.np.ufunc.parallel._launch_threads = lambda : None


def get_reduce_nodes(reduction_node, nodes, func_ir):
    gezsv__gxdd = None
    bzb__jqfis = {}

    def lookup(var, already_seen, varonly=True):
        val = bzb__jqfis.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    jqjog__kmt = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        vik__eolfp = stmt.target
        etnji__fwdf = stmt.value
        bzb__jqfis[vik__eolfp.name] = etnji__fwdf
        if isinstance(etnji__fwdf, ir.Var) and etnji__fwdf.name in bzb__jqfis:
            etnji__fwdf = lookup(etnji__fwdf, set())
        if isinstance(etnji__fwdf, ir.Expr):
            xorz__leqj = set(lookup(cznz__nkdti, set(), True).name for
                cznz__nkdti in etnji__fwdf.list_vars())
            if name in xorz__leqj:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(etnji__fwdf)]
                udt__eicd = [x for x, epamr__jdp in args if epamr__jdp.name !=
                    name]
                args = [(x, epamr__jdp) for x, epamr__jdp in args if x !=
                    epamr__jdp.name]
                wnmbr__rpfhl = dict(args)
                if len(udt__eicd) == 1:
                    wnmbr__rpfhl[udt__eicd[0]] = ir.Var(vik__eolfp.scope, 
                        name + '#init', vik__eolfp.loc)
                replace_vars_inner(etnji__fwdf, wnmbr__rpfhl)
                gezsv__gxdd = nodes[i:]
                break
    return gezsv__gxdd


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_reduce_nodes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a05b52aff9cb02e595a510cd34e973857303a71097fc5530567cb70ca183ef3b':
        warnings.warn('numba.parfors.parfor.get_reduce_nodes has changed')
numba.parfors.parfor.get_reduce_nodes = get_reduce_nodes


def _can_reorder_stmts(stmt, next_stmt, func_ir, call_table, alias_map,
    arg_aliases):
    from numba.parfors.parfor import Parfor, expand_aliases, is_assert_equiv
    if isinstance(stmt, Parfor) and not isinstance(next_stmt, Parfor
        ) and not isinstance(next_stmt, ir.Print) and (not isinstance(
        next_stmt, ir.Assign) or has_no_side_effect(next_stmt.value, set(),
        call_table) or guard(is_assert_equiv, func_ir, next_stmt.value)):
        zyxc__npju = expand_aliases({cznz__nkdti.name for cznz__nkdti in
            stmt.list_vars()}, alias_map, arg_aliases)
        bnooy__sano = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        jfkd__waa = expand_aliases({cznz__nkdti.name for cznz__nkdti in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        hift__glno = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(bnooy__sano & jfkd__waa | hift__glno & zyxc__npju) == 0:
            return True
    return False


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor._can_reorder_stmts)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '18caa9a01b21ab92b4f79f164cfdbc8574f15ea29deedf7bafdf9b0e755d777c':
        warnings.warn('numba.parfors.parfor._can_reorder_stmts has changed')
numba.parfors.parfor._can_reorder_stmts = _can_reorder_stmts


def get_parfor_writes(parfor, func_ir):
    from numba.parfors.parfor import Parfor
    assert isinstance(parfor, Parfor)
    leh__hrlz = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            leh__hrlz.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                leh__hrlz.update(get_parfor_writes(stmt, func_ir))
    return leh__hrlz


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    leh__hrlz = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        leh__hrlz.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        leh__hrlz = {cznz__nkdti.name for cznz__nkdti in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        leh__hrlz = {cznz__nkdti.name for cznz__nkdti in stmt.
            get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            leh__hrlz.update({cznz__nkdti.name for cznz__nkdti in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        bvx__vpt = guard(find_callname, func_ir, stmt.value)
        if bvx__vpt in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'), (
            'setna', 'bodo.libs.array_kernels'), ('str_arr_item_to_numeric',
            'bodo.libs.str_arr_ext'), ('str_arr_setitem_int_to_str',
            'bodo.libs.str_arr_ext'), ('str_arr_setitem_NA_str',
            'bodo.libs.str_arr_ext'), ('str_arr_set_not_na',
            'bodo.libs.str_arr_ext'), ('get_str_arr_item_copy',
            'bodo.libs.str_arr_ext'), ('set_bit_to_arr',
            'bodo.libs.int_arr_ext')):
            leh__hrlz.add(stmt.value.args[0].name)
        if bvx__vpt == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            leh__hrlz.add(stmt.value.args[1].name)
    return leh__hrlz


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.get_stmt_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1a7a80b64c9a0eb27e99dc8eaae187bde379d4da0b74c84fbf87296d87939974':
        warnings.warn('numba.core.ir_utils.get_stmt_writes has changed')


def patch_message(self, new_message):
    self.msg = new_message
    self.args = (new_message,) + self.args[1:]


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.patch_message)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'ed189a428a7305837e76573596d767b6e840e99f75c05af6941192e0214fa899':
        warnings.warn('numba.core.errors.NumbaError.patch_message has changed')
numba.core.errors.NumbaError.patch_message = patch_message


def add_context(self, msg):
    if numba.core.config.DEVELOPER_MODE:
        self.contexts.append(msg)
        swrrw__nhlcz = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        daui__tur = swrrw__nhlcz.format(self, msg)
        self.args = daui__tur,
    else:
        swrrw__nhlcz = _termcolor.errmsg('{0}')
        daui__tur = swrrw__nhlcz.format(self)
        self.args = daui__tur,
    return self


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.NumbaError.add_context)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '6a388d87788f8432c2152ac55ca9acaa94dbc3b55be973b2cf22dd4ee7179ab8':
        warnings.warn('numba.core.errors.NumbaError.add_context has changed')
numba.core.errors.NumbaError.add_context = add_context


def _get_dist_spec_from_options(spec, **options):
    from bodo.transforms.distributed_analysis import Distribution
    dist_spec = {}
    if 'distributed' in options:
        for sri__nom in options['distributed']:
            dist_spec[sri__nom] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for sri__nom in options['distributed_block']:
            dist_spec[sri__nom] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    luldo__sfmgc = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, nco__ntjzb in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(nco__ntjzb)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    brrxt__qtep = {}
    for ivl__akhp in reversed(inspect.getmro(cls)):
        brrxt__qtep.update(ivl__akhp.__dict__)
    exnm__sojl, kzfi__hfwmy, qry__gnvvh, yhby__cncpp = {}, {}, {}, {}
    for nuhbj__lgudm, cznz__nkdti in brrxt__qtep.items():
        if isinstance(cznz__nkdti, pytypes.FunctionType):
            exnm__sojl[nuhbj__lgudm] = cznz__nkdti
        elif isinstance(cznz__nkdti, property):
            kzfi__hfwmy[nuhbj__lgudm] = cznz__nkdti
        elif isinstance(cznz__nkdti, staticmethod):
            qry__gnvvh[nuhbj__lgudm] = cznz__nkdti
        else:
            yhby__cncpp[nuhbj__lgudm] = cznz__nkdti
    lcb__pqb = (set(exnm__sojl) | set(kzfi__hfwmy) | set(qry__gnvvh)) & set(
        spec)
    if lcb__pqb:
        raise NameError('name shadowing: {0}'.format(', '.join(lcb__pqb)))
    xakx__dqlfv = yhby__cncpp.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(yhby__cncpp)
    if yhby__cncpp:
        msg = 'class members are not yet supported: {0}'
        nsfwq__ycqor = ', '.join(yhby__cncpp.keys())
        raise TypeError(msg.format(nsfwq__ycqor))
    for nuhbj__lgudm, cznz__nkdti in kzfi__hfwmy.items():
        if cznz__nkdti.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(
                nuhbj__lgudm))
    jit_methods = {nuhbj__lgudm: bodo.jit(returns_maybe_distributed=
        luldo__sfmgc)(cznz__nkdti) for nuhbj__lgudm, cznz__nkdti in
        exnm__sojl.items()}
    jit_props = {}
    for nuhbj__lgudm, cznz__nkdti in kzfi__hfwmy.items():
        xwodc__iznn = {}
        if cznz__nkdti.fget:
            xwodc__iznn['get'] = bodo.jit(cznz__nkdti.fget)
        if cznz__nkdti.fset:
            xwodc__iznn['set'] = bodo.jit(cznz__nkdti.fset)
        jit_props[nuhbj__lgudm] = xwodc__iznn
    jit_static_methods = {nuhbj__lgudm: bodo.jit(cznz__nkdti.__func__) for 
        nuhbj__lgudm, cznz__nkdti in qry__gnvvh.items()}
    crd__tfsj = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    dfm__kjl = dict(class_type=crd__tfsj, __doc__=xakx__dqlfv)
    dfm__kjl.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), dfm__kjl)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, crd__tfsj)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(crd__tfsj, typingctx, targetctx).register()
    as_numba_type.register(cls, crd__tfsj.instance_type)
    return cls


if _check_numba_change:
    lines = inspect.getsource(jitclass_base.register_class_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '005e6e2e89a47f77a19ba86305565050d4dbc2412fc4717395adf2da348671a9':
        warnings.warn('jitclass_base.register_class_type has changed')
jitclass_base.register_class_type = register_class_type


def ClassType__init__(self, class_def, ctor_template_cls, struct,
    jit_methods, jit_props, jit_static_methods, dist_spec=None):
    if dist_spec is None:
        dist_spec = {}
    self.class_name = class_def.__name__
    self.class_doc = class_def.__doc__
    self._ctor_template_class = ctor_template_cls
    self.jit_methods = jit_methods
    self.jit_props = jit_props
    self.jit_static_methods = jit_static_methods
    self.struct = struct
    self.dist_spec = dist_spec
    kit__sfka = ','.join('{0}:{1}'.format(nuhbj__lgudm, cznz__nkdti) for 
        nuhbj__lgudm, cznz__nkdti in struct.items())
    nyxv__mlr = ','.join('{0}:{1}'.format(nuhbj__lgudm, cznz__nkdti) for 
        nuhbj__lgudm, cznz__nkdti in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), kit__sfka, nyxv__mlr)
    super(types.misc.ClassType, self).__init__(name)


if _check_numba_change:
    lines = inspect.getsource(types.misc.ClassType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '2b848ea82946c88f540e81f93ba95dfa7cd66045d944152a337fe2fc43451c30':
        warnings.warn('types.misc.ClassType.__init__ has changed')
types.misc.ClassType.__init__ = ClassType__init__


def jitclass(cls_or_spec=None, spec=None, **options):
    if cls_or_spec is not None and spec is None and not isinstance(cls_or_spec,
        type):
        spec = cls_or_spec
        cls_or_spec = None

    def wrap(cls):
        if numba.core.config.DISABLE_JIT:
            return cls
        else:
            from numba.experimental.jitclass.base import ClassBuilder
            return register_class_type(cls, spec, types.ClassType,
                ClassBuilder, **options)
    if cls_or_spec is None:
        return wrap
    else:
        return wrap(cls_or_spec)


if _check_numba_change:
    lines = inspect.getsource(jitclass_decorators.jitclass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '265f1953ee5881d1a5d90238d3c932cd300732e41495657e65bf51e59f7f4af5':
        warnings.warn('jitclass_decorators.jitclass has changed')


def CallConstraint_resolve(self, typeinfer, typevars, fnty):
    assert fnty
    context = typeinfer.context
    lqtaj__wwmrl = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if lqtaj__wwmrl is None:
        return
    twmi__ocoe, hktu__gzrwk = lqtaj__wwmrl
    for a in itertools.chain(twmi__ocoe, hktu__gzrwk.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, twmi__ocoe, hktu__gzrwk)
    except ForceLiteralArg as e:
        wtjy__qdqp = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(wtjy__qdqp, self.kws)
        zgzw__hfzs = set()
        tfgaw__xro = set()
        lgl__oipee = {}
        for hlh__dmxe in e.requested_args:
            juqgm__xrscu = typeinfer.func_ir.get_definition(folded[hlh__dmxe])
            if isinstance(juqgm__xrscu, ir.Arg):
                zgzw__hfzs.add(juqgm__xrscu.index)
                if juqgm__xrscu.index in e.file_infos:
                    lgl__oipee[juqgm__xrscu.index] = e.file_infos[juqgm__xrscu
                        .index]
            else:
                tfgaw__xro.add(hlh__dmxe)
        if tfgaw__xro:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif zgzw__hfzs:
            raise ForceLiteralArg(zgzw__hfzs, loc=self.loc, file_infos=
                lgl__oipee)
    if sig is None:
        qmnhy__benn = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in twmi__ocoe]
        args += [('%s=%s' % (nuhbj__lgudm, cznz__nkdti)) for nuhbj__lgudm,
            cznz__nkdti in sorted(hktu__gzrwk.items())]
        fsgfv__fogpk = qmnhy__benn.format(fnty, ', '.join(map(str, args)))
        qgf__oqzrr = context.explain_function_type(fnty)
        msg = '\n'.join([fsgfv__fogpk, qgf__oqzrr])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        xpcp__xktwf = context.unify_pairs(sig.recvr, fnty.this)
        if xpcp__xktwf is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if xpcp__xktwf is not None and xpcp__xktwf.is_precise():
            gfs__vpeiq = fnty.copy(this=xpcp__xktwf)
            typeinfer.propagate_refined_type(self.func, gfs__vpeiq)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            fkia__oxe = target.getone()
            if context.unify_pairs(fkia__oxe, sig.return_type) == fkia__oxe:
                sig = sig.replace(return_type=fkia__oxe)
    self.signature = sig
    self._add_refine_map(typeinfer, typevars, sig)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typeinfer.CallConstraint.resolve)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c78cd8ffc64b836a6a2ddf0362d481b52b9d380c5249920a87ff4da052ce081f':
        warnings.warn('numba.core.typeinfer.CallConstraint.resolve has changed'
            )
numba.core.typeinfer.CallConstraint.resolve = CallConstraint_resolve


def ForceLiteralArg__init__(self, arg_indices, fold_arguments=None, loc=
    None, file_infos=None):
    super(ForceLiteralArg, self).__init__(
        'Pseudo-exception to force literal arguments in the dispatcher',
        loc=loc)
    self.requested_args = frozenset(arg_indices)
    self.fold_arguments = fold_arguments
    if file_infos is None:
        self.file_infos = {}
    else:
        self.file_infos = file_infos


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b241d5e36a4cf7f4c73a7ad3238693612926606c7a278cad1978070b82fb55ef':
        warnings.warn('numba.core.errors.ForceLiteralArg.__init__ has changed')
numba.core.errors.ForceLiteralArg.__init__ = ForceLiteralArg__init__


def ForceLiteralArg_bind_fold_arguments(self, fold_arguments):
    e = ForceLiteralArg(self.requested_args, fold_arguments, loc=self.loc,
        file_infos=self.file_infos)
    return numba.core.utils.chain_exception(e, self)


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.
        bind_fold_arguments)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1e93cca558f7c604a47214a8f2ec33ee994104cb3e5051166f16d7cc9315141d':
        warnings.warn(
            'numba.core.errors.ForceLiteralArg.bind_fold_arguments has changed'
            )
numba.core.errors.ForceLiteralArg.bind_fold_arguments = (
    ForceLiteralArg_bind_fold_arguments)


def ForceLiteralArg_combine(self, other):
    if not isinstance(other, ForceLiteralArg):
        mfrtq__cpfi = '*other* must be a {} but got a {} instead'
        raise TypeError(mfrtq__cpfi.format(ForceLiteralArg, type(other)))
    return ForceLiteralArg(self.requested_args | other.requested_args,
        file_infos={**self.file_infos, **other.file_infos})


if _check_numba_change:
    lines = inspect.getsource(numba.core.errors.ForceLiteralArg.combine)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '49bf06612776f5d755c1c7d1c5eb91831a57665a8fed88b5651935f3bf33e899':
        warnings.warn('numba.core.errors.ForceLiteralArg.combine has changed')
numba.core.errors.ForceLiteralArg.combine = ForceLiteralArg_combine


def _get_global_type(self, gv):
    from bodo.utils.typing import FunctionLiteral
    ty = self._lookup_global(gv)
    if ty is not None:
        return ty
    if isinstance(gv, pytypes.ModuleType):
        return types.Module(gv)
    if isinstance(gv, pytypes.FunctionType):
        return FunctionLiteral(gv)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.
        _get_global_type)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8ffe6b81175d1eecd62a37639b5005514b4477d88f35f5b5395041ac8c945a4a':
        warnings.warn(
            'numba.core.typing.context.BaseContext._get_global_type has changed'
            )
numba.core.typing.context.BaseContext._get_global_type = _get_global_type


def _legalize_args(self, func_ir, args, kwargs, loc, func_globals,
    func_closures):
    from numba.core import sigutils
    from bodo.utils.transform import get_const_value_inner
    if args:
        raise errors.CompilerError(
            "objectmode context doesn't take any positional arguments")
    ynwd__aqgqb = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for nuhbj__lgudm, cznz__nkdti in kwargs.items():
        jmmz__bnq = None
        try:
            wombh__qrnu = ir.Var(ir.Scope(None, loc), ir_utils.
                mk_unique_var('dummy'), loc)
            func_ir._definitions[wombh__qrnu.name] = [cznz__nkdti]
            jmmz__bnq = get_const_value_inner(func_ir, wombh__qrnu)
            func_ir._definitions.pop(wombh__qrnu.name)
            if isinstance(jmmz__bnq, str):
                jmmz__bnq = sigutils._parse_signature_string(jmmz__bnq)
            if isinstance(jmmz__bnq, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {nuhbj__lgudm} is annotated as type class {jmmz__bnq}."""
                    )
            assert isinstance(jmmz__bnq, types.Type)
            if isinstance(jmmz__bnq, (types.List, types.Set)):
                jmmz__bnq = jmmz__bnq.copy(reflected=False)
            ynwd__aqgqb[nuhbj__lgudm] = jmmz__bnq
        except BodoError as akd__qnxd:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(jmmz__bnq, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(cznz__nkdti, ir.Global):
                    msg = f'Global {cznz__nkdti.name!r} is not defined.'
                if isinstance(cznz__nkdti, ir.FreeVar):
                    msg = f'Freevar {cznz__nkdti.name!r} is not defined.'
            if isinstance(cznz__nkdti, ir.Expr
                ) and cznz__nkdti.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=nuhbj__lgudm, msg=msg, loc=loc)
    for name, typ in ynwd__aqgqb.items():
        self._legalize_arg_type(name, typ, loc)
    return ynwd__aqgqb


if _check_numba_change:
    lines = inspect.getsource(numba.core.withcontexts._ObjModeContextType.
        _legalize_args)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '867c9ba7f1bcf438be56c38e26906bb551f59a99f853a9f68b71208b107c880e':
        warnings.warn(
            'numba.core.withcontexts._ObjModeContextType._legalize_args has changed'
            )
numba.core.withcontexts._ObjModeContextType._legalize_args = _legalize_args


def op_FORMAT_VALUE_byteflow(self, state, inst):
    flags = inst.arg
    if flags & 3 != 0:
        msg = 'str/repr/ascii conversion in f-strings not supported yet'
        raise errors.UnsupportedError(msg, loc=self.get_debug_loc(inst.lineno))
    format_spec = None
    if flags & 4 == 4:
        format_spec = state.pop()
    value = state.pop()
    fmtvar = state.make_temp()
    res = state.make_temp()
    state.append(inst, value=value, res=res, fmtvar=fmtvar, format_spec=
        format_spec)
    state.push(res)


def op_BUILD_STRING_byteflow(self, state, inst):
    psddf__dwg = inst.arg
    assert psddf__dwg > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(psddf__dwg)]))
    tmps = [state.make_temp() for _ in range(psddf__dwg - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    drog__cthyw = ir.Global('format', format, loc=self.loc)
    self.store(value=drog__cthyw, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    noav__vcnk = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=noav__vcnk, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    psddf__dwg = inst.arg
    assert psddf__dwg > 0, 'invalid BUILD_STRING count'
    cwji__nmq = self.get(strings[0])
    for other, hxd__cunc in zip(strings[1:], tmps):
        other = self.get(other)
        vdgze__vys = ir.Expr.binop(operator.add, lhs=cwji__nmq, rhs=other,
            loc=self.loc)
        self.store(vdgze__vys, hxd__cunc)
        cwji__nmq = self.get(hxd__cunc)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    dubg__lilg = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, dubg__lilg])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    bvvl__otah = mk_unique_var(f'{var_name}')
    msbzd__lywj = bvvl__otah.replace('<', '_').replace('>', '_')
    msbzd__lywj = msbzd__lywj.replace('.', '_').replace('$', '_v')
    return msbzd__lywj


if _check_numba_change:
    lines = inspect.getsource(numba.core.inline_closurecall.
        _created_inlined_var_name)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '0d91aac55cd0243e58809afe9d252562f9ae2899cde1112cc01a46804e01821e':
        warnings.warn(
            'numba.core.inline_closurecall._created_inlined_var_name has changed'
            )
numba.core.inline_closurecall._created_inlined_var_name = (
    _created_inlined_var_name)


def resolve_number___call__(self, classty):
    import numpy as np
    from numba.core.typing.templates import make_callable_template
    import bodo
    ty = classty.instance_type
    if isinstance(ty, types.NPDatetime):

        def typer(val1, val2):
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(val1,
                'numpy.datetime64')
            if val1 == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
                if not is_overload_constant_str(val2):
                    raise_bodo_error(
                        "datetime64(): 'units' must be a 'str' specifying 'ns'"
                        )
                cmix__wli = get_overload_const_str(val2)
                if cmix__wli != 'ns':
                    raise BodoError("datetime64(): 'units' must be 'ns'")
                return types.NPDatetime('ns')
    else:

        def typer(val):
            if isinstance(val, (types.BaseTuple, types.Sequence)):
                fnty = self.context.resolve_value_type(np.array)
                sig = fnty.get_call_type(self.context, (val, types.DType(ty
                    )), {})
                return sig.return_type
            elif isinstance(val, (types.Number, types.Boolean, types.
                IntEnumMember)):
                return ty
            elif val == types.unicode_type:
                return ty
            elif isinstance(val, (types.NPDatetime, types.NPTimedelta)):
                if ty.bitwidth == 64:
                    return ty
                else:
                    msg = (
                        f'Cannot cast {val} to {ty} as {ty} is not 64 bits wide.'
                        )
                    raise errors.TypingError(msg)
            elif isinstance(val, types.Array
                ) and val.ndim == 0 and val.dtype == ty:
                return ty
            else:
                msg = f'Casting {val} to {ty} directly is unsupported.'
                if isinstance(val, types.Array):
                    msg += f" Try doing '<array>.astype(np.{ty})' instead"
                raise errors.TypingError(msg)
    return types.Function(make_callable_template(key=ty, typer=typer))


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.builtins.
        NumberClassAttribute.resolve___call__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fdaf0c7d0820130481bb2bd922985257b9281b670f0bafffe10e51cabf0d5081':
        warnings.warn(
            'numba.core.typing.builtins.NumberClassAttribute.resolve___call__ has changed'
            )
numba.core.typing.builtins.NumberClassAttribute.resolve___call__ = (
    resolve_number___call__)


def on_assign(self, states, assign):
    if assign.target.name == states['varname']:
        scope = states['scope']
        wbnf__iuok = states['defmap']
        if len(wbnf__iuok) == 0:
            bbg__ipm = assign.target
            numba.core.ssa._logger.debug('first assign: %s', bbg__ipm)
            if bbg__ipm.name not in scope.localvars:
                bbg__ipm = scope.define(assign.target.name, loc=assign.loc)
        else:
            bbg__ipm = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=bbg__ipm, value=assign.value, loc=assign.loc)
        wbnf__iuok[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    bcd__yok = []
    for nuhbj__lgudm, cznz__nkdti in typing.npydecl.registry.globals:
        if nuhbj__lgudm == func:
            bcd__yok.append(cznz__nkdti)
    for nuhbj__lgudm, cznz__nkdti in typing.templates.builtin_registry.globals:
        if nuhbj__lgudm == func:
            bcd__yok.append(cznz__nkdti)
    if len(bcd__yok) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return bcd__yok


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    dhjpd__ahgbc = {}
    blzfj__tnl = find_topo_order(blocks)
    kisgd__ptfq = {}
    for xpk__zwg in blzfj__tnl:
        block = blocks[xpk__zwg]
        awu__ybblq = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                vik__eolfp = stmt.target.name
                etnji__fwdf = stmt.value
                if (etnji__fwdf.op == 'getattr' and etnji__fwdf.attr in
                    arr_math and isinstance(typemap[etnji__fwdf.value.name],
                    types.npytypes.Array)):
                    etnji__fwdf = stmt.value
                    zhv__mignz = etnji__fwdf.value
                    dhjpd__ahgbc[vik__eolfp] = zhv__mignz
                    scope = zhv__mignz.scope
                    loc = zhv__mignz.loc
                    crbn__zok = ir.Var(scope, mk_unique_var('$np_g_var'), loc)
                    typemap[crbn__zok.name] = types.misc.Module(numpy)
                    axmhp__mfn = ir.Global('np', numpy, loc)
                    ifdu__skfu = ir.Assign(axmhp__mfn, crbn__zok, loc)
                    etnji__fwdf.value = crbn__zok
                    awu__ybblq.append(ifdu__skfu)
                    func_ir._definitions[crbn__zok.name] = [axmhp__mfn]
                    func = getattr(numpy, etnji__fwdf.attr)
                    wsuo__yyup = get_np_ufunc_typ_lst(func)
                    kisgd__ptfq[vik__eolfp] = wsuo__yyup
                if (etnji__fwdf.op == 'call' and etnji__fwdf.func.name in
                    dhjpd__ahgbc):
                    zhv__mignz = dhjpd__ahgbc[etnji__fwdf.func.name]
                    goffp__grn = calltypes.pop(etnji__fwdf)
                    uwha__hgq = goffp__grn.args[:len(etnji__fwdf.args)]
                    gve__ewvn = {name: typemap[cznz__nkdti.name] for name,
                        cznz__nkdti in etnji__fwdf.kws}
                    riavy__tjqsa = kisgd__ptfq[etnji__fwdf.func.name]
                    ubgcu__ffayq = None
                    for eit__bkz in riavy__tjqsa:
                        try:
                            ubgcu__ffayq = eit__bkz.get_call_type(typingctx,
                                [typemap[zhv__mignz.name]] + list(uwha__hgq
                                ), gve__ewvn)
                            typemap.pop(etnji__fwdf.func.name)
                            typemap[etnji__fwdf.func.name] = eit__bkz
                            calltypes[etnji__fwdf] = ubgcu__ffayq
                            break
                        except Exception as akd__qnxd:
                            pass
                    if ubgcu__ffayq is None:
                        raise TypeError(
                            f'No valid template found for {etnji__fwdf.func.name}'
                            )
                    etnji__fwdf.args = [zhv__mignz] + etnji__fwdf.args
            awu__ybblq.append(stmt)
        block.body = awu__ybblq


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    tkfd__mfo = ufunc.nin
    mxsz__rst = ufunc.nout
    gpifo__egkg = ufunc.nargs
    assert gpifo__egkg == tkfd__mfo + mxsz__rst
    if len(args) < tkfd__mfo:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), tkfd__mfo))
    if len(args) > gpifo__egkg:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            gpifo__egkg))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    ysfsr__ljr = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    ztqo__psg = max(ysfsr__ljr)
    nuxvd__kcyfm = args[tkfd__mfo:]
    if not all(d == ztqo__psg for d in ysfsr__ljr[tkfd__mfo:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(ytlg__edc, types.ArrayCompatible) and not
        isinstance(ytlg__edc, types.Bytes) for ytlg__edc in nuxvd__kcyfm):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(ytlg__edc.mutable for ytlg__edc in nuxvd__kcyfm):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    frf__qhswx = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    ngex__tvbcj = None
    if ztqo__psg > 0 and len(nuxvd__kcyfm) < ufunc.nout:
        ngex__tvbcj = 'C'
        nvj__nxn = [(x.layout if isinstance(x, types.ArrayCompatible) and 
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in nvj__nxn and 'F' in nvj__nxn:
            ngex__tvbcj = 'F'
    return frf__qhswx, nuxvd__kcyfm, ztqo__psg, ngex__tvbcj


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.Numpy_rules_ufunc.
        _handle_inputs)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4b97c64ad9c3d50e082538795054f35cf6d2fe962c3ca40e8377a4601b344d5c':
        warnings.warn('Numpy_rules_ufunc._handle_inputs has changed')
numba.core.typing.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)
numba.np.ufunc.dufunc.npydecl.Numpy_rules_ufunc._handle_inputs = (
    _Numpy_Rules_ufunc_handle_inputs)


def DictType__init__(self, keyty, valty, initial_value=None):
    from numba.types import DictType, InitialValue, NoneType, Optional, Tuple, TypeRef, unliteral
    assert not isinstance(keyty, TypeRef)
    assert not isinstance(valty, TypeRef)
    keyty = unliteral(keyty)
    valty = unliteral(valty)
    if isinstance(keyty, (Optional, NoneType)):
        cjmnk__iwdh = 'Dict.key_type cannot be of type {}'
        raise TypingError(cjmnk__iwdh.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        cjmnk__iwdh = 'Dict.value_type cannot be of type {}'
        raise TypingError(cjmnk__iwdh.format(valty))
    self.key_type = keyty
    self.value_type = valty
    self.keyvalue_type = Tuple([keyty, valty])
    name = '{}[{},{}]<iv={}>'.format(self.__class__.__name__, keyty, valty,
        initial_value)
    super(DictType, self).__init__(name)
    InitialValue.__init__(self, initial_value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.types.containers.DictType.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '475acd71224bd51526750343246e064ff071320c0d10c17b8b8ac81d5070d094':
        warnings.warn('DictType.__init__ has changed')
numba.core.types.containers.DictType.__init__ = DictType__init__


def _legalize_arg_types(self, args):
    for i, a in enumerate(args, start=1):
        if isinstance(a, types.Dispatcher):
            msg = (
                'Does not support function type inputs into with-context for arg {}'
                )
            raise errors.TypingError(msg.format(i))


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.ObjModeLiftedWith.
        _legalize_arg_types)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4793f44ebc7da8843e8f298e08cd8a5428b4b84b89fd9d5c650273fdb8fee5ee':
        warnings.warn('ObjModeLiftedWith._legalize_arg_types has changed')
numba.core.dispatcher.ObjModeLiftedWith._legalize_arg_types = (
    _legalize_arg_types)


def _overload_template_get_impl(self, args, kws):
    yuiy__pfof = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[yuiy__pfof]
        return impl, args
    except KeyError as akd__qnxd:
        pass
    impl, args = self._build_impl(yuiy__pfof, args, kws)
    return impl, args


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.templates.
        _OverloadFunctionTemplate._get_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '4e27d07b214ca16d6e8ed88f70d886b6b095e160d8f77f8df369dd4ed2eb3fae':
        warnings.warn(
            'numba.core.typing.templates._OverloadFunctionTemplate._get_impl has changed'
            )
numba.core.typing.templates._OverloadFunctionTemplate._get_impl = (
    _overload_template_get_impl)


def remove_dead_parfor(parfor, lives, lives_n_aliases, arg_aliases,
    alias_map, func_ir, typemap):
    from numba.core.analysis import compute_cfg_from_blocks, compute_live_map, compute_use_defs
    from numba.core.ir_utils import find_topo_order
    from numba.parfors.parfor import _add_liveness_return_block, _update_parfor_get_setitems, dummy_return_in_loop_body, get_index_var, remove_dead_parfor_recursive, simplify_parfor_body_CFG
    with dummy_return_in_loop_body(parfor.loop_body):
        tvcf__mfhlt = find_topo_order(parfor.loop_body)
    bzq__kmkc = tvcf__mfhlt[0]
    xgod__vwtzf = {}
    _update_parfor_get_setitems(parfor.loop_body[bzq__kmkc].body, parfor.
        index_var, alias_map, xgod__vwtzf, lives_n_aliases)
    zxl__hung = set(xgod__vwtzf.keys())
    for msiz__pwaqa in tvcf__mfhlt:
        if msiz__pwaqa == bzq__kmkc:
            continue
        for stmt in parfor.loop_body[msiz__pwaqa].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            jyzk__cvra = set(cznz__nkdti.name for cznz__nkdti in stmt.
                list_vars())
            tzl__ucj = jyzk__cvra & zxl__hung
            for a in tzl__ucj:
                xgod__vwtzf.pop(a, None)
    for msiz__pwaqa in tvcf__mfhlt:
        if msiz__pwaqa == bzq__kmkc:
            continue
        block = parfor.loop_body[msiz__pwaqa]
        mfc__xls = xgod__vwtzf.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            mfc__xls, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    tkfop__hjy = max(blocks.keys())
    xxfz__knmgq, qls__hab = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    jjgg__etk = ir.Jump(xxfz__knmgq, ir.Loc('parfors_dummy', -1))
    blocks[tkfop__hjy].body.append(jjgg__etk)
    jzg__kkqte = compute_cfg_from_blocks(blocks)
    rkz__jfgj = compute_use_defs(blocks)
    shis__ohq = compute_live_map(jzg__kkqte, blocks, rkz__jfgj.usemap,
        rkz__jfgj.defmap)
    alias_set = set(alias_map.keys())
    for xpk__zwg, block in blocks.items():
        awu__ybblq = []
        ckkse__fygt = {cznz__nkdti.name for cznz__nkdti in block.terminator
            .list_vars()}
        for fre__zrrfa, bsya__klm in jzg__kkqte.successors(xpk__zwg):
            ckkse__fygt |= shis__ohq[fre__zrrfa]
        for stmt in reversed(block.body):
            yvfd__sef = ckkse__fygt & alias_set
            for cznz__nkdti in yvfd__sef:
                ckkse__fygt |= alias_map[cznz__nkdti]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in ckkse__fygt and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                bvx__vpt = guard(find_callname, func_ir, stmt.value)
                if bvx__vpt == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in ckkse__fygt and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            ckkse__fygt |= {cznz__nkdti.name for cznz__nkdti in stmt.
                list_vars()}
            awu__ybblq.append(stmt)
        awu__ybblq.reverse()
        block.body = awu__ybblq
    typemap.pop(qls__hab.name)
    blocks[tkfop__hjy].body.pop()

    def trim_empty_parfor_branches(parfor):
        yioku__qaxyr = False
        blocks = parfor.loop_body.copy()
        for xpk__zwg, block in blocks.items():
            if len(block.body):
                int__fntev = block.body[-1]
                if isinstance(int__fntev, ir.Branch):
                    if len(blocks[int__fntev.truebr].body) == 1 and len(blocks
                        [int__fntev.falsebr].body) == 1:
                        uyce__dnnd = blocks[int__fntev.truebr].body[0]
                        otihj__cudfl = blocks[int__fntev.falsebr].body[0]
                        if isinstance(uyce__dnnd, ir.Jump) and isinstance(
                            otihj__cudfl, ir.Jump
                            ) and uyce__dnnd.target == otihj__cudfl.target:
                            parfor.loop_body[xpk__zwg].body[-1] = ir.Jump(
                                uyce__dnnd.target, int__fntev.loc)
                            yioku__qaxyr = True
                    elif len(blocks[int__fntev.truebr].body) == 1:
                        uyce__dnnd = blocks[int__fntev.truebr].body[0]
                        if isinstance(uyce__dnnd, ir.Jump
                            ) and uyce__dnnd.target == int__fntev.falsebr:
                            parfor.loop_body[xpk__zwg].body[-1] = ir.Jump(
                                uyce__dnnd.target, int__fntev.loc)
                            yioku__qaxyr = True
                    elif len(blocks[int__fntev.falsebr].body) == 1:
                        otihj__cudfl = blocks[int__fntev.falsebr].body[0]
                        if isinstance(otihj__cudfl, ir.Jump
                            ) and otihj__cudfl.target == int__fntev.truebr:
                            parfor.loop_body[xpk__zwg].body[-1] = ir.Jump(
                                otihj__cudfl.target, int__fntev.loc)
                            yioku__qaxyr = True
        return yioku__qaxyr
    yioku__qaxyr = True
    while yioku__qaxyr:
        """
        Process parfor body recursively.
        Note that this is the only place in this function that uses the
        argument lives instead of lives_n_aliases.  The former does not
        include the aliases of live variables but only the live variable
        names themselves.  See a comment in this function for how that
        is used.
        """
        remove_dead_parfor_recursive(parfor, lives, arg_aliases, alias_map,
            func_ir, typemap)
        simplify_parfor_body_CFG(func_ir.blocks)
        yioku__qaxyr = trim_empty_parfor_branches(parfor)
    bhf__kma = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        bhf__kma &= len(block.body) == 0
    if bhf__kma:
        return None
    return parfor


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.remove_dead_parfor)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1c9b008a7ead13e988e1efe67618d8f87f0b9f3d092cc2cd6bfcd806b1fdb859':
        warnings.warn('remove_dead_parfor has changed')
numba.parfors.parfor.remove_dead_parfor = remove_dead_parfor
numba.core.ir_utils.remove_dead_extensions[numba.parfors.parfor.Parfor
    ] = remove_dead_parfor


def simplify_parfor_body_CFG(blocks):
    from numba.core.analysis import compute_cfg_from_blocks
    from numba.core.ir_utils import simplify_CFG
    from numba.parfors.parfor import Parfor
    nanr__uxtsv = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                nanr__uxtsv += 1
                parfor = stmt
                anl__sya = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = anl__sya.scope
                loc = ir.Loc('parfors_dummy', -1)
                fhpn__xjxsf = ir.Var(scope, mk_unique_var('$const'), loc)
                anl__sya.body.append(ir.Assign(ir.Const(0, loc),
                    fhpn__xjxsf, loc))
                anl__sya.body.append(ir.Return(fhpn__xjxsf, loc))
                jzg__kkqte = compute_cfg_from_blocks(parfor.loop_body)
                for kyu__uefg in jzg__kkqte.dead_nodes():
                    del parfor.loop_body[kyu__uefg]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                anl__sya = parfor.loop_body[max(parfor.loop_body.keys())]
                anl__sya.body.pop()
                anl__sya.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return nanr__uxtsv


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.simplify_parfor_body_CFG)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '437ae96a5e8ec64a2b69a4f23ba8402a1d170262a5400aa0aa7bfe59e03bf726':
        warnings.warn('simplify_parfor_body_CFG has changed')
numba.parfors.parfor.simplify_parfor_body_CFG = simplify_parfor_body_CFG


def _lifted_compile(self, sig):
    import numba.core.event as ev
    from numba.core import compiler, sigutils
    from numba.core.compiler_lock import global_compiler_lock
    from numba.core.ir_utils import remove_dels
    with ExitStack() as scope:
        cres = None

        def cb_compiler(dur):
            if cres is not None:
                self._callback_add_compiler_timer(dur, cres)

        def cb_llvm(dur):
            if cres is not None:
                self._callback_add_llvm_timer(dur, cres)
        scope.enter_context(ev.install_timer('numba:compiler_lock',
            cb_compiler))
        scope.enter_context(ev.install_timer('numba:llvm_lock', cb_llvm))
        scope.enter_context(global_compiler_lock)
        with self._compiling_counter:
            flags = self.flags
            args, return_type = sigutils.normalize_signature(sig)
            jkn__nsyts = self.overloads.get(tuple(args))
            if jkn__nsyts is not None:
                return jkn__nsyts.entry_point
            self._pre_compile(args, return_type, flags)
            vhvnx__mqkr = self.func_ir
            fvjty__ghix = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=fvjty__ghix):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=vhvnx__mqkr, args=
                    args, return_type=return_type, flags=flags, locals=self
                    .locals, lifted=(), lifted_from=self.lifted_from,
                    is_lifted_loop=True)
                if cres.typing_error is not None and not flags.enable_pyobject:
                    raise cres.typing_error
                self.add_overload(cres)
            remove_dels(self.func_ir.blocks)
            return cres.entry_point


if _check_numba_change:
    lines = inspect.getsource(numba.core.dispatcher.LiftedCode.compile)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '1351ebc5d8812dc8da167b30dad30eafb2ca9bf191b49aaed6241c21e03afff1':
        warnings.warn('numba.core.dispatcher.LiftedCode.compile has changed')
numba.core.dispatcher.LiftedCode.compile = _lifted_compile


def compile_ir(typingctx, targetctx, func_ir, args, return_type, flags,
    locals, lifted=(), lifted_from=None, is_lifted_loop=False, library=None,
    pipeline_class=Compiler):
    if is_lifted_loop:
        okdy__gyq = copy.deepcopy(flags)
        okdy__gyq.no_rewrites = True

        def compile_local(the_ir, the_flags):
            cvb__xdm = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return cvb__xdm.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        fvd__drt = compile_local(func_ir, okdy__gyq)
        ejorv__qlp = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    ejorv__qlp = compile_local(func_ir, flags)
                except Exception as akd__qnxd:
                    pass
        if ejorv__qlp is not None:
            cres = ejorv__qlp
        else:
            cres = fvd__drt
        return cres
    else:
        cvb__xdm = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return cvb__xdm.compile_ir(func_ir=func_ir, lifted=lifted,
            lifted_from=lifted_from)


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.compile_ir)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c48ce5493f4c43326e8cbdd46f3ea038b2b9045352d9d25894244798388e5e5b':
        warnings.warn('numba.core.compiler.compile_ir has changed')
numba.core.compiler.compile_ir = compile_ir


def make_constant_array(self, builder, typ, ary):
    import math
    from llvmlite import ir as lir
    ejfo__stup = self.get_data_type(typ.dtype)
    wfw__inv = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        wfw__inv):
        xmag__dkpjn = ary.ctypes.data
        puly__hwsc = self.add_dynamic_addr(builder, xmag__dkpjn, info=str(
            type(xmag__dkpjn)))
        alkpm__mwzl = self.add_dynamic_addr(builder, id(ary), info=str(type
            (ary)))
        self.global_arrays.append(ary)
    else:
        atjn__ivqzw = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            atjn__ivqzw = atjn__ivqzw.view('int64')
        val = bytearray(atjn__ivqzw.data)
        usu__gph = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val)
        puly__hwsc = cgutils.global_constant(builder, '.const.array.data',
            usu__gph)
        puly__hwsc.align = self.get_abi_alignment(ejfo__stup)
        alkpm__mwzl = None
    jupq__igbvd = self.get_value_type(types.intp)
    yelhj__hagl = [self.get_constant(types.intp, ngsmv__xza) for ngsmv__xza in
        ary.shape]
    tkdb__iotuz = lir.Constant(lir.ArrayType(jupq__igbvd, len(yelhj__hagl)),
        yelhj__hagl)
    aelzf__acj = [self.get_constant(types.intp, ngsmv__xza) for ngsmv__xza in
        ary.strides]
    zwh__fnja = lir.Constant(lir.ArrayType(jupq__igbvd, len(aelzf__acj)),
        aelzf__acj)
    dhxli__sdt = self.get_constant(types.intp, ary.dtype.itemsize)
    iber__vjy = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        iber__vjy, dhxli__sdt, puly__hwsc.bitcast(self.get_value_type(types
        .CPointer(typ.dtype))), tkdb__iotuz, zwh__fnja])


if _check_numba_change:
    lines = inspect.getsource(numba.core.base.BaseContext.make_constant_array)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5721b5360b51f782f79bd794f7bf4d48657911ecdc05c30db22fd55f15dad821':
        warnings.warn(
            'numba.core.base.BaseContext.make_constant_array has changed')
numba.core.base.BaseContext.make_constant_array = make_constant_array


def _define_atomic_inc_dec(module, op, ordering):
    from llvmlite import ir as lir
    from numba.core.runtime.nrtdynmod import _word_type
    nodwq__chtha = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    rms__qimeg = lir.Function(module, nodwq__chtha, name='nrt_atomic_{0}'.
        format(op))
    [rtxf__kofap] = rms__qimeg.args
    mbhce__uir = rms__qimeg.append_basic_block()
    builder = lir.IRBuilder(mbhce__uir)
    kxlj__jzwjy = lir.Constant(_word_type, 1)
    if False:
        hjqcn__cua = builder.atomic_rmw(op, rtxf__kofap, kxlj__jzwjy,
            ordering=ordering)
        res = getattr(builder, op)(hjqcn__cua, kxlj__jzwjy)
        builder.ret(res)
    else:
        hjqcn__cua = builder.load(rtxf__kofap)
        nmxr__bljcg = getattr(builder, op)(hjqcn__cua, kxlj__jzwjy)
        ohc__wmj = builder.icmp_signed('!=', hjqcn__cua, lir.Constant(
            hjqcn__cua.type, -1))
        with cgutils.if_likely(builder, ohc__wmj):
            builder.store(nmxr__bljcg, rtxf__kofap)
        builder.ret(nmxr__bljcg)
    return rms__qimeg


if _check_numba_change:
    lines = inspect.getsource(numba.core.runtime.nrtdynmod.
        _define_atomic_inc_dec)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '9cc02c532b2980b6537b702f5608ea603a1ff93c6d3c785ae2cf48bace273f48':
        warnings.warn(
            'numba.core.runtime.nrtdynmod._define_atomic_inc_dec has changed')
numba.core.runtime.nrtdynmod._define_atomic_inc_dec = _define_atomic_inc_dec


def NativeLowering_run_pass(self, state):
    from llvmlite import binding as llvm
    from numba.core import funcdesc, lowering
    from numba.core.typed_passes import fallback_context
    if state.library is None:
        baiyy__gad = state.targetctx.codegen()
        state.library = baiyy__gad.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    beet__hzkcf = state.func_ir
    typemap = state.typemap
    crfi__usvgl = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    dobda__tknv = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            beet__hzkcf, typemap, crfi__usvgl, calltypes, mangler=targetctx
            .mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            upn__vvr = lowering.Lower(targetctx, library, fndesc,
                beet__hzkcf, metadata=metadata)
            upn__vvr.lower()
            if not flags.no_cpython_wrapper:
                upn__vvr.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(crfi__usvgl, (types.Optional, types.
                        Generator)):
                        pass
                    else:
                        upn__vvr.create_cfunc_wrapper()
            env = upn__vvr.env
            aesu__lihh = upn__vvr.call_helper
            del upn__vvr
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, aesu__lihh, cfunc=None, env=env)
        else:
            bpn__efb = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(bpn__efb, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, aesu__lihh, cfunc=bpn__efb,
                env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        vvy__vzgxq = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = vvy__vzgxq - dobda__tknv
        metadata['llvm_pass_timings'] = library.recorded_timings
    return True


if _check_numba_change:
    lines = inspect.getsource(numba.core.typed_passes.NativeLowering.run_pass)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a777ce6ce1bb2b1cbaa3ac6c2c0e2adab69a9c23888dff5f1cbb67bfb176b5de':
        warnings.warn(
            'numba.core.typed_passes.NativeLowering.run_pass has changed')
numba.core.typed_passes.NativeLowering.run_pass = NativeLowering_run_pass


def _python_list_to_native(typ, obj, c, size, listptr, errorptr):
    from llvmlite import ir as lir
    from numba.core.boxing import _NumbaTypeHelper
    from numba.cpython import listobj

    def check_element_type(nth, itemobj, expected_typobj):
        zrczs__ipl = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, zrczs__ipl),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            uzfz__ecmry.do_break()
        ldzsv__jyx = c.builder.icmp_signed('!=', zrczs__ipl, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(ldzsv__jyx, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, zrczs__ipl)
                c.pyapi.decref(zrczs__ipl)
                uzfz__ecmry.do_break()
        c.pyapi.decref(zrczs__ipl)
    mlc__ansnx, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(mlc__ansnx, likely=True) as (ipagx__ajh, gzsqt__eevv
        ):
        with ipagx__ajh:
            list.size = size
            joiej__mij = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                joiej__mij), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        joiej__mij))
                    with cgutils.for_range(c.builder, size) as uzfz__ecmry:
                        itemobj = c.pyapi.list_getitem(obj, uzfz__ecmry.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        inf__hhdhn = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(inf__hhdhn.is_error, likely=
                            False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            uzfz__ecmry.do_break()
                        list.setitem(uzfz__ecmry.index, inf__hhdhn.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with gzsqt__eevv:
            c.builder.store(cgutils.true_bit, errorptr)
    with c.builder.if_then(c.builder.load(errorptr)):
        c.context.nrt.decref(c.builder, typ, list.value)


if _check_numba_change:
    lines = inspect.getsource(numba.core.boxing._python_list_to_native)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f8e546df8b07adfe74a16b6aafb1d4fddbae7d3516d7944b3247cc7c9b7ea88a':
        warnings.warn('numba.core.boxing._python_list_to_native has changed')
numba.core.boxing._python_list_to_native = _python_list_to_native


def make_string_from_constant(context, builder, typ, literal_string):
    from llvmlite import ir as lir
    from numba.cpython.hashing import _Py_hash_t
    from numba.cpython.unicode import compile_time_get_string_data
    qclf__zttlm, jzus__ammp, redyd__lly, vlb__nyqv, ukylm__lov = (
        compile_time_get_string_data(literal_string))
    mtqk__lnu = builder.module
    gv = context.insert_const_bytes(mtqk__lnu, qclf__zttlm)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        jzus__ammp), context.get_constant(types.int32, redyd__lly), context
        .get_constant(types.uint32, vlb__nyqv), context.get_constant(
        _Py_hash_t, -1), context.get_constant_null(types.MemInfoPointer(
        types.voidptr)), context.get_constant_null(types.pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    isztt__smyoz = None
    if isinstance(shape, types.Integer):
        isztt__smyoz = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(ngsmv__xza, (types.Integer, types.IntEnumMember)) for
            ngsmv__xza in shape):
            isztt__smyoz = len(shape)
    return isztt__smyoz


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.npydecl.parse_shape)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'e62e3ff09d36df5ac9374055947d6a8be27160ce32960d3ef6cb67f89bd16429':
        warnings.warn('numba.core.typing.npydecl.parse_shape has changed')
numba.core.typing.npydecl.parse_shape = parse_shape


def _get_names(self, obj):
    if isinstance(obj, ir.Var) or isinstance(obj, str):
        name = obj if isinstance(obj, str) else obj.name
        if name not in self.typemap:
            return name,
        typ = self.typemap[name]
        if isinstance(typ, (types.BaseTuple, types.ArrayCompatible)):
            isztt__smyoz = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if isztt__smyoz == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(
                    isztt__smyoz))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            vgojq__sjtp = self._get_names(x)
            if len(vgojq__sjtp) != 0:
                return vgojq__sjtp[0]
            return vgojq__sjtp
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    vgojq__sjtp = self._get_names(obj)
    if len(vgojq__sjtp) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(vgojq__sjtp[0])


def get_equiv_set(self, obj):
    vgojq__sjtp = self._get_names(obj)
    if len(vgojq__sjtp) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(vgojq__sjtp[0])


if _check_numba_change:
    for name, orig, new, hash in ((
        'numba.parfors.array_analysis.ShapeEquivSet._get_names', numba.
        parfors.array_analysis.ShapeEquivSet._get_names, _get_names,
        '8c9bf136109028d5445fd0a82387b6abeb70c23b20b41e2b50c34ba5359516ee'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const',
        numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const,
        get_equiv_const,
        'bef410ca31a9e29df9ee74a4a27d339cc332564e4a237828b8a4decf625ce44e'),
        ('numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set', numba.
        parfors.array_analysis.ShapeEquivSet.get_equiv_set, get_equiv_set,
        'ec936d340c488461122eb74f28a28b88227cb1f1bca2b9ba3c19258cfe1eb40a')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
numba.parfors.array_analysis.ShapeEquivSet._get_names = _get_names
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_const = get_equiv_const
numba.parfors.array_analysis.ShapeEquivSet.get_equiv_set = get_equiv_set


def raise_on_unsupported_feature(func_ir, typemap):
    import numpy
    dqnw__bgeu = []
    for ejds__ayt in func_ir.arg_names:
        if ejds__ayt in typemap and isinstance(typemap[ejds__ayt], types.
            containers.UniTuple) and typemap[ejds__ayt].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(ejds__ayt))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for ikef__kplc in func_ir.blocks.values():
        for stmt in ikef__kplc.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    pos__hdg = getattr(val, 'code', None)
                    if pos__hdg is not None:
                        if getattr(val, 'closure', None) is not None:
                            krraa__xlu = '<creating a function from a closure>'
                            vdgze__vys = ''
                        else:
                            krraa__xlu = pos__hdg.co_name
                            vdgze__vys = '(%s) ' % krraa__xlu
                    else:
                        krraa__xlu = '<could not ascertain use case>'
                        vdgze__vys = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (krraa__xlu, vdgze__vys))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                rlx__zocq = False
                if isinstance(val, pytypes.FunctionType):
                    rlx__zocq = val in {numba.gdb, numba.gdb_init}
                if not rlx__zocq:
                    rlx__zocq = getattr(val, '_name', '') == 'gdb_internal'
                if rlx__zocq:
                    dqnw__bgeu.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    bwn__pabf = func_ir.get_definition(var)
                    clc__wyh = guard(find_callname, func_ir, bwn__pabf)
                    if clc__wyh and clc__wyh[1] == 'numpy':
                        ty = getattr(numpy, clc__wyh[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    eitiq__zit = '' if var.startswith('$') else "'{}' ".format(
                        var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(eitiq__zit), loc=stmt.loc)
            if isinstance(stmt.value, ir.Global):
                ty = typemap[stmt.target.name]
                msg = (
                    "The use of a %s type, assigned to variable '%s' in globals, is not supported as globals are considered compile-time constants and there is no known way to compile a %s type as a constant."
                    )
                if isinstance(ty, types.ListType):
                    raise TypingError(msg % (ty, stmt.value.name, ty), loc=
                        stmt.loc)
            if isinstance(stmt.value, ir.Yield) and not func_ir.is_generator:
                msg = 'The use of generator expressions is unsupported.'
                raise errors.UnsupportedError(msg, loc=stmt.loc)
    if len(dqnw__bgeu) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        dpf__bygh = '\n'.join([x.strformat() for x in dqnw__bgeu])
        raise errors.UnsupportedError(msg % dpf__bygh)


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.raise_on_unsupported_feature)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '237a4fe8395a40899279c718bc3754102cd2577463ef2f48daceea78d79b2d5e':
        warnings.warn(
            'numba.core.ir_utils.raise_on_unsupported_feature has changed')
numba.core.ir_utils.raise_on_unsupported_feature = raise_on_unsupported_feature
numba.core.typed_passes.raise_on_unsupported_feature = (
    raise_on_unsupported_feature)


@typeof_impl.register(dict)
def _typeof_dict(val, c):
    if len(val) == 0:
        raise ValueError('Cannot type empty dict')
    nuhbj__lgudm, cznz__nkdti = next(iter(val.items()))
    iqaxi__wnd = typeof_impl(nuhbj__lgudm, c)
    vfbkf__pvya = typeof_impl(cznz__nkdti, c)
    if iqaxi__wnd is None or vfbkf__pvya is None:
        raise ValueError(
            f'Cannot type dict element type {type(nuhbj__lgudm)}, {type(cznz__nkdti)}'
            )
    return types.DictType(iqaxi__wnd, vfbkf__pvya)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    yfbf__kaygp = cgutils.alloca_once_value(c.builder, val)
    ary__kni = c.pyapi.object_hasattr_string(val, '_opaque')
    xxx__emhh = c.builder.icmp_unsigned('==', ary__kni, lir.Constant(
        ary__kni.type, 0))
    igv__yyad = typ.key_type
    gpkwg__wze = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(igv__yyad, gpkwg__wze)

    def copy_dict(out_dict, in_dict):
        for nuhbj__lgudm, cznz__nkdti in in_dict.items():
            out_dict[nuhbj__lgudm] = cznz__nkdti
    with c.builder.if_then(xxx__emhh):
        haaj__xjzf = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        ggazj__hdmwy = c.pyapi.call_function_objargs(haaj__xjzf, [])
        jtlh__mzlsg = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(jtlh__mzlsg, [ggazj__hdmwy, val])
        c.builder.store(ggazj__hdmwy, yfbf__kaygp)
    val = c.builder.load(yfbf__kaygp)
    psux__tumr = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    mfk__uryo = c.pyapi.object_type(val)
    gfvyn__cmc = c.builder.icmp_unsigned('==', mfk__uryo, psux__tumr)
    with c.builder.if_else(gfvyn__cmc) as (mnyo__qfxrl, dveg__acoi):
        with mnyo__qfxrl:
            mgwxn__zazcg = c.pyapi.object_getattr_string(val, '_opaque')
            nvel__eal = types.MemInfoPointer(types.voidptr)
            inf__hhdhn = c.unbox(nvel__eal, mgwxn__zazcg)
            mi = inf__hhdhn.value
            qtnsl__nilcf = nvel__eal, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *qtnsl__nilcf)
            nwr__lbvvi = context.get_constant_null(qtnsl__nilcf[1])
            args = mi, nwr__lbvvi
            nycwg__juwf, zeuf__kwzy = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, zeuf__kwzy)
            c.pyapi.decref(mgwxn__zazcg)
            vge__ojwr = c.builder.basic_block
        with dveg__acoi:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", mfk__uryo, psux__tumr)
            qqzsi__pqq = c.builder.basic_block
    lkn__otxzk = c.builder.phi(zeuf__kwzy.type)
    bob__dniml = c.builder.phi(nycwg__juwf.type)
    lkn__otxzk.add_incoming(zeuf__kwzy, vge__ojwr)
    lkn__otxzk.add_incoming(zeuf__kwzy.type(None), qqzsi__pqq)
    bob__dniml.add_incoming(nycwg__juwf, vge__ojwr)
    bob__dniml.add_incoming(cgutils.true_bit, qqzsi__pqq)
    c.pyapi.decref(psux__tumr)
    c.pyapi.decref(mfk__uryo)
    with c.builder.if_then(xxx__emhh):
        c.pyapi.decref(val)
    return NativeValue(lkn__otxzk, is_error=bob__dniml)


import numba.typed.typeddict
if _check_numba_change:
    lines = inspect.getsource(numba.core.pythonapi._unboxers.functions[
        numba.core.types.DictType])
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '5f6f183b94dc57838538c668a54c2476576c85d8553843f3219f5162c61e7816':
        warnings.warn('unbox_dicttype has changed')
numba.core.pythonapi._unboxers.functions[types.DictType] = unbox_dicttype


def op_DICT_UPDATE_byteflow(self, state, inst):
    value = state.pop()
    index = inst.arg
    target = state.peek(index)
    updatevar = state.make_temp()
    res = state.make_temp()
    state.append(inst, target=target, value=value, updatevar=updatevar, res=res
        )


if _check_numba_change:
    if hasattr(numba.core.byteflow.TraceRunner, 'op_DICT_UPDATE'):
        warnings.warn(
            'numba.core.byteflow.TraceRunner.op_DICT_UPDATE has changed')
numba.core.byteflow.TraceRunner.op_DICT_UPDATE = op_DICT_UPDATE_byteflow


def op_DICT_UPDATE_interpreter(self, inst, target, value, updatevar, res):
    from numba.core import ir
    target = self.get(target)
    value = self.get(value)
    miec__ufv = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=miec__ufv, name=updatevar)
    jpzvx__ylao = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=jpzvx__ylao, name=res)


if _check_numba_change:
    if hasattr(numba.core.interpreter.Interpreter, 'op_DICT_UPDATE'):
        warnings.warn(
            'numba.core.interpreter.Interpreter.op_DICT_UPDATE has changed')
numba.core.interpreter.Interpreter.op_DICT_UPDATE = op_DICT_UPDATE_interpreter


@numba.extending.overload_method(numba.core.types.DictType, 'update')
def ol_dict_update(d, other):
    if not isinstance(d, numba.core.types.DictType):
        return
    if not isinstance(other, numba.core.types.DictType):
        return

    def impl(d, other):
        for nuhbj__lgudm, cznz__nkdti in other.items():
            d[nuhbj__lgudm] = cznz__nkdti
    return impl


if _check_numba_change:
    if hasattr(numba.core.interpreter.Interpreter, 'ol_dict_update'):
        warnings.warn('numba.typed.dictobject.ol_dict_update has changed')


def op_CALL_FUNCTION_EX_byteflow(self, state, inst):
    from numba.core.utils import PYVERSION
    if inst.arg & 1 and PYVERSION != (3, 10):
        errmsg = 'CALL_FUNCTION_EX with **kwargs not supported'
        raise errors.UnsupportedError(errmsg)
    if inst.arg & 1:
        varkwarg = state.pop()
    else:
        varkwarg = None
    vararg = state.pop()
    func = state.pop()
    res = state.make_temp()
    state.append(inst, func=func, vararg=vararg, varkwarg=varkwarg, res=res)
    state.push(res)


if _check_numba_change:
    lines = inspect.getsource(numba.core.byteflow.TraceRunner.
        op_CALL_FUNCTION_EX)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '349e7cfd27f5dab80fe15a7728c5f098f3f225ba8512d84331e39d01e863c6d4':
        warnings.warn(
            'numba.core.byteflow.TraceRunner.op_CALL_FUNCTION_EX has changed')
numba.core.byteflow.TraceRunner.op_CALL_FUNCTION_EX = (
    op_CALL_FUNCTION_EX_byteflow)


def op_CALL_FUNCTION_EX_interpreter(self, inst, func, vararg, varkwarg, res):
    func = self.get(func)
    vararg = self.get(vararg)
    if varkwarg is not None:
        varkwarg = self.get(varkwarg)
    vdgze__vys = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(vdgze__vys, res)


if _check_numba_change:
    lines = inspect.getsource(numba.core.interpreter.Interpreter.
        op_CALL_FUNCTION_EX)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '84846e5318ab7ccc8f9abaae6ab9e0ca879362648196f9d4b0ffb91cf2e01f5d':
        warnings.warn(
            'numba.core.interpreter.Interpreter.op_CALL_FUNCTION_EX has changed'
            )
numba.core.interpreter.Interpreter.op_CALL_FUNCTION_EX = (
    op_CALL_FUNCTION_EX_interpreter)


@classmethod
def ir_expr_call(cls, func, args, kws, loc, vararg=None, varkwarg=None,
    target=None):
    assert isinstance(func, ir.Var)
    assert isinstance(loc, ir.Loc)
    op = 'call'
    return cls(op=op, loc=loc, func=func, args=args, kws=kws, vararg=vararg,
        varkwarg=varkwarg, target=target)


if _check_numba_change:
    lines = inspect.getsource(ir.Expr.call)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '665601d0548d4f648d454492e542cb8aa241107a8df6bc68d0eec664c9ada738':
        warnings.warn('ir.Expr.call has changed')
ir.Expr.call = ir_expr_call


@staticmethod
def define_untyped_pipeline(state, name='untyped'):
    from numba.core.compiler_machinery import PassManager
    from numba.core.untyped_passes import DeadBranchPrune, FindLiterallyCalls, FixupArgs, GenericRewrites, InlineClosureLikes, InlineInlinables, IRProcessing, LiteralPropagationSubPipelinePass, LiteralUnroll, MakeFunctionToJitFunction, ReconstructSSA, RewriteSemanticConstants, TranslateByteCode, WithLifting
    from numba.core.utils import PYVERSION
    xqg__uie = PassManager(name)
    if state.func_ir is None:
        xqg__uie.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            xqg__uie.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        xqg__uie.add_pass(FixupArgs, 'fix up args')
    xqg__uie.add_pass(IRProcessing, 'processing IR')
    xqg__uie.add_pass(WithLifting, 'Handle with contexts')
    xqg__uie.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        xqg__uie.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        xqg__uie.add_pass(DeadBranchPrune, 'dead branch pruning')
        xqg__uie.add_pass(GenericRewrites, 'nopython rewrites')
    xqg__uie.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    xqg__uie.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        xqg__uie.add_pass(DeadBranchPrune, 'dead branch pruning')
    xqg__uie.add_pass(FindLiterallyCalls, 'find literally calls')
    xqg__uie.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        xqg__uie.add_pass(ReconstructSSA, 'ssa')
    xqg__uie.add_pass(LiteralPropagationSubPipelinePass, 'Literal propagation')
    xqg__uie.finalize()
    return xqg__uie


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'fc5a0665658cc30588a78aca984ac2d323d5d3a45dce538cc62688530c772896':
        warnings.warn(
            'numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline has changed'
            )
numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline = (
    define_untyped_pipeline)


def mul_list_generic(self, args, kws):
    a, tiiqg__fzurs = args
    if isinstance(a, types.List) and isinstance(tiiqg__fzurs, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(tiiqg__fzurs, types.List):
        return signature(tiiqg__fzurs, types.intp, tiiqg__fzurs)


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.listdecl.MulList.generic)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '95882385a8ffa67aa576e8169b9ee6b3197e0ad3d5def4b47fa65ce8cd0f1575':
        warnings.warn('numba.core.typing.listdecl.MulList.generic has changed')
numba.core.typing.listdecl.MulList.generic = mul_list_generic


@lower_builtin(operator.mul, types.Integer, types.List)
def list_mul(context, builder, sig, args):
    from llvmlite import ir as lir
    from numba.core.imputils import impl_ret_new_ref
    from numba.cpython.listobj import ListInstance
    if isinstance(sig.args[0], types.List):
        xcn__vvii, vwtg__fckzv = 0, 1
    else:
        xcn__vvii, vwtg__fckzv = 1, 0
    qls__hhho = ListInstance(context, builder, sig.args[xcn__vvii], args[
        xcn__vvii])
    xnpj__wok = qls__hhho.size
    eirao__osurh = args[vwtg__fckzv]
    joiej__mij = lir.Constant(eirao__osurh.type, 0)
    eirao__osurh = builder.select(cgutils.is_neg_int(builder, eirao__osurh),
        joiej__mij, eirao__osurh)
    iber__vjy = builder.mul(eirao__osurh, xnpj__wok)
    ehe__whnv = ListInstance.allocate(context, builder, sig.return_type,
        iber__vjy)
    ehe__whnv.size = iber__vjy
    with cgutils.for_range_slice(builder, joiej__mij, iber__vjy, xnpj__wok,
        inc=True) as (vgm__mlqej, _):
        with cgutils.for_range(builder, xnpj__wok) as uzfz__ecmry:
            value = qls__hhho.getitem(uzfz__ecmry.index)
            ehe__whnv.setitem(builder.add(uzfz__ecmry.index, vgm__mlqej),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, ehe__whnv.value)


def unify_pairs(self, first, second):
    from numba.core.typeconv import Conversion
    if first == second:
        return first
    if first is types.undefined:
        return second
    elif second is types.undefined:
        return first
    if first is types.unknown or second is types.unknown:
        return types.unknown
    mcwj__psv = first.unify(self, second)
    if mcwj__psv is not None:
        return mcwj__psv
    mcwj__psv = second.unify(self, first)
    if mcwj__psv is not None:
        return mcwj__psv
    xnjzb__gdd = self.can_convert(fromty=first, toty=second)
    if xnjzb__gdd is not None and xnjzb__gdd <= Conversion.safe:
        return second
    xnjzb__gdd = self.can_convert(fromty=second, toty=first)
    if xnjzb__gdd is not None and xnjzb__gdd <= Conversion.safe:
        return first
    if isinstance(first, types.Literal) or isinstance(second, types.Literal):
        first = types.unliteral(first)
        second = types.unliteral(second)
        return self.unify_pairs(first, second)
    return None


if _check_numba_change:
    lines = inspect.getsource(numba.core.typing.context.BaseContext.unify_pairs
        )
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'f0eaf4cfdf1537691de26efd24d7e320f7c3f10d35e9aefe70cb946b3be0008c':
        warnings.warn(
            'numba.core.typing.context.BaseContext.unify_pairs has changed')
numba.core.typing.context.BaseContext.unify_pairs = unify_pairs


def _native_set_to_python_list(typ, payload, c):
    from llvmlite import ir
    iber__vjy = payload.used
    listobj = c.pyapi.list_new(iber__vjy)
    mlc__ansnx = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(mlc__ansnx, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(iber__vjy.
            type, 0))
        with payload._iterate() as uzfz__ecmry:
            i = c.builder.load(index)
            item = uzfz__ecmry.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return mlc__ansnx, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    ihsp__fzeem = h.type
    fbk__npxkz = self.mask
    dtype = self._ty.dtype
    pkob__govhu = context.typing_context
    fnty = pkob__govhu.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(pkob__govhu, (dtype, dtype), {})
    mgjb__bcf = context.get_function(fnty, sig)
    udxch__ylhdn = ir.Constant(ihsp__fzeem, 1)
    dlq__auvp = ir.Constant(ihsp__fzeem, 5)
    qzmrb__bpx = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, fbk__npxkz))
    if for_insert:
        dll__cpit = fbk__npxkz.type(-1)
        xme__vayeh = cgutils.alloca_once_value(builder, dll__cpit)
    mzemi__dfvc = builder.append_basic_block('lookup.body')
    vpst__mgb = builder.append_basic_block('lookup.found')
    paeil__lyzi = builder.append_basic_block('lookup.not_found')
    zdyu__lnhkb = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        mtpk__ezr = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, mtpk__ezr)):
            ywd__ybuj = mgjb__bcf(builder, (item, entry.key))
            with builder.if_then(ywd__ybuj):
                builder.branch(vpst__mgb)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, mtpk__ezr)):
            builder.branch(paeil__lyzi)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, mtpk__ezr)):
                djou__hvg = builder.load(xme__vayeh)
                djou__hvg = builder.select(builder.icmp_unsigned('==',
                    djou__hvg, dll__cpit), i, djou__hvg)
                builder.store(djou__hvg, xme__vayeh)
    with cgutils.for_range(builder, ir.Constant(ihsp__fzeem, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, udxch__ylhdn)
        i = builder.and_(i, fbk__npxkz)
        builder.store(i, index)
    builder.branch(mzemi__dfvc)
    with builder.goto_block(mzemi__dfvc):
        i = builder.load(index)
        check_entry(i)
        wqu__tklwk = builder.load(qzmrb__bpx)
        wqu__tklwk = builder.lshr(wqu__tklwk, dlq__auvp)
        i = builder.add(udxch__ylhdn, builder.mul(i, dlq__auvp))
        i = builder.and_(fbk__npxkz, builder.add(i, wqu__tklwk))
        builder.store(i, index)
        builder.store(wqu__tklwk, qzmrb__bpx)
        builder.branch(mzemi__dfvc)
    with builder.goto_block(paeil__lyzi):
        if for_insert:
            i = builder.load(index)
            djou__hvg = builder.load(xme__vayeh)
            i = builder.select(builder.icmp_unsigned('==', djou__hvg,
                dll__cpit), i, djou__hvg)
            builder.store(i, index)
        builder.branch(zdyu__lnhkb)
    with builder.goto_block(vpst__mgb):
        builder.branch(zdyu__lnhkb)
    builder.position_at_end(zdyu__lnhkb)
    rlx__zocq = builder.phi(ir.IntType(1), 'found')
    rlx__zocq.add_incoming(cgutils.true_bit, vpst__mgb)
    rlx__zocq.add_incoming(cgutils.false_bit, paeil__lyzi)
    return rlx__zocq, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    jak__idoq = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    bdj__bkl = payload.used
    udxch__ylhdn = ir.Constant(bdj__bkl.type, 1)
    bdj__bkl = payload.used = builder.add(bdj__bkl, udxch__ylhdn)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, jak__idoq), likely=True):
        payload.fill = builder.add(payload.fill, udxch__ylhdn)
    if do_resize:
        self.upsize(bdj__bkl)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    rlx__zocq, i = payload._lookup(item, h, for_insert=True)
    rdpfa__rcjj = builder.not_(rlx__zocq)
    with builder.if_then(rdpfa__rcjj):
        entry = payload.get_entry(i)
        jak__idoq = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        bdj__bkl = payload.used
        udxch__ylhdn = ir.Constant(bdj__bkl.type, 1)
        bdj__bkl = payload.used = builder.add(bdj__bkl, udxch__ylhdn)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, jak__idoq), likely=True):
            payload.fill = builder.add(payload.fill, udxch__ylhdn)
        if do_resize:
            self.upsize(bdj__bkl)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    bdj__bkl = payload.used
    udxch__ylhdn = ir.Constant(bdj__bkl.type, 1)
    bdj__bkl = payload.used = self._builder.sub(bdj__bkl, udxch__ylhdn)
    if do_resize:
        self.downsize(bdj__bkl)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    ctg__zudd = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, ctg__zudd)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    udmtl__sgwp = payload
    mlc__ansnx = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(mlc__ansnx), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with udmtl__sgwp._iterate() as uzfz__ecmry:
        entry = uzfz__ecmry.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(udmtl__sgwp.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as uzfz__ecmry:
        entry = uzfz__ecmry.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    mlc__ansnx = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(mlc__ansnx), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    mlc__ansnx = cgutils.alloca_once_value(builder, cgutils.true_bit)
    ihsp__fzeem = context.get_value_type(types.intp)
    joiej__mij = ir.Constant(ihsp__fzeem, 0)
    udxch__ylhdn = ir.Constant(ihsp__fzeem, 1)
    bre__qbggo = context.get_data_type(types.SetPayload(self._ty))
    ledc__didqv = context.get_abi_sizeof(bre__qbggo)
    rwpq__wdh = self._entrysize
    ledc__didqv -= rwpq__wdh
    zgs__vttf, uors__giio = cgutils.muladd_with_overflow(builder, nentries,
        ir.Constant(ihsp__fzeem, rwpq__wdh), ir.Constant(ihsp__fzeem,
        ledc__didqv))
    with builder.if_then(uors__giio, likely=False):
        builder.store(cgutils.false_bit, mlc__ansnx)
    with builder.if_then(builder.load(mlc__ansnx), likely=True):
        if realloc:
            ormgn__wshm = self._set.meminfo
            rtxf__kofap = context.nrt.meminfo_varsize_alloc(builder,
                ormgn__wshm, size=zgs__vttf)
            bvwf__ewhng = cgutils.is_null(builder, rtxf__kofap)
        else:
            ebuo__avqqy = _imp_dtor(context, builder.module, self._ty)
            ormgn__wshm = context.nrt.meminfo_new_varsize_dtor(builder,
                zgs__vttf, builder.bitcast(ebuo__avqqy, cgutils.voidptr_t))
            bvwf__ewhng = cgutils.is_null(builder, ormgn__wshm)
        with builder.if_else(bvwf__ewhng, likely=False) as (msnq__zly,
            ipagx__ajh):
            with msnq__zly:
                builder.store(cgutils.false_bit, mlc__ansnx)
            with ipagx__ajh:
                if not realloc:
                    self._set.meminfo = ormgn__wshm
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, zgs__vttf, 255)
                payload.used = joiej__mij
                payload.fill = joiej__mij
                payload.finger = joiej__mij
                iay__rbhuj = builder.sub(nentries, udxch__ylhdn)
                payload.mask = iay__rbhuj
    return builder.load(mlc__ansnx)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    mlc__ansnx = cgutils.alloca_once_value(builder, cgutils.true_bit)
    ihsp__fzeem = context.get_value_type(types.intp)
    joiej__mij = ir.Constant(ihsp__fzeem, 0)
    udxch__ylhdn = ir.Constant(ihsp__fzeem, 1)
    bre__qbggo = context.get_data_type(types.SetPayload(self._ty))
    ledc__didqv = context.get_abi_sizeof(bre__qbggo)
    rwpq__wdh = self._entrysize
    ledc__didqv -= rwpq__wdh
    fbk__npxkz = src_payload.mask
    nentries = builder.add(udxch__ylhdn, fbk__npxkz)
    zgs__vttf = builder.add(ir.Constant(ihsp__fzeem, ledc__didqv), builder.
        mul(ir.Constant(ihsp__fzeem, rwpq__wdh), nentries))
    with builder.if_then(builder.load(mlc__ansnx), likely=True):
        ebuo__avqqy = _imp_dtor(context, builder.module, self._ty)
        ormgn__wshm = context.nrt.meminfo_new_varsize_dtor(builder,
            zgs__vttf, builder.bitcast(ebuo__avqqy, cgutils.voidptr_t))
        bvwf__ewhng = cgutils.is_null(builder, ormgn__wshm)
        with builder.if_else(bvwf__ewhng, likely=False) as (msnq__zly,
            ipagx__ajh):
            with msnq__zly:
                builder.store(cgutils.false_bit, mlc__ansnx)
            with ipagx__ajh:
                self._set.meminfo = ormgn__wshm
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = joiej__mij
                payload.mask = fbk__npxkz
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, rwpq__wdh)
                with src_payload._iterate() as uzfz__ecmry:
                    context.nrt.incref(builder, self._ty.dtype, uzfz__ecmry
                        .entry.key)
    return builder.load(mlc__ansnx)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    nog__opdl = context.get_value_type(types.voidptr)
    wqz__eczkc = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [nog__opdl, wqz__eczkc, nog__opdl])
    abxmr__whzja = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=abxmr__whzja)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        ppg__mrasp = builder.bitcast(fn.args[0], cgutils.voidptr_t.as_pointer()
            )
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, ppg__mrasp)
        with payload._iterate() as uzfz__ecmry:
            entry = uzfz__ecmry.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    hevv__fbtj, = sig.args
    hntw__pafcl, = args
    ljpax__gls = numba.core.imputils.call_len(context, builder, hevv__fbtj,
        hntw__pafcl)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, ljpax__gls)
    with numba.core.imputils.for_iter(context, builder, hevv__fbtj, hntw__pafcl
        ) as uzfz__ecmry:
        inst.add(uzfz__ecmry.value)
        context.nrt.decref(builder, set_type.dtype, uzfz__ecmry.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    hevv__fbtj = sig.args[1]
    hntw__pafcl = args[1]
    ljpax__gls = numba.core.imputils.call_len(context, builder, hevv__fbtj,
        hntw__pafcl)
    if ljpax__gls is not None:
        rlmtp__ylx = builder.add(inst.payload.used, ljpax__gls)
        inst.upsize(rlmtp__ylx)
    with numba.core.imputils.for_iter(context, builder, hevv__fbtj, hntw__pafcl
        ) as uzfz__ecmry:
        drxx__ewfg = context.cast(builder, uzfz__ecmry.value, hevv__fbtj.
            dtype, inst.dtype)
        inst.add(drxx__ewfg)
        context.nrt.decref(builder, hevv__fbtj.dtype, uzfz__ecmry.value)
    if ljpax__gls is not None:
        inst.downsize(inst.payload.used)
    return context.get_dummy_value()


if _check_numba_change:
    for name, orig, hash in ((
        'numba.core.boxing._native_set_to_python_list', numba.core.boxing.
        _native_set_to_python_list,
        'b47f3d5e582c05d80899ee73e1c009a7e5121e7a660d42cb518bb86933f3c06f'),
        ('numba.cpython.setobj._SetPayload._lookup', numba.cpython.setobj.
        _SetPayload._lookup,
        'c797b5399d7b227fe4eea3a058b3d3103f59345699388afb125ae47124bee395'),
        ('numba.cpython.setobj.SetInstance._add_entry', numba.cpython.
        setobj.SetInstance._add_entry,
        'c5ed28a5fdb453f242e41907cb792b66da2df63282c17abe0b68fc46782a7f94'),
        ('numba.cpython.setobj.SetInstance._add_key', numba.cpython.setobj.
        SetInstance._add_key,
        '324d6172638d02a361cfa0ca7f86e241e5a56a008d4ab581a305f9ae5ea4a75f'),
        ('numba.cpython.setobj.SetInstance._remove_entry', numba.cpython.
        setobj.SetInstance._remove_entry,
        '2c441b00daac61976e673c0e738e8e76982669bd2851951890dd40526fa14da1'),
        ('numba.cpython.setobj.SetInstance.pop', numba.cpython.setobj.
        SetInstance.pop,
        '1a7b7464cbe0577f2a38f3af9acfef6d4d25d049b1e216157275fbadaab41d1b'),
        ('numba.cpython.setobj.SetInstance._resize', numba.cpython.setobj.
        SetInstance._resize,
        '5ca5c2ba4f8c4bf546fde106b9c2656d4b22a16d16e163fb64c5d85ea4d88746'),
        ('numba.cpython.setobj.SetInstance._replace_payload', numba.cpython
        .setobj.SetInstance._replace_payload,
        'ada75a6c85828bff69c8469538c1979801f560a43fb726221a9c21bf208ae78d'),
        ('numba.cpython.setobj.SetInstance._allocate_payload', numba.
        cpython.setobj.SetInstance._allocate_payload,
        '2e80c419df43ebc71075b4f97fc1701c10dbc576aed248845e176b8d5829e61b'),
        ('numba.cpython.setobj.SetInstance._copy_payload', numba.cpython.
        setobj.SetInstance._copy_payload,
        '0885ac36e1eb5a0a0fc4f5d91e54b2102b69e536091fed9f2610a71d225193ec'),
        ('numba.cpython.setobj.set_constructor', numba.cpython.setobj.
        set_constructor,
        '3d521a60c3b8eaf70aa0f7267427475dfddd8f5e5053b5bfe309bb5f1891b0ce'),
        ('numba.cpython.setobj.set_update', numba.cpython.setobj.set_update,
        '965c4f7f7abcea5cbe0491b602e6d4bcb1800fa1ec39b1ffccf07e1bc56051c3')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
        orig = new
numba.core.boxing._native_set_to_python_list = _native_set_to_python_list
numba.cpython.setobj._SetPayload._lookup = _lookup
numba.cpython.setobj.SetInstance._add_entry = _add_entry
numba.cpython.setobj.SetInstance._add_key = _add_key
numba.cpython.setobj.SetInstance._remove_entry = _remove_entry
numba.cpython.setobj.SetInstance.pop = pop
numba.cpython.setobj.SetInstance._resize = _resize
numba.cpython.setobj.SetInstance._replace_payload = _replace_payload
numba.cpython.setobj.SetInstance._allocate_payload = _allocate_payload
numba.cpython.setobj.SetInstance._copy_payload = _copy_payload


def _reduce(self):
    libdata = self.library.serialize_using_object_code()
    typeann = str(self.type_annotation)
    fndesc = self.fndesc
    fndesc.typemap = fndesc.calltypes = None
    referenced_envs = self._find_referenced_environments()
    kpx__lcecw = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, kpx__lcecw, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    bpn__efb = target_context.get_executable(library, fndesc, env)
    tfkhf__cwge = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=bpn__efb, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return tfkhf__cwge


if _check_numba_change:
    for name, orig, hash in (('numba.core.compiler.CompileResult._reduce',
        numba.core.compiler.CompileResult._reduce,
        '5f86eacfa5202c202b3dc200f1a7a9b6d3f9d1ec16d43a52cb2d580c34fbfa82'),
        ('numba.core.compiler.CompileResult._rebuild', numba.core.compiler.
        CompileResult._rebuild,
        '44fa9dc2255883ab49195d18c3cca8c0ad715d0dd02033bd7e2376152edc4e84')):
        lines = inspect.getsource(orig)
        if hashlib.sha256(lines.encode()).hexdigest() != hash:
            warnings.warn(f'{name} has changed')
        orig = new
numba.core.compiler.CompileResult._reduce = _reduce
numba.core.compiler.CompileResult._rebuild = _rebuild
if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._IPythonCacheLocator.
        get_cache_path)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'eb33b7198697b8ef78edddcf69e58973c44744ff2cb2f54d4015611ad43baed0':
        warnings.warn(
            'numba.core.caching._IPythonCacheLocator.get_cache_path has changed'
            )
if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:

    def _get_cache_path(self):
        return numba.config.CACHE_DIR
    numba.core.caching._IPythonCacheLocator.get_cache_path = _get_cache_path
if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheLocator.
        ensure_cache_path)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '906b6f516f76927dfbe69602c335fa151b9f33d40dfe171a9190c0d11627bc03':
        warnings.warn(
            'numba.core.caching._CacheLocator.ensure_cache_path has changed')
if os.environ.get('BODO_PLATFORM_CACHE_LOCATION') is not None:
    import tempfile

    def _ensure_cache_path(self):
        from mpi4py import MPI
        xebsu__cjbz = MPI.COMM_WORLD
        hszx__vmqpa = None
        if xebsu__cjbz.Get_rank() == 0:
            try:
                czbo__fyat = self.get_cache_path()
                os.makedirs(czbo__fyat, exist_ok=True)
                tempfile.TemporaryFile(dir=czbo__fyat).close()
            except Exception as e:
                hszx__vmqpa = e
        hszx__vmqpa = xebsu__cjbz.bcast(hszx__vmqpa)
        if isinstance(hszx__vmqpa, Exception):
            raise hszx__vmqpa
    numba.core.caching._CacheLocator.ensure_cache_path = _ensure_cache_path
