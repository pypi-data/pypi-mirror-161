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
    for nxuu__jazfk in func_ir.blocks.values():
        new_body = []
        ewgab__rcohe = {}
        for kxg__kabi, huv__alrtp in enumerate(nxuu__jazfk.body):
            tyx__qrkvw = None
            if isinstance(huv__alrtp, ir.Assign) and isinstance(huv__alrtp.
                value, ir.Expr):
                zab__abef = huv__alrtp.target.name
                if huv__alrtp.value.op == 'build_tuple':
                    tyx__qrkvw = zab__abef
                    ewgab__rcohe[zab__abef] = huv__alrtp.value.items
                elif huv__alrtp.value.op == 'binop' and huv__alrtp.value.fn == operator.add and huv__alrtp.value.lhs.name in ewgab__rcohe and huv__alrtp.value.rhs.name in ewgab__rcohe:
                    tyx__qrkvw = zab__abef
                    new_items = ewgab__rcohe[huv__alrtp.value.lhs.name
                        ] + ewgab__rcohe[huv__alrtp.value.rhs.name]
                    ciw__izqs = ir.Expr.build_tuple(new_items, huv__alrtp.
                        value.loc)
                    ewgab__rcohe[zab__abef] = new_items
                    del ewgab__rcohe[huv__alrtp.value.lhs.name]
                    del ewgab__rcohe[huv__alrtp.value.rhs.name]
                    if huv__alrtp.value in func_ir._definitions[zab__abef]:
                        func_ir._definitions[zab__abef].remove(huv__alrtp.value
                            )
                    func_ir._definitions[zab__abef].append(ciw__izqs)
                    huv__alrtp = ir.Assign(ciw__izqs, huv__alrtp.target,
                        huv__alrtp.loc)
            for ehmom__tbapf in huv__alrtp.list_vars():
                if (ehmom__tbapf.name in ewgab__rcohe and ehmom__tbapf.name !=
                    tyx__qrkvw):
                    del ewgab__rcohe[ehmom__tbapf.name]
            new_body.append(huv__alrtp)
        nxuu__jazfk.body = new_body
    return func_ir


def _call_function_ex_replace_kws_small(keyword_expr, new_body, buildmap_idx):
    xmu__rpf = keyword_expr.items.copy()
    bbbi__hneyq = keyword_expr.value_indexes
    for zendg__bgrk, ixph__llgr in bbbi__hneyq.items():
        xmu__rpf[ixph__llgr] = zendg__bgrk, xmu__rpf[ixph__llgr][1]
    new_body[buildmap_idx] = None
    return xmu__rpf


def _call_function_ex_replace_kws_large(body, buildmap_name, buildmap_idx,
    search_end, new_body):
    dphca__zlccv = 'CALL_FUNCTION_EX with **kwargs not supported'
    new_body[buildmap_idx] = None
    xmu__rpf = []
    luv__nwd = buildmap_idx + 1
    while luv__nwd <= search_end:
        fhdus__udyr = body[luv__nwd]
        if not (isinstance(fhdus__udyr, ir.Assign) and isinstance(
            fhdus__udyr.value, ir.Const)):
            raise UnsupportedError(dphca__zlccv)
        cfxb__rcdve = fhdus__udyr.target.name
        scm__audz = fhdus__udyr.value.value
        luv__nwd += 1
        rmya__gloz = True
        while luv__nwd <= search_end and rmya__gloz:
            nagb__mhbw = body[luv__nwd]
            if (isinstance(nagb__mhbw, ir.Assign) and isinstance(nagb__mhbw
                .value, ir.Expr) and nagb__mhbw.value.op == 'getattr' and 
                nagb__mhbw.value.value.name == buildmap_name and nagb__mhbw
                .value.attr == '__setitem__'):
                rmya__gloz = False
            else:
                luv__nwd += 1
        if rmya__gloz or luv__nwd == search_end:
            raise UnsupportedError(dphca__zlccv)
        gsib__hbcej = body[luv__nwd + 1]
        if not (isinstance(gsib__hbcej, ir.Assign) and isinstance(
            gsib__hbcej.value, ir.Expr) and gsib__hbcej.value.op == 'call' and
            gsib__hbcej.value.func.name == nagb__mhbw.target.name and len(
            gsib__hbcej.value.args) == 2 and gsib__hbcej.value.args[0].name ==
            cfxb__rcdve):
            raise UnsupportedError(dphca__zlccv)
        mbhyl__vlzsa = gsib__hbcej.value.args[1]
        xmu__rpf.append((scm__audz, mbhyl__vlzsa))
        new_body[luv__nwd] = None
        new_body[luv__nwd + 1] = None
        luv__nwd += 2
    return xmu__rpf


