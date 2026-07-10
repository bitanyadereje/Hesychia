import os
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.groq import Groq
import pinecone

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Eikon — St. Isaac the Syrian",
    page_icon="🪟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VINTAGE OLD-PAPER CSS (The Aesthetic) ---
st.markdown("""
<style>
    /* Import vintage serif fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&display=swap');

    /* Main background — aged parchment with subtle texture */
    .stApp {
        background-color: #f4efe6;
        background-image: 
            linear-gradient(135deg, #f4efe6 0%, #e8dfd1 50%, #dfd4c4 100%);
        font-family: 'Cormorant Garamond', serif;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Scrollbar — old leather style */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #e8ddd0;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #b8966b;
        border-radius: 10px;
        border: 1px solid #d6c6b2;
    }

    /* Titles — gilded manuscript style */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
        font-family: 'Playfair Display', serif !important;
        color: #3b2f2f !important;
        letter-spacing: 0.5px;
    }
    
    .stMarkdown h1 {
        font-size: 3rem !important;
        font-weight: 600 !important;
        border-bottom: 1px solid #d6c6b2;
        padding-bottom: 0.3rem;
        margin-bottom: 0.5rem;
    }

    .stMarkdown em {
        color: #6b5a4a;
        font-size: 1.2rem;
    }

    /* Sidebar — old library feel */
    .css-1d391kg, .css-1lcbmhc, .stSidebar {
        background-color: #e8ddd0 !important;
        border-right: 2px solid #d6c6b2 !important;
        background-image: linear-gradient(180deg, #e8ddd0 0%, #ddd0be 100%) !important;
    }
    
    .stSidebar .stMarkdown {
        font-family: 'Cormorant Garamond', serif !important;
        color: #3b2f2f !important;
    }

    .stSidebar .stMarkdown h1 {
        font-size: 2.2rem !important;
        border-bottom: 1px solid #b8966b;
        padding-bottom: 0.5rem;
    }

    /* Chat Input — vintage writing desk */
    .stChatInput textarea {
        background-color: #fcf9f2 !important;
        border: 1px solid #c9b89b !important;
        border-radius: 8px !important;
        color: #3b2f2f !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 18px !important;
        box-shadow: inset 0 1px 4px rgba(0,0,0,0.05), 0 2px 8px rgba(0,0,0,0.02) !important;
        padding: 12px 16px !important;
    }
    .stChatInput textarea:focus {
        border-color: #b8966b !important;
        box-shadow: inset 0 1px 4px rgba(0,0,0,0.05), 0 0 0 2px rgba(184, 150, 107, 0.2) !important;
    }

    /* User messages — clean, subtle parchment */
    .stChatMessage:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #e8ddd0 !important;
        border-radius: 12px 12px 4px 12px !important;
        padding: 12px 18px !important;
        margin: 8px 0 12px 0 !important;
        border-left: 3px solid #b8966b !important;
        font-family: 'Cormorant Garamond', serif !important;
        color: #2c2424 !important;
        font-size: 17px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
        max-width: 80% !important;
        float: right !important;
    }

    /* Assistant messages — the "monk's scroll" */
    .stChatMessage:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #fcf9f2 !important;
        border-radius: 12px 12px 12px 4px !important;
        padding: 16px 22px !important;
        margin: 8px 0 12px 0 !important;
        border-right: 3px solid #a88b6b !important;
        border-left: 1px solid #e2d4c0 !important;
        font-family: 'Playfair Display', serif !important;
        color: #2c2424 !important;
        font-size: 17px !important;
        line-height: 1.7 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        max-width: 85% !important;
        float: left !important;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch"/></filter><rect width="100" height="100" filter="url(%23n)" opacity="0.04"/></svg>') !important;
        background-blend-mode: overlay !important;
    }

    /* Gold-accented buttons */
    .stButton button {
        background-color: #b8966b !important;
        color: white !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 0.5rem 1.8rem !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12) !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.5px;
    }
    .stButton button:hover {
        background-color: #a07d54 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        transform: scale(1.02);
    }
    .stButton button:active {
        transform: scale(0.97);
    }

    /* Source expander — vintage footnote style */
    .streamlit-expanderHeader {
        font-family: 'Cormorant Garamond', serif !important;
        color: #6b5a4a !important;
        font-size: 15px !important;
        font-style: italic !important;
        border-bottom: 1px dashed #d6c6b2 !important;
        padding-bottom: 4px !important;
    }
    .streamlit-expanderContent {
        background-color: #f8f2e8 !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        border-left: 2px solid #d6c6b2 !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 14px !important;
        color: #4a3f3f !important;
    }

    /* Divider — ornate */
    hr {
        border: 0 !important;
        height: 1px !important;
        background: linear-gradient(to right, transparent, #b8966b, transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* Status/warning messages */
    .stAlert {
        background-color: #f8f2e8 !important;
        border-left: 4px solid #b8966b !important;
        font-family: 'Cormorant Garamond', serif !important;
        color: #3b2f2f !important;
    }

    /* Float clearing for chat messages */
    .stChatMessage {
        clear: both !important;
    }
    
    /* Chat avatar icons */
    .stChatMessageAvatar {
        margin-top: 4px !important;
    }

    /* Small caption text for history */
    .stSidebar .stCaption {
        color: #4a3f3f !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 14px !important;
        border-bottom: 1px dotted #d6c6b2;
        padding-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: History ---
with st.sidebar:
    st.markdown("# 🪟 Eikon")
    st.markdown("*A window into the wisdom of St. Isaac the Syrian*")
    st.divider()
    
    st.markdown("### 📜 Conversation")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if len(st.session_state.messages) == 0:
        st.caption("No conversation yet. Ask a question below.")
    else:
        # Show the last 10 messages in reverse order (newest at bottom)
        for i, msg in enumerate(st.session_state.messages[-10:]):
            if msg["role"] == "user":
                st.caption(f"🧑 **You:** {msg['content'][:60]}...")
            else:
                st.caption(f"🪔 **Eikon:** {msg['content'][:60]}...")
    
    st.divider()
    if st.button("🔄 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Chat Area ---
st.markdown("# 🪟 Eikon")
st.markdown("*A gentle companion rooted in the Ascetical Homilies of St. Isaac the Syrian.*")
st.divider()

# --- Initialize Pinecone and LLM ---
@st.cache_resource
def load_index():
    try:
        # Connect to Pinecone
        pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME")
        pinecone_index = pc.Index(index_name)
        
        # Configure LlamaIndex
        Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.llm = Groq(model="llama-3.3-70b-versatile", temperature=0.3)
        
        # CRITICAL FIX: Set context window to avoid negative math error
        Settings.context_window = 16384
        Settings.num_output = 512
        Settings.chunk_size = 1024
        
        # Build the vector store index
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context
        )
        
        return index
    except Exception as e:
        st.error(f"⚠️ Could not connect to Pinecone.\n\n**Error:** {str(e)}")
        st.stop()

try:
    index = load_index()
    query_engine = index.as_query_engine(similarity_top_k=3)
except Exception as e:
    st.error(f"⚠️ Failed to initialize the search engine.\n\n**Error:** {str(e)}")
    st.stop()

# --- St. Isaac System Persona ---
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

# --- Chat Input & Response ---
if prompt := st.chat_input("Ask a question from St. Isaac's wisdom..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant", avatar="🪔"):
        with st.spinner("Searching the Homilies in stillness..."):
            # Combine system prompt with user query
            full_query = f"{EIKON_SYSTEM_PROMPT}\n\nQuestion: {prompt}"
            response = query_engine.query(full_query)
            
            # Display the response
            st.markdown(response.response)
            
            # Display source references in an elegant expander
            with st.expander("📜 View Source References"):
                for idx, source in enumerate(response.source_nodes, 1):
                    st.caption(f"**Source {idx}** — Score: {source.score:.2f}")
                    st.caption(f"📄 {source.node.metadata.get('file_name', 'Unknown source')}")
                    st.text(source.node.text[:400] + ("..." if len(source.node.text) > 400 else ""))
                    st.divider()
    
    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": response.response})

# --- Welcome Message (First Visit) ---
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant", avatar="🪔"):
        st.markdown("""
        Greetings, friend.  
        
        I am **Eikon** — a window into the tender wisdom of **St. Isaac the Syrian**.  
        
        Ask me anything about the spiritual life, the struggles of the heart, prayer, tears, stillness, or the path toward God. I will search his Ascetical Homilies and bring you an answer, always with a citation so you can read further in the original text.  
        
        *"Be at peace with your own soul, and heaven and earth will be at peace with you."*  
        — St. Isaac
        """)