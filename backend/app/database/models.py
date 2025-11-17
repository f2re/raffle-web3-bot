"""Database models"""

from datetime import datetime
from typing import List
import enum

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    """Base model class"""
    pass


class RaffleType(str, enum.Enum):
    """Raffle types"""
    EXPRESS = "express"
    STANDARD = "standard"
    PREMIUM = "premium"


class RaffleStatus(str, enum.Enum):
    """Raffle statuses"""
    ACTIVE = "active"  # Collecting participants
    WAITING = "waiting"  # Timer running
    DRAWING = "drawing"  # Drawing in progress
    COMPLETED = "completed"  # Finished
    CANCELLED = "cancelled"  # Cancelled


class TransactionType(str, enum.Enum):
    """Transaction types"""
    ENTRY = "entry"  # Entry fee payment
    PRIZE = "prize"  # Prize payout


class TransactionStatus(str, enum.Enum):
    """Transaction statuses"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    ton_wallet = Column(String(255), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Statistics
    total_participations = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_spent_ton = Column(Float, default=0.0)
    total_won_ton = Column(Float, default=0.0)

    # Relationships
    participations = relationship("Participant", back_populates="user", foreign_keys="Participant.user_id")
    won_raffles = relationship("Raffle", back_populates="winner", foreign_keys="Raffle.winner_id")
    transactions = relationship("Transaction", back_populates="user")


class Raffle(Base):
    """Raffle model"""
    __tablename__ = "raffles"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(RaffleType), nullable=False, index=True)
    status = Column(Enum(RaffleStatus), default=RaffleStatus.ACTIVE, nullable=False, index=True)

    # Parameters
    min_participants = Column(Integer, nullable=False)
    entry_fee_ton = Column(Float, nullable=False)
    prize_pool_ton = Column(Float, nullable=False)
    commission_percent = Column(Float, default=10.0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    waiting_until = Column(DateTime, nullable=True)  # When drawing will start
    drawn_at = Column(DateTime, nullable=True)  # When drawing happened

    # Result
    winner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    random_org_signature = Column(Text, nullable=True)  # Random.org signature
    random_org_url = Column(String(500), nullable=True)  # Verification URL

    # Relationships
    participants = relationship("Participant", back_populates="raffle", cascade="all, delete-orphan")
    winner = relationship("User", back_populates="won_raffles", foreign_keys=[winner_id])
    transactions = relationship("Transaction", back_populates="raffle")

    @property
    def current_participants(self) -> int:
        """Get current number of participants"""
        return len(self.participants)


class Participant(Base):
    """Participant model"""
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    raffle_id = Column(Integer, ForeignKey('raffles.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    transaction_hash = Column(String(255), nullable=True, unique=True)
    is_winner = Column(Boolean, default=False)
    prize_sent = Column(Boolean, default=False)
    prize_tx_hash = Column(String(255), nullable=True)

    # Relationships
    raffle = relationship("Raffle", back_populates="participants")
    user = relationship("User", back_populates="participations", foreign_keys=[user_id])


class Transaction(Base):
    """Transaction model"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    raffle_id = Column(Integer, ForeignKey('raffles.id'), nullable=True, index=True)

    tx_hash = Column(String(255), unique=True, nullable=False, index=True)
    from_wallet = Column(String(255), nullable=False)
    to_wallet = Column(String(255), nullable=False)
    amount_ton = Column(Float, nullable=False)

    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    confirmed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    raffle = relationship("Raffle", back_populates="transactions")
