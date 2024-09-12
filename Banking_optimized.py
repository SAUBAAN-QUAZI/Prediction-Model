import time
import random
import cProfile
import pstats
from functools import lru_cache

class Customer:
    def __init__(self, customer_id, balance):
        self.customer_id = customer_id
        self.balance = balance

class Bank:
    def __init__(self):
        self.accounts = {}
        self.existing_accounts = set()  # Track account existence more efficiently
        self.transactions = []

    def create_account(self, customer_id, balance):
        if customer_id in self.existing_accounts:  # Faster account existence check
            return
        self.accounts[customer_id] = Customer(customer_id, balance)
        self.existing_accounts.add(customer_id)

    def delete_account(self, customer_id):
        if customer_id not in self.existing_accounts:
            return
        del self.accounts[customer_id]
        self.existing_accounts.remove(customer_id)  # Update the account existence set

    def update_account(self, customer_id, new_balance):
        account = self.accounts.get(customer_id)
        if not account:
            return
        account.balance = new_balance

    def deposit(self, customer_id, amount):
        account = self.accounts.get(customer_id)
        if not account:
            return
        account.balance += amount
        self.transactions.append((customer_id, "deposit", amount))

    def batch_deposit(self, transactions):  # Batch process deposits
        for customer_id, amount in transactions:
            account = self.accounts.get(customer_id)
            if account:
                account.balance += amount
                self.transactions.append((customer_id, "deposit", amount))

    def withdraw(self, customer_id, amount):
        account = self.accounts.get(customer_id)
        if not account:
            return
        if account.balance < amount:
            return
        account.balance -= amount
        self.transactions.append((customer_id, "withdrawal", amount))

    def transfer(self, sender_id, receiver_id, amount):
        sender = self.accounts.get(sender_id)
        receiver = self.accounts.get(receiver_id)
        if not sender or not receiver:
            return
        if sender.balance < amount:
            return
        sender.balance -= amount
        receiver.balance += amount
        self.transactions.append((sender_id, "transfer", amount))

    def get_balance(self, customer_id):
        account = self.accounts.get(customer_id)
        if not account:
            return
        return account.balance

    def get_transactions(self):
        return self.transactions

@lru_cache(maxsize=100)  # Optional caching for repeated customer data access
def get_customer_info(bank, customer_id):
    return bank.accounts.get(customer_id)

def run_benchmark(bank):
    # Batch process deposits
    deposits = [(i, random.randint(1, 100)) for i in range(10000)]
    bank.batch_deposit(deposits)

    # Process withdrawals
    for i in range(10000):
        bank.withdraw(i, random.randint(1, 100))

    # Process transfers
    for i in range(10000):
        bank.transfer(i, (i + 1) % 10000, random.randint(1, 100))

def main():
    bank = Bank()

    
    for i in range(10000):
        bank.create_account(i, random.randint(100, 1000))

    # Run benchmark
    run_benchmark(bank)

if __name__ == "__main__":
    profiler = cProfile.Profile()  
    profiler.enable()              

    main()  

    profiler.disable() 

    # Create statistics object to analyze the profile data
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumtime')  # Sort by cumulative time
    stats.print_stats(10)  # Print the top 10 results
