from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

client = PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="videos",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}
)


def add_video(video_id: str, transcript: str, url: str, updated_at: str):
    collection.add(
        ids=[video_id],  # Must be unique per video
        documents=[transcript],
        metadatas=[{
            "video_url": url,
            "last_updated": updated_at
        }]
    )


def query_videos(user_query: str, n_results: int = 1):
    results = collection.query(
        query_texts=[user_query],
        n_results=n_results
    )
    return results["metadatas"][0][0]["video_url"]
