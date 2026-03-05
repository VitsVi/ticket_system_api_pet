from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String, Text, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )


class OperatorStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


class TicketStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Client(Base, TimestampMixin):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    tickets = relationship("Ticket", back_populates="client", lazy="selectin")


class Operator(Base, TimestampMixin):
    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    status: Mapped[OperatorStatus] = mapped_column(
        SQLEnum(OperatorStatus),
        default=OperatorStatus.OFFLINE,
    )

    tickets = relationship("Ticket", back_populates="operator", lazy="selectin")


class Ticket(Base, TimestampMixin):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(String(255))
    priority: Mapped[TicketPriority] = mapped_column(
        SQLEnum(TicketPriority),
        default=TicketPriority.MEDIUM
    )

    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(TicketStatus),
        default=TicketStatus.NEW,
    )

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    operator_id: Mapped[int | None] = mapped_column(
        ForeignKey("operators.id"),
        nullable=True
    )

    client = relationship("Client", back_populates="tickets")
    operator = relationship("Operator", back_populates="tickets")
    messages = relationship(
        "Message",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class UserType(str, Enum):
    CLIENT = "client"
    OPERATOR = "operator"


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id")
    )
    user_id: Mapped[int] = mapped_column(Integer)
    user_type: Mapped[UserType] = mapped_column(SQLEnum(UserType))

    ticket = relationship("Ticket", back_populates="messages", lazy="selectin")