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
            print(f"INSERT INTO transactions: {user_id}, {description}, {amount}")
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
    def get_transactions(user_id, type_filter=None, description_filter=None, start_date=None, end_date=None, sort_order=None):
        """Récupère les transactions filtrées pour un utilisateur."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor(dictionary=True)

            query = """
            SELECT t.id, t.date, t.description, t.amount
            FROM transactions t
            WHERE t.user_id = %s
            """
            params = [user_id]

            # ✅ Filtre par type (Crédit / Débit)
            if type_filter and type_filter != "All":
                query += " AND t.amount " + ("> 0" if type_filter == "Credit" else "< 0")

            # ✅ Filtre par description
            if description_filter:
                query += " AND t.description LIKE %s"
                params.append(f"%{description_filter}%")

            # ✅ Filtre par date
            if start_date:
                query += " AND t.date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND t.date <= %s"
                params.append(end_date)

            # ✅ Tri par montant
            if sort_order:
                query += f" ORDER BY t.amount {sort_order}"

            cursor.execute(query, tuple(params))
            transactions = cursor.fetchall()

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
