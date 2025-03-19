import customtkinter as ctk
from models.user import User
from models.account import Account
from views.dashboard import Dashboard  # Import Dashboard from its new location

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