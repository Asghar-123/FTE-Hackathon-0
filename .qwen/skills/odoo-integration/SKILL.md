---
name: odoo-integration
description: |
  Manage business accounting and data in Odoo Community 18/19.
  Supports executing any Odoo method and batch operations via a local MCP server.
---

# Odoo Integration

Automate your business accounting and operations with Odoo.

## Prerequisites

### 1. Setup Odoo with Docker
1. Go to `odoo-setup` directory
2. Update `.env` with your Odoo credentials
3. Run `docker-compose up -d`

### 2. Environment Variables
Ensure `odoo-setup/.env` or root `.env` contains:
```bash
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password
```

## Usage

### Using Odoo Helper
The `odoo_helper.py` script provides a clean interface for Gemini to interact with Odoo.

```python
from odoo_helper import OdooHelper
helper = OdooHelper()

# Get customers
customers = helper.get_customers()

# Create an invoice
helper.create_invoice(partner_id=12, lines=[...])
```

### Directly via HTTP API (Advanced)
Send POST requests to `http://localhost:8008/execute_method` with JSON payload:
```json
{
  "model": "res.partner",
  "method": "search_read",
  "args_json": "[[[\"customer_rank\", \">\", 0]]]",
  "kwargs_json": "{\"fields\": [\"name\", \"email\"], \"limit\": 5}"
}
```

## Common Operations

### Accounting Audit
The AI can autonomously audit transactions:
- Read `account.move` (Invoices/Bills)
- Compare with `bank.statement`
- Flag discrepancies in Obsidian Dashboard

### Customer Management
- Sync contacts from Gmail/WhatsApp to Odoo `res.partner`
- Automate lead follow-ups

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Connection refused | Ensure `odoo-mcp` docker service is running |
| Auth failure | Check Odoo credentials in `.env` |
| Method not found | Verify Odoo model and method name (case-sensitive) |
