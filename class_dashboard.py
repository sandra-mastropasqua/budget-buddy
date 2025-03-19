import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BudgetBuddyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Buddy - Financial Management")
        self.root.geometry("800x600")
        self.root.configure(bg="#2C3E50")
        
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#2C3E50")
        self.style.configure("TLabel", background="#2C3E50", foreground="white", font=("Arial", 12))
        self.style.configure("TButton", background="#2980B9", foreground="white", font=("Arial", 10), padding=5)
        self.style.configure("TEntry", padding=5)
        
        self.create_menu()
        self.show_login_frame()
    
    def create_menu(self):
        menubar = tk.Menu(self.root, bg="#34495E", fg="white")
        
        account_menu = tk.Menu(menubar, tearoff=0, bg="#34495E", fg="white")
        account_menu.add_command(label="Login", command=self.show_login_frame)
        account_menu.add_command(label="Register", command=self.show_register_frame)
        account_menu.add_separator()
        account_menu.add_command(label="Exit", command=self.root.quit)
        
        transaction_menu = tk.Menu(menubar, tearoff=0, bg="#34495E", fg="white")
        transaction_menu.add_command(label="New Transaction", command=self.show_transaction_frame)
        transaction_menu.add_command(label="History", command=self.show_history_frame)
        
        dashboard_menu = tk.Menu(menubar, tearoff=0, bg="#34495E", fg="white")
        dashboard_menu.add_command(label="Dashboard", command=self.create_dashboard_frame)
        
        menubar.add_cascade(label="Account", menu=account_menu)
        menubar.add_cascade(label="Transactions", menu=transaction_menu)
        menubar.add_cascade(label="Dashboard", menu=dashboard_menu)
        
        self.root.config(menu=menubar)
    
    def create_dashboard_frame(self):
        self.clear_frames()
        dashboard_frame = ttk.Frame(self.root)
        dashboard_frame.pack(expand=True, fill="both")
        
        ttk.Label(dashboard_frame, text="Dashboard", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(dashboard_frame, text="Current Balance: $1000", font=("Arial", 14, "bold"), foreground="lightgreen").pack(pady=5)
        
        ttk.Label(dashboard_frame, text="Spending Breakdown", font=("Arial", 12)).pack(pady=10)
        
        fig, ax = plt.subplots(figsize=(4, 4))
        categories = ["Food", "Rent", "Entertainment", "Transport"]
        amounts = [300, 500, 100, 100]
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90, colors=["#FF9999", "#66B3FF", "#99FF99", "#FFD700"])
        ax.axis("equal")
        
        canvas = FigureCanvasTkAgg(fig, master=dashboard_frame)
        canvas.get_tk_widget().pack()
        
        ttk.Label(dashboard_frame, text="Alerts & Notifications", font=("Arial", 12, "bold"), foreground="red").pack(pady=10)
        ttk.Label(dashboard_frame, text="Warning: Your balance is low!", font=("Arial", 12), foreground="red").pack()
        
    def show_login_frame(self):
        self.clear_frames()
        login_frame = ttk.Frame(self.root)
        login_frame.pack(expand=True, fill="both")
        
        ttk.Label(login_frame, text="Login", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(login_frame, text="Email:").pack(pady=5)
        email_entry = ttk.Entry(login_frame)
        email_entry.pack()
        
        ttk.Label(login_frame, text="Password:").pack(pady=5)
        password_entry = ttk.Entry(login_frame, show="*")
        password_entry.pack()
        
        ttk.Button(login_frame, text="Login", command=self.create_dashboard_frame).pack(pady=20)
    
    def clear_frames(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()
    
    def show_register_frame(self):
        pass
    
    def show_transaction_frame(self):
        pass
    
    def show_history_frame(self):
        pass
    
if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetBuddyApp(root)
    root.mainloop()