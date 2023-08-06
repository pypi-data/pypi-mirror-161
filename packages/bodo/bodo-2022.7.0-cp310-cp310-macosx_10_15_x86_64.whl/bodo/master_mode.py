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
        nzhfe__wzx = state
        iwtb__apwxt = inspect.getsourcelines(nzhfe__wzx)[0][0]
        assert iwtb__apwxt.startswith('@bodo.jit') or iwtb__apwxt.startswith(
            '@jit')
        ybj__xuti = eval(iwtb__apwxt[1:])
        self.dispatcher = ybj__xuti(nzhfe__wzx)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    cjukt__hva = MPI.COMM_WORLD
    while True:
        yrtt__dox = cjukt__hva.bcast(None, root=MASTER_RANK)
        if yrtt__dox[0] == 'exec':
            nzhfe__wzx = pickle.loads(yrtt__dox[1])
            for wmr__kupip, fxt__nwlci in list(nzhfe__wzx.__globals__.items()):
                if isinstance(fxt__nwlci, MasterModeDispatcher):
                    nzhfe__wzx.__globals__[wmr__kupip] = fxt__nwlci.dispatcher
            if nzhfe__wzx.__module__ not in sys.modules:
                sys.modules[nzhfe__wzx.__module__] = pytypes.ModuleType(
                    nzhfe__wzx.__module__)
            iwtb__apwxt = inspect.getsourcelines(nzhfe__wzx)[0][0]
            assert iwtb__apwxt.startswith('@bodo.jit'
                ) or iwtb__apwxt.startswith('@jit')
            ybj__xuti = eval(iwtb__apwxt[1:])
            func = ybj__xuti(nzhfe__wzx)
            awlok__axz = yrtt__dox[2]
            ruo__ixvv = yrtt__dox[3]
            dmel__ifi = []
            for ipn__vkq in awlok__axz:
                if ipn__vkq == 'scatter':
                    dmel__ifi.append(bodo.scatterv(None))
                elif ipn__vkq == 'bcast':
                    dmel__ifi.append(cjukt__hva.bcast(None, root=MASTER_RANK))
            mhzm__jlrcm = {}
            for argname, ipn__vkq in ruo__ixvv.items():
                if ipn__vkq == 'scatter':
                    mhzm__jlrcm[argname] = bodo.scatterv(None)
                elif ipn__vkq == 'bcast':
                    mhzm__jlrcm[argname] = cjukt__hva.bcast(None, root=
                        MASTER_RANK)
            dgxw__gcq = func(*dmel__ifi, **mhzm__jlrcm)
            if dgxw__gcq is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(dgxw__gcq)
            del (yrtt__dox, nzhfe__wzx, func, ybj__xuti, awlok__axz,
                ruo__ixvv, dmel__ifi, mhzm__jlrcm, dgxw__gcq)
            gc.collect()
        elif yrtt__dox[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    cjukt__hva = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        awlok__axz = ['scatter' for gya__uec in range(len(args))]
        ruo__ixvv = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        kdeqd__nkav = func.py_func.__code__.co_varnames
        tlcgm__deshd = func.targetoptions

        def get_distribution(argname):
            if argname in tlcgm__deshd.get('distributed', []
                ) or argname in tlcgm__deshd.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        awlok__axz = [get_distribution(argname) for argname in kdeqd__nkav[
            :len(args)]]
        ruo__ixvv = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    qkfkb__uiisr = pickle.dumps(func.py_func)
    cjukt__hva.bcast(['exec', qkfkb__uiisr, awlok__axz, ruo__ixvv])
    dmel__ifi = []
    for okln__usw, ipn__vkq in zip(args, awlok__axz):
        if ipn__vkq == 'scatter':
            dmel__ifi.append(bodo.scatterv(okln__usw))
        elif ipn__vkq == 'bcast':
            cjukt__hva.bcast(okln__usw)
            dmel__ifi.append(okln__usw)
    mhzm__jlrcm = {}
    for argname, okln__usw in kwargs.items():
        ipn__vkq = ruo__ixvv[argname]
        if ipn__vkq == 'scatter':
            mhzm__jlrcm[argname] = bodo.scatterv(okln__usw)
        elif ipn__vkq == 'bcast':
            cjukt__hva.bcast(okln__usw)
            mhzm__jlrcm[argname] = okln__usw
    ihhhs__zja = []
    for wmr__kupip, fxt__nwlci in list(func.py_func.__globals__.items()):
        if isinstance(fxt__nwlci, MasterModeDispatcher):
            ihhhs__zja.append((func.py_func.__globals__, wmr__kupip, func.
                py_func.__globals__[wmr__kupip]))
            func.py_func.__globals__[wmr__kupip] = fxt__nwlci.dispatcher
    dgxw__gcq = func(*dmel__ifi, **mhzm__jlrcm)
    for dshth__fgk, wmr__kupip, fxt__nwlci in ihhhs__zja:
        dshth__fgk[wmr__kupip] = fxt__nwlci
    if dgxw__gcq is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        dgxw__gcq = bodo.gatherv(dgxw__gcq)
    return dgxw__gcq


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
