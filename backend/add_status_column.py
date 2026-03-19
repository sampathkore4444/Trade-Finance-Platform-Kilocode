"""
Script to add all missing columns and enum values to reports table
Run: python add_status_column.py
"""

import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import text


async def add_columns():
    async with AsyncSessionLocal() as session:
        try:
            # Add all missing columns if they don't exist
            await session.execute(
                text(
                    "ALTER TABLE reports ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending'"
                )
            )
            await session.execute(
                text(
                    "ALTER TABLE reports ADD COLUMN IF NOT EXISTS file_path VARCHAR(500)"
                )
            )
            await session.execute(
                text(
                    "ALTER TABLE reports ADD COLUMN IF NOT EXISTS filename VARCHAR(255)"
                )
            )
            await session.execute(
                text("ALTER TABLE reports ADD COLUMN IF NOT EXISTS parameters TEXT")
            )

            # Add missing enum values to reporttype
            await session.execute(
                text("ALTER TYPE reporttype ADD VALUE IF NOT EXISTS 'lc_summary'")
            )
            await session.execute(
                text(
                    "ALTER TYPE reporttype ADD VALUE IF NOT EXISTS 'guarantee_summary'"
                )
            )
            await session.execute(
                text("ALTER TYPE reporttype ADD VALUE IF NOT EXISTS 'loan_summary'")
            )
            await session.execute(
                text(
                    "ALTER TYPE reporttype ADD VALUE IF NOT EXISTS 'portfolio_summary'"
                )
            )
            await session.execute(
                text("ALTER TYPE reporttype ADD VALUE IF NOT EXISTS 'compliance'")
            )

            # Add missing enum values to reportstatus
            await session.execute(
                text("ALTER TYPE reportstatus ADD VALUE IF NOT EXISTS 'pending'")
            )
            await session.execute(
                text("ALTER TYPE reportstatus ADD VALUE IF NOT EXISTS 'processing'")
            )
            await session.execute(
                text("ALTER TYPE reportstatus ADD VALUE IF NOT EXISTS 'completed'")
            )
            await session.execute(
                text("ALTER TYPE reportstatus ADD VALUE IF NOT EXISTS 'failed'")
            )

            await session.commit()
            print("All missing columns and enum values added successfully!")
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(add_columns())
