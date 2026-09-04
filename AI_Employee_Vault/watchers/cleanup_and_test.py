import os
from pathlib import Path

approved = Path('D:/hackathonAI0/FTE-Hackathon-0/AI_Employee_Vault/Approved')
needs_action = Path('D:/hackathonAI0/FTE-Hackathon-0/AI_Employee_Vault/Needs_Action')

# Clean up Approved folder
for f in approved.glob('*.md'):
    f.unlink()
    print(f"Deleted {f.name}")

print("\n✅ Cleaned up. Now test the proper workflow:")
print("\n1. Edit an email in Needs_Action:")
print("   notepad Needs_Action\\EMAIL_Testing_*.md")
print("\n2. Add reply draft in this format:")
print("""
---
**Reply To**: sender@gmail.com
**Subject**: Re: Testing

**Draft Response**:

Hi, thanks for your email!

Best regards,
Your Name
---
""")
print("\n3. Move to Approved:")
print("   move Needs_Action\\EMAIL_Testing_*.md Approved\\")
print("\n4. Run auto_employee - it will send automatically!")
