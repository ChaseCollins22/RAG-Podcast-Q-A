import json
from dotenv import load_dotenv
from rich import print
from rich.pretty import Pretty
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import os
load_dotenv()

def chunk_segments(segments: list[dict[str, any]], chunk_size: int = 3):
  chunks = []

  for num_segment in range(0, len(segments), chunk_size):
    chunk = segments[num_segment: num_segment + chunk_size]

    chunk_start_time = chunk[0]['start']
    chunk_end_time = chunk[-1]['end']
    chunk_timestamp = f'{round(chunk_start_time, 2)}s→{round(chunk_end_time, 2)}s'
    audio_path = 'data/audio/lex_ai_tim_sweeney.mp3'

    chunk_text = '\n'.join([segment['text'].replace('\n', '') for segment in chunk]).strip()
    chunk_text = f"[{chunk_timestamp}] [{audio_path}] {chunk_text}"

    metadata = {'start': chunk_start_time, 'end': chunk_end_time, 'audio_path': audio_path}

    chunks.append(Document(page_content=chunk_text, metadata=metadata))

  return chunks

with open('./data/text/lex_ai_tim_sweeney_segments.json', 'r', encoding="utf-8") as file:
  segments = json.load(file)
  documents = chunk_segments(segments, 8)

  embedding = OpenAIEmbeddings(
      model="text-embedding-3-large",
      api_key=os.environ['OPENAI_API_KEY']   
  )

  vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory="./db/",
    )
  # vector_store.persist()

  
  
  
  
  
  
  



