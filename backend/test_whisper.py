from backend.services.whisper_stt import WhisperSTT


def main():
    print("Loading Whisper...")

    whisper = WhisperSTT()

    audio_path = "backend/test_audio.mp3"

    print("\nTranscribing:", audio_path)

    text = whisper.transcribe(audio_path)

    print("\n==============================")
    print("TRANSCRIPT:")
    print(text)
    print("==============================")


if __name__ == "__main__":
    main()