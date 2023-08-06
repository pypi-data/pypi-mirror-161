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
    for vyc__xmfhf in func_ir.blocks.values():
        new_body = []
        rua__ltoh = {}
        for uhk__ksdmb, tsm__qdwtw in enumerate(vyc__xmfhf.body):
            qgczq__clrqo = None
            if isinstance(tsm__qdwtw, ir.Assign) and isinstance(tsm__qdwtw.
                value, ir.Expr):
                dhla__lyu = tsm__qdwtw.target.name
                if tsm__qdwtw.value.op == 'build_tuple':
                    qgczq__clrqo = dhla__lyu
                    rua__ltoh[dhla__lyu] = tsm__qdwtw.value.items
                elif tsm__qdwtw.value.op == 'binop' and tsm__qdwtw.value.fn == operator.add and tsm__qdwtw.value.lhs.name in rua__ltoh and tsm__qdwtw.value.rhs.name in rua__ltoh:
                    qgczq__clrqo = dhla__lyu
                    new_items = rua__ltoh[tsm__qdwtw.value.lhs.name
                        ] + rua__ltoh[tsm__qdwtw.value.rhs.name]
                    vjlg__nksob = ir.Expr.build_tuple(new_items, tsm__qdwtw
                        .value.loc)
                    rua__ltoh[dhla__lyu] = new_items
                    del rua__ltoh[tsm__qdwtw.value.lhs.name]
                    del rua__ltoh[tsm__qdwtw.value.rhs.name]
                    if tsm__qdwtw.value in func_ir._definitions[dhla__lyu]:
                        func_ir._definitions[dhla__lyu].remove(tsm__qdwtw.value
                            )
                    func_ir._definitions[dhla__lyu].append(vjlg__nksob)
                    tsm__qdwtw = ir.Assign(vjlg__nksob, tsm__qdwtw.target,
                        tsm__qdwtw.loc)
            for fek__fztzm in tsm__qdwtw.list_vars():
                if (fek__fztzm.name in rua__ltoh and fek__fztzm.name !=
                    qgczq__clrqo):
                    del rua__ltoh[fek__fztzm.name]
            new_body.append(tsm__qdwtw)
        vyc__xmfhf.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    evrk__ctwp = keyword_expr.items.copy()
    wennq__mvvz = keyword_expr.value_indexes
    for qhgg__tqt, uof__grj in wennq__mvvz.items():
        evrk__ctwp[uof__grj] = qhgg__tqt, evrk__ctwp[uof__grj][1]
    new_body[buildmap_idx] = None
    return evrk__ctwp


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    ztfi__nywqt = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    evrk__ctwp = []
    qmmii__qfn = buildmap_idx + 1
    while qmmii__qfn <= search_end:
        xrsv__pidbl = body[qmmii__qfn]
        if not (isinstance(xrsv__pidbl, ir.Assign) and isinstance(
            xrsv__pidbl.value, ir.Const)):
            raise UnsupportedError(ztfi__nywqt)
        hvb__hcmad = xrsv__pidbl.target.name
        zsfd__nlz = xrsv__pidbl.value.value
        qmmii__qfn += 1
        xqud__keeox = True
        while qmmii__qfn <= search_end and xqud__keeox:
            dxw__wanzq = body[qmmii__qfn]
            if (isinstance(dxw__wanzq, ir.Assign) and isinstance(dxw__wanzq
                .value, ir.Expr) and dxw__wanzq.value.op == 'getattr' and 
                dxw__wanzq.value.value.name == buildmap_name and dxw__wanzq
                .value.attr == '__setitem__'):
                xqud__keeox = False
            else:
                qmmii__qfn += 1
        if xqud__keeox or qmmii__qfn == search_end:
            raise UnsupportedError(ztfi__nywqt)
        yhxb__uttsy = body[qmmii__qfn + 1]
        if not (isinstance(yhxb__uttsy, ir.Assign) and isinstance(
            yhxb__uttsy.value, ir.Expr) and yhxb__uttsy.value.op == 'call' and
            yhxb__uttsy.value.func.name == dxw__wanzq.target.name and len(
            yhxb__uttsy.value.args) == 2 and yhxb__uttsy.value.args[0].name ==
            hvb__hcmad):
            raise UnsupportedError(ztfi__nywqt)
        hbq__dos = yhxb__uttsy.value.args[1]
        evrk__ctwp.append((zsfd__nlz, hbq__dos))
        new_body[qmmii__qfn] = None
        new_body[qmmii__qfn + 1] = None
        qmmii__qfn += 2
    return evrk__ctwp


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    ztfi__nywqt = 'CALL_FUNCTION_EX with **kwargs not supported'
    qmmii__qfn = 0
    nycs__kqli = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        ntbi__opix = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        ntbi__opix = vararg_stmt.target.name
    fsdf__ynuz = True
    while search_end >= qmmii__qfn and fsdf__ynuz:
        wswmu__ngmi = body[search_end]
        if (isinstance(wswmu__ngmi, ir.Assign) and wswmu__ngmi.target.name ==
            ntbi__opix and isinstance(wswmu__ngmi.value, ir.Expr) and 
            wswmu__ngmi.value.op == 'build_tuple' and not wswmu__ngmi.value
            .items):
            fsdf__ynuz = False
            new_body[search_end] = None
        else:
            if search_end == qmmii__qfn or not (isinstance(wswmu__ngmi, ir.
                Assign) and wswmu__ngmi.target.name == ntbi__opix and
                isinstance(wswmu__ngmi.value, ir.Expr) and wswmu__ngmi.
                value.op == 'binop' and wswmu__ngmi.value.fn == operator.add):
                raise UnsupportedError(ztfi__nywqt)
            fsvw__ikueg = wswmu__ngmi.value.lhs.name
            hoaw__xjt = wswmu__ngmi.value.rhs.name
            rpb__vipr = body[search_end - 1]
            if not (isinstance(rpb__vipr, ir.Assign) and isinstance(
                rpb__vipr.value, ir.Expr) and rpb__vipr.value.op ==
                'build_tuple' and len(rpb__vipr.value.items) == 1):
                raise UnsupportedError(ztfi__nywqt)
            if rpb__vipr.target.name == fsvw__ikueg:
                ntbi__opix = hoaw__xjt
            elif rpb__vipr.target.name == hoaw__xjt:
                ntbi__opix = fsvw__ikueg
            else:
                raise UnsupportedError(ztfi__nywqt)
            nycs__kqli.append(rpb__vipr.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            xdtro__pdte = True
            while search_end >= qmmii__qfn and xdtro__pdte:
                ysytn__fzw = body[search_end]
                if isinstance(ysytn__fzw, ir.Assign
                    ) and ysytn__fzw.target.name == ntbi__opix:
                    xdtro__pdte = False
                else:
                    search_end -= 1
    if fsdf__ynuz:
        raise UnsupportedError(ztfi__nywqt)
    return nycs__kqli[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    ztfi__nywqt = 'CALL_FUNCTION_EX with **kwargs not supported'
    for vyc__xmfhf in func_ir.blocks.values():
        umlq__jnu = False
        new_body = []
        for uhk__ksdmb, tsm__qdwtw in enumerate(vyc__xmfhf.body):
            if (isinstance(tsm__qdwtw, ir.Assign) and isinstance(tsm__qdwtw
                .value, ir.Expr) and tsm__qdwtw.value.op == 'call' and 
                tsm__qdwtw.value.varkwarg is not None):
                umlq__jnu = True
                dtz__zfdx = tsm__qdwtw.value
                args = dtz__zfdx.args
                evrk__ctwp = dtz__zfdx.kws
                uzrez__vhfp = dtz__zfdx.vararg
                sudal__lyml = dtz__zfdx.varkwarg
                gmvol__rrexh = uhk__ksdmb - 1
                niydx__dasxn = gmvol__rrexh
                txeo__umqxv = None
                xmt__kjah = True
                while niydx__dasxn >= 0 and xmt__kjah:
                    txeo__umqxv = vyc__xmfhf.body[niydx__dasxn]
                    if isinstance(txeo__umqxv, ir.Assign
                        ) and txeo__umqxv.target.name == sudal__lyml.name:
                        xmt__kjah = False
                    else:
                        niydx__dasxn -= 1
                if evrk__ctwp or xmt__kjah or not (isinstance(txeo__umqxv.
                    value, ir.Expr) and txeo__umqxv.value.op == 'build_map'):
                    raise UnsupportedError(ztfi__nywqt)
                if txeo__umqxv.value.items:
                    evrk__ctwp = _call_function_ex_replace_kws_small(
                        txeo__umqxv.value, new_body, niydx__dasxn)
                else:
                    evrk__ctwp = _call_function_ex_replace_kws_large(vyc__xmfhf
                        .body, sudal__lyml.name, niydx__dasxn, uhk__ksdmb -
                        1, new_body)
                gmvol__rrexh = niydx__dasxn
                if uzrez__vhfp is not None:
                    if args:
                        raise UnsupportedError(ztfi__nywqt)
                    iat__beoja = gmvol__rrexh
                    arlk__gpr = None
                    xmt__kjah = True
                    while iat__beoja >= 0 and xmt__kjah:
                        arlk__gpr = vyc__xmfhf.body[iat__beoja]
                        if isinstance(arlk__gpr, ir.Assign
                            ) and arlk__gpr.target.name == uzrez__vhfp.name:
                            xmt__kjah = False
                        else:
                            iat__beoja -= 1
                    if xmt__kjah:
                        raise UnsupportedError(ztfi__nywqt)
                    if isinstance(arlk__gpr.value, ir.Expr
                        ) and arlk__gpr.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(arlk__gpr
                            .value, new_body, iat__beoja)
                    else:
                        args = _call_function_ex_replace_args_large(arlk__gpr,
                            vyc__xmfhf.body, new_body, iat__beoja)
                niwxi__nwmc = ir.Expr.call(dtz__zfdx.func, args, evrk__ctwp,
                    dtz__zfdx.loc, target=dtz__zfdx.target)
                if tsm__qdwtw.target.name in func_ir._definitions and len(
                    func_ir._definitions[tsm__qdwtw.target.name]) == 1:
                    func_ir._definitions[tsm__qdwtw.target.name].clear()
                func_ir._definitions[tsm__qdwtw.target.name].append(niwxi__nwmc
                    )
                tsm__qdwtw = ir.Assign(niwxi__nwmc, tsm__qdwtw.target,
                    tsm__qdwtw.loc)
            new_body.append(tsm__qdwtw)
        if umlq__jnu:
            vyc__xmfhf.body = [wayv__ovjbq for wayv__ovjbq in new_body if 
                wayv__ovjbq is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for vyc__xmfhf in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        umlq__jnu = False
        for uhk__ksdmb, tsm__qdwtw in enumerate(vyc__xmfhf.body):
            frktk__rahcl = True
            uhiz__zkzi = None
            if isinstance(tsm__qdwtw, ir.Assign) and isinstance(tsm__qdwtw.
                value, ir.Expr):
                if tsm__qdwtw.value.op == 'build_map':
                    uhiz__zkzi = tsm__qdwtw.target.name
                    lit_old_idx[tsm__qdwtw.target.name] = uhk__ksdmb
                    lit_new_idx[tsm__qdwtw.target.name] = uhk__ksdmb
                    map_updates[tsm__qdwtw.target.name
                        ] = tsm__qdwtw.value.items.copy()
                    frktk__rahcl = False
                elif tsm__qdwtw.value.op == 'call' and uhk__ksdmb > 0:
                    clagj__omeze = tsm__qdwtw.value.func.name
                    dxw__wanzq = vyc__xmfhf.body[uhk__ksdmb - 1]
                    args = tsm__qdwtw.value.args
                    if (isinstance(dxw__wanzq, ir.Assign) and dxw__wanzq.
                        target.name == clagj__omeze and isinstance(
                        dxw__wanzq.value, ir.Expr) and dxw__wanzq.value.op ==
                        'getattr' and dxw__wanzq.value.value.name in
                        lit_old_idx):
                        jabtk__svy = dxw__wanzq.value.value.name
                        tbej__vtcqh = dxw__wanzq.value.attr
                        if tbej__vtcqh == '__setitem__':
                            frktk__rahcl = False
                            map_updates[jabtk__svy].append(args)
                            new_body[-1] = None
                        elif tbej__vtcqh == 'update' and args[0
                            ].name in lit_old_idx:
                            frktk__rahcl = False
                            map_updates[jabtk__svy].extend(map_updates[args
                                [0].name])
                            new_body[-1] = None
                        if not frktk__rahcl:
                            lit_new_idx[jabtk__svy] = uhk__ksdmb
                            func_ir._definitions[dxw__wanzq.target.name
                                ].remove(dxw__wanzq.value)
            if not (isinstance(tsm__qdwtw, ir.Assign) and isinstance(
                tsm__qdwtw.value, ir.Expr) and tsm__qdwtw.value.op ==
                'getattr' and tsm__qdwtw.value.value.name in lit_old_idx and
                tsm__qdwtw.value.attr in ('__setitem__', 'update')):
                for fek__fztzm in tsm__qdwtw.list_vars():
                    if (fek__fztzm.name in lit_old_idx and fek__fztzm.name !=
                        uhiz__zkzi):
                        _insert_build_map(func_ir, fek__fztzm.name,
                            vyc__xmfhf.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if frktk__rahcl:
                new_body.append(tsm__qdwtw)
            else:
                func_ir._definitions[tsm__qdwtw.target.name].remove(tsm__qdwtw
                    .value)
                umlq__jnu = True
                new_body.append(None)
        egp__vozms = list(lit_old_idx.keys())
        for cuykl__kxr in egp__vozms:
            _insert_build_map(func_ir, cuykl__kxr, vyc__xmfhf.body,
                new_body, lit_old_idx, lit_new_idx, map_updates)
        if umlq__jnu:
            vyc__xmfhf.body = [wayv__ovjbq for wayv__ovjbq in new_body if 
                wayv__ovjbq is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    zlmhr__oyjzf = lit_old_idx[name]
    qso__zmjke = lit_new_idx[name]
    hzie__xclyi = map_updates[name]
    new_body[qso__zmjke] = _build_new_build_map(func_ir, name, old_body,
        zlmhr__oyjzf, hzie__xclyi)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    iqyyq__xaj = old_body[old_lineno]
    dis__wzzd = iqyyq__xaj.target
    wwqrb__ctiti = iqyyq__xaj.value
    pffpi__qdtva = []
    mhbkp__egl = []
    for fks__irfvd in new_items:
        rjc__oozdp, wqgp__stz = fks__irfvd
        swcl__rwz = guard(get_definition, func_ir, rjc__oozdp)
        if isinstance(swcl__rwz, (ir.Const, ir.Global, ir.FreeVar)):
            pffpi__qdtva.append(swcl__rwz.value)
        eyp__pefk = guard(get_definition, func_ir, wqgp__stz)
        if isinstance(eyp__pefk, (ir.Const, ir.Global, ir.FreeVar)):
            mhbkp__egl.append(eyp__pefk.value)
        else:
            mhbkp__egl.append(numba.core.interpreter._UNKNOWN_VALUE(
                wqgp__stz.name))
    wennq__mvvz = {}
    if len(pffpi__qdtva) == len(new_items):
        egfs__juv = {wayv__ovjbq: cbd__kgvlx for wayv__ovjbq, cbd__kgvlx in
            zip(pffpi__qdtva, mhbkp__egl)}
        for uhk__ksdmb, rjc__oozdp in enumerate(pffpi__qdtva):
            wennq__mvvz[rjc__oozdp] = uhk__ksdmb
    else:
        egfs__juv = None
    qlqa__hkur = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=egfs__juv, value_indexes=wennq__mvvz, loc=
        wwqrb__ctiti.loc)
    func_ir._definitions[name].append(qlqa__hkur)
    return ir.Assign(qlqa__hkur, ir.Var(dis__wzzd.scope, name, dis__wzzd.
        loc), qlqa__hkur.loc)
