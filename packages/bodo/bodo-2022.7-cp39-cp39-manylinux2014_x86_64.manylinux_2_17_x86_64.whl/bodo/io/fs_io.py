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
            gieo__syw = self.fs.open_input_file(path)
        except:
            gieo__syw = self.fs.open_input_stream(path)
    elif mode == 'wb':
        gieo__syw = self.fs.open_output_stream(path)
    else:
        raise ValueError(f'unsupported mode for Arrow filesystem: {mode!r}')
    return ArrowFile(self, gieo__syw, path, mode, block_size, **kwargs)


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
    cxn__fjw = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    lwn__cyx = False
    pkjkd__ffm = get_proxy_uri_from_env_vars()
    if storage_options:
        lwn__cyx = storage_options.get('anon', False)
    return S3FileSystem(anonymous=lwn__cyx, region=region,
        endpoint_override=cxn__fjw, proxy_options=pkjkd__ffm)


def get_s3_subtree_fs(bucket_name, region=None, storage_options=None):
    from pyarrow._fs import SubTreeFileSystem
    from pyarrow._s3fs import S3FileSystem
    cxn__fjw = os.environ.get('AWS_S3_ENDPOINT', None)
    if not region:
        region = os.environ.get('AWS_DEFAULT_REGION', None)
    lwn__cyx = False
    pkjkd__ffm = get_proxy_uri_from_env_vars()
    if storage_options:
        lwn__cyx = storage_options.get('anon', False)
    fs = S3FileSystem(region=region, endpoint_override=cxn__fjw, anonymous=
        lwn__cyx, proxy_options=pkjkd__ffm)
    return SubTreeFileSystem(bucket_name, fs)


def get_s3_fs_from_path(path, parallel=False, storage_options=None):
    region = get_s3_bucket_region_njit(path, parallel=parallel)
    if region == '':
        region = None
    return get_s3_fs(region, storage_options)


def get_hdfs_fs(path):
    from pyarrow.fs import HadoopFileSystem as HdFS
    bcl__cbxwq = urlparse(path)
    if bcl__cbxwq.scheme in ('abfs', 'abfss'):
        xxofa__ldvn = path
        if bcl__cbxwq.port is None:
            qlwyk__vqfob = 0
        else:
            qlwyk__vqfob = bcl__cbxwq.port
        gtpaa__puk = None
    else:
        xxofa__ldvn = bcl__cbxwq.hostname
        qlwyk__vqfob = bcl__cbxwq.port
        gtpaa__puk = bcl__cbxwq.username
    try:
        fs = HdFS(host=xxofa__ldvn, port=qlwyk__vqfob, user=gtpaa__puk)
    except Exception as ladcd__fjeo:
        raise BodoError('Hadoop file system cannot be created: {}'.format(
            ladcd__fjeo))
    return fs


