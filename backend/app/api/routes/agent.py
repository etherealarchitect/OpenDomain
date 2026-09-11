from fastapi import APIRouter
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
