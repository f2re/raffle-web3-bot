"""Pydantic schemas for API"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# User schemas
class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    ton_wallet: Optional[str] = None
    total_participations: int
    total_wins: int
    total_spent_ton: float
    total_won_ton: float
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True


# Raffle schemas
class RaffleBase(BaseModel):
    type: str
    status: str


class RaffleResponse(RaffleBase):
    id: int
    min_participants: int
    current_participants: int = 0
    entry_fee_ton: float
    prize_pool_ton: float
    commission_percent: float
    created_at: datetime
    waiting_until: Optional[datetime] = None
    drawn_at: Optional[datetime] = None
    winner_id: Optional[int] = None
    random_org_signature: Optional[str] = None
    random_org_url: Optional[str] = None

    class Config:
        from_attributes = True


class RaffleDetailResponse(RaffleResponse):
    participants: List["ParticipantResponse"] = []


# Participant schemas
class ParticipantBase(BaseModel):
    raffle_id: int
    user_id: int


class ParticipantResponse(ParticipantBase):
    id: int
    joined_at: datetime
    transaction_hash: Optional[str] = None
    is_winner: bool
    prize_sent: bool

    class Config:
        from_attributes = True


# Join raffle request
class JoinRaffleRequest(BaseModel):
    tx_hash: str = Field(..., description="TON transaction hash")


# Transaction schemas
class TransactionResponse(BaseModel):
    id: int
    user_id: int
    raffle_id: Optional[int] = None
    tx_hash: str
    from_wallet: str
    to_wallet: str
    amount_ton: float
    type: str
    status: str
    created_at: datetime
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Stats schemas
class UserStatsResponse(BaseModel):
    user: UserResponse
    recent_participations: List[RaffleResponse]


class HistoryResponse(BaseModel):
    raffles: List[RaffleResponse]
    total: int


# Rebuild models with forward references
RaffleDetailResponse.model_rebuild()
