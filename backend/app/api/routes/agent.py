import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.app.agent.agent import OpenDomainAgent
from backend.app.api.deps import CurrentUser, DbSession

router = APIRouter(prefix="/agent", tags=["agent"])


class AgentMessage(BaseModel):
    message: str
    conversation_id: str | None = None


class AgentResponse(BaseModel):
    response: str
    conversation_id: str
    actions_taken: list[dict] | None = None


@router.post("/chat", response_model=AgentResponse)
async def chat(data: AgentMessage, db: DbSession, current_user: CurrentUser):
    agent = OpenDomainAgent(db=db, user=current_user)
    result = await agent.process_message(data.message, data.conversation_id)
    return result


@router.post("/chat/stream")
async def chat_stream(data: AgentMessage, db: DbSession, current_user: CurrentUser):
    async def event_generator():
        yield f"event: thinking\ndata: {json.dumps({'status': 'processing'})}\n\n"

        agent = OpenDomainAgent(db=db, user=current_user)
        result = await agent.process_message(data.message, data.conversation_id)

        if result.get("actions_taken"):
            for action in result["actions_taken"]:
                yield f"event: action\ndata: {json.dumps(action)}\n\n"

        yield f"event: message\ndata: {json.dumps({'response': result['response'], 'conversation_id': result['conversation_id']})}\n\n"
        yield f"event: done\ndata: {json.dumps({'conversation_id': result['conversation_id']})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
