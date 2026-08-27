import numpy as np
from kokoro import KPipeline
from scipy.signal import resample_poly


class KokoroTTS:

    def __init__(self):
        print("Loading Kokoro TTS...")

        self.pipeline = KPipeline(
            lang_code="a"
        )

        self.voice = "af_heart"

        print("Kokoro TTS loaded.")

    def generate(self, text: str) -> bytes:

        print("Generating speech...")

        generator = self.pipeline(
            text,
            voice=self.voice,
            speed=1.0,
        )

        audio_chunks = []

        for _, _, audio in generator:
            audio_chunks.append(
                audio.numpy()
                if hasattr(audio, "numpy")
                else np.asarray(audio)
            )

        if not audio_chunks:
            return b""

        # Combine all Kokoro chunks
        audio = np.concatenate(audio_chunks)

        # Kokoro output = 24 kHz
        # Simli requires = 16 kHz
        audio_16k = resample_poly(
            audio,
            2,
            3
        )

        # Make sure audio is mono
        audio_16k = np.asarray(
            audio_16k,
            dtype=np.float32
        )

        # Prevent clipping
        audio_16k = np.clip(
            audio_16k,
            -1.0,
            1.0
        )

        # Convert float32 [-1, 1]
        # to signed 16-bit PCM
        pcm16 = (
            audio_16k * 32767
        ).astype(np.int16)

        print(
            f"Generated {len(pcm16)} samples "
            f"at 16 kHz"
        )

        return pcm16.tobytes()