"""Payout API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime
import csv
import io
from ..core.database import get_db
from ..models.payout import Payout
from ..models.participant import Participant
from ..schemas.payout import Payout as PayoutSchema, PayoutCreate

router = APIRouter(prefix="/payouts", tags=["payouts"])


@router.get("", response_model=List[PayoutSchema])
def list_payouts(
    participant_id: int = None,
    confirmed: bool = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List payouts with optional filtering and pagination."""
    query = db.query(Payout).order_by(desc(Payout.transaction_time))

    if participant_id is not None:
        query = query.filter(Payout.participant_id == participant_id)
    if confirmed is not None:
        query = query.filter(Payout.confirmed == confirmed)

    return query.offset(offset).limit(limit).all()


@router.get("/{payout_id}", response_model=PayoutSchema)
def get_payout(payout_id: int, db: Session = Depends(get_db)):
    """Get a specific payout by ID."""
    payout = db.query(Payout).filter(Payout.id == payout_id).first()
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    return payout


@router.post("", response_model=PayoutSchema)
def create_payout(payout: PayoutCreate, db: Session = Depends(get_db)):
    """Create a new payout record."""
    # Verify participant exists
    participant = db.query(Participant).filter(
        Participant.id == payout.participant_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    # Check for duplicate transaction hash
    existing = db.query(Payout).filter(
        Payout.transaction_hash == payout.transaction_hash
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Transaction already recorded")

    db_payout = Payout(**payout.dict())
    db.add(db_payout)
    db.commit()
    db.refresh(db_payout)
    return db_payout


@router.get("/participant/{participant_id}/summary")
def get_participant_payout_summary(
    participant_id: int,
    db: Session = Depends(get_db)
):
    """Get payout summary for a participant."""
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    payouts = db.query(Payout).filter(
        Payout.participant_id == participant_id
    ).all()

    if not payouts:
        return {
            "participant_id": participant_id,
            "total_payouts": 0,
            "total_amount_ton": 0.0,
            "total_amount_usd": 0.0,
            "first_payout": None,
            "last_payout": None,
        }

    total_ton = sum(p.amount_ton for p in payouts)
    total_usd = sum(p.amount_usd or 0 for p in payouts)
    confirmed_count = len([p for p in payouts if p.confirmed])

    return {
        "participant_id": participant_id,
        "ton_wallet_address": participant.ton_wallet_address,
        "total_payouts": len(payouts),
        "confirmed_payouts": confirmed_count,
        "total_amount_ton": round(total_ton, 4),
        "total_amount_usd": round(total_usd, 2) if total_usd else None,
        "first_payout": min(p.transaction_time for p in payouts).isoformat(),
        "last_payout": max(p.transaction_time for p in payouts).isoformat(),
    }


@router.get("/export/tax-report")
def export_tax_report(
    participant_id: int = None,
    year: int = None,
    db: Session = Depends(get_db)
):
    """Export tax report in CSV format."""
    query = db.query(Payout).order_by(Payout.transaction_time)

    if participant_id is not None:
        query = query.filter(Payout.participant_id == participant_id)

    if year is not None:
        query = query.filter(
            func.extract('year', Payout.transaction_time) == year
        )

    payouts = query.all()

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Date',
        'Transaction Hash',
        'Participant ID',
        'Wallet Address',
        'Amount (TON)',
        'Amount (USD)',
        'From Address',
        'Confirmed',
        'Block Number',
        'Total Requests',
        'Compute Time (seconds)',
    ])

    # Write data
    for payout in payouts:
        participant = db.query(Participant).filter(
            Participant.id == payout.participant_id
        ).first()

        writer.writerow([
            payout.transaction_time.strftime('%Y-%m-%d %H:%M:%S'),
            payout.transaction_hash,
            payout.participant_id,
            payout.to_address,
            payout.amount_ton,
            payout.amount_usd or '',
            payout.from_address,
            'Yes' if payout.confirmed else 'No',
            payout.block_number or '',
            payout.total_requests,
            payout.total_compute_time_seconds,
        ])

    # Prepare response
    output.seek(0)
    filename = f"cocoon_payouts_tax_report_{datetime.utcnow().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
