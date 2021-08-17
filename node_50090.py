import signal
from time import sleep
from core.core import Core


my_node = None


def signal_handler(signal, frame):
    shutdown_server()

def shutdown_server():
    global my_node
    my_node.shutdown()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    global my_node
    print("IP: ")
    ip=str(input())
    my_node = Core(50090, ip, 50082)
    my_node.start()
    my_node.join_network()
    sleep(3)
    my_node.get_all_chains_for_resolve_conflict()

if __name__ == '__main__':
    main()