from pathlib import Path
import re

# Find the Testing email file
needs_action = Path('D:/hackathonAI0/FTE-Hackathon-0/AI_Employee_Vault/Needs_Action')
approved = Path('D:/hackathonAI0/FTE-Hackathon-0/AI_Employee_Vault/Approved')

for f in needs_action.glob('EMAIL_Testing_*.md'):
    content = f.read_text(encoding='utf-8')
    
    # Fix the Reply To field - extract just the email
    content = content.replace(
        '**Reply To**: "S.M.ASGHAR ALI" <smasgharali840@gmail.com>',
        '**Reply To**: smasgharali840@gmail.com'
    )
    
    # Fix the draft response - remove brackets
    content = content.replace('[I am fine thankyou]', 'I am fine thankyou')
    content = content.replace('[Asghar]', 'Asghar')
    
    # Fix the move instruction
    content = content.replace('/Pending_Approval', '/Approved folder')
    
    # Save the fixed file
    f.write_text(content, encoding='utf-8')
    print(f"Fixed: {f.name}")
    
    # Move to Approved
    dest = approved / f.name
    f.rename(dest)
    print(f"Moved to: {dest}")
    print("\n✅ Ready to send! Run: python watchers/auto_employee.py ..")
