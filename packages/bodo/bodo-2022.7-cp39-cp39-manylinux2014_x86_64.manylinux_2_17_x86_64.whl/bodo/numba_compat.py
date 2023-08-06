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
    ieea__ipg = numba.core.bytecode.FunctionIdentity.from_function(func)
    sohre__qpvl = numba.core.interpreter.Interpreter(ieea__ipg)
    nzovz__vehmi = numba.core.bytecode.ByteCode(func_id=ieea__ipg)
    func_ir = sohre__qpvl.interpret(nzovz__vehmi)
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
        rwnjf__lzhx = InlineClosureCallPass(func_ir, numba.core.cpu.
            ParallelOptions(False), {}, False)
        rwnjf__lzhx.run()
    bol__aoqs = numba.core.postproc.PostProcessor(func_ir)
    bol__aoqs.run(emit_dels)
    return func_ir


if _check_numba_change:
    lines = inspect.getsource(numba.core.compiler.run_frontend)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '8c2477a793b2c08d56430997880974ac12c5570e69c9e54d37d694b322ea18b6':
        warnings.warn('numba.core.compiler.run_frontend has changed')
numba.core.compiler.run_frontend = run_frontend


def visit_vars_stmt(stmt, callback, cbdata):
    for t, iyby__xiaq in visit_vars_extensions.items():
        if isinstance(stmt, t):
            iyby__xiaq(stmt, callback, cbdata)
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
    lxfpi__xjcoh = ['ravel', 'transpose', 'reshape']
    for refm__hhhw in blocks.values():
        for dis__hjojn in refm__hhhw.body:
            if type(dis__hjojn) in alias_analysis_extensions:
                iyby__xiaq = alias_analysis_extensions[type(dis__hjojn)]
                iyby__xiaq(dis__hjojn, args, typemap, func_ir, alias_map,
                    arg_aliases)
            if isinstance(dis__hjojn, ir.Assign):
                baovm__pvlaz = dis__hjojn.value
                qjb__zmzx = dis__hjojn.target.name
                if is_immutable_type(qjb__zmzx, typemap):
                    continue
                if isinstance(baovm__pvlaz, ir.Var
                    ) and qjb__zmzx != baovm__pvlaz.name:
                    _add_alias(qjb__zmzx, baovm__pvlaz.name, alias_map,
                        arg_aliases)
                if isinstance(baovm__pvlaz, ir.Expr) and (baovm__pvlaz.op ==
                    'cast' or baovm__pvlaz.op in ['getitem', 'static_getitem']
                    ):
                    _add_alias(qjb__zmzx, baovm__pvlaz.value.name,
                        alias_map, arg_aliases)
                if isinstance(baovm__pvlaz, ir.Expr
                    ) and baovm__pvlaz.op == 'inplace_binop':
                    _add_alias(qjb__zmzx, baovm__pvlaz.lhs.name, alias_map,
                        arg_aliases)
                if isinstance(baovm__pvlaz, ir.Expr
                    ) and baovm__pvlaz.op == 'getattr' and baovm__pvlaz.attr in [
                    'T', 'ctypes', 'flat']:
                    _add_alias(qjb__zmzx, baovm__pvlaz.value.name,
                        alias_map, arg_aliases)
                if (isinstance(baovm__pvlaz, ir.Expr) and baovm__pvlaz.op ==
                    'getattr' and baovm__pvlaz.attr not in ['shape'] and 
                    baovm__pvlaz.value.name in arg_aliases):
                    _add_alias(qjb__zmzx, baovm__pvlaz.value.name,
                        alias_map, arg_aliases)
                if isinstance(baovm__pvlaz, ir.Expr
                    ) and baovm__pvlaz.op == 'getattr' and baovm__pvlaz.attr in (
                    'loc', 'iloc', 'iat', '_obj', 'obj', 'codes', '_df'):
                    _add_alias(qjb__zmzx, baovm__pvlaz.value.name,
                        alias_map, arg_aliases)
                if isinstance(baovm__pvlaz, ir.Expr) and baovm__pvlaz.op in (
                    'build_tuple', 'build_list', 'build_set'
                    ) and not is_immutable_type(qjb__zmzx, typemap):
                    for oin__dfmu in baovm__pvlaz.items:
                        _add_alias(qjb__zmzx, oin__dfmu.name, alias_map,
                            arg_aliases)
                if isinstance(baovm__pvlaz, ir.Expr
                    ) and baovm__pvlaz.op == 'call':
                    qhe__qgwh = guard(find_callname, func_ir, baovm__pvlaz,
                        typemap)
                    if qhe__qgwh is None:
                        continue
                    vgsmv__ohw, jixq__tiv = qhe__qgwh
                    if qhe__qgwh in alias_func_extensions:
                        tmt__mpzc = alias_func_extensions[qhe__qgwh]
                        tmt__mpzc(qjb__zmzx, baovm__pvlaz.args, alias_map,
                            arg_aliases)
                    if jixq__tiv == 'numpy' and vgsmv__ohw in lxfpi__xjcoh:
                        _add_alias(qjb__zmzx, baovm__pvlaz.args[0].name,
                            alias_map, arg_aliases)
                    if isinstance(jixq__tiv, ir.Var
                        ) and vgsmv__ohw in lxfpi__xjcoh:
                        _add_alias(qjb__zmzx, jixq__tiv.name, alias_map,
                            arg_aliases)
    czv__bnmx = copy.deepcopy(alias_map)
    for oin__dfmu in czv__bnmx:
        for ufagl__znop in czv__bnmx[oin__dfmu]:
            alias_map[oin__dfmu] |= alias_map[ufagl__znop]
        for ufagl__znop in czv__bnmx[oin__dfmu]:
            alias_map[ufagl__znop] = alias_map[oin__dfmu]
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
    yyrav__glvnp = compute_cfg_from_blocks(func_ir.blocks)
    uagw__geszx = compute_use_defs(func_ir.blocks)
    fiz__dab = compute_live_map(yyrav__glvnp, func_ir.blocks, uagw__geszx.
        usemap, uagw__geszx.defmap)
    gkkd__fde = True
    while gkkd__fde:
        gkkd__fde = False
        for jqh__btri, block in func_ir.blocks.items():
            lives = {oin__dfmu.name for oin__dfmu in block.terminator.
                list_vars()}
            for rwt__lhelf, dblup__ywiw in yyrav__glvnp.successors(jqh__btri):
                lives |= fiz__dab[rwt__lhelf]
            wug__jwzx = [block.terminator]
            for stmt in reversed(block.body[:-1]):
                if isinstance(stmt, ir.Assign):
                    qjb__zmzx = stmt.target
                    ymzx__wfvaa = stmt.value
                    if qjb__zmzx.name not in lives:
                        if isinstance(ymzx__wfvaa, ir.Expr
                            ) and ymzx__wfvaa.op == 'make_function':
                            continue
                        if isinstance(ymzx__wfvaa, ir.Expr
                            ) and ymzx__wfvaa.op == 'getattr':
                            continue
                        if isinstance(ymzx__wfvaa, ir.Const):
                            continue
                        if typemap and isinstance(typemap.get(qjb__zmzx,
                            None), types.Function):
                            continue
                        if isinstance(ymzx__wfvaa, ir.Expr
                            ) and ymzx__wfvaa.op == 'build_map':
                            continue
                        if isinstance(ymzx__wfvaa, ir.Expr
                            ) and ymzx__wfvaa.op == 'build_tuple':
                            continue
                    if isinstance(ymzx__wfvaa, ir.Var
                        ) and qjb__zmzx.name == ymzx__wfvaa.name:
                        continue
                if isinstance(stmt, ir.Del):
                    if stmt.value not in lives:
                        continue
                if type(stmt) in analysis.ir_extension_usedefs:
                    xkjnh__xcg = analysis.ir_extension_usedefs[type(stmt)]
                    nqexa__zbxgc, ongh__zsclh = xkjnh__xcg(stmt)
                    lives -= ongh__zsclh
                    lives |= nqexa__zbxgc
                else:
                    lives |= {oin__dfmu.name for oin__dfmu in stmt.list_vars()}
                    if isinstance(stmt, ir.Assign):
                        lives.remove(qjb__zmzx.name)
                wug__jwzx.append(stmt)
            wug__jwzx.reverse()
            if len(block.body) != len(wug__jwzx):
                gkkd__fde = True
            block.body = wug__jwzx


ir_utils.dead_code_elimination = mini_dce
numba.core.typed_passes.dead_code_elimination = mini_dce
numba.core.inline_closurecall.dead_code_elimination = mini_dce
from numba.core.cpu_options import InlineOptions


def make_overload_template(func, overload_func, jit_options, strict, inline,
    prefer_literal=False, **kwargs):
    xiyjt__jssk = getattr(func, '__name__', str(func))
    name = 'OverloadTemplate_%s' % (xiyjt__jssk,)
    no_unliteral = kwargs.pop('no_unliteral', False)
    base = numba.core.typing.templates._OverloadFunctionTemplate
    ljej__ltd = dict(key=func, _overload_func=staticmethod(overload_func),
        _impl_cache={}, _compiled_overloads={}, _jit_options=jit_options,
        _strict=strict, _inline=staticmethod(InlineOptions(inline)),
        _inline_overloads={}, prefer_literal=prefer_literal, _no_unliteral=
        no_unliteral, metadata=kwargs)
    return type(base)(name, (base,), ljej__ltd)


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
            for enviw__nnxak in fnty.templates:
                self._inline_overloads.update(enviw__nnxak._inline_overloads)
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
    ljej__ltd = dict(key=typ, _attr=attr, _impl_cache={}, _inline=
        staticmethod(InlineOptions(inline)), _inline_overloads={},
        _no_unliteral=no_unliteral, _overload_func=staticmethod(
        overload_func), prefer_literal=prefer_literal, metadata=kwargs)
    obj = type(base)(name, (base,), ljej__ltd)
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
    tpa__laval, zkdte__mnpn = self._get_impl(args, kws)
    if tpa__laval is None:
        return
    qkxev__vojt = types.Dispatcher(tpa__laval)
    if not self._inline.is_never_inline:
        from numba.core import compiler, typed_passes
        from numba.core.inline_closurecall import InlineWorker
        yzyyp__xofuo = tpa__laval._compiler
        flags = compiler.Flags()
        lophg__poyrl = yzyyp__xofuo.targetdescr.typing_context
        gvaz__qqmjy = yzyyp__xofuo.targetdescr.target_context
        zaxh__jur = yzyyp__xofuo.pipeline_class(lophg__poyrl, gvaz__qqmjy,
            None, None, None, flags, None)
        zpg__nihlp = InlineWorker(lophg__poyrl, gvaz__qqmjy, yzyyp__xofuo.
            locals, zaxh__jur, flags, None)
        jicld__tlnqn = qkxev__vojt.dispatcher.get_call_template
        enviw__nnxak, giyx__iwhs, oxfo__nbumc, kws = jicld__tlnqn(zkdte__mnpn,
            kws)
        if oxfo__nbumc in self._inline_overloads:
            return self._inline_overloads[oxfo__nbumc]['iinfo'].signature
        ir = zpg__nihlp.run_untyped_passes(qkxev__vojt.dispatcher.py_func,
            enable_ssa=True)
        typemap, return_type, calltypes, _ = typed_passes.type_inference_stage(
            self.context, gvaz__qqmjy, ir, oxfo__nbumc, None)
        ir = PreLowerStripPhis()._strip_phi_nodes(ir)
        ir._definitions = numba.core.ir_utils.build_definitions(ir.blocks)
        sig = Signature(return_type, oxfo__nbumc, None)
        self._inline_overloads[sig.args] = {'folded_args': oxfo__nbumc}
        yihk__pve = _EmptyImplementationEntry('always inlined')
        self._compiled_overloads[sig.args] = yihk__pve
        if not self._inline.is_always_inline:
            sig = qkxev__vojt.get_call_type(self.context, zkdte__mnpn, kws)
            self._compiled_overloads[sig.args] = qkxev__vojt.get_overload(sig)
        pnery__ike = _inline_info(ir, typemap, calltypes, sig)
        self._inline_overloads[sig.args] = {'folded_args': oxfo__nbumc,
            'iinfo': pnery__ike}
    else:
        sig = qkxev__vojt.get_call_type(self.context, zkdte__mnpn, kws)
        if sig is None:
            return None
        self._compiled_overloads[sig.args] = qkxev__vojt.get_overload(sig)
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
    gguo__ind = [True, False]
    nbad__kvqq = [False, True]
    gaa__xfrgd = _ResolutionFailures(context, self, args, kws, depth=self.
        _depth)
    from numba.core.target_extension import get_local_target
    mwgbv__lfiwa = get_local_target(context)
    ypduq__ymi = utils.order_by_target_specificity(mwgbv__lfiwa, self.
        templates, fnkey=self.key[0])
    self._depth += 1
    for vxj__ysqvs in ypduq__ymi:
        hxkq__gkbif = vxj__ysqvs(context)
        jbcq__ahant = gguo__ind if hxkq__gkbif.prefer_literal else nbad__kvqq
        jbcq__ahant = [True] if getattr(hxkq__gkbif, '_no_unliteral', False
            ) else jbcq__ahant
        for lvqsx__tlaan in jbcq__ahant:
            try:
                if lvqsx__tlaan:
                    sig = hxkq__gkbif.apply(args, kws)
                else:
                    djx__knv = tuple([_unlit_non_poison(a) for a in args])
                    zmlt__rmp = {lrau__xmn: _unlit_non_poison(oin__dfmu) for
                        lrau__xmn, oin__dfmu in kws.items()}
                    sig = hxkq__gkbif.apply(djx__knv, zmlt__rmp)
            except Exception as e:
                from numba.core import utils
                if utils.use_new_style_errors() and not isinstance(e,
                    errors.NumbaError):
                    raise e
                else:
                    sig = None
                    gaa__xfrgd.add_error(hxkq__gkbif, False, e, lvqsx__tlaan)
            else:
                if sig is not None:
                    self._impl_keys[sig.args] = hxkq__gkbif.get_impl_key(sig)
                    self._depth -= 1
                    return sig
                else:
                    stptv__izp = getattr(hxkq__gkbif, 'cases', None)
                    if stptv__izp is not None:
                        msg = 'No match for registered cases:\n%s'
                        msg = msg % '\n'.join(' * {}'.format(x) for x in
                            stptv__izp)
                    else:
                        msg = 'No match.'
                    gaa__xfrgd.add_error(hxkq__gkbif, True, msg, lvqsx__tlaan)
    gaa__xfrgd.raise_error()


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
    enviw__nnxak = self.template(context)
    cmf__lwa = None
    avdt__trpr = None
    xuom__ykdd = None
    jbcq__ahant = [True, False] if enviw__nnxak.prefer_literal else [False,
        True]
    jbcq__ahant = [True] if getattr(enviw__nnxak, '_no_unliteral', False
        ) else jbcq__ahant
    for lvqsx__tlaan in jbcq__ahant:
        if lvqsx__tlaan:
            try:
                xuom__ykdd = enviw__nnxak.apply(args, kws)
            except Exception as tule__zfa:
                if isinstance(tule__zfa, errors.ForceLiteralArg):
                    raise tule__zfa
                cmf__lwa = tule__zfa
                xuom__ykdd = None
            else:
                break
        else:
            bdzu__hkwx = tuple([_unlit_non_poison(a) for a in args])
            slp__yni = {lrau__xmn: _unlit_non_poison(oin__dfmu) for 
                lrau__xmn, oin__dfmu in kws.items()}
            qyc__iswmk = bdzu__hkwx == args and kws == slp__yni
            if not qyc__iswmk and xuom__ykdd is None:
                try:
                    xuom__ykdd = enviw__nnxak.apply(bdzu__hkwx, slp__yni)
                except Exception as tule__zfa:
                    from numba.core import utils
                    if utils.use_new_style_errors() and not isinstance(
                        tule__zfa, errors.NumbaError):
                        raise tule__zfa
                    if isinstance(tule__zfa, errors.ForceLiteralArg):
                        if enviw__nnxak.prefer_literal:
                            raise tule__zfa
                    avdt__trpr = tule__zfa
                else:
                    break
    if xuom__ykdd is None and (avdt__trpr is not None or cmf__lwa is not None):
        aug__dnpv = '- Resolution failure for {} arguments:\n{}\n'
        yve__rflh = _termcolor.highlight(aug__dnpv)
        if numba.core.config.DEVELOPER_MODE:
            wsyy__wuxd = ' ' * 4

            def add_bt(error):
                if isinstance(error, BaseException):
                    wzhl__gnex = traceback.format_exception(type(error),
                        error, error.__traceback__)
                else:
                    wzhl__gnex = ['']
                hkt__knnep = '\n{}'.format(2 * wsyy__wuxd)
                uuh__lwk = _termcolor.reset(hkt__knnep + hkt__knnep.join(
                    _bt_as_lines(wzhl__gnex)))
                return _termcolor.reset(uuh__lwk)
        else:
            add_bt = lambda X: ''

        def nested_msg(literalness, e):
            dnz__nqbn = str(e)
            dnz__nqbn = dnz__nqbn if dnz__nqbn else str(repr(e)) + add_bt(e)
            nfzx__oxntm = errors.TypingError(textwrap.dedent(dnz__nqbn))
            return yve__rflh.format(literalness, str(nfzx__oxntm))
        import bodo
        if isinstance(cmf__lwa, bodo.utils.typing.BodoError):
            raise cmf__lwa
        if numba.core.config.DEVELOPER_MODE:
            raise errors.TypingError(nested_msg('literal', cmf__lwa) +
                nested_msg('non-literal', avdt__trpr))
        else:
            if 'missing a required argument' in cmf__lwa.msg:
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
            raise errors.TypingError(msg, loc=cmf__lwa.loc)
    return xuom__ykdd


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
    vgsmv__ohw = 'PyUnicode_FromStringAndSize'
    fn = self._get_function(fnty, name=vgsmv__ohw)
    return self.builder.call(fn, [string, size])


