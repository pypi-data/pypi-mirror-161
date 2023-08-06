import websockets
import json
import ssl
from socket import SOCK_DGRAM, socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import asyncio

DEBUG = True
valid_proto = ["ws", "tcp", "udp"]

def log(obj):
    if DEBUG:
        print("log: ", obj)

def retrieve(response, key=None, ret=False):
    log("retrieving data")
    if response["statusCode"] == 0:
        if ret:
            return response
        elif key is None:
            return 0
        else:
            try:
                return response[key]
            except KeyError:
                raise KeyError("Data retrieval failed.")
    raise Exception("request returned with status code " + str(response['statusCode']) + ":\n" + response['message'])


class Corelink:

    class Proto(asyncio.Protocol):
        """An asyncio Protocol class used to process incoming messages for a receiver.
        Implements TCP or UDP protocol."""
        def __init__(self, core, message: bytearray, type, port) -> None:
            self.core = core
            self.header = bytes(message)
            self.type = type
            self.transport = None
            self.port = port

        def connection_made(self, transport) -> None:
            self.transport = transport
            if self.type == 'tcp':
                self.transport.write(self.header)
            else:
                self.transport.sendto(self.header)
            log(f"[{self.type}] Receiver connected. Waiting for data.")
                
        def connection_lost(self, exc):
            log('The server closed the connection')
        
        #TCP
        def data_received(self, data: bytes) -> None:
            log("[tcp] data received")
            self.core.receiver_callback(data)

        #UDP
        def datagram_received(self, data, addr):
            log("[udp] data received")
            self.core.receiver_callback(data)

        #UDP
        def error_received(self, exc):
            print('Error received:', exc)

    def __init__(self, user: str, password: str, host: str, port: str, protocol: str = "ws") -> None:
        """Initializes corelink object with parameters
        :param user: Username
        :param password: Password
        :param host: ip or host address
        :param port: port
        :param protocol: ws or tcp or udp (default: ws websockets)
        """
        # if sys.platform == 'win32':
        #     loop = asyncio.ProactorEventLoop()
        #     asyncio.set_event_loop(loop)
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.protocol = protocol
        self.token = None
        self.connection = None
        self.user_ip = None
        self.controlID = 0
        self.request_queue = {}
        self.streams = {}
        self.receiver = {}
        self.loop = asyncio.get_running_loop()
        self.keep_open = False
        self.user_cb = self.default_cb
        self.server_callbacks = {"update": self.default_cb, "subscriber": self.default_cb, "stale": self.default_cb, "dropped": self.default_cb}

    async def connect(self):
        """Connects to server and authenticates.
        return: token
        """
        self.connection = await websockets.connect(f"wss://{self.host}:{self.port}", ssl=ssl.SSLContext(ssl.PROTOCOL_TLS))
        self.receiver_task = asyncio.create_task(self.ws_control_receiver(self.connection))
        await self.auth()

    async def close_control(self):
        """Closes Websocket control stream"""
        await self.connection.close()
        log("Websocket connection closed")
    
    # async def exit(self): # not sure if this function is necessary
    #     """Disconnects all open streams and closes connection"""
    #     self.disconnect_streams(stream_ids=list(self.streams))
    #     # self.expire()
    #     self.close()

    async def request(self, command: dict) -> dict:
        """Sends control function to server
        :param command: request to be send
        """
        log("requesting: "+ str(command))
        command['ID'] = self.controlID
        self.request_queue[self.controlID] = False
        self.controlID += 1
        await self.connection.send(json.dumps(command))
        while not self.request_queue[command['ID']]:
            await asyncio.sleep(.05)
        ret = self.request_queue[command['ID']]
        del self.request_queue[command['ID']]
        return ret

    async def ws_control_receiver(self, stream):
        log("[WS] control receiver channel open.")
        async for message in stream:
            await self.response(message)

    async def response(self, response) -> dict:
        """Processes server response and relays server control functions away"""
        log("response received")
        response = json.loads(response)
        if 'ID' in response:
            self.request_queue[response['ID']] = response
            del response['ID']
        elif 'function' in response:
            self.server_callbacks[response['function']](response, key=response['function'])

    def default_cb(self, data, *args, key='data'):
        print("Callback not set for", key)
        if key == 'data':
            print("message:\n", data)

    def set_data_callback(self, callback):  # check if this works
        """User should pass their callback function into this.
        The function is expected to take:
            param1 message: bytes,
            param2 streamID: int,
            param3 header: dict (sometimes empty)"""
        self.user_cb = callback

    def set_server_callback(self, callback, key: str):
        """Sets a callback function for server messages of the given key:
            options: 'update', 'subscriber', 'stale', 'dropped'
        callback should expect dict message with the server message (details in docs),
                           and str key listing what the message type is."""
        self.server_callbacks[key] = callback

    async def create_sender(self, workspace, protocol: str, streamID="", data_type='', metadata='', sender="", ip="", port="") -> int:
        """Requests a sender from the server and opens the connection
        return: streamID used to send
        """
        protocol = protocol.lower()
        if protocol not in valid_proto:
            raise ValueError("protocol: protocol must be ws, tcp or udp")
        request = {
            "function": "sender",
            "workspace": workspace,
            "senderID": streamID,
            "proto": protocol,
            "IP": ip,
            "port": port,
            "alert": False,
            "type": data_type,
            "meta": metadata,
            "from": sender,
            "token": self.token
        }
        sender = retrieve(await self.request(request), ret=True)
        self.streams[sender['streamID']] = sender
        self.streams[sender['streamID']]['protocol'] = request['proto']
        return sender['streamID']
    
    async def create_receiver(self, workspace, protocol, data_type="", metadata="", alert=False, echo=False, receiver_id="", stream_ids=[], ip=None, port=0) -> int:
        """Requests a receiver from the server and opens the connection.
        return: streamID used to receive
        """
        protocol = protocol.lower()
        if protocol not in valid_proto:
            raise ValueError("protocol: protocol must be ws, tcp or udp")
        if ip is None:
            ip = self.user_ip
        request = {
            "function": "receiver",
            "workspace": workspace,
            "receiverID": receiver_id,
            "streamIDs": stream_ids,
            "proto": protocol,
            "type": data_type,
            "alert": alert,
            "echo": echo,
            "IP": ip,
            "port": port,
            "meta": metadata,
            "token": self.token
        }
        receiver = retrieve(await self.request(request), ret=True)
        log("receiver: " + str(receiver))
        self.receiver[receiver['streamID']] = receiver
        return receiver['streamID']

    async def connect_sender(self, streamID):
        """Connects sender in order to send data"""
        stream = self.streams[streamID] # for convenience
        if stream['protocol'] == 'tcp':
            stream['connection'] = socket(AF_INET, SOCK_STREAM)
            stream['connection'].connect((self.host, int(stream['port'])))
        elif stream['protocol'] == 'udp':
            stream['connection'] = socket(AF_INET, SOCK_DGRAM)
            stream['connection'].connect((self.host, int(stream['port'])))
        elif stream['protocol'] == 'ws':
            stream['connection'] = await websockets.connect(f"wss://{self.host}:{stream['port']}", ssl=ssl.SSLContext(ssl.PROTOCOL_TLS))
            log('connected WS sender.')

    async def send(self, streamID, user_header: dict = None, data=None):
        """Sends data to streamID's stream (user should first call connect_sender(streamID))
        data should be either str or bytes"""
        stream = self.streams[streamID] # for convenience
        user_h = json.dumps(user_header) if user_header else ""
        header = [0, 0, 0, 0, 0, 0, 0, 0]
        header = bytearray(header)
        head = memoryview(header)
        if user_h:
            head[0:2] = int.to_bytes(len(user_h), 2, 'little')
        if data:
            if data is str:
                head[2:4] = int.to_bytes(len(data), 2, 'little')
            elif data is bytes:
                ... # finish
            else:
                raise TypeError("data should be str or bytes.")
        head[4:6] = int.to_bytes(int(streamID), 2, 'little')
        log(header)
        message = bytes(header) + user_h.encode() + data.encode()
        log(message)
        if stream['protocol'] == 'ws':
            await stream['connection'].send(message)
        else:
            stream['connection'].send(message)

    async def connect_receiver(self, streamID):
        """Connects receiver in order to send data."""
        stream = self.receiver[streamID] # for convenience
        header = [0, 0, 0, 0, 0, 0, 0, 0]
        header = bytearray(header)
        head = memoryview(header)
        head[4:6] = int.to_bytes(int(streamID), 2, 'little')

        # header = bytearray(4)  # I'm going to need to redo the header sometime
        # header.append(streamID)
        log(header)
        log(self.receiver)
        header = bytes(header)
        if stream['proto'] == 'tcp':
            stream['connection'] = await self.loop.create_connection(lambda: self.Proto(self, header, 'tcp', int(stream['port'])), 
                                                                     self.host, int(stream['port']))
        elif stream['proto'] == 'udp':
            stream['connection'] = await self.loop.create_datagram_endpoint(lambda: self.Proto(self, header, 'udp', int(stream['port'])),
                                                                            remote_addr=(self.host, int(stream['port'])), 
                                                                            allow_broadcast=True)
        elif stream['proto'] == 'ws':
            stream['connection'] = await websockets.connect(f"wss://{self.host}:{stream['port']}", 
                                      ssl=ssl.SSLContext(ssl.PROTOCOL_TLS))
            await stream['connection'].send(header)
            self.receiver_task = asyncio.create_task(self.ws_receiver(stream))

    async def ws_receiver(self, stream):
        log('[WS] Receiver connected.')
        async for message in stream['connection']:
            self.receiver_callback(message)
    
    def receiver_callback(self, message: bytes):
        log('in receiver_callback()')
        head_size = int.from_bytes(message[:2], 'little')
        if head_size:
            header = json.loads(message[8:head_size+8])
        else:
            header = {}
        streamID = int.from_bytes(message[4:6], 'little')
        message = message[8+head_size:]
        self.user_cb(message, streamID, header)
        


    async def disconnect_receiver(self, streamID):
        log("disconnecting receiver " + str(streamID))
        if self.receiver[streamID]['proto'] == 'ws':
            await self.receiver[streamID]['connection'].close()
            self.receiver_task.cancel()

        else:
            self.receiver[streamID]['connection'][0].close()
        
        # await self.disconnect_streams(stream_ids={streamID})

    async def disconnect_senders(self, streamIDs: list):
        for ID in streamIDs:
            log("disconnecting " + str(ID))
            if self.streams[ID]['protocol'] == 'ws':
                await self.streams[ID]['connection'].close()
            else:
                self.streams[ID]['connection'].close()
        # await self.disconnect_streams(stream_ids=streamIDs)

    async def auth(self) -> int:
        """Authenticates user with values in the object
        :return: token
        """
        request = {
            "function": "auth",
            "username": self.user,
            "password": self.password
        }
        response = await self.request(request)
        self.token = response['token']
        self.user_ip = response['IP']
        return self.token

    async def list_functions(self) -> list:
        """return: List of functions available to the user
        """
        request = {
            "function": "listFunctions",
            "token": self.token
        }
        return retrieve(await self.request(request), "functionList")

    async def list_server_functions(self) -> list:
        request = {
            "function": "listServerFunctions",
            "token": self.token
        }
        return retrieve(await self.request(request), "functionList")

    async def describe_function(self, func: str) -> dict:
        request = {"function": "describeFunction",
                   "functionName": func,
                   "token": self.token}
        return retrieve(await self.request(request), "description")

    async def describe_server_function(self) -> dict:
        request = {
            "function": "listServerFunctions",
            "token": self.token
        }
        return retrieve(await self.request(request), "description")

    async def list_workspaces(self) -> list:
        request = {
            "function": "listWorkspaces",
            "token": self.token
        }
        return retrieve(await self.request(request), "workspaceList")

    async def add_workspace(self, space: str):
        """Adds a workspace.
        :param space: Space to add
        :return: Workspace
        """
        request = {
            "function": "addWorkspace",
            "workspace": space,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def set_default_workspace(self, space):
        """Sets default workspace.
        :param space: space to set
        :return: Workspace
        """
        request = {
            "function": "setDefaultWorkspace",
            "workspace": space,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def get_default_workspace(self) -> str:
        """return: Default workspace
        """
        request = {
            "function": "getDefaultWorkspace",
            "token": self.token
        }
        return retrieve(await self.request(request), "workspace")

    async def remove_workspace(self, space: str):
        request = {
            "function": "rmWorkspace",
            "workspace": space,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def add_user(self, new_username, new_password, admin_bool, first_name,
                       last_name, email):
        request = {
            "function": "addUser",
            "username": new_username,
            "password": new_password,
            "admin": admin_bool,
            "first": first_name,
            "last": last_name,
            "email": email,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def change_password(self, new_password):
        request = {
            "function": "password",
            "password": new_password,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def remove_user(self, rm_username):
        request = {
            "function": "rmUser",
            "password": rm_username,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def list_users(self):
        request = {
            "function": "listUsers",
            "token": self.token
        }
        return retrieve(await self.request(request), "userList")

    async def add_group(self, group):
        request = {
            "function": "addGroup",
            "group": group,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def add_user_group(self, group, user):
        request = {
            "function": "addUserGroup",
            "group": group,
            "user": user,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def remove_user_group(self, group, user):
        request = {
            "function": "rmUserGroup",
            "group": group,
            "user": user,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def change_owner(self, group, user):
        request = {
            "function": "changeOwner",
            "group": group,
            "user": user,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def remove_group(self, group, user):
        request = {
            "function": "rmGroup",
            "group": group,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def list_groups(self, group, user):
        request = {
            "function": "listGroups",
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def list_streams(self, workspaces="", types=""):
        request = {
            "function": "listStreams",
            "workspaces": workspaces,
            "types": types,
            "token": self.token
        }
        return retrieve(await self.request(request), "senderList")

    async def stream_info(self, stream_id):
        request = {
            "function": "streamInfo",
            "streamID": stream_id,
            "token": self.token
        }
        return retrieve(await self.request(request), "info")

    async def subscribe_to_stream(self, stream_id):
        if not self.receiver:
            raise Exception("Receiver not yet created.")
        request = {
            "function": "subscribe",
            "receiverID": self.receiver['id'],
            "streamID": stream_id,
            "token": self.token
        }
        return retrieve(await self.request(request), "streamList")

    async def unsubscribe_from_stream(self, stream_id):
        if not self.receiver:
            raise Exception("Receiver not yet created.")
        request = {
            "function": "unsubscribe",
            "receiverID": self.receiver['id'],
            "streamID": stream_id,
            "token": self.token
        }
        return retrieve(await self.request(request), "streamList")

    async def set_config(self, config, context, app, username, value):
        request = {
            "function": "setConfig",
            "config": config,
            "context": context,
            "app": app,
            "user": username,
            "value": value,
            "token": self.token
        }
        return retrieve(await self.request(request))

    async def disconnect_streams(self, workspaces=None, types=None, stream_ids=None):
        """Disconnects streams of given workspaces and types, or by streamIDs
        Note: if streamIDs are passed, then other params will be ignored
        return: list of disconnected streams
        """
        if not (workspaces or types or stream_ids):
            raise ValueError
        request = {
            "function": "disconnect",
            "token": self.token
        }
        if workspaces:
            request["workspaces"] = workspaces
        if types:
            request["types"] = types
        if stream_ids:
            request["streamIDs"] = stream_ids
        return retrieve(await self.request(request), "streamList")  

    # async def expire(self):
    #     """Expires session and invalidates user token"""
    #     request = {
    #         "function": "expire",
    #         "token": self.token
    #     }
    #     return retrieve(await self.request(request))
    # Sarthak said this doesn't yet work

# def split_packet():
#     # https: // github.com / SecureAuthCorp / impacket / blob / master / examples / split.py
#     pass
