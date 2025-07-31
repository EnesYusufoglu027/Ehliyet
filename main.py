import os
import asyncio
import subprocess
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import edge_tts

# ----------------------
# 💬 Edge-TTS ile Sesli Metin Üret
# ----------------------
async def generate_speech(text, output_path):
    communicate = edge_tts.Communicate(text, voice="tr-TR-EmelNeural")
    await communicate.save(output_path)
    print(f"🎤 Ses dosyası oluşturuldu: {output_path}")

# ----------------------
# 🎬 Sesi Mevcut Videoyla Değiştir
# ----------------------
def replace_audio(input_video, output_audio, final_output):
    command = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-i", output_audio,
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        final_output
    ]
    subprocess.run(command, check=True)
    print(f"🎬 Video oluşturuldu: {final_output}")

# ----------------------
# 🔑 YouTube API Erişimi Al (client_secret + token.json ile)
# ----------------------
def get_youtube_service():
    creds = None
    if os.path.exists("token.json"):
        with open("token.json", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                ["https://www.googleapis.com/auth/youtube.upload"]
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

# ----------------------
# ⬆️ YouTube’a Video Yükle
# ----------------------
def upload_video(video_path, title, description):
    youtube = get_youtube_service()
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["ehliyet", "trafik", "yol"],
                "categoryId": "27"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(video_path)
    )
    response = request.execute()
    print(f"📺 Video yüklendi: https://youtu.be/{response['id']}")
    return response["id"]

# ----------------------
# 🚀 Ana İşlem
# ----------------------
async def main():
    input_video = "video.mp4"          # Bu videonun sesi değiştirilecek
    output_audio = "speech.mp3"
    final_video = "final_output.mp4"
    text = "Karlı havalarda hızınızı azaltın ve takip mesafenizi artırın."

    await generate_speech(text, output_audio)
    replace_audio(input_video, output_audio, final_video)
    upload_video(final_video, "Test Video - Yeni Sesli", "Edge-TTS ile oluşturulan ses kullanıldı.")

if __name__ == "__main__":
    asyncio.run(main())
