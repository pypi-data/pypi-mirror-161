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
    kwvz__gtojz = MPI.COMM_WORLD
    jnakc__djw = kwvz__gtojz.Get_rank()
    ettfm__dgwd = get_host_ranks()
    wczc__dho = get_nodes_first_ranks()
    if jnakc__djw in wczc__dho:
        try:
            fuhl__gxhpd = get_num_gpus(framework)
        except Exception as cskuf__geip:
            fuhl__gxhpd = cskuf__geip
        hsigy__yanvi = create_subcomm_mpi4py(wczc__dho)
        dxka__nnryb = hsigy__yanvi.gather(fuhl__gxhpd)
        if jnakc__djw == 0:
            gpu_ranks = []
            stveo__ekp = None
            for xzrb__ubbm, guz__bosb in enumerate(ettfm__dgwd.values()):
                bsw__pgta = dxka__nnryb[xzrb__ubbm]
                if isinstance(bsw__pgta, Exception):
                    stveo__ekp = bsw__pgta
                    break
                if bsw__pgta == 0:
                    continue
                ulg__fri = len(guz__bosb) // bsw__pgta
                for tbv__msff, wio__atn in enumerate(guz__bosb):
                    if tbv__msff % ulg__fri == 0:
                        leyt__gxgsq = tbv__msff / ulg__fri
                        if leyt__gxgsq < bsw__pgta:
                            gpu_ranks.append(wio__atn)
            if stveo__ekp:
                kwvz__gtojz.bcast(stveo__ekp)
                raise stveo__ekp
            else:
                kwvz__gtojz.bcast(gpu_ranks)
    if jnakc__djw != 0:
        gpu_ranks = kwvz__gtojz.bcast(None)
        if isinstance(gpu_ranks, Exception):
            cskuf__geip = gpu_ranks
            raise cskuf__geip
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
    dprv__uqwfm = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        hsigy__yanvi = MPI.COMM_WORLD.Split(color=0 if dprv__uqwfm in
            gpu_ranks else MPI.UNDEFINED, key=dprv__uqwfm)
        if hsigy__yanvi != MPI.COMM_NULL:
            hvd.init(comm=hsigy__yanvi)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                fgg__xkw = tf.config.experimental.list_physical_devices('GPU')
                for whuf__ccug in fgg__xkw:
                    tf.config.experimental.set_memory_growth(whuf__ccug, True)
                tf.config.experimental.set_visible_devices(fgg__xkw[hvd.
                    local_rank()], 'GPU')
    else:
        if dprv__uqwfm == 0:
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
        rysap__rmi = 17
        kwvz__gtojz = MPI.COMM_WORLD
        cnx__pbhj = MPI.Get_processor_name()
        wwnuo__uvoh = get_host_ranks()[cnx__pbhj]
        assert_dl_initialized()
        if bodo.get_rank() == wwnuo__uvoh[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for jnakc__djw in wwnuo__uvoh[1:]:
                kwvz__gtojz.isend(1, dest=jnakc__djw, tag=rysap__rmi)
        else:
            while True:
                nbqfj__rdzkm = MPI.Status()
                oepv__iziq = kwvz__gtojz.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    nbqfj__rdzkm)
                if oepv__iziq:
                    assert nbqfj__rdzkm.source == wwnuo__uvoh[0]
                    assert nbqfj__rdzkm.tag == rysap__rmi
                    kwvz__gtojz.recv(source=0, tag=rysap__rmi)
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
