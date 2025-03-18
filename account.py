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
        return result[0] if result else None

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
            raise ValueError("Solde insuffisant")

    def transfer(self, destination_account_id, amount):
        """Transfère un montant vers un autre compte si solde suffisant."""
        if self.balance < amount:
            raise ValueError("Solde insuffisant pour effectuer le transfert")

        cursor = self.db.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (destination_account_id,))
        destination = cursor.fetchone()
        if not destination:
            raise ValueError("Le compte de destination n'existe pas")

        new_source_balance = self.balance - amount
        new_dest_balance = destination[0] + amount

        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_source_balance, self.id))
        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_dest_balance, destination_account_id))
        self.db.commit()

        self.balance = new_source_balance




# Connexion à la base de données MySQL
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='ton_utilisateur',
        password='ton_mot_de_passe',
        database='gestion_finance'
    )
    
    if conn.is_connected():
        print("Connexion réussie à la base de données")

    # Création d'un compte
    compte1 = Account(conn, 1)  # Compte ID 1
    compte2 = Account(conn, 2)  # Compte ID 2

    # Déposer de l'argent
    compte1.credit(500)

    # Retirer de l'argent
    compte1.debit(200)

    # Transférer de l'argent vers un autre compte
    compte1.transfer(2, 100)  # Transfert de 100€ vers le compte ID 2

except Error as e:
    print("Erreur de connexion à la base de données", e)

finally:
    if conn.is_connected():
        conn.close()
        print("Connexion fermée")
