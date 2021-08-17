import threading

class TransactionPool:

    def __init__(self):
        print('[TX] Initializing TransactionPool...')
        self.transactions = []
        self.lock = threading.Lock()

    def set_new_transaction(self, transaction):
        with self.lock:
            print('[TX](set_new_transaction)', transaction)
            self.transactions.append(transaction)

    def clear_my_transactions(self, index):
        with self.lock:
            if index <= len(self.transactions):
                new_transactions = self.transactions
                del new_transactions[0:index]
                print('[TX](clear_my_transactions) transaction is now refreshed ... ', new_transactions)
                self.transactions = new_transactions

    def get_stored_transactions(self):
        if len(self.transactions) > 0:
            print('[TX](get_stored_transaction)', self.transactions)
            return self.transactions
        else:
            print("[TX](get_stored_transaction) Currently, it seems transaction pool is empty...")
            return []

    def renew_my_transactions(self, transactions):
        with self.lock:
            print('[TX](renew_my_transactions)', transactions)
            self.transactions = transactions