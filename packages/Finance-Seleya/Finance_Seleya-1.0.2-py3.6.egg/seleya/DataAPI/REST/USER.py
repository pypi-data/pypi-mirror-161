from . import utils
try:
    from StringIO import StringIO
except:
    from io import StringIO
import hashlib,json,os,pdb

from ...utilities import api_base
from ...config.default_config import *


def login(username=None, password=None):
    http_client = api_base.__get_conn__()
    request_string = []
    request_string.append('auth/oauth/login')
    body = {'email':username, 
            'password': hashlib.md5(password.encode('utf8')).hexdigest()}
    
    
    result = api_base.__get_result__(method='POST',request_string=''.join(request_string), 
                                     body=body, http_client=http_client, gw=True, auth=False)
    
    jtw = json.loads(result)
    if 'user' in jtw['data']:
        uid = str(jtw['data']['user']['uid'])
        os.environ.setdefault('seleya_id', uid)
    if 'clients' in jtw['data']:
        os.environ.setdefault('seleya_client_id', jtw['data']['clients'][0]['client_id'])
        os.environ.setdefault('seleya_client_secret', jtw['data']['clients'][0]['client_secret'])
        body={'grant_type':'password','username':jtw['data']['user']['username'],
          'password':hashlib.md5(password.encode('utf8')).hexdigest(),
          'scope':'profile'}
        request_string = []
        request_string.append('auth/oauth/token')
        result = api_base.__get_result__(method='POST',request_string=''.join(request_string), 
                                         body=body, http_client=http_client, gw=True, auth=True)
        
        jtw = json.loads(result)
        if 'access_token' in jtw:
            token = jtw['access_token']
            expires_in = jtw['expires_in']
            os.environ.setdefault('seleya_access_token', token)
            notice_info = """{0} login successful. UID:{1},token:{2}, Expires in {3}ms.""".format(
            username, str(uid), token, str(expires_in))
        else:
            notice_info = """oauth token error"""
    else:
        notice_info = """login failed"""
    print(notice_info)