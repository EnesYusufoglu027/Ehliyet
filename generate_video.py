import os
import random
import subprocess
import asyncio
import requests
import edge_tts
from generate_script import EhliyetContentGenerator

# Aliyun API anahtarlarını buraya doğrudan yaz
API_KEY = "ms-cbdce430-debc-4a5d-a467-5ff1e9fbd2f4"
API_SECRET = ""  # Varsa yaz, yoksa boş bırakabilirsin

def create_video_via_aliyun(text, output_path):
    url = "https://video-ai.aliyuncs.com/create"  # Gerçek endpoint ile değiştirilmeli

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "voice": "tr-TR-EmelNeural"
        # Gerekli diğer parametreler buraya eklenmeli
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        video_url = response.json().get("video_url")
        video_data = requests.get(video_url).content
        with open(output_path, "wb") as f:
            f.write(video_data)
        print(f"Video indirildi: {output_path}")
    else:
        print(f"Video oluşturma başarısız: {response.status_code} - {response.text}")

def create_dynamic_ssml(text):
    words = text.split()
    ssml_parts = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">']
    import random
    for word in words:
        rate_change = random.uniform(-20, 20)
        ssml_parts.append(
            f'<prosody rate="{rate_change:.1f}%">{word}</prosody> <break time="100ms"/>'
        )
    ssml_parts.append('</speak>')
    return ''.join(ssml_parts)

async def text_to_speech_edge_dynamic(text, output_file):
    ssml_text = create_dynamic_ssml(text)
    communicate = edge_tts.Communicate(ssml_text, voice="tr-TR-EmelNeural", input_format="ssml")
    await communicate.save(output_file)
    print(f"Dinamik hız ile Edge TTS ses dosyası oluşturuldu: {output_file}")

def merge_audio_video(audio_path, video_path, output_path):
    command = [
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_path
    ]
    subprocess.run(command, check=True)
    print(f"Ses ve video birleştirildi: {output_path}")

async def main():
    gen = EhliyetContentGenerator()
    title, text = gen.generate_tip()
    print(f"Başlık: {title}")
    print(f"Metin: {text}")

    os.makedirs("output", exist_ok=True)

    video_file = "output/video.mp4"
    audio_file = "output/audio.mp3"
    final_video = "output/final_video.mp4"

    create_video_via_aliyun(text, video_file)
    await text_to_speech_edge_dynamic(text, audio_file)
    merge_audio_video(audio_file, video_file, final_video)

if __name__ == "__main__":
    asyncio.run(main())
