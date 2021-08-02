import json

MSG_ADD = 0
MSG_REMOVE = 1
MSG_OVERWRITE_NODES = 2
MSG_REQUEST_NODES = 3
MSG_PING = 4
MSG_NEW_TRANSACTION = 7
MSG_NEW_BLOCK = 8
MSG_REQUEST_FULL_CHAIN = 9
RSP_FULL_CHAIN = 10
MSG_ENHANCED = 11


class MessageManager:

    def __init__(self):
        print('[MM] Initializing MessageManager...')

    def build(self, msg_type, my_port=50082, payload=None):
        message = {
          'msg_type': msg_type,
          'my_port': my_port
        }

        if payload is not None:
            message['payload'] = payload

        return json.dumps(message)

    def parse(self, msg):
        msg = json.loads(msg)

        cmd = msg.get('msg_type')
        my_port = msg.get('my_port')
        payload = msg.get('payload')

        if cmd in (MSG_OVERWRITE_NODES, MSG_NEW_TRANSACTION, MSG_NEW_BLOCK, RSP_FULL_CHAIN, MSG_ENHANCED):
            return (cmd, my_port, payload)
        else:
            return (cmd, my_port, None)
