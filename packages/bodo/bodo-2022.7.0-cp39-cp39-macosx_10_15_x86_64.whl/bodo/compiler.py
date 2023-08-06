"""
Defines Bodo's compiler pipeline.
"""
import os
import warnings
from collections import namedtuple
import numba
from numba.core import ir, ir_utils, types
from numba.core.compiler import DefaultPassBuilder
from numba.core.compiler_machinery import AnalysisPass, FunctionPass, register_pass
from numba.core.inline_closurecall import inline_closure_call
from numba.core.ir_utils import build_definitions, find_callname, get_definition, guard
from numba.core.registry import CPUDispatcher
from numba.core.typed_passes import DumpParforDiagnostics, InlineOverloads, IRLegalization, NopythonTypeInference, ParforPass, PreParforPass
from numba.core.untyped_passes import MakeFunctionToJitFunction, ReconstructSSA, WithLifting
import bodo
import bodo.hiframes.dataframe_indexing
import bodo.hiframes.datetime_datetime_ext
import bodo.hiframes.datetime_timedelta_ext
import bodo.io
import bodo.libs
import bodo.libs.array_kernels
import bodo.libs.int_arr_ext
import bodo.libs.re_ext
import bodo.libs.spark_extra
import bodo.transforms
import bodo.transforms.series_pass
import bodo.transforms.untyped_pass
import bodo.utils
import bodo.utils.table_utils
import bodo.utils.typing
from bodo.transforms.series_pass import SeriesPass
from bodo.transforms.table_column_del_pass import TableColumnDelPass
from bodo.transforms.typing_pass import BodoTypeInference
from bodo.transforms.untyped_pass import UntypedPass
from bodo.utils.utils import is_assign, is_call_assign, is_expr
numba.core.config.DISABLE_PERFORMANCE_WARNINGS = 1
from numba.core.errors import NumbaExperimentalFeatureWarning, NumbaPendingDeprecationWarning
warnings.simplefilter('ignore', category=NumbaExperimentalFeatureWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
inline_all_calls = False


class BodoCompiler(numba.core.compiler.CompilerBase):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=True,
            inline_calls_pass=inline_all_calls)

    def _create_bodo_pipeline(self, distributed=True, inline_calls_pass=
        False, udf_pipeline=False):
        fpid__lqu = 'bodo' if distributed else 'bodo_seq'
        fpid__lqu = fpid__lqu + '_inline' if inline_calls_pass else fpid__lqu
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, fpid__lqu)
        if inline_calls_pass:
            pm.add_pass_after(InlinePass, WithLifting)
        if udf_pipeline:
            pm.add_pass_after(ConvertCallsUDFPass, WithLifting)
        add_pass_before(pm, BodoUntypedPass, ReconstructSSA)
        replace_pass(pm, BodoTypeInference, NopythonTypeInference)
        remove_pass(pm, MakeFunctionToJitFunction)
        add_pass_before(pm, BodoSeriesPass, PreParforPass)
        if distributed:
            pm.add_pass_after(BodoDistributedPass, ParforPass)
        else:
            pm.add_pass_after(LowerParforSeq, ParforPass)
            pm.add_pass_after(LowerBodoIRExtSeq, LowerParforSeq)
        add_pass_before(pm, BodoTableColumnDelPass, IRLegalization)
        pm.add_pass_after(BodoDumpDistDiagnosticsPass, DumpParforDiagnostics)
        pm.finalize()
        return [pm]


