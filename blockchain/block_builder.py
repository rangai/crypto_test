from .block import GenesisBlock
from .block import Block

class BlockBuilder:

    def __init__(self):
        print('[BB] Initializing BlockBuilder...')
        pass

    def generate_genesis_block(self):
        print('[BB](generate_genesis_block)')
        genesis_block = GenesisBlock()
        return genesis_block

    def generate_new_block(self, tx, previous_block_hash):
        print('[BB](generate_new_block)')
        new_block = Block(tx, previous_block_hash)
        return new_block


