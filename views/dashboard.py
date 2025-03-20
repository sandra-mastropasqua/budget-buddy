import customtkinter as ctk
from models.account import Account
from models.transaction import Transaction
from models.user import User
from decimal import Decimal

class Dashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        self.title("Budget Buddy - Dashboard")
        # Retrieve user information
        user = User.get_user_by_id(user_id)
        full_name = f"{user['firstname']} {user['lastname']}" if user else "Utilisateur inconnu"

        # Display the user's name
        self.user_label = ctk.CTkLabel(self, text=f"Hello, {full_name} 👋", font=("Arial", 18))
        self.user_label.pack(pady=10)

        ctk.set_default_color_theme("dark-blue")
        ctk.set_appearance_mode("light")

        self.geometry("600x600")
        self.resizable(False, False)

        self.label_title = ctk.CTkLabel(self, text="Dashboard", font=("Arial", 24))
        self.label_title.pack(pady=20)

        self.balance_label = ctk.CTkLabel(self, text="Balance: 0€", font=("Arial", 18))
        self.balance_label.pack(pady=10)

        self.transactions_label = ctk.CTkLabel(self, text="Transaction History", font=("Arial", 16))
        self.transactions_label.pack(pady=10)

        self.transactions_list = ctk.CTkTextbox(self, width=500, height=150)
        self.transactions_list.pack(pady=10)

        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Amount") 
        self.amount_entry.pack(pady=5)

        self.credit_button = ctk.CTkButton(self, text="Credit", command=lambda: self.handle_amount("credit"))
        self.credit_button.pack(pady=5)

        self.debit_button = ctk.CTkButton(self, text="Debit", command=lambda: self.handle_amount("debit"))
        self.debit_button.pack(pady=5)

        self.logout_button = ctk.CTkButton(self, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)

        self.update_dashboard()

    def update_dashboard(self):
        """Updates balance and transaction history."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            self.balance_label.configure(text=f"Balance: {account.balance}€")

        transactions = Transaction.get_transactions(self.user_id)
        self.transactions_list.delete("1.0", "end")
        for t in transactions:
            self.transactions_list.insert("end", f"{t['date']} - {t['description']}: {t['amount']}€\n")

    def credit(self, amount):
        account = Account.get_account_by_user(self.user_id)
        if account:
            account.credit(amount)
            self.update_dashboard()

    def handle_amount(self, action):
        try:
            amount = Decimal(self.amount_entry.get())  # Convertir l'entrée en Decimal

            if action == "credit":
                self.credit(amount)  # Effectuer un crédit
            elif action == "debit":
                self.debit(amount)  # Effectuer un débit
            else:
                print("Erreur : action inconnue.")  # Sécurité

        except ValueError:
            print("Erreur : veuillez entrer un nombre valide.")  # Gestion d'erreur


    def debit(self, amount):
        account = Account.get_account_by_user(self.user_id)
        if account:
            account.debit(amount)
            self.update_dashboard()

    def logout(self):
        """Returns to the login screen."""
        from views.app import BudgetBuddyApp
        self.destroy()
        app = BudgetBuddyApp()
        app.mainloop()