import os
import re
from functools import lru_cache
from typing import List, Optional

import pinecone
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.core.llms import CustomLLM, LLMMetadata, CompletionResponse
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.pinecone import PineconeVectorStore

from mistral_client import get_mistral_response
from hf_client import get_hf_response
from gemini_client import get_gemini_response

load_dotenv()

app = FastAPI(title="Hesychia API", description="A window into St. Isaac the Syrian")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

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

# --- Pydantic Models ---
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

# --- Helper: Extract Homily Number ---
def extract_homily_number(text: str) -> Optional[str]:
    patterns = [
        r'Homily\s+(\d{1,3})',
        r'Homily\s+([IVXLCDM]+)',
        r'Hom\.\s*(\d{1,3})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"Homily {match.group(1)}"
    return None

# --- Custom Gemini LLM (Bypasses llama-index-llms-gemini) ---
class GeminiLLM(CustomLLM):
    def __init__(self, model_name: str = "gemini-3.5-flash"):
        self.model_name = model_name
        super().__init__()

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(model_name=self.model_name)

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        response_text = get_gemini_response(prompt, self.model_name)
        return CompletionResponse(text=response_text or "Error: No response from Gemini")

# --- Load Pinecone Index (cached) ---
@lru_cache(maxsize=1)
def load_index():
    pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")
    pinecone_index = pc.Index(index_name)

    Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.llm = Groq(model="llama-3.1-8b-instant", temperature=0.3)
    Settings.context_window = 16384
    Settings.num_output = 512
    Settings.chunk_size = 1024

    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

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

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    groq_models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
    groq_worked = False

    for model_name in groq_models:
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
                homily_citation = f"{homily_num}, St. Isaac of Nineveh" if homily_num else "St. Isaac of Nineveh"

            groq_worked = True
            return ChatResponse(
                answer=response.response,
                sources=sources,
                homily_citation=homily_citation
            )

        except Exception as e:
            if "RateLimitError" in str(type(e)) or "rate_limit" in str(e).lower():
                print(f"⚠️ Groq model {model_name} failed (rate limit). Trying next...")
                continue
            else:
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=str(e))

    index = load_index()
    query_engine = index.as_query_engine(similarity_top_k=3)
    retrieval_response = query_engine.query(f"{EIKON_SYSTEM_PROMPT}\n\nQuestion: {request.question}")

    retrieved_texts = [node.text for node in retrieval_response.source_nodes]
    context = "\n\n---\n\n".join(retrieved_texts)

    grounded_query = f"""{EIKON_SYSTEM_PROMPT}

Here is the context from St. Isaac's homilies:
---
{context}
---

Based ONLY on the context above, answer this question:
Question: {request.question}

If the context does not contain the answer, say: "I cannot find an answer to this question in St. Isaac's writings."
"""

    sources = [
        SourceNode(
            text=node.text[:500] + ("..." if len(node.text) > 500 else ""),
            score=node.score,
            metadata=node.metadata
        )
        for node in retrieval_response.source_nodes
    ]

    homily_citation = None
    if retrieved_texts:
        homily_num = extract_homily_number(retrieved_texts[0])
        homily_citation = f"{homily_num}, St. Isaac of Nineveh" if homily_num else "St. Isaac of Nineveh"

    if os.getenv("GOOGLE_API_KEY"):
        print("⚠️ All Groq models failed. Falling back to Gemini (grounded)...")
        answer = get_gemini_response(grounded_query, model_name="gemini-3.5-flash")
        if answer:
            return ChatResponse(
                answer=answer,
                sources=sources,
                homily_citation=homily_citation
            )

    if os.getenv("MISTRAL_API_KEY"):
        print("⚠️ All Groq models failed. Falling back to Mistral (grounded)...")
        answer = get_mistral_response(grounded_query)
        if answer:
            return ChatResponse(
                answer=answer,
                sources=sources,
                homily_citation=homily_citation
            )

    if os.getenv("HF_API_KEY"):
        print("⚠️ All Groq models failed. Falling back to Hugging Face (grounded)...")
        answer = get_hf_response(grounded_query)
        if answer:
            return ChatResponse(
                answer=answer,
                sources=sources,
                homily_citation=homily_citation
            )

    error_msg = "I'm currently experiencing high demand. Please try again in a few minutes, or ask a different question."
    return ChatResponse(
        answer=error_msg,
        sources=[],
        homily_citation="— St. Isaac of Nineveh"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))