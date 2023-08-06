import os,json,requests
from azure.storage.blob import BlobClient
from ..utilities import api_base

class BlobService(object):
    def __init__(self):
        pass
        
    def _get_sasurl(self, container_name, remote_file_name):
        http_client = api_base.__get_conn__()
        request_string = []
    
        request_string.append('/api/storage/v1/blob_sas')
        request_string.append('?uid=')
        request_string.append(str(os.environ['seleya_id']))
        
        request_string.append('&container=')
        request_string.append(str(container_name))
        
        request_string.append('&filepath=')
        request_string.append(str(remote_file_name))
        
        return api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    
    def _get_blob(self, container_name, path):
        
        http_client = api_base.__get_conn__()
        request_string = []
    
        request_string.append('/api/storage/v1/blob_explorer')
        request_string.append('?uid=')
        request_string.append(str(os.environ['seleya_id']))
        
        request_string.append('&container=')
        request_string.append(str(container_name))
        
        request_string.append('&path=')
        request_string.append(str(path))
        
        request_string.append('&Authorization=')
        request_string.append(str('Bearer'))
        
        return api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
        
    
    def blob_explorer(self, container_name, path):
        result = self._get_blob(container_name=container_name, path=path)
        blob_info = json.loads(result)
        return blob_info
        
    def upload_file(self, container_name, local_file_name,
                    remote_file_name):
        result = self._get_sasurl(container_name=container_name, remote_file_name=remote_file_name)
        url_info = json.loads(result)
        client =  BlobClient.from_blob_url(url_info['data']['url'])
        with open(local_file_name, 'rb') as f:
            try:
                client.upload_blob(f)
            except:
                print(remote_file_name + " is exist")
            
    def download_file(self, container_name, remote_file_name, local_file_name, 
                      is_office=True, is_refresh=False):
        if os.path.exists(local_file_name) and not is_refresh:
            return None
        
        dir_path, _ = os.path.split(local_file_name)
        
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            
        result = self._get_sasurl(container_name=container_name, 
                                  remote_file_name=remote_file_name)
        url_info = json.loads(result)
        if is_office:
            client =  BlobClient.from_blob_url(url_info['data']['url'])
            with open(local_file_name, "wb") as my_blob:
                try:
                    download_stream = client.download_blob()
                    my_blob.write(download_stream.readall())
                except:
                    print(remote_file_name + " is not exist")
        else:
            res = requests.get(url=url_info['data']['url'])
            with open(local_file_name,"wb") as fb:
                fb.write(res.content)
            