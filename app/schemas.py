import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import RecordType, UserRole


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    role: UserRole


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    role: UserRole | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: dt.datetime


class FinancialRecordBase(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    type: RecordType
    category: str = Field(min_length=2, max_length=60)
    date: dt.date
    notes: str | None = Field(default=None, max_length=500)


class FinancialRecordCreate(FinancialRecordBase):
    owner_id: int | None = Field(default=None, ge=1)


class FinancialRecordUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    type: RecordType | None = None
    category: str | None = Field(default=None, min_length=2, max_length=60)
    date: dt.date | None = None
    notes: str | None = Field(default=None, max_length=500)


class FinancialRecordRead(FinancialRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: dt.datetime
    updated_at: dt.datetime


class SummaryOverview(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    current_balance: Decimal
    total_records: int


class CategoryBreakdownItem(BaseModel):
    category: str
    total: Decimal
    type: RecordType


class MonthlyTotalItem(BaseModel):
    month: str
    total_income: Decimal
    total_expenses: Decimal
    net: Decimal


class RecentActivityItem(BaseModel):
    id: int
    amount: Decimal
    type: RecordType
    category: str
    date: dt.date
    owner_id: int
