from AIH_SDK.DataProcessing.DataProcessingObject import DataProcessingObject


class JobConfiguration(DataProcessingObject):
    
    def __init__(self):
        super().__init__()
        self._endpoint = 'JobConfigurations'
    
    
    def run(self, jobconfiguration_id:str=None, additional_env_var:dict=None):
        """
        To run the job configuration.
        IN: jobconfiguration_id (str) - the id of the JobConfiguration to run. If left out it will use the id from self.value if it is a dict.
        """
        jobconfiguration_id = jobconfiguration_id if jobconfiguration_id else self.value['id']
        data = {'runOptions' : additional_env_var} if additional_env_var else {'runOptions' : {}}
        
        response = self._client._post(self._api, f'Jobs/Execution/{jobconfiguration_id}', data)
        
        return response['jobId']


    def get_jobs(self, jobconfiguration_id:str=None, parameters:dict={}):
        """
        to get the jobs that have tried to run this jobconfiguration     
        IN: jobconfiguration_id (str) - the id of the JobConfiguration to run. If left out, it will use the id from self.value if it is a dict.
        OUT (list) - A list of json objects containing the job information of the jobs that have been ran for the jobconfiguration id.
        """

        if not 'configurationId' in parameters:
            parameters['configurationId'] =  self.value['id']

        jobs = self._client._get(self._api, 'Jobs', parameters)
        
        return jobs


    def amend_environment_variables(self, variables:dict):
        """
        amend_environment_variables amend environment variables to the runOptions.

        IN: variables (dict) - A dictionary with the environment varaibles to amend.
                               TODO: If key already exists as environment variable it will be overridden.
        """

        variables_str = ' '.join([f'-e {k}={v}' for k,v in variables.items()])

        if type(self.value) == list:
            for val in self.value:
                new_runOptions = ' '.join([val['runOptions'], variables_str])
                val['runOptions'] = new_runOptions

        elif type(self.value) == dict:
            new_runOptions = ' '.join([self.value['runOptions'], variables_str])
            self.value['runOptions'] = new_runOptions
        
        return self
