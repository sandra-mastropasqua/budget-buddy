import mysql.connector
import random
from dotenv import load_dotenv
import os
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

class Account:
    def __init__(self, account_id):
        """Initializes an account with its ID."""
        self.id = account_id
        self.balance = self.get_balance()

    @staticmethod
    def create_account(user_id) -> int:
        """Creates a bank account."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            account_number = f"BB-{random.randint(1000, 9999)}"

            cursor.execute("""
            INSERT INTO accounts (user_id, account_number)
            VALUES (%s, %s);
            """, (user_id, account_number))

            connection.commit()
            return cursor.lastrowid

        except mysql.connector.Error as err:
            print(f"Error MySQL : {err}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def get_balance(self):
        """Get the account balance."""
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (self.id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] if result else 0

    def update_balance(self, new_balance):
        """Update the account balance."""
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()
        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance, self.id))
        connection.commit()
        cursor.close()
        connection.close()
        self.balance = new_balance

    def credit(self, amount):
        """Add an amount to the account."""
        self.update_balance(self.balance + amount)

    def debit(self, amount):
        """Debits an amount if the balance is sufficient."""
        if self.balance >= amount:
            self.update_balance(self.balance - amount)
        else:
            raise ValueError("Insufficient funds.")

    def transfer(self, destination_account_id, amount):
        """Transfer an amount to another account."""
        if self.balance < amount:
            raise ValueError("Insufficient funds.")

        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()

        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (destination_account_id,))
        destination = cursor.fetchone()

        if not destination:
            raise ValueError("The recipient account does not exist.")

        new_source_balance = self.balance - amount
        new_dest_balance = destination[0] + amount

        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_source_balance, self.id))
        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_dest_balance, destination_account_id))
        connection.commit()

        cursor.close()
        connection.close()
        self.balance = new_source_balance