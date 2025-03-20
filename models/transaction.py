import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

class Transaction:
    def __init__(self, id: int, user_id: int, description: str, amount: float, date: str):
        self.id = id
        self.user_id = user_id
        self.description = description
        self.amount = amount
        self.date = date

    @staticmethod
    def create_transaction(user_id: int, description: str, amount: float) -> 'Transaction':
        """Creates a transaction for a user and returns the transaction."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()
            transaction_date = datetime.now()
            cursor.execute("""
            INSERT INTO transactions (user_id, description, amount)
            VALUES (%s, %s, %s);
            """, (user_id, description, amount))

            connection.commit()
            return Transaction(cursor.lastrowid, user_id, description, amount, None)

        except mysql.connector.Error as err:
            print(f"Error MySQL : {err}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def get_transactions(user_id: int):
        """Retrieve all transactions for a specific user."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            cursor.execute("""
            SELECT id, user_id, description, amount, date FROM transactions WHERE user_id = %s;
            """, (user_id,))

            transactions = []
            for row in cursor.fetchall():
                transactions.append(Transaction(row[0], row[1], row[2], row[3], row[4]))
            print(transactions)
            return transactions

        except mysql.connector.Error as err:
            print(f"Error MySQL : {err}")
            return []
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def __repr__(self):
        return f"Transaction(id={self.id}, user_id={self.user_id}, description={self.description}, amount={self.amount}, date={self.date})"
