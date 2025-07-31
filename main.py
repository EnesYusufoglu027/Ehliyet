import os
import base64
import subprocess
import asyncio

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import edge_tts

# ======= ENV DEĞERLERİNDEN KİMLİK DOSYALARINI OLUŞTUR =======

# TOKEN
token_b64 = os.environ.get("TOKEN_JSON_BASE64")
if not token_b64:
    print("❌ TOKEN_JSON_BASE64 env değişkeni bulunamadı!")
    exit(1)
with open("token.json", "wb") as f:
    f.write(base64.b64decode(token_b64))
print("✅ token.json oluşturuldu.")

# client_secret.json (zorunlu değil ama yüklemişsen hata çıkmasın)
client_secret_b64 = os.environ.get("CLIENT_SECRET_BASE64")
if client_secret_b64:
    with open("client_secret.json", "wb") as f:
        f.write(base64.b64decode(client_secret_b64))
    print("✅ client_secret.json oluşturuldu.")

# ======= Edge-TTS İLE SES OLUŞTUR =======

async def generate_speech(text, output_path):
    communicate = edge_tts.Communicate(text, voice="tr-TR-EmelNeural")
    await communicate.save(output_path)
    print(f"🎤 Ses dosyası oluşturuldu: {output_path}")

# ======= SESİ VİDEOYA GÖMME =======

def replace_audio(input_video, new_audio, output_video):
    command = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-i", new_audio,
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest", output_video
    ]
    subprocess.run(command, check=True)
    print(f"🎬 Video oluşturuldu: {output_video}")

# ======= YOUTUBE SERVİSİNE BAĞLAN =======

def get_youtube_service():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = Credentials.from_authorized_user_file("token.json", scopes)
    return build("youtube", "v3", credentials=creds)

# ======= YOUTUBE’A VİDEO YÜKLE =======

def upload_video(video_path, title, description):
    youtube = get_youtube_service()
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["ehliyet", "sürüş", "eğitim"],
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
    print(f"📤 Yüklendi: https://youtu.be/{response['id']}")

# ======= ANA FONKSİYON =======

async def main():
    input_video = "video.mp4"             # Mevcut sessiz/sesli video
    output_audio = "speech.mp3"           # Edge-TTS ile oluşturulacak ses
    final_video = "final_output.mp4"      # Son hali (yeni sesli video)

    sample_text = "Karlı havalarda yavaş gidin ve takip mesafesini artırın."
    await generate_speech(sample_text, output_audio)
    replace_audio(input_video, output_audio, final_video)
    upload_video(final_video, "Test Video - Yeni Sesli", "Edge-TTS ile oluşturulan ses kullanıldı.")

if __name__ == "__main__":
    asyncio.run(main())
