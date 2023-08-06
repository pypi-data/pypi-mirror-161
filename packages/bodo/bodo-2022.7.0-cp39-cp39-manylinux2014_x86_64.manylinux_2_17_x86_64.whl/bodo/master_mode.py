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
        xbjht__wyl = state
        tyj__eunez = inspect.getsourcelines(xbjht__wyl)[0][0]
        assert tyj__eunez.startswith('@bodo.jit') or tyj__eunez.startswith(
            '@jit')
        kco__epz = eval(tyj__eunez[1:])
        self.dispatcher = kco__epz(xbjht__wyl)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    ldho__ezi = MPI.COMM_WORLD
    while True:
        eolo__bzq = ldho__ezi.bcast(None, root=MASTER_RANK)
        if eolo__bzq[0] == 'exec':
            xbjht__wyl = pickle.loads(eolo__bzq[1])
            for gqbnv__xhb, apfu__ossin in list(xbjht__wyl.__globals__.items()
                ):
                if isinstance(apfu__ossin, MasterModeDispatcher):
                    xbjht__wyl.__globals__[gqbnv__xhb] = apfu__ossin.dispatcher
            if xbjht__wyl.__module__ not in sys.modules:
                sys.modules[xbjht__wyl.__module__] = pytypes.ModuleType(
                    xbjht__wyl.__module__)
            tyj__eunez = inspect.getsourcelines(xbjht__wyl)[0][0]
            assert tyj__eunez.startswith('@bodo.jit') or tyj__eunez.startswith(
                '@jit')
            kco__epz = eval(tyj__eunez[1:])
            func = kco__epz(xbjht__wyl)
            psj__fhnu = eolo__bzq[2]
            ueam__lemu = eolo__bzq[3]
            cev__tcvce = []
            for zgu__rijkd in psj__fhnu:
                if zgu__rijkd == 'scatter':
                    cev__tcvce.append(bodo.scatterv(None))
                elif zgu__rijkd == 'bcast':
                    cev__tcvce.append(ldho__ezi.bcast(None, root=MASTER_RANK))
            laod__vqyx = {}
            for argname, zgu__rijkd in ueam__lemu.items():
                if zgu__rijkd == 'scatter':
                    laod__vqyx[argname] = bodo.scatterv(None)
                elif zgu__rijkd == 'bcast':
                    laod__vqyx[argname] = ldho__ezi.bcast(None, root=
                        MASTER_RANK)
            dghe__ntt = func(*cev__tcvce, **laod__vqyx)
            if dghe__ntt is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(dghe__ntt)
            del (eolo__bzq, xbjht__wyl, func, kco__epz, psj__fhnu,
                ueam__lemu, cev__tcvce, laod__vqyx, dghe__ntt)
            gc.collect()
        elif eolo__bzq[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    ldho__ezi = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        psj__fhnu = ['scatter' for scf__jivyz in range(len(args))]
        ueam__lemu = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        osp__cpak = func.py_func.__code__.co_varnames
        dkuk__cakm = func.targetoptions

        def get_distribution(argname):
            if argname in dkuk__cakm.get('distributed', []
                ) or argname in dkuk__cakm.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        psj__fhnu = [get_distribution(argname) for argname in osp__cpak[:
            len(args)]]
        ueam__lemu = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    canz__nwz = pickle.dumps(func.py_func)
    ldho__ezi.bcast(['exec', canz__nwz, psj__fhnu, ueam__lemu])
    cev__tcvce = []
    for pewtb__lpy, zgu__rijkd in zip(args, psj__fhnu):
        if zgu__rijkd == 'scatter':
            cev__tcvce.append(bodo.scatterv(pewtb__lpy))
        elif zgu__rijkd == 'bcast':
            ldho__ezi.bcast(pewtb__lpy)
            cev__tcvce.append(pewtb__lpy)
    laod__vqyx = {}
    for argname, pewtb__lpy in kwargs.items():
        zgu__rijkd = ueam__lemu[argname]
        if zgu__rijkd == 'scatter':
            laod__vqyx[argname] = bodo.scatterv(pewtb__lpy)
        elif zgu__rijkd == 'bcast':
            ldho__ezi.bcast(pewtb__lpy)
            laod__vqyx[argname] = pewtb__lpy
    cvxk__hgzd = []
    for gqbnv__xhb, apfu__ossin in list(func.py_func.__globals__.items()):
        if isinstance(apfu__ossin, MasterModeDispatcher):
            cvxk__hgzd.append((func.py_func.__globals__, gqbnv__xhb, func.
                py_func.__globals__[gqbnv__xhb]))
            func.py_func.__globals__[gqbnv__xhb] = apfu__ossin.dispatcher
    dghe__ntt = func(*cev__tcvce, **laod__vqyx)
    for qoqw__jxjv, gqbnv__xhb, apfu__ossin in cvxk__hgzd:
        qoqw__jxjv[gqbnv__xhb] = apfu__ossin
    if dghe__ntt is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        dghe__ntt = bodo.gatherv(dghe__ntt)
    return dghe__ntt


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
