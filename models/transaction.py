# models/transaction.py
import mysql.connector
from datetime import datetime
from decimal import Decimal
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

class Transaction:
    @classmethod
    def create_transaction(cls, account_id, transaction_type, amount):
        """Crée une nouvelle transaction dans la base de données"""
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        try:
            with conn.cursor(dictionary=True) as cursor:
                # REQUÊTE CORRIGÉE
                cursor.execute(
                    """SELECT t.* FROM transactions t
                    INNER JOIN accounts a ON t.account_id = a.id
                    WHERE a.user_id = %s
                    ORDER BY t.date DESC""",
                    (user_id,)
                )
                return cursor.fetchall()
        finally:
            conn.close()
    @classmethod
    def get_transactions(cls, user_id):
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """SELECT t.* FROM transactions t
                    JOIN accounts a ON t.account_id = a.id  # Correction ici
                    WHERE a.user_id = %s
                    ORDER BY t.date DESC""",
                    (user_id,)
                )
                return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def get_filtered_transactions(cls, user_id, filters):
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        try:
            with conn.cursor(dictionary=True) as cursor:
                # Construction dynamique de la requête
                base_query = """SELECT t.* FROM transactions t
                              JOIN accounts a ON t.account_id = a.id
                              WHERE a.user_id = %s"""
                params = [user_id]
                conditions = []

                # Filtre par type
                if filters.get('transaction_type') and filters['transaction_type'] != 'All':
                    if filters['transaction_type'] == 'Credit':
                        conditions.append("t.amount > 0")
                    else:
                        conditions.append("t.amount < 0")

                # Filtre par description
                if filters.get('description'):
                    conditions.append("t.description LIKE %s")
                    params.append(f"%{filters['description']}%")

                # Filtre par date
                if filters.get('start_date') and filters.get('end_date'):
                    conditions.append("t.date BETWEEN %s AND %s")
                    params.extend([filters['start_date'], filters['end_date']])

                # Tri
                order_clause = ""
                if filters.get('sort_order'):
                    if filters['sort_order'] == 'Ascending':
                        order_clause = "ORDER BY t.amount ASC"
                    elif filters['sort_order'] == 'Descending':
                        order_clause = "ORDER BY t.amount DESC"

                # Assemblage final de la requête
                full_query = base_query
                if conditions:
                    full_query += " AND " + " AND ".join(conditions)
                full_query += " " + order_clause

                cursor.execute(full_query, tuple(params))
                return cursor.fetchall()
        finally:
            conn.close()