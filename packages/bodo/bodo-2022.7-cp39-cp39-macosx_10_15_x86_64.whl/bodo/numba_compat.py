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
    woxi__neoxr = numba.core.bytecode.FunctionIdentity.from_function(func)
    omotn__vyufa = numba.core.interpreter.Interpreter(woxi__neoxr)
    tclxt__jcsar = numba.core.bytecode.ByteCode(func_id=woxi__neoxr)
    func_ir = omotn__vyufa.interpret(tclxt__jcsar)
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
        jekz__rwvg = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        jekz__rwvg.run()
    tmcfg__vnfj = numba.core.postproc.PostProcessor(func_ir)
    tmcfg__vnfj.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, bxg__lnoy in visit_vars_extensions.items():
        if isinstance(stmt, t):
            bxg__lnoy(stmt, callback, cbdata)
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
    xffay__pztek = ['ravel', 'transpose', 'reshape']
    for kqrwa__nxqul in blocks.values():
        for kumzz__sebp in kqrwa__nxqul.body:
            if type(kumzz__sebp) in alias_analysis_extensions:
                bxg__lnoy = alias_analysis_extensions[type(kumzz__sebp)]
                bxg__lnoy(kumzz__sebp, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(kumzz__sebp, ir.Assign):
                eixty__jhh = kumzz__sebp.value
                kylm__exa = kumzz__sebp.target.name
                if is_immutable_type(kylm__exa, typemap):
                    continue
                if isinstance(eixty__jhh, ir.Var
                    ) and kylm__exa != eixty__jhh.name:
                    _add_alias(kylm__exa, eixty__jhh.name, alias_map,
                        arg_aliases)
                if isinstance(eixty__jhh, ir.Expr) and (eixty__jhh.op ==
                    'cast' or eixty__jhh.op in ['getitem', 'static_getitem']):
                    _add_alias(kylm__exa, eixty__jhh.value.name, alias_map,
                        arg_aliases)
                if isinstance(eixty__jhh, ir.Expr
                    ) and eixty__jhh.op == 'inplace_binop':
                    _add_alias(kylm__exa, eixty__jhh.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(eixty__jhh, ir.Expr
                    ) and eixty__jhh.op == 'getattr' and eixty__jhh.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(kylm__exa, eixty__jhh.value.name, alias_map,
                        arg_aliases)
                if isinstance(eixty__jhh, ir.Expr
                    ) and eixty__jhh.op == 'getattr' and eixty__jhh.attr not in [
                    'shape'] and eixty__jhh.value.name in arg_aliases:
                    _add_alias(kylm__exa, eixty__jhh.value.name, alias_map,
                        arg_aliases)
                if isinstance(eixty__jhh, ir.Expr
                    ) and eixty__jhh.op == 'getattr' and eixty__jhh.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(kylm__exa, eixty__jhh.value.name, alias_map,
                        arg_aliases)
                if isinstance(eixty__jhh, ir.Expr) and eixty__jhh.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(kylm__exa, typemap):
                    for wszc__jdfyn in eixty__jhh.items:
                        _add_alias(kylm__exa, wszc__jdfyn.name, alias_map,
                            arg_aliases)
                if isinstance(eixty__jhh, ir.Expr) and eixty__jhh.op == 'call':
                    qjfii__gkb = guard(find_callname, func_ir, eixty__jhh,
                        typemap)
                    if qjfii__gkb is None:
                        continue
                    djdzv__hfag, dwqt__cluqm = qjfii__gkb
                    if qjfii__gkb in alias_func_extensions:
                        ywpnb__nim = alias_func_extensions[qjfii__gkb]
                        ywpnb__nim(kylm__exa, eixty__jhh.args, alias_map,
                            arg_aliases)
                    if dwqt__cluqm == 'numpy' and djdzv__hfag in xffay__pztek:
                        _add_alias(kylm__exa, eixty__jhh.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(dwqt__cluqm, ir.Var
                        ) and djdzv__hfag in xffay__pztek:
                        _add_alias(kylm__exa, dwqt__cluqm.name, alias_map,
                            arg_aliases)
    msvk__szhzl = copy.deepcopy(alias_map)
    for wszc__jdfyn in msvk__szhzl:
        for zll__ykwso in msvk__szhzl[wszc__jdfyn]:
            alias_map[wszc__jdfyn] |= alias_map[zll__ykwso]
        for zll__ykwso in msvk__szhzl[wszc__jdfyn]:
            alias_map[zll__ykwso] = alias_map[wszc__jdfyn]
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
    mgb__ogv = compute_cfg_from_blocks(func_ir.blocks)
    ueqk__ngpbe = compute_use_defs(func_ir.blocks)
    uljno__vbbhf = compute_live_map(mgb__ogv, func_ir.blocks, ueqk__ngpbe.
        usemap, ueqk__ngpbe.defmap)
    bih__iolqc = True
    while bih__iolqc:
        bih__iolqc = False
        for nah__zwy, block in func_ir.blocks.items():
            lives = {wszc__jdfyn.name for wszc__jdfyn in block.terminator.
                list_vars()}
            for ncuq__nptr, yetga__eiw in mgb__ogv.successors(nah__zwy):
                lives |= uljno__vbbhf[ncuq__nptr]
            dsxdn__phq = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    kylm__exa = stmt.target
                    fmrnp__qph = stmt.value
                    if kylm__exa.name not in lives:
                        if isinstance(fmrnp__qph, ir.Expr
                            ) and fmrnp__qph.op == 'make_function':
                            continue
                        if isinstance(fmrnp__qph, ir.Expr
                            ) and fmrnp__qph.op == 'getattr':
                            continue
                        if isinstance(fmrnp__qph, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(kylm__exa,
                            None), types.Function):
                            continue
                        if isinstance(fmrnp__qph, ir.Expr
                            ) and fmrnp__qph.op == 'build_map':
                            continue
                        if isinstance(fmrnp__qph, ir.Expr
                            ) and fmrnp__qph.op == 'build_tuple':
                            continue
                    if isinstance(fmrnp__qph, ir.Var
                        ) and kylm__exa.name == fmrnp__qph.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    mqem__azsp = analysis.ir_extension_usedefs[type(stmt)]
                    lbm__zkwr, fxos__spiwm = mqem__azsp(stmt)
                    lives -= fxos__spiwm
                    lives |= lbm__zkwr
                else:
                    lives |= {wszc__jdfyn.name for wszc__jdfyn in stmt.
                        list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(kylm__exa.name)
                dsxdn__phq.append(stmt)
            dsxdn__phq.reverse()
            if len(block.body) != len(dsxdn__phq):
                bih__iolqc = True
            block.body = dsxdn__phq


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    xgwc__qkl = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (xgwc__qkl,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    buzer__hkdqq = dict(key=func, _overload_func=staticmethod(overload_func
        ), _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), buzer__hkdqq)


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
            for msyjr__vaep in fnty.templates:
                self._inline_overloads.update(msyjr__vaep._inline_overloads)
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
    buzer__hkdqq = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), buzer__hkdqq)
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
    hyeun__syje, qpsn__lpvm = self._get_impl(args, kws)
    if hyeun__syje is None:
        return
    zwox__xsjoj = types.Dispatcher(hyeun__syje)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        impi__uibu = hyeun__syje._compiler
        flags = compiler.Flags()
        pag__ktfj = impi__uibu.targetdescr.typing_context
        qcdre__lnc = impi__uibu.targetdescr.target_context
        bjuwu__ufvhx = impi__uibu.pipeline_class(pag__ktfj, qcdre__lnc,
            None, None, None, flags, None)
        osb__iwd = InlineWorker(pag__ktfj, qcdre__lnc, impi__uibu.locals,
            bjuwu__ufvhx, flags, None)
        wlx__myvc = zwox__xsjoj.dispatcher.get_call_template
        msyjr__vaep, pxdac__oetvy, hiud__fwsig, kws = wlx__myvc(qpsn__lpvm, kws
            )
        if hiud__fwsig in self._inline_overloads:
            return self._inline_overloads[hiud__fwsig]['iinfo'].signature
        ir = osb__iwd.run_untyped_passes(zwox__xsjoj.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, qcdre__lnc, ir, hiud__fwsig, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, hiud__fwsig, None)
        self._inline_overloads[sig.args] = {'folded_args': hiud__fwsig}
        brghy__ylhmj = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = brghy__ylhmj
        if not self._inline.is_always_inline:
            sig = zwox__xsjoj.get_call_type(self.context, qpsn__lpvm, kws)
            self._compiled_overloads[sig.args] = zwox__xsjoj.get_overload(sig)
        vwj__zoba = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': hiud__fwsig,
            'iinfo': vwj__zoba}
    else:
        sig = zwox__xsjoj.get_call_type(self.context, qpsn__lpvm, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = zwox__xsjoj.get_overload(sig)
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
    dzm__evv = [True, False]
    wirbl__cuk = [False, True]
    sgwe__mtd = _ResolutionFailures(context, self, args, kws, depth=self._depth
        )
    from numba.core.target_extension import get_local_target
    yionk__fcvyd = get_local_target(context)
    gemw__tvr = utils.order_by_target_specificity(yionk__fcvyd, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for mjyl__enom in gemw__tvr:
        nnea__xnuev = mjyl__enom(context)
        evkv__beb = dzm__evv if nnea__xnuev.prefer_literal else wirbl__cuk
        evkv__beb = [True] if getattr(nnea__xnuev, '_no_unliteral', False
            ) else evkv__beb
        for nvugx__thdc in evkv__beb:
            try:
                if nvugx__thdc:
                    sig = nnea__xnuev.apply(args, kws)
                else:
                    fth__eno = tuple([_unlit_non_poison(a) for a in args])
                    jtrzm__rns = {pvx__dhnhg: _unlit_non_poison(wszc__jdfyn
                        ) for pvx__dhnhg, wszc__jdfyn in kws.items()}
                    sig = nnea__xnuev.apply(fth__eno, jtrzm__rns)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    sgwe__mtd.add_error(nnea__xnuev, False, e, nvugx__thdc)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = nnea__xnuev.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    ucuby__lqh = getattr(nnea__xnuev, 'cases', None)
                    if ucuby__lqh is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            ucuby__lqh)
                    else:
                        msg = 'No match.'
                    sgwe__mtd.add_error(nnea__xnuev, True, msg, nvugx__thdc)
    sgwe__mtd.raise_error()


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
    msyjr__vaep = self.template(context)
    bose__xfxn = None
    rqgbt__wyrp = None
    vuljq__rqcv = None
    evkv__beb = [True, False] if msyjr__vaep.prefer_literal else [False, True]
    evkv__beb = [True] if getattr(msyjr__vaep, '_no_unliteral', False
        ) else evkv__beb
    for nvugx__thdc in evkv__beb:
        if nvugx__thdc:
            try:
                vuljq__rqcv = msyjr__vaep.apply(args, kws)
            except Exception as jul__kkyx:
                if isinstance(jul__kkyx, errors.ForceLiteralArg):
                    raise jul__kkyx
                bose__xfxn = jul__kkyx
                vuljq__rqcv = None
            else:
                break
        else:
            pgu__pgvb = tuple([_unlit_non_poison(a) for a in args])
            zbwpn__oowm = {pvx__dhnhg: _unlit_non_poison(wszc__jdfyn) for 
                pvx__dhnhg, wszc__jdfyn in kws.items()}
            hjs__ooi = pgu__pgvb == args and kws == zbwpn__oowm
            if not hjs__ooi and vuljq__rqcv is None:
                try:
                    vuljq__rqcv = msyjr__vaep.apply(pgu__pgvb, zbwpn__oowm)
                except Exception as jul__kkyx:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        jul__kkyx, errors.NumbaError):
                        raise jul__kkyx
                    if isinstance(jul__kkyx, errors.ForceLiteralArg):
                        if msyjr__vaep.prefer_literal:
                            raise jul__kkyx
                    rqgbt__wyrp = jul__kkyx
                else:
                    break
    if vuljq__rqcv is None and (rqgbt__wyrp is not None or bose__xfxn is not
        None):
        cyr__tgil = '- Resolution failure for {} arguments:\n{}\n'
        ehbaq__ovg = _termcolor.highlight(cyr__tgil)
        if numba.core.config.DEVELOPER_MODE:
            dfua__alrbt = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    jvdr__jrj = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    jvdr__jrj = ['']
                ekafb__rewy = '\n{}'.format(2 * dfua__alrbt)
                bjk__xqps = _termcolor.reset(ekafb__rewy + ekafb__rewy.join
                    (_bt_as_lines(jvdr__jrj)))
                return _termcolor.reset(bjk__xqps)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            qez__uyose = str(e)
            qez__uyose = qez__uyose if qez__uyose else str(repr(e)) + add_bt(e)
            jdfx__coz = errors.TypingError(textwrap.dedent(qez__uyose))
            return ehbaq__ovg.format(literalness, str(jdfx__coz))
        import bodo
        if isinstance(bose__xfxn, bodo.utils.typing.BodoError):
            raise bose__xfxn
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', bose__xfxn) +
                nested_msg('non-literal', rqgbt__wyrp))
        else:
            if 'missing a required argument' in bose__xfxn.msg:
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
            raise errors.TypingError(msg, loc=bose__xfxn.loc)
    return vuljq__rqcv


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
    djdzv__hfag = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=djdzv__hfag)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            yhhep__vsdqc = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), yhhep__vsdqc)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    incn__yjg = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            incn__yjg.append(types.Omitted(a.value))
        else:
            incn__yjg.append(self.typeof_pyval(a))
    xehyo__hts = None
    try:
        error = None
        xehyo__hts = self.compile(tuple(incn__yjg))
    except errors.ForceLiteralArg as e:
        lqs__eknvm = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if lqs__eknvm:
            qeen__iiel = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            hstm__cstod = ', '.join('Arg #{} is {}'.format(i, args[i]) for
                i in sorted(lqs__eknvm))
            raise errors.CompilerError(qeen__iiel.format(hstm__cstod))
        qpsn__lpvm = []
        try:
            for i, wszc__jdfyn in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        qpsn__lpvm.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        qpsn__lpvm.append(types.literal(args[i]))
                else:
                    qpsn__lpvm.append(args[i])
            args = qpsn__lpvm
        except (OSError, FileNotFoundError) as aht__yeds:
            error = FileNotFoundError(str(aht__yeds) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                xehyo__hts = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        xek__gpprf = []
        for i, wcrzu__ukaaa in enumerate(args):
            val = wcrzu__ukaaa.value if isinstance(wcrzu__ukaaa, numba.core
                .dispatcher.OmittedArg) else wcrzu__ukaaa
            try:
                pfyci__opxr = typeof(val, Purpose.argument)
            except ValueError as lxu__icfps:
                xek__gpprf.append((i, str(lxu__icfps)))
            else:
                if pfyci__opxr is None:
                    xek__gpprf.append((i,
                        f'cannot determine Numba type of value {val}'))
        if xek__gpprf:
            xsge__zstxz = '\n'.join(f'- argument {i}: {nvl__gmm}' for i,
                nvl__gmm in xek__gpprf)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{xsge__zstxz}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                buj__oni = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                ptfh__uxhem = False
                for uby__fvxm in buj__oni:
                    if uby__fvxm in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        ptfh__uxhem = True
                        break
                if not ptfh__uxhem:
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
                yhhep__vsdqc = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), yhhep__vsdqc)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return xehyo__hts


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
    for jvly__rdpre in cres.library._codegen._engine._defined_symbols:
        if jvly__rdpre.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in jvly__rdpre and (
            'bodo_gb_udf_update_local' in jvly__rdpre or 
            'bodo_gb_udf_combine' in jvly__rdpre or 'bodo_gb_udf_eval' in
            jvly__rdpre or 'bodo_gb_apply_general_udfs' in jvly__rdpre):
            gb_agg_cfunc_addr[jvly__rdpre
                ] = cres.library.get_pointer_to_function(jvly__rdpre)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for jvly__rdpre in cres.library._codegen._engine._defined_symbols:
        if jvly__rdpre.startswith('cfunc') and ('get_join_cond_addr' not in
            jvly__rdpre or 'bodo_join_gen_cond' in jvly__rdpre):
            join_gen_cond_cfunc_addr[jvly__rdpre
                ] = cres.library.get_pointer_to_function(jvly__rdpre)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    hyeun__syje = self._get_dispatcher_for_current_target()
    if hyeun__syje is not self:
        return hyeun__syje.compile(sig)
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
            sfk__iwph = self.overloads.get(tuple(args))
            if sfk__iwph is not None:
                return sfk__iwph.entry_point
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
            fti__mdnzr = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=fti__mdnzr):
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
                uyxs__rvbbb = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in uyxs__rvbbb:
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
    upww__volwo = self._final_module
    ptd__xpnmw = []
    bzuz__wrdob = 0
    for fn in upww__volwo.functions:
        bzuz__wrdob += 1
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
            ptd__xpnmw.append(fn.name)
    if bzuz__wrdob == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if ptd__xpnmw:
        upww__volwo = upww__volwo.clone()
        for name in ptd__xpnmw:
            upww__volwo.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = upww__volwo
    return upww__volwo


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
    for metaq__ynggr in self.constraints:
        loc = metaq__ynggr.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                metaq__ynggr(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                pay__ora = numba.core.errors.TypingError(str(e), loc=
                    metaq__ynggr.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(pay__ora, e))
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
                    pay__ora = numba.core.errors.TypingError(msg.format(con
                        =metaq__ynggr, err=str(e)), loc=metaq__ynggr.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(pay__ora, e))
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
    for kuj__nkoho in self._failures.values():
        for ejtj__hjb in kuj__nkoho:
            if isinstance(ejtj__hjb.error, ForceLiteralArg):
                raise ejtj__hjb.error
            if isinstance(ejtj__hjb.error, bodo.utils.typing.BodoError):
                raise ejtj__hjb.error
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
    ffa__lbpm = False
    dsxdn__phq = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        tdgb__spgy = set()
        cdbzx__ammze = lives & alias_set
        for wszc__jdfyn in cdbzx__ammze:
            tdgb__spgy |= alias_map[wszc__jdfyn]
        lives_n_aliases = lives | tdgb__spgy | arg_aliases
        if type(stmt) in remove_dead_extensions:
            bxg__lnoy = remove_dead_extensions[type(stmt)]
            stmt = bxg__lnoy(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                ffa__lbpm = True
                continue
        if isinstance(stmt, ir.Assign):
            kylm__exa = stmt.target
            fmrnp__qph = stmt.value
            if kylm__exa.name not in lives:
                if has_no_side_effect(fmrnp__qph, lives_n_aliases, call_table):
                    ffa__lbpm = True
                    continue
                if isinstance(fmrnp__qph, ir.Expr
                    ) and fmrnp__qph.op == 'call' and call_table[fmrnp__qph
                    .func.name] == ['astype']:
                    yjw__grgoj = guard(get_definition, func_ir, fmrnp__qph.func
                        )
                    if (yjw__grgoj is not None and yjw__grgoj.op ==
                        'getattr' and isinstance(typemap[yjw__grgoj.value.
                        name], types.Array) and yjw__grgoj.attr == 'astype'):
                        ffa__lbpm = True
                        continue
            if saved_array_analysis and kylm__exa.name in lives and is_expr(
                fmrnp__qph, 'getattr'
                ) and fmrnp__qph.attr == 'shape' and is_array_typ(typemap[
                fmrnp__qph.value.name]) and fmrnp__qph.value.name not in lives:
                akxm__fnlhm = {wszc__jdfyn: pvx__dhnhg for pvx__dhnhg,
                    wszc__jdfyn in func_ir.blocks.items()}
                if block in akxm__fnlhm:
                    nah__zwy = akxm__fnlhm[block]
                    svmj__gatur = saved_array_analysis.get_equiv_set(nah__zwy)
                    esoq__scg = svmj__gatur.get_equiv_set(fmrnp__qph.value)
                    if esoq__scg is not None:
                        for wszc__jdfyn in esoq__scg:
                            if wszc__jdfyn.endswith('#0'):
                                wszc__jdfyn = wszc__jdfyn[:-2]
                            if wszc__jdfyn in typemap and is_array_typ(typemap
                                [wszc__jdfyn]) and wszc__jdfyn in lives:
                                fmrnp__qph.value = ir.Var(fmrnp__qph.value.
                                    scope, wszc__jdfyn, fmrnp__qph.value.loc)
                                ffa__lbpm = True
                                break
            if isinstance(fmrnp__qph, ir.Var
                ) and kylm__exa.name == fmrnp__qph.name:
                ffa__lbpm = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                ffa__lbpm = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            mqem__azsp = analysis.ir_extension_usedefs[type(stmt)]
            lbm__zkwr, fxos__spiwm = mqem__azsp(stmt)
            lives -= fxos__spiwm
            lives |= lbm__zkwr
        else:
            lives |= {wszc__jdfyn.name for wszc__jdfyn in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                zlba__wozw = set()
                if isinstance(fmrnp__qph, ir.Expr):
                    zlba__wozw = {wszc__jdfyn.name for wszc__jdfyn in
                        fmrnp__qph.list_vars()}
                if kylm__exa.name not in zlba__wozw:
                    lives.remove(kylm__exa.name)
        dsxdn__phq.append(stmt)
    dsxdn__phq.reverse()
    block.body = dsxdn__phq
    return ffa__lbpm


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            vdia__jtnft, = args
            if isinstance(vdia__jtnft, types.IterableType):
                dtype = vdia__jtnft.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), vdia__jtnft)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    cnp__jzg = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (cnp__jzg, self.dtype)
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
        except LiteralTypingError as ojlqm__kpdn:
            return
    try:
        return literal(value)
    except LiteralTypingError as ojlqm__kpdn:
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
        znmfd__ukvve = py_func.__qualname__
    except AttributeError as ojlqm__kpdn:
        znmfd__ukvve = py_func.__name__
    iza__ipc = inspect.getfile(py_func)
    for cls in self._locator_classes:
        xcc__lfhut = cls.from_function(py_func, iza__ipc)
        if xcc__lfhut is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (znmfd__ukvve, iza__ipc))
    self._locator = xcc__lfhut
    dclng__ipok = inspect.getfile(py_func)
    azemq__rifj = os.path.splitext(os.path.basename(dclng__ipok))[0]
    if iza__ipc.startswith('<ipython-'):
        yywyb__gxv = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', azemq__rifj, count=1)
        if yywyb__gxv == azemq__rifj:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        azemq__rifj = yywyb__gxv
    ufuqj__ofa = '%s.%s' % (azemq__rifj, znmfd__ukvve)
    yhewq__nnu = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(ufuqj__ofa, yhewq__nnu
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    tfb__inomz = list(filter(lambda a: self._istuple(a.name), args))
    if len(tfb__inomz) == 2 and fn.__name__ == 'add':
        bzhgo__kduz = self.typemap[tfb__inomz[0].name]
        fayoz__knb = self.typemap[tfb__inomz[1].name]
        if bzhgo__kduz.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                tfb__inomz[1]))
        if fayoz__knb.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                tfb__inomz[0]))
        try:
            wlpai__ipa = [equiv_set.get_shape(x) for x in tfb__inomz]
            if None in wlpai__ipa:
                return None
            sxd__avgi = sum(wlpai__ipa, ())
            return ArrayAnalysis.AnalyzeResult(shape=sxd__avgi)
        except GuardException as ojlqm__kpdn:
            return None
    ppuin__rpm = list(filter(lambda a: self._isarray(a.name), args))
    require(len(ppuin__rpm) > 0)
    pwv__mjw = [x.name for x in ppuin__rpm]
    vpz__ivs = [self.typemap[x.name].ndim for x in ppuin__rpm]
    pbc__gwv = max(vpz__ivs)
    require(pbc__gwv > 0)
    wlpai__ipa = [equiv_set.get_shape(x) for x in ppuin__rpm]
    if any(a is None for a in wlpai__ipa):
        return ArrayAnalysis.AnalyzeResult(shape=ppuin__rpm[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, ppuin__rpm))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, wlpai__ipa,
        pwv__mjw)


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
    mzp__qsfg = code_obj.code
    wyr__bup = len(mzp__qsfg.co_freevars)
    jlzx__tleic = mzp__qsfg.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        goupw__qat, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        jlzx__tleic = [wszc__jdfyn.name for wszc__jdfyn in goupw__qat]
    zaok__tvg = caller_ir.func_id.func.__globals__
    try:
        zaok__tvg = getattr(code_obj, 'globals', zaok__tvg)
    except KeyError as ojlqm__kpdn:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    uip__euty = []
    for x in jlzx__tleic:
        try:
            hmiv__eam = caller_ir.get_definition(x)
        except KeyError as ojlqm__kpdn:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(hmiv__eam, (ir.Const, ir.Global, ir.FreeVar)):
            val = hmiv__eam.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                xgwc__qkl = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                zaok__tvg[xgwc__qkl] = bodo.jit(distributed=False)(val)
                zaok__tvg[xgwc__qkl].is_nested_func = True
                val = xgwc__qkl
            if isinstance(val, CPUDispatcher):
                xgwc__qkl = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                zaok__tvg[xgwc__qkl] = val
                val = xgwc__qkl
            uip__euty.append(val)
        elif isinstance(hmiv__eam, ir.Expr
            ) and hmiv__eam.op == 'make_function':
            qwcr__fud = convert_code_obj_to_function(hmiv__eam, caller_ir)
            xgwc__qkl = ir_utils.mk_unique_var('nested_func').replace('.', '_')
            zaok__tvg[xgwc__qkl] = bodo.jit(distributed=False)(qwcr__fud)
            zaok__tvg[xgwc__qkl].is_nested_func = True
            uip__euty.append(xgwc__qkl)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    ayg__bfjog = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        uip__euty)])
    dyf__evqp = ','.join([('c_%d' % i) for i in range(wyr__bup)])
    cswi__xdin = list(mzp__qsfg.co_varnames)
    nula__tmwb = 0
    vduf__avdlg = mzp__qsfg.co_argcount
    cgscm__ajj = caller_ir.get_definition(code_obj.defaults)
    if cgscm__ajj is not None:
        if isinstance(cgscm__ajj, tuple):
            d = [caller_ir.get_definition(x).value for x in cgscm__ajj]
            twynm__njk = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in cgscm__ajj.items]
            twynm__njk = tuple(d)
        nula__tmwb = len(twynm__njk)
    zbzxc__xpkqq = vduf__avdlg - nula__tmwb
    hdn__jtkep = ','.join([('%s' % cswi__xdin[i]) for i in range(zbzxc__xpkqq)]
        )
    if nula__tmwb:
        lfqu__hfb = [('%s = %s' % (cswi__xdin[i + zbzxc__xpkqq], twynm__njk
            [i])) for i in range(nula__tmwb)]
        hdn__jtkep += ', '
        hdn__jtkep += ', '.join(lfqu__hfb)
    return _create_function_from_code_obj(mzp__qsfg, ayg__bfjog, hdn__jtkep,
        dyf__evqp, zaok__tvg)


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
    for nsrgb__tyug, (ntesr__kqkq, axs__ysrwp) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % axs__ysrwp)
            rrnpj__tzrw = _pass_registry.get(ntesr__kqkq).pass_inst
            if isinstance(rrnpj__tzrw, CompilerPass):
                self._runPass(nsrgb__tyug, rrnpj__tzrw, state)
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
                    pipeline_name, axs__ysrwp)
                twuvo__jcfey = self._patch_error(msg, e)
                raise twuvo__jcfey
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
    thhzc__rbfd = None
    fxos__spiwm = {}

    def lookup(var, already_seen, varonly=True):
        val = fxos__spiwm.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    ocxfx__qnplr = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        kylm__exa = stmt.target
        fmrnp__qph = stmt.value
        fxos__spiwm[kylm__exa.name] = fmrnp__qph
        if isinstance(fmrnp__qph, ir.Var) and fmrnp__qph.name in fxos__spiwm:
            fmrnp__qph = lookup(fmrnp__qph, set())
        if isinstance(fmrnp__qph, ir.Expr):
            jdwib__hbbjy = set(lookup(wszc__jdfyn, set(), True).name for
                wszc__jdfyn in fmrnp__qph.list_vars())
            if name in jdwib__hbbjy:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(fmrnp__qph)]
                adz__cca = [x for x, abfcy__vyfm in args if abfcy__vyfm.
                    name != name]
                args = [(x, abfcy__vyfm) for x, abfcy__vyfm in args if x !=
                    abfcy__vyfm.name]
                ocppk__hhn = dict(args)
                if len(adz__cca) == 1:
                    ocppk__hhn[adz__cca[0]] = ir.Var(kylm__exa.scope, name +
                        '#init', kylm__exa.loc)
                replace_vars_inner(fmrnp__qph, ocppk__hhn)
                thhzc__rbfd = nodes[i:]
                break
    return thhzc__rbfd


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
        gvelc__phuj = expand_aliases({wszc__jdfyn.name for wszc__jdfyn in
            stmt.list_vars()}, alias_map, arg_aliases)
        xro__bnnq = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        yeod__vohw = expand_aliases({wszc__jdfyn.name for wszc__jdfyn in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        fzvs__lams = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(xro__bnnq & yeod__vohw | fzvs__lams & gvelc__phuj) == 0:
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
    wwi__hlcq = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            wwi__hlcq.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                wwi__hlcq.update(get_parfor_writes(stmt, func_ir))
    return wwi__hlcq


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    wwi__hlcq = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        wwi__hlcq.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        wwi__hlcq = {wszc__jdfyn.name for wszc__jdfyn in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        wwi__hlcq = {wszc__jdfyn.name for wszc__jdfyn in stmt.
            get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            wwi__hlcq.update({wszc__jdfyn.name for wszc__jdfyn in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        qjfii__gkb = guard(find_callname, func_ir, stmt.value)
        if qjfii__gkb in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            wwi__hlcq.add(stmt.value.args[0].name)
        if qjfii__gkb == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            wwi__hlcq.add(stmt.value.args[1].name)
    return wwi__hlcq


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
        bxg__lnoy = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        tjtv__kjyze = bxg__lnoy.format(self, msg)
        self.args = tjtv__kjyze,
    else:
        bxg__lnoy = _termcolor.errmsg('{0}')
        tjtv__kjyze = bxg__lnoy.format(self)
        self.args = tjtv__kjyze,
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
        for bmcaj__alvt in options['distributed']:
            dist_spec[bmcaj__alvt] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for bmcaj__alvt in options['distributed_block']:
            dist_spec[bmcaj__alvt] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    oqnpd__zmtgr = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, mmotl__uka in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(mmotl__uka)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    avl__duyb = {}
    for bgj__ppj in reversed(inspect.getmro(cls)):
        avl__duyb.update(bgj__ppj.__dict__)
    mulwe__eezcm, umx__lxsf, kfo__zxif, jjwpt__nxr = {}, {}, {}, {}
    for pvx__dhnhg, wszc__jdfyn in avl__duyb.items():
        if isinstance(wszc__jdfyn, pytypes.FunctionType):
            mulwe__eezcm[pvx__dhnhg] = wszc__jdfyn
        elif isinstance(wszc__jdfyn, property):
            umx__lxsf[pvx__dhnhg] = wszc__jdfyn
        elif isinstance(wszc__jdfyn, staticmethod):
            kfo__zxif[pvx__dhnhg] = wszc__jdfyn
        else:
            jjwpt__nxr[pvx__dhnhg] = wszc__jdfyn
    rhuaj__qnav = (set(mulwe__eezcm) | set(umx__lxsf) | set(kfo__zxif)) & set(
        spec)
    if rhuaj__qnav:
        raise NameError('name shadowing: {0}'.format(', '.join(rhuaj__qnav)))
    kxq__eepjg = jjwpt__nxr.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(jjwpt__nxr)
    if jjwpt__nxr:
        msg = 'class members are not yet supported: {0}'
        maeoh__wdm = ', '.join(jjwpt__nxr.keys())
        raise TypeError(msg.format(maeoh__wdm))
    for pvx__dhnhg, wszc__jdfyn in umx__lxsf.items():
        if wszc__jdfyn.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(pvx__dhnhg))
    jit_methods = {pvx__dhnhg: bodo.jit(returns_maybe_distributed=
        oqnpd__zmtgr)(wszc__jdfyn) for pvx__dhnhg, wszc__jdfyn in
        mulwe__eezcm.items()}
    jit_props = {}
    for pvx__dhnhg, wszc__jdfyn in umx__lxsf.items():
        buzer__hkdqq = {}
        if wszc__jdfyn.fget:
            buzer__hkdqq['get'] = bodo.jit(wszc__jdfyn.fget)
        if wszc__jdfyn.fset:
            buzer__hkdqq['set'] = bodo.jit(wszc__jdfyn.fset)
        jit_props[pvx__dhnhg] = buzer__hkdqq
    jit_static_methods = {pvx__dhnhg: bodo.jit(wszc__jdfyn.__func__) for 
        pvx__dhnhg, wszc__jdfyn in kfo__zxif.items()}
    suloa__auomw = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    jvkfo__urogn = dict(class_type=suloa__auomw, __doc__=kxq__eepjg)
    jvkfo__urogn.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), jvkfo__urogn)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, suloa__auomw)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(suloa__auomw, typingctx, targetctx).register()
    as_numba_type.register(cls, suloa__auomw.instance_type)
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
    hrqct__bjpm = ','.join('{0}:{1}'.format(pvx__dhnhg, wszc__jdfyn) for 
        pvx__dhnhg, wszc__jdfyn in struct.items())
    zoya__sfl = ','.join('{0}:{1}'.format(pvx__dhnhg, wszc__jdfyn) for 
        pvx__dhnhg, wszc__jdfyn in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), hrqct__bjpm, zoya__sfl)
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
    yruy__ddmqx = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if yruy__ddmqx is None:
        return
    qmh__emtoq, snfs__qkt = yruy__ddmqx
    for a in itertools.chain(qmh__emtoq, snfs__qkt.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, qmh__emtoq, snfs__qkt)
    except ForceLiteralArg as e:
        zlpfc__zmse = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(zlpfc__zmse, self.kws)
        nwdz__qkovi = set()
        tnqku__fubmq = set()
        ckrpw__uov = {}
        for nsrgb__tyug in e.requested_args:
            ehkp__dkybt = typeinfer.func_ir.get_definition(folded[nsrgb__tyug])
            if isinstance(ehkp__dkybt, ir.Arg):
                nwdz__qkovi.add(ehkp__dkybt.index)
                if ehkp__dkybt.index in e.file_infos:
                    ckrpw__uov[ehkp__dkybt.index] = e.file_infos[ehkp__dkybt
                        .index]
            else:
                tnqku__fubmq.add(nsrgb__tyug)
        if tnqku__fubmq:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif nwdz__qkovi:
            raise ForceLiteralArg(nwdz__qkovi, loc=self.loc, file_infos=
                ckrpw__uov)
    if sig is None:
        lyqq__jjpz = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in qmh__emtoq]
        args += [('%s=%s' % (pvx__dhnhg, wszc__jdfyn)) for pvx__dhnhg,
            wszc__jdfyn in sorted(snfs__qkt.items())]
        cvbwg__ddv = lyqq__jjpz.format(fnty, ', '.join(map(str, args)))
        ruj__jxfmz = context.explain_function_type(fnty)
        msg = '\n'.join([cvbwg__ddv, ruj__jxfmz])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        aqb__fhd = context.unify_pairs(sig.recvr, fnty.this)
        if aqb__fhd is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if aqb__fhd is not None and aqb__fhd.is_precise():
            chjm__wrled = fnty.copy(this=aqb__fhd)
            typeinfer.propagate_refined_type(self.func, chjm__wrled)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            iwwon__uqc = target.getone()
            if context.unify_pairs(iwwon__uqc, sig.return_type) == iwwon__uqc:
                sig = sig.replace(return_type=iwwon__uqc)
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
        qeen__iiel = '*other* must be a {} but got a {} instead'
        raise TypeError(qeen__iiel.format(ForceLiteralArg, type(other)))
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
    rwkun__vctey = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for pvx__dhnhg, wszc__jdfyn in kwargs.items():
        tgn__bujsd = None
        try:
            iwl__dahb = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var(
                'dummy'), loc)
            func_ir._definitions[iwl__dahb.name] = [wszc__jdfyn]
            tgn__bujsd = get_const_value_inner(func_ir, iwl__dahb)
            func_ir._definitions.pop(iwl__dahb.name)
            if isinstance(tgn__bujsd, str):
                tgn__bujsd = sigutils._parse_signature_string(tgn__bujsd)
            if isinstance(tgn__bujsd, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {pvx__dhnhg} is annotated as type class {tgn__bujsd}."""
                    )
            assert isinstance(tgn__bujsd, types.Type)
            if isinstance(tgn__bujsd, (types.List, types.Set)):
                tgn__bujsd = tgn__bujsd.copy(reflected=False)
            rwkun__vctey[pvx__dhnhg] = tgn__bujsd
        except BodoError as ojlqm__kpdn:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(tgn__bujsd, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(wszc__jdfyn, ir.Global):
                    msg = f'Global {wszc__jdfyn.name!r} is not defined.'
                if isinstance(wszc__jdfyn, ir.FreeVar):
                    msg = f'Freevar {wszc__jdfyn.name!r} is not defined.'
            if isinstance(wszc__jdfyn, ir.Expr
                ) and wszc__jdfyn.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=pvx__dhnhg, msg=msg, loc=loc)
    for name, typ in rwkun__vctey.items():
        self._legalize_arg_type(name, typ, loc)
    return rwkun__vctey


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
    gnty__jhtr = inst.arg
    assert gnty__jhtr > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(gnty__jhtr)]))
    tmps = [state.make_temp() for _ in range(gnty__jhtr - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    ryms__aipyn = ir.Global('format', format, loc=self.loc)
    self.store(value=ryms__aipyn, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    meux__kdr = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=meux__kdr, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    gnty__jhtr = inst.arg
    assert gnty__jhtr > 0, 'invalid BUILD_STRING count'
    goon__sbfa = self.get(strings[0])
    for other, ycpb__hdmcl in zip(strings[1:], tmps):
        other = self.get(other)
        eixty__jhh = ir.Expr.binop(operator.add, lhs=goon__sbfa, rhs=other,
            loc=self.loc)
        self.store(eixty__jhh, ycpb__hdmcl)
        goon__sbfa = self.get(ycpb__hdmcl)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    dluln__juqsd = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, dluln__juqsd])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    jwu__vewub = mk_unique_var(f'{var_name}')
    lgyh__fndgg = jwu__vewub.replace('<', '_').replace('>', '_')
    lgyh__fndgg = lgyh__fndgg.replace('.', '_').replace('$', '_v')
    return lgyh__fndgg


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
                waw__jwsw = get_overload_const_str(val2)
                if waw__jwsw != 'ns':
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
        enc__uosfr = states['defmap']
        if len(enc__uosfr) == 0:
            eao__wyda = assign.target
            numba.core.ssa._logger.debug('first assign: %s', eao__wyda)
            if eao__wyda.name not in scope.localvars:
                eao__wyda = scope.define(assign.target.name, loc=assign.loc)
        else:
            eao__wyda = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=eao__wyda, value=assign.value, loc=assign.loc
            )
        enc__uosfr[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    hvhp__gzwof = []
    for pvx__dhnhg, wszc__jdfyn in typing.npydecl.registry.globals:
        if pvx__dhnhg == func:
            hvhp__gzwof.append(wszc__jdfyn)
    for pvx__dhnhg, wszc__jdfyn in typing.templates.builtin_registry.globals:
        if pvx__dhnhg == func:
            hvhp__gzwof.append(wszc__jdfyn)
    if len(hvhp__gzwof) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return hvhp__gzwof


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    qaod__xbap = {}
    qrel__bqgdg = find_topo_order(blocks)
    jtip__fptmj = {}
    for nah__zwy in qrel__bqgdg:
        block = blocks[nah__zwy]
        dsxdn__phq = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                kylm__exa = stmt.target.name
                fmrnp__qph = stmt.value
                if (fmrnp__qph.op == 'getattr' and fmrnp__qph.attr in
                    arr_math and isinstance(typemap[fmrnp__qph.value.name],
                    types.npytypes.Array)):
                    fmrnp__qph = stmt.value
                    nzz__pepc = fmrnp__qph.value
                    qaod__xbap[kylm__exa] = nzz__pepc
                    scope = nzz__pepc.scope
                    loc = nzz__pepc.loc
                    fek__fwx = ir.Var(scope, mk_unique_var('$np_g_var'), loc)
                    typemap[fek__fwx.name] = types.misc.Module(numpy)
                    wxj__nux = ir.Global('np', numpy, loc)
                    dkwus__ntcnr = ir.Assign(wxj__nux, fek__fwx, loc)
                    fmrnp__qph.value = fek__fwx
                    dsxdn__phq.append(dkwus__ntcnr)
                    func_ir._definitions[fek__fwx.name] = [wxj__nux]
                    func = getattr(numpy, fmrnp__qph.attr)
                    vkmb__nadw = get_np_ufunc_typ_lst(func)
                    jtip__fptmj[kylm__exa] = vkmb__nadw
                if (fmrnp__qph.op == 'call' and fmrnp__qph.func.name in
                    qaod__xbap):
                    nzz__pepc = qaod__xbap[fmrnp__qph.func.name]
                    ogzc__tsw = calltypes.pop(fmrnp__qph)
                    gif__fje = ogzc__tsw.args[:len(fmrnp__qph.args)]
                    lnuoh__kkyoy = {name: typemap[wszc__jdfyn.name] for 
                        name, wszc__jdfyn in fmrnp__qph.kws}
                    myrb__wjnf = jtip__fptmj[fmrnp__qph.func.name]
                    yvoo__won = None
                    for riz__vuh in myrb__wjnf:
                        try:
                            yvoo__won = riz__vuh.get_call_type(typingctx, [
                                typemap[nzz__pepc.name]] + list(gif__fje),
                                lnuoh__kkyoy)
                            typemap.pop(fmrnp__qph.func.name)
                            typemap[fmrnp__qph.func.name] = riz__vuh
                            calltypes[fmrnp__qph] = yvoo__won
                            break
                        except Exception as ojlqm__kpdn:
                            pass
                    if yvoo__won is None:
                        raise TypeError(
                            f'No valid template found for {fmrnp__qph.func.name}'
                            )
                    fmrnp__qph.args = [nzz__pepc] + fmrnp__qph.args
            dsxdn__phq.append(stmt)
        block.body = dsxdn__phq


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    vdc__kjwfc = ufunc.nin
    ktv__noqe = ufunc.nout
    zbzxc__xpkqq = ufunc.nargs
    assert zbzxc__xpkqq == vdc__kjwfc + ktv__noqe
    if len(args) < vdc__kjwfc:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), vdc__kjwfc)
            )
    if len(args) > zbzxc__xpkqq:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            zbzxc__xpkqq))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    pof__ywqq = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    gicnl__sks = max(pof__ywqq)
    ugm__umqw = args[vdc__kjwfc:]
    if not all(d == gicnl__sks for d in pof__ywqq[vdc__kjwfc:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(dtri__khld, types.ArrayCompatible) and not
        isinstance(dtri__khld, types.Bytes) for dtri__khld in ugm__umqw):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(dtri__khld.mutable for dtri__khld in ugm__umqw):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    kxmh__qqesl = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    cijtl__pjv = None
    if gicnl__sks > 0 and len(ugm__umqw) < ufunc.nout:
        cijtl__pjv = 'C'
        exl__boca = [(x.layout if isinstance(x, types.ArrayCompatible) and 
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in exl__boca and 'F' in exl__boca:
            cijtl__pjv = 'F'
    return kxmh__qqesl, ugm__umqw, gicnl__sks, cijtl__pjv


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
        cbds__kgyi = 'Dict.key_type cannot be of type {}'
        raise TypingError(cbds__kgyi.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        cbds__kgyi = 'Dict.value_type cannot be of type {}'
        raise TypingError(cbds__kgyi.format(valty))
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
    ritj__baj = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[ritj__baj]
        return impl, args
    except KeyError as ojlqm__kpdn:
        pass
    impl, args = self._build_impl(ritj__baj, args, kws)
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
        bxxd__xwa = find_topo_order(parfor.loop_body)
    jkiw__ssuoz = bxxd__xwa[0]
    pfe__rliq = {}
    _update_parfor_get_setitems(parfor.loop_body[jkiw__ssuoz].body, parfor.
        index_var, alias_map, pfe__rliq, lives_n_aliases)
    cgpif__nlym = set(pfe__rliq.keys())
    for mpoz__xwax in bxxd__xwa:
        if mpoz__xwax == jkiw__ssuoz:
            continue
        for stmt in parfor.loop_body[mpoz__xwax].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            urm__nsv = set(wszc__jdfyn.name for wszc__jdfyn in stmt.list_vars()
                )
            gnml__qgfz = urm__nsv & cgpif__nlym
            for a in gnml__qgfz:
                pfe__rliq.pop(a, None)
    for mpoz__xwax in bxxd__xwa:
        if mpoz__xwax == jkiw__ssuoz:
            continue
        block = parfor.loop_body[mpoz__xwax]
        owsp__cnf = pfe__rliq.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            owsp__cnf, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    lhnw__ngbo = max(blocks.keys())
    hurol__ysi, ehiek__glawj = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    egtnv__rjda = ir.Jump(hurol__ysi, ir.Loc('parfors_dummy', -1))
    blocks[lhnw__ngbo].body.append(egtnv__rjda)
    mgb__ogv = compute_cfg_from_blocks(blocks)
    ueqk__ngpbe = compute_use_defs(blocks)
    uljno__vbbhf = compute_live_map(mgb__ogv, blocks, ueqk__ngpbe.usemap,
        ueqk__ngpbe.defmap)
    alias_set = set(alias_map.keys())
    for nah__zwy, block in blocks.items():
        dsxdn__phq = []
        ookyh__syib = {wszc__jdfyn.name for wszc__jdfyn in block.terminator
            .list_vars()}
        for ncuq__nptr, yetga__eiw in mgb__ogv.successors(nah__zwy):
            ookyh__syib |= uljno__vbbhf[ncuq__nptr]
        for stmt in reversed(block.body):
            tdgb__spgy = ookyh__syib & alias_set
            for wszc__jdfyn in tdgb__spgy:
                ookyh__syib |= alias_map[wszc__jdfyn]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in ookyh__syib and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                qjfii__gkb = guard(find_callname, func_ir, stmt.value)
                if qjfii__gkb == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in ookyh__syib and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            ookyh__syib |= {wszc__jdfyn.name for wszc__jdfyn in stmt.
                list_vars()}
            dsxdn__phq.append(stmt)
        dsxdn__phq.reverse()
        block.body = dsxdn__phq
    typemap.pop(ehiek__glawj.name)
    blocks[lhnw__ngbo].body.pop()

    def trim_empty_parfor_branches(parfor):
        bih__iolqc = False
        blocks = parfor.loop_body.copy()
        for nah__zwy, block in blocks.items():
            if len(block.body):
                sifqw__ijke = block.body[-1]
                if isinstance(sifqw__ijke, ir.Branch):
                    if len(blocks[sifqw__ijke.truebr].body) == 1 and len(blocks
                        [sifqw__ijke.falsebr].body) == 1:
                        fmosv__chhaq = blocks[sifqw__ijke.truebr].body[0]
                        uysx__jlbrn = blocks[sifqw__ijke.falsebr].body[0]
                        if isinstance(fmosv__chhaq, ir.Jump) and isinstance(
                            uysx__jlbrn, ir.Jump
                            ) and fmosv__chhaq.target == uysx__jlbrn.target:
                            parfor.loop_body[nah__zwy].body[-1] = ir.Jump(
                                fmosv__chhaq.target, sifqw__ijke.loc)
                            bih__iolqc = True
                    elif len(blocks[sifqw__ijke.truebr].body) == 1:
                        fmosv__chhaq = blocks[sifqw__ijke.truebr].body[0]
                        if isinstance(fmosv__chhaq, ir.Jump
                            ) and fmosv__chhaq.target == sifqw__ijke.falsebr:
                            parfor.loop_body[nah__zwy].body[-1] = ir.Jump(
                                fmosv__chhaq.target, sifqw__ijke.loc)
                            bih__iolqc = True
                    elif len(blocks[sifqw__ijke.falsebr].body) == 1:
                        uysx__jlbrn = blocks[sifqw__ijke.falsebr].body[0]
                        if isinstance(uysx__jlbrn, ir.Jump
                            ) and uysx__jlbrn.target == sifqw__ijke.truebr:
                            parfor.loop_body[nah__zwy].body[-1] = ir.Jump(
                                uysx__jlbrn.target, sifqw__ijke.loc)
                            bih__iolqc = True
        return bih__iolqc
    bih__iolqc = True
    while bih__iolqc:
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
        bih__iolqc = trim_empty_parfor_branches(parfor)
    iicbm__pulg = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        iicbm__pulg &= len(block.body) == 0
    if iicbm__pulg:
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
    tmrp__zeieq = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                tmrp__zeieq += 1
                parfor = stmt
                gcl__plov = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = gcl__plov.scope
                loc = ir.Loc('parfors_dummy', -1)
                imex__hroy = ir.Var(scope, mk_unique_var('$const'), loc)
                gcl__plov.body.append(ir.Assign(ir.Const(0, loc),
                    imex__hroy, loc))
                gcl__plov.body.append(ir.Return(imex__hroy, loc))
                mgb__ogv = compute_cfg_from_blocks(parfor.loop_body)
                for yfk__pxnap in mgb__ogv.dead_nodes():
                    del parfor.loop_body[yfk__pxnap]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                gcl__plov = parfor.loop_body[max(parfor.loop_body.keys())]
                gcl__plov.body.pop()
                gcl__plov.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return tmrp__zeieq


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
            sfk__iwph = self.overloads.get(tuple(args))
            if sfk__iwph is not None:
                return sfk__iwph.entry_point
            self._pre_compile(args, return_type, flags)
            jhba__cdt = self.func_ir
            fti__mdnzr = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=fti__mdnzr):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=jhba__cdt, args=args,
                    return_type=return_type, flags=flags, locals=self.
                    locals, lifted=(), lifted_from=self.lifted_from,
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
        oou__kdqgl = copy.deepcopy(flags)
        oou__kdqgl.no_rewrites = True

        def compile_local(the_ir, the_flags):
            ecc__bioan = pipeline_class(typingctx, targetctx, library, args,
                return_type, the_flags, locals)
            return ecc__bioan.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        kown__uss = compile_local(func_ir, oou__kdqgl)
        ssqqr__jcchm = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    ssqqr__jcchm = compile_local(func_ir, flags)
                except Exception as ojlqm__kpdn:
                    pass
        if ssqqr__jcchm is not None:
            cres = ssqqr__jcchm
        else:
            cres = kown__uss
        return cres
    else:
        ecc__bioan = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return ecc__bioan.compile_ir(func_ir=func_ir, lifted=lifted,
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
    pfiu__rrd = self.get_data_type(typ.dtype)
    vrlao__ufvu = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        vrlao__ufvu):
        dbfws__zwpup = ary.ctypes.data
        quvdg__znaxs = self.add_dynamic_addr(builder, dbfws__zwpup, info=
            str(type(dbfws__zwpup)))
        vql__xnd = self.add_dynamic_addr(builder, id(ary), info=str(type(ary)))
        self.global_arrays.append(ary)
    else:
        bdxhn__floi = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            bdxhn__floi = bdxhn__floi.view('int64')
        val = bytearray(bdxhn__floi.data)
        ftn__nxzj = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val)
        quvdg__znaxs = cgutils.global_constant(builder, '.const.array.data',
            ftn__nxzj)
        quvdg__znaxs.align = self.get_abi_alignment(pfiu__rrd)
        vql__xnd = None
    wvmqc__pnd = self.get_value_type(types.intp)
    rri__jmae = [self.get_constant(types.intp, fcx__bsloc) for fcx__bsloc in
        ary.shape]
    ibbjs__ydtg = lir.Constant(lir.ArrayType(wvmqc__pnd, len(rri__jmae)),
        rri__jmae)
    ede__sxq = [self.get_constant(types.intp, fcx__bsloc) for fcx__bsloc in
        ary.strides]
    cyt__yzwb = lir.Constant(lir.ArrayType(wvmqc__pnd, len(ede__sxq)), ede__sxq
        )
    pstl__edte = self.get_constant(types.intp, ary.dtype.itemsize)
    dgi__jad = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        dgi__jad, pstl__edte, quvdg__znaxs.bitcast(self.get_value_type(
        types.CPointer(typ.dtype))), ibbjs__ydtg, cyt__yzwb])


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
    xsst__xhja = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    kjao__ztdt = lir.Function(module, xsst__xhja, name='nrt_atomic_{0}'.
        format(op))
    [rqgd__ggnkh] = kjao__ztdt.args
    zxu__wtxta = kjao__ztdt.append_basic_block()
    builder = lir.IRBuilder(zxu__wtxta)
    bafsz__swlk = lir.Constant(_word_type, 1)
    if False:
        dykj__jpdf = builder.atomic_rmw(op, rqgd__ggnkh, bafsz__swlk,
            ordering=ordering)
        res = getattr(builder, op)(dykj__jpdf, bafsz__swlk)
        builder.ret(res)
    else:
        dykj__jpdf = builder.load(rqgd__ggnkh)
        gix__kfxt = getattr(builder, op)(dykj__jpdf, bafsz__swlk)
        emgw__xbee = builder.icmp_signed('!=', dykj__jpdf, lir.Constant(
            dykj__jpdf.type, -1))
        with cgutils.if_likely(builder, emgw__xbee):
            builder.store(gix__kfxt, rqgd__ggnkh)
        builder.ret(gix__kfxt)
    return kjao__ztdt


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
        zfaz__knnf = state.targetctx.codegen()
        state.library = zfaz__knnf.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    omotn__vyufa = state.func_ir
    typemap = state.typemap
    ecix__rdg = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    feuv__zzp = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            omotn__vyufa, typemap, ecix__rdg, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            alkvj__gclu = lowering.Lower(targetctx, library, fndesc,
                omotn__vyufa, metadata=metadata)
            alkvj__gclu.lower()
            if not flags.no_cpython_wrapper:
                alkvj__gclu.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(ecix__rdg, (types.Optional, types.Generator)
                        ):
                        pass
                    else:
                        alkvj__gclu.create_cfunc_wrapper()
            env = alkvj__gclu.env
            ijyr__mnnvv = alkvj__gclu.call_helper
            del alkvj__gclu
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, ijyr__mnnvv, cfunc=None, env=env
                )
        else:
            jhxz__pdjg = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(jhxz__pdjg, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, ijyr__mnnvv, cfunc=
                jhxz__pdjg, env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        sgi__fbak = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = sgi__fbak - feuv__zzp
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
        fhvd__nycia = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, fhvd__nycia),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            yaf__toh.do_break()
        gzk__ccnss = c.builder.icmp_signed('!=', fhvd__nycia, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(gzk__ccnss, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, fhvd__nycia)
                c.pyapi.decref(fhvd__nycia)
                yaf__toh.do_break()
        c.pyapi.decref(fhvd__nycia)
    mhf__szwhw, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(mhf__szwhw, likely=True) as (pcu__wwcq, pud__ycz):
        with pcu__wwcq:
            list.size = size
            aimz__hin = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                aimz__hin), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        aimz__hin))
                    with cgutils.for_range(c.builder, size) as yaf__toh:
                        itemobj = c.pyapi.list_getitem(obj, yaf__toh.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        apcg__caz = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(apcg__caz.is_error, likely=False
                            ):
                            c.builder.store(cgutils.true_bit, errorptr)
                            yaf__toh.do_break()
                        list.setitem(yaf__toh.index, apcg__caz.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with pud__ycz:
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
    fkpue__rcskr, roxao__pgqpa, bkl__xfs, vmbao__bmhng, dmzrk__dcd = (
        compile_time_get_string_data(literal_string))
    upww__volwo = builder.module
    gv = context.insert_const_bytes(upww__volwo, fkpue__rcskr)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        roxao__pgqpa), context.get_constant(types.int32, bkl__xfs), context
        .get_constant(types.uint32, vmbao__bmhng), context.get_constant(
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
    lxne__bmih = None
    if isinstance(shape, types.Integer):
        lxne__bmih = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(fcx__bsloc, (types.Integer, types.IntEnumMember)) for
            fcx__bsloc in shape):
            lxne__bmih = len(shape)
    return lxne__bmih


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
            lxne__bmih = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if lxne__bmih == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(lxne__bmih)
                    )
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            pwv__mjw = self._get_names(x)
            if len(pwv__mjw) != 0:
                return pwv__mjw[0]
            return pwv__mjw
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    pwv__mjw = self._get_names(obj)
    if len(pwv__mjw) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(pwv__mjw[0])


def get_equiv_set(self, obj):
    pwv__mjw = self._get_names(obj)
    if len(pwv__mjw) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(pwv__mjw[0])


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
    wtt__yuos = []
    for aoxf__hlk in func_ir.arg_names:
        if aoxf__hlk in typemap and isinstance(typemap[aoxf__hlk], types.
            containers.UniTuple) and typemap[aoxf__hlk].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(aoxf__hlk))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for kygh__tagb in func_ir.blocks.values():
        for stmt in kygh__tagb.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    ojfx__tnfik = getattr(val, 'code', None)
                    if ojfx__tnfik is not None:
                        if getattr(val, 'closure', None) is not None:
                            veu__fzqny = '<creating a function from a closure>'
                            eixty__jhh = ''
                        else:
                            veu__fzqny = ojfx__tnfik.co_name
                            eixty__jhh = '(%s) ' % veu__fzqny
                    else:
                        veu__fzqny = '<could not ascertain use case>'
                        eixty__jhh = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (veu__fzqny, eixty__jhh))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                qnp__ygu = False
                if isinstance(val, pytypes.FunctionType):
                    qnp__ygu = val in {numba.gdb, numba.gdb_init}
                if not qnp__ygu:
                    qnp__ygu = getattr(val, '_name', '') == 'gdb_internal'
                if qnp__ygu:
                    wtt__yuos.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    bqn__lya = func_ir.get_definition(var)
                    kyxtv__vrtpd = guard(find_callname, func_ir, bqn__lya)
                    if kyxtv__vrtpd and kyxtv__vrtpd[1] == 'numpy':
                        ty = getattr(numpy, kyxtv__vrtpd[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    oaotz__vljc = '' if var.startswith('$'
                        ) else "'{}' ".format(var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(oaotz__vljc), loc=stmt.loc)
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
    if len(wtt__yuos) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        wnh__anfc = '\n'.join([x.strformat() for x in wtt__yuos])
        raise errors.UnsupportedError(msg % wnh__anfc)


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
    pvx__dhnhg, wszc__jdfyn = next(iter(val.items()))
    vurw__dch = typeof_impl(pvx__dhnhg, c)
    yeqs__abraj = typeof_impl(wszc__jdfyn, c)
    if vurw__dch is None or yeqs__abraj is None:
        raise ValueError(
            f'Cannot type dict element type {type(pvx__dhnhg)}, {type(wszc__jdfyn)}'
            )
    return types.DictType(vurw__dch, yeqs__abraj)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    bhexq__csc = cgutils.alloca_once_value(c.builder, val)
    xze__bdb = c.pyapi.object_hasattr_string(val, '_opaque')
    hmfmx__dws = c.builder.icmp_unsigned('==', xze__bdb, lir.Constant(
        xze__bdb.type, 0))
    qxx__ainl = typ.key_type
    nfbh__vtfs = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(qxx__ainl, nfbh__vtfs)

    def copy_dict(out_dict, in_dict):
        for pvx__dhnhg, wszc__jdfyn in in_dict.items():
            out_dict[pvx__dhnhg] = wszc__jdfyn
    with c.builder.if_then(hmfmx__dws):
        hpul__pikhz = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        fzsg__nzbhn = c.pyapi.call_function_objargs(hpul__pikhz, [])
        zeug__kljiq = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(zeug__kljiq, [fzsg__nzbhn, val])
        c.builder.store(fzsg__nzbhn, bhexq__csc)
    val = c.builder.load(bhexq__csc)
    jhb__ptmgw = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    gyi__pgjay = c.pyapi.object_type(val)
    grcz__wfpg = c.builder.icmp_unsigned('==', gyi__pgjay, jhb__ptmgw)
    with c.builder.if_else(grcz__wfpg) as (tbq__fnng, ixps__htvjv):
        with tbq__fnng:
            vgmb__anhbo = c.pyapi.object_getattr_string(val, '_opaque')
            xgt__fobes = types.MemInfoPointer(types.voidptr)
            apcg__caz = c.unbox(xgt__fobes, vgmb__anhbo)
            mi = apcg__caz.value
            incn__yjg = xgt__fobes, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *incn__yjg)
            kag__enju = context.get_constant_null(incn__yjg[1])
            args = mi, kag__enju
            gnr__hzwiv, kmry__uap = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, kmry__uap)
            c.pyapi.decref(vgmb__anhbo)
            ulamt__vgwq = c.builder.basic_block
        with ixps__htvjv:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", gyi__pgjay, jhb__ptmgw)
            zkx__hubzj = c.builder.basic_block
    ftuq__nwya = c.builder.phi(kmry__uap.type)
    tshu__cuuus = c.builder.phi(gnr__hzwiv.type)
    ftuq__nwya.add_incoming(kmry__uap, ulamt__vgwq)
    ftuq__nwya.add_incoming(kmry__uap.type(None), zkx__hubzj)
    tshu__cuuus.add_incoming(gnr__hzwiv, ulamt__vgwq)
    tshu__cuuus.add_incoming(cgutils.true_bit, zkx__hubzj)
    c.pyapi.decref(jhb__ptmgw)
    c.pyapi.decref(gyi__pgjay)
    with c.builder.if_then(hmfmx__dws):
        c.pyapi.decref(val)
    return NativeValue(ftuq__nwya, is_error=tshu__cuuus)


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
    aaexz__wnk = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=aaexz__wnk, name=updatevar)
    jhyko__deqkp = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc
        )
    self.store(value=jhyko__deqkp, name=res)


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
        for pvx__dhnhg, wszc__jdfyn in other.items():
            d[pvx__dhnhg] = wszc__jdfyn
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
    eixty__jhh = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(eixty__jhh, res)


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
    hwacm__ivenp = PassManager(name)
    if state.func_ir is None:
        hwacm__ivenp.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            hwacm__ivenp.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        hwacm__ivenp.add_pass(FixupArgs, 'fix up args')
    hwacm__ivenp.add_pass(IRProcessing, 'processing IR')
    hwacm__ivenp.add_pass(WithLifting, 'Handle with contexts')
    hwacm__ivenp.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        hwacm__ivenp.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        hwacm__ivenp.add_pass(DeadBranchPrune, 'dead branch pruning')
        hwacm__ivenp.add_pass(GenericRewrites, 'nopython rewrites')
    hwacm__ivenp.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    hwacm__ivenp.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        hwacm__ivenp.add_pass(DeadBranchPrune, 'dead branch pruning')
    hwacm__ivenp.add_pass(FindLiterallyCalls, 'find literally calls')
    hwacm__ivenp.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        hwacm__ivenp.add_pass(ReconstructSSA, 'ssa')
    hwacm__ivenp.add_pass(LiteralPropagationSubPipelinePass,
        'Literal propagation')
    hwacm__ivenp.finalize()
    return hwacm__ivenp


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
    a, vme__nun = args
    if isinstance(a, types.List) and isinstance(vme__nun, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(vme__nun, types.List):
        return signature(vme__nun, types.intp, vme__nun)


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
        myphj__qpd, ybqu__ipk = 0, 1
    else:
        myphj__qpd, ybqu__ipk = 1, 0
    ewz__ynyrf = ListInstance(context, builder, sig.args[myphj__qpd], args[
        myphj__qpd])
    jibo__artz = ewz__ynyrf.size
    rxwq__xpsnc = args[ybqu__ipk]
    aimz__hin = lir.Constant(rxwq__xpsnc.type, 0)
    rxwq__xpsnc = builder.select(cgutils.is_neg_int(builder, rxwq__xpsnc),
        aimz__hin, rxwq__xpsnc)
    dgi__jad = builder.mul(rxwq__xpsnc, jibo__artz)
    jbs__obao = ListInstance.allocate(context, builder, sig.return_type,
        dgi__jad)
    jbs__obao.size = dgi__jad
    with cgutils.for_range_slice(builder, aimz__hin, dgi__jad, jibo__artz,
        inc=True) as (xod__tbo, _):
        with cgutils.for_range(builder, jibo__artz) as yaf__toh:
            value = ewz__ynyrf.getitem(yaf__toh.index)
            jbs__obao.setitem(builder.add(yaf__toh.index, xod__tbo), value,
                incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, jbs__obao.value)


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
    xqzws__vsis = first.unify(self, second)
    if xqzws__vsis is not None:
        return xqzws__vsis
    xqzws__vsis = second.unify(self, first)
    if xqzws__vsis is not None:
        return xqzws__vsis
    imzb__yhj = self.can_convert(fromty=first, toty=second)
    if imzb__yhj is not None and imzb__yhj <= Conversion.safe:
        return second
    imzb__yhj = self.can_convert(fromty=second, toty=first)
    if imzb__yhj is not None and imzb__yhj <= Conversion.safe:
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
    dgi__jad = payload.used
    listobj = c.pyapi.list_new(dgi__jad)
    mhf__szwhw = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(mhf__szwhw, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(dgi__jad.
            type, 0))
        with payload._iterate() as yaf__toh:
            i = c.builder.load(index)
            item = yaf__toh.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return mhf__szwhw, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    qfkgr__qermt = h.type
    vnw__nuxr = self.mask
    dtype = self._ty.dtype
    pag__ktfj = context.typing_context
    fnty = pag__ktfj.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(pag__ktfj, (dtype, dtype), {})
    saj__ftxsd = context.get_function(fnty, sig)
    kig__wgam = ir.Constant(qfkgr__qermt, 1)
    zayns__pxt = ir.Constant(qfkgr__qermt, 5)
    noi__iocx = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, vnw__nuxr))
    if for_insert:
        akytf__jdif = vnw__nuxr.type(-1)
        pqpwj__fejmc = cgutils.alloca_once_value(builder, akytf__jdif)
    yaiqw__vfw = builder.append_basic_block('lookup.body')
    jyphq__kdl = builder.append_basic_block('lookup.found')
    yqz__lam = builder.append_basic_block('lookup.not_found')
    kebzs__whaud = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        jfrza__khib = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, jfrza__khib)):
            egymb__mured = saj__ftxsd(builder, (item, entry.key))
            with builder.if_then(egymb__mured):
                builder.branch(jyphq__kdl)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, jfrza__khib)):
            builder.branch(yqz__lam)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, jfrza__khib)):
                ireo__iho = builder.load(pqpwj__fejmc)
                ireo__iho = builder.select(builder.icmp_unsigned('==',
                    ireo__iho, akytf__jdif), i, ireo__iho)
                builder.store(ireo__iho, pqpwj__fejmc)
    with cgutils.for_range(builder, ir.Constant(qfkgr__qermt, numba.cpython
        .setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, kig__wgam)
        i = builder.and_(i, vnw__nuxr)
        builder.store(i, index)
    builder.branch(yaiqw__vfw)
    with builder.goto_block(yaiqw__vfw):
        i = builder.load(index)
        check_entry(i)
        xadg__wlp = builder.load(noi__iocx)
        xadg__wlp = builder.lshr(xadg__wlp, zayns__pxt)
        i = builder.add(kig__wgam, builder.mul(i, zayns__pxt))
        i = builder.and_(vnw__nuxr, builder.add(i, xadg__wlp))
        builder.store(i, index)
        builder.store(xadg__wlp, noi__iocx)
        builder.branch(yaiqw__vfw)
    with builder.goto_block(yqz__lam):
        if for_insert:
            i = builder.load(index)
            ireo__iho = builder.load(pqpwj__fejmc)
            i = builder.select(builder.icmp_unsigned('==', ireo__iho,
                akytf__jdif), i, ireo__iho)
            builder.store(i, index)
        builder.branch(kebzs__whaud)
    with builder.goto_block(jyphq__kdl):
        builder.branch(kebzs__whaud)
    builder.position_at_end(kebzs__whaud)
    qnp__ygu = builder.phi(ir.IntType(1), 'found')
    qnp__ygu.add_incoming(cgutils.true_bit, jyphq__kdl)
    qnp__ygu.add_incoming(cgutils.false_bit, yqz__lam)
    return qnp__ygu, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    qglkp__qtkkj = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    ubu__uskv = payload.used
    kig__wgam = ir.Constant(ubu__uskv.type, 1)
    ubu__uskv = payload.used = builder.add(ubu__uskv, kig__wgam)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, qglkp__qtkkj), likely=True):
        payload.fill = builder.add(payload.fill, kig__wgam)
    if do_resize:
        self.upsize(ubu__uskv)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    qnp__ygu, i = payload._lookup(item, h, for_insert=True)
    bkhu__llzpq = builder.not_(qnp__ygu)
    with builder.if_then(bkhu__llzpq):
        entry = payload.get_entry(i)
        qglkp__qtkkj = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        ubu__uskv = payload.used
        kig__wgam = ir.Constant(ubu__uskv.type, 1)
        ubu__uskv = payload.used = builder.add(ubu__uskv, kig__wgam)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, qglkp__qtkkj), likely=True):
            payload.fill = builder.add(payload.fill, kig__wgam)
        if do_resize:
            self.upsize(ubu__uskv)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    ubu__uskv = payload.used
    kig__wgam = ir.Constant(ubu__uskv.type, 1)
    ubu__uskv = payload.used = self._builder.sub(ubu__uskv, kig__wgam)
    if do_resize:
        self.downsize(ubu__uskv)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    dlkxr__xpkuk = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, dlkxr__xpkuk)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    hle__owx = payload
    mhf__szwhw = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(mhf__szwhw), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with hle__owx._iterate() as yaf__toh:
        entry = yaf__toh.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(hle__owx.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as yaf__toh:
        entry = yaf__toh.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    mhf__szwhw = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(mhf__szwhw), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    mhf__szwhw = cgutils.alloca_once_value(builder, cgutils.true_bit)
    qfkgr__qermt = context.get_value_type(types.intp)
    aimz__hin = ir.Constant(qfkgr__qermt, 0)
    kig__wgam = ir.Constant(qfkgr__qermt, 1)
    xabz__qael = context.get_data_type(types.SetPayload(self._ty))
    hznn__ibiem = context.get_abi_sizeof(xabz__qael)
    cxup__llxh = self._entrysize
    hznn__ibiem -= cxup__llxh
    cpdq__uhk, jvjbf__jjeyi = cgutils.muladd_with_overflow(builder,
        nentries, ir.Constant(qfkgr__qermt, cxup__llxh), ir.Constant(
        qfkgr__qermt, hznn__ibiem))
    with builder.if_then(jvjbf__jjeyi, likely=False):
        builder.store(cgutils.false_bit, mhf__szwhw)
    with builder.if_then(builder.load(mhf__szwhw), likely=True):
        if realloc:
            srq__hcqwa = self._set.meminfo
            rqgd__ggnkh = context.nrt.meminfo_varsize_alloc(builder,
                srq__hcqwa, size=cpdq__uhk)
            adnwi__ygvvg = cgutils.is_null(builder, rqgd__ggnkh)
        else:
            odl__snj = _imp_dtor(context, builder.module, self._ty)
            srq__hcqwa = context.nrt.meminfo_new_varsize_dtor(builder,
                cpdq__uhk, builder.bitcast(odl__snj, cgutils.voidptr_t))
            adnwi__ygvvg = cgutils.is_null(builder, srq__hcqwa)
        with builder.if_else(adnwi__ygvvg, likely=False) as (yelwu__clh,
            pcu__wwcq):
            with yelwu__clh:
                builder.store(cgutils.false_bit, mhf__szwhw)
            with pcu__wwcq:
                if not realloc:
                    self._set.meminfo = srq__hcqwa
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, cpdq__uhk, 255)
                payload.used = aimz__hin
                payload.fill = aimz__hin
                payload.finger = aimz__hin
                zrze__gnqvl = builder.sub(nentries, kig__wgam)
                payload.mask = zrze__gnqvl
    return builder.load(mhf__szwhw)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    mhf__szwhw = cgutils.alloca_once_value(builder, cgutils.true_bit)
    qfkgr__qermt = context.get_value_type(types.intp)
    aimz__hin = ir.Constant(qfkgr__qermt, 0)
    kig__wgam = ir.Constant(qfkgr__qermt, 1)
    xabz__qael = context.get_data_type(types.SetPayload(self._ty))
    hznn__ibiem = context.get_abi_sizeof(xabz__qael)
    cxup__llxh = self._entrysize
    hznn__ibiem -= cxup__llxh
    vnw__nuxr = src_payload.mask
    nentries = builder.add(kig__wgam, vnw__nuxr)
    cpdq__uhk = builder.add(ir.Constant(qfkgr__qermt, hznn__ibiem), builder
        .mul(ir.Constant(qfkgr__qermt, cxup__llxh), nentries))
    with builder.if_then(builder.load(mhf__szwhw), likely=True):
        odl__snj = _imp_dtor(context, builder.module, self._ty)
        srq__hcqwa = context.nrt.meminfo_new_varsize_dtor(builder,
            cpdq__uhk, builder.bitcast(odl__snj, cgutils.voidptr_t))
        adnwi__ygvvg = cgutils.is_null(builder, srq__hcqwa)
        with builder.if_else(adnwi__ygvvg, likely=False) as (yelwu__clh,
            pcu__wwcq):
            with yelwu__clh:
                builder.store(cgutils.false_bit, mhf__szwhw)
            with pcu__wwcq:
                self._set.meminfo = srq__hcqwa
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = aimz__hin
                payload.mask = vnw__nuxr
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, cxup__llxh)
                with src_payload._iterate() as yaf__toh:
                    context.nrt.incref(builder, self._ty.dtype, yaf__toh.
                        entry.key)
    return builder.load(mhf__szwhw)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    ivbmv__pzsyj = context.get_value_type(types.voidptr)
    zzty__cxh = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [ivbmv__pzsyj, zzty__cxh,
        ivbmv__pzsyj])
    djdzv__hfag = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=djdzv__hfag)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        lbgku__ckcfr = builder.bitcast(fn.args[0], cgutils.voidptr_t.
            as_pointer())
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, lbgku__ckcfr)
        with payload._iterate() as yaf__toh:
            entry = yaf__toh.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    plkn__xprw, = sig.args
    goupw__qat, = args
    ekmsm__rqtqs = numba.core.imputils.call_len(context, builder,
        plkn__xprw, goupw__qat)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, ekmsm__rqtqs)
    with numba.core.imputils.for_iter(context, builder, plkn__xprw, goupw__qat
        ) as yaf__toh:
        inst.add(yaf__toh.value)
        context.nrt.decref(builder, set_type.dtype, yaf__toh.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    plkn__xprw = sig.args[1]
    goupw__qat = args[1]
    ekmsm__rqtqs = numba.core.imputils.call_len(context, builder,
        plkn__xprw, goupw__qat)
    if ekmsm__rqtqs is not None:
        pxect__ahh = builder.add(inst.payload.used, ekmsm__rqtqs)
        inst.upsize(pxect__ahh)
    with numba.core.imputils.for_iter(context, builder, plkn__xprw, goupw__qat
        ) as yaf__toh:
        vvlz__xrq = context.cast(builder, yaf__toh.value, plkn__xprw.dtype,
            inst.dtype)
        inst.add(vvlz__xrq)
        context.nrt.decref(builder, plkn__xprw.dtype, yaf__toh.value)
    if ekmsm__rqtqs is not None:
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
    kqjvo__sxod = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, kqjvo__sxod, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    jhxz__pdjg = target_context.get_executable(library, fndesc, env)
    xxl__dbhfs = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=jhxz__pdjg, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return xxl__dbhfs


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
        ewzy__socf = MPI.COMM_WORLD
        jul__kkyx = None
        if ewzy__socf.Get_rank() == 0:
            try:
                rfcs__bpwx = self.get_cache_path()
                os.makedirs(rfcs__bpwx, exist_ok=True)
                tempfile.TemporaryFile(dir=rfcs__bpwx).close()
            except Exception as e:
                jul__kkyx = e
        jul__kkyx = ewzy__socf.bcast(jul__kkyx)
        if isinstance(jul__kkyx, Exception):
            raise jul__kkyx
    numba.core.caching._CacheLocator.ensure_cache_path = _ensure_cache_path
