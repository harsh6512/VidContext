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

# Global cache
vector_store = None
main_chain = None

def format_docs(documents):
    return "\n\n".join(doc.page_content for doc in documents)

def update_vector_store(transcript):
    global vector_store, main_chain

    docs = [Document(page_content=transcript)]
    chunk_size,chunk_overlap = chunkingConfig(transcript)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)

    embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = FAISS.from_documents(chunks, embedding)
    retriever = vector_store.as_retriever()

    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
    prompt = PromptTemplate.from_template("""
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


    parser = StrOutputParser()

    parallel_chain = RunnableParallel({
        'context': retriever | RunnableLambda(format_docs),
        'question': RunnablePassthrough()
    })

    main_chain = parallel_chain | prompt | llm | parser

def ask_question(question):
    if main_chain is None:
        raise ValueError("Vector store not initialized.")
    ans = main_chain.invoke(question)
    return ans
