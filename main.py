import chainlit as cl
import os
import asyncio
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

llm = ChatOpenAI(
    model="gpt-5-nano",
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=True
)

mcp_client = MultiServerMCPClient(
    {
        "graphiti": {
            # NOTE: Graphiti MCP server only supports `stdio` and `sse`
            "transport": "sse", 
            "url": "http://localhost:8000/sse"
        }
    }
)

# Global variable to store tools
graphiti_tools = None

async def initialize_mcp_tools():
    """Initialize MCP tools from Graphiti server"""
    global graphiti_tools
    try:
        graphiti_tools = await mcp_client.get_tools()
        print(f"Connected to Graphiti MCP server. Available tools:\n {[tool.name for tool in graphiti_tools]}")
    except Exception as e:
        print(f"Failed to connect to Graphiti MCP server: {e}")
        graphiti_tools = []

async def get_memory(query: str) -> str:
    """Search for relevant memory from Graphiti"""
    if not graphiti_tools:
        return ""
    
    context_parts = []
    
    # Find search tools
    search_nodes_tool = next((t for t in graphiti_tools if t.name == "search_memory_nodes"), None)

    try:
        # Search nodes
        if search_nodes_tool:
            # query: The search query
            # group_ids: Optional list of group IDs to filter results
            # max_nodes: Maximum number of nodes to return (default: 10)
            # center_node_uuid: Optional UUID of a node to center the search around
            # entity: Optional single entity type to filter results (permitted: "Preference", "Procedure")
            nodes_result = await search_nodes_tool.ainvoke({
                "query": query,
                "group_ids": ["claude-code"],
                "max_nodes": 10,
                "center_node_uuid": None,
            })
            if nodes_result:
                print(f"Search node result: {nodes_result}")
                context_parts.append(f"Relevant context: {nodes_result}")
                
    except Exception as e:
        print(f"Error searching memory: {e}")
    
    return "\n".join(context_parts)

async def update_memory(user_message: str, assistant_response: str):
    """Update memory to Graphiti"""
    if not graphiti_tools:
        return

    add_episode_tool = next((t for t in graphiti_tools if t.name == "add_memory"), None)
    if add_episode_tool:
        try:
            
            # NOTE: we opt out of storing the assistant response to reduce memory usage
            # conversation = f"User: {user_message}\nAssistant: {assistant_response}"
            conversation = f"User: {user_message}"
            
            # name (str): Name of the episode
            # episode_body (str): The content of the episode to persist to memory. When source='json', this must be a
            #                    properly escaped JSON string, not a raw Python dictionary. The JSON data will be
            #                    automatically processed to extract entities and relationships.
            # group_id (str, optional): A unique ID for this graph. If not provided, uses the default group_id from CLI
            #                          or a generated one.
            # source (str, optional): Source type, must be one of:
            #                        - 'text': For plain text content (default)
            #                        - 'json': For structured data
            #                        - 'message': For conversation-style content
            # source_description (str, optional): Description of the source
            # uuid (str, optional): Optional UUID for the episode
            await add_episode_tool.ainvoke({
                "name": "Customer Conversation",
                "episode_body": conversation,
                "source": "message",
                "source_description": "chat transcript",
                "group_id": "claude-code",
            })
        except Exception as e:
            print(f"Error storing episode: {e}")

async def llm_node(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1] if messages else None
    
    if last_message and hasattr(last_message, 'content'):
        # Search for relevant context from memory
        memory_context = await get_memory(last_message.content[:200])
        
        # Add memory context if available
        if memory_context.strip():
            context_message = SystemMessage(content=f"Context from previous interactions:\n{memory_context}")
            enhanced_messages = [context_message] + messages
        else:
            enhanced_messages = messages
    else:
        enhanced_messages = messages
    
    # Generate response
    response = llm.invoke(enhanced_messages)
    
    # Store conversation in memory (fire and forget)
    if last_message and hasattr(last_message, 'content'):
        asyncio.create_task(update_memory(last_message.content, response.content))
    
    return {"messages": [response]}

graph = StateGraph(MessagesState)
graph.add_node("llm", llm_node)
graph.set_entry_point("llm")
graph.set_finish_point("llm")
agent = graph.compile()

@cl.on_chat_start
async def start():
    """Initialize MCP connection when chat starts"""
    await initialize_mcp_tools()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    
    try:
        async for chunk in agent.astream(
            {"messages": [HumanMessage(content=message.content)]},
            stream_mode="messages"
        ):
            if chunk[0].content:
                await msg.stream_token(chunk[0].content)
        
        await msg.send()
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        await cl.Message(content=error_msg).send()
        print(f"Error in main handler: {e}")

if __name__ == "__main__":
    main()
