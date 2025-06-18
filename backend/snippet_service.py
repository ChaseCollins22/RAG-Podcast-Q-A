from fastapi import FastAPI, WebSocket  
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
from io import BytesIO
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import re
import subprocess

from elt.retrieve import retrieve, generate

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

class ChatIn(BaseModel):
    prompt: str

class ChatOut(BaseModel):
    prompt: str
    response: str
    snippets: dict[str, str]

@app.get("/", include_in_schema=False)
async def serve_ui():
    return FileResponse("frontend/index.html")

@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn):
    prompt = body.prompt
    context = retrieve(prompt)
    raw_answer = generate(question=prompt, context=context)

    snippet_map: dict[str, str] = {}
    for doc in context:
        start = round(doc.metadata["start"], 2)
        end   = round(doc.metadata["end"],   2)
        audio_path = doc.metadata["audio_path"]
        timestamp = f"[{start}s→{end}s]"

        url   = f"http://localhost:8000/snippet?path={audio_path}&start={start}&end={end}"
        snippet_map[timestamp] = url
    return ChatOut(prompt=prompt, response=raw_answer, snippets=snippet_map)

@app.websocket("/ws-snippet")
async def ws_snippet(ws: WebSocket):
    """
    Receives JSON { path, start, end } over WS, 
    then launches ffmpeg to trim & encode, piping
    MP3 frames back in small chunks.
    """
    await ws.accept()
    
    msg = await ws.receive_json()
    path, start, end = msg["path"], msg["start"], msg["end"]
    duration = end - start

    cmd = [
      "ffmpeg",
      "-ss",    str(start),
      "-t",     str(duration),
      "-i",     path,
      "-f",     "mp3",
      "-codec:a","libmp3lame",
      "-qscale:a","5",
      "-movflags","frag_keyframe+empty_moov",
      "pipe:1"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    # Read 4kb chunks from the ffmpeg process and stream to the client
    try:
        while True:
            chunk = proc.stdout.read(4096)
            print(chunk)
            if not chunk:
                break
            await ws.send_bytes(chunk)
    finally:
        proc.stdout.close()
        proc.wait()
        await ws.close()