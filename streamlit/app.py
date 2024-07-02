import streamlit as st
import os
import time
from clova_api import clova_studio_llm
from image_loader import load_image
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from app_utils import handle_uploaded_file, process_documents, initialize_retrievers, clear_session_state, handle_user_input
from get_jobs import get_job_postings  # get_jobs.py에서 함수 가져오기
from job import get_job_summary
st.set_page_config(
    page_title="🏴‍☠️ 루피봇 (with HyperClova X)",
    page_icon="🏴‍☠️",
    layout="wide"
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("🏴‍☠️ 취업지원 비서 해적왕 루피")
st.warning("⚠️ Note: There is an 8-second delay before the model generates a response due to HyperClova API call latency.")

user_avatar_base64 = load_image("../streamlit/image/kdb.png")
assistant_avatar_base64 = load_image("../streamlit/image/luffy.png")

msgs = StreamlitChatMessageHistory(key="chat_messages")

def display_chat_messages():
    for msg in msgs.messages:
        css_class = "user-message" if msg.type == "human" else "assistant-message"
        avatar_base64 = user_avatar_base64 if msg.type == "human" else assistant_avatar_base64
        avatar_url = f"data:image/png;base64,{avatar_base64}"
        st.markdown(
            f"""
            <div class='chat-message {css_class}'>
                <img src='{avatar_url}' class='avatar' />
                <div class='message-content'>{msg.content}</div>
            </div>
            """, unsafe_allow_html=True
        )

display_chat_messages()

with st.sidebar:
    st.header("📂 루피에게 정보를 넣어줘")
    st.write("🗞️ 포네그리프, 원피스, pdf 여도 상관 없음")

    uploaded_file = st.file_uploader("파일을 업로드 해주세요", type=["pdf", "xlsx", "md"])

    if uploaded_file is not None and not st.session_state.get('loaded', False):
        with st.spinner("파일을 처리하는 중입니다..."):
            temp_file_path = os.path.join("/tmp", uploaded_file.name) 
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
            loader = handle_uploaded_file(uploaded_file, temp_file_path)
            documents, docs = process_documents(loader)
            initialize_retrievers(documents, docs)

    if st.button("Delete"):
        clear_session_state()
        msgs.messages.clear()
        st.success("Retrievers and messages have been cleared.")
    if st.button("채용정보 가져오기"):
        with st.spinner("채용 정보를 가져오는 중입니다..."):
            job_postings = get_job_postings()  # Fetch job postings
            job_summaries = get_job_summary(job_postings)
            st.session_state['job_summaries'] = job_summaries

        

prompt = st.chat_input("What is up?")
if prompt:
    handle_user_input(prompt, msgs, user_avatar_base64, assistant_avatar_base64, clova_studio_llm)

if len(msgs.messages) > 5:
    msgs.messages = msgs.messages[-5:]
