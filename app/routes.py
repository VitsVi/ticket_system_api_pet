from aiohttp import web
from app.db import async_session
from app.service import TicketService, ClientService, OperatorService, MessageService
from app.models import Ticket, Client, Operator, Message

routes = web.RouteTableDef()

# ===== TICKETS =====
@routes.get("/tickets")
async def list_tickets(request):
    async with async_session() as session:
        service = TicketService(session)
        tickets = await service.repo.list()
        return web.json_response([{"id": t.id, "subject": t.subject, "status": t.status.value} for t in tickets])

@routes.post("/tickets")
async def create_ticket(request):
    data = await request.json()
    async with async_session() as session:
        service = TicketService(session)
        ticket = Ticket(subject=data["subject"], client_id=data.get("client_id"))
        ticket = await service.create_ticket(ticket)
        return web.json_response({"id": ticket.id, "subject": ticket.subject, "status": ticket.status.value})

# ===== CLIENTS =====
@routes.post("/clients")
async def create_client(request):
    data = await request.json()
    async with async_session() as session:
        service = ClientService(session)
        client = Client(name=data["name"], email=data["email"])
        client = await service.repo.add(client)
        return web.json_response({"id": client.id, "name": client.name, "email": client.email})

@routes.get("/clients")
async def list_clients(request):
    async with async_session() as session:
        service = ClientService(session)
        clients = await service.repo.list()
        return web.json_response([{"id": c.id, "name": c.name, "email": c.email} for c in clients])

# ===== OPERATORS =====
@routes.post("/operators")
async def create_operator(request):
    data = await request.json()
    async with async_session() as session:
        service = OperatorService(session)
        operator = Operator(name=data["name"])
        operator = await service.repo.add(operator)
        return web.json_response({"id": operator.id, "name": operator.name, "status": operator.status.value})

# ===== MESSAGES =====
@routes.post("/messages")
async def create_message(request):
    data = await request.json()
    async with async_session() as session:
        service = MessageService(session)
        message = Message(content=data["content"], ticket_id=data["ticket_id"], sender_type=data["sender_type"])
        message = await service.repo.add(message)
        return web.json_response({"id": message.id, "ticket_id": message.ticket_id})