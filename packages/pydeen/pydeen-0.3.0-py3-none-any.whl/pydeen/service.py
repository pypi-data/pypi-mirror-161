import platform
import random
import json

from pydeen.types import Base
from pydeen.types import Backend

class ServiceContext(Base):
    def __init__(self):
        super().__init__()
        self.type = "pydeen.ServiceContext"
        self.trace_on = True
        self.actions = []
        self.groups = []
        self.commands = {}        
        self.client_id = ""
        self.ext_client_id = ""
        self.restart_mode = True
        self.restart_wait = 5
        self.restart_count = 0

    def run(self) -> bool:
        return False

    def run_async(self) -> bool:
        return False

    def start(self) -> bool:
        return False

    def stop(self, restart:bool=False) -> bool:
        return False

    def destroy(self):
        return True             

    def send_text(self, text:str) -> bool:
        return False             

    def set_client_id(self, client_id):
        self.client_id = client_id

    def get_client_id(self) -> str:
        return self.client_id

    def generate_client_id(self, prefix="", postfix="") -> str:
        
        hostname = platform.node()
        append = postfix
        if append == "":
            append = str(random.randint(0, 99999999))

        if prefix == "":
            return f"{self.type}:{hostname}:{append}"
        else:
            return f"{prefix}:{hostname}:{append}"        

    def is_valid_client_id(self, receivers:str) -> bool:
        if receivers == None or receivers == "" or receivers == "*" or receivers == "[]":
            return True
        if len(self.client_id) > 0 and receivers.find(self.client_id) >= 0:
            return True
        if len(self.ext_client_id) > 0 and receivers.find(self.ext_client_id) >= 0:
            return True
        if len(self.groups) > 0:
            for group in self.groups:
                if receivers.find(group) > 0:
                    return True
        return False

    def get_registered_commands(self) -> list:
        return self.commands

    def get_count_registered_commands(self) -> int:
        return len(self.commands)

    def get_registered_actions(self) -> list:
        return self.actions

    def get_count_registered_actions(self) -> int:
        return len(self.actions)

    def trace(self, msg):
        if self.trace_on == True:
            print(msg)

    def error(self, msg):
        print("ERROR:", msg)


class ServiceAction(Base):
    """ 
        Abstract service action - to be used to incoming messages
    """ 
    def __init__(self):
        super().__init__()
        self.type = "pydeen.ServiceAction"

    def parse(self, payload:str) -> bool:
        """
            check if an incoming service message is valid for this action
        """
        return False

    def handle(self, payload:str, service:ServiceContext) -> bool:
        """
            handle an service messsage checked before by parse()
        """
        service.trace(f"< method handle not redefined in {type(self)}")
        return False

