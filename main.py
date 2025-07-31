import os
import sys
import subprocess
import base64
import asyncio

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import edge_tts

# -- ENV DEĞİŞKENLERİNİ YÜKLE --
token_b64 = os.environ.get("TOKEN_JSON_BASE64")
client_b64 = os.environ.get("CLIENT_SECRET_BASE64")

if not token_b64 or not client_b64:
    print("TOKEN_JSON_BASE64 veya CLIENT_SECRET_BASE64 eksik!")
    exit(1)

with open("token.json", "wb") as f:
    f.write(base64.b64decode(token_b64))

with open("client_secret.json", "wb") as f:
    f.write(base64.b64decode(client_b64))

print("✅ Gerekli kimlik dosyaları oluşturuldu.")

# -- SES OLUŞTUR --
async def create_speech(text, path):
    communicate = edge_tts.Communicate(text=text, voice="tr-TR-EmelNeural")
    await communicate.save(path)
    print(f"🎤 Ses dosyası oluşturuldu: {path}")

# -- VİDEO TEMİZLEME (SESSİZLEŞTİRME) --
def reencode_video(input_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-an",
        output_path
    ]
    subprocess.run(command, check=True)
    print(f"🎞️ Video yeniden encode edildi: {output_path}")

# -- SESİ BİRLEŞTİR --
def replace_audio(video_path, audio_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_path
    ]
    subprocess.run(command, check=True)
    print(f"🎬 Final video oluşturuldu: {output_path}")

# -- YOUTUBE YÜKLEME --
def upload_to_youtube(video_path, title, desc):
    creds = service_account.Credentials.from_service_account_file(
        "client_secret.json", scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    youtube = build("youtube", "v3", credentials=creds)
    request_body = {
        "snippet": {
            "title": title,
            "description": desc,
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    media = MediaFileUpload(video_path)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
    response = request.execute()
    print(f"✅ Yüklendi: https://youtu.be/{response['id']}")

# -- ANA AKIŞ --
async def main():
    input_video = "video.mp4"
    silent_video = "video_silent.mp4"
    speech_file = "speech.mp3"
    final_output = "final_output.mp4"

    await create_speech("Bu test yayınıdır. Lütfen ehliyet kurallarına dikkat ediniz.", speech_file)
    reencode_video(input_video, silent_video)
    replace_audio(silent_video, speech_file, final_output)
    upload_to_youtube(final_output, "Test Video - Ehliyet", "Test açıklama içeriği")

if __name__ == "__main__":
    asyncio.run(main())