numba.core.pythonapi.PythonAPI.string_from_string_and_size = (
    string_from_string_and_size)


def _compile_for_args(self, *args, **kws):
    assert not kws
    self._compilation_chain_init_hook()
    import bodo

    def error_rewrite(e, issue_type):
        if numba.core.config.SHOW_HELP:
            lqq__bpiwu = errors.error_extras[issue_type]
            e.patch_message('\n'.join((str(e).rstrip(), lqq__bpiwu)))
        if numba.core.config.FULL_TRACEBACKS:
            raise e
        else:
            raise e.with_traceback(None)
    tjpxy__tecv = []
    for a in args:
        if isinstance(a, numba.core.dispatcher.OmittedArg):
            tjpxy__tecv.append(types.Omitted(a.value))
        else:
            tjpxy__tecv.append(self.typeof_pyval(a))
    kvdhg__laum = None
    try:
        error = None
        kvdhg__laum = self.compile(tuple(tjpxy__tecv))
    except errors.ForceLiteralArg as e:
        xstq__olfmp = [i for i in e.requested_args if isinstance(args[i],
            types.Literal) and not isinstance(args[i], types.LiteralStrKeyDict)
            ]
        if xstq__olfmp:
            dltr__heblr = """Repeated literal typing request.
{}.
This is likely caused by an error in typing. Please see nested and suppressed exceptions."""
            jkbqv__bcwp = ', '.join('Arg #{} is {}'.format(i, args[i]) for
                i in sorted(xstq__olfmp))
            raise errors.CompilerError(dltr__heblr.format(jkbqv__bcwp))
        zkdte__mnpn = []
        try:
            for i, oin__dfmu in enumerate(args):
                if i in e.requested_args:
                    if i in e.file_infos:
                        zkdte__mnpn.append(types.FilenameType(args[i], e.
                            file_infos[i]))
                    else:
                        zkdte__mnpn.append(types.literal(args[i]))
                else:
                    zkdte__mnpn.append(args[i])
            args = zkdte__mnpn
        except (OSError, FileNotFoundError) as qyxnk__mhx:
            error = FileNotFoundError(str(qyxnk__mhx) + '\n' + e.loc.
                strformat() + '\n')
        except bodo.utils.typing.BodoError as e:
            error = bodo.utils.typing.BodoError(str(e))
        if error is None:
            try:
                kvdhg__laum = self._compile_for_args(*args)
            except TypingError as e:
                error = errors.TypingError(str(e))
            except bodo.utils.typing.BodoError as e:
                error = bodo.utils.typing.BodoError(str(e))
    except errors.TypingError as e:
        hoxcb__jwpe = []
        for i, owdpm__kkr in enumerate(args):
            val = owdpm__kkr.value if isinstance(owdpm__kkr, numba.core.
                dispatcher.OmittedArg) else owdpm__kkr
            try:
                wftly__omhzy = typeof(val, Purpose.argument)
            except ValueError as gquzs__lcu:
                hoxcb__jwpe.append((i, str(gquzs__lcu)))
            else:
                if wftly__omhzy is None:
                    hoxcb__jwpe.append((i,
                        f'cannot determine Numba type of value {val}'))
        if hoxcb__jwpe:
            oulta__nzrz = '\n'.join(f'- argument {i}: {xlodt__lqtws}' for i,
                xlodt__lqtws in hoxcb__jwpe)
            msg = f"""{str(e).rstrip()} 

This error may have been caused by the following argument(s):
{oulta__nzrz}
"""
            e.patch_message(msg)
        if "Cannot determine Numba type of <class 'numpy.ufunc'>" in e.msg:
            msg = 'Unsupported Numpy ufunc encountered in JIT code'
            error = bodo.utils.typing.BodoError(msg, loc=e.loc)
        elif not numba.core.config.DEVELOPER_MODE:
            if bodo_typing_error_info not in e.msg:
                yjur__yxq = ['Failed in nopython mode pipeline',
                    'Failed in bodo mode pipeline', 'Failed at nopython',
                    'Overload', 'lowering']
                khvio__qte = False
                for mmlo__uohoq in yjur__yxq:
                    if mmlo__uohoq in e.msg:
                        msg = 'Compilation error. '
                        msg += f'{bodo_typing_error_info}'
                        khvio__qte = True
                        break
                if not khvio__qte:
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
                lqq__bpiwu = errors.error_extras['reportable']
                e.patch_message('\n'.join((str(e).rstrip(), lqq__bpiwu)))
        raise e
    finally:
        self._types_active_call = []
        del args
        if error:
            raise error
    return kvdhg__laum


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
    for jssy__yoow in cres.library._codegen._engine._defined_symbols:
        if jssy__yoow.startswith('cfunc'
            ) and 'get_agg_udf_addr' not in jssy__yoow and (
            'bodo_gb_udf_update_local' in jssy__yoow or 
            'bodo_gb_udf_combine' in jssy__yoow or 'bodo_gb_udf_eval' in
            jssy__yoow or 'bodo_gb_apply_general_udfs' in jssy__yoow):
            gb_agg_cfunc_addr[jssy__yoow
                ] = cres.library.get_pointer_to_function(jssy__yoow)


def resolve_join_general_cond_funcs(cres):
    from bodo.ir.join import join_gen_cond_cfunc_addr
    for jssy__yoow in cres.library._codegen._engine._defined_symbols:
        if jssy__yoow.startswith('cfunc') and ('get_join_cond_addr' not in
            jssy__yoow or 'bodo_join_gen_cond' in jssy__yoow):
            join_gen_cond_cfunc_addr[jssy__yoow
                ] = cres.library.get_pointer_to_function(jssy__yoow)


def compile(self, sig):
    import numba.core.event as ev
    from numba.core import sigutils
    from numba.core.compiler_lock import global_compiler_lock
    import bodo
    tpa__laval = self._get_dispatcher_for_current_target()
    if tpa__laval is not self:
        return tpa__laval.compile(sig)
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
            dzq__itcq = self.overloads.get(tuple(args))
            if dzq__itcq is not None:
                return dzq__itcq.entry_point
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
            veoz__hfavi = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=veoz__hfavi):
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
                nrtb__dfs = bodo.get_nodes_first_ranks()
                if bodo.get_rank() in nrtb__dfs:
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
    mmga__sjvps = self._final_module
    fyohl__mdyg = []
    tlim__ptk = 0
    for fn in mmga__sjvps.functions:
        tlim__ptk += 1
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
            fyohl__mdyg.append(fn.name)
    if tlim__ptk == 0:
        raise RuntimeError(
            'library unfit for linking: no available functions in %s' % (self,)
            )
    if fyohl__mdyg:
        mmga__sjvps = mmga__sjvps.clone()
        for name in fyohl__mdyg:
            mmga__sjvps.get_function(name).linkage = 'linkonce_odr'
    self._shared_module = mmga__sjvps
    return mmga__sjvps


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
    for tru__wju in self.constraints:
        loc = tru__wju.loc
        with typeinfer.warnings.catch_warnings(filename=loc.filename,
            lineno=loc.line):
            try:
                tru__wju(typeinfer)
            except numba.core.errors.ForceLiteralArg as e:
                errors.append(e)
            except numba.core.errors.TypingError as e:
                numba.core.typeinfer._logger.debug('captured error', exc_info=e
                    )
                zxxr__rzetf = numba.core.errors.TypingError(str(e), loc=
                    tru__wju.loc, highlighting=False)
                errors.append(numba.core.utils.chain_exception(zxxr__rzetf, e))
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
                    zxxr__rzetf = numba.core.errors.TypingError(msg.format(
                        con=tru__wju, err=str(e)), loc=tru__wju.loc,
                        highlighting=False)
                    errors.append(utils.chain_exception(zxxr__rzetf, e))
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
    for ywv__zir in self._failures.values():
        for spv__xmd in ywv__zir:
            if isinstance(spv__xmd.error, ForceLiteralArg):
                raise spv__xmd.error
            if isinstance(spv__xmd.error, bodo.utils.typing.BodoError):
                raise spv__xmd.error
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
    iqklq__pvajm = False
    wug__jwzx = [block.terminator]
    for stmt in reversed(block.body[:-1]):
        cqcph__zrvai = set()
        fko__ahbc = lives & alias_set
        for oin__dfmu in fko__ahbc:
            cqcph__zrvai |= alias_map[oin__dfmu]
        lives_n_aliases = lives | cqcph__zrvai | arg_aliases
        if type(stmt) in remove_dead_extensions:
            iyby__xiaq = remove_dead_extensions[type(stmt)]
            stmt = iyby__xiaq(stmt, lives, lives_n_aliases, arg_aliases,
                alias_map, func_ir, typemap)
            if stmt is None:
                iqklq__pvajm = True
                continue
        if isinstance(stmt, ir.Assign):
            qjb__zmzx = stmt.target
            ymzx__wfvaa = stmt.value
            if qjb__zmzx.name not in lives:
                if has_no_side_effect(ymzx__wfvaa, lives_n_aliases, call_table
                    ):
                    iqklq__pvajm = True
                    continue
                if isinstance(ymzx__wfvaa, ir.Expr
                    ) and ymzx__wfvaa.op == 'call' and call_table[ymzx__wfvaa
                    .func.name] == ['astype']:
                    hmg__deacv = guard(get_definition, func_ir, ymzx__wfvaa
                        .func)
                    if (hmg__deacv is not None and hmg__deacv.op ==
                        'getattr' and isinstance(typemap[hmg__deacv.value.
                        name], types.Array) and hmg__deacv.attr == 'astype'):
                        iqklq__pvajm = True
                        continue
            if saved_array_analysis and qjb__zmzx.name in lives and is_expr(
                ymzx__wfvaa, 'getattr'
                ) and ymzx__wfvaa.attr == 'shape' and is_array_typ(typemap[
                ymzx__wfvaa.value.name]
                ) and ymzx__wfvaa.value.name not in lives:
                qbhs__qkgcs = {oin__dfmu: lrau__xmn for lrau__xmn,
                    oin__dfmu in func_ir.blocks.items()}
                if block in qbhs__qkgcs:
                    jqh__btri = qbhs__qkgcs[block]
                    mfvm__ywkm = saved_array_analysis.get_equiv_set(jqh__btri)
                    lss__vngup = mfvm__ywkm.get_equiv_set(ymzx__wfvaa.value)
                    if lss__vngup is not None:
                        for oin__dfmu in lss__vngup:
                            if oin__dfmu.endswith('#0'):
                                oin__dfmu = oin__dfmu[:-2]
                            if oin__dfmu in typemap and is_array_typ(typemap
                                [oin__dfmu]) and oin__dfmu in lives:
                                ymzx__wfvaa.value = ir.Var(ymzx__wfvaa.
                                    value.scope, oin__dfmu, ymzx__wfvaa.
                                    value.loc)
                                iqklq__pvajm = True
                                break
            if isinstance(ymzx__wfvaa, ir.Var
                ) and qjb__zmzx.name == ymzx__wfvaa.name:
                iqklq__pvajm = True
                continue
        if isinstance(stmt, ir.Del):
            if stmt.value not in lives:
                iqklq__pvajm = True
                continue
        if isinstance(stmt, ir.SetItem):
            name = stmt.target.name
            if name not in lives_n_aliases:
                continue
        if type(stmt) in analysis.ir_extension_usedefs:
            xkjnh__xcg = analysis.ir_extension_usedefs[type(stmt)]
            nqexa__zbxgc, ongh__zsclh = xkjnh__xcg(stmt)
            lives -= ongh__zsclh
            lives |= nqexa__zbxgc
        else:
            lives |= {oin__dfmu.name for oin__dfmu in stmt.list_vars()}
            if isinstance(stmt, ir.Assign):
                hhwsr__lwyui = set()
                if isinstance(ymzx__wfvaa, ir.Expr):
                    hhwsr__lwyui = {oin__dfmu.name for oin__dfmu in
                        ymzx__wfvaa.list_vars()}
                if qjb__zmzx.name not in hhwsr__lwyui:
                    lives.remove(qjb__zmzx.name)
        wug__jwzx.append(stmt)
    wug__jwzx.reverse()
    block.body = wug__jwzx
    return iqklq__pvajm