def add_pass_before(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for cjpvb__vnodn, (wefst__ebpr, ttoxs__iexse) in enumerate(pm.passes):
        if wefst__ebpr == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(cjpvb__vnodn, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for cjpvb__vnodn, (wefst__ebpr, ttoxs__iexse) in enumerate(pm.passes):
        if wefst__ebpr == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[cjpvb__vnodn] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for cjpvb__vnodn, (wefst__ebpr, ttoxs__iexse) in enumerate(pm.passes):
        if wefst__ebpr == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(cjpvb__vnodn)
    pm._finalized = False


@register_pass(mutates_CFG=True, analysis_only=False)
class InlinePass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        inline_calls(state.func_ir, state.locals)
        state.func_ir.blocks = ir_utils.simplify_CFG(state.func_ir.blocks)
        return True


def _convert_bodo_dispatcher_to_udf(rhs, func_ir):
    aeyt__hhjps = guard(get_definition, func_ir, rhs.func)
    if isinstance(aeyt__hhjps, (ir.Global, ir.FreeVar, ir.Const)):
        etmea__bkafz = aeyt__hhjps.value
    else:
        zvx__xfq = guard(find_callname, func_ir, rhs)
        if not (zvx__xfq and isinstance(zvx__xfq[0], str) and isinstance(
            zvx__xfq[1], str)):
            return
        func_name, func_mod = zvx__xfq
        try:
            import importlib
            vny__mgmb = importlib.import_module(func_mod)
            etmea__bkafz = getattr(vny__mgmb, func_name)
        except:
            return
    if isinstance(etmea__bkafz, CPUDispatcher) and issubclass(etmea__bkafz.
        _compiler.pipeline_class, BodoCompiler
        ) and etmea__bkafz._compiler.pipeline_class != BodoCompilerUDF:
        etmea__bkafz._compiler.pipeline_class = BodoCompilerUDF
        etmea__bkafz.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for qlo__nrdm in block.body:
                if is_call_assign(qlo__nrdm):
                    _convert_bodo_dispatcher_to_udf(qlo__nrdm.value, state.
                        func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        wtr__lhz = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        wtr__lhz.run()
        return True


def _update_definitions(func_ir, node_list):
    imkq__dpidy = ir.Loc('', 0)
    nnkm__jpvl = ir.Block(ir.Scope(None, imkq__dpidy), imkq__dpidy)
    nnkm__jpvl.body = node_list
    build_definitions({(0): nnkm__jpvl}, func_ir._definitions)


_series_inline_attrs = {'values', 'shape', 'size', 'empty', 'name', 'index',
    'dtype'}
_series_no_inline_methods = {'to_list', 'tolist', 'rolling', 'to_csv',
    'count', 'fillna', 'to_dict', 'map', 'apply', 'pipe', 'combine',
    'bfill', 'ffill', 'pad', 'backfill', 'mask', 'where'}
_series_method_alias = {'isnull': 'isna', 'product': 'prod', 'kurtosis':
    'kurt', 'is_monotonic': 'is_monotonic_increasing', 'notnull': 'notna'}
_dataframe_no_inline_methods = {'apply', 'itertuples', 'pipe', 'to_parquet',
    'to_sql', 'to_csv', 'to_json', 'assign', 'to_string', 'query',
    'rolling', 'mask', 'where'}
TypingInfo = namedtuple('TypingInfo', ['typingctx', 'targetctx', 'typemap',
    'calltypes', 'curr_loc'])


def _inline_bodo_getattr(stmt, rhs, rhs_type, new_body, func_ir, typingctx,
    targetctx, typemap, calltypes):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import compile_func_single_block
    if isinstance(rhs_type, SeriesType) and rhs.attr in _series_inline_attrs:
        zttif__upp = 'overload_series_' + rhs.attr
        lsc__tkuj = getattr(bodo.hiframes.series_impl, zttif__upp)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        zttif__upp = 'overload_dataframe_' + rhs.attr
        lsc__tkuj = getattr(bodo.hiframes.dataframe_impl, zttif__upp)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    pqg__hvdci = lsc__tkuj(rhs_type)
    zeydw__kuuw = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc
        )
    hqrl__bbip = compile_func_single_block(pqg__hvdci, (rhs.value,), stmt.
        target, zeydw__kuuw)
    _update_definitions(func_ir, hqrl__bbip)
    new_body += hqrl__bbip
    return True


def _inline_bodo_call(rhs, i, func_mod, func_name, pass_info, new_body,
    block, typingctx, targetctx, calltypes, work_list):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.utils.transform import replace_func, update_locs
    func_ir = pass_info.func_ir
    typemap = pass_info.typemap
    if isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        SeriesType) and func_name not in _series_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        if (func_name in bodo.hiframes.series_impl.explicit_binop_funcs or 
            func_name.startswith('r') and func_name[1:] in bodo.hiframes.
            series_impl.explicit_binop_funcs):
            return False
        rhs.args.insert(0, func_mod)
        snequ__zloxr = tuple(typemap[ofskq__uzzl.name] for ofskq__uzzl in
            rhs.args)
        ldir__mfxmu = {fpid__lqu: typemap[ofskq__uzzl.name] for fpid__lqu,
            ofskq__uzzl in dict(rhs.kws).items()}
        pqg__hvdci = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*snequ__zloxr, **ldir__mfxmu)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        snequ__zloxr = tuple(typemap[ofskq__uzzl.name] for ofskq__uzzl in
            rhs.args)
        ldir__mfxmu = {fpid__lqu: typemap[ofskq__uzzl.name] for fpid__lqu,
            ofskq__uzzl in dict(rhs.kws).items()}
        pqg__hvdci = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*snequ__zloxr, **ldir__mfxmu)
    else:
        return False
    crpru__azk = replace_func(pass_info, pqg__hvdci, rhs.args, pysig=numba.
        core.utils.pysignature(pqg__hvdci), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    vcdt__guuna, ttoxs__iexse = inline_closure_call(func_ir, crpru__azk.
        glbls, block, len(new_body), crpru__azk.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=crpru__azk.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for ddlr__jwrhx in vcdt__guuna.values():
        ddlr__jwrhx.loc = rhs.loc
        update_locs(ddlr__jwrhx.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    ovmkd__gcwe = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = ovmkd__gcwe(func_ir, typemap)
    rqvxo__vbli = func_ir.blocks
    work_list = list((ocu__uvn, rqvxo__vbli[ocu__uvn]) for ocu__uvn in
        reversed(rqvxo__vbli.keys()))
    while work_list:
        rtns__ieibd, block = work_list.pop()
        new_body = []
        bpo__wig = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                zvx__xfq = guard(find_callname, func_ir, rhs, typemap)
                if zvx__xfq is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = zvx__xfq
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    bpo__wig = True
                    break
            new_body.append(stmt)
        if not bpo__wig:
            rqvxo__vbli[rtns__ieibd].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        asfl__cvi = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = asfl__cvi.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        ekaxf__noc = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        slz__ohj = ekaxf__noc.run()
        tby__gdxn = slz__ohj
        if tby__gdxn:
            tby__gdxn = ekaxf__noc.run()
        if tby__gdxn:
            ekaxf__noc.run()
        return slz__ohj


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        wtz__vbtv = 0
        dwv__vou = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            wtz__vbtv = int(os.environ[dwv__vou])
        except:
            pass
        if wtz__vbtv > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(wtz__vbtv, state
                .metadata)
        return True


class BodoCompilerSeq(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False,
            inline_calls_pass=inline_all_calls)


class BodoCompilerUDF(BodoCompiler):

    def define_pipelines(self):
        return self._create_bodo_pipeline(distributed=False, udf_pipeline=True)


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerParforSeq(FunctionPass):
    _name = 'bodo_lower_parfor_seq_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        bodo.transforms.distributed_pass.lower_parfor_sequential(state.
            typingctx, state.func_ir, state.typemap, state.calltypes, state
            .metadata)
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class LowerBodoIRExtSeq(FunctionPass):
    _name = 'bodo_lower_ir_ext_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        from bodo.transforms.distributed_pass import distributed_run_extensions
        from bodo.transforms.table_column_del_pass import remove_dead_table_columns
        from bodo.utils.transform import compile_func_single_block
        from bodo.utils.typing import decode_if_dict_array, to_str_arr_if_dict_array
        state.func_ir._definitions = build_definitions(state.func_ir.blocks)
        zeydw__kuuw = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, zeydw__kuuw)
        for block in state.func_ir.blocks.values():
            new_body = []
            for qlo__nrdm in block.body:
                if type(qlo__nrdm) in distributed_run_extensions:
                    zdf__aoov = distributed_run_extensions[type(qlo__nrdm)]
                    jbhg__cgjq = zdf__aoov(qlo__nrdm, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += jbhg__cgjq
                elif is_call_assign(qlo__nrdm):
                    rhs = qlo__nrdm.value
                    zvx__xfq = guard(find_callname, state.func_ir, rhs)
                    if zvx__xfq == ('gatherv', 'bodo') or zvx__xfq == (
                        'allgatherv', 'bodo'):
                        ndg__kbp = state.typemap[qlo__nrdm.target.name]
                        pcsve__gdt = state.typemap[rhs.args[0].name]
                        if isinstance(pcsve__gdt, types.Array) and isinstance(
                            ndg__kbp, types.Array):
                            cpvhn__gjhyr = pcsve__gdt.copy(readonly=False)
                            ink__jylp = ndg__kbp.copy(readonly=False)
                            if cpvhn__gjhyr == ink__jylp:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), qlo__nrdm.target, zeydw__kuuw)
                                continue
                        if ndg__kbp != pcsve__gdt and to_str_arr_if_dict_array(
                            ndg__kbp) == to_str_arr_if_dict_array(pcsve__gdt):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), qlo__nrdm.target,
                                zeydw__kuuw, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            qlo__nrdm.value = rhs.args[0]
                    new_body.append(qlo__nrdm)
                else:
                    new_body.append(qlo__nrdm)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        piw__pup = TableColumnDelPass(state.func_ir, state.typingctx, state
            .targetctx, state.typemap, state.calltypes)
        return piw__pup.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    zdxp__ubn = set()
    while work_list:
        rtns__ieibd, block = work_list.pop()
        zdxp__ubn.add(rtns__ieibd)
        for i, yvqnr__ypdcv in enumerate(block.body):
            if isinstance(yvqnr__ypdcv, ir.Assign):
                xsg__svctn = yvqnr__ypdcv.value
                if isinstance(xsg__svctn, ir.Expr) and xsg__svctn.op == 'call':
                    aeyt__hhjps = guard(get_definition, func_ir, xsg__svctn
                        .func)
                    if isinstance(aeyt__hhjps, (ir.Global, ir.FreeVar)
                        ) and isinstance(aeyt__hhjps.value, CPUDispatcher
                        ) and issubclass(aeyt__hhjps.value._compiler.
                        pipeline_class, BodoCompiler):
                        gbp__mlq = aeyt__hhjps.value.py_func
                        arg_types = None
                        if typingctx:
                            zmr__tbv = dict(xsg__svctn.kws)
                            budad__jwwb = tuple(typemap[ofskq__uzzl.name] for
                                ofskq__uzzl in xsg__svctn.args)
                            usxrj__fvowg = {wrpud__dukt: typemap[
                                ofskq__uzzl.name] for wrpud__dukt,
                                ofskq__uzzl in zmr__tbv.items()}
                            ttoxs__iexse, arg_types = (aeyt__hhjps.value.
                                fold_argument_types(budad__jwwb, usxrj__fvowg))
                        ttoxs__iexse, dugp__eutvs = inline_closure_call(func_ir
                            , gbp__mlq.__globals__, block, i, gbp__mlq,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((dugp__eutvs[wrpud__dukt].name,
                            ofskq__uzzl) for wrpud__dukt, ofskq__uzzl in
                            aeyt__hhjps.value.locals.items() if wrpud__dukt in
                            dugp__eutvs)
                        break
    return zdxp__ubn


def udf_jit(signature_or_function=None, **options):
    fnv__bdgwb = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=fnv__bdgwb,
        pipeline_class=bodo.compiler.BodoCompilerUDF, **options)


