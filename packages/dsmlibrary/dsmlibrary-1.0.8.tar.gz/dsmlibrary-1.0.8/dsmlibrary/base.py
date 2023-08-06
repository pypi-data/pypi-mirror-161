import os
import requests
import time

from minio import Minio

defind_clear_output = False
try:
    from IPython.display import clear_output
    defind_clear_output = True
except:
    pass

discovery = os.environ.get('discovery_url', "https://discovery.data.storemesh.com")

_base_discovery_api = os.environ.get('BASE_DISCOVERY_API', "https://api.discovery.data.storemesh.com")
_internal_base_discovery_api = os.environ.get('INTERNAL_BASE_DISCOVERY_API',"http://discovery-backend:8000")

_external_api_minio = os.environ.get('external_api_minio',"")
_internal_api_minio = os.environ.get('internal_api_minio',"")

_base_minio_url=os.environ.get('base_minio_url')
bucket_name = os.environ.get('bucketname', 'dataplatform')

class Base:
    def __init__(self, token=None):
        """Init DSM Dataset Manager

        Args:
            jwt_token (str): JWT token from IaM.
        """
        
        _internal = os.environ.get('internal', None) == "true"
        self._internal = _internal
        if self._internal:
            base_discovery_api = _internal_base_discovery_api
        else:
            base_discovery_api = _base_discovery_api
        self._base_discovery_api = base_discovery_api
        self._discovery_api = f"{base_discovery_api}/api/v2"
        
        if token is None:
            print(f"Please get token from {discovery}")
            token = input("Your Token : ")
            if defind_clear_output:
                time.sleep(2)
                clear_output()
        if token in [None, '']:
            raise Exception('Please enter your key from dsmOauth')
        self._jwt_header = {
            'Authorization': f'Bearer {token}'
        }
        _res = requests.get(f"{base_discovery_api}/api/v2/account/me/", headers=self._jwt_header)
        if _res.status_code != 200:
            txt = _res.json() if _res.status_code < 500 else " "
            raise Exception(f"Can not connect to DataPlatform, {txt}")
        self.token = token
        self._tmp_path = 'dsm.tmp'
        os.makedirs(self._tmp_path, exist_ok=True)
        _res = requests.get(f"{base_discovery_api}/api/minio/minio-user/me/", headers=self._jwt_header)
        if _res.status_code != 200:
            raise Exception("Can not get minio user")
        data = _res.json()
        self._minio_access = data['access']
        self._minio_secret = data['secret']
        
        self.client = Minio(
            _base_minio_url,
            access_key=self._minio_access,
            secret_key=self._minio_secret,
            secure=False
        )
        _scheme = "http" if self._internal else "https"
        self._storage_options = {
            'key': self._minio_access,
            'secret': self._minio_secret,
            'client_kwargs':{
                'endpoint_url': f"{_scheme}://{_base_minio_url}"
            }
        }
        
        print("Init DataNode sucessful!")
        
    def _replace_minio_api(self, url):
        return url.replace('https', 'http').replace(_external_api_minio, _internal_api_minio)
    
    def _check_fileExists(self, directory, name):
        _res = requests.get(f"{self._discovery_api}/directory/{directory}/fileExists/?filename={name}", headers=self._jwt_header)
        if _res.status_code == 200:
            replace = False
        elif _res.status_code == 302:
            replace = input(f"File {name} alrady exists, do you want to replace y/n : ").replace(' ', '').lower() == "y"
        else:
            status = _res.json() if _res.status_code < 500 else ""
            raise Exception(f"check file exists error {status}")
        return replace