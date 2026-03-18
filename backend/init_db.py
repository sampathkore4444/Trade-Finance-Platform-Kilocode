"""
Database initialization script.
Run this to create all database tables.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db

# Import all models to register them with Base.metadata
from app.modules.users.models import User, Role, Permission, Organization, UserSession
from app.modules.letter_of_credit.models import LetterOfCredit, LCAmendment, LCDocument
from app.modules.bank_guarantee.models import BankGuarantee
from app.modules.documentary_collection.models import DocumentaryCollection
from app.modules.invoice_financing.models import InvoiceFinancing
from app.modules.trade_loan.models import TradeLoan
from app.modules.documents.models import Document
from app.modules.notifications.models import Notification
from app.modules.risk_management.models import RiskAssessment
from app.modules.compliance.models import ComplianceCheck
from app.modules.reports.models import Report


async def main():
    """Initialize the database."""
    print("Creating database tables...")

    try:
        await init_db()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
