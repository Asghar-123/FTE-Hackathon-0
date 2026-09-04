---
name: approval-workflow
description: |
  Human-in-the-Loop (HITL) approval workflow for sensitive actions.
  Creates approval request files, manages approval/rejection process,
  and tracks approval history.
---

# Approval Workflow

Human-in-the-Loop approval system for sensitive actions.

## Overview

When the AI Employee detects an action that requires human approval, it:

1. Creates an approval request file in `Pending_Approval/`
2. Waits for human to move file to `Approved/` or `Rejected/`
3. Processes approved actions automatically
4. Logs all decisions

## What Requires Approval

| Action Type | Approval Required | Threshold |
|-------------|-------------------|-----------|
| Payments | ✅ Yes | > $100 |
| Sending emails | ✅ Yes | New contacts |
| Social media posts | ✅ Yes | Always |
| File deletions | ✅ Yes | Always |
| Subscription changes | ✅ Yes | Always |
| Internal tasks | ❌ No | - |

## Approval File Format

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-03-10T16:00:00Z
expires: 2026-03-11T16:00:00Z
status: pending
---

# Approval Required: Payment

## Details
- **Action**: Payment
- **Amount**: $500.00
- **Recipient**: Client A
- **Reason**: Invoice #1234 payment
- **Created**: 2026-03-10 16:00:00

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.

## Notes
*Add any comments or conditions.*

---
*Created by AI Employee Approval System*
```

## Usage

### Manual Approval (File Movement)

```bash
# To approve: Move file to Approved folder
mv Pending_Approval/APPROVAL_payment.md Approved/

# To reject: Move file to Rejected folder
mv Pending_Approval/APPROVAL_payment.md Rejected/
```

### Via Python Script

```bash
# Approve an action
python watchers/approval_workflow.py ../AI_Employee_Vault \
  --approve APPROVAL_payment.md

# Reject an action
python watchers/approval_workflow.py ../AI_Employee_Vault \
  --reject APPROVAL_payment.md \
  --reason "Budget not approved"

# List pending approvals
python watchers/approval_workflow.py ../AI_Employee_Vault --list
```

### Programmatically

```python
from approval_workflow import ApprovalWorkflow

workflow = ApprovalWorkflow('../AI_Employee_Vault')

# Create approval request
approval_path = workflow.create_approval(
    action_type='payment',
    amount=500.00,
    recipient='Client A',
    reason='Invoice #1234',
    source_file='FILE_invoice.md'
)

# Check approval status
status = workflow.check_status(approval_path)
```

## Workflow States

```
┌─────────────────┐
│ Pending_Approval│ ← Created by AI
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────┐
│ Approved│ │ Rejected │
└────┬────┘ └────┬─────┘
     │           │
     ▼           │
  Process        │
     │           │
     ▼           │
┌─────────┐      │
│  Done/  │◄─────┘
└─────────┘
```

## Auto-Approval Rules

Configure automatic approval for low-risk actions:

```python
# In orchestrator.py
AUTO_APPROVAL_RULES = {
    'payment_threshold': 100.00,  # Auto-approve payments < $100
    'allowed_domains': ['company.com'],  # Auto-approve emails to these domains
    'allowed_keywords': ['internal', 'routine']  # Auto-approve if contains
}
```

## Expiration

Approval requests can have expiration times:

```yaml
---
expires: 2026-03-11T16:00:00Z
---
```

Expired approvals are moved to `Rejected/` with note.

## Audit Log

All approvals are logged in `Accounting/approval_log.md`:

```markdown
## Approval History

| Date | Action | Amount | Decision | Notes |
|------|--------|--------|----------|-------|
| 2026-03-10 | Payment | $500 | Approved | Budget Q1 |
| 2026-03-10 | Email | - | Rejected | Wrong recipient |
```

## Integration

### With Orchestrator

```python
# Check if action requires approval
if workflow.requires_approval(action_data):
    workflow.create_approval(...)
else:
    # Process directly
    process_action(...)
```

### With Qwen Code

```bash
qwen "Check Pending_Approval folder and summarize items awaiting approval"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not processed | Ensure file is in Approved/ folder |
| File not moving | Check file permissions |
| Expired approvals | Run cleanup script |
