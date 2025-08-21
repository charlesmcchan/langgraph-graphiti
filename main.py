import chainlit as cl
import os
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=True
)

def llm_node(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(MessagesState)
graph.add_node("llm", llm_node)
graph.set_entry_point("llm")
graph.set_finish_point("llm")
agent = graph.compile()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    
    async for chunk in agent.astream(
        {"messages": [HumanMessage(content=message.content)]},
        stream_mode="messages"
    ):
        if chunk[0].content:
            await msg.stream_token(chunk[0].content)
    
    await msg.send()

if __name__ == "__main__":
    main()
