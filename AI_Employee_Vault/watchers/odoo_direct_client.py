import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from odoo-setup/.env
load_dotenv('odoo-setup/.env')

class OdooDirectClient:
    def __init__(self):
        # Use localhost because we are running from the host machine
        self.url = "http://localhost:8069"
        self.db = os.getenv('ODOO_DB', 'odoo_db')
        self.username = os.getenv('ODOO_USERNAME', 'admin')
        self.password = os.getenv('ODOO_PASSWORD', 'admin')
        self.session_id = None

    def authenticate(self):
        """
        Authenticate with Odoo and get a session ID.
        """
        auth_url = f"{self.url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.db,
                "login": self.username,
                "password": self.password
            }
        }
        
        try:
            response = requests.post(auth_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"Odoo Auth Error: {result['error']}")
                return False
                
            self.session_id = response.cookies.get('session_id')
            # print(f"Authenticated successfully. Session ID: {self.session_id}")
            return True
        except Exception as e:
            print(f"Error authenticating with Odoo: {e}")
            return False

    def execute_kw(self, model, method, args=None, kwargs=None):
        """
        Execute a method on an Odoo model using call_kw.
        """
        if not self.session_id and not self.authenticate():
            return None

        call_url = f"{self.url}/web/dataset/call_kw"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args or [],
                "kwargs": kwargs or {},
            }
        }
        
        cookies = {'session_id': self.session_id}
        
        try:
            response = requests.post(call_url, json=payload, cookies=cookies)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                print(f"Odoo Execution Error: {result['error']}")
                return None
                
            return result.get("result")
        except Exception as e:
            print(f"Error executing Odoo method: {e}")
            return None

    def get_customers(self, limit=5):
        return self.execute_kw(
            "res.partner", 
            "search_read", 
            kwargs={"fields": ["name", "email"], "limit": limit}
        )

if __name__ == "__main__":
    client = OdooDirectClient()
    print(f"Connecting to Odoo at {client.url} (DB: {client.db})...")
    if client.authenticate():
        print("Fetching customers...")
        customers = client.get_customers()
        if customers:
            print("Found customers:")
            for c in customers:
                print(f"- {c.get('name')} ({c.get('email') or 'no email'})")
        else:
            print("No customers found or empty database.")
    else:
        print("Failed to authenticate with Odoo.")
