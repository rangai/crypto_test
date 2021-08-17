import threading


class Nodes:

    def __init__(self):
        self.lock = threading.Lock()
        self.nodes = set()

    def add_node(self, node):
        with self.lock:
            print('[ N](add_node) Adding node: ', node)
            self.nodes.add((node))
            print('[ N](add_node) Current nodes: ', self.nodes)


    def remove_node(self, node):
        with self.lock:
            if node in self.nodes:
                print('[ N](remove_node) Removing node: ', node)
                self.nodes.remove(node)
                print('[ N](remove_node) Current nodes: ', self.nodes)

    def overwrite(self, new_nodes):
        with self.lock:
            print('[ N](overwrite) Overwriting nodes')
            self.nodes = new_nodes
            print('[ N](overwrite) Current nodes: ', self.nodes)


    def get_nodes(self):
        print('[ N] get_nodes')
        return self.nodes
