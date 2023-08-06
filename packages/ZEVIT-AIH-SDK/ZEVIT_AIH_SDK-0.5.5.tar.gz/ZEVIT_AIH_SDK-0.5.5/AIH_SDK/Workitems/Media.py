import io

import AIH_SDK.AIHExceptions as AIHE
from AIH_SDK.v1Object import v1Object
from PIL import Image


class Media(v1Object):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'api/v1/media'
        self._valid_filetypes = ['image', 'document']
    

    def get(self, id:str=None):
        """
        To get a list of all media or a specific media.
        Result is set as self.value
        """
        
        if id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{id}')
            self.value = self.value['mediaItem']
        else:
            self.value = self._client._get(self._api, self._endpoint)
            self.value = self.value['mediaItems']
        
        return self
            
    
    def download(self, name:str=None, filetype:str=None):
        f"""
        To download the image with a given name.
        IN: name - The name of the media it should get. If not specified or None, it will use the name of the object if it is a dict. 
            filetype - the type of file to be downloaded. If not specified it will use the continer name of the object. Must  be one of the following {self._valid_filetypes}
        
        OUT: (generator) A generator with the downloaded media as an PIL Image if filetype is 'image'. If filetype is 'document' it will output file content.
        """
        
        if type(self.value) == dict:
            if not filetype:
                filetype = self.value['container']
            if not name:
                name = self.value['name']
        
            content = self._client._download_media(filetype, name)
            
            if filetype == 'image':
                file = Image.open(io.BytesIO(content))
            elif filetype == 'document':
                file = content
            else:
                raise AIHE.AIHException(f'filetype was {filetype}, but must be one of the following {self._valid_filetypes}')
            
            yield file
        
        elif type(self.value) == list:
            for media in self.value:
                filetype = media['container']
                name = media['name']
                
                content = self._client._download_media(filetype, name)
                
                if filetype == 'image':
                    file = Image.open(io.BytesIO(content))
                elif filetype == 'document':
                    file = content
                else:
                    raise AIHE.AIHException(f'filetype was {filetype}, but must be one of the following {self._valid_filetypes}')
                        
                yield file
        
    
    
    def upload(self, file, name:str, filetype:str, exif:bytes=None):
        f"""
        To post the updates that have been made.
        IN: file     - The that should be uploaded
            name     - The name of the file that should be uploaded. Should contain the file extention
            filetype - The type of the file that should be uploaded. Should be one of the following {self._valid_filetypes}.
            exif     - Exif dictionary that is converted to bytes. Is used to set the metadata.
        """
        
        fileextension = name.split('.')[-1]
        _file = io.BytesIO()
        
        if filetype == 'image':
            if exif:
                file.save(_file, format='jpeg' if fileextension.lower() == 'jpg' else fileextension, exif=exif)
            else:
                file.save(_file, format='jpeg' if fileextension.lower() == 'jpg' else fileextension)

            _file.seek(0)
        elif filetype == 'document':
            _file = file
        else:
            raise AIHE.AIHException(f'filetype was {filetype}, but must be one of the following {self._valid_filetypes}')
        
        response_json = self._client._upload_media(filetype, _file, name)
        self.value = response_json['mediaItem']
        
        return self
    

    def get_keys(self):
        return ['id', 'name', 'displayName', 'dbStatus', 'type', 'container']
