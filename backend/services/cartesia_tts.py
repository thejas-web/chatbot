import re
import time

from cartesia import Cartesia

from backend.config import cartesia_api_key


def clean_text_for_tts(text: str) -> str:
    """
    Clean text before sending it to TTS.
    """

    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text


class CartesiaTTS:

    def __init__(
        self,
        model="sonic-3.5",
        voice_id=None,
    ):
        if not cartesia_api_key:
            raise ValueError("CARTESIA_API_KEY is not configured.")

        self.client = Cartesia(api_key=cartesia_api_key)

        self.model = model
        self.voice_id = voice_id

    def split_text(
        self,
        text: str,
        max_chars: int = 1000,
        min_chars: int = 80,
    ):
        """
        Split long text into reasonably sized chunks.

        Prefer sentence boundaries instead of cutting
        through a sentence.
        """

        text = text.strip()

        if len(text) <= max_chars:
            return [text]

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        chunks = []
        current = ""

        for sentence in sentences:

            if not sentence:
                continue

            candidate = (
                f"{current} {sentence}".strip()
                if current
                else sentence
            )

            if len(candidate) <= max_chars:
                current = candidate

            else:

                if current:
                    chunks.append(current)

                current = sentence

        if current:
            chunks.append(current)

        return chunks

    def _generate_chunk(self, text: str):

        print(
            f"Generating Cartesia TTS chunk "
            f"({len(text)} characters)"
        )

        start_time = time.time()

        audio_stream = self.client.tts.bytes(
            model_id="sonic-3.6",
            transcript=text,
            voice={
                "mode": "id",
                "id": self.voice_id,
            },
            output_format={
                "container": "raw",
                "encoding": "pcm_s16le",
                "sample_rate": 16000,
            },
            language="en",
            generation_config={
                "speed": 1.4,
                "volume": 1.0,
                "emotion": "content",
            },
        )

        audio = b"".join(audio_stream)

        print(
            f"Cartesia TTS chunk generated in "
            f"{time.time() - start_time:.3f}s"
        )

        return audio

    def generate_chunks(self, text: str):

        text = clean_text_for_tts(text)

        if not text:
            return

        chunks = self.split_text(
            text,
            max_chars=1000,
            min_chars=80,
        )

        print("\n" + "=" * 60)
        print("CARTESIA TTS STREAM")
        print("=" * 60)

        print(f"Original text: {len(text)} characters")
        print(f"TTS chunks: {len(chunks)}")

        for index, chunk in enumerate(chunks, start=1):

            print(
                f"\nGenerating chunk "
                f"{index}/{len(chunks)}"
            )

            print(
                f"Text ({len(chunk)} chars):"
            )

            print(chunk)

            pcm = self._generate_chunk(chunk)

            print(
                f"PCM size: {len(pcm)} bytes"
            )

            yield pcm

    def generate(self, text: str):

        return b"".join(
            self.generate_chunks(text)
        )