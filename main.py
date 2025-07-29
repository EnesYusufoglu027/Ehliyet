import os
import sys
import subprocess
import asyncio
import schedule
import time
import random
import requests
import shutil
import base64
import json

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import edge_tts

# -- ffmpeg kontrolü --
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("HATA: ffmpeg sistemde bulunamadı. Lütfen CI ortamında ffmpeg'in kurulu olduğundan emin olun.")
        sys.exit(1)
    else:
        print("ffmpeg bulundu.")

check_ffmpeg()

# -- Gerekli paketleri yükle --
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in ["schedule", "google-api-python-client", "google-auth", "google-auth-oauthlib", "edge-tts", "requests"]:
    try:
        __import__(pkg)
    except ImportError:
        print(f"{pkg} paketi yüklü değil, yükleniyor...")
        install(pkg)

# -- YouTube servisi --
def get_youtube_service():
    base64_secret = os.environ.get("CLIENT_SECRET_BASE64")
    if not base64_secret:
        raise Exception("CLIENT_SECRET_BASE64 bulunamadı.")

    # JSON oluştur
    secret_json = base64.b64decode(base64_secret).decode("utf-8")
    with open("service_account.json", "w") as f:
        f.write(secret_json)

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = service_account.Credentials.from_service_account_file("service_account.json", scopes=scopes)
    service = build("youtube", "v3", credentials=creds)
    return service

# -- YouTube video yükleme --
def upload_video_to_youtube(video_path, title, description):
    youtube = get_youtube_service()
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['ehliyet', 'sürüş', 'hava durumu', 'kış sürüşü'],
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        }
    }
    media = MediaFileUpload(video_path)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print(f"Video yüklendi: ID={response['id']}")
    return response['id']

# -- İçerik üretici sınıfı --
class EhliyetContentGenerator:
    def __init__(self):
        self.content = {
            "Hava Koşulları": {
                "Karlı": [
                    "Karlı havalarda mutlaka hızınızı azaltın ve takip mesafenizi artırın.",
                    "Karlı yollarda ani fren ve ani hızlanmalardan kaçının.",
                    "Kış lastiği kullanmak kayma riskini azaltır.",
                    "Araçta kayma başladığında panik yapmadan direksiyonu kayma yönüne çevirin.",
                    "Sileceklerinizi kontrol edin, görüş alanını net tutun."
                ],
                "Yağmurlu": [
                    "Yağmurda yavaş sürün ve fren mesafenizi artırın.",
                    "Islak zeminlerde ani hareketlerden kaçının.",
                    "Farlarınızı açmayı unutmayın.",
                    "Lastik diş derinliğine dikkat edin.",
                    "Sileceklerin çalışır durumda olduğundan emin olun."
                ],
                "Güneşli": [
                    "Güneşli havalarda gözlük takarak görüşünüzü artırın.",
                    "Yol çizgilerini dikkatle takip edin.",
                    "Ani fren ve dönüşlerden kaçının.",
                    "Yayalara dikkat edin.",
                    "Klima kullanarak rahat sürüş sağlayın."
                ]
            }
        }

    def get_weather_condition(self):
        return random.choice(list(self.content["Hava Koşulları"].keys()))

    def generate_short_tip(self, condition):
        return random.choice(self.content["Hava Koşulları"][condition])

    def generate_long_tip(self, condition):
        tips = self.content["Hava Koşulları"][condition]
        tip1 = random.choice(tips)
        tip2 = random.choice([t for t in tips if t != tip1])
        return f"{tip1} {tip2}"

# -- SSML üretici --
def create_dynamic_ssml(text):
    words = text.split()
    ssml_parts = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">']
    for word in words:
        rate = random.uniform(-20, 20)
        ssml_parts.append(f'<prosody rate="{rate:.1f}%">{word}</prosody><break time="100ms"/>')
    ssml_parts.append('</speak>')
    return ''.join(ssml_parts)

# -- Ses dosyası üretimi --
async def text_to_speech_edge_dynamic(text, output_file):
    ssml = create_dynamic_ssml(text)
    communicate = edge_tts.Communicate(ssml, voice="tr-TR-EmelNeural", input_format="ssml")
    await communicate.save(output_file)
    print(f"Ses dosyası oluşturuldu: {output_file}")

# -- Aliyun üzerinden video oluştur --
def create_video_via_aliyun(text, output_path):
    aliyun_token = os.environ.get("ALIYUN_ACCESS_TOKEN")
    if not aliyun_token:
        raise Exception("ALIYUN_ACCESS_TOKEN bulunamadı.")

    url = "https://video-ai.aliyuncs.com/create"  # gerçek endpoint kullanılmalı
    headers = {
        "Authorization": f"Bearer {aliyun_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice": "tr-TR-EmelNeural"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        video_url = response.json().get("video_url")
        video_data = requests.get(video_url).content
        with open(output_path, "wb") as f:
            f.write(video_data)
        print(f"Video indirildi: {output_path}")
    else:
        raise Exception(f"Aliyun video oluşturma hatası: {response.status_code} - {response.text}")

# -- Video ve sesi birleştir --
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
    print(f"Video ve ses birleştirildi: {output_path}")

# -- Günlük video üret ve yükle --
async def generate_and_upload_videos():
    gen = EhliyetContentGenerator()
    condition = gen.get_weather_condition()

    os.makedirs("output", exist_ok=True)

    # SHORT video
    short_text = gen.generate_short_tip(condition)
    short_audio = "output/short_audio.mp3"
    short_video = "output/short_video.mp4"
    short_final = "output/short_final.mp4"

    # LONG video
    long_text = gen.generate_long_tip(condition)
    long_audio = "output/long_audio.mp3"
    long_video = "output/long_video.mp4"
    long_final = "output/long_final.mp4"

    create_video_via_aliyun(short_text, short_video)
    await text_to_speech_edge_dynamic(short_text, short_audio)
    merge_audio_video(short_audio, short_video, short_final)

    create_video_via_aliyun(long_text, long_video)
    await text_to_speech_edge_dynamic(long_text, long_audio)
    merge_audio_video(long_audio, long_video, long_final)

    # YouTube'a yükleme
    long_video_id = upload_video_to_youtube(long_final, f"Hava Durumu Detayları: {condition}", f"İki ipucu bir arada.")
    short_video_id = upload_video_to_youtube(short_final, f"{condition} İçin Kısa İpucu", f"Uzun video: https://youtu.be/{long_video_id}")

    print(f"Yüklenen videolar: SHORT={short_video_id}, LONG={long_video_id}")

# -- Zamanlayıcı başlat --
def job():
    print("Günlük video üretimi başlıyor...")
    asyncio.run(generate_and_upload_videos())
    print("Video üretimi tamamlandı.")

if __name__ == "__main__":
   print("BAŞARILI")
