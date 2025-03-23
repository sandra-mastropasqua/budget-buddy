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
        self.canvas = None

        self.title("Budget Buddy - Dashboard")
        self.geometry("1000x600")
        self.resizable(False, False)

        # Retrieve user's name to display
        user = User.get_user_by_id(user_id)
        full_name = f"{user['firstname']} {user['lastname']}" if user else "Unknown User"

        # ----- HEADER -----
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(fill="x", padx=10, pady=10)

        self.user_label = ctk.CTkLabel(self.header_frame, text=f"Hello, {full_name} 👋", font=("Arial", 18))
        self.user_label.pack(side="left", padx=10)

        self.balance_label = ctk.CTkLabel(self.header_frame, text="Balance: 0€", font=("Arial", 18))
        self.balance_label.pack(side="right", padx=10)

        # ►► Overdraft notification label
        self.notification_label = ctk.CTkLabel(self.header_frame, text="", text_color="red", font=("Arial", 14))
        self.notification_label.pack(side="bottom", pady=5)

        # ----- TABVIEW -----
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.transactions_tab = self.tabview.add("Transactions")
        self.overview_tab = self.tabview.add("Overview")
        self.settings_tab = self.tabview.add("Settings")

        # Set up each tab
        self.setup_transactions_tab()
        self.setup_overview_tab()
        self.setup_settings_tab()

        # Initial dashboard update
        self.update_dashboard()

    # -----------------------------------------------------------------------
    # "Overview" Tab
    # -----------------------------------------------------------------------
    def setup_overview_tab(self):
        """Sets up the 'Overview' tab with a column-based layout."""
        self.overview_frame = ctk.CTkFrame(self.overview_tab)
        self.overview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left frame: transaction list
        self.transactions_frame = ctk.CTkFrame(self.overview_frame, width=400)
        self.transactions_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.transactions_label = ctk.CTkLabel(self.transactions_frame, text="Transaction History", font=("Arial", 16))
        self.transactions_label.pack(pady=10)

        self.transactions_container_overview = ctk.CTkFrame(self.transactions_frame)
        self.transactions_container_overview.pack(fill="both", expand=True, padx=10, pady=10)

        # Right frame: graph
        self.graph_frame = ctk.CTkFrame(self.overview_frame, width=500, height=400)
        self.graph_frame.pack(side="right", expand=True, padx=10, pady=10)

    # -----------------------------------------------------------------------
    # "Transactions" Tab
    # -----------------------------------------------------------------------
    def setup_transactions_tab(self):
        """Sets up the 'Transactions' tab with filters and actions."""

        # Main frame for the "Transactions" tab
        self.transactions_layout = ctk.CTkFrame(self.transactions_tab)
        self.transactions_layout.pack(fill="both", expand=True, padx=10, pady=10)

        # 1) Filter frame at the top
        self.filter_frame = ctk.CTkFrame(self.transactions_layout)
        self.filter_frame.pack(side="top", fill="x", padx=5, pady=5)

        ctk.CTkLabel(self.filter_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.type_filter = ctk.CTkComboBox(self.filter_frame, values=["All", "Credit", "Debit"])
        self.type_filter.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.filter_frame, text="Description:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.description_filter = ctk.CTkEntry(self.filter_frame, placeholder_text="Ex: Courses, Loyer...")
        self.description_filter.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.filter_frame, text="From:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.start_date_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.filter_frame, text="To:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.end_date_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.filter_frame, text="Sort by Amount:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.amount_sort = ctk.CTkComboBox(self.filter_frame, values=["None", "Ascending", "Descending"])
        self.amount_sort.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.filter_button = ctk.CTkButton(self.filter_frame, text="Filter", command=self.apply_filters)
        self.filter_button.grid(row=2, column=3, padx=5, pady=5, sticky="e")

        # Allow some columns to stretch if needed
        self.filter_frame.columnconfigure(1, weight=1)
        self.filter_frame.columnconfigure(3, weight=1)

        # Main content frame (below): two columns
        self.content_frame = ctk.CTkFrame(self.transactions_layout)
        self.content_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # Left column: transaction list
        self.transactions_list_frame = ctk.CTkFrame(self.content_frame)
        self.transactions_list_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.transactions_label = ctk.CTkLabel(
            self.transactions_list_frame,
            text="Transaction History",
            font=("Arial", 16, "bold")
        )
        self.transactions_label.pack(pady=10)

        self.transactions_container = ctk.CTkFrame(self.transactions_list_frame)
        self.transactions_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Right column: "New Transaction"
        self.actions_frame = ctk.CTkFrame(self.content_frame)
        self.actions_frame.pack(side="right", fill="both", expand=False, padx=5, pady=5)

        ctk.CTkLabel(self.actions_frame, text="New Transaction", font=("Arial", 16, "bold")).pack(pady=10)

        self.amount_entry = ctk.CTkEntry(self.actions_frame, placeholder_text="Amount")
        self.amount_entry.pack(pady=5)

        self.description_entry = ctk.CTkEntry(self.actions_frame, placeholder_text="Description")
        self.description_entry.pack(pady=5)

        self.credit_button = ctk.CTkButton(self.actions_frame, text="Credit", command=lambda: self.handle_amount("credit"))
        self.credit_button.pack(pady=5)

        self.debit_button = ctk.CTkButton(self.actions_frame, text="Debit", command=lambda: self.handle_amount("debit"))
        self.debit_button.pack(pady=5)

    # -----------------------------------------------------------------------
    # "Settings" Tab
    # -----------------------------------------------------------------------
    def setup_settings_tab(self):
        """Sets up the 'Settings' tab."""
        ctk.CTkLabel(self.settings_tab, text="Settings", font=("Arial", 16)).pack(pady=10)
        self.logout_button = ctk.CTkButton(self.settings_tab, text="Logout", command=self.logout)
        self.logout_button.pack(pady=5)

    # -----------------------------------------------------------------------
    # General dashboard update
    # -----------------------------------------------------------------------
    def update_dashboard(self):
        """Updates the balance, transaction history, and overdraft alert."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            balance = float(account.balance)
            self.balance_label.configure(text=f"Balance: {balance:.2f}€")

            # Check if balance is negative -> overdraft alert
            if balance < 0:
                self.notification_label.configure(text="Attention : Vous êtes en découvert !")
            else:
                self.notification_label.configure(text="")

        transactions = Transaction.get_transactions(self.user_id)

        # Remove previous transaction display
        for widget in self.transactions_container.winfo_children():
            widget.destroy()

        if not transactions:
            ctk.CTkLabel(self.transactions_container, text="No transactions found.", font=("Arial", 14)).pack(pady=5)
        else:
            for t in transactions:
                date_str = t["date"].strftime("%d/%m/%Y %H:%M") if t["date"] else "Unknown Date"
                type_transaction = "Credit" if t["amount"] > 0 else "Debit"
                description = t["description"]
                amount = f"{float(t['amount']):.2f}€"

                ctk.CTkLabel(
                    self.transactions_container,
                    text=f"{date_str} - {type_transaction} - {description}: {amount}",
                    font=("Arial", 14)
                ).pack(anchor="w", padx=5, pady=2)

        # Update the graph in the "Overview" tab
        self.plot_transactions()

    # -----------------------------------------------------------------------
    # Graph display in the "Overview" tab
    # -----------------------------------------------------------------------
    def plot_transactions(self):
        """Displays a graph of the account balance evolution over time."""
        transactions = Transaction.get_transactions(self.user_id)
        if not transactions:
            print("No transactions to display.")
            return

        # Sort transactions by date
        transactions.sort(key=lambda t: t["date"])

        current_balance = 0
        dates = []
        balances = []

        for t in transactions:
            dates.append(t["date"])
            current_balance += float(t["amount"])
            balances.append(current_balance)

        # Convert date objects to strings
        dates_str = [datetime.strftime(d, "%d/%m/%Y %H:%M") for d in dates]

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(dates_str, balances, marker="o", linestyle="-", color="b", label="Balance")
        ax.set_xlabel("Date")
        ax.set_ylabel("Balance (€)")
        ax.set_title("Balance Evolution")
        ax.legend()
        ax.grid()
        plt.xticks(rotation=60)

        # Destroy any previous canvas
        if hasattr(self, "canvas") and self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Display the graph in the "graph_frame"
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

    # -----------------------------------------------------------------------
    # Handling credit/debit amounts
    # -----------------------------------------------------------------------
    def handle_amount(self, action):
        """Enter the amount."""
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
        """Adds a credit."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            account.update_balance(amount)
            Transaction.create_transaction(self.user_id, description, amount)
            self.update_dashboard()

    def debit(self, amount, description):
        """Adds a debit."""
        account = Account.get_account_by_user(self.user_id)
        if account:
            account.update_balance(-amount)
            Transaction.create_transaction(self.user_id, description, -amount)
            self.update_dashboard()

    # -----------------------------------------------------------------------
    # Transaction filters
    # -----------------------------------------------------------------------
    def apply_filters(self):
        """Applies the selected filters and updates the transaction display."""
        type_filter = self.type_filter.get()
        description_filter = self.description_filter.get().strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        amount_sort = self.amount_sort.get()

        sort_order = "ASC" if amount_sort == "Ascending" else "DESC" if amount_sort == "Descending" else None

        # Retrieve filtered transactions
        transactions = Transaction.get_transactions(
            user_id=self.user_id,
            type_filter=type_filter,
            description_filter=description_filter,
            start_date=start_date,
            end_date=end_date,
            sort_order=sort_order
        )

        # Clear previous display
        for widget in self.transactions_container.winfo_children():
            widget.destroy()

        if not transactions:
            ctk.CTkLabel(self.transactions_container, text="No transactions found.", font=("Arial", 14)).pack(pady=5)
        else:
            for t in transactions:
                date_str = t["date"].strftime("%d/%m/%Y") if t["date"] else "Unknown"
                type_transaction = "Credit" if t["amount"] > 0 else "Debit"
                description = t["description"]
                amount = f"{float(t['amount']):.2f}€"

                ctk.CTkLabel(
                    self.transactions_container,
                    text=f"{date_str} - {type_transaction} - {description}: {amount}",
                    font=("Arial", 14)
                ).pack(anchor="w", padx=5, pady=2)

    # -----------------------------------------------------------------------
    # Logout (return to login screen)
    # -----------------------------------------------------------------------
    def logout(self):
        """logout and go back to login screen."""
        from views.app import BudgetBuddyApp
        self.destroy()
        app = BudgetBuddyApp()
        app.mainloop()
