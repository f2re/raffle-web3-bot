"""FastAPI routes"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database.models import User
from app.api.auth import verify_telegram_auth
from app.services.raffle_service import raffle_service
from app.database.crud import RaffleCRUD, UserCRUD
from app.schemas.pydantic import (
    RaffleResponse,
    RaffleDetailResponse,
    JoinRaffleRequest,
    UserStatsResponse,
    HistoryResponse,
    ParticipantResponse
)


router = APIRouter(prefix="/api/v1", tags=["api"])


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@router.get("/raffles/active", response_model=List[RaffleResponse])
async def get_active_raffles(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(verify_telegram_auth)
):
    """Get all active raffles (3 types)"""
    raffles = await RaffleCRUD.get_all_active(db)

    # Convert to response format with current_participants
    response = []
    for raffle in raffles:
        raffle_dict = {
            "id": raffle.id,
            "type": raffle.type.value,
            "status": raffle.status.value,
            "min_participants": raffle.min_participants,
            "current_participants": len(raffle.participants),
            "entry_fee_ton": raffle.entry_fee_ton,
            "prize_pool_ton": raffle.prize_pool_ton,
            "commission_percent": raffle.commission_percent,
            "created_at": raffle.created_at,
            "waiting_until": raffle.waiting_until,
            "drawn_at": raffle.drawn_at,
            "winner_id": raffle.winner_id,
            "random_org_signature": raffle.random_org_signature,
            "random_org_url": raffle.random_org_url,
        }
        response.append(RaffleResponse(**raffle_dict))

    return response


@router.get("/raffles/{raffle_id}", response_model=RaffleDetailResponse)
async def get_raffle_details(
    raffle_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(verify_telegram_auth)
):
    """Get details of a specific raffle"""
    raffle = await RaffleCRUD.get_by_id(db, raffle_id)
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")

    # Convert to response format
    raffle_dict = {
        "id": raffle.id,
        "type": raffle.type.value,
        "status": raffle.status.value,
        "min_participants": raffle.min_participants,
        "current_participants": len(raffle.participants),
        "entry_fee_ton": raffle.entry_fee_ton,
        "prize_pool_ton": raffle.prize_pool_ton,
        "commission_percent": raffle.commission_percent,
        "created_at": raffle.created_at,
        "waiting_until": raffle.waiting_until,
        "drawn_at": raffle.drawn_at,
        "winner_id": raffle.winner_id,
        "random_org_signature": raffle.random_org_signature,
        "random_org_url": raffle.random_org_url,
        "participants": [
            ParticipantResponse(
                id=p.id,
                raffle_id=p.raffle_id,
                user_id=p.user_id,
                joined_at=p.joined_at,
                transaction_hash=p.transaction_hash,
                is_winner=p.is_winner,
                prize_sent=p.prize_sent
            )
            for p in raffle.participants
        ]
    }

    return RaffleDetailResponse(**raffle_dict)


@router.post("/raffles/{raffle_id}/join", response_model=ParticipantResponse)
async def join_raffle(
    raffle_id: int,
    request: JoinRaffleRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(verify_telegram_auth)
):
    """Join a raffle after payment"""
    try:
        participant = await raffle_service.join_raffle(
            db=db,
            raffle_id=raffle_id,
            user_id=user.id,
            tx_hash=request.tx_hash
        )

        return ParticipantResponse(
            id=participant.id,
            raffle_id=participant.raffle_id,
            user_id=participant.user_id,
            joined_at=participant.joined_at,
            transaction_hash=participant.transaction_hash,
            is_winner=participant.is_winner,
            prize_sent=participant.prize_sent
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/stats", response_model=UserStatsResponse)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(verify_telegram_auth)
):
    """Get user statistics"""
    # Refresh user from DB
    user = await UserCRUD.get_by_id(db, user.id)

    # TODO: Get recent participations
    recent_raffles = []

    from app.schemas.pydantic import UserResponse

    return UserStatsResponse(
        user=UserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            ton_wallet=user.ton_wallet,
            total_participations=user.total_participations,
            total_wins=user.total_wins,
            total_spent_ton=user.total_spent_ton,
            total_won_ton=user.total_won_ton,
            created_at=user.created_at,
            last_active=user.last_active
        ),
        recent_participations=recent_raffles
    )


@router.get("/history", response_model=HistoryResponse)
async def get_raffle_history(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(verify_telegram_auth)
):
    """Get user's raffle history"""
    # TODO: Implement history query
    return HistoryResponse(
        raffles=[],
        total=0
    )
