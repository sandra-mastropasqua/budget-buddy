import customtkinter as ctk
from models.account import Account
from models.transaction import Transaction
from models.user import User
from decimal import Decimal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from views.transfer_window import TransferWindow
from tkinter import messagebox
import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

class Dashboard(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.canvas = None  # ✅ Stocke le graphique

        self.title("Budget Buddy - Dashboard")
        self.geometry("1000x600")  # ✅ Réduit un peu la hauteur pour optimiser l'espace
        self.resizable(False, False)

        user = User.get_user_by_id(user_id)
        full_name = f"{user['firstname']} {user['lastname']}" if user else "Utilisateur inconnu"

        # ✅ HEADER (Nom de l'utilisateur et solde)
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(fill="x", padx=10, pady=10)

        self.user_label = ctk.CTkLabel(self.header_frame, text=f"Hello, {full_name} 👋", font=("Arial", 18))
        self.user_label.pack(side="left", padx=10)

        self.balance_label = ctk.CTkLabel(self.header_frame, text="Balance: 0€", font=("Arial", 18))
        self.balance_label.pack(side="right", padx=10)


        # ✅ CONTENEUR PRINCIPAL (2 colonnes)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ LEFT FRAME - Liste des transactions
        self.left_frame = ctk.CTkFrame(self.main_frame, width=450)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.transactions_label = ctk.CTkLabel(self.left_frame, text="Historique des Transactions", font=("Arial", 16))
        self.transactions_label.pack(pady=10)

        self.transactions_list = ctk.CTkTextbox(self.left_frame, width=400, height=300)
        self.transactions_list.pack(pady=10)

        # ✅ RIGHT FRAME - Graphique des transactions
        self.right_frame = ctk.CTkFrame(self.main_frame, width=550)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.update_dashboard()
        self.plot_transactions()  # ✅ Ajout du graphique

        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Amount") 
        self.amount_entry.pack(pady=5)

        self.credit_button = ctk.CTkButton(self, text="Credit", command=lambda: self.handle_amount("credit"))
        self.credit_button.pack(pady=5)

        self.debit_button = ctk.CTkButton(self, text="Debit", command=lambda: self.handle_amount("debit"))
        self.debit_button.pack(pady=5)

        self.transfer_button = ctk.CTkButton(self, text="Transfer money", command=self.open_transfer_window)
        self.transfer_button.pack(pady=10)

        self.logout_button = ctk.CTkButton(self, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)

        self.update_dashboard()

    def update_dashboard(self):
        """Mise à jour du solde et de l'historique des transactions."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            self.balance_label.configure(text=f"Balance: {float(account.balance):.2f}€")

        transactions = Transaction.get_transactions(self.user_id)

        self.transactions_list.configure(state="normal")
        self.transactions_list.delete("1.0", "end")

        if not transactions:
            self.transactions_list.insert("end", "Aucune transaction trouvée.\n")
        else:
            for t in transactions:
                date = t.date.strftime("%d/%m/%Y %H:%M") if t.date else "Inconnue"
                description = t.description
                amount = float(t.amount)
                self.transactions_list.insert("end", f"{date} - {description}: {amount:.2f}€\n")

        self.transactions_list.configure(state="disabled")
        self.plot_transactions()  # ✅ Mettre à jour le graphique après mise à jour des transactions
    
    def open_transfer_window(self):
        """Ouvre la fenêtre de transfert d'argent """
        TransferWindow(self.user_id, self)

    def plot_transactions(self):
        """Affiche un graphique de l'évolution du solde du compte au fil du temps."""
        transactions = Transaction.get_transactions(self.user_id)

        if not transactions:
            print("Aucune transaction à afficher.")
            return

        # ✅ Supprimer l'ancien graphique s'il existe
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # ✅ Trier les transactions par date
        transactions.sort(key=lambda t: t.date)

        # ✅ Récupérer le solde initial du compte
        account = Account.get_account_by_user(self.user_id)
        balance = float(account.balance) if account else 0  

        # ✅ Extraction des dates et calcul du solde cumulé
        dates = []  
        balances = []  

        for t in transactions:
            dates.append(t.date)  
            balance += float(t.amount)  
            balances.append(balance)  

        # ✅ Convertir les dates en format lisible
        dates = [datetime.strftime(d, "%d/%m/%Y %H:%M") for d in dates]

        # ✅ Création du graphique
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(dates, balances, marker="o", linestyle="-", color="b", label="Solde")
        ax.set_xlabel("Date")
        ax.set_ylabel("Solde (€)")
        ax.set_title("Évolution du Solde")
        ax.legend()
        ax.grid()
        plt.xticks(rotation=45)  

        # ✅ Intégration avec Tkinter dans le RIGHT FRAME
        self.canvas = FigureCanvasTkAgg(fig, master=self.right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)

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
    
    def open_transfer_window(self):
        """Ouvre la fenêtre de transfert d'argent"""
        TransferWindow(self.user_id, self)

    def logout(self):
        """Returns to the login screen."""
        from views.app import BudgetBuddyApp
        self.destroy()
        app = BudgetBuddyApp()
        app.mainloop()
    
    def update_balance(self):
        """Met a jour le solde affiché après un transfert"""
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
            messagebox.showinfo("DEBUG",f"Nouveau solde récupéré : {new_balance}euros ")
        
        cursor.close()
        connection.close()