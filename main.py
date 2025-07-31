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
from google.oauth2.credentials import Credentials
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

# -- token.json BASE64 decode --
token_b64 = os.environ.get("TOKEN_JSON_BASE64")
if not token_b64:
    print("TOKEN_JSON_BASE64 env değişkeni bulunamadı!")
    exit(1)
with open("token.json", "wb") as f:
    f.write(base64.b64decode(token_b64))
print("✅ token.json başarıyla oluşturuldu.")

# -- YouTube servisi --
def get_youtube_service():
    with open("token.json", "r") as f:
        token_data = json.load(f)

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = Credentials.from_authorized_user_info(token_data, scopes=scopes)
    return build("youtube", "v3", credentials=creds)

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

# -- Ses sentezi (Edge TTS) --
def create_dynamic_ssml(text):
    words = text.split()
    ssml_parts = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">']
    for word in words:
        rate = random.uniform(-20, 20)
        ssml_parts.append(f'<prosody rate="{rate:.1f}%">{word}</prosody><break time="100ms"/>')
    ssml_parts.append('</speak>')
    return ''.join(ssml_parts)

async def text_to_speech_edge_dynamic(text, output_file):
    ssml = create_dynamic_ssml(text)
    communicate = edge_tts.Communicate(ssml, voice="tr-TR-EmelNeural", ssml=True)
    await communicate.save(output_file)
    print(f"Ses dosyası kaydedildi: {output_file}")

# -- Aliyun video --
def create_video_via_aliyun(text, output_path):
    aliyun_token = os.environ.get("ALIYUN_ACCESS_TOKEN")
    if not aliyun_token:
        raise Exception("ALIYUN_ACCESS_TOKEN bulunamadı!")

    url = "https://video-ai.aliyuncs.com/create"  # örnek
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

# -- ffmpeg birleştirme --
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

# -- İçerik oluşturucu --
class EhliyetContentGenerator:
    def __init__(self):
        self.content = {
            "Hava Koşulları": {
                "Karlı": [
                    "Karlı havalarda mutlaka hızınızı azaltın ve takip mesafenizi artırın.",
                    "Karlı yollarda ani fren ve ani hızlanmalardan kaçının.",
                    "Kış lastiği kullanmak kayma riskini azaltır.",
                    "Araçta kayma başladığında panik yapmadan direksiyonu kayma yönünü çevirin.",
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
        return f"{tips[0]} {tips[1]}"

# -- Günlük üret ve yükle --
async def generate_and_upload_videos():
    gen = EhliyetContentGenerator()
    condition = gen.get_weather_condition()

    os.makedirs("output", exist_ok=True)

    short_text = gen.generate_short_tip(condition)
    long_text = gen.generate_long_tip(condition)

    paths = {
        "short_audio": "output/short_audio.mp3",
        "short_video": "output/short_video.mp4",
        "short_final": "output/short_final.mp4",
        "long_audio": "output/long_audio.mp3",
        "long_video": "output/long_video.mp4",
        "long_final": "output/long_final.mp4",
    }

    create_video_via_aliyun(short_text, paths["short_video"])
    await text_to_speech_edge_dynamic(short_text, paths["short_audio"])
    merge_audio_video(paths["short_audio"], paths["short_video"], paths["short_final"])

    create_video_via_aliyun(long_text, paths["long_video"])
    await text_to_speech_edge_dynamic(long_text, paths["long_audio"])
    merge_audio_video(paths["long_audio"], paths["long_video"], paths["long_final"])

    long_id = upload_video_to_youtube(paths["long_final"], f"Hava Durumu Detayları: {condition}", "Uzun sürüş ipuçları")
    short_id = upload_video_to_youtube(paths["short_final"], f"Shorts: {condition} Sürüş Tüyosu", f"Uzun video: https://youtu.be/{long_id}")

    print(f"Yükleme tamam: SHORT={short_id}, LONG={long_id}")

# -- Çalıştır --
if __name__ == "__main__":
    print("BAŞLIYOR...")
    asyncio.run(generate_and_upload_videos())
