"""Participant API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from ..core.database import get_db
from ..models.participant import Participant
from ..models.worker import Worker
from ..models.payout import Payout
from ..schemas.participant import (
    Participant as ParticipantSchema,
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantStats
)

router = APIRouter(prefix="/participants", tags=["participants"])


@router.get("", response_model=List[ParticipantSchema])
def list_participants(
    is_active: bool = None,
    is_operator: bool = None,
    db: Session = Depends(get_db)
):
    """List all participants with optional filtering."""
    query = db.query(Participant)

    if is_active is not None:
        query = query.filter(Participant.is_active == is_active)
    if is_operator is not None:
        query = query.filter(Participant.is_operator == is_operator)

    return query.all()


@router.get("/{participant_id}", response_model=ParticipantStats)
def get_participant(participant_id: int, db: Session = Depends(get_db)):
    """Get a specific participant with statistics."""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    # Calculate statistics
    total_workers = db.query(func.count(Worker.id)).filter(
        Worker.participant_id == participant_id
    ).scalar()

    active_workers = db.query(func.count(Worker.id)).filter(
        Worker.participant_id == participant_id,
        Worker.is_active == True
    ).scalar()

    total_revenue = db.query(func.sum(Payout.amount_ton)).filter(
        Payout.participant_id == participant_id
    ).scalar() or 0.0

    total_payouts = db.query(func.count(Payout.id)).filter(
        Payout.participant_id == participant_id
    ).scalar()

    last_payout = db.query(Payout).filter(
        Payout.participant_id == participant_id
    ).order_by(desc(Payout.transaction_time)).first()

    participant_dict = ParticipantSchema.from_orm(participant).dict()
    participant_dict.update({
        "total_workers": total_workers,
        "active_workers": active_workers,
        "total_revenue_ton": round(total_revenue, 4),
        "total_payouts": total_payouts,
        "last_payout_date": last_payout.transaction_time if last_payout else None,
    })

    return ParticipantStats(**participant_dict)


@router.post("", response_model=ParticipantSchema)
def create_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    """Create a new participant."""
    # Check if wallet address already exists
    existing = db.query(Participant).filter(
        Participant.ton_wallet_address == participant.ton_wallet_address
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Wallet address already registered")

    db_participant = Participant(**participant.dict())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


@router.patch("/{participant_id}", response_model=ParticipantSchema)
def update_participant(
    participant_id: int,
    participant_update: ParticipantUpdate,
    db: Session = Depends(get_db)
):
    """Update a participant."""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    update_data = participant_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(participant, field, value)

    db.commit()
    db.refresh(participant)
    return participant


@router.get("/wallet/{wallet_address}", response_model=ParticipantStats)
def get_participant_by_wallet(wallet_address: str, db: Session = Depends(get_db)):
    """Get participant by TON wallet address."""
    participant = db.query(Participant).filter(
        Participant.ton_wallet_address == wallet_address
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    return get_participant(participant.id, db)
