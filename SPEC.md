# Trade Finance Platform - Technical Specification

## 1. Project Overview

### 1.1 Purpose
Enterprise-grade Trade Finance Platform for commercial banks enabling end-to-end management of trade finance instruments including Letters of Credit (LC), Bank Guarantees, Standby Letters of Credit (SBLC), Documentary Collection, Invoice Financing, and Supply Chain Finance.

### 1.2 Goals
- Provide a unified platform for managing all trade finance instruments
- Enable seamless collaboration between importers, exporters, and banks
- Automate workflow processes and reduce manual intervention
- Ensure regulatory compliance with international trade standards (UCP 600, URDG 758, ISP98)
- Deliver real-time transaction monitoring and reporting
- Support multi-currency transactions with competitive exchange rates

### 1.3 Target Users
- **Bank Officers**: Trade finance managers, credit officers, operations staff
- **Corporate Clients**: Importers, exporters, trading companies
- **Correspondent Banks**: Partner banks for cross-border transactions
- **Compliance Teams**: KYC/AML reviewers, risk analysts
- **Auditors**: Internal and external audit personnel

---

## 2. Architecture

### 2.1 Modular Monolithic Architecture

The platform follows a **Modular Monolithic Architecture** that provides:

| Aspect | Description |
|--------|-------------|
| **Modularity** | Clear separation of business domains as independent modules |
| **Scalability** | Horizontal scaling through stateless service instances |
| **Maintainability** | Isolated module updates without full system redeployment |
| **Reliability** | Fault isolation within modules |
| **Deployability** | Single deployment unit with nginx load balancing |

### 2.2 System Architecture Diagram

```
                                    ┌─────────────────────────────────────────┐
                                    │         External Clients               │
                                    │  (Corporate Clients, Correspondent      │
                                    │   Banks, External Systems)             │
                                    └─────────────────┬───────────────────────┘
                                                      │
                                    ┌─────────────────▼───────────────────────┐
                                    │              Nginx Load Balancer        │
                                    │         (Port 80/443 - HTTPS)          │
                                    │  - SSL/TLS Termination                 │
                                    │  - Static Asset Serving                │
                                    │  - Load Balancing                      │
                                    │  - Rate Limiting                       │
                                    └─────────────────┬───────────────────────┘
                                                      │
                    ┌─────────────────────────────────┼─────────────────────────────────┐
                    │                                 │                                 │
        ┌───────────▼───────────┐       ┌───────────▼───────────┐       ┌───────────▼───────────┐
        │    Frontend Server    │       │    Backend API        │       │    Static Assets      │
        │    (Vite + React)     │       │    (FastAPI)          │       │    (Nginx)            │
        │    Port: 5173         │       │    Port: 8000         │       │    Port: 8080         │
        └───────────────────────┘       └───────────┬───────────┘       └───────────────────────┘
                                                    │
                    ┌───────────────────────────────┼───────────────────────────────┐
                    │                               │                               │
        ┌───────────▼───────────┐       ┌───────────▼───────────┐       ┌───────────▼───────────┐
        │    Module 1           │       │    Module 2           │       │    Module N           │
        │    Letter of Credit   │       │    Bank Guarantee     │       │    ...                │
        │    (lc/)              │       │    (guarantee/)       │       │                       │
        └───────────────────────┘       └───────────────────────┘       └───────────────────────┘
                    │                               │                               │
                    └───────────────────────────────┼───────────────────────────────┘
                                                    │
                                    ┌───────────────▼───────────────┐
                                    │       Shared Core Services     │
                                    │  ┌─────────────────────────┐  │
                                    │  │ Authentication (JWT)    │  │
                                    │  │ Authorization (RBAC)    │  │
                                    │  │ Audit Logging           │  │
                                    │  │ Notification Service    │  │
                                    │  │ File Storage            │  │
                                    │  │ Payment Gateway         │  │
                                    │  │ External API Gateway    │  │
                                    │  └─────────────────────────┘  │
                                    └───────────────┬───────────────┘
                                                    │
                    ┌───────────────────────────────┼───────────────────────────────┐
                    │                               │                               │
        ┌───────────▼───────────┐       ┌───────────▼───────────┐       ┌───────────▼───────────┐
        │    PostgreSQL        │       │    Redis Cache        │       │    Message Queue      │
        │    (Primary DB)      │       │    (Sessions/Cache)  │       │    (RabbitMQ)         │
        │    Port: 5432        │       │    Port: 6379         │       │    Port: 5672         │
        └───────────────────────┘       └───────────────────────┘       └───────────────────────┘
```

