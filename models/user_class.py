import mysql.connector
import bcrypt
import random

class User:
    def __init__(self, id: int, first_name: str, last_name: str, email: str, password: str):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.__password = self.hash_password(password)

    def hash_password(self, password: str) -> str:
        """Hash the password."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Check if the password fits with the hash one."""
        return bcrypt.checkpw(password.encode('utf-8'), self.__password.encode('utf-8'))

    @staticmethod
    def create_database_and_tables():
        """Creates database and tables if they don't exist."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="YoelIT2024!"
            )
            cursor = connection.cursor()

            cursor.execute("CREATE DATABASE IF NOT EXISTS budget_buddy")
            cursor.execute("USE budget_buddy")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                firstname VARCHAR(255) NOT NULL,
                lastname VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                account_number VARCHAR(20) UNIQUE NOT NULL,
                balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)

            connection.commit()
            print("Database successfully creates.")

        except mysql.connector.Error as err:
            print(f"Erreur MySQL : {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def create_user(first_name: str, last_name: str, email: str, password: str) -> int:
        """Creates a user and return its ID."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="YoelIT2024!",
                database="budget_buddy"
            )
            cursor = connection.cursor()

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            cursor.execute("""
            INSERT INTO users (firstname, lastname, email, password)
            VALUES (%s, %s, %s, %s);
            """, (first_name, last_name, email, hashed_password))

            connection.commit()
            return cursor.lastrowid

        except mysql.connector.Error as err:
            print(f"Error MySQL : {err}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()


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
                host="localhost",
                user="root",
                password="YoelIT2024!",
                database="budget_buddy"
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
        """Update the account balance."""
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
        """Add an amount to the account."""
        self.update_balance(self.balance + amount)

    def debit(self, amount):
        """Debits an amount if the balance is sufficient."""
        if self.balance >= amount:
            self.update_balance(self.balance - amount)
        else:
            raise ValueError("Insufficient funds.")

    def transfer(self, destination_account_id, amount):
        """Transfer an amount to an other account."""
        if self.balance < amount:
            raise ValueError("Insufficient funds.")

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
            raise ValueError("The recipient account does not exist.")

        new_source_balance = self.balance - amount
        new_dest_balance = destination[0] + amount

        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_source_balance, self.id))
        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_dest_balance, destination_account_id))
        connection.commit()

        cursor.close()
        connection.close()
        self.balance = new_source_balance


# ✅ TESTS
if __name__ == "__main__":
    User.create_database_and_tables()

    # 1️⃣ Création d'un utilisateur et d'un compte
    user_id = User.create_user("Guillaume", "Nurdin", "guillaume.nurdin@example.com", "secure123")
    if user_id:
        print(f"Utilisateur Guillaume créé avec ID {user_id}")

    account_id = Account.create_account(user_id)
    if account_id:
        print(f"Compte créé avec ID {account_id}")

    # 2️⃣ Test Crédit et Débit
    account = Account(account_id)
    print(f"Solde initial : {account.balance}€")
    
    account.credit(100)
    print(f"Solde après crédit de 100€ : {account.balance}€")

    account.debit(50)
    print(f"Solde après débit de 50€ : {account.balance}€")

    # 3️⃣ Test Transfert
    recipient_id = Account.create_account(user_id)
    recipient_account = Account(recipient_id)
    account.transfer(recipient_id, 30)

    print(f"Solde après transfert : {account.balance}€")
    print(f"Solde du destinataire après réception : {recipient_account.get_balance()}€")