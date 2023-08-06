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
    ana__zia = MPI.COMM_WORLD
    ahg__grn = ana__zia.Get_rank()
    kdjtx__yia = get_host_ranks()
    qamx__xfezm = get_nodes_first_ranks()
    if ahg__grn in qamx__xfezm:
        try:
            wenv__smeuo = get_num_gpus(framework)
        except Exception as aowvu__ncof:
            wenv__smeuo = aowvu__ncof
        qhiol__igj = create_subcomm_mpi4py(qamx__xfezm)
        oplhk__ipmh = qhiol__igj.gather(wenv__smeuo)
        if ahg__grn == 0:
            gpu_ranks = []
            cxfp__hbmgs = None
            for honx__tqa, woiu__txg in enumerate(kdjtx__yia.values()):
                hyw__tnb = oplhk__ipmh[honx__tqa]
                if isinstance(hyw__tnb, Exception):
                    cxfp__hbmgs = hyw__tnb
                    break
                if hyw__tnb == 0:
                    continue
                geu__kgw = len(woiu__txg) // hyw__tnb
                for meezd__qkhl, dvwpj__nfyem in enumerate(woiu__txg):
                    if meezd__qkhl % geu__kgw == 0:
                        urng__dxpe = meezd__qkhl / geu__kgw
                        if urng__dxpe < hyw__tnb:
                            gpu_ranks.append(dvwpj__nfyem)
            if cxfp__hbmgs:
                ana__zia.bcast(cxfp__hbmgs)
                raise cxfp__hbmgs
            else:
                ana__zia.bcast(gpu_ranks)
    if ahg__grn != 0:
        gpu_ranks = ana__zia.bcast(None)
        if isinstance(gpu_ranks, Exception):
            aowvu__ncof = gpu_ranks
            raise aowvu__ncof
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
    xisi__xavgh = MPI.COMM_WORLD.rank
    if len(gpu_ranks) > 0:
        qhiol__igj = MPI.COMM_WORLD.Split(color=0 if xisi__xavgh in
            gpu_ranks else MPI.UNDEFINED, key=xisi__xavgh)
        if qhiol__igj != MPI.COMM_NULL:
            hvd.init(comm=qhiol__igj)
            if framework == 'torch':
                torch.cuda.set_device(hvd.local_rank())
            elif framework == 'tensorflow':
                aut__bsb = tf.config.experimental.list_physical_devices('GPU')
                for ysku__twmpl in aut__bsb:
                    tf.config.experimental.set_memory_growth(ysku__twmpl, True)
                tf.config.experimental.set_visible_devices(aut__bsb[hvd.
                    local_rank()], 'GPU')
    else:
        if xisi__xavgh == 0:
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
        gldvp__ywy = 17
        ana__zia = MPI.COMM_WORLD
        kkqy__rnhsv = MPI.Get_processor_name()
        nnprh__mqvih = get_host_ranks()[kkqy__rnhsv]
        assert_dl_initialized()
        if bodo.get_rank() == nnprh__mqvih[0]:
            assert bodo.get_rank() in dl_status.gpu_ranks
            for ahg__grn in nnprh__mqvih[1:]:
                ana__zia.isend(1, dest=ahg__grn, tag=gldvp__ywy)
        else:
            while True:
                yrclo__tqfif = MPI.Status()
                ptz__xev = ana__zia.Iprobe(MPI.ANY_SOURCE, MPI.ANY_TAG,
                    yrclo__tqfif)
                if ptz__xev:
                    assert yrclo__tqfif.source == nnprh__mqvih[0]
                    assert yrclo__tqfif.tag == gldvp__ywy
                    ana__zia.recv(source=0, tag=gldvp__ywy)
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
