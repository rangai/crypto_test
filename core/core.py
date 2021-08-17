import time
import socket, threading, json
import pickle

from blockchain.blockchain_manager import BlockchainManager
from blockchain.block_builder import BlockBuilder
from tx.transaction_pool import TransactionPool
from p2p.connection_manager import ConnectionManager
from p2p.message_manager import (
    MSG_NEW_TRANSACTION,
    MSG_NEW_BLOCK,
    MSG_REQUEST_FULL_CHAIN,
    RSP_FULL_CHAIN,
)

STATE_INIT = 0
STATE_STANDBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3

CHECK_INTERVAL = 10

class Core:

    def __init__(self, my_port=50082, node_host=None, node_port=None):
        self.server_state = STATE_INIT
        print('[ C] Initializing node...')
        self.my_ip = self.__get_myip()
        print('[ C] IP address is set to ... ', self.my_ip)
        self.my_port = my_port
        self.cm = ConnectionManager(self.my_ip, self.my_port, self.__handle_message)
        self.node_host = node_host
        self.node_port = node_port

        self.bb = BlockBuilder()
        self.flag_stop_block_building = False
        my_genesis_block = self.bb.generate_genesis_block()
        self.bm = BlockchainManager(my_genesis_block.to_dict())
        self.prev_block_hash = self.bm.get_hash(my_genesis_block.to_dict()) 
        self.tp = TransactionPool()

    def start_block_building(self):
        print('[ C](start_block_building)')
        self.bb_timer = threading.Timer(CHECK_INTERVAL, self.__generate_block_with_tp)
        self.bb_timer.start()

    def stop_block_building(self):
        print('[ C](stop_block_building) Thread for __generate_block_with_tp is stopped now')
        self.bb_timer.cancel()

    def start(self):
        print('[ C](start)')
        self.server_state = STATE_STANDBY
        self.cm.start()
        self.start_block_building()


    def join_network(self):
        print('[ C](join_network)')
        if self.node_host != None:
            self.server_state = STATE_CONNECTED_TO_NETWORK
            self.cm.connect_to_network(self.node_host, self.node_port)
        else:
            print('[ C](join_network) This server is runnning as Genesis Core Node...')

    def shutdown(self):
        self.server_state = STATE_SHUTTING_DOWN
        print('[ C](shutdown) Shutting down...')
        self.cm.connection_close()
        self.stop_block_building()

    def get_all_chains_for_resolve_conflict(self):
        print('[ C](get_all_chains_for_resolve_conflict)')
        new_message = self.cm.get_message_text(MSG_REQUEST_FULL_CHAIN)
        self.cm.broadcast(new_message)

    def send_message_to_core(self, msg_type, msg):
        print('[ C](send_message_to_core)')
        msg_txt = self.cm.get_message_text(msg_type, msg)
        print('[ C](send_message_to_core) msg is ...', msg_txt)
        self.cm.send_msg((self.my_ip, self.my_port), msg_txt)


    def __generate_block_with_tp(self):
        print('[ C](__generate_block_with_tp) Thread for generate_block_with_tp started.')
        while self.flag_stop_block_building is not True:
            result = self.tp.get_stored_transactions()
            if result == None:
                print('[ C](__generate_block_with_tp) Transaction Pool is empty ...')
                break
            new_tp = self.bm.remove_useless_transaction(result)
            self.tp.renew_my_transactions(new_tp)
            if len(new_tp) == 0:
                break
            new_block = self.bb.generate_new_block(result, self.prev_block_hash)
            self.bm.set_new_block(new_block.to_dict())
            self.prev_block_hash = self.bm.get_hash(new_block.to_dict())
            index = len(result)
            self.tp.clear_my_transactions(index)
            break

        print('[ C](__generate_block_with_tp) Current Blockchain is ... ', self.bm.chain)
        print('[ C](__generate_block_with_tp) Current prev_block_hash is ... ', self.prev_block_hash)
        self.flag_stop_block_building = False
        self.is_bb_running = False
        self.bb_timer = threading.Timer(CHECK_INTERVAL, self.__generate_block_with_tp)
        self.bb_timer.start()


    def __handle_message(self, msg, node=None):
        print('[ C](__handle_message)', msg, node)
        if node != None:
            if msg[1] == MSG_REQUEST_FULL_CHAIN:
                print('[ C](__handle_message) MSG_REQUEST_FULL_CHAIN: for reply to', node)
                mychain = self.bm.get_my_blockchain()
                print('[ C](__handle_message) My chain:', mychain)
                chain_data = pickle.dumps(mychain, 0).decode()
                new_message = self.cm.get_message_text(RSP_FULL_CHAIN, chain_data)
                self.cm.send_msg(node,new_message)
        else:
            if msg[1] == MSG_NEW_TRANSACTION:
                new_transaction = json.loads(msg[3])
                print("[ C](__handle_message) MSG_NEW_TRANSACTION: received new_transaction", new_transaction)
                current_transactions = self.tp.get_stored_transactions()
                if new_transaction in current_transactions:
                    print("[ C](__handle_message) This transaction is already pooled:", new_transaction)
                    return
                self.tp.set_new_transaction(new_transaction)
                new_message = self.cm.get_message_text(MSG_NEW_TRANSACTION, json.dumps(new_transaction))
                self.cm.broadcast(new_message)
            elif msg[1] == MSG_NEW_BLOCK:
                new_block = json.loads(msg[3])
                print('[ C](__handle_message) MSG_NEW_BLOCK:', new_block)
                if self.bm.is_valid_block(self.prev_block_hash, new_block):
                    if self.is_bb_running:
                        self.flag_stop_block_building = True
                    self.prev_block_hash = self.bm.get_hash(new_block)
                    self.bm.set_new_block(new_block)
                else:
                    self.get_all_chains_for_resolve_conflict()
            elif msg[1] == RSP_FULL_CHAIN:
                new_block_chain = pickle.loads(msg[3].encode('utf8'))
                print('[ C](__handle_message) RSP_FULL_CHAIN: New Blockchain', new_block_chain)
                result, pool_for_orphan_blocks = self.bm.resolve_conflicts(new_block_chain)
                print('[ C](__handle_message) Blockchain received')
                if result is not None:
                    self.prev_block_hash = result
                    if len(pool_for_orphan_blocks) != 0:
                        new_transactions = self.bm.get_transactions_from_orphan_blocks(pool_for_orphan_blocks)
                        for t in new_transactions:
                            self.tp.set_new_transaction(t)
                else:
                    print('[ C](__handle_message) Received blockchain is useless...')

    def __get_myip(self):
        print('[ C](__get_myip)')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
