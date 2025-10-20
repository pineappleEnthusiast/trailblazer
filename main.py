from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_PLAYLIST_URL = os.getenv("YOUTUBE_PLAYLIST_URL")

app = FastAPI()

# Allow your frontend origin (adjust if needed)
origins = [
    "http://localhost:5173",  # React dev server
     "https://framer.com",     # Framer preview
    "https://trailblazernetwork.framer.ai/",  # If you have a custom Framer page
    "https://trailblazernetwork.framer.ai/chatbot"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SurveyInput(BaseModel):
    user_input: str

@app.post("/recommend")
async def recommend_video(data: SurveyInput):
    video_url = database.query_videos(data.user_input)
    return {
        "videoUrl": video_url,
        "message": ""
    }

########################################################################


def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=os.getenv("WEBSHARE_USERNAME"),
                proxy_password=os.getenv("WEBSHARE_PASSWORD")
            )
        ).list(video_id)
        transcript = transcript_list.find_transcript(['en'])
        return " ".join([item.text for item in transcript.fetch()])

    except Exception as e:
        print(e)
        return "No transcript available."


@app.get("/refresh")
async def refresh():
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        videos = []
        next_page_token = None

        while True:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=YOUTUBE_PLAYLIST_URL,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            videos.extend(response["items"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        existing = database.collection.get(include=["metadatas"])
        existing_urls = {meta["video_url"]: meta["last_updated"] for meta in existing["metadatas"]}

        for item in videos:
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_url = f"https://www.youtube.com/embed/{video_id}"

            last_updated = item["snippet"]["publishedAt"]

            if video_url in existing_urls:
                if last_updated > existing_urls[video_url]:
                    transcript = get_transcript(video_url)
                    database.collection.delete(ids=[video_id])
                    database.add_video(video_id, transcript, video_url, last_updated)
                continue
            
            transcript = get_transcript(video_id)
            if transcript == "No transcript available.":
                print(f'Video {video_id} has no transcript so will be excluded from the database.')
                continue
            database.add_video(video_id, transcript, video_url, last_updated)
        
        print(database.collection.get(include=["documents", "metadatas"]))
        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/debug-videos")
async def debug_videos():
    results = database.collection.get(include=["documents", "metadatas"])
    for doc in results['documents']:
        print(doc)
    return results
