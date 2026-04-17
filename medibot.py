import os
import streamlit as st

from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate

from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from dotenv import load_dotenv
load_dotenv()

DB_FAISS_PATH = "vectorstore/db_faiss"

MEDICAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

/* ── Root & Background ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #080d12 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Sidebar (if any) ── */
[data-testid="stSidebar"] {
    background: #0d1620 !important;
    border-right: 1px solid #1a2a3a !important;
}

/* ── Main container ── */
.main .block-container {
    padding: 2rem 3rem 1rem !important;
    max-width: 860px !important;
}

/* ── Title ── */
h1 {
    font-family: 'Space Mono', monospace !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #00c9a7 !important;
    letter-spacing: -0.5px !important;
    padding-bottom: 0.75rem !important;
    border-bottom: 1px solid #1a2a3a !important;
    margin-bottom: 1.5rem !important;
}

h1::before {
    content: '⚕ ';
    font-size: 1.1rem;
}

/* ── Chat messages wrapper ── */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    margin-bottom: 0.75rem !important;
    padding: 1rem 1.25rem !important;
    border: 1px solid #1a2a3a !important;
    transition: border-color 0.2s ease;
}

[data-testid="stChatMessage"]:hover {
    border-color: #00c9a720 !important;
}

/* User message */
[data-testid="stChatMessage"][data-testid*="user"],
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #0d1a2a !important;
}

/* Assistant message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #0a1520 !important;
    border-left: 2px solid #00c9a7 !important;
}

/* ── Avatar icons ── */
[data-testid="chatAvatarIcon-user"] {
    background: #1a3a5a !important;
    color: #7ec8e3 !important;
    border: 1px solid #1a3a5a !important;
}

[data-testid="chatAvatarIcon-assistant"] {
    background: #00c9a715 !important;
    color: #00c9a7 !important;
    border: 1px solid #00c9a730 !important;
}

/* ── Message text ── */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #c8d8e8 !important;
    font-size: 0.95rem !important;
    line-height: 1.7 !important;
}

[data-testid="stChatMessage"] strong {
    color: #7ec8e3 !important;
}

/* ── Chat input ── */
[data-testid="stChatInputContainer"] {
    background: #0d1620 !important;
    border: 1px solid #1a2a3a !important;
    border-radius: 14px !important;
    padding: 0.25rem 0.5rem !important;
    box-shadow: 0 0 24px #00c9a708 !important;
    margin-top: 1rem !important;
}

[data-testid="stChatInputContainer"]:focus-within {
    border-color: #00c9a750 !important;
    box-shadow: 0 0 0 2px #00c9a715 !important;
}

[data-testid="stChatInputContainer"] textarea {
    background: transparent !important;
    color: #c8d8e8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    caret-color: #00c9a7 !important;
}

[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #3a5a7a !important;
}

/* ── Send button ── */
[data-testid="stChatInputSubmitButton"] button {
    background: #00c9a715 !important;
    border: 1px solid #00c9a740 !important;
    border-radius: 10px !important;
    color: #00c9a7 !important;
    transition: all 0.2s ease !important;
}

[data-testid="stChatInputSubmitButton"] button:hover {
    background: #00c9a730 !important;
    border-color: #00c9a7 !important;
}

/* ── Error / info alerts ── */
[data-testid="stAlert"] {
    background: #1a0d0d !important;
    border: 1px solid #ff4b4b30 !important;
    border-radius: 10px !important;
    color: #ff8080 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080d12; }
::-webkit-scrollbar-thumb { background: #1a2a3a; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #00c9a740; }

/* ── Top status bar ── */
.medical-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: #3a5a7a;
    font-family: 'Space Mono', monospace;
    margin-bottom: 1.5rem;
    padding: 0.5rem 0.75rem;
    background: #0d1620;
    border-radius: 8px;
    border: 1px solid #1a2a3a;
}

.pulse-dot {
    width: 7px;
    height: 7px;
    background: #00c9a7;
    border-radius: 50%;
    animation: pulse 2s infinite;
    display: inline-block;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}
</style>
"""

STATUS_BAR = """
<div class="medical-status">
    <span class="pulse-dot"></span>
    MEDIBOT v1.0 &nbsp;·&nbsp; RAG-FAISS &nbsp;·&nbsp; LLaMA 3.1 via Groq &nbsp;·&nbsp; GALE Encyclopedia
</div>
"""


@st.cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    return db


def set_custom_prompt(custom_prompt_template):
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])
    return prompt


def main():
    st.set_page_config(
        page_title="MediBot",
        page_icon="⚕",
        layout="centered"
    )

    st.markdown(MEDICAL_CSS, unsafe_allow_html=True)
    st.title("MediBot")
    st.markdown(STATUS_BAR, unsafe_allow_html=True)

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])

    prompt = st.chat_input("Ask a medical question...")

    if prompt:
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role': 'user', 'content': prompt})

        try:
            vectorstore = get_vectorstore()
            if vectorstore is None:
                st.error("Failed to load the vector store")

            GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
            GROQ_MODEL_NAME = "llama-3.1-8b-instant"
            llm = ChatGroq(
                model=GROQ_MODEL_NAME,
                temperature=0.5,
                max_tokens=512,
                api_key=GROQ_API_KEY,
            )

            retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
            combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
            rag_chain = create_retrieval_chain(
                vectorstore.as_retriever(search_kwargs={'k': 3}),
                combine_docs_chain
            )

            response = rag_chain.invoke({'input': prompt})
            result = response["answer"]
            st.chat_message('assistant').markdown(result)
            st.session_state.messages.append({'role': 'assistant', 'content': result})

        except Exception as e:
            st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()