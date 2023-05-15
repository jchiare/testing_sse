from quart import Quart, jsonify, make_response
import openai
from quart_cors import cors

import asyncio

app = Quart(__name__)
app = cors(app)

async def ai_response():
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"content": "Do as I say?", "role": "system"}, {"content": "Yes", "role": "user"}],
        temperature=0,
        stream=True,
        request_timeout=5,
    )
    return response

@app.route('/')
@app.route('/api/conversation', methods=["GET", "POST"])
async def hello():
    
    text = await ai_response()
    
    async def eventStream(text):
        async for i in text:
            delta = i["choices"][0]["delta"]
            if "content" in delta:
                yield f'id: {43243}\nevent: message \ndata: {{"sender": "assistant", "text": "{delta["content"]}"}} \n\n'
            else:
                print("Else")
                
    response = await make_response(
        eventStream(text),
        {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Transfer-Encoding": "chunked",
        },
    )
    response.timeout = None
    return response

@app.route("/api/conversation/welcome_message", methods=["GET", "POST"])
async def welcome_message():
    return jsonify ({"welcome_message": "Welcome to the conversation API!"})

if __name__ == '__main__':
    app.run(port=5000)
    
    