import os
import subprocess
import asyncio
import edge_tts
from generate_script import EhliyetContentGenerator

async def text_to_speech(text, output_file):
    communicate = edge_tts.Communicate(text, voice="tr-TR-EmelNeural")
    await communicate.save(output_file)
    print(f"Ses dosyası oluşturuldu: {output_file}")

def merge_audio_video(audio_path, video_path, output_path):
    command = [
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", output_path
    ]
    subprocess.run(command, check=True)
    print(f"Video oluşturuldu: {output_path}")

async def main():
    gen = EhliyetContentGenerator()
    title, text = gen.generate_tip()
    print(f"Başlık: {title}")
    print(f"Metin: {text}")

    os.makedirs("output", exist_ok=True)

    video_file = "video.mp4"   # statik video dosyan
    audio_file = "output/audio.mp3"
    final_video = "output/final_video.mp4"

    await text_to_speech(text, audio_file)
    merge_audio_video(audio_file, video_file, final_video)

    # Başlık ve açıklama dışa aktarılabilir
    print(f"Video hazır: {final_video}")
    print(f"Başlık: {title}")
    print(f"Açıklama: {text}")

if __name__ == "__main__":
    asyncio.run(main())
