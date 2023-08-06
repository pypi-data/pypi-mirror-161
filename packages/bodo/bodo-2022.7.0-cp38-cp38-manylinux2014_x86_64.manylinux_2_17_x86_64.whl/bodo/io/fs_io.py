"""
S3 & Hadoop file system supports, and file system dependent calls
"""
import glob
import os
import warnings
from urllib.parse import urlparse
import llvmlite.binding as ll
import numba
import numpy as np
from fsspec.implementations.arrow import ArrowFile, ArrowFSWrapper, wrap_exceptions
from numba.core import types
from numba.extending import NativeValue, models, overload, register_model, unbox
import bodo
from bodo.io import csv_cpp
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.str_ext import unicode_to_utf8, unicode_to_utf8_and_len
from bodo.utils.typing import BodoError, BodoWarning, get_overload_constant_dict
from bodo.utils.utils import check_java_installation


def fsspec_arrowfswrapper__open(self, path, mode='rb', block_size=None, **
    kwargs):
    if mode == 'rb':
        try:
            uim__hfhl = self.fs.open_input_file(path)
        except:
            uim__hfhl = self.fs.open_input_stream(path)
    elif mode == 'wb':
        uim__hfhl = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, uim__hfhl, path, mode, block_size, **kwargs)


ArrowFSWrapper._open = wrap_exceptions(fsspec_arrowfswrapper__open)
_csv_write = types.ExternalFunction('csv_write', types.void(types.voidptr,
    types.voidptr, types.int64, types.int64, types.bool_, types.voidptr,
    types.voidptr))
ll.add_symbol('csv_write', csv_cpp.csv_write)
bodo_error_msg = """
    Some possible causes:
        (1) Incorrect path: Specified file/directory doesn't exist or is unreachable.
        (2) Missing credentials: You haven't provided S3 credentials, neither through 
            environment variables, nor through a local AWS setup 
            that makes the credentials available at ~/.aws/credentials.
        (3) Incorrect credentials: Your S3 credentials are incorrect or do not have
            the correct permissions.
        (4) Wrong bucket region is used. Set AWS_DEFAULT_REGION variable with correct bucket region.
    """


def get_proxy_uri_from_env_vars():
    return os.environ.get('http_proxy', None) or os.environ.get('https_proxy',
        None) or os.environ.get('HTTP_PROXY', None) or os.environ.get(
        'HTTPS_PROXY', None)


