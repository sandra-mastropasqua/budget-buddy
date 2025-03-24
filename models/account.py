# models/account.py
import mysql.connector
import os
from dotenv import load_dotenv
from models.transaction import Transaction
from tkinter import messagebox
from datetime import datetime

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

class Account:
    def __init__(self, account_id, account_number, balance):
        """Initializes a bank account object."""
        self.account_id = account_id
        self.account_number = account_number
        self.balance = balance

    @staticmethod
    def create_account(user_id):
        """Creates an account for a given user."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            account_number = f"BB{user_id:06d}"  # Generates a unique account number
            cursor.execute("INSERT INTO accounts (user_id, account_number, balance) VALUES (%s, %s, %s)",
                           (user_id, account_number, 0.00))
            connection.commit()

            return cursor.lastrowid  # Returns the created account ID

        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def get_account_by_user(user_id):
        """Retrieves a user's bank account using their ID."""
        connection = None
        account = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()  # Fetch the first row

            if result:
                account = Account(
                    account_id=result["id"],
                    account_number=result["account_number"],
                    balance=result["balance"]
                )

            # Clear any remaining results
            cursor.fetchall()

        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

        return account

    def credit(self, amount):
        """Adds an amount to the account balance."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            self.balance += amount
            cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (self.balance, self.account_id))
            connection.commit()

            Transaction.create_transaction(self.account_id, "Credit", amount)

        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def debit(self, amount):
        """Withdraws an amount from the account balance."""
        if self.balance < amount:
            print("Insufficient funds.")
            return

        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            self.balance -= amount
            cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (self.balance, self.account_id))
            connection.commit()

            Transaction.create_transaction(self.account_id, "Debit", -amount)

        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def transfer_funds(from_account_id, to_account_number, amount):
        print(f"DEBUG: transfer_funds(from={from_account_id}, to={to_account_number}, amount={amount})")

        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            connection.autocommit = False  # 🔴 Désactiver l'autocommit pour contrôler la transaction
            cursor = connection.cursor(dictionary=True)

            # 🔎 Vérifier le solde du compte source avec un verrou `FOR UPDATE`
            cursor.execute("SELECT balance FROM accounts WHERE id = %s FOR UPDATE", (from_account_id,))
            from_account = cursor.fetchone()

            if not from_account or from_account["balance"] < amount:
                print("DEBUG: Solde insuffisant ou compte inexistant")
                return False

            # 🔎 Récupérer l'ID du compte destinataire avec un verrou `FOR UPDATE`
            cursor.execute("""
                SELECT accounts.id FROM accounts
                JOIN users ON accounts.user_id = users.id
                WHERE users.email = %s
                FOR UPDATE
            """, (to_account_number,))
            to_account = cursor.fetchone()

            if not to_account:
                print("DEBUG: Destination account not found")
                return False

            to_account_id = int(to_account["id"])

            # 🔎 Vérifier l'existence du compte destinataire
            cursor.execute("SELECT balance FROM accounts WHERE id = %s FOR UPDATE", (to_account_id,))
            to_account_balance = cursor.fetchone()

            if not to_account_balance:
                print("DEBUG: Impossible to get the sold of the account")
                return False

            # ✅ Calcul des nouveaux soldes
            new_balance_from = float(from_account["balance"]) - amount
            new_balance_to = float(to_account_balance["balance"]) + amount

            # 🔄 DÉBUT TRANSACTION
            cursor.execute("START TRANSACTION;")

            # 🏦 Mise à jour des soldes
            cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance_from, from_account_id))
            cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance_to, to_account_id))

            # 📜 Enregistrement des transactions
            Transaction.create_transaction(from_account_id, f"Transfer to {to_account_number}", -amount, datetime.now())
            Transaction.create_transaction(to_account_id, f"Transfer received from {from_account_id}", amount, datetime.now())

            # ✅ Valider la transaction
            connection.commit()
            print("DEBUG: Commit OK, transfert terminé")

            return True

        except mysql.connector.Error as err:
            print(f"DEBUG: Exception MySQL => {err}")
            if connection:
                connection.rollback()  # ❌ Annuler la transaction en cas d'erreur
            return False

        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
