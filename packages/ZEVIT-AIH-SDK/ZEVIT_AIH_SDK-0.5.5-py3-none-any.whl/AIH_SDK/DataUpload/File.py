import io
import pickle

from AIH_SDK.AIHExceptions import AIHException
from AIH_SDK.DataUpload.DataUploadObject import DataUploadObject
from PIL import Image


class File(DataUploadObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'Files'
        self._image_extensions = ['jpg', 'jpeg', 'png']

    
    def get(self, file_id:str=None, datatype_id:str=None):
        """
        get gets the file with the specific id or a list of files with the datatype_id.
        Exactly one of the ids should be stated. 
            If both None: Error will be raised.
            If both stated: Only file_id will be used.

        IN: file_id (str)     - The id of the file to get.
            datatype_id (str) - The id of the datatype to get a list of files from.

        OUT: self
        """

        if file_id:
            self.value = self._client._get(self._api, f'{self._endpoint}/{file_id}')
        elif datatype_id:
            self.value = self._client._get(self._api, f'{self._endpoint}', parameters=[('dataTypeId', datatype_id)])
        else:
            raise AIHException('file_id or datatype_id must be stated.')
        
        return self
    
        
            
    def download(self):
        f"""
        download create a generator that downloads the file or files if a list.

        OUT (generator) - A generator where each object is bytes for files. 
                          If file extension is in {self._image_extensions} the object will be a PIL Image.
        """

        if type(self.value) == dict:
            content = self._client._download_file(self.value["id"])

            if self.value['name'].split('.')[-1] in self._image_extensions:
                # If file is an image, set content to PIL.Image
                content = Image.open(io.BytesIO(content))

            elif self.value['name'].split('.')[-1] == 'pickle':
                # If file is a pickle, load it the type it represents
                content = pickle.loads(content)

            yield content

        elif type(self.value) == list:
            for val in self.value:
                content = self._client._download_file(val["id"])
                
                if val['name'].split('.')[-1].lower() in self._image_extensions:
                    # If file is an image, set content to PIL.Image
                    content = Image.open(io.BytesIO(content))

                elif val['name'].split('.')[-1] == 'pickle':
                    # If file is a pickle, load it the type it represents
                    content = pickle.loads(content)

                yield content
    

    def upload(self, file, datatype_id:str, name:str, exif:bytes=None):
        """
        To post the updates that have been made.
        IN: file              - The that should be uploaded.
            datatype_id (str) - The guid of the datatype that that the file should be upload as.
            name (str)        - The name of the file that should be uploaded. Should contain the file extention.
            exif (dict)       - Exif dictionary that is converted to bytes. Is used to set the metadata.

        OUT: self
        """
        
        fileextension = name.split('.')[-1]
        _file = io.BytesIO()
        
        if fileextension.lower() in self._image_extensions:
            if exif:
                file.save(_file, format='jpeg' if fileextension.lower() == 'jpg' else fileextension, exif=exif)
            else:
                file.save(_file, format='jpeg' if fileextension.lower() == 'jpg' else fileextension)

            _file.seek(0)
        else:
            _file = file
        
        response_json = self._client._upload_file(datatype_id, _file, name)
        self.value = response_json
        
        return self
    

    def upload_from_data(self, data:dict, datatype_id:str, name:str):
        """
        upload_from_data creates a file containing the data and uploads it.

        IN: data              - The data to create a file from and upload. Can e.g. be dict, list, strings etc.
            datatype_id (str) - The guid of the datatype that that the file should be upload as.
            name (str)        - The name of the file that should be uploaded. Should contain the file extention.

        OUR: self
        """
        f = io.BytesIO()
        pickle.dump(data, f)
        f.seek(0)

        return self.upload(f, datatype_id, name)

