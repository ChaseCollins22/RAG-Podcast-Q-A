import os
import json
import whisper
from dotenv import load_dotenv

load_dotenv()

AUDIO_DIR = "data/audio"
OUTPUT_DIR = "data/text"
os.makedirs(OUTPUT_DIR, exist_ok=True)

model = whisper.load_model("tiny")

for fname in os.listdir(AUDIO_DIR):
    path = os.path.join(AUDIO_DIR, fname)
    base, _ = os.path.splitext(fname)

    if not os.path.isfile(path) or os.path.exists(f'{OUTPUT_DIR}/{base}.json'):
        print(f"\n{path} already exists. Skipping to next file\n")
        continue

    print("Found file:", path)
    print(f"→ transcribing {fname}...\n")
    result = model.transcribe(path)

   
    json_path = os.path.join(OUTPUT_DIR, f"{base}.json")
    with open(json_path, "w") as f_json:
        json.dump(result["segments"], f_json, indent=2)

    print(f"→ segments saved to   {json_path}")
