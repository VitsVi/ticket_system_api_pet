from http import HTTPStatus

from aiohttp import web

from app.db import async_session
from app.models import Client, Message, Operator, Ticket
from app.schemas import (ClientCreateSchema, ClientUpdateSchema,
                         MessageCreateSchema, MessageUpdateSchema,
                         OperatorCreateSchema, OperatorUpdateSchema,
                         TicketCreateSchema, TicketUpdateSchema, TicketReadSchema,
                         ClientReadSchema, OperatorReadSchema)
from app.service import (ClientService, MessageService, OperatorService,
                         TicketService)
from app.utils import validate_request


routes = web.RouteTableDef()


########################## TICKETS ###############################
@routes.get("/tickets")
async def list_tickets(request):
    async with async_session() as session:
        service = TicketService(session)
        tickets = await service.repo.list()
        tickets_data = [TicketReadSchema.from_model(t).model_dump() for t in tickets]
        return web.json_response(tickets_data)


@routes.get("/tickets/{ticket_id}")
async def get_ticket(request):
    ticket_id = int(request.match_info["ticket_id"])
    
    async with async_session() as session:
        service = TicketService(session)
        ticket = await service.repo.get_by_id(ticket_id)
        if ticket is None:
            return web.json_response({"error": "Ticket not found"}, status=HTTPStatus.NOT_FOUND)
        
        ticket_data = TicketReadSchema.from_model(ticket).model_dump()
        return web.json_response(ticket_data)


@routes.post("/tickets")
async def create_ticket(request):
    data = await validate_request(request, TicketCreateSchema)

    async with async_session() as session:
        service = TicketService(session)
        ticket = Ticket(
            subject=data.subject,
            client_id=data.client_id,
            priority=data.priority,
            status=data.status,
            operator_id=data.operator_id
        )
        try:
            ticket = await service.create_ticket(ticket)
        except ValueError as e:
            return web.json_response(
                {"error": str(e)},
                status=HTTPStatus.BAD_REQUEST
            )
        return web.json_response({
            "id": ticket.id,
            "subject": ticket.subject,
            "status": ticket.status.value
        })


@routes.patch("/tickets/{ticket_id}")
async def patch_ticket(request):
    ticket_id = int(request.match_info["ticket_id"])
    data = await validate_request(request, TicketUpdateSchema)

    async with async_session() as session:
        service = TicketService(session)
        ticket = await service.get_ticket(ticket_id)
        if not ticket:
            raise web.HTTPNotFound(text="Ticket not found")

        # преобразуем Pydantic в dict
        update_data = {k: v for k, v in data.dict().items() if v is not None}

        ticket = await service.update_ticket(ticket, update_data)

        return web.json_response({
            "id": ticket.id,
            "subject": ticket.subject,
            "status": ticket.status.value,
            "priority": ticket.priority.value if ticket.priority else None,
            "client_id": ticket.client_id,
            "operator_id": ticket.operator_id
        })


@routes.delete("/tickets/{ticket_id}")
async def delete_ticket(request):
    ticket_id = int(request.match_info["ticket_id"])

    async with async_session() as session:
        service = TicketService(session)
        ticket = await service.get_ticket(ticket_id)
        if not ticket:
            raise web.HTTPNotFound(text="Ticket not found")

        await service.delete_ticket(ticket)
        return web.json_response({"status": "deleted"})


######################## CLIENTS ########################
@routes.post("/clients")
async def create_client(request):
    data = await validate_request(request, ClientCreateSchema)

    async with async_session() as session:
        service = ClientService(session)
        client = Client(name=data.name, email=data.email)
        client = await service.repo.add(client)
        return web.json_response({"id": client.id, "name": client.name, "email": client.email})


@routes.get("/clients")
async def list_clients(request):
    async with async_session() as session:
        service = ClientService(session)
        clients = await service.repo.list()
        clients_data = [ClientReadSchema.from_model(c).model_dump() for c in clients]
        
        return web.json_response(clients_data)


@routes.get("/clients/{client_id}")
async def get_client(request):
    client_id = int(request.match_info["client_id"])
    
    async with async_session() as session:
        service = ClientService(session)
        client = await service.repo.get_by_id(client_id)
        if client is None:
            return web.json_response({"error": "Client not found"}, status=HTTPStatus.NOT_FOUND)
        
        client_data = ClientReadSchema.from_model(client).model_dump()
        return web.json_response(client_data)


