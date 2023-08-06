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
            knbj__hivvz = self.fs.open_input_file(path)
        except:
            knbj__hivvz = self.fs.open_input_stream(path)
    elif mode == 'wb':
        knbj__hivvz = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, knbj__hivvz, path, mode, block_size, **kwargs)


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
    ivgs__laxro = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    lvfpc__nrr = False
    jbfhe__pmgh = get_proxy_uri_from_env_vars()
    if storage_options:
        lvfpc__nrr = storage_options.get('anon', False)
    return S3FileSystem(anonymous=lvfpc__nrr, region=region,
        endpoint_override=ivgs__laxro, proxy_options=jbfhe__pmgh)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    ivgs__laxro = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    lvfpc__nrr = False
    jbfhe__pmgh = get_proxy_uri_from_env_vars()
    if storage_options:
        lvfpc__nrr = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=ivgs__laxro,
        anonymous=lvfpc__nrr, proxy_options=jbfhe__pmgh)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    tqqh__tcvjh = urlparse(path)
    if tqqh__tcvjh.scheme in ('abfs', 'abfss'):
        wbty__qcr = path
        if tqqh__tcvjh.port is None:
            ixx__pzhv = 0
        else:
            ixx__pzhv = tqqh__tcvjh.port
        nekcq__ndkzu = None
    else:
        wbty__qcr = tqqh__tcvjh.hostname
        ixx__pzhv = tqqh__tcvjh.port
        nekcq__ndkzu = tqqh__tcvjh.username
    try:
        fs = HdFS(host=wbty__qcr, port=ixx__pzhv, user=nekcq__ndkzu)
    except Exception as tpo__rnz:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            tpo__rnz))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        radj__aevmr = fs.isdir(path)
    except gcsfs.utils.HttpError as tpo__rnz:
        raise BodoError(
            f'{tpo__rnz}. Make sure your google cloud credentials are set!')
    return radj__aevmr


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [bmbk__uvwl.split('/')[-1] for bmbk__uvwl in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        tqqh__tcvjh = urlparse(path)
        mgyb__ylxv = (tqqh__tcvjh.netloc + tqqh__tcvjh.path).rstrip('/')
        oawe__vzlvk = fs.get_file_info(mgyb__ylxv)
        if oawe__vzlvk.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown
            ):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if (not oawe__vzlvk.size and oawe__vzlvk.type == pa_fs.FileType.
            Directory):
            return True
        return False
    except (FileNotFoundError, OSError) as tpo__rnz:
        raise
    except BodoError as cbq__dahhl:
        raise
    except Exception as tpo__rnz:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(tpo__rnz).__name__}: {str(tpo__rnz)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    zwu__ljycl = None
    try:
        if s3_is_directory(fs, path):
            tqqh__tcvjh = urlparse(path)
            mgyb__ylxv = (tqqh__tcvjh.netloc + tqqh__tcvjh.path).rstrip('/')
            tqd__kcy = pa_fs.FileSelector(mgyb__ylxv, recursive=False)
            xtwf__ruxnw = fs.get_file_info(tqd__kcy)
            if xtwf__ruxnw and xtwf__ruxnw[0].path in [mgyb__ylxv,
                f'{mgyb__ylxv}/'] and int(xtwf__ruxnw[0].size or 0) == 0:
                xtwf__ruxnw = xtwf__ruxnw[1:]
            zwu__ljycl = [frqev__kjwy.base_name for frqev__kjwy in xtwf__ruxnw]
    except BodoError as cbq__dahhl:
        raise
    except Exception as tpo__rnz:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(tpo__rnz).__name__}: {str(tpo__rnz)}
{bodo_error_msg}"""
            )
    return zwu__ljycl


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    tqqh__tcvjh = urlparse(path)
    oyl__hvq = tqqh__tcvjh.path
    try:
        dyvkt__sxyc = HadoopFileSystem.from_uri(path)
    except Exception as tpo__rnz:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            tpo__rnz))
    duk__tbn = dyvkt__sxyc.get_file_info([oyl__hvq])
    if duk__tbn[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not duk__tbn[0].size and duk__tbn[0].type == FileType.Directory:
        return dyvkt__sxyc, True
    return dyvkt__sxyc, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    zwu__ljycl = None
    dyvkt__sxyc, radj__aevmr = hdfs_is_directory(path)
    if radj__aevmr:
        tqqh__tcvjh = urlparse(path)
        oyl__hvq = tqqh__tcvjh.path
        tqd__kcy = FileSelector(oyl__hvq, recursive=True)
        try:
            xtwf__ruxnw = dyvkt__sxyc.get_file_info(tqd__kcy)
        except Exception as tpo__rnz:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(oyl__hvq, tpo__rnz))
        zwu__ljycl = [frqev__kjwy.base_name for frqev__kjwy in xtwf__ruxnw]
    return dyvkt__sxyc, zwu__ljycl


def abfs_is_directory(path):
    dyvkt__sxyc = get_hdfs_fs(path)
    try:
        duk__tbn = dyvkt__sxyc.info(path)
    except OSError as cbq__dahhl:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if duk__tbn['size'] == 0 and duk__tbn['kind'].lower() == 'directory':
        return dyvkt__sxyc, True
    return dyvkt__sxyc, False


def abfs_list_dir_fnames(path):
    zwu__ljycl = None
    dyvkt__sxyc, radj__aevmr = abfs_is_directory(path)
    if radj__aevmr:
        tqqh__tcvjh = urlparse(path)
        oyl__hvq = tqqh__tcvjh.path
        try:
            chiae__rovh = dyvkt__sxyc.ls(oyl__hvq)
        except Exception as tpo__rnz:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(oyl__hvq, tpo__rnz))
        zwu__ljycl = [fname[fname.rindex('/') + 1:] for fname in chiae__rovh]
    return dyvkt__sxyc, zwu__ljycl


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    ngq__muk = urlparse(path)
    fname = path
    fs = None
    use__vfee = 'read_json' if ftype == 'json' else 'read_csv'
    gyu__gml = (
        f'pd.{use__vfee}(): there is no {ftype} file in directory: {fname}')
    olx__zxl = directory_of_files_common_filter
    if ngq__muk.scheme == 's3':
        dowfc__vkl = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        skmea__big = s3_list_dir_fnames(fs, path)
        mgyb__ylxv = (ngq__muk.netloc + ngq__muk.path).rstrip('/')
        fname = mgyb__ylxv
        if skmea__big:
            skmea__big = [(mgyb__ylxv + '/' + bmbk__uvwl) for bmbk__uvwl in
                sorted(filter(olx__zxl, skmea__big))]
            kndky__ordu = [bmbk__uvwl for bmbk__uvwl in skmea__big if int(
                fs.get_file_info(bmbk__uvwl).size or 0) > 0]
            if len(kndky__ordu) == 0:
                raise BodoError(gyu__gml)
            fname = kndky__ordu[0]
        jwyxl__rjaw = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        hsspx__jaw = fs._open(fname)
    elif ngq__muk.scheme == 'hdfs':
        dowfc__vkl = True
        fs, skmea__big = hdfs_list_dir_fnames(path)
        jwyxl__rjaw = fs.get_file_info([ngq__muk.path])[0].size
        if skmea__big:
            path = path.rstrip('/')
            skmea__big = [(path + '/' + bmbk__uvwl) for bmbk__uvwl in
                sorted(filter(olx__zxl, skmea__big))]
            kndky__ordu = [bmbk__uvwl for bmbk__uvwl in skmea__big if fs.
                get_file_info([urlparse(bmbk__uvwl).path])[0].size > 0]
            if len(kndky__ordu) == 0:
                raise BodoError(gyu__gml)
            fname = kndky__ordu[0]
            fname = urlparse(fname).path
            jwyxl__rjaw = fs.get_file_info([fname])[0].size
        hsspx__jaw = fs.open_input_file(fname)
    elif ngq__muk.scheme in ('abfs', 'abfss'):
        dowfc__vkl = True
        fs, skmea__big = abfs_list_dir_fnames(path)
        jwyxl__rjaw = fs.info(fname)['size']
        if skmea__big:
            path = path.rstrip('/')
            skmea__big = [(path + '/' + bmbk__uvwl) for bmbk__uvwl in
                sorted(filter(olx__zxl, skmea__big))]
            kndky__ordu = [bmbk__uvwl for bmbk__uvwl in skmea__big if fs.
                info(bmbk__uvwl)['size'] > 0]
            if len(kndky__ordu) == 0:
                raise BodoError(gyu__gml)
            fname = kndky__ordu[0]
            jwyxl__rjaw = fs.info(fname)['size']
            fname = urlparse(fname).path
        hsspx__jaw = fs.open(fname, 'rb')
    else:
        if ngq__muk.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {ngq__muk.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        dowfc__vkl = False
        if os.path.isdir(path):
            chiae__rovh = filter(olx__zxl, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            kndky__ordu = [bmbk__uvwl for bmbk__uvwl in sorted(chiae__rovh) if
                os.path.getsize(bmbk__uvwl) > 0]
            if len(kndky__ordu) == 0:
                raise BodoError(gyu__gml)
            fname = kndky__ordu[0]
        jwyxl__rjaw = os.path.getsize(fname)
        hsspx__jaw = fname
    return dowfc__vkl, hsspx__jaw, jwyxl__rjaw, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    gcbw__yuim = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            hyrbt__leaok, slsez__ttryl = pa_fs.S3FileSystem.from_uri(
                s3_filepath)
            bucket_loc = hyrbt__leaok.region
        except Exception as tpo__rnz:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{tpo__rnz}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = gcbw__yuim.bcast(bucket_loc)
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
        lqhya__nspmt = get_s3_bucket_region_njit(path_or_buf, parallel=
            is_parallel)
        ozp__gzgg, qtafs__yjnf = unicode_to_utf8_and_len(D)
        ibik__izzcu = 0
        if is_parallel:
            ibik__izzcu = bodo.libs.distributed_api.dist_exscan(qtafs__yjnf,
                np.int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), ozp__gzgg, ibik__izzcu,
            qtafs__yjnf, is_parallel, unicode_to_utf8(lqhya__nspmt),
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
    ska__ksqf = get_overload_constant_dict(storage_options)
    qdn__ggnf = 'def impl(storage_options):\n'
    qdn__ggnf += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    qdn__ggnf += f'    storage_options_py = {str(ska__ksqf)}\n'
    qdn__ggnf += '  return storage_options_py\n'
    yuqf__rko = {}
    exec(qdn__ggnf, globals(), yuqf__rko)
    return yuqf__rko['impl']
