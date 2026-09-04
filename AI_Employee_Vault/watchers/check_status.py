from pathlib import Path
approved = Path('D:/hackathonAI0/FTE-Hackathon-0/AI_Employee_Vault/Approved')
done = Path('D:/hackathonAI0/FTE-Hackathon-0/AI_Employee_Vault/Done')

print('Approved folder:', list(approved.glob('EMAIL_Dinner*.md')) if approved.exists() else 'Empty')
print('Done folder:', list(done.glob('EMAIL_Dinner*.md')) if done.exists() else 'Empty')