ir_utils.remove_dead_block = bodo_remove_dead_block


@infer_global(set)
class SetBuiltin(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if args:
            mjgi__uyic, = args
            if isinstance(mjgi__uyic, types.IterableType):
                dtype = mjgi__uyic.iterator_type.yield_type
                if isinstance(dtype, types.Hashable
                    ) or dtype == numba.core.types.unicode_type:
                    return signature(types.Set(dtype), mjgi__uyic)
        else:
            return signature(types.Set(types.undefined))


def Set__init__(self, dtype, reflected=False):
    assert isinstance(dtype, (types.Hashable, types.Undefined)
        ) or dtype == numba.core.types.unicode_type
    self.dtype = dtype
    self.reflected = reflected
    ewg__blxpr = 'reflected set' if reflected else 'set'
    name = '%s(%s)' % (ewg__blxpr, self.dtype)
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
        except LiteralTypingError as sww__zsdv:
            return
    try:
        return literal(value)
    except LiteralTypingError as sww__zsdv:
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
        nnch__yxbny = py_func.__qualname__
    except AttributeError as sww__zsdv:
        nnch__yxbny = py_func.__name__
    gxpi__qskf = inspect.getfile(py_func)
    for cls in self._locator_classes:
        qxfe__ifxdc = cls.from_function(py_func, gxpi__qskf)
        if qxfe__ifxdc is not None:
            break
    else:
        raise RuntimeError(
            'cannot cache function %r: no locator available for file %r' %
            (nnch__yxbny, gxpi__qskf))
    self._locator = qxfe__ifxdc
    zujh__nnw = inspect.getfile(py_func)
    lqbeg__jnce = os.path.splitext(os.path.basename(zujh__nnw))[0]
    if gxpi__qskf.startswith('<ipython-'):
        ysdi__txv = re.sub('(ipython-input)(-\\d+)(-[0-9a-fA-F]+)',
            '\\1\\3', lqbeg__jnce, count=1)
        if ysdi__txv == lqbeg__jnce:
            warnings.warn(
                'Did not recognize ipython module name syntax. Caching might not work'
                )
        lqbeg__jnce = ysdi__txv
    cjq__fyu = '%s.%s' % (lqbeg__jnce, nnch__yxbny)
    fohjl__wmdk = getattr(sys, 'abiflags', '')
    from bodo import __version__ as bodo_version
    self._filename_base = self.get_filename_base(cjq__fyu, fohjl__wmdk
        ) + 'bodo' + bodo_version


if _check_numba_change:
    lines = inspect.getsource(numba.core.caching._CacheImpl.__init__)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b46d298146e3844e9eaeef29d36f5165ba4796c270ca50d2b35f9fcdc0fa032a':
        warnings.warn('numba.core.caching._CacheImpl.__init__ has changed')
numba.core.caching._CacheImpl.__init__ = CacheImpl__init__


def _analyze_broadcast(self, scope, equiv_set, loc, args, fn):
    from numba.parfors.array_analysis import ArrayAnalysis
    qlzg__ywpdb = list(filter(lambda a: self._istuple(a.name), args))
    if len(qlzg__ywpdb) == 2 and fn.__name__ == 'add':
        ncpow__nrf = self.typemap[qlzg__ywpdb[0].name]
        nrim__qbm = self.typemap[qlzg__ywpdb[1].name]
        if ncpow__nrf.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                qlzg__ywpdb[1]))
        if nrim__qbm.count == 0:
            return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
                qlzg__ywpdb[0]))
        try:
            dvsn__giov = [equiv_set.get_shape(x) for x in qlzg__ywpdb]
            if None in dvsn__giov:
                return None
            bpx__dhbq = sum(dvsn__giov, ())
            return ArrayAnalysis.AnalyzeResult(shape=bpx__dhbq)
        except GuardException as sww__zsdv:
            return None
    emj__vna = list(filter(lambda a: self._isarray(a.name), args))
    require(len(emj__vna) > 0)
    bll__yexgr = [x.name for x in emj__vna]
    gqj__gcy = [self.typemap[x.name].ndim for x in emj__vna]
    zkbm__grr = max(gqj__gcy)
    require(zkbm__grr > 0)
    dvsn__giov = [equiv_set.get_shape(x) for x in emj__vna]
    if any(a is None for a in dvsn__giov):
        return ArrayAnalysis.AnalyzeResult(shape=emj__vna[0], pre=self.
            _call_assert_equiv(scope, loc, equiv_set, emj__vna))
    return self._broadcast_assert_shapes(scope, equiv_set, loc, dvsn__giov,
        bll__yexgr)


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
    xku__aopvd = code_obj.code
    yowa__taf = len(xku__aopvd.co_freevars)
    ljuc__juuqp = xku__aopvd.co_freevars
    if code_obj.closure is not None:
        assert isinstance(code_obj.closure, ir.Var)
        qqf__skws, op = ir_utils.find_build_sequence(caller_ir, code_obj.
            closure)
        assert op == 'build_tuple'
        ljuc__juuqp = [oin__dfmu.name for oin__dfmu in qqf__skws]
    kdq__ookzo = caller_ir.func_id.func.__globals__
    try:
        kdq__ookzo = getattr(code_obj, 'globals', kdq__ookzo)
    except KeyError as sww__zsdv:
        pass
    msg = (
        "Inner function is using non-constant variable '{}' from outer function. Please pass as argument if possible. See https://docs.bodo.ai/latest/api_docs/udfs/."
        )
    pgyk__kaug = []
    for x in ljuc__juuqp:
        try:
            teenj__ambm = caller_ir.get_definition(x)
        except KeyError as sww__zsdv:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
        from numba.core.registry import CPUDispatcher
        if isinstance(teenj__ambm, (ir.Const, ir.Global, ir.FreeVar)):
            val = teenj__ambm.value
            if isinstance(val, str):
                val = "'{}'".format(val)
            if isinstance(val, pytypes.FunctionType):
                xiyjt__jssk = ir_utils.mk_unique_var('nested_func').replace('.'
                    , '_')
                kdq__ookzo[xiyjt__jssk] = bodo.jit(distributed=False)(val)
                kdq__ookzo[xiyjt__jssk].is_nested_func = True
                val = xiyjt__jssk
            if isinstance(val, CPUDispatcher):
                xiyjt__jssk = ir_utils.mk_unique_var('nested_func').replace('.'
                    , '_')
                kdq__ookzo[xiyjt__jssk] = val
                val = xiyjt__jssk
            pgyk__kaug.append(val)
        elif isinstance(teenj__ambm, ir.Expr
            ) and teenj__ambm.op == 'make_function':
            aazd__wda = convert_code_obj_to_function(teenj__ambm, caller_ir)
            xiyjt__jssk = ir_utils.mk_unique_var('nested_func').replace('.',
                '_')
            kdq__ookzo[xiyjt__jssk] = bodo.jit(distributed=False)(aazd__wda)
            kdq__ookzo[xiyjt__jssk].is_nested_func = True
            pgyk__kaug.append(xiyjt__jssk)
        else:
            raise bodo.utils.typing.BodoError(msg.format(x), loc=code_obj.loc)
    hyzx__kis = '\n'.join([('\tc_%d = %s' % (i, x)) for i, x in enumerate(
        pgyk__kaug)])
    tgh__fhj = ','.join([('c_%d' % i) for i in range(yowa__taf)])
    ihtr__xci = list(xku__aopvd.co_varnames)
    apjjl__szl = 0
    rgtf__qajkt = xku__aopvd.co_argcount
    nazjg__yupt = caller_ir.get_definition(code_obj.defaults)
    if nazjg__yupt is not None:
        if isinstance(nazjg__yupt, tuple):
            d = [caller_ir.get_definition(x).value for x in nazjg__yupt]
            lejcd__xgbk = tuple(d)
        else:
            d = [caller_ir.get_definition(x).value for x in nazjg__yupt.items]
            lejcd__xgbk = tuple(d)
        apjjl__szl = len(lejcd__xgbk)
    fsk__ofzr = rgtf__qajkt - apjjl__szl
    nhdqc__ehmtc = ','.join([('%s' % ihtr__xci[i]) for i in range(fsk__ofzr)])
    if apjjl__szl:
        mea__qvfs = [('%s = %s' % (ihtr__xci[i + fsk__ofzr], lejcd__xgbk[i]
            )) for i in range(apjjl__szl)]
        nhdqc__ehmtc += ', '
        nhdqc__ehmtc += ', '.join(mea__qvfs)
    return _create_function_from_code_obj(xku__aopvd, hyzx__kis,
        nhdqc__ehmtc, tgh__fhj, kdq__ookzo)


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
    for flnf__asjw, (gioc__hjf, nfyt__koueo) in enumerate(self.passes):
        try:
            numba.core.tracing.event('-- %s' % nfyt__koueo)
            eagrq__hfj = _pass_registry.get(gioc__hjf).pass_inst
            if isinstance(eagrq__hfj, CompilerPass):
                self._runPass(flnf__asjw, eagrq__hfj, state)
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
                    pipeline_name, nfyt__koueo)
                bzeln__ozx = self._patch_error(msg, e)
                raise bzeln__ozx
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
    lyoj__jdee = None
    ongh__zsclh = {}

    def lookup(var, already_seen, varonly=True):
        val = ongh__zsclh.get(var.name, None)
        if isinstance(val, ir.Var):
            if val.name in already_seen:
                return var
            already_seen.add(val.name)
            return lookup(val, already_seen, varonly)
        else:
            return var if varonly or val is None else val
    name = reduction_node.name
    hkpm__zdmah = reduction_node.unversioned_name
    for i, stmt in enumerate(nodes):
        qjb__zmzx = stmt.target
        ymzx__wfvaa = stmt.value
        ongh__zsclh[qjb__zmzx.name] = ymzx__wfvaa
        if isinstance(ymzx__wfvaa, ir.Var) and ymzx__wfvaa.name in ongh__zsclh:
            ymzx__wfvaa = lookup(ymzx__wfvaa, set())
        if isinstance(ymzx__wfvaa, ir.Expr):
            aafb__raw = set(lookup(oin__dfmu, set(), True).name for
                oin__dfmu in ymzx__wfvaa.list_vars())
            if name in aafb__raw:
                args = [(x.name, lookup(x, set(), True)) for x in
                    get_expr_args(ymzx__wfvaa)]
                bzc__snx = [x for x, suj__eigup in args if suj__eigup.name !=
                    name]
                args = [(x, suj__eigup) for x, suj__eigup in args if x !=
                    suj__eigup.name]
                nra__djohs = dict(args)
                if len(bzc__snx) == 1:
                    nra__djohs[bzc__snx[0]] = ir.Var(qjb__zmzx.scope, name +
                        '#init', qjb__zmzx.loc)
                replace_vars_inner(ymzx__wfvaa, nra__djohs)
                lyoj__jdee = nodes[i:]
                break
    return lyoj__jdee


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
        prdc__gzzh = expand_aliases({oin__dfmu.name for oin__dfmu in stmt.
            list_vars()}, alias_map, arg_aliases)
        kwa__bvkty = expand_aliases(get_parfor_writes(stmt, func_ir),
            alias_map, arg_aliases)
        stibb__kdthf = expand_aliases({oin__dfmu.name for oin__dfmu in
            next_stmt.list_vars()}, alias_map, arg_aliases)
        emac__fnhlm = expand_aliases(get_stmt_writes(next_stmt, func_ir),
            alias_map, arg_aliases)
        if len(kwa__bvkty & stibb__kdthf | emac__fnhlm & prdc__gzzh) == 0:
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
    kudig__pve = set()
    blocks = parfor.loop_body.copy()
    blocks[-1] = parfor.init_block
    for block in blocks.values():
        for stmt in block.body:
            kudig__pve.update(get_stmt_writes(stmt, func_ir))
            if isinstance(stmt, Parfor):
                kudig__pve.update(get_parfor_writes(stmt, func_ir))
    return kudig__pve


if _check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.get_parfor_writes)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'a7b29cd76832b6f6f1f2d2397ec0678c1409b57a6eab588bffd344b775b1546f':
        warnings.warn('numba.parfors.parfor.get_parfor_writes has changed')


