import json
import binascii
import hashlib
from time import time
from datetime import datetime

class Block:
    def __init__(self, transactions, previous_block_hash):
        self.timestamp = time()
        self.transactions = transactions
        self.previous_block = previous_block_hash

        current = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print("[ B]", current)

        json_block = json.dumps(self.to_dict(include_nonce=False) , sort_keys=True)
        print('[ B] JSON Block :', json_block)
        self.nonce = self._compute_nonce_for_pow(json_block)

        current2 = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print("[ B]", current2)


    def to_dict(self,include_nonce= True):
        print('[ B](to_dict)', include_nonce)
        d = {
            'timestamp' : self.timestamp,
            'transactions': list(map(json.dumps, self.transactions)),
            'previous_block': self.previous_block,
        }

        if include_nonce:
            d['nonce'] = self.nonce
        return d

    def _compute_nonce_for_pow(self, msg, difficulty=5):
        print('[ B](_compute_nonce_for_pow)', msg, difficulty)
        i = 0
        suffix = '0' * difficulty
        while True:
            nonce = str(i)
            digest = binascii.hexlify(self._get_double_sha256((msg + nonce).encode('utf-8'))).decode('ascii')
            if digest.endswith(suffix):
                return nonce
            i += 1

    def _get_double_sha256(self, msg):
        return hashlib.sha256(hashlib.sha256(msg).digest()).digest()


class GenesisBlock(Block):
    def __init__(self):
        super().__init__(transactions='AD9B477B42B22CDF18B1335603D07378ACE83561D8398FBFC8DE94196C65D806', previous_block_hash=None)

    def to_dict(self, include_nonce=True):
        print('[GB](to_dict)', include_nonce)
        d = {
            'transactions': self.transactions,
            'genesis_block': True,
        }
        if include_nonce:
            d['nonce'] = self.nonce
        return d