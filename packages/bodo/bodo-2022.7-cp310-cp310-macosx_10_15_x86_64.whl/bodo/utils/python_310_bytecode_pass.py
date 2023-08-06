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
    for znr__lelgu in func_ir.blocks.values():
        new_body = []
        jpjc__klnnc = {}
        for vkn__lbgnp, vtuk__vil in enumerate(znr__lelgu.body):
            uxsk__gdbsq = None
            if isinstance(vtuk__vil, ir.Assign) and isinstance(vtuk__vil.
                value, ir.Expr):
                zti__ltbq = vtuk__vil.target.name
                if vtuk__vil.value.op == 'build_tuple':
                    uxsk__gdbsq = zti__ltbq
                    jpjc__klnnc[zti__ltbq] = vtuk__vil.value.items
                elif vtuk__vil.value.op == 'binop' and vtuk__vil.value.fn == operator.add and vtuk__vil.value.lhs.name in jpjc__klnnc and vtuk__vil.value.rhs.name in jpjc__klnnc:
                    uxsk__gdbsq = zti__ltbq
                    new_items = jpjc__klnnc[vtuk__vil.value.lhs.name
                        ] + jpjc__klnnc[vtuk__vil.value.rhs.name]
                    zcz__myx = ir.Expr.build_tuple(new_items, vtuk__vil.
                        value.loc)
                    jpjc__klnnc[zti__ltbq] = new_items
                    del jpjc__klnnc[vtuk__vil.value.lhs.name]
                    del jpjc__klnnc[vtuk__vil.value.rhs.name]
                    if vtuk__vil.value in func_ir._definitions[zti__ltbq]:
                        func_ir._definitions[zti__ltbq].remove(vtuk__vil.value)
                    func_ir._definitions[zti__ltbq].append(zcz__myx)
                    vtuk__vil = ir.Assign(zcz__myx, vtuk__vil.target,
                        vtuk__vil.loc)
            for ngpq__xffsv in vtuk__vil.list_vars():
                if (ngpq__xffsv.name in jpjc__klnnc and ngpq__xffsv.name !=
                    uxsk__gdbsq):
                    del jpjc__klnnc[ngpq__xffsv.name]
            new_body.append(vtuk__vil)
        znr__lelgu.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    ngps__cslt = keyword_expr.items.copy()
    wdl__cbpxx = keyword_expr.value_indexes
    for vtmw__xonyh, boy__chy in wdl__cbpxx.items():
        ngps__cslt[boy__chy] = vtmw__xonyh, ngps__cslt[boy__chy][1]
    new_body[buildmap_idx] = None
    return ngps__cslt


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    rnjkd__tlwj = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    ngps__cslt = []
    tirde__ywq = buildmap_idx + 1
    while tirde__ywq <= search_end:
        jxr__uhk = body[tirde__ywq]
        if not (isinstance(jxr__uhk, ir.Assign) and isinstance(jxr__uhk.
            value, ir.Const)):
            raise UnsupportedError(rnjkd__tlwj)
        mes__mnyc = jxr__uhk.target.name
        jzzgf__mfkmv = jxr__uhk.value.value
        tirde__ywq += 1
        ohql__tvwl = True
        while tirde__ywq <= search_end and ohql__tvwl:
            feyxn__iqjos = body[tirde__ywq]
            if (isinstance(feyxn__iqjos, ir.Assign) and isinstance(
                feyxn__iqjos.value, ir.Expr) and feyxn__iqjos.value.op ==
                'getattr' and feyxn__iqjos.value.value.name ==
                buildmap_name and feyxn__iqjos.value.attr == '__setitem__'):
                ohql__tvwl = False
            else:
                tirde__ywq += 1
        if ohql__tvwl or tirde__ywq == search_end:
            raise UnsupportedError(rnjkd__tlwj)
        jui__oqndw = body[tirde__ywq + 1]
        if not (isinstance(jui__oqndw, ir.Assign) and isinstance(jui__oqndw
            .value, ir.Expr) and jui__oqndw.value.op == 'call' and 
            jui__oqndw.value.func.name == feyxn__iqjos.target.name and len(
            jui__oqndw.value.args) == 2 and jui__oqndw.value.args[0].name ==
            mes__mnyc):
            raise UnsupportedError(rnjkd__tlwj)
        nxej__vdl = jui__oqndw.value.args[1]
        ngps__cslt.append((jzzgf__mfkmv, nxej__vdl))
        new_body[tirde__ywq] = None
        new_body[tirde__ywq + 1] = None
        tirde__ywq += 2
    return ngps__cslt


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    rnjkd__tlwj = 'CALL_FUNCTION_EX with **kwargs not supported'
    tirde__ywq = 0
    ydm__wzygr = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        upp__vhtrb = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        upp__vhtrb = vararg_stmt.target.name
    suf__dilsg = True
    while search_end >= tirde__ywq and suf__dilsg:
        ibj__amfae = body[search_end]
        if (isinstance(ibj__amfae, ir.Assign) and ibj__amfae.target.name ==
            upp__vhtrb and isinstance(ibj__amfae.value, ir.Expr) and 
            ibj__amfae.value.op == 'build_tuple' and not ibj__amfae.value.items
            ):
            suf__dilsg = False
            new_body[search_end] = None
        else:
            if search_end == tirde__ywq or not (isinstance(ibj__amfae, ir.
                Assign) and ibj__amfae.target.name == upp__vhtrb and
                isinstance(ibj__amfae.value, ir.Expr) and ibj__amfae.value.
                op == 'binop' and ibj__amfae.value.fn == operator.add):
                raise UnsupportedError(rnjkd__tlwj)
            bwse__gbh = ibj__amfae.value.lhs.name
            dkje__zzg = ibj__amfae.value.rhs.name
            ucy__ejxzm = body[search_end - 1]
            if not (isinstance(ucy__ejxzm, ir.Assign) and isinstance(
                ucy__ejxzm.value, ir.Expr) and ucy__ejxzm.value.op ==
                'build_tuple' and len(ucy__ejxzm.value.items) == 1):
                raise UnsupportedError(rnjkd__tlwj)
            if ucy__ejxzm.target.name == bwse__gbh:
                upp__vhtrb = dkje__zzg
            elif ucy__ejxzm.target.name == dkje__zzg:
                upp__vhtrb = bwse__gbh
            else:
                raise UnsupportedError(rnjkd__tlwj)
            ydm__wzygr.append(ucy__ejxzm.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            yyzr__qrsoi = True
            while search_end >= tirde__ywq and yyzr__qrsoi:
                gzb__gmk = body[search_end]
                if isinstance(gzb__gmk, ir.Assign
                    ) and gzb__gmk.target.name == upp__vhtrb:
                    yyzr__qrsoi = False
                else:
                    search_end -= 1
    if suf__dilsg:
        raise UnsupportedError(rnjkd__tlwj)
    return ydm__wzygr[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    rnjkd__tlwj = 'CALL_FUNCTION_EX with **kwargs not supported'
    for znr__lelgu in func_ir.blocks.values():
        lsm__cmc = False
        new_body = []
        for vkn__lbgnp, vtuk__vil in enumerate(znr__lelgu.body):
            if (isinstance(vtuk__vil, ir.Assign) and isinstance(vtuk__vil.
                value, ir.Expr) and vtuk__vil.value.op == 'call' and 
                vtuk__vil.value.varkwarg is not None):
                lsm__cmc = True
                lpzd__qkeqx = vtuk__vil.value
                args = lpzd__qkeqx.args
                ngps__cslt = lpzd__qkeqx.kws
                rxk__pitwj = lpzd__qkeqx.vararg
                nql__sdpkg = lpzd__qkeqx.varkwarg
                xhqvl__mfv = vkn__lbgnp - 1
                uzjzo__sxje = xhqvl__mfv
                wylm__gjmvs = None
                aqzcw__vtvs = True
                while uzjzo__sxje >= 0 and aqzcw__vtvs:
                    wylm__gjmvs = znr__lelgu.body[uzjzo__sxje]
                    if isinstance(wylm__gjmvs, ir.Assign
                        ) and wylm__gjmvs.target.name == nql__sdpkg.name:
                        aqzcw__vtvs = False
                    else:
                        uzjzo__sxje -= 1
                if ngps__cslt or aqzcw__vtvs or not (isinstance(wylm__gjmvs
                    .value, ir.Expr) and wylm__gjmvs.value.op == 'build_map'):
                    raise UnsupportedError(rnjkd__tlwj)
                if wylm__gjmvs.value.items:
                    ngps__cslt = _call_function_ex_replace_kws_small(
                        wylm__gjmvs.value, new_body, uzjzo__sxje)
                else:
                    ngps__cslt = _call_function_ex_replace_kws_large(znr__lelgu
                        .body, nql__sdpkg.name, uzjzo__sxje, vkn__lbgnp - 1,
                        new_body)
                xhqvl__mfv = uzjzo__sxje
                if rxk__pitwj is not None:
                    if args:
                        raise UnsupportedError(rnjkd__tlwj)
                    oox__pizq = xhqvl__mfv
                    ltyt__leq = None
                    aqzcw__vtvs = True
                    while oox__pizq >= 0 and aqzcw__vtvs:
                        ltyt__leq = znr__lelgu.body[oox__pizq]
                        if isinstance(ltyt__leq, ir.Assign
                            ) and ltyt__leq.target.name == rxk__pitwj.name:
                            aqzcw__vtvs = False
                        else:
                            oox__pizq -= 1
                    if aqzcw__vtvs:
                        raise UnsupportedError(rnjkd__tlwj)
                    if isinstance(ltyt__leq.value, ir.Expr
                        ) and ltyt__leq.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(ltyt__leq
                            .value, new_body, oox__pizq)
                    else:
                        args = _call_function_ex_replace_args_large(ltyt__leq,
                            znr__lelgu.body, new_body, oox__pizq)
                dcpr__rgfz = ir.Expr.call(lpzd__qkeqx.func, args,
                    ngps__cslt, lpzd__qkeqx.loc, target=lpzd__qkeqx.target)
                if vtuk__vil.target.name in func_ir._definitions and len(
                    func_ir._definitions[vtuk__vil.target.name]) == 1:
                    func_ir._definitions[vtuk__vil.target.name].clear()
                func_ir._definitions[vtuk__vil.target.name].append(dcpr__rgfz)
                vtuk__vil = ir.Assign(dcpr__rgfz, vtuk__vil.target,
                    vtuk__vil.loc)
            new_body.append(vtuk__vil)
        if lsm__cmc:
            znr__lelgu.body = [ntm__xtsp for ntm__xtsp in new_body if 
                ntm__xtsp is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for znr__lelgu in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        lsm__cmc = False
        for vkn__lbgnp, vtuk__vil in enumerate(znr__lelgu.body):
            xcq__osj = True
            tbfif__diil = None
            if isinstance(vtuk__vil, ir.Assign) and isinstance(vtuk__vil.
                value, ir.Expr):
                if vtuk__vil.value.op == 'build_map':
                    tbfif__diil = vtuk__vil.target.name
                    lit_old_idx[vtuk__vil.target.name] = vkn__lbgnp
                    lit_new_idx[vtuk__vil.target.name] = vkn__lbgnp
                    map_updates[vtuk__vil.target.name
                        ] = vtuk__vil.value.items.copy()
                    xcq__osj = False
                elif vtuk__vil.value.op == 'call' and vkn__lbgnp > 0:
                    wsyl__gml = vtuk__vil.value.func.name
                    feyxn__iqjos = znr__lelgu.body[vkn__lbgnp - 1]
                    args = vtuk__vil.value.args
                    if (isinstance(feyxn__iqjos, ir.Assign) and 
                        feyxn__iqjos.target.name == wsyl__gml and
                        isinstance(feyxn__iqjos.value, ir.Expr) and 
                        feyxn__iqjos.value.op == 'getattr' and feyxn__iqjos
                        .value.value.name in lit_old_idx):
                        orpnl__xvuid = feyxn__iqjos.value.value.name
                        qqa__ghah = feyxn__iqjos.value.attr
                        if qqa__ghah == '__setitem__':
                            xcq__osj = False
                            map_updates[orpnl__xvuid].append(args)
                            new_body[-1] = None
                        elif qqa__ghah == 'update' and args[0
                            ].name in lit_old_idx:
                            xcq__osj = False
                            map_updates[orpnl__xvuid].extend(map_updates[
                                args[0].name])
                            new_body[-1] = None
                        if not xcq__osj:
                            lit_new_idx[orpnl__xvuid] = vkn__lbgnp
                            func_ir._definitions[feyxn__iqjos.target.name
                                ].remove(feyxn__iqjos.value)
            if not (isinstance(vtuk__vil, ir.Assign) and isinstance(
                vtuk__vil.value, ir.Expr) and vtuk__vil.value.op ==
                'getattr' and vtuk__vil.value.value.name in lit_old_idx and
                vtuk__vil.value.attr in ('__setitem__', 'update')):
                for ngpq__xffsv in vtuk__vil.list_vars():
                    if (ngpq__xffsv.name in lit_old_idx and ngpq__xffsv.
                        name != tbfif__diil):
                        _insert_build_map(func_ir, ngpq__xffsv.name,
                            znr__lelgu.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if xcq__osj:
                new_body.append(vtuk__vil)
            else:
                func_ir._definitions[vtuk__vil.target.name].remove(vtuk__vil
                    .value)
                lsm__cmc = True
                new_body.append(None)
        fss__tpral = list(lit_old_idx.keys())
        for abzoh__fox in fss__tpral:
            _insert_build_map(func_ir, abzoh__fox, znr__lelgu.body,
                new_body, lit_old_idx, lit_new_idx, map_updates)
        if lsm__cmc:
            znr__lelgu.body = [ntm__xtsp for ntm__xtsp in new_body if 
                ntm__xtsp is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    ulau__ocpxg = lit_old_idx[name]
    xxd__qxtn = lit_new_idx[name]
    biygq__tuxx = map_updates[name]
    new_body[xxd__qxtn] = _build_new_build_map(func_ir, name, old_body,
        ulau__ocpxg, biygq__tuxx)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    qffbc__pjvu = old_body[old_lineno]
    orsx__usdf = qffbc__pjvu.target
    iswmx__anmf = qffbc__pjvu.value
    ykynd__imh = []
    mhtrt__nct = []
    for zmuex__gunw in new_items:
        nlb__ach, uuqdc__fdgiz = zmuex__gunw
        cqw__lsxg = guard(get_definition, func_ir, nlb__ach)
        if isinstance(cqw__lsxg, (ir.Const, ir.Global, ir.FreeVar)):
            ykynd__imh.append(cqw__lsxg.value)
        gyx__aeoq = guard(get_definition, func_ir, uuqdc__fdgiz)
        if isinstance(gyx__aeoq, (ir.Const, ir.Global, ir.FreeVar)):
            mhtrt__nct.append(gyx__aeoq.value)
        else:
            mhtrt__nct.append(numba.core.interpreter._UNKNOWN_VALUE(
                uuqdc__fdgiz.name))
    wdl__cbpxx = {}
    if len(ykynd__imh) == len(new_items):
        ebdm__nce = {ntm__xtsp: vnv__kjk for ntm__xtsp, vnv__kjk in zip(
            ykynd__imh, mhtrt__nct)}
        for vkn__lbgnp, nlb__ach in enumerate(ykynd__imh):
            wdl__cbpxx[nlb__ach] = vkn__lbgnp
    else:
        ebdm__nce = None
    cpwz__xzxjt = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=ebdm__nce, value_indexes=wdl__cbpxx, loc=iswmx__anmf.loc)
    func_ir._definitions[name].append(cpwz__xzxjt)
    return ir.Assign(cpwz__xzxjt, ir.Var(orsx__usdf.scope, name, orsx__usdf
        .loc), cpwz__xzxjt.loc)
