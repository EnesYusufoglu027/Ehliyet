import os
import sys
import subprocess
import asyncio
import schedule
import time
import random
import pickle
import requests
import edge_tts
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from generate_script import EhliyetContentGenerator

# -- Gereken paketleri yükle --
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in ["schedule", "google-api-python-client", "google-auth", "google-auth-oauthlib", "edge-tts", "requests"]:
    try:
        __import__(pkg)
    except ImportError:
        print(f"{pkg} yükleniyor...")
        install(pkg)

# -- YouTube API ayarları --
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)

def upload_video_to_youtube(video_path, title, description):
    youtube = get_authenticated_service()
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['ehliyet', 'sürüş', 'trafik', 'hava durumu'],
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    media = MediaFileUpload(video_path)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print(f"✅ Yüklendi: https://youtu.be/{response['id']}")
    return response['id']

# -- TTS SSML Dinamik --
def create_dynamic_ssml(text):
    words = text.split()
    ssml_parts = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">']
    for word in words:
        rate_change = random.uniform(-20, 20)
        ssml_parts.append(f'<prosody rate="{rate_change:.1f}%">{word}</prosody> <break time="100ms"/>')
    ssml_parts.append('</speak>')
    return ''.join(ssml_parts)

async def text_to_speech_edge_dynamic(text, output_file):
    ssml_text = create_dynamic_ssml(text)
    communicate = edge_tts.Communicate(ssml_text, voice="tr-TR-EmelNeural", input_format="ssml")
    await communicate.save(output_file)
    print(f"🔊 Ses dosyası oluşturuldu: {output_file}")

# -- Sahte video oluşturucu (Aliyun yerine geçici simülasyon) --
def create_video_stub(text, output_path):
    # Sadece boş bir mp4 dosyası oluşturalım (ffmpeg dummy)
    command = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=1080x1920:d=10",
        "-vf", f"drawtext=text='{text}':fontcolor=white:fontsize=60:x=50:y=H/2",
        output_path
    ]
    subprocess.run(command, check=True)
    print(f"📹 Simülasyon video oluşturuldu: {output_path}")

# -- Ses + video birleştir --
def merge_audio_video(audio_path, video_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]
    subprocess.run(command, check=True)
    print(f"🎬 Video tamamlandı: {output_path}")

# -- Günlük video üretimi ve yükleme --
async def generate_and_upload_videos():
    gen = EhliyetContentGenerator()
    condition = gen.get_weather_condition()

    # Short video
    short_text = gen.generate_short_tip(condition)
    short_title = f"{condition} Hakkında Kısa Bilgi #shorts"
    short_audio = "output/short_audio.mp3"
    short_video = "output/short_video.mp4"
    short_final = "output/short_final.mp4"

    # Long video
    long_text = gen.generate_long_tip(condition)
    long_title = f"{condition} Hakkında Detaylı Bilgi"
    long_audio = "output/long_audio.mp3"
    long_video = "output/long_video.mp4"
    long_final = "output/long_final.mp4"

    os.makedirs("output", exist_ok=True)

    # LONG VIDEO
    create_video_stub(long_text, long_video)
    await text_to_speech_edge_dynamic(long_text, long_audio)
    merge_audio_video(long_audio, long_video, long_final)
    long_id = upload_video_to_youtube(long_final, long_title, "Bugünkü detaylı hava durumu sürüş ipuçları.")

    # SHORT VIDEO
    create_video_stub(short_text, short_video)
    await text_to_speech_edge_dynamic(short_text, short_audio)
    merge_audio_video(short_audio, short_video, short_final)
    short_id = upload_video_to_youtube(short_final, short_title, f"Detaylı bilgi: https://youtu.be/{long_id}")

    print(f"📦 Upload tamamlandı. SHORT ID: {short_id}, LONG ID: {long_id}")

# -- Günlük zamanlayıcı --
def job():
    print("🕒 Video üretimi başladı...")
    asyncio.run(generate_and_upload_videos())
    print("✅ İşlem tamam.")

def run_scheduler():
    schedule.every().day.at("07:30").do(job)
    print("⏳ Zamanlayıcı aktif. 07:30'u bekliyor...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    run_scheduler()
