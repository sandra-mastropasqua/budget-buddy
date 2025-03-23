import customtkinter as ctk
from PIL import Image
from models.user import User
from models.account import Account
from views.dashboard import Dashboard
import re

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class BudgetBuddyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Budget Buddy - Login")
        self.geometry("400x400")
        self.resizable(False, False)

        self.create_login_interface()

    def create_login_interface(self):
        """Creates the login interface."""
        # Load and display the logo
        self.logo = ctk.CTkImage(light_image=Image.open("assets/images/logo.png"), size=(100, 100))
        self.logo_label = ctk.CTkLabel(self, image=self.logo, text="")
        self.logo_label.pack(pady=10)

        self.label_title = ctk.CTkLabel(self, text="Budget Buddy", font=("Arial", 24, "bold"))
        self.label_title.pack(pady=10)

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", width=250)
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=10)

        self.login_button = ctk.CTkButton(self, text="Login", command=self.login, width=150)
        self.login_button.pack(pady=10)

        self.register_button = ctk.CTkButton(self, text="Create Account", command=self.create_account, width=150)
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
        register_window.attributes('-topmost', True)

        ctk.CTkLabel(register_window, text="Create Account", font=("Arial", 20)).pack(pady=10)

        first_name_entry = ctk.CTkEntry(register_window, placeholder_text="First Name")
        first_name_entry.pack(pady=5)

        last_name_entry = ctk.CTkEntry(register_window, placeholder_text="Last Name")
        last_name_entry.pack(pady=5)

        email_entry = ctk.CTkEntry(register_window, placeholder_text="Email")
        email_entry.pack(pady=5)

        password_entry = ctk.CTkEntry(register_window, placeholder_text="Password", show="*")
        password_entry.pack(pady=5)

        # ✅ Ajout d'un label pour afficher les messages d'erreur dans `register_window`
        message_label = ctk.CTkLabel(register_window, text="", text_color="red")
        message_label.pack(pady=5)

        def submit_registration():
            """Soumet l'inscription et crée un compte bancaire après validation."""
            User.create_database_and_tables()
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            email = email_entry.get().strip()
            password = password_entry.get().strip()

            # 🔴 Vérification des champs vides
            if not all([first_name, last_name, email, password]):
                message_label.configure(text="Please fill in all fields", text_color="red")
                return

            # 🔎 Vérification du format de l'email (regex)
            email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_regex, email):
                message_label.configure(text="Invalid email format", text_color="red")
                return

            # 🔒 Vérification de la sécurité du mot de passe (regex)
            password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{10,}$"
            if not re.match(password_regex, password):
                message_label.configure(
                    text="Weak password:\n(Min. 10 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special character)",
                    text_color="red"
                )
                return

            # ✅ Si tout est bon, créer l'utilisateur
            user_id = User.create_user(first_name, last_name, email, password)
            if user_id:
                account_id = Account.create_account(user_id)  # Crée un compte bancaire associé
                if account_id:
                    message_label.configure(text="Account succesfully created !", text_color="green")
                    register_window.after(1000, register_window.destroy)  # Ferme après 1s
                else:
                    message_label.configure(text="Error creating bank account", text_color="red")
            else:
                message_label.configure(text="Error creating user account", text_color="red")

        submit_button = ctk.CTkButton(register_window, text="Sign Up", command=submit_registration)
        submit_button.pack(pady=10)


    def open_dashboard(self, user_id):
        """Opens the dashboard interface."""
        self.destroy()
        dashboard = Dashboard(user_id)
        dashboard.mainloop()

