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

load_dotenv()

app = FastAPI(title="Hyescia API", description="A window into St. Isaac the Syrian")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:4321",
    "http://localhost:5173",
    "https://hesychia.vercel.app",  
    "https://your-render-backend.onrender.com", 
],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    
)

# --- Models ---
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

# --- System Prompt ---
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

# --- Load Index ---
@lru_cache(maxsize=1)
def load_index():
    pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")
    pinecone_index = pc.Index(index_name)
    
    Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.llm = Groq(model="llama-3.3-70b-versatile", temperature=0.3)
    Settings.context_window = 16384
    Settings.num_output = 512
    Settings.chunk_size = 1024
    
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

# --- Health Endpoint ---
@app.get("/api/health")
async def health_check():
    try:
        load_index()
        return {
            "status": "ready",
            "message": "Hyescia backend is running.",
            "index_name": os.getenv("PINECONE_INDEX_NAME")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Chat Endpoint ---
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
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
        if sources and "file_name" in sources[0].metadata:
            homily_citation = f"Source: {sources[0].metadata['file_name']}"
        elif sources and "homily" in sources[0].metadata:
            homily_citation = f"Homily {sources[0].metadata['homily']}, St. Isaac of Nineveh"
        
        return ChatResponse(
            answer=response.response,
            sources=sources,
            homily_citation=homily_citation
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)