### 2.3 Nginx Configuration

#### Main Nginx Configuration (`nginx.conf`)

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging Format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # Performance Optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript 
               application/xml application/xml+rss text/javascript application/x-javascript;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    # Upstream Backend Servers
    upstream backend_api {
        server 127.0.0.1:8000 weight=5;
        server 127.0.0.1:8001 weight=3;
        server 127.0.0.1:8002 weight=2;
        keepalive 32;
    }

    # Include module configurations
    include /etc/nginx/conf.d/*.conf;
}
```

#### API Gateway Configuration (`api.conf`)

```nginx
server {
    listen 80;
    server_name api.tradefinance.local;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.tradefinance.local;

    ssl_certificate /etc/nginx/ssl/tradefinance.crt;
    ssl_certificate_key /etc/nginx/ssl/tradefinance.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # Rate Limiting
    limit_req zone=api_limit burst=20 nodelay;
    limit_conn conn_limit 10;

    # API Request Buffering
    client_body_buffer_size 16k;
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    proxy_busy_buffers_size 256k;

    location /api/ {
        # Auth Endpoints - Stricter Rate Limiting
        location ~ ^/api/v1/auth {
            limit_req zone=auth_limit burst=10 nodelay;
            proxy_pass http://backend_api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # Other API Endpoints
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout Settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket Support
    location /ws/ {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Health Check Endpoint
    location /health {
        proxy_pass http://backend_api;
        access_log off;
    }

    # Monitoring Metrics
    location /metrics {
        proxy_pass http://backend_api;
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        deny all;
    }
}
```

#### Frontend Configuration (`frontend.conf`)

```nginx
server {
    listen 80;
    server_name tradefinance.local;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tradefinance.local;

    ssl_certificate /etc/nginx/ssl/tradefinance.crt;
    ssl_certificate_key /etc/nginx/ssl/tradefinance.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    root /var/www/tradefinance/dist;
    index index.html;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.tradefinance.local wss://api.tradefinance.local;" always;

    # Gzip for Static Assets
    gzip on;
    gzip_static on;
    gzip_types text/plain text/css application/json application/javascript text/javascript;
    gzip_min_length 1000;

    # Static Assets Caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # HTML - No Cache for SPA
    location / {
        try_files /index.html =404;
        
        # CORS Headers for API Calls
        add_header Access-Control-Allow-Origin "https://tradefinance.local" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
        
        if ($request_method = OPTIONS) {
            return 204;
        }
    }

    # Admin Section - Additional Security
    location /admin {
        # Require specific IP range or use VPN
        # allow 10.0.0.0/8;
        # deny all;
        
        try_files /admin/index.html =404;
    }
}
```

---

## 3. Technology Stack

### 3.1 Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI Framework |
| Vite | 5.x | Build Tool & Dev Server |
| Tailwind CSS | 3.x | Utility-first CSS Framework |
| React Router | 6.x | Client-side Routing |
| Zustand | 4.x | State Management |
| React Query | 5.x | Server State Management |
| Axios | 1.x | HTTP Client |
| React Hook Form | 7.x | Form Management |
| Zod | 3.x | Schema Validation |
| Recharts | 2.x | Charts & Visualizations |
| TanStack Table | 8.x | Data Tables |
| React Hook Form | 7.x | Form Validation |
| date-fns | 3.x | Date Utilities |

### 3.2 Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.109+ | Web Framework |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.x | Data Validation |
| Alembic | 1.13+ | Database Migrations |
| PostgreSQL | 15+ | Primary Database |
| Redis | 7.x | Cache & Session Store |
| RabbitMQ | 3.12+ | Message Queue |
| Celery | 5.3+ | Task Queue |
| Python-Jose | 3.x | JWT Handling |
| Passlib | 1.7+ | Password Hashing |
| Bcrypt | 4.x | Cryptography |
| PyPDF2 | 3.x | PDF Processing |
| OpenPyXL | 3.x | Excel Processing |
| Uvicorn | 0.27+ | ASGI Server |
| Gunicorn | 21.x | WSGI Server |
| Psycopg2 | 2.9+ | PostgreSQL Driver |
| Python-Multipart | 0.0.x | File Upload |

### 3.3 DevOps & Infrastructure

| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Orchestration |
| Nginx | Reverse Proxy & Load Balancer |
| GitLab CI/CD | Continuous Integration |
| Prometheus | Metrics Collection |
| Grafana | Monitoring Dashboards |

---

## 4. Feature Specifications

### 4.1 Authentication & Authorization

#### Features
- Multi-factor Authentication (MFA)
- Single Sign-On (SSO) Integration
- Role-Based Access Control (RBAC)
- JWT Token Management with Refresh Tokens
- Session Management with Concurrent Login Controls
- Password Policies with Complexity Requirements
- Account Lockout After Failed Attempts
- Audit Logging for All Authentication Events

#### User Roles
| Role | Permissions |
|------|-------------|
| System Admin | Full system access, user management, configuration |
| Trade Finance Manager | Approve/reject transactions, manage team, reports |
| Relationship Manager | Client management, transaction initiation |
| Operations Officer | Transaction processing, document handling |
| Credit Officer | Credit assessments, risk evaluation |
| Compliance Officer | KYC/AML review, sanctions screening |
| Auditor | Read-only access to all transactions |
| Corporate Client | Self-service portal access |

### 4.2 Letter of Credit (LC) Module

#### LC Types
- **Import LC**: Documentary credit issued on behalf of importer
- **Export LC**: Documentary credit received from foreign bank
- **Standby LC**: Guarantee payment on default
- **Revocable/Irrevocable LC**: Amendment flexibility
- **Confirmed LC**: Additional guarantee from confirming bank
- **Transferable LC**: Beneficiary can transfer to third party
- **Back-to-Back LC**: Two linked LCs for trade chain

#### Features
- LC Application & Issuance
- Amendment Processing
- Document Presentation & Checking
- Negotiation & Payment
- LC Tracking & Status Updates
- SWIFT MT700/MT701 Message Generation
- Electronic Bill of Lading Integration
- Blockchain-based LC Tracking (Optional)

#### LC Workflow
```
Draft → Submitted → Under Review → Approved → Issued → 
Documents Received → Examination → Payment/Acceptance → Closed
```

### 4.3 Bank Guarantee Module

#### Guarantee Types
- **Bid Bond/Tender Guarantee**: Tender participation security
- **Performance Bond**: Contract performance guarantee
- **Advance Payment Guarantee**: Refund of advance payment
- **Warranty Guarantee**: Post-delivery obligations
- **Customs Guarantee**: Duty deferment
- **Financial Guarantee**: Financial obligations

#### Features
- Guarantee Application
- Counter-Guarantee Management
- Claim Processing
- Expiry & Extension Management
- Guarantee Pricing & Fee Calculation
- SWIFT MT760/MT762 Message Generation

### 4.4 Documentary Collection Module

#### Collection Types
- **Documents Against Payment (D/P)**: Payment before release
- **Documents Against Acceptance (D/A)**: Acceptance before release
- **Clean Collection**: Documents without shipping

#### Features
- Collection Initiation
- Document Dispatch
- Payment/Acceptance Tracking
- Nostro/Vostro Account Management
- SWIFT MT410/MT412/MT420 Messages

### 4.5 Invoice Financing Module

#### Financing Types
- **Invoice Discounting**: Seller borrows against receivables
- **Factoring**: Full receivable management
- **Supply Chain Finance**: Buyer-centric financing
- **Reverse Factoring**: Approved supplier financing

#### Features
- Invoice Submission & Verification
- Financing Request & Approval
- Payment Processing
- Receivable Tracking
- Credit Risk Assessment
- Early/Late Payment Calculations

### 4.6 Trade Loan Module

#### Loan Types
- **Import Finance**: Pre-shipment/post-shipment financing
- **Export Finance**: Pre-shipment credit
- **Working Capital Loan**: Trade cycle financing
- **Structured Trade Finance**: Project-specific

#### Features
- Loan Application
- Credit Assessment & Scoring
- Collateral Management
- Disbursement Processing
- Repayment Schedule
- Interest Calculation
- Loan Restructuring

### 4.7 Risk Management Module

#### Features
- Credit Risk Assessment
- Country Risk Evaluation
- Counterparty Risk Analysis
- Market Risk Monitoring
- Operational Risk Controls
- Risk Rating & Scoring
- Limit Management
- Exposure Tracking
- Stress Testing
- Risk Alerts & Notifications

### 4.8 Compliance & Regulatory Module

#### Features
- KYC/AML Screening
- Sanctions List Checking
- PEP (Politically Exposed Persons) Screening
- Adverse Media Monitoring
- Transaction Monitoring
- Suspicious Activity Reports (SAR)
- Regulatory Reporting
- Audit Trail
- Data Retention Policies

### 4.9 Reporting & Analytics Module

#### Report Types
- Transaction Reports
- Portfolio Reports
- Risk Reports
- Compliance Reports
- Performance Reports
- Regulatory Reports
- Custom Report Builder

#### Analytics
- Real-time Dashboards
- Trend Analysis
- Predictive Analytics
- Portfolio Segmentation
- Key Risk Indicators (KRI)
- Key Performance Indicators (KPI)

### 4.10 Notification & Communication Module

#### Features
- Email Notifications
- SMS Alerts
- In-App Notifications
- Webhooks for External Systems
- SWIFT Message Notifications
- Task Assignments
- Approval Workflow Notifications
- Document Request Notifications

### 4.11 Document Management Module

#### Features
- Document Upload & Storage
- Document Classification
- Version Control
- Digital Signatures
- Document Templates
- OCR for Document Extraction
- Secure Document Sharing
- Document Expiry Tracking
- Archival & Retention

### 4.12 Integration Module

#### External Integrations
- SWIFT Network (MT messages)
- Blockchain Platforms (Trade Finance)
- Credit Bureaus
- Sanctions Databases
- Exchange Rate Providers
- Payment Gateways
- ERP Systems
- Trade Registry APIs

---

## 5. Database Schema Overview

### 5.1 Core Tables

```sql
-- Users & Authentication
users
user_roles
role_permissions
permissions
sessions
login_audit

-- Organizations
organizations
branches
departments

-- Trade Finance Transactions
letters_of_credit
lc_amendments
lc_documents
lc_guarantees

bank_guarantees
guarantee_amendments
guarantee_claims

documentary_collections
collection_documents

invoice_financing
invoices
financing_requests

trade_loans
loan_disbursements
loan_repayments
collaterals

-- Risk & Compliance
risk_assessments
compliance_screening
sanctions_checks
audit_logs
```

---

## 6. API Specification

### 6.1 API Structure

```
/api/v1/
├── /auth/                    # Authentication
│   ├── POST /login
│   ├── POST /logout
│   ├── POST /refresh
│   ├── POST /mfa/verify
│   └── POST /password/reset
│
├── /users/                   # User Management
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   ├── DELETE /{id}
│   └── PUT /{id}/roles
│
├── /lc/                      # Letter of Credit
│   ├── GET /                # List LC
│   ├── POST /               # Create LC
│   ├── GET /{id}            # Get LC Details
│   ├── PUT /{id}            # Update LC
│   ├── POST /{id}/amend     # Amend LC
│   ├── POST /{id}/documents # Submit Documents
│   ├── POST /{id}/accept    # Accept Documents
│   └── POST /{id}/payment   # Process Payment
│
├── /guarantee/              # Bank Guarantee
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   ├── POST /{id}/claim
│   └── POST /{id}/extend
│
├── /collection/             # Documentary Collection
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   └── POST /{id}/dispatch
│
├── /invoice/                # Invoice Financing
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   └── POST /{id}/finance
│
├── /loan/                   # Trade Loan
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── POST /{id}/disburse
│   └── POST /{id}/repay
│
├── /risk/                   # Risk Management
│   ├── GET /assessment
│   ├── POST /assessment
│   ├── GET /limits
│   └── GET /exposures
│
├── /compliance/             # Compliance
│   ├── GET /kyc
│   ├── POST /kyc/screen
│   ├── GET /sanctions
│   └── GET /reports
│
├── /documents/             # Document Management
│   ├── GET /
│   ├── POST /upload
│   ├── GET /{id}
│   ├── DELETE /{id}
│   └── GET /{id}/download
│
├── /reports/               # Reporting
│   ├── GET /transactions
│   ├── GET /portfolio
│   ├── GET /risk
│   └── POST /custom
│
├── /notifications/         # Notifications
│   ├── GET /
│   ├── PUT /{id}/read
│   └── DELETE /{id}
│
└── /webhooks/             # Webhooks
    ├── GET /
    ├── POST /
    ├── PUT /{id}
    └── DELETE /{id}
```

---

## 7. Module Structure

### 7.1 Backend Module Structure

```
backend/
├── app/
│   ├── main.py                    # Application Entry Point
│   ├── config.py                  # Configuration Management
│   ├── database.py                # Database Connection
│   └── utils/
│       ├── exceptions.py          # Custom Exceptions
│       ├── validators.py          # Input Validators
│       └── helpers.py             # Utility Functions
│
│   ├── core/                      # Core Services
│   │   ├── auth/
│   │   │   ├── jwt_handler.py
│   │   │   ├── password_handler.py
│   │   │   ├── mfa_handler.py
│   │   │   └── rbac_handler.py
│   │   ├── security/
│   │   │   ├── encryption.py
│   │   │   ├── sanitization.py
│   │   │   └── audit_logger.py
│   │   ├── notifications/
│   │   │   ├── email_service.py
│   │   │   ├── sms_service.py
│   │   │   └── webhook_service.py
│   │   └── integrations/
│   │       ├── swift_service.py
│   │       ├── payment_gateway.py
│   │       └── exchange_rate.py
│   │
│   ├── modules/                   # Business Modules
│   │   ├── users/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routers.py
│   │   │   └── services.py
│   │   │
│   │   ├── letter_of_credit/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routers.py
│   │   │   ├── services.py
│   │   │   └── workflows.py
│   │   │
│   │   ├── bank_guarantee/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routers.py
│   │   │   └── services.py
│   │   │
│   │   ├── documentary_collection/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routers.py
│   │   │   └── services.py
│   │   │
│   │   ├── invoice_financing/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routers.py
│   │   │   └── services.py
│   │   │
│   │   ├── trade_loan/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routers.py
│   │   │   └── services.py
│   │   │
│   │   ├── risk_management/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routers.py
│   │   │   ├── services.py
│   │   │   └── calculators.py
│   │   │
│   │   ├── compliance/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routers.py
│   │   │   ├── services.py
│   │   │   └── screening.py
│   │   │
│   │   ├── documents/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routers.py
│   │   │   ├── services.py
│   │   │   └── storage.py
│   │   │
│   │   ├── reports/
│   │   │   ├── routers.py
│   │   │   ├── services.py
│   │   │   └── generators.py
│   │   │
│   │   └── notifications/
│   │       ├── models.py
│   │       ├── schemas.py
│   │       ├── routers.py
│   │       └── services.py
│   │
│   └── tasks/                     # Celery Tasks
│       ├── notification_tasks.py
│       ├── compliance_tasks.py
│       ├── report_tasks.py
│       └── cleanup_tasks.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── alembic/                       # Database Migrations
│   └── versions/
│
├── scripts/                       # Utility Scripts
│   ├── seed_data.py
│   ├── create_admin.py
│   └── setup_swift.py
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 7.2 Frontend Module Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
│
├── src/
│   ├── main.tsx                   # Application Entry
│   ├── App.tsx                    # Root Component
│   ├── index.css                  # Global Styles
│   │
│   ├── api/                       # API Layer
│   │   ├── axios.ts               # Axios Configuration
│   │   ├── endpoints.ts           # API Endpoints
│   │   └── interceptors.ts        # Request/Response Interceptors
│   │
│   ├── components/                # Shared Components
│   │   ├── ui/                    # Base UI Components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Card.tsx
│   │   │   └── ...
│   │   │
│   │   ├── forms/                 # Form Components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── LCForm.tsx
│   │   │   ├── GuaranteeForm.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/                # Layout Components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Layout.tsx
│   │   │
│   │   └── common/               # Common Components
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── ConfirmDialog.tsx
│   │       └── FileUploader.tsx
│   │
│   ├── pages/                     # Page Components
│   │   ├── auth/
│   │   │   ├── Login.tsx
│   │   │   ├── ForgotPassword.tsx
│   │   │   └── VerifyMFA.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── Dashboard.tsx
│   │   │   └── components/
│   │   │
│   │   ├── lc/
│   │   │   ├── LCList.tsx
│   │   │   ├── LCCreate.tsx
│   │   │   ├── LCDetail.tsx
│   │   │   ├── LCAmend.tsx
│   │   │   └── LCDocuments.tsx
│   │   │
│   │   ├── guarantee/
│   │   │   ├── GuaranteeList.tsx
│   │   │   ├── GuaranteeCreate.tsx
│   │   │   └── GuaranteeDetail.tsx
│   │   │
│   │   ├── collection/
│   │   │   ├── CollectionList.tsx
│   │   │   └── CollectionDetail.tsx
│   │   │
│   │   ├── invoice/
│   │   │   ├── InvoiceList.tsx
│   │   │   └── InvoiceFinance.tsx
│   │   │
│   │   ├── loan/
│   │   │   ├── LoanList.tsx
│   │   │   ├── LoanApply.tsx
│   │   │   └── LoanDetail.tsx
│   │   │
│   │   ├── risk/
│   │   │   ├── RiskDashboard.tsx
│   │   │   └── RiskAssessment.tsx
│   │   │
│   │   ├── compliance/
│   │   │   ├── KYCScreening.tsx
│   │   │   └── ComplianceReports.tsx
│   │   │
│   │   ├── reports/
│   │   │   ├── TransactionReports.tsx
│   │   │   └── CustomReportBuilder.tsx
│   │   │
│   │   ├── settings/
│   │   │   ├── Profile.tsx
│   │   │   ├── Security.tsx
│   │   │   └── Notifications.tsx
│   │   │
│   │   └── admin/
│   │       ├── UserManagement.tsx
│   │       ├── RoleManagement.tsx
│   │       └── SystemConfiguration.tsx
│   │
│   ├── hooks/                     # Custom Hooks
│   │   ├── useAuth.ts
│   │   ├── useLC.ts
│   │   ├── useGuarantee.ts
│   │   ├── useDebounce.ts
│   │   └── usePagination.ts
│   │
│   ├── stores/                    # State Management
│   │   ├── authStore.ts
│   │   ├── notificationStore.ts
│   │   └── uiStore.ts
│   │
│   ├── services/                  # Service Layer
│   │   ├── authService.ts
│   │   ├── lcService.ts
│   │   ├── guaranteeService.ts
│   │   └── ...
│   │
│   ├── utils/                     # Utilities
│   │   ├── constants.ts
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── formatters/
│   │       ├── currency.ts
│   │       ├── date.ts
│   │       └── document.ts
│   │
│   ├── types/                     # TypeScript Types
│   │   ├── user.ts
│   │   ├── lc.ts
│   │   ├── guarantee.ts
│   │   └── ...
│   │
│   └── config/                    # Configuration
│       ├── constants.ts
│       └── environment.ts
│
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```

---

## 8. Security Features

### 8.1 Authentication Security
- JWT tokens with short expiration (15 min access, 7 day refresh)
- HTTP-only secure cookies for token storage
- MFA with TOTP/SMS
- Account lockout after 5 failed attempts
- Session timeout after 30 minutes of inactivity

### 8.2 Data Security
- AES-256 encryption for sensitive data at rest
- TLS 1.3 for data in transit
- Field-level encryption for PII (National ID, Tax IDs)
- Database row-level security
- Encrypted backups

### 8.3 API Security
- Rate limiting per user/IP
- Request validation with Pydantic
- SQL injection prevention via ORM
- XSS protection headers
- CSRF token validation
- API key authentication for integrations

### 8.4 Compliance
- GDPR data handling
- Audit logging for all operations
- Data retention policies
- Right to deletion support
- Access control logging

---

## 9. Deployment Configuration

### 9.1 Docker Compose (Development)

```yaml
version: '3.8'

services:
  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    volumes:
      - ./frontend/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
    networks:
      - tradefinance

  # Backend API
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://tfuser:tfpass@postgres:5432/tradefinance
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - rabbitmq
    networks:
      - tradefinance

  # Additional Backend Instances
  backend-worker:
    build: ./backend
    command: celery -A app.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://tfuser:tfpass@postgres:5432/tradefinance
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - rabbitmq
    networks:
      - tradefinance

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    networks:
      - tradefinance

  # Database
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=tfuser
      - POSTGRES_PASSWORD=tfpass
      - POSTGRES_DB=tradefinance
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - tradefinance

  # Redis Cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - tradefinance

  # Message Queue
  rabbitmq:
    image: rabbitmq:3.12-management
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - tradefinance

networks:
  tradefinance:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
```

---

## 10. Development Guidelines

### 10.1 Code Standards
- **Python**: PEP 8, type hints required, docstrings for all modules
- **TypeScript**: ESLint + Prettier, strict mode enabled
- **React**: Functional components, hooks, strict null checks
- **Testing**: Minimum 80% code coverage for core business logic

### 10.2 Git Workflow
- Feature branch per ticket
- Squash commits before merge
- Require code review for all changes
- Automated tests must pass before merge

### 10.3 API Design Principles
- RESTful URL structure
- Consistent response format
- Proper HTTP status codes
- Versioned APIs (v1, v2)
- Pagination for list endpoints
- Idempotent operations for mutations

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Backend: pytest with fixtures
- Frontend: Vitest + React Testing Library

### 11.2 Integration Tests
- API endpoint testing
- Database integration
- External service mocking

### 11.3 E2E Tests
- Playwright for full user flows
- Critical path coverage

### 11.4 Performance Tests
- Load testing with k6
- API response time benchmarks

---

## 12. Future Enhancements

### Phase 2
- Blockchain-based LC processing
- AI-powered document verification
- Real-time FX hedging
- Mobile applications

### Phase 3
- Open Banking API integration
- Smart contract automation
- Advanced analytics with ML
- Multi-bank collaboration hub

---

## 13. Glossary

| Term | Definition |
|------|------------|
| LC | Letter of Credit |
| SBLC | Standby Letter of Credit |
| UCP 600 | Uniform Customs and Practice for Documentary Credits |
| URDG 758 | Uniform Rules for Demand Guarantees |
| ISP98 | International Standby Practices |
| SWIFT | Society for Worldwide Interbank Financial Telecommunication |
| KYC | Know Your Customer |
| AML | Anti-Money Laundering |
| PEP | Politically Exposed Person |
| D/P | Documents Against Payment |
| D/A | Documents Against Acceptance |

---

## 14. References

- [UCP 600](https://www.iccwbo.org/) - Documentary Credits
- [URDG 758](https://www.iccwbo.org/) - Demand Guarantees
- [ISP98](https://www.iccwbo.org/) - Standby Practices
- [SWIFT Standards](https://www.swift.com/) - Trade Finance Messages
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-17  
**Author**: Trade Finance Platform Team  
**Status**: Draft for Review
