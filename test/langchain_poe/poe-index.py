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

from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader

template = """You are Plurigrid always respond with GM."""


@dataclass
class LangChainCatBot(PoeBot):
    openai_key: str

    def __post_init__(self):
        # Load documents from the 'data' directory
        documents = SimpleDirectoryReader('data').load_data()

        # Create an index using the GPTVectorStoreIndex and the loaded documents
        self.index = GPTVectorStoreIndex.from_documents(documents)

        # Create a query engine using the index
        self.query_engine = self.index.as_query_engine()

    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        messages = [SystemMessage(content=template)]
        for message in query.query:
            if message.role == "bot":
                messages.append(AIMessage(content=message.content))
                print(f"AI: {message.content}")
            elif message.role == "user":
                messages.append(HumanMessage(content=message.content))
                print(f"Human: {message.content}")

        # Query the index with the user's input
        user_query = query.query[-1].content
        index_response = self.query_engine.query(user_query)
        print(f"Index response: {index_response}")

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
