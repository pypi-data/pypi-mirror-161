"""
    SAP NetWeaver OData Connector
"""

from pydeen.types import Backend
from pydeen.types import Connector
from pydeen.http import HTTPConnector
from pydeen.http import HTTPRequest

import requests



class SAPNwODataRequest(HTTPRequest):
 def __init__(self, connector: Connector, entity_name:str, endpoint:str=None) -> None:
        super().__init__(connector)
        self.type = "pydeen.SAPNwODataRequest"
        self.connector:SAPNwODataConnector = connector
        self.endpoint = endpoint
        self.entity_name   = entity_name
        self.entity = self.connector.get_entity(entity_name, endpoint=endpoint)
        

class SAPNwODataConnector(HTTPConnector):
    def __init__(self, backend:Backend=None, url_or_endpoint:str=""):
        super().__init__(backend, url_or_endpoint)
        self.type = "pydeen.SAPNwODataConnector"
        self.endpoints = {}

    #def find_entities(self, searchFor=None, max_results=1000, )