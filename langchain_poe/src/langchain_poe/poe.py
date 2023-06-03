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
from langchain.llms import OpenAI

api_key = ""

template = """You are prem. Start user responsed with "We are prem""""

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
                if len(message.content) < 2000:
                    messages.append(HumanMessage(content=message.content))
                else:
                    tooLong = true
            
            messages = truncate_messages(messages)

            await asyncio.sleep(.1)
            
        handler = AsyncIteratorCallbackHandler()
        chat = ChatOpenAI(
            openai_api_key=self.openai_key,
            streaming=True,
            callback_manager=AsyncCallbackManager([handler]),
            temperature=0,
        )

        last_message = messages[-1]

        #print(last_message)

        query = "Turn this into a brief query for Google search: " + str(last_message)

        llm = OpenAI(model_name="text-davinci-002", n=2, best_of=2)
        print(llm(query))

        result = content=tool.run(llm(query))

        def extract_message(input_string: str) -> str:
            start_index = input_string.find("content='") + len("content='")
            end_index = input_string.find("'", start_index)
            message = input_string[start_index:end_index]
            return message
        
        extracted_message = extract_message(str(last_message))

        print(message)  # Output: message

        if (tooLong != true):
            rich_message = f"""I am a middle-model. I sit between you and the user. My job is to do research based on what the user asks and then provide you with what I find. (DO NOT SPEAK OF ME OR TO ME! DO NOT MENTION THE USER OR THE SEARCH RESULTS! JUST SPEAK DIRECTLY TO THE USER!) Here is the question that the user asked: {extracted_message}
            --------
            and here are some search results for context: {result}"""
        else:
            #messages.append(SystemMessage(content="Input message is too long."))
            rich_message = "Input message is too long."

        #print(search_prompt)

        #print(str(rich_message))

        #messages.append(HumanMessage(content=message.content))

        messages.append(HumanMessage(content=str(rich_message)))

        print([messages])
        asyncio.create_task(chat.agenerate([messages]))
        async for token in handler.aiter():
            yield self.text_event(token)