def get_stmt_writes(stmt, func_ir):
    import bodo
    from bodo.utils.utils import is_call_assign
    kudig__pve = set()
    if isinstance(stmt, (ir.Assign, ir.SetItem, ir.StaticSetItem)):
        kudig__pve.add(stmt.target.name)
    if isinstance(stmt, (bodo.ir.csv_ext.CsvReader, bodo.ir.parquet_ext.
        ParquetReader)):
        kudig__pve = {oin__dfmu.name for oin__dfmu in stmt.out_vars}
    if isinstance(stmt, (bodo.ir.join.Join, bodo.ir.aggregate.Aggregate)):
        kudig__pve = {oin__dfmu.name for oin__dfmu in stmt.get_live_out_vars()}
    if isinstance(stmt, bodo.ir.sort.Sort):
        if not stmt.inplace:
            kudig__pve.update({oin__dfmu.name for oin__dfmu in stmt.
                get_live_out_vars()})
    if is_call_assign(stmt):
        qhe__qgwh = guard(find_callname, func_ir, stmt.value)
        if qhe__qgwh in (('setitem_str_arr_ptr', 'bodo.libs.str_arr_ext'),
            ('setna', 'bodo.libs.array_kernels'), (
            'str_arr_item_to_numeric', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_int_to_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_setitem_NA_str', 'bodo.libs.str_arr_ext'), (
            'str_arr_set_not_na', 'bodo.libs.str_arr_ext'), (
            'get_str_arr_item_copy', 'bodo.libs.str_arr_ext'), (
            'set_bit_to_arr', 'bodo.libs.int_arr_ext')):
            kudig__pve.add(stmt.value.args[0].name)
        if qhe__qgwh == ('generate_table_nbytes', 'bodo.utils.table_utils'):
            kudig__pve.add(stmt.value.args[1].name)
    return kudig__pve


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
        iyby__xiaq = _termcolor.errmsg('{0}') + _termcolor.filename(
            'During: {1}')
        uoe__coc = iyby__xiaq.format(self, msg)
        self.args = uoe__coc,
    else:
        iyby__xiaq = _termcolor.errmsg('{0}')
        uoe__coc = iyby__xiaq.format(self)
        self.args = uoe__coc,
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
        for ecll__qwz in options['distributed']:
            dist_spec[ecll__qwz] = Distribution.OneD_Var
    if 'distributed_block' in options:
        for ecll__qwz in options['distributed_block']:
            dist_spec[ecll__qwz] = Distribution.OneD
    return dist_spec


def register_class_type(cls, spec, class_ctor, builder, **options):
    import typing as pt
    from numba.core.typing.asnumbatype import as_numba_type
    import bodo
    dist_spec = _get_dist_spec_from_options(spec, **options)
    ore__xyfx = options.get('returns_maybe_distributed', True)
    if spec is None:
        spec = OrderedDict()
    elif isinstance(spec, Sequence):
        spec = OrderedDict(spec)
    for attr, xckn__zhpe in pt.get_type_hints(cls).items():
        if attr not in spec:
            spec[attr] = as_numba_type(xckn__zhpe)
    jitclass_base._validate_spec(spec)
    spec = jitclass_base._fix_up_private_attr(cls.__name__, spec)
    nhu__rivl = {}
    for tuujz__akpqz in reversed(inspect.getmro(cls)):
        nhu__rivl.update(tuujz__akpqz.__dict__)
    mjdy__jgnu, zeb__rsc, iefzy__xut, yczs__fllr = {}, {}, {}, {}
    for lrau__xmn, oin__dfmu in nhu__rivl.items():
        if isinstance(oin__dfmu, pytypes.FunctionType):
            mjdy__jgnu[lrau__xmn] = oin__dfmu
        elif isinstance(oin__dfmu, property):
            zeb__rsc[lrau__xmn] = oin__dfmu
        elif isinstance(oin__dfmu, staticmethod):
            iefzy__xut[lrau__xmn] = oin__dfmu
        else:
            yczs__fllr[lrau__xmn] = oin__dfmu
    ttums__npd = (set(mjdy__jgnu) | set(zeb__rsc) | set(iefzy__xut)) & set(spec
        )
    if ttums__npd:
        raise NameError('name shadowing: {0}'.format(', '.join(ttums__npd)))
    qndm__ktimt = yczs__fllr.pop('__doc__', '')
    jitclass_base._drop_ignored_attrs(yczs__fllr)
    if yczs__fllr:
        msg = 'class members are not yet supported: {0}'
        svkcc__dsr = ', '.join(yczs__fllr.keys())
        raise TypeError(msg.format(svkcc__dsr))
    for lrau__xmn, oin__dfmu in zeb__rsc.items():
        if oin__dfmu.fdel is not None:
            raise TypeError('deleter is not supported: {0}'.format(lrau__xmn))
    jit_methods = {lrau__xmn: bodo.jit(returns_maybe_distributed=ore__xyfx)
        (oin__dfmu) for lrau__xmn, oin__dfmu in mjdy__jgnu.items()}
    jit_props = {}
    for lrau__xmn, oin__dfmu in zeb__rsc.items():
        ljej__ltd = {}
        if oin__dfmu.fget:
            ljej__ltd['get'] = bodo.jit(oin__dfmu.fget)
        if oin__dfmu.fset:
            ljej__ltd['set'] = bodo.jit(oin__dfmu.fset)
        jit_props[lrau__xmn] = ljej__ltd
    jit_static_methods = {lrau__xmn: bodo.jit(oin__dfmu.__func__) for 
        lrau__xmn, oin__dfmu in iefzy__xut.items()}
    ywl__xnmt = class_ctor(cls, jitclass_base.ConstructorTemplate, spec,
        jit_methods, jit_props, jit_static_methods, dist_spec)
    fnovx__frti = dict(class_type=ywl__xnmt, __doc__=qndm__ktimt)
    fnovx__frti.update(jit_static_methods)
    cls = jitclass_base.JitClassType(cls.__name__, (cls,), fnovx__frti)
    typingctx = numba.core.registry.cpu_target.typing_context
    typingctx.insert_global(cls, ywl__xnmt)
    targetctx = numba.core.registry.cpu_target.target_context
    builder(ywl__xnmt, typingctx, targetctx).register()
    as_numba_type.register(cls, ywl__xnmt.instance_type)
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
    reiox__njzp = ','.join('{0}:{1}'.format(lrau__xmn, oin__dfmu) for 
        lrau__xmn, oin__dfmu in struct.items())
    gqm__dimag = ','.join('{0}:{1}'.format(lrau__xmn, oin__dfmu) for 
        lrau__xmn, oin__dfmu in dist_spec.items())
    name = '{0}.{1}#{2:x}<{3}><{4}>'.format(self.name_prefix, self.
        class_name, id(self), reiox__njzp, gqm__dimag)
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
    tpp__ivhpe = numba.core.typeinfer.fold_arg_vars(typevars, self.args,
        self.vararg, self.kws)
    if tpp__ivhpe is None:
        return
    gxss__tsrsz, gzup__toal = tpp__ivhpe
    for a in itertools.chain(gxss__tsrsz, gzup__toal.values()):
        if not a.is_precise() and not isinstance(a, types.Array):
            return
    if isinstance(fnty, types.TypeRef):
        fnty = fnty.instance_type
    try:
        sig = typeinfer.resolve_call(fnty, gxss__tsrsz, gzup__toal)
    except ForceLiteralArg as e:
        spk__bby = (fnty.this,) + tuple(self.args) if isinstance(fnty,
            types.BoundFunction) else self.args
        folded = e.fold_arguments(spk__bby, self.kws)
        dbmhp__eoke = set()
        gyorl__nkkiz = set()
        cgmiy__iwijz = {}
        for flnf__asjw in e.requested_args:
            seb__tms = typeinfer.func_ir.get_definition(folded[flnf__asjw])
            if isinstance(seb__tms, ir.Arg):
                dbmhp__eoke.add(seb__tms.index)
                if seb__tms.index in e.file_infos:
                    cgmiy__iwijz[seb__tms.index] = e.file_infos[seb__tms.index]
            else:
                gyorl__nkkiz.add(flnf__asjw)
        if gyorl__nkkiz:
            raise TypingError('Cannot request literal type.', loc=self.loc)
        elif dbmhp__eoke:
            raise ForceLiteralArg(dbmhp__eoke, loc=self.loc, file_infos=
                cgmiy__iwijz)
    if sig is None:
        kij__xkst = 'Invalid use of {0} with parameters ({1})'
        args = [str(a) for a in gxss__tsrsz]
        args += [('%s=%s' % (lrau__xmn, oin__dfmu)) for lrau__xmn,
            oin__dfmu in sorted(gzup__toal.items())]
        fpv__ykx = kij__xkst.format(fnty, ', '.join(map(str, args)))
        vtguf__ggyqw = context.explain_function_type(fnty)
        msg = '\n'.join([fpv__ykx, vtguf__ggyqw])
        raise TypingError(msg)
    typeinfer.add_type(self.target, sig.return_type, loc=self.loc)
    if isinstance(fnty, types.BoundFunction
        ) and sig.recvr is not None and sig.recvr != fnty.this:
        qtiyd__mero = context.unify_pairs(sig.recvr, fnty.this)
        if qtiyd__mero is None and fnty.this.is_precise(
            ) and sig.recvr.is_precise():
            msg = 'Cannot refine type {} to {}'.format(sig.recvr, fnty.this)
            raise TypingError(msg, loc=self.loc)
        if qtiyd__mero is not None and qtiyd__mero.is_precise():
            qiuin__urocs = fnty.copy(this=qtiyd__mero)
            typeinfer.propagate_refined_type(self.func, qiuin__urocs)
    if not sig.return_type.is_precise():
        target = typevars[self.target]
        if target.defined:
            tpanp__xnj = target.getone()
            if context.unify_pairs(tpanp__xnj, sig.return_type) == tpanp__xnj:
                sig = sig.replace(return_type=tpanp__xnj)
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
        dltr__heblr = '*other* must be a {} but got a {} instead'
        raise TypeError(dltr__heblr.format(ForceLiteralArg, type(other)))
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
    how__nsbdl = {}

    def report_error(varname, msg, loc):
        raise errors.CompilerError(
            f'Error handling objmode argument {varname!r}. {msg}', loc=loc)
    for lrau__xmn, oin__dfmu in kwargs.items():
        yfqlo__ajbr = None
        try:
            rfj__ozp = ir.Var(ir.Scope(None, loc), ir_utils.mk_unique_var(
                'dummy'), loc)
            func_ir._definitions[rfj__ozp.name] = [oin__dfmu]
            yfqlo__ajbr = get_const_value_inner(func_ir, rfj__ozp)
            func_ir._definitions.pop(rfj__ozp.name)
            if isinstance(yfqlo__ajbr, str):
                yfqlo__ajbr = sigutils._parse_signature_string(yfqlo__ajbr)
            if isinstance(yfqlo__ajbr, types.abstract._TypeMetaclass):
                raise BodoError(
                    f"""objmode type annotations require full data types, not just data type classes. For example, 'bodo.DataFrameType((bodo.float64[::1],), bodo.RangeIndexType(), ('A',))' is a valid data type but 'bodo.DataFrameType' is not.
Variable {lrau__xmn} is annotated as type class {yfqlo__ajbr}."""
                    )
            assert isinstance(yfqlo__ajbr, types.Type)
            if isinstance(yfqlo__ajbr, (types.List, types.Set)):
                yfqlo__ajbr = yfqlo__ajbr.copy(reflected=False)
            how__nsbdl[lrau__xmn] = yfqlo__ajbr
        except BodoError as sww__zsdv:
            raise
        except:
            msg = (
                'The value must be a compile-time constant either as a non-local variable or an expression that refers to a Bodo type.'
                )
            if isinstance(yfqlo__ajbr, ir.UndefinedType):
                msg = f'not defined.'
                if isinstance(oin__dfmu, ir.Global):
                    msg = f'Global {oin__dfmu.name!r} is not defined.'
                if isinstance(oin__dfmu, ir.FreeVar):
                    msg = f'Freevar {oin__dfmu.name!r} is not defined.'
            if isinstance(oin__dfmu, ir.Expr) and oin__dfmu.op == 'getattr':
                msg = 'Getattr cannot be resolved at compile-time.'
            report_error(varname=lrau__xmn, msg=msg, loc=loc)
    for name, typ in how__nsbdl.items():
        self._legalize_arg_type(name, typ, loc)
    return how__nsbdl


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
    fok__vwk = inst.arg
    assert fok__vwk > 0, 'invalid BUILD_STRING count'
    strings = list(reversed([state.pop() for _ in range(fok__vwk)]))
    tmps = [state.make_temp() for _ in range(fok__vwk - 1)]
    state.append(inst, strings=strings, tmps=tmps)
    state.push(tmps[-1])


numba.core.byteflow.TraceRunner.op_FORMAT_VALUE = op_FORMAT_VALUE_byteflow
numba.core.byteflow.TraceRunner.op_BUILD_STRING = op_BUILD_STRING_byteflow


def op_FORMAT_VALUE_interpreter(self, inst, value, res, fmtvar, format_spec):
    value = self.get(value)
    jvwaz__gqs = ir.Global('format', format, loc=self.loc)
    self.store(value=jvwaz__gqs, name=fmtvar)
    args = (value, self.get(format_spec)) if format_spec else (value,)
    hxo__kib = ir.Expr.call(self.get(fmtvar), args, (), loc=self.loc)
    self.store(value=hxo__kib, name=res)


def op_BUILD_STRING_interpreter(self, inst, strings, tmps):
    fok__vwk = inst.arg
    assert fok__vwk > 0, 'invalid BUILD_STRING count'
    vafg__gqj = self.get(strings[0])
    for other, hgeas__aprbz in zip(strings[1:], tmps):
        other = self.get(other)
        baovm__pvlaz = ir.Expr.binop(operator.add, lhs=vafg__gqj, rhs=other,
            loc=self.loc)
        self.store(baovm__pvlaz, hgeas__aprbz)
        vafg__gqj = self.get(hgeas__aprbz)


numba.core.interpreter.Interpreter.op_FORMAT_VALUE = (
    op_FORMAT_VALUE_interpreter)
numba.core.interpreter.Interpreter.op_BUILD_STRING = (
    op_BUILD_STRING_interpreter)


