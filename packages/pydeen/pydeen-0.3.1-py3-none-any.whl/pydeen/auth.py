from pydeen.types import Auth
from base64 import b64encode
import requests

class AuthBasic(Auth):
    def __init__(self):
        super().__init__()
        self.type = "pydeeen.AuthBasic"

    def set_basic_auth(self, user:str, password:str) -> bool:
        self._properties = {}
        self.set_property(Auth.AUTH_PROP_TYPE, Auth.AUTH_TYPE_BASIC)
        self.set_property(Auth.AUTH_PROP_USER, user)
        self.set_property(Auth.AUTH_PROP_PASS, password)
        return True

    def init_from_config(self, type, config) -> bool:
        if type == Auth.AUTH_TYPE_BASIC:
            self._properties = {}
            self.set_property(Auth.AUTH_PROP_TYPE, Auth.AUTH_TYPE_BASIC)
            self.set_property(Auth.AUTH_PROP_USER, config[Auth.AUTH_PROP_USER])
            self.set_property(Auth.AUTH_PROP_PASS, config[Auth.AUTH_PROP_PASS])
            return True
        else:
            return False      

    def get_username(self) -> str:
        if len(self._properties) > 0 and self.get_property(Auth.AUTH_PROP_TYPE) == Auth.AUTH_TYPE_BASIC:
            return self.get_property(Auth.AUTH_PROP_USER)
        else:
            return None

    def get_password(self) -> str:
        if len(self._properties) > 0 and self.get_property(Auth.AUTH_PROP_TYPE) == Auth.AUTH_TYPE_BASIC:
            return self.get_property(Auth.AUTH_PROP_PASS)
        else:
            return None

    def get_auth_for_request(self):
        if len(self._properties) > 0 and self.get_property(Auth.AUTH_PROP_TYPE) == Auth.AUTH_TYPE_BASIC:
            username = self.get_property(Auth.AUTH_PROP_USER)
            password = self.get_property(Auth.AUTH_PROP_PASS)
            
            if len(username) == 0 or len(password) == 0:
                return None 
            
            return (username,password)
        else:
            return None    

    def get_auth_for_requests_session(self):
        self.trace("set basic auth info as requests session")
        s = requests.Session()
        s.auth = (self.get_username(), self.get_password())
        return s


    def get_auth_headers(self) -> dict:
        if len(self._properties) > 0 and self.get_property(Auth.AUTH_PROP_TYPE) == Auth.AUTH_TYPE_BASIC:
            username = self.get_property(Auth.AUTH_PROP_USER)
            password = self.get_property(Auth.AUTH_PROP_PASS)
            
            if len(username) == 0 or len(password) == 0:
                return None 
            
            user_pass = f'{username}:{password}'
            basic_credentials = b64encode(user_pass.encode()).decode()
            return {'Authorization': f'Basic {basic_credentials}'}
        else:
            return None    
