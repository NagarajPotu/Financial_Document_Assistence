import requests
import streamlit as st
from extractor import extract_pdf_text, read_excel  # your own functions

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"   # or "gemma2:2b" if you pulled it

# Function to talk to Ollama
def ask_ollama(prompt):
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False   # get full response at once
    }
    response = requests.post(OLLAMA_URL, json=data)
    return response.json()["response"]

# Streamlit UI
st.title("📊 Financial Document Q&A")

if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded = st.file_uploader("Upload a PDF or Excel", type=["pdf", "xlsx", "xls"])

extracted_text = ""
if uploaded:
    if uploaded.name.endswith(".pdf"):
        extracted_text = extract_pdf_text(uploaded)
    else:
        excel_data = read_excel(uploaded)
        extracted_text = str(excel_data)

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a financial question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Include extracted text as context
            full_prompt = f"Context:\n{extracted_text[:2000]}\n\nQuestion:\n{prompt}"
            reply = ask_ollama(full_prompt)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
