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
        wlg__udg = 'bodo' if distributed else 'bodo_seq'
        wlg__udg = wlg__udg + '_inline' if inline_calls_pass else wlg__udg
        pm = DefaultPassBuilder.define_nopython_pipeline(self.state, wlg__udg)
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
    for mqp__sjhy, (tiet__tjfh, tff__hsn) in enumerate(pm.passes):
        if tiet__tjfh == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.insert(mqp__sjhy, (pass_cls, str(pass_cls)))
    pm._finalized = False


def replace_pass(pm, pass_cls, location):
    assert pm.passes
    pm._validate_pass(pass_cls)
    pm._validate_pass(location)
    for mqp__sjhy, (tiet__tjfh, tff__hsn) in enumerate(pm.passes):
        if tiet__tjfh == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes[mqp__sjhy] = pass_cls, str(pass_cls)
    pm._finalized = False


def remove_pass(pm, location):
    assert pm.passes
    pm._validate_pass(location)
    for mqp__sjhy, (tiet__tjfh, tff__hsn) in enumerate(pm.passes):
        if tiet__tjfh == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes.pop(mqp__sjhy)
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
    fnl__pxbin = guard(get_definition, func_ir, rhs.func)
    if isinstance(fnl__pxbin, (ir.Global, ir.FreeVar, ir.Const)):
        rkgga__owshg = fnl__pxbin.value
    else:
        tos__akdvo = guard(find_callname, func_ir, rhs)
        if not (tos__akdvo and isinstance(tos__akdvo[0], str) and
            isinstance(tos__akdvo[1], str)):
            return
        func_name, func_mod = tos__akdvo
        try:
            import importlib
            tfl__lew = importlib.import_module(func_mod)
            rkgga__owshg = getattr(tfl__lew, func_name)
        except:
            return
    if isinstance(rkgga__owshg, CPUDispatcher) and issubclass(rkgga__owshg.
        _compiler.pipeline_class, BodoCompiler
        ) and rkgga__owshg._compiler.pipeline_class != BodoCompilerUDF:
        rkgga__owshg._compiler.pipeline_class = BodoCompilerUDF
        rkgga__owshg.recompile()


@register_pass(mutates_CFG=True, analysis_only=False)
class ConvertCallsUDFPass(FunctionPass):
    _name = 'inline_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        for block in state.func_ir.blocks.values():
            for ermvg__rnjb in block.body:
                if is_call_assign(ermvg__rnjb):
                    _convert_bodo_dispatcher_to_udf(ermvg__rnjb.value,
                        state.func_ir)
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoUntypedPass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        pndrl__fzvwn = UntypedPass(state.func_ir, state.typingctx, state.
            args, state.locals, state.metadata, state.flags)
        pndrl__fzvwn.run()
        return True


def _update_definitions(func_ir, node_list):
    feluj__zca = ir.Loc('', 0)
    cnd__kugha = ir.Block(ir.Scope(None, feluj__zca), feluj__zca)
    cnd__kugha.body = node_list
    build_definitions({(0): cnd__kugha}, func_ir._definitions)


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
        heme__nurw = 'overload_series_' + rhs.attr
        roys__mqh = getattr(bodo.hiframes.series_impl, heme__nurw)
    if isinstance(rhs_type, DataFrameType) and rhs.attr in ('index', 'columns'
        ):
        heme__nurw = 'overload_dataframe_' + rhs.attr
        roys__mqh = getattr(bodo.hiframes.dataframe_impl, heme__nurw)
    else:
        return False
    func_ir._definitions[stmt.target.name].remove(rhs)
    fco__djp = roys__mqh(rhs_type)
    bfqea__wek = TypingInfo(typingctx, targetctx, typemap, calltypes, stmt.loc)
    pthz__ffdzg = compile_func_single_block(fco__djp, (rhs.value,), stmt.
        target, bfqea__wek)
    _update_definitions(func_ir, pthz__ffdzg)
    new_body += pthz__ffdzg
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
        rxgfr__hqbka = tuple(typemap[zld__znwf.name] for zld__znwf in rhs.args)
        grl__mos = {wlg__udg: typemap[zld__znwf.name] for wlg__udg,
            zld__znwf in dict(rhs.kws).items()}
        fco__djp = getattr(bodo.hiframes.series_impl, 'overload_series_' +
            func_name)(*rxgfr__hqbka, **grl__mos)
    elif isinstance(func_mod, ir.Var) and isinstance(typemap[func_mod.name],
        DataFrameType) and func_name not in _dataframe_no_inline_methods:
        if func_name in _series_method_alias:
            func_name = _series_method_alias[func_name]
        rhs.args.insert(0, func_mod)
        rxgfr__hqbka = tuple(typemap[zld__znwf.name] for zld__znwf in rhs.args)
        grl__mos = {wlg__udg: typemap[zld__znwf.name] for wlg__udg,
            zld__znwf in dict(rhs.kws).items()}
        fco__djp = getattr(bodo.hiframes.dataframe_impl, 
            'overload_dataframe_' + func_name)(*rxgfr__hqbka, **grl__mos)
    else:
        return False
    gais__ykmt = replace_func(pass_info, fco__djp, rhs.args, pysig=numba.
        core.utils.pysignature(fco__djp), kws=dict(rhs.kws))
    block.body = new_body + block.body[i:]
    zstbo__owpj, tff__hsn = inline_closure_call(func_ir, gais__ykmt.glbls,
        block, len(new_body), gais__ykmt.func, typingctx=typingctx,
        targetctx=targetctx, arg_typs=gais__ykmt.arg_types, typemap=typemap,
        calltypes=calltypes, work_list=work_list)
    for slnpb__yhkc in zstbo__owpj.values():
        slnpb__yhkc.loc = rhs.loc
        update_locs(slnpb__yhkc.body, rhs.loc)
    return True


