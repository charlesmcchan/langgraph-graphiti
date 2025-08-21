import chainlit as cl
import openai
import os

@cl.on_message
async def main(message: cl.Message):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message.content}],
        stream=True
    )
    
    msg = cl.Message(content="")
    
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            await msg.stream_token(chunk.choices[0].delta.content)
    
    await msg.send()

if __name__ == "__main__":
    main()
