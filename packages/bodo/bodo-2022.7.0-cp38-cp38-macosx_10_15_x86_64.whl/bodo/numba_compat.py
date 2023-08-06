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
    iaz__gifw = numba.core.bytecode.FunctionIdentity.from_function(func)
    oeb__lji = numba.core.interpreter.Interpreter(iaz__gifw)
    kuuk__zhp = numba.core.bytecode.ByteCode(func_id=iaz__gifw)
    func_ir = oeb__lji.interpret(kuuk__zhp)
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
        urye__wffz = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        urye__wffz.run()
    ehxa__flv = numba.core.postproc.PostProcessor(func_ir)
    ehxa__flv.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, puanf__wcvu in visit_vars_extensions.items():
        if isinstance(stmt, t):
            puanf__wcvu(stmt, callback, cbdata)
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
    nif__mcbz = ['ravel', 'transpose', 'reshape']
    for uwl__xiwmw in blocks.values():
        for lnlu__ueyot in uwl__xiwmw.body:
            if type(lnlu__ueyot) in alias_analysis_extensions:
                puanf__wcvu = alias_analysis_extensions[type(lnlu__ueyot)]
                puanf__wcvu(lnlu__ueyot, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(lnlu__ueyot, ir.Assign):
                aqzg__smjbk = lnlu__ueyot.value
                rlji__dxhh = lnlu__ueyot.target.name
                if is_immutable_type(rlji__dxhh, typemap):
                    continue
                if isinstance(aqzg__smjbk, ir.Var
                    ) and rlji__dxhh != aqzg__smjbk.name:
                    _add_alias(rlji__dxhh, aqzg__smjbk.name, alias_map,
                        arg_aliases)
                if isinstance(aqzg__smjbk, ir.Expr) and (aqzg__smjbk.op ==
                    'cast' or aqzg__smjbk.op in ['getitem', 'static_getitem']):
                    _add_alias(rlji__dxhh, aqzg__smjbk.value.name,
                        alias_map, arg_aliases)
                if isinstance(aqzg__smjbk, ir.Expr
                    ) and aqzg__smjbk.op == 'inplace_binop':
                    _add_alias(rlji__dxhh, aqzg__smjbk.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(aqzg__smjbk, ir.Expr
                    ) and aqzg__smjbk.op == 'getattr' and aqzg__smjbk.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(rlji__dxhh, aqzg__smjbk.value.name,
                        alias_map, arg_aliases)
                if isinstance(aqzg__smjbk, ir.Expr
                    ) and aqzg__smjbk.op == 'getattr' and aqzg__smjbk.attr not in [
                    'shape'] and aqzg__smjbk.value.name in arg_aliases:
                    _add_alias(rlji__dxhh, aqzg__smjbk.value.name,
                        alias_map, arg_aliases)
                if isinstance(aqzg__smjbk, ir.Expr
                    ) and aqzg__smjbk.op == 'getattr' and aqzg__smjbk.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(rlji__dxhh, aqzg__smjbk.value.name,
                        alias_map, arg_aliases)
                if isinstance(aqzg__smjbk, ir.Expr) and aqzg__smjbk.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(rlji__dxhh, typemap):
                    for jdp__xtjj in aqzg__smjbk.items:
                        _add_alias(rlji__dxhh, jdp__xtjj.name, alias_map,
                            arg_aliases)
                if isinstance(aqzg__smjbk, ir.Expr
                    ) and aqzg__smjbk.op == 'call':
                    cgz__hmfn = guard(find_callname, func_ir, aqzg__smjbk,
                        typemap)
                    if cgz__hmfn is None:
                        continue
                    nse__juteg, vpfls__rins = cgz__hmfn
                    if cgz__hmfn in alias_func_extensions:
                        uefyc__xoh = alias_func_extensions[cgz__hmfn]
                        uefyc__xoh(rlji__dxhh, aqzg__smjbk.args, alias_map,
                            arg_aliases)
                    if vpfls__rins == 'numpy' and nse__juteg in nif__mcbz:
                        _add_alias(rlji__dxhh, aqzg__smjbk.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(vpfls__rins, ir.Var
                        ) and nse__juteg in nif__mcbz:
                        _add_alias(rlji__dxhh, vpfls__rins.name, alias_map,
                            arg_aliases)
    juom__ljp = copy.deepcopy(alias_map)
    for jdp__xtjj in juom__ljp:
        for aiy__hztfg in juom__ljp[jdp__xtjj]:
            alias_map[jdp__xtjj] |= alias_map[aiy__hztfg]
        for aiy__hztfg in juom__ljp[jdp__xtjj]:
            alias_map[aiy__hztfg] = alias_map[jdp__xtjj]
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
    xwtq__seqo = compute_cfg_from_blocks(func_ir.blocks)
    mnp__orjez = compute_use_defs(func_ir.blocks)
    kovru__fjw = compute_live_map(xwtq__seqo, func_ir.blocks, mnp__orjez.
        usemap, mnp__orjez.defmap)
    cax__xcjj = True
    while cax__xcjj:
        cax__xcjj = False
        for hst__uhnup, block in func_ir.blocks.items():
            lives = {jdp__xtjj.name for jdp__xtjj in block.terminator.
                list_vars()}
            for wro__locbr, nkq__cwvi in xwtq__seqo.successors(hst__uhnup):
                lives |= kovru__fjw[wro__locbr]
            edcon__tcpjb = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    rlji__dxhh = stmt.target
                    zofpg__iml = stmt.value
                    if rlji__dxhh.name not in lives:
                        if isinstance(zofpg__iml, ir.Expr
                            ) and zofpg__iml.op == 'make_function':
                            continue
                        if isinstance(zofpg__iml, ir.Expr
                            ) and zofpg__iml.op == 'getattr':
                            continue
                        if isinstance(zofpg__iml, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(rlji__dxhh,
                            None), types.Function):
                            continue
                        if isinstance(zofpg__iml, ir.Expr
                            ) and zofpg__iml.op == 'build_map':
                            continue
                        if isinstance(zofpg__iml, ir.Expr
                            ) and zofpg__iml.op == 'build_tuple':
                            continue
                    if isinstance(zofpg__iml, ir.Var
                        ) and rlji__dxhh.name == zofpg__iml.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    ftqze__djkyw = analysis.ir_extension_usedefs[type(stmt)]
                    tndre__rpe, qfjom__ejqvj = ftqze__djkyw(stmt)
                    lives -= qfjom__ejqvj
                    lives |= tndre__rpe
                else:
                    lives |= {jdp__xtjj.name for jdp__xtjj in stmt.list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(rlji__dxhh.name)
                edcon__tcpjb.append(stmt)
            edcon__tcpjb.reverse()
            if len(block.body) != len(edcon__tcpjb):
                cax__xcjj = True
            block.body = edcon__tcpjb


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    ula__nme = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (ula__nme,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    lhxsh__wxu = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), lhxsh__wxu)


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
            for dswbr__qjaev in fnty.templates:
                self._inline_overloads.update(dswbr__qjaev._inline_overloads)
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
    lhxsh__wxu = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), lhxsh__wxu)
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
    jylh__llm, fey__ekh = self._get_impl(args, kws)
    if jylh__llm is None:
        return
    shvr__avvh = types.Dispatcher(jylh__llm)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        jaic__qqht = jylh__llm._compiler
        flags = compiler.Flags()
        nsmd__ikeee = jaic__qqht.targetdescr.typing_context
        logf__jwx = jaic__qqht.targetdescr.target_context
        dvv__qis = jaic__qqht.pipeline_class(nsmd__ikeee, logf__jwx, None,
            None, None, flags, None)
        cby__wkl = InlineWorker(nsmd__ikeee, logf__jwx, jaic__qqht.locals,
            dvv__qis, flags, None)
        oozpj__yxyvp = shvr__avvh.dispatcher.get_call_template
        dswbr__qjaev, yyfu__pgybe, gwugl__fad, kws = oozpj__yxyvp(fey__ekh, kws
            )
        if gwugl__fad in self._inline_overloads:
            return self._inline_overloads[gwugl__fad]['iinfo'].signature
        ir = cby__wkl.run_untyped_passes(shvr__avvh.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, logf__jwx, ir, gwugl__fad, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, gwugl__fad, None)
        self._inline_overloads[sig.args] = {'folded_args': gwugl__fad}
        gyfwg__het = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = gyfwg__het
        if not self._inline.is_always_inline:
            sig = shvr__avvh.get_call_type(self.context, fey__ekh, kws)
            self._compiled_overloads[sig.args] = shvr__avvh.get_overload(sig)
        mralf__wyhz = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': gwugl__fad,
            'iinfo': mralf__wyhz}
    else:
        sig = shvr__avvh.get_call_type(self.context, fey__ekh, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = shvr__avvh.get_overload(sig)
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
    zbf__dsca = [True, False]
    utjy__uevlm = [False, True]
    kimry__ooauy = _ResolutionFailures(context, self, args, kws, depth=self
        ._depth)
    from numba.core.target_extension import get_local_target
    zphdz__duj = get_local_target(context)
    jdc__flxr = utils.order_by_target_specificity(zphdz__duj, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for mvmr__klqt in jdc__flxr:
        coutd__pgu = mvmr__klqt(context)
        fxsf__neum = zbf__dsca if coutd__pgu.prefer_literal else utjy__uevlm
        fxsf__neum = [True] if getattr(coutd__pgu, '_no_unliteral', False
            ) else fxsf__neum
        for rllq__zgvze in fxsf__neum:
            try:
                if rllq__zgvze:
                    sig = coutd__pgu.apply(args, kws)
                else:
                    yzh__ufkp = tuple([_unlit_non_poison(a) for a in args])
                    gzkim__nll = {gtily__cuckl: _unlit_non_poison(jdp__xtjj
                        ) for gtily__cuckl, jdp__xtjj in kws.items()}
                    sig = coutd__pgu.apply(yzh__ufkp, gzkim__nll)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    kimry__ooauy.add_error(coutd__pgu, False, e, rllq__zgvze)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = coutd__pgu.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    wipii__fkyt = getattr(coutd__pgu, 'cases', None)
                    if wipii__fkyt is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            wipii__fkyt)
                    else:
                        msg = 'No match.'
                    kimry__ooauy.add_error(coutd__pgu, True, msg, rllq__zgvze)
    kimry__ooauy.raise_error()


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
    dswbr__qjaev = self.template(context)
    itgby__sxt = None
    dux__cpl = None
    bkjpu__jvpzq = None
    fxsf__neum = [True, False] if dswbr__qjaev.prefer_literal else [False, True
        ]
    fxsf__neum = [True] if getattr(dswbr__qjaev, '_no_unliteral', False
        ) else fxsf__neum
    for rllq__zgvze in fxsf__neum:
        if rllq__zgvze:
            try:
                bkjpu__jvpzq = dswbr__qjaev.apply(args, kws)
            except Exception as ubsih__cssvw:
                if isinstance(ubsih__cssvw, errors.ForceLiteralArg):
                    raise ubsih__cssvw
                itgby__sxt = ubsih__cssvw
                bkjpu__jvpzq = None
            else:
                break
        else:
            hcpsq__mvp = tuple([_unlit_non_poison(a) for a in args])
            izopk__yletx = {gtily__cuckl: _unlit_non_poison(jdp__xtjj) for 
                gtily__cuckl, jdp__xtjj in kws.items()}
            udtb__rnwlh = hcpsq__mvp == args and kws == izopk__yletx
            if not udtb__rnwlh and bkjpu__jvpzq is None:
                try:
                    bkjpu__jvpzq = dswbr__qjaev.apply(hcpsq__mvp, izopk__yletx)
                except Exception as ubsih__cssvw:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        ubsih__cssvw, errors.NumbaError):
                        raise ubsih__cssvw
                    if isinstance(ubsih__cssvw, errors.ForceLiteralArg):
                        if dswbr__qjaev.prefer_literal:
                            raise ubsih__cssvw
                    dux__cpl = ubsih__cssvw
                else:
                    break
    if bkjpu__jvpzq is None and (dux__cpl is not None or itgby__sxt is not None
        ):
        jni__qvgk = '- Resolution failure for {} arguments:\n{}\n'
        cbf__dpvtw = _termcolor.highlight(jni__qvgk)
        if numba.core.config.DEVELOPER_MODE:
            jklrj__bkbpz = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    iqz__upx = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    iqz__upx = ['']
                fzfg__mzek = '\n{}'.format(2 * jklrj__bkbpz)
                xxnn__tif = _termcolor.reset(fzfg__mzek + fzfg__mzek.join(
                    _bt_as_lines(iqz__upx)))
                return _termcolor.reset(xxnn__tif)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            clhbr__arcrg = str(e)
            clhbr__arcrg = clhbr__arcrg if clhbr__arcrg else str(repr(e)
                ) + add_bt(e)
            iuw__yxnsh = errors.TypingError(textwrap.dedent(clhbr__arcrg))
            return cbf__dpvtw.format(literalness, str(iuw__yxnsh))
        import bodo
        if isinstance(itgby__sxt, bodo.utils.typing.BodoError):
            raise itgby__sxt
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', itgby__sxt) +
                nested_msg('non-literal', dux__cpl))
        else:
            if 'missing a required argument' in itgby__sxt.msg:
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
            raise errors.TypingError(msg, loc=itgby__sxt.loc)
    return bkjpu__jvpzq


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
    nse__juteg = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=nse__juteg)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            nqxzx__woz = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), nqxzx__woz)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    jfi__tug = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            jfi__tug.append(types.Omitted(a.value))
        else:
            jfi__tug.append(self.typeof_pyval(a))
    escdi__yctf = None
    try:
        error = None
        escdi__yctf = self.compile(tuple(jfi__tug))
    except errors.ForceLiteralArg as e:
        xcid__lefwi = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if xcid__lefwi:
            oykd__kmiwt = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            azdk__nelrz = ', '.join('Arg #{} is {}'.format(i, args[i]) for
                i in sorted(xcid__lefwi))
            raise errors.CompilerError(oykd__kmiwt.format(azdk__nelrz))
        fey__ekh = []
        try:
            for i, jdp__xtjj in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        fey__ekh.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        fey__ekh.append(types.literal(args[i]))
                else:
                    fey__ekh.append(args[i])
            args = fey__ekh
        except (OSError, FileNotFoundError) as fslx__afefw:
            error = FileNotFoundError(str(fslx__afefw) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                escdi__yctf = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        ifdfz__ysm = []
        for i, tkrs__pfluq in enumerate(args):
            val = tkrs__pfluq.value if isinstance(tkrs__pfluq, numba.core.
                dispatcher.OmittedArg) else tkrs__pfluq
            try:
                tvtyn__haxld = typeof(val, Purpose.argument)
            except ValueError as vupm__vzw:
                ifdfz__ysm.append((i, str(vupm__vzw)))
            else:
                if tvtyn__haxld is None:
                    ifdfz__ysm.append((i,
                        f'cannot determine Numba type of value {val}'))
        if ifdfz__ysm:
            xkkg__sjpd = '\n'.join(f'- argument {i}: {bjdu__qsgpf}' for i,
                bjdu__qsgpf in ifdfz__ysm)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{xkkg__sjpd}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                vri__xyno = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                kpqo__rhf = False
                for kmdfx__ktq in vri__xyno:
                    if kmdfx__ktq in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        kpqo__rhf = True
                        break
                if not kpqo__rhf:
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
                nqxzx__woz = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), nqxzx__woz)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return escdi__yctf


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
    for grq__mind in cres.library._codegen._engine._defined_symbols:
        if grq__mind.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in grq__mind and (
            'bodo_gb_udf_update_local' in grq__mind or 
            'bodo_gb_udf_combine' in grq__mind or 'bodo_gb_udf_eval' in
            grq__mind or 'bodo_gb_apply_general_udfs' in grq__mind):
            gb_agg_cfunc_addr[grq__mind
                ] = cres.library.get_pointer_to_function(grq__mind)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for grq__mind in cres.library._codegen._engine._defined_symbols:
        if grq__mind.startswith('cfunc') and ('get_join_cond_addr' not in
            grq__mind or 'bodo_join_gen_cond' in grq__mind):
            join_gen_cond_cfunc_addr[grq__mind
                ] = cres.library.get_pointer_to_function(grq__mind)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    jylh__llm = self._get_dispatcher_for_current_target()
    if jylh__llm is not self:
        return jylh__llm.compile(sig)
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
            ntmvy__airis = self.overloads.get(tuple(args))
            if ntmvy__airis is not None:
                return ntmvy__airis.entry_point
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
            hdcq__mrerz = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=hdcq__mrerz):
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
                umbxd__zcpmb = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in umbxd__zcpmb:
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
    rhip__xdazz = self._final_module
    kolhp__ttmuf = []
    iouj__ckw = 0
    for fn in rhip__xdazz.functions:
        iouj__ckw += 1
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
            kolhp__ttmuf.append(fn.name)
    if iouj__ckw == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if kolhp__ttmuf:
        rhip__xdazz = rhip__xdazz.clone()
        for name in kolhp__ttmuf:
            rhip__xdazz.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = rhip__xdazz
    return rhip__xdazz


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
    for bqkt__gri in self.constraints:
        loc = bqkt__gri.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                bqkt__gri(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                sxw__wmoua = numba.core.errors.TypingError(str(e), loc=
                    bqkt__gri.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(sxw__wmoua, e))
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
                    sxw__wmoua = numba.core.errors.TypingError(msg.format(
                        con=bqkt__gri, err=str(e)), loc=bqkt__gri.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(sxw__wmoua, e))
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
    for rkrs__xfkw in self._failures.values():
        for mixr__decjw in rkrs__xfkw:
            if isinstance(mixr__decjw.error, ForceLiteralArg):
                raise mixr__decjw.error
            if isinstance(mixr__decjw.error, bodo.utils.typing.BodoError):
                raise mixr__decjw.error
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
    zny__uedox = False
    edcon__tcpjb = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        uihys__ofrgl = set()
        ixb__fspbe = lives & alias_set
        for jdp__xtjj in ixb__fspbe:
            uihys__ofrgl |= alias_map[jdp__xtjj]
        lives_n_aliases = lives | uihys__ofrgl | arg_aliases
        if type(stmt) in remove_dead_extensions:
            puanf__wcvu = remove_dead_extensions[type(stmt)]
            stmt = puanf__wcvu(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                zny__uedox = True
                continue
        if isinstance(stmt, ir.Assign):
            rlji__dxhh = stmt.target
            zofpg__iml = stmt.value
            if rlji__dxhh.name not in lives:
                if has_no_side_effect(zofpg__iml, lives_n_aliases, call_table):
                    zny__uedox = True
                    continue
                if isinstance(zofpg__iml, ir.Expr
                    ) and zofpg__iml.op == 'call' and call_table[zofpg__iml
                    .func.name] == ['astype']:
                    kgfpr__oisu = guard(get_definition, func_ir, zofpg__iml
                        .func)
                    if (kgfpr__oisu is not None and kgfpr__oisu.op ==
                        'getattr' and isinstance(typemap[kgfpr__oisu.value.
                        name], types.Array) and kgfpr__oisu.attr == 'astype'):
                        zny__uedox = True
                        continue
            if saved_array_analysis and rlji__dxhh.name in lives and is_expr(
                zofpg__iml, 'getattr'
                ) and zofpg__iml.attr == 'shape' and is_array_typ(typemap[
                zofpg__iml.value.name]) and zofpg__iml.value.name not in lives:
                ilc__csyq = {jdp__xtjj: gtily__cuckl for gtily__cuckl,
                    jdp__xtjj in func_ir.blocks.items()}
                if block in ilc__csyq:
                    hst__uhnup = ilc__csyq[block]
                    kjbh__qgryw = saved_array_analysis.get_equiv_set(hst__uhnup
                        )
                    lar__ccg = kjbh__qgryw.get_equiv_set(zofpg__iml.value)
                    if lar__ccg is not None:
                        for jdp__xtjj in lar__ccg:
                            if jdp__xtjj.endswith('#0'):
                                jdp__xtjj = jdp__xtjj[:-2]
                            if jdp__xtjj in typemap and is_array_typ(typemap
                                [jdp__xtjj]) and jdp__xtjj in lives:
                                zofpg__iml.value = ir.Var(zofpg__iml.value.
                                    scope, jdp__xtjj, zofpg__iml.value.loc)
                                zny__uedox = True
                                break
            if isinstance(zofpg__iml, ir.Var
                ) and rlji__dxhh.name == zofpg__iml.name:
                zny__uedox = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                zny__uedox = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            ftqze__djkyw = analysis.ir_extension_usedefs[type(stmt)]
            tndre__rpe, qfjom__ejqvj = ftqze__djkyw(stmt)
            lives -= qfjom__ejqvj
            lives |= tndre__rpe
        else:
            lives |= {jdp__xtjj.name for jdp__xtjj in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                vclko__qbetm = set()
                if isinstance(zofpg__iml, ir.Expr):
                    vclko__qbetm = {jdp__xtjj.name for jdp__xtjj in
                        zofpg__iml.list_vars()}
                if rlji__dxhh.name not in vclko__qbetm:
                    lives.remove(rlji__dxhh.name)
        edcon__tcpjb.append(stmt)
    edcon__tcpjb.reverse()
    block.body = edcon__tcpjb
    return zny__uedox


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            mrdop__wiaq, = args
            if isinstance(mrdop__wiaq, types.IterableType):
                dtype = mrdop__wiaq.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), mrdop__wiaq)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    kpp__dcav = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (kpp__dcav, self.dtype)
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
        except LiteralTypingError as pojur__txfl:
            return
    try:
        return literal(value)
    except LiteralTypingError as pojur__txfl:
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
        vgt__ystpt = py_func.__qualname__
    except AttributeError as pojur__txfl:
        vgt__ystpt = py_func.__name__
    lvt__ltjq = inspect.getfile(py_func)
    for cls in self._locator_classes:
        rlo__vlf = cls.from_function(py_func, lvt__ltjq)
        if rlo__vlf is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (vgt__ystpt, lvt__ltjq))
    self._locator = rlo__vlf
    gzer__iet = inspect.getfile(py_func)
    othl__fva = os.path.splitext(os.path.basename(gzer__iet))[0]
    if lvt__ltjq.startswith('<ipython-'):
        kror__quv = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', othl__fva, count=1)
        if kror__quv == othl__fva:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        othl__fva = kror__quv
    env__rugvg = '%s.%s' % (othl__fva, vgt__ystpt)
    erkn__mhnb = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(env__rugvg, erkn__mhnb
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    tbiwh__ibyce = list(filter(lambda a: self._istuple(a.name), args))
    if len(tbiwh__ibyce) == 2 and fn.__name__ == 'add':
        wfnn__qvja = self.typemap[tbiwh__ibyce[0].name]
        jycj__rnp = self.typemap[tbiwh__ibyce[1].name]
        if wfnn__qvja.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                tbiwh__ibyce[1]))
        if jycj__rnp.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                tbiwh__ibyce[0]))
        try:
            jgw__ckl = [equiv_set.get_shape(x) for x in tbiwh__ibyce]
            if None in jgw__ckl:
                return None
            big__avi = sum(jgw__ckl, ())
            return ArrayAnalysis.AnalyzeResult(shape=big__avi)
        except GuardException as pojur__txfl:
            return None
    hth__yms = list(filter(lambda a: self._isarray(a.name), args))
    require(len(hth__yms) > 0)
    egy__mzud = [x.name for x in hth__yms]
    dmw__nkmuo = [self.typemap[x.name].ndim for x in hth__yms]
    cleeu__wltg = max(dmw__nkmuo)
    require(cleeu__wltg > 0)
    jgw__ckl = [equiv_set.get_shape(x) for x in hth__yms]
    if any(a is None for a in jgw__ckl):
        return ArrayAnalysis.AnalyzeResult(shape=hth__yms[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, hth__yms))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, jgw__ckl,
        egy__mzud)


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
    rllo__fsr = code_obj.code
    vrwkk__fdi = len(rllo__fsr.co_freevars)
    mone__xqt = rllo__fsr.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        uaql__seuwr, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        mone__xqt = [jdp__xtjj.name for jdp__xtjj in uaql__seuwr]
    odq__gkeh = caller_ir.func_id.func.__globals__
    try:
        odq__gkeh = getattr(code_obj, 'globals', odq__gkeh)
    except KeyError as pojur__txfl:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    bbilb__ctnjy = []
    for x in mone__xqt:
        try:
            ztgv__felya = caller_ir.get_definition(x)
        except KeyError as pojur__txfl:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(ztgv__felya, (ir.Const, ir.Global, ir.FreeVar)):
            val = ztgv__felya.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                ula__nme = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                odq__gkeh[ula__nme] = bodo.jit(distributed=False)(val)
                odq__gkeh[ula__nme].is_nested_func = True
                val = ula__nme
            if isinstance(val, CPUDispatcher):
                ula__nme = ir_utils.mk_unique_var('nested_func').replace('.',
                    '_')
                odq__gkeh[ula__nme] = val
                val = ula__nme
            bbilb__ctnjy.append(val)
        elif isinstance(ztgv__felya, ir.Expr
            ) and ztgv__felya.op == 'make_function':
            scge__nhzn = convert_code_obj_to_function(ztgv__felya, caller_ir)
            ula__nme = ir_utils.mk_unique_var('nested_func').replace('.', '_')
            odq__gkeh[ula__nme] = bodo.jit(distributed=False)(scge__nhzn)
            odq__gkeh[ula__nme].is_nested_func = True
            bbilb__ctnjy.append(ula__nme)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    gzyfd__nra = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        bbilb__ctnjy)])
    ywy__qotim = ','.join([('c_%d' % i) for i in range(vrwkk__fdi)])
    qzs__tbb = list(rllo__fsr.co_varnames)
    xeo__jxe = 0
    rovl__swbiu = rllo__fsr.co_argcount
    qglb__qhd = caller_ir.get_definition(code_obj.defaults)
    if qglb__qhd is not None:
        if isinstance(qglb__qhd, tuple):
            d = [caller_ir.get_definition(x).value for x in qglb__qhd]
            xuc__gai = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in qglb__qhd.items]
            xuc__gai = tuple(d)
        xeo__jxe = len(xuc__gai)
    tjll__ajp = rovl__swbiu - xeo__jxe
    zdl__ldiyk = ','.join([('%s' % qzs__tbb[i]) for i in range(tjll__ajp)])
    if xeo__jxe:
        txmp__kstld = [('%s = %s' % (qzs__tbb[i + tjll__ajp], xuc__gai[i])) for
            i in range(xeo__jxe)]
        zdl__ldiyk += ', '
        zdl__ldiyk += ', '.join(txmp__kstld)
    return _create_function_from_code_obj(rllo__fsr, gzyfd__nra, zdl__ldiyk,
        ywy__qotim, odq__gkeh)


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
    for dglr__rex, (zhgf__tel, mfs__rhyd) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % mfs__rhyd)
            jbj__ksre = _pass_registry.get(zhgf__tel).pass_inst
            if isinstance(jbj__ksre, CompilerPass):
                self._runPass(dglr__rex, jbj__ksre, state)
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
                    pipeline_name, mfs__rhyd)
                rfjjy__oivp = self._patch_error(msg, e)
                raise rfjjy__oivp
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
    zjedz__hvn = None
    qfjom__ejqvj = {}

    def lookup(var, already_seen, varonly=True):
        val = qfjom__ejqvj.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    hsuoq__gzvj = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        rlji__dxhh = stmt.target
        zofpg__iml = stmt.value
        qfjom__ejqvj[rlji__dxhh.name] = zofpg__iml
        if isinstance(zofpg__iml, ir.Var) and zofpg__iml.name in qfjom__ejqvj:
            zofpg__iml = lookup(zofpg__iml, set())
        if isinstance(zofpg__iml, ir.Expr):
            xrewt__xfp = set(lookup(jdp__xtjj, set(), True).name for
                jdp__xtjj in zofpg__iml.list_vars())
            if name in xrewt__xfp:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(zofpg__iml)]
                zchr__mxxgu = [x for x, ukfr__fuhpe in args if ukfr__fuhpe.
                    name != name]
                args = [(x, ukfr__fuhpe) for x, ukfr__fuhpe in args if x !=
                    ukfr__fuhpe.name]
                oiu__tpdic = dict(args)
                if len(zchr__mxxgu) == 1:
                    oiu__tpdic[zchr__mxxgu[0]] = ir.Var(rlji__dxhh.scope, 
                        name + '#init', rlji__dxhh.loc)
                replace_vars_inner(zofpg__iml, oiu__tpdic)
                zjedz__hvn = nodes[i:]
                break
    return zjedz__hvn


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
        sca__dhamp = expand_aliases({jdp__xtjj.name for jdp__xtjj in stmt.
            list_vars()}, alias_map, arg_aliases)
        xjg__ltoeh = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        pyaq__idye = expand_aliases({jdp__xtjj.name for jdp__xtjj in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        epoi__nli = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(xjg__ltoeh & pyaq__idye | epoi__nli & sca__dhamp) == 0:
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
    obogm__nwj = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            obogm__nwj.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                obogm__nwj.update(get_parfor_writes(stmt, func_ir))
    return obogm__nwj


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    obogm__nwj = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        obogm__nwj.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        obogm__nwj = {jdp__xtjj.name for jdp__xtjj in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        obogm__nwj = {jdp__xtjj.name for jdp__xtjj in stmt.get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            obogm__nwj.update({jdp__xtjj.name for jdp__xtjj in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        cgz__hmfn = guard(find_callname, func_ir, stmt.value)
        if cgz__hmfn in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            obogm__nwj.add(stmt.value.args[0].name)
        if cgz__hmfn == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            obogm__nwj.add(stmt.value.args[1].name)
    return obogm__nwj


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
        puanf__wcvu = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        bcr__yiyx = puanf__wcvu.format(self, msg)
        self.args = bcr__yiyx,
    else:
        puanf__wcvu = _termcolor.errmsg('{0}')
        bcr__yiyx = puanf__wcvu.format(self)
        self.args = bcr__yiyx,
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
        for jied__gyli in options['distributed']:
            dist_spec[jied__gyli] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for jied__gyli in options['distributed_block']:
            dist_spec[jied__gyli] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    uuiw__eekql = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, igw__exs in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(igw__exs)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    xzrlg__sltur = {}
    for qdwj__mwi in reversed(inspect.getmro(cls)):
        xzrlg__sltur.update(qdwj__mwi.__dict__)
    lncdw__hvwp, xfyqv__xgnyh, higa__myb, uuu__txkl = {}, {}, {}, {}
    for gtily__cuckl, jdp__xtjj in xzrlg__sltur.items():
        if isinstance(jdp__xtjj, pytypes.FunctionType):
            lncdw__hvwp[gtily__cuckl] = jdp__xtjj
        elif isinstance(jdp__xtjj, property):
            xfyqv__xgnyh[gtily__cuckl] = jdp__xtjj
        elif isinstance(jdp__xtjj, staticmethod):
            higa__myb[gtily__cuckl] = jdp__xtjj
        else:
            uuu__txkl[gtily__cuckl] = jdp__xtjj
    utwyz__ghuhx = (set(lncdw__hvwp) | set(xfyqv__xgnyh) | set(higa__myb)
        ) & set(spec)
    if utwyz__ghuhx:
        raise NameError('name shadowing: {0}'.format(', '.join(utwyz__ghuhx)))
    mzfd__vzlb = uuu__txkl.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(uuu__txkl)
    if uuu__txkl:
        msg = 'class members are not yet supported: {0}'
        laxot__ewbv = ', '.join(uuu__txkl.keys())
        raise TypeError(msg.format(laxot__ewbv))
    for gtily__cuckl, jdp__xtjj in xfyqv__xgnyh.items():
        if jdp__xtjj.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(
                gtily__cuckl))
    jit_methods = {gtily__cuckl: bodo.jit(returns_maybe_distributed=
        uuiw__eekql)(jdp__xtjj) for gtily__cuckl, jdp__xtjj in lncdw__hvwp.
        items()}
    jit_props = {}
    for gtily__cuckl, jdp__xtjj in xfyqv__xgnyh.items():
        lhxsh__wxu = {}
        if jdp__xtjj.fget:
            lhxsh__wxu['get'] = bodo.jit(jdp__xtjj.fget)
        if jdp__xtjj.fset:
            lhxsh__wxu['set'] = bodo.jit(jdp__xtjj.fset)
        jit_props[gtily__cuckl] = lhxsh__wxu
    jit_static_methods = {gtily__cuckl: bodo.jit(jdp__xtjj.__func__) for 
        gtily__cuckl, jdp__xtjj in higa__myb.items()}
    auej__cjpzp = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    qktp__pdjfi = dict(class_type=auej__cjpzp, __doc__=mzfd__vzlb)
    qktp__pdjfi.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), qktp__pdjfi)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, auej__cjpzp)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(auej__cjpzp, typingctx, targetctx).register()
    as_numba_type.register(cls, auej__cjpzp.instance_type)
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
    mqb__xmx = ','.join('{0}:{1}'.format(gtily__cuckl, jdp__xtjj) for 
        gtily__cuckl, jdp__xtjj in struct.items())
    bqdcv__roqj = ','.join('{0}:{1}'.format(gtily__cuckl, jdp__xtjj) for 
        gtily__cuckl, jdp__xtjj in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), mqb__xmx, bqdcv__roqj)
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
    veqmo__uxm = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if veqmo__uxm is None:
        return
    arxs__tnvm, tid__dpvq = veqmo__uxm
    for a in itertools.chain(arxs__tnvm, tid__dpvq.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, arxs__tnvm, tid__dpvq)
    except ForceLiteralArg as e:
        cql__rwhk = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(cql__rwhk, self.kws)
        gbsz__wiyp = set()
        vgczf__whu = set()
        limms__hxgns = {}
        for dglr__rex in e.requested_args:
            ujbhl__acy = typeinfer.func_ir.get_definition(folded[dglr__rex])
            if isinstance(ujbhl__acy, ir.Arg):
                gbsz__wiyp.add(ujbhl__acy.index)
                if ujbhl__acy.index in e.file_infos:
                    limms__hxgns[ujbhl__acy.index] = e.file_infos[ujbhl__acy
                        .index]
            else:
                vgczf__whu.add(dglr__rex)
        if vgczf__whu:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif gbsz__wiyp:
            raise ForceLiteralArg(gbsz__wiyp, loc=self.loc, file_infos=
                limms__hxgns)
    if sig is None:
        kqrw__iojs = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in arxs__tnvm]
        args += [('%s=%s' % (gtily__cuckl, jdp__xtjj)) for gtily__cuckl,
            jdp__xtjj in sorted(tid__dpvq.items())]
        whrql__mcwtj = kqrw__iojs.format(fnty, ', '.join(map(str, args)))
        zurnh__zjar = context.explain_function_type(fnty)
        msg = '\n'.join([whrql__mcwtj, zurnh__zjar])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        cuue__idt = context.unify_pairs(sig.recvr, fnty.this)
        if cuue__idt is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if cuue__idt is not None and cuue__idt.is_precise():
            uqckl__aolp = fnty.copy(this=cuue__idt)
            typeinfer.propagate_refined_type(self.func, uqckl__aolp)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            qyz__bntvp = target.getone()
            if context.unify_pairs(qyz__bntvp, sig.return_type) == qyz__bntvp:
                sig = sig.replace(return_type=qyz__bntvp)
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
        oykd__kmiwt = '*other* must be a {} but got a {} instead'
        raise TypeError(oykd__kmiwt.format(ForceLiteralArg, type(other)))
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
    ulvz__hrgnv = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for gtily__cuckl, jdp__xtjj in kwargs.items():
        vklhj__tcoz = None
        try:
            rgc__hlo = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var(
                'dummy'), loc)
            func_ir._definitions[rgc__hlo.name] = [jdp__xtjj]
            vklhj__tcoz = get_const_value_inner(func_ir, rgc__hlo)
            func_ir._definitions.pop(rgc__hlo.name)
            if isinstance(vklhj__tcoz, str):
                vklhj__tcoz = sigutils._parse_signature_string(vklhj__tcoz)
            if isinstance(vklhj__tcoz, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {gtily__cuckl} is annotated as type class {vklhj__tcoz}."""
                    )
            assert isinstance(vklhj__tcoz, types.Type)
            if isinstance(vklhj__tcoz, (types.List, types.Set)):
                vklhj__tcoz = vklhj__tcoz.copy(reflected=False)
            ulvz__hrgnv[gtily__cuckl] = vklhj__tcoz
        except BodoError as pojur__txfl:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(vklhj__tcoz, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(jdp__xtjj, ir.Global):
                    msg = f'Global {jdp__xtjj.name!r} is not defined.'
                if isinstance(jdp__xtjj, ir.FreeVar):
                    msg = f'Freevar {jdp__xtjj.name!r} is not defined.'
            if isinstance(jdp__xtjj, ir.Expr) and jdp__xtjj.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=gtily__cuckl, msg=msg, loc=loc)
    for name, typ in ulvz__hrgnv.items():
        self._legalize_arg_type(name, typ, loc)
    return ulvz__hrgnv


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
    aiuc__halm = inst.arg
    assert aiuc__halm > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(aiuc__halm)]))
    tmps = [state.make_temp() for _ in range(aiuc__halm - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    ggf__bcan = ir.Global('format', format, loc=self.loc)
    self.store(value=ggf__bcan, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    ntbi__jgdo = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=ntbi__jgdo, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    aiuc__halm = inst.arg
    assert aiuc__halm > 0, 'invalid BUILD_STRING count'
    bnly__assa = self.get(strings[0])
    for other, pry__jwymo in zip(strings[1:], tmps):
        other = self.get(other)
        aqzg__smjbk = ir.Expr.binop(operator.add, lhs=bnly__assa, rhs=other,
            loc=self.loc)
        self.store(aqzg__smjbk, pry__jwymo)
        bnly__assa = self.get(pry__jwymo)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    aaqk__grxj = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, aaqk__grxj])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    urx__qsa = mk_unique_var(f'{var_name}')
    ezgkm__ecgws = urx__qsa.replace('<', '_').replace('>', '_')
    ezgkm__ecgws = ezgkm__ecgws.replace('.', '_').replace('$', '_v')
    return ezgkm__ecgws


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
                zwkco__awzp = get_overload_const_str(val2)
                if zwkco__awzp != 'ns':
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
        jsm__qcw = states['defmap']
        if len(jsm__qcw) == 0:
            ufst__saxs = assign.target
            numba.core.ssa._logger.debug('first assign: %s', ufst__saxs)
            if ufst__saxs.name not in scope.localvars:
                ufst__saxs = scope.define(assign.target.name, loc=assign.loc)
        else:
            ufst__saxs = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=ufst__saxs, value=assign.value, loc=
            assign.loc)
        jsm__qcw[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    dgzgd__ctwnq = []
    for gtily__cuckl, jdp__xtjj in typing.npydecl.registry.globals:
        if gtily__cuckl == func:
            dgzgd__ctwnq.append(jdp__xtjj)
    for gtily__cuckl, jdp__xtjj in typing.templates.builtin_registry.globals:
        if gtily__cuckl == func:
            dgzgd__ctwnq.append(jdp__xtjj)
    if len(dgzgd__ctwnq) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return dgzgd__ctwnq


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    vxf__llp = {}
    lpqbh__fulxe = find_topo_order(blocks)
    pqga__tvovl = {}
    for hst__uhnup in lpqbh__fulxe:
        block = blocks[hst__uhnup]
        edcon__tcpjb = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                rlji__dxhh = stmt.target.name
                zofpg__iml = stmt.value
                if (zofpg__iml.op == 'getattr' and zofpg__iml.attr in
                    arr_math and isinstance(typemap[zofpg__iml.value.name],
                    types.npytypes.Array)):
                    zofpg__iml = stmt.value
                    bmqr__vmsaq = zofpg__iml.value
                    vxf__llp[rlji__dxhh] = bmqr__vmsaq
                    scope = bmqr__vmsaq.scope
                    loc = bmqr__vmsaq.loc
                    qairl__bmuag = ir.Var(scope, mk_unique_var('$np_g_var'),
                        loc)
                    typemap[qairl__bmuag.name] = types.misc.Module(numpy)
                    vlx__zwnrz = ir.Global('np', numpy, loc)
                    tsxi__flef = ir.Assign(vlx__zwnrz, qairl__bmuag, loc)
                    zofpg__iml.value = qairl__bmuag
                    edcon__tcpjb.append(tsxi__flef)
                    func_ir._definitions[qairl__bmuag.name] = [vlx__zwnrz]
                    func = getattr(numpy, zofpg__iml.attr)
                    xnp__wzje = get_np_ufunc_typ_lst(func)
                    pqga__tvovl[rlji__dxhh] = xnp__wzje
                if (zofpg__iml.op == 'call' and zofpg__iml.func.name in
                    vxf__llp):
                    bmqr__vmsaq = vxf__llp[zofpg__iml.func.name]
                    rkws__lqins = calltypes.pop(zofpg__iml)
                    mzidi__trji = rkws__lqins.args[:len(zofpg__iml.args)]
                    uzrx__hjexg = {name: typemap[jdp__xtjj.name] for name,
                        jdp__xtjj in zofpg__iml.kws}
                    nwwdr__gedgf = pqga__tvovl[zofpg__iml.func.name]
                    gahwq__mxet = None
                    for zpblo__ubso in nwwdr__gedgf:
                        try:
                            gahwq__mxet = zpblo__ubso.get_call_type(typingctx,
                                [typemap[bmqr__vmsaq.name]] + list(
                                mzidi__trji), uzrx__hjexg)
                            typemap.pop(zofpg__iml.func.name)
                            typemap[zofpg__iml.func.name] = zpblo__ubso
                            calltypes[zofpg__iml] = gahwq__mxet
                            break
                        except Exception as pojur__txfl:
                            pass
                    if gahwq__mxet is None:
                        raise TypeError(
                            f'No valid template found for {zofpg__iml.func.name}'
                            )
                    zofpg__iml.args = [bmqr__vmsaq] + zofpg__iml.args
            edcon__tcpjb.append(stmt)
        block.body = edcon__tcpjb


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    yzrk__jubu = ufunc.nin
    ffwe__eomh = ufunc.nout
    tjll__ajp = ufunc.nargs
    assert tjll__ajp == yzrk__jubu + ffwe__eomh
    if len(args) < yzrk__jubu:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), yzrk__jubu)
            )
    if len(args) > tjll__ajp:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), tjll__ajp))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    gkrnx__wjm = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    inuu__eix = max(gkrnx__wjm)
    oytva__dayv = args[yzrk__jubu:]
    if not all(d == inuu__eix for d in gkrnx__wjm[yzrk__jubu:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(rfi__xvcsl, types.ArrayCompatible) and not
        isinstance(rfi__xvcsl, types.Bytes) for rfi__xvcsl in oytva__dayv):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(rfi__xvcsl.mutable for rfi__xvcsl in oytva__dayv):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    lkxev__tgly = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    aqeh__ahtyj = None
    if inuu__eix > 0 and len(oytva__dayv) < ufunc.nout:
        aqeh__ahtyj = 'C'
        cqyof__fhlxi = [(x.layout if isinstance(x, types.ArrayCompatible) and
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in cqyof__fhlxi and 'F' in cqyof__fhlxi:
            aqeh__ahtyj = 'F'
    return lkxev__tgly, oytva__dayv, inuu__eix, aqeh__ahtyj


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
        zmi__spbnu = 'Dict.key_type cannot be of type {}'
        raise TypingError(zmi__spbnu.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        zmi__spbnu = 'Dict.value_type cannot be of type {}'
        raise TypingError(zmi__spbnu.format(valty))
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
    qui__ooh = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[qui__ooh]
        return impl, args
    except KeyError as pojur__txfl:
        pass
    impl, args = self._build_impl(qui__ooh, args, kws)
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
        pkrqj__edtze = find_topo_order(parfor.loop_body)
    pevqt__ymstn = pkrqj__edtze[0]
    kkc__hbv = {}
    _update_parfor_get_setitems(parfor.loop_body[pevqt__ymstn].body, parfor
        .index_var, alias_map, kkc__hbv, lives_n_aliases)
    maeq__njap = set(kkc__hbv.keys())
    for rfef__qnhm in pkrqj__edtze:
        if rfef__qnhm == pevqt__ymstn:
            continue
        for stmt in parfor.loop_body[rfef__qnhm].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            eymp__smqo = set(jdp__xtjj.name for jdp__xtjj in stmt.list_vars())
            owvv__igs = eymp__smqo & maeq__njap
            for a in owvv__igs:
                kkc__hbv.pop(a, None)
    for rfef__qnhm in pkrqj__edtze:
        if rfef__qnhm == pevqt__ymstn:
            continue
        block = parfor.loop_body[rfef__qnhm]
        eain__mlii = kkc__hbv.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            eain__mlii, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    fmzu__epgpq = max(blocks.keys())
    gfz__pswau, fvrrh__rte = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    xtntg__csyn = ir.Jump(gfz__pswau, ir.Loc('parfors_dummy', -1))
    blocks[fmzu__epgpq].body.append(xtntg__csyn)
    xwtq__seqo = compute_cfg_from_blocks(blocks)
    mnp__orjez = compute_use_defs(blocks)
    kovru__fjw = compute_live_map(xwtq__seqo, blocks, mnp__orjez.usemap,
        mnp__orjez.defmap)
    alias_set = set(alias_map.keys())
    for hst__uhnup, block in blocks.items():
        edcon__tcpjb = []
        bxmsn__icq = {jdp__xtjj.name for jdp__xtjj in block.terminator.
            list_vars()}
        for wro__locbr, nkq__cwvi in xwtq__seqo.successors(hst__uhnup):
            bxmsn__icq |= kovru__fjw[wro__locbr]
        for stmt in reversed(block.body):
            uihys__ofrgl = bxmsn__icq & alias_set
            for jdp__xtjj in uihys__ofrgl:
                bxmsn__icq |= alias_map[jdp__xtjj]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in bxmsn__icq and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                cgz__hmfn = guard(find_callname, func_ir, stmt.value)
                if cgz__hmfn == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in bxmsn__icq and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            bxmsn__icq |= {jdp__xtjj.name for jdp__xtjj in stmt.list_vars()}
            edcon__tcpjb.append(stmt)
        edcon__tcpjb.reverse()
        block.body = edcon__tcpjb
    typemap.pop(fvrrh__rte.name)
    blocks[fmzu__epgpq].body.pop()

    def trim_empty_parfor_branches(parfor):
        cax__xcjj = False
        blocks = parfor.loop_body.copy()
        for hst__uhnup, block in blocks.items():
            if len(block.body):
                oouws__fvpdh = block.body[-1]
                if isinstance(oouws__fvpdh, ir.Branch):
                    if len(blocks[oouws__fvpdh.truebr].body) == 1 and len(
                        blocks[oouws__fvpdh.falsebr].body) == 1:
                        okylx__pac = blocks[oouws__fvpdh.truebr].body[0]
                        bmczi__kas = blocks[oouws__fvpdh.falsebr].body[0]
                        if isinstance(okylx__pac, ir.Jump) and isinstance(
                            bmczi__kas, ir.Jump
                            ) and okylx__pac.target == bmczi__kas.target:
                            parfor.loop_body[hst__uhnup].body[-1] = ir.Jump(
                                okylx__pac.target, oouws__fvpdh.loc)
                            cax__xcjj = True
                    elif len(blocks[oouws__fvpdh.truebr].body) == 1:
                        okylx__pac = blocks[oouws__fvpdh.truebr].body[0]
                        if isinstance(okylx__pac, ir.Jump
                            ) and okylx__pac.target == oouws__fvpdh.falsebr:
                            parfor.loop_body[hst__uhnup].body[-1] = ir.Jump(
                                okylx__pac.target, oouws__fvpdh.loc)
                            cax__xcjj = True
                    elif len(blocks[oouws__fvpdh.falsebr].body) == 1:
                        bmczi__kas = blocks[oouws__fvpdh.falsebr].body[0]
                        if isinstance(bmczi__kas, ir.Jump
                            ) and bmczi__kas.target == oouws__fvpdh.truebr:
                            parfor.loop_body[hst__uhnup].body[-1] = ir.Jump(
                                bmczi__kas.target, oouws__fvpdh.loc)
                            cax__xcjj = True
        return cax__xcjj
    cax__xcjj = True
    while cax__xcjj:
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
        cax__xcjj = trim_empty_parfor_branches(parfor)
    vidf__rjvyq = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        vidf__rjvyq &= len(block.body) == 0
    if vidf__rjvyq:
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
    ntc__wjo = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                ntc__wjo += 1
                parfor = stmt
                hxbnh__jxn = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = hxbnh__jxn.scope
                loc = ir.Loc('parfors_dummy', -1)
                rdjgz__yvywn = ir.Var(scope, mk_unique_var('$const'), loc)
                hxbnh__jxn.body.append(ir.Assign(ir.Const(0, loc),
                    rdjgz__yvywn, loc))
                hxbnh__jxn.body.append(ir.Return(rdjgz__yvywn, loc))
                xwtq__seqo = compute_cfg_from_blocks(parfor.loop_body)
                for wlavh__pijnf in xwtq__seqo.dead_nodes():
                    del parfor.loop_body[wlavh__pijnf]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                hxbnh__jxn = parfor.loop_body[max(parfor.loop_body.keys())]
                hxbnh__jxn.body.pop()
                hxbnh__jxn.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return ntc__wjo


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
            ntmvy__airis = self.overloads.get(tuple(args))
            if ntmvy__airis is not None:
                return ntmvy__airis.entry_point
            self._pre_compile(args, return_type, flags)
            cadij__tkdaa = self.func_ir
            hdcq__mrerz = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=hdcq__mrerz):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=cadij__tkdaa, args=
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
        ksdfb__bvst = copy.deepcopy(flags)
        ksdfb__bvst.no_rewrites = True

        def compile_local(the_ir, the_flags):
            qnleu__xzvzw = pipeline_class(typingctx, targetctx, library,
                args, return_type, the_flags, locals)
            return qnleu__xzvzw.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        zab__hzsh = compile_local(func_ir, ksdfb__bvst)
        mnp__zznv = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    mnp__zznv = compile_local(func_ir, flags)
                except Exception as pojur__txfl:
                    pass
        if mnp__zznv is not None:
            cres = mnp__zznv
        else:
            cres = zab__hzsh
        return cres
    else:
        qnleu__xzvzw = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return qnleu__xzvzw.compile_ir(func_ir=func_ir, lifted=lifted,
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
    seuav__hjg = self.get_data_type(typ.dtype)
    nobp__mmajo = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        nobp__mmajo):
        yaamq__xtkz = ary.ctypes.data
        hrpw__wid = self.add_dynamic_addr(builder, yaamq__xtkz, info=str(
            type(yaamq__xtkz)))
        mmb__zlyk = self.add_dynamic_addr(builder, id(ary), info=str(type(ary))
            )
        self.global_arrays.append(ary)
    else:
        dllru__hauua = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            dllru__hauua = dllru__hauua.view('int64')
        val = bytearray(dllru__hauua.data)
        yqsxa__tvzi = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val
            )
        hrpw__wid = cgutils.global_constant(builder, '.const.array.data',
            yqsxa__tvzi)
        hrpw__wid.align = self.get_abi_alignment(seuav__hjg)
        mmb__zlyk = None
    qqim__zxcoq = self.get_value_type(types.intp)
    gvxg__wgw = [self.get_constant(types.intp, oor__kfn) for oor__kfn in
        ary.shape]
    bwe__ppe = lir.Constant(lir.ArrayType(qqim__zxcoq, len(gvxg__wgw)),
        gvxg__wgw)
    vjjhi__cpq = [self.get_constant(types.intp, oor__kfn) for oor__kfn in
        ary.strides]
    eine__ftp = lir.Constant(lir.ArrayType(qqim__zxcoq, len(vjjhi__cpq)),
        vjjhi__cpq)
    gbk__qly = self.get_constant(types.intp, ary.dtype.itemsize)
    gguc__zkale = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        gguc__zkale, gbk__qly, hrpw__wid.bitcast(self.get_value_type(types.
        CPointer(typ.dtype))), bwe__ppe, eine__ftp])


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
    lbopx__pfjp = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    svr__bgjmy = lir.Function(module, lbopx__pfjp, name='nrt_atomic_{0}'.
        format(op))
    [eafsq__xhi] = svr__bgjmy.args
    qcaho__jje = svr__bgjmy.append_basic_block()
    builder = lir.IRBuilder(qcaho__jje)
    sptts__ohlr = lir.Constant(_word_type, 1)
    if False:
        kzlq__aunm = builder.atomic_rmw(op, eafsq__xhi, sptts__ohlr,
            ordering=ordering)
        res = getattr(builder, op)(kzlq__aunm, sptts__ohlr)
        builder.ret(res)
    else:
        kzlq__aunm = builder.load(eafsq__xhi)
        jwruj__ole = getattr(builder, op)(kzlq__aunm, sptts__ohlr)
        uuk__osrv = builder.icmp_signed('!=', kzlq__aunm, lir.Constant(
            kzlq__aunm.type, -1))
        with cgutils.if_likely(builder, uuk__osrv):
            builder.store(jwruj__ole, eafsq__xhi)
        builder.ret(jwruj__ole)
    return svr__bgjmy


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
        afcdd__vtz = state.targetctx.codegen()
        state.library = afcdd__vtz.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    oeb__lji = state.func_ir
    typemap = state.typemap
    bgy__tiv = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    wnc__yzxy = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            oeb__lji, typemap, bgy__tiv, calltypes, mangler=targetctx.
            mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            sxh__pola = lowering.Lower(targetctx, library, fndesc, oeb__lji,
                metadata=metadata)
            sxh__pola.lower()
            if not flags.no_cpython_wrapper:
                sxh__pola.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(bgy__tiv, (types.Optional, types.Generator)):
                        pass
                    else:
                        sxh__pola.create_cfunc_wrapper()
            env = sxh__pola.env
            xsnyx__wltb = sxh__pola.call_helper
            del sxh__pola
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, xsnyx__wltb, cfunc=None, env=env
                )
        else:
            nfbir__szf = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(nfbir__szf, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, xsnyx__wltb, cfunc=
                nfbir__szf, env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        qfx__gffwk = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = qfx__gffwk - wnc__yzxy
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
        muvi__lphvw = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, muvi__lphvw),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            bxp__ksasd.do_break()
        jouuj__ncgjq = c.builder.icmp_signed('!=', muvi__lphvw, expected_typobj
            )
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(jouuj__ncgjq, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, muvi__lphvw)
                c.pyapi.decref(muvi__lphvw)
                bxp__ksasd.do_break()
        c.pyapi.decref(muvi__lphvw)
    owkpl__jlc, list = listobj.ListInstance.allocate_ex(c.context, c.
        builder, typ, size)
    with c.builder.if_else(owkpl__jlc, likely=True) as (ggu__eyl, sakdb__ddah):
        with ggu__eyl:
            list.size = size
            amhnf__ksx = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                amhnf__ksx), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        amhnf__ksx))
                    with cgutils.for_range(c.builder, size) as bxp__ksasd:
                        itemobj = c.pyapi.list_getitem(obj, bxp__ksasd.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        hgnoi__tna = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(hgnoi__tna.is_error, likely=
                            False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            bxp__ksasd.do_break()
                        list.setitem(bxp__ksasd.index, hgnoi__tna.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with sakdb__ddah:
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
    qui__xwcfb, spwss__dvi, clrb__knh, esqp__xowj, qkzsc__vjny = (
        compile_time_get_string_data(literal_string))
    rhip__xdazz = builder.module
    gv = context.insert_const_bytes(rhip__xdazz, qui__xwcfb)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        spwss__dvi), context.get_constant(types.int32, clrb__knh), context.
        get_constant(types.uint32, esqp__xowj), context.get_constant(
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
    whb__sjyp = None
    if isinstance(shape, types.Integer):
        whb__sjyp = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(oor__kfn, (types.Integer, types.IntEnumMember)) for
            oor__kfn in shape):
            whb__sjyp = len(shape)
    return whb__sjyp


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
            whb__sjyp = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if whb__sjyp == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(whb__sjyp))
        else:
            return name,
    elif isinstance(obj, ir.Const):
        if isinstance(obj.value, tuple):
            return obj.value
        else:
            return obj.value,
    elif isinstance(obj, tuple):

        def get_names(x):
            egy__mzud = self._get_names(x)
            if len(egy__mzud) != 0:
                return egy__mzud[0]
            return egy__mzud
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    egy__mzud = self._get_names(obj)
    if len(egy__mzud) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(egy__mzud[0])


def get_equiv_set(self, obj):
    egy__mzud = self._get_names(obj)
    if len(egy__mzud) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(egy__mzud[0])


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
    jwnz__hbau = []
    for xjwnp__yloe in func_ir.arg_names:
        if xjwnp__yloe in typemap and isinstance(typemap[xjwnp__yloe],
            types.containers.UniTuple) and typemap[xjwnp__yloe].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(xjwnp__yloe))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for ddt__jwc in func_ir.blocks.values():
        for stmt in ddt__jwc.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    yoipp__ryyaz = getattr(val, 'code', None)
                    if yoipp__ryyaz is not None:
                        if getattr(val, 'closure', None) is not None:
                            yyh__cim = '<creating a function from a closure>'
                            aqzg__smjbk = ''
                        else:
                            yyh__cim = yoipp__ryyaz.co_name
                            aqzg__smjbk = '(%s) ' % yyh__cim
                    else:
                        yyh__cim = '<could not ascertain use case>'
                        aqzg__smjbk = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (yyh__cim, aqzg__smjbk))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                znq__wrnd = False
                if isinstance(val, pytypes.FunctionType):
                    znq__wrnd = val in {numba.gdb, numba.gdb_init}
                if not znq__wrnd:
                    znq__wrnd = getattr(val, '_name', '') == 'gdb_internal'
                if znq__wrnd:
                    jwnz__hbau.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    irnz__robz = func_ir.get_definition(var)
                    cno__fkt = guard(find_callname, func_ir, irnz__robz)
                    if cno__fkt and cno__fkt[1] == 'numpy':
                        ty = getattr(numpy, cno__fkt[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    rrowv__kjsw = '' if var.startswith('$'
                        ) else "'{}' ".format(var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(rrowv__kjsw), loc=stmt.loc)
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
    if len(jwnz__hbau) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        apa__xbqsj = '\n'.join([x.strformat() for x in jwnz__hbau])
        raise errors.UnsupportedError(msg % apa__xbqsj)


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
    gtily__cuckl, jdp__xtjj = next(iter(val.items()))
    pyo__gdkw = typeof_impl(gtily__cuckl, c)
    ewss__wvjo = typeof_impl(jdp__xtjj, c)
    if pyo__gdkw is None or ewss__wvjo is None:
        raise ValueError(
            f'Cannot type dict element type {type(gtily__cuckl)}, {type(jdp__xtjj)}'
            )
    return types.DictType(pyo__gdkw, ewss__wvjo)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    yoxau__ptkmf = cgutils.alloca_once_value(c.builder, val)
    zkg__humwu = c.pyapi.object_hasattr_string(val, '_opaque')
    nuyuy__bjxl = c.builder.icmp_unsigned('==', zkg__humwu, lir.Constant(
        zkg__humwu.type, 0))
    ybs__nvnvz = typ.key_type
    qvjvs__tey = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(ybs__nvnvz, qvjvs__tey)

    def copy_dict(out_dict, in_dict):
        for gtily__cuckl, jdp__xtjj in in_dict.items():
            out_dict[gtily__cuckl] = jdp__xtjj
    with c.builder.if_then(nuyuy__bjxl):
        bjw__eynpp = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        fzfn__acmj = c.pyapi.call_function_objargs(bjw__eynpp, [])
        yba__psb = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(yba__psb, [fzfn__acmj, val])
        c.builder.store(fzfn__acmj, yoxau__ptkmf)
    val = c.builder.load(yoxau__ptkmf)
    wqz__jvlom = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    sdjfp__zwzqy = c.pyapi.object_type(val)
    ymb__kjzfl = c.builder.icmp_unsigned('==', sdjfp__zwzqy, wqz__jvlom)
    with c.builder.if_else(ymb__kjzfl) as (qvbm__cwyt, kkot__huw):
        with qvbm__cwyt:
            oybc__ihqdp = c.pyapi.object_getattr_string(val, '_opaque')
            ykxdg__xbji = types.MemInfoPointer(types.voidptr)
            hgnoi__tna = c.unbox(ykxdg__xbji, oybc__ihqdp)
            mi = hgnoi__tna.value
            jfi__tug = ykxdg__xbji, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *jfi__tug)
            wqa__hjqw = context.get_constant_null(jfi__tug[1])
            args = mi, wqa__hjqw
            wptm__ena, wzbvf__mhye = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, wzbvf__mhye)
            c.pyapi.decref(oybc__ihqdp)
            uuv__lfwa = c.builder.basic_block
        with kkot__huw:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", sdjfp__zwzqy, wqz__jvlom)
            xgx__wudh = c.builder.basic_block
    bdnc__qei = c.builder.phi(wzbvf__mhye.type)
    ticki__fuisa = c.builder.phi(wptm__ena.type)
    bdnc__qei.add_incoming(wzbvf__mhye, uuv__lfwa)
    bdnc__qei.add_incoming(wzbvf__mhye.type(None), xgx__wudh)
    ticki__fuisa.add_incoming(wptm__ena, uuv__lfwa)
    ticki__fuisa.add_incoming(cgutils.true_bit, xgx__wudh)
    c.pyapi.decref(wqz__jvlom)
    c.pyapi.decref(sdjfp__zwzqy)
    with c.builder.if_then(nuyuy__bjxl):
        c.pyapi.decref(val)
    return NativeValue(bdnc__qei, is_error=ticki__fuisa)


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
    hgx__lvnrb = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=hgx__lvnrb, name=updatevar)
    ionl__baxh = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=ionl__baxh, name=res)


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
        for gtily__cuckl, jdp__xtjj in other.items():
            d[gtily__cuckl] = jdp__xtjj
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
    aqzg__smjbk = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(aqzg__smjbk, res)


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
    vgm__ufm = PassManager(name)
    if state.func_ir is None:
        vgm__ufm.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            vgm__ufm.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        vgm__ufm.add_pass(FixupArgs, 'fix up args')
    vgm__ufm.add_pass(IRProcessing, 'processing IR')
    vgm__ufm.add_pass(WithLifting, 'Handle with contexts')
    vgm__ufm.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        vgm__ufm.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        vgm__ufm.add_pass(DeadBranchPrune, 'dead branch pruning')
        vgm__ufm.add_pass(GenericRewrites, 'nopython rewrites')
    vgm__ufm.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    vgm__ufm.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        vgm__ufm.add_pass(DeadBranchPrune, 'dead branch pruning')
    vgm__ufm.add_pass(FindLiterallyCalls, 'find literally calls')
    vgm__ufm.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        vgm__ufm.add_pass(ReconstructSSA, 'ssa')
    vgm__ufm.add_pass(LiteralPropagationSubPipelinePass, 'Literal propagation')
    vgm__ufm.finalize()
    return vgm__ufm


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
    a, jhsp__ielry = args
    if isinstance(a, types.List) and isinstance(jhsp__ielry, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(jhsp__ielry, types.List):
        return signature(jhsp__ielry, types.intp, jhsp__ielry)


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
        mif__cvwx, lwh__eyzq = 0, 1
    else:
        mif__cvwx, lwh__eyzq = 1, 0
    azlw__gfaa = ListInstance(context, builder, sig.args[mif__cvwx], args[
        mif__cvwx])
    omxdo__cqnia = azlw__gfaa.size
    rrey__ybxkn = args[lwh__eyzq]
    amhnf__ksx = lir.Constant(rrey__ybxkn.type, 0)
    rrey__ybxkn = builder.select(cgutils.is_neg_int(builder, rrey__ybxkn),
        amhnf__ksx, rrey__ybxkn)
    gguc__zkale = builder.mul(rrey__ybxkn, omxdo__cqnia)
    zdhzc__guobh = ListInstance.allocate(context, builder, sig.return_type,
        gguc__zkale)
    zdhzc__guobh.size = gguc__zkale
    with cgutils.for_range_slice(builder, amhnf__ksx, gguc__zkale,
        omxdo__cqnia, inc=True) as (ztqx__qfh, _):
        with cgutils.for_range(builder, omxdo__cqnia) as bxp__ksasd:
            value = azlw__gfaa.getitem(bxp__ksasd.index)
            zdhzc__guobh.setitem(builder.add(bxp__ksasd.index, ztqx__qfh),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, zdhzc__guobh
        .value)


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
    nttlh__kqgzt = first.unify(self, second)
    if nttlh__kqgzt is not None:
        return nttlh__kqgzt
    nttlh__kqgzt = second.unify(self, first)
    if nttlh__kqgzt is not None:
        return nttlh__kqgzt
    pdwd__pto = self.can_convert(fromty=first, toty=second)
    if pdwd__pto is not None and pdwd__pto <= Conversion.safe:
        return second
    pdwd__pto = self.can_convert(fromty=second, toty=first)
    if pdwd__pto is not None and pdwd__pto <= Conversion.safe:
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
    gguc__zkale = payload.used
    listobj = c.pyapi.list_new(gguc__zkale)
    owkpl__jlc = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(owkpl__jlc, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(
            gguc__zkale.type, 0))
        with payload._iterate() as bxp__ksasd:
            i = c.builder.load(index)
            item = bxp__ksasd.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return owkpl__jlc, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    xrdbi__snafl = h.type
    nvisp__ffun = self.mask
    dtype = self._ty.dtype
    nsmd__ikeee = context.typing_context
    fnty = nsmd__ikeee.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(nsmd__ikeee, (dtype, dtype), {})
    knxq__ewk = context.get_function(fnty, sig)
    iif__hteie = ir.Constant(xrdbi__snafl, 1)
    flvz__hdth = ir.Constant(xrdbi__snafl, 5)
    tkp__luh = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, nvisp__ffun))
    if for_insert:
        zsxit__akc = nvisp__ffun.type(-1)
        eys__vum = cgutils.alloca_once_value(builder, zsxit__akc)
    ripvs__sqgp = builder.append_basic_block('lookup.body')
    wwz__csmhk = builder.append_basic_block('lookup.found')
    nxvks__sdk = builder.append_basic_block('lookup.not_found')
    plh__tnjyy = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        xaju__vef = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, xaju__vef)):
            jdthi__vag = knxq__ewk(builder, (item, entry.key))
            with builder.if_then(jdthi__vag):
                builder.branch(wwz__csmhk)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, xaju__vef)):
            builder.branch(nxvks__sdk)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, xaju__vef)):
                yrno__wofs = builder.load(eys__vum)
                yrno__wofs = builder.select(builder.icmp_unsigned('==',
                    yrno__wofs, zsxit__akc), i, yrno__wofs)
                builder.store(yrno__wofs, eys__vum)
    with cgutils.for_range(builder, ir.Constant(xrdbi__snafl, numba.cpython
        .setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, iif__hteie)
        i = builder.and_(i, nvisp__ffun)
        builder.store(i, index)
    builder.branch(ripvs__sqgp)
    with builder.goto_block(ripvs__sqgp):
        i = builder.load(index)
        check_entry(i)
        zxq__flws = builder.load(tkp__luh)
        zxq__flws = builder.lshr(zxq__flws, flvz__hdth)
        i = builder.add(iif__hteie, builder.mul(i, flvz__hdth))
        i = builder.and_(nvisp__ffun, builder.add(i, zxq__flws))
        builder.store(i, index)
        builder.store(zxq__flws, tkp__luh)
        builder.branch(ripvs__sqgp)
    with builder.goto_block(nxvks__sdk):
        if for_insert:
            i = builder.load(index)
            yrno__wofs = builder.load(eys__vum)
            i = builder.select(builder.icmp_unsigned('==', yrno__wofs,
                zsxit__akc), i, yrno__wofs)
            builder.store(i, index)
        builder.branch(plh__tnjyy)
    with builder.goto_block(wwz__csmhk):
        builder.branch(plh__tnjyy)
    builder.position_at_end(plh__tnjyy)
    znq__wrnd = builder.phi(ir.IntType(1), 'found')
    znq__wrnd.add_incoming(cgutils.true_bit, wwz__csmhk)
    znq__wrnd.add_incoming(cgutils.false_bit, nxvks__sdk)
    return znq__wrnd, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    zwao__elam = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    dohf__doz = payload.used
    iif__hteie = ir.Constant(dohf__doz.type, 1)
    dohf__doz = payload.used = builder.add(dohf__doz, iif__hteie)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, zwao__elam), likely=True):
        payload.fill = builder.add(payload.fill, iif__hteie)
    if do_resize:
        self.upsize(dohf__doz)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    znq__wrnd, i = payload._lookup(item, h, for_insert=True)
    zjg__qqfsp = builder.not_(znq__wrnd)
    with builder.if_then(zjg__qqfsp):
        entry = payload.get_entry(i)
        zwao__elam = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        dohf__doz = payload.used
        iif__hteie = ir.Constant(dohf__doz.type, 1)
        dohf__doz = payload.used = builder.add(dohf__doz, iif__hteie)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, zwao__elam), likely=True):
            payload.fill = builder.add(payload.fill, iif__hteie)
        if do_resize:
            self.upsize(dohf__doz)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    dohf__doz = payload.used
    iif__hteie = ir.Constant(dohf__doz.type, 1)
    dohf__doz = payload.used = self._builder.sub(dohf__doz, iif__hteie)
    if do_resize:
        self.downsize(dohf__doz)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    hnq__ivkan = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, hnq__ivkan)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    omret__vjyby = payload
    owkpl__jlc = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(owkpl__jlc), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with omret__vjyby._iterate() as bxp__ksasd:
        entry = bxp__ksasd.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(omret__vjyby.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as bxp__ksasd:
        entry = bxp__ksasd.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    owkpl__jlc = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(owkpl__jlc), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    owkpl__jlc = cgutils.alloca_once_value(builder, cgutils.true_bit)
    xrdbi__snafl = context.get_value_type(types.intp)
    amhnf__ksx = ir.Constant(xrdbi__snafl, 0)
    iif__hteie = ir.Constant(xrdbi__snafl, 1)
    dqre__qbaxu = context.get_data_type(types.SetPayload(self._ty))
    nnsra__aplt = context.get_abi_sizeof(dqre__qbaxu)
    qwn__jmc = self._entrysize
    nnsra__aplt -= qwn__jmc
    joqbz__ncsxj, hxijw__fjsi = cgutils.muladd_with_overflow(builder,
        nentries, ir.Constant(xrdbi__snafl, qwn__jmc), ir.Constant(
        xrdbi__snafl, nnsra__aplt))
    with builder.if_then(hxijw__fjsi, likely=False):
        builder.store(cgutils.false_bit, owkpl__jlc)
    with builder.if_then(builder.load(owkpl__jlc), likely=True):
        if realloc:
            sbikk__xaj = self._set.meminfo
            eafsq__xhi = context.nrt.meminfo_varsize_alloc(builder,
                sbikk__xaj, size=joqbz__ncsxj)
            blipu__wtxr = cgutils.is_null(builder, eafsq__xhi)
        else:
            blu__too = _imp_dtor(context, builder.module, self._ty)
            sbikk__xaj = context.nrt.meminfo_new_varsize_dtor(builder,
                joqbz__ncsxj, builder.bitcast(blu__too, cgutils.voidptr_t))
            blipu__wtxr = cgutils.is_null(builder, sbikk__xaj)
        with builder.if_else(blipu__wtxr, likely=False) as (zsvgs__ikb,
            ggu__eyl):
            with zsvgs__ikb:
                builder.store(cgutils.false_bit, owkpl__jlc)
            with ggu__eyl:
                if not realloc:
                    self._set.meminfo = sbikk__xaj
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, joqbz__ncsxj, 255)
                payload.used = amhnf__ksx
                payload.fill = amhnf__ksx
                payload.finger = amhnf__ksx
                sxqtr__zcd = builder.sub(nentries, iif__hteie)
                payload.mask = sxqtr__zcd
    return builder.load(owkpl__jlc)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    owkpl__jlc = cgutils.alloca_once_value(builder, cgutils.true_bit)
    xrdbi__snafl = context.get_value_type(types.intp)
    amhnf__ksx = ir.Constant(xrdbi__snafl, 0)
    iif__hteie = ir.Constant(xrdbi__snafl, 1)
    dqre__qbaxu = context.get_data_type(types.SetPayload(self._ty))
    nnsra__aplt = context.get_abi_sizeof(dqre__qbaxu)
    qwn__jmc = self._entrysize
    nnsra__aplt -= qwn__jmc
    nvisp__ffun = src_payload.mask
    nentries = builder.add(iif__hteie, nvisp__ffun)
    joqbz__ncsxj = builder.add(ir.Constant(xrdbi__snafl, nnsra__aplt),
        builder.mul(ir.Constant(xrdbi__snafl, qwn__jmc), nentries))
    with builder.if_then(builder.load(owkpl__jlc), likely=True):
        blu__too = _imp_dtor(context, builder.module, self._ty)
        sbikk__xaj = context.nrt.meminfo_new_varsize_dtor(builder,
            joqbz__ncsxj, builder.bitcast(blu__too, cgutils.voidptr_t))
        blipu__wtxr = cgutils.is_null(builder, sbikk__xaj)
        with builder.if_else(blipu__wtxr, likely=False) as (zsvgs__ikb,
            ggu__eyl):
            with zsvgs__ikb:
                builder.store(cgutils.false_bit, owkpl__jlc)
            with ggu__eyl:
                self._set.meminfo = sbikk__xaj
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = amhnf__ksx
                payload.mask = nvisp__ffun
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, qwn__jmc)
                with src_payload._iterate() as bxp__ksasd:
                    context.nrt.incref(builder, self._ty.dtype, bxp__ksasd.
                        entry.key)
    return builder.load(owkpl__jlc)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    jogt__rqrz = context.get_value_type(types.voidptr)
    ezfam__ywzko = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [jogt__rqrz, ezfam__ywzko,
        jogt__rqrz])
    nse__juteg = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=nse__juteg)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        daqgq__zoi = builder.bitcast(fn.args[0], cgutils.voidptr_t.as_pointer()
            )
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, daqgq__zoi)
        with payload._iterate() as bxp__ksasd:
            entry = bxp__ksasd.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    ddfnv__oghma, = sig.args
    uaql__seuwr, = args
    dutg__mccdo = numba.core.imputils.call_len(context, builder,
        ddfnv__oghma, uaql__seuwr)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, dutg__mccdo)
    with numba.core.imputils.for_iter(context, builder, ddfnv__oghma,
        uaql__seuwr) as bxp__ksasd:
        inst.add(bxp__ksasd.value)
        context.nrt.decref(builder, set_type.dtype, bxp__ksasd.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    ddfnv__oghma = sig.args[1]
    uaql__seuwr = args[1]
    dutg__mccdo = numba.core.imputils.call_len(context, builder,
        ddfnv__oghma, uaql__seuwr)
    if dutg__mccdo is not None:
        pnvuf__xekid = builder.add(inst.payload.used, dutg__mccdo)
        inst.upsize(pnvuf__xekid)
    with numba.core.imputils.for_iter(context, builder, ddfnv__oghma,
        uaql__seuwr) as bxp__ksasd:
        lmzct__xlta = context.cast(builder, bxp__ksasd.value, ddfnv__oghma.
            dtype, inst.dtype)
        inst.add(lmzct__xlta)
        context.nrt.decref(builder, ddfnv__oghma.dtype, bxp__ksasd.value)
    if dutg__mccdo is not None:
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
    axkol__dykiy = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, axkol__dykiy, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    nfbir__szf = target_context.get_executable(library, fndesc, env)
    bwllp__vsipg = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=nfbir__szf, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return bwllp__vsipg


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
        tluy__dlg = MPI.COMM_WORLD
        ubsih__cssvw = None
        if tluy__dlg.Get_rank() == 0:
            try:
                iunlm__dprii = self.get_cache_path()
                os.makedirs(iunlm__dprii, exist_ok=True)
                tempfile.TemporaryFile(dir=iunlm__dprii).close()
            except Exception as e:
                ubsih__cssvw = e
        ubsih__cssvw = tluy__dlg.bcast(ubsih__cssvw)
        if isinstance(ubsih__cssvw, Exception):
            raise ubsih__cssvw
    numba.core.caching._CacheLocator.ensure_cache_path = _ensure_cache_path
