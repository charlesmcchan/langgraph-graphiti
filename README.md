# langgraph-graphiti

A simple Chainlit chat application that connects directly to OpenAI's GPT models.

## Setup

1. Copy the environment template and add your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
   
2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

## Run

Start the Chainlit server:
```bash
uv run chainlit run main.py
```

The application will open in your browser with a simple chat interface.