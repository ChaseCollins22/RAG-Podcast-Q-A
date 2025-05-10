import whisper, json

model = whisper.load_model("tiny")
audio_path = "data/audio/lex_ai_tim_sweeney.mp3"

result = model.transcribe(audio_path, verbose=False)

segments = result["segments"]

with open("data/text/lex_ai_tim_sweeney_segments.json", "w") as f:
    json.dump(segments, f, indent=2)
