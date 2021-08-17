import signal
from time import sleep
import json

from core.core import Core
from p2p.message_manager import MSG_NEW_TRANSACTION

my_node = None

def signal_handler(signal, frame):
    shutdown_server()

def shutdown_server():
    global my_node
    my_node.shutdown()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    global my_node
    my_node = Core(50082) 
    my_node.start()
    sleep(10)
    transaction = { 
        'sender': 'test1',
        'recipient': 'test2',
        'value': 3
    }

    my_node.send_message_to_core(MSG_NEW_TRANSACTION,json.dumps(transaction))

    sleep(3)

    transaction2 = { 
        'sender': 'test4',
        'recipient': 'test5',
        'value': 6
    }
    
    my_node.send_message_to_core(MSG_NEW_TRANSACTION,json.dumps(transaction2))

    sleep(3)

    transaction3 = { 
        'sender': 'test7',
        'recipient': 'test8',
        'value': 9
    }

    my_node.send_message_to_core(MSG_NEW_TRANSACTION,json.dumps(transaction3))


if __name__ == '__main__':
    main()