import os
import sys
import subprocess
import asyncio
import schedule
import time
import random
import requests
import shutil
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import edge_tts

# -- ffmpeg var mı kontrol et, yoksa hata ver --
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("HATA: ffmpeg sistemde bulunamadı. Lütfen CI ortamında ffmpeg'in kurulu olduğundan emin olun.")
        sys.exit(1)
    else:
        print("ffmpeg bulundu.")

check_ffmpeg()

# -- Gerekli paketleri kontrol edip yükleyen fonksiyon --
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in ["schedule", "google-api-python-client", "google-auth", "google-auth-oauthlib", "edge-tts", "requests"]:
    try:
        __import__(pkg)
    except ImportError:
        print(f"{pkg} paketi yüklü değil, yükleniyor...")
        install(pkg)

# --- Ehliyet içerik üretici (basit örnek) ---
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
        tips = self.content["Hava Koşulları"][condition]
        return random.choice(tips)

    def generate_long_tip(self, condition):
        tips = self.content["Hava Koşulları"][condition]
        tip1 = random.choice(tips)
        tip2 = random.choice([t for t in tips if t != tip1])
        return f"{tip1} {tip2}"

# -- Aliyun API keyleri burada --
API_KEY = "ms-cbdce430-debc-4a5d-a467-5ff1e9fbd2f4"
API_SECRET = ""  # Eğer varsa

# -- YouTube API ayarları --
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = "client_secret.json"

def get_youtube_service():
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import google.auth.transport.requests
    import google.oauth2.credentials
    import os.path

    creds = None
    token_file = "token.json"
    if os.path.exists(token_file):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_console()
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    service = build('youtube', 'v3', credentials=creds)
    return service

def upload_video_to_youtube(video_path, title, description):
    youtube = get_youtube_service()
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['ehliyet', 'sürüş', 'hava durumu', 'kış sürüşü'],
            'categoryId': '27'  # Eğitim
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        }
    }
    media = MediaFileUpload(video_path)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    response = request.execute()
    print(f"Video yüklendi: ID={response['id']}")
    return response['id']

# -- Dinamik hızla Edge TTS ses dosyası oluşturma --
def create_dynamic_ssml(text):
    words = text.split()
    ssml_parts = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">']
    import random
    for word in words:
        rate_change = random.uniform(-20, 20)
        ssml_parts.append(f'<prosody rate="{rate_change:.1f}%">{word}</prosody> <break time="100ms"/>')
    ssml_parts.append('</speak>')
    return ''.join(ssml_parts)

async def text_to_speech_edge_dynamic(text, output_file):
    ssml_text = create_dynamic_ssml(text)
    communicate = edge_tts.Communicate(ssml_text, voice="tr-TR-EmelNeural", input_format="ssml")
    await communicate.save(output_file)
    print(f"Ses dosyası oluşturuldu: {output_file}")

# -- Aliyun ile text-to-video (örnek, gerçek endpoint değiştirilmeli) --
def create_video_via_aliyun(text, output_path):
    url = "https://video-ai.aliyuncs.com/create"  # Gerçek endpoint koy
    headers = {
        "Authorization": f"Bearer {API_KEY}",
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
        raise Exception(f"Video oluşturma başarısız: {response.status_code} - {response.text}")

# -- ffmpeg ile ses ve videoyu birleştir --
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

# -- Günlük 2 video üretim fonksiyonu --
async def generate_and_upload_videos():
    gen = EhliyetContentGenerator()
    condition = gen.get_weather_condition()

    # SHORT video (kısa ipucu)
    short_text = gen.generate_short_tip(condition)
    short_title = f"Hava Durumu Shorts: {condition} Hakkında İpucu"
    short_audio = "output/short_audio.mp3"
    short_video = "output/short_video.mp4"
    short_final = "output/short_final.mp4"

    # LONG video (daha detaylı)
    long_text = gen.generate_long_tip(condition)
    long_title = f"Hava Durumu Detayları: {condition}"
    long_audio = "output/long_audio.mp3"
    long_video = "output/long_video.mp4"
    long_final = "output/long_final.mp4"

    os.makedirs("output", exist_ok=True)

    # SHORT video oluştur
    create_video_via_aliyun(short_text, short_video)
    await text_to_speech_edge_dynamic(short_text, short_audio)
    merge_audio_video(short_audio, short_video, short_final)

    # LONG video oluştur
    create_video_via_aliyun(long_text, long_video)
    await text_to_speech_edge_dynamic(long_text, long_audio)
    merge_audio_video(long_audio, long_video, long_final)

    # LONG video ID alın ve SHORTS açıklamasına ekle
    long_video_id = upload_video_to_youtube(long_final, long_title, f"Detaylı video için: https://youtu.be/SHORTS_VIDEO_ID")
    short_video_id = upload_video_to_youtube(short_final, short_title, f"Detaylı video için: https://youtu.be/{long_video_id}")

    print(f"Shorts video ID: {short_video_id}, Normal video ID: {long_video_id}")

# -- Zamanlayıcı fonksiyonu --
def job():
    print("Günlük video üretim ve yükleme başladı.")
    asyncio.run(generate_and_upload_videos())
    print("Video üretimi ve yüklemesi tamamlandı.")

def run_scheduler():
    # Her gün 07:30'da çalışacak
    schedule.every().day.at("07:30").do(job)
    print("Scheduler başlatıldı. Bekleniyor...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    run_scheduler()
