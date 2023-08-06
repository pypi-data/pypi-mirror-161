import logging, os, functools, pdb
from contextlib import contextmanager
import pandas as pd
import six as six
from ..utilities.warning import warnings_filter

try:
    from six.moves import cPickle as pickle
except ImportError:
    from six.moves import cPickle as pickle

if six.PY3:
    Unpickler = pickle._Unpickler
    Pickler = pickle._Pickler
else:
    Unpickler = pickle.Unpickler
    Pickler = pickle.Pickler

if six.PY3:

    def as_bytes(s):
        if isinstance(s, bytes):
            return s
        return s.encode('latin1')
else:
    as_bytes = str
"""HDF5_COMP_LEVEL：压缩级别：0-9，如果修改了压缩级别，需要删除之前的物理文件"""
HDF5_COMP_LEVEL = 4
""" HDF5_COMP_LIB: 使用的压缩库:'blosc', 'bzip2', 'lzo', 'zlib', 如果修改了压缩库，需要删除之前的物理文件"""
HDF5_COMP_LIB = 'blosc'
"""HDF5内部存贮依然会使用pickle，即python版本切换，本地文件会有协议冲突：使用所支持的最高协议进行dump"""
K_SET_PICKLE_HIGHEST_PROTOCOL = False
"""HDF5内部存贮依然会使用pickle，即python版本切换，本地文件会有协议冲突：python2, python3协议兼容模式，使用protocol=0"""
K_SET_PICKLE_ZERO_PROTOCOL = False


def ensure_dir(a_path):
    if os.path.isdir(a_path):
        a_dir = a_path
    else:
        a_dir = os.path.dirname(a_path)
    if not os.path.exists(a_dir):
        os.makedirs(a_dir)


def load_pickle(file_name):
    """
    读取python序列化的本地文件
    """
    if not file_exist(file_name):
        logging.error('load_pickle file_name={} not exists!'.format(file_name))
        return None

    logging.info('please wait! load_pickle....:', file_name)

    try:
        with open(file_name, 'rb') as unpickler_file:
            unpickler = Unpickler(unpickler_file)
            ret = unpickler.load()
    except EOFError:
        logging.error(
            'unpickler file with EOFError, please check {} is 0kb!!!'.format(
                file_name))
        ret = {}
    return ret


def dump_pickle(input_obj, file_name, how='normal'):
    ensure_dir(file_name)
    logging.info('please wait! dump_pickle....:{0}'.format(file_name))

    try:
        with open(file_name, "wb") as pick_file:
            if K_SET_PICKLE_HIGHEST_PROTOCOL or how == 'high':
                """使用所支持的最高协议进行dump"""
                pickle.dump(input_obj, pick_file, pickle.HIGHEST_PROTOCOL)
            elif K_SET_PICKLE_ZERO_PROTOCOL or how == 'zero':
                """python2, python3协议兼容模式，使用protocol=0"""
                pickle.dump(input_obj, pick_file, 0)
            else:
                pickler = Pickler(pick_file)
                pickler.dump(input_obj)
    except Exception as e:
        logging.exception(e)


"""hdf5批量处理时保存HDFStore对象，为避免反复open，close"""
__g_batch_h5s = None


def __start_batch_h5s(file_name, mode):
    global __g_batch_h5s
    __g_batch_h5s = pd.HDFStore(file_name,
                                mode,
                                complevel=HDF5_COMP_LEVEL,
                                complib=HDF5_COMP_LIB)


def __end_batch_h5s():
    global __g_batch_h5s
    if __g_batch_h5s is not None and __g_batch_h5s.is_open:
        __g_batch_h5s.flush()
        __g_batch_h5s.close()
        __g_batch_h5s = None


def file_exist(a_path):
    return os.path.exists(a_path)


def batch_h5s(h5_fn, mode='a'):

    def _batch_h5s(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if h5_fn is not None:
                __start_batch_h5s(h5_fn, mode)
            ret = func(*args, **kwargs)
            if h5_fn is not None:
                __end_batch_h5s()
            return ret

        return wrapper

    return _batch_h5s


@contextmanager
def batch_ctx_h5s(h5_fn, mode='a'):
    """
    使用上下文管理器方式对hdf5操作进行批量处理，与装饰器模式batch_h5s
    功能相同，为外部不方便封装为具体操作函数时使用
    """
    if h5_fn is not None:
        __start_batch_h5s(h5_fn, mode)
    yield
    if h5_fn is not None:
        __end_batch_h5s()


@warnings_filter
def dump_del_hdf5(file_name, dump_dict, del_array=None):
    """
    对hdf5进行删除和保存操作，del_array中的key先删除，后保存dump_dict
    字典中的数据
    """
    global __g_batch_h5s

    def do_dump_del_hdf5(h5s):
        """
        对hdf5进行删除和保存操作执行函数
        """
        if del_array is not None:
            for del_key in del_array:
                if h5s.__contains__(del_key):
                    del h5s[del_key]
        for input_key in dump_dict:
            input_obj = dump_dict[input_key]
            h5s[input_key] = input_obj

    if __g_batch_h5s is None:
        # 如果批处理句柄没有打着，使用with pd.HDFStore先打开
        with pd.HDFStore(file_name,
                         'a',
                         complevel=HDF5_COMP_LEVEL,
                         complib=HDF5_COMP_LIB) as h5s_obj:
            do_dump_del_hdf5(h5s_obj)
    else:
        # 使用批处理句柄__g_batch_h5s操作
        do_dump_del_hdf5(__g_batch_h5s)


@warnings_filter
def dump_hdf5(file_name, input_obj, input_key):
    """
    对hdf5进行保存操作
    """
    global __g_batch_h5s
    if __g_batch_h5s is None:
        with pd.HDFStore(file_name,
                         'a',
                         complevel=HDF5_COMP_LEVEL,
                         complib=HDF5_COMP_LIB) as h5s:
            h5s[input_key] = input_obj
    else:
        __g_batch_h5s[input_key] = input_obj


def del_hdf5(file_name, key):
    """
    对hdf5进行删除操作
    """
    if not file_exist(file_name):
        return
    if __g_batch_h5s is None:
        with pd.HDFStore(file_name,
                         'a',
                         complevel=HDF5_COMP_LEVEL,
                         complib=HDF5_COMP_LIB) as h5s:
            if h5s.__contains__(key):
                del h5s[key]
    else:
        if __g_batch_h5s.__contains__(key):
            del __g_batch_h5s[key]


def load_hdf5(file_name, key):
    """
    读取hdf5中的数据
    """
    global __g_batch_h5s
    if not file_exist(file_name):
        return None

    def _load_hdf5(h5s):
        load_obj = None
        if h5s.__contains__(key):
            try:
                load_obj = h5s[key]
            except (AttributeError, TypeError):
                pass
        return load_obj

    if __g_batch_h5s is None:
        with pd.HDFStore(file_name,
                         'a',
                         complevel=HDF5_COMP_LEVEL,
                         complib=HDF5_COMP_LIB) as h5s_obj:
            return _load_hdf5(h5s_obj)
    else:
        return load_hdf5(__g_batch_h5s)