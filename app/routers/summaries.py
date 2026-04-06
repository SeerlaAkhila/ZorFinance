from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user, require_role
from app.models import FinancialRecord, RecordType, User, UserRole
from app.schemas import (
    CategoryBreakdownItem,
    MonthlyTotalItem,
    RecentActivityItem,
    SummaryOverview,
)

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.get(
    "/overview",
    response_model=SummaryOverview,
    dependencies=[Depends(require_role({UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN}))],
)
def get_overview(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    income_expr = case((FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount), else_=0)
    expense_expr = case((FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount), else_=0)

    totals = db.execute(
        select(
            func.coalesce(func.sum(income_expr), 0),
            func.coalesce(func.sum(expense_expr), 0),
            func.count(FinancialRecord.id),
        )
    ).one()

    total_income = Decimal(str(totals[0]))
    total_expenses = Decimal(str(totals[1]))

    return SummaryOverview(
        total_income=total_income,
        total_expenses=total_expenses,
        current_balance=total_income - total_expenses,
        total_records=int(totals[2]),
    )


@router.get(
    "/category-breakdown",
    response_model=list[CategoryBreakdownItem],
    dependencies=[Depends(require_role({UserRole.ANALYST, UserRole.ADMIN}))],
)
def category_breakdown(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rows = db.execute(
        select(
            FinancialRecord.category,
            FinancialRecord.type,
            func.coalesce(func.sum(FinancialRecord.amount), 0).label("total"),
        )
        .group_by(FinancialRecord.category, FinancialRecord.type)
        .order_by(func.sum(FinancialRecord.amount).desc())
    ).all()

    return [
        CategoryBreakdownItem(category=row[0], type=row[1], total=Decimal(str(row[2])))
        for row in rows
    ]


@router.get(
    "/monthly-totals",
    response_model=list[MonthlyTotalItem],
    dependencies=[Depends(require_role({UserRole.ANALYST, UserRole.ADMIN}))],
)
def monthly_totals(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    month_col = func.strftime("%Y-%m", FinancialRecord.date)

    income_expr = case((FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount), else_=0)
    expense_expr = case((FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount), else_=0)

    rows = db.execute(
        select(
            month_col.label("month"),
            func.coalesce(func.sum(income_expr), 0).label("income"),
            func.coalesce(func.sum(expense_expr), 0).label("expense"),
        )
        .group_by(month_col)
        .order_by(month_col.desc())
    ).all()

    result: list[MonthlyTotalItem] = []
    for month, income, expense in rows:
        income_dec = Decimal(str(income))
        expense_dec = Decimal(str(expense))
        result.append(
            MonthlyTotalItem(
                month=month,
                total_income=income_dec,
                total_expenses=expense_dec,
                net=income_dec - expense_dec,
            )
        )
    return result


@router.get(
    "/recent-activity",
    response_model=list[RecentActivityItem],
    dependencies=[Depends(require_role({UserRole.ANALYST, UserRole.ADMIN}))],
)
def recent_activity(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=100),
):
    rows = db.scalars(
        select(FinancialRecord)
        .order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
        .limit(limit)
    ).all()

    return [
        RecentActivityItem(
            id=row.id,
            amount=row.amount,
            type=row.type,
            category=row.category,
            date=row.date,
            owner_id=row.owner_id,
        )
        for row in rows
    ]
