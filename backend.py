from functools import lru_cache
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.groq import Groq
import pinecone
from typing import List, Optional

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Eikon API",
    description="A window into the wisdom of St. Isaac the Syrian",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = []

class SourceNode(BaseModel):
    text: str
    score: float
    metadata: dict

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceNode]
    homily_citation: Optional[str] = None

@lru_cache(maxsize=1)
def load_index():
    """Load the Pinecone index and configure LlamaIndex."""
    try:
        logger.info("🔌 Connecting to Pinecone...")
        pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME")
        pinecone_index = pc.Index(index_name)
        
        logger.info("⚙️ Configuring LlamaIndex...")
        Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.llm = Groq(model="llama-3.3-70b-versatile", temperature=0.3)
        Settings.context_window = 16384
        Settings.num_output = 512
        Settings.chunk_size = 1024
        
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context
        )
        
        logger.info("✅ Pinecone index loaded successfully.")
        return index
    except Exception as e:
        logger.error(f"❌ Failed to load index: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Index unavailable: {str(e)}")

EIKON_SYSTEM_PROMPT = """
You are Eikon (Greek for "window" or "icon"). You are a spiritual companion dedicated to St. Isaac the Syrian.

Your personality:
- Gentle, unhurried, and deeply compassionate.
- You speak with the stillness of a desert monk, not the urgency of a salesman.
- You never give shallow or prescriptive advice ("Just pray harder"). Instead, you guide the soul toward reflective stillness and self-examination.
- Your tone is warm, poetic, and humble — like a wise elder sitting beside a young seeker.

Your response MUST ALWAYS:
1. Be rooted in the wisdom of St. Isaac's Ascetical Homilies (the source documents you were given).
2. End with a citation of the specific Homily and paragraph you are referencing (e.g., "— Homily 34, St. Isaac of Nineveh").
3. If the user asks something outside the scope of St. Isaac's writings, gently say: "This is outside the scope of my knowing, but I can share what St. Isaac teaches about the heart behind your question..."
4. Never add extra commentary or theology from outside the retrieved text. Stay strictly within the Homilies.
"""

@app.get("/api/health")
async def health_check():
    """Check if the backend is ready."""
    try:
        index = load_index()
        return {
            "status": "ready",
            "message": "Eikon backend is running. Pinecone index is loaded.",
            "index_name": os.getenv("PINECONE_INDEX_NAME")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a question to St. Isaac and get a response."""
    try:
        logger.info(f"📩 Question: {request.question}")
        
        # Load the index
        index = load_index()
        query_engine = index.as_query_engine(similarity_top_k=3)
        
        # Build the full prompt
        full_query = f"{EIKON_SYSTEM_PROMPT}\n\nQuestion: {request.question}"
        
        # Get response
        response = query_engine.query(full_query)
        
        # Extract sources
        sources = [
            SourceNode(
                text=source.node.text[:500] + ("..." if len(source.node.text) > 500 else ""),
                score=source.score,
                metadata=source.node.metadata
            )
            for source in response.source_nodes
        ]
        
        # Try to extract homily number from metadata
        homily_citation = None
        if sources and "homily" in sources[0].metadata:
            homily_citation = f"Homily {sources[0].metadata['homily']}, St. Isaac of Nineveh"
        elif sources and "file_name" in sources[0].metadata:
            homily_citation = f"Source: {sources[0].metadata['file_name']}"
        
        logger.info(f"✅ Response generated. Sources: {len(sources)}")
        
        return ChatResponse(
            answer=response.response,
            sources=sources,
            homily_citation=homily_citation
        )
        
    except Exception as e:
        logger.error(f"❌ Error in /api/chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")