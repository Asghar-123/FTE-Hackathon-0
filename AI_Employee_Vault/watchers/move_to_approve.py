from pathlib import Path
approved = Path('D:/hackathonAI0/FTE-Hackathon-0/AI_Employee_Vault/Approved')
needs_action = Path('D:/hackathonAI0/FTE-Hackathon-0/AI_Employee_Vault/Needs_Action')

print("Approved folder:", list(approved.glob('*.md')) if approved.exists() else 'Not exists')
print("Needs_Action:", list(needs_action.glob('EMAIL_*.md')) if needs_action.exists() else 'Not exists')

# Move Lucnh email to Approved if exists
for f in needs_action.glob('EMAIL_Lucnh_*.md'):
    dest = approved / f.name
    f.rename(dest)
    print(f"Moved {f.name} to Approved/")
