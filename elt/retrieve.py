from xml.dom.minidom import Document
from dotenv import load_dotenv
from langchain import hub
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import os
load_dotenv()

embedding = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=os.environ['OPENAI_API_KEY']
)
vector_store = Chroma(persist_directory="./db/", embedding_function=embedding)

llm = ChatOpenAI(
  model="gpt-3.5-turbo",
  api_key=os.environ['OPENAI_API_KEY']
)

custom_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
         "You are a RAG assistant. The user-provided context is split into labeled chunks:\n"
        "  [start→end] chunk text\n\n"
        "For _every_ sentence in your answer that draws on a chunk, you **must** end that sentence with the exact `[start→end]` label. "
        "Whenever you use or paraphrase information from a chunk, end the very same sentence with that chunk’s timestamp `[start→end]`.  "
        "Do not drop or move any timestamps.  Your entire answer must be **no more than 12 sentences**.  "
        "If the question cannot be answered from the context, reply “I don’t know.”"
    ),
    HumanMessagePromptTemplate.from_template(
        "Context:\n\n{context}\n\nQuestion:\n\n{question}\n\nAnswer:"
    ),
])

def retrieve(question: str):
  results = vector_store.similarity_search(question, k=5)
  return results

def generate(question: str, context: list[Document]):
   messages = custom_prompt.format_messages(question=question, context=context)
   response = llm.invoke(messages)
   return response.content

