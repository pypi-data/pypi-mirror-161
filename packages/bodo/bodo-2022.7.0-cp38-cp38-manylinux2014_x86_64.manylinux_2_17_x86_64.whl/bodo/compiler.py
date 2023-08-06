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
        xxqy__sqkm = 'bodo' if distributed else 'bodo_seq'
        xxqy__sqkm = (xxqy__sqkm + '_inline' if inline_calls_pass else
            xxqy__sqkm)
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, xxqy__sqkm
            )
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
    for wzwpe__hrwh, (rrhov__noetc, oyrmp__gohp) in enumerate(pm.passes):
        if rrhov__noetc == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(wzwpe__hrwh, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for wzwpe__hrwh, (rrhov__noetc, oyrmp__gohp) in enumerate(pm.passes):
        if rrhov__noetc == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[wzwpe__hrwh] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for wzwpe__hrwh, (rrhov__noetc, oyrmp__gohp) in enumerate(pm.passes):
        if rrhov__noetc == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(wzwpe__hrwh)
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
    pnrgc__wsw = guard(get_definition, func_ir, rhs.func)
    if isinstance(pnrgc__wsw, (ir.Global, ir.FreeVar, ir.Const)):
        mlo__aomv = pnrgc__wsw.value
    else:
        flbdp__dueba = guard(find_callname, func_ir, rhs)
        if not (flbdp__dueba and isinstance(flbdp__dueba[0], str) and
            isinstance(flbdp__dueba[1], str)):
            return
        func_name, func_mod = flbdp__dueba
        try:
            import importlib
            dan__afp = importlib.import_module(func_mod)
            mlo__aomv = getattr(dan__afp, func_name)
        except:
            return
    if isinstance(mlo__aomv, CPUDispatcher) and issubclass(mlo__aomv.
        _compiler.pipeline_class, BodoCompiler
        ) and mlo__aomv._compiler.pipeline_class != BodoCompilerUDF:
        mlo__aomv._compiler.pipeline_class = BodoCompilerUDF
        mlo__aomv.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for zdp__kkeb in block.body:
                if is_call_assign(zdp__kkeb):
                    _convert_bodo_dispatcher_to_udf(zdp__kkeb.value, state.
                        func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        edu__ebfb = UntypedPass(state.func_ir, state.typingctx, state.args,
            state.locals, state.metadata, state.flags)
        edu__ebfb.run()
        return True


def _update_definitions(func_ir, node_list):
    tki__qhq = ir.Loc('', 0)
    hse__sglwy = ir.Block(ir.Scope(None, tki__qhq), tki__qhq)
    hse__sglwy.body = node_list
    build_definitions({(0): hse__sglwy}, func_ir._definitions)


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
        ntsot__uwh = 'overload_series_' + rhs.attr
        ldv__dqhh = getattr(bodo.hiframes.series_impl, ntsot__uwh)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        ntsot__uwh = 'overload_dataframe_' + rhs.attr
        ldv__dqhh = getattr(bodo.hiframes.dataframe_impl, ntsot__uwh)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    owpl__kti = ldv__dqhh(rhs_type)
    qja__ela = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    fkt__seq = compile_func_single_block(owpl__kti, (rhs.value,), stmt.
        target, qja__ela)
    _update_definitions(func_ir, fkt__seq)
    new_body += fkt__seq
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
        yhzty__ktam = tuple(typemap[pkr__owoj.name] for pkr__owoj in rhs.args)
        wub__kqh = {xxqy__sqkm: typemap[pkr__owoj.name] for xxqy__sqkm,
            pkr__owoj in dict(rhs.kws).items()}
        owpl__kti = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*yhzty__ktam, **wub__kqh)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        yhzty__ktam = tuple(typemap[pkr__owoj.name] for pkr__owoj in rhs.args)
        wub__kqh = {xxqy__sqkm: typemap[pkr__owoj.name] for xxqy__sqkm,
            pkr__owoj in dict(rhs.kws).items()}
        owpl__kti = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*yhzty__ktam, **wub__kqh)
    else:
        return False
    qjqlq__qmcl = replace_func(pass_info, owpl__kti, rhs.args, pysig=numba.
        core.utils.pysignature(owpl__kti), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    lzw__pialq, oyrmp__gohp = inline_closure_call(func_ir, qjqlq__qmcl.
        glbls, block, len(new_body), qjqlq__qmcl.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=qjqlq__qmcl.arg_types, typemap=
        typemap, calltypes=calltypes, work_list=work_list)
    for fmnw__nnrn in lzw__pialq.values():
        fmnw__nnrn.loc = rhs.loc
        update_locs(fmnw__nnrn.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    wfap__zmd = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = wfap__zmd(func_ir, typemap)
    qtkcf__czfs = func_ir.blocks
    work_list = list((fezdl__yjzh, qtkcf__czfs[fezdl__yjzh]) for
        fezdl__yjzh in reversed(qtkcf__czfs.keys()))
    while work_list:
        papvk__grjx, block = work_list.pop()
        new_body = []
        mfn__lgkfq = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                flbdp__dueba = guard(find_callname, func_ir, rhs, typemap)
                if flbdp__dueba is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = flbdp__dueba
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    mfn__lgkfq = True
                    break
            new_body.append(stmt)
        if not mfn__lgkfq:
            qtkcf__czfs[papvk__grjx].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        hyygx__czwf = DistributedPass(state.func_ir, state.typingctx, state
            .targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = hyygx__czwf.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        aywd__avdka = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        aexf__izozv = aywd__avdka.run()
        sylhy__mmjpg = aexf__izozv
        if sylhy__mmjpg:
            sylhy__mmjpg = aywd__avdka.run()
        if sylhy__mmjpg:
            aywd__avdka.run()
        return aexf__izozv


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        zvvqw__vtqvk = 0
        gwh__bsb = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            zvvqw__vtqvk = int(os.environ[gwh__bsb])
        except:
            pass
        if zvvqw__vtqvk > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(zvvqw__vtqvk,
                state.metadata)
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
        qja__ela = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, qja__ela)
        for block in state.func_ir.blocks.values():
            new_body = []
            for zdp__kkeb in block.body:
                if type(zdp__kkeb) in distributed_run_extensions:
                    ipx__klvkt = distributed_run_extensions[type(zdp__kkeb)]
                    beksm__wbwea = ipx__klvkt(zdp__kkeb, None, state.
                        typemap, state.calltypes, state.typingctx, state.
                        targetctx)
                    new_body += beksm__wbwea
                elif is_call_assign(zdp__kkeb):
                    rhs = zdp__kkeb.value
                    flbdp__dueba = guard(find_callname, state.func_ir, rhs)
                    if flbdp__dueba == ('gatherv', 'bodo') or flbdp__dueba == (
                        'allgatherv', 'bodo'):
                        svp__cwtjw = state.typemap[zdp__kkeb.target.name]
                        knm__koay = state.typemap[rhs.args[0].name]
                        if isinstance(knm__koay, types.Array) and isinstance(
                            svp__cwtjw, types.Array):
                            qhk__okxdo = knm__koay.copy(readonly=False)
                            pvfk__trf = svp__cwtjw.copy(readonly=False)
                            if qhk__okxdo == pvfk__trf:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), zdp__kkeb.target, qja__ela)
                                continue
                        if (svp__cwtjw != knm__koay and 
                            to_str_arr_if_dict_array(svp__cwtjw) ==
                            to_str_arr_if_dict_array(knm__koay)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), zdp__kkeb.target, qja__ela,
                                extra_globals={'decode_if_dict_array':
                                decode_if_dict_array})
                            continue
                        else:
                            zdp__kkeb.value = rhs.args[0]
                    new_body.append(zdp__kkeb)
                else:
                    new_body.append(zdp__kkeb)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        fvh__zyzl = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return fvh__zyzl.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    abmb__flmq = set()
    while work_list:
        papvk__grjx, block = work_list.pop()
        abmb__flmq.add(papvk__grjx)
        for i, ozako__uudhe in enumerate(block.body):
            if isinstance(ozako__uudhe, ir.Assign):
                tfkp__dcpeq = ozako__uudhe.value
                if isinstance(tfkp__dcpeq, ir.Expr
                    ) and tfkp__dcpeq.op == 'call':
                    pnrgc__wsw = guard(get_definition, func_ir, tfkp__dcpeq
                        .func)
                    if isinstance(pnrgc__wsw, (ir.Global, ir.FreeVar)
                        ) and isinstance(pnrgc__wsw.value, CPUDispatcher
                        ) and issubclass(pnrgc__wsw.value._compiler.
                        pipeline_class, BodoCompiler):
                        iralj__kmlqs = pnrgc__wsw.value.py_func
                        arg_types = None
                        if typingctx:
                            ndylo__tnu = dict(tfkp__dcpeq.kws)
                            dnfxc__knxm = tuple(typemap[pkr__owoj.name] for
                                pkr__owoj in tfkp__dcpeq.args)
                            zgh__bllln = {woemm__rma: typemap[pkr__owoj.
                                name] for woemm__rma, pkr__owoj in
                                ndylo__tnu.items()}
                            oyrmp__gohp, arg_types = (pnrgc__wsw.value.
                                fold_argument_types(dnfxc__knxm, zgh__bllln))
                        oyrmp__gohp, arc__nvgjf = inline_closure_call(func_ir,
                            iralj__kmlqs.__globals__, block, i,
                            iralj__kmlqs, typingctx=typingctx, targetctx=
                            targetctx, arg_typs=arg_types, typemap=typemap,
                            calltypes=calltypes, work_list=work_list)
                        _locals.update((arc__nvgjf[woemm__rma].name,
                            pkr__owoj) for woemm__rma, pkr__owoj in
                            pnrgc__wsw.value.locals.items() if woemm__rma in
                            arc__nvgjf)
                        break
    return abmb__flmq


def udf_jit(signature_or_function=None, **options):
    hvul__ohiyj = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=hvul__ohiyj,
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
    for wzwpe__hrwh, (rrhov__noetc, oyrmp__gohp) in enumerate(pm.passes):
        if rrhov__noetc == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:wzwpe__hrwh + 1]
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
    ybii__tzdl = None
    psjba__plejy = None
    _locals = {}
    nyj__yame = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(nyj__yame, arg_types,
        kw_types)
    uujt__zshi = numba.core.compiler.Flags()
    lfr__jupi = {'comprehension': True, 'setitem': False, 'inplace_binop': 
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    shaz__mqs = {'nopython': True, 'boundscheck': False, 'parallel': lfr__jupi}
    numba.core.registry.cpu_target.options.parse_as_flags(uujt__zshi, shaz__mqs
        )
    fbieq__rjfg = TyperCompiler(typingctx, targetctx, ybii__tzdl, args,
        psjba__plejy, uujt__zshi, _locals)
    return fbieq__rjfg.compile_extra(func)
