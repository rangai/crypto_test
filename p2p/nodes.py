import threading


class Nodes:

    def __init__(self):
        self.lock = threading.Lock()
        self.nodes = set()

    def add_node(self, peer):
        with self.lock:
            print('[ N] Adding peer: ', peer)
            self.nodes.add((peer))
            print('[ N] Current nodes: ', self.nodes)


    def remove_node(self, peer):
        with self.lock:
            if peer in self.nodes:
                print('[ N] Removing node: ', peer)
                self.nodes.remove(peer)
                print('[ N] Current nodes: ', self.nodes)

    def overwrite(self, new_nodes):
        with self.lock:
            print('[ N] Overwriting nodes')
            self.nodes = new_nodes
            print('[ N] Current nodes: ', self.nodes)


    def get_nodes(self):
        return self.nodes
