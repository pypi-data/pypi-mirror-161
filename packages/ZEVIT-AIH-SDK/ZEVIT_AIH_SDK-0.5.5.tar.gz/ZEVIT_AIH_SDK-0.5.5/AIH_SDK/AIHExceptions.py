class AIHClientException(Exception):
    
    def __init__(self, message='Something went wrong'):
        self.message = message
        super().__init__(self.message)
 

       
class AIHException(Exception):

    def __init__(self, message='Something went wrong'):
        self.message = message
        super().__init__(self.message)