# main.py
import scripts.generate_script as gen_script
import scripts.generate_audio as gen_audio
import scripts.make_video as make_video
import scripts.upload_youtube as upload_yt

def main():
    print("Ehliyet Bot Başlıyor...")
    text = gen_script.generate_tip()
    print(f"Metin üretildi:\n{text}\n")
    audio_path = gen_audio.text_to_speech(text)
    print(f"Ses dosyası oluşturuldu: {audio_path}")
    video_path = make_video.create_video(audio_path, text)
    print(f"Video oluşturuldu: {video_path}")
    upload_yt.upload(video_path, text)
    print("Video başarıyla yüklendi.")

if __name__ == "__main__":
    main()
