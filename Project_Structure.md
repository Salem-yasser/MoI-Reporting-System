MOI-REPORTING-API/
│
├── 📁 app/
│   ├── __init__.py
│   ├── main.py                       # ⚡ UPDATED: Initializes both DB engines on startup
│   │
│   ├── 📁 api/
│   │   ├── __init__.py
│   │   └── 📁 v1/
│   │       ├── __init__.py
│   │       ├── admin.py              # 🆕 NEW: Admin Dashboard endpoints (Reads from Analytics DB)
│   │       ├── auth.py
│   │       ├── reports.py            # ⚡ UPDATED: Uses 'get_db_ops' dependency (Writes to Ops DB)
│   │       └── users.py
│   │
│   ├── 📁 core/
│   │   ├── __init__.py
│   │   ├── config.py                 # ⚡ UPDATED: Contains 2 connection strings (Ops & Analytics)
│   │   ├── database.py               # ⚡ UPDATED: Defines 2 Engines & 2 Dependency Generators
│   │   └── security.py
│   │
│   ├── 📁 models/                    # ⚡ UPDATED: Models split by Database
│   │   ├── __init__.py
│   │   ├── analytics.py              # 🆕 NEW: Star Schema models (Fact_Reports, Dim_Date) -> Analytics DB
│   │   ├── attachment.py             # (Stays same, inherits from BaseOps) -> Ops DB
│   │   ├── report.py                 # (Stays same, inherits from BaseOps) -> Ops DB
│   │   └── user.py                   # (Stays same, inherits from BaseOps) -> Ops DB
│   │
│   ├── 📁 schemas/                   # (Data contracts don't change much, just add new ones)
│   │   ├── __init__.py
│   │   ├── analytics.py              # 🆕 NEW: Schemas for Admin Dashboard responses (e.g., WeeklyStats)
│   │   ├── attachment.py
│   │   ├── report.py
│   │   └── user.py
│   │
│   └── 📁 services/
│       ├── __init__.py
│       ├── analytics_service.py      # 🆕 NEW: Logic for complex queries on Analytics DB
│       ├── report_service.py         # ⚡ UPDATED: logic for standard CRUD on Ops DB
│       ├── user_service.py
│       ├── blob_service.py
│       ├── speech_service.py         # 🆕 NEW: Azure Speech SDK logic (separated from AI)
│       ├── notification_service.py   # 🆕 NEW: Firebase/Email logic (separated for clean code)
│       └── ai_service.py             # ⚡ UPDATED: Focuses only on ML Model integration
│
├── 📁 database/
│   ├── 📁 docs/
│   ├── 📁 migrations/                # (Advanced: You might need separate Alembic branches for 2 DBs)
│   └── 📁 scripts/
│       ├── schema_ops.sql            # 🆕 NEW: SQL script for Transactional DB
│       ├── schema_analytics.sql      # 🆕 NEW: SQL script for Star Schema DB
│       ├── seed_data.sql
│       └── test_queries.sql
│
├── 📁 tests/
│   ├── __init__.py
│   ├── conftest.py                   # ⚡ UPDATED: Fixtures for mocking 2 databases
│   ├── test_api_reports.py
│   ├── test_api_admin.py             # 🆕 NEW: Tests for admin endpoints
│   ├── test_database.py
│   └── test_services.py
│
├── 📄 .env                           # ⚡ UPDATED: Includes SQLALCHEMY_DATABASE_URI_OPS & _ANALYTICS
├── 📄 docker-compose.yml
├── 📄 Dockerfile
├── 📄 requirements.txt
└── 📄 README.md