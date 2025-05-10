# app.py
import os
from dotenv import load_dotenv
import streamlit as st
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from elt.retrieve import retrieve, generate

load_dotenv()

st.set_page_config(page_title="Podcast QA", page_icon="🎙️", layout="wide")
st.title("📻 Podcast QA Chat")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

if "messages" not in st.session_state:
    st.session_state.messages = []

user_prompt = st.chat_input("Ask anything about the podcast…")
if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    context = retrieve(user_prompt)
    for doc in context:
        start, end, path = doc.metadata['start'], doc.metadata['end'], doc.metadata['audio_path']
        snippet_url = f"http://127.0.0.1:8000/snippet?path={path}&start={start}&end={end}"
    print(context)
    answer = generate(question=user_prompt, context=context)
    #print(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])







