import mysql.connector
from models.user import User
from models.transaction import Transaction
from models.account import Account
from mysql.connector import Error

# ✅ TESTS
if __name__ == "__main__":
    User.create_database_and_tables()

    # 1️⃣ Création d'un utilisateur et d'un compte
    user_id = User.create_user("Guillaume", "Nurdin", "guillaume.nurdin@example.com", "secure123")
    if user_id:
        print(f"Utilisateur Guillaume créé avec ID {user_id}")

    # 2️⃣ Test Crédit et Débit sur le compte
    account_id = Account.create_account(user_id)
    if account_id:
        print(f"Compte créé avec ID {account_id}")

    account = Account(account_id)
    print(f"Solde initial : {account.balance}€")

    # Test Crédit
    account.credit(100)
    print(f"Solde après crédit de 100€ : {account.balance}€")

    # Test Débit
    account.debit(50)
    print(f"Solde après débit de 50€ : {account.balance}€")

    # 3️⃣ Test Transfert entre comptes
    recipient_id = Account.create_account(user_id)
    recipient_account = Account(recipient_id)
    account.transfer(recipient_id, 30)

    print(f"Solde après transfert : {account.balance}€")
    print(f"Solde du destinataire après réception : {recipient_account.get_balance()}€")

    # 4️⃣ Test des Transactions
    print("\nTest des transactions:")

    # Créer une transaction pour un crédit
    transaction_credit = Transaction.create_transaction(user_id, "Crédit de 100€", 100.00)
    if transaction_credit:
        print(f"Transaction crédit créée : {transaction_credit}")

    # Créer une transaction pour un débit
    transaction_debit = Transaction.create_transaction(user_id, "Débit de 50€", -50.00)
    if transaction_debit:
        print(f"Transaction débit créée : {transaction_debit}")

    # Afficher toutes les transactions pour l'utilisateur
    transactions = Transaction.get_transactions(user_id)
    print("\nToutes les transactions de l'utilisateur :")
    for t in transactions:
        print(t)