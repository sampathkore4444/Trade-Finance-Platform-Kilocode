"""
Trade Loan Service
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.trade_loan.models import TradeLoan, LoanStatus, LoanType
from app.common.exceptions import NotFoundException
from app.common.helpers import generate_random_string


class TradeLoanService:
    async def generate_loan_number(self) -> str:
        prefix = "LN"
        date_part = datetime.utcnow().strftime("%Y%m%d")
        return f"{prefix}{date_part}{generate_random_string(6, True)}"

    async def create_loan(
        self,
        db: AsyncSession,
        loan_type: LoanType,
        principal_amount: Decimal,
        currency: str,
        created_by: int,
        **kwargs,
    ) -> TradeLoan:
        loan = TradeLoan(
            loan_number=await self.generate_loan_number(),
            loan_type=loan_type,
            principal_amount=principal_amount,
            currency=currency,
            status=LoanStatus.DRAFT,
            created_by=created_by,
            **kwargs,
        )
        db.add(loan)
        await db.flush()
        return loan

    async def get_loan_by_id(self, db: AsyncSession, loan_id: int) -> TradeLoan:
        result = await db.execute(select(TradeLoan).where(TradeLoan.id == loan_id))
        loan = result.scalar_one_or_none()
        if not loan:
            raise NotFoundException(f"Loan {loan_id} not found")
        return loan

    async def list_loans(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: Optional[LoanStatus] = None,
    ) -> Tuple[List[TradeLoan], int]:
        query = select(TradeLoan)
        if status:
            query = query.where(TradeLoan.status == status)
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = (
            query.offset((page - 1) * page_size)
            .limit(page_size)
            .order_by(TradeLoan.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all()), total


trade_loan_service = TradeLoanService()
