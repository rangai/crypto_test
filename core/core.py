import socket

from p2p.connection_manager import ConnectionManager

STATE_INIT = 0
STATE_STANDBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3


class Core:

    def __init__(self, my_port=50082, node_host=None, node_port=None):
        self.server_state = STATE_INIT
        print('[ C] Initializing node...')
        self.my_ip = self.__get_myip()
        print('[ C] Node IP address is set to ... ', self.my_ip)
        self.my_port = my_port
        self.cm = ConnectionManager(self.my_ip, self.my_port)
        self.node_host = node_host
        self.node_port = node_port

    def start(self):
        self.server_state = STATE_STANDBY
        self.cm.start()

    def join_network(self):
        if self.node_host is not None:
            self.server_state = STATE_CONNECTED_TO_NETWORK
            self.cm.connect_to_network(self.node_host, self.node_port)
        else:
            print('[ C] This node is runnning as Genesis Node...')

    def shutdown(self):
        self.server_state = STATE_SHUTTING_DOWN
        print('[ C] Shutdown node...')
        self.cm.close_connection()

    def get_my_current_state(self):
        return self.server_state

    def __get_myip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