def _call_function_ex_replace_args_small(tuple_expr, new_body, buildtuple_idx):
    new_body[buildtuple_idx] = None
    return tuple_expr.items


def _call_function_ex_replace_args_large(vararg_stmt, body, new_body,
    search_end):
    dphca__zlccv = 'CALL_FUNCTION_EX with **kwargs not supported'
    luv__nwd = 0
    glk__ual = []
    if isinstance(vararg_stmt, ir.Assign) and isinstance(vararg_stmt.value,
        ir.Var):
        zise__wmfxx = vararg_stmt.value.name
        new_body[search_end] = None
        search_end -= 1
    else:
        zise__wmfxx = vararg_stmt.target.name
    zdo__poi = True
    while search_end >= luv__nwd and zdo__poi:
        zwa__kupna = body[search_end]
        if (isinstance(zwa__kupna, ir.Assign) and zwa__kupna.target.name ==
            zise__wmfxx and isinstance(zwa__kupna.value, ir.Expr) and 
            zwa__kupna.value.op == 'build_tuple' and not zwa__kupna.value.items
            ):
            zdo__poi = False
            new_body[search_end] = None
        else:
            if search_end == luv__nwd or not (isinstance(zwa__kupna, ir.
                Assign) and zwa__kupna.target.name == zise__wmfxx and
                isinstance(zwa__kupna.value, ir.Expr) and zwa__kupna.value.
                op == 'binop' and zwa__kupna.value.fn == operator.add):
                raise UnsupportedError(dphca__zlccv)
            fbca__jni = zwa__kupna.value.lhs.name
            chi__tccz = zwa__kupna.value.rhs.name
            zkq__brl = body[search_end - 1]
            if not (isinstance(zkq__brl, ir.Assign) and isinstance(zkq__brl
                .value, ir.Expr) and zkq__brl.value.op == 'build_tuple' and
                len(zkq__brl.value.items) == 1):
                raise UnsupportedError(dphca__zlccv)
            if zkq__brl.target.name == fbca__jni:
                zise__wmfxx = chi__tccz
            elif zkq__brl.target.name == chi__tccz:
                zise__wmfxx = fbca__jni
            else:
                raise UnsupportedError(dphca__zlccv)
            glk__ual.append(zkq__brl.value.items[0])
            new_body[search_end] = None
            new_body[search_end - 1] = None
            search_end -= 2
            evlja__nwgz = True
            while search_end >= luv__nwd and evlja__nwgz:
                otgzu__zuc = body[search_end]
                if isinstance(otgzu__zuc, ir.Assign
                    ) and otgzu__zuc.target.name == zise__wmfxx:
                    evlja__nwgz = False
                else:
                    search_end -= 1
    if zdo__poi:
        raise UnsupportedError(dphca__zlccv)
    return glk__ual[::-1]


