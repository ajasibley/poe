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

template = """You are Plurigrid always respond with GM."""


@dataclass
class LangChainCatBot(PoeBot):
    openai_key: str

    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        messages = [SystemMessage(content=template)]
        for message in query.query:
            if message.role == "bot":
                messages.append(AIMessage(content=message.content))
                print(f"AI: {message.content}")
            elif message.role == "user":
                messages.append(HumanMessage(content=message.content))
                print(f"Human: {message.content}")
        handler = AsyncIteratorCallbackHandler()
        chat = ChatOpenAI(
            openai_api_key=self.openai_key,
            streaming=True,
            callback_manager=AsyncCallbackManager([handler]),
            temperature=0,
        )
        asyncio.create_task(chat.agenerate([messages]))
        async for token in handler.aiter():
            yield self.text_event(token)
