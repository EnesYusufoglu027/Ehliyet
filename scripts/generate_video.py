import os
import random
import subprocess
import asyncio
import edge_tts
from generate_script import EhliyetContentGenerator

def create_dynamic_ssml(text):
    words = text.split()
    ssml_parts = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">']
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

def select_random_video():
    video_folder = "background_videos"
    videos = [f for f in os.listdir(video_folder) if f.lower().endswith((".mp4", ".mov", ".avi"))]
    if not videos:
        raise Exception(f"{video_folder} klasöründe video dosyası bulunamadı!")
    chosen_video = random.choice(videos)
    return os.path.join(video_folder, chosen_video)

def merge_audio_video(audio_path, video_path, output_path):
    command = [
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_path
    ]
    subprocess.run(command, check=True)
    print(f"Video oluşturuldu: {output_path}")

async def main():
    gen = EhliyetContentGenerator()
    title, text = gen.generate_tip()
    print(f"Başlık: {title}")
    print(f"Metin: {text}")

    os.makedirs("output", exist_ok=True)
    audio_file = "output/audio_dynamic_edge.mp3"
    video_file = select_random_video()
    output_video = "output/final_video.mp4"

    await text_to_speech_edge_dynamic(text, audio_file)
    merge_audio_video(audio_file, video_file, output_video)

if __name__ == "__main__":
    asyncio.run(main())
