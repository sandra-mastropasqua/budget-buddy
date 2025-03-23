import customtkinter as ctk
from models.account import Account
from models.transaction import Transaction
from models.user import User
from decimal import Decimal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from views.transfer_window2 import TransferWindow
from datetime import datetime
from tkinter import messagebox
import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()


class Dashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.canvas = None

        self.title("Budget Buddy - Dashboard")
        self.geometry("1000x600")
        self.resizable(False, False)

        user = User.get_user_by_id(user_id)
        full_name = f"{user['firstname']} {user['lastname']}" if user else "Unknown User"

        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(fill="x", padx=10, pady=10)

        self.user_label = ctk.CTkLabel(self.header_frame, text=f"Hello, {full_name} 👋", font=("Arial", 18))
        self.user_label.pack(side="left", padx=10)

        self.balance_label = ctk.CTkLabel(self.header_frame, text="Balance: 0€", font=("Arial", 18))
        self.balance_label.pack(side="right", padx=10)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.transactions_tab = self.tabview.add("Transactions")
        self.overview_tab = self.tabview.add("Overview")
        self.settings_tab = self.tabview.add("Settings")

        self.setup_transactions_tab()
        self.setup_overview_tab()
        self.setup_settings_tab()

        self.update_dashboard()

    def setup_overview_tab(self):
        """Configuration de l'onglet Aperçu avec une organisation en colonnes."""

        # ✅ Cadre principal pour contenir les deux sections
        self.overview_frame = ctk.CTkFrame(self.overview_tab)
        self.overview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ Frame de gauche : Liste des transactions
        self.transactions_frame = ctk.CTkFrame(self.overview_frame, width=400)
        self.transactions_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.transactions_label = ctk.CTkLabel(self.transactions_frame, text="Transaction History", font=("Arial", 16))
        self.transactions_label.pack(pady=10)

        # ✅ Utiliser un Frame pour les transactions (au lieu de CTkTextbox)
        self.transactions_container = ctk.CTkFrame(self.transactions_frame)
        self.transactions_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ Frame de droite : Graphique des transactions
        self.graph_frame = ctk.CTkFrame(self.overview_frame, width=500, height=400)
        self.graph_frame.pack(side="right", expand=True, padx=10, pady=10)


    def setup_transactions_tab(self):
        """Configuration de l'onglet Transactions avec filtres et actions."""

        self.transactions_layout = ctk.CTkFrame(self.transactions_tab)
        self.transactions_layout.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ 1️⃣ FRAME FILTRES
        self.filter_frame = ctk.CTkFrame(self.transactions_layout)
        self.filter_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.filter_frame, text="Type:").grid(row=0, column=0, padx=5)
        self.type_filter = ctk.CTkComboBox(self.filter_frame, values=["All", "Credit", "Debit"])
        self.type_filter.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(self.filter_frame, text="Description:").grid(row=0, column=2, padx=5)
        self.description_filter = ctk.CTkEntry(self.filter_frame, placeholder_text="Ex: Courses, Loyer...")
        self.description_filter.grid(row=0, column=3, padx=5)

        ctk.CTkLabel(self.filter_frame, text="From:").grid(row=1, column=0, padx=5)
        self.start_date_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.grid(row=1, column=1, padx=5)

        ctk.CTkLabel(self.filter_frame, text="To:").grid(row=1, column=2, padx=5)
        self.end_date_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.grid(row=1, column=3, padx=5)

        ctk.CTkLabel(self.filter_frame, text="Sort by Amount:").grid(row=2, column=0, padx=5)
        self.amount_sort = ctk.CTkComboBox(self.filter_frame, values=["None", "Ascending", "Descending"])
        self.amount_sort.grid(row=2, column=1, padx=5)

        self.filter_button = ctk.CTkButton(self.filter_frame, text="Filter", command=self.apply_filters)
        self.filter_button.grid(row=2, column=3, padx=5, pady=5)

        # ✅ 2️⃣ FRAME PRINCIPAL POUR LISTE + ACTIONS
        self.transactions_pane = ctk.CTkFrame(self.transactions_layout)
        self.transactions_pane.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ Partie gauche : Liste des transactions
        self.transactions_list_frame = ctk.CTkFrame(self.transactions_pane, width=500)
        self.transactions_list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.transactions_label = ctk.CTkLabel(self.transactions_list_frame, text="Transaction History", font=("Arial", 16))
        self.transactions_label.pack(pady=10)

        # ✅ Cadre pour les transactions
        self.transactions_container = ctk.CTkFrame(self.transactions_list_frame)
        self.transactions_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ Partie droite : Saisie des crédits/débits
        self.actions_frame = ctk.CTkFrame(self.transactions_pane, width=300)
        self.actions_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.actions_frame, text="New Transaction", font=("Arial", 16)).pack(pady=10)

        self.amount_entry = ctk.CTkEntry(self.actions_frame, placeholder_text="Amount")
        self.amount_entry.pack(pady=5)

        self.description_entry = ctk.CTkEntry(self.actions_frame, placeholder_text="Description")
        self.description_entry.pack(pady=5)

        self.credit_button = ctk.CTkButton(self.actions_frame, text="Credit", command=lambda: self.handle_amount("credit"))
        self.credit_button.pack(pady=5)

        self.debit_button = ctk.CTkButton(self.actions_frame, text="Debit", command=lambda: self.handle_amount("debit"))
        self.debit_button.pack(pady=5)

        self.transfer_button = ctk.CTkButton(self, text="Transfer money", command=self.open_transfer_window)
        self.transfer_button.pack(pady=10)


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

        # ✅ Supprimer les anciennes transactions affichées
        for widget in self.transactions_container.winfo_children():
            widget.destroy()

        if not transactions:
            ctk.CTkLabel(self.transactions_container, text="No transactions found.", font=("Arial", 14)).pack(pady=5)
        else:
            for t in transactions:
                date = t["date"].strftime("%d/%m/%Y %H:%M") if t["date"] else "Unknown Date"
                type_transaction = "Credit" if t["amount"] > 0 else "Debit"
                description = t["description"]
                amount = f"{float(t['amount']):.2f}€"

                # ✅ Affichage sous forme de labels (lecture seule)
                ctk.CTkLabel(
                    self.transactions_container,
                    text=f"{date} - {type_transaction} - {description}: {amount}",
                    font=("Arial", 14)
                ).pack(anchor="w", padx=5, pady=2)

        self.plot_transactions()  # ✅ Mettre à jour le graphique après l'affichage des transactions


    def plot_transactions(self):
        """Affiche un graphique de l'évolution du solde du compte au fil du temps."""
        transactions = Transaction.get_transactions(self.user_id)

        if not transactions:
            print("No transactions to display.")
            return

        # ✅ Trier les transactions par date
        transactions.sort(key=lambda t: t["date"])

        account = Account.get_account_by_user(self.user_id)
        initial_balance = 0  # ✅ On part de 0 et on reconstruit le solde

        dates = []
        balances = []
        current_balance = initial_balance  

        for t in transactions:
            dates.append(t["date"])  # ✅ Accéder à la date comme un dictionnaire
            current_balance += float(t["amount"])
            balances.append(current_balance)

        # ✅ Convertir les dates en format lisible
        dates = [datetime.strftime(d, "%d/%m/%Y %H:%M") for d in dates]

        # ✅ Création du graphique avec une hauteur augmentée
        fig, ax = plt.subplots(figsize=(7, 4))  # ✅ Augmenter la taille

        ax.plot(dates, balances, marker="o", linestyle="-", color="b", label="Balance")
        ax.set_xlabel("Date")
        ax.set_ylabel("Balance (€)")
        ax.set_title("Balance Evolution")
        ax.legend()
        ax.grid()

        plt.xticks(rotation=60)  # ✅ Incliner les dates pour qu'elles soient lisibles

        # ✅ Affichage du graphique dans `self.graph_frame`
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

    def handle_amount(self, action):
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
            account.update_balance(amount)  # ✅ Mise à jour en base de données
            Transaction.create_transaction(self.user_id, description, amount)
            self.update_dashboard()  # ✅ Recharge l'interface

    def debit(self, amount, description):
        """Ajoute un débit."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            account.update_balance(-amount)  # ✅ Mise à jour en base de données
            Transaction.create_transaction(self.user_id, description, -amount)
            self.update_dashboard()  # ✅ Recharge l'interface


    def apply_filters(self):
        """Applique les filtres sélectionnés et met à jour l'affichage des transactions."""
        type_filter = self.type_filter.get()
        description_filter = self.description_filter.get().strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        amount_sort = self.amount_sort.get()

        sort_order = "ASC" if amount_sort == "Ascending" else "DESC" if amount_sort == "Descending" else None

        # ✅ Récupérer les transactions filtrées
        transactions = Transaction.get_transactions(
            user_id=self.user_id,
            type_filter=type_filter,
            description_filter=description_filter,
            start_date=start_date,
            end_date=end_date,
            sort_order=sort_order
        )

        # ✅ Supprimer les anciennes transactions affichées
        for widget in self.transactions_container.winfo_children():
            widget.destroy()

        if not transactions:
            ctk.CTkLabel(self.transactions_container, text="No transactions found.", font=("Arial", 14)).pack(pady=5)
        else:
            for t in transactions:
                date = t["date"].strftime("%d/%m/%Y") if t["date"] else "Unknown"
                type_transaction = "Credit" if t["amount"] > 0 else "Debit"
                description = t["description"]
                amount = f"{float(t['amount']):.2f}€"

                # ✅ Affichage sous forme de labels (lecture seule)
                ctk.CTkLabel(
                    self.transactions_container,
                    text=f"{date} - {type_transaction} - {description}: {amount}",
                    font=("Arial", 14)
                ).pack(anchor="w", padx=5, pady=2)

    def open_transfer_window(self):
        """Open the transfer window"""
        TransferWindow(self.user_id, self)

    def logout(self):
        """Back to the screen"""
        from views.app import BudgetBuddyApp
        self.destroy()
        app = BudgetBuddyApp()
        app.mainloop()
    
    def update_balance(self):
        """Update the displayed balance after a transfer"""
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (self.user_id,))
        account = cursor.fetchone()

        if account :
            new_balance = account["balance"]
            self.balance_label.configure(text=f"Balance :{new_balance}euros")
            self.update_idletasks()
            messagebox.showinfo("DEBUG",f"New balance : {new_balance}euros ")
        
        cursor.close()
        connection.close()