def bodo_overload_inline_pass(func_ir, typingctx, targetctx, typemap, calltypes
    ):
    ewj__zpc = namedtuple('PassInfo', ['func_ir', 'typemap'])
    pass_info = ewj__zpc(func_ir, typemap)
    jtbq__mklge = func_ir.blocks
    work_list = list((zcpw__gcj, jtbq__mklge[zcpw__gcj]) for zcpw__gcj in
        reversed(jtbq__mklge.keys()))
    while work_list:
        iwoml__daywn, block = work_list.pop()
        new_body = []
        mzfzo__fbhjj = False
        for i, stmt in enumerate(block.body):
            if is_assign(stmt) and is_expr(stmt.value, 'getattr'):
                rhs = stmt.value
                rhs_type = typemap[rhs.value.name]
                if _inline_bodo_getattr(stmt, rhs, rhs_type, new_body,
                    func_ir, typingctx, targetctx, typemap, calltypes):
                    continue
            if is_call_assign(stmt):
                rhs = stmt.value
                tos__akdvo = guard(find_callname, func_ir, rhs, typemap)
                if tos__akdvo is None:
                    new_body.append(stmt)
                    continue
                func_name, func_mod = tos__akdvo
                if _inline_bodo_call(rhs, i, func_mod, func_name, pass_info,
                    new_body, block, typingctx, targetctx, calltypes, work_list
                    ):
                    mzfzo__fbhjj = True
                    break
            new_body.append(stmt)
        if not mzfzo__fbhjj:
            jtbq__mklge[iwoml__daywn].body = new_body
    func_ir.blocks = ir_utils.simplify_CFG(func_ir.blocks)


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoDistributedPass(FunctionPass):
    _name = 'bodo_distributed_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        from bodo.transforms.distributed_pass import DistributedPass
        jxvml__bli = DistributedPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.return_type,
            state.metadata, state.flags)
        state.return_type = jxvml__bli.run()
        return True


@register_pass(mutates_CFG=True, analysis_only=False)
class BodoSeriesPass(FunctionPass):
    _name = 'bodo_series_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        ugh__ltk = SeriesPass(state.func_ir, state.typingctx, state.
            targetctx, state.typemap, state.calltypes, state.locals)
        uef__tsls = ugh__ltk.run()
        xdq__yxqe = uef__tsls
        if xdq__yxqe:
            xdq__yxqe = ugh__ltk.run()
        if xdq__yxqe:
            ugh__ltk.run()
        return uef__tsls


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoDumpDistDiagnosticsPass(AnalysisPass):
    _name = 'bodo_dump_diagnostics_pass'

    def __init__(self):
        AnalysisPass.__init__(self)

    def run_pass(self, state):
        hqm__shar = 0
        saz__eae = 'BODO_DISTRIBUTED_DIAGNOSTICS'
        try:
            hqm__shar = int(os.environ[saz__eae])
        except:
            pass
        if hqm__shar > 0 and 'distributed_diagnostics' in state.metadata:
            state.metadata['distributed_diagnostics'].dump(hqm__shar, state
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
        bfqea__wek = TypingInfo(state.typingctx, state.targetctx, state.
            typemap, state.calltypes, state.func_ir.loc)
        remove_dead_table_columns(state.func_ir, state.typemap, bfqea__wek)
        for block in state.func_ir.blocks.values():
            new_body = []
            for ermvg__rnjb in block.body:
                if type(ermvg__rnjb) in distributed_run_extensions:
                    dvtr__xwa = distributed_run_extensions[type(ermvg__rnjb)]
                    bcjv__acwb = dvtr__xwa(ermvg__rnjb, None, state.typemap,
                        state.calltypes, state.typingctx, state.targetctx)
                    new_body += bcjv__acwb
                elif is_call_assign(ermvg__rnjb):
                    rhs = ermvg__rnjb.value
                    tos__akdvo = guard(find_callname, state.func_ir, rhs)
                    if tos__akdvo == ('gatherv', 'bodo') or tos__akdvo == (
                        'allgatherv', 'bodo'):
                        kgyn__zyzf = state.typemap[ermvg__rnjb.target.name]
                        dwcyx__narr = state.typemap[rhs.args[0].name]
                        if isinstance(dwcyx__narr, types.Array) and isinstance(
                            kgyn__zyzf, types.Array):
                            ytrjb__dgqhz = dwcyx__narr.copy(readonly=False)
                            ccz__wwy = kgyn__zyzf.copy(readonly=False)
                            if ytrjb__dgqhz == ccz__wwy:
                                new_body += compile_func_single_block(eval(
                                    'lambda data: data.copy()'), (rhs.args[
                                    0],), ermvg__rnjb.target, bfqea__wek)
                                continue
                        if (kgyn__zyzf != dwcyx__narr and 
                            to_str_arr_if_dict_array(kgyn__zyzf) ==
                            to_str_arr_if_dict_array(dwcyx__narr)):
                            new_body += compile_func_single_block(eval(
                                'lambda data: decode_if_dict_array(data)'),
                                (rhs.args[0],), ermvg__rnjb.target,
                                bfqea__wek, extra_globals={
                                'decode_if_dict_array': decode_if_dict_array})
                            continue
                        else:
                            ermvg__rnjb.value = rhs.args[0]
                    new_body.append(ermvg__rnjb)
                else:
                    new_body.append(ermvg__rnjb)
            block.body = new_body
        return True


@register_pass(mutates_CFG=False, analysis_only=True)
class BodoTableColumnDelPass(AnalysisPass):
    _name = 'bodo_table_column_del_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        aij__qdj = TableColumnDelPass(state.func_ir, state.typingctx, state
            .targetctx, state.typemap, state.calltypes)
        return aij__qdj.run()


