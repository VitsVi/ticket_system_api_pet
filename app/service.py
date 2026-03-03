# app/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Ticket, TicketStatus, Client, Operator, Message
from app.repo import TicketRepo, ClientRepo, OperatorRepo, MessageRepo
from app.cache import update_ticket_count
from datetime import datetime, timedelta

# ===== TICKET SERVICE =====
class TicketService:
    def __init__(self, session: AsyncSession):
        self.repo = TicketRepo(session)

    async def create_ticket(self, ticket: Ticket):
        operator = await self.repo.get_free_operator()
        if operator:
            ticket.operator_id = operator.id
            ticket.status = TicketStatus.IN_PROGRESS
        else:
            ticket.status = TicketStatus.NEW

        ticket = await self.repo.add(ticket)
        await update_ticket_count(ticket.status.value, 1)
        return ticket

    async def get_ticket(self, ticket_id: int):
        return await self.repo.get_by_id(ticket_id)

    async def list_tickets(self, offset=0, limit=10):
        return await self.repo.list(offset, limit)

    async def update_status(self, ticket: Ticket, new_status: TicketStatus):
        allowed_transitions = {
            TicketStatus.NEW: [TicketStatus.IN_PROGRESS],
            TicketStatus.IN_PROGRESS: [TicketStatus.WAITING, TicketStatus.RESOLVED],
            TicketStatus.WAITING: [TicketStatus.RESOLVED, TicketStatus.CLOSED],
            TicketStatus.RESOLVED: [TicketStatus.CLOSED],
            TicketStatus.CLOSED: []
        }
        if new_status not in allowed_transitions[ticket.status]:
            raise ValueError(f"Cannot move from {ticket.status.value} to {new_status.value}")

        old_status = ticket.status
        ticket.status = new_status
        await self.repo.add(ticket)
        await update_ticket_count(old_status.value, -1)
        await update_ticket_count(new_status.value, 1)
        return ticket

    async def close_waiting_tickets(self):
        tickets = await self.repo.list()
        now = datetime.utcnow()
        for ticket in tickets:
            if ticket.status == TicketStatus.WAITING and ticket.updated_at < now - timedelta(hours=24):
                await self.update_status(ticket, TicketStatus.CLOSED)


# ===== CLIENT SERVICE =====
class ClientService:
    def __init__(self, session: AsyncSession):
        self.repo = ClientRepo(session)

    async def create_client(self, client: Client):
        return await self.repo.add(client)

    async def list_clients(self, offset=0, limit=10):
        return await self.repo.list(offset, limit)

    async def get_client(self, client_id: int):
        return await self.repo.get_by_id(client_id)


# ===== OPERATOR SERVICE =====
class OperatorService:
    def __init__(self, session: AsyncSession):
        self.repo = OperatorRepo(session)

    async def create_operator(self, operator: Operator):
        return await self.repo.add(operator)

    async def list_operators(self, offset=0, limit=10):
        return await self.repo.list(offset, limit)

    async def get_operator(self, operator_id: int):
        return await self.repo.get_by_id(operator_id)


# ===== MESSAGE SERVICE =====
class MessageService:
    def __init__(self, session: AsyncSession):
        self.repo = MessageRepo(session)

    async def add_message(self, message: Message):
        return await self.repo.add(message)

    async def list_messages(self, ticket_id: int, offset=0, limit=50):
        return await self.repo.list_by_ticket(ticket_id, offset, limit)