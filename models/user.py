import mysql.connector
import bcrypt
import random
from datetime import datetime

class User:
    def __init__(self, id: int, first_name: str, last_name: str, email: str, password: str):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.__password = self.hash_password(password)

    def hash_password(self, password: str) -> str:
        """Hash the password."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Check if the password fits with the hash one."""
        return bcrypt.checkpw(password.encode('utf-8'), self.__password.encode('utf-8'))

    @staticmethod
    def create_database_and_tables():
        """Creates database and tables if they don't exist."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="YoelIT2024!"
            )
            cursor = connection.cursor()

            cursor.execute("CREATE DATABASE IF NOT EXISTS budget_buddy")
            cursor.execute("USE budget_buddy")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                firstname VARCHAR(255) NOT NULL,
                lastname VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                account_number VARCHAR(20) UNIQUE NOT NULL,
                balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                description VARCHAR(255) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)

            connection.commit()
            print("Database successfully created.")

        except mysql.connector.Error as err:
            print(f"Erreur MySQL : {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def create_user(first_name: str, last_name: str, email: str, password: str) -> int:
        """Creates a user and return its ID."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="YoelIT2024!",
                database="budget_buddy"
            )
            cursor = connection.cursor()

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            cursor.execute("""
            INSERT INTO users (firstname, lastname, email, password)
            VALUES (%s, %s, %s, %s);
            """, (first_name, last_name, email, hashed_password))

            connection.commit()
            return cursor.lastrowid

        except mysql.connector.Error as err:
            print(f"Error MySQL : {err}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

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
