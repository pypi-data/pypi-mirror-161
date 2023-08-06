
# import sub modules
import imp
import pydeen.core as core
import pydeen.types as types
import pydeen.menu as menu
import pydeen.service as service
import pydeen.auth as auth
import pydeen.pyodata as pyodata
import pydeen.sap_abap as sap_abap

# import classes and main types
from pydeen.core import PyDEEN

from pydeen.types import Auth
from pydeen.types import Backend
from pydeen.types import Connector
from pydeen.types import Request
from pydeen.types import Result

# http support
from pydeen.http import HTTPBackend
from pydeen.http import HTTPConnector
from pydeen.http import HTTPRequest

# service support 
from pydeen.service import Service
from pydeen.service import ServiceContext
from pydeen.service import ServiceAction
from pydeen.service import ServiceActionCommands
from pydeen.service import ServiceCommand


# local service suppoer
from pydeen.wsocket import WebSocketService

def menu():
    print("menu not implemented yet")
    