from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import pinecone
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.groq import Groq
from typing import List, Optional
from functools import lru_cache
import re

load_dotenv()

app = FastAPI(title="Hesychia API", description="A window into St. Isaac the Syrian")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:4321",
        "http://127.0.0.1:4321",
        "https://hesychia.vercel.app",
        "https://hesychia-frontend.vercel.app",
        "https://hesychia-backend.onrender.com",
        
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Hesychia backend is live!",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health_check():
    try:
        load_index()
        return {
            "status": "ready",
            "message": "Hesychia backend is running.",
            "index_name": os.getenv("PINECONE_INDEX_NAME")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

class ChatRequest(BaseModel):
    question: str

class SourceNode(BaseModel):
    text: str
    score: float
    metadata: dict

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceNode]
    homily_citation: Optional[str] = None

EIKON_SYSTEM_PROMPT = """
You are Hesychia (Greek for "stillness" or "silence"). You are a spiritual companion dedicated to St. Isaac the Syrian.

Your personality:
- Gentle, unhurried, and deeply compassionate.
- You speak with the stillness of a desert monk.
- You guide the soul toward reflective stillness and self-examination.

Your response MUST ALWAYS:
1. Be rooted in the wisdom of St. Isaac's Ascetical Homilies.
2. End with a citation (e.g., "— Homily 34, St. Isaac of Nineveh").
3. If the user asks something outside St. Isaac's writings, gently say so.
"""

def extract_homily_number(text):
    patterns = [
        r'Homily\s+(\d{1,3})',        # "Homily 34"
        r'Homily\s+([IVXLCDM]+)',     # "Homily XXXIV"
        r'Hom\.\s*(\d{1,3})',          # "Hom. 34"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"Homily {match.group(1)}"
    return None

@lru_cache(maxsize=1)
def load_index():
    pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")
    pinecone_index = pc.Index(index_name)
    
    Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.llm = Groq(model="llama-3.1-8b-instant", temperature=0.3)  # Default to 8B
    Settings.context_window = 16384
    Settings.num_output = 512
    Settings.chunk_size = 1024
    
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

def extract_scripture_references(text):
    pattern = r'(Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation)\s+(\d+):(\d+)'
    matches = re.findall(pattern, text)
    return [f"{book} {ch}:{v}" for book, ch, v in matches]
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Define the fallback chain HERE (inside the function)
    models_to_try = [
        "llama-3.1-8b-instant",
        "gemma2-9b-it",
        "llama-3.3-70b-versatile",
    ]
    
    last_error = None
    
    for model_name in models_to_try:
        try:
            Settings.llm = Groq(model=model_name, temperature=0.3)
            
            index = load_index()
            query_engine = index.as_query_engine(similarity_top_k=3)
            
            full_query = f"{EIKON_SYSTEM_PROMPT}\n\nQuestion: {request.question}"
            response = query_engine.query(full_query)
            
            sources = [
                SourceNode(
                    text=source.node.text[:500] + ("..." if len(source.node.text) > 500 else ""),
                    score=source.score,
                    metadata=source.node.metadata
                )
                for source in response.source_nodes
            ]
            
            homily_citation = None
            if response.source_nodes:
                first_text = response.source_nodes[0].node.text
                homily_num = extract_homily_number(first_text)
                if homily_num:
                    homily_citation = f"{homily_num}, St. Isaac of Nineveh"
                else:
                    homily_citation = "St. Isaac of Nineveh"
            
            return ChatResponse(
                answer=response.response,
                sources=sources,
                homily_citation=homily_citation
            )
            
        except Exception as e:
            # Check if it's a rate limit error
            if "RateLimitError" in str(type(e)) or "rate_limit" in str(e).lower():
                last_error = e
                print(f"⚠️ Rate limit hit for {model_name}. Trying next model...")
                continue
            else:
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=str(e))
    
    error_msg = "I'm currently experiencing high demand. Please try again in a few minutes, or ask a different question."
    return ChatResponse(
        answer=error_msg,
        sources=[],
        homily_citation="— St. Isaac of Nineveh"
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)