def object_hasattr_string(self, obj, attr):
    from llvmlite import ir as lir
    dhpg__pcxrr = self.context.insert_const_string(self.module, attr)
    fnty = lir.FunctionType(lir.IntType(32), [self.pyobj, self.cstring])
    fn = self._get_function(fnty, name='PyObject_HasAttrString')
    return self.builder.call(fn, [obj, dhpg__pcxrr])


numba.core.pythonapi.PythonAPI.object_hasattr_string = object_hasattr_string


def _created_inlined_var_name(function_name, var_name):
    qgj__dqzcd = mk_unique_var(f'{var_name}')
    rzy__bktl = qgj__dqzcd.replace('<', '_').replace('>', '_')
    rzy__bktl = rzy__bktl.replace('.', '_').replace('$', '_v')
    return rzy__bktl


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
                uaoq__kar = get_overload_const_str(val2)
                if uaoq__kar != 'ns':
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
        vis__zcy = states['defmap']
        if len(vis__zcy) == 0:
            akrdv__tljj = assign.target
            numba.core.ssa._logger.debug('first assign: %s', akrdv__tljj)
            if akrdv__tljj.name not in scope.localvars:
                akrdv__tljj = scope.define(assign.target.name, loc=assign.loc)
        else:
            akrdv__tljj = scope.redefine(assign.target.name, loc=assign.loc)
        assign = ir.Assign(target=akrdv__tljj, value=assign.value, loc=
            assign.loc)
        vis__zcy[states['label']].append(assign)
    return assign


if _check_numba_change:
    lines = inspect.getsource(numba.core.ssa._FreshVarHandler.on_assign)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '922c4f9807455f81600b794bbab36f9c6edfecfa83fda877bf85f465db7865e8':
        warnings.warn('_FreshVarHandler on_assign has changed')
numba.core.ssa._FreshVarHandler.on_assign = on_assign


def get_np_ufunc_typ_lst(func):
    from numba.core import typing
    ezx__ptbmj = []
    for lrau__xmn, oin__dfmu in typing.npydecl.registry.globals:
        if lrau__xmn == func:
            ezx__ptbmj.append(oin__dfmu)
    for lrau__xmn, oin__dfmu in typing.templates.builtin_registry.globals:
        if lrau__xmn == func:
            ezx__ptbmj.append(oin__dfmu)
    if len(ezx__ptbmj) == 0:
        raise RuntimeError('type for func ', func, ' not found')
    return ezx__ptbmj


def canonicalize_array_math(func_ir, typemap, calltypes, typingctx):
    import numpy
    from numba.core.ir_utils import arr_math, find_topo_order, mk_unique_var
    blocks = func_ir.blocks
    yhcg__gxio = {}
    csjtg__vhzsr = find_topo_order(blocks)
    djo__wfamq = {}
    for jqh__btri in csjtg__vhzsr:
        block = blocks[jqh__btri]
        wug__jwzx = []
        for stmt in block.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
                qjb__zmzx = stmt.target.name
                ymzx__wfvaa = stmt.value
                if (ymzx__wfvaa.op == 'getattr' and ymzx__wfvaa.attr in
                    arr_math and isinstance(typemap[ymzx__wfvaa.value.name],
                    types.npytypes.Array)):
                    ymzx__wfvaa = stmt.value
                    sqvml__miys = ymzx__wfvaa.value
                    yhcg__gxio[qjb__zmzx] = sqvml__miys
                    scope = sqvml__miys.scope
                    loc = sqvml__miys.loc
                    kliro__efjo = ir.Var(scope, mk_unique_var('$np_g_var'), loc
                        )
                    typemap[kliro__efjo.name] = types.misc.Module(numpy)
                    ghls__mid = ir.Global('np', numpy, loc)
                    zdh__gppnj = ir.Assign(ghls__mid, kliro__efjo, loc)
                    ymzx__wfvaa.value = kliro__efjo
                    wug__jwzx.append(zdh__gppnj)
                    func_ir._definitions[kliro__efjo.name] = [ghls__mid]
                    func = getattr(numpy, ymzx__wfvaa.attr)
                    fwu__txh = get_np_ufunc_typ_lst(func)
                    djo__wfamq[qjb__zmzx] = fwu__txh
                if (ymzx__wfvaa.op == 'call' and ymzx__wfvaa.func.name in
                    yhcg__gxio):
                    sqvml__miys = yhcg__gxio[ymzx__wfvaa.func.name]
                    uqoe__foubq = calltypes.pop(ymzx__wfvaa)
                    fgzk__qsgxp = uqoe__foubq.args[:len(ymzx__wfvaa.args)]
                    qqfc__wkr = {name: typemap[oin__dfmu.name] for name,
                        oin__dfmu in ymzx__wfvaa.kws}
                    jrwv__yrm = djo__wfamq[ymzx__wfvaa.func.name]
                    dwr__rfm = None
                    for deb__rlg in jrwv__yrm:
                        try:
                            dwr__rfm = deb__rlg.get_call_type(typingctx, [
                                typemap[sqvml__miys.name]] + list(
                                fgzk__qsgxp), qqfc__wkr)
                            typemap.pop(ymzx__wfvaa.func.name)
                            typemap[ymzx__wfvaa.func.name] = deb__rlg
                            calltypes[ymzx__wfvaa] = dwr__rfm
                            break
                        except Exception as sww__zsdv:
                            pass
                    if dwr__rfm is None:
                        raise TypeError(
                            f'No valid template found for {ymzx__wfvaa.func.name}'
                            )
                    ymzx__wfvaa.args = [sqvml__miys] + ymzx__wfvaa.args
            wug__jwzx.append(stmt)
        block.body = wug__jwzx


if _check_numba_change:
    lines = inspect.getsource(numba.core.ir_utils.canonicalize_array_math)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'b2200e9100613631cc554f4b640bc1181ba7cea0ece83630122d15b86941be2e':
        warnings.warn('canonicalize_array_math has changed')
numba.core.ir_utils.canonicalize_array_math = canonicalize_array_math
numba.parfors.parfor.canonicalize_array_math = canonicalize_array_math
numba.core.inline_closurecall.canonicalize_array_math = canonicalize_array_math


