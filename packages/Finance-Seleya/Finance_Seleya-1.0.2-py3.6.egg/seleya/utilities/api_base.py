import json,time,pdb
from requests.exceptions import ReadTimeout
from platform import python_version

from ..seleya import session
from ..version import __version__
from ..config.default_config import *
import pdb

timeout = 60
max_retries = 5
retry_interval = 2

client_info = json.dumps({"python_version": python_version(),
"client_version": __version__,
"module":"seleya_sdk"})

def __get_conn__():
    return server

def get_http_result(http_client, request_string, 
                    gw, auth=True, 
                    max_retries=max_retries):
    for i in range(1, max_retries + 1):
        try:
            if not auth:
                result = session.get("http://%s:%d/%s" % (http_client[0], http_client[1], request_string),
                                  headers={'accept': 'application/json', 
                                           'CLIENT_INFO': client_info},
                                  timeout=timeout)
            else:
                result = session.get("http://%s:%d/%s" % (http_client[0], http_client[1], request_string),
                                     headers={'accept': 'application/json', 
                                              'CLIENT_INFO': client_info,
                                     'Authorization':'Bearer ' + os.environ['seleya_access_token']},
                                  timeout=timeout)
            return result
        except Exception as e:
            time.sleep(retry_interval)

def post_http_result(http_client, request_string,  body, 
                     gw, auth=True, 
                     max_retries=max_retries):
    for i in range(1, max_retries + 1):
        try:
            if not auth:
                result = session.post("http://%s:%d/%s" % (http_client[0], http_client[1], request_string),
                                  data = body,
                                  headers={'accept': 'application/json',
                                           'Content-Type':'application/x-www-form-urlencoded',
                                           'CLIENT_INFO': client_info},
                                  timeout=timeout)
            else:
                result = session.post(
                    "http://%s:%d/%s" % (http_client[0], http_client[1], request_string),
                    data=body,
                    auth=(os.environ['seleya_client_id'],os.environ['seleya_client_secret']),
                    headers={'accept':'application/json',
                             'Content-Type':'application/x-www-form-urlencoded',
                             'CLIENT_INFO': client_info},
                    timeout=timeout)
                
            return result
        except Exception as e:
            time.sleep(retry_interval)
    
def __get_result__(method, request_string, http_client, body=None, gw=True, auth=True):
    try:
        if method == 'GET':
            result = get_http_result(http_client, request_string, gw, auth)
        elif method == 'POST':
            result = post_http_result(http_client, request_string, body, gw, auth)
            
        if result.status_code != 200:
            raise Exception(result.status_code)
        return result.text
    except ReadTimeout:
        raise Exception('Time-Out')
    except Exception as e:
        raise e