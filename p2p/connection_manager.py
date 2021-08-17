import socket
import threading
import pickle
from concurrent.futures import ThreadPoolExecutor

from .nodes import Nodes
from .message_manager import (
    MessageManager,
    MSG_ADD,
    MSG_REMOVE,
    MSG_OVERWRITE_NODES,
    MSG_REQUEST_NODES,
    MSG_PING,

    WITH_PAYLOAD,
    WITHOUT_PAYLOAD,
)


PING_INTERVAL = 10


class ConnectionManager:

    def __init__(self, host, my_port, callback):
        print('[CM] Initializing ConnectionManager...')
        self.host = host
        self.port = my_port
        self.my_c_host = None
        self.my_c_port = None
        self.nodes = Nodes()
        self.nodes.add_node((host, my_port))
        self.mm = MessageManager()
        self.callback = callback


    def start(self):
        print('[CM](start)')
        t = threading.Thread(target=self.__wait_for_access)
        t.start()

        self.ping_timer = threading.Timer(PING_INTERVAL, self.__check_connection)
        self.ping_timer.start()


    def get_message_text(self, msg_type, payload = None):
        print('[CM](get_message_text)')
        msgtxt = self.mm.build(msg_type, self.port, payload)
        print('[CM](get_message_text) Generated message:', msgtxt)
        return msgtxt


    def send_msg(self, node, msg):
        print('[CM](send_msg)')
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((node))
            s.sendall(msg.encode('utf-8'))
            s.close()
        except OSError:
            print('[CM](send_msg) Connection failed for node :', node)
            self.nodes.remove_node(node)


    def broadcast(self, msg):
        print('[CM](broadcast)', msg)
        current_nodes = self.nodes.get_nodes()
        print('[CM](broadcast) Broadcast to ...', current_nodes)
        for n in current_nodes:
            if n != (self.host, self.port):
                print("[CM](broadcast) Sent to ... ", n)
                self.send_msg(n, msg)


    def connection_close(self):
        print('[CM](connection_close)')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        self.socket.close()
        s.close()
        self.ping_timer.cancel()
        if self.my_c_host is not None:
            msg = self.mm.build(MSG_REMOVE, self.port)
            self.send_msg((self.my_c_host, self.my_c_port), msg)


    def connect_to_network(self, host, port):
        print('[CM](connect_to_network)', host, port)
        self.my_c_host = host
        self.my_c_port = port
        msg = self.mm.build(MSG_ADD, self.port)
        self.send_msg((host, port), msg)


    def __wait_for_access(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(0)

        executor = ThreadPoolExecutor(max_workers=10)

        while True:
            print('[CM](__wait_for_access) Waiting for the connection ...')
            soc, addr = self.socket.accept()
            print('[CM](__wait_for_access) Connected by .. ', addr)
            content = ''

            params = (soc, addr, content)
            executor.submit(self.__handle_message, params)


    def __handle_message(self, params):

        soc, addr, content = params

        while True:
            data = soc.recv(1024)
            content = content + data.decode('utf-8')

            if not data:
                break

        if not content:
            return
        
        print("[CM](__handle_message) content", content)
        status_type, cmd, peer_port, payload = self.mm.parse(content)
        print("[CM](__handle_message) cmd, payload:", cmd, payload)

        if status_type == WITHOUT_PAYLOAD:
            if cmd == MSG_ADD:
                print('[CM](__handle_message) ADD node request was received.')
                self.nodes.add_node((addr[0], peer_port))
                if(addr[0], peer_port) == (self.host, self.port):
                    return
                else:
                    cl = pickle.dumps(self.nodes.get_nodes(), 0).decode()
                    msg = self.mm.build(MSG_OVERWRITE_NODES, self.port, cl)
                    self.broadcast(msg)
            elif cmd == MSG_REMOVE:
                print('[CM](__handle_message) REMOVE request was received from', addr[0], peer_port)
                self.nodes.remove_node((addr[0], peer_port))
                cl = pickle.dumps(self.nodes.get_nodes(), 0).decode()
                msg = self.mm.build(MSG_OVERWRITE_NODES, self.port, cl)
                self.broadcast(msg)
            elif cmd == MSG_PING:
                return
            elif cmd == MSG_REQUEST_NODES:
                print('[CM](__handle_message) MSG_REQUEST_NODES')
                cl = pickle.dumps(self.nodes.get_nodes(), 0).decode()
                msg = self.mm.build(MSG_OVERWRITE_NODES, self.port, cl)
                self.send_msg((addr[0], peer_port), msg)
            else:
                self.callback((status_type, cmd, peer_port, payload), (addr[0], peer_port))
                return
        elif status_type == WITH_PAYLOAD:
            if cmd == MSG_OVERWRITE_NODES:
                print('[CM](__handle_message) MSG_OVERWRITE_NODES')
                new_nodes = pickle.loads(payload.encode('utf8'))
                print('[CM](__handle_message) Latest nodes: ', new_nodes)
                self.nodes.overwrite(new_nodes)
            else:
                self.callback((status_type, cmd, peer_port, payload), None)
                return
        else:
            print('[CM](__handle_message) Unexpected status', status_type)


    def __check_connection(self):
        print('[CM](__check_connection)')
        connected_nodes = self.nodes.get_nodes()
        changed = False
        disconnected_nodes = list(filter(lambda p: not self.__is_alive(p), connected_nodes))
        if disconnected_nodes:
            changed = True
            print('[CM](__check_connection) Removing peer', disconnected_nodes)
            connected_nodes = connected_nodes - set(disconnected_nodes)
            self.nodes.overwrite(connected_nodes)

        connected_nodes = self.nodes.get_nodes()
        print('[CM](__check_connection) connected nodes:', connected_nodes)
        if changed:
            cl = pickle.dumps(connected_nodes, 0).decode()
            msg = self.mm.build(MSG_OVERWRITE_NODES, self.port, cl)
            self.broadcast(msg)
        self.ping_timer = threading.Timer(PING_INTERVAL, self.__check_connection)
        self.ping_timer.start()


    def __is_alive(self, target):
        print('[CM](__is_alive)')
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target))
            msg = self.mm.build(MSG_PING)
            s.sendall(msg.encode('utf-8'))
            s.close()
            return True
        except OSError:
            return False
