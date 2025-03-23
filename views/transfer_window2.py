import customtkinter as ctk
from tkinter import messagebox
from models.account import Account

class TransferWindow(ctk.CTkToplevel):
    def __init__(self, user_id, dashboard=None):
        super().__init__()

        self.user_id = user_id
        self.dashboard = dashboard

        self.title("Transférer de l'argent")
        self.geometry("400x250")
        self.resizable(False, False)

        self.lift()
        self.attributes ('-topmost', True)
        self.after(500, lambda : self.attributes('-topmost', False))

        ctk.CTkLabel(self, text="Compte destinaire:").pack(pady=(20,5))
        self.to_account_entry = ctk.CTkEntry(self)
        self.to_account_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Montant :").pack(pady=5)
        self.amount_entry = ctk.CTkEntry(self)
        self.amount_entry.pack(pady=5)

        button_frame = ctk.CTkFrame(self,fg_color="transparent")
        button_frame.pack(pady=10)
        self.transfer_button = ctk.CTkButton(
            master=button_frame, 
            text="Transférer", 
            command=self.transfer_money,
            width=150, 
            height=35,
        )
        self.transfer_button.pack()
        
    
    def transfer_money(self):
        to_account_number = self.to_account_entry.get()

        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Erreur","Le montant doit être un nombre valide")
            return
        if amount <= 0:
            messagebow.showerror("Erreur","Le montant doit être positif")
            return
            
        user_account = Account.get_account_by_user(self.user_id)
        if not user_account:
            messagebox.showerror("Erreur","Votre compte est introuvable")
            return

        success = Account.transfer_funds(self.user_id, to_account_number, amount)

        if success:
            messagebox.showinfo("Succès","Transfert réalisé avec succès")
            if hasattr(self.dashboard, "update_balance"):
                try :
                    self.dashboard.update_balance()
                except Exception as e:
                    messagebox.showerror("Erreur",f"Echec lors de update_balance():{e}")
            else :
                messagebox.showerror("Erreur","update_balance() n'existe pas sur l'objet dashboard")

            self.destroy()
        else:
            messagebox.showerror("Erreur","Le transfert a échoué. Vérifier les informations")