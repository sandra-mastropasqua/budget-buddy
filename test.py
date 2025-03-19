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
        print(f"User created with ID {user_id}")

    # 2️⃣ Tests credit / debit
    account_id = Account.create_account(user_id)
    if account_id:
        print(f"Account created with ID {account_id}")

    account = Account(account_id)
    print(f"Initial balance : {account.balance}€")

    # Test credit
    account.credit(100)
    print(f"Balance after crediting €100 : {account.balance}€")

    # Test debit
    account.debit(50)
    print(f"Balance after debiting €50 : {account.balance}€")

    # 3️⃣ Test Transfer between accounts
    recipient_id = Account.create_account(user_id)
    recipient_account = Account(recipient_id)
    account.transfer(recipient_id, 30)

    print(f"Balance after transfer : {account.balance}€")
    print(f"Recipient's balance after receipt : {recipient_account.get_balance()}€")

    # 4️⃣ Test transactions
    print("\nTransactions tests:")

    # Creates a transaction for a credit
    transaction_credit = Transaction.create_transaction(user_id, "Credit of 100€", 100.00)
    if transaction_credit:
        print(f"Transaction credit created : {transaction_credit}")

    # Creates a transaction for a debit
    transaction_debit = Transaction.create_transaction(user_id, "Debit of 50€", -50.00)
    if transaction_debit:
        print(f"Transaction debit created : {transaction_debit}")

    # Prints all the transaction of the user
    transactions = Transaction.get_transactions(user_id)
    print("\nAll the user transactions :")
    for t in transactions:
        print(t)