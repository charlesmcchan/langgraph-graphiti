# langgraph-graphiti

A Chainlit chat application that integrates LangGraph with Graphiti's MCP (Model Context Protocol) server for persistent memory across conversations.

## Features

- **LangGraph Integration**: Uses LangGraph's StateGraph for conversation flow
- **Graphiti Memory**: Connects to Graphiti MCP server for persistent conversation memory
- **OpenAI GPT-5 Nano**: Powered by OpenAI's latest GPT-5 nano model
- **Real-time Streaming**: Supports streaming responses through Chainlit interface
- **Memory Context**: Automatically retrieves relevant context from previous conversations

## Prerequisites

- Python 3.12+
- Graphiti MCP server running on `http://localhost:8000/sse`

## Setup

1. Copy the environment template and add your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
   
2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Ensure Graphiti MCP server is running on port 8000 with SSE transport

## Run

Start the Chainlit server:
```bash
uv run chainlit run main.py
```

The application will open in your browser with a chat interface that maintains memory across sessions.
