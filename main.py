import customtkinter as ctk
from models.user import User
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration principale de la fenêtre
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class BudgetBuddyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Budget Buddy - Connexion")
        self.geometry("400x400")
        self.resizable(False, False)
        
        self.create_login_interface()
        
    def create_login_interface(self):
        """Création de l'interface de connexion."""
        
        self.label_title = ctk.CTkLabel(self, text="Budget Buddy", font=("Arial", 24))
        self.label_title.pack(pady=20)
        
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email")
        self.email_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*")
        self.password_entry.pack(pady=10)
        
        self.login_button = ctk.CTkButton(self, text="Se connecter", command=self.login)
        self.login_button.pack(pady=10)
        
        self.register_button = ctk.CTkButton(self, text="Créer un compte", command=self.create_account)
        self.register_button.pack(pady=5)
        
        self.message_label = ctk.CTkLabel(self, text="", text_color="red")
        self.message_label.pack(pady=10)
        
    def login(self):
        """Gère l'authentification de l'utilisateur."""
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        user = self.authenticate_user(email, password)
        
        if user:
            self.message_label.configure(text="Connexion réussie!", text_color="green")
            self.after(1000, self.open_dashboard)  # Redirige vers le tableau de bord
        else:
            self.message_label.configure(text="Email ou mot de passe incorrect", text_color="red")
        
    def authenticate_user(self, email, password):
        """Vérifie les identifiants dans la base de données."""
        # Connexion à la base et vérification
        return True  # À remplacer par la logique réelle
        
    def create_account(self):
        """Redirige vers l'interface d'inscription."""
        print("Redirection vers la création de compte...")
        
    def open_dashboard(self):
        """Ouvre l'interface du tableau de bord."""
        print("Ouverture du tableau de bord...")
        

if __name__ == "__main__":
    app = BudgetBuddyApp()
    app.mainloop()