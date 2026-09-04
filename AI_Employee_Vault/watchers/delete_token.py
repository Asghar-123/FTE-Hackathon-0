import os
token_path = 'D:/hackathonAI0/FTE-Hackathon-0/AI_Employee_Vault/watchers/token.json'
if os.path.exists(token_path):
    os.remove(token_path)
    print(f"Deleted {token_path}")
    print("\nNow run: python gmail_watcher.py .. --authenticate")
    print("This will create a new token with SEND permissions!")
else:
    print("Token not found")
