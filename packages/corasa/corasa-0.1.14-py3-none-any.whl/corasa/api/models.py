from typing import Optional

from pydantic import BaseModel


class ConversationData(BaseModel):
    bot_id: str
    user_id: Optional[str] = None
    authenticated_user_id: Optional[str] = None
    webhook_url: Optional[str] = None
    conversation_id: Optional[str] = None
    context_data: Optional[dict] = None


class EventData(BaseModel):
    event_type: str
    event_data: dict


class MessageData(BaseModel):
    message: str


# We have to use the below hack because "from" is a keyword in python
MessageData.__annotations__["from"] = str
