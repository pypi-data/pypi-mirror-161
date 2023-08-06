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
            ugu__tyii = self.fs.open_input_file(path)
        except:
            ugu__tyii = self.fs.open_input_stream(path)
    elif mode == 'wb':
        ugu__tyii = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, ugu__tyii, path, mode, block_size, **kwargs)


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
    kvyq__bklk = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    qkm__nytl = False
    ewlk__zlhs = get_proxy_uri_from_env_vars()
    if storage_options:
        qkm__nytl = storage_options.get('anon', False)
    return S3FileSystem(anonymous=qkm__nytl, region=region,
        endpoint_override=kvyq__bklk, proxy_options=ewlk__zlhs)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    kvyq__bklk = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    qkm__nytl = False
    ewlk__zlhs = get_proxy_uri_from_env_vars()
    if storage_options:
        qkm__nytl = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=kvyq__bklk,
        anonymous=qkm__nytl, proxy_options=ewlk__zlhs)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    merg__ktmk = urlparse(path)
    if merg__ktmk.scheme in ('abfs', 'abfss'):
        kyph__pxit = path
        if merg__ktmk.port is None:
            ouixz__gcf = 0
        else:
            ouixz__gcf = merg__ktmk.port
        vuzf__kmhbn = None
    else:
        kyph__pxit = merg__ktmk.hostname
        ouixz__gcf = merg__ktmk.port
        vuzf__kmhbn = merg__ktmk.username
    try:
        fs = HdFS(host=kyph__pxit, port=ouixz__gcf, user=vuzf__kmhbn)
    except Exception as mrzz__tcck:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            mrzz__tcck))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        kufy__gahw = fs.isdir(path)
    except gcsfs.utils.HttpError as mrzz__tcck:
        raise BodoError(
            f'{mrzz__tcck}. Make sure your google cloud credentials are set!')
    return kufy__gahw


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [hoswb__hcjv.split('/')[-1] for hoswb__hcjv in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        merg__ktmk = urlparse(path)
        ahw__cnayv = (merg__ktmk.netloc + merg__ktmk.path).rstrip('/')
        txn__mqlp = fs.get_file_info(ahw__cnayv)
        if txn__mqlp.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if not txn__mqlp.size and txn__mqlp.type == pa_fs.FileType.Directory:
            return True
        return False
    except (FileNotFoundError, OSError) as mrzz__tcck:
        raise
    except BodoError as uedw__adqyj:
        raise
    except Exception as mrzz__tcck:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(mrzz__tcck).__name__}: {str(mrzz__tcck)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    hxs__xrs = None
    try:
        if s3_is_directory(fs, path):
            merg__ktmk = urlparse(path)
            ahw__cnayv = (merg__ktmk.netloc + merg__ktmk.path).rstrip('/')
            qvkrf__hngk = pa_fs.FileSelector(ahw__cnayv, recursive=False)
            cojc__lbvo = fs.get_file_info(qvkrf__hngk)
            if cojc__lbvo and cojc__lbvo[0].path in [ahw__cnayv,
                f'{ahw__cnayv}/'] and int(cojc__lbvo[0].size or 0) == 0:
                cojc__lbvo = cojc__lbvo[1:]
            hxs__xrs = [hhz__uvsk.base_name for hhz__uvsk in cojc__lbvo]
    except BodoError as uedw__adqyj:
        raise
    except Exception as mrzz__tcck:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(mrzz__tcck).__name__}: {str(mrzz__tcck)}
{bodo_error_msg}"""
            )
    return hxs__xrs


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    merg__ktmk = urlparse(path)
    borc__wworn = merg__ktmk.path
    try:
        eyp__qhe = HadoopFileSystem.from_uri(path)
    except Exception as mrzz__tcck:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            mrzz__tcck))
    wmoli__eghsb = eyp__qhe.get_file_info([borc__wworn])
    if wmoli__eghsb[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not wmoli__eghsb[0].size and wmoli__eghsb[0].type == FileType.Directory:
        return eyp__qhe, True
    return eyp__qhe, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    hxs__xrs = None
    eyp__qhe, kufy__gahw = hdfs_is_directory(path)
    if kufy__gahw:
        merg__ktmk = urlparse(path)
        borc__wworn = merg__ktmk.path
        qvkrf__hngk = FileSelector(borc__wworn, recursive=True)
        try:
            cojc__lbvo = eyp__qhe.get_file_info(qvkrf__hngk)
        except Exception as mrzz__tcck:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(borc__wworn, mrzz__tcck))
        hxs__xrs = [hhz__uvsk.base_name for hhz__uvsk in cojc__lbvo]
    return eyp__qhe, hxs__xrs


def abfs_is_directory(path):
    eyp__qhe = get_hdfs_fs(path)
    try:
        wmoli__eghsb = eyp__qhe.info(path)
    except OSError as uedw__adqyj:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if wmoli__eghsb['size'] == 0 and wmoli__eghsb['kind'].lower(
        ) == 'directory':
        return eyp__qhe, True
    return eyp__qhe, False


def abfs_list_dir_fnames(path):
    hxs__xrs = None
    eyp__qhe, kufy__gahw = abfs_is_directory(path)
    if kufy__gahw:
        merg__ktmk = urlparse(path)
        borc__wworn = merg__ktmk.path
        try:
            jkjdc__dhhb = eyp__qhe.ls(borc__wworn)
        except Exception as mrzz__tcck:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(borc__wworn, mrzz__tcck))
        hxs__xrs = [fname[fname.rindex('/') + 1:] for fname in jkjdc__dhhb]
    return eyp__qhe, hxs__xrs


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    zdt__gyn = urlparse(path)
    fname = path
    fs = None
    nrepo__bxy = 'read_json' if ftype == 'json' else 'read_csv'
    weeoo__omjd = (
        f'pd.{nrepo__bxy}(): there is no {ftype} file in directory: {fname}')
    ldwfy__dgy = directory_of_files_common_filter
    if zdt__gyn.scheme == 's3':
        hfzo__vdjr = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        kcwew__duune = s3_list_dir_fnames(fs, path)
        ahw__cnayv = (zdt__gyn.netloc + zdt__gyn.path).rstrip('/')
        fname = ahw__cnayv
        if kcwew__duune:
            kcwew__duune = [(ahw__cnayv + '/' + hoswb__hcjv) for
                hoswb__hcjv in sorted(filter(ldwfy__dgy, kcwew__duune))]
            wnjxj__laky = [hoswb__hcjv for hoswb__hcjv in kcwew__duune if 
                int(fs.get_file_info(hoswb__hcjv).size or 0) > 0]
            if len(wnjxj__laky) == 0:
                raise BodoError(weeoo__omjd)
            fname = wnjxj__laky[0]
        isgxu__ihjki = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        emqrq__sapc = fs._open(fname)
    elif zdt__gyn.scheme == 'hdfs':
        hfzo__vdjr = True
        fs, kcwew__duune = hdfs_list_dir_fnames(path)
        isgxu__ihjki = fs.get_file_info([zdt__gyn.path])[0].size
        if kcwew__duune:
            path = path.rstrip('/')
            kcwew__duune = [(path + '/' + hoswb__hcjv) for hoswb__hcjv in
                sorted(filter(ldwfy__dgy, kcwew__duune))]
            wnjxj__laky = [hoswb__hcjv for hoswb__hcjv in kcwew__duune if 
                fs.get_file_info([urlparse(hoswb__hcjv).path])[0].size > 0]
            if len(wnjxj__laky) == 0:
                raise BodoError(weeoo__omjd)
            fname = wnjxj__laky[0]
            fname = urlparse(fname).path
            isgxu__ihjki = fs.get_file_info([fname])[0].size
        emqrq__sapc = fs.open_input_file(fname)
    elif zdt__gyn.scheme in ('abfs', 'abfss'):
        hfzo__vdjr = True
        fs, kcwew__duune = abfs_list_dir_fnames(path)
        isgxu__ihjki = fs.info(fname)['size']
        if kcwew__duune:
            path = path.rstrip('/')
            kcwew__duune = [(path + '/' + hoswb__hcjv) for hoswb__hcjv in
                sorted(filter(ldwfy__dgy, kcwew__duune))]
            wnjxj__laky = [hoswb__hcjv for hoswb__hcjv in kcwew__duune if 
                fs.info(hoswb__hcjv)['size'] > 0]
            if len(wnjxj__laky) == 0:
                raise BodoError(weeoo__omjd)
            fname = wnjxj__laky[0]
            isgxu__ihjki = fs.info(fname)['size']
            fname = urlparse(fname).path
        emqrq__sapc = fs.open(fname, 'rb')
    else:
        if zdt__gyn.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {zdt__gyn.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        hfzo__vdjr = False
        if os.path.isdir(path):
            jkjdc__dhhb = filter(ldwfy__dgy, glob.glob(os.path.join(os.path
                .abspath(path), '*')))
            wnjxj__laky = [hoswb__hcjv for hoswb__hcjv in sorted(
                jkjdc__dhhb) if os.path.getsize(hoswb__hcjv) > 0]
            if len(wnjxj__laky) == 0:
                raise BodoError(weeoo__omjd)
            fname = wnjxj__laky[0]
        isgxu__ihjki = os.path.getsize(fname)
        emqrq__sapc = fname
    return hfzo__vdjr, emqrq__sapc, isgxu__ihjki, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    gdthn__vlko = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            dmh__fsxew, gyu__qcoo = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = dmh__fsxew.region
        except Exception as mrzz__tcck:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{mrzz__tcck}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = gdthn__vlko.bcast(bucket_loc)
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
        agxtx__riku = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        sjrci__qfcy, uutzk__hnh = unicode_to_utf8_and_len(D)
        vuoc__ihj = 0
        if is_parallel:
            vuoc__ihj = bodo.libs.distributed_api.dist_exscan(uutzk__hnh,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), sjrci__qfcy, vuoc__ihj,
            uutzk__hnh, is_parallel, unicode_to_utf8(agxtx__riku),
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
    uwqqp__auegm = get_overload_constant_dict(storage_options)
    lql__cla = 'def impl(storage_options):\n'
    lql__cla += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    lql__cla += f'    storage_options_py = {str(uwqqp__auegm)}\n'
    lql__cla += '  return storage_options_py\n'
    tjgm__jqk = {}
    exec(lql__cla, globals(), tjgm__jqk)
    return tjgm__jqk['impl']