def get_s3_fs(region=None, storage_options=None):
    from pyarrow.fs import S3FileSystem
    fhqd__qafs = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    zmky__zoiz = False
    tcyi__bvco = get_proxy_uri_from_env_vars()
    if storage_options:
        zmky__zoiz = storage_options.get('anon', False)
    return S3FileSystem(anonymous=zmky__zoiz, region=region,
        endpoint_override=fhqd__qafs, proxy_options=tcyi__bvco)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    fhqd__qafs = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    zmky__zoiz = False
    tcyi__bvco = get_proxy_uri_from_env_vars()
    if storage_options:
        zmky__zoiz = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=fhqd__qafs,
        anonymous=zmky__zoiz, proxy_options=tcyi__bvco)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    ghnvi__syl = urlparse(path)
    if ghnvi__syl.scheme in ('abfs', 'abfss'):
        iwzyk__aagce = path
        if ghnvi__syl.port is None:
            kljbg__ydwl = 0
        else:
            kljbg__ydwl = ghnvi__syl.port
        unbt__alo = None
    else:
        iwzyk__aagce = ghnvi__syl.hostname
        kljbg__ydwl = ghnvi__syl.port
        unbt__alo = ghnvi__syl.username
    try:
        fs = HdFS(host=iwzyk__aagce, port=kljbg__ydwl, user=unbt__alo)
    except Exception as hhmr__yckoc:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            hhmr__yckoc))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        plz__hpu = fs.isdir(path)
    except gcsfs.utils.HttpError as hhmr__yckoc:
        raise BodoError(
            f'{hhmr__yckoc}. Make sure your google cloud credentials are set!')
    return plz__hpu


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [swn__nmmw.split('/')[-1] for swn__nmmw in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        ghnvi__syl = urlparse(path)
        mppzw__mhtee = (ghnvi__syl.netloc + ghnvi__syl.path).rstrip('/')
        oroel__qmmn = fs.get_file_info(mppzw__mhtee)
        if oroel__qmmn.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown
            ):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if (not oroel__qmmn.size and oroel__qmmn.type == pa_fs.FileType.
            Directory):
            return True
        return False
    except (FileNotFoundError, OSError) as hhmr__yckoc:
        raise
    except BodoError as rja__qtuy:
        raise
    except Exception as hhmr__yckoc:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(hhmr__yckoc).__name__}: {str(hhmr__yckoc)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    razs__fvh = None
    try:
        if s3_is_directory(fs, path):
            ghnvi__syl = urlparse(path)
            mppzw__mhtee = (ghnvi__syl.netloc + ghnvi__syl.path).rstrip('/')
            gwrz__wrr = pa_fs.FileSelector(mppzw__mhtee, recursive=False)
            ociaa__lmgwp = fs.get_file_info(gwrz__wrr)
            if ociaa__lmgwp and ociaa__lmgwp[0].path in [mppzw__mhtee,
                f'{mppzw__mhtee}/'] and int(ociaa__lmgwp[0].size or 0) == 0:
                ociaa__lmgwp = ociaa__lmgwp[1:]
            razs__fvh = [moz__zkpme.base_name for moz__zkpme in ociaa__lmgwp]
    except BodoError as rja__qtuy:
        raise
    except Exception as hhmr__yckoc:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(hhmr__yckoc).__name__}: {str(hhmr__yckoc)}
{bodo_error_msg}"""
            )
    return razs__fvh


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    ghnvi__syl = urlparse(path)
    rqqsx__jbop = ghnvi__syl.path
    try:
        hvlle__aud = HadoopFileSystem.from_uri(path)
    except Exception as hhmr__yckoc:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            hhmr__yckoc))
    rudnr__uve = hvlle__aud.get_file_info([rqqsx__jbop])
    if rudnr__uve[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not rudnr__uve[0].size and rudnr__uve[0].type == FileType.Directory:
        return hvlle__aud, True
    return hvlle__aud, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    razs__fvh = None
    hvlle__aud, plz__hpu = hdfs_is_directory(path)
    if plz__hpu:
        ghnvi__syl = urlparse(path)
        rqqsx__jbop = ghnvi__syl.path
        gwrz__wrr = FileSelector(rqqsx__jbop, recursive=True)
        try:
            ociaa__lmgwp = hvlle__aud.get_file_info(gwrz__wrr)
        except Exception as hhmr__yckoc:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(rqqsx__jbop, hhmr__yckoc))
        razs__fvh = [moz__zkpme.base_name for moz__zkpme in ociaa__lmgwp]
    return hvlle__aud, razs__fvh


def abfs_is_directory(path):
    hvlle__aud = get_hdfs_fs(path)
    try:
        rudnr__uve = hvlle__aud.info(path)
    except OSError as rja__qtuy:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if rudnr__uve['size'] == 0 and rudnr__uve['kind'].lower() == 'directory':
        return hvlle__aud, True
    return hvlle__aud, False


def abfs_list_dir_fnames(path):
    razs__fvh = None
    hvlle__aud, plz__hpu = abfs_is_directory(path)
    if plz__hpu:
        ghnvi__syl = urlparse(path)
        rqqsx__jbop = ghnvi__syl.path
        try:
            hsbyc__rwa = hvlle__aud.ls(rqqsx__jbop)
        except Exception as hhmr__yckoc:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(rqqsx__jbop, hhmr__yckoc))
        razs__fvh = [fname[fname.rindex('/') + 1:] for fname in hsbyc__rwa]
    return hvlle__aud, razs__fvh


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    ksw__cko = urlparse(path)
    fname = path
    fs = None
    xef__qoqqj = 'read_json' if ftype == 'json' else 'read_csv'
    obu__dgii = (
        f'pd.{xef__qoqqj}(): there is no {ftype} file in directory: {fname}')
    czg__elws = directory_of_files_common_filter
    if ksw__cko.scheme == 's3':
        qnvj__qnwf = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        ituw__mbr = s3_list_dir_fnames(fs, path)
        mppzw__mhtee = (ksw__cko.netloc + ksw__cko.path).rstrip('/')
        fname = mppzw__mhtee
        if ituw__mbr:
            ituw__mbr = [(mppzw__mhtee + '/' + swn__nmmw) for swn__nmmw in
                sorted(filter(czg__elws, ituw__mbr))]
            wjx__oufaq = [swn__nmmw for swn__nmmw in ituw__mbr if int(fs.
                get_file_info(swn__nmmw).size or 0) > 0]
            if len(wjx__oufaq) == 0:
                raise BodoError(obu__dgii)
            fname = wjx__oufaq[0]
        evs__yqp = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        euiaq__etfsy = fs._open(fname)
    elif ksw__cko.scheme == 'hdfs':
        qnvj__qnwf = True
        fs, ituw__mbr = hdfs_list_dir_fnames(path)
        evs__yqp = fs.get_file_info([ksw__cko.path])[0].size
        if ituw__mbr:
            path = path.rstrip('/')
            ituw__mbr = [(path + '/' + swn__nmmw) for swn__nmmw in sorted(
                filter(czg__elws, ituw__mbr))]
            wjx__oufaq = [swn__nmmw for swn__nmmw in ituw__mbr if fs.
                get_file_info([urlparse(swn__nmmw).path])[0].size > 0]
            if len(wjx__oufaq) == 0:
                raise BodoError(obu__dgii)
            fname = wjx__oufaq[0]
            fname = urlparse(fname).path
            evs__yqp = fs.get_file_info([fname])[0].size
        euiaq__etfsy = fs.open_input_file(fname)
    elif ksw__cko.scheme in ('abfs', 'abfss'):
        qnvj__qnwf = True
        fs, ituw__mbr = abfs_list_dir_fnames(path)
        evs__yqp = fs.info(fname)['size']
        if ituw__mbr:
            path = path.rstrip('/')
            ituw__mbr = [(path + '/' + swn__nmmw) for swn__nmmw in sorted(
                filter(czg__elws, ituw__mbr))]
            wjx__oufaq = [swn__nmmw for swn__nmmw in ituw__mbr if fs.info(
                swn__nmmw)['size'] > 0]
            if len(wjx__oufaq) == 0:
                raise BodoError(obu__dgii)
            fname = wjx__oufaq[0]
            evs__yqp = fs.info(fname)['size']
            fname = urlparse(fname).path
        euiaq__etfsy = fs.open(fname, 'rb')
    else:
        if ksw__cko.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {ksw__cko.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        qnvj__qnwf = False
        if os.path.isdir(path):
            hsbyc__rwa = filter(czg__elws, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            wjx__oufaq = [swn__nmmw for swn__nmmw in sorted(hsbyc__rwa) if 
                os.path.getsize(swn__nmmw) > 0]
            if len(wjx__oufaq) == 0:
                raise BodoError(obu__dgii)
            fname = wjx__oufaq[0]
        evs__yqp = os.path.getsize(fname)
        euiaq__etfsy = fname
    return qnvj__qnwf, euiaq__etfsy, evs__yqp, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    jyba__mmj = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            jdcbo__wszin, jvrro__hoo = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = jdcbo__wszin.region
        except Exception as hhmr__yckoc:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{hhmr__yckoc}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = jyba__mmj.bcast(bucket_loc)
    return bucket_loc


@numba.njit()
def get_s3_bucket_region_njit(s3_filepath, parallel):
    with numba.objmode(bucket_loc='unicode_type'):
        bucket_loc = ''
        if isinstance(s3_filepath, list):
            s3_filepath = s3_filepath[0]
        if s3_filepath.startswith('s3://'):
            bucket_loc = get_s3_bucket_region(s3_filepath, parallel)
    return bucket_loc


def csv_write(path_or_buf, D, filename_prefix, is_parallel=False):
    return None


@overload(csv_write, no_unliteral=True)
def csv_write_overload(path_or_buf, D, filename_prefix, is_parallel=False):

    def impl(path_or_buf, D, filename_prefix, is_parallel=False):
        zvdt__bhsu = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        glntr__lyqxr, linxv__ylt = unicode_to_utf8_and_len(D)
        kne__xgaf = 0
        if is_parallel:
            kne__xgaf = bodo.libs.distributed_api.dist_exscan(linxv__ylt,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), glntr__lyqxr, kne__xgaf,
            linxv__ylt, is_parallel, unicode_to_utf8(zvdt__bhsu),
            unicode_to_utf8(filename_prefix))
        bodo.utils.utils.check_and_propagate_cpp_exception()
    return impl


class StorageOptionsDictType(types.Opaque):

    def __init__(self):
        super(StorageOptionsDictType, self).__init__(name=
            'StorageOptionsDictType')


storage_options_dict_type = StorageOptionsDictType()
types.storage_options_dict_type = storage_options_dict_type
register_model(StorageOptionsDictType)(models.OpaqueModel)


@unbox(StorageOptionsDictType)
def unbox_storage_options_dict_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


def get_storage_options_pyobject(storage_options):
    pass


@overload(get_storage_options_pyobject, no_unliteral=True)
def overload_get_storage_options_pyobject(storage_options):
    bqlq__fqpto = get_overload_constant_dict(storage_options)
    oep__lxbnf = 'def impl(storage_options):\n'
    oep__lxbnf += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    oep__lxbnf += f'    storage_options_py = {str(bqlq__fqpto)}\n'
    oep__lxbnf += '  return storage_options_py\n'
    kja__qiz = {}
    exec(oep__lxbnf, globals(), kja__qiz)
    return kja__qiz['impl']
