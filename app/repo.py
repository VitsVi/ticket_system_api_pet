from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Client, Message, Operator, Ticket, TicketStatus, OperatorStatus


###################### Базовый репозиторий ################
class BaseRepo:
    def __init__(self, session: AsyncSession, model):
        self.session = session
        self.model = model

    async def add(self, obj):
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj):
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj):
        await self.session.delete(obj)
        await self.session.commit()

    async def get_by_id(self, obj_id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalar_one_or_none()

    async def list(self, offset=0, limit=10):
        result = await self.session.execute(
            select(self.model).offset(offset).limit(limit)
        )
        return result.scalars().all()


#################### TicketRepo #########################
class TicketRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Ticket)

    async def get_free_operator(self):
        subq = (
            select(Ticket.operator_id, func.count(Ticket.id).label("ticket_count"))
            .where(Ticket.status == TicketStatus.IN_PROGRESS)
            .group_by(Ticket.operator_id)
        ).subquery()

        result = await self.session.execute(
            select(Operator)
            .where(Operator.status == OperatorStatus.ONLINE)
            .outerjoin(subq, Operator.id == subq.c.operator_id)
            .order_by(subq.c.ticket_count.asc().nullsfirst())
        )
        return result.scalars().first()

    async def get_next_ticket_for_operator(self):
        result = await self.session.execute(
            select(Ticket)
            .where(Ticket.status == TicketStatus.NEW)
            .order_by(Ticket.created_at.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()


######################### ClientRepo #################
class ClientRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Client)


######################### OperatorRepo ################
class OperatorRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Operator)


######################### MessageRepo ##################
class MessageRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)

    async def list_by_ticket(self, ticket_id: int, offset=0, limit=50):
        result = await self.session.execute(
            select(Message)
            .where(Message.ticket_id == ticket_id)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()