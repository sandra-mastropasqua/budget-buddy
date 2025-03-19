import mysql.connector
from mysql.connector import Error

class Account:
    def __init__(self, db_connection, account_id):
        self.db = db_connection
        self.id = account_id
        self.balance = self.get_balance()

    def get_balance(self):
        """Récupère le solde actuel du compte depuis la base de données."""
        cursor = self.db.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (self.id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def update_balance(self, new_balance):
        """Met à jour le solde du compte dans la base de données."""
        cursor = self.db.cursor()
        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance, self.id))
        self.db.commit()
        self.balance = new_balance

    def credit(self, amount):
        """Ajoute un montant au solde."""
        new_balance = self.balance + amount
        self.update_balance(new_balance)

    def debit(self, amount):
        """Retire un montant du solde si suffisant."""
        if self.balance >= amount:
            new_balance = self.balance - amount
            self.update_balance(new_balance)
        else:
            raise ValueError("Unsufficient founds")

    def transfer(self, destination_account_id, amount):
        """Transfère un montant vers un autre compte si solde suffisant."""
        if self.balance < amount:
            raise ValueError("Unsufficient founds")

        cursor = self.db.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (destination_account_id,))
        destination = cursor.fetchone()
        if not destination:
            raise ValueError("Destination account does not exist")

        new_source_balance = self.balance - amount
        new_dest_balance = destination[0] + amount

        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_source_balance, self.id))
        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_dest_balance, destination_account_id))
        self.db.commit()

        self.balance = new_source_balance

