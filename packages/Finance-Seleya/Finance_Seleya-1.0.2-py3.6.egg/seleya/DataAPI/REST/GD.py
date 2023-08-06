from . import utils
try:
    from StringIO import StringIO
except:
    from io import StringIO
import pandas as pd
import os

from ...utilities import api_base
from ...config.default_config import *


def reviews_score(codes=None, begin_time=None, end_time=None, interval=None,
           page=None, limit=None):
    
    http_client = api_base.__get_conn__()
    request_string = []
    
    request_string.append('api/search/v1/gd_reviews_rating')
    request_string.append('?uid=')
    request_string.append(str(os.environ['seleya_id']))
    
    if codes is not None:
        request_string.append('&codes=')
        request_string.append(str(codes))
        
    if begin_time is not None:
        request_string.append('&begin_time=')
        request_string.append(str(begin_time))
    
    if end_time is not None:
        request_string.append('&end_time=')
        request_string.append(str(end_time))
    
    if interval is not None:
        request_string.append('&interval=')
        request_string.append(str(interval))
    
    if page is not None:
        request_string.append('&page=')
        request_string.append(str(page))
        
    if limit is not None:
        request_string.append('&limit=')
        request_string.append(str(limit))
    
    format_str = 1 if format=='json' else 0
    request_string.append('&format=')
    request_string.append(str(format_str))
    
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result if format=='json' else utils.to_pandas(result)

    
def reviews_text(codes=None, begin_time=None, end_time=None, interval=None,
           page=None, limit=None):
    
    http_client = api_base.__get_conn__()
    request_string = []
    
    request_string.append('api/search/v1/gd_reviews_without_search')
    request_string.append('?uid=')
    request_string.append(str(os.environ['seleya_id']))
    
    if codes is not None:
        request_string.append('&codes=')
        request_string.append(str(codes))
        
    if begin_time is not None:
        request_string.append('&begin_time=')
        request_string.append(str(begin_time))
    
    if end_time is not None:
        request_string.append('&end_time=')
        request_string.append(str(end_time))
    
    if interval is not None:
        request_string.append('&interval=')
        request_string.append(str(interval))
    
    if page is not None:
        request_string.append('&page=')
        request_string.append(str(page))
        
    if limit is not None:
        request_string.append('&limit=')
        request_string.append(str(limit))
    
    format_str = 1 if format=='json' else 0
    request_string.append('&format=')
    request_string.append(str(format_str))
    
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result if format=='json' else utils.to_pandas(result)