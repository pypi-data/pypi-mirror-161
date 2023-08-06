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
    pmc__ejcok = MPI.COMM_WORLD
    sunym__cav = pmc__ejcok.Get_rank()
    bhgrl__ovqp = get_host_ranks()
    xgtq__zqa = get_nodes_first_ranks()
    if sunym__cav in xgtq__zqa:
        try:
            bueh__xxjhi = get_num_gpus(framework)
        except Exception as ntv__ghrv:
            bueh__xxjhi = ntv__ghrv
        emhf__tbw = create_subcomm_mpi4py(xgtq__zqa)
        ogxav__yjnqw = emhf__tbw.gather(bueh__xxjhi)
        if sunym__cav == 0:
            gpu_ranks = []
            xzut__oco = None
            for xpeei__iakii, obqh__ezrk in enumerate(bhgrl__ovqp.values()):
                isl__lfvy = ogxav__yjnqw[xpeei__iakii]
                if isinstance(isl__lfvy, Exception):
                    xzut__oco = isl__lfvy
                    break
                if isl__lfvy == 0:
                    continue
                jtft__sqv = len(obqh__ezrk) // isl__lfvy
                for xaikp__mqro, ubgbu__ownp in enumerate(obqh__ezrk):
                    if xaikp__mqro % jtft__sqv == 0:
                        gcbk__gbkk = xaikp__mqro / jtft__sqv
                        if gcbk__gbkk < isl__lfvy:
                            gpu_ranks.append(ubgbu__ownp)
            if xzut__oco:
                pmc__ejcok.bcast(xzut__oco)
                raise xzut__oco
            else:
                pmc__ejcok.bcast(gpu_ranks)
    if sunym__cav != 0:
        gpu_ranks = pmc__ejcok.bcast(None)
        if isinstance(gpu_ranks, Exception):
            ntv__ghrv = gpu_ranks
            raise ntv__ghrv
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
    hvzin__zhqw = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        emhf__tbw = MPI.COMM_WORLD.Split(color=0 if hvzin__zhqw in
            gpu_ranks else MPI.UNDEFINED, key=hvzin__zhqw)
        if emhf__tbw != MPI.COMM_NULL:
            hvd.init(comm=emhf__tbw)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                tthv__xelb = tf.config.experimental.list_physical_devices('GPU'
                    )
                for gyaah__mpxia in tthv__xelb:
                    tf.config.experimental.set_memory_growth(gyaah__mpxia, True
                        )
                tf.config.experimental.set_visible_devices(tthv__xelb[hvd.
                    local_rank()], 'GPU')
    else:
        if hvzin__zhqw == 0:
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
        txmn__dvs = 17
        pmc__ejcok = MPI.COMM_WORLD
        oyia__wwqds = MPI.Get_processor_name()
        jnet__hjq = get_host_ranks()[oyia__wwqds]
        assert_dl_initialized()
        if bodo.get_rank() == jnet__hjq[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for sunym__cav in jnet__hjq[1:]:
                pmc__ejcok.isend(1, dest=sunym__cav, tag=txmn__dvs)
        else:
            while True:
                fgrg__omm = MPI.Status()
                bmr__qut = pmc__ejcok.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    fgrg__omm)
                if bmr__qut:
                    assert fgrg__omm.source == jnet__hjq[0]
                    assert fgrg__omm.tag == txmn__dvs
                    pmc__ejcok.recv(source=0, tag=txmn__dvs)
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
