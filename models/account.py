import mysql.connector
import os
from dotenv import load_dotenv
from models.transaction import Transaction

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
            cursor.execute("INSERT INTO accounts (user_id, account_number, balance) VALUES (%s, %s, %s)", (user_id, account_number, 0.00))
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

            # Ensure all results are read before closing
            cursor.fetchall()  # Clear any remaining results

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

    def update_balance(self, amount):
        """Met à jour le solde du compte dans la base de données."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            print(f"DEBUG: Mise à jour du solde en DB - Ajout de {amount}€")
            cursor.execute("""
                UPDATE accounts SET balance = balance + %s WHERE id = %s;
            """, (amount, self.account_id))

            connection.commit()
            self.balance += amount

        except mysql.connector.Error as err:
            print(f"Error MySQL : {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

