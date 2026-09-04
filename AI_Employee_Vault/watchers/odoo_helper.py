import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from odoo-setup/.env
load_dotenv('odoo-setup/.env')

class OdooHelper:
    def __init__(self):
        # Use localhost because we are running from the host machine
        self.url = "http://localhost:8069"
        self.db = os.getenv('ODOO_DB', 'odoo_db')
        self.username = os.getenv('ODOO_USERNAME', 'admin')
        self.password = os.getenv('ODOO_PASSWORD', 'admin')
        self.session_id = None

    def authenticate(self):
        auth_url = f"{self.url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0", "method": "call",
            "params": {"db": self.db, "login": self.username, "password": self.password}
        }
        try:
            response = requests.post(auth_url, json=payload)
            response.raise_for_status()
            result = response.json()
            if "error" in result: return False
            self.session_id = response.cookies.get('session_id')
            return True
        except: return False

    def execute_method(self, model, method, args=None, kwargs=None):
        if not self.session_id and not self.authenticate(): return None
        call_url = f"{self.url}/web/dataset/call_kw"
        payload = {
            "jsonrpc": "2.0", "method": "call",
            "params": {
                "model": model, "method": method,
                "args": args or [], "kwargs": kwargs or {},
            }
        }
        try:
            response = requests.post(call_url, json=payload, cookies={'session_id': self.session_id})
            response.raise_for_status()
            return response.json().get("result")
        except: return None

    def get_customers(self, limit=10):
        return self.execute_method(
            "res.partner", "search_read", 
            kwargs={"fields": ["name", "email"], "limit": limit}
        )

    def create_invoice(self, partner_id, lines):
        invoice_vals = {
            'partner_id': partner_id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, line) for line in lines]
        }
        return self.execute_method("account.move", "create", args=[invoice_vals])

if __name__ == "__main__":
    helper = OdooHelper()
    print("Odoo Helper: Fetching customers...")
    customers = helper.get_customers()
    if customers:
        for c in customers:
            print(f"- {c.get('name')} ({c.get('email') or 'no email'})")
    else:
        print("Connection failed or no customers found.")