@routes.patch("/clients/{client_id}")
async def patch_client(request):
    client_id = int(request.match_info["client_id"])
    data = await validate_request(request, ClientUpdateSchema)

    async with async_session() as session:
        service = ClientService(session)
        client = await service.get_client(client_id)
        if not client:
            raise web.HTTPNotFound(text="Client not found")

        update_data = {k: v for k, v in data.dict().items() if v is not None}
        client = await service.update_client(client, update_data)

        return web.json_response({
            "id": client.id,
            "name": client.name,
            "email": client.email
        })


@routes.delete("/clients/{client_id}")
async def delete_client(request):
    client_id = int(request.match_info["client_id"])

    async with async_session() as session:
        service = ClientService(session)
        client = await service.get_client(client_id)
        if not client:
            raise web.HTTPNotFound(text="Client not found")

        await service.delete_client(client)
        return web.json_response({"status": "deleted"})


######################### OPERATORS ##########################
@routes.get("/operators")
async def list_clients(request):
    async with async_session() as session:
        service = OperatorService(session)
        operators = await service.repo.list()
        operators_data = [OperatorReadSchema.from_model(o).model_dump() for o in operators]
        
        return web.json_response(operators_data)


@routes.get("/operators/{operator_id}")
async def get_operator(request):
    operator_id = int(request.match_info["operator_id"])
    
    async with async_session() as session:
        service = OperatorService(session)
        operator = await service.repo.get_by_id(operator_id)
        if operator is None:
            return web.json_response({"error": "Operator not found"}, status=HTTPStatus.NOT_FOUND)
        
        operator_data = OperatorReadSchema.from_model(operator).model_dump()
        return web.json_response(operator_data)


@routes.post("/operators")
async def create_operator(request):
    data = await validate_request(request, OperatorCreateSchema)

    async with async_session() as session:
        service = OperatorService(session)
        operator = Operator(name=data.name)
        operator = await service.repo.add(operator)
        return web.json_response({"id": operator.id, "name": operator.name, "status": operator.status.value})


@routes.patch("/operators/{operator_id}")
async def patch_operator(request):
    operator_id = int(request.match_info["operator_id"])
    data = await validate_request(request, OperatorUpdateSchema)

    async with async_session() as session:
        service = OperatorService(session)
        operator = await service.get_operator(operator_id)
        if not operator:
            raise web.HTTPNotFound(text="Operator not found")

        update_data = {k: v for k, v in data.dict().items() if v is not None}
        operator = await service.update_operator(operator, update_data)

        return web.json_response({
            "id": operator.id,
            "name": operator.name,
            "status": operator.status
        })


@routes.delete("/operators/{operator_id}")
async def delete_operator(request):
    operator_id = int(request.match_info["operator_id"])

    async with async_session() as session:
        service = OperatorService(session)
        operator = await service.get_operator(operator_id)
        if not operator:
            raise web.HTTPNotFound(text="Operator not found")

        await service.delete_operator(operator)
        return web.json_response({"status": "deleted"})
    

################### MESSAGES ######################3
@routes.post("/messages")
async def create_message(request):
    data = await validate_request(request, MessageCreateSchema)

    async with async_session() as session:
        service = MessageService(session)
        message = Message(content=data.content, ticket_id=data.ticket_id, user_id=data.user_id, user_type=data.user_type)
        message = await service.repo.add(message)
        return web.json_response({"id": message.id, "ticket_id": message.ticket_id})
    

@routes.patch("/messages/{message_id}")
async def patch_message(request):
    message_id = int(request.match_info["message_id"])
    data = await validate_request(request, MessageUpdateSchema)

    async with async_session() as session:
        service = MessageService(session)
        message = await service.repo.get_by_id(message_id)
        if not message:
            raise web.HTTPNotFound(text="Message not found")

        if data.text is not None:
            message = await service.update_message(message, data.text)

        return web.json_response({
            "id": message.id,
            "text": message.text,
            "ticket_id": message.ticket_id,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat()
        })


@routes.delete("/messages/{message_id}")
async def delete_message(request):
    message_id = int(request.match_info["message_id"])

    async with async_session() as session:
        service = MessageService(session)
        message = await service.repo.get_by_id(message_id)
        if not message:
            raise web.HTTPNotFound(text="Message not found")

        await service.delete_message(message)
        return web.json_response({"status": "deleted"})