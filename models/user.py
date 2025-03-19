import mysql.connector
import bcrypt
import random
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

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
    def get_user_by_id(user_id):
        """Retrieve user details from database."""
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT firstname, lastname FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()
        return user


    @staticmethod
    def create_database_and_tables():
        """Creates database and tables if they don't exist."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD
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

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                description VARCHAR(255) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)

            connection.commit()
            print("Database successfully created.")

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
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
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

    def authenticate(email: str, password: str):
        """Compares email and password with database."""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                return user  # Returns user if login succeed
            else:
                return None  # Returns None if login wrong

        except mysql.connector.Error as err:
            print(f"Erreur MySQL : {err}")
            return None
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()