def gcs_is_directory(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    try:
        egsrg__gigho = fs.isdir(path)
    except gcsfs.utils.HttpError as ladcd__fjeo:
        raise BodoError(
            f'{ladcd__fjeo}. Make sure your google cloud credentials are set!')
    return egsrg__gigho


def gcs_list_dir_fnames(path):
    import gcsfs
    fs = gcsfs.GCSFileSystem(token=None)
    return [jycum__kcyu.split('/')[-1] for jycum__kcyu in fs.ls(path)]


def s3_is_directory(fs, path):
    from pyarrow import fs as pa_fs
    try:
        bcl__cbxwq = urlparse(path)
        rmkd__inli = (bcl__cbxwq.netloc + bcl__cbxwq.path).rstrip('/')
        rciec__wjjv = fs.get_file_info(rmkd__inli)
        if rciec__wjjv.type in (pa_fs.FileType.NotFound, pa_fs.FileType.Unknown
            ):
            raise FileNotFoundError('{} is a non-existing or unreachable file'
                .format(path))
        if (not rciec__wjjv.size and rciec__wjjv.type == pa_fs.FileType.
            Directory):
            return True
        return False
    except (FileNotFoundError, OSError) as ladcd__fjeo:
        raise
    except BodoError as tcyi__vub:
        raise
    except Exception as ladcd__fjeo:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(ladcd__fjeo).__name__}: {str(ladcd__fjeo)}
{bodo_error_msg}"""
            )


def s3_list_dir_fnames(fs, path):
    from pyarrow import fs as pa_fs
    lxo__ouqi = None
    try:
        if s3_is_directory(fs, path):
            bcl__cbxwq = urlparse(path)
            rmkd__inli = (bcl__cbxwq.netloc + bcl__cbxwq.path).rstrip('/')
            tfzsg__mrni = pa_fs.FileSelector(rmkd__inli, recursive=False)
            dbgvc__vak = fs.get_file_info(tfzsg__mrni)
            if dbgvc__vak and dbgvc__vak[0].path in [rmkd__inli,
                f'{rmkd__inli}/'] and int(dbgvc__vak[0].size or 0) == 0:
                dbgvc__vak = dbgvc__vak[1:]
            lxo__ouqi = [nli__qqq.base_name for nli__qqq in dbgvc__vak]
    except BodoError as tcyi__vub:
        raise
    except Exception as ladcd__fjeo:
        raise BodoError(
            f"""error from pyarrow S3FileSystem: {type(ladcd__fjeo).__name__}: {str(ladcd__fjeo)}
{bodo_error_msg}"""
            )
    return lxo__ouqi


def hdfs_is_directory(path):
    from pyarrow.fs import FileType, HadoopFileSystem
    check_java_installation(path)
    bcl__cbxwq = urlparse(path)
    kwm__grsw = bcl__cbxwq.path
    try:
        yzzty__goah = HadoopFileSystem.from_uri(path)
    except Exception as ladcd__fjeo:
        raise BodoError(' Hadoop file system cannot be created: {}'.format(
            ladcd__fjeo))
    klsl__ehp = yzzty__goah.get_file_info([kwm__grsw])
    if klsl__ehp[0].type in (FileType.NotFound, FileType.Unknown):
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if not klsl__ehp[0].size and klsl__ehp[0].type == FileType.Directory:
        return yzzty__goah, True
    return yzzty__goah, False


def hdfs_list_dir_fnames(path):
    from pyarrow.fs import FileSelector
    lxo__ouqi = None
    yzzty__goah, egsrg__gigho = hdfs_is_directory(path)
    if egsrg__gigho:
        bcl__cbxwq = urlparse(path)
        kwm__grsw = bcl__cbxwq.path
        tfzsg__mrni = FileSelector(kwm__grsw, recursive=True)
        try:
            dbgvc__vak = yzzty__goah.get_file_info(tfzsg__mrni)
        except Exception as ladcd__fjeo:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(kwm__grsw, ladcd__fjeo))
        lxo__ouqi = [nli__qqq.base_name for nli__qqq in dbgvc__vak]
    return yzzty__goah, lxo__ouqi


def abfs_is_directory(path):
    yzzty__goah = get_hdfs_fs(path)
    try:
        klsl__ehp = yzzty__goah.info(path)
    except OSError as tcyi__vub:
        raise BodoError('{} is a non-existing or unreachable file'.format(path)
            )
    if klsl__ehp['size'] == 0 and klsl__ehp['kind'].lower() == 'directory':
        return yzzty__goah, True
    return yzzty__goah, False


def abfs_list_dir_fnames(path):
    lxo__ouqi = None
    yzzty__goah, egsrg__gigho = abfs_is_directory(path)
    if egsrg__gigho:
        bcl__cbxwq = urlparse(path)
        kwm__grsw = bcl__cbxwq.path
        try:
            aqz__locfx = yzzty__goah.ls(kwm__grsw)
        except Exception as ladcd__fjeo:
            raise BodoError('Exception on getting directory info of {}: {}'
                .format(kwm__grsw, ladcd__fjeo))
        lxo__ouqi = [fname[fname.rindex('/') + 1:] for fname in aqz__locfx]
    return yzzty__goah, lxo__ouqi


def directory_of_files_common_filter(fname):
    return not (fname.endswith('.crc') or fname.endswith('_$folder$') or
        fname.startswith('.') or fname.startswith('_') and fname !=
        '_delta_log')


def find_file_name_or_handler(path, ftype, storage_options=None):
    from urllib.parse import urlparse
    zao__xscji = urlparse(path)
    fname = path
    fs = None
    kako__tclgz = 'read_json' if ftype == 'json' else 'read_csv'
    sgb__rpcw = (
        f'pd.{kako__tclgz}(): there is no {ftype} file in directory: {fname}')
    eao__bhwvn = directory_of_files_common_filter
    if zao__xscji.scheme == 's3':
        jetj__jym = True
        fs = get_s3_fs_from_path(path, storage_options=storage_options)
        mna__oopan = s3_list_dir_fnames(fs, path)
        rmkd__inli = (zao__xscji.netloc + zao__xscji.path).rstrip('/')
        fname = rmkd__inli
        if mna__oopan:
            mna__oopan = [(rmkd__inli + '/' + jycum__kcyu) for jycum__kcyu in
                sorted(filter(eao__bhwvn, mna__oopan))]
            ntrz__tiri = [jycum__kcyu for jycum__kcyu in mna__oopan if int(
                fs.get_file_info(jycum__kcyu).size or 0) > 0]
            if len(ntrz__tiri) == 0:
                raise BodoError(sgb__rpcw)
            fname = ntrz__tiri[0]
        slo__hhq = int(fs.get_file_info(fname).size or 0)
        fs = ArrowFSWrapper(fs)
        zrjk__nvgad = fs._open(fname)
    elif zao__xscji.scheme == 'hdfs':
        jetj__jym = True
        fs, mna__oopan = hdfs_list_dir_fnames(path)
        slo__hhq = fs.get_file_info([zao__xscji.path])[0].size
        if mna__oopan:
            path = path.rstrip('/')
            mna__oopan = [(path + '/' + jycum__kcyu) for jycum__kcyu in
                sorted(filter(eao__bhwvn, mna__oopan))]
            ntrz__tiri = [jycum__kcyu for jycum__kcyu in mna__oopan if fs.
                get_file_info([urlparse(jycum__kcyu).path])[0].size > 0]
            if len(ntrz__tiri) == 0:
                raise BodoError(sgb__rpcw)
            fname = ntrz__tiri[0]
            fname = urlparse(fname).path
            slo__hhq = fs.get_file_info([fname])[0].size
        zrjk__nvgad = fs.open_input_file(fname)
    elif zao__xscji.scheme in ('abfs', 'abfss'):
        jetj__jym = True
        fs, mna__oopan = abfs_list_dir_fnames(path)
        slo__hhq = fs.info(fname)['size']
        if mna__oopan:
            path = path.rstrip('/')
            mna__oopan = [(path + '/' + jycum__kcyu) for jycum__kcyu in
                sorted(filter(eao__bhwvn, mna__oopan))]
            ntrz__tiri = [jycum__kcyu for jycum__kcyu in mna__oopan if fs.
                info(jycum__kcyu)['size'] > 0]
            if len(ntrz__tiri) == 0:
                raise BodoError(sgb__rpcw)
            fname = ntrz__tiri[0]
            slo__hhq = fs.info(fname)['size']
            fname = urlparse(fname).path
        zrjk__nvgad = fs.open(fname, 'rb')
    else:
        if zao__xscji.scheme != '':
            raise BodoError(
                f'Unrecognized scheme {zao__xscji.scheme}. Please refer to https://docs.bodo.ai/latest/file_io/.'
                )
        jetj__jym = False
        if os.path.isdir(path):
            aqz__locfx = filter(eao__bhwvn, glob.glob(os.path.join(os.path.
                abspath(path), '*')))
            ntrz__tiri = [jycum__kcyu for jycum__kcyu in sorted(aqz__locfx) if
                os.path.getsize(jycum__kcyu) > 0]
            if len(ntrz__tiri) == 0:
                raise BodoError(sgb__rpcw)
            fname = ntrz__tiri[0]
        slo__hhq = os.path.getsize(fname)
        zrjk__nvgad = fname
    return jetj__jym, zrjk__nvgad, slo__hhq, fs


def get_s3_bucket_region(s3_filepath, parallel):
    try:
        from pyarrow import fs as pa_fs
    except:
        raise BodoError('Reading from s3 requires pyarrow currently.')
    from mpi4py import MPI
    dkaum__mglm = MPI.COMM_WORLD
    bucket_loc = None
    if parallel and bodo.get_rank() == 0 or not parallel:
        try:
            myh__sakv, lulg__aamty = pa_fs.S3FileSystem.from_uri(s3_filepath)
            bucket_loc = myh__sakv.region
        except Exception as ladcd__fjeo:
            if os.environ.get('AWS_DEFAULT_REGION', '') == '':
                warnings.warn(BodoWarning(
                    f"""Unable to get S3 Bucket Region.
{ladcd__fjeo}.
Value not defined in the AWS_DEFAULT_REGION environment variable either. Region defaults to us-east-1 currently."""
                    ))
            bucket_loc = ''
    if parallel:
        bucket_loc = dkaum__mglm.bcast(bucket_loc)
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
        pqdb__jlt = get_s3_bucket_region_njit(path_or_buf, parallel=is_parallel
            )
        vxhyd__tezm, oytim__dmy = unicode_to_utf8_and_len(D)
        rmr__ilf = 0
        if is_parallel:
            rmr__ilf = bodo.libs.distributed_api.dist_exscan(oytim__dmy, np
                .int32(Reduce_Type.Sum.value))
        _csv_write(unicode_to_utf8(path_or_buf), vxhyd__tezm, rmr__ilf,
            oytim__dmy, is_parallel, unicode_to_utf8(pqdb__jlt),
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
    qrkim__etch = get_overload_constant_dict(storage_options)
    oki__tzk = 'def impl(storage_options):\n'
    oki__tzk += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    oki__tzk += f'    storage_options_py = {str(qrkim__etch)}\n'
    oki__tzk += '  return storage_options_py\n'
    srrjv__wcuub = {}
    exec(oki__tzk, globals(), srrjv__wcuub)
    return srrjv__wcuub['impl']
