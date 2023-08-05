'''
Implementation of the Optilogic Pioneer Rest API.

Pioneer Product Suite 
Encompasses Atlas and Andromeda products.

Atlas 
Web Application with cornerstone IDE, Jobs Dashboard, Account Management, and more.
https://atlas.optilogic.app

Andromeda 
On demand hyper-scaling machinery that provisions required resources for job management and run execution.

API Documentation
https://api-docs.optilogic.app/documentation

API Authentication Methods
User Pass: legacy auth method that requires time to live key management
App Key: preferred auth method for API usage

App Key Management
https://atlas.optilogic.app/dashboard/#/user-account?tab=appkey

Glossary:
account file storage: can be standard disk or premium ssd available to all user workspaces
file storage: generic storage reference to encompass workspace and account file storage types
stack: software environment configuration used to build a a workspace from ie linux based pythonic world with specific configuration
ws,wksp,workspace: software environment instance built from a stack and has associated file storage
workspace file storage: standard file storage that is bound to specific workspace instance
'''

import os
import pickle
import requests
import time
from cachetools import cached, TTLCache
from datetime import datetime
from getpass import getpass
from tempfile import gettempdir

class Api():
    '''Optilogic API is to pilot Andromeda system
    
    EXAMPLE CONFIG
    :{'un': 'username', 'pw': 'password', 'auth_legacy': True}
    :{'un': 'username', 'app_key': 'base64str'}

    :param un: str: username that has the API role
    :param pw: str: password of the user to authenticate and generate api key
    :param auth_legacy: bool: true for conventional username password or false for appkey
    :param cfg: dict: addition config to unpack and setup for api use
    :param apikey: str: username password authentication with one hour time to live
    :param appkey: str: authentication key generated in product without time to live restrictions
    '''

    JOBSTATES  = ['submitted','starting','started','running','done','stopping','stopped','canceling','cancelled','error']
    JOBSTATES_TERMINAL = ['done','stopped','cancelled','error']

    def __init__(self, auth_legacy = True, appkey = None, un = None, pw = None, **cfg):
        self.auth_apikey = None
        self.auth_apikey_expiry = None
        self.auth_apikey_mins_left = None
        self.auth_appkey = appkey
        self.auth_method_legacy = auth_legacy
        self.auth_req_header = {'x-api-key': self.auth_apikey, 'x-app-key': self.auth_appkey}
        self.auth_username = un if un else input('\nREQUIRED API Username: ')
        assert(len(self.auth_username) > 0)
        
        if self.auth_method_legacy:
            self.auth_req_header.pop('x-app-key')
            # TODO: implement a linux only max seconds to complete via SIGALRM
            self.auth_userpass = pw if pw else getpass('\nREQUIRED API User Password: ')
        else:
            self.auth_req_header.pop('x-api-key')
            # TODO: implement a linux only max seconds to complete via SIGALRM
            self.auth_appkey = cfg.get('appkey') if appkey else input('\nREQUIRED API AppKey: ')

        self.api_domain ='https://api.optilogic.app/'
        self.api_version = self.api_domain + 'v0/'
        self.debug_requests = True
        self.dir_tmp = os.path.join(gettempdir(), 'optilogic')
        self.file_cache_auth = os.path.join(self.dir_tmp, f'auth_{self.auth_username}.pkl')

        if os.path.exists(self.dir_tmp) is False:
            os.makedirs(self.dir_tmp)
        if os.path.exists(self.file_cache_auth) is False and self.auth_method_legacy:
            self.authenticate_legacy()
        
        self.job_start_recent_key = ''
        self.STORAGE_DEVICE_TYPES = ['azure_afs', 'azure_workspace', 'onedrive', 'postgres_db']

    def __batch_input_validation(self, batch: dict, find = False) -> None:
        '''assert batch input structure'''

        if batch.get('batchItems') is None:
            raise KeyError('batchItems key is missing')

        if len(batch['batchItems']) == 0:
            raise IndexError('batchItems list is empty')

        for item in batch['batchItems']:
            if find and item.get('pySearchTerm') is None:
                raise KeyError('pySearchTerm key is missing')
            if find is False and item.get('pyModulePath') is None:
                raise KeyError('pyModulePath key is missing')

    def __does_storage_exist(self, type: str, name: str = None) -> bool:
        '''does the account have a specific storage type and optionally by name
        
        :param type: str: storage type
        :param name: str: storage name of type defaults to None 
        '''

        assert(type in self.STORAGE_DEVICE_TYPES)        
        devices = self.account_storage_devices()
        
        if name is None:
            exists = [True for d in devices['storages'] if d['type'] == type]
        else:
            exists = [True for d in devices['storages'] if d['type'] == type and d['name'] == name]

        return True if len(exists) >= 1 else False

    def _cache_apikey(self) -> dict:
        '''read auth api from cache'''

        with open(self.file_cache_auth, 'rb') as f:
            cache_auth_pickle: dict = pickle.load(f)
        
        return cache_auth_pickle

    def _cache_apikey_bad(self) -> bool:
        '''check if api cache is incomplete or expired'''

        bad = False
        cache = self._cache_apikey()

        # error on safety refresh before last two minutes
        now_time = datetime.now().timestamp() + 120

        if (cache.get('apikey') is None
            or cache.get('user') is None
            or cache.get('user') != self.auth_username
            or now_time > cache.get('expiration_time', 0)):
                bad = True

        return bad
    
    def _check_apikey_expiration_time(self) -> None:
        '''userpass key is only valid for 1 hour, ensure it is refreshed'''

        key_bad = self._cache_apikey_bad()
        if key_bad:
            self.authenticate_legacy()
        else:
            # if cache has time left on the clock, reuse cached apikey
            cache = self._cache_apikey()
            now_time = datetime.now().timestamp() + 120
            mins_left = round((cache['expiration_time'] - now_time) / 60, 2)
            self.auth_apikey_mins_left = mins_left
            self.auth_apikey = cache['apikey']
            self.auth_apikey_expiry = cache['expiration_time']
            self.auth_req_header.update({'x-api-key': cache['apikey']})

    def _fetch_json(self, method: str, url: str, json = None, data = None, extra_headers: dict = None) -> dict:
        '''API calls that return a JSON response

        :param method: str: http request methods
        :param url: str: api server endpoint
        :param json: dict: payload in body of post call
        :param data: any: (optional) Dictionary, list of tuples, bytes, or file-like object
        :param extra_headers: dict: extend the request headers
        '''

        if self.auth_method_legacy is True:
            self._check_apikey_expiration_time()

        if extra_headers:
            extra_headers.update(self.auth_req_header)
            headers = extra_headers
        else:
            headers = self.auth_req_header

        try:
            resp = requests.request(method, url, headers=headers, json=json, data=data)
            resp.raise_for_status()
            resp_body_json = resp.json()
            if self.debug_requests and resp_body_json['result'] == 'error':
                print(url, resp_body_json)
        
        except Exception as ex:
            if self.debug_requests:
                print(f"\nFetch Exception: {url}\n\nResponse Body Text:\n{resp.text}\n\nException: \n{ex}")
            resp_body_json = {'crash': True, 'url': url, 'resp': resp, 'response_body': resp.text, 'exception': ex}

        return resp_body_json

    @cached(cache=TTLCache(maxsize=5, ttl=60))
    def account_info(self) -> dict:
        '''GET v0/account - Get wksp and user information about the account'''

        url = self.api_version + 'account'
        resp = self._fetch_json('get', url)
        return resp

    def account_storage_device(self, type: str, name: str = None) -> dict:
        '''get storage device
        
        :param type: str: storage device type
        :param name: str: storage device name
        '''
        
        device: dict = {}
        if self.__does_storage_exist(type, name) is True:
            devices = self.account_storage_devices()
            for d in devices['storages']:
                if d['type'] == type and name is None:
                    device = d
                    break
                elif d['type'] == type and d['name'] == name:
                    device = d
                    break
        
        return device
    
    @cached(cache=TTLCache(maxsize=5, ttl=60))
    def account_storage_devices(self) -> dict:
        '''GET ​/v0​​/storage - Get a list of available storage devices in an account'''

        url = self.api_version + 'storage'
        resp = self._fetch_json('get', url)
        return resp

    def account_workspace_create(self, name: str, stack: str = 'Gurobi') -> dict:
        '''POST /v0​/workspace - Create a new workspace'''

        url = self.api_version + f'workspace?name={name}&stack={stack}'
        resp = self._fetch_json('post', url)
        return resp 

    def account_workspace_delete(self, wksp: str) -> dict:
        '''DELETE /v0​/workspace/runtime - Delete a workspace'''

        raise NotImplementedError
        url = self.api_version + f'{wksp}/runtime'
        resp = self._fetch_json('delete', url)
        return resp 

    @cached(cache=TTLCache(maxsize=5, ttl=60))
    def account_workspaces(self) -> dict:
        '''GET ​/v0​​/workspaces - Get a list of available workspaces in an account'''

        url = self.api_version + 'workspaces'
        resp = self._fetch_json('get', url)
        return resp

    @property
    def api_server_online(self) -> bool:
        '''check if API service is up and running'''
        
        response = requests.request('get', f'{self.api_version}ping')
        return True if response.status_code == 200 else False

    def authenticate_legacy(self) -> None:
        '''POST ​/refreshApiKey - Legacy auth method that will create an Api Key via username and password

        App Key is the preferred auth method for API usage
        https://atlas.optilogic.app/dashboard/#/user-account?tab=appkey
        
        '''

        # do a fetch, process response, then set
        url = self.api_version + 'refreshApiKey'
        headers = {'x-user-id': self.auth_username, 'x-user-password': self.auth_userpass}

        response = requests.request('post', url, headers=headers)
        response.raise_for_status()
        resp = response.json()

        # set instance members
        self.auth_apikey = resp['apiKey']
        self.auth_apikey_expiry = int(resp['expirationTime'])
        self.auth_apikey_mins_left = round((self.auth_apikey_expiry - datetime.now().timestamp()) / 60, 2)
        self.auth_req_header.update({'x-api-key': resp['apiKey']})

        # cache to disk to avoid unnecessary calls to api server
        auth_pickle = {'apikey': self.auth_apikey,
                       'expiration_time': self.auth_apikey_expiry,
                       'user': self.auth_username}
        
        with open(self.file_cache_auth, 'wb') as f:
            pickle.dump(auth_pickle, f)

    def ip_address_allow(self, database_name: str, ip: str = None ) -> dict:
        '''PUT /v0/storage/{database_name}/ip-in-firewall - an ip address to be whitelisted
        
        :param database_name: str: postgres database name
        :param ip: str: ip address to allow through the firewall, defaults to None

        ommited ip address will use the client's ip address that is making the request
        '''

        exists = self.storagename_database_exists(database_name)
        if exists is False:
            raise AssertionError(f'postgress database {database_name} does not exist')

        url = f'{self.api_version}storage/{database_name}/ip-in-firewall'
        if ip:
            url += f'?ipAddress={ip}'

        time.sleep(1)
        resp = self._fetch_json('put', url)
        return resp

    def ip_address_allowed(self, database_name: str, ip: str = None ) -> dict:
        '''GET /v0/storage/{database_name}/ip-in-firewall - is this ip address whitelisted
        
        :param database_name: str: postgres database name
        :param ip: str: ip address to allow through the firewall, defaults to None
        
        ommited ip address will use the client's ip address that is making the request
        '''

        exists = self.storagename_database_exists(database_name)
        if exists is False:
            raise AssertionError(f'postgress database {database_name} does not exist')

        url = f'{self.api_version}storage/{database_name}/ip-in-firewall'
        if ip:
            url += f'?ipAddress={ip}'

        time.sleep(1)
        resp = self._fetch_json('get', url)
        return resp
    
    def onedrive_push(self, path: str) -> dict:
        '''POST /v0​/Studio/onedrive/push - Push Optilogic files to OneDrive
        
        :param path: str: file or subtree path
        '''

        url = f'{self.api_version}Studio/onedrive/push?path={path}'
        resp = self._fetch_json('post', url)
        return resp
    
    def storagename_onedrive_exists(self, name) -> bool:
        '''does the account have OneDrive file storage by name'''
        return self.__does_storage_exist('onedrive', name)
    
    def storagename_wkspfiles_exists(self, name) -> bool:
        '''does the account have workspace file storage by name'''
        return self.__does_storage_exist('azure_workspace', name)
    
    def storagename_accountfiles_exists(self, name) -> bool:
        '''does the account have account file storage by name'''
        return self.__does_storage_exist('azure_afs', name)
    
    def storagename_database_exists(self, name) -> bool:
        '''does the account have postgres database by name'''
        return self.__does_storage_exist('postgres_db', name)
    
    @property
    def storagetype_onedrive_exists(self) -> bool:
        '''does the account have OneDrive file storage'''
        return self.__does_storage_exist('onedrive')
    
    @property
    def storagetype_wkspfiles_exists(self) -> bool:
        '''does the account have workspace file storage'''
        return self.__does_storage_exist('azure_workspace')
    
    @property
    def storagetype_accountfiles_exists(self) -> bool:
        '''does the account have account file storage'''
        return self.__does_storage_exist('azure_afs')
    
    @property
    def storagetype_database_exists(self) -> bool:
        '''does the account have postgres database'''
        return self.__does_storage_exist('postgres_db')

    @cached(cache=TTLCache(maxsize=5, ttl=300))
    def sql_connection_info(self, storage_name: str) -> dict:
        '''GET /storage​/{storageName}​/connection-string
        Get the connecton information for a SQL storage item
        
        :param storage_name: str: postgres database friendly name
        '''

        assert(self.storagename_database_exists(storage_name)) 
        url = f'{self.api_version}storage/{storage_name}/connection-string'
        resp = self._fetch_json('get', url)
        return resp

    def sql_query(self, storage_name: str, query: str) -> dict:
        '''POST ​/v0​/storage/{storagename}​/query-sql - retreives data from one or more tables
        
        :param storage_name: str: postgres database friendly name
        :param query: str: sql statement
        '''
        
        assert(self.storagename_database_exists(storage_name))       
        d = {'query': query}
  
        url = f'{self.api_version}storage/{storage_name}/query-sql'
        resp = self._fetch_json('post', url, json=d)
        return resp

    def util_job_monitor(self, wksp: str, job_key: str, stop_when = 'running', secs_max = 120) -> bool:
        '''poll a job for status'
        
        :param wksp: str: workspace where relevant jobs belong to
        :param job_key: str: which job to monitor
        :param stop_when: str: return when job state matches, defaults to running
        :param secs_max: int: hard stop then return when wait time is exhausted, defaults to 100
        
        STOP WHEN STATES
        'submitted','starting','started','running','done','stopping','stopped','canceling','cancelled','error'

        fail-safe stop will occur when job is in a terminal state
        '''

        stop_when = stop_when.lower()
        assert(stop_when in self.JOBSTATES)
        
        time_start = time.time()
        while True:
            time.sleep(5)
            resp = self.wksp_job_status(wksp, job_key)
            time_delta = time.time() - time_start
            if time_delta >= secs_max:
                return False
            elif resp['status'] in self.JOBSTATES_TERMINAL or resp['status'] == stop_when:
                return True

    def wksp_file_copy(self, wksp: str, file_path_src: str, file_path_dest: str, overwrite: bool = False) -> dict:
        '''POST ​/v0​/{workspace}​/file​/copy - Copy a file within a workspace

        :param wksp: str: workspace to download from
        :param file_path_src: str: file to copy from
        :param file_path_dest: str: where to copy to
        :param overwrite: bool: overwrite existing file if exists
        '''

        src_path, src_filename = os.path.split(file_path_src)
        dest_path, dest_filename = os.path.split(file_path_dest)

        # if targetDirectoryPath is not provided, path will be defaulted to src directory
        url = f'{self.api_version }{wksp}/file/copy?sourceDirectoryPath={src_path}&sourceFilename={src_filename}'
        url += f'&targetDirectoryPath={dest_path}&targetFilename={dest_filename}&overwrite={overwrite}'
        resp = self._fetch_json('post', url)
        return resp

    def wksp_file_delete(self, wksp: str, file_path: str) -> dict:
        '''DELETE ​/v0​/{workspace}​/file​/{directoryPath}​/{filename} -Delete a specific file from a workspace

        :param wksp: str: workspace to delete from
        :param file_path: str: file to delete
        '''

        dir_path, file_name = os.path.split(file_path)
        url = f'{self.api_version}{wksp}/file/{dir_path}/{file_name}'
        resp = self._fetch_json('delete', url)
        return resp

    def wksp_file_download(self, wksp: str, file_path: str) -> str:
        '''GET ​/v0​/{workspace}​/file​/{directoryPath}​/{filename} - Get a file from a specific workspace

        :param wksp: str: workspace to download from
        :param file_path: str: file to download
        '''

        dir_path, file_name = os.path.split(file_path)
        url = f'{self.api_version}{wksp}/file/{dir_path}/{file_name}?op=download'
        response = requests.get(url=url, headers=self.auth_req_header)
        return response.text

    def wksp_file_download_status(self, wksp: str, file_path: str) -> dict:
        '''GET ​/v0​/{workspace}​/file​/{directoryPath}​/{filename} - Get a file metadata

        :param wksp: str: workspace to download from
        :param file_path: str: file to download
        '''

        dir_path, file_name = os.path.split(file_path)
        url = f'{self.api_version}{wksp}/file/{dir_path}/{file_name}?op=status'
        resp = self._fetch_json('get', url)
        return resp

    def wksp_file_upload(self, wksp: str, file_path_dest: str, file_path_local: str = None,
                        overwrite: bool = False, filestr: str = None) -> dict:
        '''POST ​/v0​/{workspace}​/file​/{directoryPath}​/{filename} - Upload a file to a workspace

        :param wksp: str: workspace to upload to
        :param file_path_dest: str: where to write file on optilogic file storage
        :param file_path_local: str: file to read from on local machine
        :param overwrite: bool: change existing file, defaults to False
        :param filestr: str: alternative file contents, defaults to None
        '''

        dir_path, file_name = os.path.split(file_path_dest)
        url = f'{self.api_version}{wksp}/file/{dir_path}/{file_name}?overwrite={overwrite}'

        if filestr:
            data = filestr
        elif file_path_local:
            assert os.path.exists(file_path_local)
            with open(file_path_local) as file:
                data = file.read()
        elif filestr is None and file_path_local is None:
            raise ValueError('must provide a file_path_local or filestr')

        headers = {'content-type': 'application/octet-stream',
                   'content-length': f'{len(data)}'}

        resp = self._fetch_json('post', url, data=data, extra_headers=headers)
        return resp

    def wksp_files(self, wksp: str, filter = None) -> dict:
        '''GET ​/v0​/{workspace}​/files - List all user files in the workspace
        
        :param wksp: str: where your files live
        :param filter: str: regex str on full file path, defautls to None
        '''

        url = self.api_version + f'{wksp}/files'
        url += f'?filter={filter}' if filter else ''
        resp = self._fetch_json('get', url)
        return resp

    def wksp_folder_delete(self, wksp: str, dir_path: str, force = False) -> dict:
        '''DELETE ​/v0/{workspace}​/folder​/{directoryPath} Delete a folder from a workspace

        :param dir_path: str: folder to delete
        '''

        url = f'{self.api_version}{wksp}/folder/{dir_path}?recursive={str(force).lower()}'
        resp = self._fetch_json('delete', url)
        return resp

    def wksp_info(self, wksp: str) -> dict:
        '''GET ​/v0​/{workspace} - Get information about a workspace

        :param wksp: str: where your files live
        '''

        url = self.api_version + wksp
        resp = self._fetch_json('get', url)
        return resp

    def wksp_job_back2back(self, wksp: str, batch: dict, verboseOutput = False, 
                      resourceConfig: str = None, tags: str = None) -> dict:
        '''POST /v0/{workspace}/jobBatch/backToBack - Queue one job to run many python modules in a row
        
        :param batch: dict: payload in body of post call
        :param resourceConfig: str: 3xs, 2xs, xs, s, m, l, xl, 2xl
        :param tags: str: earmark the job record
        :param timeout: int: max job runtime in secs
        :param verboseOutput: bool: emit python module info to stdout
        :param wksp: str: workspace scope 
        
        INPUT DIRECTIVE
        :batch: dict: payload to send in body of the request
        :batchItems: list: find python modules to execute
        :pyModulePath: str: absolute file path of the python module to execute
        :commandArgs: str: arguments to pass to associated python module
        :timeout: int: max run time of the associated python module
        {"batchItems":[
            {
                "pyModulePath":"/projects/My Models/Transportation/France.py",
                "commandArgs":"diesel",
                "timeout": 100
            }]
        } 
        '''

        self.__batch_input_validation(batch)
        url = f'{self.api_version}{wksp}/jobBatch/backToBack'
        query = ''
        query += '&verboseOutput' if verboseOutput else ''
        query += f'&resourceConfig={resourceConfig}' if resourceConfig else ''
        query += f'&tags={tags}' if tags else ''
        if len(query) > 0:
            url = f"{url}?{query.lstrip('&')}"

        resp = self._fetch_json('post', url, json=batch)
        return resp

    def wksp_job_back2back_findnrun(self, wksp: str, batch: dict, verboseOutput = False, 
                      resourceConfig: str = None, tags: str = None) -> dict:
        '''POST /v0/{workspace}/jobBatch/backToBack/searchNRun - Run many python modules back to back
        
        :param batch: dict: list of py regex search terms to discover py modules to run
        :param resourceConfig: str: 3xs, 2xs, xs, s, m, l, xl, 2xl
        :param tags: str: earmark the job record
        :param timeout: int: max job runtime in secs
        :param verboseOutput: bool: emit python module info to stdout
        :param wksp: str: workspace scope 

        INPUT DIRECTIVE
        :batch: dict: payload to send in body of the request
        :batchItems: list: find python modules to execute
        :pySearchTerm: str: regex search file paths yields python modules to execute
        :commandArgs: str: arguments to pass into matching python modules
        :timeout: int: max run time for matching python modules
        {"batchItems":[
            {"pySearchTerm":"My Models/Transportation", "commandArgs":"", "timeout": 0},
            {"pySearchTerm":"network-\d{3,}", "commandArgs":"", "timeout": 0}
        ]}
        '''

        self.__batch_input_validation(batch, find=True)
        url = f'{self.api_version}{wksp}/jobBatch/backToBack/searchNRun'
        query = ''
        query += '&verboseOutput' if verboseOutput else ''
        query += f'&resourceConfig={resourceConfig}' if resourceConfig else ''
        query += f'&tags={tags}' if tags else ''
        if len(query) > 0:
            url = f"{url}?{query.lstrip('&')}"

        resp = self._fetch_json('post', url, json=batch)
        return resp

    def wksp_job_file_error(self, wksp: str, jobkey: str) -> str:
        '''GET ​/v0​/{workspace}​/job​/{jobKey} - Get job error file

        :param wksp: str: workspace where job exists
        :param jobkey: str: unique id
        '''

        url = f'{self.api_version}{wksp}/job/{jobkey}?op=error'
        resp = requests.request('get', url, headers=self.auth_req_header)
        return resp.content.decode('utf-8')

    def wksp_job_file_result(self, wksp: str, jobkey: str) -> str:
        '''GET ​/v0​/{workspace}​/job​/{jobKey} - Get job result file

        :param wksp: str: workspace where job exists
        :param jobkey: str: unique id
        '''

        url = f'{self.api_version }{wksp}/job/{jobkey}?op=result'
        resp = requests.request('get', url, headers=self.auth_req_header)
        return resp.content.decode('utf-8')

    def wksp_job_ledger(self, wksp: str, jobkey: str, keys: str = None) -> dict:
        '''GET /{workspace}/job/{jobKey}/ledger - Get records from a specified job
        
        :param wksp: str: workspace scope
        :param jobkey: str: unique id
        :param keys: str: return only ledger records that match csv string
        '''
        
        url = f'{self.api_version}{wksp}/job/{jobkey}/ledger'
        if keys:
            url += f'?keys={keys}'
        resp = self._fetch_json('get', url)
        return resp

    def wksp_job_metrics(self, wksp: str, jobkey: str) -> dict:
        '''GET /{workspace}/job/{jobKey}/metrics - Get one second cpu and memory sampling of a job
        
        :param wksp: str: workspace scope
        :param jobkey: str: unique id
        '''

        url = f'{self.api_version}{wksp}/job/{jobkey}/metrics'
        resp = self._fetch_json('get', url)
        return resp

    def wksp_job_metrics_max(self, wksp: str, jobkey: str) -> dict:
        '''GET /{workspace}/job/{jobKey}/metrics/stats - Get peak cpu and memory stats of a job
        
        :param wksp: str: workspace scope
        :param jobkey: str: unique id
        '''

        url = f'{self.api_version}{wksp}/job/{jobkey}/metrics/stats'
        resp = self._fetch_json('get', url)
        return resp

    def wksp_job_start(self, wksp: str, file_path: str, commandArgs: str = None, tags: str = None,
                      timeout: int = None, resourceConfig: str = None) -> dict:
        '''POST ​/v0​/{workspace}​/job - Queue a job to run

        :param wksp: str: workspace scope
        :param file_path: str: python module to run
        :param commandArgs: str: positional args for py module
        :param tags: str: earmark the job record
        :param timeout: int: kill job if still running after duration
        :param resourceConfig: str: mini, 3xs, 2xs, xs, s, m, l, xl, 2xl
        '''
        
        assert(file_path.endswith('.py'))            
        dir_path, file_name = os.path.split(file_path)

        url = f'{self.api_version}{wksp}/job?directoryPath={dir_path}&filename={file_name}'
        url += f'&commandArgs={commandArgs}' if commandArgs else ''
        url += f'&tags={tags}' if tags else ''
        url += f'&timeout={timeout}' if timeout else ''
        url += f'&resourceConfig={resourceConfig}' if resourceConfig else ''
        
        now = datetime.utcnow()
        resp = self._fetch_json('post', url)
        self.job_start_recent_key = resp['jobKey']
        # burn in the req time the call was initiated
        resp['apiRequestTime'] = now
        return resp

    def wksp_job_status(self, wksp: str, jobkey: str) -> dict:
        '''GET ​/v0​/{workspace}​/job​/{jobKey} - Get job status

        :param wksp: str: workspace where job exists
        :param jobkey: str: unique id
        '''

        url = f'{self.api_version}{wksp}/job/{jobkey}?op=status'
        resp = self._fetch_json('get', url)
        return resp

    def wksp_job_stop(self, wksp: str, jobkey: str) -> dict:
        '''DELETE ​/v0​/{workspace}​/job​/{jobKey} -Stop a queued or running job

        :param wksp: str: workspace where job exists
        :param jobkey: str: unique id
        '''

        url = f'{self.api_version}{wksp}/job/{jobkey}'
        resp = self._fetch_json('delete', url)
        return resp

    def wksp_jobify(self, wksp: str, batch: dict, resourceConfig: str = None, tags: str = None) -> dict:
        '''POST /v0/{workspace}/jobBatch/jobify - batch queue many jobs

        Will create a job for each python module provided.

        :param batch: dict: list of py modules to run and their config
        :param resourceConfig: str: 3xs, 2xs, xs, s, m, l, xl, 2xl
        :param tags: str: earmark the job record
        :param timeout: int: max job runtime in secs
        :param wksp: str: workspace scope 

        INPUT DIRECTIVE
        :batch: dict: payload to send in body of the request
        :batchItems: list: find python modules to execute
        :pyModulePath: str: absolute file path of the python module to execute
        :commandArgs: str: arguments to pass to associated python module
        :timeout: int: max run time of the associated python module
        {"batchItems":[
            {
                "pyModulePath":"/projects/My Models/Transportation/France.py",
                "commandArgs":"diesel",
                "timeout": 100
            }]
        }
        '''

        self.__batch_input_validation(batch)
        url = f'{self.api_version}{wksp}/jobBatch/jobify'
        query = ''
        query += f'&resourceConfig={resourceConfig}' if resourceConfig else ''
        query += f'&tags={tags}' if tags else ''
        if len(query) > 0:
            url = f"{url}?{query.lstrip('&')}"

        resp = self._fetch_json('post', url, json=batch)
        return resp

    def wksp_jobify_findnrun(self, wksp: str, batch: dict, resourceConfig: str = None, tags: str = None) -> dict:
        '''POST /v0/{workspace}/jobBatch/jobify/searchNRun - Batch queue many jobs per search results

        :param batch: dict: list of py regex search terms to discover py modules to run
        :param resourceConfig: str: 3xs, 2xs, xs, s, m, l, xl, 2xl
        :param tags: str: earmark the job record
        :param timeout: int: max job runtime in secs
        :param wksp: str: workspace scope

        INPUT DIRECTIVE
        :batch: dict: payload to send in body of the request
        :batchItems: list: find python modules to execute
        :pySearchTerm: str: regex search file paths yields python modules to execute
        :commandArgs: str: arguments to pass into matching python modules
        :timeout: int: max run time for matching python modules
        {"batchItems":[
            {"pySearchTerm":"My Models/Transportation", "commandArgs":"", "timeout": 0},
            {"pySearchTerm":"network-\d{3,}", "commandArgs":"", "timeout": 0}
        ]}
        '''

        self.__batch_input_validation(batch, find=True)
        url = f'{self.api_version}{wksp}/jobBatch/jobify/searchNRun'
        query = ''
        query += f'&resourceConfig={resourceConfig}' if resourceConfig else ''
        query += f'&tags={tags}' if tags else ''
        if len(query) > 0:
            url = f"{url}?{query.lstrip('&')}"

        resp = self._fetch_json('post', url, json=batch)
        return resp

    def wksp_jobs(self, wksp: str, command: str = None, history: str = None, status: str = None, runSecsMin: int = None,
                      runSecsMax: str = None, tags: str = None) -> dict:
        '''GET ​/v0​/{workspace}​/jobs - List the jobs for a specific workspace

        :param wksp: str:  where your files live

        QUERYSTRING PARAMETERS
        :param command: str: run, presolve, run_custom, run_default, supplychain-3echelon, estimate, accelerate, supplychain-2echelon
        :param history: str: all, or n days ago
        :param runSecsMax: int: maximum runtime in secs
        :param runSecsMin: int: minimum runtime in secs
        :param status: str: done, error, submitted, starting, running, cancelled, stopped, cancelling, stopping
        :param tags: str: filter jobs where csv string matches
        '''

        url = f'{self.api_version}{wksp}/jobs'
        query = ''
        query += f'&command={command}' if command else ''
        query += f'&history={history}' if history else ''
        query += f'&status={status}' if status else ''
        query += f'&tags={runSecsMin}' if runSecsMin else ''
        query += f'&tags={runSecsMax}' if runSecsMax else ''
        query += f'&tags={tags}' if tags else ''
        if len(query) > 0:
            url = f"{url}?{query.lstrip('&')}"

        resp = self._fetch_json('get', url)
        return resp

    def wksp_jobs_stats(self, wksp: str, command: str = None, history: str = None, status: str = None, runSecsMin: int = None,
                      runSecsMax: str = None, tags: str = None) -> dict:
        '''GET ​/v0​/{workspace}​/jobs/stats - Get the stats for jobs for a specific workspace

        :param wksp: str:  where your files live

        QUERYSTRING PARAMETERS
        :param command: str: run, presolve, run_custom, run_default, supplychain-3echelon, estimate, accelerate, supplychain-2echelon
        :param history: str: all, or n days ago
        :param runSecsMax: int: maximum runtime in secs
        :param runSecsMin: int: minimum runtime in secs
        :param status: str: done, error, submitted, starting, running, cancelled, stopped, cancelling, stopping
        :param tags: str: filter jobs where csv string matches
        '''

        url = f'{self.api_version}{wksp}/jobs'
        query = ''
        query += f'&command={command}' if command else ''
        query += f'&history={history}' if history else ''
        query += f'&status={status}' if status else ''
        query += f'&tags={runSecsMin}' if runSecsMin else ''
        query += f'&tags={runSecsMax}' if runSecsMax else ''
        query += f'&tags={tags}' if tags else ''
        if len(query) > 0:
            url = f"{url}?{query.lstrip('&')}"

        resp = self._fetch_json('get', url)
        return resp

    def wksp_share_file(self, wksp: str, file_path: str, targetUsers: str) -> dict:
        '''POST ​/v0​/{workspace}​/file​/share - Share a specific file from a workspace to other users

        :param wksp: str: workspace to copy from
        :param file_path: str: file to share
        :param targetUsers: str: csv string of usernames or email
        '''

        dir_path, file_name = os.path.split(file_path)
        url = f'{self.api_version}{wksp}/file/share?sourceDirectoryPath={dir_path}&sourceFilename={file_name}&targetUsers={targetUsers}'
        resp = self._fetch_json('post', url)
        return resp

    def wksp_share_folder(self, wksp: str, dir_path: str, targetUsers: str, includeHidden = False) -> dict:
        '''POST ​/v0​/{workspace}​/folder/share - Share a specific subtree from a workspace to other users

        :param wksp: str: workspace to copy from
        :param dir_path: str: subtree to share
        :param targetUsers: str: csv list of usernames or email
        :param includeHidden: bool: include hidden files in folder, defaults to False
        '''

        url = f'{self.api_version}{wksp}/folder/share?sourceDirectoryPath={dir_path}&targetUsers={targetUsers}&includeHidden={includeHidden}'
        resp = self._fetch_json('post', url)
        return resp

if __name__ == '__main__':
    # legacy authentication
    # api = Api(**{'un': 'YOUR_USERNAME', 'pw': 'YOUR_PASSWORD'})
    
    # modern authentication
    api = Api(**{'auth_legacy': False, 'appkey': 'YOUR_APPLICATION_KEY', 'un': 'YOUR_USERNAME'})
    pass # set a breakpoint here
