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
        zlw__rmmjd = state
        fbydk__edk = inspect.getsourcelines(zlw__rmmjd)[0][0]
        assert fbydk__edk.startswith('@bodo.jit') or fbydk__edk.startswith(
            '@jit')
        fjkj__ddxd = eval(fbydk__edk[1:])
        self.dispatcher = fjkj__ddxd(zlw__rmmjd)


def worker_loop():
    assert bodo.get_rank() != MASTER_RANK
    dfu__zoclr = MPI.COMM_WORLD
    while True:
        aadjr__ivcq = dfu__zoclr.bcast(None, root=MASTER_RANK)
        if aadjr__ivcq[0] == 'exec':
            zlw__rmmjd = pickle.loads(aadjr__ivcq[1])
            for vyznk__qkzs, vrjwe__ygcwk in list(zlw__rmmjd.__globals__.
                items()):
                if isinstance(vrjwe__ygcwk, MasterModeDispatcher):
                    zlw__rmmjd.__globals__[vyznk__qkzs
                        ] = vrjwe__ygcwk.dispatcher
            if zlw__rmmjd.__module__ not in sys.modules:
                sys.modules[zlw__rmmjd.__module__] = pytypes.ModuleType(
                    zlw__rmmjd.__module__)
            fbydk__edk = inspect.getsourcelines(zlw__rmmjd)[0][0]
            assert fbydk__edk.startswith('@bodo.jit') or fbydk__edk.startswith(
                '@jit')
            fjkj__ddxd = eval(fbydk__edk[1:])
            func = fjkj__ddxd(zlw__rmmjd)
            dmb__itsrd = aadjr__ivcq[2]
            txgbv__mgd = aadjr__ivcq[3]
            wrrsr__kyma = []
            for hpgr__fxv in dmb__itsrd:
                if hpgr__fxv == 'scatter':
                    wrrsr__kyma.append(bodo.scatterv(None))
                elif hpgr__fxv == 'bcast':
                    wrrsr__kyma.append(dfu__zoclr.bcast(None, root=MASTER_RANK)
                        )
            tfip__aibjq = {}
            for argname, hpgr__fxv in txgbv__mgd.items():
                if hpgr__fxv == 'scatter':
                    tfip__aibjq[argname] = bodo.scatterv(None)
                elif hpgr__fxv == 'bcast':
                    tfip__aibjq[argname] = dfu__zoclr.bcast(None, root=
                        MASTER_RANK)
            lfhpn__oyg = func(*wrrsr__kyma, **tfip__aibjq)
            if lfhpn__oyg is not None and func.overloads[func.signatures[0]
                ].metadata['is_return_distributed']:
                bodo.gatherv(lfhpn__oyg)
            del (aadjr__ivcq, zlw__rmmjd, func, fjkj__ddxd, dmb__itsrd,
                txgbv__mgd, wrrsr__kyma, tfip__aibjq, lfhpn__oyg)
            gc.collect()
        elif aadjr__ivcq[0] == 'exit':
            exit()
    assert False


def master_wrapper(func, *args, **kwargs):
    dfu__zoclr = MPI.COMM_WORLD
    if {'all_args_distributed', 'all_args_distributed_block',
        'all_args_distributed_varlength'} & set(func.targetoptions.keys()):
        dmb__itsrd = ['scatter' for wwoho__gyut in range(len(args))]
        txgbv__mgd = {argname: 'scatter' for argname in kwargs.keys()}
    else:
        ixyy__twd = func.py_func.__code__.co_varnames
        azvz__uex = func.targetoptions

        def get_distribution(argname):
            if argname in azvz__uex.get('distributed', []
                ) or argname in azvz__uex.get('distributed_block', []):
                return 'scatter'
            else:
                return 'bcast'
        dmb__itsrd = [get_distribution(argname) for argname in ixyy__twd[:
            len(args)]]
        txgbv__mgd = {argname: get_distribution(argname) for argname in
            kwargs.keys()}
    mjlu__rkbu = pickle.dumps(func.py_func)
    dfu__zoclr.bcast(['exec', mjlu__rkbu, dmb__itsrd, txgbv__mgd])
    wrrsr__kyma = []
    for lev__jqaqk, hpgr__fxv in zip(args, dmb__itsrd):
        if hpgr__fxv == 'scatter':
            wrrsr__kyma.append(bodo.scatterv(lev__jqaqk))
        elif hpgr__fxv == 'bcast':
            dfu__zoclr.bcast(lev__jqaqk)
            wrrsr__kyma.append(lev__jqaqk)
    tfip__aibjq = {}
    for argname, lev__jqaqk in kwargs.items():
        hpgr__fxv = txgbv__mgd[argname]
        if hpgr__fxv == 'scatter':
            tfip__aibjq[argname] = bodo.scatterv(lev__jqaqk)
        elif hpgr__fxv == 'bcast':
            dfu__zoclr.bcast(lev__jqaqk)
            tfip__aibjq[argname] = lev__jqaqk
    fwdxl__axb = []
    for vyznk__qkzs, vrjwe__ygcwk in list(func.py_func.__globals__.items()):
        if isinstance(vrjwe__ygcwk, MasterModeDispatcher):
            fwdxl__axb.append((func.py_func.__globals__, vyznk__qkzs, func.
                py_func.__globals__[vyznk__qkzs]))
            func.py_func.__globals__[vyznk__qkzs] = vrjwe__ygcwk.dispatcher
    lfhpn__oyg = func(*wrrsr__kyma, **tfip__aibjq)
    for yjuc__unski, vyznk__qkzs, vrjwe__ygcwk in fwdxl__axb:
        yjuc__unski[vyznk__qkzs] = vrjwe__ygcwk
    if lfhpn__oyg is not None and func.overloads[func.signatures[0]].metadata[
        'is_return_distributed']:
        lfhpn__oyg = bodo.gatherv(lfhpn__oyg)
    return lfhpn__oyg


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
