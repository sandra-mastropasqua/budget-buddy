import customtkinter as ctk
from models.account import Account
from models.transaction import Transaction
from models.user import User
from decimal import Decimal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class Dashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.canvas = None  # ✅ Stocke le graphique

        self.title("Budget Buddy - Dashboard")
        self.geometry("1000x600")
        self.resizable(False, False)

        user = User.get_user_by_id(user_id)
        full_name = f"{user['firstname']} {user['lastname']}" if user else "Unknown User"

        # ✅ HEADER (Nom de l'utilisateur et solde)
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(fill="x", padx=10, pady=10)

        self.user_label = ctk.CTkLabel(self.header_frame, text=f"Hello, {full_name} 👋", font=("Arial", 18))
        self.user_label.pack(side="left", padx=10)

        self.balance_label = ctk.CTkLabel(self.header_frame, text="Balance: 0€", font=("Arial", 18))
        self.balance_label.pack(side="right", padx=10)

        # ✅ Création des onglets
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ Ajout des onglets
        self.overview_tab = self.tabview.add("Overview")
        self.transactions_tab = self.tabview.add("Transactions")
        self.settings_tab = self.tabview.add("Settings")

        # ✅ Configuration des onglets
        self.setup_overview_tab()
        self.setup_transactions_tab()
        self.setup_settings_tab()

        self.update_dashboard()

    def setup_overview_tab(self):
        """Configuration de l'onglet Aperçu"""
        self.transactions_label = ctk.CTkLabel(self.overview_tab, text="Transaction History", font=("Arial", 16))
        self.transactions_label.pack(pady=10)

        self.transactions_list = ctk.CTkTextbox(self.overview_tab, width=500, height=300)
        self.transactions_list.pack(pady=10)

        self.plot_transactions()

    def setup_transactions_tab(self):
        """Configuration de l'onglet Transactions"""
        ctk.CTkLabel(self.transactions_tab, text="Add a Transaction", font=("Arial", 16)).pack(pady=10)

        self.amount_entry = ctk.CTkEntry(self.transactions_tab, placeholder_text="Amount")
        self.amount_entry.pack(pady=5)

        self.description_entry = ctk.CTkEntry(self.transactions_tab, placeholder_text="Description")
        self.description_entry.pack(pady=5)

        self.credit_button = ctk.CTkButton(self.transactions_tab, text="Credit", command=lambda: self.handle_amount("credit"))
        self.credit_button.pack(pady=5)

        self.debit_button = ctk.CTkButton(self.transactions_tab, text="Debit", command=lambda: self.handle_amount("debit"))
        self.debit_button.pack(pady=5)

    def setup_settings_tab(self):
        """Configuration de l'onglet Paramètres"""
        ctk.CTkLabel(self.settings_tab, text="Settings", font=("Arial", 16)).pack(pady=10)

        self.logout_button = ctk.CTkButton(self.settings_tab, text="Logout", command=self.logout)
        self.logout_button.pack(pady=5)

    def update_dashboard(self):
        """Mise à jour du solde et de l'historique des transactions."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            self.balance_label.configure(text=f"Balance: {float(account.balance):.2f}€")

        transactions = Transaction.get_transactions(self.user_id)

        self.transactions_list.configure(state="normal")
        self.transactions_list.delete("1.0", "end")

        if not transactions:
            self.transactions_list.insert("end", "No transactions found.\n")
        else:
            for t in transactions:
                date = t.date.strftime("%d/%m/%Y %H:%M") if t.date else "Unknown Date"
                type_transaction = "Credit" if t.amount > 0 else "Debit"
                description = t.description
                amount = f"{float(t.amount):.2f}€"

                # ✅ Affichage d'une seule ligne : Date - Type - Description - Montant
                self.transactions_list.insert("end", f"{date} - {type_transaction} - {description}: {amount}\n")

        self.transactions_list.configure(state="disabled")
        self.plot_transactions()  # ✅ Mettre à jour le graphique après l'affichage des transactions


    def plot_transactions(self):
        """Affiche un graphique de l'évolution du solde du compte au fil du temps."""
        transactions = Transaction.get_transactions(self.user_id)

        if not transactions:
            print("No transactions to display.")
            return

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        transactions.sort(key=lambda t: t.date)

        account = Account.get_account_by_user(self.user_id)
        balance = float(account.balance) if account else 0  

        dates = []
        balances = []

        # ✅ Parcourir les transactions pour construire le bon solde
        for t in transactions:
            dates.append(t.date)
            balances.append(balance)
            balance -= float(t.amount)  # ✅ On enlève l'opération pour retrouver l'évolution correcte

        dates = [datetime.strftime(d, "%d/%m/%Y %H:%M") for d in dates]

        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(dates, balances, marker="o", linestyle="-", color="b", label="Balance")
        ax.set_xlabel("Date")
        ax.set_ylabel("Balance (€)")
        ax.set_title("Balance Evolution")
        ax.legend()
        ax.grid()
        plt.xticks(rotation=45)

        self.canvas = FigureCanvasTkAgg(fig, master=self.overview_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)


    def handle_amount(self, action):
        """Ajoute une transaction (crédit ou débit)."""
        try:
            amount = Decimal(self.amount_entry.get())
            description = self.description_entry.get()

            if action == "credit":
                self.credit(amount, description)
            elif action == "debit":
                self.debit(amount, description)
            else:
                print("Error: Unknown action.")

        except ValueError:
            print("Error: Please enter a valid number.")

    def credit(self, amount, description):
        """Ajoute un crédit."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            Transaction.create_transaction(self.user_id, description, amount)
            self.update_dashboard()

    def debit(self, amount, description):
        """Ajoute un débit."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            Transaction.create_transaction(self.user_id, description, -amount)
            self.update_dashboard()

    def logout(self):
        """Retour à l'écran de connexion."""
        from views.app import BudgetBuddyApp
        self.destroy()
        app = BudgetBuddyApp()
        app.mainloop()
