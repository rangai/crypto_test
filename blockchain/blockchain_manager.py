import json
import hashlib
import binascii
import copy
import threading


class BlockchainManager:

    def __init__(self, genesis_block):
        print('[BM] Initializing BlockchainManager...')    
        self.chain = []
        self.lock = threading.Lock()
        self.__set_my_genesis_block(genesis_block)

    def __set_my_genesis_block(self, block):
        print('[BM](__set_my_genesis_block)', block)
        self.genesis_block = block
        self.chain.append(block)

    def set_new_block(self, block):
        print('[BM](set_new_block)')
        with self.lock:
            self.chain.append(block)

    def renew_my_blockchain(self, blockchain):
        print('[BM](renew_my_blockchain)')
        with self.lock:
            if self.is_valid_chain(blockchain):
                self.chain = blockchain
                latest_block = self.chain[-1]
                return self.get_hash(latest_block)
            else:
                print('[BM](renew_my_blockchain) Invalid chain cannot be set...')
                return None

    def is_valid_chain(self,chain):
        print('[BM](is_valid_chain)')
        last_block = chain[0]
        cur = 1

        while cur < len(chain):
            block = self.chain[cur]
            if block['previous_block'] != self.get_hash(last_block):
                return False
                
            last_block = block
            cur += 1

        return True

    def get_my_blockchain(self):
        print('[BM](get_my_blockchain)')
        if len(self.chain) > 1:
            return self.chain
        else:
            return None

    def get_transactions_from_orphan_blocks(self, orphan_blocks):
        print('[BM](get_transactions_from_orphan_blocks)', orphan_blocks)
        cur = 1
        new_transactions = []

        while cur < len(orphan_blocks):
            block = orphan_blocks[cur]
            transactions = block['transactions']
            target = self.remove_useless_transaction(transactions)
            for t in target:
                new_transactions.append(t)
        
        return new_transactions

    def remove_useless_transaction(self, tx_pool):
        print('[BM](remove_useless_transaction)', tx_pool)
        if len(tx_pool) != 0:
            cur = 1

            while cur < len(self.chain):
                block = self.chain[cur]
                transactions = block['transactions']
                for t in transactions:
                    for x in tx_pool:
                        if t == json.dumps(x):
                            print('[BM](remove_useless_transaction) Already exist in my blockchain :', x)
                            tx_pool.remove(x)
                
                cur += 1
            return tx_pool
        else:
            print('[BM] No transaction to be removed.')
            return []

    def resolve_conflicts(self, chain):
        print('[BM](resolve_conflicts)', chain)
        mychain_len = len(self.chain)
        new_chain_len = len(chain)
        pool_for_orphan_blocks = copy.deepcopy(self.chain)
        if new_chain_len > mychain_len:
            for b in pool_for_orphan_blocks:
                for c in chain:
                    if b == c:
                        pool_for_orphan_blocks.remove(b)
                    
            result = self.renew_my_blockchain(chain)
            print("[BM](resolve_conflicts)", result)
            if result is not None:
                return result, pool_for_orphan_blocks
            else:
                return None, []
        else:
            print('[BM](resolve_conflicts) Invalid chain cannot be set...')
            return None, []

    def is_valid_block(self, prev_block_hash, block, difficulty=3):
        print('[BM] is_valid_block', prev_block_hash, block, difficulty)
        suffix = '0' * difficulty
        block_4_pow = copy.deepcopy(block)
        nonce = block_4_pow['nonce']
        del block_4_pow['nonce']
        print('[BM]', block_4_pow)

        message = json.dumps(block_4_pow, sort_keys=True)
        nonce = str(nonce)

        if block['previous_block'] != prev_block_hash:
            print('[BM] Invalid block (bad previous_block)')
            print('[BM]', block['previous_block'])
            print(prev_block_hash)
            return False
        else:
            digest = binascii.hexlify(self._get_double_sha256((message + nonce).encode('utf-8'))).decode('ascii')
            if digest.endswith(suffix):
                print('[BM] This seems valid block')
                return True
            else:
                print('[BM] Invalid block (bad nonce)')
                print('[BM] nonce :' , nonce)
                print('[BM] digest :' , digest)
                print('[BM] suffix', suffix)
                return False

    def is_valid_chain(self, chain):
        print('[BM] is_valid_chain', chain)
        last_block = chain[0]
        cur = 1

        while cur < len(chain):
            block = chain[cur]
            if self.is_valid_block(self.get_hash(last_block), block) is not True:
                return False
            
            last_block = chain[cur]
            cur += 1

        return True

    def _get_double_sha256(self, msg):
        return hashlib.sha256(hashlib.sha256(msg).digest()).digest()

    def get_hash(self, block):
        block_string = json.dumps(block, sort_keys=True)
        return binascii.hexlify(self._get_double_sha256((block_string).encode('utf-8'))).decode('ascii')
