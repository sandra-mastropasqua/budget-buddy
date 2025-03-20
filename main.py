import tkinter as tk
import mysql.connector
from models.user import User
from models.transaction import Transaction
from models.account import Account
from mysql.connector import Error
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

def plot_graph(user):
    user_id = user.get_id()
    transactions = Transaction.get_transactions(user_id)
    if not transactions:
        print("Aucune transaction trouvée.")
        return
    
    dates = [t["date"] for t in transactions]
    balances = []
    current_balance = 0
    
    for t in transactions:
        current_balance += t["amount"]
        balances.append(current_balance)
    
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(dates, balances, marker='o', linestyle='-', color='b', label="Solde (€)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Solde (€)")
    ax.set_title("Évolution du Solde Bancaire")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    
    for i, txt in enumerate(balances):
        ax.text(dates[i], txt + 3, str(txt), ha='center', fontsize=10)
    
    fig.autofmt_xdate()
    
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()


window = tk.Tk()
window.title("Évolution du Solde Bancaire")
window.geometry("600x500")

user_id = User.get_id(self)

plot_graph(user_id)

# ✅ TESTS
if __name__ == "__main__":
    User.create_database_and_tables()

    user_id = User.create_user("Guillaume", "Nurdin", "guillaume.nur@example.com", "secure123")
    user = User(user_id, "Guillaume", "Nurdin", "guillaume.nur@example.com", "secure123")  # Création de l'objet User

    if user_id:
        print(f"Utilisateur Guillaume créé avec ID {user_id}")

    account_id = Account.create_account(user_id)
    if account_id:
        print(f"Compte créé avec ID {account_id}")

    account = Account(account_id)
    print(f"Solde initial : {account.balance}€")

    account.credit(100)
    print(f"Solde après crédit de 100€ : {account.balance}€")

    account.debit(50)
    print(f"Solde après débit de 50€ : {account.balance}€")

    recipient_id = Account.create_account(user_id)
    recipient_account = Account(recipient_id)
    account.transfer(recipient_id, 30)

    print(f"Solde après transfert : {account.balance}€")
    print(f"Solde du destinataire après réception : {recipient_account.get_balance()}€")

    print("\nTest des transactions:")

    transaction_credit = Transaction.create_transaction(user_id, "Crédit de 100€", 100.00)
    if transaction_credit:
        print(f"Transaction crédit créée : {transaction_credit}")

    transaction_debit = Transaction.create_transaction(user_id, "Débit de 50€", -50.00)
    if transaction_debit:
        print(f"Transaction débit créée : {transaction_debit}")

    transactions = Transaction.get_transactions(user_id)
    print("\nToutes les transactions de l'utilisateur :")
    for t in transactions:
        print(t)

btn = tk.Button(window, text="Afficher le Graphique", command=lambda: plot_graph(user))
btn.pack()

window.mainloop()