def _Numpy_Rules_ufunc_handle_inputs(cls, ufunc, args, kws):
    bubbz__frmix = ufunc.nin
    txu__gqh = ufunc.nout
    fsk__ofzr = ufunc.nargs
    assert fsk__ofzr == bubbz__frmix + txu__gqh
    if len(args) < bubbz__frmix:
        msg = "ufunc '{0}': not enough arguments ({1} found, {2} required)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args),
            bubbz__frmix))
    if len(args) > fsk__ofzr:
        msg = "ufunc '{0}': too many arguments ({1} found, {2} maximum)"
        raise TypingError(msg=msg.format(ufunc.__name__, len(args), fsk__ofzr))
    args = [(a.as_array if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else a) for a in args]
    spy__kpu = [(a.ndim if isinstance(a, types.ArrayCompatible) and not
        isinstance(a, types.Bytes) else 0) for a in args]
    nstoa__qplb = max(spy__kpu)
    qappp__weo = args[bubbz__frmix:]
    if not all(d == nstoa__qplb for d in spy__kpu[bubbz__frmix:]):
        msg = "ufunc '{0}' called with unsuitable explicit output arrays."
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(isinstance(fqa__owa, types.ArrayCompatible) and not
        isinstance(fqa__owa, types.Bytes) for fqa__owa in qappp__weo):
        msg = "ufunc '{0}' called with an explicit output that is not an array"
        raise TypingError(msg=msg.format(ufunc.__name__))
    if not all(fqa__owa.mutable for fqa__owa in qappp__weo):
        msg = "ufunc '{0}' called with an explicit output that is read-only"
        raise TypingError(msg=msg.format(ufunc.__name__))
    lkpv__pafz = [(x.dtype if isinstance(x, types.ArrayCompatible) and not
        isinstance(x, types.Bytes) else x) for x in args]
    njtje__losyn = None
    if nstoa__qplb > 0 and len(qappp__weo) < ufunc.nout:
        njtje__losyn = 'C'
        ysr__jwpq = [(x.layout if isinstance(x, types.ArrayCompatible) and 
            not isinstance(x, types.Bytes) else '') for x in args]
        if 'C' not in ysr__jwpq and 'F' in ysr__jwpq:
            njtje__losyn = 'F'
    return lkpv__pafz, qappp__weo, nstoa__qplb, njtje__losyn


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
        osewm__cact = 'Dict.key_type cannot be of type {}'
        raise TypingError(osewm__cact.format(keyty))
    if isinstance(valty, (Optional, NoneType)):
        osewm__cact = 'Dict.value_type cannot be of type {}'
        raise TypingError(osewm__cact.format(valty))
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
    dnpa__ugcv = self.context, tuple(args), tuple(kws.items())
    try:
        impl, args = self._impl_cache[dnpa__ugcv]
        return impl, args
    except KeyError as sww__zsdv:
        pass
    impl, args = self._build_impl(dnpa__ugcv, args, kws)
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
        gynra__oya = find_topo_order(parfor.loop_body)
    jbqe__hcd = gynra__oya[0]
    wgx__tmfly = {}
    _update_parfor_get_setitems(parfor.loop_body[jbqe__hcd].body, parfor.
        index_var, alias_map, wgx__tmfly, lives_n_aliases)
    gceu__pye = set(wgx__tmfly.keys())
    for ojd__imq in gynra__oya:
        if ojd__imq == jbqe__hcd:
            continue
        for stmt in parfor.loop_body[ojd__imq].body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.
                Expr) and stmt.value.op == 'getitem' and stmt.value.index.
                name == parfor.index_var.name):
                continue
            rqwir__pjav = set(oin__dfmu.name for oin__dfmu in stmt.list_vars())
            gpr__ldrh = rqwir__pjav & gceu__pye
            for a in gpr__ldrh:
                wgx__tmfly.pop(a, None)
    for ojd__imq in gynra__oya:
        if ojd__imq == jbqe__hcd:
            continue
        block = parfor.loop_body[ojd__imq]
        dmtbi__ksxz = wgx__tmfly.copy()
        _update_parfor_get_setitems(block.body, parfor.index_var, alias_map,
            dmtbi__ksxz, lives_n_aliases)
    blocks = parfor.loop_body.copy()
    rtz__agl = max(blocks.keys())
    pdi__lbup, npu__pjda = _add_liveness_return_block(blocks,
        lives_n_aliases, typemap)
    wyk__iwity = ir.Jump(pdi__lbup, ir.Loc('parfors_dummy', -1))
    blocks[rtz__agl].body.append(wyk__iwity)
    yyrav__glvnp = compute_cfg_from_blocks(blocks)
    uagw__geszx = compute_use_defs(blocks)
    fiz__dab = compute_live_map(yyrav__glvnp, blocks, uagw__geszx.usemap,
        uagw__geszx.defmap)
    alias_set = set(alias_map.keys())
    for jqh__btri, block in blocks.items():
        wug__jwzx = []
        ukkn__lmdcq = {oin__dfmu.name for oin__dfmu in block.terminator.
            list_vars()}
        for rwt__lhelf, dblup__ywiw in yyrav__glvnp.successors(jqh__btri):
            ukkn__lmdcq |= fiz__dab[rwt__lhelf]
        for stmt in reversed(block.body):
            cqcph__zrvai = ukkn__lmdcq & alias_set
            for oin__dfmu in cqcph__zrvai:
                ukkn__lmdcq |= alias_map[oin__dfmu]
            if (isinstance(stmt, (ir.StaticSetItem, ir.SetItem)) and 
                get_index_var(stmt).name == parfor.index_var.name and stmt.
                target.name not in ukkn__lmdcq and stmt.target.name not in
                arg_aliases):
                continue
            elif isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr
                ) and stmt.value.op == 'call':
                qhe__qgwh = guard(find_callname, func_ir, stmt.value)
                if qhe__qgwh == ('setna', 'bodo.libs.array_kernels'
                    ) and stmt.value.args[0
                    ].name not in ukkn__lmdcq and stmt.value.args[0
                    ].name not in arg_aliases:
                    continue
            ukkn__lmdcq |= {oin__dfmu.name for oin__dfmu in stmt.list_vars()}
            wug__jwzx.append(stmt)
        wug__jwzx.reverse()
        block.body = wug__jwzx
    typemap.pop(npu__pjda.name)
    blocks[rtz__agl].body.pop()

    def trim_empty_parfor_branches(parfor):
        gkkd__fde = False
        blocks = parfor.loop_body.copy()
        for jqh__btri, block in blocks.items():
            if len(block.body):
                bkz__quega = block.body[-1]
                if isinstance(bkz__quega, ir.Branch):
                    if len(blocks[bkz__quega.truebr].body) == 1 and len(blocks
                        [bkz__quega.falsebr].body) == 1:
                        fnqf__szyrh = blocks[bkz__quega.truebr].body[0]
                        xbqm__bpdov = blocks[bkz__quega.falsebr].body[0]
                        if isinstance(fnqf__szyrh, ir.Jump) and isinstance(
                            xbqm__bpdov, ir.Jump
                            ) and fnqf__szyrh.target == xbqm__bpdov.target:
                            parfor.loop_body[jqh__btri].body[-1] = ir.Jump(
                                fnqf__szyrh.target, bkz__quega.loc)
                            gkkd__fde = True
                    elif len(blocks[bkz__quega.truebr].body) == 1:
                        fnqf__szyrh = blocks[bkz__quega.truebr].body[0]
                        if isinstance(fnqf__szyrh, ir.Jump
                            ) and fnqf__szyrh.target == bkz__quega.falsebr:
                            parfor.loop_body[jqh__btri].body[-1] = ir.Jump(
                                fnqf__szyrh.target, bkz__quega.loc)
                            gkkd__fde = True
                    elif len(blocks[bkz__quega.falsebr].body) == 1:
                        xbqm__bpdov = blocks[bkz__quega.falsebr].body[0]
                        if isinstance(xbqm__bpdov, ir.Jump
                            ) and xbqm__bpdov.target == bkz__quega.truebr:
                            parfor.loop_body[jqh__btri].body[-1] = ir.Jump(
                                xbqm__bpdov.target, bkz__quega.loc)
                            gkkd__fde = True
        return gkkd__fde
    gkkd__fde = True
    while gkkd__fde:
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
        gkkd__fde = trim_empty_parfor_branches(parfor)
    sqbnb__sxqg = len(parfor.init_block.body) == 0
    for block in parfor.loop_body.values():
        sqbnb__sxqg &= len(block.body) == 0
    if sqbnb__sxqg:
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
    ciee__ebi = 0
    for block in blocks.values():
        for stmt in block.body:
            if isinstance(stmt, Parfor):
                ciee__ebi += 1
                parfor = stmt
                gru__cpa = parfor.loop_body[max(parfor.loop_body.keys())]
                scope = gru__cpa.scope
                loc = ir.Loc('parfors_dummy', -1)
                jps__mfb = ir.Var(scope, mk_unique_var('$const'), loc)
                gru__cpa.body.append(ir.Assign(ir.Const(0, loc), jps__mfb, loc)
                    )
                gru__cpa.body.append(ir.Return(jps__mfb, loc))
                yyrav__glvnp = compute_cfg_from_blocks(parfor.loop_body)
                for rmb__exmc in yyrav__glvnp.dead_nodes():
                    del parfor.loop_body[rmb__exmc]
                parfor.loop_body = simplify_CFG(parfor.loop_body)
                gru__cpa = parfor.loop_body[max(parfor.loop_body.keys())]
                gru__cpa.body.pop()
                gru__cpa.body.pop()
                simplify_parfor_body_CFG(parfor.loop_body)
    return ciee__ebi


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
            dzq__itcq = self.overloads.get(tuple(args))
            if dzq__itcq is not None:
                return dzq__itcq.entry_point
            self._pre_compile(args, return_type, flags)
            zas__cfe = self.func_ir
            veoz__hfavi = dict(dispatcher=self, args=args, return_type=
                return_type)
            with ev.trigger_event('numba:compile', data=veoz__hfavi):
                cres = compiler.compile_ir(typingctx=self.typingctx,
                    targetctx=self.targetctx, func_ir=zas__cfe, args=args,
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
        lkjd__yuc = copy.deepcopy(flags)
        lkjd__yuc.no_rewrites = True

        def compile_local(the_ir, the_flags):
            knmxe__ggzp = pipeline_class(typingctx, targetctx, library,
                args, return_type, the_flags, locals)
            return knmxe__ggzp.compile_ir(func_ir=the_ir, lifted=lifted,
                lifted_from=lifted_from)
        kspb__njg = compile_local(func_ir, lkjd__yuc)
        hfnx__asb = None
        if not flags.no_rewrites:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', errors.NumbaWarning)
                try:
                    hfnx__asb = compile_local(func_ir, flags)
                except Exception as sww__zsdv:
                    pass
        if hfnx__asb is not None:
            cres = hfnx__asb
        else:
            cres = kspb__njg
        return cres
    else:
        knmxe__ggzp = pipeline_class(typingctx, targetctx, library, args,
            return_type, flags, locals)
        return knmxe__ggzp.compile_ir(func_ir=func_ir, lifted=lifted,
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
    tuw__ltj = self.get_data_type(typ.dtype)
    xlen__yqth = 10 ** 7
    if self.allow_dynamic_globals and (typ.layout not in 'FC' or ary.nbytes >
        xlen__yqth):
        rmn__xien = ary.ctypes.data
        xyr__pau = self.add_dynamic_addr(builder, rmn__xien, info=str(type(
            rmn__xien)))
        awcxb__tublp = self.add_dynamic_addr(builder, id(ary), info=str(
            type(ary)))
        self.global_arrays.append(ary)
    else:
        czh__rco = ary.flatten(order=typ.layout)
        if isinstance(typ.dtype, (types.NPDatetime, types.NPTimedelta)):
            czh__rco = czh__rco.view('int64')
        val = bytearray(czh__rco.data)
        rxo__zbn = lir.Constant(lir.ArrayType(lir.IntType(8), len(val)), val)
        xyr__pau = cgutils.global_constant(builder, '.const.array.data',
            rxo__zbn)
        xyr__pau.align = self.get_abi_alignment(tuw__ltj)
        awcxb__tublp = None
    pnolc__fxa = self.get_value_type(types.intp)
    biba__qvc = [self.get_constant(types.intp, qgt__kwn) for qgt__kwn in
        ary.shape]
    ovrey__dzhyg = lir.Constant(lir.ArrayType(pnolc__fxa, len(biba__qvc)),
        biba__qvc)
    bre__hazil = [self.get_constant(types.intp, qgt__kwn) for qgt__kwn in
        ary.strides]
    feq__rvnon = lir.Constant(lir.ArrayType(pnolc__fxa, len(bre__hazil)),
        bre__hazil)
    duh__cor = self.get_constant(types.intp, ary.dtype.itemsize)
    pgxi__twg = self.get_constant(types.intp, math.prod(ary.shape))
    return lir.Constant.literal_struct([self.get_constant_null(types.
        MemInfoPointer(typ.dtype)), self.get_constant_null(types.pyobject),
        pgxi__twg, duh__cor, xyr__pau.bitcast(self.get_value_type(types.
        CPointer(typ.dtype))), ovrey__dzhyg, feq__rvnon])


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
    rjk__pfgtx = lir.FunctionType(_word_type, [_word_type.as_pointer()])
    clba__iky = lir.Function(module, rjk__pfgtx, name='nrt_atomic_{0}'.
        format(op))
    [kbplh__jte] = clba__iky.args
    vgkwq__ulvhr = clba__iky.append_basic_block()
    builder = lir.IRBuilder(vgkwq__ulvhr)
    idhda__cptu = lir.Constant(_word_type, 1)
    if False:
        jaqq__oouw = builder.atomic_rmw(op, kbplh__jte, idhda__cptu,
            ordering=ordering)
        res = getattr(builder, op)(jaqq__oouw, idhda__cptu)
        builder.ret(res)
    else:
        jaqq__oouw = builder.load(kbplh__jte)
        eyi__ztv = getattr(builder, op)(jaqq__oouw, idhda__cptu)
        xcxju__klk = builder.icmp_signed('!=', jaqq__oouw, lir.Constant(
            jaqq__oouw.type, -1))
        with cgutils.if_likely(builder, xcxju__klk):
            builder.store(eyi__ztv, kbplh__jte)
        builder.ret(eyi__ztv)
    return clba__iky


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
        tkvlj__fzo = state.targetctx.codegen()
        state.library = tkvlj__fzo.create_library(state.func_id.func_qualname)
        state.library.enable_object_caching()
    library = state.library
    targetctx = state.targetctx
    sohre__qpvl = state.func_ir
    typemap = state.typemap
    zqjw__sefvt = state.return_type
    calltypes = state.calltypes
    flags = state.flags
    metadata = state.metadata
    xqux__quenx = llvm.passmanagers.dump_refprune_stats()
    msg = 'Function %s failed at nopython mode lowering' % (state.func_id.
        func_name,)
    with fallback_context(state, msg):
        fndesc = funcdesc.PythonFunctionDescriptor.from_specialized_function(
            sohre__qpvl, typemap, zqjw__sefvt, calltypes, mangler=targetctx
            .mangler, inline=flags.forceinline, noalias=flags.noalias,
            abi_tags=[flags.get_mangle_string()])
        targetctx.global_arrays = []
        with targetctx.push_code_library(library):
            iqe__aysl = lowering.Lower(targetctx, library, fndesc,
                sohre__qpvl, metadata=metadata)
            iqe__aysl.lower()
            if not flags.no_cpython_wrapper:
                iqe__aysl.create_cpython_wrapper(flags.release_gil)
            if not flags.no_cfunc_wrapper:
                for t in state.args:
                    if isinstance(t, (types.Omitted, types.Generator)):
                        break
                else:
                    if isinstance(zqjw__sefvt, (types.Optional, types.
                        Generator)):
                        pass
                    else:
                        iqe__aysl.create_cfunc_wrapper()
            env = iqe__aysl.env
            eaut__iika = iqe__aysl.call_helper
            del iqe__aysl
        from numba.core.compiler import _LowerResult
        if flags.no_compile:
            state['cr'] = _LowerResult(fndesc, eaut__iika, cfunc=None, env=env)
        else:
            vrzo__nca = targetctx.get_executable(library, fndesc, env)
            targetctx.insert_user_function(vrzo__nca, fndesc, [library])
            state['cr'] = _LowerResult(fndesc, eaut__iika, cfunc=vrzo__nca,
                env=env)
        metadata['global_arrs'] = targetctx.global_arrays
        targetctx.global_arrays = []
        kmd__wwso = llvm.passmanagers.dump_refprune_stats()
        metadata['prune_stats'] = kmd__wwso - xqux__quenx
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
        stl__qyoql = nth.typeof(itemobj)
        with c.builder.if_then(cgutils.is_null(c.builder, stl__qyoql),
            likely=False):
            c.builder.store(cgutils.true_bit, errorptr)
            vpnd__jiw.do_break()
        svbsu__anlj = c.builder.icmp_signed('!=', stl__qyoql, expected_typobj)
        if not isinstance(typ.dtype, types.Optional):
            with c.builder.if_then(svbsu__anlj, likely=False):
                c.builder.store(cgutils.true_bit, errorptr)
                c.pyapi.err_format('PyExc_TypeError',
                    "can't unbox heterogeneous list: %S != %S",
                    expected_typobj, stl__qyoql)
                c.pyapi.decref(stl__qyoql)
                vpnd__jiw.do_break()
        c.pyapi.decref(stl__qyoql)
    csjz__zxz, list = listobj.ListInstance.allocate_ex(c.context, c.builder,
        typ, size)
    with c.builder.if_else(csjz__zxz, likely=True) as (pvgie__hqs, zsfsk__pjw):
        with pvgie__hqs:
            list.size = size
            vgnzb__eveq = lir.Constant(size.type, 0)
            with c.builder.if_then(c.builder.icmp_signed('>', size,
                vgnzb__eveq), likely=True):
                with _NumbaTypeHelper(c) as nth:
                    expected_typobj = nth.typeof(c.pyapi.list_getitem(obj,
                        vgnzb__eveq))
                    with cgutils.for_range(c.builder, size) as vpnd__jiw:
                        itemobj = c.pyapi.list_getitem(obj, vpnd__jiw.index)
                        check_element_type(nth, itemobj, expected_typobj)
                        oubtq__dzpy = c.unbox(typ.dtype, itemobj)
                        with c.builder.if_then(oubtq__dzpy.is_error, likely
                            =False):
                            c.builder.store(cgutils.true_bit, errorptr)
                            vpnd__jiw.do_break()
                        list.setitem(vpnd__jiw.index, oubtq__dzpy.value,
                            incref=False)
                    c.pyapi.decref(expected_typobj)
            if typ.reflected:
                list.parent = obj
            with c.builder.if_then(c.builder.not_(c.builder.load(errorptr)),
                likely=False):
                c.pyapi.object_set_private_data(obj, list.meminfo)
            list.set_dirty(False)
            c.builder.store(list.value, listptr)
        with zsfsk__pjw:
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
    snswj__kbys, kaqy__acly, pyszr__voes, wfaal__vzncv, gwms__dgdw = (
        compile_time_get_string_data(literal_string))
    mmga__sjvps = builder.module
    gv = context.insert_const_bytes(mmga__sjvps, snswj__kbys)
    return lir.Constant.literal_struct([gv, context.get_constant(types.intp,
        kaqy__acly), context.get_constant(types.int32, pyszr__voes),
        context.get_constant(types.uint32, wfaal__vzncv), context.
        get_constant(_Py_hash_t, -1), context.get_constant_null(types.
        MemInfoPointer(types.voidptr)), context.get_constant_null(types.
        pyobject)])


if _check_numba_change:
    lines = inspect.getsource(numba.cpython.unicode.make_string_from_constant)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != '525bd507383e06152763e2f046dae246cd60aba027184f50ef0fc9a80d4cd7fa':
        warnings.warn(
            'numba.cpython.unicode.make_string_from_constant has changed')
numba.cpython.unicode.make_string_from_constant = make_string_from_constant


def parse_shape(shape):
    hwq__khalj = None
    if isinstance(shape, types.Integer):
        hwq__khalj = 1
    elif isinstance(shape, (types.Tuple, types.UniTuple)):
        if all(isinstance(qgt__kwn, (types.Integer, types.IntEnumMember)) for
            qgt__kwn in shape):
            hwq__khalj = len(shape)
    return hwq__khalj


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
            hwq__khalj = typ.ndim if isinstance(typ, types.ArrayCompatible
                ) else len(typ)
            if hwq__khalj == 0:
                return name,
            else:
                return tuple('{}#{}'.format(name, i) for i in range(hwq__khalj)
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
            bll__yexgr = self._get_names(x)
            if len(bll__yexgr) != 0:
                return bll__yexgr[0]
            return bll__yexgr
        return tuple(get_names(x) for x in obj)
    elif isinstance(obj, int):
        return obj,
    return ()


def get_equiv_const(self, obj):
    bll__yexgr = self._get_names(obj)
    if len(bll__yexgr) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_const(bll__yexgr[0])


def get_equiv_set(self, obj):
    bll__yexgr = self._get_names(obj)
    if len(bll__yexgr) != 1:
        return None
    return super(numba.parfors.array_analysis.ShapeEquivSet, self
        ).get_equiv_set(bll__yexgr[0])


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
    iuxud__jgt = []
    for gpt__keer in func_ir.arg_names:
        if gpt__keer in typemap and isinstance(typemap[gpt__keer], types.
            containers.UniTuple) and typemap[gpt__keer].count > 1000:
            msg = (
                """Tuple '{}' length must be smaller than 1000.
Large tuples lead to the generation of a prohibitively large LLVM IR which causes excessive memory pressure and large compile times.
As an alternative, the use of a 'list' is recommended in place of a 'tuple' as lists do not suffer from this problem."""
                .format(gpt__keer))
            raise errors.UnsupportedError(msg, func_ir.loc)
    for dvc__coatb in func_ir.blocks.values():
        for stmt in dvc__coatb.find_insts(ir.Assign):
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'make_function':
                    val = stmt.value
                    vaoo__raang = getattr(val, 'code', None)
                    if vaoo__raang is not None:
                        if getattr(val, 'closure', None) is not None:
                            swyr__mzj = '<creating a function from a closure>'
                            baovm__pvlaz = ''
                        else:
                            swyr__mzj = vaoo__raang.co_name
                            baovm__pvlaz = '(%s) ' % swyr__mzj
                    else:
                        swyr__mzj = '<could not ascertain use case>'
                        baovm__pvlaz = ''
                    msg = (
                        'Numba encountered the use of a language feature it does not support in this context: %s (op code: make_function not supported). If the feature is explicitly supported it is likely that the result of the expression %sis being used in an unsupported manner.'
                         % (swyr__mzj, baovm__pvlaz))
                    raise errors.UnsupportedError(msg, stmt.value.loc)
            if isinstance(stmt.value, (ir.Global, ir.FreeVar)):
                val = stmt.value
                val = getattr(val, 'value', None)
                if val is None:
                    continue
                cjm__ilc = False
                if isinstance(val, pytypes.FunctionType):
                    cjm__ilc = val in {numba.gdb, numba.gdb_init}
                if not cjm__ilc:
                    cjm__ilc = getattr(val, '_name', '') == 'gdb_internal'
                if cjm__ilc:
                    iuxud__jgt.append(stmt.loc)
            if isinstance(stmt.value, ir.Expr):
                if stmt.value.op == 'getattr' and stmt.value.attr == 'view':
                    var = stmt.value.value.name
                    if isinstance(typemap[var], types.Array):
                        continue
                    cepx__syok = func_ir.get_definition(var)
                    nqvsy__atfo = guard(find_callname, func_ir, cepx__syok)
                    if nqvsy__atfo and nqvsy__atfo[1] == 'numpy':
                        ty = getattr(numpy, nqvsy__atfo[0])
                        if numpy.issubdtype(ty, numpy.integer
                            ) or numpy.issubdtype(ty, numpy.floating):
                            continue
                    uwyse__eojoa = '' if var.startswith('$'
                        ) else "'{}' ".format(var)
                    raise TypingError(
                        "'view' can only be called on NumPy dtypes, try wrapping the variable {}with 'np.<dtype>()'"
                        .format(uwyse__eojoa), loc=stmt.loc)
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
    if len(iuxud__jgt) > 1:
        msg = """Calling either numba.gdb() or numba.gdb_init() more than once in a function is unsupported (strange things happen!), use numba.gdb_breakpoint() to create additional breakpoints instead.

Relevant documentation is available here:
https://numba.pydata.org/numba-doc/latest/user/troubleshoot.html/troubleshoot.html#using-numba-s-direct-gdb-bindings-in-nopython-mode

Conflicting calls found at:
 %s"""
        hoj__hgz = '\n'.join([x.strformat() for x in iuxud__jgt])
        raise errors.UnsupportedError(msg % hoj__hgz)


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
    lrau__xmn, oin__dfmu = next(iter(val.items()))
    hmkca__beiy = typeof_impl(lrau__xmn, c)
    bbqq__xrg = typeof_impl(oin__dfmu, c)
    if hmkca__beiy is None or bbqq__xrg is None:
        raise ValueError(
            f'Cannot type dict element type {type(lrau__xmn)}, {type(oin__dfmu)}'
            )
    return types.DictType(hmkca__beiy, bbqq__xrg)


def unbox_dicttype(typ, val, c):
    from llvmlite import ir as lir
    from numba.typed import dictobject
    from numba.typed.typeddict import Dict
    context = c.context
    dmj__uvuea = cgutils.alloca_once_value(c.builder, val)
    tqe__afzn = c.pyapi.object_hasattr_string(val, '_opaque')
    hla__mgc = c.builder.icmp_unsigned('==', tqe__afzn, lir.Constant(
        tqe__afzn.type, 0))
    xzy__movs = typ.key_type
    vvc__eddwl = typ.value_type

    def make_dict():
        return numba.typed.Dict.empty(xzy__movs, vvc__eddwl)

    def copy_dict(out_dict, in_dict):
        for lrau__xmn, oin__dfmu in in_dict.items():
            out_dict[lrau__xmn] = oin__dfmu
    with c.builder.if_then(hla__mgc):
        gwl__yrzsk = c.pyapi.unserialize(c.pyapi.serialize_object(make_dict))
        czlzj__gnu = c.pyapi.call_function_objargs(gwl__yrzsk, [])
        smust__czzgh = c.pyapi.unserialize(c.pyapi.serialize_object(copy_dict))
        c.pyapi.call_function_objargs(smust__czzgh, [czlzj__gnu, val])
        c.builder.store(czlzj__gnu, dmj__uvuea)
    val = c.builder.load(dmj__uvuea)
    uxukd__oxko = c.pyapi.unserialize(c.pyapi.serialize_object(Dict))
    zos__aqtj = c.pyapi.object_type(val)
    mas__bzqhc = c.builder.icmp_unsigned('==', zos__aqtj, uxukd__oxko)
    with c.builder.if_else(mas__bzqhc) as (pqr__zgjx, mxi__xfo):
        with pqr__zgjx:
            shez__gev = c.pyapi.object_getattr_string(val, '_opaque')
            uau__zkq = types.MemInfoPointer(types.voidptr)
            oubtq__dzpy = c.unbox(uau__zkq, shez__gev)
            mi = oubtq__dzpy.value
            tjpxy__tecv = uau__zkq, typeof(typ)

            def convert(mi, typ):
                return dictobject._from_meminfo(mi, typ)
            sig = signature(typ, *tjpxy__tecv)
            rwvc__zsj = context.get_constant_null(tjpxy__tecv[1])
            args = mi, rwvc__zsj
            ksmb__pftjw, itk__caboq = c.pyapi.call_jit_code(convert, sig, args)
            c.context.nrt.decref(c.builder, typ, itk__caboq)
            c.pyapi.decref(shez__gev)
            osdfc__egqq = c.builder.basic_block
        with mxi__xfo:
            c.pyapi.err_format('PyExc_TypeError',
                "can't unbox a %S as a %S", zos__aqtj, uxukd__oxko)
            qjui__wpe = c.builder.basic_block
    xhsw__rehgs = c.builder.phi(itk__caboq.type)
    jtozj__ywr = c.builder.phi(ksmb__pftjw.type)
    xhsw__rehgs.add_incoming(itk__caboq, osdfc__egqq)
    xhsw__rehgs.add_incoming(itk__caboq.type(None), qjui__wpe)
    jtozj__ywr.add_incoming(ksmb__pftjw, osdfc__egqq)
    jtozj__ywr.add_incoming(cgutils.true_bit, qjui__wpe)
    c.pyapi.decref(uxukd__oxko)
    c.pyapi.decref(zos__aqtj)
    with c.builder.if_then(hla__mgc):
        c.pyapi.decref(val)
    return NativeValue(xhsw__rehgs, is_error=jtozj__ywr)


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
    nmn__zzhuk = ir.Expr.getattr(target, 'update', loc=self.loc)
    self.store(value=nmn__zzhuk, name=updatevar)
    aib__jbka = ir.Expr.call(self.get(updatevar), (value,), (), loc=self.loc)
    self.store(value=aib__jbka, name=res)


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
        for lrau__xmn, oin__dfmu in other.items():
            d[lrau__xmn] = oin__dfmu
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
    baovm__pvlaz = ir.Expr.call(func, [], [], loc=self.loc, vararg=vararg,
        varkwarg=varkwarg)
    self.store(baovm__pvlaz, res)


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
    ovacz__fbz = PassManager(name)
    if state.func_ir is None:
        ovacz__fbz.add_pass(TranslateByteCode, 'analyzing bytecode')
        if PYVERSION == (3, 10):
            ovacz__fbz.add_pass(Bodo310ByteCodePass,
                'Apply Python 3.10 bytecode changes')
        ovacz__fbz.add_pass(FixupArgs, 'fix up args')
    ovacz__fbz.add_pass(IRProcessing, 'processing IR')
    ovacz__fbz.add_pass(WithLifting, 'Handle with contexts')
    ovacz__fbz.add_pass(InlineClosureLikes,
        'inline calls to locally defined closures')
    if not state.flags.no_rewrites:
        ovacz__fbz.add_pass(RewriteSemanticConstants,
            'rewrite semantic constants')
        ovacz__fbz.add_pass(DeadBranchPrune, 'dead branch pruning')
        ovacz__fbz.add_pass(GenericRewrites, 'nopython rewrites')
    ovacz__fbz.add_pass(MakeFunctionToJitFunction,
        'convert make_function into JIT functions')
    ovacz__fbz.add_pass(InlineInlinables, 'inline inlinable functions')
    if not state.flags.no_rewrites:
        ovacz__fbz.add_pass(DeadBranchPrune, 'dead branch pruning')
    ovacz__fbz.add_pass(FindLiterallyCalls, 'find literally calls')
    ovacz__fbz.add_pass(LiteralUnroll, 'handles literal_unroll')
    if state.flags.enable_ssa:
        ovacz__fbz.add_pass(ReconstructSSA, 'ssa')
    ovacz__fbz.add_pass(LiteralPropagationSubPipelinePass,
        'Literal propagation')
    ovacz__fbz.finalize()
    return ovacz__fbz


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
    a, wcmrv__ydp = args
    if isinstance(a, types.List) and isinstance(wcmrv__ydp, types.Integer):
        return signature(a, a, types.intp)
    elif isinstance(a, types.Integer) and isinstance(wcmrv__ydp, types.List):
        return signature(wcmrv__ydp, types.intp, wcmrv__ydp)


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
        nhr__felp, wpwx__zjp = 0, 1
    else:
        nhr__felp, wpwx__zjp = 1, 0
    cmgb__pgmhx = ListInstance(context, builder, sig.args[nhr__felp], args[
        nhr__felp])
    mgts__wsdbt = cmgb__pgmhx.size
    fsz__dvywx = args[wpwx__zjp]
    vgnzb__eveq = lir.Constant(fsz__dvywx.type, 0)
    fsz__dvywx = builder.select(cgutils.is_neg_int(builder, fsz__dvywx),
        vgnzb__eveq, fsz__dvywx)
    pgxi__twg = builder.mul(fsz__dvywx, mgts__wsdbt)
    jga__wtqlc = ListInstance.allocate(context, builder, sig.return_type,
        pgxi__twg)
    jga__wtqlc.size = pgxi__twg
    with cgutils.for_range_slice(builder, vgnzb__eveq, pgxi__twg,
        mgts__wsdbt, inc=True) as (phk__tgf, _):
        with cgutils.for_range(builder, mgts__wsdbt) as vpnd__jiw:
            value = cmgb__pgmhx.getitem(vpnd__jiw.index)
            jga__wtqlc.setitem(builder.add(vpnd__jiw.index, phk__tgf),
                value, incref=True)
    return impl_ret_new_ref(context, builder, sig.return_type, jga__wtqlc.value
        )


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
    ryqid__kqhld = first.unify(self, second)
    if ryqid__kqhld is not None:
        return ryqid__kqhld
    ryqid__kqhld = second.unify(self, first)
    if ryqid__kqhld is not None:
        return ryqid__kqhld
    tkp__jty = self.can_convert(fromty=first, toty=second)
    if tkp__jty is not None and tkp__jty <= Conversion.safe:
        return second
    tkp__jty = self.can_convert(fromty=second, toty=first)
    if tkp__jty is not None and tkp__jty <= Conversion.safe:
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
    pgxi__twg = payload.used
    listobj = c.pyapi.list_new(pgxi__twg)
    csjz__zxz = cgutils.is_not_null(c.builder, listobj)
    with c.builder.if_then(csjz__zxz, likely=True):
        index = cgutils.alloca_once_value(c.builder, ir.Constant(pgxi__twg.
            type, 0))
        with payload._iterate() as vpnd__jiw:
            i = c.builder.load(index)
            item = vpnd__jiw.entry.key
            c.context.nrt.incref(c.builder, typ.dtype, item)
            itemobj = c.box(typ.dtype, item)
            c.pyapi.list_setitem(listobj, i, itemobj)
            i = c.builder.add(i, ir.Constant(i.type, 1))
            c.builder.store(i, index)
    return csjz__zxz, listobj


def _lookup(self, item, h, for_insert=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    iayf__vfjhg = h.type
    dere__gmme = self.mask
    dtype = self._ty.dtype
    lophg__poyrl = context.typing_context
    fnty = lophg__poyrl.resolve_value_type(operator.eq)
    sig = fnty.get_call_type(lophg__poyrl, (dtype, dtype), {})
    xhxsx__fgk = context.get_function(fnty, sig)
    cxt__ihwxb = ir.Constant(iayf__vfjhg, 1)
    msgc__uvn = ir.Constant(iayf__vfjhg, 5)
    ldidi__hihx = cgutils.alloca_once_value(builder, h)
    index = cgutils.alloca_once_value(builder, builder.and_(h, dere__gmme))
    if for_insert:
        qtgy__epwh = dere__gmme.type(-1)
        wced__vlu = cgutils.alloca_once_value(builder, qtgy__epwh)
    ijn__pcas = builder.append_basic_block('lookup.body')
    gmc__xaty = builder.append_basic_block('lookup.found')
    lhyx__fnr = builder.append_basic_block('lookup.not_found')
    wlajs__lwzdk = builder.append_basic_block('lookup.end')

    def check_entry(i):
        entry = self.get_entry(i)
        fva__niw = entry.hash
        with builder.if_then(builder.icmp_unsigned('==', h, fva__niw)):
            suutr__kove = xhxsx__fgk(builder, (item, entry.key))
            with builder.if_then(suutr__kove):
                builder.branch(gmc__xaty)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, fva__niw)):
            builder.branch(lhyx__fnr)
        if for_insert:
            with builder.if_then(numba.cpython.setobj.is_hash_deleted(
                context, builder, fva__niw)):
                dtw__nwivm = builder.load(wced__vlu)
                dtw__nwivm = builder.select(builder.icmp_unsigned('==',
                    dtw__nwivm, qtgy__epwh), i, dtw__nwivm)
                builder.store(dtw__nwivm, wced__vlu)
    with cgutils.for_range(builder, ir.Constant(iayf__vfjhg, numba.cpython.
        setobj.LINEAR_PROBES)):
        i = builder.load(index)
        check_entry(i)
        i = builder.add(i, cxt__ihwxb)
        i = builder.and_(i, dere__gmme)
        builder.store(i, index)
    builder.branch(ijn__pcas)
    with builder.goto_block(ijn__pcas):
        i = builder.load(index)
        check_entry(i)
        yvjbk__isbx = builder.load(ldidi__hihx)
        yvjbk__isbx = builder.lshr(yvjbk__isbx, msgc__uvn)
        i = builder.add(cxt__ihwxb, builder.mul(i, msgc__uvn))
        i = builder.and_(dere__gmme, builder.add(i, yvjbk__isbx))
        builder.store(i, index)
        builder.store(yvjbk__isbx, ldidi__hihx)
        builder.branch(ijn__pcas)
    with builder.goto_block(lhyx__fnr):
        if for_insert:
            i = builder.load(index)
            dtw__nwivm = builder.load(wced__vlu)
            i = builder.select(builder.icmp_unsigned('==', dtw__nwivm,
                qtgy__epwh), i, dtw__nwivm)
            builder.store(i, index)
        builder.branch(wlajs__lwzdk)
    with builder.goto_block(gmc__xaty):
        builder.branch(wlajs__lwzdk)
    builder.position_at_end(wlajs__lwzdk)
    cjm__ilc = builder.phi(ir.IntType(1), 'found')
    cjm__ilc.add_incoming(cgutils.true_bit, gmc__xaty)
    cjm__ilc.add_incoming(cgutils.false_bit, lhyx__fnr)
    return cjm__ilc, builder.load(index)


def _add_entry(self, payload, entry, item, h, do_resize=True):
    context = self._context
    builder = self._builder
    rrk__ywt = entry.hash
    entry.hash = h
    context.nrt.incref(builder, self._ty.dtype, item)
    entry.key = item
    sjs__zsg = payload.used
    cxt__ihwxb = ir.Constant(sjs__zsg.type, 1)
    sjs__zsg = payload.used = builder.add(sjs__zsg, cxt__ihwxb)
    with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
        builder, rrk__ywt), likely=True):
        payload.fill = builder.add(payload.fill, cxt__ihwxb)
    if do_resize:
        self.upsize(sjs__zsg)
    self.set_dirty(True)


