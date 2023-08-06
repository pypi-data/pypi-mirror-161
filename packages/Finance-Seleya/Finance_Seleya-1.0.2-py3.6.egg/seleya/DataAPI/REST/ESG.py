from . import utils
try:
    from StringIO import StringIO
except:
    from io import StringIO
import pandas as pd
import os,pdb,json

from ...utilities import api_base
from ...config.default_config import *

def feed(codes=None, category=None, begin_time=None, end_time=None, 
         interval=None, page=None, limit=None, format='pandas'):
    http_client = api_base.__get_conn__()
    request_string = []
    
    
    request_string.append('api/esg/v1/feed')
    request_string.append('?uid=')
    request_string.append(str(os.environ['seleya_id']))
    
    if codes is not None:
        request_string.append('&codes=')
        request_string.append(str(codes))
        
    if category is not None:
        request_string.append('&category=')
        request_string.append(str(category))
        
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
    
    request_string.append('&summary=')
    request_string.append(str('true'))
    
    format_str = 1 if format=='json' else 0
    request_string.append('&format=')
    request_string.append(str(format_str))
    
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result if format=='json' else utils.to_pandas(result['data'])


def factor(codes=None, categories=None, level=None, 
           begin_time=None, end_time=None, interval=None, 
           cycle=None, format='pandas'):
    http_client = api_base.__get_conn__()
    request_string = []
    
    request_string.append('api/esg/v1/factor')
    request_string.append('?uid=')
    request_string.append(str(os.environ['seleya_id']))
    
    if codes is not None:
        request_string.append('&codes=')
        request_string.append(str(codes))
    
    if categories is not None:
        request_string.append('&categories=')
        request_string.append(str(categories))
        
    if level is not None:
        request_string.append('&level=')
        request_string.append(str(level))
        
    if begin_time is not None:
        request_string.append('&begin_time=')
        request_string.append(str(begin_time))
    
    if end_time is not None:
        request_string.append('&end_time=')
        request_string.append(str(end_time))
    
    if interval is not None:
        request_string.append('&interval=')
        request_string.append(str(interval))
    
    if cycle is not None:
        request_string.append('&cycle=')
        request_string.append(str(cycle))
    
    format_str = 1 if format=='json' else 0
    request_string.append('&format=')
    request_string.append(str(format_str))
    
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result if format=='json' else utils.to_pandas(result)