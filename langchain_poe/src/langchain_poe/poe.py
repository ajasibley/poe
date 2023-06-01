import asyncio
from dataclasses import dataclass
from typing import AsyncIterable

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from sse_starlette.sse import ServerSentEvent

from fastapi_poe import PoeBot
from fastapi_poe.types import QueryRequest

from langchain.tools import BraveSearch

api_key = "BSA6ybVNqM7FV8fgqwCGGjMiEWkMieA"

template = """You are Plurigrid, respond with GM!"""

tool = BraveSearch.from_api_key(api_key=api_key, search_kwargs={"count": 3})

def truncate_messages(messages, max_length=4000):
    total_length = sum(len(message.content) for message in messages)
    while total_length > max_length:
        removed_message = messages.pop(0)
        total_length -= len(removed_message.content)
    return messages

@dataclass
class LangChainCatBot(PoeBot):
    openai_key: str

    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        messages = [SystemMessage(content=template)]
        for message in query.query:
            if message.role == "bot":
                messages.append(AIMessage(content=message.content))
            elif message.role == "user":    
                messages.append(HumanMessage(content=message.content))
            
            messages = truncate_messages(messages)

            await asyncio.sleep(.01)
            
        handler = AsyncIteratorCallbackHandler()
        chat = ChatOpenAI(
            openai_api_key=self.openai_key,
            streaming=True,
            callback_manager=AsyncCallbackManager([handler]),
            temperature=0,
        )

        print([messages])

        messages.append(HumanMessage(content=tool.run(message.content)))
        print([messages])
        asyncio.create_task(chat.agenerate([messages]))
        async for token in handler.aiter():
            yield self.text_event(token)
