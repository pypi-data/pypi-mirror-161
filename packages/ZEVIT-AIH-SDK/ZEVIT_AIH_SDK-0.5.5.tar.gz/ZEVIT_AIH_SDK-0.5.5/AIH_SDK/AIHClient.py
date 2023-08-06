import json
import time

import oauthlib
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

import AIH_SDK.AIHExceptions as AIHE

class AIHClient:
    """
    AIHClient is the client that authenticates and connects to the APIs for the given environment.
    """
    
    _instance = None
    
    @staticmethod
    def get_instance():
        if AIHClient._instance:
            return AIHClient._instance
        else:
            raise AIHE.AIHClientException('AIHClient has not been initialized yet.')
        
    
    def __init__(self, environment:str, client_id:str, client_secret:str, location:str):
        """
        IN: environment (str)   - Defines where the client should connect to.
            client_id (str)     - The id the client should connect with. 
            client_secret (str) - The secret the client should connect with.
            location (str)      - The location where the service is running (we, ne, ea, etc.)
        """
        AIHClient._instance = self
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.environment = environment
        self.location = location
        self.token_url = f'https://{self.environment}-idsvr-{self.location}-api.azurewebsites.net/connect/token'
        
        # Creates the client
        backend = BackendApplicationClient(client_id=self.client_id)
        self.client = OAuth2Session(client=backend)
        self._update_token()
    
    
    def _is_expired(self):
        """
        Checks if the Bearer token for the OAuth2 connection is expired
        """
        
        return time.time() > self.expires_at - 10000
  
    
    def _update_token(self):
        """
        Gets a new Bearer token.
        Raises Exceptions if the specified environment or client credentials are wrong.
        """
        
        try:
            self.client.token = self.client.fetch_token(token_url=self.token_url, client_id=self.client_id, client_secret=self.client_secret)
            self.expires_at = self.client.token['expires_at']
            
        except oauthlib.oauth2.rfc6749.errors.InvalidClientError:
            raise AIHE.AIHClientException('Could not get access token. Please check client_id and client_secret.')
        
        except oauthlib.oauth2.rfc6749.errors.MissingTokenError:
            raise AIHE.AIHClientException('Could not get token. Please check the token URL.')
     
        
    def _get(self, api:str, endpoint:str, parameters:list=[]):
        """
        Sends a HTTPS GET request for the given endpoint.
        Raises an error if HTTPS error occurs.
        
        IN: api (str)                  - Defines which API to use
            endpoint (str)             - Defines the endpoint send a GET request to.
            parameters (list of pairs) - list with the k,v pairs of parameters to include in the query.
        
        OUT: response (json) - A json object for the response
        """
        
        if(self._is_expired()):
            self._update_token()
        
        if parameters:
            print(parameters)
            params = '&'.join([f'{k}={v}' for k,v in parameters])
            url = f'https://{self.environment}-{api}-{self.location}-api.azurewebsites.net/{endpoint}?{params}'   
        else:
            url = f'https://{self.environment}-{api}-{self.location}-api.azurewebsites.net/{endpoint}'
        
        response = self.client.get(url)
                
        try:
            response_json = response.json()
        except:
            raise AIHE.AIHClientException(f'Cannot interpret response as JSON. API might be wrong.\nAPI was: {url}\n\nResponse was:\n{response.text}')
        
        if response.status_code >= 200 and response.status_code < 300:
            return response_json
        else:
            raise AIHE.AIHClientException(f'Could not get resource\n{response.text}')
        

    def _put(self, api:str, endpoint:str, data:dict):
        """
        Sends a HTTPS PUT request for the given endpoint.
        Raises an error if HTTPS error occurs.
        
        IN: api (str)      - Defines which API to use
            endpoint (str) - Defines the endpoint send a PUT request to.
            data (dict)    - The data it should send in the body. It gets converted to json.
        """
        
        if(self._is_expired()):
            self._update_token()
        
        url = f'https://{self.environment}-{api}-{self.location}-api.azurewebsites.net/{endpoint}' 
        headers = {"Content-Type": "application/json"}
        response = self.client.put(url=url, data=json.dumps(data), headers=headers)
        
        if response.status_code < 200 or response.status_code >= 300:
            if 'unauthorized' in response.text.lower():
                # If unauthorized, try to get new toke and try once more
                self._update_token()
                url = f'https://{self.environment}-{api}-{self.location}-api.azurewebsites.net/{endpoint}' 
                headers = {"Content-Type": "application/json"}
                response = self.client.put(url=url, data=json.dumps(data), headers=headers)

                if response.status_code < 200 or response.status_code >= 300:
                    raise AIHE.AIHClientException(f'PUT request failed: {response.status_code}\n{response.text}')
            else:
                raise AIHE.AIHClientException(f'PUT request failed: {response.status_code}\n{response.text}')
        
        
    def _post(self, api:str, endpoint:str, data:dict):
        """
        Sends a HTTPS POST request for the given endpoint.
        Raises an error if HTTPS error occurs.
        
        IN: api (str)      - Defines which API to use
            endpoint (str) - Defines the endpoint send a PUT request to.
            data (dict)    - The data it should send in the body. It gets converted to json.
            
        OUT: (json)        - The response from the server in a json object
        """
        
        if(self._is_expired()):
            self._update_token()
        
        url = f'https://{self.environment}-{api}-{self.location}-api.azurewebsites.net/{endpoint}' 
        headers = {"Content-Type": "application/json"}
        response = self.client.post(url=url, data=json.dumps(data), headers=headers)
        
        if response.status_code < 200 or response.status_code >= 300:
            if 'unauthorized' in response.text.lower():
                # If unauthorized, try to get new toke and try once more
                self._update_token()
                url = f'https://{self.environment}-{api}-{self.location}-api.azurewebsites.net/{endpoint}' 
                headers = {"Content-Type": "application/json"}
                response = self.client.post(url=url, data=json.dumps(data), headers=headers)

                if response.status_code < 200 or response.status_code >= 300:
                    raise AIHE.AIHClientException(f'POST request failed: {response.status_code}\n{response.text}\n\nData was:\n{data}')
            else:
                raise AIHE.AIHClientException(f'POST request failed: {response.status_code}\n{response.text}\n\nData was:\n{data}')
            
        try:
            return response.json()
        except:
            raise AIHE.AIHClientException(f'Cannot interpret response as JSON. API might be wrong.\nAPI was: {url}\n\nResponse was:\n{response.text}')
            
            
    def _delete(self, api:str, endpoint:str, id:str=None):
        """
        Sends a HTTPS DELETE request for the given endpoint.
        Raises an error if HTTPS error occurs.
        
        IN: api (str)      - Defines which API to use
            endpoint (str) - Defines the endpoint send a GET request to.
        """
        if(self._is_expired()):
            self._update_token()
        if id == None: 
            url = f'https://{self.environment}-{api}-{self.location}-api.azurewebsites.net/{endpoint}'
        else: 
            url = f'https://{self.environment}-{api}-{self.location}-api.azurewebsites.net/{endpoint}/{id}'        
        response = self.client.delete(url)
        
        if response.status_code < 200 or response.status_code >= 300:
            if 'unauthorized' in response.text.lower():
                # If unauthorized, try to get new toke and try once more
                self._update_token()
                url = f'https://{self.environment}-{api}-{self.location}-api.azurewebsites.net/{endpoint}/{id}'        
                response = self.client.delete(url)

                if response.status_code < 200 or response.status_code >= 300:
                    raise AIHE.AIHClientException(f'DELETE request failed: {response.status_code}\n{response.text}')
            else:
                raise AIHE.AIHClientException(f'DELETE request failed: {response.status_code}\n{response.text}')
        
            
    def _download_file(self, file_id:str):
        """
        download_file downloads the file from DataUpload API.
        
        IN: file_id (str) - The id for the file to download.
        
        OUT: (content) - The response content.
        """
        
        if(self._is_expired()):
            self._update_token()
        
        url = f'https://{self.environment}-du-{self.location}-api.azurewebsites.net/files/{file_id}/Data'
        response = self.client.get(url)

        return response.content

        
    def _upload_file(self, datatype_id:str, file, name:str):
        """
        upload_file uploads a file for a DataType to the DataUpload API.

        IN: datatype_id (str) - The id of the DataType to uplaod the file to.
            file (bytes)      - The bytes for the file to upload.
            name (str)        - The name the file should be stored as. The name must include the file extension.

        OUT: (json) - The json response
        """

        if(self._is_expired()):
            self._update_token()
        
        # Get object owner for file
        user = User().get(parameters=[('keyword', self.client_id)])

        fileextension = name.split('.')[-1]
        url = f'https://{self.environment}-du-{self.location}-api.azurewebsites.net/Files'
        files = {
            'Id' : (None, ''),
            'DataTypeId' : (None, datatype_id),
            'ObjectOwnerId' : (None, user.get_value('id', -1)),
            'File' : (name, file, f'image/{fileextension}')
        } 
        
        response = self.client.post(url=url, files=files)
        
        return response.json()


    def _download_media(self, container:str, name:str):
        """
        To get download a file from the media objects.
        IN: container (str) - To specify the type of file to donwload e.g. image
            name (str) - To specify the name of the file to download
            
        OUT: the content of the downloaded file
        """
        if(self._is_expired()):
            self._update_token()
        
        url = f'https://{self.environment}-aih-{self.location}-api.azurewebsites.net/api/v1/multimedia/{container}/{name}'        
        response = self.client.get(url)
                
        return response.content


    def _upload_media(self, container, file, name):
        """
        upload_file uploads a file to a data type.

        IN: datatype_id (str) - The id of the DataType to uplaod the file to.
            file (bytes)      - The bytes for the file to upload.
            name (str)        - The name the file should be stored as. The name must include the file extension.

        OUT: (json) - The json response
        """
        
        if(self._is_expired()):
            self._update_token()
        
        
        url = f'https://{self.environment}-aih-{self.location}-api.azurewebsites.net/api/v1/media'
        
        files = {'file' : (name, file)}
        
        response = self.client.post(url=url, files=files)
        
        return response.json()
        

from AIH_SDK.Identity import User