def peep_hole_call_function_ex_to_call_function_kw(func_ir):
    dphca__zlccv = 'CALL_FUNCTION_EX with **kwargs not supported'
    for nxuu__jazfk in func_ir.blocks.values():
        nbxz__bahu = False
        new_body = []
        for kxg__kabi, huv__alrtp in enumerate(nxuu__jazfk.body):
            if (isinstance(huv__alrtp, ir.Assign) and isinstance(huv__alrtp
                .value, ir.Expr) and huv__alrtp.value.op == 'call' and 
                huv__alrtp.value.varkwarg is not None):
                nbxz__bahu = True
                qjnx__kxn = huv__alrtp.value
                args = qjnx__kxn.args
                xmu__rpf = qjnx__kxn.kws
                clohc__siyo = qjnx__kxn.vararg
                mro__wpw = qjnx__kxn.varkwarg
                ayhn__rma = kxg__kabi - 1
                bngm__qrvb = ayhn__rma
                wdnxr__zaavn = None
                kvn__lgzyv = True
                while bngm__qrvb >= 0 and kvn__lgzyv:
                    wdnxr__zaavn = nxuu__jazfk.body[bngm__qrvb]
                    if isinstance(wdnxr__zaavn, ir.Assign
                        ) and wdnxr__zaavn.target.name == mro__wpw.name:
                        kvn__lgzyv = False
                    else:
                        bngm__qrvb -= 1
                if xmu__rpf or kvn__lgzyv or not (isinstance(wdnxr__zaavn.
                    value, ir.Expr) and wdnxr__zaavn.value.op == 'build_map'):
                    raise UnsupportedError(dphca__zlccv)
                if wdnxr__zaavn.value.items:
                    xmu__rpf = _call_function_ex_replace_kws_small(wdnxr__zaavn
                        .value, new_body, bngm__qrvb)
                else:
                    xmu__rpf = _call_function_ex_replace_kws_large(nxuu__jazfk
                        .body, mro__wpw.name, bngm__qrvb, kxg__kabi - 1,
                        new_body)
                ayhn__rma = bngm__qrvb
                if clohc__siyo is not None:
                    if args:
                        raise UnsupportedError(dphca__zlccv)
                    sdl__yijy = ayhn__rma
                    dqw__aobf = None
                    kvn__lgzyv = True
                    while sdl__yijy >= 0 and kvn__lgzyv:
                        dqw__aobf = nxuu__jazfk.body[sdl__yijy]
                        if isinstance(dqw__aobf, ir.Assign
                            ) and dqw__aobf.target.name == clohc__siyo.name:
                            kvn__lgzyv = False
                        else:
                            sdl__yijy -= 1
                    if kvn__lgzyv:
                        raise UnsupportedError(dphca__zlccv)
                    if isinstance(dqw__aobf.value, ir.Expr
                        ) and dqw__aobf.value.op == 'build_tuple':
                        args = _call_function_ex_replace_args_small(dqw__aobf
                            .value, new_body, sdl__yijy)
                    else:
                        args = _call_function_ex_replace_args_large(dqw__aobf,
                            nxuu__jazfk.body, new_body, sdl__yijy)
                qxhng__efet = ir.Expr.call(qjnx__kxn.func, args, xmu__rpf,
                    qjnx__kxn.loc, target=qjnx__kxn.target)
                if huv__alrtp.target.name in func_ir._definitions and len(
                    func_ir._definitions[huv__alrtp.target.name]) == 1:
                    func_ir._definitions[huv__alrtp.target.name].clear()
                func_ir._definitions[huv__alrtp.target.name].append(qxhng__efet
                    )
                huv__alrtp = ir.Assign(qxhng__efet, huv__alrtp.target,
                    huv__alrtp.loc)
            new_body.append(huv__alrtp)
        if nbxz__bahu:
            nxuu__jazfk.body = [ndgqn__ghr for ndgqn__ghr in new_body if 
                ndgqn__ghr is not None]
    return func_ir


