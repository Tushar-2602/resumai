import os
from pinecone import Pinecone, ServerlessSpec
from GenAi.GeminiApis import getEmbedding
# Configure Gemini

# Initialize Pinecone client
pc=Pinecone(api_key=os.environ.get("PINECONE_API_KEY"), environment="us-east-1")

# Connect or create index (dimension must match Gemini: 768)

# Save to Pinecone
def saveToPine(text: str, contentId: str):
    try:
        index_name = "resume-embeddings-index"
        index = pc.Index(index_name)
        vector = getEmbedding(text)
        index.upsert([
            (contentId, vector)  
        ])
        return 1
    except Exception as e:
        print("Error in saveToPine:", e)
        return 0
    # vector dimension 3072

# Query from Pinecone
def getFromPine(query: str, top_k: int = 15):
    index_name = "resume-embeddings-index"
    index = pc.Index(index_name)
    query_vec = getEmbedding(query)
    results = index.query(vector=query_vec, top_k=top_k)
    return results

