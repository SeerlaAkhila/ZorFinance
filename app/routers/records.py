from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user, require_role
from app.models import FinancialRecord, RecordType, User, UserRole
from app.schemas import FinancialRecordCreate, FinancialRecordRead, FinancialRecordUpdate

router = APIRouter(prefix="/records", tags=["records"])


@router.post(
    "",
    response_model=FinancialRecordRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role({UserRole.ADMIN}))],
)
def create_record(
    payload: FinancialRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owner_id = payload.owner_id or current_user.id
    owner = db.get(User, owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user does not exist")

    record = FinancialRecord(
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes,
        owner_id=owner_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get(
    "",
    response_model=list[FinancialRecordRead],
    dependencies=[Depends(require_role({UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN}))],
)
def list_records(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    type: RecordType | None = Query(default=None),
    category: str | None = Query(default=None, min_length=2, max_length=60),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date cannot be after end_date")

    stmt: Select[tuple[FinancialRecord]] = select(FinancialRecord)

    if type:
        stmt = stmt.where(FinancialRecord.type == type)
    if category:
        stmt = stmt.where(FinancialRecord.category == category)
    if start_date:
        stmt = stmt.where(FinancialRecord.date >= start_date)
    if end_date:
        stmt = stmt.where(FinancialRecord.date <= end_date)

    stmt = stmt.order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc()).offset(skip).limit(limit)

    return list(db.scalars(stmt).all())


@router.get(
    "/{record_id}",
    response_model=FinancialRecordRead,
    dependencies=[Depends(require_role({UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN}))],
)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    record = db.get(FinancialRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.put(
    "/{record_id}",
    response_model=FinancialRecordRead,
    dependencies=[Depends(require_role({UserRole.ADMIN}))],
)
def update_record(
    record_id: int,
    payload: FinancialRecordUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    record = db.get(FinancialRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role({UserRole.ADMIN}))],
)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    record = db.get(FinancialRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    db.delete(record)
    db.commit()
