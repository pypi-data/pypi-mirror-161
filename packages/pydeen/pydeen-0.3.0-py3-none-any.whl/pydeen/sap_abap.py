"""
    SAP NetWeaver ABAP Stack
"""

from sympy import Q
from pydeen.types import Backend, Connector, Auth, Result
from pydeen.http import HTTPConnector, HTTPBackend, HTTPRequest
from pydeen.menu import  MenuSelection, MenuAction, UserInput

import requests


class SAPAbapHttpBackend(HTTPBackend):
    def __init__(self, name:str, url:str, client:str, auth:Auth=None) -> None:
        super().__init__(name, url, auth)
        self.set_property(Backend.BACKEND_PROP_TENANT, client)
        self.type = "pydeen.SAPAbapHttpBackend"

    def get_client(self):
        return self.get_property(Backend.BACKEND_PROP_TENANT)     
    

class SAPAbapODataConnector(HTTPConnector):
    
    # static constants
    #ODATA_SERVICE_NAME      = "ID"
    ODATA_SERVICE_NAME      = "TechnicalServiceName"
    ODATA_SERVICE_DESC      = "Description"

    ODATA_PARAM_TOP         = "$top"
    ODATA_PARAM_FORMAT      = "$format"
    ODATA_PARAM_FILTER      = "$filter"
    ODATA_PARAM_SAPCLIENT   = "sap-client"

    MENU_FIND_ENDPOINTS     = "find_endpoints"
    MENU_FIND_ENTITIES      = "find_entities"
    MENU_ENTITY_SELECT      = "select_entity"
    MENU_REQUEST_CONFIGURE  = "configure_request"
    MENU_REQUEST_METADATA   = "request_metadata"
    MENU_RESULT_RAW         = "result_raw"
    MENU_RESULT_PANDAS      = "result_pandas"
    MENU_RESET              = "reset"
    
    def __init__(self, backend:Backend=None, url_or_endpoint:str=""):
        super().__init__(backend, url_or_endpoint)
        self.type = "pydeen.SAPAbapODataConnector"
        self.endpoints = None
        self.menu_endpoint = None
        self.menu_entity   = None
        self.menu_result   = None
        self.menu_request  = None
        self.menu_request_params = {}

    def menu_action_reset(self):
        self.menu_result = None
        self.menu_endpoint = None
        self.menu_entity = None
        self.menu_request = None
        self.menu_request_params = {}
        print("Menu context cleared.")


    def menu_action_select_entity(self):
        self.menu_result = None
        if self.menu_endpoint != None and self.menu_entity != None and self.menu_request != None:
            #request = SAPAbapODataRequest(self, self.menu_entity, self.menu_endpoint)
            self.menu_result = self.menu_request.select(add_params=self.menu_request_params)
            if self.menu_result != None:
                print(f"Endpoint {self.menu_endpoint} entity {self.menu_entity} selected - {self.menu_result.get_count()} records")   
                print("Entity Columns:",self.menu_result.get_columns())            
            else:
                print("No or wrong result")
        else:
            print("Wrong context to select entity")

    def menu_configure_request(self):
        print("Configure Request Params")
        # max rows
        if SAPAbapODataConnector.ODATA_PARAM_TOP in self.menu_request_params:
            max_rows_str = str(self.menu_request_params[SAPAbapODataConnector.ODATA_PARAM_TOP])
        else:
            max_rows_str = "1000"

        max_rows = UserInput("Change parameter max_rows", max_rows_str).get_input_int(min=1)
        self.menu_request_params[SAPAbapODataConnector.ODATA_PARAM_TOP] = str(max_rows)
        print("Parameter max_rows set to", max_rows)

         # odata filter
        if SAPAbapODataConnector.ODATA_PARAM_FILTER in self.menu_request_params:
            odata_filter = str(self.menu_request_params[SAPAbapODataConnector.ODATA_PARAM_FILTER])
        else:
            odata_filter = None

        odata_filter_new = UserInput("Change parameter OData Filter", odata_filter).get_input(empty_allowed=True)
        if odata_filter_new != None and odata_filter_new != "":
            self.menu_request_params[SAPAbapODataConnector.ODATA_PARAM_FILTER] = odata_filter_new
            print("Parameter OData filter set to", odata_filter_new)

    def menu_find_entities(self):
        if self.menu_endpoint == None:
            print("Missing endpoint")
        else:    
            entities = self.get_entities(self.menu_endpoint)
            if entities == None or len(entities) == 0:
                print("No entities found for endpoint", self.menu_endpoint)
            else:
                entries = {}
                for key in entities:
                    entries[key] = key

                #show menu
                valid = True
                while valid == True:
                    action = MenuSelection("Select Entity", entries, False, True).show_menu()
                    if action.is_cancel_entered() == True:
                        valid = False
                    elif action.is_selected() == True:
                        self.menu_entity = action.get_selection()
                        self.menu_request = SAPAbapODataRequest(self, self.menu_entity, self.menu_endpoint)
                        print(f"Entity {self.menu_entity} selected")

                        metadata_xml = self.menu_request.get_metadata_xml()
                        if metadata_xml != None:
                            print(f"Metadata for endpoint {self.menu_endpoint} loaded")
                        else:
                            print(f"Metadata for endpoint {self.menu_endpoint} not available")    
                        
                        valid = False

    def menu_find_endpoints(self):
        endpoints = self.find_endpoints()
        if endpoints == None or len(endpoints) == 0:
            print("No endpoints found or errors occured")
        else:
            # build entries
            entries = {}
            for key in endpoints:
                entries[key] = f"{key} - {endpoints[key]}"

            #show menu
            valid = True
            while valid == True:
                action = MenuSelection("Select OData Endpoint", entries, False, True).show_menu()
                if action.is_cancel_entered() == True:
                    valid = False
                elif action.is_selected() == True:
                    self.menu_action_reset()
                    self.menu_endpoint = action.get_selection()
                    print(f"Endpoint selected: ", self.menu_endpoint)
                    valid = False
                    

    def menu(self):        
        valid = True
        while valid == True:
            
            # build main menu    
            entries = {}
            entries[SAPAbapODataConnector.MENU_FIND_ENDPOINTS] = "Search OData endpoints in ABAP backend"

            if self.menu_endpoint != None:
                entries[SAPAbapODataConnector.MENU_FIND_ENTITIES] = f"Get entities in OData endpoint {self.menu_endpoint}"

                if self.menu_request != None:
                    entries[SAPAbapODataConnector.MENU_REQUEST_CONFIGURE] = f"Configure entity selection request for {self.menu_entity} in endpoint {self.menu_endpoint}"
                    if self.menu_request.is_metadata_available() == True:
                        entries[SAPAbapODataConnector.MENU_REQUEST_METADATA] = f"Display metadata xml for endpoint {self.menu_endpoint}"

                if self.menu_entity != None:
                    entries[SAPAbapODataConnector.MENU_ENTITY_SELECT] = f"Select entity {self.menu_entity} in OData endpoint {self.menu_endpoint}"

            if self.menu_result != None:
                    entries[SAPAbapODataConnector.MENU_RESULT_RAW] = f"Display current result of entity {self.menu_entity} in OData endpoint {self.menu_endpoint} as raw data"
                    #entries[SAPAbapODataConnector.MENU_RESULT_PANDAS] = f"Display current result of entity {self.menu_entity} in OData endpoint {self.menu_endpoint} as pandas dataframe"

            entries[SAPAbapODataConnector.MENU_RESET] = "Reset menu context"

            # show menu            
            action = MenuSelection("SAP NetWeaver ABAP OData Connector - Menu", entries, True, False).show_menu()
            if action.is_quit_entered():
                valid = False
            else:
                selected = action.get_selection()
                if selected == SAPAbapODataConnector.MENU_FIND_ENDPOINTS:
                    self.menu_find_endpoints()
                elif selected == SAPAbapODataConnector.MENU_FIND_ENTITIES:
                    self.menu_find_entities()
                elif selected == SAPAbapODataConnector.MENU_REQUEST_CONFIGURE:
                    self.menu_configure_request()
                elif selected == SAPAbapODataConnector.MENU_ENTITY_SELECT:
                    self.menu_action_select_entity()
                elif selected == SAPAbapODataConnector.MENU_REQUEST_METADATA:
                    print(self.menu_request.get_metadata_xml())
                elif selected == SAPAbapODataConnector.MENU_RESULT_RAW:
                    print(self.menu_result.get_result_raw())
                elif selected == SAPAbapODataConnector.MENU_RESULT_PANDAS:
                    pass
                elif selected == SAPAbapODataConnector.MENU_RESET:
                    self.menu_action_reset()
                else:
                    print("unknown menu action")
    def get_endpoints(self, max_results:int=10000): #searchFor:str=None, 
        # check cached
        if self.endpoints != None:
            return self.endpoints
        
        # build a new request
        request = self.create_request()

        params = {}
        params[SAPAbapODataConnector.ODATA_PARAM_TOP] = str(max_results)
        params[SAPAbapODataConnector.ODATA_PARAM_FORMAT] = "json"

        client  = self.backend.get_client()
        if client != None:
            params[SAPAbapODataConnector.ODATA_PARAM_SAPCLIENT] = client

        #if searchFor != None and searchFor != "":
        #    params["$filter"] = f"contains(Description,'{searchFor}') or contains(SrvIdentifier,'{searchFor}')"

        self.trace("Call sap for OData Endpoints")
        http_code = request.get("/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection", params)
        if http_code < 200 or http_code > 299:
            self.trace("invalid answer - return code") 
            return None
            
        json = request.get_response_json()
        if json == None:
            self.trace("invalid answer - no json") 
            return None

        records = json["d"]["results"]
        if records == None:
            self.trace("invalid answer - no results") 
            return None
        else:
            self.endpoints = records
            return records
        
    def find_endpoints(self, searchFor:str=None, max_results:int=10000) -> dict:
        result = {}
        records = self.get_endpoints(max_results)
        if records != None:
            for record in records:
                name = record[SAPAbapODataConnector.ODATA_SERVICE_NAME]
                desc = record[SAPAbapODataConnector.ODATA_SERVICE_DESC]
                
                serviceURL = record['ServiceUrl']
                if serviceURL != None and serviceURL.find('/sap/opu/odata') > 0 and serviceURL.find(name) < 0:
                    serviceURLParts = serviceURL.split("/sap/opu/odata")
                    name = serviceURLParts[1]

                if searchFor == None or name.find(searchFor) >= 0 or desc.find(searchFor) >= 0:
                    result[name] = desc
        
        return result

    def get_entities(self, endpoint):         
        # build a new request
        request = self.create_request()

        params = {}
        params[SAPAbapODataConnector.ODATA_PARAM_FORMAT] = "json"

        client  = self.backend.get_client()
        if client != None:
            params[SAPAbapODataConnector.ODATA_PARAM_SAPCLIENT] = client

        self.trace("Call sap for OData Endpoint Entities")

        url = f"/sap/opu/odata/sap/{endpoint}/"
        if endpoint.find("/") == 0:
            url = f"/sap/opu/odata{endpoint}/"

        http_code = request.get(url, params)
        if http_code < 200 or http_code > 299:
            self.trace("invalid answer - return code") 
            return None

        json = request.get_response_json()
        if json == None:
            self.trace("invalid answer - no json") 
            return None

        records = json["d"]["EntitySets"]
        if records == None:
            self.trace("invalid answer - no results") 
            return None
        else:
            return records


