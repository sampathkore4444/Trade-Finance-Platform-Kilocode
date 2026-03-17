# Trade Finance Platform - End-to-End Flow Guide

This document explains how each feature works in the Trade Finance Platform, from a layman's perspective to technical implementation. It covers the complete flow from user action to database storage.

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Letter of Credit (LC)](#letter-of-credit-lc)
4. [Bank Guarantee](#bank-guarantee)
5. [Documentary Collection](#documentary-collection)
6. [Invoice Financing](#invoice-financing)
7. [Trade Loan](#trade-loan)
8. [Risk Management](#risk-management)
9. [Compliance & KYC](#compliance--kyc)
10. [Document Management](#document-management)
11. [Reports & Analytics](#reports--analytics)
12. [Notifications](#notifications)
13. [Docker Commands](#docker-commands)

---

## System Architecture Overview

### How the System Works (Simple Explanation)

Imagine a bank with multiple departments handling international trade transactions. This platform acts as a **digital assistant** that helps bank staff manage all trade finance operations in one place.

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                          │
│                    (React Frontend - Port 3000)                │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP Requests (REST API)
                          │ WebSocket (Real-time)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NGINX REVERSE PROXY                        │
│                    (Port 80/443)                                │
│         Routes: /api/* → Backend, /* → Frontend               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐     ┌─────────────────────┐
│   FASTAPI BACKEND   │     │    CELERY WORKER     │
│   (Port 8000)       │     │  (Background Tasks)  │
│   - REST API        │     │  - Email sending    │
│   - WebSocket       │     │  - Report gen       │
│   - Business Logic  │     │  - Notifications    │
└─────────┬───────────┘     └─────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌──────────────────┐    ┌──────────────────┐                │
│  │   PostgreSQL     │    │      Redis        │                │
│  │  (Main Database) │    │   (Cache/Queue)   │                │
│  │   Port: 5432     │    │   Port: 6379      │                │
│  └──────────────────┘    └──────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

### Frontend ↔ Backend Communication

The frontend and backend communicate through **REST API endpoints**. Here's how it works:

1. **User clicks a button** on the frontend
2. **Frontend sends HTTP request** to backend (via nginx)
3. **Backend processes the request** (validates, saves to database)
4. **Backend sends response** back to frontend
5. **Frontend updates the screen** with the result

Example: When a user clicks "Create LC", the frontend sends:
```
POST /api/v1/letter-of-credit/
Content-Type: application/json
Authorization: Bearer <token>

{
  "applicant_name": "ABC Corp",
  "beneficiary_name": "XYZ Ltd",
  "lc_amount": 50000,
  "currency": "USD",
  ...
}
```

---

## Authentication & Authorization

### What is This Feature?
**Simple Explanation:** Just like how you need to log into your bank app, this feature ensures only authorized bank staff can access the system. Each user has specific permissions (like a keycard that only opens certain doors).

### Real-World Example
- **Relationship Manager (RM)** can create and approve LCs up to $100,000
- **Credit Officer** can view all transactions but needs manager approval for large amounts
- **Operations Staff** can only process documents, not approve transactions

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| Login | POST | `/api/v1/auth/login` | User enters username/password |
| Refresh Token | POST | `/api/v1/auth/refresh` | Get new access token |
| Logout | POST | `/api/v1/auth/logout` | Invalidate session |
| Get Profile | GET | `/api/v1/auth/me` | Get current user info |
| Change Password | POST | `/api/v1/auth/change-password` | Update password |

### Data Flow
```
User Login Flow:
1. User enters email & password
2. Frontend → POST /api/v1/auth/login
3. Backend validates credentials against database
4. Backend creates JWT tokens (access + refresh)
5. Backend returns tokens to frontend
6. Frontend stores tokens in localStorage
7. All future requests include: Authorization: Bearer <token>
```

---

## Letter of Credit (LC)

### What is This Feature?
**Simple Explanation:** A Letter of Credit is like a **promise letter** from a bank. When Company A (Importer) buys goods from Company B (Exporter), the bank guarantees that Company A will pay. If Company A doesn't pay, the bank pays Company B.

### Real-World Example
**Scenario:** ABC Corp (USA) wants to buy electronics from Shenzhen Electronics (China) worth $50,000.

1. ABC Corp applies for an LC at their bank
2. The bank reviews ABC Corp's credit and approves
3. The bank sends the LC to Shenzhen Electronics' bank
4. When goods are shipped, Shenzhen Electronics presents documents
5. The bank verifies documents and pays Shenzhen Electronics
6. ABC Corp pays the bank later (with interest)

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| List LCs | GET | `/api/v1/letter-of-credit/` | Get all LCs |
| Create LC | POST | `/api/v1/letter-of-credit/` | Create new LC |
| Get LC Details | GET | `/api/v1/letter-of-credit/{id}` | View specific LC |
| Update LC | PUT | `/api/v1/letter-of-credit/{id}` | Modify LC |
| Submit for Approval | POST | `/api/v1/letter-of-credit/{id}/submit` | Send to approver |
| Approve LC | POST | `/api/v1/letter-of-credit/{id}/approve` | Approve LC |
| Reject LC | POST | `/api/v1/letter-of-credit/{id}/reject` | Reject LC |
| Issue LC | POST | `/api/v1/letter-of-credit/{id}/issue` | Send to beneficiary |
| Amend LC | POST | `/api/v1/letter-of-credit/{id}/amend` | Modify terms |

### Example Request (Create LC)
```json
POST /api/v1/letter-of-credit/
{
  "lc_type": "IRREVOCABLE",
  "applicant": {
    "name": "ABC Corp",
    "address": "123 Business St, New York",
    "country": "USA"
  },
  "beneficiary": {
    "name": "Shenzhen Electronics Ltd",
    "address": "456 Tech Park, Shenzhen",
    "country": "China"
  },
  "lc_amount": 50000.00,
  "currency": "USD",
  "validity_date": "2024-06-30",
  "description": "Import of electronic components",
  "shipment_details": {
    "from_port": "Shanghai, China",
    "to_port": "Los Angeles, USA",
    "latest_shipment_date": "2024-06-15"
  }
}
```

### LC Status Workflow
```
DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED/REJECTED → ISSUED → AMENDED/UTILIZED → CLOSED
         ↓            ↓              ↓              ↓            ↓            ↓
      (Pending)   (Credit Team)  (Manager)    (Sent to Bank)  (Documents)  (Complete)
```

---

## Bank Guarantee

### What is This Feature?
**Simple Explanation:** A Bank Guarantee is like an **insurance policy**. If Company A fails to fulfill a contract, the bank pays Company B up to a certain amount. It helps businesses trust each other when doing deals.

### Real-World Example
**Scenario:** Construction Company wins a $1M contract to build an office. The client wants assurance that the company will complete the work. The bank issues a guarantee for 10% ($100,000). If Construction Company doesn't finish, the client claims the guarantee.

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| List Guarantees | GET | `/api/v1/bank-guarantee/` | Get all guarantees |
| Create Guarantee | POST | `/api/v1/bank-guarantee/` | Apply for guarantee |
| Get Details | GET | `/api/v1/bank-guarantee/{id}` | View guarantee |
| Update | PUT | `/api/v1/bank-guarantee/{id}` | Modify guarantee |
| Approve | POST | `/api/v1/bank-guarantee/{id}/approve` | Approve guarantee |
| Claim | POST | `/api/v1/bank-guarantee/{id}/claim` | Client claims guarantee |
| Cancel | POST | `/api/v1/bank-guarantee/{id}/cancel` | Cancel guarantee |

### Example Request (Create Guarantee)
```json
POST /api/v1/bank-guarantee/
{
  "guarantee_type": "PERFORMANCE",
  "applicant": {
    "name": "Construction Co LLC",
    "address": "789 Builder Way"
  },
  "beneficiary": {
    "name": "Real Estate Development Corp",
    "address": "101 Property Ave"
  },
  "guarantee_amount": 100000.00,
  "currency": "USD",
  "validity_date": "2024-12-31",
  "contract_reference": "CONTRACT-2024-001",
  "description": "Performance guarantee for office construction"
}
```

---

## Documentary Collection

### What is This Feature?
**Simple Explanation:** This is a way to **handle shipping documents** for international trade. The bank helps the seller get paid by holding the shipping documents until the buyer pays or accepts a bill of exchange.

### Real-World Example
**Scenario:** Indian textile exporter ships goods to UK buyer. Instead of paying upfront, they use documentary collection:

1. Exporter ships goods and gets shipping documents from shipping company
2. Exporter gives documents to their bank (Collection Bank)
3. Collection Bank sends documents to UK buyer's bank
4. UK buyer either:
   - **D/P (Documents against Payment)**: Pays immediately to get documents
   - **D/A (Documents against Acceptance)**: Signs a promise to pay later
5. Once paid/accepted, buyer gets documents to claim goods

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| List Collections | GET | `/api/v1/documentary-collection/` | Get all collections |
| Create Collection | POST | `/api/v1/documentary-collection/` | Create new collection |
| Get Details | GET | `/api/v1/documentary-collection/{id}` | View collection |
| Present Documents | POST | `/api/v1/documentary-collection/{id}/present` | Present to drawee |
| Accept | POST | `/api/v1/documentary-collection/{id}/accept` | D/A acceptance |
| Payment | POST | `/api/v1/documentary-collection/{id}/payment` | D/P payment |
| Release Documents | POST | `/api/v1/documentary-collection/{id}/release` | Release documents |

### Collection Types
- **D/P (Documents against Payment)**: Buyer must pay to get documents
- **D/A (Documents against Acceptance)**: Buyer signs a promise (aval) to pay later

---

## Invoice Financing

### What is This Feature?
**Simple Explanation:** Also called "Invoice Factoring", this helps businesses **get paid faster**. Instead of waiting 30-60 days for customers to pay, businesses can get immediate cash by selling their invoices to the bank (with a small fee).

### Real-World Example
**Scenario:** Supplier ABC has sent $50,000 of goods to Big Retail Store. Big Retail promises to pay in 60 days. ABC needs cash now to pay their workers.

1. ABC submits the invoice to the bank
2. Bank reviews and approves (based on Big Retail's credit)
3. Bank advances 80-90% of invoice value ($40,000-$45,000)
4. When Big Retail pays after 60 days, bank gets paid
5. Bank deducts their fee and gives remaining amount to ABC

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| List Invoices | GET | `/api/v1/invoice-financing/` | Get all invoices |
| Submit Invoice | POST | `/api/v1/invoice-financing/` | Submit for financing |
| Get Details | GET | `/api/v1/invoice-financing/{id}` | View invoice |
| Approve Financing | POST | `/api/v1/invoice-financing/{id}/approve` | Approve advance |
| Disburse | POST | `/api/v1/invoice-financing/{id}/disburse` | Release funds |
| Receive Payment | POST | `/api/v1/invoice-financing/{id}/receive-payment` | Invoice paid by buyer |
| Reconcile | POST | `/api/v1/invoice-financing/{id}/reconcile` | Complete transaction |

### Example Request (Submit Invoice)
```json
POST /api/v1/invoice-financing/
{
  "invoice_number": "INV-2024-001",
  "seller": {
    "name": "ABC Suppliers Ltd",
    "address": "222 Supplier Lane"
  },
  "buyer": {
    "name": "Big Retail Store",
    "address": "333 Retail Blvd"
  },
  "invoice_amount": 50000.00,
  "currency": "USD",
  "invoice_date": "2024-01-15",
  "due_date": "2024-03-15",
  "financing_percentage": 85,
  "description": "Supply of office equipment"
}
```

---

## Trade Loan

### What is This Feature?
**Simple Explanation:** A Trade Loan is **short-term financing** to help businesses import or export goods. It's like a temporary loan specifically for trade transactions.

### Real-World Example
**Scenario:** Importer wants to bring electronics from China. They need to pay the Chinese manufacturer before goods arrive in the USA.

1. Importer applies for a $200,000 trade loan
2. Bank checks the trade documents (purchase order, invoice)
3. Bank approves and disburses funds to manufacturer
4. When goods arrive and are sold, importer repays the bank

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| List Loans | GET | `/api/v1/trade-loan/` | Get all loans |
| Apply | POST | `/api/v1/trade-loan/` | Apply for loan |
| Get Details | GET | `/api/v1/trade-loan/{id}` | View loan |
| Approve | POST | `/api/v1/trade-loan/{id}/approve` | Approve loan |
| Disburse | POST | `/api/v1/trade-loan/{id}/disburse` | Release funds |
| Repay | POST | `/api/v1/trade-loan/{id}/repay` | Make repayment |
| Foreclose | POST | `/api/v1/trade-loan/{id}/foreclose` | Early closure |

---

## Risk Management

### What is This Feature?
**Simple Explanation:** This feature helps the bank **identify and manage risks** in trade finance. It monitors transactions for suspicious patterns, calculates risk scores, and ensures compliance with regulations.

### Real-World Example
**Scenario:** The system flags a transaction because:
- The beneficiary is in a high-risk country
- The amount is unusually large for this customer
- The same invoice appears to be financed twice (fraud detection)

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| Risk Dashboard | GET | `/api/v1/risk/dashboard` | Get risk overview |
| Risk Assessment | POST | `/api/v1/risk/assess` | Run risk check |
| Get Alerts | GET | `/api/v1/risk/alerts` | Get risk alerts |
| Resolve Alert | POST | `/api/v1/risk/alerts/{id}/resolve` | Address alert |
| Exposure Report | GET | `/api/v1/risk/exposure` | Get exposure report |
| Limit Check | POST | `/api/v1/risk/check-limit` | Verify credit limit |

### Risk Scoring Example
```json
POST /api/v1/risk/assess
{
  "transaction_type": "LETTER_OF_CREDIT",
  "amount": 100000,
  "currency": "USD",
  "country_risk": 3,
  "beneficiary_risk_score": 65,
  "transaction_pattern": "NORMAL"
}

// Response
{
  "risk_score": 72,
  "risk_level": "HIGH",
  "factors": [
    {"type": "COUNTRY", "score": 20, "reason": "High-risk jurisdiction"},
    {"type": "AMOUNT", "score": 25, "reason": "Exceeds single transaction limit"},
    {"type": "PATTERN", "score": 27, "reason": "Unusual transaction frequency"}
  ],
  "recommendation": "REVIEW_REQUIRED"
}
```

---

## Compliance & KYC

### What is This Feature?
**Simple Explanation:** KYC (Know Your Customer) ensures the bank knows who they're doing business with. This feature verifies customer identities, checks against sanctions lists, and maintains regulatory compliance.

### Real-World Example
**Scenario:** New corporate customer wants to open trade finance accounts.

1. Bank collects company documents (registration, ownership)
2. System runs background checks
3. Verifies directors against sanctions lists
4. Assesses money laundering risk
5. Creates customer profile with risk rating

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| List Customers | GET | `/api/v1/compliance/customers` | Get all customers |
| Register Customer | POST | `/api/v1/compliance/customers` | Add new customer |
| Run KYC Check | POST | `/api/v1/compliance/kyc/{customer_id}` | Run verification |
| Get KYC Status | GET | `/api/v1/compliance/kyc/{customer_id}` | View KYC status |
| Sanctions Check | POST | `/api/v1/compliance/sanctions-check` | Screen against lists |
| Compliance Report | GET | `/api/v1/compliance/reports` | Generate reports |

---

## Document Management

### What is This Feature?
**Simple Explanation:** Trade finance involves lots of documents (invoices, bills of lading, insurance certificates). This feature stores, organizes, and manages all documents securely.

### Real-World Example
**Scenario:** User uploads a Bill of Lading for an LC.

1. User clicks "Upload Document"
2. Selects file (PDF, max 10MB)
3. Frontend uploads to backend
4. Backend stores file, creates record
5. Document is linked to the LC transaction
6. Users can view/download anytime

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| Upload | POST | `/api/v1/documents/upload` | Upload file |
| List | GET | `/api/v1/documents/` | Get documents |
| Download | GET | `/api/v1/documents/{id}/download` | Download file |
| Delete | DELETE | `/api/v1/documents/{id}` | Delete file |
| Preview | GET | `/api/v1/documents/{id}/preview` | View in browser |

### Upload Example
```javascript
// Frontend code
const formData = new FormData();
formData.append('file', selectedFile);
formData.append('document_type', 'BILL_OF_LADING');
formData.append('reference_id', 'LC-12345');

const response = await axios.post('/api/v1/documents/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

---

## Reports & Analytics

### What is This Feature?
**Simple Explanation:** This feature provides **business insights** through dashboards and reports. Managers can see transaction volumes, profitability, portfolio health, and more.

### Real-World Example
**Scenario:** The Head of Trade Finance wants a monthly report.

1. Opens Reports section
2. Selects "Monthly Trade Volume Report"
3. Picks date range (January 2024)
4. System generates PDF/Excel report
5. Can view charts on dashboard

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| Dashboard Data | GET | `/api/v1/reports/dashboard` | Get dashboard metrics |
| Generate Report | POST | `/api/v1/reports/generate` | Create new report |
| List Reports | GET | `/api/v1/reports/` | Get saved reports |
| Download Report | GET | `/api/v1/reports/{id}/download` | Download PDF/Excel |
| Schedule Report | POST | `/api/v1/reports/schedule` | Schedule automatic reports |

---

## Notifications

### What is This Feature?
**Simple Explanation:** Keeps users informed about important events. Notifications are sent when:
- An LC is approved/rejected
- A document needs review
- A payment is received
- Risk alert is triggered

### Real-World Example
**Scenario:** Relationship Manager submits an LC for approval.

1. System creates LC in "SUBMITTED" status
2. Notification sent to Credit Manager
3. Credit Manager sees notification in bell icon
4. Credit Manager reviews and approves
5. System notifies RM that LC is approved

### Frontend → Backend Communication

| Action | HTTP Method | Endpoint | Description |
|--------|-------------|----------|-------------|
| Get Notifications | GET | `/api/v1/notifications/` | Get user notifications |
| Mark Read | POST | `/api/v1/notifications/{id}/read` | Mark as read |
| Mark All Read | POST | `/api/v1/notifications/mark-all-read` | Mark all as read |
| Subscribe | POST | `/api/v1/notifications/subscribe` | Subscribe to events |

### WebSocket for Real-time Updates
```javascript
// Frontend connects to WebSocket for instant notifications
const ws = new WebSocket('ws://localhost:8000/ws/notifications');

ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  showToast(notification.title, notification.message);
};
```

---

## Docker Commands

### Starting the Platform

```bash
# 1. Navigate to project directory
cd "Python/Opencode/Trade Finance Platform"

# 2. Copy environment file (optional - uses defaults if not present)
cp .env.example .env

# 3. Build and start all services
docker-compose up -d

# 4. View service status
docker-compose ps

# 5. View logs (all services)
docker-compose logs -f

# 6. View logs (specific service)
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Checking Services

```bash
# Check if services are running
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Access API documentation
# Open in browser: http://localhost:8000/docs
```

### Common Operations

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (complete reset)
docker-compose down -v

# Restart a specific service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build

# View container resource usage
docker stats

# Execute command in container
docker-compose exec backend bash
docker-compose exec db psql -U tradefinance
```

### Database Operations

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U tradefinance -d tradefinance

# Run SQLAlchemy migrations (inside backend container)
docker-compose exec backend python -m alembic upgrade head

# Create new migration
docker-compose exec backend python -m alembic revision --autogenerate -m "description"
```

### Troubleshooting

```bash
# View logs for specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
docker-compose logs redis

# Check backend logs in real-time
docker-compose logs -f backend

# Restart stuck service
docker-compose restart backend

# Rebuild everything from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Run in production mode (no hot reload)
docker-compose -f docker-compose.yml up -d --scale backend=2

# View running containers
docker-compose ps

# Scale backend (for load balancing)
docker-compose up -d --scale backend=3
```

---

## Summary

This platform provides a comprehensive trade finance solution with:

1. **Secure Authentication** - JWT tokens, MFA support
2. **Complete Trade Products** - LC, Guarantees, Documentary Collection, Invoice Financing, Trade Loans
3. **Risk Management** - Real-time risk scoring and alerts
4. **Compliance** - KYC verification and sanctions screening
5. **Document Management** - Secure file storage and retrieval
6. **Analytics** - Dashboards and reports
7. **Real-time Notifications** - WebSocket-based alerts

All features follow RESTful API patterns with clear frontend-backend communication through nginx reverse proxy.
