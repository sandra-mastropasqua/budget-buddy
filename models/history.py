import mysql.connector

class History:
    def __init__(self, db_connection, account_id):
        self.db = db_connection
        self.account_id = account_id
        self.transactions = self.load_transactions()

    def load_transactions(self):
        """Charge toutes les transactions du compte depuis la base de données."""
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, reference, description, amount, date, type_id, category_id 
            FROM transactions 
            WHERE account_id = %s 
            ORDER BY date DESC
        """, (self.account_id,))
        return cursor.fetchall()  # Renvoie la liste des transactions sous forme de dictionnaire

    def search_by_date(self, start_date, end_date):
        """Recherche des transactions entre deux dates."""
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE account_id = %s 
            AND date BETWEEN %s AND %s
            ORDER BY date DESC
        """, (self.account_id, start_date, end_date))
        return cursor.fetchall()

    def filter_by_category(self, category_id):
        """Filtre les transactions par catégorie."""
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE account_id = %s 
            AND category_id = %s
            ORDER BY date DESC
        """, (self.account_id, category_id))
        return cursor.fetchall()

    def sort_by_amount(self, order="ASC"):
        """Trie les transactions par montant (croissant ou décroissant)."""
        if order not in ["ASC", "DESC"]:
            raise ValueError("L'ordre doit être 'ASC' ou 'DESC'")

        cursor = self.db.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT * FROM transactions 
            WHERE account_id = %s 
            ORDER BY amount {order}
        """, (self.account_id,))
        return cursor.fetchall()

    def get_monthly_summary(self):
        """Récupère le total des dépenses et revenus par mois pour un compte."""
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                DATE_FORMAT(date, '%Y-%m') AS month, 
                SUM(CASE WHEN type_id = 1 THEN amount ELSE 0 END) AS total_deposits, 
                SUM(CASE WHEN type_id = 2 THEN amount ELSE 0 END) AS total_withdrawals 
            FROM transactions 
            WHERE account_id = %s 
            GROUP BY month 
            ORDER BY month ASC
        """, (self.account_id,))
        return cursor.fetchall()
