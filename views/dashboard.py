import customtkinter as ctk
from models.account import Account
from models.transaction import Transaction

class Dashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        self.title("Budget Buddy - Dashboard")
        self.geometry("600x500")
        self.resizable(False, False)

        self.label_title = ctk.CTkLabel(self, text="Dashboard", font=("Arial", 24))
        self.label_title.pack(pady=20)

        self.balance_label = ctk.CTkLabel(self, text="Balance: 0€", font=("Arial", 18))
        self.balance_label.pack(pady=10)

        self.transactions_label = ctk.CTkLabel(self, text="Transaction History", font=("Arial", 16))
        self.transactions_label.pack(pady=10)

        self.transactions_list = ctk.CTkTextbox(self, width=500, height=200)
        self.transactions_list.pack(pady=10)

        self.credit_button = ctk.CTkButton(self, text="Credit 100€", command=self.credit)
        self.credit_button.pack(pady=5)

        self.debit_button = ctk.CTkButton(self, text="Debit 50€", command=self.debit)
        self.debit_button.pack(pady=5)

        self.update_dashboard()

        self.logout_button = ctk.CTkButton(self, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)

    def update_dashboard(self):
        """Updates balance and transaction history."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            self.balance_label.configure(text=f"Balance: {account.balance}€")

        transactions = Transaction.get_transactions(self.user_id)
        self.transactions_list.delete("1.0", "end")
        for t in transactions:
            self.transactions_list.insert("end", f"{t['date']} - {t['description']}: {t['amount']}€\n")

    def credit(self):
        """Credits 100€ to the account."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            account.credit(100)
            self.update_dashboard()

    def debit(self):
        """Debits 50€ from the account."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            account.debit(50)
            self.update_dashboard()

    def logout(self):
        """Returns to the login screen."""
        from views.app import BudgetBuddyApp  # ✅ Moved import here to avoid circular dependency
        self.destroy()
        app = BudgetBuddyApp()
        app.mainloop()