def is_udf_call(func_type):
    return isinstance(func_type, numba.core.types.Dispatcher
        ) and func_type.dispatcher._compiler.pipeline_class == BodoCompilerUDF


def is_user_dispatcher(func_type):
    return isinstance(func_type, numba.core.types.functions.ObjModeDispatcher
        ) or isinstance(func_type, numba.core.types.Dispatcher) and issubclass(
        func_type.dispatcher._compiler.pipeline_class, BodoCompiler)


@register_pass(mutates_CFG=False, analysis_only=True)
class DummyCR(FunctionPass):
    _name = 'bodo_dummy_cr'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        state.cr = (state.func_ir, state.typemap, state.calltypes, state.
            return_type)
        return True


def remove_passes_after(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for cjpvb__vnodn, (wefst__ebpr, ttoxs__iexse) in enumerate(pm.passes):
        if wefst__ebpr == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:cjpvb__vnodn + 1]
    pm._finalized = False


class TyperCompiler(BodoCompiler):

    def define_pipelines(self):
        [pm] = self._create_bodo_pipeline()
        remove_passes_after(pm, InlineOverloads)
        pm.add_pass_after(DummyCR, InlineOverloads)
        pm.finalize()
        return [pm]


def get_func_type_info(func, arg_types, kw_types):
    typingctx = numba.core.registry.cpu_target.typing_context
    targetctx = numba.core.registry.cpu_target.target_context
    qcw__gkws = None
    smhcm__wlfng = None
    _locals = {}
    uwn__cux = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(uwn__cux, arg_types,
        kw_types)
    jly__fddew = numba.core.compiler.Flags()
    qdfwc__hcs = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    atlk__iuvls = {'nopython': True, 'boundscheck': False, 'parallel':
        qdfwc__hcs}
    numba.core.registry.cpu_target.options.parse_as_flags(jly__fddew,
        atlk__iuvls)
    mdh__vbs = TyperCompiler(typingctx, targetctx, qcw__gkws, args,
        smhcm__wlfng, jly__fddew, _locals)
    return mdh__vbs.compile_extra(func)
