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
        self.canvas = None  # Pour gérer le graphique

        self.title("Budget Buddy - Dashboard")
        self.geometry("1000x600")
        self.resizable(False, False)

        user = User.get_user_by_id(user_id)
        full_name = f"{user['firstname']} {user['lastname']}" if user else "Unknown User"

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(fill="x", padx=10, pady=10)

        self.user_label = ctk.CTkLabel(self.header_frame, text=f"Hello, {full_name} 👋", font=("Arial", 18))
        self.user_label.pack(side="left", padx=10)

        self.balance_label = ctk.CTkLabel(self.header_frame, text="Balance: 0€", font=("Arial", 18))
        self.balance_label.pack(side="right", padx=10)

        # Onglets
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
        """Configuration de l'onglet Aperçu"""
        self.overview_frame = ctk.CTkFrame(self.overview_tab)
        self.overview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Partie gauche : Historique des transactions
        self.overview_transactions_frame = ctk.CTkFrame(self.overview_frame, width=400)
        self.overview_transactions_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.overview_transactions_frame, text="Recent Transactions", font=("Arial", 16)).pack(pady=10)
        
        self.overview_transactions_container = ctk.CTkScrollableFrame(self.overview_transactions_frame)
        self.overview_transactions_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Partie droite : Graphique
        self.graph_frame = ctk.CTkFrame(self.overview_frame, width=500)
        self.graph_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def setup_transactions_tab(self):
        """Configuration de l'onglet Transactions"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.transactions_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame des filtres
        filter_frame = ctk.CTkFrame(main_frame)
        filter_frame.pack(fill="x", pady=5)

        # Filtre par type
        ctk.CTkLabel(filter_frame, text="Type:").grid(row=0, column=0, padx=5)
        self.type_filter = ctk.CTkComboBox(filter_frame, 
                                        values=["All", "Credit", "Debit"])
        self.type_filter.grid(row=0, column=1, padx=5)

        # Filtre par description
        ctk.CTkLabel(filter_frame, text="Description:").grid(row=0, column=2, padx=5)
        self.description_filter = ctk.CTkEntry(filter_frame)
        self.description_filter.grid(row=0, column=3, padx=5)

        # Filtre par dates
        ctk.CTkLabel(filter_frame, text="From:").grid(row=1, column=0, padx=5)
        self.start_date_entry = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.grid(row=1, column=1, padx=5)

        ctk.CTkLabel(filter_frame, text="To:").grid(row=1, column=2, padx=5)
        self.end_date_entry = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.grid(row=1, column=3, padx=5)

        # Tri par montant
        ctk.CTkLabel(filter_frame, text="Sort:").grid(row=1, column=4, padx=5)
        self.amount_sort = ctk.CTkComboBox(filter_frame, 
                                        values=["None", "Ascending", "Descending"])
        self.amount_sort.grid(row=1, column=5, padx=5)

        # Bouton d'application des filtres
        self.filter_btn = ctk.CTkButton(filter_frame, 
                                    text="Apply Filters", 
                                    command=self.apply_filters)
        self.filter_btn.grid(row=1, column=6, padx=10)

        # Liste des transactions
        self.transactions_container = ctk.CTkScrollableFrame(main_frame)
        self.transactions_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Nouvelle transaction
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x", pady=10)

        self.amount_entry = ctk.CTkEntry(action_frame, placeholder_text="Amount", width=150)
        self.amount_entry.pack(side="left", padx=5)

        self.description_entry = ctk.CTkEntry(action_frame, placeholder_text="Description", width=300)
        self.description_entry.pack(side="left", padx=5)

        self.credit_btn = ctk.CTkButton(action_frame, text="+ Credit", 
                                     command=lambda: self.handle_transaction("credit"))
        self.credit_btn.pack(side="left", padx=5)

        self.debit_btn = ctk.CTkButton(action_frame, text="- Debit", 
                                    command=lambda: self.handle_transaction("debit"))
        self.debit_btn.pack(side="left", padx=5)

    def setup_settings_tab(self):
        """Configuration de l'onglet Paramètres"""
        ctk.CTkLabel(self.settings_tab, text="Settings", font=("Arial", 16)).pack(pady=10)
        ctk.CTkButton(self.settings_tab, text="Logout", command=self.logout).pack(pady=5)

    def update_dashboard(self):
        """Met à jour toutes les données"""
        # Balance
        account = Account.get_account_by_user(self.user_id)
        if account:
            self.balance_label.configure(text=f"Balance: {float(account.balance):.2f}€")

        # Transactions dans l'onglet Transactions
        self.update_transactions_list(Transaction.get_transactions(self.user_id))

        # Transactions dans l'onglet Overview
        self.update_overview_list(Transaction.get_transactions(self.user_id))

        # Graphique
        self.plot_transactions()

    def update_transactions_list(self, transactions):
        """Met à jour la liste dans l'onglet Transactions"""
        for widget in self.transactions_container.winfo_children():
            widget.destroy()

        if not transactions:
            ctk.CTkLabel(self.transactions_container, text="No transactions found").pack()
            return

        for transaction in transactions:
            frame = ctk.CTkFrame(self.transactions_container)
            frame.pack(fill="x", pady=2)

            date_str = transaction["date"].strftime("%d/%m/%Y")
            amount = f"+{transaction['amount']}" if transaction['amount'] > 0 else f"{transaction['amount']}"
            color = "green" if transaction['amount'] > 0 else "red"

            ctk.CTkLabel(frame, text=date_str, width=100).pack(side="left")
            ctk.CTkLabel(frame, text=transaction['description'], width=300).pack(side="left")
            ctk.CTkLabel(frame, text=amount, text_color=color, width=100).pack(side="right")

    def update_overview_list(self, transactions):
        """Met à jour la liste dans l'onglet Overview"""
        for widget in self.overview_transactions_container.winfo_children():
            widget.destroy()

        for transaction in transactions[:5]:  # Dernières 5 transactions
            frame = ctk.CTkFrame(self.overview_transactions_container)
            frame.pack(fill="x", pady=2)

            date_str = transaction["date"].strftime("%d/%m/%Y")
            amount = f"{transaction['amount']:.2f}€"
            color = "green" if transaction['amount'] > 0 else "red"

            ctk.CTkLabel(frame, text=f"{date_str} - {transaction['description']}:", width=250).pack(side="left")
            ctk.CTkLabel(frame, text=amount, text_color=color, width=100).pack(side="right")

    def plot_transactions(self):
        """Affiche correctement l'évolution du solde"""
        # Nettoyer l'ancien graphique
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Récupérer le compte et les transactions
        account = Account.get_account_by_user(self.user_id)
        transactions = Transaction.get_transactions(self.user_id)
        
        if not account or not transactions:
            return

        # Trier les transactions par date croissante
        transactions_sorted = sorted(transactions, key=lambda t: t['date'])

        # Calculer l'évolution du solde
        dates = []
        balances = []
        current_balance = account.balance  # Commence avec le solde actuel

        # Remonter dans l'historique à partir du solde initial
        for t in reversed(transactions_sorted):
            current_balance -= t['amount']  # Annule chaque opération dans l'ordre inverse
            dates.insert(0, t['date'])      # Ajoute les dates au début
            balances.insert(0, current_balance)

        # Ajouter le dernier solde actuel
        dates.append(datetime.now())
        balances.append(account.balance)

        # Création du graphique
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(dates, balances, 'g-', marker='o', linewidth=2)
        
        ax.set_title("Évolution du solde")
        ax.set_xlabel("Date")
        ax.set_ylabel("Solde (€)")
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Intégration dans Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def handle_transaction(self, transaction_type):
        try:
            amount = Decimal(self.amount_entry.get())
            description = self.description_entry.get().strip()
            
            if not description:
                raise ValueError("Description manquante")

            account = Account.get_account_by_user(self.user_id)
            if not account:
                raise ValueError("Compte introuvable")

            if transaction_type == "credit":
                account.credit(amount)
            else:
                account.debit(amount)

            # Rafraîchir l'interface
            self.update_dashboard()
            
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
        except mysql.connector.Error as e:
            messagebox.showerror("Erreur DB", f"Erreur MySQL: {e.msg}")

    def apply_filters(self):
        """Applique les filtres de manière sécurisée"""
        try:
            filters = {
                'transaction_type': self.type_filter.get(),
                'description': self.description_filter.get().strip(),
                'start_date': self.start_date_entry.get().strip(),
                'end_date': self.end_date_entry.get().strip(),
                'sort_order': self.amount_sort.get()  # Maintenant accessible
            }
            
            transactions = Transaction.get_filtered_transactions(self.user_id, filters)
            self.update_transactions_list(transactions)
            
        except Exception as e:
            messagebox.showerror("Filter Error", str(e))

    def logout(self):
        from views.app import BudgetBuddyApp
        self.destroy()
        BudgetBuddyApp().mainloop()

if __name__ == "__main__":
    app = Dashboard(user_id=1)
    app.mainloop()