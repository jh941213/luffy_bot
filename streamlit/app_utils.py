import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.retrievers import EnsembleRetriever, BM25Retriever
from langchain_core.runnables.utils import ConfigurableField
from kiwipiepy import Kiwi
from get_jobs import get_job_postings  # get_jobs.py에서 함수 가져오기
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 한국어특화 kiwi 형태소 분석기를 사용하기 위해 kiwi 객체를 생성합니다. 
kiwi = Kiwi()

def kiwi_tokenize(text):
    return [token.form for token in kiwi.tokenize(text)]

def handle_uploaded_file(uploaded_file, temp_file_path):
    if uploaded_file.type == "application/pdf":
        return PyPDFLoader(temp_file_path)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return CSVLoader(temp_file_path)
    elif uploaded_file.type == "text/markdown":
        return UnstructuredMarkdownLoader(temp_file_path)
    else:
        st.error("Unsupported file type")
        st.stop()

def process_documents(loader):
    documents = loader.load()
    st.write(f"Loaded {len(documents)} documents from the uploaded file")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100, length_function=len, is_separator_regex=False)
    docs = text_splitter.split_documents(documents)
    st.write(f"Split the documents into {len(docs)} chunks")
    return documents, docs

def initialize_retrievers(documents, docs):
    try:
        hf = HuggingFaceEmbeddings(model_name="BAAI/bge-m3", model_kwargs={"device": "mps"})
        db = FAISS.from_documents(docs, hf)
        bm25_retriever = BM25Retriever.from_texts([doc.page_content for doc in docs], metadatas=[{"source": 1}] * len(docs), preprocess_func=kiwi_tokenize)
        bm25_retriever.k = 2
        faiss_retriever = db.as_retriever(search_kwargs={"k": 2})
        ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, faiss_retriever], weights=[0.7, 0.3])

        st.session_state.documents = documents
        st.session_state.docs = docs
        st.session_state.hf = hf
        st.session_state.db = db
        st.session_state.ensemble_retriever = ensemble_retriever
        st.session_state.loaded = True

    except Exception as e:
        st.error(f"Error during embeddings or retrievers initialization: {e}")

def clear_session_state():
    st.session_state.loaded = False
    if "documents" in st.session_state: del st.session_state.documents
    if "docs" in st.session_state: del st.session_state.docs
    if "hf" in st.session_state: del st.session_state.hf
    if "db" in st.session_state: del st.session_state.db
    if "ensemble_retriever" in st.session_state: del st.session_state.ensemble_retriever
    if "job_summaries" in st.session_state: del st.session_state.job_summaries
    
def handle_user_input(prompt, msgs, user_avatar_base64, assistant_avatar_base64, clova_studio_llm):
    msgs.add_user_message(prompt)
    css_class = "user-message"
    avatar_url = f"data:image/png;base64,{user_avatar_base64}"
    st.markdown(
        f"""
        <div class='chat-message {css_class}'>
            <img src='{avatar_url}' class='avatar' />
            <div class='message-content'>{prompt}</div>
        </div>
        """, unsafe_allow_html=True
    )

    response_text = ""
    RAG_PROMPT_TEMPLATE = """
        
        #질문 : {question} 
        #정보 : {context} 
        #채용공고 :
        {data}
        
        #답변 : """

    try:
        with st.spinner("응답을 생성하는 중입니다..."):
            if st.session_state.get('loaded', False):
                docs = st.session_state.ensemble_retriever.invoke(prompt)
                context = "\n".join([doc.page_content for doc in docs])
                job_summaries = st.session_state.get('job_summaries', [])
                data_section = "\n".join(job_summaries) if job_summaries else "No job postings available."
               
                combined_prompt = RAG_PROMPT_TEMPLATE.format(question=prompt, context=context, data=data_section)
                request_data = combined_prompt
            else:
                request_data = prompt

            response_text = clova_studio_llm._call(request_data)
            msgs.add_ai_message(response_text)

    except Exception as e:
        st.error(f"Error during document retrieval or Clova Studio LLM call: {e}")

    css_class = "assistant-message"
    avatar_url = f"data:image/png;base64,{assistant_avatar_base64}"
    st.markdown(
        f"""
        <div class='chat-message {css_class}'>
            <img src='{avatar_url}' class='avatar' />
            <div class='message-content'>{response_text}</div>
        </div>
        """, unsafe_allow_html=True
    )
