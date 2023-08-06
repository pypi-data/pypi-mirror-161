"""Support distributed deep learning with Horovod
"""
import time
import numba
import numpy as np
from mpi4py import MPI
import bodo
from bodo.libs.distributed_api import create_subcomm_mpi4py, get_host_ranks, get_nodes_first_ranks
dl_status = None


def assert_dl_initialized():
    assert dl_status is not None, 'Horovod has not been initialized. Call bodo.dl.start() first'


class DLStatus(object):

    def __init__(self, framework, gpu_ranks):
        self.framework = framework
        self.gpu_ranks = gpu_ranks


def get_num_gpus(framework):
    if framework == 'torch':
        import torch
        return torch.cuda.device_count()
    elif framework == 'tensorflow':
        import tensorflow as tf
        return len(tf.config.experimental.list_physical_devices('GPU'))
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))


def get_gpu_ranks(framework):
    smh__hbw = MPI.COMM_WORLD
    bzdlo__nrk = smh__hbw.Get_rank()
    gstxo__mvieb = get_host_ranks()
    ltt__ngq = get_nodes_first_ranks()
    if bzdlo__nrk in ltt__ngq:
        try:
            dmhl__usqe = get_num_gpus(framework)
        except Exception as qgew__okxoc:
            dmhl__usqe = qgew__okxoc
        ozh__ajah = create_subcomm_mpi4py(ltt__ngq)
        wsgfd__cqrhd = ozh__ajah.gather(dmhl__usqe)
        if bzdlo__nrk == 0:
            gpu_ranks = []
            hnix__vlkj = None
            for kdgi__vwymv, ust__arcn in enumerate(gstxo__mvieb.values()):
                azf__hrc = wsgfd__cqrhd[kdgi__vwymv]
                if isinstance(azf__hrc, Exception):
                    hnix__vlkj = azf__hrc
                    break
                if azf__hrc == 0:
                    continue
                hlis__udamr = len(ust__arcn) // azf__hrc
                for yhiud__gfkv, rgwsv__rcz in enumerate(ust__arcn):
                    if yhiud__gfkv % hlis__udamr == 0:
                        gzef__qjyit = yhiud__gfkv / hlis__udamr
                        if gzef__qjyit < azf__hrc:
                            gpu_ranks.append(rgwsv__rcz)
            if hnix__vlkj:
                smh__hbw.bcast(hnix__vlkj)
                raise hnix__vlkj
            else:
                smh__hbw.bcast(gpu_ranks)
    if bzdlo__nrk != 0:
        gpu_ranks = smh__hbw.bcast(None)
        if isinstance(gpu_ranks, Exception):
            qgew__okxoc = gpu_ranks
            raise qgew__okxoc
    return gpu_ranks


def is_cuda_available():
    assert_dl_initialized()
    return len(dl_status.gpu_ranks) > 0


def initialize_horovod(framework):
    global dl_status
    if dl_status is not None:
        assert dl_status.framework == framework, 'Attempted to initialize Horovod with different DL frameworks'
        return np.array(dl_status.gpu_ranks, dtype=np.int32)
    gpu_ranks = get_gpu_ranks(framework)
    if framework == 'torch':
        import horovod.torch as hvd
        import torch
        torch.set_num_threads(1)
    elif framework == 'tensorflow':
        import horovod.tensorflow as hvd
        import tensorflow as tf
    else:
        raise RuntimeError('Framework {} not recognized'.format(framework))
    wunk__strvi = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        ozh__ajah = MPI.COMM_WORLD.Split(color=0 if wunk__strvi in
            gpu_ranks else MPI.UNDEFINED, key=wunk__strvi)
        if ozh__ajah != MPI.COMM_NULL:
            hvd.init(comm=ozh__ajah)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                oucni__jdjxh = tf.config.experimental.list_physical_devices(
                    'GPU')
                for iqu__ckpt in oucni__jdjxh:
                    tf.config.experimental.set_memory_growth(iqu__ckpt, True)
                tf.config.experimental.set_visible_devices(oucni__jdjxh[hvd
                    .local_rank()], 'GPU')
    else:
        if wunk__strvi == 0:
            print('[BODO-DL]: No GPUs found in cluster. Using CPUs')
        hvd.init()
    dl_status = DLStatus(framework, np.array(gpu_ranks, dtype=np.int32))


@numba.njit
def start(framework):
    with numba.objmode:
        initialize_horovod(framework)


@numba.njit
def end():
    with numba.objmode:
        end_py()


def end_py():
    if is_cuda_available():
        ntys__dnctv = 17
        smh__hbw = MPI.COMM_WORLD
        smxe__qlp = MPI.Get_processor_name()
        xru__eqx = get_host_ranks()[smxe__qlp]
        assert_dl_initialized()
        if bodo.get_rank() == xru__eqx[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for bzdlo__nrk in xru__eqx[1:]:
                smh__hbw.isend(1, dest=bzdlo__nrk, tag=ntys__dnctv)
        else:
            while True:
                unh__gpe = MPI.Status()
                vxola__amoip = smh__hbw.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    unh__gpe)
                if vxola__amoip:
                    assert unh__gpe.source == xru__eqx[0]
                    assert unh__gpe.tag == ntys__dnctv
                    smh__hbw.recv(source=0, tag=ntys__dnctv)
                    break
                time.sleep(1.0)
    else:
        bodo.barrier()


def _prepare_data_get_gpu_ranks():
    assert_dl_initialized()
    return dl_status.gpu_ranks


@numba.njit
def prepare_data(data):
    with numba.objmode(gpu_ranks='int32[:]'):
        gpu_ranks = _prepare_data_get_gpu_ranks()
    if len(gpu_ranks) > 0:
        data = bodo.rebalance(data, dests=list(gpu_ranks), parallel=True)
    else:
        data = bodo.rebalance(data, parallel=True)
    return data
