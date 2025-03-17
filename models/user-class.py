import bcrypt

class User:
    def __init__(self, id: int, first_name: str, name: str, email: str, password: str):
        self.id = id
        self.first_name = first_name
        self.name = name
        self.email = email
        self.__password = self.hash_password(password)
    
    def hash_password(self, password: str) -> str:
        """Hash the password using bcrypt before storing it."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.__password.encode('utf-8'))
