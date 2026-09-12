import os
import threading
from typing import Optional, Dict
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils import chunkingConfig
from dotenv import load_dotenv

load_dotenv()

# Base directory for persistent local vector store storage.
# Can be overridden via VECTOR_STORE_DIR env var (e.g. for mounted persistent volumes).
DEFAULT_VECTOR_STORE_DIR = os.path.join(os.path.dirname(__file__), "vector_stores")
VECTOR_STORE_DIR = os.environ.get("VECTOR_STORE_DIR", DEFAULT_VECTOR_STORE_DIR)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)


class VectorStoreNotFoundError(Exception):
    """Raised when a vector store for a specific video cannot be found."""
    pass


class VectorStoreManager:
    """
    Manages vector store persistence and in-memory caching per video_id.
    Isolates storage mechanics so it can easily be swapped for S3/GCS/Cloud Vector DB
    without modifying RAG chain logic.
    """
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self._cache: Dict[str, FAISS] = {}
        self._lock = threading.Lock()

    def _get_video_path(self, video_id: str) -> str:
        # Sanitize video_id to prevent directory traversal
        safe_id = "".join(c for c in str(video_id) if c.isalnum() or c in ("-", "_"))
        return os.path.join(self.storage_dir, safe_id)

    def save_vector_store(self, video_id: str, vector_store: FAISS) -> None:
        path = self._get_video_path(video_id)
        os.makedirs(path, exist_ok=True)
        vector_store.save_local(path)
        with self._lock:
            self._cache[str(video_id)] = vector_store

    def load_vector_store(self, video_id: str, embeddings) -> Optional[FAISS]:
        str_id = str(video_id)
        with self._lock:
            if str_id in self._cache:
                return self._cache[str_id]

        path = self._get_video_path(str_id)
        index_file = os.path.join(path, "index.faiss")
        if os.path.exists(index_file):
            try:
                vector_store = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
                with self._lock:
                    self._cache[str_id] = vector_store
                return vector_store
            except Exception as e:
                print(f"Error loading vector store from disk for video {str_id}: {e}")
                return None
        return None

    def has_vector_store(self, video_id: str) -> bool:
        str_id = str(video_id)
        with self._lock:
            if str_id in self._cache:
                return True
        path = self._get_video_path(str_id)
        return os.path.exists(os.path.join(path, "index.faiss"))


# Storage Manager instance
store_manager = VectorStoreManager(VECTOR_STORE_DIR)

# Shared embedding and LLM singletons
_embedding_model: Optional[GoogleGenerativeAIEmbeddings] = None
_llm_model: Optional[ChatGoogleGenerativeAI] = None

def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return _embedding_model

def get_llm() -> ChatGoogleGenerativeAI:
    global _llm_model
    if _llm_model is None:
        _llm_model = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
    return _llm_model

CHAT_PROMPT = PromptTemplate.from_template("""
You are a knowledgeable, helpful, and conversational AI assistant answering questions about a video.
Answer the user's question accurately and directly based ONLY on the provided video context below.

CONTEXT FROM VIDEO:
-----------------
{context}
-----------------

INSTRUCTIONS:
- Answer directly and naturally in a helpful, conversational tone.
- NEVER mention phrases like "Based on the transcript", "According to the transcript", "The transcript states", or "In the provided context". Speak naturally as if discussing the video itself (e.g., refer to "the video" or provide direct answers).
- Synthesize and paraphrase key points clearly and structure the response nicely (e.g., using bullet points or bold text where appropriate).
- If the answer is not mentioned or cannot be determined from the video content, respond with: "This video does not cover that topic."
- Do not make up information or use external knowledge outside what is covered in the video.

QUESTION: {question}

Answer:
""")


def format_docs(documents):
    return "\n\n".join(doc.page_content for doc in documents)


def update_vector_store(video_id: str, transcript: str):
    if not video_id:
        raise ValueError("video_id is required to update vector store.")
    if not transcript:
        raise ValueError("transcript is required to update vector store.")

    docs = [Document(page_content=transcript)]
    chunk_size, chunk_overlap = chunkingConfig(transcript)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)

    embedding = get_embeddings()
    vector_store = FAISS.from_documents(chunks, embedding)
    store_manager.save_vector_store(str(video_id), vector_store)


def ask_question(video_id: str, question: str) -> str:
    if not video_id:
        raise ValueError("video_id is required.")
    if not question:
        raise ValueError("question is required.")

    embedding = get_embeddings()
    vector_store = store_manager.load_vector_store(str(video_id), embedding)
    if vector_store is None:
        raise VectorStoreNotFoundError(f"Vector store not found for video_id: {video_id}. Please initialize the vector store first.")

    retriever = vector_store.as_retriever()
    llm = get_llm()
    parser = StrOutputParser()

    parallel_chain = RunnableParallel({
        'context': retriever | RunnableLambda(format_docs),
        'question': RunnablePassthrough()
    })

    video_chain = parallel_chain | CHAT_PROMPT | llm | parser
    ans = video_chain.invoke(question)
    return ans

