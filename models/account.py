import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

class Account:
    def __init__(self, account_id, account_number, balance):
        """Initialise un objet compte bancaire."""
        self.account_id = account_id
        self.account_number = account_number
        self.balance = balance

    @staticmethod
    def create_account(user_id):
        """Crée un compte pour un utilisateur donné."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            account_number = f"BB{user_id:06d}"  # Génère un numéro de compte unique
            cursor.execute("INSERT INTO accounts (user_id, account_number, balance) VALUES (%s, %s, %s)", (user_id, account_number, 0.00))
            connection.commit()

            return cursor.lastrowid  # Retourne l'ID du compte créé

        except mysql.connector.Error as err:
            print(f"Erreur MySQL : {err}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()


    @staticmethod
    def get_account_by_user(user_id):
        """Récupère le compte bancaire d'un utilisateur à partir de son ID."""
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
            result = cursor.fetchone()  # Récupère la première ligne

            if result:
                account = Account(
                    account_id=result["id"],
                    account_number=result["account_number"],
                    balance=result["balance"]
                )

            # S'assurer que tous les résultats sont lus avant de fermer
            cursor.fetchall()  # Vider les résultats restants (s'il y en a)

        except mysql.connector.Error as err:
            print(f"Erreur MySQL : {err}")

        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

        return account

    def credit(self, amount):
        """Ajoute un montant au solde du compte."""
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

        except mysql.connector.Error as err:
            print(f"Erreur MySQL : {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def debit(self, amount):
        """Retire un montant du solde du compte."""
        if self.balance < amount:
            print("Fonds insuffisants.")
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

        except mysql.connector.Error as err:
            print(f"Erreur MySQL : {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
