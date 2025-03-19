import mysql.connector
import random

class Account:
    def __init__(self, account_id):
        """Initialise un compte avec son ID."""
        self.id = account_id
        self.balance = self.get_balance()

    @staticmethod
    def create_account(user_id, account_type='courant') -> int:
        """Crée un compte bancaire pour un utilisateur."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="YoelIT2024!",
                database="budget_buddy"
            )
            cursor = connection.cursor()

            account_number = f"BB-{random.randint(1000, 9999)}"

            cursor.execute("""
            INSERT INTO accounts (user_id, account_number, account_type)
            VALUES (%s, %s, %s);
            """, (user_id, account_number, account_type))

            connection.commit()
            print(f"Compte {account_number} créé avec succès.")
            return cursor.lastrowid

        except mysql.connector.Error as err:
            print(f"Erreur MySQL lors de la création du compte : {err}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def get_balance(self):
        """Récupère le solde du compte."""
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="YoelIT2024!",
            database="budget_buddy"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (self.id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] if result else 0

    def update_balance(self, new_balance):
        """Met à jour le solde du compte."""
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="YoelIT2024!",
            database="budget_buddy"
        )
        cursor = connection.cursor()
        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance, self.id))
        connection.commit()
        cursor.close()
        connection.close()
        self.balance = new_balance

    def credit(self, amount):
        """Ajoute un montant au solde."""
        self.update_balance(self.balance + amount)

    def debit(self, amount):
        """Débite un montant si le solde est suffisant."""
        if self.balance >= amount:
            self.update_balance(self.balance - amount)
        else:
            raise ValueError("Fonds insuffisants")

    def transfer(self, destination_account_id, amount):
        """Transfère un montant à un autre compte."""
        if self.balance < amount:
            raise ValueError("Fonds insuffisants")

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="YoelIT2024!",
            database="budget_buddy"
        )
        cursor = connection.cursor()

        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (destination_account_id,))
        destination = cursor.fetchone()

        if not destination:
            raise ValueError("Le compte destinataire n'existe pas")

        new_source_balance = self.balance - amount
        new_dest_balance = destination[0] + amount

        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_source_balance, self.id))
        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_dest_balance, destination_account_id))
        connection.commit()

        cursor.close()
        connection.close()
        self.balance = new_source_balance