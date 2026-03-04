from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from app.models import TicketStatus, TicketPriority, OperatorStatus

# ===== Tickets =====
class TicketCreateSchema(BaseModel):
    subject: str = Field(..., max_length=255)
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM
    status: Optional[TicketStatus] = TicketStatus.NEW
    client_id: int = None
    operator_id: Optional[int] = None


# ===== Clients =====
class ClientCreateSchema(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr


# ===== Operators =====
class OperatorCreateSchema(BaseModel):
    name: str = Field(..., max_length=100)
    status: Optional[OperatorStatus] = OperatorStatus.OFFLINE


# ===== Messages =====
class MessageCreateSchema(BaseModel):
    content: str
    ticket_id: int
    sender_type: str = Field(..., max_length=20)