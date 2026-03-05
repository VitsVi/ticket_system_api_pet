from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from app.models import OperatorStatus, TicketPriority, TicketStatus, UserType


################# Messages #######################
class MessageCreateSchema(BaseModel):
    content: str
    ticket_id: int
    user_id: int
    user_type: UserType


class MessageUpdateSchema(BaseModel):
    content: Optional[str] = None


class MessageSchema(BaseModel):
    id: int
    content: str
    ticket_id: int
    user_id: int
    user_type: UserType
    created_at: str
    updated_at: Optional[str] = None

    @classmethod
    def from_model(cls, message):
        return cls(
            id=message.id,
            content=message.content,
            ticket_id=message.ticket_id,
            user_id=message.user_id,
            user_type=message.user_type,
            created_at=message.created_at.isoformat(),
            updated_at=message.updated_at.isoformat() if message.updated_at else None
        )


######################## Tickets ########################
class TicketCreateSchema(BaseModel):
    subject: str = Field(..., max_length=255)
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM
    status: Optional[TicketStatus] = TicketStatus.NEW
    client_id: int = Field(...)
    operator_id: Optional[int] = None


class TicketUpdateSchema(BaseModel):
    subject: Optional[str] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    client_id: Optional[int] = None
    operator_id: Optional[int] = None


class TicketReadSchema(BaseModel):
    id: int
    subject: str
    status: TicketStatus
    priority: Optional[TicketPriority] = None
    client_id: Optional[int] = None
    operator_id: Optional[int] = None
    messages: List[MessageSchema] = []
    created_at: str  # меняем на str
    updated_at: Optional[str] = None

    @classmethod
    def from_model(cls, ticket):
        return cls(
            id=ticket.id,
            subject=ticket.subject,
            status=ticket.status.value,
            priority=ticket.priority.value if ticket.priority else None,
            client_id=ticket.client_id,
            operator_id=ticket.operator_id,
            messages=[MessageSchema.from_model(m) for m in getattr(ticket, "messages", [])],
            created_at=ticket.created_at.isoformat(),  # конвертируем в строку
            updated_at=ticket.updated_at.isoformat() if ticket.updated_at else None
        )


################### Clients ########################
class ClientCreateSchema(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr


class ClientUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class TicketForClientSchema(BaseModel):
    id: int
    subject: str
    status: str
    priority: Optional[str] = None
    operator_id: Optional[int] = None

    @classmethod
    def from_model(cls, ticket):
        return cls(
            id=ticket.id,
            subject=ticket.subject,
            status=ticket.status.value,
            priority=ticket.priority.value if ticket.priority else None,
            operator_id=ticket.operator_id
        )


class ClientReadSchema(BaseModel):
    id: int
    name: str
    email: str
    tickets: List[TicketForClientSchema] = []

    @classmethod
    def from_model(cls, client):
        return cls(
            id=client.id,
            name=client.name,
            email=client.email,
            tickets=[TicketForClientSchema.from_model(t) for t in getattr(client, "tickets", [])]
        )


######################### Operators #########################
class OperatorCreateSchema(BaseModel):
    name: str = Field(..., max_length=100)
    status: Optional[OperatorStatus] = OperatorStatus.OFFLINE


class OperatorUpdateSchema(BaseModel):
    name: Optional[str] = None
    status: Optional[OperatorStatus] = None


class TicketForOperatorSchema(BaseModel):
    id: int
    subject: str
    status: str
    priority: Optional[str] = None
    client_id: Optional[int] = None

    @classmethod
    def from_model(cls, ticket):
        return cls(
            id=ticket.id,
            subject=ticket.subject,
            status=ticket.status.value,
            priority=ticket.priority.value if ticket.priority else None,
            client_id=ticket.client_id
        )


class OperatorReadSchema(BaseModel):
    id: int
    name: str
    status: str
    tickets: List[TicketForOperatorSchema] = []

    @classmethod
    def from_model(cls, operator):
        return cls(
            id=operator.id,
            name=operator.name,
            status=operator.status.value,
            tickets=[TicketForOperatorSchema.from_model(t) for t in getattr(operator, "tickets", [])]
        )
