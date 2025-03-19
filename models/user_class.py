import mysql.connector
from mysql.connector import errorcode
import bcrypt

class User:
    def __init__(self, id: int, first_name: str, name: str, email: str, password: str):
        self.id = id
        self.first_name = first_name
        self.name = name
        self.email = email
        self.__password = self.hash_password(password)
    
    def hash_password(self, password: str) -> str:
        """Hache le mot de passe de l'utilisateur."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Vérifie si le mot de passe donné correspond au mot de passe haché."""
        return bcrypt.checkpw(password.encode('utf-8'), self.__password.encode('utf-8'))

    @staticmethod
    def create_database_and_tables():
        """Crée la base de données et les tables nécessaires si elles n'existent pas déjà."""
        connection = None
        try:
            # Connexion à MySQL
            connection = mysql.connector.connect(
                host="localhost",
                user="root",  # Remplace par ton utilisateur MySQL
                password="pipicaca"  # Remplace par ton mot de passe MySQL
            )
            cursor = connection.cursor()

            # Créer la base de données si elle n'existe pas
            cursor.execute("CREATE DATABASE IF NOT EXISTS budget_buddy")
            print("Base de données 'budget_buddy' créée ou déjà existante.")

            # Utiliser la base de données
            cursor.execute("USE budget_buddy")

            # Créer les tables si elles n'existent pas
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                firstname VARCHAR(255) NOT NULL,
                lastname VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME DEFAULT NULL
            );
            """
            cursor.execute(create_users_table)
            print("Table 'users' créée ou déjà existante.")

            connection.commit()
        
        except mysql.connector.Error as err:
            print(f"Erreur MySQL : {err}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def create_user(first_name: str, last_name: str, email: str, password: str) -> bool:
        """Crée un utilisateur dans la base de données MySQL."""
        connection = None
        try:
            # Connexion à MySQL
            connection = mysql.connector.connect(
                host="localhost",
                user="root",  # Remplace par ton utilisateur MySQL
                password="pipicaca",  # Remplace par ton mot de passe MySQL
                database="budget_buddy"
            )
            cursor = connection.cursor()

            # Insérer un nouvel utilisateur dans la base de données
            insert_user_query = """
            INSERT INTO users (firstname, lastname, email, password)
            VALUES (%s, %s, %s, %s);
            """
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_data = (first_name, last_name, email, hashed_password)
            cursor.execute(insert_user_query, user_data)
            connection.commit()

            print(f"Utilisateur {first_name} {last_name} ajouté à la base de données.")
            return True
        
        except mysql.connector.Error as err:
            print(f"Erreur MySQL lors de la création de l'utilisateur : {err}")
            return False
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    @staticmethod
    def connect_user(email: str, password: str) -> bool:
        """Vérifie si un utilisateur existe avec l'email et le mot de passe fournis."""
        connection = None
        try:
            # Connexion à MySQL
            connection = mysql.connector.connect(
                host="localhost",
                user="root",  # Remplace par ton utilisateur MySQL
                password="pipicaca",  # Remplace par ton mot de passe MySQL
                database="budget_buddy"
            )
            cursor = connection.cursor()

            # Chercher l'utilisateur avec l'email donné
            cursor.execute("SELECT id, firstname, lastname, password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                user_id, first_name, last_name, stored_password = user
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    print(f"Connexion réussie pour {first_name} {last_name}.")
                    return True
                else:
                    print("Echec de la connexion : mot de passe incorrect.")
            else:
                print("Echec de la connexion : utilisateur non trouvé.")

            return False

        except mysql.connector.Error as err:
            print(f"Erreur MySQL lors de la connexion : {err}")
            return False
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

# Test du code
if __name__ == "__main__":
    # Créer la base de données et les tables
    User.create_database_and_tables()

    # Créer un utilisateur
    User.create_user("Chuck", "Steak", "chuck.steak@example.com", "password123")

    # Essayer de se connecter avec l'utilisateur créé
    User.connect_user("john.doe@example.com", "password123")