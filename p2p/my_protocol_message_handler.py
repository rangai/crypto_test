import json


BROADCAST = 'broadcast'


class MyProtocolMessageHandler:
    def __init__(self):
        print('[PM] Initializing MyProtocolMessageHandler...')

    def handle_message(self, msg, api):
        msg = json.loads(msg)

        my_api = api('api_type', None)
        print('my_api: ', my_api)
        if my_api == 'core_api':
            print('[PM] Bloadcasting ...', json.dumps(msg))
            api(BROADCAST, json.dumps(msg))

        return
