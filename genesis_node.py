import socket
import signal

from core.core import Core


my_node = None


def signal_handler(signal, frame):
    shutdown_node()


def shutdown_node():
    global my_node
    my_node.shutdown()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    global my_node
    my_node = Core(50082)
    my_node.start()


if __name__ == '__main__':
    main()
