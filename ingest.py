import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.fastembed import FastEmbedEmbedding  # <-- CHANGED
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
import pinecone

load_dotenv()

print("🔌 Connecting to Pinecone...")
pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")

# Check if the index exists; if not, create it
if index_name not in pc.list_indexes().names():
    print(f" Creating new Pinecone index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=384,  
        metric="cosine",
        spec=pinecone.ServerlessSpec(cloud="aws", region="us-east-1")
    )
else:
    print(f"Pinecone index '{index_name}' already exists.")

pinecone_index = pc.Index(index_name)

print(" Configuring LlamaIndex...")
Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")  # <-- CHANGED
Settings.chunk_size = 2048      # Bigger chunks = fewer chunks
Settings.chunk_overlap = 100    # Slightly more overlap for dense texts

print(" Loading documents from './data'...")
reader = SimpleDirectoryReader(input_files=["./data/st_isaac_clean.txt"])
documents = reader.load_data()

if len(documents) == 0:
    print(" ERROR: No documents found in the 'data' folder.")
    print("   Please place your St. Isaac PDF(s) or .txt files into ./data and try again.")
    exit(1)

print(f" Loaded {len(documents)} pages/documents.")

print(" Splitting documents into chunks...")
parser = SimpleNodeParser.from_defaults(
    chunk_size=Settings.chunk_size,
    chunk_overlap=Settings.chunk_overlap
)
nodes = parser.get_nodes_from_documents(documents)

print(f"✂️  Split into {len(nodes)} chunks.")

print("⬆️ Uploading chunks to Pinecone (this may take a moment)...")
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex(nodes, storage_context=storage_context)

print(f"✅ SUCCESS! Ingested {len(nodes)} chunks into Pinecone index: {index_name}")
print("🪟 You can now run the Eikon chat app.")