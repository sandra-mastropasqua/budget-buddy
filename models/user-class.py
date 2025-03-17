import bcrypt

users_db = []

class User:
    def __init__(self, id: int, first_name: str, name: str, email: str, password: str):
        self.id = id
        self.first_name = first_name
        self.name = name
        self.email = email
        self.__password = self.hash_password(password)
    
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.__password.encode('utf-8'))
    
    def create_account(self, first_name: str, name: str, email: str, password: str) -> bool:
        user_id = len(users_db) + 1
        new_user = User(user_id, first_name, name, email, password)
        users_db.append(new_user)
        print(f"Compte créé pour {first_name} {name} avec l'ID {user_id}")
        return new_user

    def connect(self, email: str, password: str) -> bool:
        for user in users_db:
            if user.email == email and user.check_password(password):
                print(f"Connexion réussie pour {user.first_name} {user.name}")
                return True
        print("Echec de la connexion : Email ou mot de passe incorrect.")
        return False