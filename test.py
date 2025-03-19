import mysql.connector
from models.user import User
from models.transaction import Transaction
from models.account import Account
from mysql.connector import Error

# ✅ TESTS
if __name__ == "__main__":
    User.create_database_and_tables()

    # 1️⃣ Create an user account
    user_id = User.create_user("Guillaume", "Nurdin", "guillaume.nurdin@example.com", "secure123")
    if user_id:
        print(f"User successfully created {user_id}")

    # 2️⃣ Test credit and debits on the account
    account_id = Account.create_account(user_id)
    if account_id:
        print(f"Account created with an ID {account_id}")

    account = Account(account_id)
    print(f"Initial amount : {account.balance}€")

    # Test Credit
    account.credit(100)
    print(f"Amount after the credit 100€ : {account.balance}€")

    # Test Debit
    account.debit(50)
    print(f"Amount after the debit 50€ : {account.balance}€")

    # 3️⃣ Test Transfer between accounts
    recipient_id = Account.create_account(user_id)
    recipient_account = Account(recipient_id)
    account.transfer(recipient_id, 30)

    print(f"Amount after tranfer : {account.balance}€")
    print(f"Recipient's balance after receipt : {recipient_account.get_balance()}€")

    # 4️⃣ Test Transactions
    print("\nTest of the transactions:")

    # Create a transaction for a debit
    transaction_credit = Transaction.create_transaction(user_id, "Credit of 100€", 100.00)
    if transaction_credit:
        print(f"Credit transaction created : {transaction_credit}")

    transaction_debit = Transaction.create_transaction(user_id, "Debit of 50€", -50.00)
    if transaction_debit:
        print(f"Debit transaction created : {transaction_debit}")

    # Print all the transactions for the user
    transactions = Transaction.get_transactions(user_id)
    print("\nAll the user's transactions :")
    for t in transactions:
        print(t) 