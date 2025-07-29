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
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import edge_tts

# -- ffmpeg kontrolü --
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("HATA: ffmpeg bulunamadı.")
        sys.exit(1)
    print("ffmpeg ✅")
check_ffmpeg()

# -- Gerekli paketleri kontrol edip yükle --
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in ["schedule", "google-api-python-client", "google-auth", "google-auth-oauthlib", "edge-tts", "requests"]:
    try:
        __import__(pkg)
    except ImportError:
        print(f"{pkg} yükleniyor...")
        install(pkg)

# -- client_secret.json base64 decode --
CLIENT_SECRET_BASE64 = os.getenv("CLIENT_SECRET_BASE64")
if not CLIENT_SECRET_BASE64:
    print("HATA: CLIENT_SECRET_BASE64 tanımsız!")
    sys.exit(1)

os.makedirs("secrets", exist_ok=True)
with open("secrets/client_secret.json", "wb") as f:
    f.write(base64.b64decode(CLIENT_SECRET_BASE64))

# -- YouTube API yetkilendirme --
def get_youtube_service():
    from google_auth_oauthlib.flow import InstalledAppFlow
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    flow = InstalledAppFlow.from_client_secrets_file("secrets/client_secret.json", SCOPES)
    creds = flow.run_local_server(port=8080)
    return build("youtube", "v3", credentials=creds)

def upload_video_to_youtube(video_path, title, description):
    youtube = get_youtube_service()
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['ehliyet', 'sürüş', 'trafik', 'hava durumu'],
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
    print(f"Yüklendi: https://youtu.be/{response['id']}")
    return response['id']

# -- Aliyun API Key --
ALIYUN_API_KEY = os.getenv("ALIYUN_ACCESS_TOKEN")
if not ALIYUN_API_KEY:
    print("HATA: ALIYUN_ACCESS_TOKEN eksik!")
    sys.exit(1)

# -- SSML oluştur --
def create_dynamic_ssml(text):
    words = text.split()
    ssml_parts = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">']
    for word in words:
        rate = random.uniform(-15, 15)
        ssml_parts.append(f'<prosody rate="{rate:.1f}%">{word}</prosody> <break time="100ms"/>')
    ssml_parts.append('</speak>')
    return ''.join(ssml_parts)

# -- Edge TTS ile ses oluştur --
async def text_to_speech_edge_dynamic(text, output_file):
    ssml_text = create_dynamic_ssml(text)
    communicate = edge_tts.Communicate(ssml_text, voice="tr-TR-EmelNeural", input_format="ssml")
    await communicate.save(output_file)
    print(f"Ses dosyası oluşturuldu: {output_file}")

# -- Aliyun video oluştur (örnek endpoint) --
def create_video_via_aliyun(text, output_path):
    url = "https://video-ai.aliyuncs.com/create"  # Gerçek endpoint olmalı
    headers = {
        "Authorization": f"Bearer {ALIYUN_API_KEY}",
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
        raise Exception(f"Aliyun video oluşturma başarısız: {response.status_code} - {response.text}")

# -- Ses + videoyu birleştir --
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

# -- İçerik üretici --
class EhliyetContentGenerator:
    def __init__(self):
        self.content = {
            "Karlı": [
                "Karlı havalarda mutlaka hızınızı azaltın.",
                "Takip mesafenizi artırın.",
                "Kış lastiği kullanmak kayma riskini azaltır.",
                "Kayma başladığında panik yapmayın.",
                "Silecekler çalışır durumda olmalı."
            ],
            "Yağmurlu": [
                "Yağmurda fren mesafesi uzar.",
                "Islak zeminde ani hareketlerden kaçının.",
                "Farlarınızı açmayı unutmayın.",
                "Silecekler görüşü artırır.",
                "Yol çizgilerine dikkat edin."
            ],
            "Güneşli": [
                "Güneş gözlüğü kullanın.",
                "Yayalara dikkat edin.",
                "Yol çizgilerini takip edin.",
                "Ani frenlerden kaçının.",
                "Rahat sürüş için klima açın."
            ]
        }

    def get_weather(self):
        return random.choice(list(self.content.keys()))

    def get_short_tip(self, condition):
        return random.choice(self.content[condition])

    def get_long_tip(self, condition):
        tips = self.content[condition]
        t1 = random.choice(tips)
        t2 = random.choice([t for t in tips if t != t1])
        return f"{t1} {t2}"

# -- Video üretimi --
async def generate_and_upload():
    gen = EhliyetContentGenerator()
    condition = gen.get_weather()

    os.makedirs("output", exist_ok=True)

    # SHORT
    short_text = gen.get_short_tip(condition)
    short_audio = "output/short_audio.mp3"
    short_video = "output/short_video.mp4"
    short_final = "output/short_final.mp4"

    # LONG
    long_text = gen.get_long_tip(condition)
    long_audio = "output/long_audio.mp3"
    long_video = "output/long_video.mp4"
    long_final = "output/long_final.mp4"

    create_video_via_aliyun(short_text, short_video)
    await text_to_speech_edge_dynamic(short_text, short_audio)
    merge_audio_video(short_audio, short_video, short_final)

    create_video_via_aliyun(long_text, long_video)
    await text_to_speech_edge_dynamic(long_text, long_audio)
    merge_audio_video(long_audio, long_video, long_final)

    long_id = upload_video_to_youtube(long_final, f"{condition} Sürüş Tavsiyeleri", "Detaylı bilgi için izleyin.")
    short_id = upload_video_to_youtube(short_final, f"{condition} Hakkında Kısa Bilgi", f"Detaylı video: https://youtu.be/{long_id}")

    print(f"✅ Yüklenen videolar: Shorts={short_id} / Uzun={long_id}")

# -- Takvim görevi --
def job():
    print("▶ Video üretimi başladı")
    asyncio.run(generate_and_upload())
    print("✅ Tamamlandı")

def run_scheduler():
    schedule.every().day.at("07:30").do(job)
    print("Takvim başlatıldı. Bekleniyor...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    run_scheduler()