def _add_key(self, payload, item, h, do_resize=True):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    cjm__ilc, i = payload._lookup(item, h, for_insert=True)
    wsbrc__xmi = builder.not_(cjm__ilc)
    with builder.if_then(wsbrc__xmi):
        entry = payload.get_entry(i)
        rrk__ywt = entry.hash
        entry.hash = h
        context.nrt.incref(builder, self._ty.dtype, item)
        entry.key = item
        sjs__zsg = payload.used
        cxt__ihwxb = ir.Constant(sjs__zsg.type, 1)
        sjs__zsg = payload.used = builder.add(sjs__zsg, cxt__ihwxb)
        with builder.if_then(numba.cpython.setobj.is_hash_empty(context,
            builder, rrk__ywt), likely=True):
            payload.fill = builder.add(payload.fill, cxt__ihwxb)
        if do_resize:
            self.upsize(sjs__zsg)
        self.set_dirty(True)


def _remove_entry(self, payload, entry, do_resize=True):
    from llvmlite import ir
    entry.hash = ir.Constant(entry.hash.type, numba.cpython.setobj.DELETED)
    self._context.nrt.decref(self._builder, self._ty.dtype, entry.key)
    sjs__zsg = payload.used
    cxt__ihwxb = ir.Constant(sjs__zsg.type, 1)
    sjs__zsg = payload.used = self._builder.sub(sjs__zsg, cxt__ihwxb)
    if do_resize:
        self.downsize(sjs__zsg)
    self.set_dirty(True)