def inline_calls(func_ir, _locals, work_list=None, typingctx=None,
    targetctx=None, typemap=None, calltypes=None):
    if work_list is None:
        work_list = list(func_ir.blocks.items())
    gszln__jpiwx = set()
    while work_list:
        iwoml__daywn, block = work_list.pop()
        gszln__jpiwx.add(iwoml__daywn)
        for i, hobiw__pzm in enumerate(block.body):
            if isinstance(hobiw__pzm, ir.Assign):
                rds__xzkvx = hobiw__pzm.value
                if isinstance(rds__xzkvx, ir.Expr) and rds__xzkvx.op == 'call':
                    fnl__pxbin = guard(get_definition, func_ir, rds__xzkvx.func
                        )
                    if isinstance(fnl__pxbin, (ir.Global, ir.FreeVar)
                        ) and isinstance(fnl__pxbin.value, CPUDispatcher
                        ) and issubclass(fnl__pxbin.value._compiler.
                        pipeline_class, BodoCompiler):
                        hxq__scdrw = fnl__pxbin.value.py_func
                        arg_types = None
                        if typingctx:
                            vpk__hyno = dict(rds__xzkvx.kws)
                            emuok__evmy = tuple(typemap[zld__znwf.name] for
                                zld__znwf in rds__xzkvx.args)
                            mfx__xlp = {sora__hxk: typemap[zld__znwf.name] for
                                sora__hxk, zld__znwf in vpk__hyno.items()}
                            tff__hsn, arg_types = (fnl__pxbin.value.
                                fold_argument_types(emuok__evmy, mfx__xlp))
                        tff__hsn, suueu__cdo = inline_closure_call(func_ir,
                            hxq__scdrw.__globals__, block, i, hxq__scdrw,
                            typingctx=typingctx, targetctx=targetctx,
                            arg_typs=arg_types, typemap=typemap, calltypes=
                            calltypes, work_list=work_list)
                        _locals.update((suueu__cdo[sora__hxk].name,
                            zld__znwf) for sora__hxk, zld__znwf in
                            fnl__pxbin.value.locals.items() if sora__hxk in
                            suueu__cdo)
                        break
    return gszln__jpiwx


def udf_jit(signature_or_function=None, **options):
    buo__dioqf = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    return numba.njit(signature_or_function, parallel=buo__dioqf,
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
    for mqp__sjhy, (tiet__tjfh, tff__hsn) in enumerate(pm.passes):
        if tiet__tjfh == location:
            break
    else:
        raise bodo.utils.typing.BodoError('Could not find pass %s' % location)
    pm.passes = pm.passes[:mqp__sjhy + 1]
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
    aly__vyziy = None
    gcp__mrs = None
    _locals = {}
    ekz__eqbkg = numba.core.utils.pysignature(func)
    args = bodo.utils.transform.fold_argument_types(ekz__eqbkg, arg_types,
        kw_types)
    nird__aofc = numba.core.compiler.Flags()
    kwrwm__ylge = {'comprehension': True, 'setitem': False, 'inplace_binop':
        False, 'reduction': True, 'numpy': True, 'stencil': False, 'fusion':
        True}
    uef__fbwv = {'nopython': True, 'boundscheck': False, 'parallel':
        kwrwm__ylge}
    numba.core.registry.cpu_target.options.parse_as_flags(nird__aofc, uef__fbwv
        )
    huybo__cmxdg = TyperCompiler(typingctx, targetctx, aly__vyziy, args,
        gcp__mrs, nird__aofc, _locals)
    return huybo__cmxdg.compile_extra(func)
