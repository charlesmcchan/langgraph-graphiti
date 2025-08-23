# langgraph-graphiti

A Chainlit chat application that integrates LangGraph with Graphiti's MCP (Model Context Protocol) server for persistent memory across conversations.

## Features

- **ChainLit Integration**: Leverages ChainLit for chat UI and authentication
- **LangGraph Integration**: Uses LangGraph's StateGraph for conversation flow
- **Graphiti Integration**: Connects to Graphiti MCP server for persistent conversation memory
- **Multi-tenancy**: Each user's conversations are stored separately using unique group IDs

## Prerequisites

- Python 3.12+
- Graphiti MCP server running on `http://localhost:8000/sse`

## Setup

1. Copy the environment template and add your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
   
2. Edit `.env` and add your OpenAI API key and authentication secret:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   CHAINLIT_AUTH_SECRET=your_auth_secret_here
   ```
   
   Generate a secure auth secret using:
   ```bash
   uv run chainlit create-secret
   ```

3. Ensure Graphiti MCP server is running on port 8000 with SSE transport

## Run

Start the Chainlit server:
```bash
uv run chainlit run main.py
```

The application will open in your browser. You'll be prompted to log in with a username and password (any non-empty values work for demo purposes). Each user's conversations and memory are isolated from other users.

## Architecture

### Authentication
- Users must authenticate with a username and password
- Each user gets isolated memory storage using `user-{username}` as the group ID
- Memory and conversation history are completely separated between users

### Memory System
- Uses Graphiti MCP server with SSE transport for persistent memory
- Memory is retrieved using the `search_memory_nodes` tool with user-specific group IDs
- Stores conversation episodes with user messages only (assistant responses excluded for efficiency)
- Context is injected as system messages to provide conversational continuity

## Reference
- [Chainlit](https://chainlit.io)
- [Graphiti](https://github.com/getzep/graphiti)
- [LangChain MCP Adapter](https://github.com/langchain-ai/langchain-mcp-adapters)
