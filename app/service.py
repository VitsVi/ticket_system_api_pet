from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import update_ticket_count
from app.models import Client, Message, Operator, Ticket, TicketStatus
from app.repo import ClientRepo, MessageRepo, OperatorRepo, TicketRepo


##################### TICKET SERVICE ################
class TicketService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TicketRepo(session)

    async def create_ticket(self, ticket: Ticket):
        result = await self.session.execute(
            select(Client).where(Client.id == ticket.client_id)
        )
        client = result.scalar_one_or_none()

        if not client:
            raise ValueError("Client not found")

        operator = await self.repo.get_free_operator()

        if operator:
            ticket.operator_id = operator.id
            ticket.status = TicketStatus.IN_PROGRESS
        else:
            ticket.status = TicketStatus.NEW

        ticket = await self.repo.add(ticket)
        await update_ticket_count(ticket.status.value, 1)
        return ticket

    async def update_ticket(self, ticket: Ticket, data: dict):
        """Обновление тикета"""
        old_status = ticket.status
        if data.get("status") and old_status != data["status"]:
            ticket = await self.update_status(ticket, data['status'])

        for field, value in data.items():
            if value is not None:
                setattr(ticket, field, value)

        ticket = await self.repo.update(ticket)
        return ticket

    async def delete_ticket(self, ticket: Ticket):
        await self.repo.delete(ticket)
        if ticket.status:
            await update_ticket_count(ticket.status.value, -1)

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
        if new_status == TicketStatus.CLOSED and ticket.operator_id:
            next_ticket = await self.repo.get_next_ticket_for_operator()
            if next_ticket:
                next_ticket.operator_id = ticket.operator_id
                next_ticket.status = TicketStatus.IN_PROGRESS
                await self.repo.update(next_ticket)

        return ticket

    async def close_waiting_tickets(self):
        tickets = await self.repo.list()
        now = datetime.now(timezone.utc)
        for ticket in tickets:
            if ticket.status == TicketStatus.WAITING and ticket.updated_at < now - timedelta(hours=24):
                await self.update_status(ticket, TicketStatus.CLOSED)


###################### CLIENT SERVICE #######################
class ClientService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ClientRepo(session)

    async def create_client(self, client: Client):
        return await self.repo.add(client)

    async def list_clients(self, offset=0, limit=10):
        return await self.repo.list(offset, limit)

    async def get_client(self, client_id: int):
        return await self.repo.get_by_id(client_id)

    async def update_client(self, client: Client, data: dict):
        for field, value in data.items():
            if value is not None:
                setattr(client, field, value)
        return await self.repo.update(client)

    async def delete_client(self, client: Client):
        await self.repo.delete(client)


############################ OPERATOR SERVICE #########################
class OperatorService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = OperatorRepo(session)

    async def create_operator(self, operator: Operator):
        return await self.repo.add(operator)

    async def list_operators(self, offset=0, limit=10):
        return await self.repo.list(offset, limit)

    async def get_operator(self, operator_id: int):
        return await self.repo.get_by_id(operator_id)

    async def update_operator(self, operator: Operator, data: dict):
        for field, value in data.items():
            if value is not None:
                setattr(operator, field, value)
        return await self.repo.update(operator)

    async def delete_operator(self, operator: Operator):
        await self.repo.delete(operator)


############################ MESSAGE SERVICE ##############################
class MessageService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = MessageRepo(session)

    async def create_message(self, message: Message):
        return await self.repo.add(message)

    async def list_messages(self, ticket_id: int, offset=0, limit=50):
        return await self.repo.list_by_ticket(ticket_id, offset, limit)

    async def get_message(self, message_id: int):
        return await self.repo.get_by_id(message_id)

    async def update_message(self, message: Message, new_text: str):
        message.text = new_text
        return await self.repo.update(message)

    async def delete_message(self, message: Message):
        await self.repo.delete(message)