
from pydeen.types import Backend
from pydeen.types import Connector
from pydeen.http import HTTPConnector
from pydeen.http import HTTPRequest

import pyodata
import requests

from pyodata.client import Client
from pyodata.v2.service import EntitySetProxy

class ODataV2Request(HTTPRequest):
 def __init__(self, connector: Connector, entity_name:str, endpoint:str=None) -> None:
        super().__init__(connector)
        self.type = "pydeen.ODataV2Request"
        self.connector:ODataV2Connector = connector
        self.endpoint = endpoint
        self.entity_name   = entity_name
        self.entity = self.connector.get_entity(entity_name, endpoint=endpoint)
        

class ODataV2Connector(HTTPConnector):
    def __init__(self, backend:Backend=None, url_or_endpoint:str=""):
        super().__init__(backend, url_or_endpoint)
        self.type = "pydeen.ODataV2Connector"
        self.endpoints = {}

    def get_endpoint(self, endpoint:str=None) -> Client:
        epname = endpoint
        if epname == None or epname == "":
            epname = "*"
        self.trace(f"OData Endpoint used: {epname}")

        if epname in self.endpoints.keys():
            return  self.endpoints[epname]

        url = self.build_url(endpoint)    
        self.trace(f"ODATA URL: {url}")
        
        session = requests.Session()
        if self.get_backend().is_auth_info_available() == True:
            session = self.get_backend().get_auth_info().get_auth_for_requests_session()
        
        client = pyodata.Client(url, session)
        
        self.endpoints[epname] = client
        self.trace(f"OData endpoint {epname} initialized")
        return client    

    def get_entity_sets(self, endpoint:str=None) -> list:
        result = []
        client = self.get_endpoint(endpoint)
        
        if client != None: 
            for entity_set in client.schema.entity_sets:
                result.append(entity_set.name)
        return result

    def get_entity_set(self, entity_name:str, endpoint:str=None) -> EntitySetProxy:
        # check endpoint first
        endpoint = self.get_endpoint(endpoint)
        if endpoint == None:
            return None

        # get entity instance from endpoint
        result = endpoint.entity_sets._entity_sets[entity_name] 
        if result == None:
            self.error(f"unknown entity {entity} in endpoint {endpoint}")
        return result    

    # def new_request(self, entity_name:str, endpoint:str=None) -> ODataV2Request:
    #     # check endpoint first
    #     endpoint = self.get_endpoint(endpoint)
    #     if endpoint == None:
    #         return None
        
    #     # get odata entity
    #     if entity_name not in self.get_entities(endpoint):
    #         self.error(f"unknown entity {entity} in endpoint {endpoint}")
    #         return None

    #     result = ODataV2Request(self, entity_name, endpoint)
    #     return result
