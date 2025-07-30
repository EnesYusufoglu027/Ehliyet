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
from google_auth_oauthlib.flow import InstalledAppFlow
import edge_tts

# --- ENV'den BASE64 ile json dosyalarını üret ---
# client_secret.json
client_secret_b64 = os.environ.get("CLIENT_SECRET_BASE64")
if not client_secret_b64:
    print("CLIENT_SECRET_BASE64 env değişkeni bulunamadı!")
    sys.exit(1)
with open("client_secret.json", "w", encoding="utf-8") as f:
    f.write(base64.b64decode(client_secret_b64).decode("utf-8"))
print("✅ client_secret.json oluşturuldu.")

# token.json (varsa)
token_json_b64 = os.environ.get("TOKEN_JSON_BASE64")
if token_json_b64:
    with open("token.json", "w", encoding="utf-8") as f:
        f.write(base64.b64decode(token_json_b64).decode("utf-8"))
    print("✅ token.json oluşturuldu (env'den).")
else:
    print("⚠️ TOKEN_JSON_BASE64 env değişkeni bulunamadı, ilk girişte konsol doğrulaması yapılacak.")

# --- ffmpeg kontrolü ---
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("HATA: ffmpeg bulunamadı.")
        sys.exit(1)
    else:
        print("✅ ffmpeg bulundu.")

check_ffmpeg()

# --- eksik paketleri yükle ---
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in ["schedule", "google-api-python-client", "google-auth", "google-auth-oauthlib", "edge-tts", "requests"]:
    try:
        __import__(pkg)
    except ImportError:
        print(f"{pkg} yükleniyor...")
        install(pkg)

# --- YouTube servisi ---
def get_youtube_service():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = None

    if os.path.exists("token.json"):
        with open("token.json", "r", encoding="utf-8") as f:
            creds_data = json.load(f)
            creds = Credentials.from_authorized_user_info(info=creds_data, scopes=scopes)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes)
        creds = flow.run_console()
        with open("token.json", "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print("✅ token.json ilk kez oluşturuldu.")

    return build("youtube", "v3", credentials=creds)

# --- Video yükle ---
def upload_video_to_youtube(video_path, title, description):
    youtube = get_youtube_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["ehliyet", "sürüş", "hava durumu"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(video_path)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print(f"✅ Video yüklendi: {response['id']}")
    return response["id"]

# --- İçerik üretici sınıfı ---
class EhliyetContentGenerator:
    def __init__(self):
        self.content = {
            "Hava Koşulları": {
                "Karlı": [
                    "Karlı havalarda mutlaka hızınızı azaltın ve takip mesafenizi artırın.",
                    "Kış lastiği kullanmak kayma riskini azaltır.",
                    "Sileceklerinizi kontrol edin."
                ],
                "Yağmurlu": [
                    "Yağmurda fren mesafenizi artırın.",
                    "Islak zeminde ani frenlerden kaçının.",
                    "Farlarınızı açmayı unutmayın."
                ],
                "Güneşli": [
                    "Güneşli havalarda gözlük takın.",
                    "Yol çizgilerini dikkatle takip edin.",
                    "Klima kullanarak rahat sürün."
                ]
            }
        }

    def get_weather_condition(self):
        return random.choice(list(self.content["Hava Koşulları"].keys()))

    def generate_short_tip(self, condition):
        return random.choice(self.content["Hava Koşulları"][condition])

    def generate_long_tip(self, condition):
        tips = self.content["Hava Koşulları"][condition]
        return " ".join(random.sample(tips, 2))

# --- Aliyun video oluşturma (örnek dummy) ---
def create_video_via_aliyun(text, output_path):
    # Gerçek Aliyun entegrasyonu burada olacak
    with open(output_path, "wb") as f:
        f.write(b"\x00" * 1024 * 1024)  # Dummy video dosyası
    print(f"🎥 Dummy video oluşturuldu: {output_path}")

# --- TTS SSML üret ---
def create_dynamic_ssml(text):
    words = text.split()
    parts = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">']
    for word in words:
        rate = random.uniform(-20, 20)
        parts.append(f'<prosody rate="{rate:.1f}%">{word}</prosody> <break time="100ms"/>')
    parts.append('</speak>')
    return "".join(parts)

# --- TTS ses üret ---
async def text_to_speech_edge_dynamic(text, output_file):
    ssml = create_dynamic_ssml(text)
    communicate = edge_tts.Communicate(ssml, voice="tr-TR-EmelNeural", input_format="ssml")
    await communicate.save(output_file)
    print(f"🔊 Ses üretildi: {output_file}")

# --- ffmpeg ile birleştir ---
def merge_audio_video(audio_path, video_path, output_path):
    command = ["ffmpeg", "-y", "-i", video_path, "-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-shortest", output_path]
    subprocess.run(command, check=True)
    print(f"🎞️ Birleştirildi: {output_path}")

# --- Video üret & yükle ---
async def generate_and_upload_videos():
    gen = EhliyetContentGenerator()
    condition = gen.get_weather_condition()

    os.makedirs("output", exist_ok=True)

    short_text = gen.generate_short_tip(condition)
    long_text = gen.generate_long_tip(condition)

    paths = {
        "short_audio": "output/short.mp3",
        "short_video": "output/short_raw.mp4",
        "short_final": "output/short_final.mp4",
        "long_audio": "output/long.mp3",
        "long_video": "output/long_raw.mp4",
        "long_final": "output/long_final.mp4"
    }

    create_video_via_aliyun(short_text, paths["short_video"])
    await text_to_speech_edge_dynamic(short_text, paths["short_audio"])
    merge_audio_video(paths["short_audio"], paths["short_video"], paths["short_final"])

    create_video_via_aliyun(long_text, paths["long_video"])
    await text_to_speech_edge_dynamic(long_text, paths["long_audio"])
    merge_audio_video(paths["long_audio"], paths["long_video"], paths["long_final"])

    long_id = upload_video_to_youtube(paths["long_final"], f"{condition} Hakkında Bilgilendirici Video", long_text)
    short_id = upload_video_to_youtube(paths["short_final"], f"{condition} İçin Kısa İpucu", f"Ayrıntılı video: https://youtu.be/{long_id}")

# --- Günlük zamanlayıcı ---
def job():
    print("🎬 Video üretim başlıyor...")
    asyncio.run(generate_and_upload_videos())
    print("✅ İşlem tamamlandı.")

if __name__ == "__main__":
    job()
