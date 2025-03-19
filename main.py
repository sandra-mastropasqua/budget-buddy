import tkinter as tk
from models.account_class import Account
from models.user_class import User
import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="pipicaca",
        database="budget_buddy"
    )

root = tk.Tk()
root.geometry('400x200')
root.title("Dashboard")

db = connect_db()
account_id = 1
account = Account(db, account_id)

balance_label = tk.Label(root, text=f"Balance: {account.balance} €", font=("Arial", 16))
balance_label.pack(pady=20)

quit_button = tk.Button(root, text="Quit", command=root.destroy)
quit_button.pack()

root.mainloop()