import gc
import inspect
import sys
import types as pytypes
import bodo
master_mode_on = False
MASTER_RANK = 0


class MasterModeDispatcher(object):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def __call__(self, *args, **kwargs):
        assert bodo.get_rank() == MASTER_RANK
        return master_wrapper(self.dispatcher, *args, **kwargs)

    def __getstate__(self):
        assert bodo.get_rank() == MASTER_RANK
        return self.dispatcher.py_func

    def __setstate__(self, state):
        assert bodo.get_rank() != MASTER_RANK
        gjjad__tbur = state
        cig__eex = inspect.getsourcelines(gjjad__tbur)[0][0]
        assert cig__eex.startswith('@bodo.jit') or cig__eex.startswith('@jit')
        jsiyu__xkb = eval(cig__eex[1:])
        self.dispatcher = jsiyu__xkb(gjjad__tbur)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    loztm__sneac = MPI.COMM_WORLD
    while True:
        gdb__lhjy = loztm__sneac.bcast(None, root=MASTER_RANK)
        if gdb__lhjy[0] == 'exec':
            gjjad__tbur = pickle.loads(gdb__lhjy[1])
            for kzg__deaj, cfe__brl in list(gjjad__tbur.__globals__.items()):
                if isinstance(cfe__brl, MasterModeDispatcher):
                    gjjad__tbur.__globals__[kzg__deaj] = cfe__brl.dispatcher
            if gjjad__tbur.__module__ not in sys.modules:
                sys.modules[gjjad__tbur.__module__] = pytypes.ModuleType(
                    gjjad__tbur.__module__)
            cig__eex = inspect.getsourcelines(gjjad__tbur)[0][0]
            assert cig__eex.startswith('@bodo.jit') or cig__eex.startswith(
                '@jit')
            jsiyu__xkb = eval(cig__eex[1:])
            func = jsiyu__xkb(gjjad__tbur)
            qne__zdmv = gdb__lhjy[2]
            lcz__dwvjf = gdb__lhjy[3]
            tkwhc__ldav = []
            for ckhep__ysx in qne__zdmv:
                if ckhep__ysx == 'scatter':
                    tkwhc__ldav.append(bodo.scatterv(None))
                elif ckhep__ysx == 'bcast':
                    tkwhc__ldav.append(loztm__sneac.bcast(None, root=
                        MASTER_RANK))
            oeu__csof = {}
            for argname, ckhep__ysx in lcz__dwvjf.items():
                if ckhep__ysx == 'scatter':
                    oeu__csof[argname] = bodo.scatterv(None)
                elif ckhep__ysx == 'bcast':
                    oeu__csof[argname] = loztm__sneac.bcast(None, root=
                        MASTER_RANK)
            ggio__bofqi = func(*tkwhc__ldav, **oeu__csof)
            if ggio__bofqi is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(ggio__bofqi)
            del (gdb__lhjy, gjjad__tbur, func, jsiyu__xkb, qne__zdmv,
                lcz__dwvjf, tkwhc__ldav, oeu__csof, ggio__bofqi)
            gc.collect()
        elif gdb__lhjy[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    loztm__sneac = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        qne__zdmv = ['scatter' for xrmg__qqf in range(len(args))]
        lcz__dwvjf = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        ljzh__bxk = func.py_func.__code__.co_varnames
        krye__wgffz = func.targetoptions

        def get_distribution(argname):
            if argname in krye__wgffz.get('distributed', []
                ) or argname in krye__wgffz.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        qne__zdmv = [get_distribution(argname) for argname in ljzh__bxk[:
            len(args)]]
        lcz__dwvjf = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    pqvkw__weyc = pickle.dumps(func.py_func)
    loztm__sneac.bcast(['exec', pqvkw__weyc, qne__zdmv, lcz__dwvjf])
    tkwhc__ldav = []
    for onrv__dhg, ckhep__ysx in zip(args, qne__zdmv):
        if ckhep__ysx == 'scatter':
            tkwhc__ldav.append(bodo.scatterv(onrv__dhg))
        elif ckhep__ysx == 'bcast':
            loztm__sneac.bcast(onrv__dhg)
            tkwhc__ldav.append(onrv__dhg)
    oeu__csof = {}
    for argname, onrv__dhg in kwargs.items():
        ckhep__ysx = lcz__dwvjf[argname]
        if ckhep__ysx == 'scatter':
            oeu__csof[argname] = bodo.scatterv(onrv__dhg)
        elif ckhep__ysx == 'bcast':
            loztm__sneac.bcast(onrv__dhg)
            oeu__csof[argname] = onrv__dhg
    lphm__qyra = []
    for kzg__deaj, cfe__brl in list(func.py_func.__globals__.items()):
        if isinstance(cfe__brl, MasterModeDispatcher):
            lphm__qyra.append((func.py_func.__globals__, kzg__deaj, func.
                py_func.__globals__[kzg__deaj]))
            func.py_func.__globals__[kzg__deaj] = cfe__brl.dispatcher
    ggio__bofqi = func(*tkwhc__ldav, **oeu__csof)
    for mcunx__ntsw, kzg__deaj, cfe__brl in lphm__qyra:
        mcunx__ntsw[kzg__deaj] = cfe__brl
    if ggio__bofqi is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        ggio__bofqi = bodo.gatherv(ggio__bofqi)
    return ggio__bofqi


def init_master_mode():
    if bodo.get_size() == 1:
        return
    global master_mode_on
    assert master_mode_on is False, 'init_master_mode can only be called once on each process'
    master_mode_on = True
    assert sys.version_info[:2] >= (3, 8
        ), 'Python 3.8+ required for master mode'
    from bodo import jit
    globals()['jit'] = jit
    import cloudpickle
    from mpi4py import MPI
    globals()['pickle'] = cloudpickle
    globals()['MPI'] = MPI

    def master_exit():
        MPI.COMM_WORLD.bcast(['exit'])
    if bodo.get_rank() == MASTER_RANK:
        import atexit
        atexit.register(master_exit)
    else:
        worker_loop()
