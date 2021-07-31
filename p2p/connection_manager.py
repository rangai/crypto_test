import socket
import threading
import pickle
from concurrent.futures import ThreadPoolExecutor

from .nodes import Nodes
from .message_manager import (
    MessageManager,
    MSG_ADD,
    MSG_REMOVE,
    MSG_NODES,
    MSG_REQUEST_NODES,
    MSG_PING,
)

PING_INTERVAL = 10


class ConnectionManager:

    def __init__(self, my_host,  my_port):
        print('[CM] Initializing ConnectionManager...')
        self.host = my_host
        self.port = my_port
        self.nodes = Nodes()
        self.nodes.add_node((my_host, my_port))
        self.mm = MessageManager()


    def start(self):
        t = threading.Thread(target=self.__wait_for_access)
        t.start()

        self.ping_timer = threading.Timer(PING_INTERVAL, self.__check_connection)
        self.ping_timer.start()


    def send_msg(self, to_node, msg):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((to_node))
            s.sendall(msg.encode('utf-8'))
            s.close()
        except OSError:
            print('[CM] Connection failed for node : ', to_node)
            self.nodes.remove_node(to_node)


    def broadcast(self, msg):
        print('[CM] Broadcasting...')
        connected_nodes = self.nodes.get_nodes()
        for n in connected_nodes:
            if n != (self.host, self.port):
                print("[CM] Message will be sent to ... ", n)
                self.send_msg(n, msg)


    def connect_to_network(self, host, port):
        self.my_c_host = host
        self.my_c_port = port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        msg = self.mm.build(MSG_ADD, self.port)
        s.sendall(msg.encode('utf-8'))
        s.close()


    def close_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.socket.close()
        s.close()
        self.ping_timer.cancel()

        msg = self.mm.build(MSG_REMOVE, self.port)
        self.send_msg((self.my_c_host, self.my_c_port), msg)


    def __wait_for_access(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(0)

        executor = ThreadPoolExecutor(max_workers=10)

        while True:

            print('[CM] Waiting for the connection ...')
            soc, addr = self.socket.accept()
            print('[CM] Connected by .. ', addr)
            data_sum = ''

            params = (soc, addr, data_sum)
            executor.submit(self.__handle_message, params)


    def __handle_message(self, params):

        soc, addr, data_sum = params

        while True:
            data = soc.recv(1024)
            data_sum = data_sum + data.decode('utf-8')

            if not data:
                break

        if not data_sum:
            return
            
        cmd, node_port, payload = self.mm.parse(data_sum)
        print("[CM]", cmd, node_port,payload)

        if cmd == MSG_ADD:
            print('[CM] ADD node request was received.')
            self.nodes.add_node((addr[0], node_port))
            if(addr[0], node_port) == (self.host, self.port):
                return
            else:
                cl = pickle.dumps(self.nodes.get_nodes(), 0).decode()
                msg = self.mm.build(MSG_NODES, self.port, cl)
                self.broadcast(msg)
        elif cmd == MSG_REMOVE:
            print('[CM] REMOVE request was received from', addr[0], node_port)
            self.nodes.remove_node((addr[0], node_port))
            cl = pickle.dumps(self.nodes.get_nodes(), 0).decode()
            msg = self.mm.build(MSG_NODES, self.port, cl)
            self.broadcast(msg)

        elif cmd == MSG_NODES:
            print('[CM] Refresh the nodes...')
            latest_nodes = pickle.loads(payload.encode('utf8'))
            print('[CM] Latest nodes: ', latest_nodes)
            self.nodes.overwrite(latest_nodes)
        elif cmd == MSG_REQUEST_NODES:
            print('[CM] Node set was requested.')
            cl = pickle.dumps(self.nodes.get_nodes(), 0).decode()
            msg = self.mm.build(MSG_NODES, self.port, cl)
            self.send_msg((addr[0], node_port), msg)
        elif cmd == MSG_PING:
            return
        else:
            print('[CM] Unknown command was received.', cmd)
            return


    def __check_connection(self):
        print('[CM] Check connection was called.')
        connected_nodes = self.nodes.get_nodes()
        changed = False
        disconnected_nodes = list(filter(lambda p: not self.__is_alive(p), connected_nodes))
        if disconnected_nodes:
            changed = True
            print('[CM] Removing node', disconnected_nodes)
            connected_nodes = connected_nodes - set(disconnected_nodes)
            self.nodes.overwrite(connected_nodes)

        connected_nodes = self.nodes.get_nodes()
        print('[CM] current nodes:', connected_nodes)
        if changed:
            cl = pickle.dumps(connected_nodes, 0).decode()
            msg = self.mm.build(MSG_NODES, self.port, cl)
            self.broadcast(msg)
        self.ping_timer = threading.Timer(PING_INTERVAL, self.__check_connection)
        self.ping_timer.start()


    def __is_alive(self, target):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target))
            msg = self.mm.build(MSG_PING)
            s.sendall(msg.encode('utf-8'))
            s.close()
            return True
        except OSError:
            return False