def peep_hole_fuse_dict_add_updates(func_ir):
    for nxuu__jazfk in func_ir.blocks.values():
        new_body = []
        lit_old_idx = {}
        lit_new_idx = {}
        map_updates = {}
        nbxz__bahu = False
        for kxg__kabi, huv__alrtp in enumerate(nxuu__jazfk.body):
            bafwy__cvhwy = True
            lyitu__arpp = None
            if isinstance(huv__alrtp, ir.Assign) and isinstance(huv__alrtp.
                value, ir.Expr):
                if huv__alrtp.value.op == 'build_map':
                    lyitu__arpp = huv__alrtp.target.name
                    lit_old_idx[huv__alrtp.target.name] = kxg__kabi
                    lit_new_idx[huv__alrtp.target.name] = kxg__kabi
                    map_updates[huv__alrtp.target.name
                        ] = huv__alrtp.value.items.copy()
                    bafwy__cvhwy = False
                elif huv__alrtp.value.op == 'call' and kxg__kabi > 0:
                    jgqi__otoe = huv__alrtp.value.func.name
                    nagb__mhbw = nxuu__jazfk.body[kxg__kabi - 1]
                    args = huv__alrtp.value.args
                    if (isinstance(nagb__mhbw, ir.Assign) and nagb__mhbw.
                        target.name == jgqi__otoe and isinstance(nagb__mhbw
                        .value, ir.Expr) and nagb__mhbw.value.op ==
                        'getattr' and nagb__mhbw.value.value.name in
                        lit_old_idx):
                        tfh__nwhb = nagb__mhbw.value.value.name
                        qsivg__lqy = nagb__mhbw.value.attr
                        if qsivg__lqy == '__setitem__':
                            bafwy__cvhwy = False
                            map_updates[tfh__nwhb].append(args)
                            new_body[-1] = None
                        elif qsivg__lqy == 'update' and args[0
                            ].name in lit_old_idx:
                            bafwy__cvhwy = False
                            map_updates[tfh__nwhb].extend(map_updates[args[
                                0].name])
                            new_body[-1] = None
                        if not bafwy__cvhwy:
                            lit_new_idx[tfh__nwhb] = kxg__kabi
                            func_ir._definitions[nagb__mhbw.target.name
                                ].remove(nagb__mhbw.value)
            if not (isinstance(huv__alrtp, ir.Assign) and isinstance(
                huv__alrtp.value, ir.Expr) and huv__alrtp.value.op ==
                'getattr' and huv__alrtp.value.value.name in lit_old_idx and
                huv__alrtp.value.attr in ('__setitem__', 'update')):
                for ehmom__tbapf in huv__alrtp.list_vars():
                    if (ehmom__tbapf.name in lit_old_idx and ehmom__tbapf.
                        name != lyitu__arpp):
                        _insert_build_map(func_ir, ehmom__tbapf.name,
                            nxuu__jazfk.body, new_body, lit_old_idx,
                            lit_new_idx, map_updates)
            if bafwy__cvhwy:
                new_body.append(huv__alrtp)
            else:
                func_ir._definitions[huv__alrtp.target.name].remove(huv__alrtp
                    .value)
                nbxz__bahu = True
                new_body.append(None)
        pmyx__pxmmi = list(lit_old_idx.keys())
        for vpiqk__klfqj in pmyx__pxmmi:
            _insert_build_map(func_ir, vpiqk__klfqj, nxuu__jazfk.body,
                new_body, lit_old_idx, lit_new_idx, map_updates)
        if nbxz__bahu:
            nxuu__jazfk.body = [ndgqn__ghr for ndgqn__ghr in new_body if 
                ndgqn__ghr is not None]
    return func_ir


def _insert_build_map(func_ir, name, old_body, new_body, lit_old_idx,
    lit_new_idx, map_updates):
    truix__njjbv = lit_old_idx[name]
    aim__vnr = lit_new_idx[name]
    thwy__uvn = map_updates[name]
    new_body[aim__vnr] = _build_new_build_map(func_ir, name, old_body,
        truix__njjbv, thwy__uvn)
    del lit_old_idx[name]
    del lit_new_idx[name]
    del map_updates[name]


def _build_new_build_map(func_ir, name, old_body, old_lineno, new_items):
    inrj__wvga = old_body[old_lineno]
    qxy__zvyfb = inrj__wvga.target
    bczhl__vvtli = inrj__wvga.value
    fzlmt__mzidk = []
    sfpj__rzlvo = []
    for amnhi__crwfc in new_items:
        ofcf__hsrq, qwaxp__monoa = amnhi__crwfc
        twg__qvp = guard(get_definition, func_ir, ofcf__hsrq)
        if isinstance(twg__qvp, (ir.Const, ir.Global, ir.FreeVar)):
            fzlmt__mzidk.append(twg__qvp.value)
        xwia__ijryi = guard(get_definition, func_ir, qwaxp__monoa)
        if isinstance(xwia__ijryi, (ir.Const, ir.Global, ir.FreeVar)):
            sfpj__rzlvo.append(xwia__ijryi.value)
        else:
            sfpj__rzlvo.append(numba.core.interpreter._UNKNOWN_VALUE(
                qwaxp__monoa.name))
    bbbi__hneyq = {}
    if len(fzlmt__mzidk) == len(new_items):
        ytovb__uofj = {ndgqn__ghr: pjrft__qhd for ndgqn__ghr, pjrft__qhd in
            zip(fzlmt__mzidk, sfpj__rzlvo)}
        for kxg__kabi, ofcf__hsrq in enumerate(fzlmt__mzidk):
            bbbi__hneyq[ofcf__hsrq] = kxg__kabi
    else:
        ytovb__uofj = None
    locu__oxtop = ir.Expr.build_map(items=new_items, size=len(new_items),
        literal_value=ytovb__uofj, value_indexes=bbbi__hneyq, loc=
        bczhl__vvtli.loc)
    func_ir._definitions[name].append(locu__oxtop)
    return ir.Assign(locu__oxtop, ir.Var(qxy__zvyfb.scope, name, qxy__zvyfb
        .loc), locu__oxtop.loc)
