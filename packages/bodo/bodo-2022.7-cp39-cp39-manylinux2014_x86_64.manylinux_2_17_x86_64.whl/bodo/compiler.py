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
        wsj__siqj = 'bodo' if distributed else 'bodo_seq'
        wsj__siqj = wsj__siqj + '_inline' if inline_calls_pass else wsj__siqj
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, wsj__siqj)
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
    for xbr__fsyt, (dzpqm__qjuz, hvvd__fzlk) in enumerate(pm.passes):
        if dzpqm__qjuz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(xbr__fsyt, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for xbr__fsyt, (dzpqm__qjuz, hvvd__fzlk) in enumerate(pm.passes):
        if dzpqm__qjuz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[xbr__fsyt] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for xbr__fsyt, (dzpqm__qjuz, hvvd__fzlk) in enumerate(pm.passes):
        if dzpqm__qjuz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(xbr__fsyt)
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
    oqlm__csi = guard(get_definition, func_ir, rhs.func)
    if isinstance(oqlm__csi, (ir.Global, ir.FreeVar, ir.Const)):
        nik__dfews = oqlm__csi.value
    else:
        jke__zsjb = guard(find_callname, func_ir, rhs)
        if not (jke__zsjb and isinstance(jke__zsjb[0], str) and isinstance(
            jke__zsjb[1], str)):
            return
        func_name, func_mod = jke__zsjb
        try:
            import importlib
            ebzl__xtln = importlib.import_module(func_mod)
            nik__dfews = getattr(ebzl__xtln, func_name)
        except:
            return
    if isinstance(nik__dfews, CPUDispatcher) and issubclass(nik__dfews.
        _compiler.pipeline_class, BodoCompiler
        ) and nik__dfews._compiler.pipeline_class != BodoCompilerUDF:
        nik__dfews._compiler.pipeline_class = BodoCompilerUDF
        nik__dfews.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for utuj__rtqek in block.body:
                if is_call_assign(utuj__rtqek):
                    _convert_bodo_dispatcher_to_udf(utuj__rtqek.value,
                        state.func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        wukai__ifolr = UntypedPass(state.func_ir, state.typingctx, state.
            args, state.locals, state.metadata, state.flags)
        wukai__ifolr.run()
        return True


def _update_definitions(func_ir, node_list):
    xai__stwrb = ir.Loc('', 0)
    duac__epo = ir.Block(ir.Scope(None, xai__stwrb), xai__stwrb)
    duac__epo.body = node_list
    build_definitions({(0): duac__epo}, func_ir._definitions)


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
        qdqmn__jqgv = 'overload_series_' + rhs.attr
        hozyb__wbiq = getattr(bodo.hiframes.series_impl, qdqmn__jqgv)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        qdqmn__jqgv = 'overload_dataframe_' + rhs.attr
        hozyb__wbiq = getattr(bodo.hiframes.dataframe_impl, qdqmn__jqgv)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    rbdr__pjw = hozyb__wbiq(rhs_type)
    dkwl__kgeaq = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc
        )
    xljao__swcwg = compile_func_single_block(rbdr__pjw, (rhs.value,), stmt.
        target, dkwl__kgeaq)
    _update_definitions(func_ir, xljao__swcwg)
    new_body += xljao__swcwg
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
        xajma__zfqx = tuple(typemap[zwmff__wbwfh.name] for zwmff__wbwfh in
            rhs.args)
        xhyli__irhz = {wsj__siqj: typemap[zwmff__wbwfh.name] for wsj__siqj,
            zwmff__wbwfh in dict(rhs.kws).items()}
        rbdr__pjw = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*xajma__zfqx, **xhyli__irhz)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        xajma__zfqx = tuple(typemap[zwmff__wbwfh.name] for zwmff__wbwfh in
            rhs.args)
        xhyli__irhz = {wsj__siqj: typemap[zwmff__wbwfh.name] for wsj__siqj,
            zwmff__wbwfh in dict(rhs.kws).items()}
        rbdr__pjw = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*xajma__zfqx, **xhyli__irhz)
    else:
        return False
    ldh__lodps = replace_func(pass_info, rbdr__pjw, rhs.args, pysig=numba.
        core.utils.pysignature(rbdr__pjw), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    wctvn__kuojo, hvvd__fzlk = inline_closure_call(func_ir, ldh__lodps.
        glbls, block, len(new_body), ldh__lodps.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=ldh__lodps.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for czg__eogx in wctvn__kuojo.values():
        czg__eogx.loc = rhs.loc
        update_locs(czg__eogx.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    ymkjm__oqti = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = ymkjm__oqti(func_ir, typemap)
    guc__ewwj = func_ir.blocks
    work_list = list((sfjav__uwp, guc__ewwj[sfjav__uwp]) for sfjav__uwp in
        reversed(guc__ewwj.keys()))
    while work_list:
        mcew__qze, block = work_list.pop()
        new_body = []
        qgukn__tpjgm = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                jke__zsjb = guard(find_callname, func_ir, rhs, typemap)
                if jke__zsjb is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = jke__zsjb
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    qgukn__tpjgm = True
                    break
            new_body.append(stmt)
        if not qgukn__tpjgm:
            guc__ewwj[mcew__qze].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        cdq__tgtrw = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = cdq__tgtrw.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        yuj__zxcxf = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        mhcon__suyuz = yuj__zxcxf.run()
        kkts__jhkph = mhcon__suyuz
        if kkts__jhkph:
            kkts__jhkph = yuj__zxcxf.run()
        if kkts__jhkph:
            yuj__zxcxf.run()
        return mhcon__suyuz


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        nwai__cajzv = 0
        kjzbd__ltgov = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            nwai__cajzv = int(os.environ[kjzbd__ltgov])
        except:
            pass
        if nwai__cajzv > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(nwai__cajzv,
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
        dkwl__kgeaq = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, dkwl__kgeaq)
        for block in state.func_ir.blocks.values():
            new_body = []
            for utuj__rtqek in block.body:
                if type(utuj__rtqek) in distributed_run_extensions:
                    mow__ivjza = distributed_run_extensions[type(utuj__rtqek)]
                    dfh__tjkin = mow__ivjza(utuj__rtqek, None, state.
                        typemap, state.calltypes, state.typingctx, state.
                        targetctx)
                    new_body += dfh__tjkin
                elif is_call_assign(utuj__rtqek):
                    rhs = utuj__rtqek.value
                    jke__zsjb = guard(find_callname, state.func_ir, rhs)
                    if jke__zsjb == ('gatherv', 'bodo') or jke__zsjb == (
                        'allgatherv', 'bodo'):
                        uuvup__lvg = state.typemap[utuj__rtqek.target.name]
                        ixega__obegm = state.typemap[rhs.args[0].name]
                        if isinstance(ixega__obegm, types.Array
                            ) and isinstance(uuvup__lvg, types.Array):
                            qzm__kex = ixega__obegm.copy(readonly=False)
                            dmxjo__jbulz = uuvup__lvg.copy(readonly=False)
                            if qzm__kex == dmxjo__jbulz:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), utuj__rtqek.target, dkwl__kgeaq)
                                continue
                        if (uuvup__lvg != ixega__obegm and 
                            to_str_arr_if_dict_array(uuvup__lvg) ==
                            to_str_arr_if_dict_array(ixega__obegm)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), utuj__rtqek.target,
                                dkwl__kgeaq, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            utuj__rtqek.value = rhs.args[0]
                    new_body.append(utuj__rtqek)
                else:
                    new_body.append(utuj__rtqek)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        bjt__ncbl = TableColumnDelPass(state.func_ir, state.typingctx,
            state.targetctx, state.typemap, state.calltypes)
        return bjt__ncbl.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    flkms__ayyzh = set()
    while work_list:
        mcew__qze, block = work_list.pop()
        flkms__ayyzh.add(mcew__qze)
        for i, opsx__jsaao in enumerate(block.body):
            if isinstance(opsx__jsaao, ir.Assign):
                cbvot__wzun = opsx__jsaao.value
                if isinstance(cbvot__wzun, ir.Expr
                    ) and cbvot__wzun.op == 'call':
                    oqlm__csi = guard(get_definition, func_ir, cbvot__wzun.func
                        )
                    if isinstance(oqlm__csi, (ir.Global, ir.FreeVar)
                        ) and isinstance(oqlm__csi.value, CPUDispatcher
                        ) and issubclass(oqlm__csi.value._compiler.
                        pipeline_class, BodoCompiler):
                        flg__hepq = oqlm__csi.value.py_func
                        arg_types = None
                        if typingctx:
                            duz__ghxah = dict(cbvot__wzun.kws)
                            sacz__hedop = tuple(typemap[zwmff__wbwfh.name] for
                                zwmff__wbwfh in cbvot__wzun.args)
                            gvon__jqopb = {mgka__dgnm: typemap[zwmff__wbwfh
                                .name] for mgka__dgnm, zwmff__wbwfh in
                                duz__ghxah.items()}
                            hvvd__fzlk, arg_types = (oqlm__csi.value.
                                fold_argument_types(sacz__hedop, gvon__jqopb))
                        hvvd__fzlk, vsjcs__dsa = inline_closure_call(func_ir,
                            flg__hepq.__globals__, block, i, flg__hepq,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((vsjcs__dsa[mgka__dgnm].name,
                            zwmff__wbwfh) for mgka__dgnm, zwmff__wbwfh in
                            oqlm__csi.value.locals.items() if mgka__dgnm in
                            vsjcs__dsa)
                        break
    return flkms__ayyzh


def udf_jit(signature_or_function=None, **options):
    qvc__ylh = {'comprehension': True, 'setitem': False, 'inplace_binop': 
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=qvc__ylh,
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
    for xbr__fsyt, (dzpqm__qjuz, hvvd__fzlk) in enumerate(pm.passes):
        if dzpqm__qjuz == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:xbr__fsyt + 1]
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
    sug__hfc = None
    ajz__via = None
    _locals = {}
    legb__qzdv = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(legb__qzdv, arg_types,
        kw_types)
    chrqv__aeow = numba.core.compiler.Flags()
    djkjd__yhr = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    stvmp__mksh = {'nopython': True, 'boundscheck': False, 'parallel':
        djkjd__yhr}
    numba.core.registry.cpu_target.options.parse_as_flags(chrqv__aeow,
        stvmp__mksh)
    rcid__spphc = TyperCompiler(typingctx, targetctx, sug__hfc, args,
        ajz__via, chrqv__aeow, _locals)
    return rcid__spphc.compile_extra(func)