class ServiceActionCommands(ServiceAction):
    
    SERVICE_CMD_RESPONSE_SUFFIX = "-response" 
    
    def __init__(self):
        super().__init__()
        self.type = "pydeen.ServiceActionDefault"
        self.separator = "::"
        self.echo = False

    
    def init_default_commands(self, service:ServiceContext, echo=True) -> bool:
        self.echo = echo
        return True

    def parse(self, payload) -> bool:
        if self.has_separator(payload) == True:
            return True
        else:
            if payload.find(" ") == 0 or payload.find("{") == 0 or payload.find("[") == 0:
                return False
            else:
                return True

    def handle_quit(self, payload, service:ServiceContext) -> bool:
        self.trace("< QUIT COMMAND ARRIVED")
        service.stop(restart=False)
        return True                

    def handle_restart(self, payload, service:ServiceContext) -> bool:
        self.trace("< RESTART COMMAND ARRIVED")
        service.stop(restart=True)
        return True                

    def handle_connected(self, payload, service:ServiceContext) -> bool:
        if self.has_separator(payload) == True:
            parts = payload.split(self.separator)
            service.ext_client_id = parts[0]
        else:
            service.ext_client_id = payload
        service.trace(f"< external client id registered: '{ service.ext_client_id }'")    
        return True

    def handle_echo(self, payload, service:ServiceContext) -> bool:
        lv_message = f"echo{ServiceActionCommands.SERVICE_CMD_RESPONSE_SUFFIX}{ self.separator }{ service.client_id }{ self.separator}{ payload }"
        service.send_text(lv_message)
        return True

    def handle_ping(self, payload, service:ServiceContext) -> bool:
        service.send_text(f"ping{ServiceActionCommands.SERVICE_CMD_RESPONSE_SUFFIX}{ self.separator }{ service.client_id } is alive")
        return True

    def handle_info(self, payload, service:ServiceContext) -> bool:
        node = platform.uname()
    
        answer = {}
        answer["system"] = node[0]
        answer["hostname"] = node[1]
        answer["release"] = node[2]
        answer["version"] = node[3]
        answer["maschine"] = node[4]
        answer["processor"] = node[5]
 
        service.send_text(f"info{ServiceActionCommands.SERVICE_CMD_RESPONSE_SUFFIX}{ self.separator }{ service.client_id }{ self.separator }{answer}")
        return True

    def handle_message(self, payload, service:ServiceContext) -> bool:
        print(f"\aMessage: {payload}")
        return True

    def handle(self, payload, service:ServiceContext) -> bool:
        # prepare    
        command = payload
        my_payload = ""
        my_command = ""
        receivers = ""
                
        parts = payload.split(self.separator)
        len_parts = len(parts)
        service.trace(f"< handle payload '{payload}' arrived in {type(self)} with {len_parts} parts of message")

        if len_parts == 0:
            return False
        elif len_parts == 1:
            my_command = parts[0].lower()
        elif len_parts == 2:
            my_command = parts[0].lower()
            my_payload = parts[1]
        else:
            my_command = parts[0].lower()
            receivers  = parts[1]
            my_payload = parts[2]

        # prepare
        service.trace(f"< COMMAND detected: {my_command} payload = '{my_payload}'")

        # receivers detected
        receivers_detected = False
        if len(receivers) > 0:
            service.trace(f"< Receivers detected: { receivers }")
            receivers_detected = True
            if service.is_valid_client_id(receivers) == False:
                service.trace(f"< Receiver is not valid. Skip message")
                return False

        # process payload
        if len(service.commands) > 0:
            if my_command in service.commands.keys():
                command_handler = service.commands[my_command]
                if command_handler.handle(command, my_payload, service) == True:
                    return True
                else:
                    service.trace(f"< Command Handler {my_command} finished without success")                    

        # answer requests to ignore
        if my_command == "connect" or my_command.find(ServiceActionCommands.SERVICE_CMD_RESPONSE_SUFFIX) > 0:
            service.trace(f"< command {my_command} ignored")
            return True

        # built in commands
        if my_command == "quit" and receivers_detected == True:
            return self.handle_quit(my_payload, service)
        elif my_command == "restart" and receivers_detected == True:
            return self.handle_restart(my_payload, service)
        elif my_command == "connected":
            return self.handle_connected(my_payload, service)
        elif my_command == "ping":
            return self.handle_ping(my_payload, service)
        elif my_command == "echo":
            return self.handle_echo(my_payload, service)
        elif my_command == "info":
            return self.handle_info(my_payload, service)
        elif my_command == "message":
            return self.handle_message(my_payload, service)
        else:
            service.trace(f"< Command {my_command} with payload {my_payload} not handled")
            return False    

    def has_separator(self, message) -> bool:
        if message.find(self.separator) > 0:
            return True
        else:
            return False      

class ServiceCommand(Base):
    """ 
        Abstract service command - to be used to incoming command messages
    """ 

    def __init__(self, command, description):
        super().__init__()
        self.type = "pydeen.ServiceCommand"
        self.set_property(Base.BASE_PROP_KEY, command)
        self.set_property(Base.BASE_PROP_DESCRIPTION, description)

    def handle(self, command:str, payload:str, service:ServiceContext) -> bool:
        """
            handle a service messsage checked before by parse()
        """
        service.error("service_command not redefined!")
        return False


class Service(ServiceContext):
    """ 
        Abstract Service
    """
    def __init__(self):
        super().__init__()
        self.type = "pydeen.Service"

    def register_action(self, action:ServiceAction) -> bool:
        if action in self.actions:
            return False
        else:
            self.actions.append(action)
            return True    

    def register_command(self, command:ServiceCommand) -> bool:
        if command in self.commands:
            return False
        else:
            self.commands[command.get_key()] = command
            return True    

    def register_group(self, group) -> bool:
        if group in self.groups:
            return False
        else:
            self.groups.append(group)
            return True    


    def set_command_mode(self, echo=True) -> bool:
        if self.get_count_registered_actions() > 0 or self.get_count_registered_commands() > 0:
            self.trace("init command mode failed - already registered actions or commands")
            return False
        else:
            default_action = ServiceActionCommands()
            default_action.init_default_commands(self, echo)    
            self.register_action(default_action)
            self.trace("command mode active: default commands are registered")
            return True    