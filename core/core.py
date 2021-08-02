import socket

from p2p.connection_manager import ConnectionManager
from p2p.my_protocol_message_handler import MyProtocolMessageHandler
from p2p.message_manager import (
    MSG_NEW_TRANSACTION,
    MSG_NEW_BLOCK,
    RSP_FULL_CHAIN,
    MSG_ENHANCED,
)

STATE_INIT = 0
STATE_STANDBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3


class Core:

    def __init__(self, my_port=50082, node_host=None, node_port=None):
        self.server_state = STATE_INIT
        print('[ C] Initializing server...')
        self.my_ip = self.__get_myip()
        print('[ C] IP address is set to ... ', self.my_ip)
        self.my_port = my_port
        self.cm = ConnectionManager(self.my_ip, self.my_port)
        self.pm = MyProtocolMessageHandler()
        self.node_host = node_host
        self.node_port = node_port
        self.my_protocol_message_store = []

    def start(self):
        self.server_state = STATE_STANDBY
        self.cm.start()

    def join_network(self):
        if self.node_host is not None:
            self.server_state = STATE_CONNECTED_TO_NETWORK
            self.cm.connect_to_network(self.node_host, self.node_port)
        else:
            print('[ C] This server is runnning as Genesis Core Node...')

    def shutdown(self):
        self.server_state = STATE_SHUTTING_DOWN
        print('[ C] Shutdown server...')
        self.cm.connection_close()

    def __core_api(self, request, message):
        if request == 'broadcast':
            new_message = self.cm.get_message_text(MSG_ENHANCED, message)
            self.cm.broadcast(new_message)
            return 'ok'
        elif request == 'api_type':
            return 'core_api'

    def __handle_message(self, msg, node=None):
        if node is not None:
            print('[ C] Send our latest blockchain for reply to : ', node)
        else:
            if msg[2] == MSG_NEW_TRANSACTION:
                pass
            elif msg[2] == MSG_NEW_BLOCK:
                pass
            elif msg[2] == RSP_FULL_CHAIN:
                pass
            elif msg[2] == MSG_ENHANCED:
                print('[ C] Received enhanced message', msg[4])
                current_messages = self.my_protocol_message_store
                if not msg[4] in current_messages:
                    self.my_protocol_message_store.append(msg[4])
                    self.pm.handle_message(msg[4], self.__core_api)

    def __get_myip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
