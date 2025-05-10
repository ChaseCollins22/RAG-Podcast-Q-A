from fastapi import FastAPI, HTTPException
from pydub import AudioSegment
from io import BytesIO
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/snippet")
def get_snippet(path: str, start: float, end: float):
  audio = AudioSegment.from_file(file=path, format="mp3", start_second=start, duration=(end-start))
  buffer = BytesIO()
  print(len(audio))
  audio.export(buffer, format="mp3")
  buffer.seek(0)

  return StreamingResponse(buffer, media_type="mp3")
