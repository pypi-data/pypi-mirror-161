import warnings, functools, os


def warnings_filter(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.simplefilter('ignore')
        ret = func(*args, **kwargs)
        if not os.environ.get('SELEYAWARNINGS', None):
            # 如果env中的设置不是忽略所有才恢复
            warnings.simplefilter('default')
        return ret

    return wrapper