def pop(self):
    context = self._context
    builder = self._builder
    ezy__xsbub = context.get_value_type(self._ty.dtype)
    key = cgutils.alloca_once(builder, ezy__xsbub)
    payload = self.payload
    with payload._next_entry() as entry:
        builder.store(entry.key, key)
        context.nrt.incref(builder, self._ty.dtype, entry.key)
        self._remove_entry(payload, entry)
    return builder.load(key)


def _resize(self, payload, nentries, errmsg):
    context = self._context
    builder = self._builder
    ptd__pbt = payload
    csjz__zxz = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(csjz__zxz), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (errmsg,))
    payload = self.payload
    with ptd__pbt._iterate() as vpnd__jiw:
        entry = vpnd__jiw.entry
        self._add_key(payload, entry.key, entry.hash, do_resize=False)
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(ptd__pbt.ptr)


def _replace_payload(self, nentries):
    context = self._context
    builder = self._builder
    with self.payload._iterate() as vpnd__jiw:
        entry = vpnd__jiw.entry
        context.nrt.decref(builder, self._ty.dtype, entry.key)
    self._free_payload(self.payload.ptr)
    csjz__zxz = self._allocate_payload(nentries, realloc=True)
    with builder.if_then(builder.not_(csjz__zxz), likely=False):
        context.call_conv.return_user_exc(builder, MemoryError, (
            'cannot reallocate set',))


def _allocate_payload(self, nentries, realloc=False):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    csjz__zxz = cgutils.alloca_once_value(builder, cgutils.true_bit)
    iayf__vfjhg = context.get_value_type(types.intp)
    vgnzb__eveq = ir.Constant(iayf__vfjhg, 0)
    cxt__ihwxb = ir.Constant(iayf__vfjhg, 1)
    tdmx__bpc = context.get_data_type(types.SetPayload(self._ty))
    ptu__qbq = context.get_abi_sizeof(tdmx__bpc)
    jbn__hozxj = self._entrysize
    ptu__qbq -= jbn__hozxj
    fbqmz__mzae, jdrj__fmsp = cgutils.muladd_with_overflow(builder,
        nentries, ir.Constant(iayf__vfjhg, jbn__hozxj), ir.Constant(
        iayf__vfjhg, ptu__qbq))
    with builder.if_then(jdrj__fmsp, likely=False):
        builder.store(cgutils.false_bit, csjz__zxz)
    with builder.if_then(builder.load(csjz__zxz), likely=True):
        if realloc:
            mqeie__qbbce = self._set.meminfo
            kbplh__jte = context.nrt.meminfo_varsize_alloc(builder,
                mqeie__qbbce, size=fbqmz__mzae)
            askh__meshu = cgutils.is_null(builder, kbplh__jte)
        else:
            pzfe__wzdfo = _imp_dtor(context, builder.module, self._ty)
            mqeie__qbbce = context.nrt.meminfo_new_varsize_dtor(builder,
                fbqmz__mzae, builder.bitcast(pzfe__wzdfo, cgutils.voidptr_t))
            askh__meshu = cgutils.is_null(builder, mqeie__qbbce)
        with builder.if_else(askh__meshu, likely=False) as (jnv__kquyb,
            pvgie__hqs):
            with jnv__kquyb:
                builder.store(cgutils.false_bit, csjz__zxz)
            with pvgie__hqs:
                if not realloc:
                    self._set.meminfo = mqeie__qbbce
                    self._set.parent = context.get_constant_null(types.pyobject
                        )
                payload = self.payload
                cgutils.memset(builder, payload.ptr, fbqmz__mzae, 255)
                payload.used = vgnzb__eveq
                payload.fill = vgnzb__eveq
                payload.finger = vgnzb__eveq
                vqtdw__lshv = builder.sub(nentries, cxt__ihwxb)
                payload.mask = vqtdw__lshv
    return builder.load(csjz__zxz)


def _copy_payload(self, src_payload):
    from llvmlite import ir
    context = self._context
    builder = self._builder
    csjz__zxz = cgutils.alloca_once_value(builder, cgutils.true_bit)
    iayf__vfjhg = context.get_value_type(types.intp)
    vgnzb__eveq = ir.Constant(iayf__vfjhg, 0)
    cxt__ihwxb = ir.Constant(iayf__vfjhg, 1)
    tdmx__bpc = context.get_data_type(types.SetPayload(self._ty))
    ptu__qbq = context.get_abi_sizeof(tdmx__bpc)
    jbn__hozxj = self._entrysize
    ptu__qbq -= jbn__hozxj
    dere__gmme = src_payload.mask
    nentries = builder.add(cxt__ihwxb, dere__gmme)
    fbqmz__mzae = builder.add(ir.Constant(iayf__vfjhg, ptu__qbq), builder.
        mul(ir.Constant(iayf__vfjhg, jbn__hozxj), nentries))
    with builder.if_then(builder.load(csjz__zxz), likely=True):
        pzfe__wzdfo = _imp_dtor(context, builder.module, self._ty)
        mqeie__qbbce = context.nrt.meminfo_new_varsize_dtor(builder,
            fbqmz__mzae, builder.bitcast(pzfe__wzdfo, cgutils.voidptr_t))
        askh__meshu = cgutils.is_null(builder, mqeie__qbbce)
        with builder.if_else(askh__meshu, likely=False) as (jnv__kquyb,
            pvgie__hqs):
            with jnv__kquyb:
                builder.store(cgutils.false_bit, csjz__zxz)
            with pvgie__hqs:
                self._set.meminfo = mqeie__qbbce
                payload = self.payload
                payload.used = src_payload.used
                payload.fill = src_payload.fill
                payload.finger = vgnzb__eveq
                payload.mask = dere__gmme
                cgutils.raw_memcpy(builder, payload.entries, src_payload.
                    entries, nentries, jbn__hozxj)
                with src_payload._iterate() as vpnd__jiw:
                    context.nrt.incref(builder, self._ty.dtype, vpnd__jiw.
                        entry.key)
    return builder.load(csjz__zxz)


def _imp_dtor(context, module, set_type):
    from llvmlite import ir
    pmt__yhy = context.get_value_type(types.voidptr)
    oyu__ogzzj = context.get_value_type(types.uintp)
    fnty = ir.FunctionType(ir.VoidType(), [pmt__yhy, oyu__ogzzj, pmt__yhy])
    vgsmv__ohw = f'_numba_set_dtor_{set_type}'
    fn = cgutils.get_or_insert_function(module, fnty, name=vgsmv__ohw)
    if fn.is_declaration:
        fn.linkage = 'linkonce_odr'
        builder = ir.IRBuilder(fn.append_basic_block())
        vgxbs__ass = builder.bitcast(fn.args[0], cgutils.voidptr_t.as_pointer()
            )
        payload = numba.cpython.setobj._SetPayload(context, builder,
            set_type, vgxbs__ass)
        with payload._iterate() as vpnd__jiw:
            entry = vpnd__jiw.entry
            context.nrt.decref(builder, set_type.dtype, entry.key)
        builder.ret_void()
    return fn


@lower_builtin(set, types.IterableType)
def set_constructor(context, builder, sig, args):
    set_type = sig.return_type
    jep__svx, = sig.args
    qqf__skws, = args
    vrxj__spe = numba.core.imputils.call_len(context, builder, jep__svx,
        qqf__skws)
    inst = numba.cpython.setobj.SetInstance.allocate(context, builder,
        set_type, vrxj__spe)
    with numba.core.imputils.for_iter(context, builder, jep__svx, qqf__skws
        ) as vpnd__jiw:
        inst.add(vpnd__jiw.value)
        context.nrt.decref(builder, set_type.dtype, vpnd__jiw.value)
    return numba.core.imputils.impl_ret_new_ref(context, builder, set_type,
        inst.value)


@lower_builtin('set.update', types.Set, types.IterableType)
def set_update(context, builder, sig, args):
    inst = numba.cpython.setobj.SetInstance(context, builder, sig.args[0],
        args[0])
    jep__svx = sig.args[1]
    qqf__skws = args[1]
    vrxj__spe = numba.core.imputils.call_len(context, builder, jep__svx,
        qqf__skws)
    if vrxj__spe is not None:
        rgnbt__zjw = builder.add(inst.payload.used, vrxj__spe)
        inst.upsize(rgnbt__zjw)
    with numba.core.imputils.for_iter(context, builder, jep__svx, qqf__skws
        ) as vpnd__jiw:
        rxaz__mxll = context.cast(builder, vpnd__jiw.value, jep__svx.dtype,
            inst.dtype)
        inst.add(rxaz__mxll)
        context.nrt.decref(builder, jep__svx.dtype, vpnd__jiw.value)
    if vrxj__spe is not None:
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
    owiai__wbph = {key: value for key, value in self.metadata.items() if (
        'distributed' in key or 'replicated' in key) and key !=
        'distributed_diagnostics'}
    return (libdata, self.fndesc, self.environment, self.signature, self.
        objectmode, self.lifted, typeann, owiai__wbph, self.reload_init,
        tuple(referenced_envs))


@classmethod
def _rebuild(cls, target_context, libdata, fndesc, env, signature,
    objectmode, lifted, typeann, metadata, reload_init, referenced_envs):
    if reload_init:
        for fn in reload_init:
            fn()
    library = target_context.codegen().unserialize_library(libdata)
    vrzo__nca = target_context.get_executable(library, fndesc, env)
    vypx__puzeb = cls(target_context=target_context, typing_context=
        target_context.typing_context, library=library, environment=env,
        entry_point=vrzo__nca, fndesc=fndesc, type_annotation=typeann,
        signature=signature, objectmode=objectmode, lifted=lifted,
        typing_error=None, call_helper=None, metadata=metadata, reload_init
        =reload_init, referenced_envs=referenced_envs)
    for env in referenced_envs:
        library.codegen.set_env(env.env_name, env)
    return vypx__puzeb


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
        xgx__clp = MPI.COMM_WORLD
        tule__zfa = None
        if xgx__clp.Get_rank() == 0:
            try:
                qblvn__wnhv = self.get_cache_path()
                os.makedirs(qblvn__wnhv, exist_ok=True)
                tempfile.TemporaryFile(dir=qblvn__wnhv).close()
            except Exception as e:
                tule__zfa = e
        tule__zfa = xgx__clp.bcast(tule__zfa)
        if isinstance(tule__zfa, Exception):
            raise tule__zfa
    numba.core.caching._CacheLocator.ensure_cache_path = _ensure_cache_path
