import customtkinter as ctk
from models.user import User
from models.account import Account
from models.transaction import Transaction
from dotenv import load_dotenv
import os

load_dotenv()

# Main window configuration
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class BudgetBuddyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Budget Buddy - Login")
        self.geometry("400x400")
        self.resizable(False, False)
        
        self.create_login_interface()
        
    def create_login_interface(self):
        """Creates the login interface."""
        
        self.label_title = ctk.CTkLabel(self, text="Budget Buddy", font=("Arial", 24))
        self.label_title.pack(pady=20)
        
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email")
        self.email_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)
        
        self.login_button = ctk.CTkButton(self, text="Login", command=self.login)
        self.login_button.pack(pady=10)
        
        self.register_button = ctk.CTkButton(self, text="Create Account", command=self.create_account)
        self.register_button.pack(pady=5)
        
        self.message_label = ctk.CTkLabel(self, text="", text_color="red")
        self.message_label.pack(pady=10)
        
    def login(self):
        """Handles user authentication."""
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        user = User.authenticate(email, password)
        
        if user:
            self.message_label.configure(text="Login successful!", text_color="green")
            self.after(1000, lambda: self.open_dashboard(user["id"]))
        else:
            self.message_label.configure(text="Incorrect email or password", text_color="red")
        
    def create_account(self):
        """Displays the account creation window and adds the user to the database."""
        register_window = ctk.CTkToplevel(self)
        register_window.title("Create Account")
        register_window.geometry("400x400")

        ctk.CTkLabel(register_window, text="Create Account", font=("Arial", 20)).pack(pady=10)
        
        first_name_entry = ctk.CTkEntry(register_window, placeholder_text="First Name")
        first_name_entry.pack(pady=5)
        
        last_name_entry = ctk.CTkEntry(register_window, placeholder_text="Last Name")
        last_name_entry.pack(pady=5)
        
        email_entry = ctk.CTkEntry(register_window, placeholder_text="Email")
        email_entry.pack(pady=5)
        
        password_entry = ctk.CTkEntry(register_window, placeholder_text="Password", show="*")
        password_entry.pack(pady=5)
        
        def submit_registration():
            """Submits registration and creates a bank account."""
            User.create_database_and_tables()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            email = email_entry.get()
            password = password_entry.get()

            user_id = User.create_user(first_name, last_name, email, password)
            if user_id:
                account_id = Account.create_account(user_id)  # Creates an account for the user
                if account_id:
                    self.message_label.configure(text="Account successfully created!", text_color="green")
                    register_window.destroy()
                else:
                    self.message_label.configure(text="Error creating bank account", text_color="red")
            else:
                self.message_label.configure(text="Error creating user account", text_color="red")

        submit_button = ctk.CTkButton(register_window, text="Sign Up", command=submit_registration)
        submit_button.pack(pady=10)

    def open_dashboard(self, user_id):
        """Opens the dashboard interface."""
        self.destroy()
        dashboard = Dashboard(user_id)
        dashboard.mainloop()

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
        self.destroy()
        app = BudgetBuddyApp()
        app.mainloop()

if __name__ == "__main__":
    app = BudgetBuddyApp()
    app.mainloop()
