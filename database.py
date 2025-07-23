import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

client = chromadb.Client(
    chromadb.config.Settings(
        persist_directory="./chroma_db",  # local folder for persistence
    )
)

collection = client.get_or_create_collection(
    name="videos",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}
)


def seed_example():
    existing = collection.get(ids=["example_video"])
    if len(existing["ids"]) == 0:
        collection.add(
            ids=["example_video"],
            documents=["This is a fake transcript about how to stay motivated while studying."],
            metadatas=[{
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "last_updated": datetime.utcnow().isoformat()
            }]
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
    return results["metadatas"][0]["video_url"]
