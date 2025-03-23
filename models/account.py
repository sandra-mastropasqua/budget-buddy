import mysql.connector
import os
from decimal import Decimal
from dotenv import load_dotenv
from models.transaction import Transaction

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

class Account:
    def __init__(self, account_id, account_number, balance):
        """Initialise un compte bancaire avec Decimal pour la balance"""
        self.account_id = account_id
        self.account_number = account_number
        self.balance = Decimal(balance)

    @staticmethod
    def create_account(user_id):
        """Crée un compte avec un numéro unique"""
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        try:
            with conn.cursor() as cursor:
                account_number = f"BB{user_id:06d}"
                cursor.execute(
                    "INSERT INTO accounts (user_id, account_number, balance) VALUES (%s, %s, %s)",
                    (user_id, account_number, 0.00)
                )
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_account_by_user(user_id):
        """Récupère le compte avec conversion en Decimal"""
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                
                if not result:
                    return None
                
                return Account(
                    account_id=result["id"],
                    account_number=result["account_number"],
                    balance=Decimal(result["balance"])
                )
        finally:
            conn.close()

    def update_balance(self, amount):
        """Met à jour le solde de manière atomique"""
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        try:
            with conn.cursor() as cursor:
                # Mise à jour atomique dans la base
                cursor.execute(
                    "UPDATE accounts SET balance = balance + %s WHERE id = %s",
                    (float(amount), self.account_id)
                )
                conn.commit()
                
                # Mise à jour de l'instance
                self.balance += Decimal(amount)
                
                # Création de la transaction
                transaction_type = "Credit" if amount > 0 else "Debit"
                Transaction.create_transaction(
                    self.account_id,
                    transaction_type,
                    float(amount)
                )
        finally:
            conn.close()

    def credit(self, amount):
        """Dépôt d'argent"""
        if amount <= 0:
            raise ValueError("Le montant doit être positif")
        self.update_balance(amount)

    def debit(self, amount):
        """Retrait d'argent"""
        if amount <= 0:
            raise ValueError("Le montant doit être positif")
        if self.balance < amount:
            raise ValueError("Solde insuffisant")
        self.update_balance(-amount)

    def get_balance(self):
        """Retourne le solde actuel"""
        return self.balance