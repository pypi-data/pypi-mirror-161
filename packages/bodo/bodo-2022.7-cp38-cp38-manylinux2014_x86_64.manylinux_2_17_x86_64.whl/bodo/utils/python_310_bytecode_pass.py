"""
transforms the IR to handle bytecode issues in Python 3.10. This
should be removed once https://github.com/numba/numba/pull/7866
is included in Numba 0.56
"""
import operator
import numba
from numba.core import ir
from numba.core.compiler_machinery import FunctionPass, register_pass
from numba.core.errors import UnsupportedError
from numba.core.ir_utils import dprint_func_ir, get_definition, guard


@register_pass(mutates_CFG=False, analysis_only=False)
class Bodo310ByteCodePass(FunctionPass):
    _name = 'bodo_untyped_pass'

    def __init__(self):
        FunctionPass.__init__(self)

    def run_pass(self, state):
        assert state.func_ir
        dprint_func_ir(state.func_ir,
            'starting Bodo 3.10 Bytecode optimizations pass')
        peep_hole_call_function_ex_to_call_function_kw(state.func_ir)
        peep_hole_fuse_dict_add_updates(state.func_ir)
        peep_hole_fuse_tuple_adds(state.func_ir)
        return True


def peep_hole_fuse_tuple_adds(func_ir):
    for qsz__zag in func_ir.blocks.values():
        new_body = []
        rdaft__uzal = {}
        for hoxj__akvj, wzmb__swzj in enumerate(qsz__zag.body):
            druya__bhbc = None
            if isinstance(wzmb__swzj, ir.Assign) and isinstance(wzmb__swzj.
                value, ir.Expr):
                mfp__xhbqa = wzmb__swzj.target.name
                if wzmb__swzj.value.op == 'build_tuple':
                    druya__bhbc = mfp__xhbqa
                    rdaft__uzal[mfp__xhbqa] = wzmb__swzj.value.items
                elif wzmb__swzj.value.op == 'binop' and wzmb__swzj.value.fn == operator.add and wzmb__swzj.value.lhs.name in rdaft__uzal and wzmb__swzj.value.rhs.name in rdaft__uzal:
                    druya__bhbc = mfp__xhbqa
                    new_items = rdaft__uzal[wzmb__swzj.value.lhs.name
                        ] + rdaft__uzal[wzmb__swzj.value.rhs.name]
                    qdg__lccit = ir.Expr.build_tuple(new_items, wzmb__swzj.
                        value.loc)
                    rdaft__uzal[mfp__xhbqa] = new_items
                    del rdaft__uzal[wzmb__swzj.value.lhs.name]
                    del rdaft__uzal[wzmb__swzj.value.rhs.name]
                    if wzmb__swzj.value in func_ir._definitions[mfp__xhbqa]:
                        func_ir._definitions[mfp__xhbqa].remove(wzmb__swzj.
                            value)
                    func_ir._definitions[mfp__xhbqa].append(qdg__lccit)
                    wzmb__swzj = ir.Assign(qdg__lccit, wzmb__swzj.target,
                        wzmb__swzj.loc)
            for latwl__ouqd in wzmb__swzj.list_vars():
                if (latwl__ouqd.name in rdaft__uzal and latwl__ouqd.name !=
                    druya__bhbc):
                    del rdaft__uzal[latwl__ouqd.name]
            new_body.append(wzmb__swzj)
        qsz__zag.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    mzwj__cjc = keyword_expr.items.copy()
    elmx__swcon = keyword_expr.value_indexes
    for cyw__fvxj, hxlj__xpnh in elmx__swcon.items():
        mzwj__cjc[hxlj__xpnh] = cyw__fvxj, mzwj__cjc[hxlj__xpnh][1]
    new_body[buildmap_idx] = None
    return mzwj__cjc


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    exzts__zgqvm = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    mzwj__cjc = []
    fawma__crin = buildmap_idx + 1
    while fawma__crin <= search_end:
        phft__eypy = body[fawma__crin]
        if not (isinstance(phft__eypy, ir.Assign) and isinstance(phft__eypy
            .value, ir.Const)):
            raise UnsupportedError(exzts__zgqvm)
        bkge__nvtgs = phft__eypy.target.name
        zgjrt__besmj = phft__eypy.value.value
        fawma__crin += 1
        hnpqt__xlu = True
        while fawma__crin <= search_end and hnpqt__xlu:
            ymf__rhvm = body[fawma__crin]
            if (isinstance(ymf__rhvm, ir.Assign) and isinstance(ymf__rhvm.
                value, ir.Expr) and ymf__rhvm.value.op == 'getattr' and 
                ymf__rhvm.value.value.name == buildmap_name and ymf__rhvm.
                value.attr == '__setitem__'):
                hnpqt__xlu = False
            else:
                fawma__crin += 1
        if hnpqt__xlu or fawma__crin == search_end:
            raise UnsupportedError(exzts__zgqvm)
        nwd__vbsn = body[fawma__crin + 1]
        if not (isinstance(nwd__vbsn, ir.Assign) and isinstance(nwd__vbsn.
            value, ir.Expr) and nwd__vbsn.value.op == 'call' and nwd__vbsn.
            value.func.name == ymf__rhvm.target.name and len(nwd__vbsn.
            value.args) == 2 and nwd__vbsn.value.args[0].name == bkge__nvtgs):
            raise UnsupportedError(exzts__zgqvm)
        awnck__catd = nwd__vbsn.value.args[1]
        mzwj__cjc.append((zgjrt__besmj, awnck__catd))
        new_body[fawma__crin] = None
        new_body[fawma__crin + 1] = None
        fawma__crin += 2
    return mzwj__cjc


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    exzts__zgqvm = 'CALL_FUNCTION_EX with **kwargs not supported'
    fawma__crin = 0
    zjtla__cdduc = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        dex__twp = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        dex__twp = vararg_stmt.target.name
    ghzx__bgq = True
    while search_end >= fawma__crin and ghzx__bgq:
        hnys__hnq = body[search_end]
        if (isinstance(hnys__hnq, ir.Assign) and hnys__hnq.target.name ==
            dex__twp and isinstance(hnys__hnq.value, ir.Expr) and hnys__hnq
            .value.op == 'build_tuple' and not hnys__hnq.value.items):
            ghzx__bgq = False
            new_body[search_end] = None
        else:
            if search_end == fawma__crin or not (isinstance(hnys__hnq, ir.
                Assign) and hnys__hnq.target.name == dex__twp and
                isinstance(hnys__hnq.value, ir.Expr) and hnys__hnq.value.op ==
                'binop' and hnys__hnq.value.fn == operator.add):
                raise UnsupportedError(exzts__zgqvm)
            ezem__kcdv = hnys__hnq.value.lhs.name
            uxtw__omqqz = hnys__hnq.value.rhs.name
            sfu__cocum = body[search_end - 1]
            if not (isinstance(sfu__cocum, ir.Assign) and isinstance(
                sfu__cocum.value, ir.Expr) and sfu__cocum.value.op ==
                'build_tuple' and len(sfu__cocum.value.items) == 1):
                raise UnsupportedError(exzts__zgqvm)
            if sfu__cocum.target.name == ezem__kcdv:
                dex__twp = uxtw__omqqz
            elif sfu__cocum.target.name == uxtw__omqqz:
                dex__twp = ezem__kcdv
            else:
                raise UnsupportedError(exzts__zgqvm)
            zjtla__cdduc.append(sfu__cocum.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            gzl__fstyf = True
            while search_end >= fawma__crin and gzl__fstyf:
                ufg__zfru = body[search_end]
                if isinstance(ufg__zfru, ir.Assign
                    ) and ufg__zfru.target.name == dex__twp:
                    gzl__fstyf = False
                else:
                    search_end -= 1
    if ghzx__bgq:
        raise UnsupportedError(exzts__zgqvm)
    return zjtla__cdduc[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    exzts__zgqvm = 'CALL_FUNCTION_EX with **kwargs not supported'
    for qsz__zag in func_ir.blocks.values():
        iwzpo__fwi = False
        new_body = []
        for hoxj__akvj, wzmb__swzj in enumerate(qsz__zag.body):
            if (isinstance(wzmb__swzj, ir.Assign) and isinstance(wzmb__swzj
                .value, ir.Expr) and wzmb__swzj.value.op == 'call' and 
                wzmb__swzj.value.varkwarg is not None):
                iwzpo__fwi = True
                pwt__vbf = wzmb__swzj.value
                args = pwt__vbf.args
                mzwj__cjc = pwt__vbf.kws
                ksr__qvtkp = pwt__vbf.vararg
                nzrqp__lgxq = pwt__vbf.varkwarg
                syi__andsh = hoxj__akvj - 1
                cpszb__xpd = syi__andsh
                aycps__lhwqm = None
                naehr__xbij = True
                while cpszb__xpd >= 0 and naehr__xbij:
                    aycps__lhwqm = qsz__zag.body[cpszb__xpd]
                    if isinstance(aycps__lhwqm, ir.Assign
                        ) and aycps__lhwqm.target.name == nzrqp__lgxq.name:
                        naehr__xbij = False
                    else:
                        cpszb__xpd -= 1
                if mzwj__cjc or naehr__xbij or not (isinstance(aycps__lhwqm
                    .value, ir.Expr) and aycps__lhwqm.value.op == 'build_map'):
                    raise UnsupportedError(exzts__zgqvm)
                if aycps__lhwqm.value.items:
                    mzwj__cjc = _call_function_ex_replace_kws_small(
                        aycps__lhwqm.value, new_body, cpszb__xpd)
                else:
                    mzwj__cjc = _call_function_ex_replace_kws_large(qsz__zag
                        .body, nzrqp__lgxq.name, cpszb__xpd, hoxj__akvj - 1,
                        new_body)
                syi__andsh = cpszb__xpd
                if ksr__qvtkp is not None:
                    if args:
                        raise UnsupportedError(exzts__zgqvm)
                    tskj__ycur = syi__andsh
                    bon__nedhu = None
                    naehr__xbij = True
                    while tskj__ycur >= 0 and naehr__xbij:
                        bon__nedhu = qsz__zag.body[tskj__ycur]
                        if isinstance(bon__nedhu, ir.Assign
                            ) and bon__nedhu.target.name == ksr__qvtkp.name:
                            naehr__xbij = False
                        else:
                            tskj__ycur -= 1
                    if naehr__xbij:
                        raise UnsupportedError(exzts__zgqvm)
                    if isinstance(bon__nedhu.value, ir.Expr
                        ) and bon__nedhu.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(bon__nedhu
                            .value, new_body, tskj__ycur)
                    else:
                        args = _call_function_ex_replace_args_large(bon__nedhu,
                            qsz__zag.body, new_body, tskj__ycur)
                wxucu__anun = ir.Expr.call(pwt__vbf.func, args, mzwj__cjc,
                    pwt__vbf.loc, target=pwt__vbf.target)
                if wzmb__swzj.target.name in func_ir._definitions and len(
                    func_ir._definitions[wzmb__swzj.target.name]) == 1:
                    func_ir._definitions[wzmb__swzj.target.name].clear()
                func_ir._definitions[wzmb__swzj.target.name].append(wxucu__anun
                    )
                wzmb__swzj = ir.Assign(wxucu__anun, wzmb__swzj.target,
                    wzmb__swzj.loc)
            new_body.append(wzmb__swzj)
        if iwzpo__fwi:
            qsz__zag.body = [umbx__qkfo for umbx__qkfo in new_body if 
                umbx__qkfo is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for qsz__zag in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        iwzpo__fwi = False
        for hoxj__akvj, wzmb__swzj in enumerate(qsz__zag.body):
            wtrs__pxgi = True
            ookzs__dqjo = None
            if isinstance(wzmb__swzj, ir.Assign) and isinstance(wzmb__swzj.
                value, ir.Expr):
                if wzmb__swzj.value.op == 'build_map':
                    ookzs__dqjo = wzmb__swzj.target.name
                    lit_old_idx[wzmb__swzj.target.name] = hoxj__akvj
                    lit_new_idx[wzmb__swzj.target.name] = hoxj__akvj
                    map_updates[wzmb__swzj.target.name
                        ] = wzmb__swzj.value.items.copy()
                    wtrs__pxgi = False
                elif wzmb__swzj.value.op == 'call' and hoxj__akvj > 0:
                    jvo__xsei = wzmb__swzj.value.func.name
                    ymf__rhvm = qsz__zag.body[hoxj__akvj - 1]
                    args = wzmb__swzj.value.args
                    if (isinstance(ymf__rhvm, ir.Assign) and ymf__rhvm.
                        target.name == jvo__xsei and isinstance(ymf__rhvm.
                        value, ir.Expr) and ymf__rhvm.value.op == 'getattr' and
                        ymf__rhvm.value.value.name in lit_old_idx):
                        iuzs__lhds = ymf__rhvm.value.value.name
                        juwmp__ieek = ymf__rhvm.value.attr
                        if juwmp__ieek == '__setitem__':
                            wtrs__pxgi = False
                            map_updates[iuzs__lhds].append(args)
                            new_body[-1] = None
                        elif juwmp__ieek == 'update' and args[0
                            ].name in lit_old_idx:
                            wtrs__pxgi = False
                            map_updates[iuzs__lhds].extend(map_updates[args
                                [0].name])
                            new_body[-1] = None
                        if not wtrs__pxgi:
                            lit_new_idx[iuzs__lhds] = hoxj__akvj
                            func_ir._definitions[ymf__rhvm.target.name].remove(
                                ymf__rhvm.value)
            if not (isinstance(wzmb__swzj, ir.Assign) and isinstance(
                wzmb__swzj.value, ir.Expr) and wzmb__swzj.value.op ==
                'getattr' and wzmb__swzj.value.value.name in lit_old_idx and
                wzmb__swzj.value.attr in ('__setitem__', 'update')):
                for latwl__ouqd in wzmb__swzj.list_vars():
                    if (latwl__ouqd.name in lit_old_idx and latwl__ouqd.
                        name != ookzs__dqjo):
                        _insert_build_map(func_ir, latwl__ouqd.name,
                            qsz__zag.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if wtrs__pxgi:
                new_body.append(wzmb__swzj)
            else:
                func_ir._definitions[wzmb__swzj.target.name].remove(wzmb__swzj
                    .value)
                iwzpo__fwi = True
                new_body.append(None)
        pld__rnvw = list(lit_old_idx.keys())
        for xpri__jao in pld__rnvw:
            _insert_build_map(func_ir, xpri__jao, qsz__zag.body, new_body,
                lit_old_idx, lit_new_idx, map_updates)
        if iwzpo__fwi:
            qsz__zag.body = [umbx__qkfo for umbx__qkfo in new_body if 
                umbx__qkfo is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    qnuyj__nkxb = lit_old_idx[name]
    kcl__tmux = lit_new_idx[name]
    quy__hzqhv = map_updates[name]
    new_body[kcl__tmux] = _build_new_build_map(func_ir, name, old_body,
        qnuyj__nkxb, quy__hzqhv)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    tdvc__qzu = old_body[old_lineno]
    ldhav__tmknx = tdvc__qzu.target
    bopb__vqge = tdvc__qzu.value
    sli__vdh = []
    muw__zatzt = []
    for avux__dbr in new_items:
        ixra__eldrw, upfjn__tla = avux__dbr
        nbksy__olpw = guard(get_definition, func_ir, ixra__eldrw)
        if isinstance(nbksy__olpw, (ir.Const, ir.Global, ir.FreeVar)):
            sli__vdh.append(nbksy__olpw.value)
        ubdyb__wrds = guard(get_definition, func_ir, upfjn__tla)
        if isinstance(ubdyb__wrds, (ir.Const, ir.Global, ir.FreeVar)):
            muw__zatzt.append(ubdyb__wrds.value)
        else:
            muw__zatzt.append(numba.core.interpreter._UNKNOWN_VALUE(
                upfjn__tla.name))
    elmx__swcon = {}
    if len(sli__vdh) == len(new_items):
        zgdmy__jnv = {umbx__qkfo: kdek__otwht for umbx__qkfo, kdek__otwht in
            zip(sli__vdh, muw__zatzt)}
        for hoxj__akvj, ixra__eldrw in enumerate(sli__vdh):
            elmx__swcon[ixra__eldrw] = hoxj__akvj
    else:
        zgdmy__jnv = None
    gnmy__hpiu = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=zgdmy__jnv, value_indexes=elmx__swcon, loc=bopb__vqge.loc
        )
    func_ir._definitions[name].append(gnmy__hpiu)
    return ir.Assign(gnmy__hpiu, ir.Var(ldhav__tmknx.scope, name,
        ldhav__tmknx.loc), gnmy__hpiu.loc)
