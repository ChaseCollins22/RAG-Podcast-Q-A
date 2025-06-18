import json
from dotenv import load_dotenv
from rich import print
from rich.pretty import Pretty
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
load_dotenv()

def chunk_segments(segments: list[dict[str, any]], audio_path: str, chunk_size: int = 3) -> list[Document]:
  chunks = []

  for num_segment in range(0, len(segments), chunk_size):
    chunk = segments[num_segment: num_segment + chunk_size]

    chunk_start_time = chunk[0]['start']
    chunk_end_time = chunk[-1]['end']
    chunk_timestamp = f'{round(chunk_start_time, 2)}s→{round(chunk_end_time, 2)}s'
  
    chunk_text = '\n'.join([segment['text'].replace('\n', '') for segment in chunk]).strip()
    chunk_text = f"[{chunk_timestamp}] [{audio_path}] {chunk_text}"

    metadata = {'start': chunk_start_time, 'end': chunk_end_time, 'audio_path': audio_path}

    chunks.append(Document(page_content=chunk_text, metadata=metadata))

  return chunks


for fname in os.listdir("data/text"):
    file_path = os.path.join('data/text', fname)
    if not os.path.isfile(file_path):
        continue
    file_name, _ = os.path.splitext(fname)
    print("Found file:", file_path)

    with open(file_path, 'r', encoding="utf-8") as json_file:
      segments = json.load(json_file)

    documents = chunk_segments(segments, f'data/audio/{file_name}.mp3', 8)
    
    embedding = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=os.environ['OPENAI_API_KEY']   
    )

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory="./db/",
    )


