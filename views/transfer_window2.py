import customtkinter as ctk
from tkinter import messagebox
from models.account import Account

class TransferWindow(ctk.CTkToplevel):
    def __init__(self, user_id, dashboard=None):
        super().__init__()

        self.user_id = user_id
        self.dashboard = dashboard

        self.title("Transfer money")
        self.geometry("400x250")
        self.resizable(False, False)

        self.lift()
        self.attributes ('-topmost', True)
        self.after(500, lambda : self.attributes('-topmost', False))

        ctk.CTkLabel(self, text="Destination account:").pack(pady=(20,5))
        self.to_account_entry = ctk.CTkEntry(self)
        self.to_account_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Amount :").pack(pady=5)
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
            messagebox.showerror("Error","The amount must be a valid number")
            return
        if amount <= 0:
            messagebow.showerror("Error","The amount must be positive")
            return
            
        user_account = Account.get_account_by_user(self.user_id)
        if not user_account:
            messagebox.showerror("Error","Account not found")
            return

        success = Account.transfer_funds(self.user_id, to_account_number, amount)

        if success:
            messagebox.showinfo("Success","Transfer made with success")
            if hasattr(self.dashboard, "update_balance"):
                try :
                    self.dashboard.update_balance()
                except Exception as e:
                    messagebox.showerror("Error",f"Failed :{e}")
            else :
                messagebox.showerror("Error","update_balance() don't exist on the dashboard")

            self.destroy()
        else:
            messagebox.showerror("Error","The transfer has failed. Check your informations")