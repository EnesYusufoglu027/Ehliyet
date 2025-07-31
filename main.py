import os
import sys
import base64
import subprocess
import asyncio
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import edge_tts

# -- Kimlik bilgilerini hazırla --
def prepare_credentials():
    token_b64 = os.environ.get("TOKEN_JSON_BASE64")
    client_b64 = os.environ.get("CLIENT_SECRET_BASE64")

    if not token_b64 or not client_b64:
        print("❌ TOKEN_JSON_BASE64 veya CLIENT_SECRET_BASE64 eksik!")
        sys.exit(1)

    with open("token.json", "wb") as f:
        f.write(base64.b64decode(token_b64))
    with open("service_account.json", "wb") as f:
        f.write(base64.b64decode(client_b64))
    print("✅ Gerekli kimlik dosyaları oluşturuldu.")

# -- YouTube servisi --
def get_youtube_service():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = service_account.Credentials.from_service_account_file("service_account.json", scopes=scopes)
    return build("youtube", "v3", credentials=creds)

# -- Video yükleme --
def upload_video(video_path, title, description):
    youtube = get_youtube_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        }
    }
    media = MediaFileUpload(video_path)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print(f"✅ Video yüklendi: https://youtu.be/{response['id']}")
    return response['id']

# -- Edge-TTS ile ses oluştur --
async def generate_audio(text, output_path):
    communicate = edge_tts.Communicate(text, voice="tr-TR-EmelNeural")
    await communicate.save(output_path)
    print(f"🎤 Ses dosyası oluşturuldu: {output_path}")

# -- Sesi çıkar, yeni sesi videoya ekle --
def replace_audio(video_path, audio_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    subprocess.run(command, check=True)
    print(f"🎬 Video oluşturuldu: {output_path}")

# -- Ana işlem --
async def main():
    prepare_credentials()
    
    # Sesli video dosyanızın adı
    input_video = "video.mp4"
    output_audio = "speech.mp3"
    final_video = "final_output.mp4"
    speech_text = "Güneşli havalarda gözlük takarak görüşünüzü artırın ve yayalara dikkat edin."

    # 1. Sesi üret
    await generate_audio(speech_text, output_audio)

    # 2. Yeni sesi videoya ekle
    replace_audio(input_video, output_audio, final_video)

    # 3. YouTube'a yükle
    upload_video(final_video, "Test Video - Yeni Sesli", "Edge-TTS ile oluşturulan ses kullanıldı.")

# -- Çalıştır --
if __name__ == "__main__":
    asyncio.run(main())