class SAPAbapODataRequest(HTTPRequest):
    def __init__(self, connector: Connector, entity:str, endpoint:str=None) -> None:
        super().__init__(connector)
        self.type = "pydeen.SAPAbapODataRequest"
        self.connector:SAPAbapODataConnector = connector
        self.endpoint = endpoint
        self.entity   = entity
        self.odata_metadata = None
        self.odata_metadata_xml = None

    def select(self, max_rows:int=1000, odataFilter:str=None, add_params:dict=None) -> Result:
        # prepare params
        if add_params != None:
            params = add_params
        else:
            params = {}    

        # main params for sap request
        params[SAPAbapODataConnector.ODATA_PARAM_FORMAT] = "json"
        client  = self.connector.backend.get_client()
        if client != None:
            params[SAPAbapODataConnector.ODATA_PARAM_SAPCLIENT] = client

        # additional params 
        if not SAPAbapODataConnector.ODATA_PARAM_TOP in params and max_rows > 0:
            params[SAPAbapODataConnector.ODATA_PARAM_TOP] = str(max_rows)

        if not SAPAbapODataConnector.ODATA_PARAM_FILTER in params and odataFilter != None:
            params[SAPAbapODataConnector.ODATA_PARAM_FILTER] = odataFilter

        # prepare url prefix
        url_prefix = "/sap/opu/odata/sap/"
        if self.endpoint != None and self.endpoint.find("/") == 0:
            url_prefix = "/sap/opu/odata"

        # prepare request and execute
        if self.endpoint == None or self.endpoint == "":
            url = f"{url_prefix}{self.entity}/"
        else:
            url = f"{url_prefix}{self.endpoint}/{self.entity}/"

        request = self.connector.create_request()
        http_code = request.get(url, params)
        if http_code < 200 or http_code > 299:
            self.trace("invalid answer - return code") 
            return None

        # process result
        json = request.get_response_json()
        if json == None:
            self.trace("invalid answer - no json") 
            return None

        records = json["d"]["results"]
        if records == None:
            self.trace("invalid answer - no results") 
            return None
        else:
            odata_type = None
            self.odata_metadata = None
            result = []
            for record in records:
                result_rec = {}
                for attr_name in record.keys():
                    if attr_name == "__metadata":
                        if odata_type == None:
                            odata_type = record["__metadata"]["type"]
                        if self.odata_metadata == None:
                            self.odata_metadata = record["__metadata"]    
                    else:
                        attr_value = record[attr_name]
                        result_rec[attr_name] = attr_value    
                result.append(result_rec);        

        return SAPAbapODataResult(self, result, odata_type) 


    def get_metadata_xml(self, add_params:dict=None) -> str:
        if self.odata_metadata_xml != None:
            return self.odata_metadata_xml

        if self.endpoint == None:
            return None
        
        # prepare params
        if add_params != None:
            params = add_params
        else:
            params = {}    

        # main params for sap request
        client  = self.connector.backend.get_client()
        if client != None:
            params[SAPAbapODataConnector.ODATA_PARAM_SAPCLIENT] = client


        # prepare url prefix
        url_prefix = "/sap/opu/odata/sap/"
        if self.endpoint != None and self.endpoint.find("/") == 0:
            url_prefix = "/sap/opu/odata"

        # prepare request and execute
        url = f"{url_prefix}{self.endpoint}/$metadata"
        
        request = self.connector.create_request()
        http_code = request.get(url, params)
        if http_code < 200 or http_code > 299:
            self.trace("invalid answer - return code") 
            return None

        # process result
        xml = request.get_response_text()
        if xml == None:
            self.trace("invalid answer - no xml answer") 
            return None

        # result
        self.odata_metadata_xml = xml
        return xml

    def is_metadata_available(self) -> bool:
        if self.odata_metadata_xml != None:
            return True
        else:
            return False        
        

class SAPAbapODataResult(Result):
    def __init__(self, request, result, odata_type:str) -> None:
        super().__init__(result)
        self.type = "pydeen.SAPAbapODataResult"
        self.request = request
        self.odata_type = odata_type