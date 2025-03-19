import customtkinter as ctk
from models.user import User
from models.account import Account
from models.transaction import Transaction
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
        
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)
        
        self.login_button = ctk.CTkButton(self, text="Login", command=self.login)
        self.login_button.pack(pady=10)
        
        self.register_button = ctk.CTkButton(self, text="Create account", command=self.create_account)
        self.register_button.pack(pady=5)
        
        self.message_label = ctk.CTkLabel(self, text="", text_color="red")
        self.message_label.pack(pady=10)
        
    def login(self):
        """Gère l'authentification de l'utilisateur."""
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        user = User.authenticate(email, password)  # Récupère l'utilisateur
        
        if user:
            self.message_label.configure(text="Connexion réussie!", text_color="green")
            self.after(1000, lambda: self.open_dashboard(user["id"]))  # Passe l'ID de l'utilisateur
        else:
            self.message_label.configure(text="Email ou mot de passe incorrect", text_color="red")

        
    def create_account(self):
        """Affiche une fenêtre de création de compte et ajoute l'utilisateur en base."""
        register_window = ctk.CTkToplevel(self)
        register_window.title("Créer un compte")
        register_window.geometry("400x400")
        
        ctk.CTkLabel(register_window, text="Créer un compte", font=("Arial", 20)).pack(pady=10)
        
        first_name_entry = ctk.CTkEntry(register_window, placeholder_text="Prénom")
        first_name_entry.pack(pady=5)
        
        last_name_entry = ctk.CTkEntry(register_window, placeholder_text="Nom")
        last_name_entry.pack(pady=5)
        
        email_entry = ctk.CTkEntry(register_window, placeholder_text="Email")
        email_entry.pack(pady=5)
        
        password_entry = ctk.CTkEntry(register_window, placeholder_text="Mot de passe", show="*")
        password_entry.pack(pady=5)
        
        def submit_registration():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            
            user_id = User.create_user(first_name, last_name, email, password)
            if user_id:
                Account.create_account(user_id)
                self.message_label.configure(text="Compte créé avec succès!", text_color="green")
                register_window.destroy()
            else:
                self.message_label.configure(text="Erreur lors de la création du compte", text_color="red")
        
        submit_button = ctk.CTkButton(register_window, text="S'inscrire", command=submit_registration)
        submit_button.pack(pady=10)
        
    def open_dashboard(self, user_id):
        """Ouvre l'interface du tableau de bord."""
        self.destroy()
        dashboard = Dashboard(user_id)
        dashboard.mainloop()

class Dashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        self.title("Budget Buddy - Tableau de Bord")
        self.geometry("600x400")
        self.resizable(False, False)
        
        self.label_title = ctk.CTkLabel(self, text="Tableau de Bord", font=("Arial", 24))
        self.label_title.pack(pady=20)
        
        self.balance_label = ctk.CTkLabel(self, text="Solde: 0€", font=("Arial", 18))
        self.balance_label.pack(pady=10)
        
        self.transactions_label = ctk.CTkLabel(self, text="Historique des transactions", font=("Arial", 16))
        self.transactions_label.pack(pady=10)
        
        self.transactions_list = ctk.CTkTextbox(self, width=500, height=200)
        self.transactions_list.pack(pady=10)
        
        self.update_dashboard()
        
        self.logout_button = ctk.CTkButton(self, text="Se déconnecter", command=self.logout)
        self.logout_button.pack(pady=10)
        
    def update_dashboard(self):
        """Mise à jour du solde et des transactions."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            self.balance_label.configure(text=f"Solde: {account.balance}€")
        
        transactions = Transaction.get_transactions(self.user_id)
        self.transactions_list.delete("1.0", "end")
        for t in transactions:
            self.transactions_list.insert("end", f"{t.date} - {t.description}: {t.amount}€\n")
        
    def logout(self):
        """Retour à l'écran de connexion."""
        self.destroy()
        app = BudgetBuddyApp()
        app.mainloop()

if __name__ == "__main__":
    app = BudgetBuddyApp()
    app.mainloop()