from backend.services.kokoro_tts import KokoroTTS


tts = KokoroTTS()

audio = tts.generate(
    "Hello, I am the Webenza AI assistant."
)

print(
    "Audio bytes:",
    len(audio)
)

with open(
    "test_output.pcm",
    "wb"
) as f:

    f.write(audio)

print("PCM file created.")