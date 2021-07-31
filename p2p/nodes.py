import threading


class Nodes:

    def __init__(self):
        self.lock = threading.Lock()
        self.nodes = set()

    def add_node(self, node):
        with self.lock:
            print('[ N] Adding node: ', node)
            self.nodes.add((node))
            print('[ N] Current nodes: ', self.nodes)

    def remove_node(self, node):
        with self.lock:
            if node in self.nodes:
                print('[ N] Removing node: ', node)
                self.nodes.remove(node)
                print('[ N] Current nodes: ', self.nodes)

    def overwrite(self, new_nodes):
        with self.lock:
            print('[ N] nodes will be going to overwrite')
            self.nodes = new_nodes
            print('[ N] Current nodes: ', self.nodes)

    def get_nodes(self):
        return self.nodes
